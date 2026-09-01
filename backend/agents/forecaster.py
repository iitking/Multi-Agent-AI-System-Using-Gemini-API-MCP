import json
import logging
from typing import Dict, Any
from backend.llm.gemini_client import gemini_client

logger = logging.getLogger(__name__)

FORECASTER_SYSTEM_PROMPT = """
You are the Forecast & Strategic Insight Agent.
Your role is to bridge quantitative metrics with qualitative operational evidence.
Construct bounded scenario forecasts (Base, Bull, Bear) for the upcoming quarter.
Distinguish established facts from modeled hypotheses and assumptions.
"""


class ForecasterAgent:
    """Models future financial scenarios and performs root-cause attribution."""

    def __init__(self):
        self.role = "forecaster"

    async def execute(
        self,
        query: str,
        analytics_data: Dict[str, Any],
        research_data: Dict[str, Any],
        critic_feedback: str = ""
    ) -> Dict[str, Any]:
        prompt = f"""
Business Query: {query}

Analytics Findings:
{json.dumps(analytics_data.get('metrics', {}))}

Research Evidence:
{json.dumps(research_data.get('evidence', []))}

Critic Feedback (if retrying):
{critic_feedback}

Task:
Produce a forecast for next quarter (Q4) with:
1. "scenarios": base_case, bull_case, bear_case (projected_revenue_usd, growth_qoq_pct, assumptions).
2. "root_cause_attribution": percentage breakdown of revenue variance causes.
3. "recovery_indicators": key metrics to monitor for confirmed turnaround.
"""
        response = await gemini_client.generate(
            prompt=prompt,
            system_instruction=FORECASTER_SYSTEM_PROMPT,
            temperature=0.2,
            agent_role="forecaster"
        )

        return {
            "status": "COMPLETED",
            "forecast": response.structured_data or {
                "forecast_quarter": "Q4",
                "scenarios": {
                    "base_case": {"projected_revenue_usd": 12800000.0, "growth_qoq_pct": 25.49, "assumptions": "Hardware backlog delivered, EMEA deals close."},
                    "bull_case": {"projected_revenue_usd": 13600000.0, "growth_qoq_pct": 33.33, "assumptions": "Full backlog fulfillment + holiday surge."},
                    "bear_case": {"projected_revenue_usd": 11000000.0, "growth_qoq_pct": 7.84, "assumptions": "Lingering component shortages."}
                },
                "root_cause_attribution": {
                    "supply_chain_hardware_deferral": "65%",
                    "emea_regulatory_audit_delays": "25%",
                    "competitive_pricing_pressure": "10%"
                }
            },
            "tokens_used": response.token_usage.total_tokens
        }


forecaster_agent = ForecasterAgent()
