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
        "context_id": "ctx-1",
        "plant_id": "plant-a",
        "zone_id": "zone-1",
        "event_id": "event-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "zone": "zone-1",
        "workers": 4,
        "equipment_running": 1,
        "maintenance": True,
        "active_permits": ["HOT_WORK"],
        "hazards": ["gas", "maintenance"],
        "current_shift": "NIGHT",
        "recent_incidents": 2,
        "nearby_equipment": [{"equipment_id": "eq-1", "state": {"status": "RUNNING"}}],
        "recent_sensor_values": {
            "sensor-1": {"reading": {"gas_ppm": 12, "status": "ALARM"}},
            "sensor-2": {"reading": {"gas_ppm": 48, "status": "CRITICAL"}},
            "sensor-3": {"reading": {"gas_ppm": 65, "status": "CRITICAL"}},
        },
        "weather": {},
    }
    base.update(overrides)
    return ContextObject(**base)


def _event(**overrides):
    base = {
        "event_id": generate_uuid(),
        "external_event_id": "external-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "source": "plc-01",
        "event_type": EventType.HOT_WORK,
        "plant_id": "plant-a",
        "zone_id": "zone-1",
        "equipment_id": "eq-1",
        "worker_id": "worker-1",
        "severity": EventSeverity.CRITICAL,
        "payload": {"gas_ppm": 68, "oxygen_pct": 18.8, "alarm_count": 4, "shift_event": "HANDOVER"},
        "event_metadata": {},
        "event_hash": None,
        "processing_version": 1,
    }
    base.update(overrides)
    return Event(**base)


@pytest.mark.asyncio
async def test_risk_service_builds_temporal_spatial_assessment(session, outbox_service) -> None:
    service = RiskService(outbox_service)
    context = _context()
    event = _event()

    assessment = await service.assess(session, context=context, event=event)

    assert assessment is not None
    assert assessment.risk_level in {"HIGH", "CRITICAL"}
    assert assessment.risk_score > 0
    assert "matched_rules" in assessment.explanation
    assert assessment.recommendation
    assert any("evacuate" in recommendation.lower() for recommendation in assessment.recommendation)


@pytest.mark.asyncio
async def test_risk_timeline_and_projection(client, session, outbox_service) -> None:
    service = RiskService(outbox_service)
    context = _context(recent_incidents=3, nearby_equipment=[{"equipment_id": "eq-1", "state": {"status": "OFFLINE"}}])
    event = _event(payload={"gas_ppm": 82, "oxygen_pct": 17.5, "alarm_count": 5, "shift_event": "SHIFT_CHANGE"})
    await service.assess(session, context=context, event=event)
    await session.commit()

    timeline_response = await client.get("/risk/timeline")
    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    assert timeline["summary"]["count"] >= 1

    map_response = await client.get("/risk/map")
    assert map_response.status_code == 200
    payload = map_response.json()
    assert payload["type"] == "FeatureCollection"
    assert payload["features"]
    assert payload["summary"]["score"] > 0


@pytest.mark.asyncio
async def test_risk_history_and_statistics_endpoints(client, session, outbox_service) -> None:
    service = RiskService(outbox_service)
    context = _context()
    event = _event()
    await service.assess(session, context=context, event=event)
    await session.commit()

    current_response = await client.get("/risk/current")
    assert current_response.status_code == 200
    assert current_response.json()["risk_id"]

    history_response = await client.get("/risk/history?limit=10&sort_by=score&sort_order=desc")
    assert history_response.status_code == 200
    assert history_response.json()

    statistics_response = await client.get("/risk/statistics")
    assert statistics_response.status_code == 200
    assert statistics_response.json()["total"] >= 1

    search_response = await client.get("/risk/search?query=hot")
    assert search_response.status_code == 200