# Chan’s crude oil rule reproduces, and on his window, joining reversal to momentum wins by sitting out the days they disagree

*Chan joins reversal to momentum on crude oil and reports a 12 percent APR and a Sharpe ratio of 1.1. Both land. The joined rule trades like half of each, so it wins on his window by swinging less, and trails momentum on earlier years when reversal loses.*

## Why join two rules that disagree

A trader who holds two signals has to decide what to do on the days they point opposite ways. A mean-reverting rule bets that a move will undo itself. A momentum rule bets that it will continue. On the same price, the two disagree often.

Ernest Chan’s second book, *Algorithmic Trading*, says the two can sometimes be combined to advantage. “Sometimes, the combination of mean-reverting and momentum rules may work better than each strategy by itself” (Chan, 2013, Kindle edition, p. 207). His example trades crude oil futures, CL. It buys at the close when the price is below its close 30 trading days earlier and above its close 40 trading days earlier. It shorts when the price is above its close 30 trading days earlier and below its close 40 trading days earlier, and otherwise holds nothing. He reports “The APR is 12 percent, with a Sharpe ratio of 1.1.” A later section, “The rule and the file”, defines both figures. He names no window and prints no figure for either rule alone.

His script for the example, `CL_rev.m`, fills in the window and holds the code for each rule alone. It loads one of his saved files of continuous futures, which this post calls a **save** and names by the date in its file name, here 2012-05-04. A continuous future is a price history stitched together across expiring contracts.

The script runs the rule over the save’s 1,000 trading days of CL, and a comment under its print line records `APR=0.117600 Sharpe=1.100368`. This post calls those days, from 2008-05-19 to 2012-05-04, the book’s window, because they are the days his script for the example reads. The script also runs three other rules on the same prices and prints nothing for them.

1. Reversal alone.
2. Momentum alone.
3. A rule it calls “ComboOR”.

### What the reproduction found

This repository ran the script’s rule, which this post calls **the join**, and its three companions on the save the script loads. It also ran the join on two of Chan’s other saves of the same series. On one of them it ran each rule alone as well, over the four years before the book’s window. Three findings came out.

1. Both of Chan’s figures land, to every digit the script prints, and a save dated a week later still prints as 12 percent and 1.1.
2. On the book’s window the join beats each rule alone, and the reason is arithmetic. Holding half a position in each rule gives almost exactly the join’s position, so the join earns close to the average of the two and wins by swinging less. Against momentum alone it earns less on an average day.
3. On the four years before the book’s window, reversal alone loses enough money that the same arithmetic drags the join below momentum alone.

**Every result here is exploratory.** Reproducing Chan’s figures reruns the rule he chose, on the 2008 to 2012 data his script reads, so it checks his numbers and cannot test the rule. Nothing shows Chan fixed the 30 and 40 days before he saw that window. This repository did not set the earlier four years aside before reading them, so they are not a clean test either.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

A **lag** here is the close a fixed number of CL’s trading days earlier. The 30-day lag on a given day is the close 30 trading days before it.

Each rule on its own reads one lag.

1. **Reversal alone** buys when the close is below its 30-day lag, because a price that has fallen is expected to come back, and shorts when the close is above it.
2. **Momentum alone** buys when the close is above its 40-day lag, because a price that has risen is expected to keep rising, and shorts when the close is below it.

If both rules read the same lag, one would buy on exactly the days the other shorts, and joining them would cancel. Chan gives them different lags and trades only where they agree. The join buys when the close is below its 30-day lag and above its 40-day lag, which is a dip inside a rise. It shorts on a bounce inside a fall, and holds nothing on any other day.

