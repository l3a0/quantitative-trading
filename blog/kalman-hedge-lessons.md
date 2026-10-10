# A Kalman filter hedge on EWA and EWC: Chan’s figures to the last digit, and a trade made before the filter knew anything

*Chan replaces a rolling regression with a Kalman filter that re-estimates a pair’s hedge every day. On his own file his script gives his figures exactly. It also shorts one fund alone on the first day, before the filter has any estimate, and that one trade is enough to move both figures at the book’s precision.*

## Why replace the rolling window with a filter

A pair trade holds one fund against another in a fixed proportion, and the proportion is usually the slope of a regression of one price on the other. A slope fitted once over years of data cannot follow a relationship that drifts. A slope refitted over the last few weeks can, but it moves in jumps. Each day one old price leaves the window and one new price enters, and if the old one was unusual the slope lurches for no reason in today’s market. Ernest Chan’s second book, *Algorithmic Trading*, calls this “an abrupt and artificial impact on the hedge ratio” (Chan, 2013, location 1633).

Two earlier posts here took the first two roads. [The post on the Johansen test](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) regressed the Canadian fund EWC on the Australian fund EWA once over the whole file. [The post on Example 3.1](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) traded gold against oil with a slope refitted every day over the last 20 days. After Example 3.2 trades the same rolling spread with bands, Chan takes a third road. A Kalman filter moves the slope and the intercept a little every day, by an amount the filter sets for itself, so no window has to be chosen and no day drops out of it.

He applies the filter to EWA and EWC with the script `KF_beta_EWA_EWC.m`. He reports an annual percentage rate, or APR, and a Sharpe ratio, the return per unit of risk, as “a reasonable APR of 26.2 percent and a Sharpe ratio of 2.4” and makes two claims about what the filter estimates (Chan, 2013, location 1726).

1. **The slope** “oscillates around 1”.
2. **The intercept** “increases monotonically with time”.

This repository ran the script’s loop on Chan’s own data file. Both figures land on the digits his script prints. The two claims get no verdict, for a reason Lesson 3 explains, and the measurements behind them teach something about how a trend claim gets decided.

**Every result here is exploratory.** Chan chose the rule and its two constants, and reproducing his figures spends the 2006 to 2012 sample on his choices. The reproduction can say whether his numbers follow from his file. It cannot say whether the filter would hedge these two funds well on data it was not tuned on.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The filter and the file

A Kalman filter is an algorithm that updates its estimate of something it cannot see each time it observes something it can. The book calls that estimate “the expected value of a hidden variable” (Chan, 2013, location 1644). Here the observable is EWC’s close, and the hidden variable is a pair of numbers that link it to EWA’s close (Chan, 2013, location 1658).

1. **The slope**, the number of EWA shares held against one share of EWC. The book calls it the hedge ratio. This post says slope throughout.
2. **The intercept**, the level EWC sits above the slope times EWA. The book uses it “in place of the moving average of the spread” (Chan, 2013, location 1678).

The filter never observes either number. It assumes each is yesterday’s value plus a little noise, and it estimates both from the closes.

In plain terms, each day runs four steps.

1. **Hold a guess.** The filter carries a slope and an intercept from yesterday, and a measure of how unsure it is of them.
2. **Forecast.** Before seeing EWC’s close, it forecasts that close as the intercept plus the slope times EWA’s close. It also says how far off the forecast could be, as a variance.
3. **Measure the miss.** The **forecast error** is EWC’s actual close minus that forecast. The book calls it “the deviation of the spread EWC-EWA from its predicted mean value” (Chan, 2013, location 1726). This post says forecast error.
4. **Update the guess.** The filter moves the slope and intercept toward values that would have explained today’s close. How far it moves is set by the **gain**. The gain is large when the filter is unsure of its guess and small when it is confident. After the move, the filter is a little more confident than before.

Two constants set the filter’s pace.

1. **`delta`** sets how far the slope and intercept are allowed to drift from one day to the next, and Chan sets it to 0.0001. The script calls the slope and intercept together beta. Its comment on `delta` says a value of 1 “gives fastest change in beta”, and a value near 0 “allows no change (like traditional linear regression)”.
2. **`Ve`** sets how much noise the filter expects in a single day’s close, and Chan sets it to 0.001.

The filter therefore gives three things at once, which is the point the book makes at location 1678.

1. **The slope** sets the hedge.
2. **The intercept** takes the place of a moving average.
3. **The forecast’s standard deviation**, the square root of its variance, takes the place of a moving standard deviation.

A rolling strategy needs a window for each, and the filter needs none.

**The rule.** The trading rule compares the forecast error with a **band** of plus and minus one forecast standard deviation.

