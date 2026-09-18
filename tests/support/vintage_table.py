"""Read and edit `data/README.md`'s table, the hand-written telling of the record.

Two surfaces state each committed vintage's vendor, symbol, price basis, span
and date. `data/vintages.jsonl` is the record, written by the recorder, and the
table under `## What each file is` is prose a person typed.
`tests/test_vintage.py` holds the second to the first, and this module is how it
reads the table and how a negative case breaks a row.

Reading goes through :func:`blank_fences` rather than :func:`blank_code`, and
the cells come out of the blanked text so that choice decides what the check
compares. `blank_code` blanks inline backtick spans as well as fenced blocks,
and every File cell and all four workbook names in the Vendor column are
backticked, so a reader built on it hands back eight rows carrying no filename
at all. `CLAUDE.md` records the same distinction for
`test_no_prose_surface_names_a_line_number`, which needed `blank_fences` for the
same reason. Blanking at all is what keeps a table inside a fenced block from
reading as the record's own.

Editing writes the raw line at the position the blanked text located, which is
the same text for every row no fence hides. It goes through the located row
rather than through a string replacement, which is the reason
:func:`tests.support.committed_vintages.rewrite_entry` goes through JSON. Every
value a negative case would change also appears in the prose around the table:
`GLD` three more times, `adjusted` three, `yfinance` twice and `2026-08-27`
twice. A replacement rewrites sentences the check never reads, so the case can
go green on an edit that landed somewhere else.

An edit that matches no row raises rather than passing, for the same reason
`rewrite_entry` does. Every case here asserts that a check fails afterwards, so
a mistyped path would otherwise report that nothing raised instead of that
nothing was edited.
"""

from __future__ import annotations

from pathlib import Path

from tests.support.markdown_sweep import blank_fences

#: The file holding the table, inside the directory holding the vintages.
README_NAME = "README.md"

#: The heading the table sits under. The table is found by this rather than by
#: its row shape, so a renamed heading is an error rather than zero rows.
TABLE_HEADING = "## What each file is"

#: The column headers, in the order the table writes them.
COLUMNS = ("File", "Vendor", "Symbol", "Price", "Span", "Downloaded")

#: Keyword form of each column, so a caller writes ``vendor=`` rather than
#: ``**{"Vendor": ...}``.
KEYWORDS = {column.lower(): column for column in COLUMNS}


def read_table(directory: Path) -> dict[str, dict[str, str]]:
    """Every row of the table, keyed by the path its File cell names.

    The cells come back as they are written, backticks included, because the
    check compares each against a cell it builds in the table's own spelling. A
    reader that stripped them would hide the difference between a workbook name
    and a bare vendor string, which is one of the things being compared. The key
    is the path with its backticks off, because the path is what pairs a row
    with an entry, and the File cell's own spelling is compared like any other.
    """
    prose, _, rows = _located(directory)
    table: dict[str, dict[str, str]] = {}
    for number in rows:
        cells = dict(zip(COLUMNS, _cells(prose[number]), strict=True))
        path = cells["File"].strip("`")
        assert path not in table, f"{path}: the table names it twice"
        table[path] = cells
    return table


def rewrite_row(directory: Path, named: str, **changes: str) -> None:
    """Hand-edit one row's cells, which is the act the agreement check catches.

    Changes are keyed by the lowercased column name, so ``vendor="acme"``
    rewrites the Vendor cell of the row whose File cell names ``named``. Writing
    ``file=`` rewrites the File cell itself, which is how a case drives a row
    whose path, or whose spelling of it, stops being the one the manifest
    records.
    """
    columns = _columns_named(changes)
    prose, lines, rows = _located(directory)
    number = _row_naming(prose, rows, named)
    cells = dict(zip(COLUMNS, _cells(lines[number]), strict=True))
    cells.update(columns)
    lines[number] = row_line(cells[column] for column in COLUMNS)
    _write(directory, lines)


def drop_row(directory: Path, named: str) -> None:
    """Delete the row whose File cell names ``named``, leaving the rest alone."""
    prose, lines, rows = _located(directory)
    del lines[_row_naming(prose, rows, named)]
    _write(directory, lines)


def add_row(directory: Path, **cells: str) -> None:
    """Append a row after the last one, taking every column as a keyword."""
    columns = _columns_named(cells)
    _, lines, rows = _located(directory)
    lines.insert(rows[-1] + 1, row_line(columns[column] for column in COLUMNS))
    _write(directory, lines)


def row_line(cells) -> str:
    """One table row as the file writes it, which is also how a case finds one."""
    return "| " + " | ".join(cells) + " |"


def _columns_named(changes: dict[str, str]) -> dict[str, str]:
    return {KEYWORDS[keyword]: value for keyword, value in changes.items()}


def _located(directory: Path) -> tuple[list[str], list[str], list[int]]:
    """The blanked lines, the raw lines, and the line numbers of the table's rows.

    The table is found by its heading and its column names rather than by its
    row shape. A check driven from the table side passes on zero rows, and a
    renamed heading produces zero rows, so finding nothing raises here instead.

    The delimiter row is filtered rather than asserted at a position, so the walk
    says what a row is instead of counting how many lines come before the first
    one.
    """
    lines = _lines(directory)
    prose = blank_fences("\n".join(lines)).split("\n")
    headings = [number for number, line in enumerate(prose) if line.strip() == TABLE_HEADING]
    assert len(headings) == 1, (
        f"{README_NAME} holds {len(headings)} headings reading {TABLE_HEADING}"
    )

    numbers = []
    for number in range(headings[0] + 1, len(prose)):
        stripped = prose[number].strip()
        if stripped.startswith("##"):
            break
        if stripped.startswith("|"):
            numbers.append(number)

    assert numbers, f"{TABLE_HEADING} carries no table"
    columns = tuple(_cells(prose[numbers[0]]))
    assert columns == COLUMNS, f"the table's columns read {columns}"
    return prose, lines, [number for number in numbers[1:] if not _is_delimiter(prose[number])]


def _row_naming(prose: list[str], rows: list[int], named: str) -> int:
    found = [number for number in rows if _cells(prose[number])[0].strip("`") == named]
    assert len(found) == 1, f"{named}: the table holds {len(found)} rows naming it"
    return found[0]


def _lines(directory: Path) -> list[str]:
    return (directory / README_NAME).read_text(encoding="utf-8").split("\n")


def _write(directory: Path, lines: list[str]) -> None:
    (directory / README_NAME).write_text("\n".join(lines), encoding="utf-8")


def _cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_delimiter(line: str) -> bool:
    return set("".join(_cells(line))) == {"-"}
