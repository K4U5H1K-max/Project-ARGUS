from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.logging import get_logger
from app.core.time import utcnow
from app.kafka.producer import EventPublisher
from app.reliability.repositories import OutboxRepository
from app.reliability.metrics import OUTBOX_FAILED, OUTBOX_PENDING


@dataclass(slots=True)
class WorkerStatus:
    running: bool = False
    last_run_at: Any | None = None
    last_error: str | None = None


class OutboxPublisherWorker:
    def __init__(self, *, session_factory: async_sessionmaker[AsyncSession], publisher: EventPublisher, repository: OutboxRepository | None = None, poll_interval_seconds: float = 2.0) -> None:
        self.session_factory = session_factory
        self.publisher = publisher
        self.repository = repository or OutboxRepository()
        self.poll_interval_seconds = poll_interval_seconds
        self.status = WorkerStatus()
        self.logger = get_logger(__name__)
        self._task: asyncio.Task[None] | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        self.status.running = True
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            await self._task
        self.status.running = False

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                async with self.session_factory() as session:
                    await self._process_batch(session)
                    OUTBOX_PENDING.set(await self.repository.backlog_count(session))
                    await session.commit()
                self.status.last_run_at = utcnow()
            except Exception as exc:  # pragma: no cover - resilient background worker
                self.logger.exception("outbox_worker_error")
                self.status.last_error = str(exc)
            await asyncio.sleep(self.poll_interval_seconds)

    async def _process_batch(self, session: AsyncSession) -> None:
        due_messages = await self.repository.fetch_due(session, limit=25)
        for message in due_messages:
            try:
                await self.publisher.publish(message.payload)
                await self.repository.mark_delivered(session, message.outbox_id)
                self.logger.info("outbox_delivered", outbox_id=str(message.outbox_id), event_type=message.event_type)
            except Exception as exc:
                attempts = message.attempts + 1
                backoff_seconds = min(2 ** attempts, 300)
                if attempts >= message.max_attempts:
                    await self.repository.mark_dead_lettered(session, message.outbox_id, error=str(exc))
                    OUTBOX_FAILED.inc()
                    self.logger.error("outbox_dead_lettered", outbox_id=str(message.outbox_id), error=str(exc))
                else:
                    await self.repository.mark_retry(session, message.outbox_id, error=str(exc), attempts=attempts, backoff_seconds=backoff_seconds)
                    self.logger.warning("outbox_retry_scheduled", outbox_id=str(message.outbox_id), attempts=attempts)
