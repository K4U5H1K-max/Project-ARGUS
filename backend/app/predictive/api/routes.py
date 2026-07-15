from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from app.predictive.models import ForecastHorizon, SimulationScenario
from app.predictive.services.services import PredictiveRiskService
from app.digital_twin.models import TwinStateSnapshot

router = APIRouter(prefix="/predictive", tags=["predictive"])
predictive_service = PredictiveRiskService()

@router.post("/forecast", response_model=Dict[str, Any])
async def generate_forecast(historical_data: List[Dict[str, Any]], minutes: int = 60) -> Dict[str, Any]:
    horizon = ForecastHorizon(minutes=minutes)
    prediction = await predictive_service.generate_prediction(historical_data, horizon)
    return {"status": "success", "prediction": prediction}

@router.post("/simulations", response_model=Dict[str, Any])
async def run_simulation(scenario: SimulationScenario, initial_snapshot: TwinStateSnapshot) -> Dict[str, Any]:
    results = await predictive_service.run_simulation(scenario, initial_snapshot)
    return {"status": "success", "results": results}

@router.get("/scenarios", response_model=Dict[str, Any])
async def get_scenarios() -> Dict[str, Any]:
    return {"scenarios": []}

@router.get("/compare", response_model=Dict[str, Any])
async def compare_scenarios() -> Dict[str, Any]:
    return {"comparison": {}}
