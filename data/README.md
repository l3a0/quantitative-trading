# Committed vintages

The price series every run here reads, committed because the numbers the suite
pins were computed from these exact bytes. A vendor restates an adjusted series
without announcing it, so a result checked against a fresh download is a result
checked against different data. [docs/design.md](../docs/design.md) carries the
reasoning.

Nothing regenerates these files. No fetch script was ported, and a re-download
would move the pinned numbers and fail the suite, which is the behaviour that
makes the pins worth having. Replacing a file is therefore a deliberate act
with a visible cost, not a refresh.

A vintage arrives one of two ways, and which one decides what holds it.
`chan.vintage.record_vintage` writes the file and appends its entry, and
refuses to overwrite either, so recording a series is a recorded act and
replacing one is not an act the recorder performs at all. It does not download.
A caller hands it rows, which is what keeps every rule it enforces testable
with no network.

The other way is by hand, and it did not stop when the recorder arrived. The
recorder takes a download date and builds a name out of it, and a column lifted
from one of Chan's workbooks has no download date to give it, so nothing can
record one. Every such column is typed into the record by hand. `spy_chan.csv`
is the first to arrive that way since `chan.vintage` existed, and
[issue 124](https://github.com/l3a0/quantitative-trading/issues/124) is where
that was settled.

A recorded vintage's name is load-bearing. The recorder builds it by joining
the five identity fields, so the vendor, symbol, price basis, span and download
date are recoverable from the path without reading a byte, and
[tests/test_vintage.py](../tests/test_vintage.py) holds every recorded entry to
the name its file took. Renaming such a file fails the suite either way.
Renaming the file alone leaves an entry naming nothing, and renaming the entry
with it makes the fields and the name disagree. The hand-written files above
are exempt, because nothing built their names out of their fields and so
nothing can compare the two. What holds a hand-written entry instead is the
identity pinned for it in
[tests/support/committed_vintages.py](../tests/support/committed_vintages.py),
and its own `Ticker,` header row, which names the series its bytes carry.

That check is what stands between a recorded entry and a file it does not
describe, and it is worth saying what it does not do. It compares the record
against its own shadow, so it catches an edit to one side and never an entry
that was consistent when it was written. The symbol's case is outside it too,
because the join lowercases it, and what catches a case edit there is
`chan.vintage`'s own refusal of a line whose vendor, symbol or price basis is
not the spelling the recorder would have written. `## Header shape` below is
why the bytes cannot carry the symbol instead.

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
| `spy_chan.csv` | Chan's `example6_2.xls` | SPY | adjusted | 1993-01-29 .. 2007-12-28 | saved 2008-01-29 |
| `yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv` | yfinance | SPY | adjusted | 1993-01-29 .. 2026-09-18 | 2026-09-18 |
| `yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv` | yfinance | AGG | adjusted | 2003-09-29 .. 2026-09-17 | 2026-09-18 |

The four GLD and GDX files were not all taken on one day. `gld_20yr_prices.csv`
was downloaded on 2026-06-16 and the other three on 2026-08-27, which leaves
GLD's adjusted series covering a different span from its raw twin at both ends.
It starts nineteen months later, in 2006-06 against 2004-11, and stops ten
weeks earlier, in 2026-06 against 2026-08.

Nobody intended that. The sibling repo carried a single comment dating all four
files to 2026-08-27, and this table is what caught it. That is the argument for
recording a download date per file rather than per directory, which is how the
misattribution happened in the first place.

`yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv` is the first
recorded vintage, written by `chan.vintage.record_vintage` rather than placed
by hand, which is why it carries the recorder's five-field name and a single
`Date,Close` header. It is read by
[src/chan/kelly_leverage.py](../src/chan/kelly_leverage.py) for Chan's Example
6.2, and by [src/chan/risk_parity.py](../src/chan/risk_parity.py) as the equity
leg of Qian's allocation. The other SPY file, `spy_chan.csv`, is a workbook
column placed by hand and reading it is
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138).

`yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv` is the second
recorded vintage and the bond leg of that same run. Two things about it are
worth stating rather than leaving a reader to infer from the span.

1. **It ends a day before the SPY file it is read beside.** The download
   returned a non-finite close for 2026-09-18, the day it was taken, and
   `_validated_rows` refuses one of those by name rather than freezing it as a
   price. The row was dropped before the recorder saw it, so the span the entry
   carries is 2003-09-29 to 2026-09-17 and the pair's common history ends
   there.
