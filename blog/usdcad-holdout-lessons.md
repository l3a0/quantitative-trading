# Trading USD.CAD’s mean reversion for fourteen years after Chan’s sample

*On fourteen years of closes kept back from every decision, Chan’s trade still ends positive, by too little to tell from chance.*

## Why trade the rule on later closes

Ernest Chan’s *Algorithmic Trading* tests USD.CAD, the price of a US dollar in Canadian dollars, for mean reversion, a pull back toward its average. He then trades it with what this post calls the linear rule. The rule holds a position equal to minus the close’s z-score. That is the number of standard deviations the close sits from its moving average, with the average and the standard deviation both taken over the same window of recent closes, the latest one included. So the rule sells as the close rises above its average and buys as it falls below. A z-score of 2 means a short position worth 2, one that gains when the price falls.

Chan reports one result in words: the profit and loss, or P&L, “manages to be positive, albeit with a large drawdown” (Chan, 2013, p. 49). A drawdown is a fall in the P&L from its running high.

The [post on Chan’s USD.CAD tests](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) reproduced that claim on his own 1,216 closes, from 2007-07-23 to 2012-03-28, and could say nothing more. Two things kept every figure there exploratory, able to justify a closer look but not to confirm anything.

1. **Chan had already looked at those days.** He chose them and printed their numbers, so reproducing them checks the arithmetic and not the rule.
2. **The lookback is a look-ahead.** The rule’s moving average and deviation look back 115 days. That is the half-life of the same closes it trades, meaning how long a distance from the average takes to halve if the series is pulled back toward it. A trader in 2008 could not have known the half-life of a series that runs to 2012.

This post removes both. It keeps the lookback at 115, fixed from Chan’s closes and never re-estimated, and trades only closes after his sample ends: 3,791 days from 2012-03-29 to 2026-10-12. The rule is the same function the earlier post ran, and that post explains the mean-reversion tests and the rule in full. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

**The verdict is registered, and the unpredicted figures are exploratory.** A **holdout** is data kept back from every decision about a test, so a result on it is a fresh check. A written plan set out six predictions about this holdout, each with its test and pass mark. A registered result is one whose test and pass mark the plan wrote down before the run computed anything on its data. Lesson 2 lists the six, and what had been read before the run.

The first prediction is Chan’s claim, and its outcome sets the verdict, reproduced or not. Four of the other five have registered outcomes too. The one left would have repeated the claim on the same kind of close Chan’s script keeps, and it did not run. The plan predicted nothing about the half-life, the drawdown, the Sharpe ratio, the largest position or how often the rule was short, so those describe the run and decide nothing.

The holdout draws five lessons.

1. **The claim survives on its sign alone.** The P&L ends at 0.1132, above 0, and its mean daily value cannot be told from zero.
2. **Writing the predictions down first is what makes it a check.** The plan filed six predictions and one figure to report before the run computed anything on the later closes, and the post sets each beside what happened.
3. **The later closes read as a random walk, as predicted.** A random walk is a series whose every daily change is a fresh draw with no pull back to an average. None of the three tests from the earlier post rejects one.
4. **The frozen lookback is about a quarter of the later half-life.** The closes after 2012 give a half-life of 457.8077 days.
5. **The fall is again several times the final P&L.** The deepest drawdown is 0.5033, more than four times what the run ends with.

## The closes and what carried over

The closes are Alpha Vantage’s daily close for USD.CAD, from its `FX_DAILY` series, downloaded 2026-10-13. The file holds 5,000 days from 2007-08-10 to 2026-10-12. Chan’s script reads prices taken every minute, each minute’s record called a bar, and keeps the bar stamped 16:59 New York time as each day’s close. A vendor’s daily close comes from a different feed, a separate source of prices, so this holdout tests the rule on a second feed as well as on later days.

The rule needs 115 closes before it can hold a position, so the run starts on the 115 closes before 2012-03-29, from 2011-10-20 to 2012-03-28. Those closes only fill the window. They fall inside Chan’s sample, so no test reads them and no P&L is earned on them. Two of the 3,793 weekdays from 2012-03-29 to 2026-10-12 have no close, which leaves the 3,791 traded days. The two are more than a year apart, so no change from one close to the next skips more than one weekday.

Everything else carried over unchanged. Each day’s P&L is yesterday’s position times today’s percent change in the close. The script treats the position as a market value. So a position of 1 held through a 1 percent rise earns 0.01, and every P&L in this post is a sum of those daily amounts rather than a percent of an account. The rule pays no transaction cost and earns or pays no overnight interest on the currencies it holds, as in Chan’s script.

