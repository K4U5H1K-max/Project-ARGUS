from __future__ import annotations

from typing import Any

from app.core.enums import EventType
from app.digital_twin.processors.base import TwinProcessor


class SensorEventProcessor(TwinProcessor):
    supports = {
        EventType.GAS_SENSOR,
        EventType.TEMPERATURE_SENSOR,
        EventType.PRESSURE_SENSOR,
        EventType.VIBRATION_SENSOR,
    }

    async def process(self, *, event: Any, state_manager: Any, session: Any) -> dict[str, Any]:
        return await state_manager.update_sensor_state(event, session)
