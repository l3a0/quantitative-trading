# Chan’s SPY index arbitrage reproduces to the last digit, and random walks unrelated to SPY pass its screen more often than stocks do

*Example 4.2 tests S&P 500 stocks one at a time against SPY for cointegration, holds the stocks that pass as one basket, and trades the basket against SPY. On Chan’s own files every figure his script prints comes back exactly. The share of stocks that pass, though, is smaller than the share of random walks unrelated to SPY that pass the same screen.*

## Why trade SPY against the stocks inside it

Index arbitrage trades an index against the stocks it is made of. If the stocks are held in the index’s own weights, their value tracks the index almost exactly, and Ernest Chan’s second book, *Algorithmic Trading*, says that is the trouble. Index arbitrage is “such a well-known strategy that the difference in market values has become extremely small” (Chan, 2013, Kindle location 2006). To widen the difference, he holds only some of the stocks. “One selection method is to just pick all the stocks that cointegrate individually with the ETF”, and he demonstrates it on SPY, the ETF that tracks the S&P 500.

Two prices that each wander on their own cointegrate when some fixed combination of them is stationary, which means the combination keeps returning to a stable level rather than wandering off.

Chan’s Example 4.2 tests every stock in his S&P 500 file against SPY over 2007. He reports “98 stocks that cointegrate (each separately) with SPY”, a basket of them that cointegrates with SPY “with better than 95 percent probability”, and a strategy on that basket from 2008 of which he writes, “The APR of this strategy is 4.5 percent, and the Sharpe ratio is 1.3” (Chan, 2013, location 2035). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk.

### What the reproduction found

Chan published the script, `indexArb.m`, and the two data files it reads. Every figure the script prints comes back to its last digit. The script came from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, and a second public copy, `ivanliu1989/algorithmic_trading`, holds the same file byte for byte.

This repository keeps each data file’s contents as one table per symbol, which together rebuild the file’s arrays exactly, and ran a line-by-line Python transcription of the script on them. The one statistical step not transcribed is the Johansen test, a test for cointegration that the next section explains. The script calls it from James LeSage’s MATLAB toolbox. In its place runs `coint_johansen` from statsmodels, a Python library of statistical tests, which carries LeSage’s tables of critical values, the bars each statistic must clear.

Two labels apply to every figure below.

1. **Every result is exploratory.** Chan chose the screen, the window and the rule, and the reproduction tests them on the same days he did. So it can say whether his numbers follow from his files and nothing about whether the trade pays today.
2. **The list of stocks is from late 2011.** The stock file holds only stocks that were in the S&P 500 in late 2011. So the 2007 screen could never pick a company that was out of the index for all of late 2011. It can still pick one that joined the index later, or left and came back, and 12 of the 98 it picks were not in the index on 2007-11-23. That is the date of Chan’s list of the S&P 500, which Lesson 4 describes.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

The test Chan uses is the Johansen test. It takes several price series and counts how many independent stationary combinations of them exist. Each such combination is a cointegrating relation, or relation for short.

The test prints one row per hypothesis, where r stands for the number of relations. The row written r ≤ 0 is the hypothesis that there is no relation, and r ≤ 1 is the hypothesis that there is at most one. Rejecting a row is evidence of more relations than it allows. The count is read from the top down: it is the number of rows rejected before the first row the test fails to reject. So on two series, rejecting both r ≤ 0 and r ≤ 1 counts two relations, and failing to reject r ≤ 0 counts none, whatever the row below it says.

