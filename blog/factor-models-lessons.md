# Three of Chan’s four factor-model printouts reproduce, and the round-off he blames is a second strategy

*Chan’s 2 and 4 percent come from two methods, not round-off. The factor momentum his strategy assumes held for the market factor and not for WML, on too few months to tell either from noise.*

## Why a factor model has to persist to trade

A factor model explains a stock’s return by a few common drivers, such as the market as a whole, small companies against large ones, or recent winners against recent losers. Each driver has a return of its own each period, called the factor return, and each stock has a sensitivity to it, called its exposure. The fit is contemporaneous. It explains this month’s returns with this month’s factor returns, so on its own it says nothing about next month.

Ernest Chan’s *Quantitative Trading* names the bridge from explanation to trading. “Often factor returns are more stable than individual stock returns”, he writes. They “exhibit stronger serial autocorrelations than individual stock’s returns”, and in other words they “have momentum” (Chan, 2021, p. 162). If a factor’s return this period predicts its return next period, a model can carry this period’s factor returns forward and rank the stocks on what they imply.

Example 7.4 is built on that assumption. It takes five statistical factors from a year of returns on the S&P 600, assumes, in Chan’s words, that the factor returns “remain constant from the current time period to the next”, and buys the stocks with the highest expected returns (p. 164). He reports 2 percent a year from the MATLAB program and 4 percent from the Python and R, before costs, and calls the difference “essentially round off errors” (p. 164).

This repository ran every printout of Example 7.4 it could run on Chan’s own file, read the one it could not, and separately built the two factors in Chan’s list that need only prices, to test whether their returns persist. Six lessons follow. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

Every result below is **exploratory**. Reproducing a printed figure, or testing a claim from the book, tests a hypothesis Chan chose rather than one written down here in advance. It says whether his numbers reproduce on his file, and nothing about whether factor models earn money today.

## How Example 7.4 and the two factors work

### Example 7.4, the statistical factor model

Most factor models name their factors in advance. A statistical factor model takes them from the returns themselves, by principal component analysis, which finds the few directions in which a set of stocks moves together most (p. 163). Example 7.4 does this every day.

1. Take the last 252 trading days of returns on each stock.
2. Find five statistical factors by principal component analysis.
3. Predict each stock’s return on the assumption that the factor returns persist.
4. Buy the 50 stocks predicted highest and short the 50 predicted lowest, and charge no cost.

The file is Chan’s `IJR_20080114.mat`, the 600 members of the S&P 600 as he saved them on 2008-01-15, spanning 2004-01-15 to 2008-01-14, 1,006 trading days of split-adjusted closes. Every printout loads it.

### The two factors that need only prices

Two of the factors Chan’s section names can be built from prices alone, and this repository built both.

1. **MKT, the market factor.** Chan names “the return of the market” as the first of Fama and French’s three factors (p. 160). Here it is SPY’s return from one month-end to the next, less that month’s three-month Treasury bill rate divided by 12. Chan’s words name only the return of the market. Subtracting the bill follows Kenneth French’s published market factor, so that step comes from French rather than from Chan.
2. **WML, winners minus losers.** Chan defines it as a portfolio that buys stocks “that previously had positive returns” and shorts those “that previously had negative returns” (p. 162). Here, at each month-end, a stock is a winner if its return from 12 months back to 1 month back was positive and a loser if it was negative. Each leg is equally weighted and held one month. Skipping the latest month follows French’s momentum factor. Chan names no lookback.

Both run on two more of Chan’s files and one public series.

1. `SPX_20071123.mat`, the 500 members of the S&P 500 as he saved them on 2007-11-24, spanning 1999-11-24 to 2007-11-23.
2. The SPY column of his `example6_2.xls`, saved 2008-01-29.
3. The three-month Treasury bill rate, TB3MS, downloaded on 2026-09-30 from FRED, the St. Louis Fed’s data service.

The month-ends are the file’s rows whose next row falls in another month, which is Chan’s own rule, and there are 96 of them. The first formation needs 12 month-ends of history behind it, so 83 holding months remain, from December 2000 to October 2007. A stock enters a month only if it has a close at every month-end the formation reads, which leaves 442 to 494 stocks at each formation.

**The statistic** is each series’ lag-1 autocorrelation, the correlation of each month’s return with the month before. Chan’s “individual stock’s returns” stand here as the median of the 446 stocks with a return in all 83 months. A stock can hold a return in every month and still miss an early formation for want of its year of history, which is how the 446 can exceed the fewest eligible.

