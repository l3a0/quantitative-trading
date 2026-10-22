# Volatility against the stock index: a hedge that holds on one file and not the next

*Chan hedges VIX futures against E-mini S&P 500 futures from August 2008 and prints four figures. Three land on his data file dated 2012-05-07, and the fourth misses by \$2.09. His file dated ten days later misses all four, the script he ships cannot have produced them, and the exit he never names decides the trade.*

## Why trade volatility against the stock index

Stocks and volatility move against each other. Ernest Chan puts it plainly in *Algorithmic Trading*: “When the market goes down, volatility shoots up” (Chan, 2013, location 2546). A trader can own both and bet that the link between them lasts. When one side runs ahead of the other, the trade expects the two to come back together.

Chan builds that trade from two futures contracts. A futures contract is an agreement to buy or sell something at a set price on a set future date, and it trades on an exchange like a share.

- **ES** is the E-mini S&P 500 future. Its price follows the S&P 500 index of large American companies.
- **VX** is the VIX future. The VIX index measures how much volatility traders expect over the next month, read from the prices of S&P 500 options, so VX rises when traders grow nervous.

Chan plots one against the other and sees “two main regimes, 2004 to May 2008 and August 2008 to 2012” (location 2552), two periods in which ES and VX keep a different relationship. He reads the second regime as having lower volatility for a given level of the index. A regression fits one straight line through the points, and Chan warns against fitting one across both regimes, so he fits only the second.

### What the book prints and what it leaves out

At location 2559 Chan reports four figures.

1. **The hedge.** A portfolio “long 0.3906 contracts of VX and long one contract of ES” should be stationary, meaning its value keeps returning to a stable average. Because the two move against each other, holding both long is what hedges each against the other.
2. **The residual’s standard deviation.** The residual is the part of each day’s ES value the fit leaves unexplained, and “The standard deviation of the residues is \$2,047.”
3. **The APR.** The annual percentage rate, the trade’s return compounded to one year, is 12.3 percent on a test set, the later days held back from the fit and used to score the trade, from 2010-07-29 to 2012-05-08.
4. **The Sharpe ratio.** The return per unit of its own variability is 1.4 on the same test set.

He leaves three choices unnamed.

1. When a position closes.
2. Which days the fit is trained on.
3. Which of his data files he ran.

None of the scripts Chan publishes prints the figures.

### What the reproduction found

This repository ran the trade on Chan’s own data, which comes as files he saved on particular dates. This post calls each one a **save** and names it by the date in its file name. A figure **lands** when it rounds to the printed one at the precision Chan printed.

Three of the four land on the 2012-05-07 save, and the residual’s standard deviation misses by \$2.09. On the 2012-05-17 save the same fit and trade miss all four. The script Chan publishes for the example fits its line on days that include the whole test set, and it never trades. Whether the trade’s figures land at all depends on when a position closes, and the APR rests on four positions in 449 days.

**Every result here is exploratory**, meaning it can point to where to look but cannot confirm anything. Reproducing Chan’s figures uses the 2008 to 2012 data to check a rule he had already chosen, so the same data cannot then test that rule as if fresh. This run chose the save and the exit because they land the printed figures, so the match is partly built in. The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The regression and the files

A futures contract expires, so a price history running for years has to be stitched from one contract after another. At each switch, called a roll, the next contract usually trades at a different price from the one expiring. A **continuous future** shifts the whole earlier history by that difference so the series has no jump at the roll. So every roll rewrites the history, and the same day can carry a different price in a file saved a week later.

Chan saved several MATLAB files of continuous futures, and three of them hold both VX and ES.

1. **The 2012-05-07 save**, `inputDataOHLCDaily_20120507.mat`. VX and ES share 1,999 trading days, from 2004-06-02 to 2012-05-08. Its last day is the last day of the book’s test set.
2. **The 2012-05-11 save.**
3. **The 2012-05-17 save**, the one Chan’s script for this example, `VX_ES.m`, loads. It also holds 1,999 common days, ending 2012-05-17.

