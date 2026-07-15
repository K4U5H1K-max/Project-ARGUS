from __future__ import annotations

from app.core.enums import EventType
from app.digital_twin.processors.base import TwinProcessor
from app.digital_twin.processors.incident import IncidentEventProcessor
from app.digital_twin.processors.maintenance import MaintenanceEventProcessor
from app.digital_twin.processors.permit import PermitEventProcessor
from app.digital_twin.processors.sensor import SensorEventProcessor
from app.digital_twin.processors.worker import WorkerEventProcessor


class ProcessorRegistry:
    def __init__(self) -> None:
        self._processors: list[TwinProcessor] = [
            SensorEventProcessor(),
            WorkerEventProcessor(),
            PermitEventProcessor(),
            MaintenanceEventProcessor(),
            IncidentEventProcessor(),
        ]

    def resolve(self, event_type: EventType) -> TwinProcessor:
        for processor in self._processors:
            if event_type in processor.supports:
                return processor
        raise ValueError(f"No processor registered for event_type={event_type}")
