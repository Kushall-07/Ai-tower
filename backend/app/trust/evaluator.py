def find_risk_flags(text: str):
    """
    Very simple keyword-based risk flagging.

    security_sensitive  → passwords, tokens, keys, OTP, CVV
    privacy_sensitive   → personal/customer data (email, phone, address, ID)
    financial_sensitive → salary, bank/card, transactions
    destructive_actions → delete/wipe/drop/shutdown type operations
    """
    text_l = text.lower()
    flags = set()

    # Security-sensitive: creds, auth, secrets
    security_keywords = [
        "password",
        "passcode",
        "login credentials",
        "admin credentials",
        "token",
        "access token",
        "secret key",
        "api key",
        "private key",
        "ssh key",
        "otp",
        "one-time password",
        "cvv",
    ]
    if any(k in text_l for k in security_keywords):
        flags.add("security_sensitive")

    # Privacy-sensitive: personal identifiable information
    privacy_keywords = [
        "personal data",
        "personal information",
        "pii",
        "customer data",
        "customer information",
        "email address",
        "email addresses",
        "phone number",
        "phone numbers",
        "mobile number",
        "home address",
        "address details",
        "date of birth",
        "dob",
        "aadhar",
        "aadhaar",
        "pan card",
        "id number",
        "identity number",
    ]
    if any(k in text_l for k in privacy_keywords):
        flags.add("privacy_sensitive")

    # Financial-sensitive: money, bank, card, salary
    financial_keywords = [
        "salary",
        "salaries",
        "payroll",
        "bank account",
        "bank accounts",
        "account number",
        "card number",
        "credit card",
        "debit card",
        "transaction history",
        "transactions",
        "iban",
        "ifsc",
    ]
    if any(k in text_l for k in financial_keywords):
        flags.add("financial_sensitive")

    # Destructive actions: dangerous operations
    destructive_keywords = [
        "delete all",
        "delete everything",
        "wipe all data",
        "wipe the database",
        "drop table",
        "drop database",
        "truncate table",
        "shutdown server",
        "format disk",
    ]
    if any(k in text_l for k in destructive_keywords):
        flags.add("destructive_actions")

    return list(flags)
