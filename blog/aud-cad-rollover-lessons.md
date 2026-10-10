# AUD.CAD overnight: what rollover interest did to a currency strategy

*Chan’s Example 5.2 adds the interest a currency position earns or pays overnight to a strategy’s return. On his own files his script’s figures land to the last digit. His “almost 5 percent” is not the rollover interest he defines, and the rollover the strategy earned was a cost of about half a point a year, because it held short more often than long.*

## Why a currency strategy’s return has to include interest

A stock bought with borrowed money costs the interest on the loan, and a backtest that ignores the loan overstates the return. A currency position carries a loan by construction. Buying the AUD.CAD cross rate, the price of one Australian dollar in Canadian dollars, means holding Australian dollars paid for with borrowed Canadian ones. Held overnight, the Australian dollars earn the Australian interest rate and the borrowed Canadian dollars cost the Canadian one.

Ernest Chan’s second book, *Algorithmic Trading*, names the difference between the two. If a trader is long a pair B.Q overnight, “the interest differential is iB − iQ”, where iB and iQ are the daily rates of the two currencies, and it is “also called a rollover interest” (Chan, 2013, location 2273). In currency markets “overnight” means held through 5 p.m. New York time. A short position reverses the sign: it pays iB − iQ rather than earning it.

Chan then says how the interest enters a backtest. The return of a cross-rate position is its percent change with the rollover interest added (Chan, 2013, location 2287, after Dueker, 2006). His Example 5.2 shows this on AUD.CAD with a mean-reverting rule, and makes three claims about it (Chan, 2013, location 2303).

1. **With rollover interest.** The strategy earns “an APR of 6.2 percent, with a Sharpe ratio of 0.54”. The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year.
2. **Without it.** The APR would rise only to 6.7 percent and the Sharpe ratio to 0.58.
3. **The interest itself.** All this holds “even though the annualized average rollover interest would amount to almost 5 percent”.

Chan published the script, `AUDCAD_daily.m`, and its last line records what it printed: an APR of 0.061564 and a Sharpe ratio of 0.541802. This repository ran a line-by-line transcription of the script on Chan’s own files.

The four figures for the strategy land to every digit the script and the book print. The rollover figure does not. The rollover interest location 2273 defines averages 3.26 percent a year on these files, below a pass mark written down before it was computed. Two other readings land inside that pass mark, and nothing in the book or the script says which one Chan computed.

**Every result here is exploratory.** Chan chose the rule and the 2007 to 2012 sample, and the reproduction tests them on the same days he did. It can say whether his numbers follow from his files and nothing about whether the cross rate reverts today.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

The rule takes four steps.

