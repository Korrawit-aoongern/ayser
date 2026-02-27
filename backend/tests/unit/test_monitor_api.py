import pytest

from app.api import monitor


@pytest.mark.anyio
async def test_monitor_service_runs_blackbox_and_graybox(monkeypatch):
    async def fake_check_service(service_id: int, user_id):
        return {"service_id": service_id, "availability": "Up"}

    async def fake_scrape(service_id: int, user_id):
        return {"service_id": service_id, "scraped": True, "skipped": False, "metrics_scraped": 4}

    monkeypatch.setattr(monitor, "check_service", fake_check_service)
    monkeypatch.setattr(monitor, "scrape_service_metrics", fake_scrape)

    result = await monitor.monitor_service(service_id=5, user_id="u1")

    assert result["service_id"] == 5
    assert result["blackbox"]["availability"] == "Up"
    assert result["graybox"]["scraped"] is True
    assert result["ran_graybox"] is True


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

    monkeypatch.setattr(monitor, "check_service", fake_check_service)
    monkeypatch.setattr(monitor, "scrape_service_metrics", fake_scrape)

    result = await monitor.monitor_service(service_id=6, user_id="u1")

    assert result["ran_graybox"] is False
    assert result["graybox"]["skipped"] is True
