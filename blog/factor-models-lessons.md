# Three of Chan’s four factor-model printouts reproduce, and the round-off he blames is a second strategy

*Chan’s 2 and 4 percent come from two methods, not round-off. His claim that factor returns have momentum held for the market factor and four of Example 7.4’s five factors, and not for the momentum factor, none of them clear of noise.*

## Why a factor model has to persist to trade

A factor model explains a stock’s return by a few common drivers, such as the market as a whole, small companies against large ones, or recent winners against recent losers. Each driver has a return of its own each period, called the factor return, and each stock has a sensitivity to it, called its exposure. The fit explains this month’s returns with this month’s factor returns, so on its own it says nothing about next month.

Ernest Chan’s *Quantitative Trading* names the bridge from explanation to trading. He writes that “often factor returns are more stable than individual stock returns”. They “exhibit stronger serial autocorrelations than individual stock’s returns”, and in other words they “have momentum” (Chan, 2021, p. 162). If a factor’s return this period predicts its return next period, a model can carry this period’s factor returns forward and rank the stocks on what they imply.

Example 7.4 is built on that assumption. It takes five statistical factors from a year of returns on the S&P 600, assumes, in Chan’s words, that the factor returns “remain constant from the current time period to the next”, and buys the stocks with the highest expected returns (p. 164). In the revised edition he reports 2 percent a year from the MATLAB program and 4 percent from the Python and R, before costs, and calls the difference “essentially round off errors” (p. 164).

This repository ran every printout of Example 7.4 it could run on Chan’s own data file, and read the one it could not. It then tested whether factor returns persist, on the two factors Chan names that can be built from prices alone and on the five statistical factors Example 7.4 fits for itself. Six lessons follow. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

Every result below is **exploratory**. Reproducing a printed figure, or testing a claim from the book, tests a hypothesis Chan chose rather than one written down here in advance. It says whether his numbers reproduce on his file, and nothing about whether factor models earn money today.

## How Example 7.4 and the two factors work

### Example 7.4, the statistical factor model

Most factor models name their factors in advance. A statistical factor model takes them from the returns themselves, by principal component analysis, which finds the few directions in which a set of stocks moves together most (p. 163). Example 7.4 does this every day.

1. Take the last 252 trading days of returns on each stock.
2. Find five statistical factors by principal component analysis.
3. Predict each stock’s return on the assumption that the factor returns persist.
4. Buy the 50 stocks predicted highest and short the 50 predicted lowest, and charge no cost.

**Which edition says what.** Example 7.4 is printed four times, and this post calls each program listing, with the figures it prints, a printout.

