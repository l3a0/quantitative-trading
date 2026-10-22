# Chan’s Johansen test on three ETFs reproduces to the last digit, and its two statistics disagree

*The Johansen test counts every stationary combination of several prices in one run. On Chan’s own file it gives every figure he printed, and its trace and eigen statistics still count different numbers of stationary combinations.*

## Why test three ETFs at once

A pair trade needs two prices that drift apart and come back. The earlier posts on [GLD and GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md) and on [testing a price spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-mean-reversion.md) test that with the Engle-Granger test. Chan’s MATLAB code runs a version of it called the cointegrated augmented Dickey-Fuller test, or CADF test. It regresses one price on the other to get a hedge ratio, the number of shares of one held against each share of the other, then tests whether the leftover spread returns to a stable level. Two prices that wander on their own but hold such a spread are said to cointegrate.

Ernest Chan’s second book, *Algorithmic Trading*, asks the same question of more than two prices. Canada and Australia both have economies that are “commodity based, so they seem likely to cointegrate” (Chan, 2013, location 1264). So EWA and EWC, the two countries’ stock ETFs, should form a pair. Chan then adds IGE, an ETF of natural resource stocks, to see how many stationary combinations, mixes of the ETFs whose value returns to a stable level, the three hold together (Chan, 2013, location 1334).

A pair test cannot answer that. One regression gives one hedge ratio, so it finds at most one combination. With three prices it also has to pick one of them to put on the left, and each choice can give a different answer. The Johansen test takes all three prices at once, counts how many stationary combinations they hold, leaving out any that is only a mix of others already counted, and returns the weights of each.

Chan published the script for all three examples, `cointegrationTests.m`, and the data file it reads. This repository keeps the file’s prices as one table per ETF, which together rebuild the file exactly, and ran a line-by-line Python transcription of the script on them. Every figure the script prints lands to its last digit. The one difference is that the Johansen test’s sets of weights, its eigenvectors, come back with their signs flipped, which Lesson 1 shows changes nothing.

The CADF statistic is −3.64346635. The portfolio Chan builds from the three ETFs takes 22.662578 days to close half its distance to its average, which is its half-life. The strategy that trades the portfolio earns an annual percentage rate, or APR, of 0.125739 with a Sharpe ratio of 1.391310, the book’s 12.6 percent and 1.4 (Chan, 2013, location 1368). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk.

**Every result here is exploratory.** Chan chose the ETFs, the test settings and the portfolio, and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the portfolio pays.

The six lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The tests and the file

Chan runs four steps (Chan, 2013, locations 1264 to 1368).

1. **The CADF test, Example 2.6.** Regress EWC on EWA with an intercept, then test the residual, the leftover spread, for a unit root. The test allows a constant and one lagged daily change, both written out in the section below. A unit root means the residual wanders with no level to return to. The test starts from the claim that a unit root is present, so rejecting that claim is evidence the pair cointegrates.
2. **The Johansen test, Example 2.7.** Run it on EWC and EWA, then on EWC, EWA and IGE, each with a constant and one lagged daily change. The script orders the columns EWC, EWA, IGE, so every set of weights below lists them in that order.
3. **The half-life.** Hold the triplet in the shares the test’s first set of weights gives, and measure how many days the value of that holding takes to close half its distance to its average. The test calls each set of weights an eigenvector, a term the next section explains.
4. **The linear rule, Example 2.8.** Each day, hold a number of units of the portfolio equal to minus its z-score, so the rule is short when the value sits above its average and long when it sits below. The z-score is the value’s distance from its moving average, divided by its moving standard deviation, both over a lookback of the half-life rounded to whole days.

The script’s CADF and Johansen functions come from jplv7, a free MATLAB econometrics toolbox by James LeSage. The Johansen test here is the `coint_johansen` function of the Python library statsmodels, which carries the same tables of critical values, the bars a test statistic must clear, and matches LeSage’s output at these settings.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10. It holds 67 ETFs over 1,500 trading days, from 2006-04-26 to 2012-04-09, and EWA, EWC and IGE each have a close on every one of those days. The file adjusts each close for dividends by subtracting them in dollars, so a return computed from it is close to, but not exactly, what a holder earned.

