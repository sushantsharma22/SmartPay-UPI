"""
transaction.py
Handles transfers, daily limits, monthly statements.
Now with a simple fraud check.
Stores transactions in blockchain always,
and optionally in CSV if USE_BLOCKCHAIN_ONLY = False.
"""

import time
import datetime
from csv_db import read_all_rows, write_all_rows, append_row
from config import (
    BANK_CSV, BANK_HEADERS,
    TRANS_CSV, TRANS_HEADERS,
    DAILY_LIMIT, STATEMENT_DAYS,
    USE_BLOCKCHAIN_ONLY
)
from bank import get_user_accounts
from notifications import send_transaction_notification
from blockchain import record_transaction_in_blockchain
from fraud_detection import is_suspicious_transaction

def transfer_funds_manual(logged_in_user, from_account=None, to_account=None, amount=None):
    print("\n=== Transfer Funds (Manual) ===")

    if not from_account or not to_account or amount is None:
        user_accts = get_user_accounts(logged_in_user)
        if not user_accts:
            print("[ERROR] You have no accounts to transfer from.")
            return

        print("Select the 'from' account index:")
        for i, acc in enumerate(user_accts, start=1):
            print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Bal: ${acc['balance']}")
        choice_from = input("Enter choice: ").strip()
        try:
            idx_from = int(choice_from) - 1
            if idx_from < 0 or idx_from >= len(user_accts):
                print("[ERROR] Invalid choice.")
                return
        except ValueError:
            print("[ERROR] Invalid input (choose a number).")
            return

        from_account = user_accts[idx_from]["account_number"]

        all_accts = read_all_rows(BANK_CSV)
        print("\nSelect the 'to' account (by index):")
        for i, acc in enumerate(all_accts, start=1):
            print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Owner: {acc['username']} | ${acc['balance']}")
        choice_to = input("Enter choice: ").strip()
        try:
            idx_to = int(choice_to) - 1
            if idx_to < 0 or idx_to >= len(all_accts):
                print("[ERROR] Invalid choice.")
                return
        except ValueError:
            print("[ERROR] Invalid input (choose a number).")
            return

        to_account = all_accts[idx_to]["account_number"]

        amt_str = input("Enter transfer amount (numeric): ").strip()
        try:
            amount = float(amt_str)
        except ValueError:
            print("[ERROR] Invalid amount. Use numbers only.")
            return

    category = input("Enter a category (e.g. Rent, Grocery) or leave blank: ").strip()
    if not category:
        category = "General"

    if not check_daily_limit(from_account, amount):
        print(f"[ERROR] Daily transfer limit of ${DAILY_LIMIT} exceeded.")
        return

    user_accts = get_user_accounts(logged_in_user)
    from_data = next((acc for acc in user_accts if acc["account_number"] == from_account), None)
    if not from_data:
        print("[ERROR] 'From' account not found among your linked accounts.")
        return

    from_balance = float(from_data["balance"])
    if amount > from_balance:
        print("[ERROR] Insufficient funds.")
        return

    # Fraud detection check
    suspicious = is_suspicious_transaction(amount, DAILY_LIMIT, from_balance)
    if suspicious:
        print("[ALERT] This transaction is flagged as suspicious. Proceeding anyway...")

    # Perform the transfer in the bank CSV
    all_accts = read_all_rows(BANK_CSV)
    from_updated = False
    to_updated = False

    for row in all_accts:
        if row["account_number"] == from_account:
            row["balance"] = str(float(row["balance"]) - amount)
            from_updated = True
        if row["account_number"] == to_account:
            row["balance"] = str(float(row["balance"]) + amount)
            to_updated = True

    if not from_updated or not to_updated:
        print("[ERROR] Invalid from/to accounts. Transfer aborted.")
        return

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accts)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "COMPLETED"

    # If USE_BLOCKCHAIN_ONLY is False, also append to CSV
    if not USE_BLOCKCHAIN_ONLY:
        append_row(TRANS_CSV, [timestamp, from_account, to_account, str(amount), status, category])

    print(f"[SUCCESS] Transferred ${amount} from {from_account} to {to_account}.")

    # record in blockchain
    record_transaction_in_blockchain(from_account, to_account, amount, status, category)

    # notify
    send_transaction_notification(
        recipient_email=logged_in_user["email"],
        subject="[SmartPay-UPI] Funds Transferred",
        body=(
            f"Hello {logged_in_user['full_name']},\n\n"
            f"You transferred ${amount} from {from_account} to {to_account}.\n"
            f"Category: {category}\n"
            f"Suspicious: {suspicious}\n\n"
            "If this was not you, please contact support.\n\n"
            "Regards,\nSmartPay-UPI"
        )
    )

