from __future__ import annotations

from typing import Any

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConcurrencyError
from app.core.time import utcnow
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


class TwinRepository:
    async def _cas_upsert(self, session: AsyncSession, model: type, pk_name: str, state_obj: Any, values: dict[str, Any]) -> Any:
        pk_value = getattr(state_obj, pk_name)
        current = await session.get(model, pk_value)
        if current is None:
            session.add(state_obj)
            await session.flush()
            return state_obj

        expected_version = getattr(state_obj, "version", current.version)
        update_values = dict(values)
        if hasattr(model, "updated_at"):
            update_values["updated_at"] = utcnow()
        statement = (
            update(model)
            .where(getattr(model, pk_name) == pk_value, model.version == expected_version)
            .values(**update_values, version=expected_version + 1)
        )
        result = await session.execute(statement)
        if result.rowcount != 1:
            raise ConcurrencyError(f"Concurrency conflict updating {model.__name__} {pk_value}")
        await session.flush()
        refreshed = await session.get(model, pk_value)
        return refreshed or state_obj

    async def get_plant(self, session: AsyncSession, plant_id: str) -> PlantState | None:
        return await session.get(PlantState, plant_id)

    async def get_zone(self, session: AsyncSession, zone_id: str) -> ZoneState | None:
        return await session.get(ZoneState, zone_id)

    async def get_equipment(self, session: AsyncSession, equipment_id: str) -> EquipmentState | None:
        return await session.get(EquipmentState, equipment_id)

    async def get_worker(self, session: AsyncSession, worker_id: str) -> WorkerState | None:
        return await session.get(WorkerState, worker_id)

    async def get_permit(self, session: AsyncSession, permit_id: str) -> PermitState | None:
        return await session.get(PermitState, permit_id)

    async def get_maintenance(self, session: AsyncSession, maintenance_id: str) -> MaintenanceState | None:
        return await session.get(MaintenanceState, maintenance_id)

    async def get_sensor(self, session: AsyncSession, sensor_id: str) -> SensorState | None:
        return await session.get(SensorState, sensor_id)

    async def get_hazard(self, session: AsyncSession, hazard_id: str) -> HazardState | None:
        return await session.get(HazardState, hazard_id)

    async def list_zones_by_plant(self, session: AsyncSession, plant_id: str) -> list[ZoneState]:
        result = await session.execute(select(ZoneState).where(ZoneState.plant_id == plant_id).order_by(ZoneState.zone_id))
        return list(result.scalars().all())

    async def list_equipment_by_zone(self, session: AsyncSession, zone_id: str) -> list[EquipmentState]:
        result = await session.execute(select(EquipmentState).where(EquipmentState.zone_id == zone_id).order_by(EquipmentState.equipment_id))
        return list(result.scalars().all())

    async def list_workers_by_zone(self, session: AsyncSession, zone_id: str) -> list[WorkerState]:
        result = await session.execute(select(WorkerState).where(WorkerState.zone_id == zone_id).order_by(WorkerState.worker_id))
        return list(result.scalars().all())

    async def list_active_permits_by_zone(self, session: AsyncSession, zone_id: str) -> list[PermitState]:
        result = await session.execute(select(PermitState).where(PermitState.zone_id == zone_id).order_by(PermitState.permit_id))
        permits = list(result.scalars().all())
        return [permit for permit in permits if bool(permit.state.get("active", False))]

    async def list_active_maintenance_by_zone(self, session: AsyncSession, zone_id: str) -> list[MaintenanceState]:
        result = await session.execute(select(MaintenanceState).where(MaintenanceState.zone_id == zone_id).order_by(MaintenanceState.maintenance_id))
        maintenance_jobs = list(result.scalars().all())
        return [job for job in maintenance_jobs if bool(job.state.get("active", False))]

    async def list_hazards_by_zone(self, session: AsyncSession, zone_id: str) -> list[HazardState]:
        result = await session.execute(select(HazardState).where(HazardState.zone_id == zone_id).order_by(HazardState.updated_at.desc()))
        return list(result.scalars().all())

    async def list_recent_sensor_states_by_zone(self, session: AsyncSession, zone_id: str, *, limit: int = 5) -> list[SensorState]:
        result = await session.execute(
            select(SensorState).where(SensorState.zone_id == zone_id).order_by(SensorState.updated_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def upsert(self, session: AsyncSession, obj: Any) -> Any:
        raise NotImplementedError

    async def upsert_plant(self, session: AsyncSession, state: PlantState) -> PlantState:
        return await self._cas_upsert(session, PlantState, "plant_id", state, {"source_event_id": state.source_event_id, "state": state.state})

    async def upsert_zone(self, session: AsyncSession, state: ZoneState) -> ZoneState:
        return await self._cas_upsert(session, ZoneState, "zone_id", state, {"plant_id": state.plant_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_equipment(self, session: AsyncSession, state: EquipmentState) -> EquipmentState:
        return await self._cas_upsert(session, EquipmentState, "equipment_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_worker(self, session: AsyncSession, state: WorkerState) -> WorkerState:
        return await self._cas_upsert(session, WorkerState, "worker_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_permit(self, session: AsyncSession, state: PermitState) -> PermitState:
        return await self._cas_upsert(session, PermitState, "permit_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_maintenance(self, session: AsyncSession, state: MaintenanceState) -> MaintenanceState:
        return await self._cas_upsert(session, MaintenanceState, "maintenance_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "equipment_id": state.equipment_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_sensor(self, session: AsyncSession, state: SensorState) -> SensorState:
        return await self._cas_upsert(session, SensorState, "sensor_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "equipment_id": state.equipment_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_hazard(self, session: AsyncSession, state: HazardState) -> HazardState:
        return await self._cas_upsert(session, HazardState, "hazard_id", state, {"plant_id": state.plant_id, "zone_id": state.zone_id, "equipment_id": state.equipment_id, "source_event_id": state.source_event_id, "state": state.state})

    async def upsert_snapshot(self, session: AsyncSession, snapshot: TwinStateSnapshot) -> TwinStateSnapshot:
        return await self._cas_upsert(session, TwinStateSnapshot, "context_id", snapshot, {"event_id": snapshot.event_id, "plant_id": snapshot.plant_id, "timestamp": snapshot.timestamp, "serialized_state": snapshot.serialized_state, "trace_metadata": snapshot.trace_metadata})

    async def get_latest_snapshot_for_plant(self, session: AsyncSession, plant_id: str) -> TwinStateSnapshot | None:
        result = await session.execute(
            select(TwinStateSnapshot).where(TwinStateSnapshot.plant_id == plant_id).order_by(TwinStateSnapshot.timestamp.desc())
        )
        return result.scalars().first()
