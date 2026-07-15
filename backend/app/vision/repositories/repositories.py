from typing import Dict, Any, List
from uuid import UUID

class VisionRepository:
    def __init__(self) -> None:
        self.tracks: Dict[str, List[Dict[str, Any]]] = {}
        self.incidents: Dict[UUID, Dict[str, Any]] = {}

    def save_track(self, track_id: str, detection: Dict[str, Any]) -> None:
        if track_id not in self.tracks:
            self.tracks[track_id] = []
        self.tracks[track_id].append(detection)

    def save_incident(self, incident_id: UUID, incident: Dict[str, Any]) -> None:
        self.incidents[incident_id] = incident
