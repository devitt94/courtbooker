import datetime
import itertools
import logging
import time
from itertools import islice
from typing import Iterable

import lxml.html as lxhtml
import lxml.html.clean as clean
import models
from settings import settings

from scraper.common import get_webdriver

BEFORE_AVAILABILITY_TABLE_STRING = "browse by location"
AFTER_AVAILABILITY_TABLE_STRING = "shopping basket"
NUM_COLUMNS = 6
PAGE_WAIT_SECONDS = 4


def parse_start_end_time(value: str) -> tuple[int, int]:
    start_time, end_time = value.split("-")
    start_time = int(start_time.strip()[:2])
    end_time = int(end_time.strip()[:2])

    return start_time, end_time


def parse_cost(value: str) -> float:
    return round(float(value.strip().lstrip("£")), 2)


def parse_availability(value: str) -> int:
    try:
        num_available = int(value.split()[0].strip())
    except ValueError:
        num_available = 0
    return num_available


def batched(iterable: Iterable, n: int):
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch


def extract_lines_from_page_source(page_source: str) -> list[str]:
    """Extracts visible text from page source as list of strings"""

    ignore_tags = {"script", "noscript", "style"}

    cleaner = clean.Cleaner()
    content = cleaner.clean_html(page_source)

    doc = lxhtml.fromstring(content)

    reached_availability_table = False
    all_lines = []

    for elt in doc.iterdescendants():
        if elt.tag in ignore_tags:
            continue
        text = elt.text or ""
        tail = elt.tail or ""
        s = " ".join((text, tail)).strip()
        if s:
            if not reached_availability_table:
                if s.lower() == BEFORE_AVAILABILITY_TABLE_STRING:
                    reached_availability_table = True

            elif s.lower() == AFTER_AVAILABILITY_TABLE_STRING:
                break
            else:
                all_lines.append(s)

    return all_lines


def create_court_session(
    start_end_time: tuple[int, int],
    cost: float,
    venue: models.Venue,
    date: datetime.date,
    url: str,
    **kwargs,
) -> models.CourtSession:
    start_hour, end_hour = start_end_time
    start_time = datetime.datetime.combine(
        date, datetime.time(hour=start_hour)
    )
    end_time = datetime.datetime.combine(date, datetime.time(hour=end_hour))

    return models.CourtSession(
        venue=venue,
        label=None,
        cost=cost,
        start_time=start_time,
        end_time=end_time,
        url=url,
    )


def get_available_sessions(
    venues: list[models.Venue],
    date_range: list[datetime.date],
) -> list[models.CourtSession]:
    COLUMN_MAPPERS = [
        (0, "start_end_time", parse_start_end_time),
        (4, "cost", parse_cost),
        (5, "availability", parse_availability),
    ]

    available_courts: list[models.CourtSession] = []

    with get_webdriver() as browser:
        logging.info(f"{venues=}, {type(venues)=}")
        logging.info(f"{date_range=}, {type(date_range)=}")
        for date, venue in itertools.product(date_range, venues):
            url = f"{settings.BETTER.BASE_URL}/{venue.path}/{date:%Y-%m-%d}/by-time"

            logging.debug(f"Getting booking page {url=}")
            browser.get(url)
            time.sleep(PAGE_WAIT_SECONDS)

            logging.debug("Extracting page source")
            lines = extract_lines_from_page_source(browser.page_source)
            if len(lines) < NUM_COLUMNS:
                logging.debug(
                    f"No valid session lines found for {venue.name=} {date=}"
                )
                continue

            for batch in batched(lines, NUM_COLUMNS):
                court = {}
                for column, key, mapper in COLUMN_MAPPERS:
                    value = batch[column]
                    try:
                        value = mapper(value)
                    except Exception as e:
                        logging.error(
                            f"Failed to parse value {value} for {key} ({batch=})"
                        )
                        raise e

                    court[key] = value

                if court["availability"] > 0:
                    court_session = create_court_session(
                        date=date, venue=venue, url=url, **court
                    )

                    logging.info(f"Found available court: {court_session}")
                    available_courts.append(court_session)

    return available_courts
