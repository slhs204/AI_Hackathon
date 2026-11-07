import pytest
from pydantic import ValidationError

from app.evidence import find_exact, verify
from app.schemas import Evidence


def text_ev(block_id, quote):
    return Evidence(kind="text", block_id=block_id, quote=quote)


def test_exact_quote_is_verified(email_factory):
    ev = verify(email_factory(), text_ev("b1", "change my salary account today"))
    assert ev is not None and ev.quote == "change my salary account today"


def test_case_and_whitespace_differences_return_original_text(email_factory):
    email = email_factory(blocks=[{"id": "b1", "text": "Please  Change my\nSalary account today."}])
    ev = verify(email, text_ev("b1", "change my salary account"))
    assert ev is not None and ev.quote == "Change my\nSalary account"


def test_curly_quotes_match_straight_quotes():
    assert find_exact("Don’t call me", "Don't call me") == "Don’t call me"


def test_invented_quote_is_rejected(email_factory):
    assert verify(email_factory(), text_ev("b1", "send your password")) is None


def test_quote_in_wrong_block_is_rejected(email_factory):
    email = email_factory(blocks=[{"id": "b1", "text": "Hello"}, {"id": "b2", "text": "Change my salary account."}])
    assert verify(email, text_ev("b1", "salary account")) is None
    assert verify(email, text_ev("b2", "salary account")) is not None


def test_unknown_block_is_rejected(email_factory):
    assert verify(email_factory(), text_ev("b9", "salary")) is None


def test_link_evidence_needs_a_real_link(email_factory):
    email = email_factory(links=[{"id": "l1", "block_id": "b1", "display_text": "portal", "href": "https://x.test"}])
    assert verify(email, Evidence(kind="link", link_id="l1")) is not None
    assert verify(email, Evidence(kind="link", link_id="l2")) is None


def test_metadata_evidence(email_factory):
    email = email_factory(reply_to="pay@evil.example")
    assert verify(email, Evidence(kind="metadata", field="sender.address", value="acme-corp.com")) is not None
    assert verify(email, Evidence(kind="metadata", field="subject", value="account UPDATE")).value == "Account update"
    assert verify(email, Evidence(kind="metadata", field="reply_to", value="evil.example")) is not None
    assert verify(email, Evidence(kind="metadata", field="reply_to", value="other.example")) is None
    assert verify(email, Evidence(kind="metadata", field="body", value="x")) is None


def test_evidence_shape_is_enforced():
    with pytest.raises(ValidationError):
        Evidence(kind="text", block_id="b1")
    with pytest.raises(ValidationError):
        Evidence(kind="link")
    with pytest.raises(ValidationError):
        Evidence(kind="metadata", field="subject")
