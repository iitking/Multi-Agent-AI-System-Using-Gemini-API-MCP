import pytest
import asyncio
from backend.services.execution import execution_service, get_state_snapshot


@pytest.mark.asyncio
async def test_end_to_end_multi_agent_workflow():
    query = (
        "Analyze why our revenue dropped this quarter, compare product performance, "
        "investigate the likely causes, forecast next quarter, and prepare an evidence-backed report. "
        "Send it to the finance team after approval."
    )

    run_id = await execution_service.create_and_start_run(
        query=query,
        user_id="analyst_jane",
        tenant_id="enterprise_demo"
    )

    # Wait for workflow to reach approval gate or completion
    state = None
    for _ in range(30):
        await asyncio.sleep(0.3)
        state = get_state_snapshot(run_id)
        if state and state.get("status") in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
            break

    assert state is not None
    assert state.get("status") in ["WAITING_APPROVAL", "COMPLETED"]
    assert state.get("plan") is not None
    assert state.get("analytics_results") is not None
    assert state.get("research_results") is not None
    assert state.get("forecast_results") is not None
    assert state.get("critic_results") is not None
    assert state.get("report_results") is not None

    # Verify human approval request was created
    assert state.get("approval_record") is not None
    assert state.get("approval_record")["action_type"] == "send_approved_email"
