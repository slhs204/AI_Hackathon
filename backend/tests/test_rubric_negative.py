"""Negative cases from the team's review of rubric v2 (2026-11-08). The rubric may only make a
verdict stricter than the score-based one, never looser, and must say "can't tell" when it can't."""
import json
from pathlib import Path

import pytest

from app import analyze as analyze_mod
from app import llm
from app.analyze import analyze
from app.schemas import AnalyzeRequest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
RANK = {"pay": 0, "verify": 1, "stop": 2}


def req(**kw):
    base = {"email_id": "neg", "sender": {"name": "", "address": ""}, "subject": "", "blocks": [], "links": []}
    return AnalyzeRequest.model_validate({**base, **kw})


def dims(r):
    return {d["key"]: d["status"] for d in r.dimensions}


@pytest.mark.parametrize("name,address", [
    ("Microsoft Security", "ms.security.alerts@gmail.com"),
    ("Apple Support", "apple.support.team@icloud.com"),
    ("PayPal Service", "paypal-service@outlook.com"),
])
def test_neg_a_brand_display_name_from_free_mail_is_never_pay(name, address):
    r = analyze(req(sender={"name": name, "address": address}, subject="Unusual sign-in activity",
                    blocks=[{"id": "b1", "text": "We detected an unusual sign-in. Review your recent activity to keep your account safe."}]))
    assert r.verdict["key"] != "pay"
    assert dims(r)["sender"] == "warn"


CEO_EXE = dict(
    sender={"name": "Jane Whitfield", "address": "jane.whitfield.ceo@gmail.com"},
    subject="Urgent - confidential",
    blocks=[{"id": "b1", "text": "I'm stuck in a board meeting and can't take calls. Urgent: install this before 5pm today "
                                 "and keep this confidential: https://bit.ly/q3-board"}],
    links=[{"id": "l1", "block_id": "b1", "display_text": "https://bit.ly/q3-board", "href": "https://bit.ly/q3-board"}],
    attachments=[{"name": "board_pack.pdf.exe"}],
)


def test_neg_b_high_risk_ceo_with_link_and_exe_stays_stop():
    r = analyze(req(**CEO_EXE))
    assert r.risk_score >= 70
    assert r.verdict["key"] == "stop"
    assert dims(r)["sender"] == "warn"


@pytest.mark.parametrize("email", [
    {},                                                         # empty email
    {"blocks": [{"id": "b1", "text": "   "}]},                  # whitespace only
    {"subject": "Invoice", "blocks": [{"id": "b1", "text": "Please see the attached invoice."}]},  # no sender address
])
def test_neg_c_incomplete_input_is_unknown_not_pay(email):
    r = analyze(req(**email))
    assert r.verdict["key"] == "verify"
    assert r.verdict.get("state") == "unknown"
    assert any(d["status"] == "unknown" for d in r.dimensions)
    assert not all(d["status"] == "ok" for d in r.dimensions)


def test_neg_c_model_failure_is_unknown_not_pay():
    def broken(system, user):
        raise llm.ModelUnavailable("simulated outage")
    r = analyze(req(sender={"name": "Payroll", "address": "payroll@acme-corp.com"}, subject="Reminder",
                    blocks=[{"id": "b1", "text": "Timesheets are due Friday."}]), broken)
    assert r.verdict["key"] == "verify"
    assert r.verdict.get("state") == "unknown"
    assert not all(d["status"] == "ok" for d in r.dimensions)


def _all_fixture_requests():
    for folder in ("emails", "blind"):
        for path in sorted((FIXTURES / folder).glob("*.json")):
            yield path.stem, json.loads(path.read_text())["request"]


def test_neg_d_rubric_never_loosens_the_score_verdict():
    seen = 0
    for name, body in _all_fixture_requests():
        for view in ("full", "gmail"):
            b = dict(body)
            if view == "gmail":
                for k in ("reply_to", "authentication_results", "attachments"):
                    b.pop(k, None)
            r = analyze(AnalyzeRequest.model_validate(b))
            legacy = analyze_mod._score_verdict(r.risk_score, r.findings, r.analysis_complete)
            assert RANK[r.verdict["key"]] >= RANK[legacy["key"]], (name, view, r.verdict, legacy)
            seen += 1
    assert seen > 200


def test_neg_d_invariant_is_enforced_in_code():
    stricter = analyze_mod._stricter
    assert stricter({"key": "pay"}, {"key": "stop"})["key"] == "stop"
    assert stricter({"key": "verify"}, {"key": "pay"})["key"] == "verify"


# --- de63312 alignment: rubric is the quick read / fallback, it must not undo the model's gating -------------

def _model(email_type):
    def call(system, user):
        return json.dumps({"email_type": email_type, "summary": "s", "explanations": [], "extra_findings": [{
            "category": "manipulation_cue", "block_id": "b1", "quote": "before Friday's payroll",
            "explanation": "x", "next_action": "y", "requested_action": "change deposit", "confidence": "high"}]})
    return call


def _ambiguous():
    return AnalyzeRequest.model_validate(json.loads((FIXTURES / "emails" / "x-ambiguous-internal-change.json").read_text())["request"])


def test_routine_notification_with_one_rule_sign_is_at_most_amber():
    r = analyze(_ambiguous(), _model("routine_notification"))
    assert dims(r)["money"] == "warn" and dims(r)["pressure"] == "warn"
    assert r.verdict["key"] == "verify"


def test_same_email_without_routine_label_is_red():
    r = analyze(_ambiguous(), _model("needs_check"))
    assert r.verdict["key"] == "stop"


def test_routine_label_never_lowers_a_score_stop():
    r = analyze(req(**CEO_EXE), _model("routine_notification"))
    assert r.risk_score >= 70 and r.verdict["key"] == "stop"


def test_pressure_words_alone_stay_a_note_but_do_not_authenticate_sender():
    r = analyze(AnalyzeRequest.model_validate(json.loads((FIXTURES / "emails" / "h-legit-urgent-cutoff.json").read_text())["request"]))
    assert r.notes and r.findings == []
    assert dims(r)["pressure"] == "ok" and "note" in next(d["answer"] for d in r.dimensions if d["key"] == "pressure")
    assert r.verdict["key"] == "verify"
