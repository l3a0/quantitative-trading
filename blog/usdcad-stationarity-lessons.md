# Trading a mean reversion strategy on a currency pair that isn’t stationary

*The trade ends positive after a fall more than five times its profit.*

## Why test a price before trading it

A mean-reversion trade bets that a price will come back to its average. A series that does come back is called stationary, and most prices are not. Ernest Chan opens the chapter on mean reversion in his second book, *Algorithmic Trading*, by saying that most price series “are not mean reverting, but are geometric random walks” (Chan, 2013, p. 39). A random walk has no average to return to, because each day’s change is a fresh draw.

So Chan tests a series before he backtests a trade on it. A test reads every day’s price, while a backtest sees only the round trips, each an entry and its exit, that one set of rules happened to make. That is why the test’s significance “is usually higher than a direct backtest” (Chan, 2013, p. 50).

Chan’s Examples 2.1 to 2.4 run four such tests on USD.CAD, the price of a US dollar in Canadian dollars. None of them can show that it reverts, and Example 2.5 trades it anyway. This repository transcribed his script, `stationarityTests.m`, and ran it on the same closes. It found three things.

1. **Three tests land every digit the script prints.** The ADF test, the variance ratio test and the half-life give four statistics between them, and all four match. So the closes here are the closes Chan ran.
2. **The Hurst exponent misses.** The book prints 0.49. The function Chan’s script calls gives 0.47, and his own Python port gives 0.48. Both misses are smaller than the spread H shows on a random walk of the same length.
3. **The trade ends positive.** Chan says its profit and loss, or P&L, “manages to be positive, albeit with a large drawdown” (Chan, 2013, p. 49). The P&L ends at 0.1141. On the way it rises to a high of 0.1321 in July 2008, then falls 0.6425 to −0.5104 by October. That fall from the high is the drawdown.

**Every result here is exploratory.** The reproduction runs Chan’s tests on Chan’s days, so it says whether his numbers follow from his closes and nothing about whether USD.CAD reverts today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The tests and the file

Each test asks the same question from a different side: does this series behave like a random walk, or is something pulling it back?

1. **The augmented Dickey-Fuller (ADF) test**, Example 2.1. It regresses each day’s change on the previous day’s close. If the series is pulled back toward a mean, a high close tends to be followed by a fall, so the coefficient on the previous close, called λ, is negative. The test divides λ by its standard error and compares the result with a critical value, the threshold the statistic must fall below for the test to reject a random walk at a chosen level of confidence (Chan, 2013, p. 42). The [post on Chan’s stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) explains how the test reads, what its lags do and where its critical values come from. Chan runs it with a constant, so the mean need not be zero. He also adds one lagged change, the previous day’s change, which is what makes the test augmented.
2. **The Hurst exponent H**, Example 2.2. Chan describes it through how fast a price spreads out (Chan, 2013, p. 41). A random walk drifts from where it started by a distance that grows like the square root of the time elapsed. So the variance of the change in the log price over τ days grows in proportion to τ, and changes over twice as many days have twice the variance. A reverting series spreads more slowly, and H measures how much: the variance grows like τ²ᴴ, which the book prints as “τ2H”. A random walk has H = 0.5, a reverting series less, and a trending series more (Chan, 2013, p. 45).
3. **The variance ratio test**, Example 2.3. H is an estimate, and on a finite sample it could sit below 0.5 by chance. The variance ratio test supplies the missing significance test (Chan, 2013, p. 45). For a random walk the variance of two-day changes is exactly twice the variance of one-day changes. The test divides the first by twice the second and asks whether the ratio differs from 1 by more than chance would give (Lo and MacKinlay, 1988). A reverting series gives a ratio below 1. Chan runs it with MATLAB’s `vratiotest`.
4. **The half-life**, Example 2.4. A λ like the ADF test’s also says how fast the pull works. When the series is written as a continuous process, its expected distance from the mean decays exponentially and halves in −ln 2 / λ days (Chan, 2013, pp. 46–47). For the half-life, Chan fits λ in a second regression of each day’s change on the previous close (Chan, 2013, p. 47). The script adds a constant and leaves out the lagged change, as the book’s regression does.

