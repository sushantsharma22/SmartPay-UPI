"""
main.py
Only showing the part that changed:
No longer importing `delete_bank_account` from bank.py.
Instead, import from admin_utils.py.
Then in the advanced admin panel, call `delete_bank_account(...)`.
"""

import urllib.parse
from csv_db import initialize_csv_files, read_all_rows, write_all_rows, append_row
from config import (
    USER_CSV, USER_HEADERS, BANK_CSV, BANK_HEADERS,
    TRANS_CSV, TRANS_HEADERS, BILL_CSV, BILL_HEADERS,
    BUDGET_CSV, BUDGET_HEADERS, ADMIN_LOGS_CSV, ADMIN_LOGS_HEADERS
)
from user import register_user, login_user, reset_password
from bank import link_bank_account, view_linked_accounts, get_user_accounts, deposit_to_account, withdraw_from_account
from transaction import transfer_funds_manual, view_transactions, generate_monthly_statement
from qr_utils import generate_qr_for_account, scan_qr_code
from budget import set_monthly_budget, view_budgets, check_budget_usage
from bill_pay import schedule_bill_payment, view_scheduled_bills, process_due_bills
from ai_assistant import get_assistance
from blockchain import blockchain
from fraud_detection import is_suspicious_transaction

# NEW import:
from admin_utils import delete_bank_account  # <--- Use this instead of bank.py for removing an account

def main():
    initialize_csv_files()
    main_menu()

