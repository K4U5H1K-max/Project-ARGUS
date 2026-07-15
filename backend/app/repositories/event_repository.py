from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.event import Event


class EventRepository:
    async def create(self, session: AsyncSession, event: Event) -> Event:
        session.add(event)
        await session.flush()
        await session.refresh(event)
        return event

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
