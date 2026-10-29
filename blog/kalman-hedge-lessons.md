# A Kalman filter hedge on EWA and EWC: Chan’s figures to the last digit, and a trade made before the filter knew anything

*Chan replaces a rolling regression with a Kalman filter that re-estimates a pair’s hedge every day. On his own file his script gives his figures exactly. It also shorts one fund alone on the first day, before the filter has any estimate. That one trade changes the APR as the book rounds it, and the Sharpe ratio too when all 1,500 trading days count, as they do in the script.*

## Why replace the rolling window with a filter

A pair trade holds one fund against another in a fixed proportion, and the proportion is usually the slope of a regression of one price on the other. A slope fitted once over years of data cannot follow a relationship that drifts. A slope refitted over the last few weeks can, but it moves in jumps. Each day one old price leaves the window and one new price enters, and if the old one was unusual the slope lurches for no reason in today’s market. Ernest Chan’s second book, *Algorithmic Trading*, calls this “an abrupt and artificial impact on the hedge ratio” (Chan, 2013, Kindle edition, p. 119).

Two earlier posts here took the first two roads. [The post on the Johansen test](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) regressed the Canadian fund EWC on the Australian fund EWA once over the whole file. [The post on the book’s Example 3.1](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) traded gold against oil with a slope refitted every day over the last 20 days. The book’s next example, Example 3.2, trades the same rolling spread with bands one standard deviation either side of its rolling mean. Chan then takes a third road. A Kalman filter moves the slope and the intercept a little every day, by an amount the filter sets for itself, so no window has to be chosen and no day drops out of it.

He applies the filter to EWA and EWC with the script `KF_beta_EWA_EWC.m`. He reports an annual percentage rate, or APR, and a Sharpe ratio, the return per unit of risk, as “a reasonable APR of 26.2 percent and a Sharpe ratio of 2.4” and makes two claims about what the filter estimates (Chan, 2013, pp. 125 to 128).

1. **The slope** “oscillates around 1”.
2. **The intercept** “increases monotonically with time”.

### What the reproduction found

This repository ran the script’s loop on Chan’s own data file. Both figures land on the digits written in the comment that closes his script. The two claims get no verdict, for a reason Lesson 3 explains. The measurements behind them still teach something about how a trend claim gets decided.

**Every result here is exploratory.** Chan chose the trading rule and the two constants that set the filter’s pace, and his figures come from the same 2006 to 2012 closes this reproduction reruns. So those years cannot also serve as a fresh test of his choices. The reproduction can say whether his numbers follow from his file. It cannot say whether the filter would hedge these two funds well on data it was not tuned on.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The filter and the file

A Kalman filter is an algorithm that updates its estimate of something it cannot see each time it observes something it can. The book calls that estimate “the expected value of a hidden variable” (Chan, 2013, p. 119). Here the observable is EWC’s close, and the hidden variable is a pair of numbers that link it to EWA’s close (Chan, 2013, p. 120).

1. **The slope**, the number of EWA shares held against one share of EWC. The book calls it the hedge ratio. This post says slope throughout.
2. **The intercept**, the level EWC sits above the slope times EWA. The spread here is EWC’s close minus the slope times EWA’s close. The book uses the intercept “in place of the moving average of the spread” (Chan, 2013, p. 121).

The filter never observes either number. It assumes each is yesterday’s value plus a little noise, and it estimates both from the closes.

### How the filter updates its guess

In plain terms, each day runs four steps.

1. **Hold a guess.** The filter carries a slope and an intercept from yesterday, and a measure of how unsure it is of them.
2. **Forecast.** Before seeing EWC’s close, it forecasts that close as the intercept plus the slope times EWA’s close. It also says how far off the forecast could be, as a variance.
3. **Measure the miss.** The **forecast error** is EWC’s actual close minus that forecast. The book calls it “the deviation of the spread EWC-EWA from its predicted mean value” (Chan, 2013, p. 127). This post says forecast error.
4. **Update the guess.** The filter moves the slope and intercept toward values that would have explained today’s close. How far it moves is set by the **gain**. The gain is large when the filter is unsure of its guess and small when it is confident.

