# Committed vintages

Eight price series, committed because the numbers in
[tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py) were
computed from these exact bytes. A vendor restates an adjusted series without
announcing it, so a result checked against a fresh download is a result checked
against different data. [docs/design.md](../docs/design.md) carries the
reasoning.

Nothing regenerates these eight files. No fetch script was ported, and a
re-download would move the pinned numbers and fail the suite, which is the
behaviour that makes the pins worth having. Replacing a file is therefore a
deliberate act with a visible cost, not a refresh.

A ninth vintage does not arrive by hand. `chan.vintage.record_vintage` writes
one and records it, and refuses to overwrite either the file or its entry, so
adding a series is a recorded act and replacing one is not an act the recorder
performs at all. It does not download. A caller hands it rows, which is what
keeps every rule it enforces testable with no network.

A recorded vintage's name is load-bearing. The recorder builds it by joining
the five identity fields, so the vendor, symbol, price basis, span and download
date are recoverable from the path without reading a byte, and
[tests/test_vintage.py](../tests/test_vintage.py) holds every recorded entry to
the name its file took. Renaming such a file fails the suite either way.
Renaming the file alone leaves an entry naming nothing, and renaming the entry
with it makes the fields and the name disagree. The eight above are exempt,
because they were committed before the recorder existed and carry hand-given
names.

That check is what stands between a recorded entry and a file it does not
describe, and it is worth saying what it does not do. It compares the record
against its own shadow, so it catches an edit to one side and never an entry
that was consistent when it was written. The symbol's case is outside it too,
because the join lowercases it. `## Header shape` below is why the bytes cannot
carry the symbol instead.

## What each file is

A vintage is one download of one series, identified by vendor, symbol, span,
download date, and which price the series carries.

| File | Vendor | Symbol | Price | Span | Downloaded |
| --- | --- | --- | --- | --- | --- |
| `gld_20yr_prices.csv` | yfinance | GLD | adjusted | 2006-06-19 .. 2026-06-16 | 2026-06-16 |
| `gld_20yr_prices_unadjusted.csv` | yfinance | GLD | raw | 2004-11-18 .. 2026-08-27 | 2026-08-27 |
| `gdx_20yr_prices.csv` | yfinance | GDX | adjusted | 2006-05-22 .. 2026-08-27 | 2026-08-27 |
| `gdx_20yr_prices_unadjusted.csv` | yfinance | GDX | raw | 2006-05-22 .. 2026-08-27 | 2026-08-27 |
| `gld_chan.csv` | Chan's `GLD.xls` | GLD | adjusted | 2004-11-18 .. 2007-11-30 | saved 2007-12-02 |
| `gdx_chan.csv` | Chan's `GDX.xls` | GDX | adjusted | 2006-05-23 .. 2007-11-30 | saved 2007-12-02 |
| `ko_chan.csv` | Chan's `KO.xls` | KO | adjusted | 1962-01-02 .. 2008-01-18 | saved 2008-01-23 |
| `pep_chan.csv` | Chan's `PEP.xls` | PEP | adjusted | 1977-01-03 .. 2008-01-18 | saved 2008-01-23 |

The four yfinance files were not all taken on one day. `gld_20yr_prices.csv`
was downloaded on 2026-06-16 and the other three on 2026-08-27, which leaves
GLD's adjusted series covering a different span from its raw twin at both ends.
It starts nineteen months later, in 2006-06 against 2004-11, and stops ten
weeks earlier, in 2026-06 against 2026-08.

Nobody intended that. The sibling repo carried a single comment dating all four
files to 2026-08-27, and this table is what caught it. That is the argument for
recording a download date per file rather than per directory, which is how the
misattribution happened in the first place.

The `*_chan.csv` files are a different kind of source. Each is the
adjusted-close column of Ernest Chan's own book-companion spreadsheet, taken
from the public mirror at
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading).
The date given is when Chan last saved the workbook, which is the closest thing
these files have to a download date. Their checksums, as `.xls`, are recorded
in [src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py) next to
the runs that read them.

## Header shape

The eight files above carry a three-row header before the data, written by
yfinance's multi-index frame:

```text
Price,Close
Ticker,GLD
Date,
2004-11-18,44.380001068115234
```

A recorded vintage carries one header row, `Date,Close`, and nothing else.
Two shapes rather than one is deliberate. The three rows above are an artifact
of one vendor's frame, and writing `Price,Close` at the top of a series some
other vendor returned would be a claim the file has no business making.

`load_close` drops every leading row whose first field does not parse as a
date, so it reads either shape and does not depend on a row count.

## Verifying the bytes

```bash
cd data && shasum -a 256 -c checksums.sha256
```

On a checkout whose bytes are the committed bytes, a mismatch means the file
changed, and any number pinned against it is no longer a number computed from
it. [.gitattributes](../.gitattributes) is what makes that condition hold, with
`data/** -text` over this directory. Without it, a clone made with
`core.autocrlf=true`, the default of Git for Windows, rewrites every line
ending here, and the check reports no mismatch at all. It reports eight files
`shasum` cannot open, because the list of filenames was rewritten along with
the vintages. The committed bytes are intact throughout, so every pinned number
is fine.

That attribute does not repair a clone made before it. There the working tree
keeps its carriage returns, and `git status` goes from clean to a list of
modified paths under `data/`, because the attribute forbids the normalization
that was hiding them. On that list is every tracked file here whose bytes the
delivering checkout did not rewrite on the way in. Committing them writes
carriage returns over the vintages and makes every recorded sha256 false, which
is the failure this record exists to prevent.

Read `git diff --stat -- data/` first, to confirm every path it lists is the
rewrite rather than an edit somebody made. Then `git checkout -- data/`
restores the committed bytes. It restores every tracked file here, so an
unstaged edit to this README or to `vintages.jsonl` goes with them and nothing
stashes it. Not `git reset --hard`, which discards uncommitted work across the
whole tree, and not `git rm --cached -r .`, which is for a change of stored
bytes rather than of working-tree shape.

Two files carry that record.

1. [vintages.jsonl](vintages.jsonl) is the record. One JSON object per line,
   naming each vintage's vendor, symbol, price basis, span, date, path, row
   count and sha256. A line carries `download_date` when a vendor was asked for
   the series and `saved_date` for the four lifted from Chan's workbooks, whose
   date is when he last saved one rather than when anything was fetched. Those
   four name their vendor `chan-xls`, which is the table's "Chan's `GLD.xls`"
   in a form a filename can hold.

   Its eight lines were written by hand, because the recorder refuses a path
   already on disk and all eight were here before it existed. They are the only
   lines that will ever be.
2. [checksums.sha256](checksums.sha256) is a projection of it, regenerated
   whenever a vintage is recorded, so `shasum` keeps working without a second
   surface anyone has to remember to update.

`TestTheCommittedManifest` in
[tests/test_vintage.py](../tests/test_vintage.py) fails on five states: when an
entry stops describing the file it names, when a file here has no entry, when
the projection stops matching the record, when one of the eight above stops
carrying the identity it was given, and when a recorded entry stops agreeing
with the name its file took. The table above is a third telling and is still
hand-written, which
[issue 43](https://github.com/l3a0/quantitative-trading/issues/43) closes.
