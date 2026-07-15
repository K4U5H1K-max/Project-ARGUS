from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthContext, authenticate_request
from app.kafka.producer import EventPublisher
from app.geo.service import GeoIntelligenceService
from app.intelligence.services import IndustrialIntelligenceService
from app.repositories.event_repository import EventRepository
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async with request.app.state.database.session_factory() as session:
        session.info["event_publisher"] = getattr(request.app.state, "kafka_producer", None)
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


def get_risk_service(request: Request):
    return request.app.state.risk_service


def get_risk_projection_service(request: Request):
    return request.app.state.risk_projection_service


def get_graph_query_service(request: Request):
    return request.app.state.graph_query_service


def get_intelligence_service(request: Request) -> IndustrialIntelligenceService:
    return request.app.state.intelligence_service


def get_geo_service(request: Request) -> GeoIntelligenceService:
    return request.app.state.geo_service


async def get_auth_context(auth_context: AuthContext = Depends(authenticate_request)) -> AuthContext:
    return auth_context
