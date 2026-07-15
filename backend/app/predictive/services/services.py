import logging
from typing import Dict, Any, List
from app.predictive.models import ForecastHorizon, Prediction, SimulatedEvent, SimulationScenario
from app.predictive.forecasting.forecasting import ForecastingFramework
from app.predictive.simulation.simulation import SimulationEngine, MonteCarloSimulator
from app.predictive.agents.agents import PredictionAgent, SimulationAgent
from app.digital_twin.models import TwinStateSnapshot
from app.core.enums import EventSeverity, EventType

logger = logging.getLogger(__name__)

class PredictiveRiskService:
    def __init__(self) -> None:
        self.forecasting = ForecastingFramework()
        self.simulation_engine = SimulationEngine()
        self.monte_carlo = MonteCarloSimulator(self.simulation_engine)
        self.prediction_agent = PredictionAgent()
        self.simulation_agent = SimulationAgent()

    async def generate_prediction(self, historical_data: List[Dict[str, Any]], horizon: ForecastHorizon) -> Prediction:
        # 1. Generate Forecast
        forecasts = self.forecasting.generate_forecast("gas_ppm", historical_data, horizon)
        
        # 2. Agent Enrichment (Identify mitigation steps based on forecast)
        mitigations = await self.prediction_agent.analyze_forecast(forecasts)
        
        # 3. Formulate Prediction Model
        simulated_events = []
        if any(f.get("ppm", 0) > 100 for f in forecasts):
            simulated_events.append(
                SimulatedEvent(
                    event_type=EventType.GAS_SENSOR,
                    timestamp=forecasts[-1]["timestamp"],
                    zone_id=historical_data[0].get("zone_id", "UNKNOWN"),
                    severity=EventSeverity.CRITICAL,
                    payload={"ppm": forecasts[-1].get("ppm", 105.0)},
                    probability=0.85
                )
            )
            
        prediction = Prediction(
            horizon=horizon,
            predicted_risk_level="CRITICAL" if simulated_events else "INFO",
            confidence=0.85,
            simulated_events=simulated_events,
            mitigation_suggestions=mitigations
        )
        
        logger.info(f"Prediction generated: {prediction.prediction_id}")
        return prediction

    async def run_simulation(self, scenario: SimulationScenario, initial_snapshot: TwinStateSnapshot) -> Dict[str, Any]:
        # 1. Run Monte Carlo Simulation
        results = await self.monte_carlo.run(scenario, initial_snapshot)
        
        # 2. Agent Evaluation
        analysis = await self.simulation_agent.analyze_scenario_outcomes(scenario, results)
        results["agent_analysis"] = analysis
        
        logger.info(f"Simulation completed for scenario: {scenario.scenario_id}")
        return results
