import json
import logging
from typing import Dict, Any, List
from backend.mcp.clients import mcp_client
from backend.llm.gemini_client import gemini_client
from backend.services.audit import audit_service

logger = logging.getLogger(__name__)

ANALYTICS_SYSTEM_PROMPT = """
You are the Quantitative Analytics Agent.
Your responsibility is to analyze enterprise datasets using authorized Data MCP tools.
Always perform exact mathematical calculations in code and return figures, variances, percentage changes, and provenance.
Never guess or fabricate numbers.
"""


class AnalyticsAgent:
    """Executes quantitative data queries and statistical KPI variance calculations via Data MCP."""

    def __init__(self):
        self.role = "analytics"

    async def execute(self, run_id: str, query: str) -> Dict[str, Any]:
        tool_audit_entries = []

        # Step 1: Query sales summary for Q2 and Q3
        tool_1 = await mcp_client.invoke_tool(
            agent_name=self.role,
            tool_name="get_sales_summary",
            arguments={"quarter": "all"},
            run_id=run_id
        )
        audit_service.log_tool_invocation(
            run_id=run_id,
            agent_name=self.role,
            server_name=tool_1.get("server_name", "Data_MCP_Server"),
            tool_name="get_sales_summary",
            arguments={"quarter": "all"},
            status=tool_1.get("status", "SUCCESS"),
            result=tool_1.get("result"),
            latency_ms=tool_1.get("latency_ms", 0.0)
        )
        tool_audit_entries.append(tool_1)

        # Step 2: Calculate KPIs and variances
        tool_2 = await mcp_client.invoke_tool(
            agent_name=self.role,
            tool_name="calculate_kpis",
            arguments={"base_quarter": "Q2", "target_quarter": "Q3"},
            run_id=run_id
        )
        audit_service.log_tool_invocation(
            run_id=run_id,
            agent_name=self.role,
            server_name=tool_2.get("server_name", "Data_MCP_Server"),
            tool_name="calculate_kpis",
            arguments={"base_quarter": "Q2", "target_quarter": "Q3"},
            status=tool_2.get("status", "SUCCESS"),
            result=tool_2.get("result"),
            latency_ms=tool_2.get("latency_ms", 0.0)
        )
        tool_audit_entries.append(tool_2)

        # Step 3: Scan for critical anomalies
        tool_3 = await mcp_client.invoke_tool(
            agent_name=self.role,
            tool_name="detect_anomalies",
            arguments={"threshold_pct": -15.0},
            run_id=run_id
        )
        audit_service.log_tool_invocation(
            run_id=run_id,
            agent_name=self.role,
            server_name=tool_3.get("server_name", "Data_MCP_Server"),
            tool_name="detect_anomalies",
            arguments={"threshold_pct": -15.0},
            status=tool_3.get("status", "SUCCESS"),
            result=tool_3.get("result"),
            latency_ms=tool_3.get("latency_ms", 0.0)
        )
        tool_audit_entries.append(tool_3)

        # Synthesize with Gemini
        kpi_result = tool_2.get("result", {})
        anomaly_result = tool_3.get("result", {})
        sales_summary = tool_1.get("result", {})

        prompt = f"""
Query: {query}
Sales Data Retrieved: {json.dumps(sales_summary)}
Calculated KPIs: {json.dumps(kpi_result)}
Detected Anomalies: {json.dumps(anomaly_result)}

Synthesize these quantitative findings into a structured analytics result object with exact numbers, product breakdowns, and provenance.
"""
        response = await gemini_client.generate(
            prompt=prompt,
            system_instruction=ANALYTICS_SYSTEM_PROMPT,
            temperature=0.1,
            agent_role="analytics"
        )

        return {
            "status": "COMPLETED",
            "metrics": kpi_result,
            "anomalies": anomaly_result.get("anomalies", []),
            "summary_data": sales_summary,
            "structured_output": response.structured_data,
            "tokens_used": response.token_usage.total_tokens,
            "tool_calls": len(tool_audit_entries)
        }


analytics_agent = AnalyticsAgent()
