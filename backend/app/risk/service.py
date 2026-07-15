from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from datetime import timedelta
from statistics import mean
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.time import utcnow
from app.core.uuid import generate_uuid
from app.context.schemas import ContextObject
from app.models.event import Event
from app.reliability.metrics import ACTIVE_RISKS, AGGREGATION_DURATION, CRITICAL_RISKS, RECOMMENDATIONS_GENERATED, RISK_ASSESSMENTS, RISK_DISTRIBUTION, RISK_ENGINE_DURATION, RISK_ENGINE_LATENCY, RISK_LEVEL, RISK_RULE_DURATION, RISK_RULE_MATCHES, RISK_TIMELINE_QUERIES, TIMELINE_LATENCY
from app.reliability.outbox import OutboxEnvelope, OutboxService
from app.risk.models import RiskAssessment
from app.risk.rules import RuleMatch, RuleRegistry


class RiskService:
    def __init__(self, outbox: OutboxService, registry: RuleRegistry | None = None, settings: Settings | None = None) -> None:
        self.outbox = outbox
        self.settings = settings or get_settings()
        self.registry = registry or RuleRegistry(worker_density_threshold=self.settings.risk_density_threshold)

    async def assess(
        self,
        session: AsyncSession,
        *,
        context: ContextObject,
        event: Event,
        graph_revision: int = 1,
        twin_revision: int = 1,
    ) -> RiskAssessment | None:
        with RISK_ENGINE_DURATION.time():
            with RISK_ENGINE_LATENCY.time():
                matches = await self._evaluate_rules(context, event)

        if not matches:
            return None

        score, level, confidence, modifiers, temporal_context = await self._aggregate_score(session, context=context, event=event, matches=matches)
        recommendations = self._build_recommendations(matches, level=level, context=context)
        explanation = self._build_explanation(
            context=context,
            event=event,
            matches=matches,
            level=level,
            score=score,
            confidence=confidence,
            modifiers=modifiers,
            temporal_context=temporal_context,
            graph_revision=graph_revision,
            twin_revision=twin_revision,
        )
        assessment = RiskAssessment(
            risk_id=generate_uuid(),
            plant_id=context.plant_id,
            zone_id=context.zone_id,
            timestamp=event.timestamp,
            revision=1,
            risk_score=score,
            risk_level=level,
            confidence=confidence,
            context_id=context.context_id,
            event_id=str(event.event_id),
            graph_revision=graph_revision,
            twin_revision=twin_revision,
            explanation=explanation,
            recommendation=recommendations,
            trace={
                "contributing_events": [str(event.event_id)],
                "contributing_contexts": [context.context_id],
                "contributing_graph_nodes": [context.plant_id, context.zone_id]
                + [equipment.get("equipment_id") for equipment in context.nearby_equipment if equipment.get("equipment_id")],
                "contributing_graph_relationships": temporal_context["graph_relationships"],
                "affected_entities": temporal_context["affected_entities"],
                "contributing_rules": [match.rule_id for match in matches],
                "temporal_window_minutes": temporal_context["window_minutes"],
            },
        )
        session.add(assessment)
        await session.flush()

        ACTIVE_RISKS.set(await self._active_risk_count(session, plant_id=context.plant_id, zone_id=context.zone_id))
        RISK_ASSESSMENTS.labels(level=level).inc()
        RISK_LEVEL.labels(level=level).inc()
        RISK_DISTRIBUTION.labels(level=level).inc()
        if level == "CRITICAL":
            CRITICAL_RISKS.inc()
        RECOMMENDATIONS_GENERATED.inc(len(recommendations))

        await self.outbox.enqueue(
            session,
            OutboxEnvelope(
                topic="industrial.events",
                event_type="RiskDetected",
                aggregate_type="risk",
                aggregate_id=str(assessment.risk_id),
                partition_key=context.plant_id,
                payload={
                    "risk_id": str(assessment.risk_id),
                    "level": level,
                    "score": score,
                    "confidence": confidence,
                    "recommendations": recommendations,
                    "explanation": explanation,
                },
                headers={"event_id": str(event.event_id), "context_id": context.context_id, "zone_id": context.zone_id},
            ),
        )
        return assessment

    async def list_history(
        self,
        session: AsyncSession,
        *,
        plant_id: str | None = None,
        zone_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> list[RiskAssessment]:
        query = self._history_query(plant_id=plant_id, zone_id=zone_id, risk_level=risk_level, status=status)
        sort_column = {
            "score": RiskAssessment.risk_score,
            "level": RiskAssessment.risk_level,
            "confidence": RiskAssessment.confidence,
            "timestamp": RiskAssessment.timestamp,
        }.get(sort_by, RiskAssessment.timestamp)
        order = sort_column.asc() if str(sort_order).lower() == "asc" else sort_column.desc()
        secondary = RiskAssessment.risk_id.asc() if str(sort_order).lower() == "asc" else RiskAssessment.risk_id.desc()
        result = await session.execute(query.order_by(order, secondary).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def current(self, session: AsyncSession, *, plant_id: str | None = None, zone_id: str | None = None) -> RiskAssessment | None:
        return await self.latest(session, plant_id=plant_id, zone_id=zone_id)

    async def search(
        self,
        session: AsyncSession,
        *,
        query: str | None = None,
        plant_id: str | None = None,
        zone_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> list[RiskAssessment]:
        items = await self.list_history(
            session,
            plant_id=plant_id,
            zone_id=zone_id,
            risk_level=risk_level,
            status=status,
            limit=max(limit, self.settings.risk_history_limit),
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        if not query:
            return items[:limit]
        needle = query.lower()
        filtered = [
            item
            for item in items
            if needle in item.plant_id.lower()
            or needle in item.zone_id.lower()
            or needle in item.risk_level.lower()
            or needle in item.status.lower()
            or needle in str(item.explanation).lower()
            or any(needle in recommendation.lower() for recommendation in item.recommendation)
        ]
        return filtered[:limit]

    async def statistics(
        self,
        session: AsyncSession,
        *,
        plant_id: str | None = None,
        zone_id: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any]:
        items = await self.list_history(session, plant_id=plant_id, zone_id=zone_id, status=status, limit=self.settings.risk_history_limit * 20)
        level_counts = Counter(item.risk_level for item in items)
        active_count = sum(1 for item in items if item.status == "ACTIVE")
        ACTIVE_RISKS.set(active_count)
        average_score = round(sum(item.risk_score for item in items) / len(items), 2) if items else 0.0
        peak = max(items, key=lambda item: item.risk_score, default=None)
        return {
            "total": len(items),
            "active": active_count,
            "level_counts": dict(level_counts),
            "average_score": average_score,
            "peak_score": peak.risk_score if peak is not None else 0.0,
            "peak_level": peak.risk_level if peak is not None else None,
            "peak_risk_id": str(peak.risk_id) if peak is not None else None,
            "latest": self._assessment_payload(items[0]) if items else None,
        }

    async def list_history_by_filter(
        self,
        session: AsyncSession,
        *,
        plant_id: str | None = None,
        zone_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> list[RiskAssessment]:
        return await self.list_history(
            session,
            plant_id=plant_id,
            zone_id=zone_id,
            risk_level=risk_level,
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def history(
        self,
        session: AsyncSession,
        *,
        plant_id: str | None = None,
        zone_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "timestamp",
        sort_order: str = "desc",
    ) -> list[RiskAssessment]:
        return await self.list_history_by_filter(
            session,
            plant_id=plant_id,
            zone_id=zone_id,
            risk_level=risk_level,
            status=status,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def recent_summary(self, session: AsyncSession, *, plant_id: str | None = None, zone_id: str | None = None) -> dict[str, Any]:
        items = await self.list_history(session, plant_id=plant_id, zone_id=zone_id, limit=5)
        return self._timeline_summary(items)

    async def latest(self, session: AsyncSession, *, plant_id: str | None = None, zone_id: str | None = None) -> RiskAssessment | None:
        items = await self.list_history(session, plant_id=plant_id, zone_id=zone_id, limit=1)
        return items[0] if items else None

    async def timeline(self, session: AsyncSession, *, plant_id: str | None = None, zone_id: str | None = None, limit: int = 50) -> dict[str, Any]:
        with TIMELINE_LATENCY.time():
            RISK_TIMELINE_QUERIES.inc()
            history = await self.list_history(session, plant_id=plant_id, zone_id=zone_id, limit=limit)
            ordered = list(reversed(history))
            return {
                "items": [self._assessment_payload(item) for item in ordered],
                "summary": self._timeline_summary(history),
                "limit": limit,
            }

    async def timeline_window(self, session: AsyncSession, *, plant_id: str, zone_id: str, window_minutes: int | None = None) -> list[RiskAssessment]:
        minutes = window_minutes or self.settings.risk_temporal_window_minutes
        cutoff = utcnow() - timedelta(minutes=minutes)
        query = (
            select(RiskAssessment)
            .where(RiskAssessment.plant_id == plant_id, RiskAssessment.zone_id == zone_id, RiskAssessment.timestamp >= cutoff)
            .order_by(RiskAssessment.timestamp.asc())
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def _evaluate_rules(self, context: ContextObject, event: Event) -> list[RuleMatch]:
        matches: list[RuleMatch] = []
        for rule in self.registry.rules:
            with RISK_RULE_DURATION.labels(rule_id=rule.rule_id).time():
                match = rule.evaluate(context, event)
            if match.matched:
                RISK_RULE_MATCHES.labels(rule_id=match.rule_id).inc()
                self._enrich_match(match, context=context, event=event)
                matches.append(match)
        return matches

    async def _aggregate_score(self, session: AsyncSession, *, context: ContextObject, event: Event, matches: Sequence[RuleMatch]) -> tuple[float, str, float, dict[str, Any], dict[str, Any]]:
        with AGGREGATION_DURATION.time():
            recent = await self.timeline_window(session, plant_id=context.plant_id, zone_id=context.zone_id)
            rule_strength = sum(match.severity * match.confidence for match in matches) / max(len(matches), 1)
            average_confidence = mean(match.confidence for match in matches)
            exposure_bonus = min(20.0, (context.workers * self.settings.risk_score_exposure_weight) + (len(context.active_permits) * self.settings.risk_score_exposure_weight * 0.45) + (len(context.hazards) * self.settings.risk_score_exposure_weight * 0.35) + (context.equipment_running * self.settings.risk_score_exposure_weight * 0.25))
            spatial_bonus = min(15.0, (len(context.nearby_equipment) + len(context.hazards)) * self.settings.risk_score_spatial_weight * 0.5)
            temporal_context = self._temporal_context(recent)
            temporal_bonus = min(20.0, temporal_context["bonus"] * self.settings.risk_score_temporal_weight)
            compound_bonus = min(20.0, self._compound_bonus(matches, recent) * self.settings.risk_score_compound_weight)
            history_bonus = min(15.0, (context.recent_incidents * self.settings.risk_score_history_weight * 0.5) + temporal_context["recent_high_count"] * 1.5)
            score = min(100.0, round((rule_strength * self.settings.risk_score_rule_weight) + (average_confidence * self.settings.risk_score_confidence_weight) + exposure_bonus + spatial_bonus + temporal_bonus + compound_bonus + history_bonus, 2))
            level = self._risk_level(score)
            confidence = round(min(0.99, (average_confidence * 0.85) + min(0.1, len(matches) * 0.02) + min(0.05, temporal_context["bonus"] * 0.01)), 3)
            modifiers = {
                "rule_strength": round(rule_strength, 2),
                "average_confidence": round(average_confidence, 3),
                "exposure_bonus": round(exposure_bonus, 2),
                "spatial_bonus": round(spatial_bonus, 2),
                "temporal_bonus": round(temporal_bonus, 2),
                "compound_bonus": round(compound_bonus, 2),
                "history_bonus": round(history_bonus, 2),
                "recent_assessments": len(recent),
            }
            temporal_context["bonus"] = round(temporal_bonus + compound_bonus + history_bonus, 2)
            return score, level, confidence, modifiers, temporal_context

    def _risk_level(self, score: float) -> str:
        if score >= self.settings.risk_critical_threshold:
            return "CRITICAL"
        if score >= self.settings.risk_high_threshold:
            return "HIGH"
        if score >= self.settings.risk_moderate_threshold:
            return "MODERATE"
        return "LOW"

    def _build_recommendations(self, matches: Sequence[RuleMatch], *, level: str, context: ContextObject) -> list[str]:
        recommendations = list(dict.fromkeys(match.recommendation for match in matches))
        if level == "CRITICAL":
            recommendations.append("Initiate emergency response and suspend all non-essential operations.")
            recommendations.append("Create incident record and dispatch a safety officer immediately.")
        elif level == "HIGH":
            recommendations.append("Increase monitoring and notify the shift supervisor.")
            recommendations.append("Trigger inspection and prepare equipment shutdown procedures.")
        if context.workers > self.settings.risk_density_threshold:
            recommendations.append("Reduce zone occupancy and stage workers outside the hazard envelope.")
        if context.maintenance and context.equipment_running > 0:
            recommendations.append("Shutdown equipment and isolate the maintenance boundary.")
        if context.active_permits:
            recommendations.append("Review permit validity and suspend conflicting permits.")
        return list(dict.fromkeys(recommendations))

    def _build_explanation(
        self,
        *,
        context: ContextObject,
        event: Event,
        matches: Sequence[RuleMatch],
        level: str,
        score: float,
        confidence: float,
        modifiers: dict[str, Any],
        temporal_context: dict[str, Any],
        graph_revision: int,
        twin_revision: int,
    ) -> dict[str, Any]:
        matched_rules = [
            {
                "rule_id": match.rule_id,
                "version": match.version,
                "severity": match.severity,
                "confidence": match.confidence,
                "evidence": match.evidence,
                "reasoning": match.explanation,
                "recommendation": match.recommendation,
                "affected_entities": list(match.affected_entities),
                "graph_nodes": list(match.contributing_graph_nodes),
                "graph_relationships": list(match.contributing_graph_relationships),
                "time_window_minutes": match.time_window_minutes,
            }
            for match in matches
        ]
        return {
            "why": f"Matched {len(matches)} deterministic risk rule(s) for zone {context.zone_id}.",
            "matched_rules": matched_rules,
            "context": {
                "context_id": context.context_id,
                "plant_id": context.plant_id,
                "zone_id": context.zone_id,
                "zone": context.zone,
                "workers": context.workers,
                "equipment_running": context.equipment_running,
                "maintenance": context.maintenance,
                "active_permits": list(context.active_permits),
                "hazards": list(context.hazards),
                "recent_incidents": context.recent_incidents,
                "nearby_equipment": context.nearby_equipment,
            },
            "temporal_context": temporal_context,
            "event": {
                "event_id": str(event.event_id),
                "event_type": str(event.event_type),
                "timestamp": event.timestamp.isoformat(),
                "severity": str(event.severity),
            },
            "reasoning_chain": [match.explanation for match in matches],
            "score": score,
            "confidence": confidence,
            "level": level,
            "graph_revision": graph_revision,
            "twin_revision": twin_revision,
            "modifiers": modifiers,
        }

    def _history_query(
        self,
        *,
        plant_id: str | None = None,
        zone_id: str | None = None,
        risk_level: str | None = None,
        status: str | None = None,
    ):
        query = select(RiskAssessment)
        if plant_id is not None:
            query = query.where(RiskAssessment.plant_id == plant_id)
        if zone_id is not None:
            query = query.where(RiskAssessment.zone_id == zone_id)
        if risk_level is not None:
            query = query.where(RiskAssessment.risk_level == risk_level)
        if status is not None:
            query = query.where(RiskAssessment.status == status)
        return query

    async def _active_risk_count(self, session: AsyncSession, *, plant_id: str, zone_id: str) -> int:
        result = await session.execute(
            select(func.count()).select_from(RiskAssessment).where(RiskAssessment.plant_id == plant_id, RiskAssessment.zone_id == zone_id, RiskAssessment.status == "ACTIVE")
        )
        return int(result.scalar_one())

    def _enrich_match(self, match: RuleMatch, *, context: ContextObject, event: Event) -> None:
        affected_entities = self._context_entities(context, event)
        object.__setattr__(match, "affected_entities", tuple(affected_entities))
        object.__setattr__(match, "contributing_graph_nodes", tuple(self._graph_nodes(context, event)))
        object.__setattr__(match, "contributing_graph_relationships", tuple(self._graph_relationships(context, event)))
        object.__setattr__(match, "time_window_minutes", self.settings.risk_temporal_window_minutes if any(keyword in match.rule_id for keyword in ("trend", "repeat", "alarm", "cascade", "shift", "history", "permit_time")) else 0)

    def _context_entities(self, context: ContextObject, event: Event) -> list[str]:
        entities = [context.plant_id, context.zone_id, context.zone, event.source, str(event.event_type)]
        if event.worker_id:
            entities.append(event.worker_id)
        if event.equipment_id:
            entities.append(event.equipment_id)
        entities.extend(str(permit) for permit in context.active_permits)
        entities.extend(str(hazard) for hazard in context.hazards)
        entities.extend(str(equipment.get("equipment_id")) for equipment in context.nearby_equipment if equipment.get("equipment_id"))
        return list(dict.fromkeys(entity for entity in entities if entity))

    def _graph_nodes(self, context: ContextObject, event: Event) -> list[str]:
        nodes = [f"Plant:{context.plant_id}", f"Zone:{context.zone_id}"]
        if event.worker_id:
            nodes.append(f"Worker:{event.worker_id}")
        if event.equipment_id:
            nodes.append(f"Equipment:{event.equipment_id}")
        for permit in context.active_permits:
            nodes.append(f"Permit:{permit}")
        for hazard in context.hazards:
            nodes.append(f"Hazard:{hazard}")
        for equipment in context.nearby_equipment:
            equipment_id = equipment.get("equipment_id")
            if equipment_id:
                nodes.append(f"Equipment:{equipment_id}")
        return list(dict.fromkeys(nodes))

    def _graph_relationships(self, context: ContextObject, event: Event) -> list[str]:
        relationships = [f"Plant({context.plant_id})-[:CONTAINS]->Zone({context.zone_id})"]
        if event.worker_id:
            relationships.append(f"Worker({event.worker_id})-[:WORKING_IN]->Zone({context.zone_id})")
        if event.equipment_id:
            relationships.append(f"Equipment({event.equipment_id})-[:LOCATED_IN]->Zone({context.zone_id})")
        for permit in context.active_permits:
            relationships.append(f"Permit({permit})-[:VALID_FOR]->Zone({context.zone_id})")
        return list(dict.fromkeys(relationships))

    def _temporal_context(self, recent: Sequence[RiskAssessment]) -> dict[str, Any]:
        scores = [item.risk_score for item in recent]
        highs = [item for item in recent if item.risk_level in {"HIGH", "CRITICAL"}]
        trend = len(scores) >= 2 and scores[-1] >= scores[0]
        escalation = len(highs) >= 2 or (len(scores) >= 3 and scores[-1] > scores[0] + 10)
        return {
            "window_minutes": self.settings.risk_temporal_window_minutes,
            "recent_count": len(recent),
            "recent_scores": scores,
            "recent_high_count": len(highs),
            "recent_average": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "trend": trend,
            "escalation": escalation,
            "bonus": 0.0 if not scores else min(1.0, (len(highs) * 0.25) + (0.25 if trend else 0.0) + (0.25 if escalation else 0.0) + min(0.25, (scores[-1] - scores[0]) / 100.0 if len(scores) >= 2 else 0.0)),
            "graph_relationships": ["PRECEDES", "ESCALATES_TO" if escalation else "SUPPORTS"],
            "affected_entities": [],
        }

    def _compound_bonus(self, matches: Sequence[RuleMatch], recent: Sequence[RiskAssessment]) -> float:
        moderate_matches = [match for match in matches if 45 <= match.severity < 85]
        high_matches = [match for match in matches if match.severity >= 85]
        bonus = 0.0
        if len(moderate_matches) >= 2:
            bonus += 1.0 + (len(moderate_matches) - 1) * 0.5
        if high_matches:
            bonus += 0.5 * len(high_matches)
        if len(matches) >= 3:
            bonus += 0.5
        if recent and any(item.risk_level == "CRITICAL" for item in recent):
            bonus += 0.5
        return bonus

    def _assessment_payload(self, assessment: RiskAssessment) -> dict[str, Any]:
        return {
            "risk_id": str(assessment.risk_id),
            "plant_id": assessment.plant_id,
            "zone_id": assessment.zone_id,
            "score": assessment.risk_score,
            "level": assessment.risk_level,
            "confidence": assessment.confidence,
            "status": assessment.status,
            "timestamp": assessment.timestamp,
            "recommendations": assessment.recommendation,
            "explanation": assessment.explanation,
            "trace": assessment.trace,
        }

    def _timeline_summary(self, assessments: Sequence[RiskAssessment]) -> dict[str, Any]:
        if not assessments:
            return {"count": 0, "latest_level": None, "peak_level": None, "peak_score": 0}
        peak = max(assessments, key=lambda item: item.risk_score)
        latest = assessments[0]
        return {
            "count": len(assessments),
            "latest_level": latest.risk_level,
            "latest_score": latest.risk_score,
            "peak_level": peak.risk_level,
            "peak_score": peak.risk_score,
            "latest_timestamp": latest.timestamp,
            "peak_timestamp": peak.timestamp,
        }
