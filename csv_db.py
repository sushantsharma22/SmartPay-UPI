"""
csv_db.py
Provides helper functions to initialize and manage CSV files for users, bank accounts, and transactions.
"""

import csv
import os

from config import USER_CSV, BANK_CSV, TRANS_CSV
from config import USER_HEADERS, BANK_HEADERS, TRANS_HEADERS

def initialize_csv_files():
    """Create the CSV files with headers if they do not exist."""
    if not os.path.exists(USER_CSV):
        with open(USER_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(USER_HEADERS)

    if not os.path.exists(BANK_CSV):
        with open(BANK_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(BANK_HEADERS)

    if not os.path.exists(TRANS_CSV):
        with open(TRANS_CSV, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(TRANS_HEADERS)


def append_row(csv_file, row_data):
    """Append a single row (list) to a specified CSV file."""
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row_data)


def read_all_rows(csv_file):
    """Read all rows (as dicts) from a CSV."""
    rows = []
    if not os.path.exists(csv_file):
        return rows
    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def write_all_rows(csv_file, headers, rows):
    """
    Overwrite the CSV with the given headers and rows (list of dicts).
    Each dict in 'rows' should match the headers.
    """
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
