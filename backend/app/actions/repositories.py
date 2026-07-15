from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.models import ActionEvent


class ActionRepository:
    async def create(self, session: AsyncSession, action: ActionEvent) -> ActionEvent:
        merged = await session.merge(action)
        await session.flush()
        return merged

    async def get_latest(self, session: AsyncSession, plant_id: str | None = None) -> ActionEvent | None:
        statement = select(ActionEvent).order_by(ActionEvent.timestamp.desc())
        if plant_id is not None:
            statement = statement.where(ActionEvent.plant_id == plant_id)
        result = await session.execute(statement.limit(1))
        return result.scalars().first()

    async def list_history(self, session: AsyncSession, *, plant_id: str | None = None, limit: int = 100, offset: int = 0) -> tuple[list[ActionEvent], int]:
        statement = select(ActionEvent).order_by(ActionEvent.timestamp.desc()).limit(limit).offset(offset)
        if plant_id is not None:
            statement = statement.where(ActionEvent.plant_id == plant_id)
        result = await session.execute(statement)
        items = list(result.scalars().all())

        count_statement = select(ActionEvent.action_id)
        if plant_id is not None:
            count_statement = count_statement.where(ActionEvent.plant_id == plant_id)
        count_result = await session.execute(count_statement)
        total = len(list(count_result.scalars().all()))
        return items, total

