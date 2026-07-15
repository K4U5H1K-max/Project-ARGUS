from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.models import ActionEvent
from app.actions.repositories import ActionRepository
from app.actions.rules import ActionDraft, RuleRegistry
from app.actions.schemas import ActionObject
from app.core.enums import ActionStatus
from app.core.logging import get_logger
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.context.schemas import ContextObject
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.models.event import Event


class ActionEngine:
    def __init__(self, repository: ActionRepository, registry: RuleRegistry, outbox_service: OutboxService) -> None:
        self.repository = repository
        self.registry = registry
        self.outbox_service = outbox_service
        self.logger = get_logger(__name__)

    async def evaluate(self, session: AsyncSession, *, context: ContextObject, event: Event) -> list[ActionObject]:
        drafts = self.registry.evaluate(context=context, event=event)
        actions: list[ActionObject] = []
        for draft in drafts:
            action = ActionEvent(
                action_id=str(generate_uuid()),
                action_type=str(draft.action_type),
                priority=draft.priority,
                reason=draft.reason,
                generated_by=draft.generated_by,
                timestamp=utcnow(),
                context_id=context.context_id,
                status=str(ActionStatus.PENDING),
                action_data=draft.action_data or {},
                plant_id=context.plant_id,
                zone_id=context.zone_id,
                trace_metadata={"context_id": context.context_id, "event_id": event.event_id.hex if hasattr(event.event_id, "hex") else str(event.event_id), "rule": draft.generated_by},
            )
            stored = await self.repository.create(session, action)
            action_model = ActionObject(
                action_id=stored.action_id,
                action_type=stored.action_type,
                priority=stored.priority,
                reason=stored.reason,
                generated_by=stored.generated_by,
                timestamp=stored.timestamp,
                context_id=stored.context_id,
                status=stored.status,
                action_data=stored.action_data,
                plant_id=stored.plant_id,
                zone_id=stored.zone_id,
            )
            self.logger.info("action_generated", action_id=stored.action_id, action_type=stored.action_type)
            await self.outbox_service.enqueue(
                session,
                OutboxEnvelope(
                    topic="industrial.events",
                    event_type="ActionGenerated",
                    aggregate_type="action",
                    aggregate_id=stored.action_id,
                    partition_key=stored.plant_id,
                    payload={
                        "event_name": "ActionGenerated",
                        "action": action_model.model_dump(mode="json"),
                        "trace": stored.trace_metadata,
                    },
                    headers={"context_id": stored.context_id, "rule": draft.generated_by},
                ),
            )
            stored.status = str(ActionStatus.EMITTED)
            await self.repository.create(session, stored)
            action_model.status = str(ActionStatus.EMITTED)
            actions.append(action_model)
            self.logger.info("action_published", action_id=stored.action_id)
        return actions
