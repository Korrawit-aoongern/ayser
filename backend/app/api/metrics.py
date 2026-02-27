from urllib.parse import urlsplit, urlunsplit
try:
    from prometheus_client.parser import text_string_to_metric_families
except Exception:  # pragma: no cover - fallback for environments without dependency
    text_string_to_metric_families = None

def build_metrics_url(service_url: str, metrics_endpoint: str = "/metrics") -> str:
    endpoint = (metrics_endpoint or "/metrics").strip()
    if not endpoint:
        endpoint = "/metrics"

    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint

    parsed = urlsplit(service_url.strip())
    endpoint_path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
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
