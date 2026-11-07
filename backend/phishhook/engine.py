"""Rule engine: parse a raw email and find payroll-weighted phishing red flags."""
import ipaddress
import json
import re
from email import policy
from email.parser import Parser
from email.utils import getaddresses, parseaddr
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

DIRECTORY = json.loads((Path(__file__).parent / "directory.json").read_text())

POINTS = {
    "lookalike": 30,
    "reply_to": 20,
    "auth": 20,
    "exec": 25,
    "links": 20,
    "attachment": 20,
    "payment": 20,
    "urgency_each": 8,
    "urgency_cap": 24,
}
FINANCE_MULTIPLIER = 1.3
IDENTITY_CATEGORIES = {"lookalike", "reply_to", "exec"}

HIGH_RISK_EXT = {
    ".html", ".htm", ".shtml", ".svg", ".iso", ".img", ".vhd", ".exe", ".scr", ".js",
    ".vbs", ".bat", ".cmd", ".lnk", ".hta", ".msi", ".jar", ".ps1", ".docm", ".xlsm",
    ".pptm", ".xlam", ".one", ".zip", ".rar", ".7z",
}
SAFE_DOC_EXT = {".pdf", ".docx", ".xlsx", ".doc", ".xls", ".txt", ".csv", ".png", ".jpg"}

URGENCY_PATTERNS = [
    r"\burgent(?:ly)?\b", r"\bimmediately\b", r"\bASAP\b", r"\bright away\b",
    r"\bwithin (?:the next )?\d+ (?:hours?|minutes?)\b", r"\bbefore (?:end of day|EOD|noon|close of business|\d{1,2}(?::\d\d)? ?[ap]m)\b",
    r"\bby end of (?:day|today)\b", r"\btoday\b", r"\bfinal (?:notice|reminder|warning)\b",
    r"\b(?:will be|be) (?:suspended|disabled|locked|deactivated|terminated)\b",
    r"\bkeep (?:this|it) (?:confidential|between us|quiet)\b", r"\bconfidential\b",
    r"\bdo not (?:call|phone|discuss|tell|share)\b", r"\bcan'?t take (?:any )?calls\b", r"\bdon'?t (?:call|tell|discuss)\b",
    r"\b(?:in|stuck in) (?:a|the) (?:board )?meeting\b", r"\bcan'?t talk\b", r"\btime[- ]sensitive\b",
    r"\boverdue\b", r"\blate (?:fee|payment penalty)\b",
]

PAYMENT_PATTERNS = [
    r"\b(?:new|updated|changed?|different) (?:bank(?:ing)?|account|remittance|payment) (?:details|information|info|account|instructions)\b",
    r"\bchanged? (?:our|my) bank(?:ing)?\b", r"\bnew bank(?:ing)? (?:account|details)\b", r"\bbank(?:ing)? details\b",
    r"\bremittance (?:details|information|instructions)\b",
    r"\brouting (?:number|no\.?)\b", r"\baccount (?:number|no\.?)\b", r"\bIBAN\b", r"\bSWIFT\b", r"\bABA\b",
    r"\bwire (?:transfer|the|a|\$)", r"\bwire\b(?= [\$\d])", r"\bprocess (?:a|the) (?:wire|payment)\b",
    r"\bgift ?cards?\b", r"\bdirect deposit\b",
    r"\b(?:verify|confirm|re-?enter|update) your (?:password|credentials|login|account)\b",
    r"\bsign in to (?:view|review|access)\b",
    r"\bW-?2s?\b", r"\bsocial security numbers?\b", r"\bSSNs?\b", r"\b(?:employee|staff) (?:list|roster|records|data)\b",
    r"\bskip (?:the )?(?:usual |normal )?(?:approval|verification|call-?back)\b", r"\bbypass (?:the )?approval\b",
]
FINANCE_CONTEXT = re.compile(r"\b(invoice|payment|wire|remit|bank|account number|gift card|direct deposit|payroll|salary|W-?2)\b", re.I)

HOMOGLYPHS = [("rn", "m"), ("vv", "w"), ("0", "o"), ("1", "l"), ("i", "l"), ("|", "l"), ("5", "s"), ("$", "s")]
CONFUSABLE = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "х": "x", "у": "y", "і": "i", "ӏ": "l",
    "ԁ": "d", "ɡ": "g", "ո": "n", "ս": "u",
})
MULTI_PART_TLDS = {"co.uk", "com.au", "co.jp", "com.tw", "co.nz", "com.br"}


# ---------------------------------------------------------------- parsing

