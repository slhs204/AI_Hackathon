"""Link checks the rule engine does not cover yet. Never opens a URL.

- javascript:/data:/file: links that run code instead of opening a page
- user@host tricks: https://acme-corp.com@evil.example/ really goes to evil.example
"""

from urllib.parse import urlsplit

from ..schemas import AnalyzeRequest, Evidence, Finding

_CODE_SCHEMES = {"javascript", "data", "file", "vbscript"}


def inspect_links_extra(email: AnalyzeRequest, already_flagged: set[str]) -> list[Finding]:
    out: list[Finding] = []
    for link in email.links[:20]:
        if link.id in already_flagged:
            continue
        href = link.href.strip()
        scheme = href.split(":", 1)[0].lower() if ":" in href else ""
        reason = None
        if scheme in _CODE_SCHEMES:
            reason = f"This link uses “{scheme}:”, which can run code or hide content instead of opening a web page."
        else:
            try:
                parts = urlsplit(href)
                if "@" in (parts.netloc or ""):
                    reason = (f"Everything before “@” in this address is ignored. The link really opens "
                              f"{parts.hostname}.")
            except ValueError:
                continue
        if reason:
            out.append(Finding(
                id="", category="deceptive_link", source="tool",
                evidence=Evidence(kind="link", link_id=link.id),
                explanation=reason,
                next_action="Do not click the link. Type the address you expect into the browser yourself.",
                points=20,
            ))
    return out
