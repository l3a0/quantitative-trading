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
    match = re.search(r"<script>(.*?)</script>", page.read_text(encoding="utf-8"), re.S)
    assert match, f"{page} has no inline script"
    return match.group(1)


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

    Issue 501 has an open pull request, so it belongs in flight and nowhere
    else. Issue 502 is the one card the fixture ranks, so the default view draws
    it in the build order and hides the other three.
    """
    ids = run_page(tmp_path, db=True, steps=[fixture_docs()])
    assert ids["source"]["html"] == ""
    assert ids["source"]["hidden"]
    for element in CONTENT:
        assert not ids[element]["hidden"], f"{element} is hidden on a live board"
    assert text(ids, "strip").startswith("5 open issues")
    assert cards(ids, "flow") == {501}
    assert cards(ids, "board") == {502}
    assert "3 other open issues are not in the priority order" in text(ids, "more")


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
    assert cards(ids, "flow") == {501}
    assert cards(ids, "board") == {502}
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


def test_live_data_lost_afterwards_stays_on_screen(tmp_path: Path) -> None:
    """Protects the last live board when a section disappears after it drew.

    The board stays drawn, and the banner says updates stopped and that what is
    shown is the last live data.
    """
    ids = run_page(tmp_path, db=True, steps=[fixture_docs(), {"state": None}])
    banner = text(ids, "source")
    assert banner.startswith("Live updates stopped (state removed).")
    assert "What is shown is the last live data" in banner
    assert cards(ids, "flow") == {501}
    assert not ids["flightsec"]["hidden"]


def test_no_tracked_file_links_to_a_claude_artifact() -> None:
    """Protects the repository from links to pages that stopped resolving.

    The artifacts that hosted the board and its two sibling pages became
    unreachable, and a link to one is a dead end for every reader. The pattern
    is assembled from pieces so this file does not match itself.
    """
    host = re.escape("claude" + ".ai/")
    pattern = re.compile((host + r"(?:code/)?" + "arti" + "fact/").encode())
    listed = subprocess.run(
        ["git", "ls-files", "-z"], cwd=REPO_ROOT, capture_output=True, check=True
    ).stdout
    hits = []
    for name in filter(None, listed.decode().split("\0")):
        path = REPO_ROOT / name
        if path.is_file() and pattern.search(path.read_bytes()):
            hits.append(name)
    assert hits == []
