from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from config import config


@dataclass
class Court:
    venue: str
    label: str = "unknown court"
    resource_id: str = "unknown"

    @property
    def ignore(self) -> bool:
        return "mini" in self.label.lower()


@dataclass
class CourtSession:
    cost: Decimal
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

    @abstractmethod
    def get_booking_url(self) -> str:
        pass

    @property
    def is_weekday(self) -> bool:
        return self.start_time.weekday() not in (5, 6)

    @property
    def venue_display_name(self) -> str:
        return self.court.venue

    def __str__(self):
        return f"{self.venue_display_name} {self.court.label} at {self.start_time:%H:%M} on {self.start_time:%A %d %B} (£{self.cost:.2f})"

    def prettify(self):
        return {
            "Venue": self.venue_display_name,
            "Court": self.court.label,
            "Date": f"{self.start_time:%A %d %B}",
            "Time": f"{self.start_time:%H:%M}",
            "Cost": f"£{self.cost:.2f}",
            "Booking Link": f'<a href="{self.get_booking_url()}">Link to book</a>',
        }

    def __lt__(self, other):
        if self.start_time < other.start_time:
            return True
        elif self.start_time == other.start_time:
            return self.venue_display_name < other.venue_display_name
        else:
            return False

    def __eq__(self, other):
        return (
            self.start_time == other.start_time
            and self.venue_display_name == other.venue_display_name
            and self.court.label == other.court.label
        )


class ClubsparkCourtSession(CourtSession):
    def get_booking_url(self) -> str:
        return f"{config['CLUBSPARK_BASE_URL']}/{self.court.venue}/Booking/BookByDate#?date={self.start_time:%Y-%m-%d}"


class BetterCourtSession(CourtSession):
    def get_booking_url(self) -> str:
        return f"{config['BETTER_BASE_URL']}/{self.court.venue}/{self.start_time:%Y-%m-%d}/by-time"

    @property
    def venue_display_name(self) -> str:
        return {
            "hackney-parks/tennis-court-outdoor": "HaggerstonPark",
            "islington-tennis-centre/rosemary-gardens-tennis": "RosemaryGardens",
        }.get(self.court.venue, self.court.venue)
