import datetime
import itertools
import logging
import time
from decimal import Decimal

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from courtbooker import models
from courtbooker.scraper.common import get_webdriver
from courtbooker.settings import app_settings

PAGE_WAIT_SECONDS = 3


def _get_dt_from_mins_and_date(
    mins: int, date: datetime.date
) -> datetime.datetime:
    hour = mins // 60
    minute = mins % 60
    time = datetime.time(hour=hour, minute=minute)
    return datetime.datetime.combine(date, time)


def get_court_availability(
    court_element: WebElement,
    label: str,
    venue: models.Venue,
    date: datetime.date,
    url: str,
) -> list[models.CourtSession]:
    available_sessions = []

    sessions = court_element.find_elements(
        By.CSS_SELECTOR, 'div.resource-session[data-availability="true"]'
    )

    for session in sessions:
        try:
            cost = Decimal(session.get_attribute("data-session-cost"))

        except TypeError:
            logging.warning(f"Could not parse cost for session: {session}")
            continue

        intervals = session.find_elements(
            By.CSS_SELECTOR, "div.resource-interval"
        )
        for interval in intervals:
            try:
                interval.find_element(By.CSS_SELECTOR, "a.not-booked")
            except NoSuchElementException:
                continue
            else:
                start_dt = _get_dt_from_mins_and_date(
                    int(interval.get_attribute("data-system-start-time")),
                    date,
                )
                end_dt = _get_dt_from_mins_and_date(
                    int(interval.get_attribute("data-system-end-time")),
                    date,
                )

                session = models.CourtSession(
                    venue=venue,
                    label=label,
                    cost=cost,
                    start_time=start_dt,
                    end_time=end_dt,
                    url=url,
                )

                logging.info(f"Found available court: {session}")
                available_sessions.append(session)

    return available_sessions


def get_available_sessions(
    venues: list[models.Venue],
    date_range: list[datetime.date],
) -> list[models.CourtSession]:
    available_courts: list[models.CourtSession] = []

    with get_webdriver() as driver:
        logging.info(f"{venues=}, {type(venues)=}")
        logging.info(f"{date_range=}, {type(date_range)=}")
        for date, venue in itertools.product(date_range, venues):
            logging.info(f"Fetching court availability for {venue} on {date}")
            venue_date_url = f"{app_settings.CLUBSPARK.BASE_URL}/{venue.path}/Booking/BookByDate#?date={date:%Y-%m-%d}"
            logging.debug(f"Fetching {venue_date_url}")
            driver.get(venue_date_url)
            time.sleep(PAGE_WAIT_SECONDS)

            courts = driver.find_elements(By.CSS_SELECTOR, "div.resource")
            for court_element in courts:
                court_label = court_element.get_attribute("data-resource-name")

                if "mini" in court_label.lower():
                    continue

                sessions = get_court_availability(
                    court_element,
                    court_label,
                    venue,
                    date,
                    venue_date_url,
                )

                available_courts.extend(sessions)

    return available_courts
