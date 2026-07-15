from __future__ import annotations

import pytest

from app.core.enums import EventSeverity, EventType
from app.digital_twin.models import WorkerState
from app.models.event import Event
from app.digital_twin.processors.registry import ProcessorRegistry
from app.digital_twin.repositories import TwinRepository
from app.digital_twin.state_manager import StateManager


@pytest.mark.asyncio
async def test_state_manager_updates_worker_state(session) -> None:
    state_manager = StateManager(ProcessorRegistry(), TwinRepository())
    event = Event(
        event_id=__import__("uuid").uuid4(),
        timestamp=__import__("datetime").datetime.now(__import__("datetime").UTC),
        source="badge-reader",
        event_type=EventType.ENTRY,
        plant_id="plant-a",
        zone_id="restricted_area",
        equipment_id=None,
        worker_id="worker-1",
        severity=EventSeverity.INFO,
        payload={},
        event_metadata={},
    )

    async with session.begin():
        result = await state_manager.apply_event(session, event)

    assert result.plant_id == "plant-a"
    worker = await session.get(WorkerState, "worker-1")
    assert worker is not None
    assert worker.zone_id == "restricted_area"
