import pytest
from fastapi import HTTPException

from app.api import ml


@pytest.mark.anyio
async def test_evaluate_service_returns_ml_result(monkeypatch):
    async def fake_eval(service_id: int, user_id):
        return {
            "ran": True,
            "result": {
                "latest": {"is_anomaly": False, "score": -0.21},
                "points_used": 80,
            },
        }

    monkeypatch.setattr(ml, "evaluate_service_anomaly", fake_eval)

    result = await ml.evaluate_service(service_id=7, user_id="u1")

    assert result["ran"] is True
    assert result["result"]["latest"]["is_anomaly"] is False


@pytest.mark.anyio
async def test_evaluate_service_not_found_raises_404(monkeypatch):
    async def fake_eval(service_id: int, user_id):
        return {"ran": False, "reason": "service-not-found"}

    monkeypatch.setattr(ml, "evaluate_service_anomaly", fake_eval)

    with pytest.raises(HTTPException) as exc:
        await ml.evaluate_service(service_id=999, user_id="u1")

    assert exc.value.status_code == 404
    assert exc.value.detail == "Service not found"
