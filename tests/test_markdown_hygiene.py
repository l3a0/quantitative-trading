"""The prose sweeps CLAUDE.md names, run as tests rather than from memory.

The behavior layer pins each sweep on small documents, which is what keeps the
code-fence exemption honest. The repository layer runs the single-document
sweeps over every Markdown file here, so a slip fails the suite locally and in
CI rather than waiting for someone to remember the command.

The cross-document layer reads one document against another. A heading quoted
in prose and an anchor written into a link both name a heading somewhere, and
both stop resolving when the heading is renamed with nothing else noticing.

The cross-surface layer is `TestTheFigureHasThreeCopies`. The one committed
figure exists as a PNG, as a base64 copy inlined in the HTML essay, and as an
embed in the blog Markdown. Redrawing it updates one of the three, and nothing
else in this repo would notice the other two.

The layers are named rather than counted, for the reason
`test_the_repo_has_markdown_to_sweep` gives about files. A count is wrong the
moment a layer is added and nothing asserts it.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.support.markdown_sweep import (
    Attribution,
    Finding,
    ReferenceFinding,
    Unit,
    attribution,
    blank_code,
    blank_fences,
    document_headings,
    fragment_links,
    heading_index,
    heading_references,
    markdown_files,
    nearest_heading,
    slug,
    sweep_file,
    sweep_fragment_links,
    sweep_heading_references,
    sweep_text,
    units,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _rules(findings: list[Finding]) -> list[str]:
    return [finding.rule for finding in findings]


def test_a_tilde_glued_to_punctuation_is_flagged() -> None:
    findings = sweep_text("The floor sits near (~30) on a slow day.\n", Path("x.md"))
    assert _rules(findings) == ["unescaped tilde, write it as \\~"]


def test_a_tilde_glued_to_a_letter_is_flagged() -> None:
    findings = sweep_text("It ran word~30 times.\n", Path("x.md"))
    assert _rules(findings) == ["unescaped tilde, write it as \\~"]


def test_a_tilde_after_whitespace_is_left_alone() -> None:
    # One after whitespace can only open a pair, never close one, so it cannot
    # strike out the text behind it.
    assert sweep_text("It retained ~90% of the return.\n", Path("x.md")) == []


def test_an_escaped_tilde_is_left_alone() -> None:
    assert sweep_text("It retained \\~90% of the return.\n", Path("x.md")) == []


def test_a_tilde_inside_a_backtick_span_is_left_alone() -> None:
    assert sweep_text("Run `rg -n '(?<!x)~'` before finalizing.\n", Path("x.md")) == []


def test_a_tilde_inside_a_fenced_block_is_left_alone() -> None:
    document = "Before.\n\n```bash\nrg -n '(?<!x)~' *.md\n```\n\nAfter.\n"
    assert sweep_text(document, Path("x.md")) == []


def test_a_tilde_after_a_fenced_block_closes_is_flagged_again() -> None:
    document = "```bash\necho (~30)\n```\n\nThe floor sits near (~30).\n"
    findings = sweep_text(document, Path("x.md"))
    assert _rules(findings) == ["unescaped tilde, write it as \\~"]
    assert [finding.line_number for finding in findings] == [5]


def test_a_tilde_fenced_block_does_not_flag_its_own_fence() -> None:
    # A fence may be written with tildes. Its own delimiter must not read as
    # prose, or every tilde-fenced block reports two findings.
    assert sweep_text("~~~python\nx = 1\n~~~\n", Path("x.md")) == []


def test_a_tight_delimiter_row_is_flagged() -> None:
    document = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    findings = sweep_text(document, Path("x.md"))
    assert _rules(findings) == ["tight table delimiter row, pad it as | --- |"]
    assert [finding.line_number for finding in findings] == [2]


def test_a_padded_delimiter_row_is_left_alone() -> None:
    assert sweep_text("| a | b |\n| --- | --- |\n| 1 | 2 |\n", Path("x.md")) == []


def test_blanking_keeps_line_numbers_and_lengths() -> None:
    document = "one\n```\ntwo\n```\nthree\n"
    blanked = blank_code(document)
    assert [len(line) for line in blanked.split("\n")] == [
        len(line) for line in document.split("\n")
    ]


def test_an_unmatched_backtick_run_stays_prose() -> None:
    # A lone backtick opens nothing, so the tilde after it is still prose and
    # still capable of closing a strikethrough pair.
    findings = sweep_text("A stray ` and then word~30.\n", Path("x.md"))
    assert _rules(findings) == ["unescaped tilde, write it as \\~"]


def test_discovery_keeps_untracked_files_and_drops_ignored_ones(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("cache/\n", encoding="utf-8")
    (tmp_path / "tracked.md").write_text("tracked\n", encoding="utf-8")
    (tmp_path / "untracked.md").write_text("written but not added\n", encoding="utf-8")
    (tmp_path / "cache").mkdir()
    (tmp_path / "cache" / "README.md").write_text("a tool wrote this\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.md"], cwd=tmp_path, check=True)

    found = [path.relative_to(tmp_path).as_posix() for path in markdown_files(tmp_path)]

    assert found == ["tracked.md", "untracked.md"]


def test_discovery_skips_a_file_deleted_but_still_in_the_index(tmp_path: Path) -> None:
    # git lists an index entry whose file is gone, and reading it raises
    # FileNotFoundError, which reports a pending deletion as a prose failure.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "kept.md").write_text("kept\n", encoding="utf-8")
    (tmp_path / "removed.md").write_text("about to go\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    (tmp_path / "removed.md").unlink()

    found = [path.relative_to(tmp_path).as_posix() for path in markdown_files(tmp_path)]

    assert found == ["kept.md"]


def test_discovery_fails_loudly_outside_a_repository(tmp_path: Path) -> None:
    # A silent empty list would turn the sweep below into a vacuous pass.
    with pytest.raises(RuntimeError):
        markdown_files(tmp_path)


# Every Markdown file this repo owns. A count would let four of them vanish
# from discovery unnoticed, and a sweep that reaches nothing passes.
MUST_BE_SWEPT = frozenset(
    {
        "CLAUDE.md",
        "README.md",
        "docs/design.md",
        "docs/replication-log.md",
        "data/README.md",
        "blog/gld-gdx-cointegration-lessons.md",
        "research/book-notes/README.md",
        "research/book-notes/quantitative-trading.md",
        "research/papers/README.md",
    }
)


def test_findings_far_apart_are_both_reported(tmp_path: Path) -> None:
    """The sweep reads the whole document and reports every finding.

    Two ways to lose a finding leave a green suite: stopping at the first one,
    and reading only the head of a long file. The book notes run past 1400
    lines, so a truncated read would reach a real finding in one of them and
    miss anything below it.
    """
    document = tmp_path / "long.md"
    filler = "\n".join("A clean line." for _ in range(1500))
    document.write_text(f"A floor near (~30).\n{filler}\nA ceiling near (~90).\n")

    findings = sweep_file(document)

    assert [finding.line_number for finding in findings] == [1, 1502]


def test_an_unreadable_document_raises_rather_than_reading_clean(tmp_path: Path) -> None:
    """A read that fails is not a document with nothing wrong in it. Swallowing
    the error would report every unreadable file as clean."""
    directory = tmp_path / "notes.md"
    directory.mkdir()

    with pytest.raises(OSError):
        sweep_file(directory)


def test_the_repo_has_markdown_to_sweep() -> None:
    """Name the files rather than count them.

    A discovery bug turns the parametrized sweep into a vacuous pass, and it
    does not announce itself: the suite goes green with fewer tests. An earlier
    count asked for at least three files against an actual eight, so five could
    vanish unnoticed.
    """
    found = {path.relative_to(REPO_ROOT).as_posix() for path in markdown_files(REPO_ROOT)}
    assert MUST_BE_SWEPT <= found, f"missing from discovery: {sorted(MUST_BE_SWEPT - found)}"


# --- The fence-closing decision ----------------------------------------------
# Every clause of the closing test below was deletable with no test noticing.


def test_a_backtick_fence_is_not_closed_by_a_tilde_line() -> None:
    document = "```bash\n~~~\necho (~30)\n```\n"
    assert sweep_text(document, Path("x.md")) == []


def test_a_longer_run_closes_a_fence() -> None:
    # The closing run may exceed the opening one, so prose after it is prose.
    document = "```\nx\n````\n\nword~30\n"
    findings = sweep_text(document, Path("x.md"))
    assert [finding.line_number for finding in findings] == [5]


def test_a_shorter_run_does_not_close_a_fence() -> None:
    document = "````\n```\nword~30\n````\n"
    assert sweep_text(document, Path("x.md")) == []


def test_a_fence_line_carrying_an_info_string_does_not_close() -> None:
    # Only a bare delimiter closes. A line with an info string opens.
    document = "```\n```python\nword~30\n```\n"
    assert sweep_text(document, Path("x.md")) == []


def test_a_fenced_block_stays_exempt_past_its_second_line() -> None:
    # Clearing the fence unconditionally would end the block after one body
    # line, leaking every longer example in the repo's own docs into prose.
    document = "```bash\nword~30\nword~30\nword~30\n```\n"
    assert sweep_text(document, Path("x.md")) == []


def test_an_indented_fence_is_still_a_fence() -> None:
    document = "  ```\n  word~30\n  ```\n"
    assert sweep_text(document, Path("x.md")) == []


def test_four_spaces_of_indent_is_not_a_fence() -> None:
    # Four spaces is an indented code block, which this sweep does not model,
    # so the delimiter is prose and the line after it is scanned.
    document = "    ```\nword~30\n"
    findings = sweep_text(document, Path("x.md"))
    assert [finding.line_number for finding in findings] == [2]


def test_a_two_character_run_is_not_a_fence() -> None:
    document = "``\nword~30\n``\n"
    findings = sweep_text(document, Path("x.md"))
    assert [finding.line_number for finding in findings] == [2]


def test_a_four_backtick_fence_opens_and_closes() -> None:
    document = "````\nx\n````\n\nword~30\n"
    findings = sweep_text(document, Path("x.md"))
    assert [finding.line_number for finding in findings] == [5]


# --- Backtick spans -----------------------------------------------------------


def test_a_longer_run_does_not_close_a_shorter_span() -> None:
    # The double run does not close the single one, so nothing on the line is
    # a span at all and the tilde is scanned as the prose it is.
    findings = sweep_text("A `word~30 and ``x`` later.\n", Path("x.md"))
    assert _rules(findings) == ["unescaped tilde, write it as \\~"]


def test_a_double_backtick_span_is_not_closed_by_a_single_backtick() -> None:
    # Only a run of exactly two closes it. Anything looser walks off the end
    # of the line, which is a crash rather than a finding.
    assert sweep_text("The span ``a b`\n", Path("x.md")) == []


def test_an_unmatched_run_does_not_swallow_a_later_span() -> None:
    assert sweep_text("A run ``` of three and `x~y` after.\n", Path("x.md")) == []


def test_an_unmatched_run_does_not_stop_the_scan() -> None:
    assert sweep_text("A stray ` and ``x~30`` later.\n", Path("x.md")) == []


def test_a_tilde_after_a_span_closing_backtick_is_left_alone() -> None:
    # The closing backtick is blanked, so the tilde follows whitespace and can
    # only open a pair. Leaving the backtick unblanked would flag this.
    assert sweep_text("Set `flag`~30 percent.\n", Path("x.md")) == []


# --- The two patterns ---------------------------------------------------------


def test_a_tilde_preceded_by_a_tilde_is_left_alone() -> None:
    # A deliberate strikethrough opener is not a slip.
    assert sweep_text("Roughly ~~30 people showed.\n", Path("x.md")) == []


def test_a_tilde_preceded_by_an_angle_bracket_is_left_alone() -> None:
    assert sweep_text("An element a<~b here.\n", Path("x.md")) == []


def test_a_tilde_preceded_by_a_tab_is_left_alone() -> None:
    # The class is whitespace, not a literal space.
    assert sweep_text("A tab\t~30 percent.\n", Path("x.md")) == []


def test_a_one_dash_tight_row_is_flagged() -> None:
    findings = sweep_text("| a |\n|-|\n", Path("x.md"))
    assert _rules(findings) == ["tight table delimiter row, pad it as | --- |"]


def test_a_row_padded_on_one_side_only_is_left_alone() -> None:
    # MD060 is about mixed padding across rows. A half-padded delimiter is not
    # the tight form this sweep exists to catch.
    assert sweep_text("| a |\n|--- |\n", Path("x.md")) == []
    assert sweep_text("| a |\n| ---|\n", Path("x.md")) == []


def test_an_empty_cell_is_not_a_delimiter_row() -> None:
    assert sweep_text("| a | b |\n||\n", Path("x.md")) == []


# --- What a finding reports ---------------------------------------------------


def test_a_finding_quotes_the_source_line_not_the_blanked_one() -> None:
    # The reader opens the file at this line, so the message has to match what
    # they will see there rather than the blanked copy the scan read.
    findings = sweep_text("A `code` and word~30.\n", Path("x.md"))
    assert [finding.line for finding in findings] == ["A `code` and word~30."]


# --- Discovery ----------------------------------------------------------------


def test_discovery_skips_a_markdown_path_that_is_not_a_regular_file(
    tmp_path: Path,
) -> None:
    # A directory named like a document satisfies an existence check and then
    # raises IsADirectoryError from the read.
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "kept.md").write_text("kept\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("about to become a directory\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    (tmp_path / "notes.md").unlink()
    (tmp_path / "notes.md").mkdir()

    found = [path.relative_to(tmp_path).as_posix() for path in markdown_files(tmp_path)]

    assert found == ["kept.md"]


@pytest.mark.parametrize(
    "path", markdown_files(REPO_ROOT), ids=lambda path: str(path.relative_to(REPO_ROOT))
)
def test_every_markdown_file_passes_the_prose_sweeps(path: Path) -> None:
    findings = sweep_file(path)
    assert not findings, "\n".join(str(finding) for finding in findings)


# --- The cross-document layer -------------------------------------------------
# A heading quoted in prose and an anchor written into a link both name a
# heading somewhere else. Neither is a link a renderer resolves, so nothing
# else here notices when the heading is renamed out from under it.


def _repository(tmp_path: Path, files: dict[str, str]) -> Path:
    """A committed repo, since discovery asks git which files it owns."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    for name, body in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    return tmp_path


