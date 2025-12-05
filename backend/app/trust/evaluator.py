from typing import List, Dict, Literal
import re

RiskLevel = Literal["low", "medium", "high"]


# Simple keyword-based risk rules (v1)
RISK_KEYWORDS = {
    "destructive_actions": [
        "delete", "drop table", "format disk", "shutdown", "kill process",
        "rm -rf", "truncate", "reset database"
    ],
    "financial_sensitive": [
        "bank account", "ifsc", "loan approval", "transfer money",
        "salary details", "upi", "credit card", "debit card"
    ],
    "privacy_sensitive": [
        "aadhaar", "pan", "passport", "phone number", "email address",
        "address", "ssn", "social security"
    ],
    "security_sensitive": [
        "password", "otp", "two factor", "2fa", "api key", "token",
        "secret", "private key", "ssh key"
    ],
}


def find_risk_flags(text: str) -> List[str]:
    """
    Look for simple risk-related patterns in the prompt/response.
    Returns a list of rule names that were triggered.
    """
    if not text:
        return []

    text_lower = text.lower()
    triggered: List[str] = []

    for rule_name, keywords in RISK_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                triggered.append(rule_name)
                break  # only add rule once, even if multiple keywords match

    return triggered


def classify_risk_level(flags: List[str]) -> RiskLevel:
    """
    Map number and type of flags to a risk level.
    Very simple v1 rule-based logic.
    """
    if not flags:
        return "low"

    # If any of these are triggered, treat as high directly
    high_risk_rules = {"destructive_actions", "security_sensitive"}

    if any(rule in high_risk_rules for rule in flags):
        return "high"

    # Medium if there are multiple other flags
    if len(flags) >= 2:
        return "medium"

    # Single non-high flag -> medium
    return "medium"


def compute_trust_score(
    has_llm_error: bool,
    risk_level: RiskLevel,
    prompt: str,
    response: str,
) -> float:
    """
    Very simple v1 trust score.
    - Start at 0.9
    - Penalize for LLM error
    - Penalize for medium/high risk
    - Penalize for very short or very long responses (suspicious)
    """
    score = 0.9

    if has_llm_error:
        score -= 0.4

    if risk_level == "medium":
        score -= 0.1
    elif risk_level == "high":
        score -= 0.3

    # Penalize extremely short answers for non-trivial prompts
    if len(prompt.split()) > 5 and len(response.split()) < 3:
        score -= 0.1

    # Clamp between 0 and 1
    score = max(0.0, min(1.0, score))
    return round(score, 2)


def evaluate_trust_and_risk(prompt: str, response: str, llm_error: str | None):
    """
    Main function your route will call.
    Returns a dict with risk, trust_score and explanation.
    """
    flags = find_risk_flags(prompt + " " + (response or ""))
    risk_level = classify_risk_level(flags)
    has_error = llm_error is not None

    trust_score = compute_trust_score(
        has_llm_error=has_error,
        risk_level=risk_level,
        prompt=prompt,
        response=response or "",
    )

    explanation_parts = []

    if has_error:
        explanation_parts.append("LLM call returned an error, so trust is reduced.")
    else:
        explanation_parts.append("LLM call completed successfully.")

    if not flags:
        explanation_parts.append("No obvious risky keywords were detected in the prompt/response.")
    else:
        explanation_parts.append(
            f"Detected potential risk patterns: {', '.join(flags)}."
        )

    explanation_parts.append(f"Overall risk level assessed as **{risk_level}**.")
    explanation = " ".join(explanation_parts)

    return {
        "trust_score": trust_score,
        "risk_level": risk_level,
        "risk_flags": flags,
        "explanation": explanation,
    }
