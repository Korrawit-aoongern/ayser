from fastapi import APIRouter, Depends, HTTPException
import asyncpg
import os
import httpx
from urllib.parse import urlsplit, urlunsplit
try:
    from prometheus_client.parser import text_string_to_metric_families
except Exception:  # pragma: no cover - fallback for environments without dependency
    text_string_to_metric_families = None
from .auth import require_user

router = APIRouter(prefix="/metrics", tags=["metrics"])


async def get_db():
    return await asyncpg.connect(os.getenv("DATABASE_URL"), statement_cache_size=0)


def _normalize_path(path: str) -> str:
    segments = [segment for segment in (path or "").split("/") if segment]
    if not segments:
        return "/metrics"
    return "/" + "/".join(segments)


def build_metrics_url(service_url: str, metrics_endpoint: str = "/metrics") -> str:
    endpoint = (metrics_endpoint or "/metrics").strip()
    if not endpoint:
        endpoint = "/metrics"

    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        parsed_endpoint = urlsplit(endpoint)
        normalized_endpoint_path = _normalize_path(parsed_endpoint.path)
        return urlunsplit(
            (
                parsed_endpoint.scheme,
                parsed_endpoint.netloc,
                normalized_endpoint_path,
                "",
                "",
            )
        )

    parsed = urlsplit(service_url.strip())
    endpoint_path = _normalize_path(endpoint if endpoint.startswith("/") else f"/{endpoint}")
    return urlunsplit((parsed.scheme, parsed.netloc, endpoint_path, "", ""))


def extract_prometheus_metrics(raw_metrics: str):
    if text_string_to_metric_families is None:
        return []
    samples = []
    for family in text_string_to_metric_families(raw_metrics):
        for sample in family.samples:
            try:
                samples.append(
                    {
                        "name": sample.name,
                        "labels": sample.labels or {},
                        "value": float(sample.value),
                    }
                )
            except (TypeError, ValueError):
                continue

    def pick_first(candidates):
        for candidate in candidates:
            for sample in samples:
                if sample["name"] == candidate:
                    return sample
        return None

    selected = {}

    cpu_sample = pick_first(
        [
            "process_cpu_seconds_total",
            "container_cpu_usage_seconds_total",
            "node_cpu_seconds_total",
            "system_cpu_usage",
            "cpu_usage",
        ]
    )
    if cpu_sample:
        selected["cpu"] = (cpu_sample["value"], "seconds")

    memory_sample = pick_first(
        [
            "process_resident_memory_bytes",
            "process_virtual_memory_bytes",
            "node_memory_MemAvailable_bytes",
            "node_memory_MemTotal_bytes",
            "container_memory_usage_bytes",
            "memory_usage_bytes",
        ]
    )
    if memory_sample:
        selected["memory"] = (memory_sample["value"], "bytes")

    disk_sample = pick_first(
        [
            "node_filesystem_avail_bytes",
            "node_filesystem_size_bytes",
            "node_disk_read_bytes_total",
            "node_disk_written_bytes_total",
            "disk_usage_bytes",
        ]
    )
    if disk_sample:
        selected["disk"] = (disk_sample["value"], "bytes")

    network_sample = pick_first(
        [
            "node_network_receive_bytes_total",
            "node_network_transmit_bytes_total",
            "container_network_receive_bytes_total",
            "container_network_transmit_bytes_total",
            "network_receive_bytes_total",
            "network_transmit_bytes_total",
        ]
    )
    if network_sample:
        selected["network"] = (network_sample["value"], "bytes")

    for sample in samples:
        quantile = sample["labels"].get("quantile")
        if quantile not in {"0.5", "0.50", "0.9", "0.90", "0.99"}:
            continue
        metric_name = sample["name"].lower()
        if "latency" not in metric_name and "duration" not in metric_name:
            continue
        value = sample["value"]
        unit = "seconds"
        if metric_name.endswith("_seconds"):
            value = value * 1000
            unit = "ms"
        if quantile in {"0.5", "0.50"} and "latency_p50" not in selected:
            selected["latency_p50"] = (value, unit)
        elif quantile in {"0.9", "0.90"} and "latency_p90" not in selected:
            selected["latency_p90"] = (value, unit)
        elif quantile == "0.99" and "latency_p99" not in selected:
            selected["latency_p99"] = (value, unit)

    request_sample = pick_first(
        [
            "http_requests_total",
            "http_server_requests_seconds_count",
            "http_request_duration_seconds_count",
            "requests_total",
            "request_count",
        ]
    )
    if request_sample:
        selected["request_count"] = (request_sample["value"], "count")

    error_rate_sample = pick_first(["error_rate", "http_error_rate", "request_error_rate"])
    if error_rate_sample:
        selected["error_rate"] = (error_rate_sample["value"], "ratio")
    else:
        total_requests = 0.0
        error_requests = 0.0
        for sample in samples:
            name = sample["name"]
            if name not in {"http_requests_total", "requests_total"}:
                continue
            total_requests += sample["value"]
            status = str(sample["labels"].get("status") or sample["labels"].get("code") or "")
            if status.startswith("4") or status.startswith("5"):
                error_requests += sample["value"]
        if total_requests > 0:
            selected["error_rate"] = ((error_requests / total_requests) * 100, "%")

    return [
        {"metric_name": name, "metric_value": value, "metric_unit": unit}
        for name, (value, unit) in selected.items()
    ]


