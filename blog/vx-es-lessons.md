# Volatility against the stock index: a hedge that holds on one file and not the next

*Chan hedges VIX futures against E-mini S&P 500 futures from August 2008 and prints four figures. Three land on his data file dated 2012-05-07, and the fourth misses by \$2.09. His file dated ten days later misses all four, the script he ships cannot have produced them, and the exit he never names decides the trade.*

## Why trade volatility against the stock index

Stocks and volatility move against each other. Ernest Chan puts it plainly in *Algorithmic Trading*: “When the market goes down, volatility shoots up” (Chan, 2013, location 2546). A trader can own both and bet that the link between them lasts. When one side runs ahead of the other, the trade expects the two to come back together.

Chan builds that trade from two futures contracts. A futures contract is an agreement to buy or sell something at a set price on a set future date, and it trades on an exchange like a share.

- **ES** is the E-mini S&P 500 future. Its price follows the S&P 500 index of large American companies.
- **VX** is the VIX future. The VIX index measures how much volatility traders expect over the next month, read from the prices of S&P 500 options, so VX rises when traders grow nervous.

Chan plots one against the other and sees “two main regimes, 2004 to May 2008 and August 2008 to 2012” (location 2552). He reads the second regime as having lower volatility for a given level of the index. A regression fits one straight line through the points, and Chan warns against fitting one across both regimes, so he fits only the second.

At location 2559 he reports four figures.

1. **The hedge.** A portfolio “long 0.3906 contracts of VX and long one contract of ES” should be stationary, meaning its value keeps returning to a stable average.
2. **The residual’s standard deviation.** The residual is the part of each day’s ES value the fit leaves unexplained, and “The standard deviation of the residues is \$2,047.”
3. **The APR.** The trade’s return compounded to one year is 12.3 percent, on a test set from July 29, 2010, to May 8, 2012.
4. **The Sharpe ratio.** The return per unit of its own variability is 1.4 on the same test set.

He leaves three choices unnamed.

1. When a position closes.
2. Which days the fit is trained on.
3. Which of his data files he ran.

No script that ships prints the figures.

This repository ran the trade on Chan’s own data, which comes as files he saved on particular dates. This post calls each one a **save** and names it by the date in its file name. A figure lands when it rounds to the printed one at the precision Chan printed. Three of the four land on the 2012-05-07 save, and the deviation misses by \$2.09. On the 2012-05-17 save the same specification misses all four. The script Chan publishes for the example fits on days that include the whole test set and never trades. Whether the trade’s figures land at all depends on the exit, and the APR rests on four positions in 449 days.

**Every result here is exploratory.** Reproducing Chan’s figures spends the 2008 to 2012 sample on a rule he chose. The save and the exit were each chosen because they land the printed figures, so the match is partly built in. The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The regression and the files

A futures contract expires, so a price history running for years has to be stitched from one contract after another. At each switch, called a roll, the next contract usually trades at a different price from the one expiring. A **continuous future** shifts the whole earlier history by that difference so the series has no jump at the roll. So every roll rewrites the history, and the same day can carry a different price in a file saved a week later.

Each of Chan’s saves is a MATLAB file of continuous futures. Three of them hold VX and ES.

1. **The 2012-05-07 save**, `inputDataOHLCDaily_20120507.mat`. VX and ES share 1,999 trading days, from 2004-06-02 to 2012-05-08. Its last day is the last day of the book’s test set.
2. **The 2012-05-11 save.**
3. **The 2012-05-17 save**, the one Chan’s `VX_ES.m` loads. It also holds 1,999 common days, ending 2012-05-17.

The regression needs one more idea first. A move of one point in VX is worth \$1,000, and a move of one point in ES is worth \$50. Those are the contracts’ dollars per point. Multiplying each price by its dollars per point turns it into the dollar value of one contract. A regression of one dollar value on the other then has a slope measured in contracts, which is the number a trader can act on. In symbols, with c the intercept, h the hedge and ε the residual on day t:

```math
50 \cdot ES_t = c - h \cdot 1000 \cdot VX_t + \varepsilon_t
```

The specification has three parts.

