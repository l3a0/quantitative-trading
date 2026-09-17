"""Two prose sweeps for Markdown that markdownlint has no rule for.

Both slips reach a rendered page with every linter clean.

A tilde meaning "approximately" can close a strikethrough pair. Markdown reads
a matching pair of tildes as deleted text, and renderers disagree about when a
tilde is allowed to close one. A tilde glued to punctuation closes on a
notebook-style renderer and not on GitHub, so `(~30` can strike out everything
back to an earlier `~90%` on one surface while reading fine on the other.
Writing the escaped form `\\~` renders as a literal tilde everywhere.

A table delimiter row written `|---|` mixes padding styles against the padded
rows around it, which is what markdownlint's MD060 flags. The tight form is
the one muscle memory produces, and MD060 only fires when the rest of the
table is padded, so it slips through a table that is tight throughout.

Both checks read prose only. Text inside a fenced block or a backtick span is
exempt, because a pattern written for prose keeps appearing inside the code
fence that documents it. Blanking keeps line numbers intact, so a finding
points at the line a reader will open.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

# A tilde that could CLOSE a strikethrough pair. One after whitespace can only
# open a pair, so it is left alone. One after a backslash is already escaped.
# One after `<` belongs to an HTML comment or tag.
CLOSE_CAPABLE_TILDE = re.compile(r"(?<![\s~\\<])~")

# A delimiter row whose dashes touch the pipes on both sides.
TIGHT_DELIMITER_ROW = re.compile(r"\|-{1,}\|")

# An opening or closing fence: up to three spaces of indent, then a run of at
# least three backticks or tildes, then an optional info string.
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


@dataclass(frozen=True)
class Finding:
    """One flagged line, named so a reader can open it."""

    path: Path
    line_number: int
    line: str
    rule: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line_number}: {self.rule}: {self.line.strip()}"


def blank_code(text: str) -> str:
    """Replace every code region with spaces, keeping the line structure.

    A blanked line keeps its length and its position, so a match found in the
    result points at the same column of the same line in the source.
    """
    blanked: list[str] = []
    fence: str | None = None
    for line in text.split("\n"):
        match = _FENCE.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
                blanked.append(" " * len(line))
                continue
            blanked.append(_blank_spans(line))
            continue
        blanked.append(" " * len(line))
        closes = (
            match is not None
            and match.group(1)[0] == fence[0]
            and len(match.group(1)) >= len(fence)
            and not match.group(2).strip()
        )
        if closes:
            fence = None
    return "\n".join(blanked)


def _blank_spans(line: str) -> str:
    """Blank every backtick span in one line of prose."""
    characters = list(line)
    length = len(characters)
    index = 0
    while index < length:
        if characters[index] != "`":
            index += 1
            continue
        run = _run_length(characters, index)
        close = _find_closing_run(characters, index + run, run)
        if close is None:
            # An unmatched run is literal text, so step past it and keep going.
            index += run
            continue
        for position in range(index, close + run):
            characters[position] = " "
        index = close + run
    return "".join(characters)


def _run_length(characters: list[str], start: int) -> int:
    run = 0
    while start + run < len(characters) and characters[start + run] == "`":
        run += 1
    return run


def _find_closing_run(characters: list[str], start: int, run: int) -> int | None:
    """Find a run of exactly `run` backticks, which is what closes a span."""
    index = start
    while index < len(characters):
        if characters[index] != "`":
            index += 1
            continue
        found = _run_length(characters, index)
        if found == run:
            return index
        index += found
    return None


def sweep_text(text: str, path: Path) -> list[Finding]:
    """Flag every close-capable tilde and tight delimiter row in one document."""
    findings: list[Finding] = []
    prose = blank_code(text).split("\n")
    source = text.split("\n")
    for number, (prose_line, source_line) in enumerate(zip(prose, source, strict=True), start=1):
        if CLOSE_CAPABLE_TILDE.search(prose_line):
            findings.append(Finding(path, number, source_line, "unescaped tilde, write it as \\~"))
        if TIGHT_DELIMITER_ROW.search(prose_line):
            findings.append(
                Finding(path, number, source_line, "tight table delimiter row, pad it as | --- |")
            )
    return findings


def markdown_files(root: Path) -> list[Path]:
    """Every Markdown file the repository owns, in a stable order.

    Asking git rather than walking the tree keeps ignored files out. A cache
    directory that ships a README is not this repo's prose, and sweeping it
    fails the suite for something the repo cannot fix. It also keeps the file
    set identical on a fresh checkout and on a working tree that has been
    built in, so a local run and a CI run collect the same tests.

    Untracked files count as long as they are not ignored. A doc written but
    not yet added is exactly the file a sweep needs to reach, and leaving it
    out is how a suite passes locally and fails in CI on the same commit.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "--",
            "*.md",
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"git ls-files failed in {root}: {message}")
    names = result.stdout.decode("utf-8").split("\0")
    # A path in the index but not on disk is a deletion that has not been
    # staged yet. Sweeping it raises FileNotFoundError from the read, which
    # reports a pending deletion as a prose failure.
    paths = (root / name for name in names if name)
    return sorted(path for path in paths if path.is_file())


def sweep_file(path: Path) -> list[Finding]:
    return sweep_text(path.read_text(encoding="utf-8"), path)