class _HTMLToText(HTMLParser):
    BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "table", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.links = []
        self._anchor = None
        self._skip = 0

    def _len(self):
        return sum(len(s) for s in self.out)

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script", "head", "title"):
            self._skip += 1
        if tag in self.BLOCK:
            self._newline()
        if tag == "a":
            self._anchor = {"href": dict(attrs).get("href", "") or "", "start": self._len()}

    def handle_endtag(self, tag):
        if tag in ("style", "script", "head", "title"):
            self._skip = max(0, self._skip - 1)
        if tag == "a" and self._anchor is not None:
            a = self._anchor
            a["end"] = self._len()
            a["text"] = "".join(self.out)[a["start"]:a["end"]]
            if a["text"].strip():
                self.links.append(a)
            self._anchor = None
        if tag in self.BLOCK:
            self._newline()

    def handle_data(self, data):
        if self._skip:
            return
        text = re.sub(r"\s+", " ", data)
        if not text.strip() and (not self.out or self.out[-1].endswith(("\n", " "))):
            return
        if self.out and self.out[-1].endswith("\n"):
            text = text.lstrip()
        self.out.append(text)

    def _newline(self):
        joined = "".join(self.out)
        if joined and not joined.endswith("\n\n"):
            self.out.append("\n")


def html_to_text(html):
    p = _HTMLToText()
    p.feed(html)
    p.close()
    text = "".join(p.out)
    stripped = text.lstrip()
    shift = len(text) - len(stripped)
    links = [{"text": l["text"], "href": l["href"], "start": l["start"] - shift, "end": l["end"] - shift}
             for l in p.links]
    return stripped.rstrip(), links


def _domain_of(addr):
    return addr.rsplit("@", 1)[-1].strip().lower().rstrip(">") if "@" in addr else ""


def registrable(domain):
    domain = (domain or "").lower().strip(".")
    parts = domain.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in MULTI_PART_TLDS:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def parse_email(raw):
    raw = raw.replace("\r\n", "\n")
    has_headers = bool(re.match(r"^[A-Za-z][A-Za-z0-9-]*:\s", raw.lstrip()))
    if not has_headers:
        raw = "Subject: (pasted text)\n\n" + raw
    msg = Parser(policy=policy.default).parsestr(raw.lstrip())

    def h(name):
        v = msg.get(name)
        return str(v) if v is not None else ""

    from_name, from_addr = parseaddr(h("From"))
    reply_name, reply_addr = parseaddr(h("Reply-To"))
    _, return_path = parseaddr(h("Return-Path"))

    plain, html, attachments = None, None, []
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if part.is_multipart():
            continue
        filename = part.get_filename()
        disp = part.get_content_disposition()
        if filename or disp == "attachment":
            attachments.append({"name": filename or "(unnamed)", "mime": part.get_content_type()})
            continue
        ctype = part.get_content_type()
        try:
            content = part.get_content()
        except Exception:
            content = part.get_payload(decode=True) or b""
            content = content.decode("utf-8", "replace") if isinstance(content, bytes) else str(content)
        if ctype == "text/html" and html is None:
            html = content
        elif ctype == "text/plain" and plain is None:
            plain = content

    if html:
        body, links = html_to_text(html)
    else:
        body = (plain or "").strip()
        links = [{"text": m.group(0), "href": m.group(0), "start": m.start(), "end": m.end()}
                 for m in re.finditer(r"https?://[^\s<>\"')\]]+", body)]

    return {
        "has_headers": has_headers,
        "from_name": from_name,
        "from_addr": from_addr.lower(),
        "from_domain": _domain_of(from_addr),
        "reply_to": reply_addr.lower(),
        "reply_to_domain": _domain_of(reply_addr),
        "return_path": return_path.lower(),
        "to": ", ".join(a for _, a in getaddresses([h("To")]) if a),
        "subject": h("Subject"),
        "date": h("Date"),
        "auth_results": " ".join(str(v) for v in (msg.get_all("Authentication-Results") or [])),
        "body": body,
        "links": links,
        "attachments": attachments,
    }


# ---------------------------------------------------------------- domain helpers

def levenshtein(a, b):
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def skeleton(s):
    s = s.lower().translate(CONFUSABLE)
    for src, dst in HOMOGLYPHS:
        s = s.replace(src, dst)
    return s


def trusted_entities():
    c = DIRECTORY["company"]
    yield {"kind": "company", "name": c["name"], "domains": c["domains"], "phone": None}
    for v in DIRECTORY["vendors"]:
        yield {"kind": "vendor", **v}
    for b in DIRECTORY["brands"]:
        yield {"kind": "brand", "phone": None, **b}


def trusted_entity_for(domain):
    reg = registrable(domain)
    if reg in DIRECTORY["free_mail"]:
        return None  # anyone can register a free-mail address, so it never vouches for a brand or company
    for ent in trusted_entities():
        if reg in ent["domains"]:
            return ent
    return None


def _decode_punycode(domain):
    try:
        return domain.encode("ascii").decode("idna")
    except Exception:
        return domain


