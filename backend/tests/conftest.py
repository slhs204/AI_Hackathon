import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import AnalyzeRequest  # noqa: E402


def make_request(**overrides) -> AnalyzeRequest:
    data = {
        "email_id": "t-001",
        "sender": {"name": "Payroll Support", "address": "support@acme-corp.com"},
        "subject": "Account update",
        "blocks": [{"id": "b1", "text": "Please change my salary account today."}],
        "links": [],
    }
    data.update(overrides)
    return AnalyzeRequest.model_validate(data)


@pytest.fixture
def email_factory():
    return make_request
