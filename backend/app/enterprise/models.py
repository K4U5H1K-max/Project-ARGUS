from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import UUID, uuid4

class Organization(BaseModel):
    org_id: str
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Region(BaseModel):
    region_id: str
    org_id: str
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class BusinessUnit(BaseModel):
    bu_id: str
    org_id: str
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Plant(BaseModel):
    plant_id: str
    region_id: str
    bu_id: Optional[str] = None
    name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutiveTimelineEvent(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime
    event_type: str
    title: str
    description: str
    source_system: str
    related_entities: List[str] = Field(default_factory=list)

class Recommendation(BaseModel):
    recommendation_id: UUID = Field(default_factory=uuid4)
    action: str
    confidence: float
    supporting_evidence: List[str] = Field(default_factory=list)
    conflicting_evidence: List[str] = Field(default_factory=list)
    priority: str
    urgency: str
    impact: str
    estimated_benefit: str

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class DecisionBrief(BaseModel):
    brief_id: UUID = Field(default_factory=uuid4)
    version: int = 1
    timestamp: datetime = Field(default_factory=utcnow)
    situation_summary: str
    risk_level: str
    affected_assets: List[str] = Field(default_factory=list)
    affected_workers: List[str] = Field(default_factory=list)
    predicted_evolution: str
    recommendations: List[Recommendation] = Field(default_factory=list)
    alternative_strategies: List[str] = Field(default_factory=list)
    trade_offs: str
    confidence: float
    document_citations: List[str] = Field(default_factory=list)
    evidence_graph: Dict[str, Any] = Field(default_factory=dict) # Keys: Risk Assessment, Context Snapshot, etc.
    feedback_status: str = "PENDING" # PENDING, ACCEPTED, REJECTED, MODIFIED, IGNORED
