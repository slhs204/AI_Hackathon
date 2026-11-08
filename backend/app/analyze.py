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
import re
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
PRESSURE_ONLY = {"urgency_pressure"}
PRESSURE_NOTE = ("Only pressure words were found in the visible text (such as \"urgent\" or \"today\"), with no request to pay, sign in, "
                 "open a file or send data. They are listed as notes, not warning signs.")

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


def _validate_model_analysis(raw: dict, schema: dict) -> None:
    """JSON syntax is not a successful review. Reject malformed structures before use."""
    def required_fields(value, shape, path="analysis"):
        if shape.get("type") == "object":
            if not isinstance(value, dict):
                raise llm.ModelOutputInvalid(f"{path}: expected object")
            for key in shape.get("required", []):
                if key not in value:
                    raise llm.ModelOutputInvalid(f"{path}.{key}: required field")
            for key, nested in shape.get("properties", {}).items():
                if key in value:
                    required_fields(value[key], nested, f"{path}.{key}")
        elif shape.get("type") == "array":
            if not isinstance(value, list):
                raise llm.ModelOutputInvalid(f"{path}: expected array")
            for index, item in enumerate(value):
                required_fields(item, shape["items"], f"{path}[{index}]")
        elif shape.get("type") == "string":
            if not isinstance(value, str):
                raise llm.ModelOutputInvalid(f"{path}: expected string")
            if "enum" in shape and value not in shape["enum"]:
                raise llm.ModelOutputInvalid(f"{path}: expected one of {', '.join(shape['enum'])}")
    required_fields(raw, schema)
    if not isinstance(raw.get("extra_findings"), list):
        raise llm.ModelOutputInvalid("analysis requires an extra_findings array")
    if "summary" in raw and not isinstance(raw["summary"], str):
        raise llm.ModelOutputInvalid("analysis summary must be text")
    if "email_type" in raw and raw["email_type"] not in (
            "routine_notification", "needs_check", "likely_phishing"):
        raise llm.ModelOutputInvalid("invalid email_type")
    expl = raw.get("explanations", [])
    if isinstance(expl, dict):  # legacy provider format
        valid = all(isinstance(k, str) and isinstance(v, str) for k, v in expl.items())
    else:
        valid = isinstance(expl, list) and all(
            isinstance(e, dict) and isinstance(e.get("category"), str)
            and isinstance(e.get("text"), str) for e in expl)
    if not valid:
        raise llm.ModelOutputInvalid("invalid explanations")
    for item in raw["extra_findings"]:
        if not isinstance(item, dict) or any(not isinstance(item.get(k), str)
                for k in ("category", "block_id", "quote", "explanation", "next_action")):
            raise llm.ModelOutputInvalid("invalid finding fields")
        if item["category"] not in MODEL_CATEGORIES:
            raise llm.ModelOutputInvalid("invalid finding category")
        if "confidence" in item and item["confidence"] not in ("low", "medium", "high"):
            raise llm.ModelOutputInvalid("invalid finding confidence")
        if "requested_action" in item and not isinstance(item["requested_action"], str):
            raise llm.ModelOutputInvalid("invalid requested_action")


# Conservative guard: lack of a rule hit is not evidence of lack of a risky request.
_RISKY_ACTION = re.compile(
    r"\b(sign[ -]?in|log[ -]?in|verify|download|install|open|click|pay|payment|wire|transfer|"
    r"bank|password|passcode|credential|verification code|gift cards?|personal data|"
    r"employee data|social security|ssn|w-?2|keep.{0,30}secret|confidential)\b", re.I)


def _can_demote_pressure(email: AnalyzeRequest) -> bool:
    return not (email.links or email.attachments or _RISKY_ACTION.search(
        email_text(email.subject, email.blocks)))


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


def _score_verdict(score: int, findings: list[Finding], complete: bool) -> dict:
    """Albert's score-based "Can I pay?" answer (unchanged from before rubric v2).
    A payment request or an incomplete analysis is never "OK to proceed"."""
    if score >= 70:
        key = "stop"
    elif score >= 30 or not complete or any(f.category == "payment_or_data_request" for f in findings):
        key = "verify"
    else:
        key = "pay"
    return {"key": key, "label": engine.VERDICTS[key]}


