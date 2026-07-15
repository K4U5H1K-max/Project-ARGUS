from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TwinEntityState(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    state: dict[str, Any] = Field(default_factory=dict)
    version: int = 1
    updated_at: datetime | None = None


class PlantStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plant_id: str
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class ZoneStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    zone_id: str
    plant_id: str
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class EquipmentStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    equipment_id: str
    plant_id: str
    zone_id: str
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class WorkerStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    worker_id: str
    plant_id: str
    zone_id: str | None = None
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class PermitStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    permit_id: str
    plant_id: str
    zone_id: str
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class MaintenanceStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    maintenance_id: str
    plant_id: str
    zone_id: str
    equipment_id: str | None = None
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class SensorStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sensor_id: str
    plant_id: str
    zone_id: str
    equipment_id: str | None = None
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None


class HazardStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    hazard_id: str
    plant_id: str
    zone_id: str
    equipment_id: str | None = None
    state: dict[str, Any]
    version: int
    updated_at: datetime | None = None
