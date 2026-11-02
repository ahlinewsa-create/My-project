import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

user = os.environ.get("GMAIL_USER", "").strip()
password = os.environ.get("GMAIL_PASS", "").strip()
recipient = os.environ.get("TO_EMAIL", "").strip()
if not (user and password and recipient):
    raise SystemExit("Email not sent: configure GMAIL_USER, GMAIL_PASS and TO_EMAIL in repository Actions secrets.")
report = Path("reports/daily.md").read_text(encoding="utf-8")
msg = EmailMessage()
msg["Subject"] = "TaL 3D | Daily website report"
msg["From"] = user
msg["To"] = recipient
msg.set_content(report)
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context(), timeout=30) as smtp:
    smtp.login(user, password)
    smtp.send_message(msg)
print("Daily report email submitted to Gmail SMTP successfully.")
