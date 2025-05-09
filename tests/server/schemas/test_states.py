from datetime import datetime, timezone
from uuid import UUID, uuid4

import pydantic
import pytest

from prefect.server.schemas.states import (
    AwaitingRetry,
    Completed,
    Failed,
    Late,
    Pending,
    Retrying,
    Running,
    Scheduled,
    State,
    StateDetails,
    StateType,
)


class TestState:
    def test_state_takes_name_from_type(self):
        state = State(type=StateType.RUNNING)
        assert state.name == "Running"

    def test_state_raises_validation_error_for_invalid_type(self):
        with pytest.raises(
            pydantic.ValidationError,
            match="1 validation error for State\ntype\n  Input should be",
        ):
            State(type="Running")

    def test_state_custom_name(self):
        state = State(type=StateType.RUNNING, name="My Running State")
        assert state.name == "My Running State"

    def test_state_default_timestamp(self):
        dt = datetime.now(timezone.utc)
        state = State(type=StateType.RUNNING)
        assert state.timestamp >= dt

    def test_state_copy_does_not_create_insertable_object(self):
        dt = datetime.now(timezone.utc)
        state = State(type=StateType.RUNNING, timestamp=dt, id=uuid4())
        new_state = state.model_copy()
        # Same UUID
        assert new_state.id == state.id

    def test_state_copy_with_field_reset_creates_insertable_object(self):
        dt = datetime.now(timezone.utc)
        state = State(type=StateType.RUNNING, timestamp=dt, id=uuid4())
        new_state = state.reset_fields()
        # New UUID
        assert new_state.id != state.id
        assert isinstance(new_state.id, UUID)
        # New state timestamp
        assert new_state.timestamp >= dt


class TestStateTypeFunctions:
    @pytest.mark.parametrize("state_type", StateType)
    def test_is_scheduled(self, state_type):
        state = State(type=state_type)
        assert state.is_scheduled() == (state_type == StateType.SCHEDULED)

    @pytest.mark.parametrize("state_type", StateType)
    def test_is_pending(self, state_type):
        state = State(type=state_type)
        assert state.is_pending() == (state_type == StateType.PENDING)

    @pytest.mark.parametrize("state_type", StateType)
    def test_is_running(self, state_type):
        state = State(type=state_type)
        assert state.is_running() == (state_type == StateType.RUNNING)

    @pytest.mark.parametrize("state_type", StateType)
    def test_is_completed(self, state_type):
        state = State(type=state_type)
        assert state.is_completed() == (state_type == StateType.COMPLETED)

    @pytest.mark.parametrize("state_type", StateType)
    def test_is_failed(self, state_type):
        state = State(type=state_type)
        assert state.is_failed() == (state_type == StateType.FAILED)

    @pytest.mark.parametrize("state_type", StateType)
    def test_is_cancelled(self, state_type):
        state = State(type=state_type)
        assert state.is_cancelled() == (state_type == StateType.CANCELLED)


class TestStateConvenienceFunctions:
    def test_completed(self):
        state = Completed()
        assert state.type == StateType.COMPLETED

    def test_completed_with_custom_attrs(self):
        state = Completed(name="my-state", state_details=StateDetails(cache_key="123"))
        assert state.name == "my-state"
        assert state.state_details.cache_key == "123"

    def test_failed(self):
        state = Failed()
        assert state.type == StateType.FAILED

    def test_running(self):
        state = Running()
        assert state.type == StateType.RUNNING

    def test_pending(self):
        state = Pending()
        assert state.type == StateType.PENDING

    def test_scheduled(self):
        dt = datetime.now(timezone.utc)
        state = Scheduled(scheduled_time=dt)
        assert state.type == StateType.SCHEDULED
        assert state.name == "Scheduled"
        assert state.state_details.scheduled_time == dt

    def test_scheduled_without_scheduled_time_defaults_to_now(self):
        dt1 = datetime.now(timezone.utc)
        state = Scheduled()
        dt2 = datetime.now(timezone.utc)
        assert dt1 <= state.state_details.scheduled_time <= dt2

    def test_scheduled_with_state_details_cant_provide_scheduled_time(self):
        dt = datetime.now(timezone.utc)
        with pytest.raises(ValueError, match="(extra scheduled_time)"):
            Scheduled(
                scheduled_time=dt,
                state_details=StateDetails(scheduled_time=dt),
            )

    def test_awaiting_retry(self):
        dt = datetime.now(timezone.utc)
        state = AwaitingRetry(scheduled_time=dt)
        assert state.type == StateType.SCHEDULED
        assert state.name == "AwaitingRetry"
        assert state.state_details.scheduled_time == dt

    def test_awaiting_retry_without_scheduled_time_defaults_to_now(self):
        dt1 = datetime.now(timezone.utc)
        state = AwaitingRetry()
        dt2 = datetime.now(timezone.utc)
        assert dt1 <= state.state_details.scheduled_time <= dt2

    def test_late(self):
        dt = datetime.now(timezone.utc)
        state = Late(scheduled_time=dt)
        assert state.type == StateType.SCHEDULED
        assert state.name == "Late"
        assert state.state_details.scheduled_time == dt

    def test_late_without_scheduled_time_defaults_to_now(self):
        dt1 = datetime.now(timezone.utc)
        state = Late()
        dt2 = datetime.now(timezone.utc)
        assert dt1 <= state.state_details.scheduled_time <= dt2

    def test_retrying(self):
        state = Retrying()
        assert state.type == StateType.RUNNING
        assert state.name == "Retrying"


class TestRepresentation:
    async def test_state_str_includes_message(self):
        assert str(Failed(message="abc")) == "Failed('abc')"

    async def test_state_str_excludes_null_message(self):
        assert str(Failed(message=None)) == "Failed()"

    async def test_state_str_excludes_null_message_with_name(self):
        assert str(Failed(message=None, name="Test")) == "Test(type=FAILED)"

    async def test_state_str_includes_type_if_name_is_custom(self):
        assert str(Failed(message="abc", name="Foo")) == "Foo('abc', type=FAILED)"