**Which edition says what.** The first edition (2009) prints Example 7.4 in MATLAB, cited here by script as `example7_4.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror. The revised edition (2021) prints it in MATLAB, Python and R on pp. 163 to 167. This post also cites its MATLAB and Python through public reposts, pinhaocheng/epchan-quant_trading_MATLAB_codes at `7430b84` and pinhaocheng/epchan-quant_trading_Python_codes at `5fcab61`, and reads its R from the pages alone. Page numbers here are the revised edition’s. This repository did not check whether the first edition carries the sentences quoted above from p. 162.

## Lesson 1: three of the four printouts reproduce, and the fourth prints another program’s figures

Here is every figure the four printouts show, at the precision each prints it, beside whether this repository’s run of that printout lands on it. Each row is an **exploratory** reproduction.

```math
\begin{array}{l|r|l}
\text{Printout} & \text{Printed} & \text{Run here} \\ \hline
\text{MATLAB, first edition, annual mean} & -1.8099 & \text{reproduces} \\
\text{MATLAB, revised, annual mean return} & 0.020205 & \text{reproduces} \\
\text{MATLAB, revised, Sharpe ratio} & 0.211120 & \text{reproduces} \\
\text{Python, revised, annual mean return} & 0.04052422056844459 & \text{within } 10^{-15} \\
\text{Python, revised, annual standard deviation} & 0.07002908500498846 & \text{within } 10^{-15} \\
\text{Python, revised, Sharpe ratio} & 0.5786769963588398 & \text{within } 10^{-15} \\
\text{R, revised, the same three lines} & \text{the Python's, digit for digit} & \text{does not reproduce}
\end{array}
```

The revised MATLAB prints its figures on p. 164, the Python on p. 165 and the R on p. 167. Three points sit behind the table.

1. **The first edition’s figure is in other units.** Its daily figure sums 100 positions of ±1 and never divides by capital. So −1.8099 is a sum over positions, not a return on capital, and it cannot be set beside the revised edition’s 2 percent. The [equity seasonals post](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) met the same thing in Example 7.7.
2. **Neither reading of the R’s code reaches the figures it prints.** The R prints the Python’s three figures to the last digit, but its code differs from the Python’s. It buys 52 stocks rather than 50, among other differences. Read without filling gaps, it gives 0.0401, 0.0797 and 0.5038. Read with gaps filled by the last price, it gives 0.0426, 0.0802 and 0.5319. The R also loads a helper file, `calculateReturns.R`, that the book does not print, and this repository has no R runtime, so the R row is a reading of the code rather than a run of it. [Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) will run it.
3. **The revised Sharpe ratio needs a helper from another book.** The revised MATLAB computes its standard deviation with a helper, `smartstd`, and Chan’s two books ship two versions of it. The one from his *Algorithmic Trading* reproduces the printed 0.211120, and the revised repost carries that one. The one from this book’s first edition gives 0.2441.

## Lesson 2: Chan’s round-off is a second strategy

Chan’s explanation of 2 against 4 percent is round-off, which would mean one method computed twice with slightly different arithmetic. The two programs are two methods, and one fact about least squares shows why.

The revised Python regresses each stock’s returns over the year, rᵢₜ, on an intercept and the five factor series. A least-squares fit with an intercept leaves residuals that sum to zero, so each stock’s fitted values sum to its returns, whatever the factors are:

```math
r_{i,t} = a_i + \sum_{k=1}^{5} b_{ik} f_{k,t} + e_{i,t}, \quad \sum_t e_{i,t} = 0 \;\Rightarrow\; \sum_t \hat r_{i,t} = \sum_t r_{i,t}
```

1. **The Python never uses its factors.** It ranks the stocks on the sum of the fitted values, which by the line above is each stock’s own return over the year. So it is a momentum strategy on single stocks, and its book, the set of positions it holds each day, is identical on every day to a ranking with the principal component analysis left out.
2. **The revised MATLAB does use them.** It fits today’s cross-section of returns on the stocks’ factor exposures, with an intercept, and ranks on the fitted values. That is a factor model in the sense the text describes.
3. **The two books barely overlap.** The printed Python buys 49 stocks, because its index range skips the top-ranked one, while the MATLAB buys 50. So the comparison gives the Python 50 longs as well. On the 752 days both hold positions, the Python’s book matches the MATLAB’s on 0 of them and differs in at least 125 positions on each. On an average day, 13.83 percent of the MATLAB’s names sit on the same side of the printed Python’s book, and 14.14 percent once the Python also buys 50. Round-off would leave two books of the same size identical every day.
4. **Three bookkeeping choices each pull the Python’s figure down toward the MATLAB’s.** Change any one and the Python’s figure rises.

```math
\begin{array}{l|r|r}
\text{Revised Python} & \text{Annual mean return} & \text{Sharpe ratio} \\ \hline
\text{As printed} & 0.04052422056844459 & 0.5786769963588398 \\
\text{Buying the top 50, not the 49 ranked second to 50th} & 0.0414 & 0.5908 \\
\text{Averaging over its 751 trading days, not all 1,006} & 0.0543 & 0.6699 \\
\text{Keeping the first day's book, which its code zeroes} & 0.0417 & 0.5945 \\ \hline
\text{Revised MATLAB, as printed} & 0.020205 & 0.211120
\end{array}
```

So the gap between 2 and 4 percent is method, an **exploratory** verdict on Chan’s file. The bookkeeping narrows the gap rather than causing it.

[Entry 13 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-13-the-pca-factor-model-chans-quantitative-trading) wrote that round-off criterion after measuring the overlap, and Lesson 5 says what that costs.

## Lesson 3: the momentum the strategy assumes held for the market factor and not for the momentum factor

Chan’s claim is that factor returns “often” autocorrelate more strongly than single stocks. Before any autocorrelation was computed, [issue 22](https://github.com/l3a0/quantitative-trading/issues/22) fixed a criterion for each factor on its own. The claim holds for a factor when its lag-1 autocorrelation is above 0 and above the median stock’s. On the same day, still before any autocorrelation was computed, the repository’s owner ruled that each factor carries its own verdict and that no combined verdict is drawn from the two.

```math
\begin{array}{l|r|r|l}
\text{Series, 83 months} & \text{Lag-1 autocorrelation} & \text{Percentile among the stocks} & \text{Claim} \\ \hline
\text{MKT} & 0.0675 & 80.7175 & \text{holds} \\
\text{WML} & -0.1099 & 27.8027 & \text{does not hold} \\ \hline
\text{446 stocks, lower quartile} & -0.1198 & & \\
\text{446 stocks, median} & -0.0392 & & \\
\text{446 stocks, upper quartile} & 0.0402 & &
\end{array}
```

Each verdict is **exploratory** and stands on its own.

1. **For MKT, the claim that factors “often” autocorrelate more strongly holds.** MKT’s 0.0675 is above 0 and above the median stock’s −0.0392. It sits above 360 of the 446 stocks.
2. **For WML, the claim that factors “often” autocorrelate more strongly does not hold.** WML’s −0.1099 is below 0 and below the median stock. It sits above only 124 of the 446 stocks, so on this file the momentum factor is less persistent than most single stocks.

The quartiles are by linear interpolation between the two nearest stocks.

**What was not tested.** Entry 14 tested the claim Example 7.4 rests on. It did not test Example 7.4’s own factors. Those are five statistical factors, on daily returns, on the S&P 600 file. MKT and WML are named factors, on monthly returns, on the S&P 500 file. And by Lesson 2 the revised Python rests on each stock’s own momentum over the year, not on any factor’s momentum. So neither verdict is a verdict on Example 7.4. [Issue 286](https://github.com/l3a0/quantitative-trading/issues/286) will test Example 7.4’s own factor returns.

## Lesson 4: a verdict can follow the declared criterion and still rest on almost nothing

The criterion asks two questions about each autocorrelation, whether it is above 0 and whether it is above the median stock. It does not ask whether 83 months can tell the answer from chance.

A series with no autocorrelation at all still produces a nonzero estimate from a finite sample. With 83 months, the estimate falls inside ±1.96/√83 about 95 percent of the time:

```math
\pm \frac{1.96}{\sqrt{83}} = \pm 0.2151
```

Both factors sit inside that band. So 83 months cannot tell MKT’s 0.0675 from no persistence at all, and the same holds for WML’s −0.1099. The verdict for MKT is what the declared criterion says, and the band says how little it rests on.

The figure below draws all of it at once. The curve is the 446 stocks’ autocorrelations, sorted, with the height at each point giving the share of stocks at or below it. Each factor’s line meets the curve at its percentile, and the shaded band is ±0.2151.

![A step curve of the 446 stocks’ lag-1 autocorrelations over 83 months, rising to 1. A shaded band covers −0.2151 to 0.2151. A dashed vertical line for WML at −0.1099 meets the curve at the 27.8027th percentile, a solid line for MKT at 0.0675 meets it at the 80.7175th, and a dotted line marks the median stock at −0.0392. Both factor lines and the median sit inside the band. The title calls the test exploratory, and the note says the stocks and WML are survivors while MKT, from SPY, is not.](../docs/figures/factor_momentum_autocorrelations.png)

*Both factors and the median stock sit inside the band where a series with no autocorrelation lands 95 percent of the time.*

The two factors’ average returns are just as uncertain, and they decide nothing. MKT earned 0.0185 a year over the bill and WML 0.0241. A t-statistic divides an average by how far it would wander by chance, and values near 0 are what luck alone produces. MKT’s is 0.3660 and WML’s 0.4505, with no correction for autocorrelation. Each annual figure is the mean monthly return times 12.

## Lesson 5: fix the rule before the number

The order in which a rule and its number arrive decides what a verdict can claim. The two entries arrived in opposite orders.

1. **Entry 14 fixed every rule first.** The criterion, the monthly frequency, the one-month skip and the comparison set were written on [issue 22](https://github.com/l3a0/quantitative-trading/issues/22) before any autocorrelation was computed, and the owner’s ruling that each factor stands alone came before too. So neither verdict can have been chosen to fit the result. The cost is that a daily autocorrelation was never tried after the monthly one was seen.
2. **Entry 13 wrote its round-off criterion after measuring.** The rule that round-off would leave books of the same size identical every day was written on [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the 0 of 752 was in hand, and the entry names that cost. A rule written after its number cannot show on its own that it was not fitted to that number.

## Lesson 6: every figure that touches the stocks is about survivors

Both stock files hold their index as it stood on the last day each file reaches, carried backwards. A company that left the S&P 500 in 2003 is not in a file saved in 2007. The [post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches what that does in general. Here survivorship reaches three things, and the way the file was built reaches a fourth.

1. **Example 7.4’s books, all of them.** Every printout ranks and trades only the 600 stocks still in the S&P 600 on 2008-01-14.
2. **WML and the median stock.** The loser leg lacks the losers that fell out of the index, which pushes WML down. The winner leg lacks past winners that later collapsed out of it, which pushes WML up. Which of the two dominates is not measured, so this post does not guess a direction.
3. **Where the median sits.** The median stock’s autocorrelation is −0.0392, below 0, so on this file a factor above 0 is also above the median stock. That is a fact about this panel of survivors, not about single stocks in general.
4. **One symbol holds two price histories.** PMC in the S&P 600 file closes, goes missing for 851 days, and resumes as a different price history under the same ticker. The three printouts that run fill the gap with the last price, so when the second history begins on 2007-08-01 the file shows one day’s return of 1.8654. Without PMC, the first edition gives −1.8014, the revised MATLAB 0.0180 at a Sharpe ratio of 0.1869, and the revised Python 0.0408 at 0.5851.

MKT is the exception. It reads SPY, which held the index as it stood each day, so it carries no survivorship.

## What this replication cannot say

Seven things.

1. **What Example 7.4 earned on the S&P 600 as it stood each day.** [Issue 269](https://github.com/l3a0/quantitative-trading/issues/269) reruns it on a universe without survivorship, which waits on data.
2. **What the printed R computed.** Without its helper file and an R runtime, the R row is a reading. [Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it.
3. **What costs would take.** Every printout charges none, and the books turn over daily.
4. **What survivorship does to WML.** [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) waits on a panel of the index as it stood each day.
5. **Whether the factors persist at another frequency.** Only monthly returns were computed, by the rule on [issue 22](https://github.com/l3a0/quantitative-trading/issues/22).
6. **Whether French’s published factors agree, and what his size and value factors, SMB and HML, do.** [Issue 274](https://github.com/l3a0/quantitative-trading/issues/274) records French’s library as a vintage, and [issue 273](https://github.com/l3a0/quantitative-trading/issues/273) carries the two factors that need company size and book value.
7. **Whether Example 7.4’s own factor returns have momentum.** Nothing here tested them. [Issue 286](https://github.com/l3a0/quantitative-trading/issues/286) will.

## What this means for a trader

Three habits follow from the lessons above.

1. **Run every printout of a published strategy before trusting the author’s account of why they differ.** Chan’s round-off turned out to be a factor model in one language and single-stock momentum in another.
2. **Check what a strategy’s assumption rests on before trading it, and test it under a rule written first.** On Chan’s S&P 500 file the market factor passed the declared test and the momentum factor failed it, both inside the range of no persistence, and neither is one of Example 7.4’s own factors.
3. **Read a verdict beside the band that says how much the sample can tell.** Both autocorrelations sit inside the range a series with no persistence produces 95 times in 100.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Example 7.4, cited by its MATLAB script, `example7_4.m`.
- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Cited for its `smartstd`.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 160, 162, 163 and 164, and Example 7.4 at pp. 163 to 167.
- Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. Cited by Chan (2021, p. 160) for the three-factor model.
- French, K. R. *Data Library*. Tuck School of Business, Dartmouth College. The source of the market factor’s step over the bill rate and the momentum factor’s skip of the latest month.

*Not investment advice. Code: [the PCA factor model](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor.py), [the two factors](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/momentum_factor.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/momentum_factor_figures.py), with the checks behind [the model’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor.py), [the factors’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_momentum_factor.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_momentum_factor_figures.py), and the replication log’s entries for [the factor model](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-13-the-pca-factor-model-chans-quantitative-trading) and [the two factors](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-14-the-market-and-momentum-factors-chans-quantitative-trading).*
