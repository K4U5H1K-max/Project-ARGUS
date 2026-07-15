from __future__ import annotations

from app.graph.models import GraphNode, GraphNodeType, GraphRelationship, GraphRelationshipType
from app.graph.repository import GraphRepository
from app.models.event import Event
from app.reliability.metrics import GRAPH_REPLAY_DURATION, GRAPH_SYNC_DURATION, GRAPH_SYNC_FAILURE, GRAPH_SYNC_SUCCESS, GRAPH_TEMPORAL_RELATIONSHIPS, GRAPH_UPDATES


class GraphSynchronizer:
    """Applies incremental graph facts from a committed twin event; never rebuilds Neo4j."""
    def __init__(self, repository: GraphRepository) -> None:
        self.repository = repository

    async def synchronize_event(self, event: Event, *, replay: bool = False) -> None:
        revision = event.processing_version
        timer = GRAPH_REPLAY_DURATION.time() if replay else GRAPH_SYNC_DURATION.time()
        checkpoint = getattr(self.repository, "checkpoint", None)
        with timer:
            try:
                plant = GraphNode(GraphNodeType.PLANT, event.plant_id, {"plant_id": event.plant_id})
                zone = GraphNode(GraphNodeType.ZONE, event.zone_id, {"zone_id": event.zone_id, "plant_id": event.plant_id})
                nodes = [plant, zone]
                relationships = [GraphRelationship(zone, GraphRelationshipType.PART_OF, plant)]
                if event.equipment_id:
                    equipment = GraphNode(GraphNodeType.EQUIPMENT, event.equipment_id, {"plant_id": event.plant_id, "zone_id": event.zone_id})
                    nodes.append(equipment); relationships.append(GraphRelationship(equipment, GraphRelationshipType.LOCATED_IN, zone))
                if event.worker_id:
                    worker = GraphNode(GraphNodeType.WORKER, event.worker_id, {"plant_id": event.plant_id})
                    nodes.append(worker); relationships.append(GraphRelationship(worker, GraphRelationshipType.WORKING_IN, zone, {"active": str(event.event_type) != "EXIT"}))
                payload = event.payload
                if sensor_id := payload.get("sensor_id") or payload.get("sensorId"):
                    sensor = GraphNode(GraphNodeType.SENSOR, str(sensor_id), {"plant_id": event.plant_id, "zone_id": event.zone_id})
                    nodes.append(sensor); relationships.append(GraphRelationship(sensor, GraphRelationshipType.LOCATED_IN, zone))
                    if event.equipment_id: relationships.append(GraphRelationship(sensor, GraphRelationshipType.MONITORS, GraphNode(GraphNodeType.EQUIPMENT, event.equipment_id)))
                if permit_id := payload.get("permit_id"):
                    permit = GraphNode(GraphNodeType.PERMIT, str(permit_id), {"plant_id": event.plant_id, "active": payload.get("active", True)})
                    nodes.append(permit); relationships.append(GraphRelationship(permit, GraphRelationshipType.VALID_FOR, zone))
                if maintenance_id := payload.get("maintenance_id"):
                    maintenance = GraphNode(GraphNodeType.MAINTENANCE, str(maintenance_id), {"plant_id": event.plant_id})
                    nodes.append(maintenance); relationships.append(GraphRelationship(maintenance, GraphRelationshipType.LOCATED_IN, zone))
                if hazard_id := payload.get("hazard_id"):
                    hazard = GraphNode(GraphNodeType.HAZARD, str(hazard_id), {"severity": str(event.severity), "active": True})
                    nodes.append(hazard); relationships.append(GraphRelationship(hazard, GraphRelationshipType.LOCATED_IN, zone))
                    if event.equipment_id: relationships.append(GraphRelationship(GraphNode(GraphNodeType.EQUIPMENT, event.equipment_id), GraphRelationshipType.AFFECTED_BY, hazard))
                for node in nodes:
                    await self.repository.upsert_node(node, revision=revision, event_id=str(event.event_id))
                for relationship in relationships:
                    await self.repository.upsert_relationship(relationship, revision=revision, event_id=str(event.event_id), occurred_at=event.timestamp)
                    GRAPH_TEMPORAL_RELATIONSHIPS.labels(relationship_type=relationship.relationship_type.value).inc()
                await self.repository.create_revision(event_id=str(event.event_id), plant_id=event.plant_id, revision=revision, replay=replay)
                if callable(checkpoint):
                    await checkpoint(plant_id=event.plant_id, graph_revision=revision, twin_revision=revision, event_id=str(event.event_id), status="SYNCED")
                GRAPH_UPDATES.labels(result="success").inc(); GRAPH_SYNC_SUCCESS.inc()
            except Exception:
                GRAPH_UPDATES.labels(result="failure").inc(); GRAPH_SYNC_FAILURE.inc()
                if callable(checkpoint):
                    await checkpoint(plant_id=event.plant_id, graph_revision=revision, twin_revision=revision, event_id=str(event.event_id), status="FAILED")
                raise
