"""The Substack converter, in both of its languages.

Every Substack draft made from ``blog/*.md`` goes through ``md2substack.py``
or its in-page copy ``md2substack.js``, both under
``.claude/skills/sync-substack``. A session creating a draft converts the post
in the page and refuses to write unless the result hashes to the local
conversion, so the two copies disagreeing stops every write. A converter that
crashes on a committed post stops that post's write the same way.

Three layers check it.

1. A fixture post using every Markdown shape the converter reads converts to a
   committed tree, so any change in behaviour fails here with a diff.
2. Every committed post converts, and the result keeps the facts that hold
   whatever the post says: its title, its subtitle, where the widgets go, and
   one block per equation, code fence and figure.
3. The JavaScript copy produces the same canonical JSON and the same text-run
   lines as the Python on the fixture and on every committed post.

The JavaScript runs under ``node`` where it is installed, which it is on
GitHub's runners, and under ``osascript -l JavaScript`` otherwise, which is
JavaScriptCore and ships with macOS. With neither, the third layer skips
rather than passes. ``tests/test_build_board.py`` picks its engine the same
way.
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import struct
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "sync-substack"
CONVERTER_JS = SKILL_DIR / "md2substack.js"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "substack"
FIXTURE = FIXTURE_DIR / "every-construct.md"
EXPECTED = FIXTURE_DIR / "every-construct.json"
POSTS = sorted((REPO_ROOT / "blog").glob("*.md"))

# The fixture's figures were never uploaded, so their Substack fields are made up.
FIXTURE_IMAGES = {
    "first_figure.png": {
        "url": "https://example.invalid/first_figure.png",
        "width": 1300,
        "height": 900,
        "bytes": 123456,
    },
    "second_figure.png": {
        "url": "https://example.invalid/second_figure.png",
        "width": 640,
        "height": 480,
        "bytes": 2048,
    },
}

IMAGE_LINE = re.compile(r"^!\[(.*)\]\(([^)]+)\)$")


def _load_converter():
    spec = importlib.util.spec_from_file_location("md2substack", SKILL_DIR / "md2substack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m2s = _load_converter()


def _png_size(path: Path) -> tuple[int, int]:
    """Width and height from a PNG's header chunk."""
    with path.open("rb") as f:
        head = f.read(24)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", f"{path} is not a PNG"
    return struct.unpack(">II", head[16:24])


def images_for(post: Path) -> dict:
    """The image map an upload would produce, with a made-up URL.

    Width, height and size come from the committed figure, so the map has the
    shape a real one has.
    """
    images = {}
    for line in post.read_text(encoding="utf-8").split("\n"):
        found = IMAGE_LINE.match(line)
        if found:
            figure = (post.parent / found.group(2)).resolve()
            width, height = _png_size(figure)
            images[figure.name] = {
                "url": f"https://example.invalid/{figure.name}",
                "width": width,
                "height": height,
                "bytes": figure.stat().st_size,
            }
    return images


def _cases() -> list[tuple[str, str, dict]]:
    """The fixture and every committed post, each with its image map."""
    cases = [(FIXTURE.name, FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES)]
    for post in POSTS:
        cases.append((post.name, post.read_text(encoding="utf-8"), images_for(post)))
    return cases


def _outside_fences(lines: list[str]) -> list[tuple[str, str | None]]:
    """Each line paired with the info string of the fence it opens, if any.

    Lines inside a fence are dropped, so a ``## `` inside a code block is not
    read as a heading.
    """
    out, fence = [], False
    for line in lines:
        if fence:
            if line == "```":
                fence = False
            continue
        if line.startswith("```"):
            fence = True
            out.append((line, line[3:]))
        else:
            out.append((line, None))
    return out


def _text_nodes(node: dict, inside_code: bool = False):
    """Every text node, and whether it sits inside a code block."""
    inside_code = inside_code or node.get("type") == "highlighted_code_block"
    if node.get("type") == "text":
        yield node, inside_code
    for child in node.get("content") or []:
        yield from _text_nodes(child, inside_code)


# --- The fixture's pinned tree --------------------------------------------------


