from __future__ import annotations

from datetime import timedelta
from typing import Any

from sqlalchemy import func, or_, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import checksum
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.reliability.models import OutboxMessage, ProcessedEvent


class ProcessedEventRepository:
    async def get(self, session: AsyncSession, *, external_event_id: str, source: str) -> ProcessedEvent | None:
        result = await session.execute(
            select(ProcessedEvent).where(ProcessedEvent.external_event_id == external_event_id, ProcessedEvent.source == source)
        )
        return result.scalars().first()

    async def create(
        self,
        session: AsyncSession,
        *,
        external_event_id: str,
        source: str,
        event_id: str,
        payload: dict[str, Any],
        processing_version: int,
    ) -> ProcessedEvent | None:
        processed_event_id = generate_uuid()
        payload_checksum = checksum(payload)
        record = ProcessedEvent(
            processed_event_id=processed_event_id,
            external_event_id=external_event_id,
            source=source,
            event_id=event_id,
            checksum=payload_checksum,
            processing_version=processing_version,
            trace={"payload": payload},
        )
        bind = session.get_bind()
        dialect_name = bind.dialect.name if bind is not None else ""
        values = {
            "processed_event_id": processed_event_id,
            "external_event_id": external_event_id,
            "source": source,
            "event_id": event_id,
            "checksum": payload_checksum,
            "processing_version": processing_version,
            "trace": {"payload": payload},
        }

        if dialect_name == "postgresql":
            stmt = pg_insert(ProcessedEvent.__table__).values(**values).on_conflict_do_nothing(index_elements=["external_event_id", "source"])
            result = await session.execute(stmt)
            if result.rowcount == 0:
                return None
        elif dialect_name == "sqlite":
            stmt = sqlite_insert(ProcessedEvent.__table__).values(**values).on_conflict_do_nothing(index_elements=["external_event_id", "source"])
            result = await session.execute(stmt)
            if result.rowcount == 0:
                return None
        else:
            session.add(record)
            await session.flush()
            return record

        await session.flush()
        return await session.get(ProcessedEvent, processed_event_id)


class OutboxRepository:
    async def create(
        self,
        session: AsyncSession,
        *,
        topic: str,
        event_type: str,
        aggregate_type: str,
        aggregate_id: str,
        partition_key: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
        status: str = "PENDING",
        max_attempts: int = 10,
        next_attempt_at=None,
    ) -> OutboxMessage:
        record = OutboxMessage(
            outbox_id=generate_uuid(),
            topic=topic,
            event_type=event_type,
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            partition_key=partition_key,
            payload=payload,
            headers=headers or {},
            checksum=checksum(payload),
            status=status,
            attempts=0,
            max_attempts=max_attempts,
            next_attempt_at=next_attempt_at,
        )
        session.add(record)
        await session.flush()
        return record

    async def fetch_due(self, session: AsyncSession, *, limit: int = 50) -> list[OutboxMessage]:
        now = utcnow()
        result = await session.execute(
            select(OutboxMessage)
            .where(
                OutboxMessage.status.in_(["PENDING", "RETRY"]),
                or_(OutboxMessage.next_attempt_at.is_(None), OutboxMessage.next_attempt_at <= now),
            )
            .order_by(OutboxMessage.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def mark_delivered(self, session: AsyncSession, outbox_id) -> None:
        await session.execute(update(OutboxMessage).where(OutboxMessage.outbox_id == outbox_id).values(status="DELIVERED", delivered_at=utcnow(), updated_at=utcnow()))

    async def mark_retry(self, session: AsyncSession, outbox_id, *, error: str, attempts: int, backoff_seconds: int) -> None:
        await session.execute(
            update(OutboxMessage)
            .where(OutboxMessage.outbox_id == outbox_id)
            .values(status="RETRY", attempts=attempts, next_attempt_at=utcnow() + timedelta(seconds=backoff_seconds), last_error=error, updated_at=utcnow(), version=OutboxMessage.version + 1)
        )

    async def mark_dead_lettered(self, session: AsyncSession, outbox_id, *, error: str) -> None:
        await session.execute(
            update(OutboxMessage)
            .where(OutboxMessage.outbox_id == outbox_id)
            .values(status="DEAD_LETTERED", dead_lettered_at=utcnow(), last_error=error, updated_at=utcnow())
        )

    async def backlog_count(self, session: AsyncSession) -> int:
        result = await session.execute(select(func.count()).select_from(OutboxMessage).where(OutboxMessage.status.in_(["PENDING", "RETRY"])))
        return int(result.scalar_one())
