import pytest
from backend.agents.planner import planner_agent
from backend.agents.analytics import analytics_agent
from backend.agents.researcher import researcher_agent
from backend.agents.forecaster import forecaster_agent
from backend.agents.critic import critic_agent
from backend.agents.reporter import reporter_agent


@pytest.mark.asyncio
async def test_planner_agent():
    plan_out = await planner_agent.create_plan("Analyze revenue drop and forecast next quarter.")
    assert "plan" in plan_out
    assert len(plan_out["plan"]["tasks"]) >= 3


@pytest.mark.asyncio
async def test_analytics_agent():
    res = await analytics_agent.execute("test_run", "Analyze revenue")
    assert res["status"] == "COMPLETED"
    assert "metrics" in res
    assert res["metrics"]["net_revenue_variance_usd"] == -2300000.0


@pytest.mark.asyncio
async def test_researcher_agent():
    res = await researcher_agent.execute("test_run", "Investigate causes")
    assert res["status"] == "COMPLETED"
    assert len(res["evidence"]) > 0


@pytest.mark.asyncio
async def test_forecaster_agent():
    analytics_data = {"metrics": {"net_revenue_variance_usd": -2300000.0}}
    research_data = {"evidence": [{"source": "DOC-1"}]}
    res = await forecaster_agent.execute("Forecast Q4", analytics_data, research_data)
    assert res["status"] == "COMPLETED"
    assert "forecast" in res
    assert "scenarios" in res["forecast"]


@pytest.mark.asyncio
async def test_critic_agent_arithmetic_verification():
    analytics_data = {
        "metrics": {
            "Q2_revenue_usd": 12500000.0,
            "Q3_revenue_usd": 10200000.0,
            "net_revenue_variance_usd": -2300000.0,
            "net_percentage_change": -18.4
        }
    }
    res = await critic_agent.execute("Query", analytics_data, {"evidence": []}, {"forecast": {}})
    assert res["quality_passed"] is True
    assert res["score"] >= 8.5


@pytest.mark.asyncio
async def test_reporter_agent():
    analytics_data = {"metrics": {"net_revenue_variance_usd": -2300000.0}}
    res = await reporter_agent.execute(
        run_id="test_run",
        query="Analyze revenue drop and send to the finance team after approval.",
        analytics_data=analytics_data,
        research_data={"evidence": []},
        forecast_data={"forecast": {}},
        critic_data={"quality_passed": True}
    )
    assert res["status"] == "COMPLETED"
    assert res["report_content"] != ""
    assert res["approval_request"] is not None
    assert res["approval_request"]["action_type"] == "send_approved_email"
