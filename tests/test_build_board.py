"""The build board's page, run rather than read.

The board's page is checked in under ``.claude/skills/update-build-board``, and
a GitHub Action publishes it on GitHub Pages beside ``board.json``, which the
same Action builds from GitHub. The page fetches that file on a timer. It
carries no copy of the board, so when it has no live data it must say so and
draw nothing that reads as data. A stale copy drawn as if it were current is
the failure this file exists to catch.

A parse check would not catch it. A page that draws stale cards parses, and a
banner sentence that renders perfectly can still say something false. So each
test executes the page's script under a JavaScript engine, with the skill's
``dom-stub.js`` standing in for the browser and a fake fetch serving
``board.json``, and reads what the page rendered. The driver serves one
response per poll and fires the page's timer between them.

Until issue 533 the page also read a claude.ai artifact's database, and these
tests drove it through a fake one as well. That board retired, so the database
driver went with it, and a test that once delivered sections one at a time now
serves a file missing a section.

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
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "update-build-board"
PAGE = SKILL_DIR / "board.html"
STUB = SKILL_DIR / "dom-stub.js"
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "build_board"
SECTIONS = ("state", "prs", "working", "planned", "next", "tracker")

# What the page renders into when it has data. With none, all three are hidden.
CONTENT = ("flightsec", "ordersec", "foot")


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


# The driver. The prelude below hands the page a fake fetch answering with the
# current step's response, and records the page's timers. The page fetches once
# on load, which takes the first response. The driver then fires the page's
# fetch timer once per further response, as two minutes passing would, and
# prints what the page drew and every fetch it made. A comment planted in the
# build order after the first draw survives only if no later fetch redraws it,
# which is how a test sees whether the page drew again. The result arrives after
# the script's last line, so it is printed rather than returned: through
# `console.log` in node and osascript, and through `print` in a bare
# JavaScriptCore shell, which has no console. When the prelude names a card in
# `__CLICK`, the driver clicks it after the last response, which is the only way
# the chain bar renders anything but its hint.
FETCH_DRIVER = """
var __flush = async function () { for (var i = 0; i < 50; i++) { await null; } };
var __MARK = "<!--first draw-->";
(async function () {
  var out = { error: null, ids: {}, fetches: __FETCHES, redrawn: null };
  try {
    await __flush();
    document.getElementById("board").innerHTML += __MARK;
    for (var k = 1; k < __RESP.length; k++) {
      __CUR = k;
      __TIMERS.forEach(function (t) { if (t.ms !== 60000) { t.fn(); } });
      await __flush();
    }
    for (var h = 0; h < __HELD.length; h++) { __HELD[h](); await __flush(); }
    if (typeof __CLICK === "number") {
      store.board.onclick({ target: { closest: function (sel) {
        return sel === ".tk" ? { dataset: { n: String(__CLICK) } } : null; } } });
    }
  } catch (e) { out.error = String(e && e.stack || e); }
  var __board = document.getElementById("board");
  out.redrawn = __board.innerHTML.indexOf(__MARK) < 0;
  __board.innerHTML = __board.innerHTML.replace(__MARK, "");
  Object.keys(store).forEach(function (id) {
    out.ids[id] = { html: store[id].innerHTML, hidden: store[id].hidden === true };
  });
  var line = "BOARD_RESULT " + JSON.stringify(out);
  if (typeof console !== "undefined" && console.log) { console.log(line); } else { print(line); }
})();
void 0;
"""


def _fetch_prelude(responses: list[dict], click: int | None = None) -> str:
    """A fake fetch serving ``responses`` in turn, and a timer list to fire.

    Each response is ``{"status": n, "body": text}``, or ``{"throw": true}``
    for a network failure. One carrying ``"hold": true`` stays unanswered
    until every other response has been served, which is a slow answer
    arriving after a later poll's. One carrying ``"never": true`` is never
    answered, which is a page still waiting for its first board.
    """
    lines = [
        "var setTimeout = function () { return 0; };",
        "var __TIMERS = [];",
        "setInterval = function (fn, ms) { __TIMERS.push({ fn: fn, ms: ms }); return 0; };",
        f"var __RESP = {json.dumps(responses)};",
        "var __CUR = 0;",
        "var __FETCHES = [];",
        "var __HELD = [];",
        "var __answer = function (r) {",
        "  if (r.throw) { return Promise.reject(new Error('offline')); }",
        "  return Promise.resolve({ ok: r.status >= 200 && r.status < 300, status: r.status,",
        "    text: function () { return Promise.resolve(r.body); } });",
        "};",
        "var fetch = function (url, opts) {",
        "  __FETCHES.push({ url: url, cache: opts && opts.cache });",
        "  var r = __RESP[__CUR];",
        "  if (r.never) { return new Promise(function () {}); }",
        "  if (!r.hold) { return __answer(r); }",
        "  return new Promise(function (ok, no) {",
        "    __HELD.push(function () { __answer(r).then(ok, no); }); });",
        "};",
    ]
    if click is not None:
        lines.append(f"var __CLICK = {int(click)};")
    return "\n".join(lines) + "\n"


def run_fetch_page(
    tmp_path: Path, responses: list[dict], *, page: Path = PAGE, click: int | None = None
) -> tuple[dict, list[dict]]:
    """Execute the page on fetched responses, returning what it drew and fetched."""
    script = (
        STUB.read_text(encoding="utf-8")
        + _fetch_prelude(responses, click)
        + _page_script(page)
        + FETCH_DRIVER
    )
    result = _execute(tmp_path, script)
    return result["ids"], result["fetches"]


def draw(tmp_path: Path, docs: dict, *, page: Path = PAGE, click: int | None = None) -> dict:
    """What the page draws from one board.json holding ``docs``."""
    return run_fetch_page(tmp_path, [served(docs)], page=page, click=click)[0]


def run_without_fetch(tmp_path: Path) -> dict:
    """What the page draws on a host with no fetch, such as osascript."""
    script = (
        STUB.read_text(encoding="utf-8")
        + "var setTimeout = function () { return 0; };\nvar fetch = undefined;\n"
        + "var __RESP = []; var __FETCHES = []; var __HELD = [];\n"
        + _page_script(PAGE)
        + FETCH_DRIVER
    )
    return _execute(tmp_path, script)["ids"]


def fetch_redraws(tmp_path: Path, responses: list[dict]) -> bool:
    """Whether any fetch after the first drew the board again."""
    script = (
        STUB.read_text(encoding="utf-8")
        + _fetch_prelude(responses)
        + _page_script(PAGE)
        + FETCH_DRIVER
    )
    return _execute(tmp_path, script)["redrawn"]


def served(board: dict, status: int = 200) -> dict:
    """A board.json response as the fake fetch serves it."""
    return {"status": status, "body": json.dumps(board)}


def _execute(tmp_path: Path, script: str) -> dict:
    """Run a script under the JavaScript engine and return the driver's result."""
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
    return result


def text(ids: dict, element: str) -> str:
    """An element's rendered text, tags dropped and whitespace collapsed."""
    raw = ids.get(element, {}).get("html", "")
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).strip()


