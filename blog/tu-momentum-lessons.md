# Chan’s TU momentum figures land on a window his script does not run, and the momentum behind them is thin

*Chapter 6 of Algorithmic Trading measures whether two-year Treasury note futures trend before it trades them. On Chan’s own file every figure in his script’s closing comment lands, but only on the full window, which the script leaves commented out. The Hurst exponent misses, and the correlation that picked the rule rests on 69 days.*

## Why measure momentum before trading it

A trend follower bets that a price which rose over some past window keeps rising over the next one. Ernest Chan’s second book, *Algorithmic Trading*, calls that bet time-series momentum and states it as a correlation: “past returns of a price series are positively correlated with future returns” (Chan, 2013, location 2600). Its sibling, cross-sectional momentum, ranks a price against other prices instead of against its own past, and the [post on Chan’s cross-sectional momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md) works through it.

A claim stated as a correlation can be measured before any money is at risk, so Chan measures first. He computes the correlation of past and future returns with its p-value, the chance of a correlation at least that strong if past and future returns were in fact unrelated. Then he says to “find the optimal pair of past and future periods that gives the highest positive correlation” and trade it (Chan, 2013, location 2612). Example 6.1 does that on TU, the two-year Treasury note future.

Chan published the script, `TU_mom.m`. This repository transcribed it line by line and ran it on the same closes. The results fall into three groups.

1. **Every figure in the script’s closing comment lands on the full window.** A figure lands when it matches every digit printed, and misses when it does not. The script’s active line starts in 2009 and lands none of the six. The line that reads every day from 2004 is commented out, and it lands all six.
2. **The Hurst exponent misses.** The book prints 0.44, and the transcription gives 0.433357. The setting that lands it on TU moves Chan’s other series further off.
3. **The momentum is thin.** The pair Chan trades correlates at 0.27 with a p-value of 0.02. That rests on 69 days, and the pair is one of 49 tried on the same closes.

**Every result here is exploratory.** Chan picked the lookback and the hold from a table computed on the 2004 to 2012 closes the rule then trades. The reproduction can say whether his numbers follow from his file and nothing about whether the rule pays today.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the file

TU is a futures contract on a US Treasury note that matures in about two years, traded on the Chicago Mercantile Exchange. A futures contract is an agreement to buy or sell something at a set price on a set future date. A note pays a fixed coupon, so when the yield on new two-year notes falls, the fixed payments of an existing note are worth more and its price rises, and TU’s with it. A rise in TU is a fall in two-year interest rates.

