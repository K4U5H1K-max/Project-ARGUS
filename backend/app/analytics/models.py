from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class KPISnapshot(BaseModel):
    snapshot_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    period: str # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
    entity_id: str # Plant ID, Region ID, Org ID
    entity_type: str
    safety_kpis: Dict[str, float] = Field(default_factory=dict)
    operational_kpis: Dict[str, float] = Field(default_factory=dict)
    risk_kpis: Dict[str, float] = Field(default_factory=dict)
    predictive_kpis: Dict[str, float] = Field(default_factory=dict)
    enterprise_metrics: Dict[str, float] = Field(default_factory=dict)

# Frontend DTOs
class ExecutiveDashboardDTO(BaseModel):
    current_critical_risks: int
    top_hazard_zones: List[Dict[str, Any]]
    live_plant_status: Dict[str, str]
    emergency_timeline: List[Dict[str, Any]]
    worker_distribution: Dict[str, int]
    active_permits: int
    equipment_health_summary: Dict[str, float]
    forecast_panel: Dict[str, Any]
    compliance_score: float
    heatmap_metadata: Dict[str, Any]
    business_metrics: Dict[str, float] # Incident cost, downtime, etc.

class IncidentDashboardDTO(BaseModel):
    incident_id: str
    severity: str
    timeline: List[Dict[str, Any]]
    affected_assets: List[str]
    root_cause_analysis: str
    response_metrics: Dict[str, float]

class PlantOverviewDTO(BaseModel):
    plant_id: str
    overall_health: float
    zone_risk_ranking: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]

class DecisionPanelDTO(BaseModel):
    active_decisions: List[Dict[str, Any]]
    historical_decisions: List[Dict[str, Any]]

class RiskTimelineDTO(BaseModel):
    historical_trend: List[Dict[str, Any]]
    future_projection: List[Dict[str, Any]]
