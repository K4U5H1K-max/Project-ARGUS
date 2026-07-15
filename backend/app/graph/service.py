from __future__ import annotations

from app.graph.repository import GraphRepository
from datetime import datetime


class GraphQueryService:
    def __init__(self, repository: GraphRepository) -> None: self.repository = repository

    async def node(self, node_type: str, node_id: str): return await self.repository.query("MATCH (n:GraphEntity {node_type:$node_type,node_id:$node_id}) RETURN n", node_type=node_type, node_id=node_id)
    async def neighbors(self, node_type: str, node_id: str): return await self.repository.query("MATCH (n:GraphEntity {node_type:$node_type,node_id:$node_id})-[r]-(m:GraphEntity) RETURN type(r) AS relationship, m", node_type=node_type, node_id=node_id)
    async def path(self, source_id: str, target_id: str, max_depth: int = 6): return await self.repository.query("MATCH p=shortestPath((a:GraphEntity {node_id:$source_id})-[*..%d]-(b:GraphEntity {node_id:$target_id})) RETURN p" % max_depth, source_id=source_id, target_id=target_id)
    async def radius(self, node_id: str, radius: int = 2): return await self.repository.query("MATCH (n:GraphEntity {node_id:$node_id})-[*1..%d]-(related:GraphEntity) RETURN DISTINCT related" % radius, node_id=node_id)
    async def zone_graph(self, zone_id: str): return await self.repository.query("MATCH (z:GraphEntity {node_type:'Zone',node_id:$zone_id})-[r*0..2]-(n:GraphEntity) RETURN z,r,n", zone_id=zone_id)
    async def impact(self, node_id: str): return await self.repository.query("MATCH (n:GraphEntity {node_id:$node_id})-[:AFFECTED_BY|DEPENDS_ON|CONNECTED_TO*1..4]-(impact:GraphEntity) RETURN DISTINCT impact", node_id=node_id)
    async def dependencies(self, node_id: str): return await self.repository.query("MATCH (n:GraphEntity {node_id:$node_id})-[:DEPENDS_ON*1..8]->(dependency:GraphEntity) RETURN DISTINCT dependency", node_id=node_id)
    async def worker_exposure(self, worker_id: str): return await self.repository.query("MATCH (w:GraphEntity {node_type:'Worker',node_id:$worker_id})-[:WORKING_IN]->(:GraphEntity)<-[:LOCATED_IN]-(asset)-[:AFFECTED_BY]->(hazard:GraphEntity) RETURN asset,hazard", worker_id=worker_id)
    async def permit_overlap(self, permit_id: str): return await self.repository.query("MATCH (p:GraphEntity {node_type:'Permit',node_id:$permit_id})-[:VALID_FOR]->(z:GraphEntity)<-[:VALID_FOR]-(other:GraphEntity {node_type:'Permit'}) WHERE other.node_id <> $permit_id RETURN other,z", permit_id=permit_id)
    async def historical_neighbors(self, node_type: str, node_id: str, at: datetime): return await self.repository.query("MATCH (n:GraphEntity {node_type:$node_type,node_id:$node_id})-[r]-(m:GraphEntity) WHERE r.valid_from <= $at AND (r.valid_to IS NULL OR r.valid_to > $at) RETURN type(r) AS relationship,m", node_type=node_type, node_id=node_id, at=at)
