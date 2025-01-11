"""
user.py
Handles registration, login, password reset, role, etc.
Phone is optional. Password can be simple.
Ensures 'role' is stored properly, fixing KeyError issues.
"""

import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from csv_db import read_all_rows, append_row, write_all_rows
from config import (
    USER_CSV, USER_HEADERS, USE_BCRYPT,
    SMTP_SERVER, SMTP_PORT,
    EMAIL_SENDER, EMAIL_PASSWORD,
    BANK_CSV
)
from notifications import send_transaction_notification

if USE_BCRYPT:
    import bcrypt
else:
    bcrypt = None

def hash_password(plain_password):
    if USE_BCRYPT and plain_password:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    else:
        return plain_password

def check_password(plain_password, hashed_password):
    if USE_BCRYPT and hashed_password:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    else:
        return plain_password == hashed_password

def generate_random_account_number(length=10):
    return ''.join(random.choices(string.digits, k=length))

def register_user():
    print("\n=== User Registration ===")
    username = input("Choose a username (unique): ").strip()

    # Make sure CSV is up to date (just in case)
    all_users = read_all_rows(USER_CSV)
    for user in all_users:
        if user["username"].lower() == username.lower():
            print("[ERROR] Username already exists.")
            return

    full_name = input("Enter your full name: ").strip()
    email = input("Enter your email (for notifications & password reset): ").strip()
    phone = input("Enter your phone number (optional, press Enter to skip): ").strip()

    password = input("Enter a password (no complexity requirement): ").strip()
    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("[ERROR] Passwords do not match.")
        return

    print("Select role:")
    print("1. Admin")
    print("2. Regular User")
    role_choice = input("Enter choice (1 or 2): ").strip()
    if role_choice == "1":
        role = "admin"
    else:
        role = "user"

    hashed_pass = hash_password(password)

    # Insert the new user row with 'role' explicitly
    append_row(USER_CSV, [username, hashed_pass, role, email, full_name, phone])

    # Generate bank account
    account_number = generate_random_account_number()
    bank_name = "UPI-Canada Bank"
    balance = "0.0"
    append_row(BANK_CSV, [username, account_number, bank_name, balance])

    send_account_notification_email(email, full_name, account_number)
    print("[SUCCESS] Registration complete. A new account has been created!")
    print(f"Your generated account number is: {account_number}")

    # Also send transaction-like notification
    send_transaction_notification(
        recipient_email=email,
        subject="[SmartPay-UPI] Registration Successful",
        body=(
            f"Hello {full_name},\n\n"
            "Thank you for registering at SmartPay-UPI Canada!\n"
            f"Your new account number is {account_number}.\n"
            "You can start using it for deposits, transfers, QR-based payments, and more.\n\n"
            "Best regards,\n"
            "SmartPay-UPI Team\n"
            "(This is an automated message, please do not reply)"
        )
    )

def send_account_notification_email(recipient_email, full_name, account_number):
    """Properly indented email body."""
    if not recipient_email:
        return

    subject = "Welcome to SmartPay-UPI! Your New Account Details"
    body = (
        f"Dear {full_name},\n\n"
        "Welcome to SmartPay-UPI Canada! We are excited to have you on board.\n\n"
        f"Your new account number is: {account_number}\n\n"
        "You can start using it immediately for secure transactions.\n"
        "Thank you for choosing our service, and if you have any questions,\n"
        "feel free to reach out at any time.\n\n"
        "Best regards,\n"
        "SmartPay-UPI Team\n"
        "(This is an automated message, please do not reply)"
    )

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

        print(f"[SUCCESS] Account notification email sent to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send notification email: {e}")

def login_user():
    print("\n=== User Login ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    all_users = read_all_rows(USER_CSV)
    for user in all_users:
        # Make sure we have all columns (role, etc.)
        # If 'role' is missing, default to 'user'
        user.setdefault("role", "user")

        if user["username"].lower() == username.lower():
            if check_password(password, user["password"]):
                print(f"[SUCCESS] Welcome, {username}!")
                return {
                    "username": user["username"],
                    "role": user["role"],
                    "email": user.get("email", ""),
                    "full_name": user.get("full_name", ""),
                    "phone": user.get("phone", "")
                }
            else:
                print("[ERROR] Invalid password.")
                return None

    print("[ERROR] User not found.")
    return None

def reset_password():
    print("\n=== Reset Password ===")
    username = input("Enter your username: ").strip()
    email_input = input("Enter your registered email: ").strip()

    all_users = read_all_rows(USER_CSV)
    user_rows = []
    user_found = False

    for u in all_users:
        u.setdefault("role", "user")  # Ensure role is present
        if u["username"].lower() == username.lower() and u.get("email", "").lower() == email_input.lower():
            user_found = True
            new_password = "TempPass123"
            u["password"] = hash_password(new_password)
            send_email_password_reset(email_input, new_password, u["username"])
        user_rows.append(u)

    if user_found:
        write_all_rows(USER_CSV, USER_HEADERS, user_rows)
        print("[INFO] A temporary password has been sent to your email.")
    else:
        print("[ERROR] Username/email combination not found.")

def send_email_password_reset(recipient_email, new_password, username):
    if not recipient_email:
        return

    subject = f"Password Reset for SmartPay-UPI Account: {username}"
    body = (
        f"Hi {username},\n\n"
        "A password reset was requested for your SmartPay-UPI Canada account.\n"
        f"Your new temporary password is: {new_password}\n\n"
        "Please log in and change this password immediately.\n\n"
        "Regards,\n"
        "SmartPay-UPI Team\n"
        "(This is an automated message, please do not reply)"
    )

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

        print(f"[SUCCESS] Password reset email sent to {recipient_email}.")
    except Exception as e:
        print(f"[ERROR] Failed to send password reset email: {e}")
