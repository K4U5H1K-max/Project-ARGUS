from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.context.schemas import ContextObject
from app.core.enums import EventSeverity, EventType
from app.database.base import Base
from app.models.event import Event
from app.reliability.outbox import OutboxService
from app.reliability.repositories import OutboxRepository
from app.risk.projection import GeoSpatialProjectionService
from app.risk.service import RiskService


class MockGraphQueryService:
    async def node(self, node_type: str, node_id: str):
        return [{"n": {"node_type": node_type, "node_id": node_id, "properties": {"coordinates": [12.0, 48.0]}}}]

    async def worker_exposure(self, worker_id: str):
        return [{"asset": {"node_type": "Equipment", "node_id": f"eq-{worker_id}", "properties": {"coordinates": [12.1, 48.1]}}}]

    async def impact(self, node_id: str):
        return [{"impact": {"node_type": "Equipment", "node_id": f"impact-{node_id}", "properties": {"coordinates": [12.2, 48.2]}}}]

    async def zone_graph(self, zone_id: str):
        return [{"z": {"node_type": "Zone", "node_id": zone_id, "properties": {"coordinates": [12.3, 48.3]}}}]


async def main() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    outbox = OutboxService(OutboxRepository())
    risk_service = RiskService(outbox)
    projection_service = GeoSpatialProjectionService(MockGraphQueryService())

    context = ContextObject(
        context_id="ctx-1",
        plant_id="plant-a",
        zone_id="zone-1",
        event_id="event-1",
        timestamp=datetime(2026, 7, 15, tzinfo=timezone.utc),
        zone="zone-1",
        workers=4,
        equipment_running=1,
        maintenance=True,
        active_permits=["HOT_WORK"],
        hazards=["gas", "maintenance"],
        current_shift="NIGHT",
        recent_incidents=2,
        nearby_equipment=[{"equipment_id": "eq-1", "state": {"status": "RUNNING"}}],
        recent_sensor_values={
            "sensor-1": {"reading": {"gas_ppm": 12, "status": "ALARM"}},
            "sensor-2": {"reading": {"gas_ppm": 48, "status": "CRITICAL"}},
            "sensor-3": {"reading": {"gas_ppm": 65, "status": "CRITICAL"}},
        },
        weather={},
    )
    event = Event(
        event_id="00000000-0000-0000-0000-000000000001",
        external_event_id="external-1",
        timestamp=datetime(2026, 7, 15, tzinfo=timezone.utc),
        source="plc-01",
        event_type=EventType.HOT_WORK,
        plant_id="plant-a",
        zone_id="zone-1",
        equipment_id="eq-1",
        worker_id="worker-1",
        severity=EventSeverity.CRITICAL,
        payload={"gas_ppm": 68, "oxygen_pct": 18.8, "alarm_count": 4, "shift_event": "HANDOVER"},
        event_metadata={},
        event_hash=None,
        processing_version=1,
    )

    async with session_factory() as session:
        assessment = await risk_service.assess(session, context=context, event=event)
        await session.commit()
        timeline = await risk_service.timeline(session, plant_id="plant-a", zone_id="zone-1")
        projection = await projection_service.project_assessment(assessment)
        hotspots = await projection_service.hotspots(assessment)

    print({"level": assessment.risk_level, "score": assessment.risk_score, "timeline_count": timeline["summary"]["count"], "features": len(projection["features"]), "hotspots": len(hotspots)})
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
