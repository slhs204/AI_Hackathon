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
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
import threading
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


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def request_for(case: dict, view: str) -> dict:
    req = dict(case["request"])
    if view == "gmail":
        for key in HEADER_FIELDS:
            req.pop(key, None)
        req["extraction_complete"] = False
        req["extraction_limitations"] = list(req.get("extraction_limitations", [])) + [
            "Gmail view omits raw authentication headers, Reply-To and attachment contents; only visible message content is evaluated."]
    return req


def parse_views(value: str) -> list[str]:
    views = value.split(",")
    if len(views) != len(set(views)) or any(v not in ("full", "gmail") for v in views):
        raise ValueError("--views must name full and/or gmail once each")
    return views


def selected_paths(fixtures: Path, split: str, split_path: Path | None = None) -> list[Path]:
    paths = sorted(fixtures.glob("*.json"))
    if split_path is None:
        if split != "all":
            raise ValueError("--split tune/test requires --set blind")
        return paths
    manifest = json.loads(split_path.read_text(encoding="utf-8"))
    tune, test = manifest["tune"], manifest["test"]
    ids = {p.stem for p in paths}
    if (len(tune) != len(set(tune)) or len(test) != len(set(test))
            or set(tune) & set(test) or set(tune) | set(test) != ids):
        raise ValueError("split must be duplicate-free, disjoint and cover exactly all fixture IDs")
    return paths if split == "all" else [p for p in paths if p.stem in set(manifest[split])]


def provenance(paths: list[Path], views: list[str], model: str, split_path: Path | None) -> dict:
    system, schema = prompts.analyze_prompt()
    sources = sorted([* (BACKEND / "app").rglob("*.py"), * (BACKEND / "phishhook").rglob("*.py"), * (BACKEND / "data").rglob("*.json"), * (BACKEND / "phishhook").glob("*.json"), Path(__file__)])
    source_hashes = {p.relative_to(BACKEND).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    inputs = {f"{v}/{p.stem}": digest(request_for(json.loads(p.read_text(encoding="utf-8")), v))
              for v in views for p in paths}
    all_fixtures = sorted(paths[0].parent.glob("*.json")) if paths else []
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=BACKEND, capture_output=True, text=True).stdout.strip()
    return {"git_revision": revision, "model": model, "views": views, "source_hashes": source_hashes,
            "fixture_hashes": {p.stem: hashlib.sha256(p.read_bytes()).hexdigest() for p in all_fixtures},
            "input_hashes": inputs, "split_hash": hashlib.sha256(split_path.read_bytes()).hexdigest() if split_path else None,
            "prompt_version": prompts.prompt_version(), "prompt_hash": digest(system),
            "schema_hash": digest(schema), "generation": {"temperature": 0.2, "max_output_tokens": llm.MAX_OUTPUT_TOKENS,
            "timeout_s": llm.TIMEOUT_S, "validation_corrections_max": 1,
            "tinker_transport_retries": 0, "endpoint_hash": digest(os.environ.get("TINKER_BASE_URL", llm.DEFAULT_TINKER_BASE_URL))}}


class Journal:
    """Append before transmission; uncertain attempts require explicit human recovery."""
    def __init__(self, path: Path, config: dict):
        self.path, self.lock, self.completed = path, threading.Lock(), {}
        self.fingerprint = digest(config)
        if path.exists():
            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            if not records or records[0].get("fingerprint") != self.fingerprint:
                raise ValueError("journal configuration mismatch")
            pending = set()
            for record in records[1:]:
                key = record["key"]
                if record["event"] == "attempted":
                    if key in pending or key in self.completed:
                        raise ValueError("journal contains duplicate attempts")
                    pending.add(key)
                elif record["event"] == "completed" and key in pending:
                    pending.remove(key)
                    self.completed[key] = record["row"]
                elif record["event"] == "provider_call" and key in pending:
                    pass
                else:
                    raise ValueError("invalid journal event")
            if pending:
                raise ValueError("journal has uncertain attempted requests; automatic replay refused")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.append({"event": "config", "fingerprint": self.fingerprint, "config": config})

    def append(self, record: dict) -> None:
        record = {**record, "at": datetime.now(timezone.utc).isoformat()}
        with self.lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            os.fsync(stream.fileno())


