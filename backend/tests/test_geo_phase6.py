from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.context.schemas import ContextObject
from app.core.enums import EventSeverity, EventType
from app.core.uuid import generate_uuid
from app.models.event import Event
from app.risk.service import RiskService


def _context(**overrides):
    base = {
        "context_id": "geo-ctx-1",
        "plant_id": "plant-a",
        "zone_id": "zone-geo-1",
        "event_id": "event-geo-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "zone": "zone-geo-1",
        "workers": 6,
        "equipment_running": 2,
        "maintenance": True,
        "active_permits": ["HOT_WORK", "CONFINED_SPACE"],
        "hazards": ["gas", "heat"],
        "current_shift": "DAY",
        "recent_incidents": 2,
        "nearby_equipment": [{"equipment_id": "eq-geo-1", "state": {"status": "RUNNING"}}],
        "recent_sensor_values": {},
        "weather": {},
    }
    base.update(overrides)
    return ContextObject(**base)


def _event(**overrides):
    base = {
        "event_id": generate_uuid(),
        "external_event_id": "geo-external-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "source": "plc-geo-1",
        "event_type": EventType.HOT_WORK,
        "plant_id": "plant-a",
        "zone_id": "zone-geo-1",
        "equipment_id": "eq-geo-1",
        "worker_id": "worker-geo-1",
        "severity": EventSeverity.CRITICAL,
        "payload": {"gas_ppm": 94, "oxygen_pct": 18.0, "alarm_count": 6, "shift_event": "SHIFT_CHANGE"},
        "event_metadata": {},
        "event_hash": None,
        "processing_version": 1,
    }
    base.update(overrides)
    return Event(**base)


@pytest.mark.asyncio
async def test_geo_layout_heatmap_and_routes(client, session, outbox_service) -> None:
    risk = RiskService(outbox_service)
    await risk.assess(session, context=_context(), event=_event())
    await session.commit()

    layout = await client.get("/geo/layout?plant_id=plant-a&zone_id=zone-geo-1")
    assert layout.status_code == 200
    layout_body = layout.json()
    assert layout_body["type"] == "FeatureCollection"
    assert layout_body["features"]
    assert layout_body["summary"]["feature_count"] > 0

    heatmap = await client.get("/geo/heatmap?plant_id=plant-a&zone_id=zone-geo-1")
    assert heatmap.status_code == 200
    assert heatmap.json()["type"] == "FeatureCollection"

    routes = await client.get("/geo/routes?plant_id=plant-a&zone_id=zone-geo-1")
    assert routes.status_code == 200
    assert routes.json()["features"]

    nearest = await client.get("/geo/nearest-safe-zone?plant_id=plant-a&zone_id=zone-geo-1")
    assert nearest.status_code == 200
    assert nearest.json()["safe_zone"] is not None
