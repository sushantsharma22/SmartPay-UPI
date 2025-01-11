"""
rewards.py
Reward points system for each successful transfer or deposit, stored in a dedicated CSV.
"""

from csv_db import read_all_rows, write_all_rows, append_row
from config import REWARDS_CSV, REWARDS_HEADERS

def add_reward_points(username, points):
    """
    Increments the user's reward points in the REWARDS_CSV file.
    """
    all_rewards = read_all_rows(REWARDS_CSV)
    for r in all_rewards:
        if r["username"].lower() == username.lower():
            current_points = int(r["points"])
            r["points"] = str(current_points + points)
            write_all_rows(REWARDS_CSV, REWARDS_HEADERS, all_rewards)
            print(f"[INFO] {points} reward points added. Total: {r['points']}")
            return

    # If not found, add new
    append_row(REWARDS_CSV, [username, str(points)])
    print(f"[INFO] {points} reward points added. Total: {points}")

def view_reward_points(username):
    """
    View the current reward points for a user.
    """
    all_rewards = read_all_rows(REWARDS_CSV)
    for r in all_rewards:
        if r["username"].lower() == username.lower():
            print(f"\n[INFO] You have {r['points']} reward points.")
            return
    print("\n[INFO] You have 0 reward points.")
