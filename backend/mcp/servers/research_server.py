from typing import Dict, Any, List, Optional

# Approved repository of internal corporate memos, operational reports, and market intelligence
COMPANY_DOCUMENTS = [
    {
        "doc_id": "DOC-2024-EMEA-089",
        "title": "EMEA Tier-1 Enterprise Contract Renewal Deferrals",
        "category": "sales_operations",
        "date": "2024-09-28",
        "author": "Marcus Vance, VP EMEA Sales",
        "content": (
            "Three tier-1 telecommunications clients in Frankfurt and London (total ACV: $1.40M) "
            "deferred final signature from late Q3 into Q4. The delay resulted from newly mandated "
            "EU NIS2 cybersecurity compliance audits. All three clients have confirmed budget reservation, "
            "and contracts are scheduled for formal signature in October."
        ),
        "tags": ["EMEA", "sales", "contracts", "regulatory", "deferral"]
    },
    {
        "doc_id": "DOC-2024-SUPPLY-041",
        "title": "DataSync Hardware Appliance Component Supply Halts",
        "category": "supply_chain",
        "date": "2024-08-15",
        "author": "Elena Rostova, Head of Hardware Operations",
        "content": (
            "Primary semiconductor supplier ChipCorp declared force majeure on the CX-90 microcontroller, "
            "resulting in a 6-week factory stoppage at our assembly facility. Consequently, 240 units "
            "of DataSync Enterprise hardware ($1.60M in delivered revenue) were deferred to Q4 delivery. "
            "ChipCorp factory output has resumed, and backlogged units are actively being fulfilled."
        ),
        "tags": ["hardware", "DataSync", "supply_chain", "shipments", "backlog"]
    },
    {
        "doc_id": "MKT-2024-INTEL-112",
        "title": "CloudMatrix Competitive Pricing Campaign Analysis",
        "category": "market_intelligence",
        "date": "2024-09-10",
        "author": "Strategic Intelligence Group",
        "content": (
            "In July, competitor CloudMatrix launched an aggressive 30% price discount on introductory "
            "AI analytics tiers. This temporarily slowed self-serve customer additions for our "
            "AI Intelligence Suite, contributing approximately $0.4M to our Q3 top-line softness. "
            "However, enterprise contract renewals remained stable at 96.2% retention."
        ),
        "tags": ["competition", "pricing", "AI_Suite", "churn", "market"]
    },
    {
        "doc_id": "FIN-2024-Q3-PREVIEW",
        "title": "Preliminary Q3 Revenue Variance and Working Capital Report",
        "category": "finance",
        "date": "2024-10-02",
        "author": "Corporate Controller",
        "content": (
            "Consolidated revenue for Q3 finished at $10.20M, compared to $12.50M in Q2. "
            "The $2.30M decline is concentrated in DataSync (-$1.70M) and EMEA (-$1.50M). "
            "Operating cash flow remains positive at $2.1M. Deferred bookings pipeline for Q4 stands at $3.8M."
        ),
        "tags": ["finance", "quarterly", "cash_flow", "pipeline"]
    }
]


class ResearchMCPServer:
    """MCP Server exposing authorized document search and knowledge retrieval tools."""

    name = "Research_MCP_Server"

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "search_company_docs",
                "description": "Search verified company documents, post-mortems, and internal memoranda by keyword or category.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search keyword or topic"},
                        "category": {"type": "string", "description": "Optional category filter: sales_operations, supply_chain, market_intelligence, finance"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "search_approved_sources",
                "description": "Search external industry reports and vetted market benchmarks.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query for approved market data"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_document_content",
                "description": "Retrieve full unabridged content of a specific verified document by its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "doc_id": {"type": "string", "description": "Document ID e.g. DOC-2024-EMEA-089"}
                    },
                    "required": ["doc_id"]
                }
            }
        ]

    def search_company_docs(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        q = query.lower()
        results = []

        for doc in COMPANY_DOCUMENTS:
            if category and doc["category"].lower() != category.lower():
                continue
            text_match = (
                q in doc["title"].lower() or
                q in doc["content"].lower() or
                any(q in tag.lower() for tag in doc["tags"])
            )
            if text_match or "revenue" in q or "drop" in q or "q3" in q or "cause" in q:
                results.append({
                    "doc_id": doc["doc_id"],
                    "title": doc["title"],
                    "category": doc["category"],
                    "date": doc["date"],
                    "author": doc["author"],
                    "snippet": doc["content"][:200] + "...",
                    "tags": doc["tags"]
                })

        return {
            "query": query,
            "total_matches": len(results),
            "documents": results
        }

    def search_approved_sources(self, query: str) -> Dict[str, Any]:
        return {
            "query": query,
            "approved_sources": [
                {
                    "source": "Gartner Enterprise Cloud Index",
                    "date": "2024-Q3",
                    "insight": "Enterprise cloud spending expanded 14% YoY; localized compliance mandates caused temporary Q3 closing friction in EMEA."
                },
                {
                    "source": "Semiconductor Supply Chain Weekly",
                    "date": "2024-09",
                    "insight": "Industrial microcontroller lead times recovered from 22 weeks to normal 6-week averages by late September."
                }
            ]
        }

    def get_document_content(self, doc_id: str) -> Dict[str, Any]:
        for doc in COMPANY_DOCUMENTS:
            if doc["doc_id"].upper() == doc_id.upper():
                return {
                    "found": True,
                    "doc": doc
                }
        return {
            "found": False,
            "error": f"Document ID '{doc_id}' not found in authorized document store."
        }


research_server = ResearchMCPServer()
