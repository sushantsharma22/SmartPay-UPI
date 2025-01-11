"""
bank.py
Handles linking, viewing, depositing, withdrawing from bank accounts.
"""

from csv_db import read_all_rows, append_row, write_all_rows
from config import BANK_CSV, BANK_HEADERS
from user import generate_random_account_number

def link_bank_account(logged_in_user):
    """Link a new bank account to the current user."""
    username = logged_in_user["username"]
    print("\n=== Link a Bank Account ===")
    use_random = input("Do you want to auto-generate an account number? (y/n): ").lower().strip() == 'y'

    if use_random:
        account_number = generate_random_account_number()
        print(f"[INFO] Generated account number: {account_number}")
    else:
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
    append_row(BANK_CSV, [username, account_number, bank_name, str(balance)])
    print("[SUCCESS] Bank account linked successfully.")

def view_linked_accounts(logged_in_user):
    """Show all bank accounts for the user."""
    username = logged_in_user["username"]
    print("\n=== Your Linked Bank Accounts ===")
    all_accounts = read_all_rows(BANK_CSV)
    user_accounts = [a for a in all_accounts if a["username"].lower() == username.lower()]

    if not user_accounts:
        print("No bank accounts linked yet.")
        return

    for idx, acct in enumerate(user_accounts, start=1):
        print(f"{idx}. Account# {acct['account_number']} | Bank: {acct['bank_name']} | Balance: ${acct['balance']}")

def get_user_accounts(logged_in_user):
    """Returns a list of account dicts for the user."""
    username = logged_in_user["username"]
    all_accounts = read_all_rows(BANK_CSV)
    return [a for a in all_accounts if a["username"].lower() == username.lower()]

def deposit_to_account(logged_in_user):
    """Deposit funds into one of the user's accounts."""
    user_accounts = get_user_accounts(logged_in_user)
    if not user_accounts:
        print("[ERROR] You have no linked accounts.")
        return

    print("\n=== Deposit to Account ===")
    for i, acc in enumerate(user_accounts, start=1):
        print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
    choice = input("Select account index for deposit: ").strip()

    try:
        idx_choice = int(choice) - 1
        if idx_choice < 0 or idx_choice >= len(user_accounts):
            print("[ERROR] Invalid selection.")
            return
    except ValueError:
        print("[ERROR] Invalid input.")
        return

    account_selected = user_accounts[idx_choice]
    deposit_str = input("Enter deposit amount: ").strip()

    try:
        deposit_amount = float(deposit_str)
        if deposit_amount <= 0:
            print("[ERROR] Deposit amount must be greater than 0.")
            return
    except ValueError:
        print("[ERROR] Invalid amount.")
        return

    # Update the account balance
    all_accounts = read_all_rows(BANK_CSV)
    for acct in all_accounts:
        if acct["account_number"] == account_selected["account_number"]:
            acct["balance"] = str(float(acct["balance"]) + deposit_amount)

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)
    print(f"[SUCCESS] Deposited ${deposit_amount} into account {account_selected['account_number']}.")

def withdraw_from_account(logged_in_user):
    """Withdraw funds from one of the user's accounts."""
    user_accounts = get_user_accounts(logged_in_user)
    if not user_accounts:
        print("[ERROR] You have no linked accounts.")
        return

    print("\n=== Withdraw from Account ===")
    for i, acc in enumerate(user_accounts, start=1):
        print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
    choice = input("Select account index for withdrawal: ").strip()

    try:
        idx_choice = int(choice) - 1
        if idx_choice < 0 or idx_choice >= len(user_accounts):
            print("[ERROR] Invalid selection.")
            return
    except ValueError:
        print("[ERROR] Invalid input.")
        return

    account_selected = user_accounts[idx_choice]
    balance = float(account_selected["balance"])

    withdraw_str = input("Enter withdrawal amount: ").strip()
    try:
        withdraw_amount = float(withdraw_str)
        if withdraw_amount <= 0:
            print("[ERROR] Withdrawal amount must be greater than 0.")
            return
    except ValueError:
        print("[ERROR] Invalid amount.")
        return

    if withdraw_amount > balance:
        print("[ERROR] Insufficient funds.")
        return

    # Update the account balance
    all_accounts = read_all_rows(BANK_CSV)
    for acct in all_accounts:
        if acct["account_number"] == account_selected["account_number"]:
            acct["balance"] = str(float(acct["balance"]) - withdraw_amount)

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)
    print(f"[SUCCESS] Withdrew ${withdraw_amount} from account {account_selected['account_number']}.")
