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

A vintage arrives one of three ways, and which one decides what holds it.
`chan.vintage.record_vintage` writes the file and appends its entry, and
refuses to overwrite either, so recording a series is a recorded act and
replacing one is not an act the recorder performs at all. It does not download.
A caller hands it rows, which is what keeps every rule it enforces testable
with no network.

The second way is by hand, and it did not stop when the recorder arrived. The
recorder takes a download date and builds a name out of it, and a column lifted
from one of Chan's workbooks has no download date to give it, so the recorder
cannot write one. A single such column is typed into the record by hand, and a
whole file of them goes through the third way below. `spy_chan.csv`
is the first to arrive by hand since `chan.vintage` existed, and
[issue 124](https://github.com/l3a0/quantitative-trading/issues/124) is where
that was settled.

The third way is `chan.vintage.record_lifted_columns`, which writes every
column of one of Chan's files at once, each as its own vintage carrying the
date the file was saved. It exists because typing stopped being one line per
column. Chan's first two MATLAB files held 1,100 columns between them, and
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88) is where the
owner decided on 2026-10-02 that entries at that count are written by code.
`python -m chan.mat_columns` reads a `.mat` file and hands its closes over.

A recorded vintage's name is load-bearing. The recorder builds it by joining
the five identity fields, so the vendor, symbol, price basis, span and download
date are recoverable from the path without reading a byte, and
[tests/test_vintage.py](../tests/test_vintage.py) holds every recorded entry to
the name its file took. Renaming such a file fails the suite either way.
Renaming the file alone leaves an entry naming nothing, and renaming the entry
with it makes the fields and the name disagree. The hand-written files above
are exempt, because nothing built their names out of their fields and so
nothing can compare the two, and so are the lifted columns, which take their
source's directory and their symbol rather than the recorder's join. What holds
a hand-written entry instead is the identity pinned for it in
[tests/support/committed_vintages.py](../tests/support/committed_vintages.py),
what holds a lifted column is the pin for its source in the same file, and
both carry their own `Ticker,` header row, which names the series their bytes
carry.

That check is what stands between a recorded entry and a file it does not
describe, and it is worth saying what it does not do. It compares the record
against its own shadow, so it catches an edit to one side and never an entry
that was consistent when it was written. The symbol's case is outside it too,
because the join lowercases it, and what catches a case edit there is
`chan.vintage`'s own refusal of a line whose vendor, symbol or price basis is
not the spelling the recorder would have written. `## Header shape` below is
why the bytes cannot carry the symbol instead.

## What each file is

