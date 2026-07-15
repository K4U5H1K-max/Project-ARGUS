from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.core.enums import EventSeverity, EventType
from app.graph.synchronizer import GraphSynchronizer
from app.models.event import Event


class RecordingGraphRepository:
    def __init__(self) -> None: self.nodes = []; self.relationships = []; self.revisions = []
    async def upsert_node(self, node, **kwargs): self.nodes.append((node, kwargs))
    async def upsert_relationship(self, relationship, **kwargs): self.relationships.append((relationship, kwargs))
    async def create_revision(self, **kwargs): self.revisions.append(kwargs)


@pytest.mark.asyncio
async def test_synchronizer_merges_incremental_operational_facts() -> None:
    repository = RecordingGraphRepository()
    event = Event(event_id=uuid4(), external_event_id="graph-1", timestamp=datetime.now(UTC), source="test", event_type=EventType.GAS_SENSOR, plant_id="plant-1", zone_id="zone-1", equipment_id="eq-1", worker_id="worker-1", severity=EventSeverity.WARNING, payload={"sensor_id": "sensor-1", "hazard_id": "hazard-1"}, event_metadata={}, processing_version=3)
    await GraphSynchronizer(repository).synchronize_event(event, replay=True)
    assert {node.node_type.value for node, _ in repository.nodes} == {"Plant", "Zone", "Equipment", "Worker", "Sensor", "Hazard"}
    assert any(relationship.relationship_type.value == "MONITORS" for relationship, _ in repository.relationships)
    assert repository.revisions[0]["replay"] is True
