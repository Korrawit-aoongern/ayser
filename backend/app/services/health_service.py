import httpx
from datetime import datetime

async def check_service_health(service_id: int):
    """Check health status of a service by URL"""
    # Mock services mapping - replace with database later
    services = {
        1: "https://example.com",
        2: "https://service2.example.com"
    }
    
    url = services.get(service_id)
    if not url:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
        return {
            "service_id": service_id,
            "status": "Running" if response.status_code == 200 else "Down",
            "health": "100%" if response.status_code == 200 else "0%",
            "latency_ms": int(response.elapsed.total_seconds() * 1000),
            "response_code": response.status_code,
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "service_id": service_id,
            "status": "Down",
            "health": "0%",
            "latency_ms": 0,
            "response_code": 0,
            "last_check": datetime.now().isoformat()
        }
