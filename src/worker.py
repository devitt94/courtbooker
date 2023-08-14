import datetime
import logging
import os

import models
import scraper.better
import scraper.clubspark
from celery import Celery
from database import db_session
from settings import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)


SCRAPERS = {
    "better": scraper.better,
    "clubspark": scraper.clubspark,
}


class SqlAlchemyTask(celery.Task):
    """An abstract Celery Task that ensures that the connection the the
    database is closed on task completion"""

    abstract = True

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        db_session.remove()


def _fetch_or_create_venues(
    data_source: str,
    venues: list[str],
) -> list[models.Venue]:
    """Fetches or creates the venues for a given data source

    Args:
        data_source (str): The data source to fetch venues for
        venues (list[str]): The venues to fetch

    Returns:
        list[models.Venue]: The venues for the given data source
    """
    data_source = models.DataSource(data_source)
    new_venues = [
        models.Venue(path=venue, data_source=data_source) for venue in venues
    ]

    db_session.add_all(new_venues)
    db_session.commit()

    return new_venues


def get_all_available_sessions() -> list[models.CourtSession]:
    today = datetime.datetime.today().date()
    all_courts = []

    for data_source, _scraper in SCRAPERS.items():
        data_source_settings = settings.data_sources[data_source]

        date_range = [
            today + datetime.timedelta(days=i)
            for i in range(data_source_settings.LOOK_AHEAD_DAYS)
        ]

        logging.info(
            f"Scraping {data_source} for {date_range[0]} to {date_range[-1]}"
        )

        venues: list[models.Venue] = _fetch_or_create_venues(
            data_source, data_source_settings.VENUES
        )

        courts = _scraper.get_available_sessions(venues, date_range)

        logging.info(f"Found {len(courts)} courts")

        all_courts.extend(courts)

    return all_courts


@celery.task(name="scrape_sessions", base=SqlAlchemyTask)
def scrape_sessions():
    start_time = datetime.datetime.now()

    courts = get_all_available_sessions()
    for court in courts:
        db_session.add(court)

    end_time = datetime.datetime.now()

    task = models.ScrapeTask(
        time_started=start_time,
        time_finished=end_time,
        params=settings.model_dump(),
        court_sessions=courts,
    )

    db_session.add(task)
    db_session.commit()
