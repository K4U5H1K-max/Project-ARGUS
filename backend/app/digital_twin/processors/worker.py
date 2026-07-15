from __future__ import annotations

from typing import Any

from app.core.enums import EventType
from app.digital_twin.processors.base import TwinProcessor


class WorkerEventProcessor(TwinProcessor):
    supports = {EventType.ENTRY, EventType.EXIT, EventType.PPE_VIOLATION}

    async def process(self, *, event: Any, state_manager: Any, session: Any) -> dict[str, Any]:
        return await state_manager.update_worker_state(event, session)
