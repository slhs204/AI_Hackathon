"""Regression cases for incomplete extraction and false-safe UI decisions. No paid calls."""
import json

import pytest
from fastapi.testclient import TestClient

import main
from app.analyze import analyze
from app.schemas import AnalyzeRequest


def email(text="A routine update.", **extra):
    return AnalyzeRequest.model_validate({"sender": {"address": "stranger@example.net"},
        "subject": "Update", "blocks": [{"id": "b1", "text": text}], **extra})


@pytest.mark.parametrize("address", ["unknown", "", "stranger@example.net", "payroll@acme-corp.com"])
def test_sender_absence_of_warning_does_not_authenticate(address):
    result = analyze(email(sender={"address": address}))
    assert result.verdict["key"] != "pay"
    assert next(d for d in result.dimensions if d["key"] == "sender")["status"] == "unknown"


@pytest.mark.parametrize("payload", [{}, {"extra_findings": None}, {"extra_findings": {}},
    {"extra_findings": [], "summary": {}}, {"extra_findings": [], "email_type": "safe"},
    {"extra_findings": [None]}, {"extra_findings": [{"quote": 42}]},
    {"extra_findings": [], "explanations": [{"category": [], "text": "x"}]}])
def test_malformed_json_object_is_not_success(payload):
    calls = []
    def fake(system, user):
        calls.append(1)
        return json.dumps(payload)
    result = analyze(email(), fake)
    assert len(calls) == 2
    assert result.model == "rules-only (model unavailable)"
    assert not result.analysis_complete
    assert result.assessment == "insufficient_evidence"
    assert result.verdict["key"] != "pay"


@pytest.mark.parametrize("text", ["Urgent: sign in to review this today.",
    "Urgent: download the document today.", "Urgent: open the secure attachment today.",
    "Urgent: keep this confidential today.", "Urgent: verify your details today."])
def test_pressure_with_risky_action_is_not_demoted(text):
    result = analyze(email(text))
    assert any(f.category == "urgency_pressure" for f in result.findings)
    assert not result.notes
    assert result.verdict["key"] != "pay"


def test_partial_extraction_is_incomplete_even_without_findings():
    result = analyze(email(extraction_complete=False,
                           extraction_limitations=["Visible Gmail body only; attachments unavailable."]))
    assert not result.analysis_complete
    assert result.assessment == "insufficient_evidence"
    assert result.verdict["key"] != "pay"
    assert any("attachments unavailable" in x for x in result.limitations)


@pytest.mark.parametrize("route,payload", [
    ("/analyze", email().model_dump()),
    ("/triage", {"emails": [{"email_id": "one"}]}),
    ("/challenge", {"email": email().model_dump(), "finding_id": "f1", "context": "A check"}),
])
def test_rules_only_header_stops_before_provider_selection(monkeypatch, route, payload):
    monkeypatch.setenv("DEMO_API_TOKEN", "test-token")
    monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
    def forbidden(*args):
        pytest.fail("model selection must not run")
    monkeypatch.setattr(main, "model_for_request", forbidden)
    response = TestClient(main.app).post(route, json=payload,
        headers={"X-Demo-Token": "test-token", "X-Require-Rules-Only": "1"})
    assert response.status_code == 409


@pytest.mark.parametrize("payload", [{}, {"items": 42}, {"items": [{"email_id": "one", "priority": [], "reason": {}}]}])
def test_malformed_triage_response_falls_back(payload):
    from app.triage import triage
    from app.schemas import TriageRequest
    result = triage(TriageRequest.model_validate({"emails": [{"email_id": "one"}]}),
                    lambda *_: json.dumps(payload))
    assert result.model == "rules-only (model unavailable)"
    assert result.items[0].source == "rules"


def test_malformed_challenge_text_does_not_become_user_advice():
    from app.challenge import challenge
    from app.schemas import ChallengeRequest
    req_email = email("Please change my salary account today.")
    finding = next(f for f in analyze(req_email).findings if f.category == "payment_or_data_request")
    result = challenge(ChallengeRequest(email=req_email, finding=finding, user_context="I know them."),
        lambda *_: json.dumps({"assessment": "less_concerning", "message": {"safe": True},
                               "still_unresolved": []}))
    assert result.model == "rules-only (model unavailable)"
    assert result.assessment == "still_concerning"
    assert "Procedure:" in result.still_unresolved


@pytest.mark.parametrize("token,status", [("test-token", 200), ("", 401), ("wrong", 401)])
def test_session_validates_token_without_email(monkeypatch, token, status):
    monkeypatch.setenv("DEMO_API_TOKEN", "test-token")
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    def forbidden(*args):
        pytest.fail("session must not select or call a model")
    monkeypatch.setattr(main, "model_for_request", forbidden)
    response = TestClient(main.app).get("/session", headers={
        "X-Demo-Token": token, "X-Require-Rules-Only": "1"})
    assert response.status_code == status
    if status == 200:
        assert response.json() == main.health()
        assert response.json()["model"]["analyze"] == "rules-only"


