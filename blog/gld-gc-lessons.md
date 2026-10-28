# Chan’s long GLD, short gold futures trade reproduces on his own files, and the bill rate alone takes about half its return

*Chan owns GLD and shorts gold futures to collect gold’s negative roll return, and reports 1.9 percent a year with a drawdown of 0.8 percent. He then says financing GLD costs about as much, leaving an excess return close to zero. On his own files, the five figures in his script’s closing comment and the two in the book’s text all reproduce at the decimals printed. The script’s Sharpe ratio is negative only because of a constant it subtracts. Over the backtest’s three years, the three-month Treasury bill rate alone equals about half the return. The book’s warning that the two prices are recorded hours apart does not reach this backtest, though not for the reason it gives: the gold price in his file is recorded within minutes of GLD’s close.*

## Why own the metal and short the future

A future’s total return splits into two parts. The spot return is the move of the price of the thing the contract is written on. The roll return is the drift of the contract’s price toward that spot price as it nears expiry. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#why-split-a-futures-return-in-two) builds both up, along with contango, the state in which later contracts trade above nearer ones and the roll return is negative.

Ernest Chan’s *Algorithmic Trading* turns the split into a trade. If the roll return is negative, “buy the underlying asset and short the futures” (Chan, 2013, Kindle edition, p. 208). The spot returns of the two legs cancel, and what is left is the roll return with its sign flipped, which is positive. The same passage cites gold futures’ roll return as “−4.9 percent annualized from December 1982 to May 2004”.

![An animated whiteboard sketch titled “The spot returns cancel, and the roll return is left”, drawn slowly stroke by stroke. It is schematic and carries no figures. A green arrow pointing up sits beside the green words “own the metal:” and “+ spot return”. Below it a red arrow pointing down sits beside the red words “short the future:”, “− spot return” and “− roll return”, with the two spot returns one above the other. A black slash then strikes out each spot return. A brown arrow points down from the roll return to the brown words “left: − roll return”. Last, a green check mark sits beside “in contango the roll return is below 0, so − roll return is above 0”. The finished drawing holds for twelve seconds.](../docs/figures/gld_gc_sketch_roll_left.gif)

Owning gold bars is awkward, so the long leg is GLD, an exchange-traded fund that holds gold. Chan writes that “GLD actually owns physical gold, and thus tracks the gold spot price very closely”. That is why GLD can stand in for spot gold. The short leg is GC, the gold future. GLD is also the gold leg of the pair in the [post on GLD and GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md), which pairs it with the gold miners instead.

His backtest of the trade “yields an annualized return of 1.9 percent and a maximum drawdown of 0.8 percent” from August 3, 2007, to August 2, 2010. He notes that with “a leverage of 5 or 6” that would look attractive, and then takes it back. Owning GLD costs financing, “not very different from 1.9 percent over the backtest period”, so “the excess return of this strategy is close to zero”.

### What the reproduction found

This repository transcribed his MATLAB script, `GLD_GC.m`, line by line into Python and ran it on his own files. Four results came out.

1. **Every printed figure reproduces at the decimals printed.** Five come from the script’s closing comment and two from the book’s text. The 0.8 percent drawdown is mostly one day in November 2007. The longest drawdown the script prints, 91 days, is a different and shallower one.
2. **The negative Sharpe ratio comes from a constant.** The script subtracts 2 percent a year, which is more than the trade earns. That is arithmetic and not a measurement of what financing cost.
3. **The bill rate takes about half the return.** It is the least that financing GLD can cost. In a split by calendar year, chosen after seeing the results, the return fell each year as the bill rate fell.
4. **GC’s price is recorded within minutes of GLD’s 4 p.m. close.** The book warns that the two are recorded hours apart, and dismisses the warning for a reason that does not fit the script.

**Every result here is exploratory.** Chan chose the instruments, the rule and the dates, and the reproduction runs them on his own files. It can say whether his numbers follow from those files, and nothing about whether the trade would pay after 2010. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The trade and the files

Chan’s script does five things.

