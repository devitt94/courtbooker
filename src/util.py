from datetime import datetime

import models
import schemas
from database import DbSession


def get_court_sessions(
    task_ids: list[str] | None = None,
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
) -> list[schemas.CourtSession]:
    with DbSession(read_only=True) as db_session:
        if task_ids is None:
            task_ids: set[str] = {
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

        filters = [
            models.CourtSession.task_id.in_(task_ids),
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
