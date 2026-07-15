from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol

from app.actions.schemas import ActionObject
from app.core.enums import ActionStatus, ActionType, EventType
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.context.schemas import ContextObject
from app.models.event import Event


@dataclass(slots=True)
class ActionDraft:
    action_type: ActionType
    priority: int
    reason: str
    generated_by: str
    status: ActionStatus = ActionStatus.PENDING
    action_data: dict[str, object] | None = None


class ActionRule(Protocol):
    name: str

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        ...


class RestrictedZoneRule:
    name = "RestrictedZoneRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        restricted = bool(context.weather.get("restricted_zone")) or bool(context.zone.lower().startswith("restricted"))
        if event.event_type == EventType.ENTRY and restricted and not context.active_permits:
            return [
                ActionDraft(
                    action_type=ActionType.RESTRICTED_ZONE_ENTRY,
                    priority=1,
                    reason=f"Worker entered restricted zone {context.zone} without an active permit",
                    generated_by=self.name,
                    action_data={"zone_id": context.zone_id, "event_type": event.event_type},
                )
            ]
        return []


class PermitExpiryRule:
    name = "PermitExpiryRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        expires_at = event.payload.get("expires_at")
        if expires_at:
            try:
                parsed = datetime.fromisoformat(str(expires_at))
            except ValueError:
                return []
            if parsed <= utcnow():
                return [
                    ActionDraft(
                        action_type=ActionType.PERMIT_EXPIRED,
                        priority=2,
                        reason=f"Permit expired for zone {context.zone}",
                        generated_by=self.name,
                        action_data={"permit": event.payload.get("permit_id") or event.event_type},
                    )
                ]
        if event.payload.get("status") in {"EXPIRED", "CLOSED"}:
            return [
                ActionDraft(
                    action_type=ActionType.PERMIT_EXPIRED,
                    priority=2,
                    reason=f"Permit marked as {event.payload.get('status')} in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"permit": event.payload.get("permit_id") or event.event_type},
                )
            ]
        return []


class EquipmentOfflineRule:
    name = "EquipmentOfflineRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        offline = [equipment for equipment in context.nearby_equipment if equipment.get("state", {}).get("status") == "OFFLINE"]
        if offline:
            return [
                ActionDraft(
                    action_type=ActionType.EQUIPMENT_OFFLINE,
                    priority=2,
                    reason=f"One or more equipment assets are offline in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"equipment": offline},
                )
            ]
        return []


class WorkerExitRule:
    name = "WorkerExitRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        if event.event_type == EventType.EXIT and context.workers == 0:
            return [
                ActionDraft(
                    action_type=ActionType.WORKER_EXIT,
                    priority=3,
                    reason=f"Worker exit recorded without an active presence in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"worker_id": event.worker_id},
                )
            ]
        return []


class MaintenanceStartedRule:
    name = "MaintenanceStartedRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        if event.event_type == EventType.START and event.payload.get("maintenance") is True:
            return [
                ActionDraft(
                    action_type=ActionType.MAINTENANCE_STARTED,
                    priority=2,
                    reason=f"Maintenance started in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"maintenance_id": event.payload.get("maintenance_id")},
                )
            ]
        return []


class PpeViolationRule:
    name = "PpeViolationRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        if event.event_type == EventType.PPE_VIOLATION:
            return [
                ActionDraft(
                    action_type=ActionType.PPE_VIOLATION,
                    priority=1,
                    reason=f"PPE violation reported in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"worker_id": event.worker_id},
                )
            ]
        return []


class HazardDetectedRule:
    name = "HazardDetectedRule"

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        if event.event_type in {EventType.FIRE, EventType.LEAK, EventType.EXPLOSION, EventType.NEAR_MISS}:
            return [
                ActionDraft(
                    action_type=ActionType.HAZARD_DETECTED,
                    priority=1,
                    reason=f"Operational hazard detected in zone {context.zone}",
                    generated_by=self.name,
                    action_data={"hazard": event.event_type},
                )
            ]
        return []


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: list[ActionRule] = [
            RestrictedZoneRule(),
            PermitExpiryRule(),
            EquipmentOfflineRule(),
            WorkerExitRule(),
            MaintenanceStartedRule(),
            PpeViolationRule(),
            HazardDetectedRule(),
        ]

    def evaluate(self, *, context: ContextObject, event: Event) -> list[ActionDraft]:
        actions: list[ActionDraft] = []
        for rule in self._rules:
            actions.extend(rule.evaluate(context=context, event=event))
        return actions