Each contract expires, so a price history that runs for years is stitched from one contract after the next into a continuous future. The [post on VX and ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains that stitching and the roll that joins each contract to the next. Chan’s reason why futures trend at all rests on the roll return, the part of a future’s return that comes from its price drifting toward the spot price as expiry nears. He argues that “the sign of roll returns does not vary very often” and names TU among the futures the explanation fits (Chan, 2013, location 2683).

### The correlation table

The table starts from one cell, a lookback of 250 days and a hold of 25. On each day the past return is the change in TU’s close over the previous 250 days, and the future return is the change over the next 25. Each day that has both gives one pair of numbers. The cell is the correlation of the past returns with the future returns across those days. A positive value says a rise over the last 250 days tended to be followed by a rise over the next 25.

Neighbouring days share almost all of their windows. Two consecutive future returns overlap on 24 of their 25 days, so counting both treats one move as two pieces of evidence. Chan warns that “we must take care not to use overlapping data” (Chan, 2013, location 2623), and his Figure 6.1 draws the fix as two pairs of bars. When the lookback is longer than the hold, the next pair of returns starts one hold later. When the hold is longer, it starts one lookback later. So the script keeps the first day that has both returns and then every day one shorter period later. For 250 and 25 it keeps every 25th day, and 69 days survive.

The table repeats that for every pairing of 1, 5, 10, 25, 60, 120 and 250 days, seven lookbacks against seven holds, which makes 49 cells. In what follows, 250/25 means a lookback of 250 days and a hold of 25.

### The rule

Chan takes the rule from a paper he cites as “Moskowitz, Yao, and Pedersen”, published as Moskowitz, Ooi and Pedersen (2012): buy a future whose 12-month return is positive, sell one whose return is negative, and hold for a month. Example 6.1 counts the year as 250 trading days and the month as 25, and changes one detail. It decides every day, “each day investing only one twenty-fifth of the total capital” (Chan, 2013, location 2659).

So each day opens a tranche, a slice of one twenty-fifth of the capital, long if TU’s close is above its close 250 days earlier and short if below. Each tranche is held for 25 days, so up to 25 are open at once. Counted in tranches, the position runs from −25, all short, to 25, all long. A day’s return is yesterday’s position times today’s percentage change in the close, divided by 25. The first 250 days have no 250-day return, so the rule holds nothing until 2005-06-01 and earns its first return on 2005-06-02.

### The six figures

The script’s closing lines print six figures from the daily returns.

1. **The average annual return**, the mean daily return times 252, the number of trading days in a year.
2. **The Sharpe ratio**, the mean daily return divided by its standard deviation, times √252. It measures return per unit of risk, here with no risk-free rate taken off.
3. **The APR**, the annual percentage rate. It compounds the daily returns into one growth factor and annualizes it over 252 days a year.
4. **The maximum drawdown**, the deepest fall of the cumulative return below its previous high.
5. **The longest drawdown**, the most days the cumulative return spent below a previous high.
6. **The Kelly f**, the leverage at which capital grows fastest if returns follow a bell curve, which is the mean daily return divided by its variance. The [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives it.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_20120511.mat`, saved on 2012-05-12 and converted here to one file per future. TU’s column holds 2,000 daily closes of the continuous future, from 2004-06-01 to 2012-05-11, the window the book names. This repository transcribed `TU_mom.m` from `ericnberwick/EpchanPreview` at commit `e4bc46f`, a public copy of Chan’s code.

## Lesson 1: the book’s figures come from the full window, not the line the script runs

The script picks its window with `idx = find(tday == 20090102)`, so its figures read the days from 2009-01-02 on. The line under it, `% idx=1;`, would read every day from the first. The `%` makes it a comment, which MATLAB skips. The book’s own sentence names the full window: “From June 1, 2004, to May 11, 2012, the Sharpe ratio is a respectable 1” (Chan, 2013, location 2668).

Here is each figure on both windows, beside the script’s closing comment and the book. The full window is all 2,000 days. The active line is the 849 days from 2009-01-02.

```math
\begin{array}{l|r|r|r|r}
\text{Figure} & \text{Full window} & \text{Active line} & \text{Script's comment} & \text{Book} \\ \hline
\text{Average annual return} & 0.016699 & 0.014042 & 0.0167 & \text{none} \\
\text{Sharpe ratio} & 1.041462 & 1.187438 & 1.04 & 1 \\
\text{APR} & 0.016708 & 0.014069 & 0.0167 & 1.7\text{ percent} \\
\text{Maximum drawdown} & -0.024847 & -0.009851 & -0.024847 & 2.5\text{ percent} \\
\text{Longest drawdown, days} & 343 & 164 & 343 & \text{none} \\
\text{Kelly f} & 64.919535 & 100.298107 & 64.919535 & \text{none}
\end{array}
```

Every full-window figure lands every digit the comment prints and the book’s rounder figure beside it. The maximum drawdown is 2.484746 percent, which rounds to the book’s 2.5. Every figure on the active line misses the comment. The comment also prints no annual volatility, although the script’s printing line asks for one, so the comment came from an earlier version of that line.

The figure below redraws the script’s plot of the cumulative return, the product of one plus each daily return, less 1, over all 2,000 days. TU’s closes sit above it on the same dates.

![Two charts stacked on one shared date axis from June 2004 to May 2012. The top chart shows TU’s 2,000 daily closes. They start at 97.9219 on 2004-06-01 and drift down until mid-2007, then climb steeply through 2008 with a dip in its second quarter, and keep rising to a high of 110.3125 on 2011-09-19, marked with a dot, before ending at 110.2734 on 2012-05-11. The bottom chart shows the momentum rule’s cumulative return as one green line. It is flat at zero until 2005-06-02, while the rule waits for its first 250-day return, dips just below zero later in 2005, and wanders a little above zero until late 2007. Then it climbs steeply. A shaded band marks its maximum drawdown, from a high on 2008-03-17 to a low on 2008-06-13. A dashed vertical line at 2009-01-02 marks where the script’s active line starts, with the curve at 0.085439 there. The curve flattens through most of 2009, then rises steadily to its highest point, 0.140951 on 2011-09-19, marked with a dot, and ends at 0.140547. The title calls the redraw exploratory.](../docs/figures/tu_momentum.png)

*TU’s closes and the momentum rule’s cumulative return on the full window, with the maximum drawdown shaded and the start of the script’s active line marked. The bottom panel redraws the script’s plot, which the book prints as its Figure 6.2, “Equity Curve of TU Momentum Strategy” (Chan, 2013, location 2668). Nothing compares this redraw with the book’s image, so it is a redraw of the script’s plot rather than a checked copy.*

The curve shows why the two windows disagree. It stands at 0.085439 on 2009-01-02 and ends at 0.140547, so the active line starts after more than half of the gain was already in. It also starts after the maximum drawdown, which runs from 2008-03-17 to 2008-06-13. The active line sees a smaller gain and a shallower fall, and every figure moves.

A second file settles which save the book used. Chan’s `correlationTest.m` computes the table alone and loads a later save, from 2012-05-17. TU’s close is the same on all 1,996 days the two saves share. The later save’s 2,000 days start on 2004-06-07, four trading days later, and that shift alone moves the 250/25 correlation to 0.287046, which rounds to 0.29 rather than the book’s 0.27. It moves the Kelly f to 64.930941, off the comment’s digits. So the book’s figures come from the 2012-05-11 save. That four days at the start move a correlation in its second decimal is a first sign of how few days stand behind it.

## Lesson 2: the Hurst exponent misses, and no setting lands both of Chan’s series

Chapter 2 of the book introduced the Hurst exponent and the variance ratio test as tests for mean reversion, and location 2620 says they “can just as well be used as momentum tests” (Chan, 2013, location 2620). The [post on Chan’s stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md#the-tests-and-the-file) explains both. In short, the Hurst exponent H measures how fast a price spreads out over time. A random walk has an H of 0.5, a trending series more, and a reverting series less. On TU the book reports 0.44, a lean toward reversion, which sits against the momentum the table shows.

The script computes H with `genhurst`, a MATLAB function by Tomaso Aste, and this repository transcribed it to Python. On TU’s log closes the transcription gives 0.433357. That prints as 0.43, so it misses the book’s 0.44 with a gap of −0.01, computed minus published. It misses on Chan’s own file, so a later download is not the explanation. The 2012-05-17 save gives 0.446556, which prints as 0.45 and misses on the other side.

`genhurst` has one setting that moves H, `maxT`, the longest gap in days over which it measures changes, 19 by default. Raising `maxT` to 24 lands TU at 0.440450. The same change moves USD.CAD, the other series the book prints an H for, from 0.473233 to 0.471426, further from its printed 0.49. No single setting lands both.

Neither H the book prints lands through the Python copy of `genhurst`, so no figure of Chan’s vouches for it. Two kinds of check test it instead.

1. **Rules on synthetic series.** `TestGenhurst` in the repository’s tests checks that a random walk gives an H near a half, that a reverting series built from the same random shocks gives less, that the level and scale of a series leave H unchanged, and that the window lengths matter.
2. **Pins on real data.** The tests hold TU’s 0.433357 and USD.CAD’s 0.473233 to six decimals. A change to the code fails them. They record what the copy gives without showing that it gives what Chan’s function gave.

A search could go on, through other settings, other versions of the function or other ways of rounding. Each try would be choosing a reading after seeing its number, and a reading chosen that way says nothing about TU. So the replication stopped at the one diagnostic, `maxT`, and recorded the miss.

What survives is the conclusion the figure was printed for. Every reading here, 0.433357, 0.440450 and the later save’s 0.446556, is below a half.

## Lesson 3: the momentum the table shows is thin

Here are all 49 correlations of the table, the lookback down the side and the hold across the top. Bold marks a cell whose p-value is below 0.05.

```math
\begin{array}{r|rrrrrrr}
\text{Lookback} \backslash \text{hold} & 1 & 5 & 10 & 25 & 60 & 120 & 250 \\ \hline
1 & \mathbf{-0.0576} & \mathbf{-0.0755} & -0.0288 & -0.0152 & 0.0293 & 0.0185 & 0.0377 \\
5 & \mathbf{-0.0756} & \mathbf{-0.1271} & -0.0474 & 0.0304 & 0.0784 & 0.0511 & 0.1022 \\
10 & -0.0280 & -0.0485 & 0.0366 & 0.1124 & \mathbf{0.1675} & 0.0848 & \mathbf{0.1686} \\
25 & -0.0140 & 0.0319 & 0.1219 & 0.1955 & \mathbf{0.2333} & 0.1482 & \mathbf{0.2620} \\
60 & 0.0313 & 0.0799 & \mathbf{0.1718} & \mathbf{0.2592} & 0.2162 & -0.0331 & 0.3137 \\
120 & 0.0222 & 0.0565 & 0.0955 & 0.1456 & -0.0192 & 0.2081 & 0.4072 \\
250 & 0.0411 & \mathbf{0.1068} & \mathbf{0.1784} & \mathbf{0.2719} & \mathbf{0.4245} & 0.5112 & 0.4873
\end{array}
```

The traded cell, 250/25, is 0.271855 with a p-value of 0.023841, and both land the book’s 0.27 and 0.02. Three things thin it out.

1. **It rests on 69 days.** Keeping every 25th day stops the future returns from overlapping. The past returns still overlap, since each kept one shares 225 of its 250 days with the next.
2. **It is one of 49.** Fourteen of the 49 cells have a p-value below 0.05. Ten of them are positive. The four negative ones are exactly the shortest pairs, 1/1, 1/5, 5/1 and 5/5, where a rise over one or five days tended to be followed by a fall over the next one or five. If the cells were 49 independent tests of returns with no pattern at all, about 2.45 would fall below 0.05 by chance. They are not independent. Every cell reads the same 2,000 closes and neighbouring cells share most of their windows, so 14 against 2.45 tests nothing. The same goes for the traded cell, whose p-value is not corrected for the other 48. Of the six pairs location 2646 calls “some of the best compromises”, all correlate positively and five have a p-value below 0.05. The exception is 250/120, at 0.0617 on 14 days.
3. **The variance ratio test does not reject a random walk.** For a random walk, changes over two days have twice the variance of changes over one day, and the test asks whether TU’s ratio departs from that by more than chance. On 1,998 daily changes in TU’s log close its p-value is 0.126860, so it cannot tell TU from a random walk.

Location 2646 reconciles the table with the test by saying that TU “exhibits momentum and mean reversion at different time frames” (Chan, 2013, location 2646), and that the variance ratio test cannot look at particular time frames. The four negative short cells fit that reading. But the reading comes from the same table it explains. A test of it would name the time frames first and then measure them on closes the table never saw.

The trade leans on TU’s direction as well as on the correlation. TU’s close rose from 97.9219 on the first day to 110.2734 on the last. The position was +25, fully long, on 1,176 of the 2,000 days, −25 on 397, and 0 on 251, of which 250 came before the first signal. A rule that is fully long on most days of a rising price earns part of that rise, whatever the correlation says.

The return also leans on one year. Calendar 2008 alone compounds to 0.060565, and the other years together, from the first trade in June 2005 to May 2012, compound to 0.075414. So 2008, the year of the financial crisis, earned about four-fifths as much as the rest of the run combined, and it holds the maximum drawdown too.

**This lesson is exploratory like the others.** The table, the pair and the rule all come from the same closes. The correlation picked the pair, and the pair was then traded on the days that produced the correlation, so nothing here tests whether TU trends.

## What this replication cannot say

Three questions are beyond it.

1. **Whether 250/25 would be chosen without hindsight.** The pair was picked from a table of 49 computed on the 2004 to 2012 closes it then trades, so its p-value is not corrected for the other 48. Example 1.1 of the book runs three hypothesis tests on the same returns, and [Entry 37 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-37-three-hypothesis-tests-on-tu-momentum-chans-algorithmic-trading) is where that significance question is asked.
2. **What computed the book’s 0.44.** One setting lands it on TU and moves USD.CAD further from its 0.49. Searching further would be choosing a reading after seeing its number.
3. **What a trader would earn.** The returns are on the notional value of the contract, about \$200,000 by location 2668, with no transaction cost and no margin. The same location puts the margin at about \$400 and says leverage can boost the 1.7 percent. Leverage would multiply the drawdowns along with it. Nothing here measures what costs or leverage would do.

## What this means for a trader

One habit for each lesson.

1. **Run a published script on every window it names.** A commented-out line can be the one behind the printed figures, and the line that runs can land none of them.
2. **Do not tune an estimator until it lands a figure.** When the setting that lands one series moves another away, record the miss and check whether the conclusion still stands.
3. **Count the cells tried and the days behind the chosen one.** A significant cell picked from 49 that share the same closes is a lead, not a finding, and a rule that is mostly long on a rising price earns part of its return from the rise.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 6.1 and Kindle locations 2600, 2612, 2620, 2623, 2646, 2659, 2668 and 2683.
2. Moskowitz, T. J., Ooi, Y. H., and Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, 104(2), 228–250. The book cites it as “Moskowitz, Yao, and Pedersen”.
3. `TU_mom.m` and `correlationTest.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. The script’s closing comment is the source of its six-decimal figures.
4. Aste, T. `genhurst.m`, the generalized Hurst exponent, MATLAB File Exchange, dated 2013-01-30.

*Not investment advice. Code: [the example](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_momentum.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/tu_momentum_figures.py), with the checks behind [the example’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_momentum.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_tu_momentum_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-33-time-series-momentum-on-tu-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
