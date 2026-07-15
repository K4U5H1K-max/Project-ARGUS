from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_auth_context, get_db_session
from app.context.repositories import ContextRepository
from app.context.schemas import ContextSnapshotResponse
from app.core.auth import AuthContext
from app.core.time import utcnow

router = APIRouter(tags=["context"])
repository = ContextRepository()


@router.get("/contexts/latest", response_model=ContextSnapshotResponse)
async def latest_context(
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> ContextSnapshotResponse:
    record = await repository.get_latest(session)
    if record is None:
        return ContextSnapshotResponse(context_id="", event_id="", plant_id="", zone_id="", timestamp=utcnow(), serialized_context={}, version=1)
    return ContextSnapshotResponse.model_validate(record)


@router.get("/contexts/history", response_model=list[ContextSnapshotResponse])
async def context_history(
    plant_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> list[ContextSnapshotResponse]:
    records = await repository.list_history(session, plant_id=plant_id, limit=limit, offset=offset)
    return [ContextSnapshotResponse.model_validate(record) for record in records]
