from typing import Dict, Any, List
from app.vision.models import Detection
from app.core.enums import EventType

class EventTranslator:
    def translate(self, fused_scene: Dict[str, Any]) -> List[Dict[str, Any]]:
        events = []
        camera_id = fused_scene.get("camera_id")
        zone_id = fused_scene.get("zone_id", "UNKNOWN")
        
        for hazard in fused_scene.get("hazards", []):
            if hazard.label == "Smoke":
                event_type = EventType.SMOKE_DETECTED
            elif hazard.label == "Fire":
                event_type = EventType.FIRE_DETECTED
            elif hazard.label == "Gas Cloud":
                event_type = EventType.GAS_CLOUD_DETECTED
            else:
                continue
                
            events.append({
                "source": f"vision-camera-{camera_id}",
                "event_type": event_type,
                "plant_id": "UNKNOWN",
                "zone_id": zone_id,
                "severity": "CRITICAL",
                "payload": {
                    "camera_id": camera_id,
                    "confidence": hazard.confidence,
                    "label": hazard.label,
                    "bounding_box": hazard.bounding_box.__dict__ if hazard.bounding_box else None
                }
            })
            
        for entity in fused_scene.get("entities", []):
            if entity.label == "Worker":
                event_type = EventType.WORKER_DETECTED
                events.append({
                    "source": f"vision-camera-{camera_id}",
                    "event_type": event_type,
                    "plant_id": "UNKNOWN",
                    "zone_id": zone_id,
                    "severity": "INFO",
                    "payload": {
                        "camera_id": camera_id,
                        "confidence": entity.confidence,
                        "label": entity.label,
                        "track_id": entity.track_id,
                        "attributes": entity.attributes
                    }
                })
                # Check for PPE violations
                if entity.attributes.get("helmet") == False:
                    events.append({
                        "source": f"vision-camera-{camera_id}",
                        "event_type": EventType.PPE_VIOLATION,
                        "plant_id": "UNKNOWN",
                        "zone_id": zone_id,
                        "severity": "WARNING",
                        "payload": {
                            "camera_id": camera_id,
                            "confidence": entity.confidence,
                            "label": "Missing Helmet",
                            "track_id": entity.track_id
                        }
                    })
        return events
