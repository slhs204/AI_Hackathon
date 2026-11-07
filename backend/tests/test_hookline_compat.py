"""Requests shaped exactly like Jenessa's Hookline extension sends them
(chrome_extension/content.js and sidepanel.js DEMO_EMAIL)."""

import pytest
from fastapi.testclient import TestClient

HOOKLINE_DEMO = {
    "email_id": "demo-001",
    "sender": {"name": "Payroll Support", "address": "support@example.test"},
    "subject": "Urgent account update",
    "blocks": [{"id": "b1", "text": "Hello, Please change my salary account today. This is urgent. Do not tell anyone until it is complete."}],
    "links": [],
}

HOOKLINE_GMAIL = {
    "email_id": "gmail-abc123",
    "sender": {"name": "DocuSign", "address": "dse@docusign-secure.example"},
    "subject": "Please review and sign: Payroll Policy 2026",
    "blocks": [{"id": "b1", "text": "You have a document waiting.\nREVIEW DOCUMENT\nOr visit www.docusign.com to sign in."}],
    "links": [
        {"id": "l1", "text": "REVIEW DOCUMENT", "url": "http://203.0.113.9/sign"},
        {"id": "l2", "text": "www.docusign.com", "url": "https://docusign-login.example/auth"},
    ],
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("DEMO_API_TOKEN", raising=False)
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    import main

    return TestClient(main.app)


def test_link_names_text_url_are_accepted(client):
    r = client.post("/analyze", json=HOOKLINE_GMAIL)
    assert r.status_code == 200
    links = [f for f in r.json()["findings"] if f["evidence"]["kind"] == "link" or f["category"] == "deceptive_link"]
    assert links, "links sent as {text,url} must still be checked"


def test_every_finding_has_title_and_quote(client):
    body = client.post("/analyze", json=HOOKLINE_GMAIL).json()
    for f in body["findings"]:
        assert f["title"]
        assert f["evidence"].get("quote"), f


def test_link_evidence_points_at_a_highlightable_substring_of_b1(client):
    body = client.post("/analyze", json=HOOKLINE_GMAIL).json()
    text = HOOKLINE_GMAIL["blocks"][0]["text"]
    for f in body["findings"]:
        ev = f["evidence"]
        if ev.get("block_id") == "b1":
            assert ev["quote"] in text  # Hookline uses a plain, case-sensitive includes()


def test_demo_email_gets_findings_and_disclaimer(client):
    body = client.post("/analyze", json=HOOKLINE_DEMO).json()
    assert body["disclaimer"]
    assert body["summary"] is not None
    cats = {f["category"] for f in body["findings"]}
    assert "urgency_pressure" in cats


def test_long_single_block_body_is_accepted(client):
    long = dict(HOOKLINE_DEMO, blocks=[{"id": "b1", "text": "Routine update. " * 600}])  # ~9,600 chars in one block
    assert client.post("/analyze", json=long).status_code == 200


def test_challenge_with_finding_id_and_context(client):
    analysis = client.post("/analyze", json=HOOKLINE_DEMO).json()
    fid = analysis["findings"][0]["id"]
    r = client.post("/challenge", json={"email": HOOKLINE_DEMO, "finding_id": fid, "context": "I called them yesterday."})
    assert r.status_code == 200
    data = r.json()
    assert data["explanation"] and data["next_action"] and data["finding_id"] == fid


def test_challenge_with_unknown_finding_id_is_422(client):
    r = client.post("/challenge", json={"email": HOOKLINE_DEMO, "finding_id": "f99", "context": "x"})
    assert r.status_code == 422


def test_demo_salary_account_request_is_caught_with_bank_policy(client):
    body = client.post("/analyze", json=HOOKLINE_DEMO).json()
    pay = [f for f in body["findings"] if f["category"] == "payment_or_data_request"]
    assert pay and pay[0]["evidence"]["quote"] == "change my salary account"
    assert pay[0]["policy_id"] == "bank_account_change"
