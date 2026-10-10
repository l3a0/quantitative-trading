"""The book notes' counts, held by the suite rather than by their own prose.

A note is quoted material, so nothing edits it by hand. The prose sweeps read
it, but none of them counts anything. That leaves one failure with nothing
watching for it: a re-extraction that silently returns fewer highlights than
the last one. The file would still read correctly, its header would still claim
a number, and the count in ``research/book-notes/README.md`` would still say
what it always said.

So the counts are asserted three ways here: the entries actually in the file,
the counts the file's own header claims, and the total the README's table
quotes. Each is written by a different hand, and a re-extraction that truncates
moves the first one only.

Both of the header's numbers are held, the total and how many were recovered.
The recovered ones came from the Cloud Reader rather than from Amazon's export,
so they are the entries a re-extraction is most likely to come back without,
and a note could keep its total while losing them.
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
    "algorithmic-trading.md": 301,
    "quantitative-trading.md": 235,
}

# How many of those were cut off by Amazon's export limit and recovered from
# the Cloud Reader. A truncated re-extraction could hold its total and lose
# these, since a recovered highlight is the fragile kind.
EXPECTED_RECOVERED = {
    "algorithmic-trading.md": 223,
    "quantitative-trading.md": 57,
}

ENTRY = re.compile(r"^### Location ", re.MULTILINE)
RECOVERED_ENTRY = re.compile(r"^### Location .*↻ recovered", re.MULTILINE)
HEADER_COUNT = re.compile(r"^(\d+) highlights\b", re.MULTILINE)
# The header can count its recovered entries in two clauses. The Algorithmic
# Trading note says 83 "were cut off" and 140 more were "hidden entirely", and
# all 223 carry the tag, so reading the first clause alone would hold 83.
HEADER_RECOVERED = re.compile(
    r"^\d+ highlights\b.*?(\d+) of these were cut off(?:[^.]*?\band (\d+) hidden entirely)?",
    re.MULTILINE,
)


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


@pytest.mark.parametrize("name", sorted(EXPECTED_RECOVERED))
def test_the_note_holds_the_recovered_highlights_it_claims(name: str) -> None:
    """The recovered entries and the count the header claims agree.

    A recovered highlight is the one Amazon's export never handed over, so it
    is the piece a re-extraction is most likely to come back without. The total
    alone would not notice: a note can hold 235 entries with fewer of them
    recovered than before.
    """
    text = (NOTES_DIR / name).read_text(encoding="utf-8")
    header = HEADER_RECOVERED.search(text)
    assert header is not None, f"{name} has no 'N of these were cut off' claim"
    claimed = int(header.group(1)) + int(header.group(2) or 0)
    assert len(RECOVERED_ENTRY.findall(text)) == EXPECTED_RECOVERED[name]
    assert claimed == EXPECTED_RECOVERED[name]


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
    assert present == set(EXPECTED_RECOVERED)


def test_the_bibliography_section_survives_a_re_extraction() -> None:
    """The Algorithmic Trading note's bibliography section is added by hand.

    A re-extraction rebuilds only the highlights, so it would drop the section
    without changing any count above. The AUD.CAD post's reference to Dueker
    and Neely cites this entry, which is why its absence fails here.
    """
    text = (NOTES_DIR / "algorithmic-trading.md").read_text(encoding="utf-8")
    _, found, section = text.partition("\n## Bibliography\n")
    assert found, "algorithmic-trading.md has lost its ## Bibliography section"
    assert "### Page 192 · bibliography" in section
    assert (
        "Dueker, Michael J., and Christopher J. Neely. “Can Markov Switching Models"
        " Predict Excess Foreign Exchange Returns?” Federal Reserve Bank of St. Louis"
        " Working Paper 2001-021F, 2001." in section
    )
    assert not re.search(r"^### Location ", section, re.MULTILINE)
