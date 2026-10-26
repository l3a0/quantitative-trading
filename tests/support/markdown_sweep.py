"""The prose sweeps for Markdown that markdownlint has no rule for.

Two read one document's own characters, flagging a tilde that can close a
strikethrough pair and a table delimiter row written tight. Two read a
reference in one document against a heading in another, one for a heading
quoted in prose and one for an anchor written into a link. One reads a test
named in prose against the suite under `tests/`. A count here would go stale
the next time a check is added, which is what
`test_the_repo_has_markdown_to_sweep` already decided about files.

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

The single-document checks read prose only. Text inside a fenced block or a
backtick span is exempt, because a pattern written for prose keeps appearing
inside the code fence that documents it. Blanking keeps line numbers intact,
so a finding points at the line a reader will open. The cross-document checks
blank fenced blocks and keep inline spans, because the reference they read is
normally written in backticks.

A test named in prose stops resolving when the test is renamed, or when the
sentence misremembers which class holds it. The suite is the single authority
for every number the prose quotes, so the sentence then points a reader at an
assertion that is not there. The index of real tests is read from each test
file's syntax tree rather than from a pytest collection, which would import
every test module first.

`entry_sections` reads no prose for a sweep of its own. It splits the
replication log into each entry's `###` sections, for checks that read one
section against itself, such as a count stated in a section's lead sentence
against the items listed under it.
"""

from __future__ import annotations

import ast
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
    """One link carrying an anchor, and what the sweep can say about its target.

    `document` is the Markdown file whose headings answer the anchor, and it
    is empty when there is no such file. `exists` then separates the two
    reasons. A target that is there but is not Markdown, such as the committed
    HTML essay, carries headings this sweep cannot index, and calling it a
    document the repo does not keep would be a false claim about a tracked
    file. A target that is not there at all is the retired document this
    sweep exists to notice.
    """

    path: Path
    line_number: int
    target: str
    document: Path | None
    exists: bool
    fragment: str


# A heading quoted in prose. The text may wrap in a hard-wrapped file, so the
# span is read across the unit rather than within one line and its whitespace
# is collapsed afterwards.
#
# Two hashes at least, because one hash and a space is how a shell or Python
# comment is written, and prose quotes those in backticks the same way it
# quotes a heading. A document's one-hash heading is its title, which prose
# names by filename instead, and no tracked file quotes one.
HEADING_SPAN = re.compile(r"`(#{2,6}[ \t][^`]+?)`")

# A positional word, accepted only where it follows the span. Accepting one
# anywhere in the unit fails correct prose: a paragraph can end "the rules
# above" with five unrelated spans in front of it.
POSITIONAL = re.compile(r"[ \t\n]*\b(above|below)\b")

_MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_BACKTICKED_DOCUMENT = re.compile(r"`([^`\s]+\.md)`")
_ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
_TABLE_ROW = re.compile(r"^[ \t]*\|")
_LIST_ITEM = re.compile(r"^[ \t]*(?:[-*+]|[0-9]+[.)])[ \t]")
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# A document this repo's prose names by a phrase rather than by its path. The
# table costs one entry and buys the reference whose target has actually moved
# before now. Skipping what carries no path would drop it.
DOCUMENT_ALIASES = {"the design doc": "docs/design.md"}

_ALIAS = re.compile(
    r"\b(?:" + "|".join(re.escape(alias) for alias in DOCUMENT_ALIASES) + r")\b",
    re.IGNORECASE,
)

# Matched case-insensitively, so the lookup is folded rather than trusting
# every key to be written in lower case.
_ALIAS_TARGETS = {alias.lower(): target for alias, target in DOCUMENT_ALIASES.items()}


def units(text: str) -> list[Unit]:
    """Split a document into the stretches the attribution scan reads.

    A line is the wrong unit because this repo wraps two ways. Some of its
    Markdown files are hard-wrapped near eighty columns and others are authored
    one paragraph per line, so in a hard-wrapped file an attribution and the
    span it governs share a line only by luck. Re-wrapping a paragraph would
    then silence a reference with nothing announcing it.

    The blank-line paragraph is the wrong unit too. A table is one paragraph,
    and a register table's rows each carry their own links and their own
    spans, so reading the table whole hands every row's attribution to every
    other row's span.

    A tight list has the same shape as a table and takes the same rule. Its
    items sit in one blank-line paragraph and each carries its own subject, so
    a list read whole hands one item's attribution to the next item's span.
    This repo writes tight lists everywhere, and one of them already carries a
    heading span.

    So a table row and a list item are each their own unit, and everything
    else is the blank-line paragraph it sits in. A line that continues a list
    item is indented rather than marked, so it joins the item above it.
    """
    found: list[Unit] = []
    buffer: list[str] = []
    first = 0

    def flush() -> None:
        nonlocal buffer
        if buffer:
            found.append(Unit("\n".join(buffer), first))
            buffer = []

    for number, line in enumerate(text.split("\n"), start=1):
        if not line.strip():
            flush()
            continue
        if _TABLE_ROW.match(line):
            flush()
            found.append(Unit(line, number))
            continue
        if _LIST_ITEM.match(line):
            flush()
        if not buffer:
            first = number
        buffer.append(line)
    flush()
    return found


