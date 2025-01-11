"""
qr_utils.py
Generate and scan QR codes using qrcode, pyzbar, and OpenCV.
Also, send QR codes to an email address.
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
    """
    Generate a QR code for the account and (optionally) send it via email.
    """
    # Create QR code data
    qr_data = f"upi://pay?pa={account_number}&pn=User&am=0&cu=CAD"
    img = qrcode.make(qr_data)

    # Save the QR code locally
    filename = f"account_{account_number}.png"
    file_path = os.path.join(QR_CODES_DIR, filename)
    img.save(file_path)
    print(f"[INFO] QR code for account '{account_number}' saved to {file_path}")

    # Prompt for email address
    recipient_email = input("Enter email address to send QR code (or press Enter to skip): ").strip()
    if recipient_email:
        send_email(recipient_email, file_path, account_number)

    return file_path

def send_email(recipient_email, file_path, account_number):
    """
    Send an email with the QR code as an attachment using the dedicated email.
    """
    subject = f"QR Code for SmartPay-UPI Account {account_number}"
    body = f"""
    Dear User,

    Thank you for using SmartPay-UPI Canada. Please find attached the QR code for your account {account_number}.
    You can use this QR code to make secure transactions effortlessly.

    If you have any questions, feel free to contact us.

    Best regards,  
    SmartPay-UPI Team  
    (This is an automated message, please do not reply)
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(file_path)}",
    )
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        print(f"[SUCCESS] QR code sent to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

def scan_qr_code():
    """
    Scan a QR code using the laptop camera and decode transaction data.
    Automatically closes the camera after a successful scan.
    """
    if not OPENCV_AVAILABLE:
        print("[ERROR] OpenCV or pyzbar not installed. Cannot scan QR.")
        return None

    print("\n[INFO] Opening camera to scan QR code. Press 'q' to quit.")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not access the camera.")
        return None

    qr_data = None
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to capture frame from camera.")
            break

        decoded_objects = decode(frame)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8")
            print(f"[INFO] Decoded QR data: {qr_data}")
            break

        if qr_data:
            break

        cv2.imshow("Scan QR Code - Press 'q' to quit", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("[INFO] User canceled QR scanning.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if qr_data:
        return qr_data
    else:
        print("[ERROR] No QR code detected.")
        return None
