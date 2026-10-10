# Chan’s roll-return signal on Treasury futures beats his momentum rule by stepping aside, and misses all three of his figures

*Algorithmic Trading revises its momentum strategy on TU, the two-year Treasury note future, to trade the lagged roll return instead of the past return. It reports a higher APR, a higher Sharpe ratio and a smaller drawdown. On one rebuilt series the comparison holds, mostly because the old rule never leaves the market in that window and the new one does. None of the book’s three figures reproduces.*

## Why trade the roll return instead of the past return

A trend-following rule on futures has a puzzle behind it. Why should a future’s past return say anything about its next one? Ernest Chan’s second book, *Algorithmic Trading*, offers an answer and then tests it.

The test starts from Example 6.1, a momentum strategy on TU, the two-year Treasury note future. Each day it buys if TU’s price is above its level 250 trading days earlier and sells if it is below, and it holds each of those bets for 25 days. Chan reports that from 2004-06-01 to 2012-05-11 “the Sharpe ratio is a respectable 1”, with an APR of 1.7 percent and a maximum drawdown of 2.5 percent (Chan, 2013, location 2668). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk. The maximum drawdown is the largest fall from a peak.

Then comes the explanation. A future’s total return splits into the move of the spot price under it and a roll return, which the future earns by converging on the spot as it nears expiry. Chan argues that the roll return is what makes futures trend: “Typically, the sign of roll returns does not vary very often” (Chan, 2013, location 2683). The spot return swings in both directions from day to day. So if the roll return keeps its sign for months and dominates the average, a long holding period sees a total return that keeps its sign too.

If that is the cause, the roll return itself should be a better signal than the past total return. Location 2690 says so, calling it “a cleaner and potentially better momentum signal”, and tries it on TU. The rule goes long when the lagged roll return is above 3 percent a year, short when it is below −3 percent, and flat otherwise. Chan reports “a higher APR of 2.5 percent and Sharpe ratio of 2.1 from January 2, 2009, to August 13, 2012, with a reduced maximum drawdown of 1.1 percent” (Chan, 2013, location 2690).

No script ships for that experiment, so this repository wrote the rule down itself and ran it on Chan’s own files. The rule misses all three printed figures. It does beat Example 6.1 on all three when both run on one series over one window, and Chan’s own continuous close agrees. The Sharpe ratio carries most of that win, and the APR margin is about the size of the rebuilt series’ own error.

**Every result here is exploratory.** The rule was written down after about 90 scratch readings of the same data, so the run cannot count as a test of whether the roll-return signal works. It can say what the book’s sentence gives on Chan’s files under one stated reading, and nothing about the trade today.

The four lessons below say what the run does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

A futures contract is a promise to buy or sell something on a set date, and each delivery month trades as its own contract. The [post on calendar spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) explains them. When later contracts trade above nearer ones, the market is in contango, and a long position loses as its contract’s price sinks toward the spot. When later contracts trade below nearer ones, the market is in backwardation, and a long position gains as its price rises toward the spot. That gain or loss is the roll return.

### The roll return γ

Chan estimates the roll return, which he writes γ, in Example 5.3, by regressing “the prices of the various contracts against their time to maturity” on a fixed day (Chan, 2013, location 2399). His script, `estimateFuturesReturns.m`, does it on each day with the log prices of the five nearest contracts against their place in line, 1 to 5. Then γ is −12 times the slope, an annual rate. A positive γ means the later contracts are cheaper, which is backwardation and pays a long position.

The −12 assumes adjacent contracts are a month apart. TU’s contracts are a quarter apart, so the script’s γ is three times the rate the book’s words describe. On TU, the reading in months is a third of the reading in contract columns on all 1,087 rows where γ is defined. Location 2690 gives its threshold in annualized terms, so the reading in months might look like the right one. It peaks at 2.447 percent inside the test window and never reaches 3 percent, so a rule on it never trades. The rule here therefore reads γ in columns, the script’s unit. That is a reading of the book, and the post says so wherever it matters.

### Example 6.1’s rule

Example 6.1 trades in 25 tranches. A tranche is one twenty-fifth of the capital, opened on one day and held for 25. Each day opens a long tranche if the price is above its level 250 rows back, or a short one if it is below, and the oldest tranche closes. So the position runs from 25 tranches short to 25 long, and each day’s return is the position’s profit divided by 25.

### The declared rule

With no script to transcribe, the rule was written down in five parts before the build.

