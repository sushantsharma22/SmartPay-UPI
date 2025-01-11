"""
notifications.py
Sends real-time email notifications for transactions, with improved indentation.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD, SMTP_SERVER, SMTP_PORT

def send_transaction_notification(recipient_email, subject, body):
    """Send a transaction-related notification email with consistent indentation."""
    if not recipient_email:
        return

    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())

        print(f"[SUCCESS] Notification email sent to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send notification email: {e}")
