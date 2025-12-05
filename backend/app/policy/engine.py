from typing import List, Literal, Dict

from ..trust.evaluator import find_risk_flags, classify_risk_level

PolicyDecision = Literal["allow", "needs_approval", "block"]


class PolicyConfig:
    """
    Simple global policy config v1.
    Later this can come from DB / UI.
    """

    # Max allowed tokens for responses (we don't enforce at LLM yet, just for info)
    max_tokens: int = 512

    # Whether high-risk prompts require human approval
    require_approval_for_high_risk: bool = True

    # Whether destructive actions are completely blocked
    block_destructive_actions: bool = True

    # Whether security-sensitive operations require approval
    require_approval_for_security_sensitive: bool = True

    # Whether accessing personal / financial data requires approval
    require_approval_for_sensitive_data: bool = True


def evaluate_policies(prompt: str, response: str) -> Dict:
    """
    Run simple policy logic on the prompt/response.
    Returns a dict with:
      - decision: "allow" | "needs_approval" | "block"
      - reasons: list of strings
      - flags: risk flags (reuse from trust layer)
    """

    flags = find_risk_flags(prompt + " " + (response or ""))
    risk_level = classify_risk_level(flags)
    reasons: List[str] = []
    decision: PolicyDecision = "allow"

    # If destructive actions and policy says block -> BLOCK
    if "destructive_actions" in flags and PolicyConfig.block_destructive_actions:
        decision = "block"
        reasons.append(
            "Prompt/response appears to contain destructive actions, "
            "and policy is configured to block such requests."
        )

    # If security-sensitive and not already blocked -> NEEDS APPROVAL
    if (
        decision == "allow"
        and "security_sensitive" in flags
        and PolicyConfig.require_approval_for_security_sensitive
    ):
        decision = "needs_approval"
        reasons.append(
            "Security-sensitive patterns detected (e.g., passwords, tokens). "
            "Policy requires human approval."
        )

    # If privacy/financial-sensitive and not already decided -> NEEDS APPROVAL
    sensitive_data_rules = {"privacy_sensitive", "financial_sensitive"}
    if (
        decision == "allow"
        and PolicyConfig.require_approval_for_sensitive_data
        and any(rule in sensitive_data_rules for rule in flags)
    ):
        decision = "needs_approval"
        reasons.append(
            "Access to personal or financial data detected. "
            "Policy requires human approval before proceeding."
        )

    # If still allow but overall risk is high -> NEEDS APPROVAL
    if (
        decision == "allow"
        and risk_level == "high"
        and PolicyConfig.require_approval_for_high_risk
    ):
        decision = "needs_approval"
        reasons.append(
            "Overall risk level assessed as HIGH. Policy requires human approval."
        )

    if decision == "allow" and not reasons:
        reasons.append("No policy violations detected. Request is allowed.")

    return {
        "decision": decision,
        "reasons": reasons,
        "risk_flags": flags,
        "risk_level": risk_level,
    }
