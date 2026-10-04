# Chan’s buy on gap reproduces on his own file, and its mirror does not

*Reproducing a strategy on its author’s own file checks the figures he printed. A rule he only described has to be written down before it can be checked at all.*

## Why reproduce a strategy that buys a panic

Ernest Chan’s second book, *Algorithmic Trading*, has a strategy in its chapter on mean reversion in stocks that buys a morning panic. On a day when index futures are down before the open, he argues, some stocks open far below where they traded the day before, because of “panic selling at the open”. Once the selling is over, the stock “will gradually appreciate over the course of the day” (Chan, 2013, location 1948). So the strategy buys those stocks at the open and sells them at the same day’s close.

He reports that on the S&P 500 from May 2006 to April 2012, the strategy earned an annual percentage rate, or APR, of 8.7 percent, with a Sharpe ratio of 1.5 (Chan, 2013, location 1974). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk. He also reports the mirror image, which shorts stocks that open far above the day before, at 46 percent and 1.27 (Chan, 2013, location 1993).

Chan published the script for the first strategy and the data file it reads, so a reader can check whether his figures follow from them before arguing about the strategy. This repository keeps a copy of the file and ran the script on it. He published no script for the mirror, so this repository wrote a rule down from his one sentence about it before running anything.

Both figures Chan prints for the first strategy match. The computed APR is 0.087385, the book’s 8.7 percent, and the computed Sharpe ratio is 1.5371, the book’s 1.5. The mirror does not match. The rule written down here lands at 12 percent and 1.79.

Two labels apply to every figure below.

1. **Every result is exploratory.** Chan chose the rule and its settings, and the reproduction tests them on the same days he did. It can say whether his numbers follow from his file and nothing about whether the rule pays.
2. **Every figure is about survivors.** The file holds the S&P 500 as Chan held it on 2012-04-24, carried backwards. A company that left the index before then is not in it, and Chan says the universe “has survivorship bias” (Chan, 2013, location 1974).

The six lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The strategy and the file

Chan states four rules (Chan, 2013, location 1948).

1. **The drop.** Select the stocks whose return from the previous day’s low to today’s open is “lower than one standard deviation”, which `bog.m` reads as a drop of more than one standard deviation. The standard deviation is that of the stock’s close-to-close returns over the last 90 days. These are the stocks that gapped down. In this post, gap means only that move to the open.
2. **The filter.** Keep only the stocks whose open is still above the 20-day moving average of their closes.
3. **The selection.** Buy the ten with the deepest drops, or all of them if fewer than ten qualify.
4. **The exit.** Sell everything at the close.

The script, `bog.m`, adds a fifth rule about sizing. It sums each day’s returns across the stocks it bought and divides by 10, whatever the day’s count. So a day with three stocks holds three tenths of the capital and leaves the rest idle.

Chan gives a reason for rule 2. He calls it “a momentum filter superimposed on a mean-reverting strategy”. A stock that dropped “just a little” is more likely to recover than one that dropped “a lot”, because a large drop often carries bad news, and a drop caused by news is less likely to revert (Chan, 2013, location 1948).

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_stocks_20120424.mat`, saved on 2012-04-25 and converted here to one file per stock. It holds the daily open, high, low and close of 497 stocks over 1,500 trading days, from 2006-05-11 to 2012-04-24. The script loads it under a slightly different name, `inputDataOHLCDaily_20120424`, with no `_stocks`. Two public copies of Chan’s code exist on GitHub, and the only file of that name in either holds the same bytes as Chan’s file. This repository transcribed `bog.m` line by line from one of those copies, `ivanliu1989/algorithmic_trading` at commit `45670240`.

## Lesson 1: both figures bog.m prints reproduce on Chan’s own file

`bog.m` closes on a comment that reads `APR=8.7%, Sharpe=1.5`. Its print statements would show more digits, but nothing records what they printed, so the comment’s one decimal is the precision the source carries. Here is each figure, computed, beside the comment and the book.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \texttt{bog.m}\text{'s comment} & \text{Book} \\ \hline
\text{APR} & 0.087385 & 8.7\% & \text{8.7 percent} \\
\text{Sharpe ratio} & 1.5371 & 1.5 & 1.5 \\
\text{Arithmetic annual return} & 0.085279 & \text{none} & \text{none} \\
\text{Maximum drawdown} & -0.052459 & \text{none} & \text{none} \\
\text{Longest drawdown, days} & 159 & \text{none} & \text{none} \\
\text{Positions taken} & 695 & \text{none} & \text{none} \\
\text{Days holding any} & 391 & \text{none} & \text{none}
\end{array}
```

