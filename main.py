"""
main.py
Now uses a clean menu. If role == 'admin', we call admin_menu() from admin.py.
"""
#fields
import urllib.parse
from csv_db import initialize_csv_files
from user import register_user, login_user, reset_password
from bank import link_bank_account, view_linked_accounts, get_user_accounts, deposit_to_account, withdraw_from_account
from transaction import transfer_funds_manual, view_transactions, generate_monthly_statement
from qr_utils import generate_qr_for_account, scan_qr_code
from budget import set_monthly_budget, view_budgets, check_budget_usage
from bill_pay import schedule_bill_payment, view_scheduled_bills, process_due_bills
from ai_assistant import get_assistance
# NEW import:
from admin import admin_menu  # our new admin file

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
                        print("[ERROR] You have no linked accounts.")
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
                admin_menu(logged_in_user)  # <--- we now call admin.py's admin_menu
            else:
                print("[ERROR] Invalid choice.")

if __name__ == "__main__":
    main()
