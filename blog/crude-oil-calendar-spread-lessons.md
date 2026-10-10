# Chan’s crude oil calendar spread reproduces on his own file, and its trade bets the other way from its comment

*Example 5.4 of Algorithmic Trading trades the spread between crude oil contracts a year apart. On Chan’s own file the book’s figures reproduce, the script’s own figures need a start one day later, and the trade that earns them bets on the spread moving away from its average rather than back.*

## Why trade the roll return

Two futures contracts on the same commodity, one expiring a year after the other, both track the same barrel of oil. So the gap between their prices looks like a natural candidate for a trade that bets on a gap returning to its average. Ernest Chan’s *Algorithmic Trading* says the intuition usually fails: calendar spreads “do not generally mean-revert” (Chan, 2013, location 2321).

His reason is the roll return, the part of a futures contract’s return that comes from its price converging on the spot price as it nears expiry. Under the book’s model of futures prices, the gap between two contracts’ log prices depends only on that roll return. The calendar spread’s signal “does not depend at all on the spot price, only on the roll return!” (Chan, 2013, location 2453). A spread built on oil therefore trades oil’s roll return and none of oil’s price.

Chan then finds a spread that does revert. For crude oil’s 12-month calendar spread, the ADF test finds it “stationary with 99 percent probability, and a half-life of 36 days”, and his usual mean-reverting rule earns “an APR of 8.3 percent and a Sharpe ratio of 1.3 from January 2, 2008, to August 13, 2012” (Chan, 2013, location 2461). Example 5.4 describes the backtest, and Chan published its script, `calendarSpdsMeanReversion.m`. This repository transcribed it line by line and ran it on the file it loads.

The results fall into four groups.

1. **The book’s figures reproduce.** The half-life, the APR, the Sharpe ratio and both drawdown figures match the book or the script’s comment, and the stationarity claim holds.
2. **The script’s comment needs a start one day later.** Its APR and Sharpe ratio land to every digit only when the window starts on 2008-01-03 rather than the 2008-01-02 the script states.
3. **The trade bets the other way from its comment.** The spread moves opposite to the roll return, and the script reverses its position on the roll return’s sign. So it sells the spread when the spread is low. Reversing the sign, which is the bet the book describes, loses 8.0 percent a year.
4. **The last three months hold nothing.** Contracts still trading when the file was saved look expired on its last day, so the trade lets go of its last pair in May 2012.

**Every result here is exploratory.** Chan chose the commodity, the spread, the rule and the dates, and the reproduction runs them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the trade would pay after 2012.

An [earlier post on Chan’s calendar spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) tested his first book’s claim that calendar spreads cointegrate, on one-month spreads of natural gas and gasoline. It borrowed this example’s 36-day half-life as a speed of reversion to simulate, and ran no trade. This post reproduces that half-life and runs the trade. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The spread, the signal and the file

Six ideas set up everything that follows.

1. **A futures contract and its expiry.** A futures contract is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, and each stops trading at its expiry. A position held for longer than one contract’s life has to move to the next one, which is called a roll. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) shows what a roll does to a price history stitched from one contract after another. This trade stitches nothing. It holds named contracts and moves to the next pair on a schedule.
2. **The roll return.** Contracts with different expiries trade at different prices, and each has to converge on the spot price by its expiry. So a futures position earns a return “even if the underlying spot price remains unchanged”, and that return is the roll return (Chan, 2013, location 2326). When near contracts trade above far ones, called backwardation, the roll return is positive. When they trade below, called contango, it is negative.
3. **The model.** Location 2364 writes a simple model of futures prices, crediting Hull (1997), in which the roll return is a constant γ. A contract expiring at T is worth the spot price S(t) times a factor that shrinks to 1 as t reaches T:

   ```math
   F(t, T) = S(t)\, e^{\gamma (t - T)}
   ```

   Chan’s Example 5.3 estimates γ on each day by regressing the log prices of the five nearest contracts on their time to maturity. γ is −12 times the slope, so it is an annual rate, positive in backwardation, where the far contracts are cheaper. On crude oil, WTI futures that trade as CL, γ moves slowly from day to day.
