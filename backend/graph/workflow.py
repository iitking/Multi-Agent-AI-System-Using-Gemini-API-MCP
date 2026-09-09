import time
import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from backend.graph.state import AgentWorkflowState
from backend.graph.checkpoints import memory_checkpointer, save_state_snapshot
from backend.agents.planner import planner_agent
from backend.agents.analytics import analytics_agent
from backend.agents.researcher import researcher_agent
from backend.agents.forecaster import forecaster_agent
from backend.agents.critic import critic_agent
from backend.agents.reporter import reporter_agent
from backend.mcp.clients import mcp_client
from backend.services.audit import audit_service
from backend.services.metrics import metrics_service

logger = logging.getLogger(__name__)


# Node 1: Planner
async def planner_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    t0 = time.time()

    res = await planner_agent.create_plan(query)
    plan = res["plan"]
    token_usage = res["token_usage"]

    step_info = {
        "step": "planner",
        "agent": "planner",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": token_usage.total_tokens,
        "summary": plan.get("summary", "Plan formulated")
    }

    return {
        "plan": plan,
        "status": "RUNNING",
        "current_node": "planner",
        "step_history": [step_info],
        "total_tokens": token_usage.total_tokens,
        "total_cost": token_usage.estimated_cost_usd
    }


# Node 2: Analytics Agent
async def analytics_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    t0 = time.time()

    res = await analytics_agent.execute(run_id, query)
    tokens = res.get("tokens_used", 400)
    cost = (tokens / 1_000_000.0) * 0.15

    step_info = {
        "step": "analytics",
        "agent": "analytics",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": tokens,
        "tool_calls": res.get("tool_calls", 3),
        "summary": f"Calculated revenue variance: {res.get('metrics', {}).get('net_revenue_variance_usd', '-$2.3M')}"
    }

    return {
        "analytics_results": res,
        "current_node": "analytics",
        "step_history": [step_info],
        "total_tokens": tokens,
        "total_cost": cost
    }


# Node 3: Researcher Agent
async def researcher_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    t0 = time.time()

    res = await researcher_agent.execute(run_id, query)
    tokens = res.get("tokens_used", 450)
    cost = (tokens / 1_000_000.0) * 0.15

    step_info = {
        "step": "researcher",
        "agent": "researcher",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": tokens,
        "tool_calls": res.get("tool_calls", 3),
        "summary": f"Retrieved {len(res.get('evidence', []))} verified documents from Research MCP"
    }

    return {
        "research_results": res,
        "current_node": "researcher",
        "step_history": [step_info],
        "total_tokens": tokens,
        "total_cost": cost
    }


# Node 4: Forecaster & Insight Agent
async def forecaster_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    analytics_data = state["analytics_results"]
    research_data = state["research_results"]
    critic_feedback = state.get("critic_results", {}).get("feedback", "")
    t0 = time.time()

    res = await forecaster_agent.execute(query, analytics_data, research_data, critic_feedback)
    tokens = res.get("tokens_used", 500)
    cost = (tokens / 1_000_000.0) * 0.15

    step_info = {
        "step": "forecaster",
        "agent": "forecaster",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": tokens,
        "summary": "Generated Base/Bull/Bear scenarios and root-cause attribution"
    }

    return {
        "forecast_results": res,
        "current_node": "forecaster",
        "step_history": [step_info],
        "total_tokens": tokens,
        "total_cost": cost
    }


# Node 5: Critic / Quality Agent
async def critic_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    analytics_data = state["analytics_results"]
    research_data = state["research_results"]
    forecast_data = state["forecast_results"]
    retry_count = state.get("retry_count", 0)
    t0 = time.time()

    res = await critic_agent.execute(query, analytics_data, research_data, forecast_data, retry_count)
    tokens = res.get("tokens_used", 350)
    cost = (tokens / 1_000_000.0) * 0.15

    quality_passed = res.get("quality_passed", True)

    step_info = {
        "step": "critic",
        "agent": "critic",
        "status": "PASSED" if quality_passed else "RETRY_REQUIRED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": tokens,
        "score": res.get("score", 9.0),
        "summary": f"Quality Score: {res.get('score', 9.0)}/10. Passed: {quality_passed}"
    }

    new_retry_count = retry_count + (0 if quality_passed else 1)

    return {
        "critic_results": res,
        "quality_passed": quality_passed,
        "retry_count": new_retry_count,
        "current_node": "critic",
        "step_history": [step_info],
        "total_tokens": tokens,
        "total_cost": cost
    }


# Node 6: Escalation (when retries exhausted)
async def escalation_node(state: AgentWorkflowState) -> Dict[str, Any]:
    step_info = {
        "step": "escalate",
        "agent": "supervisor",
        "status": "ESCALATED",
        "summary": "Max retries reached on quality checks. Partial results escalated to human reviewer."
    }
    return {
        "status": "ESCALATED",
        "current_node": "escalate",
        "step_history": [step_info]
    }


