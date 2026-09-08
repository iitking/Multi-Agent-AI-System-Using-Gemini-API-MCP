import operator
from typing import TypedDict, List, Dict, Any, Optional, Annotated


def last_str(current: str, update: str) -> str:
    return update


class AgentWorkflowState(TypedDict):
    """Shared persistent state across all agents and nodes in LangGraph workflow."""
    run_id: str
    user_id: str
    tenant_id: str
    query: str

    # Plan
    plan: Dict[str, Any]

    # Specialist Agent Outputs
    analytics_results: Dict[str, Any]
    research_results: Dict[str, Any]
    forecast_results: Dict[str, Any]
    critic_results: Dict[str, Any]

    # Bounded Retry Tracking
    retry_count: int
    max_retries: int
    quality_passed: bool

    # Report & Actions
    report_results: Dict[str, Any]
    approval_record: Optional[Dict[str, Any]]
    approval_status: str  # NONE, PENDING, APPROVED, REJECTED
    action_execution_result: Optional[Dict[str, Any]]

    # Observability & Lifecycle with LangGraph concurrent reducers
    status: Annotated[str, last_str]
    current_node: Annotated[str, last_str]
    step_history: Annotated[List[Dict[str, Any]], operator.add]
    total_tokens: Annotated[int, operator.add]
    total_cost: Annotated[float, operator.add]
    errors: Annotated[List[str], operator.add]
