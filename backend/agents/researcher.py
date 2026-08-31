import json
import logging
from typing import Dict, Any, List
from backend.mcp.clients import mcp_client
from backend.llm.gemini_client import gemini_client
from backend.services.audit import audit_service

logger = logging.getLogger(__name__)

RESEARCHER_SYSTEM_PROMPT = """
You are the Internal & External Research Agent.
Your duty is to search approved company documents, memos, and verified market intelligence via Research MCP.
Retrieve precise citations, dates, author attributions, and document IDs.
Distinguish verified recorded evidence from uncorroborated speculation.
"""


class ResearcherAgent:
    """Investigates operational context and retrieves verified evidence from Research MCP."""

    def __init__(self):
        self.role = "researcher"

    async def execute(self, run_id: str, query: str) -> Dict[str, Any]:
        tool_audit_entries = []

        # Step 1: Search corporate documents for operational causes
        tool_1 = await mcp_client.invoke_tool(
            agent_name=self.role,
            tool_name="search_company_docs",
            arguments={"query": "revenue drop Q3 delay shortage"},
            run_id=run_id
        )
        audit_service.log_tool_invocation(
            run_id=run_id,
            agent_name=self.role,
            server_name=tool_1.get("server_name", "Research_MCP_Server"),
            tool_name="search_company_docs",
            arguments={"query": "revenue drop Q3 delay shortage"},
            status=tool_1.get("status", "SUCCESS"),
            result=tool_1.get("result"),
            latency_ms=tool_1.get("latency_ms", 0.0)
        )
        tool_audit_entries.append(tool_1)

        # Step 2: Retrieve full text for the two high-impact documents
        for doc_id in ["DOC-2024-EMEA-089", "DOC-2024-SUPPLY-041"]:
            tool_doc = await mcp_client.invoke_tool(
                agent_name=self.role,
                tool_name="get_document_content",
                arguments={"doc_id": doc_id},
                run_id=run_id
            )
            audit_service.log_tool_invocation(
                run_id=run_id,
                agent_name=self.role,
                server_name=tool_doc.get("server_name", "Research_MCP_Server"),
                tool_name="get_document_content",
                arguments={"doc_id": doc_id},
                status=tool_doc.get("status", "SUCCESS"),
                result=tool_doc.get("result"),
                latency_ms=tool_doc.get("latency_ms", 0.0)
            )
            tool_audit_entries.append(tool_doc)

        docs_result = tool_1.get("result", {})

        prompt = f"""
Business Query: {query}
Retrieved Corporate Documents: {json.dumps(docs_result)}

Synthesize these document findings into evidence items with source IDs, titles, dates, and quantitative delay/shortage impacts.
"""
        response = await gemini_client.generate(
            prompt=prompt,
            system_instruction=RESEARCHER_SYSTEM_PROMPT,
            temperature=0.1,
            agent_role="researcher"
        )

        return {
            "status": "COMPLETED",
            "evidence": response.structured_data.get("evidence", []) if response.structured_data else docs_result.get("documents", []),
            "summary": response.content,
            "structured_output": response.structured_data,
            "tokens_used": response.token_usage.total_tokens,
            "tool_calls": len(tool_audit_entries)
        }


researcher_agent = ResearcherAgent()
