from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.repositories import ActionRepository
from app.actions.schemas import ActionListResponse, ActionObject
from app.api.deps import get_auth_context, get_db_session
from app.core.auth import AuthContext
from app.core.time import utcnow

router = APIRouter(tags=["actions"])
repository = ActionRepository()


@router.get("/actions/latest", response_model=ActionObject)
async def latest_actions(
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> ActionObject:
    record = await repository.get_latest(session)
    if record is None:
        return ActionObject(action_id="", action_type="", priority=0, reason="", generated_by="", timestamp=utcnow(), context_id="", status="PENDING", action_data={}, plant_id="", zone_id="")
    return ActionObject.model_validate(record)


@router.get("/actions/history", response_model=ActionListResponse)
async def action_history(
    plant_id: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
) -> ActionListResponse:
    records, total = await repository.list_history(session, plant_id=plant_id, limit=limit, offset=offset)
    items = [ActionObject.model_validate(record) for record in records]
    return ActionListResponse(items=items, total=total, limit=limit, offset=offset)
