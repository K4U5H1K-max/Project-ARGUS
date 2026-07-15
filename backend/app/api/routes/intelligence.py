from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session, get_intelligence_service
from app.core.time import utcnow
from app.intelligence.repositories import DocumentPayload

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


def _serialize_risk_reference(risk) -> dict[str, object]:
    return {
        "risk_id": str(risk.risk_id),
        "plant_id": risk.plant_id,
        "zone_id": risk.zone_id,
        "score": risk.risk_score,
        "level": risk.risk_level,
        "confidence": risk.confidence,
        "timestamp": risk.timestamp,
        "explanation": risk.explanation,
        "recommendations": risk.recommendation,
        "trace": risk.trace,
    }


@router.get("/report/{risk_id}")
async def report(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return None
    return await intelligence_service.report(session, risk)


@router.get("/history/{risk_id}")
async def history(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return None
    return await intelligence_service.historical_history(session, risk)


@router.get("/regulations/{risk_id}")
async def regulations(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return []
    return await intelligence_service.regulations(session, risk)


@router.get("/recommendations/{risk_id}")
async def recommendations(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return []
    return await intelligence_service.recommendations(session, risk)


@router.get("/similar-incidents/{risk_id}")
async def similar_incidents(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return []
    return await intelligence_service.similar_incidents(session, risk)


@router.get("/root-causes/{risk_id}")
async def root_causes(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return []
    return await intelligence_service.root_causes(session, risk)


@router.get("/citations/{risk_id}")
async def citations(risk_id: str, session: AsyncSession = Depends(get_db_session), intelligence_service=Depends(get_intelligence_service)):
    risk = await intelligence_service.get_risk(session, risk_id)
    if risk is None:
        return []
    return await intelligence_service.citations(session, risk)


@router.post("/documents/ingest")
async def ingest_document(
    title: str,
    source_type: str,
    content: str,
    uri: str | None = None,
    session: AsyncSession = Depends(get_db_session),
    intelligence_service=Depends(get_intelligence_service),
):
    payload = DocumentPayload(title=title, source_type=source_type, content=content, uri=uri, metadata={"ingested_at": utcnow().isoformat()})
    return await intelligence_service.ingest_document(session, payload)
