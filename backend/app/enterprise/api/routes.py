from fastapi import APIRouter
from typing import Dict, Any, List, Optional
from app.enterprise.models import DecisionBrief
from app.enterprise.decision.decision import DecisionSupportAgent
from app.enterprise.search.search import EnterpriseSearchService, EnterpriseSearchQuery, SearchResult

router = APIRouter(prefix="/enterprise", tags=["enterprise"])
decision_agent = DecisionSupportAgent()
search_service = EnterpriseSearchService()

@router.get("/decisions/brief", response_model=DecisionBrief)
async def get_decision_brief(context_id: str, incident_id: Optional[str] = None) -> DecisionBrief:
    return await decision_agent.generate_brief(context_id, incident_id)

@router.post("/search", response_model=List[SearchResult])
async def search_enterprise(query: EnterpriseSearchQuery) -> List[SearchResult]:
    return await search_service.unified_search(query)
