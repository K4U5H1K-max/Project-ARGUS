from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import EventSeverity, EventType


class EventCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    external_event_id: str | None = None
    timestamp: datetime | None = None
    source: str
    event_type: EventType
    plant_id: str
    zone_id: str
    equipment_id: str | None = None
    worker_id: str | None = None
    severity: EventSeverity
    payload: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    event_id: UUID
    external_event_id: str | None = None
    timestamp: datetime
    source: str
    event_type: EventType
    plant_id: str
    zone_id: str
    equipment_id: str | None = None
    worker_id: str | None = None
    severity: EventSeverity
    payload: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
    limit: int
    offset: int