4. **The calendar spread.** A calendar spread is long one contract and short another on the same underlying with a different expiry (Chan, 2013, location 2449). Under the model, the log value of a spread long the far contract, expiring at T₂, and short the near one, expiring at T₁, is

   ```math
   \log F(t, T_2) - \log F(t, T_1) = \gamma\,(T_1 - T_2)
   ```

   The spot price cancels, which is location 2453’s point. T₂ is later, so T₁ − T₂ is negative, and the spread’s log value is minus γ times the gap between the expiries. When γ rises, the spread falls.
5. **The signal and the rule.** The script measures γ’s half-life, the time a gap from its average takes to close halfway, and rounds it to a lookback of 36 days. Each day it computes γ’s z-score, the number of 36-day moving standard deviations γ sits from its 36-day moving average. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds the z-score up, and the [post on the stationarity tests on USD.CAD](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md) explains the ADF test and the half-life. The script starts every day long the far contract and short the near one, and reverses both legs wherever the z-score is above 0. Chan calls this his linear mean-reverting strategy, but the position here is always one unit of the spread. Only the z-score’s sign matters, not its size.
6. **The schedule.** Contract c is held short against contract c + 12 long, so the two expire a year apart. Each pair is held to 10 trading days before its near contract’s last priced day. The first pair starts 73 days before that day, and each later pair starts the day after the last one ended. A pair is skipped when that leaves fewer than 63 days to hold it. Each day’s return is yesterday’s position times each leg’s percent change, summed and halved because there are two contracts. No cost is charged.

The data is the file the script loads, `inputDataDaily_CL_20120813.mat`, saved 2012-08-14 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). It holds 89 CL contracts, one for each month from January 2007 to May 2014, and the spot price, over 6,467 days from 1986-11-03. γ can be fitted on 1,941 of them, from 2004-11-22. The figures read the 1,164 days from 2008-01-02 to 2012-08-13, annualised over 252 days by compounding daily returns. The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate.

This repository transcribed the script from `ericnberwick/EpchanPreview` at commit `e4bc46f`. The rules that decide each result are in [Entry 34 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the book’s figures reproduce, and the comment’s need a start one day later

The script prints its figures to six decimals in its comments, and the book rounds them. Here is each figure, computed on the window the script states, beside both.

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

A drawdown is a fall from the highest value reached so far. The deepest fall in the cumulative return is 5.3 percent, and the longest stretch below a previous high lasts 206 days.

Every figure the book prints reproduces. The APR of 8.27 percent rounds to 8.3, and the Sharpe ratio of 1.278 rounds to 1.3. The half-life and both drawdown figures land every digit the script prints.

The stationarity claim holds too. Location 2461 prints no statistic for it, so the replication needed a pass mark, and the plan wrote one down: the claim holds when the ADF statistic is below its 1 percent critical value. A scratch run had already measured the statistic when the plan was written, which weakens the pass mark as evidence. What saves it is that reading “99 percent” as the test’s 1 percent level leaves no threshold to choose. The statistic of −4.727778 clears the critical value of −3.4583 by 1.269478.

The test reads γ, the slope across the five nearest contracts, and not the 12-month spread the trade holds. That is what the script does, and Lesson 2 shows the two are close relatives rather than the same series.

Two figures miss. The script states its window in one line, `idx=find(tday==20080102)`, and on that window the APR and Sharpe ratio fall short of the comment’s 0.083406 and 1.288661 by 0.000735 and 0.010445. Starting one day later, on 2008-01-03, lands both to every digit, along with both drawdown figures. The difference is a single day. The trade lost 0.28 percent on 2008-01-02, and dropping that day lands the comment’s figures. Holding the day flat at 0 instead gives 0.083331 and 1.288104, which land neither, so it is the shorter window and not the missing loss that the comment’s figures need.

That later start was found by a scan of windows after the script’s own window missed, so it is a row beside the replication and not a replication. For the script’s line to start on 2008-01-03, Chan’s copy of the file would have to label its rows a day earlier than the shipped one, or he ran it with another start. Nothing committed tells the two apart. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run) met the same thing: a figure that lands only on a window one day shorter, found by a sweep.

