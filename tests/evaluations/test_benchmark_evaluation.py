import pytest
from backend.evaluation.benchmark import run_benchmark_comparison


@pytest.mark.asyncio
async def test_benchmark_evaluation_comparison():
    res = await run_benchmark_comparison()
    assert res is not None
    assert "single_agent_baseline" in res
    assert "multi_agent_system" in res

    single = res["single_agent_baseline"]
    multi = res["multi_agent_system"]

    # Verify Multi-Agent outscores Single-Agent on mathematical accuracy and gate enforcement
    assert multi["calculation_accuracy_score"] >= single["calculation_accuracy_score"]
    assert multi["human_approval_gate_enforced"] is True
    assert single["human_approval_gate_enforced"] is False