![Two charts stacked on one shared date axis from October 2011 to October 2026. The top chart shows USD.CAD’s daily closes, starting near 1.00 in 2012, climbing to about 1.46 by early 2016, swinging between about 1.20 and 1.45 through 2020 and 2021, and ending near 1.43 in 2026. A smoother brown line, the 115-day moving average, trails the closes from the end of March 2012. A dashed vertical line through both charts marks the first traded day, 2012-03-29. The bottom chart shows the cumulative P&L of the linear rule as a green line from 2012-03-29. It rises to 0.1035 on 2013-11-20, marked with a dot, then falls inside a shaded band to −0.3998 on 2016-01-19, marked with a red dot. It climbs back with sharp drops in early 2020 and in 2022, passes its 2013 high in 2024, and ends at 0.1132. A horizontal line marks zero. The heading above the top chart gives the half-life of the traded closes as 457.8 days, and the heading above the bottom chart calls the P&L unlevered and before costs. The title calls the verdict registered and the path exploratory, and the note says the curve, the fall and the half-life are exploratory.](../docs/figures/usdcad_holdout.png)

*USD.CAD’s closes after Chan’s sample with their 115-day moving average, and the linear rule’s cumulative P&L with its deepest fall shaded. The lookback is frozen at the half-life of Chan’s closes. Of everything the chart shows, the plan predicted only the sign of the final P&L.*

## Lesson 1: the claim survives on its sign alone

The pass mark, written down before the run, was that the daily P&L summed over the 3,791 traded days is above 0. It is 0.1132. So Chan’s claim that the P&L “manages to be positive” holds on the fourteen years after his sample, and the verdict is **reproduced**. On his own closes the P&L ended at 0.1141.

A positive sum says less than it seems to, because a rule with no edge can end positive by chance. The question is whether the mean daily P&L behind the sum is above zero by more than chance would give.

The t-statistic answers it. It divides the mean daily P&L by its standard error, the amount that mean would typically wander by chance. The **Newey-West** version widens that standard error when nearby days’ P&L moves together, which a rule that holds much the same position for weeks could cause. It allows for days up to 8 apart moving together. A test that asks only whether the mean is above zero is one-sided. This one accepts a 5 percent chance of a false alarm, so it needs a t above 1.645.

```math
\small\begin{array}{l|r|r}
\text{Figure} & \text{Chan's closes} & \text{After 2012} \\ \hline
\text{Days with P}\&\text{L} & 1{,}101 & 3{,}791 \\
\text{Final P}\&\text{L} & 0.1141 & 0.1132 \\
\text{Newey-West t} & \text{not computed} & 0.2670 \\
\text{Sharpe ratio} & 0.12 & 0.0715 \\
\text{Deepest drawdown} & 0.6425 & 0.5033
\end{array}
```

Chan’s 1,216 closes give 1,101 days with P&L, because the first 115 only fill the window.

The t is 0.2670, far below 1.645, as the plan predicted. So the mean daily P&L cannot be told from zero.

![An animated whiteboard sketch titled “The sign and the t”, drawn stroke by stroke. A green check mark comes first, with the words “sum 0.1132 > 0” beside it. Below them a number line carries two ticks, labelled “0” and “1.645”. A red hatched zone above the line runs from the 1.645 tick to the line’s right end, under the words “beats chance, one-sided 5%”. A brown dot lands on the line just right of the 0 tick, far left of the zone, labelled “t = 0.2670”, with “mean daily P&L” above that. The finished sketch holds for four seconds before it redraws.](../docs/figures/usdcad_holdout_sign_and_t.gif)

*The sum clears its pass mark of 0, and the t falls far short of 1.645. The line is drawn to scale, so the gap between any two points on it is in proportion to the gap between their values. The sum and the t come from the run.*

The Sharpe ratio says the same thing as the t, in the form most traders use. It is the mean daily P&L over its standard deviation, times the square root of 252 trading days. Dividing every day’s P&L by a fixed account size leaves the ratio unchanged, so it can be computed without choosing an account size. After 2012 it is 0.0715, against 0.12 on Chan’s closes. Both Sharpe ratios leave out the transaction costs and the overnight interest, as the P&L does.

## Lesson 2: writing the predictions down first is what makes it a check

A test chosen after the data is seen proves little, because some test always fits the data. So before this run computed anything on the closes after 2012-03-28, its plan wrote down six predictions and one figure to report beside them. Each named its statistic, its pass mark where it had one, and the days it reads. The plan also fixed the lookback at 115 and said which outcome of the first prediction would count as reproduced. The list keeps the plan’s labels, H1 to H7, and Lesson 3 explains the three tests behind H4 to H6.