def lookalike_match(domain):
    """Return (entity, trusted_domain, reason) if domain imitates a trusted one."""
    if not domain or trusted_entity_for(domain):
        return None
    reg = registrable(domain)
    if reg in DIRECTORY["free_mail"]:
        return None
    is_puny = any(label.startswith("xn--") for label in domain.split("."))
    decoded = _decode_punycode(reg) if is_puny else reg
    label = decoded.rsplit(".", 1)[0]
    for ent in trusted_entities():
        for td in ent["domains"]:
            t_label = td.rsplit(".", 1)[0]
            if is_puny and skeleton(label) == skeleton(t_label):
                return ent, td, f"uses international look-alike characters (punycode “{reg}” displays as “{decoded}”)"
            if skeleton(label) == skeleton(t_label) and label != t_label:
                return ent, td, "swaps letters for look-alike characters (e.g. 1↔l, 0↔o, rn↔m)"
            dist = levenshtein(label, t_label)
            if 0 < dist <= 2 and len(t_label) >= 5:
                return ent, td, f"is {dist} character{'s' if dist > 1 else ''} away from the real domain"
            if label == t_label and decoded != td:
                return ent, td, "uses the real name with a different ending (TLD)"
            brand = t_label.replace("-", "")
            if len(brand) >= 5 and brand in re.sub(r"[-.]", "", decoded) and label != t_label:
                return ent, td, f"wraps the real name “{t_label}” inside a different domain"
    return None


# ---------------------------------------------------------------- detectors

def _body_marks(body, patterns, limit=6):
    marks, seen = [], set()
    for pat in patterns:
        for m in re.finditer(pat, body, re.I):
            if any(m.start() < e and s < m.end() for s, e in seen):
                continue
            seen.add((m.start(), m.end()))
            marks.append({"kind": "body", "start": m.start(), "end": m.end(), "quote": m.group(0)})
    marks.sort(key=lambda x: x["start"])
    return marks[:limit]


def _header_mark(field, quote):
    return {"kind": "header", "field": field, "quote": quote}


def detect_lookalike(em):
    candidates = [("from", em["from_domain"])]
    if em["reply_to_domain"]:
        candidates.append(("reply_to", em["reply_to_domain"]))
    for field, dom in candidates:
        hit = lookalike_match(dom)
        if hit:
            ent, td, reason = hit
            return {
                "category": "lookalike",
                "title": "Look-alike sender domain",
                "points": POINTS["lookalike"],
                "why": f"“{dom}” is not “{td}”. It {reason}. Criminals register domains like this so a quick glance "
                       f"reads as {ent['name']}.",
                "marks": [_header_mark(field, dom)],
                "impersonates": ent,
            }
    name = em["from_name"].lower()
    for ent in trusted_entities():
        if ent["kind"] == "brand" and ent["name"].lower() in name and not trusted_entity_for(em["from_domain"]):
            return {
                "category": "lookalike",
                "title": f"Claims to be {ent['name']}, sent from elsewhere",
                "points": POINTS["lookalike"],
                "why": f"The sender name says “{ent['name']}” but the address is @{em['from_domain']}. "
                       f"Real {ent['name']} mail comes from {', '.join(ent['domains'])}.",
                "marks": [_header_mark("from", em["from_name"]), _header_mark("from", em["from_domain"])],
                "impersonates": ent,
            }
    return None


def detect_reply_to(em):
    if not em["reply_to_domain"] or not em["from_domain"]:
        return None
    if registrable(em["reply_to_domain"]) == registrable(em["from_domain"]):
        return None
    return {
        "category": "reply_to",
        "title": "Replies go somewhere else",
        "points": POINTS["reply_to"],
        "why": f"The mail says it is from @{em['from_domain']}, but if you press Reply your answer goes to "
               f"{em['reply_to']}. That is how attackers keep the conversation once you respond.",
        "marks": [_header_mark("reply_to", em["reply_to"])],
    }


def parse_auth_results(auth):
    out = {}
    for mech in ("spf", "dkim", "dmarc"):
        m = re.search(rf"\b{mech}=(\w+)", auth, re.I)
        if m:
            out[mech] = m.group(1).lower()
    return out


def detect_auth(em):
    results = parse_auth_results(em["auth_results"])
    if not results:
        return None
    bad = {k: v for k, v in results.items() if v in ("fail", "softfail", "permerror", "none", "neutral")}
    if not bad:
        return None
    summary = ", ".join(f"{k.upper()}={v}" for k, v in bad.items())
    return {
        "category": "auth",
        "title": "Failed sender authentication",
        "points": POINTS["auth"],
        "why": f"The receiving mail server checked whether this message really came from @{em['from_domain']} "
               f"and it did not pass ({summary}). The “From” line can be forged; these checks cannot.",
        "marks": [_header_mark("auth", f"{k}={v}") for k, v in bad.items()],
    }


