from fastapi import APIRouter, HTTPException, Depends
from ..schemas.health import HealthCheckResult, ServiceEvent, HealthMetrics
from .auth import require_user
import httpx
import time
import os
import asyncpg
from datetime import datetime


router = APIRouter(prefix="/health", tags=["health"])

# ---- DB ----
async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))


# ---- ROUTE ----
@router.get("/services/{service_id}")
async def get_service_health(service_id: int, user_id=Depends(require_user)):
    """Get service health data and recent events"""
    db = await get_db()
    try:
        service = await db.fetchrow(
            "SELECT service_id, service_name, service_url FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        health = await db.fetchrow(
            """
            SELECT health_id, service_id, availability, responsiveness, reliability, overall_score, checked_at
            FROM service_health
            WHERE service_id=$1
            ORDER BY checked_at DESC
            LIMIT 1
            """,
            service_id
        )

        events = await db.fetch(
            """
            SELECT event_level as type, event_message as message, detected_at
            FROM service_events
            WHERE service_id=$1
            ORDER BY detected_at DESC
            LIMIT 10
            """,
            service_id
        )

        return {
            "service": {
                "service_id": service["service_id"],
                "service_name": service["service_name"],
                "service_url": service["service_url"]
            },
            "health": dict(health) if health else {},
            "events": [dict(e) for e in events]
        }
    finally:
        await db.close()


@router.post("/services/{service_id}/check")
async def check_service(service_id: int, user_id=Depends(require_user)):
    """Perform black box monitoring check on service"""
    db = await get_db()
    try:
        service = await db.fetchrow(
            "SELECT service_id, service_url, check_type FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )

        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        url = service["service_url"]
        availability = "Down"
        responsiveness = "Slow"
        reliability = "Unstable"
        http_status = None
        latency_ms = None

        # Black box check - measure response time and status
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            latency_ms = (time.perf_counter() - start) * 1000
            availability = "Up"
            http_status = response.status_code
            
            # Determine responsiveness
            if latency_ms < 200:
                responsiveness = "Fast"
            elif latency_ms < 500:
                responsiveness = "Fast"
            else:
                responsiveness = "Slow"
                
        except httpx.TimeoutException:
            latency_ms = 10000  # Timeout threshold
            availability = "Down"
            responsiveness = "Slow"
        except Exception as e:
            latency_ms = None
            availability = "Down"
            responsiveness = "Slow"

        # Calculate overall score
        if availability == "Up":
            if latency_ms < 500:
                overall_score = 100
            elif latency_ms < 1000:
                overall_score = 80
            elif latency_ms < 2000:
                overall_score = 60
            else:
                overall_score = 40
        else:
            overall_score = 0

        # Reliability based on historical data
        recent_checks = await db.fetch(
            """
            SELECT availability FROM service_health
            WHERE service_id=$1
            ORDER BY checked_at DESC
            LIMIT 10
            """,
            service_id
        )
        
        up_count = sum(1 for check in recent_checks if check["availability"] == "Up")
        if recent_checks:
            uptime_percentage = (up_count / len(recent_checks)) * 100
            reliability = "Stable" if uptime_percentage >= 95 else "Unstable"
        else:
            reliability = "Unstable"

        # Insert health record
        health_id = await db.fetchval(
            """
            INSERT INTO service_health
            (service_id, availability, responsiveness, reliability, overall_score)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING health_id
            """,
            service_id,
            availability,
            responsiveness,
            reliability,
            overall_score
        )

        # Record event if service is down
        if availability == "Down":
            await db.execute(
                """
                INSERT INTO service_events
                (service_id, event_level, event_message)
                VALUES ($1, $2, $3)
                """,
                service_id,
                "ERROR",
                f"Service unreachable - {str(http_status) if http_status else 'Connection failed'}"
            )
        elif latency_ms and latency_ms > 2000:
            await db.execute(
                """
                INSERT INTO service_events
                (service_id, event_level, event_message)
                VALUES ($1, $2, $3)
                """,
                service_id,
                "WARNING",
                f"High latency detected: {latency_ms:.0f}ms"
            )

        # Insert latency metric
        if latency_ms is not None:
            await db.execute(
                """
                INSERT INTO service_metrics
                (service_id, metric_name, metric_value, metric_unit)
                VALUES ($1, $2, $3, $4)
                """,
                service_id,
                "response_latency",
                latency_ms,
                "ms"
            )

        return {
            "health_id": health_id,
            "service_id": service_id,
            "availability": availability,
            "responsiveness": responsiveness,
            "reliability": reliability,
            "latency_ms": latency_ms,
            "http_status": http_status,
            "overall_score": overall_score,
            "checked_at": datetime.utcnow().isoformat()
        }

    finally:
        await db.close()


@router.get("/services/{service_id}/history")
async def get_service_health_history(service_id: int, limit: int = 100, user_id=Depends(require_user)):
    """Get health check history for a service"""
    db = await get_db()
    try:
        # Verify user owns the service
        service = await db.fetchrow(
            "SELECT service_id FROM services WHERE service_id=$1 AND user_id=$2",
            service_id, user_id
        )
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        history = await db.fetch(
            """
            SELECT health_id, service_id, availability, responsiveness, reliability, overall_score, checked_at
            FROM service_health
            WHERE service_id=$1
            ORDER BY checked_at DESC
            LIMIT $2
            """,
            service_id, limit
        )

        return [dict(h) for h in history]
    finally:
        await db.close()

