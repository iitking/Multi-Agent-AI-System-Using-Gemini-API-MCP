from typing import Literal
from backend.graph.state import AgentWorkflowState


def route_quality_check(state: AgentWorkflowState) -> Literal["reporter", "forecaster", "escalate"]:
    """Conditional router for the Critic / Quality verification gate."""
    if state.get("quality_passed", False):
        return "reporter"

    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)

    if retry_count < max_retries:
        return "forecaster"
    else:
        return "escalate"


def route_approval_gate(state: AgentWorkflowState) -> Literal["action_executor", "record_rejection", "persister", "wait_approval"]:
    """Conditional router for consequential human-in-the-loop action approval."""
    app_record = state.get("approval_record")
    if not app_record:
        return "persister"

    status = state.get("approval_status", "PENDING")
    if status == "APPROVED":
        return "action_executor"
    elif status == "REJECTED":
        return "record_rejection"
    else:
        # Pauses at human approval gate
        return "wait_approval"
