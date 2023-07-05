import datetime
import logging

import scraper.better as better
import scraper.clubspark as clubspark
from config import config
from email_sender import send_email


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    today = datetime.datetime.today().date()
    date_range = [
        today + datetime.timedelta(days=i)
        for i in range(config["LOOK_AHEAD_DAYS"])
    ]

    logging.debug(
        f"Checking availability for {date_range[0]:%A %d %B} to {date_range[-1]:%A %d %B}"
    )

    better_courts = better.get_all_available_sessions(
        config["BETTER_VENUES"], date_range
    )

    clubspark_courts = clubspark.get_all_available_sessions(
        config["CLUBSPARK_VENUES"], date_range
    )

    available_courts = clubspark_courts + better_courts

    logging.info(f"Found {len(available_courts)} available courts")

    if available_courts:
        send_email(available_courts)


if __name__ == "__main__":
    main()
