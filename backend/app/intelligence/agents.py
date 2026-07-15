from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.intelligence.knowledge import KnowledgeTopic
from app.intelligence.retrieval import RetrievalHit


@dataclass(slots=True)
class AgentResult:
    agent: str
    summary: str
    items: list[dict[str, Any]]
    confidence: float


class IncidentIntelligenceAgent:
    def summarize(self, hits: list[RetrievalHit]) -> AgentResult:
        items = [self._serialize_hit(hit) for hit in hits]
        confidence = round(sum(hit.score for hit in hits) / max(len(hits), 1), 3) if hits else 0.0
        summary = "Historical incidents and near misses with similar operational patterns."
        return AgentResult(agent="incident-intelligence", summary=summary, items=items, confidence=confidence)

    def _serialize_hit(self, hit: RetrievalHit) -> dict[str, Any]:
        return {
            "document_id": hit.document_id,
            "chunk_id": hit.chunk_id,
            "title": hit.title,
            "source_type": hit.source_type,
            "uri": hit.uri,
            "content": hit.content,
            "score": hit.score,
            "metadata": hit.metadata,
            "citation": hit.citation.to_dict(),
        }


class RegulationAgent:
    def summarize(self, hits: list[RetrievalHit]) -> AgentResult:
        items = [self._serialize_hit(hit) for hit in hits]
        confidence = round(sum(hit.score for hit in hits) / max(len(hits), 1), 3) if hits else 0.0
        summary = "Applicable standards and internal procedures that match the risk profile."
        return AgentResult(agent="regulation-agent", summary=summary, items=items, confidence=confidence)

    def _serialize_hit(self, hit: RetrievalHit) -> dict[str, Any]:
        return {
            "document_id": hit.document_id,
            "chunk_id": hit.chunk_id,
            "title": hit.title,
            "source_type": hit.source_type,
            "uri": hit.uri,
            "content": hit.content,
            "score": hit.score,
            "metadata": hit.metadata,
            "citation": hit.citation.to_dict(),
        }


class HistoricalAnalysisAgent:
    def summarize(self, hits: list[RetrievalHit]) -> AgentResult:
        items = [self._serialize_hit(hit) for hit in hits]
        confidence = round(sum(hit.score for hit in hits) / max(len(hits), 1), 3) if hits else 0.0
        summary = "Recurring failure modes, root causes, and preventive patterns from prior incidents."
        return AgentResult(agent="historical-analysis-agent", summary=summary, items=items, confidence=confidence)

    def _serialize_hit(self, hit: RetrievalHit) -> dict[str, Any]:
        return {
            "document_id": hit.document_id,
            "chunk_id": hit.chunk_id,
            "title": hit.title,
            "source_type": hit.source_type,
            "uri": hit.uri,
            "content": hit.content,
            "score": hit.score,
            "metadata": hit.metadata,
            "citation": hit.citation.to_dict(),
        }


class RecommendationAgent:
    def prioritize(self, topics: list[KnowledgeTopic], hits: list[RetrievalHit]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        for topic in topics:
            top_hit = self._best_hit_for_topic(topic, hits)
            recommendations.append(
                {
                    "topic": topic.topic,
                    "recommendation": self._recommendation_text(topic.topic),
                    "rationale": topic.rationale,
                    "source": top_hit.citation.to_dict() if top_hit is not None else None,
                    "confidence": round(min(0.99, topic.weight * (top_hit.score if top_hit is not None else 0.5)), 3),
                }
            )
        return recommendations

    def _best_hit_for_topic(self, topic: KnowledgeTopic, hits: list[RetrievalHit]) -> RetrievalHit | None:
        if not hits:
            return None
        ranked = sorted(hits, key=lambda hit: hit.score, reverse=True)
        return ranked[0]

    def _recommendation_text(self, topic: str) -> str:
        mapping = {
            "safety-procedures": "Verify the applicable SOP and update the work permit before continuing.",
            "regulations": "Review the applicable regulations and document compliance checks.",
            "incident-patterns": "Compare against prior incidents and adopt the previously successful control set.",
            "gas-exposure": "Increase gas monitoring, ventilate the area, and verify respiratory protection.",
            "permit-control": "Suspend conflicting permits and revalidate the isolation boundary.",
            "worker-safety": "Confirm PPE, assembly points, and supervisor communication are in place.",
        }
        return mapping.get(topic, "Apply the highest-confidence evidence-backed mitigation.")