## Lesson 2: the trade bets the spread moves further from its average

The fourth idea above showed that the spread’s log value is minus γ times the gap between expiries. So when γ sits above its average, the spread sits below its own. A bet on the spread reverting would buy it then.

The script does the opposite. Its line 99 says it presumes “we long spread (long back contract, short front contract)”, and line 71 calls the block a “linear mean reversion strategy”. Line 107 then reverses that position wherever γ’s z-score is above 0, when the spread is low. It sells the spread when the spread is low and buys it when the spread is high. That is a bet that the spread keeps moving away from its average.

Three measurements on Chan’s file confirm it.

1. **The spread moves against γ.** On the 1,097 days of the window that hold a pair, the held pair’s log spread, far minus near, correlates with γ at −0.883910. The figure’s lower panel plots one against the other. The relationship is strong but not the one-for-one the model gives, which location 2453 anticipates when it warns that the formula “may not hold if T2 − T1 is large”.
2. **The far leg is short wherever the z-score is above 0.** On all 554 held days in the window with a z-score above 0, the trade is short the far contract and long the near one. On all 543 with a z-score below 0, it is the other way round.
3. **The bet the book describes loses what the script earns.** Reversing every position gives an APR of −8.0 percent, −0.080125, and a Sharpe ratio of −1.278216 on the same 1,164 days.

![Two charts. The top chart shows the cumulative compounded return of the trade on CL’s 12-month calendar spread from January 2008 to August 2012. A solid dark line stays near zero until late 2008, climbs in steps through 2009 and 2010, and reaches about 44 percent by the spring of 2012. A dashed grey line, the same trade with every position reversed, mirrors it below zero and ends near −32 percent. A dashed vertical mark labels 2012-05-08 as the last day a pair is held, and a shaded band covers the 66 days after it, where both lines run flat. The bottom chart is a scatter of the held pair’s log spread, far minus near, against the roll return γ on the 1,097 held days from 2008-01-02. γ runs from about −110 percent to about 25 percent a year, and the spread from about −0.08 to 0.30. The points slope down from upper left to lower right, and the panel’s title gives the correlation as −0.883910. The title calls the result exploratory.](../docs/figures/calendar_spread_reversion.png)

*The top panel redraws the book’s Figure 5.7, “Cumulative Returns of the Linear Mean Reversion Strategy Applied on CL 12-Month Calendar Spread”, on Chan’s file, with the trade reversed beside it. The bottom panel is the sign the trade’s direction rests on.*

So the 8.3 percent is evidence that γ kept moving in the direction it was already going, measured against a 36-day average, and not evidence that it came back. Both can be true of one series. The ADF test says γ returns to a long-run level, over the 1,941 days from 2004. The trade earns from γ continuing past its recent average, over days. The script’s comments name the first and its arithmetic collects the second.

Chan’s next paragraph runs the same script on VIX futures, with the ratio of the back contract to the front one as the signal (Chan, 2013, location 2502). That ratio rises when the spread rises, so on VIX the same line 107 does bet on reversion. The sign of the signal against the spread decides which bet one line of code places.

## Lesson 3: the book’s 61 days and the script’s 63 give different trades

The book’s text gives the holding period as “3 months (61 trading days)” (Chan, 2013, location 2471). The script sets it to `3*21`, which is 63. The difference decides which later pairs are skipped, because a pair is held only when at least that many days remain.

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

At 61 days the APR falls to 6.7 percent and the Sharpe ratio to 1.04, both well short of the book’s 8.3 percent and 1.3. So the script’s 63 is what printed the book’s figures, and the replication runs it. Two days of slack change which pairs pass the test, and the last of them is held to 2012-07-06.

When a book’s text and its code disagree, the code is the specification, because the code is what printed the figures. The text is still worth testing, because a reader following the text alone gets a different trade.

