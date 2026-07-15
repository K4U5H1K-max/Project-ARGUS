from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import checksum
from app.core.uuid import generate_uuid
from app.intelligence.chunking import ChunkingService
from app.intelligence.embeddings import EmbeddingService
from app.intelligence.models import IntelligenceChunk, IntelligenceDocument


@dataclass(frozen=True, slots=True)
class DocumentPayload:
    title: str
    source_type: str
    content: str
    uri: str | None = None
    language: str = "en"
    metadata: dict[str, Any] | None = None


class IntelligenceRepository:
    def __init__(self, chunking_service: ChunkingService | None = None, embedding_service: EmbeddingService | None = None) -> None:
        self.chunking_service = chunking_service or ChunkingService()
        self.embedding_service = embedding_service or EmbeddingService()

    async def upsert_document(self, session: AsyncSession, payload: DocumentPayload) -> IntelligenceDocument:
        document_checksum = checksum({"title": payload.title, "source_type": payload.source_type, "content": payload.content, "uri": payload.uri, "language": payload.language})
        existing = await self.get_document_by_checksum(session, document_checksum)
        if existing is not None:
            await self.replace_chunks(session, existing.document_id, payload.content, payload)
            return existing

        document = IntelligenceDocument(
            document_id=generate_uuid(),
            source_type=payload.source_type,
            title=payload.title,
            uri=payload.uri,
            language=payload.language,
            checksum=document_checksum,
            metadata=payload.metadata or {},
        )
        session.add(document)
        await session.flush()
        await self.replace_chunks(session, document.document_id, payload.content, payload)
        return document

    async def replace_chunks(self, session: AsyncSession, document_id: UUID, content: str, payload: DocumentPayload) -> list[IntelligenceChunk]:
        await session.execute(delete(IntelligenceChunk).where(IntelligenceChunk.document_id == document_id))
        created: list[IntelligenceChunk] = []
        for chunk in self.chunking_service.chunk(content, metadata=payload.metadata or {}):
            record = IntelligenceChunk(
                chunk_id=generate_uuid(),
                document_id=document_id,
                chunk_index=chunk.index,
                content=chunk.content,
                token_count=len(chunk.content.split()),
                embedding=self.embedding_service.embed(chunk.content),
                metadata=chunk.metadata,
                source_type=payload.source_type,
                title=payload.title,
                uri=payload.uri,
            )
            session.add(record)
            created.append(record)
        await session.flush()
        return created

    async def get_document_by_checksum(self, session: AsyncSession, document_checksum: str) -> IntelligenceDocument | None:
        result = await session.execute(select(IntelligenceDocument).where(IntelligenceDocument.checksum == document_checksum))
        return result.scalars().first()

    async def list_documents(self, session: AsyncSession) -> list[IntelligenceDocument]:
        result = await session.execute(select(IntelligenceDocument).order_by(IntelligenceDocument.created_at.desc()))
        return list(result.scalars().all())

    async def list_chunks(self, session: AsyncSession) -> list[dict[str, Any]]:
        result = await session.execute(select(IntelligenceChunk).order_by(IntelligenceChunk.chunk_index.asc()))
        chunks = list(result.scalars().all())
        return [self._serialize_chunk(chunk) for chunk in chunks]

    async def get_chunks_for_document(self, session: AsyncSession, document_id: UUID) -> list[dict[str, Any]]:
        result = await session.execute(select(IntelligenceChunk).where(IntelligenceChunk.document_id == document_id).order_by(IntelligenceChunk.chunk_index.asc()))
        return [self._serialize_chunk(chunk) for chunk in result.scalars().all()]

    def _serialize_chunk(self, chunk: IntelligenceChunk) -> dict[str, Any]:
        return {
            "document_id": chunk.document_id,
            "chunk_id": chunk.chunk_id,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "token_count": chunk.token_count,
            "embedding": chunk.embedding,
            "metadata": chunk.metadata,
            "source_type": chunk.source_type,
            "title": chunk.title,
            "uri": chunk.uri,
        }
