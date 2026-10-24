# Chan’s post-earnings drift reproduces to the digit, and the digits cannot say whether it pays

*Reproducing a strategy on its author’s own files checks his arithmetic. It does not check his edge.*

## Why reproduce a strategy that trades the news without reading it

Ernest Chan’s second book, *Algorithmic Trading*, has a strategy that trades earnings announcements without reading them. A company announces after the close. The next morning, the stock opens well above or well below where it closed. Chan buys the stock if the open is up and shorts it if the open is down, and closes the position at the end of the same day. His case rests on an effect called post-earnings announcement drift: after an earnings surprise, a result above or below what analysts expected, the price keeps moving in the same direction for a while. The open already tells the trader which direction that is. The strategy “does not even require the trader to know whether the earnings are above or below analysts’ expectations” (Chan, 2013, Kindle location 2994).

He reports that on the S&P 500 from January 2011 to April 2012, the strategy earned an annual percentage rate, or APR, of 6.7 percent, with a Sharpe ratio of “a very respectable 1.5” (Chan, 2013, location 3024). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk.

Chan published both his code and the two data files it reads, so a reader can check whether his figures follow from them before arguing about the strategy. Any later argument about whether the drift pays rests on that check. This repository keeps copies of both files, translated his script line by line into Python, and ran the translation on them.

### What the reproduction found

Every number Chan prints for this example matches. Recomputed here, the arithmetic annual return, which is the average daily return times 252 trading days a year, is 0.066743, the book’s 6.7 percent. Lesson 1 shows why the book’s APR is this figure. The Sharpe ratio is 1.4909, the book’s 1.5. Three more figures the script prints match too, and so do two numbers Chan states in his text. Lesson 1’s table lists all seven. Every one of these results is **exploratory**. Chan chose the rule and its settings on these same days, so the results can show that his numbers reproduce but cannot confirm that the strategy works.

None of that says whether the drift pays. A reproduction on the author’s files with a translation of the author’s script can say whether his numbers follow from his data. It cannot say what the strategy earned on the stocks a trader could actually have held in 2011, what it earns after costs, or what it has earned since.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the two files

Chan says the drift has been “known and studied since 1968”, citing a 1989 paper by Bernard and Thomas (Chan, 2013, location 2994). His argument starts from a common belief. “If, as many people believe, momentum is driven by the slow diffusion of news”, a trader can profit from the first few days, hours or even seconds after the news (Chan, 2013, location 2990). Momentum here means a price that keeps moving the way it has been moving.

His version measures the surprise from the price alone. Call the move from one day’s close to the next day’s open the gap. In this post, gap means only that.

1. **The announcement.** The trade needs a stock that announced after the previous close and before today’s open, between 4:00 p.m. and 9:30 a.m. Eastern (Chan, 2013, locations 3002 and 3010). An announcement during a trading day does not count. One made during the previous day’s session is already in that day’s close, so the gap does not carry it. One made after today’s open comes too late for a trade entered at the open.
2. **The threshold.** The gap has to be large against the stock’s own recent gaps. Chan measures that with the gap’s 90-day moving standard deviation, which is the standard deviation of the stock’s gaps over the most recent 90 trading days, recomputed each day. It is the yardstick for whether an announcement was “surprising” enough (Chan, 2013, location 3019). A gap of at least half that deviation goes long. A gap of at most minus half goes short.
3. **The holding period.** The position opens at the open and closes at the same day’s close. In the chapter before this example, Chan writes that momentum from earnings announcements “used to last several days” and now lasts “barely until the market closes” (Chan, 2013, location 2890). That is why the strategy exits at the close.
4. **The sizing.** The strategy sums each day’s returns across stocks and divides by 30, so every position gets a thirtieth of the capital. Lesson 3 says where the 30 comes from.

![An animated whiteboard sketch titled “One trade, two days”, drawn slowly stroke by stroke. It is schematic and carries no figures from the run. A grey time axis runs across the board with three ticks labelled “close 4:00 p.m.”, “open 9:30 a.m.” and “close”, and beneath it “the day before” and “today” name the two sessions. A black price line wanders through the day before’s session and ends at its 4:00 p.m. close. A brown bracket spans the night from that close to the next open, labelled “announced here: counts”. A grey dashed line carries the close’s level across the night, and a black arrow at the open climbs from it to the higher open, labelled “the gap: the signal”. A second black price line runs through today’s session from the open to the close. A thick green bar runs beneath it from the open to the close, labelled “held: the return earned”, and in the night a grey note reads “nothing held overnight”. Last, a red mark crosses the day before’s price inside its session, labelled “news already in the close, so the gap misses it”, and a red mark crosses today’s price after the open, labelled “too late: the trade opened at 9:30”. The finished drawing holds for twelve seconds.](../docs/figures/pead_sketch_one_trade.gif)

