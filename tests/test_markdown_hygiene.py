"""The prose sweeps CLAUDE.md names, run as tests rather than from memory.

Two layers. The first pins the sweep's own behavior on small documents, which
is what keeps the code-fence exemption honest. The second runs the sweep over
every Markdown file in the repo, so a slip fails the suite locally and in CI
rather than waiting for someone to remember the command.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.support.markdown_sweep import (
    Finding,
    blank_code,
    markdown_files,
    sweep_file,
    sweep_text,
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


def test_the_repo_has_markdown_to_sweep() -> None:
    # Without this, a discovery bug turns the sweep below into a vacuous pass.
    assert len(markdown_files(REPO_ROOT)) >= 3


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
