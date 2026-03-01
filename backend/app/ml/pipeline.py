import os
from collections import defaultdict
from typing import Any

import asyncpg
import httpx

METRIC_FEATURES = [
    "error_rate",
    "response_latency",
    "latency_p50",
    "latency_p90",
    "latency_p99",
    "cpu",
    "memory",
]

MIN_POINTS = 50
WINDOW_SIZE = 100


async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


def _build_aligned_samples(raw_rows: list[dict], min_points: int, window_size: int) -> dict[str, Any]:
    metric_to_rn_values: dict[str, dict[int, float]] = defaultdict(dict)
    for row in raw_rows:
        metric_to_rn_values[row["metric_name"]][int(row["rn"])] = float(row["metric_value"])

    present_metrics = [name for name in METRIC_FEATURES if name in metric_to_rn_values]
    if len(present_metrics) < 2:
        return {"ok": False, "reason": "not-enough-metrics"}

    common_points = min(len(metric_to_rn_values[name]) for name in present_metrics)
    points = min(common_points, window_size)
    if points < min_points:
        return {"ok": False, "reason": "insufficient-points", "points": points}

    samples: list[list[float]] = []
    for rn in range(points, 0, -1):
        sample = []
        for metric_name in present_metrics:
            metric_values = metric_to_rn_values[metric_name]
            if rn not in metric_values:
                return {"ok": False, "reason": "sparse-ranks"}
            sample.append(metric_values[rn])
        samples.append(sample)

    return {
        "ok": True,
        "feature_names": present_metrics,
        "samples": samples,
        "points": points,
    }


async def _fetch_metric_rows(db, service_id: int, window_size: int) -> list[dict]:
    rows = await db.fetch(
        """
        SELECT metric_name, metric_value, rn
        FROM (
            SELECT
                metric_name,
                metric_value,
                ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY collected_at DESC) AS rn
            FROM service_metrics
            WHERE service_id=$1 AND metric_name = ANY($2::text[])
        ) t
        WHERE rn <= $3
        """,
        service_id,
        METRIC_FEATURES,
        window_size,
    )
    return [dict(row) for row in rows]


async def _insert_ml_event(db, service_id: int, event_level: str, message: str):
    await db.execute(
        """
        INSERT INTO service_events (service_id, event_level, event_message)
        VALUES ($1, $2, $3)
        """,
        service_id,
        event_level,
        message,
    )


async def evaluate_service_anomaly(service_id: int, user_id: str) -> dict[str, Any]:
    ml_service_url = os.getenv("ML_SERVICE_URL", "http://localhost:8010").rstrip("/")
    contamination = float(os.getenv("ML_IF_CONTAMINATION", "0.05"))
    min_points = int(os.getenv("ML_MIN_POINTS", str(MIN_POINTS)))
    window_size = int(os.getenv("ML_WINDOW_SIZE", str(WINDOW_SIZE)))

    db = await get_db()
    try:
        service = await db.fetchrow(
            "SELECT service_id FROM services WHERE service_id=$1 AND user_id=$2",
            service_id,
            user_id,
        )
        if not service:
            return {"ran": False, "reason": "service-not-found"}

        raw_rows = await _fetch_metric_rows(db, service_id, window_size)
        dataset = _build_aligned_samples(raw_rows, min_points=min_points, window_size=window_size)
        if not dataset["ok"]:
            return {"ran": False, "reason": dataset["reason"], "points": dataset.get("points", 0)}

        payload = {
            "service_id": service_id,
            "feature_names": dataset["feature_names"],
            "samples": dataset["samples"],
            "contamination": contamination,
            "random_state": 42,
        }

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(f"{ml_service_url}/evaluate", json=payload)
                response.raise_for_status()
                result = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response is not None else None
            response_preview = ""
            if exc.response is not None:
                response_preview = (exc.response.text or "")[:220]
            await _insert_ml_event(
                db,
                service_id,
                "WARNING",
                f"ML evaluation failed: upstream_status={status_code}, response={response_preview}",
            )
            return {
                "ran": False,
                "reason": "ml-service-http-error",
                "status_code": status_code,
                "response": response_preview,
            }
        except httpx.ConnectError as exc:
            await _insert_ml_event(
                db,
                service_id,
                "WARNING",
                f"ML evaluation skipped: connect error ({str(exc)[:120]})",
            )
            return {
                "ran": False,
                "reason": "ml-service-connect-error",
                "detail": str(exc)[:220],
            }
        except httpx.TimeoutException as exc:
            await _insert_ml_event(
                db,
                service_id,
                "WARNING",
                f"ML evaluation skipped: timeout ({str(exc)[:120]})",
            )
            return {
                "ran": False,
                "reason": "ml-service-timeout",
                "detail": str(exc)[:220],
            }
        except Exception as exc:
            await _insert_ml_event(
                db,
                service_id,
                "WARNING",
                f"ML evaluation skipped: service unavailable ({str(exc)[:120]})",
            )
            return {
                "ran": False,
                "reason": "ml-service-unavailable",
                "error_type": type(exc).__name__,
                "detail": str(exc)[:220],
            }

        latest = result.get("latest", {})
        if latest.get("is_anomaly"):
            top_features = result.get("top_features") or []
            top_text = ", ".join(
                f"{item['name']}={item['value']:.2f}" for item in top_features[:2] if "value" in item
            )
            message = (
                f"ML anomaly detected (Isolation Forest, score={latest.get('score', 0):.4f}, "
                f"points={result.get('points_used', 0)})"
            )
            if top_text:
                message = f"{message}: {top_text}"
            await _insert_ml_event(db, service_id, "WARNING", message)

        return {"ran": True, "result": result}
    finally:
        await db.close()
