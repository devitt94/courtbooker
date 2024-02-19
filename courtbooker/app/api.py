from datetime import datetime

from fastapi import APIRouter

from courtbooker import schemas
from courtbooker.util import get_court_sessions
from courtbooker.worker import daily_update

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.get("/courts", response_model=schemas.CourtsResponse)
def courts(
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
):
    court_sessions = get_court_sessions(
        venues=venues,
        start_time_after=start_time_after,
        start_time_before=start_time_before,
    )

    return {
        "message": "Success",
        "courts": court_sessions,
    }


@router.get("/daily")
def run_daily():
    task = daily_update.delay()
    return {
        "message": "Success",
        "task_id": task.id,
    }