After the first day, the filter never becomes confident on this file. On the first day it is certain of a guess of 0, for a reason Lesson 2 explains. Each update leaves it surer. But each new day it allows for the slope and intercept to have drifted since yesterday. On a typical day that drift takes back all the certainty the update added. So the gain stays large. The updated slope and intercept, applied to the day’s EWA close, would have forecast EWC’s close almost exactly, closing 98 percent of the miss on a median day. The slope still moves only a little each day, about 0.009 on a median day. A change in the slope moves the updated forecast by that change times EWA’s close, so a small change is enough to close a miss of a fraction of a dollar.

![An animated whiteboard sketch titled “One day of the filter”, drawn slowly stroke by stroke. Grey axes come first, labelled “EWA close” across and “EWC close” up. They are zoomed around 2007-05-15, each axis on its own scale, and every mark is drawn to scale on them. A black line, yesterday’s slope and intercept, crosses the plot, and a numbered list of steps down the left side, each in its mark’s colour, starts with “1 hold”. Past the line’s right end its label reads “yesterday: slope 1.127974,” and “intercept 0.471207”. A grey tick on the axis is labelled “EWA 23.31”, and a thick grey tick on the black line above it is the forecast, with the list’s “2 forecast” and the label “forecast 26.76”. Two brass hairlines above and below the forecast, one forecast standard deviation either way, are labelled “band ±0.24”. A black dot higher up is EWC’s close, labelled “close 27.15”, and a red bar from the forecast up to the dot is the miss, with the list’s “3 miss” and the label “error 0.39”. Last, a green line, the slope and intercept after the update, appears above the black line. On these narrow axes it looks lifted rather than turned. Its intercept has barely changed. Its slope has risen by 0.016211, and at an EWA close of 23.31 that rise lifts the line by 0.38, so it passes almost through the black dot. The list reads “4 update”, and past the green line’s end its label reads “updated: slope 1.144185,” and “intercept 0.472220”. A line of green words at the bottom reads “slope +0.016211 × EWA 23.31 = +0.38, intercept +0.001013: line to 27.14, 98% of the miss”. The finished drawing holds for twelve seconds.](../docs/figures/kalman_hedge_sketch_one_day.gif)

*One day of the filter, 2007-05-15, on axes zoomed around the day: yesterday’s line forecasts EWC, the brass band spans one forecast standard deviation either way, the close misses the forecast, and a rise in the slope, larger than a median day’s but still small, moves the line almost onto the close.*

### The filter’s constants and outputs

Two constants set the filter’s pace.

1. **`delta`** sets how far the slope and intercept are allowed to drift from one day to the next, and Chan sets it to 0.0001. The script calls the slope and intercept together beta. Its comment on `delta` says a value of 1 “gives fastest change in beta”, and a value near 0 “allows no change (like traditional linear regression)”.
2. **`Ve`** sets how much noise the filter expects in a single day’s close, and Chan sets it to 0.001.

The filter gives three things at once, which is the point the book makes on p. 121.

1. **The slope** sets the hedge.
2. **The intercept** takes the place of a moving average.
3. **The forecast’s standard deviation**, the square root of its variance, takes the place of a moving standard deviation.

A rolling strategy needs a window for each, and the filter needs none.

### The units, the rule and the daily return

The strategy trades the pair in units. One long unit is short a number of EWA shares equal to the slope and long one share of EWC. A short unit is the reverse.

The trading rule compares the forecast error with a **band** of plus and minus one forecast standard deviation.

1. **A short** enters when the forecast error rises above the upper band, because EWC has closed further above its forecast than the filter expected. It exits when the forecast error falls back below the upper band.
2. **A long** enters when the forecast error falls below the lower band, and exits when it rises back above the lower band.

