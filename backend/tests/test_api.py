import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "emails"
BODY = json.loads((FIXTURES / "vendor-bank-change.json").read_text())["request"]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("DEMO_API_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    import main

    return TestClient(main.app)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_analyze_without_token_config_runs_rules_only(client):
    r = client.post("/analyze", json=BODY)
    assert r.status_code == 200
    assert r.json()["model"] == "rules-only"


def test_wrong_or_missing_token_is_rejected_before_any_model_call(client, monkeypatch):
    import main

    monkeypatch.setenv("DEMO_API_TOKEN", "s3cret")
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    called = []
    monkeypatch.setattr(main.llm, "_tinker_call", lambda s, u: called.append(1) or "{}")
    assert client.post("/analyze", json=BODY).status_code == 401
    assert client.post("/analyze", json=BODY, headers={"X-Demo-Token": "nope"}).status_code == 401
    assert called == []


def test_paid_model_is_disabled_when_no_token_is_configured(client, monkeypatch):
    import main

    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    called = []
    monkeypatch.setattr(main.llm, "_tinker_call", lambda s, u: called.append(1) or "{}")
    r = client.post("/analyze", json=BODY)
    assert r.status_code == 200 and called == []


def test_correct_token_reaches_the_model(client, monkeypatch):
    import main

    monkeypatch.setenv("DEMO_API_TOKEN", "s3cret")
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    monkeypatch.setenv("TINKER_MODEL", "test-model")
    monkeypatch.setattr(main.llm, "default_call", lambda: (lambda s, u: json.dumps({"summary": "hi", "extra_findings": []})))
    r = client.post("/analyze", json=BODY, headers={"X-Demo-Token": "s3cret"})
    assert r.status_code == 200 and r.json()["summary"] == "hi"


def test_oversized_and_invalid_requests(client):
    big = dict(BODY, blocks=[{"id": f"b{i}", "text": "x" * 3000} for i in range(10)])
    assert client.post("/analyze", json=big).status_code == 422  # over MAX_TOTAL_CHARS
    dup = dict(BODY, blocks=[{"id": "b1", "text": "a"}, {"id": "b1", "text": "b"}])
    assert client.post("/analyze", json=dup).status_code == 422


def test_cors_allows_gmail_and_token_header(client):
    r = client.options("/analyze", headers={"Origin": "https://mail.google.com",
                                            "Access-Control-Request-Method": "POST",
                                            "Access-Control-Request-Headers": "content-type,x-demo-token"})
    assert r.headers.get("access-control-allow-origin") == "https://mail.google.com"


def test_challenge_endpoint(client):
    analysis = client.post("/analyze", json=BODY).json()
    finding = next(f for f in analysis["findings"] if f["category"] == "payment_or_data_request")
    r = client.post("/challenge", json={"email": BODY, "finding": finding, "user_context": "I called them on the number on file."})
    assert r.status_code == 200
    assert r.json()["assessment"] in ("still_concerning", "less_concerning")
