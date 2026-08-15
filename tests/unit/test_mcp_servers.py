import pytest
from backend.mcp.servers.data_server import data_server
from backend.mcp.servers.research_server import research_server
from backend.mcp.servers.document_server import document_server
from backend.mcp.servers.automation_server import automation_server


def test_data_mcp_sales_summary():
    summary = data_server.get_sales_summary(quarter="all")
    assert summary["record_count"] > 0
    assert "breakdown_by_quarter" in summary
    assert "Q2" in summary["breakdown_by_quarter"]
    assert "Q3" in summary["breakdown_by_quarter"]


def test_data_mcp_kpi_calculation():
    kpis = data_server.calculate_kpis(base_quarter="Q2", target_quarter="Q3")
    assert kpis["Q2_revenue_usd"] == 12500000.0
    assert kpis["Q3_revenue_usd"] == 10200000.0
    assert kpis["net_revenue_variance_usd"] == -2300000.0
    assert kpis["net_percentage_change"] == -18.4


def test_data_mcp_anomaly_detection():
    anomalies = data_server.detect_anomalies(threshold_pct=-15.0)
    assert anomalies["anomalies_detected_count"] >= 1
    # DataSync should be identified as anomalous drop
    product_names = [a["entity"] for a in anomalies["anomalies"]]
    assert "DataSync_Enterprise" in product_names


def test_research_mcp_document_search():
    res = research_server.search_company_docs(query="delay")
    assert res["total_matches"] >= 1
    doc_ids = [d["doc_id"] for d in res["documents"]]
    assert "DOC-2024-EMEA-089" in doc_ids or "DOC-2024-SUPPLY-041" in doc_ids


def test_document_mcp_report_creation():
    rep = document_server.create_report(
        title="Test Report",
        sections=[{"heading": "Summary", "content": "Test content"}]
    )
    assert rep["status"] == "CREATED"
    assert rep["report_id"].startswith("REP-")


@pytest.mark.asyncio
async def test_automation_mcp_token_required():
    # Attempting action without approval token must fail
    with pytest.raises(PermissionError):
        await automation_server.send_approved_email(
            to="test@company.com",
            subject="Test",
            body="Test body",
            approval_token=""
        )

    # Valid token succeeds
    res = await automation_server.send_approved_email(
        to="finance@apexcloud.io",
        subject="Approved Report",
        body="Attached",
        approval_token="APPR-TEST-VALID-TOKEN-123"
    )
    assert res["status"] == "SUCCESS"
