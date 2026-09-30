from pydantic import BaseModel
from typing import Optional, Dict, Any


class ApprovalDecisionRequest(BaseModel):
    decision: str  # "APPROVED" or "REJECTED"
    reviewer: Optional[str] = "admin"
    comment: Optional[str] = None


class ApprovalResponse(BaseModel):
    status: str
    run_id: str
    action_result: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None
