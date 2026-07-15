from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, Uuid

from app.database.base import Base


class PlantState(Base):
    __tablename__ = "plant_states"

    plant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class ZoneState(Base):
    __tablename__ = "zone_states"

    zone_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class EquipmentState(Base):
    __tablename__ = "equipment_states"

    equipment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class WorkerState(Base):
    __tablename__ = "worker_states"

    worker_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class PermitState(Base):
    __tablename__ = "permit_states"

    permit_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class MaintenanceState(Base):
    __tablename__ = "maintenance_states"

    maintenance_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class SensorState(Base):
    __tablename__ = "sensor_states"

    sensor_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class HazardState(Base):
    __tablename__ = "hazard_states"

    hazard_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    equipment_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())


class TwinStateSnapshot(Base):
    __tablename__ = "twin_state_snapshots"

    context_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.event_id", ondelete="CASCADE"), nullable=False, index=True)
    plant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    serialized_state: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False)
    processor_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    trace_metadata: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), nullable=False, default=dict)
