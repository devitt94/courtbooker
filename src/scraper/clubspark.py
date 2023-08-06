import datetime
import itertools
import logging
import time

from schemas import ClubsparkAvailableCourt, Court
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from settings import settings

from scraper.common import get_webdriver

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
    court: Court,
    date: datetime.date,
) -> list[ClubsparkAvailableCourt]:
    available_sessions = []

    sessions = court_element.find_elements(
        By.CSS_SELECTOR, 'div.resource-session[data-availability="true"]'
    )

    for session in sessions:
        try:
            cost = float(session.get_attribute("data-session-cost"))

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

                session = ClubsparkAvailableCourt(
                    cost=cost,
                    start_time=start_dt,
                    end_time=end_dt,
                    court=court,
                )

                logging.info(f"Found available court: {session}")
                available_sessions.append(session)

    return available_sessions


def get_all_available_sessions(
    venues: list[str],
    date_range: list[datetime.date],
) -> list[ClubsparkAvailableCourt]:
    available_courts: list[ClubsparkAvailableCourt] = []

    with get_webdriver() as driver:
        for date, venue in itertools.product(date_range, venues):
            venue_date_url = f"{settings.CLUBSPARK.BASE_URL}/{venue}/Booking/BookByDate#?date={date:%Y-%m-%d}"
            logging.debug(f"Fetching {venue_date_url}")
            driver.get(venue_date_url)
            time.sleep(PAGE_WAIT_SECONDS)

            courts = driver.find_elements(By.CSS_SELECTOR, "div.resource")
            for court_element in courts:
                court = Court(
                    label=court_element.get_attribute("data-resource-name"),
                    venue=venue,
                    resource_id=court_element.get_attribute(
                        "data-resource-id"
                    ),
                )

                if court.ignore:
                    continue

                sessions = get_court_availability(court_element, court, date)

                available_courts.extend(sessions)

    return available_courts
