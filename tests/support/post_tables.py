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
"""

from __future__ import annotations

import re

#: A number cell of a ``math`` table: a date, then a signed decimal or integer.
CELL = re.compile(r"\d{4}-\d{2}-\d{2}|-?\d+(?:\.\d+)?")


def not_found_once(text: str, fragments: list[str]) -> list[str]:
    """The fragments the post does not hold exactly once, so each names one place."""
    return [fragment for fragment in fragments if text.count(fragment) != 1]


def tables(text: str) -> list[list[list[str]]]:
    """Each ``math`` array's cells, row by row, in the order the arrays appear.

    A cell holding a number reads as that number. A cell holding none, such
    as a row label, a column head or ``\\text{none}``, reads as the words
    inside its ``\\text{}``, and an empty cell as ``""``. ``\\small``, each
    array's column spec, ``\\hline`` and ``\\text{-}`` inside a date are
    dealt with first, so neither the layout nor a date split for
    typesetting adds or splits a number.
    """
    blocks = re.findall(r"```math\n(.*?)```", text, flags=re.S)
    grids = []
    for block in blocks:
        if "\\begin{array}" not in block:
            continue
        plain = re.sub(
            r"\\small|\\hline|\\begin\{array\}\{[^}]*\}|\\end\{array\}", "", block
        ).replace("\\text{-}", "-")
        grid = []
        for row in plain.split("\\\\"):
            cells = row.split("&")
            numbers = [CELL.findall(cell) for cell in cells]
            assert all(len(found) <= 1 for found in numbers), row
            words = [re.search(r"\\text\{([^}]*)\}", cell) for cell in cells]
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
