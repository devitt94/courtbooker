import datetime
import itertools
import logging
import time
from contextlib import contextmanager

import geckodriver_autoinstaller
from config import config
from email_sender import send_email
from models import Court, CourtSession
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

LOOK_AHEAD_DAYS = 7
PAGE_WAIT_SECONDS = 3


@contextmanager
def get_webdriver() -> webdriver.Firefox:
    try:
        logging.debug("Initiliasing Firefox webdriver")
        geckodriver_autoinstaller.install()
        driver = webdriver.Firefox()
        yield driver
    except Exception as e:
        logging.exception(e)
    finally:
        logging.debug("Closing driver")
        driver.quit()


def _get_dt_from_mins_and_date(
    mins: int, date: datetime.date
) -> datetime.datetime:
    hour = mins // 60
    minute = mins % 60
    time = datetime.time(hour=hour, minute=minute)
    return datetime.datetime.combine(date, time)


def get_court_availability(
    court_element: webdriver.remote.webelement.WebElement,
    court: Court,
    date: datetime.date,
) -> list[CourtSession]:
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

                session = CourtSession(
                    cost=cost,
                    start_time=start_dt,
                    end_time=end_dt,
                    court=court,
                )

                if session.is_peak_time:
                    logging.info(f"Found peak time session: {session}")
                    available_sessions.append(session)

    return available_sessions


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    today = datetime.datetime.today().date()
    date_range = [
        today + datetime.timedelta(days=i) for i in range(LOOK_AHEAD_DAYS)
    ]

    logging.debug(
        f"Checking availability for {date_range[0]:%A %d %B} to {date_range[-1]:%A %d %B}"
    )

    available_courts: list[CourtSession] = []
    with get_webdriver() as driver:
        for venue, date in itertools.product(config["VENUES"], date_range):
            venue_date_url = f"{config['BASE_URL']}/{venue}/Booking/BookByDate#?date={date:%Y-%m-%d}"
            logging.debug(f"Fetching {venue_date_url}")
            driver.get(venue_date_url)
            time.sleep(PAGE_WAIT_SECONDS)

            courts = driver.find_elements(By.CSS_SELECTOR, "div.resource")
            for court_element in courts:
                court = Court(
                    label=court_element.get_attribute("data-resource-name"),
                    venue=venue,
                )

                if court.ignore:
                    continue

                sessions = get_court_availability(court_element, court, date)

                available_courts.extend(sessions)

    logging.info(f"Found {len(available_courts)} available courts")

    if available_courts:
        send_email(available_courts)


if __name__ == "__main__":
    main()
