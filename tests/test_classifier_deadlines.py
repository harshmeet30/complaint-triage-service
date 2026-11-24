from datetime import date

from triage.classifier import classify, detect_vulnerability
from triage.deadlines import due_date, response_days


def test_scam_classified():
    c = classify("I was scammed. There are unauthorised transfers I did not make.")
    assert c.category == "scam_fraud" and not c.abstained and c.confidence >= 0.6


def test_hardship_classified():
    c = classify("I lost my job and cannot afford my repayments, I need hardship help.")
    assert c.category == "financial_hardship"


def test_fees_classified():
    c = classify("You charged a monthly account fee and an overdraft fee. Refund the fee.")
    assert c.category == "fees_charges"


def test_no_signal_abstains():
    c = classify("Hello, I would like to talk to someone about my situation.")
    assert c.abstained and c.category is None and c.abstain_reason == "no_signal"


def test_weak_signal_abstains():
    c = classify("There was an error somewhere.")
    assert c.abstained and c.abstain_reason == "weak_signal"


def test_ambiguous_categories_abstain():
    c = classify("Unauthorised fraud on my account and also a huge overdraft fee and poor service.")
    assert c.abstained and c.abstain_reason == "ambiguous_categories"


def test_vulnerability_detected_even_when_abstained():
    c = classify("My husband died last month and I need someone to call me.")
    assert c.abstained
    assert "bereavement" in c.vulnerability_flags


def test_vulnerability_flags():
    assert detect_vulnerability("I am escaping domestic violence") == ("family_violence",)
    assert detect_vulnerability("Nothing special here") == ()


def test_deadlines_rg271():
    d = date(2026, 3, 1)
    assert response_days(hardship=False) == 30 and response_days(hardship=True) == 21
    assert due_date(d, hardship=False) == date(2026, 3, 31)
    assert due_date(d, hardship=True) == date(2026, 3, 22)
    assert due_date(date(2026, 12, 20), hardship=False) == date(2027, 1, 19)
