import uuid
import json
import logging
from typing import Dict, Any
from backend.mcp.clients import mcp_client
from backend.llm.gemini_client import gemini_client
from backend.services.audit import audit_service

logger = logging.getLogger(__name__)

REPORTER_SYSTEM_PROMPT = """
You are the Synthesis & Report Agent for Enterprise Operations.
Your task is to compile a formal, high-impact Executive Intelligence Report in Markdown.
Structure the report with:
1. Executive Summary (with variance figures)
2. Product & Regional Breakdown Table
3. Root Cause Analysis (with specific document IDs and citations)
4. Next Quarter Financial Scenarios (Base, Bull, Bear)
5. Strategic Recommendations & Risk Mitigation
6. Actionable Next Steps

If the user requested delivery (e.g. 'Send to the finance team'), formulate the exact proposed external action for Human Approval Gate.
"""


class ReporterAgent:
    """Generates executive reports and creates human approval requests for consequential actions."""

    def __init__(self):
        self.role = "reporter"

    async def execute(
        self,
        run_id: str,
        query: str,
        analytics_data: Dict[str, Any],
        research_data: Dict[str, Any],
        forecast_data: Dict[str, Any],
        critic_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = f"""
Business Request:
{query}

Verified Analytics:
{json.dumps(analytics_data.get('metrics', {}))}

Document Evidence:
{json.dumps(research_data.get('evidence', []))}

Scenario Forecasts:
{json.dumps(forecast_data.get('forecast', {}))}

Quality Review:
{json.dumps(critic_data)}

Generate the complete, publication-ready Executive Report in Markdown.
Also identify any external action requested (e.g. emailing the finance team).
"""
        response = await gemini_client.generate(
            prompt=prompt,
            system_instruction=REPORTER_SYSTEM_PROMPT,
            temperature=0.2,
            agent_role="reporter"
        )

        # Call Document MCP tool to persist report
        doc_tool = await mcp_client.invoke_tool(
            agent_name=self.role,
            tool_name="create_report",
            arguments={
                "title": "Audited Q3 Financial Intelligence & Q4 Recovery Report",
                "sections": [{"heading": "Complete Report", "content": response.content}],
                "format": "markdown"
            },
            run_id=run_id
        )
        audit_service.log_tool_invocation(
            run_id=run_id,
            agent_name=self.role,
            server_name=doc_tool.get("server_name", "Document_MCP_Server"),
            tool_name="create_report",
            arguments={"title": "Audited Q3 Financial Intelligence Report"},
            status=doc_tool.get("status", "SUCCESS"),
            result=doc_tool.get("result"),
            latency_ms=doc_tool.get("latency_ms", 0.0)
        )

        # Check if external delivery was requested in query or prompt
        query_lower = query.lower()
        requires_approval = any(w in query_lower for w in ["send", "email", "notify", "approval", "finance team", "slack"])

        approval_request = None
        if requires_approval:
            approval_token = f"APPR-{uuid.uuid4().hex[:12].upper()}"
            approval_request = {
                "action_type": "send_approved_email",
                "recipient": "finance-leadership@apexcloud.io",
                "subject": "Audited Q3 Financial Intelligence & Q4 Recovery Report",
                "summary": "Email audited revenue decline and Q4 recovery report to the Executive Finance Committee.",
                "approval_token": approval_token,
                "status": "PENDING"
            }

        return {
            "status": "COMPLETED",
            "report_content": response.content,
            "report_id": doc_tool.get("result", {}).get("report_id", f"REP-{run_id[:8]}"),
            "approval_request": approval_request,
            "tokens_used": response.token_usage.total_tokens
        }


reporter_agent = ReporterAgent()
