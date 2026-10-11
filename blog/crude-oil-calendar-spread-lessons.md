# Chan’s crude oil calendar spread reproduces on his own file, and its trade bets against the reversion its comments describe

*Example 5.4 of Algorithmic Trading trades the spread between crude oil contracts a year apart. On Chan’s own file the book’s figures reproduce, the figures in the script’s comment need a start one day later, and the trade that earns them bets on the spread moving away from its average rather than back.*

## Why trade the roll return

Two futures contracts on the same commodity, one expiring a year after the other, both track the same barrel of oil. So the gap between their prices looks like a candidate for a trade that bets on a gap returning to its average, called mean reversion. Ernest Chan’s *Algorithmic Trading* says the intuition usually fails: calendar spreads “do not generally mean-revert” (Chan, 2013, location 2321).

His reason is the roll return, the part of a futures contract’s return that comes from its price converging on the spot price, the price of the commodity for delivery today, as it nears expiry. Under the book’s model of futures prices, the gap between two contracts’ log prices depends only on that roll return. The calendar spread’s signal “does not depend at all on the spot price, only on the roll return!” (Chan, 2013, location 2453). A spread built on oil therefore trades oil’s roll return and none of oil’s price.

Chan then finds a spread that does revert. He runs the augmented Dickey-Fuller (ADF) test, which asks whether a series is pulled back toward an average, on crude oil’s 12-month calendar spread. He finds it “stationary with 99 percent probability, and a half-life of 36 days”, the half-life being the time a gap from the average takes to close halfway. His usual mean-reverting rule then earns “an APR of 8.3 percent and a Sharpe ratio of 1.3 from January 2, 2008, to August 13, 2012” (Chan, 2013, location 2461). The APR is the compounded annual return, and the Sharpe ratio is the return per unit of its volatility. Example 5.4 describes the backtest, the run of the rule on past prices, and Chan published its script, `calendarSpdsMeanReversion.m`. This repository transcribed it line by line and ran it on the file it loads.

The results fall into four groups.

1. **The book’s figures reproduce.** The half-life, the APR, the Sharpe ratio and both drawdown figures match the book or the script’s comment, and the stationarity claim holds. A drawdown is a fall from the highest value reached so far.
2. **The figures in the script’s comment need a start one day later.** Its APR and Sharpe ratio land to every digit only when the window starts on 2008-01-03 rather than the 2008-01-02 the script states.
3. **The trade bets against the reversion its comments describe.** The spread moves opposite to the roll return, and the script reverses its position wherever the roll return sits above its recent average. So it mostly sells the spread when the spread is low. Reversing every position loses 8.0 percent a year, and trading the spread’s own reversion loses too.
4. **The last three months earn nothing.** Contracts still trading when the file was saved look expired on its last day, so the trade lets go of its last pair in May 2012.

**Every result here is exploratory.** Chan chose the commodity, the spread, the rule and the dates, and the reproduction runs them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the trade would pay after 2012.

An [earlier post on Chan’s calendar spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) tested his first book’s claim that calendar spreads cointegrate, on one-month spreads of natural gas and gasoline. It borrowed this example’s 36-day half-life as a speed of reversion to simulate, and ran no trade. This post reproduces that half-life and runs the trade. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The spread, the signal and the file

Six ideas set up everything that follows.

