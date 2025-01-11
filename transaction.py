"""
transaction.py
Handles money transfers, transaction history, daily limits, monthly statements, and transaction categories.
"""

import time
import datetime
from csv_db import read_all_rows, write_all_rows, append_row
from config import (
    BANK_CSV, BANK_HEADERS, TRANS_CSV, TRANS_HEADERS,
    DAILY_LIMIT, STATEMENT_DAYS
)
from bank import get_user_accounts
from notifications import send_transaction_notification

def transfer_funds_manual(logged_in_user, from_account=None, to_account=None, amount=None):
    """
    Transfer funds by manually choosing from/to accounts or using provided parameters.
    Ensures daily limit is not exceeded. Includes optional transaction category.
    """
    print("\n=== Transfer Funds (Manual) ===")

    # If parameters are not provided, request user input
    if not from_account or not to_account or amount is None:
        user_accounts = get_user_accounts(logged_in_user)
        if not user_accounts:
            print("[ERROR] You have no linked accounts to transfer from.")
            return

        print("Select the 'from' account index:")
        for i, acc in enumerate(user_accounts, start=1):
            print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
        choice_from = input("Enter choice (index): ").strip()

        try:
            idx_from = int(choice_from) - 1
            if idx_from < 0 or idx_from >= len(user_accounts):
                print("[ERROR] Invalid selection.")
                return
        except ValueError:
            print("[ERROR] Invalid selection.")
            return

        from_account = user_accounts[idx_from]["account_number"]

        # Next, pick the "to" account
        all_accounts = read_all_rows(BANK_CSV)
        print("\nSelect the 'to' account (by index):")
        for i, acc in enumerate(all_accounts, start=1):
            print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Owner: {acc['username']} | Balance: ${acc['balance']}")
        choice_to = input("Enter choice (index): ").strip()

        try:
            idx_to = int(choice_to) - 1
            if idx_to < 0 or idx_to >= len(all_accounts):
                print("[ERROR] Invalid selection.")
                return
        except ValueError:
            print("[ERROR] Invalid selection.")
            return

        to_account = all_accounts[idx_to]["account_number"]

        # Enter amount
        amount_str = input("Enter transfer amount: ").strip()
        try:
            amount = float(amount_str)
        except ValueError:
            print("[ERROR] Invalid amount.")
            return

    # Ask user for a category (optional)
    category = input("Enter a category for this transaction (e.g., 'Groceries', 'Rent', etc.) or leave blank: ").strip()
    if not category:
        category = "General"

    # Check daily limit
    if not check_daily_limit(from_account, amount):
        print(f"[ERROR] Daily transfer limit of ${DAILY_LIMIT} exceeded.")
        return

    # Ensure sufficient balance for the transfer
    user_accounts = get_user_accounts(logged_in_user)
    from_account_data = next(
        (acc for acc in user_accounts if acc["account_number"] == from_account), None
    )
    if not from_account_data:
        print("[ERROR] Invalid 'from' account.")
        return

    if float(from_account_data["balance"]) < amount:
        print("[ERROR] Insufficient balance.")
        return

    # Perform the transfer
    all_accounts = read_all_rows(BANK_CSV)
    from_updated = False
    to_updated = False

    for row in all_accounts:
        if row["account_number"] == from_account:
            row["balance"] = str(float(row["balance"]) - amount)
            from_updated = True
        if row["account_number"] == to_account:
            row["balance"] = str(float(row["balance"]) + amount)
            to_updated = True

    if not from_updated or not to_updated:
        print("[ERROR] Invalid from/to accounts. Transfer aborted.")
        return

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)

    # Log the transaction
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "COMPLETED"
    append_row(TRANS_CSV, [timestamp, from_account, to_account, str(amount), status, category])

    print(f"[SUCCESS] Transferred ${amount} from {from_account} to {to_account}.")

    # Send an email notification
    send_transaction_notification(
        recipient_email=logged_in_user["email"],
        subject="[SmartPay-UPI] Funds Transferred",
        body=(
            f"Hello {logged_in_user['full_name']},\n\n"
            f"You have transferred ${amount} from Account {from_account} to {to_account}.\n"
            f"Category: {category}\n\n"
            "If this was not you, please contact support immediately.\n\n"
            "Best regards,\nSmartPay-UPI Team"
        )
    )

def check_daily_limit(from_account, amount):
    """Checks if the daily limit for transfers from a specific account is exceeded."""
    import time
    today_str = time.strftime("%Y-%m-%d")
    all_trans = read_all_rows(TRANS_CSV)

    daily_sum = 0.0
    for tx in all_trans:
        date_part = tx["timestamp"].split(" ")[0]
        if tx["from_account"] == from_account and date_part == today_str:
            daily_sum += float(tx["amount"])

    if (daily_sum + amount) > DAILY_LIMIT:
        return False
    return True

def view_transactions(logged_in_user):
    """View last 10 transactions (descending order) involving any of the user's accounts."""
    print("\n=== Transaction History (Last 10) ===")
    user_accts = get_user_accounts(logged_in_user)
    user_acct_nums = [acct["account_number"] for acct in user_accts]

    all_trans = read_all_rows(TRANS_CSV)
    # Filter transactions that involve user's accounts
    relevant_trans = []
    for tx in all_trans:
        if tx["from_account"] in user_acct_nums or tx["to_account"] in user_acct_nums:
            relevant_trans.append(tx)

    # Sort by timestamp descending
    relevant_trans.sort(key=lambda x: x["timestamp"], reverse=True)

    for tx in relevant_trans[:10]:
        print(
            f"{tx['timestamp']} | "
            f"From: {tx['from_account']} -> To: {tx['to_account']} | "
            f"Amount: ${tx['amount']} | {tx['status']} | Category: {tx['category']}"
        )

def generate_monthly_statement(logged_in_user):
    """Generates a monthly statement (last STATEMENT_DAYS) of all transactions for the user's accounts."""
    print(f"\n=== Monthly Statement for {logged_in_user['username']} ===")
    user_accts = get_user_accounts(logged_in_user)
    user_acct_nums = [acct["account_number"] for acct in user_accts]

    all_trans = read_all_rows(TRANS_CSV)
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=STATEMENT_DAYS)

    relevant_trans = []
    for tx in all_trans:
        try:
            tx_time = datetime.datetime.strptime(tx["timestamp"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue

        if tx_time >= cutoff_date:
            if tx["from_account"] in user_acct_nums or tx["to_account"] in user_acct_nums:
                relevant_trans.append(tx)

    relevant_trans.sort(key=lambda x: x["timestamp"])

    if not relevant_trans:
        print("No transactions in the last 30 days.")
        return

    total_in = 0.0
    total_out = 0.0
    for tx in relevant_trans:
        amount = float(tx["amount"])
        if tx["to_account"] in user_acct_nums:
            total_in += amount
        else:
            total_out += amount

        print(
            f"{tx['timestamp']} | "
            f"From: {tx['from_account']} -> To: {tx['to_account']} | "
            f"Amount: ${tx['amount']} | {tx['status']} | Category: {tx['category']}"
        )

    print(f"\n[INFO] Total Inflow: ${total_in} | Total Outflow: ${total_out}")
