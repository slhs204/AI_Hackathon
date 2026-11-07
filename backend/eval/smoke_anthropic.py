"""First real Claude calls: Haiku sorts a 3-email inbox, Sonnet analyzes one email.

Usage (from backend/; the key is read from the environment and never printed):
  export ANTHROPIC_API_KEY=...      # or `ant auth login`
  .venv/bin/python -m eval.smoke_anthropic

Cost: about one cent in total.
"""

import json
import os
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
os.environ["MODEL_PROVIDER"] = "anthropic"

from app import llm, prompts  # noqa: E402
from app.analyze import analyze  # noqa: E402
from app.schemas import AnalyzeRequest, TriageRequest  # noqa: E402
from app.triage import triage  # noqa: E402

INBOX = {"emails": [
    {"email_id": "m1", "sender": {"name": "Jane Whitfield", "address": "jane.whitfield.ceo@gmail.com"},
     "subject": "Wire needed today", "snippet": "Process a wire of $9,000 today. Keep this confidential."},
    {"email_id": "m2", "sender": {"name": "Robert Chen", "address": "robert.chen@acme-corp.com"},
     "subject": "Draft handbook", "snippet": "Comments by Wednesday please."},
    {"email_id": "m3", "sender": {"name": "Globex Supply AR", "address": "ar@globex-supply.com"},
     "subject": "Invoice GS-21007 remittance", "snippet": "Please note we have moved banks; send future payments to our new account."},
]}


def main() -> int:
    print(f"[1/2] triage with {llm.model_label('triage')} ...")
    r = triage(TriageRequest.model_validate(INBOX), llm.default_call("triage", prompts.TRIAGE_SCHEMA))
    print(f"  model: {r.model}   {r.elapsed_ms} ms")
    for it in r.items:
        print(f"  {it.email_id}: {it.priority:6s} ({it.source}) {it.reason}")
    if "unavailable" in r.model:
        print("  -> model call failed; check the key (see server log line 'triage model unavailable').")
        return 1

    print(f"\n[2/2] analyze h-compromised-vendor with {llm.model_label('analyze')} ...")
    case = json.loads((BACKEND.parent / "fixtures" / "emails" / "h-compromised-vendor.json").read_text())
    a = analyze(AnalyzeRequest.model_validate(case["request"]), llm.default_call("analyze", prompts.ANALYZE_SCHEMA))
    print(f"  model: {a.model}   {a.elapsed_ms} ms   assessment: {a.assessment}   verdict: {a.verdict}")
    print(f"  summary: {a.summary!r}")
    for f in a.findings:
        print(f"  [{f.source}] {f.category}: {(f.evidence.quote or '')[:70]!r}")
    print("\nIf both worked: .venv/bin/python -m eval.run_eval --model   (and --set blind)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
