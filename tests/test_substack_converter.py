"""The Substack converter, in both of its languages.

Every Substack draft made from ``blog/*.md`` goes through ``md2substack.py``
or its in-page copy ``md2substack.js``, both under
``.claude/skills/sync-substack``. A session creating a draft converts the post
in the page and refuses to write unless the result hashes to the local
conversion, so the two copies disagreeing stops every write. A converter that
crashes on a committed post stops that post's write the same way.

Three layers check it.

1. Two fixture posts convert to committed trees, so any change in behaviour
   fails here with a diff. One uses every Markdown shape the converter reads.
   The other puts each block shape straight under a paragraph line, with no
   blank line between, and holds an ordered list long enough to need
   two-digit numbers.
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

import hashlib
import importlib.util
import json
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "sync-substack"
CONVERTER_JS = SKILL_DIR / "md2substack.js"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "substack"
FIXTURE = FIXTURE_DIR / "every-construct.md"
EXPECTED = FIXTURE_DIR / "every-construct.json"
EDGE = FIXTURE_DIR / "edge-cases.md"
EDGE_EXPECTED = FIXTURE_DIR / "edge-cases.json"
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
    cases = [
        (FIXTURE.name, FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES),
        (EDGE.name, EDGE.read_text(encoding="utf-8"), FIXTURE_IMAGES),
    ]
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


def test_the_edge_cases_convert_to_the_committed_tree() -> None:
    """A paragraph line stops where a block shape starts, blank line or not.

    Each paragraph in the edge-case fixture is one line with an image, a
    numbered item, a bullet, a heading of each level or a fence straight under
    it. A paragraph that read on would swallow the block as text. The sequence
    of blocks is spelled out here as well as pinned whole, since regenerating
    the committed tree from a broken converter would pin the swallowed
    version. ``edge-cases.json`` is regenerated the same way as
    ``every-construct.json``.
    """
    draft = m2s.convert(EDGE.read_text(encoding="utf-8"), FIXTURE_IMAGES)
    assert draft == json.loads(EDGE_EXPECTED.read_text(encoding="utf-8"))
    blocks = draft["body"]["content"]
    assert [n["type"] for n in blocks] == [
        "paragraph",
        "captionedImage",
        "paragraph",
        "paragraph",
        "ordered_list",
        "paragraph",
        "bullet_list",
        "paragraph",
        "heading",
        "paragraph",
        "heading",
        "paragraph",
        "highlighted_code_block",
        "ordered_list",
        "paragraph",
        "subscribeWidget",
    ]
    # A line that opens in italics is a caption only when all of it is italic.
    assert len(blocks[1]["content"]) == 1
    assert blocks[2]["content"][0] == {
        "type": "text",
        "text": "Italic opening",
        "marks": [{"type": "em"}],
    }
    # Items 10 and 11 stay in the list, so the item pattern takes any number.
    assert len(blocks[13]["content"]) == 11
    # The last paragraph is the comment that turns off markdownlint's
    # blank-line rules for this file, which the fixture breaks on purpose.
    assert blocks[14]["content"][0]["text"].startswith("<!-- markdownlint-disable-file")


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


def _unterminated(info: str) -> str:
    """A post whose last fence, on line 7, never closes."""
    return f"# Title\n\n*Subtitle*\n\nText.\n\n```{info}\nx = 1\n"


@pytest.mark.parametrize("info", ["math", "python"])
def test_an_unterminated_fence_raises(info: str) -> None:
    """A fence with no closing line stops the conversion with a clear error.

    Before this was checked, the Python raised an ``IndexError`` naming no line
    and the in-page copy looped forever, freezing the tab it ran in.
    """
    with pytest.raises(ValueError, match=f"unterminated fence opened on line 7: ```{info}"):
        m2s.convert(_unterminated(info), {})


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


# Posts whose Markdown uses a shape the converter does not handle: a pipe
# table, a heading of four to six hashes, or a linked image. Both had drafts
# made by another route before the converter existed, and SKILL.md says they
# cannot be synced through it. A third post using one of these shapes fails
# below, because its draft would show the Markdown as literal text.
UNSUPPORTED_SHAPES = frozenset(
    {
        "gld-gdx-cointegration-lessons.md",
        "price-spread-mean-reversion.md",
    }
)


def _paragraph_texts(node: dict):
    """The plain text of every paragraph, in order."""
    if node.get("type") == "paragraph":
        yield "".join(t["text"] for t, _ in _text_nodes(node))
    for child in node.get("content") or []:
        yield from _paragraph_texts(child)


def test_only_the_named_posts_use_shapes_the_converter_does_not_handle() -> None:
    """No converted paragraph opens with what an unhandled shape leaves behind.

    A table row opens ``|`` and a deep heading opens ``#``. A linked image
    ``[![alt](x.png)](x.png)`` becomes a link whose text opens ``![``, which no
    handled paragraph can, since a line opening ``![`` is read as an image.
    The set must match exactly, so a post that stops using these shapes
    leaves the list too.
    """
    found = set()
    for post in POSTS:
        draft = m2s.convert(post.read_text(encoding="utf-8"), images_for(post))
        if any(t.startswith(("|", "#", "![")) for t in _paragraph_texts(draft["body"])):
            found.add(post.name)
    assert found == UNSUPPORTED_SHAPES


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
    } catch (e) { out.error = String(e) + (e && e.stack ? "\\n" + e.stack : ""); }
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


def _run_javascript(cases: list[tuple[str, str, dict]], directory: Path) -> dict[str, dict]:
    """Each case's result from the JavaScript copy, keyed by name.

    The engine runs under a timeout, so a copy that loops forever fails the
    test that called it rather than hanging the suite.
    """
    engine = _engine()
    script = (
        CONVERTER_JS.read_text(encoding="utf-8")
        + f"\nvar __CASES = {json.dumps(cases, ensure_ascii=False)};\n"
        + DRIVER
    )
    runner = directory / "run.js"
    runner.write_text(script, encoding="utf-8")
    try:
        done = subprocess.run(
            [*engine, str(runner)], capture_output=True, text=True, timeout=120, check=False
        )
    except subprocess.TimeoutExpired:
        pytest.fail("md2substack.js did not finish within 120 seconds")
    output = done.stdout + done.stderr
    assert done.returncode == 0, output[-2000:]
    results = {}
    for line in output.splitlines():
        if line.startswith("SUBSTACK_RESULT "):
            result = json.loads(line[len("SUBSTACK_RESULT ") :])
            results[result["name"]] = result
    return results


@pytest.fixture(scope="module")
def javascript_results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    """The JavaScript copy's output for every case, from one engine run."""
    cases = _cases()
    results = _run_javascript(cases, tmp_path_factory.mktemp("substack"))
    assert set(results) == {name for name, _, _ in cases}
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
    summary = m2s.summary(draft, FIXTURE.read_bytes())
    blocks = draft["body"]["content"]
    assert summary["blocks"] == len(blocks)
    assert summary["widgets_at"] == [13, len(blocks) - 1]
    assert summary["walk_lines"] == len(m2s.walk_lines(draft["body"]))
    assert summary["subtitle_length"] == len(draft["subtitle"])


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_summary_hashes_are_what_the_page_recomputes() -> None:
    """Each hash is recomputed here the way the page computes it.

    The page hashes the Markdown file as fetched, so ``md_sha256`` is pinned
    against the file's bytes rather than text Python read back.
    """
    md_bytes = FIXTURE.read_bytes()
    draft = m2s.convert(md_bytes.decode("utf-8"), FIXTURE_IMAGES)
    summary = m2s.summary(draft, md_bytes)
    assert summary["md_sha256"] == hashlib.sha256(md_bytes).hexdigest()
    assert summary["conversion_sha256"] == _sha256(m2s.canonical(draft))
    assert summary["body_sha256"] == _sha256(m2s.canonical(draft["body"]))
    assert summary["walk_sha256"] == _sha256("\n".join(m2s.walk_lines(draft["body"])))


def test_summary_hashes_the_file_bytes_not_the_text_read_back() -> None:
    """A file with Windows line endings reads back as different text.

    The page fetches the bytes and hashes them, so ``md_sha256`` must too, or
    the driver's Markdown check would refuse a file it should accept.
    """
    md_bytes = b"# Title\r\n\r\n*Subtitle*\r\n\r\nText.\r\n"
    draft = m2s.convert("# Title\n\n*Subtitle*\n\nText.\n", {})
    assert m2s.summary(draft, md_bytes)["md_sha256"] == hashlib.sha256(md_bytes).hexdigest()


def test_the_command_line(tmp_path: Path) -> None:
    """The command prints the draft, or with ``--summary`` its summary.

    Both runs pass the image map as a file, so a command that dropped it would
    fail on the fixture's figures.
    """
    images = tmp_path / "images.json"
    images.write_text(json.dumps(FIXTURE_IMAGES), encoding="utf-8")
    draft = m2s.convert(FIXTURE.read_text(encoding="utf-8"), FIXTURE_IMAGES)
    run = [sys.executable, str(SKILL_DIR / "md2substack.py"), str(FIXTURE), str(images)]
    full = subprocess.run(run, capture_output=True, text=True, check=True, timeout=60)
    assert json.loads(full.stdout) == draft
    run.insert(2, "--summary")
    brief = subprocess.run(run, capture_output=True, text=True, check=True, timeout=60)
    assert json.loads(brief.stdout) == m2s.summary(draft, FIXTURE.read_bytes())


def test_the_javascript_raises_on_an_unterminated_fence(tmp_path: Path) -> None:
    """The in-page copy raises the Python's error rather than looping forever.

    Before this was checked it looped forever. ``_run_javascript`` runs the
    engine under a timeout, so a copy that loops again fails here.
    """
    cases = [(info, _unterminated(info), {}) for info in ("math", "python")]
    results = _run_javascript(cases, tmp_path)
    for info in ("math", "python"):
        error = results[info]["error"] or ""
        assert f"unterminated fence opened on line 7: ```{info}" in error
