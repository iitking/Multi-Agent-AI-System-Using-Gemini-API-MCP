import math
from typing import Dict, Any, List, Optional

# Authorized in-memory read-only sales data warehouse
QUARTERLY_SALES_DATA = [
    # Q1
    {"quarter": "Q1", "region": "North_America", "product": "CloudPlatform_Core", "revenue": 5800000.0, "units": 580, "churn_pct": 2.1},
    {"quarter": "Q1", "region": "North_America", "product": "DataSync_Enterprise", "revenue": 3400000.0, "units": 170, "churn_pct": 1.8},
    {"quarter": "Q1", "region": "North_America", "product": "AI_Intelligence_Suite", "revenue": 2700000.0, "units": 270, "churn_pct": 3.0},
    {"quarter": "Q1", "region": "EMEA", "product": "CloudPlatform_Core", "revenue": 2100000.0, "units": 210, "churn_pct": 2.4},
    {"quarter": "Q1", "region": "EMEA", "product": "DataSync_Enterprise", "revenue": 1200000.0, "units": 60, "churn_pct": 1.9},
    {"quarter": "Q1", "region": "EMEA", "product": "AI_Intelligence_Suite", "revenue": 800000.0, "units": 80, "churn_pct": 2.5},
    {"quarter": "Q1", "region": "APAC", "product": "CloudPlatform_Core", "revenue": 900000.0, "units": 90, "churn_pct": 2.0},
    {"quarter": "Q1", "region": "APAC", "product": "DataSync_Enterprise", "revenue": 500000.0, "units": 25, "churn_pct": 2.1},
    {"quarter": "Q1", "region": "APAC", "product": "AI_Intelligence_Suite", "revenue": 300000.0, "units": 30, "churn_pct": 2.8},

    # Q2
    {"quarter": "Q2", "region": "North_America", "product": "CloudPlatform_Core", "revenue": 3200000.0, "units": 320, "churn_pct": 2.0},
    {"quarter": "Q2", "region": "North_America", "product": "DataSync_Enterprise", "revenue": 2000000.0, "units": 100, "churn_pct": 1.7},
    {"quarter": "Q2", "region": "North_America", "product": "AI_Intelligence_Suite", "revenue": 1300000.0, "units": 130, "churn_pct": 2.9},
    {"quarter": "Q2", "region": "EMEA", "product": "CloudPlatform_Core", "revenue": 2000000.0, "units": 200, "churn_pct": 2.2},
    {"quarter": "Q2", "region": "EMEA", "product": "DataSync_Enterprise", "revenue": 1100000.0, "units": 55, "churn_pct": 2.0},
    {"quarter": "Q2", "region": "EMEA", "product": "AI_Intelligence_Suite", "revenue": 1100000.0, "units": 110, "churn_pct": 2.6},
    {"quarter": "Q2", "region": "APAC", "product": "CloudPlatform_Core", "revenue": 800000.0, "units": 80, "churn_pct": 1.9},
    {"quarter": "Q2", "region": "APAC", "product": "DataSync_Enterprise", "revenue": 400000.0, "units": 20, "churn_pct": 2.2},
    {"quarter": "Q2", "region": "APAC", "product": "AI_Intelligence_Suite", "revenue": 600000.0, "units": 60, "churn_pct": 2.7},

    # Q3
    {"quarter": "Q3", "region": "North_America", "product": "CloudPlatform_Core", "revenue": 3200000.0, "units": 320, "churn_pct": 2.2},
    {"quarter": "Q3", "region": "North_America", "product": "DataSync_Enterprise", "revenue": 1500000.0, "units": 75, "churn_pct": 2.5},
    {"quarter": "Q3", "region": "North_America", "product": "AI_Intelligence_Suite", "revenue": 1400000.0, "units": 140, "churn_pct": 3.8},
    {"quarter": "Q3", "region": "EMEA", "product": "CloudPlatform_Core", "revenue": 2000000.0, "units": 200, "churn_pct": 2.3},
    {"quarter": "Q3", "region": "EMEA", "product": "DataSync_Enterprise", "revenue": 100000.0, "units": 5, "churn_pct": 5.4},  # major collapse due to supply halt
    {"quarter": "Q3", "region": "EMEA", "product": "AI_Intelligence_Suite", "revenue": 600000.0, "units": 60, "churn_pct": 4.1},  # contract delay
    {"quarter": "Q3", "region": "APAC", "product": "CloudPlatform_Core", "revenue": 700000.0, "units": 70, "churn_pct": 2.0},
    {"quarter": "Q3", "region": "APAC", "product": "DataSync_Enterprise", "revenue": 200000.0, "units": 10, "churn_pct": 3.5},
    {"quarter": "Q3", "region": "APAC", "product": "AI_Intelligence_Suite", "revenue": 500000.0, "units": 50, "churn_pct": 3.2},
]


