from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.context.schemas import ContextObject
from app.models.event import Event


@dataclass(frozen=True)
class RuleMatch:
    rule_id: str
    version: int
    matched: bool
    severity: int
    confidence: float
    evidence: dict[str, Any]
    explanation: str
    recommendation: str
    affected_entities: tuple[str, ...] = ()
    contributing_graph_nodes: tuple[str, ...] = ()
    contributing_graph_relationships: tuple[str, ...] = ()
    time_window_minutes: int = 0


class RiskRule:
    rule_id = ""
    version = 1
    name = ""
    category = "compound"
    priority = 100
    enabled = True
    description = ""

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        raise NotImplementedError


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _gas_ppm(event: Event) -> float:
    return _number(event.payload.get("gas_ppm", event.payload.get("ppm", 0)))


def _sensor_readings(context: ContextObject) -> list[dict[str, Any]]:
    readings: list[dict[str, Any]] = []
    for value in context.recent_sensor_values.values():
        if isinstance(value, dict):
            readings.append(dict(value.get("reading", value)))
    return readings


def _recent_values(context: ContextObject, key: str) -> list[Any]:
    values: list[Any] = []
    for value in context.recent_sensor_values.values():
        if isinstance(value, dict):
            if key in value:
                values.append(value[key])
            elif isinstance(value.get("reading"), dict) and key in value["reading"]:
                values.append(value["reading"][key])
    return values


class HotWorkGasRule(RiskRule):
    rule_id = "hot_work_flammable_gas"
    name = "Hot work and flammable gas"
    description = "Detects hot work while flammable gas is elevated."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        gas = _gas_ppm(event)
        matched = bool(context.active_permits) and gas >= 20
        return RuleMatch(self.rule_id, 1, matched, 100, 0.98, {"gas_ppm": gas, "permits": list(context.active_permits)}, "Active hot-work permit overlaps elevated flammable gas.", "Suspend hot work and evacuate the zone.")


class GasWorkerRule(RiskRule):
    rule_id = "gas_worker_presence"
    name = "Gas exposure"
    description = "Detects workers exposed to elevated gas."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        gas = _gas_ppm(event)
        matched = context.workers > 0 and gas >= 20
        return RuleMatch(self.rule_id, 1, matched, 80, 0.92, {"gas_ppm": gas, "workers": context.workers}, "Workers are present while gas is elevated.", "Evacuate personnel and increase gas monitoring.")


class MaintenanceEnergizedRule(RiskRule):
    rule_id = "maintenance_energized_equipment"
    name = "Maintenance conflict"
    description = "Detects active maintenance on energized equipment."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        matched = context.maintenance and context.equipment_running > 0
        return RuleMatch(self.rule_id, 1, matched, 75, 0.9, {"maintenance": context.maintenance, "equipment_running": context.equipment_running}, "Maintenance overlaps running equipment.", "Lock and isolate the equipment.")


class ConfinedSpaceOxygenRule(RiskRule):
    rule_id = "confined_space_low_oxygen"
    name = "Confined-space oxygen"
    priority = 1
    description = "Detects personnel in oxygen-deficient confined spaces."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        oxygen = _number(event.payload.get("oxygen_pct", 100) or 100)
        matched = context.workers > 0 and ("CONFINED_SPACE" in context.active_permits or str(event.event_type) == "CONFINED_SPACE") and oxygen < 19.5
        return RuleMatch(self.rule_id, 1, matched, 100, 0.98, {"oxygen_pct": oxygen, "workers": context.workers}, "Personnel are in a confined space with oxygen below the safe limit.", "Evacuate the confined space and ventilate immediately.")


class PermitOverlapRule(RiskRule):
    rule_id = "permit_overlap"
    name = "Permit overlap"
    description = "Detects simultaneous operational permits."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        matched = len(context.active_permits) > 1
        return RuleMatch(self.rule_id, 1, matched, 75, 0.88, {"permits": list(context.active_permits)}, "Multiple active permits overlap in the same zone.", "Suspend conflicting permits and notify the supervisor.")


class WorkerDensityRule(RiskRule):
    rule_id = "worker_density"
    name = "Worker density"
    description = "Detects excess worker density."

    def __init__(self, safe_workers: int = 5) -> None:
        self.safe_workers = safe_workers

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        matched = context.workers > self.safe_workers
        return RuleMatch(self.rule_id, 1, matched, 50, 0.82, {"workers": context.workers, "safe_limit": self.safe_workers}, "Worker density exceeds the configured zone limit.", "Limit zone entry and stage personnel outside the hazard area.")


