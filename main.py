"""
main.py
Entry point for the console-based UPI-like system:
- No password complexity check
- Phone optional
- process_due_bills fixed
"""

import urllib.parse
from csv_db import initialize_csv_files, read_all_rows
from user import register_user, login_user, reset_password
from bank import link_bank_account, view_linked_accounts, get_user_accounts, deposit_to_account, withdraw_from_account
from transaction import transfer_funds_manual, view_transactions, generate_monthly_statement
from qr_utils import generate_qr_for_account, scan_qr_code
from virtual_cards import generate_virtual_card
from rewards import add_reward_points, view_reward_points
from budget import set_monthly_budget, view_budgets, check_budget_usage
from bill_pay import schedule_bill_payment, view_scheduled_bills, process_due_bills

def main():
    # Ensure CSV files exist with headers
    initialize_csv_files()
    main_menu()

def main_menu():
    """Main loop for user registration, login, etc."""
    logged_in_user = None

    while True:
        if logged_in_user is None:
            print("\n======= SmartPay-UPI Canada (Not Logged In) =======")
            print("1. Register")
            print("2. Login")
            print("3. Reset Password")
            print("4. Process Due Bills (Admin Utility - can skip if you run via cron)")
            print("5. Exit")
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
                # Now works without the UnboundLocalError
                process_due_bills()
            elif choice == "5":
                print("Exiting program.")
                break
            else:
                print("[ERROR] Invalid choice. Please try again.")
        else:
            # User is logged in
            username = logged_in_user["username"]
            role = logged_in_user["role"]
            print(f"\n======= SmartPay-UPI Canada (Logged in as {username}, role: {role}) =======")
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
            print("14. Get a Virtual Card")
            print("15. View My Reward Points")
            print("16. Logout")

            # Admin-only option
            if role == "admin":
                print("17. Admin Panel (View All Transactions)")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                link_bank_account(logged_in_user)

            elif choice == "2":
                view_linked_accounts(logged_in_user)

            elif choice == "3":
                deposit_to_account(logged_in_user)
                add_reward_points(username, 10)  # Reward for deposit

            elif choice == "4":
                withdraw_from_account(logged_in_user)

            elif choice == "5":
                user_accounts = get_user_accounts(logged_in_user)
                if not user_accounts:
                    print("[ERROR] You have no linked accounts.")
                else:
                    print("\nSelect which account to generate QR code for:")
                    for i, acc in enumerate(user_accounts, start=1):
                        print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
                    sel = input("Enter choice (index): ").strip()
                    try:
                        idx_sel = int(sel) - 1
                        if idx_sel < 0 or idx_sel >= len(user_accounts):
                            print("[ERROR] Invalid selection.")
                        else:
                            acc_num = user_accounts[idx_sel]["account_number"]
                            generate_qr_for_account(acc_num)
                    except ValueError:
                        print("[ERROR] Invalid input.")

            elif choice == "6":
                transfer_funds_manual(logged_in_user)
                add_reward_points(username, 5)  # Reward for transfer

            elif choice == "7":
                print("\n=== Transfer Funds via QR Code ===")
                decoded_data = scan_qr_code()
                if decoded_data:
                    print(f"[INFO] Decoded QR Code Data: {decoded_data}")
                    query = urllib.parse.urlparse(decoded_data).query
                    params = urllib.parse.parse_qs(query)
                    to_account = params.get("pa", [None])[0]

                    if not to_account:
                        print("[ERROR] Invalid QR code format. Missing account number.")
                    else:
                        print(f"[INFO] Initiating transfer to account: {to_account}")
                        user_accounts = get_user_accounts(logged_in_user)
                        if not user_accounts:
                            print("[ERROR] You have no linked accounts to transfer from.")
                            continue
                        print("Select the 'from' account index:")
                        for i, acc in enumerate(user_accounts, start=1):
                            print(f"{i}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")
                        choice_from = input("Enter choice (index): ").strip()
                        try:
                            idx_from = int(choice_from) - 1
                            if idx_from < 0 or idx_from >= len(user_accounts):
                                print("[ERROR] Invalid selection.")
                                continue
                        except ValueError:
                            print("[ERROR] Invalid selection.")
                            continue
                        from_account = user_accounts[idx_from]["account_number"]
                        amount_str = input("Enter transfer amount: ").strip()
                        try:
                            amount = float(amount_str)
                        except ValueError:
                            print("[ERROR] Invalid amount.")
                            continue
                        # Execute the transfer
                        transfer_funds_manual(logged_in_user, from_account, to_account, amount)
                        add_reward_points(username, 5)  # Reward for transfer
                else:
                    print("[ERROR] QR code scan failed or canceled.")

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
                generate_virtual_card(logged_in_user)

            elif choice == "15":
                view_reward_points(username)

            elif choice == "16":
                print("[INFO] Logging out...")
                logged_in_user = None

            elif choice == "17" and role == "admin":
                admin_panel()
            else:
                print("[ERROR] Invalid choice. Please try again.")

def admin_panel():
    """Admin-only panel to view all transactions or other admin tasks."""
    print("\n=== Admin Panel ===")
    while True:
        print("1. View All Transactions")
        print("2. Return to Main Menu")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            all_trans = read_all_rows("transactions.csv")
            all_trans.sort(key=lambda x: x["timestamp"], reverse=True)
            print("\n=== All Transactions (Descending) ===")
            for tx in all_trans:
                print(
                    f"{tx['timestamp']} | "
                    f"From: {tx['from_account']} -> To: {tx['to_account']} | "
                    f"Amount: ${tx['amount']} | {tx['status']} | Category: {tx['category']}"
                )
        elif choice == "2":
            break
        else:
            print("[ERROR] Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
