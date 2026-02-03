from pydantic import BaseModel
from typing import Optional

class ServiceCreate(BaseModel):
    service_name: str
    url: str
    advanced_method: str = "None"
    metrics_endpoint: Optional[str] = None

class ServiceUpdate(BaseModel):
    service_name: Optional[str] = None
    url: Optional[str] = None
    advanced_method: Optional[str] = None
    metrics_endpoint: Optional[str] = None

class ServiceResponse(BaseModel):
    id: int
    service_name: str
    url: str
    status: str
    health: str
    last_check: str
    warnings: int
    advanced_method: str
    metrics_endpoint: Optional[str] = None
