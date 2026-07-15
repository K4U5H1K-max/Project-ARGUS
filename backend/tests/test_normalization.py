from __future__ import annotations

from app.core.enums import EventType
from app.services.event_normalization import EventNormalizationService


def test_normalizes_gas_aliases_to_ppm() -> None:
    service = EventNormalizationService()
    normalized = service.normalize(EventType.GAS_SENSOR, {"GasPPM": 12.4, "gasType": "co"})
    assert normalized["ppm"] == 12.4
    assert normalized["gas_type"] == "co"


def test_normalizes_nested_keys_to_snake_case() -> None:
    service = EventNormalizationService()
    normalized = service.normalize(EventType.START, {"sensorData": {"GasPPM": 3.2}})
    assert normalized["sensor_data"]["gas_ppm"] == 3.2
