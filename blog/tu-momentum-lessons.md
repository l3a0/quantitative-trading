# Chan’s TU momentum figures land on a window his script does not run, and the momentum behind them is thin

*Chapter 6 of Algorithmic Trading measures whether two-year Treasury note futures trend before it trades them. On Chan’s own file every figure in his script’s closing comment lands, but only on the full window, whose line the script leaves commented out. The Hurst exponent misses, and the correlation that picked the rule’s periods rests on 69 days.*

## Why measure momentum before trading it

A trend follower bets that a price which rose over some past window keeps rising over the next one. Ernest Chan’s second book, *Algorithmic Trading*, calls that bet time-series momentum and states it as a correlation: “past returns of a price series are positively correlated with future returns” (Chan, 2013, location 2600). Its sibling, cross-sectional momentum, ranks a price against other prices instead of against its own past, and the [post on Chan’s cross-sectional momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md) works through it.

A claim stated as a correlation can be measured before any money is at risk, so Chan measures first. He computes the correlation of past and future returns with its p-value, the chance of a correlation at least that strong if past and future returns were in fact unrelated. Then he says to “find the optimal pair of past and future periods that gives the highest positive correlation” and trade it (Chan, 2013, location 2612). Example 6.1 computes those correlations for TU, the two-year Treasury note future, and trades one of the pairs.

### What the reproduction found

Chan published the script, `TU_mom.m`. This repository transcribed it line by line and ran it on Chan’s own closes. The results fall into three groups.

1. **Every figure in the script’s closing comment lands on the full window.** The comment at the end of the script lists six figures. A figure lands when it matches every digit printed, and misses when it does not. The script has two lines that set the first day of the returns behind the six figures. The one it runs starts in 2009 and lands none of the six. The one below it starts in 2004 and reads every day, the full window, but it is commented out, so the script skips it. That line lands all six.
2. **The Hurst exponent misses.** The Hurst exponent measures whether a price tends to trend or to revert. The book prints 0.44, and the transcription gives 0.433357. Changing a setting of the function that computes it lands it on TU, but moves USD.CAD, the other series the book prints a Hurst exponent for, further off.
3. **The momentum is thin.** Chan trades one pair of periods, looking back 250 days and holding for 25. Of the pairs in his table of correlations, he names it among the best compromises between a strong correlation and a small p-value, though several pairs correlate more strongly. The pair correlates at 0.27 with a p-value of 0.02. The correlation rests on 69 days, and the pair is one of 49 tried on the same closes.

**Every result here is exploratory**, meaning it can kill an idea or justify a closer look but cannot confirm one. Chan picked the pair from a table computed on the 2004 to 2012 closes the rule then trades, so the closes that picked the pair are the closes that test it. The reproduction can say whether his numbers follow from his file and nothing about whether the rule pays today.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the file

TU is a futures contract on a US Treasury note that matures in about two years. It is listed on the Chicago Board of Trade, which has been part of CME Group since 2007. A futures contract is an agreement to buy or sell something at a set price on a set future date. A note pays a fixed coupon, so when the yield on new two-year notes falls, the fixed payments of an existing note are worth more and its price rises, and TU’s with it. So a rise in the note’s price reflects a fall in two-year interest rates.

