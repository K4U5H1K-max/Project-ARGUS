from typing import Dict, Any, List, Optional
from app.enterprise.models import DecisionBrief, Recommendation
from app.risk.service import RiskService
from app.digital_twin.state import StateManager
from app.intelligence.services import IndustrialIntelligenceService
from app.predictive.services.services import PredictiveRiskService

class DecisionSupportAgent:
    def __init__(
        self,
        risk_service: Optional[RiskService] = None,
        state_manager: Optional[StateManager] = None,
        intelligence_service: Optional[IndustrialIntelligenceService] = None,
        predictive_service: Optional[PredictiveRiskService] = None
    ) -> None:
        self.risk_service = risk_service or RiskService()
        self.state_manager = state_manager or StateManager()
        self.intelligence_service = intelligence_service or IndustrialIntelligenceService()
        self.predictive_service = predictive_service or PredictiveRiskService()

    async def generate_brief(self, context_id: str, incident_id: Optional[str] = None) -> DecisionBrief:
        # 1. Fetch Context Snapshot (Deterministic)
        # 2. Fetch Risk Assessment (Deterministic)
        # 3. Fetch Forecasts and Simulations (Predictive)
        # 4. Fetch RAG Regulatory / Incident citations
        
        evidence_graph = {
            "Risk Assessment": f"doc-risk-{context_id}",
            "Context Snapshot": f"doc-ctx-{context_id}",
            "Digital Twin Revision": f"rev-twin-{context_id}",
            "Forecast": "doc-forecast-latest",
            "Compliance Findings": "doc-comp-latest"
        }
        
        rec = Recommendation(
            action="Preemptively Evacuate Zone A",
            confidence=0.92,
            supporting_evidence=["Forecast indicates LEL (Lower Explosive Limit) breach in 15m", "Graph shows 5 workers in Zone A"],
            conflicting_evidence=["Maintenance log shows valve was serviced yesterday"],
            priority="CRITICAL",
            urgency="IMMEDIATE",
            impact="High (Production Stop in Zone A)",
            estimated_benefit="Prevents potential catastrophic explosion; Saves 5 workers"
        )
        
        brief = DecisionBrief(
            situation_summary="Gas leak detected in Zone A with rapidly escalating ppm levels. Forecast indicates potential explosion threshold within 15 minutes.",
            risk_level="CRITICAL",
            affected_assets=["Boiler B-1", "Valve V-9"],
            affected_workers=["W-101", "W-102", "W-103", "W-104", "W-105"],
            predicted_evolution="Concentration will exceed LEL in 15m. Probable ignition from nearby Hot Work permit (Permit-112).",
            recommendations=[rec],
            alternative_strategies=["Attempt remote shutdown of Valve V-9 (Low success probability due to rust history)"],
            trade_offs="Immediate evacuation halts production but guarantees worker safety. Remote shutdown attempts delay evacuation.",
            confidence=0.88,
            document_citations=["OSHA 1910.119", "Internal Safety Protocol SP-04"],
            evidence_graph=evidence_graph
        )
        return brief
