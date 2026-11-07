"""Request and response shapes for the extension.

Accepts BOTH extension formats in use on the team:
  - Albert's prototype:  links = {id, block_id, display_text, href}
  - Jenessa's Hookline:  links = {id, text, url}, whole body in one block "b1"
Responses follow Albert's `engine.analyze_contract` and add the fields
Hookline reads (title, evidence.quote on every finding, disclaimer).
Limits exist so one request cannot make the backend do unbounded work or spend.
"""

from typing import Any, Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

MAX_BLOCKS = 200
MAX_LINKS = 50
MAX_ATTACHMENTS = 20
MAX_BLOCK_CHARS = 20_000  # Hookline sends the whole body as one block
MAX_TOTAL_CHARS = 20_000
MAX_CONTEXT_CHARS = 1_000

# Categories produced by the rule engine (CONTRACT_CATEGORY) plus the ones
# this backend adds.
RULE_CATEGORIES = (
    "sender_impersonation",
    "reply_to_mismatch",
    "authentication_failure",
    "authority_impersonation",
    "deceptive_link",
    "risky_attachment",
    "urgency_pressure",
    "payment_or_data_request",
)
MODEL_CATEGORIES = RULE_CATEGORIES + ("manipulation_cue",)

METADATA_FIELDS = ("sender.name", "sender.address", "reply_to", "subject", "authentication_results", "attachments")


class _In(BaseModel):
    # Unknown fields are ignored, so an older or newer extension still works.
    model_config = ConfigDict(extra="ignore")


class Sender(_In):
    name: str = Field(default="", max_length=200)
    address: str = Field(default="", max_length=320)


class Block(_In):
    id: str = Field(min_length=1, max_length=40)
    text: str = Field(max_length=MAX_BLOCK_CHARS)


class Link(_In):
    id: str = Field(min_length=1, max_length=40)
    block_id: Optional[str] = Field(default=None, max_length=40)
    display_text: str = Field(default="", max_length=500)
    href: str = Field(default="", max_length=2_000)

    @model_validator(mode="before")
    @classmethod
    def _hookline_names(cls, data: Any) -> Any:
        # Hookline sends {id, text, url}.
        if isinstance(data, dict):
            data = dict(data)
            if "display_text" not in data and "text" in data:
                data["display_text"] = data.pop("text")
            if "href" not in data and "url" in data:
                data["href"] = data.pop("url")
        return data


class Attachment(_In):
    name: str = Field(max_length=255)


class AnalyzeRequest(_In):
    email_id: Optional[str] = Field(default=None, max_length=200)
    sender: Sender = Field(default_factory=Sender)
    subject: str = Field(default="", max_length=500)
    blocks: list[Block] = Field(max_length=MAX_BLOCKS)
    links: list[Link] = Field(default_factory=list, max_length=MAX_LINKS)
    reply_to: str = Field(default="", max_length=320)
    authentication_results: str = Field(default="", max_length=2_000)
    attachments: list[Attachment] = Field(default_factory=list, max_length=MAX_ATTACHMENTS)

    @model_validator(mode="after")
    def _check_ids_and_size(self) -> "AnalyzeRequest":
        block_ids = [b.id for b in self.blocks]
        if len(set(block_ids)) != len(block_ids):
            raise ValueError("block ids must be unique")
        link_ids = [link.id for link in self.links]
        if len(set(link_ids)) != len(link_ids):
            raise ValueError("link ids must be unique")
        total = len(self.subject) + sum(len(b.text) for b in self.blocks)
        if total > MAX_TOTAL_CHARS:
            raise ValueError(f"email text is longer than {MAX_TOTAL_CHARS} characters")
        # Hookline doesn't say which block a link is in: use the first block
        # whose text contains the link text.
        for link in self.links:
            if link.block_id is None and link.display_text:
                link.block_id = next((b.id for b in self.blocks if link.display_text in b.text), None)
        return self

    def block(self, block_id: Optional[str]) -> Optional[Block]:
        return next((b for b in self.blocks if b.id == block_id), None)

    def link(self, link_id: Optional[str]) -> Optional[Link]:
        return next((link for link in self.links if link.id == link_id), None)


