"""The one-off move of the artifact board's judgement onto GitHub.

``scripts/backfill_board.py`` writes to the live tracker, so its failures cost
more than a wrong page. Three matter here.

1. A second run that writes again. The script runs before a merge that may
   not follow, and may run twice, so anything GitHub already holds is skipped.
2. A write nothing can take back. Each write is logged as it lands, and the
   log reverses every kind of write the script makes.
3. A board that draws something else afterwards. The comparison names every
   field that differs, apart from the ones with no home on GitHub on purpose.

Nothing here touches GitHub. The plan runs on canned state, and the writes go
to a fake ``gh`` that records each call.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "backfill_board.py"
REPO = "l3a0/quantitative-trading"

sys.path.insert(0, str(SCRIPT.parent))
_spec = importlib.util.spec_from_file_location("backfill_board", SCRIPT)
bf = importlib.util.module_from_spec(_spec)
sys.modules["backfill_board"] = bf
_spec.loader.exec_module(bf)


def docs(**sections: list[dict]) -> dict[str, dict]:
    """A readback holding ``sections``, with the rest empty."""
    out = {name: {"schema": 1, "items": sections.get(name, [])} for name in bf.SECTIONS}
    out["state"] = {"schema": 1, "updatedAt": "2026-10-11T19:29:57Z", "issues": {"open": 2}}
    return out


def card(n: int, kind: str = "ready", needs: tuple[int, ...] = ()) -> dict:
    return {
        "n": n,
        "ms": "M",
        "label": f"Issue {n}",
        "kind": kind,
        "needs": list(needs),
        "labels": [],
    }


def live(
    n: int, labels: tuple[str, ...] = (), body: str = "", blocked_by=(), verdict=None, subs: int = 0
) -> dict:
    return {
        n: {
            "labels": set(labels),
            "body": body,
            "blocked_by": set(blocked_by),
            "sub_issues": subs,
            "verdict": verdict,
        }
    }


def test_every_judgement_field_becomes_one_write() -> None:
    """Protects the move from leaving a field behind."""
    readback = docs(
        tracker=[card(1, "decision"), card(2, needs=(1,))],
        next=[{"issue": 2, "band": 1, "ready": "build", "order": 14.05, "why": "w", "title": "t"}],
        planned=[{"n": 2, "passes": 5, "ready": "build", "note": "n"}],
        working=[{"n": 1, "kind": "build", "what": "building"}],
    )
    writes, notes = bf.plan(readback, {**live(1), **live(2)})
    assert notes == []
    assert writes == [
        {"op": "label", "issue": 2, "label": "band:1"},
        {"op": "line", "issue": 2, "line": "Board order: 14.05"},
        {"op": "verdict", "issue": 2, "ready": "build", "passes": 5},
        {"op": "label", "issue": 1, "label": "working:build"},
        {"op": "label", "issue": 1, "label": "decision"},
        {"op": "link", "issue": 2, "blocker": 1},
    ]


def test_a_second_run_writes_nothing() -> None:
    """Protects the tracker from a backfill run twice."""
    readback = docs(
        tracker=[card(1, "decision"), card(2, needs=(1,))],
        next=[{"issue": 2, "band": 1, "ready": "build", "order": 22}],
        planned=[{"n": 2, "passes": 5, "ready": "build"}],
        working=[{"n": 1, "kind": "build"}],
    )
    done = {
        **live(1, labels=("decision", "working:build")),
        **live(
            2,
            labels=("band:1",),
            body="Scope.\n\nBoard order: 22\n",
            blocked_by=(1,),
            verdict=("build", 5),
        ),
    }
    assert bf.plan(readback, done) == ([], [])


def test_what_the_backfill_will_not_decide_is_named() -> None:
    """Protects a disagreement from being settled silently.

    The artifact's ``next`` entry for issue 303 said ``plan`` while its
    ``planned`` entry said ``build``, and the rule the generator applies takes
    the plan. A closed card and an issue the artifact never carried are named
    too, as is a kind GitHub would read differently.
    """
    readback = docs(
        tracker=[card(1), card(2, "deferred"), card(9)],
        next=[{"issue": 1, "band": 1, "ready": "plan"}],
        planned=[{"n": 1, "passes": 1, "ready": "build"}],
    )
    _, notes = bf.plan(readback, {**live(1, verdict=("build", 1)), **live(2), **live(3)})
    assert notes == [
        "#1: the artifact's next entry says plan, and the rule gives build from its planned entry",
        "#2: the artifact's kind is deferred, and GitHub gives ready",
        "#9 is a card on the artifact board but not an open issue",
        "#3 is open but has no card on the artifact board",
    ]


def test_an_order_line_already_there_with_another_value_waits() -> None:
    """Protects an order someone set on GitHub from a second line."""
    readback = docs(tracker=[card(1)], next=[{"issue": 1, "band": 3, "ready": "plan", "order": 4}])
    writes, notes = bf.plan(readback, live(1, labels=("band:3",), body="Board order: 7\n"))
    assert writes == []
    assert notes == ["#1 already carries an order line ['7'], so 'Board order: 4' waits"]


class FakeGh:
    """Records each ``gh`` call and answers the few that read something."""

    def __init__(self, body: str = "Scope.\n") -> None:
        self.calls: list[list[str]] = []
        self.body = body

    def __call__(self, args: list[str]) -> str:
        self.calls.append(args)
        if args[:2] == ["api", f"repos/{REPO}/issues/7"]:
            return json.dumps({"body": self.body})
        if args[:3] == ["api", "--method", "PATCH"]:
            self.body = args[-1].split("=", 1)[1]
            return "{}"
        if args[:2] == ["api", f"repos/{REPO}/issues/8"]:
            return json.dumps({"id": 8008})
        if "comments" in args[3] and args[2] == "POST":
            return json.dumps({"id": 4242})
        return ""


@pytest.mark.parametrize(
    "write",
    [
        {"op": "label", "issue": 7, "label": "band:1"},
        {"op": "line", "issue": 7, "line": "Board order: 14.3"},
        {"op": "verdict", "issue": 7, "ready": "build", "passes": 5},
        {"op": "link", "issue": 7, "blocker": 8},
    ],
)
def test_each_write_is_logged_with_what_reverses_it(write: dict) -> None:
    """Protects the undo, which has only the log to go on."""
    gh = FakeGh()
    logged = bf.apply_write(gh, REPO, write)
    bf.undo_write(gh, REPO, logged)
    if write["op"] == "label":
        assert gh.calls == [
            ["issue", "edit", "7", "--repo", REPO, "--add-label", "band:1"],
            ["issue", "edit", "7", "--repo", REPO, "--remove-label", "band:1"],
        ]
    elif write["op"] == "line":
        assert gh.body == "Scope.\n"
    elif write["op"] == "verdict":
        assert logged["comment"] == 4242
        assert "Board verdict: build after 5 passes\n" in gh.calls[0][5]
        assert gh.calls[-1] == ["api", "--method", "DELETE", f"repos/{REPO}/issues/comments/4242"]
    else:
        assert logged["blocker_id"] == 8008
        assert gh.calls[1][-1] == "issue_id=8008"
        assert gh.calls[-1][-1] == f"repos/{REPO}/issues/7/dependencies/blocked_by/8008"


def test_the_verdict_comment_carries_a_line_the_generator_reads() -> None:
    """Protects the join between the backfill and the generator."""
    found = bf.bb.latest_verdict(
        [{"authorAssociation": "OWNER", "body": bf.verdict_comment("decide", 1)}]
    )
    assert found == ("decide", 1)


def test_the_comparison_names_each_field_that_differs_and_no_other() -> None:
    """Protects the check that the two boards draw the same thing.

    ``why``, ``title``, ``note``, ``what`` and a card's ``label`` have no home on
    GitHub on purpose, so they never count as a difference.
    """
    old = docs(
        tracker=[card(1, needs=(2,)), card(2)],
        next=[{"issue": 1, "band": 1, "ready": "plan", "why": "w", "title": "t"}],
        planned=[{"n": 1, "passes": 2, "ready": "build", "note": "n"}],
        working=[{"n": 2, "kind": "build", "what": "building"}],
    )
    new = json.loads(json.dumps(old))
    for item in new["next"]["items"]:
        del item["why"], item["title"]
    new["planned"]["items"][0].pop("note")
    new["working"]["items"][0].pop("what")
    new["tracker"]["items"][0]["label"] = "A longer issue title"
    assert bf.compare(old, new) == []

    new["tracker"]["items"][0]["needs"] = []
    new["next"]["items"][0]["ready"] = "build"
    assert bf.compare(old, new) == [
        "tracker 1 needs: [2] on the artifact, [] built",
        "next 1 ready: 'plan' on the artifact, 'build' built",
    ]


def test_a_label_chip_lost_on_the_way_is_a_difference() -> None:
    """Protects the comparison from waving a card's chips through.

    Only the chips the move changes on purpose drop out: the board's own
    ``band:N`` and ``working:`` labels, which the generator leaves off, and
    ``decision``, which the backfill adds.
    """
    old = docs(
        tracker=[
            {**card(1), "labels": ["bug", "question"]},
            {**card(2), "labels": ["bug", "band:1", "working:build"]},
        ]
    )
    new = json.loads(json.dumps(old))
    new["tracker"]["items"][0]["labels"] = []
    new["tracker"]["items"][1]["labels"] = ["bug", "decision"]
    assert bf.compare(old, new) == [
        "tracker 1 labels: ['bug', 'question'] on the artifact, [] built",
    ]


def _readback(folder: Path, readback: dict) -> Path:
    folder.mkdir()
    for name, doc in readback.items():
        (folder / f"{name}.json").write_text(json.dumps(doc), encoding="utf-8")
    return folder


def test_apply_then_undo_through_main_reverses_every_write_newest_first(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protects the undo the backfill exists for, when the merge does not follow.

    The log must carry what each write needs to be reversed, the comment's id
    and the blocker's id, because undo has nothing else to go on. Undo replays
    it newest first, and empties the log as it goes.
    """
    readback = docs(
        tracker=[card(7, needs=(8,)), card(8)],
        next=[{"issue": 7, "band": 1, "ready": "build"}],
        planned=[{"n": 7, "passes": 5, "ready": "build"}],
    )
    folder = _readback(tmp_path / "readback", readback)
    log = tmp_path / "log.jsonl"
    gh = FakeGh()
    monkeypatch.setattr(bf, "gh", gh)
    monkeypatch.setattr(bf, "read_github", lambda gql, repo: {**live(7), **live(8)})

    assert bf.main(["apply", "--repo", REPO, "--readback", str(folder), "--log", str(log)]) == 0
    logged = [json.loads(x) for x in log.read_text().splitlines()]
    assert [w["op"] for w in logged] == ["label", "verdict", "link"]
    assert logged[1]["comment"] == 4242
    assert logged[2]["blocker_id"] == 8008

    gh.calls.clear()
    assert bf.main(["undo", "--repo", REPO, "--log", str(log)]) == 0
    assert gh.calls == [
        ["api", "--method", "DELETE", f"repos/{REPO}/issues/7/dependencies/blocked_by/8008"],
        ["api", "--method", "DELETE", f"repos/{REPO}/issues/comments/4242"],
        ["issue", "edit", "7", "--repo", REPO, "--remove-label", "band:1"],
    ]
    assert log.read_text() == ""