def test_the_fixture_converts_to_the_committed_tree() -> None:
    """Any change in what the converter produces fails here.

    A draft created before the change and synced after it would differ in
    every block the change touched, so a change has to be deliberate. When it
    is, regenerate ``every-construct.json`` from the new converter and read the
    diff before committing it.
    """
    draft = m2s.convert(FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    assert draft == expected


def test_the_fixture_still_reaches_every_shape() -> None:
    """The pin above covers only the shapes the fixture uses.

    An edit that drops a shape from the fixture and regenerates the tree would
    leave that pin green, so this names each shape and checks it is there.
    """
    body = json.loads(EXPECTED.read_text(encoding="utf-8"))["body"]
    blocks = body["content"]
    kinds = [n["type"] for n in blocks]
    headings = {n["attrs"]["level"] for n in blocks if n["type"] == "heading"}
    code_blocks = [n for n in blocks if n["type"] == "highlighted_code_block"]
    figures = [n for n in blocks if n["type"] == "captionedImage"]
    nested = {
        child["type"]
        for n in blocks
        if n["type"] == "ordered_list"
        for item in n["content"]
        for child in item["content"][1:]
    }
    marks = {m["type"] for t, _ in _text_nodes(body) for m in t.get("marks", [])}
    nested_marks = {len(t.get("marks", [])) for t, _ in _text_nodes(body)}
    text = " ".join(t["text"] for t, _ in _text_nodes(body))

    assert headings == {1, 2}
    assert kinds.count("latex_block") == 2
    assert {"content" in n for n in code_blocks} == {True, False}
    assert {len(n["content"]) for n in figures} == {1, 2}
    assert nested == {"ordered_list", "bullet_list"}
    assert "bullet_list" in kinds
    assert marks == {"strong", "em", "code", "link"}
    assert 2 in nested_marks
    assert "~30" in text and "$2.09" in text
    assert kinds.count("subscribeWidget") == 2


def test_the_subtitle_keeps_its_escapes_as_typed() -> None:
    """The subtitle is copied from the Markdown, escapes and all.

    A ``\\$`` in the italic line reaches Substack as a backslash and a dollar
    sign, unlike the same escape in the body. No committed post with a subtitle
    short enough to send has one yet, which is why nothing changed it, and the
    skill says to check the subtitle before sending it. This pins the
    behaviour so a fix is a deliberate change rather than a surprise.
    """
    draft = m2s.convert(FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES)
    assert "\\$5" in draft["subtitle"]


# --- Every committed post -------------------------------------------------------


@pytest.mark.parametrize("post", POSTS, ids=lambda p: p.name)
def test_a_committed_post_converts_and_keeps_its_structure(post: Path) -> None:
    """Facts that hold whatever the post says, so a prose edit never fails here.

    The subtitle's length is not checked. Substack refuses one over 255
    characters, several committed posts are longer by the owner's choice, and
    those drafts were created with no subtitle. The skill says to measure it
    before creating a draft.
    """
    md = post.read_text(encoding="utf-8")
    lines = md.split("\n")
    draft = m2s.convert(md, images_for(post))
    blocks = draft["body"]["content"]

    assert draft["title"] == lines[0].removeprefix("# ").strip()
    assert draft["subtitle"] == lines[2].strip().strip("*")

    outside = _outside_fences(lines[3:])
    fences = [info for _, info in outside if info is not None]
    level_one = [
        i for i, n in enumerate(blocks) if n["type"] == "heading" and n["attrs"]["level"] == 1
    ]
    widgets = [i for i, n in enumerate(blocks) if n["type"] == "subscribeWidget"]
    assert len(level_one) == sum(line.startswith("## ") for line, _ in outside)
    assert widgets[-1] == len(blocks) - 1
    if len(level_one) >= 2:
        assert widgets == [level_one[1] - 1, len(blocks) - 1]
    else:
        assert widgets == [len(blocks) - 1]

    equations = [n for n in blocks if n["type"] == "latex_block"]
    assert len(equations) == sum(info.startswith("math") for info in fences)
    assert [n["attrs"]["id"] for n in equations] == [
        f"EQSTAT{k:02d}" for k in range(1, len(equations) + 1)
    ]
    code_blocks = [n for n in blocks if n["type"] == "highlighted_code_block"]
    assert len(code_blocks) == sum(not info.startswith("math") for info in fences)

    alts = [IMAGE_LINE.match(line).group(1) for line, _ in outside if IMAGE_LINE.match(line)]
    figures = [n["content"][0]["attrs"]["alt"] for n in blocks if n["type"] == "captionedImage"]
    assert figures == alts

    for node, inside_code in _text_nodes(draft["body"]):
        assert node["text"], "an empty text node, which Substack refuses"
        if not inside_code:
            assert "\\~" not in node["text"] and "\\$" not in node["text"], node["text"]


# --- Python and JavaScript agree ------------------------------------------------

# Appended after md2substack.js. It converts every case and prints one line per
# case. The output goes through `console.log` in node and osascript, and through
# `print` in a bare JavaScriptCore shell, which has no console. osascript's
# console.log reads its argument as a format string and prints `%%` as `%`, so
# every percent sign is written as the JSON escape `%`, which parses back
# to the same character.
DRIVER = """
(function () {
  var emit = function (line) {
    if (typeof console !== "undefined" && console.log) { console.log(line); } else { print(line); }
  };
  __CASES.forEach(function (c) {
    var out = { name: c[0], error: null };
    try {
      var draft = M2S.convert(c[1], c[2]);
      out.canon = M2S.canon(draft);
      out.walk = M2S.walkLines(draft.body);
    } catch (e) { out.error = String(e && e.stack || e); }
    emit("SUBSTACK_RESULT " + JSON.stringify(out).replace(/%/g, "\\\\u0025"));
  });
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


@pytest.fixture(scope="module")
def javascript_results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """The JavaScript copy's output for every case, from one engine run."""
    engine = _engine()
    cases = _cases()
    script = (
        CONVERTER_JS.read_text(encoding="utf-8")
        + f"\nvar __CASES = {json.dumps(cases, ensure_ascii=False)};\n"
        + DRIVER
    )
    runner = tmp_path_factory.mktemp("substack") / "run.js"
    runner.write_text(script, encoding="utf-8")
    done = subprocess.run(
        [*engine, str(runner)], capture_output=True, text=True, timeout=120, check=False
    )
    output = done.stdout + done.stderr
    assert done.returncode == 0, output[-2000:]
    results = {}
    for line in output.splitlines():
        if line.startswith("SUBSTACK_RESULT "):
            result = json.loads(line[len("SUBSTACK_RESULT ") :])
            results[result["name"]] = result
    assert set(results) == {name for name, _, _ in cases}, output[-2000:]
    return results


@pytest.mark.parametrize("case", _cases(), ids=lambda c: c[0] if isinstance(c, tuple) else str(c))
def test_python_and_javascript_produce_the_same_draft(
    case: tuple[str, str, dict], javascript_results: dict[str, dict]
) -> None:
    """The in-page copy agrees with the local one, byte for byte.

    Canonical JSON compares the whole tree. The text-run lines are what a sync
    hashes on the live draft, so their two implementations are compared too.
    """
    name, md, images = case
    result = javascript_results[name]
    assert result["error"] is None, result["error"]
    draft = m2s.convert(md, images)
    assert result["canon"] == m2s.canonical(draft)
    assert result["walk"] == m2s.walk_lines(draft["body"])


def test_the_canonical_form_ignores_key_order() -> None:
    """Substack returns a draft's keys in its own order, and the check must not care."""
    assert m2s.canonical({"b": [1, {"d": "é", "c": None}], "a": True}) == (
        '{"a":true,"b":[1,{"c":null,"d":"é"}]}'
    )


def test_the_summary_names_where_the_widgets_sit() -> None:
    draft = m2s.convert(FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES)
    summary = m2s.summary(draft)
    blocks = draft["body"]["content"]
    assert summary["blocks"] == len(blocks)
    assert summary["widgets_at"] == [13, len(blocks) - 1]
    assert summary["walk_lines"] == len(m2s.walk_lines(draft["body"]))
    assert summary["subtitle_length"] == len(draft["subtitle"])
