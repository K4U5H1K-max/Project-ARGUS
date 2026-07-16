import pytest
from app.enterprise.models import Organization, Plant, DecisionBrief
from app.enterprise.search.search import EnterpriseSearchService, EnterpriseSearchQuery
from app.analytics.dashboards.dashboards import DashboardService
from app.enterprise.decision.decision import DecisionSupportAgent

@pytest.mark.asyncio
async def test_enterprise_hierarchy():
    org = Organization(org_id="org-1", name="Global Steel Corp")
    plant = Plant(plant_id="plant-1", region_id="reg-1", name="Northern Refinery")
    
    assert org.org_id == "org-1"
    assert plant.region_id == "reg-1"

@pytest.mark.asyncio
async def test_enterprise_search():
    search_service = EnterpriseSearchService()
    query = EnterpriseSearchQuery(query="fire")
    results = await search_service.unified_search(query)
    
    assert len(results) > 0
    assert results[0].type == "incident"
    assert "Fire" in results[0].title

@pytest.mark.asyncio
async def test_decision_support_brief():
    agent = DecisionSupportAgent()
    brief = await agent.generate_brief(context_id="ctx-999")
    
    assert isinstance(brief, DecisionBrief)
    assert brief.risk_level == "CRITICAL"
    assert len(brief.recommendations) > 0
    assert brief.recommendations[0].priority == "CRITICAL"
    assert "Risk Assessment" in brief.evidence_graph

@pytest.mark.asyncio
async def test_executive_dashboard():
    dashboard_service = DashboardService()
    dashboard = await dashboard_service.get_executive_dashboard()
    
    assert dashboard.current_critical_risks == 2
    assert "estimated_downtime_cost" in dashboard.business_metrics
