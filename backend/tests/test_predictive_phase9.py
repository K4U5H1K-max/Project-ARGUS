import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.predictive.models import ForecastHorizon, SimulationScenario, SimulatedEvent
from app.predictive.services.services import PredictiveRiskService
from app.digital_twin.models import TwinStateSnapshot
from app.core.enums import EventType, EventSeverity
from app.core.time import utcnow

@pytest.mark.asyncio
async def test_predictive_forecast_gas_leak():
    service = PredictiveRiskService()
    
    # Simulate a gradually rising gas concentration
    historical_data = [
        {"timestamp": utcnow() - timedelta(minutes=10), "ppm": 80.0, "zone_id": "ZONE-A"},
        {"timestamp": utcnow() - timedelta(minutes=5), "ppm": 85.0, "zone_id": "ZONE-A"},
        {"timestamp": utcnow(), "ppm": 90.0, "zone_id": "ZONE-A"}
    ]
    
    # Predict 15 minutes into the future
    prediction = await service.generate_prediction(historical_data, ForecastHorizon(minutes=15))
    
    # Due to linear + 5% per minute simulation, it should exceed 100ppm and generate CRITICAL risk
    assert prediction.predicted_risk_level == "CRITICAL"
    assert len(prediction.simulated_events) > 0
    assert prediction.simulated_events[0].event_type == EventType.GAS_SENSOR
    
    # Agent should suggest mitigation
    assert any("evacuate" in m.lower() for m in prediction.mitigation_suggestions)

@pytest.mark.asyncio
async def test_monte_carlo_simulation():
    service = PredictiveRiskService()
    
    scenario = SimulationScenario(
        name="Valve Failure Test",
        description="Testing complete valve failure.",
        initial_events=[
            SimulatedEvent(
                event_type=EventType.LEAK,
                timestamp=utcnow(),
                zone_id="ZONE-B",
                severity=EventSeverity.CRITICAL,
                payload={"pressure": 0.0}
            )
        ]
    )
    
    initial_snapshot = TwinStateSnapshot(
        snapshot_id="current",
        timestamp=utcnow(),
        plant_state={},
        zone_states={}
    )
    
    results = await service.run_simulation(scenario, initial_snapshot)
    
    # Verify the Monte Carlo loop executed
    assert "iterations" in results
    assert results["iterations"] == 10
    assert results["mean_risk_level"] == "CRITICAL"
    assert "agent_analysis" in results