def detect_exec(em):
    company = DIRECTORY["company"]
    if not em["from_domain"] or registrable(em["from_domain"]) in company["domains"]:
        return None
    name = em["from_name"].lower()
    for ex in company["executives"]:
        if ex["name"].lower() in name or re.search(rf"\b{ex['title'].lower()}\b", name):
            return {
                "category": "exec",
                "title": f"Pretends to be your {ex['title']}",
                "points": POINTS["exec"],
                "why": f"The sender name says “{em['from_name']}” ({company['name']} {ex['title']}), but the address "
                       f"is outside the company (@{em['from_domain']}). Executive impersonation (CEO fraud) is the "
                       f"classic way payroll and finance teams are tricked into wiring money.",
                "marks": [_header_mark("from", em["from_name"])],
                "executive": ex,
            }
    for emp in company.get("employees", []):
        if emp["name"].lower() in name:
            return {
                "category": "exec",
                "title": "Pretends to be a colleague",
                "points": POINTS["exec"],
                "why": f"“{emp['name']}” ({emp['title']}) is in the company directory, but this mail comes from an "
                       f"outside address (@{em['from_domain']}), not @{company['domains'][0]}. Payroll and "
                       f"direct-deposit fraud starts exactly like this.",
                "marks": [_header_mark("from", em["from_name"])],
                "executive": emp,
            }
    return None


def _link_domain(href):
    try:
        return (urlsplit(href.strip()).hostname or "").lower()
    except ValueError:
        return ""


def detect_links(em):
    marks, reasons = [], []
    for link in em["links"]:
        href_host = _link_domain(link["href"])
        if not href_host:
            continue
        text = link["text"].strip()
        shown = re.search(r"(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", text, re.I)
        reason = None
        try:
            ipaddress.ip_address(href_host)
            reason = f"“{text}” points to a raw IP address ({href_host}), not a company website"
        except ValueError:
            pass
        if not reason and registrable(href_host) in DIRECTORY["url_shorteners"]:
            reason = f"“{text}” hides its destination behind a URL shortener ({href_host})"
        if not reason and shown and shown.group(1).lower().removeprefix("www.") != href_host.removeprefix("www."):
            reason = f"the text shows {shown.group(1)} but the link actually opens {href_host}"
        if not reason and lookalike_match(href_host):
            ent, td, _ = lookalike_match(href_host)
            reason = f"“{text}” opens {href_host}, a look-alike of {td}"
        if reason:
            marks.append({"kind": "body", "start": link["start"], "end": link["end"], "quote": link["text"],
                          "href": link["href"]})
            reasons.append(reason)
    if not marks:
        return None
    return {
        "category": "links",
        "title": "Link is not what it says" if len(marks) == 1 else f"{len(marks)} deceptive links",
        "points": POINTS["links"],
        "why": "Hover before you click: " + "; ".join(reasons) + ".",
        "marks": marks,
    }


def detect_attachments(em):
    bad = []
    for i, att in enumerate(em["attachments"]):
        name = att["name"].lower()
        exts = re.findall(r"\.[a-z0-9]{1,5}", name)
        last = exts[-1] if exts else ""
        double = len(exts) >= 2 and exts[-2] in SAFE_DOC_EXT and last not in SAFE_DOC_EXT
        if last in HIGH_RISK_EXT or double:
            bad.append((i, att["name"], "double extension" if double else last))
    if not bad:
        return None
    desc = ", ".join(f"{n} ({r})" for _, n, r in bad)
    return {
        "category": "attachment",
        "title": "Dangerous attachment",
        "points": POINTS["attachment"],
        "why": f"{desc}. Files like this are used to show fake login pages or install malware. A real invoice is "
               f"a plain PDF — never an .html page, macro spreadsheet or disk image.",
        "marks": [{"kind": "attachment", "index": i, "quote": n} for i, n, _ in bad],
    }


def detect_urgency(em):
    marks = _body_marks(em["subject"] + "\n" + em["body"], URGENCY_PATTERNS)
    if not marks:
        return None
    offset = len(em["subject"]) + 1
    fixed = []
    for m in marks:
        if m["start"] < offset:
            fixed.append(_header_mark("subject", m["quote"]))
        else:
            fixed.append({**m, "start": m["start"] - offset, "end": m["end"] - offset})
    return {
        "category": "urgency",
        "title": "Pressure and secrecy",
        "points": min(POINTS["urgency_each"] * len(fixed), POINTS["urgency_cap"]),
        "why": "Words like “" + "”, “".join(dict.fromkeys(m["quote"] for m in fixed)) + "” are designed to rush you "
               "past your normal checks. Real partners can wait 10 minutes for a call-back.",
        "marks": fixed,
    }


