"""What this repository still owns of the build board, once the board is shared.

Since issue 785 the generator, the page and their tests live in
l3a0/repo-template, and ``.github/workflows/board.yml`` here only calls that
template's reusable workflow at a pinned commit. The template's suite checks the
template's own caller, not this one. So the checks that read this repository's
files stay here, moved from ``tests/test_build_board.py`` and
``tests/test_build_board_generator.py`` as they stood at ``cdab8edc``.

1. The caller's triggers, schedule, concurrency group, pin and inputs.
2. The Pages block of ``scripts/setup-repo.sh``, whose deploy target the
   reusable workflow needs.
3. That no tracked file links a claude.ai artifact, a check on every file that
   the board's history is the reason for.

Nothing here makes a network read, so nothing here checks that the pinned
commit exists or that its workflow still takes these inputs. The first board
run on ``main`` after a pin moves is that check.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "board.yml"
SETUP = REPO_ROOT / "scripts" / "setup-repo.sh"
LABELS = REPO_ROOT / ".github" / "labels.json"
USES = re.compile(
    r"^    uses: l3a0/repo-template/\.github/workflows/build-board\.yml@(\S+)\s*$", re.M
)


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def _inputs() -> dict[str, str]:
    """The ``with:`` block under the job's ``uses:`` line, as written."""
    block = _workflow().split("\n    with:\n", 1)[1]
    return dict(re.findall(r"^      ([\w-]+): (.+?)\s*$", block, re.M))


def test_the_schedule_stays_off_the_hour() -> None:
    """Protects the scheduled runs from the top of the hour.

    The workflow's comment keeps the schedule off minute 0, because GitHub's
    documentation names the start of every hour as its busiest time. The test
    reads the minutes rather than pinning the line, so the minutes can move
    again without editing it. The template's generator reads this line too,
    to say when the board is stale, and it stops the run on any schedule that
    is not one list of minutes past every hour, such as ``8 */2 * * *``. So a
    line of another shape would pass this repository's CI and fail every board
    run, with the page calling itself current for ten and a half hours.
    """
    crons = re.findall(r"""^\s*-\s*cron:\s*"([^"]+)"\s*$""", _workflow(), re.M)
    assert len(crons) == 1
    minute, *rest = crons[0].split()
    assert rest == ["*", "*", "*", "*"], crons[0]
    assert re.fullmatch(r"\d{1,2}(,\d{1,2})*", minute), minute
    assert all(1 <= int(m) <= 59 for m in minute.split(",")), minute


def test_the_triggers_are_the_ones_that_can_deploy() -> None:
    """Protects the deploy, which only the default branch may make.

    ``pull_request`` and ``pull_request_review`` run on a merge ref, which the
    github-pages environment refuses. ``pull_request_target`` needs ``closed``
    and ``edited`` listed, or a merged ``Part of`` pull request and a corrected
    closing link wait for the cron run. ``workflow_dispatch`` stays because a
    "blocked by" link and a sub-issue start no run, so the session that makes
    one dispatches the board itself, which issue 587 led to.
    """
    flow = _workflow()
    on = flow.split("\non:\n", 1)[1].split("\npermissions:", 1)[0]
    triggers = re.findall(r"^  (\w+):", on, re.M)
    assert triggers == [
        "issues",
        "issue_comment",
        "pull_request_target",
        "workflow_run",
        "schedule",
        "workflow_dispatch",
    ]
    target = on.split("  pull_request_target:\n", 1)[1].split("\n  # ", 1)[0]
    assert "branches: [main]" in target
    assert "types: [opened, synchronize, reopened, closed, edited]" in target
    assert "workflows: [CI]" in on
    assert "types: [completed]" in on


def test_runs_deploy_one_at_a_time_and_none_is_cancelled() -> None:
    """Protects a newer board from an older run deploying over it."""
    assert "concurrency:\n  group: pages\n  cancel-in-progress: false\n" in _workflow()


def test_the_template_is_pinned_to_the_commit_the_header_names() -> None:
    """Protects the board from changing without a pull request here.

    A full commit SHA cannot be moved, while a branch or a tag can, so the
    called workflow and the generator and page it checks out change only when
    this line does. The header names the same commit, so a reader comparing it
    with the template's caller compares the right file.
    """
    pins = USES.findall(_workflow())
    assert len(pins) == 1
    assert re.fullmatch(r"[0-9a-f]{40}", pins[0]), pins[0]
    header = _workflow().split("\non:\n", 1)[0]
    assert re.findall(r"\b[0-9a-f]{40}\b", header) == pins