### How the Johansen test counts relations

Start from the CADF test’s second step, which writes the daily change in a spread as a response to the spread’s level the day before.

```math
\Delta z_t = \lambda \, z_{t-1} + \mu + \phi \, \Delta z_{t-1} + \varepsilon_t
```

Here zₜ is the spread on day t and Δzₜ its change from the day before. μ is a constant, φ carries yesterday’s change, the one lagged change the test’s settings allow, and εₜ is the part of today’s change the other terms do not explain. If λ is negative, a spread above its level tends to fall the next day and one below tends to rise, so it reverts. If λ is zero, yesterday’s level says nothing about today’s change, and the spread wanders. The test asks whether λ is far enough below zero to rule out the wandering case.

The Johansen test writes the same equation for several prices at once (Chan, 2013, location 1295). Now the single spread becomes Yₜ, a list of today’s prices, one per ETF, and λ becomes a square table of coefficients Λ, one row and one column per ETF. M and Φ do for each ETF what μ and φ did for the spread.

```math
\Delta Y_t = \Lambda \, Y_{t-1} + M + \Phi \, \Delta Y_{t-1} + \varepsilon_t
```

Each row of Λ weighs yesterday’s prices of all the ETFs to give one ETF’s pull, so Λ Yₜ₋₁ holds one combination of yesterday’s prices per row. The CADF test fixed its combination with a regression before testing it. Here no combination is fixed in advance. What the test counts is how many of the rows’ combinations are independent, none a mix of the others, and pull today’s changes back. That count is the rank of Λ, written r. Each combination it counts is one of the stationary combinations the opening asked about, and the rest of this post calls each one a relation.

The count runs from 0 to the number of series, n.

1. **r = 0** means no combination pulls, so nothing cointegrates.
2. **r between 0 and n** means some combinations revert and the rest wander.
3. **r = n** means every combination reverts, including each ETF held alone.

#### The eigenvalues and the two statistics

To find the rank, the test solves for n eigenvalues, written ℓ₁ ≥ ℓ₂ ≥ … ≥ ℓₙ to keep them apart from the λ above. They are numbers between 0 and 1. Each measures how strongly one combination of yesterday’s prices predicts today’s changes, and 0 means that combination does not pull at all. The rank is the number of eigenvalues that are not zero. Eigenvalues estimated from data never come out exactly zero, so the question is which of them sit too far above zero to put down to chance.

Each eigenvalue comes with an eigenvector, a combination’s weights in shares of each ETF. The eigenvectors of the r eigenvalues the test counts are the relations’ weights, the hedge ratios the CADF test could only give one at a time (Chan, 2013, location 1295). Any mix of those r sets of weights also reverts, so the test pins down how many relations exist, not one unique set of weights for each.

So the test asks whether the eigenvalues past the first r could be zero, using two statistics. Each tests a null hypothesis, the starting claim that at most r relations exist, which the test keeps unless the statistic clears its bar. With T the number of days the regression fits, the statistics are these.

```math
\begin{gathered}
\text{trace}(r) = -T \sum_{i=r+1}^{n} \ln(1 - \ell_i) \\
\text{eigen}(r) = -T \ln(1 - \ell_{r+1})
\end{gathered}
```

The trace statistic asks whether all the eigenvalues past the first r could be zero together, so it adds up the evidence from each of them. The eigen statistic asks whether only the next one could be zero, so it uses that eigenvalue alone.

Each statistic is compared with its critical value, the bar it must clear at a chosen confidence. The count comes from a sequence. Test r ≤ 0, the claim that no relation exists, first. If its statistic clears the bar, reject it and test r ≤ 1, and so on. The count is the number of nulls rejected before the first one that is not. If every null is rejected, the count is n (Chan, 2013, location 1295).

## Lesson 1: the script reproduces to its last digit

`cointegrationTests.m` prints its results, and its comments record what it printed. The two tables below set each figure, computed, beside the printout. The first holds the CADF test and the strategy.

