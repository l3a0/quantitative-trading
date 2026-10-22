# AUD.CAD overnight: what rollover interest did to a currency strategy

*Chan’s Example 5.2 adds the interest a currency position earns or pays overnight, called rollover interest, to a strategy’s return. On his own files, a Python copy of his MATLAB script matches his four figures for the strategy to every digit he printed. His “almost 5 percent” a year does not match the rollover interest he defines. Rollover interest cost the strategy about half a point a year, because it held short more often than long.*

## Why a currency strategy’s return has to include interest

A stock bought with borrowed money costs the interest on the loan, and a backtest that ignores the loan overstates the return. A currency position includes a loan by construction. AUD.CAD is a cross rate, an exchange rate between two currencies neither of which is the US dollar. It is the price of one Australian dollar in Canadian dollars, and buying it means holding Australian dollars paid for with borrowed Canadian ones. Held overnight, the Australian dollars earn the Australian interest rate and the borrowed Canadian dollars cost the Canadian one.

Ernest Chan’s second book, *Algorithmic Trading*, names the difference between the two. If a trader is long a pair B.Q overnight, “the interest differential is iB − iQ”, where iB and iQ are the daily rates of currency B and currency Q, and it is “also called a rollover interest” (Chan, 2013, Kindle location 2273, the e-book’s marker in place of a page number). In currency markets “overnight” means held through 5 p.m. New York time. A short position reverses the sign: it pays iB − iQ rather than earning it.

Chan then says how the interest enters a backtest. The return of a cross-rate position is its percent change with the rollover interest added (Chan, 2013, location 2287, after Dueker and Neely, 2006). His Example 5.2 shows this on AUD.CAD with a mean-reverting rule, one that bets a price will return toward its recent average, and makes three claims about it (Chan, 2013, location 2303).

1. **With rollover interest.** The strategy earns “an APR of 6.2 percent, with a Sharpe ratio of 0.54”. The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year.
2. **Without it.** The APR would rise only to 6.7 percent and the Sharpe ratio to 0.58.
3. **The interest itself.** Dropping the interest moves the APR by only half a point, “even though the annualized average rollover interest would amount to almost 5 percent”.

### What the reproduction found

Chan published the MATLAB script behind the example, `AUDCAD_daily.m`, and its line 50 records what it printed: an APR of 0.061564 and a Sharpe ratio of 0.541802. This repository copied the script line by line into Python and ran it on Chan’s own data files, which the next section describes.

The four figures for the strategy, its APR and Sharpe ratio with and without rollover interest, match every digit the script and the book print. The book’s rollover figure does not. Before computing it, this repository wrote down a pass mark, the range the computed figure would have to fall in for “almost 5 percent” to count as a match: at least 4.5 percent a year and below 5. The rollover interest as the book defines it, averaged and scaled to a year by 252 trading days, comes to 3.26 percent a year on these files, below that range. Two other readings of “almost 5 percent” fall inside it: the AUD rate alone, and the rate difference scaled to a year by 365 days rather than 252 trading days. Nothing in the book or the script says which, if either, Chan computed.

**Every result here is exploratory**, meaning it rechecks published claims on the data they came from. Chan chose the rule and the 2007 to 2012 sample, and the reproduction tests them on the same days he did. So it can say whether his numbers follow from his files, and nothing about whether the cross rate still returns to its average today.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

The rule takes four steps.

