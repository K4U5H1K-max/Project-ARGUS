from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request, response: Response, session: AsyncSession = Depends(get_db_session)) -> dict[str, object]:
    database_ok = kafka_ok = worker_ok = replay_ok = False
    try:
        await session.execute(text("SELECT 1"))
        database_ok = True
    except Exception:
        pass
    producer = getattr(request.app.state, "kafka_producer", None)
    kafka_ok = bool(producer and producer.is_ready)
    worker = getattr(request.app.state, "outbox_worker", None)
    worker_ok = worker is not None and bool(getattr(getattr(worker, "status", None), "running", False))
    replay_ok = getattr(request.app.state, "replay_service", None) is not None or hasattr(request.app.state, "phase2_coordinator")
    healthy = database_ok and kafka_ok
    response.status_code = status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    return {"status": "ok" if healthy else "degraded", "database": database_ok, "kafka": kafka_ok, "outbox_worker": worker_ok, "replay_service": replay_ok}


@router.get("/liveness")
async def liveness_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness")
async def readiness_check(request: Request, session: AsyncSession = Depends(get_db_session)) -> Response:
    response = Response()
    body = await health_check(request, response, session)
    ready = bool(body["database"] and body["kafka"] and body["outbox_worker"] and body["replay_service"])
    return Response(content=__import__("json").dumps(body), media_type="application/json", status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE)