def cards(ids: dict, element: str) -> set[int]:
    """The issue numbers drawn as cards inside one element."""
    raw = ids.get(element, {}).get("html", "")
    return {int(n) for n in re.findall(r'data-n="(\d+)"', raw)}


def fixture_docs() -> dict[str, dict]:
    """The six hand-built sections, as board.json holds them."""
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


def test_a_view_with_no_fetch_says_it_has_no_copy(tmp_path: Path) -> None:
    """Protects the page on a host that cannot fetch the board.

    The page used to fall back on a copy of the board built into it. That copy
    is gone, so the banner has to say the page carries none rather than drawing
    an empty board as if it were the live one.
    """
    ids = run_without_fetch(tmp_path)
    banner = text(ids, "source")
    assert banner.startswith("Showing no board data.")
    assert "This view cannot reach the live board" in banner
    assert "the page carries no copy of its own" in banner
    assert_no_board_data(ids)


def test_a_board_with_no_sections_says_the_board_is_empty(tmp_path: Path) -> None:
    """Protects the page from a board.json holding none of the six sections.

    Every section missing gets its own sentence rather than a list naming all
    six.
    """
    ids = draw(tmp_path, dict.fromkeys(SECTIONS))
    banner = text(ids, "source")
    assert banner == "Showing no board data. The live board holds no section yet."
    assert_no_board_data(ids)


def test_six_valid_sections_draw_the_live_board(tmp_path: Path) -> None:
    """Protects the path every viewer takes once the file holds a board.

    Fixture issue 90501 has an open pull request, so it belongs in flight and nowhere
    else. Fixture issue 90502 is the one card the fixture ranks, so the default view draws
    it in the build order and hides the other three.
    """
    ids = draw(tmp_path, fixture_docs())
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
    ids = draw(tmp_path, docs)

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
    ids = draw(tmp_path, docs)
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
    ids = draw(tmp_path, docs)
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
    ids = draw(tmp_path, docs)

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
    ids = draw(tmp_path, docs)

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
    docs["working"]["items"].append({"n": 90505, "kind": kind})
    ids = draw(tmp_path, docs)

    assert 90505 in cards(ids, "flow")
    tag = _card_tag(ids, "flow", 90505)
    session = "build session" if kind == "build" else "decompose loop"
    assert f"A {session} is working it." in tag
    assert "still on the branch" not in tag
    assert "still revising its plan" not in tag


@pytest.mark.parametrize("missing", SECTIONS)
def test_one_missing_section_is_named_and_draws_nothing(tmp_path: Path, missing: str) -> None:
    """Protects a board whose file holds five of the six sections.

    The page goes live only on all six, so a partial set names what is missing
    and draws no board, rather than claiming to show a copy it no longer has.
    """
    docs = fixture_docs()
    docs[missing] = None
    ids = draw(tmp_path, docs)
    banner = text(ids, "source")
    assert banner == f"Showing no board data. The live board is missing {missing}."
    assert_no_board_data(ids)


def test_every_missing_section_is_named(tmp_path: Path) -> None:
    """Protects the banner's list when more than one section is missing.

    An earlier page named only the last section reported absent, so a board
    missing two sections told the reader about one of them.
    """
    docs = fixture_docs()
    docs["prs"] = None
    docs["next"] = None
    ids = draw(tmp_path, docs)
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
    ids = draw(tmp_path, docs)
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
    ids = draw(tmp_path, docs)
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
    lost = fixture_docs()
    lost["state"] = None
    ids, _ = run_fetch_page(tmp_path, [served(fixture_docs()), served(lost)])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (board.json is missing state).")
    assert "What is shown is the last live data" in banner
    assert cards(ids, "flow") == {90501}
    assert not ids["flightsec"]["hidden"]


def test_a_live_board_still_loading_says_so_at_once(tmp_path: Path) -> None:
    """Protects the view between opening the page and the first answer.

    The page carries no copy, so a viewer would see a blank page until the
    fetch answers. The banner says the board has not arrived yet instead.
    """
    ids, _ = run_fetch_page(tmp_path, [{"never": True}])
    assert text(ids, "source") == (
        "Showing no board data. The live board has not arrived yet, "
        "and the page carries no copy of its own."
    )
    assert_no_board_data(ids)


def test_a_draw_that_throws_after_live_data_keeps_the_last_board(tmp_path: Path) -> None:
    """Protects the last good board when a later write breaks the drawing code.

    The banner says what is shown is the last live data, so the board must
    still be drawn rather than hidden behind that claim.
    """
    broken = fixture_docs()["tracker"]
    for item in broken["items"]:
        item["after"] = 7
    board = fixture_docs()
    board["tracker"] = broken
    ids, _ = run_fetch_page(tmp_path, [served(fixture_docs()), served(board)])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (a live section could not be drawn).")
    assert "What is shown is the last live data" in banner
    assert not ids["flightsec"]["hidden"]
    assert cards(ids, "flow") == {90501}


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
    docs["working"]["items"].append({"n": 90504, "kind": "build"})
    ids = draw(tmp_path, docs)

    assert 90504 in cards(ids, "flow")
    tag = _card_tag(ids, "flow", 90504)
    assert "It needs a decision, not a session." not in tag
    assert "needs a decision, not a session" not in text(ids, "flow")
    assert "plan-" not in tag
    assert "Its build session is still on the branch." in tag


@pytest.mark.parametrize("state", ["open", "merged"])
def test_the_flow_legend_explains_a_re_measured_plan_only_where_a_card_draws_it(
    tmp_path: Path, state: str
) -> None:
    """Protects the flow legend from glossing a plan marker no card draws.

    Fixture issue 90503 gets a finished plan, a decompose loop on it and a pull
    request, either open or merged with no ``Part of``. Either one suppresses
    the plan marker, so the legend has nothing to explain. It used to ask
    ``PLANNED`` rather than the marker and explained "a second loop re-measuring
    it" anyway. With the pull request gone, the card draws the marker and the
    entry comes back, which shows the test can see it.
    """
    docs = fixture_docs()
    docs["planned"]["items"].append({"n": 90503, "passes": 2, "ready": "build"})
    docs["working"]["items"].append({"n": 90503, "kind": "decompose"})
    docs["prs"]["items"].append(_pull(90602, 90503, state, linked=False, part_of=False))
    ids = draw(tmp_path, docs)

    assert 90503 in cards(ids, "flow")
    assert "plan-" not in _card_tag(ids, "flow", 90503)
    flowkey = text(ids, "flowkey")
    assert "a session is on it now" in flowkey
    assert "a second loop re-measuring it" not in flowkey

    docs["prs"]["items"] = [p for p in docs["prs"]["items"] if p["pr"] != 90602]
    ids = draw(tmp_path, docs)
    assert "plan-build" in _card_tag(ids, "flow", 90503)
    assert "a second loop re-measuring it" in text(ids, "flowkey")


