from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.time import utcnow
from app.reliability.repositories import OutboxRepository


@dataclass(slots=True)
class OutboxEnvelope:
    topic: str
    event_type: str
    aggregate_type: str
    aggregate_id: str
    partition_key: str
    payload: dict[str, Any]
    headers: dict[str, Any]


class OutboxService:
    def __init__(self, repository: OutboxRepository) -> None:
        self.repository = repository

    async def enqueue(self, session: AsyncSession, envelope: OutboxEnvelope) -> Any:
        return await self.repository.create(
            session,
            topic=envelope.topic,
            event_type=envelope.event_type,
            aggregate_type=envelope.aggregate_type,
            aggregate_id=envelope.aggregate_id,
            partition_key=envelope.partition_key,
            payload=envelope.payload,
            headers=envelope.headers,
            next_attempt_at=utcnow(),
        )
