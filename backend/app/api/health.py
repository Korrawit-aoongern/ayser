from fastapi import APIRouter, HTTPException, Depends
from .auth import require_user
import httpx
import time
import os
import asyncpg
from datetime import datetime, timezone


router = APIRouter(prefix="/health", tags=["health"])

LATENCY_BANDS_MS = [
    (200, 100, "Fast"),
    (500, 90, "Fast"),
    (1000, 75, "Moderate"),
    (2000, 55, "Slow"),
    (5000, 25, "Slow"),
]


# ---- DB ----
async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


def _score_availability(availability: str, http_status: int | None) -> float:
    if availability != "Up":
        return 0.0
    if http_status is None:
        return 85.0
    if 200 <= http_status < 400:
        return 100.0
    if 400 <= http_status < 500:
        return 70.0
    return 30.0


def _score_latency(latency_ms: float | None) -> tuple[float, str]:
    if latency_ms is None:
        return 10.0, "Unknown"
    for upper_bound, score, label in LATENCY_BANDS_MS:
        if latency_ms <= upper_bound:
            return float(score), label
    return 5.0, "Critical"


def _score_reliability(recent_checks: list[dict], current_availability: str) -> tuple[float, str, float]:
    availability_values = [c.get("availability") for c in recent_checks]
    availability_values.append(current_availability)
    total = len(availability_values)
    if total == 0:
        return 50.0, "Unknown", 0.0

    up_count = sum(1 for a in availability_values if a == "Up")
    uptime_percentage = (up_count / total) * 100.0

    if uptime_percentage >= 99:
        return 100.0, "Stable", uptime_percentage
    if uptime_percentage >= 95:
        return 85.0, "Mostly Stable", uptime_percentage
    if uptime_percentage >= 90:
        return 65.0, "Flaky", uptime_percentage
    return 35.0, "Unstable", uptime_percentage


def _to_ms(value: float, unit: str | None) -> float:
    normalized_unit = (unit or "").lower()
    if normalized_unit in {"s", "sec", "second", "seconds"}:
        return value * 1000.0
    return value


def _to_percent(value: float, unit: str | None) -> float:
    normalized_unit = (unit or "").lower()
    if normalized_unit == "ratio":
        return value * 100.0
    return value


def _evaluate_metric_risk(metric_rows: list[dict]) -> tuple[float | None, list[str]]:
    if not metric_rows:
        return None, []

    penalty = 0.0
    findings = []
    metric_map = {row["metric_name"]: row for row in metric_rows}

    p90 = metric_map.get("latency_p90")
    if p90:
        p90_ms = _to_ms(float(p90["metric_value"]), p90.get("metric_unit"))
        if p90_ms > 2000:
            penalty += 25
            findings.append("p90 latency is above 2000ms")
        elif p90_ms > 1000:
            penalty += 15
            findings.append("p90 latency is above 1000ms")
        elif p90_ms > 500:
            penalty += 8
            findings.append("p90 latency is above 500ms")

    p99 = metric_map.get("latency_p99")
    if p99:
        p99_ms = _to_ms(float(p99["metric_value"]), p99.get("metric_unit"))
        if p99_ms > 3000:
            penalty += 20
            findings.append("p99 latency is above 3000ms")
        elif p99_ms > 1500:
            penalty += 10
            findings.append("p99 latency is above 1500ms")

    error_rate = metric_map.get("error_rate")
    if error_rate:
        error_rate_pct = _to_percent(float(error_rate["metric_value"]), error_rate.get("metric_unit"))
        if error_rate_pct > 10:
            penalty += 40
            findings.append("error rate is above 10%")
        elif error_rate_pct > 5:
            penalty += 25
            findings.append("error rate is above 5%")
        elif error_rate_pct > 2:
            penalty += 10
            findings.append("error rate is above 2%")

    cpu = metric_map.get("cpu")
    if cpu and str(cpu.get("metric_unit", "")).lower() in {"%", "percent"}:
        cpu_pct = float(cpu["metric_value"])
        if cpu_pct > 90:
            penalty += 20
            findings.append("cpu usage is above 90%")
        elif cpu_pct > 80:
            penalty += 10
            findings.append("cpu usage is above 80%")

    metric_score = max(0.0, 100.0 - penalty)
    return metric_score, findings


def _compose_overall_score(
    availability: str,
    availability_score: float,
    latency_score: float,
    reliability_score: float,
    metric_score: float | None,
) -> float:
    if availability != "Up":
        return 0.0

    if metric_score is None:
        score = (
            (availability_score * 0.45)
            + (latency_score * 0.30)
            + (reliability_score * 0.25)
        )
    else:
        score = (
            (availability_score * 0.35)
            + (latency_score * 0.25)
            + (reliability_score * 0.20)
            + (metric_score * 0.20)
        )

    return round(max(0.0, min(100.0, score)), 2)


