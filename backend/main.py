"""Phishing Coach API (FastAPI). Run locally:

    uvicorn main:app --reload --port 8080

Env: MODEL_PROVIDER (mock|tinker), DEMO_API_TOKEN, TINKER_API_KEY, TINKER_MODEL,
ALLOWED_ORIGINS (comma-separated, default https://mail.google.com).
"""

import hmac
import logging

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import config, llm, prompts
from app.analyze import analyze
from app.challenge import FindingNotFound, challenge
from app.schemas import (AnalyzeRequest, AnalyzeResponse, ChallengeRequest, ChallengeResponse,
                         TriageRequest, TriageResponse)
from app.triage import triage

MAX_BODY_BYTES = 200_000

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
app = FastAPI(title="Phishing Coach API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins(),
    allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Demo-Token"],
)


@app.middleware("http")
async def limit_body(request: Request, call_next):
    length = request.headers.get("content-length")
    if request.method == "POST" and not (length and length.isdigit()):
        # Without a length (chunked upload) the size check below could be skipped.
        # Browsers' fetch() with a string body always sends Content-Length.
        return JSONResponse({"error": "Content-Length required"}, status_code=411)
    if length and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"error": "Request too large (limit 200 KB)"}, status_code=413)
    return await call_next(request)


def require_token(x_demo_token: str = Header(default="")) -> None:
    """Fail closed, same as Albert's v3.1: with no DEMO_API_TOKEN configured the
    POST routes refuse everything (503); a wrong or missing token gets 401.
    For local work set any value, e.g. DEMO_API_TOKEN=dev."""
    expected = config.demo_token()
    if not expected:
        raise HTTPException(status_code=503, detail="DEMO_API_TOKEN is not configured on the server; /analyze is disabled")
    if not hmac.compare_digest(x_demo_token.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="invalid or missing X-Demo-Token")


_SCHEMAS = {"analyze": prompts.ANALYZE_SCHEMA, "challenge": prompts.CHALLENGE_SCHEMA, "triage": prompts.TRIAGE_SCHEMA}


def model_for_request(task: str):
    """Haiku for /triage, Sonnet for /analyze and /challenge (with MODEL_PROVIDER=anthropic)."""
    return llm.default_call(task, _SCHEMAS[task])


@app.get("/health")
def health():
    return {"status": "ok", "service": "phishing-coach",
            "model": {t: llm.model_label(t) for t in ("triage", "analyze", "challenge")}}


@app.post("/analyze", response_model=AnalyzeResponse, response_model_exclude_none=True,
          dependencies=[Depends(require_token)])
def analyze_route(req: AnalyzeRequest):
    return analyze(req, model_for_request("analyze"))


@app.post("/challenge", response_model=ChallengeResponse, dependencies=[Depends(require_token)])
def challenge_route(req: ChallengeRequest):
    try:
        return challenge(req, model_for_request("challenge"))
    except FindingNotFound as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/triage", response_model=TriageResponse, dependencies=[Depends(require_token)])
def triage_route(req: TriageRequest):
    """Inbox overview: sender + subject + preview only, on the user's request."""
    return triage(req, model_for_request("triage"))
