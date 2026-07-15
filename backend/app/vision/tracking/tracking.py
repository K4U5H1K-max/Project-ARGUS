from typing import Dict, List, Any
from app.vision.models import Detection
from uuid import uuid4

class ObjectTracker:
    def __init__(self) -> None:
        self.active_tracks: Dict[str, Dict[str, Any]] = {} # id -> track info

    def track(self, detections: List[Detection], camera_id: str) -> List[Detection]:
        # Simple IoU based tracking simulation
        for detection in detections:
            if not detection.track_id:
                # Assign new track id if not provided
                detection.track_id = f"TRK-{uuid4().hex[:8]}"
            self.active_tracks[detection.track_id] = {
                "label": detection.label,
                "camera_id": camera_id,
                "last_seen": detection.bounding_box
            }
        return detections
