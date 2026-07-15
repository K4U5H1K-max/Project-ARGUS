from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.intelligence.citations import Citation
from app.intelligence.embeddings import EmbeddingService


@dataclass(frozen=True, slots=True)
class RetrievalHit:
    document_id: str
    chunk_id: str
    title: str
    source_type: str
    uri: str | None
    content: str
    score: float
    metadata: dict[str, Any]
    citation: Citation


class RetrievalService:
    def __init__(self, embedding_service: EmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or EmbeddingService()

    def rank(self, *, query: str, chunks: list[dict[str, Any]], filters: dict[str, Any] | None = None, limit: int = 10) -> list[RetrievalHit]:
        query_embedding = self.embedding_service.embed(query)
        hits: list[RetrievalHit] = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            if filters and not self._matches_filters(metadata, filters):
                continue
            chunk_embedding = chunk.get("embedding", {})
            semantic_score = self.embedding_service.similarity(query_embedding, chunk_embedding)
            keyword_score = self.embedding_service.keyword_overlap(chunk.get("content", ""), query)
            metadata_score = self.embedding_service.metadata_score(metadata, filters)
            score = round((semantic_score * 0.65) + (keyword_score * 0.25) + (metadata_score * 0.1), 6)
            citation = Citation(
                document_id=chunk["document_id"],
                chunk_id=chunk["chunk_id"],
                title=chunk["title"],
                source_type=chunk["source_type"],
                uri=chunk.get("uri"),
                snippet=self._snippet(chunk.get("content", ""), query),
                score=score,
                metadata=metadata,
            )
            hits.append(
                RetrievalHit(
                    document_id=str(chunk["document_id"]),
                    chunk_id=str(chunk["chunk_id"]),
                    title=chunk["title"],
                    source_type=chunk["source_type"],
                    uri=chunk.get("uri"),
                    content=chunk.get("content", ""),
                    score=score,
                    metadata=metadata,
                    citation=citation,
                )
            )
        hits.sort(key=lambda item: (item.score, item.title, item.chunk_id), reverse=True)
        return hits[:limit]

    def _matches_filters(self, metadata: dict[str, Any], filters: dict[str, Any]) -> bool:
        for key, expected in filters.items():
            actual = metadata.get(key)
            if actual is None:
                return False
            if isinstance(expected, str) and isinstance(actual, str):
                if expected.lower() not in actual.lower():
                    return False
            elif actual != expected:
                return False
        return True

    def _snippet(self, content: str, query: str, window: int = 160) -> str:
        lowered = content.lower()
        needle = query.lower().split()[0] if query.split() else ""
        if needle and needle in lowered:
            index = lowered.index(needle)
            start = max(0, index - window // 2)
            end = min(len(content), index + window // 2)
            return content[start:end].strip()
        return content[:window].strip()