class DataMCPServer:
    """MCP Server exposing read-only sales data and KPI calculation tools."""

    name = "Data_MCP_Server"

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "get_sales_summary",
                "description": "Retrieve aggregated revenue, volume, and churn breakdown by quarter, region, and product category.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "quarter": {"type": "string", "description": "e.g., Q1, Q2, Q3, or all"},
                        "region": {"type": "string", "description": "Optional region filter: North_America, EMEA, APAC"},
                        "product": {"type": "string", "description": "Optional product filter"}
                    }
                }
            },
            {
                "name": "query_readonly_database",
                "description": "Execute a secure, sanitized read-only analytical SQL query on financial tables.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sql_query": {"type": "string", "description": "SELECT query to execute"}
                    },
                    "required": ["sql_query"]
                }
            },
            {
                "name": "calculate_kpis",
                "description": "Calculate quarter-over-quarter percentage variance, growth rate, and product margin change.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "base_quarter": {"type": "string", "description": "Base comparison quarter, e.g. Q2"},
                        "target_quarter": {"type": "string", "description": "Target comparison quarter, e.g. Q3"}
                    },
                    "required": ["base_quarter", "target_quarter"]
                }
            },
            {
                "name": "detect_anomalies",
                "description": "Scan product lines and regions for statistical revenue declines exceeding threshold.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "threshold_pct": {"type": "number", "description": "Threshold drop percentage (default: -15.0)"}
                    }
                }
            }
        ]

    def get_sales_summary(self, quarter: Optional[str] = None, region: Optional[str] = None, product: Optional[str] = None) -> Dict[str, Any]:
        filtered = QUARTERLY_SALES_DATA
        if quarter and quarter.lower() != "all":
            filtered = [r for r in filtered if r["quarter"].upper() == quarter.upper()]
        if region:
            filtered = [r for r in filtered if r["region"].lower() == region.lower()]
        if product:
            filtered = [r for r in filtered if product.lower() in r["product"].lower()]

        total_rev = sum(r["revenue"] for r in filtered)
        total_units = sum(r["units"] for r in filtered)
        avg_churn = sum(r["churn_pct"] for r in filtered) / max(len(filtered), 1)

        by_quarter: Dict[str, float] = {}
        by_product: Dict[str, float] = {}
        by_region: Dict[str, float] = {}

        for r in filtered:
            by_quarter[r["quarter"]] = by_quarter.get(r["quarter"], 0.0) + r["revenue"]
            by_product[r["product"]] = by_product.get(r["product"], 0.0) + r["revenue"]
            by_region[r["region"]] = by_region.get(r["region"], 0.0) + r["revenue"]

        return {
            "record_count": len(filtered),
            "total_revenue_usd": round(total_rev, 2),
            "total_units": total_units,
            "average_churn_pct": round(avg_churn, 2),
            "breakdown_by_quarter": {k: round(v, 2) for k, v in by_quarter.items()},
            "breakdown_by_product": {k: round(v, 2) for k, v in by_product.items()},
            "breakdown_by_region": {k: round(v, 2) for k, v in by_region.items()},
        }

    def query_readonly_database(self, sql_query: str) -> Dict[str, Any]:
        # Enforce read-only policy
        sanitized = sql_query.strip().lower()
        if not sanitized.startswith("select"):
            raise PermissionError("Only SELECT queries are authorized on read-only database.")
        for forbidden in ["insert", "update", "delete", "drop", "alter", "truncate", "grant"]:
            if f" {forbidden} " in f" {sanitized} ":
                raise PermissionError(f"Prohibited SQL keyword detected: {forbidden.upper()}")

        # Return synthesized tabular aggregation
        summary = self.get_sales_summary(quarter="all")
        return {
            "query": sql_query,
            "status": "EXECUTED",
            "columns": ["quarter", "revenue_usd", "records"],
            "rows": [
                {"quarter": q, "revenue_usd": rev, "records": 9}
                for q, rev in summary["breakdown_by_quarter"].items()
            ],
            "execution_time_ms": 3.8
        }

    def calculate_kpis(self, base_quarter: str = "Q2", target_quarter: str = "Q3") -> Dict[str, Any]:
        base_data = self.get_sales_summary(quarter=base_quarter)
        target_data = self.get_sales_summary(quarter=target_quarter)

        base_rev = base_data["total_revenue_usd"]
        target_rev = target_data["total_revenue_usd"]
        variance = target_rev - base_rev
        pct_change = (variance / base_rev * 100.0) if base_rev else 0.0

        # Product breakdown change
        prod_analysis = {}
        for prod, b_rev in base_data["breakdown_by_product"].items():
            t_rev = target_data["breakdown_by_product"].get(prod, 0.0)
            diff = t_rev - b_rev
            p_change = (diff / b_rev * 100.0) if b_rev else 0.0
            prod_analysis[prod] = {
                f"{base_quarter}_usd": round(b_rev, 2),
                f"{target_quarter}_usd": round(t_rev, 2),
                "variance_usd": round(diff, 2),
                "percentage_change": round(p_change, 2),
                "share_of_total_drop_pct": round((abs(diff) / abs(variance) * 100.0), 2) if diff < 0 and variance < 0 else 0.0
            }

        return {
            "base_quarter": base_quarter,
            "target_quarter": target_quarter,
            f"{base_quarter}_revenue_usd": round(base_rev, 2),
            f"{target_quarter}_revenue_usd": round(target_rev, 2),
            "net_revenue_variance_usd": round(variance, 2),
            "net_percentage_change": round(pct_change, 2),
            "product_analysis": prod_analysis
        }

    def detect_anomalies(self, threshold_pct: float = -15.0) -> Dict[str, Any]:
        kpis = self.calculate_kpis(base_quarter="Q2", target_quarter="Q3")
        anomalies = []

        for prod, data in kpis["product_analysis"].items():
            if data["percentage_change"] <= threshold_pct:
                anomalies.append({
                    "entity": prod,
                    "type": "PRODUCT_DROP",
                    "percentage_change": data["percentage_change"],
                    "dollar_loss_usd": abs(data["variance_usd"]),
                    "impact_severity": "CRITICAL" if data["percentage_change"] < -30 else "HIGH"
                })

        return {
            "threshold_applied_pct": threshold_pct,
            "anomalies_detected_count": len(anomalies),
            "anomalies": anomalies
        }


data_server = DataMCPServer()
