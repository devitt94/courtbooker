from dataclasses import dataclass
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


@dataclass
class Court:
    venue: str
    label: Optional[str] = None
    resource_id: str = "unknown"

    @property
    def ignore(self) -> bool:
        return "mini" in self.label.lower()
