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
from .evidence import find_exact, verify
from .schemas import MODEL_CATEGORIES, AnalyzeRequest, AnalyzeResponse, Evidence, Finding
from .tools.extra_links import inspect_links_extra
from .tools.payroll_checks import company_name_in_sender_domain, payroll_request
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


TITLES = {
    "sender_impersonation": "Sender imitates someone trusted",
    "reply_to_mismatch": "Replies go to a different address",
    "authentication_failure": "Failed sender authentication",
    "authority_impersonation": "Pretends to be an executive or colleague",
    "deceptive_link": "Link is not what it says",
    "risky_attachment": "Dangerous attachment",
    "urgency_pressure": "Pressure or secrecy",
    "payment_or_data_request": "Asks for money, bank changes, data or a login",
    "manipulation_cue": "Manipulation tactic",
}


def _for_extension(f: Finding, email: AnalyzeRequest) -> None:
    """Give every finding a title and, where possible, a block_id + quote, so
    Hookline (which highlights only block_id + quote) can show it."""
    f.title = f.title or TITLES.get(f.category, "Warning sign")
    ev = f.evidence
    if ev.kind == "link" and not ev.quote:
        link = email.link(ev.link_id)
        block = email.block(link.block_id) if link else None
        exact = find_exact(block.text, link.display_text) if block and link.display_text else None
        f.evidence = ev.model_copy(update={"block_id": block.id, "quote": exact} if exact else
                                   {"quote": (link.display_text or link.href)[:500] if link else None})
    elif ev.kind == "metadata" and not ev.quote:
        # No block to highlight; the quote lets the card show the text.
        f.evidence = ev.model_copy(update={"quote": ev.value})


def _level(score: int) -> str:
    return "high" if score >= 70 else "medium" if score >= 30 else "low"


def _model_findings(raw: dict, email: AnalyzeRequest, has_rule_findings: bool) -> tuple[list[Finding], int]:
    """Validate the model's extra findings. Returns (verified, discarded_count).

    Prompt v2 adds a confidence per sign and an email_type. To keep false alarms
    down: low-confidence signs are dropped, and when the model itself calls the
    email a routine notification and the rules found nothing, only high-confidence
    signs are kept. Rule findings are never affected. Without these fields
    (prompt v1, Tinker without a schema) every verified sign is kept as before."""
    items = raw.get("extra_findings")
    if not isinstance(items, list):
        return [], 0
    routine = raw.get("email_type") == "routine_notification" and not has_rule_findings
    verified, discarded = [], 0
    for item in items[:MAX_MODEL_FINDINGS]:
        if not isinstance(item, dict):
            discarded += 1
            continue
        confidence = item.get("confidence")  # absent with prompt v1
        if confidence == "low" or (routine and confidence is not None and confidence != "high"):
            continue  # weak sign: not a hook piece (not counted as a failed quote either)
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
            id="", source="model", evidence=ev, title=str(item.get("title", "")).strip()[:80],
            category=category if category in MODEL_CATEGORIES else "manipulation_cue",
            explanation=str(item.get("explanation", "")).strip()[:800] or "The AI flagged this wording as a pressure tactic.",
            next_action=str(item.get("next_action", "")).strip()[:800] or "Check the request through a channel you already trust.",
        ))
    return verified, discarded


def _quote_text(f: Finding) -> str:
    return f.evidence.quote or f.evidence.value or ""


def _apply_ai_explanations(raw: dict, findings: list[Finding]) -> None:
    """Model rewording per category (Albert's v3 `ai_explanation`). Text only,
    no quotes, so nothing to verify; the rules' explanation stays as well."""
    expl = raw.get("explanations")
    if isinstance(expl, list):  # [{"category": ..., "text": ...}] (structured-output form)
        expl = {e.get("category"): e.get("text") for e in expl if isinstance(e, dict)}
    if not isinstance(expl, dict):
        return
    for f in findings:
        text = expl.get(f.category)
        if isinstance(text, str) and text.strip():
            f.ai_explanation = text.strip()[:600]


def _extra_tag(f: Finding) -> str:
    if f.category == "payment_or_data_request":
        return engine._payment_tag(_quote_text(f))
    return {"sender_impersonation": "look-alike domain", "deceptive_link": "link ≠ text",
            "manipulation_cue": "manipulation"}.get(f.category, f.category.replace("_", " "))


