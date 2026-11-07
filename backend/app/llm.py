"""The only place that talks to a model provider.

MODEL_PROVIDER=mock       no model call; rules and tools only (free, offline)
MODEL_PROVIDER=tinker     Tinker's OpenAI-compatible API (beta)
    TINKER_API_KEY, TINKER_MODEL, optional TINKER_BASE_URL
MODEL_PROVIDER=anthropic  Claude API, one model per job:
    ANTHROPIC_API_KEY (or an `ant auth login` profile)
    ANTHROPIC_TRIAGE_MODEL    default claude-haiku-5-5   -> /triage (inbox overview: cheap, fast)
    ANTHROPIC_ANALYSIS_MODEL  default claude-sonnet-5-5  -> /analyze and /challenge (one email, careful)
    ANTHROPIC_FALLBACKS       default 1: on a safety decline, Sonnet re-runs on a fallback model

Keys come from the environment (Secret Manager on Cloud Run), never from the
extension. Everything a model returns is untrusted text: callers parse it,
validate it, and check every quote against the email.
"""

import json
import os
import re
import time
from typing import Callable, Optional

from . import config

DEFAULT_TINKER_BASE_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/oai/api/v1"
DEFAULT_MODELS = {"triage": "claude-haiku-5-5", "analyze": "claude-sonnet-5-5", "challenge": "claude-sonnet-5-5"}
TIMEOUT_S = float(os.environ.get("MODEL_TIMEOUT_S", "30"))
MAX_OUTPUT_TOKENS = int(os.environ.get("MODEL_MAX_TOKENS", "4000"))

# (system, user) -> raw text. Tests replace this with a fake.
ModelCall = Callable[[str, str], str]


class ModelUnavailable(Exception):
    """No usable answer: not configured, network error, timeout, refusal, or garbage."""


def _anthropic_model(task: str) -> str:
    env = "ANTHROPIC_TRIAGE_MODEL" if task == "triage" else "ANTHROPIC_ANALYSIS_MODEL"
    return os.environ.get(env, DEFAULT_MODELS[task])


def model_label(task: str = "analyze") -> str:
    provider = config.model_provider()
    if provider == "tinker":
        return f"tinker:{os.environ.get('TINKER_MODEL', '?')}"
    if provider == "anthropic":
        return f"anthropic:{_anthropic_model(task)}"
    return "rules-only"


# ------------------------------------------------------------------ Tinker

def _tinker_call(system: str, user: str) -> str:
    key, model = os.environ.get("TINKER_API_KEY"), os.environ.get("TINKER_MODEL")
    if not key or not model:
        raise ModelUnavailable("TINKER_API_KEY or TINKER_MODEL is not set")
    from openai import OpenAI  # lazy import: mock mode needs no provider SDK

    client = OpenAI(api_key=key, base_url=os.environ.get("TINKER_BASE_URL", DEFAULT_TINKER_BASE_URL),
                    timeout=TIMEOUT_S, max_retries=1)
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            max_tokens=MAX_OUTPUT_TOKENS,
            temperature=0.2,
        )
    except Exception as exc:  # network, auth, rate limit, bad model id
        raise ModelUnavailable(type(exc).__name__) from exc
    if not resp.choices:
        raise ModelUnavailable("empty response")
    return resp.choices[0].message.content or ""


# ------------------------------------------------------------------ Anthropic

def _anthropic_call(task: str, schema: Optional[dict]) -> ModelCall:
    model = _anthropic_model(task)

    def call(system: str, user: str) -> str:
        import anthropic  # lazy import

        client = anthropic.Anthropic(timeout=TIMEOUT_S, max_retries=1)
        output_config: dict = {"effort": "low"}  # short tasks; low effort keeps latency and cost down
        if schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": schema}
        kwargs = dict(model=model, max_tokens=MAX_OUTPUT_TOKENS, system=system,
                      messages=[{"role": "user", "content": user}], output_config=output_config)
        use_fallback = model.startswith("claude-sonnet-5-5") and os.environ.get("ANTHROPIC_FALLBACKS", "1") != "0"
        try:
            if use_fallback:
                resp = client.beta.messages.create(**kwargs, betas=["server-side-fallback-2026-07-01"],
                                                   fallbacks="default")
            else:
                resp = client.messages.create(**kwargs)
        except anthropic.APIConnectionError as exc:
            raise ModelUnavailable("APIConnectionError") from exc
        except anthropic.APIStatusError as exc:
            raise ModelUnavailable(f"HTTP {exc.status_code}") from exc
        if resp.stop_reason == "refusal":
            raise ModelUnavailable("model declined the request")
        if resp.stop_reason == "max_tokens":
            raise ModelUnavailable("output cut off at max_tokens")
        return next((b.text for b in resp.content if b.type == "text"), "")

    return call


# ------------------------------------------------------------------ choosing

def default_call(task: str = "analyze", schema: Optional[dict] = None) -> Optional[ModelCall]:
    provider = config.model_provider()
    if provider == "tinker":
        return _tinker_call
    if provider == "anthropic":
        return _anthropic_call(task, schema)
    return None


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
