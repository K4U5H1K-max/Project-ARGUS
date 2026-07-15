from __future__ import annotations

from typing import Any

from app.core.enums import EventType
from app.digital_twin.processors.base import TwinProcessor


class PermitEventProcessor(TwinProcessor):
    supports = {EventType.HOT_WORK, EventType.CONFINED_SPACE, EventType.ELECTRICAL, EventType.EXCAVATION}

    async def process(self, *, event: Any, state_manager: Any, session: Any) -> dict[str, Any]:
        return await state_manager.update_permit_state(event, session)
