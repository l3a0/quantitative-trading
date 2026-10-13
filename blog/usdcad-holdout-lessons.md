# Trading USD.CAD’s mean reversion for fourteen years after the book

*On closes nobody had read, Chan’s trade still ends positive, by too little to tell from chance.*

## Why trade the rule on later closes

Ernest Chan’s *Algorithmic Trading* tests USD.CAD, the price of a US dollar in Canadian dollars, for mean reversion, and then trades it with what this post calls the linear rule. The rule holds a position equal to minus the close’s z-score, the number of moving standard deviations the close sits from its moving average, so it sells as the close rises above its average and buys as it falls below. Chan reports one result in words: the profit and loss, or P&L, “manages to be positive, albeit with a large drawdown” (Chan, 2013, p. 49).

The [post on Chan’s USD.CAD tests](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) reproduced that claim on his own 1,216 closes, from 2007-07-23 to 2012-03-28, and could say nothing more. Two things kept every figure there exploratory.

1. **The sample was spent.** Chan chose those days and printed their numbers, so reproducing them checks the arithmetic and not the rule.
2. **The lookback is a look-ahead.** The rule’s moving average and deviation look back 115 days, the half-life of the same closes it trades. A trader in 2008 could not have known the half-life of a series that runs to 2012.

This post removes both. It keeps the lookback at 115, fixed from Chan’s closes and never re-estimated, and trades only closes after his sample ends: 3,791 days from 2012-03-29 to 2026-10-12. The rule is the same function the earlier post ran, and the earlier post explains the tests and the rule in full. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

The holdout draws five lessons.

1. **The claim survives on its sign alone.** The P&L ends at 0.1132, above 0, and its mean daily value cannot be told from zero.
2. **Writing the predictions down first is what makes it a check.** Six predictions and one figure to report were filed before any later close was read, and the post sets each beside what happened.
3. **The later closes read as a random walk, as predicted.** None of the three tests from the earlier post rejects one.
4. **The frozen lookback is about a quarter of the later half-life.** The closes after 2012 give a half-life of 457.8077 days.
5. **The fall is again several times the final P&L.** The deepest drawdown is 0.5033, more than four times what the run ends with.

**The verdict is registered, and the side figures are exploratory.** A registered result is one whose test and pass mark were written down before any of its data was read. A **holdout** is data kept back from every decision about a test, so a result on it is a fresh check. The claim and four of the predictions beside it are registered. The half-life, the drawdown, the Sharpe ratio and the positions were not predicted, so they describe the run and decide nothing.

## The closes and what carried over

The closes are Alpha Vantage’s daily close for USD.CAD, from its `FX_DAILY` series, downloaded 2026-10-13. The file holds 5,000 days from 2007-08-10 to 2026-10-12. A vendor’s daily close is a different feed from the bar stamped 16:59 New York time that Chan’s script keeps, so this holdout tests the rule on a second feed as well as on later days.

The rule needs 115 closes before it can hold a position, so the run starts on the 115 closes before 2012-03-29, from 2011-10-20 to 2012-03-28. Those closes only fill the window. They fall inside Chan’s sample, so no test reads them and no P&L is earned on them. Two of the 3,793 weekdays from 2012-03-29 to 2026-10-12 have no close, and no two of those are in a row.

Everything else carried over unchanged. Each day’s P&L is yesterday’s position times today’s percent change in the close. The rule pays no transaction cost and earns or pays no overnight interest on the currencies it holds, as in Chan’s script.

![Two charts stacked on one shared date axis from October 2011 to October 2026. The top chart shows USD.CAD’s daily closes, starting near 1.00 in 2012, climbing to about 1.46 by early 2016, swinging between about 1.21 and 1.45 through 2020 and 2021, and ending near 1.43 in 2026. A smoother brown line, the 115-day moving average, trails the closes from the end of March 2012. A dashed vertical line marks the first traded day, 2012-03-29. The bottom chart shows the cumulative P&L of the linear rule as a green line from 2012-03-29. It rises to 0.1035 on 2013-11-20, marked with a dot, then falls inside a shaded band to −0.3998 on 2016-01-19, marked with a red dot. It climbs back with sharp drops in early 2020 and in 2022, passes its 2013 high in 2024, and ends at 0.1132. A horizontal line marks zero. The title calls the claim registered, and the note says the curve, the fall and the half-life are exploratory.](../docs/figures/usdcad_holdout.png)

*USD.CAD’s closes after Chan’s sample with their 115-day moving average, and the linear rule’s cumulative P&L with its deepest fall shaded. The lookback is frozen at the half-life of Chan’s closes, and only the sign of the final P&L was predicted.*

## Lesson 1: the claim survives on its sign alone

The pass mark, written down before the run, was that the daily P&L summed over the 3,791 traded days is above 0. It is 0.1132. So Chan’s claim that the P&L “manages to be positive” holds on fourteen years he never saw, and the verdict is **reproduced**. On his own closes the P&L ended at 0.1141.

