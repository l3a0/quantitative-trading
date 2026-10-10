"""The build board's page, run rather than read.

The board's page is checked in under ``.claude/skills/update-build-board`` so a
new board can be published from it. Its data lives in the published artifact's
database, in six documents, and a new board's database starts with none of
them. So the page carries no copy of the board, and when it has no live data it
must say so and draw nothing that reads as data. A stale copy drawn as if it
were current is the failure this file exists to catch.

A parse check would not catch it. A page that draws stale cards parses, and a
banner sentence that renders perfectly can still say something false. So each
test executes the page's script under a JavaScript engine, with the skill's
``dom-stub.js`` standing in for the browser and a fake database standing in for
the platform, and reads what the page rendered.

The engine is ``node`` where it is installed, which it is on GitHub's runners,
and ``osascript -l JavaScript`` otherwise, which is JavaScriptCore and ships
with macOS. With neither, the tests skip rather than pass.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "update-build-board"
PAGE = SKILL_DIR / "board.html"
STUB = SKILL_DIR / "dom-stub.js"
WITH_DB = SKILL_DIR / "with-db.py"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "build_board"
SECTIONS = ("state", "prs", "working", "planned", "next", "tracker")

# What the page renders into when it has data. With none, all three are hidden.
CONTENT = ("flightsec", "ordersec", "foot")

# Appended after the page's script. It waits for the page's own database lookup
# to settle, delivers each step's snapshots, and prints every element the page
# touched. A step maps a section to its document, or to null for a document that
# does not exist. The result arrives after the script's last line, so it is
# printed rather than returned: through `console.log` in node and osascript, and
# through `print` in a bare JavaScriptCore shell, which has no console. The
# page's loading banner arms a four-second timer when it has a copy to show, so
# a no-op timer keeps node from waiting on it.
DRIVER = """
var __flush = async function () { for (var i = 0; i < 20; i++) { await null; } };
(async function () {
  var out = { error: null, ids: {} };
  try {
    await __flush();
    for (var k = 0; k < __STEPS.length; k++) {
      var step = __STEPS[k];
      Object.keys(step).forEach(function (name) {
        var doc = step[name];
        var cb = __SUBS["board/" + name];
        if (!cb) { throw new Error("the page never subscribed to board/" + name); }
        cb({ exists: doc !== null, data: function () { return doc; } });
      });
      await __flush();
    }
  } catch (e) { out.error = String(e && e.stack || e); }
  Object.keys(store).forEach(function (id) {
    out.ids[id] = { html: store[id].innerHTML, hidden: store[id].hidden === true };
  });
  var line = "BOARD_RESULT " + JSON.stringify(out);
  if (typeof console !== "undefined" && console.log) { console.log(line); } else { print(line); }
})();
void 0;
"""


def _engine() -> list[str]:
    """The command that runs a script file, or a skip naming what is missing."""
    node = shutil.which("node")
    if node:
        return [node]
    osascript = shutil.which("osascript")
    if osascript:
        return [osascript, "-l", "JavaScript"]
    pytest.skip("no JavaScript engine: neither node nor osascript is installed")


def _page_script(page: Path) -> str:
    """The page's one inline script, as the skill's harness extracts it."""
    text = page.read_text(encoding="utf-8")
    start = text.find("<script>")
    assert start >= 0, f"{page} has no inline script"
    start += len("<script>")
    end = text.find("</script>", start)
    assert end >= 0, f"{page} never closes its script"
    return text[start:end]


def _prelude(db: bool, steps: list[dict]) -> str:
    """The fake platform, set up before the page's script runs.

    With ``db`` false there is no ``claude`` global at all, which is what a view
    with no database sees. Otherwise ``claude.use("db")`` resolves to a database
    whose ``doc(path).onSnapshot`` records the page's callback for the driver.
    """
    lines = [
        "var setTimeout = function () { return 0; };",
        "var __SUBS = {};",
        f"var __STEPS = {json.dumps(steps)};",
    ]
    if db:
        lines.append(
            "globalThis.claude = { use: function (cap) { return Promise.resolve("
            "cap === 'db' ? { doc: function (path) { return { onSnapshot: "
            "function (cb, err) { __SUBS[path] = cb; } }; } } : null); } };"
        )
    return "\n".join(lines) + "\n"


def run_page(tmp_path: Path, *, db: bool, steps: list[dict], page: Path = PAGE) -> dict:
    """Execute the page and return each element's HTML and hidden state."""
    script = STUB.read_text(encoding="utf-8") + _prelude(db, steps) + _page_script(page) + DRIVER
    runner = tmp_path / "run.js"
    runner.write_text(script, encoding="utf-8")
    done = subprocess.run(
        [*_engine(), str(runner)], capture_output=True, text=True, timeout=60, check=False
    )
    output = done.stdout + done.stderr
    assert done.returncode == 0, output
    found = [line for line in output.splitlines() if line.startswith("BOARD_RESULT ")]
    assert len(found) == 1, output
    result = json.loads(found[0][len("BOARD_RESULT ") :])
    assert result["error"] is None, result["error"]
    return result["ids"]


