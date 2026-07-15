from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.phase2 import actions_router, context_router, twin_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(events_router)
api_router.include_router(twin_router)
api_router.include_router(context_router)
api_router.include_router(actions_router)
