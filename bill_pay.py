"""
bill_pay.py
Allows users to schedule recurring bill payments.
Provides a function to process due bills (run daily or triggered).
"""

import datetime
import time

from csv_db import read_all_rows, write_all_rows, append_row
from config import BILL_CSV, BILL_HEADERS, TRANS_CSV, TRANS_HEADERS
from bank import get_user_accounts
from notifications import send_transaction_notification
from transaction import check_daily_limit


def schedule_bill_payment(logged_in_user):
    """
    Schedule a new bill payment.
    The user chooses a bill name, amount, due date, frequency, etc.
    """
    username = logged_in_user["username"]
    bill_name = input("Enter the bill name (e.g., 'Phone Bill'): ").strip()
    amount_str = input("Enter the bill amount: ").strip()
    due_date_str = input("Enter due date (YYYY-MM-DD): ").strip()
    frequency = input("Enter frequency (monthly/weekly/once): ").lower().strip()

    try:
        amount = float(amount_str)
    except ValueError:
        print("[ERROR] Invalid amount.")
        return

    try:
        datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        print("[ERROR] Invalid date format. Use YYYY-MM-DD.")
        return

    # Add to CSV
    append_row(BILL_CSV, [username, bill_name, str(amount), due_date_str, frequency, "scheduled"])
    print("[SUCCESS] Bill scheduled successfully.")

def view_scheduled_bills(logged_in_user):
    """
    Display all scheduled bills for the user.
    """
    username = logged_in_user["username"]
    all_bills = read_all_rows(BILL_CSV)
    user_bills = [b for b in all_bills if b["username"].lower() == username.lower()]

    if not user_bills:
        print("[INFO] No scheduled bills.")
        return

    print("\n=== Your Scheduled Bills ===")
    for b in user_bills:
        print(
            f"Bill: {b['bill_name']} | Amount: ${b['amount']} | "
            f"Due: {b['due_date']} | Frequency: {b['frequency']} | Status: {b['status']}"
        )

def process_due_bills():
    """
    Run this function daily or via menu to auto-debit any due bills.
    Marks the bill as 'paid' or reschedules if frequency is monthly/weekly.
    """
    all_bills = read_all_rows(BILL_CSV)
    changed = False
    today = datetime.date.today()

    for bill in all_bills:
        due_date_str = bill["due_date"]
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except:
            continue

        if due_date <= today and bill["status"] == "scheduled":
            # Bill is due
            username = bill["username"]
            amount = float(bill["amount"])
            freq = bill["frequency"]

            user_accounts = get_user_accounts({"username": username})
            if not user_accounts:
                bill["status"] = "failed"
                continue

            from_account = user_accounts[0]["account_number"]

            # Check daily limit
            if not check_daily_limit(from_account, amount):
                bill["status"] = "failed"
                continue

            # Check balance
            balance = float(user_accounts[0]["balance"])
            if balance < amount:
                bill["status"] = "failed"
                continue

            # Deduct from user's bank CSV record
            all_accounts = read_all_rows("banks.csv")
            for row in all_accounts:
                if row["account_number"] == from_account:
                    row["balance"] = str(balance - amount)
                    break
            write_all_rows("banks.csv", ["username","account_number","bank_name","balance"], all_accounts)

            # Log transaction (append to transactions.csv)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            append_row(TRANS_CSV, [timestamp, from_account, "BILL_PAYMENT", str(amount), "COMPLETED", bill["bill_name"]])

            # Email notification (if we can get user email from user.csv)
            from user import read_all_rows as user_read_rows
            from config import USER_CSV
            all_users = user_read_rows(USER_CSV)
            user_email = None
            for u in all_users:
                if u["username"].lower() == username.lower():
                    user_email = u["email"]
                    break

            if user_email:
                send_transaction_notification(
                    recipient_email=user_email,
                    subject="[SmartPay-UPI] Bill Payment",
                    body=(
                        f"Hello {username},\n\n"
                        f"Your bill '{bill['bill_name']}' of ${amount} was successfully paid.\n"
                        "Best regards,\nSmartPay-UPI Team"
                    )
                )

            # Mark bill as paid or reschedule
            if freq in ("monthly","weekly"):
                # next due date
                if freq == "monthly":
                    next_date = due_date + datetime.timedelta(days=30)
                else:  # weekly
                    next_date = due_date + datetime.timedelta(days=7)

                bill["due_date"] = next_date.strftime("%Y-%m-%d")
                bill["status"] = "scheduled"
            else:
                bill["status"] = "paid"

            changed = True

    if changed:
        write_all_rows(BILL_CSV, BILL_HEADERS, all_bills)
        print("[INFO] Due bills processed successfully.")
    else:
        print("[INFO] No bills were due today.")
