from detectors.regex_detector import detect_structured_pii, iban_check, luhn_check


def test_iban_validation():
    # یک شبا معتبر آلمانی (فیک ولی معتبر ریاضی)
    valid_iban = "DE89370400440532013000"
    invalid_iban = "DE89370400440532013001"  # آخرین رقم تغییر دادم

    assert iban_check(valid_iban) is True
    assert iban_check(invalid_iban) is False


def test_luhn_validation():
    valid_card = "4012 8888 8888 1881"
    invalid_card = "4012 8888 8888 1882"

    assert luhn_check(valid_card) is True
    assert luhn_check(invalid_card) is False


def test_detect_structured_pii():
    sample_text = (
        "Contact me at info@redactflow.local or call +4915123456789. "
        "My IBAN is DE89 3704 0044 0532 0130 00."
    )

    findings = detect_structured_pii(sample_text)

    found_types = [item["type"] for item in findings]

    assert "EMAIL" in found_types
    assert "PHONE" in found_types
    assert "IBAN" in found_types
    assert len(findings) == 3
