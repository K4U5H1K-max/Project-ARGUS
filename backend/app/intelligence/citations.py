from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Citation:
    document_id: UUID
    chunk_id: UUID
    title: str
    source_type: str
    uri: str | None
    snippet: str
    score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "document_id": str(self.document_id),
            "chunk_id": str(self.chunk_id),
            "title": self.title,
            "source_type": self.source_type,
            "uri": self.uri,
            "snippet": self.snippet,
            "score": self.score,
            "metadata": self.metadata,
        }
