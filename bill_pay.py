"""
bill_pay.py
Allows scheduling and processing of bills.
Now includes a reassign_or_remove_bills function for partial dependency handling.
"""

import datetime
import time

from csv_db import read_all_rows, write_all_rows, append_row
from config import BILL_CSV, BILL_HEADERS, TRANS_CSV, TRANS_HEADERS, BANK_CSV
from notifications import send_transaction_notification
from transaction import check_daily_limit
from csv_db import read_all_rows as csv_read, write_all_rows as csv_write

def schedule_bill_payment(logged_in_user):
    username = logged_in_user["username"]
    bill_name = input("Enter bill name: ").strip()
    amount_str = input("Enter bill amount (numeric): ").strip()
    due_date_str = input("Enter due date (YYYY-MM-DD): ").strip()
    frequency = input("Enter frequency (monthly/weekly/once): ").strip().lower()

    try:
        amount = float(amount_str)
    except ValueError:
        print("[ERROR] Invalid amount. Use numbers only.")
        return

    try:
        datetime.datetime.strptime(due_date_str, "%Y-%m-%d")
    except ValueError:
        print("[ERROR] Invalid date format. Use YYYY-MM-DD.")
        return

    append_row(BILL_CSV, [username, bill_name, str(amount), due_date_str, frequency, "scheduled"])
    print("[SUCCESS] Bill scheduled successfully.")

def view_scheduled_bills(logged_in_user):
    username = logged_in_user["username"]
    all_bills = read_all_rows(BILL_CSV)
    user_bills = [b for b in all_bills if b["username"].lower() == username.lower()]

    if not user_bills:
        print("[INFO] No scheduled bills found.")
        return

    print("\n=== Your Scheduled Bills ===")
    for b in user_bills:
        print(
            f"Bill: {b['bill_name']} | Amount: ${b['amount']} | "
            f"Due: {b['due_date']} | Frequency: {b['frequency']} | Status: {b['status']}"
        )

def process_due_bills():
    all_bills = csv_read(BILL_CSV)
    changed = False
    today = datetime.date.today()

    for bill in all_bills:
        due_date_str = bill["due_date"]
        try:
            due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
        except:
            continue

        if due_date <= today and bill["status"] == "scheduled":
            username = bill["username"]
            amount = float(bill["amount"])
            freq = bill["frequency"]

            # We'll assume the user has at least 1 account => get the first
            from bank import get_user_accounts
            user_accts = get_user_accounts({"username": username})
            if not user_accts:
                bill["status"] = "failed"
                continue

            from_account = user_accts[0]["account_number"]

            if not check_daily_limit(from_account, amount):
                bill["status"] = "failed"
                continue

            # check balance
            all_bank = csv_read(BANK_CSV)
            user_acc_data = None
            for acc in all_bank:
                if acc["account_number"] == from_account:
                    user_acc_data = acc
                    break

            if not user_acc_data:
                bill["status"] = "failed"
                continue

            balance = float(user_acc_data["balance"])
            if balance < amount:
                bill["status"] = "failed"
                continue

            # deduct
            user_acc_data["balance"] = str(balance - amount)
            csv_write(BANK_CSV, ["username","account_number","bank_name","balance"], all_bank)

            # log transaction
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            trans_rows = csv_read(TRANS_CSV)
            new_tx = {
                "timestamp": timestamp,
                "from_account": from_account,
                "to_account": "BILL_PAYMENT",
                "amount": str(amount),
                "status": "COMPLETED",
                "category": bill["bill_name"]
            }
            trans_rows.append(new_tx)
            csv_write(TRANS_CSV, TRANS_HEADERS, trans_rows)

            # notify
            from user import read_all_rows as user_read
            from config import USER_CSV
            all_users = user_read(USER_CSV)
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
                        f"Your bill '{bill['bill_name']}' of ${amount} was paid.\n"
                        "Regards,\nSmartPay-UPI"
                    )
                )

            # reschedule or finalize
            if freq == "monthly":
                next_date = due_date + datetime.timedelta(days=30)
                bill["due_date"] = next_date.strftime("%Y-%m-%d")
                bill["status"] = "scheduled"
            elif freq == "weekly":
                next_date = due_date + datetime.timedelta(days=7)
                bill["due_date"] = next_date.strftime("%Y-%m-%d")
                bill["status"] = "scheduled"
            else:
                bill["status"] = "paid"

            changed = True

    if changed:
        csv_write(BILL_CSV, BILL_HEADERS, all_bills)
        print("[INFO] Due bills processed.")
    else:
        print("[INFO] No bills were due today.")

def reassign_or_remove_bills(username, deleted_account_number):
    """
    If a user had multiple accounts, reassign bills from the old account
    to their next available account (in a simplistic sense).
    Actually, we never stored from_account in bills.csv.
    So we just mention that these bills exist, but if user has 0 accounts left, we remove them.
    """
    # We'll treat this as: if user has no more accounts, we remove all scheduled bills.
    # If user has some other accounts, we do nothing because bills are not assigned to a specific account in this system.
    from bank import get_user_accounts
    user_accts = get_user_accounts({"username": username})
    if not user_accts:
        # remove all bills
        all_bills = read_all_rows(BILL_CSV)
        updated = [b for b in all_bills if b["username"].lower() != username.lower()]
        write_all_rows(BILL_CSV, BILL_HEADERS, updated)
        print(f"[INFO] All bills for user '{username}' removed (no accounts left).")
    else:
        # do nothing, since bills are not specifically assigned to an account number in this system
        pass
