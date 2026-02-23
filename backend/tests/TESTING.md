# Backend Testing Guide

## Purpose
This folder contains backend tests for Ayser.
Current focus is **unit tests**: test API module logic with mocked dependencies (DB/network), not real external services.

## Test Structure
- `backend/tests/unit/conftest.py`
  - Adds `backend/` to `sys.path` so imports like `from app.api import ...` work.
- `backend/tests/unit/test_auth_helpers.py`
  - Password hash/verify helpers.
  - JWT creation.
  - `require_user` behavior (bearer token, cookie token, invalid/missing token).
- `backend/tests/unit/test_services_api.py`
  - Services CRUD and delete-all route logic.
  - Not-found/ownership-style error paths.
- `backend/tests/unit/test_user_api.py`
  - User get/update/change-password/delete logic.
  - Duplicate email + wrong old password error paths.
- `backend/tests/unit/test_health_api.py`
  - Health routes with mocked HTTP client and DB.
  - Not-found paths, check timeout path, history ownership path.

## What "Unit Test" Means Here
- No real Postgres connection.
- No real HTTP calls to monitored services.
- No running FastAPI server required.
- Route functions are called directly and dependencies are mocked.

## How To Run
From repository root:

```bash
pytest -q backend/tests/unit
```
From ayser\backend:

```bash
pytest
```

Run one file:

```bash
pytest -q backend/tests/unit/test_services_api.py
```

## Current Coverage Checklist
- Auth helper behavior: `DONE`
- Services API core branches: `DONE`
- User API core branches: `DONE`
- Health API key branches: `DONE`
- Event API: `TODO` (currently route stub)
- Metrics API: `TODO` (currently route stub)
- Integration tests (real app + DB): `TODO`

## When Adding New Backend Logic
For each new route/function, add tests for:
1. Success path.
2. Common validation failure (`400`).
3. Not found / ownership failure (`404`).
4. Auth failure where relevant (`401`).
5. Side effects (DB write/event/log/metric) if applicable.

## Simple Test Template
```python
@pytest.mark.anyio
async def test_example_success(monkeypatch):
    db = DummyDB(...)

    async def fake_get_db():
        return db

    monkeypatch.setattr(module_under_test, "get_db", fake_get_db)

    result = await module_under_test.some_route(...)
    assert result["message"] == "ok"
```

## CI Note
In `.gitlab-ci.yml`, unit tests run when `backend/tests/unit` exists:

```sh
if [ -d backend/tests/unit ]; then pytest -q backend/tests/unit; else python3 -m compileall backend/app; fi
```

