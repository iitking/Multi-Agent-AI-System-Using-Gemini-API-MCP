from typing import Dict, Any, List

BENCHMARK_EVAL_DATASET = [
    {
        "id": "BENCH-001-REVENUE-DROP",
        "query": (
            "Analyze why our revenue dropped this quarter, compare product performance, "
            "investigate the likely causes, forecast next quarter, and prepare an evidence-backed report. "
            "Send it to the finance team after approval."
        ),
        "expected_metrics": {
            "q2_revenue_usd": 12500000.0,
            "q3_revenue_usd": 10200000.0,
            "net_variance_usd": -2300000.0,
            "net_percentage_change": -18.4,
            "primary_product_drop": "DataSync_Enterprise",
            "primary_product_loss_usd": 1700000.0,
            "primary_region_drop": "EMEA",
            "primary_region_loss_usd": 1500000.0
        },
        "expected_citations": [
            "DOC-2024-EMEA-089",
            "DOC-2024-SUPPLY-041"
        ],
        "expected_forecast_range": {
            "base_case_min": 12000000.0,
            "base_case_max": 13500000.0
        },
        "requires_human_approval": True,
        "consequential_action": "send_approved_email"
    },
    {
        "id": "BENCH-002-PRODUCT-ANOMALY",
        "query": "Identify products that experienced revenue drops worse than -30% in Q3 and calculate their dollar loss.",
        "expected_metrics": {
            "anomalous_product": "DataSync_Enterprise",
            "percentage_change": -48.6,
            "dollar_loss_usd": 1700000.0
        },
        "expected_citations": ["DOC-2024-SUPPLY-041"],
        "requires_human_approval": False
    }
]
