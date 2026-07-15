import pytest
from datetime import datetime
from uuid import uuid4

from app.vision.models import Frame, Detection, BoundingBox
from app.vision.services.services import VisionIntelligenceService
from app.core.time import utcnow

@pytest.mark.asyncio
async def test_vision_pipeline_worker_ppe():
    service = VisionIntelligenceService()
    
    # Simulate a frame with a worker lacking a helmet
    frame = Frame(
        frame_id=str(uuid4()),
        camera_id="CAM-01",
        timestamp=utcnow(),
        detections=[
            Detection(
                label="Worker",
                confidence=0.95,
                bounding_box=BoundingBox(10.0, 10.0, 50.0, 100.0, 0.95),
                attributes={"helmet": False}
            )
        ]
    )
    
    events = await service.process_frame(frame)
    
    # Should emit WORKER_DETECTED and PPE_VIOLATION
    assert len(events) == 2
    event_types = [e["event_type"] for e in events]
    assert "WORKER_DETECTED" in event_types
    assert "PPE_VIOLATION" in event_types
    
    ppe_event = next(e for e in events if e["event_type"] == "PPE_VIOLATION")
    assert ppe_event["payload"]["label"] == "Missing Helmet"

@pytest.mark.asyncio
async def test_vision_pipeline_fire_hazard():
    service = VisionIntelligenceService()
    
    # Simulate a frame with a fire hazard
    frame = Frame(
        frame_id=str(uuid4()),
        camera_id="CAM-02",
        timestamp=utcnow(),
        detections=[
            Detection(
                label="Fire",
                confidence=0.88,
                bounding_box=BoundingBox(100.0, 100.0, 150.0, 150.0, 0.88)
            )
        ]
    )
    
    events = await service.process_frame(frame)
    
    # Should emit FIRE_DETECTED
    assert len(events) == 1
    assert events[0]["event_type"] == "FIRE_DETECTED"
    assert events[0]["severity"] == "CRITICAL"

@pytest.mark.asyncio
async def test_tracking_persistence():
    service = VisionIntelligenceService()
    
    # Frame 1
    frame1 = Frame(
        frame_id=str(uuid4()),
        camera_id="CAM-01",
        timestamp=utcnow(),
        detections=[
            Detection(label="Worker", confidence=0.9)
        ]
    )
    events1 = await service.process_frame(frame1)
    track_id = events1[0]["payload"]["track_id"]
    assert track_id is not None
    
    # Frame 2 with same track id
    frame2 = Frame(
        frame_id=str(uuid4()),
        camera_id="CAM-01",
        timestamp=utcnow(),
        detections=[
            Detection(label="Worker", confidence=0.9, track_id=track_id)
        ]
    )
    events2 = await service.process_frame(frame2)
    assert events2[0]["payload"]["track_id"] == track_id