2. **AGG is what bounds that common history, not SPY.** SPY reaches back to
   1993 and this fund's first bar is 2003-09-29, so the replication that reads
   the pair runs on about two decades rather than three. The instrument was
   committed in writing on
   [issue 15](https://github.com/l3a0/quantitative-trading/issues/15) before
   anything was downloaded, because it is the aggregate bond exposure Qian's
   argument describes, and the span is whatever that choice returned.

**Which "adjusted" it is, stated here because the word names two series.**
yfinance returns a `Close` carrying both splits and dividends under
`auto_adjust=True`, and under `auto_adjust=False` a split-only `Close` beside an
`Adj Close` that carries both. The manifest records all of them as `adjusted`,
which [issue 125](https://github.com/l3a0/quantitative-trading/issues/125) is
about. Both recorded vintages are the both-adjustments series, from

```python
yfinance.download("SPY", period="max", interval="1d", auto_adjust=True, actions=False)
yfinance.download("AGG", period="max", interval="1d", auto_adjust=True, actions=False)
```

run against yfinance 1.7.0 on 2026-09-18, with the `Close` column handed to the
recorder in each case. The distinction is not cosmetic. On Chan's own data the
dividends are worth a quarter of the answer Example 6.2 computes, and
[docs/design.md](../docs/design.md) carries why that decides which basis a
replication reads. It decides even more on the bond leg. An aggregate bond
fund's return is mostly its distributions, so a raw AGG series would strip out
most of what that leg earns and make every return and Sharpe figure computed
from it wrong.

This is the one place that call is written down. The module that reads the
series points here rather than restating it, because a fact in two places is a
fact that can drift.

The `*_chan.csv` files are a different kind of source. Each is the
adjusted-close column of Ernest Chan's own book-companion spreadsheet, taken
from the public mirror at
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading).
The date given is when Chan last saved the workbook, which is the closest thing
these files have to a download date. Which workbook each column came from is
recorded too, in the manifest's `source_workbook` field, because a workbook's
name is not its column's symbol. Chan's `example6_2.xls` holds a SPY column,
and a `SPY.xls` in the same mirror holds a different series.

Four of the five workbooks have their `.xls` checksum recorded in
[src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), beside the
runs that read the columns taken from them. `example6_2.xls` does not, because
no replication here reads `spy_chan.csv` yet.
[Issue 138](https://github.com/l3a0/quantitative-trading/issues/138) is what
adds the run and the checksum together.

## Header shape

The files placed by hand above carry a three-row header before the data. The
shape is yfinance's multi-index frame, and the workbook columns were written
into it too. What that buys, whether or not anybody meant it at the time, is
that the symbol sits in the bytes where a check can read it back, and
`tests/test_vintage.py` now does:

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
ending here, and the check reports no mismatch at all. It reports every vintage
as a file `shasum` cannot open, because the list of filenames was rewritten
along with them. The committed bytes are intact throughout, so every pinned
number is fine.

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
   the series and `saved_date` for the five lifted from Chan's workbooks, whose
   date is when he last saved one rather than when anything was fetched. Those
   lines name their vendor `chan-xls` and carry a `source_workbook` field
   holding the spreadsheet the column was lifted from. The table's
   "Chan's `GLD.xls`" is that pair written as one cell, which is what a single
   column can hold and a filename cannot.

   The workbook is recorded rather than derived from the symbol. Joining the
   two happens to spell every workbook committed so far and spells the wrong
   one for a column whose source is named after a chapter's example rather than
   after a ticker, which is a real file in the same mirror carrying another
   series. The manifest is the authority for a vintage's provenance, so the
   fact sits here and the table repeats it.

   Both surfaces stating the workbook are hand-typed, which the identity pin in
   [tests/support/committed_vintages.py](../tests/support/committed_vintages.py)
   is what answers. An edit moving the manifest and the table together agrees
   with itself, so the check comparing them passes and only the pin fails it.
   The record also refuses a downloaded vintage claiming a workbook, because a
   series a vendor returned did not come out of a spreadsheet.

   Nine of its ten lines were written by hand. Eight were here before the
   recorder existed, and `spy_chan.csv`'s was typed because the recorder cannot
   write a saved date. More will be, for as long as a replication reaches for
   another of Chan's workbook columns.
2. [checksums.sha256](checksums.sha256) is a projection of it, regenerated
   whenever a vintage is recorded, so `shasum` keeps working without a second
   surface anyone has to remember to update.

`TestTheCommittedManifest` in
[tests/test_vintage.py](../tests/test_vintage.py) fails on five states: when an
entry stops describing the file it names, when a file here has no entry, when
the projection stops matching the record, when one of the hand-written entries
above stops carrying the identity it was given, and when a recorded entry stops
agreeing with the name its file took.

The table above is a third telling and is still hand-written. What keeps it
true is another assertion in the same class, which reads both surfaces and
holds every row to the entry for the file it names. Every column is held, and
a cell that stops agreeing fails and says which path, which column, what the
cell says and what the entry gives. So does a row the manifest records nothing
for, and an entry the table has no row for. That last one is what adding a
vintage costs: the suite is red until somebody writes its row, and the failure
is the instruction saying so.
