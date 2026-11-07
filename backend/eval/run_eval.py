"""Evaluate /analyze on the fixtures and write a report.

Two views of every email:
  full   - headers included (Reply-To, Authentication-Results, attachments), as in the .eml
  gmail  - only what the Gmail extension can read today (sender, subject, body, links)

Usage (from backend/):
  .venv/bin/python -m eval.run_eval                 # rules only, free
  MODEL_PROVIDER=tinker TINKER_API_KEY=... TINKER_MODEL=... .venv/bin/python -m eval.run_eval --model

Reports measured counts only. A small synthetic set says nothing about
real-world accuracy or about learning.
"""

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app import llm, prompts  # noqa: E402
from app.analyze import analyze  # noqa: E402
from app.schemas import AnalyzeRequest  # noqa: E402

FIXTURE_SETS = {
    "core": BACKEND.parent / "fixtures" / "emails",   # Albert's samples + handwritten cases
    "blind": BACKEND.parent / "fixtures" / "blind",   # Teddyha dataset (MIT), nobody tuned rules to it
}
RESULTS = BACKEND / "eval" / "results"
HEADER_FIELDS = ("reply_to", "authentication_results", "attachments")


def flagged(r) -> bool:
    return r.assessment != "no_obvious_indicators"


def _one(path: Path, view: str, model_call) -> dict:
    case = json.loads(path.read_text())
    req = dict(case["request"])
    if view == "gmail":
        for k in HEADER_FIELDS:
            req.pop(k, None)
    t0 = time.monotonic()
    r = analyze(AnalyzeRequest.model_validate(req), model_call)
    ms = int((time.monotonic() - t0) * 1000)
    cats = sorted({f.category for f in r.findings})
    must = case["expected"].get("must_flag", [])
    return {
        "id": case["request"]["email_id"],
        "label": case["expected"]["label"],
        "assessment": r.assessment,
        "verdict": (r.verdict or {}).get("key", ""),
        "flagged": flagged(r),
        "score": r.risk_score,
        "n_findings": len(r.findings),
        "categories": cats,
        "must_flag_missing": [c for c in must if c not in cats],
        "model_findings": sum(f.source == "model" for f in r.findings),
        "model_discarded": next((int(x.split()[4]) for x in r.limitations if "not in this email" in x), 0),
        "model": r.model,
        "ms": ms,
    }


def run(fixtures: Path, view: str, model_call, workers: int = 1, only: set | None = None) -> list[dict]:
    paths = sorted(p for p in fixtures.glob("*.json") if only is None or p.stem in only)
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = [pool.submit(_one, p, view, model_call) for p in paths]
        rows = []
        for i, fut in enumerate(futures, 1):  # keeps fixture order
            rows.append(fut.result())
            if model_call is not None and i % 20 == 0:
                print(f"  {view}: {i}/{len(paths)}", file=sys.stderr, flush=True)
    return rows


def summarize(rows: list[dict]) -> dict:
    by = lambda lab: [r for r in rows if r["label"] == lab]  # noqa: E731
    phish, legit, amb = by("phishing"), by("legit"), by("ambiguous")
    ms = [r["ms"] for r in rows]
    return {
        "phishing_flagged": f"{sum(r['flagged'] for r in phish)}/{len(phish)}",
        "legit_false_alarms": f"{sum(r['flagged'] for r in legit)}/{len(legit)}",
        "ambiguous_flagged": f"{sum(r['flagged'] for r in amb)}/{len(amb)}",
        "must_flag_misses": sum(len(r["must_flag_missing"]) for r in rows),
        "incomplete_results": sum(r["assessment"] == "insufficient_evidence" for r in rows),
        "model_findings_kept": sum(r["model_findings"] for r in rows),
        "model_findings_discarded": sum(r["model_discarded"] for r in rows),
        "model_unavailable": sum("unavailable" in r["model"] for r in rows),
        "latency_ms_median": int(statistics.median(ms)) if ms else 0,
        "latency_ms_max": max(ms) if ms else 0,
    }