Two files carry the data, both Chan’s own MATLAB files, converted here to one file per stock. The repository’s [data notes](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) record where each copy came from and when it was saved.

1. **The prices**, `inputDataOHLCDaily_stocks_20120424.mat`: the opens and closes of 497 stocks, saved on 2012-04-25.
2. **The flags**, `earnannFile.mat`: for the same 497 stocks, a 1 on each day the stock announced between the previous close and the open, and a 0 otherwise. Saved on 2012-05-15, it covers 330 trading days, from 2011-01-03 to 2012-04-24.

The script, `pead.m`, cuts the prices down to the flag file’s 330 days and runs the rule. The translation follows the copy in a public mirror of Chan’s code, `ivanliu1989/algorithmic_trading` at commit `45670240`.

The price file holds 497 stocks, Chan’s list of the S&P 500 on 2012-04-24, with each one’s prices running back from that day. A company that left the index during 2011 is not in the file. Lesson 5 comes back to that.

## Lesson 1: every number Chan prints reproduces on his own files

The comment lines that close `pead.m` record five figures the script prints. The book quotes two of them, rounded, and states two more numbers in its text. The table gives each one as this repository computes it, as the script prints it, and as the book gives it. Its first and third rows are the arithmetic and compounded annual returns. The two drawdown rows give the deepest fall below an earlier high, as a fraction of that high, and the most consecutive trading days spent below one. The last row is the arithmetic return levered four times, which the book calls close to 27 percent.

```math
\small\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \texttt{pead.m} & \text{Book} \\ \hline
\text{Arithmetic} & 0.066743 & 0.0667 & 6.7\% \\
\text{Sharpe ratio} & 1.4909 & 1.49 & 1.5 \\
\text{Compounded} & 0.067952 & 0.0680 & \text{none} \\
\text{Max drawdown} & -0.026052 & -0.026052 & \text{none} \\
\text{Longest, days} & 109 & 109 & \text{none} \\
\text{Most positions} & 30 & \text{none} & 30 \\
\text{Levered 4x} & 0.266970 & \text{none} & 27\%
\end{array}
```

Every computed figure matches the printed one at the precision the source printed it. The book’s numbers come from location 3024, and the script’s from its own closing lines.

The book calls its 6.7 percent an APR, and the script prints two figures that could carry that name. One is the arithmetic annual return. The other, the compounded APR, grows the daily returns into a total and annualizes it. At the book’s one decimal, the compounded figure reads 6.8 percent, so the book’s 6.7 can only be the arithmetic one. A check that set 6.7 against the compounded figure would fail on a correct transcription and look like a problem with the data.

The figure below redraws what `pead.m` draws last, the cumulative return the book shows as Figure 7.2. No check here compares the redraw with the book’s own figure, which this repository holds no copy of, so it is a redraw of the script’s plot rather than a checked copy of the book’s.

![A line chart of the strategy’s compounded cumulative return over 330 trading days from January 2011 to April 2012, in percent of capital, unlevered and before costs. A grey band covers the first 89 days, labelled as holding no position before the 90-day deviation fills, and the line is flat at zero there. From mid-May the line climbs slowly, jumps steeply in early August to a high marked on 2011-08-04, and then sits below that high inside a shaded red band labelled 109 days below the high, from 2011-08-05 to 2012-01-10. A red point inside the band marks the deepest drawdown, −0.026052, on 2011-11-02. The line climbs back to the high in January 2012, rises past it, and ends near 9 percent in April 2012. The title calls the redraw exploratory, and the note names Chan’s two files and says every stock in the price file is a survivor.](../docs/figures/pead_cumulative_return.png)

*`pead.m`’s cumulative return, redrawn on Chan’s files. The grey band is the stretch before the moving deviation can be computed, and the red band is the longest spell below a high.*

The red band runs 109 trading days, from 2011-08-05 to 2012-01-10, and the deepest drawdown, −0.026052, falls inside it on 2011-11-02. `pead.m` reports the depth and the length separately, and the two need not belong to the same spell. On this run they do.

## Lesson 2: the gap stands in for the surprise, and the flags stand in for the calendar

The strategy never reads an earnings number, and it never reads a calendar of when each company announced. It reads a stand-in for each, and a trader can check both.