1. **The signal.** γ in column units, from Chan’s Example 5.3 fit.
2. **The threshold.** Long where γ is above 0.03 and short where it is below −0.03, both strict. A day with no γ opens neither.
3. **The lag.** The position set on one day earns the next day’s return, which is Example 6.1’s own convention.
4. **The window.** Every series is computed on the full file and cut last to 2009-01-02 to 2012-08-13, the 913 trading days location 2690 names. Cutting first would leave Example 6.1’s 250-day signal off for most of the window. With the cut first, its signal is live on only 663 of the 913 rows and its APR falls to 0.008435.
5. **The arithmetic.** Example 6.1’s script, `TU_mom.m`, for the APR, the Sharpe ratio and the drawdown, with 252 trading days a year, no risk-free rate and no cost.

### The files

The data is one of Chan’s own saves, a strip, which is one file holding every contract of one future and its spot. This strip holds 93 TU contracts and the spot over 5,565 days, from 1990-06-22 to 2012-08-13, and was saved on 2012-08-14. It is the only file in the [repository’s data](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) that reaches the end of the book’s window.

Example 6.1 trades a continuous series of TU, which stitches the front contract’s prices across rolls. Chan’s saves of that series end in May 2012, three months short of the window. So the position here earns on a front-contract series rebuilt from the strip, which Lesson 3 describes. Example 6.1’s rule runs on the same rebuilt series, so the two rules are compared on one set of prices, rows and arithmetic.

## Lesson 1: the declared rule misses all three printed figures

Here are the three figures beside the book’s. A gap is the computed figure minus the printed one, at the book’s precision. The drawdown row shows its size, as the book prints it.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Book} & \text{Gap} \\ \hline
\text{APR} & 1.3725\ \text{percent} & 2.5\ \text{percent} & -1.1 \\
\text{Sharpe ratio} & 1.803348 & 2.1 & -0.3 \\
\text{Maximum drawdown} & 0.7299\ \text{percent} & 1.1\ \text{percent} & -0.4
\end{array}
```

All three miss. The APR and the Sharpe ratio land below the book, and the drawdown is shallower than the book’s.

A different download of the prices is the first thing to suspect, because vendors restate history. It does not explain this miss. Chan’s 2012-05-11 save, a continuous TU close that ends on that day and was saved the next, covers 849 of the window’s 913 rows. On those rows, the declared rule earning that close gives an APR of 1.437321 percent, a Sharpe ratio of 1.791969 and a drawdown of 0.807695 percent. The rebuilt series gives 1.468184 percent, 1.870808 and 0.729860 percent on the same rows. Both sit far from the book. The 64 rows no saved close covers would have to carry the rest of the gap.

The rule is simple in this window. It is long on 572 of the 913 rows, 62.65 percent, and flat on the rest. It is never short, and it changes position 21 times. γ never falls below −3 percent, so the short side never fires. It also opens the window flat. γ is 1.61 percent on 2008-12-31, under the threshold. On the window’s first three days, all five contracts carry one price, so the fit’s slope and γ are zero to within 10⁻¹³.

A miss cannot say whether Chan computed a different number or read his own sentence differently. The sentence leaves the lag, the series the position earns and the unit of γ open, and each choice is part of the method. Lesson 4 shows one reading that lands two of the three figures, and why it is not the one tested.

The figure below draws both rules on the rebuilt series. The book prints no chart for this experiment, so the figure is this repository’s own.

![Two charts sharing a date axis from January 2009 to August 2012, with the same rows shaded grey in both. The top chart is the compounded cumulative return of two rules on TU, in percent, before costs. The brown line, Example 6.1’s rule, wanders around zero through mid-2009, climbs to about 3.8 percent by late 2010, dips, rises to about 5 percent by late 2011 and ends at 4.9 percent. The green line, the declared rule, is flat at zero for the first months, flat again through each shaded stretch, and otherwise moves with the brown line. It ends just above it, at 5.1 percent. Its heading sets the declared rule’s APR of 0.013725 and Sharpe ratio of 1.803348 beside the book’s 2.5 percent and 2.1, gives Example 6.1’s rule 0.013377 and 1.196742, and says Example 6.1’s rule holds all 25 tranches long on every window row, so its line is holding TU. The bottom chart is the roll return γ in column units, a step-like line between about 0 and 7.3 percent, with dashed lines at 3 and −3 percent. The shaded stretches follow γ’s spells below 3 percent, one row late, and γ never comes near −3 percent. Its heading says γ peaks at 0.073403 on 2009-10-12 and the rule is long on 572 rows, short on none and flat on the 341 shaded rows. The title calls the figure exploratory, and the note names Chan’s TU strip, saved 2012-08-14, the front contract rebuilt from it, and the rule declared after about 90 scratch readings.](../docs/figures/roll_momentum.png)

*Above, the compounded cumulative return of both rules on the rebuilt front contract, with the rows the declared rule sits flat shaded. Below, the roll return γ in column units against the 3 percent thresholds.*

## Lesson 2: it beats Example 6.1 by stepping aside

Location 2690’s comparison is three claims: a higher APR, a higher Sharpe ratio and a smaller drawdown than Example 6.1. A claim holds when the declared rule beats Example 6.1’s rule on the same series and rows. Here are the two rules side by side.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Declared rule} & \text{Example 6.1's rule} & \text{Margin} \\ \hline
\text{APR} & 0.013725 & 0.013377 & +0.000348 \\
\text{Sharpe ratio} & 1.803348 & 1.196742 & +0.606606 \\
\text{Maximum drawdown} & -0.007299 & -0.009167 & +0.001868
\end{array}
```

