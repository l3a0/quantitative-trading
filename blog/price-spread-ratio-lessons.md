# Trading gold against oil three ways, on Chan’s own file

*A pair that fails a cointegration test can still be traded on a spread refitted every day on the last 20 days. Reproducing Chan’s Example 3.1 shows what that spread is, what each signal holds, and which printed figures came from a different run.*

## Why trade a pair that does not cointegrate

A pair trade needs a signal that keeps coming back to where it started. [The post on testing a price spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-mean-reversion.md) shows how to check for one with a cointegration test, which asks whether some fixed mix of two prices is stationary, meaning it keeps returning to the same average rather than wandering off. Ernest Chan’s second book, *Algorithmic Trading*, asks the next question. What if the test fails?

His Example 3.1 takes the gold ETF GLD and the oil ETF USO, which he says “are not, in fact, cointegrated”, and asks whether there is still enough short-term mean reversion to trade (Chan, 2013, Kindle location 1505). He builds the signal three ways and trades each with the same rule. He scores each by its APR and its Sharpe ratio. The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.

1. **The price spread**, USO minus h shares of GLD, with the hedge ratio h refitted every day by regression over the last 20 days. He reports an APR of “about 10.9 percent” and a Sharpe ratio of “about 0.59”.
2. **The log price spread**, the same construction on the logarithms of the prices. He reports an APR of 9 percent and a Sharpe ratio of 0.5.
3. **The ratio**, USO divided by GLD, with equal dollars on each side. He reports “a negative APR”.

Chan published a script for each signal and the data file they read. Each script ends on a comment recording the APR and Sharpe ratio its print statement shows, to six decimals. This repository keeps the file’s contents and ran a Python transcription of each script on them.

For the price spread and the log price spread, the transcription reproduces both figures in each script’s comment, all four to six decimals. The ratio’s script, run on the same file, does not reproduce the figures in its own comment. The same script with GLD and USO swapped matches them exactly, which this repository found only after the miss.

**Every result here is exploratory.** Chan chose the rule, the pair and a 20-day lookback, which he calls “near-optimal” with “the benefit of hindsight” (Chan, 2013, location 1505). The lookback is the number of past days that every regression, average and standard deviation reads. The reproduction tests these choices on the same days Chan ran them on. It can say whether his numbers follow from his file and nothing about whether the trade pays today.

The six lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

The rule is the linear mean reversion of Chan’s Chapter 2, applied to each signal in turn.

1. **The hedge ratio.** Regress USO on GLD over the 20 days ending today, fitting a straight line with an intercept, so the line need not pass through zero. The slope is h, the number of GLD shares that hedge one share of USO. The log price spread regresses the logarithms instead.
2. **The signal.** The price spread is USO − h·GLD. The log price spread is log USO − h·log GLD. The ratio is USO / GLD and needs no h.
3. **The units.** The z-score is how many 20-day standard deviations the signal sits from its 20-day average. The rule holds a number of units of the signal’s portfolio equal to minus the z-score. One unit of the price spread holds one share of USO and −h shares of GLD, and Lesson 2 gives what a unit holds for the other two signals. So the further the signal falls below its average, the more units the rule holds long, and the further it rises above, the more it holds short.
4. **The return.** Each day’s profit on yesterday’s positions, divided by the gross dollars those positions held, meaning the long and short dollar amounts added together without their signs. No cost is charged.

Each script also throws away its first 20 days, the window the first hedge ratio is fitted on, so all three trade the same 1,480 days.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10. This repository converted it to one file per ETF. Chan’s file holds 67 ETFs over 1,500 trading days, from 2006-04-26 to 2012-04-09, and the scripts read two of them. The traded days run from 2006-05-24. The file adjusts for dividends by subtracting each one in dollars from every earlier close, and GLD pays none.

This repository transcribed the scripts from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`. A second public copy holds the same three scripts byte for byte.

## Lesson 1: two scripts land to six decimals, and one of the book’s figures does not follow from its script

Here is each figure, computed, beside the script’s comment and the book.

```math
\small\begin{array}{l|r|r}
 & \text{APR} & \text{Sharpe ratio} \\ \hline
