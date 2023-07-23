import datetime
import logging

import scraper.better as better
import scraper.clubspark as clubspark
from email_sender import (
    prepare_failure_email_body,
    prepare_success_email_body,
    send_email,
)
from settings import settings


def main():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info(f"Running in debug mode: {settings.DEBUG=}")

    today = datetime.datetime.today().date()
    club_spark_date_range = [
        today + datetime.timedelta(days=i)
        for i in range(settings.CLUBSPARK.LOOK_AHEAD_DAYS)
    ]

    better_date_range = [
        today + datetime.timedelta(days=i)
        for i in range(settings.BETTER.LOOK_AHEAD_DAYS)
    ]

    try:
        better_courts = better.get_all_available_sessions(
            settings.BETTER.VENUES, better_date_range
        )

        clubspark_courts = clubspark.get_all_available_sessions(
            settings.CLUBSPARK.VENUES, club_spark_date_range
        )

        available_courts = sorted(clubspark_courts + better_courts)

    except Exception as e:
        logging.error(f"Failed to get available courts: {e}")
        email_msg = prepare_failure_email_body(e)
        exit_code = 1
    else:
        logging.info(f"Found {len(available_courts)} available courts")
        email_msg = prepare_success_email_body(available_courts)
        exit_code = 0
    finally:
        send_email(email_msg)
        exit(exit_code)


if __name__ == "__main__":
    main()
