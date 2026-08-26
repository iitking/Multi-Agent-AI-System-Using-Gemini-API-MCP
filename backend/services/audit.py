import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("audit")

# In-memory audit log store for runs
AUDIT_LOG_STORE: List[Dict[str, Any]] = []


class AuditService:
    """Service to record immutable audit logs of agent decisions and tool invocations."""

    @staticmethod
    def log_tool_invocation(
        run_id: str,
        agent_name: str,
        server_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        latency_ms: float = 0.0,
        tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        sanitized_args = dict(arguments)
        if "approval_token" in sanitized_args:
            # Mask sensitive tokens in audit logs
            token_val = sanitized_args["approval_token"]
            sanitized_args["approval_token"] = f"{token_val[:4]}...{token_val[-4:]}" if len(token_val) > 8 else "***"

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": run_id,
            "agent_name": agent_name,
            "server_name": server_name,
            "tool_name": tool_name,
            "arguments": sanitized_args,
            "status": status,
            "result_summary": str(result)[:300] if result else None,
            "error_message": error_message,
            "latency_ms": round(latency_ms, 2),
            "tenant_id": tenant_id
        }
        AUDIT_LOG_STORE.append(entry)
        logger.info(f"AUDIT [{status}] Run={run_id} Agent={agent_name} Tool={tool_name} Latency={latency_ms:.1f}ms")
        return entry

    @staticmethod
    def get_run_audit_logs(run_id: str) -> List[Dict[str, Any]]:
        return [entry for entry in AUDIT_LOG_STORE if entry["run_id"] == run_id]


audit_service = AuditService()
