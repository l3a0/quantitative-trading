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
    PAGE,
    SKILL_DIR,
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
    body: str = "",
    blocked_by: tuple[tuple, ...] = (),
    sub_issues: int = 0,
    comments: tuple[tuple[str, str], ...] = (),
) -> dict:
    return {
        "id": f"I{n}",
        "number": n,
        "title": title or f"Issue {n}",
        "body": body,
        "milestone": {"title": milestone} if milestone is not None else None,
        "labels": conn([{"name": x} for x in labels]),
        "blockedBy": conn([blocker(*b) for b in blocked_by]),
        "subIssues": {"totalCount": sub_issues},
        "issueComments": conn([{"authorAssociation": a, "body": b} for a, b in comments]),
        "closedByPullRequestsReferences": conn([{"number": p} for p in closed_by]),
        "timelineItems": conn(
            [{"source": {"number": p, "repository": {"nameWithOwner": REPO}}} for p in mentioned_by]
        ),
    }


def blocker(n: int, state: str, repo: str = REPO) -> dict:
    """One "blocked by" link, to an issue in ``repo``."""
    return {"number": n, "state": state, "repository": {"nameWithOwner": repo}}


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
            field = re.search(r"\{ (\w+): \w+\(", query.split("... on", 1)[1]).group(1)
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
    return bb.build(gh, REPO, 30, NOW)


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


@pytest.mark.parametrize(
    ("body", "credited"),
    [
        # Line start, as most bodies write it.
        ("Part of #482. The rest of the issue stays open.\n", True),
        # Mid-paragraph, as PR 481 wrote it for 482.
        ("This writes the post. Part of #482. The draft follows it.\n", True),
        # Inside a code span that crosses a line, so the phrase opens a line.
        ("The form reads `a body writes\nPart of #482 on a line`, as shown.\n", False),
        # Inside a fenced code block. The blank line in it ends a paragraph, so
        # only the fence rule, and not the code span rule, keeps it out.
        ("The form reads:\n\n```text\nA body:\n\nPart of #482\n```\n", False),
        # A backtick inside a fence and one after it. Fences come out before
        # spans, so the two never pair and swallow the reference between them.
        ("~~~\na ` b\n~~~\nPart of #482 and a ` tick.\n", True),
        # A paragraph ahead of the reference. Paragraphs rejoin with a
        # separator, so the reference does not run into the word before it.
        ("First paragraph\n\nPart of #482", True),
        # A span on each side. Scanning resumes after a span's closing run, so
        # that run does not open a second span reaching the reference.
        ("`x` Part of #482 `y`", True),
    ],
    ids=[
        "line-start",
        "mid-paragraph",
        "code-span",
        "fence",
        "fence-then-tick",
        "paragraphs",
        "two-spans",
    ],
)
def test_a_part_of_reference_counts_anywhere_outside_code(body: str, credited: bool) -> None:
    """Protects the ``Part of`` rule the owner chose on issue 559.

    A reference counts anywhere in a body outside a code span or a fenced code
    block, the way GitHub reads a closing keyword. PR 481 wrote the phrase
    mid-paragraph for 482, and a rule reading only a line opening with it gave
    that branch no item. The code span here crosses a line, and the fence holds
    the phrase on a line of its own, so the earlier rule would have credited
    both.
    """
    gh = FakeGitHub([issue(482)], [pull(481, body=body)])
    board, _ = build(gh)
    expected = [(481, 482, False, True)] if credited else []
    assert [(p["pr"], p["issue"], p["linked"], p.get("partOf")) for p in prs_of(board)] == expected


def test_a_part_of_reference_after_a_fence_counts_in_a_crlf_body() -> None:
    """Protects the ``Part of`` rule on a body saved from GitHub's web editor.

    That editor ends each line with ``\\r\\n``. Read as it comes, the closing
    fence never matches, so the fence runs on to the end of the body and takes
    the reference below it, and no blank line ends a paragraph either. The body
    here holds a fence ahead of a reference outside it, which must count.
    """
    body = "## What\r\n\r\n```\r\ncode\r\n```\r\n\r\nPart of #482\r\n"
    gh = FakeGitHub([issue(482)], [pull(481, body=body)])
    board, _ = build(gh)
    assert [(p["pr"], p["issue"], p.get("partOf")) for p in prs_of(board)] == [(481, 482, True)]


