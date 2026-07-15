from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.time import utcnow

@dataclass
class PermitConflict:
    conflict_id: UUID = field(default_factory=uuid4)
    permit_1_id: str = ""
    permit_2_id: str = ""
    zone_id: str = ""
    conflict_type: str = "SIMULTANEOUS_OPERATIONS" # or ISOLATION_MISSING, UNAUTHORIZED
    severity: str = "CRITICAL"
    detected_at: datetime = field(default_factory=utcnow)
    resolved_at: Optional[datetime] = None
    description: str = ""
