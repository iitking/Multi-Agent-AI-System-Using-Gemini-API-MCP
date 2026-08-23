import re
import logging
from typing import Dict, Any, List, Optional
from backend.mcp.permissions import is_tool_allowed_for_agent, is_consequential_tool

logger = logging.getLogger(__name__)

# Common prompt injection signatures to sanitize
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+instructions",
    r"system\s*:\s*you\s+are\s+now",
    r"disregard\s+(the\s+)?safety\s+guidelines",
    r"bypass\s+(authorization|policy|approval)",
    r"<script[\s\S]*?>",
    r"drop\s+table",
    r"--\s*shutdown",
]


class PolicyEngine:
    """Enterprise policy enforcement for multi-agent tool execution and input safety."""

    def __init__(self):
        self.injection_regexes = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]

    def validate_request_safety(self, text: str) -> Dict[str, Any]:
        """Scan input query or context for malicious prompt injections."""
        if not text:
            return {"is_safe": True, "flags": []}

        flags = []
        for regex in self.injection_regexes:
            if regex.search(text):
                flags.append(f"Matched suspicious pattern: {regex.pattern}")

        if flags:
            logger.warning(f"Potential injection detected: {flags}")
            return {
                "is_safe": False,
                "reason": "Request flagged by prompt injection & safety policy.",
                "flags": flags
            }

        return {"is_safe": True, "flags": []}

    def check_tool_permission(self, agent_name: str, tool_name: str) -> Dict[str, Any]:
        """Verify whether an agent role is authorized to invoke a tool."""
        allowed = is_tool_allowed_for_agent(agent_name, tool_name)
        if not allowed:
            logger.error(f"Policy Violation: Agent '{agent_name}' attempted to invoke unauthorized tool '{tool_name}'")
            return {
                "allowed": False,
                "reason": f"Agent '{agent_name}' is not authorized to call tool '{tool_name}' according to RBAC policy."
            }

        consequential = is_consequential_tool(tool_name)
        return {
            "allowed": True,
            "requires_approval": consequential,
            "tool_name": tool_name,
            "agent_name": agent_name
        }

    def validate_tool_arguments(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate argument types, bounds, and sanitize parameters."""
        if tool_name == "query_readonly_database":
            sql = args.get("sql_query", "")
            if not sql.strip().lower().startswith("select"):
                return {"valid": False, "error": "Only SELECT statements permitted."}

        if tool_name in ["send_approved_email", "notify_slack", "create_crm_task"]:
            token = args.get("approval_token", "")
            if not token or len(token) < 8:
                return {"valid": False, "error": "Valid approval_token required for consequential action."}

        return {"valid": True}


policy_engine = PolicyEngine()
