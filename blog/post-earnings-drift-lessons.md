# Chan’s post-earnings drift reproduces to the digit, and the digits cannot say whether it pays

*Reproducing a strategy on its author’s own files checks his arithmetic. It does not check his edge.*

## Why reproduce a strategy that trades the news without reading it

Ernest Chan’s second book, *Algorithmic Trading*, has a strategy that trades earnings announcements without reading them. A company announces after the close. The next morning, the stock opens well above or well below where it closed. Chan buys the stock if the open is up and shorts it if the open is down, and closes the position at the end of the same day. His case is that the move after an earnings surprise keeps going in the same direction for a while, and that the open already tells the trader which direction that is. The strategy “does not even require the trader to know whether the earnings are above or below analysts’ expectations” (Chan, 2013, location 2994).

He reports that on the S&P 500 from January 2011 to April 2012, the strategy earned an APR of 6.7 percent with a Sharpe ratio of “a very respectable 1.5” (Chan, 2013, location 3024). The book’s code reads two data files that Chan saved, and both are public, so this repository committed them and ran his script on them.

Every figure Chan prints for this example lands. The arithmetic annual return comes out at 0.066743, which is the book’s 6.7 percent. The Sharpe ratio comes out at 1.4909, which is the book’s 1.5. The script’s other three printed figures land too, and so do two numbers Chan states in his text.

None of that says whether the drift pays. A reproduction on the author’s files with the author’s script can say whether his numbers follow from his data. It cannot say what the strategy earned on the stocks a trader could actually have held in 2011, what it earns after costs, or what it has earned since.

The five lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the two files

The effect is called post-earnings announcement drift. Prices keep moving in the direction of an earnings surprise after the announcement, and Chan says it has been “known and studied since 1968”, citing Bernard and Thomas, 1989 (Chan, 2013, location 2994). His explanation is that information spreads slowly: if momentum comes from “the slow diffusion of news”, a trader can profit from the hours right after the news (Chan, 2013, location 2990).

His version measures the surprise from the price alone. Call the move from one day’s close to the next day’s open the gap. In this post, gap means only that.

1. **The announcement.** The trade needs a stock that announced after the previous close and before today’s open, between 4:00 p.m. and 9:30 a.m. Eastern (Chan, 2013, locations 3002 and 3010). An announcement during the trading day does not count, because its news is already in the open.
2. **The threshold.** The gap has to be large against the stock’s own recent gaps. Chan measures that with the 90-day moving standard deviation of the gap, which is the yardstick for whether an announcement was “surprising” enough (Chan, 2013, location 3019). A gap of at least half that deviation goes long. A gap of at most minus half goes short.
3. **The holding period.** The position opens at the open and closes at the same day’s close.
4. **The sizing.** Each day’s returns are summed across stocks and divided by 30, so every position gets a thirtieth of the capital.

[Two files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) carry the data, both Chan’s own MATLAB files converted to one file per stock.

1. **The prices**, `inputDataOHLCDaily_stocks_20120424.mat`: the opens and closes of 497 stocks, saved on 2012-04-25.
2. **The flags**, `earnannFile.mat`: for the same 497 stocks, a 1 on each day the stock announced between the previous close and the open, and a 0 otherwise. Saved on 2012-05-15, it covers 330 trading days, from 2011-01-03 to 2012-04-24.

The script, `pead.m`, cuts the prices down to the flag file’s 330 days and runs the rule. This repository transcribed it line by line from a public mirror of Chan’s code, `ivanliu1989/algorithmic_trading` at commit `45670240`.

One more fact about the price file decides what any of this can mean. It is the S&P 500 as Chan held it on 2012-04-24, carried backwards. A company that left the index before that day is not in it. Lesson 5 comes back to that.

Every result below is **exploratory**. Reproducing Chan’s figures spends the 2011 and 2012 sample on a rule he chose, so the run says whether his numbers follow from his files and nothing about whether the drift pays.

## Lesson 1: every figure Chan prints reproduces on his own files