1. **The gap stands in for the surprise.** Half a moving standard deviation is a low bar. On Chan’s two files, 1,279 announcements fall on or after the first day the 90-day deviation can be computed, and 1,072 of them clear the bar and are traded. So most flagged announcements get traded, and whether a stock trades on a given day comes down mostly to whether the flag file marks it.
2. **The flags stand in for the calendar of when each company announced.** The strategy trades only where Chan’s flag file says a stock announced overnight. The file holds 1,885 flags across its 497 stocks, and 29 of the stocks carry none at all, so the strategy can never trade them. Apple is flagged on three days: 2011-04-21, 2011-07-20 and 2012-01-25. Apple released earnings six times inside the window. The last came on its final day, 2012-04-24, so only five have a next morning inside it, and two of those five mornings carry no flag. The file itself cannot say why. Its source may have recorded those two releases at a time the overnight rule skips, or may have missed them.

The book supplies a function that builds flags like these by scraping about a year of an earnings calendar from earnings.com (Chan, 2013, location 3002). Nothing in this repository records what that calendar held.

EDGAR, the SEC’s public database of company filings, records the time it accepted each company’s earnings filing, and a reader can fetch that record today. A later rerun here built a calendar from those times with a single rule. The rule flags a day only when a filing was accepted between the previous trading day’s close and that day’s open, so a filing accepted during trading hours flags nothing. That calendar flags 2011-01-19 and 2011-10-19, the mornings after the two Apple releases Chan’s file misses. EDGAR also shows that all six of Apple’s filings inside the window were accepted at about 4:30 p.m. Eastern, after the close. So the filing times look the same for the two releases Chan’s file misses and the three it flags. The rerun is exploratory, and [Entry 46 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-46-post-earnings-drift-on-edgars-calendar-and-the-archives-prices-chans-algorithmic-trading) carries it.

## Lesson 3: the 30 and the leverage are facts about the run

Two of Chan’s figures depend on this one run. The 30 comes out of the backtest and then goes back into it. The levered 27 percent multiplies a return that the 30 divided.

1. **The 30.** The busiest day of the run holds 30 positions, and that is the number Chan divides each day’s return by, because “there is a maximum of 30 positions in one day” (Chan, 2013, location 3024). Nobody trading in January 2011 could have known the busiest day ahead would hold 30. Chan names the problem himself, “a certain degree of look-ahead bias”, and argues it is “not a very grievous bias” because “the maximum number of announcements per day is quite predictable” (Chan, 2013, location 3024). The reproduction confirms the 30 and cannot measure the bias.
2. **The leverage.** Because the strategy holds nothing overnight, Chan says it can be levered “by at least four times, giving an annualized average return of close to 27 percent” (Chan, 2013, location 3024). Leverage multiplies every day’s return, so it multiplies the arithmetic annual return. At exactly four, the figure is 0.266970, which rounds to his 27. This post uses four because it is the floor Chan states.

Dividing by the busiest day’s count has a cost on every other day. Each position gets a thirtieth of the capital, so on a day with fewer than 30 positions, the rest of the capital earns nothing.

Many days hold no position whatever the divisor. No position is possible in the first 89 days, because the deviation needs 90 days in its window before it gives a number. The figure shades those days grey. The first position comes on the first day one could, 2011-05-11. After that, a day holds a position only when a flagged stock clears the bar. Across the whole window, 157 of the 330 days hold any position at all, so more than half the days hold none.

## Lesson 4: which book’s helper runs decides a printed digit

`pead.m` calls a helper named `smartstd`, a standard deviation that tolerates missing values. Chan’s two books ship two different helpers under that name. The one from *Algorithmic Trading* skips a missing value and divides by n, the number of values it kept. The one from the first edition of *Quantitative Trading* counts a missing value as zero and divides by n − 1, where n counts every value, the zeros included.

[The post on the equity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) teaches this on Example 7.7 from the revised edition of *Quantitative Trading*. There the *Algorithmic Trading* helper gives the printed Sharpe ratio of −0.1243, and the first edition’s helper gives −0.1236. Two things are new here.

1. **The helper belongs to this example’s own book.** The first edition’s helper ran this repository’s earlier replications, so it was the one a translation of Chan’s code would reach for first. The right one for `pead.m` is the *Algorithmic Trading* helper, from the book the script comes from.
2. **The digit that moves is the return, not the Sharpe ratio.** Here `smartstd` runs inside the 90-day moving deviation as well as in the Sharpe ratio. With the first edition’s helper, the strategy takes 1,071 positions rather than 1,072, and the arithmetic annual return becomes 0.066833. That prints as 0.0668, one unit off the script’s 0.0667. The Sharpe ratio, the compounded APR and both drawdown figures still print as Chan’s.

The one position that changes is PNW on 2012-02-24. Its gap was 0.4212 percent. Half the *Algorithmic Trading* helper’s deviation was 0.4189 percent, so it went long. Half the first edition’s was 0.4213 percent, so it did not. PNW has a gap on all 90 days of its window, so counting a missing value as zero plays no part here. The only difference left is the divisor, 89 rather than 90, and that alone widens the deviation. That long lost 0.36 percent on the day, so dropping it raises the return.

