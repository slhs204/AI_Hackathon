"""Convert the Teddyha dataset rows into /analyze request fixtures (fixtures/blind/).

The body becomes block b1, like Hookline sends it. URLs written in the body
become links whose shown text equals the URL (that's how plain-text links look
in Gmail). The sender has only an address in this dataset.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "external" / "teddyha"
OUT = HERE / "blind"
URL = re.compile(r"https?://[^\s<>\"')\]]+")


def main() -> None:
    rows = [r["row"] for f in ("rows_0.json", "rows_100.json") for r in json.loads((SRC / f).read_text())["rows"]]
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for row in rows:
        body = row["body"] or ""
        links = [{"id": f"l{i}", "block_id": "b1", "display_text": u.rstrip(".,;:"), "href": u.rstrip(".,;:")}
                 for i, u in enumerate(URL.findall(body), 1)]
        case = {
            "source": f"teddyha:{row['id']}",
            "title": row["subject"],
            "meta": {k: row[k] for k in ("intent", "technique", "target")},
            "request": {
                "email_id": row["id"],
                "sender": {"name": "", "address": row["spoofed_sender"] or ""},
                "subject": row["subject"] or "",
                "blocks": [{"id": "b1", "text": body}],
                "links": links,
            },
            "expected": {"label": "phishing" if row["label"] == "phishing" else "legit", "must_flag": []},
        }
        (OUT / f"{row['id']}.json").write_text(json.dumps(case, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} fixtures to {OUT}")


if __name__ == "__main__":
    main()