async def _fetch_service_for_scrape(db, service_id: int, user_id):
    try:
        service = await db.fetchrow(
            "SELECT service_id, service_url, check_type, metrics_endpoint FROM services WHERE service_id=$1 AND user_id=$2",
            service_id,
            user_id,
        )
    except asyncpg.UndefinedColumnError:
        service = await db.fetchrow(
            "SELECT service_id, service_url, check_type FROM services WHERE service_id=$1 AND user_id=$2",
            service_id,
            user_id,
        )
        if service:
            service = {**dict(service), "metrics_endpoint": "/metrics"}

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    return dict(service) if not isinstance(service, dict) else service


@router.post("/services/{service_id}/scrape")
async def scrape_service_metrics(service_id: int, user_id=Depends(require_user)):
    """Scrape Prometheus metrics for url_metrics services and store selected metrics."""
    db = await get_db()
    try:
        service = await _fetch_service_for_scrape(db, service_id, user_id)

        if service["check_type"] != "url_metrics":
            return {
                "service_id": service_id,
                "scraped": False,
                "skipped": True,
                "reason": "check_type is not url_metrics",
                "metrics_url": None,
                "metrics_scraped": 0,
            }

        metrics_url = build_metrics_url(service["service_url"], service.get("metrics_endpoint"))
        try:
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                metrics_response = await client.get(metrics_url)
                metrics_response.raise_for_status()

            parsed_metrics = extract_prometheus_metrics(metrics_response.text)
            for metric in parsed_metrics:
                await db.execute(
                    """
                    INSERT INTO service_metrics
                    (service_id, metric_name, metric_value, metric_unit)
                    VALUES ($1, $2, $3, $4)
                    """,
                    service_id,
                    metric["metric_name"],
                    metric["metric_value"],
                    metric["metric_unit"],
                )

            return {
                "service_id": service_id,
                "scraped": True,
                "skipped": False,
                "metrics_url": metrics_url,
                "metrics_scraped": len(parsed_metrics),
            }
        except Exception as exc:
            await db.execute(
                """
                INSERT INTO service_events
                (service_id, event_level, event_message)
                VALUES ($1, $2, $3)
                """,
                service_id,
                "WARNING",
                f"Metrics scrape failed: {str(exc)[:180]}",
            )
            return {
                "service_id": service_id,
                "scraped": False,
                "skipped": False,
                "metrics_url": metrics_url,
                "metrics_scraped": 0,
                "error": str(exc)[:180],
            }
    finally:
        await db.close()