![An animated whiteboard sketch titled “One position the helper flips”, drawn slowly stroke by stroke. Its marks are drawn to one scale from the run. A grey number line runs across the board. Near its left end a green upright tick is labelled “half the Algorithmic Trading helper’s deviation: 0.4189%” above and “long” below. Near its right end a taller red upright tick is labelled “half the first edition’s deviation: 0.4213%” above and “no trade” below. A black dot sits on the line just left of the red tick, past the green one and short of the red one, labelled “PNW’s gap on 2012-02-24: 0.4212%”. Last, a line beneath reads “the long lost 0.36%: annual return 0.0667 with it, 0.0668 without”. The finished drawing holds for twelve seconds.](../docs/figures/pead_sketch_helper_flip.gif)

*Drawn to one scale from the run. The black dot is PNW’s gap. It lies past the green tick, so with the *Algorithmic Trading* helper the rule goes long, and short of the red tick, so with the first edition’s helper it takes no trade.*

So a translation that used the wrong helper would match four of the five printed figures and miss the fifth by one digit. That looks like a small difference in the data. It is a wrong helper, and the only way to tell the two apart is to check which helper the script’s own book ships.

## Lesson 5: an exact reproduction checks the arithmetic, not the edge

That every number matches shows that the code, the data and the book agree. It says nothing about whether the drift paid, for three reasons.

1. **Every stock is a survivor.** The price file holds Chan’s list of the S&P 500 on 2012-04-24, with each stock’s prices running back from that day. A company that left the index during 2011, because it was acquired, shrank or failed, is absent. A trader in 2011 could have traded its announcements while it was still a member, but the backtest never sees them. [The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches in full what a database of survivors does to a backtest. This repository has not yet rerun this strategy on the index as it stood each day.
2. **No cost is charged.** `pead.m` charges nothing, and every position is a full round trip inside one day: a buy and a sell, or a short and a cover, each paying a spread and a commission. A strategy that trades 1,072 times across 330 days at a thirtieth of capital each carries costs a reader would want priced before believing the 6.7 percent.
3. **The rule was chosen on the same days it is tested on.** Chan chose the rule and its settings, and took the 30 from this very window. Reproducing his figures on the same days tests his arithmetic, so the result is exploratory. A result that could confirm the drift would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Five questions are beyond it.

1. **What the drift earned on the index as it stood each day.** Every stock here is on the S&P 500 list Chan held on 2012-04-24. Measuring it needs prices for the companies that left the index during the window.
2. **Whether Chan’s flags are the announcement calendar.** They miss two of the five Apple releases whose next morning falls inside the window. The later rerun, which is exploratory, built a calendar from EDGAR’s filings by one rule. Over the 488 stocks it could match to a filer, that calendar and Chan’s share 1,540 flags. Chan’s file holds 311 that the rule does not give, and the rule gives 914 that his file lacks. Neither count says which calendar is right. The rule flags nothing for a filing accepted during the session, a filing can be accepted days after the release it reports, and nothing reads a filing’s text to check that it reports earnings. So his flags are one reading of the calendar rather than the calendar itself, and every figure in this post is computed on his flags.
3. **What costs would take.** Nothing here charges any.
4. **How large the look-ahead in the 30 is.** Chan argues it is small, and nothing here tests the argument.
5. **Whether holding overnight adds anything.** Chan says it does not, because “the overnight returns are negative on average”, and says this “may be” a case of the drift shortening as more traders learned of it (Chan, 2013, location 3039). The script holds nothing overnight, so nothing here tests the claim.

## What this means for a trader

One habit for each lesson.

1. **Reproduce the printed figures before arguing with them.** Every number Chan prints for this example matches on his files, so any disagreement with his result is about the data or the edge, not his arithmetic.
2. **Check each stand-in a strategy reads.** The gap stands in for the surprise and a flag file stands in for the announcement calendar. Each can be wrong in its own way, and here the flag file decides most of what gets traded.
3. **Ask which numbers were chosen after the backtest ran.** The 30 is the busiest day of the very window it sizes, and the 27 percent depends on it, since leverage multiplies a return that was divided by 30.
4. **Find out which version of a helper the author ran.** A helper’s name does not identify it, and the wrong one can cost one printed digit and look like noise.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the drift pays needs the companies that left the index put back, costs charged and a rule written down before new data is read.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 7.2 and Kindle locations 2890, 2990, 2994, 3002, 3010, 3019, 3024 and 3039.
2. Bernard, V. L., & Thomas, J. K. (1989), as Chan (2013, location 2994) cites them for the drift’s history.
3. `pead.m`, at commit `45670240` of the ivanliu1989/algorithmic_trading mirror of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-12-post-earnings-drift-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
