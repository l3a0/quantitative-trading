"""The generator behind the build board on GitHub Pages, run on canned GitHub.

``scripts/build_board.py`` reads GitHub through GraphQL and writes the six
sections the board's page draws. Two failures matter more than any other here.

1. A board the page refuses. The page refuses a whole section when one item
   lacks a field it reads, so one pull request linking no issue, or one issue
   with no milestone, would blank the board.
2. A board that reads as correct and is not. A failing check passed through in
   GitHub's spelling read as green, a stranger's review comment would move a
   pull request into the owner's queue, and an error read as an empty list
   would publish a board with no pull requests.

Each test feeds the generator a fake GitHub that answers its queries from
fixtures, so nothing here touches the network. The last tests run the page on
what the generator wrote, and check the workflow and the setup script that
publish it.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from tests.test_build_board import (
    assert_no_board_data,
    cards,
    run_fetch_page,
    served,
    text,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "build_board.py"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "board.yml"
SETUP = REPO_ROOT / "scripts" / "setup-repo.sh"
REPO = "l3a0/quantitative-trading"
NOW = datetime(2026, 10, 11, 15, 0, tzinfo=UTC)

_spec = importlib.util.spec_from_file_location("build_board", SCRIPT)
bb = importlib.util.module_from_spec(_spec)
sys.modules["build_board"] = bb
_spec.loader.exec_module(bb)


def conn(nodes: list, *, more: bool = False, cursor: str = "c1") -> dict:
    """One page of a GraphQL connection."""
    return {"nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": cursor}}


def issue(
    n: int,
    *,
    title: str | None = None,
    milestone: str | None = "Chapter 7",
    labels: tuple[str, ...] = ("replication",),
    closed_by: tuple[int, ...] = (),
    mentioned_by: tuple[int, ...] = (),
) -> dict:
    return {
        "id": f"I{n}",
        "number": n,
        "title": title or f"Issue {n}",
        "milestone": {"title": milestone} if milestone is not None else None,
        "labels": conn([{"name": x} for x in labels]),
        "closedByPullRequestsReferences": conn([{"number": p} for p in closed_by]),
        "timelineItems": conn(
            [{"source": {"number": p, "repository": {"nameWithOwner": REPO}}} for p in mentioned_by]
        ),
    }


def check(name: str, conclusion: str | None, status: str = "COMPLETED") -> dict:
    return {"__typename": "CheckRun", "name": name, "status": status, "conclusion": conclusion}


def status(context: str, state: str) -> dict:
    return {"__typename": "StatusContext", "context": context, "state": state}


def pull(
    n: int,
    *,
    state: str = "OPEN",
    body: str = "",
    closes: tuple[int, ...] = (),
    comments: tuple[tuple[str, str], ...] = (),
    contexts: tuple[dict, ...] = (check("test", "SUCCESS"),),
    fork: bool = False,
) -> dict:
    return {
        "id": f"P{n}",
        "number": n,
        "state": state,
        "body": body,
        "isCrossRepository": fork,
        "closingIssuesReferences": conn([{"number": i} for i in closes]),
        "comments": conn([{"authorAssociation": a, "body": b} for a, b in comments]),
        "commits": {
            "nodes": [
                {"commit": {"statusCheckRollup": {"id": f"R{n}", "contexts": conn(list(contexts))}}}
            ]
        },
    }


class FakeGitHub:
    """Answers the generator's queries from fixtures, and records each call.

    Open issues and open pull requests are served in pages of the size the
    real queries ask for. A pull request asked for by number comes from
    ``prs``, whatever its state. ``nested`` serves the further pages of a
    nested list, keyed by the node's id and the list's name.
    """

    def __init__(self, issues: list[dict], prs: list[dict], nested: dict | None = None):
        self.issues = issues
        self.prs = {p["number"]: p for p in prs}
        self.nested = nested or {}
        self.calls: list[str] = []

    def _page(self, nodes: list[dict], size: int, after: str | None) -> dict:
        start = int(after) if after else 0
        chunk = nodes[start : start + size]
        end = start + size
        return {
            "totalCount": len(nodes),
            "nodes": chunk,
            "pageInfo": {"hasNextPage": end < len(nodes), "endCursor": str(end)},
        }

    def __call__(self, query: str, variables: dict) -> dict:
        self.calls.append(query)
        if "node(id:$id)" in query:
            # Keyed by the cursor too, so a read that asks for the first page
            # again finds nothing rather than looping on it.
            field = re.search(r"\{ (\w+)\(", query.split("... on", 1)[1]).group(1)
            return {"node": {field: self.nested[(variables["id"], field, variables["after"])]}}
        if "issues(states:OPEN" in query:
            page = self._page(self.issues, 100, variables.get("after"))
            return {"rateLimit": {"cost": 1}, "repository": {"issues": page}}
        if "pullRequests(states:OPEN" in query:
            open_prs = [p for p in self.prs.values() if p["state"] == "OPEN"]
            page = self._page(open_prs, 50, variables.get("after"))
            return {"rateLimit": {"cost": 1}, "repository": {"pullRequests": page}}
        found = {
            f"p{n}": self.prs.get(int(n)) for n in re.findall(r"pullRequest\(number:(\d+)", query)
        }
        return {"rateLimit": {"cost": 1}, "repository": found}


def build(gh: FakeGitHub) -> tuple[dict, dict]:
    return bb.build(gh, REPO, 60, NOW)


def prs_of(board: dict) -> list[dict]:
    return board["prs"]["items"]


# ---- What the page refuses ----


def test_a_pull_request_naming_no_open_issue_gets_no_item() -> None:
    """Protects the whole prs section from one branch with no card.

    8 of the last 60 pull requests on 2026-10-11 closed no issue and carried no
    ``Part of`` line, Dependabot's 434 among them. A null issue would make the
    page refuse every pull request, so such a branch gets no item and the job
    summary names it. A branch naming only a closed issue gets none either.
    """
    gh = FakeGitHub(
        [issue(10)],
        [pull(434, body="Bumps ruff."), pull(435, closes=(9,)), pull(436, closes=(10,))],
    )
    board, report = build(gh)
    assert [(p["pr"], p["issue"]) for p in prs_of(board)] == [(436, 10)]
    assert report["open_prs_left_out"] == [434, 435]


def test_a_pull_request_closing_two_issues_gets_an_item_for_each() -> None:
    """Protects the second card of a branch closing two issues.

    The page keys pull requests by issue, so one item would leave the other
    card with no branch. PR 473 closed 431 and 448.
    """
    gh = FakeGitHub([issue(431), issue(448)], [pull(473, closes=(431, 448))])
    board, _ = build(gh)
    assert [(p["pr"], p["issue"], p["linked"]) for p in prs_of(board)] == [
        (473, 431, True),
        (473, 448, True),
    ]
    assert all("partOf" not in p for p in prs_of(board))


def test_a_part_of_line_names_its_issue_and_prose_does_not() -> None:
    """Protects the ``Part of`` convention from prose that mentions one.

    PR 491's body named 462 on a line of its own and three other issues in
    sentences such as "merged in PR 488, part of 458". PR 485 quoted another
    pull request's line mid-sentence. Only a line opening with ``Part of``
    counts.
    """
    body = (
        "- The Entry 27 post merged in PR #488, part of #458.\n"
        "part of #458 was the earlier post.\n"
        'It merged in #478 as "Part of #459".\n'
        "\n"
        "Part of #462. The draft is created from the merged file.\n"
    )
    gh = FakeGitHub([issue(458), issue(459), issue(462)], [pull(491, body=body)])
    board, _ = build(gh)
    assert prs_of(board) == [
        {
            "pr": 491,
            "issue": 462,
            "state": "open",
            "linked": False,
            "reviewed": False,
            "review": "no review posted",
            "rollup": [["test", "success"]],
            "partOf": True,
        }
    ]


def test_a_merged_part_of_pull_request_stays_on_its_open_issue() -> None:
    """Protects the line saying what landed on an issue left open on purpose.

    A merged ``Part of`` pull request closes nothing, so GitHub's closing
    links never find it. The generator finds it through the issue's
    cross-references. A merged pull request that only mentions the issue in
    prose gets no item, and neither does a closed one naming nothing.
    """
    gh = FakeGitHub(
        [issue(463, mentioned_by=(490, 491, 492))],
        [
            pull(490, state="MERGED", body="Part of #463"),
            pull(491, state="MERGED", body="Its twin, from PR #490, part of #463."),
            pull(492, state="CLOSED", body="Tried #463 another way."),
        ],
    )
    board, report = build(gh)
    assert [(p["pr"], p["state"], p.get("partOf")) for p in prs_of(board)] == [
        (490, "merged", True)
    ]
    assert report["other_prs_read"] == 3
    assert report["open_prs_left_out"] == []


def test_a_merged_pull_request_whose_issue_stayed_open_reads_as_merged() -> None:
    """Protects the card held for a close by hand.

    A pull request merged with a closing link whose issue is still open has
    landed, and the page holds its card as needing only closing by hand. The
    issue's closing references are what find it.
    """
    gh = FakeGitHub([issue(352, closed_by=(479,))], [pull(479, state="MERGED", closes=(352,))])
    board, _ = build(gh)
    assert [(p["pr"], p["state"], p["linked"]) for p in prs_of(board)] == [(479, "merged", True)]


def test_an_issue_with_no_milestone_gets_an_empty_string() -> None:
    """Protects the tracker from an issue a stranger filed with no milestone.

    The page refuses a tracker item whose ``ms`` is not a string, which would
    blank the whole board.
    """
    board, _ = build(FakeGitHub([issue(7, milestone=None, labels=())], []))
    assert board["tracker"]["items"] == [
        {"n": 7, "ms": "", "label": "Issue 7", "kind": "ready", "needs": [], "labels": []}
    ]


def test_the_fields_issue_533_owns_are_written_empty_and_named() -> None:
    """Protects the page's refusal rules for the fields not on GitHub yet.

    Every card gets ``needs`` empty and ``kind`` ready, the three judgement
    sections are empty, and ``state`` names what the board does not carry so
    the banner can say so.
    """
    board, _ = build(FakeGitHub([issue(1), issue(2)], []))
    for name in ("working", "planned", "next"):
        assert board[name] == {"schema": 1, "items": []}
    assert {c["kind"] for c in board["tracker"]["items"]} == {"ready"}
    state = board["state"]
    assert state["updatedAt"] == "2026-10-11T15:00:00Z"
    assert state["issues"] == {"open": 2}
    assert state["staleAfterMinutes"] == 60
    assert state["lacks"] == bb.LACKS
    assert state["source"] == "github"


def test_a_pull_request_from_a_fork_gets_no_item() -> None:
    """Protects the free list from a stranger's branch.

    Anyone can open a pull request on a public repository, and one whose body
    says ``Part of`` an issue, or closes it, would otherwise draw a branch on
    that card. Dependabot's branches live here, so they still count.
    """
    gh = FakeGitHub(
        [issue(5), issue(6)],
        [
            pull(7, body="Part of #5", fork=True),
            pull(8, closes=(6,), fork=True),
            pull(9, closes=(6,)),
        ],
    )
    board, report = build(gh)
    assert [(p["pr"], p["issue"]) for p in prs_of(board)] == [(9, 6)]
    assert report["open_prs_left_out"] == [7, 8]


def test_a_cross_reference_from_another_repository_reads_nothing_here() -> None:
    """Protects the run from a sibling repository's pull request number.

    Issue 40 here is cross-referenced from pull requests in
    ``l3a0/ithildin-core`` and ``l3a0/trading-strategies``. Read by number,
    such a reference would fetch this repository's pull request of the same
    number, or stop the run when there is none.
    """
    first = issue(40)
    first["timelineItems"] = conn(
        [{"source": {"number": 999, "repository": {"nameWithOwner": "other/repo"}}}]
    )
    gh = FakeGitHub([first], [])
    board, report = build(gh)
    assert prs_of(board) == []
    assert report["other_prs_read"] == 0
    assert not any("pullRequest(number:999" in q for q in gh.calls)


def test_a_closed_part_of_pull_request_reads_as_closed() -> None:
    """Protects a card from reading as landed when its branch was abandoned.

    The page frees a card whose pull request closed unmerged, and holds one
    whose pull request merged with no ``Part of``. So the two states must stay
    apart.
    """
    gh = FakeGitHub([issue(5, mentioned_by=(6,))], [pull(6, state="CLOSED", body="Part of #5")])
    board, _ = build(gh)
    assert [(p["pr"], p["state"]) for p in prs_of(board)] == [(6, "closed")]


def test_an_open_pull_request_an_issue_also_references_gets_one_item() -> None:
    """Protects a card from drawing one branch twice.

    An open pull request is read with the open list and is also among the
    issue's cross-references, so it must not be read a second time by number.
    """
    gh = FakeGitHub([issue(5, closed_by=(6,), mentioned_by=(6,))], [pull(6, closes=(5,))])
    board, report = build(gh)
    assert [(p["pr"], p["issue"]) for p in prs_of(board)] == [(6, 5)]
    assert report["other_prs_read"] == 0


def test_a_pull_request_closing_one_issue_and_part_of_another_marks_only_the_second() -> None:
    """Protects the ``Part of`` mark from following whether anything else closes.

    The mark belongs to each issue the pull request names, so one that closes
    5 and is part of 6 leaves 5 to close on merge and 6 open on purpose.
    """
    gh = FakeGitHub([issue(5), issue(6)], [pull(7, closes=(5,), body="Part of #6")])
    board, _ = build(gh)
    assert [(p["issue"], p["linked"], p.get("partOf")) for p in prs_of(board)] == [
        (5, True, None),
        (6, False, True),
    ]


def test_each_check_is_labelled_with_its_own_name() -> None:
    """Protects the label of a status context, which carries no ``name``."""
    contexts = (check("test", "SUCCESS"), status("ci/legacy", "PENDING"))
    gh = FakeGitHub([issue(5)], [pull(6, closes=(5,), contexts=contexts)])
    board, _ = build(gh)
    assert prs_of(board)[0]["rollup"] == [["test", "success"], ["ci/legacy", "running"]]


def test_the_tracker_and_the_pull_requests_come_out_in_number_order() -> None:
    """Protects a board whose order does not depend on how GitHub listed it."""
    gh = FakeGitHub(
        [issue(9), issue(3), issue(5)],
        [pull(40, closes=(9,)), pull(30, closes=(3,)), pull(20, closes=(9,))],
    )
    board, _ = build(gh)
    assert [c["n"] for c in board["tracker"]["items"]] == [3, 5, 9]
    assert [(p["issue"], p["pr"]) for p in prs_of(board)] == [(3, 30), (9, 20), (9, 40)]


def test_a_pull_request_that_cannot_be_read_stops_the_run() -> None:
    """Protects the board from a reference GitHub answers with nothing."""
    gh = FakeGitHub([issue(5, mentioned_by=(77,))], [])
    with pytest.raises(bb.BoardError, match="pull request 77 could not be read"):
        build(gh)


def test_a_node_that_vanishes_mid_read_stops_the_run() -> None:
    """Protects a nested list from being cut short by a node that went away."""

    class Vanishing(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            if "node(id:$id)" in query:
                self.calls.append(query)
                return {"node": None}
            return super().__call__(query, variables)

    first = issue(5)
    first["labels"] = conn([], more=True, cursor="l1")
    with pytest.raises(bb.BoardError, match="Issue I5 vanished while reading its labels"):
        build(Vanishing([first], []))


# ---- Where reviewed comes from ----


@pytest.mark.parametrize(
    ("association", "body", "reviewed"),
    [
        ("OWNER", "## Review\n\nFour lenses ran.", True),
        ("OWNER", "\n## Review of the fixes\n", True),
        ("NONE", "## Review\n\nLooks good to me.", False),
        ("CONTRIBUTOR", "## Review\n", False),
        ("COLLABORATOR", "## Review\n", False),
        ("MEMBER", "## Review\n", False),
        ("OWNER", "## Reviewer notes\n", False),
        ("OWNER", "The review is below.\n## Review\n", False),
    ],
)
def test_only_the_owners_review_heading_counts(association: str, body: str, reviewed: bool) -> None:
    """Protects the owner's queue from a stranger's comment.

    Anyone can comment on a public repository, and a comment headed
    ``## Review`` is what moves a pull request toward the owner's column.
    """
    gh = FakeGitHub([issue(5)], [pull(6, closes=(5,), comments=((association, body),))])
    board, _ = build(gh)
    item = prs_of(board)[0]
    assert item["reviewed"] is reviewed
    assert item["review"] == ("review posted" if reviewed else "no review posted")


# ---- Check states ----


@pytest.mark.parametrize(
    ("context", "word"),
    [
        (check("t", "SUCCESS"), "success"),
        (check("t", "FAILURE"), "failure"),
        (check("t", "TIMED_OUT"), "failure"),
        (check("t", "CANCELLED"), "failure"),
        (check("t", "ACTION_REQUIRED"), "failure"),
        (check("t", "STARTUP_FAILURE"), "failure"),
        (check("t", "NEUTRAL"), "neutral"),
        (check("t", "SKIPPED"), "neutral"),
        (check("t", "STALE"), "neutral"),
        (check("t", None, status="IN_PROGRESS"), "running"),
        (check("t", None, status="QUEUED"), "running"),
        (check("t", "SUCCESS", status="IN_PROGRESS"), "running"),
        (status("t", "SUCCESS"), "success"),
        (status("t", "FAILURE"), "failure"),
        (status("t", "ERROR"), "failure"),
        (status("t", "PENDING"), "running"),
        (status("t", "EXPECTED"), "running"),
    ],
)
def test_every_check_state_maps_to_one_of_the_pages_four_words(context: dict, word: str) -> None:
    """Protects a failing check from reading as green.

    The heads of the last 60 pull requests carried 355 ``SUCCESS``, 1
    ``NEUTRAL`` and 1 ``IN_PROGRESS``, so the common case hides a state passed
    through unmapped.
    """
    unknown: set[str] = set()
    assert bb.check_word(context, unknown) == word
    assert unknown == set()


def test_a_check_state_github_adds_later_is_neither_way_and_reported() -> None:
    gh = FakeGitHub([issue(5)], [pull(6, closes=(5,), contexts=(check("t", "SOMETHING_NEW"),))])
    board, report = build(gh)
    assert prs_of(board)[0]["rollup"] == [["t", "neutral"]]
    assert report["unknown_check_states"] == ["SOMETHING_NEW"]


def test_a_head_with_no_checks_has_an_empty_rollup() -> None:
    """Protects a conflicting pull request, which gets no run at all."""
    pr = pull(6, closes=(5,))
    pr["commits"]["nodes"][0]["commit"]["statusCheckRollup"] = None
    board, _ = build(FakeGitHub([issue(5)], [pr]))
    assert prs_of(board)[0]["rollup"] == []


# ---- Requests and pagination ----


def test_one_run_makes_a_request_per_page_and_no_more() -> None:
    """Protects the request budget a busy hour spends.

    The busiest hour on 2026-10-10 carried 128 issue events, and
    ``GITHUB_TOKEN`` allows 1,000 REST requests an hour per repository. A
    generator reading per issue would spend more than one request for each of
    116 open issues. Here 150 open issues take two pages, 60 open pull requests
    take two, and 55 merged pull requests named by those issues take two
    batches of 50, so one run makes six requests whatever the issues hold.
    """
    issues = [issue(n, mentioned_by=(1000 + n,) if n < 55 else ()) for n in range(150)]
    prs = [pull(2000 + n, closes=(n,)) for n in range(60)]
    prs += [pull(1000 + n, state="MERGED", body=f"Part of #{n}") for n in range(55)]
    gh = FakeGitHub(issues, prs)
    board, _ = build(gh)
    assert len(gh.calls) == 6
    assert len(board["tracker"]["items"]) == 150
    assert len(prs_of(board)) == 115


def test_a_nested_list_longer_than_a_page_is_read_to_its_end() -> None:
    """Protects a list GitHub cut at its page size.

    An issue named by more than 100 pull requests, or a pull request with more
    than 100 comments, would otherwise lose the rest silently. Each further
    page is one more request, and each asks for the page after the last one
    read. The comments take three pages, so a read that restarts from the
    first finds no page there and stops.
    """
    first = issue(5)
    first["timelineItems"] = conn([], more=True, cursor="t1")
    pr = pull(6, state="MERGED", body="Part of #5")
    pr["comments"] = conn([], more=True, cursor="k1")
    nested = {
        ("I5", "timelineItems", "t1"): conn(
            [{"source": {"number": 6, "repository": {"nameWithOwner": REPO}}}]
        ),
        ("P6", "comments", "k1"): conn([], more=True, cursor="k2"),
        ("P6", "comments", "k2"): conn([{"authorAssociation": "OWNER", "body": "## Review\n"}]),
    }
    gh = FakeGitHub([first], [pr], nested)
    board, _ = build(gh)
    assert [(p["pr"], p["reviewed"]) for p in prs_of(board)] == [(6, True)]
    assert sum("node(id:$id)" in q for q in gh.calls) == 3


def test_a_count_that_disagrees_with_the_pages_read_stops_the_run() -> None:
    """Protects the board from a list that changed while it was read."""

    class Shifting(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "issues(states:OPEN" in query:
                data["repository"]["issues"]["totalCount"] += 1
            return data

    with pytest.raises(bb.BoardError, match="read 1 issues against a total of 2"):
        build(Shifting([issue(1)], []))


def test_an_issue_read_twice_stops_the_run() -> None:
    """Protects the count from a page that repeats an issue another dropped."""

    class Repeating(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "issues(states:OPEN" in query:
                data["repository"]["issues"]["nodes"] = [issue(1), issue(1)]
            return data

    with pytest.raises(bb.BoardError, match="read 2 issues against a total of 2"):
        build(Repeating([issue(1), issue(2)], []))


def test_a_variable_with_no_value_is_left_out_of_the_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Protects the first page of every list, which asks for no cursor.

    GraphQL reads a variable left out as null. Sent as text, it would arrive
    as the cursor "None", which GitHub refuses.
    """
    seen: list[list[str]] = []

    def run(args: list[str], **_: object) -> subprocess.CompletedProcess:
        seen.append(args)
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps({"data": {}}), stderr="")

    monkeypatch.setattr(bb.subprocess, "run", run)
    bb.GhGraphql()("query { viewer { login } }", {"owner": "l3a0", "first": 3, "after": None})
    args = seen[0]
    assert args[args.index("-f", 4) :] == ["-f", "owner=l3a0", "-F", "first=3"]


