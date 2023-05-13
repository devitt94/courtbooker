from dataclasses import dataclass
import datetime
from contextlib import contextmanager
import itertools
import logging
import time

import geckodriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
)

import config

BASE_URL = "https://clubspark.lta.org.uk/"
LOOK_AHEAD_DAYS = 7
CLUBSPARK_DATE_FORMAT = "%A %d %B %Y"

@dataclass
class Court:
    label: str
    venue: str

@dataclass
class CourtSession:
    cost: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    court: Court

    def to_dict(self):
        return {
            "cost": self.cost,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "court": self.court.label,
            "venue": self.court.venue,
        }

    @property
    def is_peak_time(self) -> bool:
        return self.start_time.weekday() in {5, 6} or self.start_time.hour >= 18
    
    def __str__(self):
        return f"{self.venue} {self.court.label} at {self.start_time:%H:%M} on {self.start_time:%A %d %B} (£{self.cost:.2f})"

@contextmanager
def get_webdriver() -> webdriver.Firefox:
    try:
        logging.info("Initiliasing Firefox webdriver")
        geckodriver_autoinstaller.install()
        driver = webdriver.Firefox()
        yield driver
    except Exception as e:
        logging.exception(e)
    finally:
        logging.info("Closing driver")
        driver.quit()

def _get_dt_from_mins_and_date(mins: int, date: datetime.date) -> datetime.datetime:
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

    sessions = court_element.find_elements(By.CSS_SELECTOR, 'div.resource-session')
    
    for session in sessions:
        cost = session.get_attribute("data-session-cost")

        intervals = session.find_elements(By.CSS_SELECTOR, 'div.resource-interval')
        for interval in intervals:

            try:
                interval.find_element(By.CSS_SELECTOR, 'a.not-booked')
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
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    today = datetime.datetime.today().date()
    date_range = [
        today + datetime.timedelta(days=i) for i in range(LOOK_AHEAD_DAYS)
    ]

    print(date_range)
    logging.info(f"Checking availability for {date_range[0]:%A %d %B} to {date_range[-1]:%A %d %B}")

    available_courts: list[CourtSession] = []
    with get_webdriver() as driver:
        for venue, date in itertools.product(config.VENUES, date_range):
            venue_date_url = f"{BASE_URL}{venue}/Booking/BookByDate#?date={date:%Y-%m-%d}"
            logging.info(f"Getting availability for {venue} on {date:%A %d %B}...")
            driver.get(venue_date_url)
            time.sleep(3)

            courts = driver.find_elements(By.CSS_SELECTOR, 'div.resource')
            for court_element in courts:
                court = Court(
                    label=court_element.get_attribute("data-resource-name"),
                    venue=venue,
                )
                sessions = get_court_availability(court_element, court, date)

                available_courts.extend(sessions)

    
    logging.info(f"Found {len(available_courts)} available courts")
    




if __name__ == "__main__":
    main()
