"""The prose sweeps for Markdown that markdownlint has no rule for.

Four checks live here. Two read one document's own characters, and two read a
reference in one document against a heading in another.

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

A heading quoted in prose stops resolving when the heading is renamed. Nothing
else here sees it, because a quoted heading is not a link, and no linter reads
one document's prose against another document's headings. The reference reads
as an instruction to open a section that is not there.

A fragment link stops resolving the same way, and renders as a working link
while doing it. GitHub answers an anchor nobody kept by leaving the reader at
the top of the page.

Both single-document checks read prose only. Text inside a fenced block or a
backtick span is exempt, because a pattern written for prose keeps appearing
inside the code fence that documents it. Blanking keeps line numbers intact,
so a finding points at the line a reader will open. Both cross-document checks
blank fenced blocks and keep inline spans, because the reference they read is
normally written in backticks.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Collection, Iterable
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

    This blanks inline spans as well as fenced blocks, which is right for the
    sweeps that consume it: a tilde or a tight delimiter row inside backticks
    is code rather than prose. A caller that wants the opposite, meaning prose
    including its inline code, wants :func:`blank_fences`.
    """
    return "\n".join(_blank_spans(line) for line in blank_fences(text).split("\n"))


def blank_fences(text: str) -> str:
    """Blank fenced code blocks only, leaving inline spans alone.

    Separate from :func:`blank_code` because a reference written in prose is
    normally written in backticks. A check for one has to see inside them,
    while a fenced block showing a command is not a prose reference at all.
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
            blanked.append(line)
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


# --- References from one document to a heading in another ---------------------
#
# Both checks below ask one question: does the heading this prose names still
# exist. They differ in how the prose names it. A quoted heading names the text
# and leaves the document to the sentence around it. A fragment link names the
# document and carries a slug rather than the text.


@dataclass(frozen=True)
class ReferenceFinding:
    """One reference that resolves to no heading, named so a reader can fix it.

    `suggestion` carries the nearest heading the attributed document does have,
    which is the answer when the failure is a rename. It is empty when nothing
    in that document shares a word with the missing text, because a suggestion
    with no overlap is a guess dressed as an answer.
    """

    path: Path
    line_number: int
    reference: str
    problem: str
    suggestion: str = ""

    def __str__(self) -> str:
        message = f"{self.path}:{self.line_number}: `{self.reference}` {self.problem}"
        if self.suggestion:
            message += f", nearest present is `{self.suggestion}`"
        return message


@dataclass(frozen=True)
class Heading:
    """One ATX heading, with the anchor GitHub gives it."""

    level: int
    text: str
    line_number: int
    slug: str

    @property
    def span(self) -> str:
        """The heading as prose quotes it, hashes and all."""
        return f"{'#' * self.level} {self.text}"


@dataclass(frozen=True)
class Unit:
    """One stretch of prose the attribution scan reads as a whole."""

    text: str
    first_line: int

    def line_of(self, offset: int) -> int:
        """The source line an offset into this unit sits on."""
        return self.first_line + self.text.count("\n", 0, offset)


@dataclass(frozen=True)
class Attribution:
    """Which document a sentence hands a quoted heading to.

    Three outcomes, and the middle one is why this is a class rather than an
    optional path. A sentence naming a document this repo does not keep is the
    trace a retired file leaves behind, and skipping it would make the sweep
    quiet about exactly the deletion it exists to notice.
    """

    written: str
    target: Path | None
    path_shaped: bool


@dataclass(frozen=True)
class QuotedHeading:
    """One heading quoted in prose, and the document the sentence hands it to."""

    path: Path
    line_number: int
    written: str
    attributed: Attribution


@dataclass(frozen=True)
class FragmentLink:
    """One link carrying an anchor. `document` is empty when the target is gone."""

    path: Path
    line_number: int
    target: str
    document: Path | None
    fragment: str


# A heading quoted in prose. The text may wrap in a hard-wrapped file, so the
# span is read across the unit rather than within one line and its whitespace
# is collapsed afterwards.
HEADING_SPAN = re.compile(r"`(#{1,6}[ \t][^`]+?)`")

# A positional word, accepted only where it follows the span. Accepting one
# anywhere in the unit fails correct prose: a paragraph can end "the rules
# above" with five unrelated spans in front of it.
POSITIONAL = re.compile(r"[ \t\n]*\b(above|below)\b")

_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_BACKTICKED_DOCUMENT = re.compile(r"`([^`\s]+\.md)`")
_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_TABLE_ROW = re.compile(r"^[ \t]*\|")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# A document this repo's prose names by a phrase rather than by its path. The
# table costs one entry and buys the reference whose target has actually moved
# before now. Skipping what carries no path would drop it.
DOCUMENT_ALIASES = {"the design doc": "docs/design.md"}

_ALIAS = re.compile("|".join(re.escape(alias) for alias in DOCUMENT_ALIASES), re.IGNORECASE)


def units(text: str) -> list[Unit]:
    """Split a document into the stretches the attribution scan reads.

    A line is the wrong unit because this repo wraps two ways. Six of its ten
    Markdown files are hard-wrapped near eighty columns and four are authored
    one paragraph per line, so in a hard-wrapped file an attribution and the
    span it governs share a line only by luck. Re-wrapping a paragraph would
    then silence a reference with nothing announcing it.

    The blank-line paragraph is the wrong unit too. A table is one paragraph,
    and a register table's rows each carry their own links and their own
    spans, so reading the table whole hands every row's attribution to every
    other row's span.

    So a table row is its own unit, and outside a table the unit is the
    blank-line paragraph.
    """
    found: list[Unit] = []
    buffer: list[str] = []
    first = 0
    for number, line in enumerate(text.split("\n"), start=1):
        if not line.strip():
            if buffer:
                found.append(Unit("\n".join(buffer), first))
                buffer = []
            continue
        if _TABLE_ROW.match(line):
            if buffer:
                found.append(Unit("\n".join(buffer), first))
                buffer = []
            found.append(Unit(line, number))
            continue
        if not buffer:
            first = number
        buffer.append(line)
    if buffer:
        found.append(Unit("\n".join(buffer), first))
    return found


def slug(text: str) -> str:
    """GitHub's anchor for a heading text, before any repeat suffix.

    Lowercase, drop what is neither alphanumeric nor a space, hyphen or
    underscore, then hyphenate the spaces. Inline markup is not stripped
    first, because no heading in this repo carries a backtick or a link and a
    normaliser for markup nothing has is a path nothing exercises. Emphasis
    markers fall out anyway, since an asterisk is not alphanumeric.
    """
    kept = [c for c in text.strip().lower() if c.isalnum() or c in " -_"]
    return "".join(kept).replace(" ", "-")


def document_headings(text: str) -> list[Heading]:
    """Every ATX heading in one document, in order, each with its anchor.

    Fenced blocks are blanked first. A line starting `#` inside a shell fence
    is a comment, and an index that counted it would let a reference resolve
    against something no reader can click.

    A repeated heading text takes GitHub's numeric suffix, counting
    occurrences rather than special-casing the first repeat.
    `docs/replication-log.md` already carries four repeated texts, and a third
    entry produces a second repeat of each.
    """
    seen: dict[str, int] = {}
    found: list[Heading] = []
    for number, line in enumerate(blank_fences(text).split("\n"), start=1):
        match = _ATX_HEADING.match(line)
        if match is None:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count}"
        found.append(Heading(len(match.group(1)), match.group(2), number, anchor))
    return found


def heading_index(documents: Iterable[Path]) -> dict[Path, list[Heading]]:
    """Every document's headings, keyed by the path the caller handed in."""
    return {document: document_headings(document.read_text("utf-8")) for document in documents}


