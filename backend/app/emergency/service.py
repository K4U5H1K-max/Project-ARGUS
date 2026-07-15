from typing import Any, Dict, List
from uuid import UUID

from app.core.time import utcnow
from app.emergency.agents import EmergencyResponseAgent, IncidentManagerAgent, ResourceAllocationAgent
from app.emergency.models import EmergencyIncident, EmergencyResource
from app.geo.service import GeoIntelligenceService

class EmergencyService:
    def __init__(self, geo_service: GeoIntelligenceService | None = None) -> None:
        self.geo_service = geo_service
        self.incident_manager = IncidentManagerAgent()
        self.response_agent = EmergencyResponseAgent()
        self.resource_agent = ResourceAllocationAgent()
        self.incidents: Dict[UUID, EmergencyIncident] = {}
        self.resources: List[EmergencyResource] = [
            EmergencyResource("RES-01", "Fire Team", "Zone-A"),
            EmergencyResource("RES-02", "Medical Team", "Zone-B"),
            EmergencyResource("RES-03", "Hazmat Team", "Zone-C"),
        ]

    def create_incident(self, risk_id: UUID, plant_id: str, zone_id: str, severity: str, hazards: List[str]) -> EmergencyIncident:
        incident = EmergencyIncident(risk_id=risk_id, plant_id=plant_id, zone_id=zone_id, severity=severity)
        playbook = self.response_agent.select_playbook(hazards)
        if playbook:
            incident.playbook_id = playbook.playbook_id
        
        self.incidents[incident.incident_id] = incident
        return incident

    def transition_status(self, incident_id: UUID) -> EmergencyIncident | None:
        incident = self.incidents.get(incident_id)
        if not incident:
            return None
        
        new_status = self.incident_manager.evaluate_status_transition(incident.status, incident.timeline)
        if new_status != incident.status:
            incident.status = new_status
            incident.timeline.append({"status": new_status, "timestamp": utcnow().isoformat()})
            if new_status == "RESOLVED":
                incident.resolved_at = utcnow()
                
        return incident

    def allocate_resources(self, incident_id: UUID) -> List[EmergencyResource]:
        incident = self.incidents.get(incident_id)
        if not incident:
            return []
        
        allocated = self.resource_agent.allocate(incident, self.resources)
        incident.timeline.append({"action": "allocated_resources", "resources": [r.resource_id for r in allocated], "timestamp": utcnow().isoformat()})
        return allocated