def flagged(r) -> bool:
    return bool(r.findings)


def _one(path: Path, view: str, model_call, journal: Journal | None = None) -> dict:
    key = f"{view}/{path.stem}"
    if journal and key in journal.completed:
        return journal.completed[key]
    case = json.loads(path.read_text(encoding="utf-8"))
    req = request_for(case, view)
    calls = 0
    def counted(system, user):
        nonlocal calls
        calls += 1
        if journal:
            journal.append({"event": "provider_call", "key": key, "number": calls})
        return model_call(system, user)
    if journal:
        journal.append({"event": "attempted", "key": key, "input_hash": digest(req)})
    t0 = time.monotonic()
    r = analyze(AnalyzeRequest.model_validate(req), counted if model_call else None)
    ms = int((time.monotonic() - t0) * 1000)
    cats = sorted({f.category for f in r.findings})
    must = case["expected"].get("must_flag", [])
    row = {
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
        "analysis_complete": r.analysis_complete,
        "provider_success": bool(calls and r.model == llm.model_label("analyze")),
        "model_calls": calls,
        "corrections": max(0, calls - 1),
        "findings": [{"source": f.source, "category": f.category, "quote": f.evidence.quote or f.evidence.value,
                      "explanation": f.explanation} for f in r.findings],
        "notes": [{"source": f.source, "category": f.category, "quote": f.evidence.quote or f.evidence.value,
                   "explanation": f.explanation} for f in getattr(r, "notes", [])],
        "limitations": r.limitations,
        "ms": ms,
    }
    if journal:
        journal.append({"event": "completed", "key": key, "row": row})
    return row


def run(fixtures: Path, view: str, model_call, workers: int = 1, only: set | None = None,
        journal: Journal | None = None) -> list[dict]:
    paths = sorted(p for p in fixtures.glob("*.json") if only is None or p.stem in only)
    with ThreadPoolExecutor(max_workers=min(3, max(1, workers))) as pool:
        futures = [pool.submit(_one, p, view, model_call, journal) for p in paths]
        rows = []
        for i, fut in enumerate(futures, 1):  # keeps fixture order
            rows.append(fut.result())
            if model_call is not None and i % 20 == 0:
                print(f"  {view}: {i}/{len(paths)}", file=sys.stderr, flush=True)
    return rows


def rate(n: int, total: int) -> dict:
    if not total:
        return {"numerator": n, "denominator": total, "rate": None, "wilson95": None}
    z, p = 1.959963984540054, n / total
    center = (p + z*z/(2*total)) / (1 + z*z/total)
    half = z * ((p*(1-p)/total + z*z/(4*total*total)) ** 0.5) / (1 + z*z/total)
    return {"numerator": n, "denominator": total, "rate": p,
            "wilson95": [max(0., center-half), min(1., center+half)]}


def confusion(rows: list[dict]) -> dict:
    phish = [r for r in rows if r["label"] == "phishing"]
    legit = [r for r in rows if r["label"] == "legit"]
    tp, fp = sum(r["flagged"] for r in phish), sum(r["flagged"] for r in legit)
    tn, fn = len(legit)-fp, len(phish)-tp
    return {"n": len(phish)+len(legit), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": rate(tp, tp+fp), "recall": rate(tp, len(phish)), "false_positive_rate": rate(fp, len(legit))}


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
        "all_input_warnings": confusion(rows),
        "provider_success_warnings": confusion([r for r in rows if r.get("provider_success")]),
        "complete_only_warnings": confusion([r for r in rows if r.get("analysis_complete")]),
        "completion_coverage": rate(sum(r.get("analysis_complete", False) for r in rows), len(rows)),
        "provider_success_coverage": rate(sum(r.get("provider_success", False) for r in rows), len(rows)),
        "outcomes_by_label": {lab: {"n": len(by(lab)),
            "warnings": sum(r["flagged"] for r in by(lab)),
            "no_findings": sum(not r["flagged"] for r in by(lab)),
            "incomplete": sum(not r.get("analysis_complete", False) for r in by(lab)),
            "unfinished_no_findings": sum(not r["flagged"] and not r.get("analysis_complete", False) for r in by(lab)),
            "provider_failures": sum(r.get("model_calls", 0) > 0 and not r.get("provider_success", False) for r in by(lab))}
            for lab in ("phishing", "legit", "ambiguous")},
        "model_calls": sum(r.get("model_calls", 0) for r in rows),
        "corrections": sum(r.get("corrections", 0) for r in rows),
        "latency_ms_median": int(statistics.median(ms)) if ms else 0,
        "latency_ms_max": max(ms) if ms else 0,
    }


