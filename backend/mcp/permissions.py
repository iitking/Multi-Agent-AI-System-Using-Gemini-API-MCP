from typing import Dict, List, Set

# Strict mapping of Agent roles to permitted MCP tools
AGENT_TOOL_PERMISSIONS: Dict[str, Set[str]] = {
    "planner": {
        # Planner only orchestrates and does not invoke data mutation tools
    },
    "analytics": {
        "get_sales_summary",
        "query_readonly_database",
        "calculate_kpis",
        "detect_anomalies",
    },
    "researcher": {
        "search_company_docs",
        "search_approved_sources",
        "get_document_content",
    },
    "forecaster": {
        "calculate_kpis",  # Can verify forecast formulas
    },
    "critic": {
        "query_readonly_database",
        "get_document_content",
    },
    "reporter": {
        "read_document",
        "create_report",
        "save_report",
    },
    "action_executor": {
        "send_approved_email",
        "notify_slack",
        "create_crm_task",
    }
}

# Consequential tools requiring human approval tokens
CONSEQUENTIAL_TOOLS: Set[str] = {
    "send_approved_email",
    "notify_slack",
    "create_crm_task",
}


def is_tool_allowed_for_agent(agent_name: str, tool_name: str) -> bool:
    """Validate whether an agent has authorization to execute a specific tool."""
    allowed_tools = AGENT_TOOL_PERMISSIONS.get(agent_name, set())
    return tool_name in allowed_tools


def is_consequential_tool(tool_name: str) -> bool:
    """Check if tool call requires human-in-the-loop approval."""
    return tool_name in CONSEQUENTIAL_TOOLS
