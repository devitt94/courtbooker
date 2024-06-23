from datetime import datetime, timedelta

from courtbooker.settings import app_settings
from courtbooker.util import get_latest_update_time
from courtbooker.worker import court_refresh_task, get_running_task_id


def refresh_court_data():
    # Prevents the task from running multiple times
    current_task_id = get_running_task_id(
        "court_refresh_task"
    ) or get_running_task_id("scrape_sessions")
    if current_task_id:
        return {
            "message": "Refresh task already running",
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
                "message": f"Please wait at least {app_settings.REFRESH_COOLDOWN_MINUTES} minutes before refreshing",
                "last_update_time": last_update_time,
            }

    task = court_refresh_task.delay()
    return {
        "message": "Refresh task started",
        "task_id": task.id,
    }
