# Chan’s momentum script disagrees with its own comment, and the code agrees with the book

*A script’s closing comment printed a Sharpe ratio of 0.40 against the book’s 4.1. Running the code settles which one to believe, and the rule written before the run decides which match counts.*

## Why reproduce a strategy whose script disagrees with itself

Stocks that rose most over the past year tend to keep rising for a while, and those that fell most tend to keep falling. Ernest Chan’s second book, *Algorithmic Trading*, trades that in its chapter on momentum in stocks. “We can buy and hold stocks within the top decile of 12-month lagged returns for a month, and vice versa for the bottom decile” (Chan, 2013, location 2797).

He reports that on the S&P 500 from 2007-05-15 to 2007-12-31, the strategy earned an annual percentage rate, or APR, of 37 percent, with a Sharpe ratio of 4.1. The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk. Over 2008 and 2009 the APR was “a miserable −30 percent” (Chan, 2013, location 2800). In the same paragraph he cites Daniel and Moskowitz finding 16.7 percent and a Sharpe ratio of 0.83 from 1947 to 2007, so his 4.1 over seven and a half months sits beside a figure from sixty years.

Chan published the script, `kentdaniel.m`, and the data file it reads. The script ends on comment lines recording what it printed, and those lines give a Sharpe ratio of 0.40, a tenth of the book’s. This repository transcribed the script and ran it on the file it loads. The code computes a Sharpe ratio of 4.0657, which rounds to the book’s 4.1, so the comment is the odd one out.

The APR is harder. Before any run, this repository wrote down a rule for reading the book’s “APR”, taken from another example in the same book, and under that rule none of the book’s figures reproduces. A different formula matches both of Chan’s APRs, and it was seen only afterwards. So the post keeps the order in which things were found.

Two labels apply to every figure below.

1. **Every result is exploratory.** Chan chose the rule and its settings, and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether momentum pays.
2. **Every figure is about survivors.** The file holds the S&P 500 as Chan held it on 2012-04-24, carried backwards, so every stock in it survived 2008 and 2009.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the file

Chan’s sentence describes deciles held for a month. `kentdaniel.m` makes that concrete in four steps.

1. **The ranking.** Each stock’s return over the last 252 trading days, about a year.
2. **The picks.** Every day, buy the 50 stocks with the highest return and short the 50 with the lowest.
3. **The holding.** Hold each day’s picks for 25 days. So on any day the portfolio holds 25 overlapping cohorts, where a cohort is one day’s 100 picks.
4. **The sizing.** Sum each day’s returns across every position and divide by 2 · 50 · 25, so a full book of 25 cohorts is one unit of capital.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_stocks_20120424.mat`, saved on 2012-04-25 and converted here to one file per stock. It holds the daily closes of 497 stocks over 1,500 trading days, from 2006-05-11 to 2012-04-24. None of them stops before the last day, and 23 start late. This repository transcribed `kentdaniel.m` line by line from a public copy of Chan’s code, `ivanliu1989/algorithmic_trading` at commit `45670240`. A second public copy holds the same bytes.

The script carries three windows, one pair of lines active and the other two commented out, so it is run once per window. They hold 160, 505 and 582 trading days. The first picks are made on 2007-05-14, the first day a 252-day return exists, and the 2007 window opens the next day. So its first 24 days hold fewer than 25 cohorts, while the script still divides by 25.

The survivors reach the two legs in opposite directions. The short leg lacks stocks that fell and then left the index, which would have earned it money, so their absence pushes the strategy down. The long leg lacks past winners that later collapsed out of the index, which would have cost it money, so their absence pushes the strategy up. Which effect dominates is not measured here.

## Lesson 1: the 0.40 is the comment’s, not the code’s

`kentdaniel.m` prints five figures for the 2007 window, and its closing comment lines record five values for them. Here is each figure, computed, as the script’s print statements format it, and as the comment records it. The book’s figures wait for Lesson 2, because which of these they match is that lesson’s question.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Prints as} & \text{Comment} \\ \hline
\texttt{Avg Ann Ret}\text{, } 252 \times \text{mean} & 0.319989 & 0.3200 & 0.0315 \\
\text{Sharpe ratio} & 4.0657 & 4.07 & 0.40 \\
\texttt{APR}\text{, compounded} & 0.372577 & 0.3726 & 0.0288 \\
\text{Maximum drawdown} & -0.033870 & -0.033870 & -0.066923 \\
\text{Longest drawdown, days} & 23 & 23 & 182
\end{array}
```

