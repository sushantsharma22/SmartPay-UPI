"""
csv_db.py
Initializes CSV files and provides read/write helpers.
"""

import csv
import os

from config import (
    USER_CSV, BANK_CSV, TRANS_CSV, BILL_CSV, BUDGET_CSV, ADMIN_LOGS_CSV,
    USER_HEADERS, BANK_HEADERS, TRANS_HEADERS, BILL_HEADERS, BUDGET_HEADERS, ADMIN_LOGS_HEADERS
)

def initialize_csv_files():
    """Create CSV files with correct headers if not existing."""
    _init_file(USER_CSV, USER_HEADERS)
    _init_file(BANK_CSV, BANK_HEADERS)
    _init_file(TRANS_CSV, TRANS_HEADERS)
    _init_file(BILL_CSV, BILL_HEADERS)
    _init_file(BUDGET_CSV, BUDGET_HEADERS)
    _init_file(ADMIN_LOGS_CSV, ADMIN_LOGS_HEADERS)

def _init_file(csv_path, headers):
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    else:
        _ensure_headers(csv_path, headers)

def _ensure_headers(csv_path, correct_headers):
    rows = []
    existing_headers = []
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_headers = reader.fieldnames or []
            for row in reader:
                rows.append(row)
    except:
        pass

    new_headers = list({*existing_headers, *correct_headers})
    final_headers = [h for h in correct_headers if h in new_headers]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=final_headers)
        writer.writeheader()
        for row in rows:
            filtered = {h: row.get(h, "") for h in final_headers}
            writer.writerow(filtered)

def append_row(csv_file, row_data):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row_data)

def read_all_rows(csv_file):
    rows = []
    if not os.path.exists(csv_file):
        return rows
    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def write_all_rows(csv_file, headers, rows):
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
