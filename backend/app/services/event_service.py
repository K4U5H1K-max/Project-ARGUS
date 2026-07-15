from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import checksum
from app.core.enums import EventSeverity, EventType
from app.core.exceptions import KafkaPublishError, NotFoundError
from app.core.logging import get_logger
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.models.event import Event
from app.reliability.repositories import ProcessedEventRepository
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreateRequest, EventListResponse, EventResponse
from app.services.event_normalization import EventNormalizationService
from app.services.event_validation import EventValidationService
from app.phase2.coordinator import Phase2Coordinator
from app.reliability.metrics import DUPLICATE_EVENTS, EVENTS_FAILED, EVENTS_PROCESSED, EVENT_PROCESSING_DURATION


class EventService:
    def __init__(
        self,
        *,
        repository: EventRepository,
        validator: EventValidationService,
        normalizer: EventNormalizationService,
        outbox_service: OutboxService,
        processed_event_repository: ProcessedEventRepository,
        phase2_coordinator: Phase2Coordinator | None = None,
    ) -> None:
        self.repository = repository
        self.validator = validator
        self.normalizer = normalizer
        self.outbox_service = outbox_service
        self.processed_event_repository = processed_event_repository
        self.phase2_coordinator = phase2_coordinator
        self.logger = get_logger(__name__)

    async def create_event(
        self,
        *,
        session: AsyncSession,
        payload: EventCreateRequest,
        request: Request,
    ) -> EventResponse:
        session.info["event_publisher"] = getattr(request.app.state, "kafka_producer", None)
        self.logger.info("received_event", source=payload.source, event_type=payload.event_type)
        validated_payload = self.validator.validate(payload.event_type, payload.payload)
        self.logger.info("validated_event", event_type=payload.event_type)

        normalized_payload = self.normalizer.normalize(payload.event_type, validated_payload)
        self.logger.info("normalized_event", event_type=payload.event_type)

        external_event_id = payload.external_event_id or request.headers.get("X-External-Event-Id") or str(generate_uuid())
        event = Event(
            event_id=generate_uuid(),
            external_event_id=external_event_id,
            event_hash=checksum({"source": payload.source, "external_event_id": external_event_id, "payload": normalized_payload}),
            timestamp=payload.timestamp or utcnow(),
            source=payload.source,
            event_type=payload.event_type,
            plant_id=payload.plant_id,
            zone_id=payload.zone_id,
            equipment_id=payload.equipment_id,
            worker_id=payload.worker_id,
            severity=payload.severity,
            payload=normalized_payload,
            event_metadata=payload.metadata,
            processing_version=1,
        )

        try:
            with EVENT_PROCESSING_DURATION.labels(event_type=payload.event_type).time():
                async with session.begin():
                    # Persist the event first: the ledger has a real event foreign key.
                    # The ledger's unique constraint is the atomic processing claim.
                    stored = await self.repository.create(session, event)
                    processed = await self.processed_event_repository.create(
                session,
                external_event_id=external_event_id,
                source=payload.source,
                event_id=str(stored.event_id),
                payload={"event": normalized_payload, "metadata": payload.metadata},
                processing_version=1,
            )
                    if processed is None:
                        DUPLICATE_EVENTS.labels(source=payload.source).inc()
                        return self._to_response(stored)

                    await self.outbox_service.enqueue(
                session,
                OutboxEnvelope(
                    topic="industrial.events",
                    event_type="EventCreated",
                    aggregate_type="event",
                    aggregate_id=str(stored.event_id),
                    partition_key=stored.plant_id,
                    payload=self._serialize_event(stored),
                    headers={"source": stored.source, "external_event_id": stored.external_event_id or ""},
                ),
            )

                    if self.phase2_coordinator is not None:
                        await self.phase2_coordinator.handle_event(session, stored, record_ledger=False)
        except Exception:
            EVENTS_FAILED.labels(source=payload.source, event_type=payload.event_type).inc()
            raise

        self.logger.info("stored_event", event_id=str(stored.event_id))
        EVENTS_PROCESSED.labels(source=payload.source, event_type=payload.event_type).inc()
        return self._to_response(stored)

    async def list_events(
        self,
        *,
        session: AsyncSession,
        request: Request,
        limit: int,
        offset: int,
    ) -> EventListResponse:
        items, total = await self.repository.list(session, limit=limit, offset=offset)
        return EventListResponse(items=[self._to_response(item) for item in items], total=total, limit=limit, offset=offset)

    async def get_event_by_id(self, *, session: AsyncSession, request: Request, event_id: UUID) -> EventResponse:
        event = await self.repository.get_by_id(session, event_id)
        if event is None:
            raise NotFoundError(f"Event {event_id} not found")
        return self._to_response(event)

    def _serialize_event(self, event: Event) -> dict[str, Any]:
        return {
            "event_id": str(event.event_id),
            "external_event_id": event.external_event_id,
            "timestamp": event.timestamp.isoformat(),
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
            "processing_version": event.processing_version,
        }

    def _to_response(self, event: Event) -> EventResponse:
        return EventResponse(
            event_id=event.event_id,
            external_event_id=event.external_event_id,
            timestamp=event.timestamp,
            source=event.source,
            event_type=event.event_type,
            plant_id=event.plant_id,
            zone_id=event.zone_id,
            equipment_id=event.equipment_id,
            worker_id=event.worker_id,
            severity=event.severity,
            payload=event.payload,
            metadata=event.event_metadata,
            created_at=event.created_at,
        )
