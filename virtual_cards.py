"""
virtual_cards.py
Generates a short-lived virtual card for secure online transactions.
Stores the virtual card details in a dedicated CSV (VIRTUAL_CARDS_CSV).
"""

import random
import string
from csv_db import read_all_rows, write_all_rows, append_row
from config import VIRTUAL_CARDS_CSV, VIRTUAL_CARD_HEADERS
from bank import get_user_accounts

def generate_virtual_card(logged_in_user):
    """
    Creates a virtual card (number, expiry) that is tied to one of the user's accounts.
    The card is stored in VIRTUAL_CARDS_CSV for future reference.
    """
    username = logged_in_user["username"]
    user_accounts = get_user_accounts(logged_in_user)
    if not user_accounts:
        print("[ERROR] No accounts found. Cannot generate a virtual card.")
        return

    # Let user pick which account to link
    print("\n=== Generate Virtual Card ===")
    for i, acc in enumerate(user_accounts, start=1):
        print(f"{i}. Account# {acc['account_number']} | Balance: ${acc['balance']}")
    choice = input("Choose an account to link this virtual card to: ").strip()
    try:
        idx_choice = int(choice) - 1
        if idx_choice < 0 or idx_choice >= len(user_accounts):
            print("[ERROR] Invalid account selection.")
            return
    except ValueError:
        print("[ERROR] Invalid input.")
        return

    linked_account = user_accounts[idx_choice]["account_number"]

    # Generate a random 16-digit card number & random expiry
    card_number = ''.join(random.choices(string.digits, k=16))
    expiry = f"{random.randint(1, 12):02d}/{(random.randint(23, 29)):02d}"  # e.g. 05/26

    # Append to CSV
    append_row(VIRTUAL_CARDS_CSV, [username, card_number, expiry, linked_account])

    print("[SUCCESS] Virtual card generated!")
    print(f"Card Number: {card_number}")
    print(f"Expiry Date: {expiry}")
