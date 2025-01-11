"""
Configuration constants for SmartPay-UPI Canada.
"""

import os

# CSV file paths
USER_CSV = "users.csv"
BANK_CSV = "banks.csv"
TRANS_CSV = "transactions.csv"
BILL_CSV = "bills.csv"
BUDGET_CSV = "budget.csv"
REWARDS_CSV = "rewards.csv"
VIRTUAL_CARDS_CSV = "virtual_cards.csv"

# CSV headers
USER_HEADERS = ["username", "password", "role", "email", "full_name", "phone"]
BANK_HEADERS = ["username", "account_number", "bank_name", "balance"]
TRANS_HEADERS = ["timestamp", "from_account", "to_account", "amount", "status", "category"]
BILL_HEADERS = ["username", "bill_name", "amount", "due_date", "frequency", "status"]
BUDGET_HEADERS = ["username", "category", "monthly_limit"]
REWARDS_HEADERS = ["username", "points"]
VIRTUAL_CARD_HEADERS = ["username", "card_number", "expiry", "linked_account"]

QR_CODES_DIR = "qr_codes"
if not os.path.exists(QR_CODES_DIR):
    os.makedirs(QR_CODES_DIR)

USE_BCRYPT = True  # Toggle if bcrypt is not installed

# Transaction / System Config
DAILY_LIMIT = 5000.0
STATEMENT_DAYS = 30

# Email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "donotreply.smartpayupi@gmail.com"
EMAIL_PASSWORD = "keyq tbri twgy btyw"
