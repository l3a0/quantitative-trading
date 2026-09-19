# Papers

Sources a replication here chases a figure from, when the source is not one of
Chan's books. [../book-notes](../book-notes/README.md) holds the books, quoted
by Kindle location. This directory holds whole documents, because the figures
they carry are not quotable in a highlight and because a citation is only as
durable as whoever is hosting it.

| File | Paper | Author | Date | Read by |
| --- | --- | --- | --- | --- |
| [qian-2005-risk-parity-portfolios.pdf](qian-2005-risk-parity-portfolios.pdf) | *Risk Parity Portfolios: Efficient Portfolios Through True Diversification* | Edward Qian | September 2005 | [docs/replication-log.md](../../docs/replication-log.md) Entry 4 |

## Why the Qian paper is committed rather than linked

Chan reports this paper at Kindle location 4684 and describes it as "not
publicly distributed". It is on PanAgora's own website. Those two facts
together are the whole argument for keeping a copy.

1. **It is the only published counterpart four of Entry 4's rows have.**
   Chan prints an allocation, a leverage and a ranking, and no returns, no
   volatilities and no correlation, so twelve of that entry's fifteen rows carry
   "none, not a replication". The paper does better on six of those twelve, and
   the six are not alike.

   - **Four carry a printed figure.** Row 5 the two leg volatilities, row 6 the
     correlation, row 7 the 60/40 risk split, and row 10 both Sharpe ratios.
   - **Row 8 carries a claim rather than a figure.** The paper says the 23-77
     weights "would have equal risk contribution from stocks and bonds" and
     prints no number for it. Table 3's 48.4 and 51.6 are loss contributions,
     which the paper keeps distinct from risk contributions throughout.
   - **Row 4 is derivable rather than printed.** The volatility ratio is the
     quotient of the two volatilities of row 5.

   The other six are row 9, which asks what leverage implies about a
   correlation the paper never poses that way, and rows 11 to 15, which are
   sub-windows the paper works no more than the book does.
2. **The repo's rule is that every published figure names where the source
   prints it.** Entry 4 now quotes figures from this paper, so the paper has to
   be reachable or the rule is satisfied in form and not in substance.
3. **A link is not a record.** Chan already believed this document was not
   publicly available, which is one step from it not being. The premise this
   repo is built on is that a number whose source nobody kept is a number
   nobody can check, and that applies to a published figure as much as to a
   price series.

The price is named rather than hidden. This is a third party's copyrighted
document in a public repository, kept under the reasoning above and removable
on request. The repo owner made that call on 2026-09-18.

## What it holds

Six pages. The figures below are what Entry 4 reads, quoted at the precision
the paper prints. Each is stated by the paper rather than computed here. The
one derived number in this file is the volatility ratio two sections down,
which is a quotient of the two volatilities in this table and is labelled as
derived where it appears.

| Figure | Value | Where |
| --- | --- | --- |
| Sample span | 1983 to 2004 | the captions of Tables 1 and 2 |
| Sample frequency | monthly | the prose beside Table 1, on its own N column |
| Stock index | Russell 1000 | Table 2, as a column header |
| Bond index | Lehman Aggregate Bond Index | page 1 and Table 1's caption, abbreviated to "Lehman Agg" in Table 2 and given in full as "Lehman Brothers" only in the page 5 disclosure |
| Return basis | excess returns, "the returns of the assets minus 90-day T-bills" | footnote 3, and page 2 words the same thing as three-month Treasury bills |
| Stock volatility | 15.1 percent | Table 2 |
| Bond volatility | 4.6 percent | Table 2 |
| Stock-bond correlation | 0.2 | page 1 |
| 60/40 risk contribution | 93 percent stocks, 7 percent bonds | page 1 |
| Risk-parity allocation | 23 percent stocks, 77 percent bonds | page 2 |
| Leverage to match 60/40's risk | 1.8:1 | page 3 |
| Sharpe, 60/40 | 0.67 | Table 2 |
| Sharpe, levered risk parity | 0.87 | Table 2 |

## Two things it settles that were argued rather than cited

Both were decided on this repo's own reasoning before anybody read the paper,
which is why they are worth recording as confirmations rather than as changes.

1. **The bond proxy.**
   [Issue 15](https://github.com/l3a0/quantitative-trading/issues/15) chose AGG
   over TLT because Qian's leg is an aggregate bond exposure rather than a
   long-duration one. The paper's own disclosure describes the Lehman Aggregate
   as roughly 6,000 bonds with an approximate average maturity of ten years,
   which is intermediate duration. The ruling was right and this is the
   citation it did not have.
2. **The band around the printed weights.** `BOOK_RATIO_BAND` in
   [src/chan/risk_parity.py](../../src/chan/risk_parity.py) was derived purely
   from the rounding of 23 and 77, with no knowledge of the paper, and it runs
   from 3.2553 to 3.4444. Dividing the two volatilities the paper prints gives
   3.2826, which lands inside it. That quotient is derived here rather than
   printed by the paper, which is why it is not in the table above.

## What it does not settle

Two things, and each has a card that is the authority for what it is.

1. **The equity leg.** He read the Russell 1000 and Entry 4 reads SPY, which
   tracks the S&P 500.
   [Issue 160](https://github.com/l3a0/quantitative-trading/issues/160).
2. **The sample.** His is 1983 to 2004 and Entry 4's is 2003 to 2026.
   [Issue 161](https://github.com/l3a0/quantitative-trading/issues/161).

## Provenance

| Field | Value |
| --- | --- |
| Source | `https://www.panagora.com/assets/PanAgora-Risk-Parity-Portfolios-Efficient-Portfolios-Through-True-Diversification.pdf` |
| Downloaded | 2026-09-18 |
| Bytes | 288,359 |
| sha256 | `d9b6a7185726767e36628c79ecbc006044e7da23f0f38f1cf04d71311fd0e7c2` |
| Copyright | PanAgora Asset Management, per the notice the document carries |

The checksum is recorded for the same reason a vintage carries one, so a reader
can tell this copy from a later revision. Nothing executes it. It is stated here
rather than held by a test, because nothing has replaced a paper yet and the
counting rule in [CLAUDE.md](../../CLAUDE.md) defers a guard on a path that has
run zero times.
[Issue 164](https://github.com/l3a0/quantitative-trading/issues/164) is where
that deferral is written down, with what would reopen it.
The file itself carries a 2011 copyright line and a `270416 9/11` document code,
so it is a reprint of the September 2005 paper rather than the original
release.

Verify it the same way the vintages are verified:

```bash
shasum -a 256 research/papers/qian-2005-risk-parity-portfolios.pdf
```