def text(ids: dict, element: str) -> str:
    """An element's rendered text, tags dropped and whitespace collapsed."""
    raw = ids.get(element, {}).get("html", "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def cards(ids: dict, element: str) -> set[int]:
    """The issue numbers drawn as cards inside one element."""
    raw = ids.get(element, {}).get("html", "")
    return {int(n) for n in re.findall(r'data-n="(\d+)"', raw)}


def fixture_docs() -> dict[str, dict]:
    """The six hand-built documents, as the database would deliver them."""
    return {
        name: json.loads((FIXTURE / f"{name}.json").read_text(encoding="utf-8"))
        for name in SECTIONS
    }


def assert_no_board_data(ids: dict) -> None:
    """Nothing but the banner is drawn, so nothing renders as if it were data."""
    for element in CONTENT:
        assert ids.get(element, {}).get("hidden"), f"{element} is not hidden"
    for element in ("strip", "flow", "board", "foot"):
        assert text(ids, element) == "", f"{element} drew {text(ids, element)!r}"
    assert not ids["source"]["hidden"], "the banner is hidden"


def test_a_view_with_no_database_says_it_has_no_copy(tmp_path: Path) -> None:
    """Protects the published page in a view the platform gives no database.

    The page used to fall back on a copy of the board built into it. That copy
    is gone, so the banner has to say the page carries none rather than drawing
    an empty board as if it were the live one.
    """
    ids = run_page(tmp_path, db=False, steps=[])
    banner = text(ids, "source")
    assert banner.startswith("Showing no board data.")
    assert "This view cannot reach the live board" in banner
    assert "the page carries no copy of its own" in banner
    assert_no_board_data(ids)


def test_a_database_with_no_documents_says_the_board_is_empty(tmp_path: Path) -> None:
    """Protects a newly published board, whose database starts empty.

    Every section reporting no document is the normal first state, so it gets
    its own sentence rather than a list naming all six as missing.
    """
    ids = run_page(tmp_path, db=True, steps=[dict.fromkeys(SECTIONS)])
    banner = text(ids, "source")
    assert banner == "Showing no board data. The live board holds no document yet."
    assert_no_board_data(ids)


def test_six_valid_documents_draw_the_live_board(tmp_path: Path) -> None:
    """Protects the path every viewer takes once the database holds a board.

    Fixture issue 90501 has an open pull request, so it belongs in flight and nowhere
    else. Fixture issue 90502 is the one card the fixture ranks, so the default view draws
    it in the build order and hides the other three.
    """
    ids = run_page(tmp_path, db=True, steps=[fixture_docs()])
    assert ids["source"]["html"] == ""
    assert ids["source"]["hidden"]
    for element in CONTENT:
        assert not ids[element]["hidden"], f"{element} is hidden on a live board"
    assert text(ids, "strip").startswith("5 open issues")
    assert cards(ids, "flow") == {90501}
    assert cards(ids, "board") == {90502}
    assert "3 other open issues are not in the priority order" in text(ids, "more")


def _card_tag(ids: dict, element: str, n: int) -> str:
    """The opening tag of one card, which carries its classes and its label."""
    raw = ids.get(element, {}).get("html", "")
    found = re.search(r'<div class="tk[^"]*" data-n="' + str(n) + r'"[^>]*>', raw)
    assert found, f"no card for {n} in {element}"
    return found.group(0)


@pytest.mark.parametrize("state", ["merged", "closed"])
def test_a_landed_part_of_pull_request_leaves_its_card_free(tmp_path: Path, state: str) -> None:
    """Protects the free list from a pull request that is no longer open.

    On 2026-10-10 issues 431 and 432 each had a pull request merged as
    ``Part of``, with the issue left open for what that pull request did not
    do. The board note read any ``prs`` entry as work written and waiting on a
    review, so it held both back from the free list for a reason true of
    neither. Fixture issue 90505 is made ready and ranked here so the default
    view draws it, and fixture issue 90504, a decision, carries the same kind
    of pull request so its kind word can be read. Fixture issue 90503 gets a
    finished plan and one more such pull request. An open branch hides the plan
    marker, and a landed one must not, since the card then sits under "Planned,
    no builder" and a missing marker there would contradict its own column.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] in (90503, 90505):
            card["needs"] = []
    docs["next"]["items"] += [
        {"issue": 90505, "band": 3, "ready": "build", "why": "Its remainder is still to write."},
        {"issue": 90504, "band": 3, "ready": "decide", "why": "Its scope is still the owner's."},
    ]
    docs["planned"]["items"].append({"n": 90503, "passes": 2, "ready": "build"})
    for pr, issue in ((90602, 90505), (90603, 90504), (90604, 90503)):
        docs["prs"]["items"].append(
            {
                "pr": pr,
                "issue": issue,
                "state": state,
                "linked": False,
                "partOf": True,
                "reviewed": True,
                "review": "review posted",
                "rollup": [["test", "success"]],
            }
        )
    ids = run_page(tmp_path, db=True, steps=[docs])

    assert cards(ids, "flow") == {90501, 90503}
    assert {90504, 90505} <= cards(ids, "board")
    note = text(ids, "boardnote")
    assert "#90505" in note.split(" free for a session to take today")[1].split(".")[0]
    assert "waiting on a review" not in note
    assert "a pull request carries it" not in text(ids, "key")
    landed = _card_tag(ids, "board", 90505)
    assert "has-pr" not in landed
    assert f"Pull request 90602 is {state} against it." in landed
    assert "plan-build" in _card_tag(ids, "flow", 90503)
    # The fixture's open branch on 90501 is in flight, so its legend explains
    # the border while no card on the board below draws one.
    assert "a pull request carries it" in text(ids, "flowkey")
    decision = _card_tag(ids, "board", 90504)
    assert "It needs a decision, not a session." in decision
    assert "needs a decision, not a session" in text(ids, "board")
    assert "PR #90602" in text(ids, "board")

    # With the fixture's one open branch gone, nothing in flight is carried by a
    # pull request, so that legend's entry has no card to explain.
    docs["prs"]["items"] = [p for p in docs["prs"]["items"] if p["state"] != "open"]
    ids = run_page(tmp_path, db=True, steps=[docs])
    assert 90503 in cards(ids, "flow")
    assert "a pull request carries it" not in text(ids, "flowkey")


def test_an_open_branch_beside_a_landed_one_still_holds_its_card(tmp_path: Path) -> None:
    """Protects what an open pull request does, from the fix for landed ones.

    Fixture issue 90501 gets a merged ``Part of`` listed ahead of its open
    pull request. The card stays in flight with the border an open branch
    draws, and its label names the open one, which is the branch a reader acts
    on, rather than whichever entry happens to come first in ``prs``. It also
    gets a finished plan, and the open branch alone must hide the plan marker,
    since no session is on the card to hide it instead. The flow note must
    give the open branch's reason for the card and count one branch, not two.
    """
    docs = fixture_docs()
    docs["planned"]["items"].append({"n": 90501, "passes": 2, "ready": "build"})
    landed = {
        "pr": 90605,
        "issue": 90501,
        "state": "merged",
        "linked": False,
        "partOf": True,
        "reviewed": True,
        "review": "review posted",
        "rollup": [["test", "success"]],
    }
    docs["prs"]["items"].insert(0, landed)
    ids = run_page(tmp_path, db=True, steps=[docs])
    assert cards(ids, "flow") == {90501}
    tag = _card_tag(ids, "flow", 90501)
    assert "has-pr" in tag
    assert "plan-" not in tag
    assert "Pull request 90601 is open against it." in tag
    # The merged entry carries a review, so a note reading it would not call
    # the card unreviewed, and counting it as a branch would report two
    # branches racing to merge.
    flownote = text(ids, "flownote")
    assert "#90501 is written and unreviewed" in flownote
    assert "more than one open branch" not in flownote


def _pull(pr: int, issue: int, state: str, *, linked: bool, part_of: bool) -> dict:
    """One ``prs`` entry with a posted review and a green check."""
    return {
        "pr": pr,
        "issue": issue,
        "state": state,
        "linked": linked,
        "partOf": part_of,
        "reviewed": True,
        "review": "review posted",
        "rollup": [["test", "success"]],
    }


def _pr_line(ids: dict, element: str, pr: int) -> str:
    """The text of the line a card draws for one pull request."""
    raw = ids.get(element, {}).get("html", "")
    found = re.search(
        r'<div class="pr">(?:(?!</div>).)*PR #' + str(pr) + r"<(?:(?!</div>).)*</div>", raw, re.S
    )
    assert found, f"no line for PR {pr} in {element}"
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", found.group(0)))).strip()


@pytest.mark.parametrize("linked", [False, True])
def test_a_merged_pull_request_with_no_part_of_holds_its_card_for_a_close_by_hand(
    tmp_path: Path, linked: bool
) -> None:
    """Protects the owner's ruling of 2026-10-10 on a merged pull request.

    A pull request merged with no ``Part of`` was meant to close its issue, so
    its card has nothing left for a session except a close by hand. Freeing it
    would offer finished work to the next session. That holds whether or not
    GitHub registered the link, since a linked one still drawn means the
    tracker has not caught up. Fixture issue 90505 is ranked and free of
    blockers so the free list can be read for it. Fixture issue 90504, a
    decision, carries one so its kind word can be read. Fixture issue 90503
    has a finished plan, so it would sit under "Planned, no builder", whose
    note calls a card there free for anyone to pick up.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] in (90503, 90505):
            card["needs"] = []
    docs["next"]["items"] += [
        {"issue": 90505, "band": 3, "ready": "build", "why": "Only its close is left."},
        {"issue": 90504, "band": 3, "ready": "decide", "why": "Its scope is still the owner's."},
        {"issue": 90503, "band": 3, "ready": "build", "why": "Only its close is left."},
    ]
    docs["planned"]["items"].append({"n": 90503, "passes": 2, "ready": "build"})
    for pr, issue in ((90602, 90505), (90603, 90504), (90604, 90503)):
        docs["prs"]["items"].append(_pull(pr, issue, "merged", linked=linked, part_of=False))
    ids = run_page(tmp_path, db=True, steps=[docs])

    assert cards(ids, "flow") == {90501}
    assert "free for anyone to pick up" not in text(ids, "flownote")
    note = text(ids, "boardnote")
    free = note.split(" free for a session to take today")[1].split(".")[0]
    assert "#90505" not in free
    assert "#90503" not in free
    assert "have merged and need only closing by hand" in note
    assert "waiting on a review" not in note
    assert "plan-" not in _card_tag(ids, "board", 90503)
    assert "It needs a decision, not a session." not in _card_tag(ids, "board", 90504)
    assert "needs a decision, not a session" not in text(ids, "board")
    assert "merged" in _pr_line(ids, "board", 90602).split()