None of the five prints what the comment says. The script’s first figure is the arithmetic annual return, 252 times the average daily return. Its third is the compounded APR, which grows the daily returns into a total over the window and annualizes it at 252 days a year. The script labels them `Avg Ann Ret=` and `APR=`.

Four things bear on which side to believe.

1. **A second implementation agrees.** The same rule, written separately in pandas and sharing no code with the transcription, matches it on every day to within 10⁻¹⁵. It shares the transcription’s reading of one function, `lag`, which neither public copy of Chan’s code ships. The first edition of his earlier book defines a `lag1.m` as a shift of one row, and both implementations read `lag` that way. So the agreement rules out a slip in the code and not a misreading of the MATLAB.
2. **No declared variant comes near 0.40.** Before any run, this repository wrote down four readings of the script that could explain the comment, each changing one thing. Their 2007 figures, in the table after this list, sit around the script’s and nowhere near the comment’s.
3. **The helper moves the second decimal, not the first digit.** The Sharpe ratio’s standard deviation comes from a helper named `smartstd`, and Chan’s two books ship two different files under that name. With the first edition’s, the Sharpe ratio is 4.0530, which prints as 4.05 rather than 4.07. [The post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md) teaches the helper in its Lesson 2, where it moves both printed figures. Here it moves one digit, and either helper’s figure is still ten times the comment’s.
4. **Which run printed the comment is not known.** A different file, window or version of the script could each print 0.0315. Trying them until one did would be a search. Try enough variants and one lands by chance, and the landing would say nothing about what Chan ran. So none was tried.

The four readings beside the script, over 2007.

```math
\begin{array}{l|l|r|r}
\text{Reading} & \text{What changes} & \text{Arithmetic return} & \text{Sharpe ratio} \\ \hline
\text{R0} & \text{nothing, the script as printed} & 0.3200 & 4.0657 \\
\text{R1} & \text{one portfolio at a time, re-formed every 25 days} & 0.3222 & 3.9138 \\
\text{R2} & \text{the ranking return ends 21 days back} & 0.2893 & 3.8232 \\
\text{R3} & \text{a day's picks earn that same day, which looks ahead} & 0.3371 & 4.2779 \\
\text{R4} & \text{each day over the cohorts it holds rather than 25} & 0.3215 & 4.0531
\end{array}
```

## Lesson 2: a rule taken from one example did not carry to the next

Lesson 1 left two candidates for the book’s 37 percent: the arithmetic return the script labels `Avg Ann Ret`, and the compounded figure it labels `APR`. Which one Chan meant decides whether his figure reproduces. This lesson takes the steps in the order they happened, because the order is what decides which match counts.

**The rule came first.** Before any run, this repository wrote down [a rule](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-17-cross-sectional-momentum-chans-algorithmic-trading) that read the book’s “APR” as the arithmetic return. The reason was Example 7.2 in the same book, where Chan’s “APR of 6.7 percent” is the arithmetic figure from his script `pead.m` and not its compounded one. [The post on post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md) teaches that in its Lesson 1. The script’s own print line labels the compounded figure `APR=`, and so does `pead.m`’s. The rule followed Example 7.2’s prose over the script’s label. To land the book, the rule needed the 2007 arithmetic return to round to 37 percent and the Sharpe ratio to 4.1, from one reading together.

