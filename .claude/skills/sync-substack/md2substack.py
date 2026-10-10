"""Convert a blog post's Markdown into a Substack draft.

Substack stores a draft's body as ProseMirror JSON, a tree of typed nodes such
as ``paragraph``, ``heading`` and ``latex_block``, and its API takes that tree
rather than Markdown. Pasting Markdown into the editor lands as literal ``##``
text. So every draft made from ``blog/*.md`` goes through this conversion, and
the in-page copy in ``md2substack.js`` must produce the same tree, because the
draft is written from inside the signed-in Substack page. ``SKILL.md`` beside
this file says when to run which.

Usage::

    python3 md2substack.py blog/post.md images.json > draft.json
    python3 md2substack.py --summary blog/post.md images.json

The first prints ``{"title", "subtitle", "body"}``, with ``body`` the document
tree. The second prints the hashes and counts a session compares against the
live draft. ``images.json`` maps each figure's file name to the ``url``,
``width``, ``height`` and ``bytes`` Substack returned when the figure was
uploaded. A post with no figure needs no map.

The conversion handles the Markdown shapes below, listed in the order
``convert`` tries them.

1. The first line is ``# Title`` and the third is the italic subtitle line.
   The subtitle loses the backslash of ``\\$`` and ``\\~`` through the same
   function the body text uses, so the two cannot drift apart.
2. A heading of two to six hashes becomes a heading one level up, so ``## ``
   is level 1 and ``###### `` level 5. Substack keeps the post title in its
   own field rather than the body, which is why each level moves up one.
   Seven hashes, or hashes with no space after them, stay paragraph text.
3. A ```` ```math ```` fence becomes one ``latex_block``, with ids
   ``EQSTAT01``, ``EQSTAT02`` and on in order.
4. Any other fence, such as ```` ```latex ```` showing an equation's source,
   becomes a plain-text ``highlighted_code_block``. That is the editor's code
   block node, and it offers no LaTeX highlighting.
5. A line that is wholly an image, ``![alt](path)``, becomes a
   ``captionedImage``. The next non-blank line becomes its caption when it is
   wholly in single asterisks. A line that is wholly a linked image,
   ``[![alt](path)](target)``, becomes the same node. Its ``href`` is the
   target when that starts ``http://`` or ``https://``, and null otherwise,
   since a path relative to the repository means nothing on Substack. A line
   holding an image and more text is paragraph text.
6. A pipe table becomes a ``latex_block`` holding a LaTeX ``array``, the form
   the posts write by hand in a math fence, and takes the next ``EQSTAT`` id.
   Substack's editor has no table node. A table starts at a line opening
   ``|`` with a delimiter row under it, as GitHub reads one. A delimiter row
   of bare hyphens, with no ``|`` and no ``:``, starts no table, because
   GitHub reads the line above it as a heading. The table runs until a blank
   line or a line that opens another block, and any other line is a row, as
   on GitHub, whether it opens ``|`` or not. A ``|`` line with no delimiter
   row under it is a paragraph line. The price is that a cell loses its
   links and formatting.
7. Lines opening ``1. `` or ``- `` become an ordered or bulleted list. An item
   may carry one nested list, indented three spaces.
8. Every other run of non-blank lines becomes one paragraph. A paragraph ends
   at a blank line or at a line that opens any block above.

Inside text, ``**strong**``, ``*em*``, ```code``` and ``[links](url)`` become
marks, and ``\\~`` and ``\\$`` lose their backslash. LaTeX blocks keep theirs,
since a backslash there is TeX.

A table cell is read in two steps. ``cell_text`` turns its Markdown into plain
text.

1. A code span keeps its content as typed and loses its backticks.
2. Elsewhere, a backslash before ASCII punctuation is dropped, so ``\\|``,
   ``\\$`` and ``\\*`` become the bare character.
3. Strong text and emphasis keep their text, a link keeps its text, and an
   image keeps its alt text.
4. Each run of spaces and tabs becomes one space, code spans included, as
   GitHub's HTML draws it. MathJax would draw every space inside ``\\text{}``
   and a tab with no width.

A cell reads only the inline Markdown the body reads, which is code spans,
``**``, ``*``, links, images and backslash escapes. Everything else shows as
typed, such as ``_em_``, ``__strong__``, ``~~strike~~``, ``<br>``, an HTML
entity, an autolink or ``$math$``. That is part of the price the owner
accepted for tables.

``cell_latex`` then writes that text as LaTeX. Each run of ordinary characters
goes inside ``\\text{}``, spaces included. Each of ``$ % & # _ { }`` is written
outside it with a backslash, ``\\`` as ``\\backslash``, ``~`` as ``{\\sim}``
and ``^`` as ``{\\hat{\\ }}``. Substack draws LaTeX with MathJax and no
``textmacros`` package, so a backslash inside ``\\text{}`` prints as typed,
and running ``MathJax.tex2mml`` in Substack's page on 2026-10-10 drew each of
these escapes as its bare character. KaTeX refuses ``_``, ``^`` and ``%``
inside ``\\text{}``, which is why every special character stays outside it.
The caret sits over a space because ``{\\hat{}}`` has no width in either
renderer and overprints its neighbours. Measured on 2026-10-10,
``\\text{x}{\\hat{\\ }}\\text{2}`` drew 5.06 px wider than ``x2`` in MathJax
3.2.2 and 6.06 px wider in KaTeX 0.16.9. An empty cell is the empty string, a
short row is padded with empty cells and a long one is cut, as GitHub does.

Lines and cells are trimmed of ASCII whitespace only, which is space, tab,
line feed, carriage return, form feed and vertical tab. Python's ``strip()``
and JavaScript's ``trim()`` each strip characters outside that set that the
other keeps, so neither is used. A fence with no closing line raises
``ValueError`` rather than running off the end of the post.

Two subscribe widgets are added. One sits before the second ``## `` heading,
which is after the opening section, and one closes the post. That is where the
owner placed them on the first posts. Its caption is the publication's public
text, the same on every post.

**Where this came from.** No repository held this file before. Sessions wrote
it in their scratchpads by late September 2026, in a temporary directory that
macOS clears on reboot, and copied it from one scratchpad to the next. A
snapshot of every surviving copy taken on 2026-10-10 found two Python
versions, the newer a strict superset of the older. This is the newer one,
sha1 ``23b73235``, last changed on 2026-10-10 when the vx-es post brought the
first ``\\$`` in prose. The other, sha1 ``3cee9fed``, differed only in leaving
``\\$`` escaped. It was checked in on a branch from ``da64a66``. The copy changed three things.

1. The docstrings and comments were rewritten, and the code was reformatted
   to this repo's ruff settings, which moved lines and changed no behaviour.
2. ``canonical``, ``walk_lines`` and ``summary`` were added. The sessions kept
   the first two as scratch scripts beside each conversion and retyped their
   in-page copies each time, so the local and in-page checks could drift
   apart. The third gathers what those scripts printed.
3. The command line gained ``--summary``.

After the check-in, ``_fence_end`` replaced the two fence loops, which raised
``IndexError`` on a fence with no closing line, and ``summary`` gained
``md_sha256``. The change for issue 472 then taught both copies pipe tables,
headings of four to six hashes and linked images, which each came out as
literal Markdown before, and unescaped the subtitle, which kept its
backslashes before. It also made the two copies agree on whitespace and digits
outside ASCII, where they had read the same line differently. The review of
that change matched GitHub on where a table ends and on a delimiter row of
bare hyphens, gave the caret a width, collapsed whitespace in cells, and
stopped two kinds of image line from raising. It also made ``md_sha256`` and
``subtitle_length`` measure what the page measures.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys

LINK = {"target": "_blank", "rel": "noopener noreferrer nofollow", "class": None}
WIDGET = {
    "type": "subscribeWidget",
    "attrs": {"url": "%%checkout_url%%", "text": "Subscribe", "language": "en"},
    "content": [
        {
            "type": "ctaCaption",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "baowebdev is a reader-supported publication. To receive new posts "
                        "and support my work, consider becoming a free or paid subscriber."
                    ),
                }
            ],
        }
    ],
}

# What both converters trim from a line or a cell. Python's ``strip()`` also
# strips U+001C to U+001F and U+0085, and JavaScript's ``trim()`` also strips
# U+FEFF, so neither is used.
WHITESPACE = " \t\n\r\f\v"

# The byte order mark fetch's text() drops from the start of a file.
UTF8_BOM = b"\xef\xbb\xbf"

# The patterns avoid ``.``, ``\d``, ``\s`` and ``\w``, whose meaning differs
# between Python's ``re`` and JavaScript's RegExp, so ``md2substack.js`` can
# use the same text. Each string they meet is one line, or lines joined by
# spaces, so ``[^\n]`` matches any character in it.
TOKEN = re.compile(r"\*\*([^\n]+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*([^\n]+?)\*")
HEADING = re.compile(r"(#{2,6}) ")
IMAGE = re.compile(r"!\[([^\n]*)\]\(([^)]+)\)")
LINKED_IMAGE = re.compile(r"\[!\[([^\n]*)\]\(([^)]+)\)\]\(([^)]+)\)")
LIST_ITEM = re.compile(r"[0-9]+\. |- ")
NESTED_ITEM = re.compile(r"   ([0-9]+\. |- )")
# Lines opening a heading, a fence or a list item. An image or a linked image
# opens a block only when it is the whole line, so ``_opens_block`` tests those.
BLOCK_START = re.compile(r"#{2,6} |```|[0-9]+\. |- ")
DELIMITER_CELL = re.compile(r":?-+:?")
SPACE_RUN = re.compile(r"[ \t]+")

# Inside a table cell: an image, a link whose text may hold an image, strong
# text and emphasis, tried in that order at each position.
CELL_MARKUP = re.compile(
    r"!\[([^\]]*)\]\([^)]+\)"
    r"|\[((?:!\[[^\]]*\]\([^)]+\)|[^\]])+)\]\([^)]+\)"
    r"|\*\*([^\n]+?)\*\*"
    r"|\*([^\n]+?)\*"
)
CELL_HELD = re.compile(r"\\`([0-9]+)`")
ASCII_PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
LATEX_SPECIAL = {
    "$": "\\$",
    "%": "\\%",
    "&": "\\&",
    "#": "\\#",
    "_": "\\_",
    "{": "\\{",
    "}": "\\}",
    "\\": "\\backslash",
    "~": "{\\sim}",
    "^": "{\\hat{\\ }}",
}


def _trim(s):
    return s.strip(WHITESPACE)


def unescape(t):
    """Drop the backslash from ``\\~`` and ``\\$``, in body text and subtitle alike."""
    return t.replace("\\~", "~").replace("\\$", "$")


def inline(s, marks=()):
    """Split one line of text into text nodes, each carrying its marks."""
    out = []
    pos = 0
    for m in TOKEN.finditer(s):
        if m.start() > pos:
            out.append(_text(s[pos : m.start()], marks))
        if m.group(1) is not None:
            out += inline(m.group(1), marks + ({"type": "strong"},))
        elif m.group(2) is not None:
            link = {"type": "link", "attrs": {"href": m.group(3), **LINK}}
            out += inline(m.group(2), (link,) + marks)
        elif m.group(4) is not None:
            out.append(_text(m.group(4), marks + ({"type": "code"},)))
        else:
            out += inline(m.group(5), marks + ({"type": "em"},))
        pos = m.end()
    if pos < len(s):
        out.append(_text(s[pos:], marks))
    return [n for n in out if n["text"]]


def _text(t, marks):
    node = {"type": "text", "text": unescape(t)}
    if marks:
        node["marks"] = list(marks)
    return node


def para(s):
    return {"type": "paragraph", "attrs": {"textAlign": None}, "content": inline(s)}


def _fence_end(lines, i):
    """The index of the line closing the fence opened on line ``i``.

    A fence left open would otherwise run off the end of the post. The
    message names the line in the Markdown file, counting from 1, and
    ``fenceEnd`` in ``md2substack.js`` raises the same one.
    """
    j = i + 1
    while j < len(lines) and lines[j] != "```":
        j += 1
    if j == len(lines):
        raise ValueError(f"unterminated fence opened on line {i + 1}: {lines[i]}")
    return j


def _cells(row):
    """A table row's cells, untrimmed.

    One leading and one trailing ``|`` are dropped, and the rest splits at
    each ``|`` with no backslash before it, as GitHub splits a row.
    """
    s = _trim(row)
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cell = [], ""
    for k, ch in enumerate(s):
        if ch == "|" and (k == 0 or s[k - 1] != "\\"):
            cells.append(cell)
            cell = ""
        else:
            cell += ch
    cells.append(cell)
    return cells


def _table_columns(lines, i):
    """Each column's alignment when a table starts on line ``i``, else None.

    A table is a line opening ``|`` with a delimiter row straight under it.
    The delimiter row's cells are hyphens with an optional colon at either
    end, and it must have as many cells as the line above. ``:---`` and plain
    ``---`` align left, ``---:`` right and ``:---:`` centre, as GitHub draws
    them. A delimiter row with no ``|`` and no ``:`` is bare hyphens, which
    GitHub reads as underlining the line above into a heading, so it starts
    no table.
    """
    if not lines[i].startswith("|") or i + 1 >= len(lines):
        return None
    below = lines[i + 1]
    if "|" not in below and ":" not in below:
        return None
    marks = [_trim(c) for c in _cells(below)]
    if not all(DELIMITER_CELL.fullmatch(c) for c in marks):
        return None
    if len(_cells(lines[i])) != len(marks):
        return None
    return ["c" if c[0] == ":" and c[-1] == ":" else "r" if c[-1] == ":" else "l" for c in marks]


def _closing_run(s, j, run):
    """Where the next run of exactly ``run`` backticks at or after ``j`` starts, or -1."""
    while j < len(s):
        if s[j] == "`":
            k = j
            while k < len(s) and s[k] == "`":
                k += 1
            if k - j == run:
                return j
            j = k
        else:
            j += 1
    return -1


def _strip_markup(s):
    """Images become their alt text, links their text, and emphasis its text."""

    def keep(m):
        return _strip_markup(next(g for g in m.groups() if g is not None))

    return CELL_MARKUP.sub(keep, s)


def cell_text(cell):
    """A table cell's plain text, after its inline Markdown is read.

    Each code span and escaped character is held aside while the markup is
    read, written in its place as a backslash, a backtick, its number and a
    backtick. No cell can hold that sequence itself, because a backslash
    before a backtick is an escape and would be held aside too. Each run of
    spaces and tabs in the result becomes one space.
    """
    held, out, i = [], [], 0

    def hold(t):
        out.append(f"\\`{len(held)}`")
        held.append(t)

    while i < len(cell):
        ch = cell[i]
        if ch == "\\" and i + 1 < len(cell) and cell[i + 1] in ASCII_PUNCTUATION:
            hold(cell[i + 1])
            i += 2
        elif ch == "`":
            j = i
            while j < len(cell) and cell[j] == "`":
                j += 1
            close = _closing_run(cell, j, j - i)
            if close < 0:
                # Backticks with no matching run after them are literal.
                hold(cell[i:j])
                i = j
            else:
                code = cell[j:close]
                # As CommonMark does, one space comes off each end of a code
                # span that has one at both ends and is not all spaces.
                if code[:1] == " " and code[-1:] == " " and code.strip(" "):
                    code = code[1:-1]
                hold(code)
                i = close + (j - i)
        else:
            out.append(ch)
            i += 1
    text = CELL_HELD.sub(lambda m: held[int(m.group(1))], _strip_markup("".join(out)))
    return SPACE_RUN.sub(" ", text)


def cell_latex(text):
    """A cell's plain text as LaTeX that Substack's MathJax draws as typed.

    KaTeX draws it nearly so, but applies its text-mode ligatures, turning
    ``--`` into an en dash, ``---`` into an em dash, a backtick into an
    opening quote and ``'`` into a closing one. MathJax applies none of them.
    """
    out, run = [], ""
    for ch in text:
        if ch in LATEX_SPECIAL:
            if run:
                out.append("\\text{" + run + "}")
                run = ""
            out.append(LATEX_SPECIAL[ch])
        else:
            run += ch
    if run:
        out.append("\\text{" + run + "}")
    return "".join(out)


def table_latex(header, rows, columns):
    """A table as a LaTeX ``array``, laid out as the posts write one by hand.

    The header row ends with a line break and ``\\hline``, and each body row
    but the last ends with a line break. A table with no body rows keeps the
    rule under its header, as GitHub draws a border under a lone header.
    GitHub unescapes ``\\|`` in a cell before reading its Markdown, inside
    code spans too, so this does the same.
    """

    def row(cells):
        cells = (cells + [""] * len(columns))[: len(columns)]
        return " & ".join(cell_latex(cell_text(_trim(c).replace("\\|", "|"))) for c in cells)

    out = ["\\begin{array}{" + "|".join(columns) + "}", row(header) + " \\\\ \\hline"]
    out += [row(r) + " \\\\" for r in rows[:-1]] + [row(r) for r in rows[-1:]]
    out.append("\\end{array}")
    return "\n".join(out)


def _opens_block(line):
    """Whether a line opens a heading, fence, list, image or linked image."""
    return bool(BLOCK_START.match(line) or IMAGE.fullmatch(line) or LINKED_IMAGE.fullmatch(line))


def _starts_block(lines, i):
    """Whether line ``i`` opens a block, which ends any paragraph above it."""
    return _opens_block(lines[i]) or _table_columns(lines, i) is not None


def _figure(lines, i, images, alt, path, href):
    """A captioned image, and the index of the line after it and its caption."""
    img = images[path.rsplit("/", 1)[-1]]
    node = {
        "type": "captionedImage",
        "content": [
            {
                "type": "image2",
                "attrs": {
                    "src": img["url"],
                    "srcNoWatermark": None,
                    "fullscreen": None,
                    "imageSize": None,
                    "height": img["height"],
                    "width": img["width"],
                    "resizeWidth": None,
                    "bytes": img["bytes"],
                    "alt": alt,
                    "title": None,
                    "type": "image/png",
                    "href": href,
                    "belowTheFold": False,
                    "topImage": False,
                    "internalRedirect": None,
                    "isProcessing": False,
                    "align": None,
                    "offset": False,
                },
            }
        ],
    }
    j = i + 1
    while j < len(lines) and not _trim(lines[j]):
        j += 1
    # A figure on the post's last non-blank line has no caption to look for.
    cap = lines[j] if j < len(lines) else ""
    if cap.startswith("*") and cap.endswith("*") and not cap.startswith("**"):
        node["content"].append({"type": "caption", "content": inline(cap[1:-1])})
        return node, j + 1
    return node, i + 1


def convert(md, images):
    """The draft's title, subtitle and body for one post's Markdown."""
    lines = md.split("\n")
    title = _trim(lines[0].removeprefix("# "))
    subtitle = unescape(_trim(lines[2]).strip("*"))
    body, i, n_heading, eq = [], 3, 0, 0
    while i < len(lines):
        line = lines[i]
        if not _trim(line):
            i += 1
            continue
        heading = HEADING.match(line)
        image = IMAGE.fullmatch(line)
        linked = LINKED_IMAGE.fullmatch(line)
        columns = _table_columns(lines, i)
        if heading:
            level = len(heading.group(1)) - 1
            if level == 1:
                n_heading += 1
                if n_heading == 2:
                    body.append(WIDGET)
            body.append(
                {
                    "type": "heading",
                    "attrs": {"textAlign": None, "level": level},
                    "content": inline(_trim(line[heading.end() :])),
                }
            )
            i += 1
        elif line.startswith("```math"):
            j = _fence_end(lines, i)
            eq += 1
            body.append(
                {
                    "type": "latex_block",
                    "attrs": {
                        "persistentExpression": "\n".join(lines[i + 1 : j]),
                        "id": f"EQSTAT{eq:02d}",
                    },
                }
            )
            i = j + 1
        elif line.startswith("```"):
            j = _fence_end(lines, i)
            code = "\n".join(lines[i + 1 : j])
            node = {
                "type": "highlighted_code_block",
                "attrs": {"language": "plaintext", "nodeId": None},
            }
            if code:
                node["content"] = [{"type": "text", "text": code}]
            body.append(node)
            i = j + 1
        elif image:
            node, i = _figure(lines, i, images, image.group(1), image.group(2), None)
            body.append(node)
        elif linked:
            target = linked.group(3)
            href = target if target.startswith(("http://", "https://")) else None
            node, i = _figure(lines, i, images, linked.group(1), linked.group(2), href)
            body.append(node)
        elif columns:
            # As on GitHub, every line up to a blank one or one that opens
            # another block is a row, whether it opens "|" or not.
            j = i + 2
            while j < len(lines) and _trim(lines[j]) and not _opens_block(lines[j]):
                j += 1
            rows = [_cells(r) for r in lines[i + 2 : j]]
            eq += 1
            body.append(
                {
                    "type": "latex_block",
                    "attrs": {
                        "persistentExpression": table_latex(_cells(line), rows, columns),
                        "id": f"EQSTAT{eq:02d}",
                    },
                }
            )
            i = j
        elif LIST_ITEM.match(line):
            ordered = not line.startswith("- ")
            items = []
            while i < len(lines) and (item := LIST_ITEM.match(lines[i])):
                items.append((lines[i][item.end() :], []))
                i += 1
                # A nested list, ordered or bulleted, sits three spaces under its item.
                while i < len(lines) and (nested := NESTED_ITEM.match(lines[i])):
                    items[-1][1].append((lines[i].startswith("   - "), lines[i][nested.end() :]))
                    i += 1
            li = []
            for t, sub in items:
                content = [para(t)]
                if sub:
                    subitems = [{"type": "list_item", "content": [para(s)]} for _, s in sub]
                    if sub[0][0]:
                        content.append({"type": "bullet_list", "content": subitems})
                    else:
                        content.append(
                            {
                                "type": "ordered_list",
                                "attrs": {"start": 1, "type": None, "order": 1},
                                "content": subitems,
                            }
                        )
                li.append({"type": "list_item", "content": content})
            if ordered:
                body.append(
                    {
                        "type": "ordered_list",
                        "attrs": {"start": 1, "type": None, "order": 1},
                        "content": li,
                    }
                )
            else:
                body.append({"type": "bullet_list", "content": li})
        else:
            buf = [line]
            i += 1
            while i < len(lines) and _trim(lines[i]) and not _starts_block(lines, i):
                buf.append(lines[i])
                i += 1
            body.append(para(" ".join(buf)))
    body.append(WIDGET)
    return {"title": title, "subtitle": subtitle, "body": {"type": "doc", "content": body}}


def canonical(value):
    """One string per JSON value, whatever order its keys arrived in.

    Keys are sorted and no whitespace is added, so a draft read back from
    Substack and a fresh conversion compare equal exactly when their trees do.
    ``canon`` in ``md2substack.js`` produces the same string.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def walk_lines(node, path=""):
    """One line per text run, LaTeX block and image, each naming its place.

    A line reads ``path|marks|text``, where the path lists each ancestor's
    index and the first three letters of its type. Comparing these lines
    rather than whole trees ignores attributes Substack adds on a save, while
    still catching moved, re-marked or re-worded text. ``walkLines`` in
    ``md2substack.js`` produces the same lines.
    """
    out = []
    kind = node.get("type")
    if kind == "text":
        marks = ",".join(
            sorted(
                m["type"] + (":" + m["attrs"]["href"] if m["type"] == "link" else "")
                for m in node.get("marks") or []
            )
        )
        out.append(f"{path}|{marks}|{node['text']}")
    if kind == "latex_block":
        out.append(f"{path}|latex|{node['attrs']['persistentExpression']}")
    if kind == "image2":
        out.append(f"{path}|img|{node['attrs']['src']}|{node['attrs']['alt']}")
    for i, child in enumerate(node.get("content") or []):
        out += walk_lines(child, f"{path}/{i}{child.get('type', '')[:3]}")
    return out


