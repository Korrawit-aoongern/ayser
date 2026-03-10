from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HealthCheck(BaseModel):
    health_id: Optional[int] = None
    service_id: int
    availability: str  # "Up" or "Down"
    responsiveness: Optional[str] = None  # "Fast" or "Slow"
    reliability: Optional[str] = None  # "Stable" or "Unstable"
    overall_score: Optional[float] = None
    checked_at: Optional[datetime] = None

class HealthCheckResult(BaseModel):
    health_id: Optional[int] = None
    service_id: int
    availability: str
    responsiveness: Optional[str] = None
    reliability: Optional[str] = None
    overall_score: Optional[float] = None
    latency_ms: Optional[float] = None
    http_status: Optional[int] = None
    checked_at: Optional[datetime] = None

class ServiceEvent(BaseModel):
    event_id: Optional[int] = None
    service_id: int
    event_level: str  # "INFO", "WARNING", "ERROR"
    event_message: str
    detected_at: Optional[datetime] = None

class ServiceMetric(BaseModel):
    metric_id: Optional[int] = None
    service_id: int
    metric_name: str
    metric_value: float
    metric_unit: Optional[str] = None
    collected_at: Optional[datetime] = None

class HealthMetrics(BaseModel):
    availability: str
    responsiveness: Optional[str] = None
    reliability: Optional[str] = None
    overall_score: Optional[float] = None
    error_count: int = 0
    check_count: int = 0
    uptime_percentage: float = 100.0

