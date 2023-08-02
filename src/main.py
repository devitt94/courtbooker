import logging

from email_sender import (
    prepare_failure_email_body,
    prepare_success_email_body,
    send_email,
)
from settings import settings
from worker import get_all_available_sessions, write_courts_to_file


def main():
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    try:
        available_courts = get_all_available_sessions()

    except Exception as e:
        logging.error(f"Failed to get available courts: {e}")
        email_msg = prepare_failure_email_body(e)
        exit_code = 1
    else:
        logging.info(f"Found {len(available_courts)} available courts")
        email_msg = prepare_success_email_body(available_courts)
        exit_code = 0
    finally:
        logging.info(f"Writing courts to file in {settings.DATA_DIR}")
        write_courts_to_file(available_courts)
        logging.info("Sending email")
        send_email(email_msg)
        exit(exit_code)


if __name__ == "__main__":
    main()
