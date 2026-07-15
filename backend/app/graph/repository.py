from __future__ import annotations

from datetime import datetime
from typing import Any

from neo4j import AsyncGraphDatabase, AsyncDriver
from neo4j.graph import Node, Path, Relationship

from app.graph.models import GraphNode, GraphRelationship, GraphRelationshipType


class GraphRepository:
    """Neo4j persistence adapter. Labels/types originate only from enums, never input."""
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j") -> None:
        self.database = database
        self.driver: AsyncDriver = AsyncGraphDatabase.driver(uri, auth=(username, password))

    async def close(self) -> None:
        await self.driver.close()

    async def verify_connectivity(self) -> None:
        await self.driver.verify_connectivity()

    async def bootstrap(self) -> None:
        async with self.driver.session(database=self.database) as session:
            await session.run("CREATE CONSTRAINT graph_entity_identity IF NOT EXISTS FOR (n:GraphEntity) REQUIRE (n.node_type, n.node_id) IS UNIQUE")
            await session.run("CREATE INDEX graph_revision_event IF NOT EXISTS FOR (r:GraphRevision) ON (r.event_id)")

    async def upsert_node(self, node: GraphNode, *, revision: int, event_id: str) -> None:
        query = """
        MERGE (n:GraphEntity {node_type: $node_type, node_id: $node_id})
        SET n += $properties, n.revision = $revision, n.last_event_id = $event_id
        """
        async with self.driver.session(database=self.database) as session:
            await session.run(query, node_type=node.node_type.value, node_id=node.node_id, properties=node.properties, revision=revision, event_id=event_id)

    async def upsert_relationship(self, relationship: GraphRelationship, *, revision: int, event_id: str, occurred_at: datetime) -> None:
        rel_type = GraphRelationshipType(relationship.relationship_type).value
        query = f"""
        MATCH (source:GraphEntity {{node_type: $source_type, node_id: $source_id}})
        MATCH (target:GraphEntity {{node_type: $target_type, node_id: $target_id}})
        OPTIONAL MATCH (source)-[open:{rel_type}]->(target) WHERE open.valid_to IS NULL
        FOREACH (existing IN CASE WHEN open IS NULL THEN [] ELSE [open] END | SET existing.valid_to = $occurred_at, existing.updated_at = datetime())
        MERGE (source)-[r:{rel_type} {{relationship_id: $relationship_id}}]->(target)
        SET r += $properties, r.revision = $revision, r.relationship_version = $revision,
            r.last_event_id = $event_id, r.valid_from = $occurred_at, r.valid_to = NULL,
            r.created_at = coalesce(r.created_at, datetime()), r.updated_at = datetime()
        """
        async with self.driver.session(database=self.database) as session:
            relationship_id = f"{event_id}:{rel_type}:{relationship.source.node_type.value}:{relationship.source.node_id}:{relationship.target.node_type.value}:{relationship.target.node_id}"
            await session.run(query, source_type=relationship.source.node_type.value, source_id=relationship.source.node_id, target_type=relationship.target.node_type.value, target_id=relationship.target.node_id, properties=relationship.properties, revision=revision, event_id=event_id, occurred_at=occurred_at, relationship_id=relationship_id)

    async def checkpoint(self, *, plant_id: str, graph_revision: int, twin_revision: int, event_id: str, status: str) -> None:
        async with self.driver.session(database=self.database) as session:
            await session.run("MERGE (c:GraphSyncCheckpoint {plant_id:$plant_id}) SET c.graph_revision=$graph_revision,c.twin_revision=$twin_revision,c.event_id=$event_id,c.sync_status=$status,c.sync_timestamp=datetime()", plant_id=plant_id, graph_revision=graph_revision, twin_revision=twin_revision, event_id=event_id, status=status)

    async def checkpoint_status(self, plant_id: str) -> list[dict[str, Any]]:
        return await self.query("MATCH (c:GraphSyncCheckpoint {plant_id:$plant_id}) RETURN c", plant_id=plant_id)

    async def create_revision(self, *, event_id: str, plant_id: str, revision: int, replay: bool) -> None:
        async with self.driver.session(database=self.database) as session:
            await session.run("CREATE (:GraphRevision {event_id: $event_id, plant_id: $plant_id, revision: $revision, replay: $replay, created_at: datetime()})", event_id=event_id, plant_id=plant_id, revision=revision, replay=replay)

    async def query(self, cypher: str, **parameters: Any) -> list[dict[str, Any]]:
        async with self.driver.session(database=self.database) as session:
            result = await session.run(cypher, **parameters)
            return [{key: self._jsonable(value) for key, value in record.data().items()} async for record in result]

    def _jsonable(self, value: Any) -> Any:
        if isinstance(value, Node): return {"node_type": value.get("node_type"), "node_id": value.get("node_id"), "properties": dict(value)}
        if isinstance(value, Relationship): return {"relationship": value.type, "properties": dict(value)}
        if isinstance(value, Path): return {"nodes": [self._jsonable(node) for node in value.nodes], "relationships": [self._jsonable(rel) for rel in value.relationships]}
        if isinstance(value, list): return [self._jsonable(item) for item in value]
        if isinstance(value, dict): return {key: self._jsonable(item) for key, item in value.items()}
        return value
