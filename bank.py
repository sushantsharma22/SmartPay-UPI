"""
bank.py
Handles linking and viewing bank accounts.
"""

from csv_db import read_all_rows, append_row, write_all_rows
from config import BANK_CSV, BANK_HEADERS

def link_bank_account(logged_in_user):
    """Link a new bank account to the current user."""
    print("\n=== Link a Bank Account ===")
    account_number = input("Enter account number (unique): ").strip()
    bank_name = input("Enter bank name: ").strip()
    balance_str = input("Enter initial balance (numbers only): ").strip()

    try:
        balance = float(balance_str)
    except ValueError:
        print("[ERROR] Invalid balance input.")
        return

    # Check if account number already taken
    all_accounts = read_all_rows(BANK_CSV)
    for acct in all_accounts:
        if acct["account_number"] == account_number:
            print("[ERROR] This account number is already linked by someone.")
            return

    # Add new bank account
    append_row(BANK_CSV, [logged_in_user, account_number, bank_name, str(balance)])
    print("[SUCCESS] Bank account linked successfully.")

def view_linked_accounts(logged_in_user):
    """Show all bank accounts for the user."""
    print("\n=== Your Linked Bank Accounts ===")
    all_accounts = read_all_rows(BANK_CSV)
    user_accounts = [a for a in all_accounts if a["username"].lower() == logged_in_user.lower()]

    if not user_accounts:
        print("No bank accounts linked yet.")
        return

    for idx, acct in enumerate(user_accounts, start=1):
        print(f"{idx}. Account# {acct['account_number']} | Bank: {acct['bank_name']} | Balance: ${acct['balance']}")

def get_user_accounts(logged_in_user):
    """Returns a list of account dicts for the user."""
    all_accounts = read_all_rows(BANK_CSV)
    return [a for a in all_accounts if a["username"].lower() == logged_in_user.lower()]
