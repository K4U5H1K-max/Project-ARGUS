from fastapi import APIRouter
from typing import Any, Dict, List
from uuid import UUID

from app.permit.service import PermitIntelligenceService

router = APIRouter(prefix="/permit", tags=["permit"])
permit_service = PermitIntelligenceService()

@router.post("/scan", response_model=Dict[str, Any])
async def scan_permits(zone_id: str, active_permits: List[Dict[str, Any]]) -> Dict[str, Any]:
    conflicts = await permit_service.scan_zone_permits(zone_id, active_permits)
    return {"conflicts": [c.__dict__ for c in conflicts]}

@router.post("/resolve/{conflict_id}", response_model=Dict[str, Any])
async def resolve_conflict(conflict_id: UUID) -> Dict[str, Any]:
    conflict = permit_service.resolve_conflict(conflict_id)
    return {"conflict": conflict.__dict__ if conflict else None}
