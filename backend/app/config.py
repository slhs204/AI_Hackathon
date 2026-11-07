"""Settings read from the environment, plus the versioned JSON data files."""

import json
import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@lru_cache
def policies() -> list[dict]:
    return _load(ROOT / "data" / "policies.json")["policies"]


@lru_cache
def drill_questions() -> list[dict]:
    return _load(ROOT / "phishhook" / "drill_bank.json")["questions"]


def model_provider() -> str:
    """"mock" = no model call (rules and tools only). "tinker" = real model."""
    return os.environ.get("MODEL_PROVIDER", "mock").strip().lower()


def demo_token() -> str:
    return os.environ.get("DEMO_API_TOKEN", "")


def allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", "https://mail.google.com")
    return [o.strip() for o in raw.split(",") if o.strip()]