@pytest.mark.parametrize(("state", "part_of"), [("closed", False), ("merged", True)])
def test_the_label_names_the_pull_request_that_holds_the_card(
    tmp_path: Path, state: str, part_of: bool
) -> None:
    """Protects the label from naming a pull request that does not hold the card.

    Fixture issue 90505 gets a closed pull request, or a merged ``Part of``,
    listed ahead of one merged with no ``Part of``. Only that last one holds
    the card for a close by hand, so the label names it, rather than whichever
    entry ``prs`` lists first or the first one that merged.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] == 90505:
            card["needs"] = []
    docs["next"]["items"].append({"issue": 90505, "band": 3, "ready": "build", "why": "x"})
    docs["prs"]["items"] += [
        _pull(90602, 90505, state, linked=False, part_of=part_of),
        _pull(90603, 90505, "merged", linked=False, part_of=False),
    ]
    ids = draw(tmp_path, docs)

    tag = _card_tag(ids, "board", 90505)
    assert "Pull request 90603 is merged against it." in tag
    assert "Pull request 90602" not in tag


def _show_all_page(tmp_path: Path) -> Path:
    """A copy of the page that reads its show-all setting as on.

    The stub has no ``localStorage``, so the page's own lookup fails and it
    draws the short view. A deferred card is in the short view only through
    the ranking, which leaves it out on purpose, so reading one needs this.
    """
    page = tmp_path / "board-all.html"
    shim = 'var localStorage = { getItem: function () { return "1"; }, setItem: function () {} };'
    page.write_text(
        PAGE.read_text(encoding="utf-8").replace("<script>", "<script>\n" + shim, 1),
        encoding="utf-8",
    )
    return page


@pytest.mark.parametrize(
    ("kind", "reason"),
    [
        ("decision", "need a decision rather than a session"),
        ("deferred", "be deferred on purpose"),
        ("parent", "be a parent whose children carry the work"),
    ],
)
def test_a_card_held_for_a_close_by_hand_gives_no_kind_reason(
    tmp_path: Path, kind: str, reason: str
) -> None:
    """Protects the board note's reasons from a kind the card no longer shows.

    Fixture issue 90504 is the only card in the first column, given each kind
    in turn. A pull request merged against it with no ``Part of`` hides its
    kind word, so the note holds it for the close by hand and gives no reason
    drawn from its kind. Without the pull request the kind reason returns,
    which shows the test can see it.
    """
    page = _show_all_page(tmp_path)
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] == 90504:
            card["kind"] = kind
    docs["prs"]["items"].append(_pull(90602, 90504, "merged", linked=False, part_of=False))
    ids = draw(tmp_path, docs, page=page)

    note = text(ids, "boardnote")
    assert "out of 1 in the first column" in note
    assert "have merged and need only closing by hand" in note
    assert reason not in note

    docs["prs"]["items"] = [p for p in docs["prs"]["items"] if p["pr"] != 90602]
    ids = draw(tmp_path, docs, page=page)
    assert reason in text(ids, "boardnote")


def test_a_planned_card_held_for_a_close_by_hand_keeps_its_plan_position(
    tmp_path: Path,
) -> None:
    """Protects the sort's decision to read ``PLANNED`` rather than the marker.

    Fixture issues 90503 and 90505 both sit in the first column, and the
    ranking puts 90505 first. 90503 has a finished plan and a pull request
    merged with no ``Part of``, so it draws no plan marker. The sort still
    puts it first, because a card keeps its position whether or not its
    marker is drawn, which the comment on ``landed`` records as accepted.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] in (90503, 90505):
            card["needs"] = []
    docs["next"]["items"] += [
        {"issue": 90505, "band": 2, "ready": "build", "why": "x"},
        {"issue": 90503, "band": 3, "ready": "build", "why": "Only its close is left."},
    ]
    docs["planned"]["items"].append({"n": 90503, "passes": 2, "ready": "build"})
    docs["prs"]["items"].append(_pull(90602, 90503, "merged", linked=False, part_of=False))
    ids = draw(tmp_path, docs)

    raw = ids["board"]["html"]
    assert "plan-" not in _card_tag(ids, "board", 90503)
    assert raw.index('data-n="90503"') < raw.index('data-n="90505"')


def _with_needs(docs: dict, needs: dict[int, list[int]]) -> dict:
    """The fixture with some cards' ``needs`` replaced."""
    for card in docs["tracker"]["items"]:
        if card["n"] in needs:
            card["needs"] = needs[card["n"]]
    return docs


def test_a_card_waiting_on_two_issues_is_not_called_behind_one_thing(tmp_path: Path) -> None:
    """Protects the depth sentence from reading as a count of blockers.

    On 2026-10-11 issue 303 gained needs of 249 and 510, both open and neither
    waiting on anything. The note still said nothing sat behind more than one
    thing, and the column it sat in said one thing had to land first. Fixture
    issue 90505 is given the same shape here, waiting on 90501 and 90504, and
    90503 is cleared so that no chain runs two steps.
    """
    docs = _with_needs(fixture_docs(), {90503: [], 90505: [90501, 90504]})
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path))

    note = text(ids, "boardnote")
    assert "more than one thing" not in note
    assert (
        "No card waits on an issue that waits on another, so none is more than 1 step behind."
        in note
    )
    assert "#90505 waits on 2 open issues at once, #90501 and #90504." in note
    board = text(ids, "board")
    assert "one thing has to land first" not in board
    for phrase in (
        "One step behind",
        "what these wait on waits on no open issue",
        "Two steps behind or more",
        "something these wait on waits on another",
    ):
        assert phrase in board
    raw = ids["board"]["html"]
    second = raw.split('<div class="col k1')[1].split('<div class="col k2')[0]
    assert 'data-n="90505"' in second


@pytest.mark.parametrize(
    ("needs", "sentence"),
    [
        ({}, "2 cards wait on an issue that waits on another, and the deepest is 2 steps behind."),
        (
            {90504: [90503]},
            "3 cards wait on an issue that waits on another, and the deepest is 3 steps behind.",
        ),
    ],
)
def test_the_depth_sentence_names_the_longest_chain(
    tmp_path: Path, needs: dict, sentence: str
) -> None:
    """Protects the deep branch from calling two steps the deepest there is.

    The fixture chains 90503 and 90505 behind 90502, which waits on 90501, so
    its longest chain is two steps. Putting 90504 behind 90503 makes it three,
    which the sentence used to call "the deepest the graph goes" at two. The
    short view draws only 90502, so it counts the hidden cards and says so.
    """
    docs = _with_needs(fixture_docs(), needs)
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path))
    note = text(ids, "boardnote")
    assert sentence in note
    assert "Counting the hidden issues" not in note.split(sentence)[0]

    ids = draw(tmp_path, docs)
    assert "Counting the hidden issues, " + sentence in text(ids, "boardnote")


def test_several_cards_waiting_on_several_issues_are_each_named(tmp_path: Path) -> None:
    """Protects the plural branch and the pointer at cards the short view hides.

    Fixture issues 90503 and 90505 each wait on two open issues here, and the
    short view draws neither, so the note names both and says they are hidden.
    """
    docs = _with_needs(fixture_docs(), {90503: [90502, 90504], 90505: [90501, 90504]})
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path))
    note = text(ids, "boardnote")
    assert "#90503 and #90505 each wait on more than one open issue." in note
    assert "hidden in this view" not in note

    ids = draw(tmp_path, docs)
    assert "#90503 and #90505 are hidden in this view" in text(ids, "boardnote")


