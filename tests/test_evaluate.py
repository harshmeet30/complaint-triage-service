import json

import pytest

from triage.evaluate import DEFAULT_PATH, evaluate, load, main


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


def test_cli_passes_on_shipped_set(capsys):
    assert main([]) == 0
    assert "EVAL PASSED" in capsys.readouterr().out


def test_cli_fails_and_lists_errors_on_bad_data(tmp_path, capsys):
    bad = tmp_path / "bad.jsonl"
    text = "I was scammed, unauthorised transfers I did not make."
    bad.write_text(json.dumps({"text": text, "expected": "fees_charges"}) + "\n", encoding="utf-8")
    assert main([str(bad), "--verbose"]) == 1
    out = capsys.readouterr().out
    assert "EVAL FAILED" in out and "expected fees_charges" in out


def test_cli_verbose_lists_abstained_labelled_cases(capsys):
    assert main(["--verbose"]) == 0
    assert "abstained on labelled cases" in capsys.readouterr().out


def test_load_rejects_malformed_rows(tmp_path):
    bad = tmp_path / "bad.jsonl"
    bad.write_text('{"text": "no label here"}\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load(bad)


def test_should_abstain_but_answered_is_reported():
    rows = [
        {"text": "Charged a monthly account fee and a dishonour fee.", "expected": "needs_review"}
    ]
    rep = evaluate(rows)
    assert rep.metrics["safe_abstain_recall"] == 0.0 and rep.errors


def test_dataset_is_well_formed():
    rows = load(DEFAULT_PATH)
    assert len(rows) >= 50
    labels = {r["expected"] for r in rows}
    assert labels == {
        "scam_fraud",
        "financial_hardship",
        "fees_charges",
        "service_conduct",
        "product_issue",
        "needs_review",
    }
    json.dumps(rows)
