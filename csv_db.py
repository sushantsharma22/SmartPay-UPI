"""
csv_db.py
Ensures CSV files have correct headers and provides read/write helpers.
"""

import csv
import os

from config import (
    USER_CSV, BANK_CSV, TRANS_CSV, BILL_CSV, BUDGET_CSV, REWARDS_CSV, VIRTUAL_CARDS_CSV,
    USER_HEADERS, BANK_HEADERS, TRANS_HEADERS, BILL_HEADERS, BUDGET_HEADERS, REWARDS_HEADERS, VIRTUAL_CARD_HEADERS
)

def initialize_csv_files():
    """Create the CSV files with the correct headers if they do not exist."""
    _init_file(USER_CSV, USER_HEADERS)
    _init_file(BANK_CSV, BANK_HEADERS)
    _init_file(TRANS_CSV, TRANS_HEADERS)
    _init_file(BILL_CSV, BILL_HEADERS)
    _init_file(BUDGET_CSV, BUDGET_HEADERS)
    _init_file(REWARDS_CSV, REWARDS_HEADERS)
    _init_file(VIRTUAL_CARDS_CSV, VIRTUAL_CARD_HEADERS)

def _init_file(csv_path, headers):
    # If the file doesn't exist at all, create and write the headers
    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
    else:
        # If it exists, ensure it has the correct headers by merging
        _ensure_headers(csv_path, headers)

def _ensure_headers(csv_path, correct_headers):
    """
    If the CSV has partial/missing headers, fix them by rewriting
    all existing data with the new full set of headers.
    """
    rows = []
    existing_headers = []
    try:
        with open(csv_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            existing_headers = reader.fieldnames or []
            for row in reader:
                rows.append(row)
    except:
        # If there's an error reading, treat it as empty
        pass

    # Merge existing with correct headers
    new_headers = list({*existing_headers, *correct_headers})
    # But we actually want the order from correct_headers
    final_headers = [h for h in correct_headers if h in new_headers]

    # Re-write the CSV with the final headers
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=final_headers)
        writer.writeheader()
        for row in rows:
            # Only keep columns that match final_headers
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