Each exit sits on its own entry band. That differs from Example 3.2, the band strategy the book trades on gold and oil just before this one. The book calls it a Bollinger band strategy, and [the post on Bollinger bands](https://github.com/l3a0/quantitative-trading/blob/main/blog/bollinger-band-lessons.md) covers it. There, a position enters one standard deviation from a rolling mean and exits at the mean itself (Chan, 2013, p. 114).

On p. 128 the book says that once the entry and exit signals are set, the rest of the Kalman code is the same as Example 3.2’s, with the filter’s slope in place of the rolling one.

Each day’s return is the profit on yesterday’s positions divided by the gross dollars they held, as in the earlier posts, and no cost is charged. Each trading day is one row of the file, and all 1,500 rows count toward the figures.

### The prices and the script

The prices come from Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and [converted here](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) to one file per fund. It is the same file the Johansen post read.

The file adjusts its closes for dividends by subtracting each dividend in dollars from every earlier close. This repository checked that method on two other funds in the file, SPY and GDX, and not on EWA or EWC. Where a dividend was subtracted, a close from before it sits below the price the fund traded at that day. A return computed from these closes is not exactly what a holder earned.

EWA and EWC are both priced on all 1,500 trading days from 2006-04-26 to 2012-04-09. The script is `KF_beta_EWA_EWC.m` as published with the book’s code, and the replication transcribes its loop line for line rather than using a library’s filter, because the script’s starting values are part of what is being tested. The script starts the slope, the intercept and the uncertainty at 0.

## Lesson 1: the script’s figures land every digit

The table sets each computed figure against the script’s closing comment and the book.

```math
\small\begin{array}{l|r|r}
\text{Source} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{Computed} & 0.26225194 & 2.36116164 \\
\text{Script's comment} & 0.262252 & 2.361162 \\
\text{Book} & 26.2\ \text{percent} & 2.4
\end{array}
```

Both computed figures match the comment at every one of its six decimals. The book’s 26.2 percent and 2.4 are those figures rounded, correctly. The APR is the compounded annual return over 252 trading days a year. The Sharpe ratio is the average daily return over its standard deviation, scaled to a year, with no risk-free rate subtracted.

An exact match on Chan’s file through Chan’s own loop confirms that the code here does what his code does on the same numbers. It is also a narrow result. Lesson 2 shows that matching every digit says nothing about whether every trade the script makes has a basis.

The figure below redraws the book’s Figures 3.5 to 3.8 from the run. Like everything here it is exploratory. The constants and the rule were Chan’s, and nothing here tests them on other years.

![Four charts stacked on one shared date axis from April 2006 to April 2012. The first, Figure 3.5, plots the slope in shares of EWA per share of EWC. A red dot marks its start at 0 on 2006-04-26. It jumps to about 1.4 on the next day, wanders between about 1.05 and 1.5 until late 2008, drops to about 1 in late 2008, and stays between about 0.86 and 1.19 from 2009, ending near 0.9. A dashed line marks 1. The heading gives a median of 1.047367, a mean of 1.089693, and 894 of 1,500 days above 1. The second, Figure 3.6, plots the intercept in dollars, which rises from 0 to about 2 by the start of September 2008, climbs steeply to about 5.8 by the end of 2008, and creeps up to about 6.8 by 2012. Thick brass steps mark each calendar year’s mean, each one higher than the last. A red dot marks the highest value, 6.803488 on 2011-09-08. The heading says the yearly mean falls on 0 of 6 steps and the daily intercept falls on 513 of 1,499 steps. The third, Figure 3.7, plots the forecast error from 2006-04-28 on, mostly between about −0.9 and 0.9 dollars with spikes past 1 in either direction from late 2006 to late 2008, around brass lines at plus and minus one forecast standard deviation of about 0.09 to 0.3. A red note says the first two days sit off the axis at 22.95, EWC’s whole close, and 22.78, and that the script trades on both. The fourth, Figure 3.8, plots the cumulative compounded return of the script, solid, and of the run with no signal on the first two days, dashed green. The two lines nearly coincide, rising to about 300 percent by 2012. The legend gives an APR of 0.262252 and a Sharpe ratio of 2.361162 for the script, and 0.260669 and 2.349460 for the dashed run. The title calls the figure exploratory, and the note names Chan’s file and says every figure is in-sample.](../docs/figures/kalman_hedge.png)

*The slope, the intercept with its yearly means, the forecast error inside its band, and the cumulative return, on Chan’s file over its 1,500 days, with the forecast error drawn from the third day on.*

## Lesson 2: the script trades before the filter has learned anything

The script starts the slope and intercept at 0, and it starts the filter’s uncertainty at 0 too. An uncertainty of 0 tells the filter that its guess of 0 is exactly right. On the file’s first day that start decides the trade.

**Row 1, 2006-04-26.** The filter has not yet updated anything, so the slope and intercept are both 0. Its forecast of EWC is therefore 0 plus 0 times EWA, which is 0. The forecast error is EWC’s whole close of 22.95. The filter’s uncertainty is also 0, so its gain is 0 and the update leaves the slope and intercept at 0. With no uncertainty, the forecast variance is just `Ve`, and the band is its square root, 0.031623.

An error of 22.95 against a band of 0.031623 is far above the upper band, so the rule enters a short. A short unit is long a number of EWA shares equal to the slope and short one share of EWC. With the slope at 0, the EWA side holds no dollars. So on its first day the strategy shorts EWC alone, with no hedge at all.

**Row 2, 2006-04-27.** The filter’s uncertainty now has its first day of drift added, so the gain is no longer 0, and the update moves the slope from 0 to 1.366666. That is exactly the value the filter’s equations give when worked by hand from a zero start. The forecast of EWC, though, is made before the update, from row 1’s slope and intercept of 0. So the forecast is again 0, and the forecast error is EWC’s whole close of 22.78, against a band of 0.163213. The short stays on. The position is sized after the update, so on row 2 the short unit is long 1.366666 EWA shares and short one EWC share. From row 3 on, each forecast uses a slope that has moved off 0.

**What that trade earns.** The first nonzero return falls on 2006-04-27. It comes from the short on EWC alone, held as EWC fell from 22.95 to 22.78. That is a gain of 0.0074074, or 0.74 percent in a day, on a position the filter had no basis for.

![An animated whiteboard sketch titled “Two rows on a forecast of 0”, drawn slowly stroke by stroke. Three columns, the file’s first three rows, share one dollar scale from 0 to about 23. In each, a grey dot left of a red bar is the forecast, a black dot right of it is EWC’s close, and the red bar between their heights is the forecast error. Two brass hairlines across the bar, above and below the forecast, mark the band, drawn to the same scale. In the first column the grey dot sits at the bottom, “forecast 0”, the black dot at the top, “close 22.95”, and the red bar runs the whole height, “error 22.95”. Its two hairlines merge into one short brass tick at the bottom, labelled “band ±0.031623”, and the column is dated “row 1, 2006-04-26”. Red words under it read “short EWC alone, 0 EWA shares”. The second column repeats the picture with “forecast 0”, “close 22.78”, “error 22.78” and “band ±0.163213”, dated “row 2, 2006-04-27”, and black words under it read “slope 0 → 1.366666,” and “after the forecast”. Green words then appear under the first column, “+0.74% on 2006-04-27”. In the third column the two dots sit near the top a hair apart, and the red bar between them is a few pixels tall. Its labels read “close 22.94”, “error 0.85”, “band ±0.167334” and “forecast 22.09”, top to bottom, it is dated “row 3, 2006-04-28”, and black words under it read “forecast uses” and “slope 1.366666”, the slope row 2’s update left. The finished drawing holds for twelve seconds.](../docs/figures/kalman_hedge_sketch_zero_start.gif)

*The file’s first three rows on one dollar scale: on rows 1 and 2 the forecast is 0, so the error is EWC’s whole close and the band beside it all but vanishes.*

### The figures without the first trade

One way to remove the first day’s short is to give the rule no signal on rows 1 and 2, and leave everything else alone. That run holds exactly the same units as the script from row 3 on. The whole difference between the two is the returns of 2006-04-27 and 2006-04-28, the two days on which the positions taken on rows 1 and 2 earn their returns. The table sets that run beside the script. Below them, the table’s last line gives the same run’s figures with rows 1 and 2 dropped from the returns.

```math
\small\begin{array}{l|r|r}
\text{Run} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{The script} & 0.26225194 & 2.36116164 \\
\begin{array}{l}\text{No signal on} \\ \text{rows 1 and 2,} \\ \text{all 1,500 rows}\end{array} & 0.26066891 & 2.34946035 \\
\begin{array}{l}\text{No signal on} \\ \text{rows 1 and 2,} \\ \text{the two rows} \\ \text{dropped}\end{array} & 0.26105886 & 2.35106158
\end{array}
```

This post quotes the middle run, which annualises all 1,500 days as the script does. Its figures round to 26.1 percent and 2.3, not the book’s 26.2 and 2.4. The Sharpe ratio lands 0.00054 below 2.35, the value at which it would round to the book’s 2.4. Two days out of 1,500 move both figures at the precision the book prints. They are 2006-04-27 and 2006-04-28, the first two of the three days on which the opening short, held on rows 1 to 3, earns a return. That so few days move both figures says more about how close the script’s figures sit to the book’s rounding than about how large the trade is. The script gains on 412 days. On 252 of them, setting that day’s return to 0 also makes the APR round below the book’s 26.2 percent, and on 144 of those it makes the Sharpe ratio round below 2.4 as well.

The table’s last line is there so that a figure computed with rows 1 and 2 dropped is not mistaken for the one this post quotes. The middle run holds nothing on those rows and earns 0 on them, so dropping them changes only how many days the figures average over. Under that reading the APR still rounds to 26.1 percent, but the Sharpe ratio rounds to the book’s 2.4. So without the first trade, the APR rounds below the book’s 26.2 percent whichever way the returns are counted, and the Sharpe ratio rounds below the book’s 2.4 only while all 1,500 days count, as they do in the script.

### What the script’s chart leaves out, and three ways round the zero start

The script plots the forecast error as `e(3:end)` and its standard deviation as `sqrt(Q(3:end))`, so its chart of the forecast error starts on row 3. The third of Lesson 1’s four charts does the same and names the two missing values in a note. The two rows the chart leaves out are the two on which the filter forecasts EWC at 0, and the strategy trades on both.

A filter needs a starting guess, and a start at 0 is wrong on day one. There are three ways round it.

1. **Withhold the signal for the first days.** The middle run above does that for the first two, and it removes the trade.
2. **Start the filter from a regression’s slope and intercept.** In a backtest that regression has to end before the first day traded, or the starting guess would use prices a trader could not yet have seen. This file holds no data from before its first day. So here the regression would have to read the file’s own first days, and the backtest would give up trading on them.
3. **Start the filter unsure of its guess.** A starting uncertainty above 0 gives row 1 a gain above 0, so the update moves the slope off 0 before the first position is sized. A large enough one also widens row 1’s band past the error of 22.95, so row 1 enters no trade. Such a start changes what the filter estimates on every later day too, and nothing in this replication runs it.

The script does none of the three, and it gives a reader of the backtest no warning of that first trade.

## Lesson 3: the grain decides “monotonically”

The book says the slope “oscillates around 1” and the intercept “increases monotonically with time” (pp. 125 to 127). Neither claim comes with a number or a test. To judge either, a reader has to choose what would count. This repository wrote its only criteria for the two claims after a first run had measured them, as [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-32-a-kalman-filter-hedge-ratio-on-ewa-and-ewc-chans-algorithmic-trading) records, so neither claim gets a verdict. This lesson reports what the measurements show, and what they show is how much a choice made after seeing the data can decide the answer.

### The intercept’s rise, year by year and day by day

Whether a series rises “monotonically” depends on how closely it is looked at. Call that the **grain**: the length of the period that is averaged. Each average is then compared with the one before it, and that comparison is a step. A day, a month, a quarter, a year and a rolling window of 250 days are all grains. At each one, the question is how many steps go down.

The yearly means of the intercept rise every year.

```math
\begin{array}{l|r}
\text{Year} & \text{Mean intercept} \\ \hline
2006 & 0.1440 \\
2007 & 0.6336 \\
2008 & 2.5795 \\
2009 & 5.6350 \\
2010 & 6.0380 \\
2011 & 6.5851 \\
2012 & 6.7748
\end{array}
```

At every finer grain, some steps fall.

```math
\small\begin{array}{l|r|r}
\text{Grain} & \text{Steps} & \text{Steps that fall} \\ \hline
\text{Year} & 6 & 0 \\
\text{Quarter} & 24 & 3 \\
\text{Month} & 72 & 9 \\
\text{Rolling 250-day mean} & 1{,}250 & 57 \\
\text{Day} & 1{,}499 & 513
\end{array}
```

The rolling mean shows the grain deciding the answer even when only the window’s length changes. Lengthen the window from 250 days to 300 and the number of falls shrinks from 57 of 1,250 steps to 25 of 1,200. At 350 days, none of the 1,150 steps falls. The window’s length alone decides whether this measure finds any fall, and the claim names no length.

The intercept also peaks at 6.803488 on 2011-09-08, above its last value of 6.767360 on the file’s final day. So it ends below its own peak, which a series that only rises could not do.

A reader who picks the yearly grain says the claim holds. A reader who picks the daily grain says it fails, on 513 of 1,499 steps. Both picks are defensible, and both can be made after looking at the chart. The second of Lesson 1’s four charts shows the two grains at once. Its brass steps never go down. The line beneath them goes down often.

The single regression over the whole file in the Johansen post found a slope of 0.9624 and an intercept of 6.4113. The filter’s intercept starts at 0 and ends at 6.767360, not far from that level. Lesson 2 showed the zero start deciding a trade. Here the same start may be deciding a trend. Part of the rise may be the filter leaving its start of 0 rather than a change in the market. The section on what this replication cannot say returns to the question.

### The slope’s median, mean and crossings

“Around 1” has the same trouble as “monotonically”, with different choices to make. The slope’s median is 1.047367 and its mean is 1.089693. At one decimal the median rounds to 1.0 and the mean to 1.1. The median sits 0.002633 below 1.05, the threshold where it too would round to 1.1. The slope sits above 1 on 894 of the 1,500 days, 59.6 percent of them. It crosses 1 a total of 54 times. One of those is row 2, where it jumps from its zero start to 1.366666, so 53 crossings remain once that step is set aside.

So “around 1” holds or fails depending on whether the median or the mean is read, at what precision, and whether a slope that sits above 1 on 59.6 percent of days still counts as oscillating around 1. Each of those is a reasonable choice. The replication wrote none of them down before it saw the numbers.

### What would settle the two claims

Write the grain and the threshold before running anything. For the intercept, that means naming the period to average and how many falls are allowed. For the slope, it means naming the statistic, the precision and how many crossings count. For the APR and the Sharpe ratio, Chan’s printed digits fixed the test before any run. For these two claims nothing did.

On this file it is too late to do that. Every grain above has already been measured here, and so have the slope’s median, mean and crossings. A criterion written now would be chosen knowing its answer. Testing such a criterion would need closes from outside the file’s six years, such as those after April 2012.

## Lesson 4: an exact reproduction checks the arithmetic, not the edge

Matching Chan’s figures to the digit says the code here does what his code does. It says nothing about whether the strategy would have worked for someone who did not already know how these six years went, for three reasons.

1. **The constants are Chan’s.** `delta` is 0.0001 and `Ve` is 0.001. None of the book’s passages recorded in this repository’s notes gives a reason for either value. The script’s comment on `delta` describes the range from no change to fastest change, which invites tuning it. Nothing here tunes either constant. They are taken as given, and that makes every figure in-sample, measured on the same years Chan reported them from with no data held back.
2. **The rule trades often, and pays nothing to do so.** Over the 1,500 days the script holds a long on 358, a short on 350 and nothing on 792. Its units change from one day to the next 875 times. Every change is a trade in two funds, and on the days between, the EWA side is resized to each day’s slope. The script charges nothing for either kind of trade. A cost per trade would come straight off the APR, and nothing here measures how much.
3. **The sample is one stretch of history.** A filter that adapts as it goes still adapts only to the six years it is run on, and those are the years its figures are measured on.

The result is exploratory however closely it matches. It shows that Chan’s numbers follow from his file and his script. A test that could say more would fix in writing `delta`, `Ve`, the filter’s starting guess and its starting uncertainty, how many of the first days give no signal, a cost per trade, and the result after costs that counts as a pass. It would then run the filter on EWA and EWC after April 2012.

## What this replication cannot say

Four questions are beyond it.

1. **What other values of `delta` or `Ve` give.** Trying several values and keeping the best is a search, and a search needs its own guard against finding something by luck. Nothing here runs one.
2. **What the filter gives as a market-making model.** On pp. 129 to 131 the book describes a second use of the filter, estimating the mean price of a single asset. The book calls this “a favorite model for market makers”, a point it credits to Euan Sinclair. It prints no figure and names no script.
3. **Anything about costs.** The band changes the position whenever the forecast error crosses it, and the script charges nothing for those trades.
4. **Whether the intercept’s rise belongs to the market or to the zero start.** The filter starts the intercept at 0. The single regression over the whole file puts it at 6.4113. A filter started from that value would show how much of the rise the zero start explains. It would not be a backtest, because that regression reads every day of the file. Nothing here starts the filter anywhere else, so the question stays open.

## What this means for a trader

One habit for each lesson.

1. **Match the printed figure before trusting the rule behind it.** A reproduction to the last digit confirms that the code does what the original does, and every later question starts from there.
2. **Check what a filter does before it has seen any data.** An adaptive estimate starts somewhere, and a backtest that trades from its first row trades on that start.
3. **Fix the grain and the threshold before reading a trend claim.** “Monotonically” and “around 1” have no answer until the period and the threshold are chosen, and choosing them after seeing the chart decides the answer.
4. **Treat constants someone else chose as in-sample.** A rule with two tuning constants set on the same years it is tested on has been fitted to those years, whoever did the fitting.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Pages 114, 119 to 121 and 125 to 131 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. Chan, E. P. `KF_beta_EWA_EWC.m`, git blob `e2f8a62`, `fillMissingData.m`, git blob `88632fc`, and the data file `inputData_ETF.mat`, git blob `261718b`, all under `public/img/book2/` at commit `e4bc46f` of [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview), a public copy of Chan’s code and data.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kalman_hedge.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kalman_hedge_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/kalman_hedge_whiteboard.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kalman_hedge.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kalman_hedge_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_kalman_hedge_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every sentence quoted from the book with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-32-a-kalman-filter-hedge-ratio-on-ewa-and-ewc-chans-algorithmic-trading) that sets each of Chan’s claims beside what was found here.*
