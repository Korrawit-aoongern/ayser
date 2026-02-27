import pytest
from fastapi import HTTPException

from app.api import services
from app.schemas.service import ServiceCreate, ServiceUpdate


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
        return self.execute_results.pop(0)

    async def close(self):
        self.closed = True


@pytest.mark.anyio
async def test_get_all_services_returns_rows(monkeypatch):
    db = DummyDB(
        fetch_results=[
            [
                {
                    "service_id": 1,
                    "user_id": "u1",
                    "service_name": "API",
                    "service_url": "https://example.com",
                    "check_type": "url",
                    "created_at": None,
                    "availability": "Up",
                    "checked_at": None,
                }
            ]
        ]
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    result = await services.get_all_services(user_id="u1")

    assert len(result) == 1
    assert result[0]["service_name"] == "API"
    assert db.closed is True


@pytest.mark.anyio
async def test_get_service_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await services.get_service(service_id=99, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"
    assert db.closed is True


@pytest.mark.anyio
async def test_create_service_returns_created_record(monkeypatch):
    db = DummyDB(
        fetchval_results=[10],
        fetchrow_results=[
            {
                "service_id": 10,
                "user_id": "u1",
                "service_name": "Svc",
                "service_url": "https://svc.test",
                "check_type": "url",
                "created_at": None,
            }
        ],
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    payload = ServiceCreate(
        service_name="Svc",
        service_url="https://svc.test",
        check_type="url",
    )
    result = await services.create_service(payload, user_id="u1")

    assert result["service_id"] == 10
    assert result["service_name"] == "Svc"


@pytest.mark.anyio
async def test_create_service_empty_metrics_endpoint_defaults_to_metrics(monkeypatch):
    db = DummyDB(
        fetchval_results=[11],
        fetchrow_results=[
            {
                "service_id": 11,
                "user_id": "u1",
                "service_name": "Svc2",
                "service_url": "https://svc2.test",
                "check_type": "url_metrics",
                "metrics_endpoint": "/metrics",
                "created_at": None,
            }
        ],
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    payload = ServiceCreate(
        service_name="Svc2",
        service_url="https://svc2.test",
        check_type="url_metrics",
        metrics_endpoint="",
    )
    await services.create_service(payload, user_id="u1")

    insert_call = next(c for c in db.calls if c[0] == "fetchval")
    assert insert_call[2][4] == "/metrics"


@pytest.mark.anyio
async def test_update_service_empty_payload_returns_current(monkeypatch):
    db = DummyDB(
        fetchrow_results=[
            {"service_id": 10},  # existing check
            {
                "service_id": 10,
                "user_id": "u1",
                "service_name": "Svc",
                "service_url": "https://svc.test",
                "check_type": "url",
                "created_at": None,
            },  # no-op select
        ]
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    result = await services.update_service(
        service_id=10, service=ServiceUpdate(), user_id="u1"
    )

    assert result["service_id"] == 10
    assert result["service_url"] == "https://svc.test"


@pytest.mark.anyio
async def test_delete_service_not_found_raises_404(monkeypatch):
    db = DummyDB(execute_results=["DELETE 0"])

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await services.delete_service(service_id=99, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"


@pytest.mark.anyio
async def test_delete_all_services_returns_deleted_count(monkeypatch):
    db = DummyDB(fetchval_results=[3], execute_results=["DELETE 3"])

    async def fake_get_db():
        return db

    monkeypatch.setattr(services, "get_db", fake_get_db)

    result = await services.delete_all_services(user_id="u1")

    assert result["deleted_count"] == 3
    assert result["message"] == "All services deleted"
