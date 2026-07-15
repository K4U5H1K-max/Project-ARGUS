from __future__ import annotations
from datetime import datetime
from typing import Any
from uuid import UUID
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from app.database.base import Base

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    risk_id: Mapped[UUID] = mapped_column(primary_key=True)
    plant_id: Mapped[str] = mapped_column(String(64), index=True); zone_id: Mapped[str] = mapped_column(String(64), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True); revision: Mapped[int] = mapped_column(Integer, default=1)
    risk_score: Mapped[float] = mapped_column(Float); risk_level: Mapped[str] = mapped_column(String(16), index=True); confidence: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16), default="ACTIVE", index=True); explanation: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB,"postgresql"), default=dict)
    recommendation: Mapped[list[str]] = mapped_column(JSON().with_variant(JSONB,"postgresql"), default=list); processor_version: Mapped[int] = mapped_column(Integer, default=1)
    context_id: Mapped[str] = mapped_column(String(36), ForeignKey("context_snapshots.context_id"), index=True); event_id: Mapped[str] = mapped_column(String(36), index=True)
    graph_revision: Mapped[int] = mapped_column(Integer, default=1); twin_revision: Mapped[int] = mapped_column(Integer, default=1)
    trace: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB,"postgresql"), default=dict); created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