@pytest.mark.parametrize(
    ("body", "credited"),
    [
        # A run of one backtick closes only at a run of one, so the two runs of
        # two inside it are code and the reference with them.
        ("`a`` Part of #482 ``b`", False),
        # A run nothing closes is literal text.
        ("A stray ` backtick, then Part of #482.", True),
        # A code span ends with its paragraph, so a backtick in each of two
        # paragraphs opens no span between them.
        ("A stray ` here.\n\nPart of #482, and another ` there.\n", True),
        # A span removed leaves a separator, so the words either side of it do
        # not join into the phrase.
        ("Part `x`of #482", False),
        # The same with no space on either side. GitHub shows code between the
        # words, so the separator must not be the space the phrase needs.
        ("Part`x`of #482", False),
        # A run of two nothing closes. Scanning goes on past it, and not from
        # inside it, so the span after it still holds the reference.
        ("A `` stray pair, then `Part of #482`.", False),
        # A line of only spaces ends a paragraph as an empty line does.
        ("A stray ` here.\n \nPart of #482, and another ` there.\n", True),
    ],
    ids=["width", "unclosed", "paragraph", "joined", "no-space", "stray-pair", "spaces-line"],
)
def test_a_code_span_closes_only_on_a_run_of_its_own_width(body: str, credited: bool) -> None:
    """Protects the reference from a span read wider or narrower than GitHub reads it.

    CommonMark closes a code span at the next run of exactly as many backticks
    in the same paragraph, and leaves a run nothing closes as literal text.
    Reading any run as a closer, or a lone backtick as opening to the end of
    the body, would drop a reference GitHub shows as plain text.
    """
    gh = FakeGitHub([issue(482)], [pull(481, body=body)])
    board, _ = build(gh)
    assert [(p["pr"], p["issue"]) for p in prs_of(board)] == ([(481, 482)] if credited else [])


@pytest.mark.parametrize(
    "body",
    ["XPart of #482", "Part of #482abc", "Part of 482", "Part of # 482"],
    ids=["word-before", "word-after", "no-hash", "hash-space"],
)
def test_a_part_of_reference_is_the_whole_phrase_and_nothing_between(body: str) -> None:
    """Protects the ``Part of`` rule from text that only contains the phrase.

    The phrase starts and ends on a word boundary, and the number follows its
    ``#`` with nothing between. Text joining a word to either end, or dropping
    the ``#`` or spacing it from the number, is not the reference GitHub
    renders as a link.
    """
    gh = FakeGitHub([issue(482)], [pull(481, body=body)])
    board, _ = build(gh)
    assert prs_of(board) == []


def test_lowercase_prose_naming_an_issue_is_no_part_of_reference() -> None:
    """Protects the ``Part of`` rule from prose that names another issue.

    PR 491's body named 462 with the phrase and three other issues in
    sentences such as "merged in PR 488, part of 458". Lowercase prose is not
    a reference. A capitalised quotation of another pull request's line is
    one, as PR 485's was, and that is the price the owner accepted on issue
    559: a sentence mentioning the phrase counts unless a code span holds it.
    """
    body = (
        "- The Entry 27 post merged in PR #488, part of #458.\n"
        "part of #458 was the earlier post.\n"
        'It merged in #478 as "Part of #459".\n'
        "It also merged in #479 as `Part of #460`.\n"
        "\n"
        "Part of #462. The draft is created from the merged file.\n"
    )
    gh = FakeGitHub([issue(458), issue(459), issue(460), issue(462)], [pull(491, body=body)])
    board, _ = build(gh)
    assert [p["issue"] for p in prs_of(board)] == [459, 462]
    assert prs_of(board)[1] == {
        "pr": 491,
        "issue": 462,
        "state": "open",
        "linked": False,
        "reviewed": False,
        "review": "no review posted",
        "rollup": [["test", "success"]],
        "partOf": True,
    }


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


def test_an_issue_with_no_judgement_set_reads_as_a_plain_card() -> None:
    """Protects the page's refusal rules on an issue nobody has ranked.

    A card with no labels, links or lines of the board's own is ready, waits on
    nothing, and appears in none of the three judgement sections. ``state``
    carries no list of missing fields, because the board now carries them all.
    """
    board, _ = build(FakeGitHub([issue(1), issue(2)], []))
    for name in ("working", "planned", "next"):
        assert board[name] == {"schema": 1, "items": []}
    assert {c["kind"] for c in board["tracker"]["items"]} == {"ready"}
    assert all(c["needs"] == [] and "after" not in c for c in board["tracker"]["items"])
    state = board["state"]
    assert state["updatedAt"] == "2026-10-11T15:00:00Z"
    assert state["issues"] == {"open": 2}
    assert state["longestGapMinutes"] == 30
    assert state["staleAfterMinutes"] == 630
    assert "lacks" not in state
    assert state["source"] == "github"


