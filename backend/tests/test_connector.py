import io
import json
import subprocess
from http.client import IncompleteRead
from urllib.error import HTTPError, URLError

import pytest
from fastapi.testclient import TestClient

import connector as c

SESSION = {"status": "ok", "service": "phishing-coach",
           "model": {task: "tinker:Qwen/Qwen3-8B" for task in ("triage", "analyze", "challenge")}}
HEADERS = {"X-Demo-Token": "local", "X-Require-Tinker": "1"}
BODY = {"blocks": [{"id": "b1", "text": "Test"}]}


class Reply(io.BytesIO):
    def __init__(self, data, code=200):
        super().__init__(data if isinstance(data, bytes) else json.dumps(data).encode())
        self.code = code


@pytest.fixture
def setup(monkeypatch):
    monkeypatch.setenv("DEMO_API_TOKEN", "local")
    monkeypatch.setenv("MODEL_PROVIDER", "tinker")
    monkeypatch.setenv("CLOUD_DEMO_TOKEN", "cloud")
    monkeypatch.delenv("CLOUD_RUN_URL", raising=False)
    calls = []
    replies = []
    monkeypatch.setattr(c, "mint_token", lambda: calls.append("mint") or "identity")

    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            assert timeout <= 35
            reply = replies.pop(0) if replies else Reply(SESSION)
            if isinstance(reply, Exception):
                raise reply
            return reply

    def opener(*handlers):
        assert handlers[0].proxies == {}
        assert handlers[1].redirect_request(None, None, None, None, None, "https://evil") is None
        return Opener()

    monkeypatch.setattr(c, "build_opener", opener)
    with TestClient(c.app) as client:
        calls.clear()
        yield client, calls, replies


def test_local_guards_and_routes_never_mint(setup, monkeypatch):
    client, calls, _ = setup
    for path in ("/session", "/analyze", "/challenge"):
        method = client.get if path == "/session" else client.post
        kwargs = {} if path == "/session" else {"json": BODY}
        for headers, code in (({}, 401), ({**HEADERS, "X-Demo-Token": "wrong"}, 401),
                              ({"X-Demo-Token": "local"}, 409),
                              ({**HEADERS, "X-Require-Rules-Only": "1"}, 409)):
            assert method(path, headers=headers, **kwargs).status_code == code
    for path in ("/triage", "/anything"):
        assert client.post(path, json=BODY, headers=HEADERS).status_code == 404
    assert calls == []
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    assert client.get("/session", headers=HEADERS).status_code == 409
    assert calls == []


def test_health_snapshot_and_header_replacement(setup):
    client, calls, _ = setup
    assert client.get("/health").json()["execution"] == "cloud-run"
    assert calls == []
    assert client.get("/session", headers={**HEADERS, "Authorization": "evil", "Cookie": "evil"}).status_code == 200
    request = calls[-1]
    assert dict(request.header_items()) == {"Authorization": "Bearer identity", "X-demo-token": "cloud",
                                           "X-require-tinker": "1", "Content-type": "application/json"}


@pytest.mark.parametrize("url", ["http://phish-staging-az465uxmla-uc.a.run.app", c.SERVICE_URL + "/",
    c.SERVICE_URL + ":443", c.SERVICE_URL + "?x", c.SERVICE_URL + "#x",
    "https://user@phish-staging-az465uxmla-uc.a.run.app", "https://evil.example"])
def test_invalid_host_refused_before_mint(setup, monkeypatch, url):
    client, calls, _ = setup
    monkeypatch.setenv("CLOUD_RUN_URL", url)
    assert client.get("/session", headers=HEADERS).status_code == 503
    assert calls == []


def test_tag_and_body_limits(setup, monkeypatch):
    client, calls, _ = setup
    monkeypatch.setenv("CLOUD_RUN_URL", c.SERVICE_URL.replace("https://", "https://a002-ai---"))
    assert client.get("/session", headers=HEADERS).status_code == 200
    calls.clear()
    assert client.post("/analyze", content=b"{}", headers={**HEADERS, "Content-Length": ""}).status_code == 411
    assert client.post("/analyze", content=b"x" * 200001, headers=HEADERS).status_code == 413
    assert calls == []