def _sha256(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def summary(draft, md_bytes):
    """The hashes and counts a session compares against the live draft.

    ``md_sha256`` hashes the Markdown file's bytes with one leading UTF-8 byte
    order mark removed. That is what the page hashes, since it encodes the
    text fetch returned and fetch's ``text()`` drops that mark. Hashing text
    read back in Python could differ, since reading text can translate line
    endings.

    ``subtitle_length`` counts UTF-16 code units, as the page's
    ``subtitle.length`` does and as Substack's 255 limit counts. A character
    outside the Basic Multilingual Plane, such as an emoji, counts as two.
    """
    blocks = draft["body"]["content"]
    lines = walk_lines(draft["body"])
    return {
        "md_sha256": hashlib.sha256(md_bytes.removeprefix(UTF8_BOM)).hexdigest(),
        "conversion_sha256": _sha256(canonical(draft)),
        "body_sha256": _sha256(canonical(draft["body"])),
        "walk_sha256": _sha256("\n".join(lines)),
        "walk_lines": len(lines),
        "blocks": len(blocks),
        "widgets_at": [i for i, n in enumerate(blocks) if n["type"] == "subscribeWidget"],
        "subtitle_length": len(draft["subtitle"].encode("utf-16-le")) // 2,
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    want_summary = args[:1] == ["--summary"]
    if want_summary:
        args = args[1:]
    with open(args[0], "rb") as f:
        md_bytes = f.read()
    # The page reads the file through fetch, whose text() keeps line endings
    # as they are and drops a leading byte order mark. Reading the file as
    # text here would turn CRLF into LF, so it is decoded the way fetch does.
    md = md_bytes.removeprefix(UTF8_BOM).decode("utf-8")
    images = {}
    if len(args) > 1:
        with open(args[1], encoding="utf-8") as f:
            images = json.load(f)
    draft = convert(md, images)
    print(json.dumps(summary(draft, md_bytes) if want_summary else draft, ensure_ascii=False))
