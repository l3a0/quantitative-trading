# Committed vintages

Eight price series, committed because the numbers in
[tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py) were
computed from these exact bytes. A vendor restates an adjusted series without
announcing it, so a result checked against a fresh download is a result checked
against different data. [docs/design.md](../docs/design.md) carries the
reasoning.

Nothing regenerates these files. There is no fetch script, on purpose. A
re-download would move the pinned numbers and fail the suite, which is the
behaviour that makes the pins worth having.

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

The four yfinance files were not all taken on one day, and the difference is
the point rather than an oversight. `gld_20yr_prices.csv` was downloaded on
2026-06-16 and the other three on 2026-08-27, so GLD's adjusted series stops
ten weeks before its raw twin. Reading a download date off the directory
instead of off the file is how a vintage gets misattributed.

The `*_chan.csv` files are a different kind of source. Each is the
adjusted-close column of Ernest Chan's own book-companion spreadsheet, taken
from the public mirror at
[egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading).
The date given is when Chan last saved the workbook, which is the closest thing
these files have to a download date. Their checksums, as `.xls`, are recorded
in [src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py) next to
the runs that read them.

## Header shape

Every file carries a three-row header before the data, written by yfinance's
multi-index frame:

```text
Price,Close
Ticker,GLD
Date,
2004-11-18,44.380001068115234
```

`load_close` drops every leading row whose first field does not parse as a
date, so the reader does not depend on that row count staying at three.

## Verifying the bytes

```bash
cd data && shasum -a 256 -c checksums.sha256
```

The manifest is [checksums.sha256](checksums.sha256). A mismatch means the file
changed, and any number pinned against it is no longer a number computed from
it.
