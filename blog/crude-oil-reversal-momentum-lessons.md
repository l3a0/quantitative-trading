# Chan’s crude oil rule reproduces, and on his window joining reversal to momentum wins by sitting out the days they disagree

*Algorithmic Trading joins a 30-day reversal rule to a 40-day momentum rule on crude oil futures and reports an APR of 12 percent and a Sharpe ratio of 1.1. Both figures land on Chan’s own file. The join turns out to be half of each rule held together, so it earns close to their average and beats them on his window by swinging less. On the four years before, one of the two loses too much for that to work.*

## Why join two rules that disagree

A trader who holds two signals has to decide what to do on the days they point opposite ways. A mean-reverting rule bets that a move will undo itself. A momentum rule bets that it will continue. On the same price, the two disagree often.

Ernest Chan’s second book, *Algorithmic Trading*, says the two can sometimes be combined to advantage. “Sometimes, the combination of mean-reverting and momentum rules may work better than each strategy by itself” (Chan, 2013, location 2701). His example trades crude oil futures, CL. It buys at the close when the price is below its close 30 trading days earlier and above its close 40 trading days earlier, shorts when the price is above the first and below the second, and otherwise holds nothing. He reports “The APR is 12 percent, with a Sharpe ratio of 1.1.” He names no window and prints no figure for either rule alone.

His script for the example, `CL_rev.m`, supplies both. It loads one of his saved files of continuous futures, which this post calls a **save** and names by the date in its file name, here 2012-05-04. It runs the rule over its 1,000 trading days of CL, and a comment under its print line records `APR=0.117600 Sharpe=1.100368`. It also runs three other rules on the same prices, including each rule alone, and prints nothing for them.

This repository ran the script’s rule and its three companions on Chan’s own file, and on two other saves of the same series. Three findings came out.

1. Both of Chan’s figures land, to every digit the script prints, and a save whose name is a week later still prints as 12 percent and 1.1.
2. On the book’s window the join beats each rule alone, and the reason is arithmetic. Holding half a position in each rule gives the join’s position, so the join earns close to the average of the two and wins by swinging less. Against momentum alone it earns less per day.
3. On the four years before the book’s window, reversal alone loses enough money that the same arithmetic drags the join below momentum alone.

**Every result here is exploratory.** Reproducing Chan’s figures uses up the 2008 to 2012 data on a rule he chose, and nothing shows the 30 and 40 days were fixed before he saw that window. The earlier four years were not set aside before they were read, so they are not a clean test either.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

A **lag** here is the close a fixed number of trading days earlier. The 30-day lag on a given day is the close 30 rows before it.

Each rule on its own reads one lag.

1. **Reversal alone** buys when the close is below its 30-day lag, because a price that has fallen is expected to come back, and shorts when the close is above it.
2. **Momentum alone** buys when the close is above its 40-day lag, because a price that has risen is expected to keep rising, and shorts when the close is below it.

