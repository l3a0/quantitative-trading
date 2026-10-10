# Chan’s SPY index arbitrage reproduces to the last digit, and random walks unrelated to SPY pass its screen more often than stocks do

*Example 4.2 picks the S&P 500 stocks that pass a cointegration test against SPY one at a time, holds them as one basket, and trades the basket against SPY. On Chan’s own files every figure his script prints comes back exactly. The count of stocks that pass, though, is smaller than the count a screen of random walks unrelated to SPY would give.*

## Why trade SPY against the stocks inside it

Index arbitrage trades an index against the stocks it is made of. If the stocks are held in the index’s own weights, their value tracks the index almost exactly, and Ernest Chan’s second book, *Algorithmic Trading*, says that is the trouble. It is “such a well-known strategy that the difference in market values has become extremely small” (Chan, 2013, location 2006). To widen the difference, he holds only some of the stocks. “One selection method is to just pick all the stocks that cointegrate individually with the ETF”, and he demonstrates it on SPY, the ETF that tracks the S&P 500.

Two prices that each wander on their own cointegrate when some fixed combination of them is stationary, which means the combination keeps returning to a stable level rather than wandering off. Chan’s Example 4.2 tests every stock in his S&P 500 file against SPY over 2007. He reports “98 stocks that cointegrate (each separately) with SPY”, a basket of them that cointegrates with SPY “with better than 95 percent probability”, and a strategy on that basket from 2008 of which he writes, “The APR of this strategy is 4.5 percent, and the Sharpe ratio is 1.3” (Chan, 2013, location 2035). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.

Chan published the script, `indexArb.m`, and the data files it reads. This repository keeps a copy of both files and ran a line-by-line transcription of the script on them. Every figure the script prints comes back to its last digit.

**Every result here is exploratory and survivor-only.** Chan chose the screen, the window and the rule, and the reproduction tests them on the same days he did. It can say whether his numbers follow from his files and nothing about whether the trade pays today. The stock file also holds only companies that were in the S&P 500 in April 2012, so the 2007 screen could never pick a company that left the index before then.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

