import logging
from typing import Any, Dict, List
from uuid import UUID

from app.compliance.agents import ComplianceIntelligenceAgent
from app.compliance.models import ComplianceViolation
from app.core.time import utcnow

logger = logging.getLogger(__name__)

class ComplianceIntelligenceService:
    def __init__(self) -> None:
        self.agent = ComplianceIntelligenceAgent()
        self.violations: Dict[UUID, ComplianceViolation] = {}

    async def scan_context(self, context_snapshot: Dict[str, Any]) -> List[ComplianceViolation]:
        new_violations = await self.agent.evaluate_compliance(context_snapshot)
        for violation in new_violations:
            self.violations[violation.violation_id] = violation
            logger.warning(f"Compliance Violation Detected: {violation.description}")
        return new_violations
        
    def resolve_violation(self, violation_id: UUID) -> ComplianceViolation | None:
        violation = self.violations.get(violation_id)
        if violation:
            violation.resolved_at = utcnow()
        return violation
