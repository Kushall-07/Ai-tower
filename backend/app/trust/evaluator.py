from typing import List, Dict, Any, Optional, Set


def find_risk_flags(text: str) -> List[str]:
    """
    Very simple keyword-based risk flagging.

    security_sensitive  → passwords, tokens, keys, OTP, CVV
    privacy_sensitive   → personal/customer data (email, phone, address, ID)
    financial_sensitive → salary, bank/card, transactions
    destructive_actions → delete/wipe/drop/shutdown type operations
    """
    text_l = text.lower()
    flags: Set[str] = set()

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


def classify_risk_level(flags: List[str]) -> str:
    """
    Tune risk levels:
      - HIGH   → destructive or security-sensitive
      - MEDIUM → privacy-sensitive or financial-sensitive
      - LOW    → everything else
    """
    f = set(flags)

    # High risk
    if "destructive_actions" in f or "security_sensitive" in f:
        return "high"

    # Medium risk
    medium_risk = {"privacy_sensitive", "financial_sensitive"}
    if f & medium_risk:
        return "medium"

    # Everything else
    return "low"


def evaluate_trust_and_risk(
    prompt: str,
    response: Optional[str],
    llm_error: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluate trust and risk for a given prompt/response pair.

    Returns a dict with:
      - trust_score (0–1)
      - risk_level ("low" | "medium" | "high")
      - risk_flags (list[str])
      - explanation (text)
    """
    # Combine prompt + response text for flagging
    combined = (prompt or "") + " " + (response or "")
    flags = find_risk_flags(combined)
    risk_level = classify_risk_level(flags)

    # Simple trust score heuristic:
    # start from 0.9, reduce for errors + risk
    trust_score = 0.9

    if llm_error:
        trust_score -= 0.3

    if risk_level == "high":
        trust_score -= 0.3
    elif risk_level == "medium":
        trust_score -= 0.1

    # clamp to [0, 1]
    trust_score = max(0.0, min(1.0, trust_score))

    # Explanation
    if llm_error:
        explanation = (
            f"LLM call returned error: {llm_error}. "
            f"Risk flags: {', '.join(flags) if flags else 'none'}. "
            f"Overall risk level assessed as {risk_level}."
        )
    else:
        explanation = (
            "LLM call completed successfully. "
            f"Detected potential risk patterns: {', '.join(flags) if flags else 'none'}. "
            f"Overall risk level assessed as {risk_level}."
        )

    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "risk_flags": flags,
        "explanation": explanation,
    }
