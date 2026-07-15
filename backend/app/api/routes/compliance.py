from fastapi import APIRouter
from typing import Any, Dict

from app.compliance.service import ComplianceIntelligenceService

router = APIRouter(prefix="/compliance", tags=["compliance"])
compliance_service = ComplianceIntelligenceService()

@router.post("/scan", response_model=Dict[str, Any])
async def scan_compliance(context_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    violations = await compliance_service.scan_context(context_snapshot)
    return {"violations": [v.__dict__ for v in violations]}
