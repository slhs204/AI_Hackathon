import types

import pytest

from eval import smoke_tinker


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("TINKER_API_KEY", "test-only-never-live")
    monkeypatch.setenv("TINKER_MODEL", "test-checkpoint")
    monkeypatch.setattr(smoke_tinker.importlib.util, "find_spec", lambda name: object())


def test_missing_configuration_never_calls(monkeypatch):
    monkeypatch.delenv("TINKER_API_KEY", raising=False)
    monkeypatch.delenv("TINKER_MODEL", raising=False)
    monkeypatch.setattr(smoke_tinker.llm, "_tinker_call", lambda *a: pytest.fail("network call"))
    assert smoke_tinker.main(["--allow-paid"]) == 2


def test_default_and_preflight_do_not_call(configured, monkeypatch, capsys):
    monkeypatch.setattr(smoke_tinker.llm, "_tinker_call", lambda *a: pytest.fail("network call"))
    assert smoke_tinker.main([]) == 0
    assert smoke_tinker.main(["--preflight"]) == 0
    output = capsys.readouterr().out
    assert "PREFLIGHT ONLY" in output
    assert "test-only-never-live" not in output


@pytest.mark.parametrize("reply", ["bad", "{}", '{"ok":false}', '{"ok":1}'])
def test_tiny_bad_response_fails_before_analysis(configured, monkeypatch, reply):
    monkeypatch.setattr(smoke_tinker.llm, "_tinker_call", lambda *a: reply)
    monkeypatch.setattr(smoke_tinker, "analyze", lambda *a: pytest.fail("analysis must not run"))
    assert smoke_tinker.main(["--allow-paid"]) == 1


@pytest.mark.parametrize("model,complete,summary,expected", [
    ("rules-only (model unavailable)", False, "", 1),
    ("tinker:test-checkpoint", False, "summary", 1),
    ("tinker:test-checkpoint", True, "", 1),
    ("tinker:test-checkpoint", True, "summary", 0),
])
def test_analysis_must_really_succeed(configured, monkeypatch, model, complete, summary, expected):
    monkeypatch.setattr(smoke_tinker.llm, "_tinker_call", lambda *a: '{"ok":true}')
    monkeypatch.setattr(smoke_tinker, "analyze", lambda *a: types.SimpleNamespace(
        model=model, analysis_complete=complete, elapsed_ms=1, summary=summary, findings=[]))
    assert smoke_tinker.main(["--allow-paid"]) == expected
