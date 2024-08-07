from datetime import datetime, timedelta
from typing import Optional

from courtbooker import models, schemas
from courtbooker.database import DbSession


def get_court_sessions(
    task_ids: list[str] | None = None,
    venues: list[str] | None = None,
    start_time_after: datetime | None = None,
    start_time_before: datetime | None = None,
    only_multiple_sessions: bool = False,
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

    if only_multiple_sessions:
        court_sessions = filter_out_single_sessions(court_sessions)

    return court_sessions


def get_venues() -> list[str]:
    with DbSession(read_only=True) as db_session:
        venues = (
            db_session.query(models.Venue).order_by(models.Venue.name).all()
        )

        venue_names = [venue.name for venue in venues]

    return venue_names


def get_latest_update_time() -> Optional[datetime]:
    with DbSession(read_only=True) as db_session:
        latest_update_time = (
            db_session.query(models.ScrapeTask.time_finished)
            .order_by(models.ScrapeTask.time_finished.desc())
            .first()
        )

        if latest_update_time is not None:
            latest_update_time = latest_update_time[0]

    return latest_update_time


def filter_out_single_sessions(
    court_sessions: list[schemas.CourtSession],
) -> list[schemas.CourtSession]:
    """
    Filter out court sessions that don't have another available session immediately before or after at the same venue.
    """
    # Group court sessions by venue and start time
    court_sessions_grouped = {}
    for court_session in court_sessions:
        key = (court_session.venue, court_session.start_time)
        if key not in court_sessions_grouped:
            court_sessions_grouped[key] = []
        court_sessions_grouped[key].append(court_session)

    keys_to_remove = set()
    for key in court_sessions_grouped.keys():
        hour_before, hour_after = (
            key[1] - timedelta(hours=1),
            key[1] + timedelta(hours=1),
        )
        key_before, key_after = (key[0], hour_before), (key[0], hour_after)
        if (
            key_before not in court_sessions_grouped
            and key_after not in court_sessions_grouped
        ):
            keys_to_remove.add(key)

    for key in keys_to_remove:
        del court_sessions_grouped[key]

    court_sessions = [
        court_session
        for court_sessions_list in court_sessions_grouped.values()
        for court_session in court_sessions_list
    ]

    return court_sessions