@pytest.mark.parametrize("part_of", [False, True])
@pytest.mark.parametrize("linked", [False, True])
def test_a_closed_pull_request_says_closed_and_frees_its_card(
    tmp_path: Path, linked: bool, part_of: bool
) -> None:
    """Protects a closed pull request's line from reading as an open one.

    A closed entry stays in ``prs`` while its issue is open. Its line used to
    repeat the review text it carried when it closed, and an unlinked one went
    on saying what merging would do, about a pull request that never will.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] == 90505:
            card["needs"] = []
    docs["next"]["items"].append({"issue": 90505, "band": 3, "ready": "build", "why": "x"})
    docs["prs"]["items"].append(_pull(90602, 90505, "closed", linked=linked, part_of=part_of))
    ids = run_page(tmp_path, db=True, steps=[docs])

    line = _pr_line(ids, "board", 90602)
    assert "closed" in line.split()
    assert "review posted" not in line
    assert "merging" not in line
    assert "stays open" not in line
    note = text(ids, "boardnote")
    assert "#90505" in note.split(" free for a session to take today")[1].split(".")[0]


@pytest.mark.parametrize("kind", ["build", "decompose"])
def test_a_session_beside_a_landed_part_of_is_not_on_a_branch(tmp_path: Path, kind: str) -> None:
    """Protects the label's account of a session from a pull request that merged.

    A session on a card whose ``Part of`` has merged is writing the remainder,
    and no branch of its exists yet. The label said the session was still on
    the branch, or still revising the plan, whenever any ``prs`` entry stood
    against the card.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] == 90505:
            card["needs"] = []
    docs["prs"]["items"].append(_pull(90602, 90505, "merged", linked=False, part_of=True))
    docs["working"]["items"].append({"n": 90505, "kind": kind, "what": "writing the remainder"})
    ids = run_page(tmp_path, db=True, steps=[docs])

    assert 90505 in cards(ids, "flow")
    tag = _card_tag(ids, "flow", 90505)
    assert "A session is working it: writing the remainder." in tag
    assert "still on the branch" not in tag
    assert "still revising its plan" not in tag


