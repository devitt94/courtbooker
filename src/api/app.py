from datetime import datetime

import schemas
from database import Base, engine
from fastapi import FastAPI
from util import get_court_sessions
from worker import daily_update

Base.metadata.create_all(bind=engine)
app = FastAPI()


@app.get("/courts", response_model=schemas.CourtsResponse)
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


@app.get("/daily")
def run_daily():
    task = daily_update.delay()
    return {
        "message": "Success",
        "task_id": task.id,
    }