1. **H1, the final P&L is above 0.** This is Chan’s claim. It is 0.1132.
2. **H2, the same holds on Chan’s 16:59 bar.** It did not run.
3. **H3, the Newey-West t is not above 1.645.** It is 0.2670.
4. **H4, the ADF statistic is not below its 10 percent critical value.** It is −2.0814.
5. **H5, the variance ratio test does not reject at 5 percent.** Its p-value is 0.4343.
6. **H6, the Hurst exponent sits inside its random-walk band.** It is 0.4974.
7. **H7, the half-life, with no prediction.** It is 457.8077 days.

H1 decides the verdict. H3 to H6 were written down first too, so their outcomes are registered, but the verdict does not rest on them. Each came out as predicted. H7 carried no prediction, so it is exploratory.

H2 would have tested the same claim on Chan’s own feed, the 16:59 bar, rebuilt from another vendor’s minute bars. On this repository’s data subscription those bars reach back only to 2024-10-13, so H2 was planned on the closes since then, not on fourteen years of them. The only route this repository has to those bars cannot yet save them as one complete file to keep, so H2 waits. Without it, nothing here says whether the result depends on the feed.

### What was read before the run

The plan names four reads made before the run. Three came before it was written. That matters because the less an author had seen before writing a prediction down, the better a check the prediction is.

1. **The Johansen test on AUD.USD against CAD.USD**, run earlier in this repository, had already read about 20 of the holdout’s first days. A Johansen test asks whether some mix of two prices keeps returning to a level. CAD.USD is one over USD.CAD, the price of a Canadian dollar in US dollars, and Chan’s file for it runs to 2012-04-26. That run used a different rule on Chan’s feed, and the [post on that test](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-johansen-lessons.md) covers it.
2. **A check of the vendor’s coverage** compared its closes with Chan’s only on the days the two share, up to 2012-03-28.
3. **A check of the other vendor’s minute bars** read one day, 2026-10-12, to confirm that its 16:59 bar exists, and computed nothing on it.
4. **The file checks** read every close as the file went into the repository. They confirmed its checksum, its columns and that no close moves by more than a factor of 1.6 from the one before. They reported only whether each check passed.

None of them computed the rule’s P&L or any predicted statistic on the later days.

## Lesson 3: the later closes read as a random walk, as predicted

The earlier post ran three tests on Chan’s closes, and none could tell USD.CAD from a random walk. The plan predicted the same on the later closes, and the same tests say so.

```math
\small\begin{array}{l|r|r}
\text{Test} & \text{Chan's closes} & \text{After 2012} \\ \hline
\text{ADF statistic} & -1.8407 & -2.0814 \\
\text{Variance ratio, p} & 0.3673 & 0.4343 \\
\text{Hurst exponent} & 0.4732 & 0.4974
\end{array}
```

1. **The augmented Dickey-Fuller (ADF) test** asks whether each day’s change tends to pull the close back toward a fixed level, so that a high close tends to be followed by a fall. It rejects a random walk when its statistic falls below a critical value, the threshold for a chosen level of confidence. Chan’s script calls the version in jplv7, a MATLAB toolbox. Run that way, allowing for one earlier day’s change, it gives −2.0814. That is above its 10 percent critical value of −2.5937, so it does not reject. `adfuller`, the version most Python code calls, gives −2.0243 on the same closes. The earlier post’s second lesson explains why the two versions differ.
2. **The variance ratio test** divides the variance of the close’s two-day changes by twice the variance of its one-day changes. Variance measures how widely the changes spread. A random walk’s two-day changes have twice the variance of its one-day ones, so the ratio is 1 for a random walk. It rejects when its p-value falls to 0.05 or below. It gives a p-value of 0.4343, so a random walk would give a ratio this far from 1 more than two times in five.
3. **The Hurst exponent** is 0.4974, from `genhurst`, the function Chan’s script calls. Near 0.5 it marks a random walk, and below 0.5 a series that tends to reverse its moves. On 40,000 simulated random walks, each 3,791 closes long, the same estimator averages 0.4987 with a standard deviation of 0.0130. The plan’s band is two standard deviations either side, 0.4987 ± 0.0260, and the Hurst exponent sits 0.0014 below the average, measured before rounding.

The ADF test’s 10 percent critical value is the same −2.5937 on Chan’s 1,216 closes, because the toolbox reads one value for every series this long. The earlier post rounds it to −2.594. The Hurst exponent’s band is for the 3,791 later closes only. On Chan’s closes its random-walk spread was wider, as the earlier post’s third lesson measures.

So fourteen more years of closes did not turn USD.CAD into a series a test can call mean reverting. The rule still trades it as one.

