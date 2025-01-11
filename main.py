"""
main.py
Entry point for the console-based UPI-like system with CSV storage and QR code integration.
"""

from csv_db import initialize_csv_files
from user import register_user, login_user
from bank import link_bank_account, view_linked_accounts, get_user_accounts
from transaction import transfer_funds_manual, view_transactions
from qr_utils import generate_qr_for_account, scan_qr_code

def main_menu():
    """Main loop for user registration, login, etc."""
    logged_in_user = None

    while True:
        if logged_in_user is None:
            print("\n======= UPI-Canada System (Not Logged In) =======")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                register_user()
            elif choice == "2":
                user = login_user()
                if user:
                    logged_in_user = user
            elif choice == "3":
                print("Exiting program.")
                break
            else:
                print("[ERROR] Invalid choice. Please try again.")
        else:
            # User is logged in
            print(f"\n======= UPI-Canada System (Logged in as {logged_in_user}) =======")
            print("1. Link Bank Account")
            print("2. View My Bank Accounts")
            print("3. Generate QR for an Account")
            print("4. Transfer Funds (Manual Selection)")
            print("5. Transfer Funds via QR Code (Scan)")
            print("6. View Transactions")
            print("7. Logout")

            choice = input("Choose an option: ").strip()

            if choice == "1":
                link_bank_account(logged_in_user)

            elif choice == "2":
                view_linked_accounts(logged_in_user)


            elif choice == "3":

                # Generate QR for one of the user's linked accounts

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


            elif choice == "4":
                # Manual transfer
                transfer_funds_manual(logged_in_user)



            elif choice == "5":

                print("\n=== Transfer Funds via QR Code ===")

                decoded_data = scan_qr_code()

                if decoded_data:

                    print(f"[INFO] Decoded QR Code Data: {decoded_data}")

                    # Extract account details from the QR code data

                    # Assuming QR code is in the format: upi://pay?pa=<account_number>&pn=User&am=0&cu=CAD

                    import urllib.parse

                    query = urllib.parse.urlparse(decoded_data).query

                    params = urllib.parse.parse_qs(query)

                    to_account = params.get("pa", [None])[0]  # Extract 'pa' (to account)

                    if not to_account:

                        print("[ERROR] Invalid QR code format. Missing account number.")

                    else:

                        # Proceed with fund transfer

                        print(f"[INFO] Initiating transfer to account: {to_account}")

                        # Find the logged-in user's accounts

                        user_accounts = get_user_accounts(logged_in_user)

                        if not user_accounts:
                            print("[ERROR] You have no linked accounts to transfer from.")

                            continue

                        print("Select the 'from' account index:")

                        for i, acc in enumerate(user_accounts):
                            print(f"{i + 1}. {acc['account_number']} | {acc['bank_name']} | Balance: ${acc['balance']}")

                        choice_from = input("Enter choice (index): ").strip()

                        try:

                            idx_from = int(choice_from) - 1

                            if idx_from < 0 or idx_from >= len(user_accounts):
                                print("[ERROR] Invalid selection.")

                                continue

                        except ValueError:

                            print("[ERROR] Invalid selection.")

                            continue

                        from_account = user_accounts[idx_from]

                        from_balance = float(from_account["balance"])

                        # Get the transfer amount

                        amount_str = input("Enter transfer amount: ").strip()

                        try:

                            amount = float(amount_str)

                        except ValueError:

                            print("[ERROR] Invalid amount.")

                            continue

                        if amount <= 0:
                            print("[ERROR] Amount must be > 0.")

                            continue

                        if from_balance < amount:
                            print("[ERROR] Insufficient balance.")

                            continue

                        # Perform the transaction

                        transfer_funds_manual(logged_in_user, from_account["account_number"], to_account, amount)

                else:

                    print("[ERROR] QR code scan failed or canceled.")


def main():
    # Ensure CSV files exist with headers
    initialize_csv_files()
    # Start main menu
    main_menu()

if __name__ == "__main__":
    main()
