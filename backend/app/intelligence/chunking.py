from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


_SENTENCE_BOUNDARY = re.compile(r"(?<=[.!?])\s+")


@dataclass(frozen=True)
class Chunk:
    index: int
    content: str
    metadata: dict[str, Any]


class ChunkingService:
    def __init__(self, *, max_chars: int = 1200, overlap_chars: int = 120) -> None:
        self.max_chars = max_chars
        self.overlap_chars = overlap_chars

    def chunk(self, text: str, *, metadata: dict[str, Any] | None = None) -> list[Chunk]:
        metadata = metadata or {}
        if not text.strip():
            return []
        sentences = _SENTENCE_BOUNDARY.split(text.strip())
        chunks: list[str] = []
        current = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            candidate = f"{current} {sentence}".strip() if current else sentence
            if len(candidate) <= self.max_chars:
                current = candidate
                continue
            if current:
                chunks.append(current)
            current = sentence
            if len(current) > self.max_chars:
                chunks.extend(self._hard_split(current))
                current = ""
        if current:
            chunks.append(current)

        resolved: list[Chunk] = []
        for index, content in enumerate(chunks):
            resolved.append(Chunk(index=index, content=content, metadata={**metadata, "chunk_index": index, "character_count": len(content)}))
        return resolved

    def _hard_split(self, text: str) -> list[str]:
        if len(text) <= self.max_chars:
            return [text]
        parts: list[str] = []
        start = 0
        while start < len(text):
            end = min(len(text), start + self.max_chars)
            parts.append(text[start:end].strip())
            start = max(end - self.overlap_chars, end)
        return [part for part in parts if part]
