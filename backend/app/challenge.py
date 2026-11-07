"""POST /challenge: reassess ONE finding with the user's extra context.

The result updates the current assessment only. It is not stored, not used
for training, and never clears a finding: the best it can say is
"less concerning", and any money / data / password procedure still applies.
"""

import logging
import re
from typing import Optional

from . import llm, prompts
from .schemas import ChallengeRequest, ChallengeResponse
from .tools.lookup import email_text, lookup_payroll_policy, policy_next_action

log = logging.getLogger("phishing-coach")

# Context that describes an independent check the user already did.
_VERIFIED_CONTEXT = re.compile(
    r"\b(called|phoned|rang|spoke (?:to|with)|talked (?:to|with)|in person|face to face|confirmed by phone|"
    r"verified (?:by|on|over) (?:the )?phone|met (?:them|him|her))\b", re.I)


def _fallback(context: str, has_policy: bool) -> tuple[str, str, str]:
    if _VERIFIED_CONTEXT.search(context):
        return ("less_concerning",
                "Thanks, that context helps: an independent conversation makes this request less unexpected.",
                "If they asked you to act from this email, the company procedure still applies."
                if has_policy else "The email itself could still have been sent by someone else.")
    return ("still_concerning",
            "Thanks for the context. It doesn't include an independent check, so this warning sign still stands.",
            "We still can't tell whether the person you know actually sent this email.")


def challenge(req: ChallengeRequest, model_call: Optional[llm.ModelCall] = None) -> ChallengeResponse:
    f = req.finding
    quote = f.evidence.quote or f.evidence.value or ""
    policy = lookup_payroll_policy(f.category, quote) or lookup_payroll_policy(
        f.category, email_text(req.email.subject, req.email.blocks))
    next_action = policy_next_action(policy.id) if policy else f.next_action
    steps = policy.steps if policy else []

    assessment, message, unresolved = _fallback(req.user_context, policy is not None)
    model_name = "rules-only"
    if model_call is not None:
        try:
            raw, _ = llm.call_json(model_call, prompts.CHALLENGE_SYSTEM,
                                   prompts.challenge_user(req.email, f, req.user_context, steps))
            a = raw.get("assessment")
            if a in ("still_concerning", "less_concerning"):
                assessment = a
                message = str(raw.get("message", "")).strip()[:600] or message
                unresolved = str(raw.get("still_unresolved", "")).strip()[:600] or unresolved
                model_name = llm.model_label()
        except llm.ModelUnavailable as exc:
            log.warning("model unavailable in challenge: %s", exc)
            model_name = "rules-only (model unavailable)"

    # The procedure is not negotiable, whatever the model or the user says.
    if policy and policy.title not in unresolved:
        unresolved = f"{unresolved} Procedure: {policy.title} — {steps[0] if steps else ''}".strip()

    log.info("challenge finding=%s category=%s assessment=%s model=%s", f.id, f.category, assessment, model_name)
    return ChallengeResponse(finding_id=f.id, assessment=assessment, message=message,
                             still_unresolved=unresolved, next_action=next_action, model=model_name)