Earlier in the same chapter, Chan measures whether two-year Treasury note futures trend before he trades momentum on them, which [the post on TU momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#why-measure-momentum-before-trading-it) reproduces. For the crude oil rule, the book names its two lags and says nothing about how they were picked.

On one shared lag the two would take opposite sides every day, and joining them would cancel. Chan gives them different lags and trades only where they agree. The join buys when the close is below its 30-day lag and above its 40-day lag, which is a dip inside a rise. It shorts on a bounce inside a fall, and holds nothing on any other day.

Every rule earns yesterday’s position on today’s percentage change in price, with no trading cost. Two figures summarise each run, both over every row, the days with no position included.

- **The APR** is the compounded annual return, `prod(1 + r)^(252/n) − 1` over n daily returns r. [The post on Chan’s 2012 reversal](https://github.com/l3a0/quantitative-trading/blob/main/blog/khandani-lo-reversal-lessons.md#lesson-1-every-figure-chan-prints-lands-on-his-own-file) explains compounding.
- **The Sharpe ratio** is the average daily return divided by its standard deviation, the typical size of a day’s move away from that average, scaled by √252 to a year. It measures return per unit of swing, with no risk-free rate taken off.

The script’s fourth rule, which it names “ComboOR”, takes a long wherever either of the join’s two buy conditions holds and a short wherever either short condition holds, and its position each day is the sum of the two. Lesson 2 shows it is the join under another name.

The prices are a **continuous future**. A futures contract expires, so a long history is stitched from one contract after the next, and at each switch, called a roll, the older history is shifted by the difference between the two contracts’ prices so the series has no jump. [The post on volatility against the stock index](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains the stitching. The shift means CL’s early closes sit well above the price that traded. The book’s window opens at 175.48 on 2008-05-19, two months before crude oil’s 2008 peak, which Chan dates elsewhere in the book to July 14, 2008, as [the post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#why-test-the-reason-a-strategy-failed) recounts. A percentage return divides each day’s dollar move by that shifted price, so the file decides the figures as much as the rule does.

Three of Chan’s saves were read, each named by the date in its file name.

1. **The 2012-05-04 save**, the one `CL_rev.m` loads. CL holds 1,000 rows, from 2008-05-19 to 2012-05-04, which is the book’s window.
2. **The 2012-05-11 save**, read over the same 1,000 days.
3. **The 2012-05-07 save**, whose CL closes equal the first save’s on all 1,000 of the book’s days. Its 998 earlier rows, from 2004-05-24 to 2008-05-16, extend the same series backward.

## Lesson 1: both figures land, and a save a week later prints the same to the book’s precision

Here is the join on the 2012-05-04 and 2012-05-11 saves, beside the script’s comment and the book.

```math
\begin{array}{l|r|r|r|r}
\text{Figure} & \text{2012-05-04 save} & \text{Script comment} & \text{Book} & \text{2012-05-11 save} \\ \hline
\text{APR} & 0.117600 & 0.117600 & \text{12 percent} & 0.117226 \\
\text{Sharpe ratio} & 1.100368 & 1.100368 & 1.1 & 1.100045
\end{array}
```

On the save the script loads, both figures land on every digit of its comment, and both round to the book’s figures. The 2012-05-07 save gives the same two figures to six decimals, since its closes on those days are the same.

The 2012-05-11 save is different. Its closes sit 0.27 higher on every one of the 1,000 days. The rule compares closes with closes, so a uniform shift changes no position. What it changes is the price each dollar move is divided by. A slightly larger divisor makes every return slightly smaller in size, and the APR falls to 0.117226 and the Sharpe ratio to 1.100045. Both still round to 12 percent and 1.1, so the book’s rounding cannot tell the two saves apart. The script’s comment matches the 2012-05-04 save, and nothing shows whether the book’s rounded figures came from that same run.

That is a mild case. [In the volatility post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run), the APR fell by more than half between two of Chan’s saves whose names are ten days apart. A continuous future is rewritten at every roll, so the save is part of what a backtest specifies, even when, as here, the change stays below the printed digits.

## Lesson 2: the join is half of each rule, so it wins by swinging less

On the book’s window, each rule alone scores below the join on both figures.

```math
\begin{array}{l|r|r|r|r}
\text{Rule} & \text{Average daily return} & \text{Standard deviation} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{The join} & 0.000463 & 0.006687 & 0.117600 & 1.100368 \\
\text{Momentum alone} & 0.000519 & 0.018748 & 0.090228 & 0.439049 \\
\text{Reversal alone} & 0.000440 & 0.018864 & 0.068326 & 0.370289
\end{array}
```

The table bears out Chan’s sentence on his own window. The book prints no figure for either rule alone, so these rows carry no verdict. Its first column shows momentum alone earning more on an average day than the join, yet losing on both figures.

The reason is that the join is not a third rule. Hold half a position in reversal alone and half in momentum alone.

1. **Where the two agree**, both halves point the same way and add to one full position. Those are exactly the days the join holds that position.
2. **Where they disagree**, a half long and a half short add to nothing. Those are exactly the days the join is flat.

So half of each rule gives the join’s position on every row but ten. Those ten, from 2008-07-01 to 2008-07-15, are the warm-up rows at the start of the run, where the 30-day lag exists and the 40-day lag does not yet, so reversal alone holds a position and the join cannot. On every day but ten, then, the join’s daily return is the average of the two rules’ daily returns.

The two rules mostly disagree. Of the 960 rows where both lags exist, they agree on 157 and take opposite sides on 803. On each of those 803 days one rule’s gain is the other’s loss, and the average is zero. The join holds a position on 157 days, long on 98 and short on 59, and is flat on the other 843.

The join’s average day, 0.000463, sits between reversal’s 0.000440 and momentum’s 0.000519. It sits slightly below the plain average of the two, because on the ten warm-up days reversal alone traded and the join did not. Cancelling 803 days of opposite bets gives a standard deviation of 0.006687, a little over a third of either rule’s. The Sharpe ratio divides the first by the second, so the join wins it easily.

The APR follows the same way, because compounding charges for swings. A day that loses 2 percent followed by one that gains 2 percent leaves 0.98 × 1.02 = 0.9996 of the capital, a small loss from two moves that cancel in the average. Larger swings lose more to this, and the two rules alone swing hard. The chart below shows how hard.

![Two line charts, one above the other, each plotting the compounded cumulative return of three rules on crude oil: the join in a heavy black line, momentum alone in brown and reversal alone in red. The upper chart covers the book’s window, May 2008 to May 2012. Momentum alone climbs to 117.0 percent by June 11, 2009, then drifts down to end at 40.9 percent. Reversal alone falls to −58.7 percent by February 18, 2009, then climbs back to end at 30.0 percent. The join moves in flat steps, stays within a few percent of zero through 2008, never falls below −4.0 percent, and ends highest of the three at 55.5 percent. The lower chart covers May 2004 to May 2008. Momentum alone wanders between about −7 and 12 percent until late 2007, then climbs to end at 43.0 percent. Reversal alone drifts down to about −29 percent and ends at −23.6 percent. The join sits below zero for most of the period, as low as about −11 percent, and ends at 8.7 percent. The title calls the chart exploratory, and the note says the lower chart’s prices sit far above the traded price.](../docs/figures/cl_reversal_momentum.png)

*The join, momentum alone and reversal alone, compounded daily with no cost, on Chan’s continuous CL, shifted at each roll. Above, the book’s 1,000 rows on the save the script loads. Below, the 998 rows before them on the 2012-05-07 save. `CL_rev.m` plots a fourth curve, ComboOR, which this chart leaves out.*

Momentum alone rose 117.0 percent and then gave back most of that gain, ending at 40.9 percent. Reversal alone fell 58.7 percent before recovering to 30.0 percent. Sitting out the days they disagreed, the join never lost more than 4.0 percent from its start, and finished at 55.5 percent.

Against momentum alone, then, “work better” here means smoother rather than more profitable per day.

The same picture explains one change tried here and the script’s last rule.

1. **Swapping the lags, a change tried here, reverses the rule.** With reversal on the 40-day lag and momentum on the 30-day lag, a buy needs the close below the 40-day lag and above the 30-day lag, which is the original’s short condition. Every long becomes a short. The Sharpe ratio flips sign exactly, to −1.100368, and the APR becomes −0.115294, not quite the negative of 0.117600 because compounding is not symmetric. Which lag carries which rule decides the sign of every position. [The post on crude oil’s calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md#lesson-2-the-trade-bets-the-spread-moves-further-from-its-average) found another of Chan’s crude oil scripts whose trade bets the opposite way from what its comments describe, so a rule’s sign is worth checking by running it rather than by reading it.
2. **ComboOR adds no evidence.** Where both buy conditions hold, neither short condition does, so it holds one long. Where neither buy condition holds, both short conditions do, so it holds one short. Where exactly one buy condition holds, the other rule’s short condition holds too, so it scores a long and a short, which add to nothing. So it matches the join everywhere except the same ten warm-up rows, where it trades reversal alone. Its APR of 0.125917 and Sharpe ratio of 1.123042 differ from the join’s only through those ten rows.

## Lesson 3: on the four years before, the losing half drags the join below momentum alone

The 2012-05-07 save holds the same series back to 2004-05-24. Its 998 rows before the book’s window give a different ordering.

```math
\begin{array}{l|r|r|r|r}
\text{Rule} & \text{Average daily return} & \text{Standard deviation} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{The join} & 0.000091 & 0.003922 & 0.021324 & 0.369864 \\
\text{Momentum alone} & 0.000406 & 0.009765 & 0.094589 & 0.660514 \\
\text{Reversal alone} & -0.000222 & 0.009792 & -0.065694 & -0.359464
\end{array}
```

Momentum alone beats the join on both figures, and reversal alone loses money.

The arithmetic from Lesson 2 still holds. Half of each rule gives the join’s position on all but 12 of these rows. Ten are the warm-up rows again. The other two, 2005-06-15 and 2007-04-17, are days when the close equals its 40-day lag exactly, which leaves momentum alone with no position while reversal alone holds one. Of the 958 rows where both lags exist, the two rules agree on 162 and disagree on 796.

So the join is still close to the average of the two rules, and here one of them loses. Its average day is 0.000091, near the plain average of a rule that earns 0.000406 a day and one that loses 0.000222. Cutting the swings no longer rescues it. Its standard deviation is about 40 percent of momentum’s, but its average day is under a quarter of momentum’s, and its Sharpe ratio falls to 0.37 against momentum’s 0.66.

Here the losing half loses too much for the smaller swings to make up. The join earns close to the average of the two rules’ days, so a rule that loses money lowers that average. Whether the smaller swings outweigh the loss depends on how much the rule loses and how often the two cancel, and on these four years they do not. Chan wrote “Sometimes”, which allows exactly this. The segment does not contradict the book. It shows the advantage is not general.

Two cautions limit what this segment can show.

1. **Its prices are shifted far from what traded.** The series closes at 119.12 on 2004-05-24, while West Texas crude averaged $41.51 over 2004 on the US Energy Information Administration’s spot price series, the price of oil delivered that day. Each day’s dollar move is divided by a price far above what traded, so every percentage return comes out smaller in size than what a trader earned. These are the rule’s figures on Chan’s series, not a trader’s.
2. **It is not data set aside before the rule was chosen.** The years before the book were in Chan’s own save, and nothing was written down here before they were read. [The commodity seasonals post](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md#lesson-3-a-trade-chosen-after-looking-at-the-history-is-tested-by-the-years-after-the-book) tested Chan’s trades on the years after his book, which he could not have seen. Years before a book are years its author could have looked at.

The result is exploratory either way. It is consistent with the join’s advantage on the book’s window resting on both rules earning there, and says nothing about whether either would earn next.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the lags were chosen on this window.** The book names 30 and 40 days and says nothing about how they were picked. A little later in the same section, writing about momentum strategies, Chan warns against data snooping, meaning a rule fitted to the history it is then tested on, and writes that “The real test for the strategy is, as always, in true out-of-sample testing” (location 2715). A search over other lags would multiply the chances of a lucky fit, and this run tries none.
2. **What costs would take.** The book charges none and neither does this run. The join changes position 124 times in 1,000 days, and nothing here measures what a cost on each change would take from 12 percent.
3. **What the earlier segment would give on traded prices.** Its figures are on a series shifted far above the price that traded, and no unadjusted CL series for those years is committed here.

## What this means for a trader

One habit for each lesson.

1. **Record which file a backtest read.** A continuous future is rewritten at every roll, so the same rule on the same days can print different figures from saves a week apart.
2. **Before trusting a combined rule, compare it with its parts held together.** If half of each rule gives the combined position, the combination’s average day sits between its parts’, so any advantage over the better part comes from the swing it removes. Read the average day and the standard deviation separately to see which one moved.
3. **Check what each part earns on its own.** A combination averages its parts, so a part that loses money lowers its average day. Check whether the smoother ride makes up for that, rather than assuming it does.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 2701 and 2715.
2. Chan, E. P. `CL_rev.m`, as published in the [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) repository at commit `e4bc46f`.
3. US Energy Information Administration. [Cushing, OK WTI Spot Price FOB, annual, dollars per barrel](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=A).

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cl_reversal_momentum.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cl_reversal_momentum_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cl_reversal_momentum.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cl_reversal_momentum_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-31-crude-oil-reversal-joined-to-momentum-chans-algorithmic-trading) that sets each of Chan’s figures beside what was found here.*