# Rubric v2: four plain-language questions. Each maps to public BEC/payroll fraud patterns
# (FBI IC3 BEC advisories, IRS W-2 phishing alerts); the agencies publish patterns, not weights.
DIMENSIONS = (
    ("sender", "Can you trust the sender?",
     {"sender_impersonation", "reply_to_mismatch", "authentication_failure", "authority_impersonation"},
     "The sender looks genuine as far as we can check.",
     "The sender may not be who they claim to be (look-alike or free-mail address, executive or brand name, Reply-To)."),
    ("money", "Does it ask for money, bank changes or employee data?",
     {"payment_or_data_request"},
     "No request for money, bank details, employee data or passwords.",
     "It asks to move money, change bank details, or send employee data or a password."),
    ("pressure", "Is there pressure to skip the normal process?",
     {"urgency_pressure", "authority_impersonation", "manipulation_cue"},
     "No pressure, secrecy or executive name-dropping.",
     "It rushes you, asks for secrecy or leans on an executive's authority."),
    ("links", "Are the links or attachments risky?",
     {"deceptive_link", "risky_attachment"},
     "No disguised links or risky attachments.",
     "A link or attachment is disguised or dangerous."),
)
UNKNOWN_TEXT = "Can't tell: {why}. Verify through a channel you already trust."
_RANK = {"pay": 0, "verify": 1, "stop": 2}


def _unknown_reasons(email: AnalyzeRequest, complete: bool, model_failed: bool) -> dict[str, str]:
    """Dimensions we could not check. Missing evidence is never shown as a pass."""
    body = " ".join(b.text for b in email.blocks).strip()
    why = {}
    if not body:
        for key in ("money", "pressure", "links"):
            why[key] = "the email text is empty or could not be read"
    # Neither directory matches nor user-supplied headers authenticate the sender.
    why["sender"] = ("the sender address is missing" if not email.sender.address.strip()
                     else "displayed sender details cannot establish who sent this email")
    if not complete or model_failed:
        reason = "the AI review failed" if model_failed else "the analysis is incomplete"
        for key, *_ in DIMENSIONS:
            why.setdefault(key, reason)
    return why


def _dimensions(findings: list[Finding], unknown: dict[str, str]) -> list[dict]:
    out = []
    for key, question, cats, ok_text, warn_text in DIMENSIONS:
        hits = [f.id for f in findings if f.category in cats]
        if hits:
            status, answer = "warn", warn_text
        elif key in unknown:
            status, answer = "unknown", UNKNOWN_TEXT.format(why=unknown[key])
        else:
            status, answer = "ok", ok_text
        out.append({"key": key, "question": question, "status": status, "answer": answer, "finding_ids": hits})
    return out


def _rubric_verdict(dimensions: list[dict]) -> dict:
    """Red: money asked for with an untrusted sender or pressure, or a risky link/attachment from an untrusted
    sender. Amber: any single warning, or any question we could not answer. Green: four clear answers."""
    warn = {d["key"] for d in dimensions if d["status"] == "warn"}
    unknown = any(d["status"] == "unknown" for d in dimensions)
    if ("money" in warn and warn & {"sender", "pressure"}) or {"links", "sender"} <= warn:
        key, rule = "stop", "Asks for money or data (or sends a risky link) and the sender or the pressure is a red flag."
    elif warn:
        key, rule = "verify", "A warning sign: check through a channel you already trust."
    elif unknown:
        key, rule = "verify", "We could not check everything, so this is not an all-clear."
    else:
        key, rule = "pay", "None of the four questions raised a warning. This is not a guarantee."
    v = {"key": key, "label": engine.VERDICTS[key], "rule": rule}
    if unknown and not warn:
        v.update(state="unknown", label="Can't tell - call back first")
    return v


def _stricter(a: dict, b: dict) -> dict:
    """Invariant: the final answer is the stricter of the two; the rubric can only raise a verdict."""
    return a if _RANK[a["key"]] >= _RANK[b["key"]] else b