Drawdowns are signed here, so the larger number is the smaller fall. All three claims hold. They hold on Chan’s 2012-05-11 save too, over the 849 rows it covers. There the declared rule gives 1.437321 percent, 1.791969 and a drawdown of 0.807695 percent, against Example 6.1’s 1.406935 percent, 1.187438 and 0.9851 percent.

The margins are not equally strong. The rebuilt series and Chan’s close differ in APR by 0.000309 over the rows they share, which is the rebuild’s own error. The APR margin of 0.000348 is about that size, so the APR half of the claim is the weakest. The Sharpe ratio’s margin of 0.606606 is the one that carries it.

### Where the Sharpe ratio’s margin comes from

In this window Example 6.1 never leaves the market. On every day it opened a tranche during and just before the window, TU stood above its level 250 rows earlier, so all 25 tranches are long on all 913 rows. A rule that is fully long every day earns exactly the contract’s own return, so in this window Example 6.1’s rule is the same as buying TU and holding it.

The declared rule is that same long position with 341 rows taken out. Over those 341 rows, TU’s return compounds to −0.001244, close to nothing. Over the 572 rows the rule is long, it compounds to 0.050629, which is the declared rule’s whole return. So the two rules earn almost the same. The declared rule’s average annual return is 0.013661 against 0.013351.

What differs is the risk. Sitting out 341 rows that went nowhere removes their day-to-day swings without removing any return. The declared rule’s annual volatility is 0.007575 against 0.011156 for holding TU. Divide each average return by its volatility and the Sharpe ratios of 1.80 and 1.20 follow.

The figure’s top panel shows it. The declared rule’s line goes flat through every shaded stretch, while Example 6.1’s line wanders up in some of them and down in others, and the two end close together.

So on this window the roll-return signal’s advantage is that it was out of the market on 341 of the 913 days, and those days happened to earn nothing. That is a real difference between the rules. It is also a narrow one. It says nothing about Example 6.1 in a window where TU fell, where Example 6.1 would go short and the declared rule, never short here, could not.

### The book’s own comparison spans two windows

The book sets its 2.5 percent, 2.1 and 1.1 percent against Example 6.1’s printed 1.7 percent, 1 and 2.5 percent. Those printed figures cover 2004-06-01 to 2012-05-11, while the new ones start in 2009. So the book compares two windows as well as two rules. On one window, the APR margin is 0.000348, far smaller than the gap between the printed 2.5 and 1.7 percent.

## Lesson 3: a series nobody saved has to be rebuilt

This repository rests on one premise. A vendor can restate a price history, so a number computed from a series nobody kept is a number nobody can check. This experiment meets the other side of that problem. The series it needs, TU’s front contract through August 2012, exists in no file anyone kept. So it has to be built, and then checked against the nearest thing that was kept.

A continuous future stitches one contract after another, and each switch is a roll. The [post on VX against ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md) explains how a saved continuous series shifts its earlier prices at each roll so the series has no jump. The rebuild here does something simpler. Each day’s return is taken within one contract, from yesterday’s close to today’s, so a roll never enters a return.

The question is which day to switch. The rule takes the nearest contract that was priced the day before and still has at least seven trading rows left before its last price. So the old contract earns through the seventh row before its last price and the new one from the sixth. The March 2012 roll shows it. The March 2012 contract’s last price in the strip is on 2012-03-30. It earns through 2012-03-21, and the June contract earns from 2012-03-22.

Seven rows is not a choice made to fit a result. It was read off Chan’s 2012-05-11 save, which follows the old contract until eight rows before its last price, takes the new one from six, and jumps by the adjustment on the row between. The check against that save covers the 1,999 daily changes the two series share.

