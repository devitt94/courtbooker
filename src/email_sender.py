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


def send_email(sessions: list[CourtSession]):
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

    sender_email = config["SENDER_EMAIL"]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(config["RECEIVER_EMAILS"])
    message["Subject"] = SUBJECT
    message.attach(MIMEText("Peak-time available courts:", "plain"))
    message.attach(MIMEText(peak_sessions_table, "html"))
    message.attach(MIMEText("Non peak-time available courts:", "plain"))
    message.attach(MIMEText(non_peak_sessions_table, "html"))

    with smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(sender_email, config["SENDER_EMAIL_PASSWORD"])
        smtp.send_message(message)
