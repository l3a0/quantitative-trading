# Chan’s buy on gap reproduces on his own file, and its mirror does not

*Reproducing a strategy on its author’s own file checks the figures he printed. A rule he only described has to be written down before it can be checked at all.*

## Why reproduce a strategy that buys a panic

In its chapter on mean reversion in stocks, Ernest Chan’s second book, *Algorithmic Trading*, has a strategy that buys a morning panic. On a day when index futures are down before the open, he argues, some stocks open far below where they traded the day before, because of “panic selling at the open”. Once the selling is over, the stock “will gradually appreciate over the course of the day” (Chan, 2013, location 1948). So the strategy buys those stocks at the open and sells them at the same day’s close.

He reports that on the S&P 500 from May 2006 to April 2012, the strategy earned an annual percentage rate, or APR, of 8.7 percent, with a Sharpe ratio of 1.5 (Chan, 2013, location 1974). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk. He also reports the mirror image, which shorts stocks that open far above the day before, at an APR of 46 percent and a Sharpe ratio of 1.27 (Chan, 2013, location 1993).

### What the reproduction found

Chan published the script for the first strategy and the data file it reads, so a reader can check whether his figures follow from them before arguing about the strategy. This repository keeps the file’s contents as one table per stock. Together the tables rebuild the file’s open, high, low, close and volume arrays exactly. This repository ran a line-by-line Python transcription of the script on those tables. He published no script for the mirror, so this repository wrote a rule down from his one sentence about it before running anything.

Both figures Chan prints for the first strategy match. The computed APR is 0.087385, the book’s 8.7 percent, and the computed Sharpe ratio is 1.5371, the book’s 1.5. The mirror does not match. The rule written down here lands at an APR of 12 percent and a Sharpe ratio of 1.79.

Two labels apply to every figure below.

1. **Every result is exploratory.** Chan chose the rule and its settings, and the reproduction tests them on the same days he did. The reproduction can say whether his numbers follow from his file and nothing about whether the rule pays.
2. **Every figure is about survivors.** The file holds 497 stocks that were in the S&P 500 in late 2011, and treats them as the index on every earlier day too. A company that was out of the index for all of late 2011 is not in the file, and Chan says the universe “has survivorship bias” (Chan, 2013, location 1974).

The six lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the file

Chan states four rules (Chan, 2013, location 1948).

1. **The drop.** Select the stocks whose return from the previous day’s low to today’s open is “lower than one standard deviation”. Chan’s script, `bog.m`, reads that as a drop of more than one standard deviation. The standard deviation is that of the stock’s close-to-close returns over the last 90 days. These are the stocks that gapped down. In this post, gap means only that move to the open.
2. **The filter.** Keep only the stocks whose open is still above the 20-day moving average of their closes.
3. **The selection.** Buy the ten with the deepest drops, or all of them if fewer than ten qualify.
4. **The exit.** Sell everything at the close.

The script adds a fifth rule about sizing. It sums each day’s returns across the stocks it bought and divides by 10, however many stocks it bought that day. So a day with three stocks holds three tenths of the capital and leaves the rest idle.

Chan gives a reason for rule 2, which he calls “a momentum filter superimposed on a mean-reverting strategy”. A mean-reverting strategy bets that a price returns toward where it was, and a momentum filter keeps only stocks still trading above their recent average, here an open above the 20-day moving average. Chan argues that a stock that dropped “just a little” is more likely to recover than one that dropped “a lot”, because a large drop often carries bad news, and a drop caused by news is less likely to revert (Chan, 2013, location 1948).

![An animated whiteboard sketch titled “Where the open has to land”, drawn stroke by stroke and drawn to scale from one day’s prices. A grey price axis rises on the left, labelled “price”, and grey words at the top right read “PCS on 2011-01-06, the only stock bought”. Three lines run right from the axis. A solid line at the top is labelled “yesterday’s low 13.68”. A dashed line below it is labelled “low × (1 − 0.020967) 13.39”, the previous low lowered by a fraction equal to one 90-day standard deviation of the stock’s daily returns. A solid line lower still is labelled “20-day average 12.70”. A pale green band with a green edge fills the space between the dashed line and the average, labelled “an open in this band qualifies”. A brown dot lands inside the band, labelled “open 13.01” on the left of the axis. A red hatched zone below the average is labelled “not bought” on the left, with “a large drop often carries bad news” and “and is less likely to revert” beside it on the right. Last, a brown arrow rises from the dot to the right and ends inside the band, just under the dashed line and well under yesterday’s low, labelled “sell at the close 13.30”. The finished sketch holds for four seconds before it redraws.](../docs/figures/buy_on_gap_where_the_open_lands.gif)

