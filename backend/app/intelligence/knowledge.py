from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class KnowledgeTopic:
    topic: str
    query: str
    weight: float
    rationale: str


class KnowledgeFusionService:
    def derive_topics(self, *, risk_level: str, rule_ids: list[str], hazards: list[str], plant_context: dict[str, Any]) -> list[KnowledgeTopic]:
        topics: list[KnowledgeTopic] = [
            KnowledgeTopic(topic="safety-procedures", query="permit procedure emergency manual SOP", weight=1.0, rationale="baseline operational guidance"),
            KnowledgeTopic(topic="regulations", query="Factory Act DGMS OISD OSHA industrial safety", weight=1.0, rationale="compliance references"),
        ]
        if risk_level in {"HIGH", "CRITICAL"}:
            topics.append(KnowledgeTopic(topic="incident-patterns", query="near miss incident root cause preventive action", weight=1.2, rationale="high-severity incidents merit historical comparison"))
        if any("gas" in hazard.lower() for hazard in hazards):
            topics.append(KnowledgeTopic(topic="gas-exposure", query="gas exposure ventilation confined space monitoring", weight=1.1, rationale="gas exposure is part of the current hazard profile"))
        if any("permit" in rule_id.lower() for rule_id in rule_ids):
            topics.append(KnowledgeTopic(topic="permit-control", query="permit suspension hot work isolation verification", weight=1.1, rationale="permit rules require work control evidence"))
        if plant_context.get("workers", 0) > 0:
            topics.append(KnowledgeTopic(topic="worker-safety", query="PPE worker exposure evacuation assembly point", weight=1.05, rationale="worker exposure needs protective guidance"))
        return topics