def check_daily_limit(from_account, amount):
    today_str = time.strftime("%Y-%m-%d")
    all_trans = read_all_rows(TRANS_CSV)

    daily_sum = 0.0
    for tx in all_trans:
        date_part = tx["timestamp"].split(" ")[0]
        if tx["from_account"] == from_account and date_part == today_str:
            daily_sum += float(tx["amount"])

    return (daily_sum + amount) <= DAILY_LIMIT

def view_transactions(logged_in_user):
    print("\n=== Transaction History (Last 10) ===")
    from bank import get_user_accounts
    user_accts = get_user_accounts(logged_in_user)
    user_nums = [a["account_number"] for a in user_accts]

    if not USE_BLOCKCHAIN_ONLY:
        all_trans = read_all_rows(TRANS_CSV)
        # filter
        relevant = []
        for tx in all_trans:
            if tx["from_account"] in user_nums or tx["to_account"] in user_nums:
                relevant.append(tx)
        relevant.sort(key=lambda x: x["timestamp"], reverse=True)
        for tx in relevant[:10]:
            print(
                f"{tx['timestamp']} | From: {tx['from_account']} -> {tx['to_account']} | "
                f"Amount: ${tx['amount']} | {tx['status']} | Category: {tx['category']}"
            )
    else:
        # If using chain only, we parse from chain data
        from blockchain import blockchain
        chain_data = []
        for block in blockchain.chain:
            if isinstance(block.transactions, list):
                for t in block.transactions:
                    # see if from_account or to_account is in user_nums
                    if t.get("from_account") in user_nums or t.get("to_account") in user_nums:
                        chain_data.append(t)
        chain_data.sort(key=lambda x: x["time"], reverse=True)
        for tx in chain_data[:10]:
            print(
                f"{tx['time']} | From: {tx['from_account']} -> {tx['to_account']} | "
                f"Amount: ${tx['amount']} | {tx['status']} | Category: {tx['category']}"
            )

def generate_monthly_statement(logged_in_user):
    print(f"\n=== Monthly Statement for {logged_in_user['username']} ===")
    from bank import get_user_accounts
    user_accts = get_user_accounts(logged_in_user)
    user_nums = [a["account_number"] for a in user_accts]

    cutoff = datetime.datetime.now() - datetime.timedelta(days=STATEMENT_DAYS)
    relevant_trans = []

    if not USE_BLOCKCHAIN_ONLY:
        # read from CSV
        all_trans = read_all_rows(TRANS_CSV)
        for tx in all_trans:
            try:
                tx_time = datetime.datetime.strptime(tx["timestamp"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
            if tx_time >= cutoff:
                if tx["from_account"] in user_nums or tx["to_account"] in user_nums:
                    relevant_trans.append(tx)
        relevant_trans.sort(key=lambda x: x["timestamp"])
    else:
        # read from chain
        from blockchain import blockchain
        chain_data = []
        for block in blockchain.chain:
            if isinstance(block.transactions, list):
                for t in block.transactions:
                    try:
                        tx_time = datetime.datetime.strptime(t["time"], "%Y-%m-%d %H:%M:%S")
                        if tx_time >= cutoff:
                            if t.get("from_account") in user_nums or t.get("to_account") in user_nums:
                                chain_data.append(t)
                    except:
                        pass
        chain_data.sort(key=lambda x: x["time"])
        relevant_trans = chain_data

    if not relevant_trans:
        print("No transactions in the last 30 days.")
        return

    total_in = 0.0
    total_out = 0.0
    for tx in relevant_trans:
        amount = float(tx["amount"])
        if tx["to_account"] in user_nums:
            total_in += amount
        else:
            total_out += amount
        print(
            f"{tx['time']} | "
            f"From: {tx['from_account']} -> {tx['to_account']} | "
            f"${tx['amount']} | {tx['status']} | Category: {tx['category']}"
        )

    print(f"\n[INFO] Total Inflow: ${total_in} | Total Outflow: ${total_out}")