Both printed figures match at the precision printed. The APR is compounded: it grows the daily returns into a total over all 1,500 days and annualizes it at 252 days a year. The Sharpe ratio subtracts no risk-free rate. The arithmetic annual return, 252 times the average daily return, is the figure Lesson 3 needs.

The rule is selective. Across the 1,500 days, a stock passes the first two rules 972 times and is bought 695 times. Only ten days buy the full ten stocks. No position can come before 2006-09-19, the first day a 90-day standard deviation exists, and the first comes on 2006-09-22.

The figure below redraws what `bog.m` draws last, the cumulative return Chan prints as Figure 4.1. Its lower panel is the mirror Lesson 4 turns to. Nothing compares the redraw with the chart the book prints, so it is a redraw of the script’s plot rather than a checked copy.

![Two line charts stacked on one shared scale, each showing a strategy’s compounded cumulative return over 1,500 trading days from May 2006 to April 2012, in percent of capital, unlevered and before costs. In both, a grey band covers the first 90 days, before the 90-day standard deviation exists, and the line is flat at zero there. The top panel labels the band as holding no position. The top panel, Figure 4.1, buy on gap, climbs steadily to a high marked on 2008-08-29, then sits below it inside a red band labelled 159 days below the high, from 2008-09-02 to 2009-04-20, with its deepest drawdown of −0.052459 marked on 2008-12-09, and then climbs on to the end. The bottom panel, the mirror as declared here, climbs more steeply through 2007 and 2008 to a high marked on 2008-11-21, then sits below it inside a much wider red band labelled 363 days below the high, from 2008-11-24 to 2010-05-05, with its deepest drawdown of −0.064928 marked on 2009-02-03, and ends above where the top panel ends. Each panel’s heading sets its APR and Sharpe ratio beside the book’s: 0.087385 and 1.5371 against 8.7 percent and 1.5 on top, and 0.122030 and 1.7853 against 46 percent and 1.27 below. The title calls the redraw exploratory, and the note names Chan’s file and says every stock in it is a survivor.](../docs/figures/buy_on_gap_cumulative_returns.png)

*`bog.m`’s cumulative return redrawn on Chan’s file, above, and the declared mirror, below, on the same scale. The grey bands are the days before the 90-day standard deviation exists, and the red bands are each side’s longest spell below a high.*

## Lesson 2: the helper behind the 90-day standard deviation decides both printed figures

The 90-day standard deviation in rule 1 is computed by a helper named `smartstd`, a standard deviation that tolerates missing values. Chan’s two books ship two different helpers under that name. The one from *Algorithmic Trading* skips a missing value and divides by n. The one from the first edition of *Quantitative Trading* counts a missing value as zero and divides by n − 1.