## Lesson 4: the last 66 days hold nothing

The script marks a contract expired on the last day it has a price (line 75). On a file saved while contracts are still trading, that last day is the file’s last day, so every contract still trading on 2012-08-13 looks as if it expired on 2012-08-13. Each pair is let go 10 days before its near contract expires, and a new pair needs at least 63 days to hold. Neither fits before the file ends.

So the trade lets go of its last pair on 2012-05-08, and the window’s last 66 days return exactly 0. The top panel of the figure shows the curve running flat over them. The APR is a compounded return spread over 1,164 days, and 66 of those days earn nothing, which pulls the annual rate down. Measured over the 1,098 days to 2012-05-09, the last day with a return, the APR is 8.8 percent, 0.087853, and the Sharpe ratio is 1.316295. The cumulative return is 0.443248 either way.

The book’s window ends on the file’s last day, so Chan’s figures carry the flat stretch too. It is not an error in the replication. It is what any backtest that infers expiry from the last price will do at the end of its data.

## Lesson 5: the lookback came from the series it trades

The 36-day lookback is γ’s half-life, and the half-life is measured on every day γ can be fitted, 1,941 of them from 2004-11-22. The traded window is 1,164 of those days, 60 percent. A trader starting in January 2008 could not have known a half-life measured on days that run to August 2012. The [USD.CAD post’s Lesson 5](https://github.com/l3a0/quantitative-trading/blob/main/blog/usdcad-stationarity-lessons.md#lesson-5-the-trades-lookback-came-from-the-closes-it-traded) works through the same look-ahead in Chapter 2, where Chan names it.

Lesson 2 adds a twist. The half-life measures how fast γ returns to its average, and it sets the lookback for a trade that bets γ moves away from its average. A number chosen without optimising anything still carries a claim about the series, and here the trade does not use that claim.

So the result is exploratory. The reproduction checks the arithmetic and not whether the trade would pay. It shows that the book’s figures follow from Chan’s file and his script, that the comment’s figures need one day fewer, and that the script’s profit comes from the opposite bet to the one its comments describe.

## What this replication cannot say

Five questions are beyond it.

1. **Which day the comment’s run started on.** The script states 2008-01-02, a start one day later lands the comment, and nothing committed tells the two apart.
2. **The ADF statistic Chan saw.** The script prints it and records no value in its comment, so the replication checks the book’s “99 percent” and not a number.
3. **What the lookback would be without hindsight.** The half-life is measured on all of γ, including the window it trades.
4. **Anything about costs.** None is charged, though each roll trades four contracts, closing one pair and opening the next.
5. **Whether γ’s continuation holds outside 2008 to 2012.** Lesson 2 measures the direction on the days Chan chose. Whether the reversed sign would lose on other days, or the script’s sign would keep earning, is untested.

## What this means for a trader

One habit for each lesson.

1. **Report the window the code states beside any window that lands.** When the code’s own window misses its own comment and a window one day shorter lands it, report both, and say which one the code states.
2. **Check the sign of the signal against the position.** A rule written as “sell when the signal is high” only bets on reversion when the position rises with the signal. Here it falls, so the same rule bets on continuation.
3. **When text and code disagree, run both.** The code printed the figures, so it is the specification, and the text describes a different trade that a reader might build.
4. **Look at the end of the backtest.** Expiry inferred from the last price makes every live contract look expired on the file’s last day, and the flat stretch it leaves dilutes an annual rate.
5. **Fit the lookback on earlier days than the trade.** A half-life measured on the traded sample is a look-ahead, and here it also measures a property the trade does not bet on.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 5.3 and 5.4, Figure 5.7, and Kindle locations 2321, 2326, 2364, 2449, 2453, 2461, 2471 and 2502.
2. `calendarSpdsMeanReversion.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Hull, J. C. (1997). *Options, Futures, and Other Derivatives* (3rd ed.). Prentice Hall. Cited at location 2364 for the model of futures prices.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion.py), [the roll return](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_reversion_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_reversion.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_reversion_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
