from fastapi import APIRouter, HTTPException
from typing import List
from schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse

router = APIRouter(prefix="/services", tags=["services"])

# Mock database - replace with real DB later
mock_services = {
    1: {
        "id": 1,
        "service_name": "Service 1",
        "url": "https://example.com",
        "status": "Running",
        "health": "96.45%",
        "last_check": "12 minutes ago",
        "warnings": 3,
        "advanced_method": "None",
        "metrics_endpoint": None
    },
    2: {
        "id": 2,
        "service_name": "Service 2 Healths",
        "url": "https://service2.example.com",
        "status": "Running",
        "health": "98.12%",
        "last_check": "5 minutes ago",
        "warnings": 1,
        "advanced_method": "Metrics endpoint",
        "metrics_endpoint": "/metrics"
    }
}

@router.get("", response_model=List[ServiceResponse])
def get_all_services():
    """Get all services"""
    return list(mock_services.values())

@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int):
    """Get specific service by ID"""
    if service_id not in mock_services:
        raise HTTPException(status_code=404, detail="Service not found")
    return mock_services[service_id]

@router.post("", response_model=ServiceResponse)
def create_service(service: ServiceCreate):
    """Create new service"""
    new_id = max(mock_services.keys()) + 1 if mock_services else 1
    new_service = {
        "id": new_id,
        **service.dict(),
        "status": "Running",
        "health": "100%",
        "last_check": "Just now",
        "warnings": 0
    }
    mock_services[new_id] = new_service
    return new_service

@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(service_id: int, service: ServiceUpdate):
    """Update service"""
    if service_id not in mock_services:
        raise HTTPException(status_code=404, detail="Service not found")
    
    updated = mock_services[service_id]
    update_data = service.dict(exclude_unset=True)
    updated.update(update_data)
    mock_services[service_id] = updated
    return updated

@router.delete("/{service_id}")
def delete_service(service_id: int):
    """Delete service"""
    if service_id not in mock_services:
        raise HTTPException(status_code=404, detail="Service not found")
    del mock_services[service_id]
    return {"message": f"Service {service_id} deleted"}