class Evidence(BaseModel):
    """kind=text: block_id + quote. kind=link: link_id. kind=metadata: field + value."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["text", "link", "metadata"]
    block_id: Optional[str] = None
    quote: Optional[str] = Field(default=None, max_length=500)
    link_id: Optional[str] = None
    field: Optional[str] = None
    value: Optional[str] = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _shape(self) -> "Evidence":
        if self.kind == "text" and not (self.block_id and self.quote):
            raise ValueError("text evidence needs block_id and quote")
        if self.kind == "link" and not self.link_id:
            raise ValueError("link evidence needs link_id")
        if self.kind == "metadata" and not (self.field and self.value):
            raise ValueError("metadata evidence needs field and value")
        return self


class Finding(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    category: str
    evidence: Evidence
    explanation: str = Field(max_length=800)
    next_action: str = Field(max_length=800)
    points: int = 0
    tag: Optional[str] = None  # short chip text from engine v3.1, e.g. "bank change"
    ai_explanation: Optional[str] = None  # model's plain-English rewording (Albert v3 field)
    # added
    title: str = ""
    source: Literal["rules", "tool", "model"] = "rules"
    evidence_verified: bool = True
    policy_id: Optional[str] = None


class Policy(BaseModel):
    id: str
    title: str
    steps: list[str]


class PracticeQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    category: str
    answer: str
    from_name: str
    from_addr: str
    subject: str
    body: str
    lesson: str


class AnalyzeResponse(BaseModel):
    analysis_id: str
    email_id: Optional[str]
    assessment: Literal["insufficient_evidence", "needs_verification", "no_obvious_indicators"]
    analysis_complete: bool
    risk_score: int
    risk_level: str
    payroll_weighted: bool
    scam_type: str
    findings: list[Finding]
    recommended_actions: list[str]
    limitations: list[str]
    # engine v3.1 fields read by Albert's v3 extension / Outlook pane
    verdict: Optional[dict[str, str]] = None  # {"key": pay|verify|stop, "label": ...}
    callback: Optional[dict[str, str]] = None  # who to call, from the directory, never from the email
    hold_scenario: Optional[str] = None
    stages: list[dict[str, Any]] = Field(default_factory=list)  # [{stage: subject|body, score, flags}]
    ai_summary: Optional[str] = None
    # added
    summary: str = ""
    disclaimer: str = "No warning signs found does not mean the email is safe."
    policies: list[Policy] = Field(default_factory=list)
    practice: Optional[PracticeQuestion] = None
    model: str
    elapsed_ms: int


class ChallengeRequest(_In):
    """Either the whole finding (Albert-style) or just its id (Hookline sends
    {email, finding_id, context}); with only an id the backend finds it again."""

    email: AnalyzeRequest
    finding: Optional[Finding] = None
    finding_id: Optional[str] = Field(default=None, max_length=40)
    user_context: str = Field(min_length=1, max_length=MAX_CONTEXT_CHARS,
                              validation_alias=AliasChoices("user_context", "context"))

    @model_validator(mode="after")
    def _needs_finding(self) -> "ChallengeRequest":
        if self.finding is None and not self.finding_id:
            raise ValueError("send finding or finding_id")
        return self


class ChallengeResponse(BaseModel):
    finding_id: str
    # A challenge can lower concern but never clears a finding by itself.
    assessment: Literal["still_concerning", "less_concerning"]
    message: str
    still_unresolved: str
    next_action: str
    explanation: str  # message + still_unresolved, the one text Hookline shows
    model: str


# ------------------------------------------------------------------ /triage

MAX_TRIAGE_EMAILS = 50
MAX_SNIPPET_CHARS = 500


class TriageEmail(_In):
    email_id: str = Field(min_length=1, max_length=200)
    sender: Sender = Field(default_factory=Sender)
    subject: str = Field(default="", max_length=500)
    snippet: str = Field(default="", max_length=MAX_SNIPPET_CHARS)  # the preview line, not the whole body


class TriageRequest(_In):
    emails: list[TriageEmail] = Field(min_length=1, max_length=MAX_TRIAGE_EMAILS)

    @model_validator(mode="after")
    def _unique_ids(self) -> "TriageRequest":
        ids = [e.email_id for e in self.emails]
        if len(set(ids)) != len(ids):
            raise ValueError("email ids must be unique")
        return self


class TriageItem(BaseModel):
    email_id: str
    priority: Literal["high", "medium", "low"]
    reason: str
    rule_score: int
    tags: list[str]
    source: Literal["rules", "model"]  # who set the final priority


class TriageResponse(BaseModel):
    items: list[TriageItem]  # same order as the request
    model: str
    elapsed_ms: int
    notice: str = ("Triage only looks at the sender, subject and preview. Open an email and run the full "
                   "check before acting. Low priority does not mean safe.")
