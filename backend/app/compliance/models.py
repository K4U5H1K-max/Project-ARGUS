from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from app.core.time import utcnow

@dataclass
class ComplianceViolation:
    violation_id: UUID = field(default_factory=uuid4)
    regulation: str = "OISD"
    description: str = ""
    severity: str = "HIGH"
    detected_at: datetime = field(default_factory=utcnow)
    resolved_at: Optional[datetime] = None
    plant_id: str = "unknown"
    zone_id: str = "unknown"