# ---- The judgement fields, from labels, links and lines ----


def card(board: dict, n: int) -> dict:
    return next(c for c in board["tracker"]["items"] if c["n"] == n)


@pytest.mark.parametrize(
    ("labels", "subs", "kind"),
    [
        ((), 0, "ready"),
        (("question",), 0, "ready"),
        (("decision",), 0, "decision"),
        (("deferred",), 0, "deferred"),
        (("blocked-on-data",), 0, "data"),
        (("deferred", "decision"), 0, "deferred"),
        (("blocked-on-data", "deferred"), 0, "data"),
        (("blocked-on-data",), 3, "parent"),
        ((), 1, "parent"),
    ],
)
def test_a_cards_kind_comes_from_its_labels_and_sub_issues(
    labels: tuple[str, ...], subs: int, kind: str
) -> None:
    """Protects the kind word and the column a card's kind decides.

    ``question`` is not ``decision``, because an issue can carry it while it
    waits on research rather than on the owner. Any sub-issue makes a parent,
    open or closed, which is how issue 16 reads with its three children closed.
    """
    board, _ = build(FakeGitHub([issue(1, labels=labels, sub_issues=subs)], []))
    assert card(board, 1)["kind"] == kind


def test_needs_keeps_only_blockers_that_are_open_issues() -> None:
    """Protects a card from waiting on work that has landed.

    A "blocked by" link outlives its blocker closing, as issues 359 and 365
    showed on 2026-10-11, and the page draws only open issues. So a closed
    blocker, or one that is not an open issue here, drops out.
    """
    gh = FakeGitHub(
        [
            issue(1),
            issue(2, blocked_by=((1, "OPEN"), (3, "CLOSED"), (9, "OPEN"))),
        ],
        [],
    )
    board, _ = build(gh)
    assert card(board, 2)["needs"] == [1]
    assert card(board, 1)["needs"] == []


def test_a_blocker_in_another_repository_is_not_this_repositorys_issue() -> None:
    """Protects a card from waiting on an issue that shares only a number.

    A "blocked by" link can name an issue in any repository, and issue 1 in a
    sibling repository is not issue 1 here.
    """
    gh = FakeGitHub([issue(1), issue(2, blocked_by=((1, "OPEN", "l3a0/trading-strategies"),))], [])
    board, _ = build(gh)
    assert card(board, 2)["needs"] == []


def test_lines_inside_a_fenced_block_are_not_read() -> None:
    """Protects the board from a comment or body quoting the formats.

    A skill or a review that shows the verdict line in a fence is explaining
    it, not recording one.
    """
    fenced = "The format:\n\n```text\nBoard verdict: build after 5 passes\n```\n"
    body = "```\nBoard order: 3\nBoard after: #1\n```\n"
    gh = FakeGitHub(
        [issue(1), issue(2, labels=("band:1",), body=body, comments=(("OWNER", fenced),))], []
    )
    board, _ = build(gh)
    assert board["planned"]["items"] == []
    assert board["next"]["items"] == [{"issue": 2, "band": 1, "ready": "plan"}]
    assert "after" not in card(board, 2)


def test_an_issue_claiming_two_kinds_is_reported() -> None:
    """Protects a kind label that loses from going unnoticed."""
    gh = FakeGitHub(
        [
            issue(1, labels=("deferred", "blocked-on-data")),
            issue(2, labels=("decision",), sub_issues=1),
        ],
        [],
    )
    board, report = build(gh)
    assert [c["kind"] for c in board["tracker"]["items"]] == ["data", "parent"]
    assert report["label_conflicts"] == [
        "#1 reads as data and deferred, read as data",
        "#2 reads as parent and decision, read as parent",
    ]


@pytest.mark.parametrize(
    "body",
    [
        "Note: Board verdict: build after 5 passes",
        "Board verdict: build after 5 passes, and then some",
    ],
)
def test_a_verdict_line_must_stand_alone(body: str) -> None:
    """Protects the plan marker from prose that mentions the format."""
    board, _ = build(FakeGitHub([issue(1, comments=(("OWNER", body),))], []))
    assert board["planned"]["items"] == []


@pytest.mark.parametrize(
    "body",
    [
        "See Board order: 3\nBoard after: #2\n",
        "Board order: 3 or so\nNot Board after: #2\n",
    ],
)
def test_order_and_after_lines_must_stand_alone(body: str) -> None:
    """Protects the sort from a sentence that quotes a board line mid-way."""
    gh = FakeGitHub([issue(1, labels=("band:1",), body=body), issue(2)], [])
    board, _ = build(gh)
    entry = board["next"]["items"][0]
    assert "order" not in entry
    if body.startswith("See"):
        assert card(board, 1)["after"] == [2]
    else:
        assert "after" not in card(board, 1)


