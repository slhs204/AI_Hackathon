"""Private Cloud Run connector; launch on 127.0.0.1:8081 only."""

import json
import os
import re
import socket
import subprocess
import sys
from contextlib import asynccontextmanager
from http.client import HTTPException as HTTPReadError
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from main import MAX_BODY_BYTES, config, limit_body, require_token
from app.schemas import AnalyzeRequest, AnalyzeResponse, ChallengeRequest, ChallengeResponse

SERVICE_URL = "https://phish-staging-az465uxmla-uc.a.run.app"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def cloud_url():
    url = os.environ.get("CLOUD_RUN_URL", SERVICE_URL)
    if not re.fullmatch(r"https://(?:[a-z][a-z0-9-]{0,61}[a-z0-9]---)?phish-staging-az465uxmla-uc\.a\.run\.app", url):
        raise HTTPException(503, "Cloud service URL is not allowed")
    return url


def mint_token():
    executable = os.environ.get("CLOUD_GCLOUD", "")
    if not executable or not os.path.isabs(executable) or not os.path.isfile(executable):
        raise HTTPException(503, "Cloud sign-in executable is not configured")
    try:
        command = [executable]
        if Path(executable).suffix.lower() == ".cmd":
            script = Path(executable).parent.parent / "lib" / "gcloud.py"
            bundled = Path(executable).parent.parent / "platform" / "bundledpython" / "python.exe"
            interpreter = os.environ.get("CLOUDSDK_PYTHON") or (str(bundled) if bundled.is_file() else sys.executable)
            if not script.is_file() or not os.path.isabs(interpreter) or not os.path.isfile(interpreter):
                raise ValueError()
            # Avoid cmd's child process and inherited pipes defeating the timeout.
            command = [interpreter, str(script)]
        env = {k: v for k, v in os.environ.items()
               if k.upper() not in {"DEMO_API_TOKEN", "CLOUD_DEMO_TOKEN", "TINKER_API_KEY"}}
        env["CLOUDSDK_CORE_DISABLE_PROMPTS"] = "1"
        token = subprocess.run(command + ["auth", "print-identity-token"],
                               stdin=subprocess.DEVNULL, env=env, capture_output=True,
                               text=True, timeout=8, check=True).stdout.strip()
        if not token or any(c.isspace() for c in token):
            raise ValueError()
        return token
    except (OSError, subprocess.SubprocessError, ValueError):
        raise HTTPException(502, "Cloud sign-in failed; sign in with gcloud and restart") from None


def forward(path, body=None):
    url = cloud_url()
    app_token = os.environ.get("CLOUD_DEMO_TOKEN", "")
    if not app_token:
        raise HTTPException(503, "Cloud application token is not configured")
    headers = {"Authorization": "Bearer " + mint_token(), "X-Demo-Token": app_token,
               "X-Require-Tinker": "1", "Content-Type": "application/json"}
    request = Request(url + path, data=None if body is None else json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode(), headers=headers)
    try:
        try:
            response = build_opener(ProxyHandler({}), NoRedirect()).open(request, timeout=35)
        except HTTPError as exc:
            response = exc
        with response:
            status = response.code
            raw = response.read(MAX_BODY_BYTES + 1)
        if 300 <= status < 400 or len(raw) > MAX_BODY_BYTES:
            raise ValueError()
        try:
            data = json.loads(raw)
        except (ValueError, UnicodeError):
            if status in (401, 403):
                raise HTTPException(502, "Cloud sign-in was rejected; sign in with gcloud and restart") from None
            raise ValueError() from None
        if not isinstance(data, dict):
            raise ValueError()
        if status == 401:
            raise HTTPException(502, "Cloud application token rejected; restart the demo connection")
        if not 200 <= status < 300:
            return JSONResponse({"detail": data.get("detail", "Cloud application request failed")}, status_code=status)
        return data
    except (TimeoutError, socket.timeout):
        raise HTTPException(504, "Cloud request timed out") from None
    except URLError as exc:
        raise HTTPException(504 if isinstance(exc.reason, TimeoutError) else 502, "Cloud service is unavailable") from None
    except (OSError, ValueError, HTTPReadError):
        raise HTTPException(502, "Cloud service returned an invalid response") from None


def cloud_session():
    data = forward("/session")
    if isinstance(data, JSONResponse):
        raise HTTPException(data.status_code, json.loads(data.body)["detail"])
    models = data.get("model") if isinstance(data, dict) else None
    if (not isinstance(data, dict) or data.get("status") != "ok"
            or data.get("service") != "phishing-coach" or not isinstance(models, dict)
            or set(models) != {"triage", "analyze", "challenge"}
            or len(set(str(v) for v in models.values())) != 1
            or not all(isinstance(v, str) and v.startswith("tinker:") and len(v) > 7 for v in models.values())):
        raise HTTPException(502, "Cloud service is not consistently configured for Tinker")
    return {**data, "execution": "cloud-run"}


@asynccontextmanager
async def lifespan(app):
    # Startup runs before accepting requests; health only reads this snapshot.
    app.state.health = cloud_session()
    yield


app = FastAPI(title="Phishing Coach Cloud Connector", lifespan=lifespan)
app.middleware("http")(limit_body)
app.add_middleware(CORSMiddleware, allow_origins=config.allowed_origins(),
                   allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
                   allow_methods=["GET", "POST", "OPTIONS"],
                   allow_headers=["Content-Type", "X-Demo-Token", "X-Require-Rules-Only", "X-Require-Tinker"])


@app.get("/health")
def health():
    return app.state.health


def cloud_permission(_=Depends(require_token), x_require_tinker: str = Header(default="")):
    if config.model_provider() != "tinker" or x_require_tinker != "1":
        raise HTTPException(409, "Explicit Tinker permission and configuration are required")


@app.get("/session", dependencies=[Depends(cloud_permission)])
def session():
    return cloud_session()


def validated(path, req, schema):
    data = forward(path, req.model_dump())
    if isinstance(data, JSONResponse):
        return data
    try:
        if schema is AnalyzeResponse:
            data.setdefault("email_id", None)  # Upstream excludes optional None fields.
        result = schema.model_validate(data).model_dump(exclude_none=True)
        if not result["model"].startswith("tinker:"):
            raise ValueError()
        return {**result, "execution": "cloud-run"}
    except (ValidationError, ValueError):
        raise HTTPException(502, "Cloud service returned an invalid analysis") from None


@app.post("/analyze", dependencies=[Depends(cloud_permission)])
def analyze(req: AnalyzeRequest):
    return validated("/analyze", req, AnalyzeResponse)


@app.post("/challenge", dependencies=[Depends(cloud_permission)])
def challenge(req: ChallengeRequest):
    return validated("/challenge", req, ChallengeResponse)