def detect_payment(em):
    marks = [_header_mark("subject", m["quote"]) for m in _body_marks(em["subject"], PAYMENT_PATTERNS)]
    marks += _body_marks(em["body"], PAYMENT_PATTERNS)
    if not marks:
        return None
    is_cred = [bool(re.search(r"password|credential|login|sign in", m["quote"], re.I)) for m in marks]
    creds = any(is_cred)
    return {
        "money": not all(is_cred),
        "category": "payment",
        "title": "Asks for credentials" if creds and len(marks) == 1 else "Asks to move money, change bank details or send employee data",
        "points": POINTS["payment"],
        "why": "This email asks you to " + ("hand over your login" if creds and len(marks) == 1 else
               "send money, change where pay is deposited, share employee data or skip approval") + ". This is the action that turns a phishing email into "
               "a real loss — it must always be verified through a channel you already trust.",
        "marks": marks,
    }


DETECTORS = [detect_lookalike, detect_reply_to, detect_auth, detect_exec, detect_links, detect_attachments,
             detect_urgency, detect_payment]


# ---------------------------------------------------------------- scoring & advice

def trust_signals(em):
    signals = []
    auth = parse_auth_results(em["auth_results"])
    passed = [k.upper() for k, v in auth.items() if v == "pass"]
    if passed:
        signals.append(f"{' / '.join(passed)} passed for @{em['from_domain']} — proves which domain sent it, "
                       f"not that the sender is who they claim")
    if not auth and em["has_headers"]:
        signals.append("No Authentication-Results header — SPF/DKIM/DMARC not checked (not assumed safe)")
    ent = trusted_entity_for(em["from_domain"])
    if ent:
        signals.append(f"Sender domain matches {ent['name']} in your {'directory' if ent['kind'] != 'vendor' else 'vendor master file'}")
    return signals


def recommended_actions(findings, em):
    cats = {f["category"] for f in findings}
    actions = []
    vendor = next((f["impersonates"] for f in findings if f.get("impersonates", {}).get("kind") == "vendor"), None)
    if not vendor:
        ent = trusted_entity_for(em["from_domain"])
        vendor = ent if ent and ent["kind"] == "vendor" else None
    if "payment" in cats:
        if vendor and vendor.get("phone"):
            actions.append(f"Do not change any bank details. Call {vendor['name']} at {vendor['phone']} "
                           f"(number from the vendor master file — not from this email).")
        else:
            actions.append("Do not send money or change bank details. Call the requester back on a phone number "
                           "you already have on file — never one from this email.")
    exec_f = next((f for f in findings if f["category"] == "exec"), None)
    if exec_f:
        ex = exec_f["executive"]
        actions.append(f"Verify with {ex['name']} directly at {ex['phone']} or in person. "
                       f"Payment and payroll changes never skip the approval workflow because of an email.")
    if "links" in cats or "attachment" in cats:
        actions.append("Do not click the links or open the attachments.")
    if "reply_to" in cats or "lookalike" in cats:
        actions.append("Do not reply. Start a new email to the address saved in your contacts.")
    if findings:
        actions.append("Click “Report phishing” so IT can block the sender for the whole company.")
    else:
        actions.append("No red flags found. Still follow the call-back rule for any new or changed payment request.")
    return actions


def score(findings, em):
    raw = sum(f["points"] for f in findings)
    cats = {f["category"] for f in findings}
    finance_context = bool(FINANCE_CONTEXT.search(em["subject"] + " " + em["body"]))
    money = any(f["category"] == "payment" and f["money"] for f in findings)
    weighted = (money or (finance_context and "attachment" in cats)) and bool(cats & IDENTITY_CATEGORIES)
    total = min(100, round(raw * FINANCE_MULTIPLIER) if weighted else raw)
    level = "high" if total >= 70 else "medium" if total >= 30 else "low"
    return raw, total, level, weighted


def scam_type(findings, em):
    cats = {f["category"] for f in findings}
    text = (em["subject"] + " " + em["body"]).lower()
    if not findings:
        return "No known scam pattern"
    exec_title = next((f["executive"]["title"] for f in findings if f["category"] == "exec"), "")
    pay = next((f for f in findings if f["category"] == "payment"), None)
    if pay and not pay["money"]:
        return "Credential phishing"
    if pay and re.search(r"\bw-?2s?\b|social security|ssn|employee (?:list|records|data)", text):
        return "Employee-data theft (W-2 scam)"
    if exec_title in ("CEO", "CFO") and pay:
        return "CEO / CFO fraud (Business Email Compromise)"
    if pay and not cats & IDENTITY_CATEGORIES and "auth" not in cats:
        return "Unverified payment request"
    if pay and re.search(r"direct deposit|salary", text):
        return "Payroll diversion fraud (BEC)"
    if pay and re.search(r"bank|remittance|routing|iban", text):
        return "Bank-detail change fraud (BEC)"
    if "invoice" in text and cats & {"attachment", "links", "lookalike"}:
        return "Fake invoice"
    if cats & {"links", "lookalike"} and re.search(r"sign|password|document|review|verify", text):
        return "Credential phishing"
    return "Suspicious email"


