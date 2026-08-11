import pytest
from backend.llm.gemini_client import gemini_client


@pytest.mark.asyncio
async def test_gemini_client_generation():
    prompt = "Explain why revenue declined."
    res = await gemini_client.generate(prompt=prompt, agent_role="general")
    assert res is not None
    assert res.content != ""
    assert res.token_usage.total_tokens > 0
    assert res.latency_ms >= 0.0


@pytest.mark.asyncio
async def test_gemini_client_planner_role():
    prompt = "Plan revenue analysis"
    res = await gemini_client.generate(prompt=prompt, agent_role="planner")
    assert res.structured_data is not None
    assert "tasks" in res.structured_data
    assert len(res.structured_data["tasks"]) >= 3
