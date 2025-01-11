"""
config.py
Configuration constants for the UPI-like system.
"""

import os

# Paths to CSV files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_CSV = os.path.join(BASE_DIR, "users.csv")
BANK_CSV = os.path.join(BASE_DIR, "bank_accounts.csv")
TRANS_CSV = os.path.join(BASE_DIR, "transactions.csv")

# CSV Headers
USER_HEADERS = ["username", "password"]   # Removed KYC doc to simplify
BANK_HEADERS = ["username", "account_number", "bank_name", "balance"]
TRANS_HEADERS = ["timestamp", "from_account", "to_account", "amount", "status"]

# Directory to store QR codes
QR_CODES_DIR = os.path.join(BASE_DIR, "qr_codes")
if not os.path.exists(QR_CODES_DIR):
    os.makedirs(QR_CODES_DIR)

# If bcrypt is installed, we use it to hash passwords
try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False
