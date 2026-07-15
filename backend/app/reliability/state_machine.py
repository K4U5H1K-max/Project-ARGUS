from __future__ import annotations

from dataclasses import dataclass

from app.core.exceptions import ValidationAppError


@dataclass(frozen=True, slots=True)
class Transition:
    from_state: str
    to_state: str


class StateMachine:
    def __init__(self, *, name: str, initial_state: str, transitions: list[Transition]) -> None:
        self.name = name
        self.initial_state = initial_state
        self._transitions = transitions

    def can_transition(self, from_state: str, to_state: str) -> bool:
        return any(item.from_state == from_state and item.to_state == to_state for item in self._transitions)

    def transition(self, current_state: str | None, next_state: str) -> str:
        current = current_state or self.initial_state
        if current == next_state:
            return current
        if not self.can_transition(current, next_state):
            raise ValidationAppError(f"Invalid transition for {self.name}: {current} -> {next_state}")
        return next_state


WORKER_MACHINE = StateMachine(
    name="worker",
    initial_state="UNKNOWN",
    transitions=[Transition("UNKNOWN", "ENTERED"), Transition("ENTERED", "ACTIVE"), Transition("ACTIVE", "EXITED"), Transition("ENTERED", "EXITED")],
)

PERMIT_MACHINE = StateMachine(
    name="permit",
    initial_state="CREATED",
    transitions=[Transition("CREATED", "ACTIVE"), Transition("ACTIVE", "EXPIRED"), Transition("ACTIVE", "CLOSED"), Transition("EXPIRED", "CLOSED")],
)

MAINTENANCE_MACHINE = StateMachine(
    name="maintenance",
    initial_state="SCHEDULED",
    transitions=[Transition("SCHEDULED", "STARTED"), Transition("STARTED", "COMPLETED"), Transition("COMPLETED", "ARCHIVED")],
)
