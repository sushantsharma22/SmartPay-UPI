"""
fraud_detection.py
A minimal rule-based system to flag suspicious transactions.
"""

def is_suspicious_transaction(amount, daily_limit, user_acct_balance):
    """
    Example checks:
    1. If amount > daily_limit * 0.8 => suspicious
    2. If amount > user_acct_balance => suspicious (though that's also an error case)
    3. If amount is extremely large (like > daily_limit entirely), definitely suspicious
    You can expand these rules as needed.
    """
    if amount > daily_limit:
        return True
    if amount > (daily_limit * 0.8):
        return True
    if amount > user_acct_balance:
        return True
    # Could do more complex checks
    return False
