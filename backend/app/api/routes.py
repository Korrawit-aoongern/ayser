from fastapi import APIRouter
from .auth import router as auth_router
from .services import router as services_router
from .health import router as health_router

router = APIRouter(prefix="/api")

# Include all route modules
router.include_router(auth_router)
router.include_router(services_router)
router.include_router(health_router)