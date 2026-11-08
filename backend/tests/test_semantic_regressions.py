"""Synthetic controls only; no benchmark inputs or live calls."""
import pytest
from app import prompts
from phishhook.engine import detect_payment

@pytest.mark.parametrize("text", ["Our bank details have not changed.", "Our remittance details are unchanged.", "We will never ask you to change bank details by email."])
def test_negated_bank_statement_is_not_payment(text):
    assert detect_payment({"subject": "Notice", "body": text}) is None

@pytest.mark.parametrize("tail", [". Please use our new account details for payments.", ", but use our new bank account for payment.", "; verify your password on this page.", ". Please wire transfer the balance."])
def test_negation_does_not_hide_another_request(tail):
    finding = detect_payment({"subject": "Notice", "body": "Our bank details have not changed" + tail})
    assert finding
    assert all(m["quote"].lower() != "bank details" for m in finding["marks"])

@pytest.mark.parametrize("provider,version", [("tinker", "v3"), ("anthropic", "v1"), ("mock", "v1")])
def test_provider_default(monkeypatch, provider, version):
    monkeypatch.delenv("PROMPT_VERSION", raising=False)
    monkeypatch.setenv("MODEL_PROVIDER", provider)
    assert prompts.analyze_prompt() == prompts.analyze_prompt(version)

@pytest.mark.parametrize("version", ["v1", "v2"])
def test_explicit_versions_remain(monkeypatch, version):
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    monkeypatch.setenv("PROMPT_VERSION", version)
    assert prompts.analyze_prompt() == prompts.analyze_prompt(version)

def test_v3_uses_v2_contract():
    assert prompts.analyze_prompt("v3")[1] is prompts.ANALYZE_SCHEMA_V2


def test_negative_marks_cannot_hide_a_later_request():
    text = "Our bank details have not changed. " * 8 + "Use our new account details."
    assert detect_payment({"subject": "Notice", "body": text})


def test_partial_routine_deadline_is_note_not_warning():
    from app.analyze import analyze
    from app.schemas import AnalyzeRequest
    email = AnalyzeRequest.model_validate({"email_id": "synthetic-deadline", "sender": {"name": "Team", "address": "team@example.org"}, "subject": "Schedule", "blocks": [{"id": "b1", "text": "Please submit your timesheet today."}], "links": [], "extraction_complete": False})
    result = analyze(email)
    assert not result.findings
    assert result.notes
    assert not result.analysis_complete
    assert result.assessment == "insufficient_evidence"
    assert result.verdict["key"] != "pay"


@pytest.mark.parametrize("body,risky", [
    ("Please submit your timesheet today.", False),
    ("Please verify your password today.", True),
    ("Use our new bank account today.", True),
    ("Keep this confidential today.", True),
])
def test_partial_deadline_keeps_identity_and_actual_risk(body, risky):
    from app.analyze import analyze
    from app.schemas import AnalyzeRequest
    from phishhook.engine import DIRECTORY
    email = AnalyzeRequest.model_validate({"email_id": "synthetic-pair", "sender": {"name": DIRECTORY["company"]["executives"][0]["name"], "address": "outsider@gmail.com"}, "subject": "Schedule", "blocks": [{"id": "b1", "text": body}], "extraction_complete": False})
    result = analyze(email)
    cats = {f.category for f in result.findings}
    assert cats & {"sender_impersonation", "authority_impersonation"}
    assert ("urgency_pressure" in cats) == risky
    assert not result.analysis_complete
    assert result.verdict["key"] != "pay"
    if not risky:
        assert result.risk_score == sum(f.points for f in result.findings)
        assert sum(st["score"] for st in result.stages) == result.risk_score


@pytest.mark.parametrize("verb", ["Send", "Remit", "Direct", "Route"])
@pytest.mark.parametrize("scope", ["all upcoming", "this and future"])
def test_actual_payment_redirection(verb, scope):
    text = f"{verb} {scope} payments to our new account at the local branch."
    finding = detect_payment({"subject": "Notice", "body": text})
    assert finding and finding["money"]


def test_opening_account_is_not_payment_redirection():
    assert detect_payment({"subject": "Notice", "body": "We are opening a new account at the local branch."}) is None


def test_pressure_demotion_recomputes_pre_cap_score():
    from app.analyze import analyze
    from app.schemas import AnalyzeRequest
    from phishhook.engine import DIRECTORY
    email = AnalyzeRequest.model_validate({"sender": {"name": DIRECTORY["company"]["executives"][0]["name"], "address": "fake@acme-payroll-help.example"}, "reply_to": "fraud@elsewhere.example", "authentication_results": "spf=fail dkim=fail dmarc=fail", "subject": "Schedule", "blocks": [{"id": "b1", "text": "Please submit timesheets today."}], "extraction_complete": False})
    result = analyze(email)
    assert result.notes
    assert sum(f.points for f in result.findings) == 95
    assert result.risk_score == 95
    assert sum(st["score"] for st in result.stages) == 95
