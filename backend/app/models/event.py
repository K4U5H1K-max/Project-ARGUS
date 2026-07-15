from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.core.enums import EventSeverity, EventType
from app.database.base import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (UniqueConstraint("source", "external_event_id", name="uq_events_source_external_event_id"),)

    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    external_event_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_type: Mapped[EventType] = mapped_column(String(64), nullable=False, index=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    worker_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    severity: Mapped[EventSeverity] = mapped_column(String(16), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    event_metadata: Mapped[dict[str, Any]] = mapped_column("metadata", JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    event_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    processing_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
