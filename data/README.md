# Committed vintages

The price series every run here reads, except the ones
`## Vintages kept in the owner's archive` describes, committed because the
numbers the suite pins were computed from these exact bytes. A vendor restates an adjusted series
without announcing it, so a result checked against a fresh download is a result
checked against different data. [docs/design.md](../docs/design.md) carries the
reasoning.

Nothing regenerates these files. No fetch script was ported, and a re-download
would move the pinned numbers and fail the suite, which is the behaviour that
makes the pins worth having. Replacing a file is therefore a deliberate act
with a visible cost, not a refresh.

A vintage in this directory arrives one of three ways, and which one decides
what holds it. The two kept in the owner's archive are typed into their own
record instead, which their section below describes.
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
that was settled. The seven files of Chan's 2018 Python port arrived by hand
too, because they are committed as his zip shipped them and neither writer
produces that shape.

The third way is `chan.vintage.record_lifted_columns`, which writes every
column of one of Chan's files at once, each as its own vintage carrying the
date the file was saved. It exists because typing stopped being one line per
column. Chan's first two MATLAB files held 1,100 columns between them, and
[issue 88](https://github.com/l3a0/quantitative-trading/issues/88) is where the
owner decided on 2026-10-02 that entries at that count are written by code.
`python -m chan.mat_columns` reads a `.mat` file, or one of Chan's CSV files with the
`--saved-date` it cannot carry, and hands its fields over.

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
carry. A file of Chan's Python port carries no such row, so its pin there
checks its symbol against the file name the zip gave it.

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
vendor, symbol, span, that date, and which price, rate, event or return the series
carries.
The date is a download date for a series a vendor returned, and a saved date
for a series lifted from one of Chan's own files.

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
| `ijr_20080131/` | Chan's `IJR_20080131.mat` | 600 members | adjusted | 2004-01-15 .. 2008-02-01 | saved 2008-02-02 |
| `inputdataohlcdaily_stocks_20120424/` | Chan's `inputDataOHLCDaily_stocks_20120424.mat` | 497 members | adjusted | 2006-05-11 .. 2012-04-24 | saved 2012-04-25 |
| `earnannfile/` | Chan's `earnannFile.mat` | 497 members | event | 2011-01-03 .. 2012-04-24 | saved 2012-05-15 |
| `inputdatadaily_br_20120813/` | Chan's `inputDataDaily_BR_20120813.mat` | 322 members | raw | 1995-11-01 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_c2_20120813/` | Chan's `inputDataDaily_C2_20120813.mat` | 31 members | raw | 1986-11-03 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_cl_20120813/` | Chan's `inputDataDaily_CL_20120813.mat` | 90 members | raw | 1986-11-03 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_hg_20120813/` | Chan's `inputDataDaily_HG_20120813.mat` | 182 members | raw | 1986-11-03 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_ho2_20120813/` | Chan's `inputDataDaily_HO2_20120813.mat` | 351 members | raw | 1986-11-03 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_tu_20120813/` | Chan's `inputDataDaily_TU_20120813.mat` | 94 members | raw | 1990-06-22 .. 2012-08-13 | saved 2012-08-14 |
| `inputdatadaily_cl_20120502/` | Chan's `inputDataDaily_CL_20120502.mat` | 89 members | raw | 2000-11-20 .. 2012-05-02 | saved 2012-05-03 |
| `inputdatadaily_vx_20120507/` | Chan's `inputDataDaily_VX_20120507.mat` | 72 members | raw | 2006-03-23 .. 2012-05-07 | saved 2012-05-08 |
| `inputdata_gc_1600_20100802/` | Chan's `inputData_GC_1600_20100802.mat` | 1 member | raw | 2007-08-03 .. 2010-08-02 | saved 2012-05-07 |
| `inputdata_etf/` | Chan's `inputData_ETF.mat` | 67 members | adjusted | 2006-04-26 .. 2012-04-09 | saved 2012-04-10 |
| `pythoncodesanddata/inputData_USDCAD.csv` | Chan's `PythonCodesAndData.zip` | USDCAD | raw | 2007-07-22 .. 2012-03-28 | saved 2018-10-13 |
| `pythoncodesanddata/inputData_USDCAD_20120426.csv` | Chan's `PythonCodesAndData.zip` | USDCAD | raw | 2009-01-02 .. 2012-04-26 | saved 2018-12-12 |
| `pythoncodesanddata/inputData_AUDUSD_20120426.csv` | Chan's `PythonCodesAndData.zip` | AUDUSD | raw | 2009-01-02 .. 2012-04-26 | saved 2018-12-12 |
| `pythoncodesanddata/inputData_AUDCAD_20120426.csv` | Chan's `PythonCodesAndData.zip` | AUDCAD | raw | 2007-07-23 .. 2012-04-26 | saved 2018-12-13 |
| `pythoncodesanddata/AUD_interestRate.csv` | Chan's `PythonCodesAndData.zip` | AUDRATE | rate | 2000-01-01 .. 2012-03-01 | saved 2018-12-13 |
| `pythoncodesanddata/CAD_interestRate.csv` | Chan's `PythonCodesAndData.zip` | CADRATE | rate | 2000-01-01 .. 2011-12-01 | saved 2018-12-13 |
| `pythoncodesanddata/AUDCAD_unequal_ret.csv` | Chan's `PythonCodesAndData.zip` | AUDCAD-UNEQUAL | return | 2009-12-18 .. 2012-04-26 | saved 2018-12-26 |
| `inputdataohlcdaily_20120504/` | Chan's `inputDataOHLCDaily_20120504.mat` | 51 members | adjusted | 2008-04-02 .. 2012-05-04 | saved 2012-05-07 |
| `inputdataohlcdaily_20120507/` | Chan's `inputDataOHLCDaily_20120507.mat` | 53 members | adjusted | 1995-10-20 .. 2012-05-08 | saved 2012-05-09 |
| `inputdataohlcdaily_20120511/` | Chan's `inputDataOHLCDaily_20120511.mat` | 52 members | adjusted | 1995-10-20 .. 2012-05-11 | saved 2012-05-12 |
| `inputdataohlcdaily_20120517/` | Chan's `inputDataOHLCDaily_20120517.mat` | 52 members | adjusted | 1995-10-20 .. 2012-05-17 | saved 2012-05-18 |
| `vix/` | Chan's `VIX.csv` | 1 member | raw | 1990-01-02 .. 2012-05-08 | saved 2012-05-09 |

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
leg of Qian's allocation. Two of the other SPY files are workbook
columns placed by hand, and the third is a raw download described below.
The Kelly run reads `spy_chan.csv` under `--chan`,
[src/chan/momentum_factor.py](../src/chan/momentum_factor.py) reads it as the
market factor of
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22), and
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
committed. [Issue 137](https://github.com/l3a0/quantitative-trading/issues/137)
reads the eight natural gas and RBOB files again, to test Chan's calendar
spreads. Five things about them are worth stating rather than leaving a reader
to infer.

1. **Each file is a chain of contracts.** Contract 1 is whichever contract
   expires next, so on an expiry day a file's next close belongs to a different
   contract, and the day-over-day ratio across it compares two instruments.
   [src/chan/futures.py](../src/chan/futures.py) holds the expiry rules that
   map a contract number back to a named contract, and its docstring says how
   they were checked against the files.
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
   outside the package, and `chan.vintage.record_vintage` wrote what it
   returned. Its `Close` is the file, which carries splits and not
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
whose month end the second file stops short of. `ijr_20080131/`, described
after this list, is that later save.
[`chan.equity_seasonals`](../src/chan/equity_seasonals.py) reads the first
directory for Example 7.7 and `ijr_20080131/` for Example 7.6.
[`chan.pca_factor`](../src/chan/pca_factor.py) reads the
second's closes for Example 7.4. The revised edition's Python for that example
reads `IJR_20080114.txt` instead, reposted at
pinhaocheng/epchan-quant_trading_Python_codes `5fcab61` and at
liujiantong/epchan_books `653cf92` as one git blob. Measured on
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21) at `3bb9cce`,
it holds the same 1,006 days, the same 600 symbols in the same order and the
same NaN cells as this directory's closes, and every value agrees to a largest
relative difference of 2.0e-16. The revised MATLAB repost at
pinhaocheng/epchan-quant_trading_MATLAB_codes `7430b84` carries an
`IJR_20080114.mat` with the sha256 recorded below. Each directory holds only the companies
still in its index on that day, carried backwards, so a figure computed from
either is a figure about survivors.
[`chan.momentum_factor`](../src/chan/momentum_factor.py) reads the first's
closes to build the momentum factor and the stocks it is compared against, for
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22).
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
   S&P 500 list below raises it.

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
   same across 400 days to 2007-07-02. `ijr_20080114/pmc.csv` holds two price
   histories the same way, closing at 6.02 on 2004-03-12 and then at 17.25 on
   2007-08-01, 851 trading days apart.
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
   no jump. Three are the splices in point 3. Four more sit within 0.02 of a
   two-for-one split, and whether any of them is an unadjusted split is not
   known.

   1. AES on 2001-09-26, in the S&P 500 file.
   2. AYE on 2002-10-08, in the S&P 500 file.
   3. CBU on 2004-04-13, in the S&P 600 file.
   4. INSP on 2008-01-09, in the S&P 600 file.

`ijr_20080131/` is the file Chan's Example 7.6 script loads, a later save of
the S&P 600 file holding the same 600 symbols.
[Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) committed
it so that the example's third return, January 2008, can be computed, and
carries the measurements below. `chan.equity_seasonals` reads it, and its
tests read `ijr_20080114/` beside it to say whether the first two Januaries
moved between the saves.

1. **Where it came from.** Not the mirror above, which does not hold it. It
   comes from
   [pinhaocheng/epchan-quant_trading_MATLAB_codes](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84a14a5f5b2216c03d0bfe62704368c7d47)
   at `7430b84`, a third party's repost of the revised edition's code and
   data rather than Chan's own mirror. The owner decided on 2026-10-03 to
   commit it from there. The copy is trusted because of its sibling: the same
   repost carries an `IJR_20080114.mat` whose sha256 is `a30f6560…`, the same
   bytes as the file the mirror holds and the first list records, so the
   repost carries Chan's files unaltered where that can be checked. The `.mat`
   is 10,675,731 bytes. It is not committed, and its sha256 is recorded here.
   The conversion read all five fields back from the committed files and
   found them equal to the file's arrays, NaN for NaN.

   ```text
   1a038ce1adf7af8461400ee8c8b7bc33696851397b6ebface5f913be34bce164  IJR_20080131.mat
   ```

2. **The names are 17 days apart and the saves 18.** The MAT header records
   2008-02-02, against 2008-01-15 for the earlier save. Unlike the first two
   files, this name is not the last trading day. The last row is 2008-02-01,
   priced for 596 of the 600, and four share classes have no close on it:
   MOG.A, MOGN, TRX.B and TRY.B. That trailing row is what makes 2008-01-31 a
   January month-end under every printout's rules, so the third holding
   needs it.
3. **The two saves disagree only on the earlier save's last six trading
   days.** `chan.series.vintage_overlap` set each stock's two closes side by
   side on the 589,660 days they share, and `chan.series.departures` found 198
   that differ, in 42 stocks, every one between 2008-01-07 and 2008-01-14. A
   tolerance of half a cent finds the same 198. The opens, highs and lows
   differ on the same six days, and the volumes on none. The first two
   Januaries read no close after 2007-01-31, so both saves give them to the
   same digits. Two of the departures are large, and which save is right is
   not known.
   1. INSP's later save scales its closes on 2008-01-07 and 2008-01-08 by
      0.4969 and leaves the days before them alone. That moves the
      two-for-one-sized step the earlier save shows on 2008-01-09 to
      2008-01-07.
   2. SHFL's close on 2008-01-10 is 10.30 in the earlier save and 9.09 in the
      later one.
4. **It is recorded as `adjusted`, on the measurement the first list's point
   5 made.** Across 596,817 ratios of an open to the close before it, two sit
   within 0.01 of a two-for-one split: CBU on 2004-04-13, as in the earlier
   save, and INSP on 2008-01-07, the step point 3 describes. Five sit within
   0.01 of a three-for-two split, against four in the earlier save.
5. **The scale-break guard flags 21 days in 19 of the 600, on the close.**
   Seventeen of the earlier save's eighteen flagged stocks flag the same days.
   INSP's flag moves to 2008-01-07, per point 3. IDXX is new, and its two
   days are one close: 30.05 on 2008-01-25, between 55.60 and 53.75, equal
   to that day's low and far below its open of 55.28. Example 7.6 reads
   neither stock on those days, because its January 2008 holding reads the
   closes of 2007-12-31 and 2008-01-31. All 21 are pinned in
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
6. **It fits the budget.** The directory holds 26.10 MB, and its manifest and
   checksum lines and this section add 0.25 MB, which takes `data/` from
   108.56 MB to 134.91 MB of file content. That left 15.09 MB under the
   150 MB budget point 5 of the book-two S&P 500 list below set at the time.

Two more directories hold the two files of Chan's second book, *Algorithmic
Trading*, that his Example 7.2 reads.
[Issue 20](https://github.com/l3a0/quantitative-trading/issues/20) reproduces
that example.
[Issue 297](https://github.com/l3a0/quantitative-trading/issues/297) and
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295) reproduce
Examples 6.2 and 4.1 on the price file alone,
[issue 296](https://github.com/l3a0/quantitative-trading/issues/296) reads its
opens and closes for Examples 4.3 and 4.4, and
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343) reads its
closes against the ETF file's SPY for Example 4.2.
`inputdataohlcdaily_stocks_20120424/` is the S&P 500 as Chan held it on
2012-04-24, with the same five fields per stock as the first two
directories. `earnannfile/` holds his earnings-announcement flags for the same
497 stocks, a 0 or 1 for each trading day. Like the first two, the price file
holds only the companies still in the index on its date, so a figure computed
from it is a figure about survivors.
[`chan.cross_sectional_momentum`](../src/chan/cross_sectional_momentum.py) reads
the price file's closes for Example 6.2, for
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297), and
[`chan.index_arbitrage`](../src/chan/index_arbitrage.py) reads them for
Example 4.2, for
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343).
[Issue 250](https://github.com/l3a0/quantitative-trading/issues/250) carries the
measurements below.

1. **Where they came from.** Two public mirrors of Chan's book-two code hold
   both files with identical git blob hashes:
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview)
   at `e4bc46f`, under `public/img/book2/`, and
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
   at `4567024`, under `archived/matlab/`. Neither carries a licence, which
   README's licence paragraph already covers. The `.mat` files are not
   committed, and their sha256 is recorded here. EpchanPreview holds the price
   file a third time, as
   `public/img/book3/Chap3 Time Series/inputDataOHLCDaily_20120424.mat`, the
   same git blob, `0fb5ebc`, and the same sha256. That is the name, with no
   `_stocks`, that Example 4.1's `bog.m` loads, and neither mirror holds
   another file of that name. `chan.mat_columns.round_trip_differs` finds the
   committed members rebuild all five of its arrays exactly. What the copy
   cannot show is that the file Chan ran in 2012 was the one he later shipped
   under that name.
   `andrewlo_2007_2012.m`, the script of Examples 4.3 and 4.4, and
   `indexArb.m` load the same name. Example 4.4's run lands on the six
   decimals its script printed, which
   [issue 296](https://github.com/l3a0/quantitative-trading/issues/296)
   measured, and so does Example 4.2's, which
   [issue 343](https://github.com/l3a0/quantitative-trading/issues/343)
   measured.

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
   the 2011 and 2012 window Example 7.2 trades. Example 6.2's script reads
   across all 30, one in its 2007 window and 29 in its 2008 and 2009 window,
   and [issue 297](https://github.com/l3a0/quantitative-trading/issues/297)
   decided not to call the guard there. All 30 also fall in Example 4.1's
   window, which is the file's whole span, and in the 2007 to 2011 window
   Examples 4.3 and 4.4 trade. One of them, CAH on 2009-09-02, reads as a data
   error or a corporate action rather than a crash, and
   `chan.khandani_lo_book_two`'s docstring says why that run computes across
   them. Example 4.2 reads across all 30 too, ETFC's 2007-11-12 in its 2007
   training window and 29 in its 2008 to 2012 test, and
   [issue 343](https://github.com/l3a0/quantitative-trading/issues/343)
   decided to guard only its SPY leg. They are pinned beside the others in
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
5. **The size budget is raised.** The two directories hold 32.01 MB, which
   takes `data/` from 74.41 MB to 106.86 MB of file content. The owner decided
   on 2026-10-03 to commit the whole price file rather than stay under the
   100 MB budget, because the mirrors are the only free copies, and raised the
   budget so that `data/` stays under 150 MB of file content. A later panel
   still states its own size against that in its issue before it is recorded.
   The owner raised the cap to 205 MB on 2026-10-04, on
   [issue 300](https://github.com/l3a0/quantitative-trading/issues/300), for
   the four book-two lifts of that day, and the lift of Chan's Python port
   below is what took `data/` past 150 MB.

The directory `pythoncodesanddata/` holds seven files of Chan's 2018 Python
port of *Algorithmic Trading*'s code, `PythonCodesAndData.zip`, committed byte
for byte under the names the zip gives them. Neither `.mat` mirror holds these
series, and the zip is the only free copy of them.

- USD.CAD's one-minute bars, which Examples 2.1 to 2.5 read at 16:59. The
  stationarity tests on USD.CAD run those examples, and they are the first run
  here to read any of the seven.
- The daily closes of USD.CAD, AUD.USD and AUD.CAD, which Examples 5.1 and 5.2
  read. Example 5.1 runs here, on the first two.
- The monthly AUD and CAD interest rates, which Example 5.2 reads for its
  rollover interest.
- The AUD.CAD returns Example 5.1 saved, which Chapter 8's Monte Carlo
  leverage, historical optimization and CPPI boxes read.

[Issue 301](https://github.com/l3a0/quantitative-trading/issues/301) carries
the measurements below.

1. **Where they came from.** The zip sits in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview)
   at `e4bc46f`, under `public/img/book2/`, as git blob `b573b1a` of
   13,645,198 bytes. The other mirror, ivanliu1989/algorithmic_trading, does
   not hold it. Each committed file is what
   `unzip -p PythonCodesAndData.zip PythonCodesAndData/<name>` writes, and
   [tests/test_python_port.py](../tests/test_python_port.py) pins each one's
   sha256. Each saved date is that file's own timestamp in the zip's central
   directory, the index of members that is part of the zip's bytes, and the vendor is `chan-py`.
   It is a vendor of its own rather than `chan-mat` or `chan-xls`, because
   those name his MATLAB files and his workbooks, and sharing one would let a
   read match two sources.

   ```text
   91e3d0d534f465feae31da3f6a19db03e32b190cf70a2470f03cde60617f8317  PythonCodesAndData.zip
   ```

2. **They keep the zip's shape.** The owner ruled on 2026-10-04 that the
   minute file is committed unchanged, so the other six are committed the same
   way, and each can be hashed against its zip member. A daily or minute file
   writes its date as `YYYYMMDD`. The headers are `Date,Time,Close` for the
   minute file, `Date,Close` for a daily one, `Year,Month,Rates` for a rate
   file and `Return` alone for the return file. All seven end their lines
   with a carriage return and a newline, which makes them the first files here
   to carry a carriage return. `data/** -text` in
   [.gitattributes](../.gitattributes) keeps those bytes as they are. They do
   not share one basis or one saved date, so each has its own row in the table
   above rather than one row for the directory.
3. **The minute file's clock is New York time, with daylight saving.** It
   holds 1,730,962 bars on 1,466 dates, from 2007-07-22 to 2012-03-28, with no
   date and time repeated. No bar falls from 17:00 to 17:14 on any day, across
   every change of clock from 2007 to 2012. A file kept in a fixed offset
   would shift that gap by an hour twice a year. The currency market's day closes
   at 17:00, so a full day holds 1,425 bars, the 1,440 minutes of a day less
   the 15-minute pause. The date column is the bar's calendar date, so a
   Sunday evening's bars carry the Sunday. No Sunday bar comes before 17:15,
   and every Friday's last bar is 16:59, except 2011-12-23's, at 14:59.
4. **Its daily close is the 16:59 bar, filtered at read time rather than
   committed.** Chan's MATLAB takes `cl(hhmm==1659)` and his Python takes
   `df['Time']==1659`, and `chan.series.load_minute_close` does the same from
   the verified bytes. That gives 1,216 closes from 2007-07-23 to 2012-03-28.
   Of the 1,466 dates, 250 hold no 16:59 bar.
   - 245 Sundays, whose session opens at 17:15.
   - Four holidays: 2007-12-25, 2008-01-01, 2008-12-25 and 2009-01-01.
   - The early close on 2011-12-23.

   The scale-break guard reads these closes, and it flags no day in them or in
   the three daily files.
5. **The bases.** A currency is `raw`, because it has no splits or dividends
   to adjust for. The two interest-rate files are `rate`, and each one's span
   runs from the first of its first month to the first of its last, the
   convention the FRED bill series uses. The return file carries a fifth
   basis, `return`, which the owner added on 2026-10-04, under the symbol
   `AUDCAD-UNEQUAL`. It holds no dates. `AUDCAD_unequal.m`, Example 5.1's
   script, trains on the first 250 of the AUD.USD daily file's 862 days and
   saves the returns of the other 612, so its span is that file's rows 251 to
   862, 2009-12-18 to 2012-04-26. Those are the dates the book gives for
   Example 5.1's performance. The two USD.CAD files share vendor, symbol and
   basis, so a reader passes the saved date to name one.
6. **The files agree with each other.** Each of these is a test in
   [tests/test_python_port.py](../tests/test_python_port.py).
   1. The 16:59 closes equal the daily USD.CAD file exactly on all 841 dates
      the two share, 2009-01-02 to 2012-03-28. The daily file runs 21 dates
      further.
   2. The AUD.USD and USD.CAD daily files carry the same 862 dates, which
      `AUDCAD_unequal.m` assumes when it takes one file's dates for both.
   3. AUD.CAD agrees with AUD.USD times USD.CAD on those 862 dates. The median
      relative gap is 6.0e-5 and the largest is 0.19%, on 2009-05-27.
   4. AUD.CAD agrees loosely with the inverse of the yfinance `CADAUD=X` raw
      vintage above, on the 1,220 of its 1,237 dates that vintage also holds.
      The median relative gap is 0.16%, the 95th percentile 0.83%, and three
      days pass 2%, the largest 6.6% on 2008-10-10. yfinance does not record
      the hour its currency close is taken at, so this bounds a gross error
      and no more.
7. **The rates and returns match the `.mat` files Chan's MATLAB loaded.**
   Three `.mat` files in the mirror hold the same series. They are not
   committed, so this is a measurement rather than a test. The examples'
   printed figures come from the MATLAB, which read these, and no difference
   below moves a printed digit.

   - `AUD_interestRate.mat`, blob `c1613e4`, whose header says it was saved
     on 2012-04-30, holds the same 147 years and months, and its rates differ
     from the CSV's by at most 4.9e-15.
   - `CAD_interestRate.mat`, blob `95f3a9d`, saved on 2012-04-30, holds the
     same 144 years and months and identical rates.
   - `AUDCAD_unequal_ret.mat`, blob `e2c3465`, saved on 2012-07-03, holds the
     same 612 returns, differing by at most 4.0e-16. It is an output rather
     than an input: `AUDCAD_unequal.m` ends by saving its returns under that
     name, and `monteCarloOptimLeverage.m` loads it.

   ```text
   02d86dd720e149b03a6bae7bd561116be9ab227f59a2c890890b6f187d021a90  AUD_interestRate.mat
   36b7ece549e60052c043619684030ea1d4b7159359dd6b68604b501e346fd519  CAD_interestRate.mat
   13a058403b5ef592dc27b2839bb81b695622740f4218e4896fa6064a01922c5e  AUDCAD_unequal_ret.mat
   ```

8. **Three things cannot be checked here.**
   1. Whether the four currency files equal the `.mat` files Chan's MATLAB
      loaded, `inputData_USDCAD.mat` and the three `_20120426.mat` files.
      Neither mirror holds any of them, so three have indirect evidence
      instead and the AUD.CAD file has none. Example 5.1 run as the MATLAB
      runs it, on the AUD.USD and USD.CAD daily files, returns all 612 of the
      returns `AUDCAD_unequal_ret.mat` saved, within the 1e-9 declared before
      any was computed. So those two files agree with the MATLAB's inputs up to
      a constant scale on each leg, which no return can see. That is Entry 25
      of the
      [replication log](../docs/replication-log.md), which
      [tests/test_aud_cad_johansen.py](../tests/test_aud_cad_johansen.py)
      pins. The minute file's evidence is four statistics computed from its
      16:59 closes, which land every digit `stationarityTests.m` prints for
      Examples 2.1, 2.3 and 2.4, as Entry 22 records and
      [tests/test_usdcad_mean_reversion.py](../tests/test_usdcad_mean_reversion.py)
      pins.
   2. Who supplied the bars, and whether a bar's label is its first minute or
      its last. Chan's text calls the 16:59 bar the daily close at 16:59 ET,
      and nothing in the files says more.
   3. The rates against the Reserve Bank of Australia's and the Bank of
      Canada's own tables, which the book names as their source.
9. **The owner raised the size cap to 205 MB.** The seven files hold 38,634,670
   bytes, 38.63 MB. With their manifest and checksum lines and this section
   they take `data/` from 148.72 MB, where the futures strips and the ETF file
   below left it, to 187.37 MB of file content, past the 150 MB cap. The owner ruled on 2026-10-04, on
   [issue 300](https://github.com/l3a0/quantitative-trading/issues/300), that
   the four book-two lifts of that day land whole under a cap of 205 MB, and
   that past 205 MB the work stops and asks. So `data/` now stays under
   205 MB of file content.

The next eight directories are Chan's per-contract futures strips from
*Algorithmic Trading*, and the ninth is his gold series sampled at 16:00. A
futures contract is an agreement to trade a commodity in one delivery month,
and the exchange publishes a settlement price for it each day it trades. A
strip holds one column of those settlements per contract, for one commodity,
named by the exchange's code for that commodity, its root, such as CL for
crude oil. A spot column holds the price of the commodity itself rather than
of a contract on it.

His Example 5.3, `estimateFuturesReturns.m`, reads seven of the strips one at
a time. It splits each commodity's return into the part that comes from the
commodity's own price and the part that comes from holding contracts as they
near delivery. His Example 5.4, `calendarSpdsMeanReversion.m`, reads the CL
strip named for 2012-08-13 to trade the gap between two crude contracts
delivering 12 months apart. Two unnumbered experiments read the TU and VX
strips. `VX_ES_rollreturn.m` also reads the VX strip, and `GLD_GC.m` reads the
gold series. No replication reads any of them yet.
[Issue 300](https://github.com/l3a0/quantitative-trading/issues/300) carries
the decision behind the shape, and the build measured what follows.

1. **Where they came from.** Both mirrors named in point 1 of the book-two
   S&P 500 list above hold all nine, with identical git blobs: EpchanPreview at
   `e4bc46f` under `public/img/book2/`, and ivanliu1989/algorithmic_trading at
   `4567024` under `archived/matlab/`. Neither carries a licence. The `.mat`
   files are not committed, and their sha256 is recorded here.

   ```text
   e6cd73a6ee37377769dbdf4047df8a4d17c2c599114a073e133f8c724e0c3d65  inputDataDaily_BR_20120813.mat
   7fadd1939c3b85fc2bb9121aecbae6c4f13394a76cb0aa0ea3c04b8bd943470f  inputDataDaily_C2_20120813.mat
   3d4c5f2373eeb0c99ed18c903e0926d7c41a22a12055bd2ce661de249de80af2  inputDataDaily_CL_20120813.mat
   684df457d7c1a4d4d915ec25e010b0d9fe19eb73e779d6db9918125be2a8746b  inputDataDaily_HG_20120813.mat
   9cce5d11c2c1f142bec4f9321e3ea787d9f32cdcb17b0df1a743a53278c40ff8  inputDataDaily_HO2_20120813.mat
   c75a09f543ce0d03d398f220dddca568d3b4f01a0042c27eb3515350ff2614a5  inputDataDaily_TU_20120813.mat
   3ff9af0b9f084159647547f5f0c412b1fd9e8474525ab64804b071abf75d0485  inputDataDaily_CL_20120502.mat
   baa6ff188a232c2ee96d3f94b3ec4b3003994ec6e3ec3ab2ee1705bc06bf5f3b  inputDataDaily_VX_20120507.mat
   eaacdd398a9677207b02c524dd686081823b03a5cb1b148b2fba132c7babd257  inputData_GC_1600_20100802.mat
   ```

2. **Each contract is one vintage holding its settlement alone.** A strip
   holds `tday`, `contracts` and `cl` and nothing else, so each member's
   `Close` field holds the contract's daily settlement and no other field
   exists. The symbol joins the root in the file's name to the contract, such
   as `CL-2007F`, where 2007 is the delivery year and F is CME's letter for
   January. The root is there because the six strips named for 2012-08-13
   share one saved date, 2012-08-14, and all six hold a December 2007
   contract. A bare `2007Z` would name six vintages under one vendor, basis
   and date, and no reader argument could separate them. Chan names the spot
   column `0000$`, which the record's symbol rule refuses, so it is recorded
   as `<root>-SPOT`. Six strips carry one, and the CL strip named for
   2012-05-02 and the VX strip carry none.
3. **The basis is `raw`.** A contract's settlement is the price it traded at,
   and nothing adjusts it. A continuous series, which switches from each
   expiring contract to the next, is different, because its history is
   shifted at every switch.
4. **Sorted symbols are Chan's contract order.** `chan.series.load_panel`
   returns members sorted by symbol, and CME's month letters, F G H J K M N Q
   U V X Z, run alphabetically in calendar order. In all eight strips the
   contracts in file order are their sorted order. The spot column sorts
   last, although four strips hold it first, which the committed bytes cannot
   show and nothing pins. The order matters because
   `calendarSpdsMeanReversion.m` pairs a contract with the one 12 places later
   by position.
5. **A day without a settlement is a missing row.** No strip holds a day on
   which no contract settled, so the union of the members' dates is the
   file's own `tday`, and `load_panel` rebuilds every NaN. Some columns stop
   and restart: 15 in BR, 29 in HG, 31 in HO2, 2 in TU and 1 in the CL strip
   named for 2012-08-13, spot columns included. The scripts read those holes,
   because they find a contract's last day as the last finite settlement
   before a NaN. `chan.mat_columns.strip_round_trip_differs` rebuilt each
   strip's `cl` array from the committed bytes and found it equal, days,
   column order and every NaN included.
6. **HO2's expiries follow a rule `chan.futures` already holds.** The rule for
   RBOB, NYMEX's gasoline contract, is the last business day of the month
   before delivery, and heating oil's is the same. Of HO2's 309 contracts that
   stop before the file does, 300 last settle on that rule's day. For 8, the
   rule's day has no row in the file, such as 1986-11-28 and 1993-12-31, and
   each stops on the row before, so Chan's calendar lacks some NYMEX trading
   days. One, August 2012, stops a day early.
   [tests/test_futures_strips.py](../tests/test_futures_strips.py) pins those
   counts.
7. **No other expiry rule is built.** `chan.futures` has none for CL, VX, TU,
   BR, HG or C2, and nothing needs one, because every script finds a
   contract's last day from the data. A scratch script, not committed, wrote
   two to see how far the files follow the exchanges, and none of its figures
   is pinned. CME's crude rule, three business days before the 25th of the
   month before delivery, gives the last settlement of 65 of the 68 expired
   contracts in the CL strip named for 2012-08-13 and 62 of the 65 in the one
   named for 2012-05-02. The three misses are the same three contracts in
   both, each stopping one trading day early. For VX, CFE, the Cboe futures
   exchange, settles a contract on the Wednesday 30 days before the next
   month's third Friday, or 30 days before the Thursday when that Friday is a
   holiday. The last settlement of 36 of VX's 64 expired contracts falls on
   that day, 23 on the trading day before it, and 5 on neither.
8. **The Python port's copies agree.** Chan's 2018 Python port,
   `PythonCodesAndData.zip` in EpchanPreview, sha256
   `91e3d0d534f465feae31da3f6a19db03e32b190cf70a2470f03cde60617f8317`,
   carries three of the strips as CSV: C2, the CL strip named for 2012-05-02,
   and VX. Each holds the `.mat` file's days and columns in the same order,
   and each equals it cell for cell, NaN for NaN, across 25,168, 92,440 and
   12,279 settlements. C2's copy names its spot column `C_Spot` rather than
   `0000$`. The zip is not committed, so the comparison ran when the strips
   were recorded, and nothing pins it.
9. **The gold series is one vintage, `GC`.** It is recorded under `chan-mat`
   and `raw`, the close alone, and its root comes from its name the way a
   strip's does. The GC column of `inputDataOHLCDaily_20120504.mat`, sha256
   `b69f8b8c…`, is a continuous series, shifted at each switch of contract.
   On all 555 days the two share, the 16:00 close sits between 15.4 dollars
   below it and 84.7 dollars above it, a measurement nothing pins because
   that file is not committed. Both carry the saved date 2012-05-07, so the
   basis is also what keeps them apart. The file also holds `hhmm`, 18,326
   times of day taking 27 values, against 761 closes, so it does not index
   them. `GLD_GC.m` loads `hhmm` but never uses it, so the lift drops it.
10. **The scale-break guard flags nothing.** It reads all 1,232 members as
    prices, because their basis is `raw`, and no close in any of them sits
    below 0.625 or above 1.6 times the one before.
11. **It fits the budget.** The nine directories and their manifest and
    checksum lines hold 10.36 MB, and this section adds 0.01 MB, which takes
    `data/` from 134.91 MB to 145.28 MB of file content, under the 150 MB
    budget point 5 of the book-two S&P 500 list above set at the time. The owner ruled on
    2026-10-04, on
    [issue 300](https://github.com/l3a0/quantitative-trading/issues/300), that
    this lift and the three built beside it may take `data/` to 205 MB, and
    the change that crosses 150 MB raises the budget. Point 9 of the Python
    port list above is that change.

`inputdata_etf/` is Chan's book-two ETF file, `inputData_ETF.mat`, which most
of *Algorithmic Trading*'s ETF experiments read. It holds 67 ETFs over 1,500
trading days, 2006-04-26 to 2012-04-09, with the same five fields per member
as the stock files. Nine of his book-two scripts load it, and each reads only
its days, its symbols and its closes. They cover the cointegration tests and
mean-reversion portfolio of Examples 2.6 to 2.8 on EWA, EWC and IGE, the
price spread, ratio, Bollinger band and Kalman filter examples of Chapter 3
on GLD, USO, EWA and EWC, and the SPY leg of Example 4.2. Example 3.1 is
the first run to read it, GLD and USO alone, under
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340).
Examples 2.6 to 2.8 read EWA, EWC and IGE from it through
`chan.etf_cointegration`, for
[issue 339](https://github.com/l3a0/quantitative-trading/issues/339), and
Example 4.2 reads SPY through `chan.index_arbitrage`, for
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343).
Example 3.2 reads GLD and USO through `chan.bollinger`, which reuses Example
3.1's reader, for
[issue 341](https://github.com/l3a0/quantitative-trading/issues/341).
[Issue 299](https://github.com/l3a0/quantitative-trading/issues/299)
carries the measurements below.

1. **Where it came from.** Three copies exist, and all three are one git
   blob, `261718b`.

   1. [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview)
      at `e4bc46f`, under `public/img/book2/`.
   2. The same mirror at the same commit, under
      `public/img/book3/Chap3 Time Series/`.
   3. [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading)
      at `4567024`, under `archived/matlab/`.

   Neither mirror carries a licence, which README's licence paragraph already
   covers. The `.mat` is 1,218,621 bytes. It is not committed, and its sha256
   is recorded here. Its header says it was created on 2012-04-10, which is
   the saved date every member carries. The file names its list of symbols
   `syms` where the stock files say `stocks`, and `chan.mat_columns` reads
   either. `chan.mat_columns.round_trip_differs` finds the committed members
   rebuild all five of its arrays exactly, NaN for NaN.

   ```text
   5f8dc0f05cba1bd69dc1fa3fe11b6a397c06cfd39174ba47171bd8ff66ff2065  inputData_ETF.mat
   ```

2. **Chan's Python port agrees with it.** EpchanPreview alone holds
   `PythonCodesAndData.zip`, blob `b573b1a`, Chan's 2018 port of the book's
   code. Its `inputData_ETF_stocks.csv` lists the same 67 symbols in the same
   order. Its `inputData_ETF_cl.csv` holds the same 1,500 days, all 83,454
   priced closes are equal, and the same cells are missing.
   `inputData_EWA_EWC.csv`, `inputData_EWA_EWC_IGE.csv` and
   `inputData_GLD_USO.csv` are exact copies of those columns. The port holds
   closes only, so the opens, highs, lows and volumes exist only in the
   `.mat`.
3. **The prices are `adjusted`, by subtraction rather than by rescaling.**
   This file folds each dividend in by subtracting it in dollars from every
   earlier close, where a yfinance adjusted close multiplies every earlier
   close by a factor. Against the raw SPY downloaded on 2026-10-03, rounded to
   the cent, Chan's SPY sits 14.98 below raw on 2006-04-26 and level with it on
   2012-04-09. The gap moves by more than a cent on exactly the 24 days the
   adjusted SPY downloaded on 2026-09-18 marks as ex-dividend. Those 24 moves
   run from 0.48 to 0.80, each within a cent of the dividend that download
   implies. On
   43 other days it moves by one cent, which is the two vendors disagreeing on
   a raw close. GDX moves the same way on its five December ex-dividend days,
   and GLD, which pays nothing, equals its raw download on all 1,500 days.
   Splits are folded in as well. Across 83,387 ratios of an open to the close
   before it, none sits within 0.01 of the ratio a 2:1, 3:2 or 4:1 split or a
   1:2, 1:4, 1:5 or 1:10 reverse split would give.

   A subtracted dividend can take a close below zero, and 11 go there, in
   EDC, MWJ and SMN, such as MWJ at −1.07 on 2009-03-06. The owner decided on
   2026-10-04 to record the file as `adjusted` rather than add a basis, and
   [docs/design.md](../docs/design.md) widens its **adjusted price** row to
   cover both methods. The price of that decision is that a return computed
   from these closes is not the return a holder earned. None of the ETFs the
   examples above read comes near zero, and their lowest closes run from
   EWA's 7.49 to SPY's 60.48. `TestTheETFFileSubtractsEachDividend` in
   [tests/test_series.py](../tests/test_series.py) pins every figure in this
   point.
4. **The scale-break guard flags 58 days in eight of the 67, on the close.** Each
   of the eight is a leveraged or inverse fund, and every day falls between
   2008-04-16 and 2009-06-25.

   1. EDC on 13 days.
   2. EEV on 2.
   3. FAS on 2.
   4. FAZ on 4.
   5. MWJ on 11.
   6. MWN on 1.
   7. SMN on 24.
   8. TNA on 1.

   None of them is an ETF the examples above read. All 58 are pinned in
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
5. **It fits the budget.** The directory holds 3.40 MB, and its manifest and
   checksum lines and this section add 0.03 MB, which takes `data/` from
   145.28 MB to 148.72 MB of file content. That stayed under the 150 MB
   budget that point 5 of the book-two S&P 500 list set at the time. The owner set a
   ceiling of 205 MB on 2026-10-04, on
   [issue 300](https://github.com/l3a0/quantitative-trading/issues/300), for
   this lift and the book-two lifts of issues
   [300](https://github.com/l3a0/quantitative-trading/issues/300),
   [301](https://github.com/l3a0/quantitative-trading/issues/301) and
   [313](https://github.com/l3a0/quantitative-trading/issues/313). The lift
   that takes `data/` past 150 MB raises the budget to it, which point 9 of
   the Python port list above does.

The four `inputdataohlcdaily_2012*/` directories hold four saves of Chan's
continuous futures series from *Algorithmic Trading*, and `vix/` holds his
`VIX.csv`. A futures contract expires, so a series running for years is built
by rolling from one contract to the next and shifting the history at each roll.
Each of the four futures directories is named for the date in its file's name.
The saved date, one to three days later, comes from the MAT header. These scripts read them, by file
and symbol.

1. `TU_mom_hypothesisTest.m` and `TU_mom.m`, Examples 1.1 and 6.1, read TU
   from the 2012-05-11 save.
2. `CL_rev.m` reads CL from the 2012-05-04 save.
3. `VX_ES.m` reads VX and ES, and `gapFutures_FSTX.m`, Example 7.1's gap on
   Euro Stoxx 50 futures, reads FSTX, all from the 2012-05-17 save.
4. `VX_ES_rollreturn.m` reads ES from the 2012-05-07 save and the close of
   `VIX.csv`.
5. The two VIX-filtered variants at Kindle location 3509, of Examples 4.1 and 7.1,
   read `VIX.csv`.

[Issue 313](https://github.com/l3a0/quantitative-trading/issues/313) carries
the measurements below.

1. **Where they came from.** The two mirrors that hold the book-two stock file
   above hold all five, with identical git blobs: EpchanPreview at `e4bc46f`
   under `public/img/book2/`, and algorithmic_trading at `4567024` under
   `archived/matlab/`. The sources are not committed, and their sha256 is
   recorded here.

   ```text
   b69f8b8ce0c14b422184e15f20ff93cd65d56141ae632c92ac8115fd1c06144f  inputDataOHLCDaily_20120504.mat
   3cc01a9623031df25aa45abfc2201869d7a1288c018d8a46e62f7cad1fe72892  inputDataOHLCDaily_20120507.mat
   1714d630b05b9343d569092ade56f3f6f2885d0db0e2a9150b4841062640be98  inputDataOHLCDaily_20120511.mat
   b155d8d50634d7322a24808160f97269c3687f52ce7ae160d1002ac3a0835c08  inputDataOHLCDaily_20120517.mat
   3e7374d398758b468d765b32e20ab6aaf2a8ed93eafe348c8a8bf3f9ccde874a  VIX.csv
   ```

   Only EpchanPreview holds `PythonCodesAndData.zip`, Chan's 2018 Python port,
   at blob `b573b1a`. Points 6 and 7 read it.

   ```text
   91e3d0d534f465feae31da3f6a19db03e32b190cf70a2470f03cde60617f8317  PythonCodesAndData.zip
   ```

2. **The series are rewritten between saves, and recorded as `adjusted`.**
   How they are rewritten was measured for CL alone. On 2008-05-19 the 2012-05-04 save's CL closes at 175.48, where the CL front
   contract in Chan's `inputDataDaily_CL_20120502.mat` settles at 127.05, and
   by 2012-04-10 the gap is 0.51. Of the 998 days the two share, the save
   equals the front contract on 8. The contract file is committed above as
   `inputdatadaily_cl_20120502/`, and `TestTheCommittedSavesAreChansColumns`
   in [tests/test_continuous_futures.py](../tests/test_continuous_futures.py)
   pins all four figures against it. That is the price back-adjustment Chan's
   Chapter 5 describes, which shifts the history by each roll's gap rather
   than rescaling it. Between the 2012-05-07 and 2012-05-11 saves, CL and QM
   each move by one constant on every shared day, which is what a roll falling
   between two saves does to such a series. 46 of the other symbols do not move
   at all. C, ES, GC and VX change by neither one constant nor one factor, so
   how Chan's source built those four was not measured, and a return computed
   across a roll in them should not assume a shift. The basis field exists to
   tell a series rewritten backward between vintages from one that is not, and
   every one of these can be, so `adjusted` names them all.
   `docs/design.md`'s vocabulary entry for **adjusted price** covers a futures
   series rewritten at each roll as well as a close adjusted for splits and
   dividends.
3. **Each symbol keeps its own calendar.** `tday` is a date-by-symbol array,
   1,000 by 51 in the 2012-05-04 save and 2,000 by 52 or 53 in the others, and
   each script takes one symbol's column of it. A member's rows are the days
   its column is priced. Every column's unpriced cells lead it, measured on all
   208 columns, so dropping them moves no row a script steps through, and
   `chan.mat_columns.read_continuous` refuses a file where they do not.
   CL, ES, TU, VX and FSTX are priced on every row in every save that holds
   them. `chan.mat_columns.continuous_round_trip_differs` holds each member's
   rows to its column's priced rows, every field, exactly, and found all 208
   identical. The panel `chan.series.load_panel` builds is the union of the
   members' days, which is not this file's layout, so a replication reads one
   member as `load_panel(source)[symbol].dropna()`.

   Unpriced cells are not the only break a row-by-row script can step across.
   In each of the three 2,000-row saves, ZB's and ZF's own days run straight
   from 1998-03-10 to 2008-04-16, and ZN's to 2008-04-17. Those are adjacent
   rows ten years apart, so a return taken across them spans a decade. Their
   stretch before it is sparse too, with gaps of up to 103 days, and no other
   column in any save skips more than ten days between rows. The reader checks
   that days increase, not how far apart they are, so it does not refuse this.
   No script of Chan's reads ZB, ZF or ZN.
4. **The column with no name is kept as `COLUMN-6`.** The 2012-05-07 save holds
   53 columns, and the sixth, between BZ and CAD, has an empty name. Its 2,000
   closes equal the 2012-05-11 save's `C` on all 1,997 days the two share,
   while the same save's own `C` is a different series, 48.75 below it at the
   median. No script reads the column. The owner decided on 2026-10-04 to keep
   it under a name built from its position, counting from one, because that name claims nothing
   the file does not say. It also keeps three days no later save holds,
   2004-05-28, 2004-06-01 and 2004-06-02. The reader names that one column for
   these bytes alone and refuses any other empty name.
5. **The four saves are four vintages, and they disagree.**
   `chan.series.vintage_overlap` set each symbol a script reads against its
   next save, and `chan.series.departures` with no tolerance counted the days
   their closes differ. Items 1 to 5 compare the close alone, and item 1 also
   says where the volume moves. Item 6 compares every field.
   1. TU's close never moves on a shared day. Its volume differs on each
      earlier save's last day.
   2. CL moves between the 2012-05-07 and 2012-05-11 saves by one constant on
      all 1,997 shared days: the later save is 0.27 higher.
   3. ES takes 17 distinct differences between those two saves, zero
      included, and agrees on 294 of 1,997 days.
   4. VX takes 79 distinct differences between those two saves and agrees on
      3 of 1,997 days.
   5. FSTX moves between the 2012-05-11 and 2012-05-17 saves, with 25 distinct
      differences, and agrees on 45 of 1,996 days.
   6. Of the 2012-05-04 save's 51 members, 18 agree with the 2012-05-07 save
      on every field of every shared day. 31 of the other 33 differ on one row,
      2012-05-04, the earlier save's last day. FFI differs on two, and BZ on
      all 1,000.
6. **The Python port's copies agree.** `inputDataDaily_ES_20120507.csv`,
   `inputDataDaily_FSTX_20120517.csv`, `inputDataOHLCDaily_TU_20120511.csv`
   and `TU.csv` from the zip each equal their member's committed fields cell
   for cell, 2,000 days each, the FSTX file on its open, high, low and close.
   The zip is not committed, so this ran when the files were recorded, the way
   the TLT and IEF column check did.
7. **`VIX.csv` is recorded under vendor `chan-csv`, basis `raw`, symbol
   `VIX`.** `chan-csv` names the kind of file Chan shipped, beside `chan-xls`
   and `chan-mat`. An index level as published has nothing to adjust. The file
   spans 1990-01-02 to 2012-05-08, 5,635 rows, and its volume is non-zero on
   136. Its `Adj Close` equals its `Close` on every row, so the vintage keeps
   the close, high, low, open and volume, and the reader refuses a file where
   the two differ. A CSV carries no header recording when it was saved, so the
   command takes `--saved-date`. The date, 2012-05-09, is the timestamp the
   zip records for its copy, which is the same file with CRLF line endings.
   Stripping the carriage returns gives the mirror's bytes, and the zip's copy
   itself hashes to this.

   ```text
   2013110389a7aa0366b6d1560e073ce980e8a9efbb7ba1370ae6c4620b5efedf  PythonCodesAndData/VIX.csv
   ```

8. **The scale-break guard flags ZB on 33 days and ZF on 9, in each of the
   three 2,000-row saves.** They fall between 1995-12-05 and 2008-04-16, and
   ZB's close goes as low as 0.4844. Up to 1998-03-10 ZB's closes run from
   0.4844 to 5.1094 and ZF's from 1.3594 to 3.3594, which is not the scale of
   a bond future. The next row in each is 2008-04-16, ten years later, per
   point 3, where ZB closes at 106.67 and ZF at 103.21, and neither closes
   below 99 after it. That flag is the jump across the hole onto the bond's
   scale. ZN has the same hole but sits on a bond's scale on both sides of
   it, from 84.05 to 94.77 before and 92.94 to 133.08 after, so nothing flags
   it. No script reads ZB, ZF or ZN.
   `VIX.csv` flags one day, 2007-02-27, when the index closed at 18.31 after
   11.15, which is a real move. Nothing else flags, the 2012-05-04 save
   included. All of them are pinned in
   [tests/test_scale_breaks.py](../tests/test_scale_breaks.py).
9. **It fits under the 205 MB ceiling.** The five directories and their
   manifest and checksum lines hold 15.11 MB, which takes `data/` from
   187.37 MB, where the Python port's files above left it, to 202.47 MB of
   file content before this section and 202.48 MB with it. That leaves
   2.52 MB under the 205 MB budget point 9 of the Python port list sets, under
   the owner's ruling of 2026-10-04 on
   [issue 300](https://github.com/l3a0/quantitative-trading/issues/300). Past
   205 MB the work stops and asks the owner.

## Vintages kept in the owner's archive

Two kinds of series a run reads are not in this directory: two files of minute
bars, and one cross-section of daily closes, the last part of this section.
`archive_vintages.jsonl` records Alpha Vantage's one-minute bars for GLD and GDX, which
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23) reads for
Example 7.1, and the files themselves stay in the owner's data archive. The
vendor's terms grant personal, non-commercial use, so the bytes may not be
republished here. The owner decided on 2026-10-03 that the archive keeps them
and this repo keeps their hashes, and `docs/design.md`'s premise records that
as an exception.

| File | Vendor | Symbol | Span | Downloaded | Basis | Rows |
| --- | --- | --- | --- | --- | --- | --- |
| `gld_intraday_1min.csv.gz` | Alpha Vantage, `TIME_SERIES_INTRADAY` | GLD | 2004-11-18 to 2026-07-16 | 2026-07-17 | raw, as `adjusted=false` returns it, extended hours included | 2,984,037 |
| `gdx_intraday_1min.csv.gz` | the same | GDX | 2006-05-22 to 2026-10-02 | 2026-10-03 | the same | 2,656,028 |

`chan.archive` hands a file's bytes back only once they hash to its line, and
refuses with both hashes otherwise. On a machine with no archive it raises
`ArchiveUnavailable` instead, and every test reading the bars turns that into a
skip carrying the message. `docs/design.md`'s Configuration section says where
the archive's path is set.

Neither file is in `checksums.sha256`, which projects `vintages.jsonl` alone.
[tests/test_archive.py](../tests/test_archive.py) holds them instead. It pins
each line field for field. Wherever an archive is configured it also re-hashes
both files and holds each day's last regular-session close from 2006 to 2020 to
the committed raw daily vintage of the same symbol, reading the session as
`chan.cpo` does, so an early close ends at 12:59. On GLD's 3,776 days the
median gap is 0.012% and no day differs by more than 2%. On GDX's 3,680 days
the median is 0.046%, and nine days differ by more than 2%. Seven of those
fall in the crashes of 2008 and March 2020, where a closing auction can move
away from the last minute's trade. Two, 2009-09-17 and 2014-12-03, have no
cause found, and the second is 7.0% off.

That comparison is also what stands in for the scale-break guard, which reads
committed daily closes and never these minute bars. A minute series that
changed scale would show up as a day whose last close disagrees with the daily
vintage, and none does beyond the nine named.

The archive copy is the only kept copy of these bytes. The archive's own
`README.txt` marks both files as pinned by hash here, so a refresh writes a new
file name and never rewrites one this record names.

The same manifest can also record a cross-section of Alpha Vantage's daily
closes, which the owner ruled into the exception on 2026-10-04 for the S&P 600,
on [issue 335](https://github.com/l3a0/quantitative-trading/issues/335). Each
stock is one file in the archive, at `sp600/daily_<SYMBOL>.csv`, and one line
here carrying `"cross_section": "sp600"`. The file is the vendor's
`TIME_SERIES_DAILY_ADJUSTED` response unchanged, so it holds the raw close
beside the adjusted close, and its line records the basis as `adjusted`.
`chan.fetch_alphavantage` writes both, and `chan.archive.read_cross_section`
reads a cross-section back as a date-by-symbol frame of either close.

[Issue 333](https://github.com/l3a0/quantitative-trading/issues/333) recorded
the first 603 lines on 2026-10-05, one for each company IJR held at
2025-12-31, under the symbol `chan.equity_seasonals.ALPHAVANTAGE_SYMBOLS` maps
it to. The table above stays the two minute-bar files, because a table with a
row per stock would be 603 rows long.

| Cross-section | Vendor | Symbols | Span | Downloaded | Basis | Rows |
| --- | --- | --- | --- | --- | --- | --- |
| `sp600` | Alpha Vantage, `TIME_SERIES_DAILY_ADJUSTED`, `outputsize=full` | 603 | 1999-11-01 to 2026-10-02, each symbol from its first row to its last | 2026-10-05 | adjusted, with the raw close beside it | 2,993,012 |

Twenty-four of the 603 end before 2026-10-02, the earliest on 2026-01-22,
because those companies were delisted after the filing. Every file is the
vendor's response for the symbol named in its line, and no file is in this
directory.

The lines count against the size budget, because the manifest is in this
directory. The 603 lines hold 233,992 bytes. That takes `data/` from the
202.48 MB of file content that point 9 of
[issue 313](https://github.com/l3a0/quantitative-trading/issues/313)'s
measurements above left it at, to 202.72 MB, which leaves 2.28 MB under the 205 MB budget.
[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) adds the
companies that left the index to the same cross-section, and states its own
size before it records them.

[tests/test_archive.py](../tests/test_archive.py) pins the two standalone
lines field for field and hashes every line's file wherever an archive is
configured, which takes about a second with the cross-section in place.
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) holds the
603 lines by the sha256 of their bytes, everywhere, and leaves out lines the
cross-section gains for other symbols.

[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) recorded
896 lines on 2026-10-05 for the companies IJR held at a year-end from 2007 to
2024 and no longer held at 2025-12-31, beside the 603 that
[issue 333](https://github.com/l3a0/quantitative-trading/issues/333) recorded
for the 2025-12-31 members. 884 are under a ticker
`research/filings/ijr/members.csv` maps a company to, and 12 hold a ticker
that was tried and then replaced, which no member reads.

| Cross-section | Vendor | Symbols | Span | Downloaded | Basis | Rows |
| --- | --- | --- | --- | --- | --- | --- |
| `sp600`, [issue 332](https://github.com/l3a0/quantitative-trading/issues/332)'s lines | Alpha Vantage, `TIME_SERIES_DAILY_ADJUSTED`, `outputsize=full` | 896 | 1999-11-01 to 2026-10-02, each symbol from its first row to its last | 2026-10-05 | adjusted, with the raw close beside it | 3,653,318 |

Some of those series belong to a later company that reused a ticker, because
a ticker was fetched before the check could say whose prices it held. The
members file's check is what says which series a member's close comes from.
The 896 lines hold 347,681 bytes, which
[tests/test_sp600_panel.py](../tests/test_sp600_panel.py) pins with their row
count, their download date and their sha256. They take `data/` from the
202.72 MB above to 203.07 MB of file content, measured before this paragraph,
which leaves 1.93 MB under the 205 MB budget. Those two sizes were measured on
this branch and no test holds them.

## Header shape

The vintages here carry one of three header shapes.

The files placed by hand above carry a three-row header before the data,
except the seven of Chan's Python port, which the third shape below covers.
The shape is yfinance's multi-index frame, and the workbook columns were
written into it too, as is every stock `record_lifted_columns` writes. A stock
lifted with all five fields widens it to one cell per field, so its first two
rows read `Price,Close,High,Low,Open,Volume` and `Ticker,KO,KO,KO,KO,KO`. What
that buys, whether or not anybody meant it at the time, is that the symbol sits
in the bytes where a check can read it back, and `tests/test_vintage.py` now
does:

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

Those two shapes rather than one are deliberate. The three rows above are an artifact
of one vendor's frame, and writing `Price,Close` at the top of a series some
other vendor returned would be a claim the file has no business making. The
columns lifted from Chan's own files take the three-row shape anyway, the
workbook columns since before the recorder existed and the MATLAB columns
because they are held by the same check: the `Ticker,` row is what names the
series in the bytes, and none of them came from the recorder.

`load_close` drops every leading row whose first field does not parse as a
date, so it reads both of those shapes and does not depend on a row count.

The third shape is the header Chan's 2018 Python port gave each of its files,
such as `Date,Time,Close` for the minute bars and `Year,Month,Rates` for a
rate. A minute or daily file writes its dates as `YYYYMMDD`. The owner ruled
on 2026-10-04, on
[issue 301](https://github.com/l3a0/quantitative-trading/issues/301), that
these files are committed as the zip shipped them, so no header of this
repo's can be added to them. Every check that reads their dates knows each
file's layout from the pin in
[tests/support/committed_vintages.py](../tests/support/committed_vintages.py).
`chan.series.load_port_close` reads the daily files, and refuses the minute
file, whose second column is a time. `chan.series.load_minute_close` reads
that one, and `chan.series.load_returns` reads the return file, which holds no
dates.

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
   was fetched. Those lines name their vendor `chan-xls` for a workbook column,
   `chan-mat` for a column of one of his MATLAB files, `chan-py` for a file of
   his Python port and `chan-csv` for one of his CSV files, and carry a
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
   write a saved date, and the seven files of Chan's Python port, which were
   typed because they keep the zip's shape. Every other line was written by
   code, a download by
   `record_vintage` and a column lifted from Chan's MATLAB and CSV files by
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
- Every hand-written entry, and every column lifted from Chan's MATLAB and CSV
  files,
  names the series its file's `Ticker,` row carries.
- The hand-written entries, the lifted sources and the files of Chan's Python
  port carry the identity `tests/support/committed_vintages.py` pins for them,
  and each lifted source holds the number of members its pin gives, each at
  the path its directory and symbol make.
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

A directory of lifted columns gets one row rather than one per file, so a
source's lifted columns take one row between them. The row states what every
file in it has in common, which is the vendor, the basis and the date, along
with how many members it holds and the earliest and latest day any of them
carries. Its members must agree on the three shared cells, or the failure names the directory and the values. What
holds each member's own identity is the pin for its source in
[tests/support/committed_vintages.py](../tests/support/committed_vintages.py),
which also counts the members. The directory of Chan's Python port gets one
row per file instead, because its files do not share one basis or one saved
date, so one row could not state them. The check tells the two kinds
apart by the file names: a lifted column is named for its symbol, and a file
of the port keeps the name the zip gave it.
