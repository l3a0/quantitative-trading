# Filings

Example 7.6 ranks the S&P 600 as it stood at each December year-end, Example
7.7 ranks the S&P 500 at each month-end, and nothing Chan saved says which
companies those were. IJR and IVV, the iShares funds that track the two
indices, print their whole schedule of investments in the filings iShares
Trust makes with the SEC. This directory holds what those filings say the two
funds held, so a panel can be built from the membership the fund reported
rather than from today's list carried backwards.
[Issue 361](https://github.com/l3a0/quantitative-trading/issues/361) built it
for IJR at every December 31 from 2007 to 2025, and
[issue 372](https://github.com/l3a0/quantitative-trading/issues/372) added IVV
at every quarter-end from 2008-12-31 to 2026-06-30.
[src/chan/fund_holdings.py](../../src/chan/fund_holdings.py) reads and writes
it.

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

1. **`index.jsonl`**, one line per fund and filing. It names the fund, the
   series, the form, the accession, the filing and report dates, the primary
   document and its sha256, the holdings file and its sha256 and row count, and
   for an HTML schedule the "Total Common Stocks" it prints. One N-Q holds every
   fund in the trust, so IJR's and IVV's December N-Q are one accession with a
   line for each fund.
2. **One CSV per fund and filing**, at `<fund>/<report date>.csv`, holding
   the rows under common stocks in the filing's order. The columns are
   `name,shares,value,cusip,isin,ticker`.

The CSV is written as the filing prints it, with three exceptions.

1. An HTML schedule's numbers lose their thousands separators, and a number
   printed with a space inside it, as IJR's 2018 N-Q does twice, is read as
   one number.
2. Footnote markers are dropped, every run of whitespace becomes one space,
   and a name the 2010-09-30 shareholder report wraps across two table rows is
   joined into one.
3. An N-PORT row takes the holding's `title` for its name, because from 2022
   the XML cuts `name` at 30 characters, and a CUSIP of nine zeros is written
   empty.

Four forms carry the schedules, and three of them are HTML: an N-Q, a
shareholder report, which is an N-CSR or N-CSRS, and the standalone NPORT-EX
that holds IVV's 2019-06-30. HTML prints no identifiers, so those rows leave
the last three columns empty. An N-PORT is XML, and its share counts and
values are the XML's own strings, decimals included. IVV's N-PORT rows carry
no ticker, while IJR's do from 2022.

IVV's 2013-09-30 has no file. Its shareholder report prints only a summary
schedule, so the date stays on the fund's list in the module with the reason,
and reading its members refuses and says why.

The source documents are not committed, because each N-Q or shareholder report
runs to 15 to 59 MB.
The index's `document_sha256` says which bytes were parsed.

## Regenerating a file

SEC asks every request to name a contact, and a contact identifies a person, so
it is read from the machine rather than from this repo. Set
`QT_SEC_USER_AGENT`, or write one line to
`~/.config/quantitative-trading/sec_user_agent`, then run:

```bash
uv run python -m chan.fund_holdings fetch IJR
```

The same command with `IVV` regenerates IVV's files.

The run downloads each filing in the fund's committed list into a temporary
directory, parses it, and deletes it. Where the index already names a document,
a download with a different sha256 is refused. Where a file already exists, a
parse that would write the same bytes changes nothing and one that would write
different bytes is refused, naming both hashes. So to regenerate one file,
delete it and run again. The index line stays, and the run refuses if the new
parse disagrees with it.

IJR's files were written on 2026-10-04 by `record` in that module, from the
documents the survey on its issue downloaded that day. IVV's were written on
2026-10-05 the same way. `fetch` wraps the same call around a download, and it
has run against EDGAR once for each fund, on 2026-10-05. IJR's run downloaded
all 19 documents and IVV's all 70. Each document's sha256 equalled the
index's, and neither run wrote a byte, because every parse reproduced the
committed file.

## What reads it

[tests/test_fund_holdings.py](../../tests/test_fund_holdings.py) is the
authority for every count about IJR, and
[tests/test_ivv_holdings.py](../../tests/test_ivv_holdings.py) for every count
about IVV. Those counts include how many rows each filing holds, how many of
them are companies' stocks, and how many of those can be paired with the
filing before. No replication reads this directory yet.
