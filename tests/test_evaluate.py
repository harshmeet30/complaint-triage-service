import json

from triage.evaluate import DEFAULT_PATH, evaluate, load


def test_shipped_eval_set_meets_gates():
    rep = evaluate(load(DEFAULT_PATH))
    assert rep.passed, rep.metrics


def test_harness_fails_when_gates_are_breached(tmp_path):
    # Mislabelled on purpose: the gate must detect it rather than pass vacuously.
    text = "I was scammed, unauthorised transfers I did not make."
    rows = [{"text": text, "expected": "fees_charges"}] * 4
    rep = evaluate(rows)
    assert not rep.passed and rep.metrics["accuracy"] == 0.0


def test_critical_misroute_is_counted():
    text = "Charged a monthly account fee and a dishonour fee."
    rows = [{"text": text, "expected": "scam_fraud"}]
    rep = evaluate(rows)
    assert rep.metrics["critical_misroutes"] == 1 and not rep.gates["critical_misroutes"]


def test_dataset_is_well_formed():
    rows = load(DEFAULT_PATH)
    assert len(rows) >= 50
    labels = {r["expected"] for r in rows}
    assert labels == {
        "scam_fraud", "financial_hardship", "fees_charges",
        "service_conduct", "product_issue", "needs_review",
    }
    json.dumps(rows)
