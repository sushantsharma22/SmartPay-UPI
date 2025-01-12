"""
admin_utils.py
Provides admin actions that previously caused circular imports, such as deleting a bank account
(reassigning or removing bills/budgets), to avoid bank.py -> bill_pay.py -> transaction.py -> bank.py loops.
"""

from csv_db import read_all_rows, write_all_rows, append_row
from config import BANK_CSV, BANK_HEADERS, ADMIN_LOGS_CSV
from bill_pay import reassign_or_remove_bills
from budget import reassign_or_remove_budgets
import datetime

def delete_bank_account(account_number, admin_username):
    """
    Deletes the specified bank account from banks.csv.
    Then reassigns or removes any budgets/bills referencing it,
    as implemented in bill_pay.py / budget.py,
    to avoid orphaned references.
    """
    all_banks = read_all_rows(BANK_CSV)
    target = next((b for b in all_banks if b["account_number"] == account_number), None)
    if not target:
        print(f"[ERROR] No such account '{account_number}'.")
        return

    updated_banks = [b for b in all_banks if b["account_number"] != account_number]
    write_all_rows(BANK_CSV, BANK_HEADERS, updated_banks)

    user_name = target["username"]
    # Reassign or remove any budgets/bills that might be referencing this user+account
    reassign_or_remove_budgets(user_name, account_number)
    reassign_or_remove_bills(user_name, account_number)

    # Log admin action
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action_details = f"Deleted account {account_number} for user {user_name}"
    append_row(ADMIN_LOGS_CSV, [timestamp, admin_username, "DELETE_ACCOUNT", action_details])

    print(f"[INFO] Account '{account_number}' removed + budgets/bills handled (if any).")
