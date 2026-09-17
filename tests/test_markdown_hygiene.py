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


def test_discovery_fails_loudly_outside_a_repository(tmp_path: Path) -> None:
    # A silent empty list would turn the sweep below into a vacuous pass.
    with pytest.raises(RuntimeError):
        markdown_files(tmp_path)


def test_the_repo_has_markdown_to_sweep() -> None:
    # Without this, a discovery bug turns the sweep below into a vacuous pass.
    assert len(markdown_files(REPO_ROOT)) >= 3


@pytest.mark.parametrize(
    "path", markdown_files(REPO_ROOT), ids=lambda path: str(path.relative_to(REPO_ROOT))
)
def test_every_markdown_file_passes_the_prose_sweeps(path: Path) -> None:
    findings = sweep_file(path)
    assert not findings, "\n".join(str(finding) for finding in findings)
