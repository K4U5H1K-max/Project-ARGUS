from __future__ import annotations

import pytest

from app.actions.repositories import ActionRepository
from app.actions.rules import RuleRegistry
from app.actions.service import ActionEngine
from app.context.schemas import ContextObject
from app.core.enums import EventSeverity, EventType
from app.kafka.producer import EventPublisher
from app.models.event import Event


class CapturePublisher(EventPublisher):
    def __init__(self) -> None:
        self.is_ready = True
        self.events: list[dict[str, object]] = []

    async def start(self) -> None:
        self.is_ready = True

    async def stop(self) -> None:
        self.is_ready = False

    async def publish(self, event: dict[str, object]) -> None:
        self.events.append(event)


@pytest.mark.asyncio
async def test_action_engine_generates_restricted_zone_action(session) -> None:
    publisher = CapturePublisher()
    engine = ActionEngine(repository=ActionRepository(), registry=RuleRegistry(), publisher=publisher)
    context = ContextObject(
        context_id="ctx-1",
        plant_id="plant-a",
        zone_id="restricted_zone",
        event_id="event-1",
        timestamp=__import__("datetime").datetime.now(__import__("datetime").UTC),
        zone="restricted_zone",
        workers=0,
        equipment_running=0,
        maintenance=False,
        active_permits=[],
        hazards=[],
        current_shift="Night",
        recent_incidents=0,
        nearby_equipment=[],
        recent_sensor_values={},
        weather={},
    )
    event = Event(
        event_id=__import__("uuid").uuid4(),
        timestamp=__import__("datetime").datetime.now(__import__("datetime").UTC),
        source="badge-reader",
        event_type=EventType.ENTRY,
        plant_id="plant-a",
        zone_id="restricted_zone",
        equipment_id=None,
        worker_id="worker-1",
        severity=EventSeverity.WARNING,
        payload={},
        event_metadata={},
    )

    actions = await engine.evaluate(session, context=context, event=event)
    assert actions
    assert actions[0].action_type == "RESTRICTED_ZONE_ENTRY"
    assert publisher.events[0]["event_name"] == "ActionGenerated"
