from typing import Any, List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from app.core.time import utcnow

@dataclass
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    confidence: float

@dataclass
class Detection:
    label: str
    confidence: float
    detection_id: UUID = field(default_factory=uuid4)
    bounding_box: Optional[BoundingBox] = None
    attributes: Dict[str, Any] = field(default_factory=dict) # e.g., PPE specifics
    track_id: Optional[str] = None

@dataclass
class CameraMetadata:
    camera_id: str
    plant_id: str
    zone_id: str
    location_x: float
    location_y: float
    fov_polygon: List[List[float]] = field(default_factory=list)
    status: str = "ONLINE"
    resolution: str = "1080p"
    fps: int = 30

@dataclass
class Frame:
    frame_id: str
    camera_id: str
    timestamp: datetime
    detections: List[Detection] = field(default_factory=list)
    image_url: Optional[str] = None
