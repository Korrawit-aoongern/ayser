import os
import time

import httpx


BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
ML_BASE_URL = os.getenv("ML_BASE_URL", "http://localhost:8010")


def _wait_for(url: str, timeout_seconds: int = 30) -> httpx.Response:
    deadline = time.time() + timeout_seconds
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=5)
            if response.status_code < 500:
                return response
        except Exception as exc:  # pragma: no cover - best effort retry
            last_error = exc
        time.sleep(1)
    raise AssertionError(f"Service not ready: {url}. Last error: {last_error}")


def test_backend_root_is_healthy() -> None:
    response = _wait_for(f"{BACKEND_BASE_URL}/")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("service") == "Ayser Backend"


def test_ml_service_evaluates_payload() -> None:
    response = _wait_for(f"{ML_BASE_URL}/")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("service") == "Ayser ML Service"

    evaluate_payload = {
        "service_id": 123,
        "feature_names": ["latency", "error_rate"],
        "samples": [
            [120.0, 0.02],
            [130.0, 0.03],
            [125.0, 0.01],
        ],
        "contamination": 0.05,
        "random_state": 42,
    }
    evaluate_response = httpx.post(
        f"{ML_BASE_URL}/evaluate",
        json=evaluate_payload,
        timeout=10,
    )
    assert evaluate_response.status_code == 200
    evaluate_body = evaluate_response.json()
    assert evaluate_body["service_id"] == 123
    assert evaluate_body["model"] == "IsolationForest"
