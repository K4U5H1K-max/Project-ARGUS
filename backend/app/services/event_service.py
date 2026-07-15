from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums import EventSeverity, EventType
from app.core.exceptions import KafkaPublishError, NotFoundError
from app.core.logging import get_logger
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.kafka.producer import EventPublisher
from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreateRequest, EventListResponse, EventResponse
from app.services.event_normalization import EventNormalizationService
from app.services.event_validation import EventValidationService


class EventService:
    def __init__(
        self,
        *,
        repository: EventRepository,
        validator: EventValidationService,
        normalizer: EventNormalizationService,
        publisher: EventPublisher,
    ) -> None:
        self.repository = repository
        self.validator = validator
        self.normalizer = normalizer
        self.publisher = publisher
        self.logger = get_logger(__name__)

    async def create_event(
        self,
        *,
        session: AsyncSession,
        payload: EventCreateRequest,
        request: Request,
    ) -> EventResponse:
        self.logger.info("received_event", source=payload.source, event_type=payload.event_type)
        validated_payload = self.validator.validate(payload.event_type, payload.payload)
        self.logger.info("validated_event", event_type=payload.event_type)

        normalized_payload = self.normalizer.normalize(payload.event_type, validated_payload)
        self.logger.info("normalized_event", event_type=payload.event_type)

        event = Event(
            event_id=generate_uuid(),
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
        )

        async with session.begin():
            stored = await self.repository.create(session, event)

        self.logger.info("stored_event", event_id=str(stored.event_id))

        event_message = self._serialize_event(stored)
        try:
            await self.publisher.publish(event_message)
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.exception("event_publish_failed", event_id=str(stored.event_id))
            raise KafkaPublishError("Event stored but Kafka publication failed") from exc

        self.logger.info("published_event", event_id=str(stored.event_id))
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
        }

    def _to_response(self, event: Event) -> EventResponse:
        return EventResponse(
            event_id=event.event_id,
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
