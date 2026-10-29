"""Read a blog post's quoted figures and its ``math`` tables, for the classes that check them.

A ``TestWhatThePostQuotes`` class builds each run figure from the run and
looks for it in the post. :func:`not_found_once` says which short fragments
the post does not hold exactly once, so each fragment names one place.
:func:`tables` reads every ``math`` array as a grid of cells, and
:func:`either_way` gives a grid both as laid out and turned on its side, so a
table passes whichever way the post sets it.

The three functions and :data:`CELL` came out of
``tests/test_calendar_spread_reversion.py``'s class unchanged, so that the
crude oil and VX calendar spread posts read their tables the same way.
``blog/kalman-hedge-lessons.md`` later needed two more things of
:func:`tables`, and neither changes a grid the other posts' tables give.

1. A row label stacked in an array of its own reads as one cell of words,
   even where its words hold numbers, such as "rows 1 and 2".
2. A thousands separator set as ``{,}`` reads as a comma, so ``1{,}250``
   reads as ``1,250``.

A number inside a ``\\text{}`` that is not stacked still reads as the cell,
because the VX post's tables are read that way. So ``\\text{B1}`` reads as
``1``, and ``\\text{Rolling 250-day mean}`` as ``250``.
"""

from __future__ import annotations

import re

#: A number cell of a ``math`` table: a date, a number with thousands
#: separators, then a signed decimal or integer.
CELL = re.compile(r"\d{4}-\d{2}-\d{2}|-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?")

#: A ``\text{}`` and the words inside it.
TEXT = re.compile(r"\\text\{([^}]*)\}")

#: A stacked label once :func:`tables` has joined its lines, and its words.
STACKED = re.compile(r"\\stacked\{([^}]*)\}")

#: An array holding no other array, which inside a table is a stacked label.
INNER = re.compile(
    r"\\begin\{array\}\{[^}]*\}((?:(?!\\begin\{array\}).)*?)\\end\{array\}", flags=re.S
)


def not_found_once(text: str, fragments: list[str]) -> list[str]:
    """The fragments the post does not hold exactly once, so each names one place."""
    return [fragment for fragment in fragments if text.count(fragment) != 1]


def _one_label(stacked: re.Match[str]) -> str:
    """A label stacked in an array of its own, as one ``\\stacked{}`` of its lines' words."""
    return "\\stacked{" + " ".join(words.strip() for words in TEXT.findall(stacked[1])) + "}"


def tables(text: str) -> list[list[list[str]]]:
    """Each ``math`` array's cells, row by row, in the order the arrays appear.

    A cell holding a number reads as that number. A cell holding none, such
    as a row label, a column head or ``\\text{none}``, reads as the words
    inside its ``\\text{}``, and an empty cell as ``""``. A label stacked in
    an array of its own reads as its lines' words joined by spaces, whatever
    numbers they hold. ``\\small``, each array's column spec, ``\\hline``,
    ``\\text{-}`` inside a date and ``{,}`` inside a number are dealt with
    first, so neither the layout nor a number set for typesetting adds or
    splits a number.
    """
    blocks = re.findall(r"```math\n(.*?)```", text, flags=re.S)
    grids = []
    for block in blocks:
        if "\\begin{array}" not in block:
            continue
        while block.count("\\begin{array}") > 1:
            block = INNER.sub(_one_label, block, count=1)
        plain = (
            re.sub(r"\\small|\\hline|\\begin\{array\}\{[^}]*\}|\\end\{array\}", "", block)
            .replace("\\text{-}", "-")
            .replace("{,}", ",")
        )
        grid = []
        for row in plain.split("\\\\"):
            cells = row.split("&")
            numbers = [CELL.findall(STACKED.sub(" ", cell)) for cell in cells]
            assert all(len(found) <= 1 for found in numbers), row
            words = [STACKED.search(cell) or TEXT.search(cell) for cell in cells]
            grid.append(
                [
                    found[0] if found else (word[1].strip() if word else "")
                    for found, word in zip(numbers, words, strict=True)
                ]
            )
        grids.append(grid)
    return grids


def either_way(rows: list[list[str]]) -> tuple[list[list[str]], list[list[str]]]:
    """A table as the post lays it out, and the same table turned on its side."""
    return rows, [list(column) for column in zip(*rows, strict=True)]
