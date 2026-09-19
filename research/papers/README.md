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

1. **It is the only published counterpart six of Entry 4's rows have.**
   Chan prints an allocation, a leverage and a ranking, and no returns, no
   volatilities and no correlation. Twelve of that entry's fifteen rows
   therefore carry "none, not a replication", and the paper states a figure for
   six of them: rows 5 through 10, the two volatilities, the correlation, both
   risk splits and both Sharpe ratios. The other six are sub-windows, which the
   paper works no more than the book does.
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
the paper prints and computed nowhere in this repo.

| Figure | Value | Where |
| --- | --- | --- |
| Sample | 1983 to 2004, monthly | Tables 1 and 2 |
| Stock index | Russell 1000 | Table 2 |
| Bond index | Lehman Brothers Aggregate Bond Index | Table 2 |
| Return basis | excess over three-month Treasury bills | footnote 3 |
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
   from the rounding of 23 and 77, with no knowledge of the paper. Qian's
   measured volatility ratio of 3.2826 lands inside it.

## What it does not settle

The equity leg. Qian read the Russell 1000 and Entry 4 reads SPY, which tracks
the S&P 500.
[Issue 160](https://github.com/l3a0/quantitative-trading/issues/160) swaps in
IWB, which tracks his index and shares Entry 4's window, so that substitution
is measurable on free data.

The sample. His is 1983 to 2004 and Entry 4's is 2003 to 2026, and the two
share about fifteen months.
[Issue 161](https://github.com/l3a0/quantitative-trading/issues/161) reaches
his, and it is blocked on licensed index history.

## Provenance

| Field | Value |
| --- | --- |
| Source | `https://www.panagora.com/assets/PanAgora-Risk-Parity-Portfolios-Efficient-Portfolios-Through-True-Diversification.pdf` |
| Downloaded | 2026-09-18 |
| Bytes | 288,359 |
| sha256 | `d9b6a7185726767e36628c79ecbc006044e7da23f0f38f1cf04d71311fd0e7c2` |
| Copyright | PanAgora Asset Management, per the notice the document carries |

The checksum is recorded for the same reason a vintage carries one, so a reader
can tell this copy from a later revision. It is stated here rather than held by
a test, because nothing has replaced a paper yet and the counting rule in
[CLAUDE.md](../../CLAUDE.md) defers a guard on a path that has run zero times.
The file itself carries a 2011 copyright line and a `270416 9/11` document code,
so it is a reprint of the September 2005 paper rather than the original
release.

Verify it the same way the vintages are verified:

```bash
shasum -a 256 research/papers/qian-2005-risk-parity-portfolios.pdf
```
