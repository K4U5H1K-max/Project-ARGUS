from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.api.deps import get_db_session, get_event_service
from app.api.router import api_router
from app.actions.repositories import ActionRepository
from app.context.repositories import ContextRepository
from app.core.exceptions import register_exception_handlers
from app.database.base import Base
from app.geo.service import GeoIntelligenceService
from app.digital_twin.repositories import TwinRepository
from app.intelligence.repositories import IntelligenceRepository
from app.intelligence.services import IndustrialIntelligenceService
from app.risk.projection import GeoSpatialProjectionService
from app.risk.service import RiskService
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreateRequest
from app.phase2.coordinator import Phase2Coordinator
from app.reliability.outbox import OutboxService
from app.reliability.repositories import OutboxRepository
from app.reliability.repositories import ProcessedEventRepository
from app.reliability.worker import OutboxPublisherWorker
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService


class MockGraphQueryService:
    async def node(self, node_type: str, node_id: str):
        return [{"n": {"node_type": node_type, "node_id": node_id, "properties": {"coordinates": [12.0, 48.0]}}}]

    async def worker_exposure(self, worker_id: str):
        return [{"asset": {"node_type": "Equipment", "node_id": f"eq-{worker_id}", "properties": {"coordinates": [12.1, 48.1]}}}]

    async def impact(self, node_id: str):
        return [{"impact": {"node_type": "Equipment", "node_id": f"impact-{node_id}", "properties": {"coordinates": [12.2, 48.2]}}}]

    async def zone_graph(self, zone_id: str):
        return [{"z": {"node_type": "Zone", "node_id": zone_id, "properties": {"coordinates": [12.3, 48.3]}}}]


class MockKafkaPublisher:
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
def outbox_repository() -> OutboxRepository:
    return OutboxRepository()


@pytest.fixture()
def outbox_service(outbox_repository: OutboxRepository) -> OutboxService:
    return OutboxService(outbox_repository)


@pytest.fixture()
def phase2_coordinator(outbox_service: OutboxService) -> Phase2Coordinator:
    return Phase2Coordinator(
        twin_repository=TwinRepository(),
        context_repository=ContextRepository(),
        action_repository=ActionRepository(),
        outbox_service=outbox_service,
    )


@pytest.fixture()
def mock_graph_query_service() -> MockGraphQueryService:
    return MockGraphQueryService()


@pytest.fixture()
def risk_service(outbox_service: OutboxService) -> RiskService:
    return RiskService(outbox_service)


@pytest.fixture()
def risk_projection_service(mock_graph_query_service: MockGraphQueryService) -> GeoSpatialProjectionService:
    return GeoSpatialProjectionService(mock_graph_query_service)


@pytest.fixture()
def event_service(phase2_coordinator: Phase2Coordinator, outbox_service: OutboxService) -> EventService:
    return EventService(
        repository=EventRepository(),
        validator=EventValidationService(),
        normalizer=EventNormalizationService(),
        outbox_service=outbox_service,
        processed_event_repository=ProcessedEventRepository(),
        phase2_coordinator=phase2_coordinator,
    )


@pytest.fixture()
def app(event_service: EventService, db_session_factory: async_sessionmaker[AsyncSession], mock_publisher: MockKafkaPublisher, phase2_coordinator: Phase2Coordinator, risk_service: RiskService, risk_projection_service: GeoSpatialProjectionService, mock_graph_query_service: MockGraphQueryService) -> FastAPI:
    application = FastAPI()
    register_exception_handlers(application)
    application.include_router(api_router)
    application.state.kafka_producer = mock_publisher
    application.state.event_service = event_service
    application.state.phase2_coordinator = phase2_coordinator
    application.state.risk_service = risk_service
    application.state.risk_projection_service = risk_projection_service
    application.state.graph_query_service = mock_graph_query_service
    application.state.intelligence_service = IndustrialIntelligenceService(IntelligenceRepository())
    application.state.geo_service = GeoIntelligenceService(application.state.graph_query_service, risk_service, risk_projection_service)
    application.state.outbox_worker = None
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
