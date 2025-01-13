"""
admin.py
All admin-related logic in one place, to keep main.py clean.
"""

import datetime
from csv_db import read_all_rows, write_all_rows, append_row
from config import (
    USER_CSV, USER_HEADERS, BANK_CSV, BANK_HEADERS,
    TRANS_CSV, TRANS_HEADERS, BILL_CSV, BILL_HEADERS,
    BUDGET_CSV, BUDGET_HEADERS,
    ADMIN_LOGS_CSV
)
from blockchain import blockchain
from admin_utils import delete_bank_account
from bill_pay import process_due_bills
from budget import view_budgets
from transaction import check_daily_limit
from user import read_all_rows as read_user_rows  # or just do csv_db read if needed
from fraud_detection import is_suspicious_transaction

def admin_menu(admin_user):
    """
    Displays the admin panel with advanced controls for user management,
    blockchain tampering checks and restoration, suspicious transaction viewing, etc.
    """
    while True:
        print("\n=== Admin Panel (Advanced) ===")
        print("1. View All Transactions")
        print("2. Check Blockchain Validity (Auto-Restore if tampered)")
        print("3. Delete a User and All Their Data")
        print("4. Delete a Bank Account (with Bill/Budget reassign)")
        print("5. View All Budgets and Bills")
        print("6. Show Suspicious Transactions")
        print("7. Return to Main Menu")

        choice = input("Choose an option: ").strip()
        if choice == "1":
            do_view_all_transactions()
        elif choice == "2":
            do_check_blockchain_validity(admin_user)
        elif choice == "3":
            do_delete_user_and_data(admin_user)
        elif choice == "4":
            do_delete_bank_account(admin_user)
        elif choice == "5":
            do_view_all_budgets_and_bills()
        elif choice == "6":
            do_show_suspicious_transactions()
        elif choice == "7":
            break
        else:
            print("[ERROR] Invalid choice. Please try again.")

def do_view_all_transactions():
    all_t = read_all_rows(TRANS_CSV)
    all_t.sort(key=lambda x: x["timestamp"], reverse=True)
    print("\n=== All Transactions (Descending) ===")
    if not all_t:
        print("[INFO] No transactions found.")
        return
    for tx in all_t:
        print(
            f"{tx['timestamp']} | From: {tx['from_account']} -> {tx['to_account']} | "
            f"${tx['amount']} | {tx['status']} | Category: {tx['category']}"
        )

def do_check_blockchain_validity(admin_user):
    valid, tampered_blocks = blockchain.is_chain_valid(verbose=True)
    if not valid:
        print("[WARNING] Blockchain tampered in blocks:", tampered_blocks)
        print("[ACTION] Restoring chain to last valid backup...")
        blockchain.restore_chain()
        # Log admin action
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action_details = f"Restored chain after tampering in blocks {tampered_blocks}"
        append_row(ADMIN_LOGS_CSV, [timestamp, admin_user["username"], "BLOCKCHAIN_RESTORE", action_details])
    else:
        print("[INFO] Blockchain is valid. No action needed.")

def do_delete_user_and_data(admin_user):
    """
    Removes user row from users.csv,
    plus any bank accounts, budgets, bills, transactions referencing them.
    """
    from admin_utils import delete_user_and_data
    delete_user_and_data(admin_user)

def do_delete_bank_account(admin_user):
    acct_num = input("Enter the account number to delete: ").strip()
    if not acct_num:
        print("[ERROR] No account number provided.")
        return
    delete_bank_account(acct_num, admin_user["username"])

def do_view_all_budgets_and_bills():
    print("\n=== All Budgets ===")
    all_budgets = read_all_rows(BUDGET_CSV)
    if not all_budgets:
        print("[INFO] No budgets found at all.")
    else:
        for bd in all_budgets:
            print(f"User: {bd['username']} | Category: {bd['category']} | Limit: {bd['monthly_limit']}")

    print("\n=== All Bills ===")
    all_bills = read_all_rows(BILL_CSV)
    if not all_bills:
        print("[INFO] No bills found at all.")
    else:
        for bill in all_bills:
            print(
                f"User: {bill['username']} | Bill: {bill['bill_name']} | Amount: {bill['amount']} "
                f"| Due: {bill['due_date']} | Freq: {bill['frequency']} | Status: {bill['status']}"
            )

def do_show_suspicious_transactions():
    from transaction import check_daily_limit
    all_banks = read_all_rows(BANK_CSV)
    all_trans = read_all_rows(TRANS_CSV)

    suspicious_list = []
    for tx in all_trans:
        amt = float(tx["amount"])
        from_acct = tx["from_account"]
        from_bank_data = next((b for b in all_banks if b["account_number"] == from_acct), None)
        if not from_bank_data:
            continue
        balance = float(from_bank_data["balance"])
        from config import DAILY_LIMIT
        from fraud_detection import is_suspicious_transaction

        if is_suspicious_transaction(amt, DAILY_LIMIT, balance):
            suspicious_list.append(tx)

    if suspicious_list:
        suspicious_list.sort(key=lambda x: x["timestamp"], reverse=True)
        print("\n=== Suspicious Transactions ===")
        for s in suspicious_list:
            print(
                f"{s['timestamp']} | From: {s['from_account']} -> {s['to_account']} | "
                f"Amount: ${s['amount']} | {s['status']} | Category: {s['category']}"
            )
    else:
        print("[INFO] No suspicious transactions found.")