@pytest.mark.parametrize(
    ("returncode", "stdout", "message"),
    [
        (1, "", "gh api graphql failed"),
        (0, "not json", "returned no JSON"),
        (0, json.dumps({"errors": [{"message": "rate limited"}]}), "GraphQL errors"),
        (0, json.dumps({"data": None}), "returned no data"),
    ],
)
def test_a_failed_read_fails_the_run(
    monkeypatch: pytest.MonkeyPatch, returncode: int, stdout: str, message: str
) -> None:
    """Protects the last good board from a read that went wrong.

    An error read as an empty list publishes a board with no pull requests,
    which reads as correct. So every failure stops the run, and the last good
    board stays up.
    """
    done = subprocess.CompletedProcess([], returncode, stdout=stdout, stderr="")
    monkeypatch.setattr(bb.subprocess, "run", lambda *a, **k: done)
    with pytest.raises(bb.BoardError, match=message):
        bb.GhGraphql()("query { viewer { login } }", {})


def test_the_cli_exits_non_zero_when_github_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    done = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP 502")
    monkeypatch.setattr(bb.subprocess, "run", lambda *a, **k: done)
    argv = ["build", "--repo", REPO, "--workflow", str(WORKFLOW), "--out", str(tmp_path)]
    assert bb.main(argv) == 1
    assert not (tmp_path / "board.json").exists()


