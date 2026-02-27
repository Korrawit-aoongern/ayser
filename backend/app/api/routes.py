from fastapi import APIRouter
from .auth import router as auth_router

from .services import router as services_router
from .user import router as user_router
from .health import router as health_router
from .event import router as event_router
from .metrics import router as metrics_router
from .monitor import router as monitor_router

router = APIRouter(prefix="/api")

# Include all route modules
router.include_router(auth_router)
router.include_router(services_router)
router.include_router(user_router)
router.include_router(health_router)
router.include_router(event_router)
router.include_router(metrics_router)
router.include_router(monitor_router)
