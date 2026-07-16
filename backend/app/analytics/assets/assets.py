from typing import Dict, Any

class AssetIntelligenceService:
    async def calculate_health_score(self, equipment_id: str) -> float:
        return 92.5

    async def estimate_rul(self, equipment_id: str) -> int:
        # Remaining Useful Life in days
        return 120
