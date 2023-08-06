import datetime
from decimal import Decimal
from typing import Optional

from database import Base
from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CourtSession(Base):
    __tablename__ = "court_session"

    id: Mapped[int] = mapped_column(primary_key=True)
    venue: Mapped[str] = mapped_column(String)
    label: Mapped[Optional[str]] = mapped_column(String)
    cost: Mapped[Decimal] = mapped_column(String)
    start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    url: Mapped[str] = mapped_column(String)
    task_id: Mapped[int] = mapped_column(ForeignKey("scrape_task.id"))
    task: Mapped["ScrapeTask"] = relationship(back_populates="court_sessions")


class ScrapeTask(Base):
    __tablename__ = "scrape_task"

    id: Mapped[int] = mapped_column(primary_key=True)
    time_started: Mapped[datetime.datetime] = mapped_column(DateTime)
    time_finished: Mapped[datetime.datetime] = mapped_column(DateTime)
    params: Mapped[dict] = mapped_column(JSON)
    court_sessions: Mapped[list["CourtSession"]] = relationship(
        back_populates="task"
    )