1. **The signal.** Each day’s close gets a z-score, the number of 20-day standard deviations it sits from its 20-day average. [The post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds the z-score up and trades a rule that holds minus it.
2. **The position.** This rule holds minus the z-score’s sign instead. A close above its average means short one unit and a close below it means long one unit, held from the next day. Once the first 20 days have filled the window, the rule is never flat. Location 2303 still calls it the linear mean-reverting strategy, though the size of a position no longer depends on how far the close has strayed.
3. **The return.** Each day’s return is yesterday’s position times today’s log move in the close, plus yesterday’s rollover interest on that position. The script compounds those log returns as if they were simple returns to reach its APR, and the run does the same.
4. **The costs.** None. The script charges nothing to trade.

The rollover interest needs three ideas, each in one sentence.

1. **The daily rate.** The rate files give each currency’s rate in percent a year, so a day’s rate is that number divided by 365 and by 100, and 3.65 percent a year becomes 0.0001 a day.
2. **The tripled day.** Interest accrues every calendar day, including the weekend when nothing trades, so one weekday each week pays three days’ interest at once.
3. **T + 2 settlement.** A currency trade made on day T changes hands two business days later, so a position held past 5 p.m. on Wednesday rolls its settlement from Friday to the following Monday, across a weekend, and Wednesday is the day that pays three times.

The script triples AUD’s daily rate on Wednesdays and CAD’s on Thursdays. Each day takes the rate of its own calendar month.

The data is [three files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) from Chan’s 2018 Python port of the book’s code, saved here on 2018-12-13. The closes hold 1,237 days from 2007-07-23 to 2012-04-26. The two rate files hold monthly rates, and location 2303 names the Reserve Bank of Australia and the Bank of Canada as their sources. The AUD file holds 147 months and stops at March 2012, and the CAD file holds 144 months and stops at December 2011. Both stop before the trading does, which Lesson 4 takes up. The MATLAB script read a minute-by-minute file that no public copy holds and kept the bar at 16:59 each day, so this run read the port’s daily file instead. The same two currencies, quoted the other way round as CAD/AUD, appear in [the post on stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md), which tests the rate for stationarity on a separate vintage from Yahoo Finance and finds evidence over the whole test period that it reverts.

## Lesson 1: the script’s figures land every digit

Here are the four figures for the strategy, as the script prints them, as the book rounds them, and as this repository computed them.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Script} & \text{Book} & \text{Computed} \\ \hline
\text{APR with rollover interest} & 0.061564 & \text{6.2 percent} & 0.0615638271 \\
\text{Sharpe ratio with rollover interest} & 0.541802 & 0.54 & 0.5418018005 \\
\text{APR without rollover interest} & \text{none} & \text{6.7 percent} & 0.0671408367 \\
\text{Sharpe ratio without rollover interest} & \text{none} & 0.58 & 0.5845063318
\end{array}
```

Every figure lands. The script prints only the pair with rollover interest. Its line for the return without it is commented out, and running that line gives the book’s 6.7 percent and 0.58. Each gap, the difference between a published figure and the computed one at the precision both support, rounds to zero at the precision Chan printed.

A match this exact still says less about the files than it seems to. Every return is a log move times a sign, and a log move is the same whatever units the closes are quoted in. The sign of a z-score is the same too. So multiplying every close by 1.7 moves none of the four figures, which a test in the repository confirms. The match is indirect evidence that the port’s daily file holds the closes the MATLAB script kept, up to a constant scale, and it says nothing about their level. It is also four summary figures standing for 1,237 days. A file matched against a published series day by day would be stronger evidence than a few numbers that sum it up.

The figure shows what goes into those numbers.

![Three charts stacked on one shared date axis from July 2007 to April 2012. The top chart plots the monthly interest rates in percent a year, with a dot per month. AUD starts at 6.25, peaks at 7.25 in July 2008, falls to 3.00 by May 2009, and climbs back to about 4.75 through 2011 before easing to about 4.25. CAD starts near 4.5, peaks at 4.51 in October 2007, falls to 0.24 by May 2009, and sits at 1.00 from late 2010. AUD stays above CAD in every month. Dotted lines drop each currency to hollow rings at zero for the months its file lacks, January to April 2012 for CAD and April 2012 for AUD. The middle chart plots the AUD.CAD close, from a low of 0.72500 on 2008-10-08 to a high of 1.07555 on 2012-02-08, on a background shaded green on the 510 days held long, red on the 707 held short, and grey on the first 20 days, which hold nothing. Long and short spells alternate across the whole span. The bottom chart plots the cumulative return compounded as the script compounds it, a solid line with rollover interest and a dashed line without. Both climb to about 35 percent by mid-2008, fall to near zero in October 2008, recover to around 40 percent in 2009 and 2010, and end at 34.08 percent with rollover interest and 37.57 percent without, with the dashed line above the solid one on every day after January 2008. The title calls the figure exploratory, and the note names Chan’s three files and says no cost is charged.](../docs/figures/aud_cad_rollover.png)

*The two monthly rates with the months the files lack, the close with the days held each way, and the cumulative return with and without rollover interest, on Chan’s files over 1,237 days.*

The top panel is the raw material of Lesson 2. AUD’s rate runs from 7.25 percent in July 2008 down to 3.00 in May 2009, and CAD’s from 4.51 percent in October 2007 down to 0.24 in May 2009. The rings at zero on the right are the months the files lack, which Lesson 4 takes up. The middle panel shows how often the rule changes sides, which is what Lesson 3 counts. In the bottom panel the two cumulative returns end at 34.08 percent with rollover interest and 37.57 percent without. Both fall hardest from 2008-07-30 to 2008-10-08, the day of the close’s low, by 24.86 percent with rollover interest and 25.45 percent without.

## Lesson 2: the book’s rollover figure is not the rollover interest it defines

Location 2303 says the annualised average rollover interest “would amount to almost 5 percent”. Location 2273 defines rollover interest as the difference between the two rates on a long position, AUD’s rate less CAD’s. Those two sentences can be checked against each other, and they disagree.

**The pass mark was written first.** Before the row was computed, this repository wrote down that “almost 5 percent” holds for a value of at least 4.5 percent and below 5 percent a year. “Almost” says below 5, and close enough to round to it. The computation is the one location 2273 defines. Take the rollover interest a long position would earn each day, yesterday’s AUD rate less yesterday’s CAD rate, over all 1,237 days. Average it and multiply by 252, the trading days in a year.

The pass mark was not written blind, and that belongs in the open. Its author already knew the monthly rates averaged 4.908 percent for AUD and 1.592 percent for CAD from July 2007. Those two averages differ by about 3.3 points, so a miss was likely, and the same note named the AUD rate alone as the likely reason the book’s figure was higher.

**The rollover interest misses.** It comes to 3.26 percent a year, below the floor of 4.5 percent.

**Two other readings land inside the pass mark.**

```math
\begin{array}{l|r|c}
\text{Reading} & \text{Annualised} & \text{Inside 4.5 to 5 percent} \\ \hline
\text{AUD rate less CAD rate, over 252 days} & 0.0326416903 & \text{no} \\
\text{AUD rate alone, over 252 days} & 0.0466475912 & \text{yes} \\
\text{AUD rate less CAD rate, over 365 days} & 0.0472786388 & \text{yes}
\end{array}
```

1. **The AUD rate alone, 4.66 percent.** That is what the long leg of a long position earns before the short leg’s cost. It is not the difference location 2273 defines.
2. **The difference over 365 days, 4.73 percent.** The script divides each annual rate by 365 to reach a daily one, so multiplying the daily average back by 365 looks like the natural inverse. It overstates the year, because the tripled day has already paid for the weekends. The 252 trading days of a year carry interest for nearly every calendar day between them, so this reading is the first one scaled up by 365 / 252, about 1.45 times.

**The run picks neither.** Either reading could be what Chan computed, and nothing in the book or the script says which. The script computes no rollover figure at all. Choosing a reading after seeing the miss would fit the explanation to the number, so the row stays a miss and both readings stay beside it as explanations. What the evidence does support is narrower. The rollover interest as the book defines it is 3.26 percent a year on these files, not almost 5.

## Lesson 3: a strategy earns rollover only on its net position

The book’s sentence reads as a surprise. Dropping a rollover interest of almost 5 percent moves the APR by only half a point “even though” the interest is that large. The positions explain it.

**The positions and what they cost.** The rule holds a position on 1,217 days, every day after the first 20. It is short on 707 of them and long on 510. A long day earns the day’s rollover interest and a short day pays it, so most of what the long days earn, the short days pay back. The rollover the strategy earned, 252 times the average of what rollover interest added to each day’s return, comes to −0.522 percent a year. It is a cost.

**The net position explains the cost.** The rule holds short on 197 more days than it holds long. Over its 1,217 days that is a net share of −16.2 percent, and that share times the 3.26 percent a year from Lesson 2 gives −0.528 percent, close to the −0.522 percent the strategy earned. The two are close because long days and short days see nearly the same rollover interest: 3.290 percent a year averaged over the days held long, and 3.287 percent over the days held short. If the rule had happened to hold long whenever the rollover interest was high, the net share would explain much less.

**The two APRs differ by a different amount.** Without rollover interest the APR is 6.71 percent, and with it 6.16 percent. The difference between them is 0.558 points, not the −0.522 percent the strategy earned. The APR compounds the daily returns, while the rollover the strategy earned is their average scaled to a year, and the two are different summaries of the same days.

**The book’s sentence, answered.** A strategy earns the rollover interest only on its net position. On 1,020 of this rule’s days a short day cancels a long one, and only the net short share is left to pay, so a rollover interest of 3.26 percent a year reached the return as about half a point. Counted this way, the half point in location 2303 is what the positions predict.

## Lesson 4: an empty month decides the Sharpe ratio’s second decimal

The rate files stop before the trading does. The script gives each day the rate of its own month and fills a month the file lacks with zero, carrying nothing forward. So 84 days carry no CAD rate, every trading day of 2012, and 19 carry no AUD rate, every trading day of April 2012. On those days the script treats that currency’s rate as zero.

Carrying each file’s last month forward instead is the obvious alternative. It gives an APR of 6.21 percent and a Sharpe ratio of 0.5457, against the script’s 6.16 percent and 0.5418. The APR still rounds to the book’s 6.2 percent. The Sharpe ratio rounds to 0.55 rather than 0.54.

Neither version is the measured truth. Carrying a month forward is a guess about four months of rates, and the zero fill is a different guess. The book’s 0.54 is what the zero fill produces. So the book’s second decimal rests on a choice about missing data that neither the book nor the script mentions.

## Lesson 5: an exact reproduction checks the arithmetic, not the edge

That four figures land to the digit says the script, the files and the book agree. It says nothing about whether trading AUD.CAD this way paid, for two reasons.

1. **No cost is charged.** The rule can reverse its position every day, and the script charges nothing for any trade.
2. **The rule was chosen on these days.** Chan picked the rule and the 20-day window, and the 2007 to 2012 sample has been spent on them.

So the result is exploratory, like every figure above. Reproducing Chan’s figures on his window tests his arithmetic. A result that could confirm an edge would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Four questions are beyond it.

1. **Whether the script’s settlement rule is the right one.** Location 2273 triples a cross’s rollover interest when day T + 3 falls on a weekend, which makes Wednesday the tripled day for both currencies. It names T + 1 settlement, and so Thursday, as the exception for USD.CAD. The script triples CAD on Thursday, which is that exception applied to one leg of a cross. The run transcribes the script, because the script printed the figures. Running the book’s rule after seeing the figures would be a search.
2. **What holidays would add.** Seven weekdays are absent from the file: Christmas Day in 2007, 2008 and 2009, New Year’s Day in 2008, 2009 and 2010, and 2011-12-23. No day multiplies its rollover interest for a holiday, so a position held across Christmas earns nothing for the day the market was shut.
3. **What the 2012 rates were.** Lesson 4 says what carrying a month forward moves, not what the rates were. The files were not checked against the two central banks’ own tables.
4. **What costs would take.** Nothing here charges any or counts how often the rule trades.

## What this means for a trader

One habit for each lesson.

1. **Ask what a matching figure can see.** A return built from log moves and signs cannot see the scale of the prices, so a perfect match says nothing about their level.
2. **Check a quoted figure against its own definition.** The book defines rollover interest as a difference of two rates, and its “almost 5 percent” matches readings other than that difference.
3. **Count the net position before reading a rollover figure.** A strategy that is long and short in turns earns rollover interest only on its net position.
4. **Find out what fills a missing month.** A zero, a carried rate and a measured rate are three different inputs, and here the choice moves a printed decimal.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the rule pays needs costs, a rule fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.2 and Kindle locations 2273, 2287 and 2303.
2. `AUDCAD_daily.m`, git blob `823983a`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. Its line 50 records the printout `APR=0.061564 Sharpe=0.541802`.
3. Dueker (2006), which location 2287 cites for the excess return of a cross-rate position. Its full entry is in the book’s bibliography.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_rollover.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_rollover_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_rollover.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_rollover_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-30-audcad-with-rollover-interest-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
