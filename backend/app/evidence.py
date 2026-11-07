"""Check that a finding's evidence really exists in the submitted email.

The model may paraphrase, change case, or invent text. We accept small
formatting differences (case, repeated whitespace, curly quotes) and then
return the exact original text, so the extension highlights what is really
in the email. Anything else is unverified and must never be highlighted.
"""

import unicodedata
from typing import Optional

from .schemas import AnalyzeRequest, Evidence

_QUOTE_MAP = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', " ": " "})


def _normalize_with_map(text: str) -> tuple[str, list[int]]:
    """Normalized string plus, for each of its characters, the index of the
    original character it came from."""
    out: list[str] = []
    index_map: list[int] = []
    prev_space = True  # also strips leading whitespace
    for i, ch in enumerate(text):
        for c in unicodedata.normalize("NFKC", ch).translate(_QUOTE_MAP):
            if c.isspace():
                if prev_space:
                    continue
                out.append(" ")
                index_map.append(i)
                prev_space = True
            else:
                out.append(c.casefold())
                index_map.append(i)
                prev_space = False
    while out and out[-1] == " ":
        out.pop()
        index_map.pop()
    return "".join(out), index_map


def normalize(text: str) -> str:
    return _normalize_with_map(text)[0]


def find_exact(haystack: str, quote: str) -> Optional[str]:
    """Original substring of haystack matching quote after normalization."""
    needle = normalize(quote)
    if not needle:
        return None
    norm, index_map = _normalize_with_map(haystack)
    pos = norm.find(needle)
    if pos < 0:
        return None
    return haystack[index_map[pos] : index_map[pos + len(needle) - 1] + 1]


def _metadata_text(email: AnalyzeRequest, field: str) -> Optional[str]:
    return {
        "sender.name": email.sender.name,
        "sender.address": email.sender.address,
        "reply_to": email.reply_to,
        "subject": email.subject,
        "authentication_results": email.authentication_results,
        "attachments": "\n".join(a.name for a in email.attachments),
    }.get(field)


def verify(email: AnalyzeRequest, evidence: Evidence) -> Optional[Evidence]:
    """Evidence with its quote/value replaced by the exact original text, or
    None when it cannot be found where it says."""
    if evidence.kind == "text":
        block = email.block(evidence.block_id)
        exact = find_exact(block.text, evidence.quote) if block else None
        return evidence.model_copy(update={"quote": exact}) if exact else None
    if evidence.kind == "link":
        return evidence if email.link(evidence.link_id) else None
    text = _metadata_text(email, evidence.field or "")
    exact = find_exact(text, evidence.value) if text else None
    return evidence.model_copy(update={"value": exact}) if exact else None