### The specification

The regression needs one idea first. A move of one point in VX is worth \$1,000, and a move of one point in ES is worth \$50. Those are the contracts’ dollars per point. Multiplying each price by its dollars per point turns it into the dollar value of one contract. A regression of one dollar value on the other then has a slope measured in contracts, which is the number a trader can act on. In symbols, with c the intercept, h the hedge and ε the residual on day t:

```math
50 \cdot ES_t = c - h \cdot 1000 \cdot VX_t + \varepsilon_t
```

The specification has three parts.

1. **The fit.** Regress 50·ES on 1000·VX with an intercept, over the 500 common days from 2008-08-04 to 2010-07-28. Those 500 days are the training days, the only days the fit sees. That first day and that 500-day training span come from Chan’s own `VX_ES_rollreturn.m`, the script behind a later trade in the book that reuses this hedge. The slope is negative, because the two move against each other. The hedge is minus the slope.
2. **The band.** Each day the portfolio, h VX contracts and one ES contract, both long, gets a z-score. That is its distance from the intercept c, measured in standard deviations of the training residual ε. The intercept is the portfolio’s average value over the training days, so a z-score of zero means the portfolio sits at that average. The band runs from −1 to +1. When the z-score falls below −1, the rule buys one unit of the portfolio. When it rises above +1, the rule sells one unit short. When to close the position is a separate choice. This run holds a long until the z-score rises above +1 and a short until it falls below −1, the opposite edge of the band from where each began. So the day the z-score rises above +1 closes a long and opens a short, and the day it falls below −1 closes a short and opens a long. After its first entry, the run always holds a position.
3. **The test.** The 449 days from 2010-07-29 to 2012-05-08, with no trading cost. Each day’s return is the profit on yesterday’s positions divided by the dollar value both legs held, each counted as positive, as [the post on price spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md#the-rule-and-the-file) builds it. The APR compounds the daily returns to a year of 252 trading days. The Sharpe ratio is the mean daily return over its standard deviation, scaled by √252.

The top panel of the chart below redraws the book’s Figure 5.10 from the 2012-05-07 save. The two regimes sit on two separate lines, and the fit runs along the second.

![Three panels stacked. The top panel is a scatter of 50·ES against 1000·VX, both in dollars per contract, on the 1,999 days both traded. Days from 2004 to May 2008, in brass, form a band high on the panel, with ES between about 56,000 and 76,000 dollars while VX runs from about 40,000 to 75,000. Days from August 2008 to May 2012, in black, form a lower line falling from about 70,000 dollars of ES at 20,000 dollars of VX to about 38,000 at 100,000. A few pale grey days from June and July 2008 sit between the two. A red line, the fit on the 500 training days, runs along the lower group. The middle panel plots the z-score from August 2008 to May 2012, with dotted lines at plus and minus one and a dashed line at 2010-07-28. Its background is shaded green while the position is long and red while it is short. Right of the dashed line it stays shaded green and mostly below minus one until November 2011, dipping to its lowest, −3.89, on 2011-08-08, then switches between red, green and red. The bottom panel plots the test set’s cumulative return. It wanders between about minus 5 and plus 3 percent until July 2011, falls to about minus 8 percent just after a dashed red line at 2011-08-05 labelled minus 4.59 percent, and then climbs to 22.92 percent by May 2012, with three dots where the position changes. The title calls the chart exploratory, and the note names the 2012-05-07 save and says the save and the exit were chosen because they land the printed figures.](../docs/figures/vx_es.png)

*The book’s Figures 5.10 to 5.12 redrawn on Chan’s 2012-05-07 save: the two regimes, the z-score with its band, and the test set’s cumulative return.*

## Lesson 1: three figures land and the deviation misses by \$2.09

Here is each figure beside the book’s. The computed APR is written as a fraction of one, so 0.122811 is 12.28 percent.

```math
\small\begin{array}{l|r|r|l}
 & \text{Computed} & \text{Book} & \text{Verdict} \\ \hline
\text{Hedge} & 0.390594 & 0.3906 & \text{lands} \\
\text{Deviation} & \$2{,}044.91 & \$2{,}047 & \text{misses by }\$2.09 \\
\text{APR} & 0.122811 & 12.3\% & \text{lands} \\
\text{Sharpe} & 1.393201 & 1.4 & \text{lands}
\end{array}
```

The fit lands the hedge to four decimals and misses the deviation by about a tenth of a percent. Fitting on one trading day fewer, from 2008-08-05, lands both, at 0.390635 and \$2,046.93. A search of [22,446 windows, recorded in this repository’s replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-28-vx-futures-against-e-mini-futures-chans-algorithmic-trading), found that window, and it is the only one of them that rounds to both printed figures. Nothing in the code reruns that search, so both counts, the 22,446 windows and the single match, rest on that record alone. A window found by searching for the answer shows only that a window close to Chan’s exists. It cannot say which window he used, so the run keeps the one `VX_ES_rollreturn.m` names, starting 2008-08-04.

The printed hedge is also safe to reuse. Trading the rounded 0.3906 in place of the fitted 0.390594 gives an APR of 0.122810 and a Sharpe ratio of 1.393205, which changes neither figure at the precision Chan printed. The book’s next trade on these two futures, at location 2754, holds “0.3906 front contracts of VX” as a fixed number, so it trades the same portfolio to the book’s precision. Its script as published, `VX_ES_rollreturn.m`, does not trade that portfolio. Every line holding 0.3906 is turned into a comment, which MATLAB skips, and the script trades one VX contract against one ES contract.

## Lesson 2: the save decides, and the script that ships is not the run

The same specification on the other two saves misses everything. Each column below names a save by its day in May 2012. The 2012-05-11 and 2012-05-17 saves give identical figures, so they share a column. The last column is Chan’s `VX_ES.m` as published, described under the next heading, and the book’s own figures are in Lesson 1’s table.

```math
\small\begin{array}{l|r|r|r}
 & \text{May 7} & \text{May 11, 17} & \texttt{VX}\_\texttt{ES.m} \\ \hline
\text{Hedge} & 0.390594 & 0.376431 & 0.350731 \\
\text{Deviation} & \$2{,}044.91 & \$2{,}291.00 & \$2{,}373.59 \\
\text{APR} & 0.122811 & 0.056582 & \text{no trade} \\
\text{Sharpe} & 1.393201 & 0.673910 & \text{no trade}
\end{array}
```

On the 2012-05-17 save the specification trains and tests on the same dates as on the 2012-05-07 save, so what changed is the closes. The same days carry different prices, and the APR falls by more than half.

[The post on GLD and GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md#3-adjusted-close-is-not-a-fixed-number) found a hedge ratio drifting with the date its prices were downloaded, as the vendor folded years of dividends into its dividend-adjusted closing prices. A continuous future can do the same thing within days. The later save’s VX and ES closes also give a different hedge. Nothing here measured how Chan’s data source rebuilt the two legs between saves. A single roll would shift every earlier close of one leg by one amount. That moves every dot of the scatter the same distance, so the slope, and with it the hedge, stays where it was. Here the closes of the same days shift by uneven amounts, and those shifts change the slope. So a roll explains how a history like this can change, but not why the hedge moved here.

![An animated whiteboard sketch titled “One shift slides, it does not tilt”, drawn slowly stroke by stroke. It is schematic and carries no figures from the run. A grey axis across is labelled “1000·VX” and a grey axis up is labelled “50·ES”. Black dots fall from upper left to lower right, and a black line fitted through them is labelled “one save”. Brown copies of the same dots, each moved right by the same amount, follow with a brown fitted line parallel to the black one, labelled “every close + the same amount: same slope”. Red copies, each moved right by a different amount, come last, with a red fitted line, through dots spread wider, visibly less steep than the other two, labelled “uneven shifts: a different slope”. The finished drawing holds for twelve seconds.](../docs/figures/vx_es_sketch_one_shift.gif)

### The script Chan published

Chan’s `VX_ES.m`, as published at commit `e4bc46f` of the `ericnberwick/EpchanPreview` repository, does four things.

1. It loads the 2012-05-17 save.
2. It keeps the days VX and ES both traded.
3. It draws the scatter of Figure 5.10.
4. It fits the regression on every day from 2008-08-01 to the end of the file.

That fit runs over 957 days, through 2012-05-17, so it includes the whole test set. Then the script stops. It prints nothing and runs no trade, and its fit misses both printed figures a fit alone can produce, the hedge and the deviation. Two facts point to the 2012-05-07 save without using the figures.

1. The book’s test set ends on 2012-05-08, that save’s last day.
2. Chan’s `VX_ES_rollreturn.m` reads ES from that save.

A published script and the numbers printed beside it can come from different files and different runs. Here the figures land only on a save the script does not load, with a window and an exit the script does not contain.

## Lesson 3: the exit the book leaves out decides the trade

The book describes the entry and is silent about the exit. The table below compares three rules: this run’s and two variants.

1. **Opposite band**, this run’s rule, holds a long until the z-score rises above +1 and a short until it falls below −1.
2. **Mean** closes each position when the z-score crosses zero.
3. **Flat start** follows the opposite-band rule but drops the long position this run carries in from the training days, so it starts the test with no position.

```math
\small\begin{array}{l|r|r|l}
\text{Rule} & \text{APR} & \text{Sharpe} & \text{Lands} \\ \hline
\text{Opposite band} & 0.122811 & 1.393201 & \text{both} \\
\text{Mean} & 0.068463 & 0.870716 & \text{neither} \\
\text{Flat start} & 0.124916 & 1.415772 & \text{Sharpe}
\end{array}
```

Chan’s script for Example 3.2, `bollinger.m`, closes each position when the z-score crosses zero. That example trades GLD, a gold fund, against USO, an oil fund, with a band of the same kind, which Chan calls a Bollinger band. [The post on Bollinger bands](https://github.com/l3a0/quantitative-trading/blob/main/blog/bollinger-band-lessons.md#the-rule-and-the-file) reproduces that example to six digits, exit at zero included, and [the post on price spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md#lesson-5-a-return-that-cannot-see-its-own-scale) mentions it in its fifth lesson. With that exit, this trade earns 6.8 percent a year rather than 12.3.

![An animated whiteboard sketch titled “Two ways to close a position”, drawn slowly stroke by stroke. It is schematic and carries no figures from the run. Three grey dashed lines are labelled “+1”, “0” and “−1”. A black z-score path starts just above 0, dips below −1, climbs back through 0, rises above +1, falls back through 0 and dips below −1 again, then turns back up to end just above it. Beneath it, two strips follow the same path. The first, labelled “hold until the opposite band (this run)”, is a green bar marked “long” from the dip below −1 to the rise above +1, a red bar marked “short” from there to the next dip below −1, and a green bar marked “long” after it. The second, labelled “close at the mean (bollinger.m)”, is a green bar marked “long” from the dip below −1 to the crossing of 0, a short thin grey stretch marked “flat” until the rise above +1, a red bar marked “short” until the path falls back through 0, another short grey stretch marked “flat” until the next dip below −1, and a green bar marked “long” after it. The finished drawing holds for twelve seconds.](../docs/figures/vx_es_sketch_two_exits.gif)

This run carries the training position into the test. On 2010-07-28, the last training day, the z-score is −1.041, so the position is already long. `VX_ES_rollreturn.m` computes a return for every day, then drops the 500 training days and keeps the rest. So its first test day earns on the position held at the close of the last training day, and this run does the same. Starting instead with no position on the first test day lands the Sharpe ratio and misses the APR, at 12.5 percent.

Holding each position until the opposite band is the one rule of the three tried that lands both the APR and the Sharpe ratio. That is why the run uses it.

**So the result is exploratory here too.** This run chose both the save and the exit because they land the printed figures. A match built from choices made to produce it confirms that the arithmetic can reach Chan’s numbers. It cannot confirm that his run made those choices.

## Lesson 4: an APR from four bets

An APR of 12.3 percent sounds like the summary of many trades. Here it is four. The position is already long when the test begins, and it changes three times in 449 days.

```math
\begin{array}{l|l|r|r}
\text{Position} & \text{Earns from} & \text{Days} & \text{Return} \\ \hline
\text{Long} & \text{2010-07-29} & 325 & 0.058104 \\
\text{Short} & \text{2011-11-09} & 28 & 0.056144 \\
\text{Long} & \text{2011-12-20} & 41 & 0.056877 \\
\text{Short} & \text{2012-02-21} & 55 & 0.040777
\end{array}
```

The rule changes position at the close of 2011-11-08, 2011-12-19 and 2012-02-17, so each new position starts earning the next trading day, and the last one earns through 2012-05-08. The trade is in the market on all 449 test days. All four bets win, and compounded together they make the test set’s 22.92 percent. The test runs about a year and three quarters, so that gain works out to 12.3 percent a year, the APR.

Chan writes that the trade “was particularly profitable” from around Standard and Poor’s downgrade of the U.S. credit rating (location 2559). The agency announced it after the close of Friday 2011-08-05. At that close, after 259 of the 449 test days, the trade was down 4.59 percent. On Monday 2011-08-08 it reached its lowest point, down 7.76 percent, and the z-score reached −3.89, its lowest since the fit’s first day in 2008. From the close of 2011-08-05 to the end of the test, the trade grew 28.84 percent in 190 days.

So the trade earned more than its whole gain after that close, because it was already down by then. That fits Chan’s sentence. But 2011-08-05 falls one trading day before the trade’s low, and dividing the test on any day near that low would show the same thing. Such a division dates when the trade made its money. It says nothing about what the downgrade did.

The bottom panel of the chart shows that path. The first bet, the long carried in from training, spent its 325 test days earning 5.81 percent, and was down 7.76 percent at its worst along the way. It paid off only because the rule kept the position open through the worst day.

One more count suggests the test set behaved differently from training. The z-score sits below −1 or above +1 on 236 of the 449 test days, against 113 of the 500 training days. A portfolio that returned to its average as reliably in the test as in training would stray more than one standard deviation from it about as often. This one spent more than half the test outside the band.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the portfolio is stationary.** Chan argues it from a plot, Figure 5.11, and prints no statistic. This replication runs no statistical test either. The z-score spending 236 of 449 test days outside the band is a reason to doubt it rather than a result.
2. **What costs would take.** Neither the book nor this run charges any. Four positions in 449 days is few trades, but nothing here measures what a cost would do. Each unit also holds 0.39 of a VX contract, which a real account cannot hold, and nothing here measures what rounding it would change.
3. **Whether the window is the book’s.** The search found one window that lands both fitted figures, and the run uses a neighbor of it, the one `VX_ES_rollreturn.m` names. Nothing Chan printed confirms either, so the match shows a window close to his and no more.

## What this means for a trader

One habit for each lesson.

1. **Hold a reproduction to the printed precision, and say how much it misses by.** Three figures landing and one missing by \$2.09 is a more useful report than “it reproduces.”
2. **Record which file a backtest read.** A continuous future can be rewritten between saves, so a hedge fitted on one save can fail on a save made days later.
3. **Ask for the exit.** An entry rule with no exit is half a strategy, and here the half left out cuts the APR from 12.3 percent to 6.8.
4. **Count the bets behind an APR.** Four winning positions in 449 days is a sample of four, however steady the final 22.92 percent looks.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 2546, 2552, 2559 and 2754.
2. Chan, E. P. `VX_ES.m` and `VX_ES_rollreturn.m`, as published in the [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview) repository at commit `e4bc46f`.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es_whiteboard.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-28-vx-futures-against-e-mini-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside what was found here.*