def test_a_board_where_nothing_waits_says_no_depth(tmp_path: Path) -> None:
    """Protects the empty branch, where no card waits on any open issue.

    The second and third columns are then empty, so the note gives no depth at
    all, and the freeing clause is what says nothing waits on anything.
    """
    docs = _with_needs(fixture_docs(), {90502: [], 90503: [], 90505: []})
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path))
    note = text(ids, "boardnote")
    assert "behind." not in note
    assert "waits on an issue that waits on another" not in note
    assert "No card here is waiting on another" in note


@pytest.mark.parametrize("show_all", [False, True], ids=["short view", "full view"])
def test_a_board_where_nothing_waits_points_at_no_card(tmp_path: Path, show_all: bool) -> None:
    """Protects the two pointers from naming every card when nothing frees anything.

    With every ``needs`` empty, each card frees no other, so the cards tied at
    the top are all of them. The note used to say no card was waiting and then
    point at fixture issue 90501 in flight, and in the short view at 90503,
    90504 and 90505 as hidden, as though each one freed the most. Neither
    pointer names a card here, and the freeing clause still speaks.
    """
    docs = _with_needs(fixture_docs(), {n: [] for n in (90501, 90502, 90503, 90504, 90505)})
    page = _show_all_page(tmp_path) if show_all else PAGE
    note = text(draw(tmp_path, docs, page=page), "boardnote")
    assert "No card here is waiting on another" in note
    assert "rather than in a column here" not in note
    assert "hidden in this view" not in note


@pytest.mark.parametrize("show_all", [False, True], ids=["short view", "full view"])
def test_the_card_freeing_the_most_is_pointed_at_in_flight(tmp_path: Path, show_all: bool) -> None:
    """Protects the in-flight pointer on a board where something waits.

    In the fixture as shipped, issue 90501 has an open branch and frees 90502,
    90503 and 90505, so it frees the most while the In flight section draws
    it. The note names it and says where it is, in either view.
    """
    page = _show_all_page(tmp_path) if show_all else PAGE
    note = text(draw(tmp_path, fixture_docs(), page=page), "boardnote")
    assert "#90501 is the single card whose landing frees the most" in note
    assert "#90501 is in the In flight section above rather than in a column here." in note


@pytest.mark.parametrize("show_all", [False, True], ids=["short view", "full view"])
def test_a_card_freeing_the_most_in_a_column_is_not_pointed_at_in_flight(
    tmp_path: Path, show_all: bool
) -> None:
    """Protects the in-flight pointer from naming a card the columns drew.

    With pull request 90601 taken out of the fixture, issue 90501 has no open
    branch, so a column draws it while it still frees 90502, 90503 and 90505.
    It is also ranked, because the short view draws only ranked cards and would
    otherwise hide it. The note names it as freeing the most and says nothing
    about the In flight section, in either view.
    """
    docs = fixture_docs()
    docs["prs"]["items"] = [p for p in docs["prs"]["items"] if p["issue"] != 90501]
    docs["next"]["items"].append(
        {"issue": 90501, "band": 1, "ready": "build", "why": "Nothing it waits on is open."}
    )
    page = _show_all_page(tmp_path) if show_all else PAGE
    ids = draw(tmp_path, docs, page=page)
    note = text(ids, "boardnote")
    _card_tag(ids, "board", 90501)
    assert "#90501 is the single card whose landing frees the most" in note
    assert "rather than in a column here" not in note


def test_a_shallow_graph_says_when_it_counts_hidden_cards(tmp_path: Path) -> None:
    """Protects the shallow branch's qualifier, which the deep branch already had.

    Fixture issue 90503 waits on 90501 here and nothing else waits on anything.
    The short view draws only 90502, so its second column is empty while a
    hidden card sits one step behind. The sentence says it is counting hidden
    cards, and the freeing clause after it then says it is counting them too.
    The clause naming a card with several blockers can sit between the two, so
    the second says which cards it means rather than "them".
    """
    docs = _with_needs(fixture_docs(), {90502: [], 90503: [90501], 90505: []})
    ids = draw(tmp_path, docs)
    note = text(ids, "boardnote")
    assert (
        "Counting the hidden issues, no card waits on an issue that waits on another, "
        "so none is more than 1 step behind."
    ) in note
    assert "Counting the hidden issues too, #90501" in note

    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path))
    assert "Counting the hidden issues" not in text(ids, "boardnote")


@pytest.mark.parametrize(
    ("needs", "card", "line"),
    [
        ({}, 90503, "#90503 · waits on 1 directly and 2 along the whole chain"),
        ({}, 90501, "#90501 · 1 waiting on it directly and 3 along the whole chain"),
        ({90505: [90501, 90504]}, 90505, "#90505 · waits on 2 Clear"),
    ],
)
def test_the_chain_bar_tells_direct_blockers_from_the_chain(
    tmp_path: Path, needs: dict, card: int, line: str
) -> None:
    """Protects the chain bar from counting a whole chain as blockers.

    The fixture chains 90503 behind 90502 behind 90501, so 90503 waits on one
    issue directly and two along the chain, and 90501 has one card waiting on
    it directly and three in all. The bar used to say "waits on 2" for 90503,
    while its own card named one issue. A card whose blockers wait on nothing
    keeps the bare count, since the two numbers agree.
    """
    docs = _with_needs(fixture_docs(), needs)
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path), click=card)
    assert line in text(ids, "chainbar")


FREE_CLAIM = "can be taken on its own"


def _with_fields(docs: dict, n: int, **fields: object) -> dict:
    """The fixture with one card's fields replaced."""
    for card in docs["tracker"]["items"]:
        if card["n"] == n:
            card.update(fields)
    return docs


def _picked(tmp_path: Path, docs: dict, card: int) -> str:
    """What the chain bar says once a card is picked.

    One call writes both bars, so the In flight copy has to match the build
    order's. A second path writing only one of them would break that.
    """
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path), click=card)
    said = text(ids, "chainbar")
    assert said == text(ids, "flowchain")
    return said


def _picked_sentence(tmp_path: Path, docs: dict, card: int) -> str:
    """The chain bar's whole sentence once a card is picked, without its button.

    The sentence is the bar's first ``span``, so reading that span lets a test
    compare the whole sentence without also pinning the Clear button's label.
    """
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path), click=card)
    assert text(ids, "chainbar") == text(ids, "flowchain")
    found = re.match(r"\s*<span>(.*?)</span>", ids["chainbar"]["html"], re.S)
    assert found, ids["chainbar"]["html"]
    return text({"s": {"html": found.group(1)}}, "s")


def _session_on(docs: dict, n: int, kind: str = "build") -> dict:
    docs["working"]["items"].append({"n": n, "kind": kind})
    return docs


def _planned(docs: dict, n: int, ready: str) -> dict:
    docs["planned"]["items"].append({"n": n, "passes": 2, "ready": ready})
    return docs


def _on_branch(kind: str) -> dict:
    """Fixture issue 90501 with 90502's blocker removed and the given kind.

    90501 carries the fixture's open pull request, so with nothing waiting on
    it the chain bar takes the unlinked branch for a card with a branch open.
    """
    return _with_fields(_with_needs(fixture_docs(), {90502: []}), 90501, kind=kind)


