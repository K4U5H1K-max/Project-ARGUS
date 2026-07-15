from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ContextObject(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context_id: str
    plant_id: str
    zone_id: str
    event_id: str
    timestamp: datetime
    zone: str
    workers: int
    equipment_running: int
    maintenance: bool
    active_permits: list[str]
    hazards: list[str]
    current_shift: str
    recent_incidents: int
    nearby_equipment: list[dict[str, Any]] = []
    recent_sensor_values: dict[str, Any] = {}
    weather: dict[str, Any] = {}


class ContextSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    context_id: str
    event_id: str
    plant_id: str
    zone_id: str
    timestamp: datetime
    serialized_context: dict[str, Any]
    version: int
    created_at: datetime | None = None
