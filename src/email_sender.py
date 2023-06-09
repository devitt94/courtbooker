import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import config
from json2html import json2html
from models import CourtSession

SUBJECT = "Hackney Tennis Court Availability"

TABLE_ATTRIBUTES = (
    'style="width: 100%; border: none; font-size: 14px; text-align: left;"'
)


def prepare_success_email_body(sessions: list[CourtSession]) -> MIMEMultipart:
    peak_sessions = filter(lambda s: s.is_peak_time, sessions)
    non_peak_sessions = filter(lambda s: not s.is_peak_time, sessions)

    peak_sessions_table = json2html.convert(
        json=[session.prettify() for session in peak_sessions],
        escape=False,
        table_attributes=TABLE_ATTRIBUTES,
    )

    non_peak_sessions_table = json2html.convert(
        json=[session.prettify() for session in non_peak_sessions],
        escape=False,
        table_attributes=TABLE_ATTRIBUTES,
    )

    message = MIMEMultipart()

    message["From"] = config["SENDER_EMAIL"]
    message["To"] = ", ".join(config["RECEIVER_EMAILS"])
    message["Subject"] = SUBJECT
    message.attach(MIMEText("<h3>Peak-time available courts:</h3>", "html"))
    message.attach(MIMEText(peak_sessions_table, "html"))
    message.attach(
        MIMEText("<h3>Non peak-time available courts:</h3>", "html")
    )
    message.attach(MIMEText(non_peak_sessions_table, "html"))

    return message


def prepare_failure_email_body(e: Exception) -> MIMEMultipart:
    message = MIMEMultipart()

    message["From"] = config["SENDER_EMAIL"]
    message["To"] = config["SENDER_EMAIL"]
    message["Subject"] = f"{SUBJECT} - Failed"
    message.attach(
        MIMEText(
            f"Failed to get available courts due to the following exception:\n{e}",
            "plain",
        )
    )

    return message


def send_email(message: MIMEMultipart):
    with smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(config["SENDER_EMAIL"], config["SENDER_EMAIL_PASSWORD"])
        smtp.send_message(message)
