"""Payroll-specific checks the rule engine misses. Found by the eval:

- "Please change my salary account today" (the team's own demo email) is not
  matched by the engine's PAYMENT_PATTERNS, so the hook shows no payment piece.
- acme-payroll-support.com is not flagged, because the engine's
  brand-inside-domain check needs the whole name "acmecorp".

These live here instead of in phishhook/engine.py so Albert's file stays an
unchanged copy. Tell Albert; if he adds them upstream, delete these.
"""

import re

from phishhook import engine

from ..evidence import find_exact
from ..schemas import AnalyzeRequest, Evidence, Finding

PAYROLL_PATTERNS = [
    r"\b(?:change|update|switch|replace|redirect)\s+(?:my|our|the|his|her|their)?\s*"
    r"(?:salary|pay|payroll|paycheck|wage|deposit)\s+(?:account|details|information|info|bank)\b",
    r"\b(?:salary|payroll|paycheck)\s+(?:account|bank)\b",
    r"\bnew\s+(?:salary|payroll|paycheck)\b",
]
_GENERIC = {"corp", "inc", "llc", "ltd", "group", "co", "company", "the"}


def payroll_request(email: AnalyzeRequest, already: set[str]) -> list[Finding]:
    if "payment_or_data_request" in already:
        return []
    for block in email.blocks:
        for pat in PAYROLL_PATTERNS:
            m = re.search(pat, block.text, re.I)
            if m:
                return [Finding(
                    id="", category="payment_or_data_request", source="tool", points=20,
                    evidence=Evidence(kind="text", block_id=block.id, quote=m.group(0)),
                    explanation="This email asks to change where someone's pay goes. Payroll diversion is how "
                                "these scams turn into real losses, so it must be verified outside email.",
                    next_action="Verify through a channel you already trust.",
                )]
    return []


def company_name_in_sender_domain(email: AnalyzeRequest, already: set[str]) -> list[Finding]:
    if "sender_impersonation" in already:
        return []
    address = email.sender.address.lower()
    domain = address.rsplit("@", 1)[-1] if "@" in address else ""
    if not domain or engine.trusted_entity_for(domain):
        return []
    label = engine.registrable(domain).rsplit(".", 1)[0]
    company = engine.DIRECTORY["company"]
    for real in company["domains"]:
        tokens = [t for t in re.split(r"[-.]", real.rsplit(".", 1)[0]) if len(t) >= 4 and t not in _GENERIC]
        hit = next((t for t in tokens if t in label), None)
        if hit and find_exact(email.sender.address, domain):
            return [Finding(
                id="", category="sender_impersonation", source="tool", points=30,
                evidence=Evidence(kind="metadata", field="sender.address", value=domain),
                explanation=f"“{domain}” contains the company name “{hit}” but is not {real}. Scammers register "
                            f"domains like this so it looks internal at a glance.",
                next_action=f"Check the address carefully: real {company['name']} mail comes from {real}.",
            )]
    return []