def test_session_rejects_nonmock_without_model_calls(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", "test-token")
    monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
    def forbidden(*args):
        pytest.fail("session must not select or call a model")
    monkeypatch.setattr(main, "model_for_request", forbidden)
    response = TestClient(main.app).get("/session", headers={
        "X-Demo-Token": "test-token", "X-Require-Rules-Only": "1"})
    assert response.status_code == 409


@pytest.mark.parametrize("version,missing", [("v1", "summary"), ("v1", "explanations"),
    ("v1", "extra_findings"), ("v2", "email_type"), ("v2", "summary"), ("v2", "explanations")])
def test_selected_schema_required_fields_fail_closed(monkeypatch, version, missing):
    monkeypatch.setenv("PROMPT_VERSION", version)
    payload = {"summary": "Update", "explanations": [], "extra_findings": [], "email_type": "routine_notification"}
    del payload[missing]
    result = analyze(email(), lambda *_: json.dumps(payload))
    assert not result.analysis_complete
    assert result.model == "rules-only (model unavailable)"


@pytest.mark.parametrize("missing", ["requested_action", "confidence", "quote", "category", "explanation", "next_action", "block_id"])
def test_v2_nested_required_fields_fail_closed(monkeypatch, missing):
    monkeypatch.setenv("PROMPT_VERSION", "v2")
    item = {"category": "manipulation_cue", "block_id": "b1", "quote": "A routine update",
            "explanation": "A concern", "next_action": "Check independently",
            "requested_action": "Open a link", "confidence": "high"}
    del item[missing]
    payload = {"summary": "Update", "explanations": [], "extra_findings": [item], "email_type": "needs_check"}
    result = analyze(email(), lambda *_: json.dumps(payload))
    assert not result.analysis_complete
    assert result.model == "rules-only (model unavailable)"


def test_explicit_v1_schema_does_not_require_v2_fields(monkeypatch):
    monkeypatch.setenv("PROMPT_VERSION", "v1")
    result = analyze(email(), lambda *_: json.dumps({"summary": "Update", "explanations": [], "extra_findings": []}))
    assert result.analysis_complete
    assert result.model == "rules-only"  # fake provider, no paid calls

@pytest.mark.parametrize('provider', ['mock', 'anthropic'])
@pytest.mark.parametrize('route', ['/session', '/analyze'])
def test_tinker_permission_blocks_other_providers_before_selection(monkeypatch, provider, route):
    monkeypatch.setenv('DEMO_API_TOKEN', 'test-token')
    monkeypatch.setenv('MODEL_PROVIDER', provider)
    monkeypatch.setattr(main, 'model_for_request', lambda *args: pytest.fail('model selection must not run'))
    client = TestClient(main.app)
    headers = {'X-Demo-Token': 'test-token', 'X-Require-Tinker': '1'}
    response = client.get(route, headers=headers) if route == '/session' else client.post(route, json=email().model_dump(), headers=headers)
    assert response.status_code == 409

@pytest.mark.parametrize('route', ['/session', '/analyze', '/challenge', '/triage'])
def test_tinker_requires_explicit_permission_even_with_valid_token(monkeypatch, route):
    monkeypatch.setenv('DEMO_API_TOKEN', 'test-token')
    monkeypatch.setenv('MODEL_PROVIDER', 'tinker')
    monkeypatch.setattr(main, 'model_for_request', lambda *args: pytest.fail('model selection must not run'))
    client = TestClient(main.app)
    response = client.get(route, headers={'X-Demo-Token': 'test-token'}) if route == '/session' else client.post(route, json={}, headers={'X-Demo-Token': 'test-token'})
    assert response.status_code == 409

def test_tinker_failure_returns_incomplete_instead_of_clearance(monkeypatch):
    from app.llm import ModelUnavailable
    monkeypatch.setenv('DEMO_API_TOKEN', 'test-token')
    monkeypatch.setenv('MODEL_PROVIDER', 'tinker')
    monkeypatch.setenv('TINKER_MODEL', 'test-sampler')
    def unavailable(*args):
        raise ModelUnavailable('test outage')
    monkeypatch.setattr(main, 'model_for_request', lambda *args: unavailable)
    response = TestClient(main.app).post('/analyze', json=email().model_dump(), headers={'X-Demo-Token':'test-token','X-Require-Tinker':'1'})
    assert response.status_code == 200
    body = response.json()
    assert body['analysis_complete'] is False
    assert body['model'] == 'rules-only (model unavailable)'
    assert body['verdict']['key'] != 'pay'