The trade, Example 2.5, uses what this post calls the linear rule. Each day it computes the close’s z-score, the number of moving standard deviations the close sits from its moving average, where a standard deviation measures how far values typically stray from their average, and holds minus that number (Chan, 2013, p. 48). So it sells more as the close rises further above its average and buys more as it falls further below. Both the average and the deviation look back over the half-life rounded to whole days, 115. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds the z-score up and trades the same rule on a pair of ETFs.

The script calls the position its market value. Each day’s P&L is yesterday’s position times today’s percent change in the close. Nothing else enters it. The rule pays no transaction cost and earns or pays no overnight interest on the currencies it holds, which the [post on AUD.CAD with rollover interest](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-rollover-lessons.md) shows can matter. The P&L is in units of the position, not a return on capital, so it has no Sharpe ratio, and the book prints none.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) of minute bars from Chan’s 2018 Python port of his book’s code, saved 2018-10-13. The script loads a MATLAB file of the same bars, which neither public copy of his code includes. The script keeps the bar stamped 16:59 New York time on each day, which gives 1,216 closes from 2007-07-23 to 2012-03-28. This repository transcribed the script from `ericnberwick/EpchanPreview` at commit `e4bc46f`. It also transcribed jplv7’s `adf` and Aste’s `genhurst` from another public copy, and rebuilt `vratiotest` from Lo and MacKinlay’s paper rather than copying MathWorks’ code.

## Lesson 1: 4 statistics reproduced

