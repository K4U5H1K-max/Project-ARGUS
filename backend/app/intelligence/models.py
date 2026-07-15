from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

from app.database.base import Base


class IntelligenceDocument(Base):
    __tablename__ = "intelligence_documents"
    __table_args__ = (UniqueConstraint("checksum", name="uq_intelligence_documents_checksum"),)

    document_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256), index=True)
    uri: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    language: Mapped[str] = mapped_column(String(16), default="en")
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    chunks: Mapped[list["IntelligenceChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class IntelligenceChunk(Base):
    __tablename__ = "intelligence_chunks"

    chunk_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("intelligence_documents.document_id"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, index=True)
    content: Mapped[str] = mapped_column(Text)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding: Mapped[dict[str, float]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    metadata: Mapped[dict[str, Any]] = mapped_column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256), index=True)
    uri: Mapped[str | None] = mapped_column(String(512), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    document: Mapped[IntelligenceDocument] = relationship(back_populates="chunks")
