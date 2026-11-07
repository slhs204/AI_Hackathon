"""The only place that talks to a model provider.

MODEL_PROVIDER=mock    no model call; analysis = rules + tools only (free, offline)
MODEL_PROVIDER=tinker  Tinker's OpenAI-compatible API (beta)
    TINKER_API_KEY   from Secret Manager in Cloud Run, never in the extension
    TINKER_MODEL     the model/checkpoint the team's smoke test proved works
    TINKER_BASE_URL  optional; defaults to the documented endpoint

Everything the model returns is treated as untrusted text: callers parse it,
validate it, and check every quote against the email.
"""

import json
import os
import re
import time
from typing import Callable, Optional

from . import config

DEFAULT_TINKER_BASE_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1"
TIMEOUT_S = float(os.environ.get("MODEL_TIMEOUT_S", "30"))
MAX_OUTPUT_TOKENS = int(os.environ.get("MODEL_MAX_TOKENS", "1500"))

# (system, user) -> raw text. Tests replace this with a fake.
ModelCall = Callable[[str, str], str]


class ModelUnavailable(Exception):
    """No usable answer: not configured, network error, timeout, or garbage."""


def model_label() -> str:
    if config.model_provider() == "tinker":
        return f"tinker:{os.environ.get('TINKER_MODEL', '?')}"
    return "rules-only"


def _tinker_call(system: str, user: str) -> str:
    key, model = os.environ.get("TINKER_API_KEY"), os.environ.get("TINKER_MODEL")
    if not key or not model:
        raise ModelUnavailable("TINKER_API_KEY or TINKER_MODEL is not set")
    from openai import OpenAI  # imported lazily so mock mode needs no network library setup

    client = OpenAI(
        api_key=key,
        base_url=os.environ.get("TINKER_BASE_URL", DEFAULT_TINKER_BASE_URL),
        timeout=TIMEOUT_S,
        max_retries=1,
    )
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.2,
        )
    except Exception as exc:  # network, auth, rate limit, bad model id
        raise ModelUnavailable(f"{type(exc).__name__}") from exc
    if not resp.choices:
        raise ModelUnavailable("empty response")
    return resp.choices[0].message.content or ""


def default_call() -> Optional[ModelCall]:
    return _tinker_call if config.model_provider() == "tinker" else None


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)
_THINK = re.compile(r"<think>.*?</think>", re.S | re.I)


def parse_json_object(text: str) -> dict:
    """Pull one JSON object out of model text (tolerates code fences, a
    leading sentence, or a <think> block). Raises ModelUnavailable."""
    t = _FENCE.sub("", _THINK.sub("", text or "").strip())
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end <= start:
        raise ModelUnavailable("no JSON object in model output")
    try:
        obj = json.loads(t[start : end + 1])
    except json.JSONDecodeError as exc:
        raise ModelUnavailable("model output is not valid JSON") from exc
    if not isinstance(obj, dict):
        raise ModelUnavailable("model output is not a JSON object")
    return obj


def call_json(call: ModelCall, system: str, user: str, retries: int = 1) -> tuple[dict, int]:
    """Call the model and parse a JSON object, retrying once on bad output.
    Returns (object, elapsed_ms)."""
    started = time.monotonic()
    last: Exception = ModelUnavailable("no attempt")
    for attempt in range(retries + 1):
        prompt = user if attempt == 0 else user + "\n\nYour last reply was not one valid JSON object. Reply with ONLY the JSON object."
        try:
            obj = parse_json_object(call(system, prompt))
            return obj, int((time.monotonic() - started) * 1000)
        except ModelUnavailable as exc:
            last = exc
    raise last