Each row comes with two statistics, the trace and the eigen statistic, which read the same evidence in two ways. Each statistic is compared with a critical value, the bar it must clear for the test to reject that row at a given level, such as 90 or 95 percent. The [post on Chan’s Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains how the count is made and why the two statistics can disagree.

### What the script does

The script runs in five steps.

1. **The screen.** For each stock, take its 2007 closes and SPY’s, in prices rather than log prices, and run the Johansen test with a constant term and one lagged daily change in its model. A stock passes when the trace statistic clears its 90 percent bar for r ≤ 0, the hypothesis of no relation. Location 2027 calls this finding the stocks that cointegrate with SPY “with at least 90 percent probability”.
2. **The basket.** Hold every stock that passed with equal capital. The script tracks the basket with one series, the sum of the stocks’ log prices. A log price is the natural logarithm of a close. A day’s change in a log price is close to that day’s return, so a day’s change in the sum is close to the profit on $1 held in each stock. The holding stays at $1 a stock only if the basket is rebalanced every day, which Chan says he expects to do: “rebalance this portfolio every day” (Chan, 2013, location 2027).
3. **The second test.** Run the Johansen test again on two series, the basket’s sum of log prices and SPY’s log price. Chan explains why it is needed: “an arbitrary assignment of equal capital weight to each stock does not necessarily produce a portfolio price series that cointegrates with that of SPY” (Chan, 2013, location 2027).
4. **The weights.** Each relation the test finds comes as an eigenvector, a set of weights that turns the prices into a stationary combination. The first eigenvector, the one the test ranks first by its eigenvalue, gives one weight to the basket and one to SPY. The test ran on log prices, so the weights are dollars rather than shares. The basket is a plain sum of its stocks’ log prices, so the basket’s weight applies to each stock in it.
5. **The rule.** One unit of the combination holds each weight in dollars: long the basket’s weight in every stock, and short SPY by the size of SPY’s weight. From 2008, the z-score is how many standard deviations the combination sits from its average, both taken over the last 5 days. Those 5 days are the rule’s lookback. The rule holds minus the z-score in units, so it sells more as the combination rises above its average and buys more as it falls below.

Step 5’s rule is the one the Johansen post’s portfolio trades, with dollars in place of shares. Each day’s return is the profit on yesterday’s positions divided by the total dollars they held, the long dollars and the short dollars added together. No cost is charged.

Chan tests one stock at a time rather than all 500 with SPY in one run, for two reasons (Chan, 2013, location 2066).

1. **Size.** The Johansen implementation he knew, LeSage’s (1998), “can accept a maximum of 12 symbols only”.
2. **Signs.** “The eigenvectors will usually involve both long and short stock positions.” He wants a basket that is long every stock.

### Where the prices come from, and the days they cover

The data is [two files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), both Chan’s own MATLAB files converted here to one table per symbol.

1. **The stocks.** The stock file holds 497 stocks that were in the S&P 500 in late 2011, with prices from 2006-05-11 to 2012-04-24, and was saved on 2012-04-25. Its name, `inputDataOHLCDaily_stocks_20120424.mat`, carries the last day of its prices, not the date of its list of stocks. Companies that left the index in its December 2011 rebalance are still in the file.
2. **SPY.** It comes from his ETF file, whose closes end on 2012-04-09 and which was saved on 2012-04-10.

The two share 1,489 trading days from 2006-05-11 to 2012-04-09. Training is the 251 days of 2007, from 2007-01-03 to 2007-12-31, and the test period is the 1,076 days from 2008-01-02 to 2012-04-09, the window location 2035 names.

The screen needs more than 250 days of closes, so it skips 17 stocks. Eleven have no 2007 close at all, and six began trading during 2007. It tests the other 480.

### What one unit holds, and when it first earns

The second test’s first eigenvector gives two weights, 1.0939 on the basket and −105.5600 on SPY. The basket’s weight goes on each of its 98 stocks, so the script holds 99 positions, 1.0939 on each stock and −105.5600 on SPY. Chan says so in a parenthesis: “The weight on each individual stock is, of course, the same, due to our assumption of equal capital allocation” (Chan, 2013, location 2035).

So one unit of the combination is long $1.09386 of each stock, $107.198 of stocks in all, and short $105.560 of SPY. The two sides differ by $1.638, so a unit holds nearly as many dollars of stocks as it is short of SPY. The rule scales the whole unit up or down each day by minus the z-score.

![An animated whiteboard sketch titled “What one unit holds”, drawn to one scale from the run. On the left a grid of 98 green dots appears, one for each stock, labelled “98 stocks” above and “$1.09386 each” below. A green arrow points right from the grid. A grey baseline appears, and a green column rises from it, labelled “long $107.198” inside. A red column of the same width stands beside it on the same baseline, labelled “short SPY $105.560” inside. Its top sits lower than the green column’s by 1.5 percent of the height, about 3 pixels, too little to measure by eye. Two black arrows point down at the two tops, then “$1.638 apart” appears above them. Last, grey words at the lower left read “the rule scales the whole unit by minus the z-score”.](../docs/figures/index_arbitrage_sketch_one_unit.gif)

*Drawn to scale from the run. The short SPY column’s top sits $1.638 below the long column’s, too close to read by eye, so the callout names the difference.*

The 5-day standard deviation first exists on the fifth test day, so the strategy’s first return falls on 2008-01-09, the sixth test day. From there the strategy earns a return on every one of the 1,071 remaining days.

## Lesson 1: every figure the script prints reproduces to its last digit

Here is each figure computed on Chan’s files, beside what the script prints. The first row is the screen. The statistics below it come from the second test, on the basket and SPY.

```math
\begin{array}{l|r|r}
\text{Figure} & \text{Computed} & \text{Script} \\ \hline
\text{Stocks passing} & 98 & 98 \\
\text{Trace, } r \le 0 & 15.868648 & 15.869 \\
\text{Trace, } r \le 1 & 6.197357 & 6.197 \\
\text{Eigen, } r \le 0 & 9.671291 & 9.671 \\
\text{Eigen, } r \le 1 & 6.197357 & 6.197
\end{array}
```

The second test’s two eigenvectors each give the basket one weight and SPY another.

```math
\small\begin{array}{l|r|r}
\text{Eigenvector} & \text{Computed} & \text{Script} \\ \hline
\text{First, basket} & 1.09386171 & 1.0939 \\
\text{First, SPY} & -105.55999232 & -105.5600 \\
\text{Second, basket} & -0.27989806 & -0.2799 \\
\text{Second, SPY} & 56.09328286 & 56.0933
\end{array}
```

The book prints three of the script’s figures. One is the 98 in the first table. The other two are the strategy’s APR and Sharpe ratio, and the table below sets the book’s values beside the script’s.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script} & \text{Book} \\ \hline
\text{APR} & 0.0449298745 & 0.044930 & 4.5\% \\
\text{Sharpe} & 1.3193972970 & 1.319397 & 1.3
\end{array}
```

Every computed figure rounds to what the script prints, and the eigenvectors come back with Chan’s signs. The book’s 4.5 percent and 1.3 are the script’s figures rounded.

One thing the match cannot show is which 98 stocks Chan’s run picked. Neither the book nor the script names them, so the reproduction says only that the same rule on the same file picks 98.

### What the second test supports

The book makes two claims about the second test, both in one passage (Chan, 2013, location 2035). They fare less well than the book’s figures, and the script’s own printout already shows why.

1. **The basket cointegrates with SPY “with better than 95 percent probability”.** The claim names no statistic, so the table below reads each statistic for r ≤ 0 against its own bars.
2. **“There are, in fact, two cointegrating relations”.** Chan writes it as an aside, in parentheses.

```math
\begin{array}{l|r|r}
r \le 0 & \text{Trace} & \text{Eigen} \\ \hline
\text{Value} & 15.869 & 9.671 \\
\text{90 percent bar} & 13.429 & 12.297 \\
\text{95 percent bar} & 15.494 & 14.264
\end{array}
```

The trace statistic clears its 95 percent bar by 0.374. The eigen statistic falls short of even its 90 percent bar. So the trace test supports the first claim and the eigen test does not support it at any level. The trace statistic for r ≤ 0 is the sum of the two eigen statistics, 9.671291 and 6.197357, which the first table above lists for r ≤ 0 and r ≤ 1. The first falls short of the trace statistic’s 95 percent bar on its own. So the trace test clears that bar only by adding the second, the evidence of a second relation.

On the second claim, the trace test counts two relations at both 90 and 95 percent, because its r ≤ 1 statistic, 6.197, also clears that row’s bars, which the script prints as 2.705 and 3.841. The eigen test fails to reject its first row, so it counts none at any level, although its r ≤ 1 statistic clears the same bars. Lesson 3 says what a count of two means here.

### The cumulative return, and how often the screen passes

The figure below redraws the book’s Figure 4.3, the strategy’s cumulative return. The script plots it against each test day’s row number, and the redraw plots it against the date. Its second panel belongs to Lesson 2. Nothing compares the redraw with the chart in the book, so it is a redraw of the script’s plot rather than a checked copy.

![Two charts. The top chart is the compounded cumulative return of the strategy from January 2008 to April 2012, in percent, unlevered and before costs. It stays near zero through mid-2008, climbs steeply from late 2008 through 2009 to above 20 percent, peaks in late 2010, and drifts down to end at about 20.6 percent. Its heading sets the APR of 0.044930 and the Sharpe ratio of 1.319397 beside the book’s 4.5 percent and 1.3, and says the curve is zero until the first return on 2008-01-09 and 0.206422 on the last day. The bottom chart is two horizontal bars giving the share of series the screen passes over 2007. The green bar is 98 of 480 stocks in Chan’s file, 20.4 percent. The brown bar is 561 of 2,000 random walks unrelated to SPY, 28.1 percent. A dashed vertical line marks the nominal 10 percent at the 90 percent bar, and both bars reach well past it. The title calls the figure exploratory and survivor-only, and the note names both of Chan’s files and says the lookback was chosen with hindsight and every stock in the file was in the S&P 500 in late 2011.](../docs/figures/index_arbitrage.png)

*Above, the book’s Figure 4.3 redrawn against the date on Chan’s files. Below, the share of series the screen passes, for the stocks and for random walks unrelated to SPY, which Lesson 2 explains.*

## Lesson 2: the screen’s 98 is a count of tests passed, and random walks unrelated to SPY pass more often

Location 2027 describes the screen as finding stocks that cointegrate with SPY “with at least 90 percent probability”. That reads the bar as a probability about each stock, and the bar is not one. A 90 percent bar says how often the test should reject when there is no relation: at most 10 percent of the time. It says nothing on its own about the chance that a stock which passed really cointegrates.

The screen runs that test 480 times. If the test rejected exactly as often as its bar allows, and no stock had a relation to SPY, chance alone would pass about 10 percent of the 480, which is 48. A count of 98 would then look like evidence. A random walk is a series built by adding an independent random step each day, so it wanders with no pull back toward any level and no link to anything else. The walks here have no drift, which means their steps average zero. Two measurements on them show that the test rejects more often than its bar allows.

1. **The test on its own.** On 2,000 pairs of random walks of 251 days, unrelated to each other and with no drift, the trace test with a constant rejects the hypothesis of no relation on 410 pairs at its 90 percent bar and on 242 at its 95. That is 20.5 and 12.1 percent, where the bars allow 10 and 5.
2. **The screen against SPY.** Run exactly as it runs on the stocks, the screen passes 561 of 2,000 random walks unrelated to SPY against SPY’s own 2007 closes. That is 28.1 percent, or about 135 of 480. It is higher than the 20.5 percent of the first measurement. Apart from their random draws, the two differ only in the second series, SPY’s real 2007 closes in place of a second walk. Nothing here measures why the rate is higher against SPY.

The stocks pass at 20.4 percent, 98 of 480. The random walks unrelated to SPY pass at 28.1 percent. The figure’s second panel sets the two side by side against the 10 percent the bar allows.

Random walks with no drift are not stocks, so this does not show that none of the 98 cointegrates with SPY. It shows that the count is no evidence that any of them does. A screen that judged 480 tests together would need a false-discovery control, a rule that limits the share of passes expected to be false across the whole batch. Such a control works from p-values. A p-value is the probability that a statistic this large would arise with no relation. `coint_johansen` returns no p-values, so no control is computed here.

## Lesson 3: two relations between two series claim each one is stationary alone

The second test runs on two series, the basket and SPY, and the trace test counts two relations. Lesson 4 of the [Johansen post](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains why that is a strong claim. A count of relations equal to the number of series says every combination of the series is stationary. That includes holding the basket alone, or SPY alone. So the count says that each of them, over 2007, returned to a stable level on its own.

Chan reads the second relation differently, as a second portfolio he chose not to use, picking “the one with the largest eigenvalue” (Chan, 2013, location 2035). Two tests aimed at the claim that each series is stationary alone do not support it.

1. **A test of each series alone.** The augmented Dickey-Fuller test, or ADF test, asks whether a single series wanders or returns to a level. With a constant term and one lagged daily change in its model, it gives −2.461086 for the basket’s 2007 sum of log prices and −2.381322 for SPY’s 2007 log price. Neither falls below −2.57, the bar at 90 percent (MacKinnon, 2010), so neither rejects the hypothesis that the series wanders even at that level. An ADF test over 251 days has little power, which means it often fails to reject when the series does return to a level, so this is weak evidence rather than proof.
2. **The eigen test.** It finds no relation at all, so it does not support a count of two either.

Lesson 2 adds one more caution. The trace test rejects the hypothesis of no relation on 12.1 percent of pairs of unrelated random walks with no drift at its 95 percent bar, so the trace pass in Lesson 1 is weaker evidence than its 95 percent label suggests.

## Lesson 4: the 4.5 percent rests on a lookback chosen with hindsight and a stock list from late 2011

The stocks and weights are fitted on 2007 and traded from 2008 to 2012, which makes the result look out-of-sample. It is not, for two reasons.

1. **The lookback was chosen with hindsight.** Chan fixed the 5-day lookback “with the benefit of hindsight” (Chan, 2013, location 2035). The test years chose one of the rule’s settings, so the APR and the Sharpe ratio are in-sample figures, meaning the same days chose a setting and scored it.
2. **The list of stocks is from late 2011.** Location 2035 says the example uses the same stock universe as Example 4.1, and location 1974 says that universe “has survivorship bias”. The file holds 497 stocks that were in the S&P 500 in late 2011 and treats them as the index on every earlier day too. A company that was out of the index for all of late 2011 is not in the file, so the 2007 screen could not pick it. The screen does pick stocks that were out of the index at other times. Twelve of the 98 are missing from Chan’s list of the S&P 500 as it stood on 2007-11-23, which this repository also keeps. Two more, the insurer ACE and Cooper Industries, are missing from the holdings of iShares’ S&P 500 fund at some quarter-ends of the test period. That fund tracks the index. All 14 stay in the basket on every test day.

The [post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches what a database of survivors does to a backtest, and the [post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md) applies it to this same file. This repository has not measured the effect here. Chan’s 2007 list comes in a file whose prices end on 2007-11-23. So screening the index as it stood in 2007 would need prices from 2007 to 2012 for every company on that list that the stock file lacks, and no run here has assembled them.

So the result is exploratory. It shows that Chan’s figures follow from his files and his script. The same days that score the strategy chose its lookback, and the screen chose its stocks from a list of companies in the S&P 500 in late 2011.

### Chan’s reading of the later years

Chan reads Figure 4.3 as showing that “the performance decreases as time goes on, partly because we have not retrained the model periodically to select new constituent stocks with new hedge ratios” (Chan, 2013, location 2035). No test here checks that reading. Any measure of a decline chosen now would be chosen after seeing his chart and the redraw in Lesson 1, and four years of returns are unlikely to separate a decline from noise.

## What this replication cannot say

Four things are beyond it.

1. **Which stocks cointegrate with SPY.** Lesson 2 is why. A screen with a false-discovery control, or one judged against a baseline built from real prices rather than random walks, would be a new study that tests many hypotheses. Such a study needs its hypotheses written down before it runs and some data held back that it never loads.
2. **Whether the strategy works with another lookback or with periodic retraining.** Location 2035 suggests retraining. Trying variants on these same days is the same kind of study, so it needs the same safeguards.
3. **What costs would take.** The rule resizes 99 positions every day, and neither the script nor the reproduction charges any cost.
4. **How much survivorship bias is worth.** No run here has screened the index as it stood in 2007, for the reason Lesson 4 gives.

## What this means for a trader

One habit for each lesson.

1. **Read the printout beside the prose.** Here the script’s figures come back to the last digit, and its own table already shows that the eigen test does not back “better than 95 percent probability”.
2. **Measure how often a screen passes unrelated series before counting its passes.** A count of passes means something only next to the count the same test gives on series known to be unrelated, and here those series passed more often.
3. **Ask what a count of relations claims.** Two relations between two series say that each series is stationary alone. A test on each series can check that, though over one year it is a weak check.
4. **Find what chose the settings and the universe.** The test years shaped both the lookback picked with hindsight and the list of stocks from late 2011, though each looks like a choice made before them. A clean split between the 2007 training window and the test period does not change that.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.1 and 4.2 and Kindle locations 1974, 2006, 2027, 2035 and 2066.
2. LeSage, J. P. (1998). The Econometrics Toolbox for MATLAB, as Chan (2013) cites it at location 2066.
3. MacKinnon, J. G. (2010). Critical values for cointegration tests. Queen’s Economics Department Working Paper No. 1227.
4. `indexArb.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the screen and the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/index_arbitrage.py), [the Johansen wrapper](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/johansen.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/index_arbitrage_figures.py) and [the whiteboard sketch](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/index_arbitrage_whiteboard.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_index_arbitrage.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_index_arbitrage_figures.py) and [what the sketch draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_index_arbitrage_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-24-spy-against-its-component-stocks-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
