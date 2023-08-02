import csv
import datetime

import scraper.better
import scraper.clubspark
from models import CourtSession
from settings import settings

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

        courts = _scraper.get_all_available_sessions(
            data_source_settings.VENUES, date_range
        )

        all_courts.extend(courts)

    return all_courts


def write_courts_to_file(courts: list[CourtSession]) -> None:
    output_file = settings.DATA_DIR / "output.csv"
    output_file.parent.mkdir(exist_ok=True)
    fieldnames = courts[0].to_dict().keys()
    with output_file.open("w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for court in courts:
            writer.writerow(court.to_dict())
