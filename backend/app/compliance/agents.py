from typing import List, Dict, Any
from app.compliance.models import ComplianceViolation
from app.intelligence.services import IndustrialIntelligenceService

class ComplianceIntelligenceAgent:
    def __init__(self, intelligence_service: IndustrialIntelligenceService | None = None) -> None:
        self.intelligence_service = intelligence_service or IndustrialIntelligenceService()
        
    async def evaluate_compliance(self, context_snapshot: Dict[str, Any]) -> List[ComplianceViolation]:
        violations = []
        # Basic deterministic rule: If Hot Work is happening without a Fire Watch/Gas Mask in context
        permits = context_snapshot.get("active_permits", [])
        ppe = context_snapshot.get("workers", [{}])[0].get("ppe", []) if context_snapshot.get("workers") else []
        
        has_hot_work = any(p.get("type") == "HOT_WORK" for p in permits)
        if has_hot_work and "Gas Mask" not in ppe:
            violations.append(ComplianceViolation(
                regulation="OISD Safety Guidance for Hot Work",
                description="Hot work proceeding without required Gas Mask PPE.",
                plant_id=context_snapshot.get("zone", {}).get("plant_id", "unknown"),
                zone_id=context_snapshot.get("zone", {}).get("zone_id", "unknown")
            ))
        return violations
