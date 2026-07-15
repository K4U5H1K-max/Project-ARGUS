import logging
from typing import Any, Dict
from uuid import UUID

from app.core.time import utcnow
from app.notifications.agents import NotificationCoordinator
from app.notifications.models import NotificationEvent

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self) -> None:
        self.coordinator = NotificationCoordinator()
        self.events: Dict[UUID, NotificationEvent] = {}

    def dispatch(self, event_type: str, priority: str, payload: Dict[str, Any]) -> NotificationEvent:
        channels = self.coordinator.route_notification(event_type, priority, payload)
        event = NotificationEvent(topic=event_type, priority=priority, payload=payload, channels=channels)
        self.events[event.notification_id] = event
        
        for channel in channels:
            logger.info(f"Dispatching notification via {channel}: {event_type} - {payload}")
            
        event.status = "DISPATCHED"
        return event

    def acknowledge(self, notification_id: UUID, user_id: str) -> NotificationEvent | None:
        event = self.events.get(notification_id)
        if event:
            event.status = "ACKNOWLEDGED"
            event.acknowledged_by = user_id
            event.acknowledged_at = utcnow()
        return event
        
    def status(self, notification_id: UUID) -> str:
        event = self.events.get(notification_id)
        return event.status if event else "NOT_FOUND"
