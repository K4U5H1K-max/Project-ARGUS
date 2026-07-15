from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_auth_context, get_db_session, get_event_service
from app.core.auth import AuthContext
from app.schemas.event import EventCreateRequest, EventListResponse, EventResponse
from app.services.event_service import EventService

router = APIRouter(tags=["events"])


@router.post("/events", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: Request,
    payload: EventCreateRequest,
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    return await service.create_event(session=session, payload=payload, request=request)


@router.get("/events", response_model=EventListResponse)
async def list_events(
    request: Request,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
    service: EventService = Depends(get_event_service),
) -> EventListResponse:
    return await service.list_events(session=session, request=request, limit=limit, offset=offset)


@router.get("/events/{event_id}", response_model=EventResponse)
async def get_event_by_id(
    request: Request,
    event_id: UUID,
    _: AuthContext = Depends(get_auth_context),
    session: AsyncSession = Depends(get_db_session),
    service: EventService = Depends(get_event_service),
) -> EventResponse:
    return await service.get_event_by_id(session=session, request=request, event_id=event_id)
