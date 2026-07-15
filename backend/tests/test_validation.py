from __future__ import annotations

import pytest

from app.core.enums import EventType
from app.core.exceptions import ValidationAppError
from app.services.event_validation import EventValidationService


def test_gas_sensor_validation_accepts_required_fields() -> None:
    service = EventValidationService()
    payload = service.validate(EventType.GAS_SENSOR, {"gas_type": "co2", "ppm": 15.2})
    assert payload["gas_type"] == "co2"
    assert payload["ppm"] == 15.2


def test_gas_sensor_validation_rejects_missing_fields() -> None:
    service = EventValidationService()
    with pytest.raises(ValidationAppError):
        service.validate(EventType.GAS_SENSOR, {"ppm": 15.2})


def test_temperature_validation_normalizes_unit() -> None:
    service = EventValidationService()
    payload = service.validate(EventType.TEMPERATURE_SENSOR, {"temperature": 30.0, "unit": "c"})
    assert payload["unit"] == "C"
