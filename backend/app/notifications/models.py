from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from app.core.time import utcnow


@dataclass
class NotificationEvent:
    notification_id: UUID = field(default_factory=uuid4)
    topic: str = "general"
    priority: str = "LOW"
    channels: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "PENDING"
    created_at: datetime = field(default_factory=utcnow)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
