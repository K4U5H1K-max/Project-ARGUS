from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.predictive.models import ForecastHorizon

class BaseForecaster:
    def forecast(self, historical_data: List[Dict[str, Any]], horizon: ForecastHorizon) -> List[Dict[str, Any]]:
        raise NotImplementedError

class LinearTrendForecaster(BaseForecaster):
    def forecast(self, historical_data: List[Dict[str, Any]], horizon: ForecastHorizon) -> List[Dict[str, Any]]:
        # Simulate simple linear extrapolation for numeric metrics
        if not historical_data:
            return []
            
        last_point = historical_data[-1]
        forecasts = []
        
        # Example naive extrapolation
        for minute in range(1, horizon.minutes + 1):
            projected = last_point.copy()
            projected["timestamp"] = last_point["timestamp"] + timedelta(minutes=minute)
            # Simulate a 5% increase per minute for gas
            if "ppm" in projected:
                projected["ppm"] = projected["ppm"] * 1.05
            forecasts.append(projected)
            
        return forecasts

class ForecastingFramework:
    def __init__(self) -> None:
        self.providers: Dict[str, BaseForecaster] = {
            "linear": LinearTrendForecaster()
        }

    def generate_forecast(self, metric: str, historical_data: List[Dict[str, Any]], horizon: ForecastHorizon, provider: str = "linear") -> List[Dict[str, Any]]:
        forecaster = self.providers.get(provider)
        if not forecaster:
            raise ValueError(f"Unknown forecasting provider: {provider}")
        return forecaster.forecast(historical_data, horizon)
