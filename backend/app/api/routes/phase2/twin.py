from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_auth_context, get_db_session
from app.core.auth import AuthContext
from app.digital_twin.models import EquipmentState, HazardState, MaintenanceState, PermitState, PlantState, SensorState, WorkerState, ZoneState
from app.digital_twin.repositories import TwinRepository
from app.digital_twin.schemas import (
    EquipmentStateResponse,
    HazardStateResponse,
    MaintenanceStateResponse,
    PermitStateResponse,
    PlantStateResponse,
    SensorStateResponse,
    WorkerStateResponse,
    ZoneStateResponse,
)

router = APIRouter(tags=["digital-twin"])
repository = TwinRepository()


@router.get("/twin/plants/{plant_id}", response_model=PlantStateResponse)
async def get_plant_state(plant_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> PlantStateResponse:
    record = await repository.get_plant(session, plant_id)
    return PlantStateResponse(plant_id=plant_id, state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/zones/{zone_id}", response_model=ZoneStateResponse)
async def get_zone_state(zone_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> ZoneStateResponse:
    record = await repository.get_zone(session, zone_id)
    return ZoneStateResponse(zone_id=zone_id, plant_id=(record.plant_id if record else ""), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/equipment/{equipment_id}", response_model=EquipmentStateResponse)
async def get_equipment_state(equipment_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> EquipmentStateResponse:
    record = await repository.get_equipment(session, equipment_id)
    return EquipmentStateResponse(equipment_id=equipment_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else ""), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/workers/{worker_id}", response_model=WorkerStateResponse)
async def get_worker_state(worker_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> WorkerStateResponse:
    record = await repository.get_worker(session, worker_id)
    return WorkerStateResponse(worker_id=worker_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else None), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/permits/{permit_id}", response_model=PermitStateResponse)
async def get_permit_state(permit_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> PermitStateResponse:
    record = await repository.get_permit(session, permit_id)
    return PermitStateResponse(permit_id=permit_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else ""), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/maintenance/{maintenance_id}", response_model=MaintenanceStateResponse)
async def get_maintenance_state(maintenance_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> MaintenanceStateResponse:
    record = await repository.get_maintenance(session, maintenance_id)
    return MaintenanceStateResponse(maintenance_id=maintenance_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else ""), equipment_id=(record.equipment_id if record else None), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/sensors/{sensor_id}", response_model=SensorStateResponse)
async def get_sensor_state(sensor_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> SensorStateResponse:
    record = await repository.get_sensor(session, sensor_id)
    return SensorStateResponse(sensor_id=sensor_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else ""), equipment_id=(record.equipment_id if record else None), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))


@router.get("/twin/hazards/{hazard_id}", response_model=HazardStateResponse)
async def get_hazard_state(hazard_id: str, _: AuthContext = Depends(get_auth_context), session: AsyncSession = Depends(get_db_session)) -> HazardStateResponse:
    record = await repository.get_hazard(session, hazard_id)
    return HazardStateResponse(hazard_id=hazard_id, plant_id=(record.plant_id if record else ""), zone_id=(record.zone_id if record else ""), equipment_id=(record.equipment_id if record else None), state=(record.state if record else {}), version=(record.version if record else 1), updated_at=(record.updated_at if record else None))
