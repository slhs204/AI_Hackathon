"""lookup_payroll_policy and get_training_example: read-only lookups in
versioned JSON files. Only fixed category names and the email's own text are
matched; nothing here can be steered into reading other files."""

import re
from typing import Optional

from .. import config
from ..schemas import Policy, PracticeQuestion

# Rule categories that always relate to one policy, regardless of wording.
_CATEGORY_POLICY = {"authority_impersonation": "payment_approval"}


def lookup_payroll_policy(category: str, text: str) -> Optional[Policy]:
    """The approved procedure that applies to a finding.

    For payment_or_data_request, the email text decides which procedure
    (bank change vs. W-2 request vs. wire vs. password)."""
    pols = {p["id"]: p for p in config.policies()}
    pid = _CATEGORY_POLICY.get(category)
    if category in ("payment_or_data_request", "manipulation_cue") and pid is None:
        low = text.lower()
        for p in config.policies():  # order in the JSON = priority
            if any(m in low for m in p["match"]):
                pid = p["id"]
                break
    if pid is None:
        return None
    p = pols[pid]
    return Policy(id=p["id"], title=p["title"], steps=p["steps"])


def policy_next_action(policy_id: str) -> str:
    return next(p["next_action"] for p in config.policies() if p["id"] == policy_id)


def get_training_example(drill_category: str, seed: str = "") -> Optional[PracticeQuestion]:
    """One reviewed practice email from the drill bank, same scam type when
    possible. `seed` picks deterministically so a re-check shows the same one."""
    bank = config.drill_questions()
    same = [q for q in bank if q["category"] == drill_category]
    if drill_category == "payroll":
        same += [q for q in bank if q["category"] == "bank_change"]
    pool = same or bank
    if not pool:
        return None
    idx = sum(map(ord, seed)) % len(pool) if seed else 0
    return PracticeQuestion.model_validate(pool[idx])


def email_text(subject: str, blocks: list) -> str:
    return re.sub(r"\s+", " ", subject + " " + " ".join(b.text for b in blocks))