*PCS on 2011-01-06, the only stock the reproduction bought that day, drawn to scale from Chan’s file. It opened more than one standard deviation of its daily returns, 0.020967, below the previous low and still above the 20-day average. So it qualified, and the reproduction bought it as the day’s only qualifier. It gained 2.2 percent by the close without getting back to that low.*

### Where the prices and the script come from

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_stocks_20120424.mat`, saved on 2012-04-25 and converted here to one file per stock. It holds the daily open, high, low and close of 497 stocks over 1,500 trading days, from 2006-05-11 to 2012-04-24. The date in its name is the last day of its prices, not the date of its list of stocks, which is from late 2011.

The script loads a file under a slightly different name, `inputDataOHLCDaily_20120424`, with no `_stocks`, so the name alone does not show that the script read Chan’s file. Of the public copies of Chan’s code that this repository has read, two hold Chan’s file.

1. Only one of them also holds a file under the name that `bog.m` loads, and that file has the same bytes as Chan’s file.
2. The other, `ivanliu1989/algorithmic_trading` at commit `45670240`, holds no file under that name, and it is the copy this repository transcribed `bog.m` from, line by line.

## Lesson 1: both figures bog.m prints reproduce on Chan’s own file

`bog.m`’s last print statement is followed by a comment that reads `APR=8.7%, Sharpe=1.5`. `bog.m`’s print statements would show more digits, but no record of what they printed exists. So the comment’s one decimal is all the precision the source gives. Here are the two figures `bog.m` prints, as this reproduction computes them, beside the comment and the book.

```math
\begin{array}{l|r|r}
 & \text{APR} & \text{Sharpe} \\ \hline
