from fastapi import APIRouter
from typing import Any, Dict, List
from app.vision.models import Frame
from app.vision.services.services import VisionIntelligenceService

router = APIRouter(prefix="/vision", tags=["vision"])
vision_service = VisionIntelligenceService()

@router.post("/detections", response_model=Dict[str, Any])
async def process_detections(frame: Frame) -> Dict[str, Any]:
    events = await vision_service.process_frame(frame)
    return {"status": "success", "events_emitted": len(events), "events": events}

@router.get("/tracks", response_model=Dict[str, Any])
async def get_tracks() -> Dict[str, Any]:
    return {"tracks": vision_service.repository.tracks}

@router.get("/cameras", response_model=Dict[str, Any])
async def get_cameras() -> Dict[str, Any]:
    return {"cameras": []} # In a real implementation, query from DB/Graph
