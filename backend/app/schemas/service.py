from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ServiceCreate(BaseModel):
    service_name: str
    service_url: str
    check_type: str = "url"  # 'url' or 'url_metrics'

class ServiceUpdate(BaseModel):
    service_name: Optional[str] = None
    service_url: Optional[str] = None
    check_type: Optional[str] = None

class ServiceResponse(BaseModel):
    service_id: int
    user_id: Optional[str] = None
    service_name: str
    service_url: str
    check_type: str
    created_at: Optional[datetime] = None

class ServiceWithHealth(BaseModel):
    service_id: int
    service_name: str
    service_url: str
    check_type: str
    created_at: Optional[datetime] = None
    latest_health: Optional[dict] = None

