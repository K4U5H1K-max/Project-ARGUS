from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EventType
from app.core.exceptions import ValidationAppError
from app.core.logging import get_logger
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.digital_twin.models import (
    EquipmentState,
    HazardState,
    MaintenanceState,
    PermitState,
    PlantState,
    SensorState,
    TwinStateSnapshot,
    WorkerState,
    ZoneState,
)
from app.digital_twin.repositories import TwinRepository
from app.digital_twin.processors.registry import ProcessorRegistry
from app.models.event import Event


@dataclass(slots=True)
class StateChangeResult:
    plant_id: str
    zone_id: str
    processor_name: str
    updated_entities: list[str]


class StateManager:
    def __init__(self, registry: ProcessorRegistry, repository: TwinRepository | None = None) -> None:
        self.registry = registry
        self.repository = repository or TwinRepository()
        self.logger = get_logger(__name__)

    async def apply_event(self, session: AsyncSession, event: Event) -> StateChangeResult:
        processor = self.registry.resolve(event.event_type)
        self.logger.info("twin_update_started", event_id=str(event.event_id), processor=processor.__class__.__name__)
        result = await processor.process(event=event, state_manager=self, session=session)
        await self.persist_state_snapshot(session, event)
        self.logger.info("twin_updated", event_id=str(event.event_id))
        return StateChangeResult(
            plant_id=event.plant_id,
            zone_id=event.zone_id,
            processor_name=processor.__class__.__name__,
            updated_entities=result.get("updated_entities", []),
        )

    async def update_sensor_state(self, event: Event, session: AsyncSession) -> dict[str, Any]:
        sensor_id = str(event.payload.get("sensor_id") or event.payload.get("sensorId") or event.event_id)
        current = await self.repository.get_sensor(session, sensor_id)
        state = dict(current.state if current else {})
        state.update(
            {
                "event_type": str(event.event_type),
                "reading": dict(event.payload),
                "active": True,
                "updated_from_event_id": str(event.event_id),
            }
        )
        await self.repository.upsert_sensor(
            session,
            SensorState(
                sensor_id=sensor_id,
                plant_id=event.plant_id,
                zone_id=event.zone_id,
                equipment_id=event.equipment_id,
                source_event_id=str(event.event_id),
                state=state,
                version=(current.version + 1 if current else 1),
            ),
        )
        return {"updated_entities": ["sensor", "hazard"]}

    async def update_worker_state(self, event: Event, session: AsyncSession) -> dict[str, Any]:
        if not event.worker_id:
            raise ValidationAppError("Worker events require worker_id")
        current = await self.repository.get_worker(session, event.worker_id)
        current_zone = current.zone_id if current else None
        if event.event_type == EventType.EXIT and not event.worker_id:
            raise ValidationAppError("Worker exit event requires worker_id")
        if event.event_type == EventType.EXIT and current_zone is None:
            raise ValidationAppError("Worker exits without entering")
        zone_id = event.zone_id if event.event_type == EventType.ENTRY else None
        state = dict(current.state if current else {})
        state.update(
            {
                "status": "IN_ZONE" if zone_id else "OUT_OF_ZONE",
                "last_event_type": str(event.event_type),
                "updated_from_event_id": str(event.event_id),
            }
        )
        await self.repository.upsert_worker(
            session,
            WorkerState(
                worker_id=event.worker_id,
                plant_id=event.plant_id,
                zone_id=zone_id,
                source_event_id=str(event.event_id),
                state=state,
                version=(current.version + 1 if current else 1),
            ),
        )
        return {"updated_entities": ["worker", "zone"]}

    async def update_permit_state(self, event: Event, session: AsyncSession) -> dict[str, Any]:
        permit_id = str(event.payload.get("permit_id") or f"{event.event_type}:{event.zone_id}")
        current = await self.repository.get_permit(session, permit_id)
        current_active = bool(current.state.get("active", False)) if current else False
        next_active = event.payload.get("active")
        if next_active is None:
            next_active = event.payload.get("status") not in {"CLOSED", "EXPIRED", "REVOKED"}
        if current and not current_active and not next_active:
            raise ValidationAppError("Permit closes twice")
        state = dict(current.state if current else {})
        state.update(
            {
                "permit_type": str(event.event_type),
                "active": bool(next_active),
                "status": "ACTIVE" if next_active else "CLOSED",
                "updated_from_event_id": str(event.event_id),
            }
        )
        await self.repository.upsert_permit(
            session,
            PermitState(
                permit_id=permit_id,
                plant_id=event.plant_id,
                zone_id=event.zone_id,
                source_event_id=str(event.event_id),
                state=state,
                version=(current.version + 1 if current else 1),
            ),
        )
        return {"updated_entities": ["permit", "zone"]}

    async def update_maintenance_state(self, event: Event, session: AsyncSession) -> dict[str, Any]:
        maintenance_id = str(event.payload.get("maintenance_id") or f"maintenance:{event.zone_id}:{event.equipment_id or 'general'}")
        current = await self.repository.get_maintenance(session, maintenance_id)
        active = event.event_type == EventType.START and event.payload.get("status") != "COMPLETE"
        if current and current.state.get("active") is False and event.event_type == EventType.COMPLETE:
            raise ValidationAppError("Maintenance completes twice")
        state = dict(current.state if current else {})
        state.update(
            {
                "active": active,
                "status": "ACTIVE" if active else "COMPLETE",
                "maintenance_type": event.payload.get("maintenance_type"),
                "updated_from_event_id": str(event.event_id),
            }
        )
        await self.repository.upsert_maintenance(
            session,
            MaintenanceState(
                maintenance_id=maintenance_id,
                plant_id=event.plant_id,
                zone_id=event.zone_id,
                equipment_id=event.equipment_id,
                source_event_id=str(event.event_id),
                state=state,
                version=(current.version + 1 if current else 1),
            ),
        )
        if event.equipment_id:
            equipment = await self.repository.get_equipment(session, event.equipment_id)
            equipment_state = dict(equipment.state if equipment else {})
            equipment_state.update(
                {
                    "status": "UNDER_MAINTENANCE" if active else "AVAILABLE",
                    "maintenance_id": maintenance_id,
                    "updated_from_event_id": str(event.event_id),
                }
            )
            await self.repository.upsert_equipment(
                session,
                EquipmentState(
                    equipment_id=event.equipment_id,
                    plant_id=event.plant_id,
                    zone_id=event.zone_id,
                    source_event_id=str(event.event_id),
                    state=equipment_state,
                    version=(equipment.version + 1 if equipment else 1),
                ),
            )
        return {"updated_entities": ["maintenance", "equipment"]}

    async def update_hazard_state(self, event: Event, session: AsyncSession) -> dict[str, Any]:
        hazard_id = str(event.payload.get("hazard_id") or f"hazard:{event.zone_id}:{event.event_type}")
        current = await self.repository.get_hazard(session, hazard_id)
        state = dict(current.state if current else {})
        state.update(
            {
                "kind": str(event.event_type),
                "severity": str(event.severity),
                "active": True,
                "incident": True,
                "updated_from_event_id": str(event.event_id),
            }
        )
        await self.repository.upsert_hazard(
            session,
            HazardState(
                hazard_id=hazard_id,
                plant_id=event.plant_id,
                zone_id=event.zone_id,
                equipment_id=event.equipment_id,
                source_event_id=str(event.event_id),
                state=state,
                version=(current.version + 1 if current else 1),
            ),
        )
        return {"updated_entities": ["hazard", "zone"]}

    async def persist_state_snapshot(self, session: AsyncSession, event: Event) -> TwinStateSnapshot:
        plant = await self.repository.get_plant(session, event.plant_id)
        zone = await self.repository.get_zone(session, event.zone_id)
        if plant is None:
            plant = PlantState(plant_id=event.plant_id, source_event_id=str(event.event_id), state={"plant_id": event.plant_id, "zones": 1}, version=1)
            await self.repository.upsert_plant(session, plant)
        if zone is None:
            zone = ZoneState(zone_id=event.zone_id, plant_id=event.plant_id, source_event_id=str(event.event_id), state={"zone_id": event.zone_id, "name": event.zone_id}, version=1)
            await self.repository.upsert_zone(session, zone)

        workers = await self.repository.list_workers_by_zone(session, event.zone_id)
        equipment = await self.repository.list_equipment_by_zone(session, event.zone_id)
        permits = await self.repository.list_active_permits_by_zone(session, event.zone_id)
        maintenance = await self.repository.list_active_maintenance_by_zone(session, event.zone_id)
        hazards = await self.repository.list_hazards_by_zone(session, event.zone_id)

        plant.state = {
            "plant_id": event.plant_id,
            "zones": len({zone.zone_id for zone in await self.repository.list_zones_by_plant(session, event.plant_id)}),
            "workers": len(workers),
            "equipment_running": sum(1 for item in equipment if item.state.get("status") == "RUNNING"),
            "active_permits": len(permits),
            "maintenance_active": bool(maintenance),
            "hazards": len(hazards),
            "last_event_id": str(event.event_id),
        }
        zone.state = {
            "zone_id": event.zone_id,
            "workers": len(workers),
            "equipment_running": sum(1 for item in equipment if item.state.get("status") == "RUNNING"),
            "active_permits": len(permits),
            "maintenance": bool(maintenance),
            "hazards": [hazard.state.get("kind", hazard.hazard_id) for hazard in hazards],
            "last_event_id": str(event.event_id),
        }
        await self.repository.upsert_plant(session, plant)
        await self.repository.upsert_zone(session, zone)

        snapshot = TwinStateSnapshot(
            context_id=str(generate_uuid()),
            event_id=str(event.event_id),
            plant_id=event.plant_id,
            timestamp=event.timestamp,
            serialized_state={
                "plant_id": event.plant_id,
                "zone_id": event.zone_id,
                "event_type": event.event_type,
                "source_event_id": str(event.event_id),
                "updated_at": utcnow().isoformat(),
            },
            version=1,
            trace_metadata={
                "source_event_id": str(event.event_id),
                "external_event_id": event.external_event_id or str(event.event_id),
                "event_hash": event.event_hash,
                "processor_version": 1,
                "snapshot_version": 1,
            },
        )
        session.add(snapshot)
        await session.flush()
        return snapshot
