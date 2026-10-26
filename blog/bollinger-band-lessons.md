# Chan’s Bollinger band on gold and oil reproduces to six digits, and its threshold makes the divisor matter

*Example 3.2 trades the same gold and oil spread as Example 3.1, but holds at most one unit and enters only beyond a fixed threshold. On Chan’s own file both of its printed figures land, and the fixed threshold is what lets the divisor of a standard deviation move them.*

## Why trade the same spread with a band

The [post on Example 3.1](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) traded the gold ETF GLD against the oil ETF USO on a price spread, USO − h·GLD. The hedge ratio h is refitted every day by a regression over the last 20 days. The spread is the price of one unit of a portfolio that holds one share of USO and −h shares of GLD. The z-score is how many 20-day standard deviations the spread sits from its 20-day average.

That post’s rule, called the linear rule here, holds a number of units equal to minus the spread’s z-score. So it buys more as the spread falls further below its average and sells more as the spread rises further above it. From the first day its z-score exists, it is in the market every day, and its size changes every day.

Ernest Chan’s second book, *Algorithmic Trading*, offers a rule for practical trading on the same signal, the Bollinger band (Chan, 2013, Kindle location 1548). The rule is named for a band drawn a set number of standard deviations either side of the spread’s moving average, and this post calls the rule itself the band. It opens a position only when the spread moves outside the band, and it closes the position when the spread comes back to its average. At any time it holds “either zero or one unit (long or short) invested”, which Chan says makes it “very easy to allocate capital to this strategy or to manage its risk”.

His Example 3.2 trades the GLD and USO spread with that band and reports an APR of 17.8 percent and a Sharpe ratio of 0.96, “quite an improvement from the linear mean reversal strategy” (Chan, 2013, location 1559). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.

### What the reproduction found

Chan published the script, `bollinger.m`, and the data file it reads. This repository keeps the file’s contents, as one CSV per ETF, and ran a Python transcription of the script on them. Both figures the script prints match to six decimals, an APR of 0.178249 and a Sharpe ratio of 0.964673.

**Every result here is exploratory.** Chan chose the pair, the thresholds and the 20-day lookback, which he calls “near-optimal” with “the benefit of hindsight” (Chan, 2013, location 1505), and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the trade pays today.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

The band keeps everything from Example 3.1 except how many units it holds.

1. **The spread and its z-score.** These are Example 3.1’s, unchanged.
2. **The entries.** Buy one unit when the z-score falls below −1. Sell one unit short when it rises above 1.
3. **The exits.** Close a long when the z-score rises above 0, which is where the spread crosses back through its average. Close a short when the z-score falls below 0.
4. **The days between.** A day with no entry and no exit carries yesterday’s units forward. Chan’s script does this with a helper called `fillMissingData`. So the units are only ever −1, 0 or 1.
5. **The return.** Each day’s profit on yesterday’s positions, divided by the gross dollars those positions held, as in Example 3.1. No cost is charged.

Each comparison is strict, so a z-score of exactly −1 enters nothing and one of exactly 0 exits nothing. No day on Chan’s file has a z-score of exactly −1, 0 or 1, so the band’s APR and Sharpe ratio cannot tell a strict comparison from an inclusive one.

At these thresholds a unit can also turn to the other side in a single day. While a long is held, a z-score that jumps from below 0 to above 1 clears the long’s exit at 0 and the short’s entry at 1 on the same close. A held short turns long the same way, when the z-score jumps from above 0 to below −1.

![An animated whiteboard sketch titled “Sixteen days of the band”, drawn slowly stroke by stroke and held for twelve seconds when finished. It is drawn to one scale from the run, one dot for each traded day. A red dashed line labelled “+1”, a grey line labelled “0” and a red dashed line labelled “−1” cross the board. Sixteen black dots for the z-score appear, with the dates “2006-07-27 to 2006-08-17” at the top right. The first dot sits just below 0. The next nine sit near −1, seven of them below it and two just above it. The eleventh rises to just below 0, and the twelfth jumps above +1. The one after stays just above +1, then the dots fall to just above 0, to between 0 and −1, and far below −1. Under the dots, a strip labelled “units held” starts as a thin grey line marked “flat” and turns into a thick green bar marked “long” at the second dot. “enters below −1” appears ending just past that dot, then “back inside the band, still long” under the two dots just above −1. A brown ring circles the twelfth dot, the first above +1, and “one close: exit at 0 and short above 1” appears beside it. There the green bar ends and a thick red bar marked “short” runs for three days, then a thin grey line marked “flat” for one day and a green bar marked “long” on the last day.](../docs/figures/bollinger_sketch_one_close.gif)