def nearest_heading(text: str, headings: Iterable[Heading]) -> str:
    """The present heading sharing the most words with one that is missing.

    A rename is the failure this check exists for, so the heading is usually
    sitting in the attributed document under a new name. Zero overlap returns
    nothing, because an unrelated heading offered as the answer sends a reader
    to the wrong section.
    """
    wanted = _words(text)
    best: Heading | None = None
    score = 0
    for heading in headings:
        shared = len(wanted & _words(heading.text))
        if shared > score:
            best, score = heading, shared
    return best.span if best is not None else ""


def attribution(
    unit: Unit,
    start: int,
    end: int,
    document: Path,
    root: Path,
    known: Collection[Path],
) -> Attribution:
    """Decide which document a heading span in `unit` is attributed to.

    A positional word immediately after the span binds tightest and names the
    document the sentence is already in. Otherwise the nearest attribution
    ending before the span wins, which is a Markdown link, a backticked
    filename or an alias phrase.

    `known` holds the resolved paths of the documents in the sweep, and it is
    what separates the second branch from the first. A path-shaped attribution
    outside it names a document nobody keeps.
    """
    if POSITIONAL.match(unit.text, end):
        return Attribution("the document it is written in", document, False)
    candidate = _last_attribution(unit.text[:start], document, root)
    if candidate is None:
        return Attribution("", None, False)
    written, target = candidate
    if target is None:
        return Attribution(written, None, False)
    return Attribution(written, target if target in known else None, True)


def heading_references(root: Path) -> list[QuotedHeading]:
    """Every heading quoted in the repo's prose, each with what attributes it.

    Separate from the sweep below so the suite can assert the scan reaches
    something. This check arrives empty by design, so an empty result and a
    scan that matches nothing are the same green suite, and only a test that
    asks whether anything resolved tells them apart.
    """
    root = root.resolve()
    index = heading_index(path.resolve() for path in markdown_files(root))
    found: list[QuotedHeading] = []
    for document in index:
        text = blank_fences(document.read_text("utf-8"))
        for unit in units(text):
            for match in HEADING_SPAN.finditer(unit.text):
                found.append(
                    QuotedHeading(
                        document,
                        unit.line_of(match.start()),
                        " ".join(match.group(1).split()),
                        attribution(unit, match.start(), match.end(), document, root, index),
                    )
                )
    return found


