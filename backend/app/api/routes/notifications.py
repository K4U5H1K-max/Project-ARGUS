from fastapi import APIRouter
from typing import Any, Dict
from uuid import UUID

from app.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()

@router.post("/dispatch", response_model=Dict[str, Any])
async def dispatch_notification(event_type: str, priority: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    event = notification_service.dispatch(event_type, priority, payload)
    return {"notification": event.__dict__}

@router.post("/{notification_id}/acknowledge", response_model=Dict[str, Any])
async def acknowledge(notification_id: UUID, user_id: str) -> Dict[str, Any]:
    event = notification_service.acknowledge(notification_id, user_id)
    return {"notification": event.__dict__ if event else None}
