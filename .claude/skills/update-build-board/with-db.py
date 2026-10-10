"""Splice the board's live database documents into a copy of its page.

The page draws from its database, and the verification harness runs the page's
script with no database at all. The page carries no copy of the board, its
FALLBACK line reading `{ none: true }`, so on its own the harness would see
only the banner. This writes a scratch copy of the page whose FALLBACK is the
documents just read, so the harness checks the data a viewer is about to see.

Usage, from the scratch directory:

    python3 with-db.py qt-board.html readback/board > qt-board-live.html

`readback/board` is the directory an `ArtifactData` list of the `board`
collection with `out_dir` set to `readback` writes, one JSON file per section.
The output is for the harness only. A publish sends the page with FALLBACK left
as `{ none: true }`, because a copy carried by the published page goes stale
with nothing to refresh it.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SECTIONS = ("state", "prs", "working", "planned", "next", "tracker")


def strip_meta(doc: dict) -> dict:
    """Drop the fields the database adds, which the page never reads."""
    return {k: v for k, v in doc.items() if not k.startswith("__")}


def main() -> None:
    page_path, docs_dir = Path(sys.argv[1]), Path(sys.argv[2])
    page = page_path.read_text(encoding="utf-8")
    fallback = {}
    for name in SECTIONS:
        doc = strip_meta(json.loads((docs_dir / f"{name}.json").read_text(encoding="utf-8")))
        if doc.get("schema") != 1:
            sys.exit(f"{name}: schema {doc.get('schema')!r}, expected 1")
        fallback[name] = doc if name == "state" else doc["items"]
    # A "</script>" inside any string would end the page's script early, so
    # every "<" is written as its JSON escape, which parses to the same text.
    body = json.dumps(fallback, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    line = f"const FALLBACK = {body};"
    new, count = re.subn(r"^const FALLBACK = .*;$", lambda _: line, page, flags=re.MULTILINE)
    if count != 1:
        sys.exit(f"expected one FALLBACK line in {page_path}, found {count}")
    sys.stdout.write(new)


if __name__ == "__main__":
    main()
