from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.models import ActionEvent
from app.actions.repositories import ActionRepository
from app.actions.rules import ActionDraft, ActionType, RuleRegistry
from app.actions.schemas import ActionObject
from app.core.enums import ActionStatus
from app.core.logging import get_logger
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.context.schemas import ContextObject
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.kafka.producer import EventPublisher
from app.models.event import Event
from app.risk.models import RiskAssessment


class ActionEngine:
    def __init__(
        self,
        repository: ActionRepository,
        registry: RuleRegistry,
        outbox_service: OutboxService | None = None,
        publisher: EventPublisher | None = None,
    ) -> None:
        self.repository = repository
        self.registry = registry
        self.outbox_service = outbox_service
        self.publisher = publisher
        self.logger = get_logger(__name__)

    async def evaluate(self, session: AsyncSession, *, context: ContextObject, event: Event, risk_assessment: RiskAssessment | None = None) -> list[ActionObject]:
        drafts = self.registry.evaluate(context=context, event=event)
        if risk_assessment is not None:
            drafts.extend(self._risk_drafts(risk_assessment, context=context))
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
            envelope = OutboxEnvelope(
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
            )
            if self.outbox_service is not None:
                await self.outbox_service.enqueue(session, envelope)
            elif self.publisher is not None:
                await self.publisher.publish(envelope.payload)
            stored.status = str(ActionStatus.EMITTED)
            await self.repository.create(session, stored)
            action_model.status = str(ActionStatus.EMITTED)
            actions.append(action_model)
            self.logger.info("action_published", action_id=stored.action_id)
        return actions

    def _risk_drafts(self, assessment: RiskAssessment, *, context: ContextObject) -> list[ActionDraft]:
        drafts: list[ActionDraft] = []
        recommendations = list(assessment.recommendation or [])
        if assessment.risk_level == "CRITICAL":
            drafts.append(
                ActionDraft(
                    action_type=ActionType.EVACUATE_ZONE,
                    priority=1,
                    reason=f"Critical risk detected in zone {context.zone}",
                    generated_by="RiskAssessmentEngine",
                    action_data={"risk_id": assessment.risk_id, "risk_level": assessment.risk_level, "score": assessment.risk_score},
                )
            )
        if assessment.risk_level in {"HIGH", "CRITICAL"}:
            drafts.append(
                ActionDraft(
                    action_type=ActionType.NOTIFY_SUPERVISOR,
                    priority=2,
                    reason=f"High risk assessment requires supervisor notification for zone {context.zone}",
                    generated_by="RiskAssessmentEngine",
                    action_data={"risk_id": assessment.risk_id, "risk_level": assessment.risk_level},
                )
            )
        for recommendation in recommendations:
            recommendation_lower = str(recommendation).lower()
            if "evacuate" in recommendation_lower:
                action_type = ActionType.EVACUATE_ZONE
            elif "suspend" in recommendation_lower and "permit" in recommendation_lower:
                action_type = ActionType.SUSPEND_PERMIT
            elif "shutdown" in recommendation_lower or "isolate" in recommendation_lower or "lock" in recommendation_lower:
                action_type = ActionType.LOCK_EQUIPMENT
            elif "monitor" in recommendation_lower:
                action_type = ActionType.INCREASE_MONITORING
            elif "inspect" in recommendation_lower:
                action_type = ActionType.DISPATCH_INSPECTION
            else:
                continue
            drafts.append(
                ActionDraft(
                    action_type=action_type,
                    priority=3 if assessment.risk_level == "HIGH" else 2,
                    reason=recommendation,
                    generated_by="RiskAssessmentEngine",
                    action_data={"risk_id": assessment.risk_id, "risk_level": assessment.risk_level, "score": assessment.risk_score},
                )
            )
        return drafts