class HazardCascadeRule(RiskRule):
    rule_id = "hazard_cascade"
    name = "Hazard cascade"
    description = "Escalates multiple active hazards."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        matched = len(context.hazards) >= 2
        return RuleMatch(self.rule_id, 1, matched, 72, 0.86, {"hazards": list(context.hazards)}, "Multiple hazards are active in one zone.", "Dispatch a safety officer and isolate the affected zone.")


class SensorConflictRule(RiskRule):
    rule_id = "sensor_conflict"
    name = "Sensor conflict"
    description = "Detects contradictory sensor readings."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        readings = _sensor_readings(context)
        gases = [
            _number(reading.get("gas_ppm", reading.get("ppm")))
            for reading in readings
            if reading.get("gas_ppm") is not None or reading.get("ppm") is not None
        ]
        matched = len(gases) >= 2 and max(gases) - min(gases) > 50
        return RuleMatch(self.rule_id, 1, matched, 55, 0.75, {"readings": readings}, "Sensor readings conflict beyond the configured tolerance.", "Dispatch inspection and increase independent monitoring.")


class AlarmFloodRule(RiskRule):
    rule_id = "alarm_flood"
    name = "Alarm flood"
    description = "Detects excessive alarm density."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        flood_count = sum(1 for reading in _sensor_readings(context) if str(reading.get("status", "")).upper() in {"ALARM", "CRITICAL"})
        payload_count = int(event.payload.get("alarm_count", 0) or 0)
        matched = flood_count + payload_count >= 5
        return RuleMatch(self.rule_id, 1, matched, 68, 0.84, {"alarm_count": flood_count + payload_count, "recent_signals": len(context.recent_sensor_values)}, "Multiple alarms are active in a short window.", "Stabilize the control room, validate sensors, and notify supervision.")


class GasTrendEscalationRule(RiskRule):
    rule_id = "gas_trend_escalation"
    name = "Gas trend escalation"
    description = "Detects a monotonic increase in gas readings."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        readings = _recent_values(context, "gas_ppm") or _recent_values(context, "ppm")
        ordered = [_number(value) for value in readings if value is not None]
        matched = len(ordered) >= 3 and ordered[-1] > ordered[0] and ordered[-1] - ordered[0] >= 10
        return RuleMatch(self.rule_id, 1, matched, 78, 0.9, {"gas_trend": ordered}, "Gas readings are trending upward across the recent window.", "Escalate monitoring and prepare zone isolation.")


class EmergencyEscalationRule(RiskRule):
    rule_id = "emergency_escalation"
    name = "Emergency escalation"
    description = "Escalates active emergencies."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        event_name = str(event.event_type)
        matched = event_name in {"FIRE", "LEAK", "EXPLOSION"} or (event_name == "NEAR_MISS" and context.recent_incidents > 0)
        return RuleMatch(self.rule_id, 1, matched, 100, 0.99, {"event_type": event_name, "recent_incidents": context.recent_incidents}, "The zone is experiencing an active emergency or a near-miss pattern.", "Trigger the emergency response protocol and clear the affected zone.")


class EquipmentDependencyFailureRule(RiskRule):
    rule_id = "equipment_dependency_failure"
    name = "Equipment dependency failure"
    description = "Detects failed assets that other equipment depends on."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        failed_assets = [equipment for equipment in context.nearby_equipment if str(equipment.get("state", {}).get("status", "")).upper() in {"OFFLINE", "FAILED", "STOPPED"}]
        dependent_assets = [equipment for equipment in context.nearby_equipment if equipment.get("state", {}).get("depends_on")]
        matched = bool(failed_assets and dependent_assets)
        return RuleMatch(self.rule_id, 1, matched, 70, 0.83, {"failed_assets": failed_assets, "dependent_assets": dependent_assets}, "An upstream asset is offline and dependent equipment is still present.", "Isolate affected equipment and inspect the dependency chain.")


class NeighborHazardPropagationRule(RiskRule):
    rule_id = "neighbor_hazard_propagation"
    name = "Neighbor hazard propagation"
    description = "Detects propagation into neighboring assets or zones."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        neighboring_hazards = [hazard for hazard in context.hazards if "NEIGHBOR" in hazard.upper() or "PROPAGAT" in hazard.upper()]
        nearby_asset_count = len(context.nearby_equipment)
        matched = bool(neighboring_hazards) or (nearby_asset_count >= 3 and context.recent_incidents > 0)
        return RuleMatch(self.rule_id, 1, matched, 74, 0.87, {"hazards": neighboring_hazards, "nearby_assets": nearby_asset_count}, "A hazard is propagating through related assets or adjacent zones.", "Expand the exclusion perimeter and inspect affected assets.")