def test_a_spliced_copy_still_draws_as_the_copy_built_into_the_page(tmp_path: Path) -> None:
    """Protects the skill's harness, which runs the page with no database.

    ``with-db.py`` writes the documents just read into the page's FALLBACK line,
    and the harness then checks what that copy draws. The page must still draw
    it, and the banner must still say it is the copy built into the page.
    """
    spliced = subprocess.run(
        [sys.executable, str(WITH_DB), str(PAGE), str(FIXTURE)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    page = tmp_path / "board.html"
    page.write_text(spliced, encoding="utf-8")
    ids = run_page(tmp_path, db=False, steps=[], page=page)
    banner = text(ids, "source")
    assert banner.startswith("Showing the copy built into the page, measured ")
    assert "so anything a session wrote since then is missing here" in banner
    assert cards(ids, "flow") == {90501}
    assert cards(ids, "board") == {90502}
    assert text(ids, "strip").startswith("5 open issues")


@pytest.mark.parametrize("missing", SECTIONS)
def test_one_missing_document_is_named_and_draws_nothing(tmp_path: Path, missing: str) -> None:
    """Protects a board whose database holds five of the six documents.

    The page goes live only on all six, so a partial set names what is missing
    and draws no board, rather than claiming to show a copy it no longer has.
    """
    docs = fixture_docs()
    docs[missing] = None
    ids = run_page(tmp_path, db=True, steps=[docs])
    banner = text(ids, "source")
    assert banner == f"Showing no board data. The live board is missing {missing}."
    assert_no_board_data(ids)


def test_every_missing_document_is_named(tmp_path: Path) -> None:
    """Protects the banner's list when more than one document is missing.

    An earlier page named only the last section reported absent, so a board
    missing two sections told the reader about one of them.
    """
    docs = fixture_docs()
    docs["prs"] = None
    docs["next"] = None
    ids = run_page(tmp_path, db=True, steps=[docs])
    banner = text(ids, "source")
    assert banner == "Showing no board data. The live board is missing prs and next."
    assert_no_board_data(ids)


def test_a_bad_section_before_any_live_data_draws_nothing(tmp_path: Path) -> None:
    """Protects the shape check when there is no earlier board to keep.

    A tracker item without ``needs`` would crash the redraw, so the section is
    refused. With no live data seen yet, nothing is left to show.
    """
    docs = fixture_docs()
    del docs["tracker"]["items"][0]["needs"]
    ids = run_page(tmp_path, db=True, steps=[docs])
    banner = text(ids, "source")
    assert banner.startswith("Showing no board data.")
    assert "section is missing fields this page needs" in banner
    assert_no_board_data(ids)


def test_a_first_draw_that_throws_leaves_no_board_data(tmp_path: Path) -> None:
    """Protects the strip when the first live draw fails partway.

    ``usableSection`` leaves ``after`` unchecked, so a tracker item with a
    number there passes the check and throws while the build order draws, after
    the strip has drawn. The page rolls back to no data, and the strip must not
    keep that draw's count beside a banner saying no board data is shown.
    """
    docs = fixture_docs()
    docs["tracker"]["items"][0]["after"] = 5
    ids = run_page(tmp_path, db=True, steps=[docs])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (a live section could not be drawn).")
    assert text(ids, "strip") == ""
    # The build order drew part of itself before throwing, inside a section the
    # page then hides, so no viewer sees it.
    for element in CONTENT:
        assert ids[element]["hidden"], f"{element} is not hidden"


def test_live_data_lost_afterwards_stays_on_screen(tmp_path: Path) -> None:
    """Protects the last live board when a section disappears after it drew.

    The board stays drawn, and the banner says updates stopped and that what is
    shown is the last live data.
    """
    ids = run_page(tmp_path, db=True, steps=[fixture_docs(), {"state": None}])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (state removed).")
    assert "What is shown is the last live data" in banner
    assert cards(ids, "flow") == {90501}
    assert not ids["flightsec"]["hidden"]


def test_a_live_board_still_loading_says_so_at_once(tmp_path: Path) -> None:
    """Protects the view between opening the page and the first snapshot.

    The page carries no copy, so a viewer would see a blank page until the
    database answers. The banner says the board has not arrived yet instead.
    """
    ids = run_page(tmp_path, db=True, steps=[])
    assert text(ids, "source") == (
        "Showing no board data. The live board has not arrived yet, "
        "and the page carries no copy of its own."
    )
    assert_no_board_data(ids)


def test_a_document_that_arrives_is_no_longer_named(tmp_path: Path) -> None:
    """Protects the banner from naming a section that has since arrived.

    A new board's documents land one at a time, and until the sixth lands the
    banner must name only the sections still missing.
    """
    docs = fixture_docs()
    ids = run_page(
        tmp_path, db=True, steps=[{"state": None, "prs": None}, {"state": docs["state"]}]
    )
    assert text(ids, "source") == "Showing no board data. The live board is missing prs."
    assert_no_board_data(ids)


def test_a_draw_that_throws_after_live_data_keeps_the_last_board(tmp_path: Path) -> None:
    """Protects the last good board when a later write breaks the drawing code.

    The banner says what is shown is the last live data, so the board must
    still be drawn rather than hidden behind that claim.
    """
    broken = fixture_docs()["tracker"]
    for item in broken["items"]:
        item["after"] = 7
    ids = run_page(tmp_path, db=True, steps=[fixture_docs(), {"tracker": broken}])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (a live section could not be drawn).")
    assert "What is shown is the last live data" in banner
    assert not ids["flightsec"]["hidden"]
    assert cards(ids, "flow") == {90501}


def _splice(tmp_path: Path, docs: dict, page: Path = PAGE) -> subprocess.CompletedProcess:
    """Run ``with-db.py`` on ``page`` with ``docs`` written as its readback."""
    folder = tmp_path / "readback"
    folder.mkdir(exist_ok=True)
    for name, doc in docs.items():
        (folder / f"{name}.json").write_text(json.dumps(doc), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(WITH_DB), str(page), str(folder)],
        capture_output=True,
        text=True,
        check=False,
    )


def test_the_splice_refuses_a_document_the_page_would_refuse(tmp_path: Path) -> None:
    """Protects the harness from checking a document the page would not draw."""
    docs = fixture_docs()
    docs["prs"]["schema"] = 2
    done = _splice(tmp_path, docs)
    assert done.returncode != 0
    assert "prs: schema 2, expected 1" in done.stderr


def test_the_splice_survives_a_closing_script_tag_in_the_data(tmp_path: Path) -> None:
    """Protects the spliced page from data that would end its script early.

    A card label holding a closing script tag must be escaped, and the escape
    must reach the page unchanged rather than be read as a replacement pattern.
    """
    docs = fixture_docs()
    docs["tracker"]["items"][1]["label"] = "a </script> in a label"
    done = _splice(tmp_path, docs)
    assert done.returncode == 0, done.stderr
    page = tmp_path / "spliced.html"
    page.write_text(done.stdout, encoding="utf-8")
    ids = run_page(tmp_path, db=False, steps=[], page=page)
    assert cards(ids, "board") == {90502}


def test_the_splice_refuses_a_page_with_two_copy_lines(tmp_path: Path) -> None:
    """Protects the splice from filling one copy line and leaving another."""
    line = "const FALLBACK = { none: true };"
    page = tmp_path / "two.html"
    page.write_text(PAGE.read_text(encoding="utf-8").replace(line, f"{line}\n{line}"), "utf-8")
    done = _splice(tmp_path, fixture_docs(), page=page)
    assert done.returncode != 0
    assert "found 2" in done.stderr


def test_no_tracked_file_links_to_a_claude_artifact() -> None:
    """Protects every machine from a board address only one account can reach.

    A claude.ai artifact belongs to one account, so an address written into
    this repository points every machine at a page that a machine signed in
    elsewhere cannot open. That is how the first board, and the three pages it
    linked to, were lost here on 2026-10-09. A board's address lives in a file
    on the machine, per the Configuration section of ``docs/design.md``. The
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


def test_an_open_branch_still_suppresses_what_it_always_did(tmp_path: Path) -> None:
    """Protects the open-branch half of each condition the landed fix rewrote.

    Fixture issue 90504, a decision, gets a finished plan, an open pull request
    and a build session still on it. Each of the four things an open branch
    decides on a card is read: the kind word and its sentence go, the plan
    marker goes, and the label says the build session is still on the branch.
    """
    docs = fixture_docs()
    docs["planned"]["items"].append({"n": 90504, "passes": 2, "ready": "decide"})
    docs["prs"]["items"].append(_pull(90606, 90504, "open", linked=True, part_of=False))
    docs["working"]["items"].append({"n": 90504, "kind": "build", "what": "writing the ruling"})
    ids = run_page(tmp_path, db=True, steps=[docs])

    assert 90504 in cards(ids, "flow")
    tag = _card_tag(ids, "flow", 90504)
    assert "It needs a decision, not a session." not in tag
    assert "needs a decision, not a session" not in text(ids, "flow")
    assert "plan-" not in tag
    assert "Its build session is still on the branch." in tag


def test_a_missing_closing_link_names_the_open_branch(tmp_path: Path) -> None:
    """Protects the flow note's warning from reading a merged entry.

    Fixture issue 90501 gets a merged pull request with no closing link listed
    ahead of its open one, which also has none. Only the open one can still be
    merged, so the warning names it and counts one branch.
    """
    docs = fixture_docs()
    docs["prs"]["items"][0]["linked"] = False
    docs["prs"]["items"].insert(0, _pull(90605, 90501, "merged", linked=False, part_of=False))
    ids = run_page(tmp_path, db=True, steps=[docs])

    flownote = text(ids, "flownote")
    assert "GitHub registered no closing link for PR #90601" in flownote
    assert "PR #90605" not in flownote
    assert "more than one open branch" not in flownote
