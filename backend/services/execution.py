import asyncio
import uuid
import time
import logging
from typing import Dict, Any, Optional, AsyncGenerator
from backend.graph.state import AgentWorkflowState
from backend.graph.workflow import multi_agent_graph
from backend.graph.checkpoints import save_state_snapshot, get_state_snapshot
from backend.database.session import async_session
from backend.database.models import RunRecord, TaskStep, ApprovalRecord, FinalReport
from backend.mcp.clients import mcp_client
from backend.services.audit import audit_service

logger = logging.getLogger(__name__)

# Run event queues for real-time Server-Sent Events (SSE)
RUN_EVENT_QUEUES: Dict[str, asyncio.Queue] = {}


class ExecutionService:
    """Orchestrates workflow runs, checkpoints, resume actions, and SSE broadcasting."""

    @staticmethod
    async def create_and_start_run(query: str, user_id: str = "analyst_jane", tenant_id: str = "enterprise_demo") -> str:
        run_id = f"run_{uuid.uuid4().hex[:10]}"
        queue = asyncio.Queue()
        RUN_EVENT_QUEUES[run_id] = queue

        initial_state: AgentWorkflowState = {
            "run_id": run_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "query": query,
            "plan": {},
            "analytics_results": {},
            "research_results": {},
            "forecast_results": {},
            "critic_results": {},
            "retry_count": 0,
            "max_retries": 2,
            "quality_passed": False,
            "report_results": {},
            "approval_record": None,
            "approval_status": "NONE",
            "action_execution_result": None,
            "status": "RUNNING",
            "current_node": "START",
            "step_history": [],
            "total_tokens": 0,
            "total_cost": 0.0,
            "errors": []
        }

        save_state_snapshot(run_id, initial_state)

        # Launch graph execution in background task
        asyncio.create_task(ExecutionService._run_graph_loop(run_id, initial_state, queue))
        return run_id

    @staticmethod
    async def _run_graph_loop(run_id: str, state: AgentWorkflowState, queue: asyncio.Queue):
        try:
            await queue.put({
                "event": "run_started",
                "run_id": run_id,
                "timestamp": time.time(),
                "query": state["query"]
            })

            # Stream execution nodes through LangGraph
            config = {"configurable": {"thread_id": run_id}}
            async for output in multi_agent_graph.astream(state, config=config):
                for node_name, node_update in output.items():
                    # Merge update into current state
                    state.update(node_update)
                    save_state_snapshot(run_id, state)

                    await queue.put({
                        "event": "node_completed",
                        "run_id": run_id,
                        "node": node_name,
                        "status": state.get("status"),
                        "total_tokens": state.get("total_tokens", 0),
                        "total_cost": state.get("total_cost", 0.0),
                        "approval_needed": (state.get("status") == "WAITING_APPROVAL"),
                        "step_info": state["step_history"][-1] if state["step_history"] else {}
                    })

            await queue.put({
                "event": "run_finished",
                "run_id": run_id,
                "status": state.get("status", "COMPLETED"),
                "report_id": state.get("report_results", {}).get("report_id")
            })

        except Exception as e:
            logger.error(f"Error executing run {run_id}: {e}", exc_info=True)
            state["status"] = "FAILED"
            state["errors"].append(str(e))
            save_state_snapshot(run_id, state)
            await queue.put({
                "event": "run_failed",
                "run_id": run_id,
                "error": str(e)
            })

    @staticmethod
    async def resolve_approval(run_id: str, decision: str, reviewer: str = "admin", reason: Optional[str] = None) -> Dict[str, Any]:
        """Human approval gate resolution: resumes workflow with decision."""
        state = get_state_snapshot(run_id)
        if not state:
            raise ValueError(f"Run {run_id} not found.")

        app_record = state.get("approval_record")
        if not app_record:
            raise ValueError(f"Run {run_id} has no pending approval requests.")

        queue = RUN_EVENT_QUEUES.get(run_id)

        if decision.upper() == "APPROVED":
            state["approval_status"] = "APPROVED"
            app_record["status"] = "APPROVED"
            app_record["approved_by"] = reviewer

            # Execute the approved consequential action via Automation MCP tool
            action_type = app_record.get("action_type", "send_approved_email")
            token = app_record.get("approval_token", "")

            exec_res = await mcp_client.invoke_tool(
                agent_name="action_executor",
                tool_name=action_type,
                arguments={
                    "to": app_record.get("recipient", "finance-leadership@apexcloud.io"),
                    "subject": app_record.get("subject", "Financial Intelligence Report"),
                    "body": state.get("report_results", {}).get("report_content", "")[:1000],
                    "approval_token": token
                },
                run_id=run_id
            )
            state["action_execution_result"] = exec_res
            state["status"] = "COMPLETED"
            save_state_snapshot(run_id, state)

            audit_service.log_tool_invocation(
                run_id=run_id,
                agent_name="action_executor",
                server_name="Automation_MCP_Server",
                tool_name=action_type,
                arguments={"to": app_record.get("recipient"), "approval_token": token},
                status="SUCCESS",
                result=exec_res,
                latency_ms=exec_res.get("latency_ms", 0.0)
            )

            if queue:
                await queue.put({
                    "event": "approval_resolved",
                    "run_id": run_id,
                    "decision": "APPROVED",
                    "execution_result": exec_res
                })

            return {"status": "APPROVED", "run_id": run_id, "action_result": exec_res}

        else:
            state["approval_status"] = "REJECTED"
            app_record["status"] = "REJECTED"
            app_record["rejection_reason"] = reason or "Rejected by human reviewer."
            state["status"] = "COMPLETED"
            save_state_snapshot(run_id, state)

            if queue:
                await queue.put({
                    "event": "approval_resolved",
                    "run_id": run_id,
                    "decision": "REJECTED",
                    "reason": reason
                })

            return {"status": "REJECTED", "run_id": run_id, "reason": reason}

    @staticmethod
    async def event_generator(run_id: str) -> AsyncGenerator[str, None]:
        queue = RUN_EVENT_QUEUES.get(run_id)
        if not queue:
            # Send immediate snapshot event
            state = get_state_snapshot(run_id)
            if state:
                yield f"data: {{\"event\": \"current_state\", \"status\": \"{state.get('status')}\"}}\n\n"
            return

        while True:
            try:
                event_data = await asyncio.wait_for(queue.get(), timeout=20.0)
                import json
                yield f"data: {json.dumps(event_data)}\n\n"
                if event_data.get("event") in ["run_finished", "run_failed"]:
                    break
            except asyncio.TimeoutError:
                # Keep-alive heartbeat
                yield f": ping\n\n"


execution_service = ExecutionService()