def _final_verdict(score: int, findings: list[Finding], complete: bool, dimensions: list[dict],
                   email_type: Optional[str] = None) -> dict:
    """The stricter of the score verdict and the rubric. The rubric is the quick first read and the fallback when
    the AI is off; it must not undo the model's false-alarm gating: when the model calls the email a routine
    notification and the rules found at most one kind of sign, the rubric alone never makes it red."""
    legacy = _score_verdict(score, findings, complete)
    rubric = _rubric_verdict(dimensions)
    rule_kinds = {f.category for f in findings if f.source != "model"}
    if rubric["key"] == "stop" and email_type == "routine_notification" and len(rule_kinds) <= 1:
        rubric = {"key": "verify", "label": engine.VERDICTS["verify"],
                  "rule": "The AI reads this as a routine notification and the rules found one kind of sign: check it, "
                          "but it is not marked red."}
    chosen = _stricter(rubric, legacy)
    final = dict(chosen)
    if chosen is legacy and legacy["key"] != rubric["key"]:
        final["rule"] = f"The risk score ({score}/100) calls for the stricter answer."
    final["basis"] = "rubric" if final["key"] == rubric["key"] else "score"
    if rubric.get("state") == "unknown" and final["key"] == "verify":
        final["state"] = "unknown"
    assert _RANK[final["key"]] >= max(_RANK[legacy["key"]], _RANK[rubric["key"]])
    return final


def analyze(email: AnalyzeRequest, model_call: Optional[llm.ModelCall] = None) -> AnalyzeResponse:
    started = time.monotonic()
    rules = engine.analyze_contract(email.model_dump())
    complete = bool(rules["analysis_complete"]) and email.extraction_complete
    limitations = list(rules["limitations"]) + email.extraction_limitations
    if not any(b.text.strip() for b in email.blocks) or not email.sender.address.strip():
        complete = False
        limitations.append("The sender address or readable message body is missing.")
    if not email.extraction_complete:
        limitations.append("The email extraction is partial; unextracted content was not checked.")

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
    email_type: Optional[str] = None
    if model_call is not None:
        try:
            system, _schema = prompts.analyze_prompt()
            raw, _ = llm.call_json(model_call, system, prompts.analyze_user(email, findings + extras),
                                   validate=lambda result: _validate_model_analysis(result, _schema))
            email_type = raw.get("email_type") if isinstance(raw.get("email_type"), str) else None
            model_extra, discarded = _model_findings(raw, email, bool(findings or extras))
            summary = str(raw.get("summary", "")).strip()[:600]
            _apply_ai_explanations(raw, findings + extras)
            model_name = llm.model_label("analyze")
        except llm.ModelUnavailable as exc:
            log.warning("model unavailable: %s", exc)
            complete = False
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

    # Pressure words alone ("urgent", "today", "confidential") with nothing else
    # are the most common false alarm: real payroll deadlines sound like that too.
    # Without a request to pay, sign in, open a file or send data, they become a
    # note instead of a hook piece, including on partial extraction. Identity warnings
    # remain; another action or manipulation sign keeps pressure as a warning.
    notes: list[Finding] = []
    identity_only = {"sender_impersonation", "reply_to_mismatch", "authentication_failure", "authority_impersonation"}
    if (_can_demote_pressure(email) and any(f.category in PRESSURE_ONLY for f in all_findings)
            and all(f.category in PRESSURE_ONLY | identity_only for f in all_findings)):
        notes = [f for f in all_findings if f.category in PRESSURE_ONLY]
        all_findings = [f for f in all_findings if f.category not in PRESSURE_ONLY]
        score = min(100, sum(f.points for f in all_findings))
        moved = {f.id for f in notes}
        for st in stages:
            st["flags"] = [fl for fl in st["flags"] if not set(fl.get("finding_ids", [])) <= moved]
            st["score"] = sum(fl.get("points", 0) for fl in st["flags"])
        if notes:
            limitations.append(PRESSURE_NOTE)

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
    unknown = _unknown_reasons(email, complete, model_name.endswith("(model unavailable)"))
    dimensions = _dimensions(all_findings, unknown)
    if notes:  # de63312: pressure words alone are notes, not a warning; say so instead of a bare check mark
        for d in dimensions:
            if d["key"] == "pressure" and d["status"] == "ok":
                d["answer"] = "Only pressure words such as \"urgent\" or \"today\" (listed as a note, not a warning sign)."
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
        notes=notes,
        recommended_actions=rules["recommended_actions"],
        limitations=limitations,
        verdict=_final_verdict(score, all_findings, complete, dimensions, email_type),
        dimensions=dimensions,
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
