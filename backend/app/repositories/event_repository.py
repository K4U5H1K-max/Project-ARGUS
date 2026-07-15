from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    async def create(self, session: AsyncSession, event: Event) -> Event:
        bind = session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else ""
        values = {
            "event_id": event.event_id,
            "external_event_id": event.external_event_id,
            "timestamp": event.timestamp,
            "source": event.source,
            "event_type": event.event_type,
            "plant_id": event.plant_id,
            "zone_id": event.zone_id,
            "equipment_id": event.equipment_id,
            "worker_id": event.worker_id,
            "severity": event.severity,
            "payload": event.payload,
            "metadata": event.event_metadata,
            "event_hash": event.event_hash,
            "processing_version": event.processing_version or 1,
        }

        if dialect_name == "postgresql":
            stmt = pg_insert(Event.__table__).values(**values).on_conflict_do_nothing(index_elements=["source", "external_event_id"])
            result = await session.execute(stmt)
            if result.rowcount == 0:
                existing = await self.get_by_external_event_id(session, event.source, event.external_event_id or "")
                if existing is not None:
                    return existing
        elif dialect_name == "sqlite":
            stmt = sqlite_insert(Event.__table__).values(**values).on_conflict_do_nothing(index_elements=["source", "external_event_id"])
            result = await session.execute(stmt)
            if result.rowcount == 0:
                existing = await self.get_by_external_event_id(session, event.source, event.external_event_id or "")
                if existing is not None:
                    return existing
        else:
            session.add(event)
            await session.flush()
            await session.refresh(event)
            return event

        await session.flush()
        existing = await self.get_by_external_event_id(session, event.source, event.external_event_id or "")
        return existing or event

    async def get_by_external_event_id(self, session: AsyncSession, source: str, external_event_id: str) -> Event | None:
        result = await session.execute(select(Event).where(Event.source == source, Event.external_event_id == external_event_id))
        return result.scalars().first()

    async def get_by_id(self, session: AsyncSession, event_id: UUID) -> Event | None:
        result = await session.execute(select(Event).where(Event.event_id == event_id))
        return result.scalar_one_or_none()

    async def list(self, session: AsyncSession, *, limit: int, offset: int) -> tuple[list[Event], int]:
        items_result = await session.execute(
            select(Event).order_by(Event.timestamp.desc()).limit(limit).offset(offset)
        )
        items = list(items_result.scalars().all())

        total_result = await session.execute(select(func.count()).select_from(Event))
        total = int(total_result.scalar_one())
        return items, total
