# Chan’s VIX calendar spread reverts on his own file, and the trade his text describes loses

*Chan reports that the ratio of a far VIX future to a near one returns to its average, and that trading it earned 17.7 percent a year. On his own file the ratio passes the test, the trade read from his text loses 4.0 percent a year, and one of five readings written down before the run lands his figures, which makes the match the result of a search.*

## Why trade the ratio of two VIX futures

A VIX future, which trades as VX, is a bet on the level of the VIX volatility index on its expiry date. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#why-trade-volatility-against-the-stock-index) explains what VIX measures and why a VX future moves the way it does. Ernest Chan’s *Algorithmic Trading* finds that a VX price does not return to any average, so a bet on it reverting has nothing to stand on. He reports that the spread between two VX contracts does revert, and that nothing explains why.

The model of futures prices Chan uses for crude oil “works only for a future whose underlying is a traded asset, and VIX is not one”, and none of the alternatives he tried “can explain the mean-reverting property of VX calendar spreads in the face of the non-mean reversion of the VX future itself” (Chan, 2013, location 2502). So the evidence is the data alone. The same paragraph makes three claims.

1. An ADF test on “the ratio back/front of VX” finds it “stationary with a 99 percent probability”.
2. His usual mean-reverting rule on that ratio, “with a 15-day look-back”, earns “an APR of 17.7 percent and a Sharpe ratio of 1.5 from October 27, 2008, to April 23, 2012”.
3. It “performed much more poorly prior to October 2008”.

No script ships for this trade. The script for crude oil’s calendar spread, `calendarSpdsMeanReversion.m`, opens with a commented-out line loading Chan’s VX file above the line loading crude oil, so he ran that script on VX. This repository ran it the same way, on that file.

The results fall into four groups.

1. **The ratio passes the stationarity test, and the trade the text describes loses.** It returns −4.0 percent a year where the book prints 17.7 percent.
2. **The signal reads one pair of contracts while the trade holds another.** The pair the script holds is usually two to five contracts out, while the ratio it trades on is the front two.
3. **One of five readings lands the book’s figures.** It was picked out after seeing all five, so the match is the result of a search and confirms nothing.
4. **The script runs on VX without complaint while pairing nothing.** As shipped, it holds the near contract alone on most of the days it holds anything.

**Every result here is exploratory.** Chan chose the instrument, the signal, the rule and the dates, and the reproduction runs them on his own file. It can say whether his numbers follow from that file under some reading of his text, and nothing about whether the trade would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## What changes from crude oil

An earlier post on Chan’s crude oil calendar spread works through `calendarSpdsMeanReversion.m` line by line: how it picks a pair of contracts on each day, how its z-score decides the side, how it halves the daily return because there are two contracts, and how it measures a drawdown. This post covers only what is different on VX. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds up the z-score, the number of moving standard deviations a series sits from its moving average. The [post on the stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) explains the ADF test and the half-life.

Four things change.

1. **The signal is a ratio of prices.** On crude oil the script trades γ, the roll return a fitted model reads off the five nearest contracts. VIX has no such model, so the signal is the price of the back contract divided by the price of the front one. Its log is log(back) − log(front), which is the log value of a spread long the back contract and short the front. So the ratio rises when the spread rises.
2. **The script’s flip can now bet on reversion.** The script starts every day long the far contract and short the near one, and reverses both legs wherever the z-score is above 0. On crude oil the spread falls as γ rises, so that flip bets on the spread moving further from its average. Here the ratio rises with the spread, so when the signal is the ratio of the pair the script holds, the flip sells that spread when it is high. That is the bet on reversion the book describes. Lesson 2 measures how often the signal is that ratio.
3. **The pair is one month apart.** The crude oil script pairs each contract with the one expiring 12 months later. Chan’s VX file prices only 2 to 10 contracts on any day, so 12 months apart rarely finds both legs priced. Lesson 4 measures what that does.
4. **The file holds single contracts and no index.** It is `inputDataDaily_VX_20120507.mat`, the file the commented-out line names, saved 2012-05-08 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). It holds 72 contracts, one for each month from January 2007 to December 2012, over 1,543 days from 2006-03-23 to 2012-05-07. Each contract keeps its own prices. The VX against E-mini post read a different kind of file, a [continuous future](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) stitched from one contract after another.

The book names VX, the ratio, the 15-day lookback and the window, and leaves the rest to the reader. So before any APR, Sharpe ratio or ADF statistic on VX was computed, this repository wrote down one reading of the text, called S, and four rows beside it. A row is one way of running the script. Writing all five down first means a row that lands cannot have been tuned to land.