The test Chan uses is the Johansen test. It takes several price series and counts how many independent stationary combinations of them exist, each one a cointegrating relation, or relation for short. It counts by testing a ladder of hypotheses. The row written r ≤ 0 is the hypothesis that there is no relation, r ≤ 1 that there is at most one, and rejecting a row is evidence of more relations than it allows. Each row comes with two statistics, the trace and the eigen statistic, which read the same evidence in two ways. Each statistic is compared with a critical value, the bar it must clear for the test to reject that row at a given level, such as 90 or 95 percent. The [post on Chan’s Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains how the count is made and why the two statistics can disagree.

The script runs in five steps.

1. **The screen.** For each stock, take its 2007 closes and SPY’s, in prices, and run the Johansen test with a constant and one lagged change. A stock passes when the trace statistic clears its 90 percent bar for r ≤ 0, the hypothesis of no relation. Location 2027 calls this finding the stocks that cointegrate with SPY “with at least 90 percent probability”.
2. **The basket.** Hold every stock that passed with equal capital. The basket’s value is the sum of their log prices.
3. **The second test.** Run the Johansen test again on the basket’s log value and SPY’s log price. Chan explains why it is needed: “an arbitrary assignment of equal capital weight to each stock does not necessarily produce a portfolio price series that cointegrates with that of SPY” (Chan, 2013, location 2027).
4. **The weights.** Each relation the test finds comes as an eigenvector, a set of weights that turns the prices into a stationary combination. The first eigenvector, from the relation with the largest eigenvalue, gives one weight to the basket and one to SPY. The test ran on log prices, so the weights are dollars rather than shares, and every stock in the basket carries the basket’s weight.
5. **The rule.** From 2008, the z-score is how many 5-day standard deviations the weighted combination sits from its 5-day average. The rule holds minus the z-score in units of the combination, so it sells more as the combination rises above its average and buys more as it falls below. This is the same linear rule the Johansen post’s portfolio trades, with dollars in place of shares. Each day’s return is the profit on yesterday’s positions divided by the gross dollars they held. No cost is charged.

Chan tests one stock at a time rather than all 500 with SPY in one run, for two reasons (Chan, 2013, location 2066).

1. **Size.** The Johansen implementation he knew “can accept a maximum of 12 symbols only” (LeSage, 1998).
2. **Signs.** “The eigenvectors will usually involve both long and short stock positions.” He wants a basket that is long every stock.

The data is [two files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), both Chan’s own MATLAB files converted here to one file per symbol. The stock file holds 497 members of the S&P 500, saved on 2012-04-25. SPY comes from his ETF file, saved on 2012-04-10. The two share 1,489 trading days from 2006-05-11 to 2012-04-09. Training is the 251 days of 2007, from 2007-01-03 to 2007-12-31, and the test is the 1,076 days from 2008-01-02 to 2012-04-09, the window location 2035 names.

The screen needs more than 250 days of closes, so it skips 17 stocks. Eleven have no 2007 close at all, and six began trading during 2007. It tests the other 480. This repository transcribed the script from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, which a second copy holds byte for byte.

### What one unit holds

The second test’s first eigenvector gives 99 weights, one for each of the 98 stocks and one for SPY. Every stock carries the same 1.0939, and SPY carries −105.5600. Chan says so in a parenthesis: “The weight on each individual stock is, of course, the same, due to our assumption of equal capital allocation” (Chan, 2013, location 2035).

So one unit of the combination is long $1.0939 of each stock, $107.198 of stocks in all, and short $105.560 of SPY. The two sides differ by $1.638, so a unit holds nearly as many dollars of stocks as it is short of SPY. The rule scales the whole unit up or down each day by minus the z-score.

The 5-day standard deviation first exists on the fifth test day, so the first position earns its first return on 2008-01-09, the sixth. From there the strategy earns a return on every one of the 1,071 remaining days.

## Lesson 1: every figure the script prints reproduces to its last digit

Here is each figure computed on Chan’s files, beside what the script prints and what the book prints.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script} & \text{Book} \\ \hline
\text{Stocks passing the screen} & 98 & 98 & 98 \\
\text{Trace statistic, } r \le 0 & 15.868648 & 15.869 & \text{none} \\
\text{Trace statistic, } r \le 1 & 6.197357 & 6.197 & \text{none} \\
\text{Eigen statistic, } r \le 0 & 9.671291 & 9.671 & \text{none} \\
\text{Eigen statistic, } r \le 1 & 6.197357 & 6.197 & \text{none} \\
\text{Eigenvector 1, basket and SPY} & 1.09386171,\ -105.55999232 & 1.0939,\ -105.5600 & \text{none} \\
\text{Eigenvector 2, basket and SPY} & -0.27989806,\ 56.09328286 & -0.2799,\ 56.0933 & \text{none} \\
\text{APR} & 0.0449298745 & 0.044930 & \text{4.5 percent} \\
\text{Sharpe ratio} & 1.3193972970 & 1.319397 & 1.3
\end{array}
```

Every computed figure rounds to what the script prints, and the eigenvectors come back with Chan’s signs. The book’s 4.5 percent and 1.3 are the script’s figures rounded. A gap is the difference between a printed figure and a computed one, and every gap here is zero.

One thing the match cannot show is which 98 stocks Chan’s run picked. Neither the book nor the script names them, so the reproduction says only that the same rule on the same file picks 98.

The book’s two claims about the second test fare less well, and the script’s own printout already shows why. “Better than 95 percent probability” names no statistic, so the table reads each statistic against its own bars.

```math
\begin{array}{l|r|r|r}
\text{Statistic, } r \le 0 & \text{Value} & \text{90 percent bar} & \text{95 percent bar} \\ \hline
\text{Trace} & 15.869 & 13.429 & 15.494 \\
\text{Eigen} & 9.671 & 12.297 & 14.264
\end{array}
```

The trace statistic clears its 95 percent bar by 0.374. The eigen statistic falls short of even its 90 percent bar. So the trace test supports the claim and the eigen test does not support it at any level.

The second claim is a parenthesis in the same passage: “There are, in fact, two cointegrating relations” (Chan, 2013, location 2035). The trace test counts two at both 90 and 95 percent. The eigen test stops at its first row and counts none at any level. Lesson 3 says what a count of two means here.

The figure below redraws the book’s Figure 4.3, the strategy’s cumulative return. The script plots it against the row number, and the redraw plots it against the date. Its second panel belongs to Lesson 2. Nothing compares the redraw with the chart in the book, so it is a redraw of the script’s plot rather than a checked copy.

![Two charts. The top chart is the compounded cumulative return of the strategy from January 2008 to April 2012, in percent, unlevered and before costs. It stays near zero through mid-2008, climbs steeply from late 2008 through 2009 to above 20 percent, peaks in late 2010, and drifts down to end at about 20.6 percent. Its heading sets the APR of 0.044930 and the Sharpe ratio of 1.319397 beside the book’s 4.5 percent and 1.3, and says the curve is zero until the first return on 2008-01-09 and 0.206422 on the last day. The bottom chart is two horizontal bars giving the share of series the screen passes over 2007. The green bar is 98 of 480 stocks in Chan’s file, 20.4 percent. The brown bar is 561 of 2,000 random walks unrelated to SPY, 28.1 percent. A dashed vertical line marks the nominal 10 percent at the 90 percent bar, and both bars reach well past it. The title calls the figure exploratory and survivor-only, and the note names both of Chan’s files and says the lookback was chosen with hindsight and every stock survived to 2012.](../docs/figures/index_arbitrage.png)

*Above, the book’s Figure 4.3 redrawn against the date on Chan’s files. Below, the share of series the screen passes, for the stocks and for random walks unrelated to SPY, which Lesson 2 explains.*

## Lesson 2: the screen’s 98 is a count of tests passed, and random walks unrelated to SPY pass more often

Location 2027 describes the screen as finding stocks that cointegrate with SPY “with at least 90 percent probability”. That reads the bar as a probability about each stock, and the bar is not one. A 90 percent bar says how often the test should reject when there is no relation: at most 10 percent of the time. It says nothing on its own about the chance that a stock which passed really cointegrates.

The screen runs that test 480 times. If it held its nominal rate, chance alone would pass about 10 percent of 480 stocks with no relation to SPY, which is 48. A count of 98 would then look like evidence. On random walks with no drift the test does not hold that rate, and two measurements show it. Both use random walks, series built by adding an independent random step each day, so each one wanders with no pull back toward any level and no link to anything else.

1. **The test on its own.** On 2,000 pairs of random walks of 251 days, unrelated to each other and with no drift, the trace test with a constant rejects the hypothesis of no relation on 410 pairs at its 90 percent bar and on 242 at its 95. That is 20.5 and 12.1 percent, where 10 and 5 are nominal.
2. **The screen against SPY.** Run exactly as it runs on the stocks, the screen passes 561 of 2,000 random walks unrelated to SPY against SPY’s own 2007 closes. That is 28.1 percent, or about 135 of 480.

The stocks pass at 20.4 percent, 98 of 480. The random walks unrelated to SPY pass at 28.1 percent. The figure’s second panel sets the two side by side against the nominal 10 percent.

Random walks with no drift are not stocks, so this does not show that none of the 98 cointegrates with SPY. It shows that the count is no evidence that any of them does. A screen that judged 480 tests together would need a false-discovery control, a rule that limits the share of passes expected to be false across the whole batch. Such a control works from p-values. A p-value is the probability that a statistic this large would arise with no relation. The test routine this repository uses returns none, so no control is computed here.

## Lesson 3: two relations between two series claim each one is stationary alone

The second test runs on two series, the basket and SPY, and the trace test counts two relations. Lesson 4 of the [Johansen post](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains why that is a strong claim. A count of relations equal to the number of series is called a full rank, and a full rank says every combination of the series is stationary. That includes holding the basket alone, or SPY alone. So the count says that each of them, over 2007, returned to a stable level on its own.

Chan reads the second relation differently, as a second portfolio he chose not to use, picking “the one with the largest eigenvalue” (Chan, 2013, location 2035). Two tests aimed at the full-rank claim do not support it.

1. **A test of each series alone.** The augmented Dickey-Fuller test, or ADF test, asks whether a single series wanders or returns to a level. With a constant and one lagged change, it gives −2.461086 for the basket’s 2007 log value and −2.381322 for SPY’s 2007 log price. Both fall short of −2.57, the bar for rejecting wandering at even 90 percent (MacKinnon, 2010). An ADF test over 251 days has little power, which means it often fails to reject when the series does return to a level, so this is weak evidence rather than proof.
2. **The eigen test.** It finds no relation at all, so it does not support the full rank either.

Lesson 2 adds one more caution. The trace test rejects the hypothesis of no relation on 12.1 percent of pairs of unrelated random walks with no drift at its 95 percent bar, so the trace pass in Lesson 1 is weaker evidence than its 95 percent label suggests.

## Lesson 4: the 4.5 percent is in-sample on its lookback and survivor-only

The stocks and weights are fitted on 2007 and traded from 2008 to 2012, which makes the result look out-of-sample. It is not, for two reasons.

1. **The lookback was chosen with hindsight.** Chan fixed the 5-day lookback “with the benefit of hindsight” (Chan, 2013, location 2035). The test years chose one of the rule’s settings, so the APR and the Sharpe ratio are in-sample figures, meaning the same days chose a setting and scored it.
2. **Every stock is a survivor.** Location 2035 says the example uses the same stock universe as Example 4.1, and location 1974 says that universe “has survivorship bias”. The file is the S&P 500 as Chan held it on 2012-04-24, the date in its name, carried backwards. A company that left the index between 2007 and 2012 could not enter the 2007 screen. The [post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches what a database of survivors does to a backtest, and the [post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md) applies it to this same file. This repository cannot measure the effect here. The index holdings it has committed start at the end of 2008, so no file here holds the 2007 members beside the ones that later left.

Chan reads Figure 4.3 as showing that “the performance decreases as time goes on, partly because we have not retrained the model periodically to select new constituent stocks with new hedge ratios” (Chan, 2013, location 2035). No test here checks that reading. Any measure of a decline chosen now would be chosen after seeing his chart and this one, and four years of returns are unlikely to separate a decline from noise.

So the result is exploratory. It shows that Chan’s figures follow from his files and his script, on a sample that picked the lookback and could only ever hold survivors.

## What this replication cannot say

Four things are beyond it.

1. **Which stocks cointegrate with SPY.** Lesson 2 is why. A screen with a false-discovery control, or one judged against a baseline built from real prices rather than random walks, would be a new search, with its hypothesis written down before it runs and data held back that the search never loads.
2. **Whether the strategy works with another lookback or with periodic retraining.** Location 2035 suggests retraining. Each variant is a search too, for the same reason.
3. **What costs would take.** The rule resizes 99 positions every day, and neither the script nor the reproduction charges any cost.
4. **How much survivorship bias is worth.** No file here holds the index as it stood in 2007, for the reason Lesson 4 gives.

## What this means for a trader

One habit for each lesson.

1. **Read the printout beside the prose.** Here the script’s figures land to every digit, and its own table already shows that the eigen test does not back “better than 95 percent probability”.
2. **Measure how often a screen passes unrelated series before counting its passes.** A count of passes means something only next to the count the same test gives on series known to be unrelated, and here those series passed more often.
3. **Ask what a full rank claims.** Two relations between two series says each series is stationary alone, which a test aimed at each series can test, if weakly over one year.
4. **Find what chose the settings and the universe.** A lookback picked with hindsight and a list of survivors each put the test years inside the backtest, however cleanly the fitting and trading windows are split.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.1 and 4.2 and Kindle locations 1974, 2006, 2027, 2035 and 2066.
2. LeSage, J. P. (1998). The Econometrics Toolbox for MATLAB, as Chan (2013) cites it at location 2066.
3. MacKinnon, J. G. (2010). Critical values for cointegration tests. Queen’s Economics Department Working Paper No. 1227.
4. `indexArb.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the screen and the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/index_arbitrage.py), [the Johansen wrapper](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/johansen.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/index_arbitrage_figures.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_index_arbitrage.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_index_arbitrage_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-24-spy-against-its-component-stocks-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