def _merged_whole(docs: dict, n: int) -> dict:
    docs["prs"]["items"].append(_pull(90602, n, "merged", linked=False, part_of=False))
    return docs


@pytest.mark.parametrize(
    ("docs", "card", "reason"),
    [
        (
            _with_fields(fixture_docs(), 90504, kind="decision"),
            90504,
            "it needs a decision rather than a session",
        ),
        (_with_fields(fixture_docs(), 90504, kind="deferred"), 90504, "it is deferred on purpose"),
        (
            _with_fields(fixture_docs(), 90504, kind="parent"),
            90504,
            "it is a parent whose children carry the work",
        ),
        (
            _session_on(_with_fields(fixture_docs(), 90504, kind="ready"), 90504),
            90504,
            "it already has somebody on it",
        ),
        (
            _session_on(_with_fields(fixture_docs(), 90504, kind="ready"), 90504, "decompose"),
            90504,
            "it already has somebody on it",
        ),
        (
            _merged_whole(_with_fields(fixture_docs(), 90504, kind="ready"), 90504),
            90504,
            "it has merged and needs only closing by hand",
        ),
        (
            _with_needs(fixture_docs(), {90502: []}),
            90501,
            "it is already written and waiting on a review",
        ),
        (
            _session_on(_with_fields(fixture_docs(), 90504, kind="deferred"), 90504),
            90504,
            "it is deferred on purpose and already has somebody on it",
        ),
        (_on_branch("decision"), 90501, "it is already written and waiting on a review"),
        (_on_branch("deferred"), 90501, "it is already written and waiting on a review"),
        (_on_branch("parent"), 90501, "it is already written and waiting on a review"),
        (
            _merged_whole(
                _planned(_with_fields(fixture_docs(), 90504, kind="ready"), 90504, "decide"), 90504
            ),
            90504,
            "it has merged and needs only closing by hand",
        ),
        (
            _session_on(
                _planned(_with_fields(fixture_docs(), 90504, kind="ready"), 90504, "decide"),
                90504,
                "decompose",
            ),
            90504,
            "it already has somebody on it",
        ),
    ],
    ids=[
        "decision",
        "deferred",
        "parent",
        "session",
        "loop",
        "close-by-hand",
        "open-branch",
        "deferred-with-session",
        "decision-on-branch",
        "deferred-on-branch",
        "parent-on-branch",
        "owner-plan-merged",
        "owner-plan-under-a-loop",
    ],
)
def test_an_unlinked_card_the_board_holds_back_is_not_called_free(
    tmp_path: Path, docs: dict, card: int, reason: str
) -> None:
    """Protects the chain bar from calling a card free that the board holds back.

    The bar used to say any card with no open ``needs`` either way "can be
    taken on its own", reading nothing but ``needs``. Fixture issue 90504 is
    such a card, and the cases give it a kind word saying not to start it, a
    build session, a decompose loop, or a pull request merged with no ``Part
    of``. With 90502's blocker removed, 90501 is one too and carries its open
    pull request. Each reason is the one the board note's free list holds that
    card back for, in the form a sentence about one card takes, and two reasons
    on one card are joined with "and" because both apply to it.

    A card with an open branch draws no kind word, because the branch already
    answered what kind of work it was. So the three cases with a branch give
    only the branch as the reason, whatever the kind, and the bar gives no
    reason the card itself withholds. A plan whose one question is the owner's
    is a reason only where the card draws that marker, so the last two cases,
    one merged with no ``Part of`` and one under a decompose loop, give only
    the reason each already has.
    """
    said = _picked(tmp_path, docs, card)
    assert FREE_CLAIM not in said
    assert (
        f"#{card} is linked to nothing else here, but it is not free to take, because {reason}."
        in said
    )


def test_an_unlinked_card_with_nothing_holding_it_can_be_taken_on_its_own(
    tmp_path: Path,
) -> None:
    """Protects the free claim where it is true, so a fix cannot simply delete it.

    Fixture issue 90504 as ordinary work, with no session and no pull request,
    is the one card the board note lists as free, and the bar says the same.
    """
    docs = _with_fields(fixture_docs(), 90504, kind="ready")
    ids = draw(tmp_path, docs, page=_show_all_page(tmp_path), click=90504)
    assert "out of 1 in the first column: #90504." in text(ids, "boardnote")
    said = _picked(tmp_path, docs, 90504)
    assert "#90504 is linked to nothing else here, so it can be taken on its own." in said


def test_an_unlinked_card_of_no_listed_kind_says_only_what_its_links_show(
    tmp_path: Path,
) -> None:
    """Protects the bar from claiming freedom for a kind the free list never reads.

    A card blocked on data sits in the fourth column, which the board note's
    free list does not cover, so neither a free claim nor a reason applies.
    The bar says what the links show and stops.
    """
    docs = _with_fields(fixture_docs(), 90504, kind="data")
    said = _picked(tmp_path, docs, 90504)
    assert "#90504 is linked to nothing else here." in said
    assert FREE_CLAIM not in said
    assert "because" not in said


@pytest.mark.parametrize(
    ("ready", "line"),
    [
        ("build", "#90504 is linked to nothing else here, so it can be taken on its own."),
        (
            "decide",
            "#90504 is linked to nothing else here, but it is not free to take, "
            "because it waits on a question only the owner can answer.",
        ),
    ],
    ids=["ready-to-build", "waits-on-the-owner"],
)
def test_a_planned_card_waiting_on_the_owner_is_not_called_free(
    tmp_path: Path, ready: str, line: str
) -> None:
    """Protects the chain bar from contradicting the In flight note on a plan.

    Fixture issue 90504 as ordinary work gets a finished plan and nothing on
    it, so it sits under "Planned, no builder". With one question left for the
    owner, the In flight note says it waits on a question only the owner can
    answer, and the bar used to call it free to take on its own anyway. A plan
    ready to build is the control, where both say the card is free.
    """
    docs = _planned(_with_fields(fixture_docs(), 90504, kind="ready"), 90504, ready)
    said = _picked(tmp_path, docs, 90504)
    assert line in said
    flownote = text(draw(tmp_path, docs), "flownote")
    if ready == "decide":
        assert "#90504 is planned, and waits on a question only the owner can answer" in flownote
    else:
        assert "#90504 is planned and free for anyone to pick up" in flownote


@pytest.mark.parametrize(
    ("kind", "ready", "reason"),
    [
        ("decision", "build", "needs a decision rather than a session"),
        ("deferred", "build", "is deferred on purpose"),
        ("parent", "build", "is a parent whose children carry the work"),
        (
            "deferred",
            "decide",
            "is deferred on purpose and waits on a question only the owner can answer",
        ),
    ],
    ids=["decision", "deferred", "parent", "deferred-and-owner"],
)
def test_a_planned_card_of_a_held_kind_is_not_called_free_in_flight(
    tmp_path: Path, kind: str, ready: str, reason: str
) -> None:
    """Protects the In flight note from calling a planned card free that its kind holds back.

    Fixture issue 90504 gets a kind word saying not to start it, and a finished
    plan with nothing on it. So it sits under "Planned, no builder". The note
    used to read only whether the plan waited on the owner, so it called the
    card "planned and free for anyone to pick up" while the chain bar said it
    was not free to take. Issue 573 recorded it. The note now gives the reasons
    the bar gives, in the same words, and both are pinned here so neither can
    drift from the other.
    """
    docs = _planned(_with_fields(fixture_docs(), 90504, kind=kind), 90504, ready)
    flownote = text(draw(tmp_path, docs), "flownote")
    assert "free for anyone to pick up" not in flownote
    assert f"#90504 is planned, and {reason}." in flownote
    said = _picked(tmp_path, docs, 90504)
    assert FREE_CLAIM not in said
    assert f"but it is not free to take, because it {reason}." in said


