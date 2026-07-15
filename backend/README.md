# Project ARGUS Backend

Phase 1 implements the event platform for the Industrial Safety Intelligence Platform.

## Services

- FastAPI API for event ingestion and querying
- PostgreSQL persistence with SQLAlchemy 2.x
- Kafka publication after successful persistence
- Alembic migrations

## Run with Docker

```bash
docker compose up --build
```

## API

- Swagger UI: http://localhost:8000/docs
- Health: `GET /health`
- Create event: `POST /events`
- List events: `GET /events`
- Get event by id: `GET /events/{id}`

## Environment

Copy `.env.example` to `.env` and adjust values if needed.