def test_the_job_grants_what_the_reusable_workflow_asks_for() -> None:
    """Protects the run from a job asking for a scope the caller did not grant.

    A called workflow can only narrow what its caller grants. These are the
    scopes the template's build and deploy jobs declare at the pinned commit,
    which were also this repository's own two jobs' scopes before the move.
    A pin that moves to a commit whose jobs ask for more fails here only if
    this list is updated with it, so moving the pin means reading the
    template's ``build-board.yml`` at the new commit.
    """
    job = _workflow().split("\n  board:\n", 1)[1]
    block = job.split("    permissions:\n", 1)[1].split("\n    uses:", 1)[0]
    granted = dict(re.findall(r"^      ([\w-]+): (\w+)\s*$", block, re.M))
    assert granted == {
        "contents": "read",
        "issues": "read",
        "pull-requests": "read",
        "checks": "read",
        "statuses": "read",
        "pages": "write",
        "id-token": "write",
        "actions": "read",
    }
    assert re.search(r"^permissions: \{\}\s*$", _workflow(), re.M)


def test_the_data_label_is_a_label_this_repository_creates() -> None:
    """Protects the Waiting on data column from a label nobody carries.

    The reusable workflow draws a card in that column when it carries the
    label the ``data-label`` input names. A name with no label behind it reads
    as zero cards rather than failing, so the input is checked against the
    labels ``scripts/setup-repo.sh`` creates. The title input keeps the
    heading this board had before the move.
    """
    inputs = _inputs()
    assert inputs == {
        "title": "Quantitative Trading Build Board",
        "data-label": "blocked-on-data",
    }
    names = {label["name"] for label in json.loads(LABELS.read_text(encoding="utf-8"))}
    assert inputs["data-label"] in names


def test_no_tracked_file_links_to_a_claude_artifact() -> None:
    """Protects every machine from a board address only one account can reach.

    A claude.ai artifact belongs to one account, so an address written into
    this repository points every machine at a page that a machine signed in
    elsewhere cannot open. That is how the first board, and the three pages it
    linked to, were lost here on 2026-10-09. The board now lives on GitHub
    Pages, and nothing in the repository needs an artifact's address. The
    pattern is assembled from pieces so this file does not match itself.
    """
    host = re.escape("claude" + ".ai/")
    pattern = re.compile((host + r"(?:code/|public/)?" + "arti" + r"facts?/").encode())
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout
    hits = []
    for name in filter(None, listed.decode().split("\0")):
        path = REPO_ROOT / name
        if path.is_file() and pattern.search(path.read_bytes()):
            hits.append(name)
    assert hits == []


# A repository with no Pages site answers 404, and the real `gh` prints that
# error's JSON body to stdout and exits 1, skipping `--jq`. The fake does the
# same. A fake writing its error to stderr let a draft of the script pass here
# while it read that body as a source type, which a dry run against this
# repository caught.
FAKE_GH = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
case "$*" in
  *"repos/x/y/pages --jq .build_type"*)
    if [ -n "$PAGES_TYPE" ]; then echo "$PAGES_TYPE"; exit 0; fi
    echo '{"message":"Not Found","status":"404"}'
    echo "gh: Not Found (HTTP 404)" >&2
    exit 1 ;;
esac
exit 0
"""


@pytest.mark.parametrize(
    ("pages_type", "line", "write"),
    [
        ("", "pages: enabling, source GitHub Actions", "--method POST repos/x/y/pages"),
        (
            "legacy",
            "pages: switching source from legacy to GitHub Actions",
            "--method PUT repos/x/y/pages",
        ),
        ("workflow", "pages: already on, source GitHub Actions", None),
    ],
)
def test_the_setup_script_turns_pages_on_with_actions_as_its_source(
    tmp_path: Path, pages_type: str, line: str, write: str | None
) -> None:
    """Protects the deploy job, which has nowhere to go with Pages off.

    The script reads the site first, so a run against a repository that
    already has it set leaves it alone, and a dry run writes nothing.
    """
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "gh"
    fake.write_text(FAKE_GH)
    fake.chmod(0o755)
    log = tmp_path / "gh.log"
    env = {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "GH_LOG": str(log),
        "PAGES_TYPE": pages_type,
    }
    done = subprocess.run(
        ["bash", str(SETUP), "x/y"], env=env, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stderr
    assert line in done.stdout
    calls = log.read_text()
    if write:
        assert f"api {write}" in calls
        assert "build_type=workflow" in calls
    else:
        assert "--method POST repos/x/y/pages" not in calls
        assert "--method PUT repos/x/y/pages" not in calls

    dry = subprocess.run(
        ["bash", str(SETUP), "x/y"],
        env={**env, "DRY_RUN": "1", "GH_LOG": str(tmp_path / "dry.log")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert dry.returncode == 0, dry.stderr
    assert line in dry.stdout
    assert "--method" not in (tmp_path / "dry.log").read_text()
