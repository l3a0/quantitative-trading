# Filings

Example 7.6 ranks the S&P 600 as it stood at each December year-end, and
nothing Chan saved says which companies those were. IJR, the iShares fund that
tracks the S&P 600, prints its whole schedule of investments for every
December 31 in a filing iShares Trust makes with the SEC. This directory holds
what those filings say IJR held, so a panel can be built from the membership
the fund reported rather than from today's list carried backwards.
[Issue 361](https://github.com/l3a0/quantitative-trading/issues/361) built it,
and [src/chan/fund_holdings.py](../../src/chan/fund_holdings.py) reads and
writes it.

## Why a filing is pinned by its accession

A vendor restates a price series, so the repo keeps a vintage's bytes in
`data/`, because a result computed from a series nobody kept cannot be checked.
The SEC never restates a filing. Each filing has an accession number, which
names fixed bytes, and a correction is filed as a new accession. So the
accession pins what was read, the way the edition pins a table printed in a
book, and these files are a record of what a filing says rather than a
vintage.

That is also why they sit here rather than in `data/`. Every CSV under `data/`
must have a line in `data/vintages.jsonl`, and a schedule of holdings is
neither a dated series nor a column lifted from one of Chan's files.
[docs/design.md](../../docs/design.md)'s section "A record that reads a fund's
filings" carries the full reasoning and the two shapes that were rejected.

The price is that [data/README.md](../../data/README.md) and the manifest do
not list these files, and the size cap on `data/` does not count them.

## What is here

1. **`index.jsonl`**, one line per filing. It names the fund, the series, the
   form, the accession, the filing and report dates, the primary document and
   its sha256, the holdings file and its sha256 and row count, and for an N-Q
   the "Total Common Stocks" the schedule prints.
2. **One CSV per filing**, at `<fund>/<report date>.csv`, holding the rows under
   common stocks in the filing's order. The columns are
   `name,shares,value,cusip,isin,ticker`.

The CSV is written as the filing prints it, with three exceptions.

1. An N-Q's numbers lose their thousands separators, and the two 2018 values
   printed with a space inside them are each read as one number.
2. Footnote markers are dropped, and every run of whitespace becomes one space.
3. An N-PORT row takes the holding's `title` for its name, because from 2022
   the XML cuts `name` at 30 characters, and a CUSIP of nine zeros is written
   empty.

An N-Q prints no identifiers, so its rows leave the last three columns empty.
An N-PORT's share counts and values are the XML's own strings, decimals
included.

The source documents are not committed, because each N-Q runs to 15 to 38 MB.
The index's `document_sha256` says which bytes were parsed.

## Regenerating a file

SEC asks every request to name a contact, and a contact identifies a person, so
it is read from the machine rather than from this repo. Set
`QT_SEC_USER_AGENT`, or write one line to
`~/.config/quantitative-trading/sec_user_agent`, then run:

```bash
uv run python -m chan.fund_holdings fetch IJR
```

The run downloads each filing in the fund's committed list into a temporary
directory, parses it, and deletes it. Where the index already names a document,
a download with a different sha256 is refused. Where a file already exists, a
parse that would write the same bytes changes nothing and one that would write
different bytes is refused, naming both hashes. So to regenerate one file,
delete it and run again. The index line stays, and the run refuses if the new
parse disagrees with it.

The committed files were written on 2026-10-04 by `record` in that module, from
the documents the survey on the issue downloaded that day. `fetch` wraps the
same call around a download and has not yet run against EDGAR, so its first run
is also the first check that EDGAR still serves the bytes the index names.

## What reads it

[tests/test_fund_holdings.py](../../tests/test_fund_holdings.py) is the
authority for every count, including how many rows each filing holds, how many
of them are companies' stocks, and how many of those can be paired with the
filing before. No replication reads this directory yet.
