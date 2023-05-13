import datetime
import logging

import scraper
from config import config
from email_sender import send_email


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    today = datetime.datetime.today().date()
    date_range = [
        today + datetime.timedelta(days=i) for i in range(config["LOOK_AHEAD_DAYS"])
    ]

    logging.debug(
        f"Checking availability for {date_range[0]:%A %d %B} to {date_range[-1]:%A %d %B}"
    )

    available_courts = scraper.get_all_available_sessions(
        config["VENUES"], date_range
    )

    logging.info(f"Found {len(available_courts)} available courts")

    if available_courts:
        send_email(available_courts)


if __name__ == "__main__":
    main()