Here is each figure, computed, beside the value the script’s comments record and the one the book prints.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{ADF statistic, 1 lag} & -1.840744 & -1.840744 & \text{about } -1.84 \\
\text{AR(1) estimate} & 0.994120 & 0.994120 & \text{none} \\
\text{Critical value, 1 percent} & -3.458 & -3.458 & \text{none} \\
\text{Critical value, 5 percent} & -2.871 & -2.871 & \text{none} \\
\text{Critical value, 10 percent} & -2.594 & -2.594 & -2.594 \\
\text{Variance ratio test, rejects} & \text{no} & \text{no} & \text{none} \\
\text{Variance ratio test, p-value} & 0.367281 & 0.367281 & \text{none} \\
\text{Half-life, days} & 115.209794 & 115.209794 & 115 \\
\text{Hurst exponent H} & 0.473233 & \text{none} & 0.49
\end{array}
```

The AR(1) estimate, from a first-order autoregression, is the coefficient on the previous close when the regression predicts the close rather than its change, so it equals 1 + λ. At 0.9941, each day keeps roughly 99.41 percent of the previous day’s distance from the mean.

Chan reads two things from these figures, and both survive.

1. **The test cannot reject a random walk.** The statistic of −1.84 is above the 10 percent critical value of −2.594, and it has to be below it to reject. So “we can’t show that USD.CAD is stationary” (Chan, 2013, p. 44).
2. **λ is negative**, which Chan reads as a sign that the series is “at least not trending”.

The MATLAB file Chan loaded cannot be compared with the file here, so the match is the only evidence that the two hold the same closes. The four statistics come from three calculations.

1. **The ADF regression**, which gives both the statistic and the AR(1) estimate.
2. **The variance ratio test**, which gives the p-value.
3. **The half-life regression**, which gives the half-life.

Each lands all six decimals the script prints. None of them depends on the units, so every close multiplied by one constant would match too. Closes that moved differently would be unlikely to match all four to six decimals.

## Lesson 2: the ADF figure depends on which toolbox runs it

Chan’s script calls `adf` from jplv7, James LeSage’s free MATLAB toolbox for econometrics. Most Python code reaches for `adfuller` from `statsmodels` instead. Both run the same regression at one lag, and they disagree in the third decimal.

1. **jplv7’s `adf`** fits 1,213 rows and gives −1.840744, the script’s figure.
2. **`adfuller`** fits 1,214 rows and gives −1.843018.

The difference is one row of the sample. A regression on one lagged change cannot use the first two days, because they have no earlier change to lag. jplv7 then trims one more row when it lines up the lagged close, so it starts a day later than `adfuller` does.

Two other copies of this test show why that row matters. Chan’s own 2018 Python port of the script calls `adfuller`, so it would print −1.843018 where the script’s comment records −1.840744. This repository’s shared library of statistics runs `adfuller` too, so a transcription that reached for it would have missed the script’s figure. This repository’s test suite holds both numbers, so a port that swaps one toolbox for the other fails a test. On these closes the test’s conclusion does not change, since both statistics are far above −2.594. On a series sitting near a critical value, it could.

## Lesson 3: H misses 0.49 by less than chance moves it

The book reports an H of 0.49 from the MATLAB code, “which suggests that the price series is weakly mean reverting” (Chan, 2013, p. 45). It is the one figure in the chapter’s script that does not land. Three readings of H on the same closes all miss it.

1. **Tomaso Aste’s `genhurst`**, the function the script calls, gives 0.473233. It estimates H from how the size of changes grows with the number of days between them, averaged over windows from 5 to 19 days.
2. **Chan’s 2018 Python port** replaces `genhurst` with a different estimator of its own name. It fits the log variance of τ-day changes against log τ and halves the slope, which is the book’s definition applied directly. It gives 0.475844, nearer the book and still a miss.
3. **`genhurst` with a longer window.** The function’s last argument sets the longest window it fits, 19 days by default. Raising it to 24, the setting that lands H for Chan’s example on TU, the two-year Treasury note future, later in the book, moves USD.CAD’s H to 0.471426, further from 0.49.

Every copy of Aste’s function that a search of public code found carries the same date, 2013-01-30, and runs the same algorithm, so no earlier version is available to try. Searching for a variant that lands 0.49 would mean choosing a method after seeing its number. A method chosen that way proves nothing about the closes, so this replication did not run that search.

Whether a miss of 0.02 matters depends on how far H moves by chance. H is an estimate from one sample, so even a series with no pull at all gives a value that wanders from sample to sample. A random walk has nothing to find, so the spread of its H is what chance alone does. To measure that spread, this repository drew 40,000 random walks of 1,216 days each, the length of Chan’s sample, and computed both estimators on every one. The measurement was designed after the miss was seen, so it is exploratory like everything else here.

The usual measure of a spread is the standard deviation, or SD, the same unit the linear rule’s z-score counts in. About two-thirds of the values in a bell-shaped spread land within one SD of their average. A random walk’s H is 0.5 in theory, but an estimator run on 1,216 days need not average exactly that, and on the random walks the two estimators differ.

1. **`genhurst`** averages 0.496, close to 0.5, with an SD of 0.023.
2. **The port’s estimator** averages between 0.47 and 0.48, short of 0.5, with an SD of 0.06, more than twice as wide.

So each estimate is best set against its own estimator’s random-walk average rather than against 0.5.

1. **`genhurst`’s 0.4732** is 1.0 SD below its random-walk average, and 16 percent of the random walks give a lower value. The book’s 0.49 is 0.7 SDs above it.
2. **The port’s 0.4758** is within 0.1 SD of its random-walk average, and about half the random walks give a lower value. The book’s 0.49 is 0.2 SDs above it.

The day the sample starts moves `genhurst` too. `genhurst` reads every second close, every third and so on, counting from the first, so dropping one close changes which closes it reads. Starting the sample on 2007-07-24, one day later, moves `genhurst` from 0.4732 to 0.4891, which prints as 0.49. Of the eleven start days from 2007-07-23 to 2007-08-06, six print as 0.49 and one gives 0.5062, above 0.5. The script’s own start gives the lowest value of the eleven. The port’s estimator uses every overlapping change and barely moves, staying between 0.4741 and 0.4758.

The script’s other figures show which start its own run used. A start one day later moves the ADF statistic from the script’s −1.840744 to −1.836150, so the run the script’s comments record starts on 2007-07-23, where `genhurst` gives 0.4732. A later start would explain `genhurst`’s miss only if the book’s H came from another run, and Chan’s MATLAB file is not public, so that cannot be checked. No start day brings the port’s estimator near 0.49, so its miss has no such explanation. This replication keeps the script’s start. Taking the start day that lands 0.49 would mean choosing the data after seeing its number, which proves no more than choosing a method that way.

All three readings fall below 0.5, as the book’s does, and that is not evidence of reversion. An H this close to 0.5 cannot be told from a random walk on 1,216 days. Both estimators measured here, `genhurst` and the port’s, put USD.CAD within about one SD of their own random-walk averages, and a one-day change of start is enough to carry `genhurst` to the book’s figure.

Then the variance ratio test says what H cannot. The ratio is 0.964745, below 1, as a reverting series would give. Its statistic is −0.901577, and its p-value of 0.367281 means a random walk would give a ratio this far from 1 more than a third of the time. The test does not reject. So the ADF test, H and the variance ratio test agree: each statistic sits on the side a reverting series would give, and none can tell USD.CAD from 2007 to 2012 apart from a random walk.

## Lesson 4: the trade ends positive after a fall more than five times its final P&L

Chan trades the rate anyway. He argues that failing a test at 90 percent certainty need not end the matter, “because most profitable trading strategies do not require such a high level of certainty” (Chan, 2013, p. 47). He then reports the result in words only: the P&L “manages to be positive, albeit with a large drawdown” (Chan, 2013, p. 49).

“Positive” is checkable, so before any P&L was computed, the replication wrote down a pass mark: the claim holds if the daily P&L sums to more than 0 over all 1,216 days. The [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-22-the-stationarity-tests-on-usdcad-chans-algorithmic-trading) records it. The 115-day window first fills on 2007-12-31, so the rule earns its first P&L on 2008-01-02, and the P&L ends at 0.1141. The claim holds.

“Large” names no scale, so the drawdown is reported beside the claim and decides nothing. The P&L reaches its high of 0.1321 on 2008-07-22 and falls to −0.5104 on 2008-10-27, a drop of 0.6425 in three months. That is more than five times what the run ends with. The high is never regained. The P&L ends 0.0180 below it, after climbing 0.6246 back from the October low.

The figure below redraws the script’s two plots, the closes and the cumulative P&L. The book prints a chart of the cumulative P&L, and nothing compares this redraw with it, so it is a redraw of the script’s plot rather than a checked copy.

![Two charts stacked on one shared date axis from July 2007 to March 2012. The top chart shows USD.CAD’s 1,216 daily closes at 16:59 New York time, starting near 1.05, falling to about 0.92 in late 2007, then climbing steeply from about 1.00 in July 2008 to nearly 1.30 by late October 2008. It touches 1.30 again in March 2009 and eases back to about 1.00 by 2011. A smoother brown line, the 115-day moving average, starts at the end of December 2007 and trails the closes, peaking near 1.24 in the spring of 2009. The bottom chart shows the cumulative P&L of the linear rule as a green line, flat at zero until January 2008. It rises to a high of 0.1321 on 2008-07-22, marked with a dot, then falls inside a shaded band to a low of −0.5104 on 2008-10-27, marked with a red dot. It first climbs back to zero in December 2010 and ends at 0.1141, below its 2008 high. A horizontal line marks zero. The title calls the redraw exploratory.](../docs/figures/usdcad_mean_reversion.png)

*USD.CAD’s closes with their 115-day moving average, and the linear rule’s cumulative P&L with its fall from 2008-07-22 to 2008-10-27 shaded, redrawn on Chan’s closes. The bottom panel redraws the script’s plot of the cumulative P&L, which the book prints as its Figure 2.3 under a caption that names AUDCAD rather than USD.CAD.*

The top panel shows what the rule bet against. Across the fall, USD.CAD rose from 1.00835 to 1.29485, so the US dollar gained 28.4 percent on the Canadian dollar. That was the autumn of 2008. Chan calls the Canadian dollar a commodity currency (Chan, 2013, p. 44), which fits a fall in it that autumn, though nothing here tests the link. The linear rule was short the US dollar on all 69 days of the fall.

That is the third of the cautions Chan names: “an unlimited amount of capital may be needed” because nothing caps the position (Chan, 2013, p. 50). The rule’s largest short came on 2008-10-10, inside the fall, when the close stood 4.12 moving standard deviations above its average and the position was −4.12. The close rose another 10.4 percent by 2008-10-27, but the moving deviation widened with it, so the short eased to −3.83. The position is largest when the close stands furthest above its average in deviations, and here that was inside the move against it. Its largest long, 3.04, came on 2009-05-29.

Most of the loss came in 2008, which ended with the P&L at −0.2552, and the three years and three months after it added 0.3693. Over the 1,101 days the rule holds a position, it is short on 488 and long on 613.

## Lesson 5: the trade’s lookback came from the closes it traded

Chan names three cautions (Chan, 2013, pp. 49–50).

1. **No transaction costs.**
2. **A look-ahead.**
3. **The unlimited capital of Lesson 4.**

The look-ahead is that the 115 days are the half-life of the same 1,216 closes the rule trades. A trader starting in January 2008 could not have known the half-life of a series that runs to March 2012.

Later in the chapter Chan makes a different claim about the same choice. Setting the lookback to the half-life means the rule “has no parameters to optimize”, since the half-life is “a quantity that depends on the properties of the price series itself” (Chan, 2013, p. 60). Both statements are true. Nothing was tuned on the P&L, so there is no search to correct for, and the half-life was still read from the days being traded. A replication that avoids the look-ahead has to measure the half-life on earlier days than it trades.

The half-life also limits what the trade can show. Chan warns that a λ very close to zero, which means a very long half-life, leaves a strategy unable to “complete many round-trip trades” (Chan, 2013, p. 47). At 115 days, the 1,216 closes span 10.6 half-lives, so the whole sample holds about ten stretches long enough for a distance from the mean to halve. That is little evidence, and it assumes the reversion is real. The tests could not reject a random walk, which has no half-life at all, so the 115 days are an estimate from a series that may not revert. The [post on Chan’s stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) shows, for a currency rate with a 141.6-day half-life, how slow reversion makes the linear rule hard to size. For comparison, the three-ETF portfolio of Example 2.7 has a half-life of 23 days, “considerably shorter than the 115 days for USD.CAD” (Chan, 2013, p. 58), which the [post on the Johansen test](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) reproduces.

So the result is exploratory. The reproduction checks the arithmetic and not whether the trade would pay. It shows that every figure but H follows from Chan’s closes and his script, and that the trade’s one claim survives on the days that set its lookback.

## What this replication cannot say

Three questions are beyond it.

1. **What computed the book’s 0.49.** No copy of `genhurst` found gives it on the closes the script’s comments match, and those comments record no value for it. Six of the ten later start days give it, and nothing public shows which run the book’s figure came from.
2. **Whether Example 2.5 would pay.** It carries the look-ahead, charges no transaction cost, and holds a position that grows without limit as the close strays, all of which Chan names. Its P&L is not a return on capital, so it has no annual return or Sharpe ratio to judge it by.
3. **Anything about USD.CAD after March 2012.** Every figure is exploratory, on a sample Chan chose.

## What this means for a trader

One habit for each lesson.

1. **Match the script before trusting the data.** When the original data file cannot be compared, several statistics from separate calculations landing every digit are the next best check that the data is the same.
2. **Name the toolbox.** Two implementations of one test can differ by a row of sample, so a port should say which one produced a figure.
3. **Measure the noise before chasing a figure that misses.** When every available implementation misses a printed number, record the miss, measure how far the statistic moves by chance, and check whether the conclusion still stands.
4. **Read the drawdown beside the P&L.** A positive total can hide a fall more than five times its size, and an uncapped position can be at its largest inside the move against it.
5. **Fit the lookback on earlier days than the trade.** A half-life measured on the traded sample is a look-ahead, however principled the choice.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 2.1 to 2.5, with pages 39, 41, 42, 44, 45, 46, 47, 48, 49, 50, 58 and 60 cited. The page numbers are the 2013 print edition’s, ISBN 9781118460146, found by searching each quoted sentence in Google Books’ preview on 2026-10-11.
2. `stationarityTests.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. LeSage, J. P. The jplv7 Econometrics Toolbox for MATLAB, `adf.m` and `ztcrit.m`.
4. Aste, T. `genhurst.m`, the generalized Hurst exponent, MATLAB File Exchange, dated 2013-01-30.
5. Lo, A. W., and MacKinlay, A. C. (1988). Stock market prices do not follow random walks: evidence from a simple specification test. *Review of Financial Studies*, 1(1), 41–66.

*Not investment advice. Code: [the five examples](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_mean_reversion.py), [the three toolbox tests](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationarity_tests.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/usdcad_mean_reversion_figures.py), with the checks behind [the examples’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_mean_reversion.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_usdcad_mean_reversion_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its Kindle location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-22-the-stationarity-tests-on-usdcad-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
