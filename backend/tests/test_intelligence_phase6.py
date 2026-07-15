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
        "context_id": "intel-ctx-1",
        "plant_id": "plant-a",
        "zone_id": "zone-intel-1",
        "event_id": "event-intel-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "zone": "zone-intel-1",
        "workers": 3,
        "equipment_running": 1,
        "maintenance": True,
        "active_permits": ["HOT_WORK"],
        "hazards": ["gas"],
        "current_shift": "NIGHT",
        "recent_incidents": 1,
        "nearby_equipment": [{"equipment_id": "eq-intel-1", "state": {"status": "RUNNING"}}],
        "recent_sensor_values": {},
        "weather": {},
    }
    base.update(overrides)
    return ContextObject(**base)


def _event(**overrides):
    base = {
        "event_id": generate_uuid(),
        "external_event_id": "intel-external-1",
        "timestamp": datetime(2026, 7, 15, tzinfo=timezone.utc),
        "source": "plc-intel-1",
        "event_type": EventType.HOT_WORK,
        "plant_id": "plant-a",
        "zone_id": "zone-intel-1",
        "equipment_id": "eq-intel-1",
        "worker_id": "worker-intel-1",
        "severity": EventSeverity.CRITICAL,
        "payload": {"gas_ppm": 88, "oxygen_pct": 18.5, "alarm_count": 4, "shift_event": "HANDOVER"},
        "event_metadata": {},
        "event_hash": None,
        "processing_version": 1,
    }
    base.update(overrides)
    return Event(**base)


@pytest.mark.asyncio
async def test_intelligence_report_and_citations(client, session, outbox_service) -> None:
    risk = RiskService(outbox_service)
    assessment = await risk.assess(session, context=_context(), event=_event())
    await session.commit()
    assert assessment is not None

    report = await client.get(f"/intelligence/report/{assessment.risk_id}")
    assert report.status_code == 200
    body = report.json()
    assert body["risk_id"] == str(assessment.risk_id)
    assert body["citations"]
    assert body["industrial_intelligence"]["applicable_standards"]
    assert body["industrial_intelligence"]["recommendations"]

    regulations = await client.get(f"/intelligence/regulations/{assessment.risk_id}")
    assert regulations.status_code == 200
    assert regulations.json()

    similar = await client.get(f"/intelligence/similar-incidents/{assessment.risk_id}")
    assert similar.status_code == 200
    assert similar.json()

    citations = await client.get(f"/intelligence/citations/{assessment.risk_id}")
    assert citations.status_code == 200
    assert citations.json()


@pytest.mark.asyncio
async def test_intelligence_document_ingestion(client) -> None:
    response = await client.post(
        "/intelligence/documents/ingest?title=Plant%20SOP&source_type=SOP&content=Hot%20work%20permits%20must%20be%20verified%20before%20ignition.&uri=memory:sop-1",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["chunk_count"] >= 1
    assert body["source_type"] == "SOP"
