from datetime import datetime

import models
import schemas
from database import Base, engine
from email_sender import prepare_success_email_body, send_email
from fastapi import FastAPI, Request
from util import get_court_sessions
from worker import scrape_sessions

Base.metadata.create_all(bind=engine)
app = FastAPI()


running_tasks: dict[str, str] = {}


@app.get("/scrape", response_model=schemas.ScrapeTaskResponse)
def scrape(request: Request):
    global running_tasks

    if running_tasks:
        return {
            "message": "ScrapeTasks already running",
            "tasks": running_tasks,
        }

    for data_source in models.DataSource:
        task = scrape_sessions.delay(data_source.value)
        running_tasks[data_source.value] = task.id

    return {"message": "Scrape tasks started", "tasks": running_tasks}


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


@app.get("/email")
def email():
    emails = prepare_success_email_body(get_court_sessions())
    send_email(emails)
