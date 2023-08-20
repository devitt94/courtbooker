import datetime
import logging
import os
from typing import Any

import geckodriver_autoinstaller
import models
import scraper.better
import scraper.clubspark
from celery import Celery
from celery.schedules import crontab
from database import DbSession
from email_sender import prepare_success_email_body, send_email
from settings import settings
from util import get_court_sessions

geckodriver_autoinstaller.install()
celery = Celery(__name__)
celery.conf.broker_url = os.environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379"
)
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)


SCRAPERS = {
    models.DataSource.BETTER: scraper.better,
    models.DataSource.CLUBSPARK: scraper.clubspark,
}


def _fetch_or_create_venues(
    data_source: models.DataSource,
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
    with DbSession(read_only=True) as db_session:
        venues_to_create = []
        for venue in venues:
            existing_venues = (
                db_session.query(models.Venue)
                .filter(
                    models.Venue.data_source == data_source,
                    models.Venue.path == venue,
                )
                .all()
            )

            if existing_venues:
                continue

            venues_to_create.append(
                models.Venue(
                    path=venue,
                    data_source=data_source,
                )
            )

    return [*existing_venues, *venues_to_create]


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
    venues = _fetch_or_create_venues(data_source, data_source_settings.VENUES)

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


@celery.task(name="send_emails")
def send_emails():
    email = prepare_success_email_body(get_court_sessions())
    send_email(email)


@celery.task(name="daily_update")
def daily_update():
    scrape_task_group = celery.group(
        [
            scrape_sessions.s(data_source.value)
            for data_source in models.DataSource
        ]
    )

    if scrape_task_group.ready() and scrape_task_group.successful():
        send_emails.delay()


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=7, minute=30),
        daily_update.s(),
    )