[The post on post-earnings drift](https://github.com/l3a0/quantitative-trading/blob/main/blog/post-earnings-drift-lessons.md) teaches this on Example 7.2 from the same book, where the wrong helper moves one printed digit. Here it moves both printed figures. With the first edition’s helper behind the standard deviation, the APR becomes 0.083629 and the Sharpe ratio 1.6503. Those round to 8.4 percent and 1.7, against Chan’s 8.7 and 1.5, and the strategy takes 693 positions rather than 695.

The first edition’s helper ran this repository’s earlier replications from Chan’s first book, so it was the one a Python rewrite of the script would reach for first. A rewrite that used it would miss both of Chan’s figures and look like a disagreement with his data. The cause is the helper. Checking which helper the script’s own book ships finds it, and so does running both and comparing each with the book.

## Lesson 3: one phrase names two formulas

In a later chapter, on risk management, Chan returns to this strategy as an example of a risk indicator, and says it “had an annualized average return of around 8.7 percent and a Sharpe ratio of 1.5” over the same dates (Chan, 2013, location 3509).

That phrase has a history in this book. In Example 7.2, Chan calls 252 times the average daily return an APR, and then calls the same figure levered four times an “annualized average return” (Chan, 2013, location 3024). The [replication log’s Entry 12](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-12-post-earnings-drift-chans-algorithmic-trading) found that his 6.7 percent there is that arithmetic figure, and not the compounded one.

Read the same way here, location 3509’s 8.7 percent would be the arithmetic annual return, 0.085279. At the book’s one decimal that is 8.5 percent, not 8.7. The 8.7 is the compounded APR from Lesson 1 under a second name. A check that read the label rather than the script would have set Chan’s figure against the wrong formula and reported a miss on a correct transcription.

The word “APR” does the same thing. [Entry 17 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-17-cross-sectional-momentum-chans-algorithmic-trading) found that it names the arithmetic figure in Example 7.2 and the compounded one in Example 6.2. Within one book by one author, only the script says which formula produced a return.

## Lesson 4: a mirror written down before the run lands at 12 percent, not 46

Chan describes the mirror in one sentence. “Can we short stocks that gap up a standard deviation but are still lower than their 20-day moving average? Yes, we can” (Chan, 2013, location 1993). He gives an APR of 46 percent and a Sharpe ratio of 1.27, and says the mirror has the “steeper drawdown”. He prints no script.

A sentence leaves choices open, so a rule has to fill them before a run can test anything. This repository [wrote the rule down](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-18-buy-on-gap-and-its-mirror-chans-algorithmic-trading) before computing any figure for it, taking `bog.m`’s choice reversed wherever the sentence is silent.

1. **The jump is measured from the previous day’s high**, mirroring the drop from the previous low. Two things in Chan’s code point that way.
   1. `bog.m` loads the daily highs and never reads them.
   2. Another of the book’s scripts, `gapFutures_FSTX.m`, measures a jump up from the previous high.
2. **The open must clear the previous high by more than one standard deviation and stay below the 20-day average.**
3. **The ten largest jumps are shorted**, and everything else is `bog.m`.

Under that rule, the mirror lands at an APR of 0.122030 and a Sharpe ratio of 1.7853. That is 12 percent against Chan’s 46, and 1.79 against his 1.27. Across the 1,500 days, a stock qualifies 1,308 times and is shorted 725 times.

One claim does reproduce. The mirror’s deepest drawdown is −0.064928 against the buy side’s −0.052459, so it is the steeper, as Chan says. Its longest spell below a high runs 363 days against 159, which the lower panel of the figure shows.

This repository named two other readings of Chan’s sentence beside this one, and ran neither.

1. A jump measured from the previous close.
2. Shorting the smallest qualifying jumps first.

Running them after the first one missed would be a search. Try enough readings and one could land near 46 percent by chance, and the landing would say nothing about what Chan ran.

## Lesson 5: Chan’s own two figures rule out the declared rule’s scale

If Chan computed his two figures for the mirror the way `bog.m` computes its own, then taken together they need a strategy far more volatile than the declared rule. Given that assumption, the rest is arithmetic.

Start from how `bog.m` computes the two figures. Over n days of returns rₜ, the APR is the compounded total annualized, and the Sharpe ratio S is √252 times the mean return over its standard deviation. The annual volatility σ is √252 times that standard deviation, which makes it the arithmetic annual return divided by S.

The link between the two returns is that ln(1 + r) ≤ r for every daily return. Summing over the days and annualizing gives ln(1 + APR) ≤ 252 · mean, so the arithmetic return is at least the log of one plus the APR. Dividing by S then gives a floor on the volatility.

```math
\sigma \ge \frac{\ln(1 + \text{APR})}{S}
```

With Chan’s 46 percent and 1.27, the floor is 0.2980. The declared rule has an annual volatility of 0.0657, so whatever rule Chan ran moved at least four and a half times as much.

The declared rule is small in scale. It holds a position on 338 of the 1,500 days, shorts the full ten stocks on only 16 of them, and gives each position a tenth of the capital.

The floor rests on one assumption and has one limit.

1. **It assumes Chan computed both figures with `bog.m`’s formulas**, a compounded APR and a Sharpe ratio with no risk-free rate. Different formulas would move the floor.
2. **It cannot say where the difference lies.** Chan’s rule may have chosen other stocks, traded on more days or sized each position larger. Nothing here tests which.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

That every printed buy-side figure matches says the code, the data and the book agree. It says nothing about whether the strategy paid, for four reasons.

1. **Every stock is a survivor.** A company that left the S&P 500 between 2006 and 2012, because it was acquired, shrank or failed, is absent, and the strategy could not have bought its panics. [The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches in full what a database of survivors does to a backtest. This repository has not yet rerun this strategy on the index as it stood each day.
2. **No cost is charged, and the open cannot be known in time.** `bog.m` charges nothing, and every position is a round trip inside one day. Chan names a cost of his own. A trader deciding on the open “can’t” be filled at that same official open, and has to decide on preopen prices instead, which he calls “signal noise” (Chan, 2013, location 1988). The mirror also faces the short-sale constraint, which he says it “suffered from” (Chan, 2013, location 1993).
3. **Chan’s own trading was of another version.** He traded a version “quite profitably”, but it did not include rule 2, and it “suffered from diminishing returns from 2009 onward”. The backtest here says nothing about that version. He adds that so few stocks trade each day that the strategy “does not have a large capacity” (Chan, 2013, location 1974).
4. **The rule was chosen on the same days it is tested on.** Reproducing Chan’s figures on his window tests his arithmetic, so the result is exploratory. A result that could confirm the edge would need a rule fixed in writing first and data the rule had never seen.

## What this replication cannot say

Five questions are beyond it.

1. **Which rule Chan ran for the mirror.** This repository named two other readings of his sentence in advance and ran neither, for the reason Lesson 4 gives.
2. **Which file Chan ran in 2012.** The name `bog.m` loads points, in both public copies of his code, at the same bytes as the committed file. That says what the name means in the code he published, not that it is the file he ran when he wrote the book. That both figures match is consistent with it and does not prove it.
3. **What costs and execution would take.** Nothing here charges any, and nothing models the difference between the preopen price and the open.
4. **What the rule earned on the index as it stood each day.** Every stock here was in the S&P 500 on 2012-04-24. Measuring it needs prices for the companies that left.
5. **Whether one flagged day was a clean print.** A check this repository runs on other strategies flags Morgan Stanley’s move into 2008-10-13 as too large for an ordinary day, and the mirror shorted Morgan Stanley that day. This repository does not run the check here, because the job is to reproduce what Chan’s script computed on the prices as they stand. Nothing here checks that print against another source.

## What this means for a trader

One habit for each lesson.

1. **Reproduce the printed figures before arguing with them.** Both of Chan’s buy-side figures match on his file, so any disagreement with his result is about the data or the edge, not his arithmetic.
2. **Find out which version of a helper the author ran.** A helper’s name does not identify it, and here the wrong one moves every printed figure.
3. **Read the formula, not the label.** “APR” and “annualized average return” each name both a compounded and an arithmetic figure in this one book.
4. **Write a rule down before running it.** A strategy described in one sentence is many strategies, and trying them until one matches is a search, not a test.
5. **Test a published pair of figures against each other.** A return and a Sharpe ratio together imply a floor on volatility, and a floor can rule out a reading without running it.
6. **Treat an exact reproduction as a check on arithmetic.** Whether buying a panic pays needs prices for the companies that left, a charge for costs and for trading on the preopen price, and a rule fixed in writing before it meets new data.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 4.1 and Kindle locations 1948, 1974, 1988, 1993, 3024 and 3509.
2. `bog.m`, at commit `45670240` of ivanliu1989/algorithmic_trading, a public copy of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/buy_on_gap.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/buy_on_gap_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_buy_on_gap.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_buy_on_gap_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-18-buy-on-gap-and-its-mirror-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