```math
\small\begin{array}{l|r|r}
\text{Figure} & \text{Computed} & \text{Printed} \\ \hline
\text{CADF statistic} & -3.6434663489 & -3.64346635 \\
\text{CADF } \lambda & -0.0204108120 & -0.020411 \\
\text{Half-life, days} & 22.6625778505 & 22.662578 \\
\text{APR} & 0.1257386810 & 0.125739 \\
\text{Sharpe ratio} & 1.3913100883 & 1.391310
\end{array}
```

Chan’s text quotes four of these, rounded: a CADF statistic of about −3.64, a half-life of 23 days, an APR of 12.6 percent and a Sharpe ratio of 1.4 (Chan, 2013, locations 1292, 1347 and 1368). It quotes none of the Johansen test’s figures, which the second table holds.

```math
\small\begin{array}{l|r|r}
\text{Johansen figure} & \text{Computed} & \text{Printed} \\ \hline
\text{Pair trace, } r \le 0 & 19.983219 & 19.983 \\
\text{Pair trace, } r \le 1 & 3.982761 & 3.983 \\
\text{Pair eigen, } r \le 0 & 16.000457 & 16.000 \\
\text{Pair eigen, } r \le 1 & 3.982761 & 3.983 \\
\text{Triplet trace, } r \le 0 & 34.428620 & 34.429 \\
\text{Triplet trace, } r \le 1 & 17.531719 & 17.532 \\
\text{Triplet trace, } r \le 2 & 4.471021 & 4.471 \\
\text{Triplet eigen, } r \le 0 & 16.896901 & 16.897 \\
\text{Triplet eigen, } r \le 1 & 13.060698 & 13.061 \\
\text{Triplet eigen, } r \le 2 & 4.471021 & 4.471 \\
\text{Triplet eigenvalue 1} & 0.01121626 & 0.0112 \\
\text{Triplet eigenvalue 2} & 0.00868086 & 0.0087 \\
\text{Triplet eigenvalue 3} & 0.00298021 & 0.0030 \\
\text{First eigenvector, EWC} & 1.0460 & -1.0460 \\
\text{First eigenvector, EWA} & -0.7600 & 0.7600 \\
\text{First eigenvector, IGE} & -0.2233 & 0.2233
\end{array}
```

Every Johansen critical value matches the printout too, at the three decimals it prints. The CADF test’s critical values are LeSage’s own table, quoted rather than computed: −3.880 at 99 percent and −3.359 at 95. The computed −3.6435 is below −3.359 but above −3.880, and a CADF statistic clears its bar by falling below it. So the pair cointegrates at 95 percent, as Chan says (Chan, 2013, location 1292), and not at 99, which he does not claim.

The three rows of the first eigenvector differ in sign. Every one of the three eigenvectors comes back with all its signs flipped. That follows from the software rather than the data. The statsmodels library multiplies all three eigenvectors by the sign of the first one’s first weight, so that weight always comes back positive, and MATLAB gave −1.0460 there. An eigenvector negated is the same portfolio held short, and the linear rule holds minus the z-score of whatever it is given. So flipping the sign leaves the half-life, the lookback and every day’s return exactly where they were, which a test in the repository checks.

The figure below redraws three of the book’s charts and adds the statistics Lesson 3 turns to.

![Four charts stacked, three of them over the file’s 1,500 trading days, from April 2006 to April 2012. The first, Figure 2.4, plots the adjusted closes of EWA and EWC in dollars. The two lines move together, EWC a few dollars above EWA throughout, and both fall sharply in late 2008. The second, Figure 2.6, plots the residual EWC − 0.9624·EWA, which crosses a dashed line at its mean of 6.41, the regression’s intercept, many times. Its heading gives the CADF statistic of −3.6435 against the 95 percent bar of −3.359. The third is a bar chart of the Johansen test on EWC, EWA and IGE, with a trace column and an eigen column for each of the nulls r ≤ 0, r ≤ 1 and r ≤ 2, each crossed by dotted, solid and dashed lines at its 90, 95 and 99 percent critical values. Every trace column, 34.429, 17.532 and 4.471, rises above its 95 percent line and stops below its 99 percent line. The first eigen column, 16.897, stops below even its 90 percent line, and a note reads 16.897, short of 18.893, its 90 percent bar. The fourth, Figure 2.7, plots the strategy’s compounded cumulative return, which climbs from 0 to a high on 2009-04-01, sits below that high in a shaded band labelled 598 days, from 2009-04-02 to 2011-08-15, with its deepest drawdown of −0.101249 marked on 2010-08-16, and ends near 102 percent. Its heading gives an APR of 0.125739 and a Sharpe ratio of 1.3913 against the book’s 12.6 percent and 1.4. The title calls the redraw exploratory, and the note says the eigenvector is fitted on the days the strategy trades, so every figure is in-sample.](../docs/figures/etf_cointegration.png)