A vintage is one series as one source held it on one date, identified by
vendor, symbol, span, that date, and which price, rate or event the series carries.
The date is a download date for a series a vendor returned, and a saved date
for a column lifted from one of Chan's own files.

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
| `spy_unadjusted_chan.csv` | Chan's `example6_2.xls` | SPY | raw | 1993-01-29 .. 2007-12-28 | saved 2008-01-29 |
| `yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv` | yfinance | SPY | adjusted | 1993-01-29 .. 2026-09-18 | 2026-09-18 |
| `yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv` | yfinance | AGG | adjusted | 2003-09-29 .. 2026-09-17 | 2026-09-18 |
| `fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv` | fred | TB3MS | rate | 1934-01-01 .. 2026-08-01 | 2026-09-30 |
| `yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv` | yfinance | TLT | raw | 2002-07-30 .. 2026-10-01 | 2026-10-02 |
| `yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv` | yfinance | IEF | raw | 2002-07-30 .. 2026-10-01 | 2026-10-02 |
| `yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv` | yfinance | CADAUD=X | raw | 2005-07-04 .. 2026-09-30 | 2026-10-02 |
| `eia_eer-epmrr-pe1-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv` | eia | EER-EPMRR-PE1-Y35NY-DPG | raw | 2005-10-03 .. 2024-04-05 | 2026-10-02 |
| `eia_eer-epmrr-pe2-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv` | eia | EER-EPMRR-PE2-Y35NY-DPG | raw | 2005-10-03 .. 2024-04-05 | 2026-10-02 |
| `eia_eer-epmrr-pe3-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv` | eia | EER-EPMRR-PE3-Y35NY-DPG | raw | 2005-10-03 .. 2024-04-05 | 2026-10-02 |
| `eia_eer-epmrr-pe4-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv` | eia | EER-EPMRR-PE4-Y35NY-DPG | raw | 2005-10-03 .. 2024-04-05 | 2026-10-02 |
| `eia_eer-epmr-pe1-y35ny-dpg_raw_1985-01-02_2006-12-29_dl2026-10-02.csv` | eia | EER-EPMR-PE1-Y35NY-DPG | raw | 1985-01-02 .. 2006-12-29 | 2026-10-02 |
| `eia_eer-epmr-pe2-y35ny-dpg_raw_1994-01-20_2006-11-29_dl2026-10-02.csv` | eia | EER-EPMR-PE2-Y35NY-DPG | raw | 1994-01-20 .. 2006-11-29 | 2026-10-02 |
| `eia_eer-epmr-pe3-y35ny-dpg_raw_1984-12-03_2006-10-31_dl2026-10-02.csv` | eia | EER-EPMR-PE3-Y35NY-DPG | raw | 1984-12-03 .. 2006-10-31 | 2026-10-02 |
| `eia_eer-epmr-pe4-y35ny-dpg_raw_1994-01-28_2006-09-29_dl2026-10-02.csv` | eia | EER-EPMR-PE4-Y35NY-DPG | raw | 1994-01-28 .. 2006-09-29 | 2026-10-02 |
| `eia_rngc1_raw_1994-01-13_2024-04-05_dl2026-10-02.csv` | eia | RNGC1 | raw | 1994-01-13 .. 2024-04-05 | 2026-10-02 |
| `eia_rngc2_raw_1994-01-12_2024-04-05_dl2026-10-02.csv` | eia | RNGC2 | raw | 1994-01-12 .. 2024-04-05 | 2026-10-02 |
| `eia_rngc3_raw_1994-01-19_2024-04-05_dl2026-10-02.csv` | eia | RNGC3 | raw | 1994-01-19 .. 2024-04-05 | 2026-10-02 |
| `eia_rngc4_raw_1993-12-20_2024-04-05_dl2026-10-02.csv` | eia | RNGC4 | raw | 1993-12-20 .. 2024-04-05 | 2026-10-02 |
| `yfinance_iwb_adjusted_2000-05-19_2026-10-02_dl2026-10-03.csv` | yfinance | IWB | adjusted | 2000-05-19 .. 2026-10-02 | 2026-10-03 |
| `yfinance_iwb_raw_2000-05-19_2026-10-02_dl2026-10-03.csv` | yfinance | IWB | raw | 2000-05-19 .. 2026-10-02 | 2026-10-03 |
| `yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv` | yfinance | SPY | raw | 1993-01-29 .. 2026-10-02 | 2026-10-03 |
| `spx_20071123/` | Chan's `SPX_20071123.mat` | 500 members | adjusted | 1999-11-24 .. 2007-11-23 | saved 2007-11-24 |
| `ijr_20080114/` | Chan's `IJR_20080114.mat` | 600 members | adjusted | 2004-01-15 .. 2008-01-14 | saved 2008-01-15 |
| `inputdataohlcdaily_stocks_20120424/` | Chan's `inputDataOHLCDaily_stocks_20120424.mat` | 497 members | adjusted | 2006-05-11 .. 2012-04-24 | saved 2012-04-25 |
| `earnannfile/` | Chan's `earnannFile.mat` | 497 members | event | 2011-01-03 .. 2012-04-24 | saved 2012-05-15 |

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
leg of Qian's allocation. Two of the other SPY files are workbook columns
placed by hand, and the third is a raw download described below. The Kelly run reads `spy_chan.csv` under `--chan`, and
`tests/test_kelly_leverage.py` reads `spy_unadjusted_chan.csv` to pin what the
price basis is worth on Chan's own data.

`yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv` is recorded the
same way and is the bond leg of that same run. Two things about it are
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

**Which "adjusted" it is.** yfinance hands back two closes a vintage could
record. `Close` under `auto_adjust=True` carries both splits and dividends. It
is `Adj Close` under `auto_adjust=False` renamed, so those two routes give the
same values. `Close` under `auto_adjust=False` carries splits and not
dividends, which is what this repo records as `raw`. What can go wrong is that
split-only `Close` handed to the recorder as `adjusted`, and the recorder cannot
see it happen, because it takes rows rather than the call that produced them.

So every `adjusted` yfinance line in the manifest carries a `vendor_column`
field naming the column and the argument that selected it, and
[tests/test_vintage.py](../tests/test_vintage.py) fails when one does not, or
when it names anything but one of the two spellings of the both-adjustments
close. Each such line reads `Close, auto_adjust=True` today, and two kinds of
evidence stand behind the value.

1. **SPY and AGG carry the call made when they were recorded.** It was

   ```python
   yfinance.download("SPY", period="max", interval="1d", auto_adjust=True, actions=False)
   yfinance.download("AGG", period="max", interval="1d", auto_adjust=True, actions=False)
   ```

   run against yfinance 1.7.0 on 2026-09-18, with the `Close` column handed to
   the recorder in each case. The field holds the column and its argument, and
   this paragraph holds the rest of the call. IWB's line carries its call the
   same way, written in its own paragraph below, and it is the one line with
   both kinds of evidence, because a raw twin from the same session checks it.
