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

MIN_POINTS = 5
WINDOW_SIZE = 100
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"
LLM_SYSTEM_INSTRUCTION = """System Instruction (LLM Role):
You are a monitoring advisor system.
Your task is to analyze anomaly detection results and generate a short event message for a service monitoring panel.

Rules:
Output must be concise.
Maximum 4-5 short lines.
Use simple, clear language.
Do not explain technical model details.
Do not mention algorithms (e.g., IsolationForest).
Focus only on operational meaning.
End with a short action recommendation.
No personality, no extra commentary.

Level criteria:
INFO: No anomaly or minor normal variation.
WARNING: Moderate deviation that may affect performance.
ERROR: Clear abnormal behavior or service degradation.
"""


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


def _extract_text_from_gemini_response(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    content = candidates[0].get("content") or {}
    parts = content.get("parts") or []
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "\n".join(text for text in texts if text).strip()


def _parse_level_and_message(text: str) -> tuple[str, str]:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    if not lines:
        return "WARNING", "Anomaly detected in service behavior.\nAction: Run a health check and inspect metrics."

    first = lines[0]
    first_upper = first.upper()
    start_idx = 0
    if first_upper.startswith("LEVEL: INFO"):
        level = "INFO"
        start_idx = 1
    elif first_upper.startswith("LEVEL: ERROR"):
        level = "ERROR"
        start_idx = 1
    elif first_upper.startswith("LEVEL: WARNING"):
        level = "WARNING"
        start_idx = 1
    else:
        level = "WARNING"

    content_lines = lines[start_idx:] if lines[start_idx:] else lines
    limited_lines = content_lines[:5]
    message = "\n".join(limited_lines)
    return level, message


def _is_valid_llm_message(message: str) -> bool:
    lines = [line.strip() for line in (message or "").splitlines() if line.strip()]
    if len(lines) < 2:
        return False
    if not any(line.upper().startswith("ACTION:") for line in lines):
        return False
    return True


def _fallback_anomaly_message(result: dict[str, Any]) -> tuple[str, str]:
    latest = result.get("latest") or {}
    score = float(latest.get("score", 0.0))
    top_features = result.get("top_features") or []
    if score < -0.65:
        level = "ERROR"
        summary = "Clear abnormal behavior detected."
    else:
        level = "WARNING"
        summary = "Unusual metric deviation detected."

    top_text = ", ".join(
        f"{item.get('name')}={float(item.get('value', 0.0)):.2f}" for item in top_features[:2]
    )
    lines = [
        summary,
        f"Signal score: {score:.4f}",
    ]
    if top_text:
        lines.append(f"Key signals: {top_text}")
    lines.append("Action: Check recent deployments and investigate service logs.")
    return level, "\n".join(lines[:5])


def _apply_level_gates(event_level: str, event_message: str, result: dict[str, Any]) -> tuple[str, str]:
    points_used = int(result.get("points_used", 0) or 0)
    anomaly_count = int(result.get("anomaly_count", 0) or 0)
    adjusted_level = event_level
    reasons: list[str] = []

    # Confidence gate by dataset size.
    if points_used < 20:
        if adjusted_level != "INFO":
            reasons.append("Low confidence: fewer than 20 data points.")
        adjusted_level = "INFO"
    elif points_used < 50 and adjusted_level == "ERROR":
        adjusted_level = "WARNING"
        reasons.append("Medium confidence: fewer than 50 data points.")

    # Persistence gate for ERROR.
    if adjusted_level == "ERROR" and anomaly_count < 2:
        adjusted_level = "WARNING"
        reasons.append("Single anomaly signal; waiting for persistence.")

    lines = [line.strip() for line in (event_message or "").splitlines() if line.strip()]
    action_line = next((line for line in lines if line.upper().startswith("ACTION:")), None)
    if not action_line:
        action_line = "Action: Run a health check and inspect recent metrics."

    body_lines = [
        line
        for line in lines
        if not line.upper().startswith("LEVEL:") and not line.upper().startswith("ACTION:")
    ]

    output_lines = body_lines[:3]
    if reasons:
        output_lines.append(f"Note: {' '.join(reasons)}")
    output_lines.append(action_line)

    return adjusted_level, "\n".join(output_lines[:5])


async def _generate_llm_anomaly_message(service_id: int, result: dict[str, Any]) -> tuple[str, str]:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash").strip()
    if not api_key:
        return _fallback_anomaly_message(result)

    latest = result.get("latest") or {}
    payload_summary = {
        "service_id": service_id,
        "latest": latest,
        "anomaly_count": result.get("anomaly_count"),
        "anomaly_ratio": result.get("anomaly_ratio"),
        "points_used": result.get("points_used"),
        "top_features": result.get("top_features") or [],
    }

    user_prompt = (
        f"{LLM_SYSTEM_INSTRUCTION}\n\n"
        "Input anomaly result (JSON):\n"
        f"{payload_summary}\n\n"
        "Generate event message now."
    )

    request_body = {
        "contents": [{"parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 260,
        },
    }
    endpoint = f"{GEMINI_API_BASE}/models/{model}:generateContent?key={api_key}"

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(endpoint, json=request_body)
            response.raise_for_status()
            response_payload = response.json()
        text = _extract_text_from_gemini_response(response_payload)
        if not text:
            return _fallback_anomaly_message(result)
        level, message = _parse_level_and_message(text)
        if not _is_valid_llm_message(message):
            return _fallback_anomaly_message(result)
        return level, message
    except Exception:
        return _fallback_anomaly_message(result)


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
            event_level, event_message = await _generate_llm_anomaly_message(service_id, result)
            event_level, event_message = _apply_level_gates(event_level, event_message, result)
            await _insert_ml_event(db, service_id, event_level, event_message)

        return {"ran": True, "result": result}
    finally:
        await db.close()
