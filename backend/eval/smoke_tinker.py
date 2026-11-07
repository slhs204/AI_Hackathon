"""First real Tinker call: is the key/model OK, does the model return JSON, how slow is it?

Usage (from backend/; the key is read from the environment and never printed):
  export TINKER_API_KEY=...        # or put it in backend/.env and `set -a; source .env; set +a`
  export TINKER_MODEL=...          # the value from the team's smoke test
  .venv/bin/python -m eval.smoke_tinker

Step 1 sends a 1-line prompt (a few tokens). Step 2 runs one full /analyze on a
fixture. Total cost is well under one cent on small models.
"""

import json
import os
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app import llm  # noqa: E402
from app.analyze import analyze  # noqa: E402
from app.schemas import AnalyzeRequest  # noqa: E402


def main() -> int:
    missing = [k for k in ("TINKER_API_KEY", "TINKER_MODEL") if not os.environ.get(k)]
    if missing:
        print(f"Set {', '.join(missing)} first (see the docstring).")
        return 2
    print(f"model:    {os.environ['TINKER_MODEL']}")
    print(f"base url: {os.environ.get('TINKER_BASE_URL', llm.DEFAULT_TINKER_BASE_URL)}")

    print("\n[1/2] tiny JSON call ...")
    t0 = time.monotonic()
    try:
        raw = llm._tinker_call("Reply with only JSON.", 'Return exactly this JSON object: {"ok": true}')
    except llm.ModelUnavailable as exc:
        print(f"  FAILED: {exc}")
        print("  Check: key valid? model name right? (the OpenAI-compatible API may need a tinker:// checkpoint path)")
        return 1
    ms = int((time.monotonic() - t0) * 1000)
    print(f"  {ms} ms, raw reply: {raw[:200]!r}")
    try:
        print(f"  parsed: {llm.parse_json_object(raw)}")
    except llm.ModelUnavailable as exc:
        print(f"  reply is not clean JSON ({exc}); the backend will retry once, then fall back to rules")

    print("\n[2/2] full /analyze on fixtures/emails/vendor-bank-change.json ...")
    case = json.loads((BACKEND.parent / "fixtures" / "emails" / "vendor-bank-change.json").read_text())
    os.environ["MODEL_PROVIDER"] = "tinker"
    r = analyze(AnalyzeRequest.model_validate(case["request"]), llm._tinker_call)
    print(f"  model label: {r.model}   elapsed: {r.elapsed_ms} ms   complete: {r.analysis_complete}")
    print(f"  summary: {r.summary!r}")
    for f in r.findings:
        if f.source == "model":
            print(f"  + model finding [{f.category}] {f.evidence.quote!r}: {f.explanation[:100]}")
    for note in r.limitations:
        if "AI" in note:
            print(f"  ! {note}")
    print("\nIf both steps worked, run the full eval:  .venv/bin/python -m eval.run_eval --model")
    return 0


if __name__ == "__main__":
    sys.exit(main())