2. **GLD and GDX carry an inference that their bytes bound.** Nobody wrote
   their calls down. A comparison against the raw twin beside each, which
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) pins, says what
   the bytes can. GDX's adjusted file sits below its raw twin on every shared
   day before 2025-12-22 and equals it from that day on, which is where the
   last dividend in the file goes ex. That is the shape a close carrying the
   dividends takes, so the file is the both-adjustments close. GLD's equals its
   raw twin on every shared day, because GLD pays no distributions and has not
   split, so its bytes cannot tell any column apart and the route cannot move a
   number read from it. Which of the two spellings each call took is not in
   the bytes. `Close, auto_adjust=True` is the likely one, because the sibling
   repository's `pipeline/download_prices.py` at `477c594` calls
   `yfinance.download` without `auto_adjust`, whose default is `True`, and that
   script's naming matches these files. That is an inference from a filename
   rather than a record.

The distinction is not cosmetic. On Chan's own data the dividends are worth a
quarter of the answer Example 6.2 computes, and
[docs/design.md](../docs/design.md) carries why that decides which basis a
replication reads. It decides even more on the bond leg. An aggregate bond
fund's return is mostly its distributions, so a raw AGG series would strip out
most of what that leg earns and make every return and Sharpe figure computed
from it wrong.

[src/chan/kelly_leverage.py](../src/chan/kelly_leverage.py), which reads the
SPY download, points at the manifest line and at this paragraph rather than
restating either, because a fact in two places is a fact that can drift.

`fred_tb3ms_rate_1934-01-01_2026-08-01_dl2026-09-30.csv` is the first vintage
that is not a price. It is the St. Louis Fed's three-month Treasury-bill rate,
series TB3MS, in percent a year, one row per month dated the first of the
month. The values are FRED's, written through `record_vintage`. So the header
is `Date,Close` rather than FRED's own, and each value is written as a float,
which drops a trailing zero: FRED's 0.20 is stored as 0.2.

