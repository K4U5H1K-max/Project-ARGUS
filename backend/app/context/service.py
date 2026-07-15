from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.context.models import ContextSnapshot
from app.context.repositories import ContextRepository
from app.context.schemas import ContextObject
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.digital_twin.repositories import TwinRepository
from app.models.event import Event


@dataclass(slots=True)
class WeatherProvider:
    async def get_current_weather(self, *, plant_id: str, zone_id: str) -> dict[str, Any]:
        return {"condition": "clear", "temperature_c": 24.0, "humidity": 35}


class ShiftProvider:
    def current_shift(self, timestamp: datetime) -> str:
        hour = timestamp.astimezone(UTC).hour
        return "Night" if hour < 6 or hour >= 18 else "Day"


class ContextEngine:
    def __init__(self, twin_repository: TwinRepository, context_repository: ContextRepository, weather_provider: WeatherProvider | None = None) -> None:
        self.twin_repository = twin_repository
        self.context_repository = context_repository
        self.weather_provider = weather_provider or WeatherProvider()
        self.shift_provider = ShiftProvider()
        self.logger = get_logger(__name__)

    async def build_context(self, session: AsyncSession, event: Event) -> tuple[ContextObject, ContextSnapshot]:
        zone_id = event.zone_id
        plant_id = event.plant_id

        zone = await self.twin_repository.get_zone(session, zone_id)
        workers = await self.twin_repository.list_workers_by_zone(session, zone_id)
        equipment = await self.twin_repository.list_equipment_by_zone(session, zone_id)
        permits = await self.twin_repository.list_active_permits_by_zone(session, zone_id)
        maintenance = await self.twin_repository.list_active_maintenance_by_zone(session, zone_id)
        hazards = await self.twin_repository.list_hazards_by_zone(session, zone_id)
        sensors = await self.twin_repository.list_recent_sensor_states_by_zone(session, zone_id)
        weather = await self.weather_provider.get_current_weather(plant_id=plant_id, zone_id=zone_id)

        context_id = str(generate_uuid())
        context = ContextObject(
            context_id=context_id,
            plant_id=plant_id,
            zone_id=zone_id,
            event_id=str(event.event_id),
            timestamp=event.timestamp,
            zone=zone.state.get("name", zone_id) if zone else zone_id,
            workers=len(workers),
            equipment_running=sum(1 for item in equipment if item.state.get("status") == "RUNNING"),
            maintenance=bool(maintenance),
            active_permits=[permit.state.get("permit_type", permit.permit_id) for permit in permits],
            hazards=[hazard.state.get("kind", hazard.hazard_id) for hazard in hazards],
            current_shift=self.shift_provider.current_shift(event.timestamp),
            recent_incidents=sum(1 for hazard in hazards if hazard.state.get("severity") in {"CRITICAL", "HIGH"} or hazard.state.get("incident") is True),
            nearby_equipment=[{"equipment_id": item.equipment_id, "state": item.state} for item in equipment],
            recent_sensor_values={item.sensor_id: item.state for item in sensors},
            weather=weather,
        )

        snapshot = ContextSnapshot(
            context_id=context_id,
            event_id=str(event.event_id),
            plant_id=plant_id,
            zone_id=zone_id,
            timestamp=event.timestamp,
            serialized_context=context.model_dump(mode="json"),
            version=1,
            trace_metadata={
                "source_event_id": str(event.event_id),
                "external_event_id": event.external_event_id or str(event.event_id),
                "event_hash": event.event_hash,
                "processor_version": 1,
                "context_version": 1,
            },
        )

        self.logger.info("context_built", context_id=snapshot.context_id, event_id=str(event.event_id))
        return context, snapshot
