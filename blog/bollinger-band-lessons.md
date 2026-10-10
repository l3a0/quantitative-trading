# Chan’s Bollinger band on gold and oil reproduces to six digits, and its threshold makes the divisor matter

*Example 3.2 trades the same gold and oil spread as Example 3.1, but holds at most one unit and enters only beyond a fixed threshold. On Chan’s own file both of its printed figures land, and the fixed threshold is what lets the divisor of a standard deviation move them.*

## Why trade the same spread with a band

The [post on Example 3.1](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) traded the gold ETF GLD against the oil ETF USO on a price spread, USO − h·GLD. The hedge ratio h is refitted every day by a regression over the last 20 days. One unit of that portfolio holds one share of USO and −h shares of GLD, so the spread is its price. The z-score is how many 20-day standard deviations the spread sits from its 20-day average. That post’s rule, called the linear rule here, holds minus the spread’s z-score in units of the portfolio. So it buys more as the spread falls further below its average and sells more as the spread rises further above it. It is in the market every day, and its size changes every day.

Ernest Chan’s second book, *Algorithmic Trading*, offers a rule for practical trading on the same signal, the Bollinger band (Chan, 2013, location 1548). The rule is named for a band drawn a set number of standard deviations either side of the spread’s moving average. It enters only when the spread leaves the band, and it leaves when the spread comes back. At any time it holds “either zero or one unit (long or short) invested”, which Chan says makes it “very easy to allocate capital to this strategy or to manage its risk”.

His Example 3.2 trades the GLD and USO spread with that band and reports an APR of 17.8 percent and a Sharpe ratio of 0.96, “quite an improvement from the linear mean reversal strategy” (Chan, 2013, location 1559). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.

Chan published the script, `bollinger.m`, and the data file it reads. This repository keeps a copy of the file and ran a line-by-line transcription of the script on it. Both figures the script prints land to six decimals, an APR of 0.178249 and a Sharpe ratio of 0.964673.

**Every result here is exploratory.** Chan chose the pair, the thresholds and a lookback he calls “near-optimal” with “the benefit of hindsight” (Chan, 2013, location 1505), and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the trade pays today.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

The band keeps everything from Example 3.1 except how many units it holds.

1. **The spread and its z-score.** These are Example 3.1’s, unchanged.
2. **The entries.** Buy one unit when the z-score falls below −1. Sell one unit short when it rises above 1.
3. **The exits.** Close a long when the z-score rises above 0, which is where the spread crosses back through its average. Close a short when the z-score falls below 0.
4. **The days between.** A day with no entry and no exit carries yesterday’s units forward. Chan’s script does this with a helper called `fillMissingData`. So the units are only ever −1, 0 or 1.
5. **The return.** Each day’s profit on yesterday’s positions, divided by the gross dollars those positions held, as in Example 3.1. No cost is charged.

Each comparison is strict, so a z-score of exactly −1 enters nothing and one of exactly 0 exits nothing. No day on Chan’s file has a z-score of exactly −1, 0 or 1, so these figures cannot tell a strict comparison from an inclusive one. At these thresholds a long can also turn into a short in a single day. While a long is held, a z-score that jumps from below 0 to above 1 clears the long’s exit at 0 and the short’s entry at 1 on the same close.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), the same one Example 3.1 reads. It is Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and converted here to one file per ETF. It holds 67 ETFs over 1,500 trading days, from 2006-04-26 to 2012-04-09, and the script reads two of them. Like Example 3.1, the script throws away its first 20 days, where the first hedge ratio is still being fitted, so it trades the 1,480 days from 2006-05-24. The 20-day standard deviation first exists on 2006-06-21, the band enters its first position that day, and the position earns its first return on 2006-06-22, the same day as Example 3.1’s. This repository transcribed the script from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, which a second copy holds byte for byte.

## Lesson 1: both figures land to six digits, and the book rounds them correctly

