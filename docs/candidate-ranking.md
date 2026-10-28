# Candidate ranking

This document ranks every strategy tested in this repository, and every search
in the sibling [trading-strategies](https://github.com/l3a0/trading-strategies),
by after-cost evidence on data no search had loaded. It answers
[issue 774](https://github.com/l3a0/quantitative-trading/issues/774), which the
owner set on 2026-10-28 with a pass mark fixed before any row was filled in.
The paper ledger of [issue 775](https://github.com/l3a0/quantitative-trading/issues/775)
runs whatever this ranking registers, and a placeholder until it registers
something.

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
- [The registration screen](#the-registration-screen)
- [What paper trading can show](#what-paper-trading-can-show)
- [What this ranking cannot say](#what-this-ranking-cannot-say)

## The result

**No row passes, and none is registered yet. Six rows wait only on data.**

1. **No row passes the pass mark.** A row passes with an after-cost t at 5 bp
   a side of at least t\* = 5.200, on a span no search had loaded. The only
   statistics in either repository on such a span are registered holdouts, and
   the largest of them is a bound of 3.70 before costs, on a series whose
   other bound is −4.96. Every other figure was computed on loaded data, so it
   cannot pass whatever its size.
2. **Six rows meet two of the three registration conditions.** Each has a
   positive Sharpe ratio after 5 bp a side and enough unloaded history that the
   ratio, if it held, would reach t\*. The third condition, that the data for
   that history can be bought, is not yet shown for any of them. They are one
   rule on two universes.
   1. Entry 44's reversal at the open on the S&P 600, at 2.0257 after costs,
      needs 6.59 of the 9.21 years from the index's launch to Chan's file.
   2. Entry 10's reversal at the open on the S&P 500, in five readings from
      1.0149 to 1.3997 after costs. Its rule A at 1.3997 needs 13.80 of the
      32.89 years before Chan's file, and the lowest reading needs 26.25.
3. **Sixteen more rows could become registrable once measured at 5 bp a side.**
   Their Sharpe ratios before costs, carried over the history no search loaded,
   reach t\*. None has an after-cost figure.

[Issue 777](https://github.com/l3a0/quantitative-trading/issues/777) carries
both open steps. It finds out whether the data for the six can be bought, and
measures the sixteen. A registration there names its rule,
parameters and span before any statistic on that span is computed.

All six rows that wait on data are one reversal rule, on spans before 2004
that overlap its published record. Two readings of the method also decide a
row each. [What the owner rules on](#what-the-owner-rules-on) sets out all
three.

The owner's private economic test applies on top of this one. A row that
passed here would be necessary rather than sufficient.

## The pass mark

The pass mark is the issue's, and the method that applies it was posted as
[a comment on the issue](https://github.com/l3a0/quantitative-trading/issues/774#issuecomment-6481756644)
before any row was computed. In short:

1. **The adjustment is Bonferroni.** A row passes when its after-cost t reaches
   the t whose one-sided normal tail equals the tail at t = 2 divided by N.
   That tail is 0.02275, so at N variants the hurdle is
   t\* = Φ⁻¹(1 − 0.02275 / N).
2. **The t is the entry's own pinned t at 5 bp a side.** Where only a Sharpe
   ratio is pinned, t is the annualized Sharpe ratio times the root of the
   span's years. Where no after-cost figure is pinned, the before-cost t is an
   upper bound.
3. **Only a span no search loaded counts.** A registered holdout counts when
   its rule and span were written down before it first ran. A figure on a span
   in-sample to the book that printed it fails, whatever its t.
4. **A row is registered only if a holdout test could pass.** That needs a
   positive after-cost Sharpe ratio, an unloaded span whose data exists or can
   be bought, and enough of that span for the Sharpe ratio, held exactly, to
   reach t\*.

"No search loaded" here means no run in either repository computed a
statistic from the instrument's or universe's data over that span. A file read
whole and cut before any statistic does not spend its other years, which is how
Entry 51's registered holdout read its own span. A span before a vendor file
starts counts, and so does a span after it ends. Where an instrument has
several such spans, they join into one holdout. Both of those are readings,
and [What the owner rules on](#what-the-owner-rules-on) names the row each
decides.

Bonferroni was chosen because it needs only N and holds under any dependence
among the variants. The price is power. Cells of one grid are strongly
correlated, so Bonferroni treats them as independent looks and can fail a real
but modest edge.

## How the variants were counted

**N = 228,274 variants across both repositories, which puts t\* at 5.200.**

A variant is one combination of rule, parameters, instrument or universe, and
span whose trading return was computed. A cell rerun at another cost is the
same variant. A computation that measures no return, such as a stationarity
test, is none. When it was unclear, the cell counted.

| Source | Variants | What dominates it |
| --- | --- | --- |
| This repository, Entries 1 to 52 | 221,302 | Entry 34's two scans, 220,104 between them |
| `trading-strategies` | 6,972 | walk-forward grids counted once per training window |
| **Both** | **228,274** | |

Entry 34's scans make up 96 percent of N. They searched 172,056 start and end
windows, and a grid of up to 48,048 parameter cells, for the run behind the
book's printed figures, rather than for an edge. The grid's count is the
product of the ranges the replication log states, since the log gives no count
of cells that ran. The counting rules still count both scans, because each
computed a return on each cell.

The per-entry counts are `REPO_VARIANTS` in
[tests/test_candidate_ranking.py](../tests/test_candidate_ranking.py). The
largest after Entry 34 are Entry 16 at 803, from a 400-cell grid scored on both
its training and test spans, and Entry 36 at 100, most of them scratch runs
before its rule was declared. Entries 44 and 50 count only the cells they add,
2 and 6, because each reruns cells an earlier entry counted.

The sibling's count is `SIBLING_SEARCHES` in the same file:

| Sibling search | Variants |
| --- | --- |
| Support and resistance catalog | 384 |
| Real-chain covered call | 152 |
| Registered put credit spread | 142 |
| Structure campaign and LLM proposer | 82 |
| Factor panel | 63 |
| Generative search | 56 |
| Intraday breakout continuation | 46 |
| Covered call in R-multiples, and the NVDA and GLD coda | 42 |
| Proxy covered call | 36 |
| QQQ one-day wheel | 30 |
| Volatility premium | 20 |
| Volume-profile reversal | 20 |
| Gap E, Gap G and the call-spread exits | 16 |
| Cup-and-handle scan | 12 |
| Random-entry replication | 3 |
| **Once per instrument and span** | **1,104** |
| Walk-forward grids once per training window, adding | 5,847 |
| Conditioning splits | 21 |
| **Total** | **6,972** |

The two grids are the covered call's 141 cells, which become 2,952 evaluations
across their training windows, and the put credit spread's 138, which become
3,174. The ledgers were deduplicated on template, parameters and ticker, which
leaves the edge ledger's 63 cells all inside the idea ledger's 82. The 1,260 or
so placebo and random-entry draws are null runs rather than variants anyone
could pick, and are left out.

The pass verdict does not depend on these choices. Dropping Entry 34's scans,
and counting the sibling's grids once per instrument and span, leaves
N = 2,302 and t\* = 4.268. No row passes at that hurdle either, and the largest
t at 5 bp a side on any span is 2.0217. The lower hurdle does widen the
registration screen, which
[What this ranking cannot say](#what-this-ranking-cannot-say) states.

## The ranking

The columns are the seven the issue fixes, plus the row and where it stands.
"Book" means the Chan book whose example the row reproduces. "Not stated"
means neither the entry nor its source says. Column 4 gives the span no search
loaded, and
[The registration screen](#the-registration-screen) gives each one's years.

### Rows with an after-cost figure at 5 bp a side

Ranked by t after costs. Every Sharpe ratio converts to t over its span in
`TestTheAfterCostRows`.

| Row | 1. Sharpe and t, before and after 5 bp a side | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays, and why a fund cannot take it | 6. Capacity | 7. Holding and trades | Stands |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry 44, Khandani-Lo reversal at the open, Chan's S&P 600 file | 5.3052, t 5.2947. Then 2.0257, t 2.0217 | no, the book's 2006, on a survivor file | 2 new | the S&P 600 from its 1994-10-28 launch to 2004-01-14 | The book says most of the returns come from small and microcap stocks. Inference: traders who need to trade now pay the liquidity provider, and a large fund would pay more than 5 bp a side in small caps, which the log says a flat 5 bp flatters | no estimate, the file holds no market values | one day, rebalanced daily, turnover 1.4505 to 1.4729 a day | waits on data |
| Entry 50, the same rule on an S&P 600 rebuilt from Alpha Vantage | 4.5808, t 4.5717. Then 1.6903, t 1.6869 | no, 2006 | 6 new | as above | as Entry 44 | no estimate | one day, daily | needs 9.46 of 9.21 years |
| Entry 10, rule A, S&P 500 at the open | 2.3818, t 2.3771. Then 1.3997, t 1.3969. Without the forward fill 1.0335, and the three steps between rule B and rule A 1.0149 to 1.0314 | no, the book's 2006 | 13 | S&P 500 members before 1999-11-24 | The book attributes Khandani and Lo's returns to small caps. Not stated for the S&P 500 | no estimate | one day, daily | waits on data |
| Entry 19, row 10, the first book's rule on the 2012 panel | 1.2219, t 2.7323. Then 0.3797, t 0.8490 | no, the second book's 2007 to 2011 | 6 | as Entry 10 | as Entry 10 | no estimate | one day, daily | needs 187.55 of 32.89 years |
| Entry 10, rule B, S&P 500 at the open | 4.4202, t 4.4114. Then 0.8293, t 0.8277 | no, 2006 | in Entry 10's 13 | as Entry 10 | as Entry 10 | no estimate | one day, daily | needs 39.32 of 32.89 years |
| Entry 50, Khandani-Lo at the open, S&P 400 | 3.4533, t 3.4464. Then 0.4884, t 0.4874 | no, 2006 | in Entry 50's 6 | the S&P 400 from its 1991 launch, outside 2006 and 2016 on | as Entry 44 | no estimate | one day, daily | needs 113.36 of 23.45 years |
| Entry 50, the rebuilt S&P 600 at the close | 3.5194, t 3.5124. Then 0.0575, t 0.0574 | no, 2006 | in Entry 50's 6 | as Entry 44 | as Entry 44 | no estimate | one day, daily | far short |
| Entry 44, Chan's S&P 600 file at the close | 3.4086, t 3.4018. Then −0.3255 | no, 2006 | in Entry 44's 2 | as Entry 44 | as Entry 44 | no estimate | one day, daily | negative after costs |
| Sibling, volatility premium, SPY 0.25Δ short call, delta-hedged | Sharpe 0.52 (`docs/vol_premium.md:209`) and Newey-West t +2.54 gross. t −0.35 at 5 bp (`docs/vol_premium.md:147-148`) | no, exploratory | in the 20 | SPY chains from their 2005-01-10 listing to 2007-12-31, if bought. The sibling's early walk-forwards trained on 2008 on | the doc names an index correlation risk premium (`docs/vol_premium.md:178-180`). Why not a fund: not stated | not stated. t falls below zero between 2 bp and 5 bp | 30 days to expiry, about 11 cycles a year | negative after costs |
| Entry 50, S&P 400 at the close | 2.0338, t 2.0298. Then −1.4524 | no, 2006 | in Entry 50's 6 | as Entry 50 | as Entry 44 | no estimate | one day, daily | negative after costs |
| Entry 8, Khandani-Lo at the close, S&P 500 | 0.2510, t 0.2505. Then −3.2337 | no, the book's 2006 | 1 | as Entry 10 | as Entry 10 | no estimate | one day, daily | negative after costs |

"0.25Δ" names an option whose price moves 0.25 for each 1 the underlying moves.

### Rows with an after-cost figure only at a lower cost

None was run at 5 bp a side. A cost of 5 bp a side is at least as large as the
cost in each figure here, so each after-cost figure is an upper bound on its
figure at 5 bp.

| Row | 1. Sharpe and t, before and after the cost shown | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays, and why a fund cannot take it | 6. Capacity | 7. Holding and trades | Stands |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sibling, generative search, SPY 0.05Δ short call, 30 days | Sharpe 0.688, Newey-West t +3.35 at a 1 bp hedge (`data/gen_ledger.jsonl:62`). The doc reads it as the best of about 131 noise draws (`docs/generative_search.md:57-61`) | no | 56 of its 70 cells, the ones that traded | as above | not stated | not stated | 30 days, about 12 a year | needs 57.12 of 2.97 years |
| Sibling, structure campaign, SPY 0.25Δ short call | t +2.17 (`data/idea_ledger.jsonl:26`) and Sharpe 0.436 (the regenerable `data/edge_ledger.jsonl:5`), at the 1 bp hedge cost the `short_vol` structure defaults to in `realchains/vol_premium.py`. e-LOND, the sibling's false-discovery control, flags 0 of 63 (`docs/edge_search.md:589-590`) | no | 82 with the proposer's 19 | as above | not stated | not stated | 30 days, about 12 a year | lower than the cell above |
| Sibling, LLM proposer, SPY short calls | t +2.17 at 21 days and 0.15Δ, +2.03 at 45 days and the money (`data/idea_ledger.jsonl:67`, `:60`), at the same 1 bp | no | inside the 82 | as above | not stated | not stated | 21 and 45 days | lower than the cell above |
| Entry 41, VX against ES on VX's roll return | 1.030894 before any cost, 1.002020 under the script's 1 bp | no, the book's 2010 to 2012 | 3 | VX from its 2004-03-26 launch to 2004-05-31, and VX and ES from 2012-05-09 | not stated | no estimate | one day a signal, 224 of 448 test days held | needs 25.44 of 14.57 years |
| Entry 16, Conditional Parameter Optimization on GLD and GDX minutes, the unconditional arm | 5.700 before costs, −7.614 at 1 bp a round trip. The conditional arm is 5.274 and −6.122 | no, the book's 2018 to 2020 | 803 | GLD and GDX minutes from 2021, which the archive holds and no run has computed on | not stated | no estimate | intraday, 46.7 round trips a day | negative after costs |
| Sibling, registered put credit spread | t −2.26 on SPY and −2.51 on IWM at 0.5 bp (`docs/put_credit_spread_results.md:32-35`) | yes, registered and computed | 142 | none | not stated | not stated | about 11 spreads a year | negative |
| Sibling, real-chain covered call | no cell above t +0.73, the hedged MSFT book at mid fills. The unhedged MSFT book is at Newey-West t −1.73 at bid and ask fills (`README.md:81`, `docs/explorations.md:289-292`) | walk-forward only | 152 | none | not stated | not stated | about 18 calls a year | below t\* before costs |
| Sibling, volume-profile reversal, S&P 400 over 10 days | the trade earns +6.45 bp gross over 2016 to 2026, −2.16 bp over 2016 to 2021 and +16.11 bp over 2022 to 2026. Against a random-entry control the excess is +9.50 bp at Newey-West t 6.41 (`data/volume_profile_universe_results.json`, the `sp400` pool's `prior_lb20_b48_va70_s1_h10d` reversion cells) | the 2022 to 2026 holdout was computed, and the full span includes it | in the 20 | before 2016, if intraday bars are bought | not stated | not stated | 10 days | a 10 bp round trip exceeds the 6.45 bp trade |
| Sibling, intraday breakout continuation | +6.5 bp at touch fills, below an 8 to 15 bp round trip. Mean R −0.22 net of 10 bp (`docs/explorations.md:1299-1320`, `:1384-1388`) | no | 46 | before 2016, if bought | not stated | not stated | intraday | negative after costs |

### Registered holdouts

These are the only statistics in either repository computed on a span no
search had loaded when they ran. Each span is loaded now, so column 4 is
"none" throughout and is left out.

| Row | 1. The registered statistic | 2. Span | 3. Variants | 5. Who pays, and why a fund cannot take it | 6. Capacity | 7. Holding and trades | Stands |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Entry 7, Example 7.6, the January effect on IJR's point-in-time members | mean January return after costs between −0.1057 and 0.0869, as the missing members are read low or high. iid t between −4.96 and 3.70 before costs | Januaries of 2009 to 2026 | in Entry 7's 32 | not stated | no estimate | one month a year | the bounds disagree, and the high one needs 35.55 of 9.21 years |
| Sibling, straddle secondary on IWM | t +1.42 gross, +1.28 at 0.5 bp. SPY +0.90 and +0.72 (`docs/vol_premium.md:323-326`) | 2010-12-01 to 2026-06-05 | in the 20 | not stated | not stated | 30 days | needs 255.97 of at most 10.51 years |
| Sibling, registered put wing | IWM t +1.00 gross, +0.91 at 0.5 bp. SPY +0.20 and +0.09 (`docs/vol_premium.md:278-281`) | 2010-12-01 to 2026-06-05 | in the 20 | the registration's prior is a skew premium (`docs/prereg_vol_premium.md:112-118`) | not stated | 30 days | needs 506.44 of at most 10.51 years |
| Entry 51, Example 2.5 on USD/CAD after 2012 | Newey-West t 0.2670 before costs, Sharpe 0.0715 on raw P&L | 2012-03-29 to 2026-10-12 | 1 | not stated | no estimate | a position every day | needs 5,514.21 of 36.54 years before costs |
| Sibling, volume profile, NVDA continuation | t +0.03 gross on 2022 to 2026 (`docs/explorations.md:99-111`) | 2022 to 2026 | in the 20 | not stated | not stated | intraday | far short |
| Entry 7, Example 7.7 on IVV's members | Newey-West t −0.11 before costs | 2009-01 to 2026-09 | in Entry 7's 32 | not stated | no estimate | one month, 12 a year | negative |
| Entry 49, levered low beta against high beta on IVV | Newey-West t −0.4974 on the gap, before costs | 2009-01 to 2026-04 | 3 | not stated. The book's premise is that low beta earns a higher Sharpe ratio | no estimate | one month, 12 a year | negative |
| Sibling, registered trend gate | killed at its first stage, one-sided p 0.736 (`docs/trend_gate_results.md:123-126`) | 2010 to 2026 by ticker | 2 conditioning tests | not stated | not stated | conditions a short call | negative |

### Rows with no after-cost figure

The before-cost Sharpe ratio is an upper bound on the after-cost one. A row
whose unloaded history is too short even for that bound fails whatever its
costs. A row whose history is long enough goes to
[issue 777](https://github.com/l3a0/quantitative-trading/issues/777) for an
after-cost figure.

| Row | 1. Sharpe before costs | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays, and why a fund cannot take it | 6. Capacity | 7. Holding and trades | Stands |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Entry 19, Example 4.4, open to close | 4.713284 | no, the second book's 2007 to 2011 | in Entry 19's 6 | as Entry 10 | as Entry 10 | no estimate | open to close, twice a day | measure |
| Entry 32, Kalman filter hedge on EWA and EWC | 2.36116164 | no, the book's 2006 to 2012 | 3 | EWA and EWC from their 1996 launch to 2006-04-25, and from 2012-04-10 | not stated | no estimate | units change 875 times in 1,499 days | measure |
| Entry 36, TU on the lagged roll return | 1.803348 | no, the book's file, declared after about 90 scratch runs | 100 | TU from 2012-08-14 | not stated | no estimate | 21 position changes in 913 days | measure |
| Entry 18, buy on gap and its mirror | 1.5371 and 1.7853 | no, the book's 2006 to 2012 | 4 | as Entry 10 | not stated | no estimate | open to close | measure |
| Entry 46 and Entry 12, post-earnings drift | 1.2815 to 1.7045 across ten runs, and 1.4909 | no, the book's 2011 to 2012 | 18 | as Entry 10, with earnings dates bought | not stated | no estimate | open to close, 25 to 55 positions on the busiest day | measure |
| Entry 25, AUD.USD against CAD.USD | 1.6108902337 | no, the book's 2009 to 2012 | 2 | both rates from the Australian dollar's float on 1983-12-12 to 2007-07-20 | not stated | no estimate | rebalanced daily | measure |
| Entry 35, VX calendar spread B3 | 1.457009 | no, the book's 2008 to 2012 | 10 | as Entry 41 | not stated | no estimate | about monthly, reversing on 109 days | measure |
| Entry 40, the opening gap on FSTX | 1.441620 | no, the book's 2004 to 2012 | 10 | FSTX from its 1998-06-22 launch to 2004-07-06, and from 2012-05-18 | the book names stops triggered by the gap. The return that reproduces fades the gap | no estimate | open to close, long on 278 and short on 191 of 2,000 days | measure |
| Entry 47, buy on gap under a VIX filter | 1.417425 | no | 11 | as Entry 10 | not stated | no estimate | open to close | measure |
| Entry 28, VX against ES | 1.393201 | no, the book's 2010 to 2012 | 7 | as Entry 41 | not stated | no estimate | four positions in 449 days | measure |
| Entry 23, Johansen portfolio of EWA, EWC and IGE | 1.3913100883 | no, the book's 2006 to 2012 | 1 | IGE's 2001-10-22 launch to 2006-04-25, and from 2012-04-10 | not stated | no estimate | re-set daily | measure |
| Entry 34, CL 12-month calendar spread | 1.278216 | no, the book's 2008 to 2012 | 220,111 | CL from its 1983-03-30 launch to 1986-11-02, and from 2012-08-14 | not stated | no estimate | pairs held at least 63 days | measure, if 12-month spreads traded before 1986 and the spans join |
| Entry 19, Example 4.3, close to close | 1.259478 | no, 2007 to 2011 | in Entry 19's 6 | as Entry 10 | as Entry 10 | no estimate | one day | measure |
| Entry 31, CL reversal joined to momentum | 1.100368 | no | 11 | as Entry 34 | not stated | no estimate | in the market on 157 of 1,000 days | needs 22.33 of 17.72 years |
| Entry 33 and Entry 37, TU momentum, 250-day lookback and 25-day hold | 1.041462, and an iid t of 2.933253 on holds that overlap | no, the book's 2004 to 2012 | 52 and 1 | as Entry 36 | not stated | no estimate | 25 days in daily tranches | needs 24.93 of 14.13 years |
| Entry 11, commodity seasonals | one ratio per yearly trade: natural gas 1.0008 over 1994 to 2008, gasoline 0.7764 | no | 2 | natural gas from its 1990 launch to 1993-12-19, gasoline from 1985 to 1994-03-31, before the fill test's April 1994, and both from 2024-04-06 | not stated | no estimate | one trade a year | natural gas needs 27.00 of 6.20 years, gasoline 44.86 of 11.72 |
| Entry 52, `MomSeasonShort` from Open Source Asset Pricing | 0.8096 over 1965 to 2024. Monthly t 8.63 over 1965 to 2002 and 0.50 over 2002 to 2024 | 2002 on is after the book | 7 | 1927 to 1964, in a committed file no run has computed on | not stated | no estimate | one month, 12 a year | needs 41.25 of 38.00 years |
| Entry 13, the PCA factor model | 0.5787 | no, the book's S&P 600 file | 11 | as Entry 44 | not stated | no estimate | one day | needs 80.74 of 9.21 years |
| Entry 30, AUD.CAD with rollover | 0.5418018005 | no | 3 | as Entry 25 | not stated | no estimate | daily sign | needs 92.11 of 23.60 years |
| Entry 17, cross-sectional momentum | −0.4800 over every day of its three windows, 2007-05-15 to 2012-04-24 | no | 16 | as Entry 10 | not stated | no estimate | 25 days in daily cohorts | negative |
| Entry 24, SPY against a 98-stock basket | 1.3193972970 | no, the book's 2008 to 2012 | 1 | none, Entries 3 and 4 load SPY from 1993 to 2026 | not stated | no estimate | re-set daily | no unloaded span |
| Entry 39, XLE against USO by contango | 1.046596 | no | 5 | none, the sibling's XLE chains load XLE through 2026 | not stated | no estimate | held through the window | no unloaded span |
| Entry 26, Bollinger bands on GLD and USO | 0.964673 | no | 2 | none, Entry 1 loads GLD through 2026 | not stated | no estimate | 162 changes in 5.9 years | no unloaded span |
| Entry 21, GLD and USO price spread | 0.589651 | no | 7 | none, as Entry 26 | not stated | no estimate | daily | no unloaded span |
| Entry 22, USD.CAD linear mean reversion | 0.1188463477 | no, 2008 to 2012 | 1 | 1971-01-04 to 2007-07-21 | not stated | no estimate | daily | needs 1,914.39 of 36.54 years |
| Entry 48 and Entry 45, low beta at a broker's leverage | Newey-West t 1.0715 and 1.2111 on the gap, before costs | no, the book's 2000 to 2007 | 5 | as Entry 10 | not stated. The book's premise is that low beta earns a higher Sharpe ratio | no estimate | one month, 12 a year | needs 127.51 of 32.89 years at the higher t |
| Entry 4, risk parity against 60/40 | 60/40 at 0.4111, levered risk parity at 0.1942 | mostly after Qian's 1983 to 2004 sample | 13 | none, Entries 3 and 4 load SPY and AGG starts in 2003 | not stated | no estimate | constant weights, daily | no unloaded span |
| Entry 14, the momentum factor | plain t 0.4505 | no | 2 | as Entry 10 | not stated | no estimate | one month | needs 921.53 of 32.89 years |
| Entry 7, Example 7.6 on IJR survivors | mean January 0.0098 after costs, t 1.15 before costs over 18 Januaries | after the book, but survivor-only | in Entry 7's 32 | as Entry 44 | not stated | no estimate | one month a year | needs 368.03 of 9.21 years |
| Entry 7, Example 7.7 on Chan's file | −0.1243 | no | in Entry 7's 32 | as Entry 10 | not stated | no estimate | one month | negative |
| Entry 35, VX calendar spread S | −0.563912 | no | in Entry 35's 10 | as Entry 35 B3 | not stated | no estimate | pairs held at least 63 days | negative |
| Entry 38, long GLD and short gold futures | −0.066564 over a 2 percent bill | no | 5 | none, as Entry 26 | the book: the roll return less GLD's financing, "close to zero" | no estimate | held through the window | negative |
| Entry 9, the survivorship toy | a one-year return from printed tables | no | 5 | not applicable | not applicable | not applicable | one year | a toy, not a strategy |
| Entry 3, Kelly leverage on buy-and-hold SPY | SPY at 0.4313 over a 4 percent rate | no | 6 | not applicable | the equity premium | not applicable | buy and hold | a benchmark, not a strategy |

Entries 1, 2, 5, 6, 15, 20, 27, 29, 42 and 43 measure no strategy return. They
compute stationarity tests, simulations, roll-return estimates and leverage
arithmetic, and count no variants.

### The sibling's other searches

| Search | 1. The best figure | 2. Out of sample? | 3. Variants | 4. Span no search loaded | 5. Who pays | 6. Capacity | 7. Holding | Stands |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Covered call in R-multiples | daily t +1.25 at most, with no hedge cost (`docs/explorations.md:680`, `:699`) | no | 42 with the coda | as the volatility premium | not stated | not stated | 30 days | needs 268.41 of 2.97 years |
| Gap G, portfolio combinations | t 1.54 against its better leg's 2.47, and 1.01 against 2.56 (`docs/explorations.md:403-410`) | no | inside Gap E, G and the exits' 16 | as above | not stated | not stated | 30 days | needs 176.84 of 2.97 years |
| QQQ one-day wheel | negative on all 48 cells. The hedged companion's +2.40 charges the hedge nothing (`docs/explorations.md:922-933`, `:978-988`) | no | 30 | not worked out | not stated | not stated | one day, about 124 sales a year | negative, and the companion is not screened |
| Factor panel, 63 information coefficients | Newey-West \|t\| 1.52, with no cost and on a coefficient rather than a return (`docs/factor_real_panel.md:44-45`) | no | 63 | not assessed | not stated | not stated | one day | below t\* before costs |
| Proxy covered call | Newey-West t +0.46 on simulated chains (`README.md:50-52`) | walk-forward only | 36 | not applicable | not stated | not stated | about 18 calls a year | below t\* |
| Support and resistance catalog | 0 of 384 cells beat random entry (`docs/explorations.md:1095-1107`) | no | 384 | not assessed | not stated | not stated | by horizon | no edge |
| Cup-and-handle scan | below the random null at every horizon (`docs/explorations.md:1503-1510`) | no | 12 | not assessed | not stated | not stated | by horizon | no edge |
| Exit and sizing studies, random-entry replication | expectancy in R rather than a t. The best is +0.0011R pooled over 195,900 trades (`docs/explorations.md:488-501`) | no | inside the 16, and 3 | not assessed | not stated | not stated | a median of about 40 days | no t to test |

## The registration screen

A holdout can pass only if the years it covers are enough for the row's Sharpe
ratio to reach t\*. Held exactly, a Sharpe ratio S reaches t\* after
(t\* / S)² years, and a t of t measured over Y years reaches it after
Y × (t\* / t)² years. `TestTheScreen` screens every positive row this way
except six kinds.

1. A row another row of the same search dominates, with a lower figure on the
   same span. That covers the structure campaign and the LLM proposer under the
   generative cell, Entry 37 under Entry 33, the SPY legs of the straddle and
   put wing under their IWM legs, and Gap G's 1.01 under its 1.54.
2. A figure that is not a return, the factor panel's coefficient.
3. A figure from simulated rather than traded prices, the proxy covered call.
4. A row that fails on cost by arithmetic, the volume-profile reversal.
5. The QQQ wheel's hedged companion, whose hedge is charged nothing and whose
   unloaded span has not been worked out.
6. A row with no unloaded span, which the tables mark "none" or "not
   applicable": Entries 3, 4, 9, 21, 24, 26 and 39, and the sibling's
   real-chain covered call.

Entry 46's eight middle runs are not listed either. Each lies between its
lowest and highest runs on the same span, and the lowest already reaches t\*.

Each Sharpe ratio is after 5 bp a side where one is pinned, and before costs
otherwise.

| Row | Sharpe | After costs? | Years available | Years needed | Stands |
| --- | --- | --- | --- | --- | --- |
| Entry 44, S&P 600 at the open | 2.0257 | yes | 9.21 | 6.59 | waits on data |
| Entry 10, rule A at the open | 1.3997 | yes | 32.89 | 13.80 | waits on data |
| Entry 10, rule A without the fill | 1.0335 | yes | 32.89 | 25.32 | waits on data |
| Entry 10, third step from rule B to rule A | 1.0314 | yes | 32.89 | 25.42 | waits on data |
| Entry 10, second step | 1.0307 | yes | 32.89 | 25.45 | waits on data |
| Entry 10, first step | 1.0149 | yes | 32.89 | 26.25 | waits on data |
| Entry 50, rebuilt S&P 600 at the open | 1.6903 | yes | 9.21 | 9.46 | short |
| Entry 10, rule B at the open | 0.8293 | yes | 32.89 | 39.32 | short |
| Entry 50, S&P 400 at the open | 0.4884 | yes | 23.45 | 113.36 | short |
| Entry 19, row 10 | 0.3797 | yes | 32.89 | 187.55 | short |
| Entry 19, Example 4.4 | 4.713284 | no | 32.89 | 1.22 | measure |
| Entry 32, Kalman EWA and EWC | 2.36116164 | no | 24.57 | 4.85 | measure |
| Entry 36, TU on the roll | 1.803348 | no | 14.13 | 8.31 | measure |
| Entry 18, short on gap | 1.7853 | no | 32.89 | 8.48 | measure |
| Entry 46, drift run B1 | 1.7045 | no | 32.89 | 9.31 | measure |
| Entry 25, AUD.USD and CAD.USD | 1.6108902337 | no | 23.60 | 10.42 | measure |
| Entry 18, buy on gap | 1.5371 | no | 32.89 | 11.44 | measure |
| Entry 12, drift | 1.4909 | no | 32.89 | 12.16 | measure |
| Entry 35, VX B3 | 1.457009 | no | 14.57 | 12.74 | measure |
| Entry 40, FSTX | 1.441620 | no | 20.41 | 13.01 | measure |
| Entry 47, buy on gap under VIX | 1.417425 | no | 32.89 | 13.46 | measure |
| Entry 28, VX against ES | 1.393201 | no | 14.57 | 13.93 | measure |
| Entry 23, EWA, EWC and IGE | 1.3913100883 | no | 18.98 | 13.97 | measure |
| Entry 46, drift run A_U | 1.2815 | no | 32.89 | 16.47 | measure |
| Entry 34, CL calendar spread | 1.278216 | no | 17.72 | 16.55 | measure |
| Entry 19, Example 4.3 | 1.259478 | no | 32.89 | 17.05 | measure |
| Entry 31, CL | 1.100368 | no | 17.72 | 22.33 | short |
| Entry 33, TU momentum | 1.041462 | no | 14.13 | 24.93 | short |
| Entry 41, VX on the roll | 1.030894 | no | 14.57 | 25.44 | short |
| Entry 11, natural gas | 1.0008 | no | 6.20 | 27.00 | short |
| Entry 11, gasoline | 0.7764 | no | 11.72 | 44.86 | short |
| Entry 52, `MomSeasonShort` | 0.8096 | no | 38.00 | 41.25 | short |
| Sibling, generative 0.05Δ call | 0.688 | no | 2.97 | 57.12 | short |
| Entry 13, PCA factor model | 0.5787 | no | 9.21 | 80.74 | short |
| Entry 30, AUD.CAD | 0.5418018005 | no | 23.60 | 92.11 | short |
| Entry 22, USD.CAD | 0.1188463477 | no | 36.54 | 1,914.39 | short |

The rows pinned as a t, each in `TestTheScreen::test_each_row_pinned_as_a_t`, are all short. The nearest is the registered January effect's high bound, which needs 35.55 of 9.21 years.

The sixteen rows to measure are thirteen entries, since Entries 18, 19 and 46
each appear twice.

Four things bound the "years available" column.

1. **The S&P 500 span is an upper bound.** Norgate sells point-in-time S&P 500
   membership with delisted stocks, reported to reach 1967
   ([a Wealth-Lab forum post](https://wl6.wealth-lab.com/Forum/Posts/Survivorship-bias-Delisted-symbols-Historical-index-components-33495)).
   Its opening prices may not reach as far back as its membership, and every
   S&P 500 row but Example 4.3 trades at the open.
2. **The S&P 600 span is partly held and partly to be bought.** The Alpha
   Vantage `sp600` cross-section holds 1999-11-01 onward, survivors only.
   Entry 50 reads it whole and cuts it to 2006, and no run has computed a
   statistic on its years before 2004. No vendor has been
   found for 1994-10-28 to 1999-10-31 with point-in-time members and opens.
3. **CL's early span assumes 12-month spreads.** NYMEX crude oil futures began
   on 1983-03-30, and whether contracts a year apart traded before 1986 is not
   checked.
4. **Several start dates come from outside this repository.** No file here
   records the launches of EWA, EWC, IGE, IWM, FSTX, CL, VX, natural gas
   futures, NVDA's listing, SPY's options, the S&P 600 or the S&P 400, nor the
   Australian dollar's float on 1983-12-12 or FRED's 1971 start for daily US
   dollar rates. IWM's span starts at the fund's launch, so its options' years
   are an upper bound.

### What the owner rules on

Three questions decide rows and are not settled by the method's text. Each was
seen after the rows were, so each is the owner's to rule on rather than this
ranking's.

1. **Whether a span inside the rule's published record counts.** All six rows
   that wait on data test Lo and MacKinlay's contrarian weighting, published
   in 1990. Khandani and Lo ran it on daily returns of US stocks from January
   1995 to August 2007 and reported its returns year by year
   ([the paper's page](https://web.mit.edu/%7Ealo/www/Papers/august07.html)),
   and the first book quotes their 2006 figure of 4.47. They report it earning
   the most early in that span and decaying towards 2007. Entry 44's span,
   1994-10-28 to 2004-01-14, lies almost wholly inside it, and so do the last
   five years of Entry 10's. A pass on those years would say little about
   trading the rule now. Excluding Khandani and Lo's years decides Entry 44.
   Entry 10 keeps 27.99 years before 1995, enough for every one of its
   readings, so it turns on Lo and MacKinlay's sample too, which this ranking
   has not checked.
   `TestTheScreen::test_khandani_and_los_sample_alone_leaves_entry_10_its_years`
   pins it. The method excludes only
   spans in-sample to the book that printed a figure, and Chan's books printed
   none of these years, so it does not exclude them.
2. **Whether a file read whole spends its other years.** The method says
   "loaded". This ranking reads that as a statistic computed, which is how
   Entry 51's registered holdout treated reads that computed nothing. Under
   the other reading, Entry 50's whole read of the Alpha Vantage `sp600` file
   spends 1999-11-01 onward, Entry 44's span shrinks to 5.01 years and it no
   longer reaches the 6.59 it needs.
   `TestTheScreen::test_the_s_and_p_600_row_turns_on_what_loaded_means` pins
   both.
3. **Whether separate unloaded spans join into one holdout.** The method says
   "a span". Joining decides one row, Entry 34's CL calendar spread, whose
   14.13 years after 2012 fall short of the 16.55 it needs and whose 17.72
   joined years do not. `TestTheScreen::test_the_cl_row_turns_on_joining_spans`
   pins it.

[Issue 777](https://github.com/l3a0/quantitative-trading/issues/777) asks for
these rulings before it registers anything. It also carries this ranking's
proposal for choosing among rows that qualify, by the largest ratio of years
available to years needed, which is an addition the owner approves or replaces.

The readings matter at the narrow hurdle too. Of the two rows it would add to
the rows to measure, Entry 31 reaches only on the joined CL span, and Entry
52's 1927 to 1964 sits in a file Entry 52 read whole.

## What paper trading can show

The span after today is the one span no search can have loaded, so it is the
one every row has. It is slow. Held exactly, a row's after-cost Sharpe ratio
reaches t\* after (t\* / Sharpe)² years of forward data:

| Row | After-cost Sharpe | Years to reach t\* = 5.200 |
| --- | --- | --- |
| Entry 44, S&P 600 at the open | 2.0257 | 6.6 |
| Entry 50, rebuilt S&P 600 at the open | 1.6903 | 9.5 |
| Entry 19, row 10 | 0.3797 | 187.6 |

So the paper ledger of [issue 775](https://github.com/l3a0/quantitative-trading/issues/775)
can kill a candidate quickly and confirm one only over years. That holds for
every row here.

## What this ranking cannot say

1. **Whether any of the sixteen rows survives costs, and whether the data for
   the six can be bought.** That is
   [issue 777](https://github.com/l3a0/quantitative-trading/issues/777).
2. **Whether the counting rules are right.** N moves by two orders of
   magnitude between the rules and the narrowest reading, and t\* moves from
   5.200 to 4.268. No row passes at either hurdle. The lower one would add
   Entry 31 and Entry 52 to the rows to measure, and Entry 50's rebuilt S&P 600
   and Entry 10's rule B to the rows that wait on data, which
   `TestTheScreen::test_the_narrow_hurdle_adds_four_rows` pins.
3. **Whether a row that passed would be worth trading.** The owner's economic
   test, capacity at the owner's size and costs above 5 bp a side all sit
   outside this pass mark.
4. **Anything about the sibling after `7a26498`.** Its searches continue, and a
   later count would move N. Re-measure against a newer commit rather than
   editing a cell.
