from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.context.models import ContextSnapshot


class ContextRepository:
    async def create(self, session: AsyncSession, snapshot: ContextSnapshot) -> ContextSnapshot:
        merged = await session.merge(snapshot)
        await session.flush()
        return merged

    async def get_latest(self, session: AsyncSession, plant_id: str | None = None) -> ContextSnapshot | None:
        statement = select(ContextSnapshot).order_by(ContextSnapshot.timestamp.desc())
        if plant_id is not None:
            statement = statement.where(ContextSnapshot.plant_id == plant_id)
        result = await session.execute(statement.limit(1))
        return result.scalars().first()

    async def list_history(self, session: AsyncSession, *, plant_id: str | None = None, limit: int = 100, offset: int = 0) -> list[ContextSnapshot]:
        statement = select(ContextSnapshot).order_by(ContextSnapshot.timestamp.desc()).limit(limit).offset(offset)
        if plant_id is not None:
            statement = statement.where(ContextSnapshot.plant_id == plant_id)
        result = await session.execute(statement)
        return list(result.scalars().all())