def test_a_planned_card_blocked_on_data_is_not_called_free_in_flight(tmp_path: Path) -> None:
    """Protects the note for a kind no row of the board's reasons names.

    A card blocked on data with a finished plan and no open blocker sits under
    "Planned, no builder" as well. `takeable` turns it down while no reason
    holds it, so the chain bar says only what its links show. The note says it
    is not free and gives no reason, rather than calling it free.
    """
    docs = _planned(_with_fields(fixture_docs(), 90504, kind="data"), 90504, "build")
    flownote = text(draw(tmp_path, docs), "flownote")
    assert "free for anyone to pick up" not in flownote
    assert "#90504 is planned, and is not free to take." in flownote
    assert FREE_CLAIM not in _picked(tmp_path, docs, 90504)


def test_planned_cards_held_for_one_reason_share_a_sentence(tmp_path: Path) -> None:
    """Protects the grouping of held planned cards by the reasons that hold them.

    Fixture issue 90504 is a decision, and 90503 and 90505 are deferred. All
    three get a plan ready to build and nothing open ahead of them, so none is
    free. The two deferred cards share one sentence, which says each of them is
    deferred, and that sentence says "too" because the one before it already
    said a card was planned.
    """
    docs = _with_needs(fixture_docs(), {90503: [], 90505: []})
    docs = _with_fields(docs, 90503, kind="deferred")
    docs = _with_fields(docs, 90505, kind="deferred")
    for n in (90503, 90504, 90505):
        docs = _planned(docs, n, "build")
    flownote = text(draw(tmp_path, docs), "flownote")
    assert (
        "#90504 is planned, and needs a decision rather than a session. "
        "#90503 and #90505 are planned too, and each is deferred on purpose." in flownote
    )


def test_two_planned_cards_held_for_no_named_reason_share_one_sentence(tmp_path: Path) -> None:
    """Protects the plural of the sentence that gives no reason.

    Fixture issues 90504 and 90505 are both blocked on data, with plans ready
    to build and nothing open ahead of them. "Each is not free to take" can be
    read as "not every one is free", so the plural says none of them is.
    """
    docs = _with_needs(fixture_docs(), {90505: []})
    for n in (90504, 90505):
        docs = _planned(_with_fields(docs, n, kind="data"), n, "build")
    flownote = text(draw(tmp_path, docs), "flownote")
    assert "#90504 and #90505 are planned, and none of them is free to take." in flownote


def test_the_in_flight_note_joins_free_and_held_planned_cards(tmp_path: Path) -> None:
    """Protects the joins when free and held planned cards share the column.

    Fixture issues 90503 and 90505 are ordinary work and 90504 is deferred.
    All three get a plan ready to build. The free sentence comes first, so the
    held one says "too", and two free cards take the plural.
    """
    docs = _with_needs(fixture_docs(), {90503: [], 90505: []})
    docs = _with_fields(docs, 90503, kind="ready")
    docs = _with_fields(docs, 90505, kind="ready")
    docs = _with_fields(docs, 90504, kind="deferred")
    for n in (90503, 90504, 90505):
        docs = _planned(docs, n, "build")
    flownote = text(draw(tmp_path, docs), "flownote")
    assert (
        "#90503 and #90505 are planned and free for anyone to pick up. "
        "#90504 is planned too, and is deferred on purpose." in flownote
    )


@pytest.mark.parametrize(
    ("after", "card", "line"),
    [
        (
            {90504: [90502]},
            90504,
            "Nothing here blocks #90504 or waits on it, so it can be taken on its own. "
            "It should land after #90502.",
        ),
        (
            {90503: [90504]},
            90504,
            "Nothing here blocks #90504 or waits on it, so it can be taken on its own. "
            "#90503 should land after it.",
        ),
        (
            {90504: [90502, 90503], 90501: [90504], 90505: [90504]},
            90504,
            "Nothing here blocks #90504 or waits on it, so it can be taken on its own. "
            "It should land after #90502 and #90503. #90501 and #90505 should land after it.",
        ),
    ],
    ids=["holds-after", "named-by-after", "two-each-way"],
)
def test_a_card_tied_by_an_ordering_is_not_called_linked_to_nothing(
    tmp_path: Path, after: dict, card: int, line: str
) -> None:
    """Protects the bar from calling a card with a ``Board after:`` tie unlinked.

    ``after`` is an ordering nothing enforces, so it leaves a card free to
    take, and the board note's free list does not read it. It is still a link,
    though, and the card itself says it should land after the issue it names.
    So the bar names the ordering in both directions rather than saying the
    card is linked to nothing.

    The whole sentence is compared, because a substring passes a bar that adds
    a card to either list. Two targets each way pin the join, which takes
    "and" because every ordering named holds for this one card, and pin that
    no target after the first is dropped. The cards naming 90504 carry
    ``needs`` of their own, which leaves 90504's bar on its unlinked branch,
    since nothing 90504 waits on or feeds is among them.
    """
    docs = _with_fields(fixture_docs(), 90504, kind="ready")
    for n, names in after.items():
        docs = _with_fields(docs, n, after=names)
    assert _picked_sentence(tmp_path, docs, card) == line


def test_an_ordering_on_an_issue_not_on_the_board_is_no_link(tmp_path: Path) -> None:
    """Protects the bar from naming an ordering on an issue the board does not hold.

    Fixture issue 90504 names 99999 in ``after``, an issue that is not open on
    the tracker, as one already closed would not be. The card itself draws no
    ordering for it, so the bar keeps the plain free sentence and says nothing
    about landing after it.
    """
    docs = _with_fields(fixture_docs(), 90504, kind="ready", after=[99999])
    assert (
        _picked_sentence(tmp_path, docs, 90504)
        == "#90504 is linked to nothing else here, so it can be taken on its own."
    )


def test_the_board_note_lists_two_held_cards_reasons_in_table_order(tmp_path: Path) -> None:
    """Protects the note's reasons when two first-column cards are held for different ones.

    Fixture issue 90504 is deferred and 90505, with its blocker removed, needs
    a decision. Both sit in the first column of the Show all view. Each reason
    comes from a different card, so the note offers both as alternatives, in
    the order of the table that holds them. A note that kept only the reasons
    every held card shared would offer neither.
    """
    docs = _with_fields(fixture_docs(), 90504, kind="deferred")
    docs = _with_fields(docs, 90505, kind="decision", needs=[])
    note = text(draw(tmp_path, docs, page=_show_all_page(tmp_path)), "boardnote")
    assert (
        "because a card can need a decision rather than a session or be deferred on purpose, "
        "and depth alone does not say what to pick." in note
    )


