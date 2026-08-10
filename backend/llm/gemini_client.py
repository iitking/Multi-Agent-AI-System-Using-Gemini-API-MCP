import json
import logging
import time
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
from google import genai
from google.genai import types

from backend.config import settings
from backend.llm.model_config import LLMResponse, TokenUsage

logger = logging.getLogger(__name__)


class GeminiClient:
    """Enterprise client for Google Gemini API using official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL
        self.client: Optional[genai.Client] = None

        if self.api_key and self.api_key != "your_gemini_api_key_here":
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google GenAI client with model: {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not initialize GenAI client: {e}. Falling back if enabled.")
        else:
            logger.info("No valid GEMINI_API_KEY found. Mock mode will be used if enabled.")

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        # Standard Gemini 2.5 Flash pricing: ~$0.075 / 1M prompt tokens, ~$0.30 / 1M completion tokens
        cost = (prompt_tokens / 1_000_000.0) * 0.075 + (completion_tokens / 1_000_000.0) * 0.30
        return round(cost, 6)

    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2,
        agent_role: str = "general"
    ) -> LLMResponse:
        """Generate response from Gemini or deterministic mock engine."""
        start_time = time.time()

        if self.client:
            try:
                config_args: Dict[str, Any] = {
                    "temperature": temperature,
                }
                if system_instruction:
                    config_args["system_instruction"] = system_instruction

                if response_schema:
                    config_args["response_mime_type"] = "application/json"
                    config_args["response_schema"] = response_schema

                config = types.GenerateContentConfig(**config_args)
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config
                )

                latency_ms = (time.time() - start_time) * 1000.0
                prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", len(prompt) // 4)
                candidate_tokens = getattr(response.usage_metadata, "candidates_token_count", len(response.text or "") // 4)
                total_tokens = getattr(response.usage_metadata, "total_token_count", prompt_tokens + candidate_tokens)

                structured_data = None
                if response_schema and response.text:
                    try:
                        structured_data = json.loads(response.text)
                    except Exception:
                        pass

                return LLMResponse(
                    content=response.text or "",
                    structured_data=structured_data,
                    token_usage=TokenUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=candidate_tokens,
                        total_tokens=total_tokens,
                        estimated_cost_usd=self._calculate_cost(prompt_tokens, candidate_tokens)
                    ),
                    latency_ms=latency_ms,
                    model_name=self.model_name
                )
            except Exception as e:
                logger.error(f"Gemini API invocation error: {e}")
                if not settings.GEMINI_FALLBACK_TO_MOCK:
                    raise e
                logger.info("Falling back to deterministic agent reasoning engine.")

        # Fallback deterministic enterprise reasoning engine
        return self._generate_mock(prompt, system_instruction, response_schema, agent_role, start_time)

    def _generate_mock(
        self,
        prompt: str,
        system_instruction: Optional[str],
        response_schema: Optional[Type[BaseModel]],
        agent_role: str,
        start_time: float
    ) -> LLMResponse:
        """Deterministic mock responses for evaluation and testing without API key."""
        prompt_tokens = max(len(prompt) // 4, 120)
        completion_tokens = 350
        latency_ms = (time.time() - start_time) * 1000.0 + 85.0

        content = ""
        structured: Dict[str, Any] = {}

        if agent_role == "planner":
            structured = {
                "summary": "Multi-phase revenue drop investigation, KPI calculation, cause analysis, and scenario forecasting plan.",
                "tasks": [
                    {
                        "task_id": "task_1_analytics",
                        "agent": "analytics",
                        "description": "Query sales database via Data MCP to retrieve Q2 vs Q3 revenue breakdowns by product and region.",
                        "tools": ["get_sales_summary", "calculate_kpis", "detect_anomalies"],
                        "dependencies": []
                    },
                    {
                        "task_id": "task_2_research",
                        "agent": "researcher",
                        "description": "Search internal company documents and operational memos via Research MCP regarding Q3 issues.",
                        "tools": ["search_company_docs", "get_document_content"],
                        "dependencies": []
                    },
                    {
                        "task_id": "task_3_forecast",
                        "agent": "forecaster",
                        "description": "Synthesize data metrics and research findings to generate Q4 financial forecasts (Base, Bull, Bear).",
                        "tools": [],
                        "dependencies": ["task_1_analytics", "task_2_research"]
                    },
                    {
                        "task_id": "task_4_critic",
                        "agent": "critic",
                        "description": "Verify calculation accuracy, cross-validate citations, and assess evidence completeness.",
                        "tools": [],
                        "dependencies": ["task_3_forecast"]
                    },
                    {
                        "task_id": "task_5_report",
                        "agent": "reporter",
                        "description": "Synthesize verified findings into formal executive report and flag finance team delivery action.",
                        "tools": ["create_report"],
                        "dependencies": ["task_4_critic"]
                    }
                ],
                "requires_human_approval": True,
                "approval_action": "send_approved_email",
                "estimated_tokens": 1200
            }
            content = json.dumps(structured, indent=2)

        elif agent_role == "analytics":
            structured = {
                "status": "COMPLETED",
                "metrics": {
                    "q2_revenue_usd": 12500000.0,
                    "q3_revenue_usd": 10200000.0,
                    "revenue_variance_usd": -2300000.0,
                    "percentage_change": -18.4,
                    "products": {
                        "CloudPlatform_Core": {"q2": 6000000.0, "q3": 5900000.0, "change_pct": -1.67},
                        "DataSync_Enterprise": {"q2": 3500000.0, "q3": 1800000.0, "change_pct": -48.57},
                        "AI_Intelligence_Suite": {"q2": 3000000.0, "q3": 2500000.0, "change_pct": -16.67}
                    },
                    "regions": {
                        "North_America": {"q2": 6500000.0, "q3": 6100000.0, "change_pct": -6.15},
                        "EMEA": {"q2": 4200000.0, "q3": 2700000.0, "change_pct": -35.71},
                        "APAC": {"q2": 1800000.0, "q3": 1400000.0, "change_pct": -22.22}
                    }
                },
                "anomalies_detected": [
                    "DataSync Enterprise hardware revenue dropped by $1.7M (-48.6%), representing 73.9% of total company revenue decline.",
                    "EMEA regional revenue plunged by $1.5M (-35.7%), indicating localized market or deal execution disruption."
                ],
                "provenance": "PostgreSQL read-only financial data warehouse (table: quarterly_sales_aggregates)"
            }
            content = json.dumps(structured, indent=2)

        elif agent_role == "researcher":
            structured = {
                "status": "COMPLETED",
                "evidence": [
                    {
                        "source": "DOC-2024-EMEA-089",
                        "title": "EMEA Tier-1 Enterprise Renewal Delays",
                        "findings": "3 major enterprise deals valued at $1.4M ACV were deferred from Q3 to Q4 due to EU regulatory compliance audit delays.",
                        "confidence": 0.95,
                        "timestamp": "2024-09-28"
                    },
                    {
                        "source": "DOC-2024-SUPPLY-041",
                        "title": "DataSync Appliance Component Shortage Notice",
                        "findings": "Supplier ChipCorp experienced a critical microcontroller supply constraint, halting DataSync appliance shipments for 6 weeks ($1.6M deferred delivery).",
                        "confidence": 0.98,
                        "timestamp": "2024-08-15"
                    },
                    {
                        "source": "MKT-2024-INTEL-112",
                        "title": "CloudMatrix Competitive Pricing Campaign",
                        "findings": "Competitor CloudMatrix launched a 30% discount offensive in mid-Q3, impacting AI Intelligence Suite entry-tier customer conversions.",
                        "confidence": 0.88,
                        "timestamp": "2024-09-10"
                    }
                ],
                "summary": "Revenue decline was driven by temporary supply chain halts on DataSync hardware ($1.6M) and delayed EMEA enterprise deal closures ($1.4M), rather than systemic structural churn."
            }
            content = json.dumps(structured, indent=2)

        elif agent_role == "forecaster":
            structured = {
                "status": "COMPLETED",
                "forecast_quarter": "Q4",
                "scenarios": {
                    "base_case": {
                        "projected_revenue_usd": 12800000.0,
                        "growth_qoq_pct": 25.49,
                        "assumptions": "Hardware supply chain resumes full production; 80% of deferred EMEA enterprise pipeline closes."
                    },
                    "bull_case": {
                        "projected_revenue_usd": 13600000.0,
                        "growth_qoq_pct": 33.33,
                        "assumptions": "100% of deferred contracts close with accelerated backlogged appliance delivery plus holiday sales expansion."
                    },
                    "bear_case": {
                        "projected_revenue_usd": 11000000.0,
                        "growth_qoq_pct": 7.84,
                        "assumptions": "Supply chain recovery extends 3 weeks into Q4; ongoing price pressure on AI Suite from competitors."
                    }
                },
                "root_cause_attribution": {
                    "supply_chain_hardware_deferral": "65%",
                    "emea_regulatory_audit_delays": "25%",
                    "competitive_pricing_pressure": "10%"
                }
            }
            content = json.dumps(structured, indent=2)

        elif agent_role == "critic":
            structured = {
                "status": "COMPLETED",
                "quality_passed": True,
                "score": 9.4,
                "verification_checks": {
                    "arithmetic_accuracy": "PASSED - $12.5M to $10.2M equals exactly -$2.3M (-18.4%) change.",
                    "product_reconciliation": "PASSED - Component drops sum consistently with observed variance.",
                    "evidence_grounding": "PASSED - All claims linked to verified internal documents DOC-2024-EMEA-089 and DOC-2024-SUPPLY-041.",
                    "forecast_sanity": "PASSED - Scenarios are bounded and mathematically sound."
                },
                "issues": [],
                "feedback": "Analysis is rigorous, mathematically sound, and substantiated by documented evidence."
            }
            content = json.dumps(structured, indent=2)

        elif agent_role == "reporter":
            content = (
                "# Executive Financial & Operational Intelligence Report\n\n"
                "**Subject:** Comprehensive Investigation of Q3 Revenue Decline and Q4 Outlook\n"
                "**Classification:** Confidential - Executive & Finance Committee\n\n"
                "## 1. Executive Summary\n"
                "Total company revenue decreased from **$12.50M in Q2** to **$10.20M in Q3** (-$2.30M or **-18.4%**). "
                "Our cross-functional multi-agent investigation confirms that this contraction is **non-structural and recoverable**, "
                "primarily driven by two discrete operational bottlenecks:\n"
                "1. **Supply Chain Disruption (Hardware Appliance Line):** A 6-week microcontroller shortage at primary supplier ChipCorp halted DataSync shipments, deferring $1.6M in recognized revenue.\n"
                "2. **EMEA Enterprise Contract Deferrals:** $1.4M ACV across 3 tier-1 telecom renewals slipped into Q4 due to mandatory EU regulatory compliance audits.\n\n"
                "## 2. Product & Regional Performance Breakdown\n\n"
                "| Product Line | Q2 Revenue | Q3 Revenue | Variance ($) | Variance (%) |\n"
                "|---|---|---|---|---|\n"
                "| CloudPlatform Core | $6.00M | $5.90M | -$0.10M | -1.7% |\n"
                "| DataSync Enterprise | $3.50M | $1.80M | -$1.70M | -48.6% |\n"
                "| AI Intelligence Suite | $3.00M | $2.50M | -$0.50M | -16.7% |\n"
                "| **Total** | **$12.50M** | **$10.20M** | **-$2.30M** | **-18.4%** |\n\n"
                "## 3. Evidence-Backed Root Cause Analysis\n"
                "- **DataSync Appliance Contraction (DOC-2024-SUPPLY-041):** Accounted for 73.9% of the net dollar decline. Production is back online with backlog shipments underway.\n"
                "- **EMEA Deal Postponement (DOC-2024-EMEA-089):** The contracts remain intact; legal review is scheduled for final signature in the first week of next month.\n"
                "- **Competitive Dynamics (MKT-2024-INTEL-112):** CloudMatrix discounting impacted entry-tier AI Suite deals. Enterprise retention remained high at 96.2%.\n\n"
                "## 4. Q4 Financial Forecast Scenarios\n"
                "- **Base Case (Most Likely): $12.80M (+25.5% QoQ)** — Full clearance of hardware backorders and closure of delayed EMEA contracts.\n"
                "- **Bull Case: $13.60M (+33.3% QoQ)** — Full backlog fulfillment plus accelerated year-end renewals.\n"
                "- **Bear Case: $11.00M (+7.8% QoQ)** — Partial supply friction extending into early quarter.\n\n"
                "## 5. Strategic Recommendations & Actions\n"
                "1. **Dual-Sourcing Key Components:** Qualify secondary supplier for microcontrollers by end of month.\n"
                "2. **EMEA Fast-Track Desk:** Establish dedicated regulatory pre-clearance task force for EMEA enterprise deals.\n"
                "3. **Value Bundling:** Bundle AI Suite features with CloudPlatform Core to counter competitor discounting.\n\n"
                "> **Action Required:** Disseminate this audited analysis to the Executive Finance Committee via automated email distribution upon human approval.\n"
            )
            structured = {
                "title": "Comprehensive Investigation of Q3 Revenue Decline and Q4 Outlook",
                "summary": "Net decline of $2.3M (-18.4%) was verified as non-structural, caused by $1.6M hardware supply constraints and $1.4M EMEA deal deferrals. Base forecast projects recovery to $12.8M in Q4.",
                "proposed_external_action": {
                    "action_type": "send_approved_email",
                    "recipient": "finance-leadership@apexcloud.io",
                    "subject": "Audited Q3 Financial Intelligence & Q4 Recovery Report",
                    "summary": "Send full audited revenue decline and Q4 forecast report to Executive Finance Committee."
                }
            }

        else:
            content = f"Processed request for role: {agent_role}"
            structured = {"result": content}

        return LLMResponse(
            content=content,
            structured_data=structured,
            token_usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                estimated_cost_usd=self._calculate_cost(prompt_tokens, completion_tokens)
            ),
            latency_ms=latency_ms,
            model_name=self.model_name
        )


gemini_client = GeminiClient()
