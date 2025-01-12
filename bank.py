"""
bank.py
Handles linking accounts, viewing them, depositing, withdrawing.
Removed references to bill_pay.py to avoid circular imports.
(No delete_bank_account function here anymore—it's moved to admin_utils.py)
"""

from csv_db import read_all_rows, write_all_rows, append_row
from config import BANK_CSV, BANK_HEADERS
from user import generate_random_account_number

def link_bank_account(logged_in_user):
    username = logged_in_user["username"]
    print("\n=== Link a Bank Account ===")
    use_auto = input("Auto-generate account number? (y/n): ").strip().lower()

    if use_auto == "y":
        account_number = generate_random_account_number()
        print(f"[INFO] Generated account number: {account_number}")
    else:
        account_number = input("Enter an account number: ").strip()

    bank_name = input("Enter bank name: ").strip()
    balance_str = input("Enter initial balance: ").strip()

    try:
        balance = float(balance_str)
    except ValueError:
        print("[ERROR] Invalid balance. Please provide a numeric value.")
        return

    all_accounts = read_all_rows(BANK_CSV)
    for acct in all_accounts:
        if acct["account_number"] == account_number:
            print("[ERROR] This account number is already used.")
            return

    append_row(BANK_CSV, [username, account_number, bank_name, str(balance)])
    print("[SUCCESS] Bank account linked successfully.")

def view_linked_accounts(logged_in_user):
    username = logged_in_user["username"]
    print("\n=== Your Linked Bank Accounts ===")
    all_accounts = read_all_rows(BANK_CSV)
    user_accounts = [a for a in all_accounts if a["username"].lower() == username.lower()]

    if not user_accounts:
        print("No bank accounts found.")
        return

    for i, acc in enumerate(user_accounts, start=1):
        print(f"{i}. Account#: {acc['account_number']} | Bank: {acc['bank_name']} | Balance: ${acc['balance']}")

def get_user_accounts(logged_in_user):
    """Returns a list of accounts for the current user."""
    username = logged_in_user["username"]
    all_accounts = read_all_rows(BANK_CSV)
    return [a for a in all_accounts if a["username"].lower() == username.lower()]

def deposit_to_account(logged_in_user):
    accounts = get_user_accounts(logged_in_user)
    if not accounts:
        print("[ERROR] You have no accounts.")
        return

    print("\n=== Deposit to Account ===")
    for i, a in enumerate(accounts, start=1):
        print(f"{i}. {a['account_number']} | {a['bank_name']} | Balance: ${a['balance']}")
    choice = input("Choose an account index: ").strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(accounts):
            print("[ERROR] Invalid selection.")
            return
    except ValueError:
        print("[ERROR] Invalid input (choose a number).")
        return

    amount_str = input("Enter deposit amount: ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("[ERROR] Deposit must be > 0.")
            return
    except ValueError:
        print("[ERROR] Invalid amount (numbers only).")
        return

    selected_acct = accounts[idx]
    all_accounts = read_all_rows(BANK_CSV)
    for row in all_accounts:
        if row["account_number"] == selected_acct["account_number"]:
            row["balance"] = str(float(row["balance"]) + amount)

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)
    print(f"[SUCCESS] Deposited ${amount} into account {selected_acct['account_number']}.")

def withdraw_from_account(logged_in_user):
    accounts = get_user_accounts(logged_in_user)
    if not accounts:
        print("[ERROR] You have no accounts.")
        return

    print("\n=== Withdraw from Account ===")
    for i, a in enumerate(accounts, start=1):
        print(f"{i}. {a['account_number']} | {a['bank_name']} | Balance: ${a['balance']}")
    choice = input("Choose an account index: ").strip()
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(accounts):
            print("[ERROR] Invalid choice.")
            return
    except ValueError:
        print("[ERROR] Invalid input (choose a number).")
        return

    amount_str = input("Enter withdrawal amount: ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("[ERROR] Withdrawal must be > 0.")
            return
    except ValueError:
        print("[ERROR] Invalid amount (numbers only).")
        return

    selected_acct = accounts[idx]
    balance = float(selected_acct["balance"])
    if amount > balance:
        print("[ERROR] Insufficient balance.")
        return

    all_accounts = read_all_rows(BANK_CSV)
    for row in all_accounts:
        if row["account_number"] == selected_acct["account_number"]:
            row["balance"] = str(balance - amount)

    write_all_rows(BANK_CSV, BANK_HEADERS, all_accounts)
    print(f"[SUCCESS] Withdrew ${amount} from account {selected_acct['account_number']}.")
