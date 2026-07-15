from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Any, Dict, List, Optional
from app.core.enums import EventType, EventSeverity

@dataclass
class ForecastHorizon:
    minutes: int

@dataclass
class SimulatedEvent:
    event_type: EventType
    timestamp: datetime
    zone_id: str
    severity: EventSeverity
    payload: Dict[str, Any] = field(default_factory=dict)
    probability: float = 1.0

@dataclass
class Prediction:
    horizon: ForecastHorizon
    predicted_risk_level: str
    confidence: float
    prediction_id: UUID = field(default_factory=uuid4)
    simulated_events: List[SimulatedEvent] = field(default_factory=list)
    mitigation_suggestions: List[str] = field(default_factory=list)

@dataclass
class SimulationScenario:
    name: str
    description: str
    scenario_id: UUID = field(default_factory=uuid4)
    initial_events: List[SimulatedEvent] = field(default_factory=list)
    horizon: ForecastHorizon = field(default_factory=lambda: ForecastHorizon(60))
    metadata: Dict[str, Any] = field(default_factory=dict)
