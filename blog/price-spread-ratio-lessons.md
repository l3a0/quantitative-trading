# Trading gold against oil three ways, on Chan’s own file

*A pair that fails a cointegration test can still be traded on a spread refitted every 20 days. Reproducing Chan’s Example 3.1 shows what that spread is, what each signal holds, and which printed figure came from a different run.*

## Why trade a pair that does not cointegrate

A pair trade needs a signal that keeps coming back to where it started. [The post on testing a price spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-mean-reversion.md) shows how to check for one with a cointegration test, which asks whether some fixed mix of two prices is stationary. Ernest Chan’s second book, *Algorithmic Trading*, asks the next question. What if the test fails?

His Example 3.1 takes the gold ETF GLD and the oil ETF USO, which he says “are not, in fact, cointegrated”, and asks whether there is still enough short-term mean reversion to trade (Chan, 2013, location 1505). He builds the signal three ways and trades each with the same rule.

1. **The price spread**, USO minus h shares of GLD, with the hedge ratio h refitted every day by regression over the last 20 days. He reports an APR of “about 10.9 percent” and a Sharpe ratio of “about 0.59”. The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.
2. **The log price spread**, the same construction on the logarithms of the prices. He reports 9 percent and 0.5.
3. **The ratio**, USO divided by GLD, with equal dollars on each side. He reports “a negative APR”.

Chan published a script for each signal and the data file they read. Each script ends on a comment holding the six decimals its print statement shows. This repository keeps a copy of the file and ran a line-by-line transcription of each script on it.

The price spread and the log price spread match all four of their scripts’ figures to six decimals. The ratio’s script misses its own comment. The same script with GLD and USO swapped matches it exactly, which this repository found only after the miss.

**Every result here is exploratory.** Chan chose the rule, the pair and a lookback he calls “near-optimal” with “the benefit of hindsight” (Chan, 2013, location 1505), and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the trade pays today.

The six lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

The rule is the linear mean reversion of Chan’s Chapter 2, applied to each signal in turn.

1. **The hedge ratio.** Regress USO on GLD, with an intercept, over the 20 days ending today. The slope is h, the number of GLD shares that hedge one share of USO. The log price spread regresses the logarithms instead.
2. **The signal.** The price spread is USO − h·GLD. The log price spread is log USO − h·log GLD. The ratio is USO / GLD and needs no h.
3. **The units.** Hold minus the signal’s z-score in units of the portfolio. The z-score is how many 20-day standard deviations the signal sits from its 20-day average. So the rule buys the portfolio in proportion as the signal falls below its average, and sells it in proportion as the signal rises above.
4. **The return.** Each day’s profit on yesterday’s positions, divided by the gross dollars those positions held. No cost is charged.

Each script also throws away its first 20 days, where the first hedge ratio is still being fitted, so all three trade the same 1,480 days.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and converted here to one file per ETF. It holds 67 ETFs over 1,500 trading days, from 2006-04-26 to 2012-04-09, and the scripts read two of them. The traded days run from 2006-05-24. The file folds dividends in by subtracting them in dollars, and GLD pays none. This repository transcribed the scripts from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, which a second copy holds byte for byte.

## Lesson 1: two scripts land to six digits, and the book rounds one of them up

