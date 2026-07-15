from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db_session, get_event_service
from app.api.router import api_router
from app.core.exceptions import register_exception_handlers
from app.database.base import Base
from app.kafka.producer import EventPublisher
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreateRequest
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService


class MockKafkaPublisher(EventPublisher):
    def __init__(self) -> None:
        self.is_ready = True
        self.published_events: list[dict[str, object]] = []

    async def start(self) -> None:
        self.is_ready = True

    async def stop(self) -> None:
        self.is_ready = False

    async def publish(self, event: dict[str, object]) -> None:
        self.published_events.append(event)


@pytest_asyncio.fixture()
async def db_session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()


@pytest_asyncio.fixture()
async def session(db_session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    async with db_session_factory() as session:
        yield session


@pytest.fixture()
def mock_publisher() -> MockKafkaPublisher:
    return MockKafkaPublisher()


@pytest.fixture()
def event_service(mock_publisher: MockKafkaPublisher) -> EventService:
    return EventService(
        repository=EventRepository(),
        validator=EventValidationService(),
        normalizer=EventNormalizationService(),
        publisher=mock_publisher,
    )


@pytest.fixture()
def app(event_service: EventService, db_session_factory: async_sessionmaker[AsyncSession], mock_publisher: MockKafkaPublisher) -> FastAPI:
    application = FastAPI()
    register_exception_handlers(application)
    application.include_router(api_router, prefix="/api/v1")
    application.state.kafka_producer = mock_publisher
    application.state.event_service = event_service
    application.state.database = type(
        "DatabaseState",
        (),
        {"session_factory": db_session_factory},
    )()

    async def override_db_session() -> AsyncIterator[AsyncSession]:
        async with db_session_factory() as db_session:
            yield db_session

    def override_event_service() -> EventService:
        return event_service

    application.dependency_overrides[get_db_session] = override_db_session
    application.dependency_overrides[get_event_service] = override_event_service
    return application


@pytest.fixture()
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture()
def valid_gas_event_payload() -> dict[str, object]:
    return {
        "source": "plc-01",
        "event_type": "GAS_SENSOR",
        "plant_id": "plant-a",
        "zone_id": "zone-1",
        "severity": "WARNING",
        "payload": {"gas_type": "co", "gas_ppm": 42.5},
        "metadata": {"asset_vendor": "acme"},
    }
