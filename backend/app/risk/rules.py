from __future__ import annotations
from dataclasses import dataclass
from app.context.schemas import ContextObject
from app.models.event import Event

@dataclass(frozen=True)
class RuleMatch:
    rule_id: str; version: int; matched: bool; severity: int; confidence: float; evidence: dict; explanation: str; recommendation: str

class RiskRule:
    rule_id=""; version=1; name=""; category="compound"; priority=100; enabled=True; description=""
    def evaluate(self, context: ContextObject, event: Event) -> RuleMatch: raise NotImplementedError

class HotWorkGasRule(RiskRule):
    rule_id="hot_work_flammable_gas"; name="Hot work and flammable gas"; description="Detects hot work while flammable gas is elevated."
    def evaluate(self,c,e):
        gas=float(e.payload.get("gas_ppm",e.payload.get("ppm",0)) or 0); matched=bool(c.active_permits) and gas>=20
        return RuleMatch(self.rule_id,1,matched,100,.98,{"gas_ppm":gas,"permits":c.active_permits},"Active hot-work permit overlaps elevated flammable gas.","Suspend hot work and evacuate the zone.")

class GasWorkerRule(RiskRule):
    rule_id="gas_worker_presence"; name="Gas exposure"; description="Detects workers exposed to elevated gas."
    def evaluate(self,c,e):
        gas=float(e.payload.get("gas_ppm",e.payload.get("ppm",0)) or 0); matched=c.workers>0 and gas>=20
        return RuleMatch(self.rule_id,1,matched,80,.92,{"gas_ppm":gas,"workers":c.workers},"Workers are present while gas is elevated.","Evacuate personnel and increase gas monitoring.")

class MaintenanceEnergizedRule(RiskRule):
    rule_id="maintenance_energized_equipment"; name="Maintenance conflict"; description="Detects active maintenance on energized equipment."
    def evaluate(self,c,e):
        matched=c.maintenance and c.equipment_running>0
        return RuleMatch(self.rule_id,1,matched,75,.9,{"maintenance":c.maintenance,"equipment_running":c.equipment_running},"Maintenance overlaps running equipment.","Lock and isolate the equipment.")

class RuleRegistry:
    def __init__(self): self.rules=[HotWorkGasRule(),GasWorkerRule(),MaintenanceEnergizedRule()]
    def evaluate(self,c,e): return [rule.evaluate(c,e) for rule in self.rules if rule.enabled]
