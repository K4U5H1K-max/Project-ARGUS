from app.analytics.models import KPISnapshot
from typing import List

class HistoricalAnalyticsService:
    async def save_snapshot(self, snapshot: KPISnapshot) -> None:
        pass

    async def get_snapshots(self, entity_id: str, period: str) -> List[KPISnapshot]:
        return []