**Under that rule, nothing reproduces.** Here are the book’s three figures beside both formulas, with the columns in the order they were looked at.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Book} & \text{The rule: arithmetic} & \text{Seen afterwards: compounded} \\ \hline
\text{2007 return} & \text{37 percent} & 0.319989 & 0.372577 \\
\text{2007 Sharpe ratio} & 4.1 & 4.0657 & \text{n/a} \\
\text{2008 and 2009 return} & -30\text{ percent} & -0.323195 & -0.298789
\end{array}
```

The arithmetic return is 32 percent against 37, and −32 against −30. Every reading’s 2007 arithmetic return rounds to 32, 32, 29, 34 or 32, so none reaches 37. The Sharpe ratio rounds to 4.1 for R0 and R4 alone, which the rule called a partial landing, because it needed 37 and 4.1 together. So under the rule written in advance, none of the book’s figures reproduces.

**Afterwards, the compounded figures matched.** 0.372577 and −0.298789 round to 37 and −30 percent, both of the book’s. They are reported beside the verdicts and decide none of them.

**The order stays visible for a reason.** A formula chosen after seeing which one matches is a rule the answer chose. Choose between two formulas after looking, and the one chosen is the one that matches, whatever Chan computed. So the verdicts stand as the declared rule gave them. The match is still worth something. One formula landing both windows is a hypothesis about how Chan labels a return, and a rule for his next example can declare it before that run, which is what would test it.

The same paragraph of the book shows the problem on its face. Location 2800 calls Chan’s own 37 percent an “APR” and Daniel and Moskowitz’s 16.7 percent an “annualized average return”. [The post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md) works through that second phrase in its Lesson 3, where it names both formulas in this book too. The scripts are the consistent party. `kentdaniel.m`, `pead.m` and the buy-on-gap script `bog.m` each label the compounded figure `APR`, and only the prose of Example 7.2 departs from them. Within this book, only the script says which formula produced a return.

## Lesson 3: the crash Chan describes is in the file

`kentdaniel.m` closes on a plot of the cumulative return, compounded from zero over the active window. Run once per window, it draws three charts, and the figure below redraws all three side by side on one scale.

Three of the four observations in this lesson were made after the run and decide nothing. The third is the exception, because the rule for it was fixed before the number was seen.

1. **2007.** The strategy earns a Sharpe ratio of 4.0657 over the window the book reports.
2. **2008 and 2009.** The arithmetic return is −0.323195 and the Sharpe ratio −1.2930. The cumulative return rises to a high on 2008-07-14, then falls to its deepest drawdown, −0.606634, on 2009-09-22. On the window’s last day, 371 days after the high, it is still below it. So the drawdown did not end inside the window. The window ended first.
3. **2010 to 2012.** The arithmetic return is 0.016244 and the Sharpe ratio 0.2004. Chan says the return after 2009 “did stabilize, though it hasn’t returned to its former high level yet” (Chan, 2013, location 2800). The rule for that claim, a return of at least zero and below 2007’s, was written down before the run, and it holds. It is the one row from the book that reproduces.
4. **Chan’s own account.** Later in the chapter, he says the strategy “performed similarly well pre-2008” to the reversal strategy of Chapter 4 on the same universe, whose Sharpe ratio he gives as 4.7. Then cross-sectional momentum “vanished during the aftermath of the stock market crash in 2008–2009” (Chan, 2013, location 2890). [Entry 19 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-19-the-khandani-lo-reversal-on-the-2012-panel-chans-algorithmic-trading) reproduced that 4.7 on this same file as 4.713284.

Chan also gives a cause. The crash “is mainly due to the strong rebound of short positions following a market crisis” (Chan, 2013, location 2890). Nothing here tests that sentence.

![Three line charts side by side on one shared vertical scale, each showing the compounded cumulative return of kentdaniel.m restarted at zero on its window’s first day, in percent of capital, unlevered and before costs. The panels are as wide as their windows are long: 160, 505 and 582 trading days. The left panel, 2007-05-15 to 2007-12-31, climbs to about 22 percent, with its high marked on 2007-11-07 and its deepest drawdown of −0.033870 marked on 2007-11-13. Its heading gives the compounded figure 0.372577, the arithmetic 0.319989 and the Sharpe ratio 4.0657, beside the book’s 37 percent and 4.1. The middle panel, 2008-01-02 to 2009-12-31, rises to a high marked on 2008-07-14, then falls to about −52 percent, with its deepest drawdown of −0.606634 marked on 2009-09-22. A red band covers 2008-07-15 to 2009-12-31, labelled 371 days below the high, still running when the window ends. Its heading gives −0.298789, −0.323195 and −1.2930, beside the book’s −30 percent. The right panel, 2010-01-04 to 2012-04-24, wanders within a few percent of zero, with its high marked on 2011-09-22 and its deepest drawdown of −0.095556 marked on 2012-02-06. Its heading gives 0.013043, 0.016244 and 0.2004, beside the book’s claim that the return did stabilize. The title calls the redraw exploratory, and the note names Chan’s file, says each panel restarts at zero, and says every stock in the file is a survivor.](../docs/figures/cross_sectional_momentum_cumulative_returns.png)

*`kentdaniel.m`’s cumulative return redrawn on Chan’s file, once for each window the script carries. Each panel marks its deepest drawdown, and the red band is the 2008 and 2009 spell below the high, which the window ends inside.*

Nothing compares the redraw with the chart the book prints as Figure 6.6, so it is a redraw of the script’s plot rather than a checked copy.

## Lesson 4: a reproduction checks the arithmetic, not the edge

That the code reproduces the book’s Sharpe ratio, and that its compounded figures land both APRs, says the code, the data and the book agree. It says nothing about whether momentum paid, for four reasons.

1. **Every stock is a survivor, and the two legs lose different stocks.** A company that left the S&P 500 between 2006 and 2012, because it was acquired, shrank or failed, is absent. The short leg could not have sold it as it fell and the long leg could not have held it as it collapsed. [The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches in full what a database of survivors does to a backtest. This repository has not yet rerun this strategy on the index as it stood each day.
2. **No cost is charged.** `kentdaniel.m` charges nothing, yet every day one cohort of 100 picks enters and the one formed 25 days earlier leaves.
3. **The sample is spent on a rule Chan chose.** Reproducing his figures on his window tests his arithmetic, so the result is exploratory. A result that could confirm the edge would need a rule fixed in writing first and data the rule had never seen.
4. **The sample ends in April 2012.** Nothing here says whether momentum pays today.

## What this replication cannot say

Six questions are beyond it.

1. **Which run printed the comment.** Lesson 1 gives the reason none was searched for.
2. **What survivorship does to these figures.** Every stock here was in the S&P 500 on 2012-04-24. Measuring it needs prices for the companies that left.
3. **What costs would take.** Nothing here charges any.
4. **Whether momentum pays today.** The sample ends in April 2012.
5. **Whether Chan’s cause for the crash holds.** He blames the rebound of the short positions. Splitting each day’s return by the side of each position would test that, and nothing here does.
6. **Whether the one flagged day in 2007 was a clean print.** A check this repository runs on other strategies flags 30 days where one stock’s close moved too far for an ordinary day, one in 2007 and 29 in 2008 and 2009. The 2007 one is ETFC’s close on 2007-11-12, which fell from 85.9 to 35.5, and the strategy held ETFC short at the full 25 cohorts going into it. The 2007 panel’s deepest drawdown runs from 2007-11-07 to 2007-11-13, the same week, and nothing here measures how much of it the one print explains. The run does not call the check, because the job is to reproduce what the script computed on the closes as they stand. Nothing here checks that print against another source.

## What this means for a trader

One habit for each lesson.

1. **Run the code before trusting its comment.** A comment records one run, and nothing says which. Here the code agrees with the book and the comment agrees with neither.
2. **Write down which formula a label means before comparing.** “APR” names the arithmetic figure in one example of this book and the compounded one in the next, so the rule has to be fixed before the comparison, and a match found afterwards is a hypothesis for the next test.
3. **Read a drawdown’s length against the window it sits in.** A spell still running when the data ends has no length yet, only a lower bound.
4. **Treat an exact reproduction as a check on arithmetic.** Whether momentum pays needs prices for the companies that left, a charge for costs, and a rule fixed in writing before it meets new data.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 6.2 and Kindle locations 2797, 2800 and 2890.
2. Daniel, K., and Moskowitz, T. J. (2011), as Chan (2013, locations 2800 and 2890) cites them.
3. `kentdaniel.m`, at commit `45670240` of ivanliu1989/algorithmic_trading, a public copy of Chan’s code. ericnberwick/EpchanPreview at commit `e4bc46f` holds the same bytes.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cross_sectional_momentum.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cross_sectional_momentum_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cross_sectional_momentum.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cross_sectional_momentum_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-17-cross-sectional-momentum-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
