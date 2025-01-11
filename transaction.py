"""
transaction.py
Handles money transfers and transaction history.
"""

import time
from csv_db import read_all_rows, write_all_rows, append_row
from config import BANK_CSV, BANK_HEADERS, TRANS_CSV, TRANS_HEADERS
from bank import get_user_accounts

def transfer_funds_manual(logged_in_user):
    """
    Transfer funds by manually choosing from/to accounts (no QR).
    """
    print("\n=== Transfer Funds (Manual) ===")
    user_accounts = get_user_accounts(logged_in_user)
    if not user_accounts:
        print("[ERROR] You have no linked accounts to transfer from.")
        return

    print("Select the 'from' account index:")
    for i, acc in enumerate(user_accounts):
        print(f"{i+1}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
    choice_from = input("Enter choice (index): ").strip()

    try:
        idx_from = int(choice_from) - 1
        if idx_from < 0 or idx_from >= len(user_accounts):
            print("[ERROR] Invalid selection.")
            return
    except ValueError:
        print("[ERROR] Invalid selection.")
        return

    from_account = user_accounts[idx_from]
    from_balance = float(from_account["balance"])

    # Next, pick the "to" account (could be user's own or another user's)
    all_accounts = read_all_rows(BANK_CSV)
    print("\nSelect the 'to' account (by index):")
    for i, acc in enumerate(all_accounts):
        print(f"{i+1}. {acc['account_number']} | {acc['bank_name']} | Owner: {acc['username']} | Balance: ${acc['balance']}")
    choice_to = input("Enter choice (index): ").strip()

    try:
        idx_to = int(choice_to) - 1
        if idx_to < 0 or idx_to >= len(all_accounts):
            print("[ERROR] Invalid selection.")
            return
    except ValueError:
        print("[ERROR] Invalid selection.")
        return

    to_account = all_accounts[idx_to]

    # Enter amount
    amount_str = input("Enter transfer amount: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("[ERROR] Invalid amount.")
        return

    if amount <= 0:
        print("[ERROR] Amount must be > 0.")
        return

    if from_balance < amount:
        print("[ERROR] Insufficient balance.")
        return

    # Perform transaction
    new_from_balance = from_balance - amount
    new_to_balance = float(to_account["balance"]) + amount

    # Update the CSV in memory
    for row in all_accounts:
        if row["account_number"] == from_account["account_number"]:
            row["balance"] = str(new_from_balance)
        if row["account_number"] == to_account["account_number"]:
            row["balance"] = str(new_to_balance)

    # Save changes back to CSV
    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)

    # Log transaction
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "COMPLETED"
    append_row(TRANS_CSV, [timestamp, from_account["account_number"], to_account["account_number"], str(amount), status])

    print(f"[SUCCESS] Transferred ${amount} from {from_account['account_number']} to {to_account['account_number']}.")

def view_transactions(logged_in_user):
    """View last 10 transactions (descending order by timestamp) involving any of the user's accounts."""
    print("\n=== Transaction History (Last 10) ===")
    all_trans = read_all_rows(TRANS_CSV)
    user_accts = get_user_accounts(logged_in_user)
    user_acct_nums = [acct["account_number"] for acct in user_accts]

    # Filter transactions that involve user's accounts
    relevant_trans = []
    for tx in all_trans:
        if tx["from_account"] in user_acct_nums or tx["to_account"] in user_acct_nums:
            relevant_trans.append(tx)

    # Sort by timestamp descending (quick approach: lexical sort if all timestamps have same length)
    relevant_trans.sort(key=lambda x: x["timestamp"], reverse=True)

    # Show last 10
    for tx in relevant_trans[:10]:
        print(f"{tx['timestamp']} | From: {tx['from_account']} -> To: {tx['to_account']} | Amount: ${tx['amount']} | {tx['status']}")
