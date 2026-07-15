import logging
from typing import Any, Dict, List
from uuid import UUID

from app.graph.service import GraphQueryService
from app.permit.agents import PermitIntelligenceAgent
from app.permit.models import PermitConflict
from app.core.time import utcnow

logger = logging.getLogger(__name__)

class PermitIntelligenceService:
    def __init__(self, graph_service: GraphQueryService | None = None) -> None:
        self.graph_service = graph_service
        self.agent = PermitIntelligenceAgent()
        self.conflicts: Dict[UUID, PermitConflict] = {}

    async def scan_zone_permits(self, zone_id: str, active_permits: List[Dict[str, Any]]) -> List[PermitConflict]:
        # Using the agent to deterministically evaluate RAG / Knowledge conflicts
        new_conflicts = await self.agent.evaluate_conflicts(active_permits, zone_id)
        
        # Simulating Graph overlap logic if graph_service was available
        if self.graph_service:
            pass # Would call self.graph_service.permit_overlap()
            
        for conflict in new_conflicts:
            self.conflicts[conflict.conflict_id] = conflict
            logger.warning(f"Detected Permit Conflict: {conflict.description}")
            
        return new_conflicts
        
    def resolve_conflict(self, conflict_id: UUID) -> PermitConflict | None:
        conflict = self.conflicts.get(conflict_id)
        if conflict:
            conflict.resolved_at = utcnow()
        return conflict
