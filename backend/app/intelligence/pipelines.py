from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.intelligence.repositories import DocumentPayload, IntelligenceRepository


@dataclass(frozen=True, slots=True)
class IngestionResult:
    title: str
    source_type: str
    document_id: str
    chunk_count: int
    metadata: dict[str, Any]


class DocumentPipeline:
    def __init__(self, repository: IntelligenceRepository) -> None:
        self.repository = repository

    async def ingest(self, session: AsyncSession, payload: DocumentPayload) -> IngestionResult:
        document = await self.repository.upsert_document(session, payload)
        chunks = await self.repository.get_chunks_for_document(session, document.document_id)
        return IngestionResult(title=document.title, source_type=document.source_type, document_id=str(document.document_id), chunk_count=len(chunks), metadata=document.metadata)
