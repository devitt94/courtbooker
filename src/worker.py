import csv
import datetime
import logging
import os

import scraper.better
import scraper.clubspark
from celery import Celery
from models import CourtSession
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


def get_all_available_sessions() -> list[CourtSession]:
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
        courts = _scraper.get_all_available_sessions(
            data_source_settings.VENUES, date_range
        )

        logging.info(f"Found {len(courts)} courts")

        all_courts.extend(courts)

    return all_courts


def write_courts_to_file(courts: list[CourtSession]) -> None:
    output_file = settings.DATA_DIR / "output.csv"
    output_file.parent.mkdir(exist_ok=True)
    fieldnames = courts[0].to_dict().keys()

    logging.info(f"Writing {len(courts)} courts to {output_file.absolute()}")

    with output_file.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for court in courts:
            writer.writerow(court.to_dict())


@celery.task(name="scrape_sessions")
def scrape_sessions():
    available_courts = get_all_available_sessions()
    return [court.to_dict() for court in available_courts]
