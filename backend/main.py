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

from app import config, llm
from app.analyze import analyze
from app.challenge import FindingNotFound, challenge
from app.schemas import AnalyzeRequest, AnalyzeResponse, ChallengeRequest, ChallengeResponse

MAX_BODY_BYTES = 200_000

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
app = FastAPI(title="Phishing Coach API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allowed_origins(),
    allow_origin_regex=r"chrome-extension://[a-p]{32}",
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Demo-Token"],
)


@app.middleware("http")
async def limit_body(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and length.isdigit() and int(length) > MAX_BODY_BYTES:
        return JSONResponse({"error": "Request too large (limit 200 KB)"}, status_code=413)
    return await call_next(request)


def require_token(x_demo_token: str = Header(default="")) -> None:
    """Checked before any model call. With no DEMO_API_TOKEN configured, the
    real model is refused entirely (see model_for_request)."""
    expected = config.demo_token()
    if expected and not hmac.compare_digest(x_demo_token.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="invalid or missing X-Demo-Token")


def model_for_request():
    call = llm.default_call()
    if call is not None and not config.demo_token():
        # A paid model must never be reachable without a token.
        logging.getLogger("phishing-coach").error("MODEL_PROVIDER=tinker but DEMO_API_TOKEN is unset; model disabled")
        return None
    return call


@app.get("/health")
def health():
    return {"status": "ok", "service": "phishing-coach", "model": llm.model_label()}


@app.post("/analyze", response_model=AnalyzeResponse, response_model_exclude_none=True,
          dependencies=[Depends(require_token)])
def analyze_route(req: AnalyzeRequest):
    return analyze(req, model_for_request())


@app.post("/challenge", response_model=ChallengeResponse, dependencies=[Depends(require_token)])
def challenge_route(req: ChallengeRequest):
    try:
        return challenge(req, model_for_request())
    except FindingNotFound as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