![An animated whiteboard sketch titled “A dip inside a rise, a bounce inside a fall”, drawn slowly stroke by stroke. It is schematic: each panel keeps the order of its day’s three closes up the board. It draws neither the gaps between those closes nor the days between them to scale. The left panel comes first. A black line rises from a low black dot to a high one and falls back to a dot between them, and along the bottom the three dots are labelled, in that order, “40 days ago”, “30 days ago” and “today”. Above the panel, “the join’s first long, 2008-07-30” names the day. A grey dashed line runs from the high dot across past today’s dot, and a line beneath the panel reads “below the 30-day lag: reversal buys”. A grey dashed line runs from the low dot across past today’s dot, and the next line reads “above the 40-day lag: momentum buys”. A blue arrow beside today’s dot points up, and a blue line reads “both buy: long”. The right panel mirrors it. Its black line falls from a high dot to a low one and rises a little to a dot between them, labelled, in that order, “40 days ago”, “30 days ago” and “today”, under “the join’s first short, 2008-07-18”. A grey dashed line from the low dot comes with “above the 30-day lag: reversal shorts”, and one from the high dot with “below the 40-day lag: momentum shorts”. A vermilion arrow beside today’s dot points down, and a vermilion line reads “both short: short”. Last, a short grey flat line at the bottom is labelled “any other day: flat”. The finished drawing holds for twelve seconds.](../docs/figures/cl_reversal_momentum_sketch_dip_and_bounce.gif)

*The left panel is the join’s first long, on 2008-07-30, and the right its first short, on 2008-07-18, which is also its first position. Both days come from the 2012-05-04 save. The sketch is schematic. Its heights keep only the order of each day’s three closes, and its spacing across does not follow the days between them. On 2008-07-30 the close of 174.35 sat below its 30-day lag of 182.73 and above its 40-day lag of 173.07. On 2008-07-18 the close of 177.05 sat above its 30-day lag of 176.55 and below its 40-day lag of 181.93.*

The script’s fourth rule, which it names “ComboOR”, scores a long on any day the close is below its 30-day lag or above its 40-day lag. It scores a short on any day the close is above its 30-day lag or below its 40-day lag. Its position each day is the long and the short added together, so a day that scores both is flat. Lesson 2 shows that ComboOR takes the join’s position on every row but ten early ones.

### The daily return, the APR and the Sharpe ratio

Each rule’s return on a day is the position it held at the previous close times that day’s percentage change in price, with no trading cost. Two figures summarise each run. Both count every row, including the days with no position.

