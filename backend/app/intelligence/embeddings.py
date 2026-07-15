from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any


_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


class EmbeddingService:
    def embed(self, text: str) -> dict[str, float]:
        tokens = [token.lower() for token in _TOKEN_PATTERN.findall(text) if token.lower() not in _STOPWORDS]
        counts = Counter(tokens)
        norm = math.sqrt(sum(value * value for value in counts.values())) or 1.0
        return {token: round(count / norm, 6) for token, count in counts.items()}

    def similarity(self, left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(value * right.get(token, 0.0) for token, value in left.items())
        norm_left = math.sqrt(sum(value * value for value in left.values())) or 1.0
        norm_right = math.sqrt(sum(value * value for value in right.values())) or 1.0
        return round(dot / (norm_left * norm_right), 6)

    def keyword_overlap(self, text: str, query: str) -> float:
        text_tokens = set(self.embed(text).keys())
        query_tokens = set(self.embed(query).keys())
        if not query_tokens:
            return 0.0
        return round(len(text_tokens & query_tokens) / len(query_tokens), 6)

    def metadata_score(self, metadata: dict[str, Any], filters: dict[str, Any] | None = None) -> float:
        if not filters:
            return 0.0
        score = 0.0
        for key, expected in filters.items():
            actual = metadata.get(key)
            if actual is None:
                continue
            if isinstance(expected, str) and isinstance(actual, str) and expected.lower() in actual.lower():
                score += 1.0
            elif actual == expected:
                score += 1.0
        return round(score / max(len(filters), 1), 6)