*Drawn to one scale from the run on Chan’s file. Each dot is one day’s z-score, and the strip under it is the units held at that day’s close.*

### The prices, the days traded and the script

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), the same one Example 3.1 reads. It is Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10, which this repository converted to one file per ETF. It holds 67 ETFs over 1,500 trading days, from 2006-04-26 to 2012-04-09, and the script reads two of them.

Like Example 3.1, the script throws away its first 20 days, the window the first hedge ratio is fitted on, so it trades the 1,480 days from 2006-05-24. The 20-day standard deviation first exists on 2006-06-21, the band enters its first position that day, and the position earns its first return on 2006-06-22, the same day as Example 3.1’s.

This repository transcribed the script from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`. A second public copy holds the same `bollinger.m` and `fillMissingData.m`, byte for byte.

## Lesson 1: both figures land to six digits, and the book rounds them correctly

Each of Chan’s scripts closes on a comment that holds the six decimals it prints. Here is each rule’s pair of figures, computed, beside that comment and the book, the band first.

```math
\small\begin{array}{l|r|r}
\text{The band} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{Computed} & 0.178249 & 0.964673 \\
\text{Script's comment} & 0.178249 & 0.964673 \\
\text{Book} & 17.8\% & 0.96
\end{array}
```

```math
\small\begin{array}{l|r|r}
\text{The linear rule} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{Computed} & 0.108335 & 0.589651 \\
\text{Script's comment} & 0.108335 & 0.589651 \\
\text{Book} & \text{about }10.9\% & \text{about }0.59
\end{array}
```

All four match their scripts to the last digit printed. The band’s book figures are its script’s figures rounded, 0.178249 to 17.8 percent and 0.964673 to 0.96. That was not true of the linear rule’s APR in Example 3.1. Its script prints 0.108335, which is 10.8 percent at one decimal, and the book prints “about 10.9 percent” (Chan, 2013, location 1505). So for Example 3.2 the computation, the script and the book agree at every digit each one prints.

### The z-score, the units and the return, redrawn

The figure below redraws the band. The top panel is the z-score it trades on, with its entry lines at −1 and 1 and its exit line at 0. The middle panel is the units it holds. The bottom panel sets its cumulative return beside the linear rule’s. The book prints the band’s alone, as Figure 3.3. Only the bottom panel’s solid green line is a line `bollinger.m` plots, and this repository adds the rest. Nothing compares the figure with the chart in the book, so it shows what the script computes rather than a checked copy of Chan’s Figure 3.3.

![Three charts stacked on one shared date axis from May 2006 to April 2012. The top chart is the 20-day z-score of the price spread USO minus h times GLD. It swings back and forth across dashed red lines at −1 and 1 and a solid line at 0, reaching beyond both dashed lines many times a year. The middle chart is the units held, a step line that moves between short −1, flat 0 and long 1. Its heading says the band is short on 547 days, flat on 334 and long on 599, and that its units change on 162 days where the linear rule’s change on 1,460. The bottom chart is the compounded cumulative return of three runs, unlevered and before costs. The band, a solid green line, rises unevenly and ends well above the linear rule, a solid brown line. A dashed green line for the band with the moving standard deviation divided by n runs close to the solid green line throughout. The legend sets each run’s APR and Sharpe ratio: 0.178249 and 0.964673 for the band, 0.108335 and 0.589651 for the linear rule, and 0.183306 and 0.984872 for the band with the deviation divided by n, which the legend calls a diagnostic. The title calls the redraw exploratory, and the note names Chan’s file and says the 20-day lookback was chosen with hindsight.](../docs/figures/bollinger_band.png)

*The z-score the band trades on, the units it holds, and its cumulative return beside the linear rule’s, redrawn on Chan’s file over the 1,480 traded days. The dashed line divides the moving standard deviation by n rather than n − 1, which Lesson 3 explains.*

## Lesson 2: the same spread, a different rule, better figures

Chan calls the band “quite an improvement” on the linear rule, so the reproduction checks the two measures he names. The APR rises from 0.108335 to 0.178249, by 0.069915. The Sharpe ratio rises from 0.589651 to 0.964673, by 0.375022. Both rules trade one spread, built by the same code, with one 20-day lookback. So the difference between them is the rule alone.

The reproduction’s test of Chan’s claim was written after the first transcription had run, and it asks only that both figures be higher, by any amount. A test chosen after its numbers are seen proves less than one written down first, so this one shows only that his sentence holds on his file.

A third measure, the drawdown, points the same way as the APR and the Sharpe ratio, though the book prints it for neither rule. A drawdown is a fall from the highest value reached so far. On the compounded cumulative return, the comparison runs as follows.

1. **The band.** Its deepest drawdown is −21.83 percent, with its trough on 2009-05-21. Its longest spell below a high lasts 252 trading days, from 2008-12-08 to 2009-12-07.
2. **The linear rule.** Its deepest drawdown is −34.24 percent, with its trough on 2009-01-06. Its longest spell below a high lasts 640 trading days, from 2008-12-08 to 2011-06-22.

Both spells start the day after the same high, on 2008-12-05. The band falls less far and regains its high in less than half the time.

## Lesson 3: a fixed threshold makes the divisor matter

Lesson 5 of [the Example 3.1 post](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) pointed ahead to this example. Among the helper functions Chan’s code ships for a standard deviation, two compute it over the last n days. A standard deviation over n days adds up each day’s squared distance from the average, divides that sum by a number called the divisor, and takes the square root. The plain `movingStd` uses a divisor of n − 1, and `smartMovingStd`, which skips missing values, uses n. Over 20 days, the standard deviation with divisor n equals the one with divisor n − 1 multiplied by √(19/20). A z-score divides by the standard deviation, so every z-score built with divisor n is the one built with n − 1 multiplied by √(20/19). It is larger in size whatever its sign.

```math
z^{(n)}_t = \sqrt{\tfrac{20}{19}}\; z^{(n-1)}_t \approx 1.0260\, z^{(n-1)}_t
```

Here z⁽ⁿ⁻¹⁾ₜ is day t’s z-score with the n − 1 divisor and z⁽ⁿ⁾ₜ is the same day’s with n. The linear rule holds minus the z-score in units, so the factor scales every position. Its return is profit over gross dollars, and the factor multiplies both, so it cancels. That is why the two helpers gave Example 3.1 the same figures.

The band compares the z-score with fixed numbers instead. Multiplying by 1.0260 never changes a z-score’s sign, so the exit test at 0 passes on the same days under either divisor. It can push a z-score across ±1, though. A z-score just inside 1 with divisor n − 1, such as 0.99, moves just outside it with divisor n, and that day can enter a position.

### What dividing by n changes

On Chan’s file the z-score exists on 1,461 of the 1,480 days. It sits beyond ±1 on 756 of them with divisor n − 1 and on 777 with divisor n. Although the exit test passes on the same days, an exit can move, because a position has to be open to close. All 76 exits with divisor n − 1 fall on the same days with divisor n, but the run with divisor n has a 77th, on 2007-06-07. It closes a short entered on 2007-05-29 that the run with divisor n − 1 never opened. The units differ on 15 days, and that is enough to move both figures. Seven of them are that short. On the other eight, the run with divisor n enters a position one day before the run with divisor n − 1 does.

1. **The APR** becomes 0.183306, up by 0.005057. The book’s rounding would print it as 18.3 percent.
2. **The Sharpe ratio** becomes 0.984872, up by 0.020199. The book would print 0.98.

![An animated whiteboard sketch titled “One close, two divisors”, drawn slowly stroke by stroke and held for twelve seconds when finished. It is drawn to one scale from the run, two dots for each of 11 traded days. A red dashed line labelled “+1” crosses the board, with “short above +1” under its right end, and a grey line labelled “0” runs below it. Black dots for each day’s z-score appear, labelled “left dots: divide by n − 1”, with the dates “2007-05-24 to 2007-06-08” at the top right. Brown dots then appear just right of the black ones, labelled “right dots: divide by n”, each level with its black neighbour to the eye. The dots start at about 0.3, sit between about 0.8 and +1 from the second day to the seventh, then fall, and the last two sit below 0. A brown ring circles the third day’s pair, where the black dot sits just under +1 and the brown just over it, too close to the line to tell apart by eye, and “0.9867 × 1.0260 = 1.0124” appears beside it. Below, a thin grey strip labelled “n − 1 (bollinger.m)” is marked “flat throughout”. Under it, a strip labelled “n” is a thin grey line marked “flat” for two days, a thick red bar marked “short” from the ringed day for seven days, and a thin grey line marked “flat” for the last two, with “a 77th exit, on 2007-06-07” beneath where the red bar ends. Last, “the units differ on 7 days here and 15 in all” appears at the lower left.](../docs/figures/bollinger_sketch_two_divisors.gif)

*Drawn to one scale from the run on Chan’s file. A day’s two z-scores differ by too little to see at this scale, so each pair sits side by side and the ring’s label gives the figures.*

Swapping the moving average as well, for Chan’s `smartMovingAvg`, which also skips missing values, moves nothing further. The spread has no missing values for it to skip, so the two averages differ only in the order they add up a window, which changes the last digit or two and leaves every day’s return as it was. The dashed line in the figure’s bottom panel is the band with the deviation divided by n.

`bollinger.m` calls `movingStd`, so the transcription divides by n − 1, and that divisor is the one that matches Chan’s figures. A port of this script that reached for the other helper would miss both. In Example 3.1 a matching figure said nothing about which helper was right, because the factor cancels out of the return. Here the figures tell the two helpers apart, because with a fixed threshold the factor changes which days trade.

## Lesson 4: one unit at most, and fewer trades

The band holds one unit or none, as location 1548 says. Over the 1,480 traded days it is short on 547, flat on 334 and long on 599.

The Example 3.1 post reports the hedge ratio below zero on 334 days of the same 1,480. On those days −h is positive, so one unit is long both ETFs. That matches the band’s flat count, which could suggest the band sits out exactly those days. It does not. The band is flat with the hedge ratio below zero on only 62 days.

Position changes are also far rarer. The band’s units change on 162 days, against 1,460 for the linear rule, which changes its units every day after its first. Its 162 changes come in three kinds.

1. **77 entries**, from flat to a unit.
2. **76 exits**, from a unit to flat. The run starts flat and ends holding a unit, so it has one more entry than exit.
3. **9 turns**, from one side to the other in a single day, as the rule section described.

The count of 162 understates how much the band trades. One unit holds −h shares of GLD for each share of USO, and h is refitted every day. So a held unit’s GLD leg is resized every day, even on a day the unit count stands still. Neither rule is charged a cost for any of it.

Location 1548 adds that a shorter lookback and smaller thresholds bring “more round trip trades and generally higher profits”. Nothing here tests that sentence. It would take a search over lookbacks and thresholds, run on data the search had not seen.

## Lesson 5: an exact reproduction checks the arithmetic, not the edge

That both figures match to six digits says the code, the data and the script’s comment agree. It says nothing about whether the band pays, for four reasons.

1. **The parameters are in-sample, meaning nothing shows they were fixed before these days were seen.** Location 1548 calls the entry threshold “a free parameter to be optimized in a training set”, and says the lookback “can be a free parameter to be optimized, or it can be set equal to the half-life of mean reversion”. The half-life is how long the spread takes, on average, to close half of its distance from its mean. Location 1559 sets the thresholds at 1 and 0 without saying how they were chosen. The 20-day lookback is the one location 1505 says was set with “the benefit of hindsight”.
2. **No cost is charged.** The band trades less often than the linear rule, but Lesson 4 shows it still resizes its GLD leg every day.
3. **The pair shows no cointegration.** A cointegration test asks whether some fixed mix of two prices is stationary, meaning it keeps returning to the same average rather than wandering off. The [post on testing a price spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-mean-reversion.md) explains how it works. The Example 3.1 post found that GLD and USO fail it on Chan’s file and that the 20-day hedge ratio changes sign. The band trades the same spread, so its profit too rests on a 20-day fit rather than on a relationship known to persist.
4. **A confirming test needs rules fixed first.** Reproducing Chan’s figures on his window tests his arithmetic. A result that could confirm the edge would need thresholds and a lookback fixed in writing first, and data the rule had never seen.

So the result is exploratory. It shows that Chan’s figures follow from his file and his script, and that the band beats the linear rule on the sample where their shared lookback was chosen.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the reversion is real.** The band trades the same spread as Example 3.1, and nothing here separates a real short-term reversion between gold and oil from a pattern that refitting a line every day on the last 20 days creates by itself.
2. **What costs would take.** Nothing here charges any, or measures how much the GLD leg is resized while a unit is held.
3. **Whether 1, 0 and 20 were fair choices.** The 20-day lookback was set with hindsight on this sample, and the book does not say how the thresholds were chosen. Nothing here tries any of the three on other data.

## What this means for a trader

One habit for each lesson.

1. **Check the script before the prose.** Here the two agree to every digit the book prints, which is worth knowing before arguing with the result.
2. **Compare two rules on one spread.** When the spread, the lookback and the code are shared, a difference in the figures belongs to the rule, and a drawdown is worth comparing beside the two figures the book prints.
3. **Find every place a z-score meets a fixed threshold.** A rule that compares a z-score with a fixed threshold can trade on different days when the divisor of its standard deviation changes, so a port has to use the helper its script called.
4. **Count what a position change hides.** A unit held unchanged can still trade one of its legs every day, so a count of changed units is a floor on trading, not the trading.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the band pays needs costs, thresholds and a lookback fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 3.2 and Kindle locations 1505, 1548 and 1559.
2. `bollinger.m` and `fillMissingData.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the band](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/bollinger.py), [the spread it trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/bollinger_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/bollinger_whiteboard.py), with the checks behind [the band’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_bollinger.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_bollinger_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_bollinger_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-26-bollinger-bands-on-gld-and-uso-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
