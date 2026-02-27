from fastapi import APIRouter, Depends

from .auth import require_user
from .health import check_service
from .metrics import scrape_service_metrics

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.post("/services/{service_id}/check")
async def monitor_service(service_id: int, user_id=Depends(require_user)):
    """Orchestrate blackbox check and conditional graybox scrape."""
    blackbox = await check_service(service_id=service_id, user_id=user_id)
    graybox = await scrape_service_metrics(service_id=service_id, user_id=user_id)

    return {
        "service_id": service_id,
        "blackbox": blackbox,
        "graybox": graybox,
        "ran_graybox": not graybox.get("skipped", False),
    }
