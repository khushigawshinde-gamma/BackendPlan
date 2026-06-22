import os
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_otp_email(receiver_email: str, otp: str):

    print("SMTP_EMAIL =", SMTP_EMAIL)
    print("Receiver =", receiver_email)

    message = MIMEMultipart()

    message["From"] = SMTP_EMAIL
    message["To"] = receiver_email
    message["Subject"] = "Planners.in Login OTP"

    body = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 5 minutes.

Thanks,
Planners.in Team
"""

    message.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)

    server.starttls()

    server.login(
        SMTP_EMAIL,
        SMTP_PASSWORD
    )

    server.send_message(message)

    print("Email sent successfully")

    server.quit()