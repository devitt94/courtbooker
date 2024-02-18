import datetime
import json
import logging
import os
from typing import Any

import geckodriver_autoinstaller
import models
from celery import Celery, group
from celery.schedules import crontab
from database import DbSession
from settings import settings

from courtbooker.scraper import better as better_scraper
from courtbooker.scraper import clubspark as clubspark_scraper

geckodriver_autoinstaller.install()
celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)


SCRAPERS = {
    models.DataSource.BETTER: better_scraper,
    models.DataSource.CLUBSPARK: clubspark_scraper,
}


def _fetch_or_create_venues(
    data_source: models.DataSource,
    venue_names: list[str],
) -> list[models.Venue]:
    """Fetches or creates the venues for a given data source

    Args:
        data_source (str): The data source to fetch venues for
        venues (list[str]): The venues to fetch

    Returns:
        list[models.Venue]: The venues for the given data source
    """
    data_source = models.DataSource(data_source)

    venues = []

    with DbSession(read_only=True) as db_session:
        for venue_name in venue_names:
            venue = (
                db_session.query(models.Venue)
                .filter(
                    models.Venue.data_source == data_source,
                    models.Venue.path == venue_name,
                )
                .one_or_none()
            )

            if venue is None:
                logging.info(f"Creating new venue {venue}")
                venue = models.Venue(
                    path=venue_name,
                    data_source=data_source,
                )

            venues.append(venue)

    return venues


def get_all_available_sessions(
    data_source: models.DataSource,
    look_ahead_days: int,
    venues: list[models.Venue],
    _scraper: Any,
) -> list[models.CourtSession]:
    today = datetime.datetime.today().date()
    date_range = [
        today + datetime.timedelta(days=i) for i in range(look_ahead_days)
    ]

    logging.info(
        f"Scraping {data_source} for {date_range[0]} to {date_range[-1]}"
    )

    courts = _scraper.get_available_sessions(venues, date_range)

    logging.info(f"Found {len(courts)} courts")

    return courts


@celery.task(name="scrape_sessions")
def scrape_sessions(data_source_name: str):
    start_time = datetime.datetime.now()

    data_source = models.DataSource(data_source_name)
    data_source_settings = settings.data_sources[data_source.value]
    logging.info(
        f"Settings:{json.dumps(data_source_settings.model_dump(), indent=2)}"
    )
    venues = _fetch_or_create_venues(data_source, data_source_settings.VENUES)

    if len(venues) != len(data_source_settings.VENUES):
        logging.warning(
            f"Could not find all venues for {data_source} {venues=}, {data_source_settings.VENUES=}"
        )

    logging.info(f"Scraping {data_source} for {len(venues)} venues")

    courts = get_all_available_sessions(
        data_source,
        look_ahead_days=data_source_settings.LOOK_AHEAD_DAYS,
        venues=venues,
        _scraper=SCRAPERS[data_source],
    )

    end_time = datetime.datetime.now()

    task = models.ScrapeTask(
        time_started=start_time,
        time_finished=end_time,
        data_source=data_source,
        params=settings.model_dump(),
        court_sessions=courts,
    )
    for court in courts:
        court.task = task

    with DbSession() as db_session:
        db_session.add_all(venues)
        db_session.add_all(courts)
        db_session.add(task)
        task_id = task.id

    return task_id


@celery.task(name="daily_update")
def daily_update():
    scrape_task_group = group(
        [
            scrape_sessions.s(data_source.value)
            for data_source in models.DataSource
        ]
    )

    scrape_task_group()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour="7", minute="30"),
        daily_update.s(),
    )
