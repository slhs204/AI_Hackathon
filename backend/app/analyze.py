"""POST /analyze pipeline.

1. Rule engine (Albert's phishhook) -> findings with evidence
2. Extra link checks the engine lacks
3. Optional model pass: up to 3 extra signs + a summary
4. Every piece of evidence is re-checked against the email; model claims
   that can't be found are discarded and the result is marked incomplete
5. Company policy and a practice question are attached

A failed model call never turns into an all-clear: the rule result stands.
"""

import logging
import time
from typing import Optional

from phishhook import engine

from . import llm, prompts
from .evidence import verify
from .schemas import MODEL_CATEGORIES, AnalyzeRequest, AnalyzeResponse, Evidence, Finding
from .tools.extra_links import inspect_links_extra
from .tools.lookup import email_text, get_training_example, lookup_payroll_policy, policy_next_action

log = logging.getLogger("phishing-coach")

MAX_MODEL_FINDINGS = 3
MODEL_POINTS_EACH, MODEL_POINTS_CAP = 8, 16

NO_HOOK_NOTICE = "No warning signs found does not mean the email is safe."

_SCAM_TO_DRILL = {
    "Credential phishing": "credential",
    "Employee-data theft (W-2 scam)": "data_request",
    "CEO / CFO fraud (Business Email Compromise)": "ceo_fraud",
    "Payroll diversion fraud (BEC)": "payroll",
    "Bank-detail change fraud (BEC)": "bank_change",
    "Unverified payment request": "bank_change",
    "Fake invoice": "fake_invoice",
    "No known scam pattern": "legit",
}


def _level(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 30 else "low"


def _model_findings(raw: dict, email: AnalyzeRequest) -> tuple[list[Finding], int]:
    """Validate the model's extra findings. Returns (verified, discarded_count)."""
    items = raw.get("extra_findings")
    if not isinstance(items, list):
        return [], 0
    verified, discarded = [], 0
    for item in items[:MAX_MODEL_FINDINGS]:
        if not isinstance(item, dict):
            discarded += 1
            continue
        quote = str(item.get("quote", "")).strip()
        block_id = str(item.get("block_id", "")).strip()
        if len(quote) < 3 or not block_id:
            discarded += 1
            continue
        ev = verify(email, Evidence(kind="text", block_id=block_id, quote=quote[:500]))
        if ev is None:
            discarded += 1
            continue
        category = str(item.get("category", ""))
        verified.append(Finding(
            id="", source="model", evidence=ev,
            category=category if category in MODEL_CATEGORIES else "manipulation_cue",
            explanation=str(item.get("explanation", "")).strip()[:800] or "The AI flagged this wording as a pressure tactic.",
            next_action=str(item.get("next_action", "")).strip()[:800] or "Check the request through a channel you already trust.",
        ))
    return verified, discarded


def _quote_text(f: Finding) -> str:
    return f.evidence.quote or f.evidence.value or ""


def analyze(email: AnalyzeRequest, model_call: Optional[llm.ModelCall] = None) -> AnalyzeResponse:
    started = time.monotonic()
    rules = engine.analyze_contract(email.model_dump())
    complete = bool(rules["analysis_complete"])
    limitations = list(rules["limitations"])

    # 1. Rule findings, re-checked against the email.
    findings: list[Finding] = []
    for f in rules["findings"]:
        finding = Finding.model_validate({**f, "source": "rules"})
        ev = verify(email, finding.evidence)
        if ev is None:
            complete = False
            continue
        findings.append(finding.model_copy(update={"evidence": ev}))

    # 2. Extra deterministic link checks.
    flagged_links = {f.evidence.link_id for f in findings if f.evidence.kind == "link"}
    extras = inspect_links_extra(email, flagged_links)

    # 3. Optional model pass.
    summary, model_name, model_extra, discarded = "", "rules-only", [], 0
    if model_call is not None:
        try:
            raw, _ = llm.call_json(model_call, prompts.ANALYZE_SYSTEM, prompts.analyze_user(email, findings + extras))
            model_extra, discarded = _model_findings(raw, email)
            summary = str(raw.get("summary", "")).strip()[:600]
            model_name = llm.model_label()
        except llm.ModelUnavailable as exc:
            log.warning("model unavailable: %s", exc)
            model_name = "rules-only (model unavailable)"
            limitations.append("The AI review was unavailable, so only the automatic checks ran.")
    if discarded:
        complete = False
        limitations.append(
            f"The AI pointed to {discarded} piece(s) of text that are not in this email. "
            "Those claims were discarded; verify this email manually."
        )

    # Points: like the rule engine, only the first finding of a category scores,
    # so the hook gets one piece per kind of warning sign.
    scored = {f.category for f in findings if f.points}
    extra_points = 0
    for f in extras:
        if f.category in scored:
            f.points = 0
        else:
            scored.add(f.category)
            extra_points += f.points
    model_points = 0
    for f in model_extra:
        if f.category in scored or model_points >= MODEL_POINTS_CAP:
            f.points = 0
        else:
            f.points = min(MODEL_POINTS_EACH, MODEL_POINTS_CAP - model_points)
            model_points += f.points
            scored.add(f.category)
    all_findings = findings + extras + model_extra

    # 4. Policies and ids.
    text = email_text(email.subject, email.blocks)
    used_policies = {}
    for i, f in enumerate(all_findings, 1):
        f.id = f"f{i}"
        policy = lookup_payroll_policy(f.category, _quote_text(f)) or lookup_payroll_policy(f.category, text)
        if policy:
            f.policy_id = policy.id
            f.next_action = policy_next_action(policy.id)
            used_policies[policy.id] = policy

    score = min(100, int(rules["risk_score"]) + extra_points + model_points)
    if not complete:
        assessment = "insufficient_evidence"
    elif all_findings:
        assessment = "needs_verification"
    else:
        assessment = "no_obvious_indicators"
    limitations.append(NO_HOOK_NOTICE)

    elapsed = int((time.monotonic() - started) * 1000)
    log.info("analyze email_id=%s findings=%d model=%s discarded=%d complete=%s ms=%d",
             email.email_id, len(all_findings), model_name, discarded, complete, elapsed)
    return AnalyzeResponse(
        analysis_id=rules["analysis_id"],
        email_id=email.email_id,
        assessment=assessment,
        analysis_complete=complete,
        risk_score=score,
        risk_level=_level(score),
        payroll_weighted=bool(rules["payroll_weighted"]),
        scam_type=rules["scam_type"],
        findings=all_findings,
        recommended_actions=rules["recommended_actions"],
        limitations=limitations,
        summary=summary,
        policies=list(used_policies.values()),
        practice=get_training_example(_SCAM_TO_DRILL.get(rules["scam_type"], "fake_invoice"), email.email_id or ""),
        model=model_name,
        elapsed_ms=elapsed,
    )
