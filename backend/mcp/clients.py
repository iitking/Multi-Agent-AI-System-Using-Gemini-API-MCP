import time
import logging
from typing import Dict, Any, List, Optional
from backend.policy.engine import policy_engine
from backend.mcp.servers.data_server import data_server
from backend.mcp.servers.research_server import research_server
from backend.mcp.servers.document_server import document_server
from backend.mcp.servers.automation_server import automation_server

logger = logging.getLogger(__name__)


class MCPClientRegistry:
    """Standardized MCP Client adapter to discover, authorize, and invoke tools across MCP servers."""

    def __init__(self):
        self.servers = {
            "data": data_server,
            "research": research_server,
            "document": document_server,
            "automation": automation_server
        }

    def list_all_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from all registered MCP servers."""
        all_tools = []
        for server_name, server in self.servers.items():
            for tool in server.get_tool_definitions():
                tool_copy = dict(tool)
                tool_copy["server_name"] = server.name
                all_tools.append(tool_copy)
        return all_tools

    def get_tools_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Discover tools permitted for a specific agent role."""
        allowed = []
        for tool in self.list_all_tools():
            perm = policy_engine.check_tool_permission(agent_name, tool["name"])
            if perm.get("allowed"):
                allowed.append(tool)
        return allowed

    async def invoke_tool(
        self,
        agent_name: str,
        tool_name: str,
        arguments: Dict[str, Any],
        run_id: str = "run_default"
    ) -> Dict[str, Any]:
        """Authorize and invoke an MCP tool with audit tracking."""
        start_time = time.time()

        # Step 1: Policy Authorization
        auth_check = policy_engine.check_tool_permission(agent_name, tool_name)
        if not auth_check.get("allowed"):
            latency_ms = (time.time() - start_time) * 1000.0
            error_msg = auth_check.get("reason", "Permission denied.")
            return {
                "success": False,
                "error": error_msg,
                "status": "DENIED",
                "latency_ms": latency_ms,
                "tool_name": tool_name,
                "agent_name": agent_name
            }

        # Step 2: Argument Validation
        arg_check = policy_engine.validate_tool_arguments(tool_name, arguments)
        if not arg_check.get("valid"):
            latency_ms = (time.time() - start_time) * 1000.0
            error_msg = arg_check.get("error", "Invalid arguments.")
            return {
                "success": False,
                "error": error_msg,
                "status": "INVALID_ARGUMENTS",
                "latency_ms": latency_ms,
                "tool_name": tool_name
            }

        # Step 3: Route to Server
        try:
            result = None
            server_name = ""

            # Data Server
            if tool_name == "get_sales_summary":
                server_name = data_server.name
                result = data_server.get_sales_summary(**arguments)
            elif tool_name == "query_readonly_database":
                server_name = data_server.name
                result = data_server.query_readonly_database(**arguments)
            elif tool_name == "calculate_kpis":
                server_name = data_server.name
                result = data_server.calculate_kpis(**arguments)
            elif tool_name == "detect_anomalies":
                server_name = data_server.name
                result = data_server.detect_anomalies(**arguments)

            # Research Server
            elif tool_name == "search_company_docs":
                server_name = research_server.name
                result = research_server.search_company_docs(**arguments)
            elif tool_name == "search_approved_sources":
                server_name = research_server.name
                result = research_server.search_approved_sources(**arguments)
            elif tool_name == "get_document_content":
                server_name = research_server.name
                result = research_server.get_document_content(**arguments)

            # Document Server
            elif tool_name == "read_document":
                server_name = document_server.name
                result = document_server.read_document(**arguments)
            elif tool_name == "create_report":
                server_name = document_server.name
                result = document_server.create_report(**arguments)
            elif tool_name == "save_report":
                server_name = document_server.name
                result = document_server.save_report(**arguments)

            # Automation Server
            elif tool_name == "send_approved_email":
                server_name = automation_server.name
                result = await automation_server.send_approved_email(**arguments)
            elif tool_name == "notify_slack":
                server_name = automation_server.name
                result = await automation_server.notify_slack(**arguments)
            elif tool_name == "create_crm_task":
                server_name = automation_server.name
                result = await automation_server.create_crm_task(**arguments)

            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            latency_ms = (time.time() - start_time) * 1000.0
            return {
                "success": True,
                "status": "SUCCESS",
                "result": result,
                "server_name": server_name,
                "tool_name": tool_name,
                "latency_ms": latency_ms,
                "arguments": arguments
            }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "status": "ERROR",
                "error": str(e),
                "tool_name": tool_name,
                "latency_ms": latency_ms
            }


mcp_client = MCPClientRegistry()
