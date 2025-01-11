"""
user.py
Manages user registration and login (password hashing if bcrypt is available).
"""

import getpass
from config import USER_CSV, USER_HEADERS, USE_BCRYPT
from csv_db import read_all_rows, append_row

if USE_BCRYPT:
    import bcrypt
else:
    bcrypt = None  # Fallback if bcrypt is not installed

def hash_password(plain_password):
    """Return a hashed version of the password using bcrypt (if available) or plain text."""
    if USE_BCRYPT:
        return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    else:
        return plain_password  # Fallback (not secure)

def check_password(plain_password, hashed_password):
    """Check if the plain_password matches the hashed_password."""
    if USE_BCRYPT:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    else:
        return plain_password == hashed_password

def register_user():
    """Register a new user."""
    print("\n=== User Registration ===")
    username = input("Enter a username: ").strip()

    # Check if user already exists
    all_users = read_all_rows(USER_CSV)
    for user in all_users:
        if user["username"].lower() == username.lower():
            print("[ERROR] Username already exists.")
            return

    # Get password (visible input)
    print("Note: Password will be visible as you type.")
    password = input("Enter a password: ").strip()
    confirm = input("Confirm password: ").strip()
    if password != confirm:
        print("[ERROR] Passwords do not match.")
        return

    hashed_pass = hash_password(password)
    append_row(USER_CSV, [username, hashed_pass])
    print("[SUCCESS] Registration complete. You can now log in.")


def login_user():
    """
    Attempt to log in the user.
    Returns the username if successful, else None.
    """
    print("\n=== User Login ===")
    username = input("username: ").strip()
    password = input("Password (visible): ").strip()  # Note: Password will be visible

    all_users = read_all_rows(USER_CSV)
    for user in all_users:
        if user["username"].lower() == username.lower():
            # Check password
            if check_password(password, user["password"]):
                print(f"[SUCCESS] Welcome, {username}!")
                return user["username"]
            else:
                print("[ERROR] Invalid password.")
                return None

    print("[ERROR] User not found.")
    return None

