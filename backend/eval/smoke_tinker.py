"""First real Tinker call: is the key/model OK, does the model return JSON, how slow is it?

Usage (from backend/; the key is read from the environment and never printed):
  export TINKER_API_KEY=...        # or put it in backend/.env and `set -a; source .env; set +a`
  export TINKER_MODEL=...          # the value from the team's smoke test
  .venv/bin/python -m eval.smoke_tinker --preflight  # no provider request
  .venv/bin/python -m eval.smoke_tinker --allow-paid  # only after cost approval

The default is a configuration-only check. --allow-paid sends a tiny JSON prompt
and runs one full analysis on a synthetic fixture. Pricing depends on the chosen
checkpoint and provider; this script cannot enforce a dollar spending limit.
Bad JSON, fallback, or incomplete analysis must not be reported as a live pass.
"""

import argparse
import importlib.util
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--preflight", action="store_true", help="Check configuration without any network request (default)")
    mode.add_argument("--allow-paid", action="store_true", help="Run live Tinker requests after explicit cost approval")
    args = parser.parse_args(argv)
    missing = [k for k in ("TINKER_API_KEY", "TINKER_MODEL") if not os.environ.get(k)]
    if missing:
        print(f"Set {', '.join(missing)} first (see the docstring).")
        return 2
    if importlib.util.find_spec("openai") is None:
        print("Install backend requirements first: the OpenAI SDK is missing.")
        return 2
    print("Tinker key and model are configured (values not printed).")
    if not args.allow_paid:
        print("PREFLIGHT ONLY: no Tinker request was sent; credentials/checkpoint are not yet verified.")
        print("After cost approval, run again with --allow-paid.")
        return 0

    print("\n[1/2] tiny JSON call ...")
    t0 = time.monotonic()
    try:
        raw = llm._tinker_call("Reply with only JSON.", 'Return exactly this JSON object: {"ok": true}')
    except llm.ModelUnavailable as exc:
        print(f"  FAILED: {exc}")
        print("  Check: key valid? model name right? (the OpenAI-compatible API may need a tinker:// checkpoint path)")
        return 1
    ms = int((time.monotonic() - t0) * 1000)
    print(f"  {ms} ms")
    try:
        parsed = llm.parse_json_object(raw)
    except llm.ModelUnavailable as exc:
        print(f"  FAILED: reply is not valid JSON ({exc}).")
        return 1
    if set(parsed) != {"ok"} or parsed["ok"] is not True:
        print("  FAILED: tiny JSON response did not match the requested object.")
        return 1

    print("\n[2/2] full /analyze on fixtures/emails/vendor-bank-change.json ...")
    case = json.loads((BACKEND.parent / "fixtures" / "emails" / "vendor-bank-change.json").read_text())
    os.environ["MODEL_PROVIDER"] = "tinker"
    r = analyze(AnalyzeRequest.model_validate(case["request"]), llm._tinker_call)
    provider_ok = r.model == llm.model_label("analyze")
    print(f"  Tinker model used: {provider_ok}   elapsed: {r.elapsed_ms} ms   complete: {r.analysis_complete}")
    print(f"  findings: {len(r.findings)}   summary present: {bool(r.summary.strip())}")
    if not provider_ok or not r.analysis_complete or not r.summary.strip():
        print("  FAILED: live analysis fell back, was incomplete, or returned no summary.")
        return 1
    print("\nLIVE TINKER PASS: tiny JSON and synthetic full analysis succeeded.")
    print("This is a connectivity smoke test, not an accuracy evaluation or browser E2E test.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