def test_an_undo_that_stops_partway_resumes_where_it_stopped(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protects a second undo from failing on a write already reversed.

    The network drops on the second reversal. A second run must start from
    that write rather than reverse the first one again, which GitHub answers
    with a 404.
    """
    log = tmp_path / "log.jsonl"
    writes = [{"op": "label", "issue": 7, "label": f"band:{b}"} for b in (1, 2, 3)]
    log.write_text("".join(json.dumps(w) + "\n" for w in writes), encoding="utf-8")
    calls: list[str] = []
    healed = {"now": False}

    def flaky(args: list[str]) -> str:
        if len(calls) == 1 and not healed["now"]:
            raise bf.bb.BoardError("network dropped")
        calls.append(args[-1])
        return ""

    monkeypatch.setattr(bf, "gh", flaky)
    assert bf.main(["undo", "--repo", REPO, "--log", str(log)]) == 1
    assert calls == ["band:3"]
    healed["now"] = True
    assert bf.main(["undo", "--repo", REPO, "--log", str(log)]) == 0
    assert calls == ["band:3", "band:2", "band:1"]


def test_a_link_to_another_repository_does_not_count_as_present() -> None:
    """Protects a write from being skipped for a sibling's issue of the same number."""
    empty = {"hasNextPage": False, "endCursor": None}

    def gql(query: str, variables: dict) -> dict:
        foreign = {"number": 1, "state": "OPEN", "repository": {"nameWithOwner": "l3a0/other"}}
        node = {
            "id": "I2",
            "number": 2,
            "body": "",
            "labels": {"nodes": [], "pageInfo": empty},
            "blockedBy": {"nodes": [foreign], "pageInfo": empty},
            "subIssues": {"totalCount": 0},
            "issueComments": {"nodes": [], "pageInfo": empty},
        }
        return {"repository": {"issues": {"totalCount": 1, "nodes": [node], "pageInfo": empty}}}

    assert bf.read_github(gql, REPO)[2]["blocked_by"] == set()


def test_a_second_apply_adds_to_the_log_rather_than_replacing_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Protects the record of a first run that stopped partway.

    Its writes are still on GitHub, so a rerun that wiped the log would leave
    them where ``undo`` cannot reach.
    """
    folder = _readback(tmp_path / "readback", docs(tracker=[card(7, "decision")]))
    log = tmp_path / "log.jsonl"
    earlier = {"op": "label", "issue": 7, "label": "band:1"}
    log.write_text(json.dumps(earlier) + "\n", encoding="utf-8")
    monkeypatch.setattr(bf, "gh", FakeGh())
    monkeypatch.setattr(bf, "read_github", lambda gql, repo: live(7))
    assert bf.main(["apply", "--repo", REPO, "--readback", str(folder), "--log", str(log)]) == 0
    assert [json.loads(x) for x in log.read_text().splitlines()] == [
        earlier,
        {"op": "label", "issue": 7, "label": "decision"},
    ]


def test_github_is_read_for_the_verdicts_already_posted() -> None:
    """Protects a second ``apply`` from posting every verdict again."""
    empty = {"hasNextPage": False, "endCursor": None}

    def gql(query: str, variables: dict) -> dict:
        verdict = {"authorAssociation": "OWNER", "body": "Board verdict: build after 5 passes"}
        node = {
            "id": "I2",
            "number": 2,
            "body": "",
            "labels": {"nodes": [], "pageInfo": empty},
            "blockedBy": {"nodes": [], "pageInfo": empty},
            "subIssues": {"totalCount": 0},
            "issueComments": {"nodes": [verdict], "pageInfo": empty},
        }
        return {"repository": {"issues": {"totalCount": 1, "nodes": [node], "pageInfo": empty}}}

    assert bf.read_github(gql, REPO)[2]["verdict"] == ("build", 5)


def test_a_different_verdict_on_github_is_corrected() -> None:
    """Protects the plan marker from an older verdict the artifact superseded."""
    readback = docs(tracker=[card(1)], planned=[{"n": 1, "passes": 5, "ready": "build"}])
    writes, _ = bf.plan(readback, live(1, verdict=("decide", 3)))
    assert writes == [{"op": "verdict", "issue": 1, "ready": "build", "passes": 5}]


def test_a_cards_after_becomes_its_line() -> None:
    """Protects a measured ordering from being dropped on the way."""
    readback = docs(tracker=[{**card(1), "after": [2, 3]}, card(2), card(3)])
    writes, _ = bf.plan(readback, {**live(1), **live(2), **live(3)})
    assert writes == [{"op": "line", "issue": 1, "line": "Board after: #2, #3"}]


def test_a_blocker_that_closed_gets_no_link_and_is_named() -> None:
    """Protects the tracker from a link to finished work, and the reader from a silent skip."""
    readback = docs(tracker=[card(1, needs=(9,))])
    writes, notes = bf.plan(readback, live(1))
    assert writes == []
    assert notes == ["#1 needs #9, which is not open, so no link is added"]


def test_the_comparison_reads_every_section_and_every_field() -> None:
    """Protects the check from going quiet on a whole kind of difference.

    Each line below is one the comparison exists to print: the open count, a
    card on one side only, a session, a plan, a pull request's field and a
    card's kind.
    """
    old = docs(
        tracker=[card(1, "decision"), card(2)],
        working=[{"n": 1, "kind": "build"}],
        planned=[{"n": 1, "passes": 2, "ready": "build"}],
        prs=[{"pr": 10, "issue": 1, "state": "open", "reviewed": True}],
    )
    new = docs(
        tracker=[card(1), card(3)],
        working=[{"n": 1, "kind": "decompose"}],
        planned=[{"n": 1, "passes": 3, "ready": "build"}],
        prs=[{"pr": 10, "issue": 1, "state": "merged", "reviewed": True}],
    )
    new["state"]["issues"]["open"] = 3
    assert bf.compare(old, new) == [
        "state: open issues 2 on the artifact, 3 built",
        "tracker 1 kind: 'decision' on the artifact, 'ready' built",
        "tracker 2: on the artifact only",
        "tracker 3: built only",
        "working 1 kind: 'build' on the artifact, 'decompose' built",
        "planned 1 passes: 2 on the artifact, 3 built",
        "prs (1, 10) state: 'open' on the artifact, 'merged' built",
    ]