def analyze(raw):
    em = parse_email(raw)
    findings = [f for f in (d(em) for d in DETECTORS) if f]
    for i, f in enumerate(findings, 1):
        f["n"] = i
    raw_score, total, level, weighted = score(findings, em)
    stages = build_stages(findings)
    for f in findings:
        for m in f["marks"]:
            m["tag"] = flag_tag(f["category"], m["quote"])
    return {
        "stages": stages,
        "email": {k: em[k] for k in ("from_name", "from_addr", "reply_to", "return_path", "to", "subject", "date",
                                     "auth_results", "body", "attachments", "has_headers", "links")},
        "findings": [{k: v for k, v in f.items() if k not in ("impersonates", "executive")} for f in findings],
        "score": total,
        "raw_score": raw_score,
        "level": level,
        "finance_weighted": weighted,
        "scam_type": scam_type(findings, em),
        "trust_signals": trust_signals(em),
        "actions": recommended_actions(findings, em),
        "verdict": verdict(findings, total),
        "callback": callback_contact(findings, em),
        "hold_scenario": hold_scenario(findings, em),
        "drill_category": drill_category(findings, em),
        "fingerprint": fingerprint(em, findings, total),
        "mode": "rules",
    }


# ---------------------------------------------------------------- team API contract (PROJECT_SPEC §7)

CONTRACT_CATEGORY = {
    "lookalike": "sender_impersonation", "reply_to": "reply_to_mismatch", "auth": "authentication_failure",
    "exec": "authority_impersonation", "links": "deceptive_link", "attachment": "risky_attachment",
    "urgency": "urgency_pressure", "payment": "payment_or_data_request",
}


def analyze_contract(req):
    """POST /analyze body per PROJECT_SPEC draft (sender, subject, blocks, links) -> contract response."""
    sender = req.get("sender") or {}
    blocks = [b for b in req.get("blocks") or [] if isinstance(b, dict) and "id" in b]
    links = [l for l in req.get("links") or [] if isinstance(l, dict) and "id" in l]
    sep = "\n\n"
    body, offsets = "", []
    for b in blocks:
        offsets.append((len(body), b["id"]))
        body += str(b.get("text", "")) + sep
    em = {
        "has_headers": False, "from_name": str(sender.get("name", "")), "from_addr": str(sender.get("address", "")).lower(),
        "reply_to": str(req.get("reply_to", "")).lower(), "return_path": "", "to": "", "date": "",
        "subject": str(req.get("subject", "")), "auth_results": str(req.get("authentication_results", "")),
        "body": body, "attachments": [{"name": str(a.get("name", "")), "mime": ""} for a in req.get("attachments") or []],
        "links": [],
    }
    em["from_domain"] = _domain_of(em["from_addr"])
    em["reply_to_domain"] = _domain_of(em["reply_to"])
    link_ids = {}
    for l in links:
        block_start = next((o for o, bid in offsets if bid == l.get("block_id")), None)
        text = str(l.get("display_text", ""))
        pos = body.find(text, block_start) if block_start is not None else -1
        start = pos if pos >= 0 else len(body)
        em["links"].append({"text": text, "href": str(l.get("href", "")), "start": start, "end": start + len(text)})
        link_ids[start] = l["id"]

    def block_for(pos):
        bid, bstart = None, 0
        for o, b in offsets:
            if o <= pos:
                bid, bstart = b, o
        return bid, bstart

    findings = [f for f in (d(em) for d in DETECTORS) if f]
    out, complete = [], True
    actions = recommended_actions(findings, em)
    for f in findings:
        for m in f["marks"]:
            if m["kind"] == "header":
                field = {"from": "sender.address", "reply_to": "reply_to", "subject": "subject", "auth": "authentication_results"}[m["field"]]
                if m["field"] == "from" and m["quote"] == em["from_name"]:
                    field = "sender.name"
                evidence = {"kind": "metadata", "field": field, "value": m["quote"]}
            elif m["kind"] == "attachment":
                evidence = {"kind": "metadata", "field": "attachments", "value": m["quote"]}
            elif m.get("href") is not None and m["start"] in link_ids:
                evidence = {"kind": "link", "link_id": link_ids[m["start"]]}
            else:
                bid, bstart = block_for(m["start"])
                block_text = next(str(b.get("text", "")) for b in blocks if b["id"] == bid) if bid else ""
                if m["quote"] not in block_text:
                    complete = False
                    continue
                evidence = {"kind": "text", "block_id": bid, "quote": m["quote"]}
            first = not any(o["category"] == CONTRACT_CATEGORY[f["category"]] for o in out)
            out.append({"id": f"f{len(out) + 1}", "category": CONTRACT_CATEGORY[f["category"]], "evidence": evidence,
                        "tag": flag_tag(f["category"], m["quote"]),
                        "explanation": f["why"], "next_action": actions[0], "points": f["points"] if first else 0})
    raw_score, total, level, weighted = score(findings, em)
    for f in findings:
        f["n"] = findings.index(f) + 1
    stages = build_stages(findings)
    by_cat = {}
    for o in out:
        by_cat.setdefault(o["category"], []).append(o)
    for st in stages:
        for fl in st["flags"]:
            ids = [o["id"] for o in by_cat.get(CONTRACT_CATEGORY[fl["category"]], [])
                   if (o["evidence"]["kind"] == "metadata") == (st["stage"] == "subject")]
            fl["finding_ids"] = ids
            fl["category"] = CONTRACT_CATEGORY[fl["category"]]
    assessment = "insufficient_evidence" if not complete else ("needs_verification" if findings else "no_obvious_indicators")
    limitations = ["Displayed sender details do not establish sender authenticity."]
    if not em["auth_results"]:
        limitations.append("No Authentication-Results provided; SPF/DKIM/DMARC were not evaluated.")
    return {
        "analysis_id": "analysis-" + format(abs(hash((em["from_addr"], em["subject"], body))) % 10**10, "010d"),
        "email_id": req.get("email_id"), "assessment": assessment, "analysis_complete": complete,
        "risk_score": total, "risk_level": level, "payroll_weighted": weighted,
        "scam_type": scam_type(findings, em), "findings": out, "recommended_actions": actions,
        "verdict": verdict(findings, total), "callback": callback_contact(findings, em),
        "hold_scenario": hold_scenario(findings, em), "stages": stages,
        "limitations": limitations,
    }


