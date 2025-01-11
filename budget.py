"""
budget.py
Allows users to set monthly budgets for various categories and alerts if the limit is exceeded.
"""

from csv_db import read_all_rows, write_all_rows, append_row
from config import BUDGET_CSV, BUDGET_HEADERS, TRANS_CSV
import datetime

def set_monthly_budget(username):
    """
    Let user set or update a budget for a specific category (e.g., Groceries).
    """
    category = input("Enter category name (e.g., 'Groceries'): ").strip()
    limit_str = input("Enter monthly budget limit: ").strip()
    try:
        limit_val = float(limit_str)
    except ValueError:
        print("[ERROR] Invalid budget limit.")
        return

    all_budgets = read_all_rows(BUDGET_CSV)
    updated = False
    for b in all_budgets:
        if b["username"].lower() == username.lower() and b["category"].lower() == category.lower():
            b["monthly_limit"] = str(limit_val)
            updated = True
    if not updated:
        append_row(BUDGET_CSV, [username, category, str(limit_val)])
    else:
        write_all_rows(BUDGET_CSV, BUDGET_HEADERS, all_budgets)
    print(f"[SUCCESS] Budget set for {category}: ${limit_val}")

def view_budgets(username):
    """
    Display the budgets for all categories the user has set.
    """
    all_budgets = read_all_rows(BUDGET_CSV)
    user_budgets = [b for b in all_budgets if b["username"].lower() == username.lower()]
    if not user_budgets:
        print("[INFO] No budgets found.")
        return

    print("\n=== Your Current Budgets ===")
    for b in user_budgets:
        print(f"Category: {b['category']}, Monthly Limit: ${b['monthly_limit']}")

def check_budget_usage(username):
    """
    Calculates how much user has spent in each category within the current month
    and compares against the set budget.
    """
    # Build a dictionary: category -> monthly_limit
    all_budgets = read_all_rows(BUDGET_CSV)
    budget_map = {}
    for b in all_budgets:
        if b["username"].lower() == username.lower():
            budget_map[b["category"].lower()] = float(b["monthly_limit"])

    if not budget_map:
        return

    # We gather transactions for the current month
    from config import TRANS_CSV
    all_trans = read_all_rows(TRANS_CSV)

    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    category_spending = {}  # category -> spending
    for tx in all_trans:
        # Only consider transactions from user (i.e., from_account is user's)
        tx_category = tx.get("category", "General")
        # parse timestamp
        try:
            tx_time = datetime.datetime.strptime(tx["timestamp"], "%Y-%m-%d %H:%M:%S")
        except:
            continue
        if tx["from_account"] is None:
            continue

        # check date
        if tx_time.year == current_year and tx_time.month == current_month:
            # accumulate spending if category is in budget_map
            if tx_category.lower() in budget_map:
                spent = float(tx["amount"])
                category_spending[tx_category.lower()] = category_spending.get(tx_category.lower(), 0.0) + spent

    # Now compare usage with budgets
    for cat, spent in category_spending.items():
        limit_val = budget_map.get(cat, None)
        if limit_val is not None and spent > limit_val:
            print(f"[ALERT] You have exceeded your monthly budget for '{cat}'!")
        elif limit_val is not None:
            print(f"[INFO] Category '{cat}': Spent ${spent} / Budget ${limit_val}")
