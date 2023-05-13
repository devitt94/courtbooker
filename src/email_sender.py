import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import config
from json2html import json2html
from models import CourtSession

SUBJECT = "Hackney Tennis Court Availability"


def send_email(sessions: list[CourtSession]):
    available_courts_table = json2html.convert(
        json=[session.to_dict() for session in sessions]
    )
    sender_email = config["SENDER_EMAIL"]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = config["RECEIVER_EMAILS"][0]
    message["Subject"] = SUBJECT
    message.attach(MIMEText("Available courts:", "plain"))
    message.attach(MIMEText(available_courts_table, "html"))

    with smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(sender_email, config["SENDER_EMAIL_PASSWORD"])
        smtp.send_message(message)