# ---- The stale threshold ----


def test_the_stale_threshold_is_twice_the_workflows_longest_gap() -> None:
    """Protects the page's stale warning from a second copy of the schedule."""
    assert bb.stale_after_minutes(WORKFLOW) == 60


@pytest.mark.parametrize(
    ("cron", "minutes"),
    [("*/15 * * * *", 30), ("0 * * * *", 120), ("5,15 * * * *", 100)],
)
def test_the_threshold_follows_the_schedule(tmp_path: Path, cron: str, minutes: int) -> None:
    workflow = tmp_path / "board.yml"
    workflow.write_text(f'on:\n  schedule:\n    - cron: "{cron}"\n')
    assert bb.stale_after_minutes(workflow) == minutes


@pytest.mark.parametrize(
    "lines",
    [
        '    - cron: "0 */2 * * *"\n',
        '    - cron: "60 * * * *"\n',
        '    - cron: "0 * * * 1"\n',
        '    - cron: "7 * * * *"\n    - cron: "37 * * * *"\n',
        "",
    ],
)
def test_a_schedule_it_cannot_read_stops_the_run(tmp_path: Path, lines: str) -> None:
    workflow = tmp_path / "board.yml"
    workflow.write_text("on:\n  schedule:\n" + lines)
    with pytest.raises(bb.BoardError):
        bb.stale_after_minutes(workflow)


