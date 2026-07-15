from __future__ import annotations

from uuid import UUID, uuid4


def generate_uuid() -> UUID:
    try:
        from uuid import uuid7  # type: ignore[attr-defined]

        return uuid7()
    except Exception:
        return uuid4()