def sweep_heading_references(root: Path) -> list[ReferenceFinding]:
    """Flag every quoted heading naming no heading in its attributed document.

    The level has to match as well as the text. Every resolving span in this
    repo is written `##` against a level-two heading, so requiring it costs
    nothing today and catches a reference left at `##` for a heading since
    demoted.
    """
    root = root.resolve()
    index = heading_index(path.resolve() for path in markdown_files(root))
    findings: list[ReferenceFinding] = []
    for reference in heading_references(root):
        named = reference.attributed
        here = reference.path.relative_to(root)
        if named.target is None:
            if named.path_shaped:
                findings.append(
                    ReferenceFinding(
                        here,
                        reference.line_number,
                        reference.written,
                        f"is attributed to {named.written}, which this repo does not keep",
                    )
                )
            continue
        level, _, text = reference.written.partition(" ")
        headings = index[named.target]
        if any(head.level == len(level) and head.text == text for head in headings):
            continue
        findings.append(
            ReferenceFinding(
                here,
                reference.line_number,
                reference.written,
                f"names no heading in {named.target.relative_to(root)}",
                nearest_heading(text, headings),
            )
        )
    return findings


def fragment_links(root: Path) -> list[FragmentLink]:
    """Every intra-repository link carrying an anchor, with its target resolved.

    Separate from the sweep below for the reason :func:`heading_references` is.
    """
    root = root.resolve()
    documents = {path.resolve() for path in markdown_files(root)}
    found: list[FragmentLink] = []
    for document in sorted(documents):
        text = blank_fences(document.read_text("utf-8"))
        for match in _MARKDOWN_LINK.finditer(text):
            target = match.group(1)
            if "#" not in target or _SCHEME.match(target):
                continue
            where, _, fragment = target.partition("#")
            named = document if not where else _relative(where, document)
            found.append(
                FragmentLink(
                    document,
                    text.count("\n", 0, match.start()) + 1,
                    target,
                    named if named in documents else None,
                    fragment,
                )
            )
    return found


def sweep_fragment_links(root: Path) -> list[ReferenceFinding]:
    """Flag every fragment link whose slug no heading in its target produces.

    A link into a document this repo does not keep is reported rather than
    skipped, for the reason the attribution scan reports one: a retired
    document is the thing that takes anchors with it.
    """
    root = root.resolve()
    index = heading_index(path.resolve() for path in markdown_files(root))
    findings: list[ReferenceFinding] = []
    for link in fragment_links(root):
        here = link.path.relative_to(root)
        if link.document is None:
            findings.append(
                ReferenceFinding(
                    here,
                    link.line_number,
                    link.target,
                    "points at a document this repo does not keep",
                )
            )
            continue
        headings = index[link.document]
        if any(head.slug == link.fragment for head in headings):
            continue
        findings.append(
            ReferenceFinding(
                here,
                link.line_number,
                link.target,
                f"names no anchor in {link.document.relative_to(root)}",
                nearest_heading(link.fragment.replace("-", " "), headings),
            )
        )
    return findings


def _words(text: str) -> set[str]:
    return {word for word in re.split(r"[^0-9A-Za-z]+", text.lower()) if word}


def _relative(target: str, document: Path) -> Path:
    return Path(os.path.normpath(document.parent / target)).resolve()


def _last_attribution(before: str, document: Path, root: Path) -> tuple[str, Path | None] | None:
    """The attribution nearest the span, scanning back through one unit.

    A Markdown link resolves from the file holding it, because that is what a
    renderer follows. A filename written in prose is followed by nobody and
    this repo writes those from the repository root, so that is the only place
    one is looked for. Trying the document's own directory as well would give
    a filename naming nothing a second chance, which is the branch that
    reports a retired document.
    """
    found: list[tuple[int, str, Path | None]] = []
    for match in _MARKDOWN_LINK.finditer(before):
        target = match.group(1).partition("#")[0]
        if not target.endswith(".md") or _SCHEME.match(target):
            continue
        found.append((match.end(), target, _relative(target, document)))
    for match in _BACKTICKED_DOCUMENT.finditer(before):
        found.append((match.end(), match.group(1), (root / match.group(1)).resolve()))
    for match in _ALIAS.finditer(before):
        aliased = DOCUMENT_ALIASES[match.group(0).lower()]
        found.append((match.end(), match.group(0), (root / aliased).resolve()))
    if not found:
        return None
    _, written, target = max(found)
    return written, target
