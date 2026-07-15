from fastapi import APIRouter, Depends
from typing import Any, Dict, List
from uuid import UUID

from app.emergency.service import EmergencyService
from app.api.deps import get_db

router = APIRouter(prefix="/emergency", tags=["emergency"])
emergency_service = EmergencyService()

@router.post("/incidents", response_model=Dict[str, Any])
async def create_incident(risk_id: UUID, plant_id: str, zone_id: str, severity: str, hazards: List[str]) -> Dict[str, Any]:
    incident = emergency_service.create_incident(risk_id, plant_id, zone_id, severity, hazards)
    return {"incident": incident.__dict__}

@router.post("/incidents/{incident_id}/transition", response_model=Dict[str, Any])
async def transition_incident(incident_id: UUID) -> Dict[str, Any]:
    incident = emergency_service.transition_status(incident_id)
    return {"incident": incident.__dict__ if incident else None}

@router.post("/incidents/{incident_id}/allocate", response_model=Dict[str, Any])
async def allocate_resources(incident_id: UUID) -> Dict[str, Any]:
    resources = emergency_service.allocate_resources(incident_id)
    return {"allocated_resources": [r.__dict__ for r in resources]}
