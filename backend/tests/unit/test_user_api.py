import pytest
from fastapi import HTTPException

from app.api import user


class DummyDB:
    def __init__(self, fetchrow_results=None, fetchval_results=None, execute_results=None):
        self.fetchrow_results = list(fetchrow_results or [])
        self.fetchval_results = list(fetchval_results or [])
        self.execute_results = list(execute_results or [])
        self.closed = False
        self.calls = []

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


@pytest.mark.anyio
async def test_get_current_user_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchrow_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await user.get_current_user(user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@pytest.mark.anyio
async def test_update_current_user_duplicate_email_raises_400(monkeypatch):
    db = DummyDB(fetchrow_results=[{"user_id": "other"}])

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)
    data = user.UserUpdateRequest(username="alice", email="alice@test.com")

    with pytest.raises(HTTPException) as exc:
        await user.update_current_user(data, user_id="u1")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email already registered"


@pytest.mark.anyio
async def test_update_current_user_success(monkeypatch):
    db = DummyDB(
        fetchrow_results=[
            None,  # duplicate email check
            {"user_id": "u1", "username": "alice", "email": "alice@test.com"},
        ]
    )

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)
    data = user.UserUpdateRequest(username="alice", email="alice@test.com")

    result = await user.update_current_user(data, user_id="u1")

    assert result["message"] == "User updated successfully"
    assert result["user"]["username"] == "alice"


@pytest.mark.anyio
async def test_change_password_wrong_old_password_raises_400(monkeypatch):
    db = DummyDB(fetchrow_results=[{"password_hash": "hashed"}])

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)
    monkeypatch.setattr(user, "verify_password", lambda old, hashed: False)

    data = user.PasswordChangeRequest(old_password="old", new_password="new")

    with pytest.raises(HTTPException) as exc:
        await user.change_password(data, user_id="u1")

    assert exc.value.status_code == 400
    assert exc.value.detail == "Old password is incorrect"


@pytest.mark.anyio
async def test_change_password_success_returns_force_logout(monkeypatch):
    db = DummyDB(fetchrow_results=[{"password_hash": "hashed"}], execute_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)
    monkeypatch.setattr(user, "verify_password", lambda old, hashed: True)
    monkeypatch.setattr(user, "hash_password", lambda value: "new-hash")

    data = user.PasswordChangeRequest(old_password="old", new_password="new")
    result = await user.change_password(data, user_id="u1")

    assert result["force_logout"] is True
    assert result["message"] == "Password changed successfully"
    execute_call = next(c for c in db.calls if c[0] == "execute")
    assert execute_call[2][0] == "new-hash"


@pytest.mark.anyio
async def test_delete_current_user_not_found_raises_404(monkeypatch):
    db = DummyDB(fetchval_results=[None])

    async def fake_get_db():
        return db

    monkeypatch.setattr(user, "get_db", fake_get_db)

    with pytest.raises(HTTPException) as exc:
        await user.delete_current_user(user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"
