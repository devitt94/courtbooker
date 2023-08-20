from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class CourtSession(BaseModel):
    venue: str
    label: Optional[str]
    cost: Decimal
    start_time: datetime
    end_time: datetime
    url: str

    @property
    def is_peak_time(self) -> bool:
        if self.is_weekday:
            return self.start_time.hour >= 18
        else:
            return self.start_time.hour >= 9

    @property
    def is_weekday(self) -> bool:
        return self.start_time.weekday() not in (5, 6)

    def prettify(self):
        return {
            "Venue": self.venue,
            "Court": self.label or "unknown",
            "Date": f"{self.start_time:%A %d %B}",
            "Time": f"{self.start_time:%H:%M}",
            "Cost": f"£{self.cost:.2f}",
            "Booking Link": f'<a href="{self.url}">Link to book</a>',
        }


class Task(BaseModel):
    time_started: datetime
    time_finished: datetime
    params: dict
    court_sessions: list[CourtSession]


class ScrapeTaskResponse(BaseModel):
    message: str
    tasks: dict[str, str]


class CourtsResponse(BaseModel):
    message: str
    courts: list[CourtSession]
