from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CourtSession(BaseModel):
    venue: str
    label: Optional[str]
    cost: str
    start_time: datetime
    end_time: datetime
    url: str


class Task(BaseModel):
    time_started: datetime
    time_finished: datetime
    params: dict
    court_sessions: list[CourtSession]


class ScrapeTaskResponse(BaseModel):
    message: str
    task_id: str


class CourtsResponse(BaseModel):
    message: str
    courts: list[CourtSession]