1. It loads GC’s closes from one of his files and GLD’s from another.
2. It keeps the days both files hold.
3. It takes each day’s return as GLD’s percentage change less GC’s. Holding \$1 of GLD and short \$1 of GC each day earns exactly that difference.
4. It sets the first day’s return, which has no day before it, to 0.
5. It holds the pair every day with no signal and prints five figures, which the table in Lesson 1 lists.

### What the five figures measure

Three of the five figures need explaining. The **average annual return** is the mean daily return times 252, the number of trading days in a year. The **APR** is the compounded annual return, `prod(1 + r)^(252/n) − 1` over n daily returns r, which grows each day’s return on the ones before it. The **Sharpe ratio** is the average daily return divided by its standard deviation, which is the typical size of a day’s move away from that average. The ratio is then scaled to a year by multiplying by √252. The [post on the crude oil reversal joined to momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#the-rule-and-the-file) uses the APR and the Sharpe ratio too. This script’s Sharpe ratio first subtracts a risk-free rate, the return on cash that carries no risk, of 2 percent a year from every day’s return. So it measures the return above that rate, as the [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) does.

A **drawdown** is the fall from the highest point the cumulative return has reached so far, and its **duration** is the count of days spent below that high. The script reports the deepest drawdown and the longest duration, and the two need not be the same episode.

### The GC and ETF files, and the days each holds

The script reads two of Chan’s saved files.

1. **The GC file**, `inputData_GC_1600_20100802.mat`, saved 2012-05-07. It holds 761 rows from 2007-08-03 to 2010-08-02, the book’s window exactly. Its name carries 1600, and this post calls its series **the 16:00 series**. Lesson 4 measures when it is recorded.
2. **The ETF file**, `inputData_ETF.mat`, saved 2012-04-10. GLD pays no dividend, so its adjusted close is its close.

The two calendars share 752 days. GC holds 9 rows GLD lacks, and each one is a US exchange holiday. GLD holds 3 days in the window that GC lacks. Lesson 4 returns to those 9 holidays.

### The script unchanged, and the bill rate beside it

This repository wrote down two things before computing any of the five figures.

1. **S** is the script with none of its steps changed, run on the GC file and the ETF file. The tables and the chart below label its results S.
2. **The financing comparison** sets the three-month Treasury bill rate over the window against S’s return. The book does not say how close “not very different” is, so the comparison cannot confirm or refute it.

Both are in [this repository’s replication log, in its entry for this trade](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-38-long-gld-and-short-gold-futures-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: every figure reproduces, and the 0.8 percent is mostly one day

A figure **reproduces** when the computed value rounds to the printed one at the decimals printed. The script’s closing comment records the five figures it printed when Chan ran it, and the book’s text prints two more.

```math
\small\begin{array}{l|r|r}
 & \text{S} & \text{Printed} \\ \hline
\text{Script's comment} & & \\
\text{Average annual return} & 0.019014 & 0.0190 \\
\text{Sharpe ratio} & -0.066564 & -0.07 \\
\text{APR} & 0.019084 & 0.0191 \\
\text{Maximum drawdown} & -0.0082465 & -0.008247 \\
\text{Longest duration, days} & 91 & 91 \\ \hline
\text{Book's text, percent} & & \\
\text{Annualized return} & 1.901433 & 1.9 \\
 & 1.908382 & \\
\text{Maximum drawdown} & 0.824652 & 0.8
\end{array}
```

All seven reproduce. The book’s text says “annualized return” and the script prints two, the average and the APR, so this post checks the 1.9 percent against both, and both round to it. The files are Chan’s own, so no vendor’s later revision of the prices could have moved these.

The two drawdown figures describe two different stretches. The deepest runs from a high on 2007-10-12 to a trough on 2007-11-12, and the trade is back at a new high on 2007-11-14. Most of it is one day. On 2007-11-12 GLD fell 4.7213 percent and GC fell 4.0442 percent, so the trade lost 0.6771 percent. Lesson 4 shows that the two legs parted more that day than on any other.

The 91 days are the longest stretch below a high, from 2009-08-28 to 2010-01-08. At its worst that stretch stood 0.40907 percent below its high, about half the depth of the November 2007 fall.

## Lesson 2: the negative Sharpe ratio comes from a constant

The script sets its risk-free rate with one line, `riskFreeRate=0.02/252`, which is 2 percent a year. The trade’s average annual return is 1.9014 percent. The return above that rate is therefore negative, and so is the Sharpe ratio, −0.066564.

Three Sharpe ratios on the same returns show how much the constant decides.

```math
\small\begin{array}{l|r}
\text{Rate subtracted} & \text{Sharpe ratio} \\ \hline
\text{none} & 1.284060 \\
\text{the average bill rate, 1.0141 percent} & 0.599257 \\
\text{the script's 2 percent} & -0.066564
\end{array}
```

The break-even rate is the average annual return itself. Any rate above 1.9014 percent a year turns the Sharpe ratio negative, and any rate below it leaves it positive. The script’s 2 percent is 105.18 percent of the return, so it sits just past that line.

The script never reads a financing rate, so its output holds no evidence about whether financing eats the return. That depends on what financing GLD actually cost, which Lesson 3 takes up.

## Lesson 3: the bill rate takes about half, and the return fell with it

A trader who buys GLD with borrowed money pays a broker’s rate. A broker lends above what the US Treasury pays on three-month bills, so the bill rate is a floor on that cost. A trader who buys GLD with spare cash gives up at least the bill rate on it too. The series here is TB3MS, the monthly average three-month bill rate, downloaded on 2026-09-30 from FRED, the St. Louis Fed’s public data service. The [post on factor models](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#how-example-74-and-the-two-factors-work) reads it too.

Averaged over the 37 months from August 2007 to August 2010, the bill rate is 1.0141 percent. Subtracted before rounding, the bill rate leaves 0.8874 percentage points of S’s 1.9014 percent above it, so it takes 53.33 percent of the return, about half. The bill rate is the least that financing GLD could cost. So the trade’s return above its actual financing cost, which Chan calls the excess return, is at most 0.8874 percentage points a year. For his “close to zero” to hold, financing GLD must have cost close to S’s whole return, which means about that margin above bills on average over the window. This repository holds no data on what GLD’s holders paid, so it can neither confirm nor refute the claim.

### S and the bill rate in each calendar year

**The split by calendar year below was chosen after seeing the results, so it can suggest a pattern but cannot test one.** It sets S’s average annual return against the bill rate one calendar year at a time, leaving out the first row, whose return the script sets to 0.

```math
\small\begin{array}{l|r|r|r}
\text{Year} & \text{Days} & \text{S} & \text{Bill rate} \\ \hline
\text{2007, Aug to Dec} & 101 & 0.052235 & 0.036520 \\
\text{2008} & 253 & 0.027315 & 0.013650 \\
\text{2009} & 251 & 0.005822 & 0.001500 \\
\text{2010, Jan to Aug} & 146 & 0.004458 & 0.001350
\end{array}
```

The return fell as the bill rate fell. S stays above bills in every year, and its margin over them shrinks from 1.57 percentage points in 2007 to 0.31 in 2010. The bill rate sat below 0.5 percent in 22 of the 37 months, every month from November 2008 on.

The usual explanation is the **cost of carry** (Hull, 1997). Leaving storage aside, a future on an asset that pays nothing trades above spot by about the cost of financing the asset until the contract expires. The future therefore drifts down toward spot at roughly the interest rate, and shorting it earns roughly that rate back. That is also why owning the metal and shorting the future should earn close to nothing above financing, which is Chan’s claim. This repository did not test the model. It fits the table, and four calendar years cannot establish it.

![Two charts. The top chart shows three cumulative returns from August 2007 to August 2010, each starting at zero. A black line, S, climbs to about 5 percent by the end of 2008, then flattens and ends near 5.8 percent. A brass line, three-month bills, rises to about 2.9 percent by the end of 2008 and then barely moves, ending near 3.1 percent. A dashed grey line, the script’s 2 percent a year, rises steadily, crosses above S in mid 2010, and ends near 6.1 percent. A shaded band from late August 2009 to early January 2010 is labelled as 91 days below a high, at worst −0.41 percent. A red dot on S in November 2007 marks the deepest drawdown, −0.82 percent, on 2007-11-12. The bottom chart plots the daily change in the log of GC over GLD over 751 days for two series. A grey line, the OHLC series shifted at each roll, swings widely, with spikes near 0.1 and −0.075 in September 2008 and several others past dashed lines at plus and minus 0.02. A black line, the 16:00 series, stays close to zero throughout, with its largest move, 0.007082, labelled on 2007-11-12. The title calls the result exploratory.](../docs/figures/gld_gc.png)

*The top panel sets S beside two rates of financing, the three-month bill rate and the script’s 2 percent. Its curves were drawn after the run, though the comparison with the window’s average bill rate was written down before it. On 2008-12-31 S stood at 4.9260 percent and the bills at 2.8733 percent. From there S rose by less than a percentage point to its high of 5.8415 percent on 2010-07-27, and it last stood above the 2 percent line on 2010-05-21. At the end S is at 5.8033 percent, the bills at 3.1057 percent and 2 percent a year at 6.1413 percent. The bottom panel is Lesson 4’s evidence. The run itself computed each series’ standard deviation, its largest move and its count of moves past 0.02. Only the dates of the largest moves, and each series’ most negative move, were measured after the run.*

## Lesson 4: the closes line up, though not for the book’s reason

The book raises a caveat itself. GC’s prices “are recorded at 1:30 p.m. ET, while those of GLD are recorded at 4:00 p.m. ET” (p. 209). A futures price from a data vendor is usually “the settlement price, not the last traded price” (p. 39). The settlement price is the official price the exchange fixes once a day. COMEX, the exchange GC trades on, fixes it at its own hour, which the book gives as 1:30 p.m. ET. Chapter 1 warns that a spread between two instruments closing at different times is wrong, and adds, “This is true also if we try to form a spread between a future and an ETF” (p. 41).

Chan then dismisses the caveat because “the trading signals are generated based on GC closing prices alone” (p. 209). That reason does not fit `GLD_GC.m`, which has no signal. It holds the pair every day, and each day’s return is GLD’s return less GC’s. If GC were recorded two and a half hours before GLD, every day’s return would carry gold’s move between 1:30 and 4 p.m. The book’s reason cannot keep that difference in timing out of this backtest. The file Chan saved keeps it out, as two measurements show.

### GC’s calendar rules out the 1:30 p.m. settlement

The first measurement is the calendar. A settlement series has no row on a day the exchange is shut, and the GC file holds 9 such rows, each a US exchange holiday. That rules out the settlement series the caveat describes.

### A bound of about 2.6 minutes, against the caveat’s 150

The second measurement is the ratio GC / GLD. Both legs follow gold, so if both are recorded at the same moment, the ratio barely moves from one day to the next. The measurement uses the logarithm of the ratio, whose daily change is close to the ratio’s percentage change.

Suppose instead GC were recorded some time before GLD. Each day’s log ratio would then carry gold’s move during that offset. Each day’s change in it would carry two such moves, today’s and yesterday’s with its sign flipped.

**Variance**, the square of the standard deviation, adds up over time. Gold trades nearly around the clock, so a move over an offset carries roughly the offset’s share of a whole day’s variance, and two such moves carry twice that share. GLD’s own daily log return stands in for a day of gold, and its standard deviation is 0.015660. The daily change in log(GC / GLD) has a standard deviation of 0.000933. Other things move the ratio too. As long as they do not cancel the offset’s moves, the offset’s two moves can carry no more than the whole variance of that daily change. So twice the offset’s share of GLD’s variance is at most 0.000933 squared, and the share is at most half the squared ratio of the two standard deviations.

```math
\frac{1}{2} \left( \frac{0.000933}{0.015660} \right)^{2} = 0.001775
```

Of a 24-hour day, a share of 0.001775 is about 2.6 minutes, against the 150 minutes from 1:30 to 4:00 p.m. that the caveat describes. The bound assumes that the ratio’s other moves do not cancel the offset’s, and nothing here tests that.

![An animated whiteboard sketch titled “An offset puts two moves in each day’s change”, drawn slowly stroke by stroke. It is schematic apart from its last line, which reads the run’s bound. A wiggly brown line, gold’s price, runs across two days. On each day a dashed grey tick stands where GC would be recorded, and a solid black tick a little later stands where GLD is recorded, the gap between them drawn about twice as wide as two and a half hours of a day would be. Above the first day’s ticks, grey words read “if GC were recorded at 1:30 p.m.” and black words read “GLD recorded at 4 p.m.”. Grey labels name the first day “yesterday” and the second “today”. A brown brace under each day spans the gap between its two ticks, where the price rises. Three lines of black words follow: “each day’s log(GC / GLD) carries that day’s move over the gap”, “each change carries two: today’s, and yesterday’s with its sign flipped” and “each move carries the gap’s share of a day’s variance, so the change carries twice that”. Last, a green check mark sits beside “at most 0.001775 of a day, about 2.6 minutes, against 150”. The finished drawing holds for twelve seconds.](../docs/figures/gld_gc_sketch_two_moves.gif)

### Chan’s other GC series, for contrast

For contrast, Chan saved a second GC series. His file `inputDataOHLCDaily_20120507.mat`, saved 2012-05-09, holds each day’s open, high, low and close for several futures. Its GC close, which this post calls **the OHLC series**, is a continuous future: one long series spliced from successive contracts, with its prices shifted at each roll, the day it switches from an expiring contract to the next. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains both at more length. Against GLD, the OHLC series’ daily change in log(GC / GLD) has a standard deviation of 0.009243, about ten times the 16:00 series’ 0.000933. It has 20 moves past 0.02, 8 up and 12 down. Its largest is 0.097332, on 2008-09-18, and the next day it moves −0.075146, most of the way back. The 16:00 series has none past 0.02, and its largest move is 0.007082, on 2007-11-12, the day of the deepest drawdown.

A daily change **reverses** when a move one day tends to come back the next. That shows as a negative correlation between each day’s change and the next one’s, called the lag-1 autocorrelation. The gap between the two GC prices, the 16:00 close less the OHLC close, reverses: its daily change has a lag-1 autocorrelation of −0.559953. A difference in timing predicts that, because a move between the two series’ recording times on one day comes back the day after. A shift at a roll is a step that stays, so it predicts no reversal.

The 16:00 series’ own daily change against GLD reverses too, at −0.437059. Any small error in either recorded price on a day produces that, as does an offset of a few minutes. The data places the 16:00 series within minutes of GLD’s close, and cannot say the exact minute.

## What this replication cannot say

Four questions are beyond it.

1. **What financing GLD cost a trader.** The bill rate is a floor, and a broker’s rate sits above it by a spread this repository has no data for. The excess return is known only to be at most 0.8874 percentage points a year, and is not measured.
2. **How the trade does on the 1:30 p.m. settlement.** That needs the OHLC series, whose returns are shifted at each roll and would need their own reading.
3. **Whether the trade works after 2010.** The window is the book’s, and nothing here reads later data.
4. **Gold’s roll return of −4.9 percent from 1982 to 2004.** The book cites it as the reason to try the trade. No gold futures series here starts before 2004-05-24, the OHLC series’ first day, which falls in May 2004, the month the book’s span ends.

## What this means for a trader

One habit for each lesson.

1. **Ask which drawdown a figure names.** A deepest drawdown and a longest one can be different episodes, and a deep one can be mostly a single day.
2. **Check what a Sharpe ratio subtracts before reading its sign.** A constant risk-free rate above a series’ mean return makes its Sharpe ratio negative, whatever financing actually cost.
3. **Set a trade that collects a future’s roll return against the rate that finances it, period by period.** The margin above the rate is what the trade earns. A return that falls with the rate need not be mostly the rate: in 2009 and 2010 the bill rate took under a third of S’s return.
4. **Measure when each price is recorded, rather than trusting the file’s label or the book’s reason.** The ratio of two prices on the same asset bounds any difference in timing between them, as long as the ratio’s other moves do not cancel the moves that timing adds.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Pages 39, 41 and 208 to 209 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. `GLD_GC.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Hull, J. C. (1997). *Options, Futures, and Other Derivatives*. Prentice Hall. The cost-of-carry model of a futures price.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gld_gc.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gld_gc_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gld_gc.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gld_gc_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-38-long-gld-and-short-gold-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