# ---- The page, on what the generator wrote ----


def test_the_page_draws_what_the_generator_writes(tmp_path: Path) -> None:
    """Protects the join between the two halves.

    A field the generator leaves out, or writes in a shape the page refuses,
    blanks the board, and neither half's own tests would notice. So the page
    runs on the generator's output, built from a tracker holding every case
    above at once.
    """
    gh = FakeGitHub(
        [
            issue(10, mentioned_by=(20,)),
            issue(11, milestone=None, labels=()),
            issue(12),
            issue(13),
        ],
        [
            pull(20, state="MERGED", body="Part of #10"),
            pull(21, closes=(11, 12), comments=(("OWNER", "## Review\n"),)),
            pull(22, body="Bumps a dependency."),
            pull(23, closes=(13,), contexts=(check("test", "TIMED_OUT"),)),
        ],
    )
    board, _ = build(gh)
    board["state"]["updatedAt"] = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert text(ids, "strip").startswith("4 open issues")
    assert text(ids, "source").startswith("Built from GitHub alone. This board does not carry")
    assert cards(ids, "flow") == {11, 12, 13}
    assert "1 check failing" in text(ids, "flow")


def test_a_board_with_no_open_issues_draws_nothing(tmp_path: Path) -> None:
    """Protects the page's refusal of an empty tracker, which it keeps."""
    board, _ = build(FakeGitHub([], []))
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert "tracker section is missing fields" in text(ids, "source")
    assert_no_board_data(ids)