Here is each figure, computed, beside the script’s comment and the book.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{Price spread, APR} & 0.108335 & 0.108335 & \text{about 10.9 percent} \\
\text{Price spread, Sharpe ratio} & 0.589651 & 0.589651 & \text{about } 0.59 \\
\text{Log price spread, APR} & 0.088863 & 0.088863 & \text{9 percent} \\
\text{Log price spread, Sharpe ratio} & 0.504153 & 0.504153 & 0.5
\end{array}
```

All four match the scripts to the last digit printed. The first position is held into 2006-06-22, the day after the 20-day standard deviation first exists, and every run has it there.

One figure in the book does not follow from its own script. The price spread’s comment prints 0.108335, which is 10.8 percent at one decimal, and the book prints “about 10.9 percent”. The difference is small and the word “about” covers it. It still matters for anyone checking a book against its code: the script is the record of what ran, and a rounded figure in the prose is a second copy that can drift from it.

The figure below redraws what the scripts plot. The top panel is the hedge ratio Lesson 4 turns to. The second and third are the price spread and the ratio, which the book prints as Figures 3.1 and 3.2. The bottom panel is each run’s cumulative return. Nothing compares the redraw with the charts in the book, so it is a redraw of the scripts’ plots rather than a checked copy.

![Four line charts stacked on one shared date axis from May 2006 to April 2012. The top chart is the 20-day hedge ratio, in GLD shares per USO share, swinging between −0.948 and 2.168 with a zero line marked and the stretches below zero shaded red. Its heading says it is below zero on 334 of 1,480 days, when one unit holds both ETFs long. The second chart, Figure 3.1, is the price spread USO minus h times GLD, in dollars, crossing zero again and again. The third chart, Figure 3.2, is the ratio USO over GLD, which starts at 1.03, peaks at 1.30, falls steeply through late 2008 and ends at 0.24 without returning. The bottom chart is each run’s compounded cumulative return, unlevered and before costs. The price spread and the log price spread both rise unevenly, the price spread ending higher. The ratio as published falls through 2008 and ends well below zero, and a dashed line for the ratio with GLD and USO swapped runs just below it. The legend sets each run’s APR and Sharpe ratio: 0.108335 and 0.589651, 0.088863 and 0.504153, −0.134608 and −0.702522, and −0.141522 and −0.746663. The title calls the redraw exploratory, and the note names Chan’s file and says the 20-day lookback was chosen with hindsight.](../docs/figures/price_spread_signals.png)

*The hedge ratio, the price spread, the ratio and each run’s cumulative return, redrawn on Chan’s file over the 1,480 traded days. Red shading marks the days the hedge ratio is below zero.*

## Lesson 2: three signals, three portfolios

The three signals are not three readings of one portfolio. Each one holds a different portfolio, and the difference is in what one unit of it holds.

```math
\begin{array}{l|l|l}
\text{Signal} & \text{One unit holds} & \text{Which means} \\ \hline
\text{Price spread} & -h \text{ shares of GLD}, +1 \text{ share of USO} & \text{fixed shares} \\
\text{Log price spread} & -h \text{ dollars of GLD}, +1 \text{ dollar of USO} & \text{fixed dollars} \\
\text{Ratio} & -1 \text{ dollar of GLD}, +1 \text{ dollar of USO} & \text{equal dollars}
\end{array}
```

The price spread is the market value of a portfolio holding a fixed number of shares. Its value moves with the prices, and that value is the signal.

The log price spread is different. Chan shows that a stationary mix of log prices is the value of a portfolio holding a constant dollar amount in each asset, with cash making up the rest (Chan, 2013, location 1435). Keeping the dollar amounts constant means rebalancing every day as the prices move. Chan names the extra cost of that daily rebalancing, and the backtest charges nothing for it. The log price spread’s figures are lower even so, an APR of 0.088863 against 0.108335 and a Sharpe ratio of 0.504153 against 0.589651, before any trade is priced. Chan’s sentence that both are “actually lower” holds on his file.

The ratio holds the same portfolio as the log price spread would with h fixed at 1, equal dollars on each side, but it trades on USO/GLD itself rather than on its logarithm. Chan notes that a ratio is stationary only when the two hedge ratios are equal and opposite, which is “a special case” (Chan, 2013, location 1476). He also gives the argument for it: a ratio does not need a hedge ratio at all, and it stays the same when both prices double. Whether a ratio beats an adaptive hedge ratio, he says he knows no general answer. On GLD and USO the ratio loses money, and the third panel of the figure shows what it was trading against. USO’s price was 1.03 times GLD’s on the first traded day and 0.24 times it on the last, and after 2008 the ratio never rose above 0.44.

## Lesson 3: the ratio’s printed figures match the legs swapped

`Ratio.m` closes on the comment `APR=-0.141522 Sharpe=-0.746663`. The transcription, run on Chan’s file, gives −0.134608 and −0.702522. The same code matches the other two scripts to six digits, and the data is Chan’s own file, so an old download cannot explain the miss.

This repository tried three readings after the miss, in this order.

1. **Keeping the first 20 days.** It gives −0.140674 and −0.744310, closer to the comment and matching neither figure.
2. **Chan’s own Python port of the script**, which ships with its own copy of the two price series. That copy equals the committed closes exactly. The port gives −0.140674 and −0.749583, and matches neither figure either.
3. **The script with GLD and USO swapped.** The signal becomes GLD/USO, and a positive unit buys GLD. It gives −0.141522 and −0.746663, both figures to all six digits.

```math
\begin{array}{l|r|r}
\text{Run} & \text{APR} & \text{Sharpe ratio} \\ \hline
\texttt{Ratio.m}\text{'s comment} & -0.141522 & -0.746663 \\
\text{As published, USO/GLD} & -0.134608 & -0.702522 \\
\text{Legs swapped, GLD/USO} & -0.141522 & -0.746663
\end{array}
```

The book captions its Figure 3.2 “Ratio = USO/GLD” (Chan, 2013, location 1505), and the published script computes USO/GLD. So the evidence favours the comment coming from a run with the legs the other way round, perhaps an earlier draft of the script. The two matching figures come from one series of daily returns, so they are not two independent coincidences. Two different summaries of it still match to six digits, which a near miss would not do.

The swap is reported as a cause the evidence favours, not as a reproduction, because it was found by trying readings after the first one failed. A reading chosen after its number is seen proves less than one written down first, however well it matches. Chan’s point survives either way. The ratio loses 13.5 percent a year as published and 14.2 percent with the legs swapped.

## Lesson 4: no cointegration, and a spread that is mostly the fit’s intercept

The data agree with Chan that GLD and USO do not cointegrate. The Engle-Granger test regresses USO on GLD over all 1,500 days and asks whether the leftover is stationary. Its statistic is −1.5150, against a 10 percent critical value of −3.04. A statistic needs to be more negative than the critical value to reject the hypothesis of no cointegration, so the test does not come close to finding any. Even the whole-period hedge ratio is negative, at −0.2669. A test that fails to reject cannot prove there is no relationship, but it gives the rule no long-run equilibrium to lean on.

What the rule leans on instead is a regression refitted on the last 20 days. The top panel of the figure shows what that refitting does to the hedge.

1. **It swings widely.** The 20-day hedge ratio runs from −0.948 to 2.168.
2. **It changes sign.** It is below zero on 334 of the 1,480 traded days. On those days one unit of the “spread” is long USO and long GLD, so it is a bet on both ETFs at once rather than a hedge.

The spread is not the regression’s leftover either. Each 20-day regression fits USO = c + h·GLD + e, an intercept c as well as a slope h, and the scripts trade USO − h·GLD, which is c + e. The intercept moves with every window, and on Chan’s file it carries almost all of the spread.

1. **The intercept tracks the spread.** Their correlation is 0.9987.
2. **The leftover is small.** The spread’s standard deviation is 45.37 dollars and the leftover’s is 2.27, so the leftover holds a quarter of a percent of the spread’s variance.
3. **The leftover alone earns nothing.** Traded by the same rule, it gives an APR of −0.005130 and a Sharpe ratio of 0.082065.

So the spread in the second panel, which Chan says looks stationary (Chan, 2013, location 1505), is mostly the 20-day intercept moving. Whether trading it captures a real short-term reversion between gold and oil or a property of the fitting, the backtest cannot say. The 20-day lookback was also chosen knowing how the strategy turned out, and a lookback chosen that way flatters every figure it produces.

## Lesson 5: a return that cannot see its own scale

The rule holds minus the z-score in units, so doubling every z-score doubles every position. It also doubles each day’s profit and the gross dollars held, and the return is one divided by the other. The two doublings cancel.

```math
r_t = \frac{\sum_i P_{i,t-1}\,\Delta p_{i,t} / p_{i,t-1}}{\sum_i |P_{i,t-1}|}
```

Here Pᵢ,ₜ₋₁ is yesterday’s dollar position in ETF i and Δpᵢ,ₜ / pᵢ,ₜ₋₁ is its return today. Multiply every position by any positive constant and rₜ does not move.

That has a consequence for checking the code. Chan’s book ships two standard deviation helpers. The plain `movingStd` divides by n − 1, and `smartMovingStd`, which skips missing values, divides by n. Over 20 days that rescales every z-score by the same factor, so the two give the same daily returns here to within 10⁻¹², and the same figures. In the posts on [post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md) and [buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md), a standard deviation helper fed a fixed threshold, so its scale mattered and the choice of helper moved printed figures. Here nothing compares the z-score with a threshold, so these figures are no evidence about which helper is right. A matching figure only checks the parts of the code it can see.

The next example in the book, Example 3.2, trades the same spread with Bollinger bands. It enters when the z-score crosses a fixed threshold, so there the scale does not cancel, and the choice of helper can move its figures. [The post on Bollinger bands](https://github.com/l3a0/quantitative-trading/blob/main/blog/bollinger-band-lessons.md#lesson-3-a-fixed-threshold-makes-the-divisor-matter) found that dividing by n rather than n − 1 lifts Example 3.2’s APR from 0.178249 to 0.183306 and its Sharpe ratio from 0.964673 to 0.984872.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

That two scripts match to six digits says the code, the data and the scripts’ comments agree. It says nothing about whether the trade paid, for four reasons.

1. **No cost is charged.** Every script trades every day, because the units change with the z-score every day. Chan names an extra cost for the log price spread’s rebalancing himself (Chan, 2013, location 1505).
2. **The lookback was chosen in hindsight.** Chan calls 20 days “near-optimal” with “the benefit of hindsight”, so the figures are in-sample.
3. **The pair shows no cointegration.** The profit rests on a 20-day fit whose hedge changes sign and whose intercept is most of the spread, which Lesson 4 describes, rather than on a relationship known to persist.
4. **The rule was chosen on the same days it is tested on.** Reproducing Chan’s figures on his window tests his arithmetic, so the result is exploratory. A result that could confirm the edge would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Four questions are beyond it.

1. **Which run produced `Ratio.m`’s comment.** Swapping the legs matches both figures. Neither public copy holds another version of the script, so whether Chan edited it after running it, or ran an earlier one, cannot be recovered here.
2. **Whether the reversion is real.** The Engle-Granger test finds no cointegration over the whole file, and nothing here tests shorter windows or separates real reversion from what a 20-day fit produces.
3. **What costs would take.** Nothing here charges any or measures how much each signal trades.
4. **Whether 20 days was a fair choice.** The lookback was fitted to this sample, and nothing here tries it on data it was not chosen on.

## What this means for a trader

One habit for each lesson.

1. **Check the script before the prose.** Both match here except one rounding, and when they disagree the script is the record of what ran.
2. **Ask what one unit of the signal holds.** The three signals here hold three different portfolios, even when they share a chart.
3. **Treat a printed result as a record of one run.** A comment can outlive the code it came from, and a reading that matches after a miss is evidence, not a reproduction.
4. **Look at the fit, not only the spread.** A hedge ratio that changes sign is not hedging, and a spread that leaves out the fit’s intercept can be mostly that intercept.
5. **Know what a matching figure can see.** A return that cancels any scale on its positions cannot tell two scaling choices apart, however well it matches.
6. **Treat an exact reproduction as a check on arithmetic.** Whether trading gold against oil pays needs costs, a lookback fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 3.1 and Kindle locations 1435, 1476 and 1505.
2. `PriceSpread.m`, `LogPriceSpread.m` and `Ratio.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Engle, R. F., and Granger, C. W. J. (1987). Co-integration and error correction: representation, estimation, and testing. *Econometrica*, 55(2), 251–276.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_price_spread.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_price_spread_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-21-price-spread-log-price-spread-and-ratio-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
