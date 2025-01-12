"""
user.py
Handles user registration, login, password reset, etc., with improved error feedback.
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
    if not username:
        print("[ERROR] Username cannot be empty.")
        return

    all_users = read_all_rows(USER_CSV)
    for user in all_users:
        if user["username"].lower() == username.lower():
            print(f"[ERROR] Username '{username}' already exists.")
            return

    full_name = input("Enter your full name: ").strip()
    if not full_name:
        print("[ERROR] Full name cannot be empty.")
        return

    email = input("Enter your email (for notifications & password reset): ").strip()
    password = input("Enter a password: ").strip()
    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("[ERROR] Passwords do not match.")
        return

    print("Select role:")
    print("1. Admin")
    print("2. Regular User")
    role_choice = input("Enter choice (1 or 2): ").strip()
    role = "admin" if role_choice == "1" else "user"

    hashed_pass = hash_password(password)
    append_row(USER_CSV, [username, hashed_pass, role, email, full_name, ""])

    # auto-gen a bank account
    acct_num = generate_random_account_number()
    bank_name = "UPI-Canada Bank"
    balance = "0.0"
    append_row(BANK_CSV, [username, acct_num, bank_name, balance])

    send_account_notification_email(email, full_name, acct_num)
    print("[SUCCESS] Registration complete!")
    print(f"Your bank account number is: {acct_num}")

    send_transaction_notification(
        recipient_email=email,
        subject="[SmartPay-UPI] Registration Successful",
        body=(
            f"Hello {full_name},\n\n"
            f"Thank you for registering at SmartPay-UPI.\n"
            f"Your new account number is {acct_num}.\n\n"
            "Best,\nSmartPay-UPI Team"
        )
    )

def send_account_notification_email(recipient_email, full_name, account_number):
    if not recipient_email:
        return

    subject = "Welcome to SmartPay-UPI! Your New Account"
    body = (
        f"Dear {full_name},\n\n"
        "Welcome to SmartPay-UPI. Below are your new bank account details:\n\n"
        f"Account Number: {account_number}\n\n"
        "Keep this info secure.\n\n"
        "Best,\nSmartPay-UPI Team"
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
        if user["username"].lower() == username.lower():
            if check_password(password, user["password"]):
                print(f"[SUCCESS] Welcome, {username}!")
                return {
                    "username": user["username"],
                    "role": user["role"],
                    "email": user.get("email", ""),
                    "full_name": user.get("full_name", "")
                }
            else:
                print("[ERROR] Invalid password.")
                return None

    print(f"[ERROR] User '{username}' not found.")
    return None

def reset_password():
    print("\n=== Reset Password ===")
    username = input("Enter your username: ").strip()
    if not username:
        print("[ERROR] Username is required.")
        return

    email_input = input("Enter your registered email: ").strip()

    all_users = read_all_rows(USER_CSV)
    user_rows = []
    user_found = False

    for u in all_users:
        if u["username"].lower() == username.lower() and u.get("email", "").lower() == email_input.lower():
            user_found = True
            new_password = "TempPass123"
            u["password"] = hash_password(new_password)
            send_email_password_reset(email_input, new_password, username)
        user_rows.append(u)

    if user_found:
        write_all_rows(USER_CSV, USER_HEADERS, user_rows)
        print("[INFO] A temporary password has been emailed to you.")
    else:
        print("[ERROR] Username/email combination not found.")

def send_email_password_reset(recipient_email, new_password, username):
    if not recipient_email:
        return

    subject = f"Password Reset for SmartPay-UPI: {username}"
    body = (
        f"Hi {username},\n\n"
        f"Your password has been reset. Use this temporary password: {new_password}\n\n"
        "Please log in and change it immediately.\n\n"
        "Best,\nSmartPay-UPI Team"
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
