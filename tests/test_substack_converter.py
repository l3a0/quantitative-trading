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
   two-digit numbers. Five more fixtures cover pipe tables, deep headings,
   linked images, subtitle escapes and inputs at the edges of those shapes,
   and their tests spell out the expected output rather than pinning a
   regenerated tree.
2. Every committed post converts, and the result keeps the facts that hold
   whatever the post says: its title, its subtitle, where the widgets go, and
   one block per equation, table, code fence, heading and figure.
3. The JavaScript copy produces the same canonical JSON and the same text-run
   lines as the Python on the fixtures, on every committed post, and on
   strings built where Python's and JavaScript's regular expressions and
   string methods disagree.

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
TABLES = FIXTURE_DIR / "tables.md"
DEEP_HEADINGS = FIXTURE_DIR / "deep-headings.md"
LINKED_IMAGES = FIXTURE_DIR / "linked-images.md"
SUBTITLE_ESCAPES = FIXTURE_DIR / "subtitle-escapes.md"
SHAPE_EDGES = FIXTURE_DIR / "shape-edges.md"
SHAPE_FIXTURES = [TABLES, DEEP_HEADINGS, LINKED_IMAGES, SUBTITLE_ESCAPES, SHAPE_EDGES]
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
LINKED_IMAGE_LINE = re.compile(r"^\[!\[(.*)\]\(([^)]+)\)\]\(([^)]+)\)$")
# The committed posts write every delimiter row with a pipe at each end.
DELIMITER_ROW = re.compile(r"\|( *:?-+:? *\|)+ *")
ASCII_WHITESPACE = " \t\n\r\f\v"


def _figure_line(line: str) -> re.Match | None:
    """The match for an image line or a linked image line, whose groups 1 and 2 are alt and path."""
    return IMAGE_LINE.match(line) or LINKED_IMAGE_LINE.match(line)


