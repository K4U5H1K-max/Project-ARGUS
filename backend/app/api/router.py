from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.geo import router as geo_router
from app.api.routes.health import router as health_router
from fastapi import APIRouter

from app.api.routes.events import router as events_router
from app.api.routes.geo import router as geo_router
from app.api.routes.health import router as health_router
from app.api.routes.graph import router as graph_router
from app.api.routes.intelligence import router as intelligence_router
from app.api.routes.risk import router as risk_router
from app.api.routes.phase2 import actions_router, context_router, twin_router
from app.api.routes.emergency import router as emergency_router
from app.api.routes.permit import router as permit_router
from app.api.routes.compliance import router as compliance_router
from app.api.routes.notifications import router as notifications_router
from app.vision.api.routes import router as vision_router
api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(graph_router)
api_router.include_router(risk_router)
api_router.include_router(geo_router)
api_router.include_router(intelligence_router)
api_router.include_router(events_router)
api_router.include_router(twin_router)
api_router.include_router(context_router)
api_router.include_router(actions_router)
api_router.include_router(emergency_router)
api_router.include_router(permit_router)
api_router.include_router(compliance_router)
api_router.include_router(notifications_router)
api_router.include_router(vision_router)
