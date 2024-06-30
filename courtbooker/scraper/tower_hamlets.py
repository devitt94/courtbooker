import datetime
import itertools
import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from courtbooker import models
from courtbooker.scraper.common import get_webdriver
from courtbooker.settings import app_settings

PAGE_WAIT_SECONDS = 5

COURT_CSS_SELECTOR = "label.court"


def _format_url(venue: models.Venue, date: datetime.date) -> str:
    return f"{app_settings.TOWERHAMLETS.BASE_URL}/{venue.path}/{date.strftime('%Y-%m-%d')}"


def get_available_sessions(
    venues: list[models.Venue],
    date_range: list[datetime.date],
) -> list[models.CourtSession]:
    available_courts: list[models.CourtSession] = []

    with get_webdriver() as driver:
        logging.info(f"{venues=}")
        logging.info(f"{date_range=}")

        for date, venue in itertools.product(date_range, venues):
            logging.info(f"Checking availability for {venue} on {date}")
            url = _format_url(venue, date)
            driver.get(url)
            time.sleep(PAGE_WAIT_SECONDS)

            courts = driver.find_elements(By.CSS_SELECTOR, COURT_CSS_SELECTOR)

            for court in courts:
                try:
                    court_info = court.find_element(
                        By.CSS_SELECTOR, "input.bookable"
                    )
                except NoSuchElementException:
                    continue

                cost = float(court_info.get_attribute("data-price"))

                court_label = court.text.split("£")[0]
                try:
                    _, _, date_str, time_str = court_info.get_attribute(
                        "value"
                    ).split("_")
                except ValueError:
                    logging.warning(
                        f"Could not parse court time: {court_info.get_attribute('value')}"
                    )
                    continue

                start_time = datetime.datetime.strptime(
                    f"{date_str} {time_str}", "%Y-%m-%d %H:%M"
                )
                end_time = start_time + datetime.timedelta(hours=1)

                session = models.CourtSession(
                    venue=venue,
                    label=court_label,
                    start_time=start_time,
                    end_time=end_time,
                    cost=cost,
                    url=url,
                )
                logging.info(f"Found available court: {session}")
                available_courts.append(session)

    return available_courts