def test_counting_too_names_the_hidden_issues_after_a_named_card(tmp_path: Path) -> None:
    """Protects the freeing clause's prefix from pointing at the wrong cards.

    Fixture issue 90505 waits on 90502 and 90504 here, so a clause naming it and
    both blockers sits between the depth sentence and the freeing clause in the
    short view. A bare "Counting them too" there read as counting 90502 and
    90504 rather than the hidden issues.
    """
    docs = _with_needs(fixture_docs(), {90505: [90502, 90504]})
    note = text(draw(tmp_path, docs), "boardnote")
    assert "#90505 waits on 2 open issues at once, #90502 and #90504." in note
    assert "Counting them too" not in note
    assert "Counting the hidden issues too, #90501" in note


def test_only_open_blockers_of_cards_in_the_columns_are_counted(tmp_path: Path) -> None:
    """Protects which blockers and which cards the depth and blocker clauses read.

    Issue numbers 99998 and 99999 are not in the tracker, so they stand for
    closed issues, and neither counts. Fixture issue 90504 becomes a data card
    waiting on two open issues and sitting three steps deep. A data card sits in
    the fourth column, outside the chain the sentence measures, so it is neither
    named nor allowed to deepen the chain past 90503's two steps.
    """
    docs = _with_needs(
        fixture_docs(),
        {90503: [90502, 99998], 90505: [90501, 90502, 99999], 90504: [90503, 90505]},
    )
    for card in docs["tracker"]["items"]:
        if card["n"] == 90504:
            card["kind"] = "data"
    note = text(draw(tmp_path, docs, page=_show_all_page(tmp_path)), "boardnote")
    assert "#90505 waits on 2 open issues at once, #90501 and #90502." in note
    assert "#99999" not in note
    assert "#90503 waits on" not in note
    assert "#90504" not in note.split("free for a session")[1].split("frees the most")[0]
    assert "and the deepest is 2 steps behind." in note


def test_one_deep_card_takes_a_singular_verb(tmp_path: Path) -> None:
    """Protects the verb's agreement when exactly one card is two steps deep."""
    docs = _with_needs(fixture_docs(), {90505: []})
    note = text(draw(tmp_path, docs, page=_show_all_page(tmp_path)), "boardnote")
    assert (
        "1 card waits on an issue that waits on another, and the deepest is 2 steps behind." in note
    )


def test_the_hidden_pointer_lists_top_cards_and_blocked_cards_in_order(tmp_path: Path) -> None:
    """Protects the pointer when it names both kinds of hidden card.

    Fixture issues 90504 and 90505 each free 90503, which waits on both of
    them, and the short view draws none of the three. The pointer names the
    cards that free the most and the card with several blockers together, in
    issue order rather than in the order the two lists were joined.
    """
    docs = _with_needs(fixture_docs(), {90502: [], 90503: [90505, 90504], 90505: []})
    note = text(draw(tmp_path, docs), "boardnote")
    assert "#90503, #90504 and #90505 are hidden in this view" in note


def test_a_board_with_nothing_in_the_chain_columns_gives_no_depth(tmp_path: Path) -> None:
    """Protects the longest chain's floor when no card is in the first three columns.

    Every card but the one in flight becomes a data card, so the chain the
    sentence measures holds no card at all and its longest is zero rather than
    an empty maximum.
    """
    docs = fixture_docs()
    for card in docs["tracker"]["items"]:
        if card["n"] != 90501:
            card["kind"] = "data"
    note = text(draw(tmp_path, docs, page=_show_all_page(tmp_path)), "boardnote")
    assert "Infinity" not in note
    assert "behind." not in note


# ---- The fetch path, for the board on GitHub Pages ----


def fixture_board(**state: object) -> dict:
    """The six fixture documents as one board.json, with ``state`` fields added."""
    board = fixture_docs()
    board["state"].update(state)
    return board


def _iso(minutes_ago: float) -> str:
    stamp = datetime.now(UTC) - timedelta(minutes=minutes_ago)
    return stamp.strftime("%Y-%m-%dT%H:%M:%SZ")


def test_each_fetch_asks_for_a_url_no_cache_has_seen(tmp_path: Path) -> None:
    """Protects the page from reading a copy Pages' cache kept.

    Pages sends ``cache-control: max-age=600``, so a plain fetch can return a
    board ten minutes old. Each fetch carries a fresh query string and asks the
    browser to store nothing, and the timer fetches again.
    """
    _, fetches = run_fetch_page(tmp_path, [served(fixture_board())] * 3)
    assert len(fetches) == 3
    assert all(re.fullmatch(r"board\.json\?t=\d+", f["url"]) for f in fetches)
    assert all(f["cache"] == "no-store" for f in fetches)


def test_a_fresh_board_from_github_has_an_empty_banner(tmp_path: Path) -> None:
    """Protects a current board from a banner that reads as a warning.

    Until issue 533 the generator listed the fields it did not carry in
    ``lacks``, and the banner named them. Every field now comes from GitHub,
    so a ``lacks`` list left in an old file is not read, and the footer says
    the board is built rather than measured by hand.
    """
    board = fixture_board(
        source="github",
        updatedAt=_iso(1),
        longestGapMinutes=30,
        staleAfterMinutes=90,
        lacks=["the priority order"],
    )
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert ids["source"]["hidden"]
    assert text(ids, "source") == ""
    foot = text(ids, "foot")
    assert foot.startswith("Built from GitHub by an Action on each change and on a schedule")
    assert "Measured by hand" not in foot


@pytest.mark.parametrize(("minutes_ago", "stale"), [(89, False), (91, True)])
def test_a_board_older_than_its_threshold_says_it_may_be_stale(
    tmp_path: Path, minutes_ago: int, stale: bool
) -> None:
    """Protects the one warning a failed run leaves the reader.

    A failed run leaves the last board up, and a board hours stale looks
    like a fresh one. The threshold comes from the board, which takes it from
    the workflow's schedule, so the page carries no second copy of it. The
    banner names the gap between scheduled runs and says GitHub can start one
    late, because GitHub promises no cadence the page could quote as a bound.
    """
    board = fixture_board(
        source="github",
        updatedAt=_iso(minutes_ago),
        longestGapMinutes=30,
        staleAfterMinutes=90,
    )
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    banner = text(ids, "source")
    if stale:
        assert banner == (
            "This board may be stale. It was built from GitHub 1h ago. "
            "Scheduled rebuilds are due at most 30 minutes apart, and it is older than that "
            "plus an allowance for GitHub starting one late, "
            "so the Action that rebuilds it may be failing."
        )
    else:
        assert banner == ""
        assert ids["source"]["hidden"]


def test_the_banner_names_the_gap_it_was_given(tmp_path: Path) -> None:
    """Protects the banner from working the gap out from the threshold."""
    board = fixture_board(
        source="github", updatedAt=_iso(101), longestGapMinutes=20, staleAfterMinutes=100
    )
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert "Scheduled rebuilds are due at most 20 minutes apart," in text(ids, "source")


def test_a_stale_board_with_no_gap_names_no_cadence(tmp_path: Path) -> None:
    """Protects the banner from quoting a cadence the board does not carry."""
    board = fixture_board(source="github", updatedAt=_iso(91), staleAfterMinutes=90)
    ids, _ = run_fetch_page(tmp_path, [served(board)])
    assert text(ids, "source") == (
        "This board may be stale. It was built from GitHub 1h ago. "
        "The Action that rebuilds it may be failing."
    )


