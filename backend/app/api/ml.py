from fastapi import APIRouter, Depends, HTTPException

from .auth import require_user
from ..ml.pipeline import evaluate_service_anomaly

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/services/{service_id}/evaluate")
async def evaluate_service(service_id: int, user_id=Depends(require_user)):
    """Run per-service ML anomaly evaluation and return the latest result."""
    result = await evaluate_service_anomaly(service_id=service_id, user_id=user_id)
    if result.get("reason") == "service-not-found":
        raise HTTPException(status_code=404, detail="Service not found")
    return result
