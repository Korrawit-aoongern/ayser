import pytest
from fastapi import HTTPException

from app.api import health


class DummyDB:
    def __init__(
        self,
        fetch_results=None,
        fetchrow_results=None,
        fetchval_results=None,
        execute_results=None,
    ):
        self.fetch_results = list(fetch_results or [])
        self.fetchrow_results = list(fetchrow_results or [])
        self.fetchval_results = list(fetchval_results or [])
        self.execute_results = list(execute_results or [])
        self.closed = False
        self.calls = []

    async def fetch(self, query, *args):
        self.calls.append(("fetch", query, args))
        return self.fetch_results.pop(0)

    async def fetchrow(self, query, *args):
        self.calls.append(("fetchrow", query, args))
        return self.fetchrow_results.pop(0)

    async def fetchval(self, query, *args):
        self.calls.append(("fetchval", query, args))
        return self.fetchval_results.pop(0)

    async def execute(self, query, *args):
        self.calls.append(("execute", query, args))
        return self.execute_results.pop(0) if self.execute_results else None

    async def close(self):
        self.closed = True


class FakeResponse:
    def __init__(self, status_code: int):
        self.status_code = status_code


class FakeAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url):
        return FakeResponse(status_code=200)


@pytest.mark.anyio
async def test_get_service_health_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(health, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await health.get_service_health(service_id=1, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"


@pytest.mark.anyio
async def test_get_service_health_sets_http_status_for_up(monkeypatch):
    db = DummyDB(
        fetchrow_results=[
            {
                "service_id": 1,
                "service_name": "Svc",
                "service_url": "https://svc.test",
                "check_type": "url",
                "created_at": None,
            },
            {
                "health_id": 11,
                "service_id": 1,
                "availability": "Up",
                "responsiveness": "Fast",
                "reliability": "Stable",
                "overall_score": 100,
                "checked_at": None,
            },
        ],
        fetchval_results=[123.4],
        fetch_results=[[{"event_id": 1, "service_id": 1, "event_level": "INFO", "event_message": "ok", "detected_at": None}]],
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(health, "get_db", fake_get_db)
    monkeypatch.setattr(health.httpx, "AsyncClient", FakeAsyncClient)

    result = await health.get_service_health(service_id=1, user_id="u1")

    assert result["health"]["http_status"] == 200
    assert result["health"]["latency_ms"] == 123.4
    assert result["service"]["service_id"] == 1


@pytest.mark.anyio
async def test_check_service_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(health, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await health.check_service(service_id=1, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"


@pytest.mark.anyio
async def test_check_service_timeout_records_down_and_event(monkeypatch):
    class TimeoutClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url):
            raise health.httpx.TimeoutException("timeout")

    db = DummyDB(
        fetchrow_results=[{"service_id": 1, "service_url": "https://svc.test", "check_type": "url"}],
        fetch_results=[[]],  # recent checks
        fetchval_results=[77],  # health_id
        execute_results=[None, None],  # service_events insert + metrics insert
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(health, "get_db", fake_get_db)
    monkeypatch.setattr(health.httpx, "AsyncClient", TimeoutClient)

    result = await health.check_service(service_id=1, user_id="u1")

    assert result["availability"] == "Down"
    assert result["overall_score"] == 0
    assert result["latency_ms"] == 10000
    execute_calls = [c for c in db.calls if c[0] == "execute"]
    assert len(execute_calls) >= 2


@pytest.mark.anyio
async def test_get_service_health_history_requires_ownership(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(health, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await health.get_service_health_history(service_id=1, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"
