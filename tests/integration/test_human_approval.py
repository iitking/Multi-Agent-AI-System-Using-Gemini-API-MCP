import pytest
import asyncio
from backend.services.execution import execution_service, get_state_snapshot


@pytest.mark.asyncio
async def test_human_approval_resolution():
    query = "Analyze revenue and send report to finance team after approval."
    run_id = await execution_service.create_and_start_run(query=query)

    # Poll until approval gate reached
    state = None
    for _ in range(50):
        await asyncio.sleep(0.1)
        state = get_state_snapshot(run_id)
        if state and state.get("status") in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
            break

    assert state is not None
    assert state.get("status") == "WAITING_APPROVAL"
    assert state.get("approval_record") is not None

    # Approve action
    res = await execution_service.resolve_approval(
        run_id=run_id,
        decision="APPROVED",
        reviewer="finance_director",
        reason="Verified and approved for dispatch"
    )

    assert res["status"] == "APPROVED"
    updated_state = get_state_snapshot(run_id)
    assert updated_state["status"] == "COMPLETED"
    assert updated_state["approval_status"] == "APPROVED"
    assert updated_state["action_execution_result"]["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_human_approval_rejection():
    query = "Analyze revenue and send report to finance team after approval."
    run_id = await execution_service.create_and_start_run(query=query)

    state = None
    for _ in range(50):
        await asyncio.sleep(0.1)
        state = get_state_snapshot(run_id)
        if state and state.get("status") in ["WAITING_APPROVAL", "COMPLETED", "FAILED"]:
            break

    assert state is not None
    assert state.get("status") == "WAITING_APPROVAL"
    assert state.get("approval_record") is not None

    # Reject action
    res = await execution_service.resolve_approval(
        run_id=run_id,
        decision="REJECTED",
        reviewer="compliance_officer",
        reason="Requires legal review first"
    )

    assert res["status"] == "REJECTED"
    updated_state = get_state_snapshot(run_id)
    assert updated_state["approval_status"] == "REJECTED"
