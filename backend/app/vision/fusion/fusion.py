from typing import List, Dict, Any
from app.vision.models import Detection
from app.graph.service import GraphQueryService

class SceneFusion:
    def __init__(self, graph_service: GraphQueryService | None = None) -> None:
        self.graph_service = graph_service

    def fuse(self, detections: List[Detection], camera_id: str) -> Dict[str, Any]:
        fused_scene = {
            "camera_id": camera_id,
            "entities": [],
            "hazards": [],
            "zone_id": "UNKNOWN"
        }
        
        # Link camera to zone via graph
        if self.graph_service:
            # simulated lookup
            pass
            
        for detection in detections:
            if detection.label in ["Smoke", "Fire", "Gas Cloud", "Spill"]:
                fused_scene["hazards"].append(detection)
            elif detection.label in ["Worker", "Vehicle"]:
                fused_scene["entities"].append(detection)
                
        return fused_scene
