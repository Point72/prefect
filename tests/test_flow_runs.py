import time

import pytest

import prefect.client.schemas as client_schemas
from prefect import flow
from prefect.client.orchestration import PrefectClient
from prefect.exceptions import FlowRunWaitTimeout
from prefect.flow_runs import wait_for_flow_run
from prefect.states import Completed


async def test_create_then_wait_for_flow_run(prefect_client: PrefectClient):
    @flow
    def foo():
        pass

    flow_run = await prefect_client.create_flow_run(foo, state=Completed())
    assert isinstance(flow_run, client_schemas.FlowRun)

    lookup = await wait_for_flow_run(flow_run.id)
    # Estimates will not be equal since time has passed
    assert lookup == flow_run
    assert flow_run.state
    assert flow_run.state.is_final()


async def test_create_then_wait_timeout(prefect_client: PrefectClient):
    @flow
    def foo():
        time.sleep(9999)

    flow_run = await prefect_client.create_flow_run(
        foo,
    )
    assert isinstance(flow_run, client_schemas.FlowRun)

    with pytest.raises(FlowRunWaitTimeout):
        await wait_for_flow_run(flow_run.id, timeout=0)