# ---- ROUTE ----
@router.get("/services/{service_id}")
async def get_service_health(service_id: int, user_id=Depends(require_user)):
    """Get service health data and recent events"""
    db = await get_db()
    try:
        try:
            service = await db.fetchrow(
                "SELECT service_id, service_name, service_url, check_type, metrics_endpoint, created_at FROM services WHERE service_id=$1 AND user_id=$2",
                service_id, user_id
            )
        except asyncpg.UndefinedColumnError:
            service = await db.fetchrow(
                "SELECT service_id, service_name, service_url, check_type, created_at FROM services WHERE service_id=$1 AND user_id=$2",
                service_id, user_id
            )
            if service:
                service = {**dict(service), "metrics_endpoint": None}

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

        latest_latency = await db.fetchval(
            """
            SELECT metric_value
            FROM service_metrics
            WHERE service_id=$1 AND metric_name='response_latency'
            ORDER BY collected_at DESC
            LIMIT 1
            """,
            service_id
        )

        http_status = None
        if health and health["availability"] == "Up":
            try:
                async with httpx.AsyncClient(timeout=5) as client:
                    response = await client.get(service["service_url"])
                http_status = response.status_code
            except Exception:
                http_status = None
        elif health and health["availability"] == "Down":
            http_status = 503

        events = await db.fetch(
            """
            SELECT event_id, service_id, event_level, event_message, detected_at
            FROM service_events
            WHERE service_id=$1
            ORDER BY detected_at DESC
            LIMIT 10
            """,
            service_id
        )

        latest_selected_metrics = await db.fetch(
            """
            SELECT t.metric_name, t.metric_value, t.metric_unit
            FROM (
                SELECT
                    metric_name,
                    metric_value,
                    metric_unit,
                    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY collected_at DESC) AS rn
                FROM service_metrics
                WHERE service_id=$1 AND metric_name = ANY($2::text[])
            ) t
            WHERE t.rn = 1
            """,
            service_id,
            ["cpu", "memory", "latency_p50", "latency_p90", "latency_p99", "error_rate"]
        )

        metric_rows = [dict(row) for row in latest_selected_metrics]
        metric_map = {row["metric_name"]: row for row in metric_rows}
        metric_score, metric_findings = _evaluate_metric_risk(metric_rows)

        health_payload = dict(health) if health else {
            "health_id": None,
            "service_id": service_id,
            "availability": "Unknown",
            "responsiveness": None,
            "reliability": None,
            "overall_score": None,
            "checked_at": None
        }
        health_payload["latency_ms"] = float(latest_latency) if latest_latency is not None else None
        health_payload["http_status"] = http_status
        health_payload["metrics"] = {
            "cpu": float(metric_map["cpu"]["metric_value"]) if "cpu" in metric_map else None,
            "memory": float(metric_map["memory"]["metric_value"]) if "memory" in metric_map else None,
            "p50": float(metric_map["latency_p50"]["metric_value"]) if "latency_p50" in metric_map else None,
            "p90": float(metric_map["latency_p90"]["metric_value"]) if "latency_p90" in metric_map else None,
            "p99": float(metric_map["latency_p99"]["metric_value"]) if "latency_p99" in metric_map else None,
            "cpu_unit": metric_map["cpu"]["metric_unit"] if "cpu" in metric_map else None,
            "memory_unit": metric_map["memory"]["metric_unit"] if "memory" in metric_map else None,
            "p50_unit": metric_map["latency_p50"]["metric_unit"] if "latency_p50" in metric_map else None,
            "p90_unit": metric_map["latency_p90"]["metric_unit"] if "latency_p90" in metric_map else None,
            "p99_unit": metric_map["latency_p99"]["metric_unit"] if "latency_p99" in metric_map else None,
            "error_rate": float(metric_map["error_rate"]["metric_value"]) if "error_rate" in metric_map else None,
            "error_rate_unit": metric_map["error_rate"]["metric_unit"] if "error_rate" in metric_map else None,
        }
        health_payload["metrics_evaluation"] = {
            "score": metric_score,
            "findings": metric_findings,
        }

        return {
            "service": {
                "service_id": service["service_id"],
                "service_name": service["service_name"],
                "service_url": service["service_url"],
                "check_type": service["check_type"],
                "metrics_endpoint": service.get("metrics_endpoint") if isinstance(service, dict) else service["metrics_endpoint"],
                "created_at": service["created_at"]
            },
            "health": health_payload,
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
        responsiveness = "Critical"
        reliability = "Unstable"
        http_status = None
        latency_ms = None

        # Black box check - measure response time and status
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
            latency_ms = (time.perf_counter() - start) * 1000
            http_status = response.status_code
            availability = "Up" if http_status < 500 else "Down"

        except httpx.TimeoutException:
            latency_ms = 10000
            availability = "Down"
        except Exception:
            latency_ms = None
            availability = "Down"

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

        latest_metrics_for_eval = await db.fetch(
            """
            SELECT t.metric_name, t.metric_value, t.metric_unit
            FROM (
                SELECT
                    metric_name,
                    metric_value,
                    metric_unit,
                    ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY collected_at DESC) AS rn
                FROM service_metrics
                WHERE service_id=$1 AND metric_name = ANY($2::text[])
            ) t
            WHERE t.rn = 1
            """,
            service_id,
            ["cpu", "latency_p90", "latency_p99", "error_rate"]
        )

        availability_score = _score_availability(availability, http_status)
        latency_score, responsiveness = _score_latency(latency_ms)
        reliability_score, reliability, uptime_percentage = _score_reliability(
            [dict(row) for row in recent_checks], availability
        )
        metric_score, metric_findings = _evaluate_metric_risk([dict(row) for row in latest_metrics_for_eval])

        overall_score = _compose_overall_score(
            availability=availability,
            availability_score=availability_score,
            latency_score=latency_score,
            reliability_score=reliability_score,
            metric_score=metric_score,
        )

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
        elif overall_score < 70:
            details = ", ".join(metric_findings[:2]) if metric_findings else "degraded health factors detected"
            await db.execute(
                """
                INSERT INTO service_events
                (service_id, event_level, event_message)
                VALUES ($1, $2, $3)
                """,
                service_id,
                "WARNING",
                f"Service health degraded (score={overall_score:.1f}, uptime={uptime_percentage:.1f}%, {details})"
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
            "score_breakdown": {
                "availability": availability_score,
                "latency": latency_score,
                "reliability": reliability_score,
                "metrics": metric_score,
            },
            "metric_findings": metric_findings,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    finally:
        await db.close()