Each contract expires, so a price history that runs for years is stitched from one contract after the next into a continuous future. The [post on VX and ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains that stitching and the roll, the switch from an expiring contract to the next. The roll return is the part of a future’s return that comes from its price drifting toward the spot price, the price of the underlying notes for delivery today, as expiry nears. The series here is back-adjusted, which means the prices before each roll are shifted so the series has no jump there. The shift leaves each contract’s own day-to-day changes alone, its drift toward the spot price included, so the series’ rises carry the roll return as well as moves in yields.

### Why TU might trend

Chan names four main causes of momentum (Chan, 2013, location 2591).

1. For futures, “the persistence of roll returns, especially of their signs”.
2. The slow spread, analysis and acceptance of new information.
3. Forced buying and selling of assets by funds of various kinds.
4. Manipulation of the market by high-frequency traders.

The first is the one Chan applies to TU. He argues that “the sign of roll returns does not vary very often” and names TU among the futures the explanation fits (Chan, 2013, location 2683). The [post on Chan’s spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md) splits the returns of five futures, TU among them, into roll return and spot return, as Chan’s Table 5.1 does, and checks that table on his own files. The spot return is the part that comes from the spot price’s own moves.

### The correlation table

The table starts from one cell, a lookback of 250 days and a hold of 25. On each day the past return is the percentage change in TU’s close over the previous 250 days, and the future return is the percentage change over the next 25. Each day that has both gives one pair of numbers. The cell is the correlation of the past returns with the future returns across those days. A positive value says a rise over the last 250 days tended to be followed by a rise over the next 25.

Neighbouring days share almost all of their windows. Two consecutive future returns overlap on 24 of their 25 days, so counting both treats one move as two pieces of evidence. Chan warns that “we must take care not to use overlapping data” (Chan, 2013, location 2623), and his Figure 6.1 draws the fix as two pairs of bars. When the lookback is longer than the hold, the next pair of returns starts one hold later. When the hold is longer, it starts one lookback later. So the script keeps the first day that has both returns, then steps forward by whichever of the two periods is shorter. For 250 and 25 it keeps every 25th day, and 69 days survive. The past returns still overlap, by 225 of their 250 days from one kept day to the next.

![A whiteboard sketch titled “Future returns end to end, past returns overlap”, drawn slowly. A grey line under where the bars go is labelled “trading days, to scale”. Above it, a long brass bar labelled “past 250 days” ends where a black bar one tenth as long, labelled “future 25 days”, begins, and the pair is labelled “first kept day, 2005-06-01”. A second pair below starts one hold to the right. Its black bar begins exactly where the first black bar ends, with a dashed grey join between the two, and it is labelled “2005-07-07, one hold later”. A grey bracket between the two brass bars runs from where the second starts to where the first ends and is labelled “225 of 250 days shared”. A third pair, one more hold to the right with its black bar again starting where the second ends, is labelled “2005-08-11, two holds later”. Under the axis, a row of black dots is labelled “69 kept days, every 25th, dots not to scale”, and the sketch closes with “future returns: no overlap” in black on the left and “past returns: still overlap” in brass on the right. The finished drawing holds for twelve seconds.](../docs/figures/tu_momentum_sketch_futures_tile.gif)

The table repeats that calculation for every pairing of 1, 5, 10, 25, 60, 120 and 250 days, seven lookbacks against seven holds, which makes 49 cells. In what follows, 250/25 means a lookback of 250 days and a hold of 25.

### The rule

Chan picks 250/25 from the table and then looks for a rule to trade it. He takes the rule from a paper by Moskowitz, Ooi and Pedersen (2012), which he cites as “Moskowitz, Yao, and Pedersen”. The rule buys a future whose 12-month return is positive, sells one whose return is negative, and holds for a month. Example 6.1 sets the rule’s year at 250 trading days and its month at 25, and changes one detail. It decides every day, “each day investing only one twenty-fifth of the total capital” (Chan, 2013, location 2659).

So each day opens a tranche, a slice of one twenty-fifth of the capital, long if TU’s close is above its close 250 days earlier and short if below. Each tranche is held for 25 days, so up to 25 are open at once. Counted in tranches, the position runs from −25, all short, to 25, all long. A day’s return is yesterday’s position times today’s percentage change in the close, divided by 25. The first 250 days have no 250-day return, so the rule holds nothing until 2005-06-01 and earns its first return on 2005-06-02.

### The six figures

The script’s closing comment records six figures from the daily returns.

1. **The average annual return**, the mean daily return times 252, the number of trading days a year the script uses to annualize.
2. **The Sharpe ratio**, the mean daily return divided by its standard deviation, times √252. It measures return per unit of risk, here with no risk-free rate taken off.
3. **The APR**, the annual percentage rate. It compounds the daily returns into one growth factor and annualizes it over 252 days a year.
4. **The maximum drawdown**, the deepest fall of the account’s value below its previous high, as a fraction of that high. The account’s value is the product of one plus each daily return, and the cumulative return is that value less 1.
5. **The longest drawdown**, the most days the cumulative return spent below a previous high.
6. **The Kelly f**, the mean daily return divided by its variance. It is the leverage at which capital grows fastest if returns follow a bell curve. The [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives it.

### The prices and the script

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_20120511.mat`, saved on 2012-05-12 and converted here to one file per future. TU’s column holds 2,000 daily closes of the continuous future, from 2004-06-01 to 2012-05-11, the window the book names. This repository transcribed `TU_mom.m` from `ericnberwick/EpchanPreview` at commit `e4bc46f`, a public copy of Chan’s code.

## Lesson 1: the book’s figures come from the full window, not the line the script runs

The script picks its window with `idx=find(tday==20090102);`, so its figures read the days from 2009-01-02 on. The line under it, `% idx=1;`, would read every day from the first. The `%` makes it a comment, which MATLAB skips. The book’s own sentence names the full window: “From June 1, 2004, to May 11, 2012, the Sharpe ratio is a respectable 1” (Chan, 2013, location 2668).

Here is each figure in two tables, each with a row for the full window, the active line, the script’s closing comment and the book. The full window is all 2,000 days. The active line, the one the script runs, reads the 849 days from 2009-01-02. The first table’s columns, Return, Sharpe and APR, are the average annual return, the Sharpe ratio and the APR. The second table’s, Drawdown, Days and Kelly f, are the maximum drawdown, the longest drawdown in days and the Kelly f.

```math
\small\begin{array}{l|r|r|r}
 & \text{Return} & \text{Sharpe} & \text{APR} \\ \hline
\text{Full window} & 0.016699 & 1.041462 & 0.016708 \\
\text{Active line} & 0.014042 & 1.187438 & 0.014069 \\
\text{Comment} & 0.0167 & 1.04 & 0.0167 \\
\text{Book} & \text{none} & 1 & 1.7\text{ percent}
\end{array}
```

```math
\small\begin{array}{l|r|r|r}
 & \text{Drawdown} & \text{Days} & \text{Kelly f} \\ \hline
\text{Full window} & -0.024847 & 343 & 64.919535 \\
\text{Active line} & -0.009851 & 164 & 100.298107 \\
\text{Comment} & -0.024847 & 343 & 64.919535 \\
\text{Book} & 2.5\text{ percent} & \text{none} & \text{none}
\end{array}
```

Every full-window figure lands every digit the comment prints, and the book’s rounder figure where the book prints one. The maximum drawdown of −0.024847 is a fall of 2.484746 percent, which rounds to the book’s 2.5 percent. Every figure on the active line misses the comment.

The comment also lists no annual volatility, although the script’s printing line asks for one, which suggests the comment was pasted from an earlier version of that line.

### Why the two windows disagree

The figure below redraws the script’s plot of the cumulative return over all 2,000 days, with TU’s closes above it on the same dates.

![Two charts stacked on one shared date axis from June 2004 to May 2012. The top chart shows TU’s 2,000 daily closes. They start at 97.9219 on 2004-06-01, rise through late 2004 and drift down until mid-2007, then climb steeply through 2008 with a dip in its second quarter, and keep rising to a high of 110.3125 on 2011-09-19, marked with a dot, before ending at 110.2734 on 2012-05-11. The bottom chart shows the momentum rule’s cumulative return as one green line. It is flat at zero until 2005-06-02, while the rule waits for its first 250-day return, dips just below zero later in 2005, and stays near zero until late 2007. Then it climbs steeply. A shaded band marks its maximum drawdown, from a high on 2008-03-17 to a low on 2008-06-13. A dashed vertical line at 2009-01-02 marks where the script’s active line starts, with the curve at 0.085439 there. The curve flattens through the first half of 2009, then rises steadily to its highest point, 0.140951 on 2011-09-19, marked with a dot, and ends at 0.140547. The title calls the redraw exploratory.](../docs/figures/tu_momentum.png)

*TU’s closes and the momentum rule’s cumulative return on the full window, with the maximum drawdown shaded and the start of the script’s active line marked. The bottom panel redraws the script’s plot, which the book prints as its Figure 6.2, “Equity Curve of TU Momentum Strategy” (Chan, 2013, location 2668). Nothing compares this redraw with the book’s image, so it is a redraw of the script’s plot rather than a checked copy.*

The curve stands at 0.085439 on 2009-01-02 and ends at 0.140547, so the active line starts after more than half of the gain was already in. The active line also starts after the maximum drawdown, which runs from 2008-03-17 to 2008-06-13. The active line sees a smaller gain and a shallower fall, and every figure moves. The standard deviation of its daily returns shrinks by more than their mean does, so its Sharpe ratio and Kelly f come out higher.

### Chan’s later data file

A second data file of Chan’s settles which file the book used. His `correlationTest.m` computes only the correlation table, and it loads `inputDataOHLCDaily_20120517.mat`, whose closes run to 2012-05-17. TU’s close is the same on all 1,996 days the two files share. The later file’s 2,000 days start on 2004-06-07, four trading days later, so the days the 250/25 cell keeps, every 25th one, start four trading days later too, on 2005-06-07 rather than 2005-06-01. Each file gives the cell 69 days, and no day appears in both sets.

The four-day shift alone moves the 250/25 correlation to 0.287046, which rounds to 0.29 rather than the book’s 0.27. Run over the whole later file, which also ends four trading days later, `TU_mom.m` gives a Kelly f of 64.930941, off the comment’s digits. So the book’s figures come from the file whose closes end on 2012-05-11. Four days at the start move the correlation in its second decimal, a first sign of how few days stand behind it.

![A whiteboard sketch titled “Same closes, no kept day shared”, drawn slowly. A black line with four upright ticks, one for each of the first four days the 250/25 cell keeps, is labelled “file ending 2012-05-11”, with “2005-06-01” over its first tick. Below it, a brass line with four ticks is labelled “file ending 2012-05-17”, with “2005-06-07” under its first tick. Each brass tick sits a short way right of a black tick and far short of the next one, so no brass tick lines up with a black one. Dashed grey links join each black tick to the brass tick after it and are labelled “each 4 trading days later”, and a grey note reads “first 4 kept days of each”. Four lines close it: “1,996 closes in both files, every one equal”, “69 kept days in each, none shared”, “250/25 correlation: 0.2719 on the earlier, 0.2870 on the later” and “at the book’s two decimals: 0.27 against 0.29”. The finished drawing holds for twelve seconds.](../docs/figures/tu_momentum_sketch_no_shared_day.gif)

## Lesson 2: the Hurst exponent misses, and no `maxT` lands both of Chan’s series

Chapter 2 of the book introduced the Hurst exponent and the variance ratio test as tests for mean reversion, a price’s pull back toward its average. Chan says they “can just as well be used as momentum tests” (Chan, 2013, location 2620). The [post on Chan’s stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md#the-tests-and-the-file) explains both. In short, the Hurst exponent H measures how fast a price spreads out over time. A random walk has an H of 0.5, a trending series more, and a reverting series less. The variance ratio test, which Lesson 3 returns to, asks whether a price’s changes spread out as fast as a random walk’s. On TU the book reports an H of 0.44, a lean toward reversion, which sits against the momentum the correlation table shows.

The script computes H with `genhurst`, a MATLAB function by Tomaso Aste, and this repository transcribed it to Python. On TU’s log closes the transcription gives 0.433357. That prints as 0.43, so it misses the book’s 0.44 with a gap of −0.01, computed minus published. It misses on Chan’s own file, so the gap does not come from a vendor revising the prices after Chan saved them. Chan’s later file, whose closes run to 2012-05-17, gives 0.446556, which prints as 0.45 and misses on the other side.

`genhurst` takes two settings.

1. `q`, the power the function raises each change’s size to before averaging. The script passes it as 2.
2. `maxT`, the longest gap in days over which it measures changes. The script leaves it at its default of 19.

Raising `maxT` to 24 lands TU at 0.440450. The same change moves USD.CAD, the other series the book prints an H for, from 0.473233 to 0.471426, further from its printed 0.49. No value of `maxT` from 5 to 40 lands both.

At the settings Chan’s scripts use, the Python copy of `genhurst` lands neither H the book prints, so no figure of Chan’s confirms the copy. Two kinds of check test it instead.

1. **Expected behaviour on synthetic series.** `TestGenhurst` in the repository’s tests checks that a random walk gives an H near 0.5, that a reverting series built from the same random shocks gives less, that the level and scale of a series leave H unchanged, and that changing `maxT` changes H.
2. **Recorded values on real data.** The tests hold TU’s 0.433357 and USD.CAD’s 0.473233 to six decimals. A change to the code fails them. They record what the copy gives without showing that it gives what Chan’s function gave.

A search could go on, through other settings, other versions of the function or other ways of rounding. Each try would pick a way of computing H after seeing the H it gives, and an H chosen that way says nothing about TU. So the replication stopped after trying one setting, `maxT`, and recorded the miss.

Every H here, 0.433357, 0.440450 and the later file’s 0.446556, sits below 0.5, on the same side as the book’s 0.44. Each is a point estimate with no standard error, though, and the variance ratio test in Lesson 3 cannot tell TU from a random walk. So the miss does not overturn the book’s lean toward reversion, and it does not make that lean a finding either.

## Lesson 3: the momentum the table shows is thin

Here are all 49 correlations of the table in two parts, holds of 1 to 25 days and then holds of 60 to 250 days. In each part the lookback runs down the side and the hold across the top. Bold marks a cell whose p-value is below 0.05.

```math
\small\begin{array}{r|rrrr}
 & 1 & 5 & 10 & 25 \\ \hline
1 & \mathbf{-0.0576} & \mathbf{-0.0755} & -0.0288 & -0.0152 \\
5 & \mathbf{-0.0756} & \mathbf{-0.1271} & -0.0474 & 0.0304 \\
10 & -0.0280 & -0.0485 & 0.0366 & 0.1124 \\
25 & -0.0140 & 0.0319 & 0.1219 & 0.1955 \\
60 & 0.0313 & 0.0799 & \mathbf{0.1718} & \mathbf{0.2592} \\
120 & 0.0222 & 0.0565 & 0.0955 & 0.1456 \\
250 & 0.0411 & \mathbf{0.1068} & \mathbf{0.1784} & \mathbf{0.2719}
\end{array}
```

```math
\small\begin{array}{r|rrr}
 & 60 & 120 & 250 \\ \hline
1 & 0.0293 & 0.0185 & 0.0377 \\
5 & 0.0784 & 0.0511 & 0.1022 \\
10 & \mathbf{0.1675} & 0.0848 & \mathbf{0.1686} \\
25 & \mathbf{0.2333} & 0.1482 & \mathbf{0.2620} \\
60 & 0.2162 & -0.0331 & 0.3137 \\
120 & -0.0192 & 0.2081 & 0.4072 \\
250 & \mathbf{0.4245} & 0.5112 & 0.4873
\end{array}
```

The traded cell, 250/25, is 0.271855 with a p-value of 0.023841, and both land the book’s 0.27 and 0.02. Three things thin it out.

1. **It rests on 69 days.** Keeping every 25th day stops the future returns from overlapping. The past returns still overlap, since each kept one shares 225 of its 250 days with the next.
2. **It is one of 49.** Fourteen of the 49 cells have a p-value below 0.05. Ten of them are positive. The four negative ones are exactly the shortest pairs, 1/1, 1/5, 5/1 and 5/5, where a rise over one or five days tended to be followed by a fall over the next one or five. If the cells were 49 independent tests of returns with no pattern at all, chance alone would put 2.45 of them below 0.05 on average. They are not independent. Every cell reads the same 2,000 closes, and neighbouring cells share a lookback or a hold, so their returns overlap. So comparing 14 with 2.45 is not a valid test. A pair of two long periods keeps few days, so a strong correlation there can still have a large p-value. Chan weighs a strong correlation against a small p-value, and calls six pairs “some of the best compromises” (Chan, 2013, location 2646): 60/10, 60/25, 250/10, 250/25, 250/60 and 250/120. All six correlate positively and five have a p-value below 0.05. The exception is 250/120, whose p-value is 0.0617 on 14 days.
3. **The variance ratio test does not reject a random walk.** For a random walk, changes over two days have twice the variance of changes over one day. The test asks whether TU’s two-day variance departs from twice its one-day variance by more than chance. It uses 1,998 of the 1,999 daily changes in TU’s log close, because it keeps a whole number of two-day periods. Its p-value is 0.126860, so it cannot tell TU from a random walk.

Chan reconciles the table with the test by saying that TU “exhibits momentum and mean reversion at different time frames” (Chan, 2013, location 2646), and that the variance ratio test cannot look at particular time frames. The four negative short cells fit that reading. But the reading comes from the same table it explains. A test of it would name the time frames first and then measure them on closes the table never saw.

### TU’s rise and the year 2008

The trade leans on TU’s direction as well as on the 250/25 correlation. TU’s close rose from 97.9219 on the first day to 110.2734 on the last. The position was +25, fully long, on 1,176 of the 2,000 days and −25 on 397. It was between −25 and +25 but not 0 on 176 days, and 0 on the other 251, of which 250 came before the first signal. A rule that is fully long on most days of a rising price earns part of that rise, whatever the correlation says.

Example 1.1 of the book runs three hypothesis tests on this rule’s daily returns. The [post on those three tests](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-hypothesis-tests-lessons.md#lesson-5-two-checks-added-afterwards-point-at-drift-not-kurtosis) reports two checks its replication added after a trial run. They point at this upward drift as what drives the result of the second of those tests, the one that reruns the rule on simulated prices. They point away from fat tails, meaning rare large days.

The return also leans on one year. Calendar 2008 alone compounds to 0.060565, and the other years together, from the first trade in June 2005 to May 2012, compound to 0.075414. So 2008, the year of the financial crisis, earned about four-fifths as much as the rest of the run combined, and it holds the maximum drawdown too.

**This lesson is exploratory like the others.** The correlation picked the pair, and the pair was then traded on the days that produced the correlation. Nothing here tests whether TU trends at 250/25 on closes the table never saw.

## What this replication cannot say

Three questions are beyond this replication.

1. **Whether 250/25 would be chosen without hindsight.** The pair was picked from a table of 49 computed on the 2004 to 2012 closes it then trades, so its p-value is not corrected for the other 48. [Entry 37 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-37-three-hypothesis-tests-on-tu-momentum-chans-algorithmic-trading) is where that significance question is asked, through Example 1.1’s three tests, and the [post on those three tests](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-hypothesis-tests-lessons.md) works through it.
2. **What computed the book’s 0.44.** A setting tried after the miss lands it on TU and moves USD.CAD further from its 0.49, and Lesson 2 says why the search stopped there.
3. **What a trader would earn.** The returns are measured against the notional value of the contract, the face value of the notes it controls, about \$200,000 (Chan, 2013, location 2668), rather than against the margin, the deposit a broker holds against each contract. They take off no transaction cost. Chan puts the margin at about \$400 and says leverage can boost the book’s APR of 1.7 percent. Leverage would multiply the drawdowns along with it. Nothing here measures what costs or leverage would do.

## What this means for a trader

One habit for each lesson.

1. **Run a published script on every window it names.** A commented-out line can be the one behind the printed figures, and the line that runs can land none of them.
2. **Do not tune an estimator until it lands a figure.** When the setting that lands one series moves another away, record the miss and check whether the conclusion still stands.
3. **Count the cells tried and the days behind the chosen one.** A significant cell picked from 49 that share the same closes is a lead, not a finding, and a rule that is mostly long on a rising price earns part of its return from the rise.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 6.1 and Kindle locations 2591, 2600, 2612, 2620, 2623, 2646, 2659, 2668 and 2683.
2. Moskowitz, T. J., Ooi, Y. H., and Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. The book cites it as “Moskowitz, Yao, and Pedersen”.
3. `TU_mom.m` and `correlationTest.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. The script’s closing comment is the source of its six-decimal figures.
4. Aste, T. `genhurst.m`, the generalized Hurst exponent, MATLAB File Exchange, dated 2013-01-30.

*Not investment advice. Code: [the example](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_momentum.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_momentum_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_momentum_whiteboard.py), with the checks behind [the example’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_momentum.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_momentum_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_momentum_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-33-time-series-momentum-on-tu-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