# ---------------------------------------------------------------- v2: pre-payment decision support

VERDICTS = {
    "pay": "OK to proceed",
    "verify": "Call back first",
    "stop": "Don't pay — report it",
}


def verdict(findings, total):
    """The question she actually has: can I pay? Score only decides which of three answers."""
    cats = {f["category"] for f in findings}
    if total >= 70:
        key = "stop"
    elif total >= 30 or "payment" in cats:
        key = "verify"
    else:
        key = "pay"
    return {"key": key, "label": VERDICTS[key]}


def callback_contact(findings, em):
    for f in findings:
        if f.get("executive"):
            p = f["executive"]
            return {"name": p["name"], "role": p["title"], "phone": p["phone"], "email": p.get("email", ""),
                    "source": "company directory"}
    for f in findings:
        ent = f.get("impersonates")
        if ent and ent.get("phone"):
            return {"name": ent["name"], "role": "vendor", "phone": ent["phone"], "email": ent.get("email", ""),
                    "source": "vendor master file"}
    ent = trusted_entity_for(em["from_domain"]) if em["from_domain"] else None
    if ent and ent.get("phone"):
        return {"name": ent["name"], "role": "vendor", "phone": ent["phone"], "email": ent.get("email", ""),
                "source": "vendor master file"}
    return None


def hold_scenario(findings, em):
    text = (em["subject"] + " " + em["body"]).lower()
    pay = next((f for f in findings if f["category"] == "payment"), None)
    if not findings or (pay and not pay["money"]):
        return None
    if re.search(r"\bw-?2s?\b|social security|ssn|employee (?:list|records|data)", text):
        return "employee_data"
    if re.search(r"bank|routing|account number|direct deposit|remittance|iban", text):
        return "bank_change"
    if re.search(r"password|sign in|credential", text):
        return None
    return "urgent_payment"


def drill_category(findings, em):
    cats = {f["category"] for f in findings}
    text = (em["subject"] + " " + em["body"]).lower()
    pay = next((f for f in findings if f["category"] == "payment"), None)
    if not findings:
        return "legit"
    if pay and not pay["money"]:
        return "credential"
    if re.search(r"\bw-?2s?\b|social security|employee list", text):
        return "data_request"
    if re.search(r"direct deposit|salary", text):
        return "payroll"
    if "exec" in cats:
        return "ceo_fraud"
    if re.search(r"bank|routing|remittance", text):
        return "bank_change"
    if re.search(r"password|sign in", text):
        return "credential"
    if "attachment" in cats:
        return "attachment"
    return "fake_invoice"


RADAR_FLAG = {"lookalike": "lookalike_domain", "reply_to": "reply_to_mismatch", "exec": "exec_impersonation",
              "links": "link_mismatch", "attachment": "risky_attachment", "urgency": "urgency"}


def _fnv1a64(text):
    h = 0xCBF29CE484222325
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x100000001B3) & ((1 << 64) - 1)
    return h


def _simhash64(text):
    words = text.split()
    feats = words + [words[i] + " " + words[i + 1] for i in range(len(words) - 1)]
    vec = [0] * 64
    for f in feats:
        h = _fnv1a64(f)
        for bit in range(64):
            vec[bit] += 1 if (h >> bit) & 1 else -1
    return format(sum(1 << bit for bit in range(64) if vec[bit] > 0), "016x")


