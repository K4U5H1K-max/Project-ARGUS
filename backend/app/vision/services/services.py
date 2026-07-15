import logging
from typing import Dict, Any, List
from app.vision.models import Frame
from app.vision.detectors.detectors import YoloDetector
from app.vision.tracking.tracking import ObjectTracker
from app.vision.fusion.fusion import SceneFusion
from app.vision.events.events import EventTranslator
from app.vision.agents.agents import VisionIntelligenceAgent
from app.vision.repositories.repositories import VisionRepository

logger = logging.getLogger(__name__)

class VisionIntelligenceService:
    def __init__(self) -> None:
        self.detector = YoloDetector()
        self.tracker = ObjectTracker()
        self.fusion = SceneFusion()
        self.translator = EventTranslator()
        self.agent = VisionIntelligenceAgent()
        self.repository = VisionRepository()

    async def process_frame(self, frame: Frame) -> List[Dict[str, Any]]:
        # 1. Detection
        detections = self.detector.detect(frame)
        
        # 2. Tracking
        tracked_detections = self.tracker.track(detections, frame.camera_id)
        
        # 3. Fusion
        fused_scene = self.fusion.fuse(tracked_detections, frame.camera_id)
        
        # 4. Agent Enrichment
        enriched_scene = await self.agent.analyze_scene(fused_scene)
        
        # 5. Event Translation
        events = self.translator.translate(enriched_scene)
        
        for event in events:
            logger.info(f"Vision Event Emitted: {event['event_type']} from {event['source']}")
            
        return events
