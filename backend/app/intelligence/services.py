from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.context.schemas import ContextObject
from app.core.time import utcnow
from app.intelligence.agents import HistoricalAnalysisAgent, IncidentIntelligenceAgent, RecommendationAgent, RegulationAgent
from app.intelligence.knowledge import KnowledgeFusionService
from app.intelligence.pipelines import DocumentPipeline
from app.intelligence.repositories import DocumentPayload, IntelligenceRepository
from app.intelligence.retrieval import RetrievalHit, RetrievalService
from app.risk.models import RiskAssessment


_DEFAULT_DOCUMENTS: list[DocumentPayload] = [
    DocumentPayload(
        title="OISD Safety Guidance for Hot Work",
        source_type="REGULATION",
        uri="memory:oisd-hot-work",
        content=(
            "Hot work shall only proceed under valid permit control. Flammable gas tests, ventilation, "
            "continuous monitoring, and supervisor authorization are required before ignition sources are introduced. "
            "Suspend work when gas levels trend upward or when nearby workers cannot maintain a safe distance."
        ),
        metadata={"topic": "hot_work", "authority": "OISD"},
    ),
    DocumentPayload(
        title="Factory Act Worker Safety Reference",
        source_type="REGULATION",
        uri="memory:factory-act-worker-safety",
        content=(
            "Employers shall provide safe working conditions, supervision, ventilation, emergency exits, "
            "safe assembly points, and protective equipment. Hazardous work areas require access control, "
            "incident reporting, and documented mitigation steps."
        ),
        metadata={"topic": "worker_safety", "authority": "Factory Act"},
    ),
    DocumentPayload(
        title="DGMS Confined Space and Gas Controls",
        source_type="REGULATION",
        uri="memory:dgms-confined-space",
        content=(
            "Confined space entry requires atmospheric testing, standby personnel, rescue readiness, and isolation of energy sources. "
            "Oxygen deficiency and gas accumulation are criteria for evacuation and escalation."
        ),
        metadata={"topic": "confined_space", "authority": "DGMS"},
    ),
    DocumentPayload(
        title="Industrial Incident: Gas Trend Escalation",
        source_type="INCIDENT_REPORT",
        uri="memory:incident-gas-trend",
        content=(
            "A recurring gas trend escalation was resolved by isolating the leak source, increasing ventilation, "
            "suspending hot work permits, and adding continuous gas monitoring. The root cause was a failing gasket."
        ),
        metadata={"topic": "incident_pattern", "outcome": "mitigated"},
    ),
    DocumentPayload(
        title="Permit Procedure for Hot Work and Maintenance",
        source_type="SOP",
        uri="memory:permit-procedure",
        content=(
            "Permits must be reviewed for conflicts, validity, scope, and overlapping hazardous operations. "
            "Conflicting permits are suspended before work continues, and maintenance boundaries must be isolated from energized equipment."
        ),
        metadata={"topic": "permit_control", "procedure": "work_permit"},
    ),
]


@dataclass(frozen=True, slots=True)
class IntelligenceSection:
    title: str
    summary: str
    items: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    confidence: float