A positive sum says less than it seems to, because a rule with no edge can end positive by chance. The question that matters is whether the mean daily P&L behind the sum is above zero by more than chance would give. The t-statistic answers it. It divides the mean daily P&L by its standard error, the amount that mean would typically wander by chance. The **Newey-West** version widens that standard error when nearby days’ P&L moves together, which it does here, because the rule holds much the same position for weeks. It allows for neighbours up to 8 days apart. A one-sided test at the 5 percent level needs a t above 1.645.

```math
\begin{array}{l|r|r}
\text{Figure} & \text{Chan's closes, 2008 to 2012} & \text{After 2012} \\ \hline
\text{Days with P\&L} & 1{,}101 & 3{,}791 \\
\text{Final P\&L} & 0.1141 & 0.1132 \\
\text{Newey-West t of the mean daily P\&L} & \text{none} & 0.2670 \\
\text{Sharpe ratio} & 0.12 & 0.0715 \\
\text{Deepest drawdown} & 0.6425 & 0.5033
\end{array}
```

The t is 0.2670, far below 1.645, as the registration predicted. So the mean daily P&L cannot be told from zero. The claim survives on the sign of the sum and on nothing stronger.

The Sharpe ratio says the same thing in the form most traders use. It is the mean daily P&L over its standard deviation, times the square root of 252 trading days. Dividing every day’s P&L by any fixed account size leaves it unchanged, so it needs no account. After 2012 it is 0.0715, against 0.12 on Chan’s closes. Both leave out the transaction costs and the overnight interest, as the P&L does.

## Lesson 2: writing the predictions down first is what makes it a check

A test chosen after the data is seen proves little, because some test always fits the data. So before any close after 2012-03-28 was read, the plan for this run wrote down six predictions and one figure to report beside them. Each named its statistic, its pass mark where it had one, and the days it reads. The plan also fixed the lookback at 115 and said which outcome of the first prediction would count as reproduced.

```math
\begin{array}{l|l|l|l}
\text{Prediction} & \text{Predicted} & \text{Outcome} & \text{As predicted} \\ \hline
\text{H1, final P\&L above 0} & \text{yes, the claim} & 0.1132 & \text{yes} \\
\text{H2, the same on Chan's 16:59 bar} & \text{yes} & \text{not run} & \text{n/a} \\
\text{H3, Newey-West t above 1.645} & \text{no} & 0.2670 & \text{yes} \\
\text{H4, ADF below its 10 percent value} & \text{no} & -2.0814 & \text{yes} \\
\text{H5, variance ratio rejects at 5 percent} & \text{no} & p = 0.4343 & \text{yes} \\
\text{H6, H inside its random-walk band} & \text{yes} & 0.4974 & \text{yes} \\
\text{H7, the half-life} & \text{none} & 457.8077 \text{ days} & \text{n/a}
\end{array}
```

H1 decides the verdict. H3 to H6 decide nothing on their own, and each landed as written. H7 carried no prediction, so it is exploratory.

H2 did not run. It would have tested the same claim on Chan’s own feed, the 16:59 bar, rebuilt from another vendor’s minute bars. Those bars reach back only to 2024-10-13 on the plan this repository has, so H2 waits for data that covers 2012. Without it, nothing here says whether the result depends on the feed.

Three reads of the later closes came before the run, and the plan names all three because a registration is only as clean as what was seen before it.

1. **The Johansen test on AUD.CAD** in this repository had already read about 20 of the holdout’s first days, through 2012-04-26, from a file of Chan’s that runs to that date. That run used a different rule on Chan’s feed. The [post on that test](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-johansen-lessons.md) covers it.
2. **A check of the vendor’s coverage** compared its closes with Chan’s only on the days the two share, up to 2012-03-28.
3. **The file checks** read every close when the vintage was committed, to confirm its checksum and its columns, and only whether they passed was looked at.

None of them computed a P&L or a test statistic on the later days.

## Lesson 3: the later closes read as a random walk, as predicted

The earlier post ran three tests on Chan’s closes, and none could tell USD.CAD from a random walk, a series whose every daily change is a fresh draw with no pull back to an average. The plan predicted the same on the later closes, and the same tests say so.

```math
\begin{array}{l|r|r|r}
\text{Test} & \text{Chan's closes} & \text{After 2012} & \text{Rejects a random walk when} \\ \hline
\text{ADF statistic, jplv7, 1 lag} & -1.8407 & -2.0814 & \text{below } -2.5937 \\
\text{Variance ratio test, p-value} & 0.3673 & 0.4343 & \text{below 0.05} \\
\text{Hurst exponent H, genhurst} & 0.4732 & 0.4974 & \text{outside } 0.4987 \pm 0.0260
\end{array}
```

1. **The augmented Dickey-Fuller (ADF) test** gives −2.0814, above its 10 percent critical value of −2.5937, so it does not reject. The statistic has to fall below the critical value to reject. `adfuller`, the version most Python code calls, gives −2.0243 on the same closes, which the earlier post’s second lesson explains.
2. **The variance ratio test** gives a p-value of 0.4343. A random walk would give a ratio this far from 1 more than two times in five.
3. **The Hurst exponent H** is 0.4974. On 40,000 random walks of the same 3,791 closes, the same estimator averages 0.4987 with a standard deviation of 0.0130. The plan’s band is two standard deviations either side, 0.4987 ± 0.0260, and H sits 0.0014 below the average. The 10 percent critical value above is the one for this sample’s length, where the earlier post’s was for Chan’s 1,216 closes.