## Lesson 4: the frozen lookback is about a quarter of the later half-life

On Chan’s closes the half-life was 115.209794 days, which the rule rounds to its lookback. On the closes after 2012 it is 457.8077 days, almost four times as long.

```math
\small\begin{array}{l|r}
\text{Half-life on Chan's closes} & 115.209794 \text{ days} \\
\text{Lookback the rule trades at} & 115 \text{ days} \\
\text{Half-life after 2012} & 457.8077 \text{ days}
\end{array}
```

Chan sets the lookback to the half-life because the half-life “depends on the properties of the price series itself” (Chan, 2013, p. 60). On the closes after 2012 the estimate came out almost four times longer, and a rule fixed in 2012 kept measuring its deviations over 115 days. The plan carried no prediction for the half-life, so this is a description of the run and nothing more.

The 457.8077-day half-life also cannot be read as the right lookback. The tests in Lesson 3 cannot reject a random walk, which has no half-life at all, so the figure is an estimate from a series that may not revert. Running the rule again at a lookback of 458 would be choosing a parameter after seeing its number. That would make a new run, and an exploratory one.

## Lesson 5: the fall is again several times the final P&L

On Chan’s closes the P&L fell 0.6425 from its high, more than five times what it ended with. After 2012 it happened again at a smaller scale. The P&L rose to 0.1035 on 2013-11-20 and fell to −0.3998 on 2016-01-19, a drawdown of 0.5033, more than four times the final 0.1132.

As in Chan’s sample, whose fall came in 2008, this fall came while the US dollar rose. Across the P&L’s fall, USD.CAD rose from 1.0445 to 1.45699, so the US dollar gained 39.5 percent on the Canadian dollar. The rule bets that the close returns to its average, so this time it was mostly short. It was short the US dollar on 458 of the 562 days of the fall. In 2008 it was short on all 69 days of the fall.

The P&L did not pass its 2013 high again until 2024-03-06, more than ten years later.

Chan also cautions that “an unlimited amount of capital may be needed”, because nothing caps the position (Chan, 2013, p. 50). The largest position after 2012 was a short of 5.4054, taken at the close of 2020-03-18. That close stood more than five moving standard deviations above its average. On Chan’s closes the largest was a short of 4.12.

The rule also leaned the other way from Chan’s sample. On his closes it was short on 488 of the 1,101 days it held a position, fewer than half. After 2012 it was short on 60.06 percent of the traded days and long on 39.94 percent, and it held a position on every traded day.

## What this holdout cannot say

Four questions are beyond it.

1. **Whether the result depends on the feed.** The vendor’s daily close is not Chan’s 16:59 bar, and the holdout on his bar has not run.
2. **Whether the rule would pay.** It charges no transaction cost, earns or pays no overnight interest, and holds a position that grows without limit as the close strays.
3. **Whether the mean is real.** The claim is about the sign of a sum, and a t of 0.2670 cannot separate the mean daily P&L from zero.
4. **Anything about a lookback other than 115.** The plan fixed the lookback before the run read the later closes, and any other lookback would be chosen after seeing them.

## What this means for a trader

One habit for each lesson.

1. **Read the t beside the sign.** A total that ends positive over fourteen years can still come from a mean daily P&L that cannot be told from zero, and the sign alone says little about an edge.
2. **Write the predictions down before reading the data.** A plan filed first, with its pass marks and the days it reads, is the difference between a check and a story told afterwards. Name what was seen before it, too.
3. **Run the tests again before trading a rule on new years.** A rule built for a reverting series trades whatever series it is given, including one the tests cannot tell from a random walk, and only the tests say so.
4. **Check a fixed parameter against the new data, and do not re-fit it there.** A lookback set on one period can be a quarter of what the next period measures. Changing it after seeing that makes a new, exploratory run.
5. **Size the drawdown before the trade.** The P&L of an uncapped rule that sells a rising price fell from its high by more than four times its final value here, and by more than five times in Chan’s sample.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 2.5, with pages 49, 50 and 60 cited. The page numbers are the 2013 print edition’s, ISBN 9781118460146.
2. `alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv`, Alpha Vantage’s `FX_DAILY` close for USD.CAD, downloaded 2026-10-13. Its [record in the data index](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) names its source, span and price basis.
3. Newey, W. K., and West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
4. The earlier post’s references cover the ADF, variance ratio and Hurst code, and the script this run’s rule was transcribed from.

*Not investment advice. Code: [the holdout](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_holdout.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_holdout_figures.py), with the checks behind [the holdout’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_holdout.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_holdout_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-51-example-25s-linear-rule-on-usdcad-after-2012-chans-algorithmic-trading) that records each prediction beside its outcome.*
