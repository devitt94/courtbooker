import datetime

from fastapi import FastAPI, Request
from models import CourtSession
from pydantic import BaseModel
from worker import scrape_sessions

app = FastAPI()

running_task = None


class CourtSessionResponse(BaseModel):
    venue: str
    court: str
    cost: float
    start_time: datetime.datetime
    end_time: datetime.datetime
    link: str


class Response(BaseModel):
    message: str
    courts: list[CourtSession]


@app.get("/")
def home(request: Request):
    global running_task
    courts = []
    if running_task is None:
        message = "Starting task"
        running_task = scrape_sessions.delay()
    elif running_task.ready():
        message = "Task finished"
        courts = running_task.get()
        running_task = None
    else:
        message = "Task running"

    return {
        "message": message,
        "courts": courts,
    }
