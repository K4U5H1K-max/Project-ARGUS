from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.models import ActionEvent
from app.context.models import ContextSnapshot
from app.digital_twin.models import EquipmentState, HazardState, MaintenanceState, PermitState, PlantState, SensorState, TwinStateSnapshot, WorkerState, ZoneState
from app.models.event import Event
from app.phase2.coordinator import Phase2Coordinator


@dataclass(slots=True)
class ReplayRequest:
    plant_id: str
    replay_until: datetime | None = None
    replay_until_event_id: UUID | None = None
    from_checkpoint_context_id: str | None = None
    full_replay: bool = False


@dataclass(slots=True)
class ReplayResult:
    processed_events: int
    rebuilt_contexts: int
    rebuilt_actions: int


class ReplayService:
    def __init__(self, phase2_coordinator: Phase2Coordinator) -> None:
        self.phase2_coordinator = phase2_coordinator

    async def replay(self, session: AsyncSession, request: ReplayRequest) -> ReplayResult:
        statement = select(Event).where(Event.plant_id == request.plant_id).order_by(Event.timestamp.asc(), Event.event_id.asc())
        if request.replay_until is not None:
            statement = statement.where(Event.timestamp <= request.replay_until)
        if request.replay_until_event_id is not None:
            statement = statement.where(Event.event_id <= request.replay_until_event_id)

        events = list((await session.execute(statement)).scalars().all())

        if request.full_replay:
            await self._reset_plant_state(session, request.plant_id)

        processed = 0
        for event in events:
            await self.phase2_coordinator.handle_event(session, event)
            processed += 1

        return ReplayResult(processed_events=processed, rebuilt_contexts=processed, rebuilt_actions=processed)

    async def _reset_plant_state(self, session: AsyncSession, plant_id: str) -> None:
        for model in [TwinStateSnapshot, ContextSnapshot, ActionEvent, PlantState, ZoneState, EquipmentState, WorkerState, PermitState, MaintenanceState, SensorState, HazardState]:
            await session.execute(delete(model).where(getattr(model, "plant_id", plant_id) == plant_id))