# ---- The workflow ----


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_no_step_reads_the_event_payload() -> None:
    """Protects the run steps from an issue title written as shell.

    Anyone can file an issue on a public repository, and CodeQL rates an event
    field expanded into a step as critical, which the ruleset refuses to merge.
    Fields such as ``github.head_ref`` carry a stranger's text without naming
    the event, so the workflow may use only the expressions listed here, none
    of which a stranger writes.
    """
    used = set(re.findall(r"\$\{\{\s*([^}]*?)\s*\}\}", _workflow()))
    assert used == {
        "github.token",
        "steps.board.outputs.updated_at",
        "steps.deployment.outputs.page_url",
        "needs.build.outputs.updated_at",
    }


def test_nothing_checks_out_a_pull_requests_code() -> None:
    """Protects the write token ``pull_request_target`` runs with."""
    flow = _workflow()
    assert flow.count("uses: actions/checkout@") == 2
    assert not re.search(r"^\s+ref:", flow, re.M)
    assert flow.count("persist-credentials: false") == 2


def test_the_triggers_are_the_ones_that_can_deploy() -> None:
    """Protects the deploy, which only the default branch may make.

    ``pull_request`` and ``pull_request_review`` run on a merge ref, which the
    github-pages environment refuses. ``pull_request_target`` needs ``closed``
    and ``edited`` listed, or a merged ``Part of`` pull request and a corrected
    closing link wait for the cron run. It runs on a pull request's base
    branch, so it admits only pull requests into ``main``.
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


def test_each_job_declares_only_the_scopes_it_uses() -> None:
    """Protects the build from a starved token and the deploy from a broad one.

    Declaring any scope sets every unlisted one to none, so the build job
    lists each scope the generator reads.
    """
    flow = _workflow()
    assert "\npermissions: {}\n" in flow
    jobs = flow.split("\njobs:\n", 1)[1]
    build_job, deploy_job = jobs.split("\n  deploy:\n", 1)

    def scopes(job: str) -> dict[str, str]:
        block = job.split("    permissions:\n", 1)[1].split("\n    outputs:", 1)[0]
        block = block.split("\n    environment:", 1)[0]
        return dict(re.findall(r"^      ([\w-]+): (\w+)$", block, re.M))

    assert scopes(build_job) == {
        "contents": "read",
        "issues": "read",
        "pull-requests": "read",
        "checks": "read",
        "statuses": "read",
    }
    assert scopes(deploy_job) == {
        "pages": "write",
        "id-token": "write",
        "contents": "read",
        "actions": "read",
    }
    assert "name: github-pages" in deploy_job


def test_runs_deploy_one_at_a_time_and_none_is_cancelled() -> None:
    """Protects a newer board from an older run deploying over it."""
    assert "concurrency:\n  group: pages\n  cancel-in-progress: false\n" in _workflow()


def test_every_successful_build_deploys() -> None:
    """Protects the stale warning from a skipped deploy.

    A deploy skipped because the board matched the last one would freeze its
    stamp, and the page would then call a current board stale. So the deploy
    job waits on the build and carries no condition of its own.
    """
    deploy = _workflow().split("\n  deploy:\n", 1)[1]
    assert "    needs: build\n" in deploy
    assert not re.search(r"^\s+if:", deploy, re.M)
    assert not re.search(r"^\s+if:", _workflow(), re.M)


def test_the_measure_step_holds_the_pages_group_for_a_minute_at_most() -> None:
    """Protects the next run from waiting on a measurement.

    The whole run holds the ``pages`` concurrency group, so the next board
    waits for the measure step to finish polling.
    """
    measure = _workflow().split("- name: Measure delivery", 1)[1]
    assert "--wait 60" in measure
    assert "timeout=10" in SCRIPT.read_text(encoding="utf-8")


def test_the_page_published_is_the_checked_in_one() -> None:
    """Protects the one page both boards publish."""
    flow = _workflow()
    assert "cp .claude/skills/update-build-board/board.html _site/index.html" in flow
    assert "--workflow .github/workflows/board.yml" in flow


# ---- The setup script ----


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