So fourteen more years of closes did not turn USD.CAD into a series a test can call mean reverting. The rule still trades it as one.

## Lesson 4: the frozen lookback is about a quarter of the later half-life

The **half-life** is how long a distance from the mean takes to halve, if the series is pulled back toward a mean. On Chan’s closes it was 115.2 days, which the rule rounds to its lookback. On the closes after 2012 it is 457.8077 days, almost four times as long.

```math
\begin{array}{l|r}
\text{Half-life on Chan's closes, 2007 to 2012} & 115.2 \text{ days} \\
\text{Lookback the rule trades at} & 115 \text{ days} \\
\text{Half-life on the closes after 2012} & 457.8077 \text{ days}
\end{array}
```

Chan sets the lookback to the half-life because the half-life “depends on the properties of the price series itself” (Chan, 2013, p. 60). On these closes that property moved by a factor of four, and a rule fixed in 2012 kept measuring its deviations over 115 days. The plan carried no prediction for the half-life, so this is a description of the run and nothing more.

It also cannot be read as the right lookback. The tests in Lesson 3 cannot reject a random walk, which has no half-life at all, so 457.8077 days is an estimate from a series that may not revert. Running the rule again at a lookback of 458 would be choosing a parameter after seeing its number. That would make a new run, and an exploratory one.

## Lesson 5: the fall is again several times the final P&L

On Chan’s closes the P&L fell 0.6425 from its high, more than five times what it ended with. After 2012 it happened again at a smaller scale. The P&L rose to 0.1035 on 2013-11-20 and fell to −0.3998 on 2016-01-19, a drawdown of 0.5033, more than four times the final 0.1132.

The fall has the same cause as in 2008. Across it USD.CAD rose from 1.0445 to 1.45699, so the US dollar gained 39.5 percent on the Canadian dollar. The rule bets that the close returns to its average, so it was short the US dollar on 458 of the 562 days of the fall. The P&L did not pass its 2013 high again until 2024-03-06, more than ten years later.

Chan’s third caution is that “an unlimited amount of capital may be needed”, because nothing caps the position (Chan, 2013, p. 50). The largest position after 2012 was a short of 5.4054 on 2020-03-19, when the close stood more than five moving standard deviations above its average. On Chan’s closes the largest was a short of 4.12.

The rule also leaned the other way from Chan’s sample. On his closes it was short on 488 of the 1,101 days it held a position. After 2012 it was short on 0.6006 of the traded days and long on 0.3994, and it was never flat. A rule that sells a rising close spends most of its time short through a dollar that rose for most of the period.

## What this holdout cannot say

Four questions are beyond it.

1. **Whether the result depends on the feed.** The vendor’s daily close is not Chan’s 16:59 bar, and the holdout on his bar has not run.
2. **Whether the rule would pay.** It charges no transaction cost, earns or pays no overnight interest, and holds a position that grows without limit as the close strays.
3. **Whether the mean is real.** The claim is about the sign of a sum, and a t of 0.2670 cannot separate the mean daily P&L from zero.
4. **Anything about a lookback other than 115.** The lookback was fixed before the later closes were read, and any other would be chosen after seeing them.

## What this means for a trader

One habit for each lesson.

1. **Read the t beside the sign.** A total that ends positive over fourteen years can still be indistinguishable from zero, and the sign alone says nothing about an edge.
2. **Write the predictions down before reading the data.** A plan filed first, with its pass marks and the days it reads, is the difference between a check and a story told afterwards. Name what was seen before it, too.
3. **Run the tests again before trading a rule on new years.** A rule built for a reverting series still trades a series that no longer looks like one, and only the tests say so.
4. **Check a fixed parameter against the new data, and do not re-fit it there.** A lookback set on one period can be a quarter of what the next period measures. Changing it after seeing that makes a new, exploratory run.
5. **Size the drawdown before the trade.** An uncapped rule that sells a rising price fell more than four times its final P&L here and more than five times in Chan’s sample.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 2.5, with pages 49, 50 and 60 cited. The page numbers are the 2013 print edition’s, ISBN 9781118460146.
2. `alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv`, Alpha Vantage’s `FX_DAILY` close for USD.CAD, downloaded 2026-10-13. Its [record in the data index](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) names its source, span and price basis.
3. Newey, W. K., and West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
4. The earlier post’s references cover the ADF, variance ratio and Hurst code, and the script this run’s rule was transcribed from.

*Not investment advice. Code: [the holdout](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_holdout.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_holdout_figures.py), with the checks behind [the holdout’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_holdout.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_holdout_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-51-example-25s-linear-rule-on-usdcad-after-2012-chans-algorithmic-trading) that records each prediction beside its outcome.*