def _normalize_subject(subject):
    s = (subject or "").lower()
    s = re.sub(r"^(\s*(re|fw|fwd)\s*:\s*)+", "", s)
    s = re.sub(r"[0-9]+", "#", s)
    return " ".join(re.sub(r"[^a-z#]+", " ", s).split())


def fingerprint(em, findings, total):
    """Phish Radar report fingerprint (same keys/hash as builds/3_phish_radar): no body text, no recipients."""
    import hashlib
    text = (em["subject"] + " " + em["body"]).lower()
    flags = {RADAR_FLAG[f["category"]] for f in findings if f["category"] in RADAR_FLAG}
    if any(f["category"] == "payment" for f in findings):
        if re.search(r"\bw-?2s?\b|social security|ssn|employee", text):
            flags.add("employee_data")
        elif re.search(r"gift ?card", text):
            flags.add("gift_card")
        elif re.search(r"password|sign in|credential", text):
            flags.add("credential_request")
        else:
            flags.add("payment_change")
    look = next((f.get("impersonates") for f in findings if f["category"] == "lookalike"), None)
    norm = _normalize_subject(em["subject"])
    return {
        "v": 1,
        "sender_domain": em["from_domain"],
        "display_name": em["from_name"],
        "reply_to_domain": em["reply_to_domain"] or None,
        "subject_simhash": _simhash64(norm),
        "subject_template": hashlib.sha256(norm.encode()).hexdigest()[:16],
        "link_domains": sorted({(urlsplit(l["href"]).hostname or "").lower() for l in em["links"]} - {""}),
        "attachment_hashes": [],
        "attachment_types": sorted(re.findall(r"\.[a-z0-9]{1,5}$", a["name"].lower())[0] if re.search(r"\.[a-z0-9]{1,5}$", a["name"].lower()) else "" for a in em["attachments"]),
        "flags": sorted(flags),
        "lookalike_of": (look["domains"][0] if look else None),
        "client_score": total,
    }


# ---------------------------------------------------------------- v3.1: two-stage scan (subject line, then body)

SUBJECT_STAGE = {"lookalike", "reply_to", "auth", "exec"}
TAGS = {"lookalike": "look-alike domain", "reply_to": "Reply-To mismatch", "auth": "SPF/DMARC fail",
        "exec": "impersonation", "links": "link ≠ text", "attachment": "risky attachment"}


def _payment_tag(quote):
    q = quote.lower()
    for pat, tag in ((r"w-?2|social security|ssn|employee", "employee data"), (r"gift", "gift cards"),
                     (r"password|sign in|credential|login", "credentials"), (r"wire", "wire"),
                     (r"direct deposit", "direct deposit"), (r"approval|verification|call-?back", "skip approval")):
        if re.search(pat, q):
            return tag
    return "bank change"


def flag_tag(category, quote):
    if category == "urgency":
        return quote.lower()
    if category == "payment":
        return _payment_tag(quote)
    return TAGS.get(category, category)


def _is_header(mark):
    return mark["kind"] == "header"


def _stage_split(findings):
    """Assign each finding's points to the subject stage (sender line + subject) or the body stage."""
    subject, body = [], []
    urgency_left = POINTS["urgency_cap"]
    for f in findings:
        head = [m for m in f["marks"] if _is_header(m)]
        rest = [m for m in f["marks"] if not _is_header(m)]
        if f["category"] == "urgency":
            ps = min(POINTS["urgency_each"] * len(head), urgency_left)
            pb = min(POINTS["urgency_each"] * len(rest), urgency_left - ps)
        elif f["category"] in SUBJECT_STAGE:
            ps, pb = f["points"], 0
        elif rest:
            ps, pb = 0, f["points"]
        else:
            ps, pb = f["points"], 0
        if head:
            subject.append((f, head, ps))
        if rest:
            body.append((f, rest, pb))
    return subject, body


def _stage_flags(items):
    return [{"n": f["n"], "category": f["category"], "points": pts,
             "tags": list(dict.fromkeys(flag_tag(f["category"], m["quote"]) for m in marks))}
            for f, marks, pts in items]


def analyze_subject(em):
    """Stage 1: red flags visible on the subject line and the sender line (From, Reply-To, auth results)."""
    findings = [f for f in (d(em) for d in DETECTORS) if f]
    for i, f in enumerate(findings, 1):
        f["n"] = i
    return _stage_flags(_stage_split(findings)[0])


def analyze_body(em):
    """Stage 2: red flags in the message body, links and attachments."""
    findings = [f for f in (d(em) for d in DETECTORS) if f]
    for i, f in enumerate(findings, 1):
        f["n"] = i
    return _stage_flags(_stage_split(findings)[1])


def build_stages(findings):
    subject, body = _stage_split(findings)
    out = []
    for name, items in (("subject", subject), ("body", body)):
        flags = _stage_flags(items)
        out.append({"stage": name, "score": sum(fl["points"] for fl in flags), "flags": flags})
    return out
