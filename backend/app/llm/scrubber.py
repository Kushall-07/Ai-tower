import re

# Very simple regex-based PII scrubber
SENSITIVE_PATTERNS = [
    # Aadhaar-like 12 digit numbers
    r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    # 10-digit phone numbers
    r"\b\d{10}\b",
    # Email addresses
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    # PAN-like pattern (ABCDE1234F)
    r"\b[A-Z]{5}\d{4}[A-Z]\b",
]


def scrub_text(text: str) -> str:
    """
    Replace obvious PII patterns with [REDACTED].
    This keeps us safe when using external LLMs.
    """
    if not text:
        return text

    scrubbed = text
    for pattern in SENSITIVE_PATTERNS:
        scrubbed = re.sub(pattern, "[REDACTED]", scrubbed)

    return scrubbed