1. **The returns agree.** They correlate at 0.998359.
2. **Every disagreement sits on the roll row.** 30 changes differ by more than the files’ rounding. All 30 fall on the seventh row before a contract’s last price, where the save’s back-adjustment jumps and the rebuild takes a return within one contract instead. The save’s span holds 32 rolls, and on the other two the save’s jump lands within rounding.

So the rebuild follows the same contracts as the save on every row, and it differs only where the save’s stitching makes a jump. That bounds what the rebuild can be trusted for. Its APR over the shared rows sits 0.000309 above the save’s, and any margin smaller than that, like Lesson 2’s APR margin, is a margin the rebuild cannot vouch for on its own.

## Lesson 4: a rule declared late, and a reading set aside

A rule fixed before the data is read can be tested by the data. A rule fixed after reading many variants has already been fitted to it. This experiment’s rule was meant to be written down before any figure was computed. It was not. Two scratch runs read about 90 variants first, across lags, held contracts, units, thresholds and roll rules. That count comes from the run’s own written disclosure, and no test here pins it.

The declaration rests on three grounds the scratch runs did not choose.

1. **The lag** is Example 6.1’s own convention, a position set on one day earning the next.
2. **The series** is the one location 2690 says it revises, Example 6.1’s front contract.
3. **The roll row** was read off the 2012-05-11 save, as Lesson 3 describes, rather than chosen by any strategy figure.

One reading in the scratch runs came close to the book, and it is worth showing because it is tempting. It holds the fifth contract priced the day before, the farthest of the five that γ is fitted on, instead of the front contract. That gives an APR of 2.4712 percent, a Sharpe ratio of 2.144165 and a drawdown of 1.1583 percent. The first two land the book’s 2.5 percent and 2.1. The drawdown misses 1.1 percent.

It is set aside because of how it is built. The position is set by γ, and γ is fitted partly on that same fifth contract’s price. Suppose the fifth contract closes a little low one day. The slope steepens, γ rises, and the rule goes long that same contract. If the low close was noise that reverses the next day, the long position earns the reversal. So part of what the reading earns could come from the fit and the held contract sharing one price, rather than from the roll return the book describes. A scratch fit of γ on the four nearest contracts alone, which leaves the held contract out of the fit, lowered the Sharpe ratio to 1.801. No test repeats that 1.801, so the shared price is a candidate explanation rather than a finding. One variant is pinned beside it. Counting the fifth contract only among those priced on both days, which skips a nearer contract that stopped trading the day before, gives a Sharpe ratio of 1.957852.

Picking this reading now, after seeing that it lands the book, would be a search. A search on one file can always find a variant that matches a printed number. So the fifth-contract reading stays a row beside the replication and is never its verdict.

The same reasoning sets this post’s label. The declaration came after the readings, so nothing here is a registered test of the roll-return signal, one whose rule was written down before any data was read. A registered test would fix its rule first and run on data this search never loaded.

## What this replication cannot say

Three things are beyond it.

1. **Whether the signal works out of sample.** The rule was written down after about 90 readings of the same strip, so its margins are not a test.
2. **What Chan held.** No script ships for location 2690, and the book does not say how far the roll return is lagged or which price the position earns. The fifth-contract reading lands near the book, and choosing it after its number was seen would be a search.
3. **What a trader would earn.** The returns are on the notional value of one contract, with no cost and no margin. Location 2668 puts TU’s notional value at about $200,000 against a margin of about $400, so any real position would be leveraged, and the figures here say nothing about the leverage.

## What this means for a trader

One habit for each lesson.

1. **Test the reading before blaming the data.** Here Chan’s saved close lands near the rebuild, so the miss lives in how the sentence was read rather than in which file was downloaded.
2. **Ask what the benchmark was doing.** Example 6.1 was fully long for the whole window, so beating it meant beating buy and hold, and the win came from sitting out days that earned nothing.
3. **Check a rebuilt series against the nearest saved one, and treat its error as a floor.** A margin smaller than the rebuild’s own error is not evidence for either rule.
4. **Write the rule down before reading the data, and distrust the variant that lands the book.** A reading found after the number is seen has already been fitted to it.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 5.3 and 6.1 and Kindle locations 2399, 2668, 2683 and 2690.
2. `TU_mom.m` and `estimateFuturesReturns.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [both rules and the rebuild](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_momentum.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_momentum_figures.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_momentum.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_momentum_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-36-tu-momentum-traded-on-the-lagged-roll-return-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