`pead.m` prints five figures in the comment lines that close it. The book quotes two of them, rounded, and states two more numbers in its text. Here is each one, computed, as the script prints it, and as the book gives it.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \texttt{pead.m} & \text{Book} \\ \hline
\text{Arithmetic annual return} & 0.066743 & 0.0667 & \text{6.7 percent} \\
\text{Sharpe ratio} & 1.4909 & 1.49 & 1.5 \\
\text{Compounded APR} & 0.067952 & 0.0680 & \text{none} \\
\text{Maximum drawdown} & -0.026052 & -0.026052 & \text{none} \\
\text{Longest drawdown, days} & 109 & 109 & \text{none} \\
\text{Most positions on one day} & 30 & \text{none} & 30 \\
\text{Levered four times} & 0.266970 & \text{none} & \text{close to 27 percent}
\end{array}
```

Every computed figure lands on the printed one at the precision it was printed. The book’s numbers come from location 3024, and the script’s from its own closing lines.

The book calls its 6.7 percent an APR, and the script prints two figures that could carry that name. The arithmetic one is 252 times the mean daily return. The compounded one grows the daily returns into a total and annualizes it. At the book’s one decimal, the compounded figure reads 6.8 percent, so the book’s 6.7 can only be the arithmetic one. A check that set 6.7 against the compounded figure would fail on a correct transcription and look like a problem with the data.

The figure below redraws what `pead.m` draws last, the cumulative return Chan prints as Figure 7.2 in the book. Nothing compares it with the book’s own figure, which is not among the committed highlights, so it is a redraw of the script’s plot rather than a checked copy of the book’s.

![A line chart of the strategy’s compounded cumulative return over 330 trading days from January 2011 to April 2012, in percent of capital, unlevered and before costs. A grey band covers the first 89 days, labelled as holding no position before the 90-day deviation fills, and the line is flat at zero there. From mid-May the line climbs slowly, jumps steeply in early August to a high marked on 2011-08-04, and then sits below that high inside a shaded red band labelled 109 days below the high, from 2011-08-05 to 2012-01-10. A red point inside the band marks the deepest drawdown, −0.026052, on 2011-11-02. The line recovers past the high in January 2012 and ends above it. The title calls the redraw exploratory, and the note names Chan’s two files and says the price file holds only survivors.](../docs/figures/pead_cumulative_return.png)

*`pead.m`’s cumulative return, redrawn on Chan’s files. The grey band is the stretch before the moving deviation can be computed, and the red band is the longest spell below a high.*

## Lesson 2: the gap stands in for the surprise, and the flags stand in for the calendar

The strategy never reads an earnings number. It reads two things that stand in for one, and each is something a trader can check.

1. **The gap stands in for the surprise.** Half a moving standard deviation is a low bar. On the committed files, 1,279 announcements fall on or after the first day the 90-day deviation can be computed, and 1,072 of them clear the bar and are traded. So most flagged announcements get traded, and whether a stock trades on a given day comes down mostly to whether the flag file marks it.
2. **The flags stand in for the calendar.** The strategy trades only where Chan’s flag file says a stock announced overnight. The file holds 1,885 flags across its 497 stocks, and 29 of the stocks carry none at all, so the strategy can never trade them. Apple is flagged on three days: 2011-04-21, 2011-07-20 and 2012-01-25. Apple released earnings five times inside the window, so two of its releases carry no flag. Whether that comes from timing or from the source Chan scraped, the committed file cannot say.

The book supplies a function that builds flags like these by scraping about a year of an earnings calendar from earnings.com (Chan, 2013, location 3002). Nothing committed here records what that calendar held. [Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) reruns the rule on announcement times from the SEC’s EDGAR filings, which a reader can fetch today.

The short holding period is part of Chan’s argument too. In the previous chapter he writes that momentum from earnings announcements “used to last several days” and now lasts “barely until the market closes” (Chan, 2013, location 2890). That is why the strategy exits at the close.

## Lesson 3: the 30 and the leverage are facts about the run

Two of Chan’s numbers are outputs of the backtest that he then uses as inputs to it.

1. **The 30.** The busiest day of the run holds 30 positions, and that is the number Chan divides each day’s return by, because “there is a maximum of 30 positions in one day” (Chan, 2013, location 3024). Nobody trading in January 2011 could have known the busiest day ahead would hold 30. Chan names the problem himself, “a certain degree of look-ahead bias”, and argues it is “not a very grievous bias” because the number of announcements a day is predictable (Chan, 2013, location 3024). The reproduction confirms the 30 and cannot measure the bias.
2. **The idle capital.** Sizing every position at a thirtieth of capital means that on a day with fewer than 30 positions, the rest of the capital earns nothing. No position is possible in the first 89 days, because the 90-day deviation has not filled, which is the grey band in the figure. The first position comes on the first day one could, 2011-05-11. Across the whole window, 157 of the 330 days hold any position at all, so more than half the days hold none.
3. **The leverage.** Idle capital is what makes Chan’s next step possible. Because the strategy holds nothing overnight, he says it can be levered “by at least four times, giving an annualized average return of close to 27 percent” (Chan, 2013, location 3024). Leverage multiplies every day’s return, so it multiplies the arithmetic annual return. At exactly four, the figure is 0.266970, which rounds to his 27. The check takes four because it is the floor Chan states.

The figure shows what the idle days do to the line. The longest spell below a high runs 109 trading days, from 2011-08-05 to 2012-01-10, and the deepest drawdown, −0.026052, falls inside it on 2011-11-02. `pead.m` reports the depth and the length separately, and the two need not belong to the same spell. On this run they do.

## Lesson 4: which book’s helper runs decides a printed digit

`pead.m` calls a helper named `smartstd`, a standard deviation that tolerates missing values. Chan’s two books ship two different helpers under that name. The one from *Algorithmic Trading* skips a missing value and divides by n. The one from the first edition of *Quantitative Trading* counts a missing value as zero and divides by n − 1.

[The post on the equity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) teaches this on the revised Example 7.7, where the second book’s helper prints a Sharpe ratio of −0.1243 and the first edition’s gives −0.1236. Two things are new here.

1. **The helper belongs to this example’s own book.** The first edition’s helper ran this repository’s earlier replications, so it was the one a port would reach for first. The right one for `pead.m` is the second book’s, the book the script comes from.
2. **The digit that moves is the return, not the Sharpe ratio.** Here `smartstd` runs inside the 90-day moving deviation as well as in the Sharpe ratio. With the first edition’s helper, the strategy takes 1,071 positions rather than 1,072, and the arithmetic annual return becomes 0.066833. That prints as 0.0668, one unit off the script’s 0.0667. The Sharpe ratio, the compounded APR and both drawdown figures still print as Chan’s.

So a port that used the wrong helper would land on four of the five printed figures and miss the fifth by one digit. That looks like a near miss on the data. It is a wrong helper, and the only way to tell the two apart is to check which helper the script’s own book ships.

## Lesson 5: an exact reproduction checks the arithmetic, not the edge

Every figure landing says that the code, the data and the book agree. It says nothing about whether the drift paid, for three reasons.

1. **Every stock is a survivor.** The price file is the S&P 500 as it stood on 2012-04-24, carried backwards over the window. A company that left the index during 2011, because it was acquired, shrank or failed, is absent, and the strategy could not have traded its announcements. [The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches in full what a database of survivors does to a backtest. [Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) reruns this strategy on the index as it stood each day.
2. **No cost is charged.** `pead.m` charges nothing, and every position is a full round trip inside one day: a buy and a sell, or a short and a cover, each paying a spread and a commission. A strategy that trades 1,072 times across 330 days at a thirtieth of capital each carries costs a reader would want priced before believing the 6.7 percent.
3. **The sample is spent.** Chan chose the rule and its settings, and took the 30 from this very window. Reproducing his figures on the same days tests his arithmetic, so the result is exploratory. A result that could confirm the drift would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Five questions are beyond it.

1. **What the drift earned on the index as it stood each day.** Every stock here was in the S&P 500 on 2012-04-24. [Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) is where that gets measured.
2. **Whether Chan’s flags are the announcement calendar.** They miss two of Apple’s five releases inside the window. [Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) reruns the rule on EDGAR’s filings.
3. **What costs would take.** Nothing here charges any.
4. **How large the look-ahead in the 30 is.** Chan argues it is small, and nothing here tests the argument.
5. **Whether holding overnight adds anything.** Chan says it does not, because “the overnight returns are negative on average”, and reads that as the drift having shortened as more traders learned of it (Chan, 2013, location 3039). The script holds nothing overnight, so nothing here tests the claim.

## What this means for a trader

One habit for each lesson.

1. **Reproduce the printed figures before arguing with them.** Every figure for this example lands on Chan’s files, so any disagreement with his result is about the data or the edge, not his arithmetic.
2. **Check each stand-in a strategy reads.** The gap stands in for the surprise and a scraped calendar stands in for the announcements. Each can be wrong in its own way, and here the calendar decides most of what gets traded.
3. **Ask which numbers were chosen after the backtest ran.** The 30 is the busiest day of the very window it sizes, and the four-times leverage rests on how much capital that 30 leaves idle.
4. **Find out which version of a helper the author ran.** A helper’s name does not identify it, and the wrong one can cost one printed digit and look like noise.
5. **Treat an exact reproduction as a check on arithmetic.** Whether the drift pays needs survivors replaced, costs charged and a rule written down before new data is read.

On Chan’s own files, every number he prints for this strategy reproduces. Whether it earns money is a separate question, and two open issues are where it gets asked.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 7.2 and Kindle locations 2890, 2990, 2994, 3002, 3010, 3019, 3024 and 3039.
2. Bernard, V. L., & Thomas, J. K. (1989), as Chan (2013, location 2994) cites them for the drift’s history.
3. `pead.m`, at commit `45670240` of the ivanliu1989/algorithmic_trading mirror of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pead_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pead_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-12-post-earnings-drift-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
