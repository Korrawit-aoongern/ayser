from fastapi import APIRouter, HTTPException
from ..schemas.health import HealthCheckResult, HealthMetrics

router = APIRouter(prefix="/metrics", tags=["metrics"])