- **The APR**, the annual percentage rate, is the return compounded to a year of 252 trading days. Over n daily returns r it is `prod(1 + r)^(252/n) − 1`, where prod multiplies together the 1 + r of every day. [The post on Chan’s reversal rule for stocks](https://github.com/l3a0/quantitative-trading/blob/main/blog/khandani-lo-reversal-lessons.md#lesson-1-every-return-and-sharpe-ratio-chan-prints-reproduces-on-his-own-file) explains compounding.
- **The Sharpe ratio** is the average daily return divided by its standard deviation, then scaled to a year by multiplying by √252. The standard deviation, which this post calls the swing, is the typical size of a day’s move away from that average. So the Sharpe ratio measures return per unit of swing, with nothing taken off for a risk-free rate, the return on cash.

### The prices and the three saves

A futures contract expires, so CL’s long history is a continuous future, stitched from one contract after the next. At each switch, called a roll, the older history is shifted by the difference between the two contracts’ prices so the series has no jump. [The post on volatility against the stock index](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains the stitching.

The shift means CL’s early closes sit well above the price that traded. The book’s window opens at 175.48 on 2008-05-19, a day the contract nearest delivery closed at 127.05. That day is two months before crude oil’s 2008 peak, which Chan dates elsewhere in the book to July 14, 2008, as [the post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#why-test-the-reason-a-strategy-failed) recounts. A percentage return divides each day’s dollar move by that shifted price. A later save can shift the same day’s close by a different amount, as Lesson 1 shows, so the figures depend on which save a run reads, not only on the rule.

This replication reads three of Chan’s saves.

1. **The 2012-05-04 save**, the one `CL_rev.m` loads. CL holds 1,000 rows, from 2008-05-19 to 2012-05-04.
2. **The 2012-05-11 save**, read over the same 1,000 days.
3. **The 2012-05-07 save**, whose CL closes equal the first save’s on all 1,000 of the book’s days. Its 998 earlier rows, from 2004-05-24 to 2008-05-16, extend the same series backward.

## Lesson 1: both figures land, and a save a week later prints the same to the book’s precision

Here is the join on the 2012-05-04 and 2012-05-11 saves, beside the script’s comment and the book.

```math
\small\begin{array}{l|r|r}
\text{Source} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{2012-05-04 save} & 0.117600 & 1.100368 \\
\text{Script comment} & 0.117600 & 1.100368 \\
\text{Book} & \text{12 percent} & 1.1 \\
\text{2012-05-11 save} & 0.117226 & 1.100045
\end{array}
```

On the save the script loads, both figures land on every digit of its comment, and both round to the book’s figures. The 2012-05-07 save gives the same two figures to six decimals, since its closes on those days are the same.

The 2012-05-11 save is different. Its closes sit 0.27 higher on every one of the 1,000 days. The rule compares closes with closes, so a uniform shift changes no position. What it changes is the price that divides each dollar move. A slightly larger divisor makes every return slightly smaller in size, and the APR falls to 0.117226 and the Sharpe ratio to 1.100045. Both still round to 12 percent and 1.1, so the book’s rounding cannot tell the two saves apart. The script’s comment matches the 2012-05-04 save, and nothing shows whether the book’s rounded figures came from that same run.

That is a mild case. [In the volatility post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run), the APR fell by more than half between two of Chan’s saves whose names are ten days apart. A continuous future is rewritten at every roll. So when a backtest replays a rule on past prices, the save is part of what it specifies, even when, as here, the change stays below the book’s printed digits.

## Lesson 2: the join is half of each rule, so it wins by swinging less

On the book’s window, each rule alone scores below the join on both the APR and the Sharpe ratio.

```math
\small\begin{array}{l|r|r|r}
\text{Figure} & \text{The join} & \begin{array}{r}\text{Momentum}\\\text{alone}\end{array} & \begin{array}{r}\text{Reversal}\\\text{alone}\end{array} \\ \hline
\begin{array}{l}\text{Average}\\\text{daily return}\end{array} & 0.000463 & 0.000519 & 0.000440 \\
\begin{array}{l}\text{Standard}\\\text{deviation}\end{array} & 0.006687 & 0.018748 & 0.018864 \\
\text{APR} & 0.117600 & 0.090228 & 0.068326 \\
\begin{array}{l}\text{Sharpe}\\\text{ratio}\end{array} & 1.100368 & 0.439049 & 0.370289
\end{array}
```

The table bears out Chan’s claim that the combination may work better than each rule by itself, at least on this window. The book prints no figure for either rule alone, so nothing here checks the figures for momentum alone and reversal alone against it. Momentum alone earns more than the join on an average day, yet scores lower on both the APR and the Sharpe ratio.

The reason is that the join is almost exactly half of each rule. Hold half a position in reversal alone and half in momentum alone.

1. **Where the two agree**, both halves point the same way and add to one full position. Those are exactly the days the join holds that position.
2. **Where they disagree**, a half long and a half short add to nothing, and on each of those days the join is flat.

So half of each rule gives the join’s position on every row but ten. Those ten, from 2008-07-01 to 2008-07-15, come early in the run, when the 30-day lag exists and the 40-day lag does not yet, so reversal alone holds a position and the join cannot. A position earns on the next day’s move. So on every day except the day after each of those ten rows, the join’s daily return is the average of the two rules’ daily returns.

The two rules mostly disagree. Of the 960 rows where both lags exist, they agree on 157 and take opposite sides on 803. On the day after each of those 803 rows, one rule’s gain is the other’s loss, and the average is zero. The join holds a position on 157 of the 1,000 rows, long on 98 and short on 59. It is flat on the other 843, which are the 803 rows where the rules take opposite sides and the first 40 rows, before the 40-day lag exists.

![An animated whiteboard sketch titled “Half of each rule is the join”, drawn slowly stroke by stroke. Its counts come from the run. Four grey boxes form a two-by-two grid, with columns headed “reversal: long” and “reversal: short” and rows headed “momentum: long” and “momentum: short”. Each box holds two vertical arrows, reversal’s on the left and momentum’s on the right, each labelled “½”, blue and pointing up for a long, vermilion and pointing down for a short, with their sum written beneath. Top left, two blue up arrows, labelled “½” and “½”, sum to “½ + ½ = long”, in blue, beside “98 days”. Top right, a vermilion down arrow labelled “½” and a blue up arrow labelled “½” sum to “−½ + ½ = flat”, in grey. Bottom left, a blue up arrow labelled “½” and a vermilion down arrow labelled “½” sum to “½ − ½ = flat”, in grey. Bottom right, two vermilion down arrows, labelled “½” and “½”, sum to “−½ − ½ = short”, in vermilion, beside “59 days”. In the gap between the columns, one grey arrow points up to the top right box and one down to the bottom left box, from a grey note that reads “803 days: flat”. Last, a line beneath the grid reads “on these 960 days, the join holds the average of the two rules’ positions”. The finished drawing holds for twelve seconds.](../docs/figures/cl_reversal_momentum_sketch_half_of_each.gif)

*Counted over the 960 rows of the 2012-05-04 save where both lags exist. In each box the left arrow is half of reversal’s position and the right arrow half of momentum’s.*

The join’s average day, 0.000463, sits between reversal’s 0.000440 and momentum’s 0.000519. It sits slightly below the plain average of the two, because on those ten early days reversal alone held shorts that made money on balance, while the join held nothing. Cancelling 803 days of opposite bets gives a standard deviation of 0.006687, a little over a third of either rule’s. The Sharpe ratio divides the average day by the standard deviation, so the join wins it easily.

### What the swings cost

Smaller swings give the join the highest APR of the three as well as the highest Sharpe ratio, because compounding charges for swings. A day that loses 2 percent followed by one that gains 2 percent leaves 0.98 × 1.02 = 0.9996 of the capital, a small loss from two moves that cancel in the average. Larger swings lose more to this, and the two rules alone swing hard. The sketch below measures what the swings took from each rule’s average day, and the chart after it shows where those swings carried each rule’s capital.

![An animated whiteboard sketch titled “What the swings take from an average day”, drawn slowly stroke by stroke. Its figures come from the run. Three upright bars stand side by side, drawn to one scale, each as tall as its rule’s average day. Each bar’s lower part is a pale tint with a blue edge, and its upper part is solid vermilion. The left bar comes first, with “the join” written beneath it. Beside its lower part a blue label reads “kept 0.000441”. Its vermilion part is only a thin strip at the top, and beside it a vermilion label reads “lost to swings 0.000022”. The middle bar, the tallest, is named “momentum alone”, with “kept 0.000343” beside its lower part and “lost to swings 0.000176” beside a vermilion part about half as tall as the lower part. The right bar is named “reversal alone”, with “kept 0.000262” beside its lower part and “lost to swings 0.000178” beside a vermilion part about two thirds as tall as the lower part. Last, a line beneath the bars reads “the join keeps the most of its average day”. The finished drawing holds for twelve seconds.](../docs/figures/cl_reversal_momentum_sketch_swing_cost.gif)

*Over the 1,000 rows of the 2012-05-04 save. Kept is the daily return that would reach the same final capital as the rule if it were earned every day. Compounded over 252 days, it gives the rule’s APR in the table. Lost to swings is the average day minus kept. On each rule, the amount lost to swings comes close to half the square of the standard deviation, so momentum alone and reversal alone, which swing nearly three times as much as the join, lose about eight times as much.*

![Two line charts, one above the other, each plotting the compounded cumulative return of three rules on crude oil: the join in a heavy black line, momentum alone in berry and reversal alone in vermilion. The upper chart covers the book’s window, May 2008 to May 2012. Momentum alone climbs to 117.0 percent by June 11, 2009, then drifts down to end at 40.9 percent. Reversal alone falls to −58.7 percent by February 18, 2009, then climbs back to end at 30.0 percent. The join moves in flat steps, stays within a few percent of zero through 2008, never falls below −4.0 percent, and ends highest of the three at 55.5 percent. The lower chart covers May 2004 to May 2008. Momentum alone wanders between about −7 and 12 percent until late 2007, then climbs to end at 43.0 percent. Reversal alone drifts down to about −29 percent and ends at −23.6 percent. The join sits below zero for most of the period, as low as about −11 percent, and ends at 8.7 percent. The title calls the chart exploratory, and the note says the lower chart’s prices sit far above the traded price.](../docs/figures/cl_reversal_momentum.png)

*The join, momentum alone and reversal alone, compounded daily with no cost, on Chan’s continuous CL, shifted at each roll. Above, the book’s 1,000 rows on the save the script loads. Below, the 998 rows before them on the 2012-05-07 save. `CL_rev.m` plots a fourth curve, ComboOR, which this chart leaves out.*

Momentum alone rose 117.0 percent and then gave back most of that gain, ending at 40.9 percent. Reversal alone fell 58.7 percent before recovering to 30.0 percent. Sitting out the days they disagreed, the join never lost more than 4.0 percent from its start, and finished at 55.5 percent.

Against momentum alone, then, “work better” here means a smoother ride rather than a larger average day.

### Swapped lags and ComboOR

How the join reads its two lags explains two more results.

1. **Swapping the lags, a change tried here, reverses the rule.** With reversal on the 40-day lag and momentum on the 30-day lag, a buy needs the close below the 40-day lag and above the 30-day lag, which is the original’s short condition. Every long becomes a short. The Sharpe ratio flips sign exactly, to −1.100368, and the APR becomes −0.115294, not quite the negative of 0.117600 because compounding is not symmetric. Which lag carries which rule decides the sign of every position. [The post on crude oil’s calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md#lesson-2-the-trade-bets-the-spread-moves-further-from-its-average) found another of Chan’s crude oil scripts whose trade bets the opposite way from what its comments describe, so a rule’s sign is worth checking by running it rather than by reading it.
2. **ComboOR adds no evidence.** On the book’s window no close equals its 30-day or 40-day lag exactly, so wherever both lags exist, a close that is not below a lag is above it. On those rows, ComboOR’s buy conditions decide its position. Where both buy conditions hold, neither short condition does, so it holds one long. Where neither buy condition holds, both short conditions do, so it holds one short. Where exactly one buy condition holds, the short condition on the other lag holds too, so it scores a long and a short, which add to nothing. On the first 30 rows neither lag exists, and it holds nothing, as the join does. So it matches the join everywhere except the same ten early rows, where it trades reversal alone. Its APR of 0.125917 and Sharpe ratio of 1.123042 differ from the join’s only through those ten rows.

## Lesson 3: on the four years before the book’s window, the losing half drags the join below momentum alone

The 2012-05-07 save holds the same series back to 2004-05-24. Its 998 rows before the book’s window rank the three rules differently.

```math
\small\begin{array}{l|r|r|r}
\text{Figure} & \text{The join} & \begin{array}{r}\text{Momentum}\\\text{alone}\end{array} & \begin{array}{r}\text{Reversal}\\\text{alone}\end{array} \\ \hline
\begin{array}{l}\text{Average}\\\text{daily return}\end{array} & 0.000091 & 0.000406 & -0.000222 \\
\begin{array}{l}\text{Standard}\\\text{deviation}\end{array} & 0.003922 & 0.009765 & 0.009792 \\
\text{APR} & 0.021324 & 0.094589 & -0.065694 \\
\begin{array}{l}\text{Sharpe}\\\text{ratio}\end{array} & 0.369864 & 0.660514 & -0.359464
\end{array}
```

Momentum alone beats the join on both the APR and the Sharpe ratio, and reversal alone loses money.

The arithmetic from Lesson 2 still holds. Half of each rule gives the join’s position on all but 12 of these rows. Ten are again the early rows where only the 30-day lag exists, here from 2004-07-08 to 2004-07-21. The other two, 2005-06-15 and 2007-04-17, are days when the close equals its 40-day lag exactly. On those days momentum alone holds no position, while reversal alone holds one. Of the 958 rows where both lags exist, the two rules agree on 162 and take opposite sides on 794. The other two are those tie days.

So the join is still close to the average of the two rules, and here one of them loses. Its average day is 0.000091, near the plain average of a rule that earns 0.000406 a day and one that loses 0.000222. Cutting the swings no longer rescues it. Its standard deviation is about 40 percent of momentum’s, but its average day is under a quarter of momentum’s, and its Sharpe ratio falls to 0.37 against momentum’s 0.66.

Whether the smaller swings make up for a losing half depends on how much that half loses and how often the two rules cancel. On these four years the smaller swings do not make up for it. Chan wrote “Sometimes”, which allows exactly this. These four years do not contradict the book. They show the advantage is not general.

Two cautions limit what this segment can show.

1. **Its prices are shifted far from what traded.** The series closes at 119.12 on 2004-05-24, while West Texas crude averaged $41.51 over 2004 on the US Energy Information Administration’s spot price series, the price of oil for immediate delivery. Each day’s dollar move is divided by a price far above what traded, so every percentage return comes out smaller in size than what a trader earned. These are the rule’s figures on Chan’s series, not a trader’s.
2. **It is not data set aside before the rule was chosen.** The years before the book were in Chan’s own save, and nothing was written down here before they were read. [The commodity seasonals post](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md#lesson-3-a-trade-chosen-after-looking-at-the-history-is-tested-by-the-years-after-the-book) tested Chan’s trades on the years after the counts his book prints, years his rules were not chosen on. Years before a book are years its author could have looked at.

The result is exploratory. It fits the reading that the join’s advantage on the book’s window needed both rules to make money there. It says nothing about whether either rule would make money next.

## What this replication cannot say

Three questions stay open.

1. **Whether the lags were chosen on this window.** For the crude oil rule, the book names 30 and 40 days and says nothing about how Chan picked them. Earlier in the same chapter, by contrast, Chan measures whether two-year Treasury note futures trend before he trades momentum on them, which [the post on Treasury note momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#why-measure-momentum-before-trading-it) reproduces. A little after the crude oil rule, in the same section, Chan warns about the strategies there that hold positions for long periods. They make few trades on his test data, so their results carry a risk of data snooping, meaning a rule fitted to the history it is then tested on. He adds that “The real test for the strategy is, as always, in true out-of-sample testing” (p. 208). A search over other lag lengths would multiply the chances of a lucky fit. This run tries 30 and 40 days and no other length, and the swap in Lesson 2 only exchanges which rule reads which lag.
2. **What costs would take.** The book charges none and neither does this run. The join changes position 124 times in 1,000 days, and nothing here measures what a cost on each change would take from 12 percent.
3. **What the four years before the book’s window would give on traded prices.** Their figures are on a series shifted far above the price that traded. Chan’s files of single crude oil contracts start with the contract delivering in January 2007, so for most of those four years they lack the contract nearest delivery. One of those files also holds a spot price, the price of oil itself, which is not what a futures position earns.

## What this means for a trader

One habit for each lesson.

1. **Record which file a backtest read.** A continuous future is rewritten at every roll, so the same rule on the same days can print different figures from saves a week apart.
2. **Before trusting a combined rule, compare it with half a position in each of its parts.** If half of each rule gives the combined position, the combination’s average day sits between its parts’, so any advantage over the better part comes from the swing it removes. Read the average day and the standard deviation separately to see which one moved.
3. **Check what each part earns on its own.** A combination averages its parts, so a part that loses money lowers the combination’s average day. Check whether the smoother ride makes up for that, rather than assuming it does.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Pages 207 and 208 cited. The page numbers are the Kindle edition’s and differ from the print edition’s.
2. Chan, E. P. `CL_rev.m`, as published in the [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) repository at commit `e4bc46f`.
3. US Energy Information Administration. [Cushing, OK WTI Spot Price FOB, annual, dollars per barrel](https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=RWTC&f=A).

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cl_reversal_momentum.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cl_reversal_momentum_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cl_reversal_momentum_whiteboard.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cl_reversal_momentum.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cl_reversal_momentum_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cl_reversal_momentum_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-31-crude-oil-reversal-joined-to-momentum-chans-algorithmic-trading) that sets each of Chan’s figures beside what was found here.*
