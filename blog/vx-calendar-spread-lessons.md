# Chan’s VIX calendar spread reverts on his own file, and the plainest reading of his text loses

*Chan reports that the ratio of a far VIX future to a near one returns to its average, and that trading it earned 17.7 percent a year. On his own file the ratio passes the test, the trade read most plainly from his text loses 4.0 percent a year, and one of five readings written down before the run matches his figures, which makes the match the result of a search.*

## Why trade the ratio of two VIX futures

A VIX future, which trades as VX, is a bet on the level of the VIX volatility index on its expiry date. The [post on VX against the E-mini S&P 500 future](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#why-trade-volatility-against-the-stock-index) explains what VIX measures and why a VX future moves the way it does. Ernest Chan’s *Algorithmic Trading* treats the VX future itself as not returning to any average. A calendar spread on VX owns one VX contract and sells another with a different expiry. Chan reports that this spread does return to its average, and that none of the models he tried explains why.

The model of futures prices Chan uses for crude oil “works only for a future whose underlying is a traded asset, and VIX is not one”, and none of the alternatives he tried “can explain the mean-reverting property of VX calendar spreads in the face of the non-mean reversion of the VX future itself” (Chan, 2013, location 2502). So Chan’s case that the spread returns to its average rests on the data alone. His paragraph at that location makes three claims.

1. An ADF test on “the ratio back/front of VX” finds it “stationary with a 99 percent probability”. The ADF test, short for augmented Dickey-Fuller, asks whether a series is pulled back toward an average or wanders like a random walk, whose changes carry no memory of where it has been. The back is the later-expiring of two contracts and the front the earlier. The book does not say which two contracts, and Lesson 2 turns on that.
2. His usual mean-reverting rule on that ratio, “with a 15-day look-back”, earns “an APR of 17.7 percent and a Sharpe ratio of 1.5 from October 27, 2008, to April 23, 2012”. That rule takes its side from whether the ratio sits above or below its moving average. The look-back is the number of days that average covers. The APR is the annual return, compounded. The Sharpe ratio is the mean daily return over its standard deviation, scaled to a year.
3. It “performed much more poorly prior to October 2008”.

### What the reproduction found

Chan’s published code has no script for the VX calendar spread. The script for crude oil’s calendar spread, `calendarSpdsMeanReversion.m`, opens with a commented-out line loading Chan’s VX file above the line loading crude oil, so he most likely ran that script on VX. This repository ran it the same way, on that file.

The results fall into four groups. Each result rests on a reading, meaning one way of filling in what the book’s text leaves open.

1. **The ratio passes the stationarity test, and the plainest reading of the text loses.** The trade that reading describes returns −4.0 percent a year where the book prints 17.7 percent.
2. **The signal reads one pair of contracts while the trade holds another.** The near contract of the pair the script holds is usually the second to the fifth contract still trading, while the ratio its signal reads is that of the front pair, the two nearest contracts.
3. **One of five readings written down before the run matches the book’s figures.** This repository picked it out after seeing all five, so the match is the result of a search and confirms nothing.
4. **The script runs on VX without complaint while rarely trading a spread.** Run as Chan published it, the script holds the near contract alone on most of the days it holds anything.

**Every result here is exploratory.** Chan chose the instrument, the signal, the rule and the dates, and the reproduction runs them on his own file. It can say whether his numbers follow from that file under some reading of his text, and nothing about whether the trade would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## What changes from crude oil

The [post on Chan’s crude oil calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md) works through `calendarSpdsMeanReversion.m` line by line: how it picks a pair of contracts on each day, how the sign of a z-score decides the side, how it halves the daily return because there are two contracts, and how it measures a drawdown. This post covers what the VX run needs and what is different on VX.

Two more posts build up the tools used here. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds up the z-score, the number of moving standard deviations a series sits from its moving average. The [post on the stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) explains the ADF test and the half-life.

Each pair has two legs. The near leg is the contract that expires first and the far leg the one that expires later. The front contract is the nearest one still trading. The script holds each pair for a stretch of days, then switches to the next pair, which is called a roll. Four things change from crude oil.

1. **The signal is a ratio of prices.** On crude oil the script trades γ, the roll return. That is the part of a contract’s return that comes from its price converging on the spot price as it nears expiry, a separate idea from the roll between pairs. A model fits γ across the five nearest contracts each day, and the [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#the-model-and-the-files) builds that model up. VIX has no such model, so the signal is the price of the back contract divided by the price of the front one. Its log is log(back) − log(front), the gap between the two log prices. A spread long the back contract and short the front, meaning it owns the back and has sold the front, earns, as the script counts its returns, on exactly the days that gap widens. So the ratio rises when that spread earns and falls when it loses.
2. **Reversing the position when the signal is high can now bet on reversion.** The script starts every day long the far contract and short the near one, and reverses both legs wherever the z-score is above 0. The crude oil post’s [second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md#lesson-2-the-trade-bets-the-spread-moves-further-from-its-average) measures that on crude oil the spread mostly falls as γ rises. So when γ sits above its average the spread usually sits below its own, and the flip sells it then, a bet that the spread moves further from its average. Here, when the signal is the ratio of the pair the script holds, the flip sells that spread when the ratio is above its 15-day average. That is the bet on reversion the book describes. Lesson 2 measures how often the signal is that ratio.
3. **The pair is one month apart.** The crude oil script pairs each contract with the one expiring 12 months later. Chan’s VX file prices only 2 to 10 contracts on any day, so 12 months apart rarely finds both legs priced. Lesson 4 measures what pairing 12 months apart does on VX.
4. **The file holds single contracts and no price for the VIX index itself.** It is `inputDataDaily_VX_20120507.mat`, the file the commented-out line names, saved 2012-05-08 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). It holds 72 contracts, one for each month from January 2007 to December 2012, over 1,543 days from 2006-03-23 to 2012-05-07. Each contract keeps its own prices. The VX against E-mini post read a different kind of file, a [continuous future](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) stitched from one contract after another.

## Five readings of the book’s text

The book names VX, the ratio, the 15-day lookback and the window, and leaves the rest to the reader. So before any APR, Sharpe ratio or ADF statistic on VX was computed, this repository wrote down one reading of the text, called S, and four more beside it. Writing all five down first means none could have been tuned to match. Picking the one that matches is still a choice made after the run, and Lesson 3 weighs it.

1. **S, the plainest reading.** The script holds each pair for at least 63 days, its own minimum, and S makes five edits to it.
   1. The VX file.
   2. Contracts one month apart.
   3. The ratio of the front pair, the nearest two priced contracts, as the signal.
   4. The 15-day lookback.
   5. The window from 2008-10-27 to the file’s last day, 2012-05-07, which is 889 days.
2. **B1** trades the ratio of the pair the script holds that day, the far contract over the near one, instead of the ratio of the nearest two. The script’s own comment calls the held pair’s far and near contracts the back and the front.
3. **B2** sets the minimum holding period to 0, so each pair is held from the day after the previous pair ends to 10 days before its own near contract expires.
4. **B3** is B1’s signal with B2’s holding period.
5. **B4** is S measured to 2012-04-23, the book’s end date, 879 days.

When a reading matches the book’s figures and S does not, the replication reports that reading and keeps S as the reading the results are judged on. The rules that decide each result are in [Entry 35 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-35-vix-futures-calendar-spreads-on-the-ratio-of-back-to-front-chans-algorithmic-trading), which records each figure beside the code check that computes it.

## Lesson 1: the ratio is stationary, and the plainest reading of the text loses

The first claim holds. A critical value is the figure an ADF statistic must fall below for the test to reject a random walk at a given level. The ADF statistic of S’s ratio is −5.568107, against a 1 percent critical value of −3.4583, so the test rejects a random walk at the level “99 percent” names, with a margin of 2.109807. The test reads all 1,395 days on which the ratio can be computed, from 2006-10-23.

The second claim does not. This post’s tables give the APR and the maximum drawdown as fractions, so −0.040454 in the table below is −4.0 percent. In that table, the half-life is the number of days a gap from the average takes to close halfway, and the maximum drawdown is the deepest fall from a previous high.

```math
\small\begin{array}{l|r|r}
\text{Figure} & \text{S} & \text{Book} \\ \hline
\text{ADF statistic} & -5.568107 & \text{99 percent} \\
\text{Half-life, days} & 13.036829 & \text{none printed} \\
\text{APR} & -0.040454 & 17.7 \text{ percent} \\
\text{Sharpe ratio} & -0.563912 & 1.5 \\
\text{Maximum drawdown} & -0.255618 & \text{none}
\end{array}
```

The book prints no half-life for VX. The script sets its lookback to the half-life rounded, which here would be 13 days. The book gives the lookback as 15 days, and S uses 15.

The APR is −4.0 percent and the Sharpe ratio is −0.56, so both miss with the wrong sign. The file is Chan’s own, so a different download cannot explain the gap. Measuring S to the book’s end date instead, which is B4, lowers the APR by 0.000451, which is 0.0451 percentage points, and the Sharpe ratio by 0.003199. So the window does not explain it either. What remains is mainly the reading of the text, and Lesson 2 measures one place where S’s reading may differ from the one Chan ran.

The ADF test says the ratio returns to a long-run level. The trade earns only if the position it takes on each day pays when the ratio moves back over the following days, and S’s does not.

## Lesson 2: the signal reads one pair and the trade holds another

The script holds each pair for at least 63 days and lets it go 10 days before its near contract’s last trading day, so it opens each pair at least 73 days before that day. VX contracts expire every month, so 73 trading days before a contract expires, three earlier contracts are still trading. S opens most of its pairs earlier than that, when four are. The pair the script holds is therefore usually not the front pair. S’s signal reads the front pair all the same, because that is what the book’s “ratio back/front” most plainly means.

![A whiteboard sketch titled “S holds one pair while its signal reads four”, drawn slowly and holding its finished drawing for twelve seconds. A grey trading-day axis runs along the bottom from early February to late May 2009, with a grey tick below it at each front contract’s last priced day, named and dated under it: “VX-2009G” and “Feb, 02-18”, “VX-2009H” and “Mar, 03-18”, “VX-2009J” and “Apr, 04-15”, and “VX-2009K” and “May, 05-20”. A grey note at the bottom reads “each tick: a contract’s last priced day, which the script takes as its expiry”. A thick black bar near the top, with “S holds” on its left and “near VX-2009K, far VX-2009M: 02-04 to 05-06, 64 days” above it, ends before the VX-2009K tick, and a thin grey bracket runs from its end to that tick, labelled “10 days to its” and “last priced day”. Under the bar a row of four thin black spans gives the near leg’s place among the contracts priced each day: “4th” above the first, with “near leg’s place” on its left and “10 days” below it, then “3rd” with “20 days”, “2nd” with “19 days”, and “front” above the last, which sits in a pale green box with a green edge labelled “same pair: 15 days” in green. Under that a row of four brown spans gives the front pair the signal reads, each ending at its front contract’s tick: “G and H”, with “signal reads” on its left, then “H and J”, “J and K” and “K and M”, the last running past the end of the black bar to the VX-2009K tick.](../docs/figures/vx_calendar_spread_sketch_one_hold.gif)

On the 847 days from 2008-10-27 on which S holds a pair, its near leg is the front contract on 126. On the rest it is the second to the fifth contract still trading. So on six days in seven, S trades one pair on the z-score of another.

```math
\begin{array}{c|r}
\text{Near leg's place} & \text{Days held by S} \\ \hline
1 & 126 \\
2 & 229 \\
3 & 221 \\
4 & 201 \\
5 & 70
\end{array}
```

S holds 11 pairs in that time. The near leg of the first is VX-2009G, the February 2009 contract, and of the last VX-2012H, the March 2012 one, and each pair starts three or four months after the one before.

### What the readings beside S earn

Three of the four readings beside S change which pair the signal reads, how each pair is held, or both. B4 changes only the end date, so the table leaves it out.

1. **B1** reads the held pair’s own ratio.
2. **B2** sets the minimum holding period to 0 and holds each pair in turn from 2008-10-27. Its near leg is the front contract on 459 of its 879 held days and the second on the other 420. Those 420 are the first 10 days after each of its 42 rolls in that time, while the old near contract still trades.
3. **B3** does both.

```math
\small\begin{array}{l|l|r|r}
\text{Reading} & \text{Signal} & \text{APR} & \text{Sharpe} \\ \hline
\text{S} & \text{front pair} & -0.040454 & -0.563912 \\
\text{B1} & \text{held pair} & 0.033430 & 0.510861 \\
\text{B2} & \text{front pair} & -0.113153 & -0.990744 \\
\text{B3} & \text{held pair} & 0.173462 & 1.457009
\end{array}
```

The two readings whose signal reads the pair they hold are the two that earn. That is a pattern across four readings written down in advance, and four cannot establish a cause. B2 also argues against treating the pattern as a cause. Its signal reads the pair it holds on 459 of its 879 days, against S’s 126 of 847, and it loses more than S does. So the logic of the bets suggests a reason, without settling it. A rule that sells a spread when its own z-score is high bets on that spread reverting. A rule that sells one spread when another spread’s z-score is high bets on the two moving together, which nothing here tested.

## Lesson 3: one reading of five matches the book, and that is a search

B3 matches the book’s figures on the book’s own window. Measured to 2012-04-23, the book’s end date, its APR is 0.176952 and its Sharpe ratio 1.475658, which round to the printed 17.7 percent and 1.5. Measured to the file’s last day, they are 0.173462 and 1.457009. That APR is 17.3 percent, which misses 17.7 percent by 0.4 percentage points at the book’s precision.

![Two charts. The top chart shows the cumulative compounded return of four ways of trading the VX calendar spread from late October 2008 to early May 2012. A solid black line, B3, climbs from zero to about 50 percent by mid 2010, falls back to about 40 percent late that year, and ends near 76 percent. A brown line, S, stays below zero from September 2009 and ends near −14 percent. A dashed grey line, B1, rises to about 20 percent in 2009 and ends near 12 percent. A dotted grey line, B2, stays near zero until September 2009, then falls and ends near −35 percent. A dashed vertical mark labels 2012-04-23 as the book’s end. The bottom chart is a bar chart of each reading’s APR before October 2008 beside its APR from 2008-10-27. S shows −2.8 and −4.0 percent, B1 20.4 and 3.3, B2 −1.9 and −11.3, and B3 −7.4 and 17.3. Only B3’s bar before October 2008 is lower than its bar after. The title calls the result exploratory.](../docs/figures/vx_calendar_spread.png)

*The top panel redraws the book’s Figure 5.8, “Cumulative Returns of Linear Mean Reversion Strategy on VX Calendar Spread”, for the four readings that run to the file’s last day. The bottom panel is the book’s third claim, measured on each of them.*

Two things single B3 out from the other four readings.

1. **It rounds to both printed figures**, on the book’s window.
2. **It is the only reading that does worse before October 2008**, as the book’s third claim says. From its first held day, 2007-01-23, to 2008-10-24, its APR is −0.074173 and its Sharpe ratio −0.562291. S, B1 and B2 each do better before October 2008 than after. The bottom panel shows it.

A third thing looks like evidence for B3 and is not. B3’s last held day is 2012-04-23, the book’s printed end date, and so is B2’s. VX-2012K is the May 2012 contract. It is the near leg of the last pair B2 and B3 hold, and it still trades on the file’s last day. The script marks a contract as expired on the last day it has a price, so it reads 2012-05-07 as VX-2012K’s expiry and lets go of the pair 10 days earlier, on 2012-04-23. So the book’s end date is what holding each pair in turn produces on this file. That is evidence for the way B2 and B3 hold pairs, and it does not tell the two apart.

This repository picked B3 out after seeing all five readings, and measured it on the book’s window because it had come closest on the window that runs to the file’s last day. Choosing the best of several readings after seeing them is a search. Each extra reading is another chance for one to match by luck, so the match confirms nothing. What would confirm B3 is a test written down before it runs, on VX prices after 2012-05-07 that Chan never saw, with costs charged.

## Lesson 4: a script runs on a file it was not written for

The script as Chan published it pairs each contract with the one expiring 12 months later, which suits crude oil. Uncommenting the VX load line and commenting out the crude oil one loads a file that prices at most 10 contracts on any day. The script raises no error. It builds its schedule, holds positions, and prints an APR.

Run on VX with Chan’s 12-month spacing, its schedule holds a pair on 1,284 days. Both legs have a price on 84 of them. On 1,183 only the near leg is priced, and on 17 neither is. The script sums the returns of the legs that have one and skips the rest, so on those 1,183 days any position it takes is one VX contract outright, which is not a calendar spread at all. The number it prints at the end looks like any other APR.

![A whiteboard sketch titled “On 2010-01-04 the far leg has no price”, drawn slowly and holding its finished drawing for twelve seconds. A row of sixteen boxes runs across the board, lettered F to Z and then F to J, one for each VX contract from January 2010 to April 2011: eight solid boxes in black for the contracts priced that day, then eight dashed boxes in grey for the rest. A grey note near the bottom reads “letters are months: F to Z run Jan to Dec 2010, then F to J run Jan to Apr 2011”. A grey bracket under the eight solid boxes reads “priced that day: 8 contracts”. A brown ring circles the fourth box, J, with “near: VX-2010J” in brown below it. A brown arrow arcs from the ring over the row, labelled “+12 months”, to the last dashed box, with “far: VX-2011J, no price” in red below it. Two grey lines under the note close it: “the script adds up the legs that have a price, so it holds VX-2010J alone” and “near leg alone on 1,183 of 1,284 held days”.](../docs/figures/vx_calendar_spread_sketch_twelve_apart.gif)

That is why S changes the spacing to one month. The book’s text does not say so. It follows from the file, which prices 2 to 10 contracts a day with a median of 8.

## What this replication cannot say

Every result here is exploratory. The reproduction shows that Chan’s file supports his stationarity claim, that the plainest reading of his text misses his trade with the wrong sign, and that one of five readings matches his figures. Four questions are beyond it.

1. **Which rule Chan ran.** The book names VX, the ratio, the 15-day lookback and the window. The rest of S is this repository’s reading, and B3 is a different reading that happens to match the book’s figures.
2. **Whether B3 is more than the best of five.** It was found by looking at five readings, and only a test written down in advance and run on later data could say more.
3. **The ADF statistic Chan saw.** The book prints none, so the replication checks the “99 percent” and not a number.
4. **Anything about costs.** None is charged. From 2008-10-27, B3 holds 43 pairs and enters 42 of them, since the first was already open on that day. Each new pair’s near contract is the old pair’s far one. A roll closes the old near contract, opens the new far one, and trades the shared contract only if it changes side, from long to short or back. So a roll trades two contracts when that contract keeps its side and four when it switches. B3 also reverses both legs on 109 days between rolls, each one a day its z-score crosses 0, and those reversals are most of the contracts it trades.

## What this means for a trader

Each lesson leaves one habit.

1. **Test the trade, not just the signal.** A stationary signal says the series comes back. Only the trade’s returns say whether the position taken on each day pays.
2. **Check that the signal reads what the trade holds.** When a rule picks its pair by one schedule and its signal by another, measure how often the two agree. Here they agreed on 126 of 847 held days.
3. **Write the readings down before the run, and report all of them.** When one of several matches, say how many were tried, and treat the one that matched as the next thing to test rather than as the answer.
4. **Check the data a script runs on against the data it was written for.** A script that runs without error on a new instrument can still be computing something else. Count how often each leg has a price before reading any figure it prints.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.4, Figure 5.8, and Kindle location 2502.
2. `calendarSpdsMeanReversion.m`, at commit `e4bc46f` of [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview), a public copy of Chan’s code.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_calendar_spread.py), [the script it runs](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_calendar_spread_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_calendar_spread.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_calendar_spread_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-35-vix-futures-calendar-spreads-on-the-ratio-of-back-to-front-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