def main_menu():
    logged_in_user = None
    while True:
        if logged_in_user is None:
            print("\n======= SmartPay-UPI (Not Logged In) =======")
            print("1. Register")
            print("2. Login")
            print("3. Reset Password")
            print("4. Process Due Bills (Admin Utility)")
            print("5. Ask AI Assistant")
            print("6. Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                register_user()
            elif choice == "2":
                user_info = login_user()
                if user_info:
                    logged_in_user = user_info
            elif choice == "3":
                reset_password()
            elif choice == "4":
                process_due_bills()
            elif choice == "5":
                user_query = input("Ask the AI about SmartPay-UPI usage: ")
                ans = get_assistance(user_query)
                print(f"\n[AI Assistant]: {ans}")
            elif choice == "6":
                print("Exiting program.")
                break
            else:
                print("[ERROR] Invalid choice.")
        else:
            username = logged_in_user["username"]
            role = logged_in_user["role"]
            print(f"\n======= SmartPay-UPI (Logged in as {username}, role: {role}) =======")
            print("1. Link Bank Account")
            print("2. View My Bank Accounts")
            print("3. Deposit to an Account")
            print("4. Withdraw from an Account")
            print("5. Generate QR for an Account")
            print("6. Transfer Funds (Manual Selection)")
            print("7. Transfer Funds via QR Code (Scan)")
            print("8. View My Transactions (Last 10)")
            print("9. Generate My Monthly Statement")
            print("10. Create/Update Budget")
            print("11. View My Budgets & Usage")
            print("12. Schedule a Bill Payment")
            print("13. View Scheduled Bills")
            print("14. Ask AI Assistant")
            print("15. Logout")
            if role == "admin":
                print("16. Admin Panel (Advanced)")

            choice = input("Choose an option: ").strip()
            if choice == "1":
                link_bank_account(logged_in_user)
            elif choice == "2":
                view_linked_accounts(logged_in_user)
            elif choice == "3":
                deposit_to_account(logged_in_user)
            elif choice == "4":
                withdraw_from_account(logged_in_user)
            elif choice == "5":
                user_accts = get_user_accounts(logged_in_user)
                if not user_accts:
                    print("[ERROR] You have no accounts.")
                    continue
                print("\nSelect which account to generate a QR code for:")
                for i, acc in enumerate(user_accts, start=1):
                    print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Bal: ${acc['balance']}")
                idx_str = input("Enter choice index: ").strip()
                try:
                    idx_sel = int(idx_str) - 1
                    if idx_sel < 0 or idx_sel >= len(user_accts):
                        print("[ERROR] Invalid selection.")
                    else:
                        acct_num = user_accts[idx_sel]["account_number"]
                        generate_qr_for_account(acct_num)
                except ValueError:
                    print("[ERROR] Invalid input.")
            elif choice == "6":
                transfer_funds_manual(logged_in_user)
            elif choice == "7":
                print("\n=== Transfer via QR Code ===")
                data = scan_qr_code()
                if data:
                    parsed = urllib.parse.urlparse(data)
                    params = urllib.parse.parse_qs(parsed.query)
                    to_acc = params.get("pa", [None])[0]
                    if not to_acc:
                        print("[ERROR] Invalid QR format.")
                        continue
                    print(f"[INFO] Transfer to account: {to_acc}")
                    user_accts = get_user_accounts(logged_in_user)
                    if not user_accts:
                        print("[ERROR] No linked accounts.")
                        continue
                    print("Select a 'from' account index:")
                    for i, a in enumerate(user_accts, start=1):
                        print(f"{i}. {a['account_number']} | {a['bank_name']} | Bal: ${a['balance']}")
                    c_from = input("Enter choice: ").strip()
                    try:
                        i_from = int(c_from) - 1
                        if i_from < 0 or i_from >= len(user_accts):
                            print("[ERROR] Invalid selection.")
                            continue
                    except ValueError:
                        print("[ERROR] Invalid input.")
                        continue
                    from_acc = user_accts[i_from]["account_number"]
                    amt_str = input("Enter amount to transfer: ").strip()
                    try:
                        amt_val = float(amt_str)
                    except ValueError:
                        print("[ERROR] Invalid amount.")
                        continue
                    transfer_funds_manual(logged_in_user, from_acc, to_acc, amt_val)
                else:
                    print("[ERROR] QR scan failed or canceled.")
            elif choice == "8":
                view_transactions(logged_in_user)
            elif choice == "9":
                generate_monthly_statement(logged_in_user)
            elif choice == "10":
                set_monthly_budget(username)
            elif choice == "11":
                view_budgets(username)
                check_budget_usage(username)
            elif choice == "12":
                schedule_bill_payment(logged_in_user)
            elif choice == "13":
                view_scheduled_bills(logged_in_user)
            elif choice == "14":
                user_q = input("Ask the AI: ")
                ai_ans = get_assistance(user_q)
                print(f"\n[AI Assistant]: {ai_ans}")
            elif choice == "15":
                print("[INFO] Logging out...")
                logged_in_user = None
            elif choice == "16" and role == "admin":
                advanced_admin_panel(logged_in_user)
            else:
                print("[ERROR] Invalid choice.")

def advanced_admin_panel(admin_user):
    while True:
        print("\n=== Admin Panel (Advanced) ===")
        print("1. View All Transactions")
        print("2. Check Blockchain Validity (Auto-Restore if tampered)")
        print("3. Delete a User and All Their Data")
        print("4. Delete a Bank Account (with Bill/Budget reassign)")
        print("5. View All Budgets and Bills")
        print("6. Show Suspicious Transactions")
        print("7. Return to Main Menu")

        ch = input("Choose an option: ").strip()
        if ch == "1":
            all_t = read_all_rows(TRANS_CSV)
            all_t.sort(key=lambda x: x["timestamp"], reverse=True)
            print("\n=== All Transactions (Descending) ===")
            for tx in all_t:
                print(
                    f"{tx['timestamp']} | From: {tx['from_account']} -> {tx['to_account']} | "
                    f"${tx['amount']} | {tx['status']} | Category: {tx['category']}"
                )
        elif ch == "2":
            valid, tampered_blocks = blockchain.is_chain_valid(verbose=True)
            if not valid:
                print("[WARNING] Blockchain tampered at blocks:", tampered_blocks)
                print("[ACTION] Restoring chain to last valid backup...")
                blockchain.restore_chain()
                # log admin action
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                action_details = f"Restored chain after tampering in blocks {tampered_blocks}"
                append_row(ADMIN_LOGS_CSV, [timestamp, admin_user["username"], "BLOCKCHAIN_RESTORE", action_details])
            else:
                print("[INFO] Blockchain is valid. No action needed.")
        elif ch == "3":
            delete_user_and_data(admin_user)
        elif ch == "4":
            acct_num = input("Enter the account number to delete: ").strip()
            if acct_num:
                delete_bank_account(acct_num, admin_user["username"])
            else:
                print("[ERROR] No account number provided.")
        elif ch == "5":
            view_all_budgets_and_bills()
        elif ch == "6":
            show_suspicious_transactions()
        elif ch == "7":
            break
        else:
            print("[ERROR] Invalid choice.")

def delete_user_and_data(admin_user):
    target_username = input("Enter the username you want to delete: ").strip()
    if not target_username:
        print("[ERROR] Invalid username.")
        return

    if target_username.lower() == admin_user["username"].lower():
        print("[ERROR] You cannot delete your own admin account while logged in.")
        return

    all_users = read_all_rows(USER_CSV)
    updated_users = [u for u in all_users if u["username"].lower() != target_username.lower()]
    if len(updated_users) == len(all_users):
        print("[ERROR] No such user found.")
        return
    write_all_rows(USER_CSV, USER_HEADERS, updated_users)

    # remove from banks
    all_banks = read_all_rows(BANK_CSV)
    user_banks = [b for b in all_banks if b["username"].lower() == target_username.lower()]
    updated_banks = [b for b in all_banks if b["username"].lower() != target_username.lower()]
    write_all_rows(BANK_CSV, BANK_HEADERS, updated_banks)

    # remove from bills
    all_bills = read_all_rows(BILL_CSV)
    updated_bills = [bill for bill in all_bills if bill["username"].lower() != target_username.lower()]
    write_all_rows(BILL_CSV, BILL_HEADERS, updated_bills)

    # remove from budget
    all_budgets = read_all_rows(BUDGET_CSV)
    updated_budgets = [bd for bd in all_budgets if bd["username"].lower() != target_username.lower()]
    write_all_rows(BUDGET_CSV, BUDGET_HEADERS, updated_budgets)

    # remove transactions referencing user accounts
    all_trans = read_all_rows(TRANS_CSV)
    user_acct_nums = [b["account_number"] for b in user_banks]
    def is_user_tx(tx):
        return (tx["from_account"] in user_acct_nums) or (tx["to_account"] in user_acct_nums)

    updated_trans = [t for t in all_trans if not is_user_tx(t)]
    write_all_rows(TRANS_CSV, TRANS_HEADERS, updated_trans)

    # log admin action
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action_details = f"Deleted user '{target_username}' + data."
    append_row(ADMIN_LOGS_CSV, [timestamp, admin_user["username"], "DELETE_USER", action_details])

    print(f"[INFO] User '{target_username}' and all their data have been deleted from the system.")

def view_all_budgets_and_bills():
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

def show_suspicious_transactions():
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
