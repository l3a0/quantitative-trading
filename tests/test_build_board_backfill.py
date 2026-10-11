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
