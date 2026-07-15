from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_risk_projection_service, get_risk_service
from app.reliability.metrics import HEATMAP_REQUESTS

router = APIRouter(prefix="/risk", tags=["risk"])


def _serialize_risk(risk) -> dict[str, object]:
    return {
        "risk_id": str(risk.risk_id),
        "plant_id": risk.plant_id,
        "zone_id": risk.zone_id,
        "score": risk.risk_score,
        "level": risk.risk_level,
        "confidence": risk.confidence,
        "status": risk.status,
        "timestamp": risk.timestamp,
        "recommendations": risk.recommendation,
        "explanation": risk.explanation,
        "trace": risk.trace,
    }


@router.get("")
async def latest(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service)):
    risks = await risk_service.list_history(session, limit=100)
    return [_serialize_risk(risk) for risk in risks]


@router.get("/latest")
async def latest_only(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service)):
    risk = await risk_service.latest(session)
    return _serialize_risk(risk) if risk is not None else None


@router.get("/current")
async def current(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), plant_id: str | None = Query(default=None), zone_id: str | None = Query(default=None)):
    risk = await risk_service.current(session, plant_id=plant_id, zone_id=zone_id)
    return _serialize_risk(risk) if risk is not None else None


@router.get("/history")
async def history(
    session: AsyncSession = Depends(get_db_session),
    risk_service=Depends(get_risk_service),
    plant_id: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="timestamp"),
    sort_order: str = Query(default="desc"),
):
    risks = await risk_service.history(
        session,
        plant_id=plant_id,
        zone_id=zone_id,
        risk_level=risk_level,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return [_serialize_risk(risk) for risk in risks]


@router.get("/search")
async def search(
    session: AsyncSession = Depends(get_db_session),
    risk_service=Depends(get_risk_service),
    query: str | None = Query(default=None),
    plant_id: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    sort_by: str = Query(default="timestamp"),
    sort_order: str = Query(default="desc"),
):
    risks = await risk_service.search(
        session,
        query=query,
        plant_id=plant_id,
        zone_id=zone_id,
        risk_level=risk_level,
        status=status,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return [_serialize_risk(risk) for risk in risks]


@router.get("/statistics")
async def statistics(
    session: AsyncSession = Depends(get_db_session),
    risk_service=Depends(get_risk_service),
    plant_id: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    return await risk_service.statistics(session, plant_id=plant_id, zone_id=zone_id, status=status)


@router.get("/critical")
async def critical(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service)):
    risks = await risk_service.list_history(session, risk_level="CRITICAL")
    return [_serialize_risk(risk) for risk in risks]


@router.get("/zones/{zone_id}")
async def zone(zone_id: str, session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service)):
    risks = await risk_service.list_history(session, zone_id=zone_id)
    return [_serialize_risk(risk) for risk in risks]


@router.get("/timeline")
async def timeline(
    session: AsyncSession = Depends(get_db_session),
    risk_service=Depends(get_risk_service),
    plant_id: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    return await risk_service.timeline(session, plant_id=plant_id, zone_id=zone_id, limit=limit)


@router.get("/cluster")
async def cluster(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return {"clusters": [], "summary": {"count": 0}}
    projection = await projection_service.project_assessment(latest_risk)
    return {"clusters": projection["summary"].get("clusters", 0), "summary": projection["summary"], "features": projection["features"]}


@router.get("/radius")
async def radius(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return {"radius_meters": 0, "features": []}
    projection = await projection_service.project_assessment(latest_risk)
    return {
        "radius_meters": max((feature["properties"].get("radius_meters", 0) for feature in projection["features"]), default=0),
        "features": projection["features"],
        "summary": projection["summary"],
    }


@router.get("/map")
@router.get("/heatmap")
async def map_risks(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    HEATMAP_REQUESTS.inc()
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return {"type": "FeatureCollection", "features": [], "summary": {"count": 0}}
    return await projection_service.project_assessment(latest_risk)


@router.get("/zones")
async def projected_zones(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return []
    return await projection_service.zones(latest_risk)


@router.get("/workers")
async def projected_workers(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return []
    return await projection_service.workers(latest_risk)


@router.get("/equipment")
async def projected_equipment(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return []
    return await projection_service.equipment(latest_risk)


@router.get("/hotspots")
async def projected_hotspots(session: AsyncSession = Depends(get_db_session), risk_service=Depends(get_risk_service), projection_service=Depends(get_risk_projection_service)):
    latest_risk = await risk_service.latest(session)
    if latest_risk is None:
        return []
    return await projection_service.hotspots(latest_risk)
