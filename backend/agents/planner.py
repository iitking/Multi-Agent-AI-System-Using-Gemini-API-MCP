import json
import logging
from typing import Dict, Any, List
from backend.llm.gemini_client import gemini_client
from backend.llm.model_config import LLMResponse

logger = logging.getLogger(__name__)

PLANNER_SYSTEM_PROMPT = """
You are the Lead Multi-Agent Supervisor and Strategic Planner in an Enterprise AI Operations Platform.
Your mission is to decompose complex business queries into a rigorous, dependency-aware multi-agent execution graph.

You coordinate:
- 'analytics' agent: Queries read-only database via Data MCP for sales, KPIs, and anomalies.
- 'researcher' agent: Retrieves internal documents, memos, and supplier notices via Research MCP.
- 'forecaster' agent: Synthesizes numbers and evidence into statistical scenarios (Base/Bull/Bear).
- 'critic' agent: Rigorously verifies arithmetic, citations, and evidence sufficiency.
- 'reporter' agent: Compiles executive intelligence reports and identifies consequential actions.

Always enforce safety, tool allowlists, and identify whether the final outcome involves consequential external actions requiring human approval.
"""


class PlannerAgent:
    """Decomposes business queries into structured task execution plans."""

    def __init__(self):
        self.role = "planner"

    async def create_plan(self, query: str, user_role: str = "analyst") -> Dict[str, Any]:
        prompt = f"""
Business Request:
"{query}"

User Role: {user_role}

Please produce a structured JSON execution plan containing:
1. "summary": High level execution strategy.
2. "tasks": An array of tasks with task_id, agent, description, tools, dependencies.
3. "requires_human_approval": true if external delivery/action is requested.
4. "approval_action": tool name if external action is proposed (e.g. send_approved_email).
"""
        response: LLMResponse = await gemini_client.generate(
            prompt=prompt,
            system_instruction=PLANNER_SYSTEM_PROMPT,
            temperature=0.1,
            agent_role="planner"
        )

        plan = response.structured_data or {
            "summary": "Multi-agent analytical and forecasting plan.",
            "tasks": [
                {"task_id": "analytics_task", "agent": "analytics", "tools": ["get_sales_summary", "calculate_kpis", "detect_anomalies"], "dependencies": []},
                {"task_id": "research_task", "agent": "researcher", "tools": ["search_company_docs", "get_document_content"], "dependencies": []},
                {"task_id": "forecast_task", "agent": "forecaster", "tools": [], "dependencies": ["analytics_task", "research_task"]},
                {"task_id": "critic_task", "agent": "critic", "tools": [], "dependencies": ["forecast_task"]},
                {"task_id": "report_task", "agent": "reporter", "tools": ["create_report"], "dependencies": ["critic_task"]}
            ],
            "requires_human_approval": True,
            "approval_action": "send_approved_email"
        }

        return {
            "plan": plan,
            "token_usage": response.token_usage,
            "latency_ms": response.latency_ms
        }


planner_agent = PlannerAgent()
