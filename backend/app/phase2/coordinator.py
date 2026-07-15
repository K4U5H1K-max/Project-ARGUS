from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.repositories import ActionRepository
from app.actions.rules import RuleRegistry
from app.actions.service import ActionEngine
from app.context.repositories import ContextRepository
from app.context.service import ContextEngine
from app.core.logging import get_logger
from app.core.crypto import checksum
from app.digital_twin.processors.registry import ProcessorRegistry
from app.digital_twin.repositories import TwinRepository
from app.digital_twin.state_manager import StateManager
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.reliability.repositories import ProcessedEventRepository
from app.models.event import Event
from app.graph.synchronizer import GraphSynchronizer
from app.risk.service import RiskService


@dataclass(slots=True)
class Phase2Outcome:
    context_id: str
    action_count: int


class Phase2Coordinator:
    def __init__(self, *, twin_repository: TwinRepository, context_repository: ContextRepository, action_repository: ActionRepository, outbox_service: OutboxService, graph_synchronizer: GraphSynchronizer | None = None, risk_service: RiskService | None = None) -> None:
        self.state_manager = StateManager(ProcessorRegistry())
        self.context_engine = ContextEngine(twin_repository=twin_repository, context_repository=context_repository)
        self.action_engine = ActionEngine(repository=action_repository, registry=RuleRegistry(), outbox_service=outbox_service)
        self.twin_repository = twin_repository
        self.context_repository = context_repository
        self.action_repository = action_repository
        self.outbox_service = outbox_service
        self.graph_synchronizer = graph_synchronizer
        self.risk_service = risk_service or RiskService(outbox_service)
        self.processed_event_repository = ProcessedEventRepository()
        self.logger = get_logger(__name__)

    async def handle_event(self, session: AsyncSession, event: Event, *, record_ledger: bool = True, replay: bool = False) -> Phase2Outcome:
        external_event_id = event.external_event_id or str(event.event_id)
        if record_ledger:
            processed = await self.processed_event_repository.create(
                session,
                external_event_id=external_event_id,
                source=event.source,
                event_id=str(event.event_id),
                payload={"event": event.payload, "metadata": event.event_metadata},
                processing_version=1,
            )
            if processed is None:
                self.logger.info("duplicate_event_skipped", event_id=str(event.event_id), external_event_id=external_event_id)
                existing = await self.processed_event_repository.get(session, external_event_id=external_event_id, source=event.source)
                return Phase2Outcome(context_id=existing.trace.get("context_id", "") if existing else "", action_count=0)

        await self.state_manager.apply_event(session, event)
        if self.graph_synchronizer is not None:
            await self.graph_synchronizer.synchronize_event(event, replay=replay)
        context, snapshot = await self.context_engine.build_context(session, event)
        await self.context_repository.create(session, snapshot)
        await self.risk_service.assess(session, context=context, event=event, graph_revision=event.processing_version, twin_revision=event.processing_version)
        await self.outbox_service.enqueue(
            session,
            OutboxEnvelope(
                topic="industrial.events",
                event_type="ContextBuilt",
                aggregate_type="context",
                aggregate_id=snapshot.context_id,
                partition_key=event.plant_id,
                payload={
                    "event_name": "ContextBuilt",
                    "context": context.model_dump(mode="json"),
                    "context_id": snapshot.context_id,
                    "event_id": str(event.event_id),
                    "trace": snapshot.trace_metadata,
                },
                headers={"source_event_id": str(event.event_id), "context_id": snapshot.context_id},
            ),
        )
        actions = await self.action_engine.evaluate(session, context=context, event=event)
        return Phase2Outcome(context_id=snapshot.context_id, action_count=len(actions))
