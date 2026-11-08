import json
from types import SimpleNamespace

import pytest

from eval import run_eval as ev


def test_warning_metrics_separate_incomplete_and_provider_failure():
    rows = [dict(label=label, flagged=flag, assessment="insufficient_evidence", analysis_complete=False,
                 provider_success=success, model_calls=1, corrections=0, model="qwen" if success else "rules-only (model unavailable)",
                 ms=1, must_flag_missing=[], model_findings=0, model_discarded=0)
            for label, flag, success in [("phishing", False, False), ("phishing", True, True),
                                          ("legit", False, True), ("legit", True, False)]]
    result = ev.summarize(rows)
    assert {k: result["all_input_warnings"][k] for k in ("tp", "fp", "tn", "fn")} == dict(tp=1, fp=1, tn=1, fn=1)
    assert result["complete_only_warnings"]["n"] == 0
    assert result["provider_success_warnings"]["n"] == 2
    assert result["outcomes_by_label"]["phishing"]["unfinished_no_findings"] == 1
    assert result["completion_coverage"]["rate"] == 0
    assert ev.rate(0, 0)["wilson95"] is None
    assert ev.rate(5, 10)["wilson95"][0] < .5 < ev.rate(5, 10)["wilson95"][1]
    assert not ev.flagged(SimpleNamespace(findings=[], assessment="insufficient_evidence"))


def test_gmail_partial_view_preserves_input():
    case = {"request": {"reply_to": "x", "attachments": [], "authentication_results": "pass",
                        "extraction_limitations": ["original"]}}
    req = ev.request_for(case, "gmail")
    assert not req["extraction_complete"]
    assert all(k not in req for k in ev.HEADER_FIELDS)
    assert req["extraction_limitations"][0] == "original"
    assert case["request"]["extraction_limitations"] == ["original"]


@pytest.mark.parametrize("tune,test", [(["a", "a"], ["b"]), (["a"], ["a", "b"]),
                                         (["a"], []), (["a"], ["missing"])])
def test_invalid_split_rejected(tmp_path, tune, test):
    for name in ("a", "b"):
        (tmp_path / f"{name}.json").write_text("{}", encoding="utf-8")
    manifest = tmp_path / "split.txt"
    manifest.write_text(json.dumps(dict(tune=tune, test=test)), encoding="utf-8")
    with pytest.raises(ValueError):
        ev.selected_paths(tmp_path, "test", manifest)
    with pytest.raises(ValueError):
        ev.selected_paths(tmp_path, "test")


def test_journal_completed_resume_and_uncertain_block(tmp_path):
    path = tmp_path / "run.jsonl"
    journal = ev.Journal(path, {"model": "qwen"})
    journal.append({"event": "attempted", "key": "gmail/a"})
    journal.append({"event": "provider_call", "key": "gmail/a", "number": 1})
    with pytest.raises(ValueError, match="uncertain"):
        ev.Journal(path, {"model": "qwen"})
    journal.append({"event": "completed", "key": "gmail/a", "row": {"id": "a"}})
    resumed = ev.Journal(path, {"model": "qwen"})
    assert ev._one(tmp_path / "a.json", "gmail", lambda *_: pytest.fail("replayed"), resumed) == {"id": "a"}
    with pytest.raises(ValueError, match="mismatch"):
        ev.Journal(path, {"model": "other"})


def test_provider_count_and_fallback_are_not_success(tmp_path, monkeypatch):
    case = tmp_path / "a.json"
    case.write_text(json.dumps({"request": {"email_id": "a"}, "expected": {"label": "legit"}}), encoding="utf-8")
    monkeypatch.setattr(ev.AnalyzeRequest, "model_validate", lambda value: value)
    monkeypatch.setattr(ev.llm, "model_label", lambda *_: "tinker:qwen")
    journal = ev.Journal(tmp_path / "run.jsonl", {"model": "tinker:qwen"})
    def fake_analyze(req, call):
        assert "attempted" in journal.path.read_text(encoding="utf-8")
        call("system", "first")
        call("system", "correction")
        return SimpleNamespace(findings=[], assessment="insufficient_evidence", verdict={}, risk_score=0,
                               limitations=[], model="rules-only (model unavailable)", analysis_complete=False)
    monkeypatch.setattr(ev, "analyze", fake_analyze)
    row = ev._one(case, "gmail", lambda *_: "unused", journal)
    assert row["model_calls"] == 2 and row["corrections"] == 1
    assert not row["provider_success"] and not row["flagged"]
    assert ev.Journal(journal.path, {"model": "tinker:qwen"}).completed["gmail/a"] == row


def test_fingerprint_changes_for_prompt_and_input(tmp_path, monkeypatch):
    case = tmp_path / "a.json"
    case.write_text('{"request":{"email_id":"a"}}', encoding="utf-8")
    monkeypatch.setattr(ev.prompts, "analyze_prompt", lambda: ("first", {}))
    first = ev.provenance([case], ["gmail"], "qwen", None)
    monkeypatch.setattr(ev.prompts, "analyze_prompt", lambda: ("second", {}))
    assert ev.digest(first) != ev.digest(ev.provenance([case], ["gmail"], "qwen", None))
    case.write_text('{"request":{"email_id":"b"}}', encoding="utf-8")
    assert first["input_hashes"] != ev.provenance([case], ["gmail"], "qwen", None)["input_hashes"]


@pytest.mark.parametrize("value", ["gmail,gmail", "invalid", "", "gmail,"])
def test_views_refuse_accidental_extra_paid_passes(value):
    with pytest.raises(ValueError):
        ev.parse_views(value)
    assert ev.parse_views("gmail") == ["gmail"]
    assert ev.parse_views("full,gmail") == ["full", "gmail"]


def test_provenance_labels_actual_tinker_default(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    path = tmp_path / "a.json"
    path.write_text('{"request":{"email_id":"a"}}', encoding="utf-8")
    record = ev.provenance([path], ["gmail"], "tinker:qwen", None)
    assert record["prompt_version"] == "v3"
    assert record["prompt_hash"] == ev.digest(ev.prompts.ANALYZE_SYSTEM_V3)