def slug(text: str) -> str:
    """GitHub's anchor for a heading text, before any repeat suffix.

    Lowercase, drop what is neither alphanumeric nor a space, hyphen or
    underscore, then hyphenate the spaces. Inline markup is not stripped
    first. Emphasis markers and code-span backticks fall out anyway, since
    neither an asterisk nor a backtick is alphanumeric, and GitHub drops both
    when it builds the anchor. A link would not fall out, since its URL is
    alphanumeric, but no heading in this repo carries one, and a normaliser
    for markup nothing has is a path nothing exercises.
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
    for line in blank_fences(text).split("\n"):
        match = _ATX_HEADING.match(line)
        if match is None:
            continue
        base = slug(match.group(2))
        count = seen.get(base, 0)
        seen[base] = count + 1
        anchor = base if count == 0 else f"{base}-{count}"
        found.append(Heading(len(match.group(1)), match.group(2), anchor))
    return found


@dataclass(frozen=True)
class EntrySection:
    """One `###` section under a `## Entry N` heading of the replication log."""

    entry: int
    heading: Heading
    first_line: int
    body: str


_ENTRY_HEADING = re.compile(r"Entry (\d+)\b")


def entry_sections(text: str) -> list[EntrySection]:
    """Every subsection of every replication log entry, in order.

    A section runs from its heading to the next heading of level one to three.
    Its body is read after fenced blocks are blanked, so a `#` line inside a
    fence neither opens a section nor ends one. `first_line` is the 1-based
    line the heading sits on, so a finding points at a line a reader opens.

    A `###` heading outside any entry, such as one under `## How to read an
    entry`, belongs to no entry and is left out.
    """
    lines = blank_fences(text).split("\n")
    headings = iter(document_headings(text))
    found: list[EntrySection] = []
    entry: int | None = None
    current: tuple[Heading, int] | None = None
    body: list[str] = []

    def flush() -> None:
        if current is not None and entry is not None:
            found.append(EntrySection(entry, current[0], current[1], "\n".join(body)))

    for number, line in enumerate(lines, start=1):
        # document_headings reads the same blanked lines with the same pattern,
        # so its headings arrive one per matching line, in order.
        heading = next(headings) if _ATX_HEADING.match(line) else None
        if heading is None or heading.level > 3:
            body.append(line)
            continue
        flush()
        body = []
        current = None
        if heading.level <= 2:
            entry_match = _ENTRY_HEADING.match(heading.text) if heading.level == 2 else None
            entry = int(entry_match.group(1)) if entry_match else None
        elif heading.level == 3:
            current = (heading, number)
    flush()
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
    positional = POSITIONAL.match(unit.text, end)
    if positional is not None:
        return Attribution(positional.group(1), document, False)
    candidate = _last_attribution(unit.text[:start], document, root)
    if candidate is None:
        return Attribution("", None, False)
    written, target = candidate
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
            named = _link_target(where, document, root)
            found.append(
                FragmentLink(
                    document,
                    text.count("\n", 0, match.start()) + 1,
                    target,
                    named if named in documents else None,
                    named.exists(),
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
            if link.exists:
                continue
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


# A test cited in prose is a reference into the suite rather than into another
# document. The suite is the single authority for every number the prose
# quotes, so a sentence naming a test is how a reader finds the assertion
# behind a figure. A renamed or misremembered test leaves the sentence pointing
# at nothing, and no renderer or linter reads backticked names against
# `tests/`. README once cited a test under a class that does not hold it, and
# the sentence stood from the pull request that wrote it until a review loop
# found it by hand.
#
# The prose cites a test in five shapes, each a backtick span.
#
# 1. `TestClass::test_name`, sometimes with a parametrize id in brackets.
# 2. `::test_name`, which continues the class cited before it, often in an
#    earlier table row whose citation the next row says "the same" about.
# 3. `TestClass` on its own.
# 4. `test_name` on its own, a module function or any class's method.
# 5. `tests/test_file.py`, alone or ahead of `::` and one of the shapes above.
#
# A parametrize id in brackets is not checked. The ids come from running the
# decorator, which an index read from the syntax tree does not do.
#
# Only shape 5 binds a citation to a file. A paragraph naming a test file
# beside a test class is not a claim that the class lives there, and binding
# the two failed all twelve such citations on main at fdc4938e, each of them
# correct prose naming the file for a different sentence.

_PARAMETRIZE_ID = r"(?:\[[^\]`]*\])?"
_SPAN = re.compile(r"`([^`\n]+)`")
_FILE_CITATION = re.compile(r"^tests/(test_\w+\.py)(?:::(.+?))?$")
_CLASS_AND_TEST = re.compile(rf"^(Test\w+)::(test\w*){_PARAMETRIZE_ID}$")
_CONTINUATION = re.compile(rf"^::(test\w*){_PARAMETRIZE_ID}$")
_CLASS = re.compile(r"^Test[A-Z]\w*$")
_TEST = re.compile(rf"^(test_\w+){_PARAMETRIZE_ID}$")


@dataclass(frozen=True)
class CitedTest:
    """One test named in prose, with the node id it is read as.

    `node` is `TestClass::test_name`, `TestClass` or `test_name`, the id
    pytest prints after the file. It is empty when the span names a file and
    nothing in it. `file` is the test file the span itself names, or empty
    when it names none.
    """

    path: Path
    line_number: int
    written: str
    node: str
    file: str


def suite_index(tests: Path) -> dict[str, frozenset[str]]:
    """Every test file's node ids, read from its syntax tree.

    Reading the tree rather than collecting with pytest skips importing every
    test module and what it imports. At fdc4938e the read took about a second
    and a collection about twenty. The price is that pytest's own rules are
    restated.
    A function or method counts when its name starts `test`, a class when its
    name starts `Test`, and a class also holds the tests of a base class
    defined in the same file. At that commit this index and pytest's
    collection listed the same node ids once parametrize ids were dropped.
    """
    index: dict[str, frozenset[str]] = {}
    for path in sorted(tests.glob("test_*.py")):
        tree = ast.parse(path.read_text("utf-8"), str(path))
        classes = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}
        ids = set(_test_names(tree.body))
        for name, cls in classes.items():
            if not name.startswith("Test"):
                continue
            ids.add(name)
            ids.update(f"{name}::{test}" for test in _class_tests(cls, classes, set()))
        index[path.name] = frozenset(ids)
    return index


def cited_tests(text: str, path: Path) -> list[CitedTest]:
    """Every test the prose of one document cites, in document order.

    A continuation takes the class of the citation before it, which can sit
    in an earlier unit. A replication log row that says "the same, and" a
    continuation is relying on the row above it.
    """
    found: list[CitedTest] = []
    file, cls = "", ""
    for unit in units(blank_fences(text)):
        for match in _SPAN.finditer(unit.text):
            written = match.group(1)
            line = unit.line_of(match.start())
            if named := _FILE_CITATION.match(written):
                file, node = named.group(1), named.group(2) or ""
                node = re.sub(_PARAMETRIZE_ID + "$", "", node)
                cls = node.partition("::")[0] if node.startswith("Test") else ""
            elif named := _CLASS_AND_TEST.match(written):
                file, cls = "", named.group(1)
                node = f"{cls}::{named.group(2)}"
            elif named := _CONTINUATION.match(written):
                node = f"{cls}::{named.group(1)}" if cls else named.group(1)
            elif _CLASS.match(written):
                file, cls, node = "", written, written
            elif named := _TEST.match(written):
                found.append(CitedTest(path, line, written, named.group(1), ""))
                continue
            else:
                continue
            found.append(CitedTest(path, line, written, node, file))
    return found


def sweep_cited_tests(
    documents: Iterable[Path], root: Path, index: dict[str, frozenset[str]]
) -> list[ReferenceFinding]:
    """Flag every cited test the suite does not hold.

    A citation naming a file must resolve in that file. One naming none may
    resolve in any, and a bare `test_name` matches a method of any class as
    well as a module function.
    """
    findings: list[ReferenceFinding] = []
    for document in documents:
        for cited in cited_tests(document.read_text("utf-8"), document.relative_to(root)):
            problem = _cited_test_problem(cited, index)
            if problem:
                findings.append(
                    ReferenceFinding(
                        cited.path,
                        cited.line_number,
                        cited.written,
                        problem,
                        _nearest_test(cited.node, index),
                    )
                )
    return findings


def _cited_test_problem(cited: CitedTest, index: dict[str, frozenset[str]]) -> str:
    if cited.file and cited.file not in index:
        return f"names tests/{cited.file}, which this repo does not keep"
    if not cited.node:
        return ""
    files = [index[cited.file]] if cited.file else list(index.values())
    if any(_holds(ids, cited.node) for ids in files):
        return ""
    where = f"tests/{cited.file}" if cited.file else "the suite"
    return f"names no test in {where}"


def _holds(ids: frozenset[str], node: str) -> bool:
    if node in ids:
        return True
    return (
        "::" not in node
        and node.startswith("test")
        and any(one.endswith(f"::{node}") for one in ids)
    )


def _nearest_test(node: str, index: dict[str, frozenset[str]]) -> str:
    """The present test a missing citation most likely meant.

    The test named under the wrong class is the failure seen so far, so a
    test of the same name under another class wins outright. Otherwise the id
    of the same shape sharing the most words, and nothing when none shares
    one, as `nearest_heading` does.
    """
    if not node:
        return ""
    present = sorted(f"tests/{name}::{one}" for name, ids in index.items() for one in ids)
    wanted = node.rpartition("::")[2]
    if "::" in node:
        same_name = [one for one in present if one.endswith(f"::{wanted}")]
        if same_name:
            return same_name[0]
    shape = node.count("::")
    best, score = "", 0
    for one in present:
        test = one.partition("::")[2]
        if test.count("::") != shape:
            continue
        shared = len(_words(node) & _words(test))
        if shared > score:
            best, score = one, shared
    return best


def _test_names(body: list[ast.stmt]) -> list[str]:
    return [
        node.name
        for node in body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test")
    ]


def _class_tests(cls: ast.ClassDef, classes: dict[str, ast.ClassDef], seen: set[str]) -> set[str]:
    seen.add(cls.name)
    tests = set(_test_names(cls.body))
    for base in cls.bases:
        if isinstance(base, ast.Name) and base.id in classes and base.id not in seen:
            tests |= _class_tests(classes[base.id], classes, seen)
    return tests


def _words(text: str) -> set[str]:
    return {word for word in re.split(r"[^0-9A-Za-z]+", text.lower()) if word}


def _relative(target: str, document: Path) -> Path:
    return Path(os.path.normpath(document.parent / target)).resolve()


def _link_target(where: str, document: Path, root: Path) -> Path:
    """The file a link points at. An empty target means the document itself.

    A leading slash is repository-absolute on GitHub rather than filesystem
    absolute, so it resolves from the root. Reading it as a machine path
    sends every such link to a file no checkout has.
    """
    if not where:
        return document
    if where.startswith("/"):
        return (root / where.lstrip("/")).resolve()
    return _relative(where, document)


def _inside_the_repository(target: str) -> bool:
    """Whether a name in prose could be a document this repository holds.

    A URL, a home-directory path and a machine-absolute path all name
    something outside the checkout, so none of them attributes a heading to a
    tracked document. Treating one as an attribution reports a retired
    document for prose that is right, and `CLAUDE.md` already names the
    owner's global instructions file by a home-directory path.
    """
    return not (_SCHEME.match(target) or target.startswith(("~", "/")))


def _document_path(target: str, document: Path, root: Path) -> Path:
    """Resolve a filename written in prose.

    One written from the repository root is the form this repo uses, so that
    is the default. A leading `./` or `../` says otherwise and is read as
    written, since the root has no parent to climb to and the notation can
    only mean the document's own directory.
    """
    if target.startswith(("./", "../")):
        return _relative(target, document)
    return (root / target).resolve()


def _last_attribution(before: str, document: Path, root: Path) -> tuple[str, Path] | None:
    """The attribution nearest the span, scanning back through one unit.

    A Markdown link resolves from the file holding it, because that is what a
    renderer follows. A filename written in prose is followed by nobody, so it
    is read by the rule above instead.
    """
    found: list[tuple[int, str, Path]] = []
    for match in _MARKDOWN_LINK.finditer(before):
        target = match.group(1).partition("#")[0]
        if not target.endswith(".md") or not _inside_the_repository(target):
            continue
        found.append((match.end(), target, _relative(target, document)))
    for match in _BACKTICKED_DOCUMENT.finditer(before):
        target = match.group(1)
        if not _inside_the_repository(target):
            continue
        found.append((match.end(), target, _document_path(target, document, root)))
    for match in _ALIAS.finditer(before):
        aliased = _ALIAS_TARGETS[match.group(0).lower()]
        found.append((match.end(), match.group(0), (root / aliased).resolve()))
    if not found:
        return None
    _, written, target = max(found)
    return written, target