\text{Computed} & 0.087385 & 1.5371 \\
\texttt{bog.m}\text{'s comment} & 8.7\% & 1.5 \\
\text{Book} & \text{8.7 percent} & 1.5
\end{array}
```

Both printed figures match at the precision printed. The APR is compounded: it grows the daily returns into a total over all 1,500 days and annualizes it at 252 days a year. The Sharpe ratio subtracts no risk-free rate, the return cash would have earned over the same days.

The run also computes five figures that neither the comment nor the book prints.

```math
\begin{array}{l|r}
\text{Figure} & \text{Computed} \\ \hline
\text{Arithmetic annual return} & 0.085279 \\
\text{Maximum drawdown} & -0.052459 \\
\text{Longest drawdown, days} & 159 \\
\text{Positions taken} & 695 \\
\text{Days holding any} & 391
\end{array}
```

The arithmetic annual return, 252 times the average daily return, is the figure Lesson 3 needs. A drawdown is the fraction of its value the strategy has lost since its highest point so far, written here as a negative number. A drawdown’s length is the number of days the strategy stays below that high.

The rule is selective. Across the 1,500 days, the first two rules pass a stock 972 times, and 695 of those passes become purchases. The strategy holds at least one stock on 391 days, and buys the full ten stocks on only ten of them. No position can come before 2006-09-19, the first day a 90-day standard deviation exists, and the first position comes on 2006-09-22.

### The cumulative return of the strategy and its mirror

The figure below redraws what `bog.m` draws last, the cumulative return Chan prints as Figure 4.1. The figure’s lower panel draws the mirror Lesson 4 turns to. No check here compares the redraw with the chart the book prints, so it is a redraw of the script’s plot rather than a checked copy.

![Two line charts stacked on one shared scale, each showing a strategy’s compounded cumulative return over 1,500 trading days from May 2006 to April 2012, in percent of capital, unlevered and before costs. In both, a grey band covers the first 90 days, before the 90-day standard deviation exists, and the line is flat at zero there. The top panel labels the band as holding no position. The top panel, Figure 4.1, buy on gap, climbs steadily to a high marked on 2008-08-29, then sits below it inside a red band labelled 159 days below the high, from 2008-09-02 to 2009-04-20, with its deepest drawdown of −0.052459 marked on 2008-12-09, and then climbs on to the end. The bottom panel, the mirror as declared here, climbs more steeply through 2007 and 2008 to a high marked on 2008-11-21, then sits below it inside a much wider red band labelled 363 days below the high, from 2008-11-24 to 2010-05-05, with its deepest drawdown of −0.064928 marked on 2009-02-03, and ends above where the top panel ends. Each panel’s heading sets its APR and Sharpe ratio beside the book’s: 0.087385 and 1.5371 against 8.7 percent and 1.5 on top, and 0.122030 and 1.7853 against 46 percent and 1.27 below. The title calls the redraw exploratory, and the note names Chan’s file and says every stock in it is a survivor.](../docs/figures/buy_on_gap_cumulative_returns.png)

*The upper panel redraws `bog.m`’s cumulative return on Chan’s file. The lower panel, on the same scale, draws the declared mirror, the rule this repository wrote down before any run. The grey bands are the days before the 90-day standard deviation exists, and the red bands are each side’s longest drawdown, its longest run of days below an earlier high.*

## Lesson 2: the helper behind the 90-day standard deviation decides both printed figures

Rule 1’s 90-day standard deviation comes from a helper, a short function in Chan’s code. The helper is named `smartstd`, and it computes a standard deviation that tolerates missing values. Chan’s two books ship two different helpers under that name. The one from *Algorithmic Trading* skips a missing value and divides by n, the count of values left. The one from the first edition of *Quantitative Trading* counts a missing value as zero and divides by n − 1, where n counts every value.

[The post on post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md) teaches this on Example 7.2 of *Algorithmic Trading*, where the wrong helper moves one printed digit. Here it moves both printed figures. With the first edition’s helper behind the standard deviation, the APR becomes 0.083629 and the Sharpe ratio 1.6503. Those round to 8.4 percent and 1.7, against Chan’s 8.7 and 1.5, and the strategy takes 693 positions rather than 695.

This repository’s replications from the first edition of *Quantitative Trading* use the first edition’s helper, so a Python rewrite of the script could reach for it by mistake. A rewrite that used it would miss both of Chan’s figures, and the miss would look like a disagreement with his data when the helper caused it. Checking which helper ships with the script’s own book finds that cause. So does running both helpers and comparing each result with the book.

## Lesson 3: one phrase names two formulas

In a later chapter, on risk management, Chan returns to this strategy to try the VIX on it as a risk indicator, a reading meant to predict how risky the next day’s return will be. The VIX is an index of how far options traders expect the S&P 500 to move. He says the strategy “had an annualized average return of around 8.7 percent and a Sharpe ratio of 1.5” over the same dates (Chan, 2013, location 3509).

The phrase “annualized average return” has a history in this book. In Example 7.2, Chan reports an APR of 6.7 percent. He then levers that figure four times, as if trading four times the capital, and calls the result an “annualized average return” (Chan, 2013, location 3024). The [replication log’s Entry 12](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-12-post-earnings-drift-chans-algorithmic-trading), where this repository records each reproduction, found that the 6.7 percent is 252 times the average daily return, and not the compounded APR.

Read the same way here, the 8.7 percent at location 3509 would be the arithmetic annual return, 0.085279. At the book’s one decimal that is 8.5 percent, not 8.7. The 8.7 is the compounded APR from Lesson 1 under a second name. A check that trusted the label instead of reading the script would have compared Chan’s 8.7 percent with the wrong formula, and reported a miss when the transcription was correct.

The word “APR” does the same thing. [The post on cross-sectional momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md) shows that it names the arithmetic figure in Example 7.2 and the compounded one in Example 6.2. Within one book by one author, only the script says which formula produced a return.

## Lesson 4: a mirror written down before the run lands at 12 percent, not 46

Chan describes the mirror in one sentence. “Can we short stocks that gap up a standard deviation but are still lower than their 20-day moving average? Yes, we can” (Chan, 2013, location 1993). He gives an APR of 46 percent and a Sharpe ratio of 1.27, and says the mirror has the “steeper drawdown”. He prints no script.

A sentence leaves choices open, so a rule has to fill them before a run can test anything. This repository [wrote the rule down](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-18-buy-on-gap-and-its-mirror-chans-algorithmic-trading) before computing any figure for it. Wherever the sentence is silent, the rule takes `bog.m`’s choice and reverses its direction.

1. **The jump is measured from the previous day’s high**, mirroring the drop from the previous low. Two things in Chan’s code point that way.
   1. `bog.m` loads the daily highs and never reads them.
   2. Another of the book’s scripts, `gapFutures_FSTX.m`, measures a jump up from the previous high. Its return line, the line of code that computes each day’s return, pays out as if the script sold short at the open after that upward jump and bought back at the close. That is the mirror’s direction, as the [post on the opening gap strategy](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-1-the-script-trades-against-the-jump-the-text-says-it-follows) shows.
2. **The open must clear the previous high by more than one standard deviation and stay below the 20-day moving average.**
3. **The rule shorts the ten largest jumps**, and every other step follows `bog.m`.

Under that rule, the mirror lands at an APR of 0.122030 and a Sharpe ratio of 1.7853. That is 12 percent against Chan’s 46, and 1.79 against his 1.27. Across the 1,500 days, stocks qualify 1,308 times in all, and 725 of those are shorted.

One claim does reproduce. The mirror’s deepest drawdown is −0.064928 against the buy side’s −0.052459, so it is the steeper, as Chan says. Its longest drawdown runs 363 days against 159, which the lower panel of the figure shows.

### Why no second reading was tried

This repository named two other readings of Chan’s sentence in advance and ran neither.

1. A jump measured from the previous close.
2. Shorting the smallest qualifying jumps first.

Running them after the first reading missed would be a search for a match rather than a test. With enough readings tried, one could land near 46 percent by chance, and that landing would say nothing about what Chan ran.

## Lesson 5: Chan’s own two figures rule out the declared rule’s scale

Suppose Chan computed his two figures for the mirror with the formulas `bog.m` uses for its own. Then, taken together, those two figures require a strategy far more volatile than the declared rule, the one this repository wrote down in Lesson 4 before running it. Given that assumption, the rest is arithmetic.

Start from how `bog.m` computes the two figures. Over n days of returns rₜ, the APR is the compounded total annualized, and the Sharpe ratio S is √252 times the mean return over its standard deviation. The annual volatility σ is √252 times that standard deviation. Multiplied together, σ and S give 252 times the mean, because the standard deviation cancels. That product is the arithmetic annual return, so σ is the arithmetic annual return divided by S.

The link between the compounded APR and the arithmetic annual return is the natural logarithm, ln. Taking the log of one plus the APR turns the product of daily growth into a sum, so ln(1 + APR) is 252 / n times the sum of ln(1 + rₜ). Each term of that sum is at most rₜ, because ln(1 + r) ≤ r for every daily return. The rₜ themselves add up to n times the mean, so ln(1 + APR) ≤ 252 · mean. The arithmetic return is therefore at least the log of one plus the APR. Dividing by S, which is positive here, then gives a floor on the volatility.

```math
\sigma \ge \frac{\ln(1 + \text{APR})}{S}
```

With Chan’s 46 percent and 1.27, the floor is 0.2980. The declared rule has an annual volatility of 0.0657, so whatever rule Chan ran moved at least four and a half times as much.

That volatility is low because the declared rule is small in scale. It holds a position on 338 of the 1,500 days, shorts the full ten stocks on only 16 of them, and gives each position a tenth of the capital.

The floor rests on one assumption and has one limit.

1. **It assumes Chan computed both figures with `bog.m`’s formulas**, a compounded APR and a Sharpe ratio with no risk-free rate. Different formulas would move the floor.
2. **It cannot say where the difference lies.** Chan’s rule may have chosen other stocks, traded on more days or sized each position larger. Nothing here tests which.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

Every printed buy-side figure matches, which says the code, the data and the book agree. It says nothing about whether the strategy paid, for four reasons.

1. **Every stock is a survivor.** A company that was out of the S&P 500 for all of late 2011 is absent, whether it was acquired, shrank, failed or left for another reason. So the strategy could not have bought its panics. [The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches in full what a database of survivors does to a backtest. This repository has not yet rerun this strategy on the index as it stood each day. Chan’s Example 4.2 builds a second strategy from this same file, a basket of its stocks traded against SPY, the exchange-traded fund that tracks the S&P 500 (Chan, 2013, location 2035). [The post on Chan’s SPY index arbitrage](https://github.com/l3a0/quantitative-trading/blob/main/blog/index-arbitrage-lessons.md) runs into the same limit.
2. **`bog.m` charges no cost, and a trader cannot know the open in time.** Every position is a round trip inside one day. Chan names a cost of his own. A trader who picks the stocks from the official open price “can’t” then be filled at that same price, so has to pick them from preopen prices, the quotes before the market opens, instead. The stocks the preopen prices pick do not exactly match the ones the official open would pick, and Chan calls that difference “signal noise” (Chan, 2013, location 1988). The mirror also faces the short-sale constraint, the risk that a borrowed stock is recalled or that a rule bars selling it short, which he says it “suffered from” (Chan, 2013, location 1993).
3. **Chan traded another version.** He traded a version “quite profitably”, but it did not include rule 2, and it “suffered from diminishing returns from 2009 onward”. The backtest here says nothing about that version. He adds that so few stocks trade each day that the strategy “does not have a large capacity”, meaning it cannot take much capital before its own trades move the prices (Chan, 2013, location 1974).
4. **The rule was chosen on the same days it is tested on.** Reproducing Chan’s figures on his window tests his arithmetic, so the result is exploratory. A result that could confirm the edge would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Five questions are beyond it.

1. **Which rule Chan ran for the mirror.** This repository named two other readings of his sentence in advance and ran neither, for the reason Lesson 4 gives.
2. **Which file Chan ran in 2012.** Only one public copy of his code that this repository has read holds a file under the name that `bog.m` loads. That file has the same bytes as Chan’s file, whose contents this repository keeps. The match says what the name means in the code he published, not that it is the file he ran when he wrote the book. That both figures match is consistent with his having run that file, and does not prove it.
3. **How much costs and execution would take from the return.** Nothing here charges any, and nothing models the difference between the preopen price and the open.
4. **What the rule earned on the index as it stood each day.** Every stock here was in the S&P 500 in late 2011. Measuring it needs prices for every company in the index on each day, including those that left.
5. **Whether one flagged day’s price is correct.** A check this repository runs on other strategies flags Morgan Stanley’s rise from its close on 2008-10-10 to its close on 2008-10-13 as too large for an ordinary day, and the mirror shorted Morgan Stanley on 2008-10-13. The strategy’s run does not apply that check, because the job here is to reproduce what Chan’s script computed on the prices as they stand. Applied, the check would refuse the whole run, since the window from 2006 to 2012 crosses a day it flags. Nothing here checks that price against another source.

## What this means for a trader

One habit for each lesson.

1. **Reproduce the printed figures before arguing with them.** Both of Chan’s buy-side figures match on his file, so any disagreement with his result is about the data or the edge, not his arithmetic.
2. **Find out which version of a helper the author ran.** A helper’s name does not identify it, and here the wrong one moves both figures `bog.m` prints.
3. **Read the formula, not the label.** “APR” and “annualized average return” each name both a compounded and an arithmetic figure in this one book.
4. **Write a rule down before running it.** A strategy described in one sentence is many strategies, and trying them until one matches is a search, not a test.
5. **Test a published pair of figures against each other.** A compounded annual return and a positive Sharpe ratio with no risk-free rate together set a floor on annual volatility. A rule whose annual volatility falls below that floor cannot have produced both.
6. **Treat an exact reproduction as a check on arithmetic.** Whether buying a panic pays needs prices for the companies that left, a charge for costs and for trading on the preopen price, and a rule fixed in writing before it meets new data.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.1, 4.2, 6.2 and 7.2 and Kindle locations 1948, 1974, 1988, 1993, 2035, 3024 and 3509.
2. `bog.m`, at commit `45670240` of ivanliu1989/algorithmic_trading, a public copy of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/buy_on_gap.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/buy_on_gap_figures.py) and [the whiteboard sketch](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/buy_on_gap_whiteboard.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_buy_on_gap.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_buy_on_gap_figures.py) and [what the sketch draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_buy_on_gap_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-18-buy-on-gap-and-its-mirror-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