def _load_converter():
    spec = importlib.util.spec_from_file_location("md2substack", SKILL_DIR / "md2substack.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m2s = _load_converter()
WIDGET_CONTENT = m2s.WIDGET["content"]


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
        found = _figure_line(line)
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
    """The fixtures and every committed post, each with its image map."""
    cases = [
        (fixture.name, fixture.read_text(encoding="utf-8"), FIXTURE_IMAGES)
        for fixture in [FIXTURE, EDGE, *SHAPE_FIXTURES]
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

    assert headings == {1, 2, 3}
    assert kinds.count("latex_block") == 3
    latex = [n["attrs"]["persistentExpression"] for n in blocks if n["type"] == "latex_block"]
    assert sum(e.startswith("\\begin{array}") for e in latex) == 1
    assert {"content" in n for n in code_blocks} == {True, False}
    assert {len(n["content"]) for n in figures} == {1, 2}
    assert {n["content"][0]["attrs"]["href"] is None for n in figures} == {True, False}
    assert nested == {"ordered_list", "bullet_list"}
    assert "bullet_list" in kinds
    assert marks == {"strong", "em", "code", "link"}
    assert 2 in nested_marks
    assert "~30" in text and "$2.09" in text
    assert kinds.count("subscribeWidget") == 2


def _convert_fixture(path: Path) -> dict:
    return m2s.convert(path.read_text(encoding="utf-8"), FIXTURE_IMAGES)


def test_the_subtitle_loses_its_escapes_as_the_body_does() -> None:
    """A ``\\$`` or ``\\~`` in the italic line reaches Substack without its backslash.

    Before, the subtitle was copied as typed, so a ``\\$`` there showed its
    backslash on Substack while the same escape in the body did not.
    """
    draft = _convert_fixture(SUBTITLE_ESCAPES)
    assert draft["subtitle"] == (
        "A trade costs $5 and lasts ~30 days, and the subtitle loses both backslashes."
    )
    [paragraph, _] = draft["body"]["content"]
    assert paragraph["content"] == [
        {"type": "text", "text": "The body loses them too: a trade costs $5 and lasts ~30 days."}
    ]
    assert _convert_fixture(FIXTURE)["subtitle"].startswith("The subtitle line costs $5 ")


# The tables fixture's three tables, as the arrays Substack receives. Every
# alignment, every special character, a code span, a link, an image, a linked
# image, emphasis, an escaped pipe, unmatched backticks, a short row and a long
# row are in the first.
FIRST_TABLE = "\n".join(
    [
        r"\begin{array}{l|l|r|c}",
        r"\text{Left} & \text{Plain} & \text{Right} & \text{Centre} \\ \hline",
        r"\text{a|b *c*} & \text{a link} & \text{bold and em} & \text{alt text} \\",
        r"\$\text{ }\%\text{ }\&\text{ }\#\text{ }\_\text{ }\{\text{ }\}\text{ }\backslash"
        r"\text{ }{\sim}\text{ }{\hat{\ }} & \$\text{ }{\sim}\text{ * }\backslash"
        r" & \text{a`b} & \text{x} \\",
        r"\text{short row} &  &  &  \\",
        r"\text{one} & \text{two} & \text{three} & \text{four} \\",
        r" & \text{inner} & \text{`open} & \text{2 * 3}",
        r"\end{array}",
    ]
)
HEADER_ONLY_TABLE = "\\begin{array}{l}\n\\text{Header only} \\\\ \\hline\n\\end{array}"
LAST_TABLE = "\n".join(
    [
        r"\begin{array}{l}",
        r"\text{Runs to a blank line} \\ \hline",
        r"\text{a row that opens a pipe} \\",
        r"\text{a line with no pipe is a row too}",
        r"\end{array}",
    ]
)


def test_a_pipe_table_becomes_a_latex_array() -> None:
    """Each table is one LaTeX block, numbered in sequence with the math fences.

    A ``|`` line with no delimiter row under it, or with one whose cell count
    differs, stays paragraph text. A table interrupts a paragraph. As on
    GitHub, it runs until a blank line or a line opening another block, and
    a line not opening ``|`` is a row like any other.
    """
    blocks = _convert_fixture(TABLES)["body"]["content"]
    assert [n["type"] for n in blocks] == [
        "paragraph",
        "latex_block",
        "latex_block",
        "paragraph",
        "latex_block",
        "paragraph",
        "paragraph",
        "latex_block",
        "bullet_list",
        "paragraph",
        "subscribeWidget",
    ]
    tables = [n["attrs"] for n in blocks if n["type"] == "latex_block"][1:]
    assert tables == [
        {"persistentExpression": FIRST_TABLE, "id": "EQSTAT02"},
        {"persistentExpression": HEADER_ONLY_TABLE, "id": "EQSTAT03"},
        {"persistentExpression": LAST_TABLE, "id": "EQSTAT04"},
    ]
    texts = [n["content"][0]["text"] for n in blocks if n["type"] == "paragraph"]
    assert texts[1:4] == [
        "A paragraph line",
        "| Not a table, since no delimiter row follows | | a paragraph line that opens a pipe |",
        "| One | Two | | --- | | The delimiter row above has one cell for two headers, "
        "so this is a paragraph |",
    ]
    assert blocks[8]["content"][0]["content"][0]["content"][0]["text"] == (
        "and a bullet ends the table"
    )


# Each cell and the LaTeX it becomes. The examples follow the rule in
# ``md2substack.py``'s docstring, and each also runs as one row of a table
# through both converters, in ``SHAPE_EDGE_STRINGS`` below.
CELL_RULE = [
    (">90% conf.", r"\text{>90}\%\text{ conf.}"),
    (r"\~10 days → \~10 days", r"{\sim}\text{10 days → }{\sim}\text{10 days}"),
    ("", ""),
    ("`a\\b` and \\\\", r"\text{a}\backslash\text{b and }\backslash"),
    ("**[a *b*](u)** ![c](d)", r"\text{a b c}"),
    ("x^2 ^^", r"\text{x}{\hat{\ }}\text{2 }{\hat{\ }}{\hat{\ }}"),
    ("a   b\t\tc `d  \t e`", r"\text{a b c d e}"),
    (r"x \\", r"\text{x }\backslash"),
    (r"\`x`", r"\text{`x`}"),
    (r"a \| b", r"\text{a | b}"),
    (r"\[x](y)", r"\text{[x](y)}"),
    ("`x`` y`", r"\text{x`` y}"),
    ("`  `", r"\text{ }"),
    ("`  x  `", r"\text{ x }"),
    ("` x`", r"\text{ x}"),
    ("*a* b*", r"\text{a b*}"),
    (
        "_em_ __strong__ ~~s~~ <br> &amp; $m$",
        r"\_\text{em}\_\text{ }\_\_\text{strong}\_\_"
        r"\text{ }{\sim}{\sim}\text{s}{\sim}{\sim}\text{ <br> }\&\text{amp; }\$\text{m}\$",
    ),
    (f"*a{chr(0x2028)}b* **c{chr(0x2028)}d**", f"\\text{{a{chr(0x2028)}b c{chr(0x2028)}d}}"),
]


@pytest.mark.parametrize(("cell", "latex"), CELL_RULE)
def test_a_cell_follows_the_stated_rule(cell: str, latex: str) -> None:
    """The examples from the rule in ``md2substack.py``'s docstring.

    A caret is drawn over a space, since ``{\\hat{}}`` has no width. Spaces
    and tabs collapse to one space, code spans included. Markdown the body
    does not read, such as underscores, strikethrough, HTML and dollar math,
    shows as typed. Emphasis may span a line separator, which JavaScript's
    ``.`` would not match.
    """
    assert m2s.cell_latex(m2s.cell_text(cell)) == latex


def test_headings_of_four_to_six_hashes_move_up_one_level() -> None:
    """``####`` to ``######`` become levels 3 to 5, and only ``## `` places a widget."""
    blocks = _convert_fixture(DEEP_HEADINGS)["body"]["content"]
    shape = [(n["type"], (n.get("attrs") or {}).get("level")) for n in blocks]
    assert shape == [
        ("heading", 1),
        ("heading", 2),
        ("heading", 3),
        ("heading", 4),
        ("heading", 5),
        ("paragraph", None),
        ("paragraph", None),
        ("paragraph", None),
        ("heading", 3),
        ("subscribeWidget", None),
        ("heading", 1),
        ("paragraph", None),
        ("paragraph", None),
        ("subscribeWidget", None),
    ]
    assert blocks[2]["content"] == [
        {"type": "text", "text": "Level four with "},
        {"type": "text", "text": "emphasis", "marks": [{"type": "em"}]},
    ]
    assert [blocks[k]["content"][0]["text"] for k in (4, 5, 6, 7, 8)] == [
        "Level six",
        "####### Seven hashes make a paragraph line",
        "####No space makes a paragraph line too",
        "A paragraph line",
        "A level-four heading straight after text",
    ]


def test_a_linked_image_becomes_a_figure() -> None:
    """The image keeps its caption, and links out only to a web address.

    A relative target, such as the committed PNG a post links to, would point
    nowhere on Substack, so ``href`` stays null for it. A line holding more
    than the linked image stays a paragraph, as before.
    """
    blocks = _convert_fixture(LINKED_IMAGES)["body"]["content"]
    assert [n["type"] for n in blocks] == [
        "captionedImage",
        "captionedImage",
        "paragraph",
        "captionedImage",
        "paragraph",
        "subscribeWidget",
    ]
    attrs = [blocks[k]["content"][0]["attrs"] for k in (0, 1, 3)]
    assert [(a["src"], a["alt"], a["href"]) for a in attrs] == [
        (
            "https://example.invalid/first_figure.png",
            "A figure linked to a web page",
            "https://example.com/full-size",
        ),
        ("https://example.invalid/second_figure.png", "A figure linked to its own file", None),
        (
            "https://example.invalid/first_figure.png",
            "A linked figure straight after text",
            "http://example.com/plain",
        ),
    ]
    assert blocks[0]["content"][1] == {
        "type": "caption",
        "content": [{"type": "text", "text": "Figure 1: the caption is the next italic line."}],
    }
    assert [len(blocks[k]["content"]) for k in (1, 3)] == [1, 1]
    assert blocks[2]["content"] == [{"type": "text", "text": "A paragraph line"}]
    assert blocks[4]["content"][-1]["text"].endswith("with text after it stays a paragraph.")


def test_lines_at_the_edges_of_a_shape_read_as_github_reads_them() -> None:
    """Each input in the shape-edges fixture sits just inside or outside a shape.

    A table needs a header opening ``|``, a real delimiter row and a matching
    cell count. A delimiter row of bare hyphens underlines a heading on
    GitHub, so it starts no table, while one holding a colon does. Seven
    hashes, hashes with no space, an image or linked image with text after
    it, and non-ASCII digits all stay inside the paragraph above them. A
    linked image takes its picture from the image path and links out only to
    a target starting ``http://`` or ``https://``. A linked image on the
    last line has nothing after it to read as a caption.
    """
    blocks = _convert_fixture(SHAPE_EDGES)["body"]["content"]
    kinds = [n["type"] for n in blocks]
    assert kinds == [
        "paragraph",
        "paragraph",
        "paragraph",
        "latex_block",
        "paragraph",
        "latex_block",
        "latex_block",
        "paragraph",
        "paragraph",
        "paragraph",
        "paragraph",
        "paragraph",
        "captionedImage",
        "captionedImage",
        "captionedImage",
        "latex_block",
        "captionedImage",
        "subscribeWidget",
    ]
    texts = {k: "".join(t["text"] for t in blocks[k]["content"]) for k in (1, 2, 4, 7, 8, 10)}
    assert texts == {
        1: "Total | --- |",
        2: "| a | | a-b |",
        4: "| a | --- | x |",
        7: "para ####### x",
        8: "para ####x",
        10: "para ١٢. x",
    }
    assert blocks[9]["content"][0]["text"] == "para "
    assert blocks[9]["content"][-1]["text"] == "](https://e) more"
    assert blocks[11]["content"][-1]["text"] == " and more"
    # A delimiter row that opens like a bullet, "- | -", is still a delimiter row.
    assert blocks[6]["attrs"]["persistentExpression"] == "\n".join(
        [
            r"\begin{array}{l|l}",
            r"\text{a} & \text{b} \\ \hline",
            r"\text{1} & \text{2}",
            r"\end{array}",
        ]
    )
    latex = [blocks[k]["attrs"]["persistentExpression"] for k in (3, 5, 15)]
    assert latex == [
        "\n".join(
            [
                r"\begin{array}{l|l}",
                r"\text{x} & \text{y} \\ \hline",
                r"\text{x} & \text{y|} \\",
                r" & \text{y }\backslash",
                r"\end{array}",
            ]
        ),
        "\\begin{array}{l}\n\\text{1.5 =} \\\\ \\hline\n\\end{array}",
        "\n".join(
            [
                r"\begin{array}{l|l|l|l}",
                r"\text{Code} & \text{Emphasis} & \text{Strong} & \text{Spaces} \\ \hline",
                r"\text{a|b|c} & \text{x y} & \text{x y} & \text{a b}",
                r"\end{array}",
            ]
        ),
    ]
    figures = [blocks[k]["content"] for k in (12, 13, 14, 16)]
    assert [(f[0]["attrs"]["src"], f[0]["attrs"]["href"], len(f)) for f in figures] == [
        ("https://example.invalid/first_figure.png", None, 1),
        ("https://example.invalid/first_figure.png", None, 1),
        ("https://example.invalid/second_figure.png", "https://e/first_figure.png", 1),
        ("https://example.invalid/first_figure.png", "https://e", 1),
    ]


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

    assert draft["title"] == lines[0].removeprefix("# ").strip(ASCII_WHITESPACE)
    subtitle = lines[2].strip(ASCII_WHITESPACE).strip("*")
    assert draft["subtitle"] == subtitle.replace("\\~", "~").replace("\\$", "$")

    outside = _outside_fences(lines[3:])
    fences = [info for _, info in outside if info is not None]
    levels = [n["attrs"]["level"] for n in blocks if n["type"] == "heading"]
    level_one = [
        i for i, n in enumerate(blocks) if n["type"] == "heading" and n["attrs"]["level"] == 1
    ]
    widgets = [i for i, n in enumerate(blocks) if n["type"] == "subscribeWidget"]
    for hashes in range(2, 7):
        written = sum(line.startswith("#" * hashes + " ") for line, _ in outside)
        assert levels.count(hashes - 1) == written, f"headings of {hashes} hashes"
    assert widgets[-1] == len(blocks) - 1
    if len(level_one) >= 2:
        assert widgets == [level_one[1] - 1, len(blocks) - 1]
    else:
        assert widgets == [len(blocks) - 1]

    equations = [n for n in blocks if n["type"] == "latex_block"]
    tables = sum(
        line.startswith("|") and DELIMITER_ROW.fullmatch(below) is not None
        for (line, _), (below, _) in zip(outside, outside[1:], strict=False)
    )
    assert len(equations) == sum(info.startswith("math") for info in fences) + tables
    assert [n["attrs"]["id"] for n in equations] == [
        f"EQSTAT{k:02d}" for k in range(1, len(equations) + 1)
    ]
    code_blocks = [n for n in blocks if n["type"] == "highlighted_code_block"]
    assert len(code_blocks) == sum(not info.startswith("math") for info in fences)

    alts = [_figure_line(line).group(1) for line, _ in outside if _figure_line(line)]
    figures = [n["content"][0]["attrs"]["alt"] for n in blocks if n["type"] == "captionedImage"]
    assert figures == alts

    for node, inside_code in _text_nodes(draft["body"]):
        assert node["text"], "an empty text node, which Substack refuses"
        if not inside_code:
            assert "\\~" not in node["text"] and "\\$" not in node["text"], node["text"]


def _paragraph_texts(node: dict):
    """The plain text of every paragraph, in order."""
    if node.get("type") == "paragraph":
        yield "".join(t["text"] for t, _ in _text_nodes(node))
    for child in node.get("content") or []:
        yield from _paragraph_texts(child)


def test_no_committed_post_leaves_markdown_as_literal_text() -> None:
    """No converted paragraph opens with what an unread shape would leave behind.

    A table row opens ``|`` and a deep heading opens ``#``. A linked image the
    converter missed becomes a link whose text opens ``![``. A paragraph can
    open ``![`` only when its first line holds an image and more text, which
    no committed post has. Two posts did this before the converter learned
    these shapes, and their drafts were made by another route.
    """
    found = set()
    for post in POSTS:
        draft = m2s.convert(post.read_text(encoding="utf-8"), images_for(post))
        if any(t.startswith(("|", "#", "![")) for t in _paragraph_texts(draft["body"])):
            found.add(post.name)
    assert found == set()


# --- Python and JavaScript agree ------------------------------------------------

# Appended after md2substack.js. It converts every case and prints one line per
# case. The output goes through `console.log` in node and osascript, and through
# `print` in a bare JavaScriptCore shell, which has no console. osascript's
# console.log reads its argument as a format string and prints `%%` as `%`, so
# every percent sign is written as the JSON escape `%`, which parses back
# to the same character. U+0085, U+2028 and U+2029 are written as escapes too,
# because JSON leaves them raw and Python's splitlines() breaks a line at each.
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
    var escape = function (c) {
      return "\\\\u" + ("000" + c.charCodeAt(0).toString(16)).slice(-4);
    };
    emit("SUBSTACK_RESULT " + JSON.stringify(out).replace(/[%\\u0085\\u2028\\u2029]/g, escape));
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


# Strings where Python's ``re`` and string methods read the same text
# differently from JavaScript's. No committed post holds any of them. Each but
# the last made the two converters disagree, or the JavaScript raise, before
# both stopped using the construct.
DIVERGENCES = {
    # Python's \d matches any Unicode digit, JavaScript's only 0 to 9.
    "non-ASCII digits": "# T\n\n*S*\n\n١٢. not an item\n\n- an item\n   ٣. not a nested item\n",
    # JavaScript's trim() strips U+FEFF and Python's strip() does not.
    "byte order marks": "\ufeff# Title\ufeff\n\n*Sub*\ufeff\n\n"
    "## \ufeffHeading\ufeff\n\n\ufeff\n\nText\ufeff\n",
    # Python's strip() strips U+001C to U+001F and U+0085, and trim() does not.
    "separators Python strips": "# T\n\n*S*\n\n\x1c\n\n## Heading\x1f\n\nText\x85\n",
    # JavaScript's . excludes \r, U+2028 and U+2029, and Python's excludes only \n.
    "line separators": "# T\n\n*S*\n\n**bold\u2028text** and *em\u2029text*\n\n"
    "![alt\u2028text](images/first_figure.png)\n\nEnd.\n",
    "carriage returns": "# T\r\n\r\n*S*\r\n\r\n## Head\r\n\r\nText **a\r\nb** c\r\n\r\n"
    "| a | b |\r\n| --- | --- |\r\n| 1 | 2 |\r\n",
    # json.dumps and JSON.stringify could escape control characters differently.
    # They agree today, and this case keeps them agreeing.
    "control characters": "# T\n\n*S*\n\nText \x01\x7f\x1f\u2028 \U0001f600 end.\n",
}


# Inputs at the edge of a shape that a fixture file cannot hold cleanly, since
# they need invisible characters, a trailing space or no closing newline. The
# characters are built with chr() so no editor can turn an escape into the
# character itself.
LINE_SEPARATOR, TAB, FORM_FEED, VERTICAL_TAB = chr(0x2028), chr(9), chr(12), chr(11)
SHAPE_EDGE_STRINGS = {
    "trimmed headings": f"# T\n\n*S*\n\n## H{TAB}\n\n{FORM_FEED}\n\n## K{VERTICAL_TAB}\n",
    "linked image alt with a line separator": "# T\n\n*S*\n\n"
    f"[![a{LINE_SEPARATOR}b](images/first_figure.png)](https://e)\n\nEnd.\n",
    "figure on the last line": "# T\n\n*S*\n\n![a](images/first_figure.png)\n",
    "linked figure on the last line": "# T\n\n*S*\n\n[![a](images/first_figure.png)](https://e)",
    "image with a trailing space": "# T\n\n*S*\n\n![a](images/first_figure.png) \n",
    "strong subtitle": "# T\n\n**S**\n\nBody.\n",
    "cell rule": "# T\n\n*S*\n\n| Cell |\n| --- |\n" + "".join(f"| {c} |\n" for c, _ in CELL_RULE),
}
STRING_CASES = {**DIVERGENCES, **SHAPE_EDGE_STRINGS}


@pytest.fixture(scope="module")
def divergence_results(tmp_path_factory: pytest.TempPathFactory) -> dict[str, dict]:
    cases = [(name, md, FIXTURE_IMAGES) for name, md in STRING_CASES.items()]
    return _run_javascript(cases, tmp_path_factory.mktemp("divergences"))


@pytest.mark.parametrize("name", sorted(STRING_CASES))
def test_python_and_javascript_agree_where_their_languages_differ(
    name: str, divergence_results: dict[str, dict]
) -> None:
    """Both converters read these strings the same way, one character set for both."""
    result = divergence_results[name]
    assert result["error"] is None, result["error"]
    draft = m2s.convert(STRING_CASES[name], FIXTURE_IMAGES)
    assert result["canon"] == m2s.canonical(draft)
    assert result["walk"] == m2s.walk_lines(draft["body"])


def test_the_shape_edge_strings_read_as_intended() -> None:
    """Headings lose a trailing tab or vertical tab, and a form-feed line is blank.

    A figure on the last line has no caption and does not raise. An image line
    with anything after the image, even one space, is paragraph text. A
    subtitle loses every asterisk at its ends, so ``**S**`` gives ``S``.
    """

    def convert(name: str) -> dict:
        return m2s.convert(SHAPE_EDGE_STRINGS[name], FIXTURE_IMAGES)

    headings = convert("trimmed headings")["body"]["content"]
    assert [(n["type"], n.get("content")) for n in headings] == [
        ("heading", [{"type": "text", "text": "H"}]),
        ("subscribeWidget", WIDGET_CONTENT),
        ("heading", [{"type": "text", "text": "K"}]),
        ("subscribeWidget", WIDGET_CONTENT),
    ]
    [figure, _, _] = convert("linked image alt with a line separator")["body"]["content"]
    assert figure["content"][0]["attrs"]["alt"] == f"a{LINE_SEPARATOR}b"
    for name in ("figure on the last line", "linked figure on the last line"):
        blocks = convert(name)["body"]["content"]
        assert [n["type"] for n in blocks] == ["captionedImage", "subscribeWidget"]
        assert len(blocks[0]["content"]) == 1
    trailing = convert("image with a trailing space")["body"]["content"]
    assert [n["type"] for n in trailing] == ["paragraph", "subscribeWidget"]
    assert convert("strong subtitle")["subtitle"] == "S"
    [table, _] = convert("cell rule")["body"]["content"]
    rows = table["attrs"]["persistentExpression"].split("\n")[2:-1]
    assert [row.removesuffix(" \\\\") for row in rows] == [latex for _, latex in CELL_RULE]


def test_the_divergent_strings_read_as_intended() -> None:
    """What the two converters agree on, spelled out for the decisive cases.

    Only ASCII digits number a list item, and only ASCII whitespace is trimmed
    or makes a line blank.
    """

    def kinds(name: str) -> list[str]:
        blocks = m2s.convert(DIVERGENCES[name], FIXTURE_IMAGES)["body"]["content"]
        return [n["type"] for n in blocks]

    assert kinds("non-ASCII digits") == ["paragraph", "bullet_list", "paragraph", "subscribeWidget"]
    marks = m2s.convert(DIVERGENCES["byte order marks"], {})
    assert marks["title"] == "\ufeff# Title\ufeff"
    assert [m2s.walk_lines(n)[0] for n in marks["body"]["content"][:3]] == [
        "/0tex||\ufeffHeading\ufeff",
        "/0tex||\ufeff",
        "/0tex||Text\ufeff",
    ]
    assert kinds("separators Python strips") == [
        "paragraph",
        "heading",
        "paragraph",
        "subscribeWidget",
    ]
    assert kinds("line separators")[:2] == ["paragraph", "captionedImage"]
    returns = m2s.convert(DIVERGENCES["carriage returns"], {})["body"]["content"]
    assert [n["type"] for n in returns] == [
        "heading",
        "paragraph",
        "latex_block",
        "subscribeWidget",
    ]
    strong = {"type": "text", "text": "a\r b", "marks": [{"type": "strong"}]}
    assert returns[1]["content"][1] == strong


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
    assert summary["widgets_at"] == [16, len(blocks) - 1]
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

    The page hashes the text fetch returned, encoded back to UTF-8. That keeps
    every byte of the file except a leading byte order mark, which fetch's
    ``text()`` drops. So ``md_sha256`` hashes the bytes with that one mark
    removed, or the driver's Markdown check would refuse a file it should
    accept.
    """
    md_bytes = b"# Title\r\n\r\n*Subtitle*\r\n\r\nText.\r\n"
    draft = m2s.convert("# Title\n\n*Subtitle*\n\nText.\n", {})
    assert m2s.summary(draft, md_bytes)["md_sha256"] == hashlib.sha256(md_bytes).hexdigest()
    marked = m2s.summary(draft, b"\xef\xbb\xbf" + md_bytes)["md_sha256"]
    assert marked == hashlib.sha256(md_bytes).hexdigest()
    twice = m2s.summary(draft, b"\xef\xbb\xbf\xef\xbb\xbf" + md_bytes)["md_sha256"]
    assert twice == hashlib.sha256(b"\xef\xbb\xbf" + md_bytes).hexdigest()


def test_the_subtitle_length_counts_what_substack_counts() -> None:
    """The page's ``subtitle.length`` counts UTF-16 units, and so does the summary.

    An emoji is one code point and two UTF-16 units, so a subtitle of ``a``,
    an emoji and ``b`` measures 4 against Substack's 255 limit, not 3.
    """
    draft = m2s.convert(f"# T\n\n*a{chr(0x1F600)}b*\n\nBody.\n", {})
    assert m2s.summary(draft, b"")["subtitle_length"] == 4


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


def test_the_command_line_reads_the_file_as_the_page_does(tmp_path: Path) -> None:
    """Line endings stay as they are and a leading byte order mark goes.

    The page reads the Markdown through fetch, and fetch's ``text()`` does
    both. Reading the file as Python text would turn CRLF into LF and give
    the in-page conversion a different tree to match. Only one mark goes, so
    a file opening with two keeps the second, and ``md_sha256`` hashes what
    is left. A non-ASCII character decodes as UTF-8.
    """
    bom = b"\xef\xbb\xbf"
    raw = (DIVERGENCES["carriage returns"] + "An arrow → stays.\r\n").encode("utf-8")
    for prefix, kept in ((bom, b""), (bom + bom, bom)):
        post = tmp_path / "post.md"
        post.write_bytes(prefix + raw)
        run = [sys.executable, str(SKILL_DIR / "md2substack.py"), str(post)]
        done = subprocess.run(run, capture_output=True, text=True, check=True, timeout=60)
        expected = m2s.convert((kept + raw).decode("utf-8"), {})
        assert json.loads(done.stdout) == expected
        assert json.loads(done.stdout) != m2s.convert(post.read_text(encoding="utf-8-sig"), {})
        run.insert(2, "--summary")
        brief = subprocess.run(run, capture_output=True, text=True, check=True, timeout=60)
        assert json.loads(brief.stdout)["md_sha256"] == hashlib.sha256(kept + raw).hexdigest()


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
