from __future__ import annotations
from app.core.uuid import generate_uuid
from app.context.schemas import ContextObject
from app.models.event import Event
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.risk.models import RiskAssessment
from app.risk.rules import RuleRegistry

class RiskService:
    def __init__(self, outbox: OutboxService, registry: RuleRegistry|None=None): self.outbox=outbox; self.registry=registry or RuleRegistry()
    async def assess(self, session, *, context: ContextObject, event: Event, graph_revision: int=1, twin_revision: int=1) -> RiskAssessment|None:
        matches=[m for m in self.registry.evaluate(context,event) if m.matched]
        if not matches: return None
        score=min(100,sum(m.severity*m.confidence for m in matches)); level="CRITICAL" if score>=90 else "HIGH" if score>=70 else "MODERATE" if score>=40 else "LOW"
        assessment=RiskAssessment(risk_id=generate_uuid(),plant_id=context.plant_id,zone_id=context.zone_id,timestamp=event.timestamp,revision=1,risk_score=score,risk_level=level,confidence=sum(m.confidence for m in matches)/len(matches),context_id=context.context_id,event_id=str(event.event_id),graph_revision=graph_revision,twin_revision=twin_revision,explanation={"matched_rules":[m.rule_id for m in matches],"evidence":[m.evidence for m in matches],"reasoning":[m.explanation for m in matches]},recommendation=list(dict.fromkeys(m.recommendation for m in matches)),trace={"contributing_events":[str(event.event_id)],"contributing_contexts":[context.context_id],"contributing_graph_nodes":[context.plant_id,context.zone_id],"contributing_rules":[m.rule_id for m in matches]})
        session.add(assessment); await session.flush()
        await self.outbox.enqueue(session,OutboxEnvelope(topic="industrial.events",event_type="RiskDetected",aggregate_type="risk",aggregate_id=str(assessment.risk_id),partition_key=context.plant_id,payload={"risk_id":str(assessment.risk_id),"level":level,"score":score,"explanation":assessment.explanation},headers={"event_id":str(event.event_id),"context_id":context.context_id}))
        return assessment