It is recorded under the `rate` basis rather than `raw`, because the
scale-break guard reads every `raw` series as a price. The **rate** entry in
the [design doc's vocabulary](../docs/design.md#vocabulary) says why a rate
cannot be read that way, and
[tests/test_scale_breaks.py](../tests/test_scale_breaks.py) measures it where
it skips the series. [src/chan/bill_rates.py](../src/chan/bill_rates.py) reads
it, and the risk parity post's bill-rate averages trace to
[tests/test_bill_rates.py](../tests/test_bill_rates.py).
[Issue 187](https://github.com/l3a0/quantitative-trading/issues/187) is where
storing it was decided.

`yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv` and
`yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv` are the two legs of
Chan's fixed-income candidate, which
[src/chan/stationary_candidates.py](../src/chan/stationary_candidates.py)
reads. TLT holds Treasuries maturing in twenty years or more and IEF holds
Treasuries maturing in seven to ten, and
[issue 136](https://github.com/l3a0/quantitative-trading/issues/136) is where
both were named before anything was downloaded. Three things about them are
worth stating rather than leaving a reader to infer.

1. **They are the raw basis, and this is the call that produced it.** Raw here
   means adjusted for splits and not for dividends, which on yfinance is the
   `Close` column when `auto_adjust` is off, not that call's `Adj Close`.

   ```python
   yfinance.download("TLT", period="max", interval="1d", auto_adjust=False, actions=False)
   yfinance.download("IEF", period="max", interval="1d", auto_adjust=False, actions=False)
   ```

   Both ran against yfinance 1.7.0 on 2026-10-02, outside the package, with
   the `Close` column handed to the recorder. The two columns differed on every
   day but the last, so the column recorded is not the adjusted one. That check
   ran at download time against a column this repo does not commit, so nothing
   here can run it again.
2. **Nothing was dropped.** The rule settled on the issue before the download
   was to drop a non-finite close on the download date itself and stop on any
   other. The download ran after the 2026-10-01 close and returned no
   non-finite close on either leg, so the rule removed nothing and each file
   holds all 6,083 rows the vendor returned.
3. **The two spans are the same.** The yfinance history of both begins on
   2002-07-30, so the pair's common history is each leg's whole history, and
   `scale_breaks` finds nothing on either.

`yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv` is the
Canadian dollar priced in Australian dollars, the cross rate Chan calls "quite
stationary" at Kindle location 3951.
[src/chan/stationary_candidates.py](../src/chan/stationary_candidates.py)
reads it, and
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) is where
the symbol, the rows and the span were settled before anything was recorded.
It is the first committed symbol carrying `=`, which `SYMBOL_PATTERN` admits
for currency pairs. Four things about it are worth stating rather than leaving
a reader to infer.

1. **It is a raw rate, and this is the call that produced it.**

   ```python
   yfinance.download("CADAUD=X", period="max", interval="1d", auto_adjust=False, actions=False)
   ```

   It ran against yfinance 1.7.0 on 2026-10-02, outside the package, with the
   `Close` column handed to the recorder and each date taken from the index as
   returned. A currency has no splits or dividends to adjust for, and on this
   series a read-only probe the same day found `Adj Close` equal to `Close` on
   every row, and the same `Close` under either `auto_adjust`. It is recorded under `raw` rather than `rate`, because
   `close_identity` reaches `raw` through `unadjusted=True` and the scale-break
   guard reads it as the price it is. The issue carries the full argument.
2. **Two rows were dropped, by date.** The vendor dates an FX bar on the London
   calendar and returns the download day's bar as a live, finite quote, which
   the recorder's refusal of a non-finite close cannot catch. So the rule fixed
   on the issue drops every row dated on or after the day before the download
   date. The download returned 5,440 rows ending 2026-10-02, the rule dropped
   2026-10-01 and 2026-10-02, and the file holds the other 5,438. No other
   close was non-finite.
3. **Nothing else was edited.** The vendor's own gaps stay, so does every
   repeated or stale quote, and no day was filled. The largest gap runs from
   2007-04-02 to 2007-08-03, 90 weekdays with no row. The test reads from
   2007-08-06 so no regression spans it, and
   [tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py)
   pins the gap so the reason for that start cannot quietly stop being true.
4. **`scale_breaks` finds nothing on it.** Its largest day-over-day move is a
   small fraction of the bound, so a flagged day would be a bad print.

The twelve `eia_` files are NYMEX futures settlement prices as the US Energy
Information Administration publishes them, contracts 1 to 4 of three products.
They are what [issue 19](https://github.com/l3a0/quantitative-trading/issues/19)
needs to check Chan's two commodity seasonals, gasoline in April and natural gas
from February to April, and the owner decided on 2026-10-02 that they may be
committed. Five things about them are worth stating rather than leaving a reader
to infer.

1. **Each file is a chain of contracts.** Contract 1 is whichever contract
   expires next, so on an expiry day a file's next close belongs to a different
   contract, and the day-over-day ratio across it compares two instruments. The
   issue says how a run maps a contract number back to a named contract.
2. **The symbol names the product.**
   - `EER-EPMR-PE1-Y35NY-DPG` to `PE4` are New York Harbor regular gasoline,
     the contract RBOB replaced, in dollars a gallon.
   - `EER-EPMRR-PE1-Y35NY-DPG` to `PE4` are RBOB gasoline, in dollars a gallon.
   - `RNGC1` to `RNGC4` are Henry Hub natural gas, in dollars per million Btu.

   Each symbol is EIA's own series id with every underscore written as a
   hyphen, because a recorded vintage's name joins its identity fields with
   underscores and so no field may hold one. The natural gas ids carry none and
   are unchanged.
3. **This is how they were fetched.** Each came on 2026-10-02 from EIA's daily
   workbook, `https://www.eia.gov/dnav/pet/hist_xls/<id>d.xls` for gasoline and
   `https://www.eia.gov/dnav/ng/hist_xls/<id>d.xls` for natural gas, read
   outside the package. The script read the sheet `Data 1` with `xlrd`, took
   each date from its Excel serial, and handed each settlement to the recorder
   as stored. Every row was kept, because no settlement was blank or non-finite
   and no date repeated. EIA prints a settlement to three decimal places. For
   natural gas that matches the exchange's settlement tick today, and for RBOB
   it is ten times coarser than today's tick of $0.0001 a gallon. The recorder
   writes each value as a float, which drops a trailing zero, so EIA's 0.510 is
   stored as 0.51.
4. **No row after 2024-04-05 will arrive from this source.** Each RBOB and
   natural gas workbook names 2024-04-05 as its latest data, and EIA's pages
   have added no row since. The four New York Harbor files end in 2006, between
   2006-09-29 and 2006-12-29, because RBOB replaced that contract. Years after
   2024 need another vendor, which the issue names.
5. **Nothing was filled here, and EIA filled some days itself.** Contracts of
   one product do not hold the same days. RBOB's four files span the same
   2005-10-03 to 2024-04-05 and hold 4,609, 4,618, 4,625 and 4,623 rows, so a
   run pairing two contracts reads only the days both hold. The New York Harbor
   contract-1 file misses trading days too, among them 1997-04-14, which leaves
   three of the gasoline seasonal's years unreadable. The natural gas
   files go the other way on exchange holidays. They carry rows such as
   2018-01-01, 2018-03-30 and 2018-12-25 that repeat the day before's
   settlement exactly, and the files keep them, so a return across one of those
   days reads as zero. `scale_breaks` finds nothing on any of the twelve,
   though they widened the range of ordinary daily moves the bound was fitted
   to, which [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) pins.

`yfinance_iwb_adjusted_2000-05-19_2026-10-02_dl2026-10-03.csv` and
`yfinance_iwb_raw_2000-05-19_2026-10-02_dl2026-10-03.csv` are IWB, the fund
that tracks the Russell 1000. That is the equity index Qian's paper reads,
where SPY, the equity leg of the risk parity run, tracks the S&P 500.
[Issue 160](https://github.com/l3a0/quantitative-trading/issues/160) runs IWB
beside SPY on the same window and the same AGG vintage, so that whatever moves
is the instrument. Three things about the pair are worth stating rather than
leaving a reader to infer.

1. **Both came from one session, and these are the calls.**

   ```python
   yfinance.download("IWB", period="max", interval="1d", auto_adjust=True, actions=False)
   yfinance.download("IWB", period="max", interval="1d", auto_adjust=False, actions=False)
   ```

   Both ran against yfinance 1.7.0 on 2026-10-03, after the 2026-10-02 close,
   outside the package. The first call's `Close` is the adjusted file, and its
   manifest line carries `vendor_column` as `Close, auto_adjust=True`. The
   second call's `Close` is the raw file, which carries splits and not
   dividends. The second call's `Adj Close` matched the first call's `Close` on
   every row to within 0.00013, which is the claim above that the two routes
   give the same values, checked at download time against a column this repo does not commit.
2. **Nothing was dropped.** The download ran on a Saturday and returned no
   non-finite close on either call, so each file holds all 6,632 rows the
   vendor returned.
3. **The raw twin is what makes the adjusted label checkable.** A split-only
   `Close` recorded as `adjusted` would strip the dividends from IWB, and the
   risk parity run would report them as what the SPY proxy cost.
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) pins the shape a
   close carrying the dividends takes against its twin, the form GDX's
   comparison above takes. The adjusted file sits below the raw one on every day
   before 2026-09-15 and equals it from then on.

`yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv` is SPY's raw close,
recorded to check the design doc's claim that a raw price is the same in every
vintage. It is set against `spy_unadjusted_chan.csv`, Chan's as-traded close,
on the 3,758 days the two share, and
[tests/test_vintage_overlap.py](../tests/test_vintage_overlap.py) pins what
that comparison finds.
[Issue 139](https://github.com/l3a0/quantitative-trading/issues/139) asked for
it. Three things about it are worth stating rather than leaving a reader to
infer.

1. **This is the call.**

   ```python
   yfinance.download("SPY", period="max", interval="1d", auto_adjust=False, actions=False)
   ```

   It ran against yfinance 1.7.0 on 2026-10-03, after the 2026-10-02 close,
   outside the package. Its `Close` is the file, which carries splits and not
   dividends. SPY has never split, so here that is the as-traded close. The
   call returned no non-finite close, so the file holds all 8,477 rows the
   vendor returned. Its `Adj Close` is not committed, because a second
   yfinance `adjusted` SPY entry would be a second download of one committed
   series, which
   [issue 83](https://github.com/l3a0/quantitative-trading/issues/83) is about.
2. **It is not a second download of anything committed.** No yfinance `raw`
   SPY entry existed before it, so the reader's arguments still name one entry
   each, and no case needs a date to read it.
3. **It departs from Chan's file on two days.** On 2006-08-07 Chan's file
   reads 127.95 and this one 127.90, and on 2007-05-21 they read 152.61 and
   152.54. Neither is a split, a dividend or the rounding of a price quoted in
   eighths, which accounts for every other difference. On 2006-08-07 the same
   call returned an `Open` equal to that `Close` to the cent, a column this
   repo does not commit. That is the shape of a close filled from the open,
   and it says nothing about which vendor holds the right number. No third
   source was available to settle either day.

The `*_chan.csv` files are a different kind of source. Each is one price
column of Ernest Chan's own book-companion spreadsheet, taken from the public
mirror at
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading).
The date given is when Chan last saved the workbook, which is the closest thing
these files have to a download date. Which workbook each column came from is
recorded too, in the manifest's `source_workbook` field, because a workbook's
name is not its column's symbol. Chan's `example6_2.xls` holds SPY's columns,
and a `SPY.xls` in the same mirror holds a different series.

Every one of them is the adjusted close except `spy_unadjusted_chan.csv`. That
file is the `Close` column of the same `example6_2.xls` that gives
`spy_chan.csv` its `Adj Close`, so the two share a workbook, a saved date and a
calendar, and differ only in basis. Its basis is `raw` because the column is
the as-traded close. SPY has not split, so the column carries no split for a
vendor to have adjusted away, and `scale_breaks` finds nothing on it.
[Issue 192](https://github.com/l3a0/quantitative-trading/issues/192) committed
it to pin Chan's Kelly leverage on the as-traded close, which is the figure
that shows the price basis deciding his Black Monday conclusion.

Every workbook has its `.xls` checksum recorded beside the run that reads a
column taken from it. The checksums of `GLD.xls`, `GDX.xls`, `KO.xls` and
`PEP.xls` are in
[src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), and that
of `example6_2.xls` is in
[src/chan/kelly_leverage.py](../src/chan/kelly_leverage.py).

The first two directories hold Chan's first-edition MATLAB files, one vintage per
stock, each carrying that stock's close, high, low, open and volume. `spx_20071123/` is the S&P 500 as it stood on 2007-11-23,
which his Examples 3.7 and 7.7 read, and `ijr_20080114/` is the S&P 600 as it
stood on 2008-01-14.
[src/chan/khandani_lo.py](../src/chan/khandani_lo.py) reads the first's
closes for Example 3.7 and its opens for Example 3.8. His Example 7.6 loads `IJR_20080131`, which the mirror
does not hold, and its third printed return is the trade into January 2008,
whose month end this file stops short of. So this file can give Example 7.6's
first two returns and not its third.
[`chan.equity_seasonals`](../src/chan/equity_seasonals.py) reads both
directories, and
[issue 225](https://github.com/l3a0/quantitative-trading/issues/225) is where
the third gets computed. Each holds only the companies
still in its index on that day, carried backwards, so a figure computed from
either is a figure about survivors.
[Issue 88](https://github.com/l3a0/quantitative-trading/issues/88) carries the
measurements below and the decision behind the shape.

1. **Where they came from.** The same mirror, at commit
   [`1a71950`](https://github.com/egorpe/EPChan-QuantitativeTrading/tree/1a7195003cf3e85a806e18867e0af547d17ad5c4),
   which ships each as a `.zip`. The `.mat` files inside are not committed, and
   their sha256 is recorded here instead, the way the workbooks' is recorded
   beside the runs that read them. Summed from the sizes git records for each
   file, the two directories held 71.9 MB of the 74.3 MB `data/` held when
   they were committed, where it held 2.0 MB before them. A filesystem's block size makes `du`
   report more, by an amount that differs between machines. The budget
   proposed on
   [issue 88](https://github.com/l3a0/quantitative-trading/issues/88) is that
   `data/` stays under 100 MB of file content, and a later panel states its own size
   against that in its issue before it is recorded. Point 5 of the book-two
   list below raises it.

   ```text
   8d3ccbbd2c95b1ea342dfd5f953075f24c0df561efc9c6cc2cce651294ee73dc  SPX_20071123.mat
   a30f6560988b7d0774d0258569ef2c4ef8d6a416e94c64da48a9cec9e8c76d28  IJR_20080114.mat
   ```

2. **Every field is kept, in one file per stock.** Each file carries five
   date-by-stock arrays: `cl`, `hi`, `lo`, `op` and `vol`. Every figure Chan's
   code prints from them reads `cl`, and the other four exist only in the
   mirror, which this repo does not control, so the owner decided on
   2026-10-02 to commit all five rather than leave four to a mirror that can
   disappear. They
   share one file because they are one stock saved once. An open series
   written as a vintage of its own would share vendor, symbol, basis and date
   with the close, and nothing in an entry's identity could tell the two apart.
   The columns run `Close,High,Low,Open,Volume`, yfinance's default order, which
   keeps the close second, where every reader here takes it. A volume is
   written as the whole number it is, and the `adjusted` basis names the four
   prices rather than the volume.
   [Issue 206](https://github.com/l3a0/quantitative-trading/issues/206) is the
   first step that reads the opens, for Example 3.8 in `chan.khandani_lo`.
   Chan's Python notebook for that example reads `SPX_op_20071123.txt`, and its
   twin for Example 3.7 reads `SPX_20071123.txt`. Neither is committed. Both
   are reposted at Delta-Pion/Financial-Prediction-Research-RM `d47c2e1`, and
   measured on that issue at `7150afb` each matches its panel cell for cell, NaN for NaN, to
   a largest relative difference of 2.0e-16, so they are the same series as
   the file recorded here and not a second vintage of it.
3. **A day without a price is a missing row.** Chan marks a day a stock has no
   price with NaN in all five arrays at once, and a vintage refuses one, so
   each file holds only the days its stock was priced. Nothing is lost. No trading day in either file lacks a
   close in every column, so `chan.series.load_panel` rebuilds each of Chan's
   arrays by putting every member on the union of their dates, and the
   conversion checked all five, NaN for NaN, before anything was committed. Compute
   returns on that panel rather than on one file's own rows. `spx_20071123/wyn.csv`
   holds two companies under one symbol, 952 trading days apart, closing at
   0.26 and then at 31.85 on 2006-08-01, and `spx_20071123/dfs.csv` does the
   same across 400 days to 2007-07-02.
4. **The date is the save.** It comes from each file's MAT header, which
   records when the file was created. That is a day after the date in each
   name, because the name carries the last trading day.
5. **Both are recorded as `adjusted`, and neither says how.** The S&P 500 file
   is split-adjusted, as AAPL across its 2005-02-28 split shows, and its KO
   column sits below KO's raw close by amounts that do not reconcile with
   dividends alone, measured in
   [the survivorship comment on issue 88](https://github.com/l3a0/quantitative-trading/issues/88#issuecomment-5945872363). The S&P 600
   file was measured for this commit, on the ratio of each open to the close
   before it. Across 589,021 consecutive pairs, one sits within 0.01 of a
   two-for-one split, CBU on 2004-04-13, against none of 961,582 in the S&P 500
   file. Four sit within 0.01 of a three-for-two split, against ten in the S&P
   500 file, which is split-adjusted, so a ratio near two thirds is not on its
   own a sign of an unadjusted split.
   Six hundred unadjusted small caps over four years would be expected to show
   far more than one two-for-one gap, which is an expectation rather than a
   measurement. So the file is recorded as split-adjusted, and CBU's day is a
   likely exception nobody here has verified.
6. **The scale-break guard flags 62 days in 52 of the 1,100, on the close.** They are pinned
   by path and day in [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
   A flag is a day's close below 0.625 or above 1.6 times the one before. Most
   are real moves, such as AAPL falling to 0.4813 of its close on 2000-09-29,
   its profit-warning day, in a column that absorbs its June 2000 split with
   no jump. Two are the splices in point 3. Four more sit within 0.02 of a
   two-for-one split, and whether any of them is an unadjusted split is not
   known.

   1. AES on 2001-09-26, in the S&P 500 file.
   2. AYE on 2002-10-08, in the S&P 500 file.
   3. CBU on 2004-04-13, in the S&P 600 file.
   4. INSP on 2008-01-09, in the S&P 600 file.

The other two directories hold the two files of Chan's second book, *Algorithmic
Trading*, that his Example 7.2 reads.
[Issue 20](https://github.com/l3a0/quantitative-trading/issues/20) reproduces
that example. `inputdataohlcdaily_stocks_20120424/` is the S&P 500 as Chan held
it on 2012-04-24, with the same five fields per stock as the first two
directories. `earnannfile/` holds his earnings-announcement flags for the same
497 stocks, a 0 or 1 for each trading day. Like the first two, the price file
holds only the companies still in the index on its date, so a figure computed
from it is a figure about survivors.
[Issue 250](https://github.com/l3a0/quantitative-trading/issues/250) carries the
measurements below.

1. **Where they came from.** Two public mirrors of Chan's book-two code hold
   both files with identical git blob hashes:
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview)
   at `e4bc46f`, under `public/img/book2/`, and
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
   at `4567024`, under `archived/matlab/`. Neither carries a licence, which
   README's licence paragraph already covers. The `.mat` files are not
   committed, and their sha256 is recorded here.

   ```text
   4a62f5851de9962b72c6b135d4f4addc3cb13ff1ce28afe45defceb47c318849  inputDataOHLCDaily_stocks_20120424.mat
   16cfebaa1ee0eecd606543ee0c18ebbd8b85c7e48fe7fbd26ede36242ab27679  earnannFile.mat
   ```

2. **The prices are recorded as `adjusted`, for splits at least.** Across
   734,022 ratios of an open to the close before it, none sits within 0.01 of
   a two-for-one or a three-for-two split. NVDA's three-for-two split on
   2007-09-11 and CMI's two-for-one on 2008-01-02 both pass with no jump.
   Whether the file is adjusted for dividends was not measured.
3. **The flags are a basis of their own, kept for every day.** A flag is not a
   price, so its vintages carry the `event` basis and one field, `Flag`, written
   as the whole number it is. Each stock keeps all 330 days from 2011-01-03 to
   2012-04-24, zeros included, rather than only its announcements. Chan's code
   cuts its prices to the flag file's own days before taking a return, and the
   first flag falls on 2011-01-05. A file of announcements alone would start
   two days late, which moves the reproduction off every figure Chan printed.
   `chan.mat_columns.flag_round_trip_differs` rebuilt the 330 by 497 array from
   the committed bytes and found it identical, day for day.
4. **The scale-break guard flags 30 days in 17 of the 497, on the close.** Every
   one falls between 2007 and 2009, most are banks and insurers in the 2008
   crisis, such as AIG on 2008-09-15, and none sits near a split. None falls in
   the 2011 and 2012 window Example 7.2 trades. They are pinned beside the
   others in [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
5. **The size budget is raised.** The two directories hold 32.01 MB, which
   takes `data/` from 74.41 MB to 106.86 MB of file content. The owner decided
   on 2026-10-03 to commit the whole price file rather than stay under the
   100 MB budget, because the mirrors are the only free copies, and raised the
   budget so that `data/` stays under 150 MB of file content. A later panel
   still states its own size against that in its issue before it is recorded.

## Header shape

The files placed by hand above carry a three-row header before the data. The
shape is yfinance's multi-index frame, and the workbook columns were written
into it too, as is every stock `record_lifted_columns` writes. A stock lifted
with all five fields widens it to one cell per field, so its first two rows
read `Price,Close,High,Low,Open,Volume` and `Ticker,KO,KO,KO,KO,KO`. What that buys, whether or not anybody meant it at the time, is
that the symbol sits in the bytes where a check can read it back, and
`tests/test_vintage.py` now does:

```text
Price,Close
Ticker,GLD
Date,
2004-11-18,44.380001068115234
```

A vintage `record_vintage` writes carries one header row, `Date,Close`, and
nothing else.
In a `rate` vintage the `Close` column holds the rate, because the recorder
writes one header for every series it records.
Two shapes rather than one is deliberate. The three rows above are an artifact
of one vendor's frame, and writing `Price,Close` at the top of a series some
other vendor returned would be a claim the file has no business making. The
columns lifted from Chan's own files take the three-row shape anyway, the
workbook columns since before the recorder existed and the MATLAB columns
because they are held by the same check: the `Ticker,` row is what names the
series in the bytes, and none of them came from the recorder.

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
   the series and `saved_date` for a series lifted from one of Chan's own
   files, whose date is when he last saved that file rather than when anything
   was fetched. Those lines name their vendor `chan-xls` for a workbook column
   and `chan-mat` for a stock from one of his MATLAB files, and carry a
   `source_workbook` field holding the file the series was lifted from. The
   table's "Chan's `GLD.xls`" is that pair written as one cell, which is what
   a single column can hold and a filename cannot. An `adjusted` yfinance line
   carries a `vendor_column` field instead, naming the column of yfinance's
   response its series is, for the reason given above beside the SPY and AGG
   calls.

   The workbook is recorded rather than derived from the symbol. Joining the
   two spells the right workbook for every committed column but the two SPY
   ones, `spy_chan.csv` and `spy_unadjusted_chan.csv`, whose source,
   `example6_2.xls`, is named after a chapter's example rather than after a
   ticker. The `SPY.xls` the join would give is a real file in the
   same mirror carrying another series. The manifest is the authority for a vintage's provenance, so the
   fact sits here and the table repeats it.

   Both surfaces stating the workbook are hand-typed, which the identity pin in
   [tests/support/committed_vintages.py](../tests/support/committed_vintages.py)
   is what answers. An edit moving the manifest and the table together agrees
   with itself, so the check comparing them passes and only the pin fails it.
   The record also refuses a downloaded vintage claiming a workbook, because a
   series a vendor returned did not come out of a spreadsheet.

   Its hand-written lines are the eight that were here before the recorder
   existed and the two SPY workbook columns', `spy_chan.csv`'s and
   `spy_unadjusted_chan.csv`'s, which were typed because the recorder cannot
   write a saved date. Every other line was written by code, a download by
   `record_vintage` and a stock lifted from Chan's MATLAB files by
   `record_lifted_columns`. More lines will be typed by hand for as long as a
   replication reaches for another of Chan's workbook columns.

   An earlier version of this paragraph counted every line in the manifest,
   and each change that recorded a vintage made it false again.
   [Issue 132](https://github.com/l3a0/quantitative-trading/issues/132), the
   sweep of prose that counts the committed vintages, is why it names the
   hand-written lines instead. Only a hand-typed workbook column changes that
   set, and that is the change that would also write the line.
2. [checksums.sha256](checksums.sha256) is a projection of it, regenerated
   whenever a vintage is recorded, so `shasum` keeps working without a second
   surface anyone has to remember to update.

`TestTheCommittedManifest` in
[tests/test_vintage.py](../tests/test_vintage.py) fails when any of these stops
holding. The class is the authority for the list, which grows whenever it gains
a test, so no total is given here.

- Every entry describes the file it names, by its sha256, its row count and
  its span.
- Every CSV file here has exactly one entry, at any depth.
- `checksums.sha256` is the projection the manifest produces, and regenerating
  it changes nothing.
- Every hand-written entry, and every stock lifted from Chan's MATLAB files,
  names the series its file's `Ticker,` row carries.
- The hand-written entries and the lifted sources carry the identity
  `tests/support/committed_vintages.py` pins for them, and each lifted source
  holds the number of members its pin gives, each at the path its directory
  and symbol make.
- Every recorded entry agrees with the name its file took.
- Every manifest line is the text its own entry would write.
- Neither the manifest nor the projection carries a carriage return.
- The table above states what the manifest states.
- Every entry carries exactly one kind of date, and it is a saved date if and
  only if the series was lifted from one of Chan's own files.
- An entry names a source workbook if and only if its series was lifted from
  one of Chan's files, and a download claiming one is refused when the
  manifest is read.

The table above is a third telling and is still hand-written. What keeps it
true is the table assertion in that list, which reads both surfaces and
holds every row to the entry for the file it names. Every column is held, and
a cell that stops agreeing fails and says which path, which column, what the
cell says and what the entry gives. So does a row the manifest records nothing
for, and an entry the table has no row for. That last one is what adding a
vintage costs: the suite is red until somebody writes its row, and the failure
is the instruction saying so.

A directory gets one row rather than one per file, so the 2,094 lifted columns
are four rows. The row states what every file in it shares, which is the
vendor, the basis and the date, along with how many members it holds and the
earliest and latest day any of them carries. Its members must agree on the
three shared cells, or the failure names the directory and the values. What
holds each member's own identity is the pin for its source in
[tests/support/committed_vintages.py](../tests/support/committed_vintages.py),
which also counts the members.