1. **A short** enters when the forecast error rises above the upper band, because EWC has closed further above its forecast than the filter expected. It exits when the forecast error falls back below the upper band.
2. **A long** enters when the forecast error falls below the lower band, and exits when it rises back above the lower band.

Each exit sits on its own entry band. That differs from Example 3.2, the band strategy the book trades on gold and oil just before this one. [The post on Bollinger bands](https://github.com/l3a0/quantitative-trading/blob/main/blog/bollinger-band-lessons.md) covers it. There, a position enters one standard deviation from a rolling mean and exits at the mean itself (Chan, 2013, location 1559). Location 1726 says the rest of the Kalman code is the same as that example’s, with the filter’s slope in place of the rolling one.

One long unit is short the slope’s worth of EWA shares and long one share of EWC. A short unit is the reverse. Each day’s return is the profit on yesterday’s positions divided by the gross dollars they held, as in the earlier posts, and no cost is charged. Each trading day is one row of the file, and all 1,500 rows count toward the figures.

**The file** is Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and [converted here](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) to one file per fund. It is the same file the Johansen post read. EWA and EWC are both priced on all 1,500 trading days from 2006-04-26 to 2012-04-09. The script is `KF_beta_EWA_EWC.m` as published with the book’s code, and the replication transcribes its loop line for line rather than using a library’s filter, because the script’s starting point is part of what is being tested.

## Lesson 1: the script’s figures land every digit

Here is each figure as computed, beside the script’s closing comment and the book.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{APR} & 0.26225194 & 0.262252 & 26.2\ \text{percent} \\
\text{Sharpe ratio} & 2.36116164 & 2.361162 & 2.4
\end{array}
```

Both computed figures match the comment at every one of its six decimals. The book’s 26.2 percent and 2.4 are those figures rounded, correctly. The APR is the compounded annual return over 252 trading days a year. The Sharpe ratio is the average daily return over its standard deviation, scaled to a year, with no risk-free rate subtracted.

An exact match on Chan’s file through Chan’s own loop confirms that the code here does what his code does on the same numbers. It is also a narrow result. Lesson 2 shows that matching every digit says nothing about whether every row the script trades makes sense.

The figure below redraws the book’s Figures 3.5 to 3.8 from the run. Like everything here it is exploratory. The constants and the rule were Chan’s, and nothing here tests them on other years.

![Four charts stacked on one shared date axis from April 2006 to April 2012. The first, Figure 3.5, plots the slope in shares of EWA per share of EWC. A red dot marks its start at 0 on 2006-04-26. It jumps to about 1.4 on the next day, wanders between about 1.05 and 1.5 until late 2008, drops to about 1 in late 2008, and stays between about 0.86 and 1.19 from 2009, ending near 0.9. A dashed line marks 1. The heading gives a median of 1.047367, a mean of 1.089693, and 894 of 1,500 days above 1. The second, Figure 3.6, plots the intercept in dollars, which rises from 0 to about 2.9 by September 2008, climbs steeply to about 5.8 by the end of 2008, and creeps up to about 6.8 by 2012. Thick brass steps mark each calendar year’s mean, each one higher than the last. A red dot marks the highest value, 6.803488 on 2011-09-08. The heading says the yearly mean falls on 0 of 6 steps and the daily intercept falls on 513 of 1,499 steps. The third, Figure 3.7, plots the forecast error from 2006-04-28 on, mostly between about −0.9 and 0.9 dollars with spikes past 1 in either direction from late 2006 to late 2008, around brass lines at plus and minus one forecast standard deviation of about 0.09 to 0.3. A red note says the first two days sit off the axis at 22.95, EWC’s whole close, and 22.78, and that the script trades on both. The fourth, Figure 3.8, plots the cumulative compounded return of the script, solid, and of the run with no signal on the first two days, dashed green. The two lines nearly coincide, rising to about 300 percent by 2012. The legend gives an APR of 0.262252 and a Sharpe ratio of 2.361162 for the script, and 0.260669 and 2.349460 for the dashed run. The title calls the figure exploratory, and the note names Chan’s file and says every figure is in-sample.](../docs/figures/kalman_hedge.png)

*The slope, the intercept with its yearly means, the forecast error inside its band, and the cumulative return, on Chan’s file over its 1,500 days, the forecast error from the third.*

## Lesson 2: the script trades before the filter has learned anything

The script starts the slope and intercept at 0, and it starts the filter’s uncertainty at 0 too. On the file’s first day that start decides the trade.

**Row 1, 2006-04-26.** The filter has not yet updated anything, so the slope and intercept are both 0. Its forecast of EWC is therefore 0 plus 0 times EWA, which is 0. The forecast error is EWC’s whole close of 22.95. The filter’s uncertainty is also 0, so its gain is 0 and the update leaves the slope and intercept at 0. With no uncertainty, the forecast variance is just `Ve`, and the band is its square root, 0.031623.

An error of 22.95 against a band of 0.031623 is far above the upper band, so the rule enters a short. A short unit holds the slope’s worth of EWA against one share of EWC. With the slope at 0, the EWA side holds no dollars. So on its first day the strategy shorts EWC alone, with no hedge at all.

**Row 2, 2006-04-27.** The filter’s uncertainty now has its first day of drift added, so the gain is no longer 0, and the update moves the slope from 0 to 1.366666. That is exactly the value the filter’s equations give when worked by hand from a zero start. The forecast of EWC, though, is made before the update, from row 1’s slope and intercept of 0. So the forecast is again 0, and the forecast error is EWC’s whole close of 22.78, against a band of 0.163213. The short stays on.

**What that trade earns.** The first nonzero return falls on 2006-04-27. It is the short on EWC alone, held as EWC fell from 22.95 to 22.78. That is a gain of 0.0074074, or 0.74 percent in a day, on a position the filter had no basis for. From row 3 on, the slope has moved off 0 and the forecasts mean something.

**The figures without it.** One way to remove the trade is to give the rule no signal on rows 1 and 2, and leave everything else alone. That run holds exactly the same units as the script from row 3 on. The whole difference between the two is the returns of 2006-04-27 and 2006-04-28, the two days on which the positions taken on rows 1 and 2 earn their returns. The table sets that run beside the script, and beside a second reading that also drops the two rows from the returns.

```math
\begin{array}{l|r|r}
\text{Run} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{The script} & 0.26225194 & 2.36116164 \\
\text{No signal on rows 1 and 2, all 1,500 rows} & 0.26066891 & 2.34946035 \\
\text{No signal on rows 1 and 2, the two rows dropped} & 0.26105886 & 2.35106158
\end{array}
```

This post quotes the middle run, which annualises all 1,500 days as the script does. Its figures round to 26.1 percent and 2.3, not the book’s 26.2 and 2.4. One position, held over two days out of 1,500, moves both figures at the precision the book prints. The last run is a different reading, and it is shown so the two cannot be confused.

**The script’s own chart leaves both rows out.** The script plots the forecast error as `e(3:end)` and its standard deviation as `sqrt(Q(3:end))`, so its chart of the forecast error starts on row 3. The figure above does the same and names the two missing values in a note. The two rows the chart leaves out are the two the strategy trades on before its filter has an estimate.

A filter needs a starting guess, and a start at 0 is wrong on day one. Withholding the signal for the first days removes the trade, as the middle run above does for the first two. Starting from a regression would need data from before the file’s first day, which this file does not hold. The script gives a reader of the backtest no warning of that first trade.

## Lesson 3: the grain decides “monotonically”

Location 1726 says the slope “oscillates around 1” and the intercept “increases monotonically with time”. Neither claim comes with a number or a test. To judge either, a reader has to choose what would count. [The replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-32-a-kalman-filter-hedge-ratio-on-ewa-and-ewc-chans-algorithmic-trading) records how that went here. This repository wrote its only criteria for the two claims after a first run had measured them, so neither claim gets a verdict. This lesson reports what the measurements show, and what they show is how much a choice made after seeing the data can decide.

**The intercept.** Whether a series rises “monotonically” depends on how closely it is looked at. Call that the **grain**: the length of the period averaged before each average is compared with the one before it. A day, a month, a quarter, a year and a rolling window of 250 days are all grains. At each one, the question is how many steps go down.

The yearly means of the intercept rise every year.

```math
\begin{array}{l|r|r|r|r|r|r|r}
\text{Year} & 2006 & 2007 & 2008 & 2009 & 2010 & 2011 & 2012 \\ \hline
\text{Mean intercept} & 0.1440 & 0.6336 & 2.5795 & 5.6350 & 6.0380 & 6.5851 & 6.7748
\end{array}
```

At every finer grain, some steps fall.

```math
\begin{array}{l|r|r}
\text{Grain} & \text{Steps} & \text{Steps that fall} \\ \hline
\text{Year} & 6 & 0 \\
\text{Quarter} & 24 & 3 \\
\text{Month} & 72 & 9 \\
\text{Rolling 250-day mean} & 1{,}250 & 57 \\
\text{Day} & 1{,}499 & 513
\end{array}
```

The intercept also peaks at 6.803488 on 2011-09-08, above its last value of 6.767360 on the file’s final day. So it ends lower than it has been.

A reader who picks the yearly grain says the claim holds. A reader who picks the daily grain says it fails, on 513 of 1,499 steps. Both picks are defensible, and both can be made after looking at the chart, which is the problem. The figure’s second panel shows the two grains at once. Its brass steps never go down. The line beneath them goes down often.

**The slope.** “Around 1” has the same trouble with a different dial. The slope’s median is 1.047367 and its mean is 1.089693. At one decimal the median rounds to 1.0 and the mean to 1.1. The median sits 0.002633 below 1.05, the threshold where it too would round to 1.1. The slope sits above 1 on 894 of the 1,500 days, 59.6 percent of them. It crosses 1 a total of 54 times. One of those is row 2, where it jumps from its zero start to 1.366666, so 53 crossings remain once that step is set aside.

So “around 1” holds or fails depending on whether the median or the mean is read, at what precision, and whether more than half the days on one side counts as oscillating. Each of those is a reasonable choice. The replication wrote none of them down before it saw the numbers.

**What to do instead.** Write the grain and the threshold before running anything. For the intercept, that means naming the period to average and how many falls are allowed. For the slope, it means naming the statistic, the precision and how many crossings count. For the APR and the Sharpe ratio, Chan’s printed digits fixed the test before any run. For these two claims nothing did, and that is why they carry findings rather than verdicts.

The single regression over the whole file in the Johansen post found a slope of 0.9624 and an intercept of 6.4113. The filter’s intercept starts at 0 and ends at 6.767360, not far from that level. Lesson 2 showed the zero start deciding a trade. Here it may be deciding a trend, and the section on what this replication cannot say returns to it.

## Lesson 4: an exact reproduction checks the arithmetic, not the edge

Matching Chan’s figures to the digit says the code is right. It says nothing about whether the strategy would have worked for someone who did not already know how these six years went, for three reasons.

1. **The constants are Chan’s.** `delta` is 0.0001 and `Ve` is 0.001. The passages of the book recorded here give no reason for either value, and the script’s comment on `delta` describes the range from no change to fastest change, which invites tuning it. Nothing here tunes either constant. They are taken as given, and that makes every figure in-sample, measured on the same years Chan reported them from with no data held back.
2. **The rule trades often, and pays nothing to do so.** Over the 1,500 days the script holds a long on 358, a short on 350 and nothing on 792. Its units change from one day to the next 875 times. Every change is a trade in two funds, and on the days between, the EWA side is resized to each day’s slope. The script charges nothing for either kind of trade. A cost per trade would come straight off the APR, and nothing here measures how much.
3. **The sample is one stretch of history.** A filter that adapts as it goes still adapts only to the six years it is run on, and those are the years its figures are measured on.

The result is exploratory however closely it matches. It shows that Chan’s numbers follow from his file and his script. A test that could say more would fix `delta`, `Ve` and a cost per trade in writing, then run the filter on EWA and EWC after April 2012.

## What this replication cannot say

Four questions are beyond it.

1. **What other values of `delta` or `Ve` give.** Trying several values and keeping the best is a search, and a search needs its own guard against finding something by luck. Nothing here runs one.
2. **What the filter gives as a market-making model.** Location 1760 describes a second use of the filter, estimating the mean price of a single asset, and it prints no figure and names no script.
3. **Anything about costs.** The band changes the position whenever the forecast error crosses it, and the script charges nothing for those trades.
4. **Whether the intercept’s rise belongs to the market or to the zero start.** The filter starts the intercept at 0. The single regression over the whole file puts it at 6.4113. A filter started from that value might show no rise at all. Nothing here starts the filter anywhere else, so the question stays open.

## What this means for a trader

One habit for each lesson.

1. **Match the printed figure before trusting the rule behind it.** A reproduction to the last digit confirms the code, and every later question starts from there.
2. **Check what a filter does before it has seen any data.** An adaptive estimate starts somewhere, and a backtest that trades from its first row trades on that start.
3. **Fix the grain and the threshold before reading a trend claim.** “Monotonically” and “around 1” have no answer until the period and the threshold are chosen, and choosing them after the chart decides the answer.
4. **Treat constants someone else chose as in-sample.** A rule with two tuning constants set on the same years it is tested on has been fitted to those years, whoever did the fitting.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 1559, 1633, 1644, 1658, 1678, 1726 and 1760.
2. Chan, E. P. `KF_beta_EWA_EWC.m`, git blob `e2f8a62` under `public/img/book2/`, and `fillMissingData.m`, the book’s code, as published at commit `e4bc46f` of [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview).

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kalman_hedge.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kalman_hedge_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kalman_hedge.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kalman_hedge_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-32-a-kalman-filter-hedge-ratio-on-ewa-and-ewc-chans-algorithmic-trading) that sets each of Chan’s claims beside what was found here.*
