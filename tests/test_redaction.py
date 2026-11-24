import pytest

from triage.redaction import luhn_valid, redact


def test_email_redacted():
    r = redact("Contact me at jane.doe+bank@example.com please")
    assert "example.com" not in r.text
    assert r.counts == {"EMAIL": 1}


def test_valid_card_redacted_with_separators():
    r = redact("My card 4111 1111 1111 1111 was charged")
    assert "4111" not in r.text and "[CARD]" in r.text
    r2 = redact("card 4111-1111-1111-1111")
    assert "[CARD]" in r2.text


def test_non_luhn_digit_run_not_treated_as_card():
    r = redact("reference 1234 5678 9012 3456 was quoted")
    assert "[CARD]" not in r.text


@pytest.mark.parametrize(
    "phone", ["0412 345 678", "0412345678", "+61 412 345 678", "(02) 9999 8888", "02 9999 8888"]
)
def test_au_phone_redacted(phone):
    r = redact(f"Call me on {phone} tomorrow")
    assert "[PHONE]" in r.text
    assert phone not in r.text


def test_bsb_and_labelled_account_redacted_keeping_label():
    r = redact("BSB 062-000, account number 12345678 was debited")
    assert "062-000" not in r.text
    assert "12345678" not in r.text
    assert "account number [ACCOUNT]" in r.text


def test_tfn_redacted():
    r = redact("My TFN is 123 456 782.")
    assert "123 456 782" not in r.text
    assert r.counts == {"TFN": 1}


def test_plain_text_unchanged_and_amounts_kept():
    text = "I was charged a $35 fee on 12 March, twice."
    r = redact(text)
    assert r.text == text and r.total == 0


def test_multiple_pii_counts():
    r = redact("Email a@b.com or a@c.com, phone 0412 345 678")
    assert r.counts == {"EMAIL": 2, "PHONE": 1}


def test_luhn_helper():
    assert luhn_valid("4111111111111111")
    assert not luhn_valid("4111111111111112")
    assert not luhn_valid("123")
