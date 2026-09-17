"""The book notes' counts, held by the suite rather than by their own prose.

A note is quoted material, so nothing edits it by hand and the prose sweeps
skip it. That leaves one failure with nothing watching for it: a re-extraction
that silently returns fewer highlights than the last one. The file would still
read correctly, its header would still claim a number, and the count in
``research/book-notes/README.md`` would still say what it always said.

So the count is asserted three ways here: the entries actually in the file, the
count the file's own header claims, and the count the README's table quotes.
Each of the three is written by a different hand, and a re-extraction that
truncates moves the first one only.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

NOTES_DIR = Path(__file__).resolve().parents[1] / "research" / "book-notes"

# The counts the README quotes. Pinning the literals is what makes this file
# the authority for them, rather than a consistency check that would pass just
# as happily if every surface drifted together.
EXPECTED_HIGHLIGHTS = {
    "quantitative-trading.md": 235,
}

ENTRY = re.compile(r"^### Location ", re.MULTILINE)
HEADER_COUNT = re.compile(r"^(\d+) highlights\b", re.MULTILINE)


@pytest.mark.parametrize("name", sorted(EXPECTED_HIGHLIGHTS))
def test_the_note_holds_the_highlights_it_claims(name: str) -> None:
    """The entries in the file, the count in its header, and the count in the
    README all agree."""
    text = (NOTES_DIR / name).read_text(encoding="utf-8")
    entries = len(ENTRY.findall(text))
    header = HEADER_COUNT.search(text)
    assert header is not None, f"{name} has no 'N highlights' line in its header"
    assert entries == EXPECTED_HIGHLIGHTS[name]
    assert int(header.group(1)) == EXPECTED_HIGHLIGHTS[name]


@pytest.mark.parametrize("name", sorted(EXPECTED_HIGHLIGHTS))
def test_the_readme_quotes_the_same_count(name: str) -> None:
    """The README's table is prose quoting a number, so it is checked against
    the same authority rather than trusted."""
    readme = (NOTES_DIR / "README.md").read_text(encoding="utf-8")
    row = next(line for line in readme.splitlines() if f"]({name})" in line)
    cells = [cell.strip() for cell in row.strip("|").split("|")]
    assert int(cells[-1]) == EXPECTED_HIGHLIGHTS[name]


def test_every_note_is_covered() -> None:
    """A note added without a count here would otherwise be unwatched."""
    present = {path.name for path in NOTES_DIR.glob("*.md")} - {"README.md"}
    assert present == set(EXPECTED_HIGHLIGHTS)