def _messages(findings: list) -> list[str]:
    return [str(finding) for finding in findings]


# --- The unit the attribution scan reads --------------------------------------


def test_a_paragraph_is_one_unit_across_its_lines() -> None:
    # A hard-wrapped file puts the attribution and the span it governs on the
    # same line only by luck, so the scan reads past the wrap.
    found = units("The design doc's\n`## Heading` carries it.\n")
    assert [unit.text for unit in found] == ["The design doc's\n`## Heading` carries it."]


def test_a_blank_line_ends_a_unit() -> None:
    found = units("First.\n\nSecond.\n")
    assert [(unit.text, unit.first_line) for unit in found] == [("First.", 1), ("Second.", 3)]


def test_a_table_row_is_its_own_unit() -> None:
    # A register table is one blank-line paragraph, and reading it whole hands
    # every row's attribution to every other row's span.
    found = units("| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    assert [unit.first_line for unit in found] == [1, 2, 3]
    assert [unit.text for unit in found] == ["| a | b |", "| --- | --- |", "| 1 | 2 |"]


def test_a_table_row_breaks_the_paragraph_around_it() -> None:
    found = units("Lead in.\n| a |\nTrail.\n")
    assert [(unit.text, unit.first_line) for unit in found] == [
        ("Lead in.", 1),
        ("| a |", 2),
        ("Trail.", 3),
    ]


def test_a_list_item_is_its_own_unit() -> None:
    # A tight list is one blank-line paragraph and each item carries its own
    # subject, so reading the list whole lends one item's attribution to the
    # next item's span. CLAUDE.md already writes a list of that shape.
    found = units("- First names a file.\n- Second quotes a heading.\n")
    assert [(unit.text, unit.first_line) for unit in found] == [
        ("- First names a file.", 1),
        ("- Second quotes a heading.", 2),
    ]


def test_a_numbered_item_is_its_own_unit() -> None:
    found = units("1. First.\n2. Second.\n")
    assert [unit.first_line for unit in found] == [1, 2]


def test_a_continuation_line_joins_the_item_above_it() -> None:
    # A wrapped item is indented rather than marked, so it belongs to the
    # item it continues and not to a unit of its own.
    found = units("- An item that runs on\n  past the margin.\n- The next one.\n")
    assert [unit.text for unit in found] == [
        "- An item that runs on\n  past the margin.",
        "- The next one.",
    ]


def test_a_unit_reports_the_line_an_offset_sits_on() -> None:
    # The finding points at the line the span sits on, which the paragraph
    # rule would otherwise lose to the line the unit starts at.
    unit = units("one\ntwo\nthree\n")[0]
    assert [unit.line_of(unit.text.index(word)) for word in ("one", "two", "three")] == [1, 2, 3]


# --- The heading index --------------------------------------------------------


def test_a_heading_carries_its_level_and_its_text() -> None:
    found = document_headings("# Title\n\ntext\n\n### Deep\n")
    assert [(head.level, head.text) for head in found] == [(1, "Title"), (3, "Deep")]


def test_a_hash_inside_a_fence_is_not_a_heading() -> None:
    # A line starting `#` inside a shell fence is a comment. CLAUDE.md has two,
    # and an index counting them lets a reference resolve against a comment.
    assert document_headings("```bash\n# Not a heading\n```\n") == []


def test_a_closing_hash_run_is_not_part_of_the_heading_text() -> None:
    assert [head.text for head in document_headings("## Closed ##\n")] == ["Closed"]


def test_a_repeated_heading_text_takes_githubs_numeric_suffix() -> None:
    # MD024 is set to siblings_only on purpose, so the log repeats a table
    # heading per entry and a third entry produces a second repeat.
    found = document_headings("### The verdicts\n\n### The verdicts\n\n### The verdicts\n")
    assert [head.slug for head in found] == ["the-verdicts", "the-verdicts-1", "the-verdicts-2"]


def test_the_index_keys_headings_by_the_path_handed_in(tmp_path: Path) -> None:
    (tmp_path / "one.md").write_text("## One\n", encoding="utf-8")
    index = heading_index([tmp_path / "one.md"])
    assert [head.span for head in index[tmp_path / "one.md"]] == ["## One"]


# --- The anchor a heading produces --------------------------------------------


def test_a_slug_lowercases_and_hyphenates() -> None:
    assert slug("How work is cut and ordered") == "how-work-is-cut-and-ordered"


def test_a_slug_drops_punctuation_and_emphasis() -> None:
    assert slug("Entry 1: GLD/GDX and KO/PEP, Chan's *Quantitative Trading*") == (
        "entry-1-gldgdx-and-kopep-chans-quantitative-trading"
    )


def test_a_slug_keeps_digits_underscores_and_hyphens() -> None:
    assert slug("Pass 2_3 and non-obvious") == "pass-2_3-and-non-obvious"


# --- Which document a sentence attributes a heading to ------------------------


def _attributed(text: str, span: str, document: Path, root: Path, known=()) -> Attribution:
    start = text.index(span)
    return attribution(Unit(text, 1), start, start + len(span), document, root, set(known))


def test_a_positional_word_after_the_span_names_the_document_it_is_in() -> None:
    here = Path("/repo/data/README.md")
    named = _attributed("`## Header shape` below is why.", "`## Header shape`", here, Path("/repo"))
    assert named.target == here


def test_a_positional_word_elsewhere_in_the_unit_does_not_attribute() -> None:
    # CLAUDE.md's pull request paragraph ends "the writing-style rules above"
    # with five correct spans in front of it. Accepting the word anywhere in
    # the unit fails all five.
    text = "Lead with `## Why`, then `## What`. The prose obeys the rules above."
    named = _attributed(text, "`## Why`", Path("/repo/CLAUDE.md"), Path("/repo"))
    assert named.target is None and not named.path_shaped


def test_a_positional_word_still_binds_across_a_wrapped_line() -> None:
    # Re-wrapping a paragraph is an edit nothing announces, and a line scan
    # goes quiet when the wrap lands between the span and the word.
    here = Path("/repo/data/README.md")
    text = "The check compares the record against `## Header shape`\nbelow, which says why."
    assert _attributed(text, "`## Header shape`", here, Path("/repo")).target == here


def test_a_markdown_link_attributes_the_span_that_follows_it(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("## Status\n", encoding="utf-8")
    named = _attributed(
        "and [README.md](README.md)'s `## Status` names what runs today.",
        "`## Status`",
        tmp_path / "CLAUDE.md",
        tmp_path,
        known=[(tmp_path / "README.md").resolve()],
    )
    assert named.target == (tmp_path / "README.md").resolve()


def test_a_link_resolves_from_the_file_holding_it(tmp_path: Path) -> None:
    # docs/design.md writes `../data/README.md`, which is what a renderer
    # follows and is not where the repository root would look.
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "README.md").write_text("## Header shape\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    named = _attributed(
        "the prose in [data/README.md](../data/README.md)'s `## Header shape`",
        "`## Header shape`",
        tmp_path / "docs" / "design.md",
        tmp_path,
        known=[(tmp_path / "data" / "README.md").resolve()],
    )
    assert named.target == (tmp_path / "data" / "README.md").resolve()


def test_a_backticked_filename_resolves_from_the_repository_root(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("## The write-up\n", encoding="utf-8")
    named = _attributed(
        "`README.md`'s `## The write-up` lists the rest.",
        "`## The write-up`",
        tmp_path / "CLAUDE.md",
        tmp_path,
        known=[(tmp_path / "README.md").resolve()],
    )
    assert named.target == (tmp_path / "README.md").resolve()


def test_the_nearest_attribution_wins(tmp_path: Path) -> None:
    # A register row carries several links, and the span belongs to the one
    # beside it rather than to the first in the row.
    for name in ("one.md", "two.md"):
        (tmp_path / name).write_text("## Shared\n", encoding="utf-8")
    known = [(tmp_path / name).resolve() for name in ("one.md", "two.md")]
    named = _attributed(
        "| `one.md` sets it out and `two.md`'s `## Shared` repeats it. |",
        "`## Shared`",
        tmp_path / "docs.md",
        tmp_path,
        known=known,
    )
    assert named.target == (tmp_path / "two.md").resolve()


def test_an_alias_resolves_through_the_table(tmp_path: Path) -> None:
    # The reference whose target has actually moved carries no path at all.
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "design.md").write_text("## How work is cut and ordered\n", "utf-8")
    named = _attributed(
        "The design doc's `## How work is cut and ordered` carries the rules.",
        "`## How work is cut and ordered`",
        tmp_path / "CLAUDE.md",
        tmp_path,
        known=[(tmp_path / "docs" / "design.md").resolve()],
    )
    assert named.target == (tmp_path / "docs" / "design.md").resolve()


def test_an_attribution_naming_no_tracked_document_stays_path_shaped(tmp_path: Path) -> None:
    named = _attributed(
        "`docs/build-plan.md`'s `## The order` says so.",
        "`## The order`",
        tmp_path / "CLAUDE.md",
        tmp_path,
    )
    assert named.target is None and named.path_shaped


def test_a_span_with_nothing_attributing_it_resolves_to_nothing() -> None:
    named = _attributed(
        "An issue body opens with `## Done when`.",
        "`## Done when`",
        Path("/repo/docs/design.md"),
        Path("/repo"),
    )
    assert named.target is None and not named.path_shaped


def test_a_one_hash_span_is_a_comment_rather_than_a_heading(tmp_path: Path) -> None:
    # A shell or Python comment is quoted in backticks the same way a heading
    # is, and prose in this repo writes plenty of them.
    root = _repository(
        tmp_path,
        {"CLAUDE.md": "The design doc explains `# type: ignore`.\n", "docs/design.md": "# D\n"},
    )
    assert sweep_heading_references(root) == []


def test_an_alias_needs_its_own_word_boundaries(tmp_path: Path) -> None:
    # "the design docs" names no one document, so it attributes nothing.
    named = _attributed(
        "Neither the design docs nor the tracker keep a body's `## Evidence`.",
        "`## Evidence`",
        tmp_path / "CLAUDE.md",
        tmp_path,
    )
    assert named.target is None and not named.path_shaped


def test_a_url_ending_in_md_is_not_an_attribution(tmp_path: Path) -> None:
    # A link to another repository's file names nothing this checkout holds,
    # so reporting it would fail correct prose rather than find a deletion.
    for written in (
        "The template's `https://github.com/l3a0/repo-template/blob/main/CLAUDE.md`",
        "The template's [CLAUDE.md](https://github.com/l3a0/repo-template/blob/main/CLAUDE.md)",
    ):
        named = _attributed(
            f"{written} and a body's `## Why` after it.",
            "`## Why`",
            tmp_path / "CLAUDE.md",
            tmp_path,
        )
        assert named.target is None and not named.path_shaped


def test_a_home_directory_path_is_not_an_attribution(tmp_path: Path) -> None:
    # CLAUDE.md names the owner's global instructions file this way today.
    named = _attributed(
        "The owner's global `~/.claude/CLAUDE.md` is the source, and its `## Writing style` wins.",
        "`## Writing style`",
        tmp_path / "CLAUDE.md",
        tmp_path,
    )
    assert named.target is None and not named.path_shaped


def test_a_backticked_filename_written_upwards_resolves_from_the_document(
    tmp_path: Path,
) -> None:
    # The repository root has no parent to climb to, so `../` can only mean
    # the directory the sentence is written in.
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "README.md").write_text("## Header shape\n", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    named = _attributed(
        "`../data/README.md`'s `## Header shape` states it.",
        "`## Header shape`",
        tmp_path / "docs" / "design.md",
        tmp_path,
        known=[(tmp_path / "data" / "README.md").resolve()],
    )
    assert named.target == (tmp_path / "data" / "README.md").resolve()


def test_a_positional_attribution_records_the_word_it_matched() -> None:
    here = Path("/repo/data/README.md")
    named = _attributed("`## Header shape` below is why.", "`## Header shape`", here, Path("/repo"))
    assert named.written == "below"


def test_a_python_filename_is_not_an_attribution(tmp_path: Path) -> None:
    # Only a Markdown file can hold a Markdown heading, so a source file
    # beside a span leaves the span unattributed rather than reported.
    named = _attributed(
        "[src/chan/vintage.py](src/chan/vintage.py) and `## Done when` after it.",
        "`## Done when`",
        tmp_path / "docs.md",
        tmp_path,
    )
    assert named.target is None and not named.path_shaped


# --- What a reference finding says --------------------------------------------


def test_the_nearest_heading_is_the_one_sharing_most_words() -> None:
    present = document_headings("## How work is cut\n\n## What this repo is for\n")
    assert nearest_heading("How work is cut and ordered", present) == "## How work is cut"


def test_no_shared_word_suggests_nothing() -> None:
    # An unrelated heading offered as the answer sends a reader to the wrong
    # section, which is worse than saying nothing.
    present = document_headings("## Configuration\n")
    assert nearest_heading("Status", present) == ""


def test_a_finding_names_the_file_the_line_the_span_and_the_nearest_heading() -> None:
    finding = ReferenceFinding(
        Path("CLAUDE.md"), 6, "## Status", "names no heading in README.md", "## Statuses"
    )
    assert str(finding) == (
        "CLAUDE.md:6: `## Status` names no heading in README.md, nearest present is `## Statuses`"
    )


def test_a_finding_with_no_suggestion_says_nothing_about_one() -> None:
    finding = ReferenceFinding(Path("CLAUDE.md"), 6, "## Status", "names no heading in README.md")
    assert str(finding) == "CLAUDE.md:6: `## Status` names no heading in README.md"


# --- The heading sweep, end to end --------------------------------------------


def test_a_renamed_heading_fails_and_the_message_names_the_one_that_replaced_it(
    tmp_path: Path,
) -> None:
    root = _repository(
        tmp_path,
        {
            "CLAUDE.md": "See [README.md](README.md)'s `## Status` for what runs.\n",
            "README.md": "# Repo\n\n## Status of each replication\n\nRows.\n",
        },
    )
    findings = sweep_heading_references(root)
    assert _messages(findings) == [
        "CLAUDE.md:1: `## Status` names no heading in README.md, "
        "nearest present is `## Status of each replication`"
    ]


def test_a_rename_sharing_no_word_is_still_caught_and_suggests_nothing(tmp_path: Path) -> None:
    root = _repository(
        tmp_path,
        {
            "CLAUDE.md": "See [README.md](README.md)'s `## Status` for what runs.\n",
            "README.md": "# Repo\n\n## Where the numbers come from\n\nRows.\n",
        },
    )
    assert _messages(sweep_heading_references(root)) == [
        "CLAUDE.md:1: `## Status` names no heading in README.md"
    ]


def test_a_demoted_heading_fails_although_its_text_is_still_there(tmp_path: Path) -> None:
    # Nothing was renamed and nothing moved, and the reference still sends a
    # reader to a section that is not at the level the prose says.
    root = _repository(
        tmp_path,
        {
            "CLAUDE.md": "See [README.md](README.md)'s `## Status` for what runs.\n",
            "README.md": "# Repo\n\n### Status\n\nRows.\n",
        },
    )
    assert _messages(sweep_heading_references(root)) == [
        "CLAUDE.md:1: `## Status` names no heading in README.md, nearest present is `### Status`"
    ]


def test_a_span_attributed_to_a_document_this_repo_does_not_keep_is_reported(
    tmp_path: Path,
) -> None:
    # What a retired document leaves behind. Skipping an attribution that does
    # not resolve would make the sweep quiet about exactly that deletion.
    root = _repository(tmp_path, {"CLAUDE.md": "`docs/build-plan.md`'s `## The order` says.\n"})
    assert _messages(sweep_heading_references(root)) == [
        "CLAUDE.md:1: `## The order` is attributed to docs/build-plan.md, "
        "which this repo does not keep"
    ]


def test_a_past_tense_record_naming_a_retired_document_stays_quiet(tmp_path: Path) -> None:
    # The branch is keyed on the span rather than on the filename, so a
    # sentence saying a file used to hold something reports nothing.
    root = _repository(tmp_path, {"CLAUDE.md": "`docs/build-plan.md` used to hold both.\n"})
    assert sweep_heading_references(root) == []


def test_a_span_nothing_attributes_is_left_alone(tmp_path: Path) -> None:
    # An issue body's `## Done when` is not a rename of anything, and a
    # fallback requiring the heading to exist somewhere fails nine correct
    # sentences in this repo.
    root = _repository(tmp_path, {"docs.md": "An issue body opens with `## Done when`.\n"})
    assert sweep_heading_references(root) == []


def test_a_table_row_does_not_lend_its_attribution_to_the_next_row(tmp_path: Path) -> None:
    # Reading the table as one paragraph fails both rows below, which are
    # correct prose. Removing the table-row split is what this pins.
    root = _repository(
        tmp_path,
        {
            "docs.md": (
                "| Row | Note |\n"
                "| --- | --- |\n"
                "| A | [README.md](README.md)'s `## Status` lists it. |\n"
                "| B | An issue body opens with `## Done when`. |\n"
            ),
            "README.md": "# Repo\n\n## Status\n",
        },
    )
    assert sweep_heading_references(root) == []


def test_a_heading_span_wrapped_across_two_lines_still_resolves(tmp_path: Path) -> None:
    root = _repository(
        tmp_path,
        {
            "docs.md": "See [README.md](README.md)'s `## How work is\ncut and ordered` for it.\n",
            "README.md": "# Repo\n\n## How work is cut and ordered\n",
        },
    )
    assert sweep_heading_references(root) == []


def test_a_heading_quoted_inside_a_fence_is_not_a_reference(tmp_path: Path) -> None:
    root = _repository(
        tmp_path,
        {"docs.md": "```bash\ngrep -n '[README.md](README.md)' && echo '`## Gone`'\n```\n"},
    )
    assert sweep_heading_references(root) == []


# --- The anchor sweep, end to end ---------------------------------------------


def test_an_anchor_no_heading_produces_is_flagged(tmp_path: Path) -> None:
    root = _repository(tmp_path, {"docs.md": "# Doc\n\n[Jump](#the-order)\n\n## The ordering\n"})
    assert _messages(sweep_fragment_links(root)) == [
        "docs.md:3: `#the-order` names no anchor in docs.md, nearest present is `## The ordering`"
    ]


def test_an_anchor_matching_a_heading_resolves(tmp_path: Path) -> None:
    root = _repository(tmp_path, {"docs.md": "# Doc\n\n[Jump](#the-order)\n\n## The order\n"})
    assert sweep_fragment_links(root) == []


def test_a_repeated_headings_suffixed_anchor_resolves(tmp_path: Path) -> None:
    # The log's Contents links depend on the suffix, and a third entry adds a
    # second repeat of each of its four repeated texts.
    root = _repository(
        tmp_path,
        {
            "log.md": "[One](#the-verdicts)\n[Two](#the-verdicts-1)\n\n## The verdicts\n\n"
            "## The verdicts\n"
        },
    )
    assert sweep_fragment_links(root) == []


def test_a_cross_document_anchor_resolves_against_the_other_file(tmp_path: Path) -> None:
    root = _repository(
        tmp_path,
        {
            "docs/log.md": "[Terms](design.md#vocabulary)\n",
            "docs/design.md": "# Design\n\n## Vocabulary\n",
        },
    )
    assert sweep_fragment_links(root) == []


def test_a_cross_document_anchor_that_stopped_resolving_is_flagged(tmp_path: Path) -> None:
    root = _repository(
        tmp_path,
        {
            "docs/log.md": "[Terms](design.md#vocabulary)\n",
            "docs/design.md": "# Design\n\n## Pinned vocabulary\n",
        },
    )
    assert _messages(sweep_fragment_links(root)) == [
        "docs/log.md:1: `design.md#vocabulary` names no anchor in docs/design.md, "
        "nearest present is `## Pinned vocabulary`"
    ]


def test_an_anchor_into_a_document_this_repo_does_not_keep_is_flagged(tmp_path: Path) -> None:
    root = _repository(tmp_path, {"docs.md": "[Order](build-plan.md#the-order)\n"})
    assert _messages(sweep_fragment_links(root)) == [
        "docs.md:1: `build-plan.md#the-order` points at a document this repo does not keep"
    ]


def test_an_anchor_into_a_tracked_file_this_sweep_cannot_index_is_left_alone(
    tmp_path: Path,
) -> None:
    # The committed HTML essay is a prose surface this repo keeps and this
    # sweep cannot read headings from. Calling it missing is a false claim
    # about a tracked file.
    root = _repository(
        tmp_path,
        {
            "README.md": "# R\n\nSee [the essay](docs/essay.html#lesson-three).\n",
            "docs/essay.html": "<h2 id='lesson-three'>Lesson three</h2>\n",
        },
    )
    assert sweep_fragment_links(root) == []


def test_a_root_absolute_anchor_resolves_from_the_repository_root(tmp_path: Path) -> None:
    # A leading slash is repository-absolute on GitHub rather than a machine
    # path, and reading it as one sends every such link to a file nobody has.
    root = _repository(
        tmp_path,
        {"docs/design.md": "# D\n\n## Vocabulary\n\n[Terms](/docs/design.md#vocabulary)\n"},
    )
    assert sweep_fragment_links(root) == []


def test_an_external_fragment_link_is_left_alone(tmp_path: Path) -> None:
    root = _repository(tmp_path, {"docs.md": "[Spec](https://example.com/page#section)\n"})
    assert sweep_fragment_links(root) == []


def test_an_anchor_inside_a_fence_is_not_a_link(tmp_path: Path) -> None:
    root = _repository(tmp_path, {"docs.md": "```markdown\n[Gone](#no-such-heading)\n```\n"})
    assert sweep_fragment_links(root) == []


# --- The two whole-repo assertions ---------------------------------------------


def test_the_repo_has_references_to_sweep() -> None:
    """Name the shape rather than count the references.

    Both sweeps below arrive empty and stay empty, so a scan that matches
    nothing and a repo with nothing wrong in it are the same green suite. This
    is what tells them apart. A count would go stale on the next paragraph
    anybody writes, which is what `test_the_repo_has_markdown_to_sweep`
    already decided about files.
    """
    quoted = [one for one in heading_references(REPO_ROOT) if one.attributed.target]
    anchors = [link for link in fragment_links(REPO_ROOT) if link.document]
    assert quoted, "no quoted heading in this repo is attributed to a document it keeps"
    assert anchors, "no fragment link in this repo resolves to a document it keeps"


def test_no_prose_surface_quotes_a_heading_that_is_not_there() -> None:
    """A quoted heading is not a link, so nothing else here resolves it.

    A reader who cannot find the section guesses which one was meant, or
    concludes the instructions are stale and discounts the rest. CLAUDE.md is
    loaded at the start of every session, so the second reading is paid by
    every session after the drift lands.
    """
    findings = sweep_heading_references(REPO_ROOT)
    assert not findings, "\n".join(_messages(findings))


def test_every_fragment_link_resolves_to_a_heading() -> None:
    """CLAUDE.md says to verify the Contents anchors by hand when a heading
    changes. This is that, executed. An anchor nobody kept still renders as a
    working link, and GitHub answers it by leaving the reader at the top."""
    findings = sweep_fragment_links(REPO_ROOT)
    assert not findings, "\n".join(_messages(findings))


# --- The cross-surface layer ---------------------------------------------------
# CLAUDE.md's sweep policy, executed. Two of its three sweeps have nothing to
# check here yet, so the assertions below say so rather than passing vacuously.

FIGURE = REPO_ROOT / "docs" / "figures" / "reproduction_regime_map.png"
ESSAY_HTML = REPO_ROOT / "docs" / "gld-gdx-cointegration-lessons.html"
ESSAY_MD = REPO_ROOT / "blog" / "gld-gdx-cointegration-lessons.md"


class TestTheFigureHasThreeCopies:
    def test_the_inlined_figure_matches_the_committed_png(self) -> None:
        """Redrawing the figure and not re-inlining it is the failure here.

        The HTML is self-contained on purpose, so it carries the image rather
        than linking it. That makes the page publishable and makes the bytes a
        second copy, which is the thing a sweep exists to catch.
        """
        import base64
        import re

        html = ESSAY_HTML.read_text(encoding="utf-8")
        matches = re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)", html)
        assert len(matches) == 1, f"expected one inlined image, found {len(matches)}"
        assert base64.b64decode(matches[0]) == FIGURE.read_bytes()

    def test_every_figure_the_blog_embeds_exists(self) -> None:
        """A relative embed resolves from the Markdown file's own directory."""
        import re

        embeds = re.findall(r"\]\(([^)]*docs/figures/[^)]+\.png)\)", ESSAY_MD.read_text("utf-8"))
        assert embeds, "the blog post embeds no figure, so this sweep checks nothing"
        for embed in embeds:
            assert (ESSAY_MD.parent / embed).resolve().is_file(), f"missing embed: {embed}"

    def test_no_prose_surface_names_a_line_number(self) -> None:
        """A prose reference names a symbol, which survives an edit.

        This is empty today and the assertion is what keeps it empty. A line
        number in prose is invisible to every other sweep here, because it is
        not a link and resolves to nothing a checker can follow.
        """
        import re

        pattern = re.compile(r"[a-z_]+\.py[:#]L?\d")
        offenders = [
            f"{path.relative_to(REPO_ROOT)}:{n}"
            for path in markdown_files(REPO_ROOT)
            for n, line in enumerate(blank_fences(path.read_text("utf-8")).splitlines(), 1)
            if pattern.search(line)
        ]
        assert not offenders, "line references in prose: " + ", ".join(offenders)