1. **S, the specification.** The script with five edits: the VX file, contracts one month apart, the ratio of the nearest two priced contracts as the signal, the 15-day lookback, and the window from 2008-10-27 to the file’s last day, 2012-05-07, which is 889 days. Each pair is held for 63 days, as the script sets it.
2. **B1** trades the ratio of the pair the script holds that day, the far contract over the near one, instead of the nearest two. The script’s own comment calls those two the back and the front.
3. **B2** sets the holding period to 0, so each pair is held from the day after the previous pair ends to 10 days before its own near contract expires.
4. **B3** is B1’s signal with B2’s holding period.
5. **B4** is S measured to 2012-04-23, the book’s end date, 879 days.

A row beside S that lands while S misses is reported and not promoted to the specification. The rules that decide each result are in [Entry 35 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-35-vix-futures-calendar-spreads-on-the-ratio-of-back-to-front-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the ratio is stationary, and the trade the text describes loses

The first claim holds. The ADF statistic of S’s ratio is −5.568107, against a 1 percent critical value of −3.4583, so the test rejects a random walk at the level “99 percent” names, with a margin of 2.109807. The test reads all 1,395 days on which the ratio can be computed, from 2006-10-23.

The second claim does not.

```math
\begin{array}{l|r|r}
\text{Figure} & \text{S, computed} & \text{Book} \\ \hline
\text{ADF statistic} & -5.568107 & \text{a 99 percent claim} \\
\text{Half-life, days} & 13.036829 & \text{none, a 15-day lookback} \\
\text{APR} & -0.040454 & 17.7 \text{ percent} \\
\text{Sharpe ratio} & -0.563912 & 1.5 \\
\text{Maximum drawdown} & -0.255618 & \text{none}
\end{array}
```

The APR is −4.0 percent and the Sharpe ratio is −0.56, so both miss with the wrong sign. The file is Chan’s own, so a different download cannot explain the gap. Measuring S to the book’s end date instead, which is B4, changes the APR by 0.000451 and the Sharpe ratio by 0.003199. So the window does not explain it either. What remains is the reading of the text, and Lesson 2 shows where that reading goes wrong.

A stationary signal does not make a profitable trade. The ADF test says the ratio returns to a long-run level. The trade earns only if the position it takes on each day pays when the ratio moves back over the following days, and S fails that.

## Lesson 2: the signal reads one pair and the trade holds another

The script holds each pair for at least 63 days and lets it go 10 days before its near contract’s last trading day, so it takes each pair on at least 73 days before that day. VX contracts expire every month, so 73 trading days before a contract expires, three or four earlier contracts are still trading. The pair the script holds is therefore usually not the front pair. S’s signal reads the front pair all the same, because that is what the book’s “ratio back/front” most plainly means.

On the 847 days from 2008-10-27 on which S holds a pair, its near leg is the front contract on 126. On the rest it is the second to the fifth contract still trading.

```math
\begin{array}{l|r|r|r|r|r}
\text{Near leg's place among priced contracts} & 1 & 2 & 3 & 4 & 5 \\ \hline
\text{Days held by S} & 126 & 229 & 221 & 201 & 70
\end{array}
```

S holds 11 pairs in that time, from VX-2009G’s to VX-2012H’s, each three or four months after the last. So on six days in seven, S trades one pair on the z-score of another.

The four rows beside it each change one or both of those choices. B1 reads the held pair’s own ratio. B2 holds every pair in turn, so its near leg is the front contract on 459 of its 879 held days and the second on the other 420, the 10 days after each roll while the old near contract still trades. B3 does both.

```math
\begin{array}{l|l|l|r|r}
\text{Row} & \text{Signal} & \text{Pairs held} & \text{APR} & \text{Sharpe} \\ \hline
\text{S} & \text{front pair} & \text{every 63 days} & -0.040454 & -0.563912 \\
\text{B1} & \text{held pair} & \text{every 63 days} & 0.033430 & 0.510861 \\
\text{B2} & \text{front pair} & \text{each in turn} & -0.113153 & -0.990744 \\
\text{B3} & \text{held pair} & \text{each in turn} & 0.173462 & 1.457009
\end{array}
```

The two rows whose signal reads the pair they hold are the two that earn. That is a pattern across four rows written down in advance, and four rows cannot establish a cause. It is the explanation the arithmetic suggests. A rule that sells a spread when its own z-score is high bets on that spread reverting. A rule that sells one spread when another spread’s z-score is high bets on the two moving together, which nothing here tested.

## Lesson 3: one row of five lands, and that is a search

B3 lands. Its APR of 0.173462 and Sharpe ratio of 1.457009 run to the file’s last day. Measured on the book’s own window, to 2012-04-23, they are 0.176952 and 1.475658, which round to the printed 17.7 percent and 1.5. To the file’s end its APR misses 17.7 percent by 0.4 percent at the book’s precision.

![Two charts. The top chart shows the cumulative compounded return of four ways of trading the VX calendar spread from late October 2008 to early May 2012. A solid black line, B3, climbs from zero to about 40 percent by mid 2010, dips, and ends near 76 percent. A brass line, S, drifts below zero from late 2009 and ends near −14 percent. A dashed grey line, B1, rises to about 20 percent in 2009 and ends near 12 percent. A dotted grey line, B2, falls steadily and ends near −35 percent. A dashed vertical mark labels 2012-04-23 as the book’s end. The bottom chart is a bar chart of each row’s APR before October 2008 beside its APR from 2008-10-27. S reads −2.8 and −4.0 percent, B1 20.4 and 3.3, B2 −1.9 and −11.3, and B3 −7.4 and 17.3. Only B3’s bar before October 2008 is lower than its bar after. The title calls the result exploratory.](../docs/figures/vx_calendar_spread.png)

*The top panel redraws the book’s Figure 5.8, “Cumulative Returns of Linear Mean Reversion Strategy on VX Calendar Spread”, for the four rows that run to the file’s last day. The bottom panel is the book’s third claim, measured on each of them.*

Two things single B3 out from the other four rows.

1. **It rounds to both printed figures**, on the book’s window.
2. **It is the only row that does worse before October 2008**, as the book’s third claim says. From its first held day, 2007-01-23, to 2008-10-24, its APR is −0.074173 and its Sharpe ratio −0.562291. S, B1 and B2 each do better before October 2008 than after. The bottom panel shows it.

A third thing looks like evidence and is not. B3’s last held day is 2012-04-23, the book’s printed end date, and so is B2’s. VX-2012K, the near leg of the last pair B2 and B3 hold, still trades on the file’s last day. The script marks a contract as expired on the last day it has a price, so it reads 2012-05-07 as VX-2012K’s expiry and lets go of the pair 10 days earlier, on 2012-04-23. That date is evidence for holding each pair in turn, which B2 and B3 share, and does not tell them apart.

B3 was picked out after seeing all five rows, and the book’s window was measured because B3 had come closest on the file’s. Choosing the best of several readings after seeing them is a search. Each extra reading is another chance for one to land by luck, so the match carries no verdict. What would confirm B3 is a test written down before it runs, on VX prices after 2012-05-07 that Chan never saw.

## Lesson 4: a script runs on a strip it was not written for

The script as shipped pairs each contract with the one 12 columns later, which on crude oil is a year out. On VX the commented-out load line swaps in a file that prices at most 10 contracts on any day. The script raises no error. It builds its schedule, holds positions, and prints an APR.

Run on VX with the shipped setting, it holds a pair on 1,284 days. Both legs have a price on 84 of them. On 1,183 only the near leg has one, and on 17 neither does. The script sums the legs that have a return and skips the ones that do not, so on those 1,183 days it holds one VX contract outright, which is not a calendar spread at all. The number it prints at the end looks like any other APR.

That is why S changes the spacing to one month. The book’s text does not say so. It follows from the file, which prices 2 to 10 contracts a day with a median of 8.

## What this replication cannot say

Four questions are beyond it.

1. **Which rule Chan ran.** The book names VX, the ratio, the 15-day lookback and the window. The rest of S is this repository’s reading, and B3 is a different reading that happens to land.
2. **Whether B3 is more than the best of five.** It was found by looking at five rows, and only a registered test on later data could say more.
3. **The ADF statistic Chan saw.** The book prints none, so the replication checks the “99 percent” and not a number.
4. **Anything about costs.** None is charged. From 2008-10-27, B3 holds 43 pairs and enters 42 of them, and each roll trades four contracts, closing one pair and opening the next.

## What this means for a trader

One habit for each lesson.

1. **Test the trade, not just the signal.** A stationary signal says the series comes back. Only the trade’s returns say whether the position taken on each day pays.
2. **Check that the signal reads what the trade holds.** When a rule picks its pair by one schedule and its signal by another, measure how often the two agree. Here they agreed on 126 of 847 held days.
3. **Write the readings down before the run, and report all of them.** When one of several lands, say how many were tried, and treat the one that landed as the next thing to test rather than as the answer.
4. **Check the data a script runs on against the data it was written for.** A script that runs without error on a new instrument can still be computing something else. Count how often each leg has a price before reading any figure it prints.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.4, Figure 5.8, and Kindle location 2502.
2. `calendarSpdsMeanReversion.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_calendar_spread.py), [the script it runs](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_calendar_spread_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_calendar_spread.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_calendar_spread_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-35-vix-futures-calendar-spreads-on-the-ratio-of-back-to-front-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
