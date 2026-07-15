from dataclasses import dataclass
from typing import List

@dataclass
class EmergencyPlaybook:
    playbook_id: str
    name: str
    scenario: str
    response_sequence: List[str]
    required_ppe: List[str]
    evacuation_required: bool

DEFAULT_PLAYBOOKS = [
    EmergencyPlaybook(
        playbook_id="PB-GAS-001",
        name="Gas Leak Response",
        scenario="Gas Leak",
        response_sequence=["Isolate valves", "Evacuate zone", "Deploy HAZMAT"],
        required_ppe=["Gas Mask", "Hazmat Suit"],
        evacuation_required=True,
    ),
    EmergencyPlaybook(
        playbook_id="PB-FIRE-001",
        name="Fire Response",
        scenario="Fire",
        response_sequence=["Trigger alarms", "Evacuate zone", "Deploy Fire Team"],
        required_ppe=["Fire Retardant Suit"],
        evacuation_required=True,
    )
]
