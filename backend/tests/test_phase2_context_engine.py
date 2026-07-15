from __future__ import annotations

import pytest

from app.context.repositories import ContextRepository
from app.context.service import ContextEngine
from app.core.enums import EventSeverity, EventType
from app.digital_twin.models import PermitState, ZoneState, WorkerState, EquipmentState
from app.digital_twin.repositories import TwinRepository
from app.models.event import Event


@pytest.mark.asyncio
async def test_context_engine_builds_snapshot(session) -> None:
    twin_repository = TwinRepository()
    context_repository = ContextRepository()

    async with session.begin():
        await twin_repository.upsert_zone(
            session,
            ZoneState(zone_id="zone-a", plant_id="plant-a", source_event_id="seed", state={"name": "Battery_A"}, version=1),
        )
        await twin_repository.upsert_worker(
            session,
            WorkerState(worker_id="worker-1", plant_id="plant-a", zone_id="zone-a", source_event_id="seed", state={"status": "IN_ZONE"}, version=1),
        )
        await twin_repository.upsert_equipment(
            session,
            EquipmentState(equipment_id="eq-1", plant_id="plant-a", zone_id="zone-a", source_event_id="seed", state={"status": "RUNNING"}, version=1),
        )
        await twin_repository.upsert_permit(
            session,
            PermitState(permit_id="permit-1", plant_id="plant-a", zone_id="zone-a", source_event_id="seed", state={"active": True, "permit_type": "HOT_WORK"}, version=1),
        )

    event = Event(
        event_id=__import__("uuid").uuid4(),
        timestamp=__import__("datetime").datetime.now(__import__("datetime").UTC),
        source="badge-reader",
        event_type=EventType.ENTRY,
        plant_id="plant-a",
        zone_id="zone-a",
        equipment_id=None,
        worker_id="worker-1",
        severity=EventSeverity.INFO,
        payload={},
        event_metadata={},
    )

    engine = ContextEngine(twin_repository=twin_repository, context_repository=context_repository)
    context, snapshot = await engine.build_context(session, event)
    await context_repository.create(session, snapshot)

    assert context.zone == "Battery_A"
    assert context.workers == 1
    assert context.equipment_running == 1
    assert context.active_permits == ["HOT_WORK"]
