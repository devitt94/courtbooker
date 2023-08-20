import logging
from datetime import datetime

import models
import schemas
from database import Base, DbSession, engine
from fastapi import FastAPI, Request
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


def _get_court_sessions(
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
) -> list[schemas.CourtSession]:
    with DbSession(read_only=True) as db_session:
        latest_task_ids: set[str] = {
            task.id
            for task in (
                db_session.query(models.ScrapeTask)
                .distinct(models.ScrapeTask.data_source)
                .order_by(
                    models.ScrapeTask.data_source,
                    models.ScrapeTask.time_started.desc(),
                )
            )
        }
        logging.info(f"Latest task ids: {latest_task_ids}")

        filters = [
            models.CourtSession.task_id.in_(latest_task_ids),
        ]

        if venues:
            filters.append(models.Venue.name.in_(venues))

        if start_time_after:
            filters.append(models.CourtSession.start_time >= start_time_after)

        if start_time_before:
            filters.append(models.CourtSession.start_time <= start_time_before)

        query = db_session.query(models.CourtSession).join(
            models.CourtSession.venue
        )
        court_sessions = (
            query.filter(*filters)
            .order_by(
                models.CourtSession.start_time,
            )
            .all()
        )

        court_sessions = [
            schemas.CourtSession(
                venue=court_session.venue.name,
                label=court_session.label,
                start_time=court_session.start_time,
                end_time=court_session.end_time,
                cost=court_session.cost,
                url=court_session.url,
            )
            for court_session in court_sessions
        ]

    return court_sessions


@app.get("/courts", response_model=schemas.CourtsResponse)
def courts(
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
):
    court_sessions = _get_court_sessions(
        venues=venues,
        start_time_after=start_time_after,
        start_time_before=start_time_before,
    )

    return {
        "message": "Success",
        "courts": court_sessions,
    }
