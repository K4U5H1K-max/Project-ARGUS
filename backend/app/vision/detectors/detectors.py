from abc import ABC, abstractmethod
from typing import List
from app.vision.models import Frame, Detection

class VisionDetector(ABC):
    @abstractmethod
    def detect(self, frame: Frame) -> List[Detection]:
        pass

class YoloDetector(VisionDetector):
    def detect(self, frame: Frame) -> List[Detection]:
        # Simulated YOLO inference
        return frame.detections