def to_markdown(results: dict) -> str:
    out = [f"# Eval report ({results['fixture_set']}) — {results['generated_at']}", "", f"Model: `{results['model']}`, prompt `{results.get('prompt', '-')}`, split `{results.get('split', 'all')}`. "
           f"{results['n_cases']} synthetic cases. Counts only; not a real-world accuracy claim.", ""]
    out += ["| metric | " + " | ".join(results["views"]) + " |", "|---|" + "---|" * len(results["views"])]
    for key in next(iter(results["summary"].values())):
        out.append(f"| {key} | " + " | ".join(str(results["summary"][v][key]) for v in results["views"]) + " |")
    for view in results["views"]:
        out += ["", f"## Per case — {view}", "", "| case | label | assessment | verdict | score | findings | categories | missing | ms |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in results["rows"][view]:
            out.append(f"| {r['id']} | {r['label']} | {r['assessment']} | {r['verdict']} | {r['score']} | {r['n_findings']} | "
                       f"{', '.join(r['categories']) or '—'} | {', '.join(r['must_flag_missing']) or '—'} | {r['ms']} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", action="store_true", help="call the configured model (costs credits)")
    ap.add_argument("--set", choices=sorted(FIXTURE_SETS), default="core", help="which fixtures to run")
    ap.add_argument("--views", default="full,gmail", help="comma list of views: full, gmail")
    ap.add_argument("--workers", type=int, default=1, help="parallel requests (model runs only)")
    ap.add_argument("--split", choices=["all", "tune", "test"], default="all",
                    help="blind set only: tune prompts on 'tune', report from one run on 'test'")
    ap.add_argument("--prompt", choices=["v1", "v2"], default="", help="analyze prompt version (default: PROMPT_VERSION or v1)")
    ap.add_argument("--analysis-model", default="", help="override ANTHROPIC_ANALYSIS_MODEL, e.g. claude-haiku-5-5")
    ap.add_argument("--tag", default="", help="suffix for the result file names")
    args = ap.parse_args()
    if args.prompt:
        os.environ["PROMPT_VERSION"] = args.prompt
    if args.analysis_model:
        os.environ["ANTHROPIC_ANALYSIS_MODEL"] = args.analysis_model
    model_call = llm.default_call("analyze", prompts.analyze_prompt()[1]) if args.model else None
    if args.model and model_call is None:
        sys.exit("--model needs MODEL_PROVIDER (tinker or anthropic) and that provider's key/model settings")

    # "full" keeps Reply-To / auth results / attachments; "gmail" drops them, as the extensions can't read them yet.
    views = [v for v in args.views.split(",") if v in ("full", "gmail")] or ["full", "gmail"]
    only = None
    if args.set == "blind" and args.split != "all":
        only = set(json.loads((BACKEND.parent / "fixtures" / "blind_split.json").read_text())[args.split])
    rows = {v: run(FIXTURE_SETS[args.set], v, model_call, args.workers if model_call else 1, only) for v in views}
    results = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "fixture_set": args.set,
        "model": llm.model_label("analyze") if model_call else "rules-only",
        "prompt": os.environ.get("PROMPT_VERSION", "v1") if model_call else "-",
        "split": args.split,
        "n_cases": len(rows[views[0]]),
        "views": views,
        "summary": {v: summarize(rows[v]) for v in views},
        "rows": rows,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    stem = ("model" if model_call else "rules-only") + ("" if args.set == "core" else f"-{args.set}")
    stem += ("" if args.split == "all" else f"-{args.split}") + (f"-{args.tag}" if args.tag else "")
    (RESULTS / f"{stem}.json").write_text(json.dumps(results, indent=2) + "\n")
    (RESULTS / f"{stem}.md").write_text(to_markdown(results))
    print(to_markdown(results))


if __name__ == "__main__":
    main()
