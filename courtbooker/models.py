import datetime
import enum
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    JSON,
    DateTime,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from courtbooker.database import Base


class DataSource(enum.Enum):
    BETTER = "better"
    CLUBSPARK = "clubspark"
    TOWERHAMLETS = "towerhamlets"


class Venue(Base):
    __tablename__ = "venue"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource))

    court_sessions: Mapped[list["CourtSession"]] = relationship(
        back_populates="venue"
    )
    name: Mapped[str] = mapped_column(String)

    __table_args__ = (
        UniqueConstraint("path", "data_source", name="path_source"),
    )

    __venue_path_to_name_mappings = {
        "hackney-parks/tennis-court-outdoor": "HaggerstonPark",
        "britannia-leisure-centre/tennis-court-outdoor": "ShoreditchPark",
        "islington-tennis-centre/tennis-court-outdoor": "IslingtonTennisCentreOutdoor",
        "islington-tennis-centre/tennis-court-indoor": "IslingtonTennisCentreIndoor",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.name = self.__venue_path_to_name_mappings[self.path]
        except KeyError:
            self.name = (
                self.path.split("/")[-1]
                .replace("-", " ")
                .title()
                .replace(" ", "")
            )

    def __str__(self):
        return f"{self.name} ({self.data_source})"


class CourtSession(Base):
    __tablename__ = "court_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[Optional[str]] = mapped_column(String)
    cost: Mapped[Decimal] = mapped_column(String)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    url: Mapped[str] = mapped_column(String)

    venue_id: Mapped[int] = mapped_column(ForeignKey("venue.id"))
    venue: Mapped["Venue"] = relationship(back_populates="court_sessions")

    task_id: Mapped[int] = mapped_column(ForeignKey("scrape_task.id"))
    task: Mapped["ScrapeTask"] = relationship(back_populates="court_sessions")

    def __str__(self) -> str:
        return f"{self.venue.name} {self.label} at {self.start_time:%H:%M} on {self.start_time:%A %d %B} (£{self.cost:.2f})"

    @property
    def is_peak_time(self) -> bool:
        return (self.start_time.hour > 17 and self.start_time.day < 5) or (
            self.start_time.hour > 9 and self.start_time.day >= 5
        )


class ScrapeTask(Base):
    __tablename__ = "scrape_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    time_started: Mapped[datetime.datetime] = mapped_column(DateTime)
    time_finished: Mapped[datetime.datetime] = mapped_column(DateTime)
    data_source: Mapped[DataSource] = mapped_column(Enum(DataSource))
    params: Mapped[dict] = mapped_column(JSON)
    court_sessions: Mapped[list["CourtSession"]] = relationship(
        back_populates="task"
    )