@pytest.mark.parametrize("reply,code,detail", [
    (Reply(b"<html>denied secret</html>", 403), 502, "sign-in"),
    (HTTPError(c.SERVICE_URL, 401, "Unauthorized", {}, io.BytesIO(b"IAM secret")), 502, "sign-in"),
    (Reply({"detail": "Explicit permission required"}, 409), 409, "Explicit permission"),
    (Reply(b"not json"), 502, "invalid response"),
    (Reply(b"x" * 200001), 502, "invalid response"),
    (Reply({}, 302), 502, "invalid response"),
    (Reply([]), 502, "invalid response"),
    (Reply({}), 502, "invalid analysis"),
    (URLError("secret address"), 502, "unavailable"),
    (TimeoutError("secret"), 504, "timed out"),
])
def test_upstream_failures_are_closed(setup, reply, code, detail):
    client, calls, replies = setup
    replies.append(reply)
    response = client.post("/analyze", json=BODY, headers=HEADERS)
    assert response.status_code == code
    assert detail in response.json()["detail"]
    assert "secret" not in response.text
    assert len(calls) == 2  # No automatic retry.


def test_successful_schema_and_challenge(setup):
    client, _, replies = setup
    replies.append(Reply({"finding_id": "f1", "assessment": "less_concerning", "message": "m",
                          "still_unresolved": "u", "next_action": "n", "explanation": "e", "model": "tinker:test"}))
    response = client.post("/challenge", json={"email": BODY, "finding_id": "f1", "context": "verified"}, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["execution"] == "cloud-run"


def test_successful_analysis(setup):
    client, _, replies = setup
    replies.append(Reply({"analysis_id": "a1", "assessment": "needs_verification",
        "analysis_complete": True, "risk_score": 10, "risk_level": "low", "payroll_weighted": False,
        "scam_type": "unknown", "findings": [], "recommended_actions": [], "limitations": [],
        "model": "tinker:test", "elapsed_ms": 1}))
    response = client.post("/analyze", json=BODY, headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["execution"] == "cloud-run"
    assert response.json()["assessment"] == "needs_verification"


def test_failed_minter_never_sends_request(setup, monkeypatch):
    client, calls, _ = setup
    def fail():
        raise c.HTTPException(502, "Cloud sign-in failed")
    monkeypatch.setattr(c, "mint_token", fail)
    assert client.post("/analyze", json=BODY, headers=HEADERS).status_code == 502
    assert calls == []


def test_session_preserves_application_error(setup):
    client, _, replies = setup
    replies.append(Reply({"detail": "invalid application token"}, 401))
    response = client.get("/session", headers=HEADERS)
    assert response.status_code == 502
    assert response.json() == {"detail": "Cloud application token rejected; restart the demo connection"}


def test_startup_refuses_non_tinker(setup):
    _, _, replies = setup
    replies.append(Reply({**SESSION, "model": {"analyze": "rules-only"}}))
    with pytest.raises(c.HTTPException, match="consistently"):
        with TestClient(c.app):
            pass


@pytest.mark.parametrize("failure", ["exit", "timeout"])
def test_minter_fixed_arguments_and_sanitized_failure(monkeypatch, tmp_path, failure):
    executable = tmp_path / "bin" / "gcloud.cmd"
    executable.parent.mkdir()
    executable.touch()
    script = tmp_path / "lib" / "gcloud.py"
    script.parent.mkdir()
    script.touch()
    monkeypatch.setenv("CLOUD_GCLOUD", str(executable))
    monkeypatch.setenv("CLOUDSDK_PYTHON", c.sys.executable)
    for key in ("DEMO_API_TOKEN", "CLOUD_DEMO_TOKEN", "TINKER_API_KEY"):
        monkeypatch.setenv(key, "secret")
    calls = []
    def run(args, **kwargs):
        calls.append((args, kwargs))
        if failure == "timeout":
            raise subprocess.TimeoutExpired(args, 8, stderr="secret")
        raise subprocess.CalledProcessError(1, args, stderr="secret")
    monkeypatch.setattr(c.subprocess, "run", run)
    with pytest.raises(c.HTTPException) as error:
        c.mint_token()
    assert "secret" not in error.value.detail
    args, options = calls[0]
    assert args == [c.sys.executable, str(script), "auth", "print-identity-token"]
    assert options["stdin"] == subprocess.DEVNULL
    assert options["timeout"] == 8
    assert options["check"] and options["capture_output"] and options["text"]
    assert options["env"]["CLOUDSDK_CORE_DISABLE_PROMPTS"] == "1"
    assert not {"DEMO_API_TOKEN", "CLOUD_DEMO_TOKEN", "TINKER_API_KEY"} & options["env"].keys()


def test_upstream_truncated_read_is_sanitized(setup):
    client, _, replies = setup
    class Truncated(Reply):
        def read(self, limit):
            raise IncompleteRead(b"secret")
    replies.append(Truncated({}))
    response = client.post("/analyze", json=BODY, headers=HEADERS)
    assert response.status_code == 502
    assert "secret" not in response.text


@pytest.mark.parametrize("tag", ["a", "ends-", "-starts", "a" * 64])
def test_tag_validation_matches_launcher(setup, monkeypatch, tag):
    client, calls, _ = setup
    monkeypatch.setenv("CLOUD_RUN_URL", c.SERVICE_URL.replace("https://", "https://" + tag + "---"))
    assert client.get("/session", headers=HEADERS).status_code == 503
    assert calls == []


def test_sdk_wrapper_requires_script_and_uses_python_fallback(monkeypatch, tmp_path):
    executable = tmp_path / "bin" / "gcloud.cmd"
    executable.parent.mkdir()
    executable.touch()
    monkeypatch.setenv("CLOUD_GCLOUD", str(executable))
    monkeypatch.delenv("CLOUDSDK_PYTHON", raising=False)
    calls = []
    monkeypatch.setattr(c.subprocess, "run", lambda args, **kw: calls.append(args) or subprocess.CompletedProcess(args, 0, "identity\n"))
    with pytest.raises(c.HTTPException):
        c.mint_token()
    assert calls == []
    script = tmp_path / "lib" / "gcloud.py"
    script.parent.mkdir()
    script.touch()
    assert c.mint_token() == "identity"
    assert calls == [[c.sys.executable, str(script), "auth", "print-identity-token"]]
    bundled = tmp_path / "platform" / "bundledpython" / "python.exe"
    bundled.parent.mkdir(parents=True)
    bundled.touch()
    assert c.mint_token() == "identity"
    assert calls[-1] == [str(bundled), str(script), "auth", "print-identity-token"]


def test_forward_preserves_utf8_request_size(setup):
    _, calls, _ = setup
    body = {"blocks": [{"id": "b1", "text": "中文" * 18000}]}
    c.forward("/analyze", body)
    raw = calls[-1].data
    assert json.loads(raw) == body
    assert "中文".encode("utf-8") in raw
    assert len(raw) < c.MAX_BODY_BYTES
    assert len(json.dumps(body).encode()) > c.MAX_BODY_BYTES


@pytest.mark.parametrize("interpreter", ["relative-python", "C:/missing/python.exe"])
def test_bad_sdk_interpreter_fails_without_spawn(monkeypatch, tmp_path, interpreter):
    executable = tmp_path / "bin" / "gcloud.cmd"
    executable.parent.mkdir()
    executable.touch()
    script = tmp_path / "lib" / "gcloud.py"
    script.parent.mkdir()
    script.touch()
    monkeypatch.setenv("CLOUD_GCLOUD", str(executable))
    monkeypatch.setenv("CLOUDSDK_PYTHON", interpreter)
    calls = []
    monkeypatch.setattr(c.subprocess, "run", lambda *args, **kw: calls.append(args))
    with pytest.raises(c.HTTPException) as error:
        c.mint_token()
    assert error.value.status_code == 502
    assert calls == []