Here is each rule’s pair of figures, computed, beside the script’s comment and the book.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{The band, APR} & 0.178249 & 0.178249 & \text{17.8 percent} \\
\text{The band, Sharpe ratio} & 0.964673 & 0.964673 & 0.96 \\
\text{The linear rule, APR} & 0.108335 & 0.108335 & \text{about 10.9 percent} \\
\text{The linear rule, Sharpe ratio} & 0.589651 & 0.589651 & \text{about } 0.59
\end{array}
```

All four match their scripts to the last digit printed. The band’s book figures are its script’s figures rounded, 0.178249 to 17.8 percent and 0.964673 to 0.96. That was not true of Example 3.1. Its script prints 0.108335, which is 10.8 percent at one decimal, and the book prints “about 10.9 percent” (Chan, 2013, location 1505). So for Example 3.2 the computation, the script and the book agree at every digit each one prints.

The figure below redraws the band. The top panel is the z-score it trades on, with its entry lines at −1 and 1 and its exit line at 0. The middle panel is the units it holds. The bottom panel sets its cumulative return beside the linear rule’s. The book prints the band’s alone, as Figure 3.3. Nothing compares the redraw with the chart in the book, so it is a redraw of the script’s plot rather than a checked copy.

![Three charts stacked on one shared date axis from May 2006 to April 2012. The top chart is the 20-day z-score of the price spread USO minus h times GLD. It swings back and forth across dashed red lines at −1 and 1 and a solid line at 0, reaching beyond both dashed lines many times a year. The middle chart is the units held, a step line that moves between short −1, flat 0 and long 1. Its heading says the band is short on 547 days, flat on 334 and long on 599, and that its units change on 162 days where the linear rule’s change on 1,460. The bottom chart is the compounded cumulative return of three runs, unlevered and before costs. The band, a solid green line, rises unevenly and ends well above the linear rule, a solid brown line. A dashed green line for the band with the moving standard deviation divided by n runs close to the solid green line throughout. The legend sets each run’s APR and Sharpe ratio: 0.178249 and 0.964673 for the band, 0.108335 and 0.589651 for the linear rule, and 0.183306 and 0.984872 for the diagnostic. The title calls the redraw exploratory, and the note names Chan’s file and says the 20-day lookback was chosen with hindsight.](../docs/figures/bollinger_band.png)

*The z-score the band trades on, the units it holds, and its cumulative return beside the linear rule’s, redrawn on Chan’s file over the 1,480 traded days. The dashed line divides the moving standard deviation by n rather than n − 1, which Lesson 3 explains.*

## Lesson 2: the same spread, a different rule, better figures

Chan calls the band “quite an improvement” on the linear rule, so the reproduction checks the two measures he names. The APR rises from 0.108335 to 0.178249, by 0.069915. The Sharpe ratio rises from 0.589651 to 0.964673, by 0.375022. Both rules trade one spread, built by the same code, with one 20-day lookback. So the difference between them is the rule alone.

A third measure points the same way, though the book prints it for neither rule. A drawdown is a fall from the highest value reached so far. On the compounded cumulative return, the comparison runs as follows.

1. **The band.** Its deepest drawdown is −21.83 percent, with its trough on 2009-05-21. Its longest spell below a high lasts 252 trading days, from 2008-12-08 to 2009-12-07.
2. **The linear rule.** Its deepest drawdown is −34.24 percent, with its trough on 2009-01-06. Its longest spell below a high lasts 640 trading days, from 2008-12-08 to 2011-06-22.

Both spells start the day after the same high, on 2008-12-05. The band falls less far and regains its high in less than half the time.

The reproduction’s test of that claim was written after the first transcription had run, and it asks only that both figures be higher, by any amount. A test chosen after its numbers are seen proves less than one written down first, so this one shows only that his sentence holds on his file.

## Lesson 3: a fixed threshold makes the divisor matter

Lesson 5 of [the Example 3.1 post](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) pointed ahead to this example. Chan’s code ships two moving standard deviation helpers. A standard deviation over n days adds up each day’s squared distance from the average, divides that sum, and takes the square root. The plain `movingStd` divides by n − 1, and `smartMovingStd`, which skips missing values, divides by n. Over 20 days the deviation divided by n is the one divided by n − 1 times √(19/20). So every z-score built from it is the other multiplied by √(20/19), larger in size whatever its sign.

```math
z^{(n)}_t = \sqrt{\tfrac{20}{19}}\; z^{(n-1)}_t \approx 1.0260\, z^{(n-1)}_t
```

Here z⁽ⁿ⁻¹⁾ₜ is day t’s z-score with the n − 1 divisor and z⁽ⁿ⁾ₜ is the same day’s with n. The linear rule holds minus the z-score in units, so the factor scales every position. Its return is profit over gross dollars, and the factor multiplies both, so it cancels. That is why the two helpers gave Example 3.1 the same figures.

The band compares the z-score with fixed numbers instead. Multiplying by 1.0260 never changes a z-score’s sign, so the exit test at 0 passes on the same days under either divisor. It can push a z-score across ±1, though. A z-score just inside 1 under n − 1, such as 0.99, moves just outside it under n, and that day can enter a position.

On Chan’s file the z-score exists on 1,461 of the 1,480 days. It sits beyond ±1 on 756 of them under n − 1 and on 777 under n. An exit can still move, because a position has to be open to close. All 76 exits under n − 1 fall on the same days under n, but the run divided by n has a 77th, on 2007-06-07. It closes a short entered on 2007-05-29 that the n − 1 run never opened. The units differ on 15 days, and that is enough to move both figures.

1. **The APR** becomes 0.183306, up by 0.005057. The book’s rounding would print it as 18.3 percent.
2. **The Sharpe ratio** becomes 0.984872, up by 0.020199. The book would print 0.98.

Swapping the moving average for its `smart` version as well moves nothing further, because the spread has no missing values for it to skip. The dashed line in the figure’s bottom panel is the band with the deviation divided by n.

`bollinger.m` calls `movingStd`, so the transcription divides by n − 1, and that divisor is the one that lands Chan’s figures. A port of this script that reached for the other helper would miss both. In Example 3.1 a matching figure said nothing about which helper was right, because the return could not see the scale. Here the figures tell the two helpers apart, because a fixed threshold makes the scale decide which days trade.

## Lesson 4: one unit at most, and fewer trades

The band holds one unit or none, as location 1548 says. Over the 1,480 traded days it is short on 547, flat on 334 and long on 599.

The Example 3.1 post reports the hedge ratio below zero on 334 days of the same 1,480, the days one unit is long both ETFs. That matches the band’s flat count, which could suggest the band sits out exactly those days. It does not. The band is flat with the hedge ratio below zero on only 62 days.

Position changes are also far rarer. The band’s units change on 162 days, against 1,460 for the linear rule, which changes its units every day after its first. Its 162 changes come in three kinds.

1. **77 entries**, from flat to a unit.
2. **76 exits**, from a unit to flat. The run starts flat and ends holding a unit, so it has one more entry than exit.
3. **9 turns**, from one side to the other in a single day, as the rule section described.

The count of 162 understates how much the band trades. One unit holds −h shares of GLD for each share of USO, and h is refitted every day. So a held unit’s GLD leg is resized every day, even on a day the unit count stands still. Neither rule is charged a cost for any of it.

Location 1548 adds that a shorter lookback and smaller thresholds bring “more round trip trades and generally higher profits”. Nothing here tests that sentence. It would take a search over lookbacks and thresholds, run on data the search had not seen.

## Lesson 5: an exact reproduction checks the arithmetic, not the edge

That both figures match to six digits says the code, the data and the script’s comment agree. It says nothing about whether the band pays, for four reasons.

1. **The parameters are in-sample.** Location 1548 calls the entry threshold “a free parameter to be optimized in a training set”, and says the lookback “can be a free parameter to be optimized, or it can be set equal to the half-life of mean reversion”. The half-life is how long the spread takes, on average, to close half of its distance from its mean. Location 1559 sets the thresholds at 1 and 0 without saying how they were chosen. The 20-day lookback is the one location 1505 says was set with “the benefit of hindsight”.
2. **No cost is charged.** The band trades less often than the linear rule, but Lesson 4 shows it still resizes its GLD leg every day.
3. **The pair shows no cointegration.** A cointegration test asks whether some fixed mix of two prices is stationary, and the [post on testing a price spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-mean-reversion.md) explains how it works. The Example 3.1 post found that GLD and USO fail it on Chan’s file and that the 20-day hedge ratio changes sign. The band trades the same spread, so its profit too rests on a 20-day fit rather than on a relationship known to persist.
4. **The rule was chosen on the same days it is tested on.** Reproducing Chan’s figures on his window tests his arithmetic. A result that could confirm the edge would need thresholds and a lookback fixed in writing first, and data the rule had never seen.

So the result is exploratory. It shows that Chan’s figures follow from his file and his script, and that the band beats the linear rule on the sample where their shared lookback was chosen.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the reversion is real.** The band trades the same spread as Example 3.1, and nothing here separates a real short-term reversion between gold and oil from what a 20-day fit produces.
2. **What costs would take.** Nothing here charges any, or measures how much the GLD leg is resized while a unit is held.
3. **Whether 1, 0 and 20 were fair choices.** The 20-day lookback was set with hindsight on this sample, and the book does not say how the thresholds were chosen. Nothing here tries any of the three on other data.

## What this means for a trader

One habit for each lesson.

1. **Check the script before the prose.** Here the two agree to every digit the book prints, which is worth knowing before arguing with the result.
2. **Compare two rules on one spread.** When the spread, the lookback and the code are shared, a difference in the figures belongs to the rule, and a drawdown is worth comparing beside the two figures the book prints.
3. **Find every place a scale meets a fixed number.** A rule that compares a z-score with a threshold can see the divisor of its standard deviation, so a port has to use the helper its script called.
4. **Count what a position change hides.** A unit held unchanged can still trade one of its legs every day, so a count of changed units is a floor on trading, not the trading.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the band pays needs costs, thresholds and a lookback fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 3.2 and Kindle locations 1505, 1548 and 1559.
2. `bollinger.m` and `fillMissingData.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the band](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/bollinger.py), [the spread it trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/price_spread.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/bollinger_figures.py), with the checks behind [the band’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_bollinger.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_bollinger_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-26-bollinger-bands-on-gld-and-uso-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
