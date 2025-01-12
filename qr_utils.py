"""
qr_utils.py
Generate and scan QR codes, with optional emailing.
"""

import os
import qrcode
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

try:
    import cv2
    from pyzbar.pyzbar import decode
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

from config import QR_CODES_DIR, SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD

def generate_qr_for_account(account_number):
    data = f"upi://pay?pa={account_number}&pn=User&am=0&cu=CAD"
    img = qrcode.make(data)

    filename = f"qr_{account_number}.png"
    filepath = os.path.join(QR_CODES_DIR, filename)
    img.save(filepath)
    print(f"[INFO] QR code saved: {filepath}")

    send_email_choice = input("Enter email to send this QR code (or press Enter to skip): ").strip()
    if send_email_choice:
        send_qr_email(send_email_choice, filepath, account_number)

def send_qr_email(recipient_email, filepath, account_number):
    subject = f"QR Code for Account {account_number}"
    body = (
        f"Hello,\n\n"
        f"Attached is your QR code for account {account_number}. "
        f"Use it to receive payments.\n\n"
        "Best,\nSmartPay-UPI"
    )

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(filepath, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(filepath)}"')
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        print(f"[SUCCESS] QR code emailed to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send QR code email: {e}")

def scan_qr_code():
    if not OPENCV_AVAILABLE:
        print("[ERROR] Camera scanning not available (missing opencv or pyzbar).")
        return None

    print("[INFO] Opening camera to scan. Press 'q' to quit.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not access camera.")
        return None

    qr_data = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        decoded = decode(frame)
        for obj in decoded:
            qr_data = obj.data.decode("utf-8")
            break

        if qr_data:
            break

        cv2.imshow("Scan QR Code", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Scan canceled by user.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if qr_data:
        return qr_data
    else:
        print("[ERROR] No QR code detected.")
        return None
