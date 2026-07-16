from fastapi import APIRouter
from typing import Dict, Any, List
from app.analytics.models import ExecutiveDashboardDTO, KPISnapshot
from app.analytics.dashboards.dashboards import DashboardService
from app.analytics.historical.historical import HistoricalAnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])
dashboard_service = DashboardService()
historical_service = HistoricalAnalyticsService()

@router.get("/dashboard/executive", response_model=ExecutiveDashboardDTO)
async def get_executive_dashboard() -> ExecutiveDashboardDTO:
    return await dashboard_service.get_executive_dashboard()

@router.get("/historical/snapshots", response_model=List[KPISnapshot])
async def get_snapshots(entity_id: str, period: str) -> List[KPISnapshot]:
    return await historical_service.get_snapshots(entity_id, period)
