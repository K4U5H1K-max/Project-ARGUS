from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.database.session import DatabaseManager
from app.kafka.producer import AIOKafkaEventPublisher
from app.repositories.event_repository import EventRepository
from app.services.event_normalization import EventNormalizationService
from app.services.event_service import EventService
from app.services.event_validation import EventValidationService


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

    repository = EventRepository()
    validator = EventValidationService()
    normalizer = EventNormalizationService()
    service = EventService(
        repository=repository,
        validator=validator,
        normalizer=normalizer,
        publisher=kafka_producer,
    )

    app.state.settings = settings
    app.state.database = database
    app.state.kafka_producer = kafka_producer
    app.state.event_service = service
    app.state.logger = logger

    logger.info("application_started", app_name=settings.app_name, env=settings.app_env)
    try:
        yield
    finally:
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
