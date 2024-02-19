from datetime import datetime, timedelta

from fastapi import APIRouter

from courtbooker import schemas
from courtbooker.settings import app_settings
from courtbooker.util import get_court_sessions, get_latest_update_time
from courtbooker.worker import court_refresh_task, get_running_task_id

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


@router.get("/refresh-courts")
def refresh_courts():
    # Prevents the task from running multiple times
    current_task_id = get_running_task_id(
        "court_refresh_task"
    ) or get_running_task_id("scrape_sessions")
    if current_task_id:
        return {
            "message": "Task already running",
            "task_id": current_task_id,
        }

    last_update_time = get_latest_update_time()
    current_time = datetime.now()
    if last_update_time is not None:
        time_since_update = current_time - last_update_time
        if time_since_update < timedelta(
            minutes=app_settings.REFRESH_COOLDOWN_MINUTES
        ):
            return {
                "message": f"Task already ran less than {app_settings.REFRESH_COOLDOWN_MINUTES} minutes ago",
                "last_update_time": last_update_time,
            }

    task = court_refresh_task.delay()
    return {
        "message": "Success",
        "task_id": task.id,
    }
