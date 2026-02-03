from pydantic import BaseModel
from typing import Optional

class HealthCheckResult(BaseModel):
    service_id: int
    status: str  # "Running" or "Down"
    health: str  # percentage like "96.45%"
    latency_ms: int
    response_code: int
    last_check: str

class HealthMetrics(BaseModel):
    availability: str
    responsiveness: str
    reliability: str
    cpu: str
    memory: str
    disk: str
    error_rate: str
    request_count: int
    latency: int
