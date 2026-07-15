from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.actions.repositories import ActionRepository
from app.context.repositories import ContextRepository
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.database.session import DatabaseManager
from app.kafka.producer import AIOKafkaEventPublisher
from app.digital_twin.repositories import TwinRepository
from app.phase2.coordinator import Phase2Coordinator
from app.reliability.outbox import OutboxService
from app.reliability.repositories import OutboxRepository
from app.reliability.repositories import ProcessedEventRepository
from app.reliability.worker import OutboxPublisherWorker
from app.reliability.replay import ReplayService
from app.repositories.event_repository import EventRepository
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService
from app.graph.repository import GraphRepository
from app.graph.service import GraphQueryService
from app.graph.synchronizer import GraphSynchronizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    database = DatabaseManager(settings.database_url)
    await database.start()

    kafka_producer = AIOKafkaEventPublisher(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        topic=settings.kafka_topic_events,
    )
    await kafka_producer.start()

    outbox_repository = OutboxRepository()
    graph_repository = GraphRepository(settings.neo4j_uri, settings.neo4j_username, settings.neo4j_password, settings.neo4j_database)
    await graph_repository.bootstrap()
    graph_synchronizer = GraphSynchronizer(graph_repository)
    outbox_service = OutboxService(outbox_repository)
    outbox_worker = OutboxPublisherWorker(session_factory=database.session_factory, publisher=kafka_producer, repository=outbox_repository)
    await outbox_worker.start()

    repository = EventRepository()
    validator = EventValidationService()
    normalizer = EventNormalizationService()
    processed_event_repository = ProcessedEventRepository()
    twin_repository = TwinRepository()
    context_repository = ContextRepository()
    action_repository = ActionRepository()
    phase2_coordinator = Phase2Coordinator(
        twin_repository=twin_repository,
        context_repository=context_repository,
        action_repository=action_repository,
        outbox_service=outbox_service,
        graph_synchronizer=graph_synchronizer,
    )
    service = EventService(
        repository=repository,
        validator=validator,
        normalizer=normalizer,
        outbox_service=outbox_service,
        processed_event_repository=processed_event_repository,
        phase2_coordinator=phase2_coordinator,
    )
    replay_service = ReplayService(phase2_coordinator)

    app.state.settings = settings
    app.state.database = database
    app.state.kafka_producer = kafka_producer
    app.state.outbox_worker = outbox_worker
    app.state.phase2_coordinator = phase2_coordinator
    app.state.event_service = service
    app.state.graph_repository = graph_repository
    app.state.graph_query_service = GraphQueryService(graph_repository)
    app.state.replay_service = replay_service
    app.state.logger = logger

    logger.info("application_started", app_name=settings.app_name, env=settings.app_env)
    try:
        yield
    finally:
        await outbox_worker.stop()
        await graph_repository.close()
        await kafka_producer.stop()
        await database.stop()
        logger.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    register_exception_handlers(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
