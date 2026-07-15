from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActionObject(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    action_id: str
    action_type: str
    priority: int
    reason: str
    generated_by: str
    timestamp: datetime
    context_id: str
    status: str
    action_data: dict[str, Any]
    plant_id: str
    zone_id: str


class ActionListResponse(BaseModel):
    items: list[ActionObject]
    total: int
    limit: int
    offset: int
