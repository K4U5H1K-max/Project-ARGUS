from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request
from datetime import datetime

router = APIRouter(prefix="/graph", tags=["knowledge-graph"])


def _service(request: Request):
    service = getattr(request.app.state, "graph_query_service", None)
    if service is None:
        raise HTTPException(status_code=503, detail="Knowledge graph is unavailable")
    return service


@router.get("/nodes/{node_type}/{node_id}")
async def node(request: Request, node_type: str, node_id: str): return await _service(request).node(node_type, node_id)
@router.get("/nodes/{node_type}/{node_id}/neighbors")
async def neighbors(request: Request, node_type: str, node_id: str): return await _service(request).neighbors(node_type, node_id)
@router.get("/nodes/{node_type}/{node_id}/neighbors-at")
async def historical_neighbors(request: Request, node_type: str, node_id: str, at: datetime): return await _service(request).historical_neighbors(node_type, node_id, at)
@router.get("/paths/{source_id}/{target_id}")
async def path(request: Request, source_id: str, target_id: str, max_depth: int = Query(6, ge=1, le=12)): return await _service(request).path(source_id, target_id, max_depth)
@router.get("/nodes/{node_id}/radius")
async def radius(request: Request, node_id: str, hops: int = Query(2, ge=1, le=8)): return await _service(request).radius(node_id, hops)
@router.get("/zones/{zone_id}")
async def zone(request: Request, zone_id: str): return await _service(request).zone_graph(zone_id)
@router.get("/equipment/{equipment_id}")
async def equipment(request: Request, equipment_id: str): return await _service(request).node("Equipment", equipment_id)
@router.get("/workers/{worker_id}")
async def worker(request: Request, worker_id: str): return {"node": await _service(request).node("Worker", worker_id), "exposure": await _service(request).worker_exposure(worker_id)}
@router.get("/nodes/{node_id}/impact")
async def impact(request: Request, node_id: str): return await _service(request).impact(node_id)
@router.get("/nodes/{node_id}/dependencies")
async def dependencies(request: Request, node_id: str): return await _service(request).dependencies(node_id)
@router.get("/permits/{permit_id}/overlap")
async def permit_overlap(request: Request, permit_id: str): return await _service(request).permit_overlap(permit_id)