@pytest.mark.parametrize("label", ["old-band:1", "band:1-old"])
def test_only_a_whole_band_label_ranks_a_card(label: str) -> None:
    """Protects the priority order from a label that only contains a band."""
    board, _ = build(FakeGitHub([issue(1, labels=(label,))], []))
    assert board["next"]["items"] == []
    assert card(board, 1)["labels"] == [label]


def test_after_names_neither_the_card_itself_nor_a_bare_number() -> None:
    """Protects a card from sorting below itself, or below a stray digit."""
    gh = FakeGitHub([issue(1), issue(2), issue(5, body="Board after: #5, 1, #2\n")], [])
    board, _ = build(gh)
    assert card(board, 5)["after"] == [2]


def test_the_job_summary_lists_what_disagrees(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protects the one place a conflict is reported, since it does not fail the run."""
    fake = FakeGitHub([issue(1, labels=("band:1", "band:3"))], [])
    fake.requests, fake.cost = 1, 1
    monkeypatch.setattr(bb, "GhGraphql", lambda: fake)
    summary = tmp_path / "summary.md"
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(summary))
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    out = tmp_path / "site"
    assert bb.main(["build", "--repo", REPO, "--workflow", str(WORKFLOW), "--out", str(out)]) == 0
    assert (
        "| Labels or lines that disagree | #1 carries 2 band labels, read as band:1 |"
        in summary.read_text()
    )


def test_after_comes_from_its_line_and_keeps_open_issues() -> None:
    """Protects a measured ordering from prose that only mentions a number."""
    body = "Waits on nothing.\n\nBoard after: #1, #3 and #2\nSee #4 too.\n"
    gh = FakeGitHub([issue(1), issue(2), issue(5, body=body)], [])
    board, _ = build(gh)
    assert card(board, 5)["after"] == [1, 2]
    assert "after" not in card(board, 1)


def test_a_band_label_puts_the_card_in_the_priority_order() -> None:
    """Protects the default view, which draws only the cards ``next`` names.

    The order line takes a decimal, because the artifact board ordered cards
    at 14.05 and 14.85, and an order written as a whole number stays one.
    """
    gh = FakeGitHub(
        [
            issue(1, labels=("band:3",), body="Board order: 14.05\n"),
            issue(2, labels=("band:1",), body="Board order: 22\n"),
            issue(3, labels=("band:5",)),
            issue(4),
        ],
        [],
    )
    board, _ = build(gh)
    assert board["next"]["items"] == [
        {"issue": 1, "band": 3, "ready": "plan", "order": 14.05},
        {"issue": 2, "band": 1, "ready": "plan", "order": 22},
        {"issue": 3, "band": 5, "ready": "plan"},
    ]


def test_the_boards_own_labels_are_left_off_the_cards_chips() -> None:
    """Protects a card from drawing its rank and its session twice."""
    labels = ("replication", "band:1", "working:build", "decision")
    board, _ = build(FakeGitHub([issue(1, labels=labels)], []))
    assert card(board, 1)["labels"] == ["replication", "decision"]


@pytest.mark.parametrize(
    ("labels", "comments", "ready"),
    [
        (("band:1",), (), "plan"),
        (("band:1", "decision"), (), "decide"),
        (("band:1",), (("OWNER", "## Verdict\n\nBoard verdict: build after 5 passes\n"),), "build"),
        (("band:1", "decision"), (("OWNER", "Board verdict: build after 1 pass"),), "build"),
        (("band:1",), (("OWNER", "Board verdict: decide after 3 passes."),), "decide"),
        (("band:1",), (("NONE", "Board verdict: build after 5 passes"),), "plan"),
    ],
)
def test_a_ranked_cards_readiness_comes_from_its_verdict_then_its_kind(
    labels: tuple[str, ...], comments: tuple[tuple[str, str], ...], ready: str
) -> None:
    """Protects the sort, which reads ``ready`` after the band and the order."""
    board, _ = build(FakeGitHub([issue(1, labels=labels, comments=comments)], []))
    assert board["next"]["items"][0]["ready"] == ready


@pytest.mark.parametrize(
    ("comments", "planned"),
    [
        (
            (("OWNER", "## Decompose verdict\n\nBoard verdict: build after 5 passes\n"),),
            (5, "build"),
        ),
        (
            (
                ("OWNER", "Board verdict: build after 5 passes"),
                ("OWNER", "Board verdict: decide after 7 passes"),
            ),
            (7, "decide"),
        ),
        ((("CONTRIBUTOR", "Board verdict: build after 5 passes"),), None),
        ((("COLLABORATOR", "Board verdict: build after 5 passes"),), None),
        ((("MEMBER", "Board verdict: build after 5 passes"),), None),
        ((("OWNER", "The line `Board verdict: build after 5 passes` goes here."),), None),
        ((("OWNER", "Board verdict: ready after 5 passes"),), None),
    ],
)
def test_only_the_owners_newest_verdict_line_plans_a_card(
    comments: tuple[tuple[str, str], ...], planned: tuple[int, str] | None
) -> None:
    """Protects the plan marker from a stranger's comment and from prose.

    Anyone can comment on a public repository. A loop run again writes a new
    verdict, so the newest wins, and a line quoted inside a sentence is not one.
    """
    board, _ = build(FakeGitHub([issue(1, comments=comments)], []))
    items = board["planned"]["items"]
    if planned is None:
        assert items == []
    else:
        assert items == [{"n": 1, "passes": planned[0], "ready": planned[1]}]


def test_a_working_label_marks_the_session_on_the_card() -> None:
    """Protects the columns a session holds a card in, and the review word.

    A build session's open branch reads "review in progress" until its review
    is posted, as the artifact board wrote it, and a branch nobody holds reads
    "no review posted".
    """
    gh = FakeGitHub(
        [
            issue(1, labels=("working:build",)),
            issue(2, labels=("working:decompose",)),
            issue(3),
        ],
        [pull(10, closes=(1,)), pull(11, closes=(3,))],
    )
    board, _ = build(gh)
    assert board["working"]["items"] == [{"n": 1, "kind": "build"}, {"n": 2, "kind": "decompose"}]
    assert {p["pr"]: p["review"] for p in prs_of(board)} == {
        10: "review in progress",
        11: "no review posted",
    }


def test_labels_that_disagree_take_one_value_and_are_reported() -> None:
    """Protects the board from freezing on one stray label.

    Two bands take the lower, both session labels take ``build``, and two order
    lines take the first, and the job summary lists each.
    """
    gh = FakeGitHub(
        [
            issue(
                1,
                labels=("band:3", "band:1", "working:decompose", "working:build"),
                body="Board order: 4\nBoard order: 9\n",
            )
        ],
        [],
    )
    board, report = build(gh)
    assert board["next"]["items"] == [{"issue": 1, "band": 1, "ready": "plan", "order": 4}]
    assert board["working"]["items"] == [{"n": 1, "kind": "build"}]
    assert report["label_conflicts"] == [
        "#1 carries both working labels, read as build",
        "#1 carries 2 band labels, read as band:1",
        "#1 carries 2 order lines, read as 4",
    ]


def test_an_issues_comments_and_blockers_are_read_to_their_end() -> None:
    """Protects a verdict or a blocker past the first hundred.

    An issue's comments go under an alias, because a pull request's comments
    share the name, and the further pages must ask for the issue's.
    """
    first = issue(5, labels=("band:2",))
    first["issueComments"] = conn([], more=True, cursor="c1")
    first["blockedBy"] = conn([], more=True, cursor="b1")
    nested = {
        ("I5", "issueComments", "c1"): conn(
            [{"authorAssociation": "OWNER", "body": "Board verdict: build after 2 passes"}]
        ),
        ("I5", "blockedBy", "b1"): conn([blocker(6, "OPEN")]),
    }
    gh = FakeGitHub([first, issue(6)], [], nested)
    board, _ = build(gh)
    assert card(board, 5)["needs"] == [6]
    assert board["planned"]["items"] == [{"n": 5, "passes": 2, "ready": "build"}]
    paged = [q for q in gh.calls if "node(id:$id)" in q]
    assert any("issueComments: comments(" in q for q in paged)


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


def test_a_count_that_disagrees_with_the_pages_read_stops_the_run(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Protects the board from a read that disagrees with its count on every read.

    A list GitHub cut short would disagree this way on every read. The list is
    read three times, and each of the first two reads prints one line saying
    what it saw.
    """

    class Shifting(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "issues(states:OPEN" in query:
                data["repository"]["issues"]["totalCount"] += 1
            return data

    gh = Shifting([issue(1)], [])
    with pytest.raises(bb.BoardError, match="read 1 issues against a total of 2 on 3 reads"):
        build(gh)
    assert sum("issues(states:OPEN" in q for q in gh.calls) == 3
    assert capsys.readouterr().err.count("reading the list again") == 2


def test_a_pull_request_count_that_disagrees_on_every_read_stops_the_run() -> None:
    """Protects the board from a pull request list it cannot trust.

    The pull request list is read by the same loop as the issue list, so a
    read that disagrees with its count on every read stops the run here too,
    rather than publishing the pull requests it did read.
    """

    class Shifting(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "pullRequests(states:OPEN" in query:
                data["repository"]["pullRequests"]["totalCount"] += 1
            return data

    gh = Shifting([issue(1)], [pull(2000, closes=(1,))])
    with pytest.raises(bb.BoardError, match="read 1 pullRequests against a total of 2 on 3 reads"):
        build(gh)
    assert sum("pullRequests(states:OPEN" in q for q in gh.calls) == 3


def test_an_issue_repeated_beside_the_right_count_of_others_stops_the_run() -> None:
    """Protects the board from a page that repeats an issue.

    GitHub's pages continue after the last issue read, so a close or a filing
    cannot repeat one, and the generator keeps a guard against a page that
    repeats one anyway. Here issues 1 and 2 are two distinct numbers against a
    total of 2, so only the count of entries read, three, catches the repeat.
    A read accepted on its distinct numbers alone would draw issue 2 twice.
    """

    class Padded(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "issues(states:OPEN" in query:
                data["repository"]["issues"]["nodes"] = [issue(1), issue(2), issue(2)]
            return data

    with pytest.raises(bb.BoardError, match="read 3 issues against a total of 2 on 3 reads"):
        build(Padded([issue(1), issue(2)], []))


def test_an_issue_read_twice_stops_the_run() -> None:
    """Protects the count from a page that repeats an issue another dropped."""

    class Repeating(FakeGitHub):
        def __call__(self, query: str, variables: dict) -> dict:
            data = super().__call__(query, variables)
            if "issues(states:OPEN" in query:
                data["repository"]["issues"]["nodes"] = [issue(1), issue(1)]
            return data

    gh = Repeating([issue(1), issue(2)], [])
    with pytest.raises(bb.BoardError, match="read 2 issues against a total of 2 on 3 reads"):
        build(gh)
    assert sum("issues(states:OPEN" in q for q in gh.calls) == 3


class Growing(FakeGitHub):
    """Opens one more issue or pull request partway through the first read.

    The entry lands between the first and second page of the list's first
    read, the way an issue filed while the run reads does. ``reads`` counts
    each time the list is asked for from its first page.
    """

    def __init__(self, issues: list[dict], prs: list[dict], field: str, extra: dict):
        super().__init__(issues, prs)
        self.field = field
        self.extra: dict | None = extra
        self.reads = 0

    def __call__(self, query: str, variables: dict) -> dict:
        if f"{self.field}(states:OPEN" in query:
            if variables.get("after") is None:
                self.reads += 1
            elif self.extra is not None:
                if self.field == "issues":
                    self.issues.append(self.extra)
                else:
                    self.prs[self.extra["number"]] = self.extra
                self.extra = None
        return super().__call__(query, variables)


def test_an_issue_filed_while_the_list_is_read_is_read_again(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Protects the board from an issue filed between two pages of one read.

    Run 38167738593 failed on 2026-10-11 reading 119 issues against a total of
    118. The first read here disagrees with its own count, so the whole list is
    read again from its first page, and the second read holds every issue,
    the new one included.
    """
    gh = Growing([issue(n) for n in range(101)], [], "issues", issue(101))
    board, _ = build(gh)
    assert [c["n"] for c in board["tracker"]["items"]] == list(range(102))
    assert gh.reads == 2
    assert (
        "build_board: read 102 issues against a total of 101, reading the list again (read 2 of 3)"
    ) in capsys.readouterr().err


def test_a_pull_request_opened_while_the_list_is_read_is_read_again(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Protects the open pull request list, which pages the same way."""
    prs = [pull(2000 + n, closes=(1,)) for n in range(51)]
    gh = Growing([issue(1)], prs, "pullRequests", pull(2051, closes=(1,)))
    board, _ = build(gh)
    assert [p["pr"] for p in prs_of(board)] == list(range(2000, 2052))
    assert gh.reads == 2
    assert (
        "build_board: read 52 pullRequests against a total of 51, "
        "reading the list again (read 2 of 3)"
    ) in capsys.readouterr().err


def test_an_issue_closed_after_its_page_was_read_is_left_off_the_board() -> None:
    """Protects the board from carrying an entry only the first read held.

    Issue 50 is closed after the first page of the first read, and issue 101
    is filed before its second page. Pages continue after the last issue read,
    the way GitHub's cursors do, so the close moves nothing onto or off the
    second page. The first read holds issue 50 and 102 issues against a total
    of 101, and the second read holds the 101 issues still open. The board
    is the second read exactly, without issue 50.
    """

    class ClosedAndFiled(FakeGitHub):
        def __init__(self, issues: list[dict]):
            super().__init__(issues, [])
            self.changed = False

        def _page(self, nodes: list[dict], size: int, after: str | None) -> dict:
            rest = [n for n in nodes if after is None or n["number"] > int(after)]
            chunk = rest[:size]
            return {
                "totalCount": len(nodes),
                "nodes": chunk,
                "pageInfo": {
                    "hasNextPage": len(rest) > size,
                    "endCursor": str(chunk[-1]["number"]) if chunk else after,
                },
            }

        def __call__(self, query: str, variables: dict) -> dict:
            if "issues(states:OPEN" in query and variables.get("after") and not self.changed:
                self.issues = [i for i in self.issues if i["number"] != 50] + [issue(101)]
                self.changed = True
            return super().__call__(query, variables)

    gh = ClosedAndFiled([issue(n) for n in range(101)])
    board, _ = build(gh)
    assert [c["n"] for c in board["tracker"]["items"]] == [n for n in range(102) if n != 50]
    assert sum("issues(states:OPEN" in q for q in gh.calls) == 4


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


def test_the_stale_threshold_is_the_longest_gap_plus_ten_hours_for_a_dropped_run() -> None:
    """Protects the page's stale warning from a schedule GitHub mostly skips.

    The workflow's cron line leaves 30 minutes between runs. GitHub can start
    a scheduled run late or drop it, and documents no bound. Issue 587
    measured up to 603 minutes between two scheduled runs over 185 hours, and
    at the earlier 60-minute allowance a healthy board would have read as
    stale 45% of that time. So the threshold adds 600 minutes, and no gap
    measured there would have read as a failing Action.
    """
    assert bb.SCHEDULE_DELAY_ALLOWANCE == 600
    assert bb.longest_gap_minutes(WORKFLOW) == 30
    assert bb.stale_after_minutes(bb.longest_gap_minutes(WORKFLOW)) == 630


def test_the_skill_quotes_the_allowance_the_script_adds() -> None:
    """Protects the skill's data table from a second copy of the allowance."""
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert f"a {bb.SCHEDULE_DELAY_ALLOWANCE}-minute allowance" in skill


def test_the_threshold_adds_the_named_allowance(monkeypatch: pytest.MonkeyPatch) -> None:
    """Protects the allowance from a second copy of 600 inside the formula."""
    monkeypatch.setattr(bb, "SCHEDULE_DELAY_ALLOWANCE", 7)
    assert bb.stale_after_minutes(30) == 37


def test_the_cli_writes_the_workflows_gap_and_threshold(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protects the board from carrying the threshold where the gap belongs.

    ``5,15`` puts runs 10 and 50 minutes apart, so the longest gap differs from
    any even split of the hour, and the threshold differs from the gap.
    """
    fake = FakeGitHub([issue(1)], [])
    fake.requests, fake.cost = 1, 1
    monkeypatch.setattr(bb, "GhGraphql", lambda: fake)
    monkeypatch.delenv("GITHUB_STEP_SUMMARY", raising=False)
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    workflow = tmp_path / "board.yml"
    workflow.write_text('on:\n  schedule:\n    - cron: "5,15 * * * *"\n')
    out = tmp_path / "site"
    assert bb.main(["build", "--repo", REPO, "--workflow", str(workflow), "--out", str(out)]) == 0
    state = json.loads((out / "board.json").read_text())["state"]
    assert state["longestGapMinutes"] == 50
    assert state["staleAfterMinutes"] == 650


@pytest.mark.parametrize(
    ("cron", "gap", "stale_after"),
    [("*/15 * * * *", 15, 615), ("0 * * * *", 60, 660), ("5,15 * * * *", 50, 650)],
)
def test_the_threshold_follows_the_schedule(
    tmp_path: Path, cron: str, gap: int, stale_after: int
) -> None:
    workflow = tmp_path / "board.yml"
    workflow.write_text(f'on:\n  schedule:\n    - cron: "{cron}"\n')
    assert bb.longest_gap_minutes(workflow) == gap
    assert bb.stale_after_minutes(gap) == stale_after


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
        bb.longest_gap_minutes(workflow)


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
            issue(13, labels=("working:build",)),
            issue(
                14,
                labels=("band:1", "decision"),
                body="Board order: 2.5\nBoard after: #15\n",
                blocked_by=((10, "OPEN"),),
            ),
            issue(
                15, labels=("band:1",), comments=(("OWNER", "Board verdict: build after 3 passes"),)
            ),
            issue(16, sub_issues=2),
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
    assert text(ids, "strip").startswith("7 open issues")
    assert ids["source"]["hidden"]
    # Issue 15's plan is finished and nothing blocks it, so it waits in flight
    # for a builder. Issue 14 is the one ranked card left for the build order.
    assert cards(ids, "flow") == {11, 12, 13, 15}
    assert "1 check failing" in text(ids, "flow")
    assert "review in progress" in text(ids, "flow")
    assert "plan complete, 3 passes" in text(ids, "flow")
    assert cards(ids, "board") == {14}


def test_a_board_with_no_open_issues_draws_nothing(tmp_path: Path) -> None:
    """Protects the page's refusal of an empty tracker, which it keeps."""
    board, _ = build(FakeGitHub([], []))
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert "tracker section is missing fields" in text(ids, "source")
    assert_no_board_data(ids)


# ---- The workflow ----


def _workflow() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_the_schedule_stays_off_the_hour() -> None:
    """Protects the scheduled runs from the top of the hour.

    The workflow's comment keeps the schedule off minute 0, because GitHub's
    documentation names the start of every hour as its busiest time. The test
    reads the minutes rather than pinning the line, so the minutes can move
    again without editing it.
    """
    crons = re.findall(r"""^\s*-\s*cron:\s*"([^"]+)"\s*$""", _workflow(), re.M)
    assert len(crons) == 1
    minute = crons[0].split()[0]
    assert not minute.startswith("*"), minute
    assert 0 not in {int(m) for m in minute.split(",")}


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


DISPATCH = "gh workflow run board.yml --repo l3a0/quantitative-trading"

# What the generator reads that no trigger above covers, each with the words a
# moment in the skill uses for the change a session makes to it.
NO_RUN_READS = {"blockedBy": '"blocked by" link', "subIssues": "sub-issue"}

# Any wording of either change, so a moment reworded away from the words above
# still has to name the dispatch.
NO_RUN_WORDING = re.compile(r"blocked[- ]by|dependenc|sub-?issue|child issue", re.I)


def _moments() -> list[str]:
    """The numbered moments under the skill's "What a session sets, and when"."""
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    section = skill.split("\n## What a session sets, and when\n", 1)[1].split("\n## ", 1)[0]
    listed = section.split("\nNothing else needs setting.", 1)[0]
    return re.split(r"\n(?=\d+\. \*\*)", listed)[1:]


def test_a_change_that_starts_no_run_names_the_dispatch() -> None:
    """Protects the board from a link or sub-issue it would show hours late.

    A "blocked by" link and a sub-issue start no run, and the schedule that
    was their backstop fired in about 11% of its slots over 185 hours, which
    issue 587 measured. The owner ruled that the session making such a change
    dispatches the board itself. So every moment in the skill that sets one
    names the dispatch, each of the two changes has a moment that names it,
    and the command names this workflow, which keeps its dispatch trigger.
    """
    assert set(NO_RUN_READS) <= set(re.findall(r"\b(blockedBy|subIssues)\b", bb.ISSUES_QUERY))
    moments = _moments()
    for words in NO_RUN_READS.values():
        assert any(words in m for m in moments), f"no moment names a {words}"
    for moment in moments:
        if NO_RUN_WORDING.search(moment):
            assert "dispatch the board" in moment.lower(), moment.split("\n", 1)[0]
    skill = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert f"\n{DISPATCH}\n" in skill
    assert f"{DISPATCH} --ref" not in skill
    assert re.search(r"^  workflow_dispatch:\s*$", _workflow(), re.M)


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


def test_the_icon_is_published_where_the_page_links_it() -> None:
    """Protects the board's tab from a blank icon.

    The page links its icon by a relative address, so Pages serves it only
    when the step that adds the page puts the icon in the same folder under
    that name. A step that dropped the copy, or a page that renamed the link,
    would leave a browser asking for a file that is not there. The copy runs
    only after the page's copy succeeds, so joining the two with ``||`` would
    skip it on every run that works.
    """
    href = re.search(r'<link rel="icon" href="([^"]+)"', PAGE.read_text(encoding="utf-8"))
    assert href, "the page links no icon"
    href = href.group(1)
    step = _workflow().split("- name: Add the page", 1)[1].split("\n      - ", 1)[0]
    assert re.search(
        r"_site/index\.html &&\s+"
        + re.escape(f"cp .claude/skills/update-build-board/{href} _site/{href}"),
        step,
    )
    assert (SKILL_DIR / href).is_file()


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
