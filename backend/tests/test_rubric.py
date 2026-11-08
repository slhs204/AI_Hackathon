import json
from pathlib import Path

from app.analyze import analyze
from app.schemas import AnalyzeRequest

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "emails"


def load(name):
    return AnalyzeRequest.model_validate(json.loads((FIXTURES / f"{name}.json").read_text())["request"])


def dims(r):
    return {d["key"]: d["status"] for d in r.dimensions}


def test_four_questions_are_always_answered():
    r = analyze(load("x-legit-internal-reminder"))
    assert dims(r) == {"sender": "unknown", "money": "ok", "pressure": "ok", "links": "ok"}
    assert r.verdict["key"] == "verify"


def test_money_plus_untrusted_sender_is_red():
    r = analyze(load("vendor-bank-change"))
    assert dims(r)["money"] == "warn" and dims(r)["sender"] == "warn"
    assert r.verdict["key"] == "stop"


def test_money_alone_is_amber_never_green():
    r = analyze(load("x-ambiguous-internal-change"))
    assert [k for k, v in dims(r).items() if v == "warn"] == ["money"]
    assert r.verdict["key"] == "verify"


def test_warning_points_at_real_findings():
    r = analyze(load("ceo-wire"))
    ids = {f.id for f in r.findings}
    for d in r.dimensions:
        assert set(d["finding_ids"]) <= ids
        assert (d["status"] == "warn") == bool(d["finding_ids"])