1. The first edition (2009) prints it in MATLAB, cited here by script as `example7_4.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror.
2. The revised edition (2021) prints it in MATLAB, also cited through the public repost pinhaocheng/epchan-quant_trading_MATLAB_codes at `7430b84`.
3. The revised edition prints it in Python, also cited through pinhaocheng/epchan-quant_trading_Python_codes at `5fcab61`.
4. The revised edition prints it in R, read here from the pages alone.

The revised edition prints its three on pp. 163 to 167, and page numbers here are the revised edition’s. This repository did not check whether the first edition carries the sentences this post quotes from p. 162.

The file is Chan’s `IJR_20080114.mat`, the 600 members of the S&P 600 as he saved them on 2008-01-15, spanning 2004-01-15 to 2008-01-14, 1,006 trading days of split-adjusted closes. Every printout loads it.

### The two factors that need only prices

Two of the factors Chan’s section names can be built from prices alone, and this repository built both.

1. **MKT, the market factor.** Chan names “the return of the market” as the first of Fama and French’s three factors (p. 160). Here it is SPY’s return from one month-end to the next, less that month’s three-month Treasury bill rate divided by 12. Chan’s words name only the return of the market. Subtracting the bill follows Kenneth French’s published market factor, so that step comes from French rather than from Chan.
2. **WML, winners minus losers.** Chan defines it as a portfolio that buys stocks “that previously had positive returns” and shorts those “that previously had negative returns” (p. 162). Here, at each month-end, a stock is a winner if its return from 12 months back to 1 month back was positive and a loser if it was negative. Each leg is equally weighted and held one month. Skipping the latest month follows French’s momentum factor. Chan names no lookback. WML is the momentum factor. The momentum Example 7.4 assumes is a different thing, a factor’s return persisting from one period to the next, and the lessons below test it on WML as on every other factor.

Between them the two factors read two more of Chan’s files and one public series.

1. `SPX_20071123.mat`, the 500 members of the S&P 500 as he saved them on 2007-11-24, spanning 1999-11-24 to 2007-11-23.
2. SPY’s dividend-adjusted close from his `example6_2.xls`, saved 2008-01-29.
3. The three-month Treasury bill rate, TB3MS, downloaded on 2026-09-30 from FRED, the St. Louis Fed’s data service.

WML and the stocks come from the first, and MKT’s returns from the other two.

The month-ends are the S&P 500 file’s rows whose next row falls in another month, which is Chan’s own rule, and there are 96 of them. The first month-end that picks winners and losers needs 12 month-ends of history behind it, and the last month-end has no month after it to hold, so 83 holding months remain, from December 2000 to October 2007. A stock enters a month only if it has a close at every month-end from 12 before the pick to the end of the month held, which leaves 442 to 494 stocks each month.

**The statistic** is each series’ lag-1 autocorrelation, the correlation of each month’s return with the month before. Chan’s “individual stock’s returns” stand here as the median of the 446 stocks with a return in all 83 months. The 446 can exceed 442, the fewest stocks in any month, because a stock can have a return in all 83 months and still be left out of an early month for want of a full year of closes before it.

## Lesson 1: three of the four printouts reproduce, and the fourth prints another program’s figures

Here is every figure the four printouts show, at the precision each prints it, beside what this repository’s run of that printout gives. Each comparison is an **exploratory** reproduction. The revised edition’s returns are fractions of capital, so 0.020205 is Chan’s 2 percent and 0.04052422056844459 his 4 percent. The Sharpe ratio is the annual mean return divided by its annual standard deviation, with no risk-free rate subtracted.

The run here reproduces all three of the MATLAB’s figures.

```math
\begin{array}{l|r}
\text{MATLAB printout} & \text{Printed} \\ \hline
\text{First edition, annual mean} & -1.8099 \\
\text{Revised, annual mean return} & 0.020205 \\
\text{Revised, Sharpe ratio} & 0.211120
\end{array}
```

The run of the revised Python lands within 10⁻¹⁵ of each of its three.

```math
\small\begin{array}{l|r}
\text{Revised Python, annual} & \text{Printed} \\ \hline
\text{Mean return} & 0.04052422056844459 \\
\text{Standard deviation} & 0.07002908500498846 \\
\text{Sharpe ratio} & 0.5786769963588398
\end{array}
```

The R prints the Python’s three figures digit for digit, and this repository’s reading of the R does not reproduce them.

The revised MATLAB prints its figures on p. 164, the Python on p. 165 and the R on p. 167. Three points sit behind these figures.

1. **The first edition’s figure is in other units.** Its daily figure sums 100 positions of ±1 and never divides by capital. So −1.8099 is a sum over positions, not a return on capital, and it cannot be set beside the revised edition’s 2 percent. The [equity seasonals post](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) met the same thing in Example 7.7.
2. **Neither of two readings of the R’s code reaches the figures it prints.** The R prints the Python’s three figures to the last digit, but its code differs from the Python’s. It buys 52 stocks where the Python buys 49, among other differences. Its line for missing prices can be read two ways, so this repository coded the R in Python both ways. Leaving each missing price empty gives 0.0401, 0.0797 and 0.5038. Filling it with the last price gives 0.0426, 0.0802 and 0.5319. The R also loads a helper file, `calculateReturns.R`, that the book does not print, and this repository has no R runtime, so the R’s figures here come from a reading of its code rather than a run of it.
3. **The revised Sharpe ratio needs a helper from another book.** The revised MATLAB computes its standard deviation with a helper, `smartstd`, and Chan’s two books ship two versions of it. The one from his *Algorithmic Trading* reproduces the printed 0.211120, and the revised repost carries that one. The one from this book’s first edition gives 0.2441.

## Lesson 2: Chan’s round-off is a second strategy

Chan’s explanation of 2 against 4 percent is round-off, which would mean one method computed twice with slightly different arithmetic. The two programs are two methods, and one fact about least squares shows why.

The revised Python regresses each stock’s returns over the year, rᵢₜ, on an intercept and the five factor series. A least-squares fit with an intercept leaves residuals that sum to zero, so the sum of each stock’s fitted values equals the sum of its returns, whatever the factors are:

```math
\begin{gathered}
r_{i,t} = a_i + \sum_{k=1}^{5} b_{ik} f_{k,t} + e_{i,t} \\
\sum_t e_{i,t} = 0 \;\Rightarrow\; \sum_t \hat r_{i,t} = \sum_t r_{i,t}
\end{gathered}
```

![An animated whiteboard sketch titled “The residuals cancel, so the sums match”, drawn stroke by stroke. It is schematic and carries no figures from the run. A grey day axis is labelled “one stock’s year (schematic)”, and twelve black bars, some above it and some below, are labelled “daily returns”. Beside each bar a brown dot marks one of the “fitted values”. The dots wander up and down from day to day rather than following a straight line. A short tick joins each dot to the end of its bar. It is green where the return sits above the dot, as “+ return above the fit” says, and red where it sits below, as “− return below the fit” says. A note reads “with an intercept, the residuals sum to 0”. To the right, a black bar marked “Σ returns” and a brown bar marked “Σ fitted” stand at the same height, joined by “=”. Last, four black bars, each with a brown dot at its end, shrink from top to bottom under “four stocks, ranked”, with the notes “rank on Σ fitted = rank on Σ returns” and “momentum, no factors needed”.](../docs/figures/factor_models_residuals_cancel.gif)

1. **The Python never uses its factors.** It ranks the stocks on the sum of the fitted values, which by the line above is each stock’s own return over the year. So it is a momentum strategy on single stocks, and the positions it holds each day are identical to those a ranking with the principal component analysis left out would hold.
2. **The revised MATLAB does use them.** It regresses today’s returns across the stocks on their factor exposures, with an intercept, and ranks on the fitted values. That is a factor model in the sense the text describes.
3. **The two programs’ positions barely overlap.** The printed Python buys 49 stocks, because its index range skips the top-ranked one, while the MATLAB buys 50. On an average day, 13.83 percent of the MATLAB’s names sit on the same side in the printed Python, and 14.14 percent once the Python also buys 50. Even at 50 longs each, the two sets of positions are identical on 0 of the 752 days both hold positions, and on each of those days at least 125 of the 600 stocks hold a different position in the two. Round-off would leave two sets of positions of the same size identical every day.
4. **Three bookkeeping choices each pull the Python’s figures down toward the MATLAB’s.** The printed Python buys the 49 stocks ranked second to 50th rather than the top 50. It averages its daily returns over all 1,006 trading days rather than the 751 on which it trades. Its code also zeroes the first day’s positions. Change any one of the three and the Python’s annual mean return rises from 0.04052422056844459, and its Sharpe ratio from 0.5786769963588398. The revised MATLAB prints 0.020205 and 0.211120.

```math
\begin{array}{l|r|r}
\text{Change} & \text{Mean} & \text{Sharpe} \\ \hline
\text{Top 50, not 49} & 0.0414 & 0.5908 \\
\text{751 days, not 1,006} & 0.0543 & 0.6699 \\
\text{First day kept} & 0.0417 & 0.5945
\end{array}
```

So the gap between 2 and 4 percent is method, an **exploratory** verdict on Chan’s file. The bookkeeping narrows the gap rather than causing it.

[Entry 13 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-13-the-pca-factor-model-chans-quantitative-trading) wrote down the test above, that round-off would leave two sets of positions of the same size identical every day, only after measuring the overlap. Lesson 5 says what that costs.

## Lesson 3: Chan’s factor-momentum claim held for the market factor and four of Example 7.4’s five factors, and not for the momentum factor

Chan’s claim is that factor returns “often” autocorrelate more strongly than single stocks. This repository tested it first on the two factors that need only prices, using monthly returns. It then tested it on the five factors Example 7.4 fits for itself, using daily returns.

### MKT and WML, month to month

Before any autocorrelation was computed, this repository fixed a criterion for each factor on its own, as [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-14-the-market-and-momentum-factors-chans-quantitative-trading) records. The claim holds for a factor when its lag-1 autocorrelation is above 0 and above the median stock’s. On the same day, still before any autocorrelation was computed, the repository’s owner ruled that each factor carries its own verdict and that no combined verdict is drawn from the two. A factor’s percentile is the share of the 446 stocks whose autocorrelation is below the factor’s.

```math
\begin{array}{l|r|r}
\text{83 months} & \text{MKT} & \text{WML} \\ \hline
\text{Autocorrelation} & 0.0675 & -0.1099 \\
\text{Percentile} & 80.7175 & 27.8027 \\
\text{Claim} & \text{holds} & \text{does not hold}
\end{array}
```

The 446 stocks’ autocorrelations have a lower quartile of −0.1198, a median of −0.0392 and an upper quartile of 0.0402, with each quartile by linear interpolation between the two nearest stocks.

Each verdict is **exploratory** and stands on its own.

1. **For MKT, the claim that factors “often” autocorrelate more strongly holds.** MKT’s 0.0675 is above 0 and above the median stock’s −0.0392. It sits above 360 of the 446 stocks.
2. **For WML, the claim that factors “often” autocorrelate more strongly does not hold.** WML’s −0.1099 is below 0 and below the median stock. It sits above only 124 of the 446 stocks, so on this file the momentum factor is less persistent than most single stocks.

### Example 7.4’s own five factors, day to day

MKT and WML are named factors, on monthly returns, on the S&P 500 file. The five factors Example 7.4 trades on are statistical and re-estimated every day on the S&P 600 file. So this repository tested them too, again under rules fixed before any factor return was computed, and with the owner’s ruling, as for MKT and WML, that each factor stands alone. The [post on Example 7.4’s own factors](https://github.com/l3a0/quantitative-trading/blob/main/blog/pca-factor-momentum-lessons.md) teaches the method in full, and measures what each other way of reading the factors would have given.

Each day’s principal component analysis gives each factor a set of weights across the stocks, and the factor’s return is the weighted sum of that day’s stock returns. The five factors are PC1 to PC5, principal components one to five, in the order each day’s analysis ranks them. PC1 carries the most of the year’s variation in returns, and each later one less. Each day’s weights come from the 252 days of returns that end the day before. A series built from each day’s fresh weights would mix more than persistence into its autocorrelation. The analysis fixes each set of weights only up to its sign, so the next day’s weights may come out flipped. The next day’s weights also come from a window that already holds today’s return. So each day’s weights are applied to that day’s returns and to the next day’s, which makes a pair from one analysis. A flip then changes the sign of both members of the pair together, and neither member’s return is in the window the weights came from. The statistic is an uncentred correlation, the correlation of the 752 pairs computed without subtracting their means first. It reads only each pair’s product and each member’s square, and a flip moves neither. A factor return that keeps one sign from day to day counts as persistent, which is what “remain constant” asks. The same statistic is computed for each of the 579 stocks with a return on every day the pairs read. The claim holds for a factor when its statistic is above 0 and above the median stock’s, and its percentile is the share of the 579 stocks whose statistic is below it.

![An animated whiteboard sketch titled “A sign flip changes both members of a pair”, drawn slowly stroke by stroke. It is schematic and carries no figures from the run. On the left, six black arrows, some up and some down, are labelled “day t’s weights”. Below them two black bars stand up from a grey line, marked “f” and “g”, and a bracket under both reads “one pair: day t, day t+1”. Beside them a green bar stands up for their product, marked “f·g” and “+”. In the middle, the same six arrows are drawn again in red with every direction reversed, labelled “day t+1’s weights, flipped”. Below them a black bar marked “f” stands up and a red bar marked “−g” hangs down. Their product, marked “f·(−g)” and “−”, hangs down in red, with the note “fresh weights each day:” and “the flip reads as a reversal”. On the right, red bars marked “−f” and “−g” both hang down, while their product, a green bar marked “+”, stands up as tall as the first product. “(−f)(−g) = fg” is written above them beside a green check, and the note reads “day t’s flip changes both,” and “so the product stays”. The finished drawing holds for twelve seconds.](../docs/figures/factor_models_sign_flip.gif)

The revised MATLAB’s five factors are the ones tested. By Lesson 2 the Python never uses its factors, and by Lesson 1 the R is read rather than run. The first edition fits each day’s returns on weights chosen from a window that includes that same day, which leaves no fair pair of one day and the next.

```math
\small\begin{array}{l|r|r|l}
\text{Factor} & \text{Correlation} & \text{Percentile} & \text{Claim} \\ \hline
\text{PC1} & 0.0316 & 83.9378 & \text{holds} \\
\text{PC2} & 0.0778 & 95.6822 & \text{holds} \\
\text{PC3} & -0.0189 & 55.0950 & \text{does not hold} \\
\text{PC4} & 0.0305 & 83.4197 & \text{holds} \\
\text{PC5} & 0.0710 & 94.3005 & \text{holds}
\end{array}
```

The median stock’s statistic is −0.0283. The claim that factors “often” autocorrelate more strongly holds for four of the five, and does not hold for PC3, which sits above the median stock but below 0. Each of the five verdicts is **exploratory**, and three things say how little they rest on.

1. **The band.** A series with no persistence still gives a nonzero statistic from a finite sample. Over 752 pairs it lands inside ±1.96/√752 = ±0.0715 about 95 percent of the time, and Lesson 4 draws the same kind of band for the monthly factors. PC2’s 0.0778 is outside it and the other four are inside.
2. **A test across all five.** Each day’s factor return times the next day’s gives one product per pair. A Newey-West t-statistic tests whether those products average above zero. It divides the average by how far it would wander by chance, widened for neighbouring days whose products move together and for days whose products swing wider than others. Its one-sided p-value is the chance that luck alone would give a t that large. Testing five factors at once raises the chance that one looks significant by luck, so the Benjamini-Hochberg procedure, which holds the expected share of false findings among those declared significant to 5 percent, runs across all five. None survives, PC2 included, and no factor’s p-value would pass at 5 percent even alone. The band assumes every day’s product is drawn independently from one distribution and the t does not, which is how PC2 can sit outside the band and still fail the test.
3. **One symbol decides which factor misses and which fall outside the band.** PMC is one ticker in the S&P 600 file that holds two price histories with a gap between them. Filling the gap with the last price joins them into one day’s return of 1.8654, a rise of 186.54 percent, and Lesson 6 gives the details. Without PMC, PC2 falls to −0.0152 and PC3 rises to 0.0139, so the claim would miss PC2 rather than PC3. PC1 at 0.0740 and PC4 at 0.0975 would sit outside the band in place of PC2. PC4’s one-sided p-value of 0.0319 would then pass at 5 percent on its own, but no factor would survive the test across all five.

Every one of these figures is about survivors, as Lesson 6 says of the whole S&P 600 file. None of them says how much of the revised MATLAB’s 2 percent the factors’ momentum earns.

## Lesson 4: a verdict can follow the declared criterion and still rest on almost nothing

The criterion asks two questions about each autocorrelation, whether it is above 0 and whether it is above the median stock. It does not ask whether 83 months can tell the answer from chance.

A series with no autocorrelation at all still produces a nonzero estimate from a finite sample. With 83 months, the estimate falls inside ±1.96/√83 about 95 percent of the time:

```math
\pm \frac{1.96}{\sqrt{83}} = \pm 0.2151
```

Both factors sit inside that band. So 83 months cannot tell MKT’s 0.0675 from no persistence at all, and the same holds for WML’s −0.1099. The verdict for MKT is what the declared criterion says, and the band says how little it rests on.

The figure below draws all of it at once. The curve is the 446 stocks’ autocorrelations, sorted, with the height at each point giving the share of stocks at or below it. Each factor’s line meets the curve at its percentile, and the shaded band is ±0.2151.

![A step curve of the 446 stocks’ lag-1 autocorrelations over 83 months, rising to 1. A shaded band covers −0.2151 to 0.2151. A dashed vertical line for WML at −0.1099 meets the curve at the 27.8027th percentile, a solid line for MKT at 0.0675 meets it at the 80.7175th, and a dotted line marks the median stock at −0.0392. A thin grey line marks zero. Both factor lines and the median sit inside the band. The title calls the test exploratory, and the note says the stocks and WML are survivors while MKT, from SPY, is not.](../docs/figures/factor_momentum_autocorrelations.png)

*Both factors and the median stock sit inside the band where a series with no autocorrelation lands 95 percent of the time.*

The criterion does not use the two factors’ average returns, and those are just as uncertain. MKT earned 0.0185 a year over the bill, and WML, which has no bill leg, earned 0.0241, each the mean monthly return times 12. A t-statistic divides an average by how far it would wander by chance, and values near 0 are what luck alone produces. MKT’s is 0.3660 and WML’s 0.4505, with no correction for autocorrelation.

## Lesson 5: fix the rule before the number

The order in which a rule and its number arrive decides what a verdict can claim. Two entries in the replication log arrived in opposite orders, Entry 13 for the factor model of Lessons 1 and 2 and Entry 14 for MKT and WML in Lesson 3.

1. **Entry 14 fixed every rule first.** The criterion, the monthly frequency, the one-month skip and the comparison set were written down before any autocorrelation was computed, as [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-14-the-market-and-momentum-factors-chans-quantitative-trading) records, and the owner’s ruling that each factor stands alone came before too. So neither verdict can have been chosen to fit the result. The cost is that a daily autocorrelation of MKT and WML was never tried.
2. **Entry 13 wrote its round-off criterion after measuring.** The rule that round-off would leave two sets of positions of the same size identical every day was written down after the count of 0 identical days out of 752 was in hand, and the entry names that cost. A rule written after its number cannot show on its own that it was not fitted to that number.

## Lesson 6: every figure that touches the stocks is about survivors

Each stock file holds only the companies in its index on the file’s last day, and gives their prices for the years before. A company that left the S&P 500 in 2003 is not in a file saved in 2007. The [post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches what that does in general. Here survivorship reaches three things, and the way the file was built reaches a fourth.

1. **Example 7.4’s positions, in every printout.** Every printout ranks and trades only the 600 stocks still in the S&P 600 on 2008-01-14.
2. **WML.** The loser leg lacks the losers that fell out of the index, which pushes WML down. The winner leg lacks past winners that later collapsed out of it, which pushes WML up. Which of the two dominates is not measured, so this post does not guess a direction.
3. **Where the median sits.** On the S&P 500 file the median stock’s monthly autocorrelation is −0.0392, and on the S&P 600 file the median daily statistic is −0.0283. Both are below 0, so on either file a factor above 0 is also above the median stock. That is a fact about these files of survivors, not about single stocks in general.
4. **One symbol holds two price histories.** PMC in the S&P 600 file closes, goes missing for 851 trading days, and resumes as a different price history under the same ticker. The three printouts that run fill the gap with the last price, so when the second history begins on 2007-08-01 the file shows one day’s return of 1.8654, a rise of 186.54 percent. Without PMC, the first edition gives −1.8014, the revised MATLAB 0.0180 at a Sharpe ratio of 0.1869, and the revised Python 0.0408 at 0.5851.

MKT is the exception. It reads SPY, which held the index as it stood each day, so it carries no survivorship.

## What this replication cannot say

Six things.

1. **What Example 7.4 earned on the S&P 600 as it stood each day, and whether its factors persist there.** A rerun on a universe without survivorship waits on data.
2. **What the printed R computed.** Without its helper file and an R runtime, the R’s figures here come from a reading rather than a run.
3. **What costs would take.** Every printout charges none, and the positions turn over daily.
4. **What survivorship does to WML.** That needs a file of the index’s members as they stood each day, with their prices, and such a file has to be bought.
5. **Whether the factors persist at another frequency or lag.** MKT and WML were computed on monthly returns, and Example 7.4’s factors on daily returns one day apart, each under rules fixed in advance.
6. **Whether French’s published factors agree, and what his size and value factors, SMB and HML, do.** This repository holds neither French’s library nor the company size and book value those two factors need.

## What this means for a trader

Three habits follow from the lessons above.

1. **Run every printout of a published strategy before trusting the author’s account of why they differ.** Chan’s round-off turned out to be a factor model in one language and single-stock momentum in another.
2. **Check what a strategy’s assumption rests on before trading it, and test it under a rule written first.** On Chan’s S&P 500 file the market factor passed the declared test and the momentum factor failed it, both inside the range of no persistence. On his S&P 600 file four of Example 7.4’s own five factors passed and one failed, none survived a test across all five, and dropping one symbol with two price histories changed which one failed.
3. **Read a verdict beside the band that says how much the sample can tell.** Both monthly autocorrelations sit inside the range a series with no persistence produces 95 times in 100, and the one daily factor outside its band survives no test across all five.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Example 7.4, cited by its MATLAB script, `example7_4.m`.
- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Cited for its `smartstd`.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 160, 162, 163 and 164, and Example 7.4 at pp. 163 to 167.
- Fama, E. F., & French, K. R. (1992). The cross-section of expected stock returns. *Journal of Finance*, 47(2), 427–465. Cited by Chan (2021, p. 160) for the three-factor model.
- French, K. R. *Data Library*. Tuck School of Business, Dartmouth College. The source of the market factor’s step over the bill rate and the momentum factor’s skip of the latest month.

*Not investment advice. Code: [the PCA factor model](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor.py), [the two factors](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/momentum_factor.py), [the test of Example 7.4’s own factors](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor_momentum.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/momentum_factor_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/factor_models_whiteboard.py), with the checks behind [the model’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor.py), [the factors’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_momentum_factor.py), [the own factors’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor_momentum.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_momentum_factor_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_factor_models_whiteboard.py), and the replication log’s entries for [the factor model](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-13-the-pca-factor-model-chans-quantitative-trading), [the two factors](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-14-the-market-and-momentum-factors-chans-quantitative-trading) and [Example 7.4’s own factors](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-42-whether-example-74s-own-factor-returns-have-momentum-chans-quantitative-trading).*
