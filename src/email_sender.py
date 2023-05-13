import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import config
from json2html import json2html
from models import CourtSession

SUBJECT = "Hackney Tennis Court Availability"

TABLE_ATTRIBUTES = 'style="width: 100%; border: none; font-size: 14px; text-align: left;"'


def send_email(sessions: list[CourtSession]):
    available_courts_table = json2html.convert(
        json=[session.prettify() for session in sessions],
        escape=False,
        table_attributes=TABLE_ATTRIBUTES,
    )

    with open("email_template.html", "w") as f:
        f.write(available_courts_table)
    
    sender_email = config["SENDER_EMAIL"]

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(config["RECEIVER_EMAILS"])
    message["Subject"] = SUBJECT
    message.attach(MIMEText("Available courts:", "plain"))
    message.attach(MIMEText(available_courts_table, "html"))

    with smtplib.SMTP(config["SMTP_SERVER"], config["SMTP_PORT"]) as smtp:
        smtp.starttls()
        smtp.login(sender_email, config["SENDER_EMAIL_PASSWORD"])
        smtp.send_message(message)
