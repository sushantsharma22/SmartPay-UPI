
"""
Configuration constants for SmartPay-UPI, including toggles for advanced features.
"""

import os

# CSV file paths
USER_CSV = "users.csv"
BANK_CSV = "banks.csv"
TRANS_CSV = "transactions.csv"
BILL_CSV = "bills.csv"
BUDGET_CSV = "budget.csv"
ADMIN_LOGS_CSV = "admin_logs.csv"

# CSV headers
USER_HEADERS = ["username", "password", "role", "email", "full_name", "phone"]
BANK_HEADERS = ["username", "account_number", "bank_name", "balance"]
TRANS_HEADERS = ["timestamp", "from_account", "to_account", "amount", "status", "category"]
BILL_HEADERS = ["username", "bill_name", "amount", "due_date", "frequency", "status"]
BUDGET_HEADERS = ["username", "category", "monthly_limit"]
ADMIN_LOGS_HEADERS = ["timestamp", "admin_username", "action", "details"]

# Directory for QR codes
QR_CODES_DIR = "qr_codes"
if not os.path.exists(QR_CODES_DIR):
    os.makedirs(QR_CODES_DIR)

USE_BCRYPT = True  # Toggle if bcrypt is installed

# Transaction / System config
DAILY_LIMIT = 5000.0
STATEMENT_DAYS = 30

# Email config
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "donotreply.smartpayupi@gmail.com"
EMAIL_PASSWORD = "keyq tbri twgy btyw"

# Blockchain file
BLOCKCHAIN_FILE = "blockchain_data.json"

# Additional toggles
USE_BLOCKCHAIN_ONLY = False  # If True, skip writing to transactions.csv, store only in blockchain
