from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.api.auth import get_current_user, require_role, UserOut, create_access_token
from backend.api.approvals import ApprovalDecisionRequest, ApprovalResponse
from backend.services.execution import execution_service, get_state_snapshot
from backend.graph.checkpoints import STATE_SNAPSHOTS
from backend.services.audit import audit_service, AUDIT_LOG_STORE
from backend.services.metrics import metrics_service
from backend.mcp.clients import mcp_client
from backend.policy.engine import policy_engine

router = APIRouter(prefix="/api/v1")


class RunRequest(BaseModel):
    query: str
    tenant_id: Optional[str] = "enterprise_demo"


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(req: LoginRequest):
    # Demo authentication: allows admin, analyst, viewer
    valid_users = {
        "admin": "admin",
        "analyst_jane": "analyst",
        "viewer_bob": "viewer"
    }
    role = valid_users.get(req.username, "analyst")
    token = create_access_token({"sub": req.username, "role": role, "tenant_id": "enterprise_demo"})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": req.username,
            "role": role,
            "tenant_id": "enterprise_demo"
        }
    }


@router.get("/auth/me")
async def get_me(user: UserOut = Depends(get_current_user)):
    return user


@router.post("/runs")
async def create_run(req: RunRequest, user: UserOut = Depends(get_current_user)):
    """Initialize and trigger a new multi-agent intelligence run."""
    # Safety & injection verification
    safety_check = policy_engine.validate_request_safety(req.query)
    if not safety_check["is_safe"]:
        raise HTTPException(status_code=400, detail=safety_check["reason"])

    run_id = await execution_service.create_and_start_run(
        query=req.query,
        user_id=user.username,
        tenant_id=req.tenant_id or user.tenant_id
    )

    return {
        "run_id": run_id,
        "status": "RUNNING",
        "query": req.query,
        "stream_url": f"/api/v1/runs/{run_id}/stream"
    }


@router.get("/runs")
async def list_runs(user: UserOut = Depends(get_current_user)):
    """List all workflow runs with execution status and metrics."""
    runs = []
    for run_id, state in STATE_SNAPSHOTS.items():
        runs.append({
            "run_id": run_id,
            "query": state.get("query"),
            "status": state.get("status"),
            "current_node": state.get("current_node"),
            "approval_status": state.get("approval_status"),
            "has_approval_pending": (state.get("status") == "WAITING_APPROVAL"),
            "total_tokens": state.get("total_tokens", 0),
            "total_cost": round(state.get("total_cost", 0.0), 4),
            "steps_count": len(state.get("step_history", []))
        })
    return {"runs": list(reversed(runs))}


@router.get("/runs/{run_id}")
async def get_run_details(run_id: str, user: UserOut = Depends(get_current_user)):
    """Retrieve full persistent state, task steps, and report for a specific run."""
    state = get_state_snapshot(run_id)
    if not state:
        raise HTTPException(status_code=404, detail="Run not found.")
    return state


@router.get("/runs/{run_id}/stream")
async def stream_run(run_id: str):
    """Server-Sent Events endpoint streaming live graph node transitions and agent outputs."""
    return StreamingResponse(
        execution_service.event_generator(run_id),
        media_type="text/event-stream"
    )


@router.post("/runs/{run_id}/approve", response_model=ApprovalResponse)
async def approve_run(
    run_id: str,
    req: ApprovalDecisionRequest,
    user: UserOut = Depends(require_role("analyst"))
):
    """Human-in-the-loop approval gate: approve pending action and execute."""
    try:
        res = await execution_service.resolve_approval(
            run_id=run_id,
            decision="APPROVED",
            reviewer=user.username,
            comment=req.comment
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/runs/{run_id}/reject", response_model=ApprovalResponse)
async def reject_run(
    run_id: str,
    req: ApprovalDecisionRequest,
    user: UserOut = Depends(require_role("analyst"))
):
    """Human-in-the-loop approval gate: reject pending action and log audit trail."""
    try:
        res = await execution_service.resolve_approval(
            run_id=run_id,
            decision="REJECTED",
            reviewer=user.username,
            reason=req.comment
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tools")
async def list_tools(user: UserOut = Depends(get_current_user)):
    """List all registered MCP tools and agent access permissions."""
    tools = mcp_client.list_all_tools()
    from backend.mcp.permissions import AGENT_TOOL_PERMISSIONS
    permissions = {agent: list(t_set) for agent, t_set in AGENT_TOOL_PERMISSIONS.items()}
    return {
        "tools": tools,
        "permission_matrix": permissions
    }


@router.get("/metrics")
async def get_system_metrics(user: UserOut = Depends(get_current_user)):
    """Retrieve operational KPIs: task completion, latency p50/p95, cost, accuracy."""
    return metrics_service.get_summary_metrics()


@router.get("/audit")
async def get_audit_trail(run_id: Optional[str] = None, user: UserOut = Depends(get_current_user)):
    """Retrieve immutable audit logs of agent decisions, tool invocations, and approvals."""
    if run_id:
        return {"audit_logs": audit_service.get_run_audit_logs(run_id)}
    return {"audit_logs": list(reversed(AUDIT_LOG_STORE[-100:]))}


@router.post("/n8n/webhook")
async def n8n_callback(payload: Dict[str, Any]):
    """Incoming webhook from n8n for bidirectional workflow automation."""
    logger_msg = f"n8n webhook received event: {payload.get('event')}"
    return {"status": "ACK", "message": logger_msg}
