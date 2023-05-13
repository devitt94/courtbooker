from dataclasses import dataclass
from datetime import datetime


@dataclass
class Court:
    label: str
    venue: str

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

    def __str__(self):
        return f"{self.court.venue} {self.court.label} at {self.start_time:%H:%M} on {self.start_time:%A %d %B} (£{self.cost:.2f})"