def to_markdown(results: dict) -> str:
    out = [f"# Eval report ({results['fixture_set']}) — {results['generated_at']}", "", f"Model: `{results['model']}`, prompt `{results.get('prompt', '-')}`, split `{results.get('split', 'all')}`. "
           f"{results['n_cases']} public/synthetic cases. Warning presence is independent of completeness; no-findings is not an all-clear. Counts only; not a real-world accuracy claim.",
           "Existing blind test partition has historical Anthropic/rule exposure; it is not a newly untouched benchmark.", ""]
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
    ap.add_argument("--prompt", choices=["v1", "v2", "v3"], default="", help="analyze prompt version (default: PROMPT_VERSION, otherwise Tinker v3 / other providers v1)")
    ap.add_argument("--analysis-model", default="", help="override ANTHROPIC_ANALYSIS_MODEL, e.g. claude-haiku-5-5")
    ap.add_argument("--tag", default="", help="suffix for the result file names")
    ap.add_argument("--journal", type=Path, help="durable JSONL run record; required for paid --model runs")
    args = ap.parse_args()
    if args.model and not args.journal:
        ap.error("--model requires --journal PATH to prevent accidental paid replay")
    if not 1 <= args.workers <= 3:
        ap.error("--workers must be between 1 and 3")
    if args.prompt:
        os.environ["PROMPT_VERSION"] = args.prompt
    if args.analysis_model:
        os.environ["ANTHROPIC_ANALYSIS_MODEL"] = args.analysis_model
    try:
        views = parse_views(args.views)
    except ValueError as exc:
        ap.error(str(exc))
    model_call = llm.default_call("analyze", prompts.analyze_prompt()[1]) if args.model else None
    if args.model and model_call is None:
        sys.exit("--model needs MODEL_PROVIDER (tinker or anthropic) and that provider's key/model settings")

    # "full" keeps Reply-To / auth results / attachments; "gmail" drops them, as the extensions can't read them yet.
    split_path = BACKEND.parent / "fixtures" / "blind_split.json" if args.set == "blind" else None
    paths = selected_paths(FIXTURE_SETS[args.set], args.split, split_path)
    if not paths:
        ap.error("no fixtures selected")
    identity = provenance(paths, views, llm.model_label("analyze") if model_call else "rules-only", split_path)
    journal = Journal(args.journal, identity) if args.journal else None
    rows = {v: run(FIXTURE_SETS[args.set], v, model_call, args.workers if model_call else 1,
                   {p.stem for p in paths}, journal) for v in views}
    results = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "fixture_set": args.set,
        "model": llm.model_label("analyze") if model_call else "rules-only",
        "prompt": prompts.prompt_version() if model_call else "-",
        "split": args.split,
        "n_cases": len(rows[views[0]]),
        "views": views,
        "summary": {v: summarize(rows[v]) for v in views},
        "rows": rows,
        "provenance": identity,
        "config_fingerprint": digest(identity),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    stem = ("model" if model_call else "rules-only") + ("" if args.set == "core" else f"-{args.set}")
    stem += ("" if args.split == "all" else f"-{args.split}") + (f"-{args.tag}" if args.tag else "")
    (RESULTS / f"{stem}.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (RESULTS / f"{stem}.md").write_text(to_markdown(results), encoding="utf-8")
    print(to_markdown(results))


if __name__ == "__main__":
    main()