def _stages(engine_stages: list, engine_ids: dict, rule_findings: list[Finding], added: list[Finding]) -> list:
    """Engine v3.1 two-stage scan (subject line, then body), with finding ids
    remapped to our final ids and our extra findings added to the right stage."""
    new_id = {engine_ids[id(f)]: f.id for f in rule_findings if id(f) in engine_ids}
    out = []
    for st in engine_stages:
        flags = []
        for fl in st.get("flags", []):
            ids = [new_id[i] for i in fl.get("finding_ids", []) if i in new_id]
            flags.append({**fl, "finding_ids": ids})
        out.append({**st, "flags": flags})
    if not out:
        out = [{"stage": "subject", "score": 0, "flags": []}, {"stage": "body", "score": 0, "flags": []}]
    by_name = {st["stage"]: st for st in out}
    for f in added:
        st = by_name["subject" if f.evidence.kind == "metadata" else "body"]
        st["flags"].append({"n": len(st["flags"]) + 1, "category": f.category, "points": f.points,
                            "tags": [f.tag] if f.tag else [], "finding_ids": [f.id]})
        st["score"] = st.get("score", 0) + f.points
    return out


def _verdict(score: int, findings: list[Finding], complete: bool) -> dict:
    """Albert's "Can I pay?" answer, recomputed after our extra findings.
    A payment request or an incomplete analysis is never "OK to proceed"."""
    if score >= 70:
        key = "stop"
    elif score >= 30 or not complete or any(f.category == "payment_or_data_request" for f in findings):
        key = "verify"
    else:
        key = "pay"
    return {"key": key, "label": engine.VERDICTS[key]}


def analyze(email: AnalyzeRequest, model_call: Optional[llm.ModelCall] = None) -> AnalyzeResponse:
    started = time.monotonic()
    rules = engine.analyze_contract(email.model_dump())
    complete = bool(rules["analysis_complete"])
    limitations = list(rules["limitations"])

    # 1. Rule findings, re-checked against the email.
    findings: list[Finding] = []
    engine_ids: dict[int, str] = {}  # id(finding) -> the engine's own id, for remapping stages
    for f in rules["findings"]:
        finding = Finding.model_validate({**f, "source": "rules"})
        ev = verify(email, finding.evidence)
        if ev is None:
            complete = False
            continue
        finding = finding.model_copy(update={"evidence": ev})
        engine_ids[id(finding)] = f["id"]
        findings.append(finding)

    # 2. Extra deterministic link checks.
    flagged_links = {f.evidence.link_id for f in findings if f.evidence.kind == "link"}
    rule_cats = {f.category for f in findings}
    extras = (inspect_links_extra(email, flagged_links)
              + payroll_request(email, rule_cats)
              + company_name_in_sender_domain(email, rule_cats))

    # 3. Optional model pass.
    summary, model_name, model_extra, discarded = "", "rules-only", [], 0
    if model_call is not None:
        try:
            system, _schema = prompts.analyze_prompt()
            raw, _ = llm.call_json(model_call, system, prompts.analyze_user(email, findings + extras))
            model_extra, discarded = _model_findings(raw, email, bool(findings or extras))
            summary = str(raw.get("summary", "")).strip()[:600]
            _apply_ai_explanations(raw, findings + extras)
            model_name = llm.model_label("analyze")
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
        _for_extension(f, email)
        policy = lookup_payroll_policy(f.category, _quote_text(f)) or lookup_payroll_policy(f.category, text)
        if policy:
            f.policy_id = policy.id
            f.next_action = policy_next_action(policy.id)
            used_policies[policy.id] = policy

    for f in extras + model_extra:
        f.tag = f.tag or _extra_tag(f)
    stages = _stages(rules.get("stages") or [], engine_ids, findings, extras + model_extra)

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
        verdict=_verdict(score, all_findings, complete),
        callback=rules.get("callback"),
        hold_scenario=rules.get("hold_scenario"),
        stages=stages,
        ai_summary=summary or None,
        summary=summary,
        policies=list(used_policies.values()),
        practice=get_training_example(_SCAM_TO_DRILL.get(rules["scam_type"], "fake_invoice"), email.email_id or ""),
        model=model_name,
        elapsed_ms=elapsed,
    )
