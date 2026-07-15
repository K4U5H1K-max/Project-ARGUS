from typing import Any, Dict, List

from app.notifications.models import NotificationEvent


class NotificationCoordinator:
    def route_notification(self, event_type: str, priority: str, payload: Dict[str, Any]) -> List[str]:
        if priority == "CRITICAL":
            return ["DASHBOARD", "WEBSOCKETS", "SMS", "KAFKA"]
        elif priority == "HIGH":
            return ["DASHBOARD", "WEBSOCKETS", "EMAIL", "KAFKA"]
        return ["DASHBOARD", "WEBSOCKETS", "KAFKA"]
