from dataclasses import dataclass
from datetime import datetime

from config import config


@dataclass
class Court:
    label: str
    venue: str
    resource_id: str

    @property
    def ignore(self) -> bool:
        return "mini" in self.label.lower()


@dataclass
class CourtSession:
    cost: str
    start_time: datetime
    end_time: datetime
    court: Court

    def to_dict(self):
        return {
            "venue": self.court.venue,
            "court": self.court.label,
            "cost": self.cost,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
        }

    @property
    def is_peak_time(self) -> bool:
        if self.is_weekday:
            return self.start_time.hour >= 18
        else:
            return self.start_time.hour >= 9

    @property
    def is_weekday(self) -> bool:
        return self.start_time.weekday() not in (5, 6)

    @property
    def booking_url(self) -> str:
        return f"{config['BASE_URL']}/{self.court.venue}/Booking/BookByDate#?date={self.start_time:%Y-%m-%d}&resourceId={self.court.resource_id}"

    def __str__(self):
        return f"{self.court.venue} {self.court.label} at {self.start_time:%H:%M} on {self.start_time:%A %d %B} (£{self.cost:.2f})"

    def prettify(self):
        return {
            "Venue": self.court.venue,
            "Court": self.court.label,
            "Date": f"{self.start_time:%A %d %B}",
            "Time": f"{self.start_time:%H:%M}",
            "Cost": f"£{self.cost:.2f}",
            "Booking Link": f'<a href="{self.booking_url}">Link to book</a>',
        }