class PermitTimeViolationRule(RiskRule):
    rule_id = "permit_time_violation"
    name = "Permit time violation"
    description = "Detects permits that have exceeded their planned duration."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        expires_at = event.payload.get("expires_at")
        duration_minutes = int(event.payload.get("permit_duration_minutes", 0) or 0)
        expired = False
        if expires_at:
            try:
                expired = datetime.fromisoformat(str(expires_at)) <= event.timestamp
            except ValueError:
                expired = False
        matched = expired or (duration_minutes > 0 and duration_minutes >= 480)
        return RuleMatch(self.rule_id, 1, matched, 66, 0.8, {"expires_at": expires_at, "permit_duration_minutes": duration_minutes}, "The permit has expired or exceeded its configured operating window.", "Suspend the permit and revalidate the work scope.")


class RepeatedMaintenanceFailuresRule(RiskRule):
    rule_id = "repeated_maintenance_failures"
    name = "Repeated maintenance failures"
    description = "Detects repeated maintenance events in the same zone."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        retries = int(event.payload.get("maintenance_retries", 0) or 0)
        matched = context.recent_incidents >= 2 or retries >= 2
        return RuleMatch(self.rule_id, 1, matched, 58, 0.77, {"recent_incidents": context.recent_incidents, "maintenance_retries": retries}, "Maintenance problems are repeating in the same operating window.", "Dispatch inspection and verify the asset is safe to return to service.")


class RepeatedAlarmPatternRule(RiskRule):
    rule_id = "repeated_alarm_patterns"
    name = "Repeated alarm patterns"
    description = "Detects repeated alarm patterns on the same sensor family."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        alarm_signals = [reading for reading in _sensor_readings(context) if str(reading.get("status", "")).upper() in {"ALARM", "CRITICAL"}]
        repeated_pattern = int(event.payload.get("repeated_alarm_count", 0) or 0)
        matched = len(alarm_signals) >= 2 or repeated_pattern >= 3
        return RuleMatch(self.rule_id, 1, matched, 62, 0.83, {"alarm_signals": alarm_signals, "repeated_alarm_count": repeated_pattern}, "The same alarm pattern is repeating across the recent window.", "Review sensor health and suppress only after validation.")


class ShiftChangeRiskRule(RiskRule):
    rule_id = "shift_change_risk"
    name = "Shift change risk"
    description = "Flags high-risk handover periods."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        handover_flags = {"SHIFT_CHANGE", "HANDOVER", "SHIFT_START", "SHIFT_END"}
        matched = context.current_shift.upper() in {"NIGHT", "SWING"} or str(event.payload.get("shift_event", "")).upper() in handover_flags
        return RuleMatch(self.rule_id, 1, matched, 54, 0.74, {"current_shift": context.current_shift, "shift_event": event.payload.get("shift_event")}, "The zone is in or near a shift transition window.", "Increase supervision during the handover period.")


class WorkerIsolationRule(RiskRule):
    rule_id = "worker_isolation"
    name = "Worker isolation"
    description = "Detects isolated workers with limited support nearby."

    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch:
        matched = context.workers == 1 and len(context.nearby_equipment) == 0 and len(context.active_permits) == 0
        return RuleMatch(self.rule_id, 1, matched, 47, 0.72, {"workers": context.workers, "nearby_equipment": len(context.nearby_equipment), "permits": list(context.active_permits)}, "A single worker is isolated without nearby assets or active permit support.", "Establish radio check-ins and dispatch a spotter.")


class RuleRegistry:
    def __init__(self, *, worker_density_threshold: int = 5) -> None:
        self.rules: list[RiskRule] = [
            HotWorkGasRule(),
            GasWorkerRule(),
            MaintenanceEnergizedRule(),
            ConfinedSpaceOxygenRule(),
            PermitOverlapRule(),
            WorkerDensityRule(safe_workers=worker_density_threshold),
            HazardCascadeRule(),
            SensorConflictRule(),
            AlarmFloodRule(),
            GasTrendEscalationRule(),
            EmergencyEscalationRule(),
            EquipmentDependencyFailureRule(),
            NeighborHazardPropagationRule(),
            PermitTimeViolationRule(),
            RepeatedMaintenanceFailuresRule(),
            RepeatedAlarmPatternRule(),
            ShiftChangeRiskRule(),
            WorkerIsolationRule(),
        ]

    def evaluate(self, context: ContextObject, event: Event) -> list[RuleMatch]:
        return [rule.evaluate(context, event) for rule in self.rules if rule.enabled]
