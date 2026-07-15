from typing import Any, Dict, List
from app.emergency.models import EmergencyIncident, EmergencyResource
from app.emergency.playbooks import DEFAULT_PLAYBOOKS, EmergencyPlaybook

class IncidentManagerAgent:
    def evaluate_status_transition(self, current_status: str, events: List[Dict[str, Any]]) -> str:
        # Simple deterministic transition logic
        transitions = {
            "DETECTED": "VALIDATED",
            "VALIDATED": "DECLARED",
            "DECLARED": "RESPONSE_STARTED",
            "RESPONSE_STARTED": "EVACUATION",
            "EVACUATION": "CONTAINMENT",
            "CONTAINMENT": "RECOVERY",
            "RECOVERY": "RESOLVED",
            "RESOLVED": "ARCHIVED",
            "ARCHIVED": "ARCHIVED"
        }
        return transitions.get(current_status, current_status)

class EmergencyResponseAgent:
    def select_playbook(self, hazards: List[str]) -> EmergencyPlaybook | None:
        for playbook in DEFAULT_PLAYBOOKS:
            if any(playbook.scenario.lower() in hazard.lower() for hazard in hazards):
                return playbook
        return DEFAULT_PLAYBOOKS[0] if DEFAULT_PLAYBOOKS else None

class ResourceAllocationAgent:
    def allocate(self, incident: EmergencyIncident, available_resources: List[EmergencyResource]) -> List[EmergencyResource]:
        allocated = []
        for resource in available_resources:
            if resource.status == "AVAILABLE":
                resource.status = "DISPATCHED"
                allocated.append(resource)
                if len(allocated) >= 2: # Limit to 2 per incident for testing
                    break
        return allocated