1. **A futures contract and its expiry.** A futures contract is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, and each stops trading at its expiry. A position held for longer than one contract’s life has to move to the next one, which is called a roll. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) shows what a roll does to a price history stitched from one contract after another. This trade stitches nothing. It holds named contracts and moves to the next pair on a schedule.
2. **The roll return.** Contracts with different expiries trade at different prices, and each has to converge on the spot price by its expiry. So a futures position earns a return “even if the underlying spot price remains unchanged”, and that return is the roll return (Chan, 2013, location 2326). When near contracts trade above far ones, called backwardation, the roll return is positive. When they trade below, called contango, it is negative.
3. **The model.** Location 2364 writes a model of futures prices, crediting Hull (1997), in which the roll return is a constant γ. A contract expiring at T is worth the spot price S(t) times a factor that converges to 1 as t reaches T. The first equation below the list writes it out. Chan’s Example 5.3 estimates γ on each day by regressing the log prices of the five nearest contracts on their time to maturity in months. γ is −12 times the slope, which turns a monthly rate into an annual one, so γ is positive in backwardation, where the far contracts are cheaper. On crude oil, the West Texas Intermediate (WTI) futures that trade as CL, γ moves slowly from day to day. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#the-model-and-the-files) works through the model and Chan’s estimates for five futures, and its Lesson 4 shows how far CL’s γ drifts.
4. **The calendar spread.** A calendar spread is long one contract, meaning it has bought it, and short another, meaning it has sold it, on the same underlying commodity with a different expiry (Chan, 2013, location 2449). The two contracts are its legs. Under the model, the spot price cancels from the log value of a spread long the far contract and short the near one, which is location 2453’s point. The second equation below the list writes it out.
5. **The signal and the rule.** The script measures γ’s half-life, the time a gap from its average takes to close halfway, and rounds it to a lookback of 36 days. Each day it computes γ’s z-score, the number of 36-day moving standard deviations γ sits from its 36-day moving average. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds the z-score up, and the [post on the stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) explains how the ADF test reads and where the half-life comes from. The script starts every day long the far contract and short the near one, and reverses both legs wherever the z-score is above 0. Chan calls this his linear mean-reverting strategy, but the position here is always one unit of the spread. Only the z-score’s sign matters, not its size.
6. **The schedule.** Contract c is held short against contract c + 12 long, so the two expire a year apart. Each pair is held to 10 trading days before its near contract’s last priced day. The first pair starts 73 days before that day, and each later pair starts the day after the last one ended. A later pair is held only when at least 63 days separate its first day from its last, and is skipped otherwise. Each day’s return is yesterday’s position times each leg’s percent change, summed and halved because there are two contracts. No cost is charged.

The model writes a contract expiring at T as

```math
F(t, T) = S(t)\, e^{\gamma (t - T)}
```

Under it, the log value of a spread long the far contract, expiring at T₂, and short the near one, expiring at T₁, is

```math
\log F(t, T_2) - \log F(t, T_1) = \gamma\,(T_1 - T_2)
```

T₂ is later, so T₁ − T₂ is negative, and the spread’s log value is minus γ times the gap between the expiries. When γ rises, the spread falls.

The data is the file the script loads, `inputDataDaily_CL_20120813.mat`, saved 2012-08-14 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). It holds 89 CL contracts, one for each month from January 2007 to May 2014, and the spot price, over 6,467 days from 1986-11-03. γ can be fitted on 1,941 of them, from 2004-11-22. The figures read the 1,164 days from 2008-01-02 to 2012-08-13, annualised over 252 days by compounding daily returns. The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate.

