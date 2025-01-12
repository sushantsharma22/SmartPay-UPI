"""
ai_assistant.py
A simple rule-based "AI" for user guidance.
No change from the earlier code, just re-included.
"""

def get_assistance(user_query):
    query_lower = user_query.lower()

    if "register" in query_lower:
        return (
            "To register, select 'Register' from the main menu. Provide a unique username, "
            "email, password, and optional phone. A default bank account is automatically created."
        )

    if "login" in query_lower:
        return (
            "To login, choose 'Login' from the main menu, then enter your username and password. "
            "Upon success, you can access user menu options."
        )

    if "link" in query_lower or "account" in query_lower:
        return (
            "To create or link a bank account, select 'Link Bank Account' after logging in. "
            "You can auto-generate or manually specify an account number."
        )

    if "deposit" in query_lower:
        return (
            "To deposit, select 'Deposit to an Account.' "
            "Pick the account and enter the amount to deposit."
        )

    if "withdraw" in query_lower:
        return (
            "To withdraw, select 'Withdraw from an Account,' choose your account, and enter the amount."
        )

    if "transfer" in query_lower:
        return (
            "Use 'Transfer Funds (Manual)' or 'Transfer Funds via QR Code' to move money between accounts."
        )

    if "qr" in query_lower:
        return (
            "You can 'Generate QR for an Account' to receive money or 'Transfer Funds via QR Code' to send money."
        )

    if "bill" in query_lower or "schedule" in query_lower:
        return (
            "Use 'Schedule a Bill Payment' to set up recurring/one-time bills. "
            "View them with 'View Scheduled Bills,' and they auto-pay upon due date if you have balance."
        )

    if "budget" in query_lower:
        return (
            "Set or update monthly budget with 'Create/Update Budget.' "
            "Then 'View My Budgets & Usage' to check spending."
        )

    if "transaction" in query_lower or "history" in query_lower:
        return (
            "Use 'View My Transactions' to see recent activity. "
            "Use 'Generate My Monthly Statement' for a 30-day summary."
        )

    if "logout" in query_lower:
        return (
            "Select 'Logout' in the user menu to end your session."
        )

    if "admin" in query_lower:
        return (
            "As an admin, you have an Admin Panel to manage users, check blockchain tampering, and more."
        )

    return (
        "I can help with linking accounts, depositing, withdrawing, transferring, bills, budgets, and more. "
        "Use keywords like 'deposit', 'bill', 'transfer', 'budget' or 'QR'."
    )