*Three of `cointegrationTests.m`’s four charts redrawn on Chan’s file, the prices, the pair’s residual and the strategy’s cumulative return, with the triplet’s Johansen statistics added as the third panel. The one left out is the script’s second chart, the Figure 2.5 scatter of EWC against EWA. The shaded band in the last panel is the longest spell below a high.*

## Lesson 2: one regression depends on its order, the Johansen test does not

The CADF test puts one ETF on the left of the regression. Chan puts EWC there, asks whether swapping the two changes the result, and answers “yes” (Chan, 2013, location 1282). His advice is to “try each variable as independent”, meaning to run the regression once with each ETF on the right-hand side, and keep the order with the most negative statistic.

On this pair the swap moves little. With EWA on the left, the statistic is −3.6405 against −3.6435, and both are past the 95 percent bar of −3.359. The verdict holds either way, so the advice costs nothing here. With three ETFs it would mean three regressions, one per choice of the left-hand ETF, and each gives one hedge ratio.

Whichever order it takes, the pair’s regression fits its hedge ratio once over all 1,500 days and holds it fixed. With EWC on the left, it finds a slope of 0.9624, which is the hedge ratio, and an intercept of 6.4113, the constant the regression adds. [The post on the Kalman filter hedge ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/kalman-hedge-lessons.md) trades EWC against EWA on the same file with a hedge ratio that a Kalman filter re-estimates every day.

The Johansen test treats every ETF the same way, so the order of the columns should not matter, and Chan says it does not (Chan, 2013, location 1324). Running the triplet’s test again with the columns ordered EWA, EWC, IGE leaves every statistic and eigenvalue within 10⁻¹¹ of the first run. The eigenvectors come back with their weights in the new order, and two of the three come back negated, which the previous lesson showed changes nothing.

## Lesson 3: the trace and eigen tests disagree

The two statistics read the same eigenvalues. The trace statistic for a null is the sum of the eigen statistics for that null and every later one, so the triplet’s 34.429 is 16.897 plus 13.061 plus 4.471. Because they add the evidence differently, they can reach different counts, and on the triplet they do.

```math
\begin{array}{l|r|r|r}
\text{Null} & r \le 0 & r \le 1 & r \le 2 \\ \hline
\text{Trace} & 34.429 & 17.532 & 4.471 \\
\text{Bar, 90 percent} & 27.067 & 13.429 & 2.705 \\
\text{Bar, 95 percent} & 29.796 & 15.494 & 3.841 \\
\text{Bar, 99 percent} & 35.463 & 19.935 & 6.635 \\ \hline
\text{Eigen} & 16.897 & 13.061 & 4.471 \\
\text{Bar, 90 percent} & 18.893 & 12.297 & 2.705 \\
\text{Bar, 95 percent} & 21.131 & 14.264 & 3.841 \\
\text{Bar, 99 percent} & 25.865 & 18.520 & 6.635
\end{array}
```

The trace test rejects all three nulls at 95 percent, so it counts three relations. The eigen test stops at the first column. Its 16.897 falls short of even the 90 percent bar of 18.893, so it rejects nothing and counts no relations at any of the three levels. The eigen test’s later columns never come into play, even where they clear a bar, as 4.471 clears 3.841, because the count stops at the first null the test fails to reject.

The first eigenvalue alone is not strong enough to clear the eigen test’s bar. The trace test adds the second and third eigenvalues’ evidence to it, and the total clears the trace test’s bar. Evidence spread across several weak combinations can pass the trace test and fail the eigen test. At 99 percent the trace test falls short too, since 34.429 is below 35.463, so at that level neither test finds a relation.

