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
   The subtitle keeps its Markdown escapes as typed, so a ``\\$`` there reaches
   Substack with its backslash. ``SKILL.md`` says what to check before sending
   it.
2. ``### `` becomes a level-2 heading and ``## `` a level-1 heading. Substack
   keeps the post title in its own field rather than the body, so each level
   moves up one.
3. A ```` ```math ```` fence becomes one ``latex_block``, with ids
   ``EQSTAT01``, ``EQSTAT02`` and on in order.
4. Any other fence, such as ```` ```latex ```` showing an equation's source,
   becomes a plain-text ``highlighted_code_block``. That is the editor's code
   block node, and it offers no LaTeX highlighting.
5. An image line ``![alt](path)`` becomes a ``captionedImage``. The next
   non-blank line becomes its caption when it is wholly in single asterisks.
6. Lines opening ``1. `` or ``- `` become an ordered or bulleted list. An item
   may carry one nested list, indented three spaces.
7. Every other run of non-blank lines becomes one paragraph.

Inside text, ``**strong**``, ``*em*``, ```code``` and ``[links](url)`` become
marks, and ``\\~`` and ``\\$`` lose their backslash. LaTeX blocks keep theirs,
since a backslash there is TeX.

Three shapes are not handled, and two committed posts use them.

1. A pipe table, a run of lines opening ``|``, becomes one paragraph of
   literal pipes.
2. A ``####``, ``#####`` or ``######`` heading becomes a paragraph that starts
   with its hashes.
3. A linked image, ``[![alt](x.png)](x.png)``, becomes a paragraph holding a
   link whose text starts ``![alt``, with no image.

``blog/gld-gdx-cointegration-lessons.md`` and
``blog/price-spread-mean-reversion.md`` use them. Their drafts were made by
another route before this converter existed, and ``SKILL.md`` says what that
means for syncing them. A fence with no closing line raises ``ValueError``
rather than running off the end of the post.

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
``md_sha256``.
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

TOKEN = re.compile(r"\*\*(.+?)\*\*|\[([^\]]+)\]\(([^)]+)\)|`([^`]+)`|\*(.+?)\*")


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
    t = t.replace("\\~", "~").replace("\\$", "$")
    node = {"type": "text", "text": t}
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


def convert(md, images):
    """The draft's title, subtitle and body for one post's Markdown."""
    lines = md.split("\n")
    title = lines[0].removeprefix("# ").strip()
    subtitle = lines[2].strip().strip("*")
    body, i, n_heading, eq = [], 3, 0, 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("### "):
            body.append(
                {
                    "type": "heading",
                    "attrs": {"textAlign": None, "level": 2},
                    "content": inline(line[4:].strip()),
                }
            )
            i += 1
        elif line.startswith("## "):
            n_heading += 1
            if n_heading == 2:
                body.append(WIDGET)
            body.append(
                {
                    "type": "heading",
                    "attrs": {"textAlign": None, "level": 1},
                    "content": inline(line[3:].strip()),
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
        elif line.startswith("!["):
            m = re.match(r"!\[(.*)\]\(([^)]+)\)$", line)
            alt, path = m.group(1), m.group(2)
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
                            "href": None,
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
            while not lines[j].strip():
                j += 1
            cap = lines[j]
            if cap.startswith("*") and cap.endswith("*") and not cap.startswith("**"):
                node["content"].append({"type": "caption", "content": inline(cap[1:-1])})
                i = j + 1
            else:
                i += 1
            body.append(node)
        elif re.match(r"\d+\. ", line) or line.startswith("- "):
            ordered = bool(re.match(r"\d+\. ", line))
            items = []
            while i < len(lines) and (re.match(r"\d+\. ", lines[i]) or lines[i].startswith("- ")):
                items.append((re.sub(r"^(\d+\. |- )", "", lines[i]), []))
                i += 1
                # A nested list, ordered or bulleted, sits three spaces under its item.
                while i < len(lines) and re.match(r"   (\d+\. |- )", lines[i]):
                    items[-1][1].append(
                        (lines[i].startswith("   - "), re.sub(r"^   (\d+\. |- )", "", lines[i]))
                    )
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
            while (
                i < len(lines)
                and lines[i].strip()
                and not re.match(r"(### |## |```|!\[|\d+\. |- )", lines[i])
            ):
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

    ``md_sha256`` hashes the Markdown file's raw bytes, which is what the page
    hashes after fetching the file from GitHub. Hashing text read back in
    Python could differ, since reading text can translate line endings.
    """
    blocks = draft["body"]["content"]
    lines = walk_lines(draft["body"])
    return {
        "md_sha256": hashlib.sha256(md_bytes).hexdigest(),
        "conversion_sha256": _sha256(canonical(draft)),
        "body_sha256": _sha256(canonical(draft["body"])),
        "walk_sha256": _sha256("\n".join(lines)),
        "walk_lines": len(lines),
        "blocks": len(blocks),
        "widgets_at": [i for i, n in enumerate(blocks) if n["type"] == "subscribeWidget"],
        "subtitle_length": len(draft["subtitle"]),
    }


if __name__ == "__main__":
    args = sys.argv[1:]
    want_summary = args[:1] == ["--summary"]
    if want_summary:
        args = args[1:]
    with open(args[0], encoding="utf-8") as f:
        md = f.read()
    with open(args[0], "rb") as f:
        md_bytes = f.read()
    images = {}
    if len(args) > 1:
        with open(args[1], encoding="utf-8") as f:
            images = json.load(f)
    draft = convert(md, images)
    print(json.dumps(summary(draft, md_bytes) if want_summary else draft, ensure_ascii=False))
