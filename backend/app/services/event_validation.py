from __future__ import annotations

from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, AliasChoices, field_validator

from app.core.enums import EventType
from app.core.exceptions import ValidationAppError


class GenericPayload(BaseModel):
    model_config = ConfigDict(extra="allow")


class GasSensorPayload(BaseModel):
    gas_type: str
    ppm: float = Field(ge=0, validation_alias=AliasChoices("gas_ppm", "ppm"))


class TemperatureSensorPayload(BaseModel):
    temperature: float
    unit: str

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in {"C", "F", "K"}:
            raise ValueError("unit must be one of C, F, or K")
        return normalized


class PressureSensorPayload(BaseModel):
    pressure: float
    unit: str | None = None


class VibrationSensorPayload(BaseModel):
    vibration: float
    unit: str | None = None


class VisionDetectionPayload(BaseModel):
    camera_id: str
    bounding_box: list[float] | None = None
    confidence: float
    label: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class EventValidationService:
    _registry: ClassVar[dict[EventType, type[BaseModel]]] = {
        EventType.GAS_SENSOR: GasSensorPayload,
        EventType.TEMPERATURE_SENSOR: TemperatureSensorPayload,
        EventType.PRESSURE_SENSOR: PressureSensorPayload,
        EventType.VIBRATION_SENSOR: VibrationSensorPayload,
        EventType.WORKER_DETECTED: VisionDetectionPayload,
        EventType.WORKER_LOST: VisionDetectionPayload,
        EventType.SMOKE_DETECTED: VisionDetectionPayload,
        EventType.FIRE_DETECTED: VisionDetectionPayload,
        EventType.GAS_CLOUD_DETECTED: VisionDetectionPayload,
        EventType.RESTRICTED_AREA_VIOLATION: VisionDetectionPayload,
        EventType.VEHICLE_DETECTED: VisionDetectionPayload,
        EventType.WORKER_FALL: VisionDetectionPayload,
        EventType.PPE_VIOLATION: VisionDetectionPayload,
    }
    def validate(self, event_type: EventType, payload: dict[str, Any]) -> dict[str, Any]:
        model = self._registry.get(event_type, GenericPayload)
        try:
            validated = model.model_validate(payload)
        except ValidationError as exc:
            raise ValidationAppError("Event payload validation failed", details=exc.errors()) from exc
        return validated.model_dump(mode="json")
