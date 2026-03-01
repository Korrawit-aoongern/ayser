import pytest
from fastapi import BackgroundTasks

from app.api import monitor


@pytest.mark.anyio
async def test_monitor_service_runs_blackbox_and_graybox(monkeypatch):
    async def fake_check_service(service_id: int, user_id):
        return {"service_id": service_id, "availability": "Up"}

    async def fake_scrape(service_id: int, user_id):
        return {"service_id": service_id, "scraped": True, "skipped": False, "metrics_scraped": 4}

    async def fake_ml_eval(service_id: int, user_id):
        return {"ran": True, "result": {"latest": {"is_anomaly": False}}}

    monkeypatch.setattr(monitor, "check_service", fake_check_service)
    monkeypatch.setattr(monitor, "scrape_service_metrics", fake_scrape)
    monkeypatch.setattr(monitor, "evaluate_service_anomaly", fake_ml_eval)

    result = await monitor.monitor_service(service_id=5, user_id="u1", background_tasks=BackgroundTasks())

    assert result["service_id"] == 5
    assert result["blackbox"]["availability"] == "Up"
    assert result["graybox"]["scraped"] is True
    assert result["ran_graybox"] is True
    assert result["ml"]["queued"] is True
    assert result["ml"]["mode"] == "background-task"


@pytest.mark.anyio
async def test_monitor_service_marks_graybox_not_run_when_skipped(monkeypatch):
    async def fake_check_service(service_id: int, user_id):
        return {"service_id": service_id, "availability": "Up"}

    async def fake_scrape(service_id: int, user_id):
        return {
            "service_id": service_id,
            "scraped": False,
            "skipped": True,
            "reason": "check_type is not url_metrics",
            "metrics_scraped": 0,
        }

    async def fake_ml_eval(service_id: int, user_id):
        return {"ran": False, "reason": "insufficient-points"}

    monkeypatch.setattr(monitor, "check_service", fake_check_service)
    monkeypatch.setattr(monitor, "scrape_service_metrics", fake_scrape)
    monkeypatch.setattr(monitor, "evaluate_service_anomaly", fake_ml_eval)

    result = await monitor.monitor_service(service_id=6, user_id="u1", background_tasks=BackgroundTasks())

    assert result["ran_graybox"] is False
    assert result["graybox"]["skipped"] is True
    assert result["ml"]["queued"] is True
    assert result["ml"]["mode"] == "background-task"
