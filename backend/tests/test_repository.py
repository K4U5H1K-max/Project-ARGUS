from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.enums import EventSeverity, EventType
from app.models.event import Event
from app.repositories.event_repository import EventRepository


@pytest.mark.asyncio
async def test_repository_create_list_and_get(session) -> None:
    repository = EventRepository()
    event = Event(
        event_id=uuid4(),
        timestamp=datetime.now(tz=UTC),
        source="plc-01",
        event_type=EventType.GAS_SENSOR,
        plant_id="plant-a",
        zone_id="zone-1",
        equipment_id=None,
        worker_id=None,
        severity=EventSeverity.WARNING,
        payload={"gas_type": "co", "ppm": 12.1},
        event_metadata={"source_version": "1.0"},
    )

    async with session.begin():
        created = await repository.create(session, event)

    fetched = await repository.get_by_id(session, created.event_id)
    assert fetched is not None
    assert fetched.source == "plc-01"

    items, total = await repository.list(session, limit=10, offset=0)
    assert total == 1
    assert len(items) == 1
