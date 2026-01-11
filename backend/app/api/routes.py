from fastapi import APIRouter
from services.health_service import get_health_status

router = APIRouter()

@router.get("/services/{service_id}/health")
def service_health(service_id: str):
    return get_health_status(service_id)