1. **The signal.** Each day’s close gets a z-score, the number of 20-day standard deviations it sits from its 20-day average. [The post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds the z-score up and trades a rule whose position is minus the z-score, so the further the close strays, the bigger the bet against it.
2. **The position.** This rule uses only the z-score’s sign, and bets against it. A close above its average means short one unit and a close below it means long one unit, held from the next day. Once the first 20 days have filled the 20-day window, the rule always holds a position. The book still calls this the linear mean-reverting strategy (location 2303). That name fits a position that grows in step with the z-score, and here the position is one unit however far the close has strayed.
3. **The return.** A log move is the logarithm of the ratio of today’s close to yesterday’s, and a simple return is the percent change. Each day’s return is yesterday’s position times today’s log move in the close, plus yesterday’s rollover interest on that position. To reach its APR, the script compounds each day’s return as if it were a simple return, though it is built from a log move. That slightly understates the total, and this reproduction does the same.
4. **The costs.** None. The script charges nothing to trade.

### A day’s rollover interest

The rollover interest needs three ideas.

1. **The daily rate.** The rate files give each currency’s rate in percent a year for each calendar month, and each day takes its own month’s rate. A day’s rate is that number divided by 365 and by 100, and 3.65 percent a year becomes 0.0001 a day.
2. **The tripled day.** Interest accrues every calendar day, including the weekend when nothing trades, so one weekday each week pays three days’ interest at once.
3. **T + 2 settlement.** A currency trade made on day T settles two business days later, on T + 2. Settling means the two currencies change hands. Holding a position past 5 p.m. on day T moves its settlement one business day later. When T is a Wednesday, the settlement moves from Friday to Monday across the weekend, so Wednesday pays three days’ interest. The book’s settlement rule counts in calendar days instead. It multiplies a day’s rollover interest when day T + 3 falls on a weekend or holiday, and its example is a Wednesday, whose T + 3 is a Saturday. Read word for word, the rule would also multiply a Thursday, whose T + 3 is a Sunday. For a cross rate, the book names only Wednesday.

The script triples AUD’s daily rate on Wednesdays, as the book’s settlement rule says, but CAD’s on Thursdays. That departs from the book, and the section on what this replication cannot say takes it up.

### The data

The data is [three files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) from Chan’s 2018 Python version of the book’s code, each dated 2018-12-13 in the zip archive he distributed. The closing prices cover 1,237 days from 2007-07-23 to 2012-04-26. The two rate files hold monthly rates, and the example names the Reserve Bank of Australia and the Bank of Canada as their sources. The AUD file holds 147 months and stops at March 2012, and the CAD file holds 144 months and stops at December 2011. Both stop before the trading does, which Lesson 4 takes up.

The MATLAB script read a file of one-minute prices and kept the price at 16:59 each day. Neither of two public copies of Chan’s code holds that file, so this reproduction read the Python version’s daily file instead.

The same two currencies, quoted the other way round as CAD/AUD, appear in [the post on stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md). That post tests whether the CAD/AUD exchange rate keeps returning to a stable average, on separate prices downloaded from Yahoo Finance, and finds evidence over the whole test period that it does.

## Lesson 1: the four figures match to the digit but cannot see the price level

Here are the four figures for the strategy, as the script prints them, as the book rounds them, and as this repository computed them.

```math
\small
\begin{array}{l|r|r|r}
 & \text{Script} & \text{Book} & \text{Computed} \\ \hline
\text{With rollover} & & & \\
\quad\text{APR} & 0.061564 & 6.2\% & 0.0615638271 \\
\quad\text{Sharpe} & 0.541802 & 0.54 & 0.5418018005 \\ \hline
\text{Without} & & & \\
\quad\text{APR} & \text{none} & 6.7\% & 0.0671408367 \\
\quad\text{Sharpe} & \text{none} & 0.58 & 0.5845063318
\end{array}
```

The script prints only the pair with rollover interest. Its line for the return without rollover interest is switched off, kept in the file as a comment, and running that line gives the book’s 6.7 percent and 0.58. Rounded to the digits Chan printed, each computed figure equals his.

A match this exact still says less about the files than it seems to. Every return is a log move times a sign, plus a rollover term that reads only the rates, and a log move is the same whatever units the closes are quoted in. The sign of a z-score is the same too. So multiplying every close by 1.7 moves none of the four figures, which a test in the repository confirms. The match is indirect evidence that the Python version’s daily file holds the closes the MATLAB script kept, up to a constant scale, and it says nothing about their level. It is also four summary figures standing for 1,237 days. A file matched against a published series day by day would be stronger evidence than a few numbers that sum it up.

### The rates, the positions and the returns

The chart shows what goes into the four figures.

![Three charts stacked on one shared date axis from July 2007 to April 2012. The top chart plots the monthly interest rates in percent a year, with a dot per month. AUD starts at 6.25, reaches 7.25 in April 2008 and holds it to August, falls to 3.00 by May 2009, and climbs back to about 4.75 through 2011 before easing to about 4.25. CAD starts near 4.5, peaks at 4.51 in October 2007, falls to 0.24 by May 2009, and sits near 1.00 from September 2010. AUD stays above CAD in every month both files hold. Dotted lines drop each currency to hollow rings at zero for the months its file lacks, January to April 2012 for CAD and April 2012 for AUD. The middle chart plots the AUD.CAD close, from a low of 0.72500 on 2008-10-08 to a high of 1.07555 on 2012-02-08, on a background shaded green on the 510 days held long, red on the 707 held short, and grey on the first 20 days, which hold nothing. Long and short spells alternate across the whole span. The bottom chart plots the cumulative return compounded as the script compounds it, a solid line with rollover interest and a dashed line without. Both climb by mid-2008, to about 37 percent with rollover interest and 39 percent without, fall to near zero in October 2008, move between about 23 and 46 percent through 2009 and 2010, and end at 34.08 percent with rollover interest and 37.57 percent without, with the dashed line above the solid one on every day after January 2008. The title calls the figure exploratory, and the note names Chan’s three files and says no cost is charged.](../docs/figures/aud_cad_rollover.png)

*The two monthly rates with the months the files lack, the close with the days held each way, and the cumulative return with and without rollover interest, on Chan’s files over 1,237 days.*

The top panel is the raw material of Lesson 2. AUD’s rate held 7.25 percent from April to August 2008 and fell to 3.00 in May 2009. CAD’s ran from 4.51 percent in October 2007 down to 0.24 in May 2009. The rings at zero on the right are the months the files lack, which Lesson 4 takes up. The middle panel shows which days the rule holds long and which short, and Lesson 3 counts them. In the bottom panel the two cumulative returns end at 34.08 percent with rollover interest and 37.57 percent without. Both fall hardest from 2008-07-30 to 2008-10-08, the day of the close’s low. Over that stretch the strategy loses 24.86 percent of its value with rollover interest and 25.45 percent without, which brings both lines down to near zero.

## Lesson 2: the book’s rollover figure is not the rollover interest it defines

Example 5.2 says the annualised average rollover interest “would amount to almost 5 percent”. The book’s definition, quoted above, takes the difference between the two rates on a long position, AUD’s rate less CAD’s. On these files, the two sentences disagree.

**The pass mark came first.** Before computing the figure, this repository wrote down [a pass mark](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-30-audcad-with-rollover-interest-chans-algorithmic-trading): “almost 5 percent” holds for a value of at least 4.5 percent and below 5 percent a year. “Almost” says below 5, and close enough to round to it. The computation follows the book’s definition. Take the rollover interest a long position would earn each day, yesterday’s AUD rate less yesterday’s CAD rate, over all 1,237 days. Average it and multiply by 252, the trading days a year the script uses to annualise its returns.

The pass mark was not written blind. Its author already knew the monthly rates averaged 4.908 percent for AUD and 1.592 percent for CAD from July 2007. Those two averages differ by about 3.3 points, so a miss was likely. When writing the pass mark down, its author also named the AUD rate alone as the likely reason the book’s figure was higher.

**The defined figure misses.** Rollover interest comes to 3.26 percent a year, below the floor of 4.5 percent.

Two other readings fall inside the pass mark.

```math
\small
\begin{array}{l|r|c}
\text{Reading} & \text{Annualised} & \text{Passes} \\ \hline
\text{Difference, 252 days} & 0.0326416903 & \text{no} \\
\text{AUD alone, 252 days} & 0.0466475912 & \text{yes} \\
\text{Difference, 365 days} & 0.0472786388 & \text{yes}
\end{array}
```

1. **The AUD rate alone, 4.66 percent.** That is what the Australian dollars earn before the borrowed Canadian dollars cost anything. It is not the difference the book defines.
2. **The difference over 365 days, 4.73 percent.** The script divides each annual rate by 365 to reach a daily one, so multiplying the daily average back by 365 looks like the natural inverse. It overstates the year, because the tripled day has already paid for the weekends. Each week’s five trading days pay for seven calendar days, so multiplying their average by 365 counts the weekends twice. This reading is the 252-day difference scaled up by 365 / 252, about 1.45 times.

![An animated whiteboard sketch titled “Five trading days pay for seven”, drawn stroke by stroke. A row labelled “AUD” holds five boxes under the weekday names “Mon”, “Tue”, “Wed”, “Thu” and “Fri”. Each box holds the days of interest that day pays, “1”, except Wednesday, which is outlined in brown and holds “3”. A grey brace under the row reads “5 trading days pay 7 days of interest”. A second row labelled “CAD” does the same, except that Thursday is the box outlined in brown and holding “3”, with the same brace and words under it. To the right and between the two rows, a green arrow labelled “average of AUD less CAD” and “× 252 trading days” ends at “3.26 percent”, and below it a red arrow labelled “the same average × 365 counts” and “every weekend again” ends at “4.73 percent”. A grey note reads “365 / 252 is about 1.45,” and “so 3.26 becomes 4.73”, and a brown line closes the sketch: “the tripled day already paid for the weekend”.](../docs/figures/aud_cad_rollover_five_pay_seven.gif)

**This reproduction picks neither.** Either reading could be what Chan computed, and nothing in the book or the script says which, if either. The script computes no rollover figure at all. Choosing a reading after seeing the miss would fit the explanation to the number, so the result stays a miss and both readings stay beside it as explanations. The rollover interest as the book defines it is 3.26 percent a year on these files, not almost 5.

## Lesson 3: a strategy earns rollover interest roughly on its net position

The book’s sentence reads as a surprise. Dropping a rollover interest of almost 5 percent moves the APR by only half a point “even though” the rollover interest is that large. The positions explain it.

**Positions and their cost.** The rule holds a position on 1,217 days, every day after the first 20. It is short on 707 of them and long on 510. A long day earns the day’s rollover interest and a short day pays it, so the short days pay back everything the long days earn, and more. Averaged over all 1,237 days and multiplied by 252, what rollover interest added to each day’s return comes to −0.522 percent a year. It is a cost.

**Net position explains the cost.** The rule holds short on 197 more days than it holds long. Over its 1,217 days that is a net share of −16.2 percent, the long days less the short days as a share of the days held. That share times the 3.26 percent a year from Lesson 2 gives −0.528 percent, near the −0.522 percent that rollover interest actually added. The match is this good because long days and short days see nearly the same rollover interest: 3.290 percent a year averaged over the days held long, and 3.287 percent over the days held short. If the rule had happened to hold long whenever the rollover interest was high, the net share would explain much less. Both averages sit slightly above the 3.26 percent averaged over all 1,237 days, because that average also counts the first 20 days, which hold no position and saw a narrower gap between the two rates.

![An animated whiteboard sketch titled “Long and short days cancel”, drawn slowly stroke by stroke. One bar stands for the 1,217 days the rule holds a position, to scale, with the days grouped by side rather than by date: a green part labelled “510 days long: earn rollover interest” and a red part labelled “707 days short: pay it”. A grey bracket under the bar pairs the 510 long days with as many short ones, a thinner grey line strikes through those days, and the bracket reads “cancel”. A red bracket under the rest of the bar reads “197 more days short:” and, on the line below, “a net share of −16.2 percent”. Below, an arrow labelled “× 3.26 percent a year” points to “−0.528 percent”, and under it a green tick marks “rollover added: −0.522 percent”. A grey note reads “they cancel because long days see 3.290 and short days 3.287 percent a year”, and a brown line closes the sketch: “what is left is the net position”. The finished drawing holds for twelve seconds.](../docs/figures/aud_cad_rollover_long_short_cancel.gif)

**The two APRs differ by more than what rollover interest cost.** Without rollover interest the APR is 6.71 percent, and with it 6.16 percent. The difference between them is 0.558 points, larger than the 0.522 percent a year that rollover interest cost. The APR compounds the daily returns, while the 0.522 percent is 252 times the average of what rollover interest added to each day’s return. They are different summaries of the same days.

**The book’s sentence, answered.** When long days and short days see about the same rollover interest, as they do here, what the long days earn cancels against what the short days pay, and only the net position is left. Here the rule held short on 197 more days than long, 16.2 percent of the 1,217 days it held a position, so a rollover interest of 3.26 percent a year reached the return as a cost of about half a point. The half point in Example 5.2 is what the positions predict, and no surprise.

## Lesson 4: missing months decide the Sharpe ratio’s second decimal

The rate files stop before the trading does. So 84 days have no CAD rate, every trading day of 2012, and 19 have no AUD rate, every trading day of April 2012. The script gives each day the rate of its own month and fills a month the file lacks with zero, carrying nothing forward.

Carrying each file’s last month forward is the alternative. It gives an APR of 6.21 percent and a Sharpe ratio of 0.5457, against the script’s 6.16 percent and 0.5418. The APR still rounds to the book’s 6.2 percent. The Sharpe ratio rounds to 0.55 rather than 0.54.

Neither version is the measured truth. Carrying a month forward is a guess about the missing months, four of CAD’s and one of AUD’s, and the zero fill is a different guess. The book’s 0.54 is what the zero fill produces. So the book’s second decimal rests on a choice about missing data that neither the example nor the script mentions.

## Lesson 5: an exact reproduction checks the arithmetic, not whether the rule makes money

The four figures match to the digit, so the script, the files and the book agree on them. That says nothing about whether trading AUD.CAD this way paid, for two reasons.

1. **No cost is charged.** The rule can reverse its position every day, and the script charges nothing for any trade.
2. **The rule is tested on the days it was reported on.** Chan reported the rule and its 20-day window on the same 2007 to 2012 sample, so those days cannot test them afresh.

A result that could show the rule makes money would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Four questions are beyond it.

1. **Whether the script’s settlement rule is the right one.** The book multiplies a cross rate’s rollover interest when day T + 3 falls on a weekend or holiday, and names Wednesday as the tripled day for both currencies (location 2273). It names T + 1 settlement as the exception for USD.CAD, so for that pair the tripled day is Thursday, when T + 2 falls on a Saturday. The script triples CAD on Thursday, which applies the USD.CAD exception to only the CAD side of the AUD.CAD trade. This reproduction follows the script, because the script printed the figures. Switching to the book’s settlement rule after seeing the figures would choose a settlement rule by its result.
2. **What holidays would add.** The book multiplies the rollover interest for a holiday too, but the script never does, so a position held across Christmas earns nothing for the day the market was shut. Seven weekdays are absent from the closing-price file.
   1. Christmas Day in 2007, 2008 and 2009.
   2. New Year’s Day in 2008, 2009 and 2010.
   3. 2011-12-23, an early close rather than a holiday.
3. **What the 2012 rates were.** Lesson 4 says what carrying a month forward moves, not what the rates were. This reproduction did not check the files against the two central banks’ own tables.
4. **What costs would take.** Nothing here charges any, though the rule reverses its position 180 times over the 1,217 days it holds one.

## What this means for a trader

One habit for each lesson.

1. **Ask what a matching figure can see.** A return built from log moves and signs cannot see the scale of the prices, so a perfect match says nothing about their level.
2. **Check a quoted figure against its own definition.** The book defines rollover interest as a difference of two rates. Its “almost 5 percent” matches the AUD rate alone, or that difference scaled to a year by 365 days, but not the same difference scaled by the 252 trading days the script uses for its returns.
3. **Count the net position before reading a rollover figure.** A strategy that is long and short in turns earns rollover interest roughly on its net position, provided its long and short days see about the same rates.
4. **Find out what fills a missing month.** A zero, a rate carried forward and a measured rate are different inputs, and here the choice moves a printed decimal.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the rule pays needs costs, a rule fixed in writing before the test, and data the rule has not seen.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.2 and Kindle locations 2273, 2287 and 2303.
2. `AUDCAD_daily.m`, git blob `823983a`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. Its line 50 records the printout `APR=0.061564 Sharpe=0.541802`.
3. Dueker, M. J., and Neely, C. J. (2006). Can Markov switching models predict excess foreign exchange returns? Federal Reserve Bank of St. Louis Working Paper 2001-021F, revised January 30, 2006, at [doi.org/10.20955/wp.2001.021](https://doi.org/10.20955/wp.2001.021). Location 2287 cites it as Dueker (2006), and the book’s bibliography, on page 192 of the print edition, lists both authors and dates it 2001. Published as Dueker, M. J., and Neely, C. J. (2007). Can Markov switching models predict excess foreign exchange returns? *Journal of Banking & Finance*, 31(2), 279–296.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_rollover.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_rollover_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_rollover_whiteboard.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_rollover.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_rollover_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_rollover_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-30-audcad-with-rollover-interest-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
