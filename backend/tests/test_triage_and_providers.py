import json
import sys
import types

import pytest
from fastapi.testclient import TestClient

from app import llm, prompts
from app.schemas import TriageRequest
from app.triage import triage

INBOX = {"emails": [
    {"email_id": "m1", "sender": {"name": "Jane Whitfield", "address": "jane.whitfield.ceo@gmail.com"},
     "subject": "Wire needed today", "snippet": "Process a wire of $9,000 today. Keep this confidential."},
    {"email_id": "m2", "sender": {"name": "Robert Chen", "address": "robert.chen@acme-corp.com"},
     "subject": "Draft handbook", "snippet": "Comments by Wednesday please."},
    {"email_id": "m3", "sender": {"name": "Payroll Desk", "address": "desk@payroll-help.example"},
     "subject": "Quick question", "snippet": "Can you look at the attached form?"},
]}


def fake(reply):
    calls = []

    def call(system, user):
        calls.append(user)
        return reply

    call.calls = calls
    return call


def test_rules_only_triage_orders_risk():
    r = triage(TriageRequest.model_validate(INBOX))
    pri = {i.email_id: i.priority for i in r.items}
    assert pri["m1"] == "high" and pri["m2"] == "low"
    assert [i.email_id for i in r.items] == ["m1", "m2", "m3"]
    assert "not mean safe" in r.notice


def test_model_can_raise_but_not_lower_priority():
    reply = json.dumps({"items": [
        {"email_id": "m1", "priority": "low", "reason": "looks fine"},          # must be ignored
        {"email_id": "m3", "priority": "high", "reason": "Unknown payroll sender with a form"},
        {"email_id": "zz", "priority": "high", "reason": "not in the inbox"},  # unknown id ignored
    ]})
    r = triage(TriageRequest.model_validate(INBOX), fake(reply))
    pri = {i.email_id: (i.priority, i.source) for i in r.items}
    assert pri["m1"] == ("high", "rules")
    assert pri["m3"] == ("high", "model")


def test_triage_sends_only_preview_fields():
    call = fake(json.dumps({"items": []}))
    triage(TriageRequest.model_validate(INBOX), call)
    sent = call.calls[0]
    assert "<<<INBOX" in sent and "Process a wire" in sent
    assert '"body"' not in sent


def test_triage_endpoint_and_limits(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", "dev")
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    import main

    c = TestClient(main.app, headers={"X-Demo-Token": "dev"})
    assert c.post("/triage", json=INBOX).status_code == 200
    too_many = {"emails": [{"email_id": f"m{i}", "subject": "x"} for i in range(51)]}
    assert c.post("/triage", json=too_many).status_code == 422
    assert c.post("/triage", json=INBOX, headers={"X-Demo-Token": "no"}).status_code == 401


# --- Anthropic provider (fake SDK, no network) --------------------------------

class _Block:
    def __init__(self, type_, text=""):
        self.type, self.text = type_, text


class _Resp:
    def __init__(self, text, stop="end_turn"):
        self.content = [_Block("thinking"), _Block("text", text)]
        self.stop_reason = stop


@pytest.fixture
def fake_anthropic(monkeypatch):
    seen = {}

    class Messages:
        def __init__(self, beta):
            self.beta = beta

        def create(self, **kw):
            seen.update(kw, beta=self.beta)
            return _Resp(seen.get("reply", '{"items": []}'), seen.get("stop", "end_turn"))

    class Client:
        def __init__(self, **kw):
            self.messages = Messages(False)
            self.beta = types.SimpleNamespace(messages=Messages(True))

    mod = types.SimpleNamespace(Anthropic=Client, APIConnectionError=type("E1", (Exception,), {}),
                                APIStatusError=type("E2", (Exception,), {}))
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
    return seen


def test_triage_uses_haiku_without_fallback(fake_anthropic):
    call = llm.default_call("triage", prompts.TRIAGE_SCHEMA)
    call("sys", "user")
    assert fake_anthropic["model"] == "claude-haiku-5-5"
    assert fake_anthropic["beta"] is False
    assert fake_anthropic["output_config"]["effort"] == "low"
    assert fake_anthropic["output_config"]["format"]["schema"] == prompts.TRIAGE_SCHEMA
    assert "temperature" not in fake_anthropic


def test_analysis_uses_sonnet_with_server_side_fallback(fake_anthropic):
    llm.default_call("analyze", prompts.ANALYZE_SCHEMA)("sys", "user")
    assert fake_anthropic["model"] == "claude-sonnet-5-5"
    assert fake_anthropic["beta"] is True and fake_anthropic["fallbacks"] == "default"
    assert fake_anthropic["betas"] == ["server-side-fallback-2026-07-01"]
    assert llm.model_label("analyze") == "anthropic:claude-sonnet-5-5"
    assert llm.model_label("triage") == "anthropic:claude-haiku-5-5"


def test_refusal_becomes_model_unavailable(fake_anthropic):
    fake_anthropic["stop"] = "refusal"
    with pytest.raises(llm.ModelUnavailable):
        llm.default_call("analyze", prompts.ANALYZE_SCHEMA)("sys", "user")


def test_model_names_can_be_overridden(fake_anthropic, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_ANALYSIS_MODEL", "claude-opus-5-5")
    llm.default_call("analyze", prompts.ANALYZE_SCHEMA)("sys", "user")
    assert fake_anthropic["model"] == "claude-opus-5-5" and fake_anthropic["beta"] is False


def test_schemas_are_strict_objects():
    for s in (prompts.ANALYZE_SCHEMA, prompts.CHALLENGE_SCHEMA, prompts.TRIAGE_SCHEMA):
        assert s["type"] == "object" and s["additionalProperties"] is False
        assert set(s["required"]) == set(s["properties"])


# --- error handling found in self-review ---------------------------------------

def test_sdk_error_without_credentials_becomes_model_unavailable(monkeypatch):
    class Client:
        def __init__(self, **kw):
            pass

        @property
        def messages(self):
            raise TypeError("Could not resolve authentication method")

    mod = types.SimpleNamespace(Anthropic=Client, APIConnectionError=type("E1", (Exception,), {}),
                                APIStatusError=type("E2", (Exception,), {}))
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_FALLBACKS", "0")
    with pytest.raises(llm.ModelUnavailable):
        llm.default_call("triage", prompts.TRIAGE_SCHEMA)("s", "u")


def test_no_retry_when_the_failure_is_not_bad_json():
    calls = []

    def refusing(system, user):
        calls.append(1)
        raise llm.ModelUnavailable("model declined the request")

    with pytest.raises(llm.ModelUnavailable):
        llm.call_json(refusing, "s", "u")
    assert len(calls) == 1  # a refusal or auth error would fail again and cost money


def test_bad_json_is_retried_once():
    calls = []

    def sloppy(system, user):
        calls.append(1)
        return "not json"

    with pytest.raises(llm.ModelOutputInvalid):
        llm.call_json(sloppy, "s", "u")
    assert len(calls) == 2


def test_post_without_content_length_is_refused(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", "dev")
    import main

    c = TestClient(main.app, headers={"X-Demo-Token": "dev"})

    def chunks():
        yield json.dumps(INBOX).encode()

    r = c.post("/triage", content=chunks(), headers={"Content-Type": "application/json"})
    assert r.status_code == 411