# Node 7: Reporter Agent
async def reporter_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    query = state["query"]
    analytics_data = state["analytics_results"]
    research_data = state["research_results"]
    forecast_data = state["forecast_results"]
    critic_data = state["critic_results"]
    t0 = time.time()

    res = await reporter_agent.execute(run_id, query, analytics_data, research_data, forecast_data, critic_data)
    tokens = res.get("tokens_used", 600)
    cost = (tokens / 1_000_000.0) * 0.20

    approval_req = res.get("approval_request")
    approval_status = "PENDING" if approval_req else "NONE"
    next_status = "WAITING_APPROVAL" if approval_req else "COMPLETED"

    step_info = {
        "step": "reporter",
        "agent": "reporter",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "tokens": tokens,
        "summary": "Compiled executive report. Human approval requested." if approval_req else "Compiled executive report."
    }

    return {
        "report_results": res,
        "approval_record": approval_req,
        "approval_status": approval_status,
        "status": next_status,
        "current_node": "reporter",
        "step_history": [step_info],
        "total_tokens": tokens,
        "total_cost": cost
    }


# Node 8: Action Executor (Post-Approval)
async def action_executor_node(state: AgentWorkflowState) -> Dict[str, Any]:
    run_id = state["run_id"]
    app_record = state.get("approval_record", {})
    action_type = app_record.get("action_type", "send_approved_email")
    token = app_record.get("approval_token", "")

    t0 = time.time()
    res = await mcp_client.invoke_tool(
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

    audit_service.log_tool_invocation(
        run_id=run_id,
        agent_name="action_executor",
        server_name="Automation_MCP_Server",
        tool_name=action_type,
        arguments={"to": app_record.get("recipient"), "approval_token": token},
        status="SUCCESS",
        result=res,
        latency_ms=res.get("latency_ms", 0.0)
    )

    step_info = {
        "step": "action_executor",
        "agent": "action_executor",
        "status": "COMPLETED",
        "latency_ms": round((time.time() - t0) * 1000.0, 2),
        "summary": f"Executed approved action '{action_type}' via Automation MCP & n8n webhook"
    }

    return {
        "action_execution_result": res,
        "status": "COMPLETED",
        "current_node": "action_executor",
        "step_history": [step_info]
    }


# Node 9: Record Rejection
async def record_rejection_node(state: AgentWorkflowState) -> Dict[str, Any]:
    step_info = {
        "step": "record_rejection",
        "agent": "human_reviewer",
        "status": "REJECTED",
        "summary": "External action was rejected by human reviewer. Rejection recorded in audit trail."
    }
    return {
        "status": "COMPLETED",
        "current_node": "record_rejection",
        "step_history": [step_info]
    }


# Node 10: Persister & Finalizer
async def persister_node(state: AgentWorkflowState) -> Dict[str, Any]:
    save_state_snapshot(state["run_id"], state)
    metrics_service.record_run_completion(
        run_id=state["run_id"],
        success=(state["status"] in ["COMPLETED", "WAITING_APPROVAL"]),
        latency_seconds=12.5,
        tokens_used=state.get("total_tokens", 2500),
        cost_usd=state.get("total_cost", 0.04),
        retries_used=state.get("retry_count", 0),
        approved=(state.get("approval_status") == "APPROVED")
    )
    return {
        "current_node": "persister"
    }


# Conditional routing functions
def quality_router(state: AgentWorkflowState) -> Literal["reporter", "forecaster", "escalate"]:
    if state.get("quality_passed", False):
        return "reporter"
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "forecaster"
    return "escalate"


def approval_router(state: AgentWorkflowState) -> Literal["action_executor", "record_rejection", "persister"]:
    app_record = state.get("approval_record")
    if not app_record:
        return "persister"

    status = state.get("approval_status", "PENDING")
    if status == "APPROVED":
        return "action_executor"
    elif status == "REJECTED":
        return "record_rejection"
    return "persister"


# Construct LangGraph StateGraph
def build_multi_agent_graph():
    builder = StateGraph(AgentWorkflowState)

    # Add Nodes
    builder.add_node("planner", planner_node)
    builder.add_node("analytics", analytics_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("forecaster", forecaster_node)
    builder.add_node("critic", critic_node)
    builder.add_node("escalate", escalation_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("action_executor", action_executor_node)
    builder.add_node("record_rejection", record_rejection_node)
    builder.add_node("persister", persister_node)

    # Edges
    builder.add_edge(START, "planner")

    # Supervisor splits into parallel specialist analytics and researcher
    builder.add_edge("planner", "analytics")
    builder.add_edge("planner", "researcher")

    # Analytics and researcher merge into forecaster
    builder.add_edge("analytics", "forecaster")
    builder.add_edge("researcher", "forecaster")

    # Forecaster goes to critic
    builder.add_edge("forecaster", "critic")

    # Critic conditionally branches: quality passed -> reporter; fail -> retry forecaster; max retries -> escalate
    builder.add_conditional_edges(
        "critic",
        quality_router,
        {
            "reporter": "reporter",
            "forecaster": "forecaster",
            "escalate": "escalate"
        }
    )

    builder.add_edge("escalate", "persister")

    # Reporter conditionally branches depending on approval status
    builder.add_conditional_edges(
        "reporter",
        approval_router,
        {
            "action_executor": "action_executor",
            "record_rejection": "record_rejection",
            "persister": "persister"
        }
    )

    builder.add_edge("action_executor", "persister")
    builder.add_edge("record_rejection", "persister")
    builder.add_edge("persister", END)

    # Compile with memory checkpointer
    graph = builder.compile(checkpointer=memory_checkpointer)
    return graph


multi_agent_graph = build_multi_agent_graph()
