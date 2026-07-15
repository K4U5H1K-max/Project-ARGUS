from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, authenticate_stub
from app.kafka.producer import EventPublisher
from app.repositories.event_repository import EventRepository
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.database.session_factory() as session:
        yield session


def get_repository() -> EventRepository:
    return EventRepository()


def get_validator() -> EventValidationService:
    return EventValidationService()


def get_normalizer() -> EventNormalizationService:
    return EventNormalizationService()


def get_publisher(request: Request) -> EventPublisher:
    return request.app.state.kafka_producer


def get_event_service(request: Request) -> EventService:
    return request.app.state.event_service


async def get_auth_context(_: AuthContext = Depends(authenticate_stub)) -> AuthContext:
    return AuthContext(system="stub", subject="anonymous")