![An animated whiteboard sketch titled “Weak pieces add up”, drawn stroke by stroke. Two columns stand on one grey floor, drawn to one scale. On the left, a black block marked “16.897”, labelled “eigen test, r ≤ 0”, stops just below a dashed line labelled “90% eigen bar, 18.893”, and red words say “falls short”. A grey arrow labelled “the same piece” carries the block to the right, where the same black block, marked “16.897” and labelled “trace test, r ≤ 0”, has two brown blocks stacked on it, “+ 13.061” and then “+ 4.471”. A dashed line labelled “95% trace bar, 29.796” crosses the stack at the top of the second block, and the green words “34.429 clears it” close the sketch.](../docs/figures/etf_cointegration_trace_stack.gif)

Chan’s text reads the table differently. “Both Trace statistic and Eigen statistic tests conclude” that the triplet holds three relations at 95 percent (Chan, 2013, location 1337). The trace test does. The eigen test does not, and the script’s own printout already shows it. A reader who trusts Chan’s paragraph over the printout takes away a stronger result than the run gave.

## Lesson 4: two relations between two series claim each ETF reverts alone

On the pair, both tests agree. The trace test rejects r ≤ 0 with 19.983, past even its 99 percent bar of 19.935, and the eigen test rejects it with 16.000 against 14.264 at 95. Both then reject r ≤ 1 with 3.983 against 3.841. So both count two relations between EWA and EWC.

Chan reads the two relations as two hedge ratios, one from each order of the regression, “which are not necessarily reciprocal of each other” (Chan, 2013, location 1324). The test says something stronger. Two relations between two series is a full rank, r = n. A full rank means every combination of the two prices reverts, and holding EWA alone, a weight of one on EWA and zero on EWC, is one such combination. So the test is saying that each ETF reverts to a stable level on its own. The triplet’s trace count of three says the same of all three.

![An animated whiteboard sketch titled “The test’s two relations span every portfolio”, drawn stroke by stroke. It is schematic and carries none of the run’s figures. A grey axis across is labelled “shares of EWA” and a grey axis up is labelled “shares of EWC”. From where they cross, a black arrow labelled “relation 1” points down and to the right, and a black arrow labelled “relation 2” points up and to the right. A grey dashed line runs from each arrow’s tip, parallel to the other arrow, and the two meet on the EWA axis, labelled “a mix of relations 1 and 2”. A thick brown arrow then runs along the EWA axis to that corner, labelled “EWA alone (1, 0)”, and the words “if both relations revert, so does EWA alone” close the sketch.](../docs/figures/etf_cointegration_two_relations.gif)

A test aimed at each ETF alone disagrees. The CADF test runs an augmented Dickey-Fuller test on its spread. Run on each price alone, with a constant and one lagged change, the same test gives −1.86 for EWA, −1.90 for EWC and −2.08 for IGE. All three fall short of −2.57, the bar for rejecting a unit root at even 90 percent confidence (MacKinnon, 2010). None of the three rejects the wandering case on its own.

That is a tension rather than a refutation. A Dickey-Fuller test on prices has little power, which means it often fails to reject a unit root that is not there. Failing to reject is weak evidence of a unit root rather than proof of one. The run does not settle which reading holds.

The full rank is also thin. The second relation, the one that makes the rank full, rests on 3.983 against a bar of 3.841. It clears its bar by only 0.141. At 99 percent the bar is 6.635, and the trace test counts one relation rather than two.

