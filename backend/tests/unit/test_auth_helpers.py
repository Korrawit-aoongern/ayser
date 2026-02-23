import pytest
import jwt
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from app.api import auth


def make_request_with_cookie(token: str | None) -> Request:
    cookie_header = f"access_token={token}".encode() if token else b""
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"cookie", cookie_header)] if token else [],
    }
    return Request(scope)


def test_hash_and_verify_password_success():
    password = "my-secret-password"
    hashed = auth.hash_password(password)

    assert hashed != password
    assert auth.verify_password(password, hashed) is True


def test_verify_password_fails_for_wrong_password():
    hashed = auth.hash_password("correct-password")

    assert auth.verify_password("wrong-password", hashed) is False


def test_create_jwt_contains_subject():
    token = auth.create_jwt("user-123")
    payload = jwt.decode(token, auth.JWT_SECRET, algorithms=[auth.JWT_ALGO])

    assert payload["sub"] == "user-123"
    assert "exp" in payload


def test_require_user_reads_bearer_credentials():
    token = auth.create_jwt("user-abc")
    request = make_request_with_cookie(None)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    user_id = auth.require_user(request=request, credentials=creds)

    assert user_id == "user-abc"


def test_require_user_reads_cookie_token():
    token = auth.create_jwt("cookie-user")
    request = make_request_with_cookie(token)

    user_id = auth.require_user(request=request, credentials=None)

    assert user_id == "cookie-user"


def test_require_user_without_token_raises_401():
    request = make_request_with_cookie(None)

    with pytest.raises(HTTPException) as exc:
        auth.require_user(request=request, credentials=None)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_require_user_with_invalid_token_raises_401():
    request = make_request_with_cookie("not-a-jwt")

    with pytest.raises(HTTPException) as exc:
        auth.require_user(request=request, credentials=None)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token"
