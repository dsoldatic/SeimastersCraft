import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
 
if not GMAIL_USER or not GMAIL_PASS:
  raise RuntimeError("GMAIL_USER i GMAIL_PASS env varijable moraju biti postavljene")

def send_email(to_email: str, subject: str, body_plain: str, body_html: str):
    msg = MIMEMultipart("alternative")
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    part_plain = MIMEText(body_plain, "plain")
    part_html  = MIMEText(body_html,  "html")
    msg.attach(part_plain)
    msg.attach(part_html)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)