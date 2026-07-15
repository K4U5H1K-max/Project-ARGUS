from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.core.enums import EventType


class TwinProcessor(ABC):
    supports: set[EventType]

    @abstractmethod
    async def process(self, *, event: Any, state_manager: Any, session: Any) -> dict[str, Any]:
        raise NotImplementedError
