# Candidate ranking

This document ranks every strategy tested in this repository, and every search
in the sibling [trading-strategies](https://github.com/l3a0/trading-strategies),
by after-cost evidence on data no search had loaded. It answers
[issue 774](https://github.com/l3a0/quantitative-trading/issues/774), which the
owner set on 2026-10-28 with a pass mark fixed before any row was filled in.
The paper ledger of [issue 775](https://github.com/l3a0/quantitative-trading/issues/775)
runs whatever this document names, and a placeholder until it names something.

It is read at `6da0ee38` here and `7a26498` in the sibling. Every figure is
either quoted from the test or sibling file that pins it, which the row names,
or derived from those figures in
[tests/test_candidate_ranking.py](../tests/test_candidate_ranking.py), which
pins the arithmetic.

## Contents

- [The result](#the-result)
- [The pass mark](#the-pass-mark)
- [How the variants were counted](#how-the-variants-were-counted)
- [The ranking](#the-ranking)
- [Why nothing is registered](#why-nothing-is-registered)
- [What paper trading can show](#what-paper-trading-can-show)
- [What this ranking cannot say](#what-this-ranking-cannot-say)

## The result

**No row clears, and no row is registered.**

1. **No row clears the pass mark.** A row passes with an after-cost t at 5 bp a
   side of at least t* = 5.200, on a span no search had loaded. The only
   statistics in either repository that sit on such a span are registered
   holdouts, and the largest of them is a bound of 3.70 before costs, on a
   series whose other bound is −4.96. Every other figure was computed on
   loaded data, so it cannot pass whatever its size.
2. **No row can be registered on the evidence pinned today.** Registration
   needs a positive after-cost Sharpe ratio and an unloaded span long enough
   that the Sharpe ratio, if it held, would reach t*. Every row with a pinned
   after-cost figure fails one of those.
3. **Eight rows could become registrable once measured.** Their Sharpe ratios
   before costs, carried over a span no search loaded, reach t*. None of the
   eight has an after-cost figure, so none can be judged yet.
   [Issue 777](https://github.com/l3a0/quantitative-trading/issues/777) measures
   them and registers the first that qualifies, or records that none does.

The strongest after-cost row is the Khandani-Lo reversal traded at the open
on S&P 600 members, at a Sharpe ratio of 2.0257 after 5 bp a side. It is one
year, 2006, on a survivor file the book's own example used, and the reasons it
is not registered are under
[The S&P 600 row](#the-sp-600-row-turns-on-one-judgement).

The owner's private economic test applies on top of this one. A row that
passed here would be necessary rather than sufficient.

## The pass mark

The pass mark is the issue's, and the method that applies it was posted as
[a comment on the issue](https://github.com/l3a0/quantitative-trading/issues/774#issuecomment-6481756644)
before any row was computed. In short:

1. **The adjustment is Bonferroni.** A row passes when its after-cost t reaches
   the t whose one-sided normal tail equals the tail at t = 2 divided by N.
   That tail is 0.02275, so at N variants the hurdle is
   t* = Φ⁻¹(1 − 0.02275 / N).
2. **The t is the entry's own pinned t at 5 bp a side.** Where only a Sharpe
   ratio is pinned, t is the annualized Sharpe ratio times the root of the
   span's years. Where no after-cost figure is pinned, the before-cost t is an
   upper bound.
3. **Only a span no search loaded counts.** A registered holdout counts when
   its rule and span were written down before it first ran. The method says a
   span in-sample to the book that printed a figure does not count. This
   ranking reads that as the publication that printed the rule's results,
   which matters for one row, as
   [The S&P 600 row](#the-sp-600-row-turns-on-one-judgement) explains.
4. **A row is registered only if a holdout test could pass.** That needs a
   positive after-cost Sharpe ratio, an unloaded span whose data exists or can
   be bought, and an after-cost Sharpe ratio times the root of that span's
   years at or above t*.

Bonferroni was chosen because it needs only N and holds under any dependence
among the variants. The price is power. Cells of one grid are strongly
correlated, so Bonferroni treats them as independent looks and can fail a real
but modest edge.

## How the variants were counted

**N = 228,274 variants across both repositories, which puts t* at 5.200.**

A variant is one combination of rule, parameters, instrument or universe, and
span whose trading return was computed. A cell rerun at another cost is the
same variant. A computation that measures no return, such as a stationarity
test, is none. When it was unclear, the cell counted.

| Source | Variants | What dominates it |
| --- | --- | --- |
| This repository, Entries 1 to 52 | 221,302 | Entry 34's two scans, 220,104 between them |
| `trading-strategies` | 6,972 | walk-forward grids counted once per training window, 6,951, plus 21 conditioning splits |
| **Both** | **228,274** | |

Entry 34's scans make up 96 percent of N. They searched 172,056 start and end
windows, and a grid of up to 48,048 parameter cells, for the run behind the
book's printed figures, rather than for an edge. The grid's count is the
product of the ranges the replication log states, since the log gives no count
of cells that ran. The counting rules still count both scans, because each
computed a return on each cell.

The verdict does not depend on that choice. Dropping both scans, and counting
the sibling's grids once per instrument and span rather than once per training
window, leaves N = 2,302 and t* = 4.268. No row clears at that hurdle either,
and the largest t at 5 bp a side on any span is 2.0217. The lower hurdle
widens the registration screen, which
[What this ranking cannot say](#what-this-ranking-cannot-say) states.

The per-entry counts are `REPO_VARIANTS` in
[tests/test_candidate_ranking.py](../tests/test_candidate_ranking.py), and the
sibling's per-search counts are column 3 of its rows below. The
largest in this repository after Entry 34 are Entry 16 at 803, from a 400-cell
grid scored on both its training and test spans, and Entry 36 at 100, most of
them scratch runs before its rule was declared. Placebo and random-entry draws
in the sibling, about 1,260 of them, are null runs rather than variants anyone
could pick, and are left out.

## The ranking

The columns are the seven the issue fixes, plus the row and the condition each
row fails on. "Book" means the Chan book whose example the row reproduces.
"Not stated" means neither the entry nor its source says.

### Rows with an after-cost figure at 5 bp a side

Ranked by after-cost t. Every Sharpe ratio converts to t over its span in
`TestTheAfterCostRows`.

| Row | 1. Sharpe, before and after 5 bp a side, and t | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays, and why a fund cannot take it | 6. Capacity | 7. Holding and trades | Fails on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry 44, Khandani-Lo at the open, S&P 600 file | 5.3052, then 2.0257. t 2.0217 | no, the book's 2006, on a survivor file | 4 | none, as [below](#the-sp-600-row-turns-on-one-judgement) | The book says most of the returns come from small and microcap stocks. Inference: traders who need to trade now pay the liquidity provider, and a large fund pays more than 5 bp a side in small caps, which the log says a flat 5 bp flatters | no estimate, the file holds no market values | one day, rebalanced daily, turnover 1.4505 to 1.4729 a day | no unloaded span |
| Entry 50, the same rule on an S&P 600 rebuilt from Alpha Vantage | 4.5808, then 1.6903. t 1.6869 | no, 2006 | 6 new | none, as above | as above | no estimate | one day, daily | no unloaded span |
| Entry 10, rule A, S&P 500 at the open | 2.3818, then 1.3997. t 1.3969 | no, the book's 2006 | 13 | S&P 500 opens from about 1992-07 to 1994-12, if bought | as Entry 44 | no estimate | one day, daily | product 2.21, below t* |
| Entry 19, row 10, the first book's rule on the 2012 panel | 1.2219, then 0.3797. t 0.8490 | no, the second book's 2007 to 2011 | 6 | S&P 500 closes for 1988 to 1994, between the two published samples, if bought | as Entry 44 | no estimate | one day, daily | product below t* |
| Entry 10, rule B, S&P 500 at the open | 4.4202, then 0.8293. t 0.8277 | no, 2006 | in Entry 10's 13 | as rule A | as Entry 44 | no estimate | one day, daily | product below t* |
| Entry 50, Khandani-Lo at the open, S&P 400 | 3.4533, then 0.4884. t 0.4874 | no, 2006 | in Entry 50's 6 | 2008-01 to 2015-12 | as Entry 44 | no estimate | one day, daily | product below t* |
| Entry 50, the rebuilt S&P 600 at the close | 3.5194, then 0.0575. t 0.0574 | no, 2006 | in Entry 50's 6 | none | as Entry 44 | no estimate | one day, daily | product below t* |
| Entry 44, S&P 600 file at the close | 3.4086, then −0.3255 | no, 2006 | in Entry 44's 4 | none | as Entry 44 | no estimate | one day, daily | negative after costs |
| Sibling, volatility premium, SPY 0.25Δ short call, delta-hedged | Sharpe 0.52 and Newey-West t +2.54 gross. t −0.35 at 5 bp (`docs/vol_premium.md:147-148`) | no, exploratory | about 20 | SPY chains before 2010, which the sibling's data holds only with placeholder greeks | the doc names an index correlation risk premium (`docs/vol_premium.md:178-180`). Why not a fund: not stated | not stated. t falls below zero between 2 bp and 5 bp | 30 days to expiry, about 11 cycles a year | negative after costs |
| Entry 50, S&P 400 at the close | 2.0338, then −1.4524 | no, 2006 | in Entry 50's 6 | 2008-01 to 2015-12 | as Entry 44 | no estimate | one day, daily | negative after costs |
| Entry 8, Khandani-Lo at the close, S&P 500 | 0.2510, then −3.2337 | no, the book's 2006 | 1 | S&P 500 closes for 1988 to 1994, if bought | as Entry 44 | no estimate | one day, daily | negative after costs |

### Rows with an after-cost figure only at a lower cost

None was run at 5 bp a side. A cost of 5 bp a side is at least as large as the
cost in each figure here, so each after-cost figure is an upper bound on its
figure at 5 bp.

| Row | 1. Sharpe and t, before and after the cost shown | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays | 6. Capacity | 7. Holding and trades | Fails on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sibling, generative search, SPY 0.05Δ short call, 30 days | Sharpe 0.688, Newey-West t +3.35 at a 1 bp hedge (`data/gen_ledger.jsonl:62`). The doc reads it as the best of about 131 noise draws (`docs/generative_search.md:57-61`) | no | 56 with a return | SPY chains from 1996 to 2010, if bought | not stated | not stated | 30 days, about 12 a year | product 2.66 over those 14.90 years, below t* |
| Sibling, structure campaign, SPY 0.25Δ short call | Sharpe 0.436, t +2.17 at 1 bp (`data/idea_ledger.jsonl:26`). e-LOND flags 0 of 63 | no | 82 with the proposer's 19 | as above | not stated | not stated | 30 days, about 12 a year | product below t* |
| Sibling, LLM proposer, SPY short calls | t +2.17 at 21 days and 0.15Δ, +2.03 at 45 days and the money, both at 1 bp (`data/idea_ledger.jsonl:67`, `:60`) | no | inside the 82 | as above | not stated | not stated | 21 and 45 days | product below t* |
| Entry 41, VX against ES on VX's roll return | 1.030894 before any cost, 1.002020 under the script's 1 bp | no, the book's 2010 to 2012 | 3 | VX and ES after 2012-05-08 | not stated | no estimate | one day a signal, 224 of 448 test days held | product 3.91 before the 1 bp, below t* |
| Entry 16, Conditional Parameter Optimization on GLD and GDX minutes | 5.700 before costs, −7.614 at 1 bp a round trip | no, the book's 2018 to 2020 | 803 | GLD and GDX minutes from 2021-01-01, which the archive holds | not stated | no estimate | intraday, 46.7 round trips a day | negative after costs |
| Sibling, registered put credit spread | t −2.26 on SPY and −2.51 on IWM at 0.5 bp (`docs/put_credit_spread_results.md:32-35`) | yes, registered and computed | 142 | none | not stated | not stated | about 11 spreads a year | negative |
| Sibling, real-chain covered call | no cell above t +0.73, which is the hedged MSFT book at mid fills. MSFT naive t −1.73 at bid and ask fills (`README.md:81`, `docs/explorations.md:289-292`) | walk-forward only | 152 | none | not stated | not stated | about 18 calls a year | negative |
| Sibling, volume-profile reversal, S&P 400 over 10 days | the trade earns +6.45 bp gross over 2016 to 2026, −2.16 bp over 2016 to 2021 and +16.11 bp over 2022 to 2026. Against a random-entry control the excess is +9.50 bp at Newey-West t 6.41 (`data/volume_profile_universe_results.json`, the `sp400` pool's `prior_lb20_b48_va70_s1_h10d` reversion cells) | the 2022 to 2026 holdout was computed, and the full span includes it | 20 | before 2016, if intraday bars are bought | not stated | not stated | 10 days | a 10 bp round trip exceeds the 6.45 bp full-span trade |
| Sibling, intraday breakout continuation | +6.5 bp at touch fills, below an 8 to 15 bp round trip. Mean R −0.22 net of 10 bp (`docs/explorations.md:1299-1320`, `:1384-1388`) | no | 46 | not assessed | not stated | not stated | intraday | negative after costs |

### Registered holdouts

These are the only statistics in either repository computed on a span no
search had loaded when they ran. Each is now loaded.

| Row | 1. The registered statistic | 2. Span | 3. Variants | 5. Who pays | 7. Holding and trades | Fails on |
| --- | --- | --- | --- | --- | --- | --- |
| Entry 7, Example 7.6, the January effect on IJR's point-in-time members | mean January return after costs between −0.1057 and 0.0869, as the missing members are read low or high. iid t between −4.96 and 3.70 before costs | Januaries of 2009 to 2026 | in Entry 7's 32 | not stated | one month a year | the bounds disagree, and 3.70 is below t* |
| Entry 51, Example 2.5 on USD/CAD after 2012 | Newey-West t 0.2670 before costs, Sharpe 0.0715 on raw P&L | 2012-03-29 to 2026-10-12 | 1 | not stated | a position every day | t below t* before any cost |
| Entry 7, Example 7.7 on IVV's members | Newey-West t −0.11 before costs | 2009-01 to 2026-09 | in Entry 7's 32 | not stated | one month, 12 a year | negative |
| Entry 49, levered low beta against high beta on IVV | Newey-West t −0.4974 on the gap, before costs | 2009-01 to 2026-04 | 3 | not stated | one month, 12 a year | negative |
| Sibling, registered put wing, IWM arm | t +0.91 at 0.5 bp (`docs/vol_premium.md:278-281`) | 2010-12-01 to 2026-06-05 | in the 20 | crash insurance, per the registration | 30 days | t below t* |
| Sibling, volume profile, NVDA continuation | t +0.03 gross on 2022 to 2026 (`docs/explorations.md:99-111`) | 2022 to 2026 | in the 20 | not stated | intraday | t below t* |

### Rows with no after-cost figure

The before-cost Sharpe ratio is an upper bound on the after-cost one. Where that
bound, times the root of the years of an unloaded span, is below t*, the row
fails whatever its costs. Where it reaches t*, the row is one of the eight
[issue 777](https://github.com/l3a0/quantitative-trading/issues/777) measures.
Every product is pinned in `TestTheScreen`.

| Row | 1. Sharpe before costs | 2. Out of sample? | 3. Variants | 4. Span no search loaded, and its product | 5. Who pays | 6. Capacity | 7. Holding and trades | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry 32, Kalman filter hedge on EWA and EWC | 2.36116164 | no, the book's 2006 to 2012 | 3 | 2012-04-10 on, 14.47 years. Product 8.98 | not stated | no estimate | units change 875 times in 1,499 days | measure, [issue 777](https://github.com/l3a0/quantitative-trading/issues/777) |
| Entry 25, AUD.USD against CAD.USD | 1.6108902337 | no, the book's 2009 to 2012 | 2 | 1971-01-04 to 2007-07-20, 36.54 years. Product 9.74 | not stated | no estimate | rebalanced daily | measure |
| Entry 19, Example 4.4, open to close | 4.713284 | no, the second book's 2007 to 2011 | in Entry 19's 6 | about 1992-07 to 1994-12, 2.50 years, if bought. Product 7.45 | as Entry 44 | no estimate | open to close, twice a day | measure |
| Entry 36, TU on the lagged roll return | 1.803348 | no, the book's file, declared after about 90 scratch runs | 100 | 2012-08-14 on, 14.13 years. Product 6.78 | not stated | no estimate | 21 position changes in 913 days | measure |
| Entry 35, VX calendar spread B3 | 1.457009 | no, the book's 2008 to 2012 | 10 | 2012-05-08 on, 14.40 years. Product 5.53 | not stated | no estimate | about monthly, reversing on 109 days | measure |
| Entry 40, the opening gap on FSTX | 1.441620 | no, the book's 2004 to 2012 | 10 | 2012-05-18 on, 14.37 years. Product 5.46 | the book names stops triggered by the gap. The return that reproduces fades the gap | no estimate | open to close, long on 278 and short on 191 of 2,000 days | measure |
| Entry 23, Johansen portfolio of EWA, EWC and IGE | 1.3913100883 | no, the book's 2006 to 2012 | 1 | 2012-04-10 on, 14.47 years. Product 5.29 | not stated | no estimate | re-set daily | measure |
| Entry 28, VX against ES | 1.393201 | no, the book's 2010 to 2012 | 7 | 2012-05-09 on, 14.39 years. Product 5.29 | not stated | no estimate | four positions in 449 days | measure |
| Entry 34, CL 12-month calendar spread | 1.278216 | no, the book's 2008 to 2012 | 220,111 | 2012-08-14 on. Product 4.80 | not stated | no estimate | pairs held at least 63 days | product below t* |
| Entry 31, CL reversal joined to momentum | 1.100368 | no | 11 | 2012-05-05 on. Product 4.18 | not stated | no estimate | in the market on 157 of 1,000 days | product below t* |
| Entry 33, TU momentum, 250-day lookback and 25-day hold | 1.041462, and an iid t of 2.933253 on holds that overlap | no, the book's 2004 to 2012 | 52 | 2012-08-14 on. Product 3.91 | not stated | no estimate | 25 days in daily tranches | product below t* |
| Entry 52, `MomSeasonShort` from Open Source Asset Pricing | 0.8096 over 1965 to 2024. t 8.63 over 1965 to 2002 and 0.50 over 2002 to 2024, monthly | 2002 on is after the book | 7 | 1927 to 1964, 38.00 years. Product 4.99 | not stated | no estimate | one month, 12 a year | product below t* |
| Entry 18, buy on gap and its mirror | 1.5371 and 1.7853 | no, the book's 2006 to 2012 | 4 | S&P 500 opens before 1995, about 2.5 years. Product 2.82 for the mirror | not stated | no estimate | open to close | product below t* |
| Entry 46 and Entry 12, post-earnings drift | 1.2815 to 1.7045 across ten runs | no, the book's 2011 to 2012 | 18 | as Entry 18. Product 2.69 for the best run | not stated | no estimate | open to close, 30 to 55 positions on the busiest day | product below t* |
| Entry 47, buy on gap and FSTX under a VIX filter | 1.417425 and 0.164869 | no | 11 | as Entry 18 and Entry 40 | not stated | no estimate | open to close | product below t* |
| Entry 24, SPY against a 98-stock basket | 1.3193972970 | no, the book's 2008 to 2012 | 1 | none, Entry 3 loads SPY from 1993 | not stated | no estimate | re-set daily | no unloaded span |
| Entry 19, Example 4.3, close to close | 1.259478 | no, 2007 to 2011 | in Entry 19's 6 | S&P 500 closes for 1988 to 1994, if bought. Product 3.33 | as Entry 44 | no estimate | one day | product below t* |
| Entry 17, cross-sectional momentum | 4.0657 in 2007, −1.2930 in 2008 to 2009, 0.2004 in 2010 to 2012 | no | 16 | S&P 500 closes before 1999-11, if bought | not stated | no estimate | 25 days in daily cohorts | no full-span figure is pinned, and the later two windows sit at or below 0.20 |
| Entry 39, XLE against USO by contango | 1.046596 | no | 5 | none, the sibling's XLE chains load XLE through 2026 | not stated | no estimate | held through the window | no unloaded span |
| Entry 26, Bollinger bands on GLD and USO | 0.964673 | no | 2 | none, Entry 1 loads GLD through 2026 | not stated | no estimate | 162 changes in 5.9 years | no unloaded span |
| Entry 13, the PCA factor model | 0.5787 | no, the book's S&P 600 file | 11 | S&P 600 before 2004, 9.28 years. Product 1.76 | not stated | no estimate | one day | product below t* |
| Entry 21, GLD and USO price spread | 0.589651 | no | 7 | none, as Entry 26 | not stated | no estimate | daily | no unloaded span |
| Entry 30, AUD.CAD with rollover | 0.5418018005 | no | 3 | 1971-01-04 to 2007-07-20, as Entry 25. Product 3.28 | not stated | no estimate | daily sign | product below t* |
| Entry 22, USD.CAD linear mean reversion | 0.1188463477 | no, 2008 to 2012 | 1 | before 2007-08, as Entry 30 | not stated | no estimate | daily | product below t* |
| Entry 48 and Entry 45, low beta at a broker's leverage | Newey-West t 1.0715 and 1.2111 on the gap, before costs | no, the book's 2000 to 2007 | 5 | S&P 500 before 1999-11, if bought | not stated. The book's premise is that low beta earns a higher Sharpe ratio | no estimate | one month, 12 a year | Entry 49's registered holdout of the same rule came back at −0.4974 |
| Entry 4, risk parity against 60/40 | 60/40 at 0.4111, levered risk parity at 0.1942 | mostly after Qian's 1983 to 2004 sample | 13 | none, Entry 3 loads SPY from 1993 and AGG starts in 2003 | not stated | no estimate | constant weights, daily | the ranking went against the book, t −2.1727 |
| Entry 11, commodity seasonals | one ratio per yearly trade, 1.0008 for natural gas over 1994 to 2008 | no | 2 | natural gas from 1990-04 to 1993-12, 3.75 years. Product 1.94 | not stated | no estimate | one trade a year | product below t* |
| Entry 14, the momentum factor | plain t 0.4505 | no | 2 | as Entry 48 | not stated | no estimate | one month | t below t* before costs |
| Entry 7, Example 7.6 on IJR survivors | mean January 0.0098 after costs, t 1.15 before costs over 18 Januaries | after the book, but survivor-only | in Entry 7's 32 | before 2004-01, as Entry 13. Product 0.83 at the same rate | not stated | no estimate | one month a year | product below t* |
| Entry 7, Example 7.7 on Chan's file | −0.1243 | no | in Entry 7's 32 | before 1999-11 | not stated | no estimate | one month | negative |
| Entry 35, VX calendar spread S | −0.563912 | no | in Entry 35's 10 | as Entry 35 B3 | not stated | no estimate | pairs held at least 63 days | negative |
| Entry 38, long GLD and short gold futures | −0.066564 over a 2 percent bill | no | 5 | none, as Entry 26 | the book: the roll return less GLD's financing, "close to zero" | no estimate | held through the window | negative |
| Entry 9, the survivorship toy | a one-year return from printed tables | no | 5 | not applicable | not applicable | not applicable | one year | a toy, not a strategy |
| Entry 3, Kelly leverage on buy-and-hold SPY | SPY at 0.4313 over a 4 percent rate | no | 6 | not applicable | the equity premium | not applicable | buy and hold | a benchmark, not a strategy |

Entries 1, 2, 5, 6, 15, 20, 27, 29, 42 and 43 measure no strategy return. They
compute stationarity tests, simulations, roll-return estimates and leverage
arithmetic, and count no variants.

The sibling's other searches either measured no return or nothing positive. Its
factor panel tested 63 information coefficients, the strongest at Newey-West t
1.52, with no cost (`docs/factor_real_panel.md:6`). Its support and resistance
catalog found 0 of 384 cells beating random entry
(`docs/explorations.md:1095-1107`). Its cup-and-handle scan fell below the
random null at every horizon (`docs/explorations.md:1503-1510`). Its QQQ
one-day wheel was negative on all 48 cells, and the hedged companion's t of
+2.40 charges the hedge nothing (`docs/explorations.md:922-933`, `:978-988`).
Its proxy covered call reached Newey-West t +0.46 (`README.md:50-52`). The
covered call in R-multiples reaches a daily t of +1.25 at most
(`docs/explorations.md:620-628`). The portfolio combinations of its Gap G fall
below their better leg, 1.54 against 2.47 and 1.01 against 2.56, where the legs
are volatility-premium cells before any hedge cost
(`docs/explorations.md:403-410`). Its exit and sizing studies and its
random-entry replication report expectancy in R rather than a t, and the best
of them is +0.0011R pooled over 195,900 trades
(`docs/explorations.md:488-501`).

## Why nothing is registered

Every row with a pinned after-cost figure fails one of the three registration
conditions, as the tables above say. Two rows need more than a table cell.

### The S&P 600 row turns on one judgement

Entry 44's reversal at the open on the S&P 600 file is the strongest
after-cost row, at 2.0257 on 2006. Its universe's spans divide into four, and
whether any of them is unloaded is the one place where a judgement rather than
a figure decides the outcome.

1. **2004-01-15 to 2008-01-14** is Chan's own S&P 600 file, which Entries 7,
   13, 42 and 44 read.
2. **2007-12-01 to 2026-10-02** is the Alpha Vantage `sp600` cross-section,
   which Entry 7's January runs read.
3. **1999-11-01 to 2004-01-14** is in the same cross-section and no run here
   computed a statistic on it. It holds only the stocks that were IJR members
   in 2007 or later, so it would be a survivor-only test.
4. **1994-10 to 1999-10** is in no file here and would have to be bought, with
   point-in-time members and the prices of stocks since delisted.

Spans 3 and 4 fall inside the sample of the paper that printed the rule's
results. Khandani and Lo's "What Happened to the Quants in August 2007?" runs
this contrarian rule on daily returns of US stocks from January 1995 to August
2007 and reports its returns year by year
([the paper's page](https://web.mit.edu/%7Ealo/www/Papers/august07.html)), and
the first book quotes their 2006 figure of 4.47. Their universe is all US
stocks rather than the S&P 600, but it contains the S&P 600, and the book's
own explanation is that the small and microcap stocks carried their returns.
So this ranking reads 1995 to 2004 as in-sample for the rule's source and
counts neither span as unloaded. That leaves the row with no unloaded span.

The other reading changes the answer, so it is stated rather than left for a
reviewer to find. Counted as unloaded, span 4 joined to span 3 runs from
1994-10-03 to 2004-01-14, 9.28 years. Chan's file's 2.0257 times the root of
that is 6.17, which clears t*. The rebuilt control's 1.6903 gives 5.15, which
does not, and `TestTheScreen::test_the_s_and_p_600_row_turns_on_the_span_alone`
pins both. Three things weigh against registering it under that reading, even
so.

1. **The 2.0257 is the more flattering of two measurements of one year.** Both
   are survivor files, and the one rebuilt from the vendor the holdout would
   use is the one that falls short.
2. **A flat 5 bp a side flatters small caps,** which the log says of this
   very row.
3. **The answer on 1995 to 2003 is close to known.** Khandani and Lo report
   the rule at its strongest in those years and decaying towards 2007, so a
   test there could pass and still say nothing about trading it now.

The owner can overrule the reading on the pull request. If the owner does, the
row is registered on 1994-10-03 to 2004-01-14 with bought point-in-time data,
on Chan's file's rule and parameters, before any statistic on that span is
computed.

### Seasonal momentum fails before any cost

Entry 52's `MomSeasonShort` series holds 1927 to 1964 in a committed file that
no run has computed a statistic on, 38.00 years. Its Sharpe ratio before costs
over the 1965 to 2024 span Entry 52 read is 0.8096, so even with no cost the
product is 4.99, below t*. Its returns since 2002 are not detectable above
zero, at t 0.50 before costs. `TestTheSeasonalMomentumRow` measures the
Sharpe ratio after dropping every month before 1965, so the earlier span stays
unread.

## What paper trading can show

The span after today is the one span no search can have loaded, so it is the
one every row has. It is slow. If a row's after-cost Sharpe ratio held exactly,
the years of forward data before its t reached t* are (t* / Sharpe)²:

| Row | After-cost Sharpe | Years to reach t* = 5.200 |
| --- | --- | --- |
| Entry 44, S&P 600 at the open | 2.0257 | 6.6 |
| Entry 50, rebuilt S&P 600 at the open | 1.6903 | 9.5 |
| Entry 19, row 10 | 0.3797 | 187.6 |

So the paper ledger of [issue 775](https://github.com/l3a0/quantitative-trading/issues/775)
can kill a candidate quickly and confirm one only over years. That holds for
every row here.

## What this ranking cannot say

1. **Whether any of the eight rows survives costs.** That is
   [issue 777](https://github.com/l3a0/quantitative-trading/issues/777).
2. **Whether the counting rules are right.** N moves by two orders of
   magnitude between the rules and the narrowest reading, and t* moves from
   5.200 to 4.268. No row clears at either hurdle. The lower one would add
   two rows to the eight to measure, Entry 34 at a product of 4.80 and
   Entry 52 at 4.99, and would let the rebuilt S&P 600 control's 5.15 clear
   under the reading this ranking rejects.
3. **Whether a row that passed would be worth trading.** The owner's economic
   test, capacity at the owner's size and costs above 5 bp a side all sit
   outside this pass mark.
4. **Anything about the sibling after `7a26498`.** Its searches continue, and a
   later count would move N. Re-measure against a newer commit rather than
   editing a cell.
