import pytest
from fastapi import HTTPException

from app.api import metrics


class DummyDB:
    def __init__(
        self,
        fetch_results=None,
        fetchrow_results=None,
        execute_results=None,
    ):
        self.fetch_results = list(fetch_results or [])
        self.fetchrow_results = list(fetchrow_results or [])
        self.execute_results = list(execute_results or [])
        self.closed = False
        self.calls = []

    async def fetch(self, query, *args):
        self.calls.append(("fetch", query, args))
        return self.fetch_results.pop(0)

    async def fetchrow(self, query, *args):
        self.calls.append(("fetchrow", query, args))
        return self.fetchrow_results.pop(0)

    async def execute(self, query, *args):
        self.calls.append(("execute", query, args))
        return self.execute_results.pop(0) if self.execute_results else None

    async def close(self):
        self.closed = True


class FakeResponse:
    def __init__(self, status_code: int, text: str = ""):
        self.status_code = status_code
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise metrics.httpx.HTTPStatusError(
                f"status={self.status_code}",
                request=None,
                response=None,
            )


def test_build_metrics_url_normalizes_relative_endpoint():
    url = metrics.build_metrics_url(
        "https://prometheus.demo.prometheus.io/query",
        " //a///b//metrics// ",
    )
    assert url == "https://prometheus.demo.prometheus.io/a/b/metrics"


def test_build_metrics_url_normalizes_absolute_endpoint():
    url = metrics.build_metrics_url(
        "https://ignored.example.com/path",
        "https://prometheus.demo.prometheus.io//x///metrics/?q=1",
    )
    assert url == "https://prometheus.demo.prometheus.io/x/metrics"


def test_build_metrics_url_defaults_to_metrics_for_empty_endpoint():
    url = metrics.build_metrics_url("https://svc.test/base", "   ")
    assert url == "https://svc.test/metrics"


def test_evaluate_scraped_metrics_healthy_when_no_risky_signals():
    evaluation = metrics.evaluate_scraped_metrics(
        [
            {"metric_name": "latency_p90", "metric_value": 120.0, "metric_unit": "ms"},
            {"metric_name": "error_rate", "metric_value": 1.0, "metric_unit": "%"},
        ]
    )
    assert evaluation["status"] == "Healthy"
    assert evaluation["score"] == 100.0
    assert evaluation["findings"] == []


def test_evaluate_scraped_metrics_critical_when_multiple_thresholds_breach():
    evaluation = metrics.evaluate_scraped_metrics(
        [
            {"metric_name": "latency_p90", "metric_value": 2100.0, "metric_unit": "ms"},
            {"metric_name": "latency_p99", "metric_value": 3.2, "metric_unit": "seconds"},
            {"metric_name": "error_rate", "metric_value": 12.0, "metric_unit": "%"},
        ]
    )
    assert evaluation["status"] == "Critical"
    assert evaluation["score"] == 15.0
    assert "p90 latency above 2000ms" in evaluation["findings"]
    assert "error rate above 10%" in evaluation["findings"]


@pytest.mark.anyio
async def test_scrape_service_metrics_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(metrics, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await metrics.scrape_service_metrics(service_id=1, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"


@pytest.mark.anyio
async def test_scrape_service_metrics_skips_for_non_url_metrics(monkeypatch):
    db = DummyDB(
        fetchrow_results=[
            {"service_id": 1, "service_url": "https://svc.test", "check_type": "url", "metrics_endpoint": "/metrics"}
        ]
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(metrics, "get_db", fake_get_db)

    result = await metrics.scrape_service_metrics(service_id=1, user_id="u1")

    assert result["skipped"] is True
    assert result["metrics_scraped"] == 0


@pytest.mark.anyio
async def test_scrape_service_metrics_inserts_selected_metrics(monkeypatch):
    class MetricsClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            return FakeResponse(status_code=200, text="# HELP metrics")

    db = DummyDB(
        fetchrow_results=[
            {
                "service_id": 1,
                "service_url": "https://svc.test",
                "check_type": "url_metrics",
                "metrics_endpoint": "/prom-metrics",
            }
        ],
        execute_results=[None] * 20,
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(metrics, "get_db", fake_get_db)
    monkeypatch.setattr(metrics.httpx, "AsyncClient", MetricsClient)
    monkeypatch.setattr(
        metrics,
        "extract_prometheus_metrics",
        lambda raw: [
            {"metric_name": "cpu", "metric_value": 10.0, "metric_unit": "seconds"},
            {"metric_name": "memory", "metric_value": 2048.0, "metric_unit": "bytes"},
            {"metric_name": "latency_p90", "metric_value": 125.0, "metric_unit": "ms"},
        ],
    )

    result = await metrics.scrape_service_metrics(service_id=1, user_id="u1")

    assert result["scraped"] is True
    assert result["metrics_url"] == "https://svc.test/prom-metrics"
    assert result["metrics_scraped"] == 3
    assert result["evaluation"]["status"] == "Healthy"

    inserted_metric_names = [
        call[2][1]
        for call in db.calls
        if call[0] == "execute" and "INSERT INTO service_metrics" in call[1]
    ]
    assert inserted_metric_names == ["cpu", "memory", "latency_p90"]
