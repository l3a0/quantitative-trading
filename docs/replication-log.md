# Replication log

A replication is finished when it reaches a verdict. Until then the repo holds
a reproduced experiment, which is a number sitting next to another number with
nobody saying what the pair means.

This file is where the verdicts live. One entry per replication, apart from
the one exception the paragraphs below name, and one row per published result, carrying the five parts
[docs/design.md](design.md#vocabulary) defines: the published figure, the
vintage, what this repo computed, the gap, and the verdict. A row usually
matches one published figure to one computation. Four of Entry 1's rows do not,
and each says so in its own cells.

1. Row 2 carries no published figure, because the book prints no
   with-intercept slope.
2. Row 5 reproduces one published figure from two vintages at once.
3. Row 10 carries no published figure, because the book stops in 2007.
4. Row 11 covers the two statistics Chan printed from what he read as one
   disagreement, and they come from two different tests.

Entries 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37 and 38 carry their own, three, eleven, twelve, five,
six, one, three, eight, six, two, eight, seven, twelve, six, two, five, three,
three, three, seven, six, seven, three, four, five, seven, eight, five, twelve, seven, eight, four, eight, eight, four and five, and they are listed in those entries rather than here, because the list is about an entry's rows and not
about the file.

Entry 5 is the one entry that is not a replication. Chan states the claim it
tests without printing a number, so it carries a finding rather than a verdict,
and its tables drop the columns that would hold a published figure, a gap and a
verdict. Entries 6 and 15 come from the same sentence of the book and are
replications, because the claim each tests is about a series Chan names or a
class whose members are tested directly.

Every result in Entries 1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38 and 39 is **exploratory** in the design
doc's sense. Reproducing a published figure spends the sample on a hypothesis
someone else already chose, and testing a claim the source states does the same, so an
entry can say whether the number reproduces or the claim holds on its vintage
and nothing about whether the trade works today. Entry 7's rows 35 to 49 are
the one exception, and they are **registered**: their claim, test and verdict
wording were written before any return was computed. Entries 2 and 9 spend no
sample at all and are outside that label and its opposite both, which each
states rather than picking one. Entry 20 works arithmetic on inputs the book
states and is outside both for the same reason, which its first conclusion
says.

## Contents

- [How to read an entry](#how-to-read-an-entry)
  - [Two traceability rules](#two-traceability-rules)
  - [What precision a number is quoted at](#what-precision-a-number-is-quoted-at)
  - [How a verdict is chosen](#how-a-verdict-is-chosen)
  - [Rows that are not replications](#rows-that-are-not-replications)
  - [What a second entry does to this file](#what-a-second-entry-does-to-this-file)
- [Entry 1: GLD/GDX and KO/PEP, Chan's *Quantitative Trading*](#entry-1-gldgdx-and-kopep-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed)
  - [What this repo computed](#what-this-repo-computed)
  - [The verdicts](#the-verdicts)
  - [What the entry concludes](#what-the-entry-concludes)
  - [Which lag count the residuals allow](#which-lag-count-the-residuals-allow)
  - [Two counts and two senses of one word](#two-counts-and-two-senses-of-one-word)
  - [What the citations do not cover](#what-the-citations-do-not-cover)
  - [The chapter labels are first-edition shorthand](#the-chapter-labels-are-first-edition-shorthand)
  - [Nothing checks this file's numbers against the suite](#nothing-checks-this-files-numbers-against-the-suite)
- [Entry 2: the coin-flip gamble, Chan's *Quantitative Trading*](#entry-2-the-coin-flip-gamble-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-1)
  - [What this repo computed](#what-this-repo-computed-1)
  - [The verdicts](#the-verdicts-1)
  - [What the entry concludes](#what-the-entry-concludes-1)
  - [Why no simulated number is pinned against the book](#why-no-simulated-number-is-pinned-against-the-book)
- [Entry 3: Kelly leverage on SPY, Chan's *Quantitative Trading*](#entry-3-kelly-leverage-on-spy-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-2)
  - [What this repo computed](#what-this-repo-computed-2)
  - [The verdicts](#the-verdicts-2)
  - [What the entry concludes](#what-the-entry-concludes-2)
  - [What this entry cannot say](#what-this-entry-cannot-say)
- [Entry 4: risk parity against 60/40, Chan's *Quantitative Trading*](#entry-4-risk-parity-against-6040-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-3)
  - [What this repo computed](#what-this-repo-computed-3)
  - [The verdicts](#the-verdicts-3)
  - [What the entry concludes](#what-the-entry-concludes-3)
  - [What this entry cannot say](#what-this-entry-cannot-say-1)
- [Entry 5: the fixed-income candidate, Chan's *Quantitative Trading*](#entry-5-the-fixed-income-candidate-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated)
  - [What this repo computed](#what-this-repo-computed-4)
  - [What each row says](#what-each-row-says)
  - [What the entry concludes](#what-the-entry-concludes-4)
  - [What this entry cannot say](#what-this-entry-cannot-say-2)
- [Entry 6: the CAD/AUD cross rate, Chan's *Quantitative Trading*](#entry-6-the-cadaud-cross-rate-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-4)
  - [What this repo computed](#what-this-repo-computed-5)
  - [The verdicts](#the-verdicts-4)
  - [What the entry concludes](#what-the-entry-concludes-5)
  - [What this entry cannot say](#what-this-entry-cannot-say-3)
- [Entry 7: the equity seasonals, Chan's *Quantitative Trading*](#entry-7-the-equity-seasonals-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-5)
  - [What this repo computed](#what-this-repo-computed-6)
  - [The verdicts](#the-verdicts-5)
  - [What the entry concludes](#what-the-entry-concludes-6)
  - [What this entry cannot say](#what-this-entry-cannot-say-4)
- [Entry 8: the Khandani-Lo reversal, Chan's *Quantitative Trading*](#entry-8-the-khandani-lo-reversal-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-6)
  - [What this repo computed](#what-this-repo-computed-7)
  - [The verdicts](#the-verdicts-6)
  - [What the entry concludes](#what-the-entry-concludes-7)
  - [What this entry cannot say](#what-this-entry-cannot-say-5)
- [Entry 9: the survivorship toy, Chan's *Quantitative Trading*](#entry-9-the-survivorship-toy-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-7)
  - [What this repo computed](#what-this-repo-computed-8)
  - [The verdicts](#the-verdicts-7)
  - [What the entry concludes](#what-the-entry-concludes-8)
  - [What this entry cannot say](#what-this-entry-cannot-say-6)
- [Entry 10: the Khandani-Lo reversal at the open, Chan's *Quantitative Trading*](#entry-10-the-khandani-lo-reversal-at-the-open-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-8)
  - [What this repo computed](#what-this-repo-computed-9)
  - [The verdicts](#the-verdicts-8)
  - [What the entry concludes](#what-the-entry-concludes-9)
  - [What this entry cannot say](#what-this-entry-cannot-say-7)
- [Entry 11: the commodity seasonals, Chan's *Quantitative Trading*](#entry-11-the-commodity-seasonals-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-9)
  - [What this repo computed](#what-this-repo-computed-10)
  - [The verdicts](#the-verdicts-9)
  - [What the entry concludes](#what-the-entry-concludes-10)
  - [What this entry cannot say](#what-this-entry-cannot-say-8)
- [Entry 12: post-earnings drift, Chan's *Algorithmic Trading*](#entry-12-post-earnings-drift-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-10)
  - [What this repo computed](#what-this-repo-computed-11)
  - [The verdicts](#the-verdicts-10)
  - [What the entry concludes](#what-the-entry-concludes-11)
  - [What this entry cannot say](#what-this-entry-cannot-say-9)
- [Entry 13: the PCA factor model, Chan's *Quantitative Trading*](#entry-13-the-pca-factor-model-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-11)
  - [What this repo computed](#what-this-repo-computed-12)
  - [The verdicts](#the-verdicts-11)
  - [What the entry concludes](#what-the-entry-concludes-12)
  - [What this entry cannot say](#what-this-entry-cannot-say-10)
- [Entry 14: the market and momentum factors, Chan's *Quantitative Trading*](#entry-14-the-market-and-momentum-factors-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-1)
  - [What this repo computed](#what-this-repo-computed-13)
  - [The verdicts](#the-verdicts-12)
  - [What the entry concludes](#what-the-entry-concludes-13)
  - [What this entry cannot say](#what-this-entry-cannot-say-11)
- [Entry 15: calendar spreads, Chan's *Quantitative Trading*](#entry-15-calendar-spreads-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-12)
  - [What this repo computed](#what-this-repo-computed-14)
  - [The verdicts](#the-verdicts-13)
  - [What the entry concludes](#what-the-entry-concludes-14)
  - [What this entry cannot say](#what-this-entry-cannot-say-12)
- [Entry 16: Conditional Parameter Optimization, Chan's *Quantitative Trading*](#entry-16-conditional-parameter-optimization-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-13)
  - [What this repo computed](#what-this-repo-computed-15)
  - [The verdicts](#the-verdicts-14)
  - [What the entry concludes](#what-the-entry-concludes-15)
  - [What this entry cannot say](#what-this-entry-cannot-say-13)
- [Entry 17: cross-sectional momentum, Chan's *Algorithmic Trading*](#entry-17-cross-sectional-momentum-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-14)
  - [What this repo computed](#what-this-repo-computed-16)
  - [The verdicts](#the-verdicts-15)
  - [The declared readings](#the-declared-readings)
  - [What the entry concludes](#what-the-entry-concludes-16)
  - [What this entry cannot say](#what-this-entry-cannot-say-14)
- [Entry 18: buy on gap and its mirror, Chan's *Algorithmic Trading*](#entry-18-buy-on-gap-and-its-mirror-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-15)
  - [What this repo computed](#what-this-repo-computed-17)
  - [The verdicts](#the-verdicts-16)
  - [What the entry concludes](#what-the-entry-concludes-17)
  - [What this entry cannot say](#what-this-entry-cannot-say-15)
- [Entry 19: the Khandani-Lo reversal on the 2012 panel, Chan's *Algorithmic Trading*](#entry-19-the-khandani-lo-reversal-on-the-2012-panel-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-16)
  - [What this repo computed](#what-this-repo-computed-18)
  - [The verdicts](#the-verdicts-17)
  - [Beside Entries 8 and 10](#beside-entries-8-and-10)
  - [What the entry concludes](#what-the-entry-concludes-18)
  - [What this entry cannot say](#what-this-entry-cannot-say-16)
- [Entry 20: constant leverage and capped Kelly allocation, Chan's *Algorithmic Trading*](#entry-20-constant-leverage-and-capped-kelly-allocation-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-17)
  - [What this repo computed](#what-this-repo-computed-19)
  - [The verdicts](#the-verdicts-18)
  - [What the entry concludes](#what-the-entry-concludes-19)
  - [What this entry cannot say](#what-this-entry-cannot-say-17)
- [Entry 21: price spread, log price spread and ratio, Chan's *Algorithmic Trading*](#entry-21-price-spread-log-price-spread-and-ratio-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-18)
  - [What this repo computed](#what-this-repo-computed-20)
  - [The verdicts](#the-verdicts-19)
  - [What the entry concludes](#what-the-entry-concludes-20)
  - [What this entry cannot say](#what-this-entry-cannot-say-18)
- [Entry 22: the stationarity tests on USD.CAD, Chan's *Algorithmic Trading*](#entry-22-the-stationarity-tests-on-usdcad-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-19)
  - [What this repo computed](#what-this-repo-computed-21)
  - [The verdicts](#the-verdicts-20)
  - [What the entry concludes](#what-the-entry-concludes-21)
  - [What this entry cannot say](#what-this-entry-cannot-say-19)
- [Entry 23: EWA, EWC and IGE, Chan's *Algorithmic Trading*](#entry-23-ewa-ewc-and-ige-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-20)
  - [What this repo computed](#what-this-repo-computed-22)
  - [The verdicts](#the-verdicts-21)
  - [What the entry concludes](#what-the-entry-concludes-22)
  - [What this entry cannot say](#what-this-entry-cannot-say-20)
- [Entry 24: SPY against its component stocks, Chan's *Algorithmic Trading*](#entry-24-spy-against-its-component-stocks-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-21)
  - [What this repo computed](#what-this-repo-computed-23)
  - [The verdicts](#the-verdicts-22)
  - [What the entry concludes](#what-the-entry-concludes-23)
  - [What this entry cannot say](#what-this-entry-cannot-say-21)
- [Entry 25: AUD.USD against CAD.USD, Chan's *Algorithmic Trading*](#entry-25-audusd-against-cadusd-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-22)
  - [What this repo computed](#what-this-repo-computed-24)
  - [The verdicts](#the-verdicts-23)
  - [What the entry concludes](#what-the-entry-concludes-24)
  - [What this entry cannot say](#what-this-entry-cannot-say-22)
- [Entry 26: Bollinger bands on GLD and USO, Chan's *Algorithmic Trading*](#entry-26-bollinger-bands-on-gld-and-uso-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-23)
  - [What this repo computed](#what-this-repo-computed-25)
  - [The verdicts](#the-verdicts-24)
  - [What the entry concludes](#what-the-entry-concludes-25)
  - [What this entry cannot say](#what-this-entry-cannot-say-23)
- [Entry 27: spot and roll returns of five futures, Chan's *Algorithmic Trading*](#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-24)
  - [What this repo computed](#what-this-repo-computed-26)
  - [The verdicts](#the-verdicts-25)
  - [What the entry concludes](#what-the-entry-concludes-26)
  - [What this entry cannot say](#what-this-entry-cannot-say-24)
- [Entry 28: VX futures against E-mini futures, Chan's *Algorithmic Trading*](#entry-28-vx-futures-against-e-mini-futures-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-25)
  - [What this repo computed](#what-this-repo-computed-27)
  - [The verdicts](#the-verdicts-26)
  - [What the entry concludes](#what-the-entry-concludes-27)
  - [What this entry cannot say](#what-this-entry-cannot-say-25)
- [Entry 29: GLD, GDX and USO around July 2008, Chan's *Algorithmic Trading*](#entry-29-gld-gdx-and-uso-around-july-2008-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-26)
  - [What this repo computed](#what-this-repo-computed-28)
  - [The verdicts](#the-verdicts-27)
  - [What the entry concludes](#what-the-entry-concludes-28)
  - [What this entry cannot say](#what-this-entry-cannot-say-26)
- [Entry 30: AUD.CAD with rollover interest, Chan's *Algorithmic Trading*](#entry-30-audcad-with-rollover-interest-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-27)
  - [What this repo computed](#what-this-repo-computed-29)
  - [The verdicts](#the-verdicts-28)
  - [What the entry concludes](#what-the-entry-concludes-29)
  - [What this entry cannot say](#what-this-entry-cannot-say-27)
- [Entry 31: crude oil reversal joined to momentum, Chan's *Algorithmic Trading*](#entry-31-crude-oil-reversal-joined-to-momentum-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-28)
  - [What this repo computed](#what-this-repo-computed-30)
  - [The verdicts](#the-verdicts-29)
  - [What the entry concludes](#what-the-entry-concludes-30)
  - [What this entry cannot say](#what-this-entry-cannot-say-28)
- [Entry 32: a Kalman filter hedge ratio on EWA and EWC, Chan's *Algorithmic Trading*](#entry-32-a-kalman-filter-hedge-ratio-on-ewa-and-ewc-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-29)
  - [What this repo computed](#what-this-repo-computed-31)
  - [The verdicts](#the-verdicts-30)
  - [What the entry concludes](#what-the-entry-concludes-31)
  - [What this entry cannot say](#what-this-entry-cannot-say-29)
- [Entry 33: time-series momentum on TU, Chan's *Algorithmic Trading*](#entry-33-time-series-momentum-on-tu-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-30)
  - [What this repo computed](#what-this-repo-computed-32)
  - [The verdicts](#the-verdicts-31)
  - [What the entry concludes](#what-the-entry-concludes-32)
  - [What this entry cannot say](#what-this-entry-cannot-say-30)
- [Entry 34: mean reversion on crude oil's 12-month calendar spread, Chan's *Algorithmic Trading*](#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-31)
  - [What this repo computed](#what-this-repo-computed-33)
  - [The verdicts](#the-verdicts-32)
  - [What the entry concludes](#what-the-entry-concludes-33)
  - [What this entry cannot say](#what-this-entry-cannot-say-31)
- [Entry 35: VIX futures calendar spreads on the ratio of back to front, Chan's *Algorithmic Trading*](#entry-35-vix-futures-calendar-spreads-on-the-ratio-of-back-to-front-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-32)
  - [What this repo computed](#what-this-repo-computed-34)
  - [The verdicts](#the-verdicts-33)
  - [What the entry concludes](#what-the-entry-concludes-34)
  - [What this entry cannot say](#what-this-entry-cannot-say-32)
- [Entry 36: TU momentum traded on the lagged roll return, Chan's *Algorithmic Trading*](#entry-36-tu-momentum-traded-on-the-lagged-roll-return-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-33)
  - [What this repo computed](#what-this-repo-computed-35)
  - [The verdicts](#the-verdicts-34)
  - [What the entry concludes](#what-the-entry-concludes-35)
  - [What this entry cannot say](#what-this-entry-cannot-say-33)
- [Entry 37: three hypothesis tests on TU momentum, Chan's *Algorithmic Trading*](#entry-37-three-hypothesis-tests-on-tu-momentum-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-34)
  - [What this repo computed](#what-this-repo-computed-36)
  - [The verdicts](#the-verdicts-35)
  - [What the entry concludes](#what-the-entry-concludes-36)
  - [What this entry cannot say](#what-this-entry-cannot-say-34)
- [Entry 38: long GLD and short gold futures, Chan's *Algorithmic Trading*](#entry-38-long-gld-and-short-gold-futures-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-35)
  - [What this repo computed](#what-this-repo-computed-37)
  - [The verdicts](#the-verdicts-36)
  - [What the entry concludes](#what-the-entry-concludes-37)
  - [What this entry cannot say](#what-this-entry-cannot-say-35)
- [Entry 39: XLE against USO signed by crude oil's contango, Chan's *Algorithmic Trading*](#entry-39-xle-against-uso-signed-by-crude-oils-contango-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-36)
  - [What this repo computed](#what-this-repo-computed-38)
  - [The verdicts](#the-verdicts-37)
  - [What the entry concludes](#what-the-entry-concludes-38)
  - [What this entry cannot say](#what-this-entry-cannot-say-36)

## How to read an entry

### Two traceability rules

The two columns of numbers come from different places, so one rule cannot cover
both.

1. **Every computed number names the assertion that holds it.** One test file
   per entry is the single authority for every figure that entry computes, and
   the computed column states those figures rather than deriving them.
   [tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py)
   holds Entry 1,
   [tests/test_coin_flip_growth.py](../tests/test_coin_flip_growth.py) holds
   Entry 2, and
   [tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py) holds
   Entry 3,
   [tests/test_risk_parity.py](../tests/test_risk_parity.py) holds Entry 4,
   [tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py)
   holds Entries 5, 6 and 15, which come from one sentence of the book and
   share a module,
   [tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) holds
   Entry 7, [tests/test_khandani_lo.py](../tests/test_khandani_lo.py) holds
   Entries 8 and 10, which are Examples 3.7 and 3.8 and share a module,
   [tests/test_survivorship_bias.py](../tests/test_survivorship_bias.py) holds
   Entry 9,
   [tests/test_commodity_seasonals.py](../tests/test_commodity_seasonals.py)
   holds Entry 11, [tests/test_pead.py](../tests/test_pead.py) holds
   Entry 12, [tests/test_pca_factor.py](../tests/test_pca_factor.py) holds
   Entry 13,
   [tests/test_momentum_factor.py](../tests/test_momentum_factor.py) holds
   Entry 14, [tests/test_cpo.py](../tests/test_cpo.py) holds Entry 16,
   whose pins run only where the owner's data archive is,
   [tests/test_cross_sectional_momentum.py](../tests/test_cross_sectional_momentum.py)
   holds Entry 17, [tests/test_buy_on_gap.py](../tests/test_buy_on_gap.py)
   holds Entry 18,
   [tests/test_khandani_lo_book_two.py](../tests/test_khandani_lo_book_two.py)
   holds Entry 19,
   [tests/test_kelly_allocation.py](../tests/test_kelly_allocation.py) holds
   Entry 20, [tests/test_price_spread.py](../tests/test_price_spread.py)
   holds Entry 21,
   [tests/test_usdcad_mean_reversion.py](../tests/test_usdcad_mean_reversion.py)
   holds Entry 22,
   [tests/test_etf_cointegration.py](../tests/test_etf_cointegration.py) holds
   Entry 23,
   [tests/test_index_arbitrage.py](../tests/test_index_arbitrage.py) holds
   Entry 24,
   [tests/test_aud_cad_johansen.py](../tests/test_aud_cad_johansen.py) holds
   Entry 25, [tests/test_bollinger.py](../tests/test_bollinger.py) holds
   Entry 26, [tests/test_roll_returns.py](../tests/test_roll_returns.py)
   holds Entry 27, [tests/test_vx_es.py](../tests/test_vx_es.py) holds
   Entry 28,
   [tests/test_gold_miners_oil.py](../tests/test_gold_miners_oil.py) holds
   Entry 29,
   [tests/test_aud_cad_rollover.py](../tests/test_aud_cad_rollover.py) holds
   Entry 30,
   [tests/test_cl_reversal_momentum.py](../tests/test_cl_reversal_momentum.py)
   holds Entry 31,
   [tests/test_kalman_hedge.py](../tests/test_kalman_hedge.py) holds
   Entry 32, [tests/test_tu_momentum.py](../tests/test_tu_momentum.py) holds
   Entry 33,
   [tests/test_calendar_spread_reversion.py](../tests/test_calendar_spread_reversion.py)
   holds Entry 34,
   [tests/test_vx_calendar_spread.py](../tests/test_vx_calendar_spread.py)
   holds Entry 35,
   [tests/test_roll_momentum.py](../tests/test_roll_momentum.py) holds
   Entry 36,
   [tests/test_tu_hypothesis_tests.py](../tests/test_tu_hypothesis_tests.py)
   holds Entry 37, [tests/test_gld_gc.py](../tests/test_gld_gc.py) holds
   Entry 38, and
   [tests/test_xle_uso_roll_return.py](../tests/test_xle_uso_roll_return.py)
   holds Entry 39.
2. **Every published figure names where the source prints it, or says it has no
   citation.** A published figure is quoted from the book and is asserted
   nowhere. Chan's 1.6766 is a target the replication chases, and the design
   doc and the suite's own docstring both record that it is asserted nowhere.
   Where the figure is among the committed
   highlights in [research/book-notes](../research/book-notes/README.md), the
   row gives its Kindle location. Where it is not, the row says so and points at
   the recorded absence.

Three of the figures below carry no location, and that absence is already
written down. [research/book-notes/README.md](../research/book-notes/README.md)
names −3.357, 1.0114 and −2.14 as the figures the highlights miss, because a
highlight covers the sentences somebody marked rather than the numbers a
replication ends up chasing. Their values survive in `BOOK_REF_FULL` and
`KOPEP_REF` in
[src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), which is
where those rows trace to.

Row 8 is therefore quoted at the two decimals `KOPEP_REF` records, and not at
the −2.14258438 that the docstring of `test_fails_to_cointegrate` also carries.
A docstring is not an authority for a number. Row 4 looks like the opposite
call and is not: its eight-digit figure is quoted because the book prints it,
at location 3718. Row 12 quotes the same figure for the same reason.

### What precision a number is quoted at

A computed number is quoted at the precision its assertion holds, never past it.

The CADF statistics of rows 3, 4, 8 and 10 are pinned at `abs=1e-2`, so they
are quoted at two decimals even though the engine returns four. The hedge
ratios are pinned at `abs=5e-4` and are quoted at four. The Chapter 3 statistic
is the exception: `TestLagSettingDetour::test_fixed_lag_reproduces_the_book`
holds that same statistic at `abs=5e-4`, so row 4 quotes −3.0875 and cites that
assertion rather than the two-decimal pin on the same quantity. Row 12, the
same statistic on Chan's own files under `cadf`'s own regression, is held at
`abs=5e-9`, so it quotes all eight decimals the book prints.

That exception carries weight. Row 4's verdict turns on a margin of 0.0055
against Chan's own printed critical values, and at two decimals the margin
would print as 0.01, nearly double the real one.

Two quantities are derived rather than stated: a gap, which the vocabulary
defines as exactly that difference, and a rejection margin, which is a
statistic minus a critical value. Neither is a published figure, so neither
meets the design doc's cut on recomputing a published number in prose. No
published figure is recomputed in any entry.

A gap runs computed minus published, so a negative gap means this repo landed
below the book. The vocabulary names a gap's two operands without fixing their
order, which leaves a reader to guess, so the column header states the
direction and every row follows it.

A gap is stated at the precision both sides support, which is the coarser of
the two, and it is rounded from the engine's full value rather than from the
quoted one. Subtracting two already-rounded numbers moves a gap by up to a full
unit of the last digit, which is how Entry 1's row 3 gap of −0.10 would
otherwise print as −0.09. The +0.0035 in its row 12 reason column would print
as +0.0036 the same way, which is the figure
[issue 232](https://github.com/l3a0/quantitative-trading/issues/232) first
quoted. Row numbers restart per entry, so a reference to one
outside its own entry names the entry too.

### How a verdict is chosen

The vocabulary defines three verdicts and does not say how to pick between
them. Without a rule the obvious choices contradict each other: row 1 misses by
−0.0387 and row 6 misses by −0.0371, a smaller distance, and they do not get
the same verdict.

The rule is this. **A verdict says whether the claim the published figure was
printed to support survives on this repo's vintage.** How far the number moved
does not decide it.

1. **reproduced.** The claim survives and the number lands where the
   specification and the vintage predict.
2. **reproduced with a gap.** The claim survives, the number differs, and the
   difference has a named cause outside the method. A vintage nobody holds is
   that cause here.
3. **did not reproduce.** The number differs and no such cause is available.
   The source's own saved data is the sharpest case of this, because there the
   vintage explanation is spent.

That is why rows 1 and 6 part. Row 1 runs on a modern download and misses a
figure computed from a 2007 series no surviving file carries, so the cause is
named and outside the method. Row 6 re-runs Chan's own saved spreadsheet
through the same specification and still misses the number he printed from it.
Nothing is left to blame, which is the harder failure and the worse verdict.

The rule also settles the two CADF rows, which carry gaps of −0.10 and +0.0940
and still reproduce. Chan's claim is that the pair rejects the no-cointegration
null at a stated level. Both rows reject at that level, so the claim survives.

Two more verdict values suggest themselves and are not adopted. `reproduced
exactly` is not needed, because a gap of 0.0000 already says it in the column
built for it. `not a replication` is not a verdict at all, for the reason
below.

### Rows that are not replications

The vocabulary defines a replication as an attempt to reproduce a specific
published number. A row with no published number is therefore not a
replication, and it can carry neither a gap nor any of the three verdicts.
Entry 1's rows 2 and 10 are in that position, as are Entry 2's rows 6, 7 and 8,
Entry 3's rows 10, 13, 14, 16, 17 and 29 to 34, and Entry 4's rows 4 to 21, and
each verdict cell says so rather than reaching for a fourth value. Every row of
Entry 5 is in that position too, so that entry drops the verdict column rather
than filling it. So are Entry 6's rows 2 to 9, Entry 7's rows 15 to 18, 23 to 29 and 30 to 49,
Entry 8's row 3, Entry 9's rows 3 to 5, Entry 10's rows 6 to 13, Entry 11's
rows 2 and 6 to 10, Entry 12's rows 10 and 11, Entry 13's rows 11 to 16,
Entry 14's rows 3 to 9, Entry 15's rows 3 to 14, Entry 16's rows 6 to 11,
Entry 17's rows 10 and 11, Entry 18's rows 8 to 12, Entry 19's rows 9 to 11,
Entry 20's rows 11 to 13, Entry 21's rows 9 to 11, Entry 22's rows 8 to 10,
Entry 23's rows 15 to 20, Entry 24's rows 10 to 16, Entry 25's rows 5 to 7,
Entry 26's rows 4 to 7, Entry 27's rows 15 to 18, Entry 28's rows 5 to 11,
Entry 29's rows 7 to 14, Entry 30's rows 6 to 8, Entry 31's rows 3 to 14,
Entry 32's rows 5 to 7, Entry 33's rows 11 to 15, Entry 34's rows 10 to 12,
Entry 35's rows 4 to 9, Entry 36's rows 7 to 14, Entry 37's rows 6 to 8, and
Entry 38's rows 8 to 11.

Entry 25's row 5 is the one among them that verdicts rest on. It asks whether
the run's 612 returns equal the ones Chan's script saved, which no source
prints, so it carries no verdict of its own. Chan's saved returns give all
three of his printed figures, so rows 2 to 4 cite row 5 as their evidence. Its
criterion, a largest difference of at most 1e-9 on every row, was written on
[issue 345](https://github.com/l3a0/quantitative-trading/issues/345) before any
return was computed, because a tolerance chosen after the comparison could be
set to pass it.

A row with no published *number* can still be a replication, which is the case
[docs/design.md](design.md) covers by saying that where a source states a
ranking or a verdict, the claim is what gets pinned. Entry 3's rows 12, 15, 27
and 28 are all of those, and they split two and two. So is Entry 4's row 3,
which is the ranking Qian's two printed figures were printed to support.
Entry 10's row 1 is one too, for the reason Entry 6's row 1 below is: the
claim is about one strategy the book names, and its criterion was declared on
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206) before
any figure was computed. Entry 11's row 3 is one as well. The sidebar's claim
names one trade, and its criterion, a profit in every year from 1995 to 2008,
was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) before any
trade was computed. Entry 13's row 10 is a claim too, and the first exception
among them: its criterion was written on
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the
overlap it judges was measured. Round-off would leave two books of one size
the same on every day. Given the MATLAB's 50 longs, the Python's book matches
on none of 752 days and differs in at least 125 positions on each, so the
verdict does not rest on where a threshold sits. Entry 14's rows 1 and 2 are
two more. Location 4014's claim is about factors, and the section names both
MKT and WML, so each is a definite case of it. Their criterion was written on
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22), and the
owner ruled that each factor carries its own verdict, both before any
autocorrelation was computed.

Entry 5's claim does not take that route. Each claim above is about an
instrument its source names, SPY in Chan's Example 6.2 and Qian's own
portfolios. Chan's fixed-income sentence names none, so what Entry 5 tests is a
pair of stand-ins this repo chose, and its result is a finding about them
rather than a verdict on his sentence. His claim is also that such pairs can be
found, and one pair that fails does not refute that.

Entry 6's row 1 does take it. The same passage gives the CAD/AUD cross rate as
its example and says the rate "is quite stationary", which is a definite claim
about one series it names. The owner ruled on 2026-10-02 that the row carries a
verdict, and the criterion was written on
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) before any
statistic was computed, because a criterion chosen after the number is a
search.

Entry 7's row 22 takes it as well. P. 180 says the most recent five years of
the program's data give even worse average returns, a definite claim about one
strategy on one file. The owner ruled on 2026-10-04 that the revised MATLAB's
rules carry it, and the criterion, the rerun's annual return below the whole
period's, was written on
[issue 254](https://github.com/l3a0/quantitative-trading/issues/254) before
any five-year figure was computed.

Entry 15's rows 1 and 2 take it too, one per commodity. Chan names calendar
spreads as the simplest cointegrating futures pairs, and a June and July
natural gas pair is a member of that class rather than a stand-in for it,
which is the difference from Entry 5. A batch of them failing would bear on
his sentence, which one failing pair of bond funds cannot. The owner ruled on
2026-10-03 that each commodity carries a verdict, and the criterion was written
on [issue 137](https://github.com/l3a0/quantitative-trading/issues/137) before
any statistic on the futures was computed.

Entry 16's row 5 takes it as well. Chan states that conditional parameter
optimization improves every metric of the strategy he names, which is a
definite claim about one strategy, and the criterion, all four metrics better,
was written on
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23) before any
return on the minute bars was computed.

Entry 17's row 9 takes it too. Location 2800 says the return of the strategy
it names "did stabilize, though it hasn't returned to its former high level
yet" after 2009, and the criterion, a return from 2010 on of at least 0 and
below 2007's under the same script, was written on
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297) before
any return was computed.

Entry 18's row 7 takes it too. Chan says the mirror he names "does have
steeper drawdown", a definite claim about one strategy, and the criterion, the
deeper drawdown of the two as `calculateMaxDD` measures it, was written on
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295) before
any return was computed. Its rows 5 and 6 are replications of printed figures,
but the mirror's rule was read from one sentence, so it was declared on the
same issue before any run, and the verdicts name it.

Entry 21's rows 7 and 8 take it as well, and like Entry 13's row 10 their
criteria were written on
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340) after
the first run. Each reads its criterion straight from location 1505's words,
"a negative APR" and "actually lower" on both figures it names, so there was
no threshold left to choose once the numbers were seen.

Entry 22's row 7 takes it too. Location 1225 says the P&L of the strategy it
names "manages to be positive", and the criterion, the sum of the daily P&L
over all 1,216 rows above 0, was written on
[issue 338](https://github.com/l3a0/quantitative-trading/issues/338) before
any P&L was computed.

Entry 23's rows 3, 6 and 9 take it too, each a claim about the ETFs the
example names, and they are the exception Entry 13's row 10 is: their
criterion, each statistic past the critical value the script prints beside it,
was written on
[issue 339](https://github.com/l3a0/quantitative-trading/issues/339) after
the statistics were measured. The script had printed both the statistics and
the bars in 2012, so the criterion reads Chan's own table rather than choosing
a line, and no figure computed here could move a verdict.

Entry 24's rows 5 and 6 take it as well, each a claim about the basket the
example builds against SPY, and they are the exception Entry 23's rows are.
Their criteria, each test's statistic past its 95 percent value and each
test's count of relations at 95 percent, were written on
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343) after
the issue had read the statistics from the script's printout, though before
any was computed here. Location 2035 names neither test, so the criteria read
each separately, and each row carries one of the three verdicts per test
rather than a fourth value. The criteria read Chan's own table, so no figure
computed here could move a verdict.

Entry 26's row 3 takes it as well, and like Entry 21's rows 7 and 8 its
criterion was written on
[issue 341](https://github.com/l3a0/quantitative-trading/issues/341) after a
first transcription ran. Location 1559 calls the band "quite an improvement"
on the linear rule, and the criterion reads that as both figures the book
prints above Entry 21's on the same spread, with no margin. Choosing no margin
was a reading made after the run. The band leads by +0.069915 on the APR and
+0.375022 on the Sharpe ratio, so any margin a reader would put on "quite"
passes too.

Entry 27's rows 13 and 14 take it too, each a claim about futures the book
names, and like Entry 13's row 10 their criteria were written after the
figures they judge were measured. The criteria, |γ| at least twice |α| for
"much larger" and |γ| above |α| for "bigger", were written on
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347) after a
scratch run had measured the figures, though before the build. The
narrowest case clears the first by a factor of two, so the verdict does not
rest on where that line sits.
Entry 30's row 5 takes it too. Location 2303's "almost 5 percent" is a
hedged figure rather than an exact one, so it is judged against a criterion, the annualised differential
location 2273 defines at least 0.045 and below 0.050, was written on
[issue 346](https://github.com/l3a0/quantitative-trading/issues/346) before
the row was computed. The issue also wrote that the two rates' monthly means
were known when it chose the criterion, and that they pointed at a miss.

Entry 29's rows 1 to 6 take it too. Location 1922 makes three claims about the
ETFs it names and prints no statistic for any of them. Their criteria, each
claim's count of relations at 99 percent on the trace and eigen statistics
separately, were written on
[issue 344](https://github.com/l3a0/quantitative-trading/issues/344) before
any statistic was computed.

Entry 33's row 4 takes it too. Location 2646 says the variance ratio test
"failed to reject the hypothesis that this is a random walk", a definite claim
about one series it names. Its criterion, `h` = 0 at `vratiotest`'s default 5
percent, was written on
[issue 351](https://github.com/l3a0/quantitative-trading/issues/351) after a
scratch run had read the test, though before the build. Like Entry 21's rows 7
and 8, it reads the book's own words, and the 5 percent is the level the
script reads `h` at, so there was no threshold left to choose.

Entry 34's row 9 takes it too. Location 2461 says CL's 12-month log calendar
spread is "stationary with 99 percent probability", a definite claim about one
series it names, and prints no statistic. Its criterion, an ADF statistic
below its 1 percent critical value, was written on
[issue 348](https://github.com/l3a0/quantitative-trading/issues/348) after a
scratch run had measured −4.727778, though before the build, which is the
exception Entry 13's row 10 and Entry 27's rows 13 and 14 are. The criterion
reads "99 percent" as the 1 percent test level, the reading Entry 22's row 1
applies to a "90 percent" and Entry 29 declared on
[issue 344](https://github.com/l3a0/quantitative-trading/issues/344) before
any statistic was computed. So there was no threshold left to choose. Entry
32's rows 3 and 4, below, carry no verdict on the owner's ruling on
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342), because
each would rest on where its line sat. Here the line is the book's own level,
as Entry 33's row 4 reads `vratiotest`'s 5 percent, and −4.727778 clears
−3.4583 by 1.269478, so the verdict does not rest on where the line sits.

Entry 35's row 1 takes it too. Location 2502 says the ratio of VX's back
contract to its front is "stationary with a 99 percent probability", a
definite claim about one series it names, and prints no statistic. Its
criterion, an ADF statistic below its 1 percent critical value, was written on
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349) on
2026-10-05 before any statistic on VX was computed.

Entry 36's rows 4 to 6 take it too. Location 2690 says its revised rule
yields "a higher APR" and Sharpe ratio than Example 6.1, "with a reduced
maximum drawdown", three definite claims about one strategy it names. Their
criterion, the revised rule's figure the better one when both rules run on
one rebuilt series over one window with one arithmetic, was written on
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353) after
the scratch runs had measured it, though before the build, the order Entry
13's row 10 allows when it is stated. The criterion reads the book's words
with no margin, and a test pins each margin, because row 4's is about the
size of the rebuild's own error. All three claims also hold on Chan's own
2012-05-11 close over the rows it covers, under row 10. Rows 1 to 3 of the same entry are
replications of printed figures under a rule declared after the scratch
runs, so their verdicts name that rule.

Entry 32's rows 3 and 4 do not take it, and like Entry 27's row 16 they test
claims and carry no verdict. Location 1726 says the filter's slope
"oscillates around 1" and its intercept "increases monotonically with time",
each a definite claim about the series the script computes. The only criteria
for them were written on
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342) after a
scratch run had measured what they read, and unlike Entry 13's row 10 or
Entry 27's rows 13 and 14, each verdict would rest on where its line sat. The
owner ruled on 2026-10-06 that both rows report their figures as findings with
no verdict, and that neither counts toward the entry's tally. Each verdict cell
says so, with the value "none, a finding" that Entry 5 carries as a whole.

Entry 35's row 10 does not take it either. Location 2502 says the strategy
"performed much more poorly prior to October 2008", a definite claim, but the
declaration on
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349) gave it
no criterion, and the figures before October 2008 were measured after the
issue's table had been seen. A verdict would rest on a line chosen with the
figures in view, so the row reports them as a finding with no verdict, as
Entry 32's rows 3 and 4 do.

Entry 37's row 5 carries no verdict for a third reason. It runs the third
test of `TU_mom_hypothesisTest.m` as written, and the script adds each draw's
shuffled tranches to the observed positions rather than to the simulated ones,
so every simulated return is zero and the count is 0 whatever the data. A
count that cannot fail cannot reproduce anything, so its cell reads "none, a
finding", the value Entry 32's rows 3 and 4 carry, and row 4's corrected test
carries the verdict.
[Issue 352](https://github.com/l3a0/quantitative-trading/issues/352) declared
both before any draw on the seed they share.

Entry 1's rows 2 and 10, the first rows this section names, are in that entry
because leaving them out misleads. Row 2 is the slope
from the test's own regression, and a reader who compares it against 1.6766 is
comparing two specifications. Row 10 is what the book's pair looks like twenty
years on, which is the result that makes the shelf life visible.

Entry 1's row 11 is the opposite case and stays a replication. Chan prints three
statistics there, so there is something to reproduce. The figures reproduce and
the conclusion he drew from them does not, so the verdict stays with the
figures and the reason column carries the refutation.

### What a second entry does to this file

A second entry is a new `## Entry N` section below the last one, with the same
three tables and its own numbered rows, restarting at 1. The sections above are
shared and are not restated per entry. Entry 2 is the first of these and what
follows was written before it, so each point below now names what the entry
actually did.

Three things about the shape are deliberate.

- **A vintage column can be empty, and says so rather than going blank.** The
  coin-flip game is synthetic. It has no vendor and no download date, so the
  column that makes a row checkable has nothing to hold. Such a row writes
  `none, synthetic` rather than going blank, because a blank cell reads as an
  omission. Every row of Entry 2 does. Entry 9 reads the tables Chan prints,
  which have a source and no vendor, so its rows write
  `none, the book's printed tables` instead.
- **A column with nothing to hold in any row is dropped rather than filled.**
  Entry 1's computed table carries a Window column, because a window is what
  selects the rows a vintage is read over. A gamble has no window in any row,
  so Entry 2's table has five columns where Entry 1's has six. The vintage
  column survives the same test because `none, synthetic` is information and an
  empty window is not.
- **A negative-results log stays a separate document.**
  [docs/design.md](design.md) names one as a candidate. It records an
  idea that was killed, which is a different object from a published figure
  that was chased, so it does not fit these columns and would not share this
  file.

## Entry 1: GLD/GDX and KO/PEP, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, `example7_2.m`, `example3_6_1.m` and
`example7_3.m`. Shipped under
[issue 4](https://github.com/l3a0/quantitative-trading/issues/4), which covered
four reproduced experiments in one piece of work.

Both pairs are in one entry on purpose. KO/PEP is the pair that reproduces to
the digit and GLD/GDX is the pair with the gap, so an entry carrying either
alone would report only matches or only misses. The design doc's
considered-and-rejected register cuts the first of those outright.

Twelve rows, and all of them are derivable from
[tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py).

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | GLD/GDX hedge, Chapter 7 window, through the origin | 1.6766 | Kindle location 3727 |
| 2 | GLD/GDX hedge, Chapter 7 window, with an intercept | none, Chan prints no with-intercept slope | n/a |
| 3 | GLD/GDX CADF statistic, Chapter 7 window | −3.357, reported as better than 95% | no location, absence recorded in the book notes, value kept in `BOOK_REF_FULL` |
| 4 | GLD/GDX CADF statistic, Chapter 3 window | −3.18156477, quoted in his prose as −3.18 and reported as better than 90% | Kindle location 3718 |
| 5 | GLD/GDX mean-reversion half-life | about 10 days | Kindle location 4226 |
| 6 | GLD/GDX hedge from Chan's own archive, through the origin | 1.6766, the same figure as row 1 | Kindle location 3727 |
| 7 | KO/PEP hedge, through the origin | 1.0114 | no location, absence recorded in the book notes, value kept in `KOPEP_REF` |
| 8 | KO/PEP CADF statistic | −2.14258438, quoted in `KOPEP_REF` as −2.14 and reported as not cointegrating | no location, absence recorded in the book notes, value kept in `KOPEP_REF` |
| 9 | KO/PEP daily-return correlation | 0.4849, reported as statistically significant | Kindle location 3838 |
| 10 | GLD/GDX CADF statistic, full modern span | none, the book stops in 2007 | n/a |
| 11 | Chan's Python-versus-MATLAB disagreement, with his R run read as the tiebreak | −2.4 from his Python run, printed in full as t = −2.3591268376687244 with p = 0.3444494880427884 and a through-origin hedge of 1.631009, and −3.2 from his R run, printed in full as t = −3.240868894 with p = 0.004975, against the −3.18156477 of row 4 | Kindle locations 3755 and 3806 for the prose. The code and the full printouts are at pp. 149 to 151 of the revised edition, read by the owner on 2026-10-02 and recorded on [issue 168](https://github.com/l3a0/quantitative-trading/issues/168) rather than in the book notes |
| 12 | GLD/GDX CADF statistic from Chan's own archive, Chapter 3 window | −3.18156477, the same figure as row 4, printed beside an AR(1) estimate of −0.070038 | Kindle location 3718 |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 2006-05-23 to 2007-11-30 | OLS through the origin, no intercept, Chan's `ols(GLD, GDX)` | `gld_20yr_prices_unadjusted.csv` and `gdx_20yr_prices_unadjusted.csv`, yfinance raw closes, both downloaded 2026-08-27 | 1.6379 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 2 | 2006-05-23 to 2007-11-30 | OLS with an intercept, the cointegrating regression the test itself runs | same two files as row 1 | 1.3905, intercept 9.9361 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 3 | 2006-05-23 to 2007-11-30 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 1 | −3.45 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 4 | 2006-05-23 to 2007-05-23 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 1 | −3.0875 | `TestLagSettingDetour::test_fixed_lag_reproduces_the_book` |
| 5 | 2006-05-23 to 2007-11-30, both runs | Ornstein-Uhlenbeck half-life of the with-intercept residual spread | two vintages, run separately: the two raw yfinance files of row 1, and `gld_chan.csv` with `gdx_chan.csv`, saved 2007-12-02 | 10.6 on the yfinance raw closes, 10.3 on Chan's archive | `TestGldGdxReproduction::test_ch7_hedge_and_stat` and `TestGldGdxChanArchive::test_reproduces_chans_archive` |
| 6 | 2006-05-23 to 2007-11-30 | OLS through the origin, no intercept, the same specification as row 1 | `gld_chan.csv` and `gdx_chan.csv`, the adjusted-close columns of Chan's own `GLD.xls` and `GDX.xls`, saved 2007-12-02 | 1.6395 | `TestGldGdxChanArchive::test_reproduces_chans_archive` for the value, and `test_hedge_is_not_the_lost_book_vintage` for the distance only, since that one asserts a two-sided bound of more than 0.03 away from 1.6766 rather than a number, and carries no direction |
| 7 | 1977-01-03 to 2008-01-18 | OLS through the origin, no intercept | `ko_chan.csv` and `pep_chan.csv`, the adjusted-close columns of Chan's own `KO.xls` and `PEP.xls`, saved 2008-01-23 | 1.0114 | `TestKoPepNonCointegration::test_hedge_matches_chan_exactly` |
| 8 | 1977-01-03 to 2008-01-18 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 7 | −2.14 | `TestKoPepNonCointegration::test_fails_to_cointegrate` |
| 9 | 1977-01-03 to 2008-01-18 | Pearson correlation of daily returns, returns divided by the earlier price, two-sided significance on n−2 degrees of freedom | same two files as row 7 | 0.48492, with t = 49.0707 | `TestKoPepNonCointegration::test_returns_are_correlated` |
| 10 | 2006-06-19 to 2026-06-16 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | `gld_20yr_prices.csv`, downloaded 2026-06-16, and `gdx_20yr_prices.csv`, downloaded 2026-08-27, both Yahoo dividend-adjusted. Two files and two dates, so naming one of them cannot re-derive the row | −1.45, with a half-life of 833.5 | `TestGldGdxReproduction::test_full_span_fails_to_reject` |
| 11 | 2006-05-23 to 2007-05-23 for the Python run and the lag sweep, 2006-05-23 to 2007-11-30 for the R run | Python: `statsmodels` `coint` at its defaults, which is the Engle-Granger test on the with-intercept residual spread at the lag `autolag='aic'` picks. R: Hansen's covariate-augmented Dickey-Fuller regression, the daily change in GLD by OLS on a constant, GLD's lagged level, one lagged change of GLD, and GDX today and yesterday, with the t on the lagged level. GDX enters as its price, so the regression is an error-correction cointegration test whose coefficients imply a hedge. The lag sweep: row 4's spread at `autolag='aic'` and at every fixed lag from 0 to 16 | two vintages, run separately: `gld_chan.csv` and `gdx_chan.csv`, saved 2007-12-02, for both of Chan's runs, and the two raw yfinance files of row 1 for the sweep | On Chan's files, −2.3591 at 6 lags with p = 0.3444, and −3.2409 on 378 residual degrees of freedom, with an implied hedge of 1.6992, and +0.3554 when GDX's daily change replaces its price. On the yfinance raw closes, −2.2979 at 6 lags and −3.0875 at 1 lag, and the sweep clears −3.04 only at 0 and 1 lags | `TestChansPythonRun::test_coint_at_its_defaults_lands_the_printout` and `::test_the_default_picks_six_lags`, and `TestChansRRunIsACovariateAugmentedDickeyFuller::test_the_regression_lands_the_printout`, `::test_the_covariate_went_in_as_a_price` and `::test_the_training_subset_was_not_applied` for Chan's files, and `TestLagSettingDetour::test_the_default_lag_choice_flips_the_verdict`, `::test_fixed_lag_reproduces_the_book` and `::test_the_statistic_is_not_monotone_in_the_lag` for the yfinance raw closes |
| 12 | 2006-05-23 to 2007-05-23 | LeSage's `cadf(GLD, GDX, 0, 1)` as `example3_6_1.m` calls it, reconstructed as `lesage_cadf`: ADF at a fixed lag of 1 on the with-intercept residual spread, with the regression demeaned and its standard error formed as `cadf` forms it | `gld_chan.csv` and `gdx_chan.csv`, the adjusted-close columns of Chan's own `GLD.xls` and `GDX.xls`, saved 2007-12-02 | −3.18156477, with an AR(1) estimate of −0.070038. Row 4's specification gives −3.1780 on the same files | `TestChansPythonRun::test_cadfs_own_regression_lands_matlabs_printout`, `::test_the_port_misses_cadf_by_one_detail_of_its_regression` for −3.1780, and `TestResidualCheckOnChansFiles::test_the_fit_and_its_residuals` for the residual check the reason column quotes |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0387 | reproduced with a gap | The claim survives on rows 3 and 4, which reject the no-cointegration null. The number does not, and the cause is named and outside the method: Chan read a 2007-vintage adjusted series, and nineteen years of GDX distributions have rescaled that history since, so no modern download reaches it. |
| 2 | none | none, not a replication | The book prints no with-intercept slope, so there is nothing to reproduce. The row exists so that 1.3905 is not read against 1.6766, which would compare two specifications rather than two vintages. |
| 3 | −0.10 | reproduced | Chan reports better than 95% confidence. The computed statistic clears the 5% critical value under both tables in play, −3.34 from `EG_CRIT_N2` in the tree and −3.380 from the MATLAB printout quoted at location 3718, so the level he states survives. That printout is from his Chapter 3 run, and these are asymptotic values, so reading it across to this window is sound. |
| 4 | +0.0940 | reproduced | Chan reports better than 90% and not 95%, which is exactly the band the computed statistic lands in. It clears the 10% value and misses the 5% one under both tables. The margin is what the verdict rests on, and the two tables disagree about how thin it is: −0.0475 against `EG_CRIT_N2`'s −3.04, which is the only critical table in the tree, and −0.0055 against the −3.082 his MATLAB printed at location 3718, which survives only as quoted highlight text. Same verdict, and under his table the margin is smaller by a factor of 8.6. This row cites `EG_CRIT_N2` as the table it used. Under `cadf`'s own regression, which row 12 reproduces on Chan's files, these closes give −3.0908 and the margin against his table widens to −0.0088, so the verdict holds under it too. |
| 5 | not statable, the source gives one significant figure | reproduced | Both computations land on about 10 days. Two vintages that disagree on the hedge agree on the half-life, which is the evidence for which of the two estimates is fragile. |
| 6 | −0.0371 | did not reproduce | A smaller distance than row 1 and a worse verdict, because the vintage explanation is spent. This is Chan's own saved spreadsheet, re-run through his own specification, missing the number he printed from it. The 2007 book-run series is a state no surviving file carries, his included. |
| 7 | 0.0000 | reproduced | The same code, on a vintage that was not lost, lands on the printed digits. This is the counterpart to row 1 and the reason the GLD/GDX gap is a vintage story rather than a broken implementation. |
| 8 | 0.00 | reproduced | Chan's claim is that the pair does not cointegrate. The computed statistic sits well above `EG_CRIT_N2`'s 10% value of −3.04, so it fails to reject and the claim survives. |
| 9 | 0.0000 at four decimals | reproduced | Chan's claim is that the correlation is statistically significant. It clears the 5% level two-sided by a wide margin. Together with row 8 this is the demonstration that correlation and cointegration are different things. |
| 10 | none | none, not a replication | The book stops in 2007, so there is no published figure. What the row shows is the shelf life: the statistic fails to reject at 10% and the half-life runs to 833.5 days against the about 10 of row 5. |
| 11 | 0.0000 at four decimals on Chan's files, against both printed t-statistics. On the yfinance raw closes, +0.1 against his −2.4 | reproduced | Every figure both runs print reproduces on Chan's files at the precision printed, apart from R's p-value and its ρ², and the verdict rests there. The yfinance gap is the vintage gap of row 1. The Python claim survives: its p of 0.3444 fails to reject at 10%. The R claim is not settled by its own printout. Its p of 0.004975 comes from Hansen's distribution, which assumes a stationary covariate, and the code passed GDX's price, which fails to reject a unit root. That makes the regression an error-correction cointegration test, so neither Hansen's table nor `EG_CRIT_N2` is its critical value, and nothing here supplies one. Given GDX's daily change, the input Hansen's test is built for, the t is +0.3554, which rejects nothing. The conclusion Chan draws does not survive. He concludes that Python's statistics and econometrics packages are not to be trusted. Python and MATLAB ran one test on one window and differ in the lag count and in a detail of `cadf`'s regression worth 0.0035 at one lag, which row 12 pins, and R ran a different test on a longer window with an input it was not built for, so the disagreement says nothing about Python's packages. `TestChansPythonRun::test_the_fixed_lags_that_matched_the_2026_closes_miss_on_chans` kills three earlier readings: zero fixed lags, which give −3.2018 on the yfinance closes and −3.2975 on Chan's, three fixed lags, which give −2.4067 against −2.4857, and one fixed lag, whose −3.1780 rounds to R's −3.2 but comes from a different test than R ran. |
| 12 | 0.00000000 on the t-statistic and 0.000000 on the AR(1) estimate, at the decimals printed | reproduced | Chan's own files land both figures his MATLAB printed, once `cadf`'s own regression runs. The claim survives too. Chan reports better than 90% and not 95%, and the statistic clears `EG_CRIT_N2`'s −3.04 by 0.1416 and the −3.082 his MATLAB printed by 0.0996, and misses both 5% values. Row 4's specification gives −3.1780 on these files, +0.0035 away, and the difference is how `cadf` forms its regression. It demeans the regressors, charges the constant that implies no degree of freedom, and takes the covariance from the raw regressors. With a constant, row 4's specification matches `cadf`'s coefficient at every printed digit and gives −3.1749, so what is left is the standard error. The detail is inside the method and does not explain row 4's gap: `cadf`'s regression gives −3.0908 on the yfinance closes against −3.0875. The residual check ran on row 4's specification rather than on `cadf`'s. On these files it gives a Breusch-Godfrey p of 0.0460 and residual lag 6 outside the band, which limits what the rejection supports, as it does for row 4, and leaves the verdict alone. |

### What the entry concludes

Four things, in the order of how much they cost to learn.

1. **The pair's verdict reproduced and its hedge ratio did not.** Rows 3, 4,
   8 and 12 land the rejection levels Chan states, row 5 lands his half-life,
   and row 9 lands his correlation. Rows 1 and 6 miss his hedge. A published
   number and the claim it supports have different shelf lives, and only the
   number depends on a vintage.
2. **Chan's own saved data misses his own printed hedge.** Row 6 is the
   receipt. It removes the obvious reply to row 1, that the reproduction is
   simply wrong, and it puts the 2007 book-run series beyond reach of any file
   that still exists. Row 12 lands his Chapter 3 statistic on the same files to
   all eight decimals printed. His Chapter 7 statistic is not in the same
   position: those files give −3.52 over the Chapter 7 window against the
   −3.357 he printed, which no row carries yet, and
   [issue 268](https://github.com/l3a0/quantitative-trading/issues/268) asks
   why.
3. **Chan's conclusion about Python is refuted by his own numbers.** Row 11 is
   the most useful verdict here. His −2.4 and his −3.2 both reproduce on his
   own files, each t-statistic to within a billionth, and they come from two
   different tests on two different windows. His Python run is the
   Engle-Granger test on 252 days, with `autolag='aic'` picking six lags. His
   R run calls Hansen's covariate-augmented Dickey-Fuller test on all 385
   days and passes GDX's price where the test expects a stationary series, so
   its printed p-value does not settle whether it rejects. Chan's MATLAB call,
   as `example3_6_1.m` reads, runs the Engle-Granger test on the same 252 days
   as Python with one lag passed as an argument, so against MATLAB what
   separates Python is mostly the lag count. Row 12 reproduces that MATLAB call
   on his files, so all three printouts reproduce there. The rest is a detail
   of how `cadf` forms its regression, which makes MATLAB's one-lag statistic
   0.0035 more negative than the port's and changes no verdict. On the
   yfinance raw closes the statistic does not weaken steadily as lags are added, since it is more
   negative at four lags than at three. The verdict is what holds there: zero or one lag clears the 10% line
   and every count from two to sixteen misses it. A conclusion about a library
   turns out to be a conclusion about a default and about which test ran.
   Which lag count the test is entitled to is a separate question, taken up
   under
   [Which lag count the residuals allow](#which-lag-count-the-residuals-allow).
4. **The relationship itself has expired.** Row 10 is not a replication and is
   the reason the entry does not end on a match.

Every computed figure here agrees with
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md),
which carries a four-row summary of the same comparison and compresses the two
CADF windows into one cell. The two-run table's published figures agree too,
and one of them took a correction to get there. Row 12 has no counterpart in
the essay, whose fifth detour says Chan's files land two of his three numbers.
[Issue 262](https://github.com/l3a0/quantitative-trading/issues/262) carries
the third.

That essay's two-run table once gave the published hedge as 1.6766 on its
Chapter 3 row as well as its Chapter 7 row. The book prints 1.6766 for the
Chapter 7 window only, at location 3727. The Chapter 3 window's through-origin
slope is 1.6283, pinned by `TestGldGdxReproduction::test_ch3_hedge_and_stat`,
and it has no published counterpart at all. Reading one published hedge onto
both windows is the exact trap this replication exists to make visible. The
cell now reads `none` in both copies of the essay, the second being
[docs/gld-gdx-cointegration-lessons.html](gld-gdx-cointegration-lessons.html),
corrected under
[issue 27](https://github.com/l3a0/quantitative-trading/issues/27).

One smaller wording difference is worth naming rather than leaving for a reader
to trip on. The essay says Chan's own data "lands at 1.6395, which is no closer
to his printed figure". Rows 1 and 6 give the two distances as 0.0387 and
0.0371, so 1.6395 is nearer by under two thousandths. The essay rounds that to
nothing, which is fair at its granularity, and the rows state both distances
because the verdict rule turns on them.

### Which lag count the residuals allow

Row 11 shows that the lag count decides the verdict. It does not say which lag
count to believe. The ADF critical values assume the fitted regression leaves
residuals with no autocorrelation. A lag count that leaves some behind reads its
statistic against a table that does not apply, so the test no longer rejects at
the rate it states. Which way the error runs depends on what is left behind. On
this spread, the fits with fewer lags are the ones that reject.

This check is exploratory. It spent the Chapter 3 sample looking, after the
sweep behind row 11 had already been seen.

Each fixed-lag fit on the row 4 spread had its residuals checked at lags 1 to
10, in two ways. Passing means both.

1. Each autocorrelation against a white-noise band of ±1.96/√n, which is
   ±0.1240 at one lag. The band is pointwise. Under white noise each bar has a
   5% chance of leaving it, so one of ten bars outside is common and says less
   than it looks.
2. A Breusch-Godfrey test over the same ten lags, at the 10% cut. It replaces
   Ljung-Box here because the ADF regression carries lagged differences on its
   right-hand side, which is the case Breusch-Godfrey is built for.

[![Five panels of residual autocorrelation at lags 1 to 10, one panel each for ADF fits at 0, 1, 2, 3 and 6 lags. In the first four panels a bar at lag 6 rises above the shaded white-noise band, and in the panel for 2 lags a bar at lag 3 falls below it. In the panel for 6 lags every bar sits inside the band.](figures/adf_residual_autocorrelation.png)](figures/adf_residual_autocorrelation.png)

An autocorrelation at lag 6 of 0.15 to 0.18 survives every fit from zero lags
to five. Six lags is the first count whose residuals pass both checks, with a
Breusch-Godfrey p of 0.8395, and at six lags the statistic is −2.2979, which
does not reject. At one lag, which is the book's specification and the one row 4
reproduces, the Breusch-Godfrey p is 0.0421. So the fit behind Chan's
better-than-90% verdict fails the residual check, and the fit `autolag='aic'`
picks is the one that passes it.

The ten-lag horizon is a choice, so the check was repeated at every horizon
from one to ten. The one-lag fit fails at every horizon from two up, and six
lags pass at all ten. Zero lags is the fit whose verdict turns on the choice,
failing only at horizons six and seven.

Row 4's verdict stands, because it asks whether Chan's number reproduces under
his specification, and it does. What changes is what that number can support.
At the first lag count whose residuals pass, the test does not reject, so the
Chapter 3 window gives no evidence of cointegration on this vintage. That is an
absence of evidence rather than evidence against. The ADF has little power on
245 observations, and a failure to reject is what a weakly cointegrated pair
would also produce. Two more things bear on how far the result reaches.

1. At one lag the lag-6 autocorrelation is 0.1668 against a band of 0.1240, on
   250 observations, near enough the edge that a different vintage could move
   it inside. Chan's own files, the vintage his Python printout reproduces on,
   do not. There the bar is 0.1659 against the same band, the one-lag fit
   fails Breusch-Godfrey with a p of 0.0460, and six lags is again the first
   count that passes, at −2.3591, which does not reject. That six-lag fit is
   the one `coint` runs at its defaults, so the statistic Chan printed and
   distrusted is the one whose residuals pass. The one-lag fit checked here is
   row 4's specification on Chan's files rather than `cadf`'s own regression,
   which row 12 reproduces, and its failure bears on what row 12's rejection
   supports rather than on its verdict.
2. At the 5% cut, Breusch-Godfrey alone passes the fits at zero, two and five
   lags as well, and still fails one lag. What keeps those three out is the
   lag-6 bar outside the band, and the band is the pointwise check.

The same check on the Chapter 7 window, 2006-05-23 to 2007-11-30, gives a
different answer. It ran on two vintages, the yfinance raw closes behind row 3
and Chan's own files, and the two agree on the shape. At one lag, which rejects
at 5% on both, the residuals fail both halves of the check. The Breusch-Godfrey
p is 0.0325 on the yfinance closes and 0.0337 on Chan's files, and the
autocorrelation at lag 10 is 0.1443 and 0.1435 against a band of 0.1002. Every
lag count from zero to nine leaves that lag-10 autocorrelation outside the
band. Ten lags is the first count that passes, with a Breusch-Godfrey p of
0.3861 and 0.3896, and there the test still rejects. On the yfinance closes the
statistic is −3.2965, which clears 10% and misses 5% under both tables. On
Chan's files it is −3.3580, which clears `EG_CRIT_N2`'s −3.34 by 0.018 and
misses the −3.380 his MATLAB printed by 0.022. Its nearness to Chan's printed
−3.357 is a coincidence, since that figure is a one-lag fit on an earlier
vintage.

The lag-10 bar that decides this is the last one the band reads, so the count
of bars is a choice in the way the Breusch-Godfrey horizon is. With the
horizon held at ten, a band reading nine bars lets zero lags pass first, and a
band reading sixteen or more reaches a lag-16 bar and moves the first pass to
sixteen lags. At every setting tried, the first fit that passes rejects at 10%
or better on both vintages. So the check leaves the rejection in row 3
standing, at better than 90% rather than the better than 95% Chan reports.
Row 3's verdict stands for the reason row 4's does, since it asks whether
Chan's number reproduces under his specification.

Zero lags, which `autolag='aic'` and `autolag='bic'` both pick on this window,
clears Breusch-Godfrey and rejects at 5%. One bar at lag 10 keeps it out, and
that bar stays outside even a band widened for reading ten bars at once,
2.807/√n. This check is exploratory too, and it was run after the Chapter 3
result had been seen.

`TestResidualCheck`, `TestResidualCheckOnChansFiles` and
`TestResidualCheckChapter7` in `tests/test_pair_cointegration.py` pin every
number in this section.
`src/chan/lag_residual_figure.py` redraws the figure, and
`tests/test_lag_residual_figure.py` holds that it draws what the check
computes.

### Two counts and two senses of one word

Both are ambiguous in the code this entry quotes, so the entry says which it
means.

**Which count.** A run of `python -m chan.pair_cointegration --ch7` reports 385
aligned trading days and 383 ADF observations. The difference is one day to
difference the spread and one more for the lag, so the two counts are not
interchangeable and a row has to say which it means. The window column above
gives date spans rather than counts, because a row's count depends on what that
row computes.

- A hedge ratio is an OLS fit over every aligned trading day: 385 for rows 1, 2
  and 6, and 7835 for row 7. The suite asserts none of these four.
- A CADF statistic is an ADF fit, two observations shorter at the fixed lag of
  1 that these rows use: 383 for row 3, 250 for rows 4 and 12, 7833 for row 8,
  and 5028 for row 10. The suite pins all five.
- Row 5's half-life is an AR(1) regression on the same spreads as rows 3 and 6.
- Row 9 is neither. It runs on 7834 daily returns with 7832 degrees of freedom,
  which is what its pinned t of 49.0707 carries.
- Row 11 holds several runs, each with its own count. On the yfinance raw
  closes, the fixed-lag run has the 250 observations of row 4. The
  `autolag='aic'` run drops five more to its six lags and has 245, which the
  suite does not assert there, because
  `test_the_default_lag_choice_flips_the_verdict` pins the lag and the
  statistic and discards the count. The sweep drops one observation per lag,
  from 251 at 0 lags to 235 at 16, and the suite does not assert those counts
  either. On Chan's files the Python run also has 245, which
  `TestChansPythonRun::test_the_default_picks_six_lags` asserts, and the R
  regression has 383 rows and 378 residual degrees of freedom, which
  `TestChansRRunIsACovariateAugmentedDickeyFuller::test_the_regression_lands_the_printout`
  asserts.

**Which sense of verdict.** The same run prints `Verdict: REJECTS the
no-cointegration null`, which is the statistical sense: what the test concluded
about one spread. Every use of the word in this file is the vocabulary's sense
instead: the written conclusion of a replication, one of three values, chosen
by the rule above. The statistical sense appears here only inside the reason
column, where it is the thing the vocabulary's verdict is judging.

### What the citations do not cover

Every computed number above names an assertion, and the assertion holds less
than the row might suggest.
[Issue 10](https://github.com/l3a0/quantitative-trading/issues/10) lists what
survived a mutation pass over the ported suite. Three of its findings look as
though they sit under the rejection levels this entry quotes. Re-running them
says one does, one is narrower than the issue claims, and one does not reach
these rows at all.

1. `EG_CRIT_N2` is protected only by accident, through window counts in the
   rolling tests. Nothing asserts the three values themselves, so the table the
   rows compare against could be moved with the suite green.
2. The specification a row names is held, and by exactly one assertion.
   Forcing the ADF regression term from `n` to `c` moves the Chapter 7
   statistic by 0.0042, well inside every `abs=1e-2` pin, and the one test that
   fails is `TestLagSettingDetour::test_fixed_lag_reproduces_the_book`, whose
   `abs=5e-4` pin on −3.0875 is tight enough to catch it. Forcing the term to
   `ct` fails eleven tests. [Issue 10](https://github.com/l3a0/quantitative-trading/issues/10)'s body says all three terms leave the
   suite green, which running them does not bear out, and that correction is
   recorded on the issue.
3. `_verdict` has no test either, and reversing its level order so that every
   rejection reports the weakest level goes unnoticed. That one does not reach
   these rows. `_verdict` formats the CLI's report, and every rejection claim
   above traces instead to a test comparing the statistic against `EG_CRIT_N2`
   directly, such as `assert ch7.adf_stat < EG_CRIT_N2["5%"]`.

So a row saying the statistic rejects at the 5% level traces to a real
assertion, and the one thing that assertion would not notice is the critical
table moving underneath it. Closing that pin belongs to [issue 10](https://github.com/l3a0/quantitative-trading/issues/10) rather than to
this entry.

### The chapter labels are first-edition shorthand

The rows call one window the Chapter 7 window and the other the Chapter 3
window, which is this repo's naming throughout, taken from the first edition's
`example3_6_1.m` and page 63. That naming does not survive into the edition
committed here, and
[issue 12](https://github.com/l3a0/quantitative-trading/issues/12) settled it.

The *Quantitative Trading* notes in
[research/book-notes](../research/book-notes/README.md) are the 2021 revised
edition. In it the two printouts sit nine Kindle locations apart,
at 3718 and 3727, under one worked example introduced at location 3678 as
teaching both the cointegration test and the hedge ratio. Chan writes at
location 1862 that Chapter 3 defers the training-set analysis to Chapter 7
rather than performing it. So there is no two-chapter split in that edition.

What the rows rest on is untouched by this, and the distinction is the point.
The separation that matters is between two regression specifications, `cadf`
with an intercept against a through-origin `ols`, and that comes from the
MATLAB package rather than from the book's structure. Chapter numbering was
never load-bearing for a single pinned figure.
[docs/design.md](design.md) carries the full argument.

The labels stay, because the windows they name are unambiguous whatever the
chapters are called, and every row already carries its own date range and price
basis. What changed is that they are declared shorthand rather than left to
look like the book's own structure. The
windows themselves are unambiguous whatever the chapters turn out to be, since
each row gives its dates.

### Nothing checks this file's numbers against the suite

Nothing compares the numbers in this document against the assertions they name.
[tests/test_markdown_hygiene.py](../tests/test_markdown_hygiene.py) sweeps this
file's formatting and resolves every anchor its Contents carries, and neither
reads a figure, so a re-pin that moves a number leaves this entry stale and
the suite green. Whether that guard gets built is the decision on
[issue 6](https://github.com/l3a0/quantitative-trading/issues/6).

Until then this file joins the re-pin sweep by hand. A change to any assertion
named above moves the entry that cites it in the same commit. For Entry 1 that
carries both copies of the essay too, which quote the same figures at coarser
granularity:
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md)
and the published
[docs/gld-gdx-cointegration-lessons.html](gld-gdx-cointegration-lessons.html).
Missing the second is the easy slip, because it is a hand-maintained copy that
no build step regenerates. 1.6766 now appears on eleven tracked files and
1.6379 on ten.

## Entry 2: the coin-flip gamble, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Box 6.1, "Loss aversion is not a behavioral
bias". Shipped under
[issue 13](https://github.com/l3a0/quantitative-trading/issues/13).

The label is a revised-edition one, and this entry declares it because the
repo reads a label as first-edition unless it says otherwise. The gamble sits in Box 6.1 of
Chapter 6, a sidebar the 2009 edition could not hold because it quotes
Kahneman's 2011 book. The box cites a separate Example 6.1 at Kindle location
3186, "As Example 6.1 shows", for the continuous approximation it uses. This
entry called the gamble Example 6.1 until 2026-09-29, misreading that sentence,
and the owner corrected the label against the book. The first-edition code
mirror this repo cites for `example7_2.m` and `example7_3.m` carries
`example6_2.xls` and `example6_3.m` and nothing for Box 6.1, so there is no
companion file to check the arithmetic against. The printed prose is the whole
source.

Eight rows, all derivable from
[tests/test_coin_flip_growth.py](../tests/test_coin_flip_growth.py). Three
carry no published figure and say so in their own cells: row 6 is the exact
discrete rate the book does not print, row 7 states the ensemble side in log
units, and row 8 compounds those two against each other, the ensemble side over
the exact discrete rate, into the capital comparison that makes the argument
visible.

**The vintage column says `none, synthetic` in every row.** A gamble has no
vendor and no download date, so the column that makes every other row checkable
has nothing to hold. Leaving it blank would read as an omission.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Expected gain per round, with infinite capital | \$5 | Kindle locations 3176 and 3186, which print it twice |
| 2 | Expected return of one round | 0.005 | location 3186 |
| 3 | Standard deviation of that return | 0.105 | location 3186 |
| 4 | Expected growth rate, continuous approximation | −0.0005125 per round | location 3186 |
| 5 | The rescaling, worked | \$2,000 of capital wins \$220 or loses \$200 | location 3186 |
| 6 | Exact discrete growth rate | none, the book gives only the continuous approximation | n/a |
| 7 | Ensemble average in log units | none, the book prints the simple return | n/a |
| 8 | Capital after 1,000 rounds, the ensemble side against the exact discrete rate | none, the book works no horizon | n/a |

### What this repo computed

| # | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | Half the win less half the loss, at the starting capital | none, synthetic | \$5.00 | `TestBookFigures::test_expected_gain_is_five_dollars` |
| 2 | Mean of the two equally likely returns, +0.11 and −0.10 | none, synthetic | 0.005 | `TestBookFigures::test_expected_return_and_standard_deviation` |
| 3 | Population standard deviation over those two outcomes, not the sample form | none, synthetic | 0.105 | `TestBookFigures::test_expected_return_and_standard_deviation` |
| 4 | `g = m - s^2 / 2` on that mean and that standard deviation | none, synthetic | −0.0005125 | `TestBookFigures::test_the_growth_rate_reproduces_to_the_digit` |
| 5 | The stake the rescaling implies, as a fraction of capital at any level | none, synthetic | exactly 1/10, against a break-even stake of 1/11 | `TestBookFigures::test_the_stake_is_exactly_a_tenth` and `::test_the_gamble_sits_just_past_break_even` |
| 6 | `0.5 * ln(1.11) + 0.5 * ln(0.90)` | none, synthetic | −0.00050025 | `TestTheNearMisses::test_the_exact_discrete_rate_is_a_different_number` |
| 7 | `ln(1 + m)`, so both averages are per-round log rates | none, synthetic | +0.0049875 | `TestBookFigures::test_the_two_averages_disagree_in_sign` |
| 8 | `ensemble_log_growth` and `growth_exact` each compounded from \$1,000 over 1,000 rounds | none, synthetic | \$146,576 against \$606, a ratio of 241.72 | `TestTheCapitalDiverges::test_the_capital_a_reader_sees_at_a_thousand_rounds`, `::test_the_gap_widens_with_every_round` and `::test_the_time_average_path_is_the_median_path` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | \$0, the book prints one significant figure | reproduced | Chan's claim is that a player with infinite capital collects \$5 a round. The figure is exact and nothing can move it. |
| 2 | 0.000 at the three decimals the book prints | reproduced | Exact at that precision. |
| 3 | 0.000 at the three decimals the book prints | reproduced | Exact at that precision, and the specification is what the row holds. The sample form over two outcomes gives 0.14849 instead, which the suite pins as the near miss it is. |
| 4 | 0.0000000 | reproduced | The replication. Chan's claim is that the growth rate is negative while the expected return is positive, so the layman refusing the gamble is right. It reproduces at the seven decimals he prints, and the claim survives with it. |
| 5 | not statable, the source works an illustration rather than a figure | reproduced | Chan's claim is that adjusting the payoff keeps the return moments constant as capital moves. It does, and the stake it implies is exactly a tenth, so the word "roughly" in any paraphrase is doing no work. |
| 6 | none | none, not a replication | The book prints only the continuous approximation. The row exists so −0.00050025 is not read as a failure to reproduce −0.0005125: it is a different quantity, computed exactly, differing at the second significant digit. |
| 7 | none | none, not a replication | Derived so the two averages can be compared. The book's own two figures are not in one unit, since 0.005 is an arithmetic mean simple return and −0.0005125 is a log growth rate. |
| 8 | none | none, not a replication | The book works no horizon. This row is what makes the argument visible, and the reason the entry does not end on a rate. |

### What the entry concludes

Four things, and the first is why a verdict here carries less than it looks.

1. **The verdict was knowable before the work started.** A verdict says whether
   the claim a published figure supports survives on this repo's vintage, and a
   vintage is the mechanism that moves a number. There is none, so nothing
   could have moved it and rows 1 to 5 could only reproduce. What this entry is
   worth is rows 7 and 8, not its verdict column.
2. **The book prints no formula, so the formula is what rows 3 and 4 hold.**
   Three candidate formulas give three numbers, and only one reproduces all four
   of Chan's figures at once. The sample standard deviation gives −0.006025, out
   by a factor of 11.8 and still printing as a small negative number. The exact
   discrete rate gives −0.00050025. Both are pinned, because an assertion on
   −0.0005125 alone would hold a number rather than a choice.
3. **The two rates do not diverge. The capital does.** Both are constants in
   the number of rounds, so a report showing two rates at one horizon shows a
   disagreement in sign and never a divergence. Row 8 of this entry is the
   divergence: the ratio grows as
   `exp((ensemble_log_growth - growth_exact) * n)`, and it reaches 241.72 by
   1,000 rounds. That exponent rounds to 0.005488 per round, which is a
   rounding of the rate and not the recipe the ratio comes from. Multiplying
   the rounded figure by 1,000 gives 241.77 instead.

   What the ensemble side is set against changes between the two rows, and
   what each row is for is the reason. Row 7 of this entry states that side in
   log units so it can be compared against the continuous approximation the
   book prints, which is what row 4 of this entry reproduces. Row 8 of this
   entry compounds a capital instead, and the book works no horizon there, so
   there is no published figure to match and `growth_exact`, the exact
   discrete rate, is the quantity available. It is also the only rate that
   reproduces the median path: at 1,000 rounds that path reaches \$606, where
   the approximation compounds to \$599, a capital no run of the gamble can
   produce.
4. **Neither epistemic label reaches this entry.** The design doc defines
   exploratory as a result produced by looking at the data and registered as one
   whose hypothesis was committed before the number was seen. This spends no
   sample, so the entry says both are inapplicable rather than picking one. A
   reader taking "exploratory" here would think the arithmetic might not hold.

### Why no simulated number is pinned against the book

[src/chan/coin_flip_growth.py](../src/chan/coin_flip_growth.py) also runs a
seeded simulation, and none of its output appears in the tables above. That is
deliberate and worth stating, because a reader expecting a Monte Carlo would
otherwise look for one.

The per-flip standard deviation of the log return is 0.10486, so a growth rate
estimated from a million flips carries a standard error of 1.05e-4 against a
quantity of 5e-4. Chan prints seven decimals. Bringing the standard error down
to one part in a hundred thousand takes about 110 million flips, and to one
part in a million about eleven billion. So the simulation demonstrates the argument and the closed form
is what the book's figures are pinned against.

Two things the suite does pin about it, because a demonstration nobody sized is
a demonstration that works on the seed somebody tried. At 1,000 paths by 1,000
rounds the time average comes out negative on all of the first 200 seeds. At
100 rounds by 200 paths it comes out positive on 56 of them, so more than a
quarter of seeds get the sign of the time average wrong. The report prints the
standard error beside the estimate and says when a size cannot resolve the
sign, which is a line a reader sees rather than an exception, because at that
size nothing has failed.

The draw method is part of what a seed means, and the module names it. On seed
7, `rng.integers`, `rng.random`, `rng.binomial` and `rng.standard_normal` give
four different flip sequences. This is the shape row 11 of Entry 1 records,
where a conclusion about a library turned out to be a conclusion about an
`autolag` default.

Nothing checks this entry against the suite either, for the reason Entry 1
states above. A change to any assertion this entry names moves it in the same
commit, and moves
[blog/coin-toss-expected-value-vs-growth.md](../blog/coin-toss-expected-value-vs-growth.md)
with it, since that post quotes the same pins.

## Entry 3: Kelly leverage on SPY, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Example 6.2, with the specification read off his
own `example6_3.m`. Rows 1 to 17 shipped under
[issue 14](https://github.com/l3a0/quantitative-trading/issues/14), rows 18 to
30 under [issue 138](https://github.com/l3a0/quantitative-trading/issues/138),
and rows 31 to 34 under
[issue 192](https://github.com/l3a0/quantitative-trading/issues/192).

Thirty-four rows, all derivable from
[tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py).

**The entry reads three vintages of SPY over Chan's own span.**

1. **Rows 1 to 17 read a 2026 download.** He read SPY through 2007-12-28 on a
   2008-vintage adjusted series, so rows 1 to 8 measure how two downloads
   eighteen years apart differ, with the window held fixed. Rows 1 and 3 to 8
   all miss, every one of them high. Row 2, the dispersion, lands on the two
   decimals he prints.
2. **Rows 18 to 28 read his own `example6_2.xls`**, committed as
   `data/spy_chan.csv`. Every figure he computed from a series reproduces from
   it at the precision he printed it. The one printed figure that does not is
   row 26's \$252,800, because he rounded the leverage to 2.528 before
   multiplying.
3. **Rows 31 to 34 read the same workbook's as-traded `Close`**, committed as
   `data/spy_unadjusted_chan.csv`. Chan printed nothing from it. It shares the
   adjusted column's days and saved date, so it changes the price basis and
   nothing else, and on his data that is enough to reverse his risk
   conclusion.

Rows 29 and 30 set the first two day by day against each other, which is what
says why the first group misses. Dividends paid after his window cannot
explain it, because they scale every price inside it by one factor and leave
every return unchanged. Those two hold the same 3,758 days, and the
whole gap in the mean sits on about ten days on or beside SPY's quarterly
ex-dividend dates. The differences mostly raise the 2026 mean, and the rest of
the days together pull back less than a tenth of the gap. A few large
differences move a mean while barely touching a standard deviation. Row 30 pins
all of that, including that each of the ten falls on a quarter-end month's
third Friday or the trading day after.

Two finer descriptions are measured on
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138) rather
than pinned. On the four largest days, one download folds nearly a whole
quarterly payout into the day's return and the other does not, and on the rest
of the ten it folds in part of one. Outside the ten, the differences are mostly
rounding and a few smaller dividend differences.

Two more rows reproduce and neither reads a series. Rows 9 and 11 are
arithmetic on figures the book prints, so nothing could have moved them.

Eleven rows carry no published figure and say so in their own cells.

- Row 10 is the 2026 download's own account beside the book's.
- Row 13 is the worst day SPY actually holds.
- Rows 14, 16 and 17 are three windows the book does not work. Those three are
  why the window is an argument, and rows 16 and 17 are the two that make the
  case, since between them the leverage runs from a short of 2.82 times equity
  to a long of 4.90.
- Rows 29 and 30 are the first two vintages set against each other.
- Rows 31 to 34 read the as-traded column, which Chan printed nothing from.
  Row 34 is his Black Monday claim tested on that column, and it is not a
  replication because his claim is about the series he read.

Four rows chase a claim rather than a number, which is the shape
[docs/design.md](design.md) names for a source that states a verdict instead of
a figure. Rows 12 and 27 are Chan's Black Monday conclusion, on the 2026
download and on his adjusted column, and it survives on both. Rows 15 and 28
are his time-scale independence, and it fails on both. A fifth row, 34, tests
the Black Monday conclusion a third time, on his as-traded column, where it
fails. It is not among the four and carries no verdict rather than `did not reproduce`, because rows 12 and 27 test
his claim on the series he read and row 34 tests it on a series he did not.

Every result here is **exploratory** in the design doc's sense, and this is the
first entry where that matters to a reader rather than to a bookkeeper. Its
output is a leverage rather than a statistic, so it is the first result in this
repo that could be mistaken for advice. The report says so on its own last
lines.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | SPY mean annual return | 11.23 percent | Kindle location 2858 |
| 2 | Annualised standard deviation | 16.91 percent | location 2858 |
| 3 | Mean excess return, over a 4 percent risk-free rate the book supplies | 7.231 percent | location 2858 |
| 4 | Sharpe ratio | 0.4275 | location 2858 |
| 5 | Optimal Kelly leverage | 2.528 | location 2858 |
| 6 | Levered compounded growth rate, including financing costs | 13.14 percent | locations 2858 and 2869 |
| 7 | Unlevered compounded growth rate | 9.8 percent | location 2869 |
| 8 | Half-Kelly leverage | 1.26 | location 3083 |
| 9 | The worked example and the rebalancing chain | \$100,000 of equity buys \$252,800, which falls to \$227,520, leaving \$74,720 of equity, resized to \$188,892 | locations 2869 and 3021 |
| 10 | The same account on this run's leverage | none, the book works one leverage | n/a |
| 11 | The leverage a 20 percent one-day tolerance allows | about 1 | location 3083 |
| 12 | Chan's conclusion, that even half-Kelly would not have survived Black Monday | a claim rather than a figure, resting on a 20.47 percent S&P 500 loss on 1987-10-19 | location 3083 |
| 13 | Worst one-day loss in SPY | none, his 20.47 percent is an S&P 500 index figure from six years before SPY existed | n/a |
| 14 | Kelly leverage over the full modern span | none, the book stops in 2007 | n/a |
| 15 | Kelly's independence of time scale, unlike the Sharpe ratio | a claim rather than a figure | location 2858 |
| 16 | Kelly leverage over the 2000 to 2002 bear market | none, the book works one window | n/a |
| 17 | Kelly leverage over the 2003 to 2007 bull market | none, the book works one window | n/a |
| 18 | SPY mean annual return, on Chan's own workbook | 11.23 percent | location 2858 |
| 19 | Annualised standard deviation, on Chan's own workbook | 16.91 percent | location 2858 |
| 20 | Mean excess return, on Chan's own workbook | 7.231 percent | location 2858 |
| 21 | Sharpe ratio, on Chan's own workbook | 0.4275 | location 2858 |
| 22 | Optimal Kelly leverage, on Chan's own workbook | 2.528 | location 2858 |
| 23 | Levered compounded growth rate, on Chan's own workbook | 13.14 percent | locations 2858 and 2869 |
| 24 | Unlevered compounded growth rate, on Chan's own workbook | 9.8 percent | location 2869 |
| 25 | Half-Kelly leverage, on Chan's own workbook | 1.26 | location 3083 |
| 26 | The worked example and the rebalancing chain, on the leverage his own workbook gives | \$252,800, \$227,520, \$74,720 and \$188,892, the same figures as row 9 | locations 2869 and 3021 |
| 27 | Chan's Black Monday conclusion, on his own workbook | the claim of row 12 | location 3083 |
| 28 | Kelly's independence of time scale, on his own workbook | the claim of row 15 | location 2858 |
| 29 | The days the 2026 download and Chan's adjusted column hold over his span | none, the book reads one vintage | n/a |
| 30 | The difference in return between those two over Chan's span | none, the book reads one vintage | n/a |
| 31 | Optimal Kelly leverage, on Chan's own as-traded close | none, the book reads only the adjusted close | n/a |
| 32 | What the price basis is worth on the leverage | none, the book reads one price basis | n/a |
| 33 | What the price basis is worth on the mean annual return | none, the book reads one price basis | n/a |
| 34 | Chan's Black Monday conclusion, on his own as-traded close | the claim of row 12, on a series he did not read | location 3083 |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 1993-01-29 to 2007-12-28 | simple daily returns on the adjusted close, mean times 252 | `yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv`, yfinance's both-adjustments close, downloaded 2026-09-18 | 11.2948 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 2 | 1993-01-29 to 2007-12-28 | sample standard deviation, dividing by n−1, times the square root of 252 | same file as row 1 | 16.9117 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 3 | 1993-01-29 to 2007-12-28 | the mean less 0.04/252 per day, annualised by 252 | same file as row 1 | 7.2948 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 4 | 1993-01-29 to 2007-12-28 | `S = m / s` on rows 3 and 2 | same file as row 1 | 0.4313 | `TestChansWindowOnAModernDownload::test_the_sharpe_ratio_at_a_tolerance_that_holds_the_specification` |
| 5 | 1993-01-29 to 2007-12-28 | `f* = m / s^2` on rows 3 and 2 | same file as row 1 | 2.5506 | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 6 | 1993-01-29 to 2007-12-28 | `g = r + S^2 / 2`, the scalar case of `example6_3.m`'s `g=0.04+F'*C*F/2` | same file as row 1 | 13.3031 percent | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 7 | 1993-01-29 to 2007-12-28 | `g = r + m - s^2 / 2`, with m the excess return of row 3 | same file as row 1 | 9.8648 percent | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 8 | 1993-01-29 to 2007-12-28 | row 5 halved, the convention location 2836 states | same file as row 1 | 1.2753 | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 9 | none, the chain reads no series | buy at the book's rounded 2.528, take a 10 percent loss on the position, resize at the same leverage | none, arithmetic on a published figure | \$252,800.00, \$227,520.00, \$74,720.00 and \$188,892.16 | `TestTheWorkedExample::test_the_books_own_chain_reproduces_to_the_cent` |
| 10 | 1993-01-29 to 2007-12-28 | the same chain at row 5's leverage | same file as row 1 | \$255,059.13, \$229,553.22, \$74,494.09 and \$190,003.97 | `TestTheWorkedExample::test_this_vintages_chain_is_a_different_account` |
| 11 | none, both operands are book constants | 0.20 divided by 0.2047 | none, arithmetic on two published figures | 0.977040 | `TestTheStressTest::test_the_tolerance_allows_about_one_times_equity` |
| 12 | 1993-01-29 to 2007-12-28 | row 8 against row 11, which holds exactly while row 5 is above 1.954079 | same file as row 1, for row 5 only | the claim holds, by a margin of 0.60 on the leverage | `TestTheStressTest::test_the_conclusion_has_a_threshold_and_this_run_clears_it` and `::test_the_verdict_turns_over_at_the_threshold_and_not_before` |
| 13 | 1993-01-29 to 2007-12-28 | the minimum of the daily simple returns | same file as row 1 | −7.2473 percent, on 1997-10-27 | `TestTheStressTest::test_black_monday_is_a_book_constant_and_not_a_vintage_figure` |
| 14 | 1993-01-29 to 2026-09-18 | the same specification as rows 1 to 8 | same file as row 1 | mean 11.9982 percent, sd 18.5349 percent, Sharpe 0.4315, `f*` 2.3281 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_full_modern_span_has_no_published_counterpart` |
| 15 | 1993-01-29 to 2007-12-28 | `f*` recomputed on resampled returns, under three named monthly rules | same file as row 1 | 3.7175 on calendar month-ends, 3.7460 dropping the partial final month, 3.6438 on 21-day blocks, against 2.5506 daily | `TestTimeScaleIndependence::test_resampling_is_what_actually_moves_it` and `::test_the_conclusion_does_not_depend_on_which_monthly_rule_is_picked` |
| 16 | 2000-01-01 to 2002-12-31 | the same specification as rows 1 to 8 | same file as row 1 | mean −12.5412 percent, sd 24.2032 percent, `f*` −2.8237 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_bear_window_recommends_a_short` |
| 17 | 2003-01-01 to 2007-12-28 | the same specification as rows 1 to 8 | same file as row 1 | mean 12.2867 percent, sd 13.0081 percent, `f*` 4.8972 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_bull_window_nearly_doubles_it` |
| 18 | 1993-01-29 to 2007-12-28 | row 1's specification | `spy_chan.csv`, the adjusted-close column of Chan's own `example6_2.xls`, saved 2008-01-29 | 11.2307 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 19 | 1993-01-29 to 2007-12-28 | row 2's specification | same file as row 18 | 16.9131 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 20 | 1993-01-29 to 2007-12-28 | row 3's specification | same file as row 18 | 7.2307 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 21 | 1993-01-29 to 2007-12-28 | row 4's specification | same file as row 18 | 0.427523, against 0.427580 under the population dispersion form | `TestEveryFigureHePrintedReproducesFromHisData::test_the_sharpe_ratio_and_the_dispersion_form_it_decides` |
| 22 | 1993-01-29 to 2007-12-28 | row 5's specification | same file as row 18 | 2.5278 | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 23 | 1993-01-29 to 2007-12-28 | row 6's specification | same file as row 18 | 13.1388 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 24 | 1993-01-29 to 2007-12-28 | row 7's specification | same file as row 18 | 9.8005 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 25 | 1993-01-29 to 2007-12-28 | row 8's specification | same file as row 18 | 1.2639 | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 26 | 1993-01-29 to 2007-12-28 | row 9's chain at row 22's leverage | same file as row 18 | \$252,775.87, \$227,498.28, \$74,722.41 and \$188,880.23 | `TestThePrintedPortfolioOnHisExactLeverage::test_his_exact_leverage_buys_less_than_he_printed` and `::test_rounding_the_leverage_is_the_whole_cause` |
| 27 | 1993-01-29 to 2007-12-28 | row 25 against row 11, which holds exactly while row 22 is above 1.954079 | same file as row 18, for row 22 only | the claim holds, by a margin of 0.57 on the leverage | `TestHisOwnDataOnTheRestOfTheEntry::test_the_black_monday_conclusion_survives_on_his_data` |
| 28 | 1993-01-29 to 2007-12-28 | row 15's three monthly rules | same file as row 18 | 3.6908 on calendar month-ends, 3.7195 dropping the partial final month, 3.6163 on 21-day blocks, against 2.5278 daily | `TestHisOwnDataOnTheRestOfTheEntry::test_the_time_scale_claim_fails_on_his_own_series` |
| 29 | 1993-01-29 to 2007-12-28 | the two indexes intersected, with what each side lost counted | row 18's file and row 1's | 3,758 days in each and 3,758 joined, so the join drops nothing from either side | `TestTheTwoVintagesOverChansWindow::test_the_join_drops_nothing_from_either_side` |
| 30 | 1993-01-29 to 2007-12-28 | simple returns on the joined days, the 2026 download's less Chan's | row 18's file and row 1's | the annual mean differs by 0.0641 percentage points and the standard deviation by 0.0014. The ten largest daily differences carry 108.5 percent of the summed difference, eight raising the 2026 mean and two lowering it. Each of the ten falls on a quarter-end month's third Friday or the trading day after, and days in SPY's quarterly dividend months carry 100.4 percent | `TestTheTwoVintagesOverChansWindow::test_the_gap_in_the_mean_and_the_dispersion_that_does_not_move`, `::test_ten_days_carry_the_whole_gap_and_dividend_months_carry_it_too` and `::test_the_ten_days_are_all_quarterly_ex_dividend_days` |
| 31 | 1993-01-29 to 2007-12-28 | row 5's specification | `spy_unadjusted_chan.csv`, the as-traded `Close` column of Chan's own `example6_2.xls`, saved 2008-01-29 | 1.9341, from a mean of 9.5498 percent and a standard deviation of 16.9396 percent | `TestThePriceBasisOnHisOwnWorkbook::test_the_entry_is_his_workbook_s_close_column` and `::test_the_as_traded_leverage_and_the_moments_beneath_it` |
| 32 | 1993-01-29 to 2007-12-28 | row 22 less row 31 | row 18's file and row 31's | 0.5937 | `TestThePriceBasisOnHisOwnWorkbook::test_the_price_basis_is_worth_0_59_on_the_leverage` |
| 33 | 1993-01-29 to 2007-12-28 | row 18 less row 31's mean, in percentage points | row 18's file and row 31's | 1.6809 percentage points, against 0.0265 on the standard deviation | `TestThePriceBasisOnHisOwnWorkbook::test_the_price_basis_is_worth_1_68_points_on_the_mean` |
| 34 | 1993-01-29 to 2007-12-28 | row 31 halved against row 11, which holds exactly while row 31 is above 1.954079 | row 31's file, with row 18's beside it for the adjusted verdict | the claim fails, 0.0200 short of the threshold on the leverage, with half-Kelly at 0.9670 | `TestThePriceBasisOnHisOwnWorkbook::test_the_black_monday_conclusion_reverses_on_the_as_traded_close` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.06 percentage points | reproduced with a gap | Chan's claim is that SPY's mean annual return over his span is about 11 percent, and it survives. The number does not, and the cause is named and outside the method: his 2008 download and this one differ on about ten quarterly dividends inside the window, so this download does not reach it. Later dividends are not the cause, since they scale every earlier price by one factor and leave returns unchanged. |
| 2 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. The whole gap in the mean sits on about ten days on or beside SPY's quarterly ex-dividend dates, where one download folds in all or part of a payout that the other does not, mostly raising the 2026 mean. That moves a mean and barely touches a standard deviation. |
| 3 | +0.064 percentage points | reproduced with a gap | Row 1's gap, carried through. The risk-free rate is the book's own constant, so nothing else moved. |
| 4 | +0.0038 | reproduced with a gap | Chan's claim is that SPY's Sharpe ratio over his span is a shade above 0.42, and it survives. This row is also what holds the specification: the population dispersion form gives 0.4276 rather than 0.4275 on his own data, and only an assertion tighter than 5.7e-5 can tell the two apart. |
| 5 | +0.023 | reproduced with a gap | The replication. Chan's claim is that the growth-optimal leverage on SPY is about two and a half times equity, and it survives with room. The number does not, for row 1's reason. |
| 6 | +0.16 percentage points | reproduced with a gap | Row 4's gap carried through `S^2 / 2`, which is how 0.0038 on a Sharpe ratio becomes 0.16 percentage points of growth. The formula itself is not among the committed highlights, because location 2849 renders it as an image, so it is recovered from `example6_3.m` rather than quoted. |
| 7 | +0.1 percentage points | reproduced with a gap | Chan's claim is that unlevered growth is below the mean return and levered growth above it, and both survive. Reading `m` as the total return instead of the excess return would put this row four points out, which is a misread symbol that looks like a gap in the data. |
| 8 | +0.02 | reproduced with a gap | Row 5 halved, so its gap halved. |
| 9 | \$0 on all four figures | reproduced | Every number in the chain is arithmetic on the book's own rounded 2.528. Nothing reads a series, so nothing could have moved. Chan's printed \$252,800 is itself derived from that rounded input: the exact leverage he computed buys \$252,775.87, which is the one printed figure his own workbook misses. |
| 10 | none | none, not a replication | The book works one leverage. The row exists so \$255,059.13 is not read against \$252,800 as a failure to reproduce: it is a different account, and the difference is row 5's gap times \$100,000. |
| 11 | not statable, the source gives one significant figure | reproduced | Chan prints "about 1" and 0.20 divided by 0.2047 is 0.977040. Both operands are his. |
| 12 | none, the source states a claim | reproduced | The claim is that even half-Kelly would not have survived Black Monday, and it survives on this vintage. It is thinner than 2.5506 against 1.954079 sounds: on Chan's own workbook the as-traded close gives a leverage of 1.9341, below the threshold, so the price basis alone reverses his conclusion, which rows 31 and 34 compute. That is why this repo's usual preference for a series that cannot be restated is set aside here and the adjusted close is read. |
| 13 | none | none, not a replication | SPY's first bar is 1993-01-29 and Black Monday is 1987-10-19, so no SPY vintage of any span can check the book's 20.47 percent. The worst day this window holds is 7.2473 percent, about a third of it, and the row exists so the two are not read as one number. |
| 14 | none | none, not a replication | The book stops in 2007. What the row shows is that nineteen more years of SPY lower the leverage to 2.3281 while leaving the Sharpe ratio at 0.4315, within 0.0002 of the shorter window's. The dispersion rose and the ratio did not move, which is the shape of a claim that has aged better than its number. |
| 15 | none, the source states a claim | did not reproduce | The claim is true in the reading nobody needs and false in the one they do. Under the annualisation in use the factor cancels between the mean and the variance, so the annualised and per-period ratios agree to floating-point noise, exactly and for any factor. Resampling the returns rather than rescaling their moments moves `f*` by 43 to 47 percent, on all three monthly rules, and those sit within 0.11 of each other. No vintage explanation is available, because the same three rules on Chan's own workbook land 43 to 47 percent above his daily figure too. This is the shape of Entry 1's row 11, where a conclusion about a library turned out to be a conclusion about a default. |
| 16 | none | none, not a replication | The book works one window. Kelly recommends a short of 2.82 times equity here, because the mean excess return over these three years is negative, and the row exists because that is the case requirement 10 of the issue was written for: a negative leverage is arithmetic rather than a failure, and neither half-Kelly nor the drawdown comparison carries across the sign change. |
| 17 | none | none, not a replication | The book works one window. Read against row 16 this is the entry's fourth conclusion in two cells: one vintage, one specification, and a leverage running from −2.82 to +4.90 depending only on which years are read. |
| 18 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. This is row 1 on the series Chan read, and the gap row 1 carries is gone, which is what names it as the vintage. |
| 19 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints, as row 2 already was on the 2026 download. |
| 20 | +0.000 percentage points | reproduced | Exact at the three decimals the book prints. |
| 21 | +0.0000 | reproduced | Exact at the four decimals the book prints, and only under the sample dispersion form. The population form gives 0.427580, which prints as 0.4276, so this row demonstrates on his own data what row 4 could only argue by analogy. |
| 22 | +0.000 | reproduced | Exact at the three decimals the book prints. A zero here says Chan's arithmetic is right on Chan's data. It says nothing about whether 2.528 is a leverage anyone should carry, and the report prints that above the table. |
| 23 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. |
| 24 | +0.0 percentage points | reproduced | Exact at the one decimal the book prints. |
| 25 | +0.00 | reproduced | Exact at the two decimals the book prints. |
| 26 | −\$24, −\$22, +\$2 and −\$12, in whole dollars because the book prints whole dollars | reproduced with a gap | The claim is that 2.528 times \$100,000 buys about a quarter of a million dollars of SPY and resizes as the chain shows, and it survives. The numbers differ because Chan rounded the leverage to 2.528 before multiplying. Rounding row 22 to the three decimals he printed reproduces the first three figures to the cent and the fourth to the dollar he printed it at, so the cause is named and sits in his arithmetic rather than in his data. |
| 27 | none, the source states a claim | reproduced | The claim survives on his own data as it does on the 2026 download in row 12. The margin is 0.57 here against 0.60 there, because his leverage is the lower of the two. |
| 28 | none, the source states a claim | did not reproduce | Row 15's refutation, on the series Chan read. Every monthly rule lands 43 to 47 percent above his daily figure, so the vintage explanation is spent, which is the sharpest case of this verdict the rules above name. |
| 29 | none | none, not a replication | The book reads one vintage. The row exists because a vendor restates which days a series holds as well as what they are worth, and a silent join would hide the first. Over this span the 2026 download and his adjusted column hold the same days, so row 30 is a difference in prices rather than in calendars. |
| 30 | none | none, not a replication | The book reads one vintage. This row is why rows 1 and 3 to 8 miss while row 2 does not. About ten days near SPY's ex-dividend dates carry more than the whole gap in the mean, and they barely move a standard deviation. |
| 31 | none | none, not a replication | The book prints nothing from the as-traded close. His `example6_3.m` reads the adjusted column, and this row reads the column beside it in the same workbook. |
| 32 | none | none, not a replication | The book reads one price basis. The basis is worth more than row 27's 0.57 margin over the threshold, which is why the conclusion turns over in row 34. |
| 33 | none | none, not a replication | The book reads one price basis. The mean moves by 1.68 points and the standard deviation by 0.0265 points, so the leverage falls with the mean rather than with the risk. SPY has not split, so what separates the two columns is its distributions. |
| 34 | none, the source's claim is about the series he read | none, not a replication | The claim fails on this column. Half-Kelly is 0.9670, below the 0.977040 a 20 percent day allows, so Black Monday's loss would have left it inside the tolerance. Rows 12 and 27 test his claim on the series he read and this row tests it on one he did not, so the verdict there stands. What this row shows is that the price basis decides the verdict rather than shading it. |

### What the entry concludes

Five things, and the first is what makes the other four worth reading.

1. **Seven numbers moved and every claim but one held.** Every level Chan
   computed from a series except the dispersion is higher on the 2026 download,
   by 0.06 percentage points on the mean and 0.023 on the leverage. Every
   statement those numbers were printed to support but one still holds on that
   vintage. The exception is his claim that the Kelly leverage does not depend
   on the time scale, which rows 15 and 28 record as `did not reproduce` on that
   vintage and on his own workbook alike, so its failure owes nothing to the
   vintage. The rest is the same split Entry 1 found on
   a different pair with a different estimator: a published number and the
   claim it supports have different shelf lives, and only the number depends on
   a vintage. What is new here is the one that did not move. The dispersion of
   row 2 reproduces while the mean of row 1 does not, because the two downloads
   differ on about ten days on or beside SPY's quarterly ex-dividend dates,
   mostly raising the 2026 mean, which moves a mean and barely touches a
   standard deviation. Row 30 measures that rather than arguing it.
2. **The specification is what rows 4 and 7 really hold.** Two choices are
   invisible on the page and each has a plausible wrong answer that does not
   look wrong. On this vintage the population dispersion form moves the Sharpe
   ratio by 5.74e-5 and the leverage by 6.79e-4, so a suite pinning the
   leverage at the three decimals Chan prints passes on either. Reading `m` as the total return moves
   the unlevered growth rate by exactly the risk-free rate, four points, which
   reads as a data gap rather than a misread symbol. Both are pinned, and the
   first is pinned tighter than the precision rule would ask for, which is the
   second instance of the exception Entry 1's row 4 established.
3. **A verdict can have a threshold, and this one does.** Row 12 is a claim
   rather than a figure, so the entry computes the leverage at which it turns
   over rather than reporting two numbers and leaving a reader to compare them.
   The margin is 0.60 on a threshold of 1.954079 on the 2026 download and 0.57
   on Chan's own adjusted column. The price basis alone is worth 0.59 on his
   data, which row 32 computes, so it spends the whole of his margin and row
   34 shows the verdict turning over. A replication that reported only "2.5506
   against 1.26" would have looked comfortable.
4. **The window moves the answer further than the vendor does.** Inside this
   one vintage the leverage runs from a short of 2.82 times equity over 2000 to
   2002 to a long of 4.90 over 2003 to 2007, a spread of 7.72 against a gap of
   0.023 in row 5. So a leverage reported with no window named mixes sample
   choice and vendor drift, and neither is recoverable afterwards. That is why
   the window is an argument and why the default is Chan's own.
5. **On his own data every figure reproduces, and that is all it shows.** Rows
   18 to 25 land on what Chan printed at the precision he printed it, and row
   26 misses only by the rounding he did before multiplying. This is the repo's
   first exact reproduction of a leverage, which makes it the result most
   likely to be over-read. It is exploratory like everything above it: the
   sample was spent on a hypothesis Chan chose, so `reproduced` here means his
   arithmetic is right on his data. It is not evidence that 2.528 is a leverage
   anyone should carry, and the report prints that sentence above the table
   rather than leaving it to this one. It is also the counterpart to Entry 1's
   row 7 rather than its row 6: the same code, on a vintage that was not lost,
   reaching the printed number.

### What this entry cannot say

Two things, and both are the absence of a second series rather than an
oversight.

The 20.47 percent of row 12 is checked against nothing. Checking it needs an
S&P 500 index vintage, which is a different symbol and a different deliverable,
so it is cut and pinned in the design doc's register rather than left as
something a later reader might think was forgotten. The same applies to the 4
percent risk-free rate: a Treasury-bill series would move two inputs at once
and leave every gap above unattributable to either.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/kelly-leverage-on-spy.md](../blog/kelly-leverage-on-spy.md) moves with
it, since that essay quotes most of the figures in rows 1 to 34 and a few this
entry does not carry.

## Entry 4: risk parity against 60/40, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 4684, reporting
Edward Qian's argument. Shipped under
[issue 15](https://github.com/l3a0/quantitative-trading/issues/15).

Twenty-one rows, all derivable from
[tests/test_risk_parity.py](../tests/test_risk_parity.py).

**The allocation lands near Qian's and the ranking goes the other way.** On the
full common span the risk-parity weights are 21.78 to 78.22 against his 23-77,
and the leverage that matches 60/40's volatility is 1.9812 against his 1.8.
Rows 1 and 2 are therefore a percentage point and two tenths out. Row 3 is the
claim those two were printed to support, that the levered risk-parity portfolio
earns a higher Sharpe ratio at the same risk, and at Chan's 4 percent rate
60/40 wins it by 0.2169 with a robust t of −2.17. So this entry is the first
here where a published number lands close and the central claim behind it does
not survive.

Three rows are replications and eighteen are not. Rows 1, 2 and 3 are the three
things location 4684 prints. The other eighteen fall into five groups.

1. **Rows 4 and 5**, the volatility ratio Qian's weights imply and the one
   these two legs measured. They are what row 1's gap is really about.
2. **Rows 6 and 9**, the measured correlation and the one this run's leverage
   implies on Qian's printed weights. The second is row 2 restated in the unit
   his 1.8 is about.
3. **Rows 7, 8 and 10**, the risk decomposition under each allocation and both
   portfolios' Sharpe ratios. The decomposition is the argument the allocation
   rests on, and a weight reported with nothing behind it would be a number
   with no reasoning attached. Row 10 is there because a ranking reported as a
   sign hides its size.
4. **Rows 11 to 15**, the two sub-windows.
5. **Rows 16 to 21**, the same three windows with IWB in place of SPY. IWB
   tracks the Russell 1000, the index Qian's paper reads, so these rows price
   the substitution. Row 21 is what it cost, under a rule
   [issue 160](https://github.com/l3a0/quantitative-trading/issues/160)
   declared before any IWB number existed. SPY stays the equity leg of rows 1
   to 15, because promoting IWB after its numbers were seen would be choosing
   a proxy for its result.

**The sub-window rows carry no verdict either**, because the book makes no
claim about a window. They are what turns rows 1 to 3 into a verdict rather
than verdicts themselves, which is the position Entry 1's rows 2 and 10 are
already in.

**Two things the reader needs before reading a single number.** Both are
specification choices rather than measurements, and both push the same way.

1. **The risk-free rate is Chan's 4 percent constant, and it is not neutral.**
   The run reads no risk-free series and declares Chan's constant, so the rate
   is a specification rather than a rate anyone paid. FRED's TB3MS is
   committed under
   [issue 187](https://github.com/l3a0/quantitative-trading/issues/187), and
   the run does not read it. Only the post's figures do, for the bill
   average. Over this span AGG returned 3.09
   percent a year, so the bond leg's excess return is negative and a 78 percent
   bond weight is carrying it. The direction is exact rather than a guess: the
   Sharpe difference moves with the rate by `1 / vol(60/40)` less
   `1 / vol(risk parity)`, which is negative whenever the unlevered
   risk-parity portfolio is the quieter of the two, and it is on all three
   windows. So a higher assumed rate penalises risk parity and a lower one
   favours it. That derivative is pinned in
   `TestTheRankingIsBuiltOnAPointEstimateLeverageCannotMove`.
2. **No transaction costs and no financing spread are charged**, because the
   book charges none. The omission points one way: a daily rebalance has
   turnover, the levered portfolio has more of it plus a borrowing cost, so
   charging nothing favours the portfolio the book is arguing for. The ranking
   below goes against that portfolio anyway.

Every result here is **exploratory** in the design doc's sense. Reproducing a
figure someone else chose spends the sample on their hypothesis, so this entry
says whether the numbers reproduce and nothing about which allocation anyone
should hold.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Qian's allocation between stocks and bonds | 23-77 | Kindle location 4684 |
| 2 | The leverage on the whole risk-parity portfolio | 1.8 | location 4684 |
| 3 | Qian's claim, a higher Sharpe ratio at 60/40's risk level | a claim rather than a figure | location 4684 |
| 4 | The volatility ratio his weights imply | none, the ratio is derived from row 1 rather than printed | n/a |
| 5 | SPY and AGG annualised volatility, full span | none, the book prints no volatilities | n/a |
| 6 | The stock-bond correlation, full span | none, the book prints no correlation | n/a |
| 7 | The equity leg's risk contribution under 60/40, full span | none, the book states the imbalance without a number | n/a |
| 8 | The risk contributions under the risk-parity weights, full span | none | n/a |
| 9 | The correlation this run's leverage implies on his printed weights | none, this is row 2 read backwards through the same map | n/a |
| 10 | Both portfolios' Sharpe ratios at matched volatility, full span | none, the book prints no Sharpe ratio | n/a |
| 11 | Risk-parity weights and volatility ratio, falling-rates window | none, the book works no window | n/a |
| 12 | The ranking on the falling-rates window | none, the book works no window | n/a |
| 13 | Risk-parity weights and volatility ratio, rising-rates window | none, the book works no window | n/a |
| 14 | The ranking on the rising-rates window, on weights from before it | none, the book works no window | n/a |
| 15 | The leverage that matches 60/40's volatility, both sub-windows, on each window's own weights and on the weights row 14 carries | none, the book works no window | n/a |
| 16 | IWB and AGG annualised volatility, their correlation, the risk-parity weights and both risk splits, full span | none, the book prints no IWB figure | n/a |
| 17 | The leverage, the correlation it implies on his weights, the ranking and both Sharpe ratios on IWB, full span | none, the book prints no IWB figure | n/a |
| 18 | The falling-rates window on IWB | none, the book works no window | n/a |
| 19 | The rising-rates window on IWB, on weights from before it, and its leverage on each window's own weights | none, the book works no window | n/a |
| 20 | The rate at which the IWB ranking ties, and both Sharpe ratios at the bill average, full span | none, the book prints no IWB figure | n/a |
| 21 | What the SPY proxy cost, IWB against SPY on all three windows | none, the book prints no IWB figure | n/a |

### What this repo computed

Every row reads the same price basis under the same rebalancing rule and the
same moments, and rows 1 to 15 read the same two vintages, so all of it is
stated once here rather than in twenty-one cells. Rows 1 to 15 read
`yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv` and
`yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv`, both yfinance's
both-adjustments close, both downloaded 2026-09-18. Rows 16 to 20 read
`yfinance_iwb_adjusted_2000-05-19_2026-10-02_dl2026-10-03.csv` in place of the
SPY file, yfinance's both-adjustments close downloaded 2026-10-03, against the
same AGG file. Row 21 reads all three. IWB holds every day AGG does inside the
span, so rows 16 to 21 run on exactly the days rows 1 to 15 do. The price basis
is adjusted on both legs. The rebalancing rule is constant weights rebalanced
every trading day. The moments are simple daily returns, the mean scaled by
252 and the sample standard deviation, dividing by n−1, by the square root of
252, with a 4 percent annual risk-free rate subtracted as 0.04/252 a day.

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2003-09-30 to 2026-09-17 | inverse-volatility weights, which equalise the risk contributions on two legs | 21.78 to 78.22 | `TestTheFullSpan::test_the_risk_parity_weights_land_about_a_point_off_qians` |
| 2 | 2003-09-30 to 2026-09-17 | the multiple that lifts the risk-parity portfolio's volatility to 60/40's | 1.9812 | `TestTheFullSpan::test_the_leverage_and_what_it_implies` |
| 3 | 2003-09-30 to 2026-09-17 | the two Sharpe ratios at matched volatility, ranked as the mean of their daily excess-return difference | −0.2169, a mean difference of −2.4552 percent a year, robust t −2.1727 at lag 9 | `TestTheFullSpan::test_the_ranking_goes_against_the_book_and_the_window_resolves_it` |
| 4 | none, both operands are published figures | 0.77 divided by 0.23, and the band weights rounding to 23 and 77 admit | 3.3, band 3.26 to 3.44 | `TestTheTwoLegAlgebra::test_qians_printed_weights_are_a_statement_about_volatilities` |
| 5 | 2003-09-30 to 2026-09-17 | annualised standard deviation of each leg's simple daily returns | SPY 18.5472 percent, AGG 5.1650 percent, ratio 3.5909 | `TestTheFullSpan::test_the_leg_moments` |
| 6 | 2003-09-30 to 2026-09-17 | Pearson correlation of the two legs' daily returns | −0.0002 | `TestTheFullSpan::test_the_leg_moments` |
| 7 | 2003-09-30 to 2026-09-17 | `w_i (Sigma w)_i / (w' Sigma w)` at 60/40 | SPY 96.6717 percent, AGG 3.3283 percent | `TestTheFullSpan::test_60_40_is_nearly_all_equity_risk` |
| 8 | 2003-09-30 to 2026-09-17 | the same quantity at the row 1 weights | 50 percent each, exactly | `TestTheFullSpan::test_the_risk_parity_weights_land_about_a_point_off_qians` |
| 9 | none, the map takes no volatility | row 2 inverted through the leverage-to-correlation map on Qian's 23-77 weights | −0.1508, against the +0.1579 his 1.8 implies | `TestTheFullSpan::test_the_leverage_and_what_it_implies` |
| 10 | 2003-09-30 to 2026-09-17 | annualised mean excess return over annualised volatility, both at 11.3181 percent volatility | 60/40 0.4111, levered risk parity 0.1942 | `TestTheFullSpan::test_the_ranking_goes_against_the_book_and_the_window_resolves_it` |
| 11 | 2003-09-30 to 2022-03-15 | the row 1, 5, 7 and 8 specifications, recomputed inside the window | 20.53 to 79.47, SPY 18.8748 percent, AGG 4.8772 percent, ratio 3.8700, correlation −0.0688, 60/40 risk 98.2290 and 1.7710 percent, risk parity 50 percent each | `TestTheTwoSubWindows::test_the_falling_rates_window` |
| 12 | 2003-09-30 to 2022-03-15 | the row 2, 3, 9 and 10 specifications, on weights fitted inside the window because nothing precedes it | leverage 2.1475, implying −0.3299 on his weights, Sharpe 0.3820 against 0.2255, difference −0.1565, mean difference −1.7777 percent a year, robust t −1.3455 at lag 9 | `TestTheTwoSubWindows::test_the_falling_rates_window` |
| 13 | 2022-03-17 to 2026-09-17 | the row 1, 5, 7 and 8 specifications, recomputed inside the window | 26.63 to 73.37, SPY 17.1193 percent, AGG 6.2127 percent, ratio 2.7555, correlation +0.2442, 60/40 risk 90.0043 and 9.9957 percent, risk parity 50 percent each | `TestTheTwoSubWindows::test_the_rising_rates_window` |
| 14 | 2022-03-17 to 2026-09-17 | the row 3, 9 and 10 specifications, on the row 11 weights, which are strictly earlier data | implying +0.5689 on his weights, Sharpe 0.5071 against 0.0097, difference −0.4974, a mean difference of −5.5417 percent a year, robust t −2.1956 at lag 6 | `TestTheTwoSubWindows::test_the_rising_rates_window` |
| 15 | the two windows of rows 11 and 13 | the row 2 specification on each window's own weights, and for the rising window also on the falling window's weights, which are the weights row 14 ranks | 2.1475 falling on its own 20.53 percent stocks, 1.5495 rising on its own 26.63 percent, and 1.6572 rising on the falling window's 20.53 percent | `TestTheTwoSubWindows::test_the_falling_rates_window`, `::test_the_rising_rates_window` and `::test_each_leverage_in_row_15_names_the_weights_it_was_measured_on` |
| 16 | 2003-09-30 to 2026-09-17 | the row 1, 5, 6, 7 and 8 specifications on IWB | IWB 18.4710 percent, AGG 5.1650 percent, ratio 3.5762, correlation −0.0072, weights 21.85 to 78.15, 60/40 risk 96.7630 and 3.2370 percent, risk parity 50 percent each | `TestIWBInPlaceOfSPY::test_the_leg_moments_on_iwb` and `::test_the_weights_and_risk_split_on_iwb` |
| 17 | 2003-09-30 to 2026-09-17 | the row 2, 3, 9 and 10 specifications on IWB | leverage 1.9795, implying −0.1486 on his weights, Sharpe 0.4132 against 0.1962 at 11.2589 percent volatility, difference −0.2171, mean difference −2.4439 percent a year, robust t −2.1619 at lag 9 | `TestIWBInPlaceOfSPY::test_the_leverage_and_ranking_on_iwb` |
| 18 | 2003-09-30 to 2022-03-15 | the row 11 and 12 specifications on IWB, on weights fitted inside the window because nothing precedes it | 20.61 to 79.39, IWB 18.7833 percent, ratio 3.8512, correlation −0.0802, 60/40 risk 98.3945 percent on IWB, leverage 2.1484 on its own 20.61 percent, Sharpe 0.3887 against 0.2314, difference −0.1574, mean difference −1.7754 percent a year, robust t −1.3423 at lag 9 | `TestIWBInPlaceOfSPY::test_the_sub_windows_on_iwb` |
| 19 | 2022-03-17 to 2026-09-17 | the row 13 and 14 specifications on IWB, ranked on the row 18 weights, which are strictly earlier data, and the row 2 specification on each window's own weights, and for the rising window also on the falling window's weights, which are the weights this row ranks | 26.64 to 73.36, IWB 17.1076 percent, ratio 2.7536, correlation +0.2511, 60/40 risk 89.8823 percent on IWB, leverage 1.5467 on its own 26.64 percent and 1.6532 on the falling window's 20.61 percent, and on those Sharpe 0.4872 against 0.0003, difference −0.4869, mean difference −5.4295 percent a year, robust t −2.1556 at lag 6 | `TestIWBInPlaceOfSPY::test_the_sub_windows_on_iwb` |
| 20 | 2003-09-30 to 2026-09-17 | row 17's tie in closed form, and row 17 recomputed at the 1.744 percent TB3MS average | ties at 1.5050 percent, against SPY's 1.4977. At 1.744 percent, Sharpe 0.6136 against 0.5928, difference −0.0208, robust t −0.2071 | `TestIWBInPlaceOfSPY::test_the_tie_rate_and_the_bill_average_on_iwb` |
| 21 | all three windows | the five answers of the rule [issue 160](https://github.com/l3a0/quantitative-trading/issues/160) declared, each instrument on its own weights and leverage and every change IWB less SPY. They are the change in both Sharpe ratios, their difference and the mean difference, then the robust t on the daily change `d_IWB(t) − d_SPY(t)` in the series each ranking is the mean of, then whether any ranking's sign or resolution flips, then IWB's ratio against row 4's band, and last row 20's tie against the bill average | on the full span, falling and rising windows in turn, 60/40's Sharpe changes +0.0021, +0.0067 and −0.0199, risk parity's +0.0019, +0.0059 and −0.0094, the difference −0.0001, −0.0008 and +0.0105, and the mean difference +0.0113, +0.0023 and +0.1122 percent a year. The robust t on that change is +0.2939, +0.0557 and +0.9764. No sign or resolution flips. IWB's ratio is 3.5762, 3.8512 and 2.7536, all outside the band. The tie is 1.5050 percent, under 1.744 | `TestIWBInPlaceOfSPY::test_what_the_proxy_cost` |

**One return falls in neither sub-window and it is the boundary day's.** Rows 11
to 15 run on 4,647 and 1,130 daily returns against the full span's 5,778, one
short. A return spans two closes, so the one dated 2022-03-16 runs from the
2022-03-15 close to the 2022-03-16 close. Row 11's window ends with the return
dated 2022-03-15 and row 13's starts with the one dated 2022-03-17, so this one
belongs to neither. That return covers the day the Federal Reserve announced
its first rate rise of 2022. SPY gained 2.2174 percent that day against AGG's
0.0743 percent. So the return is named here rather than left for a reader to
notice the counts miss by one. Rows 18 and 19 run on the same counts and lose
the same return.
`TestTheTwoSubWindows::test_the_two_windows_cover_the_span_except_the_return_that_straddles_the_cut`
holds that day's two returns, so the arithmetic above stays checkable.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −1 percentage point on the equity leg | reproduced with a gap | Qian's claim is that equalising risk moves the allocation a long way toward bonds, to roughly a quarter equity, and it survives at 21.78 to 78.22. The number misses by a point, and the cause is named and outside the method: the bond proxy. AGG is the aggregate bond exposure his argument describes and it was committed in writing before anything was downloaded, so the proxy explains the gap and was not chosen to close it. Row 4 is why the miss is larger than a point makes it sound. |
| 2 | +0.2 | reproduced with a gap | His claim is that matching 60/40's risk takes roughly double leverage on the risk-parity portfolio, and 1.9812 survives it. On his printed weights the leverage reads the correlation and nothing else, so this row and row 9 are one measurement stated twice, and the gap is the distance between a correlation near zero and the +0.16 his 1.8 implies. |
| 3 | none, the source states a claim | did not reproduce | The replication. At the declared 4 percent rate, 60/40 earns the higher Sharpe ratio at matched volatility, by 0.2169, and the window resolves it at a robust t of −2.17. The instruments and the span offer no cause outside the method. The vintage explanation that carries Entry 1's rows is about a series nobody holds, and this is a claim about two instruments this repo chose in the open on a span every one of whose days is committed here. The rate is the one input that stands in for something Qian measured, the Treasury-bill rate he subtracted. The ranking ties at an assumed 1.50 percent and resolves only at rates above 3.80 percent, and What this entry cannot say gives both. What the entry concludes says what the gap is made of. |
| 4 | none | none, not a replication | Derived from row 1's published pair rather than printed. It is here because it is the quantity the printed weights are a statement about, and because a reader comparing only the weights would call row 1 a near match. |
| 5 | none | none, not a replication | The book prints no volatilities. The measured ratio of 3.5909 sits outside the 3.26 to 3.44 band row 4 gives, which is the sharper reading of row 1's gap. |
| 6 | none | none, not a replication | The book prints no correlation. Over the full span the two legs are uncorrelated to three decimals, at −0.0002, which is a coincidence of averaging rather than a stable fact: rows 11 and 13 give −0.0688 and +0.2442. |
| 7 | none | none, not a replication | Qian's premise, measured. 60 percent of the capital carries 96.67 percent of the risk, so 60/40 is nearly an all-equity portfolio in risk terms and the labels say otherwise. This row is why rows 1 and 2 are worth chasing at all. |
| 8 | none | none, not a replication | Exactly 50 percent each, which is what says the weights of row 1 are the risk-parity weights rather than something near them. |
| 9 | none | none, not a replication | Row 2 in the unit his 1.8 is really about. It is not the measured correlation of row 6 and the two are kept apart, because the map is read on his printed weights and this run's weights are not his. No claim is made about recovering the correlation Qian measured. His 1.8 carries two significant figures and so do his weights, and letting both roundings vary at once opens the band to −0.01265 through +0.37141, wide enough to include both zero and a clearly positive correlation. |
| 10 | none | none, not a replication | The book prints no Sharpe ratio, only the ranking of row 3. Both are stated because a ranking reported as a sign hides its size, and 0.4111 against 0.1942 is not a near miss. |
| 11 | none | none, not a replication | The book works no window. The bond leg is at its quietest here, so the volatility ratio reaches 3.8700 and risk parity holds the least equity it holds anywhere in this entry. |
| 12 | none | none, not a replication | The book works no window. The robust t is −1.3455, so this window does not resolve its own ranking and nothing is read off the sign. Its weights are fitted inside it, because nothing precedes it, and the row says so rather than letting it pass as the out-of-sample row 14. |
| 13 | none | none, not a replication | The book works no window. The bond leg's volatility rises to 6.2127 percent and the ratio falls to 2.7555, which moves the risk-parity weights toward stocks, to 26.63 percent. They do not pass 60, so risk parity still holds less equity than 60/40 and the correction the book argues for still points the same way. |
| 14 | none | none, not a replication | The book works no window. This is the only ranking here whose weights did not see the window they are judged on, and it is the worst of the three for risk parity, at −0.4974 with a robust t of −2.1956. Refitting the weights inside the window moves it in risk parity's favour, which is why it is not done. |
| 15 | none | none, not a replication | The book works no window. On each window's own weights, which is row 2's specification, the leverage runs from 2.1475 to 1.5495, one on each side of his 1.8. That is what says 1.8 is a regime measurement rather than a constant. Row 14 ranks the rising window at 1.6572, which is that window on the falling window's weights. So setting 1.6572 against 2.1475 holds the weights fixed and moves only the window. |
| 16 | none | none, not a replication | The book prints no IWB figure. IWB's volatility is 18.4710 percent against SPY's 18.5472, so the ratio moves from 3.5909 to 3.5762 and stays outside row 4's band, and the equity weight moves by 0.07 of a percentage point. On this window the broader index and the narrower one carry almost the same risk. |
| 17 | none | none, not a replication | The book prints no IWB figure. Every figure but the robust t moves in the third decimal or later, and the t moves by 0.0107. The leverage is 1.9795 against 1.9812, the difference −0.2171 against −0.2169, and the robust t −2.1619 against −2.1727. The ranking still goes against the book and the window still resolves it. |
| 18 | none | none, not a replication | The book works no window. The robust t is −1.3423, so as on SPY this window does not resolve its own ranking and nothing is read off the sign. |
| 19 | none | none, not a replication | The book works no window. Ranked on weights from before it, as row 14 is, it is again the worst of the three for risk parity, at −0.4869 with a robust t of −2.1556. On each window's own weights the leverage runs from 2.1484 to 1.5467 and straddles his 1.8, the way row 15's SPY figures do. |
| 20 | none | none, not a replication | The book prints no IWB figure. The tie moves by less than a hundredth of a point and stays under the 1.744 percent bill average. So at the rate bills actually paid 60/40 still leads on IWB, and the robust t of −0.2071 does not resolve it. |
| 21 | none | none, not a replication | The answer to the question [issue 160](https://github.com/l3a0/quantitative-trading/issues/160) asked, under the rule it declared before any IWB number existed. The swap moved no verdict. No window changes sign or resolution, no change in the mean difference reaches a robust t of 1, and IWB's ratio misses Qian's band on every window as SPY's does. The largest change is the rising window's, +0.0105 of Sharpe difference, against a difference of −0.4974. The paired t belongs to the change in the mean difference rather than to the change in the Sharpe difference, because the two instruments match different volatilities. |

### What the entry concludes

Five things. The first is the one the next three explain, and the fifth says
the first does not rest on the proxy.

1. **The numbers land close and the claim does not survive.** Row 1 misses by a
   percentage point and row 2 by two tenths, which on the five-figure scale
   Entry 3 works at would read as a comfortable reproduction. Row 3 is the
   claim those two were printed to support and 60/40 wins it by 0.2169 of
   Sharpe, resolved at a robust t of −2.17 at the declared 4 percent rate.
   That is the reverse of the split Entries 1 and 3 both found, where most of
   the numbers moved and the central claims held.
2. **The gap is where the return is, not where the risk is.** Row 8 lands on 50
   percent each exactly, so the method did what it says. Row 7 confirms the
   premise it rests on. What fails is the step from a balanced risk split to a
   higher Sharpe ratio, which needs the bond leg to earn enough per unit of
   risk to be worth the leverage. Over this span AGG returned 3.09 percent a
   year against the 4 percent rate the specification assumes, so its excess
   return is negative and levering a 78 percent holding of it 1.98 times
   multiplies that. The rate is a declared choice. The direction it pushes and
   the rate at which row 3 ties, 1.50 percent, follow from it in closed form
   rather than from a search, and What this entry cannot say gives both.
3. **The out-of-sample window is the worst one, which is the direction that
   matters.** Row 14 is the only ranking whose weights came from outside the
   window they are judged on, and it is the largest loss in the entry.
   Refitting inside the window would have improved it, which is the bias the
   separation exists to remove.
4. **The volatility ratio and the leverage are regime measurements rather
   than constants.** Rows 5, 11 and 13 give 3.5909, 3.8700 and 2.7555 against
   Qian's implied 3.3, and the two sub-windows straddle the band from opposite
   sides. So the quantity his 23-77 encodes moved by a third inside one pair of
   instruments, and an allocation derived from it inherits that. The leverage
   follows. Row 15 gives 2.1475 before the boundary and 1.5495 after, each on
   that window's own weights, which straddle his 1.8 the same way. Its third
   figure, 1.6572, is the later window on the earlier window's weights. Set
   against 2.1475 it measures a change of window alone, and it is not the
   leverage the later window's own risk parity needs. This is the same shape as Entry 3's fourth
   conclusion, where the window moved the leverage further than the vendor
   did.
5. **The S&P 500 proxy is not what separates row 3 from Qian's claim.** Rows
   16 to 21 run IWB, which tracks his Russell 1000, on the same window, rate
   and bond leg. No ranking changes sign or resolution, the largest change in
   a Sharpe difference is 0.0105, and no change in the mean difference reaches
   a robust t of 1. So on this window the instrument explains almost none of
   the gap. It moves the equity weight by 0.07 of a percentage point against
   row 1's miss of one, and it moves no verdict. What is left of the
   difference between his inputs and these includes his sample, his monthly
   frequency and his cash rate, which What this entry cannot say gives.

### What this entry cannot say

Four things. One is a missing series, two are choices inherited from the source
or from this repo, and the fourth is a limit of the estimator.

**Whether the ranking survives a real financing cost.** It is charged nothing,
because the book charges nothing, and the omission favours the levered
portfolio. Row 3 goes against that portfolio anyway, so the missing cost makes
the verdict safer rather than shakier, which is the one direction an omission
is allowed to point without being closed.

**Whether a realised short rate reverses row 3.** That needs a run that
charges cash at a Treasury-bill series rather than a constant, which is a
different deliverable, and the design doc's register already carries the same
cut for Entry 3's Kelly example. FRED's TB3MS is now committed, under
[issue 187](https://github.com/l3a0/quantitative-trading/issues/187), and
the run does not read it.
The rate is Chan's constant and the report says so on its own last lines. The
derivative above says which way a lower rate would push, and it also says how
far. The difference is linear in the rate, so row 3 ties at an assumed rate of
1.50 percent, row 12 at 2.45 percent, and row 14 only at −4.43 percent, which
no positive rate reaches. `test_the_rate_at_which_the_two_sharpe_ratios_tie`
pins all three. Row 3's robust t is linear in the rate too, and it reaches −2
at 3.80 percent, so the window resolves the ranking at rates down to 3.80
percent and at none below, a fifth of a point under the declared rate. At a
rate of zero risk parity leads with a t of +1.30, which does not resolve
either. Row 14's t reaches −2 at 3.25 percent in the same way.
`test_the_two_resolved_rankings_resolve_only_down_to_a_little_below_4_percent`
pins all of these. Whether the realised bill rate averaged below 1.50 percent
over the full span decides row 3's sign to first order. The committed series
answers it: TB3MS averaged 1.744 percent over the full calendar months inside
the span, above the tie, which
[tests/test_bill_rates.py](../tests/test_bill_rates.py) pins.

**Whether Qian's own instruments and span reproduce his numbers.** Chan names
neither, so SPY and AGG and this window are this repo's choice, fixed in writing
on [issue 15](https://github.com/l3a0/quantitative-trading/issues/15) before any number was seen. Rows 1 and 2 are therefore a test of the
argument on the instruments and the period this repo picked rather than of his.

Chan calls the source "not publicly distributed" and it is on PanAgora's own
site, which is what makes this a gap somebody could close rather than one nobody
can. A copy is committed at
[research/papers](../research/papers/README.md), so every figure quoted below
is checkable against the document rather than against a link. Qian's "Risk
Parity Portfolios: Efficient Portfolios Through True Diversification",
September 2005, works monthly excess returns over
three-month Treasury bills on the Russell 1000 Index and the Lehman Aggregate
Bond Index from 1983 to 2004, and prints the volatilities, the correlation, the
risk split and both Sharpe ratios this entry has no published counterpart for.
Two cards read it, because the gap splits into an instrument and a sample.
[Issue 160](https://github.com/l3a0/quantitative-trading/issues/160) swapped
the equity leg for one that tracks his index and held everything else fixed,
which ran on free data and is rows 16 to 21.
[Issue 161](https://github.com/l3a0/quantitative-trading/issues/161) reaches his
1983 to 2004 sample and is blocked on licensed history. Three things the split
turns on are worth stating here rather than leaving to those cards.

1. **His window and this one barely overlap.** 1983 to 2004 against
   2003-09-30 to 2026-09-17. The paper gives years rather than months, so
   fifteen months is the most they can share and only if his sample runs to the
   end of 2004. That is about a seventeenth of his and an eighteenth of this
   one. His is the bond bull market and this one carries its reversal.
2. **His bond index is the one AGG tracks.** The Lehman Aggregate was renamed
   to Barclays and then to Bloomberg, and AGG follows it, so the proxy ruling
   was right about the index. What the fund cannot do is reach his span. Its
   first bar is 2003-09-29 and his sample ends in 2004, so it covers the tail of
   his twenty-two years and nothing before it.
3. **His equity leg is the Russell 1000 and SPY is not that.** It is the S&P
   500, which is a narrower index. IWB tracks the Russell 1000 and shares this
   entry's own window, so rows 16 to 21 measured what the substitution costs on
   it, and it moved no verdict. What the instrument cannot answer is his span,
   which is the first item.

His bond index settles the proxy ruling from the source rather than from
argument. The paper's disclosure describes the Lehman Aggregate as roughly
6,000 bonds with an approximate average maturity of ten years. The paper never
says duration and average maturity is not duration, so the reading that this is
an intermediate rather than a long-duration index is this repo's and not his.
It is the reading [issue 15](https://github.com/l3a0/quantitative-trading/issues/15) took when it chose AGG over TLT, before any of this
was read, and a maturity the source states is better evidence for it than the
argument it had.

**How much of the robust t the estimated leverage is worth.** Every t above is
computed on `leverage * parity - bench`, with the leverage estimated from the
same sample as the mean and then treated as a known constant. The sampling
variation in the two standard deviations behind it never enters the variance,
and the bias points toward significance. A moving-block bootstrap that
re-estimates the leverage on every draw, 4,000 resamples at block length 10,
puts the understatement at 2.7 percent on the full span, 2.6 on the falling
window and 1.3 on the rising one. No verdict above turns over, and the full
span's row 3 clears its threshold by 8.6 percent against an understatement of
2.7. Closing it properly needs a bootstrapped or Jobson-Korkie standard error,
which is a second estimator and a different deliverable. The bootstrap is
quoted here as a measurement taken during review rather than as something this
suite pins, the way `README.md`'s `## The write-up` names the figures its
essays quote and the suite does not hold.

The same estimate is why the ranking's point estimate and its error bar are
reported as different things. `sharpe_difference` does not move with the
leverage at all, so row 3's −0.2169 carries no look-ahead. The t does move, and
`TestTheRankingIsBuiltOnAPointEstimateLeverageCannotMove` pins both halves,
including the rising window's spread from −2.1956 to −1.6422 across the two
leverages a reader could defend.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/risk-parity-against-60-40.md](../blog/risk-parity-against-60-40.md)
moves with it, since that essay quotes most of these figures and a few this
entry does not.

## Entry 5: the fixed-income candidate, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 3951. Shipped
under [issue 136](https://github.com/l3a0/quantitative-trading/issues/136),
under the rules
[issue 16](https://github.com/l3a0/quantitative-trading/issues/16) sets for
every stationary candidate Chan names there.

This entry is not a replication. Chan states that "fixed-income instruments
can be found to be cointegrating", and that one can long and short bonds by
the same issuer at different maturities, but he works no example and prints no
number. So the entry carries a finding rather than a verdict, and its tables
drop the published-figure, gap and verdict columns, because no row has
anything to put in them. `### Rows that are not replications` above says why
the route that lets a stated claim carry a verdict does not reach this one.

Six rows, all derivable from
[tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py).

**TLT and IEF do not cointegrate over their shared history, in either
orientation.** With TLT as the dependent leg the statistic is −2.3887, and with
IEF it is −2.3168, both against a 10% bar of −3.04. The one-lag fits leave
autocorrelation the critical values do not allow for. The first fit whose
residuals pass is at 31 lags in both orientations, and there the statistics are
−1.5677 and −1.5387, further from rejecting. The rolling scan finds 56 and 51 of
278 one-year windows clearing 10%, and just over half of those end in 2003-04
or 2020-21.

Every row reads the same stand-ins, vintages and specification, so the three
are stated once here.

1. **The stand-ins.** TLT, which holds Treasuries maturing in twenty years or
   more, and IEF, which holds Treasuries maturing in seven to ten. They are
   one issuer at two maturities, and the step between them and Chan's
   sentence is that each is a rolling basket rather than a bond. Both were
   named on the issue before anything was downloaded, and the owner confirmed
   them on 2026-09-18.
2. **The vintages.** `yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv`
   and `yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv`, both
   downloaded 2026-10-02. The basis is raw on both legs, meaning adjusted for
   splits and not for dividends. Most of a bond fund's return is its
   distributions, so an adjusted pair would drift apart by what the two
   maturities pay rather than by anything about whether their prices are
   tied.
3. **The specification.** The with-intercept Engle-Granger regression in
   levels, one ADF lag, over the full common span of 6,083 days. Both
   orientations are reported, because the test is not symmetric and Chan names
   no dependent leg. The residual check reads ten autocorrelations against the
   ±1.96/√n band and a Breusch-Godfrey test over the same ten lags at the 10%
   cut, and its search stops at Schwert's ceiling of 34 lags. The scan uses
   252-day windows stepped by 21.

Every result here is **exploratory**. The sample was spent on a claim Chan
stated and on stand-ins this repo chose for it, so the entry says whether
these two funds cointegrate over this span and nothing about bonds in general.

### What the book stated

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The claim | fixed-income instruments can be found to be cointegrating, long and short bonds by the same issuer at different maturities | Kindle location 3951 |
| 2 | TLT on IEF, full span | nothing, the book works no example | n/a |
| 3 | IEF on TLT, full span | nothing | n/a |
| 4 | The residual check at one lag, both orientations | nothing | n/a |
| 5 | The first lag count whose residuals pass, both orientations | nothing | n/a |
| 6 | The rolling scan, both orientations | nothing | n/a |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2002-07-30 to 2026-10-01 | rows 2 and 3 read together | neither orientation rejects at 10% | `TestBothOrientations::test_neither_orientation_rejects_even_at_ten_percent` |
| 2 | 2002-07-30 to 2026-10-01 | TLT = α + β·IEF + z, ADF at one lag on z | hedge 1.8632, intercept −74.8326, t −2.3887 on 6,081 observations, half-life 333.2 days | `TestBothOrientations::test_the_fit` |
| 3 | 2002-07-30 to 2026-10-01 | IEF = α + β·TLT + z, ADF at one lag on z | hedge 0.4771, intercept 46.6023, t −2.3168 on 6,081 observations, half-life 376.4 days | `TestBothOrientations::test_the_fit` |
| 4 | 2002-07-30 to 2026-10-01 | the residual check on each one-lag fit | Breusch-Godfrey p 0.0000 both ways, autocorrelations outside the band at residual lags 2 to 10 for TLT on IEF, and at 2 to 10 except 6 for IEF on TLT | `TestTheResidualCheck::test_the_one_lag_fit_fails_it` |
| 5 | 2002-07-30 to 2026-10-01 | the smallest lag count from 0 to 34 whose residuals pass both halves | 31 both ways, t −1.5677 and −1.5387, Breusch-Godfrey p 0.1352 and 0.3223 | `TestTheResidualCheck::test_the_first_fit_that_passes_is_further_from_rejecting` |
| 6 | 278 windows ending 2003-07-29 to 2026-09-11 | 252-day windows stepped by 21, one ADF lag | 56 and 51 clear 10%, 33 and 29 clear 5%, 30 and 29 of the 10% windows end in 2003-04 or 2020-21 | `TestTheRollingScan::test_the_counts` and `::test_rejections_cluster_in_two_stretches` |

### What each row says

| # | Why it is here |
| --- | --- |
| 1 | The finding. Chan's claim does not hold for this pair over this span. A stand-in that fails keeps its failure as the result, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule, so no other pair of funds is tried in its place. |
| 2 | The statistic is 0.65 short of the 10% bar, and row 3's is 0.72 short. The half-life of 333.2 trading days is more than a year, which is a spread that barely pulls back at all. |
| 3 | The other orientation, 0.0719 away from row 2, so this is a pair where the choice of dependent leg could not have turned the finding. On GLD/GDX's full raw history the two orientations sit 0.5352 apart, at −1.2893 and −1.8245. That comparison was measured on [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) and nothing in this suite pins it, because pinning the engine's asymmetry is [issue 127](https://github.com/l3a0/quantitative-trading/issues/127). |
| 4 | The one-lag fits leave autocorrelation at nearly every residual lag, so their statistics are read against critical values that do not apply. |
| 5 | The first fits whose residuals pass are further from rejecting than the one-lag fits, so the check strengthens the finding rather than weakening it. On GLD/GDX the band was the half of the check that decided. Here every autocorrelation is inside the band from 9 lags for TLT on IEF and from 10 for IEF on TLT, and the Breusch-Godfrey half is what holds the passing count at 31. `::test_the_breusch_godfrey_half_is_what_holds_the_count_at_31` pins that. |
| 6 | A description of the span, not a second finding. About one window in five clears 10% each way round. On GLD/GDX's raw history `TestRollingRegime` pins 31 of 231 for GLD on GDX, about one in seven, and pins no figure for the other orientation. No window that rejects is promoted to a claim about the pair, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule. |

### What the entry concludes

Three things, and the first is the finding.

1. **On these two funds, Chan's claim does not hold.** Both orientations fall
   short of the 10% bar, and the fits the residual check allows fall further
   short. That is evidence against TLT and IEF being cointegrated over
   2002-2026. It is not evidence against the claim Chan made, which is that
   such pairs can be found.
2. **The scan finds stretches, not a relationship.** About a fifth of the
   one-year windows reject, and just over half of those end in 2003-04 or
   2020-21, with the rest scattered across the other years. A pair trade sized
   on one of those stretches would have been sized on a window, which is the
   shape `TestRollingRegime` pins for GLD/GDX.
3. **The residual check matters more on a long span than on a short one.** The
   Chapter windows of Entry 1 first pass at 6 and 10 lags. This 6,083-day span
   first passes at 31, and it is the Breusch-Godfrey test rather than the band
   that holds it there. The ceiling on that search was fixed before anything
   was downloaded, so the 31 was found rather than chosen.

### What this entry cannot say

Four things.

**Whether individual bonds behave the way the funds do.** Each fund is a
rolling basket held near a constant maturity, while a bond's own maturity
shrinks every day until it stops trading. Chan's sentence is about bonds, and
these are funds that trade like stocks and have free daily history. Treasury
futures and individual bonds both need data this repo does not hold.

**Whether the yields behind these prices are cointegrated.** That is a related
question, whether the gap between long and intermediate yields stays put. It is a different claim from Chan's, because a yield cannot
be bought or sold, and it would need its own issue and its own stand-in named
before any data is read.

**Whether the finding survives another vintage.** These are raw closes, which
a vendor should restate only when a fund splits, so a later download should
match on every shared day unless one of the two has split by then. Nothing
has checked that against a second yfinance download. The nearest measurement
is SPY's two raw vintages, Chan's 2008 file and a 2026 yfinance download, which
come from two sources and disagree on 2 of the 3,758 days they share with no
split between them.
[tests/test_vintage_overlap.py](../tests/test_vintage_overlap.py) pins that,
and it says two sources can hold different closes rather than that a vendor
rewrote one. The comparison
[issue 139](https://github.com/l3a0/quantitative-trading/issues/139) built,
`chan.series.vintage_overlap`, is what would check TLT and IEF, and no second
download of either is committed.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md)
moves with it, since that post quotes most of these figures. So do its
three figures, which `uv run python -m chan.stationary_candidates_figures`
redraws.

## Entry 6: the CAD/AUD cross rate, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 3951. Shipped
under [issue 135](https://github.com/l3a0/quantitative-trading/issues/135),
under the rules
[issue 16](https://github.com/l3a0/quantitative-trading/issues/16) sets for
every stationary candidate Chan names there.

Nine rows, all derivable from
[tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py).

**Chan's claim reproduces.** The log of the rate rejects a unit root at 5%,
with t −3.2136 at one lag against a bar of −2.86. The one-lag fit leaves
autocorrelation the critical values do not allow for. The first fit whose
residuals pass is at 10 lags, and there t is −2.9946, still past the bar. Both
had to clear it under the criterion
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) declared
before any statistic was computed, and both do. The half-life is 141.6 trading
days, a little over half a year.

One row is a replication and seven are not. Row 1 is the claim, and it takes
the claim route `### Rows that are not replications` describes. Rows 2 and 3
are the two statistics the criterion reads, rows 4 to 6 say what the verdict
rests on, row 7 measures what row 6 can see, and row 8 measures what dropping the
constant or adding a trend would have done, and row 9 models what row 4's
half-life costs a trade.

Every row reads the same series, vintage and specification, so the three are
stated once here. Rows 5, 7 and 8 each change one part of it, and their
specification column says which.

1. **The series.** `CADAUD=X`, yfinance's quote of the rate Chan names, in
   Australian dollars per Canadian dollar. It is the rate itself rather than a
   stand-in for a class of instruments, which is what lets row 1 carry a
   verdict where Entry 5 cannot. The owner confirmed it on 2026-10-02, before
   anything was downloaded.
2. **The vintage.** `yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv`,
   downloaded 2026-10-02. The basis is raw, which for a rate means the vendor's
   close with no adjustment, because none applies. The test reads from
   2007-08-06 to 2026-09-30, 4,984 days, because the vendor returned nothing
   for the 90 weekdays from 2007-04-02 to 2007-08-03 and a lagged regression
   across that gap would treat four months as one day.
   [data/README.md](../data/README.md) says how the rows were filtered.
3. **The specification.** An augmented Dickey-Fuller test with a constant and
   no trend, on the log of the rate, at one lag, against `ADF_CRIT_CONST`. The
   residual check fits the same constant and reads ten autocorrelations against
   the ±1.96/√n band and a Breusch-Godfrey test over the same ten lags at the
   10% cut, and its search stops at Schwert's ceiling of 32 lags. The scan uses
   252-day windows stepped by 21. Entry 5 uses the same lag rule and scan, so
   the two entries read one specification where they can.

Every result here is **exploratory**. The sample was spent on a claim Chan
stated about one named rate, so the entry says whether that rate was
stationary over this window and nothing about whether trading it pays.

### What the book printed

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The CAD/AUD cross rate is quite stationary | the claim, with no figure | Kindle location 3951 |
| 2 | The ADF statistic at one lag | nothing, the book works no example | n/a |
| 3 | The residual check, and the first lag count whose residuals pass | nothing | n/a |
| 4 | The half-life | nothing | n/a |
| 5 | The test on the rate quoted the other way, and on the level | nothing | n/a |
| 6 | The rolling scan | nothing | n/a |
| 7 | How often a series that truly reverts at row 4's half-life rejects in row 6's scan | nothing | n/a |
| 8 | The test with no constant, and with a trend | nothing | n/a |
| 9 | What a known-mean version of the linear rule earns at row 4's half-life | nothing for the rate. *Algorithmic Trading* Example 5.4 gives the 36-day half-life it is set beside | Example 5.4 |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2007-08-06 to 2026-09-30 | rows 2 and 3 read against the declared criterion, both below the 5% bar of −2.86 | both clear it | `TestTheCrossRateVerdict::test_it_is_reproduced` |
| 2 | 2007-08-06 to 2026-09-30 | ADF on the log of the rate, constant, one lag | t −3.2136 on 4,982 observations, rejecting at 5% | `TestTheCrossRateStatistic::test_the_lag_one_statistic` |
| 3 | 2007-08-06 to 2026-09-30 | the residual check on the one-lag fit, then the smallest lag count from 0 to 32 whose residuals pass both halves | one lag fails, Breusch-Godfrey p 0.0002 and residual lags 2, 6, 7 and 10 outside the band. The first passing count is 10, t −2.9946, Breusch-Godfrey p 0.6487 | `TestTheCrossRateResidualCheck::test_the_lag_one_fit_fails_it` and `::test_the_first_fit_that_passes_still_rejects` |
| 4 | 2007-08-06 to 2026-09-30 | OU half-life on the log of the rate | 141.6 trading days | `TestTheCrossRateStatistic::test_the_half_life` |
| 5 | 2007-08-06 to 2026-09-30 | rows 2 and 3 on the log negated, on the level, and on the inverted level | −3.2136 negated. On the level −3.2944 at one lag and −3.0241 at the first passing count, 10. Inverted, −3.1552 and −2.9734, also at 10 | `TestTheCrossRateStatistic::test_the_quoting_direction_does_not_move_it` and `::test_on_the_level_both_statistics_the_verdict_reads_still_reject` |
| 6 | 226 windows ending 2008-07-30 to 2026-09-21 | 252-day windows stepped by 21, row 2's test in each | 23 clear 10% and 5 clear 5% | `TestTheCrossRateScan::test_the_counts` |
| 7 | 1,000 simulated paths of 4,984 days | a Gaussian AR(1) reverting at row 4's half-life, from the stationary distribution, seed 20261002, scanned as row 6 is. Declared on [issue 212](https://github.com/l3a0/quantitative-trading/issues/212) before any number was computed | 27.0 of 226 windows clear 10% on average, 12.0%, and 14.0 clear 5%, 6.2%. 388 paths have 23 or fewer past 10%. 968 reject at 5% over the whole path. Added after the results were seen, not declared: 73 have 5 or fewer past 5% | `TestTheWindowPower` |
| 8 | 2007-08-06 to 2026-09-30 | row 2's test with no constant, on the log as quoted and on the log of the rate per 100, and with a constant and a trend. Added after the verdict, not declared | No constant, −2.5159 on the log, past its 5% bar of −1.94, over a rate that ran from 0.9301 to 1.3239. Per 100, −0.2982 with no constant and −3.2136 with one. With a trend, −3.2947, past the 10% bar of −3.13 and short of the 5% bar of −3.41 | `TestTheCrossRateStatistic::test_without_the_constant_the_answer_rests_on_where_the_rate_sits` and `::test_a_trend_term_would_have_turned_the_verdict` |
| 9 | 2007-08-06 to 2026-09-30, and 400 simulated paths of 4,984 days | a Gaussian AR(1) at row 4's half-life traded at minus its distance from a known mean, no costs. The Sharpe ratio is daily, scaled by √252. Seed 20261005. Added after the verdict, not declared | 0.7845, against 1.5501 at 36 days. On whole years 1.236 against 4.291. The rate sits 10.12 times a day's noise from its mean against 5.12. The test window holds 35.2 half-lives, and one OLS standard error on the slope spans half-lives of 110.1 to 198.2 days. The Kelly leverage at 36 days is 3.88 times the rate's | `TestTheKnownMeanRule` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The criterion was declared on the issue before any statistic was computed: the one-lag statistic and the statistic at the first residual-clean lag count both below the 5% bar. They are −3.2136 and −2.9946. Neither clears 1%, at −3.43, so "quite stationary" holds at the level the criterion asks for and no stronger. |
| 2 | none, not a replication | The headline statistic. Lag 1 was fixed before any number was seen, as the rule [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) set for both candidates. Every count from 0 to the ceiling of 32 also rejects at 5%, the closest being 6 at −2.8739, so the lag rule does not decide the verdict here. `::test_every_lag_up_to_the_ceiling_rejects_at_five_percent` pins that. |
| 3 | none, not a replication | The one-lag fit leaves autocorrelation, so its statistic is read against critical values that do not apply. The fit that earns them is further from rejecting and still past the bar. Without the constant the check would audit a different regression, whose one-lag statistic is −2.5159 rather than −3.2136 and is read against a different table, so the check would no longer be about this test. |
| 4 | none, not a replication | The book prints no half-life. At 141.6 trading days a deviation takes a little over half a year to halve, which is a rate that pulls back slowly. |
| 5 | none, not a replication | Chan writes CAD/AUD without saying which currency is the unit, and a rate can be quoted either way round, so the test was run on the log, where the two directions give one answer. On the level they part, and both statistics the verdict reads still reject at 5% in both directions, so the scale did not decide the verdict either. |
| 6 | none, not a replication | A description of the window, not a second verdict. About one window in ten clears 10%. A 252-day window holds under two half-lives of the full window's estimate. No window that rejects is promoted to a claim, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule. Three windows have no finite half-life, because their fit does not revert. |
| 7 | none, not a replication | A measure of row 6's power. A series that certainly reverts this slowly clears 10% in 12.0% of its windows, against about one in ten for a series that does not revert at all, which is what a 10% bar means. So row 6 barely separates the two, and only the whole span does: it rejects at 5% in 968 of 1,000 paths. Row 6's 23 sits near the middle of the simulated counts. At 5% only 73 paths have 5 or fewer, as the rate does, a number added after the results were seen. The model has neither the rate's fat tails nor its changing volatility, and a half-life estimated from 4,984 days reads short, so the true reversion may be slower than row 4's. This shows that slow reversion can produce so few rejecting windows, and not that it is why the rate does. Exploratory. |
| 8 | none, not a replication | A measure of the declared constant and missing trend, computed after the verdict. With no constant the test asks whether the rate reverts to 1.00, and it rejects only because the rate stayed close to 1.00, since the same rate per 100 finds nothing. A trend asks whether the rate reverts around a drifting line, which is not Chan's claim, and it would have turned the verdict at 5%. [Issue 135](https://github.com/l3a0/quantitative-trading/issues/135) fixed a constant and no trend before any statistic, and these two checks show that choice could have turned the answer. Exploratory. |
| 9 | none, not a replication | A model of what the half-life alone costs a trade, computed after the verdict. Its figures are long-run averages rather than bounds, and the rule knows the mean Chan's rule estimates. The blog post's Lesson 6 reads it. It runs no trade on the rate, so it says nothing about whether trading the rate pays. Exploratory. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Chan's claim reproduces at 5% on a modern download.** Over 2007-2026 the
   CAD/AUD rate rejects a unit root under the criterion fixed before the
   statistic was read, on both statistics the criterion names. Every lag count
   up to the ceiling rejects too, and so does the level in either quoting
   direction. The log, a constant with no trend, and the window start were
   fixed on the issue before any statistic. Only the scale, the constant and
   the trend were tried another way afterwards, and row 8 reports that a trend
   would have turned the verdict at 5%.
2. **It is a slow reversion, and only the whole window shows it.** A half-life
   of 141.6 trading days means a deviation takes a little over half a year to
   halve, and only 23 of 226 one-year windows reject at 10%. Over the full
   window the rejection holds, and in a year of data it usually does not.
   Row 7 measures what a year of data can see. A simulated series that truly
   reverts at this half-life clears 10% in 12.0% of its one-year windows,
   against about one in ten for a series that does not revert, and rejects
   over its whole span in 968 of 1,000 paths. So the windows barely tell the
   two apart, the rate's 23 can come from either, and the whole-window
   rejection is what separates them. At 5% the rate's 5 windows are fewer
   than most simulated paths give, which row 7 reports and does not explain.
3. **The residual check moves the statistic and not the verdict.** The one-lag
   fit fails it, as Entry 5's one-lag fits do, and the first passing fit is at
   10 lags. That fit still rejects, closer to the bar than the one-lag fit, so
   here the check narrows the margin rather than reversing anything.

### What this entry cannot say

Four things.

**Whether the rate behaved the same before August 2007.** The vendor's history
starts in July 2005, and the 454 rows before its gap are kept in the vintage
and not read by the test, so the two years before the window are untested.

**Whether the result survives another vintage.** The vendor does not restate an
FX close for a corporate action, because a currency has none, but it can fill
or change its own history, and the 2007 gap is the sign that its history has
holes. `TestTheCrossRateVintage::test_the_gap_the_start_rests_on_is_in_the_vintage`
fails if a recorded download fills the gap, so the window cannot quietly move.

**Whether trading the rate pays.** Stationarity is a statement about the
series. A trade adds costs, carry from the two interest rates, and the
question of sizing against a half-life this long, and no trade on the rate is
run here. Row 9 models only what the half-life costs an idealised trade.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md)
moves with it, since that post quotes most of these figures. So do its
three figures, which `uv run python -m chan.stationary_candidates_figures`
redraws.

## Entry 7: the equity seasonals, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Examples 7.6 and 7.7, in both editions. Rows 1
to 18 shipped under
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18), and rows 19
to 21 under [issue 225](https://github.com/l3a0/quantitative-trading/issues/225).
Rows 22 to 29 shipped under
[issue 254](https://github.com/l3a0/quantitative-trading/issues/254), rows
30 to 34 under [issue 333](https://github.com/l3a0/quantitative-trading/issues/333),
rows 35 to 40 under
[issue 329](https://github.com/l3a0/quantitative-trading/issues/329), and rows
41 to 49 under [issue 336](https://github.com/l3a0/quantitative-trading/issues/336).

Forty-nine rows, all derivable from
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py).

**Every figure the committed files reach reproduces, in every printout.** Chan
prints these two examples in four ways: the first edition's MATLAB, and the
revised edition's MATLAB, Python and R. Seventeen printed figures need only
data this repo holds, and all seventeen land on the digits their source prints. None
of them lands from the strategy's description alone. Each needs the rules its
own script applies, and the issue records the figure each rule gives when it is
changed.

Chan publishes both strategies as already dead, so reproducing them checks
whether a documented disappearance is visible in data a reader can get. Every
printout's whole-period figure is negative on his files, as he printed it. What
the files cannot show is the 13 percent before 2002 that a disappearance would
be measured against, so this entry gives no verdict on one.

Each example reads one of two vintages.

1. **Example 7.6** reads `data/ijr_20080131/`, the 600 S&P 600 members lifted
   from Chan's `IJR_20080131.mat`, the file his script loads, vendor
   `chan-mat`, recorded as split-adjusted, saved 2008-02-02, spanning
   2004-01-15 to 2008-02-01. It comes from a repost of the revised edition's
   code rather than from the mirror, which does not hold it.
2. **Example 7.7** reads `data/spx_20071123/`, the 500 S&P 500 members lifted
   from `SPX_20071123.mat`, the same vendor and basis, saved 2007-11-24,
   spanning 1999-11-24 to 2007-11-23.

[data/README.md](../data/README.md) holds both, and says why the repost is
trusted. Each file holds only the companies in its index on the day Chan saved
it, carried backwards, which is the first thing this entry cannot get past.

Rows 30 to 34 read neither file. They run Example 7.6 on the 603 companies IJR
held at 2025-12-31, from IJR's Form N-PORT at accession `0000940400-26-007526`
as `research/filings/ijr/2025-12-31.csv` records it, carried back to 2007.
Their closes are Alpha Vantage's adjusted closes, the 603 lines of the `sp600`
cross-section in `data/archive_vintages.jsonl`, downloaded 2026-10-05, with
the bytes in the owner's archive. The committed raw SPY vintage downloaded on
2026-10-03 is the calendar.

Rows 35 to 40 read neither file either. They run Example 7.6 on the members
IJR held at each year-end from 2008 to 2025, as
`research/filings/ijr/members.csv` records them, at sha256 `c92cc251`. That
file maps each member to an Alpha Vantage ticker and records whether the
series' raw close agrees with the filing.
[Issue 332](https://github.com/l3a0/quantitative-trading/issues/332) built it.
Their closes are the adjusted closes of the 1,487 `sp600` lines it maps to,
all downloaded 2026-10-05, and the calendar is the same SPY vintage.

Rows 41 to 49 read neither of Chan's files. They run Example 7.7 on the
members IVV's 70 quarter-end schedules list from 2008-12-31 to 2026-06-30, each
carried forward to the next, as `research/filings/ivv/members.csv` records
them, at sha256 `0b8e0f8c`, with the holes file beside it at `85c6c949`.
[Issue 373](https://github.com/l3a0/quantitative-trading/issues/373) built
both. Their closes are the adjusted closes and volumes of the 817 `sp500` lines
the members file maps to, all downloaded 2026-10-05, read from 2007-12-03 to
2026-10-01, and the calendar is the same SPY vintage.

Rows 1 to 6 first ran on an earlier save, `data/ijr_20080114/`, saved
2008-01-15 and ending on 2008-01-14, which stops short of January 2008's
month-end. The two saves give rows 1 to 6 to every digit.
`chan.series.vintage_overlap` and `departures` find their closes differing on
198 of 589,660 shared days, in 42 stocks, all between 2008-01-07 and
2008-01-14, and the first two Januaries read no close after 2007-01-31.
`TestTheTwoSmallCapSaves` holds both.

The specification is the script. Rows 1 to 6 are Example 7.6, rows 7 to 14 are
Example 7.7, rows 15 to 18 split one of them at 2002, rows 19 to 21 are
Example 7.6's third January, rows 22 to 29 are p. 180's most recent five
years, rows 30 to 34 are Example 7.6 from January 2009 to January 2026 on
IJR's members at 2025-12-31, rows 35 to 40 are the same Januaries on IJR's
members at each year-end, and rows 41 to 49 are Example 7.7 from January 2009
to September 2026 on IVV's members each month. Each row names the
printout whose rules it runs, and `chan.equity_seasonals` holds those rules as
`JANUARY_RULES` and `HESTON_SADKA_RULES`.

Two of the four printouts have no code file in this repo. The revised
edition prints its Example 7.7 in MATLAB on p. 179 and in R on p. 181, and the
owner read both listings from the Kindle book on 2026-10-03.
[Issue 226's comment on the printed code](https://github.com/l3a0/quantitative-trading/issues/226#issuecomment-5973504942) quotes the expressions that
decide each rule, and rows 9, 10, 13 and 14 run those rules.

1. **The R needs no repair**, because it indexes the daily closes, and
   `R_HESTON_SADKA` follows it with no change.
2. **The MATLAB needs one repair to run.** It cuts its closes to month-end rows
   and then reads one by a daily row number. `REVISED_MATLAB` reads the
   month-end row instead and follows the listing everywhere else.
3. **The page leaves `smartstd` open.** The listing calls it, and pp. 179 to
   181 do not print its body. Chan's two books ship two versions, and only
   *Algorithmic Trading*'s prints row 10's digits.
4. **The revised code's repost settles both.** The revised edition's MATLAB as
   reposted at pinhaocheng/epchan-quant_trading_MATLAB_codes `7430b84` holds an `example7_7.m` whose mask already
   reads the month-end row, and which matches `REVISED_MATLAB` everywhere
   else, down to the −0.0129 and −0.1243 in its closing comment. Its
   `smartstd.m` divides by n, which is book two's. The repost is a third
   party's copy rather than the book, so the page stays the source for rows 9
   and 10, and the repost is what confirms the two choices the page does not
   decide.

Rows 5, 6 and 21, and the revised edition's half of rows 1, 2 and 19, rest on
a different inference: the figures match the first edition's, so its rules are
assumed.

Every result in rows 1 to 34 is **exploratory**. A replication spends the sample on a
hypothesis Chan chose, and rows 15 to 18 were computed before any criterion for
"disappeared" was written down. Row 22's criterion was written first, so it
carries a verdict, and the verdict is about Chan's file of survivors rather
than about the effect.

Rows 30 to 34 are **survivor-only** and **exploratory**, and they carry no
verdict even though their criterion was written on
[issue 333](https://github.com/l3a0/quantitative-trading/issues/333) before
any return was computed. Data tilted toward the effect can speak in one
direction only. The companies that left the index before 2025-12-31 are
missing, so the losers held long are the ones that recovered and the winners
held short are mostly the ones that stalled. A mean not detectably above zero
bounds the effect even on that data, at the X the test detects with 80%
probability. A mean above zero would have said nothing, because the bias alone
could produce it.

Rows 35 to 40 are **registered**, the first rows in this log to carry that
label. [Issue 329](https://github.com/l3a0/quantitative-trading/issues/329)
wrote the claim, the test, the bar and the wording of the verdict before any
return was computed, and the owner labelled it registered on 2026-10-04. The
claim is that Example 7.6 earns no January return detectably above zero in the
Januaries after the book was published. The panel keeps the companies that
left the index, but it does not cover every member. A member is covered when
its series passes the filing check at the year-end and, where it was in the
filing before, at that year-end too. Covered members run from 425 of 600 at 2010-12-31 to 601 of 603 at
2025-12-31. A missing member counts toward the tenth. Where one could change a
tenth, the January is computed twice, with each threatening member inserted
into the tenth it threatens at the 1st or the 99th percentile of that
January's covered returns. Every year-end has such a member, 741 member-years
in all, so every January is bounded.

Rows 41 to 49 are **registered** too.
[Issue 336](https://github.com/l3a0/quantitative-trading/issues/336) wrote the
claim, the test, the bar and the wording of the verdict before any return was
computed, and the owner ruled on them and on the label on 2026-10-04. The claim
is that Example 7.7 earns no return detectably above zero in the months after
the book, under `REVISED_MATLAB` unchanged and before costs. A member is
covered at a month-end when `chan.sp500_panel.monthly_coverage` counts its
series as checked there. Each series stops at its last row that traded and
moved, which moves the stop of 121 of the 817. A missing member is dropped,
as the owner ruled, so the tenth is a tenth of the covered members and no
month is bounded. Coverage is 98,321 of 107,115 member-months, lowest at 364
of 501 in 2012-09 and highest at 501 of 503 in 2025-09. Row 49 tests the
argument that dropping a missing member is neutral, and the verdict cell for
rows 42 to 49 says what it found.

### What the book printed

| # | Row | Published | Where |
| --- | --- | --- | --- |
| 1 | 7.6, entered 2005-12-30, MATLAB in both editions | −0.0244 | `example7_6.m` at `1a71950`, printed in its closing comment. The revised edition prints the same figure, which the owner read on 2026-10-02 |
| 2 | 7.6, entered 2006-12-29, MATLAB in both editions | −0.0068 | as row 1 |
| 3 | 7.6, exited 2006-01-31, revised Python | −0.023853 | `example7_6.py` at `653cf92` in liujiantong/epchan_books, printed in its closing comment |
| 4 | 7.6, exited 2007-01-31, revised Python | −0.003641 | as row 3 |
| 5 | 7.6, January 2006, revised R | −0.0244 | the revised Kindle edition, as the owner read it on 2026-10-02 |
| 6 | 7.6, January 2007, revised R | −0.0068 | as row 5 |
| 7 | 7.7 average annual return, first-edition MATLAB | −0.9167 | `example7_7.m` at `1a71950`, printed in its closing comment |
| 8 | 7.7 Sharpe ratio, first-edition MATLAB | −0.1055 | as row 7 |
| 9 | 7.7 average annual return, revised MATLAB | −0.0129 | the revised Kindle edition, p. 179, in the listing's closing comment, as the owner read it on 2026-10-02 and 2026-10-03 |
| 10 | 7.7 Sharpe ratio, revised MATLAB | −0.1243 | as row 9 |
| 11 | 7.7 average annual return, revised Python | −0.012679 | `example7_7.py` at `653cf92`, printed in its closing comment |
| 12 | 7.7 Sharpe ratio, revised Python | −0.122247 | as row 11 |
| 13 | 7.7 average annual return, revised R | −0.01139674 | the revised Kindle edition, p. 181, read on the same two days as row 9 |
| 14 | 7.7 Sharpe ratio, revised R | −0.1095098 | as row 13 |
| 15 | 7.7 annual return before 2002 | more than 13 percent, Heston and Sadka's sample rather than this file | Kindle location 4425 |
| 16 | 7.7 Sharpe ratio before 2002 | nothing | n/a |
| 17 | 7.7 annual return from 2002 | the effect "has disappeared since then" | Kindle location 4425 |
| 18 | 7.7 Sharpe ratio from 2002 | nothing | n/a |
| 19 | 7.6, entered 2007-12-31, MATLAB in both editions | 0.0881 | as row 1 |
| 20 | 7.6, exited 2008-01-31, revised Python | 0.088486 | as row 3 |
| 21 | 7.6, January 2008, revised R | 0.0881 | as row 5 |
| 22 | 7.7 average annual return over the most recent five years, revised MATLAB | "even worse" than the whole period, a claim, no figure | the revised Kindle edition, p. 180, directly after the MATLAB listing, as a session read it in the Kindle Cloud Reader on 2026-10-03 |
| 23 to 29 | row 22's Sharpe ratio, the same two figures over the full run's last 60 months, and all four under the revised Python's rules | nothing | n/a |
| 30 | 7.6, mean January return before costs, January 2009 to January 2026, IJR's members at 2025-12-31 | nothing, the book prints no figure for these Januaries | n/a |
| 31 to 34 | row 30's standard deviation, its one-sided t-test, the mean the test detects with 80% probability, and the mean after costs | nothing | n/a |
| 35 | 7.6, mean January return before costs, January 2009 to January 2026, IJR's members at each year-end, the low and the high series | nothing, the book prints no figure for these Januaries | n/a |
| 36 to 40 | row 35's standard deviations, each series' one-sided t-test, the mean each detects with 80% probability, the means after costs, and row 30's mean less row 35's | nothing | n/a |
| 41 | 7.7, mean monthly return before costs, January 2009 to September 2026, IVV's members each month | nothing, the book prints no figure for these months | n/a |
| 42 to 49 | row 41's standard deviation, its one-sided t-test, the annual return the test detects with 80% probability, the same figures under the revised Python's rules, the means on the two bracketing masks, and three counts: positions on names that changed between schedules, positions whose stock stopped inside the month, and where departing names fall | nothing | n/a |

None of rows 1 to 14 and 19 to 21 is among the committed highlights, because each is printed
beside code rather than in a sentence somebody marked. Row 22's sentence is not
among them either, and
[issue 254](https://github.com/l3a0/quantitative-trading/issues/254) records
when it was read.
[research/book-notes/README.md](../research/book-notes/README.md) records that
absence. Rows 5, 6, 9, 10, 13, 14 and 21 trace to
[the owner's comment on issue 18](https://github.com/l3a0/quantitative-trading/issues/18#issuecomment-5960594931),
which tables every figure the revised edition prints for both examples. The
code behind rows 9, 10, 13 and 14 traces to
[the comment on issue 226](https://github.com/l3a0/quantitative-trading/issues/226#issuecomment-5973504942).

### What this repo computed

| # | Printout's rules | Computed | Gap, computed minus published | Assertion |
| --- | --- | --- | --- | --- |
| 1 | `MATLAB_JANUARY`: month-ends by row, the number of stocks in a tenth rounded half away from zero, 58 long and 58 short of 578 ranked | −0.0244 | 0.0000 | `TestJanuaryMatlab::test_the_three_januaries_reproduce` |
| 2 | as row 1, 59 long and 59 short of 592 ranked | −0.0068 | 0.0000 | as row 1 |
| 3 | `PYTHON_JANUARY`: year-end closes forward-filled before ranking, as pandas before 3.0 did, and a winners' slice of `topN - 2` that leaves out the best, 58 long and 56 short of 579 ranked | −0.023853 | 0.000000 | `TestJanuaryPython::test_the_three_januaries_reproduce` |
| 4 | as row 3 | −0.003641 | 0.000000 | as row 3 |
| 5 | `R_JANUARY`: row 1's rules with R's half-to-even rounding | −0.0244 | 0.0000 | `TestJanuaryR::test_the_three_januaries_reproduce` |
| 6 | as row 5 | −0.0068 | 0.0000 | as row 5 |
| 7 | `FIRST_EDITION_MATLAB`: month-ends by row, a stock kept or dropped on another stock's close because a sorted row is read against one in column order, a monthly sum over positions, `smartmean` over 95 months and `smartstd` | −0.9167 | 0.0000 | `TestHestonSadkaFirstEdition::test_both_figures_reproduce` |
| 8 | as row 7 | −0.1055 | 0.0000 | as row 7 |
| 9 | `REVISED_MATLAB`: the printed code with its out-of-range index repaired, each stock kept only if its own close exists, each month divided by its positions, 83 months, *Algorithmic Trading*'s `smartstd` | −0.0129 | 0.0000 | `TestHestonSadkaRevisedMatlab::test_both_figures_reproduce` |
| 10 | as row 9 | −0.1243 | 0.0000 | as row 9 |
| 11 | `PYTHON_HESTON_SADKA`: each stock's last priced day, kept only if its own return exists, 83 months, standard deviation over n | −0.012679 | 0.000000 | `TestHestonSadkaPython::test_both_figures_reproduce` |
| 12 | as row 11 | −0.122247 | 0.000000 | as row 11 |
| 13 | `R_HESTON_SADKA`: the printed code, row 9's selection with half-to-even rounding, 83 months, standard deviation over n − 1 | −0.01139674 | 0.00000000 | `TestHestonSadkaR::test_both_figures_reproduce` |
| 14 | as row 13 | −0.1095098 | 0.0000000 | as row 13 |
| 15 | row 11's months from 2000-12-31 to 2001-12-31, 13 of them | −0.145387 | none, not a replication | `TestTheSplitAt2002::test_the_two_halves` |
| 16 | as row 15 | −0.859993 | none | as row 15 |
| 17 | row 11's months from 2002-01-31 to 2007-10-31, 70 of them | 0.011967 | none, not a replication | as row 15 |
| 18 | as row 17 | 0.141777 | none | as row 15 |
| 19 | as row 1, 59 long and 59 short of 594 ranked | 0.0881 | 0.0000 | as row 1 |
| 20 | as row 3, 60 long and 58 short of 595 ranked | 0.088486 | 0.000000 | as row 3 |
| 21 | as row 5 | 0.0881 | 0.0000 | as row 5 |
| 22 | `REVISED_MATLAB` rerun unchanged on the rows of `spx_20071123/` after 2002-11-23, keeping 47 months from 2003-12-31 to 2007-10-31, and read against row 9 | −0.0165 against −0.0129, so it holds | none, a claim | `TestTheMostRecentFiveYears::test_the_revised_matlab_reproduces_the_claim` |
| 23 | as row 22 | −0.2963 | none | `TestTheMostRecentFiveYears::test_the_revised_matlab_figures_with_no_verdict` |
| 24 | row 9's last 60 kept months, 2002-11-29 to 2007-10-31 | −0.0171 | none | as row 23 |
| 25 | as row 24 | −0.2609 | none | as row 23 |
| 26 | `PYTHON_HESTON_SADKA` rerun as row 22, and read against row 11 | −0.016431 against −0.012679 | none | `TestTheMostRecentFiveYears::test_the_revised_python_beside_it_with_no_verdict` |
| 27 | as row 26 | −0.294952 | none | as row 26 |
| 28 | row 11's last 60 kept months, 2002-11-30 to 2007-10-31 | −0.017011 | none | as row 26 |
| 29 | as row 28 | −0.259985 | none | as row 26 |
| 30 | `MATLAB_JANUARY` unchanged, in one call on the closes from 2007-12-01 to 2026-10-02: 18 Januaries, from 36 long and 36 short of 362 ranked to 60 long and 60 short of 598 ranked, each return with its two one-way costs added back | 0.0108 | none, survivor-only and exploratory | `TestTheSurvivorPins::test_the_mean_is_not_detectably_above_zero` |
| 31 | the standard deviation of row 30's 18 Januaries, with one degree of freedom removed | 0.0398 | none | as row 30 |
| 32 | a one-sided t-test of row 30 against zero at 5%, at 17 degrees of freedom | t 1.15, p 0.132 | none | as row 30 |
| 33 | the smallest mean the test detects with 80% probability at row 31's deviation, from the noncentral t | 0.0243 | none | `TestTheSurvivorPins::test_x_is_2_4_percent_a_january` |
| 34 | row 30 after the two one-way costs of 5 basis points | 0.0098 | none | `TestTheSurvivorPins::test_the_mean_after_costs` |
| 35 | `MATLAB_JANUARY` unchanged, one year-end at a time on its covered members, with the tenth taken of the ranked covered members plus every missing member, from 59 long and 59 short of 433 ranked to 60 long and 60 short of 598 ranked. Every January is bounded, low then high | −0.1047 and 0.0879 | none, registered | `TestThePointInTimePins::test_the_low_series_is_not_above_zero` and `test_the_high_series_is_above_zero` |
| 36 | the standard deviation of each series' 18 Januaries, with one degree of freedom removed | 0.0896 and 0.1007 | none | as row 35 |
| 37 | a one-sided t-test of each series against zero at 5%, at 17 degrees of freedom | t −4.96, p 1.000, and t 3.70, p 0.001 | none | as row 35 |
| 38 | the smallest mean each test detects with 80% probability at its own deviation | 0.0547 and 0.0615 | none | `TestThePointInTimePins::test_x_for_each_series` |
| 39 | row 35 after the two one-way costs of 5 basis points | −0.1057 and 0.0869 | none | `TestThePointInTimePins::test_the_means_after_costs` |
| 40 | row 30's mean less row 35's, described rather than tested. The per-January differences print from `--point-in-time`, and the same test pins them | 0.1155 and −0.0771 | none | `TestThePointInTimePins::test_the_survivor_run_less_this_one` |
| 41 | `REVISED_MATLAB` unchanged, on the closes from 2007-12-03 to 2026-10-01, each series stopped at its last row that traded and moved, each month-end ranking only its covered members: 98,321 of 107,115 member-months, from 364 of 501 in 2012-09 to 501 of 503 in 2025-09. The 213 months from January 2009 to September 2026 | −0.0001 a month | none, registered | `TestTheMonthlyPins::test_the_revised_matlab_mean_is_not_detectably_above_zero`, `test_98321_of_107115_member_months_are_covered_with_83_stops` and `test_the_lowest_and_highest_months_coverage` |
| 42 | the standard deviation of row 41's 213 months, with one degree of freedom removed | 0.0206 a month | none | `TestTheMonthlyPins::test_the_revised_matlab_mean_is_not_detectably_above_zero` |
| 43 | a one-sided t-test of row 41 against zero at 5%, at 212 degrees of freedom, and beside it the Newey-West t at lag 4, whose standard error is 0.0013 | t −0.10, p 0.539, Newey-West t −0.11 | none | as row 42, and `test_the_newey_west_t_beside_it` |
| 44 | the smallest monthly mean the test detects with 80% probability at row 42's deviation, from the noncentral t, times 12 | 4.22% a year | none | `TestTheMonthlyPins::test_x_is_4_22_percent_a_year` |
| 45 | `PYTHON_HESTON_SADKA` on the same panel and members. Its months are labelled by the month's last calendar day, so January 2009 is 2009-01-31 rather than 2009-01-30 | rows 41 to 44 to every digit, and every month equal | none | `TestTheMonthlyPins::test_the_revised_python_with_no_verdict` and `test_the_two_rules_agree_on_every_month` |
| 46 | row 41 rerun on the two masks that bracket each name changing between schedules. The intersection keeps a name only where both schedules list it, and the union where either does | −0.0004 and −0.0000 a month | none | `TestTheMonthlyPins::test_the_intersection_and_union_means_with_no_verdict` |
| 47 | positions in the months between two schedules held on a name that changed: those the carry-forward run gave a removed name, then those the union run gave an added name. The 69 pairs of schedules removed 500 names and added 503 | 216 and 162, 378 in all | none | `TestTheMonthlyPins::test_the_positions_on_names_that_changed_per_pair_and_in_total` and `TestTheScheduleChanges::test_500_names_removed_and_503_added_over_69_pairs` |
| 48 | positions whose stock stopped strictly between the month-end that set them and the next, and their returns summed, each signed by its side | 23, summing to −0.7013 | none | `TestTheMonthlyPins::test_23_positions_stopped_inside_the_month_held` |
| 49 | covered member-months from ranking months 2008-12 to 2025-08, split by whether the name leaves the index within twelve months, and placed long, short or neither by row 41's rules. Described rather than tested | departing 12.0%, 16.5% and 71.5%, staying 9.8%, 9.6% and 80.6% | none | `TestTheMonthlyPins::test_departing_names_fall_in_a_tenth_more_often` |

Each of rows 1 to 14 and 19 to 21 is asserted twice: its full value at `abs=1e-9`, and its
rounding at the precision its source prints. So the computed column quotes the
printed precision, and the gap is zero at that precision. Rows 22 to 29 are
asserted the same way, at the precision their printout's rules print, and have
no published figure to take a gap from.

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The script's date check passes on the file it loads, which holds four December year-ends and five January month-ends. It drops the first January, and each December keeps the January after it. On the earlier save the check fails, because that file holds four of each, and dropping the first January leaves three dates to compare against four. Rounding the decile down instead gives −0.0234. |
| 2 | reproduced | as row 1 |
| 3 | reproduced | Taking the full top decile instead gives rows 1 and 2 to every digit, so in 2006 and 2007 the two editions differ by the winners' slice alone. Without the forward fill the script ranks 578, as MATLAB does, and the return does not move. |
| 4 | reproduced | as row 3 |
| 5 | reproduced | Inferred rules, as the entry's opening says. No decile on this file lands on a half, so R's rounding and MATLAB's give the same stocks. |
| 6 | reproduced | as row 5 |
| 7 | reproduced | The return is a sum over every position held that month, never divided by their number, so −0.9167 is in units of summed positions rather than a fraction of capital. Keeping each stock on its own close instead gives −1.0822, and averaging over the 83 months that hold positions gives −1.0492. Dividing each month by its positions gives −0.0120 a year, a figure this repo derived and Chan did not print. |
| 8 | reproduced | Skipping the NaN month in the standard deviation instead of counting it as zero gives −0.1049. |
| 9 | reproduced | The printed code with one repair. As printed, it reads a daily row of a 96-row array and cannot run. The repair reads the month-end row, and because the printed mask removes stocks by column, it keeps each stock on its own close. Keeping the first edition's sorted-against-columns rule instead gives −0.0120 and does not print. Keeping each stock on its own return also prints −0.0129, so the code chooses the close where four decimals cannot. |
| 10 | reproduced | As row 9. Pp. 179 to 181 do not print `smartstd`, and the revised code's repost ships book two's. *Algorithmic Trading*'s, which skips a month with no position and divides by n, prints −0.1243. The first edition's gives −0.1236. Every month the drop removes holds no position, so under the former the drop count moves no figure. Under the first edition's it does: dropping 12 also prints −0.1243 by counting one empty month as zero, which is the reading this row ran before the code was read, and dropping none gives −0.1330. |
| 11 | reproduced | Taking one shared row per month instead gives −0.012917. |
| 12 | reproduced | Dividing by n − 1 instead gives −0.121508. |
| 13 | reproduced | The printed code, unchanged, and the tightest of rows 9 to 14, because R prints seven significant digits. Rounding half away from zero instead gives −0.0118031, and keeping each stock on its own return gives −0.0117146. |
| 14 | reproduced | Dividing by n instead gives −0.1101755. |
| 15 | none, not a replication | Heston and Sadka's 13 percent is from their own sample, which this file does not reach. It has 13 months before 2002 after the twelve-month lookback, and they lost. |
| 16 | none, not a replication | as row 15 |
| 17 | none, not a replication | Location 4425's claim is a verdict, and `### Rows that are not replications` would let it be pinned as one. It is not, because Entry 6's rule wants the criterion written before any statistic, and these were computed first. |
| 18 | none, not a replication | as row 17 |
| 19 | reproduced | This is the January Chan's text says "worked wonderfully" (p. 175). Its month-end, 2008-01-31, is one only because the file's last row is 2008-02-01. Cut at 2008-01-31, no printout's rules reach it. |
| 20 | reproduced | The forward fill moves this row, where it moves neither row 3 nor row 4. It ranks PMC, which has no 2006 close, on its last close before an 851-day gap, a return of 1.3056 that puts it fourth of 595 and short. So 595 stocks are ranked, and a tenth of them, 59.5, rounds to 60. Without the fill 594 are ranked, a tenth rounds to 59, and the return is 0.090908. Taking the full top decile with the fill gives 0.085757, and dropping both the slice and the fill gives row 19's figure. |
| 21 | reproduced | Inferred rules, as for row 5. A tenth of 594 is 59.4, so R's rounding and MATLAB's give the same stocks. |
| 22 | reproduced | The criterion was written on [issue 254](https://github.com/l3a0/quantitative-trading/issues/254) before any five-year figure was computed, under the owner's ruling that the revised MATLAB's rules carry it. The post's running-sum figure, which shows the shape of those years, was already published then, as the issue records. P. 180 tells the reader to run the program on the most recent five years instead of the entire data period, so the program is rerun on the last five years of its input. The rerun's 47 months are the full run's last 47, value for value. The claim holds on Chan's file of survivors. The rerun's annual return has a standard error of 0.0281 a year, about eight times the 0.0036 gap, so the row says nothing about whether the effect weakened. `TestTheMostRecentFiveYears::test_the_gap_is_far_inside_the_noise_of_47_months` holds both figures. |
| 23 to 29 | none, not a replication | Reported beside row 22 with no verdict. Rows 24, 25, 28 and 29 average the tail of the full run, a rule the book does not print, and p. 180 names the average returns rather than the Sharpe ratio. |
| 30 | none, survivor-only and exploratory | No January effect detectable above about 2.4% a January, on members that favour the effect. The test fails to reject, so the reading takes the owner's wording for [issue 329](https://github.com/l3a0/quantitative-trading/issues/329), with X at the measured deviation, and it never says the effect disappeared. Two ranked members have no exit close and are skipped as `smartmean` skips them: INDV, which has no row on 2019-01-31, and GES, delisted on 2026-01-22. Two members are never ranked at all, because Alpha Vantage's NVRI and GTES hold nothing before 2026, so at most 601 of the 603 can rank. Row 40 takes these rows' mean less row 35's. |
| 31 to 34 | none, survivor-only and exploratory | Reported beside row 30. Row 33 is 2.4% where the issue's power estimate before the run was 3.7%, because the measured deviation of 0.0398 is smaller than the 6.05% of Chan's three printed Januaries. |
| 35 | none, registered | The free sources cannot decide it, which is the verdict's own wording rather than one of the three a replication takes. The low series is nowhere near above zero, with a p of 1.000, and the high series is, with a p of 0.001. The criterion takes a verdict only where both series give the same answer, so neither "no January effect detectable" nor "a January effect above zero" can be written. The width is the threatening members. At 2008-12-31, 89 of the 161 missing members threaten a tenth of 59, so most of both tenths hold an assumed return. The bound shrinks as coverage grows, to −0.0023 and 0.0027 at 2025-12-31, where one member threatens. The next step the owner's ruling names is buying prices for the threatening members alone, which [issue 407](https://github.com/l3a0/quantitative-trading/issues/407) carries. |
| 36 to 40 | none, registered | Reported beside row 35. Row 40 compares two runs on one cross-section, so it measures membership rather than two download dates. Its two figures differ in sign because the bound is wider than the gap it would measure, so it says nothing yet about what survivorship cost Example 7.6. |
| 41 | none, registered | The registered verdict is "no return detectable above about 4.2% a year", the criterion's own wording rather than one of the three a replication takes. The mean is −0.0001 a month with a one-sided p of 0.539, so the test does not reject. The 4.2% is row 44's X at one decimal of a percent, as the issue fixed. A true return below that size could pass undetected, so the verdict never says the strategy is dead. It is before costs and on covered members only. Its membership is carried forward between quarterly schedules, and it lacks the return a failing stock takes when it leaves, which the free source does not carry. `TestTheMonthlyPins::test_the_verdict` holds the wording. |
| 42 to 49 | none, registered | Reported beside row 41. Row 45 equals row 41 because the printouts' differences never bind on this panel. Every ranked member has the closes its month needs, so keeping a stock on its own close and keeping it on its own return keep the same stocks. Rows 46 and 47 measure what carrying a schedule forward misdates, and both bracketing means are negative, like row 41's. Row 48's positions earn their return to the last close and nothing after it. Row 49 tests the argument the dropped members rest on. Among covered members, names that leave the index within a year land in a tenth more often than names that stay, most of all in the short tenth. The issue said before the run that a clear difference would count as evidence against the argument that dropping a missing member is neutral, and this is such a difference. Which way it moves row 41's mean is not measured. The chi-square p prints as 0.000 and decides nothing, because member-months repeat the same names. |

### What the entry concludes

Seven things.

1. **Every reachable figure reproduces, and not under the strategy as
   described.** The seventeen rows land at the precision each printout gives.
   Each of these six rules moves a printed figure, and none is in the
   description:
   1. keeping or dropping a stock on another stock's close,
   2. a monthly sum rather than a mean over positions,
   3. months with no position counted as zero in the mean,
   4. a standard deviation that counts a NaN month as zero,
   5. a winners' slice that leaves out the best stock,
   6. year-end closes forward-filled before ranking, which moves January 2008.
2. **The four Heston and Sadka printouts disagree on units and agree on sign.**
   The first edition's −0.9167 is a sum over positions. The revised edition
   divides by the positions, and its three printouts land between −0.0114 and
   −0.0129 a year. All four lose money on this file.
3. **Under the revised Python's rules, the loss sits before 2002.** Rows 15
   to 18 show the 13 months before 2002 returning −0.145387 a year and the 70
   after returning 0.011967. Only that printout's rules were split. It is a
   finding about survivors over one short window, with no verdict, and it
   says nothing about Heston and Sadka, whose sample this file does not
   reach.
4. **On this file, the most recent five years do worse, as p. 180 says.**
   Rerun on them, the revised MATLAB's rules give −0.0165 a year against the
   whole period's −0.0129. The gap is about an eighth of the rerun's standard
   error of 0.0281, so this says Chan's comparison holds on his own file, and
   nothing more. It does not contradict conclusion 3. The rerun leaves out the
   23 months from January 2002 to November 2003, which return 0.069997 a year
   under the revised Python's rules, and that figure is exploratory like the
   split.
5. **On IJR's members at 2025-12-31, no January effect is detectable above
   about 2.4% a January, on data that favour it.** Rows 30 to 34 average
   0.0108 a January before costs over 18 Januaries, with a one-sided p of
   0.132. The data are survivors, tilted toward the effect, so this reading
   goes one way only.
6. **On IJR's members as they stood at each year-end, the free sources cannot
   decide whether the January effect survived the book.** This is the log's
   first registered result. Rows 35 to 40 bound every January, because every
   year-end has members with no checked price that could change a tenth. The
   low series averages −0.1047 a January with a one-sided p of 1.000, and the
   high series 0.0879 with a p of 0.001. A purchase of the threatening
   members' prices is what could decide it.
7. **On the S&P 500 as IVV held it each month, Example 7.7 earns no return
   detectable above about 4.2% a year after the book.** This is registered.
   Row 41 averages −0.0001 a month before costs over the 213 months from
   January 2009 to September 2026, with a one-sided p of 0.539. The revised
   Python's rules give the same months, and the means on both bracketing
   masks are negative too, with no verdict.

### What this entry cannot say

Four things.

**Whether Example 7.6's January effect survived the book.** Rows 35 to 40
were built to say, and the bound is too wide for either answer. Members with
no checked price could change a tenth at every year-end, and the free sources
hold no price for them. Rows 30 to 34 bound it in one direction only, on
survivors.

**Whether the effect existed before 2002.** Both files hold only the companies
still in their index on the day Chan saved them, and the S&P 500 file starts
in November 1999. [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196)
is where the 13 percent is tested on a panel that still holds the companies
that left.

**How the revised R rounds Example 7.6.** It is assumed from its Example 7.7
code. The revised MATLAB's `smartstd`, which the page leaves open, is settled
by the revised code's repost.

**Whether Example 7.7 earns a small return after the book.** Rows 41 to 44
detect nothing above about 4.2% a year, and a true return below that could
pass undetected. The verdict also leaves out four things.

1. **Costs.** The run charges none. Costs only lower the return, so they
   cannot turn this result into a finding, and no after-cost figure is
   pinned.
2. **Members with no checked price.** They are dropped, as the owner ruled,
   so coverage falls as low as 364 of 501 in 2012-09. Row 49 is evidence
   against the argument that dropping them is neutral, so the bias from
   dropping them is reported rather than removed.
3. **Membership between schedules.** IVV's schedules are quarterly, so each is
   carried forward, and 378 positions sit on names that changed between two
   schedules. Row 46 brackets the mean on either side of that misdating,
   and row 47 counts the positions it touches.
4. **A failing stock's last return.** A stock that stops inside a month earns
   its return to its last close and nothing after, as row 48's 23 positions
   do. The return a delisted stock takes when it leaves needs a licensed
   database.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/equity-seasonals-lessons.md](../blog/equity-seasonals-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.equity_seasonals_figures` redraws.

## Entry 8: the Khandani-Lo reversal, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.7, Kindle locations
2099, 2137 and 2233. Shipped under
[issue 17](https://github.com/l3a0/quantitative-trading/issues/17).

Three computed rows, all derivable from
[tests/test_khandani_lo.py](../tests/test_khandani_lo.py).

**Both of Chan's figures reproduce at the precision he printed.** The rule buys
the stocks that fell most against the market yesterday and shorts the ones that
rose most. On his own S&P 500 file over 2006 it earns a Sharpe ratio of 0.2510
before costs, against his 0.25, and −3.1884 after 5 basis points a trade,
against his −3.19. A cost a large-cap trader pays every day turns a small edge
into a large loss, and that collapse is the lesson the example was printed to
teach.

The second figure reproduces only because two quirks of Chan's code are kept.
His script never charges the first day's rebalance, which leaves that day's
after-cost profit as NaN. His `smartstd` then counts that NaN as 0 while his
`smartmean` skips it. A port that skips the NaN in both, the way pandas does,
gives −3.1822 and misses −3.19 by one unit. Row 3 removes both quirks and
gives −3.2337, a little worse than Chan printed.

Two rows are replications and one is not. Rows 1 and 2 are the two figures
Chan prints. Row 3 is the same run with both quirks removed, which Chan prints
no figure for, so it carries no verdict.

Two figures from the book have a row in the first table and none in the other
two.

1. **Khandani and Lo's 4.47**, the Sharpe ratio they report for 2006. It was
   computed on their own universe, which this repo does not hold, so nothing
   here computes it and it takes no verdict. Chan's figure is about the S&P
   500, and the distance between his 0.25 and their 4.47 is his point rather
   than a gap.
2. **Chan's explanation**, that most of their returns came from small and
   microcap stocks. It is a claim about a universe this run does not read.
   Location 2236, at the end of Example 3.8, leaves rerunning the strategy on
   the S&P 400 and S&P 600 as an exercise, which would test it, and nothing
   here runs that.

Every row reads the same vintage, window and specification, so the three are
stated once here.

1. **The vintage.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, lifted one vintage per stock, saved 2007-11-24, and read
   back as one frame through `chan.series.load_panel`.
   [data/README.md](../data/README.md) says where the file came from. It is
   the S&P 500 as it stood on 2007-11-23, carried backwards, so a company that
   left the index before then is absent. Of the 500, 491 are priced on the
   window's first day and 495 on its last. **Every figure here is about
   survivors.** [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198)
   is where the same rule runs on the index as it stood in 2006, and
   [issue 213](https://github.com/l3a0/quantitative-trading/issues/213) is
   Chan's own demonstration of what survivorship does.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days. Returns,
   weights and profit are computed on the whole file and only then cut, so the
   window's first profit uses the weights from the day before it.
3. **The specification.** Chan's `example3_7.m`, read in the mirror
   [egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
   at `1a71950`. A stock's weight is minus its return less the equal-weighted
   market's, divided by the count of stocks with a close that day, and 0 where
   either day's close is missing. The weights are held for one day and sum to
   zero across stocks. The cost is 5 basis points on each side of a change in
   weight, which is location 998's convention that a round trip is two
   transactions. The Sharpe ratio is √252 times the mean over the standard
   deviation, with no risk-free rate subtracted.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 sample on a rule somebody else chose, so the entry says whether his
numbers reproduce on his file and nothing about whether the rule pays today.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Sharpe ratio on the S&P 500 in 2006, before costs | 0.25 | Kindle location 2137, and again at 2233 |
| 2 | Sharpe ratio after 5 basis points a trade | −3.19 | location 2233 |
| 3 | Sharpe ratio after costs, with the first day charged and nothing zero-filled | none, the book prints no such figure | n/a |
| 4 | Khandani and Lo's Sharpe ratio for 2006, on their own universe | 4.47 | location 2099 |
| 5 | Chan's explanation of the drop | that most of their returns came from small and microcap stocks, a claim rather than a figure | location 2137 |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2006-01-03 to 2006-12-29 | Chan's rule before costs, his `sharpe` | 0.2510 | `TestTheFigures::test_before_costs` |
| 2 | 2006-01-03 to 2006-12-29 | Chan's rule after costs, his `sharpeminustcost`, with the first day uncharged and its NaN counted as 0 in the deviation | −3.1884 | `TestTheFigures::test_after_costs_with_both_quirks` |
| 3 | 2006-01-03 to 2006-12-29 | row 2 with the first day charged from the weights before the window, so no day is NaN | −3.2337 | `TestTheFigures::test_after_costs_with_both_quirks_removed` |

`TestTheQuirksMoveTheFigure::test_dropping_the_nan_misses_chans_second_digit`
holds the −3.1822 a pandas port gives, and that it misses −3.19.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.00 | reproduced | Chan's claim is that the rule earns a mediocre Sharpe ratio on the S&P 500 in 2006, far below Khandani and Lo's. On his own file and his own code it lands on his figure at the two decimals he printed. |
| 2 | 0.00 | reproduced | The claim is that 5 basis points a trade turns that small edge into a large loss, and it survives at his printed precision. It lands there only with both quirks of his code kept, which is the specification the figure came from rather than a choice made to close a gap. |
| 3 | none | none, not a replication | Chan prints no figure for it. It is here because it is the after-cost figure with the first day charged, so its series holds no NaN for the deviation to count as 0. It lands a little below Chan's figure, so the two quirks moved his figure in his favour without moving the claim. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Both figures reproduce on Chan's own file.** The vintage explanation that
   carries Entry 1's misses is not needed here, because the file is his and
   the code transcribes his script. What the entry adds
   is that his second figure depends on how his helpers treat one NaN, so a
   careful port of the formula alone misses it.
2. **On the S&P 500 the daily cost is larger than the daily edge.** A Sharpe
   ratio of 0.2510 before costs and −3.1884 after is a rule whose average
   daily profit is smaller than the average cost of rebalancing into it every
   day. On the specification of row 3, the average day's cost is 13.7453
   times its average profit. The rule trades 1.4505 times its average gross
   position a day. `TestWhatAnAverageDayCosts` holds both. Removing the
   quirks makes the after-cost figure slightly worse, not better.
3. **The universe is survivors, and nothing here measures what that cost.**
   Every stock that left the S&P 500 before 2007-11-23 is missing, whether it
   failed or was taken over, so neither the size nor the sign of the effect on
   either figure is known.
   [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) is
   what would measure it.

### What this entry cannot say

Four things.

**Whether Khandani and Lo's figure reproduces.** It was computed on a universe
this repo does not hold, so it stays a cited number.

**Whether Chan's explanation holds.** The rule on small caps is the test of
it, and Chan leaves that as an exercise. The S&P 600 file under
`ijr_20080114/` spans 2006, and running the rule on it would be a finding with
no published figure to check, like Entry 5, rather than a replication.
[Issue 249](https://github.com/l3a0/quantitative-trading/issues/249) runs it.

**What survivorship cost.** Neither its size nor its sign is measured.

**What trading at the open gives.** That is Example 3.8, and Entry 10
carries it. Entry 10 also reproduces Chan's Python notebook for this example,
which prints 0.9578 and −2.1617 rather than 0.25 and −3.19, because its rule
differs from `example3_7.m` in six ways and its forward-fill reads WYN's gap
as one day's move.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post quotes most of these figures. So does its
running-profit figure, which `uv run python -m chan.survivorship_and_costs_figures`
redraws.
[blog/khandani-lo-reversal-lessons.md](../blog/khandani-lo-reversal-lessons.md)
moves with it too, since it quotes the before-cost and after-cost figures and
the average day of 2006 beside the 2012 panel's.

## Entry 9: the survivorship toy, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.3, between the
highlights at Kindle locations 1423 and 1474. Shipped under
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213).

Chan warns at location 1012 that a database holding only surviving stocks
inflates a backtest that buys cheap stocks, because some stocks are cheap
because the company is about to fail. Example 3.3 is the toy he points to. It
buys the 10 lowest-priced stocks among the 1,000 largest by market
capitalisation at the close on 1/2/2001, with equal capital in each, and sells
at the close on 1/2/2002. The book prints two tables of ten picks.

1. **The survivorship-free picks.** Nine of the ten were delisted during the
   year, so the book gives each a terminal price, the last price traded on or
   before 1/2/2002. Only MDM has a close on that date.
2. **The survivor-only picks.** A database holding only survivors keeps MDM and
   continues up the price ranking past the nine stocks it never held.

The label is a revised-edition one, and this entry declares it because the
repo reads an example number as first-edition unless it says otherwise. Whether the 2009
edition numbers this example 3.3 and prints the same tables was not checked.
The first-edition code mirror this repo cites elsewhere holds no file for it
among its Chapter 3 files, so the printed tables are the whole source.

Five rows, all derivable from
[tests/test_survivorship_bias.py](../tests/test_survivorship_bias.py). Rows 1
and 2 are the two figures the book prints. Rows 3 and 4 are the equal-shares
near miss on each table, and row 5 is the survivor-only figure with NEOF on one
share basis. Those three carry no published figure and say so in their own
cells.

**The vintage column says `none, the book's printed tables` in every row.** The
twenty rows are copied from the book into
[src/chan/survivorship_bias.py](../src/chan/survivorship_bias.py), whose
docstring names their source, and nothing was downloaded. A printed number
cannot be restated by a vendor, so the edition is what pins it.
[docs/design.md](design.md#a-replication-that-reads-the-books-own-tables) says
why that is not a vintage. The cell names no price basis, because the book does
not say whether its database adjusted for splits, and row 5 shows that at least
one row was not adjusted.

**The window column stays.** Entry 2 dropped it because a gamble has no window,
and this toy has one in every row, because the book fixes the dates.

Neither epistemic label reaches this entry, for the reason Entry 2 gives.
Reproducing the arithmetic on a printed table spends no sample.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Survivorship-free portfolio, equal capital | −42 percent, the return Chan says a trader would actually have had | Kindle location 1471 |
| 2 | Survivor-only portfolio, equal capital | 388 percent, which Chan calls fictitious | Kindle location 1471 |
| 3 | Survivorship-free portfolio, equal shares | none, the book specifies equal capital | n/a |
| 4 | Survivor-only portfolio, equal shares | none, the book specifies equal capital | n/a |
| 5 | Survivor-only portfolio with NEOF on one share basis | none, the book prints NEOF's row as it stands | n/a |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 1/2/2001 to 1/2/2002 | mean of the ten per-stock returns, end over start less one, each delisted stock at its terminal price | none, the book's printed tables | −41.72 percent | `TestBookFigures::test_the_survivorship_free_portfolio_loses_42_percent` |
| 2 | 1/2/2001 to 1/2/2002 | the same mean over the survivor-only picks | none, the book's printed tables | 387.88 percent | `TestBookFigures::test_the_survivor_only_portfolio_gains_388_percent` |
| 3 | 1/2/2001 to 1/2/2002 | one share of each, the sum of end prices over the sum of start prices less one | none, the book's printed tables | −47.62 percent | `TestTheNearMiss::test_equal_shares_on_the_survivorship_free_picks` |
| 4 | 1/2/2001 to 1/2/2002 | the same over the survivor-only picks | none, the book's printed tables | 373.17 percent | `TestTheNearMiss::test_equal_shares_on_the_survivor_picks` |
| 5 | 1/2/2001 to 1/2/2002 | row 2's mean with NEOF's start price multiplied by 10, the ratio of its 2001 reverse split | none, the book's printed tables | 100.91 percent. As printed, NEOF carries 308.86 of row 2's 387.88 points | `TestTheReverseSplit::test_on_one_share_basis_the_survivor_portfolio_still_gains` and `::test_neof_carries_most_of_the_survivor_only_return` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0 at the whole percent the book prints | reproduced | Chan's claim is that a trader running this strategy on the stocks actually available would have lost money. The equal-capital mean is negative and rounds to his figure, so the claim survives. |
| 2 | 0 at the whole percent the book prints | reproduced | Chan's claim is that a survivor-only backtest turns that loss into a large gain. The figure reproduces from his table as printed. Most of it rests on NEOF's row, which compares a price before a reverse split with a price after it, and row 5 puts it on one basis. The claim survives there at a gain against a loss, so the verdict stays with the figure, as Entry 1's row 11 does, and this column carries the qualification. |
| 3 | none | none, not a replication | The book specifies equal capital. The row exists so the specification is held rather than the number: buying one share of each gives −47.62 percent, which does not round to −42. |
| 4 | none | none, not a replication | The same near miss on the second table. It gives 373.17 percent, which does not round to 388. The two misses together are what rule the weighting out. |
| 5 | none | none, not a replication | The book prints NEOF's row unadjusted. Neoforma's FY2001 10-K, [on EDGAR](https://www.sec.gov/Archives/edgar/data/1096219/000101287002001537/d10k.htm), states a 1-for-10 reverse split effective 2001-08-27 and restates its quarterly price tables for it, so 0.875 is a price before the split and 27.9 a price after it. On one basis the survivor-only portfolio still gains, which is the claim row 2 supports, and by far less than the printed figure. |

### What the entry concludes

Three things, and the first is why the verdicts carry less than they look.

1. **The verdicts were knowable before the work started.** As with Entry 2,
   nothing can move a printed table's arithmetic, so rows 1 and 2 could only
   reproduce once the right weighting was found. The work is worth the
   specification it settles and the row it checked against an outside source.
2. **The book prints no formula, so the weighting is what rows 1 to 4 hold.**
   Equal capital reproduces both figures, and equal shares misses both. Both
   are pinned, because an assertion on the right figure alone would hold a
   number rather than a choice.
3. **One stock carries most of the fictitious return, and its row mixes two
   share bases.** NEOF contributes 308.86 of the 387.88 points. With its start
   price on the basis of its reverse split, the survivor-only portfolio returns
   100.91 percent. The lesson survives, since −41.72 against 100.91 is still a
   loss against a gain, but the difference between the two portfolios is much
   smaller once NEOF's row is on one share basis. That is a finding about
   Chan's table, and it does not change what the table as printed reproduces
   to.

Chan tells the same toy a second time. The notes on his *Algorithmic
Trading*, at location 704 in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md),
give the same 388 percent but describe the honest outcome as "almost 100
percent loss" rather than −42 percent. That is the same author with a
different number, cited from the note and not reproduced.

### What this entry cannot say

Four things.

**Whether the picks are right.** The universe of 1,000 stocks is not printed,
so the selection step cannot be re-run. Re-running it would need the 1,000
largest US stocks as they stood on 2001-01-02, delisted ones included, which is
bought data. No issue is filed for it, because both printed figures sit
downstream of the picks.

**Whether the other nineteen rows sit on one share basis.** Only NEOF was
checked against a filing. The rest are taken as printed, so row 5 corrects the
one row known to mix two bases and claims nothing about the others.

**Whether buying cheap stocks pays.** The toy shows what a survivor-only
database does to a backtest. It runs one year on ten stocks and is not a test
of the strategy.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post quotes most of these figures. So does its
figure of the three portfolios' returns, which
`uv run python -m chan.survivorship_and_costs_figures` redraws.

## Entry 10: the Khandani-Lo reversal at the open, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.8, p. 78, and the
notebook `example3_8.ipynb` the book points to. Shipped under
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206).

The label is a revised-edition one, and this entry declares it because the
repo reads an example number as first-edition unless it says otherwise. The
first-edition mirror holds `example3_7.m` and no file for this example, and
whether the 2009 edition carries it was not checked.

Thirteen rows, all derivable from
[tests/test_khandani_lo.py](../tests/test_khandani_lo.py).

**Chan's notebook reproduces, and the book's claim does not.** Example 3.8
takes Example 3.7's reversal and changes one thing, updating the positions at
the market open instead of the close. The book prints no figure and says only
that the Sharpe ratios before and after costs are "both very positive". Chan's
notebook prints 2.3818 before costs and 1.3997 after, and its transcription
lands on both. Run on the rule the book describes, the reversal earns 4.4202
before costs and 0.7834 after, so the after-cost figure misses the line of 1.0
that the claim was held to, declared before any figure on the opens was
computed.

Those two results come from two rules, and the difference between them is the
finding.

1. **Rule B is Example 3.7's MATLAB with the open in place of the close**, the
   rule Entry 8 reproduces. Chan's sentence at p. 78 recalls that strategy's
   0.25 and −3.19 and calls updating at the open "the only change", so rule B
   carries the claim.
2. **Rule A is the notebook as written.** It forward-fills before taking
   returns, carrying each stock's last price into a gap. It scales each day's
   weights to a gross exposure of 1, zeroes no stock for a missing price,
   divides its deviation by n, charges nothing on the first day, and charges
   no change in weight beside a missing one. Its Example 3.7 twin prints
   0.9578 and −2.1617 rather than the book's 0.25 and −3.19, and rows 4 and 5
   reproduce both on the closes.

The forward-fill is what separates them most. `spx_20071123/wyn.csv` holds two
companies under one symbol, 952 trading days apart, and the fill reads that gap
as a single day's move on 2006-08-01: a return of 121.5 on the closes and
127.65 on the opens, gains of over 12,000 percent. On the closes the fill
lifts rule A from 0.4179 to 0.9578 before costs, and dropping WYN alone gives
0.4268. On the opens it pulls rule A's figure before costs down, from 4.8606 to
2.3818, and dropping WYN alone gives 4.8508. After costs on the opens it
pushes the figure up, from 1.0335 to 1.3997.

Five rows are replications and eight are not. Row 1 is the claim, which takes
the claim route `### Rows that are not replications` describes, and rows 2 to
5 are the four figures Chan's notebooks print. Rows 6 to 13 have no published
figure.

Every row reads the same vintage, window and costs, so the three are stated
once here.

1. **The vintage.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, read through `chan.series.load_panel` with
   `field="Open"`, or the default close where a row says closes. Chan's
   notebooks read `SPX_op_20071123.txt` and `SPX_20071123.txt` instead, which
   this repo does not commit. Measured on
   [issue 206](https://github.com/l3a0/quantitative-trading/issues/206) at
   `7150afb`, each
   matches its panel cell for cell, NaN for NaN, to a largest relative
   difference of 2.0e-16, so the two are one series and nothing here can
   re-measure that. **Every figure here is about survivors**, for the reason
   Entry 8 gives.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days, cut after the
   profit is computed.
3. **The costs and the ratio.** 5 basis points on each side of a change in
   weight, and √252 times the mean over the standard deviation with no
   risk-free rate. Rule B divides the deviation by n − 1 and rule A by n.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 sample on a rule somebody else chose, so the entry says whether his
numbers and his claim reproduce on his file and nothing about whether trading
at the open pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Both Sharpe ratios, before and after costs, at the open | "both very positive", a claim rather than a figure | p. 78. Not among the committed highlights, as [research/book-notes/README.md](../research/book-notes/README.md) records |
| 2 | The notebook's Sharpe ratio before costs | 2.381759409645483 | `example3_8.ipynb`, as reposted at pinhaocheng/epchan-quant_trading_Python_codes `5fcab61` |
| 3 | The notebook's Sharpe ratio after costs | 1.3996944546182997 | the same |
| 4 | The Example 3.7 notebook's Sharpe ratio before costs, on the closes | 0.957785681010386 | `example3_7.ipynb`, the same repost |
| 5 | The Example 3.7 notebook's Sharpe ratio after costs | −2.1617433718962276 | the same |
| 6 to 13 | rule B's figures, what the open recovered, rule A without its fill or without WYN, and the one-year bar | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | rows 6 and 7 read against the declared criterion, both at least 1.0 unrounded | before costs clears it and after costs does not | `TestTheVerdicts::test_the_claim_does_not_hold_because_after_costs_misses` |
| 2 | rule A on the opens, before costs | 2.3818 | `TestRuleAOnTheOpens::test_the_figures` |
| 3 | rule A on the opens, after costs | 1.3997 | `TestRuleAOnTheOpens::test_the_figures` |
| 4 | rule A on the closes, before costs | 0.9578 | `TestRuleAOnTheCloses::test_it_reproduces_the_notebooks_example_37` |
| 5 | rule A on the closes, after costs | −2.1617 | `TestRuleAOnTheCloses::test_it_reproduces_the_notebooks_example_37` |
| 6 | rule B on the opens, before costs | 4.4202 | `TestRuleBOnTheOpens::test_before_costs` |
| 7 | rule B on the opens, after costs, first day uncharged and its NaN counted as 0 | 0.7834 | `TestRuleBOnTheOpens::test_after_costs_with_both_quirks` |
| 8 | row 7 with the first day charged, so no day is NaN | 0.8293 | `TestRuleBOnTheOpens::test_after_costs_with_both_quirks_removed` |
| 9 | row 7 less Entry 8's row 2 | 3.9718 | `TestRuleBOnTheOpens::test_what_trading_at_the_open_recovered` |
| 10 | rule A on the opens without the forward-fill | 4.8606 before costs, 1.0335 after | `TestRuleAOnTheOpens::test_without_the_forward_fill` |
| 11 | rule A on the opens without WYN | 4.8508 before costs, 1.0357 after | `TestRuleAOnTheOpens::test_without_wyn` |
| 12 | rule A on the closes without the forward-fill, and without WYN | 0.4179 and −3.3760, and 0.4268 and −3.3643 | `TestRuleAOnTheCloses::test_without_the_forward_fill_it_does_not` and `::test_without_wyn_it_lands_near_the_unfilled_figure` |
| 13 | rows 2, 3, 6 and 7 against 1 × √(681/251), Chan's minimum-backtest estimate at p. 61 scaled to the window | the bar is 1.6472, and only the two before-cost figures clear it | `TestTheVerdicts::test_which_figures_clear_the_one_year_bar` and `::test_the_bar_is_chans_estimate_scaled_to_the_window` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, the source states a claim | did not reproduce | The criterion was declared on [issue 206](https://github.com/l3a0/quantitative-trading/issues/206) and the threshold confirmed by the owner before any figure on the opens was computed: both of rule B's figures at least 1.0, Chan's own line for a strategy worth trading on its own at p. 23. Before costs is 4.4202 and after costs 0.7834. The run reads Chan's own file through a transcription of the rule Entry 8 reproduces, so no cause outside the method is available, which is the reasoning behind Entry 1's row 6. |
| 2 | 0.0000 | reproduced | Chan's figure, on his own data, through his own notebook transcribed. |
| 3 | 0.0000 | reproduced | The same. |
| 4 | 0.0000 | reproduced | Rule A's control. Without it a transcription that leaned on pandas' current `pct_change`, which no longer fills gaps, would give row 12's 0.4179 and look plausible. |
| 5 | 0.0000 | reproduced | The same. |
| 6 | none | none, not a replication | Half of what row 1 reads. Updating at the open lifts the figure before costs from Entry 8's 0.2510 to 4.4202. |
| 7 | none | none, not a replication | The half that fails. Charging 5 basis points a side takes the figure from row 6's 4.4202 to 0.7834. |
| 8 | none | none, not a replication | Charging the first day moves the figure up rather than down here, and it stays below 1.0, so the quirks do not decide row 1. |
| 9 | none | none, not a replication | What the open recovered against Example 3.7 after costs. It turns a large loss into a small gain. |
| 10 | none | none, not a replication | The forward-fill is pandas 0.24's default, which the notebook's bare `pct_change()` inherits rather than asks for. Without it rule A's after-cost figure is 1.0335, above 1.0. |
| 11 | none | none, not a replication | Dropping only WYN gives 4.8508 against row 10's 4.8606, and 1.0357 against 1.0335, so on the opens WYN's gap carries most of what the fill does. |
| 12 | none | none, not a replication | The same pair on the closes. There WYN's gap lifts the figure rather than lowering it, and dropping WYN alone brings rule A from row 4's 0.9578 to 0.4268, near the 0.4179 it gives without the fill. |
| 13 | none | none, not a replication | The two before-cost figures clear the bar and the two after-cost figures do not. Chan states the estimate behind it as 95 percent confidence over 681 days, and scaling it to one year is this repo's step, so the row decides nothing. |

### What the entry concludes

Three things, and the first is the verdict.

1. **On the rule the book describes, the claim does not hold.** Updating at
   the open turns Example 3.7's −3.1884 after costs into 0.7834, a recovery of
   3.9718, and the before-cost figure reaches 4.4202. "Both very positive"
   asks both to clear 1.0, and the after-cost figure does not.
2. **Chan's notebook reproduces exactly and computes something else.** Its
   figures land at four decimals on both examples, and both of its Example
   3.8 figures clear 1.0. But it differs from the MATLAB in six ways, and on
   Example 3.7 it prints 0.9578 where the book prints 0.25, so it is not the
   strategy behind 0.25 and −3.19 with one change, which is what the book's
   sentence describes.
3. **WYN's gap moves rule A on both fields, in opposite directions.** Reading
   it as a gap rather than a move, by dropping the fill or dropping WYN, gives
   0.4179 to 0.4268 before costs on the closes and 4.8508 to 4.8606 on the
   opens. Rule A's after-cost figure on the opens stays above 1.0 either way,
   at 1.0335 and 1.0357.

### What this entry cannot say

Four things.

**What `example3_8.R` prints.** The book points to it beside the notebook, and
no copy was found.

**Whether trading at the open is tradeable on the open's own signal.** Both
rules set a weight from the day's open and trade at that same open, as Example
3.7 does at the close. Neither run adjusts that timing.

**What survivorship cost.** Neither its size nor its sign is measured, as
Entry 8 says.

**Whether the rule pays on small caps.** Chan leaves that as an exercise, and
[issue 249](https://github.com/l3a0/quantitative-trading/issues/249) runs it on
the S&P 600 file.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post's Lessons 6 and 7 quote these figures.

## Entry 11: the commodity seasonals, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, the main text at Kindle
locations 4529, 4585 and 4632 and the two sidebars at 4536 and 4590. Shipped
under [issue 19](https://github.com/l3a0/quantitative-trading/issues/19).

Ten rows, all derivable from
[tests/test_commodity_seasonals.py](../tests/test_commodity_seasonals.py).

**Both natural gas figures reproduce under the reading the issue pinned, and
the gasoline count agrees with the book on every year the file can read.** Chan says commodity seasonal trades still pay where
the equity ones have died, and gives two. Gasoline buys the May contract at the
close of April 13 and sells at the close of April 25. Natural gas buys the June
contract at the close of February 25 and sells at the close of April 15.

1. **Natural gas.** Every year from 1994 to 2008 is profitable. Counted from
   1995, the run is 13 years ending in 2007 and 14 ending in 2008, the main
   text's figure and the sidebar's.
2. **Gasoline.** 1995 to 2015 holds exactly 2 losing years, 2009 and 2012,
   which is 21 less 19. It shows 16 profitable years rather than 19, because
   EIA's file holds no row on the trade date in 1997, 1998 or 1999.

Every rule was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) on
2026-10-03, before any trade was computed. One was corrected afterwards: the
review of [PR #260](https://github.com/l3a0/quantitative-trading/pull/260)
found the pre-1997 expiries the first run missed, and the correction changed
no count. Three of the rules carry the result, so they are stated here.

1. **The vintages.** EIA's NYMEX settlements, downloaded 2026-10-02:
   `eia_eer-epmr-pe1-y35ny-dpg_raw_1985-01-02_2006-12-29_dl2026-10-02.csv`, New
   York Harbor regular gasoline, through 2005,
   `eia_eer-epmrr-pe1-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv`,
   RBOB gasoline, from 2006, and `eia_rngc2`, `eia_rngc3` and `eia_rngc4` for
   natural gas. [data/README.md](../data/README.md) says what each holds. Each
   file numbers contracts by expiry, so the run maps a date to the file that
   holds the May or June contract. The expiry rule behind that map gives the
   last trading day the Massive futures API recorded for all 16 contracts
   checked, March to June of 2017, 2018, 2021 and 2024. Those 16 dates were read
   from the API on 2026-10-03 and are pinned as a measurement, because nothing
   in this repo can read them again. Before mid-1997 contracts stopped trading
   five or six days before delivery rather than three, which the files'
   handovers show, and the rule follows them. That moves the 1996 and 1997
   entries to contract 3 and changes neither year's sign.
2. **Profitable** means the exit settlement strictly above the entry, on one
   contract, with no costs.
3. **A missing row stays missing.** A year whose trade date has no row in its
   file counts neither way, rather than moving to another day.

Every result here is **exploratory**. Chan chose both trades after looking at
the history the run reads, so the entry says whether his counts reproduce and
nothing about whether either trade pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Gasoline, profitable years in 1995 to 2015 | 19 of 21 | location 4529 |
| 2 | Gasoline, the years out of sample | the last 9 of the 21, with no count | location 4529 |
| 3 | Gasoline, the sidebar's claim | a profit every year since 1995 | location 4536 |
| 4 | Natural gas, the main text's run | 13 consecutive years | location 4585 |
| 5 | Natural gas, the sidebar's run | 14 consecutive years | location 4590 |
| 6 | Natural gas out of sample | "didn't hold up as well", a claim with no figure | location 4632 |
| 7 to 10 | the runs counted from 1994, 2006 on the older gasoline contract, the expiry-day file, and both trades after the book | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | gasoline, 1995 to 2015 | 16 profitable, 2 losses in 2009 and 2012, 3 unreadable in 1997, 1998 and 1999 | `TestTheVerdicts::test_19_of_21_reproduces_with_a_gap_the_missing_years_explain` |
| 2 | gasoline, 2007 to 2015 | 7 of 9 | `TestTheVerdicts::test_the_nine_out_of_sample_years` |
| 3 | gasoline, 1995 to 2008, read as the years before the 2008 first edition | no loss, 11 profitable, 3 unreadable | `TestTheVerdicts::test_every_year_since_1995_has_no_loss_and_three_unreadable_years` |
| 4 | natural gas, the run counted from 1995 ending in 2007 | 13 | `TestTheVerdicts::test_13_and_14_consecutive_years_reproduce` |
| 5 | natural gas, the run counted from 1995 ending in 2008 | 14 | `TestTheVerdicts::test_13_and_14_consecutive_years_reproduce` |
| 6 | natural gas, 1994 to 2008 against 2009 to 2023 | 15 of 15 against 7 of 15 | `TestTheVerdicts::test_natural_gas_before_and_after_the_first_edition` |
| 7 | natural gas, the runs counted from 1994 ending in 2006, 2007 and 2008 | 13, 14 and 15 | `TestNaturalGas::test_the_runs_counted_from_the_files_first_year` |
| 8 | gasoline 2006 on the older contract instead of RBOB | unreadable, no row on 2006-04-13 | `TestGasoline::test_the_2006_side_row_on_the_harbor_contract_is_missing` |
| 9 | the 10 natural gas entries on the March contract's last day, read from contract 3 instead of 4 | no year changes sign | `TestTheNaturalGasExpiries::test_ten_entries_fall_on_march_s_last_day_and_none_flips_on_the_other_file` |
| 10 | both trades, 2016 to 2023 | gasoline 3 of 8, natural gas 4 of 8 | `TestTheVerdicts::test_both_trades_after_the_book` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −3 profitable years, all 3 unreadable | reproduced with a gap | The criterion the issue pinned, exactly 19, fails at 16. The verdict was taken afterwards under this file's rule, and the issue records that. The file bounds the count between 16 and 19 rather than settling it. The cause is named and outside the method: EIA's harbor gasoline file holds no row on 1997-04-14, 1998-04-24 or 1999-04-23, each a trading day, and the run neither fills a row nor moves a date. Every readable year agrees with the book, because the 2 losses are the 2 that 21 less 19 allows. |
| 2 | none | none, not a replication | The book says which years were out of sample and prints no count for them. 7 of the 9 were profitable, and the two losses of row 1 both fall among them. |
| 3 | none, the source states a claim | reproduced with a gap | The criterion the issue pinned, a profit in every year, cannot be met with 3 years unreadable, and the verdict was taken afterwards on the same footing as row 1. The claim holds on every readable year, with no loss from 1995 to 2008. Read as 1995 to 2007 instead, it gives no loss and 10 profitable. |
| 4 | 0 | reproduced | Under the reading pinned on the issue, both figures written for the 2008 first edition and counted from 1995. |
| 5 | 0 | reproduced | The same reading. The two figures differ by the one year between the main text and the sidebar. |
| 6 | none | none, not a replication | A claim with no figure, and the issue declared no criterion for it. The halves are 15 of 15 and 7 of 15. |
| 7 | none | none, not a replication | 1994 is profitable too, so counting from the first year the files hold a whole trade makes both runs one longer. With runs ending in 2007 and 2008, only a count from 1995 matches, the year the gasoline sidebar names as its start. Counted from 1994, runs of 13 and 14 end in 2006 and 2007 instead. |
| 8 | none | none, not a replication | The older contract's file has no row on 2006's entry day, so the side row cannot say whether the switch to RBOB decides 2006. |
| 9 | none | none, not a replication | In 10 years the entry falls on the March contract's last trading day, so the file read depends on contract 1 keeping an expiring contract on its last day. The files show that convention in 2014 and 2019. Reading contract 3 instead flips no year, so the convention cannot move a verdict. |
| 10 | none | none, not a replication | After the book, gasoline profits in 3 of 8 years and natural gas in 4 of 8, its 2016 to 2023 share of row 6. |

### What the entry concludes

Three things.

1. **Natural gas reproduces under the pinned reading.** Every year from 1995
   to 2008 is profitable, which gives the main text's 13 and the sidebar's 14
   once both are read as first-edition figures counted from 1995. 2009 is a
   loss, so neither figure can be a run ending in the revised edition's years.
2. **Gasoline agrees with the book on every year the file can read.** 1995 to
   2015 holds the 2 losing years 19 of 21 allows and no third. The three
   unreadable years are gaps in EIA's file, not losses.
3. **In this exploratory record, both trades win fewer years after the years
   Chan read.** Natural gas wins 15 of 15 through 2008 and 7 of 15 after, which
   agrees with his remark at location 4632. Gasoline wins 3 of 8 from 2016 to
   2023. Eight years with no costs charged can show the change and cannot
   measure it.

### What this entry cannot say

Four things.

**What the three unreadable years held.** EIA's harbor file has no row on any
of them, and no other committed source covers the contract then. A source
holding each named contract's settlements would settle them.

**Whether Chan read the same contracts.** The sidebar names RB and glosses it
as the unleaded gasoline futures. Before RBOB began trading in October 2005,
his series presumably held the older contract, and the run assumes so. His
data vendor is not named.

**Which year each natural gas figure was written in.** Neither passage says,
and the reading pinned on the issue is a hypothesis that both are
first-edition figures counted from 1995. The files rule out a run ending in
the revised edition's years, because 2009 is a loss. They cannot pick the
start year, because 1994 is profitable too.

**Whether either trade pays after costs.** No commission, slippage or margin is
charged, as the rule on the issue states.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/commodity-seasonals-lessons.md](../blog/commodity-seasonals-lessons.md)
moves with it, since that post quotes most of these figures. So does its
figure of every year of both trades, which
`uv run python -m chan.commodity_seasonals_figures` redraws.

## Entry 12: post-earnings drift, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 7.2, Kindle location 3024, and the script
`pead.m` the example names. Shipped under
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20). It is the
first entry from Chan's second book, and its location numbers are that book's,
in [research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from [tests/test_pead.py](../tests/test_pead.py).

**Every figure Chan prints reproduces on his own files.** Prices drift in the
direction of an earnings surprise after the announcement, and Chan trades the
first day of that drift without knowing what was announced. On a day a stock
announced after the previous close and before the open, the gap from that
close to the open stands in for the surprise. A gap of at least half its
90-day moving standard deviation buys the stock at the open, or shorts it if
the gap was down, and the position is closed at the same day's close. Each
day's summed return is divided by 30. The book reports an APR of 6.7 percent
and a Sharpe ratio of 1.5. `pead.m` prints five figures, and the
transcription in `chan.pead` lands on all of them at the precision the script
prints.

One choice decides a printed digit. Chan's two books ship two helpers called
`smartstd`. The first edition's, which Entries 8 and 10 and Entry 7's
first-edition rows run, counts a missing value as zero and divides by n − 1.
Book two's, which Entry 7's revised MATLAB rows run too, skips it and divides
by n. With book two's, the arithmetic return is 0.066743, which prints as
Chan's 0.0667. With the first edition's it is 0.066833, which prints as
0.0668, and row 11 holds that.

Every row reads the same vintages and specification, so both are stated once
here.

1. **The vintages.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read for
   the open and the close, and `earnannfile/`, the 497 flag series of his
   `earnannFile.mat`, saved 2012-05-15. Both are read through
   `chan.series.load_panel`, and [data/README.md](../data/README.md) records
   where each came from and what it holds. **Every figure here is about
   survivors**, because the price file is the S&P 500 as Chan held it on
   2012-04-24, carried backwards.
2. **The specification.** `pead.m` at `45670240` in
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading).
   The prices are cut to the flag file's 330 days, 2011-01-03 to 2012-04-24,
   before the gap is taken. The lookback is 90 days, the entry is 0.5 moving
   standard deviations, and the denominator is 30. Every annualisation uses
   252 days, and the Sharpe ratio subtracts no risk-free rate. No cost is
   charged.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2011 and 2012 sample on a rule he chose, so the entry says whether his numbers
reproduce on his files and nothing about whether the drift pays today.

### What the book printed

`pead.m` prints its figures in the comment lines that close it, and the book
quotes two of them rounded.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Arithmetic annual return, 252 times the mean daily return | 0.0667 | `pead.m` |
| 2 | The same figure, as the book quotes it | "APR" of 6.7 percent | location 3024 |
| 3 | Sharpe ratio | 1.49 | `pead.m` |
| 4 | The same figure, as the book quotes it | 1.5 | location 3024 |
| 5 | Compounded APR | 0.0680 | `pead.m` |
| 6 | Maximum drawdown | −0.026052 | `pead.m` |
| 7 | Maximum drawdown duration | 109 days | `pead.m` |
| 8 | Most positions held on one day, which is the denominator | 30 | location 3024 |
| 9 | Annual return levered four times | "close to 27 percent" | location 3024 |
| 10 and 11 | the positions taken in all, and row 1 under the first edition's `smartstd` | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · smartmean(ret)` | 0.066743 | `TestTheFigures::test_the_arithmetic_annual_return_is_the_books_apr` |
| 2 | row 1, in percent at the book's one decimal, against the compounded figure's 6.8 | 6.7 | the same, and `TestTheFigures::test_the_books_apr_is_not_the_compounded_one` |
| 3 | `√252 · smartmean(ret) / smartstd(ret)`, book two's `smartstd` | 1.4909 | `TestTheFigures::test_the_sharpe_ratio` |
| 4 | row 3 at the book's one decimal | 1.5 | the same |
| 5 | `prod(1 + ret)^(252/330) − 1` | 0.067952 | `TestTheFigures::test_the_compounded_apr` |
| 6 | `calculateMaxDD` on `cumprod(1 + ret) − 1` | −0.026052 | `TestTheFigures::test_the_maximum_drawdown_and_its_duration` |
| 7 | the same | 109 days | the same |
| 8 | the most nonzero positions on one of the 330 days | 30 | `TestTheFigures::test_the_busiest_day_holds_chans_denominator` |
| 9 | four times row 1 | 0.266970 | `TestTheFigures::test_levered_four_times_it_is_close_to_27_percent` |
| 10 | the nonzero positions across the window, none in its first 89 days | 1,072 | `TestTheFigures::test_the_busiest_day_holds_chans_denominator` and `::test_no_stock_trades_before_its_window_fills` |
| 11 | row 1 with the first edition's `smartstd` in the moving deviation and the Sharpe ratio | 0.066833, and 1,071 positions | `TestTheHelperMovesADigit::test_the_first_editions_helper_misses_chans_printed_digit` and `::test_the_other_printed_figures_survive_the_swap` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | Chan's figure, on his own files, through his own script transcribed. |
| 2 | 0.0 | reproduced | The book's "APR" is the arithmetic figure. The compounded one is 6.8 percent at the book's precision, so the label names the wrong one of the two. |
| 3 | 0.00 | reproduced | The same as row 1. |
| 4 | 0.0 | reproduced | The same. |
| 5 | 0.0000 | reproduced | The same. |
| 6 | 0.000000 | reproduced | The same. The port keeps `calculateMaxDD`'s two quirks, a high-water mark that starts at zero and a loop that starts on the second row. Neither moves this run, because its first day returns nothing, so `tests/test_matlab_helpers.py` holds both on inputs where they do. |
| 7 | 0 | reproduced | The same. |
| 8 | 0 | reproduced | The 30 is a fact about the run that Chan then used as an input, and the run gives it back. He names the look-ahead bias that makes it at location 3024. |
| 9 | 0 | reproduced | 26.6970 percent rounds to 27, the precision Chan quotes. Leverage multiplies every day's return by four, so it multiplies the arithmetic figure by four. |
| 10 | none | none, not a replication | The first 89 days hold no position, because the moving deviation has not filled. |
| 11 | none | none, not a replication | The first edition's helper also takes one position fewer, 1,071. The Sharpe ratio, the compounded APR and the drawdown still print as Chan's, so the arithmetic return is the only printed figure it moves. |

### What the entry concludes

Two things.

1. **Example 7.2 reproduces exactly on Chan's own files.** Every figure
   `pead.m` prints, both figures the book quotes, its 30 and its levered 27
   percent land at the precision each was printed.
2. **Which book's helper runs is part of the specification.** The two
   `smartstd` files share a name and differ in what they do with a missing
   value and in their denominator. Here the difference is one unit in one
   printed digit, so a port that reached for the helper the repo already held
   would have looked like a near miss on a vintage problem rather than a
   wrong helper.

### What this entry cannot say

Four things.

**What the drift earned on the index as it stood each day.** Every stock here
was in the S&P 500 on 2012-04-24.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) reruns the
rule on a point-in-time universe, which waits on a purchase.

**Whether Chan's flags are the announcement calendar.** They catch three of
Apple's five releases inside the window, a measurement recorded on
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20).
[Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) reruns the
rule on EDGAR's filings and modern prices.

**What costs would take.** `pead.m` charges none, and every position is a
round trip inside one day.

**How large the look-ahead in the 30 is.** Chan argues it is small because the
number of announcements a day is predictable, and nothing here tests that.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/post-earnings-drift-lessons.md](../blog/post-earnings-drift-lessons.md)
moves with it, since that post quotes most of these figures. So does the
post's one figure, which `uv run python -m chan.pead_figures` redraws.

## Entry 13: the PCA factor model, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading*, Example 7.4, "Principal
Component Analysis as an Example of the Factor Model". The revised edition
prints it on pp. 163 to 167, read in the Kindle Cloud Reader on 2026-10-03,
with its setup at Kindle location 4034 and its result at 4051. The first
edition's script is `example7_4.m`. Shipped under
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21).

Sixteen rows, all derivable from
[tests/test_pca_factor.py](../tests/test_pca_factor.py). Eight do not pair one
published figure with one computation. Row 7 sets two readings against three
printed figures, row 9 sets three programs against one, and rows 11 to 16
carry no published figure.

**Three of the four printouts reproduce, and Chan's account of why they
disagree does not hold.** The strategy takes five statistical factors from a
year of returns, assumes the factor returns carry momentum, buys the 50 stocks
with the highest expected return and shorts the 50 with the lowest. Chan
reports 2 percent a year in MATLAB and 4 percent in Python and R, and calls the
difference "essentially round off errors". The first edition's MATLAB, the
revised MATLAB and the revised Python each land on every figure they print,
on the file they all load. The revised R prints the Python's three figures to
17 digits, and its own code reads differently.

The spread between 2 and 4 percent is method. The revised Python never uses
its factors. It regresses each stock's returns on an intercept and five factor
series and ranks on the summed fitted values, and with an intercept in the
regression that sum is the stock's summed return. So the Python ranks on a
year of momentum, and its book is the same on every day as a ranking that
leaves the PCA out. The revised MATLAB fits today's cross-section of returns
on the stocks' factor exposures instead. Given the MATLAB's 50 longs, the
Python's book matches the MATLAB's on none of the 752 days both trade.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `ijr_20080114/`, the 600 stocks of Chan's
   `IJR_20080114.mat`, saved 2008-01-15, spanning 2004-01-15 to 2008-01-14,
   read for the close through `chan.series.load_panel`. Every printout loads
   this file. The revised repost's `.mat` has the sha256 the lifted file has,
   and the Python's text file holds the same closes to 2.0e-16, which
   [data/README.md](../data/README.md) records. **Every figure here is about
   survivors**, because the file holds the S&P 600 as it stood on 2008-01-14,
   carried backwards.
2. **The specification.** A lookback of 252, five factors, 50 stocks shorted
   and no cost, under each printout's own rule as `chan.pca_factor`
   transcribes it. The first edition's `example7_4.m` is read at `1a71950` in
   the mirror [data/README.md](../data/README.md) names. The revised MATLAB and
   Python are read from the book's pages and from their reposts at
   pinhaocheng/epchan-quant_trading_MATLAB_codes `7430b84` and
   pinhaocheng/epchan-quant_trading_Python_codes `5fcab61`. The R is read from
   the pages alone. Every annualisation uses 252 days, and no Sharpe ratio
   subtracts a risk-free rate.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2004 to 2008 sample on a rule he chose, so the entry says whether his numbers
reproduce on his file and nothing about whether a statistical factor model
earns money.

### What the book printed

The revised edition prints each program's figures in the comment lines that
close its listing, and the text quotes two of them as whole percents. Only the
text is among the committed highlights. The code-printed figures are not, and
[research/book-notes/README.md](../research/book-notes/README.md) records that
absence.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | First-edition MATLAB, `smartmean(ret)*252`, a sum over positions | −1.8099 | `example7_4.m`, first edition |
| 2 | Revised MATLAB, annual mean return | 0.020205 | revised edition p. 164 |
| 3 | Revised MATLAB, Sharpe ratio | 0.211120 | revised edition p. 164 |
| 4 | Revised Python, annual mean return | 0.04052422056844459 | revised edition p. 165 |
| 5 | Revised Python, annualised standard deviation | 0.07002908500498846 | revised edition p. 165 |
| 6 | Revised Python, Sharpe ratio | 0.5786769963588398 | revised edition p. 165 |
| 7 | Revised R, the same three lines | rows 4 to 6, digit for digit | revised edition p. 167 |
| 8 | The MATLAB return, as the text quotes it | 2% | location 4051 |
| 9 | The Python and R return, as the text quotes it | 4% | location 4051 |
| 10 | Why the programs differ | "essentially round off errors" | location 4051 |
| 11 to 16 | what separates the printouts, and each without PMC | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `first_edition_matlab`, the mean over 1,005 rows | −1.809865 | `TestThePrintouts::test_the_first_edition_prints_minus_1_8099` |
| 2 | `revised_matlab`, the mean over the 752 days that trade | 0.020205 | `TestThePrintouts::test_the_revised_matlab_prints_its_two_figures` |
| 3 | the same, with book two's `smartstd` | 0.211120 | the same |
| 4 | `revised_python`, the mean over all 1,006 rows | 0.040524220568445 | `TestThePrintouts::test_the_revised_python_lands_its_printed_figures` |
| 5 | the same, `np.nanstd` dividing by n | 0.070029085004988 | the same |
| 6 | the same | 0.578676996358840 | the same |
| 7 | `revised_r_reading`, unfilled and forward-filled | 0.0401, 0.0797, 0.5038 and 0.0426, 0.0802, 0.5319 | `TestThePrintouts::test_neither_r_reading_lands_the_printed_figures` |
| 8 | row 2 at the text's whole percent | 2% | `TestThePrintouts::test_the_revised_matlab_prints_its_two_figures` |
| 9 | row 4 at the text's whole percent, and row 7's two readings | 4%, 4% and 4% | `TestThePrintouts::test_the_revised_python_lands_its_printed_figures` and `::test_neither_r_reading_lands_the_printed_figures` |
| 10 | the shared days on which the revised MATLAB and the Python given 50 longs hold the same book, and the fewest positions in which they differ on one day | 0 of 752, and 125 | `TestWhatSeparatesTwoFromFour::test_at_one_size_the_revised_books_are_never_identical` and `::test_round_off_does_not_explain_the_spread` |
| 11 | the Python ranked on each stock's summed return, with the PCA left out | the same book on every day | `TestWhatSeparatesTwoFromFour::test_the_pythons_pca_changes_no_position` |
| 12 | the mean share of the revised MATLAB's names the Python holds the same way, as printed and with 50 longs | 13.83% and 14.14% | `TestWhatSeparatesTwoFromFour::test_the_revised_books_share_few_names` and `::test_at_one_size_the_revised_books_are_never_identical` |
| 13 | the Python buying the top 50 rather than the 49 ranked second to 50th | 0.0414, Sharpe ratio 0.5908 | `TestWhatSeparatesTwoFromFour::test_fifty_longs_move_the_pythons_figures` |
| 14 | the Python over its 751 trading days, the first edition over its 753, and the Python keeping the first book it clears | 0.0543, Sharpe ratio 0.6699, then −2.4156, then 0.0417, Sharpe ratio 0.5945 | `TestWhatSeparatesTwoFromFour::test_averaging_over_trading_days_moves_both_programs` and `::test_keeping_the_first_book_moves_the_pythons_figures` |
| 15 | row 3 under the first edition's `smartstd` | 0.2441 | `TestWhatSeparatesTwoFromFour::test_the_first_editions_smartstd_moves_the_revised_sharpe` |
| 16 | rows 1 to 6 without PMC | −1.8014, then 0.0180 and 0.1869, then 0.0408 and 0.5851 | `TestTheSplice::test_each_printout_without_pmc` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | Chan's first-edition figure, on his file, through his script transcribed. It is a sum over 100 positions of ±1 with no division by capital, and its mean runs over 252 rows from before the first trade. |
| 2 | 0.000000 | reproduced | The same, for the revised MATLAB. |
| 3 | 0.000000 | reproduced | The same. The printed figure lands with book two's `smartstd` and misses with the first edition's, row 15, and the revised repost at `7430b84` carries book two's file. |
| 4 | under 1e-15 | reproduced | Within 1e-12 of each figure printed to 17 digits, the verdict's criterion, and within 1e-15, the pin. They agree to 15 significant digits. |
| 5 | under 1e-15 | reproduced | The same. |
| 6 | under 1e-15 | reproduced | The same. |
| 7 | none | did not reproduce | Neither reading of the printed R lands its printed figures, which are the Python's to the last digit. The R's window ends today rather than yesterday, it buys 52, its mean skips the days with no position, and its `sd` divides by n − 1. It sources a `calculateReturns.R` the book does not print, and no R runtime is installed here, so the row is a reading of the code rather than a run of it. [Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it once Chan's download is in hand. |
| 8 | 0 | reproduced | 2.02 percent rounds to 2. |
| 9 | 0 | reproduced | The Python's 4.05 percent rounds to 4, and so does each R reading. The whole-percent figure is reached even by the code whose 17-digit figures are not. |
| 10 | none | did not reproduce | Round-off would leave two books of one size the same on every day. The printed Python buys 49 and the MATLAB 50, so the comparison gives the Python 50, and the books then match on none of 752 days and differ in at least 125 positions on each. The criterion was written on [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the overlap was measured, which is the cost named there. |
| 11 | none | none, not a replication | This is why the Python's figure is momentum's. Its PCA changes no position. |
| 12 | none | none, not a replication | The two revised programs trade mostly different stocks. |
| 13 | none | none, not a replication | The Python's `np.arange(-topN, -1)` never buys the top-ranked stock. |
| 14 | none | none, not a replication | The Python's mean and spread run over all 1,006 rows, including 255 that hold no position, and its `positionsTable[capital==0,]=0` zeroes its first book. The first edition's mean runs over 252 rows with no position. |
| 15 | none | none, not a replication | The first edition's `smartstd` zero-fills a missing day and divides by n − 1. |
| 16 | none | none, not a replication | PMC closes at 6.02 on 2004-03-12 and resumes at 17.25 on 2007-08-01, two price histories under one symbol. Every program but the unfilled R reading forward-fills, so the gap becomes one day's return of 1.8654. |

### What the entry concludes

Two things.

1. **The three printouts that can run reproduce on Chan's file.** The first
   edition's −1.8099 and the revised MATLAB's 0.020205 and 0.211120 land at
   the precision printed, and the revised Python's three 17-digit figures land
   within 1e-15.
2. **The 2-versus-4 spread is two different strategies, not round-off.** The
   revised MATLAB trades a factor model and the Python trades a year of
   momentum, because its regression's intercept cancels its factors. Three
   bookkeeping choices each lower the Python's figure toward the MATLAB's: its
   long side, its averaging, and the first book it clears. Without any one of
   them the Python's figure is higher than 4.05 percent, rows 13 and 14.

### What this entry cannot say

Four things.

**What the strategy earned on the index as it stood each day.** Every stock
here was in the S&P 600 on 2008-01-14.
[Issue 269](https://github.com/l3a0/quantitative-trading/issues/269) reruns it
on a point-in-time universe, which waits on data.

**What the R printout actually computed.** Without `calculateReturns.R` and an
R runtime, row 7 is a reading.
[Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it
once Chan's download is in hand.

**What costs would take.** Every printout charges none, and the books turn over
daily.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/factor-models-lessons.md](../blog/factor-models-lessons.md) moves with
it, since that post quotes most of these figures.

## Entry 14: the market and momentum factors, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 3978, 4004
and 4014. Shipped under
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22). Every
location is the revised edition's. Whether the first edition carries the
sentences at 4004 and 4014 was not checked.

Nine rows, all derivable from
[tests/test_momentum_factor.py](../tests/test_momentum_factor.py).

**The claim holds for the market factor and does not hold for the momentum
factor.** Chan says at location 4014 that "often factor returns are more
stable than individual stock returns", that they "exhibit stronger serial
autocorrelations than individual stock's returns", and so "have momentum".
That persistence is what lets this period's factor return stand in for the
next. Two of the factors his section names need only prices. MKT, which
location 3978 names as "the return of the market", is built here as the
index's return over the bill rate, the way French's market factor is. WML, winners
minus losers, defined at location 4004, longs the stocks whose past return was
positive and shorts those whose past return was negative. Over 83 months,
MKT's lag-1 autocorrelation is 0.0675 and WML's is −0.1099, against a median
of −0.0392 across the 446 stocks priced in every month. MKT is above 0 and
above the median stock. WML is below both.

Two rows are claims and seven are not replications. Rows 1 and 2 take the
claim route `### Rows that are not replications` describes, one per factor.
Rows 3 to 9 are the figures the issue reports beside the verdicts, which
decide nothing.

Every rule was fixed on
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22) on
2026-10-03, before any autocorrelation was computed. The owner ruled the same
day, also before, that each factor carries its own verdict with Chan's "often"
quoted beside it and that no combined verdict is formed. Four of the rules
carry the result, so they are stated here.

1. **The vintages.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, saved 2007-11-24, read through `chan.series.load_panel`.
   `spy_chan.csv`, the adjusted-close column of his `example6_2.xls`, saved
   2008-01-29. FRED's TB3MS, downloaded 2026-09-30.
   [data/README.md](../data/README.md) says what each holds.
2. **The construction.** The month-ends are the panel's rows whose next row
   falls in another month, Chan's own rule, which gives 96 from 1999-11-30 to
   2007-10-31. At month-end t a stock's past return runs from its close at
   t − 12 to its close at t − 1, skipping the latest month as French's
   momentum factor does. A positive past return makes a winner and a negative
   one a loser. A stock enters only with a finite close at all 14 month-ends
   from t − 12 to t + 1, which leaves 442 to 494 at each formation. Each leg is
   equally weighted, held one month, and charged no costs. MKT is SPY's
   month-end to month-end return less that month's TB3MS over 12. The
   holding months run from December 2000 to October 2007, 83 of them.
3. **The statistic.** `pandas.Series.autocorr(lag=1)` on each series of 83
   monthly returns, which is the correlation of the 82 pairs of one month's
   return with the month before. The comparison set is every stock with a
   finite return in all 83 months, 446 of them, and their median stands for
   "individual stock's returns".
4. **The criterion.** The claim holds for a factor when its autocorrelation is
   above 0 and above the median stock's, both compared unrounded. Monthly is
   the only frequency computed, because the factors are re-formed monthly.

**Every figure touching the stocks is about survivors.** The panel is the
S&P 500 as it stood on 2007-11-23, carried backwards. That reaches WML's two
legs in opposite directions, and which dominates is not measured here.

1. **The loser leg** lacks the stocks that fell and then left the index, so
   it holds losers that recovered enough to stay. That pushes WML down.
2. **The winner leg** lacks past winners that later collapsed out of the
   index. That pushes WML up.

MKT reads SPY, which held the index as it stood each day, so it carries no
survivorship.

Every result here is **exploratory**. Testing a claim someone else chose
spends the 2000 to 2007 sample on it, so the entry says whether the claim
holds on this file and nothing about factor momentum today.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | MKT has stronger serial autocorrelation than single stocks, so it has momentum | the claim, "often", with no figure | location 4014, MKT defined at location 3978 |
| 2 | WML has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014, WML defined at location 4004 |
| 3 to 9 | each factor's autocorrelation and percentile, the stocks' quartiles, the band, each factor's mean and t-statistic, and the legs | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | MKT's autocorrelation against 0 and against the median stock's, unrounded | 0.0675, above 0 and above −0.0392 | `TestTheVerdicts::test_mkt_holds_above_zero_and_above_the_median_stock` |
| 2 | WML's autocorrelation against the same two | −0.1099, below 0 and below −0.0392 | `TestTheVerdicts::test_wml_does_not_hold_on_either_half` |
| 3 | MKT's lag-1 autocorrelation, and the percent of the 446 stocks strictly below it | 0.0675, 80.7175, which is 360 stocks | `TestTheFigures::test_mkts_autocorrelation` and `::test_each_factors_percentile_among_the_stocks` |
| 4 | WML's lag-1 autocorrelation, and the same percent | −0.1099, 27.8027, which is 124 stocks | `TestTheFigures::test_wmls_autocorrelation` and `::test_each_factors_percentile_among_the_stocks` |
| 5 | the 446 stocks' lag-1 autocorrelations, lower quartile, median and upper quartile, by linear interpolation | −0.1198, −0.0392 and 0.0402 | `TestTheFigures::test_the_stocks_quartiles` |
| 6 | ±1.96/√83, and which factors fall outside it | 0.2151, neither | `TestTheBand::test_the_band_is_1_96_over_root_83` and `::test_neither_factor_falls_outside_it` |
| 7 | MKT's mean monthly return times 12, and its plain t-statistic | 0.0185 and 0.3660 | `TestTheFigures::test_each_factors_annual_mean_and_t_statistic` |
| 8 | WML's mean monthly return times 12, and its plain t-statistic | 0.0241 and 0.4505 | `TestTheFigures::test_each_factors_annual_mean_and_t_statistic` |
| 9 | the eligible stocks, the excluded stocks, the winner leg and the loser leg, fewest and most over the 83 formations | 442 to 494 eligible, so 6 to 58 excluded for a missing close. Winners 79 to 468, losers 11 to 397 | `TestTheLegs::test_442_to_494_stocks_are_eligible`, `::test_6_to_58_stocks_are_excluded` and `::test_the_winner_and_loser_legs_sizes` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The claim holds for MKT, which Chan says factors "often" show. Its autocorrelation is above 0 and above the median stock's, under the criterion declared on the issue before any autocorrelation was computed. It sits at 0.0675, inside row 6's band, so a series with no autocorrelation would land there often, and this verdict could be noise. |
| 2 | did not reproduce | The claim, which Chan says factors "often" show, does not hold for WML, on either half: its autocorrelation is below 0 and below the median stock's. Under the owner's ruling this verdict stands on its own, and no combined verdict is drawn from rows 1 and 2. The value is forced, because the log's two other verdicts both need the claim to survive. Two causes outside the method are open and neither is measured: the panel holds only survivors, and 2000 to 2007 is one window. Nothing here argues which way either moves an autocorrelation. |
| 3 | none, not a replication | MKT sits at the 80.7175th percentile of the stocks, above 360 of 446. |
| 4 | none, not a replication | WML sits at the 27.8027th percentile, above 124 of 446, so it is less persistent than most single stocks on this file. |
| 5 | none, not a replication | The quartiles use pandas' default linear interpolation. The median is negative, so on this file a factor above 0 is also above the median stock. That is a fact about this panel, and the criterion keeps both halves as declared. |
| 6 | none, not a replication | Under a series with no autocorrelation, an estimate from 83 months falls outside ±0.2151 about 5 percent of the time. Both factors sit inside it, so neither verdict rests on an autocorrelation 83 months can tell from zero. |
| 7 | none, not a replication | MKT's mean monthly return over the bill, times 12, is 0.0185, an arithmetic figure rather than a compounded one. Its plain t-statistic of 0.3660 is uncorrected for autocorrelation and decides nothing. |
| 8 | none, not a replication | WML's mean monthly return times 12 is 0.0241, with a plain t-statistic of 0.4505 that decides nothing. Survivorship moves a mean before it moves an autocorrelation, so this row carries the survivor-only label most loudly. |
| 9 | none, not a replication | Every formation has both legs, so the refusal for an empty leg never fires. At its smallest the loser leg holds 11 stocks, so WML's return that month rests on few short positions. |

### What the entry concludes

Three things, and the first is the verdict.

1. **On this file the claim holds for the market factor and not for the
   momentum factor.** MKT's autocorrelation is positive and above the median
   stock's. WML's is negative and below the median stock's. Each verdict
   stands on its own, with Chan's "often" quoted beside it, and the entry
   draws no combined verdict from the two.
2. **Neither autocorrelation is far from zero.** Both sit inside the band a
   series with no autocorrelation stays inside 95 percent of the time, so 83
   months cannot tell MKT's 0.0675 from no persistence at all. The verdict in
   row 1 is what the declared criterion says, and row 6 says how little it
   rests on.
3. **The median stock sits below 0 on this file.** Its lag-1 autocorrelation
   is −0.0392, so a factor above 0 is also above the median stock here. The
   comparison set is survivors, so where the median sits is a fact about this
   panel rather than about single stocks in general.

### What this entry cannot say

Four things.

**What survivorship does to WML.** The panel lacks the stocks that left the
index before 2007-11-23, and the two legs lose different ones.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) waits on
a panel of the index as it stood each day, which would measure it.

**Whether the factors persist at another frequency.** Only monthly returns
were computed, by the rule on the issue, so a daily autocorrelation was not
tried after the monthly one was seen.

**Whether French's published factors agree.** Kenneth French's library
publishes a market and a momentum factor built on every listed stock.
[Issue 274](https://github.com/l3a0/quantitative-trading/issues/274) records
that library as a vintage, and the skip here matches its momentum factor's so
the two can be set side by side.

**What the other two factors of location 3978 do.** SMB and HML need market
capitalisation and book value at each date, which this repo does not hold.
[Issue 273](https://github.com/l3a0/quantitative-trading/issues/273) carries
them.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/factor-models-lessons.md](../blog/factor-models-lessons.md) moves with
it, since that post quotes most of these figures. So does its one figure, which `uv run python -m chan.momentum_factor_figures` redraws.

## Entry 15: calendar spreads, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 3951. Shipped
under [issue 137](https://github.com/l3a0/quantitative-trading/issues/137),
under the rules
[issue 16](https://github.com/l3a0/quantitative-trading/issues/16) sets for
every stationary candidate Chan names there.

Fourteen rows, all derivable from
[tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py).

**Chan's claim reproduces for natural gas and does not reproduce for RBOB
gasoline.** Chan names calendar spreads as "the simplest examples of
cointegrating futures pairs". Of 360 adjacent natural gas pairs, 57 reject no
cointegration in both orientations, against a bar of 47. Of 220 RBOB pairs, 14
reject, against a bar of 31. Each bar is the 975th of 1,000 shares from
simulated contracts that do not cointegrate but move together as closely as
the real ones do.

**The bars were corrected after the result was seen, and both readings are
reported.** The issue declared a null in which every contract is an
independent random walk, and under it the bars are 19 and 13 and both
commodities reproduce. Review found that real neighbouring contracts move
almost together, and that at that correlation the requirement that both
orientations reject is barely stricter than one. The owner ruled on 2026-10-03
to re-judge both commodities against a null at the files' own correlation, and
the reasoning and the measurement are recorded on the issue. The correction can
only make a pass harder, so it is not a search toward the claim. It moves the
RBOB verdict and not the natural gas one.

Two rows are replications and twelve are not. Rows 1 and 2 are the claim, one
per commodity, and each takes the claim route
`### Rows that are not replications` describes. Rows 3 and 4 are the claim
under the declared null, which rows 1 and 2 supersede. Row 5 is the
correlation the correction reads. Rows 6 to 12 describe the two batches, and
row 12 was added after the verdicts were seen. Rows 13 and 14 check the expiry
map the pairs are read through.

Rows 1 to 12 read the same vintages and specification, so they are stated
once here.

1. **The vintages.** EIA's NYMEX settlements for the nearest four contracts,
   all downloaded 2026-10-02 on the raw basis. Natural gas is `eia_rngc1` to
   `eia_rngc4`, 1993-12-20 to 2024-04-05 across the four. RBOB gasoline is
   `eia_eer-epmrr-pe1-y35ny-dpg` to `pe4`, 2005-10-03 to 2024-04-05.
   [data/README.md](../data/README.md) says what each file holds. New York
   Harbor gasoline is left out. Its four files each lack different days, so an
   adjacent pair of its contracts keeps a median of 42 days and 141 of its 150
   pairs keep fewer than 50. The issue measured that before any statistic, and
   no test pins it.
2. **The pairs.** Every pair of adjacent delivery months, contract m against
   m+1, whose whole window lies inside all four of a commodity's files: 360
   natural gas pairs with near months May 1994 to April 2024, and 220 RBOB
   pairs with near months January 2006 to April 2024. A wider gap is out,
   because it overlaps for two months or less inside the nearest four.
3. **The days.** A pair's window is every trading day both contracts sit in
   the nearest four, from the day after contract m−3 expires through contract
   m's last day. Six days of it are dropped: the first and last, and each of
   the two expiries inside it with the day after. An expiry rule one day wrong
   then misreads only dropped days. A day either file lacks is dropped rather
   than filled. Natural gas pairs keep 39 to 59 days, a median of 56, and RBOB
   pairs 40 to 59, a median of 57.
4. **The test.** Engle-Granger on levels at one lag, in both orientations,
   because the test is not symmetric and Chan names no dependent leg. A pair
   rejects only when both orientations clear the 10% bar of −3.04.
5. **The criterion.** A commodity's statistic is the share of its pairs that
   reject. The bar's critical values are asymptotic while a window is about 56
   days, and pairs sharing a contract are not independent, so 10% is not the
   reference for that share and the reference comes from simulation. In each
   of 1,000 sets, seed 20261003, every contract walks on every trading day of
   its run, and each pair is read on the same days the real pair keeps. The
   claim reproduces for a commodity when its share is strictly above the 975th
   of those 1,000 shares. The 975th rather than the 950th splits a family-wise
   5% across the two commodities. The owner ruled on 2026-10-03 that each
   commodity carries its own verdict, and there is no combined one.
6. **The correction.** In the declared null each contract's walk is
   independent. In the corrected one it is the square root of ρ times one walk
   shared by the whole commodity, plus the square root of 1 − ρ times its own,
   so any two contracts' daily changes correlate at ρ. ρ is the commodity's
   median, over its pairs, of the correlation between the two legs' daily
   changes on the days the pair keeps. Everything else in item 5 is unchanged.

No pair is tested alone, because 56 days give one pair little power, and no
pair's result is a finding about that pair. Every result here is
**exploratory**. The sample was spent on a claim Chan stated, so the entry says
whether these spreads behaved as he said over these windows and nothing about
whether trading them pays.

### What the book printed

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`. Chan's later book qualifies the
sentence, at *Algorithmic Trading* location 2321, saying calendar spreads "do
not generally mean-revert". The issue recorded that as a prior against the
claim before any statistic, so the result cannot be presented afterwards as a
surprise in either direction.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | Natural gas calendar spreads cointegrate | the claim, with no figure | Kindle location 3951 |
| 2 | RBOB gasoline calendar spreads cointegrate | the same claim | Kindle location 3951 |
| 3 | Natural gas, the claim under the declared null | the same claim | Kindle location 3951 |
| 4 | RBOB, the claim under the declared null | the same claim | Kindle location 3951 |
| 5 | How closely the two legs of a pair move together | nothing | n/a |
| 6 | Natural gas, each orientation alone | nothing | n/a |
| 7 | RBOB, each orientation alone | nothing | n/a |
| 8 | Natural gas, the residual check at one lag | nothing | n/a |
| 9 | RBOB, the residual check at one lag | nothing | n/a |
| 10 | Natural gas, how often spreads that truly revert reject | a 36-day half-life for a 12-month crude oil calendar spread, used here as the reversion speed | *Algorithmic Trading* locations 2461 and 2471 |
| 11 | RBOB, the same | the same | the same |
| 12 | How many null sets reach each commodity's share | nothing | n/a |
| 13 | Natural gas, whether the files hand over on the expiry rule's day | nothing | n/a |
| 14 | RBOB, the same | nothing | n/a |

### What this repo computed

| # | Pairs | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 360 natural gas | the share rejecting in both orientations, against the 975th of 1,000 shares under the corrected null | 57 of 360, 0.1583, against 47 of 360, 0.1306. The null's median is 35 of 360 | `TestTheCalendarSpreadVerdicts::test_natural_gas_reproduces` |
| 2 | 220 RBOB | the same | 14 of 220, 0.0636, against 31 of 220, 0.1409. The null's median is 21.5 of 220 | `TestTheCalendarSpreadVerdicts::test_rbob_does_not_reproduce` |
| 3 | 360 natural gas | the same share against the declared null, every contract an independent walk | against 19 of 360, 0.0528, with a median of 12 | `TestTheCalendarSpreadVerdicts::test_under_the_declared_null` |
| 4 | 220 RBOB | the same | against 13 of 220, 0.0591, with a median of 7 | the same |
| 5 | both | ρ, the median correlation of the two legs' daily changes over a commodity's pairs | 0.9942 for natural gas and 0.9951 for RBOB | `TestTheCalendarSpreadVerdicts::test_the_correlation_the_correction_reads` |
| 6 | 360 natural gas | each orientation alone at 10% | near on far 62 and far on near 62 | `TestTheCalendarSpreadDescriptions::test_each_orientation_alone` |
| 7 | 220 RBOB | the same | near on far 17 and far on near 16 | the same |
| 8 | 360 natural gas | pairs whose one-lag fit passes both halves of the residual check | near on far 250 and far on near 255 | `TestTheCalendarSpreadDescriptions::test_the_residual_check_at_one_lag` |
| 9 | 220 RBOB | the same | near on far 168 and far on near 166 | the same |
| 10 | 360 natural gas | 1,000 sets in which every pair cointegrates: the far leg a random walk and the near leg the far leg plus a Gaussian AR(1) spread with a 36-day half-life, seed 20261004, tested as row 1 is | a mean share of 0.0609, 21.9 of 360 pairs | `TestTheCalendarSpreadDescriptions::test_the_power_row` |
| 11 | 220 RBOB | the same | a mean share of 0.0614, 13.5 of 220 pairs | the same |
| 12 | both | null sets whose share reaches the real one. Added after the verdicts were seen, not declared | under the corrected null, none of 1,000 for natural gas and 973 for RBOB. Under the declared null, none and 22 | `TestTheCalendarSpreadVerdicts::test_how_many_null_sets_reach_each_share` |
| 13 | 363 natural gas expiries, February 1994 to April 2024 | expiries where the files' prices hand over on the rule's day rather than not, among those every file can read, then with the rule moved one trading day earlier and one later | 298 of 316. Moved earlier 38 of 324, and later 16 of 324 | `TestTheExpiryMapAgainstTheFiles::test_the_handover_counts` |
| 14 | 220 RBOB expiries, January 2006 to April 2024 | the same | 202 of 213. Moved earlier 15 of 210, and later 9 of 213 | the same |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The share is strictly above the 975th corrected null share, 57 against 47, and no corrected null set reaches it. It also clears the declared null, so the correction does not move this verdict. |
| 2 | did not reproduce | 14 is well under the bar of 31, and 973 of 1,000 corrected null sets reach it. Contracts that move together this closely and do not cointegrate give RBOB's share most of the time. |
| 3 | none, superseded by row 1 | Under the declared null natural gas also reproduces, 57 against 19. |
| 4 | none, superseded by row 2 | Under the declared null RBOB cleared 13 by one pair. That pass came from a null whose contracts move independently, which real contracts do not. |
| 5 | none, not a replication | The correction's one input. Contracts a month apart move almost as one, which is what makes requiring both orientations nearly no stricter than requiring one. |
| 6 | none, not a replication | Requiring both orientations costs five pairs against either one alone. |
| 7 | none, not a replication | Requiring both costs three pairs against the near-on-far orientation alone. Reading either orientation would have been the search [issue 16](https://github.com/l3a0/quantitative-trading/issues/16) forbids. |
| 8 | none, not a replication | About seven fits in ten pass. The rest fail the check, so their statistics are read against critical values that may not apply. The criterion reads lag 1 and the null is tested at lag 1 too, so the search for a passing lag count was left out rather than run on one side only. |
| 9 | none, not a replication | About three fits in four pass, the same reading as row 8. |
| 10 | none, not a replication | A measure of power. If every natural gas pair reverted at 36 days, 21.9 of 360 would reject on average. The real 57 is far more than spreads reverting that slowly would give, so whatever produces the rejections reverts faster within these windows, or comes from something neither simulation models. The row decides neither. |
| 11 | none, not a replication | If every RBOB pair reverted at 36 days, 13.5 of 220 would reject on average. The real 14 is about what reversion that slow would give, and also about what no reversion at all gives under row 2's null, so a 56-day window cannot tell the two apart for RBOB. |
| 12 | none, not a replication | Added after the verdicts were seen, because a bar alone does not say how close a verdict sat to it. |
| 13 | none, not a replication | The rule's day fits 298 of 316 handovers, about 94%, and a day either side fits between 4% and 12% of them, so the map reads the right contract on almost every day. Whether each of the 18 that do not fit is noise or a rule one day off is not settled here, and one day is what the dropped days absorb. A rule two days off would put a neighbouring contract into a day or two of four pairs, which these counts do not rule out. |
| 14 | none, not a replication | The same reading for RBOB, with 11 that do not fit. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Natural gas reproduces and RBOB does not.** Natural gas rejects in 57
   pairs against a bar of 47 from contracts that move together as the real
   ones do, and no null set reaches 57. RBOB rejects in 14 against a bar of
   31, which most null sets reach. Each verdict stands alone, as the owner
   ruled.
2. **Requiring both orientations is not the safeguard it looks like here.**
   It was declared so that neither leg would be chosen as the dependent one
   after the fact. Two contracts a month apart move almost as one, and then
   the two orientations nearly agree, so the requirement removes little. With
   no cointegration, a null of independent walks has a median of 12 natural
   gas pairs rejecting, and a null at the files' correlation has 35. The
   declared null missed that, and it is why the bars were corrected.
3. **The expiry map holds where it was checked, and one correction to it was
   owed.** Three days the calendar listed as closures, the two days of
   Hurricane Sandy in October 2012 and 2018-12-05, are days every natural gas
   and RBOB file settled. Counted closed, they put the November 2012 natural
   gas expiry two trading days early, beyond what the dropped days absorb, so
   the calendar no longer counts them closed. No figure in Entry 11 reads any
   of the three.

### What this entry cannot say

Four things.

**Whether a pair cointegrates over its whole life.** The nearest four hold a
pair for about three months. A contract's full history, and gaps wider than
one month, need contract-level data EIA does not publish. A probe of the
Massive futures API on 2026-10-03, recorded on
[issue 137](https://github.com/l3a0/quantitative-trading/issues/137), returned
no bars for the three natural gas contracts it asked for, so no free source for
that data is known here. It is a stronger test than Chan's sentence asks for
and nothing has asked for it, so it is deferred under the ranking rule rather
than filed.

**How much the corrected null leaves out.** It gives every pair of contracts
in a commodity one correlation, the median, and equal volatilities. Real
correlations vary from pair to pair and over time, and so do the two legs'
volatilities. Natural gas clears the corrected bar by ten
pairs and RBOB misses it by seventeen, so neither verdict sits on that edge.

**Which pairs cointegrate.** No pair is a finding, because a pair tested on
56 days has little power and 580 pairs tested at 10% produce rejections by
chance.

**Whether trading a calendar spread pays.** Cointegration is a statement about
two price series. A trade adds costs, roll timing and margin, and none of
those are here.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.
[blog/calendar-spreads-lessons.md](../blog/calendar-spreads-lessons.md) moves
with it, since that post writes up every row, and so does
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md),
since that post quotes the verdicts. So does the calendar spreads post's
figure, which `uv run python -m chan.calendar_spread_figures` redraws.

## Entry 16: Conditional Parameter Optimization, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 7.1, pp. 137 to 146.
Shipped under [issue 23](https://github.com/l3a0/quantitative-trading/issues/23).

Eleven rows, all derivable from [tests/test_cpo.py](../tests/test_cpo.py) on a
machine that holds the owner's data archive. On any other machine those tests
skip, which is the price of the exception `docs/design.md`'s premise records
for these bars.

**Neither of Chan's columns reproduces, and his claim does not hold.** Holding
the parameters the train years chose, the strategy earns a test Sharpe ratio of
5.700 against his 1.947, about three times his figure. The other three figures
overshoot by more: cumulative return about 4.7 times, annual return about 3.8
times and the Calmar ratio about 15.5 times. Re-choosing the parameters each day
beats holding them on the Calmar ratio alone and loses on the other three, so
the claim that it improves every metric fails. At a cost of 1 basis point a
round trip both arms lose money.

**The first run broke a declared reading, and both runs are reported.** On
NYSE's 34 early closes from 2006 to 2020 the session ends at 13:00, and the
first run kept the extended-hours bars from 13:00 to 15:59, against reading 2.
The review of the pull request found it, and the fix implements the reading as
declared rather than changing it. The corrected run gives every figure below.
The first run gave 3.55, 0.6798, 5.791 and 15.676 for the unconditional column,
and 3.48, 0.6710, 5.916 and 16.604 for the conditional, where re-choosing won on
the Sharpe and Calmar ratios. The claim failed in both runs.

Rows 1 to 4 are replications, one per printed figure of the unconditional
column. Row 5 is Chan's claim and takes the claim route
`### Rows that are not replications` describes. Rows 6 to 11 are not
replications. Row 6 sets the conditional column beside Chan's, which the issue
declared could only be reproduced in kind, because it rests on PredictNow's
model. Row 10, and row 6's count of how often the model kept one cell, were
added after the result was seen.

Every row reads the same vintages and specification, so they are stated once
here.

1. **The vintages.** Alpha Vantage's one-minute bars at `adjusted=false`:
   GLD's `gld_intraday_1min.csv.gz`, downloaded 2026-07-17, and GDX's
   `gdx_intraday_1min.csv.gz`, downloaded 2026-10-03. Both are kept in the
   owner's archive and verified against the hashes in
   `data/archive_vintages.jsonl` before they are parsed.
   [data/README.md](../data/README.md) says what each holds and how each was
   checked against the committed daily closes.
2. **The readings.** The book leaves the bar grid, the rule order, the
   annual-return definition, the features' daily form, the model and the
   costs unstated, and its entry grid misprints a value. All 19 readings were
   declared on
   [issue 23](https://github.com/l3a0/quantitative-trading/issues/23#issuecomment-5975426355)
   on 2026-10-04, before any return on the minute bars was computed, and
   `src/chan/cpo.py` cites each by number. In short:

   - the regular session, 09:30 to 15:59 by opening minute, or to 12:59 on an
     early close
   - every day both ETFs traded from GDX's first day, 2006-05-22, to
     2020-12-31, split 80% and 20% by trading days
   - the endnote's recursions run continuously over the minutes
   - exits before entries, flat at each day's open, liquidation at the last close
   - the label is the sum of the day's round trips, at zero cost
   - the unconditional cell maximises the compounded train return
   - pyfolio's definitions for the four metrics

3. **The model and features.** scikit-learn's `HistGradientBoostingRegressor`
   with default hyperparameters and `random_state=0`, on 101 features: the
   three parameters, and seven named indicators on each ETF at seven lookbacks,
   each read at the day's last bar. Six indicators come from `ta`, and the
   Bollinger z-score is computed the way `ta`'s bands are. The book's unnamed
   eighth indicator is left out.

Every result here is **exploratory**. A replication spends its sample on a
hypothesis someone else chose, so the entry says whether Chan's numbers and
claim reproduce on these bars and nothing about whether the method works.

### What the book printed

The setup of Example 7.1 is among the committed highlights in
[research/book-notes](../research/book-notes/README.md), at Kindle locations
3428 to 3517. Its results are not, because the book prints them in a table
beside code and a figure, as `research/book-notes/README.md` records. Those
rows trace to the pages read on 2026-10-03, recorded on
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23).

| # | Row | Published | Where |
| --- | --- | --- | --- |
| 1 | Unconditional cumulative return over the three test years | 73% | p. 145, not among the highlights |
| 2 | Unconditional annual return | 17.29% | p. 145, not among the highlights |
| 3 | Unconditional Sharpe ratio | 1.947 | p. 145, not among the highlights |
| 4 | Unconditional Calmar ratio | 0.984 | p. 145, not among the highlights |
| 5 | Conditional beats unconditional on every metric | "All other metrics are improved using CPO" | p. 145, not among the highlights |
| 6 | The conditional column | 83%, 19.77%, 2.325 and 1.454 | p. 145, not among the highlights |
| 7 | The arithmetic annual return | nothing | n/a |
| 8 | Both arms net of 1 basis point a round trip | nothing, the book mentions no costs | n/a |
| 9 | Round trips a day | nothing beyond multiple round trips a day | Kindle location 3444 |
| 10 | Where 1.947 sits among the 400 cells' test Sharpe ratios | nothing | n/a |
| 11 | The span and the split | 2006-01-01 to 2020-12-31, 80% and 20%, the test the last three years | Kindle location 3444, and p. 145 for the test years |

The book's own figures disagree with each other. 17.29% a year compounds to
61.4% over three years, not 73%, and 19.77% to 71.8%, not 83%, which
`test_chan_s_annual_returns_do_not_compound_to_his_cumulative_ones` holds.
Neither the compounded nor the arithmetic definition of annual return makes
them agree, so rows 1 and 2 cannot both reproduce under either. Read as
arithmetic, 17.29% a year can compound to at most 68.0% over three years and
19.77% to at most 81.0%, which
`test_chan_s_annual_returns_read_as_arithmetic_cannot_reach_them_either` holds.

### What this repo computed

| # | Specification | Computed | Gap | Assertion |
| --- | --- | --- | --- | --- |
| 1 | `∏(1 + r) − 1` over the 736 test days | 3.40 | +2.67 | `TestExample71OnTheArchive::test_rows_1_to_4_the_unconditional_figures_and_their_gaps` |
| 2 | `(1 + cumulative)^(252 / n) − 1` | 0.6612 | +0.4883 | the same |
| 3 | `√252 · mean(r) / std(r)`, sample standard deviation, risk-free rate zero | 5.700 | +3.753 | the same |
| 4 | row 2 over the magnitude of the deepest drawdown of compounded wealth | 15.249 | +14.265 | the same |
| 5 | conditional against unconditional on rows 1 to 4 | better on the Calmar ratio, worse on the Sharpe ratio and both returns | n/a | `TestExample71OnTheArchive::test_row_5_chan_s_claim_does_not_hold` |
| 6 | the conditional arm, specified as rows 1 to 4 | 3.12, 0.6234, 5.274 and 18.637. Added after the result was seen: it keeps the unconditional cell on 557 of the 736 days, uses 44 cells and switches 254 times | n/a | `TestExample71OnTheArchive::test_row_6_the_conditional_figures_beside_chan_s` and the row after it |
| 7 | `252 · mean(r)` | 0.5121 unconditional and 0.4892 conditional | n/a | `TestExample71OnTheArchive::test_row_7_the_arithmetic_annual_returns` |
| 8 | each day's return less 1 basis point per round trip | Sharpe ratios of −7.614 and −6.122, and cumulative returns of −0.858 and −0.814 | n/a | `TestExample71OnTheArchive::test_row_8_one_basis_point_a_round_trip_turns_both_arms_to_losses` |
| 9 | the mean count of round trips on a test day | 46.7 unconditional and 42.1 conditional | n/a | `TestExample71OnTheArchive::test_row_9_round_trips_a_day` |
| 10 | each cell's test Sharpe ratio, all 400. Added after the result was seen | 0.807 to 5.891, median 3.506, the highest at `2.5_30_0.2`. 39 cells sit below 1.947, and the nearest is `3_60_2.5`, at 1.931 and 1.19 round trips a day | n/a | `TestExample71OnTheArchive::test_row_10_where_chan_s_sharpe_sits_among_the_400_cells` |
| 11 | every day both ETFs have a regular-session bar | 3,680 days from 2006-05-22 to 2020-12-31, the test starting 2018-01-31 | n/a | `TestExample71OnTheArchive::test_row_11_the_span_and_the_split` |

A cell is written as Chan's p. 145 output writes it: weight, lookback in
minutes, entry threshold.

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | did not reproduce | 3.40 against 0.73. The selection rule chose `2_30_0.2`, the smallest weight, the shortest lookback and the lowest entry threshold, which trades 46.7 round trips a day on the test days. |
| 2 | did not reproduce | 0.6612 against 0.1729. |
| 3 | did not reproduce | 5.700 against 1.947. |
| 4 | did not reproduce | 15.249 against 0.984. |
| 5 | did not reproduce | The claim needs all four. Re-choosing wins on Calmar, 18.637 against 15.249, and loses on Sharpe, 5.274 against 5.700, on cumulative return, 3.12 against 3.40, and on annual return. |
| 6 | none, not a replication | The issue declared before the run that this column rests on a model this repo cannot have, so its figures are set beside Chan's rather than judged against them. The model keeps the unconditional cell on 557 of the 736 days, so the arms differ less than their names suggest. |
| 7 | none, not a replication | The arithmetic figures are lower than the compounded ones and still about three times Chan's. Neither definition rescues row 2. |
| 8 | none, not a replication | A cost of 1 basis point a round trip, the figure reading 16 declared, turns both arms into heavy losses. |
| 9 | none, not a replication | The two arms trade 46.7 and 42.1 round trips a day. Chan says only that the strategy may make multiple round trips a day. |
| 10 | none, not a replication | Added after the verdicts were seen, because a gap alone does not say where the book's figure would have to come from. Chan's 1.947 sits in the bottom tenth of what these 400 cells earned on the test days, and the nearest cell to it trades about once a day. |
| 11 | none, not a replication | GDX's first trading day is 2006-05-22, so Chan's stated start of January 1, 2006 cannot hold for the pair. The 80% boundary falls on 2018-01-31, which fits Figure 7.1's curves beginning just after the 2018 tick. That reading of the figure is by eye. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Neither column reproduces, and the claim fails.** Selecting the parameters
   that maximise train return at no cost picks `2_30_0.2`, a cell that trades
   about 47 round trips a day, and it earns about three times Chan's Sharpe
   ratio on the test years. Re-choosing daily improves the Calmar ratio and
   nothing else.
2. **A hypothesis for a later run, which nothing here tests: Chan's figures
   carry a cost, or something that acts like one.** At no cost the selection
   landed on a cell trading dozens of times a day, and at 1 basis point a round
   trip that cell loses money. The cell nearest his 1.947 trades about once a
   day. A cost charged during his own optimisation, a fill one bar later, or a
   coarser bar could each move the choice toward cells like that. None was
   declared before the run, so none was tried.
3. **The third-party run overshot the same way.** The reproduction cited on
   the issue, on Kibot bars from 2009, reported a test Sharpe ratio of 5.974
   for its unconditional arm at 50.1 round trips a day. Both runs land on a
   high-turnover cell and overshoot Chan's Sharpe ratio about threefold. They
   differ on where 1.947 sits. They placed it near their minimum of 1.931,
   while here 39 cells sit below it and the minimum is 0.807.

### What this entry cannot say

Four things.

**Whether conditional parameter optimization works.** The model here is not
PredictNow's, its features lack the book's unnamed eighth indicator, and the
features are read at the day's last bar rather than summarised over it. `ta`'s
ATR and ADX also return 0 rather than nothing before their window fills, so the
earliest rows carry zeros the model cannot tell from readings. A better model
could win where this one did not. The test is of Chan's printed claim on this
strategy, not of the method.

**What would reproduce Chan's numbers.** Row 10 places his Sharpe ratio among
cells that trade far less, and the cost row shows the chosen cell losing once
trading costs something. A search over costs and fill delays until one matched
would be the search the honesty rail forbids, so it was not run.

**Whether the strategy pays.** At 1 basis point a round trip both arms lose
heavily. What a round trip in GLD actually costs is not measured here.

**Anything a public clone can check.** The bars are licensed, so the pins run
only where the owner's archive is. The hashes say exactly which bytes were
read, and nothing here can show them to anyone else.

Four more pins in `TestExample71OnTheArchive` hold figures that post quotes
and the tables above do not, so they are named here.

1. `test_rows_1_to_4_as_multiples_of_chan_s_figures`, the multiples above.
2. `test_each_arm_earns_less_a_round_trip_than_a_round_trip_costs`, a gross
   0.435 and 0.462 basis points a round trip against a cost of 1.
3. `test_the_chosen_cell_is_the_second_busiest_of_the_400`, with only
   `2.5_30_0.2` trading more.
4. `test_turnover_and_sharpe_ratio_rise_together_across_the_400_cells`,
   Spearman's rank correlation of 0.95.

The last three were added after the result was seen and decide nothing.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/conditional-parameter-optimization-lessons.md](../blog/conditional-parameter-optimization-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which draws row 10 and redraws only where the archive is, with
`QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.cpo_figures`.

## Entry 17: cross-sectional momentum, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 6.2, Kindle locations 2797, 2800 and 2890,
and the script `kentdaniel.m` the example names. Shipped under
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297), whose
body declared the four readings below, and the rule deciding whether one
lands, before any of them was computed.

Eleven rows, all derivable from
[tests/test_cross_sectional_momentum.py](../tests/test_cross_sectional_momentum.py),
and a table of the readings.

**The script's figures sit near the book's and far from its own comment's.** Stocks
that rose most over the past year tend to keep rising, so Chan buys the 50
with the highest 252-day return and shorts the 50 with the lowest, holds each
day's picks 25 days in overlapping cohorts, and divides each day's return by
2 · 50 · 25. The book reports 37 percent and a Sharpe ratio of 4.1 from
2007-05-15 to 2007-12-31, and −30 percent over 2008 and 2009. The comment
lines that close `kentdaniel.m` print 0.0315 and 0.40 over the same 2007
window, which is where
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297) started.
Transcribed and run on the file it loads, the script gives none of the five
figures its comment prints. It gives a Sharpe ratio of 4.0657, and a
compounded APR of 0.372577 in 2007 and −0.298789 over 2008 and 2009, which
round to the book's 4.1, 37 percent and −30 percent. A second implementation
written separately in pandas agrees with the transcription on every day, which
`TestASecondImplementation` holds. It shares the transcription's reading of
the script, a one-row `lag` among it, so it rules out a slip in the numpy code
and not a misreading of the MATLAB. The comment would have confirmed that
reading, and it did not.

**Under the rule declared in advance, no book figure reproduces.** The
issue set the book's "APR" against the arithmetic return, because Entry 12
found that Example 7.2's "APR" is the arithmetic figure. Here the arithmetic
return is 0.319989 in 2007 and −0.323195 over 2008 and 2009, which round to 32
and −32 percent. The rule needed 37 percent and 4.1 together, so none of the
four readings lands and the 4.1 row does not reproduce either, though the
script's own Sharpe ratio rounds to it. That the compounded figure is the one
matching was seen only after the rule was fixed, so row 10 reports it and it
decides nothing. Chan's word "APR" names the arithmetic figure in Example 7.2
and the compounded one here, and a rule taken from one example did not carry
to the next.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read for
   the close through `chan.series.load_panel`.
   [data/README.md](../data/README.md) records where it came from. **Every
   figure here is about survivors**, because the file is the S&P 500 as Chan
   held it on 2012-04-24, carried backwards, and none of its 497 stocks stops
   before that day. That reaches the two legs in opposite directions. The
   short leg lacks stocks that fell and then left the index, which pushes the
   strategy down, and the long leg lacks past winners that later collapsed
   out of it, which pushes it up. Which dominates is not measured here, as
   Entry 14 found for its own panel.
2. **The specification.** `kentdaniel.m` at `45670240` in
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading),
   with `lag` read as a one-row shift, since neither mirror ships a `lag.m`.
   A 252-row ranking return, the 50 highest long and the 50 lowest short on
   every row from the 253rd, each row's picks held 25 rows, each day's summed
   return over 2 · 50 · 25. Book two's `smartstd`, which divides by n, and its
   `calculateMaxDD`. Every annualisation uses 252 days, the Sharpe ratio
   subtracts no risk-free rate, and no cost is charged. The 2007 window opens
   the day after the first picks, so its first 24 days hold fewer than 25
   cohorts while the script divides by 25.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2007 to 2012 sample on a rule he chose, and a reading tried against his number
is an explanation found by a search, so the entry says whether his numbers
reproduce on his file and nothing about whether momentum pays today.

### What the book printed

`kentdaniel.m` prints five figures for the 2007 window in the comment lines
that close it. The book quotes two figures for that window, one for 2008 and
2009, and a claim about the years after.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Arithmetic annual return, 2007 | 0.0315 | `kentdaniel.m` |
| 2 | Sharpe ratio, 2007 | 0.40 | `kentdaniel.m` |
| 3 | Compounded APR, 2007 | 0.0288 | `kentdaniel.m` |
| 4 | Maximum drawdown, 2007 | −0.066923 | `kentdaniel.m` |
| 5 | Maximum drawdown duration, 2007 | 182 days | `kentdaniel.m` |
| 6 | "APR", 2007-05-15 to 2007-12-31 | 37 percent | location 2800 |
| 7 | Sharpe ratio, the same window | 4.1 | location 2800 |
| 8 | "APR", 2008-01-02 to 2009-12-31 | −30 percent | location 2800 |
| 9 | After 2009 the return "did stabilize, though it hasn't returned to its former high level yet" | a claim, no figure | location 2800 |
| 10 and 11 | rows 6 and 8 on the compounded APR, and row 7 under the first edition's `smartstd` | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · smartmean(ret)` over the 160 days of 2007 | 0.319989 | `TestTheScript::test_the_arithmetic_annual_return` |
| 2 | `√252 · smartmean(ret) / smartstd(ret)`, book two's `smartstd` | 4.0657 | `TestTheScript::test_the_sharpe_ratio` |
| 3 | `prod(1 + ret)^(252/160) − 1` | 0.372577 | `TestTheScript::test_the_compounded_apr` |
| 4 | `calculateMaxDD` on `cumprod(1 + ret) − 1` | −0.033870 | `TestTheScript::test_the_maximum_drawdown_and_its_duration` |
| 5 | the same | 23 days | the same |
| 6 | row 1 in whole percent, under the declared rule | 32 | `TestTheBook::test_the_arithmetic_return_misses_37_percent_on_every_reading` |
| 7 | row 2 at one decimal, which the declared rule needed together with row 6 | 4.1 | `TestTheBook::test_two_readings_land_4_1_alone` and `::test_no_reading_lands_37_percent_and_4_1` |
| 8 | `252 · smartmean(ret)` over the 505 days of 2008 and 2009, in whole percent | −0.323195, so −32 | `TestTheScriptOverTheOtherWindows::test_2008_and_2009` and `TestTheBook::test_the_script_misses_minus_30_percent_on_the_arithmetic_return` |
| 9 | 2010-01-04 to 2012-04-24's arithmetic return at least 0 and below row 1 | 0.016244, so it holds | `TestTheBook::test_the_return_after_2009_stabilised_below_2007` |
| 10 | the compounded APR of 2007 and of 2008 and 2009, in whole percent | 0.372577 and −0.298789, so 37 and −30 | `TestTheBook::test_the_compounded_aprs_round_to_both_of_the_books` |
| 11 | row 2 with the first edition's `smartstd`, which divides by n − 1 | 4.0530 | `TestTheHelperMovesADigit::test_the_first_editions_helper_prints_4_05_rather_than_4_07` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.2885 | did not reproduce | The script, on the file it loads by name, does not print its own comment. The vintage explanation is spent, and nothing found says which run printed 0.0315. |
| 2 | +3.67 | did not reproduce | The same. The comment's 0.40 is a tenth of what the code computes. |
| 3 | +0.3438 | did not reproduce | The same. |
| 4 | +0.033053 | did not reproduce | The same. |
| 5 | −159 | did not reproduce | The same. |
| 6 | −5 | did not reproduce | The declared rule reads the book's "APR" as the arithmetic return, and no reading's rounds to 37. |
| 7 | −0.0 | did not reproduce | The declared rule needed 37 percent and 4.1 from one reading together. The script's 4.0657, 0.0343 below the book, rounds to 4.1 alone, which the rule calls a partial landing rather than a landing. |
| 8 | −2 | did not reproduce | The declared rule again. The arithmetic return rounds to −32 percent. |
| 9 | none | reproduced | The claim holds on the script as printed. The rule was fixed before the number was seen. |
| 10 | none | none, not a replication | Seen after the rule was fixed. Both of the book's APRs are the script's compounded figure at the book's precision, and that decides no verdict. |
| 11 | none | none, not a replication | The first edition's helper prints 4.05 against book two's 4.07, so a port reaching for the helper the repo held first fails a test. Both round to the book's 4.1. |

### The declared readings

[Issue 297](https://github.com/l3a0/quantitative-trading/issues/297) declared
R1 to R4 as what could explain a script printing 0.40 against a book printing
4.1, each changing one thing from the script, and no combination was run. Each
cell is the arithmetic annual return and then the Sharpe ratio, from
`TestTheReadings` and `TestTheScriptOverTheOtherWindows`. A reading lands when
its 2007 return rounds to 37 percent and its 2007 Sharpe ratio to 4.1. The
last column is each 2007 figure less the book's, from `TestTheDistances`, which
also holds each reading's distance from −30 percent.

| Reading | What changes | 2007 | 2008 and 2009 | 2010 to 2012 | Lands | From 37 percent and 4.1 |
| --- | --- | --- | --- | --- | --- | --- |
| R0 | nothing, the script as printed | 0.3200, 4.0657 | −0.3232, −1.2930 | 0.0162, 0.2004 | no, 4.1 alone | −0.0500, −0.0343 |
| R1 | one portfolio held at a time, re-formed every 25 days | 0.3222, 3.9138 | −0.3130, −1.2586 | 0.0104, 0.1277 | no | −0.0478, −0.1862 |
| R2 | the ranking return ends 21 days back | 0.2893, 3.8232 | −0.3053, −1.2821 | 0.0176, 0.2262 | no | −0.0807, −0.2768 |
| R3 | a day's picks earn that same day, which looks ahead | 0.3371, 4.2779 | −0.2923, −1.1695 | 0.0332, 0.4093 | no | −0.0329, +0.1779 |
| R4 | each day over the cohorts it holds rather than 25 | 0.3215, 4.0531 | R0's | R0's | no, 4.1 alone | −0.0485, −0.0469 |

The readings were declared to explain a script printing 0.40 against a book
printing 4.1. The code's own Sharpe ratio is 4.0657, and their 2007 Sharpe
ratios span 3.82 to 4.28 around it. Long losers and
short winners was declared too, and negating every position negates every
day's return exactly, which `TestTheReadings::test_the_opposite_sign_negates_every_day`
holds.

### What the entry concludes

Three things.

1. **The 0.40 is the comment's, not the code's.** `kentdaniel.m` as
   transcribed, on the file it loads, gives a Sharpe ratio that rounds to the
   book's, and compounded APRs that round to both of the book's APRs. The 0.40
   in its closing comment is a tenth of what the code computes, and no reading
   was added to find the run that printed it. The one assumption the
   transcription makes, that `lag` is a one-row shift, is the one the comment
   would have confirmed.
2. **A rule taken from one example did not carry to the next.** Example 7.2's
   "APR" is the arithmetic return. The figures seen afterwards point to the
   compounded one in Example 6.2, in one book by one author. The rule declared
   in advance followed the first example, so the verdicts on rows 6 to 8 say
   what that rule gives, and row 10 says what was seen afterwards.
3. **Seen after the run and deciding nothing, the crash Chan describes is in
   the file.** The strategy that earned a Sharpe ratio of 4.07 over 2007
   lost 32 percent a year over 2008 and 2009, with a drawdown of −0.606634
   from a high on 2008-07-14. It was still below that high 371 days later,
   when the window ended, so the drawdown had not finished. The strategy
   earned 1.6 percent a year from 2010 to 2012. That is the collapse location
   2890 describes, where momentum "vanished during the aftermath of the stock
   market crash".

### What this entry cannot say

Four things.

**Which run printed the comment.** A different file, window or version of the
script could each print 0.0315, and trying them until one did would be the
search the issue's rule forbids, so none was tried.

**What survivorship does to these figures.** Every stock here survived to
2012-04-24, and the two legs lose different stocks.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) waits on
a panel that could measure what that costs a cross-sectional rule.

**What costs would take.** `kentdaniel.m` charges none, and every day one
cohort of 100 picks enters and the one formed 25 days earlier leaves.

**Whether momentum pays today.** The sample ends in April 2012.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/cross-sectional-momentum-lessons.md](../blog/cross-sectional-momentum-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.cross_sectional_momentum_figures`
redraws.

## Entry 18: buy on gap and its mirror, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 4.1, Kindle locations 1948 to 1993 and 3509,
and the script `bog.m` the example names. Shipped under
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295). The
location numbers are that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Twelve rows, all derivable from
[tests/test_buy_on_gap.py](../tests/test_buy_on_gap.py).

**Both figures `bog.m` prints reproduce on Chan's own file, and the mirror
does not.** Chan argues that a stock's open can overshoot on a morning of panic
selling and drift back during the day. So each day the rule buys at the open
the ten stocks that opened furthest below their previous day's low, by more
than one 90-day standard deviation of their daily returns, provided the open is
still above the 20-day moving average of closes, and sells them at the close.
The book reports an APR of 8.7 percent and a Sharpe ratio of 1.5, and the
transcription in `chan.buy_on_gap` lands on both at the precision printed.
Chan also reports the mirror image, shorting stocks that open a standard
deviation above the previous day while below their moving average, at 46
percent and 1.27. He prints no script for it, and the rule [issue 295](https://github.com/l3a0/quantitative-trading/issues/295) declared
before any run lands at 12 percent and 1.79.

One choice decides both printed figures. `bog.m`'s moving deviation calls book
two's `smartstd`, which skips a missing return and divides by n. With the first
edition's, which counts it as zero and divides by n − 1, the APR rounds to 8.4
percent and the Sharpe ratio to 1.7, and row 10 holds that. It is Entry 12's
lesson again, on two figures rather than one digit.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read for
   the open, high, low and close through `chan.series.load_panel`, all 1,500
   days from 2006-05-11 to 2012-04-24. `bog.m` loads
   `inputDataOHLCDaily_20120424`, with no `_stocks`, and the only file of that
   name in either public mirror of Chan's code is the same bytes, which
   [data/README.md](../data/README.md) records. **Every figure here is about
   survivors**, because the file is the S&P 500 as Chan held it on 2012-04-24,
   carried backwards, and location 1974 says so.
2. **The specification.** `bog.m` at `45670240` in
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading).
   The spread is book two's `smartMovingStd` over 90 rows of close-to-close
   returns and the average is `smartMovingAvg` over 20 rows of closes, both
   moved one row later. Entry is one spread below the previous low, at most ten
   positions a day, and each day's sum is divided by 10 whatever the day's
   count. The APR is compounded over all 1,500 days at 252 a year, and the
   Sharpe ratio uses MATLAB's n − 1 `std` and subtracts no risk-free rate. No
   cost is charged. The mirror measures its jump from the previous day's high,
   requires the open below the average, and shorts the ten largest jumps, as
   [issue 295](https://github.com/l3a0/quantitative-trading/issues/295) declared.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 to 2012 sample on a rule he chose, so the entry says whether his numbers
reproduce on his file and nothing about whether the rule pays today. The
mirror's rule was declared before its numbers were seen, but it is a reading of
one sentence rather than a hypothesis tested on held-out data.

### What the book printed

`bog.m` closes on the comment `% APR=8.7%, Sharpe=1.5`. Its `fprintf` lines
would print more digits, but nothing records what they printed, so the
comment's one decimal is the precision the source carries.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The window `bog.m` prints | `20060511 - 20120424` | `bog.m`, location 1974 |
| 2 | Buy on gap, APR | 8.7 percent | `bog.m`, location 1974 |
| 3 | Buy on gap, Sharpe ratio | 1.5 | `bog.m`, location 1974 |
| 4 | Location 3509's figure, read as the arithmetic annual return | "around 8.7 percent", an "annualized average return" | location 3509 |
| 5 | Short on gap, APR | 46 percent | location 1993 |
| 6 | Short on gap, Sharpe ratio | 1.27 | location 1993 |
| 7 | Short on gap has the steeper drawdown | a claim | location 1993 |
| 8 to 12 | the qualifiers and positions, the first positions, the other `smartstd`, the late listings and the flagged days | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | the first and last of the panel's days | `20060511 - 20120424` | `TestTheVintages::test_the_window_is_the_one_bog_m_prints` |
| 2 | `prod(1 + ret)^(252/1500) − 1` | 0.087385 | `TestTheFigures::test_the_apr_is_chans_8_7_percent` |
| 3 | `√252 · mean(ret) / std(ret)` | 1.5371 | `TestTheFigures::test_the_sharpe_ratio_is_chans_1_5` |
| 4 | `252 · mean(ret)` | 0.085279 | `TestTheFigures::test_the_arithmetic_return_does_not_reach_location_3509s_8_7` |
| 5 | row 2 under the declared mirror | 0.122030 | `TestTheMirror::test_the_apr_lands_far_from_46_percent` |
| 6 | row 3 under the declared mirror | 1.7853 | `TestTheMirror::test_the_sharpe_ratio_lands_above_1_27` |
| 7 | `calculateMaxDD` on each side's `cumprod(1 + ret) − 1` | −0.064928 short against −0.052459 long | `TestTheMirror::test_its_drawdown_is_the_steeper_as_location_1993_says` |
| 8 | qualifiers, positions and days holding one, buy side then mirror | 972, 695 and 391, then 1,308, 725 and 338, at most 10 on a day | `TestTheFigures::test_the_comparison_as_written_selects_what_the_algebra_does`, `::test_the_positions_and_the_busiest_day` and `TestTheMirror::test_the_arithmetic_return_and_the_positions` |
| 9 | the first position on each side | 2006-09-22 and 2006-09-25, after the spread first exists on 2006-09-19 | `TestTheFigures::test_nothing_is_held_before_the_spread_exists` |
| 10 | rows 2 and 3, and 5 and 6, with the first edition's `smartstd` in the spread | 0.083629 and 1.6503, then 0.116340 and 1.7234 | `TestTheHelperMovesBothFigures` |
| 11 | positions resting on fewer than 90 returns after 2006-09-19 | 3: CFN and MPC long, DPS short, none on a spread of 0 | `TestTheLateListings::test_three_positions_rest_on_fewer_than_90_returns` |
| 12 | positions on one of the 30 days the scale-break guard flags | 1, MS short on 2008-10-13 | `TestTheScaleBreakDecision::test_one_position_falls_on_a_flagged_day` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, exact | reproduced | The panel's span is the window `bog.m` prints. |
| 2 | 0.0 | reproduced | Chan's figure, on his own file, through his own script transcribed. |
| 3 | 0.0 | reproduced | The same as row 2. |
| 4 | −0.2 | did not reproduce | Read as the arithmetic return, as Example 7.2's "annualized average return" was, the figure is 8.5 percent at the book's precision. What fails is that reading rather than Chan's number: location 3509's 8.7 is row 2's compounded APR, which reproduces. |
| 5 | −34 | did not reproduce | Under the rule [issue 295](https://github.com/l3a0/quantitative-trading/issues/295) declared. The reading is part of the method, so it cannot explain a miss from outside it, and no second reading was tried. |
| 6 | +0.52 | did not reproduce | The same as row 5. |
| 7 | none, a claim | reproduced | The short side's deepest drawdown is the more negative, the criterion [issue 295](https://github.com/l3a0/quantitative-trading/issues/295) fixed before any run. Its longest stretch below a high is 363 days against 159. |
| 8 | none | none, not a replication | Comparing each open against `bog.m`'s `buyPrice`, as the script writes it, selects exactly what comparing the drop against the spread does. No two qualifiers on one day tie, so MATLAB's tie order moves nothing either. Ten days fill all ten buy positions. |
| 9 | none | none, not a replication | No position can come before 2006-09-19, the first day a 90-row spread exists. |
| 10 | none | none, not a replication | The first edition's helper moves both printed figures off Chan's, to 8.4 percent and 1.7, and takes two buy positions fewer. |
| 11 | none | none, not a replication | A stock listed inside the window reaches the rule before 90 returns stand behind its spread, which is what Chan's helper does. Of the 23 late listings, three positions come from it. |
| 12 | none | none, not a replication | The guard is not called, so this counts what it would have refused. The issue decided not to call it on the reasoning [issue 18](https://github.com/l3a0/quantitative-trading/issues/18), [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) and [issue 22](https://github.com/l3a0/quantitative-trading/issues/22) give. |

### What the entry concludes

Three things.

1. **Example 4.1 reproduces exactly on Chan's own file.** Both figures `bog.m`
   prints land at the precision printed, and only with book two's `smartstd`
   inside the spread.
2. **One phrase names two formulas in this book.** In Example 7.2, "annualized
   average return" is the arithmetic figure. At location 3509 the same phrase
   carries Example 4.1's compounded APR, which the arithmetic figure misses.
   Reading the label instead of the script would have pinned row 2 against
   the arithmetic figure and called it a miss. Entry 17 found the same of the
   word "APR", which names the arithmetic figure in Example 7.2 and the
   compounded one in Example 6.2.
3. **The declared mirror is a different strategy from Chan's.** Its drawdown
   is steeper, as he says, and its return is not. His own pair of figures
   rules out the declared rule's scale on arithmetic alone, if he computed
   them with `bog.m`'s formulas and no risk-free rate. Because ln(1 + r) ≤ r
   every day, an APR of 46 percent and a Sharpe ratio of 1.27 need an annual
   volatility of at least ln(1.46) / 1.27 = 0.2980, and the declared rule's
   is 0.0657, about four and a half times less, held by
   `TestTheMirror::test_chans_two_figures_need_four_and_a_half_times_this_volatility`.
   The declared rule holds a position on 338 of 1,500 days and ten at once on
   16 of them. The floor says nothing about whether the difference lies in
   which stocks Chan's rule chose, how many days it traded, or how it sized
   each position, and nothing here tests them.

### What this entry cannot say

Five things.

**Which rule Chan ran for the mirror.** Two other readings of location 1993
were named on [issue 295](https://github.com/l3a0/quantitative-trading/issues/295) and not run. Trying readings until one matched would be the
search the honesty rail forbids.

**Which file Chan ran in 2012.** The name `bog.m` loads points, in both
public mirrors, at the same bytes as the committed panel's source. That says
what the name means in the code he published, not that the file he ran when
he wrote the book was this one. Both figures reproducing is consistent with
it and does not prove it.

**What costs and execution would take.** `bog.m` charges none. Location 1993
names the short-sale constraint the mirror suffers from, and location 1988
names the signal noise of deciding on the official open, which cannot be known
before the trade at that open.

**What the rule earned on the index as it stood each day.** Every stock here
was in the S&P 500 on 2012-04-24. The point-in-time panel
[issue 252](https://github.com/l3a0/quantitative-trading/issues/252) waits on
would answer it for this rule too.

**Whether MS's flagged day was a clean print.** The guard flags the move from
2008-10-10 to 2008-10-13 as too large for a price change, and the mirror shorted
MS that day. Nothing here checks the print against another source.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/buy-on-gap-lessons.md](../blog/buy-on-gap-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.buy_on_gap_figures` redraws.

## Entry 19: the Khandani-Lo reversal on the 2012 panel, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Examples 4.3 and 4.4, Kindle locations 2087 to 2135
and 2890, and the script `andrewlo_2007_2012.m` the examples name. Shipped
under [issue 296](https://github.com/l3a0/quantitative-trading/issues/296).
Every example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md),
apart from Examples 3.7 and 3.8, which are *Quantitative Trading*'s.

Eleven rows, all derivable from
[tests/test_khandani_lo_book_two.py](../tests/test_khandani_lo_book_two.py).

**Every figure Chan prints reproduces on his own file.** The rule is the one
Entries 8 and 10 run: weight every stock by minus its return against the
equal-weighted market, so the rule buys what fell most against its peers and
shorts what rose most. Example 4.3 holds the weights from one close to the
next. Example 4.4 takes its signal from the gap between yesterday's close and
today's open, enters at the open and exits at the same day's close. The book
reports an APR of 13.7 percent and a Sharpe ratio of 1.3 for the first, with
30 percent in 2008 and 11 percent in 2011, and 73 percent and 4.7 for the
second. The transcription in `chan.khandani_lo_book_two` lands on all six, and
on the two figures the script printed for Example 4.4 at six decimals.

The owner's rule of 2026-10-04, recorded on
[issue 296](https://github.com/l3a0/quantitative-trading/issues/296), is that a
run on different data or over a different window is a new run rather than a
duplicate. This entry runs on a different file over a different window from
Entries 8 and 10, and its rule differs from Entry 8's in five ways, so none of
its rows is a check on theirs.

1. **The weights are scaled to a gross of 1 each day**, where Entry 8's
   divide by the count of stocks priced.
2. **A missing price leaves its weight missing**, where Entry 8's sets it to 0.
3. **No cost is charged.** The script's cost lines are commented out.
4. **The window is cut before any return is taken**, so the first days earn
   nothing, where Entry 8's takes returns on the whole file and cuts the
   profit afterwards.
5. **The Sharpe ratio takes MATLAB's own mean and standard deviation**, where
   Entry 8's pairs `smartmean` with the first edition's `smartstd`. The two
   agree on a series with no missing day, which every series here is, so this
   difference moves no figure in this entry.

Entry 10's rule A, Chan's Python notebook, already scales to a gross of 1 and
skips a missing return the same way. Without its forward-fill, its profit
before costs differs from this rule's only on the days the cut zeroes, which
row 11 measures.

Rows 9 to 11 separate the data and the window from the rule, and on 2006 the
cut from the weighting.

Every row reads the same vintage and specification, so both are stated once
here. Rows 9 to 11 are the exception. Rows 9 and 11 read the first book's file,
rows 10 and 11 run a rule other than this one, and each row says which.

1. **The vintage.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read
   for the open and the close through `chan.series.load_panel`. The script
   loads `inputDataOHLCDaily_20120424`, without `_stocks`, and
   [data/README.md](../data/README.md) records that the copy under that name
   is the same bytes. **Every figure here is about survivors**, because the
   panel is the S&P 500 as Chan held it on 2012-04-24, carried backwards.
2. **The specification.** `andrewlo_2007_2012.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   identical to the copy at `4567024` in
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading).
   Both price frames are cut to 2007-01-03 through 2011-12-30, 1,260 trading
   days, before any return is taken. The book's January 2, 2007 was a market
   holiday. The APR is `prod(1 + r)^(252 / n) − 1` and the Sharpe ratio is
   `√252 · mean / std` over all 1,260 days, zeros included, with the deviation
   over n − 1 and no risk-free rate. No cost is charged.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2007 to 2011 sample on a rule somebody else chose, so the entry says whether
his numbers reproduce on his file and nothing about whether the rule pays
today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Example 4.3's APR, close to close | 13.7 percent | location 2110, and the script's comment `APR=13.7%` |
| 2 | Example 4.3's Sharpe ratio | 1.3 | location 2110, and the script's comment |
| 3 | Example 4.3's APR in 2008 | 30 percent | location 2110 |
| 4 | Example 4.3's APR in 2011 | 11 percent | location 2110 |
| 5 | Example 4.4's APR, open to close | 73 percent | location 2135 |
| 6 | Example 4.4's Sharpe ratio | 4.7 | locations 2135 and 2890 |
| 7 | Example 4.4's APR as the script printed it | 0.731553 | `andrewlo_2007_2012.m` |
| 8 | Example 4.4's Sharpe ratio as the script printed it | 4.713284 | `andrewlo_2007_2012.m` |
| 9 to 11 | the two books' rules on each other's data | none, the book prints no such figures | n/a |

### What this repo computed

The assertions are in `tests/test_khandani_lo_book_two.py`. Rows 1 to 8 are
the cases of `TestTheFigures::test_each_figure_reproduces` named by the
figure, and each is held at six decimals and again at the precision printed.

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | Example 4.3, `prod(1 + r)^(252/1260) − 1`, in percent | 13.677582 | `4.3 APR percent` |
| 2 | Example 4.3, `√252 · mean / std` | 1.259478 | `4.3 Sharpe` |
| 3 | row 1's APR line on the 253 days of 2008 in Example 4.3's series | 30.164676 | `4.3 APR percent in 2008` |
| 4 | the same on the 252 days of 2011 | 10.577823 | `4.3 APR percent in 2011` |
| 5 | Example 4.4, `prod(1 + r)^(252/1260) − 1`, in percent | 73.155250 | `4.4 APR percent` |
| 6 | Example 4.4, `√252 · mean / std` | 4.713284 | `4.4 Sharpe` |
| 7 | row 5 as a fraction | 0.731553 | `4.4 APR` |
| 8 | row 6 | 4.713284 | `4.4 Sharpe as printed` |
| 9 | Example 4.3's rule on `spx_20071123/`'s closes over 2006, Entry 8's file and window, cut first | 0.5484 | `TestBesideTheFirstBook::test_book_twos_rule_on_the_first_books_file_and_year` |
| 10 | Entry 8's rule, `chan.khandani_lo.reversal`, on this panel's closes over this window, before costs and after 5 basis points a side with the first day charged | 1.2219 and 0.3797 | `TestBesideTheFirstBook::test_the_first_books_rule_on_this_panel_and_window` |
| 11 | row 9 with returns taken before the cut, so 2006-01-03 and 2006-01-04 earn | 0.4170 | `TestBesideTheFirstBook::test_on_one_year_the_two_days_the_cut_zeroes_move_the_figure_by_a_third` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0 | reproduced | Chan's figure, on his own file, through his own script transcribed. |
| 2 | −0.0 | reproduced | The same. 1.2595 sits 0.0095 above the 1.25 where it would round down, so the book's 1.3 has less room than it reads as having. `TestTheFigures::test_two_book_figures_sit_close_to_their_rounding_points` holds the distance. |
| 3 | 0 | reproduced | The script prints no yearly figure, so the specification applies its APR line to one year of the full run. Rerunning the year on its own would zero its first two days, and `TestTheFigures::test_a_year_rerun_on_its_own_would_be_a_different_figure` holds that it moves the figure. |
| 4 | −0 | reproduced | The same. 10.58 sits 0.08 above the 10.5 where it would round down, held by the same test as row 2's. |
| 5 | 0 | reproduced | The same as row 1. |
| 6 | 0.0 | reproduced | The same. |
| 7 | −0.000000 | reproduced | The same, at every decimal the script printed. The full value is 0.7315525016, which is 1.6 × 10⁻⁹ above the point where the sixth decimal would round down, held by `TestTheFigures::test_the_printed_apr_sits_just_above_its_rounding_point`. |
| 8 | 0.000000 | reproduced | The same. |
| 9 | none | none, not a replication | Against Entry 8's 0.2510 on the same file and days. Book two's rule earns more on the first book's year, before any cost on either side. |
| 10 | none | none, not a replication | Before costs it lands near row 2's 1.2595. Five basis points a side take it to 0.3797. |
| 11 | none | none, not a replication | Entry 10's row 12 is this rule taking returns before the cut, 0.4179 with the deviation over n. The series differ only on 2006's first two days, which lost 0.48 and 0.14 percent there and earn nothing in row 9. |

### Beside Entries 8 and 10

The two books' runs of one rule, each on its own file and window, with rows 9
to 11 between them. Every figure is a Sharpe ratio, and none of the rows is a
check on another.

| Run | File and window | Weights | Cost | Sharpe ratio | Figure |
| --- | --- | --- | --- | --- | --- |
| Entry 8, Example 3.7 | `spx_20071123/` closes, 2006, 251 days | divided by the stocks priced, a missing price weighted 0 | none, then 5 basis points a side | `smartmean` over the first edition's `smartstd` | 0.2510, then −3.1884 |
| Entry 10, Example 3.8, rule B | the same file's opens, the same days | as Entry 8 | as Entry 8 | as Entry 8 | 4.4202, then 0.7834 |
| Entry 10, Example 3.8, rule A | the same opens, forward-filled | a gross of 1 | as Entry 8 | `np.mean` over `np.std`, over n | 2.3818, then 1.3997 |
| Row 11 | Entry 8's closes and days, returns taken before the cut | a gross of 1 | none | MATLAB `mean` over `std`, n − 1 | 0.4170 |
| Row 9 | the same, cut first | a gross of 1 | none | the same | 0.5484 |
| Row 10 | this panel's closes, 2007 to 2011, 1,260 days | as Entry 8 | none, then 5 basis points a side | as Entry 8 | 1.2219, then 0.3797 |
| Example 4.3, rows 1 and 2 | this panel's closes, the same days, cut first | a gross of 1 | none | MATLAB `mean` over `std`, n − 1 | 1.2595 |
| Example 4.4, rows 5 and 6 | this panel's opens and closes, the same days | a gross of 1, on the overnight gap | none | the same | 4.7133 |

Rows 9 to 11 are pinned in `tests/test_khandani_lo_book_two.py`, and the other
figures from Entries 8 and 10 in `tests/test_khandani_lo.py`.

### What the entry concludes

Three things.

1. **Examples 4.3 and 4.4 reproduce on Chan's own file.** All six figures
   the book prints land at its precision, and Example 4.4's two lands at the
   six decimals the script printed.
2. **The distance from the first book's 0.25 to this book's 1.3 is mostly
   the data and the window rather than the rule.** Entry 8's rule on this
   panel earns 1.2219 before costs, near book two's 1.2595 on the same days
   (row 10). Taking the rule first gives the same answer: on the first book's
   year it moves 0.2510 to 0.5484 (row 9), less than the rest of the way to
   1.2595. Of that 0.2974, the two days the cut zeroes carry 0.1313, 0.44
   of it (row 11), because a window of 251 days lets two days move a Sharpe
   ratio by a third. Both differences come from the unrounded figures,
   which `TestBesideTheFirstBook::test_the_differences_the_post_quotes_round_from_the_unrounded_figures`
   holds. The data include a longer survivor horizon, since this
   panel carries 2012-04-24's membership back to 2007, five years, where
   Entry 8's file carries 2007-11-23's back to 2006, under two, and nothing
   here prices what that adds.
3. **Entry 8's lesson survives the move to the 2012 panel.** Charged 5 basis
   points a side, the first book's rule falls from 1.2219 to 0.3797 over 2007
   to 2011 (row 10). Chan prints both of this book's figures before costs.

Location 2110 calls the strategy "almost perfectly dollar neutral". With the
weights scaled to a gross of 1, they sum to zero exactly every day, up to
rounding, and `TestTheWeights::test_the_weights_sum_to_zero_every_day` holds
it.

### What this entry cannot say

Five things.

**What the rule earned on the index as it stood each day.** Every stock here
was in the S&P 500 on 2012-04-24.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) prices
survivorship on this file for Example 7.2 over 2011 and 2012, and nothing yet
prices it for this rule over 2007 to 2011.

**Whether 2008 to 2011 is out of sample in Chan's sense.** He calls it "a
true out-of-sample test, as the strategy was published in 2007". It is out of
sample in time, but the stocks were chosen with 2012's membership, so the
entry repeats his sentence and gives it no verdict.

**What costs would take from Example 4.4.** It trades twice a day, which Chan
says doubles the cost at location 2135, and nothing here charges one. Row 10
charges the first book's rule, which trades once a day.

**Whether the open is tradeable on its own signal.** Example 4.4 sets its
weights from today's open and enters at that same open. Chan names the noise
that brings at location 2135, and nothing here measures it.

**Whether the rule pays today.** The window ends in 2011.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/khandani-lo-reversal-lessons.md](../blog/khandani-lo-reversal-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.khandani_lo_book_two_figures` redraws.

## Entry 20: constant leverage and capped Kelly allocation, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Examples 8.1 and 8.2, Kindle locations 3216 and 3287,
introduced at 3210 and 3268. Shipped under
[issue 298](https://github.com/l3a0/quantitative-trading/issues/298). Neither
example has a script in Chan's public code mirrors, which hold only
`monteCarloOptimLeverage.m` for Chapter 8, so the printed prose is the whole
source.

Thirteen rows, all derivable from
[tests/test_kelly_allocation.py](../tests/test_kelly_allocation.py). Three
carry no published figure and say so in their own cells. Row 11 is the growth
rate at the uncapped Kelly leverages, which Equation 8.3 gives as an image the
highlights did not capture. Rows 12 and 13 are what the arithmetic shows about
Chan's claim, and the book prints neither.

**Example 8.1** holds a leverage of 5 on \$100K of equity through a \$10K loss
and then a \$20K gain, resizing after each. Keeping the leverage constant means
selling into the loss and buying into the gain.
[src/chan/kelly_allocation.py](../src/chan/kelly_allocation.py) runs each resize
through `chan.kelly_leverage.rebalance`, the same operation Entry 3 runs for
*Quantitative Trading*'s Example 6.2, rather than a second copy of it.

**Example 8.2** has two uncorrelated strategies, with annualised mean excess
returns of 30 and 60 percent and volatilities of 26 and 35 percent, under a
broker's cap of 2 on gross leverage. Location 3268 calls scaling every Kelly
leverage down by one factor "the usual recommendation", and the example exists
to show it is not the allocation that grows fastest. The growth rate is
`g = r + F'M - F'CF / 2` at a risk-free rate of 0.

**The vintage column says `none, synthetic` in every row**, as in Entry 2.
Every input is a number the book states, and nothing reads a series. No row has
a window either, so the computed table drops that column the way Entry 2's
does.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | 8.1, the position after a \$10K loss | \$490K | location 3216 |
| 2 | 8.1, the trade that restores leverage 5 | sell \$40K, to \$450K | location 3216 |
| 3 | 8.1, the position after a \$20K gain the next day | \$470K | location 3216 |
| 4 | 8.1, the trade that restores leverage 5 | buy \$80K, to \$550K | location 3216 |
| 5 | 8.2, Kelly leverage of strategy 1 | 4.4 | location 3287 |
| 6 | 8.2, Kelly leverage of strategy 2 | 4.9 | location 3287 |
| 7 | 8.2, total gross Kelly leverage | 9.3 | location 3287 |
| 8 | 8.2, both leverages scaled to the cap of 2 | 0.95 and 1.05 | location 3287 |
| 9 | 8.2, growth rate at those leverages, Equation 8.4 | 0.82 | location 3287 |
| 10 | 8.2, growth rate with all of the cap on strategy 2 | 0.96 | location 3287 |
| 11 | 8.2, growth rate at the uncapped Kelly leverages, Equation 8.3 | none in the highlights, the equation is an image | absent, as [research/book-notes/README.md](../research/book-notes/README.md) records |
| 12 | 8.2, the line's stationary point when F2 is not bounded | none, the book plots F2 from 0 to the cap only | n/a |
| 13 | 8.2, the cap above which all on strategy 2 stops being best | none, the book says only "much smaller than" the total | location 3268 states the claim |

### What this repo computed

| # | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | `rebalance(5, equity=100000, shock=0.02)`, the dollar loss as a fraction of the \$500K position | none, synthetic | \$490,000 | `TestConstantLeverage::test_the_loss_day_sells_forty_thousand` |
| 2 | Target `5 × 90,000` less the position after the loss | none, synthetic | −\$40,000, to \$450,000 | `TestConstantLeverage::test_the_loss_day_sells_forty_thousand` |
| 3 | The \$20K gain as a negative shock on the \$450K position | none, synthetic | \$470,000 | `TestConstantLeverage::test_the_gain_day_buys_eighty_thousand` |
| 4 | Target `5 × 110,000` less the position after the gain | none, synthetic | +\$80,000, to \$550,000 | `TestConstantLeverage::test_the_gain_day_buys_eighty_thousand` |
| 5 | `F = C^-1 M`, zero correlation, so `0.30 / 0.26^2` | none, synthetic | 4.437870 | `TestKellyLeverages::test_the_computed_leverages` |
| 6 | `0.60 / 0.35^2` | none, synthetic | 4.897959 | `TestKellyLeverages::test_the_computed_leverages` |
| 7 | The absolute sum of rows 5 and 6 | none, synthetic | 9.335829 | `TestKellyLeverages::test_the_computed_leverages` |
| 8 | Both scaled by `2 / 9.335829`, a factor of 0.214228 | none, synthetic | 0.950718 and 1.049282 | `TestTheProportionalScaling::test_the_capped_leverages` |
| 9 | `g = F'M - F'CF / 2` at row 8 | none, synthetic | 0.816798 | `TestTheProportionalScaling::test_the_growth_rate_at_the_capped_leverages` |
| 10 | The same at F1 = 0, F2 = 2, the long-only optimum of the line `F1 = 2 - F2` | none, synthetic | 0.955, exactly 191/200 | `TestTheCorner::test_the_growth_rate_is_exactly_a_tie` and `::test_a_grid_over_the_whole_gross_boundary_agrees` |
| 11 | The same at rows 5 and 6 | none, synthetic | 2.135068 | `TestTheKellyGrowthRate::test_the_growth_rate_at_kelly` |
| 12 | The line's stationary point with F2 unbounded | none, synthetic | F2 = 2.289321, F1 = −0.289321, growth 0.962956, gross leverage 2.578643 | `TestTheNearMisses::test_the_unbounded_line_peaks_outside_the_cap` |
| 13 | `(m2 - m1) / (c22 - c12)` | none, synthetic | 2.448980 | `TestWhereTheCornerStopsWinning::test_the_threshold` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | \$0 | reproduced | Exact. |
| 2 | \$0 | reproduced | Chan's claim is that a constant leverage sells into a loss. The trade is a sale of exactly the size he prints. |
| 3 | \$0 | reproduced | Exact. |
| 4 | \$0 | reproduced | The same claim on the other side: the trade is a purchase into the gain. |
| 5 | +0.0 at the one decimal the book prints | reproduced | Exact at that precision. |
| 6 | −0.0 at one decimal | reproduced | Exact at that precision. |
| 7 | +0.0 at one decimal | reproduced | Exact at that precision. |
| 8 | +0.00 and −0.00 at two decimals | reproduced | Exact at that precision. This is the proportional scaling location 3268 calls the usual recommendation, which Example 8.2 sets out to refute, not a candidate for the best allocation. |
| 9 | −0.00 at two decimals | reproduced | Exact at that precision. |
| 10 | −0.005, stated at three decimals | reproduced | Chan's claim is that putting the whole cap on strategy 2 beats the proportional scaling, and 0.955 against row 9's 0.816798 says it does. The growth rate rises over the whole line and peaks at the corner. This file states a gap at the coarser precision, rounded from the full value, and that would print −0.01 for a figure that lands. The computed value is an exact tie at the book's two decimals, and Chan prints it rounded up, which half-up and half-to-even rounding both give. |
| 11 | none | none, not a replication | Equation 8.3 is an image the highlights did not capture, so whether the book prints a value is not known here. The row exists so the figure is pinned when it is. |
| 12 | none | none, not a replication | The near miss. Substituting `F1 = Fmax - F2` without bounding F2 finds a higher growth rate by shorting strategy 1, at a gross leverage above the cap. Location 3268 is explicit that the cap is on gross leverage, so this allocation is not allowed. |
| 13 | none | none, not a replication | Chan says the corner tends to win when the cap is "much smaller than" the total Kelly leverage. On these inputs it wins for any cap below 2.448980, against a total of 9.335829, and above that the best allocation holds both strategies. |

### What the entry concludes

Four things.

1. **The verdicts were known before the work started.** Nothing can move an
   arithmetic result, which is Entry 2's first conclusion, and planning on the
   issue computed every row before the module existed. Neither epistemic label
   reaches the entry either, for the reason Entry 2 gives: no sample was spent.
   What the entry is worth is rows 10, 12 and 13, which pin what the book's
   claim rests on rather than only the figures it prints.
2. **The book already answers whether 0.95 and 1.05 is the best allocation.**
   It is the proportional scaling the example refutes. Along the line
   `F1 = 2 - F2` the slope of the growth rate is `0.4352 - 0.1901 F2`, positive
   for every F2 from 0 to 2, so the growth rate peaks with everything on
   strategy 2.
3. **The printed 0.96 depends on a rounding mode.** The exact value is 0.955.
   A float holding it sits just below the tie, so the formatting a report would
   reach for first prints 0.95 beside Chan's 0.96. The module prints three
   decimals, and the suite pins the tie and the two rounding rules that give
   0.96.
4. **The best allocation under the cap is long-only here, and not in general.**
   On Chan's inputs a grid over every allocation the gross cap allows, short
   positions included, finds the same corner. With a strong positive
   correlation it does not. `TestTheLongOnlyLimit` holds a case where a short
   hedge inside the cap grows at 0.656501 against 0.48 for the best long-only
   allocation, which is why the module's capped search says it is long-only.

### What this entry cannot say

Two things.

**Whether Equation 8.3 prints a number.** Row 11 waits on the book itself. If
it prints a value, the row gains a published figure and a verdict.

**Anything about a real pair of strategies.** Every input is hypothetical and
Gaussian by assumption. Whether a cap makes a real second strategy worth
dropping depends on moments estimated from data, with the estimation error
location 3235 warns about.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 21: price spread, log price spread and ratio, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 3.1, Kindle locations 1476 to 1505, and the
scripts `PriceSpread.m`, `LogPriceSpread.m` and `Ratio.m` the example names.
Shipped under
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340). The
location numbers are that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from
[tests/test_price_spread.py](../tests/test_price_spread.py).

**Two of the three scripts reproduce to six digits on Chan's own file, and the
third misses, landing only with its two legs swapped.** A pair trade needs a signal
that reverts, and Example 3.1 asks which one to build from two prices. It runs
one rule on the gold ETF GLD and the oil ETF USO three ways: on the price spread
`USO − h·GLD`, on the log price spread `log USO − h·log GLD`, and on the ratio
`USO / GLD`. The hedge ratio `h` is refitted every day by regression over the
last 20 days. Each day the rule holds minus the signal's 20-day z-score in
units of the pair, so it buys the spread in proportion as it falls below its
moving average. Chan notes that GLD and USO are not cointegrated, and asks
whether there is enough short-term reversion to trade anyway.

The price spread and the log price spread land all four figures their scripts
print. `Ratio.m` as published misses both of its own. The same script with GLD
and USO swapped lands both, to all six digits, a reading tried after the miss,
and the book's sentence that the ratio loses money holds either way.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdata_etf/gld.csv` and `inputdata_etf/uso.csv`, two
   of the 67 ETFs of Chan's `inputData_ETF.mat`, saved 2012-04-10, read through
   `chan.series.load_panel`, 1,500 days from 2006-04-26 to 2012-04-09. The file
   folds dividends in by subtracting them in dollars, and GLD pays none.
   Neither leg carries a day the scale-break guard flags, so the run calls the
   guard and it refuses nothing.
2. **The specification.** The three scripts at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   the same git blobs as in ivanliu1989/algorithmic_trading at `4567024`. The
   hedge ratio is the slope of `ols(USO, [GLD ones])` over the 20 rows ending at
   each row, on log prices for the log price spread. The first 20 rows are
   dropped, leaving 1,480 from 2006-05-24. The units are minus the 20-row
   z-score, from `movingAvg` and `movingStd`, the plain mean and MATLAB's
   n − 1 `std`. One unit holds `[−h·GLD, USO]` dollars for the price spread,
   `[−h, 1]` for the log price spread and `[−1, 1]` for the ratio. The return
   is the day's profit on yesterday's dollars over the gross dollars held, with
   a NaN day set to 0. The APR is compounded over all 1,480 rows at 252 a year,
   and the Sharpe ratio uses MATLAB's n − 1 `std` and subtracts no risk-free
   rate. No cost is charged.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 to 2012 sample on a rule he chose, with a lookback he calls
"near-optimal" with "the benefit of hindsight", so the entry says whether his
numbers reproduce on his file and nothing about whether the rule pays today.

### What the book printed

Each script closes on a comment holding the six decimals its
`fprintf('APR=%f Sharpe=%f')` prints. Location 1505 rounds the first two
scripts' figures and prints no number for the ratio.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Price spread, APR | 0.108335, and "about 10.9 percent" | `PriceSpread.m`, location 1505 |
| 2 | Price spread, Sharpe ratio | 0.589651, and "about 0.59" | `PriceSpread.m`, location 1505 |
| 3 | Log price spread, APR | 0.088863, and "9 percent" | `LogPriceSpread.m`, location 1505 |
| 4 | Log price spread, Sharpe ratio | 0.504153, and "0.5" | `LogPriceSpread.m`, location 1505 |
| 5 | Ratio, APR | −0.141522 | `Ratio.m` |
| 6 | Ratio, Sharpe ratio | −0.746663 | `Ratio.m` |
| 7 | The ratio loses money | "a negative APR", a claim | location 1505 |
| 8 | The log price spread does worse than the price spread | "actually lower", a claim | location 1505 |
| 9 to 11 | the swapped legs, the first position, and two choices that move nothing | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + ret)^(252/1480) − 1` on the price spread | 0.108335 | `TestTheFigures::test_the_price_spread_apr_is_chans_0_108335` and `::test_the_books_about_10_9_percent_is_not_its_scripts_figure_rounded` |
| 2 | `√252 · mean(ret) / std(ret)` on the price spread | 0.589651 | `TestTheFigures::test_the_price_spread_sharpe_ratio_is_chans_0_589651` |
| 3 | row 1 on the log price spread | 0.088863 | `TestTheFigures::test_the_log_price_spread_apr_is_chans_0_088863` |
| 4 | row 2 on the log price spread | 0.504153 | `TestTheFigures::test_the_log_price_spread_sharpe_ratio_is_chans_0_504153` |
| 5 | row 1 on the ratio, `Ratio.m` as published | −0.134608 | `TestTheRatio::test_the_published_script_misses_both_figures` |
| 6 | row 2 on the ratio, `Ratio.m` as published | −0.702522 | `TestTheRatio::test_the_published_script_misses_both_figures` |
| 7 | row 5, as published and with the legs swapped | −0.134608 and −0.141522, both below 0 | `TestTheClaims::test_the_ratio_loses_money` |
| 8 | rows 3 and 4 against rows 1 and 2 | both lower | `TestTheClaims::test_the_log_price_spread_is_below_the_price_spread_on_both_figures` |
| 9 | rows 5 and 6 with GLD and USO swapped, so the signal is GLD/USO | −0.141522 and −0.746663 | `TestTheRatio::test_the_script_with_gld_and_uso_swapped_lands_both` |
| 10 | the first day with units, and the first day a return is earned, on every run | 2006-06-21 and 2006-06-22 | `TestTheFigures::test_the_first_position_is_held_into_2006_06_22` |
| 11 | every run with `lag` padding 0 rather than NaN, and with book two's `smart` average and deviation | the same returns, exactly and within 1e-12 | `TestWhatMovesNothing` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.000000 against the script, −0.1 against the book | reproduced | Chan's figure, on his own file, through his own script transcribed. The book's "about 10.9 percent" is not the script's 0.108335 rounded, which is 10.8, so the book's figure does not follow from its own script's. |
| 2 | 0.000000 against the script, 0.00 against the book | reproduced | The same as row 1. |
| 3 | 0.000000 against the script, 0 against the book | reproduced | The same as row 1. |
| 4 | 0.000000 against the script, 0.0 against the book | reproduced | The same as row 1. |
| 5 | +0.006914 | did not reproduce | Chan's own file and his published script, so the vintage explanation is spent. The same script with the legs swapped lands the comment's figure exactly, row 9, so the evidence favours the comment coming from a different run rather than from this script. That cause is a different method, so it cannot turn the miss into a gap. |
| 6 | +0.044141 | did not reproduce | The same as row 5. |
| 7 | none, a claim | reproduced | The APR is below 0 on the published script and on the swapped legs both. The criterion was written on [issue 340](https://github.com/l3a0/quantitative-trading/issues/340) after the first transcription ran, and it is the sentence's own word, negative, with no threshold to choose. |
| 8 | none, a claim | reproduced | The log price spread's APR and Sharpe ratio are both below the price spread's. The criterion was written after the first run, as row 7's was, and reads "lower" on both figures the sentence names. |
| 9 | none | none, not a replication | A reading chosen after row 5 missed, the third of three that [issue 340](https://github.com/l3a0/quantitative-trading/issues/340) names. The other two, keeping the first 20 days and Chan's Python port, match neither figure, which `TestTheRatio::test_keeping_the_first_20_days_matches_neither_figure` and `::test_chans_python_port_matches_neither_figure` hold. It lands both of the comment's figures to six digits. The two come from one return series, so they are not independent matches, but a coincidence would still have to land two different summaries of it. |
| 10 | none | none, not a replication | `movingStd` first fills on the 20th kept row, and a position earns from the next close, so every run holds its first position into 2006-06-22. |
| 11 | none | none, not a replication | Neither mirror holds `lag.m`. A NaN pad makes the first row's return NaN. A zero pad divides by a price of 0, so the first row's profit is NaN over zero gross dollars, and either NaN is set to 0. The return is profit over gross dollars, so a deviation that divides by n rather than n − 1 scales every unit by one factor and cancels. |

### What the entry concludes

Three things.

1. **Example 3.1's price spread and log price spread reproduce exactly on
   Chan's own file.** All four figures the two scripts print land to six
   digits. The book's "about 10.9 percent" is the one rounding that does not
   follow from its script, which prints 10.8 percent to that precision.
2. **The ratio's printed figures match a run with GLD and USO swapped.**
   The book captions its Figure 3.2 "Ratio = USO/GLD", and the published
   `Ratio.m` computes USO/GLD. Its comment's two figures are what GLD/USO
   gives, with a positive unit buying GLD. The reading was found after the
   miss rather than declared, so it is the cause the evidence favours, not a
   reproduction. Chan's point survives either way: the ratio loses money on
   this pair, by 13.5 or 14.2 percent a year, which
   `TestTheClaims::test_the_ratio_loses_13_5_or_14_2_percent_a_year` holds.
3. **The linear rule cannot see how the deviation is scaled.** Its return is
   profit over gross dollars, so multiplying every unit by one constant leaves
   it unchanged. Book two's `smartMovingStd`, which divides by n, gives the
   same figures here as `movingStd`, unlike Entries 12 and 18, where the
   choice of `smartstd` moved a printed digit. Example 3.2 compares the
   z-score with a fixed threshold, where no constant cancels, so
   [issue 341](https://github.com/l3a0/quantitative-trading/issues/341)
   cannot rely on this entry's figures to say which divisor its own need.
   Entry 26 measures it, and there the divisor moves both figures.

### What this entry cannot say

Four things.

**Which run produced `Ratio.m`'s comment.** Swapping the legs lands both
figures. Neither mirror holds another version of the script, so whether Chan
edited the script after running it, or ran an earlier one, is not recoverable
here.

**Whether the reversion is real.** Chan says GLD and USO do not cointegrate,
and on his file the test does not come close to finding that they do.
Engle-Granger at one lag, USO on GLD over all 1,500 days, gives −1.5150
against a 10% bar of −3.04, which
`TestThePairDoesNotCointegrate::test_engle_granger_does_not_reject_at_10_percent`
holds. The 20-day hedge ratio is below zero on 334 of the 1,480 traded days,
which `::test_the_20_day_hedge_ratio_changes_sign` holds. The spread the
scripts trade leaves out the 20-day fit's intercept, which tracks it at a
correlation of 0.9987, and the fit's leftover traded alone earns an APR of
−0.005130, which `::test_the_spread_is_almost_all_the_fits_intercept` holds.
Nothing here separates a real short-term reversion from what a 20-day fit
produces.

**What costs would take.** No script charges any. Location 1505 names the
extra cost of the log price spread, which rebalances both legs every day to
hold its dollar split.

**Whether 20 days was a fair choice.** Chan calls it near-optimal with the
benefit of hindsight, so the lookback was fitted to this sample, and every
figure above is in-sample.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/price-spread-ratio-lessons.md](../blog/price-spread-ratio-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.price_spread_figures` redraws.

## Entry 22: the stationarity tests on USD.CAD, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Examples 2.1 to 2.5, Kindle locations 1076 to 1225,
with the half-life repeated at 1347. Shipped under
[issue 338](https://github.com/l3a0/quantitative-trading/issues/338). One
script, `stationarityTests.m`, runs all five examples in order on the same
closes, and its comments print every figure but one. The script is in
ericnberwick/EpchanPreview at `e4bc46f`, under `public/img/book2/`.

Ten rows, all derivable from
[tests/test_usdcad_mean_reversion.py](../tests/test_usdcad_mean_reversion.py).
Seven do not match one printed figure to one computation, and each says so in
its own cells. Rows 1, 3, 5 and 6 each cover more than one figure from one
computation. Rows 8 to 10 carry no published figure.

**The closes.** Every row reads one vintage: Chan's minute file of USD.CAD,
vendor `chan-py`, symbol `USDCAD`, basis `raw`, saved 2018-10-13, from his
2018 Python port. The script keeps the bar stamped 16:59 New York time on each
day, which gives 1,216 closes from 2007-07-23 to 2012-03-28. The script loads
a MATLAB file of the same bars that neither public mirror holds, so the only
evidence that the two hold the same closes is that every figure below except
H lands every digit the script prints.

**The three functions Chan did not write.**
[src/chan/stationarity_tests.py](../src/chan/stationarity_tests.py) transcribes
each, and its docstring names where each came from.

1. James LeSage's jplv7 `adf`, with the critical values of its `ztcrit`. It
   fits one row fewer than `statsmodels`' `adfuller` at the same lag, because
   it trims the lagged level after trimming the lagged changes.
2. Tomaso Aste's `genhurst`, from the MATLAB File Exchange. Every surviving
   copy is dated 2013-01-30, and they run one algorithm.
3. MATLAB's `vratiotest`, Lo and MacKinlay's variance ratio test with a
   variance that allows for changing volatility. It trims the returns to a
   whole number of periods before anything else.

The half-life is `ithildincore`'s `ou_half_life`, which is the script's own
regression, and Example 2.5 uses Chan's `movingAvg` and `movingStd`, which
[src/chan/matlab_helpers.py](../src/chan/matlab_helpers.py) carries.

**Example 2.5's claim was declared before its P&L existed.** Location 1225
says the P&L "manages to be positive, albeit with a large drawdown".
[Issue 338](https://github.com/l3a0/quantitative-trading/issues/338) wrote down
that the claim holds when the sum of the daily P&L over all 1,216 rows is
above 0. "Large" names no scale, so the drawdown is reported beside the claim
and decides nothing.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | 2.1, the ADF statistic at 1 lag | −1.840744, and "about −1.84" | the script's comment, location 1114 |
| 2 | 2.1, the AR(1) estimate | 0.994120 | the script's comment |
| 3 | 2.1, the 1, 5 and 10 percent critical values | −3.458, −2.871 and −2.594 | the script's comment, location 1114 for the 10 percent value |
| 4 | 2.2, the Hurst exponent | 0.49 | location 1119 |
| 5 | 2.3, the variance ratio test's decision and p-value | h=0, 0.367281 | the script's comment |
| 6 | 2.4, the half-life | 115.209794, and 115 days | the script's comment, locations 1193 and 1347 |
| 7 | 2.5, the cumulative P&L is positive | a claim | location 1225 |
| 8 | 2.1, the statistic `adfuller` gives at the same lag | none, the book runs jplv7 | n/a |
| 9 | 2.2, H from the Python port's own `genhurst` | none, the book runs Aste's | n/a |
| 10 | 2.5, the deepest drawdown | none, the book says only "large" | location 1225 states the claim |

### What this repo computed

| # | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | jplv7 `adf(y, 0, 1)` on the 1,216 closes, 1,213 rows fitted | `chan-py` USDCAD raw, saved 2018-10-13 | −1.840744089 | `TestExample21TheAdfTest::test_the_statistic_is_chans_minus_1_840744` |
| 2 | The same regression's coefficient on the lagged level | the same | 0.9941196429 | `TestExample21TheAdfTest::test_the_ar1_estimate_is_chans_0_994120` |
| 3 | `ztcrit`'s row for 1,216 observations at trend order 0 | the same | −3.45830, −2.87104 and −2.59369 | `TestExample21TheAdfTest::test_the_critical_values_are_chans` |
| 4 | `genhurst(log(y), 2)`, window lengths 5 to 19 | the same | 0.4732326652 | `TestExample22TheHurstExponent::test_h_misses_the_books_0_49` |
| 5 | `vratiotest(log(y))`, period 2, 1,214 returns | the same | h=0, p 0.3672813756 | `TestExample23TheVarianceRatio::test_the_decision_and_p_value_are_chans` |
| 6 | `−log(2)/λ`, λ from the change on the previous close and a constant | the same | 115.2097944852 | `TestExample24TheHalfLife::test_the_half_life_is_chans_115_209794` |
| 7 | The sum of the daily P&L, at a lookback of 115, the half-life rounded, so the first position is held on 2008-01-02 | the same | 0.1141168588 | `TestExample25LinearMeanReversion::test_the_cumulative_pnl_is_positive_as_location_1225_says` |
| 8 | `adfuller(y, maxlag=1, regression='c', autolag=None)`, 1,214 rows fitted | the same | −1.8430182830 | `TestExample21TheAdfTest::test_adfuller_at_the_same_lag_misses_by_the_one_row_it_keeps` |
| 9 | `genhurst.py` from Chan's 2018 Python port, on the log closes | the same | 0.4758441244 | `TestExample22TheHurstExponent::test_the_python_ports_own_genhurst_misses_too` |
| 10 | The deepest fall of the cumulative P&L below its running high | the same | 0.6425313986, from 2008-07-22 to 2008-10-27 | `TestExample25LinearMeanReversion::test_the_drawdown_reported_beside_it` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000 at six decimals | reproduced | Exact at the six decimals the script prints. Location 1114's reading survives: the statistic sits above the 10 percent value of −2.594, so a unit root is not rejected. |
| 2 | −0.000000 at six decimals | reproduced | Exact at that precision. λ, the estimate less 1, is negative, which is location 1114's second reading. |
| 3 | −0.000, −0.000 and +0.000 at three decimals | reproduced | Exact at that precision. 1,216 observations fall in the table's last bin, which every series of 425 or more reads. |
| 4 | −0.02 at two decimals | did not reproduce | 0.4732 prints as 0.47 against the book's 0.49, on the closes every other test lands. The claim the figure was printed for survives: H is below 0.5, which location 1119 reads as weakly mean reverting. No cause outside the method is available. The only candidate is a `genhurst` older than the one every surviving copy carries, and that would be a different method rather than a different vintage. |
| 5 | +0.000000 at six decimals | reproduced | The decision is exact and the p-value is exact at six decimals. The variance ratio is 0.9647, below 1, as a reverting series gives, and not significantly so. |
| 6 | +0.000000 at six decimals, and 0 days | reproduced | Exact at the six decimals the script prints, and at the whole days the book prints. |
| 7 | none, a claim | reproduced | The criterion written on [issue 338](https://github.com/l3a0/quantitative-trading/issues/338) before any P&L existed holds. The P&L ends at 0.1141, above 0. |
| 8 | none | none, not a replication | Both `ithildincore`'s `adf_tstat` and the ADF line in Chan's 2018 Python port run `adfuller`, which fits the one row jplv7 drops. The Python port would print −1.843018 for the figure the script's comment records as −1.840744. |
| 9 | none | none, not a replication | The port's `genhurst` is a different estimator, the slope of the log variance of τ-day changes on log τ, halved. It lands nearer the book than Aste's, at 0.48, and still misses 0.49. |
| 10 | none | none, not a replication | The cumulative P&L reaches 0.1321 on 2008-07-22 and falls to −0.5104 on 2008-10-27, a drop more than five times what the run ends with. That reads as large on any scale, but the book gives none, so it decides nothing. |

### What the entry concludes

Four things.

1. **The closes Chan ran are the closes committed here.** The MATLAB file
   cannot be compared directly, and four independent statistics landing every
   printed digit is stronger evidence than a comparison of a sample of days
   would be.
2. **The ADF figure depends on which toolbox runs it.** jplv7's `adf` and
   `adfuller` agree on the regression and differ by one row of sample, and
   that row moves the third decimal, from −1.8407 to −1.8430. This repo's
   existing ADF lives in `ithildincore` and runs `adfuller`, so a replication
   of a jplv7 figure needs jplv7's trimming, which is why
   `chan.stationarity_tests` exists beside it.
3. **H is the one figure that does not land, and it misses under both
   implementations Chan's code uses.** Aste's `genhurst` gives 0.47 and Chan's
   2018 Python port gives 0.48, so the book's 0.49 is not what either computes on
   these closes. Every reading of H here agrees with the book's conclusion,
   that USD.CAD is at most weakly mean reverting, and the variance ratio test
   says the same thing more carefully: not distinguishable from a random walk.
4. **Example 2.5's claim survives, and it carries the look-ahead Chan names.**
   The lookback of 115 days is the half-life of the same 1,216 closes the
   strategy trades. Its P&L is positive by 0.1141 after a fall of 0.6425, and
   whether that survives a lookback chosen without seeing the closes is a
   question this entry does not ask.

### What this entry cannot say

Four things.

**What computed the book's 0.49.** No surviving copy of `genhurst` gives it,
and the script that printed it records no value. Searching for the variant
that lands it would be choosing a reading after its number is seen.

**Whether Example 2.5 would pay.** The look-ahead above, no transaction cost,
and a position that grows without limit as the deviation does, all of which
location 1225 names. The P&L is in units of the position's own scale rather
than a return on capital, so it carries no Sharpe ratio or APR, and the book
prints none.

**Anything about USD.CAD after March 2012.** Every figure is exploratory, on a
sample Chan already chose.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/usdcad-stationarity-lessons.md](../blog/usdcad-stationarity-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.usdcad_mean_reversion_figures` redraws.

## Entry 23: EWA, EWC and IGE, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Examples 2.6 to 2.8, Kindle locations 1252 to 1368,
and the script `cointegrationTests.m` all three examples name. Shipped under
[issue 339](https://github.com/l3a0/quantitative-trading/issues/339). Every
example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Twenty rows, all derivable from
[tests/test_etf_cointegration.py](../tests/test_etf_cointegration.py).

Chan asks whether EWA and EWC, the Australian and Canadian country ETFs, are
cointegrated, since both economies run on commodities. Example 2.6 runs the
CADF test, which regresses EWC on EWA and tests the residual for a unit root.
Example 2.7 runs the Johansen test, which takes any number of series and counts
how many independent stationary combinations they hold, first on the pair and
then with IGE, a fund of natural resource stocks, added. Each combination is an
eigenvector, so the test hands back hedge ratios as well as a count. Chan
builds a portfolio from the triplet's first eigenvector, measures its
half-life, and Example 2.8 trades it with a linear mean-reversion rule, holding
minus its z-score in units of the portfolio.

**Every figure the script prints reproduces on Chan's own file, to every
digit it prints, with the eigenvectors' signs flipped.** The one claim that fails is in the prose, and the script's own
printout already contradicts it. Location 1337 says both Johansen statistics
find three relations for the triplet. The eigen statistic for the first null is
16.897, short of even its 90 percent bar of 18.893.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdata_etf/ewa.csv`, `ewc.csv` and `ige.csv`, lifted
   from Chan's `inputData_ETF.mat`, saved 2012-04-10, 1,500 trading days from
   2006-04-26 to 2012-04-09, read for the close through
   `chan.series.load_panel`. The file adjusts for dividends by subtracting
   them in dollars, which [data/README.md](../data/README.md) records, so a
   return taken from it is not quite the return a holder earned.
2. **The specification.** `cointegrationTests.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview).
   The CADF test is jplv7's `cadf(EWC, EWA, 0, 1)`, a constant and one lag,
   run by `chan.pair_cointegration.lesage_cadf`. The Johansen test is jplv7's
   `johansen(·, 0, 1)`, a constant and one lagged difference, on columns
   ordered EWC, EWA, IGE, run by `chan.johansen.johansen` over statsmodels'
   `coint_johansen`, which carries LeSage's critical-value tables and matches
   his function's output at these settings. The half-life comes from a regression of the
   portfolio's daily change on its lagged level with an intercept. The
   strategy's lookback is that half-life rounded half away from zero, the
   APR is `prod(1 + r)^(252 / n) − 1` and the Sharpe ratio is
   `√252 · mean / std` over all 1,500 days, with no risk-free rate and no
   cost.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 to 2012 sample on a portfolio he chose. The eigenvector is also fitted on
the same 1,500 days the strategy trades, so the APR is in-sample by
construction.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | 2.6, CADF t-statistic, EWC on EWA | −3.64346635, "about –3.64" | script line 36, location 1292 |
| 2 | 2.6, CADF AR(1) estimate | −0.020411 | script line 36 |
| 3 | 2.6, the pair cointegrates at 95 percent | a claim, against jplv7's −3.359 | location 1292 |
| 4 | 2.7, pair trace statistics, r ≤ 0 and r ≤ 1 | 19.983 and 3.983 | script lines 51 and 52 |
| 5 | 2.7, pair eigen statistics | 16.000 and 3.983 | script lines 55 and 56 |
| 6 | 2.7, both tests find two relations for the pair | a claim, with the trace's r ≤ 0 rejected at 99 percent | location 1324 |
| 7 | 2.7, triplet trace statistics | 34.429, 17.532 and 4.471 | script lines 73 to 75 |
| 8 | 2.7, triplet eigen statistics | 16.897, 13.061 and 4.471 | script lines 78 to 80 |
| 9 | 2.7, both tests find three relations for the triplet at 95 percent | a claim | location 1337 |
| 10 | 2.7, the triplet's eigenvalues | 0.0112, 0.0087 and 0.0030 | script lines 86 to 88 |
| 11 | 2.7, the triplet's eigenvectors | a 3 × 3 matrix, first column −1.0460, 0.7600, 0.2233 | script lines 94 to 96 |
| 12 | 2.7, half-life of the first eigenvector's portfolio | 22.662578, "23 days" | script line 110, location 1347 |
| 13 | 2.8, the strategy's APR | 0.125739, "12.6 percent" | script line 125, location 1368 |
| 14 | 2.8, the strategy's Sharpe ratio | 1.391310, "1.4" | the same |
| 15 | the hedge ratio, EWC on EWA with an intercept | none, it feeds Figure 2.6 only | script line 23 |
| 16 | the CADF test with the legs reversed | none, location 1282 says only that it differs | location 1282 |
| 17 | the triplet's test with the columns reordered | none, location 1324 says only that order does not matter | location 1324 |
| 18 | each eigenvector's half-life | none, location 1340 says only that the first should be shortest | location 1340 |
| 19 | a plain ADF test of each ETF alone | none | n/a |
| 20 | the first day the strategy earns, and how many days it does | none | n/a |

The critical values are pinned beside rows 1, 4, 5, 7 and 8, at the three
decimals the script prints. The Johansen ones come from statsmodels, which
carries LeSage's tables. The CADF ones are jplv7's own table, quoted rather
than computed, since no code here carries it. MacKinnon's table, which
`ithildincore` carries, puts the 5 percent bar at −3.34 and gives the same
verdict, which `test_row_3_the_pair_cointegrates_at_95_percent` also asserts.

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `lesage_cadf(EWC, EWA, 1)` | −3.6434663489 | `TestExample26TheCadfTest::test_row_1_the_t_statistic` |
| 2 | The same | −0.0204108120, on 1,498 observations | `TestExample26TheCadfTest::test_row_2_the_ar1_estimate_and_the_observations` |
| 3 | Row 1 against jplv7's −3.880 and −3.359 | between them | `TestExample26TheCadfTest::test_row_3_the_pair_cointegrates_at_95_percent` |
| 4 | `johansen([EWC, EWA], 0, 1)` | 19.983219 and 3.982761 | `TestExample27TheJohansenTest::test_row_4_the_pair_trace_statistics` |
| 5 | The same | 16.000457 and 3.982761 | `TestExample27TheJohansenTest::test_row_5_the_pair_eigen_statistics` |
| 6 | Nulls rejected in order, up to the first that is not | 2 by each test at 95 percent, the trace's first also at 99 | `TestTheClaims::test_row_6_both_tests_find_two_relations_for_the_pair_at_95` and the two tests beside it |
| 7 | `johansen([EWC, EWA, IGE], 0, 1)` | 34.428620, 17.531719 and 4.471021 | `TestExample27TheJohansenTest::test_row_7_the_triplet_trace_statistics` |
| 8 | The same | 16.896901, 13.060698 and 4.471021 | `TestExample27TheJohansenTest::test_row_8_the_triplet_eigen_statistics` |
| 9 | As row 6 | 3 by the trace test at 90 and 95 percent and 0 at 99, and 0 by the eigen test at all three | `TestTheClaims::test_row_9_the_trace_test_finds_three_relations_at_95`, `::test_row_9_the_trace_test_finds_none_at_99` and `::test_row_9_the_eigen_test_finds_none_even_at_90` |
| 10 | The same test as row 7 | 0.01121626, 0.00868086 and 0.00298021 | `TestExample27TheJohansenTest::test_row_10_the_triplet_eigenvalues` |
| 11 | The same | Chan's matrix with every sign flipped, first column 1.0460, −0.7600, −0.2233 | `TestExample27TheJohansenTest::test_row_11_the_eigenvectors_are_chans_with_every_sign_flipped` |
| 12 | `ou_half_life` on the first eigenvector's portfolio | 22.6625778505 | `TestExample27TheJohansenTest::test_row_12_the_half_life` |
| 13 | A lookback of 23, the script's lines 115 to 124 | 0.1257386810 | `TestExample28TheStrategy::test_row_13_the_apr` |
| 14 | The same | 1.3913100883 | `TestExample28TheStrategy::test_row_14_the_sharpe_ratio` |
| 15 | `ols(EWC, [EWA, 1])` | 0.9624293987 | `TestBesideTheReplication::test_the_hedge_ratio_feeds_only_the_figure` |
| 16 | `lesage_cadf(EWA, EWC, 1)` | −3.6405421403, 0.0029 less negative than row 1 | `TestBesideTheReplication::test_reversing_the_legs_moves_the_statistic_and_not_the_verdict` |
| 17 | `johansen([EWA, EWC, IGE], 0, 1)` | every statistic and eigenvalue within 10⁻¹¹ of rows 7, 8 and 10, and the eigenvectors' rows permuted with the first two columns negated | `TestBesideTheReplication::test_reordering_the_columns_leaves_every_statistic` |
| 18 | `ou_half_life` on each eigenvector's portfolio | 22.662578, 43.731678 and 151.546826 days | `TestBesideTheReplication::test_the_first_eigenvector_reverts_fastest` |
| 19 | ADF with a constant and one lag, against MacKinnon's −2.57 at 90 percent | −1.863334 for EWA, −1.901877 for EWC and −2.078705 for IGE | `TestBesideTheReplication::test_no_etf_alone_rejects_a_unit_root_even_at_90` |
| 20 | The first non-zero day of row 13's returns | 2006-05-30, row 23, and 1,477 days from there on | `TestExample28TheStrategy::test_the_first_return_is_on_row_23_and_every_later_day_has_one` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.00000000 at the eight decimals the script prints | reproduced | Exact, and so at the book's two. |
| 2 | 0.000000 | reproduced | Exact. |
| 3 | none, a claim | reproduced | −3.643 is past −3.359, so the pair cointegrates at 95 percent, as Chan says. It is short of the 99 percent bar of −3.880, which he does not claim. |
| 4 | 0.000 on each | reproduced | Exact. |
| 5 | 0.000 on each | reproduced | Exact. |
| 6 | none, a claim | reproduced | Both tests reject r ≤ 0 and r ≤ 1 at 95 percent, and the trace's 19.983 clears its 99 percent bar of 19.935. What two relations between two series means is the subject of the second conclusion below. |
| 7 | 0.000 on each | reproduced | Exact. |
| 8 | 0.000 on each | reproduced | Exact. |
| 9 | none, a claim | did not reproduce | The trace test finds three relations at 95 percent. The eigen test finds none, because 16.897 falls short of the 90 percent bar of 18.893 before the later nulls are reached. The claim is that both tests agree, and the script's own printout, which is what this row reads, shows they do not. |
| 10 | 0.0000 on each | reproduced | Exact at the four decimals printed. |
| 11 | 0.0000 on each magnitude | reproduced | Every sign is flipped, and the specification predicts it. statsmodels multiplies the whole matrix by the sign of its top-left element, and MATLAB gave −1.0460 there. A negated portfolio is the same portfolio held short, and `TestExample28TheStrategy::test_negating_the_eigenvector_moves_nothing` shows rows 12 to 14 do not move. |
| 12 | 0.000000, and 0 at the book's whole days | reproduced | Exact. |
| 13 | 0.000000, and 0.0 at the book's one decimal of a percent | reproduced | Exact. |
| 14 | 0.000000, and 0.0 at the book's one decimal | reproduced | Exact. |
| 15 | none | none, not a replication | The script prints nothing from it. |
| 16 | none | none, not a replication | Location 1282 says swapping the legs changes the result. It does, by 0.0029, and both orders cointegrate at 95 percent. |
| 17 | none | none, not a replication | Location 1324 says the Johansen test does not depend on the order of its series. The statistics agree to rounding, and the eigenvectors come back with their rows permuted and two of the three negated. |
| 18 | none | none, not a replication | Location 1340 expects the first eigenvector to revert fastest. It does, and the half-lives rise as the eigenvalues fall. |
| 19 | none | none, not a replication | None of the three rejects a unit root on its own, which is what row 6's reading turns on. |
| 20 | none | none, not a replication | The moving deviation first fills on row 22, so positions first earn on row 23. |

### What the entry concludes

Three things.

1. **The script reproduces and the prose around it does not, in one
   place.** Every number `cointegrationTests.m` prints lands to its last digit
   on Chan's own file, the eigenvectors up to their sign, so the entry has nothing to say about the data. Row 9
   is the exception, and the evidence against it is Chan's own printout, which
   sits next to the sentence in the book. A reader who trusts the paragraph
   over the table takes away a stronger result than the run gave. The trace
   test finds three relations and the eigen test none.
2. **Two relations between two series is a stronger claim than Chan reads
   it as.** Location 1324 explains the pair's two relations as two hedge
   ratios, one from each regression order. A Johansen rank equal to the number
   of series says something else: that every combination is stationary,
   including each ETF on its own around a constant. The triplet's trace test
   reaches full rank too, three relations among three series, so it says the
   same of all three. Row 19 sits in tension with both. No ETF rejects a unit
   root on its own, at −1.86, −1.90 and −2.08 against −2.57. A plain ADF on
   levels has little power, so failing to reject is weak evidence of a unit
   root rather than proof of one, and this run does not settle which reading
   holds. What it does show is how thin the pair's full rank is: the second
   null falls by 0.141, 3.983 against 3.841.
3. **The strategy's 12.6 percent carries look-ahead in its weights as well
   as its lookback.** The eigenvector is fitted on the same 1,500 days the
   strategy then trades, and so is the half-life that sets the lookback. Chan
   says as much: location 1225 names the look-ahead in fitting a half-life on
   in-sample data, and location 1429 says the book's backtests use the same
   data to find a hedge ratio and to test it. Location 1350's claim is a
   different one, that the rule has no parameter to search over, so no
   data-snooping. Both statements hold, and the figure is in-sample either way.
   Nothing in this entry measures how much the look-ahead is worth.

### What this entry cannot say

Four things.

**Whether the portfolio works out of sample.** No row refits the eigenvector
on one window and trades it on the next. That is the experiment that would
price the third conclusion above, and it is a different run with its own
issue to file.

**Anything about costs.** The linear rule trades every day by construction, and
location 1350 calls it impractical for that reason. No cost is charged here, as
none is in the script.

**Whether another lag count changes the counts.** Every book-two script uses
`k = 1`, and so does this entry. The relation counts in rows 6 and 9 are for
that lag alone, and row 6's rests on a margin of 0.141.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/johansen-etf-lessons.md](../blog/johansen-etf-lessons.md) moves with
it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.etf_cointegration_figures` redraws.

## Entry 24: SPY against its component stocks, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 4.2, Kindle locations 2027 and 2035, and the
script `indexArb.m` the example names. Shipped under
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343). Every
example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Sixteen rows, all derivable from
[tests/test_index_arbitrage.py](../tests/test_index_arbitrage.py).

Chan trades an index against the stocks inside it. He tests each stock in his
2012 S&P 500 file against SPY over 2007 with the Johansen test, keeps the
stocks that pass, and holds them with equal capital as one basket. A second
Johansen test checks that the basket's log price cointegrates with SPY's, and
its first eigenvector sets one dollar weight for every stock and another for
SPY. From 2008 he trades that combination with the linear mean-reversion rule
of Example 2.8, holding minus its 5-day z-score in dollars.

**Every figure the script prints reproduces on Chan's own files, to every
digit it prints, with his own signs on the eigenvectors.** The screen passes
98 stocks, and the APR and Sharpe ratio land at 0.044930 and 1.319397. The
prose claim that the basket cointegrates with SPY at better than 95 percent
holds for the trace test and fails for the eigen test, which the script's
own printout already shows.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdataohlcdaily_stocks_20120424/`, 497 members lifted
   from Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25,
   and `inputdata_etf/spy.csv`, lifted from `inputData_ETF.mat`, saved
   2012-04-10. Both are read for the close through `chan.series.load_panel`,
   and their 1,489 common days run from 2006-05-11 to 2012-04-09. The ETF file
   adjusts for dividends by subtracting them in dollars, which
   [data/README.md](../data/README.md) records. The second Johansen test runs
   on log prices, where a subtracted dividend and a rescaled one differ, so
   that property is part of the input this entry reproduces.
2. **The specification.** `indexArb.m`, git blob `dcb079a`, at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview).
   Training is 2007, 251 days, and the test is every later day, 1,076 of them.
   The screen runs jplv7's `johansen(·, 0, 1)`, a constant and one lagged
   difference, on each stock's close and SPY's, in prices. A stock is tested
   only when more than 250 rows hold both, and it passes when the trace
   statistic for r ≤ 0 is above its 90 percent value. The basket is the sum of
   the passing stocks' log closes, tested against SPY's log close the same
   way. The strategy holds each instrument's eigenvector weight times minus
   the 5-day z-score in dollars, earns yesterday's dollars times today's
   change in log price, and divides by yesterday's gross. The APR is
   `prod(1 + r)^(252 / n) − 1` and the Sharpe ratio is `√252 · mean / std`
   over all 1,076 test days, with no risk-free rate and no cost.
   `chan.johansen.johansen` runs both tests.

Every result here is **exploratory** and **survivor-only**. Reproducing
Chan's figures spends the 2007 to 2012 sample on a rule he chose. The panel is
the index as he held it on 2012-04-24, so the 2007 screen picks only from
stocks that survived to 2012. The stocks and weights come from 2007 and trade
from 2008, but location 2035 says the lookback of 5 was fixed "with the
benefit of hindsight", so the APR and Sharpe ratio are not out-of-sample
figures.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The test window | January 2, 2008, to April 9, 2012 | location 2035 |
| 2 | Stocks passing the screen | 98 | script line 35, location 2035 |
| 3 | Basket trace statistics, r ≤ 0 and r ≤ 1 | 15.869 and 6.197 | script lines 50 and 51 |
| 4 | Basket eigen statistics | 9.671 and 6.197 | script lines 54 and 55 |
| 5 | The basket cointegrates with SPY at better than 95 percent | a claim | location 2035 |
| 6 | Two cointegrating relations | a claim | location 2035 |
| 7 | The basket test's eigenvectors | 1.0939 and −0.2799 over −105.5600 and 56.0933 | script lines 61 and 62 |
| 8 | The strategy's APR | 0.044930, "4.5 percent" | script line 83, location 2035 |
| 9 | The strategy's Sharpe ratio | 1.319397, "1.3" | the same |
| 10 | The stocks tested and skipped | none | n/a |
| 11 | A plain ADF test of each 2007 log series | none | n/a |
| 12 | The first day the strategy earns, and how many days it does | none | n/a |
| 13 | The returns under a zero-padded `lag` | none | n/a |
| 14 | The basket's stocks carrying a flagged scale-break day | none | n/a |
| 15 | The screen's pass rate on random walks unrelated to SPY | none | n/a |
| 16 | The trace test's rejection rate on two unrelated random walks | none | n/a |

The critical values are pinned beside rows 3 and 4, at the three decimals
the script prints. They come from statsmodels, which carries LeSage's tables.

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | Every common day after 2007-12-31 | 2008-01-02 to 2012-04-09, 1,076 days | `TestRow1TheWindows::test_row_1_the_test_window_is_the_books` |
| 2 | The screen over 2007 | 98 | `TestRow2TheScreen::test_row_2_98_stocks_pass` |
| 3 | `johansen([basket, log SPY], 0, 1)` | 15.868648 and 6.197357 | `TestTheBasketTest::test_row_3_the_trace_statistics` |
| 4 | The same | 9.671291 and 6.197357 | `TestTheBasketTest::test_row_4_the_eigen_statistics` |
| 5 | Each test's r ≤ 0 statistic against its 95 percent value | the trace's 15.869 past 15.494 by 0.374, the eigen's 9.671 short of even 12.297 at 90 percent | `TestTheClaims::test_row_5_the_trace_rejects_r_le_0_at_95` and `::test_row_5_the_eigen_does_not_reject_r_le_0_even_at_90` |
| 6 | Nulls rejected in order at 95 percent, up to the first that is not | 2 by the trace test and 0 by the eigen test | `TestTheClaims::test_row_6_the_trace_counts_two_relations_at_95` and `::test_row_6_the_eigen_counts_none_at_any_level` |
| 7 | The same test as row 3 | 1.09386171 and −0.27989806 over −105.55999232 and 56.09328286 | `TestTheBasketTest::test_row_7_the_eigenvectors_are_chans_with_his_signs` |
| 8 | A lookback of 5, the script's lines 70 to 77 | 0.0449298745 | `TestTheStrategy::test_row_8_the_apr` |
| 9 | The same | 1.3193972970 | `TestTheStrategy::test_row_9_the_sharpe_ratio` |
| 10 | The screen's rule on 497 stocks | 480 tested at a per-test 90 percent bar, 17 skipped | `TestRow2TheScreen::test_480_are_tested` and `::test_the_17_skipped_are_the_11_with_no_2007_close_and_6_listed_during_it` |
| 11 | ADF with a constant and one lag, against MacKinnon's −2.57 at 90 percent | −2.461086 for the basket and −2.381322 for SPY | `TestBesideTheReplication::test_neither_2007_log_series_rejects_a_unit_root_even_at_90` |
| 12 | The first non-zero day of row 8's returns | 2008-01-09, the sixth test day, and 1,071 days from there on | `TestTheStrategy::test_the_first_return_is_on_the_sixth_test_row_and_every_later_day_has_one` |
| 13 | LeSage's `lag`, which pads with zero, in place of `backshift` | the same returns to 10⁻¹⁵, and the same days at zero | `TestTheStrategy::test_zero_padding_the_lag_as_lesage_does_gives_the_same_series` |
| 14 | `scale_breaks` on each of the 98 | CVH, MOS, PNC and STT, every flag in the test window | `TestTheScaleBreakDecision::test_four_of_the_baskets_stocks_carry_a_flag_all_in_the_test` |
| 15 | The screen on 2,000 Gaussian random walks with no drift, seeded with 343, against SPY's 2007 closes | 561 pass, 28 percent, about 135 of 480 | `TestBesideTheReplication::test_the_screen_passes_561_of_2000_walks_unrelated_to_spy` |
| 16 | `johansen(·, 0, 1)` on 2,000 pairs of such walks, seeded with 345 | r ≤ 0 rejected on 410 at the 90 percent value and 242 at the 95, 20.5 and 12.1 percent | `TestBesideTheReplication::test_the_trace_test_rejects_two_to_three_times_its_nominal_rate_on_unrelated_walks` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, dates | reproduced | Exact. |
| 2 | 0 | reproduced | Exact. Chan's 98 are not named anywhere, so this run cannot say they are the same 98, only that the rule picks 98. |
| 3 | 0.000 on each | reproduced | Exact. |
| 4 | 0.000 on each | reproduced | Exact. |
| 5 | none, a claim | reproduced by the trace test, did not reproduce by the eigen test | The trace statistic clears its 95 percent bar by 0.374. The eigen statistic falls short of even its 90 percent bar. Location 2035 names no statistic, so each is read on its own, as the criterion on the issue set out. |
| 6 | none, a claim | reproduced by the trace test, did not reproduce by the eigen test | The trace test rejects r ≤ 0 and r ≤ 1 at 95 percent. The eigen test stops at r ≤ 0. What two relations between two series means is the subject of the third conclusion below. |
| 7 | 0.0000 on each | reproduced | Exact at the four decimals printed, with Chan's signs. statsmodels makes the top-left element positive, and his 1.0939 already is. |
| 8 | 0.000000, and 0.0 at the book's one decimal of a percent | reproduced | Exact. |
| 9 | 0.000000, and 0.0 at the book's one decimal | reproduced | Exact. |
| 10 | none | none, not a replication | Eleven stocks have no 2007 close and six listed during it. |
| 11 | none | none, not a replication | Neither series rejects a unit root on its own, which is what row 6's reading turns on. |
| 12 | none | none, not a replication | The moving deviation first fills on the fifth test day, so positions first earn on the sixth. |
| 13 | none | none, not a replication | Under either pad the first five test days are not a number and become 0. |
| 14 | none | none, not a replication | `indexArb.m` ran across these days as they stand, and the guard on SPY passes. |
| 15 | none | none, not a replication | More walks pass than the 98 stocks do, so the screen's count does not by itself show cointegration. |
| 16 | none | none, not a replication | The test with a constant rejects two to three times its nominal rate on walks with no drift, so a pass at either bar is weaker evidence than its label. |

### What the entry concludes

Four things.

1. **The script reproduces on Chan's own files.** Every number `indexArb.m`
   prints lands to its last digit, and the eigenvectors come back with his
   signs, so the entry has nothing to say about the data. Rows 5 and 6 are
   the exception, and the evidence against their eigen halves is the
   printout that sits beside the example.
2. **The screen's 98 is a count of tests passed, and no more than chance
   gives.** The script tests 480 stocks at a per-test 90 percent bar, whose
   nominal rate would put about 48 passes down to chance. The test does not
   hold that rate. Row 16 shows the trace test with a constant rejecting 20.5
   percent of pairs of unrelated walks at its 90 percent value, and row 15
   shows the screen passing 28 percent of such walks against SPY's own 2007
   closes, about 135 of 480. The 98 stocks are fewer than that. Gaussian walks
   with no drift are not stocks, so this does not say none of the 98
   cointegrates with SPY. It says the count is no evidence that any does. No
   false-discovery control is computed, because `coint_johansen` returns no
   p-values to read.
3. **The basket's two relations make the same claim Entry 23's pair did.**
   Location 2035 reads two relations as a second portfolio Chan chose not to
   use. A Johansen rank of 2 between two series says every combination is
   stationary, including the basket and SPY each on its own around a
   constant. Row 11 sits in tension with that. Neither rejects a unit root on
   its own, at −2.46 and −2.38 against −2.57. A plain ADF over 251 days has
   little power, so this is weak evidence rather than proof. The eigen test,
   which finds no relation at all, does not support the full rank either, and
   row 16 shows the trace test rejecting 12.1 percent of unrelated pairs at
   its 95 percent value, so row 5's trace pass is weaker than its label.
4. **The 4.5 percent is in-sample on its lookback and survivor-only.** The
   stocks and weights are fitted on 2007 and traded on 2008 to 2012, which
   looks out-of-sample. Location 2035 says the lookback of 5 was chosen with
   hindsight, so it was not, and the screen picks only from stocks that
   survived to 2012. Nothing here measures how much either is worth.

### What this entry cannot say

Four things.

**Which stocks cointegrate with SPY.** Conclusion 2 is why. Rows 15 and 16
size the test on walks with no drift, which is enough to retire 48 and not
enough to judge a stock. A screen with a false-discovery control, or one judged
against a null built from real prices, is a search this repo would be running,
so it needs a hypothesis written before its run, data it never loads, and its
own issue.

**Whether the strategy works with another lookback or with retraining.**
Location 2035 suggests retraining the basket periodically. Each variant is a
search too, for the same reason.

**Anything about costs.** The rule rebalances 99 positions every day, and no
cost is charged here, as none is in the script.

**How much survivorship bias is worth.** No panel here holds the S&P 500's
2007 members with the ones that later left, so the screen cannot be run on
the index as it stood.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/index-arbitrage-lessons.md](../blog/index-arbitrage-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.index_arbitrage_figures` redraws.

## Entry 25: AUD.USD against CAD.USD, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 5.1, Kindle locations 2186 to 2237, and the
script `AUDCAD_unequal.m` the example names. Shipped under
[issue 345](https://github.com/l3a0/quantitative-trading/issues/345). Every
example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seven rows, all derivable from
[tests/test_aud_cad_johansen.py](../tests/test_aud_cad_johansen.py).

Chan trades the Australian dollar against the Canadian dollar, two commodity
currencies he expects to move together. Both are quoted against the US dollar,
as AUD.USD and CAD.USD, so a point move in either is worth the same in
dollars. That is why USD.CAD is inverted before the test. Each day the script runs the test on the 250 days before it, takes the first
eigenvector as that day's hedge, and holds minus the portfolio's 20-day
z-score in units of it. The return is the day's profit over the capital held
the day before.

**Every figure reproduces, because the run reproduces Chan's own saved returns
on every one of the 612 days.** Chan's script saved the
returns it traded, and that file is committed. The criterion for comparing
them was written on the issue before any return was computed. So the match
says the committed daily files agree with the inputs the MATLAB read, up to a
constant scale on each leg, which
[issue 301](https://github.com/l3a0/quantitative-trading/issues/301) could not
check because the `.mat` files are in neither mirror.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `pythoncodesanddata/inputData_AUDUSD_20120426.csv` and
   `pythoncodesanddata/inputData_USDCAD_20120426.csv`, from Chan's 2018 Python
   port, saved 2018-12-12, 862 days from 2009-01-02 to 2012-04-26, as traded,
   read through `chan.series.load_port_close`. Row 5 also reads
   `pythoncodesanddata/AUDCAD_unequal_ret.csv`, the 612 returns the MATLAB
   saved, saved 2018-12-26, through `chan.series.load_returns`.
2. **The specification.** `AUDCAD_unequal.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `5b8fbc2`. The legs are AUD.USD and the inverse of USD.CAD. Each
   day's hedge is the first eigenvector of jplv7's `johansen(·, 0, 1)`, a
   constant and one lagged difference, on the 250 rows before the day, run by
   `chan.johansen.johansen`. The units are minus the z-score of the portfolio
   over the 20 rows ending on the day, with the n − 1 deviation. The return is
   yesterday's positions times today's simple returns, summed, over yesterday's
   gross. The figures are taken over the 612 days from 2009-12-18 on: the APR
   is `prod(1 + r)^(252 / 612) − 1`, the Sharpe ratio is `√252 · mean / std`,
   and the Kelly leverage is `mean / std²`, with no risk-free rate, no cost and
   no rollover interest.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2009 to 2012 sample on a rule he chose, and location 2237 says the 250-day
training length "gives better results in hindsight".

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The test window | 2009-12-18 to 2012-04-26, after the first 250 days | location 2237 |
| 2 | Compounded APR | 0.112410, "11 percent" | script line 60, location 2237 |
| 3 | Sharpe ratio | 1.610890, "1.6" | the same |
| 4 | Kelly leverage, `mean / std²` | 23.845328 | script line 66 |
| 5 | The 612 returns equal Chan's saved ones | `AUDCAD_unequal_ret.csv`, no printed figure | script line 69 |
| 6 | How many training windows each Johansen statistic finds a relation in, at 95 percent | none | n/a |
| 7 | The last day's hedge, with AUD.USD's weight scaled to 1 | none | n/a |

Location 3342 gives a Kelly leverage of 18.4 for this strategy. Row 4 is the
script's own 23.845328 instead, because neither the population variance nor
the mean of squared returns takes the saved series to 18.4.
[Issue 360](https://github.com/l3a0/quantitative-trading/issues/360) owns that
figure.

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | Rows 251 to 862 of the two daily files | 612 returns, 2009-12-18 to 2012-04-26 | `TestRow1TheTestWindow::test_612_returns_from_the_books_first_day_to_its_last` |
| 2 | Over row 1's returns | 0.1124100634 | `TestRows2To4TheFigures::test_row_2_the_apr` |
| 3 | The same | 1.6108902337 | `TestRows2To4TheFigures::test_row_3_the_sharpe_ratio` |
| 4 | The same | 23.8453277641 | `TestRows2To4TheFigures::test_row_4_the_kelly_leverage` |
| 5 | Each return against Chan's on the same row, criterion 1e-9 | no row over it | `TestRow5TheReturnsAreChans::test_every_row_agrees_within_the_declared_criterion` |
| 6 | `Johansen.relations` on each of the 612 windows | the trace test in 26, two relations in 19 of them, and the eigen test in 11 | `TestBesideTheReplication::test_the_trace_test_finds_a_relation_in_26_of_612_windows` and `::test_the_eigen_test_finds_one_in_11` |
| 7 | The eigenvector of 2012-04-26 over its first element, and that day's positions over the first | 1 unit of AUD.USD to −0.7796733233 of CAD.USD, and in dollars 1 to −0.7622442800 | `TestBesideTheReplication::test_the_last_days_hedge_holds_0_7797_of_cad_per_aud_short` |

Row 5's largest difference is printed by the run rather than pinned, because
it is rounding and moves with the platform. On the machine that built the
entry it was 2.0e-15.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, a window | reproduced | The first test day is row 251 of the files, 2009-12-18, and the last is their last, as location 2237 says. |
| 2 | 0.000000, and 0 at the book's whole percent | reproduced | Row 5 holds, and Chan's saved returns give 0.112410 themselves. |
| 3 | 0.000000, and 0.0 at the book's one decimal | reproduced | The same. |
| 4 | 0.000000 | reproduced | The same. The n − 1 variance matters here: the population form gives 23.884354. |
| 5 | none | none, not a replication | No source prints it. It is the evidence rows 2 to 4 cite, and it holds on every row. |
| 6 | none | none, not a replication | The script trades every window whether or not either test finds a relation. |
| 7 | none | none, not a replication | The weights count units, and a unit is worth its quote in dollars, so the split in capital is each weight times its quote. The strategy ended long AUD and short 0.7622 dollars of CAD for each dollar of AUD. |

### What the entry concludes

Three things.

1. **The committed currency files agree with the ones Chan's MATLAB read,
   up to a constant scale on each leg.** The script loaded two minute `.mat`
   files that neither mirror carries, and this run read the Python port's daily
   copies. Every one of the 612 returns lands on the one Chan saved, inside the
   1e-9 declared before the run, and the largest difference was 2.0e-15 where
   the entry was built. Two things bound what that shows, and
   `TestRow5TheReturnsAreChans` holds both.
   1. Scaling either leg by a constant moves no return, because a simple
      return ignores the scale and the eigenvector rescales to cancel it.
   2. A change of 1e-6, one unit in the files' last decimal, on a close in
      the test window breaks the match, because the close enters a simple
      return directly. The same change on the first training row does not,
      because that close reaches the returns only through the hedge.

   So the match answers the question
   [issue 301](https://github.com/l3a0/quantitative-trading/issues/301) left
   open for these two files. It says nothing about the port's USD.CAD minute
   file or its AUD.CAD file, which this script does not read.
2. **The hedge was rarely one the Johansen test backed.** The trace test finds
   a relation in 26 of the 612 training windows and the eigen test in 11. In
   19 of those 26, the trace test finds two relations, which the test reads as
   each currency being stationary on its own rather than the two sharing one.
   That is a 95 percent rejection on overlapping windows of two rates close to
   random walks, so it is weak evidence either way. So on nearly
   every day the strategy traded an eigenvector of a pair the test did not call
   cointegrated. Chan's rule never asks, and the figures are the rule's.
3. **The Python port's version of this example is a different strategy.** It
   ends the Johansen window and the z-score window a day earlier, and
   [issue 301](https://github.com/l3a0/quantitative-trading/issues/301)
   recorded that it prints a Sharpe ratio of 1.362926, which no test here
   pins. Ending both windows a day earlier here leaves 611 of the 612 returns
   over the criterion, every one but the first, which is 0 either way. Its
   Sharpe ratio is 1.359568, not the port's 1.362926, so the port differs in
   more than the windows and nothing here reproduces its printout.
   `TestTheRule::test_ending_both_windows_a_day_earlier_breaks_row_5` holds
   both. So the port's printout is no evidence about the data, and the MATLAB
   is the specification.

### What this entry cannot say

Four things.

**Anything about costs or rollover interest.** The rule trades every day, and
no cost is charged, as none is in the script. Location 2205 sets rollover
interest aside for this example as small for a short-term strategy, and
nothing here measures how small.

**Whether the 250-day training length was chosen on this sample.** Location
2237 says it gives better results in hindsight. No row runs another length, and
any that did would be searching the sample this entry already spent.

**Whether the pair trades today.** The run ends on 2012-04-26 with Chan's
data. It says whether his numbers reproduce on his files and nothing about the
two currencies since.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/aud-cad-johansen-lessons.md](../blog/aud-cad-johansen-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.aud_cad_johansen_figures` redraws.

## Entry 26: Bollinger bands on GLD and USO, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 3.2, Kindle locations 1548 to 1559, and the
script `bollinger.m` the example names. Shipped under
[issue 341](https://github.com/l3a0/quantitative-trading/issues/341). The
location numbers are that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seven rows, all derivable from
[tests/test_bollinger.py](../tests/test_bollinger.py).

**Both figures `bollinger.m` prints reproduce to six digits on Chan's own
file, and the band beats Example 3.1's linear rule on both.** Entry 21's linear
rule holds minus the spread's z-score in units of the pair every day, so it is
always in the market. Example 3.2 trades the same GLD and USO price spread with
a Bollinger band instead. It buys one unit when the z-score falls below −1,
sells one short when it rises above 1, and holds either until the z-score
crosses back through 0. On days with no signal it carries yesterday's units
forward. Location 1559 reports an APR of 17.8 percent and a Sharpe ratio of
0.96, "quite an improvement" on the linear rule.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** Entry 21's: `inputdata_etf/gld.csv` and
   `inputdata_etf/uso.csv`, two of the 67 ETFs of Chan's `inputData_ETF.mat`,
   saved 2012-04-10, read through `chan.series.load_panel`, 1,500 days from
   2006-04-26 to 2012-04-09. The scale-break guard runs on both legs and
   refuses nothing.
2. **The specification.** `bollinger.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `6d80817`, the same blob as in ivanliu1989/algorithmic_trading at
   `4567024`, with `fillMissingData.m` at `88632fc` in both. Everything up to
   the units is Entry 21's price spread: the 20-row rolling hedge ratio, the
   first 20 rows dropped, leaving 1,480 from 2006-05-24, and the 20-row
   z-score from `movingAvg` and `movingStd`, MATLAB's n − 1 `std`. A long
   enters below −1 and exits above 0, and a short enters above 1 and exits
   below 0. Each side starts at 0 and `fillMissingData` carries its last value
   over every row with no signal. One unit holds `[−h·GLD, USO]` dollars. The
   return, the APR and the Sharpe ratio are Entry 21's, and no cost is
   charged.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 to 2012 sample on a rule he chose, with a lookback Entry 21 records he
tuned with "the benefit of hindsight", so the entry says whether his numbers
reproduce on his file and nothing about whether the rule pays today.

### What the book printed

The script closes on a comment holding the six decimals its
`fprintf('APR=%f Sharpe=%f')` prints, and location 1559 rounds both.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | APR | 0.178249, and "17.8 percent" | `bollinger.m`, location 1559 |
| 2 | Sharpe ratio | 0.964673, and "0.96" | `bollinger.m`, location 1559 |
| 3 | The band improves on the linear rule | "quite an improvement", a claim | location 1559 |
| 4 to 7 | the divisor, the first position, the `lag` padding and the band at its edges | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + ret)^(252/1480) − 1` | 0.178249 | `TestTheFigures::test_the_apr_is_chans_0_178249` |
| 2 | `√252 · mean(ret) / std(ret)` | 0.964673 | `TestTheFigures::test_the_sharpe_ratio_is_chans_0_964673` |
| 3 | rows 1 and 2 against Entry 21's rows 1 and 2, 0.108335 and 0.589651 | both higher, by +0.069915 and +0.375022 | `TestTheClaim` |
| 4 | rows 1 and 2 with `smartMovingStd`, which divides by n, in place of `movingStd` | 0.183306 and 0.984872, moved by +0.005057 and +0.020199 | `TestTheDivisor` |
| 5 | the first day with units, and the first day a return is earned | 2006-06-21 and 2006-06-22 | `TestTheFigures::test_the_first_position_is_held_into_2006_06_22` |
| 6 | the run with `lag` padding 0 rather than NaN | the same returns, exactly | `TestWhatMovesNothing` |
| 7 | the units on synthetic arrays: a z-score of exactly −1 or 1, exactly 0, NaN, and a long turning short in one day | enters nothing, exits nothing, holds yesterday's units, and turns in one day | `TestBandUnits` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.000000 against the script, 0.0 against the book | reproduced | Chan's figure, on his own file, through his own script transcribed. The book's 17.8 percent is the script's figure rounded, unlike Entry 21's 10.9. |
| 2 | 0.000000 against the script, 0.00 against the book | reproduced | The same as row 1. |
| 3 | none, a claim | reproduced | The APR and the Sharpe ratio are both above the linear rule's on the same spread. The criterion was written on [issue 341](https://github.com/l3a0/quantitative-trading/issues/341) after a first transcription ran, as Entry 21's rows 7 and 8 were, and reads the sentence's comparison on the two figures the book prints. |
| 4 | none | none, not a replication | `bollinger.m` calls `movingStd`, so n − 1 is the transcription. Entry 21's linear rule could not see the divisor, because a constant on every unit cancels out of profit over gross dollars. This rule compares the z-score with a fixed threshold, so the scale decides which days trade, and both figures move. |
| 5 | none | none, not a replication | `movingStd` first fills on the 20th kept row, and the band enters there, so the run holds its first position into 2006-06-22, the same days as Entry 21's row 10. |
| 6 | none | none, not a replication | Neither mirror holds `lag.m`. A NaN pad makes the first row's return NaN. A zero pad divides by a price of 0, so the first row's profit is NaN over zero gross dollars, and either NaN is set to 0. |
| 7 | none | none, not a replication | No kept row of the real data has a z-score of exactly −1, 0 or 1, which `TestTheFigures::test_no_kept_row_sits_exactly_on_a_band` holds, so only synthetic arrays reach the edges of the band. |

### What the entry concludes

Three things.

1. **Example 3.2 reproduces exactly on Chan's own file.** Both figures the
   script prints land to six digits, and the book's 17.8 percent and 0.96 are
   those figures rounded.
2. **The band beats the linear rule on this sample, by both measures the book
   names.** The APR rises from 0.108335 to 0.178249 and the Sharpe ratio from
   0.589651 to 0.964673. The two rules trade the same spread with the same
   lookback, so the difference is the rule alone. Both share a lookback
   tuned on this sample, so the comparison is between two in-sample figures.
3. **The divisor of the moving deviation matters here, where it did not for
   Entry 21.** Dividing by n rather than n − 1 shrinks the deviation, so the
   z-score is larger and sits beyond ±1 on more days. The APR moves by
   +0.005057 and the Sharpe ratio by +0.020199, so the book's 17.8 percent
   and 0.96 would read 18.3 and 0.98. This answers the question Entry 21's
   third conclusion left open: a rule with a fixed threshold needs the
   divisor its script used, and a port reaching for `smartMovingStd` would
   miss.

### What this entry cannot say

Four things.

**Whether the reversion is real.** Entry 21's "What this entry cannot say"
holds unchanged, because this run trades the same spread. GLD and USO do not
cointegrate on this file, and the 20-day hedge ratio changes sign.

**What costs would take.** No script charges any. The band's units change on
162 of the 1,480 days, which `TestTheSpecification` holds, against every day
for the linear rule. That understates how often the band trades, because a
held unit's GLD leg is resized every day as the hedge ratio is refitted.
Nothing here measures what a cost per trade would take from either rule.

**Whether 1, 0 and 20 were fair choices.** Location 1548 calls the entry
threshold and the lookback free parameters to be optimized on a training set.
Location 1559 sets the thresholds without saying how they were chosen, and the
lookback is the one Entry 21 records Chan tuned on this sample. Every figure
above is in-sample.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/bollinger-band-lessons.md](../blog/bollinger-band-lessons.md) moves with
it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.bollinger_figures` redraws.

## Entry 27: spot and roll returns of five futures, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 5.3, Kindle locations 2364 to 2444, with
Table 5.1 recalled at 2683. Shipped under
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347). The
script is `estimateFuturesReturns.m`, in ericnberwick/EpchanPreview at
`e4bc46f` under `public/img/book2/`, git blob `1a70a28`. Every location in
this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eighteen rows, all derivable from
[tests/test_roll_returns.py](../tests/test_roll_returns.py). Five do not match
one printed figure to one computation, and each says so in its own cells. Row
12 covers two figures from one computation, and rows 15 to 18 carry no
published figure.

A future's return splits into the move of the spot price under it and the
return it earns by converging on that spot as it nears expiry, the roll return.
Chan assumes both are constant and estimates each by regression, for the
Brazilian real (BR), corn (C), WTI crude (CL), copper (HG) and the two-year
Treasury note (TU). The spot return α is the slope of the log spot price on
time. The roll return γ comes from one day's forward curve: the log prices of
the five nearest contracts regressed on their time to maturity, fitted afresh
each day. Chapter 6 uses the result to explain why BR, HG and TU trend.

**Eight of Table 5.1's ten cells reproduce on Chan's own files, and HG's and
TU's spot returns do not.** CL's γ starts on Figure 5.5's first day, and C's
two figures agree with the ones Chan's Python port prints to within 10⁻¹².
Separately, the script measures maturity in contract columns rather than
months, which overstates the roll return of the three strips whose contracts
are not one month apart.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** The five strips `inputdatadaily_br_20120813/`,
   `inputdatadaily_c2_20120813/`, `inputdatadaily_cl_20120813/`,
   `inputdatadaily_hg_20120813/` and `inputdatadaily_tu_20120813/`, vendor
   `chan-mat`, basis `raw`, saved 2012-08-14, one vintage per contract and
   one for the spot, read for the close through `chan.series.load_panel`.
   Table 5.1's C is the C2 strip.
2. **The specification.** α is 252 times the OLS slope of the log spot on the
   strip's row number. The rows are numbered over every day of the file before
   the days with no spot are dropped, so a gap still counts as elapsed days. γ
   is −12 times the OLS slope of the five nearest priced contracts' log prices
   on their column positions 1 to 5, on rows where those five are adjacent
   columns, and the figure is its mean over the rows where it is defined.

Every result here is **exploratory**. Reproducing Table 5.1 spends Chan's 1986
to 2012 strips on a model he chose, so it says whether his numbers reproduce on
his file and nothing about whether a roll return persists out of sample.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | BR, α | −2.7% | location 2399, Table 5.1 |
| 2 | BR, γ | 10.8% | the same |
| 3 | C, α | 2.8% | the same, and location 2444 |
| 4 | C, γ | −12.8% | the same, and location 2444 |
| 5 | CL, α | 7.3% | location 2399, Table 5.1 |
| 6 | CL, γ | −7.1% | the same |
| 7 | HG, α | 5.0% | the same |
| 8 | HG, γ | 7.7% | the same |
| 9 | TU, α | −0.0%, a negative number that rounds to zero | the same |
| 10 | TU, γ | 3.2% | the same |
| 11 | CL's first day with γ | November 22, 2004 | location 2399, Figure 5.5 |
| 12 | C's α and γ in full | `0.02805562210100287` and `-0.12775650227459556` | the Python port's comments, not the book |
| 13 | For BR, C and TU, \|γ\| is much larger than \|α\| | a claim | location 2399 |
| 14 | BR, HG and TU each have \|γ\| bigger than \|α\| | a claim | location 2683 |
| 15 | γ with maturity in months | none | n/a |
| 16 | Rows 13 and 14 on the month-spaced γ | none | n/a |
| 17 | The month gaps across the five contracts each day's γ reads | none | n/a |
| 18 | The days with γ and their span | none | n/a |

Row 12's port is `estimateFuturesReturns.py` in `PythonCodesAndData.zip` at
the same commit, the zip [data/README.md](../data/README.md) records with its
sha256. Its rule is the MATLAB script's.

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | α on the BR strip | −0.026903 | `TestTheFigures::test_alpha_and_gamma_at_the_six_decimals_the_script_prints` |
| 2 | γ on the BR strip | 0.108133 | the same |
| 3 | α on the C2 strip | 0.028056 | the same |
| 4 | γ on the C2 strip | −0.127757 | the same |
| 5 | α on the CL strip | 0.073019 | the same |
| 6 | γ on the CL strip | −0.070592 | the same |
| 7 | α on the HG strip | 0.050567 | the same, and `TestTheFigures::test_hgs_alpha_rounds_to_5_1_not_the_printed_5_0` |
| 8 | γ on the HG strip | 0.077172 | `TestTheFigures::test_alpha_and_gamma_at_the_six_decimals_the_script_prints` |
| 9 | α on the TU strip | 0.000039, positive | the same, and `TestTheFigures::test_tus_alpha_is_positive_where_the_book_prints_a_negative_zero` |
| 10 | γ on the TU strip | 0.032032 | `TestTheFigures::test_alpha_and_gamma_at_the_six_decimals_the_script_prints` |
| 11 | CL's first and last day with γ | 2004-11-22 to 2012-08-13 | `TestTheFigures::test_cls_first_day_with_gamma_is_figure_5_5s_first_day` |
| 12 | Rows 3 and 4 against the port | within 10⁻¹² of each | `TestTheFigures::test_c_agrees_with_the_python_ports_printed_figures` |
| 13 | \|γ\| at least twice \|α\| | holds for all three, the narrowest BR at 4.02 times | `TestTheClaims::test_br_c_and_tu_each_have_a_roll_return_at_least_twice_their_spot_return` |
| 14 | \|γ\| greater than \|α\| | holds for all three | `TestTheClaims::test_br_hg_and_tu_each_have_a_roll_return_bigger_than_their_spot_return` |
| 15 | The same fit regressed on each contract's month offset from the nearest | BR 0.108133, C −0.053011, CL −0.070592, HG 0.038573 and TU 0.010677, so the script's γ is 2.4 times C's, 2.0 times HG's and 3.0 times TU's | `TestTheRowsBeside::test_gamma_with_maturity_in_months` and `::test_the_script_overstates_c_by_2_4_hg_by_2_0_and_tu_by_3_0` |
| 16 | Rows 13's and 14's criteria on row 15 | row 13's holds for BR and TU and fails for C, at 1.89 times. Row 14's holds for BR and TU and fails for HG | `TestTheRowsBeside::test_location_2399_fails_for_c_on_the_month_spaced_gamma` and `::test_location_2683_fails_for_hg_on_the_month_spaced_gamma` |
| 17 | Each row's gaps in months across its five contracts | all one month for BR and CL, all three for TU, five patterns for C and six for HG | `TestTheRowsBeside::test_the_spacings_each_strips_gamma_reads` |
| 18 | Rows where γ is defined | BR 4,210 from 1995-11-09, CL 1,941 from 2004-11-22, HG 6,028 from 1986-11-03 and TU 1,087 from 2008-03-10, all four to 2012-08-13, and C 1,570 from 2005-12-19 to 2012-03-14 | `TestTheRowsBeside::test_the_days_with_gamma_and_their_span` and `::test_cs_gamma_stops_when_its_strip_runs_out_of_contracts` |

`TestTheFigures::test_eight_of_table_5_1s_ten_cells_land_and_hg_and_tu_alpha_miss`
holds which of rows 1 to 10 round to the book's figure, sign included.

### The verdicts

Rows 1 to 10 are compared at the book's one decimal of a percent, so each gap is
in percentage points at that precision.

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0 | reproduced | −2.69 percent rounds to −2.7. |
| 2 | 0.0 | reproduced | |
| 3 | 0.0 | reproduced | |
| 4 | 0.0 | reproduced | |
| 5 | 0.0 | reproduced | |
| 6 | 0.0 | reproduced | −7.06 percent rounds to −7.1. |
| 7 | +0.1 | did not reproduce | 5.06 percent rounds to 5.1, on Chan's own saved file, so the vintage explanation is spent. Three readings were tried after the miss, and `TestTheReadingsTriedAfterTheMiss` pins each. Renumbering the rows after the spot's gaps are dropped gives 0.050587, and reading the prices at single precision gives 0.050567. Regressing on calendar days and annualizing by 365 gives 0.050315, which lands the cell. The specification stays the row number. The script reads `T=[1:length(spot)]'`, and the calendar-day reading moves C's α to 0.027998, off the 0.028056 the Python port printed, which the row number lands. |
| 8 | 0.0 | reproduced | |
| 9 | 0.0, with the opposite sign | did not reproduce | 0.0039 percent rounds to 0.0, but the book's −0.0 is a negative number and this one is positive. None of the three readings in row 7 turns it negative. |
| 10 | 0.0 | reproduced | |
| 11 | 0 days | reproduced | Exact. |
| 12 | under 10⁻¹² on each | reproduced | The two programs sum in different orders, so the pin allows 10⁻¹². |
| 13 | none, a claim | reproduced | The criterion, \|γ\| at least twice \|α\|, was written before the build but after a scratch run had measured the figures. BR is the narrowest at 4.02 times, so the verdict does not rest on where the line sits. Row 16 runs it on the month-spaced γ, and there it fails for C. |
| 14 | none, a claim | reproduced | It holds under the script's γ, which is what printed Table 5.1. Row 16 is the same claim under the book's own description of the method, and there it fails for HG. |
| 15 | none | none, not a replication | No figure is printed for it. Monthly strips give the same γ either way, to rounding. |
| 16 | none | none, not a replication | C's month-spaced γ is less than twice its α, and HG's is smaller than its α. [Issue 347](https://github.com/l3a0/quantitative-trading/issues/347) declared only row 14's criterion for this γ. Row 13's was added at the build, after the figures were seen, which is one more reason the row carries no verdict. |
| 17 | none | none, not a replication | It is why rows 15 and 16 move only C, HG and TU. |
| 18 | none | none, not a replication | γ needs five priced contracts. C's strip ends at 2012Z, so after its March 2012 contract expires no day prices more than four. |

### What the entry concludes

Three things.

1. **The table reproduces on Chan's own files except for two spot returns.**
   C's two figures agree with what his Python port printed on the same strip,
   CL's γ starts on the day his figure does, and eight of ten cells land at the
   book's precision. HG's and TU's α miss on Chan's own file, so no vintage
   explanation is left. The one reading that lands HG, regression on calendar
   days, is not what the mirrored script or the Python port computes. HG's
   miss is one tenth of a point and TU's is a sign, so neither changes what
   the table is used to argue.
2. **The script measures maturity in columns, so three of its five γ figures
   are not what the text describes.** The book says the fit regresses on time
   to maturity "measured in months". The script regresses on 1 to 5 and
   annualizes as if adjacent contracts were a month apart. That holds for BR
   and CL. C's contracts sit two or three months apart, HG's mix gaps of one,
   two and three months, and TU's sit three apart, so Table 5.1 overstates
   their roll returns by 2.4, 2.0 and 3.0
   times.
3. **Under months, both claims lose a strip.** Location 2683 explains BR's,
   HG's and TU's momentum by their roll returns exceeding their spot returns.
   HG's month-spaced roll return, 3.86 percent, is smaller than its 5.06
   percent spot return, so the comparison Chapter 6 rests its HG explanation
   on holds only under the script's arithmetic. Location 2399's claim that
   BR's, C's and TU's roll returns are much larger than their spot returns
   holds for BR and TU either way. C's month-spaced roll return is 1.89 times
   its spot return, short of the criterion's 2. Neither row tests whether a
   roll return explains any momentum.

### What this entry cannot say

Four things.

**Whether returns are constant.** The model is the book's simplification, and
location 2399 already says the fitted γ drifts from day to day. A mean of a
drifting series is a summary, and this entry reproduces the summary without
testing the model.

**Whether the month-spaced γ is what Chan meant.** Rows 15 and 16 are this
repo's reading of the book's sentence, declared on
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347) before the
build.
Chan printed no figure for them, so they carry no verdict.

**Whether a roll return persists.** Every row is in-sample on 1986 to 2012.
The two experiments that trade on γ, Example 5.4 and the TU momentum test,
are Entries 34 and 36.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/roll-returns-lessons.md](../blog/roll-returns-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.roll_returns_figures` redraws.

## Entry 28: VX futures against E-mini futures, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle locations 2546 to 2559, and the script
`VX_ES.m` the example names. Shipped under
[issue 350](https://github.com/l3a0/quantitative-trading/issues/350). The
location numbers are that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from
[tests/test_vx_es.py](../tests/test_vx_es.py).

**Three of the four printed figures reproduce at the book's precision, and the
fourth misses by $2.09, on a save and an exit chosen because they land the
printed figures.** Volatility rises when stocks fall, so VX, the VIX future,
and ES, the E-mini S&P 500 future, should move against each other. Chan plots
one against the other and sees two regimes, 2004 to May 2008 and August 2008
to 2012. He regresses ES on VX over the second, with each price multiplied by
its dollars per point, so the slope counts contracts. He reports that a
portfolio long 0.3906 VX contracts and one ES contract should be stationary,
with a residual standard deviation of $2,047. He then trades it against one
training-set standard deviation and reports an APR of 12.3 percent and a
Sharpe ratio of 1.4 from July 29, 2010, to May 8, 2012.

The book names no exit, no training window and no save, and the script that
ships cannot be what produced its figures. `VX_ES.m` fits on every day from
2008-08-01 to the last day of a save made on 2012-05-17, so its fit includes
the whole test set, and it prints nothing and runs no trade. Row 10 runs it.
The run here takes three choices from elsewhere.

1. **The save.** A sweep on
   [issue 350](https://github.com/l3a0/quantitative-trading/issues/350) fitted
   every window starting between 2008-07-01 and 2008-10-31 and ending between
   2010-06-01 and 2010-09-30 on each of three saves, 22,446 windows in all.
   Exactly one rounds to both 0.3906 and $2,047, on the 2012-05-07 save,
   ending 2010-07-28, the day before the printed test begins. That save's last
   day is the book's last test day. The suite does not run the sweep, so these
   two counts are unpinned, and the issue records them.
2. **The training window.** Chan's own `VX_ES_rollreturn.m`, the script behind
   the roll-return trade that reuses this hedge, anchors at 2008-08-04 and
   tests from the 501st row on. The run fits on rows 1 to 500, which ends on
   2010-07-28 too.
3. **The exit.** A position is held until the opposite band, since that is
   the one rule tried that lands both the APR and the Sharpe ratio.

Every row reads one of three vintages and one of two specifications, so they
are stated once here.

1. **The vintages.** Three saves of Chan's continuous futures, each rolled
   from contract to contract and shifted at each roll, read for VX and ES
   through `chan.series.load_panel`. Each leg keeps its own calendar, so each
   is cut to its own rows and the two are intersected, as the script does.
   1. `inputdataohlcdaily_20120507/`, saved 2012-05-09, 1,999 common days
      from 2004-06-02 to 2012-05-08. Rows 1 to 8 and 11 read it.
   2. `inputdataohlcdaily_20120517/`, saved 2012-05-18, the save `VX_ES.m`
      loads, 1,999 common days from 2004-06-14 to 2012-05-17. Rows 9 and 10
      read it.
   3. `inputdataohlcdaily_20120511/`, saved 2012-05-12, read for row 9 only.

   The scale-break guard runs on each leg over its own span in every save the
   run reads, and refuses nothing.
2. **The specification.** `ols(50·ES, [1000·VX, 1])` on the first 500 common
   days on or after 2008-08-04, which are 2008-08-04 to 2010-07-28. The hedge
   is minus the slope, and the residual's standard deviation divides by
   n − 1. Each day from the anchor is scored as the portfolio less the
   intercept, over that deviation. `chan.bollinger.band_units` goes long one
   unit below −1 and short one unit above +1, and holds each until the
   opposite band. Each day's return is profit on yesterday's dollar positions
   over yesterday's gross dollars, measured on the 449 days from 2010-07-29 to
   2012-05-08, annualised over 252 days with no cost.
3. **The script as shipped.** `VX_ES.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `ca480c4`: the same regression on every common day from
   2008-08-01 to the save's end.

Every result here is **exploratory**, for two reasons. Reproducing Chan's
figures spends the 2008 to 2012 sample on a rule he chose. And the save and
the exit were each chosen because they land the printed figures, so the match
is partly built in. The training window is the one a script of Chan's names,
and it misses the printed deviation.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The hedge, VX contracts per ES contract | "0.3906" | location 2559 |
| 2 | The residual's standard deviation | "$2,047" | location 2559 |
| 3 | The test set's APR | "12.3 percent" | location 2559 |
| 4 | The test set's Sharpe ratio | "1.4" | location 2559 |
| 5 to 11 | the first training row, the exit, the first test day, the rounded hedge, the later saves, the script as shipped, and the holding periods | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | minus the slope of `50·ES` on `1000·VX` and a constant | 0.390594 | `TestTheSpecification::test_the_hedge` |
| 2 | the residual's standard deviation, n − 1 | $2,044.91 | `TestTheSpecification::test_the_residual_standard_deviation_misses_by_two_dollars` |
| 3 | `prod(1 + ret)^(252/449) − 1` | 0.122811 | `TestTheSpecification::test_the_apr` |
| 4 | `√252 · mean(ret) / std(ret)` | 1.393201 | `TestTheSpecification::test_the_sharpe_ratio` |
| 5 | rows 1 to 4 fitted on training rows 2 to 500, from 2008-08-05 | 0.390635, $2,046.93, 0.122804 and 1.393228 | `TestTheDiagnostics::test_dropping_the_first_training_row_reaches_both_printed_figures` |
| 6 | rows 3 and 4 with each position closed when the z-score crosses 0, as `bollinger.m` exits | 0.068463 and 0.870716 | `TestTheDiagnostics::test_an_exit_at_the_mean_misses` |
| 7 | rows 3 and 4 with the band started flat on 2010-07-29 | 0.124916 and 1.415772 | `TestTheDiagnostics::test_starting_flat_on_the_first_test_day_misses` |
| 8 | rows 3 and 4 trading the printed 0.3906 in place of the fitted hedge | 0.122810 and 1.393205 | `TestTheDiagnostics::test_the_printed_constant_moves_nothing_that_prints` |
| 9 | rows 1 to 4 on the 2012-05-17 save, the test cut at 2012-05-08, and on the 2012-05-11 save | 0.376431, $2,291.00, 0.056582 and 0.673910 on both | `TestTheDiagnostics::test_the_2012_05_17_save_misses` and `::test_the_2012_05_11_save_agrees_with_the_2012_05_17_save` |
| 10 | `VX_ES.m` as shipped, 957 days from 2008-08-01 to 2012-05-17 on the 2012-05-17 save | 0.350731 and $2,373.59, and no trade | `TestTheDiagnostics::test_the_script_as_shipped` |
| 11 | the position held into the test and the changes in it | long at the close of 2010-07-28, short on 2011-11-08, long on 2011-12-19 and short on 2012-02-17 | `TestTheTrade` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | 0.390594 rounds to the printed 0.3906. |
| 2 | −$2, and −$2.09 before rounding | did not reproduce | The fit lands the hedge to four decimals and misses the deviation by a tenth of a percent. Row 5 shows that a window one day shorter lands it. Nothing that ships says why a row would be dropped. |
| 3 | 0.0 | reproduced | 0.122811 rounds to 12.3 percent. |
| 4 | 0.0 | reproduced | 1.393201 rounds to 1.4. |
| 5 | none | none, not a replication | Fitting from 2008-08-05 lands both of row 1's and row 2's printed figures and moves rows 3 and 4 by less than their last printed digit. It is the one window of the sweep's 22,446 that lands both, so it was found by searching and is not evidence of anything else. Rows 1 to 4 keep the window a script of Chan's states. |
| 6 | none | none, not a replication | The exit is what decides the trade's figures. Closing at the mean, the rule Chan's other Bollinger band uses, gives 6.8 percent against the printed 12.3. Holding until the opposite band is the one rule tried that lands both of rows 3 and 4. |
| 7 | none | none, not a replication | On 2010-07-28 the z-score is −1.041, so the band is already long. Carrying that position into the test is what `VX_ES_rollreturn.m`'s slicing does, and starting flat moves the APR to 12.5 percent. |
| 8 | none | none, not a replication | Trading the printed constant moves nothing that prints, so a run that takes 0.3906 as given, as the roll-return trade does, trades the same portfolio to the book's precision. |
| 9 | none | none, not a replication | The 2012-05-11 and 2012-05-17 saves agree with each other over these days and disagree with the 2012-05-07 save, because the back-adjusted history was rewritten between them. On either, the specification misses all four figures. |
| 10 | none | none, not a replication | The script as shipped fits on days that include the whole test set and runs no trade, so it cannot be the source of rows 3 and 4. Its hedge and deviation miss rows 1 and 2 as well. |
| 11 | none | none, not a replication | The portfolio is in the market on all 449 test days and holds four positions. |

### What the entry concludes

Three things.

1. **The hedge, the APR and the Sharpe ratio reproduce on Chan's 2012-05-07
   save.** The residual deviation misses by $2.09, and one dropped training
   row closes it. That save's last day is the last day of the printed test,
   which points to the same save by a route other than the figures.
2. **The script that ships is not the run behind the figures.** It loads a
   later save, fits on the test set and stops before any trade. The run that
   lands the figures takes a save, a window and an exit from outside
   `VX_ES.m`. The window comes from `VX_ES_rollreturn.m`. The save and the
   exit were chosen because they land the figures.
3. **The trade's figures rest on four bets.** The portfolio enters the test
   already long and changes position three times in 449 days. An APR of 12.3
   percent from four holding periods says little about how often the band
   pays.

### What this entry cannot say

Four things.

**Whether the portfolio is stationary.** The book argues it from a plot,
Figure 5.11, and prints no statistic, and this run takes no test. The z-score
sits beyond a band on 236 of the 449 test days against 113 of the 500
training days, which `TestTheTrade` holds, so the test set strays more often
than training did.

**What costs would take.** The book charges none and this run charges none.
Four positions in 449 days is few trades, but nothing here measures what a
cost would take. Each unit also holds 0.39 of a VX contract, which a real
account cannot hold, and nothing here measures what rounding it would move.

**Whether the window is the book's.** The sweep found one window that lands
both fitted figures, and rows 1 to 4 use a neighbour of it that a script of
Chan's names. Neither is confirmed by anything he printed, so the match is
evidence that this window is close to his, and no more.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/vx-es-lessons.md](../blog/vx-es-lessons.md), this entry's write-up,
moves with it, since that post quotes most of these figures. The post's one
figure moves too, and `uv run python -m chan.vx_es_figures` redraws it.

## Entry 29: GLD, GDX and USO around July 2008, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 1922, with the same story repeated
at 3537 and 3570. No script ships for it. Shipped under
[issue 344](https://github.com/l3a0/quantitative-trading/issues/344). Every
location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Fourteen rows, all derivable from
[tests/test_gold_miners_oil.py](../tests/test_gold_miners_oil.py).

Chan pairs the gold fund GLD with the gold miners' fund GDX, since a miner's
main asset is gold. He says the pair cointegrated until July 14, 2008, the day
oil peaked near $145 a barrel, and stopped afterwards. His explanation is that
dear oil makes gold dearer to mine, so the miners lag the metal. He tests it
by adding the oil fund USO and finding that the three cointegrate over the
whole span. The book offers this as an example of forming a hypothesis about
why a strategy stopped working and testing it.

**All three claims hold on Chan's own file, on both Johansen statistics, at 99
percent and at 90.** The control the book leaves out holds as well. GLD and
GDX alone over the triplet's days find no relation even at 90 percent, so the
triplet's relation is not one the pair already had. It may be GDX and USO's
own, though, because those two alone find one relation at 99 percent.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdata_etf/gld.csv`, `gdx.csv` and `uso.csv`, lifted
   from Chan's `inputData_ETF.mat`, saved 2012-04-10, read for the close
   through `chan.series.load_panel`. The file holds GLD and USO from
   2006-04-26 and GDX from 2006-05-23, so the run cuts to GDX's first price.
   That leaves 1,481 trading days to 2012-04-09, and Chan's first window starts
   on the same day. The first window, to 2008-07-14, holds 539 of them, and
   the second, from 2008-07-15, holds 942.
2. **The specification.** No script ships, so it was declared on the issue
   before any statistic was computed. The Johansen test is jplv7's
   `johansen(·, 0, 1)`, a constant and one lagged difference, which every
   book-two script passes, run by `chan.johansen.johansen`. The columns run
   GLD, GDX and then USO. The book does not say which of the two Johansen
   statistics it read, and Entry 23 found them disagreeing on Chan's own file.
   So each claim is two rows, one per statistic, each judged at 99 percent,
   the level all three claims name.

Every result here is **exploratory**, twice over. Reproducing the claims
spends the 2006 to 2012 sample on a split Chan chose. The split date and the
third ETF were both chosen after the break was seen, so the triplet's result
cannot confirm the oil hypothesis however it comes out.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | GLD and GDX cointegrate, 2006-05-23 to 2008-07-14, trace statistic | a claim, "cointegrate with 99 percent probability" | location 1922 |
| 2 | The same, eigen statistic | the same claim | location 1922 |
| 3 | GLD and GDX have lost it, 2008-07-15 to 2012-04-09, trace statistic | a claim, "have lost the cointegration" | location 1922 |
| 4 | The same, eigen statistic | the same claim | location 1922 |
| 5 | GLD, GDX and USO hold exactly one relation, 2006 to 2012, trace statistic | a claim, "a 99 percent probability that there exists one cointegrating relationship" | location 1922 |
| 6 | The same, eigen statistic | the same claim | location 1922 |
| 7 | The pair's statistics and eigenvalues before the break | none | n/a |
| 8 | The pair's statistics and eigenvalues after the break | none | n/a |
| 9 | The triplet's statistics and eigenvalues | none | n/a |
| 10 | GLD and GDX alone over the triplet's 1,481 days | none, the control the book leaves out | n/a |
| 11 | The triplet's first eigenvector | none, location 1922 says the triplet can be traded and prints no weights | location 1922 |
| 12 | The CADF test of GLD on GDX in each window | none | n/a |
| 13 | A plain ADF test of each ETF alone in each window it enters | none | n/a |
| 14 | GLD and USO, and GDX and USO, each alone over the triplet's 1,481 days | none | n/a |

Each row's claim criterion was written on the issue before any statistic was
computed. Rows 1 and 2 hold on one relation or two, rows 3 and 4 on none, and
rows 5 and 6 on exactly one. Row 14 was not on the issue. The pull request's
review added it after the first run, to ask whether the triplet's relation is
one of the other two pairs' own. The criteria are pinned in
`TestTheSpecification::test_the_six_criteria_are_the_ones_issue_344_declared`.
The critical values beside each statistic are LeSage's tables, which Entry 23
checked against Chan's own printout.

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `johansen([GLD, GDX], 0, 1)`, first window, trace | 1 relation at 99 percent, 22.571096 against 19.935 | `TestTheClaims::test_rows_1_and_2_the_pair_holds_one_relation_before` |
| 2 | The same, eigen | 1 relation at 99 percent, 22.423682 against 18.520 | the same |
| 3 | `johansen([GLD, GDX], 0, 1)`, second window, trace | 0 relations at 90, 95 and 99 percent, 6.132867 against 13.429 at 90 | `TestTheClaims::test_rows_3_and_4_the_pair_holds_none_after_even_at_90` |
| 4 | The same, eigen | 0 relations at 90, 95 and 99 percent, 6.059166 against 12.297 at 90 | the same |
| 5 | `johansen([GLD, GDX, USO], 0, 1)`, whole span, trace | 1 relation at 90, 95 and 99 percent | `TestTheClaims::test_rows_5_and_6_the_triplet_holds_one_at_every_level` |
| 6 | The same, eigen | 1 relation at 90, 95 and 99 percent | the same |
| 7 | As row 1 | trace 22.571096 and 0.147414, eigen 22.423682 and 0.147414, eigenvalues 0.04089749 and 0.00027448 | `TestEachTestsTable::test_row_7_the_pair_before` |
| 8 | As row 3 | trace 6.132867 and 0.073701, eigen 6.059166 and 0.073701, eigenvalues 0.00642519 and 0.00007840 | `TestEachTestsTable::test_row_8_the_pair_after` |
| 9 | As row 5 | trace 44.837732, 7.004501 and 0.164176, eigen 37.833231, 6.840326 and 0.164176, eigenvalues 0.02525587, 0.00461429 and 0.00011100 | `TestEachTestsTable::test_row_9_the_triplet` |
| 10 | `johansen([GLD, GDX], 0, 1)`, whole span | trace 10.446773 and 0.044664, eigen 10.402109 and 0.044664, eigenvalues 0.00700853 and 0.00003020, so 0 relations even at 90 percent | `TestEachTestsTable::test_row_10_the_control_the_pair_alone_over_the_triplets_days` and `::test_row_10_the_control_finds_no_relation_even_at_90` |
| 11 | Column 0 of row 9's eigenvectors, rows GLD, GDX, USO | 0.033109, −0.177036 and 0.002549 | `TestBesideTheReplication::test_row_11_the_triplets_first_eigenvector` |
| 12 | `lesage_cadf(GLD, GDX, 1)` against MacKinnon's two-series bars, −3.34 at 95 percent and −3.90 at 99 | −3.724034 in the first window, −1.511680 in the second and −1.517588 over the whole span | `TestBesideTheReplication::test_row_12_the_cadf_rejects_at_95_before_and_not_at_99` |
| 13 | ADF with a constant and one lag, against MacKinnon's −2.57 at 90 percent | first window GLD −0.033875 and GDX −1.962727, second GLD −0.575590 and GDX −1.720225, whole span GLD −0.370352, GDX −2.371217 and USO −1.213340 | `TestBesideTheReplication::test_row_13_no_series_alone_rejects_a_unit_root_even_at_90` |
| 14 | `johansen([GLD, USO], 0, 1)` and `johansen([GDX, USO], 0, 1)`, whole span | GLD and USO trace 4.349962 and 0.573598, 0 relations even at 90 percent. GDX and USO trace 27.165550 and 3.034162, eigen 24.131388 and 3.034162, 1 relation at 95 and 99 percent and 2 at 90 | `TestBesideTheReplication::test_row_14_gdx_and_uso_alone_hold_a_relation_and_gld_and_uso_do_not` |

### The verdicts

| # | Gap | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, a claim | reproduced | The trace statistic rejects no cointegration at 99 percent, clearing its bar by 2.636, and stops at one relation. |
| 2 | none, a claim | reproduced | The eigen statistic does the same, clearing its bar by 3.904. |
| 3 | none, a claim | reproduced | No relation at 99 percent, and none at 90 either. |
| 4 | none, a claim | reproduced | The same on the eigen statistic. |
| 5 | none, a claim | reproduced | One relation, and the second null stands at every level, 7.005 against 13.429 at 90 percent. |
| 6 | none, a claim | reproduced | The same on the eigen statistic, 6.840 against 12.297 at 90 percent. |
| 7 | none | none, not a replication | The book prints no statistic. |
| 8 | none | none, not a replication | The book prints no statistic. |
| 9 | none | none, not a replication | The book prints no statistic. |
| 10 | none | none, not a replication | The pair alone finds nothing over the triplet's days, which is what row 5 needs to mean anything. |
| 11 | none | none, not a replication | The sign is statsmodels', which makes the first row positive. |
| 12 | none | none, not a replication | The CADF test rejects at 95 percent before the break and not after it. At the 99 percent level the claims are judged at, it rejects in neither window. |
| 13 | none | none, not a replication | No series is stationary on its own in any window. |
| 14 | none | none, not a replication | GDX and USO alone hold the relation the triplet finds, so the triplet's row cannot separate the oil hypothesis from that pair's own link. |

### What the entry concludes

Four things.

1. **Every claim holds with room, on both statistics.** The nearest call is
   row 1, whose trace statistic of 22.571 clears its 99 percent bar of 19.935
   by 2.636. Every other claim clears or misses its bar by more,
   `TestEachTestsTable::test_the_closest_call_is_row_1_clearing_its_bar_by_2_636`
   lists each, and the counts at 90 and 95 percent agree with 99 on every
   row. So the choice of statistic and the choice of level that the book left
   open move nothing here, which is the opposite of what Entry 23 met. The
   loss holds even at 90 percent, so the stronger reading of "lost" holds too.
   The book's "99 percent probability" is a test level rather than a
   probability. The test rejects no cointegration at the 1 percent level, and
   it says nothing about how likely the pair is to cointegrate.
2. **The control holds, and a second control weakens what it shows.** GLD
   and GDX alone over the triplet's 1,481 days give a trace statistic of
   10.447, short of even the 90 percent bar of 13.429. Adding USO raises the
   first null's trace to 44.838, so the triplet's relation is not one the pair
   already had. Row 14 asks the same of the other two pairs. GLD and USO alone
   find nothing, at 4.350. GDX and USO alone find one relation at 99 percent,
   at 27.166 against 19.935. So a triplet of rank 1 is also what a link
   between the miners and oil alone would produce, with GLD along for the
   ride, and that reading says nothing about oil restoring the link between
   gold and the miners. Rank 1 cannot tell the two readings apart, and this
   entry does not try. The eigenvector's entries are shares per unit of the
   portfolio, so their sizes are not comparable across ETFs at different
   prices, and no row here measures any weight in dollars.
3. **The Engle-Granger family sees the same break, and no series is
   stationary alone.** The CADF statistic of GLD on GDX is −3.724 before the
   break, past the 95 percent bar of −3.34 and short of the 99 percent bar of
   −3.90, and −1.512 after it. So that test rejects before the break at 95
   percent rather than 99, and finds nothing after it. None of the seven ADF
   statistics in row 13 rejects a unit root even at 90 percent. No rank in
   rows 1 to 10 equals its column count, so the full-rank question Entry 23
   left open does not arise there. GDX and USO alone in row 14 do reach full
   rank at 90 percent, on a second null of 3.034 against 2.705, while neither
   ETF rejects a unit root alone. That is Entry 23's tension again, at a level
   no claim here is judged at.
4. **Detour 6 of `blog/gld-gdx-cointegration-lessons.md` bears on the same
   break.** That post says the miners "detached from gold
   somewhere in the 2010s", from yfinance closes and a rolling CADF. This run
   reads Chan's file with the Johansen test and finds no relation over
   2008-07-15 to 2012-04-09 as a whole. The two differ in file, test and
   window. One test over a window that runs into 2012 cannot say where inside
   it the link failed, so this entry does not date the break, and it says
   nothing about the years after 2012.
   [blog/gold-miners-oil-lessons.md](../blog/gold-miners-oil-lessons.md), this
   entry's write-up, sets the two side by side. On 2026-10-06 the owner chose
   to keep the earlier post's sentence, so that post and its Substack copy are
   unchanged.

### What this entry cannot say

Four things.

1. **Anything about oil itself.** USO holds front-month WTI futures rather
   than oil, which location 1939 raises about a different pair. A futures fund
   drifts from the spot price by its roll, so the triplet's relation is with
   the fund, and whether it holds with the spot price is a different test.
2. **Whether the break is where Chan put it.** The date was chosen by looking
   at the data, so a test that splits there is favoured by construction. No
   row here searches for the break or tests another date, and doing so would
   be a search with its own rail.
3. **How much the three tests confirm each other.** Each is a fixed-level test,
   and the triplet's span contains both of the pair's windows, so the rows are
   not independent. Nothing here corrects for running several tests on one
   sample.
4. **Whether the oil hypothesis holds.** It was formed on this sample and
   tested on the same one. The test that would bear on it runs GLD, GDX and
   USO after 2012-04-09, with the hypothesis written down first. That is a
   registered experiment, which [docs/design.md](design.md) names as a
   different object from a replication, and no issue carries it yet.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/gold-miners-oil-lessons.md](../blog/gold-miners-oil-lessons.md) moves
with it, since that post quotes most of these figures. The post's one figure
moves too, and `uv run python -m chan.gold_miners_oil_figures` redraws it.

## Entry 30: AUD.CAD with rollover interest, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 5.2, Kindle location 2303, with the rollover
interest defined at location 2273, and the script `AUDCAD_daily.m` the example
names. Shipped under
[issue 346](https://github.com/l3a0/quantitative-trading/issues/346). Every
example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eight rows, all derivable from
[tests/test_aud_cad_rollover.py](../tests/test_aud_cad_rollover.py). Rows 1
and 2 each cover two printed figures from one computation, and rows 6 to 8
carry no published figure.

A currency position held past 5 p.m. New York time earns the interest rate of
the currency it is long and pays the rate of the one it is short. Location 2273
calls the difference the rollover interest, and Chan uses this example to show
that a currency strategy's return has to include it. He trades the AUD.CAD
cross rate with a linear mean-reverting rule. Each day the position is minus
the sign of the close's 20-day z-score, so the strategy is long or short one
unit and never flat once the window fills. The return is the next day's log
move plus the rollover on the position held overnight.

**The script's figures reproduce and the book's rollover figure does not.**
Both figures `AUDCAD_daily.m` prints land every digit, and so do the two the
book gives without rollover. The book's annualised rollover of "almost 5
percent" misses the criterion written before it was computed. Two other
readings land inside it, and nothing here chooses between them.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `pythoncodesanddata/inputData_AUDCAD_20120426.csv`, from
   Chan's 2018 Python port, saved 2018-12-13, 1,237 days from 2007-07-23 to
   2012-04-26, as traded, read through `chan.series.load_port_close`. The
   rates are `pythoncodesanddata/AUD_interestRate.csv`, 147 months from
   2000-01 to 2012-03, and `pythoncodesanddata/CAD_interestRate.csv`, 144
   months from 2000-01 to 2011-12, both saved 2018-12-13, read through
   `chan.series.load_rates`.
2. **The specification.** `AUDCAD_daily.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `823983a`, as `chan.aud_cad_rollover` transcribes it. The position
   is minus the sign of a 20-row z-score that includes the day, with the n − 1
   deviation, held from the next day. Each day takes its calendar month's
   rate, and 0 where the file holds no such month, divided by 365 and by 100.
   AUD's daily rate is tripled on Wednesdays and CAD's on Thursdays. The return
   is yesterday's position times today's log move plus yesterday's
   `log(1 + aud) − log(1 + cad)`. The figures run over all 1,237 rows, the
   first 20 of them 0: the APR is `prod(1 + r)^(252 / 1237) − 1`, which
   compounds a log return as if it were simple, and the Sharpe ratio is
   `√252 · mean / std`, with no risk-free rate and no cost.

**Row 5's criterion was written before the row was computed.** Location 2273
defines the rollover on a long position as the differential of the two rates.
So row 5 is 252 times the mean, over every row, of the rollover term the
script adds to a long position.
[Issue 346](https://github.com/l3a0/quantitative-trading/issues/346) wrote on
2026-10-05 that "almost 5 percent" holds when that value is at least 0.045 and
below 0.050, because the words say below 5 and close enough to round to it.
The criterion was written knowing the two monthly means from July 2007, 4.908
percent for AUD and 1.592 for CAD, and the issue said so and named the AUD
rate alone as the likely explanation of a miss. That reading is row 6, beside
the replication rather than the criterion, because it contradicts the book's
own definition. The review of this entry found a second reading that lands,
the differential annualised over 365 days, which is row 8.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2007 to 2012 sample on a rule he chose, so the entry says whether his numbers
reproduce on his files and nothing about whether the cross rate reverts today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | APR with rollover interest | 0.061564, and 6.2 percent | script line 50, location 2303 |
| 2 | Sharpe ratio with rollover interest | 0.541802, and 0.54 | the same |
| 3 | APR without rollover interest | 6.7 percent | location 2303 |
| 4 | Sharpe ratio without rollover interest | 0.58 | location 2303 |
| 5 | Annualised average rollover interest | "almost 5 percent" | location 2303 |
| 6 | Row 5 on the AUD rate alone | none | n/a |
| 7 | Rows 1 and 2 with each missing month carried forward | none | n/a |
| 8 | Row 5 annualised over 365 days rather than 252 | none | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | Line 43's returns over all 1,237 rows | 0.0615638271 | `TestRows1And2WithRollover::test_row_1_the_apr` |
| 2 | The same | 0.5418018005 | `TestRows1And2WithRollover::test_row_2_the_sharpe_ratio` |
| 3 | Line 44's returns, which are line 43's with both rates at 0 | 0.0671408367 | `TestRows3And4WithoutRollover::test_row_3_the_apr` |
| 4 | The same | 0.5845063318 | `TestRows3And4WithoutRollover::test_row_4_the_sharpe_ratio` |
| 5 | 252 times the mean of `lag(log(1 + aud) − log(1 + cad), 1)`, first row 0 | 0.0326416903 | `TestRow5TheAnnualisedRollover::test_row_5_misses_the_criterion` |
| 6 | Row 5 with CAD's rate at 0 | 0.0466475912 | `TestBesideTheReplication::test_row_5_on_the_aud_rate_alone_lands_inside_the_criterion` |
| 7 | Line 43 with each missing month given the last month its file holds | APR 0.0620850756, Sharpe ratio 0.5457420240 | `TestBesideTheReplication::test_rows_1_and_2_with_each_missing_month_carried_forward` |
| 8 | 365 times row 5's mean, 365 being the divisor lines 21 and 33 apply | 0.0472786388 | `TestBesideTheReplication::test_row_5_annualised_over_365_days_lands_inside_the_criterion_too` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000, and −0.0 at the book's tenth of a percent | reproduced | Exact at the six decimals the script prints. |
| 2 | −0.000000, and +0.00 at the book's two decimals | reproduced | The same. |
| 3 | +0.0 at the book's tenth of a percent | reproduced | Rows 1 and 2 land, so the inputs are the script's, and 6.71 percent rounds to the book's 6.7. |
| 4 | +0.00 at the book's two decimals | reproduced | The same, at 0.5845. |
| 5 | none, a criterion, and below its floor of 0.045 | did not reproduce | Rows 1 and 2 land every digit, so the input is not the cause, and the differential location 2273 defines averages 3.26 percent a year. Rows 6 and 8 are two explanations, and neither is ruled out. |
| 6 | none | none, not a replication | The AUD rate alone gives 4.66 percent, inside row 5's criterion. That is the rate a long position earns rather than the differential it nets. |
| 7 | none | none, not a replication | Carrying the last month forward gives CAD a rate in 2012 and AUD one in April 2012, and moves the APR from 0.061564 to 0.062085 and the Sharpe ratio from 0.541802 to 0.545742, which rounds to 0.55 rather than the book's 0.54. |
| 8 | none | none, not a replication | The differential over 365 days gives 4.73 percent, inside row 5's criterion. The script divides each annual rate by 365, so annualising its daily term by 365 rather than by the 252 it uses for returns is a slip it invites. |

### What the entry concludes

Four things.

1. **The AUD.CAD file and the two rate files give the figures Chan's MATLAB
   printed.** The script loaded a minute `.mat` file that neither mirror
   carries, and this run read the Python port's daily copy. Both printed
   figures land every digit, which is indirect evidence that the copy holds
   the 16:59 closes the MATLAB kept, up to a constant scale. Log moves and the
   sign of a z-score cannot see a scale, and
   `TestTheRule::test_a_constant_scale_on_every_close_moves_no_figure` holds
   that. It is weaker evidence than Entry 25's 612 returns matched row by row,
   since two figures sum up 1,237 days.
2. **The book's rollover figure is not the differential it defines, and two
   readings explain it.** The differential location 2273 defines gives 3.26
   percent a year, which no reading of "almost 5 percent" reaches. The AUD
   rate alone gives 4.66 percent, and the differential annualised over 365
   days gives 4.73. Both land inside the criterion, and nothing in the book
   or the script says which one Chan computed.
3. **Rollover cost the strategy about half a point a year, because it was
   short more often than long.** A long position earns the differential and a
   short one pays it. The rule is short on 707 of the 1,217 days it holds a
   position and long on 510, and the rollover it earned comes to −0.005221 a
   year. That is close to the half point between the book's APR of 6.7
   percent without rollover and 6.2 with it, and the two differ because the
   APR compounds the returns while this is their mean.
   `TestBesideTheReplication::test_the_rule_holds_short_on_707_days_and_long_on_510`
   and `::test_the_rollover_the_strategy_earned_is_a_cost_of_0_005221` hold
   those figures.
4. **The book's Sharpe ratio of 0.54 depends on the zero fill.** The script
   gives the 84 days of 2012 no CAD rate and the 19 days of April 2012 no AUD
   rate. Row 7 carries each file's last month forward instead, and gives an
   APR of 0.062085 and a Sharpe ratio of 0.545742 against the script's 0.061564
   and 0.541802. The APR still rounds to 6.2 percent, and the Sharpe ratio
   rounds to 0.55 rather than the book's 0.54.

### What this entry cannot say

Four things.

**Whether the script's settlement rule is the right one.** Location 2273 says
a cross triples its rollover when day T + 3 is a weekend, which is Wednesday
for both currencies, and names T + 1 settlement as the exception for USD.CAD.
The script triples CAD on Thursday, which is the USD.CAD rule applied to one
leg of a cross. The run transcribes the script, and no row runs the book's
rule, because choosing between the two after seeing the figures would be a
search.

**What holidays would add.** No day multiplies its rollover for a holiday.
Seven weekdays are absent from the file: Christmas Day in 2007, 2008 and 2009,
New Year's Day in 2008, 2009 and 2010, and 2011-12-23, an early close.
`TestTheVintages::test_seven_weekdays_are_absent_and_none_is_a_weekend` holds
the list. A position held across Christmas earns nothing for the day the
market was shut.

**What the 2012 rates were.** Row 7 says what carrying the last month forward
moves, and it is a guess about four months of rates rather than a measurement
of them. The rates were not checked against the Reserve Bank of Australia's or
the Bank of Canada's own tables, which
[data/README.md](../data/README.md) says cannot be done here.

**Anything about costs.** The rule can reverse its position every day, and the
script charges nothing for it.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/aud-cad-rollover-lessons.md](../blog/aud-cad-rollover-lessons.md) moves
with it, since that post quotes most of these figures. The post's one figure
moves too, and `uv run python -m chan.aud_cad_rollover_figures` redraws it.

## Entry 31: crude oil reversal joined to momentum, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 2701, and the script `CL_rev.m` that
computes it. Shipped under
[issue 354](https://github.com/l3a0/quantitative-trading/issues/354). The
location number is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Fourteen rows, all derivable from
[tests/test_cl_reversal_momentum.py](../tests/test_cl_reversal_momentum.py).

**Both printed figures reproduce at the script's six decimals and at the
book's precision. On the book's window the joined rule beats each rule alone,
and on the four years before it momentum alone beats the joined rule.** A
mean-reverting rule bets a move will undo itself and a momentum rule bets it
will continue. On one shared lookback they take opposite sides every day, so
joining them would cancel. Chan gives them different lookbacks and trades only
on the days the two agree. His sentence is that "Sometimes, the combination of
mean-reverting and momentum rules may work better than each strategy by
itself." His rule on crude oil futures buys at the close when the price is
below its level 30 trading days ago and above its level 40 trading days ago,
shorts on the mirror, and is flat otherwise. He reports an APR of 12 percent and a Sharpe ratio of 1.1,
names no window and no save, and prints no figure for either rule alone.

`CL_rev.m` names both. It loads CL from the save Chan's file name dates
2012-05-04, 1,000 rows from 2008-05-19 to 2012-05-04, runs the rule over
every row, and its comment records `APR=0.117600 Sharpe=1.100368`. It runs
three more rules on the same series and prints nothing for them: momentum
alone against the 40-day lag, reversal alone against the 30-day lag, and a
fourth it names "ComboOR", which takes a long wherever either long condition
holds and a short wherever either short condition holds, and sums them.

Every row reads one of three vintages and one specification, so they are
stated once here.

1. **The vintages.** Three saves of Chan's continuous futures, each rolled
   from contract to contract and shifted at each roll, read for CL through
   `chan.series.load_panel` and cut to CL's own rows. A save is named by the
   date in its file name.
   1. `inputdataohlcdaily_20120504/`, downloaded 2012-05-07, the save
      `CL_rev.m` loads, 1,000 rows from 2008-05-19 to 2012-05-04. Rows 1 to
      5 and 10 to 14 read it.
   2. `inputdataohlcdaily_20120511/`, downloaded 2012-05-12, read over the
      same 1,000 days for row 6. Its closes sit 0.27 higher on every one.
   3. `inputdataohlcdaily_20120507/`, downloaded 2012-05-09. Its CL closes
      equal the first save's on all 1,000 of those days, so its earlier rows
      extend the same series backward. Rows 7 to 9 read its 998 rows from
      2004-05-24 to 2008-05-16.

   The scale-break guard runs on CL over each span read in each save, and
   refuses nothing.
2. **The specification.** `CL_rev.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `420d501`. Long where the close is below `backshift(30, cl)` and
   above `backshift(40, cl)`, short where it is above the first and below the
   second, flat otherwise. A comparison against the missing lag in the first
   rows is false, so those rows are flat. Each day earns yesterday's position
   on today's percentage move, with NaN set to 0. The APR is
   `prod(1 + ret)^(252/n) − 1` and the Sharpe ratio `√252 · mean(ret) /
   std(ret)` with n − 1, both over every row, flat rows included, with no
   cost.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2008 to 2012 sample on a rule he chose, and nothing shows the lookbacks were
fixed before the window they are reported on was seen. Rows 7 to 9 run on
data the book did not report, but nothing was registered before they were
read, so they are not a holdout.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The combination's APR | "12 percent", and `0.117600` in the script's comment | location 2701, and `CL_rev.m` |
| 2 | The combination's Sharpe ratio | "1.1", and `1.100368` in the script's comment | location 2701, and `CL_rev.m` |
| 3 to 14 | each rule alone, ComboOR, a later save, the four years before, the positions, and five changes to the specification | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + ret)^(252/1000) − 1` | 0.117600 | `TestTheSpecification::test_the_apr_reproduces_the_script_s_comment` |
| 2 | `√252 · mean(ret) / std(ret)` | 1.100368 | `TestTheSpecification::test_the_sharpe_ratio_reproduces_the_script_s_comment` |
| 3 | rows 1 and 2 for momentum alone, long above the 40-day lag and short below | 0.090228 and 0.439049 | `TestTheRowsBeside::test_momentum_alone` |
| 4 | rows 1 and 2 for reversal alone, long below the 30-day lag and short above | 0.068326 and 0.370289 | `TestTheRowsBeside::test_reversal_alone` |
| 5 | rows 1 and 2 for ComboOR | 0.125917 and 1.123042 | `TestTheRowsBeside::test_combo_or` |
| 6 | rows 1 and 2 on the 2012-05-11 save over the same days | 0.117226 and 1.100045 | `TestTheRowsBeside::test_the_later_save` |
| 7 | rows 1 and 2 on the 998 rows before the book's window | 0.021324 and 0.369864 | `TestBeforeTheBookSWindow::test_the_combination` |
| 8 | row 3 on those rows | 0.094589 and 0.660514 | `TestBeforeTheBookSWindow::test_momentum_alone` |
| 9 | row 4 on those rows | −0.065694 and −0.359464 | `TestBeforeTheBookSWindow::test_reversal_alone` |
| 10 | the combination's positions | long 98 rows, short 59, flat 843, 124 changes, the first on 2008-07-18 | `TestTheSpecification::test_the_position_is_flat_on_most_days` and `::test_the_first_position_is_taken_on_2008_07_18` |
| 11 | rows 1 and 2 with the two lookbacks swapped | −0.115294 and −1.100368 | `TestTheMutations::test_swapping_the_lookbacks_negates_the_rule` |
| 12 | rows 1 and 2 earning the same day's position rather than yesterday's | 0.008903 and 0.139324 | `TestTheMutations::test_trading_on_the_same_day_s_position` |
| 13 | rows 1 and 2 measured from row 41, the first row both lags exist, over 960 rows | 0.122789 and 1.123147 | `TestTheMutations::test_measuring_from_the_first_row_both_lags_exist` |
| 14 | row 2 dividing by n rather than n − 1 | 1.100919 | `TestTheMutations::test_dividing_the_sharpe_ratio_by_n` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.000000 against the script, 0 against the book | reproduced | 0.117600 is the script's comment to every digit and rounds to 12 percent. |
| 2 | 0.000000 against the script, 0.0 against the book | reproduced | 1.100368 is the script's comment to every digit and rounds to 1.1. |
| 3 | none | none, not a replication | Momentum alone earns less than the combination on both figures. |
| 4 | none | none, not a replication | Reversal alone earns less than the combination on both figures, which with row 3 is the book's sentence, measured on its window. |
| 5 | none | none, not a replication | ComboOR is the combination except on the 10 rows from 2008-07-01 to 2008-07-15, where the 30-day lag exists and the 40-day one does not and OR trades the reversal rule alone. Off those rows, a row where both conditions hold is long under both rules, a row where neither holds is short under both, and a row where one holds is flat under both, since OR sums a long and a short. |
| 6 | none | none, not a replication | The 2012-05-11 save, whose file name is dated a week later, still rounds to 12 percent and 1.1 and misses the script's comment at the fourth decimal, so the save is part of the specification at six decimals and not at the book's precision. |
| 7 to 9 | none | none, not a replication | On the four years before the window, momentum alone beats the combination on both figures, and reversal alone loses money. The series there is back-adjusted further from the traded price. It closes at 119.12 on 2004-05-24, against an EIA annual WTI spot average near $41 that year, a figure not measured here. So each percentage return divides by a price well above what traded. |
| 10 | none | none, not a replication | The rule is flat on 843 of 1,000 days and cannot signal for the first 40, so the two figures rest on 157 days in the market. |
| 11 | none | none, not a replication | Every long becomes a short, so the Sharpe ratio flips sign exactly. Which lookback carries which rule decides the sign of every position. |
| 12 to 14 | none | none, not a replication | Each moves a figure the script prints, so the suite notices each one. |

### What the entry concludes

Three things.

1. **Both figures reproduce on the save the script loads.** The APR and the
   Sharpe ratio match the output `CL_rev.m`'s comment records to six
   decimals, and that output rounds to the book's two figures. Row 6 shows
   another save also rounds to them, so nothing here shows which run the book
   printed.
2. **On the book's window the combination beats each rule alone.** It earns
   more than momentum alone and reversal alone on both figures from
   2008-05-19 to 2012-05-04. Rows 3 and 4 carry no verdict, because the book
   prints no figure for either rule alone. ComboOR, the script's fourth curve, is the same rule outside
   ten warm-up rows, so it adds no evidence of its own.
3. **The combination does not beat momentum alone on the four years
   before.** From 2004-05-24 to 2008-05-16, momentum alone earns more on both
   figures. The book's "Sometimes" already allows that, so the segment shows
   the advantage is not general rather than contradicting the book. Its
   prices are distorted by the back-adjustment, so it is not a backtest
   either.

### What this entry cannot say

Four things.

**Whether the lookbacks were chosen on this window.** The book names 30 and
40 days and nothing about how they were picked. A search over other lookbacks
would be the many-hypotheses case `CLAUDE.md` puts behind its own rail, and
this run tries none.

**What costs would take.** The book charges none and this run charges none.
The rule changes position 124 times in 1,000 days, and nothing here measures
what a cost per change would take from 12 percent.

**What the earlier segment would give on traded prices.** Rows 7 to 9 read a
series back-adjusted above the price that traded, and no unadjusted CL series
for those years is committed. So the earlier segment's figures are what the
rule gives on Chan's series, not what a trader would have earned.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 32: a Kalman filter hedge ratio on EWA and EWC, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle locations 1633 to 1726, and the script
`KF_beta_EWA_EWC.m` the example names. Shipped under
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342). The
highlights never give the example's number, so the entry names it by its script
and its location. The location numbers are that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seven rows, all derivable from
[tests/test_kalman_hedge.py](../tests/test_kalman_hedge.py). Rows 1 and 2
each cover two printed figures from one computation. Rows 3 and 4 test claims
and carry findings with no verdict, and rows 5 to 7 carry no published figure.

Example 3.2 hedges one ETF with another through a slope refitted over a
rolling window. A Kalman filter replaces the window. Each day it moves
yesterday's estimate of the slope and intercept toward whatever explains
today's pair of closes, by an amount set by how uncertain the estimate was.
It also forecasts EWC's close
before seeing it, with a variance for that forecast. The strategy buys the
spread when the forecast error falls below minus the forecast's standard
deviation and sells it when the error rises above plus that deviation, so the
filter supplies the hedge, the mean and the band at once.

**Both printed figures reproduce to the script's last digit, and the book's
two claims about the filter carry no verdict.** The book's 26.2 percent and
2.4 are the script's closing comment rounded. Location 1726 also says the
slope "oscillates around 1" and the intercept "increases monotonically with
time". No criterion for either was written before a run, so the owner ruled
on 2026-10-06 that both are carried as findings, and rows 3 and 4 report what
can be read against them.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdata_etf/ewa.csv` and `inputdata_etf/ewc.csv`, two
   of the 67 ETFs lifted from Chan's `inputData_ETF.mat`, git blob `261718b`,
   chan-mat, adjusted, saved 2012-04-10, 1,500 days from 2006-04-26 to
   2012-04-09, read through `chan.series.load_panel`. This is the only save of
   either ETF the repo holds, and both legs are priced on every row.
2. **The specification.** `KF_beta_EWA_EWC.m` at `e4bc46f` in
   [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview),
   git blob `e2f8a62`, as `chan.kalman_hedge` transcribes it. Box 3.1, which
   carries the equations, is not among the highlights, and the script labels
   its lines with equations 3.7 to 3.12, so the script is the specification.
   EWC's close is regressed on EWA's close and a column of ones, with `delta`
   0.0001 and `Ve` 0.001, and the state and its covariance start at 0. One
   unit goes long while the forecast error `e` is below `−sqrt(Q)` and short
   while it is above `sqrt(Q)`, and each side exits on its own entry band. The
   positions are `[−slope, 1]` of EWA and EWC. The return is profit over gross
   dollars with a NaN day set to 0, over all 1,500 rows. The APR is
   compounded over 252 days a year and the Sharpe ratio is `√252 · mean / std`
   with MATLAB's n − 1 `std`, with no risk-free rate and no cost.

**Rows 3 and 4 carry no verdict because their only criteria were written after
the run.** Location 1726 prints no number for either claim. The plan on
[issue 342](https://github.com/l3a0/quantitative-trading/issues/342) proposed
a criterion for each, a median slope that rounds to 1.0 with more than one
crossing of 1, and yearly mean intercepts that never fall. A scratch run had
already measured the figures both criteria read. This file accepts such a
criterion only when the verdict does not rest on where its line sits, and
neither meets that. The median sits 0.002633 below 1.05, where it would round
to 1.1, and the intercept rises at the yearly grain and falls at every finer
one. So the owner ruled that both rows report their figures and carry no
verdict. Neither counts toward this entry's two rows reproduced and none not
reproduced.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 to 2012 sample on a rule and two constants he chose, so the entry says
whether his numbers reproduce on his file and nothing about whether the filter
hedges EWA and EWC today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | APR | 0.262252, and 26.2 percent | script's closing comment, location 1726 |
| 2 | Sharpe ratio | 2.361162, and 2.4 | the same |
| 3 | The slope "oscillates around 1" | a claim, drawn as Figure 3.5 | location 1726 |
| 4 | The intercept "increases monotonically with time" | a claim, drawn as Figure 3.6 | location 1726 |
| 5 | The first position and the first return | none | n/a |
| 6 | Rows 1 and 2 with no signal on the file's first two days | none | n/a |
| 7 | The filter's first two rows | none | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | The script over all 1,500 rows | 0.26225194 | `TestTheFigures::test_the_apr_is_chans_0_262252` |
| 2 | The same | 2.36116164 | `TestTheFigures::test_the_sharpe_ratio_is_chans_2_361162` |
| 3 | The slope after each day's update, over all 1,500 rows | median 1.047367, mean 1.089693, above 1 on 894 rows, which is 59.6 percent, and 54 crossings of 1, the first of them on row 2 as the slope leaves its zero start | `TestTheSlopeFinding` |
| 4 | The intercept after each day's update, over all 1,500 rows | yearly means 0.1440, 0.6336, 2.5795, 5.6350, 6.0380, 6.5851 and 6.7748 from 2006 to 2012. Falls in 3 of 24 quarterly steps, 9 of 72 monthly steps, 57 of 1,250 steps of a 250-day rolling mean and 513 of 1,499 daily steps. A 300-day rolling mean falls in 25 of 1,200 steps and a 350-day one in none of 1,150. Peak 6.803488 on 2011-09-08, last 6.767360 | `TestTheInterceptFinding` |
| 5 | Row 1's run | a short on 2006-04-26 with the slope at 0, and the first nonzero return on 2006-04-27 | `TestTheFirstRows::test_the_first_unit_is_a_short_held_while_the_slope_is_0`, `::test_the_first_nonzero_return_falls_on_2006_04_27` |
| 6 | The four signal arrays false on rows 1 and 2, all 1,500 returns annualised | APR 0.26066891, Sharpe ratio 2.34946035 | `TestTheFigures::test_no_signal_on_rows_1_and_2_over_all_1500_rows` |
| 7 | Rows 1 and 2 of the filter | row 1: state 0, `Q` equal to `Ve`, `e` 22.95 against a `sqrt(Q)` of 0.031623. Row 2: slope 1.366666, equal to its closed form, `e` 22.78 against a `sqrt(Q)` of 0.163213 | `TestTheFirstRows::test_row_1_has_a_zero_gain_and_q_equal_to_ve`, `::test_row_2_equals_its_closed_form` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000, and +0.0 at the book's tenth of a percent | reproduced | Exact at the six decimals the script's comment prints, on Chan's own file through his own script. |
| 2 | −0.000000, and −0.0 at the book's tenth | reproduced | The same. |
| 3 | none, a claim | none, a finding | The median rounds to 1.0 and the mean to 1.1, and the slope crosses 1 54 times, one of them the step up from the zero start on row 2. The only criterion was written after the run, and the median sits 0.002633 inside the line it would have drawn, so the owner ruled the row carries no verdict. |
| 4 | none, a claim | none, a finding | Every yearly mean is above the year before, and the intercept falls at every finer grain, including 513 of its 1,499 daily steps. It peaks on 2011-09-08 above its last value. The only criterion was written after the run and chose the yearly grain, at which the claim holds, after the finer grains had been seen to fall, so the owner ruled the row carries no verdict. |
| 5 | none | none, not a replication | On row 1 the state is still 0, so the forecast is 0 and `e` is EWC's whole close. The script shorts EWC alone, with no EWA leg, on the file's first day. |
| 6 | none | none, not a replication | The script's own plot of `e` starts on row 3, which leaves both rows out. Withholding the signal there moves the APR to 26.1 percent and the Sharpe ratio to 2.3 at the book's precision, so neither of the book's figures survives it. Dropping the two rows from the returns as well gives 0.261059 and 2.351062, and `::test_dropping_rows_1_and_2_from_the_returns_is_a_different_reading` holds that this row is not that reading. |
| 7 | none | none, not a replication | Row 2's state matches `c·y·[x 1]' / (c·(x² + 1) + Ve)` with `c = delta / (1 − delta)` to 1e-12, which is what the zero start predicts. |

### What the entry concludes

Three things.

1. **Chan's file through Chan's script gives the figures his comment prints.**
   Both land every digit at six decimals. Entry 28 had to find which of three
   saves its figures came from. This file has one candidate, because
   `data/README.md` records the `.mat` as one git blob in all three published
   copies.
2. **The book's figures rest on a trade the filter has no basis for.** On the
   file's first day the filter has seen nothing, so its forecast of EWC is 0
   and the error is EWC's whole price. The script reads that as a spread far
   above its band and shorts EWC alone. Rows 5 and 6 measure it: withholding
   the signal on the first two days moves the APR from 0.262252 to 0.260669
   and the Sharpe ratio from 2.361162 to 2.349460, which round to 26.1 percent
   and 2.3 rather than the book's 26.2 and 2.4.
3. **The intercept rises as a trend, and not day by day.** The yearly means
   rise every year, from 0.1440 in 2006 to 6.7748 in 2012. At a quarter, a
   month, a 250-day window and a day, it falls, and 513 of its 1,499 daily
   steps go down. Whether that is "monotonically" depends on the grain, which
   is why row 4 reports the grains rather than choosing one. The slope sits
   above 1 on 59.6 percent of days, with a median of 1.047367 and a mean of
   1.089693.

### What this entry cannot say

Four things.

**What other values of `delta` or `Ve` give.** The script's comment invites
tuning `delta`. Varying it is a search over a hypothesis space, which needs
the honesty rail `CLAUDE.md` describes, so no other value is run or pinned.

**What the filter's market-making use at location 1760 gives.** That passage
prints no figure and names no script.

**Anything about costs.** The band changes position whenever the error crosses
it, and the script charges nothing for a trade.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/kalman-hedge-lessons.md](../blog/kalman-hedge-lessons.md), this entry's
write-up, moves with it, since that post quotes most of these figures. The
post's one figure moves too, and `uv run python -m chan.kalman_hedge_figures`
redraws it.

## Entry 33: time-series momentum on TU, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 6.1, Kindle locations 2623 to 2668. Shipped
under [issue 351](https://github.com/l3a0/quantitative-trading/issues/351).
The script is `TU_mom.m`, in ericnberwick/EpchanPreview at `e4bc46f` under
`public/img/book2/`, git blob `f7935c7`. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Fifteen rows, all derivable from
[tests/test_tu_momentum.py](../tests/test_tu_momentum.py). Eight do not match
one printed figure to one computation, and each says so in its own cells. Rows
6, 7 and 8 each cover the script's figure and the book's rounder one from one
computation, and rows 11 to 15 carry no published figure.

A trend follower bets that a price which rose over some past window keeps
rising over the next one. Example 6.1 tests that bet on TU, the two-year
Treasury note future, before trading it. It correlates TU's return over a
lookback with its return over a following hold, for every pair of 1, 5, 10,
25, 60, 120 and 250 days. To keep overlapping windows from counting one move
many times, it keeps every `min(lookback, hold)`-th day of each pair. The
250-day lookback and 25-day hold correlate at 0.27 with a p-value of 0.02, so
Chan trades them: long when the 250-day return is positive, short when it is
negative, deciding every day with a twenty-fifth of the capital and holding
each day's call for 25 days.

**Every figure the script prints reproduces, on a window the script's active
line does not read, and the Hurst exponent misses.** `TU_mom.m` picks its
window with `idx = find(tday == 20090102)` and leaves `% idx=1;` commented out
under it. All six figures in its closing comment land on `idx = 1`, the full
2004-06-01 window the book's sentence names, and none lands on 2009. Row 12
runs the active line.

Every row reads one vintage and one specification unless it names another, so
both are stated once here.

1. **The vintage.** `inputdataohlcdaily_20120511/tu.csv`, vendor `chan-mat`,
   basis `adjusted`, saved 2012-05-12, TU's column of Chan's
   `inputDataOHLCDaily_20120511.mat`. Its own rows are 2,000 days from
   2004-06-01 to 2012-05-11, the book's window exactly, read through
   `chan.series.load_panel` with the column's NaN dropped. The scale-break
   guard runs on TU over that span and refuses nothing.
2. **The specification.** `TU_mom.m` with `idx = 1`. The correlation is
   `scipy.stats.pearsonr`, whose p-value is the two-sided t-test that MATLAB's
   `corrcoef` returns. H is `genhurst(log(cl), 2)` at `maxT` 19, and the
   variance ratio test is `vratiotest(log(cl))` at period 2, both from
   `chan.stationarity_tests`. The return is yesterday's position times today's
   return, divided by 25. The figures read all 2,000 daily returns, annualised
   over 252 days with no risk-free rate and no cost. The Sharpe ratio divides
   by book two's `smartstd`, which divides by n. The Kelly f is
   `mean / std²` with MATLAB's n − 1 `std`.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2004 to 2012 sample on a lookback and a hold he picked from a table computed on
the same closes, so the entry says whether his numbers reproduce on his file
and nothing about whether the rule pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The 250/25 correlation of past and future returns | 0.27 | location 2659 |
| 2 | Its p-value | 0.02 | location 2659 |
| 3 | The Hurst exponent | 0.44 | location 2646 |
| 4 | The variance ratio test does not reject a random walk | a claim, "failed to reject" | location 2646 |
| 5 | The average annual return | 0.0167 | `TU_mom.m`'s comment |
| 6 | The Sharpe ratio | 1.04, and "a respectable 1" | `TU_mom.m`'s comment, location 2668 |
| 7 | The APR | 0.0167, and 1.7 percent | `TU_mom.m`'s comment, location 2668 |
| 8 | The maximum drawdown | −0.024847, and 2.5 percent | `TU_mom.m`'s comment, location 2668 |
| 9 | The longest drawdown | 343 days | `TU_mom.m`'s comment |
| 10 | The Kelly f | 64.919535 | `TU_mom.m`'s comment |
| 11 to 15 | the whole correlation table, the script's active line, the 2012-05-17 save, H at another `maxT`, and the statistic Example 1.1 starts from | none here, as each row says | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `corrcoef` of the 250-day past and 25-day future returns, every 25th of the 1,725 days both exist, so 69 | 0.271855 | `TestTheCorrelationTable::test_the_traded_cell_lands_the_book` |
| 2 | the same test's two-sided p-value | 0.023841 | the same |
| 3 | `genhurst(log(cl), 2)` at `maxT` 19 | 0.433357 | `TestTheTwoTests::test_h_misses_the_book_s_0_44` |
| 4 | `vratiotest(log(cl))` at period 2, 1,998 returns | h = 0, p 0.126860 | `TestTheTwoTests::test_the_variance_ratio_test_does_not_reject` |
| 5 | `252 · smartmean(ret)` | 0.016699 | `TestTheFigures::test_the_average_annual_return` |
| 6 | `√252 · smartmean(ret) / smartstd(ret)` | 1.041462 | `TestTheFigures::test_the_sharpe_ratio` |
| 7 | `prod(1 + ret)^(252/2000) − 1` | 0.016708 | `TestTheFigures::test_the_apr` |
| 8 | `calculateMaxDD(cumprod(1 + ret) − 1)`, the deepest drawdown | −0.024847 | `TestTheFigures::test_the_maximum_drawdown` |
| 9 | the same, the longest run of days below a high | 343 | `TestTheFigures::test_the_longest_drawdown` |
| 10 | `mean(ret) / std(ret)²` | 64.919535 | `TestTheFigures::test_the_kelly_f` |
| 11 | every pair of 1, 5, 10, 25, 60, 120 and 250 days, and the six pairs location 2646 calls the best compromises | 49 coefficients and p-values. The six are 0.1718, 0.2592, 0.1784, 0.2719, 0.4245 and 0.5112 | `TestTheCorrelationTable::test_every_cell` and `::test_the_six_compromises` |
| 12 | rows 5 to 10 from the script's active line, 849 days from 2009-01-02 | 0.014042, 1.187438, 0.014069, −0.009851, 164 days and 100.298107 | `TestTheWindow::test_its_figures` |
| 13 | rows 1, 2, 3 and 10, and row 4's p-value, on `inputdataohlcdaily_20120517/tu.csv`, saved 2012-05-18, 2,000 days from 2004-06-07 to 2012-05-17 | 0.287046, 0.016785, 0.446556, 64.930941 and 0.132819 | `TestTheSave::test_its_traded_cell_and_kelly_f_miss` and `::test_its_two_tests` |
| 14 | row 3 at `maxT` 24, and Entry 22's H on USD.CAD at `maxT` 19 and 24 | 0.440450 on TU, and 0.473233 and 0.471426 on USD.CAD | `TestTheTwoTests::test_no_single_max_t_lands_both_books_figures` |
| 15 | `mean(ret) / std(ret) · √2000` with the n − 1 `std`, on the returns built from the module's exported functions | 2.933253 | `TestTheGaussianStatistic::test_the_exports_give_tu_mom_hypothesis_test_s_2_93` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.00 | reproduced | 0.2719 rounds to the printed 0.27. |
| 2 | +0.00 | reproduced | 0.0238 rounds to the printed 0.02, and the correlation is significant at 5 percent, which is what location 2659 picks the pair for. |
| 3 | −0.01 | did not reproduce | 0.433357 prints as 0.43 on Chan's own saved file, so the vintage explanation is spent. Row 14 is the one reading tried after the miss. H rises with `maxT` and first prints as 0.44 at 24, but the same change moves Entry 22's USD.CAD further from its 0.49. No single `maxT` lands both, so the miss is not a different default. The claim the figure was printed for survives, since H is below a half here too. |
| 4 | none, a claim | reproduced | h is 0 at `vratiotest`'s default 5 percent, the level the script reads `h` at, so the test does not reject a random walk. |
| 5 | −0.0000 | reproduced | 0.016699 rounds to the printed 0.0167. |
| 6 | +0.00, and +0 against the book | reproduced | 1.041462 rounds to 1.04 and to 1. `chan.khandani_lo.plain_sharpe` divides by n − 1 and gives 1.041201, which `TestTheFigures::test_the_sharpe_ratio_divides_by_n` holds. That also prints as 1.04, so the row uses the script's divisor because it is the script's, not because it lands. |
| 7 | +0.0000, and −0.0 percent against the book | reproduced | 0.016708 rounds to 0.0167 and to 1.7 percent. |
| 8 | −0.000000, and −0.0 percent against the book | reproduced | Exact at the six decimals the script prints, and 2.484746 percent rounds to 2.5. |
| 9 | 0 days | reproduced | Exact. |
| 10 | −0.000000 | reproduced | Exact at the six decimals the script prints. |
| 11 | none | none, not a replication | The book prints one cell. The six compromise pairs all correlate positively, and five of them are significant at 5 percent. The exception is 250/120, at a p-value of 0.0617 on 14 days. |
| 12 | none | none, not a replication | The active line lands none of the comment's six figures, so the comment comes from `idx = 1`. The comment also prints no annual volatility although the printing line asks for one, so it was pasted from an earlier version of that line. |
| 13 | none | none, not a replication | TU's close is the same on every day the two saves share, so only the window moves, four trading days later. That is enough to move the correlation to 0.29 at two decimals and the Kelly f off the printed digits, which places the book's figures on the 2012-05-11 save. |
| 14 | none | none, not a replication | Tried after row 3 missed, as a diagnostic rather than a reading. |
| 15 | none | none, not a replication | `TU_mom_hypothesisTest.m` prints 2.93, which is Example 1.1's figure, replicated as Entry 37's row 1. It is pinned here because it shows that the returns Entry 37 imports are this entry's. |

### What the entry concludes

Three things.

1. **The book's figures come from the full window.** All six of the
   script's printed figures reproduce on `idx = 1`, the window the book's
   sentence names, while the line the script runs as shipped starts in 2009
   and lands none of them. The 2012-05-11 save is the one behind them, since
   the 2012-05-17 save that `correlationTest.m` loads moves both the
   correlation and the Kelly f.
2. **`genhurst` misses on both series the book prints an H for.** USD.CAD's
   0.4732 against 0.49 in Entry 22 and TU's 0.4334 against 0.44 here run
   through the same transcription, on Chan's own data, and no `maxT` lands
   both. No figure of Chan's vouches for the transcription. What checks its
   rules is the invariances `TestGenhurst` checks on synthetic series, and
   the two pins on USD.CAD and TU catch a change without showing it is right.
3. **The momentum the table shows is thin.** The traded pair's correlation
   rests on 69 days, its p-value of 0.0238 is one of 49 tried, and the
   variance ratio test sees a random walk. Location 2646 reconciles the two
   by saying momentum lives at some time frames and not others, which is a
   reading of the same table rather than a test of it.

### What this entry cannot say

Four things.

**Whether 250/25 would be chosen without hindsight.** The pair was picked from
a table of 49 computed on the 2004 to 2012 closes it then trades, so its
p-value is not corrected for the other 48. Example 1.1's three tests of the
same returns, in Entry 37, are where the significance question is asked.

**What computed the book's 0.44.** Row 14 found a `maxT` that lands it on TU
and breaks USD.CAD. Searching further would be choosing a reading after its
number is seen.

**What a trader would earn.** The returns are on the notional value of the
contract with no cost and no margin, and location 2668 says leverage is
needed to make the 1.7 percent worth having. Nothing here measures what costs
or leverage would do.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/tu-momentum-lessons.md](../blog/tu-momentum-lessons.md), this entry's
write-up, moves with it, since that post quotes most of these figures. The
post's one figure moves too, and `uv run python -m chan.tu_momentum_figures`
redraws it.

## Entry 34: mean reversion on crude oil's 12-month calendar spread, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 5.4, Kindle locations 2461 and 2471. Shipped
under [issue 348](https://github.com/l3a0/quantitative-trading/issues/348).
The script is `calendarSpdsMeanReversion.m`, in ericnberwick/EpchanPreview at
`e4bc46f` under `public/img/book2/`, git blob `277d84d`. Every location in
this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Twelve rows, all derivable from
[tests/test_calendar_spread_reversion.py](../tests/test_calendar_spread_reversion.py).
Four do not match one printed figure to one computation, and each says so in
its own cells. Row 9 tests a claim that prints no statistic, and rows 10 to 12
carry no published figure.

A calendar spread is long one futures contract and short another on the same
underlying with a different expiry. Under the constant-returns model of
Entry 27, the log value of a spread long the far contract and short the near
one is γ(T1 − T2), where γ is the roll return, T1 the near expiry and T2 the
later far one. That is minus γ times the gap between their expiries. So the
spread's signal depends on γ alone and not on the spot price, which is the
book's point.
Chan tests whether γ on CL, WTI crude oil, reverts to its mean, and then
trades it. Each day the z-score of γ over a lookback equal to its half-life
decides the side. A pair of contracts a year apart is held until 10 days
before the near one expires, the next pair takes over only when at least 63
days remain before its own exit, and the spread is reversed when z is above 0.

**The script's own window reproduces six of the eight printed figures and the
book's stationarity claim, and misses the comment's APR and Sharpe ratio.**
The script's comment prints five of the eight and the book three. Starting one
day later lands every digit of the comment, and nothing committed says which
start Chan ran.

**Row 9's criterion was written after the statistic was measured.** Location
2461 calls the spread "stationary with 99 percent probability" and prints no
statistic. [Issue 348](https://github.com/l3a0/quantitative-trading/issues/348)
wrote that the claim holds when jplv7's ADF statistic is below its 1 percent
critical value. A scratch run had already measured −4.727778 when the issue
wrote it, though the build had not run. The criterion reads "99 percent" as
the 1 percent test level, so it left no threshold to choose, and the
statistic clears the line by 1.269478.

Every row reads one vintage and one specification unless it names another, so
both are stated once here.

1. **The vintage.** `data/inputdatadaily_cl_20120813/`, vendor `chan-mat`,
   basis `raw`, saved 2012-08-14, lifted from `inputDataDaily_CL_20120813.mat`,
   the file the script's load line names. It is one vintage per contract, 89 of
   them from CL-2007F to CL-2014K, each a month after the last, and one for
   `CL-SPOT`, over 6,467 days from 1986-11-03. It is read through
   `chan.roll_returns.load_strip`, which runs the scale-break guard on every
   member's own rows and refuses nothing.
2. **The specification.** `calendarSpdsMeanReversion.m` as
   `chan.calendar_spread_reversion` transcribes it. γ is Entry 27's,
   `chan.roll_returns.roll_returns`, forward-filled. The half-life and jplv7's
   `adf(·, 0, 1)` read every finite row of the filled γ, 1,941 of them from
   2004-11-22, and the lookback is the half-life rounded half away from zero,
   36. Contract c is held short against contract c + 12 long, the first pair
   from 73 rows before its near contract's last priced row and each pair to 10
   rows before it. A later pair starts the row after the last one ended and is
   skipped when that leaves fewer than 63 rows. The spread is reversed where z
   is above 0 and flat where z is not a number. The return is yesterday's
   positions times each leg's return, summed over the legs that have one and
   divided by 2. The figures read the 1,164 rows from 2008-01-02 to
   2012-08-13, annualised over 252 days by compounding simple returns, with
   the Sharpe ratio on MATLAB's n − 1 `std`, no risk-free rate and no cost.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2008 to 2012 sample on a rule he chose, and row 10 was found by a scan after
the script's window missed two of the comment's figures.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The half-life of γ, script | 36.394034 | script line 63 |
| 2 | The half-life of γ, book | "a half-life of 36 days" | location 2461 |
| 3 | The APR, script | 0.083406 | script line 123 |
| 4 | The APR, book | 8.3 percent | locations 2461 and 2471 |
| 5 | The Sharpe ratio, script | 1.288661 | script line 123 |
| 6 | The Sharpe ratio, book | 1.3 | locations 2461 and 2471 |
| 7 | The maximum drawdown | −0.053222 | script line 124 |
| 8 | The longest drawdown | 206 days | script line 124 |
| 9 | CL's 12-month log calendar spread is stationary | a claim, "stationary with 99 percent probability" | location 2461 |
| 10 | The specification from 2008-01-03 | none | n/a |
| 11 | The specification holding each pair at least 61 days | none, the book's text says 61 where the script sets 63 | location 2471 |
| 12 | The last day the specification holds a pair | none | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `ou_half_life` on the filled γ's 1,941 finite rows | 36.394034 | `TestTheFigures::test_each_runs_figures` |
| 2 | The same | 36.394034 | `TestTheFigures::test_each_runs_figures`, and `::test_s_and_r1_both_match_the_books_figures` for the rounding |
| 3 | `prod(1 + ret)^(252 / 1164) − 1` | 0.082671 | `TestTheFigures::test_each_runs_figures` and `::test_s_misses_the_comments_apr_and_sharpe_ratio` |
| 4 | The same, in percent | 8.267103 | `TestTheReport::test_each_of_ss_eight_rows_carries_a_verdict`, and `TestTheFigures::test_s_and_r1_both_match_the_books_figures` for the rounding |
| 5 | `√252 · mean(ret) / std(ret)` | 1.278216 | `TestTheFigures::test_each_runs_figures` and `::test_s_misses_the_comments_apr_and_sharpe_ratio` |
| 6 | The same | 1.278216 | `TestTheFigures::test_each_runs_figures`, and `::test_s_and_r1_both_match_the_books_figures` for the rounding |
| 7 | `calculateMaxDD(cumprod(1 + ret) − 1)`, the deepest drawdown | −0.053222 | `TestTheFigures::test_each_runs_figures` |
| 8 | The same, the longest run of days below a high | 206 | `TestTheFigures::test_each_runs_figures` |
| 9 | jplv7's `adf(·, 0, 1)` on the filled γ's finite rows, against its 1 percent critical value | −4.727778 against −3.4583, a margin of 1.269478 | `TestTheTest::test_the_adf_statistic_clears_the_1_percent_critical_value` |
| 10 | Rows 3, 5, 7 and 8 on the 1,163 rows from 2008-01-03 | 0.083406, 1.288661, −0.053222 and 206 days | `TestTheFigures::test_each_runs_figures` and `::test_r1_matches_every_figure_the_scripts_comment_prints` |
| 11 | Rows 3, 5, 7 and 8 with `holddays=61` from 2008-01-02 | 0.067315, 1.044327, −0.098047 and 208 days, last held 2012-07-06 | `TestTheFigures::test_each_runs_figures` and `::test_the_last_held_day_of_s_and_of_r2` |
| 12 | The last row of the unflipped schedule holding a pair, and the window's rows that return exactly 0 | 2012-05-08, and the last 66 rows and no other | `TestTheFigures::test_the_last_held_day_of_s_and_of_r2` and `::test_ss_window_returns_exactly_zero_on_its_last_66_rows_and_no_other` |

Four groups of figures from the scratch run on the issue are unpinned,
because the suite does not run the computation that gave them, and the issue
records them.

1. The scan that found row 10 tried 172,056 windows, 856 starts from
   2006-01-01 to 2009-06-01 against the last 201 ends. Row 10 was the only
   window within 1e-6 on both of the comment's figures, and the next best
   missed by 88e-6.
2. A grid over `holddays` 55 to 70, `numDaysEnd` 5 to 15, the first pair's
   start offset 0 to 20 and the lookback 30 to 42 found no match, and neither
   did the alternatives to the script's division by 2 and to its APR and
   Sharpe ratio formulas.
3. The 2012-05-02 CL save, `data/inputdatadaily_cl_20120502/`, equals the
   2012-08-13 save on all 92,440 priced cells of its 2,867 days.
   `tests/test_futures_strips.py` pins those two counts without running the
   comparison. The save has no spot and ends before the book's window does.
4. Chan's Python port, `calendarSpdsMeanReversion.py`, reads the 2012-05-02
   CSV, measures the whole sample, never assigns its forward fill and divides
   by the gross position. Its comment prints 0.024347, 1.275860 and a
   half-life of 41.095, none of them the book's.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000 | reproduced | Exact at the six decimals the script prints. |
| 2 | +0 | reproduced | 36.394034 rounds to the book's 36. |
| 3 | −0.000735 | did not reproduce | The shipped file under the script's own window misses. Row 10 lands the figure by starting a day later, and nothing committed says which start printed it. |
| 4 | −0.0 percent | reproduced | 8.27 percent rounds to the book's 8.3. |
| 5 | −0.010445 | did not reproduce | The same as row 3. |
| 6 | −0.0 | reproduced | 1.278216 rounds to the book's 1.3. |
| 7 | +0.000000 | reproduced | Exact at the six decimals the script prints. |
| 8 | 0 days | reproduced | Exact. |
| 9 | none, a claim | reproduced | The statistic is below the 1 percent critical value, so the test rejects a unit root at the level "99 percent" names. |
| 10 | none | none, not a replication | It lands every digit the comment prints. It drops 2008-01-02's return of −0.0028127. Setting that day's return to 0 instead gives 0.083331 and 1.288104, which miss both of the comment's figures. So dropping the day lands them and holding it flat does not. It was found by a scan, so it is not evidence of what Chan ran, and rows 3 and 5 keep the window the script states. |
| 11 | none | none, not a replication | Holding at least 61 days misses both book figures, at 6.7 percent and 1.04, so the script's 63 is the specification. Under 61 days a later pair leaves enough rows to be held, to 2012-07-06. |
| 12 | none | none, not a replication | Line 75 marks a contract expired on its last priced row, so the contracts still trading on 2012-08-13 expire on the file's last row, and too few rows remain before it for their pairs to be held. The window's last 66 rows hold nothing and return exactly 0. |

### What the entry concludes

Four things.

1. **Chan's stationarity claim and his rounded figures survive on his own
   file.** The ADF statistic of −4.727778 clears the 1 percent value by
   1.269478, the half-life rounds to 36 days, and the APR and Sharpe ratio
   round to the book's 8.3 percent and 1.3.
2. **Starting a day later lands the comment's APR and Sharpe ratio.** The
   start was chosen because it lands them, by a scan rather than from
   anything the script says. The script reads `tday` in one line,
   `idx=find(tday==20080102)`. For that line to start on the shipped file's
   2008-01-03 row, Chan's own copy of the file would have to label its rows a
   day earlier than the shipped one. The other way to reach it is a run with
   another `idx`. Entry 28's row 5, a window one day shorter found by a
   sweep, set the precedent that such a row carries no verdict.
3. **The last three months of the window hold no position.** Contracts that
   were still trading when the file was saved look expired on its last day,
   so the rule lets go of its last pair on 2012-05-08. The final 66 rows of
   the window earn exactly 0, and the APR spreads the same compounded return
   over those extra days.
4. **The trade bets the spread moves further from its average.** The log
   spread is minus γ times the gap between expiries, so it falls when γ
   rises. On the window's 1,097 held rows the held pair's log spread
   correlates with γ at −0.883910, and its own 36-day z-score has the
   opposite sign to γ's on 841 of them. Line 107 reverses the long-far,
   short-near position where γ's z-score is above 0, so it mostly sells the
   spread low and buys it high. Line 71 still calls the block a "linear mean
   reversion strategy". Reversing every position, the direction location 2471
   describes for γ, gives an APR of −0.080125 and a Sharpe ratio of
   −1.278216. Reversion on the spread's own z-score, closer to location
   2461's words, gives −0.027380 and −0.402360. `TestTheTradesDirection` and
   `TestTheSpreadsOwnAverage` pin them. Writing the post found this. Row 9's
   stationarity still holds, since it reads γ's long-run level rather than
   the direction the trade bets.

### What this entry cannot say

Five things.

**Which day the comment's run started on.** Rows 3, 5 and 10 narrow it to the
script's 2008-01-02 against a start one day later, and nothing committed tells
the two apart.

**The ADF statistic Chan saw.** The script prints it through `prt` and records
no value in its comment, so row 9 checks the book's "99 percent" and not a
number.

**What the lookback would be without hindsight.** The half-life, and so the
36-row lookback, is measured on all of γ, including the 2008 to 2012 window it
trades. Entry 22 names the same limit for USD.CAD's lookback.

**Anything about costs.** None is charged, though each roll trades four legs,
closing one pair and opening the next.

**Whether the direction holds outside 2008 to 2012.** The script's rule also
earns on the file's 332 rows before the window, 0.050334 from 2006-09-05 to
2007-12-31, which `TestBeforeAndAcrossTheWindow` pins. That is the same file
and before costs.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/crude-oil-calendar-spread-lessons.md](../blog/crude-oil-calendar-spread-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.calendar_spread_reversion_figures`
redraws.

## Entry 35: VIX futures calendar spreads on the ratio of back to front, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Chapter 5, Kindle location 2502. Shipped under
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349). No script
ships under the experiment's own name. Example 5.4's
`calendarSpdsMeanReversion.m`, in ericnberwick/EpchanPreview at `e4bc46f`
under `public/img/book2/`, opens with a commented-out load of this strip above
its live CL line, so Chan ran that script on VX. Every location in this entry
is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Ten rows, all derivable from
[tests/test_vx_calendar_spread.py](../tests/test_vx_calendar_spread.py). Eight
do not match one printed figure to one computation, and each says so in its
own cells. Rows 1 and 10 test claims that print no statistic, and rows 4 to 9
carry no published figure.

A VX future is a futures contract on the VIX volatility index. The book's
point is that the VX future does not revert to a mean while the spread between
two of its contracts does, and that no model of the forward curve Chan tried
explains why. VIX is not a traded asset, so Entry 27's model of a future's
price as the spot plus a roll return does not apply, and the evidence is
empirical alone. Each day the z-score of the ratio of a back contract to a
front one over a 15-day lookback decides the side. The spread is reversed when
z is above 0, as in Entry 34.

**The specification misses the trade with the wrong sign, and one of the four
rows declared beside it lands.** The specification, S, passes the book's
stationarity claim. Its APR and Sharpe ratio are negative where the book
prints 17.7 percent and 1.5. B3, which trades the held pair's ratio with
`holddays=0`, rounds to both printed figures on the book's own window, and it
is the only row that does worse before October 2008. B3 was picked out after
the run among five rows, so its match is a search rather than a registered
result.

Every row reads one vintage and one specification unless it names another, so
both are stated once here.

1. **The vintage.** `data/inputdatadaily_vx_20120507/`, vendor `chan-mat`,
   basis `raw`, saved 2012-05-08, lifted from `inputDataDaily_VX_20120507.mat`,
   the file the commented load line names. It is one vintage per contract, 72
   of them from VX-2007F to VX-2012Z, each a month after the last, over 1,543
   days from 2006-03-23 to 2012-05-07, with no spot column. It is read through
   `chan.roll_returns.load_strip`, widened here to a strip with no spot, which
   runs the scale-break guard on every member's own rows and refuses nothing.
2. **The specification.** `calendarSpdsMeanReversion.m` as
   `chan.calendar_spread_reversion` transcribes it, with five edits declared on
   [issue 349](https://github.com/l3a0/quantitative-trading/issues/349) on
   2026-10-05 at `f107b1f`, before any APR, Sharpe ratio or ADF statistic on
   VX was computed.
   1. The VX load line in place of the CL one.
   2. `spreadMonth=1`. The strip lists 2 to 10 contracts a day, and the
      shipped 12 holds 1,284 days, of which 84 have both legs priced, 1,183
      the near leg alone and 17 neither.
   3. The signal is the second-nearest priced contract over the nearest, not a
      number where the two are not adjacent columns, then forward-filled as
      the script fills γ. That leaves only the strip's first 148 rows empty,
      all before 2006-10-23.
   4. `lookback=15` in place of `round(halflife)`.
   5. The window from 2008-10-27 to the file's last row, 2012-05-07, 889 rows.

   Everything else is the script as shipped. jplv7's `adf(·, 0, 1)` and the
   half-life read every finite row of the filled signal. The first pair of
   adjacent contracts starts 73 rows before its near contract's last priced
   row, every pair ends 10 rows before its own, and a later pair is skipped
   when that leaves it fewer than 63 rows. The return is yesterday's positions times each leg's
   return, summed over the legs that have one and divided by 2, annualised
   over 252 days by compounding simple returns, with the Sharpe ratio on
   MATLAB's n − 1 `std`, no risk-free rate and no cost.

Four rows beside S were declared with it, and a row that lands while S misses
is reported and not promoted to the specification.

1. **B1** trades the held pair's ratio, the far contract over the near one
   for the pair the schedule holds that day, filled forward across the days
   nothing is held. The script's own comment calls those two the back and the
   front.
2. **B2** sets `holddays=0`, so each pair is held from the day after the
   previous pair's last day to 10 rows before its own expiry. The first pair
   is never held, because its window is one row, and pairs whose near
   contract still trades on the file's last row are skipped once VX-2012K's
   pair has taken the rows to the end. VX holds 64 of its 71 pairs.
3. **B3** is B1's signal built on B2's schedule, run with `holddays=0`.
4. **B4** is S measured to 2012-04-23, the book's end date, 879 rows.

Every result here is **exploratory**. Reproducing Chan's figures spends his
2006 to 2012 strip on a rule he chose, S is this repo's reading of the book's
text, and B3 was picked out after the run.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The ratio of back to front is stationary | a claim, "stationary with a 99 percent probability" | location 2502 |
| 2 | The APR from October 27, 2008, to April 23, 2012 | 17.7 percent | location 2502 |
| 3 | The Sharpe ratio over the same window | 1.5 | location 2502 |
| 4 | The half-life of S's signal | none, the book gives the lookback as 15 days | n/a |
| 5 | B1, the held pair's ratio | none | n/a |
| 6 | B2, `holddays=0` | none | n/a |
| 7 | B3, B1 and B2 together | none | n/a |
| 8 | B4, S to the book's end date | none | n/a |
| 9 | B3 on the book's window, measured after the run | none | n/a |
| 10 | The strategy "performed much more poorly prior to October 2008" | a claim, with no criterion declared | location 2502 |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | jplv7's `adf(·, 0, 1)` on the filled ratio's 1,395 finite rows, against its 1 percent critical value | −5.568107 against −3.4583, a margin of 2.109807 | `TestTheRows::test_each_rows_figures`, `TestTheRows::test_the_1_percent_critical_value_is_minus_3_4583`, `TestTheClaims::test_ss_adf_statistic_clears_the_1_percent_critical_value` and, for the 1,395 rows, `TestTheSignalsOnVx::test_ss_signal_is_missing_only_on_its_first_148_rows` |
| 2 | `prod(1 + ret)^(252 / 889) − 1`, in percent | −4.045401 | `TestTheReport::test_ss_apr_and_sharpe_ratio_carry_a_verdict` and `TestTheClaims::test_s_misses_the_apr_and_sharpe_ratio_with_the_wrong_sign` |
| 3 | `√252 · mean(ret) / std(ret)` | −0.563912 | `TestTheRows::test_each_rows_figures`, `TestTheReport::test_ss_apr_and_sharpe_ratio_carry_a_verdict` and `TestTheClaims::test_s_misses_the_apr_and_sharpe_ratio_with_the_wrong_sign` |
| 4 | `ou_half_life` on the filled ratio's finite rows | 13.036829, against the 15-day lookback | `TestTheRows::test_each_rows_figures` |
| 5 | B1 | ADF −4.010034, half-life 20.509824, APR 0.033430, Sharpe 0.510861, drawdown −0.161533 over 628 days, last held 2012-03-07. Its half-life on the held rows alone is 15.106686 | `TestTheRows::test_each_rows_figures` and `TestTheSignalsOnVx::test_b1s_fill_moves_its_half_life_from_15_to_20` |
| 6 | B2 | ADF −5.568107, half-life 13.036829, APR −0.113153, Sharpe −0.990744, drawdown −0.404239 over 870 days, last held 2012-04-23 | `TestTheRows::test_each_rows_figures` and `TestTheSignalsOnVx::test_holddays_0_holds_64_of_vxs_71_pairs` |
| 7 | B3 | ADF −4.839517, half-life 16.273041, APR 0.173462, Sharpe 1.457009, drawdown −0.107287 over 166 days, last held 2012-04-23 | `TestTheRows::test_each_rows_figures` and `TestTheClaims::test_b3_rounds_to_the_sharpe_ratio_but_not_the_apr_to_the_files_end` |
| 8 | B4 | APR −0.040905, Sharpe −0.567112, drawdown −0.255618 over 861 days, last held 2012-03-07. Against S, its APR is 0.000451 lower, its Sharpe ratio 0.003199 lower, and its drawdown the same but 10 days shorter | `TestTheRows::test_each_rows_figures` and `TestTheClaims::test_b4_misses_the_same_way_on_the_books_end_date` |
| 9 | B3 on the 879 rows from 2008-10-27 to 2012-04-23 | APR 0.176952, Sharpe 1.475658, last held 2012-04-23 | `TestTheMeasurementsAfterTheRun::test_b3_on_the_books_window` |
| 10 | Each row from the first row its flipped positions hold anything to 2008-10-24 | S from 2006-11-10, 492 rows, −0.027638 and −0.291914. B1 from 2006-11-10, 0.204377 and 2.279855. B2 from 2006-12-29, 459 rows, −0.018707 and −0.091522. B3 from 2007-01-23, 445 rows, −0.074173 and −0.562291 | `TestTheMeasurementsAfterTheRun::test_each_row_before_october_2008` and `::test_only_b3_does_worse_before_october_2008_than_after` |

S's drawdown is −0.255618 over 871 days, and its last held day is 2012-03-07,
which `TestTheRows::test_each_rows_figures` pins with the rest of its row.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, a claim | reproduced | The statistic is below the 1 percent critical value, so the test rejects a unit root at the level "99 percent" names. |
| 2 | −21.7 percent | did not reproduce | S runs on Chan's own file and returns a negative APR, so the vintage explanation is spent. S is a reading of the book's text rather than a script, which is a cause inside the method. |
| 3 | −2.1 | did not reproduce | The same as row 2. |
| 4 | none | none, not a replication | The book prints no half-life for VX. The script's half-life sets its lookback, and the book's 15 days replaces it. |
| 5 | none | none, not a replication | Declared beside S. It is positive where S is negative, and well short of both printed figures. |
| 6 | none | none, not a replication | Declared beside S. Setting `holddays=0` alone makes S worse. |
| 7 | none | none, not a replication | Declared beside S, and the row that lands. Its Sharpe ratio rounds to 1.5. Its APR of 0.173462 misses 17.7 percent on the window to the file's end, a gap of −0.4 percent at the book's precision. It is reported and not promoted, because it was picked out after the run among five rows. |
| 8 | none | none, not a replication | Declared beside S. Ending on the book's date lowers S's APR by 0.000451 and its Sharpe ratio by 0.003199, and shortens its longest drawdown by 10 days, the rows cut. |
| 9 | none | none, not a replication | Measured after seeing rows 1 to 8. Both figures round to the printed 17.7 percent and 1.5. The last held day is the book's printed end date, as B2's is, so the date does not separate B3 from B2. |
| 10 | none, a claim | none, a finding | Only B3 does worse before October 2008 than after it, on both figures, as the claim says. S, B1 and B2 each do better before. No criterion was declared, so the row carries no verdict. |

### What the entry concludes

Two things.

1. **The specification fits the book's first claim and not its trade.** The
   ratio's ADF statistic of −5.568107 clears the 1 percent value by 2.109807.
   Trading it as the book's text describes, with the script's 63-day holding
   period, gives an APR of −4.045401 percent and a Sharpe ratio of −0.563912.
2. **The evidence favours B3 as what Chan ran.** Two things single it out
   from the other four rows.
   1. On the book's window it rounds to both printed figures, 0.176952 and
      1.475658.
   2. It is the only row that does worse before October 2008, as the book's
      third claim says.

   Its last held day, the book's printed end date of 2012-04-23, does not
   single it out, because B2 ends there too. VX-2012K still trades on the
   file's last row, 2012-05-07, so the schedule reads that row as its expiry,
   and under `holddays=0` its pair ends 10 rows earlier, on 2012-04-23. The
   date is evidence for holding each pair until 10 rows before its expiry,
   which B2 and B3 share.

   B3 was picked out after the run among five rows, and the window the first
   point reads was chosen after seeing the table, so this is a search. A
   registered test of B3 on VX data after 2012-05-07 is what would confirm it.

### What this entry cannot say

Four things.

**Which rule Chan ran.** No script ships under the experiment's own name. The
commented load line says which script he ran on VX. The book's text at
location 2502 gives four things.

1. VX as the instrument.
2. The ratio of back to front as the signal.
3. The 15-day lookback.
4. The window, from October 27, 2008, to April 23, 2012.

The rest of S is this repo's reading, in three choices.

1. `spreadMonth=1`, forced by how few contracts the strip prices on a day.
2. No signal where the nearest two priced contracts are not adjacent columns.
3. Measuring to the file's last row, as the script measures to its own,
   rather than to the book's printed end, which B4 does.

**Whether B3's match is more than the best of five.** B3's match was found by
looking at five rows, and the book's window was then measured because B3 had
come closest on the file's window. Choosing among rows after seeing them is the
search `CLAUDE.md`'s research pins put under their own rail.

**The ADF statistic Chan saw.** The book prints none, so row 1 checks the
"99 percent" and not a number.

**Anything about costs.** None is charged. Under `holddays=0`, from
2008-10-27, B3 holds a near leg in 43 pairs, every one from VX-2008X's to
VX-2012K's, and enters 42 of them on or after that date.
`TestTheSignalsOnVx::test_from_2008_10_27_b3_holds_43_pairs_and_enters_42`
pins both counts. Each roll trades four legs.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 36: TU momentum traded on the lagged roll return, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 2690, the revision of Example 6.1
that follows the book's explanation of futures momentum. Shipped under
[issue 353](https://github.com/l3a0/quantitative-trading/issues/353). No
script ships for it. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Fourteen rows, all derivable from
[tests/test_roll_momentum.py](../tests/test_roll_momentum.py). Eight do not
match one printed figure to one computation, and each says so in its own
cells. Row 7 sets two of the book's printed sets against each other with no
computation, and rows 8 to 14 carry no published figure.

Location 2683 explains futures momentum by the roll return, the part of a
future's return that comes from converging on the spot as it nears expiry,
which Entry 27 estimates as γ. The sign of γ rarely changes, so a future held
for a long time keeps earning in one direction. If that is the cause, γ itself
should be a cleaner signal than the past total return Example 6.1 trades.
Location 2690 tries it on TU, the two-year Treasury note future: long when the
lagged γ is above 3 percent, short when it is below −3 percent, and flat
otherwise. It reports a higher APR, a higher Sharpe ratio and a smaller
maximum drawdown than Example 6.1.

**The rule misses all three printed figures and beats Example 6.1 on all
three.** Rows 1 to 3 land well below the book. Rows 4 to 6 hold, because the
revised rule beats Example 6.1's when both run on one series over one window,
and they hold on Chan's own close too.

Every row reads one vintage and one specification unless it names another, so
both are stated once here.

1. **The vintage.** `inputdatadaily_tu_20120813/`, vendor `chan-mat`, basis
   `raw`, saved 2012-08-14, 93 contracts and `TU-SPOT` over 5,565 days from
   1990-06-22 to 2012-08-13, read through `chan.roll_returns.load_strip`,
   which runs the scale-break guard on each member's own rows. This strip is
   the only committed save that covers the book's window. Example 6.1 trades
   the continuous `TU` close of the OHLC saves, and those end in May 2012.
2. **The specification.** The rule
   [issue 353](https://github.com/l3a0/quantitative-trading/issues/353)
   declares, in five parts.
   1. γ is Entry 27's `roll_returns` in the script's column units.
   2. Long where γ > 0.03 and short where γ < −0.03, both strict, with a NaN
      comparison false.
   3. The return is yesterday's position times today's return on the
      rebuilt front contract, with NaN set to 0. With L the held contract's
      last priced row, row t earns `close(t) / close(t−1) − 1` of the nearest
      contract that was priced at t−1 and has L − t ≥ 7, or of the contract
      still trading on the file's last row. So the old contract earns through
      row L − 7 and the new one from row L − 6.
   4. Every series runs on the full 5,565-row index, and the cut to
      2009-01-02 to 2012-08-13, 913 rows, comes last.
   5. The figures are `TU_mom.m`'s arithmetic, through
      `chan.tu_momentum.figures`, annualised over 252 days with no risk-free
      rate and no cost.

   Example 6.1's rule, for rows 4 to 6, is `chan.tu_momentum`'s own
   `signals` on the rebuilt level, then `positions`, then `strategy_returns`
   on the rebuilt return. The level adds up the held contract's price changes,
   which is an additive back-adjustment.

**The rule was declared after the scratch runs.** The issue said these
choices had to be declared before any figure was computed. Two scratch runs
read about 90 variants first, a count from the issue's disclosure that no
test here pins, across lags, held contracts, units, thresholds
and roll rules, and one of them came close to the book. The declaration rests
on grounds the runs did not choose. The lag is Example 6.1's own convention,
the series is the one the book says it revises, and the roll row was read off
the 2012-05-11 save rather than chosen by any strategy figure. Row 14 is the
reading that came close, and it is never the verdict.

Every result here is **exploratory**. The declaration came after the
readings, so this entry cannot count as a registered test of the roll-return
signal either. A registered test would
declare its rule before any reading and run it on data this search never
loaded.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The APR | 2.5 percent | location 2690 |
| 2 | The Sharpe ratio | 2.1 | location 2690 |
| 3 | The maximum drawdown | 1.1 percent | location 2690 |
| 4 | A higher APR than Example 6.1 | a claim, "a higher APR" | location 2690 |
| 5 | A higher Sharpe ratio than Example 6.1 | a claim, the same "higher" | location 2690 |
| 6 | A smaller maximum drawdown than Example 6.1 | a claim, "a reduced maximum drawdown" | location 2690 |
| 7 | The book's own comparison | rows 1 to 3 against Example 6.1's 1.7 percent, 1 and 2.5 percent | locations 2690 and 2668 |
| 8 to 14 | Example 6.1 cut first, the rebuild against the save, both rules on the save, the position's shares, the flat start, the month-unit γ and the fifth contract | none here, as each row says | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + ret)^(252/913) − 1` under the declared rule | 0.013725 | `TestTheSixRows::test_row_1_the_apr_misses` |
| 2 | `√252 · smartmean(ret) / smartstd(ret)` | 1.803348 | `TestTheSixRows::test_row_2_the_sharpe_ratio_misses` |
| 3 | `calculateMaxDD(cumprod(1 + ret) − 1)` | −0.007299 | `TestTheSixRows::test_row_3_the_maximum_drawdown_misses` |
| 4 | the declared rule's APR less Example 6.1's on the same series and rows, which is 0.013377 | +0.000348 | `TestTheComparisonMargins::test_each_margin` and `::test_example_6_1_on_the_rebuild` |
| 5 | the same for the Sharpe ratio, against 1.196742 | +0.606606 | the same |
| 6 | Example 6.1's drawdown magnitude less the declared rule's, against −0.009167 | +0.001868 | the same |
| 7 | none, the book's figures alone | n/a | `TestTheRowsBeside::test_the_book_s_own_comparison` |
| 8 | Example 6.1's rule with the window cut before any series is computed | APR 0.008435, the signal live on 663 of 913 rows | `TestTheComparisonMargins::test_cutting_the_window_first_moves_example_6_1` |
| 9 | the rebuild against `inputdataohlcdaily_20120511/tu.csv`, chan-mat, adjusted, saved 2012-05-12, over the 1,999 changes they share | return correlation 0.998359. 30 changes differ by more than 1.5e-4, all on row L − 7, and the span holds 32 rolls | `TestTheRebuildAgainstTheSave::test_the_two_agree_on_every_day_but_the_jump_row` and `::test_the_save_s_span_holds_32_rolls` |
| 10 | both rules over the 849 window rows that save covers, on its own close and on the rebuild | the declared rule 1.437321 percent, 1.791969 and −0.807695 percent on the save, and 1.468184 percent, 1.870808 and −0.729860 percent on the rebuild. Example 6.1 1.445672 percent, 1.250783 and −0.916666 percent on the rebuild, and Entry 33's row 12 on the save | `TestTheRowsBeside::test_the_revised_rule_on_the_save_s_own_close`, `::test_both_rules_on_the_rebuild_over_the_same_rows` and `::test_example_6_1_on_the_save_is_entry_33_s_pin` |
| 11 | the position each window row earns on | long on 572 of 913 rows, 62.65 percent, short on 0, 21 changes | `TestTheRowsBeside::test_the_rule_is_long_or_flat_and_never_short` |
| 12 | γ on the last day before the window and its first three days | 0.0161092 on 2008-12-31, and below 1e-13 in size on 2009-01-02, 01-05 and 01-06 | `TestTheRowsBeside::test_the_window_starts_flat` |
| 13 | `roll_returns_in_months` under the same threshold, and γ's window mean | a third of γ on every row where γ is defined, a peak of 0.02447, flat on all 913 rows. γ's mean is 0.035943 | `TestTheRowsBeside::test_the_month_unit_gamma_never_trades` and `::test_gamma_has_no_nan_in_the_window` |
| 14 | the declared position held on the fifth contract priced the day before, and on the fifth of those priced on both days | 0.024712, 2.144165 and −0.011583, and a Sharpe ratio of 1.957852 | `TestTheRowsBeside::test_the_fifth_contract_reading` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −1.1 percent | did not reproduce | Under the declared rule, 1.3725 percent against 2.5. Chan's own close covers 849 of the 913 rows and lands near the rebuild under row 10, so the vintage explanation is not available. The 64 rows that save does not cover would have to carry the rest, and Entry 33's row 13 found TU's close the same on every day two saves share. A miss also cannot tell a different number from a different reading of location 2690, and the reading is part of the method. |
| 2 | −0.3 | did not reproduce | Under the declared rule, 1.803348 against 2.1, for the reason row 1 gives. |
| 3 | −0.4 percent | did not reproduce | Under the declared rule, a drawdown of 0.7299 percent against 1.1, for the reason row 1 gives. This miss runs the other way from rows 1 and 2, a shallower drawdown than the book printed. |
| 4 | none, a claim | reproduced | 0.013725 against 0.013377. The margin, +0.000348, is about the size of the rebuild's own error, since the rebuild's APR over row 10's 849 rows sits 0.000309 above the save's, which `TestTheComparisonMargins::test_row_4_s_margin_is_about_the_rebuild_s_own_error` holds. The claim holds on the save's own close as well, 1.437321 percent against Entry 33's 1.4069. |
| 5 | none, a claim | reproduced | 1.803348 against 1.196742, and 1.791969 against 1.187438 on the save. |
| 6 | none, a claim | reproduced | −0.007299 against −0.009167, and −0.807695 percent against −0.9851 percent on the save. |
| 7 | none | none, not a replication | The book's 2.5 percent, 2.1 and 1.1 percent are higher, higher and smaller than Example 6.1's printed 1.7 percent, 1 and 2.5 percent. Those sit on 2004-06-01 to 2012-05-11 rather than this window, so the book's own sentence compares two windows, which is why rows 4 to 6 run both rules on one. |
| 8 | none | none, not a replication | Cutting first leaves Example 6.1's 250-day signal off for the window's first 250 rows, so rows 4 to 6 would compare against a rule that is not trading for much of the window. |
| 9 | none | none, not a replication | The save follows the same contracts as the rebuild on every row but row L − 7, where its back-adjustment jumps and the rebuild takes a return within one contract instead. |
| 10 | none | none, not a replication | The rebuild's error over these rows is a small part of the gap to the book. |
| 11 | none | none, not a replication | γ stays above about 0 in the window, so the rule is long or flat and never short. |
| 12 | none | none, not a replication | All five contracts share one price on the three days, so γ is about 0 there and the window opens flat. |
| 13 | none | none, not a replication | Every contract is a quarter from the next, so the month reading divides γ by 3 and never reaches the threshold. That is why the declared rule reads γ in column units. |
| 14 | none | none, not a replication | Lands 2.5 percent and 2.1 at the book's precision, and misses the 1.1 percent drawdown. It came out of the scratch search, and a scratch fit of γ on the four nearest contracts, which no test here repeats, gave it a Sharpe ratio of 1.801. So the match leans on γ moving against the held contract's own price. |

### What the entry concludes

Three things.

1. **The roll-return signal beats Example 6.1's on TU, by little on the
   APR.** Rows 4 to 6 hold on the rebuild and on Chan's own close. The Sharpe
   ratio's margin is the large one. Row 4's margin is about the size of the
   rebuild's own error, so the APR half of the claim is the weakest of the
   three. In this window Example 6.1 holds all 25 tranches long on every
   row, so it is holding TU, and the declared rule is that position with 341
   rows taken out, which `TestWhatTheMarginsAreMadeOf` holds.
2. **The declared rule lands none of the book's figures, and the reading
   that comes close is suspect.** Row 14 lands two of rows 1 to 3 by holding a
   contract γ is fitted on. A scratch fit that left that contract out fell to
   a Sharpe ratio of 1.801, which no test here repeats. So the fit's own use
   of the held contract's price is a candidate for what lifts row 14, not a
   finding, and the entry cannot say which reading Chan held.
3. **The book's comparison spans two windows.** Example 6.1's printed figures
   run from 2004 and these from 2009. On one window the declared rule's APR
   margin is 0.000348, far smaller than the gap between the printed 2.5 and
   1.7 percent.

### What this entry cannot say

Four things.

**Whether the signal works out of sample.** The rule was declared after about
90 readings on the same strip, so its margins are not a test. A registered
test would fix the rule first and read data this search never loaded.

**What Chan held.** No script ships for location 2690, and the book does not
say how far the roll return is lagged or which price the position earns. Row
14 shows a reading that lands near the book, and choosing it after its number
was seen would be a search.

**What a trader would earn.** The returns are on the notional value of one
contract with no cost and no margin, as in Entry 33.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/roll-momentum-lessons.md](../blog/roll-momentum-lessons.md) moves with
it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.roll_momentum_figures` redraws.

## Entry 37: three hypothesis tests on TU momentum, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 1.1, Kindle locations 606 to 674, with the
count repeated at location 2923. Shipped under
[issue 352](https://github.com/l3a0/quantitative-trading/issues/352). The
script is `TU_mom_hypothesisTest.m`, in ericnberwick/EpchanPreview at
`e4bc46f` under `public/img/book2/`, git blob `c0dda16`, and the line numbers
below are that blob's. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eight rows, all derivable from
[tests/test_tu_hypothesis_tests.py](../tests/test_tu_hypothesis_tests.py).
Four do not match one printed figure to one computation, and each says so in
its own cells. Row 5 runs a test that cannot fail, and rows 6 to 8 carry no
published figure. Rows 2 and 3 judge one computed count, against the book's
figure and against the script's.

A backtest's average return means little until it is set against what chance
alone would give. Example 1.1 asks that of Entry 33's TU momentum strategy
three ways. The first test reads the strategy's daily returns as Gaussian. The
second reruns the strategy on 10,000 simulated series of TU market returns
that share the observed mean, standard deviation, skewness and kurtosis. The
third shuffles the strategy's long and short entry days 100,000 times. Each of
the last two counts how many draws earn an average return at or above the
observed one. The book reads the second test's count as showing that "any
random returns distribution with high kurtosis can be favorable to momentum
strategies" (location 674).

**The book's count reproduces, the script's does not, and two of the rows
beside them point at TU's drift rather than its kurtosis.** The second test lands
inside the band around the book's 1,166 and far outside the one around the
script's 0.027500. Rows 6 to 8 were added after a scratch run had seen
results, and they show that a normal draw gives the same count while removing
the drift removes almost all of it.

Every row reads one vintage and one specification unless it names another, so
both are stated once here.

1. **The vintage.** `inputdataohlcdaily_20120511/tu.csv`, vendor `chan-mat`,
   basis `adjusted`, saved 2012-05-12, TU's column of Chan's
   `inputDataOHLCDaily_20120511.mat`, the file the script loads. Its own rows
   are 2,000 days from 2004-06-01 to 2012-05-11, read through
   `chan.tu_momentum.read_sources`, which runs the scale-break guard over that
   span and refuses nothing.
2. **The specification.** Entry 33's strategy, through `chan.tu_momentum`'s
   own functions, with a lookback of 250 and a hold of 25. The rest is the
   declaration
   [issue 352](https://github.com/l3a0/quantitative-trading/issues/352) wrote
   before any draw on either seed, in four parts.
   1. The second test takes L43's moments of the 2,000 market returns, the
      first of which is 0: the mean, MATLAB's n − 1 `std`, and the biased
      skewness and kurtosis, with kurtosis not in excess form. It draws series
      i of 10,000 from row i of `default_rng(20261010).random((10_000,
      2_000))` through the Pearson type IV inverse CDF, builds `cl_sim =
      cumprod(1 + r) − 1`, reruns the strategy on it, and earns the simulated
      returns themselves, as L68 does.
   2. The corrected third test applies draw d of 100,000
      `default_rng(20261011).permutation(2_000)` calls to both signal arrays,
      which keeps 1,274 long days and 474 short days, rebuilds the positions
      and earns the observed market returns.
   3. A count lands when it lies within two binomial standard errors of the
      printed figure, using the printed proportion and the test's own N. That
      gives 1,102 to 1,230 for the book's 1,166, 243 to 307 for the script's
      0.027500 at N = 10,000, and only 0 for the book's 0 of 100,000.
   4. This is Chan's own saved file, so the vintage explanation is spent, and
      a count outside its band did not reproduce.

**Type IV is an inference about `pearsrnd`.** `pearsrnd` picks a member of
the Pearson family from the four moments, and MathWorks' page names the types
without stating its criterion. The standard criterion, as Heinrich (2004)
gives it, puts TU's moments in type IV, at a κ of 0.004645. If `pearsrnd`
chose the same type, these draws follow the script's null in distribution,
though not draw for draw.

**The third test cannot fail as written.** L88 sets `pos_sim` to zeros, and
L99 and L100 then add the shuffled tranches to `pos`, the observed positions,
rather than to `pos_sim`. So every simulated return at L103 is zero, the
observed mean is positive, and the count is 0 whatever the data. Row 5 runs
that loop and row 4 runs the corrected test.

**Rows 6 to 8 were added after the scratch run saw results.** Each varies one
input of row 2 to test a reason the book gives, and each runs on row 2's
uniforms, so it differs from row 2 in that input alone. None is a candidate
for a better p-value.

Every result here is **exploratory**. The three tests are Chan's, on a
strategy whose lookback and hold he picked from a table computed on the same
closes. Rows 6 to 8 were chosen after a scratch run, so they can motivate a
registered test of the drift reading and cannot confirm it.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The Gaussian test statistic, mean / std · √n | 2.93 | `TU_mom_hypothesisTest.m`'s comment at L40, and the statistic's definition at location 606 |
| 2 | The randomized-returns test, draws at or above the observed mean | 1,166 of 10,000 | location 665 |
| 3 | The same test's p-value | 0.027500 | the script's comment at L77 |
| 4 | The randomized-trades test, corrected | 0 of 100,000 | location 672 |
| 5 | The randomized-trades test, as written | 0, as location 672 prints it | location 672, and the script's L82 to L113 |
| 6 to 8 | the observed positions on the simulated returns, a normal draw, and type IV with the mean set to zero | none here, as each row says | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `mean(ret) / std(ret) · √2000` with the n − 1 `std` | 2.933253, and a one-sided normal tail of 0.001677 | `TestRow1TheGaussianStatistic::test_it_lands_the_script_s_2_93` and `::test_its_one_sided_normal_tail` |
| 2 | the declared second test, seed 20261010 | 1,221 of 10,000 | `TestRows2And3TheRandomizedReturns::test_the_count` and `::test_row_2_lands_the_book_s_1166` |
| 3 | the same count as a proportion | 0.122100 | `TestRows2And3TheRandomizedReturns::test_row_3_misses_the_script_s_0_027500` |
| 4 | the corrected third test, seed 20261011 | 0 of 100,000. The largest simulated mean is 3.973594e-05 against the observed 6.626644e-05, which sits 11.131886 standard deviations above the simulated means' average | `TestRow4TheCorrectedTrades::test_no_draw_reaches_the_observed_mean` and `::test_how_far_the_observed_mean_sits_above_them` |
| 5 | the third test as written, 10 draws on seed 20261011 | 0 of 10, every simulated return 0, and every draw's tranches added to the observed positions | `TestRow5TheAsWrittenTrades::test_ret_sim_is_zero_on_every_draw` and `::test_the_tranches_land_in_pos` |
| 6 | the observed positions applied to row 2's simulated returns, added after the scratch run | 277 of 10,000, 0.027700 | `TestTheRowsBesideAddedAfterTheScratchRun::test_the_observed_positions_on_the_simulated_returns` |
| 7 | a normal draw with TU's mean and `std` on row 2's uniforms, added after the scratch run | 1,165 of 10,000, 0.116500 | `TestTheRowsBesideAddedAfterTheScratchRun::test_a_normal_draw_with_tu_s_mean_and_std` |
| 8 | row 2's draws less their target mean, added after the scratch run | 19 of 10,000, 0.001900. The simulated means average 3.604899e-07, against 3.220302e-05 for row 2. Over row 2's first 1,000 draws the rule is long on 0.804654 of signal days on average, and 0.502401 with the mean removed | `TestTheRowsBesideAddedAfterTheScratchRun::test_type_iv_with_the_mean_set_to_zero`, `::test_the_drift_is_what_the_strategy_earns_on_simulated_returns` and `::test_a_drifting_series_is_long_on_most_signal_days` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.00 | reproduced | 2.933253 rounds to the printed 2.93. Entry 33's row 15 pins the same figure. |
| 2 | +55 | reproduced | 1,221 lies inside 1,102 to 1,230, nine counts from the band's top. |
| 3 | +0.094600 | did not reproduce | 0.122100 lies far outside 243 to 307 of 10,000. So the second test this file carries does not give the script's comment on Chan's own file. Row 6 is the one test found to land it. |
| 4 | +0 | reproduced | No draw of 100,000 reaches the observed mean, so the rule-of-three bound puts the p-value below 3e-05 at 95 percent. |
| 5 | none | none, a finding | The count cannot fail, so it cannot reproduce anything. It is 0 because no draw writes to `pos_sim`, not because of any property of TU. |
| 6 | none | none, not a replication | 277 lies inside the script's 243 to 307. Nothing in the script applies the observed positions to simulated returns, and the file has one commit, so the match is numerical rather than recovered history. |
| 7 | none | none, not a replication | Removing the skewness and kurtosis moves the count little, 1,165 against 1,221. |
| 8 | none | none, not a replication | Removing the drift takes the count from 1,221 to 19, close to the 0.001677 one-sided tail of row 1's Gaussian statistic. |

### What the entry concludes

Three things.

1. **The book's 1,166 reproduces and the script's 0.027500 does not.** A type
   IV generator with the script's moments lands inside the band around the
   book's count on Chan's own file, so location 665's figure is consistent
   with the test the script carries. The script's printed p-value lands only
   on row 6, a different test that nothing in the file runs.
2. **On this file, two of the rows beside point at TU's drift rather than
   its kurtosis as what drives the second test.** A normal draw with TU's mean and
   `std` gives 1,165 where type IV gives 1,221, so the shape location 674
   credits moves the count by little. Setting the mean to zero gives 19, near
   the Gaussian test's one-sided 0.001677. The mechanism is the rule itself. A
   series with a positive drift has a positive 250-day return most of the
   time, so the strategy is long most of the time and collects the drift,
   which location 665's aside calls less likely because "the position can be
   long or short". Over the first 1,000 declared draws, the strategy is long
   on about 80 percent of signal days, against about 50 at a mean of zero.
   Rows 7 and 8 were added after the scratch run, so this is a reading the
   entry motivates and does not confirm.
3. **The third test gives 0 for a reason the script does not show.** As
   written it cannot give anything else. Corrected, it still gives 0 of
   100,000, so location 672's sentence stands, and the observed mean sits
   11.131886 standard deviations above what shuffled entry days earn. The
   corrected test keeps each day's return and moves only the days, so what it
   rejects is the claim that TU momentum's timing earns nothing beyond its mix
   of long and short days.

### What this entry cannot say

Four things.

**Which Pearson type `pearsrnd` drew from.** The type IV choice is inferred
from the standard criterion rather than read from MathWorks' code. If
`pearsrnd` drew from another type with the same four moments, row 2 judges a
different null. Rows 7 and 8 suggest the count barely depends on the shape,
which limits what a different type could move.

**What computed the script's 0.027500.** Row 6 lands it with a test the
script does not contain, and the file has one commit, so the history behind
that comment is gone.

**Whether drift explains momentum's significance elsewhere.** Rows 6 to 8
were chosen after a scratch run on other seeds had seen results, on one
strategy and one future. A registered test would declare the drift reading
first and run it on data this entry never loaded.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/tu-hypothesis-tests-lessons.md](../blog/tu-hypothesis-tests-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.tu_hypothesis_tests_figures` redraws.

## Entry 38: long GLD and short gold futures, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle locations 2718 and 2730, in Chapter 6's
discussion of roll returns. Shipped under
[issue 355](https://github.com/l3a0/quantitative-trading/issues/355). The
script is `GLD_GC.m`, in ericnberwick/EpchanPreview at `e4bc46f` under
`public/img/book2/`. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from
[tests/test_gld_gc.py](../tests/test_gld_gc.py). Five do not match one
printed figure to one computation, and each says so in its own cells. Row 6
checks one printed figure against two computations, because the text's
"annualized return" could be either of the two the script prints, and rows 8
to 11 carry no published figure.

A future's total return is its spot return plus its roll return, the part
that comes from converging on the spot as it nears expiry. Gold futures carry
a negative roll return, so owning the metal and shorting the future should
collect it. GLD owns physical gold, which makes it the long leg. Location 2718
reports that the trade "yields an annualized return of 1.9 percent and a
maximum drawdown of 0.8 percent from August 3, 2007, to August 2, 2010". It
then spends the result. GLD's financing cost "is not very different from 1.9
percent over the backtest period", so "the excess return of this strategy is
close to zero".

**Every figure reproduces, and the bill rate takes about half of the
return.** Rows 1 to 7 land on the printed digits. Row 8 sets the three-month
bill rate over the window against the return. The bill rate is a floor on what
financing GLD costs, so it neither confirms nor refutes the book's "close to
zero".

Every row reads two vintages and one specification unless it names another,
so they are stated once here.

1. **The vintages.** GC is `inputdata_gc_1600_20100802/gc.csv`, vendor
   `chan-mat`, basis `raw`, saved 2012-05-07, 761 rows from 2007-08-03 to
   2010-08-02, the book's window exactly. GLD is `inputdata_etf/gld.csv`,
   vendor `chan-mat`, basis `adjusted`, saved 2012-04-10. GLD pays no
   dividend, so its adjusted close is its close. The scale-break guard reads
   each over the window on its own calendar and flags nothing.
2. **The specification S.** `GLD_GC.m` as shipped. The two calendars are
   intersected, which keeps 752 days. `ret` is GLD's daily return minus
   GC's, each taken across the kept rows, with every NaN set to 0, which
   zeroes the first row. The script then prints `252 · smartmean(ret)`, the
   Sharpe ratio `√252 · smartmean(ret − rf) / smartstd(ret − rf)` with
   `rf = 0.02 / 252` and book two's divide-by-n `smartstd`, the APR
   `prod(1 + ret)^(252/752) − 1`, and `calculateMaxDD(cumprod(1 + ret) − 1)`.

**The criterion was declared before any figure.**
[Issue 355](https://github.com/l3a0/quantitative-trading/issues/355) wrote S
and its criterion on 2026-10-10 at `a331fea`, before any of the five figures
had been computed. A printed figure reproduces when the computed one rounds to
it at the decimals it prints, through `chan.khandani_lo_book_two.matches`, and
the duration reproduces when it equals 91. The text's 1.9 and 0.8 percent are
checked the same way at one decimal. One disclosure goes with it. A
measurement of the series made before the criterion printed the ratio
GC / GLD on its first and last days, 10.822 and 10.235, and their drift
implies roughly the book's annual return. The criterion is the rule earlier
book-two entries already use, so it was not chosen against that.

Every result here is **exploratory**. The window is the book's own, so
reproducing its figures spends no fresh sample, and nothing here tests the
trade on later data.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The average annual return | 0.0190 | `GLD_GC.m`'s closing comment, no location |
| 2 | The Sharpe ratio | −.07 | the same comment |
| 3 | The APR | 0.0191 | the same comment |
| 4 | The maximum drawdown | −0.008247 | the same comment |
| 5 | The maximum drawdown's duration | 91 days | the same comment |
| 6 | The annualized return | 1.9 percent | location 2718 |
| 7 | The maximum drawdown | 0.8 percent | location 2718 |
| 8 | The financing cost | none, "not very different from 1.9 percent" | location 2718 |
| 9 to 11 | The two calendars, the series against the OHLC save's GC, and the daily change in log(GC / GLD) | none here, as each row says | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · smartmean(ret)` under S | 0.019014 | `TestTheBooksFigures::test_row_1_the_average_annual_return_reproduces` |
| 2 | `√252 · smartmean(ret − rf) / smartstd(ret − rf)` | −0.066564 | `TestTheBooksFigures::test_row_2_the_sharpe_ratio_reproduces` |
| 3 | `prod(1 + ret)^(252/752) − 1` | 0.019084 | `TestTheBooksFigures::test_row_3_the_apr_reproduces` |
| 4 | `calculateMaxDD(cumprod(1 + ret) − 1)` | −0.0082465 | `TestTheBooksFigures::test_row_4_the_maximum_drawdown_reproduces` |
| 5 | the same call's duration | 91 | `TestTheBooksFigures::test_row_5_the_drawdown_lasts_91_days` |
| 6 | rows 1 and 3 in percent | 1.901433 and 1.908382 percent | `TestTheBooksFigures::test_row_6_the_text_s_1_9_percent_reproduces_on_both_returns` |
| 7 | row 4 in percent, in size | 0.824652 percent | `TestTheBooksFigures::test_row_7_the_text_s_0_8_percent_reproduces` |
| 8 | B1, FRED's TB3MS, `rate`, downloaded 2026-09-30, averaged over August 2007 to August 2010 through `chan.bill_rates.average`, and row 1 less it | 0.010141 over 37 months, leaving +0.008874 | `TestTheFinancingCost::test_the_bill_rate_over_the_window` and `::test_what_is_left_above_it` |
| 9 | the rows GC holds and GLD lacks, and the reverse inside the window | 9 GC rows, 2007-11-22, 2008-01-21, 2008-02-18, 2008-05-26, 2008-07-04, 2008-09-01, 2008-11-27, 2009-01-19 and 2009-02-16, each a US exchange holiday. 3 GLD rows, 2007-09-19, 2007-12-24 and 2009-12-24 | `TestTheSeriesIdentity::test_gc_holds_9_us_exchange_holidays_gld_lacks` and `::test_gld_holds_3_days_gc_lacks` |
| 10 | GC against the GC close of `inputdataohlcdaily_20120507/gc.csv`, chan-mat, adjusted, saved 2012-05-09, a continuous series shifted at each roll, on the 752 kept days, and the lag-1 autocorrelation of the daily change in this GC less that one | equal on 0 of 752, the nearest 9.30 apart, daily return correlation 0.824035, autocorrelation −0.559953 | `TestTheSeriesIdentity::test_the_ohlc_save_s_gc_never_equals_it`, `::test_their_daily_returns_correlate_at_0_82` and `::test_their_difference_reverses_the_next_day` |
| 11 | the daily change in log(GC / GLD) over the 752 kept days, for each GC series: its standard deviation over n, its largest move, and its moves past 2 percent. Then GLD's daily log return over the same days, its standard deviation over n, and half the squared ratio of this GC's figure to it, the most of GLD's daily variance a gap between the two closes can carry | 0.000933, 0.007082 and none on this GC. 0.009243, 0.097332 and 20 on the OHLC save's. GLD's 0.015660, so at most 0.001775 | `TestTheSeriesIdentity::test_the_log_ratio_moves_little_on_the_16_00_series`, `::test_the_log_ratio_moves_ten_times_as_much_on_the_ohlc_save` and `::test_a_gap_between_the_closes_carries_at_most_0_18_percent_of_gld_s_variance` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | Chan's own saves under his own script land the printed digits, as the criterion asks. |
| 2 | 0.00 | reproduced | The same. The risk-free rate of 2 percent a year is what makes it negative, which `TestTheBooksFigures::test_the_sharpe_ratio_rounds_to_the_book_only_with_the_risk_free_rate` holds. |
| 3 | 0.0000 | reproduced | The same as row 1. |
| 4 | 0.000000 | reproduced | The same as row 1. |
| 5 | 0 | reproduced | The same as row 1. |
| 6 | 0.0 percent on both | reproduced | Both of the script's annual returns round to 1.9 percent, so the text's figure does not have to be assigned to one of them. |
| 7 | 0.0 percent | reproduced | The same as row 1. |
| 8 | none | none, not a replication | Declared beside S. The bill rate takes 1.0141 percent of the 1.9014 percent, so 0.8874 percent is left above it. The book gives no bound for "not very different", so this row carries no verdict. The bill rate is a floor on financing, because a trader borrows above it, and the book's "close to zero" is a claim about the rate a trader pays. |
| 9 | none | none, not a replication | A settlement series has no row on a day the exchange is shut, and this series has 9 such rows. So it is not the 1:30 p.m. settlement location 2730 describes. |
| 10 | none | none, not a replication | The two are different series, and the OHLC save is the one shifted at each roll. A shifted series would equal no unshifted one at any hour, so never equalling this one says nothing about when this one is read. The daily change in their difference reverses the next day, at an autocorrelation of −0.559953. A gap in timing predicts that, because one day's move between the two hours comes back the day after. A shift at a roll is a step that stays, so it predicts no reversal. |
| 11 | none | none, not a replication | This row says when the series is read. If GC were read at 1:30 p.m. and GLD at 4:00 p.m., the daily change in log(GC / GLD) would hold two gold returns over those two and a half hours, one from each day, and anything else that moves the ratio only adds to it. Its standard deviation of 0.000933 against GLD's 0.015660 leaves room for at most 0.001775 of GLD's daily variance in that gap. Two and a half hours is about a tenth of a day on the clock, in a market that trades nearly around it, so the gap is not there. The OHLC save's GC moves against GLD ten times as much, which its rolls and a price read at another hour both feed. |

### What the entry concludes

Three things.

1. **Chan's saves reproduce his script exactly.** All five figures of the
   closing comment and both of the text's land on the printed digits.
2. **The series the script reads is GC read within minutes of GLD's 4:00
   p.m. close, not the 1:30 p.m. settlement.** Row 11 is the evidence for the
   hour. A gap of two and a half hours between the two closes could carry at
   most 0.001775 of GLD's daily variance, far below the tenth of a day those
   hours take. Row 9 adds that the series is not a settlement series, because
   it has rows on 9 days the exchange was shut. Location 2730 warns that GC
   settles two and a half hours before GLD closes. That gap is not in the
   series the script reads, so the asynchronicity the book excuses is not in
   the backtest.
3. **The bill rate leaves about half the return standing.** Over the window
   it averages 1.0141 percent against a return of 1.9014 percent. The book's
   "close to zero" needs GLD's financing to sit about 0.89 percent a year
   above the bill rate. Whether its holders paid that is not something this
   repo holds data on.

### What this entry cannot say

Four things.

**What financing GLD actually cost.** The bill rate is a floor. A broker's
rate on a long ETF position sits above it by a spread this repo has no data
for, so row 8 bounds the excess return from above and cannot say whether it
is close to zero.

**Whether the trade would work on the 1:30 p.m. settlement.** That needs the
OHLC save's GC, whose returns are shifted at each roll and need their own
reading. The issue puts it out of scope.

**Whether the trade works after 2010.** The window is the book's, and nothing
here reads later data.

**Gold's roll return over 1982 to 2004.** Location 2718 cites "a negative roll
return of −4.9 percent annualized from December 1982 to May 2004" as the
reason to try the trade. The entry cites it and does not reproduce it, because
the earliest gold futures series here starts in May 2004, the month that span
ends.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 39: XLE against USO signed by crude oil's contango, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 2734 and Figure 6.3, in Chapter 6.
Shipped under [issue 356](https://github.com/l3a0/quantitative-trading/issues/356).
The script is `XLE_CL_rollReturn.m`, in ericnberwick/EpchanPreview at
`e4bc46f` under `public/img/book2/`, git blob `e9b8981`, and the line
numbers below are that blob's. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seven rows, all derivable from
[tests/test_xle_uso_roll_return.py](../tests/test_xle_uso_roll_return.py).
Each matches one printed figure to one computation. Rows 6 and 7 are the
book's rounded forms of what rows 3 and 2 compute.

No ETF holds physical crude oil, so no ETF pair can collect crude's roll
return the way GLD against a gold future can. Location 2385 says a fund of
oil producers such as XLE "usually cointegrates with the spot price", and
location 1939 that USO "invests in oil futures contracts", so USO earns the
roll return on top of the spot and XLE does not. Location 2718 defines
contango as a negative roll return, with the far contract priced above the
near one. Location 2734 trades the gap: short USO and long XLE whenever CL is
in contango, and the reverse in backwardation, for an APR of "a very
respectable 16 percent" from 2006-04-26 to 2012-04-09 "with a Sharpe ratio of
about 1".

**All five of the script's figures and both of the book's reproduce on
Chan's own files.** The text and the script describe one run. The book's
16 percent is the script's APR of 0.1591, and its "about 1" is the script's
Sharpe ratio of 1.05.

**A scratch run came before the criterion.** The order was not the one this
repo asks for. A research pass on the issue ran a scratch transcription and
saw all five figures before the issue wrote down what a landing figure is.
The criterion it then fixed is the rule every earlier entry uses: a figure
lands when the computed value rounds to the printed string at the decimals
the string carries, which is `chan.khandani_lo_book_two.matches`. Nothing in
it was chosen to fit the run, and there is one specification with no rows
beside it.

Every row reads two vintages and one specification, so they are stated once
here.

1. **The vintages.** Two of Chan's book-two files, both vendor `chan-mat`.
   1. `data/inputdata_etf/`, lifted from `inputData_ETF.mat`, basis
      `adjusted`, saved 2012-04-10. USO and XLE hold 1,500 closes each from
      2006-04-26 to 2012-04-09 with none missing. The file subtracts each
      dividend in dollars from every earlier close, which
      [data/README.md](../data/README.md) records.
   2. `data/inputdatadaily_cl_20120502/`, lifted from
      `inputDataDaily_CL_20120502.mat`, basis `raw`, saved 2012-05-03. It is
      one vintage per contract, 89 of them from CL-2007F to CL-2014K, over
      2,867 days from 2000-11-20, with no spot column. It is read through
      `chan.roll_returns.load_strip`, which runs the scale-break guard on
      every contract's own rows and refuses nothing.
2. **The specification.** `XLE_CL_rollReturn.m` as
   `chan.xle_uso_roll_return` transcribes it. The ratio is each contract's
   successor in the strip over the contract, on the rows the contract is the
   front. A contract is the front from 40 to 10 rows before its last priced
   row, and a later contract starts no earlier than the row after the
   previous front ended. Every other row carries a NaN ratio. On the 1,498
   days both calendars hold, a ratio above 1 is short USO and long XLE, below
   1 long USO and short XLE, and a NaN ratio or a ratio of exactly 1 holds
   nothing. Each day earns yesterday's positions times each leg's return,
   summed over the legs that have one and divided by 2, with NaN set to 0.
   The figures are `chan.tu_momentum.figures`, annualised over 252 days with
   the standard deviation dividing by n, no risk-free rate and no cost.

The two calendars share 1,498 of the ETF file's 1,500 days. The ETF file
holds 2006-07-03 and 2006-11-24, which the strip lacks. The strip's first
contract is CL-2007F, whose front window opens on 2006-10-20, so the window's
first 123 days carry no ratio and hold nothing. Of the 1,375 days that carry
one, 1,129 are in contango, 244 in backwardation, and 2 carry a ratio of
exactly 1.

Every result here is **exploratory**. Reproducing Chan's figures spends his
2006 to 2012 sample on a rule he chose.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The average annual return, script | 0.1592 | script line 63 |
| 2 | The Sharpe ratio, script | 1.05 | script line 63 |
| 3 | The APR, script | 0.1591 | script line 64 |
| 4 | The maximum drawdown | −0.192321 | script line 65 |
| 5 | The longest drawdown | 487 days | script line 65 |
| 6 | The APR, book | "a very respectable 16 percent" | location 2734 |
| 7 | The Sharpe ratio, book | "about 1" | location 2734 |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · smartmean(ret)` over the 1,498 days | 0.159231 | `TestTheSpecification::test_the_average_annual_return` |
| 2 | `√252 · smartmean(ret) / smartstd(ret)` | 1.046596 | `TestTheSpecification::test_the_sharpe_ratio` |
| 3 | `prod(1 + ret)^(252 / 1498) − 1` | 0.159102 | `TestTheSpecification::test_the_apr` |
| 4 | `calculateMaxDD(cumprod(1 + ret) − 1)`, the deepest drawdown | −0.192321 | `TestTheSpecification::test_the_maximum_drawdown` |
| 5 | The same, the longest run of days below a high | 487 | `TestTheSpecification::test_the_longest_drawdown` |
| 6 | Row 3, in percent | 15.910241 | `TestTheSpecification::test_the_apr`, and `::test_both_reproduce_the_book_s_figures` for the rounding |
| 7 | Row 2 | 1.046596 | `TestTheSpecification::test_the_sharpe_ratio`, and `::test_both_reproduce_the_book_s_figures` for the rounding |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.0000 | reproduced | 0.159231 rounds to the script's 0.1592. |
| 2 | −0.00 | reproduced | 1.046596 rounds to the script's 1.05. |
| 3 | +0.0000 | reproduced | 0.159102 rounds to the script's 0.1591. |
| 4 | +0.000000 | reproduced | Exact at the six decimals the script prints. |
| 5 | 0 days | reproduced | Exact. |
| 6 | −0 percent | reproduced | 15.91 percent rounds to the book's 16. |
| 7 | +0 | reproduced | 1.046596 rounds to the book's 1. |

### What the entry concludes

Two things.

1. **The script's rule reproduces on Chan's own files.** Every figure its
   comment prints lands at the decimals printed, and the book's two land at
   the precision Chan printed them.
2. **The book's text and the script describe one run.** The text gives no
   rule for deciding contango beyond location 2718's definition, so the rule
   here is the script's, and its APR and Sharpe ratio are the text's
   16 percent and "about 1".

### What this entry cannot say

Four things.

**What a holder of XLE earned.** `inputData_ETF.mat` subtracts each dividend
in dollars from every earlier close, which
[issue 299](https://github.com/l3a0/quantitative-trading/issues/299) found.
That leaves the replication untouched, because Chan's script read the same
bytes. It does change what a holder of XLE earned, and no second XLE
series over this window is committed to measure by how much.

**What the trade earned while it held a view.** The first 123 days carry no
ratio, because the strip's first contract opens its front window on
2006-10-20. The figures count those days as earning 0, as the script does,
and this entry measures nothing over the shorter span.

**Which standard deviation the Sharpe ratio divides by.** The run divides by
n, as `chan.matlab_helpers.smartstd_book_two` does. Dividing by n − 1 gives
1.046247, which also rounds to the script's 1.05, so this script's printout
cannot tell the two apart.

**Whether the trade works out of sample.** The rule and the window are
Chan's, and the sample is the one he reported on. A registered test would fix
the rule first and run it on data after 2012.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.
