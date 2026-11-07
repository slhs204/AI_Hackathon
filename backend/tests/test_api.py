import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "emails"
BODY = json.loads((FIXTURES / "vendor-bank-change.json").read_text())["request"]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", "dev")
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    import main

    return TestClient(main.app, headers={"X-Demo-Token": "dev"})


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_analyze_with_token_runs_rules_only_in_mock_mode(client):
    r = client.post("/analyze", json=BODY)
    assert r.status_code == 200
    assert r.json()["model"] == "rules-only"


def test_no_token_configured_fails_closed(client, monkeypatch):
    monkeypatch.delenv("DEMO_API_TOKEN")
    assert client.post("/analyze", json=BODY).status_code == 503
    assert client.post("/challenge", json={"email": BODY, "finding_id": "f1", "context": "x"}).status_code == 503


def test_wrong_or_missing_token_is_rejected_before_any_model_call(client, monkeypatch):
    import main

    monkeypatch.setenv("DEMO_API_TOKEN", "s3cret")
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    called = []
    monkeypatch.setattr(main.llm, "_tinker_call", lambda s, u: called.append(1) or "{}")
    assert client.post("/analyze", json=BODY, headers={"X-Demo-Token": ""}).status_code == 401
    assert client.post("/analyze", json=BODY, headers={"X-Demo-Token": "nope"}).status_code == 401
    assert called == []


def test_correct_token_reaches_the_model(client, monkeypatch):
    import main

    monkeypatch.setenv("DEMO_API_TOKEN", "s3cret")
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    monkeypatch.setenv("TINKER_MODEL", "test-model")
    monkeypatch.setattr(main.llm, "default_call", lambda *a: (lambda s, u: json.dumps({"summary": "hi", "extra_findings": []})))
    r = client.post("/analyze", json=BODY, headers={"X-Demo-Token": "s3cret"})
    assert r.status_code == 200 and r.json()["summary"] == "hi"


def test_oversized_and_invalid_requests(client):
    big = dict(BODY, blocks=[{"id": f"b{i}", "text": "x" * 3000} for i in range(10)])
    assert client.post("/analyze", json=big).status_code == 422  # over MAX_TOTAL_CHARS
    dup = dict(BODY, blocks=[{"id": "b1", "text": "a"}, {"id": "b1", "text": "b"}])
    assert client.post("/analyze", json=dup).status_code == 422


def test_cors_allows_mail_clients_only(client):
    for origin in ("https://mail.google.com", "https://outlook.office.com", "https://outlook.live.com",
                   "chrome-extension://abcdefghijklmnopabcdefghijklmnop"):
        r = client.options("/analyze", headers={"Origin": origin, "Access-Control-Request-Method": "POST",
                                                "Access-Control-Request-Headers": "content-type,x-demo-token"})
        assert r.headers.get("access-control-allow-origin") == origin
    r = client.options("/analyze", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert r.headers.get("access-control-allow-origin") != "https://evil.example"


def test_challenge_endpoint(client):
    analysis = client.post("/analyze", json=BODY).json()
    finding = next(f for f in analysis["findings"] if f["category"] == "payment_or_data_request")
    r = client.post("/challenge", json={"email": BODY, "finding": finding, "user_context": "I called them on the number on file."})
    assert r.status_code == 200
    assert r.json()["assessment"] in ("still_concerning", "less_concerning")