[The post on Chan’s SPY index arbitrage](https://github.com/l3a0/quantitative-trading/blob/main/blog/index-arbitrage-lessons.md) finds the same full rank, two relations between two series, in a basket of S&P 500 stocks and SPY. There the trace test counts two relations at 95 percent, and the eigen test finds none at any level.

## Lesson 5: what the portfolio holds

The first eigenvector sets the portfolio, in shares: 1.0460 of EWC, −0.7600 of EWA and −0.2233 of IGE. On the file’s last day, 2012-04-09, one unit of it holds $28.72 of EWC against −$17.43 of EWA and −$8.49 of IGE. It is long one country fund and short the other country fund and the resources fund together.

Chan picks the first eigenvector because it has the largest eigenvalue, and so he expects it to revert fastest, with the shortest half-life (Chan, 2013, location 1340). It does. Its half-life is 22.7 days, against 43.7 for the second eigenvector’s portfolio and 151.5 for the third’s.

The rule rounds 22.7 to a lookback of 23 days. Its first return comes on 2006-05-30, the trading day after the 23-day moving standard deviation first has 23 days to use, and it earns a return on every one of the 1,477 days from there on. The return each day is the profit on the positions held, divided by the dollars held long plus the dollars held short, each side counted as a positive amount.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

Every printed figure matches, so the code, the data and the book agree. The match says nothing about whether the portfolio pays, for two reasons.

1. **The weights and the lookback come from the days they trade.** The test fits the eigenvector on the same 1,500 days the rule then trades, and the half-life that sets the lookback comes from those days too. So the result is in-sample, scored on the same days that set its weights. Chan names this himself. Of the same rule in an earlier example, he says the lookback carries look-ahead bias, the use of information no trader had on the day, from “the use of in-sample data to find the half-life” (Chan, 2013, location 1225). Of the book’s backtests in general, he says they sometimes use “the same data for parameter optimization (such as finding the best hedge ratio) and for backtest” (Chan, 2013, location 1429). His claim that the rule has “no parameters to optimize” makes a different point, that nothing was searched over (Chan, 2013, location 1350). That claim holds too, and it leaves the 12.6 percent in-sample.
2. **The script charges no cost, though the rule never stops trading.** It resizes its position whenever the z-score moves, and Chan says it “continuously enters and exits positions”. He also calls it “obviously not a practical strategy”, since its capital has no ceiling and it trades on every small move (Chan, 2013, location 1350).

A drawdown is a fall from the highest value reached so far, and this return came with a long one. On the compounded cumulative return, the deepest drawdown is −0.101249, with its trough on 2010-08-16. Its longest spell below a high runs 598 trading days, from 2009-04-02 to 2011-08-15, which the figure’s last panel shades.

So the result stays exploratory. A result that could confirm the portfolio would need weights fitted on one stretch of days, fixed in writing, and traded on days the fit never saw.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the portfolio works out of sample.** Nothing here fits the eigenvector on one window and trades it on the next. That is the run that would price the look-ahead in Lesson 6, and it is a different experiment.
2. **What costs would take.** The linear rule trades every day by construction, and neither the script nor this run charges a cost.
3. **Whether another lag count changes the counts.** Every Johansen call in the book’s scripts uses one lagged daily change, and so does this run. The counts in Lessons 3 and 4 hold for that lag alone, and the pair’s full rank clears its bar by only 0.141.

## What this means for a trader

One habit for each lesson.

1. **Reproduce the printed figures before arguing with them.** Every number Chan’s script prints lands here, so any disagreement with his result is about how it is read, not his arithmetic.
2. **Use the Johansen test when more than two prices are in play.** A regression depends on which price goes on the left and gives one hedge ratio per run. The Johansen test gives every relation in one run, whatever the column order.
3. **Read the trace and eigen statistics separately.** They answer different questions of the same eigenvalues, and here one counts three relations where the other counts none.
4. **Treat a full rank as a claim that each price reverts alone.** Check it against a test on each price, and look at how far the last relation clears its bar.
5. **Look at what the eigenvector holds in dollars.** The weights are in shares, so the long and short sides are only visible once each is multiplied by its price.
6. **Treat an exact reproduction as a check on arithmetic.** Whether this portfolio pays needs weights fitted before the days they trade, and a charge for trading every day.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 2.6 to 2.8 and Kindle locations 1225, 1264, 1282, 1292, 1295, 1324, 1334, 1337, 1340, 1347, 1350, 1368 and 1429.
2. `cointegrationTests.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551–1580.
4. MacKinnon, J. G. (2010). Critical values for cointegration tests. Queen’s Economics Department Working Paper No. 1227.

*Not investment advice. Code: [the tests and the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/etf_cointegration.py), [the Johansen wrapper](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/johansen.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/etf_cointegration_figures.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_etf_cointegration.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_etf_cointegration_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-23-ewa-ewc-and-ige-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