class IndustrialIntelligenceService:
    def __init__(self, repository: IntelligenceRepository | None = None) -> None:
        self.repository = repository or IntelligenceRepository()
        self.retrieval = RetrievalService()
        self.pipeline = DocumentPipeline(self.repository)
        self.knowledge = KnowledgeFusionService()
        self.incident_agent = IncidentIntelligenceAgent()
        self.regulation_agent = RegulationAgent()
        self.historical_agent = HistoricalAnalysisAgent()
        self.recommendation_agent = RecommendationAgent()

    async def get_risk(self, session: AsyncSession, risk_id: str) -> RiskAssessment | None:
        try:
            lookup_id = UUID(risk_id)
        except ValueError:
            return None
        result = await session.execute(select(RiskAssessment).where(RiskAssessment.risk_id == lookup_id))
        return result.scalar_one_or_none()

    async def ensure_seed_corpus(self, session: AsyncSession) -> None:
        existing = await self.repository.list_documents(session)
        if existing:
            return
        for payload in _DEFAULT_DOCUMENTS:
            await self.pipeline.ingest(session, payload)
        await session.commit()

    async def ingest_document(self, session: AsyncSession, payload: DocumentPayload) -> dict[str, Any]:
        result = await self.pipeline.ingest(session, payload)
        await session.commit()
        return {
            "title": result.title,
            "source_type": result.source_type,
            "document_id": result.document_id,
            "chunk_count": result.chunk_count,
            "metadata": result.metadata,
        }

    async def report(self, session: AsyncSession, risk: RiskAssessment, context: ContextObject | None = None) -> dict[str, Any]:
        await self.ensure_seed_corpus(session)
        incident_hits = await self._retrieve(session, risk, section="incident")
        regulation_hits = await self._retrieve(session, risk, section="regulation")
        history_hits = await self._retrieve(session, risk, section="history")
        recommendation_hits = await self._retrieve(session, risk, section="recommendation")
        topics = self.knowledge.derive_topics(
            risk_level=risk.risk_level,
            rule_ids=risk.explanation.get("contributing_rules", []),
            hazards=risk.explanation.get("context", {}).get("hazards", []),
            plant_context=risk.explanation.get("context", {}),
        )
        report = {
            "risk_id": str(risk.risk_id),
            "generated_at": utcnow().isoformat(),
            "risk_summary": {
                "plant_id": risk.plant_id,
                "zone_id": risk.zone_id,
                "score": risk.risk_score,
                "level": risk.risk_level,
                "confidence": risk.confidence,
                "summary": risk.explanation.get("why"),
            },
            "industrial_intelligence": {
                "historical_comparisons": self.historical_agent.summarize(history_hits).items,
                "applicable_standards": self.regulation_agent.summarize(regulation_hits).items,
                "incident_patterns": self.incident_agent.summarize(incident_hits).items,
                "recommendations": self._compose_recommendations(topics, recommendation_hits),
            },
            "citations": self._collect_citations([incident_hits, regulation_hits, history_hits, recommendation_hits]),
            "confidence": self._confidence([incident_hits, regulation_hits, history_hits, recommendation_hits]),
        }
        report["industrial_intelligence"]["root_causes"] = self._root_causes(risk, history_hits)
        report["industrial_intelligence"]["applicable_topics"] = [topic.__dict__ for topic in topics]
        return report

    async def similar_incidents(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        await self.ensure_seed_corpus(session)
        hits = await self._retrieve(session, risk, section="incident", limit=5)
        return self.incident_agent.summarize(hits).items

    async def regulations(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        await self.ensure_seed_corpus(session)
        hits = await self._retrieve(session, risk, section="regulation", limit=5)
        return self.regulation_agent.summarize(hits).items

    async def recommendations(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        await self.ensure_seed_corpus(session)
        hits = await self._retrieve(session, risk, section="recommendation", limit=5)
        topics = self.knowledge.derive_topics(
            risk_level=risk.risk_level,
            rule_ids=risk.explanation.get("contributing_rules", []),
            hazards=risk.explanation.get("context", {}).get("hazards", []),
            plant_context=risk.explanation.get("context", {}),
        )
        return self.recommendation_agent.prioritize(topics, hits)

    async def root_causes(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        await self.ensure_seed_corpus(session)
        hits = await self._retrieve(session, risk, section="history", limit=5)
        return self._root_causes(risk, hits)

    async def citations(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        await self.ensure_seed_corpus(session)
        sections = [
            await self._retrieve(session, risk, section="incident", limit=3),
            await self._retrieve(session, risk, section="regulation", limit=3),
            await self._retrieve(session, risk, section="history", limit=3),
        ]
        return self._collect_citations(sections)

    async def historical_history(self, session: AsyncSession, risk: RiskAssessment) -> list[dict[str, Any]]:
        return await self.similar_incidents(session, risk)

    async def retrieve_for_risk(self, session: AsyncSession, risk: RiskAssessment, *, section: str, limit: int = 5) -> list[RetrievalHit]:
        return await self._retrieve(session, risk, section=section, limit=limit)

    async def _retrieve(self, session: AsyncSession, risk: RiskAssessment, *, section: str, limit: int = 5) -> list[RetrievalHit]:
        chunks = await self.repository.list_chunks(session)
        query = self._query_for_section(risk, section)
        filters = {"source_type": self._source_type_for_section(section)} if self._source_type_for_section(section) else None
        return self.retrieval.rank(query=query, chunks=chunks, filters=filters, limit=limit)

    def _query_for_section(self, risk: RiskAssessment, section: str) -> str:
        context = risk.explanation.get("context", {}) if isinstance(risk.explanation, dict) else {}
        hazards = " ".join(context.get("hazards", []))
        permits = " ".join(context.get("active_permits", []))
        rules = " ".join(risk.explanation.get("contributing_rules", [])) if isinstance(risk.explanation, dict) else ""
        base = f"{risk.risk_level} {risk.plant_id} {risk.zone_id} {rules} {hazards} {permits}"
        if section == "incident":
            return f"incident near miss root cause mitigation {base}"
        if section == "regulation":
            return f"regulation SOP permit procedure compliance {base}"
        if section == "history":
            return f"historical incident recurrence pattern {base}"
        if section == "recommendation":
            return f"preventive action recommendation inspection training maintenance {base}"
        return base

    def _source_type_for_section(self, section: str) -> str | None:
        return {
            "incident": "INCIDENT_REPORT",
            "regulation": "REGULATION",
            "history": "INCIDENT_REPORT",
            "recommendation": None,
        }.get(section)

    def _collect_citations(self, sections: list[list[RetrievalHit]]) -> list[dict[str, Any]]:
        citations: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for hits in sections:
            for hit in hits:
                key = (hit.document_id, hit.chunk_id)
                if key in seen:
                    continue
                seen.add(key)
                citations.append(hit.citation.to_dict())
        citations.sort(key=lambda item: item["score"], reverse=True)
        return citations

    def _confidence(self, sections: list[list[RetrievalHit]]) -> float:
        scores = [hit.score for hits in sections for hit in hits]
        if not scores:
            return 0.0
        return round(min(0.99, sum(scores) / len(scores)), 3)

    def _compose_recommendations(self, topics: list[Any], recommendation_hits: list[RetrievalHit]) -> list[dict[str, Any]]:
        recommendations = self.recommendation_agent.prioritize(topics, recommendation_hits)
        return recommendations

    def _root_causes(self, risk: RiskAssessment, hits: list[RetrievalHit]) -> list[dict[str, Any]]:
        causes: list[dict[str, Any]] = []
        for hit in hits[:5]:
            causes.append(
                {
                    "cause": hit.title,
                    "summary": hit.citation.snippet,
                    "confidence": round(hit.score, 3),
                    "source": hit.citation.to_dict(),
                }
            )
        if not causes:
            causes.append(
                {
                    "cause": "compound-operational-exposure",
                    "summary": risk.explanation.get("why", "Compound industrial exposure detected."),
                    "confidence": round(risk.confidence, 3),
                    "source": None,
                }
            )
        return causes
