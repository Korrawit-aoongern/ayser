from fastapi import APIRouter, HTTPException
from schemas.health import HealthCheckResult, HealthMetrics
from services.health_service import check_service_health

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/services/{service_id}", response_model=HealthCheckResult)
def get_service_health(service_id: int):
    """Get health status of a service"""
    result = check_service_health(service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return result

@router.get("/services/{service_id}/metrics", response_model=HealthMetrics)
def get_service_metrics(service_id: int):
    """Get detailed health metrics for a service"""
    # TODO: Fetch from metrics endpoint or database
    return {
        "availability": "Up",
        "responsiveness": "Fast",
        "reliability": "Stable",
        "cpu": "45%",
        "memory": "62%",
        "disk": "78%",
        "error_rate": "0.2%",
        "request_count": 1000,
        "latency": 24
    }

@router.post("/services/{service_id}/check")
def trigger_health_check(service_id: int):
    """Manually trigger a health check for a service"""
    result = check_service_health(service_id)
    if not result:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": f"Health check completed for service {service_id}", "result": result}