\textbf{Price spread} & & \\
\text{Computed} & 0.108335 & 0.589651 \\
\text{Comment} & 0.108335 & 0.589651 \\
\text{Book} & \text{about } 10.9\% & \text{about } 0.59 \\ \hline
\textbf{Log price spread} & & \\
\text{Computed} & 0.088863 & 0.504153 \\
\text{Comment} & 0.088863 & 0.504153 \\
\text{Book} & 9\% & 0.5
\end{array}
```

All four match the scripts to the last digit printed. Each of the three scripts, and the ratio with GLD and USO swapped, sets its first position on 2006-06-21, the first day the 20-day standard deviation of the signal exists, and earns its first return on 2006-06-22. The standard deviation needs 20 days of the signal, so that first return comes 20 trading days after the traded days begin.

One figure in the book does not follow from its own script. The price spread’s comment prints 0.108335, which is 10.8 percent at one decimal, and the book prints “about 10.9 percent”. The difference is small and the word “about” covers it. It still matters for anyone checking a book against its code: the script is the record of what ran, and a figure repeated in the prose is a second copy that can drift from it.

### The figure

The figure below redraws most of what the scripts plot. Its top panel adds the hedge ratio Lesson 4 turns to, which no script plots. Below it are the price spread and the ratio, which the book prints as Figures 3.1 and 3.2. The bottom panel is each run’s cumulative return, the line each script plots last. No check compares the figure with the charts in the book, so it shows what the scripts compute rather than a checked copy of Chan’s charts.

![Four line charts stacked on one shared date axis from May 2006 to April 2012. The top chart is the 20-day hedge ratio, in GLD shares per USO share, swinging between −0.948 and 2.168 with a zero line marked and the stretches below zero shaded red. Its heading says it is below zero on 334 of 1,480 days, when one unit holds both ETFs long. The second chart, Figure 3.1, is the price spread USO minus h times GLD, in dollars, crossing zero again and again. The third chart, Figure 3.2, is the ratio USO over GLD, which starts at 1.03, peaks at 1.30, falls steeply through late 2008 and ends at 0.24 without returning. The bottom chart is each run’s compounded cumulative return, unlevered and before costs. The price spread and the log price spread both rise unevenly, the price spread ending higher. The ratio as published falls through 2008 and ends well below zero, and a dashed line for the ratio with GLD and USO swapped runs just below it. The legend sets each run’s APR and Sharpe ratio: 0.108335 and 0.589651, 0.088863 and 0.504153, −0.134608 and −0.702522, and −0.141522 and −0.746663. The title calls the redraw exploratory, and the note names Chan’s file and says the 20-day lookback was chosen with hindsight.](../docs/figures/price_spread_signals.png)

*The hedge ratio, the price spread, the ratio and each run’s cumulative return, redrawn on Chan’s file over the 1,480 traded days. Red shading marks the days the hedge ratio is below zero.*

## Lesson 2: three signals, three portfolios

The three signals are not three readings of one portfolio. Each one holds a different portfolio, and the table gives what one unit of each holds.

```math
\begin{array}{l|r|r}
\text{Signal} & \text{GLD} & \text{USO} \\ \hline
\text{Price spread} & -h \text{ shares} & +1 \text{ share} \\
\text{Log price spread} & -h \text{ dollars} & +1 \text{ dollar} \\
\text{Ratio} & -1 \text{ dollar} & +1 \text{ dollar}
\end{array}
```

The price spread is the market value of a portfolio holding a fixed number of shares, one of USO and −h of GLD, for a given h. Its value moves with the prices, and that value is the signal.

The log price spread is different. Chan shows that a stationary mix of log prices is the value of a portfolio holding a constant dollar amount in each asset, with cash making up the rest (Chan, 2013, location 1435). Keeping the dollar amounts constant means rebalancing every day as the prices move. Chan names the extra cost of that daily rebalancing, and the backtest charges nothing for it. The log price spread’s figures are lower even so, an APR of 0.088863 against 0.108335 and a Sharpe ratio of 0.504153 against 0.589651, before any trade is priced. Chan’s sentence that the log price spread’s APR and Sharpe ratio are both “actually lower” holds on his file.

The ratio holds the same portfolio as the log price spread would with h fixed at 1, long a dollar of USO and short a dollar of GLD. It trades on USO/GLD itself rather than on its logarithm.

Chan notes that when a stationary mix weights the two prices equally and with opposite signs, the ratio or its logarithm is stationary. That holds exactly only for a mix of log prices, because with those weights the mix is a fixed multiple of the ratio’s logarithm. Chan calls equal and opposite weights “a special case”, so a ratio need not be stationary (Chan, 2013, location 1476).

He also argues for using a ratio. It stays the same when both prices are multiplied by the same factor, a point he credits to a reader, and it needs no hedge ratio at all. He says he knows no general answer to whether a ratio beats a price spread or log price spread whose hedge ratio adapts as the prices move, as the 20-day refit here does.

On GLD and USO the ratio loses money, and the third panel of the figure shows the fall the rule kept betting against. USO’s price was 1.03 times GLD’s on the first traded day and 0.24 times it on the last, and the ratio’s highest after 2008 was 0.44.

## Lesson 3: the ratio’s printed figures match a run with GLD and USO swapped

`Ratio.m`, the ratio’s MATLAB script, closes on the comment `APR=-0.141522 Sharpe=-0.746663`. The transcription, run on Chan’s file, gives −0.134608 and −0.702522. The same code matches the other two scripts to six decimals, and the data is Chan’s own file rather than a later download whose prices a vendor may since have revised, so a difference in the data cannot explain the miss.

This repository tried three other versions of the run after the miss, in this order.

1. **Keeping the first 20 days.** It gives −0.140674 and −0.744310, closer to the comment and matching neither figure.
2. **Chan’s own Python port of the script**, which ships with a copy of the two price series. That copy equals the closing prices in Chan’s MATLAB file exactly. The port gives −0.140674 and −0.749583, and matches neither figure.
3. **The script with GLD and USO swapped.** The signal becomes GLD/USO, and one unit is long a dollar of GLD and short a dollar of USO. It gives −0.141522 and −0.746663, both figures to all six decimals.

```math
\small\begin{array}{l|r|r}
\text{Run} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{Comment} & -0.141522 & -0.746663 \\
\text{Published, USO/GLD} & -0.134608 & -0.702522 \\
\text{Swapped, GLD/USO} & -0.141522 & -0.746663
\end{array}
```

The book captions its Figure 3.2 “Ratio = USO/GLD” (Chan, 2013, location 1505), and the published script computes USO/GLD. So the evidence favours the comment coming from a run with GLD and USO the other way round, perhaps an earlier draft of the script. The APR and the Sharpe ratio are both computed from one series of daily returns, so their two matches are not independent coincidences. Still, a run that only came close to the one behind the comment would not match both of those summaries to six decimals.

This post reports the swap as a cause the evidence favours, not as a reproduction, because this repository found it by trying versions after the first one failed. A version chosen after its number is seen proves less than one written down first, however well it matches. Chan’s conclusion that the ratio loses money survives either way. The ratio loses 13.5 percent a year as published and 14.2 percent with GLD and USO swapped.

## Lesson 4: no cointegration, and a spread that is mostly the fit’s intercept

The Engle-Granger test agrees with Chan and finds no cointegration between GLD and USO. It regresses USO on GLD over all 1,500 days and asks whether the leftover, the part of USO the fitted line does not explain, is stationary. Its statistic is −1.5150. The critical value, at the 10 percent significance level, is −3.04. To reject the hypothesis of no cointegration, the statistic must be more negative than the critical value, so the test does not come close to finding any. A test that fails to reject cannot prove there is no relationship, but it gives the rule no fixed mix of the two prices known to keep returning to its average. Even the whole-period hedge ratio is negative, at −0.2669.

### A hedge ratio that changes sign

With no cointegration found, the rule rests on a regression refitted on the last 20 days. The top panel of Lesson 1’s figure shows what that refitting does to the hedge.

1. **It swings widely.** The 20-day hedge ratio runs from −0.948 to 2.168.
2. **It changes sign.** It is below zero on 334 of the 1,480 traded days. On those days one unit of the “spread” is long USO and long GLD, so it is a bet on both ETFs at once rather than a hedge.

### An intercept that carries the spread

The spread is not the regression’s leftover. Each 20-day regression fits USO = c + h·GLD + e, where c is the intercept, h is the slope and e is the leftover. The scripts trade USO − h·GLD, which is c + e. The intercept moves with every window, and on Chan’s file it carries almost all of the spread.

1. **The intercept tracks the spread.** Their correlation is 0.9987.
2. **The leftover is small.** The spread’s standard deviation is 45.37 dollars and the leftover’s is 2.27, about a twentieth of it. Variance is the square of the standard deviation, so the leftover holds a quarter of a percent of the spread’s variance.
3. **The leftover alone earns close to nothing.** Traded by the same rule, it gives an APR of −0.005130 and a Sharpe ratio of 0.082065. Both are near zero. Their signs differ because the APR compounds the daily returns while the Sharpe ratio averages them.

![An animated whiteboard sketch titled “Why c carries the spread”, drawn slowly stroke by stroke. On the left, a grey vertical axis is labelled “USO”, and a second label, “GLD = 0”, says the axis stands where GLD is zero. A grey horizontal axis is labelled “GLD”. A small grey box sits near the right end of the GLD axis, around GLD of 91.5 dollars, and two grey lines run from it to a larger grey frame on the right that shows what is inside the box, magnified. Inside the frame’s top right, a grey label reads “12× taller”. In the frame, a grey cloud of 20 points appears with its fitted line, labelled “7 July, h 0.97”. On the left, the same line, grey and dashed, runs from the box back to the USO axis, where a brown dot is labelled “c −51.65”. A black cloud then appears in the frame, the second window, which shares fifteen days with the first. Fifteen of its points are the grey cloud’s own and turn black, and its five newest sit below the rest. The grey cloud’s five oldest stay grey, mostly at the top and right. The black cloud’s line is steeper and is labelled “14 July, h 2.17”. On the left, its dashed black line lands much lower on the USO axis, at a brown dot labelled “c −161.60”. A brown bracket joins the two dots, labelled “c fell 109.95”. A grey span along the GLD axis, from GLD = 0 to the clouds, is labelled “91.5 dollars”. Under “c fell 109.95”, a brown label reads “≈ 1.20 × 91.5”, and under that another reads “h rose 1.20”. In the frame, a black ring circles the last black point, and a short black tick runs from the black line down to it, labelled “e −3.21, a week before −2.71”. Below a grey rule under the frame, the sketch closes on three lines: “over all 1,480 traded days”, “correlation of c and the spread 0.9987” and “SD of the spread 45.37 dollars, of e 2.27”. Each axis on the left is drawn to its own linear scale, and neither is broken. The frame magnifies the points to a scale of its own. The finished sketch holds for twelve seconds before it redraws.](../docs/figures/price_spread_intercept_lever.gif)

*Two real 20-day windows from Chan’s file, ending 7 and 14 July 2009, the second on the day the spread is lowest in the whole run. Between them the slope h rose by 1.20, from 0.97 to 2.17. Both clouds sit about 91.5 dollars to the right of GLD = 0, where c is read. Steepening the line by 1.20 while it still runs through the clouds moved c down by about 1.20 × 91.5 dollars. Over the same week the leftover e on each window’s last day moved only from −2.71 to −3.21, so c makes up nearly all of the spread’s fall. Every figure comes from the run, and the three lines under the frame are figures over all 1,480 traded days, not over these two windows. The frame on the right draws each dollar of USO about 12 times taller than the left side does.*

So the spread in the second panel of Lesson 1’s figure, which Chan says looks stationary (Chan, 2013, location 1505), is mostly the 20-day intercept moving. The backtest cannot say whether trading it captures a real short-term reversion between gold and oil or only a pattern that refitting a line every day on the last 20 days creates by itself.

## Lesson 5: a return that cannot see its own scale

This rule’s return does not depend on the scale of the z-score. The rule holds a number of units equal to minus the z-score, so doubling every z-score doubles every position. It also doubles each day’s profit and the gross dollars held, and the return is one divided by the other. The two doublings cancel.

```math
r_t = \frac{\sum_i P_{i,t-1}\,\Delta p_{i,t} / p_{i,t-1}}{\sum_i |P_{i,t-1}|}
```

Here capital P is a dollar position and lower-case p is a price. Δp is the change in price from yesterday to today. The subscript i names the ETF and t names the day. The top line adds up, over the two ETFs, yesterday’s dollar position times today’s return on that ETF, which is the day’s profit. The bottom line adds up the sizes of yesterday’s positions, long and short alike, which are the gross dollars that step 4 of the rule divides by. Multiply every position by any positive constant and rₜ does not move.

That has a consequence for checking the code. Chan’s book code computes a standard deviation over the last n days with two different functions.

1. The plain `movingStd` divides by n − 1.
2. `smartMovingStd`, which skips missing values, divides by n.

Over 20 days, dividing by n rather than n − 1 rescales every z-score by the same factor, so the two functions give the same daily returns here to within 10⁻¹², and the same figures. Nothing in this rule compares the z-score with a threshold, so these figures cannot tell a transcription that calls `movingStd` from one that calls `smartMovingStd`.

The posts on [post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md) and [buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md) were different. In those posts a stock’s move was compared with a fixed multiple of its standard deviation, so the deviation’s scale mattered. The choice was between two versions of a function named `smartstd`, and it moved printed figures. One version ships with the first edition of Chan’s first book, *Quantitative Trading*, and the other with *Algorithmic Trading*.

The next example in the book, Example 3.2, trades the same spread with Bollinger bands. It enters when the z-score crosses a fixed threshold, so there the scale does not cancel, and the choice between `movingStd` and `smartMovingStd` can move its figures. [The post on Bollinger bands](https://github.com/l3a0/quantitative-trading/blob/main/blog/bollinger-band-lessons.md#lesson-3-a-fixed-threshold-makes-the-divisor-matter) found that dividing by n rather than n − 1 lifts Example 3.2’s APR from Chan’s 0.178249 to 0.183306 and its Sharpe ratio from his 0.964673 to 0.984872.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

Two scripts that match to six decimals show that the code, the data and the scripts’ comments agree. That match says nothing about whether the trade paid, for four reasons.

1. **No cost is charged.** Every script trades every day, because the units change with the z-score each day. Chan himself names an extra cost for the log price spread’s rebalancing (Chan, 2013, location 1505).
2. **The lookback was chosen in hindsight.** Chan calls 20 days “near-optimal” with “the benefit of hindsight”, so the figures are in-sample, measured on the same data Chan chose the lookback on. A lookback chosen that way tends to flatter the figures it produces.
3. **The pair shows no cointegration.** As Lesson 4 describes, the profit rests on a 20-day fit whose hedge changes sign and whose intercept is most of the spread, rather than on a relationship known to persist.
4. **The rule was chosen on the same days it is tested on.** A result that could confirm the edge would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Four questions are beyond it.

1. **Which run produced `Ratio.m`’s comment.** Swapping GLD and USO matches both figures. Neither public copy holds another version of the script, so whether Chan edited the script after running it, or ran an earlier version, cannot be recovered here.
2. **Whether the reversion is real.** The Engle-Granger test finds no cointegration over the whole file, and nothing here tests for it over shorter stretches of the file or separates real reversion from a pattern the daily 20-day refit creates by itself.
3. **How much costs would take from the returns.** Nothing here charges any or measures how much each signal trades.
4. **Whether 20 days was a fair choice.** The lookback was fitted to this sample, and nothing here tries it on data it was not chosen on.

## What this means for a trader

One habit for each lesson.

1. **Check the script before the prose.** The book’s prose matches the scripts here except for one figure, 10.9 percent where its script gives 10.8, and when they disagree the script is the record of what ran.
2. **Ask what one unit of the signal holds.** The three signals here hold three different portfolios, even when they share a chart.
3. **Treat a printed result as a record of one run.** A comment can outlive the code it came from, and a version that matches after a miss is evidence, not a reproduction.
4. **Look at the fit, not only the spread.** A hedge ratio that changes sign is not hedging, and a spread that never subtracts the fit’s intercept can be mostly that intercept.
5. **Know what a matching figure can see.** A return that cancels any scale on its positions cannot tell apart two choices that differ only by that scale, such as a standard deviation that divides by n and one that divides by n − 1.
6. **Treat an exact reproduction as a check on arithmetic.** Whether trading gold against oil pays needs costs, a lookback fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 3.1 and Kindle locations 1435, 1476 and 1505.
2. `PriceSpread.m`, `LogPriceSpread.m` and `Ratio.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Engle, R. F., and Granger, C. W. J. (1987). Co-integration and error correction: representation, estimation, and testing. *Econometrica*, 55(2), 251–276.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread_figures.py) and [the whiteboard sketch](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread_whiteboard.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_price_spread.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_price_spread_figures.py) and [what the sketch draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_price_spread_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-21-price-spread-log-price-spread-and-ratio-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
