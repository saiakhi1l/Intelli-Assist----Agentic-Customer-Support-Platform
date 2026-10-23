
from intelli_assist.policy import detect_policy, redact_pii


def test_security_incident_is_urgent():
    result = detect_policy(
        "Someone accessed my account without permission."
    )

    assert result["kind"] == "security"
    assert result["priority"] == "urgent"
    assert result["escalated"] is True


def test_suspected_payment_fraud_is_urgent():
    result = detect_policy(
        "Someone used my card without permission."
    )

    assert result["kind"] == "fraud"
    assert result["priority"] == "urgent"
    assert result["escalated"] is True


def test_lottery_question_is_out_of_scope():
    result = detect_policy(
        "Can you tell me tomorrow's winning lottery numbers?"
    )

    assert result["kind"] == "out_of_scope"
    assert result["escalated"] is False


def test_password_question_is_supported():
    result = detect_policy("How do I reset my password?")

    assert result["kind"] == "supported"
    assert result["intent"] == "account"


def test_order_question_is_supported():
    result = detect_policy("How can I check the status of my order?")

    assert result["kind"] == "supported"
    assert result["intent"] == "orders"


def test_email_redaction():
    result = redact_pii("Please contact me at user@example.com")

    assert "user@example.com" not in result
    assert "[REDACTED_EMAIL]" in result
