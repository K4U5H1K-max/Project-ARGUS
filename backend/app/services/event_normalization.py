from __future__ import annotations

import re
from typing import Any, ClassVar, Protocol

from app.core.enums import EventType


_SNAKE_CASE_PATTERN_1 = re.compile("(.)([A-Z][a-z]+)")
_SNAKE_CASE_PATTERN_2 = re.compile("([a-z0-9])([A-Z])")


def to_snake_case(value: str) -> str:
    value = _SNAKE_CASE_PATTERN_1.sub(r"\1_\2", value)
    value = _SNAKE_CASE_PATTERN_2.sub(r"\1_\2", value)
    return value.replace("-", "_").lower()


def normalize_keys(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {to_snake_case(str(key)): normalize_keys(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [normalize_keys(item) for item in payload]
    return payload


class PayloadNormalizer(Protocol):
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...


class DefaultPayloadNormalizer:
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        return normalize_keys(payload)


class GasSensorPayloadNormalizer(DefaultPayloadNormalizer):
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = super().normalize(payload)
        for alias in ("gas_ppm", "co_ppm", "gasppm", "ppm"):
            if alias in normalized:
                normalized["ppm"] = normalized.pop(alias)
                break
        return normalized


class TemperatureSensorPayloadNormalizer(DefaultPayloadNormalizer):
    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = super().normalize(payload)
        if isinstance(normalized.get("unit"), str):
            normalized["unit"] = normalized["unit"].upper()
        return normalized


class EventNormalizationService:
    _registry: ClassVar[dict[EventType, PayloadNormalizer]] = {
        EventType.GAS_SENSOR: GasSensorPayloadNormalizer(),
        EventType.TEMPERATURE_SENSOR: TemperatureSensorPayloadNormalizer(),
    }
    _default_normalizer: ClassVar[PayloadNormalizer] = DefaultPayloadNormalizer()

    def normalize(self, event_type: EventType, payload: dict[str, Any]) -> dict[str, Any]:
        normalizer = self._registry.get(event_type, self._default_normalizer)
        return normalizer.normalize(payload)
