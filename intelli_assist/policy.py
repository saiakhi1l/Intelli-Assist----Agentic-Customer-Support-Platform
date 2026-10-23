
import re
from typing import Any


# -------------------------------------------------------------------
# 1. PII REDACTION
# -------------------------------------------------------------------

def redact_pii(text: str) -> str:
    """Redact common email addresses, phone numbers, and card-like numbers."""
    if not isinstance(text, str) or not text:
        return text if isinstance(text, str) else ""

    # Email addresses
    text = re.sub(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        "[REDACTED_EMAIL]",
        text,
        flags=re.IGNORECASE,
    )

    # Credit/debit card-like numbers: 13–19 digits with optional separators.
    def redact_card(match: re.Match) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if 13 <= len(digits) <= 19:
            return "[REDACTED_CARD]"
        return match.group(0)

    text = re.sub(
        r"(?<!\d)(?:\d[ -]?){12,18}\d(?!\d)",
        redact_card,
        text,
    )

    # Phone numbers
    def redact_phone(match: re.Match) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if 8 <= len(digits) <= 15:
            return "[REDACTED_PHONE]"
        return match.group(0)

    text = re.sub(
        r"(?<!\w)\+?\d[\d(). -]{6,}\d(?!\w)",
        redact_phone,
        text,
    )

    return text


# -------------------------------------------------------------------
# 2. SECURITY-RISK DETECTION
# -------------------------------------------------------------------

def detect_security_risk(message: str) -> str | None:
    """Detect potential account-security incidents."""
    if not isinstance(message, str) or not message.strip():
        return None

    text = message.lower()

    security_patterns = (
        "accessed my account without permission",
        "unauthorized access",
        "unauthorised access",
        "account was hacked",
        "someone hacked my account",
        "bypass authentication",
        "steal password",
        "steal credentials",
    )

    for phrase in security_patterns:
        if phrase in text:
            return "Potential security incident: unauthorized account access"

    return None


# -------------------------------------------------------------------
# 3. SUPPORT POLICY CLASSIFICATION
# -------------------------------------------------------------------

def detect_policy(message: str) -> dict[str, Any]:
    """Classify support requests and determine escalation priority."""
    if not isinstance(message, str) or not message.strip():
        return {
            "kind": "out_of_scope",
            "intent": "general",
            "priority": "low",
            "escalated": False,
            "blocked": False,
            "reason": "Empty or invalid message",
        }

    text = message.lower()

    # Check payment fraud before general security incidents.
    fraud_phrases = (
        "used my card",
        "someone used my card",
        "stolen card",
        "fraudulent payment",
        "payment fraud",
        "unauthorized transaction",
        "unauthorised transaction",
    )

    if any(phrase in text for phrase in fraud_phrases):
        return {
            "kind": "fraud",
            "intent": "billing",
            "priority": "urgent",
            "escalated": True,
            "blocked": False,
            "reason": "Suspected payment fraud",
        }

    risk = detect_security_risk(message)

    security_phrases = (
        "without permission",
        "unauthorized access",
        "unauthorised access",
        "accessed my account",
        "account was hacked",
        "someone hacked my account",
    )

    if risk or any(phrase in text for phrase in security_phrases):
        return {
            "kind": "security",
            "intent": "security",
            "priority": "urgent",
            "escalated": True,
            "blocked": False,
            "reason": risk or "Potential unauthorized account access",
        }

    # Out-of-scope requests
    if any(word in text for word in ("lottery", "lotto", "jackpot")):
        return {
            "kind": "out_of_scope",
            "intent": "general",
            "priority": "low",
            "escalated": False,
            "blocked": False,
            "reason": "Request is outside customer-support scope",
        }

    # Account and password support
    if any(word in text for word in (
        "password", "login", "log in", "account access", "sign in"
    )):
        return {
            "kind": "supported",
            "intent": "account",
            "priority": "normal",
            "escalated": False,
            "blocked": False,
            "reason": None,
        }

    # Order and delivery support
    if any(word in text for word in (
        "order", "shipment", "shipping", "delivery", "tracking"
    )):
        return {
            "kind": "supported",
            "intent": "orders",
            "priority": "normal",
            "escalated": False,
            "blocked": False,
            "reason": None,
        }

    return {
        "kind": "general",
        "intent": "general",
        "priority": "low",
        "escalated": False,
        "blocked": False,
        "reason": None,
    }


# -------------------------------------------------------------------
# 4. CITATION VALIDATION
# -------------------------------------------------------------------

def validate_citations(
    answer: str,
    retrieved_documents: list[Any] | None = None,
) -> dict[str, Any]:
    """
    Validate citation references against the retrieved document indexes.

    Accepted formats:
        [SOURCE_1]
        [SOURCE_2]
        [1]
        [2]

    This validates reference format and index range, not semantic support.
    """
    if not isinstance(answer, str):
        answer = ""

    documents = retrieved_documents or []

    markers = re.findall(
        r"\[(?:SOURCE_\d+|\d+)\]",
        answer,
        flags=re.IGNORECASE,
    )

    valid_markers: set[str] = set()

    for index, _document in enumerate(documents, start=1):
        valid_markers.add(f"[{index}]")
        valid_markers.add(f"[SOURCE_{index}]")

    normalized_markers = {marker.upper() for marker in markers}
    normalized_valid = {marker.upper() for marker in valid_markers}

    valid_used = sorted(normalized_markers & normalized_valid)
    invalid_used = sorted(normalized_markers - normalized_valid)

    return {
        "valid": bool(valid_used) and not invalid_used,
        "has_citations": bool(markers),
        "valid_citations": valid_used,
        "invalid_citations": invalid_used,
        "missing_citations": bool(documents) and not bool(markers),
    }