1. **The fit.** Regress 50·ES on 1000·VX with an intercept, over the 500 common days from 2008-08-04 to 2010-07-28. That first day and that 500-day training span come from Chan’s own `VX_ES_rollreturn.m`, the script behind a later trade in the book that reuses this hedge. The slope is negative, because the two move against each other. The hedge is minus the slope.
2. **The band.** The band scores each day’s portfolio, h VX contracts and one ES contract, both long, by its z-score. That is its distance from the intercept c, measured in standard deviations of the training residual ε. Below −1, the band buys one unit of the portfolio. Above +1, it sells one unit short. When to close the position is a separate choice. This run holds each position until the z-score crosses the opposite band.
3. **The test.** The 449 days from 2010-07-29 to 2012-05-08, with no trading cost. Each day’s return is the profit on yesterday’s positions over the gross dollars they held, as [the post on price spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md#the-rule-and-the-file) builds it. The APR compounds the daily returns to a year of 252 trading days. The Sharpe ratio is the mean daily return over its standard deviation, scaled by √252.

The top panel of the figure below redraws the book’s Figure 5.10 from the 2012-05-07 save. The two regimes sit on two separate lines, and the fit runs along the second.

## Lesson 1: three figures land and the deviation misses by \$2.09

Here is each figure beside the book’s.

```math
\begin{array}{l|r|r|l}
\text{Figure} & \text{Computed} & \text{Book} & \text{Verdict} \\ \hline
\text{Hedge, VX contracts per ES contract} & 0.390594 & 0.3906 & \text{lands} \\
\text{Residual standard deviation} & \$2{,}044.91 & \$2{,}047 & \text{misses by } \$2.09 \\
\text{APR} & 0.122811 & \text{12.3 percent} & \text{lands} \\
\text{Sharpe ratio} & 1.393201 & 1.4 & \text{lands}
\end{array}
```

The fit lands the hedge to four decimals and misses the deviation by about a tenth of a percent. Fitting on one trading day fewer, from 2008-08-05, lands both, at 0.390635 and \$2,046.93. A search of [22,446 windows recorded beside the run](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-28-vx-futures-against-e-mini-futures-chans-algorithmic-trading) found that window, and it is the only one of them that rounds to both printed figures. No test reruns that search, so nothing in the code checks its two counts. A window found by searching for the answer shows only that a window close to Chan’s exists. It cannot say which window he used, so the run keeps the one his script names.

The printed hedge is also safe to reuse. Trading the rounded 0.3906 in place of the fitted 0.390594 gives an APR of 0.122810 and a Sharpe ratio of 1.393205, which moves nothing that prints. The book’s next trade on these two futures, at location 2754, holds “0.3906 front contracts of VX” as a fixed number, so it trades the same portfolio to the book’s precision. Its script as it ships, `VX_ES_rollreturn.m`, does not. Every line holding 0.3906 is commented out, and it trades one VX contract against one ES contract.

![Three charts stacked. The top chart is a scatter of 50·ES against 1000·VX, both in dollars per contract, on the 1,999 days both traded. Days from 2004 to May 2008, in brass, form a band high on the chart, with ES between about 56,000 and 76,000 dollars while VX runs from about 40,000 to 75,000. Days from August 2008 to May 2012, in black, form a lower line falling from about 70,000 dollars of ES at 20,000 dollars of VX to about 38,000 at 100,000. A few pale grey days from June and July 2008 sit between the two. A red line, the fit on the 500 training days, runs along the lower group. The middle chart plots the z-score from August 2008 to May 2012, with dotted lines at plus and minus one and a dashed line at 2010-07-28. Its background is shaded green while the band is long and red while it is short. Right of the dashed line it stays shaded green and mostly below minus one until November 2011, dipping to its lowest, −3.89, on 2011-08-08, then switches between red, green and red. The bottom chart plots the test set’s cumulative return. It wanders between about minus 5 and plus 3 percent until July 2011, falls to about minus 8 percent just after a dashed red line at 2011-08-05 labelled minus 4.59 percent, and then climbs to 22.92 percent by May 2012, with three dots where the position changes. The title calls the figure exploratory, and the note names the 2012-05-07 save and says the save and the exit were chosen because they land the printed figures.](../docs/figures/vx_es.png)

*The book’s Figures 5.10 to 5.12 redrawn on Chan’s 2012-05-07 save: the two regimes, the z-score with its band, and the test set’s cumulative return.*

## Lesson 2: the save decides, and the script that ships is not the run

The same specification on the other two saves misses everything.

```math
\begin{array}{l|r|r|r|r}
\text{Run} & \text{Hedge} & \text{Deviation} & \text{APR} & \text{Sharpe} \\ \hline
\text{Book} & 0.3906 & \$2{,}047 & \text{12.3 percent} & 1.4 \\
\text{2012-05-07 save} & 0.390594 & \$2{,}044.91 & 0.122811 & 1.393201 \\
\text{2012-05-11 save} & 0.376431 & \$2{,}291.00 & 0.056582 & 0.673910 \\
\text{2012-05-17 save} & 0.376431 & \$2{,}291.00 & 0.056582 & 0.673910 \\
\texttt{VX\_ES.m}\text{ as it ships} & 0.350731 & \$2{,}373.59 & \text{none} & \text{none}
\end{array}
```

On the 2012-05-17 save the specification trains and tests on the same dates as on the 2012-05-07 save, so what changed is the closes. The same days carry different prices, and the APR falls by more than half. The 2012-05-11 and 2012-05-17 saves give identical figures, and both disagree with the 2012-05-07 save.

[The post on GLD and GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md#3-adjusted-close-is-not-a-fixed-number) found a hedge ratio drifting with the date its prices were downloaded, as years of dividends were folded into the adjusted closes. A continuous future can do the same thing within days. Between the 2012-05-07 and 2012-05-17 saves, the same days carry different VX closes and give a different hedge. Nothing here measured how Chan’s source rebuilt VX and ES between saves. Their closes do not all move by one amount, which is what a single roll would do, so the roll explains how such a history can change and not what changed here.

Chan’s `VX_ES.m`, as published at commit `e4bc46f` of the `ericnberwick/EpchanPreview` repository, does four things.

1. It loads the 2012-05-17 save.
2. It keeps the days VX and ES both traded.
3. It draws the scatter of Figure 5.10.
4. It fits the regression on every day from 2008-08-01 to the end of the file.

That fit runs over 957 days, through 2012-05-17, so it includes the whole test set. Then the script stops. It prints nothing and runs no trade, and its fit misses both of the printed figures it could produce. Two facts point to the 2012-05-07 save without using the figures. The book’s test set ends on 2012-05-08, that save’s last day, and Chan’s `VX_ES_rollreturn.m` reads ES from it.

A published script and the numbers printed beside it can come from different files and different runs. Here the figures land only on a save the script does not load, with a window and an exit the script does not contain.

## Lesson 3: the exit the book leaves out decides the trade

The book describes the entry and is silent about the exit. Two other readings of the band show how much that silence costs.

```math
\begin{array}{l|r|r|l}
\text{Rule} & \text{APR} & \text{Sharpe} & \text{Verdict} \\ \hline
\text{Hold until the opposite band} & 0.122811 & 1.393201 & \text{lands both} \\
\text{Close at the mean} & 0.068463 & 0.870716 & \text{misses both} \\
\text{Start flat on the first test day} & 0.124916 & 1.415772 & \text{misses the APR by 0.2 points}
\end{array}
```

Closing each position when the z-score crosses zero is what `bollinger.m`, Chan’s script for Example 3.2, does. That example trades GLD against USO with a band of the same kind, which Chan calls a Bollinger band, and [the post on price spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md#lesson-5-a-return-that-cannot-see-its-own-scale) names it at its close. It has no post here yet. Read that way, this trade earns 6.8 percent a year rather than 12.3.

Starting the band flat on the first test day, so nothing is carried in from training, lands the Sharpe ratio and misses the APR, at 12.5 percent. On 2010-07-28, the last training day, the z-score is −1.041, so the band is already long. `VX_ES_rollreturn.m` computes every day’s return first and then keeps the days from the 501st on, so its first test day earns the position held the day before. This run does the same.

Holding each position until the opposite band is the one rule of the three tried that lands both the APR and the Sharpe ratio. That is why the run uses it.

**So the result is exploratory here too.** The save and the exit were both chosen because they land the printed figures. A match built from choices made to produce it confirms that the arithmetic can reach Chan’s numbers. It cannot confirm that his run made those choices.

## Lesson 4: an APR from four bets

An APR of 12.3 percent sounds like the summary of many trades. Here it is four. The band is already long when the test begins, and it changes position three times in 449 days.

```math
\begin{array}{l|l|l|r|r}
\text{Position} & \text{First day earned} & \text{Last day earned} & \text{Days} & \text{Return} \\ \hline
\text{Long} & \text{2010-07-29} & \text{2011-11-08} & 325 & 0.058104 \\
\text{Short} & \text{2011-11-09} & \text{2011-12-19} & 28 & 0.056144 \\
\text{Long} & \text{2011-12-20} & \text{2012-02-17} & 41 & 0.056877 \\
\text{Short} & \text{2012-02-21} & \text{2012-05-08} & 55 & 0.040777
\end{array}
```

The band changes position at the close of 2011-11-08, 2011-12-19 and 2012-02-17, so each new position starts earning the next trading day. It is in the market on all 449 test days. All four bets win, and compounded together they make the test set’s 22.92 percent, which is the 12.3 percent APR over a year and three quarters.

Chan writes that the trade “was particularly profitable” from around Standard and Poor’s downgrade of the U.S. credit rating (location 2559). The agency announced it after the close of Friday 2011-08-05. At that close, after 259 of the 449 test days, the trade was down 4.59 percent. On Monday 2011-08-08 it reached its lowest point, down 7.76 percent, and the z-score reached −3.89, its lowest since the fit’s first day in 2008. From the close of 2011-08-05 to the end of the test, the trade grew 28.84 percent in 190 days. So the trade earned all of its gain after that close, and more, since it was losing before it. That fits Chan’s sentence, but the split falls one trading day before the trade’s low, and any split there would show the same. It dates when the trade made its money and says nothing about what the downgrade did.

The bottom panel of the figure shows that shape. The first bet, the long carried in from training, spent 325 days earning 5.81 percent, and was down 7.76 percent at its worst along the way. It paid off only because the band held it through the worst day.

One more count suggests the test set behaved differently from training. The z-score sits beyond a band on 236 of the 449 test days, against 113 of the 500 training days. A portfolio that reverted as reliably in the test as in training would stray past one deviation about as often. This one spent more than half the test beyond the band.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the portfolio is stationary.** Chan argues it from a plot, Figure 5.11, and prints no statistic. This run takes no test either. The z-score spending 236 of 449 test days beyond the band is a reason to doubt it rather than a result.
2. **What costs would take.** Neither the book nor this run charges any. Four positions in 449 days is few trades, but nothing here measures what a cost would do. Each unit also holds 0.39 of a VX contract, which a real account cannot hold, and nothing here measures what rounding it would change.
3. **Whether the window is the book’s.** The search found one window that lands both fitted figures, and the run uses a neighbour of it that a script of Chan’s names. Nothing Chan printed confirms either, so the match shows a window close to his and no more.

## What this means for a trader

One habit for each lesson.

1. **Hold a reproduction to the printed precision, and say how much it misses by.** Three figures landing and one missing by \$2.09 is a more useful report than “it reproduces.”
2. **Record which file a backtest read.** A continuous future can be rewritten between saves, so a hedge fitted on one save can fail on a save made days later.
3. **Ask for the exit.** An entry rule with no exit is half a strategy, and here the half left out cuts the APR from 12.3 percent to 6.8.
4. **Count the bets behind an APR.** Four winning positions in 449 days is a sample of four, however steady the final 22.92 percent looks.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 2546, 2552, 2559 and 2754.
2. Chan, E. P. `VX_ES.m` and `VX_ES_rollreturn.m`, as published in the [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) repository at commit `e4bc46f`.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-28-vx-futures-against-e-mini-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside what was found here.*