This repository transcribed the script from `ericnberwick/EpchanPreview` at commit `e4bc46f`. The rules that decide each result are in [Entry 34 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the book’s figures reproduce, and the script comment’s figures need a start one day later

The script’s comments record its figures to six decimals, and the book rounds them. Here is each figure, computed on the window the script states, beside both.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{Half-life, days} & 36.394034 & 36.394034 & 36 \\
\text{APR} & 0.082671 & 0.083406 & 8.3 \text{ percent} \\
\text{Sharpe ratio} & 1.278216 & 1.288661 & 1.3 \\
\text{Maximum drawdown} & -0.053222 & -0.053222 & \text{none} \\
\text{Longest drawdown, days} & 206 & 206 & \text{none} \\
\text{ADF statistic} & -4.727778 & \text{none} & \text{a 99 percent claim}
\end{array}
```

The deepest fall in the cumulative return is 5.3 percent, and the longest stretch below a previous high lasts 206 days.

Every figure the book prints reproduces. The APR of 8.27 percent rounds to 8.3, and the Sharpe ratio of 1.278 rounds to 1.3. The half-life and both drawdown figures land every digit the script prints.

The stationarity claim holds too. Location 2461 prints no statistic for it, so the replication needed a pass mark, and [one was written down](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading) before the replication’s code ran: the claim holds when the ADF statistic is below its 1 percent critical value, the threshold the statistic must fall below to reject a random walk at the 1 percent level. An earlier exploratory run had already measured the statistic by then, which weakens the pass mark as evidence. What saves it is that reading “99 percent” as the test’s 1 percent level leaves no threshold to choose. The statistic of −4.727778 clears the critical value of −3.4583 by 1.269478.

The test reads γ, the roll return fitted across the five nearest contracts, and not the 12-month spread the trade holds. That is what the script does, and Lesson 2 shows the two are related but not the same series.

Two figures miss. The script states its window in one line, `idx=find(tday==20080102)`, and on that window the APR and Sharpe ratio fall short of the comment’s 0.083406 and 1.288661 by 0.000735 and 0.010445. Starting one day later, on 2008-01-03, lands both to every digit, along with both drawdown figures. The trade lost 0.28 percent on 2008-01-02, the day the later start drops. Holding the day flat at 0 instead gives 0.083331 and 1.288104, which land neither, so it is the shorter window and not the missing loss that the comment’s figures need.

A scan of windows found that later start after the script’s own window missed, so this post reports it beside the replication rather than as one. For the script’s line to start on 2008-01-03, Chan’s copy of the file would have to label its rows a day earlier than the shipped one, or he ran it with another start. Nothing committed tells the two apart. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-1-three-figures-land-and-the-deviation-misses-by-209) met the same thing: two figures that land only on a window one day shorter, found by a scan.

## Lesson 2: the trade bets the spread moves further from its average

The second equation above showed that the spread’s log value is minus γ times the gap between expiries. So when γ sits above its average, the spread tends to sit below its own. A bet on the spread reverting would buy it then.

The script does the opposite. Its line 99 says it presumes “we long spread (long back contract, short front contract)”, and line 71 calls the block a “linear mean reversion strategy”. Line 107 then reverses that position wherever γ’s z-score is above 0. So it mostly sells the spread when the spread is low and buys it when the spread is high, a bet that the spread keeps moving away from its average.

Two measurements on Chan’s file show how closely γ stands in for the spread.

1. **The spread moves against γ.** On the 1,097 days of the window that hold a pair, the held pair’s log spread, far minus near, correlates with γ at −0.883910. The figure’s lower panel plots one against the other. The relationship is strong but not the one-for-one the model gives, which location 2453 anticipates when it warns that the formula “may not hold if T2 − T1 is large”.
2. **Mostly, not always.** The held pair’s own z-score, its distance from its own 36-day average in standard deviations, has the opposite sign to γ’s on 841 of those 1,097 days and the same sign on 256. So on about three days in four, γ above its average means the spread below its own.

Two more facts follow from the code. On all 554 held days with γ’s z-score above 0, the trade is short the far contract and long the near one, and on all 543 with it below 0, the other way round. Reversing every position gives an APR of −0.080125, or −8.0 percent, and a Sharpe ratio of −1.278216 on the same 1,164 days, the exact mirror of the script.

That reversal is the direction location 2471 describes for γ, which it calls “(hopefully) mean-reverting” and uses “to generate trading signals”. Location 2461 instead speaks of applying the rule “to the log calendar spread”. Trading reversion on the spread’s own z-score, short where it is above 0, loses as well, with an APR of −0.027380 and a Sharpe ratio of −0.402360. Every reading of the book’s rule tried here loses on these days. Only the size of the loss depends on which reading is chosen.

![Two charts. The top chart shows the cumulative compounded return of the trade on CL’s 12-month calendar spread from January 2008 to August 2012. A solid dark line stays near zero until late 2008, climbs through 2009, 2010 and 2011, peaks near 49 percent in February 2012 and ends near 44 percent. A dashed grey line, the same trade with every position reversed, mirrors it below zero, reaching its low near −34 percent in February 2012 and ending near −32 percent. A dashed vertical mark labels 2012-05-08 as the last day a pair is held, and a shaded band covers the last 66 days, from 2012-05-10, where both lines run flat. The bottom chart is a scatter of the held pair’s log spread, far minus near, against the roll return γ on the 1,097 days a pair is held from 2008-01-02. γ runs from about −110 percent to about 25 percent a year, and the spread from about −0.08 to 0.30. The points slope down from upper left to lower right, and the panel’s title gives the correlation as −0.883910. The title calls the result exploratory.](../docs/figures/calendar_spread_reversion.png)

*The top panel redraws the book’s Figure 5.7, “Cumulative Returns of the Linear Mean Reversion Strategy Applied on CL 12-Month Calendar Spread”, on Chan’s file, with the trade reversed beside it. The bottom panel shows the spread falling as γ rises, which decides which way the trade bets.*

What the trade earns tracks the spread rather than γ. The script’s daily return correlates at 0.999030 with yesterday’s far-leg position times today’s change in the held spread, over the 1,082 days when the same pair is held on both days. From one day to the next within a pair, the spread’s change and γ’s change correlate at only −0.510282. So the 8.3 percent is evidence that the held 12-month spread kept moving away from where γ’s 36-day z-score placed it, and not evidence that it came back.

Both can be true of one series. The ADF test says γ returns to a long-run level over the 1,941 days from 2004. The trade earns from the spread continuing past the side γ’s recent average puts it on, over the following days.

A few paragraphs later, Chan tries “this same linear mean reversion strategy” on VIX futures, futures on an index of expected stock market volatility, with the ratio of the back contract to the front one as the signal (Chan, 2013, location 2502). Run on VIX, the script pairs each contract with the one expiring a month later rather than a year later, because Chan’s VIX file prices too few contracts for a year apart. The log of a pair’s ratio of far to near is that pair’s log spread. So if the signal is the ratio of the pair the script holds, reversing the position when the signal is above its average does bet on reversion. The book’s words most plainly mean the ratio of the two nearest contracts, though, and the script usually holds a pair further out. The [post on the VIX calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-calendar-spread-lessons.md#lesson-2-the-signal-reads-one-pair-and-the-trade-holds-another) finds that the signal’s pair is the held pair on 126 of the 847 days from 2008-10-27 on which a pair is held.

## Lesson 3: the book’s 61 days and the script’s 63 give different trades

The book’s text gives the holding period as “3 months (61 trading days)” (Chan, 2013, location 2471). The script sets it to `3*21`, which is 63. The difference decides which later pairs are skipped, because a later pair is held only when at least that many days separate its first day from its last.

```math
\begin{array}{l|r|r}
 & \text{Script, 63 days} & \text{Book's text, 61 days} \\ \hline
\text{APR} & 0.082671 & 0.067315 \\
\text{Sharpe ratio} & 1.278216 & 1.044327 \\
\text{Maximum drawdown} & -0.053222 & -0.098047 \\
\text{Longest drawdown, days} & 206 & 208 \\
\text{Last day a pair is held} & 2012\text{-}05\text{-}08 & 2012\text{-}07\text{-}06
\end{array}
```

At 61 days the APR falls to 6.7 percent and the Sharpe ratio to 1.04, both well short of the book’s 8.3 percent and 1.3. So the script’s 63 is what printed the book’s figures, and the replication runs it. Two days of slack change which pairs are long enough to hold, and the last of them is held to 2012-07-06. The text is still worth testing, because a reader following the text alone gets a different trade.

## Lesson 4: the last 66 days earn nothing

The script marks a contract expired on the last day it has a price (line 75). On a file saved while contracts are still trading, that last day is the file’s last day, so every contract still trading on 2012-08-13 looks as if it expired on 2012-08-13. The trade lets go of each pair 10 days before its near contract expires, and a new pair needs at least 63 days. After 2012-05-08 no pair has that many days left before the file ends.

So the trade holds its last pair on 2012-05-08. The next day earns that position’s return, and the window’s last 66 days return exactly 0. The top panel of the figure shows the curve running flat over them. The APR is a compounded return spread over 1,164 days, and 66 of those days earn nothing, which pulls the annual rate down. Measured over the 1,098 days to 2012-05-09, the last day with a return, the APR is 8.8 percent, 0.087853, and the Sharpe ratio is 1.316295. The cumulative return is 0.443248 either way.

The book’s window ends on the file’s last day, so Chan’s figures carry the flat stretch too, as will any backtest that infers expiry from the last price on a file saved while contracts still trade.

## Lesson 5: the lookback came from the series it trades

The 36-day lookback is γ’s half-life, and the half-life is measured on every day γ can be fitted, 1,941 of them from 2004-11-22. The traded window is 1,164 of those days, 60 percent. A trader starting in January 2008 could not have known a half-life measured on days that run to August 2012, so the lookback is a look-ahead, a choice that uses days the trader had not yet seen. The [USD.CAD post’s Lesson 5](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md#lesson-5-the-trades-lookback-came-from-the-closes-it-traded) works through the same look-ahead in Chapter 2, where Chan names it.

The half-life measures how fast γ returns to its average, and by Lesson 2 it sets the lookback for a trade that profits when the spread does not return. A number chosen without optimising anything still carries a claim about the series, and here the trade bets against that claim.

So the result is exploratory. The reproduction checks the arithmetic and not whether the trade would pay. It shows that the book’s figures follow from Chan’s file and his script, that the figures in the script’s comment need one day fewer, and that the script’s profit comes from the opposite bet to the one its comments describe.

## What this replication cannot say

Five questions are beyond it.

1. **Which day the comment’s run started on.** The script states 2008-01-02, a start one day later lands the comment’s figures, and nothing committed tells the two apart.
2. **The ADF statistic Chan saw.** The script prints it and records no value in its comment, so the replication checks the book’s “99 percent” and not a number.
3. **What the lookback would be without hindsight.** The half-life is measured on all of γ, including the window it trades.
4. **Anything about costs.** None is charged, though each roll trades four contracts, closing one pair and opening the next.
5. **Whether the spread’s continuation holds outside 2008 to 2012.** Lesson 2 measures the direction on the days Chan chose. The same file holds 332 earlier days, from 2006-09-05 to 2007-12-31, and the script’s rule earns 0.050334 on them, an APR of 0.037979 with a Sharpe ratio of 0.770953. That is the same file and before costs, so it says nothing about the years after 2012. Inside the window the years differ too. 2009 alone earned 0.172419, and 2012 lost 0.003779.

## What this means for a trader

One habit for each lesson.

1. **Report the window the code states beside any window that lands.** When the code’s own window misses its own comment and a window one day shorter lands it, report both, and say which one the code states.
2. **Check the sign of the signal against the position.** A rule written as “sell when the signal is high” only bets on reversion when the position rises with the signal. Here the spread falls as the signal rises, so the same rule bets on continuation.
3. **When text and code disagree, run both.** The code printed the figures, so it is the specification, while the text describes a different trade that a reader might build.
4. **Look at the end of the backtest.** Expiry inferred from the last price makes every live contract look expired on the file’s last day, and the flat stretch it leaves dilutes an annual rate.
5. **Fit the lookback on earlier days than the trade.** A half-life measured on the traded sample is a look-ahead, and here it also measures a reversion the trade bets against.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 5.3 and 5.4, Figure 5.7, and Kindle locations 2321, 2326, 2364, 2449, 2453, 2461, 2471 and 2502.
2. `calendarSpdsMeanReversion.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Hull, J. C. (1997). *Options, Futures, and Other Derivatives* (3rd ed.). Prentice Hall. Cited at location 2364 for the model of futures prices.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion.py), [the roll return](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_reversion.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_reversion_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