def test_a_first_fetch_that_fails_says_there_is_no_board(tmp_path: Path) -> None:
    """Protects a view that cannot fetch the file."""
    ids, _ = run_fetch_page(tmp_path, [{"status": 404, "body": "Not Found"}])
    assert text(ids, "source") == (
        "Showing no board data. This view cannot reach the live board, "
        "and the page carries no copy of its own."
    )
    assert_no_board_data(ids)


def _broken_board(kind: str) -> dict:
    if kind == "status":
        return {"status": 503, "body": "busy"}
    if kind == "offline":
        return {"throw": True}
    if kind == "not json":
        return {"status": 200, "body": "<html>"}
    board = fixture_board()
    if kind == "missing":
        del board["prs"]
    else:
        del board["tracker"]["items"][0]["needs"]
    return served(board)


@pytest.mark.parametrize(
    ("kind", "code"),
    [
        ("status", "board.json answered 503"),
        ("offline", "board.json could not be fetched"),
        ("not json", "board.json is not JSON"),
        ("missing", "board.json is missing prs"),
        ("unreadable", "unreadable tracker"),
    ],
)
def test_a_failed_fetch_keeps_the_last_board_and_recovers(
    tmp_path: Path, kind: str, code: str
) -> None:
    """Protects the last good board when a fetch fails after it drew.

    The board stays drawn, the banner says why updates stopped and that the
    page tries again, and the next good fetch takes the board live again.
    """
    bad = _broken_board(kind)
    ids, _ = run_fetch_page(tmp_path, [served(fixture_board()), bad])
    banner = text(ids, "source")
    assert banner.startswith(f"Live updates stopped ({code}). What is shown is the last live data")
    assert banner.endswith("The page tries again every 2 minutes.")
    assert cards(ids, "flow") == {90501}
    assert not ids["flightsec"]["hidden"]

    ids, _ = run_fetch_page(tmp_path, [served(fixture_board()), bad, served(fixture_board())])
    assert ids["source"]["hidden"]
    assert text(ids, "source") == ""


@pytest.mark.parametrize(
    ("kind", "banner"),
    [
        ("missing", "Showing no board data. The live board is missing prs."),
        ("unreadable", "section is missing fields this page needs"),
    ],
)
def test_a_first_board_the_page_refuses_draws_nothing(
    tmp_path: Path, kind: str, banner: str
) -> None:
    """Protects the first load from drawing half a board."""
    ids, _ = run_fetch_page(tmp_path, [_broken_board(kind)])
    assert banner in text(ids, "source")
    assert_no_board_data(ids)


@pytest.mark.parametrize(
    ("words", "says"),
    [
        (["success", "success"], "checks green"),
        (["success", "neutral"], "1 check reported neither way"),
        (["success", "SUCCESS"], "1 check reported neither way"),
        (["success", "skipped"], "1 check reported neither way"),
        (["FAILURE", "success"], "1 check reported neither way"),
        (["failure", "running"], "1 check failing, 1 check still running"),
    ],
)
def test_only_success_reads_as_green(tmp_path: Path, words: list[str], says: str) -> None:
    """Protects a failing check from reading as a pass.

    The page used to count three words and call every other one green, so a
    state passed through in GitHub's own spelling, such as ``FAILURE``, read as
    a pass. The generator maps every state into the page's four words, and a
    word the page does not know now reads as reported neither way.
    """
    docs = fixture_docs()
    docs["prs"]["items"][0]["rollup"] = [[f"check {i}", w] for i, w in enumerate(words)]
    ids = draw(tmp_path, docs)
    assert says in _pr_line(ids, "flow", 90601)


@pytest.mark.parametrize(("changed", "redrawn"), [(False, False), (True, True)])
def test_an_unchanged_board_json_is_not_drawn_again(
    tmp_path: Path, changed: bool, redrawn: bool
) -> None:
    """Protects what a reader picked on the board from the two-minute fetch.

    A redraw rebuilds every card, so a card picked to read its chain would be
    dropped each time the timer fired. A file identical to the last one is not
    drawn again, and a changed one is.
    """
    second = fixture_board()
    if changed:
        second["state"]["updatedAt"] = "2026-10-01T12:30:00Z"
    assert fetch_redraws(tmp_path, [served(fixture_board()), served(second)]) is redrawn


def test_a_fetched_board_that_breaks_the_drawing_code_keeps_the_last_board(
    tmp_path: Path,
) -> None:
    """Protects the last good board from a file that passes the shape check.

    ``usableSection`` leaves ``after`` unchecked, so a number there passes and
    throws while the build order draws. The page rolls back to the last good
    board, keeps trying, and the next good file goes live.
    """
    broken = fixture_board()
    for item in broken["tracker"]["items"]:
        item["after"] = 7
    ids, _ = run_fetch_page(tmp_path, [served(fixture_board()), served(broken)])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (a live section could not be drawn).")
    assert banner.endswith("The page tries again every 2 minutes.")
    assert cards(ids, "flow") == {90501}

    ids, _ = run_fetch_page(
        tmp_path, [served(fixture_board()), served(broken), served(fixture_board())]
    )
    assert text(ids, "source") == ""

    # The same broken file served again is still broken. Only a file the page
    # drew counts as the last one, so a repeat is not mistaken for it.
    ids, _ = run_fetch_page(tmp_path, [served(fixture_board()), served(broken), served(broken)])
    assert text(ids, "source").startswith(
        "Live updates stopped (a live section could not be drawn)."
    )


@pytest.mark.parametrize(
    "late",
    [
        {"status": 503, "body": "busy", "hold": True},
        {"throw": True, "hold": True},
        {**served(fixture_board()), "hold": True},
    ],
)
def test_a_slow_answer_from_an_earlier_poll_changes_nothing(tmp_path: Path, late: dict) -> None:
    """Protects a newer board from a poll that answers after a later one.

    The page polls every two minutes with nothing stopping a slow answer from
    outlasting that. Here the second poll answers last. Its failure must not
    mark the live board stopped, and its board must not draw over the third
    poll's newer one, whose open count is 6.
    """
    newer = fixture_board(updatedAt="2026-10-01T12:30:00Z")
    newer["state"]["issues"]["open"] = 6
    ids, fetches = run_fetch_page(tmp_path, [served(fixture_board()), late, served(newer)])
    assert len(fetches) == 3
    assert text(ids, "source") == ""
    assert text(ids, "strip").startswith("6 open issues")


def test_a_copy_older_than_the_board_on_screen_is_not_drawn(tmp_path: Path) -> None:
    """Protects the board from a cache serving an older copy after a newer one.

    The two copies differ in their open count, so the strip shows which one
    the page drew.
    """
    newer = fixture_board(updatedAt="2026-10-01T12:30:00Z")
    newer["state"]["issues"]["open"] = 6
    ids, _ = run_fetch_page(tmp_path, [served(newer), served(fixture_board())])
    assert text(ids, "strip").startswith("6 open issues")
    assert text(ids, "source") == ""
