from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.time import utcnow

@dataclass
class EmergencyResource:
    resource_id: str
    resource_type: str
    location: str
    status: str = "AVAILABLE"

@dataclass
class EmergencyIncident:
    incident_id: UUID = field(default_factory=uuid4)
    risk_id: Optional[UUID] = None
    plant_id: str = "unknown"
    zone_id: str = "unknown"
    status: str = "DETECTED" # DETECTED, VALIDATED, DECLARED, RESPONSE_STARTED, EVACUATION, CONTAINMENT, RECOVERY, RESOLVED, ARCHIVED
    severity: str = "HIGH"
    detected_at: datetime = field(default_factory=utcnow)
    resolved_at: Optional[datetime] = None
    playbook_id: Optional[str] = None
    timeline: List[Dict[str, Any]] = field(default_factory=list)
