"""
budget.py
Create/update budgets, check usage, and handle reassign_or_remove_budgets.
"""

from csv_db import read_all_rows, write_all_rows, append_row
from config import BUDGET_CSV, BUDGET_HEADERS, TRANS_CSV
import datetime

def set_monthly_budget(username):
    category = input("Enter category name (e.g. 'Groceries'): ").strip()
    limit_str = input("Enter monthly budget limit: ").strip()

    try:
        limit_val = float(limit_str)
    except ValueError:
        print("[ERROR] Invalid budget limit (numbers only).")
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

    print(f"[SUCCESS] Budget for '{category}' set to ${limit_val}")

def view_budgets(username):
    all_budgets = read_all_rows(BUDGET_CSV)
    user_budgets = [b for b in all_budgets if b["username"].lower() == username.lower()]
    if not user_budgets:
        print("[INFO] No budgets found.")
        return

    print("\n=== Your Current Budgets ===")
    for b in user_budgets:
        print(f"Category: {b['category']} | Monthly Limit: ${b['monthly_limit']}")

def check_budget_usage(username):
    """
    Check user spending vs. set budgets for the current month.
    """
    all_budgets = read_all_rows(BUDGET_CSV)
    budget_map = {}
    for b in all_budgets:
        if b["username"].lower() == username.lower():
            budget_map[b["category"].lower()] = float(b["monthly_limit"])

    if not budget_map:
        return

    from config import TRANS_CSV
    all_trans = read_all_rows(TRANS_CSV)

    now = datetime.datetime.now()
    current_month = now.month
    current_year = now.year

    spending = {}
    for tx in all_trans:
        tx_category = tx.get("category", "General").lower()
        try:
            tx_time = datetime.datetime.strptime(tx["timestamp"], "%Y-%m-%d %H:%M:%S")
        except:
            continue

        if not tx["from_account"]:
            continue

        if tx_time.year == current_year and tx_time.month == current_month:
            if tx_category in budget_map:
                amt = float(tx["amount"])
                spending[tx_category] = spending.get(tx_category, 0.0) + amt

    for cat, used in spending.items():
        limit_val = budget_map.get(cat, 0)
        if used > limit_val:
            print(f"[ALERT] You exceeded your '{cat}' budget of ${limit_val}. Spent: ${used}")
        else:
            print(f"[INFO] Category '{cat}': Spent ${used} / Limit ${limit_val}")

def reassign_or_remove_budgets(username, deleted_account_number):
    """
    In this system, budgets are not tied to a specific account.
    If user still has at least one account, we keep budgets.
    If user has no accounts left, we remove all budgets.
    """
    from bank import get_user_accounts
    user_accts = get_user_accounts({"username": username})
    if not user_accts:
        all_budgets = read_all_rows(BUDGET_CSV)
        updated = [b for b in all_budgets if b["username"].lower() != username.lower()]
        write_all_rows(BUDGET_CSV, BUDGET_HEADERS, updated)
        print(f"[INFO] All budgets for user '{username}' removed (no accounts left).")
    else:
        pass
