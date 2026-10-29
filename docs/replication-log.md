# Replication log

A replication is finished when it reaches a verdict. Until then the repo holds
a reproduced experiment, which is a number sitting next to another number with
nobody saying what the pair means.

This file is where the verdicts live. One entry per replication, apart from
the six exceptions the paragraphs below name, and one row per published result, carrying the five parts
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
22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 40, 41, 42, 43, 45, 47, 48, 49 and 51 carry their own, three, eleven, twelve, five,
six, one, three, eight, six, two, eight, seven, twelve, six, two, five, three,
three, three, seven, six, seven, three, four, five, seven, nine, five, twelve, seven, eight, four, eight, eight, four, five, six, one, eleven, twelve, nine, fourteen, seven, eleven and ten, and they are listed in those entries rather than here, because the list is about an entry's rows and not
about the file.

Entries 5, 44, 46, 48, 50 and 52 are the six entries that are not replications.
Chan states the claim Entries 5, 44 and 50 test without printing a number, so each
carries a finding rather than a verdict, and its tables drop the columns that
would hold a published figure, a gap and a verdict. Entry 46 reruns Example
7.2, which Entry 12 reproduces, on a calendar and prices Chan never used, so
no figure he printed applies to it and its tables drop the same columns.
Entry 48 tests location 4709's rule at two ceilings Chan prints no figure
for, so its tables drop the published-figure and gap columns, and each of its
verdict cells says it is not a replication. Entry 52 reads a series another
project built and publishes and sets the two figures it quotes beside that
series, so it chases neither, and its tables drop the gap and verdict
columns.
Entries 6 and 15 come from the same
sentence of the book as Entry 5 and are replications, because the claim each
tests is about a series Chan names or a class whose members are tested
directly.

Every result in Entries 1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51 and 52 is **exploratory** in the design
doc's sense. Reproducing a published figure spends the sample on a hypothesis
someone else already chose, and testing a claim the source states does the same, so an
entry can say whether the number reproduces or the claim holds on its vintage
and nothing about whether the trade works today. Entry 7's rows 35 to 49,
Entry 45's row 1, Entry 49's row 1 and Entry 51's rows 1 and 3 to 6 are the
exceptions, and they are **registered**. Entry 7's claim, test and verdict wording were written before
any return was computed. Entry 45's plan and criterion were written before any
number was computed, and the wording of its ruin outcome after the leverage
path and the two ruined months had been seen, which that entry states. Entry
49 runs the same plan on IVV's S&P 500 from 2008, and its rule for a formation
with no positive low-group beta was written after the first such formation
had been seen, which that entry states too. Entry 51 trades Example 2.5's
rule on USD/CAD's closes after Chan's sample at a lookback fixed from it, and
every prediction it records was written before the run computed anything on
any of those closes.
Its row 2 did not run and carries neither label. Entries 2 and 9 spend no
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
  - [How far H moves by chance and by its start day](#how-far-h-moves-by-chance-and-by-its-start-day)
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
- [Entry 40: the opening gap strategy on STOXX Europe 50 futures, Chan's *Algorithmic Trading*](#entry-40-the-opening-gap-strategy-on-stoxx-europe-50-futures-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-37)
  - [What this repo computed](#what-this-repo-computed-39)
  - [The verdicts](#the-verdicts-38)
  - [What the entry concludes](#what-the-entry-concludes-39)
  - [What this entry cannot say](#what-this-entry-cannot-say-37)
- [Entry 41: VX against ES on VX's roll return, Chan's *Algorithmic Trading*](#entry-41-vx-against-es-on-vxs-roll-return-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-38)
  - [What this repo computed](#what-this-repo-computed-40)
  - [The verdicts](#the-verdicts-39)
  - [What the entry concludes](#what-the-entry-concludes-40)
  - [What this entry cannot say](#what-this-entry-cannot-say-38)
- [Entry 42: whether Example 7.4's own factor returns have momentum, Chan's *Quantitative Trading*](#entry-42-whether-example-74s-own-factor-returns-have-momentum-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-2)
  - [What this repo computed](#what-this-repo-computed-41)
  - [The verdicts](#the-verdicts-40)
  - [What the entry concludes](#what-the-entry-concludes-41)
  - [What this entry cannot say](#what-this-entry-cannot-say-39)
- [Entry 43: Monte Carlo leverage, historical optimization and CPPI, Chan's *Algorithmic Trading*](#entry-43-monte-carlo-leverage-historical-optimization-and-cppi-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-39)
  - [What this repo computed](#what-this-repo-computed-42)
  - [The verdicts](#the-verdicts-41)
  - [Why the simulated rows are judged against an ensemble](#why-the-simulated-rows-are-judged-against-an-ensemble)
  - [What the book's 18.4 most likely came from](#what-the-books-184-most-likely-came-from)
  - [What the entry concludes](#what-the-entry-concludes-42)
  - [What this entry cannot say](#what-this-entry-cannot-say-40)
- [Entry 44: the Khandani-Lo reversal on the S&P 600, Chan's *Quantitative Trading*](#entry-44-the-khandani-lo-reversal-on-the-sp-600-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-3)
  - [What this repo computed](#what-this-repo-computed-43)
  - [What each row says](#what-each-row-says-1)
  - [The two flagged days](#the-two-flagged-days)
  - [The stocks with a missing price](#the-stocks-with-a-missing-price)
  - [What the size reading says](#what-the-size-reading-says)
  - [What the entry concludes](#what-the-entry-concludes-43)
  - [What this entry cannot say](#what-this-entry-cannot-say-41)
- [Entry 45: a levered low-beta portfolio against an unlevered high-beta one, Chan's *Quantitative Trading*](#entry-45-a-levered-low-beta-portfolio-against-an-unlevered-high-beta-one-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-4)
  - [What this repo computed](#what-this-repo-computed-44)
  - [The verdicts](#the-verdicts-42)
  - [What the entry concludes](#what-the-entry-concludes-44)
  - [What this entry cannot say](#what-this-entry-cannot-say-42)
- [Entry 46: post-earnings drift on EDGAR's calendar and the archive's prices, Chan's *Algorithmic Trading*](#entry-46-post-earnings-drift-on-edgars-calendar-and-the-archives-prices-chans-algorithmic-trading)
  - [The registration](#the-registration)
  - [What this repo computed](#what-this-repo-computed-45)
  - [The attribution](#the-attribution)
  - [Checks run after the figures were seen](#checks-run-after-the-figures-were-seen)
  - [What the entry concludes](#what-the-entry-concludes-45)
  - [What this entry cannot say](#what-this-entry-cannot-say-43)
- [Entry 47: the VIX filter on buy on gap and the STOXX Europe 50 gap rule, Chan's *Algorithmic Trading*](#entry-47-the-vix-filter-on-buy-on-gap-and-the-stoxx-europe-50-gap-rule-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-40)
  - [What this repo computed](#what-this-repo-computed-46)
  - [The verdicts](#the-verdicts-43)
  - [What the entry concludes](#what-the-entry-concludes-46)
  - [What this entry cannot say](#what-this-entry-cannot-say-44)
- [Entry 48: the low-beta rule at leverage a broker would lend, Chan's *Quantitative Trading*](#entry-48-the-low-beta-rule-at-leverage-a-broker-would-lend-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-5)
  - [What this repo computed](#what-this-repo-computed-47)
  - [The verdicts](#the-verdicts-44)
  - [What the entry concludes](#what-the-entry-concludes-47)
  - [What this entry cannot say](#what-this-entry-cannot-say-45)
- [Entry 49: the levered low-beta rule after the book, on IVV's S&P 500](#entry-49-the-levered-low-beta-rule-after-the-book-on-ivvs-sp-500)
  - [What the book stated](#what-the-book-stated-6)
  - [What this repo computed](#what-this-repo-computed-48)
  - [The verdicts](#the-verdicts-45)
  - [The skipped formations](#the-skipped-formations)
  - [What the entry concludes](#what-the-entry-concludes-48)
  - [What this entry cannot say](#what-this-entry-cannot-say-46)
- [Entry 50: the Khandani-Lo reversal on the S&P 400, Chan's *Quantitative Trading*](#entry-50-the-khandani-lo-reversal-on-the-sp-400-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-7)
  - [What this repo computed](#what-this-repo-computed-49)
  - [What each row says](#what-each-row-says-2)
  - [The flagged days](#the-flagged-days)
  - [The holdings the run leaves out](#the-holdings-the-run-leaves-out)
  - [The control](#the-control)
  - [What the entry concludes](#what-the-entry-concludes-49)
  - [What this entry cannot say](#what-this-entry-cannot-say-47)
- [Entry 51: Example 2.5's linear rule on USD/CAD after 2012, Chan's *Algorithmic Trading*](#entry-51-example-25s-linear-rule-on-usdcad-after-2012-chans-algorithmic-trading)
  - [What the book stated](#what-the-book-stated-8)
  - [What this repo computed](#what-this-repo-computed-50)
  - [The verdicts](#the-verdicts-46)
  - [What the entry concludes](#what-the-entry-concludes-50)
  - [What this entry cannot say](#what-this-entry-cannot-say-48)
- [Entry 52: Example 7.7 against Open Source Asset Pricing's `MomSeasonShort`](#entry-52-example-77-against-open-source-asset-pricings-momseasonshort)
  - [What the sources stated](#what-the-sources-stated)
  - [What this repo computed](#what-this-repo-computed-51)
  - [What each construction difference can explain](#what-each-construction-difference-can-explain)
  - [What the entry concludes](#what-the-entry-concludes-51)
  - [What this entry cannot say](#what-this-entry-cannot-say-49)

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
   Entry 38,
   [tests/test_xle_uso_roll_return.py](../tests/test_xle_uso_roll_return.py)
   holds Entry 39,
   [tests/test_opening_gap.py](../tests/test_opening_gap.py) holds Entry 40,
   [tests/test_vx_es_roll_return.py](../tests/test_vx_es_roll_return.py)
   holds Entry 41,
   [tests/test_pca_factor_momentum.py](../tests/test_pca_factor_momentum.py)
   holds Entry 42,
   [tests/test_monte_carlo_leverage.py](../tests/test_monte_carlo_leverage.py)
   holds Entry 43,
   [tests/test_khandani_lo_small_caps.py](../tests/test_khandani_lo_small_caps.py)
   holds Entry 44,
   [tests/test_low_beta_leverage.py](../tests/test_low_beta_leverage.py)
   holds Entry 45, [tests/test_pead_rerun.py](../tests/test_pead_rerun.py)
   holds Entry 46,
   [tests/test_vix_filter.py](../tests/test_vix_filter.py) holds Entry 47,
   [tests/test_low_beta_capped.py](../tests/test_low_beta_capped.py) holds
   Entry 48,
   [tests/test_low_beta_holdout.py](../tests/test_low_beta_holdout.py) holds
   Entry 49,
   [tests/test_khandani_lo_mid_caps.py](../tests/test_khandani_lo_mid_caps.py)
   holds Entry 50, and
   [tests/test_usdcad_holdout.py](../tests/test_usdcad_holdout.py) holds
   Entry 51.
   [tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) also
   holds Entry 52, whose row 5 runs only where the owner's data archive is. The archive pins of Entries 46, 49 and 50 run only where
   the owner's
   data archive is and `QT_ARCHIVE_RUN=1` asks for them.
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
Entries 5, 44, 46 and 50 is in that position too, so those entries drop the
verdict column rather than filling it. Entry 52's rows 1 and 2 quote published
figures, but set them beside a series another project built rather than one
this repository computes, so they chase neither, and that entry drops the gap
and verdict columns for the same reason. So are Entry 6's rows 2 to 9, Entry 7's rows 15 to 18, 23 to 29 and 30 to 50,
Entry 8's row 3, Entry 9's rows 3 to 5, Entry 10's rows 6 to 13, Entry 11's
rows 2 and 6 to 10, Entry 12's rows 10 and 11, Entry 13's rows 11 to 16,
Entry 14's rows 3 to 9, Entry 15's rows 3 to 14, Entry 16's rows 6 to 11,
Entry 17's rows 10 and 11, Entry 18's rows 8 to 12, Entry 19's rows 9 to 11,
Entry 20's rows 11 to 13, Entry 21's rows 9 to 11, Entry 22's rows 8 to 10,
Entry 23's rows 15 to 20, Entry 24's rows 10 to 17, Entry 25's rows 5 to 7,
Entry 26's rows 4 to 7, Entry 27's rows 15 to 18, Entry 28's rows 5 to 11,
Entry 29's rows 7 to 15, Entry 30's rows 6 to 8, Entry 31's rows 3 to 14,
Entry 32's rows 5 to 7, Entry 33's rows 11 to 15, Entry 34's rows 10 to 12,
Entry 35's rows 4 to 9, Entry 36's rows 7 to 14, Entry 37's rows 6 to 8,
Entry 38's rows 8 to 11, Entry 40's rows 6 to 9 and 12 to 16, Entry 41's row 11,
Entry 42's rows 6 to 16, Entry 43's rows 13 to 17,
Entry 45's rows 2 to 9, Entry 47's rows 13 to 18, Entry 48's rows 1 to 7,
Entry 49's rows 2 to 11, and Entry 51's rows 2 to 10.

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

Entry 44's claim does not take it either. Chan's explanation is about where
Khandani and Lo's returns came from, on their own universe, which this repo
does not hold. It also names microcaps, and the S&P 600 file holds prices and
volumes but no market values, so nothing here measures how many of its members
were microcaps. The run can say which way the gap between two of Chan's files
points, and not whether his sentence about their returns is true. Its reading
was declared on
[issue 249](https://github.com/l3a0/quantitative-trading/issues/249) before
any S&P 600 figure was computed, and it adds no verdict. Entry 50's claim is
the same sentence read on the S&P 400 beside both of Chan's files, and it does
not take the route for the same reasons. Its reading was declared on
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303) before any
S&P 400 figure was computed, and it adds no verdict either.

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

Entry 40's row 5 takes it too. Location 2965 says the rule that buys FSTX
"when the instrument gaps up" and shorts it "when it gaps down" generates an
APR of 13 percent and a Sharpe ratio of 1.4, a definite claim about one
strategy it names. Its criterion, the momentum reading's APR and Sharpe ratio
each rounding to the book's figure through `matches`, was written on
[issue 358](https://github.com/l3a0/quantitative-trading/issues/358) after a
scratch run had computed both readings, though before the build, the order
Entry 13's row 10 allows when it is stated. Line 23 of `gapFutures_FSTX.m`
can take only two signs, and the rounding rule is the one every entry uses,
so there was no reading or threshold left to choose. The momentum reading misses the APR by 25
percentage points in the wrong direction, so the verdict does not rest on
where a line sits.

Entry 42's rows 1 to 5 take it too, one per factor, as Entry 14's rows 1 and
2 do. Location 4014's claim is about factor returns, and location 4051 says
Example 7.4 rests on it, so each of the five statistical factors that example
fits is a definite case of it. Their criterion, each factor's statistic above
0 and above the median stock's, was written on
[issue 286](https://github.com/l3a0/quantitative-trading/issues/286) on
2026-10-10. The owner ruled the same day that each factor carries its own
verdict, and both came before any factor return was computed.

Entry 43's rows 4, 7, 11 and 12 take it too, each a definite claim Chapter 8
makes about the strategy and the scheme it names. The simulated optimum is
"strikingly close" to the Kelly, the historical optimum is "again the same"
as it, CPPI's growth is "very similar" to the full account's at f·D, and
CPPI's drawdown stays under 0.5 "by design". Their criteria were written on
[issue 360](https://github.com/l3a0/quantitative-trading/issues/360) before
any draw on its declared seeds, though after scratch runs on other seeds had
seen results, the order Entry 13's row 10 allows when it is stated. Row 7's
two figures are deterministic, and the issue had measured both before writing
its 1 percent line, so that criterion was written with the margin in view. They
differ by 0.52 percent, half the line, so the verdict does not rest on where
the line sits.

Entry 45's row 1 takes it too. Location 4709 names a class, "a highly
leveraged portfolio of low-beta stocks" against "an unleveraged portfolio of
high-beta stocks", and a fifth of the S&P 500 sorted on beta is a member of
that class, which is the Entry 15 case rather than the Entry 5 one. Its
criterion, the Newey-West t of the monthly log-growth gap against 1.645, was
written on
[issue 275](https://github.com/l3a0/quantitative-trading/issues/275) before
any beta or return was computed, and the row carries a verdict by that plan's
default, which the owner can reverse on
[PR #527](https://github.com/l3a0/quantitative-trading/pull/527). The criterion left
undefined a levered month losing more than the capital. The owner's amendment
of 2026-10-11 reads that case as the claim contradicted, and it was written
after the first such month was visible, which Entry 45 states beside its
label.

Entry 47's row 5 takes it too. Location 2965 describes the rule that buys FSTX
when it gaps up and shorts it when it gaps down, and location 3509 prints that
rule's return and Sharpe ratio on the days after VIX closed above 35, a
definite claim about one strategy it names.
[Issue 359](https://github.com/l3a0/quantitative-trading/issues/359) states no
criterion in words, so the criterion is the rounding rule every entry uses, the
momentum reading's return and Sharpe ratio each rounding to the book's figure
through `matches`. It was applied after a scratch run had computed both signs
under six alignments, though before the build, the order Entry 13's row 10
allows when it is stated. Line 23 of `gapFutures_FSTX.m` can take only two
signs, and the rounding rule is the one every entry uses, so there was no
reading or threshold left to choose. The momentum reading misses the return by
5.2 percentage points and the Sharpe ratio by 0.32, so the verdict does not
rest on where a line sits.

Entry 49's row 1 takes it for Entry 45's reason, on IVV's S&P 500 from 2008.
It inherits Entry 45's criterion and amendment, and the changes the panel forces were
written on [issue 526](https://github.com/l3a0/quantitative-trading/issues/526)
before any number on that panel was computed. The plan refuses a formation
whose low group's mean beta is not positive and gave that case no verdict.
The owner's second amendment of 2026-10-11 skips such a formation, and it
was written after the first one, 2026-04-30, was visible, which Entry 49
states beside its label.

Entry 51's row 1 takes it for Entry 22's row 7's reason, on USD/CAD's closes
after Chan's sample. Location 1225 says the P&L of the strategy it names
"manages to be positive", and the criterion, the sum of the daily P&L over
the traded days from 2012-03-29 above 0 at a lookback frozen at 115, was
written on [issue 607](https://github.com/l3a0/quantitative-trading/issues/607)
before the run computed anything on any of those closes. So were the four
predictions beside it, which decide nothing, and the mapping from the
criterion to a verdict.

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

Entry 48's seven rows carry no verdict for a fourth reason. Rows 1 and 2 test
the claim of location 4709 that Entry 45's row 1 tests, with the leverage
capped at 2 and at 5. Their outcomes, the control across them and the wording
of each were written on
[issue 516](https://github.com/l3a0/quantitative-trading/issues/516) before
any capped number was computed. The ceilings were chosen after Entry 45's
calendar, its leverage path, the ruin, eight months of both groups' returns
and its side figures had been seen. Those side figures are both Sharpe
ratios, the growths, the realised betas and the full-sample Kelly leverage of
9.9884. So a result here confirms nothing whichever way it lands. No row
carries a published figure either, so every cell reads "none, not a
replication, exploratory", and the reason column of rows 1 and 2 names the
outcome the plan's rules reach.

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
file's formatting, resolves every anchor its Contents carries, and checks that
every test it names exists. None of these checks reads a figure, so a re-pin
that moves a number leaves this entry stale and the suite green. Whether that
guard gets built is the decision on
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

**What checks row 12's 20.47 percent.** Nothing does. Checking it needs an
S&P 500 index vintage, which is a different symbol and a different deliverable,
so it is cut and pinned in the design doc's register rather than left as
something a later reader might think was forgotten.

**What checks the 4 percent risk-free rate.** The same applies to it. A
Treasury-bill series would move two inputs at once and leave every gap above
unattributable to either.

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
| 5 | The first fits whose residuals pass are further from rejecting than the one-lag fits, so the check strengthens the finding rather than weakening it. On GLD/GDX the band was the half of the check that decided. Here every autocorrelation is inside the band from 9 lags for TLT on IEF and from 10 for IEF on TLT, and the Breusch-Godfrey half is what holds the passing count at 31. `TestTheResidualCheck::test_the_breusch_godfrey_half_is_what_holds_the_count_at_31` pins that. |
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

Three things.

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

One row is a replication and eight are not. Row 1 is the claim, and it takes
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
| 2 | none, not a replication | The headline statistic. Lag 1 was fixed before any number was seen, as the rule [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) set for both candidates. Every count from 0 to the ceiling of 32 also rejects at 5%, the closest being 6 at −2.8739, so the lag rule does not decide the verdict here. `TestTheCrossRateStatistic::test_every_lag_up_to_the_ceiling_rejects_at_five_percent` pins that. |
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

Three things.

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
Row 50 shipped under no issue of its own. The owner asked for it while editing
the equity seasonals post, whose edits
[issue 632](https://github.com/l3a0/quantitative-trading/issues/632) tracks.

Fifty rows, all derivable from
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py).

**Every figure the committed files reach reproduces, in every printout.** Chan
prints these two examples in four ways: the first edition's MATLAB, and the
revised edition's MATLAB, Python and R. Seventeen printed figures need only
data this repo holds, and all seventeen land on the digits their source prints. None
of them lands from the strategy's description alone. Each needs the rules its
own script applies, and the issue records the figure each rule gives when it is
changed.

Chan publishes Example 7.7 as already dead and reports Example 7.6 failing in
two Januaries before working in the third, so reproducing them checks
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
all downloaded 2026-10-05, and the calendar is the same SPY vintage. Row 50
reads the same files.

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
members at each year-end, rows 41 to 49 are Example 7.7 from January 2009
to September 2026 on IVV's members each month, and row 50 is row 35's
Januaries with every missing member left out. Each row names the
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

Rows 5, 6 and 21 rest on a different inference: the R's figures match the
first edition's, so its rules are assumed, because its Example 7.6 is printed
only in the book. The revised edition's half of rows 1, 2 and 19 no longer
rests on that inference. The repost's `example7_6.m` at `7430b84` rounds a
tenth with `round`, takes a full tenth at each end, and reads one shared row
for the last day of December and of January, which are `MATLAB_JANUARY`'s
rules, and its closing comment prints the same three returns.

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

Row 50 is **exploratory**. It leaves every missing member out of row 35's
Januaries, the way rows 41 to 49 do for Example 7.7, but
[issue 329](https://github.com/l3a0/quantitative-trading/issues/329) wrote no
rule for it before the run.

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
| 50 | 7.6, mean January return before costs, row 35's Januaries with every missing member left out | nothing | n/a |

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
| 3 | `PYTHON_JANUARY`: year-end closes forward-filled before ranking, as pandas before 3.0 did, and a winners' slice of `topN - 2` that leaves out the best and the weakest of the best tenth, 58 long and 56 short of 579 ranked | −0.023853 | 0.000000 | `TestJanuaryPython::test_the_three_januaries_reproduce` |
| 4 | as row 3, 59 long and 57 short of 593 ranked | −0.003641 | 0.000000 | as row 3 |
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
| 50 | row 35's year-ends with every missing member left out, the tenth taken of the ranked covered members alone, from 43 long and 43 short of 433 ranked to 60 long and 60 short of 598 ranked. Described rather than tested, because [issue 329](https://github.com/l3a0/quantitative-trading/issues/329) wrote no rule for it | −0.0083, one-sided p 0.743 | none | `TestThePointInTimePins::test_leaving_the_missing_members_out_lands_between_the_two` |

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
| 7 | reproduced | The return is a sum over every position held that month, never divided by their number, so −0.9167 is in units of summed positions rather than a fraction of capital. Keeping each stock on its own close instead gives −1.0822, or −0.0113 a year once each month is divided by its positions. Dividing each month by its positions gives −0.0105 a year, a figure this repo derived and Chan did not print. The 12 empty months add nothing to the sum, so averaging over the 83 that hold positions divides the same sum by 83 instead of 95. Multiplying the old mean by 95/83 cancels its 95, carrying −0.9167 to −1.0492 and −0.0105 to −0.0120. |
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
| 50 | none, exploratory | Reported beside row 35 with no verdict, because [issue 329](https://github.com/l3a0/quantitative-trading/issues/329) wrote no rule for it before the run. Leaving every missing member out also ranks each year on a different set of stocks than the strategy would have traded, a bias row 49 measured for Example 7.7 and nobody has measured here. |

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
   5. a winners' slice that leaves out the best stock and the weakest of the best tenth,
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
   decide whether the January effect still worked after 2008.** This is the log's
   first registered result. Rows 35 to 40 bound every January, because every
   year-end has members with no checked price that could change a tenth. The
   low series averages −0.1047 a January with a one-sided p of 1.000, and the
   high series 0.0879 with a p of 0.001. Row 50 leaves out every member with
   no checked price and averages −0.0083, between the two, described rather
   than tested. A
   purchase of the threatening members' prices is what could decide it.
7. **On the S&P 500 as IVV held it each month, Example 7.7 earns no return
   detectable above about 4.2% a year after the book.** This is registered.
   Row 41 averages −0.0001 a month before costs over the 213 months from
   January 2009 to September 2026, with a one-sided p of 0.539. The revised
   Python's rules give the same months, and the means on both bracketing
   masks are negative too, with no verdict.

### What this entry cannot say

Four things.

**Whether Example 7.6's January effect still worked after 2008.** Rows 35 to 40
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
which `uv run python -m chan.equity_seasonals_figures` redraws. So do the
whiteboard sketches that print figures, which `uv run python -m
chan.equity_seasonals_whiteboard` redraws, fifteen of them on a machine with
the archive. Those are the opening's years and verdicts sketches, four of the
seven rule sketches, the split sketch, the five-year check's three, the January
ranges sketch, the two under "What 18 Januaries can detect", eight of the ten
sketches on whether Heston and Sadka's effect still worked after 2008, three of
them on where its 4.2 percent comes from and two on what a broader series
shows, and three of the four under "Further work". The third on the broader
series, "Before 2002 and after", draws only Entry 52's figures, as the
sketches on whether the effect existed before 2002 do.
`TestTheRuleSketchesFigures` in
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) derives the
rule sketches' figures from Chan's files, `TestTheYearsInsideTheSplit` the split
sketch's, and `TestTheFiveYearSketches` the five-year check's. The verdicts
sketch draws rows 35, 41 and 44's figures and refuses to draw unless rows 37 and
43's tests give their registered verdicts, and `PINNED` in
[tests/test_equity_seasonals_whiteboard.py](../tests/test_equity_seasonals_whiteboard.py)
moves with a re-pin of either. The January ranges sketch draws the registered
January run's eighteen Januaries and, beside each, row 50's January with every
missing member left out. `PINNED_RANGES` there moves with a re-pin of either.
The two under "What 18 Januaries can detect" draw the registered January run's
count and its two versions' spreads, from which row 38's X follows, so
`PINNED_POWER` there moves with a re-pin of it.
Three of the four under "Further work" draw rows 35 and 38's figures through
`PINNED` and `PINNED_POWER`, row 41's months through `PINNED_IVV`, and the 741
member-years the January run could not check that could change a traded
tenth, so each moves with a re-pin of
those.
The checked, leavers and running-sum sketches draw row 41's months and
coverage and row 49's departures from the IVV run, the 4.2 percent's three
draw the critical value and δ from row 41's month count, and the broader
series' scatter and running sums draw row 41's months against Entry 52's, so
`PINNED_IVV` there moves with a re-pin of any of them. `PINNED_SHIFT` there
copies the critical value, δ and the normal curve's 80th percentile that
`test_how_the_4_2_percent_is_derived` in
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) pins, and
moves with a re-pin of it.

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
   the S&P 400 and S&P 600 as an exercise, which would test it. Entry 44
   runs the S&P 600 half and Entry 50 the S&P 400 half.

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
it, and Chan leaves that as an exercise.
[Issue 249](https://github.com/l3a0/quantitative-trading/issues/249) ran it on
the S&P 600 file under `ijr_20080114/`, and Entry 44 carries the finding, with
no published figure to check, like Entry 5. Before costs the rule earns more
on the S&P 600 than on the S&P 500 at both prices, the closes this entry
reports and the opens Entry 10 reports, which is the direction Chan's
explanation predicts. Nothing in Entry 44 measures how many S&P 600 members
were microcaps, and the S&P 600 is not Khandani and Lo's universe, so even
that finding leaves this question open.

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

Three things.

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
[issue 249](https://github.com/l3a0/quantitative-trading/issues/249) ran it on
the S&P 600 file, which Entry 44 reports. That run charges small caps the same
5 basis points as large caps, so its after-cost figures at the open flatter
them, and it is one year of survivors.

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
the gasoline count agrees with the book on every year the file can read.**
Chan says commodity seasonal trades still pay where much of the equity
seasonality has weakened or disappeared, and gives two. Gasoline buys the May
contract at the close of April 13 and sells at the close of April 25. Natural
gas buys the June contract at the close of February 25 and sells on April 15,
at a time Chan does not name, which the run takes as the close.

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
   natural gas. Lesson 2's second fill also reads New York Harbor's contract 2,
   `eia_eer-epmr-pe2-y35ny-dpg`, and Lesson 5's handover check and holiday
   count read natural gas's contract 1, `eia_rngc1`. [data/README.md](../data/README.md) says what each holds. Each
   file numbers contracts by expiry, so the run maps a date to the file that
   holds the May or June contract. The expiry rule behind that map gives the
   last trading day the Massive futures API recorded for all 40 March to June
   contracts it holds from 2017, where its records begin, to 2026. Those 40 dates were read from the API on 2026-10-26, after a first
   read of 16 on 2026-10-03 that agreed, and are pinned as a measurement,
   because nothing in this repo can read them again. Before mid-1997 contracts stopped trading
   five or six days before delivery rather than three, which the files'
   handovers show, and the rule follows them. That moves the 1996 and 1997
   entries to contract 3 and changes neither year's sign.
2. **Profitable** means the exit settlement strictly above the entry, on one
   contract, with no costs.
3. **A missing row stays missing.** A year whose trade date has no row in its
   file counts neither way, rather than moving to another day.

Every result here is **exploratory**. Chan chose both trades after looking at
years before his book, which the run also reads, so on those years the entry
says whether his counts reproduce. Nobody wrote down a test for the years after
the book before the run computed them, so the entry says nothing about whether
either trade pays today.

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
| 7 | none | none, not a replication | 1994 is profitable too, so counting from the first year the files hold a whole trade makes both runs one longer. With runs ending in 2007 and 2008, only a count from 1995 matches, the year both gasoline counts start from: the sidebar names it, and the main text's 21 years to 2015 begin there. Counted from 1994, runs of 13 and 14 end in 2006 and 2007 instead. |
| 8 | none | none, not a replication | The older contract's file has no row on 2006's entry day, so the side row cannot say whether the switch to RBOB decides 2006. |
| 9 | none | none, not a replication | In 10 years the entry falls on the March contract's last trading day, so the file read depends on contract 1 keeping an expiring contract on its last day. The files show that convention in 2014 and 2019. Reading the contract-3 file instead turns no year from a profit to a loss or from a loss to a profit, so the convention cannot move a verdict. |
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
3. **In this exploratory record, both trades win a smaller share of years
   after the years Chan counted.** Natural gas wins 15 of 15 through 2008 and 7
   of 15 after, which agrees with his remark at location 4632. Gasoline wins 3
   of 8 from 2016 to 2023. Each trade's earlier years include the years Chan
   chose its rule on, so the drop can overstate how much it weakened. No costs
   are charged on either side of the split.

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

A fill of the three missing gasoline prices was tried on 2026-10-25 and cannot
decide any of the three years, a null result
`chan.commodity_seasonals.gap_fills` keeps and
[tests/test_commodity_seasonals.py](../tests/test_commodity_seasonals.py)
pins. EIA's contract-2 file, which holds June while May is contract 1, has a
row on all three days, so the run filled each gap two ways.

1. A straight line between the contract-1 rows on either side.
2. May's price on the last day before the gap, counting only days both files hold, moved by June's change since that day.

Each fill's typical miss was measured as a root mean square error on hidden
April days from 1994 to 2005 in the gap's own pattern of trading days. June's
move misses by 0.65 to 0.89 cents a gallon, and the straight line by 1.8 to
2.0. Both fills guess a profit every year, but every move lies inside one
typical miss.

Fill 2's misses also average 0.20 to 0.26 cents above zero, so it guesses May
low, by 2.7 to 3.2 standard errors that understate the truth, because test days
close together read some of the same prices.
Corrected by that average and set against the spread around it, the three
years' chances of a profit are 57%, 83% and 90%, none reaching 95%. If the
misses are normal and independent, all three years were profits with a chance
of 42%, which is what Chan's 19 of 21 needs. Before the correction the figure
was 41%.

The post also carries thirty whiteboard sketches, twenty-eight that draw
this entry's run and two schematic sketches, and
`uv run python -m chan.commodity_seasonals_whiteboard` redraws all
thirty.

1. Each trade's entry and exit on one calendar, with Chan's count for it.
2. Both trades' years won, split where the book's years end: 15 of 15 then 7 of
   15 for natural gas, and 16 of 18 then 3 of 8 for gasoline.
3. Natural gas's 2002 trade on every trading day the files hold a price. Its
   22-point fall from its 48% peak is the drawdown before 2009, inside a year
   that ended 40% up.
4. The natural gas streaks of 13 and 14, counted from 1995 and from 1994,
   against the 2009 loss and the first edition's release.
5. Gasoline's two claims, the sidebar's profit every year since 1995 ending
   in 2008 before the first loss, and the main text's 19 of 21 ending in 2015
   past both losses.
6. The range of 16 to 19 profitable gasoline years the three missing rows
   leave, with Chan's 19 at its top.
7. Chan's years and the files' as two bars, the missing years filling the
   gap between the files' 16 profits and Chan's 19.
8. A straight-line guess for 1997's missing entry, with a band of one typical
   miss either side that the exit price splits.
9. Fill 2 for 1997: June's rise across the gap carried onto May, with a band
   of fill 2's typical miss either side that the exit price splits.
10. Each missing year's move with fill 2's guess corrected by its average
   miss, against the spread of its misses either side.
11. The April trading days narrowing to 1997's 80 test days.
12. Fill 2's misses on the 80 test days of 1997's pattern, with their
   average, spread and typical miss.
13. Each April's average miss, eight of twelve leaning low.
14. Why a miss subtracts at an entry and adds at an exit, from 1997's missing
   entry and 1998's missing exit.
15. A schematic raised start, one trade's mean in the book's years drawn
   above its real edge, so the fall measured from it is longer than the fall
   the trade took, with no figures from the run.
16. Each period's Sharpe ratio with 1.96 standard errors either side.
17. Student's t's 95% multiplier for few results against the normal curve's.
18. Natural gas's ±12% half-width built from its spread, count and multiplier.
19. Each period's mean and 95% range, with each trade's earlier mean carried
   down past its later range.
20. Every pairing of an earlier natural gas year with a later one, 177 of 225
   won by the earlier year.
21. The pair counts luck alone gives, counted exactly, with natural gas's 177
   in the 0.7% of splits that land that far out.
22. The four chances against the 5% line.
23. Natural gas's mean after 2008 with and without 2022, against all 30
   years ranked.
24. Which numbered file holds the June contract on the entry and exit days of
   2008 and 2006.
25. The files handing over the day after March 1996's last trading day.
26. Which years each check of the expiry rule reaches.
27. 2018's entry on March's own last trading day.
28. A holiday row in the files, at Christmas 2018, beside none in 2016.
29. A schematic cliff beside a plateau, the two shapes a search across a
   trade's parameters tells apart, with no figures from the run.
30. Gasoline's 2019 entry date, Saturday, April 13, moved forward to Monday by
   Chan's rule and back to Friday by the outward rule and the nearest trading
   day. A trade date falls on a closed day in 17 of 29 gasoline years and 11
   of 30 natural gas years.

[tests/test_commodity_seasonals_whiteboard.py](../tests/test_commodity_seasonals_whiteboard.py)
reads every sketch but the raised-start and the cliff-or-plateau from the run, so a change to the streak counts, to a gasoline
year's result, to the expiry rule or to the trading calendar moves them too.

## Entry 12: post-earnings drift, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 7.2, Kindle location 3024, and the script
`pead.m` the example names. Shipped under
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20). It is the
first entry from Chan's second book, and its location numbers are that book's,
in [research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from [tests/test_pead.py](../tests/test_pead.py).

**Every number Chan prints reproduces on his own files.** Prices drift in the
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
first-edition rows run, counts a missing value as zero and divides by n − 1, where n counts every
value. Book two's, which Entry 7's revised MATLAB rows run too, skips it and
divides by n, the number of values it kept. With book two's, the arithmetic return is 0.066743, which prints as
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
   survivors**, because the price file is Chan's list of the S&P 500, closest
   to the index as it stood in late 2011, carried back from 2012-04-24.
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
| 11 | row 1 with the first edition's `smartstd` in the moving deviation and the Sharpe ratio | 0.066833, and 1,071 positions | `TestTheHelperMovesADigit::test_the_first_editions_helper_misses_chans_printed_digit`, `::test_the_other_printed_figures_survive_the_swap` and `::test_the_one_position_that_moves_is_pnws_long_on_2012_02_24` |

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
is on Chan's S&P 500 list, which is closest to the index of late 2011 rather
than of 2012-04-24.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) reruns the
rule on a point-in-time universe, which waits on a purchase.

**Whether Chan's flags are the announcement calendar.** They catch three of
the five Apple releases whose next morning falls inside the window, a measurement recorded on
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20).
Entry 46 reruns the rule on a calendar read from EDGAR's filings and on the
archive's Alpha Vantage prices, under
[issue 251](https://github.com/l3a0/quantitative-trading/issues/251).

**What costs would take.** `pead.m` charges none, and every position is a
round trip inside one day.

**How large the look-ahead in the 30 is.** Chan argues it is small because the
maximum number of announcements a day is predictable, and nothing here tests
that.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/post-earnings-drift-lessons.md](../blog/post-earnings-drift-lessons.md)
moves with it, since that post quotes most of these figures. So does the
post's one figure, which `uv run python -m chan.pead_figures` redraws. Its two
whiteboard sketches move too, and `uv run python -m chan.pead_whiteboard`
redraws them. The one after the strategy's rules is schematic and draws none
of these figures. The one in Lesson 4 draws the single position the first
edition's helper drops, PNW's long on 2012-02-24, from the run.

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
on the closes they all read. The revised R prints the Python's three figures to
17 digits, and its own code reads differently.

The spread between 2 and 4 percent is method. The revised Python never uses
its factors. It regresses each stock's returns on an intercept and five factor
series and ranks on the summed fitted values, and with an intercept in the
regression that sum is the stock's summed return. So the Python ranks on a
year of momentum, and its book is the same on every day as a ranking that
leaves the PCA out. The revised MATLAB fits today's cross-section of returns
on the stocks' factor exposures instead. Given the MATLAB's 50 longs, the
Python's book matches the MATLAB's on none of the 752 days both hold a book.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `ijr_20080114/`, the 600 stocks of Chan's
   `IJR_20080114.mat`, saved 2008-01-15, spanning 2004-01-15 to 2008-01-14,
   read for the close through `chan.series.load_panel`. The two MATLAB
   printouts load this file, the Python reads `IJR_20080114.txt`, and the
   printed R reads `IJR_20080114.csv`. The revised repost's `.mat` has the
   sha256 the lifted file has, and the Python's text file holds the same
   closes to 2.0e-16, which
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
| 7 | none | did not reproduce | Neither reading of the printed R lands its printed figures, which are the Python's to the last digit. The R's window ends today rather than yesterday, it buys 52, its mean skips the days that earn no return, and its `sd` divides by n − 1. It sources a `calculateReturns.R` the book does not print, and no R runtime is installed here, so the row is a reading of the code rather than a run of it. [Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it once Chan's download is in hand. |
| 8 | 0 | reproduced | 2.02 percent rounds to 2. |
| 9 | 0 | reproduced | The Python's 4.05 percent rounds to 4, and so does each R reading. The whole-percent figure is reached even by the code whose 17-digit figures are not. |
| 10 | none | did not reproduce | Round-off would leave two books of one size the same on every day. The printed Python buys 49 and the MATLAB 50, so the comparison gives the Python 50, and the books then match on none of 752 days and differ in at least 125 positions on each. The criterion was written on [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the overlap was measured, which is the cost named there. |
| 11 | none | none, not a replication | This is why the Python's figure is momentum's. Its PCA changes no position. |
| 12 | none | none, not a replication | The two revised programs trade mostly different stocks. |
| 13 | none | none, not a replication | The Python's `np.arange(-topN, -1)` never buys the top-ranked stock. |
| 14 | none | none, not a replication | The Python's mean and spread run over all 1,006 rows, including 255 that earn no return, and its `positionsTable[capital==0,]=0` zeroes its first book. The first edition's mean runs over 252 rows that earn no return. |
| 15 | none | none, not a replication | The first edition's `smartstd` zero-fills a missing day and divides by n − 1. |
| 16 | none | none, not a replication | PMC closes at 6.02 on 2004-03-12 and resumes at 17.25 on 2007-08-01, two price histories under one symbol. Every program but the unfilled R reading forward-fills, so the gap becomes one day's return of 1.8654. |

### What the entry concludes

Two things.

1. **The first edition's MATLAB, the revised MATLAB and the revised Python
   reproduce on Chan's file.** The first edition's −1.8099 and the revised
   MATLAB's 0.020205 and 0.211120 land at the precision printed, and the
   revised Python's three 17-digit figures land within 1e-15.
2. **The 2-versus-4 spread is two different strategies, not round-off.** The
   revised MATLAB trades a factor model and the Python trades a year of
   momentum, because it ranks on fitted values summed over the year, which its
   regression's intercept makes equal to summed returns. Three
   bookkeeping choices each lower the Python's figure toward the MATLAB's: its
   long side, its averaging, and the first book it clears. Without any one of
   them the Python's figure is higher than 4.05 percent, rows 13 and 14.

### What this entry cannot say

Three things.

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
it, since that post quotes most of these figures. That post's Lesson 2
whiteboard sketch, which draws the residuals cancelling so that the revised
Python ranks on each stock's own returns, is schematic and draws none of these
figures, and `uv run python -m chan.factor_models_whiteboard` redraws it.

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
index's return over the three-month bill rate, the way French's market factor
is built over the one-month rate. WML, winners minus losers, defined at
location 4004, longs the stocks whose past return was positive and shorts
those whose past return was negative. Over 83 months,
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
| 1 | reproduced | The claim holds for MKT, which Chan says factors "often" show. Its autocorrelation is above 0 and above the median stock's, under the criterion declared on the issue before any autocorrelation was computed. It sits at 0.0675, inside row 6's band, so a series of independent returns would land there often, and this verdict could be noise. |
| 2 | did not reproduce | The claim, which Chan says factors "often" show, does not hold for WML, on either half: its autocorrelation is below 0 and below the median stock's. Under the owner's ruling this verdict stands on its own, and no combined verdict is drawn from rows 1 and 2. The value is forced, because the log's two other verdicts both need the claim to survive. Two causes outside the method are open and neither is measured: the panel holds only survivors, and 2000 to 2007 is one window. Nothing here argues which way either moves an autocorrelation. |
| 3 | none, not a replication | MKT sits at the 80.7175th percentile of the stocks, above 360 of 446. |
| 4 | none, not a replication | WML sits at the 27.8027th percentile, above 124 of 446, so it is less persistent than most single stocks on this file. |
| 5 | none, not a replication | The quartiles use pandas' default linear interpolation. The median is negative, so on this file a factor above 0 is also above the median stock. That is a fact about this panel, and the criterion keeps both halves as declared. |
| 6 | none, not a replication | Under a series of independent returns, an estimate from 83 months falls outside ±0.2151 about 5 percent of the time. Both factors sit inside it, so neither verdict rests on an autocorrelation 83 months can tell from zero. |
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
   series of independent returns stays inside 95 percent of the time, so 83
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

No single pair's result counts as a verdict, because 56 days give one pair
little power, and none is a finding about that pair. Every result here is
**exploratory**. The sample was spent on a claim Chan stated, so the entry says
whether these spreads behaved as he said over these windows and nothing about
whether trading them pays.

### What the book printed

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`. *Algorithmic Trading* (2013),
published between this book's two editions, qualifies the sentence at its
location 2321, saying calendar spreads "do not generally mean-revert". The issue recorded that as a prior against the
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
| 10 | none, not a replication | A measure of power. If every natural gas pair reverted at 36 days, 21.9 of 360 would reject on average. The real 57 is far more than these sets give, so whatever produces the rejections reverts faster within these windows, or comes from something neither simulation models. The row decides neither. |
| 11 | none, not a replication | If every RBOB pair reverted at 36 days, 13.5 of 220 would reject on average. The real 14 is about what reversion that slow would give, and also about what no reversion at all gives under row 2's null, so a 56-day window cannot tell the two apart for RBOB. Rows 10 and 11 build each pair's legs from a spread as volatile as the walk, so the legs move together far less closely than the files' contracts, the omission the corrected null fixed. On legs that move together as the files' do, reversion this slow would likely give more in both commodities, above RBOB's 14 and closer to natural gas's 57. That has not been rerun, and [issue 707](https://github.com/l3a0/quantitative-trading/issues/707) pins it. |
| 12 | none, not a replication | Added after the verdicts were seen, because a bar alone does not say how close a verdict sat to it. |
| 13 | none, not a replication | The rule's day fits 298 of 316 handovers, about 94%, and a day either side fits between 4% and 12% of them, so the map reads the right contract on almost every day. Whether each of the 18 that do not fit is noise or a rule one day off is not settled here, and one day is what the dropped days absorb. A rule two days off would read a neighbouring contract on one kept day in each of up to three pairs around an expiry, which these counts do not rule out. |
| 14 | none, not a replication | The same reading for RBOB, with 11 that do not fit. The check starts at the January 2006 expiry, but the first two pairs also read the October, November and December 2005 expiries. From 3 October to 30 December 2005 the files hold the January to April 2006 contracts, so no handover falls on the rule's day for November or December 2005, and the pairs at January and February 2006 read the wrong contracts on every day they keep before December 2005. As read, neither rejects. Read as the files hold them, the February pair rejects in both orientations, which would make row 2's 14 a 15, far under the bar of 31. `TestTheFirstRbobPairs` pins this, and [issue 704](https://github.com/l3a0/quantitative-trading/issues/704) fixes the reading. |

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
   gas pairs rejecting in both orientations, and a null at the files'
   correlation has 35. The
   declared null missed that, and it is why the bars were corrected.
3. **The expiry map holds where it was checked, and one correction to it was
   owed.** Three days the calendar listed as closures, the two days of
   Hurricane Sandy in October 2012 and 2018-12-05, are days every natural gas
   and RBOB file settled. Counted closed, they put the November 2012 natural
   gas expiry two trading days early, beyond what the dropped days absorb, so
   the calendar no longer counts them closed. No figure in Entry 11 reads any
   of the three. The check did not read RBOB's 2005 expiries, and the map is
   wrong there, as row 14 says.

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

### The post's sketches

The calendar spreads post carries two whiteboard sketches, added in its review
before publishing on 2026-10-21.

1. **Each orientation alone.** It draws natural gas's null counts as circles
   whose areas stand for them. Each orientation alone rejects in a median of
   38 of 360 null pairs under either null, so correlating the walks leaves each
   orientation where it was, and the rise from 12 to 35 in row 3's and row 1's
   medians is the requirement for both losing its effect.
   `TestTheNullInEachOrientation` pins those medians beside RBOB's, 24 and 23
   under the declared null and 23 and 23 under the corrected one. They read the
   vintages and specification of rows 1 to 12, counting one orientation at a
   time on the same walks. They describe the nulls, decide nothing, and were
   computed after the verdicts were seen.
2. **One window.** It draws the June 2018 natural gas pair's window, its four
   expiries, the numbered file each leg reads on each day, and the six days it
   drops. `TestThePairs` already pins that window and those days.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.
[blog/calendar-spreads-lessons.md](../blog/calendar-spreads-lessons.md) moves
with it, since that post writes up every row, and so does
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md),
since that post quotes the verdicts. So do the calendar spreads post's figure
and its two sketches, which `uv run python -m chan.calendar_spread_figures` and
`uv run python -m chan.calendar_spreads_whiteboard` redraw.

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
lines that close `kentdaniel.m` record 0.0315 and 0.40 over the same 2007
window, which is where
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297) started.
Transcribed and run on the file it loads, the script gives none of the five
figures its comment records. It gives a Sharpe ratio of 4.0657, and a
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
decides nothing. Chan's word "APR" names the arithmetic figure in Example 7.2,
and the figures seen afterwards point to the compounded one here. A rule taken
from one example did not carry to the next.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read for
   the close through `chan.series.load_panel`.
   [data/README.md](../data/README.md) records where it came from. **Every
   figure here is about survivors**, because the file holds stocks that were in
   the S&P 500 in late 2011, carried backwards, and a company that was out of
   the index for all of late 2011 is not in it. That reaches the two legs in opposite directions. The
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

The comment lines that close `kentdaniel.m` record five figures for the 2007
window. The book quotes two figures for that window, one for 2008 and
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
R1 to R4 as what could explain a script whose comment records 0.40 against a
book printing 4.1, each changing one thing from the script, and no combination
was run. Each cell is the arithmetic annual return and then the Sharpe ratio,
from `TestTheReadings` and `TestTheScriptOverTheOtherWindows`. A reading lands when
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

The readings were declared to explain a script whose comment records 0.40
against a book printing 4.1. The code's own Sharpe ratio is 4.0657, and their
2007 Sharpe ratios span 3.82 to 4.28 around it. Long losers and short winners
was declared too, and negating every position negates every
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
3. **The crash Chan describes is in the file.** The strategy earned a Sharpe
   ratio of 4.0657 over 2007, which row 7 judges, and an arithmetic return of
   −0.323195 over 2008 and 2009, which row 8 judges. Seen only after the run,
   and deciding nothing, it fell into a drawdown of −0.606634 from a high on
   2008-07-14 and was still below that high 371 days later, when the window
   ended, so the drawdown had not finished. Its arithmetic return from 2010 to
   2012 was 0.016244, which row 9's rule, fixed before the run, reads as
   stabilised below 2007's. That is the collapse location 2890 describes,
   where momentum "vanished during the aftermath of the stock market crash".

### What this entry cannot say

Six things.

**Which run printed the comment.** The comment's 182-day longest drawdown
cannot come from the 2007 window as the script computes it, so no file with
one row per trading day, read over that window, could have printed the
comment. `calculateMaxDD` over a window's rows counts at most one fewer days
than the window holds, and the window holds 160.
`TestWhatThePostQuotes::test_the_comments_longest_drawdown_cannot_come_from_the_window`
asserts both. A different window or version of the script, read from this
file or another, might have printed the comment's figures. Trying them until
one did would be the search the issue's rule forbids, so none was tried.

**What survivorship does to these figures.** Every stock here was in the
S&P 500 in late 2011, and the two legs lose different stocks.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) waits on
a panel that could measure what that costs a cross-sectional rule.

**What costs would take.** `kentdaniel.m` charges none, and every day one
cohort of 100 picks enters and the one formed 25 days earlier leaves.

**Whether momentum pays today.** The sample ends in April 2012.

**Whether Chan's cause for momentum crashes holds here.** At location 2890 he
writes that a crash "is mainly due to the strong rebound of short positions
following a market crisis". No run here splits each day's return by the side
of each position, so nothing tests that cause on this strategy.

**Whether ETFC's close on 2007-11-12 was a real price.** It fell from 85.9 to
35.5, the one close in the 2007 window that the scale-break guard flags as too
far from the day before to be an ordinary move, and all 25 cohorts held ETFC
short going into it, which `TestTheScaleBreakDecision` holds. The run does not
call the guard, for the reason the module docstring gives, and no other source
has been checked for that close.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/cross-sectional-momentum-lessons.md](../blog/cross-sectional-momentum-lessons.md)
moves with it, since that post quotes most of these figures. So do its one
figure, which `uv run python -m chan.cross_sectional_momentum_figures`
redraws, and its two whiteboard sketches, which print the cohort counts and
the 2007 window's sum, product and two annual returns, and which
`uv run python -m chan.cross_sectional_momentum_whiteboard` redraws.

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
up to ten stocks that opened furthest below their previous day's low, by more
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
   name in either of the two public mirrors data/README.md names is the same
   bytes, which
   [data/README.md](../data/README.md) records. **Every figure here is about
   survivors**, because the file holds stocks that were in the S&P 500 in late
   2011, carried backwards, and location 1974 says the universe has
   survivorship bias.
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

`bog.m`'s last `fprintf` line is followed by the comment
`% APR=8.7%, Sharpe=1.5`. Its `fprintf` lines
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
| 8 to 12 | the qualifiers and positions, the first positions, the other `smartstd`, the late listings and the flagged closes | none, the book prints no such figures | n/a |

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
| 12 | positions that land on one of the 30 closes the scale-break guard flags | 1, MS short on 2008-10-13 | `TestTheScaleBreakDecision::test_one_position_falls_on_a_flagged_day` |

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
| 12 | none | none, not a replication | The run does not call the guard. `TestTheScaleBreakDecision` calls it, and this row counts what it would have refused. The issue decided not to call it on the reasoning [issue 18](https://github.com/l3a0/quantitative-trading/issues/18), [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) and [issue 22](https://github.com/l3a0/quantitative-trading/issues/22) give. |

### What the entry concludes

Three things.

1. **Example 4.1 reproduces exactly on Chan's own file.** Both figures `bog.m`
   prints land at the precision printed, and only with book two's `smartstd`
   inside the spread.
2. **One phrase names two formulas in this book.** In Example 7.2, "annualized
   average return" is the arithmetic figure. At location 3509 the same phrase
   carries Example 4.1's compounded APR, which the arithmetic figure misses.
   Reading the label instead of the script would have pinned row 2 against
   the arithmetic figure and called it a miss. Entry 17 found the word "APR"
   naming the arithmetic figure in Example 7.2, while the figures it saw
   afterwards point to the compounded one in Example 6.2.
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

**Which file Chan ran in 2012.** The name `bog.m` loads points, in the one
public mirror this repository has read that holds a file of that name, at the
same bytes as the
committed panel's source. That says
what the name means in the code he published, not that the file he ran when
he wrote the book was this one. Both figures reproducing is consistent with
it and does not prove it.

**What costs and execution would take.** `bog.m` charges none. Location 1993
names the short-sale constraint the mirror suffers from, and location 1988
names the signal noise of deciding on the official open, which cannot be known
before the trade at that open.

**What the rule earned on the index as it stood each day.** Every stock here
was in the S&P 500 in late 2011. The point-in-time panel
[issue 252](https://github.com/l3a0/quantitative-trading/issues/252) waits on
would answer it for this rule too.

**Whether MS's flagged day was a clean print.** The guard flags the move from
2008-10-10 to 2008-10-13 as too large for a price change, and the mirror shorted
MS that day. Nothing here checks the print against another source.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/buy-on-gap-lessons.md](../blog/buy-on-gap-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.buy_on_gap_figures` redraws, and its one whiteboard
sketch, after the strategy's rules, which draws PCS on 2011-01-06 to scale and
which `uv run python -m chan.buy_on_gap_whiteboard` redraws through the same
`entry_price` that `drop_qualifiers` compares the open against.

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

**Every return and Sharpe ratio Chan prints reproduces on his own file.** The rule is the one
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
   agree on a series with no missing day, which both examples' series are, so
   this difference moves neither example's figures.

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
   panel holds 497 stocks that were in the S&P 500 in late 2011, and the run
   treats them as the index on every earlier day it has a price for them.
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

1. **Examples 4.3 and 4.4 reproduce on Chan's own file.** All six returns and Sharpe
   ratios the book prints land at its precision, and Example 4.4's two land at the
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
   holds. The data include a longer survivor horizon. This panel's list
   dates from late 2011, almost five years after the window opens in 2007,
   where Entry 8's dates from 2007-11-23, under two years after its window
   opens in 2006. Nothing here prices what that adds.
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
was in the S&P 500 in late 2011.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) prices
survivorship on this file for Example 7.2 over 2011 and 2012, and nothing yet
prices it for this rule over 2007 to 2011.

**Whether 2008 to 2011 is out of sample in Chan's sense.** He calls it "a
true out-of-sample test, as the strategy was published in 2007". It is out of
sample in time, but the stocks were chosen from the index of late 2011, so the
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
figure, which `uv run python -m chan.khandani_lo_book_two_figures` redraws,
and so do its two whiteboard sketches, CAH's bounce in Lesson 2 and the
average day's cost and profit in Lesson 4, which
`uv run python -m chan.khandani_lo_book_two_whiteboard` redraws from the same
runs.

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
   hedge inside the cap grows at 0.656501. The best long-only allocation there
   holds strategy 2 alone at its own Kelly leverage of 3.333333, inside the
   cap, and grows at 0.5. That is why the module's capped search says it is
   long-only.

### What this entry cannot say

Two things.

**Whether Equation 8.3 prints a number.** Row 11 waits on the book itself. If
it prints a value, the row gains a published figure and a verdict.

**Anything about a real pair of strategies.** Every input is hypothetical and
Gaussian by assumption. Whether a cap makes a real second strategy worth
dropping depends on moments estimated from data, with the estimation error
location 3235 warns about.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/capped-kelly-allocation-lessons.md](../blog/capped-kelly-allocation-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.kelly_allocation_figures` redraws.

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

**Two of the three scripts reproduce to six decimals on Chan's own file, and the
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
and USO swapped lands both, to all six decimals, a reading tried after the miss,
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
`fprintf('APR=%f Sharpe=%f')` prints. Location 1505 prints the first two
scripts' figures at fewer decimals. Three of them are the scripts' figures
rounded. The fourth, the price spread's "about 10.9 percent", is not, since
0.108335 rounds to 10.8 percent. It prints no number for the ratio.

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
| 10 | the first day with units, and the first day a return is earned, on each of the three scripts and the ratio with GLD and USO swapped | 2006-06-21 and 2006-06-22 | `TestTheFigures::test_the_first_position_is_held_into_2006_06_22` |
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
| 9 | none | none, not a replication | A reading chosen after row 5 missed, the third of three that [issue 340](https://github.com/l3a0/quantitative-trading/issues/340) names. The other two, keeping the first 20 days and Chan's Python port, match neither figure, which `TestTheRatio::test_keeping_the_first_20_days_matches_neither_figure` and `::test_chans_python_port_matches_neither_figure` hold. It lands both of the comment's figures to six decimals. The two come from one return series, so they are not independent matches, but a coincidence would still have to land two different summaries of it. |
| 10 | none | none, not a replication | `movingStd` first fills on the 20th kept row, and a position earns from the next close, so each of the three scripts, and the ratio with GLD and USO swapped, holds its first position into 2006-06-22. Row 9's other two readings keep the first 20 days, so theirs is held into 2006-05-24. |
| 11 | none | none, not a replication | Neither mirror holds `lag.m`. A NaN pad makes the first row's return NaN. A zero pad divides by a price of 0, so the first row's profit is NaN over zero gross dollars, and either NaN is set to 0. The return is profit over gross dollars, so a deviation that divides by n rather than n − 1 scales every unit by one factor and cancels. |

### What the entry concludes

Three things.

1. **Example 3.1's price spread and log price spread reproduce exactly on
   Chan's own file.** All four figures the two scripts print land to six
   decimals. The book's "about 10.9 percent" is the one rounding that does not
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
scripts trade never subtracts the 20-day fit's intercept, which tracks it at a
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
figure, which `uv run python -m chan.price_spread_figures` redraws, and its one
whiteboard sketch in Lesson 4, which `uv run python -m chan.price_spread_whiteboard`
redraws through the same `rolling_intercept` that
`::test_the_spread_is_almost_all_the_fits_intercept` reads.

## Entry 22: the stationarity tests on USD.CAD, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Examples 2.1 to 2.5, Kindle locations 1076 to 1225,
with the half-life repeated at 1347. Shipped under
[issue 338](https://github.com/l3a0/quantitative-trading/issues/338). One
script, `stationarityTests.m`, runs all five examples in order on the same
closes, and its comments print every figure but one. The script is in
ericnberwick/EpchanPreview at `e4bc46f`, under `public/img/book2/`.

Eleven rows, all derivable from
[tests/test_usdcad_mean_reversion.py](../tests/test_usdcad_mean_reversion.py).
Eight do not match one printed figure to one computation, and each says so in
its own cells. Rows 1, 3, 5 and 6 each cover more than one figure from one
computation. Rows 8 to 11 carry no published figure.

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
| 11 | 2.5, the Sharpe ratio against a fixed account | none, the book prints none | n/a |

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
| 11 | `√252 · mean / std` of the daily P&L, `ddof=1`, no risk-free rate, over the 1,101 days whose previous-day position is not NaN, 2008-01-02 to 2012-03-28 | the same | 0.1188463477 | `TestExample25LinearMeanReversion::test_the_sharpe_ratio_against_any_fixed_account_is_0_12` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000 at six decimals | reproduced | Exact at the six decimals the script prints. Location 1114's reading survives: the statistic sits above the 10 percent value of −2.594, so a unit root is not rejected. |
| 2 | −0.000000 at six decimals | reproduced | Exact at that precision. λ, the estimate less 1, is negative, which is location 1114's second reading. |
| 3 | −0.000, −0.000 and +0.000 at three decimals | reproduced | Exact at that precision. 1,216 observations fall in the table's last bin, which every series of 425 or more reads. |
| 4 | −0.02 at two decimals | did not reproduce | 0.4732 prints as 0.47 against the book's 0.49, on the closes every other test lands. The claim the figure was printed for survives as far as H can carry it: H is below 0.5, which location 1119 reads as weakly mean reverting, though no estimate here can be told apart from a random walk of the same length. No cause outside the method is shown to apply. A `genhurst` older than the one every surviving copy carries would be a different method rather than a different vintage. A sample starting one day later prints 0.49, and the closes the script's comments match rule that out for the run those comments record. The section on how far H moves by chance measures both. |
| 5 | +0.000000 at six decimals | reproduced | The decision is exact and the p-value is exact at six decimals. The variance ratio is 0.9647, below 1, as a reverting series gives, and not significantly so. |
| 6 | +0.000000 at six decimals, and 0 days | reproduced | Exact at the six decimals the script prints, and at the whole days the book prints. |
| 7 | none, a claim | reproduced | The criterion written on [issue 338](https://github.com/l3a0/quantitative-trading/issues/338) before any P&L existed holds. The P&L ends at 0.1141, above 0. |
| 8 | none | none, not a replication | Both `ithildincore`'s `adf_tstat` and the ADF line in Chan's 2018 Python port run `adfuller`, which fits the one row jplv7 drops. The Python port would print −1.843018 for the figure the script's comment records as −1.840744. |
| 9 | none | none, not a replication | The port's `genhurst` is a different estimator, the slope of the log variance of τ-day changes on log τ, halved. It lands nearer the book than Aste's, at 0.48, and still misses 0.49. |
| 10 | none | none, not a replication | The cumulative P&L reaches 0.1321 on 2008-07-22 and falls to −0.5104 on 2008-10-27, a drop more than five times what the run ends with. That reads as large on any scale, but the book gives none, so it decides nothing. |
| 11 | none | none, not a replication | The P&L is in units of the position, but dividing every day by one fixed account leaves the ratio of mean to standard deviation unchanged, so the figure is the same against any account. The annual return is not, so it stays undefined, and no account is guaranteed to fund a position with no upper limit. |

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
   these closes. Every reading of H here sits below 0.5, as the book's does.
   The two estimators the section below measures each sit within about one SD
   of their own random-walk average. So an H this close to 0.5 cannot be told
   from a random walk on 1,216 days, and the variance ratio test says the same
   thing more carefully.
4. **Example 2.5's claim survives, and it carries the look-ahead Chan names.**
   The lookback of 115 days is the half-life of the same 1,216 closes the
   strategy trades. Its P&L ends positive at 0.1141 after falling 0.6425 from
   a high of 0.1321, and whether that survives a lookback chosen without seeing
   the closes is a question this entry does not ask.

### How far H moves by chance and by its start day

Row 4 says H misses. It does not say whether a miss of 0.02 means anything,
which depends on how far H moves when nothing but chance moves it. The owner
asked how significant the miss is, and
[issue 590](https://github.com/l3a0/quantitative-trading/issues/590) set out
the measurement.

This check is exploratory. It was designed after the miss had been seen, so
it reads the miss rather than testing a claim written down before it.

[src/chan/usdcad_hurst_noise.py](../src/chan/usdcad_hurst_noise.py) measures
two things on the vintage every row reads.

1. **Each estimator on random walks of the same length.** 40,000 Gaussian
   random walks of 1,216 log prices, from `numpy.random.default_rng(20261011)`,
   with `genhurst(z, 2)` at `maxT` 19 and the Python port's estimator on each.
   Both ignore a series' scale and drift, which a test checks, so the walks
   take standard normal steps. A random walk's theoretical H is 0.5, and the
   port's estimator does not average that at 1,216 points, so each observed
   H is set against its own estimator's random-walk mean.
2. **Both estimators with the first 0 to 10 closes dropped.** `genhurst`
   samples every `tt`-th close counting from the first, so the start day
   changes which closes it reads. The port's estimator uses every overlapping
   change. At each start the ADF statistic at trend order 0 and 1 lag, the
   variance ratio test at period 2 and the half-life are computed too.

| Measurement | Computed | Assertion |
| --- | --- | --- |
| `genhurst` on the random walks, mean and SD | 0.49622344 and 0.02314563 | `TestExample22HowFarHMovesByChance::test_genhurst_on_a_random_walk_averages_0_496_with_an_sd_of_0_023` |
| The port's estimator on the random walks, mean and SD | 0.47534832 and 0.05767276 | `TestExample22HowFarHMovesByChance::test_the_port_estimator_on_a_random_walk_runs_low_between_0_47_and_0_48` |
| Walks below the observed H, `genhurst` and the port | 6,434 and 19,575 of 40,000 | `TestExample22HowFarHMovesByChance::test_where_each_observed_h_falls_among_the_walks` |
| Random-walk mean minus the observed H, in SDs | 0.993309 and −0.008597 | `TestExample22HowFarHMovesByChance::test_each_estimate_against_its_own_estimators_random_walks` |
| 0.49 minus the observed H, in SDs | 0.724428 and 0.245452 | `TestExample22HowFarHMovesByChance::test_the_gap_to_the_books_0_49_is_under_one_sd` |
| `genhurst` from the first close and from the second | 0.4732326652 and 0.4890716563 | `TestExample22HowFarHMovesByChance::test_genhurst_moves_to_0_49_when_the_first_close_is_dropped` |
| Start offsets of 0 to 10 whose `genhurst` prints as 0.49 | 6, at offsets 1, 3, 4, 6, 8 and 9 | `TestExample22HowFarHMovesByChance::test_six_of_eleven_start_days_print_as_0_49` |
| The highest `genhurst` of the eleven, at offset 5 | 0.5061926171 | `TestExample22HowFarHMovesByChance::test_the_first_close_gives_the_lowest_genhurst_and_one_start_day_tops_a_half` |
| The port's estimator across the eleven, lowest and highest | 0.4741152609 and 0.4758441244 | `TestExample22HowFarHMovesByChance::test_the_port_estimator_barely_moves_with_the_start_day` |
| The ADF statistic from the second close | −1.83614998 | `TestExample22HowFarHMovesByChance::test_only_the_first_close_lands_the_scripts_other_figures` |

The table holds what seed 20261011 gives, which the tests pin exactly. What
40,000 walks support is narrower, and
`TestExample22HowFarHMovesByChance::test_the_standard_errors_of_40_000_walks`
pins the standard errors behind it. A mean's is 0.00012 for `genhurst` and
0.00029 for the port, an SD's is 0.00008 and 0.00020, and a share below the
observed H's is 0.18 and 0.25 percentage points. Each figure below is quoted
only where it and two standard errors either side round to the same digits,
which the tests check. `genhurst`'s distance from 0.5, 1.156 SDs, is pinned
and quoted nowhere, since two standard errors reach the 1.15 rounding
boundary.

Four findings.

1. **Neither estimate can be told apart from a random walk.** `genhurst`
   averages 0.496 on the random walks, with an SD of 0.023, and its 0.4732 is
   1.0 SD below that, with 16 percent of walks lower. The port's estimator
   averages between 0.47 and 0.48, with an SD of 0.06, and its 0.4758 is
   within 0.1 SD of that, with about half the walks lower.
2. **The misses are smaller than one random-walk SD.** The book's 0.49 is 0.7
   `genhurst` SDs above 0.4732 and 0.2 port SDs above 0.4758.
3. **One day of start is enough to print 0.49 for `genhurst`.** Dropping the
   first close moves it to 0.4891, and six of the eleven start days print as
   0.49. The script's own start gives the lowest of the eleven, and offset 5
   gives 0.5062, above 0.5. The port's estimator stays between 0.4741 and
   0.4758, so no start explains its miss.
4. **The run the script's comments record starts on the first close.** Only
   offset 0 lands the ADF statistic, the variance ratio's p-value and the
   half-life those comments print. From the second close the ADF statistic is
   −1.836150. So a later start would explain `genhurst`'s 0.49 only if the
   book's H came from another run, and with no public copy of
   `inputData_USDCAD.mat` that cannot be checked.

Row 4's verdict stands. A later start is a cause outside the method, but the
closes the script's comments match rule it out for that run, and nothing shows
the book's H came from another. Nothing here adopts a start day either. The
headline H stays the script's, from the first close, because taking the start
that lands 0.49 would choose the data after seeing its number. No block
bootstrap of USD.CAD's own returns was run. Resampling returns keeps their
short-range structure and breaks any reversion longer than a block, so it asks
a different question. Entry 33's miss on TU runs through the same `genhurst`,
so the same start-day sensitivity may apply there, and nothing here measures
it.

### What this entry cannot say

Three things.

**What computed the book's 0.49.** No surviving copy of `genhurst` gives it on
the closes the script's comments match, and the script that printed it
records no value. Six of the ten later start days give it, and nothing public
shows which run the book's figure came from. Searching for the variant that
lands it would be choosing a reading after its number is seen.

**Whether Example 2.5 would pay.** The look-ahead above, no transaction cost,
and a position that grows without limit as the deviation does, all of which
location 1225 names. The P&L is in units of the position's own scale rather
than a return on capital. Against any fixed account it has a Sharpe ratio of
0.12, row 11, which the book does not print. It has no APR, because the return
depends on an account size the rule never names, and no account is guaranteed
to fund a position with no upper limit.

**Anything about USD.CAD after March 2012.** Every figure is exploratory, on a
sample Chan already chose. Entry 51 trades Example 2.5's rule on a vendor's
closes after 2012 at the lookback fixed here, and carries that result.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/usdcad-stationarity-lessons.md](../blog/usdcad-stationarity-lessons.md)
moves with it, since that post quotes most of these figures. So do its two
charts in Lesson 4, the whole run and the fall alone with the position the
rule held, which `uv run python -m chan.usdcad_mean_reversion_figures`
redraws, and its fourteen whiteboard sketches, which
`uv run python -m chan.usdcad_tests_whiteboard` redraws.

1. One in its opening section.
2. Six in its section on the tests.
3. Two in Lesson 1.
4. One in Lesson 2.
5. Two in Lesson 3.
6. Two in Lesson 5.

[blog/usdcad-holdout-lessons.md](../blog/usdcad-holdout-lessons.md) sets
about ten of these figures beside Entry 51's, so a change to one of them moves
that post too.

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
| 6 | 2.7, both tests find two relations for the pair at 95 percent | a claim, with the trace's r ≤ 0 rejected at 99 percent | location 1324 |
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

Three things.

**Whether the portfolio works out of sample.** No row refits the eigenvector
on one window and trades it on the next. That is the experiment that would
price the third conclusion above, and it is a different run with its own
issue to file.

**Anything about costs.** The linear rule trades every day by construction, and
location 1350 calls it impractical for that reason. No cost is charged here, as
none is in the script.

**Whether another lag count changes the counts.** Every Johansen call in a
book-two script uses `k = 1`, and so does this entry. The relation counts in
rows 6 and 9 are for that lag alone, and row 6's rests on a margin of 0.141.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.
[blog/johansen-etf-lessons.md](../blog/johansen-etf-lessons.md) quotes most of
these figures, and the suite does check that post. `TestWhatThePostQuotes` in
[tests/test_etf_cointegration.py](../tests/test_etf_cointegration.py) rebuilds
each figure the post quotes from the run and fails when the post no longer
says it. So a re-pin that leaves the post behind fails the suite, while one
that leaves this entry behind does not. The post's one figure moves with it
too, and `uv run python -m chan.etf_cointegration_figures` redraws it. So does
its first whiteboard sketch. That sketch draws row 8's three eigen statistics,
row 7's trace statistic for r ≤ 0, and the 90 percent eigen and 95 percent
trace critical values pinned beside those rows, all to one scale.
`uv run python -m chan.etf_cointegration_whiteboard` redraws it and the post's
second sketch, the pair's two relations mixing into EWA held alone, which is
schematic.
[tests/test_etf_cointegration_whiteboard.py](../tests/test_etf_cointegration_whiteboard.py)
reads the first sketch's figures from the run.

## Entry 24: SPY against its component stocks, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 4.2, Kindle locations 2027 and 2035, and the
script `indexArb.m` the example names. Shipped under
[issue 343](https://github.com/l3a0/quantitative-trading/issues/343). Every
example number and location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seventeen rows, all derivable from
[tests/test_index_arbitrage.py](../tests/test_index_arbitrage.py).

Chan trades an index against the stocks inside it. He tests each stock in his
2012 stock file against SPY over 2007 with the Johansen test, keeps the
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
Chan's figures spends the 2007 to 2012 sample on a rule he chose. The panel
holds stocks that were in the S&P 500 in late 2011, carried back to 2006, so
the 2007 screen picks only from those, and row 17 counts 14 of its 98 that the
two committed lists show out of the index at some point. The stocks and weights
come from 2007 and trade from 2008, but location 2035 says the lookback of 5 was fixed "with the
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
| 17 | The basket's stocks that were out of the index at some point | none | n/a |

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
| 15 | The screen on 2,000 Gaussian random walks with no drift, seeded with 343, against SPY's 2007 closes | 561 pass, 28.1 percent, about 135 of 480 | `TestBesideTheReplication::test_the_screen_passes_561_of_2000_walks_unrelated_to_spy` |
| 16 | `johansen(·, 0, 1)` on 2,000 pairs of such walks, seeded with 345 | r ≤ 0 rejected on 410 at the 90 percent value and 242 at the 95, 20.5 and 12.1 percent | `TestBesideTheReplication::test_the_trace_test_rejects_two_to_three_times_its_nominal_rate_on_unrelated_walks` |
| 17 | The 98 against Chan's `spx_20071123` list and the IVV schedules from 2008-12-31 | 12 not on the 2007-11-23 list, and ACE and CBE missing at quarter-ends of the test, 14 in all | `TestTheBasketsStocksAndTheIndex::test_12_of_the_98_were_not_on_the_index_list_of_2007_11_23` and `::test_ace_and_cooper_industries_left_the_index_during_the_test_and_came_back` and `::test_ak_steel_is_in_the_basket_after_it_left_the_index` |

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
| 17 | none | none, not a replication | The file's list is from late 2011, so the 2007 screen can pick stocks that joined the index later or left and came back. AKS also left in December 2011 and stays in the basket to the end. |

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
   shows the screen passing 28.1 percent of such walks against SPY's own 2007
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
   hindsight, so it was not, and the screen picks only from stocks that were
   in the index in late 2011, 14 of which row 17 finds out of it at some point.
   Nothing here measures how much either is worth.

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

**How much survivorship bias is worth.** Chan's list of the index on
2007-11-23 is committed, but its prices end on that day. Screening the index as
it stood and trading the result would need 2007 to 2012 prices for every company
on it that the 2012 file lacks, and no run here has assembled them.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/index-arbitrage-lessons.md](../blog/index-arbitrage-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.index_arbitrage_figures` redraws, and its one
whiteboard sketch in "What one unit holds, and when it first earns", which draws the first
eigenvector's dollars to scale and which
`uv run python -m chan.index_arbitrage_whiteboard` redraws through the same
`read_sources` and `index_arbitrage`.

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
says the committed daily files carry the closes the MATLAB traded, up to a
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
the mean of squared returns takes the saved series to 18.4. Entry 43 carries
that figure, and its section
[What the book's 18.4 most likely came from](#what-the-books-184-most-likely-came-from) gives the
evidence that Chapter 8 ran on a different series of returns, with a Kelly near
18.4, that nobody holds and that no series matching this example's printed
Sharpe ratio and APR can be. The evidence cannot tell when or how that series
differed from the saved file.

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

Four things.

1. **The committed currency files carry the closes Chan's MATLAB traded, up
   to a constant scale on each leg.** The script loaded two minute `.mat`
   files that neither mirror carries, and this run read the Python port's daily
   copies. Every one of the 612 returns lands on the one Chan saved, inside the
   1e-9 declared before the run, and the largest difference was 2.0e-15 where
   the entry was built. Two things bound what that shows, and
   `TestRow5TheReturnsAreChans` holds both.
   1. Scaling either leg by a constant moves no return, because a simple
      return ignores the scale and the eigenvector rescales to cancel it.
      Doubling AUD.USD halves its weight in every day's hedge, so each leg
      holds the same dollars, and
      `test_doubling_aud_usd_halves_its_weight_and_holds_the_same_dollars`
      holds that too.
   2. A change of 1e-6, one unit in the sixth decimal, the most the files
      quote, on a close in the test window breaks the match, because the
      close enters a simple return directly. The same change on the first
      training row does not,
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
4. **The 90 days the hedge held both currencies the same way show nothing
   chance cannot explain.** On those days the hedge was long or short the US
   dollar against both currencies rather than a spread. Each hedge earns the
   next day's return, so the 90 returns that go with them are dated a day
   later. They compound alone to 0.1111 and the other 522 to 0.1657. They
   swung about twice as wide, a standard deviation of 0.0074 against 0.0034,
   and averaged 0.0012 a day against 0.0003. A Welch t of 1.13, with p of
   0.26, cannot rule out chance for that difference, so this is a null
   result, and an exploratory one.
   `TestBesideTheReplication::test_the_90_days_hedges_earned_0_1111_and_the_other_522_0_1657`
   and
   `::test_the_90_days_hedges_swung_twice_as_wide_and_a_welch_t_of_1_13_cannot_rule_out_chance`
   hold it.

### What this entry cannot say

Three things.

**Anything about costs or rollover interest.** The rule trades every day, and
no cost is charged, as none is in the script. Location 2205 sets rollover
interest aside for this example as small for a short-term strategy, and
nothing here measures how small.

**What another training length would show.** Location 2237 says the 250-day
length gives better results in hindsight, so it was chosen with this sample's
results in view. No row runs another length, and any that did would be
searching the sample this entry already spent.

**Whether the pair trades today.** The run ends on 2012-04-26 with Chan's
data. It says whether his numbers reproduce on his files and nothing about the
two currencies since.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/aud-cad-johansen-lessons.md](../blog/aud-cad-johansen-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.aud_cad_johansen_figures` redraws. So do the
post's two whiteboard sketches, which print the run's figures, and
`uv run python -m chan.aud_cad_johansen_whiteboard` redraws them. The scale
sketch is schematic apart from its scales and its count of returns. The share
sketch draws the last day's hedge from the run, and its equal pair and its
pair held the same way are schematic.

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
rule holds minus the spread's z-score in units of the pair on every day the z-score
exists, so from then on it is always in the market. Example 3.2 trades the same GLD and USO price spread with
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

The script records the six decimals its `fprintf('APR=%f Sharpe=%f')` prints
in a comment on the next line, and location 1559 rounds both.

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
| 7 | the units on synthetic arrays: a z-score of exactly −1 or 1, exactly 0, NaN, and a long turning short or a short turning long in one day | enters nothing, exits nothing, holds yesterday's units, and turns in one day | `TestBandUnits` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.000000 against the script, 0.0 against the book | reproduced | Chan's figure, on his own file, through his own script transcribed. The book's 17.8 percent is the script's figure rounded, unlike Entry 21's 10.9. |
| 2 | 0.000000 against the script, 0.00 against the book | reproduced | The same as row 1. |
| 3 | none, a claim | reproduced | The APR and the Sharpe ratio are both above the linear rule's on the same spread. The criterion was written on [issue 341](https://github.com/l3a0/quantitative-trading/issues/341) after a first transcription ran, as Entry 21's rows 7 and 8 were, and reads the sentence's comparison on the two figures the book prints. |
| 4 | none | none, not a replication | `bollinger.m` calls `movingStd`, so n − 1 is the transcription. Entry 21's linear rule could not see the divisor, because a constant on every unit cancels out of profit over gross dollars. This rule compares the z-score with a fixed threshold, so the factor changes which days trade, and both figures move. |
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
   divisor its script used, and a transcription reaching for
   `smartMovingStd` would miss.

### What this entry cannot say

Three things.

**Whether the reversion is real.** Entry 21's "What this entry cannot say"
holds unchanged, because this run trades the same spread. GLD and USO do not
cointegrate on this file, and the 20-day hedge ratio changes sign.

**What costs would take.** No script charges any. The band's units change on
162 of the 1,480 days, which `TestTheSpecification` holds, against 1,460 for
the linear rule, which changes its units every day after its first. That
understates how often the band trades, because a held unit's GLD leg is
resized every day as the hedge ratio is refitted.
Nothing here measures what a cost per trade would take from either rule.

**Whether 1, 0 and 20 were fair choices.** Location 1548 calls the entry
threshold a free parameter to be optimized in a training set, and says the
lookback can be one too or can be set to the half-life of mean reversion.
Location 1559 sets the thresholds without saying how they were chosen, and the
lookback is the one Entry 21 records Chan tuned on this sample. Every figure
above is in-sample.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/bollinger-band-lessons.md](../blog/bollinger-band-lessons.md) moves with
it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.bollinger_figures` redraws, and its two
whiteboard sketches, one of a long turning short on 2006-08-11 and one of the
short the run divided by n opens on 2007-05-29, which
`uv run python -m chan.bollinger_whiteboard` redraws through the same
`read_sources` and `example_three_two`.

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
[tests/test_roll_returns.py](../tests/test_roll_returns.py). Seven do not match
one printed figure to one computation, and each says so in its own cells. Row
12 covers two figures from one computation, rows 13 and 14 test claims that
print no statistic, and rows 15 to 18 carry no published figure.

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
are not all one month apart.

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
| 16 | none | none, not a replication | C's month-spaced γ is less than twice its α, and HG's is smaller than its α. [Issue 347](https://github.com/l3a0/quantitative-trading/issues/347) declared only row 14's criterion for this γ, after a scratch run had measured it. Row 13's was added at the build, which is one more reason the row carries no verdict. |
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

Three things.

**Whether returns are constant.** The model is the book's simplification, and
location 2399 already says the fitted γ drifts from day to day. A mean of a
drifting series is a summary, and this entry reproduces the summary without
testing the model.

**Whether the month-spaced γ is what Chan meant.** Row 15 is this repo's
reading of the book's sentence, declared on
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347) before the
build. Row 16 judges it by row 14's criterion, declared there too, and by
row 13's, added at the build. Chan printed no figure for either row, so
neither carries a verdict.

**Whether a roll return persists.** Every row is in-sample on 1986 to 2012.
The two experiments that trade on γ, Example 5.4 and the TU momentum test,
are Entries 34 and 36.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/roll-returns-lessons.md](../blog/roll-returns-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.roll_returns_figures` redraws. Its two whiteboard
sketches draw none of these figures. The one in "The model and the files" is
schematic, and the one in Lesson 2 draws the post's made-up quarterly example,
reading its 0.03 and 0.09 from the two fits run on it.
`uv run python -m chan.roll_returns_whiteboard` redraws them.

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
   from contract to contract and rewritten between saves, read for VX and ES
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
| 7 | rows 3 and 4 with the rule started flat on 2010-07-29 | 0.124916 and 1.415772 | `TestTheDiagnostics::test_starting_flat_on_the_first_test_day_misses` |
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
| 7 | none | none, not a replication | On 2010-07-28 the z-score is −1.041, so the position is already long. Carrying that position into the test is what `VX_ES_rollreturn.m`'s slicing does, and starting flat moves the APR to 12.5 percent. |
| 8 | none | none, not a replication | Trading the printed constant moves nothing that prints, so a run that takes 0.3906 as given, as the roll-return trade does, trades the same portfolio to the book's precision. |
| 9 | none | none, not a replication | The 2012-05-11 and 2012-05-17 saves agree with each other over these days and disagree with the 2012-05-07 save, because the history was rewritten between them. VX's and ES's closes change by neither one constant nor one factor, so how they were rewritten was not measured, as [data/README.md](../data/README.md) records. On either, the specification misses all four figures. |
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
   percent from four holding periods says little about how often the rule
   pays.

### What this entry cannot say

Three things.

**Whether the portfolio is stationary.** The book argues it from a plot,
Figure 5.11, and prints no statistic, and this run takes no test. The z-score
sits outside the band on 236 of the 449 test days against 113 of the 500
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
figure moves too, and `uv run python -m chan.vx_es_figures` redraws it. Its
two whiteboard sketches, one in Lesson 2 and one in Lesson 3, are schematic
and draw none of these figures, and `uv run python -m chan.vx_es_whiteboard`
redraws them.

## Entry 29: GLD, GDX and USO around July 2008, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 1922, with the same story repeated
at 3537 and 3570. No script ships for it. Shipped under
[issue 344](https://github.com/l3a0/quantitative-trading/issues/344). Every
location in this entry is that book's, in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Fifteen rows, all derivable from
[tests/test_gold_miners_oil.py](../tests/test_gold_miners_oil.py).

Chan pairs the gold fund GLD with the gold miners' fund GDX, since a miner's
main asset is gold. He says the pair cointegrated until July 14, 2008, the day
oil peaked near $145 a barrel, and stopped afterwards. His explanation is that
dear oil makes gold dearer to mine, so the miners lag the metal. He tests it
by adding the oil fund USO and finding that the three cointegrate over the
whole span. The book offers this as an example of forming a hypothesis about
why a strategy stopped working and testing it.

**All three claims hold on Chan's own file, on both Johansen statistics, at 99
percent and at 90.** The control the book leaves out comes out the way the oil
explanation needs. GLD and GDX alone over the triplet's days find no relation
even at 90 percent, so the triplet's relation is not one the pair already had.
GDX and USO alone find one relation at 99 percent, which would make the
triplet's relation theirs. A test on the triplet's weights rejects that, so
the two results conflict.

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
   the level the first and third claims name. The second names none.

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
| 15 | Each fund's weight set to zero in the triplet's one relation | none | n/a |

Each row's claim criterion was written on the issue before any statistic was
computed. Rows 1 and 2 hold on one relation or two, rows 3 and 4 on none, and
rows 5 and 6 on exactly one. Row 14 was not on the issue. The pull request's
review added it after the first run, to ask whether the triplet's relation is
one of the other two pairs' own. Row 15 came later still. The post's
pre-publish review added it after every other result here had been seen, to
test row 14's reading on the triplet's weights. The criteria are pinned in
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
| 15 | Johansen's (1991) likelihood-ratio test of β = Hφ on row 9's rank-1 relation, one fund's weight at zero, from the moments of `johansen(·, 0, 1)` with T = 1,479, against chi-squared with one degree of freedom, 2.706, 3.841 and 6.635 at 90, 95 and 99 percent | GLD's weight at zero 10.014660, GDX's 26.336768 and USO's 0.056678 | `TestTheWeightTest::test_row_15_rejects_a_zero_weight_for_gld_and_gdx_and_not_for_uso`, with the GLD figure reached again by maximising the likelihood in `::test_row_15_by_maximising_the_likelihood_directly` |

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
| 14 | none | none, not a replication | GDX and USO alone find one relation at 99 percent. Row 15 rejects the triplet's relation being theirs, so the two results conflict, and this one is the weaker. |
| 15 | none | none, not a replication | Exploratory. GLD's weight at zero is rejected against the asymptotic 99 percent bar, at a p of 0.00155, and USO's cannot be rejected even at 90, at 0.812. Added after every other result was seen, conditional on rank 1, and one of three tests run together. |

### What the entry concludes

Four things.

1. **Every claim holds with room, on both statistics.** The nearest call is
   row 1, whose trace statistic of 22.571 clears its 99 percent bar of 19.935
   by 2.636. Every other claim clears or misses its bar by more,
   `TestEachTestsTable::test_the_closest_call_is_row_1_clearing_its_bar_by_2_636`
   lists each, and the counts at 90 and 95 percent agree with 99 on every
   claim. So the choice of statistic and the choice of level that the book
   left open move no verdict here, which is the opposite of what Entry 23 met.
   The loss holds even at 90 percent, so the stronger reading of "lost" holds
   too. The book's "99 percent probability" is a test level rather than a
   probability. The test rejects no cointegration at the 1 percent level, and
   it says nothing about how likely the pair is to cointegrate.
2. **The control finds nothing, and the triplet's weights decide what a second
   control could not.** GLD and GDX alone over the triplet's 1,481 days give a
   trace statistic of 10.447, short of even the 90 percent bar of 13.429.
   Adding USO raises the first null's trace to 44.838, so the triplet's
   relation is not one the pair already had. Row 14 asks the same of the
   other two pairs. GLD and USO alone find nothing, at 4.350. GDX and USO
   alone find one relation at 99 percent, at 27.166 against 19.935. A rank of
   1 cannot say whether the triplet's relation is that pair's own, so row 15
   tests its weights. If the relation were GDX and USO's, GLD's weight in it
   would be zero. That restriction gives a likelihood-ratio statistic of
   10.015 against a 99 percent bar of 6.635, so it is rejected. GDX's weight
   at zero gives 26.337. USO's gives 0.057, short of even the 90 percent bar
   of 2.706. So gold and the miners carry the relation, and USO's weight in
   it cannot be told from zero. With row 10, that places whatever USO adds to
   the triplet outside the relation's weights, and no row here tests where.
   Rows 14 and 15 cannot both be right. If GDX and USO truly shared a
   relation, a triplet of rank 1 would have to hold that same relation, with
   GLD's weight at zero, and row 15 rejects it. Row 14's is the weaker result,
   since GDX and USO reach full rank at 90 percent while neither is stationary
   alone, which conclusion 3 takes up. Row 15 is exploratory too. The post's
   pre-publish review added it after every other result here had been seen,
   it holds only if the rank is 1, it is one of three weight tests run
   together, and its bars are asymptotic. Two resampling checks run in the
   post's review found those bars rejecting too often on 1,479 observations,
   which no row here pins, so the post and its sketch read the GLD rejection
   at 95 percent rather than 99. The eigenvector's entries are shares per unit
   of the portfolio, so their sizes are not comparable across ETFs at different
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

1. **Anything about oil itself.** Over these years USO held front-month WTI
   futures rather than oil, which location 1939 raises about a different pair.
   A futures fund drifts from the spot price by its roll, so the triplet's
   relation is with the fund, and whether it holds with the spot price is a
   different test.
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

The post also carries two whiteboard sketches, added in the first round of its
review before publishing.

1. **Counting stops at the first miss**, in Lesson 1. It draws how the triplet's
   trace test reaches its count. The first statistic, 44.838, clears its 99
   percent bar of 35.463, and the second, 7.005, falls short of its bar of
   19.935 and even of the 90 percent bar of 13.429, so the count stops at one
   relation and the third statistic, though computed, is never read.
2. **One relation, three pairs**, in Lesson 3. It draws each pair tested alone
   over the triplet's days as an edge of a triangle. GLD and GDX at 10.447 and
   GLD and USO at 4.350 find none, and GDX and USO at 27.166 find one at 99
   percent, so the triplet's count of one cannot say which pair it is. It
   closes on the zero-weight tests, 10.015 for GLD, rejected at 95 percent,
   and 0.057 for USO, not rejected.

A change to those figures moves the sketches too, and
`uv run python -m chan.gold_miners_oil_whiteboard` redraws both through the
same `read_sources` and `gold_miners_oil`.

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
a cross multiplies its rollover when day T + 3 is a weekend or holiday, names
Wednesday as the tripled day for both currencies, and names T + 1 settlement as the exception for USD.CAD.
The script triples CAD on Thursday, which is the USD.CAD rule applied to one
leg of a cross. The run transcribes the script, and no row runs the book's
rule, because choosing between the two after seeing the figures would be a
search.

**What holidays would add.** Location 2273 multiplies the rollover for a
holiday too, but no day in the script does.
Seven weekdays are absent from the file: Christmas Day in 2007, 2008 and 2009,
New Year's Day in 2008, 2009 and 2010, and 2011-12-23, an early close rather than a holiday.
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
moves too, and `uv run python -m chan.aud_cad_rollover_figures` redraws it. So
do the post's two whiteboard sketches, which print the run's figures, and
`uv run python -m chan.aud_cad_rollover_whiteboard` redraws them.

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
will continue. On one shared lookback, one rule buys on exactly the days the
other shorts, so joining them would cancel. Chan gives them different
lookbacks and trades only on the days the two agree. His sentence is that "Sometimes, the combination of
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
   date in its file name, so the 2012-05-07 save is the third below, though
   the first was saved that day.
   1. `inputdataohlcdaily_20120504/`, saved 2012-05-07, the save
      `CL_rev.m` loads, 1,000 rows from 2008-05-19 to 2012-05-04. Rows 1 to
      5 and 10 to 14 read it.
   2. `inputdataohlcdaily_20120511/`, saved 2012-05-12, read over the
      same 1,000 days for row 6. Its closes sit 0.27 higher on every one.
   3. `inputdataohlcdaily_20120507/`, saved 2012-05-09. Its CL closes
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
| 3 to 14 | each rule alone, ComboOR, a later save, the four years before, the positions, and four changes to the specification | none, the book prints no such figures | n/a |

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
| 5 | none | none, not a replication | ComboOR is the combination except on the 10 rows from 2008-07-01 to 2008-07-15, where the 30-day lag exists and the 40-day one does not and OR trades the reversal rule alone. On the 960 rows where both lags exist, no close ties either lag, so a row where both conditions hold is long under both rules, a row where neither holds is short under both, and a row where one holds is flat under both, since OR sums a long and a short. On the first 30 rows neither lag exists, and both are flat. |
| 6 | none | none, not a replication | The 2012-05-11 save, whose file name is dated a week later, still rounds to 12 percent and 1.1 and misses the script's comment at the fourth decimal, so the save is part of the specification at six decimals and not at the book's precision. |
| 7 to 9 | none | none, not a replication | On the four years before the window, momentum alone beats the combination on both figures, and reversal alone loses money. The series there is back-adjusted further from the traded price. It closes at 119.12 on 2004-05-24, against an EIA annual WTI spot average of $41.51 that year, a figure not measured here. So each percentage return divides by a price well above what traded. |
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
   ten early rows, where the 30-day lag exists and the 40-day lag does not
   yet, so it adds no evidence of its own.
3. **The combination does not beat momentum alone on the four years
   before.** From 2004-05-24 to 2008-05-16, momentum alone earns more on both
   figures. The book's "Sometimes" already allows that, so the segment shows
   the advantage is not general rather than contradicting the book. Its
   prices are distorted further by the back-adjustment, so it is evidence
   about the book's sentence rather than a clean backtest.

### What this entry cannot say

Three things.

**Whether the lookbacks were chosen on this window.** The book names 30 and
40 days and nothing about how they were picked. A search over other lookback
lengths would be the many-hypotheses case `CLAUDE.md` puts behind its own
rail. This run tries 30 and 40 days and no other length, and row 11 only
exchanges which rule reads which lookback.

**What costs would take.** The book charges none and this run charges none.
The rule changes position 124 times in 1,000 days, and nothing here measures
what a cost per change would take from 12 percent.

**What the earlier segment would give on traded prices.** Rows 7 to 9 read a
series back-adjusted above the price that traded. Chan's two CL strips start at
the January 2007 contract, which last settles on 2006-12-19, so for most of
those years the contract nearest delivery is not committed. The strip named for
2012-08-13 adds only a spot column, which is not what a futures position earns.
So the earlier segment's figures are what the rule gives on Chan's series, not
what a trader would have earned.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/crude-oil-reversal-momentum-lessons.md](../blog/crude-oil-reversal-momentum-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.cl_reversal_momentum_figures` redraws.
Its three whiteboard sketches move too, and
`uv run python -m chan.cl_reversal_momentum_whiteboard` redraws them. The one
in "The rule and the file" draws the join's first long, on 2008-07-30, and
its first short, on 2008-07-18, from the run. It is schematic: its heights
keep only the order of each day's three closes, and its spacing across does
not follow the days between them. The grid in Lesson 2 prints the 98 rows
where both rules are long, the 59 where both are short and the 803 where they
disagree, from the run. The bars under Lesson 2's "What the swings cost" split
each rule's average day into the daily return it kept, which compounds to its
APR over 252 days, and what the swings took, 0.000022 for the join against
0.000176 and 0.000178 for the rules alone, from the run.

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
| 6 | none | none, not a replication | The script's own plot of `e` starts on row 3, which leaves both rows out. Withholding the signal there moves the APR to 26.1 percent and the Sharpe ratio to 2.3 at the book's precision, so neither of the book's figures survives it. Dropping the two rows from the returns as well gives 0.261059 and 2.351062, and `TestTheFigures::test_dropping_rows_1_and_2_from_the_returns_is_a_different_reading` holds that this row is not that reading. |
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

Three things.

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

**Every figure in the script's closing comment reproduces, on a window the script's active
line does not read, and the Hurst exponent misses.** `TU_mom.m` picks its
window with `idx=find(tday==20090102);` and leaves `% idx=1;` commented out
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
| 11 to 15 | the whole correlation table, the script's active line, the 2012-05-17 save, H at other values of `maxT`, and the statistic Example 1.1 starts from | none here, as each row says | n/a |

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
| 14 | row 3 at `maxT` 24, Entry 22's H on USD.CAD at `maxT` 19 and 24, and both at every `maxT` from 5 to 40 | 0.440450 on TU, and 0.473233 and 0.471426 on USD.CAD. TU lands 0.44 at `maxT` 6, 7 and 21 to 27, and USD.CAD lands 0.49 at none | `TestTheTwoTests::test_max_t_24_lands_tu_and_moves_usdcad_further` and `::test_no_max_t_from_5_to_40_lands_both` |
| 15 | `mean(ret) / std(ret) · √2000` with the n − 1 `std`, on the returns built from the module's exported functions | 2.933253 | `TestTheGaussianStatistic::test_the_exports_give_tu_mom_hypothesis_test_s_2_93` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.00 | reproduced | 0.2719 rounds to the printed 0.27. |
| 2 | +0.00 | reproduced | 0.0238 rounds to the printed 0.02, and the correlation is significant at 5 percent, which is what location 2659 picks the pair for. |
| 3 | −0.01 | did not reproduce | 0.433357 prints as 0.43 on Chan's own saved file, so the vintage explanation is spent. Row 14 holds the diagnostic tried after the miss, every `maxT` from 5 to 40. At `maxT` 24 H prints as 0.44, but the same change moves Entry 22's USD.CAD further from its 0.49. TU also lands at `maxT` 6, 7 and 21 to 27, and each of them moves USD.CAD further from its 0.49. No `maxT` from 5 to 40 lands both, so the miss is not a different default. The claim the figure was printed for survives, since H is below a half here too. |
| 4 | none, a claim | reproduced | h is 0 at `vratiotest`'s default 5 percent, the level the script reads `h` at, so the test does not reject a random walk. |
| 5 | −0.0000 | reproduced | 0.016699 rounds to the printed 0.0167. |
| 6 | +0.00, and +0 against the book | reproduced | 1.041462 rounds to 1.04 and to 1. `chan.khandani_lo.plain_sharpe` divides by n − 1 and gives 1.041201, which `TestTheFigures::test_the_sharpe_ratio_divides_by_n` holds. That also prints as 1.04, so the row uses the script's divisor because it is the script's, not because it lands. |
| 7 | +0.0000, and −0.0 percent against the book | reproduced | 0.016708 rounds to 0.0167 and to 1.7 percent. |
| 8 | −0.000000, and −0.0 percent against the book | reproduced | Exact at the six decimals the script prints, and 2.484746 percent rounds to 2.5. |
| 9 | 0 days | reproduced | Exact. |
| 10 | −0.000000 | reproduced | Exact at the six decimals the script prints. |
| 11 | none | none, not a replication | The book prints one cell. The six compromise pairs all correlate positively, and five of them are significant at 5 percent. The exception is 250/120, at a p-value of 0.0617 on 14 days. |
| 12 | none | none, not a replication | The active line lands none of the comment's six figures, so the comment comes from `idx = 1`. The comment also lists no annual volatility although the printing line asks for one, which suggests it was pasted from an earlier version of that line. |
| 13 | none | none, not a replication | TU's close is the same on every day the two saves share, so only the window moves, four trading days later. That is enough to move the correlation to 0.29 at two decimals and the Kelly f off the printed digits, which places the book's figures on the 2012-05-11 save. |
| 14 | none | none, not a replication | Tried after row 3 missed, as a diagnostic rather than a reading. |
| 15 | none | none, not a replication | `TU_mom_hypothesisTest.m` prints 2.93, which is Example 1.1's figure, replicated as Entry 37's row 1. It is pinned here because it shows that the returns Entry 37 imports are this entry's. |

### What the entry concludes

Three things.

1. **The book's figures come from the full window.** All six figures in
   the script's closing comment reproduce on `idx = 1`, the window the book's
   sentence names, while the line the script runs as shipped starts in 2009
   and lands none of them. The 2012-05-11 save is the one behind them, since
   the 2012-05-17 save that `correlationTest.m` loads moves both the
   correlation and the Kelly f.
2. **`genhurst` misses on both series the book prints an H for.** USD.CAD's
   0.4732 against 0.49 in Entry 22 and TU's 0.4334 against 0.44 here run
   through the same transcription, on Chan's own data, and no `maxT` from 5
   to 40 lands both. No figure of Chan's vouches for the transcription. What checks its
   rules is the invariances `TestGenhurst` checks on synthetic series, and
   the two pins on USD.CAD and TU catch a change without showing it is right.
3. **The momentum the table shows is thin.** The traded pair's correlation
   rests on 69 days, its p-value of 0.0238 is one of 49 tried, and the
   variance ratio test sees a random walk. Location 2646 reconciles the two
   by saying momentum lives at some time frames and not others, which is a
   reading of the same table rather than a test of it.

### What this entry cannot say

Three things.

**Whether 250/25 would be chosen without hindsight.** The pair was picked from
a table of 49 computed on the 2004 to 2012 closes it then trades, so its
p-value is not corrected for the other 48. Example 1.1's three tests of the
same returns, in Entry 37, are where the significance question is asked.

**What computed the book's 0.44.** Row 14 found a `maxT` that lands it on TU
and breaks USD.CAD, and no `maxT` from 5 to 40 lands both. Searching other
settings would be choosing a reading after its number is seen.

**What a trader would earn.** The returns are on the notional value of the
contract with no cost and no margin, and location 2668 says the 1.7
percent may seem low and leverage can boost it. Nothing here measures what costs
or leverage would do.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/tu-momentum-lessons.md](../blog/tu-momentum-lessons.md), this entry's
write-up, moves with it, since that post quotes most of these figures. The
post's one figure moves too, and `uv run python -m chan.tu_momentum_figures`
redraws it.

The post also carries two whiteboard sketches, added in the first round of its
review before publishing.

1. **Future returns end to end, past returns overlap**, in "The correlation table". It draws the
   first three days the 250/25 cell keeps on the 2012-05-11 save, 2005-06-01,
   2005-07-07 and 2005-08-11, each as a 250-day past bar and a 25-day future
   bar to scale. Each future starts where the one before ends, and each past
   shares 225 of its 250 days with the next, which is why keeping every 25th
   day stops the futures overlapping and not the pasts. A row of 69 dots, not
   to scale, counts the kept days.
2. **Same closes, no kept day shared**, in Lesson 1. It draws the first four days
   the cell keeps on each save. The 2012-05-17 save starts four trading days
   later, so each of its kept days falls four trading days after one of the
   earlier save's, and the two sets of 69 share none although all 1,996 shared closes
   are equal. The correlations are 0.2719 and 0.2870, which print as 0.27 and
   0.29.

A change to those figures moves the sketches too, and
`uv run python -m chan.tu_momentum_whiteboard` redraws both through the same
`read_sources`, `read_later_save` and `correlation`.

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
   skipped when its last row would come fewer than 63 rows after its first. The
   spread is reversed where z
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
| 12 | none | none, not a replication | Line 75 marks a contract expired on its last priced row, so the contracts still trading on 2012-08-13 expire on the file's last row. Every pair after 2012-05-08 would be let go 10 rows before its near contract's last priced row, fewer than 63 rows after its first, so none is held. The window's last 66 rows hold nothing and return exactly 0. |

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

**Anything about costs.** None is charged. Each roll trades four contracts,
closing one pair and opening the next. So does each day γ's z-score crosses 0
while a pair is held, because the trade then reverses both legs.

**Whether the direction holds outside 2008 to 2012.** The script's rule
first holds a pair on 2006-09-05, and it also earns 0.050334 on the 332 rows
from then to 2007-12-31, which `TestBeforeAndAcrossTheWindow` pins. That is
the same file and before costs.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/crude-oil-calendar-spread-lessons.md](../blog/crude-oil-calendar-spread-lessons.md)
moves with it, since that post quotes most of these figures and
`TestWhatThePostQuotes` fails until it does. So does its one
figure, which `uv run python -m chan.calendar_spread_reversion_figures`
redraws. Its two whiteboard sketches move too, and
`uv run python -m chan.crude_oil_calendar_spread_whiteboard` redraws them. The
one in "The spread, the signal and the file" draws the script's schedule from
the run. The schedule holds the pair short K2008 and long K2009 from 2007-12-05
to 2008-04-08, skips the M2008, N2008 and Q2008 pairs that would start on
2008-04-09 because each one's last day would come fewer than 63 trading days
after its first, and holds the
pair short U2008 and long U2009 from 2008-04-09 to 2008-08-06. The one in
Lesson 2 is schematic apart from its closing note. That note prints the
fourth conclusion's 841 of 1,097 held rows, and the 554 held rows with γ's
z-score above 0, all of them short the far leg, which
`TestTheTradesDirection` also pins.

## Entry 35: VIX futures calendar spreads on the ratio of back to front, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Chapter 5, Kindle location 2502. Shipped under
[issue 349](https://github.com/l3a0/quantitative-trading/issues/349). No script
ships under the experiment's own name. Example 5.4's
`calendarSpdsMeanReversion.m`, in ericnberwick/EpchanPreview at `e4bc46f`
under `public/img/book2/`, has a commented-out load of this strip just above
its live CL line, so Chan most likely ran that script on VX. Every location in this entry
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
   when its last row would come fewer than 63 rows after its first. The return
   is yesterday's positions times each leg's return, summed over the legs that
   have one and divided by 2, annualised over 252 days by compounding simple
   returns, with the Sharpe ratio on MATLAB's n − 1 `std`, no risk-free rate and
   no cost.

Four rows beside S were declared with it, and a row that lands while S misses
is reported and not promoted to the specification.

1. **B1** trades the held pair's ratio, the far contract over the near one
   for the pair the schedule holds that day, filled forward across the days
   nothing is held. The script's own comment calls those two the back and the
   front.
2. **B2** sets `holddays=0`, so each pair is held from the day after the
   previous pair's last day to 10 rows before its own expiry. The first pair
   is never held, because its window is one row, and the six pairs after
   VX-2012K's, whose near contract also still trades on the file's last row,
   are skipped, because VX-2012K's pair already ends on 2012-04-23, the row
   where each of theirs would end. VX holds 64 of its 71 pairs.
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

Three things.

1. **The specification fits the book's first claim and not its trade.** The
   ratio's ADF statistic of −5.568107 clears the 1 percent value by 2.109807.
   Trading it as the book's text describes, with the script's minimum holding
   period of 63 days, gives an APR of −4.045401 percent and a Sharpe ratio of −0.563912.
2. **B3 is the row that matches the book, and it was found by a search.**
   Two things single it out from the other four rows.
   1. On the book's window it rounds to both printed figures, 0.176952 and
      1.475658.
   2. It is the only row that does worse before October 2008, as the book's
      third claim says.

   Its last held day, the book's printed end date of 2012-04-23, does not
   single it out, because B2 ends there too. VX-2012K still trades on the
   file's last row, 2012-05-07, so the schedule reads that row as its expiry,
   and under `holddays=0` its pair ends 10 rows earlier, on 2012-04-23. The
   date is evidence for `holddays=0`, which holds each pair in turn and which
   B2 and B3 share.

   B3 was picked out after the run among five rows, and the window the first
   point reads was chosen after seeing the table, so this is a search. A
   registered test of B3 on VX data after 2012-05-07 is what would confirm it.
3. **The specification's signal mostly reads a pair it does not hold.** Each
   pair is held for at least 63 rows and let go 10 rows before its near
   contract's last priced row, and VX expires monthly, so S's near leg is the front
   contract on 126 of its 847 held rows from 2008-10-27, and the second to the
   fifth on the rest. Under `holddays=0` it is the front on 459 of 879 and the
   second on the other 420. B1 and B3, which read the held pair's own ratio,
   are the two of the four rows running to the file's last day that earn. Four
   rows show a pattern rather than a cause, and B2 cuts against reading it as
   one: its signal reads the pair it holds on 459 of 879 days against S's 126
   of 847, and it loses more than S. `TestWhichPairTheSignalReads` pins all
   three, and the write-up found this.

### What this entry cannot say

Four things.

**Which rule Chan ran.** No script ships under the experiment's own name. The
commented load line says which script he most likely ran on VX. The book's text at
location 2502 gives four things.

1. VX as the instrument.
2. The ratio of back to front as the signal.
3. The 15-day lookback.
4. The window, from October 27, 2008, to April 23, 2012.

The rest of S is this repo's reading, in three choices.

1. `spreadMonth=1`, forced by how few contracts the strip prices on a day.
2. The nearest two priced contracts as the back and the front, rather than the
   held pair B1 reads, with no signal where the two are not adjacent columns.
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
pins both counts. Each new pair's near leg is the old pair's far one, so a
roll trades two contracts when that leg keeps its side and four when it
switches, on 26 and 16 of the 42 rolls. B3 also reverses both legs on 109
days between rolls, each a day its z-score crosses 0, which is 436 of the 554
contracts it trades from 2008-10-27.
`TestTheSignalsOnVx::test_from_2008_10_27_b3s_rolls_trade_two_or_four_and_its_reversals_most`
pins those counts.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/vx-calendar-spread-lessons.md](../blog/vx-calendar-spread-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.vx_calendar_spread_figures` redraws, and
[blog/crude-oil-calendar-spread-lessons.md](../blog/crude-oil-calendar-spread-lessons.md),
which quotes the 126 of 847. The post's two whiteboard sketches move too, and
`uv run python -m chan.vx_calendar_spread_whiteboard` redraws them. Neither is
schematic. The one in Lesson 2 draws S's hold of the pair near VX-2009K and far
VX-2009M from 2009-02-04 to 2009-05-06, 64 days. Its near leg is the 4th, 3rd
and 2nd priced contract for 10, 20 and 19 of those days and the front one for
the last 15, the only stretch on which the front pair the signal reads is the
pair held. The one in Lesson 4 draws the script as shipped on 2010-01-04,
when the near leg VX-2010J has a price and the far leg VX-2011J has none, and
closes on the 1,183 of 1,284 held days with the near leg alone.

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

Three things.

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
results, and they show that a normal draw gives nearly the same count, 1,165
against 1,221, while removing the drift removes almost all of it.

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
| 6 | none | none, not a replication | 277 lies inside the script's 243 to 307. Nothing in the script applies the observed positions to simulated returns, and the public copy holds the file in one commit, so nothing shows how the comment was made. |
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

Three things.

**Which Pearson type `pearsrnd` drew from.** The type IV choice is inferred
from the standard criterion rather than read from MathWorks' code. If
`pearsrnd` drew from another type with the same four moments, row 2 judges a
different null. Rows 7 and 8 suggest the count barely depends on the shape,
which limits what a different type could move.

**What computed the script's 0.027500.** Row 6 lands it with a test the
script does not contain, and the public copy holds the file in one commit,
with no earlier version to read.

**Whether drift explains momentum's significance elsewhere.** Rows 6 to 8
were chosen after a scratch run on other seeds had seen results, on one
strategy and one future. A registered test would declare the drift reading
first and run it on data this entry never loaded.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/tu-hypothesis-tests-lessons.md](../blog/tu-hypothesis-tests-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.tu_hypothesis_tests_figures` redraws.

The post also carries two whiteboard sketches, added in the first round of its
review before publishing.

1. **The shuffled trades land in the wrong place**, in Lesson 4. It draws row
   5's loop as boxes. The shuffled trades go into `pos`, the real positions,
   and never reach `pos_sim`, which starts as zeros. So `ret_sim` is built
   from a `pos_sim` of 0, and every simulated mean is 0 against the observed
   mean of 6.626644e-05. It closes on the 10 draws run as written, each
   returning 0.
2. **Drift makes the rule mostly long**, in Lesson 5. It draws a noisy line
   with TU's drift above one with the same noise and none. Under each sit ten
   250-day brackets, each ending in an arrow up where the rule is long and
   down where it is short. It prints the share of days with a long or short
   signal on which the rule is long, averaged over the first 1,000 of row 2's
   series, 0.804654 as drawn and 0.502401 with the mean removed. Its two lines
   are schematic random walks with TU's daily standard deviation, the upper
   one with TU's daily mean as well, not TU's closes and not row 2's series.

A change to those figures moves the sketches too, and
`uv run python -m chan.tu_hypothesis_tests_whiteboard` redraws both through
the same `read_sources`, `pearson_iv_draws` and `randomized_trades_as_written`.

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
profit from it. GLD owns physical gold, which makes it the long leg. Location 2718
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
| 10 | GC against the GC close of `inputdataohlcdaily_20120507/gc.csv`, chan-mat, adjusted, saved 2012-05-09, a continuous series, on the 752 kept days, and the lag-1 autocorrelation of the daily change in this GC less that one | equal on 0 of 752, the nearest 9.30 apart, daily return correlation 0.824035, autocorrelation −0.559953 | `TestTheSeriesIdentity::test_the_ohlc_save_s_gc_never_equals_it`, `::test_their_daily_returns_correlate_at_0_82` and `::test_their_difference_reverses_the_next_day` |
| 11 | the daily change in log(GC / GLD) over the 752 kept days, for each GC series: its standard deviation over n, its largest move, and its moves past 2 percent. Then GLD's daily log return over the same days, its standard deviation over n, and half the squared ratio of this GC's figure to it, the most of GLD's daily variance a gap between the two closes can carry if nothing else that moves the ratio cancels the gap's moves | 0.000933, 0.007082 and none on this GC. 0.009243, 0.097332 and 20 on the OHLC save's. GLD's 0.015660, so at most 0.001775 | `TestTheSeriesIdentity::test_the_log_ratio_moves_little_on_the_16_00_series`, `::test_the_log_ratio_moves_ten_times_as_much_on_the_ohlc_save` and `::test_a_gap_between_the_closes_carries_at_most_0_18_percent_of_gld_s_variance` |

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
| 9 | none | none, not a replication | The exchange sets no settlement price on a US exchange holiday, so a settlement series has no row on one, and this series has 9 such rows. So it is not the 1:30 p.m. settlement location 2730 describes. |
| 10 | none | none, not a replication | The two are different continuous series, and nothing here tests how either crosses a roll. Two series that cross rolls differently differ by an amount that changes at each roll, so they need not be equal at any hour, and never equalling this one says nothing about when this one is read. The daily change in their difference reverses the next day, at an autocorrelation of −0.559953. A gap in timing predicts that, because one day's move between the two hours enters that day's change and comes back out of the next. A step at a roll that one series takes and the other does not stays, so it predicts no reversal. |
| 11 | none | none, not a replication | This row says when the series is read. If GC were read at 1:30 p.m. and GLD at 4:00 p.m., the daily change in log(GC / GLD) would hold two gold returns over those two and a half hours, one from each day. If anything else that moves the ratio only adds to it, which nothing here tests, its standard deviation of 0.000933 against GLD's 0.015660 leaves room for at most 0.001775 of GLD's daily variance in that gap. Two and a half hours is about a tenth of a day on the clock, in a market that trades nearly around it, so the gap is not there. The OHLC save's GC moves against GLD about ten times as much, and row 10's reversal points away from steps at rolls, to a price recorded at another hour or to errors in the recorded prices, which nothing here tells apart. |

### What the entry concludes

Five things. The last two were measured by the write-up after the run, and
`TestWhatThePostMeasured` in [tests/test_gld_gc.py](../tests/test_gld_gc.py)
pins them.

1. **Chan's saves reproduce every figure his script and his text print.** All five figures of the
   closing comment and both of the text's land on the printed digits.
2. **The series the script reads is GC read within minutes of GLD's 4:00
   p.m. close, not the 1:30 p.m. settlement.** Row 11 is the evidence for the
   hour. If nothing else that moves the ratio cancels the gap's moves, a gap
   of two and a half hours between the two closes could carry at most
   0.001775 of GLD's daily variance, far below the tenth of a day those hours
   take. Row 9 adds that the series is not a settlement series, because
   it has rows on 9 US exchange holidays, days the exchange sets no
   settlement price. Location 2730 warns that GC
   settles two and a half hours before GLD closes. That gap is not in the
   series the script reads, so the asynchronicity the book excuses is not in
   the backtest.
3. **The bill rate leaves about half the return standing.** Over the window
   it averages 1.0141 percent against a return of 1.9014 percent. The book's
   "close to zero" needs GLD's financing to sit about 0.89 percentage points
   a year above the bill rate. Whether its holders paid that is not
   something this repo holds data on.
4. **The 0.8 percent and the 91 days are two drawdowns.** The deepest runs
   from a high on 2007-10-12 to a trough on 2007-11-12 and is recovered on
   2007-11-14. Most of it is 2007-11-12 alone, when the trade lost 0.6771
   percent as GLD fell 4.7213 percent and GC 4.0442 percent. That day is also
   the 16:00 series' largest move in log(GC / GLD), the 0.007082 of row 11.
   The 91 days run from 2009-08-28 to 2010-01-08 and reach only −0.40907
   percent. Measured after the run.
5. **The return fell with the bill rate, year by year.** S's average annual
   return against the bill rate over the same months, leaving out the zeroed
   first row, is 0.052235 against 0.036520 over August to December 2007,
   0.027315 against 0.013650 in 2008, 0.005822 against 0.001500 in 2009, and
   0.004458 against 0.001350 over January to August 2010. The margin shrinks
   from 1.57 percentage points to 0.31, and the bill rate sat below 0.5
   percent in 22 of the 37 months, from 2008-11. The split by year was chosen
   after the run, so it is exploratory and carries no verdict. The cost of
   carry is the usual explanation, and nothing here tests it.

### What this entry cannot say

Four things.

**What financing GLD actually cost.** The bill rate is a floor. A broker's
rate on a long ETF position sits above it by a spread this repo has no data
for, so row 8 bounds the excess return from above and cannot say whether it
is close to zero.

**Whether the trade would work on the 1:30 p.m. settlement.** The OHLC save's
GC has the calendar a settlement series would have, GLD's days in the window
and none of the 9 holidays, but nothing here measures the hour it is
recorded or what it does at each roll. What it does at a roll decides how
much of the roll return shows up in its returns, so a run of the trade on it
would need its own analysis. The issue puts it out of scope.

**Whether the trade works after 2010.** The window is the book's, and nothing
here reads later data.

**Gold's roll return over 1982 to 2004.** Location 2718 cites "a negative roll
return of −4.9 percent annualized from December 1982 to May 2004" as the
reason to try the trade. The entry cites it and does not reproduce it, because
the earliest gold futures series here starts in May 2004, the month that span
ends.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/gld-gc-lessons.md](../blog/gld-gc-lessons.md) moves with it, since that
post quotes most of these figures. So does its one figure, which
`uv run python -m chan.gld_gc_figures` redraws. Of its two whiteboard
sketches, the one in "Why own the metal and short the future" is schematic
and draws none of these figures. The one in Lesson 4 is schematic apart from
its last line, which reads row 11's bound of 0.001775 from the run.
`uv run python -m chan.gld_gc_whiteboard` redraws them.

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

Three things.

1. **The script's rule reproduces on Chan's own files.** Every figure its
   comment prints lands at the decimals printed, and the book's two land at
   the precision Chan printed them.
2. **The book's text and the script describe one run.** The text gives no
   rule for deciding contango beyond location 2718's definition, so the rule
   here is the script's, and its APR and Sharpe ratio are the text's
   16 percent and "about 1".
3. **The backwardation days earn a third of the return.** Split by the view
   held the day before, the trade earns on contango on 1,128 days and on
   backwardation on 244. Their daily returns sum to 0.638420 and 0.308117 of
   0.946538, and compound to 0.790269 and 0.343539. On the contango days USO
   fell 0.567754 and the ratio implies a roll return of −0.766081 in log
   terms, against USO's log move of −0.8388. On the backwardation days USO
   rose 0.702850, or 0.5323 in log terms, and XLE fell 0.097061, while the
   ratio implies 0.072380 in log terms, reading 12 · ln(front / back) as
   contracts a month apart. Holding
   contango's position on every day the trade holds anything gives an APR of
   0.044949 and a Sharpe ratio of 0.364524. `TestWhatThePostMeasures` pins
   all of it, and the write-up found it. The split comes from the rule's own
   two views rather than a date picked after the curve was seen, and it
   describes this sample without testing anything.

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
2006-10-20. The figures count those days as earning 0, as the script does.
Measured from 2006-10-20 instead, the APR is 0.174513 and the Sharpe ratio
1.092618, and both drawdown figures are unchanged, which
`TestWhatThePostMeasures::test_from_the_first_ratio_the_apr_and_sharpe_rise_and_the_drawdown_holds`
pins. The book prints nothing for that span, so neither figure gets a
verdict.

**Which standard deviation the Sharpe ratio divides by.** The run divides by
n, as `chan.matlab_helpers.smartstd_book_two` does. Dividing by n − 1 gives
1.046247, which also rounds to the script's 1.05, so this script's printout
cannot tell the two apart.

**Whether the trade works out of sample.** The rule and the window are
Chan's, and the sample is the one he reported on. A registered test would fix
the rule first and run it on data after 2012.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/xle-uso-roll-return-lessons.md](../blog/xle-uso-roll-return-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.xle_uso_roll_return_figures` redraws.

## Entry 40: the opening gap strategy on STOXX Europe 50 futures, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 7.1, Kindle locations 2965 to 2971, with
location 3509 quoting the same figures. Shipped under
[issue 358](https://github.com/l3a0/quantitative-trading/issues/358). The
script is `gapFutures_FSTX.m`, in ericnberwick/EpchanPreview at `e4bc46f`
under `public/img/book2/`, git blob `02db940`, and the line numbers below are
that blob's. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Sixteen rows, all derivable from
[tests/test_opening_gap.py](../tests/test_opening_gap.py).
[tests/test_continuous_futures.py](../tests/test_continuous_futures.py)
derives two of their figures as well, for the close alone. Row 8's 45
agreeing days of 1,996 come from
`tests/test_continuous_futures.py::TestWhatMovesBetweenSaves::test_the_symbols_rolled_in_between_take_many_differences`,
and row 9's equal closes from
`tests/test_continuous_futures.py::TestWhatMovesBetweenSaves::test_and_hold_still_across_the_other_pair`.
Rows 1, 2 and 4 each match one printed figure to one computation, and rows 10
and 11 each match two figures Chan's Python port prints to the port's rule.
The other eleven say what they do in their own cells. Row 3 checks one
printed figure against two computations, because location 3509 calls its
figure of around 13 percent an "annualized average return" and the script
prints a compounded one. Row 5 checks the book's two figures against a second
reading of the script. Rows 6 to 9 and 12 to 15 carry no published figure,
and row 16 carries a record of the port's comment rather than a figure of its
own.

A stop order rests until the price reaches it, so a market that opens far
outside the previous day's range can set off many at once and carry the move
through the day. Chapter 7 names that as one cause of short-term momentum.
Location 2965 calls Example 7.1 "the opposite momentum strategy" to Example
4.1's buy on gap, "buying when the instrument gaps up, and shorting when it
gaps down". It reports that on FSTX, the STOXX Europe 50 index future on
Eurex, which the book calls the Dow Jones STOXX 50, the rule "generates an
annual percentage rate (APR) of 13 percent and a Sharpe ratio of 1.4 from
July 16, 2004, to May 17, 2012". The script goes
long when the open clears the previous high by a tenth of the 90-day standard
deviation of daily returns, short when it clears the previous low by the same
margin, and holds the position from the open to the close.

**The script's figures reproduce, and they come from fading the jump rather
than following it.** Line 23 earns `positions .* (op - cl) ./ op`, so a long
profits when the price falls from the open. As written it gives the comment's
0.1327 and 1.44, and the book's 13 percent and 1.4. With the sign that location
2965 describes, the same positions earn the same returns negated, an APR of
−0.124236 and a Sharpe ratio of −1.441620.

**A scratch run came before the criterion.** The order was not the one this
repo asks for. The plan on
[issue 358](https://github.com/l3a0/quantitative-trading/issues/358) ran both
readings of line 23 and saw every figure before it wrote down what a landing
figure is and what row 5 asks. The criterion it then fixed is the rule every
earlier entry uses: a figure lands when the computed value rounds to the
printed string at the decimals the string carries, which is
`chan.khandani_lo_book_two.matches`. Line 23 can take only two signs, and
both are pinned, so nothing in the criterion was chosen to fit the run.

Every row reads one vintage and one specification unless it names another,
so both are stated once here.

1. **The vintage.** `data/inputdataohlcdaily_20120517/fstx.csv`, vendor
   `chan-mat`, basis `adjusted`, saved 2012-05-18, FSTX's column of Chan's
   `inputDataOHLCDaily_20120517.mat`. Each of its open, high, low and close
   holds 2,000 days from 2004-07-16 to 2012-05-17, the book's window exactly,
   read through `chan.series.load_panel` with the column's NaN dropped. The
   scale-break guard runs on its closes over that span and refuses nothing.
2. **The specification.** `gapFutures_FSTX.m` as `chan.opening_gap`
   transcribes it. The spread is
   `backshift(1, smartMovingStd(calculateReturns(cl, 1), 90))`, with book
   two's `smartstd` dividing by n, so the first 90 rows carry none. A day is
   long when `op >= backshift(1, hi) · (1 + 0.1 · spread)` and short when
   `op <= backshift(1, lo) · (1 − 0.1 · spread)`. Both tests are non-strict,
   and line 21 assigns the short after the long. The literal reading is line
   23 as written, `positions · (op − cl) / op`. The momentum reading changes
   that line alone, to `positions · (cl − op) / op`. Line 24 sets NaN to 0 in
   both. The APR is `prod(1 + ret)^(252 / 2000) − 1` and the Sharpe ratio
   `mean(ret) · √252 / std(ret)` with MATLAB's n − 1 `std`, with no risk-free
   rate and no cost.

**Rows 10 to 16 read a second specification, Chan's Python port.**
`gapFutures_FSTX.py` is a member of `PythonCodesAndData.zip` at the same
commit, the zip [data/README.md](../data/README.md) records with its sha256.
The member is 996 bytes, with sha256
`8b005cee1114fd019ca761c1df7331d5f66ba9a3be8d6dcb2e614b6615a095fc`, dated
2018-12-23 in the zip's central directory. It reads
`inputDataDaily_FSTX_20120517.csv`, whose open, high, low and close equal
the committed file's, as [data/README.md](../data/README.md) records. The zip
is not committed, and `chan.opening_gap.python_port` carries the port's
arithmetic. Against the script, line by line:

| Script line | `gapFutures_FSTX.m` | `gapFutures_FSTX.py` | What differs |
| --- | --- | --- | --- |
| 3 | `entryZscore=0.1;` | `entryZscore=0.1;`, the port's line 7 | The same threshold, a tenth of the spread. |
| 13 | `stdretC2C90d=backshift(1, smartMovingStd(calculateReturns(cl, 1), 90));` | `stdretC2C90d=df['Close'].pct_change().rolling(90).std().shift()` | The port divides by n − 1 rather than n. Pandas also wants all 90 returns in the window, so the port's first spread falls on 2004-11-22, one row after the script's 2004-11-19. |
| 15 | `longs= op >= backshift(1, hi).*(1+entryZscore*stdretC2C90d);` | `longs= df['Open'] >= df['High'].shift()*(1+entryZscore*stdretC2C90d)` | The same test. |
| 16 | `shorts=op <= backshift(1, lo).*(1-entryZscore*stdretC2C90d);` | `shorts=df['Open'] >= df['Low'].shift()*(1-entryZscore*stdretC2C90d)` | The port flips `<=` to `>=`, so a short qualifies on every day the open does not jump below the previous low by the margin. |
| 18 to 21 | `positions(longs)=1;` then `positions(shorts)=-1;` | `positions[longs]=1` then `positions[shorts]=-1` | The same order, the short after the long. An open that clears the previous high also clears the previous low, so every long day passes the port's short test too, and the port's line 22 makes it short. The port never holds a long position. |
| 23 | `ret=positions.*(op-cl)./op;` | `ret=positions*(df['Close']-df['Open'])/df['Open']` | The port takes the momentum sign, the one that location 2965 describes. |
| 24 | `ret(isnan(ret))=0;` | none | No return is NaN on this file, so the missing line moves nothing. |
| 26 | `prod(1+ret).^(252/length(ret))-1` and `mean(ret)*sqrt(252)/std(ret)` | `np.prod(1+ret)**(252/len(ret))-1` and `np.sqrt(252)*np.mean(ret)/np.std(ret)` | The APR is the same. `np.std` on a series divides by n, where MATLAB's `std` divides by n − 1. |
| 33 | `calculateMaxDD(cumret)` | `calculateMaxDD(cumret.fillna(0))` | The port's `calculateMaxDD` is the script's loop. Under pandas 3 the port stops here, because the loop indexes the date-indexed `cumret` by position, so it no longer runs as shipped. |

Every result here is **exploratory**. Reproducing Chan's figure spends his
2004 to 2012 sample on his rule, and no rule here, neither reading of the
script nor the port's, is evidence that an opening jump pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The APR, script | 0.1327 | script line 27, the comment recording what line 26 printed |
| 2 | The Sharpe ratio, script | 1.44 | the same comment |
| 3 | The APR, book | 13 percent at location 2965, and around 13 percent at location 3509, which calls it an "annualized average return" | locations 2965 and 3509 |
| 4 | The Sharpe ratio, book | 1.4 | locations 2965 and 3509 |
| 5 | The rule that buys an upward jump and shorts a downward one earns rows 3 and 4 | a claim | location 2965 |
| 6 to 9 | The drawdowns, the days each side holds, and the rule on two earlier saves | none, as each row says | n/a |
| 10 | The APR and the Sharpe ratio, Python port | 0.074864 and 0.494857 | the port's comment `#APR=0.074864 Sharpe=0.494857`, not the book |
| 11 | The maximum drawdown and its days, Python port | −0.233629 and 789 | the port's comment `#Max DD=-0.233629 Max DDD in days=789` |
| 12 to 15 | The days the port holds each side, and three variants that each change one difference between the two programs | none, as each row says | n/a |
| 16 | The port's APR and Sharpe ratio as the Algorithmic Trading Experiments page records them | none of its own, the page records 7.5 percent and 0.49 | the Experiments page, a claude.ai artifact the body of [issue 358](https://github.com/l3a0/quantitative-trading/issues/358) cites |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + ret)^(252 / 2000) − 1`, literal reading | 0.132733 | `TestTheSpecification::test_the_apr` |
| 2 | `mean(ret) · √252 / std(ret)`, literal reading | 1.441620 | `TestTheSpecification::test_the_sharpe_ratio` |
| 3 | Row 1 in percent, and `252 · mean(ret)` in percent | 13.2733 and 12.8622 percent | `TestTheSpecification::test_both_reproduce_the_book_s_figures` and `::test_252_times_the_mean_also_rounds_to_13_percent` |
| 4 | Row 2 | 1.441620 | `TestTheSpecification::test_both_reproduce_the_book_s_figures` |
| 5 | The APR and the Sharpe ratio under the momentum reading | −0.124236 and −1.441620 | `TestTheClaim::test_the_momentum_reading_s_figures` and `::test_neither_lands_the_book` |
| 6 | `calculateMaxDD(cumprod(1 + ret) − 1)` under each reading | literal −0.190023 over 287 days, momentum −0.651056 over 1,909 days | `TestBesideTheReplication::test_the_literal_reading_s_drawdown` and `::test_the_momentum_reading_s_drawdown` |
| 7 | The days each test qualifies, and the first day holding a position | long on 278, short on 191, both on 0, flat on 1,531, first position 2004-11-22 | `TestBesideTheReplication::test_the_days_each_side_qualifies` and `::test_the_first_position_is_on_2004_11_22` |
| 8 | The literal reading on `inputdataohlcdaily_20120511/fstx.csv`, chan-mat, adjusted, saved 2012-05-12, 2,000 days from 2004-07-12 to 2012-05-11 | APR 0.131543, Sharpe ratio 1.448082 | `TestTheEarlierSaves::test_each_misses_the_script_s_apr`, and for the 45 days of 1,996 on which each of the four fields agrees, `tests/test_continuous_futures.py::TestWhatMovesBetweenSaves::test_the_symbols_rolled_in_between_take_many_differences` for the close and `TestWhatThePostMeasures::test_the_2012_05_17_save_restates_every_field` for all four |
| 9 | The literal reading on `inputdataohlcdaily_20120507/fstx.csv`, chan-mat, adjusted, saved 2012-05-09, 2,000 days from 2004-07-07 to 2012-05-08 | APR 0.133561, Sharpe ratio 1.466345 | the same test, for the equal closes `tests/test_continuous_futures.py::TestWhatMovesBetweenSaves::test_and_hold_still_across_the_other_pair`, and for all four fields `TestWhatThePostMeasures::test_the_two_earlier_saves_price_all_four_fields_alike` |
| 10 | The port's rule, its `prod(1 + ret)^(252 / 2000) − 1`, and its `mean(ret) · √252 / std(ret)` with `np.std` dividing by n | APR 0.0748641057, Sharpe ratio 0.4948573171, and 0.4947335873 dividing by n − 1 | `TestChansPythonPort::test_row_10_the_apr_and_the_sharpe_ratio_over_n_reproduce_the_comment` and `::test_row_10_over_n_minus_1_the_sharpe_ratio_misses_the_comment` |
| 11 | `calculateMaxDD(cumprod(1 + ret) − 1)` on the port's returns | −0.2336291171 over 789 days | `TestChansPythonPort::test_row_11_the_drawdown_and_its_days_reproduce_the_comment` |
| 12 | The days the port holds each side, and the first day its spread is set | long on 0, short on 1,718, flat on 282, both tests passed on 278, first spread 2004-11-22 | `TestChansPythonPort::test_row_12_the_port_is_never_long` and `::test_the_port_s_spread_starts_on_2004_11_22_a_row_after_the_script_s` |
| 13 | The port's short test and sign on the script's spread, Sharpe ratio dividing by n − 1 | APR 0.076926, Sharpe ratio 0.505364 | `TestChansPythonPort::test_each_variant_changes_one_difference` and `::test_the_two_spreads_qualify_the_same_days_but_one` |
| 14 | The script's short test and sign on the port's spread, Sharpe ratio dividing by n − 1 | APR 0.132733, Sharpe ratio 1.441620, row 1's and row 2's returns day for day | `TestChansPythonPort::test_each_variant_changes_one_difference` and `::test_row_14_is_the_script_s_literal_reading_day_for_day` |
| 15 | The port's spread and short test with the script's sign, Sharpe ratio dividing by n − 1 | APR −0.098670, Sharpe ratio −0.494734, the port's returns negated | `TestChansPythonPort::test_each_variant_changes_one_difference` and `::test_row_15_is_the_port_s_returns_negated` |
| 16 | Row 10's APR in percent and its Sharpe ratio dividing by n, at the page's precision | 7.48641057 percent and 0.4948573171, which round to 7.5 percent and 0.49 | `TestChansPythonPort::test_row_16_the_experiments_page_rounds_the_comment` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.0000 | reproduced | 0.132733 rounds to the script's 0.1327. |
| 2 | +0.00 | reproduced | 1.441620 rounds to the script's 1.44. |
| 3 | +0 percent on the compounded APR, −0 percent on the arithmetic one | reproduced | The compounded APR and the arithmetic one both round to 13 percent, so the text's figure does not have to be assigned to one of them. |
| 4 | +0.0 | reproduced | 1.441620 rounds to the book's 1.4. Rows 1 to 4 say the number lands on the script as shipped, and row 5 asks whether the claim behind it survives. |
| 5 | −25 percent on the APR, −2.8 on the Sharpe ratio | did not reproduce | The rule that location 2965 describes loses on Chan's own file under his own script, so the vintage explanation is spent. Its daily returns are the literal reading's negated, so the figures the text prints belong to the literal sign alone. |
| 6 | none | none, not a replication | Line 34 prints a drawdown, and no comment records a value for it. |
| 7 | none | none, not a replication | No day qualifies both tests, so line 21's order decides nothing here. No open sits exactly on either threshold, so the tests being non-strict decides nothing either. `TestTheRules` holds both on synthetic days. |
| 8 | none | none, not a replication | FSTX's open, high, low and close in this save each agree with the 2012-05-17 save's on 45 of the 1,996 days they share, as [data/README.md](../data/README.md) records for the close, and the window starts and ends four trading days earlier. Its APR rounds to 0.1315 rather than 0.1327, so the save is part of the specification. |
| 9 | none | none, not a replication | FSTX's open, high, low and close in this save each equal the 2012-05-11 save's on all 1,997 days they share, over a window that starts three trading days earlier still, so the two APRs differ by the window alone. Its APR rounds to 0.1336. Both earlier saves still round to the book's 13 percent. |
| 10 | +0.000000 on the APR, +0.000000 on the Sharpe ratio | reproduced | Both land on the comment at its six decimals, on the file the port reads, with the Sharpe ratio dividing by n as `np.std` does. Dividing by n − 1 gives 0.4947335873, which misses by −0.000123, so the divisor is part of the port's specification. That n − 1 figure is the 0.494734 that [issue 505](https://github.com/l3a0/quantitative-trading/issues/505) recorded from a scratch run guessing at the port's rule before the port was read. |
| 11 | −0.000000 on the drawdown, 0 on its days | reproduced | The port's comment comes from the rule its text states, on Chan's own file. |
| 12 | none | none, not a replication | Every one of the 278 days passing the long test also passes the port's short test, and the port assigns the short after the long, so it never holds a long position. It sells the open and buys the close on the 1,718 days the open does not jump below the previous low by the margin. |
| 13 | none | none, not a replication | The two spreads qualify the same days except 2004-11-19, the one row where the script's spread is set and the port's is not. Under the port's short test that day is short, and it alone moves the APR from row 10's to 0.076926. The divisor decides no day of this file. |
| 14 | none | none, not a replication | Under the script's tests 2004-11-19 qualifies nothing on either spread, so the port's spread leaves the script's figures where rows 1 and 2 put them. |
| 15 | none | none, not a replication | Changing the sign alone negates every one of the port's returns, so the Sharpe ratio dividing by n − 1 is row 10's negated. The APR is not, because it compounds. |
| 16 | none | none, not a replication | The page recorded what the port prints rather than publishing a figure of its own. Row 10's figures round to its 7.5 percent and 0.49. |

### What the entry concludes

Four things.

1. **The script reproduces on Chan's own file, and the figure is the fade's.**
   Its two printed figures land at the decimals printed, and the book's two
   land at the precision Chan printed them. The return line that earns them
   sells an upward jump during the day and buys a downward one.
2. **The text's momentum rule loses what the fade earns.** Under the sign
   that location 2965 describes, the same positions give an APR of −0.124236 and a
   Sharpe ratio of −1.441620. The 13 percent and 1.4 do not support the claim
   they were printed beside.
3. **Chan's Python port prints what its own rule computes, and that rule is
   neither reading of the script.** Its four printed figures land on the
   committed file. It takes the momentum sign the text describes, and it
   flips the script's short test, so it never holds a long position and sells
   the open on 1,718 of 2,000 days. Its APR and Sharpe ratio, which the
   Experiments page records as 7.5 percent and 0.49, therefore say nothing
   about the rule that location 2965 describes. Yet it is short on all 278
   upward jumps, where short under its sign earns what the script's long
   earns under the literal sign, so its returns there are the script's day
   for day and sum to 0.749529. Its other 1,440 short days sum to −0.050957,
   so its gain also comes from selling the upward jump.
   `TestWhatThePostMeasures::test_the_port_earns_the_script_s_long_returns_on_every_upward_jump`
   pins it, and the write-up found it.
4. **The long days earn about three quarters of the return.** Split by the side
   held, the literal reading's daily returns sum to 0.749529 on the 278 long
   days and 0.271280 on the 191 short days, of 1.020809, and compound to
   1.084422 and 0.290022. Each side alone, earning nothing on the other's
   days, gives an APR of 0.096964 and a Sharpe ratio of 1.534735 for the long
   days, and 0.032607 and 0.527473 for the short days. From the open to the
   close, FSTX moved −0.002696 on average on the long days, closing below the
   open on 163, and +0.001420 on the short days, closing above it on 108. On
   the 1,441 flat days after the first 90 it moved +0.000025.
   `TestWhatThePostMeasures` pins all of it, and the write-up found it. The
   split comes from the rule's own two branches rather than a date picked
   after the curve was seen, and it describes this sample without testing
   anything.

### What this entry cannot say

Three things.

**Whether the rule works on GBPUSD.** Location 2971 reports an APR of 7.2
percent and a Sharpe ratio of 1.3 on GBPUSD, with the open at 5:00 a.m. ET
and the close at 5:00 p.m. ET. No such series is committed here, and neither
is the code that ran it.
[Issue 365](https://github.com/l3a0/quantitative-trading/issues/365) carries
running it.

**What the VIX filter does to the rule.** Location 3509 measures the same
rule on the days after the VIX closed above 35, and reports an annualized
average return of 2.6 percent and a Sharpe ratio of 0.16 there. This entry
does not run the filter. Running it needs both readings too, since the
figure of around 13 percent that location 3509 sets beside them belongs to
the literal sign. Entry 47 runs it, under
[issue 359](https://github.com/l3a0/quantitative-trading/issues/359), and
finds the filtered figures belong to the literal sign too.

**Whether any of the three rules works out of sample.** Neither reading of
the script and not the port's rule has been run past Chan's window. The
rules, the save and the window are Chan's, and the sample is the one he
reported on. A registered test would fix one rule first and run it on data
after 2012.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/opening-gap-lessons.md](../blog/opening-gap-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.opening_gap_figures` redraws.

The post also carries two whiteboard sketches, both in Lesson 1, added in the
first round of its review before publishing.

1. **One day, two signs**, after the paragraph on a long day. It draws the
   post's worked day, a long day falling from 100 to 90 and a short day
   rising from 100 to 120, with the literal reading earning +10% and +20%
   and the momentum reading −10% and −20%. It is schematic and carries no
   figure from the data.
2. **Why Chan’s Python port never holds a long**, after the first paragraph
   under *The port and its flipped short test*. It draws the script's long,
   flat and short zones beside the port's, whose short zone runs from the
   lower level past the top of the long zone and wins because it is set
   last. Its levels and zones are schematic. Its counts come from the run:
   long on 0 days, short on 1,718, and all 278 upward jumps sold.

A change to the port's counts moves the second sketch too, and
`uv run python -m chan.opening_gap_whiteboard` redraws both through the same
`read_sources` and `python_port`.

## Entry 41: VX against ES on VX's roll return, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle locations 2747 to 2754 and Figure 6.4, in
Chapter 6, after Simon and Campasano (2012). Shipped under
[issue 357](https://github.com/l3a0/quantitative-trading/issues/357). The
script is `VX_ES_rollreturn.m`, in ericnberwick/EpchanPreview at `e4bc46f`
under `public/img/book2/`, git blob `849e0ac`, and the line numbers below are
that blob's. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from
[tests/test_vx_es_roll_return.py](../tests/test_vx_es_roll_return.py). Ten
match one printed figure to one computation, and rows 9 and 10 are the book's
rounded forms of what rows 1 and 2 compute. Row 11 carries no published
figure, and its cells say so.

A VX future converges on the VIX index as it nears settlement, so a front
contract priced well above VIX tends to fall toward it, and one priced well
below tends to rise. That convergence is VX's roll return. Volatility rises
when the stock market falls, so E-mini S&P 500 futures, ES, held the same
way as VX hedge most of the market's move. Location 2747 says no ETF holds
VIX, because a basket of options replicating it is too expensive to keep, and
that ES, whose roll return is about 1 percent a year, can stand in for a
series that moves against it. Location 2754 gives the
rule. If the front VX contract is above VIX by 0.1 point times the trading
days left to settlement, "short 0.3906 front contracts of VX and short 1
front contract of ES. Hold for one day." If it is below by that much, buy
both. The same location reports "6.9 percent, with a Sharpe ratio of 1" from
July 29, 2010, to May 7, 2012, a period "not used for hedge ratio
determination".

**Every figure reproduces on Chan's own files, and the book's come from the
script's commented lines.** The script carries two position rules. Its live
lines, 48 to 49 and 56 to 57, hold one VX contract per ES contract, and its
comment at lines 86 to 88 prints that rule's four figures. The lines holding
0.3906 VX contracts, 47 and 55, are commented out, and the comment at lines
81 to 82 prints theirs. The book's two figures round from the block at lines
81 to 82.
Each rule misses the other's printed APR by 0.224841 and its Sharpe ratio by
2.261932, so the two blocks cannot be read as one run.

**A scratch run came before the criterion.** The order was not the one this
repo asks for. A research pass on the issue ran a scratch transcription and
saw all eight of the script's figures land before the issue wrote down what
a landing figure is. The criterion it then fixed is the rule every earlier
entry uses: a figure lands when the computed value rounds to the printed
string at the decimals the string carries, which is
`chan.khandani_lo_book_two.matches`. Nothing in it was chosen to fit the
run.

Rows 1 to 10 use three vintages as data and one of two specifications, so
they are stated once here. Row 11 also uses the fourth vintage below, and its
specification is the fitted hedge rather than 0.3906 or [1, 1].

1. **The vintages.** Four of Chan's book-two files, the fourth used as data
   for row 11 alone. Every row still checks all four against their checksums,
   because loading ES reads every member of its 53-series save, the fourth
   among them, so a changed or missing fourth refuses rows 1 to 10 too.
   1. `data/inputdatadaily_vx_20120507/`, lifted from
      `inputDataDaily_VX_20120507.mat`, vendor `chan-mat`, basis `raw`, saved
      2012-05-08. It is one vintage per contract, 72 of them from VX-2007F to
      VX-2012Z, over 1,543 days from 2006-03-23 to 2012-05-07, with no spot
      column. It is read through `chan.roll_returns.load_strip`, which guards
      every contract over its own rows and refuses nothing.
   2. `data/vix/vix.csv`, lifted from `VIX.csv`, vendor `chan-csv`, basis
      `raw`, saved 2012-05-09, 5,635 rows from 1990-01-02 to 2012-05-08. The
      script reads its last column, `Adj Close`, which equals `Close` on every
      row. This is the first replication to read the file. The scale-break
      guard reads it from 2008-08-04 to 2012-05-07 and refuses nothing. The
      file flags 2007-02-27, a real move from 11.15 to 18.31. It counts
      among the front rows below VIX in conclusion 5, and no figure of the
      trade's reads it, as
      `TestTheGuardAndTheReads::test_no_figure_reads_vix_before_the_test_s_first_held_close`
      holds.
   3. `data/inputdataohlcdaily_20120507/es.csv`, lifted from
      `inputDataOHLCDaily_20120507.mat`, vendor `chan-mat`, basis `adjusted`,
      saved 2012-05-09, 2,000 rows from 2004-06-02 to 2012-05-08. ES was
      rewritten between saves, so this save is part of the specification.
   4. `data/inputdataohlcdaily_20120507/vx.csv`, VX's continuous close from
      the same save as ES, vendor `chan-mat`, basis `adjusted`, saved
      2012-05-09, 2,000 rows from 2004-06-01 to 2012-05-08. Only row 11 uses
      its prices. `chan.vx_es.read_legs` reads it with ES to fit the
      hedge, and guards each over its whole span and refuses nothing.
      The run fits that hedge before it prints, so a flagged day in
      either would stop the run.
2. **The specifications.** `VX_ES_rollreturn.m` as
   `chan.vx_es_roll_return` transcribes it, with one of two hedges: H, the
   0.3906 of lines 47 and 55, and U, the [1, 1] of the live lines. The three
   calendars share all 1,543 of the strip's days. Each contract is the front
   from 40 to 10 rows before its last priced row, starting no earlier than
   the row after the previous front ended. That is the loop Entry 39's script
   runs, and `chan.xle_uso_roll_return.front_windows` carries it for both. On
   a front row, `(VX − VIX) / (expiry − row + 1)` above 0.1 is short the
   hedge in front VX contracts and one ES contract, below −0.1 long both, and
   anything else flat. Each day earns yesterday's dollar profit on
   `y = [1000·VX, 50·ES]` over yesterday's gross market value, less one basis
   point of the day's change in market value over the same gross, with NaN
   set to 0. The figures are taken over the 448 rows after the first 500 from
   2008-08-04, which run from 2010-07-29 to 2012-05-07. The APR is
   `prod(1 + r)^(252 / 448) − 1`, the Sharpe ratio is
   `√252 · mean(r) / std(r)` with the standard deviation dividing by
   n − 1 and no risk-free rate, and the drawdowns come from `calculateMaxDD`.

The 2008-08-04 anchor and the 500-row split are the script's, and Entry 28
found that the first 500 rows from the anchor on the same save are the window
that fits the 0.3906 hedge. Over the test, H and U hold a position on 224 of
the 448 days, short on 196 and long on 28, with 32 entries from flat.

Every result here is **exploratory**. Reproducing Chan's figures spends his
2008 to 2012 sample on a rule Simon and Campasano proposed and a hedge he
chose.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The APR, H | 0.069065 | script line 81 |
| 2 | The Sharpe ratio, H | 1.002020 | script line 81 |
| 3 | The maximum drawdown, H | −0.075683 | script line 82 |
| 4 | The longest drawdown, H | 259 days | script line 82 |
| 5 | The APR, U | 0.293906 | script line 87 |
| 6 | The Sharpe ratio, U | 3.263952 | script line 87 |
| 7 | The maximum drawdown, U | −0.035798 | script line 88 |
| 8 | The longest drawdown, U | 59 days | script line 88 |
| 9 | The APR, book | "6.9 percent" | location 2754 |
| 10 | The Sharpe ratio, book | "a Sharpe ratio of 1" | location 2754 |
| 11 | The fitted hedge traded in place of 0.3906 | none, nothing prints it | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `prod(1 + r)^(252 / 448) − 1` under H | 0.069065 | `TestTheHedgedSpecification::test_the_apr` |
| 2 | `√252 · mean(r) / std(r)` under H | 1.002020 | `TestTheHedgedSpecification::test_the_sharpe_ratio` |
| 3 | `calculateMaxDD(cumprod(1 + r) − 1)` under H, the deepest drawdown | −0.075683 | `TestTheHedgedSpecification::test_the_maximum_drawdown` |
| 4 | The same, the longest run of days below a high | 259 | `TestTheHedgedSpecification::test_the_longest_drawdown` |
| 5 | Row 1 under U | 0.293906 | `TestTheShippedSpecification::test_the_apr` |
| 6 | Row 2 under U | 3.263952 | `TestTheShippedSpecification::test_the_sharpe_ratio` |
| 7 | Row 3 under U | −0.035798 | `TestTheShippedSpecification::test_the_maximum_drawdown` |
| 8 | Row 4 under U | 59 | `TestTheShippedSpecification::test_the_longest_drawdown` |
| 9 | Row 1, in percent | 6.906464 | `TestTheHedgedSpecification::test_the_apr`, and `::test_both_reproduce_the_book_s_figures` for the rounding |
| 10 | Row 2 | 1.002020 | `TestTheHedgedSpecification::test_the_sharpe_ratio`, and `::test_both_reproduce_the_book_s_figures` for the rounding |
| 11 | H with `chan.vx_es`'s fitted hedge, 0.390594, in place of 0.3906: the APR and the Sharpe ratio | 0.069062 and 1.001978 | `TestTheFittedHedge::test_it_misses_the_script_s_sixth_decimal_on_both` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.000000 | reproduced | Exact at the six decimals the script prints. |
| 2 | +0.000000 | reproduced | The same. |
| 3 | +0.000000 | reproduced | The same. |
| 4 | 0 days | reproduced | Exact. |
| 5 | +0.000000 | reproduced | Exact at the six decimals the script prints. |
| 6 | −0.000000 | reproduced | The same. |
| 7 | −0.000000 | reproduced | The same. |
| 8 | 0 days | reproduced | Exact. |
| 9 | +0.0 percent | reproduced | 6.906464 percent rounds to the book's 6.9. |
| 10 | +0 | reproduced | 1.002020 rounds to the book's 1. |
| 11 | none | none, not a replication | Nothing prints a figure for the fitted hedge. Against rows 1 and 2's printed strings it misses by −0.000003 and −0.000042, so the script traded the rounded 0.3906 rather than the hedge Entry 28 fits, and the run takes the printed constant. |

### What the entry concludes

Six things. The last three were measured by the write-up after the run, and
`TestWhatThePostMeasured` in
[tests/test_vx_es_roll_return.py](../tests/test_vx_es_roll_return.py) pins
them.

1. **Both of the script's rules reproduce on Chan's own files.** All eight
   figures its comments print land at the precision printed, the APRs,
   Sharpe ratios and maximum drawdowns to six decimals and the two day counts
   exactly.
2. **The book's figures come from the commented rule.** The script as it
   ships prints the [1, 1] block. The book's 6.9 percent and Sharpe ratio of
   1 round from the 0.3906 block, which is the rule the text describes, and
   neither rule lands the other's figures.
3. **The script traded the printed constant.** The hedge fitted on the same
   500 rows rounds to 0.3906, but trading it misses the script's sixth
   decimal on both the APR and the Sharpe ratio.
4. **Every held stretch opens free.** The test's held days fall into 32
   stretches, 25 short and 7 long, and no position changes sign without a
   flat day between, so each of the 32 is an entry from flat. Under 0.3906,
   setting each entry day's return to one basis point lost gives an APR of
   0.067142 and a Sharpe ratio of 0.975830, and charging no cost at all gives
   0.071248 and 1.030894. Measured after the run.
5. **The window is out of sample for the hedge alone.** The hedge's 500 days,
   2008-08-04 to 2010-07-28, are the trade's own first 500 from the anchor.
   The 40-row start of the front window decides only VX-2007F's window, and
   on the test's 438 front rows the script's front is the nearest priced
   contract on 228 and the second-nearest on 210. The 0.1 threshold and the
   window carry no statement that the test did not set them. Over the whole
   calendar the front sits above VIX on 1,016 of the 1,369 front rows.
   Measured after the run.
6. **The hedge leaves the trade mostly in ES.** On the 224 held test days
   the VX leg is a median 0.119966 of the gross under 0.3906 and 0.258710
   under [1, 1]. Summed over the test, the VX leg earns 0.285954, the ES leg
   −0.159336 and the cost 0.003634 under 0.3906, for 0.122984, and 0.605959,
   −0.138046 and 0.003961 under [1, 1], for 0.463952. On 2011-08-08, the
   0.3906 rule's worst day and its deepest drawdown's trough, both rules held
   long, ES fell 7.3259 percent and VX-2011U rose 15.2672 percent, and the
   rules lost 3.9889 and 0.3823 percent. On the 224 earning test days the
   front's daily return correlates with ES's at −0.813746. Measured after
   the run, so it describes one sample and tests no cause.

### What this entry cannot say

Three things.

**What the trade cost to enter.** On the day a position opens from flat,
yesterday's gross is 0, so the day's return divides by 0, is set to 0, and
the script never charges the entry's cost. The test holds 32 such entries.
The script charges a held day on its mark-to-market move as well as on any
trade. The figures copy the free entry and the charge on mark-to-market
moves, as the criterion asks. Conclusion 4 sets two other cost models
beside them, measured after the run, and neither is what a broker charged.

**What the trade did in its last ten days.** Eight contracts are priced on
2012-05-07, the file's last day, so each reads as expiring there. VX-2012K's
window ends on 2012-04-23, its days to settlement count to 2012-05-07 rather
than to its real expiry, and the test's last 10 rows hold nothing. The
first of them, 2012-04-24, earns the position held at the 2012-04-23 close
less its exit cost, and the script counts the other nine as earning 0.

**Whether the trade works out of sample.** The rule is Simon and
Campasano's, the hedge and the window are Chan's, and the sample is the one
he reported on. A registered test would fix the rule first and run it on data
after 2012.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/vx-es-roll-return-lessons.md](../blog/vx-es-roll-return-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.vx_es_roll_return_figures` redraws.

## Entry 42: whether Example 7.4's own factor returns have momentum, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 4014 and
4051. Shipped under
[issue 286](https://github.com/l3a0/quantitative-trading/issues/286). Both
locations are the revised edition's, and both highlights are in
[research/book-notes/quantitative-trading.md](../research/book-notes/quantitative-trading.md).

Sixteen rows, all derivable from
[tests/test_pca_factor_momentum.py](../tests/test_pca_factor_momentum.py).

**The claim holds for four of Example 7.4's five factors and does not hold
for the third.** Example 7.4's revised MATLAB rests on a factor return seen
today saying something about tomorrow's. Location 4051 says the strategy is
"based on the assumption that factor returns have momentum", and location
4014 states the general claim, that factor returns "often" show stronger
serial autocorrelation than single stocks do. Entry 14 tested that claim on two
named factors, monthly, on Chan's S&P 500 file. This entry tests the five
statistical factors Example 7.4 fits for itself, daily, on the S&P 600 file
the example loads. Over 752 pairs of one day's factor return and the next,
the five statistics are 0.0316, 0.0778, −0.0189, 0.0305 and 0.0710, against a
median of −0.0283 across the 579 stocks priced on every day the pairs read.
PC1, PC2, PC4 and PC5 are above 0 and above the median stock. PC3 is above
the median stock and below 0.

The verdicts rest on little. PC2 alone sits outside the band where the
statistic of a series of independent returns centred on zero, each no more
likely to be large than any other day's, lands 95 percent of the time, and
no factor survives a control for false discoveries across the five. Which
factor misses also rests on one symbol. Dropping PMC, whose two price
histories the program joins into one day's return of 1.8654, moves PC2 below
0 and PC3 above it.

Five rows are claims and eleven are not replications. Rows 1 to 5 take the
claim route `### Rows that are not replications` describes, one per factor.
Rows 6 to 16 are the figures the issue reports beside the verdicts, which
decide nothing.

Every rule was fixed on
[issue 286](https://github.com/l3a0/quantitative-trading/issues/286) on
2026-10-10, before any factor return was computed. The owner ruled the same
day, also before, that each factor carries its own verdict with Chan's
"often" quoted beside it and that no combined verdict is formed, which carries
over the ruling Entry 14 rests on. Eight things carry the result: the vintage
and seven of the issue's rules, each as the issue fixed it.

1. **The vintage.** `ijr_20080114/`, the 600 stocks of Chan's
   `IJR_20080114.mat`, saved 2008-01-15, read for its closes through
   `chan.series.load_panel`. It spans 2004-01-15 to 2008-01-14, 1,006 days.
   Nothing was downloaded. [data/README.md](../data/README.md) says what it
   holds.
2. **The factor returns.** Only the revised MATLAB,
   `chan.pca_factor.revised_matlab`, is tested, and Entry 13 reproduces its
   figures. On day t it decomposes the 252 returns ending t − 1 by a singular
   value decomposition. For each of the five factors that gives a unit-length
   vector u_k of weights across the stocks and a singular value s_k, which
   measures how much of the window's variation the factor carries. The
   program then fits day t's returns r_t on an intercept and five scores, each
   u_k times s_k, so each fitted slope is u_k · r_t / s_k. Each score times
   its slope is u_k (u_k · r_t), so the fitted value the strategy ranks on
   does not depend on s_k. The factor return tested here is therefore
   f_t[k] = u_k · r_t, the slope times s_k. Its partner is
   f_{t+1}[k] = u_k · r_{t+1}, on the same vectors and the same stocks, so
   each pair comes from one decomposition.
   `TestOnRealDays::test_each_factor_return_is_s_times_the_programs_slope`
   holds that on three of the file's days. The price is that f is not the
   coefficient the program's regression returns. That coefficient would
   weight each day by 1/s_k², and nothing in the strategy weights days that
   way. The intercept is not a factor. It is added to every stock's expected
   return alike, so it moves no position, which the issue's rule 6 fixed
   with the others.
3. **The statistic.** For each factor, the uncentred correlation of its
   pairs: the sum of f_t f_{t+1}, over the square root of the sum of f_t²
   times the sum of f_{t+1}². It is the ordinary correlation without
   subtracting either series' mean first. A singular vector's sign is
   arbitrary, and flipping it on one day flips both members of that day's
   pair, so no product and no sum of squares moves. Leaving out the centring
   is deliberate. A factor return that keeps a steady nonzero mean in one
   orientation counts as persistent, which is what location 4051's "remain
   constant from the current time period to the next" asks. The price is that
   a few large days can carry the statistic, so row 9 reports beside it the
   share of pairs whose two members have the same sign.
4. **Which factor is factor k.** Factor k is the k-th largest component as
   each day's decomposition ranks it, named PC1 to PC5. When two neighbouring
   components swap places between days, their pairs mix into each other's
   statistic. No pair breaks, because each pair comes from one decomposition.
5. **The comparison set.** Every stock with a finite return on every row the
   pairs read, after the forward fill the program does. Each stock gets the
   same uncentred statistic on its own pairs of one day's return and the
   next. Their median stands for "individual stock's returns", as in
   Entry 14.
6. **The criterion.** The claim holds for a factor when its statistic is
   above 0 and above the median stock's, both compared unrounded. Each of the
   five carries its own verdict, under the owner's ruling.
7. **The printouts.** The revised MATLAB only, because its 2 percent is the
   figure location 4051 quotes. The revised Python and the R regress with an
   intercept that cancels their factors, Entry 13's row 11 for the Python and
   [issue 21](https://github.com/l3a0/quantitative-trading/issues/21)'s reading
   of the R's printed `lm(R[,s] ~ X)` for the R, so they have no factor
   returns to test. The first edition is not tested, for the reasons
   `### What this entry cannot say` gives.
8. **The hypothesis space.** Five hypotheses, one per factor, each at lag 1
   on the committed file with a lookback of 252 and five factors. No other
   lag, statistic, printout, lookback or factor count was tried. Significance
   is reported beside the verdicts and decides nothing. Each factor gets the
   one-sided Newey-West t of its daily products f_t f_{t+1} against a mean of
   zero, and its normal p-value. A Newey-West t is a t-statistic whose
   standard error allows for neighbouring days being correlated and for days
   of different size. Benjamini-Hochberg at q = 0.05 then runs across the
   five p-values. It holds the expected share of false discoveries among the
   factors it declares significant to 5 percent. When no factor has
   persistence, that also holds the chance that any of the five passes by
   luck to 5 percent.

**Every figure here is about survivors.** The file holds the S&P 600 as it
stood on 2008-01-14, carried backwards. The factors are fitted on stocks that
stayed in the index, and the comparison set is drawn from the same stocks.
Which way that moves any statistic is not measured here.

**One symbol holds two price histories.** PMC closes, goes missing for 851
days, and resumes as a different price history under the same ticker. The
program's forward fill reads the gap as one day's return of 1.8654, which
`TestTheSplice` in [tests/test_pca_factor.py](../tests/test_pca_factor.py)
pins. The verdicts read the file as the program does, and rows 13 to 16 give
the figures again without PMC.

Every result here is **exploratory**. Testing a claim someone else chose
spends the 2004 to 2008 sample on it, so the entry says whether the claim
holds on this file and nothing about factor momentum today.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | PC1 has stronger serial autocorrelation than single stocks, so it has momentum | the claim, "often", with no figure | location 4014, and location 4051 for Example 7.4 resting on it |
| 2 | PC2 has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014 |
| 3 | PC3 has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014 |
| 4 | PC4 has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014 |
| 5 | PC5 has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014 |
| 6 to 16 | the pairs and the comparison set, each factor's statistic, percentile and same-sign share, the stocks' quartiles, the band, each factor's Newey-West t and p-value and Benjamini-Hochberg, the intercept, and each again without PMC | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | PC1's statistic against 0 and against the median stock's, unrounded | 0.0316, above 0 and above −0.0283 | `TestTheVerdicts::test_pc1_pc2_pc4_and_pc5_hold_above_zero_and_above_the_median_stock`, for PC1 |
| 2 | PC2's statistic against the same two | 0.0778, above 0 and above −0.0283 | the same test, for PC2 |
| 3 | PC3's statistic against the same two | −0.0189, below 0 and above −0.0283 | `TestTheVerdicts::test_pc3_misses_below_zero_though_above_the_median_stock` |
| 4 | PC4's statistic against the same two | 0.0305, above 0 and above −0.0283 | the same test as row 1, for PC4 |
| 5 | PC5's statistic against the same two | 0.0710, above 0 and above −0.0283 | the same test as row 1, for PC5 |
| 6 | the pairs, and the stocks priced on every row they read | 752 pairs, day t from 2005-01-18 to 2008-01-11, every factor return finite. 579 stocks | `TestThePairs::test_752_pairs_from_the_first_fitting_day`, `::test_every_factor_return_is_finite` and `::test_579_stocks_are_priced_on_every_row_the_pairs_read` |
| 7 | each factor's statistic, and the percent of the 579 stocks strictly below it | PC1 0.0316 at 83.9378, PC2 0.0778 at 95.6822, PC3 −0.0189 at 55.0950, PC4 0.0305 at 83.4197, PC5 0.0710 at 94.3005 | `TestTheFigures::test_each_factors_statistic` and `::test_each_factors_percentile_among_the_stocks` |
| 8 | the 579 stocks' statistics, lower quartile, median and upper quartile, by linear interpolation | −0.0729, −0.0283 and 0.0137 | `TestTheFigures::test_the_stocks_median_and_quartiles` |
| 9 | each factor's share of pairs whose two members have the same sign | 0.5226, 0.5146, 0.5106, 0.5173 and 0.5000 | `TestTheFigures::test_each_factors_same_sign_share` |
| 10 | ±1.96/√752, and which factors fall outside it | 0.0715, PC2 alone | `TestTheFigures::test_the_band_is_1_96_over_root_752` and `::test_only_pc2_falls_outside_the_band` |
| 11 | each factor's one-sided Newey-West t of f_t f_{t+1} against 0, its normal p-value, and Benjamini-Hochberg at q = 0.05 across the five | t of 0.9029, 0.8254, −0.4034, 0.8743 and 1.2697. p of 0.1833, 0.2046, 0.6567, 0.1910 and 0.1021. None survives | `TestTheFigures::test_each_factors_newey_west_t_and_p` and `::test_no_factor_survives_benjamini_hochberg` |
| 12 | the intercept, which is each day's equal-weighted mean return: its uncentred statistic and its ordinary lag-1 correlation | −0.0395 and −0.0401 | `TestTheFigures::test_the_intercepts_two_figures`, and `TestTheRules::test_the_intercept_is_the_days_mean` for what it is |
| 13 | rows 7 and 8 without PMC, over the 578 stocks left | PC1 0.0740 at 94.9827, PC2 −0.0152 at 57.0934, PC3 0.0139 at 75.2595, PC4 0.0975 at 98.0969, PC5 0.0536 at 89.9654. Quartiles −0.0732, −0.0283 and 0.0137 | `TestWithoutPMC::test_each_factors_statistic`, `::test_each_factors_percentile_among_the_stocks` and `::test_the_stocks_median_and_quartiles`, and `TestThePairs::test_579_stocks_are_priced_on_every_row_the_pairs_read` for the 578 |
| 14 | rows 9 and 12 without PMC | shares of 0.5199, 0.5146, 0.5133, 0.5146 and 0.5053. The intercept's −0.0394 and −0.0401 | `TestWithoutPMC::test_each_factors_same_sign_share` and `::test_the_intercepts_two_figures` |
| 15 | rows 10 and 11 without PMC, over the same 752 pairs | 0.0715, with PC1 and PC4 outside it. t of 0.9754, −0.3926, 0.4221, 1.8537 and 1.1759. p of 0.1647, 0.6527, 0.3365, 0.0319 and 0.1198. None survives | `TestWithoutPMC::test_the_band`, `::test_pc1_and_pc4_fall_outside_the_band`, `::test_each_factors_newey_west_t_and_p` and `::test_no_factor_survives_benjamini_hochberg`, and `TestThePairs::test_752_pairs_from_the_first_fitting_day` for the pairs |
| 16 | the criterion's two halves for each factor without PMC | PC2 above −0.0283 and below 0, the other four above both | `TestWithoutPMC::test_the_criterion_would_miss_pc2_rather_than_pc3` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The claim holds for PC1, which Chan says factors "often" show. Its statistic is above 0 and above the median stock's, under the criterion declared on the issue before any factor return was computed. It sits at 0.0316, inside row 10's band, and survives no control for false discoveries in row 11, so this verdict could be noise. |
| 2 | reproduced | The claim holds for PC2, which Chan says factors "often" show. Its statistic is above 0 and above the median stock's. It sits at 0.0778, the one factor outside row 10's band, but its Newey-West t of 0.8254 gives a one-sided p-value of 0.2046 and it survives no control for false discoveries in row 11, so this verdict could be noise too. The band is right only when a large return, up or down, makes a large one the next day no more likely. PC2's largest returns fell on neighbouring days, so its products scatter far wider than the band assumes, and the t divides by a distance that comes from that scatter, which keeps it small. Without PMC its statistic falls to −0.0152, below 0, under row 16. |
| 3 | did not reproduce | The claim, which Chan says factors "often" show, does not hold for PC3. Its −0.0189 is above the median stock's −0.0283 and below 0. Under the owner's ruling this verdict stands on its own, and no combined verdict is drawn from rows 1 to 5. The value is forced, because the log's two other verdicts both need the claim to survive. It sits inside row 10's band, so this miss could be noise as much as row 1's pass could. Without PMC its statistic rises to 0.0139, above both, and PC2 misses in its place under row 16, so which factor misses rests on one symbol. Two more causes outside the method are open and neither is measured: the file holds only survivors, and 2005 to 2008 is one window. |
| 4 | reproduced | The claim holds for PC4, which Chan says factors "often" show. Its statistic is above 0 and above the median stock's. It sits at 0.0305, inside row 10's band, and survives no control for false discoveries in row 11, so this verdict could be noise. |
| 5 | reproduced | The claim holds for PC5, which Chan says factors "often" show. Its statistic is above 0 and above the median stock's. It sits at 0.0710, just inside row 10's band, and survives no control for false discoveries in row 11, so this verdict could be noise. Its pairs share a sign exactly as often as not, under row 9, so the positive statistic comes from its larger pairs agreeing in sign. |
| 6 | none, not a replication | The pairs run from the revised MATLAB's first fitting day to the second-to-last row, because day t's pair needs day t + 1. No stock in a day's cross-section lacks a return on day t + 1, so no pair has a gap. |
| 7 | none, not a replication | PC2 sits above 95.6822 percent of the stocks and PC3 above 55.0950 percent, so even the factor that misses is more persistent than the median stock on this file. |
| 8 | none, not a replication | The quartiles use pandas' default linear interpolation. The median is negative, so on this file a factor above 0 is also above the median stock. PC3 shows the other half: it is above the median stock and still below 0. That is a fact about this panel, and the criterion keeps both halves as declared. |
| 9 | none, not a replication | Every share sits between 0.5000 and 0.5226. PC5's is exactly one half, which is the price rule 3 names: a few large days can carry the statistic. |
| 10 | none, not a replication | Under a series of independent returns centred on zero, each no more likely to be large than any other day's, an estimate from 752 pairs falls outside ±0.0715 about 5 percent of the time. PC2 sits outside it, and PC5's 0.0710 sits just inside. |
| 11 | none, not a replication | The smallest p-value is PC5's 0.1021, so no factor would pass at 5 percent even tested alone, and Benjamini-Hochberg across the five rejects none. A sign flip moves no product, so it cannot move a t either. |
| 12 | none, not a replication | The intercept is added to every stock's expected return alike, so it moves no position. Both of its figures are negative and inside row 10's band. |
| 13 | none, not a replication | Without PMC the comparison set keeps the other 578 stocks, and the median is unchanged at four decimals. PC1 and PC4 rise, PC5 falls, PC2 falls below 0 and PC3 rises above it. |
| 14 | none, not a replication | Every share stays between 0.5053 and 0.5199. The intercept's uncentred figure moves from −0.0395 to −0.0394, and its ordinary one stays at −0.0401. |
| 15 | none, not a replication | Without PMC, PC1 and PC4 sit outside the band and PC2 returns inside it. Benjamini-Hochberg still rejects none, because no p-value clears its own threshold. The k-th smallest is held to k fifths of 0.05, so PC4's 0.0319, the smallest, is held to 0.01. |
| 16 | none, not a replication | Without PMC the criterion would miss PC2 and pass the other four, PC3 among them. The verdicts read the file as the program does, which forward-fills, so they stay as rows 1 to 5 give them, and this row replaces none. |

### What the entry concludes

Three things, and the first is the verdict.

1. **On this file the claim holds for four of Example 7.4's five factors and
   not for PC3.** PC1, PC2, PC4 and PC5 are above 0 and above the median
   stock. PC3 is above the median stock and below 0. Each verdict stands on
   its own, with Chan's "often" quoted beside it, and the entry draws no
   combined verdict.
2. **The verdicts rest on little.** No factor survives a control for false
   discoveries across the five, and no p-value would pass at 5 percent even
   alone. Four of the five sit inside the band where the statistic of a
   series of independent returns centred on zero, each no more likely to be
   large than any other day's, lands 95 percent of the time. PC2 sits
   outside it and still has a one-sided p-value of 0.2046.
3. **Which factor misses rests on one symbol.** Without PMC, PC2 falls below
   0 and PC3 rises above it, so the criterion would miss PC2 instead.

### What this entry cannot say

Four things.

**What the factors do on the S&P 600 as it stood each day.** The file holds
the index as it stood on 2008-01-14, carried backwards.
[Issue 269](https://github.com/l3a0/quantitative-trading/issues/269) reruns
Example 7.4 on the index as it stood each day of 2004 to 2008, which would
fit the factors on a universe without survivorship.

**Whether the first edition's factors persist.** It was not tested, for two
reasons the issue gives. Its day-t exposures come from a window that ends on
day t itself, so its day-t factor return is fitted on a cross-section that
helped choose its own exposures, while its day t + 1 return is not, and the
pair is not like for like. Its fit also demeans day t by each stock's window
mean, which leaves no rule for demeaning day t + 1.

**Whether the factors persist at another lag or frequency.** Only lag 1 on
daily returns was computed, with a lookback of 252 and five factors, under
the hypothesis space fixed on the issue. No other lag, frequency, lookback or
factor count was tried after these figures were seen.

**Whether the revised MATLAB's 2 percent comes from factor momentum.** This
entry tests the assumption the strategy rests on, and not how much of the
strategy's return the assumption earns. Nothing here splits the 2 percent
into a part that factor persistence accounts for and a part it does not.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/factor-models-lessons.md](../blog/factor-models-lessons.md) moves with
it, since that post's Lesson 3 quotes these figures.
[blog/pca-factor-momentum-lessons.md](../blog/pca-factor-momentum-lessons.md)
moves with it too, since that post quotes most of them. It also quotes what
the write-up measured after the run, which `TestWhatThePostMeasured` in
[tests/test_pca_factor_momentum.py](../tests/test_pca_factor_momentum.py)
pins and which decides nothing. It quotes how often each factor's weights
flip sign once each vector's largest weight in size is made positive, and that all but
five of those flips move the largest weight to a stock the earlier day weighed
below zero. The five left fall on days two or more factors swap rank. Those
pins also count how often they swap rank from day to
day, and give the statistic on three other ways of reading tomorrow's factor return and on
a 251-day window that still holds today's return. They read PMC's weight on
the 113 days from 2007-08-02 to 2008-01-11 whose window holds its one large
return, and which factor carries it, and name the two days that carry PC2's
statistic, which carry PC1's without PMC. Its one figure, which
`uv run python -m chan.pca_factor_momentum_figures`
redraws, moves with them. The factor models post's Lesson 3 whiteboard
sketch, which draws a sign flip in one day's weights changing both members of
a pair, is schematic and draws none of these figures, and
`uv run python -m chan.factor_models_whiteboard` redraws it. The PCA factor
momentum post's two whiteboard sketches draw some of them. The window sketch draws PC2's statistic
four ways: on tomorrow's own weights matched, with today left out, on the 251
days that still hold today, and as the pair reads it. The rank shift sketch
draws PMC's weight on PC1, the days PMC carries PC1, the two days' shares of
PC2's squared products and of PC1's without PMC, and PC2's statistic with PMC
and without. They move with a re-pin of any of those, and
`uv run python -m chan.pca_factor_momentum_whiteboard` redraws them.

## Entry 43: Monte Carlo leverage, historical optimization and CPPI, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Boxes 8.1 to 8.6 and Kindle locations 3319 to 3438,
in Chapter 8. Shipped under
[issue 360](https://github.com/l3a0/quantitative-trading/issues/360). The
script is `monteCarloOptimLeverage.m`, in ericnberwick/EpchanPreview at
`e4bc46f` under `public/img/book2/`, git blob `fc32599`, and the line numbers
below are that blob's. Every location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Seventeen rows, all derivable from
[tests/test_monte_carlo_leverage.py](../tests/test_monte_carlo_leverage.py).
Twelve do not match one printed figure to one computation, and each says so
in its own cells. Rows 3 and 5 judge two printed figures each, and row 10 a
drawdown with the leverage printed beside it. Rows 11 and 12 set printed
figures beside a claim, rows 4 and 7 are a claim alone, and rows 13 to 17
carry no published figure. Rows 1, 2, 6 and 7 are deterministic. The
simulated rows are judged against an ensemble of seeds or against the exact
distribution of the figure.

A leverage that maximizes growth can still bring a drawdown near total loss.
Chapter 8 makes that case on Example 5.1's AUD.CAD strategy, whose 612 daily
returns Entry 25 reproduces. It fits a Pearson distribution to their mean,
standard deviation, skewness and kurtosis, draws 100,000 returns from it, and
finds the leverage f that maximizes the growth rate `g(f) = mean(log(1 +
f·R))` of the draws. It finds the same optimum on the historical returns. It
then shows how deep the drawdown runs at that leverage and at fractions of it.
Last, it runs constant proportion portfolio insurance (CPPI), which trades
only a slice D of the account and refills the slice to D of the account at
each new high, so the account cannot fall more than D below its high.

**The book's 18.4 does not reproduce on Chan's own returns, the simulated
figures split, and Box 8.6's CPPI loop breaks the drawdown floor that
location 3438 says it keeps by design.** The Kelly leverage and the historical
optimum come out near 23.8 rather than 18.4. No series that matches Example
5.1's printed figures gives 18.4 under any of three ways of compounding its
APR. The most negative draw and the drawdown at the optimum land inside their
bands. The simulated optimum, the drawdowns at half and a seventh of the
optimum, and both growth rates do not. The simulated optimum landed under the
band the issue declared and misses under the band this entry chose after
seeing the ensemble, and
[Why the simulated rows are judged against an ensemble](#why-the-simulated-rows-are-judged-against-an-ensemble)
gives the reason and keeps both verdicts. Moving the draws' mean so that the
Kelly is 18.4 lands all of those but the drawdown at half the optimum, and
lands the simulated optimum under either band. The CPPI the prose describes
keeps the floor on every seed, and the loop the book prints breaks it on every
seed.

Every row reads one vintage and one specification unless it names another,
so both are stated once here.

1. **The vintage.** `pythoncodesanddata/AUDCAD_unequal_ret.csv`, vendor
   `chan-py`, symbol `AUDCAD-UNEQUAL`, basis `return`, saved 2018-12-26, the
   612 test-set returns Example 5.1's `AUDCAD_unequal.m` saved, read through
   `chan.series.load_returns`. Line 3 of the script loads the same returns
   with no slicing.
2. **The specification.** `monteCarloOptimLeverage.m` as
   `chan.monte_carlo_leverage` transcribes it, under the declaration
   [issue 360](https://github.com/l3a0/quantitative-trading/issues/360) wrote
   before any draw on its seeds, in five parts.
   1. The moments are the mean, MATLAB's n − 1 `std`, and the biased
      skewness and kurtosis, with kurtosis not in excess form. The draws come
      from the Pearson type IV with those moments, through
      `chan.tu_hypothesis_tests`' sampler on a θ grid of 20,001 points. Seed
      s's draws are `pearson_iv_draws(params, default_rng(s).random(100_000))`.
   2. The optimum is Brent's bounded search, which is what `fminbnd` runs,
      with `xatol` of 1e-10. The capped optimum searches `(0, min(20, ruin))`,
      as line 22's `fminbnd(minusGsim, 0, 20)` does. The ruin leverage is one
      over the size of the most negative return. At or above it no real growth
      rate exists, so the search stops there rather than take MATLAB's real
      part of a complex logarithm. The uncapped optimum searches `(0, ruin)`.
   3. Every drawdown is `calculateMaxDD` on `cumprod(1 + a) − 1`, through
      `chan.matlab_helpers.calculate_max_dd`. D is 0.5, and every leverage on
      the draws is a multiple of the capped optimum f on the same draws, as
      the script uses it.
   4. The declared seed is 20261012 and the ensemble is the 200 seeds 20261013
      to 20261212. A simulated figure lands when the book's value lies within
      the ensemble's 5th to 95th percentile of the same quantity. A claim row
      is judged by its own criterion, on the declared seed where the criterion
      names none. Row 3's band changed after the ensemble was seen, and the
      section on ensembles below says how.
   5. A simulated figure outside its band did not reproduce. One inside its
      band whose seeded value differs is reproduced with a gap, and the seed is
      the cause, because location 3399 says the simulated figures "are not
      exactly reproducible".

**Type IV is an inference about `pearsrnd`.** Location 3342 says the type is
4, and Pearson's κ on these moments is inside type IV's 0 < κ < 1. As Entry 37
says of the same sampler, these draws follow the script's in distribution and
not draw for draw.

**Two CPPI forms run.** Location 3426 describes CPPI as a subaccount of D
traded at f and refilled to D of the account at each new high. Box 8.6's loop,
script lines 46 to 59, instead scales `D·f` by one plus the drawdown of the
unlevered returns, which is not the account's drawdown. Only the first form
guarantees what location 3438 claims, so row 12 judges the claim on both.
The script's second CPPI loop, on the historical returns, reads `r(t)` at
line 73, which nothing defines, so MATLAB stops there. Row 17 reads `ret` for
`r`, as the same loop's next line does.

Every result here is **exploratory**. Reproducing Chan's figures spends his
612 returns on a method he chose. The entry says whether his numbers reproduce
on his file, and nothing about whether any leverage is safe to trade.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | The Kelly leverage of the test-set returns | 18.4 | location 3342 |
| 2 | The Pearson type `pearsrnd` returns | 4 | location 3342 |
| 3 | The simulated optimum | 19 from `fminbnd`, and an unconstrained 19.2 | locations 3342 and 3399 |
| 4 | The simulated optimum is close to the Kelly | "strikingly close", a claim | location 3342 |
| 5 | The most negative simulated return, and the ruin leverage | −0.0331, and 30.2 | location 3342 |
| 6 | The optimum of the historical growth rate | 18.4 | location 3379 |
| 7 | The historical optimum is the Kelly | "again the same", a claim | location 3379 |
| 8 | The simulated maximum drawdown at the optimum | −0.999 | location 3399 |
| 9 | The same at half the optimum | −0.963 | location 3399 |
| 10 | The same at a seventh of the optimum | about −0.5, at about 2.7 | location 3399 |
| 11 | The growth rate of CPPI, against the full account at f·D, with D = 0.5 | 0.002484 against 0.002525, "very similar", a claim | location 3438 |
| 12 | CPPI's drawdown is less than 0.5 by design, and the full account's at f·D | a claim, and "a painful 0.9" | location 3438 |
| 13 | The evidence on the book's 18.4 | none | n/a |
| 14 | The fitted type IV's parameters | none | n/a |
| 15 | The uncapped simulated optimum, and the seeds the ruin leverage cut | none | n/a |
| 16 | The CPPI location 3426 describes | none | n/a |
| 17 | The script's lines on the historical returns | none | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `mean / std²` with the n − 1 variance | 23.845328, the script's own figure from Entry 25 | `TestRows1And2::test_row_1_the_kelly_is_the_script_s` |
| 2 | Pearson's κ of the four moments | 0.038081, inside 0 < κ < 1 | `TestRows1And2::test_row_2_kappa_puts_the_moments_in_type_iv` |
| 3 | The uncapped optimum on the declared seed, and its band across the seeds whose ruin leverage is above the book's 30.2 | 22.295382, where the capped optimum the script searches is the cap of 20, within 1e-6. The band across the 40 such seeds is 22.969856 to 25.374220. The declared band, across all 200 seeds, is 16.622019 to 24.865122, and its 5th percentile is the capped band's. 158 of the 200 seeds sit on the cap | `TestRows3And4TheSimulatedOptimum::test_the_declared_seed_s_uncapped_optimum`, `::test_the_band_row_3_reads`, `::test_the_uncapped_band`, `::test_the_declared_band_shares_the_capped_band_s_lower_tail`, `::test_the_declared_seed_sits_on_the_cap` and `::test_158_of_200_seeds_sit_on_the_cap` |
| 4 | Row 1's Kelly against row 3's band | 23.845328, inside 22.969856 to 25.374220, and inside the declared band too | `TestRows3And4TheSimulatedOptimum::test_row_4_the_kelly_lies_inside_row_3_s_band` |
| 5 | The declared seed's minimum, and the chance the least of 100,000 draws is at or below the book's | −0.043071 and a ruin leverage of 23.217362. The chance is 0.807083 at −0.0331, and 0.806406 at the ruin leverage of 30.2 | `TestRow5TheMinimumAndTheRuinLeverage::test_the_declared_seed_s_minimum_and_ruin_leverage` and `::test_the_book_s_minimum_in_its_exact_distribution` |
| 6 | The uncapped optimum of the historical growth rate | 23.721773, and the cap of 20 when capped | `TestRows6And7TheHistoricalOptimum::test_row_6_the_historical_optimum` and `::test_capped_at_20_it_returns_the_cap` |
| 7 | Row 6 over row 1, less 1, against 1 percent | −0.005182 | `TestRows6And7TheHistoricalOptimum::test_row_7_the_historical_optimum_is_within_1_percent_of_the_kelly` |
| 8 | `calculateMaxDD` at f on the declared seed, and its band | −0.991276, band −0.999256 to −0.979930 | `TestRows8To10TheDrawdowns::test_seeded_and_banded` |
| 9 | The same at f / 2 | −0.871216, band −0.922292 to −0.763269 | the same |
| 10 | The same at f / 7 | −0.416419, band −0.468433 to −0.302281, at a leverage of 2.857143 | the same, and `::test_row_10_falls_outside_its_band` |
| 11 | Box 8.6's growth and the full account's at f·D, their bands, and how far the first falls short | 0.003224, band 0.002913 to 0.003577, against 0.003271, band 0.002955 to 0.003623. Box 8.6's loop falls short of the full account by 0.014469 of it, and by less than 0.02 on every seed. The book's own two differ by 0.016238 | `TestRow11TheGrowthRates::test_seeded_and_banded`, `::test_the_claim_holds_on_the_declared_seed_and_every_seed` and `::test_the_book_s_own_two_figures_differ_by_1_6_percent` |
| 12 | The full account's drawdown at f·D, and each CPPI form's account drawdown | −0.871216, the same figure as row 9, since f·D is f / 2. Box 8.6's loop gives −0.848088, band −0.902235 to −0.742510, and stays above −0.5 on 0 of 200 seeds. Location 3426's CPPI gives −0.495638, band −0.499628 to −0.489965, and stays above −0.5 on 200 of 200 | `TestRow12TheDrawdownCppiCaps` |
| 13 | The Kelly of a daily series with a swing under 10 percent, a Sharpe ratio of 1.55 to 1.65 and an APR of 10.5 to 11.5 percent, under three compoundings, and the ensemble with the draws' mean moved so the Kelly is 18.4 | Kelly 21.558894 to 26.757652 when the APR compounds the log growth m − σ²/2, 22.065999 to 27.261771 when it compounds 1 + m exactly, and 20.891304 to 25.928571 when it is the simple 252·m. At a Sharpe ratio of 1.6, a Kelly of 18.4 needs an APR of 0.139130, 0.144937 or 0.149230 under the three. With the mean moved, λ is −1.222510e-03, the median uncapped optimum is 18.470198, 8 of 200 seeds sit on the cap, and rows 3, 8, 10 and 11 land. Row 3's band runs 17.514982 to 20.017014 on the 39 seeds whose ruin leverage is above 30.2, and 16.339353 to 19.905622 on all 200. Row 9's band runs −0.953551 to −0.823942 | `TestRowGroup13TheEighteenPointFourGap` |
| 14 | The type IV's parameters | m 3.254731, ν −0.897242, a 7.819013e-03 and λ −1.123894e-03, so moments exist only below order 5.509462 | `TestTheSampler::test_the_parameters` and `::test_moments_exist_only_below_order_5_51` |
| 15 | The uncapped optimum, and the seeds whose ruin leverage is below 20 | 22.295382 on the declared seed, band 16.622019 to 24.865122 across all 200. 42 of 200 seeds, against an exact chance of 0.149180, or 29.8 seeds. The 42 sit 2.414274 binomial standard errors above that, and 42 or more has an exact chance of 0.012871 | `TestRows3And4TheSimulatedOptimum::test_the_declared_seed_s_uncapped_optimum`, `TestRow5TheMinimumAndTheRuinLeverage::test_the_share_of_seeds_ruined_below_the_cap` and `TestWhatThePostMeasured::test_42_seeds_ruined_below_the_cap_sit_2_4_standard_errors_above_the_exact_chance` |
| 16 | Location 3426's CPPI at f with D = 0.5 | growth 0.002436, band 0.002321 to 0.002814, which is 0.255285 below the full account's at f·D. Account drawdown −0.495638, band −0.499628 to −0.489965, as in row 12 | `TestBesideTheReplication::test_cppi_as_described_costs_about_a_quarter_of_the_growth` |
| 17 | Script lines 37 and 65 to 80 on the saved returns, at the declared seed's f | growth at f·D 0.003421, drawdown −0.526211 at f / 1.4 and −0.396779 at f·D. Box 8.6's loop gives growth 0.003368 and drawdown −0.391438, and location 3426's CPPI growth 0.002673 and drawdown −0.332652 | `TestBesideTheReplication::test_the_script_s_historical_lines` |

The growth rates are pinned at six significant figures and quoted here at the
six decimals the book prints.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +5.4 | did not reproduce | Chan's own saved returns give 23.845328, the figure his `AUDCAD_unequal.m` prints. The vintage explanation is spent, and the section below says where the evidence points. |
| 2 | none, a type | reproduced | κ puts the moments in type IV, the type the book names. |
| 3 | +3, and +3.1 | did not reproduce | Neither of the book's figures lies inside the band of the 40 seeds whose ruin leverage is above Chan's 30.2, which runs from 22.969856 to 25.374220. That band replaced the declared one after the ensemble was seen, as the section below says. Under the declared band, 16.622019 to 24.865122 across all 200 seeds, both figures land and the verdict was reproduced with a gap, the seed. The gap is to the declared seed's uncapped optimum of 22.295382, the quantity the band reads. Its capped optimum is the cap of 20, as 158 of 200 seeds' are, and its ruin leverage of 23.217362 leaves it outside the 40. |
| 4 | none, a claim | reproduced | The Kelly of 23.845328 lies inside row 3's band, and inside the declared band too, so the simulated optimum is close to the Kelly on this file whichever band reads it. |
| 5 | −0.0100, and −7.0 | reproduced with a gap | A least draw at or below −0.0331 has a chance of 0.807083 among 100,000 draws, inside the 5 to 95 percent the declaration allows. The declared seed's least draw is deeper. The seed is the cause. |
| 6 | +5.3 | did not reproduce | The historical optimum on Chan's own returns is 23.721773. As in row 1, nothing is left to blame. |
| 7 | none, a claim | reproduced | The historical optimum is within 0.52 percent of the Kelly, inside the 1 percent criterion. |
| 8 | +0.008 | reproduced with a gap | −0.999 lies inside the band. The seed is the cause. |
| 9 | +0.092, outside its band | did not reproduce | −0.963 is deeper than the band's bottom of −0.922292. |
| 10 | +0.1, outside its band | did not reproduce | −0.5 is deeper than the band's bottom of −0.468433. The declared seed's leverage of 2.857143 is the cap over 7, where the book's 2.7 is 19.2 over 7. |
| 11 | +0.000740 and +0.000746, outside both bands | did not reproduce, and the claim holds | Both of the book's growth rates sit below their bands. The claim that the two are "very similar" holds, since Box 8.6's loop falls short of the full account by 1.4 percent on the declared seed and by less than 2 percent on all 200. |
| 12 | +0.0, and none for the claim | reproduced for the full account's 0.9 and for the claim on location 3426's CPPI. Did not reproduce for the claim on Box 8.6's loop | −0.871216 rounds to the book's −0.9 at its one decimal. It is the drawdown row 9 judges, because f·D is f / 2 when D is 0.5, and `TestRow12TheDrawdownCppiCaps::test_at_d_one_half_row_12_s_full_account_is_row_9` holds the two equal on every seed. So the −0.9 reproduced, rather than reproducing with a gap, because one decimal covers anything from −0.95 to −0.85. The book's −0.963 for the same quantity does not round to −0.9, so its two prints probably come from different runs. The book reports at least two, the 19 at location 3342 and the 19.2 at location 3399, and location 3438 gives its growth rates "in one simulation". The CPPI the prose describes stays above −0.5 on every seed, with a band of −0.499628 to −0.489965. The loop the book prints falls below −0.5 on every seed, so the code Chan shows does not do what the sentence before it says. |
| 13 | none | none, not a replication | No series matching Example 5.1's printed figures has a Kelly of 18.4, under any of the three compoundings. Moving the draws' mean to a Kelly of 18.4 lands rows 3, 8, 10 and 11, and lands row 3 under the declared band and the one row 3 now reads. |
| 14 | none | none, not a replication | Moments exist only below order 5.51, so a draw's sample skewness has infinite variance. That is why the tests check the tail and the draws' mean and std rather than a draw's third and fourth moments. |
| 15 | none | none, not a replication | The ruin leverage cut the capped search on 42 seeds. The exact chance gives 29.8. The count of 42 is 2.4 binomial standard errors above it, and a count of 42 or more has a chance of about 1.3 percent. |
| 16 | none | none, not a replication | Keeping the floor costs about a quarter of the growth, far more than the scripted loop's 1.4 percent. |
| 17 | none | none, not a replication | On the 612 historical returns at the declared seed's f of 20, neither CPPI form nor the full account at f·D comes near the floor. The deepest of the script's historical lines is the drawdown at f / 1.4. |

Row 3's gap is against each of the book's two figures, at its own precision,
and so are rows 5's and 11's. `TestRows3And4TheSimulatedOptimum::test_row_3_reads_the_declared_seed_s_uncapped_optimum`
and `TestTheReport::test_each_seeded_row_s_gap` hold every gap in the table
that a seed computes.

### Why the simulated rows are judged against an ensemble

Entry 2's
[Why no simulated number is pinned against the book](#why-no-simulated-number-is-pinned-against-the-book)
pins the closed form and lets the simulation only demonstrate, because the
coin flip has a closed form to pin. Most of Chapter 8's simulated figures have
none. Chan's figures come from one set of draws nobody holds, so no seed here
can be expected to equal them, and location 3399 says so. What can be asked is
whether his figure is one this method gives on his file, and the band answers
that. Each seeded figure is still pinned, so a change to the draw method
cannot move one inside the book's rounding unnoticed.

Row 5 is the one simulated row with a closed form. The least of 100,000
independent draws exceeds x with probability `(1 − F(x))^100000`, where F is
the fitted density integrated by `scipy.integrate.quad`, so row 5 lands
against that exact distribution rather than an ensemble. The same formula
checks the ensemble's count in row 15.

**Row 3's band changed after the ensemble was seen.** The issue declared the
uncapped optimum's band across all 200 seeds. Chan's 19.2 sits below his cap,
so his uncapped optimum was 19.2 as well. The declaration set the capped band
aside because, with most capped optima on the cap, its lower tail is made of
seeds whose low ruin leverage holds the optimum down, and the book's figure
could land there for that reason alone.

The uncapped band has the same lower tail. The growth rate falls to minus
infinity at the ruin leverage, so a seed with one deep draw has a low
uncapped optimum too, and the two bands' 5th percentiles are the same value,
16.622019. So the declared rule applied the objection to the capped band and
not to the uncapped band that shares its clamped seeds. Both of the book's
figures landed under it, and that verdict, reproduced with a gap, is kept in
row 3's Why cell.

Row 3 is now judged on the 40 seeds whose ruin leverage is above Chan's own
30.2, which are the seeds whose most negative draw is no deeper than his
−0.0331. The count is within four binomial standard errors of what the exact
distribution of the minimum gives. Their band runs from 22.969856 to
25.374220, and neither 19 nor 19.2 lands, so row 3 did not reproduce. Under
the ensemble with the Kelly moved to 18.4, the same rule keeps 39 seeds, whose
band of 17.514982 to 20.017014 holds both figures. The rule was chosen after
the bands were seen, so like every result here it is exploratory.
`TestRows3And4TheSimulatedOptimum::test_the_declared_band_shares_the_capped_band_s_lower_tail`,
`::test_the_band_row_3_reads` and `::test_row_3_follows_only_the_conditioned_band`
hold the shared tail, the band and the rule row 3 reads.

### What the book's 18.4 most likely came from

Rows 1 and 6 did not reproduce on the file the script names, so the entry owes
a reason. The evidence favors Chapter 8 having run on a different series of
returns, with a Kelly near 18.4, that neither mirror holds. It cannot tell when
or how that series differed from the saved file. That is an inference rather
than a held vintage, and row 13 is what it rests on.

1. **No series matching Example 5.1's printed figures reaches 18.4, under any
   of three ways its APR compounds.** The Kelly is the Sharpe ratio per day
   over the daily standard deviation, and an APR fixes that deviation once the
   Sharpe ratio is given and the compounding is chosen. The log growth leaves
   two deviations, one near 20 percent a day with a Kelly near 0.5, so the
   smaller is the one used. Across the rounding of the printed 1.6 and 11
   percent, the Kelly runs from 21.558894 to 26.757652 when the APR compounds
   the log growth m − σ²/2, which is what `implied_kelly` assumes. Compounding
   1 + m exactly moves the lower edge to 22.065999, and taking the APR as a
   simple 252·m moves it to 20.891304. So the edge depends on the convention,
   and none of the three reaches 18.4. Example 5.1's script,
   `AUDCAD_unequal.m`, compounds the daily returns themselves, which on the
   saved file gives 0.112410 against the log growth's 0.112426. At a Sharpe
   ratio of 1.6, a Kelly of 18.4 needs an APR of 13.9 to 14.9 percent across
   the three. So that series disagreed with Example 5.1's own printed figures
   as well as with the saved file.
2. **A Kelly near 18.4 lands most of the chapter's simulated figures.** Moving
   the draws' mean so that the Kelly is 18.4 moves only λ. On the same 200
   seeds it puts the median uncapped optimum at 18.470198 and lands rows 3,
   8, 10 and 11, where rows 3, 10 and 11 missed under the file's own mean.
   Row 3 lands under the rule it is now judged by, with 19 and 19.2 inside
   17.514982 to 20.017014 on the 39 seeds whose ruin leverage is above 30.2,
   and under the declared band too. Row 9's −0.963 still sits just past its
   band, which runs to −0.953551.

[Issue 360](https://github.com/l3a0/quantitative-trading/issues/360) also
records variants of the saved series tried in scratch runs, such as dropping
the zero days or using log returns, and none reached 18.4. No test here holds
them.

### What the entry concludes

Four things. The last was measured by the write-up after the run, and
`TestWhatThePostMeasured` in
[tests/test_monte_carlo_leverage.py](../tests/test_monte_carlo_leverage.py)
pins it, along with the 2.4 standard errors in row 15.

1. **The book's Kelly and historical optimum of 18.4 belong to a series nobody
   holds.** Chan's own saved returns give 23.845328 and 23.721773. Any series
   matching Example 5.1's printed Sharpe ratio and APR, with a daily swing
   under 10 percent, gives at least 21.558894 when the APR compounds the log
   growth, and at least 20.891304 under the simplest of the three compoundings
   row 13 tries. The claims the figures were printed to support still hold:
   the historical optimum is within 0.52 percent of the Kelly, and the Kelly
   lies inside the simulated optimum's band under either rule.
2. **The growth-optimal leverage brings a drawdown near total loss on this
   file too.** At the optimum the declared seed's drawdown is −0.991276, and
   the book's −0.999 lands in the band. At half the optimum the drawdown is
   still −0.871216, and at a seventh it is −0.416419. Those two and both
   growth rates miss their bands, and so does the simulated optimum under the
   rule chosen after the ensemble was seen. Row 13 ties all of them but row 9
   to the book's draws having a lower mean than this file's.
3. **Box 8.6's loop is not the CPPI location 3426 describes, and only the
   description keeps the floor.** The loop shrinks its leverage as the
   unlevered returns fall rather than as the account falls, so the account can
   fall further than D. It did on all 200 seeds, to −0.848088 on the declared
   one. The described scheme stays above −0.5 on every seed, at a cost of
   about a quarter of the growth, 0.255285 on the declared seed. So the book's
   pairing of a growth cost near 1.6 percent with a drawdown "by design" under
   0.5 holds for neither form here. The loop gives the first and not the
   second, and the scheme gives the second and not the first.
4. **The draws reach deeper than the history because there are more of
   them, and that decides where the Kelly stands.** The least of the 612
   saved returns is −0.022031, a ruin leverage of 45.390502, and the declared
   seed's least draw of −0.043071 is 1.9550 times as deep. The fit's left
   tail is not what makes the difference. The least of 612 draws from it, the
   backtest's length, is at or below −0.022031 with a chance of only
   0.091663, so the fit's tail is thinner than the history's, and the extra
   depth comes from drawing about 163 times as many returns. The declared
   seed's ruin leverage of 23.217362 is below the Kelly of 23.845328, so at
   the Kelly one draw loses everything, and the same holds on 78 of the 200
   seeds. The 30 seeds whose uncapped optimum is at or below 19.2 all have a
   ruin leverage below 20, and a seed sits on the cap exactly when its ruin
   leverage is 20 or more. On the saved returns the drawdown is −0.737560 at
   the historical optimum and −0.739733 at the Kelly, against −0.991276 on
   the draws at the optimum. Part of that gap is length alone. The deepest
   drawdown can only grow as a path gets longer, so at the same daily risk a
   path of 100,000 days is all but certain to reach deeper than one of 612.
   Measured after the run.

### What this entry cannot say

Four things.

**Which Pearson type `pearsrnd` drew from.** The type IV choice is inferred
from the standard criterion and the book's "type is 4", as in Entry 37.

**What Chan's `ret` was.** Row 13 says a series with a Kelly near 18.4 lands
most of the simulated figures and that no series matching Example 5.1 has
one. It cannot recover that series, and the issue scopes a search for it out.

**Whether either leverage is safe to trade.** Every figure is computed on
returns drawn to match 612 days of one strategy, or on those days themselves.
Location 3417 notes that simulated returns miss serial correlation, and
nothing here measures it.

**Which band row 3 belongs against.** The declared band lands both of the
book's optima and the band chosen after the ensemble was seen lands neither.
The second rests on Chan's printed ruin leverage of 30.2, and nothing here
can say more about his draws than that one figure.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/monte-carlo-leverage-lessons.md](../blog/monte-carlo-leverage-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.monte_carlo_leverage_figures` redraws.
[blog/aud-cad-johansen-lessons.md](../blog/aud-cad-johansen-lessons.md) moves
with it too, since its Lesson 1 states what
`TestRowGroup13TheEighteenPointFourGap` found.

The post also carries two whiteboard sketches, added in the first round of its
review before publishing. Both draw on the declared seed, and the first also
on Chan's saved returns.

1. **The least of many draws goes deeper**, in Lesson 4. Three rows of dots on
   one return scale show every value below −0.012 among Chan's 612 saved
   returns, the first 612 draws and all 100,000. The saved returns' least,
   −0.022031, is a dashed line through the rows. The first 612 draws stop
   short of it, and the least of 612 draws from the fit reaches it with a
   chance of 0.091663. The least of all 100,000, −0.043071, is 1.9550 times
   as deep, with about 163 times as many draws.
2. **Box 8.6's loop barely cuts its leverage**, in Lesson 5. Each form's
   leverage on its account, one point a day, runs from the day after the
   account's high on day 169 to day 303, the loop's first day below −0.5.
   Both start at f·D, 10. The loop ends at 9.47, 10 times one plus the
   unlevered returns' drawdown through day 302, 0.946693, with its account's
   drawdown at −0.504523 on day 303. The scheme on p. 263 ends at 3.46, with
   its account's drawdown at −0.407605.

A change to those figures moves the sketches too, and
`uv run python -m chan.monte_carlo_leverage_whiteboard` redraws both through
the same `read_returns`, `pearson_fit`, `draws`, `optimal_leverage`, CPPI
functions, `account_drawdowns` and `minimum_below`.

## Entry 44: the Khandani-Lo reversal on the S&P 600, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 2137 for the
explanation and location 2236, at the end of Example 3.8 on p. 78, for the
exercise. Shipped under
[issue 249](https://github.com/l3a0/quantitative-trading/issues/249).

This entry is not a replication. Chan explains the reversal's collapse on the
S&P 500, from Khandani and Lo's 4.47 to his 0.25, by saying "most of the
returns are generated by small and microcap stocks". He then leaves rerunning
the strategy on the S&P 400 and S&P 600 as an exercise and prints no figure
for either. So the entry carries a finding rather than a verdict, and its
tables drop the published-figure, gap and verdict columns, as Entry 5's do.
`### Rows that are not replications` above says why the route that lets a
stated claim carry a verdict does not reach it.

Nine rows, all derivable from
[tests/test_khandani_lo_small_caps.py](../tests/test_khandani_lo_small_caps.py).
The module is `chan.khandani_lo_small_caps`, and its S&P 500 side lands on the
figures Entries 8 and 10 report, which `TestTheLargeCapSide` holds.

**Before costs the reversal earns more on the S&P 600 than on the S&P 500 at
both prices, so the reading points the way Chan says.** On the closes it earns
3.4086 against 0.2510, a gap of +3.1576, which is more than three times its
standard error. On the opens it earns 5.3052 against 4.4202, a gap of
+0.8850, which is smaller than its standard error. So one year of the closes
can tell the two universes apart and one year of the opens cannot.

**The comparison was declared before any S&P 600 figure was computed**, in
[the declaration comment on issue 249](https://github.com/l3a0/quantitative-trading/issues/249#issuecomment-6104832067).
It fixes four things.

1. **What each figure is read against.** Every S&P 600 figure is read
   against the S&P 500 figure with the same price, the same cost treatment and
   the same specification, which gives six pairs.
2. **What counts as pointing the way Chan says.** Before costs, the S&P 600
   higher at both prices reads as pointing the way Chan says, higher at one
   only as mixed, and higher at neither as pointing against it. The before-cost
   figure is the primary reading because the explanation is about where the
   returns come from.
3. **How big a gap must be.** Each before-cost gap is read against the
   standard error of a difference between two Sharpe ratios on the same days,
   Memmel's (2003) correction of Jobson and Korkie (1981). A gap more than
   twice its standard error reads as larger than one year's noise. The size
   reading adds no verdict.
4. **Khandani and Lo's 4.47.** The entry prints it beside the result and
   judges nothing against it, because their universe and window are not this
   file's.

The declaration's second reason does not hold. Chan dates their figure to
2006 too, at location 2099, so only the universe differs.

Entry 50 runs the S&P 400 half under
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303), with the
same declaration, which already says how a third universe extends it: before
costs the S&P 500 below the S&P 400 below the S&P 600 at both prices.

Every row reads the same two vintages, window and specification, so they are
stated once here.

1. **The vintages.** The S&P 600 side is `ijr_20080114/`, the 600 stocks of
   Chan's `IJR_20080114.mat`, saved 2008-01-15. `chan.series.load_panel` reads
   its closes, and the same call with `field="Open"` reads its opens. It is the
   S&P 600 as it stood on 2008-01-14, carried backwards, and 592 of its stocks
   are priced on the window's first day and 594 on its last. The S&P 500 side
   is Entry 8's `spx_20071123/`, the index as it stood on 2007-11-23. The two
   files share no symbol. **Every figure here is about survivors**, on both
   sides.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days, the same days
   in both files, which `TestTheCalendars` holds. That is what lets the size
   reading pair the two daily profit series day by day.
3. **The specification.** Rule B, `chan.khandani_lo.reversal` run unchanged.
   On the closes it is Example 3.7's MATLAB, and on the opens it is Example
   3.8's rule B. The run leaves out rule A, Chan's Python notebook, because its
   forward-fill reads a gap as one day's move. The cost is 5 basis points on
   each side of a change in weight, and the Sharpe ratio is √252 times the
   mean over the standard deviation with no risk-free rate. Each run gives
   Entry 8's three figures: before costs, after costs with Chan's two quirks
   kept, and after costs with the first day charged.

Every result here is **EXPLORATORY**. The run applies a rule Chan published,
unchanged, to the small-cap stocks his exercise names, so it says which way
the gap points on one year of survivors and how it compares with that year's
noise. It confirms nothing about Chan's explanation. A reading that points his
way earns a registered test on data the run has not seen.

### What the book stated

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The S&P 600 on the closes, before costs | nothing, the exercise asks for the run and prints no figure | location 2236, p. 78 |
| 2 to 6 | The S&P 600's other five figures | nothing | n/a |
| 7 and 8 | Each before-cost gap against its standard error | nothing | n/a |
| 9 | Where the returns come from | "most of the returns are generated by small and microcap stocks", a claim rather than a figure | Kindle location 2137 |

Khandani and Lo's 4.47 for 2006, at location 2099, takes no row. It was
computed on their own universe, the set of stocks they tested, so the report
prints it and the entry judges nothing against it.

### What this repo computed

The gap is the S&P 600's figure less the S&P 500's.

| # | Price and specification | S&P 600 | S&P 500 | Gap | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | closes, before costs | 3.4086 | 0.2510 | +3.1576 | `TestTheSmallCapFigures::test_closes` and `TestTheSixGaps::test_the_gap` |
| 2 | closes, after costs, first day uncharged and its NaN counted as 0 | −0.3702 | −3.1884 | +2.8181 | the same |
| 3 | closes, after costs, first day charged | −0.3255 | −3.2337 | +2.9081 | the same |
| 4 | opens, before costs | 5.3052 | 4.4202 | +0.8850 | `TestTheSmallCapFigures::test_opens` and `TestTheSixGaps::test_the_gap` |
| 5 | opens, after costs, first day uncharged and its NaN counted as 0 | 2.0147 | 0.7834 | +1.2313 | the same |
| 6 | opens, after costs, first day charged | 2.0257 | 0.8293 | +1.1964 | the same |

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 7 | row 1's gap against Memmel's standard error | correlation 0.5258, standard error 0.9872, z +3.1987, beyond one year's noise | `TestTheSizeReading::test_closes` |
| 8 | row 4's gap against Memmel's standard error | correlation 0.3663, standard error 1.1640, z +0.7603, within one year's noise | `TestTheSizeReading::test_opens` |
| 9 | rows 1 and 4 read against the declaration | the S&P 600 higher at both prices, so pointing the way Chan says | `TestTheReading::test_it_points_the_way_chan_says` |

The S&P 500 column is Entry 8's rows 1 to 3 and Entry 10's rows 6 to 8, and
`TestTheLargeCapSide` holds that this module's runs land on them.
`TestTheSizeReading::test_the_gaps_ratios_are_the_runs_own_figures_exactly`
holds that the two ratios the size reading compares are rows 1 and 4's
figures to the last bit, rather than a second computation near them.

### What each row says

| # | Why it is here |
| --- | --- |
| 1 | The primary reading on the closes, and the larger of the two gaps. |
| 2 | After Chan's costs the small caps still lose on the closes, by much less than the large caps do. |
| 3 | Charging the first day moves the figure up here, as it does on the S&P 500's opens, and leaves it below 0. |
| 4 | The primary reading on the opens. Trading at the open lifts both universes, and the gap between them is smaller than on the closes. |
| 5 | Rows 5 and 6 are the S&P 600's opens after costs, read against the S&P 500's. The run charges both universes the same 5 basis points, so these rows flatter the small caps. |
| 6 | The same, with the first day charged. |
| 7 | The closes' gap is more than three times its standard error, so one year can tell the two universes apart on the closes. |
| 8 | The opens' gap is less than one standard error, so one year cannot tell them apart on the opens. |
| 9 | The declared direction reading. It rests on rows 1 and 4 only, and row 8 says one of the two is within noise. |

### The two flagged days

`chan.series.scale_breaks` flags a day when a stock's close moves past the
factor-of-1.6 bound, meaning by more than a factor of 1.6 from the day before.
On each member's own closes it flags two days in 2006, and both were
classified before any strategy figure was computed, from each member's own
prices and from outside evidence, in
[the classification comment on issue 249](https://github.com/l3a0/quantitative-trading/issues/249#issuecomment-6104857463).
The declaration's rule was that a real traded move stays in and an unadjusted
split or a splice of two companies is set to NaN. Both are earnings warnings
recorded at the prices that traded, so neither is excluded, and the run
reports one set of figures rather than one with the exclusion and one without.

1. **BCSI on 2006-02-06** closes at 12.37 against 20.165 the day before, a
   ratio of 0.6134. Blue Coat had preannounced revenue and earnings well below
   expectations, which the Motley Fool's
   ["Blue Coat Is All Wet"](https://www.fool.com/investing/small-cap/2006/02/06/blue-coat-is-all-wet.aspx)
   reported that day. The file stands on one split-adjusted scale on both
   sides of the day, and the price never returned to its old level.
2. **SCUR on 2006-07-12** closes at 4.99 against 8.07, a ratio of 0.6183.
   Secure Computing cut its quarterly revenue outlook after the close on
   2006-07-11, and
   [TechPartner News reported on 2006-07-12](https://www.techpartner.news/news/security-vendor-blames-world-cup-for-dramatic-sales-drop-42065)
   a fall of nearly 40 per cent in after-hours trading. No source found states
   the closing price, so the match is on date, size and direction.

Both fall just past the bound on the closes and inside it on the opens.
Rule B weights each one. Its return on the flagged day is finite and sets that
day's weight, which earns the next day's return, and
`TestTheFlaggedDaysAreKept` holds both.

The module does not call the scale-break guard,
`chan.series.refuse_window_crossing_a_break`, and its docstring says why. Over
each member's own closes the guard refuses the window on exactly these two
days, and over each member's own opens it passes. Refusing would withhold the
run over two moves that traded. `TestTheScaleBreakDecision` runs both, and the
comment block above `FLAGGED_IN_CHANS_MAT_FILES` in
`tests/test_scale_breaks.py` records the decision. On the S&P 500 file the
guard passes over each member's own rows, which is why Entry 8 does not call
it. That reason does not hold here, so this entry gives its own.

### The stocks with a missing price

Eight of the 600 stocks miss a price somewhere in 2006, and
`TestTheMissingPrices` holds each group.

1. **Six have no 2006 price at all.** CENTA, FOR, GFG, PCX, PMC and ZEP.
   PMC holds two companies under one symbol, as WYN does on the S&P 500
   file, with an 851-day gap that spans the whole year. It carries a weight of
   0 on every day of 2006.
2. **Two start trading during the year.** CROX on 2006-02-08 and TRX.B on
   2006-03-31. Neither has a gap after its first price.

Rule B already weights a return that is not finite at 0, so none of these
gaps reaches a weight. Handed the panel's columns rather than each member's
own rows, the guard refuses on all eight. It refuses because it cannot read
the days beside a gap, not because it found a change of scale.

### What the size reading says

The standard error answers one question: could one year of daily profits
tell two universes' Sharpe ratios apart? With daily Sharpe ratios s₁ and s₂,
their series' correlation ρ and T days, Memmel's variance of the difference
is

```text
Var(ŝ₁ − ŝ₂) = (1/T) · [2(1 − ρ) + ½(s₁² + s₂² − 2 s₁ s₂ ρ²)]
```

The correlation matters because both reversals earn on the same market's
moves. The two daily profit series correlate at 0.5258 on the closes and
0.3663 on the opens, and a gap between positively correlated series has a
smaller standard error than one between independent series. A Sharpe ratio
does not change when a book is scaled, so the two books need no matching,
unlike Entry 4's test of a mean difference.

The price is the formula's assumption. It treats each day's profit as
independent of the day before and normal. Neither universe's daily profits are
normal, and the S&P 500's are not independent from day to day either. So the
standard errors are approximations, and nothing here measures how far off they
are. The closes' gap sits at z +3.1987, past the declared
line of 2 standard errors, and the opens' gap at z +0.7603 sits inside it.

### What the entry concludes

Five things, and the first is the finding. The write-up measured the last two
after the run, and `TestWhatThePostMeasured` in
[tests/test_khandani_lo_small_caps.py](../tests/test_khandani_lo_small_caps.py)
pins them.

1. **On Chan's S&P 600 file the reversal earns more before costs than on his
   S&P 500 file, at both prices.** That is the direction Chan's explanation
   predicts, under the reading declared before the run.
2. **One year separates the universes on the closes and not on the opens.**
   The closes' gap is more than three times its standard error, and the
   opens' gap is smaller than its standard error. So the direction on the
   opens is a reading of a gap that one year cannot resolve.
3. **After costs the small caps keep more, on a cost that flatters them.**
   Every after-cost gap is positive. The run charges both universes the same
   5 basis points, so these figures overstate what a trader in small caps
   would keep relative to one in large caps.
4. **Every book trades about the same, so the profit decides what costs
   leave.** On the specification with the first day charged, the four books
   trade between 1.4505 and 1.4729 times their mean position a day and pay
   between 7.2525 and 7.3644 basis points of it. The S&P 600's closes earn
   6.7197 basis points a day, so their cost is 1.0945 times their profit,
   against 13.7453 for the S&P 500's closes. The S&P 600's opens earn 11.8569
   and the S&P 500's 8.9815. The cost a side at which each book breaks even
   is 4.57 basis points for the S&P 600's closes, 8.05 for its opens, 0.36
   for the S&P 500's closes and 6.14 for its opens.
5. **The correlation narrows the closes' standard error, and the open lifts
   the S&P 500 far more.** With the correlation set to 0, Memmel's standard
   error on the closes would be 1.4252 rather than 0.9872, and the gap would
   be 2.2155 standard errors. The term 2(1 − ρ) carries 0.98 of the formula's
   bracket on the closes and 0.94 on the opens, because a daily Sharpe ratio
   is small. The open lifts the S&P 500's figure before costs by 4.1693 and
   the S&P 600's by 1.8966, which is why the gap shrinks at the open.

### What this entry cannot say

Five things.

**Anything about microcaps.** Chan's sentence names "small and microcap
stocks". The S&P 600 adds a company only above a minimum size, but it does
not drop a member just because it later shrank, so some of its members may
have sat below the line usually drawn for microcaps. The file holds prices and
volumes but no shares outstanding or market values, so nothing here measures
how many. The finding says the S&P 600's small caps carry more of the
reversal's return than the S&P 500's large caps, and nothing about microcaps
or the stocks outside the index.

**What survivorship did.** Both files are survivors, the S&P 600 as of
2008-01-14 and the S&P 500 as of 2007-11-23. A small cap that failed in 2006
or 2007 is missing from the first file, and a reversal buys exactly the stocks
that fell. Neither the size nor the sign of the effect is measured.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) and
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213) are where
survivorship is priced.

**Whether the gap holds in another year.** The run reads 2006 only, the year
Chan's S&P 500 figures came from, and the standard error says what one year
can resolve. A gap that points the same way in other years would be a
different and stronger result.

**What a trader in small caps would keep after costs.** The run charges both
universes 5 basis points a side, while small caps cost more to trade. So the
after-cost gaps flatter the S&P 600, and nothing here prices by how much.

**Whether Khandani and Lo's 4.47 came from small caps.** Their figure is for
2006 too, but it comes from their own universe, which is not this file's. So
the S&P 600 reaching their figure or not says nothing about where their
returns came from. The report prints 4.47 and judges
it against nothing.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/khandani-lo-small-caps-lessons.md](../blog/khandani-lo-small-caps-lessons.md)
moves with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.khandani_lo_small_caps_figures` redraws,
and its two whiteboard sketches, which
`uv run python -m chan.khandani_lo_small_caps_whiteboard` redraws: one in
Lesson 3 on how the correlation narrows the closes' standard error, and one in
Lesson 6 on the three indexes' order at the closes and the opens, which also
draws Entry 50's S&P 400 figures.

## Entry 45: a levered low-beta portfolio against an unlevered high-beta one, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 4684, 4700
and 4709. Shipped under
[issue 275](https://github.com/l3a0/quantitative-trading/issues/275). Every
location is the revised edition's and is in
[research/book-notes/quantitative-trading.md](../research/book-notes/quantitative-trading.md).

Nine rows, all derivable from
[tests/test_low_beta_leverage.py](../tests/test_low_beta_leverage.py).

**Contradicted by ruin.** "Levered to the high-beta portfolio's beta, the
low-beta portfolio lost more than its capital in the month ending 2001-06-29,
at a leverage of 58.0262, so its compounded growth is unbounded below and the
unlevered high-beta portfolio out-compounded it." That sentence is the
criterion's fixed wording. Chan's chapter summary at location 4709 says that
"Holding a highly leveraged portfolio of low-beta stocks should generate
higher long-term compounded growth than holding an unleveraged portfolio of
high-beta stocks." Location 4684 gives the reason. Levered up to the
high-beta portfolio's beta, a low-beta portfolio earns the same average return
under the Fama-French model, and "a portfolio that consists of low-beta stocks
generally has lower risk and thus a higher Sharpe ratio". At the Kelly
leverage, growth goes with the Sharpe ratio squared, so the lower-risk side
should compound faster. On Chan's own S&P 500 file the rule, read at location
4684's beta match, does not hold. The low fifth's mean beta at formation fell
as low as 0.0280, so matching the high fifth's beta took a leverage of up to
69.0762, and two holding months lost more than the capital. The low fifth's
Sharpe ratio is 1.0132 against the high fifth's 0.4457, a point estimate that
nothing here tests and that decides nothing.

One row is a claim and eight are not replications. Row 1 takes the claim route
`### Rows that are not replications` describes. Rows 2 to 9 are the figures
the issue reports beside the verdict, which decide nothing.

Every rule was fixed on
[issue 275](https://github.com/l3a0/quantitative-trading/issues/275) on
2026-10-11, before any beta or return was computed, with the one exception the
label paragraph below names. Five of the rules carry the result, so they are
stated here.

1. **The vintages.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, saved 2007-11-24, read through `chan.series.load_panel`.
   `spy_chan.csv`, the adjusted-close column of his `example6_2.xls`, saved
   2008-01-29. FRED's TB3MS, downloaded 2026-09-30.
   [data/README.md](../data/README.md) says what each holds.
2. **The beta.** The panel is cut to the 2,011 days it shares with SPY, which
   drops 13 rows on days the exchange was closed. At each of its 96 month-ends
   a stock's beta is the slope, with an intercept, of its daily return over
   the bill on SPY's, over the 252 daily returns ending there. A stock needs
   200 of those days with both returns present.
3. **The portfolios.** Among the stocks with a beta and a close at both ends
   of the coming month, the lowest fifth by beta and the highest fifth form two
   equally weighted portfolios, ties broken by symbol, held one month and
   re-formed every month-end. The first formation is 2000-11-30, the first
   month-end with 252 returns behind it, so the holding months run from
   December 2000 to October 2007, 83 of them.
4. **The leverage.** At each formation the low portfolio is levered by k, the
   high group's mean beta over the low group's. That is location 4684's match,
   and it is known before the month it applies to. The levered month returns
   rf + k × (r_low − rf), where rf is the holding month's TB3MS over 12.
   Borrowing costs the bill rate, and no trading cost is charged.
5. **The criterion.** The statistic is the Newey-West t of d, the monthly
   difference ln(1 + r_levered low) − ln(1 + r_high), tested one-sided at
   5 percent against 1.645. The claim holds when the mean of d is above 0 and
   t is at least 1.645. It is contradicted when the mean is below 0 and t is at
   most −1.645, and anything else is not decided. Under the amendment named
   below, a levered month returning −1 or less contradicts it by ruin, and
   then neither t nor the detectable gap is computed.

**Every figure drawn from the stocks is about survivors.** The panel is the
S&P 500 as it stood on 2007-11-23, carried backwards, so a stock that left the
index before then is in neither portfolio. Which side that flatters is not
measured here. Leaving out high-beta stocks that fell out of the index would
flatter the high side and work against the claim, and that is a hypothesis
rather than a finding.

Row 1 is **registered**, under the issue's amendment of 2026-10-11. The plan
and its criterion were written on the issue before any number was computed.
The plan left one case undefined, because ln(1 + r) needs r above −1. The
build found two such months, June and September 2001, and stopped before
computing anything the criterion reads. The owner then ruled that ruin reads
as the claim contradicted, and the amendment lists what had been seen by then:
the calendar, the leverage path, the two ruined months, and both groups'
unlevered returns for the first eight formations. So the ruin case and its
wording were settled after its first instance was visible. Registration rules
out a specification tuned on this panel by this repo. It does not make the
span a holdout, because Chan's premise comes from "empirical studies" of past
prices, and 2000 to 2007 were past prices by the time the book printed the
claim. Rows 2 to 9 are **exploratory**. The plan declared them, and each is a
point estimate that nothing tests.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | a highly leveraged low-beta portfolio out-compounds an unleveraged high-beta one | the rule, with no figure | location 4709, the leverage matched to beta at location 4684 |
| 2 | a low-beta portfolio has a higher Sharpe ratio | the premise, from "empirical studies", with no figure | location 4684 |
| 3 to 9 | the realised growth, the leverage path, the realised betas, the Kelly reading, the counts, the flagged stock-months and the calendar | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | the claim: any levered month at −1 or below, else the Newey-West t of d against 1.645 | two ruined months. Formed 2001-05-31, June 2001 returns −2.5053 at k 58.0262, on a low-fifth month of −0.0403, the sixth-worst of its 83. Formed 2001-08-31, September 2001 returns −1.1278 at k 31.5098. No t and no detectable gap | `TestTheVerdicts::test_the_claim_is_contradicted_by_ruin`, `::test_two_months_are_ruined`, `::test_june_2001s_low_fifth_returned_minus_0_0403`, `::test_the_wording_names_the_first_ruined_month` and `::test_neither_t_nor_y_is_computed` |
| 2 | each portfolio's Sharpe ratio on its monthly return over the bill, times √12. The levered low's reads all 83 months, each as if freshly funded | levered low 0.2836, low 1.0132, high 0.4457 | `TestTheFigures::test_the_low_and_high_sharpe_ratios` and `::test_the_levered_lows_beta_and_sharpe_over_all_83_months` |
| 3 | realised compounded growth, 12 times the mean monthly log return | levered low ruin, low 0.1254, high 0.1183, SPY 0.0379 | `TestTheFigures::test_each_series_realised_growth` |
| 4 | k over the 83 formations, and each group's mean beta | k mean 7.8414, from 2.1826 to 69.0762, the highest formed 2001-04-30. Low group 0.0280 to 0.6745, high group 1.4625 to 1.9532 | `TestTheFigures::test_the_leverage_path` and `::test_the_groups_mean_betas` |
| 5 | each series' realised beta, the slope of its monthly return over the bill on SPY's. The levered low's reads all 83 months, each as if freshly funded | levered low 3.4596, low 0.4292, high 2.0671, SPY 1 | `TestTheFigures::test_the_realised_betas` and `::test_the_levered_lows_beta_and_sharpe_over_all_83_months` |
| 6 | location 4709's Kelly reading, look-ahead: the low portfolio's full-sample m / s², and the Gaussian growth r + S²/2 there | leverage 9.9884, Gaussian growth 0.0283 + 0.5132 = 0.5415, against the high portfolio's realised 0.1183 | `TestTheFigures::test_the_kelly_reading` |
| 7 | eligible stocks and each portfolio's size, fewest and most over the 83 formations. The run prints every formation's row | 444 to 495 eligible, each portfolio 88 to 99, 7,908 stock-months each | `TestTheFigures::test_444_to_495_stocks_are_eligible`, `::test_each_portfolio_holds_88_to_99`, `::test_every_formations_eligible_count` and `::test_formation_table_rows` |
| 8 | stock-months with a scale-break flag between the beta window's first return and the holding month's end | 36 low and 186 high. The file flags 43 closes in 34 stocks | `TestTheScaleBreakDecision::test_36_low_and_186_high_stock_months_carry_a_flag` and `::test_43_flagged_days_in_34_stocks` |
| 9 | the calendar | 2,011 of 2,024 rows shared with SPY, 96 month-ends from 1999-11-30 to 2007-10-31, formations 2000-11-30 to 2007-09-28, 83 holding months | `TestTheCalendar::test_the_cut_drops_13_of_2024_rows`, `::test_96_month_ends_on_the_cut_calendar` and `::test_83_formations_from_2000_11_30` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | did not reproduce | Contradicted by ruin, the outcome the amendment of 2026-10-11 adds and maps to this value. The levered low-beta portfolio lost 2.5053 times its capital in June 2001, so it held nothing afterwards and its compounded growth is unbounded below. The registered rules left a month below −1 undefined, and the owner ruled this case after its first instance was visible. The statistic was never computed, so nothing here says what it would have read without the ruin. The panel holds only survivors. |
| 2 | none, not a replication | The low fifth's Sharpe ratio is 1.0132 and the high fifth's 0.4457. Nothing tests the difference, so it neither confirms nor refutes location 4684's premise, and it decides nothing because the claim is about growth. The levered low's 0.2836 reads each month's levered return as if freshly funded, which is how the plan defines the series and not what an investor ruined in June 2001 held. |
| 3 | none, not a replication | Unlevered, the low fifth compounded at 0.1254 a year and the high fifth at 0.1183, both above SPY's 0.0379. Nothing tests either gap, and the panel holds only survivors, so neither is a finding about either fifth. |
| 4 | none, not a replication | k is large because the low group's mean beta falls to 0.0280 while the high group's never falls below 1.4625. |
| 5 | none, not a replication | The levered low's realised beta of 3.4596 is above the high fifth's 2.0671, so after the fact the match overshot the beta it aimed at. It reads all 83 months as if each were freshly funded. The low fifth's 0.4292 sits inside the range its formations gave, 0.0280 to 0.6745. SPY's is 1 by construction. |
| 6 | none, not a replication | Look-ahead. The Kelly leverage here is computed from the whole sample, and at the full-sample Kelly leverage the Gaussian growth formula gives any portfolio at least the growth it gives the same portfolio unlevered. The 0.5415 is the Gaussian growth r + S²/2, a formula on the sample's moments, and no portfolio realised it. The reading is reported because location 4684's growth argument rests on it, and it decides nothing. |
| 7 | none, not a replication | Every formation fills both fifths, so the refusal for an empty portfolio never fires. |
| 8 | none, not a replication | No window is refused, as `tests/test_scale_breaks.py` records. The high fifth holds 186 flagged stock-months and the low fifth 36. |
| 9 | none, not a replication | The first formation is the date the plan expected, so the 83 months are the plan's. |

### What the entry concludes

Three things, and the first is the verdict. The third adds figures the
write-up measured after the run, which `TestWhatThePostMeasured` in
[tests/test_low_beta_leverage.py](../tests/test_low_beta_leverage.py) pins.
The run itself pinned June 2001's −0.0403 and its rank.

1. **Location 4684's beta match ruins the levered portfolio on this file.**
   Levered to the high fifth's beta, the low fifth lost more than its capital
   in June 2001, and a fresh stake levered by the same rule would have lost
   more than its capital again in September 2001. That is the amendment's
   Contradicted by ruin, and it maps to `did not reproduce`.
2. **The rule, read at location 4684's beta match, does not hold, and the
   leverage is what breaks it.** The match asks for a leverage of up to
   69.0762 when the low fifth's beta at formation is near zero. The low
   fifth's Sharpe ratio of 1.0132 against the high fifth's 0.4457, and its
   unlevered growth of 0.1254 against 0.1183, are untested point estimates
   that decide nothing.
3. **An ordinary month did it.** A levered month is ruined when the low
   fifth's return is at or below rf − (1 + rf) / k. In June 2001 that line
   sat at −0.0144, with a bill rate of 0.0029 and k at 58.0262, and the low
   fifth returned −0.0403, the sixth-worst of its 83 months. In September
   2001 the line sat at −0.0296 against a return of −0.0337, the
   eighth-worst. Of the 83 months, 13 fell at or below June's line, and a
   normal distribution with the low fifth's monthly mean of 0.0109 and
   standard deviation of 0.0292 gives 0.1931 for a month at or below that
   line. The smallest leverage that ruins June is 23.2017 to four places, and
   for September 27.9461. So location 4700's advice against too much leverage holds,
   while its reason, the fat tails, is not what the run shows. The low
   fifth's beta at formation was below 0.05 at four formations, 2001-03-30
   to 2001-06-29, and k was above 20 at eight, 2001-02-28 to 2001-09-28.
   Measured after the run, so exploratory, and it decides nothing.

### What this entry cannot say

Five things.

**What the test statistic would have read.** The ruin ends the comparison in
June 2001, so the Newey-West t and the detectable gap were never computed. A
leverage rule that avoided the ruin, such as a cap, is a different
specification. On this file a cap is exploratory, because the ruin had been
seen, and only on the holdout could one be registered.
[Issue 516](https://github.com/l3a0/quantitative-trading/issues/516) tests the
rule here at leverage a broker would lend, as an exploratory run, and Entry 48
carries it.

**Whether fat tails are the cause.** Location 4700 carries the caveat: "one
should be quite wary of using too much leverage on normally low-beta stocks",
because returns have fat tails. The low fifth returned −0.0403 in June 2001,
the sixth-worst of its 83 months, and a leverage of 58.0262 turned it into
ruin. Whether the near-zero betas or the fat tails did more of the damage is
not measured here.

**What survivorship does to either side.** The panel lacks the stocks that
left the index before 2007-11-23. Leaving out the high-beta stocks that fell
out of it would flatter the high side, which works against the claim, and that
is a hypothesis rather than a finding.

**Whether the claim holds after the book.** The point-in-time S&P 500 that
[issue 373](https://github.com/l3a0/quantitative-trading/issues/373) built,
IVV's members at each month-end from 2008-12 to 2026-08, is a holdout with a
smaller survivor gap than this file's. The plan chose it before any number
here was computed, and
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526) runs
this entry's registered specification on it, with the changes that panel
forces and under both amendments of 2026-10-11, this entry's and its own.
Entry 49 carries that result.
Its closes sit only in the owner's archive, so its figure pins run only where
the archive is.

**What the model's half of the argument says.** Location 4684's equal average
returns need market capitalisation and book value at each date, which
[issue 273](https://github.com/l3a0/quantitative-trading/issues/273) carries.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/levered-low-beta-lessons.md](../blog/levered-low-beta-lessons.md) moves
with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.low_beta_leverage_figures` redraws.

The post also carries two whiteboard sketches in Lesson 3, added in the first
round of its review before publishing.

1. **The ruin line.** Two levered lines turn on the point (rf, rf), with rf at
   0.0029. The leverage of 23.2017 that just ruins June 2001 meets −1 at June's
   low-fifth return of −0.0403. June's k of 58.0262 is steeper and meets −1 at
   −0.0144, so a smaller loss ruins it, and June's month sits on it at
   −2.5053.
2. **Thirteen of 83 months past June's line.** A bell curve with the low
   fifth's mean of 0.0109 and standard deviation of 0.0292 puts 0.1931 of its
   months at or below −0.0144, and a strip of the 83 monthly returns shows 13
   there.

A change to those figures moves the sketches too, and
`uv run python -m chan.levered_low_beta_whiteboard` redraws both through the
same `read_sources` and `build_portfolios`.

## Entry 46: post-earnings drift on EDGAR's calendar and the archive's prices, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 7.2, the example Entry 12 reproduces.
Shipped under [issue 251](https://github.com/l3a0/quantitative-trading/issues/251).
Entry 12 says Chan's figures reproduce from his own files. This entry asks
what the same rule gives when the calendar comes from public filings and the
prices from another vendor, and which of four differences moves the figure.

Thirty-eight rows. Rows 15, 16 and 38 count the filings and are derivable
from [tests/test_earnings_filings.py](../tests/test_earnings_filings.py), and
every other row from [tests/test_pead_rerun.py](../tests/test_pead_rerun.py).
No row reproduces a published number, so the entry carries no verdict column.
Rows 28 to 38 were measured after the runs' figures were seen, in the review
of the pull request that shipped them. They decide nothing, and the section
holding them says so.

Every result here is **exploratory**. The plan audit on the issue measured,
on Chan's flags, how much of the return each vendor could serve before the
comparison was registered, so part of the sample was already spent. R5, the
calendar nearest Chan's, reads what a trader did not have before the open, so
no figure on it is a tradable one.

Every row reads the same vintages and specification, so both are stated once
here.

1. **The vintages and the record.**
   1. Chan's `inputdataohlcdaily_stocks_20120424/` and `earnannfile/`, read as
      Entry 12 reads them.
   2. `research/filings/earnings/`, written on 2026-10-10. `tickers.csv` maps
      each of the 497 tickers to a CIK and to an archive series, with the
      route and the check behind each. `index.jsonl` holds the 2,930 original
      Item 2.02 8-Ks that EDGAR accepted from 2010-12-01 to 2012-04-24 for
      the stocks whose CIK passed, each with its Eastern acceptance time read
      from the filing's `.hdr.sgml`. A filing is pinned by its accession, so
      the record is not a vintage, as
      [docs/design.md](design.md)'s section "A record that reads a company's
      earnings filings" explains.
   3. For runs C, D, E1 and E5, the owner archive's `sp500` Alpha Vantage
      files, downloaded 2026-10-05 and pinned by their sha256s in
      `data/archive_vintages.jsonl`, read for the raw open, the raw close and
      the adjusted close. They sit under the premise's exception for licensed
      bars, so these four runs never run in CI. Locally their pins run only
      where the archive is configured and `QT_ARCHIVE_RUN=1` asks for them.
2. **The specification.** `chan.pead.pead` unchanged: the flag file's 330
   days from 2011-01-03 to 2012-04-24, prices cut to them before any gap is
   taken, a lookback of 90, an entry of 0.5 moving standard deviations, a
   denominator of 30, 252-day annualisation, book two's `smartstd` and no
   cost. The adjusted open is the raw open times that day's adjusted close
   over its raw close.

### The registration

The comparison was registered on the issue before any number on these
sources was seen, in
[the plan audit's comment](https://github.com/l3a0/quantitative-trading/issues/251#issuecomment-6104973515).
It fixes four universes.

1. `ALL`, Chan's 497 stocks.
2. `CAL`, the stocks with a checked CIK.
3. `PX`, the stocks with a checked archive series.
4. `U`, the stocks in both.

It fixes two calendars, both read from the Eastern acceptance time, both
skipping an 8-K/A, and both making one flag of several filings on one day.

1. **R1, the primary calendar.** A filing accepted before 09:30 on a trading
   day flags that day. One accepted at 16:00 or later, or on a day the market
   was shut, flags the next trading day. One accepted during the session
   flags nothing.
2. **R5, the secondary calendar.** R1, except that a filing accepted on a
   later date than its `reportDate` flags the trading day after `reportDate`,
   and one accepted during the session flags that same day. It was chosen
   because it matched Chan's flags best on a 32-stock sample.

And it fixes ten runs, each the rule above on one universe, one price
source and one calendar.

| Run | Stocks | Prices | Flags | What changes against its reference |
| --- | --- | --- | --- | --- |
| A | ALL | Chan's | Chan's | Entry 12, unchanged |
| A_CAL, A_PX, A_U | CAL, PX, U | Chan's | Chan's | the universe, against A |
| B1, B5 | CAL | Chan's | R1, R5 | the calendar, against A_CAL |
| C | PX | Alpha Vantage, adjusted | Chan's | the vendor, against A_PX |
| D | PX | Alpha Vantage, raw | Chan's | the price basis, against C |
| E1, E5 | U | Alpha Vantage, adjusted | R1, R5 | everything, against A_U and against A |

Nothing the registration fixes was changed. It left five things open, and
`chan.pead_rerun`'s docstring names each, because each moves a figure or a
count.

1. **The route to an archive series.** The audit counted 399 same-company
   series under Chan's own tickers, a count no test here holds. The check
   here passes 398 of them, and running it on every series in the
   cross-section adds 48 renamed companies, such as Chan's UTX under the
   archive's RTX, so PX holds 446. `TestTheCommittedTable` in
   `tests/test_earnings_filings.py` holds the 398 and the 48.
2. **What a checked CIK is.** A CIK passes when it was filing on 2012-03-30,
   its EDGAR name that day matches one holding in IVV's 2012-03-31 schedule,
   that holding is priced within 3 percent of Chan's close, and it filed at
   least one Item 2.02 8-K in the window. Nine stocks fail.
   1. Five are not in IVV's 2012-03-31 schedule although Chan's file holds
      them: AK Steel, Compuware, Monster Worldwide, Tellabs and MEMC. Two of
      them also carry another company's proposed CIK. Compuware's is
      TetriDyn's, 827099, and Monster Worldwide's is Verisk's, 1442145.
   2. Cablevision's proposed CIK is BJ's Wholesale's, 1037461.
   3. DuPont's proposed CIK is the DuPont formed after 2015, 1666700, which
      fails on dates because it had filed nothing by 2012-03-30.
   4. NYSE Euronext fails on the name, because EDGAR files it with no legal
      form.
   5. Leucadia's CIK filed no Item 2.02 8-K in the window.
3. **The trading days**, which are the committed raw SPY vintage's and agree
   with Chan's price file on every day the filings reach.
4. **D runs without the scale-break guard.** A split inside the window is
   what a raw series carries and what D measures. The guard would refuse 16
   of PX's stocks, which `TestTheArchiveRuns` names.
5. **The calendars cover CAL's 488 stocks rather than all 497.** The
   correction on the issue asked for flags in the shape of Chan's file, 330
   days by 497 stocks. The index holds no filing for the nine stocks outside
   CAL, so the derived calendars leave them out. No run reads a derived flag
   outside CAL, so only rows 12 and 13, the agreement over 161,040 cells,
   depend on this choice.

### What this repo computed

| # | Run or count | Arithmetic annual return | Sharpe ratio | Compounded APR, maximum drawdown, its days | Trades, busiest day | Mean return per trade | Assertion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | A, ALL 497, Chan's prices and flags | 0.066743 | 1.4909 | 0.067952, −0.026052, 109 | 1,072, 30 | 0.002446 | `TestTheCommittedRuns::test_the_figures[A]`, `::test_run_a_is_entry_12_unchanged` and `::test_the_return_per_trade[A]` |
| 2 | A_CAL, 488 stocks | 0.054481 | 1.3253 | 0.055101, −0.029402, 115 | 1,052, 28 | 0.002035 | `TestTheCommittedRuns::test_the_figures[A_CAL]` and `::test_the_return_per_trade[A_CAL]` |
| 3 | A_PX, 446 stocks | 0.053099 | 1.5028 | 0.053874, −0.023386, 112 | 964, 27 | 0.002164 | `TestTheCommittedRuns::test_the_figures[A_PX]` and `::test_the_return_per_trade[A_PX]` |
| 4 | A_U, 441 stocks | 0.043678 | 1.2815 | 0.044038, −0.023176, 114 | 949, 25 | 0.001808 | `TestTheCommittedRuns::test_the_figures[A_U]` and `::test_the_return_per_trade[A_U]` |
| 5 | B1, CAL on R1 | 0.071050 | 1.7045 | 0.072696, −0.027258, 63 | 1,291, 49 | 0.002162 | `TestTheCommittedRuns::test_the_figures[B1]` and `::test_the_return_per_trade[B1]` |
| 6 | B5, CAL on R5 | 0.063142 | 1.2988 | 0.063923, −0.031029, 80 | 1,477, 55 | 0.001679 | `TestTheCommittedRuns::test_the_figures[B5]` and `::test_the_return_per_trade[B5]` |
| 7 | C, PX on adjusted Alpha Vantage prices | 0.053206 | 1.4905 | 0.053973, −0.025224, 113 | 964, 27 | 0.002168 | `TestTheArchiveRuns::test_the_figures[C]` and `::test_the_return_per_trade[C]` |
| 8 | D, PX on raw Alpha Vantage prices | 0.053283 | 1.5255 | 0.054083, −0.023066, 112 | 954, 27 | 0.002194 | `TestTheArchiveRuns::test_the_figures[D]` and `::test_the_return_per_trade[D]` |
| 9 | E1, U on adjusted prices and R1 | 0.057489 | 1.6585 | 0.058532, −0.023984, 63 | 1,172, 44 | 0.001927 | `TestTheArchiveRuns::test_the_figures[E1]` and `::test_the_return_per_trade[E1]` |
| 10 | E5, U on adjusted prices and R5 | 0.057426 | 1.4118 | 0.058229, −0.029106, 80 | 1,339, 48 | 0.001685 | `TestTheArchiveRuns::test_the_figures[E5]` and `::test_the_return_per_trade[E5]` |

| # | Count | Value | Assertion |
| --- | --- | --- | --- |
| 11 | The universes ALL, CAL, PX and U | 497, 488, 446, 441 | `TestTheCommittedRuns::test_the_universes` |
| 12 | R1 against Chan's flags over the 161,040 cells of CAL, flagged by both, by Chan's only, by R1's only | 1,540, 311, 914 | `TestTheCalendarsAgainstChans::test_r1` |
| 13 | R5 against Chan's flags, the same three counts | 1,694, 157, 1,124 | `TestTheCalendarsAgainstChans::test_r5` |
| 14 | Apple's in-window R1 flags Chan's file lacks | 2011-01-19 and 2011-10-19 | `TestTheCalendarsAgainstChans::test_r1_catches_the_two_apple_releases_chans_flags_miss` |
| 15 | Filings in the index, accepted before 09:30, during the session, from 16:00 | 2,930: 1,460, 405, 1,065 | `TestTheCommittedIndex::test_it_holds_2930_filings_for_every_stock_of_the_calendar` and `::test_when_the_filings_were_accepted` in `tests/test_earnings_filings.py` |
| 16 | Filings accepted on a later date than they report | 343 | `TestTheCommittedIndex::test_343_were_accepted_after_the_date_they_report` in `tests/test_earnings_filings.py` |
| 17 | Stocks whose raw series the scale-break guard would refuse | 16 | `TestTheArchiveRuns::test_the_raw_prices_cross_a_split_in_sixteen_stocks` |

Row 1 is Entry 12's run, and its pins move only if Entry 12's do. The
busiest days of rows 5, 6, 9 and 10 hold more than 30 positions, so on those
days the book is levered past one, since the rule divides by 30 whatever the
count. The cells of CAL that neither calendar flags, 158,275 under R1 and
158,065 under R5, complete rows 12 and 13.

The mean return per trade is each trade's signed return from the open to the
close, averaged over the run's trades. The rule sums each day's trades and
divides by 30, so the arithmetic annual return is the trades times that mean
times 252, over 30 and over the 330 days, which
`TestTheCommittedRuns::test_the_return_is_the_trades_times_their_mean` holds.

### The attribution

Read from the arithmetic annual return and the Sharpe ratio, as registered.
`TestTheArchiveRuns::test_the_attribution` holds rows 18 to 27, and
`TestTheCommittedRuns::test_the_attribution_without_the_archive` holds rows
18, 19 and 24 where no archive is.

| # | Effect | Runs | Arithmetic annual return | Sharpe ratio |
| --- | --- | --- | --- | --- |
| 18 | The universe | A_U − A | −0.023065 | −0.2094 |
| 19 | The calendar | B1 − A_CAL | +0.016568 | +0.3792 |
| 20 | The vendor | C − A_PX | +0.000107 | −0.0123 |
| 21 | The price basis | D − C | +0.000078 | +0.0350 |
| 22 | Everything | E1 − A_U | +0.013811 | +0.3770 |
| 23 | The interaction, what E1 − A_U leaves after rows 19 to 21 | | −0.002942 | −0.0249 |

The registration's table of runs names four more comparisons than the
attribution uses. B5 is read against A_CAL, and E1 and E5 are each read
against A_U and against A.

| # | Comparison | Runs | Arithmetic annual return | Sharpe ratio |
| --- | --- | --- | --- | --- |
| 24 | The calendar, on R5 | B5 − A_CAL | +0.008661 | −0.0265 |
| 25 | E1 against all 497 on Chan's files | E1 − A | −0.009254 | +0.1677 |
| 26 | E5 against its own stocks on Chan's files | E5 − A_U | +0.013748 | +0.1303 |
| 27 | E5 against all 497 on Chan's files | E5 − A | −0.009317 | −0.0790 |

Row 23 subtracts the basis effect of row 21 from row 22, because the
registration words the interaction that way. E1 and A_U both read adjusted
prices, though, so no price basis separates them. Without row 21 the residual
is row 28. That reading was not registered, and
`TestTheArchiveRuns::test_the_interaction_without_the_basis_effect` holds it.

| # | Residual | Runs | Arithmetic annual return | Sharpe ratio |
| --- | --- | --- | --- | --- |
| 28 | What E1 − A_U leaves after rows 19 and 20 only, not registered | | −0.002865 | +0.0102 |

### Checks run after the figures were seen

The review of the pull request that shipped this entry ran these on the same
vintages. None was registered, and the thresholds in rows 29 and 33, 7 days
and 2 percent, were chosen after reading the data. They decide nothing. They
say where the figures above are fragile.

| # | Check | Value | Assertion |
| --- | --- | --- | --- |
| 29 | Filings accepted 7 or more days after their `reportDate`, those R5 flags inside the window, those dated at a quarter's end, and those whose R5 flag Chan's file also holds | 76, 73, 64, 2 | `TestTheCalendarsAgainstChans::test_r5_carries_73_long_late_filings_back_to_a_quarters_first_day` |
| 30 | B5 with row 29's filings on the day R1 gives them, arithmetic return and Sharpe ratio | 0.062600, 1.2802 | `TestTheCommittedRuns::test_b5_with_its_long_late_filings_read_three_other_ways` |
| 31 | B5 with them read by R5 without its late rule | 0.064813, 1.2880 | the same |
| 32 | B5 with them dropped | 0.059903, 1.2407 | the same |
| 33 | PX stock-days whose adjusted open, scaled by Chan's close over the archive's, lies more than 2 percent from Chan's open, the stocks they fall in, and how many fall on 2011-10-27 and on 2011-09-12 | 64, 56, 30, 24 | `TestTheArchiveOpens::test_64_stock_days_over_56_stocks_open_more_than_2_percent_off_chans` |
| 34 | The days GCI's raw open reads about 15.378 | 2011-12-27, 2012-01-03, 2012-01-17, 2012-02-21, 2012-04-09 | `TestTheArchiveOpens::test_gci_repeats_a_stale_open_after_each_holiday` |
| 35 | How far C moves with Chan's open in place of each of row 33's, arithmetic return and Sharpe ratio | +0.000015, +0.0195 | `TestTheArchiveOpens::test_chans_opens_in_their_place_move_e5_more_than_the_vendor_and_basis` |
| 36 | How far E1 moves | −0.000539, −0.0098 | the same |
| 37 | How far E5 moves | −0.004566, −0.1039 | the same |
| 38 | Filings dated at the quarter's end of 2010-12-31, 2011-03-31, 2011-06-30, 2011-09-30 and 2011-12-31 that were accepted after the 24th of the next month | 10, 9, 7, 6, 7 | `TestTheCommittedIndex::test_how_many_quarter_end_filings_trail_the_next_months_24th` in `tests/test_earnings_filings.py` |

### What the entry concludes

Four things. The fourth was measured by the write-up after the runs, and
`TestWhatThePostMeasured` in
[tests/test_pead_rerun.py](../tests/test_pead_rerun.py) pins it. It decides
nothing.

1. **On the same stocks, R1 earns more than Chan's flags in this one
   exploratory sample.** On CAL, R1 lifts A_CAL's 0.054481 to 0.071050 and
   its Sharpe ratio from 1.3253 to 1.7045. It does so in two ways.
   1. R1 takes 1,291 trades against 1,052.
   2. Each trade earns 6 percent more on average, 0.002162 against
      0.002035.

   The rule divides each day by a fixed 30, so more trades at the same mean
   raise the return in proportion. About three quarters of the +0.016568 is
   the extra trades, which
   `TestTheCommittedRuns::test_r1_earns_more_a_trade_and_r5_less_than_chans_flags_on_cal`
   holds with the 6 percent. The Sharpe ratio's gain does not depend on the
   30, because dividing every day by one number scales the mean and the
   deviation alike. On U, the archive's prices on R1 give 0.057489 and
   1.6585 against A_U's 0.043678 and 1.2815. Neither reaches Chan's 0.066743
   on all 497. E1 against A is −0.009254 in return and +0.1677 in Sharpe
   ratio, because the universe moves the return more than anything else.
2. **The universe moves the arithmetic return most, and the vendor and the
   basis barely move it, as the audit expected.** Dropping the stocks outside
   U takes 0.023065 off the arithmetic return. The vendor and the basis move it
   by about a ten-thousandth each. A same-day return from the open to the
   close does not depend on the basis, which moves only the overnight gap and
   its 90-day deviation, so D takes 954 trades where C takes 964 and earns
   almost the same. The vendor's small effect holds for the closes the series
   check compares. The opens are another matter, which the section below
   takes up.
3. **R5 matches Chan's flags more closely and earns less on each trade.** R5
   misses 157 of Chan's flags against R1's 311. On CAL it gives 0.063142 and
   a Sharpe ratio of 1.2988, against R1's 0.071050 and 1.7045. Its return
   rises over Chan's flags by +0.008661 only because it takes 1,477 trades
   against 1,052. Each of its trades earns 0.001679 on average, less than
   the 0.002035 on Chan's flags, and its Sharpe ratio is 0.0265 lower than
   A_CAL's. E5 falls below A on both figures, in row 27. Its extra flags
   come from two kinds of filing.
   1. One was accepted during the session, so the gap at that day's open
      came before the release.
   2. The other was accepted after the date it reports. R5 flags the trading
      day after that date, which reaches a long way back for a filing that
      reports a quarter's end. 73 filings accepted 7 or more days late put
      R5 flags inside the window, 64 of them dated at a quarter's end, so
      they land on the quarter's first trading day, weeks before the
      release. Chan's file flags 2 of those days.

   Read another way, row 29's filings put B5 anywhere from 0.059903 to
   0.064813 against its 0.063142, in rows 30 to 32. The index
   stops at acceptance on 2012-04-24, so R5 also loses the last quarter's
   period-end filings accepted after that day. In the five earlier quarters
   6 to 10 such filings were accepted after the 24th of the next month, in
   row 38, and each of them would have flagged a day weeks early. R1 reads
   only the acceptance time, so the cutoff costs it nothing inside the
   window.
4. **The universe effect is exactly the trades of the 56 stocks outside U.**
   Each stock trades on its own gap and its own 90-day deviation, so
   dropping some stocks changes nothing about the trades of the rest. A is
   therefore A_U's trades plus those of the stocks outside U, and row 18 is
   their contribution, all of it. It splits three ways.
   1. The 9 stocks with no checked CIK take 20 trades and add 0.012261,
      which is exactly A against A_CAL, read from the true value.
   2. The 4 stocks of CAL whose series holds another company's returns,
      AGN, CB, JCI and LSI, take 8 trades and add 0.002526.
   3. The 43 stocks of CAL whose series lacks closes or was never proposed
      take 95 trades and add 0.008278. 35 of those series start after
      2012-04-24, EP's lacks the window's first 35 days, and 7 were never
      proposed, since the `sp500` cross-section holds no series under their
      tickers.

   The 47 stocks of CAL with no checked series are the last two groups,
   with 103 trades adding 0.010803. With U's 441 stocks, 949 trades and
   0.043678, the groups sum to A's 0.066743. The stocks outside U carry 0.35
   of it. The 13 whose ticker is not tied to the right company, the first two
   groups, take 28 trades and add 0.014787, 0.64 of the universe effect. On
   2011-08-04 the stocks outside U add 0.010702 through 8 trades, 0.46 of the
   universe effect on one day, and the largest of those trades is WFR short
   at 0.1108. Their mean trade is 0.007367 over 123 against 0.001808 over
   U's 949, a Welch t of 1.46 that treats every trade as independent, so
   chance is not ruled out.

### What this entry cannot say

Five things.

**Whether the drift pays today.** The window, the rule and the 30 are
Chan's, and the audit had already looked at the sample. A registered test
would fix the rule and run it on data after 2012.

**What the stocks outside U would have earned.** Their CIK or their
series did not pass its check, so nothing here prices them on a second
source. All of the universe effect is theirs, as conclusion 4 shows.

**Whether a filing is an earnings release.** Item 2.02 is the item a release
is filed under, and nothing here reads the filing's text, so an 8-K that
carries the item for another reason flags a day too.

**Whether the archive's opens are right.** The series check in
`chan.earnings_filings` compares closes only, and the rule trades from the
open. Row 33 finds
64 stock-days over 56 stocks whose open lies more than 2 percent from Chan's
once the closes are put on one scale. GCI's raw open repeats a stale value
of about 15.378 on five days, each the first after a market holiday, in row
34. Putting Chan's open in place of each of the 64 moves C and E1 little, in
rows 35 and 36. It moves E5 by −0.004566 and −0.1039, in row 37, through
three trades.

1. PNC on 2011-09-12 turns from long to short, worth −0.002261.
2. MCO on 2012-02-08 stays short and earns less, worth −0.001751.
3. TMK on 2011-10-27 stays long and earns less, worth −0.000554.

The PNC flip alone moves E5 more than the vendor and basis effects of rows
20 and 21 together. E1's move is the same MCO and TMK trades and CAM on
2011-10-27, which turns from long to short and gains 0.001766.
`TestTheArchiveOpens::test_three_trades_make_each_of_e5s_and_e1s_moves`
holds all six, measured by the write-up after the runs. Not every
one of the 64 is an error, though. 30 fall on 2011-10-27 and 24 on
2011-09-12, days on which many stocks disagree at once, which reads more
like two vendors defining the open differently.

**What the leverage past one costs.** Rows 5, 6, 9 and 10 hold up to 55
positions on one day against a denominator of 30, and nothing here sizes the
book by each day's count.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/pead-edgar-rerun-lessons.md](../blog/pead-edgar-rerun-lessons.md) moves
with it, since that post quotes most of these figures. So does its one
figure, drawn from committed files only, which
`uv run python -m chan.pead_rerun_figures` redraws.

## Entry 47: the VIX filter on buy on gap and the STOXX Europe 50 gap rule, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Kindle location 3509, which filters Example 4.1's buy
on gap and Example 7.1's opening gap rule on the VIX. Shipped under
[issue 359](https://github.com/l3a0/quantitative-trading/issues/359). Every
location in this entry is in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eighteen rows, all derivable from
[tests/test_vix_filter.py](../tests/test_vix_filter.py) except Example 7.1's
full-calendar figures in row 15, which
[tests/test_opening_gap.py](../tests/test_opening_gap.py) derives in
`TestTheSpecification::test_252_times_the_mean_also_rounds_to_13_percent` and
`::test_the_sharpe_ratio`. Fourteen rows do not match one printed figure to one
computation, and each says so in its own cells. Row 5 checks two printed
figures against a second reading of FSTX's return line. Rows 6 to 12 check the
printed figures against readings of the sentence that were set aside, and
rows 13 to 18 carry no published figure.

Chapter 8 argues that no one risk indicator suits every strategy, because a
period that is risky for one rule can be the best period for another.
Location 3509 makes the case on two rules the book already ran. It keeps only
the days after the VIX closed above 35, "a common threshold for highly risky
periods". On those days buy on gap earns 17.2 percent at a Sharpe ratio of
1.4, against around 8.7 percent and 1.5 on every day. FSTX's opening gap rule
earns 2.6 percent at 0.16, against around 13 percent and 1.4. So the same
filter raises one rule's return and nearly erases the other's.

**All four filtered figures reproduce, under one specification and the
script's own sign for FSTX.** Each rule runs unchanged through
`chan.buy_on_gap` and `chan.opening_gap`, its calendar is joined to VIX's,
and the figures are taken over the days after a close above 35. Buy on gap
keeps 190 days and gives 0.171924 and 1.417425. FSTX keeps 185 and gives
0.025730 and 0.164869 under `gapFutures_FSTX.m`'s return line as written,
which fades the jump, as Entry 40 found for the unfiltered figures. The
momentum sign the text describes gives the same numbers negated.

**No script ships for location 3509, and the FSTX alignment was found by
search.** Neither public mirror of Chan's code holds a file that applies the
filter, so the specification is inferred from the printed figures rather than
read from code. The plan on
[issue 359](https://github.com/l3a0/quantitative-trading/issues/359) tried six
ways of aligning VIX with FSTX's calendar and two ways of averaging, and saw
their figures before choosing one. Rows 7 to 12 pin the average and the five
alignments set aside, so a reader can see what each gives.

1. **The join** lands both figures, and it is the specification below.
2. **The latest VIX close before each FSTX day**, row 8, lands the Sharpe
   ratio and prints the return as 2.5 percent.
3. **VIX forward-filled onto FSTX's calendar and moved one row**, row 10,
   keeps the same 188 days as row 8 and so gives the same figures.
4. **VIX moved one row on FSTX's own calendar**, row 9, lands neither.
5. **The same day's VIX on FSTX's own calendar**, row 11, looks ahead.
6. **The same day's VIX forward-filled**, row 12, looks ahead too.

The last two are ruled out before any figure is read. The gap rule holds FSTX
from the open to the close, and VIX closes at 16:15 New York time, hours after
FSTX opens on the same date, while the sentence asks for the preceding day's
close. Both give a negative return and Sharpe ratio besides. So only the join
lands 2.6 percent. The criterion is the one every earlier entry uses: a figure
lands when the computed value rounds to the printed string at the decimals
the string carries, which is `chan.khandani_lo_book_two.matches`. Buy on
gap's figures do not depend on which previous close is read, because its
1,500 days are exactly VIX's days over the same span. So an alignment that
reads the previous day can change only the close read on the first day,
2006-05-11, which no reading keeps. FSTX's do depend on it, so its two rows
are a fit found after the figures were seen.

Every row reads three vintages and one specification unless it names
another, so they are stated once here.

1. **VIX.** `data/vix/vix.csv`, vendor `chan-csv`, basis `raw`, saved
   2012-05-09, lifted from Chan's `VIX.csv`, 5,635 closes from 1990-01-02 to
   2012-05-08.
2. **The stocks.** `data/inputdataohlcdaily_stocks_20120424/`, the 497 stocks
   of Chan's `inputDataOHLCDaily_stocks_20120424.mat`, vendor `chan-mat`,
   basis `adjusted`, saved 2012-04-25, 1,500 days from 2006-05-11 to
   2012-04-24, as Entry 18 reads them. Every figure on them is about
   survivors.
3. **FSTX.** `data/inputdataohlcdaily_20120517/fstx.csv`, vendor `chan-mat`,
   basis `adjusted`, saved 2012-05-18, 2,000 days from 2004-07-16 to
   2012-05-17, as Entry 40 reads it.
4. **The specification.** Each rule runs on its full calendar, unchanged, and
   its daily returns are taken on the days its calendar shares with VIX's,
   which is MATLAB's `intersect` on two date vectors. A day qualifies when
   `backshift(1, vix) > 35` on that joined calendar. So the close read is the
   previous joined day's, the test is strict, and a NaN qualifies nothing.
   The return figure is `252 · mean` over the qualifying days alone, and the
   Sharpe ratio is `mean · √252 / std` over them, with MATLAB's n − 1 `std`,
   no risk-free rate and no cost.

**The scale-break guard.** The guard flags a day whose close is more than 1.6
times the close before it, or less than that close divided by 1.6. VIX flags
2007-02-27, a real move from 11.15 to 18.31, and the day falls inside both
windows, so a guard over either whole window would refuse. `chan.vix_filter`
guards VIX over two spans in each window instead. The first runs from the
window's first joined day to 2007-02-26 and the second from 2007-02-27 to its
last joined day, 2012-04-24 for buy on gap and 2012-05-08 for FSTX. Together
they guard every day-over-day move the run reads except the one real move,
and nothing flags in either. Entry 41 met the same day and guarded VIX only
from an anchor after it, which differs from this case, because no figure there
reads VIX before the anchor and here every close before the flag feeds the
filter. A rescale smaller than 1.6 times passes the guard on any span, and
row 16 shows such a rescale moving a figure. FSTX is guarded over its whole
span, as in Entry 40. The stocks are not guarded, for the reason Entry 18
gives.

Every result here is **exploratory**. Reproducing Chan's figures spends his
samples on two rules and a threshold he chose, and the FSTX alignment was
chosen after its figures were seen. So the entry says whether his numbers
reproduce on his files and nothing about whether VIX above 35 guards either
rule today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Buy on gap's annualized average return when the preceding day's VIX is over 35 | 17.2 percent | location 3509 |
| 2 | Buy on gap's Sharpe ratio on the same days | 1.4 | location 3509 |
| 3 | FSTX's annualized average return on the same condition | 2.6 percent | location 3509 |
| 4 | FSTX's Sharpe ratio on the same days | 0.16 | location 3509 |
| 5 | The momentum rule location 2965 describes earns rows 3 and 4 | a claim | locations 2965 and 3509 |
| 6 | Row 1, read as the compounded APR over the qualifying days | 17.2 percent | location 3509 |
| 7 | Rows 1 to 4, read as the other days set to 0 and every day averaged | 17.2 percent and 1.4, 2.6 percent and 0.16 | location 3509 |
| 8 | Rows 3 and 4, read with the latest VIX close before each FSTX day | 2.6 percent and 0.16 | location 3509 |
| 9 | Rows 3 and 4, read one row back on FSTX's own calendar | 2.6 percent and 0.16 | location 3509 |
| 10 | Rows 3 and 4, read with VIX forward-filled onto FSTX's calendar and moved one row | 2.6 percent and 0.16 | location 3509 |
| 11 | Rows 3 and 4, read with the same day's VIX on FSTX's own calendar | 2.6 percent and 0.16 | location 3509 |
| 12 | Rows 3 and 4, read with the same day's VIX forward-filled onto FSTX's calendar | 2.6 percent and 0.16 | location 3509 |
| 13 to 18 | The joined calendars, the qualifying days, the unfiltered figures, the guard, the rule run after the join, and whether the qualifying days differ from the rest | none, as each row says | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · mean` over buy on gap's 190 qualifying days | 0.171924 | `TestTheSpecification::test_buy_on_gap_keeps_190_days` and `::test_buy_on_gap_s_return_is_chans_17_2_percent` |
| 2 | The Sharpe ratio over the same days | 1.417425 | `TestTheSpecification::test_buy_on_gap_s_sharpe_ratio_is_chans_1_4` |
| 3 | `252 · mean` over FSTX's 185 qualifying days, literal reading | 0.025730 | `TestTheSpecification::test_fstx_keeps_185_days` and `::test_fstx_s_return_is_chans_2_6_percent_under_the_script_s_sign` |
| 4 | The Sharpe ratio over the same days, literal reading | 0.164869 | `TestTheSpecification::test_fstx_s_sharpe_ratio_is_chans_0_16_under_the_script_s_sign` |
| 5 | Rows 3 and 4 under the momentum reading | −0.025730 and −0.164869 | `TestTheClaim::test_the_momentum_sign_s_figures` and `::test_neither_lands_the_book` |
| 6 | `prod(1 + ret)^(252 / 190) − 1` over buy on gap's qualifying days | 0.179297 | `TestTheReadingsThatMiss::test_the_compounded_apr_prints_17_9_not_17_2` |
| 7 | The other days set to 0, every joined day averaged | buy on gap 0.021777 and 0.503869 over 1,500 days, FSTX 0.002447 and 0.050969 over 1,945 | `TestTheReadingsThatMiss::test_zeroing_the_other_days_lands_neither_rule` |
| 8 | Each FSTX day kept when the latest VIX close strictly before it is above 35, with no join | 188 days, 0.025319 and 0.163555 | `TestTheReadingsThatMiss::test_the_latest_close_before_each_day_prints_2_5` and `::test_the_latest_close_reading_adds_three_us_holidays` |
| 9 | VIX placed on FSTX's 2,000 days with NaN where it has no close, then moved one row | 185 days, 0.045238 and 0.291589 | `TestTheReadingsThatMiss::test_one_row_back_on_fstx_s_own_calendar_lands_neither` and `::test_the_own_calendar_reading_swaps_the_day_after_each_holiday_for_the_holiday` |
| 10 | VIX forward-filled onto FSTX's 2,000 days, then moved one row | 188 days, 0.025319 and 0.163555, the same days as row 8. The two read different closes on 23 days and none crosses 35 | `TestTheReadingsThatMiss::test_vix_forward_filled_one_row_back_keeps_the_latest_close_s_days` and `::test_the_forward_fill_and_the_latest_close_read_different_closes_on_23_days` |
| 11 | Each FSTX day kept when VIX closed above 35 on the same date, NaN on US holidays | 185 days, −0.047063 and −0.297416 | `TestTheReadingsThatMiss::test_same_day_vix_with_nan_on_holidays_is_negative` and `::test_the_same_day_readings_read_vix_on_the_trade_s_own_date` |
| 12 | Each FSTX day kept when VIX closed above 35 on the same date, forward-filled | 188 days, −0.046312 and −0.295046 | `TestTheReadingsThatMiss::test_same_day_vix_forward_filled_is_negative` and `::test_the_same_day_readings_read_vix_on_the_trade_s_own_date` |
| 13 | The joined calendars | buy on gap 1,500 of 1,500, FSTX 1,945 of 2,000, losing 7 days after 2012-05-08 and 48 the CBOE did not trade | `TestTheJoin::test_buy_on_gap_keeps_all_1500_days`, `::test_fstx_keeps_1945_of_its_2000_days` and `::test_fstx_loses_7_days_after_vix_ends_and_48_the_cboe_did_not_trade`, and for the 7 days, `TestTheReadingsThatMiss::test_the_seven_days_after_vix_ends_could_not_qualify_either_way` |
| 14 | The qualifying days, and the days each rule held a position on them | both from 2008-09-18 to 2011-11-10, after VIX's first close above 35 inside either window on 2008-09-17. Buy on gap held on 20 of 190, FSTX on 43 of 185, long on 21 and short on 22 | `TestBesideTheReplication::test_both_rules_keep_the_days_from_2008_09_18_to_2011_11_10`, `::test_vix_first_closes_above_35_inside_either_window_on_2008_09_17`, `::test_buy_on_gap_held_a_position_on_20_of_its_190_kept_days`, `::test_fstx_held_a_position_on_43_of_its_185_kept_days` and `::test_no_vix_close_sits_exactly_on_35` |
| 15 | `252 · mean` and the Sharpe ratio over every joined day, and FSTX's over its full calendar | buy on gap 0.085279 and 1.537063, FSTX 0.139950 and 1.589197 joined, 0.128622 and 1.441620 on all 2,000 days | `TestBesideTheReplication::test_buy_on_gap_unfiltered_is_entry_18_s_because_the_calendar_is_unchanged` and `::test_the_join_moves_fstx_s_unfiltered_figures` |
| 16 | VIX guarded over two spans in each window, either side of its flagged day, and a rescale too small to flag | 2007-02-27 alone flags, from 11.15 to 18.31. Each window is guarded from its first joined day to 2007-02-26 and from 2007-02-27 to its last joined day, which leaves out only the flagged move. VIX's largest close from 2004-07-16 to 2007-02-26 is 23.81, on 2006-06-13. Closes to 2006-11-30 raised 1.48 times pass both spans, and buy on gap then keeps 191 days | `TestTheGuard::test_vix_flags_2007_02_27_alone`, `::test_vix_is_guarded_on_both_sides_of_its_flagged_day_in_each_window`, `::test_the_two_spans_leave_out_only_the_flagged_move`, `::test_a_doubling_of_vix_before_its_flagged_day_is_refused`, `::test_vix_s_largest_close_before_the_flag_sits_inside_the_guard_s_blind_band` and `::test_a_rescale_under_1_6_times_passes_the_guard_and_moves_a_figure` |
| 17 | FSTX's rule run on the 1,945 joined days instead of its own 2,000 | 11 joined days' returns move, and none of the 185 qualifying days'. Ten are the first joined day after a day the CBOE did not trade, and the eleventh is 2005-09-20 | `TestTheSpecification::test_the_rule_run_after_the_join_keeps_the_same_fstx_returns` |
| 18 | Welch's t on mean daily return, the qualifying days against the other joined days, treating each day as independent | buy on gap t = 0.705402 and p = 0.481405, FSTX's literal reading t = −0.684181 and p = 0.494679, and the momentum reading the same t negated | `TestBesideTheReplication::test_neither_rule_s_kept_days_differ_from_its_other_days_beyond_noise` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0 percent | reproduced | 17.1924 percent rounds to the book's 17.2. Buy on gap's calendar is VIX's over its span, so this figure does not depend on which previous close is read. |
| 2 | +0.0 | reproduced | 1.417425 rounds to the book's 1.4. |
| 3 | −0.0 percent | reproduced | 2.5730 percent rounds to the book's 2.6, under the join chosen after six alignments were tried. Rows 8 to 12 give the other five. |
| 4 | +0.00 | reproduced | 0.164869 rounds to the book's 0.16, under the same join. |
| 5 | −5.2 percent and −0.32 | did not reproduce | The rule location 2965 describes loses on the filtered days what the fade earns, on Chan's own file, so the vintage explanation is spent. As in Entry 40, the figures the book prints belong to the script's sign. |
| 6 | +0.7 percent | did not reproduce | The compounded APR over the same days prints as 17.9 percent. What fails is that reading rather than Chan's number, which row 1 lands as `252 · mean`. |
| 7 | −15.0 percent and −0.9 for buy on gap, −2.4 percent and −0.11 for FSTX | did not reproduce | Averaging the zeroed series over every day dilutes the filtered return by the share of days kept. What fails is that reading, so the average runs over the qualifying days alone. |
| 8 | −0.1 percent and +0.00 | did not reproduce | The Sharpe ratio lands and the return prints as 2.5 percent. The join lands both, so the join is the reading kept. The three extra days are US holidays on which Eurex traded, 2008-11-27, 2009-01-19 and 2009-02-16. Each reads the close before it here, and the join drops them. |
| 9 | +1.9 percent and +0.13 | did not reproduce | It keeps 185 days, as the join does, but not the same 185. It keeps row 8's three holidays and drops the day after each, which reads the holiday's missing close and qualifies nothing. |
| 10 | −0.1 percent and +0.00 | did not reproduce | Row 8's figures, because it keeps row 8's days. After a day the CBOE traded and Eurex did not, row 8 reads that day's close and this reading reads FSTX's previous day. The nearest call is 2009-05-04, which reads 35.30 one way and 36.50 the other, both above 35. |
| 11 | −7.3 percent and −0.46 | did not reproduce | It reads VIX on the trade's own date, which closes at 16:15 New York time, after FSTX's open. That rules it out before the figures, which are negative. Each day it keeps is the joined day before one row 3 keeps. |
| 12 | −7.2 percent and −0.46 | did not reproduce | It looks ahead as row 11 does. The forward fill adds row 8's three US holidays, each reading the close before it. |
| 13 | none | none, not a replication | The 7 FSTX days after 2012-05-08 have no VIX close, so the join drops them. Under row 8's reading they would read 2012-05-08's close of 19.05, below 35, so none of them could qualify either way. |
| 14 | none | none, not a replication | Buy on gap held nothing on 170 of its 190 qualifying days, so its filtered figures rest on 20 days of trading. No VIX close sits exactly on 35, so the strict test decides no day here, and `TestTheRules` holds it on synthetic closes. |
| 15 | none | none, not a replication | The join leaves buy on gap's calendar unchanged, so its unfiltered figures are Entry 18's. It moves FSTX's to figures that print as 14 percent and 1.6, so location 3509's "around 13 percent and 1.4" is Example 7.1's full calendar, which Entry 40's rows 3 and 4 reproduce. The filtered and unfiltered FSTX figures therefore come from different calendars. |
| 16 | none | none, not a replication | The two spans guard every day-over-day move the run reads except the one real move, which `tests/test_scale_breaks.py` pins. The guard sees only a move of 1.6 times or more, on any span. A rescale of 1.47 times would carry 23.81 past 35, so a rescale inside that blind band could move a day into the filter unseen, and a planted rescale of 1.48 times does. |
| 17 | none | none, not a replication | Dropping the 48 days the CBOE did not trade moves the position on 11 joined days and on none of the qualifying days. On ten of them the open is set against the high or low of the joined day before, two sessions back, and that alone moves them. 2005-09-20 moves through the 90-day spread alone. The 7 days after 2012-05-08 come after every joined day, so dropping them moves nothing. So rows 3 and 4 cannot tell whether Chan filtered before or after running the rule. |
| 18 | none | none, not a replication | Neither p is below 0.4, so on neither rule are the qualifying days' returns distinguishable from the other days' by this test. Chan prints no test, and the figures he prints are point estimates. |

### What the entry concludes

Four things. The fourth adds figures the write-up measured after the run,
which `TestWhatThePostMeasured` in
[tests/test_vix_filter.py](../tests/test_vix_filter.py) pins.

1. **Location 3509's four figures reproduce on Chan's own files.** Buy on
   gap's do so under any alignment that reads the previous day's close,
   because its days are VIX's days. FSTX's do so under the join alone, which
   was chosen after six alignments were tried, so its rows are a fit to the
   printed figures rather than a test of them. The latest close before each
   day lands the Sharpe ratio and prints 2.5 percent, and the two same-day
   alignments look ahead.
2. **Which way the filter points on FSTX depends on the sign, and neither
   direction is distinguishable from noise.** The momentum sign the text
   describes earns each day's return negated. On the joined calendar it gives
   −0.139950 as `252 · mean` over all 1,945 days and −0.025730 over the 185
   kept, so for it the kept days are the less bad ones, the reverse of the
   fade. Row 18 tests the difference and finds none. Welch's t is −0.684181
   for the fade, with p = 0.494679, treating each day as independent. So
   Chan's reading, that VIX above 35 tells the gap trader to stay out, rests
   on point estimates this test cannot tell from noise for either sign. It is
   exploratory and decides nothing.
3. **One phrase names two formulas in one sentence.** The unfiltered
   "annualized average return" of 8.7 percent is buy on gap's compounded APR,
   as Entry 18 found, and the filtered 17.2 percent is the arithmetic
   `252 · mean`, as rows 1 and 6 show. Reading the label alone would pin one
   of them against the wrong formula.
4. **The kept days are few and bunched.** Inside FSTX's window, from
   2004-07-16 to 2012-05-08, VIX closed above 35 on 190 days in 15 runs, the
   highest 80.86 on 2008-11-20. Buy on gap's kept days number 68, 83, 9 and
   30 in 2008 to 2011, and FSTX's 65, 81, 9 and 30, so 151 of 190 and 146 of
   185 fall in 2008 and 2009. Each rule's kept days form 15 runs of
   consecutive joined days, the longest from 2008-09-30 to 2009-04-17. Buy on
   gap's daily returns sum to 0.129625 over its kept days, and one day,
   2009-04-21, returned 0.093601 of it. Without that day the other 189 give
   0.048032 and a Sharpe ratio of 0.855003. FSTX's sum to 0.018889 under the
   fade and −0.018889 under momentum. `VIX.csv` also closes above 35 on 100
   days before 2004-07-15, the first on 1990-08-06, so 2008-09-17 is the first
   close above 35 inside either window and not in the file. Measured after
   the run, so exploratory, and it decides nothing.

### What this entry cannot say

Four things.

**What Chan's own code for the filter did.** No script ships for location
3509. Six alignments were tried for FSTX before one was kept, and rows 3, 4
and 8 to 12 record what each gave. Only the join lands both figures among
them, which cannot rule out a seventh alignment that also lands both.

**Whether the filter guards either rule out of sample.** The threshold, the
rules and the windows are Chan's, and every qualifying day falls between
2008-09-18 and 2011-11-10. A registered test would fix the threshold and the
alignment first and run them on data after 2012.

**What buy on gap earned on the index as it stood each day.** Every stock here
was in the S&P 500 in late 2011, so Entry 18's caveat holds for the filtered
days too.

**Whether VIX's 2007-02-27 print is clean.** The guard flags it, the move
reads as real, and nothing here checks it against a second source. A wrong
print would move a figure only if the true close were above 35, more than
three times the 11.15 of the day before.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/vix-filter-lessons.md](../blog/vix-filter-lessons.md) moves with it,
since that post quotes most of these figures. So does its one figure, which
`uv run python -m chan.vix_filter_figures` redraws, and the third open
question of [blog/opening-gap-lessons.md](../blog/opening-gap-lessons.md),
which points at the post.

## Entry 48: the low-beta rule at leverage a broker would lend, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 814, 2836,
4684, 4700 and 4709. Shipped under
[issue 516](https://github.com/l3a0/quantitative-trading/issues/516). Every
location is the revised edition's and is in
[research/book-notes/quantitative-trading.md](../research/book-notes/quantitative-trading.md).

This entry is not a replication. Location 4709 states the rule and prints no
figure for it at any leverage, and locations 814 and 2836 give the two
ceilings without working an example at either. So no row has a published
number to reproduce, and the tables drop the published-figure and gap columns.
`### Rows that are not replications` above says why the route that lets a
stated claim carry a verdict does not reach it. Rows 1 and 2 test the claim
under rules written before any capped number, but the ceilings were chosen
after Entry 45's figures had been seen, so the claim was not tested blind.

Seven rows, all derivable from
[tests/test_low_beta_capped.py](../tests/test_low_beta_capped.py). The three
Entry 45 figures that rows 3 and 6 quote beside them are pinned in
[tests/test_low_beta_leverage.py](../tests/test_low_beta_leverage.py).

**Not decided at either ceiling, and exploratory.** "At a ceiling of 2, no gap
in compounded growth detectable above about 0.2168 a year over 83 months,
where the point estimate is 0.0934." "At a ceiling of 5, no gap in compounded
growth detectable above about 0.3407 a year over 83 months, where the point
estimate is 0.1659." Both sentences are the plan's fixed wording. Entry 45
found location 4709's rule ruined at location 4684's beta match, which asked
for a leverage of up to 69.0762. Location 4709 says only "highly leveraged",
so this entry caps the match at what location 814 says a broker lends on
stocks held overnight and asks the same question again. Neither capped
portfolio lost its capital in any month. Both out-compounded the unlevered
high fifth in point estimate, by 0.0934 a year at a ceiling of 2 and 0.1659 at
5. Neither gap is distinguishable from noise. The Newey-West t is 1.0715 and
1.2111, and Benjamini-Hochberg rejects neither ceiling in either direction.

**Every row is exploratory, and no result here confirms anything.** The plan
was written on
[issue 516](https://github.com/l3a0/quantitative-trading/issues/516) on
2026-10-11 before any capped number was computed. It came after Entry 45 had
shown its calendar, its leverage path, the ruin, both groups' returns for the
first eight formations and its side figures. The side figures are both Sharpe
ratios, the growths, the realised betas and the full-sample Kelly leverage of
9.9884. Those figures nearly fixed the sign in advance. The unlevered
low fifth already out-compounded the high fifth, and growth rises with
leverage up to the Kelly leverage under a Gaussian approximation, so both
ceilings were expected to show a positive point estimate. Every verdict cell
therefore reads "none, not a replication, exploratory", which carries this
reason and the one above.

Five of the rules carry the result, so they are stated here.

1. **The portfolios.** Entry 45's, unchanged.
   `chan.low_beta_leverage.read_sources` and `build_portfolios` run as that
   entry ran them, on the same three vintages. They are `spx_20071123/`,
   chan-mat adjusted, saved 2007-11-24, then `spy_chan.csv`, chan-xls
   adjusted, saved 2008-01-29, and FRED's TB3MS, downloaded 2026-09-30. The
   universe, the betas, the fifths, the weights and the 83 holding months from
   December 2000 to October 2007 are that entry's. So is k, the leverage that
   matches the low fifth's beta to the high fifth's.
2. **The ceilings.** At each formation the low fifth is levered by
   L = min(k, C), and the capped month returns rf + L × (r_low − rf), borrowing
   at the bill rate with no trading cost. C = 2 is Regulation T's overnight
   leverage, which location 814 gives and location 2836 repeats for a retail
   account. Because k never falls below 2.1826, it is a constant leverage of 2
   here. C = 5 is location 814's portfolio margin of "20 percent or less". That
   is the highest leverage the book puts a number on for stocks held
   overnight, and its "or less" leaves room for more.
3. **The statistic.** d = ln(1 + r_capped) − ln(1 + r_high) over the 83
   months, with its Newey-West t at the default lag. Twelve times the mean of d
   is the gap in realised compounded growth a year.
4. **The control.** Benjamini-Hochberg at q = 0.05 across the two ceilings,
   run once on the one-sided p-values in the claim's direction and once in the
   contrary direction. With two ceilings, a family rejects both when both
   p-values are at most 0.05, and otherwise only one at most 0.025. A ruined
   ceiling enters both families with a p-value of 1.
5. **The outcomes.** Contradicted by ruin when any capped month returns −1 or
   less. Holds when the mean of d is above 0 and the claim's family rejects.
   Contradicted when the mean is below 0 and the contrary family rejects. Not
   decided otherwise, with Y, Entry 45's (1.645 + 0.8416) times the Newey-West
   standard error of the mean of d, times 12. Y ignores the correction, so it
   compares with Entry 45's.

**Every figure is about survivors.** The panel is the S&P 500 as it stood on
2007-11-23, carried backwards, as in Entry 45. Three symbols, WYN, DFS and SE,
also carry an earlier company's prices, which sit in one of the fifths in 36 of
the 83 holding months. [data/README.md](../data/README.md) names the first two.
SE's closes stop on 2005-11-09 and start again on 2007-01-03, the day Spectra
Energy began regular-way trading after Duke Energy spun it off, by
[Spectra Energy's release of 2007-01-02](https://www.sec.gov/Archives/edgar/data/0001373835/000134100407000091/spectra_ex99-1.htm).
So the closes before that gap belong to another company. Their ratio across
the gap, 0.7638, is closer to 1 than the scale-break check's bound of 1.6
either way, so that check does not catch it. The write-up counted those months after the run, and
`TestWhatThePostMeasured` pins the count.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | a low-beta portfolio levered at most 2 out-compounds an unleveraged high-beta one | the rule, with no figure, and overnight positions "allow only a leverage of 2" | locations 4709, 814 and 2836 |
| 2 | a low-beta portfolio levered at most 5 out-compounds an unleveraged high-beta one | the rule, with no figure, and portfolio margin "may require only 20 percent or less of overnight margin" | locations 4709 and 814 |
| 3 to 7 | the realised growth, the leverage, the worst month, the realised beta and the break-even spread | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | ceiling 2: any capped month at −1 or below, else the Newey-West t of d under Benjamini-Hochberg at 0.05 in each direction | no ruined month. Gap 0.0934 a year, t 1.0715 at lag 3, one-sided p 0.1420 for the claim and 0.8580 against it, rejected in neither family, Y 0.2168 | `TestTheCommittedFiles::test_no_month_is_ruined_at_either_ceiling`, `::test_both_ceilings_are_not_decided`, `::test_the_gap_t_both_p_values_and_y` and `::test_each_outcome_line` |
| 2 | ceiling 5, the same | no ruined month. Gap 0.1659 a year, t 1.2111 at lag 3, one-sided p 0.1129 for the claim and 0.8871 against it, rejected in neither family, Y 0.3407 | the same four |
| 3 | realised compounded growth, 12 times the mean monthly log return | 0.2118 at ceiling 2 and 0.2843 at 5, beside Entry 45's unlevered low fifth at 0.1254 and high fifth at 0.1183 | `TestTheCommittedFiles::test_growth_mean_leverage_binding_months_and_beta`, and Entry 45's `TestTheFigures::test_each_series_realised_growth` |
| 4 | the mean leverage, and the months in which k is above the ceiling | mean 2.0000 with 83 months bound at ceiling 2, and 3.5134 with 20 months bound at 5, so the beta match set the leverage in the other 63 | `TestTheCommittedFiles::test_growth_mean_leverage_binding_months_and_beta`, `::test_ceiling_2_is_a_constant_leverage_of_2` and `::test_the_beta_match_sets_the_leverage_in_63_months_at_ceiling_5` |
| 5 | the month with the lowest capped return | at both ceilings the month ending 2002-07-31, formed 2002-06-28. It returned −0.1479 at a leverage of 2 and −0.3719 at 5 | `TestTheCommittedFiles::test_the_worst_month` |
| 6 | realised beta, the slope of the monthly return over the bill on SPY's, all 83 months each as if freshly funded | 0.8584 at ceiling 2 and 1.5831 at 5, beside the high fifth's 2.0671 | `TestTheCommittedFiles::test_growth_mean_leverage_binding_months_and_beta`, and Entry 45's `TestTheFigures::test_the_realised_betas` |
| 7 | the yearly borrowing spread over the bill, charged (L − 1) × s / 12 a month, at which the gap's point estimate reaches 0, by bisection | 0.0946 at ceiling 2 and 0.0661 at 5 | `TestTheCommittedFiles::test_the_break_even_spread` |

Each gap is rounded from its own unrounded value. So ceiling 2's growth less
the high fifth's, 0.2118 less 0.1183, reads 0.0935 while the gap reads 0.0934,
and ceiling 5's, 0.2843 less 0.1183, reads 0.1660 while its gap reads 0.1659.
These are the case `### What precision a number is quoted at` describes.

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | none, not a replication, exploratory | Not decided. The claim's one-sided p-value of 0.1420 is above 0.05, and so is ceiling 5's, so Benjamini-Hochberg rejects neither ceiling in the claim's family. The contrary family's 0.8580 is further still. The gap of 0.0934 a year is under half the detectable gap of 0.2168. The ceilings were chosen after Entry 45's calendar, leverage path, ruin, eight months of returns and side figures had been seen, so even a rejection would have confirmed nothing. |
| 2 | none, not a replication, exploratory | Not decided. The claim's one-sided p-value of 0.1129 is above 0.05, so as row 1 says, Benjamini-Hochberg rejects neither ceiling. The contrary family's 0.8871 is further still. The gap of 0.1659 a year is under half the detectable gap of 0.3407. The same label applies. |
| 3 | none, not a replication, exploratory | Both capped portfolios grew faster than either unlevered fifth in point estimate, as the plan expected before any capped number. Nothing tests the size. |
| 4 | none, not a replication, exploratory | k was above 5 in 20 of the 83 months, so the ceiling of 5 set the leverage in about a quarter of them and the beta match set it in the rest. |
| 5 | none, not a replication, exploratory | The worst month at a ceiling of 5 lost 37 percent of the capital. June 2001, the beta match's first ruin, is not the worst month at either ceiling. |
| 6 | none, not a replication, exploratory | At either ceiling the levered low fifth's realised beta, 0.8584 and 1.5831, stayed below the high fifth's 2.0671, so over the whole sample neither capped portfolio carried the high fifth's market exposure. At a ceiling of 5 the beta match still set the leverage in 63 of the 83 months. |
| 7 | none, not a replication, exploratory | Borrowing at the bill rate flatters the levered side. The point estimate stays above 0 up to a spread of 0.0946 a year at a ceiling of 2 and 0.0661 at 5, and no outcome reads it. |

### What the entry concludes

Three things, and none confirms anything. The third adds figures the
write-up measured after the run, which `TestWhatThePostMeasured` in
[tests/test_low_beta_capped.py](../tests/test_low_beta_capped.py) pins.

1. **Capped at what a broker would lend, the rule is not decided on this
   file.** Neither ceiling ruined the portfolio, and both point estimates
   favour the levered low fifth. Neither gap is distinguishable from noise
   over 83 months. The claim's one-sided p-values of 0.1420 and 0.1129 are
   both above 0.05, so Benjamini-Hochberg rejects neither. The detectable gaps
   of 0.2168 and 0.3407 a year are each more than twice its own point
   estimate.
2. **Entry 45's ruin came with the beta match's leverage.** On the same
   portfolios and the same months, a ceiling of 5 lost no month's capital,
   though its worst month lost 37 percent of it. Location 4700's caveat stands
   beside the result: "one should be quite wary of using too much leverage on
   normally low-beta stocks".
3. **Each point estimate sits short of the line a 5 percent test draws, and
   no leverage up to 5 could have ruined a month.** The yearly Newey-West
   standard error of the gap is 0.0872 at a ceiling of 2 and 0.1370 at 5, so
   the one-sided 5 percent line, 1.645 times it, sits at 0.1434 and 0.2254.
   The gaps of 0.0934 and 0.1659 fall short of those lines, and each is under
   half of its own Y. June 2001, which ruined the beta match, returned
   −0.0835 at a ceiling of 2 and −0.2132 at 5. The smallest leverage that
   would have ruined any of the 83 months is 13.4118, for July 2002, above
   both ceilings. The write-up measured these after the run, so they are
   exploratory and decide nothing.

### What this entry cannot say

Five things, the plan's five limits, with the second widened and the third
and fifth corrected since the plan.

1. **Anything confirmed.** The ceilings were chosen after Entry 45's
   calendar, its leverage path, the ruin, eight months of both groups' returns
   and its side figures had been seen. The side figures are both Sharpe
   ratios, the growths, the realised betas and the full-sample Kelly leverage
   of 9.9884. Only
   a run registered before any number on a holdout could confirm a ceiling.
   The plan sends both ceilings to
   [issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s
   panel, unchanged, if either one holds here. Neither did.
2. **What the panel's makeup does to either side.** The panel lacks the
   stocks that left the index before 2007-11-23, as in Entry 45. It also
   counts each stock that joined the index between 1999 and 2007 for the
   years before it joined, and carries earlier companies' prices under WYN,
   DFS and SE.
3. **Whether the rule holds in later years.** The years 2000 to 2007 were
   past prices by the time the book printed the claim, so this span is not a
   holdout.
4. **What borrowing really cost.** The run borrows at the bill rate, which
   flatters the levered side. Row 7's break-even spread says how far the cost
   could rise before the point estimate reaches 0, and nothing about what a
   broker charged.
5. **Whether a margin call came inside a month.** Under FINRA Rule 4210's 25
   percent maintenance margin, a position levered 2 gets a call after a fall of
   a third within the month, and month-end closes cannot see that. Regulation
   T sets only the 50 percent needed to open the position.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/capped-low-beta-lessons.md](../blog/capped-low-beta-lessons.md) moves
with it, since that post quotes most of these figures. So does its one
figure, which `uv run python -m chan.low_beta_capped_figures` redraws.

The post also carries one whiteboard sketch in Lesson 5, added in a review
round before publishing. **Who breaks even first** draws each ceiling's yearly
gap falling to 0 as a borrowing spread is charged. The line at a ceiling of 2
falls from 0.0934 to 0 at row 7's 0.0946 and borrows 1 for each unit of
capital. The line at 5 starts higher at 0.1659, borrows 2.5134, falls about
two and a half times as steeply and reaches 0 first, at 0.0661. Each line is
drawn straight between those endpoints, because the charged gap departs from a
straight line by at most about 0.00034 a year over the span drawn. A change to
those figures moves the sketch too, and
`uv run python -m chan.capped_low_beta_whiteboard` redraws it through the same
`read_sources` and `build_portfolios`.

## Entry 49: the levered low-beta rule after the book, on IVV's S&P 500

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 4684, 4700
and 4709, the claim Entry 45 tests on Chan's own file. Shipped under
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526). Entry 45
cannot say whether the rule held after the book, because Chan's file holds
only the stocks still in the index in 2007 and its span sits inside the
samples the low-beta literature used. This entry runs Entry 45's registered
specification, with the changes the panel forces, on IVV's members at each
month-end from 2008-12, every holding month after the first edition's
release in November 2008.

Eleven rows, all derivable from
[tests/test_low_beta_holdout.py](../tests/test_low_beta_holdout.py), whose
pins run only where the owner's data archive is and `QT_ARCHIVE_RUN=1` asks
for them. Row 11, all but its 6,943, and the calendar's span in row 9 also
hold on committed files alone, and those tests run everywhere.

**Not decided.** "No gap in compounded growth detectable above about 0.2948 a
year over 208 months, where the point estimate is -0.0590." That sentence is
the criterion's fixed wording. Levered to the high fifth's beta, the low
fifth compounded 0.0590 a year more slowly than the unlevered high fifth, at
a Newey-West t of −0.4974, and a gap that size is well inside what the test
cannot tell from zero. Four formations, the first 2026-04-30, are skipped
under the second amendment named below, because the low fifth's mean beta
there was zero or below. No month is ruined. Location 4700's caveat stands
beside the result: "one should be quite wary of using too much leverage on
normally low-beta stocks", because returns have fat tails. The worst levered
month, December 2024, lost 0.8014 of the capital.

One row is a claim and ten are not replications. Row 1 takes the claim route
`### Rows that are not replications` describes. Rows 2 to 11 are the figures
the issue reports beside the verdict, which decide nothing.

Everything [issue 275](https://github.com/l3a0/quantitative-trading/issues/275)
registered carries over, and Entry 45 states its five rules.
[Issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s
section "What the panel forces", written on 2026-10-11 before any beta or
return was computed on this panel, lists the changes this panel makes
necessary. Four of them carry
the result, so they are stated here.

1. **The vintages.** The members, `research/filings/ivv/members.csv` and its
   holes file, read from IVV's 70 quarter-end schedules from 2008-12-31 to
   2026-06-30. The members' closes, the 817 `sp500` Alpha Vantage lines the
   members file maps to, adjusted and downloaded 2026-10-05. The market, SPY's
   `sp500` Alpha Vantage line, adjusted and downloaded 2026-10-11 for this run.
   The calendar, the committed raw SPY vintage downloaded 2026-10-03. FRED's
   TB3MS, downloaded 2026-09-30. [data/README.md](../data/README.md) says what
   each holds.
2. **Membership at t.** A stock is a candidate when it is a member of the
   schedule that sets month t and that member-month passes the panel's
   monthly coverage rule, with Example 7.7's year-earlier reason left out.
   Membership at t + 1 is not asked for.
3. **The holding month.** Each series stops at its last row that traded and
   moved. A stock that stops inside the holding month earns its return to its
   last close and holds cash after it. One whose last row is t, or that has no
   close at t, or a hole at t + 1, is not eligible at t. The first and the
   last of those exclusions still read t + 1, which is not known at t. At the
   208 formations kept they leave out 12 member-months whose last row is t and
   4 with a hole at t + 1, beside the 97,667 covered there.
4. **The span.** Formations run from 2008-12-31 to 2026-07-31, 212 of them,
   because the committed TB3MS ends at 2026-08. A day in the run with no SPY
   close would have stopped it, and none lacks one.

**Every figure is about the members the monthly rule keeps.** The panel has
a smaller survivor gap than Chan's file, not none. On the series the run
reads, each cut at its last row that traded, the monthly rule leaves out
6,943 of the 107,115 member-months. 6,816 of those fail the row check
against the filing, and 4,614 of the 6,816 carry a ticker absent from the
2026-06-30 schedule. Of the 2,187 member rows that fail the row check, only
697 carry a ticker still in that schedule. So the gap leans toward
companies that left the index, though a ticker absent from the last schedule
also marks a company that only changed its ticker. Membership is each
quarter-end schedule carried forward, so a change between schedules is dated
up to two months late, or five around the missing 2013-09-30 schedule.

Row 1 is **registered**, under two amendments, both of 2026-10-11. The first
is [issue 275](https://github.com/l3a0/quantitative-trading/issues/275)'s, which reads a levered month losing more than its capital as
the claim contradicted, and which this run inherits as part of the
specification. No month here triggers it. The second is
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s. The
plan says a low group whose mean beta is not positive refuses rather than
levers, and it says nothing of the verdict. The one run of the registered
specification refused at the 2026-04-30 formation, where that mean was
−0.0037, before anything the criterion reads had been computed. The owner
then ruled that such a formation is skipped, its holding month leaving every
series, so the criterion, the ruin rule and every side figure read the same
remaining months and N counts them. The amendment lists what had been seen.
So the skip rule was chosen after one such formation was visible, and N is
208 rather than 212. Every holding month comes after the first edition's
release in November 2008, so unlike Entry 45 this is a holdout for the claim,
as long as that edition prints it. This repository has read the rule only in
the 2021 revised edition. Rows 2 to 11 are **exploratory**.
The plan declared them, and each is a point estimate that nothing tests.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | a highly leveraged low-beta portfolio out-compounds an unleveraged high-beta one | the rule, with no figure | location 4709, the leverage matched to beta at location 4684 |
| 2 | a low-beta portfolio has a higher Sharpe ratio | the premise, from "empirical studies", with no figure | location 4684 |
| 3 to 11 | the realised growth, the leverage path, the realised betas, the Kelly reading, the counts, the flagged stock-months, the calendar, the skipped formations and the survivor gap | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | the claim: any levered month at −1 or below, else the Newey-West t of d against 1.645, over the months the skip leaves | no ruined month. Over 208 months, 12 times the mean of d is −0.0590, the Newey-West t is −0.4974 at lag 4, and the detectable gap Y is 0.2948. The worst levered month, December 2024, returned −0.8014, at a k of 12.3588 on the low fifth's −0.0616 | `TestTheVerdict::test_the_claim_is_not_decided`, `::test_the_gap_its_newey_west_t_and_y`, `::test_the_wording`, `::test_no_month_is_ruined` and `::test_the_worst_month_levered_the_low_fifth_by_12_3588` |
| 2 | each portfolio's Sharpe ratio on its monthly return over the bill, times √12 | levered low 0.5223, low 0.8607, high 0.6770 | `TestTheSideFigures::test_growth_sharpe_and_realised_beta` |
| 3 | realised compounded growth, 12 times the mean monthly log return | levered low 0.1023, low 0.1069, high 0.1613, SPY 0.1378 | `TestTheSideFigures::test_growth_sharpe_and_realised_beta` and `::test_spys_growth` |
| 4 | k over the 208 formations kept, and the low group's mean beta | k mean 3.8247, from 1.8988, formed 2015-12-31, to 27.9727, formed 2025-03-31. Low group 0.0563 to 0.7317 | `TestTheSideFigures::test_the_leverage_path` and `::test_the_low_groups_mean_beta_over_the_formations_kept` |
| 5 | each series' realised beta, the slope of its monthly return over the bill on SPY's | levered low 1.8316, low 0.5580, high 1.6461, SPY 1 | `TestTheSideFigures::test_growth_sharpe_and_realised_beta` |
| 6 | location 4709's Kelly reading, look-ahead: the low portfolio's full-sample m / s², and the Gaussian growth r + S²/2 there | leverage 7.3632, Gaussian growth 0.0136 + 0.3704 = 0.3840, against the high portfolio's realised 0.1613 | `TestTheSideFigures::test_the_kelly_reading_labelled_look_ahead` |
| 7 | member-months, covered members and eligible stocks over the 208 formations, and each portfolio's size. The run prints every formation's row | 104,600 member-months, 97,667 covered, 97,302 eligible with a beta. 389 to 501 eligible per formation, each portfolio 77 to 100, 19,377 stock-months each. The two exclusions that read t + 1 leave out 12 member-months whose last row is t and 4 with a hole at t + 1 | `TestTheSideFigures::test_the_counts` and `::test_the_exclusions_that_read_t_plus_1` |
| 8 | stock-months with a scale-break flag between the beta window's first return and the holding month's end | 34 low and 321 high. The closes the run reads flag 820 closes in 98 stocks | `TestTheScaleBreakDecision::test_34_low_and_321_high_stock_months_carry_a_flag` and `::test_820_flagged_days_in_98_stocks` |
| 9 | the calendar | 4,695 days from 2008-01-02 to 2026-08-31, the first formation 252 rows in. 212 formations from 2008-12-31 to 2026-07-31. 121 series stop before their file's last row, and no close falls off the calendar | `TestTheRunsHelpers::test_the_frame_starts_252_rows_before_2008_12_31_and_ends_2026_08_31`, `TestTheWindow::test_212_formations_of_which_4_are_skipped_leave_208_months`, `::test_formed_2008_12_31_to_2026_03_31_held_to_2009_01_30_to_2026_04_30` and `TestTheVintages::test_121_series_stop_before_their_files_last_row_and_none_is_off_the_calendar` |
| 10 | the formations the second amendment skips, with each group's mean beta | four, the last four: formed 2026-04-30, low −0.0037 and high 1.8278. Formed 2026-05-29, low −0.0652 and high 1.8696. Formed 2026-06-30, low −0.1429 and high 1.9202. Formed 2026-07-31, low −0.2083 and high 1.9536 | `TestTheWindow::test_the_four_skipped_formations_are_the_last_four` |
| 11 | the survivor gap, on the committed members file and on the series the run cuts | 6,816 of 107,115 member-months fail the row check against the filing, and 4,614 of them carry a ticker absent from the 2026-06-30 schedule. 697 of the 2,187 failing member rows carry a ticker in that schedule. The monthly rule leaves out 6,927 member-months on the manifest's spans and 6,943 on the series the run cuts | `TestTheCoverageWithoutRank::test_the_survivor_label_counts` and `TestTheSideFigures::test_the_survivor_label` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | did not reproduce | Not decided, which the plan maps to this value: "No gap in compounded growth detectable above about 0.2948 a year over 208 months, where the point estimate is -0.0590." The point estimate favours the unlevered high fifth, and 0.2948 a year is the gap this test finds four times in five. Four formations, the first 2026-04-30, are skipped under [issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s amendment of 2026-10-11, which was ruled after the first was visible. Membership is the members the monthly rule keeps, which leans toward companies still in the index. |
| 2 | none, not a replication | The low fifth's Sharpe ratio is 0.8607 and the high fifth's 0.6770. Nothing tests the difference, so it neither confirms nor refutes location 4684's premise, and it decides nothing because the claim is about growth. |
| 3 | none, not a replication | Unlevered, the high fifth compounded at 0.1613 a year, the low fifth at 0.1069 and SPY at 0.1378. Levered, the low fifth reached 0.1023, below its own unlevered growth. Nothing tests any of these gaps. |
| 4 | none, not a replication | Over the formations kept, the low fifth's mean beta at formation bottomed at 0.0563 and k peaked at 27.9727, both at the formation of 2025-03-31, against Entry 45's 69.0762. |
| 5 | none, not a replication | The levered low's realised beta of 1.8316 is above the high fifth's 1.6461, so after the fact the match overshot the beta it aimed at, as on Chan's file. The low fifth's 0.5580 sits inside the range its formations gave. SPY's is 1 by construction. |
| 6 | none, not a replication | Look-ahead. The Kelly leverage can only be known from the whole sample, and the 0.3840 is the Gaussian growth r + S²/2, a formula on the sample's moments that no portfolio realised. The reading is reported because location 4709 means it, and it decides nothing. |
| 7 | none, not a replication | Every formation kept fills both fifths, so the refusal for an empty portfolio never fires. |
| 8 | none, not a replication | No window is refused, as `tests/test_scale_breaks.py` records for this panel. The high fifth holds 321 flagged stock-months and the low fifth 34. |
| 9 | none, not a replication | The first formation is the one the registration named, and the 212 formations are the count the audit took from the calendar before the run. |
| 10 | none, not a replication | The low fifth's mean beta fell through zero in the run's last four formations and kept falling, so the skips end the comparison in April 2026 rather than August. |
| 11 | none, not a replication | The row check against the filing fails mostly on tickers absent from the last schedule, 4,614 of 6,816 member-months, which marks a company that left the index or changed its ticker. Which fifth that flatters is not measured here. |

### The skipped formations

The registered plan refuses a formation whose low fifth has a mean beta of
zero or below, because no leverage brings a beta of zero or less to the high
fifth's. The four that do are the last four the span allows, 2026-04-30 to
2026-07-31, each lower than the one before. Over each one's 252 days, the
lowest fifth's stocks moved, on average, against the market. Skipping them
leaves 208 holding months, from January 2009 to April 2026.

### What the entry concludes

Three things, and the first is the verdict. The third adds figures the
write-up measured after the run, which `TestWhatThePostCounted` and
`TestWhatThePostMeasured` in
[tests/test_low_beta_holdout.py](../tests/test_low_beta_holdout.py) pin.

1. **On IVV's S&P 500 from 2009, the rule is not decided.** Levered to
   the high fifth's beta, the low fifth's compounded growth trailed the
   unlevered high fifth's by 0.0590 a year, at a Newey-West t of −0.4974. The
   test finds a gap of 0.2948 a year four times in five, so the run says
   little either way. That is Not decided, and it maps to
   `did not reproduce`.
2. **The beta match did not ruin the portfolio here, and it came closest in
   December 2024.** Over the formations kept, the low fifth's mean beta at
   formation bottomed at 0.0563 and k peaked at 27.9727, against Entry 45's
   69.0762. The worst levered month lost 0.8014 of the capital. In the
   last four formations the match had no leverage to offer at all. The low
   fifth's Sharpe ratio of 0.8607 against the high fifth's 0.6770 is an
   untested point estimate that decides nothing.
3. **The data reject only a large levered advantage, and one month sets the
   estimate's sign.** The gap's standard error is 0.1185 a year, so a
   one-sided test at 5 percent rejects every levered advantage above 0.1360
   a year. December 2024's d of −1.5624 is the lowest of the 208. Without it,
   twelve times the mean of d is +0.0313, and without it and March 2026's
   −1.1582 it is +0.0989. No month reached its own ruin line, and the match
   asked December 2024 for 0.80 of the leverage that ruins it, the largest
   share of any month. The 2,187 member rows failing the row check against
   the filing split 1,186 with no close, 697 with a wrong price and 304 with
   no series. 26,353 of all 35,205 member rows carry a ticker still in the
   2026-06-30 schedule, against 697 of the 2,187 failing rows. On Chan's
   file the close at t + 1 removed no company that left, only 17 stocks
   missing a month-end close at six formations. Measured after the run, so
   exploratory, and it decides nothing.

### What this entry cannot say

Four things.

**Whether a smaller gap exists.** This test finds a gap below 0.2948 a year
less than four times in five, and the point estimate of −0.0590 sits well
inside that. The panel holds no months beyond these.

**What survivorship does to either side.** 6,816 member-months fail the row
check against the filing, and 4,614 of them carry a ticker absent from the
2026-06-30 schedule, which marks a company that left the index or changed
its ticker. Which fifth they would have joined is not measured here.

**Whether fat tails are the cause of the worst month.** In December 2024 a k
of 12.3588 turned the low fifth's return of −0.0616 into a levered loss of
0.8014 of the capital. Location 4700's caveat
names the risk, and how near the run came to ruin depends on that month alone.

**What the model's half of the argument says.** Location 4684's equal average
returns need market capitalisation and book value at each date, which
[issue 273](https://github.com/l3a0/quantitative-trading/issues/273) carries.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/low-beta-holdout-lessons.md](../blog/low-beta-holdout-lessons.md) moves
with it, since that post quotes most of these figures. So does its one
figure, which `QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.low_beta_holdout_figures`
redraws where the archive is.

## Entry 50: the Khandani-Lo reversal on the S&P 400, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 2137 for the
explanation and location 2236, at the end of Example 3.8 on p. 78, for the
exercise. Shipped under
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303).

This entry is not a replication, for Entry 44's reason. Chan explains the
reversal's collapse on the S&P 500 by saying "most of the returns are
generated by small and microcap stocks", and leaves rerunning the strategy on
the S&P 400 and S&P 600 as an exercise with no figure for either. Entry 44 ran
the S&P 600 half on Chan's own file. This entry runs the S&P 400 half and
reads the three universes as one ladder, so the explanation is tested on three
points rather than two. Its tables drop the published-figure, gap and verdict
columns, as Entry 44's do.

Sixteen rows, all derivable from
[tests/test_khandani_lo_mid_caps.py](../tests/test_khandani_lo_mid_caps.py).
The module is `chan.khandani_lo_mid_caps`. Its S&P 500 and S&P 600 runs give
the same floats as `chan.khandani_lo_small_caps`, and land on the figures
Entries 8, 10 and 44 report, which `TestChansTwoFiles` holds.

**Before costs the order holds on the closes and is partial on the opens, so
the reading is mixed.** On the closes the S&P 400 earns 2.0338, between the
S&P 500's 0.2510 and the S&P 600's 3.4086. On the opens it earns 3.4533, below
both the S&P 500's 4.4202 and the S&P 600's 5.3052. So the step from the
S&P 500 to the S&P 400 rises on the closes and falls on the opens, and the
step from the S&P 400 to the S&P 600 rises on both. One of the four steps is
more than twice its standard error, the closes' step from the S&P 500 to the
S&P 400.

**The control finds the ordering separable from how the panel was built.**
The S&P 400 figure
comes from Alpha Vantage, downloaded in 2026, while both neighbours come from
Chan's vendor files of 2007 and 2008. So the run also builds the S&P 600 the
way the S&P 400 panel is built and reads it against Chan's S&P 600 file. That
control lands 0.1108 above Chan's file on the closes and 0.7244 below it on
the opens. Both gaps are smaller than the S&P 400 figure's distance to its
nearer neighbour, 1.3748 on the closes and 0.9669 on the opens, so the
declared reading applies.

**Every reading was declared before any figure was computed.** Three texts on
the tracker fix it.

1. [Issue 249's comparison declaration](https://github.com/l3a0/quantitative-trading/issues/249#issuecomment-6104832067)
   reads each figure against its neighbours at the same price, cost treatment
   and specification, and sizes each gap with Memmel's (2003) correction of
   Jobson and Korkie (1981). A gap more than twice its standard error reads
   as larger than one year's noise. Its section for
   [issue 303](https://github.com/l3a0/quantitative-trading/issues/303) extends the
   direction reading to an order.
2. [The body of issue 303](https://github.com/l3a0/quantitative-trading/issues/303)
   declares the words for three universes. Before costs, the order holds
   when the S&P 500 sits below the S&P 400 and the S&P 400 below the S&P 600.
   It is fully reversed when both steps fall, and partial otherwise. Holding
   at both prices points the way Chan says, fully reversed at both points
   against it, and anything else is mixed, with each step reported. The body
   also adds the control and its rule. If the control's gap exceeds, in
   absolute value, the S&P 400 figure's distance to its nearer neighbour at
   either price, the ordering is not separable from how the panel was built
   and no direction is read.
3. [The declarations before the run](https://github.com/l3a0/quantitative-trading/issues/303#issuecomment-6116653928)
   fix the two panels, the common days and the flagged days, from prices
   and outside evidence alone, before any return was computed on either
   panel.

Every row reads the same vintages, window and specification, so they are
stated once here.

1. **The vintages.** The S&P 500 is Entry 8's `spx_20071123/`, the index as
   it stood on 2007-11-23. The S&P 600 is Entry 44's `ijr_20080114/`, the
   index as it stood on 2008-01-14. The S&P 400 is IJH's 401 holdings in
   iShares Trust's N-Q for 2007-12-31, accession `0001193125-08-043324`,
   mapped and checked in `research/filings/ijh/members.csv`, and priced from
   the `sp400` cross-section of the owner's archive, Alpha Vantage's
   `TIME_SERIES_DAILY_ADJUSTED` downloaded on 2026-10-11. A run holds the 285
   holdings that pass the price check and have a 2006 row before the vendor's
   cut-off. The control is IJR's 602 holdings in the same N-Q, in
   `research/filings/ijr/members_2007-12-31.csv`, held by the same rule, which
   keeps 385, and priced from the `sp600` cross-section, downloaded on
   2026-10-05 and 2026-10-11. `tests/test_sp400_panel.py` pins both members
   files and every count. **Every figure here is about survivors**, on all
   four panels.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days, the same days
   in all four panels at both prices, which `TestThePanels` holds. So the gaps
   pair two daily profit series day by day through `same_days` as written,
   and nothing is intersected.
3. **The specification.** Rule B, `chan.khandani_lo.reversal` run unchanged,
   on the closes and on the opens. On the archive panels a close is the
   vendor's `adjusted_close`, and an open is `open × adjusted_close / close`
   on the same day, because the vendor adjusts only the close. Chan's files
   are read as Entry 44 reads them. The cost is 5 basis points on each side of
   a change in weight, and the Sharpe ratio is √252 times the mean over the
   standard deviation with no risk-free rate. Each run gives Entry 8's three
   figures: before costs, after costs with Chan's two quirks kept, and after
   costs with the first day charged.

Every result here is **EXPLORATORY**. The run applies a rule Chan published,
unchanged, to stocks from the S&P 400 and S&P 600, the two universes his
exercise names, so it says
which way each step points on one year of survivors and how each compares with
that year's noise. It confirms nothing about Chan's explanation, and a reading
that pointed his way would earn a registered test on data the run has not
seen.

### What the book stated

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The S&P 400 on the closes, before costs | nothing, the exercise asks for the run and prints no figure | location 2236, p. 78 |
| 2 to 6 | The S&P 400's other five figures | nothing | n/a |
| 7 to 10 | Each before-cost step against its standard error | nothing | n/a |
| 11 to 15 | The control | nothing, the control is this issue's own | n/a |
| 16 | Where the returns come from | "most of the returns are generated by small and microcap stocks", a claim rather than a figure | Kindle location 2137 |

Khandani and Lo's 4.47 for 2006, at location 2099, takes no row, for Entry
44's reason. The report prints it and the entry judges nothing against it.

### What this repo computed

| # | Price and specification | S&P 500 | S&P 400 | S&P 600 | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | closes, before costs | 0.2510 | 2.0338 | 3.4086 | `TestTheMidCapFigures::test_closes` and `TestChansTwoFiles::test_the_pinned_figures` |
| 2 | closes, after costs, first day uncharged and its NaN counted as 0 | −3.1884 | −1.4444 | −0.3702 | the same |
| 3 | closes, after costs, first day charged | −3.2337 | −1.4524 | −0.3255 | the same |
| 4 | opens, before costs | 4.4202 | 3.4533 | 5.3052 | `TestTheMidCapFigures::test_opens` and `TestChansTwoFiles::test_the_pinned_figures` |
| 5 | opens, after costs, first day uncharged and its NaN counted as 0 | 0.7834 | 0.4589 | 2.0147 | the same |
| 6 | opens, after costs, first day charged | 0.8293 | 0.4884 | 2.0257 | the same |

Each step is the smaller index's figure less the larger's, so a positive
step rises as capitalisation falls.

| # | Step before costs | Gap | Standard error | Correlation | z | One year's noise | Assertion |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | closes, S&P 400 less S&P 500 | +1.7828 | 0.8114 | 0.6758 | +2.1973 | beyond | `TestTheGapsToBothNeighbours::test_the_gap` |
| 8 | closes, S&P 600 less S&P 400 | +1.3748 | 1.0113 | 0.5028 | +1.3593 | within | the same |
| 9 | opens, S&P 400 less S&P 500 | −0.9669 | 0.8972 | 0.6188 | −1.0777 | within | the same |
| 10 | opens, S&P 600 less S&P 400 | +1.8519 | 1.1948 | 0.3250 | +1.5500 | within | the same |

The control is read with its three exclusions, which is primary, and
without them. Its gap is its figure less Chan's S&P 600 file's, before costs.

| # | Specification | With the exclusions | Without them | Assertion |
| --- | --- | --- | --- | --- |
| 11 | closes, before costs, after costs uncharged, after costs charged | 3.5194, 0.0655, 0.0575 | 1.8962, 0.9858, 0.9798 | `TestTheControl::test_the_figures_with_and_without_the_exclusions` |
| 12 | opens, the same three | 4.5808, 1.6774, 1.6903 | 2.6002, 1.5671, 1.5679 | the same |
| 13 | closes, gap to Chan's file, standard error, correlation, z | +0.1108, 0.4943, 0.8836, +0.2241, within one year's noise | −1.5124, 1.2979, 0.1758, −1.1653, within | `TestTheControl::test_the_gap_to_chans_file` and `::test_the_gap_without_the_exclusions` |
| 14 | opens, the same | −0.7244, 0.5768, 0.8484, −1.2559, within | −2.7050, 1.2882, 0.2070, −2.0998, beyond | the same |
| 15 | each gap against the S&P 400's distance to its nearer neighbour, 1.3748 on the closes and 0.9669 on the opens | inside at both prices, so separable | outside at both | `TestTheControl::test_the_ordering_is_separable_with_the_exclusions_and_not_without` |

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 16 | rows 1 and 4 read against the declaration | the order holds on the closes and is partial on the opens, where the step from the S&P 500 to the S&P 400 does not rise, so mixed | `TestTheRunsReading::test_it_reads_mixed` |

The S&P 500 and S&P 600 columns are Entry 8's rows 1 to 3, Entry 10's rows 6
to 8 and Entry 44's rows 1 to 6.
`TestChansTwoFiles::test_they_are_the_small_cap_modules_runs_to_the_bit`
holds that this module's runs give the same floats as
`chan.khandani_lo_small_caps`, and `TestChansTwoFiles::test_the_pinned_figures`
holds them at the four decimals those entries quote.

### What each row says

| # | Why it is here |
| --- | --- |
| 1 | The primary reading on the closes. The S&P 400 sits between its neighbours. |
| 2 | After Chan's costs the S&P 400 still loses on the closes, by less than the S&P 500 and more than the S&P 600. |
| 3 | The same, with the first day charged. |
| 4 | The primary reading on the opens. The S&P 400 sits below both neighbours, so the order breaks at its first step. |
| 5 | After costs the S&P 400 keeps a profit on the opens, below both neighbours. The run charges all three universes 5 basis points, so these rows flatter the smaller indexes. |
| 6 | The same, with the first day charged. |
| 7 | The one step beyond one year's noise. |
| 8 | The closes' second step rises and sits within noise. |
| 9 | The step that breaks the order is about one standard error, so one year cannot tell it from noise. |
| 10 | The opens' second step rises and sits within noise. |
| 11 | Built the way the S&P 400 panel is, the S&P 600 lands near Chan's file on the closes. Without the exclusions it lands far below. |
| 12 | On the opens it lands lower than Chan's file, and without the exclusions further below still. |
| 13 | The closes' control gap is about a fifth of a standard error. |
| 14 | The opens' control gap is the larger, and it is still inside the step it is read against. |
| 15 | The control rule. With the exclusions, how the panel was built moves the S&P 600 less than the S&P 400's nearer step at both prices. Without them it would move it more at both. |
| 16 | The declared reading. It rests on rows 1 and 4, and rows 7 to 10 say three of its four steps are within noise. |

### The flagged days

`chan.series.scale_breaks` flags a day when a stock's price moves past the
factor-of-1.6 bound. Over 2005-12-01 to 2006-12-31, on each held member's own
adjusted close and adjusted open, it flags five days, each on both prices.
They were classified before any strategy figure was computed, in
[the declarations before the run](https://github.com/l3a0/quantitative-trading/issues/303#issuecomment-6116653928),
under [issue 249](https://github.com/l3a0/quantitative-trading/issues/249)'s
rule. A real traded move stays in, and an unadjusted split
or a splice has the member's return on that day set to NaN.

1. **KCI on 2006-08-04, in the S&P 400, stays in.** The close went from
   42.58 to 24.95, on 13.6 million shares against 1.5 million the day
   before. Kinetic Concepts'
   [8-K of 2006-08-03](https://www.sec.gov/Archives/edgar/data/0000831967/000134100406002101/pal211033.txt)
   reports a jury verdict that a competitor's device did not infringe its
   patents. `TestTheFlaggedDayKept` holds that its return is finite and
   weighted on both prices.
2. **CORSQ on 2006-05-19, in the control, is excluded.** The raw close went
   from 59.21 to 30.00, an unadjusted 2-for-1 split. Corus Bankshares'
   [8-K](https://www.sec.gov/Archives/edgar/data/51939/000127528706002929/cb5932.htm)
   records the distribution on 2006-05-18.
3. **ZD on 2006-05-25, in the control, is excluded.** The raw close went from
   51.67 to 28.15, another unadjusted 2-for-1 split. An
   [ISE circular](https://iseoptions.com/marketplace/files/adjustments/2006/2006-103-J2_Global_Communications-_Inc._(JCOM)_2_for_1_Stock_Split-20060522.pdf)
   gives the ex-date as 2006-05-25.
4. **MAG on 2006-01-10, in the control, is excluded.** One day prints 1.295
   between closes of 3.32 and 3.38, on 56,800 shares against 1.9 million the
   day before, and the open prints the same 1.295. `scale_breaks` flags that
   day and the next.
   [Issue 249](https://github.com/l3a0/quantitative-trading/issues/249)'s
   rule names splits and splices, and a one-day
   bad print is neither, so the declarations extended the rule to it: its
   price on 2006-01-10 is NaN on both prices, which makes the returns on
   2006-01-10 and 2006-01-11 NaN.

`TestTheFlaggedDaysRawRows` pins each raw close and volume quoted above.

Rule B reads prices, so `chan.khandani_lo_mid_caps.exclude` makes a split
day's return NaN by carrying the member under two columns, one holding its
prices before the day and one from the day on. Every price and every other
return stays what it was, and so does each day's count of priced members.
Rule B weights a return that is not finite at 0, so the member closes its
position on the split day and opens it again the next. After costs this
charges closing the position and reopening it, which a NaN return alone would
not, so the control's after-cost rows include that charge. A literal NaN
return on the two split days gives 0.0657 and 0.0577 on the closes and 1.6775
and 1.6904 on the opens, against rows 11 and 12's 0.0655, 0.0575, 1.6774 and
1.6903.
`TestTheControl::test_a_literal_nan_return_on_the_split_days_moves_only_the_after_cost_figures`
holds those four, and that the before-cost figures do not move, so neither
does the reading.
`TestTheControl::test_the_exclusion_changes_the_returns_on_exactly_the_declared_cells`
holds that on both prices the control's returns change on exactly the four
cells above, and `TestTheExclusions` holds the same on frames built by hand.

The exclusions decide whether the control passes its rule. Without them the
control lands 1.5124 below Chan's file on the closes and 2.7050 below on the
opens, rows 13 and 14, which would put both outside the S&P 400's steps. The
S&P 400 panel has nothing excluded, so it has one set of figures.

The module does not call the scale-break guard,
`chan.series.refuse_window_crossing_a_break`, and its docstring says why. The
guard would stop the run over these five days, and their treatment was
decided in writing before the run.

### The holdings the run leaves out

IJH held 401 stocks on 2007-12-31. The run holds 285 of them, 71.1% by count
and 74.8% by value, and leaves out 116 in three groups.

1. **103 fail the price check.** The check asks whether Alpha Vantage's raw
   close on 2007-12-31 times the filing's share count equals the filing's
   value, within half a dollar plus half a share. Seven fail on the price,
   62 have a series whose first row comes after 2007-12-31, such as DRS's,
   which starts in 2022, and LEA's, which starts in 2009, and 34 have no
   series at all.
2. **10 start on 2006-12-28, the vendor's cut-off.** Alpha Vantage starts
   many histories that day whatever the company's age, so two rows in 2006
   are the vendor's cut-off rather than a listing.
3. **3 have no 2006 row.** EXH and BR did not trade in 2006. PALM did, and
   its series starts on 2007-10-25, so its absence is a gap in the vendor's
   data rather than a late listing.

A passing member with only part of 2006 is held, as on Chan's files, since
rule B weights a return that is not finite at 0. That covers 10 members with
1 to 7 missing days and HBI, KBR and CMG, which listed during 2006.
`tests/test_sp400_panel.py` pins every count and ticker here, and
`TestTheManifestLines` pins where the 62 series start,
`TestThePanels::test_the_share_of_each_filing_a_run_holds` pins the two
shares, and
`uv run python -m chan.sp400_panel report ijh` and `history ijh` print the
list below.

Every left-out name was in IJH on 2007-12-31. All but EXH and BR are left out
by how Alpha Vantage serves their tickers today rather than by anything in
2006. The members file's notes record what became of some of the companies,
such as Cephalon, which Teva bought in 2011, Foundry Networks, which Brocade
bought in 2008, and IndyMac and Colonial BancGroup, whose banks failed in 2008
and 2009. Nothing here counts those fates across the 116. The control is built
by the same rule and keeps 385 of IJR's 602, 64.0% by count, so it carries the
same kind of selection.

| Filing row | Ticker | Holding | Why the run leaves it out |
| --- | --- | --- | --- |
| 1 | GYI | Getty Images Inc. | price check: no series |
| 6 | DRS | DRS Technologies Inc. | price check: no row on 2007-12-31 |
| 14 | TBL | Timberland Co. Class A | first row on 2006-12-28, the vendor's cut-off |
| 15 | WRC | Warnaco Group Inc. (The) | price check: no row on 2007-12-31 |
| 19 | LEA | Lear Corp. | price check: no row on 2007-12-31 |
| 24 | CYN | City National Corp. | price check: no row on 2007-12-31 |
| 25 | CNB | Colonial BancGroup Inc. (The) | price check: no series |
| 28 | FMER | FirstMerit Corp. | price check: no row on 2007-12-31 |
| 30 | SNV | Synovus Financial Corp. | price check: the close disagrees with the filing |
| 31 | TCF | TCF Financial Corp. | price check: the close disagrees with the filing |
| 34 | WL | Wilmington Trust Corp. | price check: no series |
| 37 | AFFX | Affymetrix Inc. | price check: no row on 2007-12-31 |
| 39 | LIFE | Invitrogen Corp. | price check: no row on 2007-12-31 |
| 40 | MLNM | Millennium Pharmaceuticals Inc. | price check: no series |
| 48 | CHMT | Chemtura Corp. | price check: no row on 2007-12-31 |
| 52 | LZ | Lubrizol Corp. | price check: no row on 2007-12-31 |
| 58 | VAL | Valspar Corp. (The) | price check: no row on 2007-12-31 |
| 59 | ACI | Arch Coal Inc. | price check: no row on 2007-12-31 |
| 63 | CPS | ChoicePoint Inc. | price check: no row on 2007-12-31 |
| 64 | COCO | Corinthian Colleges Inc. | price check: no row on 2007-12-31 |
| 69 | ESI | ITT Educational Services Inc. | price check: no row on 2007-12-31 |
| 73 | MPS | MPS Group Inc. | price check: no series |
| 74 | NCI | Navigant Consulting Inc. | price check: no row on 2007-12-31 |
| 75 | PPDI | Pharmaceutical Product Development Inc. | price check: no series |
| 80 | BID | Sotheby’s Holdings Inc. Class A | price check: no row on 2007-12-31 |
| 83 | VCI | Valassis Communications Inc. | first row on 2006-12-28, the vendor's cut-off |
| 85 | DBD | Diebold Inc. | price check: no row on 2007-12-31 |
| 89 | MENT | Mentor Graphics Corp. | price check: no row on 2007-12-31 |
| 91 | PALM | Palm Inc. | no 2006 row, first row 2007-10-25 |
| 92 | SRX | SRA International Inc. Class A | price check: no row on 2007-12-31 |
| 95 | ACV | Alberto-Culver Co. | price check: no row on 2007-12-31 |
| 97 | IM | Ingram Micro Inc. Class A | price check: no row on 2007-12-31 |
| 99 | ACF | AmeriCredit Corp. | price check: no row on 2007-12-31 |
| 100 | EV | Eaton Vance Corp. | price check: no row on 2007-12-31 |
| 101 | IMB | IndyMac Bancorp Inc. | price check: no series |
| 102 | JEF-1 | Jefferies Group Inc. | first row on 2006-12-28, the vendor's cut-off |
| 106 | ILA | Aquila Inc. | price check: no series |
| 109 | EAS | Energy East Corp. | price check: no series |
| 115 | NST | NSTAR | price check: no series |
| 118 | PSD | Puget Energy Inc. | price check: no series |
| 120 | NVE | Sierra Pacific Resources Corp. | price check: no series |
| 121 | WR | Westar Energy Inc. | price check: no row on 2007-12-31 |
| 125 | HUBB | Hubbell Inc. Class B | price check: no row on 2007-12-31 |
| 130 | KEM | KEMET Corp. | price check: no row on 2007-12-31 |
| 132 | TNB | Thomas & Betts Corp. | price check: no series |
| 133 | VARI | Varian Inc. | price check: no series |
| 148 | HTSI | Ruddick Corp. | price check: no series |
| 149 | SFD | Smithfield Foods Inc. | price check: no row on 2007-12-31 |
| 154 | TIN | Temple-Inland Inc. | price check: no row on 2007-12-31 |
| 161 | EYE | Advanced Medical Optics Inc. | price check: no row on 2007-12-31 |
| 162 | BEC | Beckman Coulter Inc. | price check: no row on 2007-12-31 |
| 165 | GPRO | Gen-Probe Inc. | price check: no row on 2007-12-31 |
| 169 | ISRG | Intuitive Surgical Inc. | price check: the close disagrees with the filing |
| 174 | VMSI | Ventana Medical Systems Inc. | price check: no row on 2007-12-31 |
| 175 | AHG | Apria Healthcare Group Inc. | price check: the close disagrees with the filing |
| 178 | HMA | Health Management Associates Inc. Class A | price check: no row on 2007-12-31 |
| 182 | LNCR | Lincare Holdings Inc. | price check: no series |
| 183 | PSYS | Psychiatric Solutions Inc. | price check: no row on 2007-12-31 |
| 192 | FBN | Furniture Brands International Inc. | price check: the close disagrees with the filing |
| 193 | AM | American Greetings Corp. Class A | price check: no row on 2007-12-31 |
| 201 | CGI | Commerce Group Inc. | price check: the close disagrees with the filing |
| 206 | HCC | HCC Insurance Holdings Inc. | price check: no row on 2007-12-31 |
| 210 | PMI | PMI Group Inc. (The) | price check: no row on 2007-12-31 |
| 211 | PL | Protective Life Corp. | price check: no row on 2007-12-31 |
| 216 | AVCT | Avocent Corp. | price check: no row on 2007-12-31 |
| 217 | DRIV | Digital River Inc. | price check: no row on 2007-12-31 |
| 219 | MFE | McAfee Inc. | first row on 2006-12-28, the vendor's cut-off |
| 242 | NVRI | Harsco Corp. | price check: no row on 2007-12-31 |
| 243 | LANC | Lancaster Colony Corp. | price check: no series |
| 250 | BLC | Belo Corp. | first row on 2006-12-28, the vendor's cut-off |
| 251 | AUD | Entercom Communications Corp. | price check: no series |
| 254 | MEG | Media General Inc. Class A | price check: no row on 2007-12-31 |
| 264 | EAC | Encore Acquisition Co. | price check: no row on 2007-12-31 |
| 265 | FST | Forest Oil Corp. | price check: no row on 2007-12-31 |
| 268 | NFX | Newfield Exploration Co. | price check: no row on 2007-12-31 |
| 271 | PXP | Plains Exploration & Production Co. | first row on 2006-12-28, the vendor's cut-off |
| 272 | PDE | Pride International Inc. | price check: no series |
| 273 | KWKAQ | Quicksilver Resources Inc. | price check: no row on 2007-12-31 |
| 276 | EXH | Exterran Holdings Inc. | no 2006 row, first row 2007-08-21 |
| 278 | GRP | Grant Prideco Inc. | price check: no series |
| 283 | CEPH | Cephalon Inc. | price check: no series |
| 284 | ENDP | Endo Pharmaceuticals Holdings Inc. | price check: no series |
| 285 | MRX | Medicis Pharmaceutical Corp. Class A | price check: no row on 2007-12-31 |
| 286 | NTY | NBTY Inc. | first row on 2006-12-28, the vendor's cut-off |
| 288 | PRX | Par Pharmaceutical Companies Inc. | first row on 2006-12-28, the vendor's cut-off |
| 290 | SEPR | Sepracor Inc. | price check: no series |
| 291 | VRX | Valeant Pharmaceuticals International | price check: the close disagrees with the filing |
| 292 | WOOF | VCA Antech Inc. | price check: no row on 2007-12-31 |
| 299 | BRE | BRE Properties Inc. Class A | price check: no series |
| 303 | EQY | Equity One Inc. | price check: no row on 2007-12-31 |
| 311 | NHP | Nationwide Health Properties Inc. | price check: no row on 2007-12-31 |
| 321 | BJ | BJ’s Wholesale Club Inc. | price check: no row on 2007-12-31 |
| 323 | BGP | Borders Group Inc. | price check: no series |
| 327 | CHRS | Charming Shoppes Inc. | price check: no row on 2007-12-31 |
| 331 | CWTR | Coldwater Creek Inc. | price check: no series |
| 332 | PSS | Collective Brands Inc. | price check: no series |
| 338 | NDN | 99 Cents Only Stores | first row on 2006-12-28, the vendor's cut-off |
| 340 | PSUN | Pacific Sunwear of California Inc. | price check: no series |
| 345 | SKS | Saks Inc. | first row on 2006-12-28, the vendor's cut-off |
| 352 | ATML | Atmel Corp. | price check: no row on 2007-12-31 |
| 355 | FCS | Fairchild Semiconductor International Inc. Class A | price check: no row on 2007-12-31 |
| 367 | BR | Broadridge Financial Solutions Inc. | no 2006 row, first row 2007-04-02 |
| 370 | DNB | Dun & Bradstreet Corp. (The) | price check: no row on 2007-12-31 |
| 373 | MV | Metavante Technologies Inc. | price check: no series |
| 377 | SY | Sybase Inc. | price check: no row on 2007-12-31 |
| 378 | WIND | Wind River Systems Inc. | price check: no series |
| 379 | ADCT | ADC Telecommunications Inc. | price check: no row on 2007-12-31 |
| 381 | CBB | Cincinnati Bell Inc. | price check: no series |
| 382 | CTV | CommScope Inc. | price check: no row on 2007-12-31 |
| 383 | FDRY | Foundry Networks Inc. | price check: no series |
| 385 | NSR | NeuStar Inc. Class A | price check: no row on 2007-12-31 |
| 386 | POLY | Plantronics Inc. | price check: no row on 2007-12-31 |
| 388 | PWAV | Powerwave Technologies Inc. | price check: no series |
| 391 | COMS | 3Com Corp. | price check: no row on 2007-12-31 |
| 397 | OSGB | Overseas Shipholding Group Inc. | price check: no row on 2007-12-31 |
| 399 | YELL | YRC Worldwide Inc. | price check: no series |

### The control

The S&P 400 figure comes from another vendor, another download decade and
71.1% of its index by count, while both neighbours come from Chan's files. A
gap between the S&P 400 and either neighbour could come from any of those as
easily as from capitalisation. The control asks how far the same construction
moves a universe whose figure on Chan's file is known. It is the S&P 600,
built from IJR's 2007-12-31 schedule by the S&P 400 panel's rule and priced
from the `sp600` cross-section with the same open adjustment.

IJR's own members file, `research/filings/ijr/members.csv`, records only the
509 of IJR's 602 holdings that link into the 2008-12-31 schedule, so a control
read from it would hold only stocks still in the index a year later. The
control file holds all 602 instead, and its 509 shared rows are byte for byte
IJR's file's, which `tests/test_sp400_panel.py` holds. So the control carries
no survival filter the S&P 400 panel lacks.

The rule reads the control's gap against the S&P 400's distance to its nearer
neighbour, at each price. On the closes the nearer neighbour is the S&P 600,
1.3748 away, and the control's gap is 0.1108. On the opens it is the S&P 500,
0.9669 away, and the control's gap is −0.7244. Both are inside, so the
ordering is separable from how the panel was built and the declared reading
applies. The opens' margin is the narrower one.

### What the entry concludes

Four things, and the first is the finding.

1. **The reading is mixed.** On the closes the S&P 500, the S&P 400 and the
   S&P 600 rise in that order before costs, the way Chan's explanation says.
   On the opens the S&P 400 sits below the S&P 500, so the first step of the
   ladder breaks, while the second still rises. Under the words declared
   before the run, an order that holds at one price and is partial at the
   other is mixed.
2. **One year resolves one step of the four.** The closes' step from the
   S&P 500 to the S&P 400 is 2.1973 standard errors. The other three,
   including the opens' step that breaks the order, are within one year's
   noise. So the break on the opens is a reading of a gap one year cannot
   resolve, and so is the rise from the S&P 400 to the S&P 600 at both prices.
3. **Building the panel from the archive moves the S&P 600 by less than the
   S&P 400's nearer step.** With the declared exclusions the control lands
   within one year's noise of Chan's file at both prices, and inside both
   steps. Under the declared rule that makes the ordering separable from how
   the panel was built. The rule assumes the construction moves the S&P 400
   about as much as it moved the S&P 600, which this entry cannot measure.
   Without the three exclusions the control would land outside both steps,
   which is why those days were classified before the run rather than after
   it.
4. **After costs the closes keep the order and the opens keep the break.**
   After Chan's costs the S&P 400 earns −1.4444 on the closes, between the
   S&P 500's −3.1884 and the S&P 600's −0.3702. On the opens it keeps 0.4589,
   below both neighbours. Nothing was declared for an order after costs, and
   no standard error sizes these gaps, so this describes the figures rather
   than reading them. The run charges all three universes 5 basis points a
   side, so these figures flatter the smaller indexes.

### What this entry cannot say

Six things.

**Anything about microcaps.** Chan's sentence names "small and microcap
stocks". The S&P 400 holds mid caps and the S&P 600 small caps above an index
floor, and none of the four panels holds market values, so nothing here
speaks for microcaps or for stocks outside the three indexes.

**What survivorship after 2007 did.** The S&P 400 panel holds 285 of IJH's
401 holdings. Every one of the 116 it leaves out but EXH and BR is left out by
how the vendor serves its ticker today, and they include companies bought or
failed after 2007, such as Cephalon and IndyMac. Chan's two files are
survivors too, as of 2007-11-23 and 2008-01-14. A reversal buys the stocks
that fell, so the missing stocks could move it either way. Nothing here
measures the size or the sign of that on the S&P 400. The control's gap holds
the same selection's effect on the S&P 600 only, mixed with the change of
vendor and download decade.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) and
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213) are where
survivorship is priced.

**Whether the construction moves the S&P 400 as it moved the S&P 600.** The
control measures what another vendor, another download decade and the same
selection rule do to the S&P 600 in 2006. The S&P 400 panel keeps a larger
share of its index than the control does, 71.1% by count against 64.0%, and
nothing here measures how a mid-cap panel built this way differs from one
Chan's vendor would have given. The control measures the construction's
effect on one universe, and the reading assumes it is similar on the other.

**What a trader would keep after costs.** The run charges all three
universes 5 basis points a side, while smaller stocks cost more to trade. So
the after-cost figures flatter the S&P 400 against the S&P 500 and the
S&P 600 against both, and nothing here prices by how much.

**Whether the order holds in another year.** The run reads 2006 only, the
year of Chan's S&P 500 figures, and three of its four steps are within that
year's noise. An order that held across years would be a different and
stronger result.

**Whether Khandani and Lo's 4.47 came from small caps.** Their figure is for
2006 too, but it comes from their own universe, which is not these panels'. So
nothing here says where their returns came from. The report prints 4.47 and judges it against nothing.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/khandani-lo-small-caps-lessons.md](../blog/khandani-lo-small-caps-lessons.md)
moves with it, since the closing paragraphs of that post's Lesson 6 quote
the holdings it starts from, keeps and leaves out, the vendor's 2006-12-28
start, its before-cost figures, its one step beyond noise, the control's gaps
and the S&P 400's distances to its nearer neighbour.
So does the post's Lesson 6 sketch, which draws this run's S&P 400 figures
from `PINNED_MID` in
[tests/test_khandani_lo_small_caps_whiteboard.py](../tests/test_khandani_lo_small_caps_whiteboard.py).
`test_the_whiteboard_draws_this_runs_figures` in
[tests/test_khandani_lo_mid_caps.py](../tests/test_khandani_lo_mid_caps.py)
holds the two together, and a re-pin here redraws it with
`uv run python -m chan.khandani_lo_small_caps_whiteboard`.

## Entry 51: Example 2.5's linear rule on USD/CAD after 2012, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 2.5, Kindle location 1225. Shipped under
[issue 607](https://github.com/l3a0/quantitative-trading/issues/607). Entry 22
reproduces Example 2.5 on Chan's own 1,216 closes from 2007-07-23 to
2012-03-28, and every result there is exploratory for two reasons. The sample
was spent reproducing figures Chan chose, and the 115-day lookback is the
half-life of the same closes the rule trades, a look-ahead location 1225
names. This entry removes both. The lookback stays at 115, fixed from Chan's
closes and never re-estimated, and the rule trades only closes after
2012-03-28.

Ten rows. Nine are derivable from
[tests/test_usdcad_holdout.py](../tests/test_usdcad_holdout.py), whose pins
run everywhere because the vintage is committed, and row 2 records a
prediction that did not run.

**Reproduced.** Over 3,791 traded days, from 2012-03-29 to 2026-10-12, the
rule's daily P&L sums to 0.1132, above 0, so the claim that the P&L ends
positive survives out of sample on this feed. It survives narrowly. The mean
daily P&L is indistinguishable from zero, at a Newey-West t of 0.2670, and
the deepest drawdown, 0.5033, is more than four times what the run ends with.
H1 is a single-feed result, because the second holdout, H2, did not run.

One row is a claim and nine are not replications. Row 1 takes the claim
route `### Rows that are not replications` describes, since no published
number stands behind it. Row 2 is the prediction that moved to another issue.
Rows 3 to 7 are the predictions registered beside the claim, which decide
nothing, and rows 8 to 10 are the figures reported beside them.

Three things carry the result, so they are stated here.

1. **The closes.** Every row but row 2 reads one vintage,
   `alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv`, Alpha
   Vantage's `FX_DAILY` close for USD/CAD, downloaded 2026-10-13, 5,000 rows
   from 2007-08-10 to 2026-10-12. The vendor's daily close is a different
   feed from Chan's 16:59 bar, so this is the issue's holdout B, the long one
   on a different feed. The owner ruled on the issue that this one Alpha
   Vantage series is committed to `data/`, and
   [data/README.md](../data/README.md) says what it holds.
2. **The rule and its slices.** The rule is
   `chan.usdcad_mean_reversion.linear_mean_reversion` exactly. The position
   is minus the 115-day z-score of the close, each day's P&L is the previous
   day's position times the day's percent change, and there is no
   transaction cost and no rollover interest. It runs over the 115 closes
   before 2012-03-29, from 2011-10-20 to 2012-03-28, and every close after
   them together. The traded days are `pnl[115:]`, the positions that earn
   them are `market_value(...)[114:-1]`, and the tested closes `y` cover the
   traded days' span. The warm-up falls inside Chan's window, so no test
   reads it.
3. **The holdout the issue cut.** Holdout A is Chan's 16:59 specification on
   Massive's minute bars. The owner cut it, with its prediction H2, to
   [issue 608](https://github.com/l3a0/quantitative-trading/issues/608). It
   reads Massive's minute bars from 2024-10-13, and it waits until the whole
   minute file can be recorded, as row 2's verdict says. The issue had said
   that H1 and H2 disagreeing would make the result feed-dependent, and with
   H2 unrun that check is not made.

Rows 1 and 3 to 6 are **registered**. On 2026-10-13, before the run computed
anything on a holdout close,
[issue 607](https://github.com/l3a0/quantitative-trading/issues/607) wrote
down each prediction, its statistic, comparator and slice, the lookback, and
the mapping from H1 to a verdict, and the owner called the issue a
pre-registration that day. Four reads came before the run, and none decided
anything. The first three came before the issue was written, which its body
records, and the fourth after it.

1. `chan.aud_cad_johansen` already read about 20 of the holdout's first days,
   through 2012-04-26, from Chan's own `inputData_USDCAD_20120426.csv`, a
   different feed under a different rule.
2. The issue's coverage probe compared the vendor's closes with Chan's only
   on the days the two share up to 2012-03-28.
3. A probe of Massive's `C:USDCAD` minute bars read one day, 2026-10-12, to
   confirm the 16:59 bar exists, and computed no statistic.
4. The manifest, scale-break and column read-back tests read every committed
   close, so they read this vintage in the commit that landed it, and only
   their pass or fail was looked at.

Row 7 carried no prediction, so rows 7 to 10 are **exploratory** point
estimates that nothing tests. Row 2 did not run and carries neither label.

### What the book stated

The book prints no number for the claim, and nothing at all about USD/CAD
after March 2012, so the published-figure and gap columns have nothing to
hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | H1, Example 2.5's cumulative P&L is positive, on holdout B | "manages to be positive", with no figure | location 1225 |
| 2 | H2, the same claim on holdout A | the same claim | location 1225 |
| 3 to 7 | H3 to H7, the mean daily P&L, the ADF, the variance ratio, H and the half-life on the later closes | nothing about closes after March 2012. Entry 22 carries what the book prints on Chan's | n/a |
| 8 to 10 | the drawdown and Sharpe ratio, the positions, and the window | nothing, the book reports no such figure for this period | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | H1, registered: `pnl[115:].sum() > 0` | 0.1132, above 0, so H1 holds | `TestThePrimaryPrediction::test_h1_the_cumulative_pnl_is_above_0_so_the_claim_reproduces` |
| 2 | H2, registered: the same sum on holdout A's 16:59 closes | not run, moved to [#608](https://github.com/l3a0/quantitative-trading/issues/608) | none |
| 3 | H3, registered: the Newey-West t of the mean daily P&L above 1.645, predicted not to | 0.2670 at lag 8 over 3,791 days, so H3 does not hold, as registered | `TestTheSecondaryPrediction::test_h3_the_newey_west_t_does_not_clear_1_645_as_registered` |
| 4 | H4, registered: jplv7 `adf(y, 0, 1)` below `ztcrit`'s 10 percent value, predicted not to. `adfuller` at the same lag is reported beside it | −2.0814 against −2.5937, so H4 does not hold, as registered. `adfuller` gives −2.0243 | `TestTheDescriptivePredictions::test_h4_the_adf_does_not_reject_at_10_percent_as_registered` |
| 5 | H5, registered: `vratiotest(log(y))` rejects at 5 percent, predicted not to | p-value 0.4343, h = 0, so H5 does not hold, as registered | `TestTheDescriptivePredictions::test_h5_the_variance_ratio_does_not_reject_at_5_percent_as_registered` |
| 6 | H6, registered: `genhurst(log(y), 2)` within 2 SDs of its mean over 40,000 random walks of the same length from seed 20261011, predicted to | 0.4974 against 0.4987 ± 2 × 0.0130 on walks of 3,791, so H6 holds, as registered | `TestTheDescriptivePredictions::test_h6_genhurst_falls_inside_2_sds_of_the_random_walks_as_registered` |
| 7 | H7: `ou_half_life(y)`, beside the frozen 115, no prediction | 457.8077 days | `TestTheDescriptivePredictions::test_h7_the_half_life_is_457_8077_days_beside_the_frozen_115` |
| 8 | the deepest fall of the cumulative P&L below its running high, and the raw P&L's Sharpe ratio, √252 times the mean over the standard deviation | 0.5033, from 2013-11-20 to 2016-01-19. Sharpe ratio 0.0715 | `TestTheSideFigures::test_the_deepest_drawdown_and_its_dates` and `::test_the_sharpe_ratio_of_the_raw_pnl` |
| 9 | the positions that earn the traded days: the largest in absolute value, and the shares of traded days long and short | 5.4054. Long on 0.3994 and short on 0.6006, with no day flat | `TestTheSideFigures::test_the_largest_position_and_the_shares_long_and_short` |
| 10 | the window: the warm-up, the traded days, and the weekdays with no row over the traded days | 115 warm-up closes from 2011-10-20 to 2012-03-28. 3,791 traded days from 2012-03-29 to 2026-10-12. 2 of the 3,793 weekdays have no row, and no run of them is longer than 1, between 2014-12-26 and 2014-12-30 | `TestTheHoldoutWindow::test_115_warm_up_closes_from_2011_10_20_to_2012_03_28`, `::test_3791_traded_days_from_2012_03_29_to_2026_10_12`, `::test_2_of_3793_weekdays_have_no_row_and_no_run_is_longer_than_1` and `TestTheVintage::test_the_entry_names_the_fx_daily_closes_downloaded_2026_10_13` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | Registered. [Issue 607](https://github.com/l3a0/quantitative-trading/issues/607) wrote the criterion down before the run computed anything on a holdout close, and it holds: the P&L ends at 0.1132, above 0. The issue mapped H1 holding to this value before the run. It takes the claim route, and it is a single-feed result, because H2 did not run. |
| 2 | not run, moved to [#608](https://github.com/l3a0/quantitative-trading/issues/608) | Holdout A reads Massive's minute bars from 2024-10-13, the earliest the current plan reaches. It waits until the whole minute file can be recorded, and [issue 608](https://github.com/l3a0/quantitative-trading/issues/608) names what would allow that. A plan reaching back to 2012 would extend it. |
| 3 | none, not a replication | Registered, and it decides nothing. The prediction was that the t would not clear 1.645, and at 0.2670 it does not. |
| 4 | none, not a replication | Registered, and it decides nothing. The prediction was that the ADF would not reject, and −2.0814 sits above −2.5937. |
| 5 | none, not a replication | Registered, and it decides nothing. The prediction was that the variance ratio would not reject, and its p-value is 0.4343. |
| 6 | none, not a replication | Registered, and it decides nothing. The prediction was that H would fall inside the band, and 0.4974 sits 0.0014 below the walks' mean of 0.4987, against a band of ±0.0260. |
| 7 | none, not a replication | No prediction. The half-life on the later closes is 457.8077 days, almost four times the 115 the rule trades at. |
| 8 | none, not a replication | The drawdown ran from 2013-11-20 to 2016-01-19, and at 0.5033 it is more than four times the final P&L. The Sharpe ratio is on the raw P&L, which is in units of the position's own scale. |
| 9 | none, not a replication | The rule was short on 0.6006 of the traded days. Its largest position, 5.4054, is a close more than five moving standard deviations from its 115-day average. |
| 10 | none, not a replication | The window is the one the issue fixed. No gap threshold was set, because Chan's own closes skip 250 days. |

### What the entry concludes

Three things.

1. **Example 2.5's claim survives out of sample, on one feed.** At the
   lookback fixed from Chan's closes, the rule's P&L over 3,791 days after his
   sample ends at 0.1132, above 0. That is `reproduced`, registered, and the
   first registered result on USD/CAD in this repository. H2 did not run, so
   nothing here says whether the same holds on Chan's 16:59 bar.
2. **The claim survives on its sign alone.** The mean daily P&L has a
   Newey-West t of 0.2670, and the raw P&L's Sharpe ratio is 0.0715. A
   drawdown of 0.5033 from 2013-11-20 to 2016-01-19 is more than four times
   what the run ends with. So the sum is positive, and nothing here can tell
   the mean behind it from zero.
3. **The later closes read as a random walk, as registered.** The ADF of
   −2.0814 does not reject at 10 percent, the variance ratio's p-value is
   0.4343, and H of 0.4974 sits inside its random-walk band. The half-life
   on these closes is 457.8077 days, almost four times the lookback the rule
   trades at. Each of H3 to H6 landed as the issue predicted.

### What this entry cannot say

Four things.

**Whether the result depends on the feed.** The vendor's daily close is not
Chan's 16:59 bar, and the holdout that would have used his bar moved to
[issue 608](https://github.com/l3a0/quantitative-trading/issues/608).

**Whether the rule would pay.** There is no transaction cost and no rollover
interest, which the issue left to a later specification, and the position
grows without limit as the deviation does. The P&L is in units of the
position's own scale rather than a return on capital.

**Whether the mean is real.** The claim is about the sign of the sum, and a t
of 0.2670 cannot separate the mean daily P&L from zero.

**Anything about a lookback other than 115.** The issue froze it before the
run read the holdout, and a lookback chosen after seeing these numbers would
make a new run, and an exploratory one.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/usdcad-holdout-lessons.md](../blog/usdcad-holdout-lessons.md) moves with
it, since that post quotes most of these figures. So do its one figure,
which `uv run python -m chan.usdcad_holdout_figures` redraws, and its one
whiteboard sketch, which prints the final P&L, the Newey-West t and the 1.645
it falls short of, and which `uv run python -m chan.usdcad_holdout_whiteboard`
redraws.

## Entry 52: Example 7.7 against Open Source Asset Pricing's `MomSeasonShort`

Sources: Ernest P. Chan, *Quantitative Trading*, Kindle location 4425, for
the "more than 13 percent" a year before 2002. Steven Heston and Ronnie
Sadka, "Seasonality in the Cross-Section of Stock Returns", October 2006
working paper, Table 2, for 1.15 percent a month with a t of 7.6
over 1965 to 2002, as
[issue 661](https://github.com/l3a0/quantitative-trading/issues/661) records
it. The paper was published in the *Journal of Financial Economics* in 2008.
This repository holds no copy of either version. Shipped under
[issue 661](https://github.com/l3a0/quantitative-trading/issues/661).

Entry 7 reproduces Example 7.7 on Chan's S&P 500 file and tests it on IVV's
members after the book. Neither can see before 2002 on a panel that holds
the companies that later left, and Chan's file keeps 13 months before 2002
after the rule's twelve-month lookback, all on survivors. The Open Source Asset Pricing project, from Andrew Chen and
Tom Zimmermann, rebuilds Heston and Sadka's own signal from CRSP as
`MomSeasonShort` and publishes its portfolio returns from 1927.
[Issue 660](https://github.com/l3a0/quantitative-trading/issues/660)
committed them. This entry reads that series around 2002 and sets it beside
Entry 7's two runs.

This entry is not a replication. Its main series is the project's
construction, read as published, rather than a figure this repository
computes from a rule. The two published figures are set beside it, and row 1
states its distance from Heston and Sadka's, but no row chases either, so the
tables drop the gap and verdict columns, under
`### Rows that are not replications`. Every row is **exploratory**: the issue
was filed after a first look at these numbers, and neither side's
construction was chosen for this comparison.

Six rows, all derivable from
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py). Rows 1
to 4 run everywhere, because both vintages are committed. Row 5 reads the
owner's archive, as Entry 7's IVV rows do, and skips with the reader's
message where none is.

Four things carry the result.

1. **The project's series.** Release 202510, downloaded 2026-10-19,
   `openassetpricing-202510_momseasonshort-ls_return_1927-01-31_2024-12-31_dl2026-10-19.csv`,
   1,176 months from 1927-01 to 2024-12, read through
   `chan.open_asset_pricing.long_short_returns`. It is the return of the
   equal-weighted top tenth less the bottom tenth of NYSE and AMEX stocks,
   re-formed monthly, before costs, as [data/README.md](../data/README.md)
   records from the release's `SignalDoc.csv`. The signal they are sorted on
   is the return in the month a year before the month held, by the project's
   description of it, which
   [issue 661](https://github.com/l3a0/quantitative-trading/issues/661)'s
   table quotes. The file writes
   percent, and every figure here is a fraction.
2. **This repository's runs.** `REVISED_MATLAB` unchanged and before costs,
   on Chan's `SPX_20071123.mat` over the 83 months it keeps, and on IVV's
   members each month as Entry 7 names them. Months are matched by calendar
   month rather than by date, so a day that differs between two calendars
   cannot drop a month. On these runs the dates agree in every shared month.
3. **The windows.** Heston and Sadka's sample is 1965-01 to 2002-12. The
   split is the book's, at 2002-01-01, so 2002 falls in the after half, as it
   does in Entry 7's split. The before half starts at 1965-01, where their
   sample does, although the release reaches back to 1927.
4. **The scale.** `REVISED_MATLAB` divides a month's summed return by every
   position held, long and short together, so it earns half the top tenth's
   mean less the bottom's. The project's row is the whole of that difference.
   Each correlation and t is the same at either scale. A difference of means
   is not, so the halved difference sets the two at the rule's scale. Chan's
   13 percent is taken to be on the project's scale and is compared
   unhalved, but that is an inference. Location 4425 cites a 2007 seminar
   draft of Heston and Sadka's paper rather than the 2008 article, and does
   not say which scale it uses.

### What the sources stated

| # | Row | What the source says | Where |
| --- | --- | --- | --- |
| 1 | The signal over Heston and Sadka's sample | 1.15 percent a month, t 7.6, 1965 to 2002 | Heston and Sadka, Table 2, read by the post from their October 2006 working paper. This repository holds no copy of either version |
| 2 | The signal before 2002 | "more than 13 percent" a year, before transaction costs | Kindle location 4425 |
| 3 | The signal from 2002 | the effect "has disappeared since then", with no figure | Kindle location 4425 |
| 4 and 5 | Example 7.7 against the project, on Chan's file and on IVV's members | nothing | n/a |
| 6 | The rule's scale against the project's | nothing | n/a |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 1965-01 to 2002-12, 456 months | the project's series, mean and one-sided t | 0.0136 a month, t 8.63, 0.0021 above Heston and Sadka's 0.0115, about 1.3 standard errors | `TestTheOpenAssetPricingPins::test_heston_and_sadkas_sample` |
| 2 | 1965-01 to 2001-12, 444 months | the same, and twelve times the mean | 0.0131 a month, t 8.28, or 15.8% a year against Chan's more than 13% | `TestTheOpenAssetPricingPins::test_before_2002_it_earns_more_than_chans_13_percent` |
| 3 | 2002-01 to 2024-12, 276 months | the same, and its one-sided p | 0.0012 a month, t 0.50, p 0.307 | `TestTheOpenAssetPricingPins::test_from_2002_its_mean_is_not_detectably_above_zero` |
| 4 | 2000-12 to 2007-10, 83 months | `REVISED_MATLAB` on Chan's file against the project: each mean, standard deviation and t, the correlation, the difference of means, and the difference against half the project's mean | this repo −0.0011, 0.0302, t −0.33. The project 0.0018, 0.0356, t 0.46. Correlation 0.705. Difference −0.0029, or −0.0020 at the rule's scale | `TestTheOpenAssetPricingPins::test_on_chans_file` |
| 5 | 2009-01 to 2024-12, 192 months | the same on IVV's members each month | this repo −0.0004, 0.0200, t −0.27. The project 0.0012, 0.0425, t 0.39. Correlation 0.592. Difference −0.0016, or −0.0010 at the rule's scale | `TestTheOpenAssetPricingPins::test_on_ivvs_members`, which skips where no archive is |
| 6 | four synthetic months, 20 stocks | `REVISED_MATLAB`'s monthly return against the top tenth's mean less the bottom's | half of it in every month, to 12 significant digits | `TestMatchingTheProjectsMonths::test_the_rule_earns_half_the_top_tenth_less_the_bottom` |

### What each construction difference can explain

[Issue 661](https://github.com/l3a0/quantitative-trading/issues/661) asked which differences between the two sides the comparison can
attribute a gap to. Five differ, and one does not.

1. **The scale.** Row 6 holds it, so the halved differences in rows 4 and 5
   remove it by arithmetic. The halving is exact in a month where every held
   stock has a return. On Chan's file 2 held positions have none, which the
   rule still counts, and that moves one month by at most 0.0013. On IVV's
   members the scale also accounts for most of the difference in standard
   deviation. Half the project's 0.0425 is 0.0213, against the IVV run's
   0.0200. On Chan's file it does not: half the project's 0.0356 is 0.0178,
   against Chan's file's 0.0302.
2. **The universe.** The S&P 500's large companies against every NYSE and
   AMEX stock, small ones included and Nasdaq's left out. The comparison
   cannot separate this from the next two, because all three change together.
3. **Who is in it.** Chan's file holds the S&P 500 as it stood on
   2007-11-23, carried back. IVV's run holds the index as it stood each month.
   CRSP holds every company that traded, including those that later left.
4. **The returns.** Chan's vendor's closes and Alpha Vantage's adjusted
   closes against CRSP's monthly returns, whose treatment of a delisting is
   the project's.
5. **The tenth.** The rule takes the floor of a tenth of the ranked members.
   The project forms its own tenths, and this entry has not read where it
   sets their breakpoints. No test measures what the difference moves.
6. **The signal, which is the same on both sides by description.** Both rank
   on the return in the same calendar month a year before the month held.
   That rests on the project's description of its signal, as
   [issue 661](https://github.com/l3a0/quantitative-trading/issues/661)'s
   table quotes it. This repository holds neither the project's code nor its
   `SignalDoc.csv`, so nothing here checks it.

So the comparison can attribute a gap to the scale and to nothing else on its
own. What is left after halving belongs to the universe, the membership and
the returns together.

### What the entry concludes

Three things.

1. **On CRSP, the signal earned at least what both published figures say
   before 2002.** Over Heston and Sadka's sample the project's series averages
   0.0136 a month with a t of 8.63, against their 0.0115 and 7.6. The
   difference, 0.0021, is about 1.3 standard errors of the project's mean, so
   it does not separate the two. Before the book's split it averages 0.0131 a
   month, 15.8% a year, which is consistent with Chan's "more than 13
   percent". That is the release's construction and not Heston and Sadka's,
   so it says the effect shows up in a broad survivorship-free panel before
   2002, and not that their figure reproduces.
2. **From 2002 the same series averages 0.0012 a month, with a t of 0.50.**
   Over the 192 months it shares with the IVV run, it averages 0.0012 with a t
   of 0.39. So a broader panel than the S&P 500 also shows no mean
   detectably above zero after 2002, which is what Chan reports and what
   Entry 7's registered IVV run found.
3. **Example 7.7 and the project's series move together.** They correlate at
   0.705 on Chan's file and 0.592 on IVV's members. At the rule's scale,
   Example 7.7 earned 0.0020 a month less than the project's series on Chan's
   file and 0.0010 less on IVV's members.

The sketch "Before 2002, without survivors" in
[blog/equity-seasonals-lessons.md](../blog/equity-seasonals-lessons.md) draws
the first conclusion's 0.0136, its standard error and 0.0131, read from this
run. `PINNED_OSAP` in
[tests/test_equity_seasonals_whiteboard.py](../tests/test_equity_seasonals_whiteboard.py)
moves with a re-pin of any of them. "Before 2002 and after" draws the means
and standard errors of 1965 to 2001 and of 2002 to 2024, which `PINNED_BROAD`
there pins, and "Moving together" draws row 5's 192 months and their
correlation of 0.592, and "Two running sums" adds those months up, neither
halved.

### What this entry cannot say

Three things.

1. **Whether the effect existed or died.** Nothing here was registered, and
   the split date is the book's. The before-and-after contrast is what Chan
   describes, read on a second panel, and it confirms nothing.
2. **Whether Example 7.7 itself earned 13 percent before 2002.** The project's
   series is its own construction, not Chan's rule. [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196) still asks for
   the rule on a survivorship-free panel, and this entry answers part of its
   question without closing it.
3. **Which of the universe, the membership and the returns makes the halved
   differences.** They change together.
