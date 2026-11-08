"""POST /triage: sort an inbox list so the riskiest emails are checked first.

Cheap and shallow on purpose: only sender, subject and the preview snippet.
Rules run first; the triage model (Haiku by default) may RAISE a priority but
never lower what the rules found. Only runs when the user asks for it.
"""

import logging
import time
from typing import Optional

from phishhook import engine

from . import llm, prompts
from .schemas import TriageItem, TriageRequest, TriageResponse

log = logging.getLogger("phishing-coach")
RANK = {"low": 0, "medium": 1, "high": 2}


def _rule_pass(e) -> tuple[int, str, list[str]]:
    rules = engine.analyze_contract({
        "sender": e.sender.model_dump(), "subject": e.subject,
        "blocks": [{"id": "b1", "text": e.snippet}] if e.snippet else [],
    })
    score = int(rules["risk_score"])
    cats = {f["category"] for f in rules["findings"]}
    tags = list(dict.fromkeys(f.get("tag") or f["category"] for f in rules["findings"]))
    if score >= 70 or cats & {"sender_impersonation", "authority_impersonation"}:
        priority = "high"
    elif score >= 30 or "payment_or_data_request" in cats or cats:
        priority = "medium"
    else:
        priority = "low"
    return score, priority, tags


def _validate_model_triage(raw: dict) -> None:
    if not isinstance(raw.get("items"), list):
        raise llm.ModelOutputInvalid("triage requires an items array")
    for item in raw["items"]:
        if not isinstance(item, dict) or not isinstance(item.get("email_id"), str) or not isinstance(
                item.get("priority"), str) or item["priority"] not in RANK or not isinstance(item.get("reason"), str):
            raise llm.ModelOutputInvalid("invalid triage item")


def triage(req: TriageRequest, model_call: Optional[llm.ModelCall] = None) -> TriageResponse:
    started = time.monotonic()
    items = []
    for e in req.emails:
        score, priority, tags = _rule_pass(e)
        reason = ("Automatic checks: " + ", ".join(tags[:3])) if tags else "No warning signs in the preview."
        items.append(TriageItem(email_id=e.email_id, priority=priority, reason=reason,
                                rule_score=score, tags=tags, source="rules"))

    model_name = "rules-only"
    if model_call is not None:
        rows = [{"email_id": e.email_id, "from": f"{e.sender.name} <{e.sender.address}>", "subject": e.subject,
                 "preview": e.snippet, "automatic_signs": it.tags} for e, it in zip(req.emails, items)]
        try:
            raw, _ = llm.call_json(model_call, prompts.TRIAGE_SYSTEM, prompts.triage_user(rows),
                                   validate=_validate_model_triage)
            by_id = {it.email_id: it for it in items}
            for m in raw.get("items") or []:
                if not isinstance(m, dict):
                    continue
                it = by_id.get(str(m.get("email_id")))
                p = m.get("priority")
                if it is None or p not in RANK:
                    continue
                if RANK[p] > RANK[it.priority]:  # the model may raise, never lower
                    it.priority, it.source = p, "model"
                    it.reason = str(m.get("reason", "")).strip()[:160] or it.reason
                elif it.source == "rules" and not it.tags and m.get("reason"):
                    it.reason = str(m["reason"]).strip()[:160]
            model_name = llm.model_label("triage")
        except llm.ModelUnavailable as exc:
            log.warning("triage model unavailable: %s", exc)
            model_name = "rules-only (model unavailable)"

    elapsed = int((time.monotonic() - started) * 1000)
    log.info("triage n=%d model=%s ms=%d", len(items), model_name, elapsed)
    return TriageResponse(items=items, model=model_name, elapsed_ms=elapsed)
