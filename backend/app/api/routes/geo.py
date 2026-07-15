from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_geo_service

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/layout")
async def layout(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.layout(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/heatmap")
async def heatmap(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.heatmap(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/hazards")
async def hazards(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.hazards(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/routes")
async def routes(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.routes(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/evacuation")
async def evacuation(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.evacuation(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/exposure")
async def exposure(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.exposure(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/clusters")
async def clusters(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.clusters(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/resources")
async def resources(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.resources(session, plant_id=plant_id, zone_id=zone_id)


@router.get("/nearest-safe-zone")
async def nearest_safe_zone(session: AsyncSession = Depends(get_db_session), geo_service=Depends(get_geo_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    return await geo_service.nearest_safe_zone(session, plant_id=plant_id, zone_id=zone_id)
