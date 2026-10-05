# Chan’s Conditional Parameter Optimization does not reproduce, and the cell it starts from trades 47 times a day

*A method can be tested where its model cannot be had. Here the test fails, and the selection underneath it picks turnover before it picks anything else.*

## Why test the method Chan added to the revised edition

The revised edition of Ernest Chan’s *Quantitative Trading* adds a method the first edition does not have. Traders usually fit a strategy’s parameters once on a stretch of history, or re-fit them on a moving window, and Chan argues that both react too slowly. Re-fitting on a window that moves one day at a time changes the parameters very little, because one day changes the history very little. His method, Conditional Parameter Optimization, trains a model to predict the strategy’s own next-day return from the parameters and the day’s market conditions. After each close the model scores every parameter set, and the strategy trades the best one the next day. That lets traders change parameters “as frequently as they like” (Chan, 2021, location 3414).

Example 7.1 tests the method on a strategy that trades gold. Chan reports that holding the parameters fixed on the three test years earned a Sharpe ratio of 1.947, and that re-choosing them daily earned 2.325, with “all other metrics” improved (Chan, 2021, p. 145). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk.

This repository ran the example on one-minute bars and found the following.

1. **Neither of Chan’s columns reproduces.** Holding the parameters fixed earns a Sharpe ratio of 5.700 on the test years, against his 1.947.
2. **His claim fails.** Re-choosing the parameters daily beats holding them on one metric of the four he prints, and loses on the other three.
3. **His own printed figures cannot all be right.** His annual returns do not compound to his cumulative ones.

Every result here is **exploratory**. A replication spends its data on a rule someone else chose, so it can say whether Chan’s figures and claim reproduce on these bars and nothing about whether the method works. The readings the run follows were written down before any return on the minute bars was computed. That makes them declared, not registered. A registered result commits its own hypothesis in writing before the number is seen, and the hypothesis here is Chan’s. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

This is the first post here whose figures a reader cannot re-run from a clone. The minute bars are licensed for personal use, so the repository keeps their hashes and not the bars. The figures come in four kinds.

1. **Checked on every clone.** Chan’s own arithmetic in Lesson 2, the 34 early closes and the fix in Lesson 3, and the grid and rules below need no bars.
2. **Checked where the owner’s archive is.** Every computed figure from the run. Their hashes in `data/archive_vintages.jsonl` say which bytes were read, though a reader cannot read the bytes themselves.
3. **Checked at an earlier commit.** The first run’s figures in Lesson 3, whose tests were replaced when the run was corrected.
4. **Not checked at all.** Chan’s words, a third party’s figures and the references.

## The strategy, the grid and the bars

The strategy is a mean-reversion trade on a spread between two gold funds, traded in only one of them. Readers who know this pair from its daily cointegration test will find [that post](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md) useful background. This one works on minutes rather than days.

1. **The spread.** GLD holds gold, and GDX holds gold-mining stocks. The spread is GLD’s close less a weight times GDX’s (Chan, 2021, p. 137).
2. **The signal.** Each minute, the spread’s **z-score** measures how far it sits from its exponential moving average, in units of its exponential moving standard deviation. Both use a smoothing factor of 2 divided by a lookback in minutes.
3. **The rules.** Buy GLD when the z-score falls below minus the entry threshold, and short it when the z-score rises above the threshold. Exit at −0.6 times the entry threshold. Only GLD is traded. The strategy trades from 09:30 to 15:59 and liquidates at the close, and a day’s return is the sum of its round trips, since the strategy “may execute multiple round trips per day” (Chan, 2021, p. 140).
4. **The grid.** The strategy has three parameters: the weight, the entry threshold and the lookback. Five weights, from 2 to 4, ten entry thresholds, from 0.2 to 2.5, and eight lookbacks, from 30 to 720 minutes, give 400 combinations (p. 137). This post calls each combination a **cell** and writes it as Chan’s p. 145 output writes it: weight, lookback in minutes and entry threshold, joined by underscores. So `2_30_0.2` is a weight of 2, a lookback of 30 minutes and an entry threshold of 0.2. The printed entry grid has eleven tokens for a stated ten, ending “1.5, 2, 2, 5”, and the run reads the last three as 2 and 2.5.
5. **The two arms.** Chan calls them unconditional and conditional, and this post calls them fixed and re-chosen. The fixed arm holds the cell with the highest compounded return on the training years. The re-chosen arm asks a model each evening for the cell with the highest predicted return the next day, and trades that cell (p. 140).
6. **The model.** Chan uses PredictNow’s service, which he describes as “random forest with boosting” (p. 142). That model and its settings are not available, so this repository uses scikit-learn’s `HistGradientBoostingRegressor` with default settings, on 101 features where the book names 115. The features are the three parameters and seven named indicators of each fund at seven lookbacks. The book’s eighth indicator is unnamed.
7. **The bars.** Alpha Vantage one-minute bars as traded, not adjusted, GLD downloaded on 2026-07-17 and GDX on 2026-10-03. They are kept in the owner’s archive and verified against their hashes before parsing. Chan’s stated start of January 1, 2006 cannot hold for the pair, because GDX did not trade until 2006-05-22. From then to 2020-12-31 there are 3,680 days on which both funds traded. The first 80% train the selection, and the test starts on 2018-01-31 with 736 days.

The book leaves the bar grid, the order of the rules, the definition of annual return, how a minute’s indicators become a day’s features, the model and the costs unstated. All 19 readings that fill those gaps were written down before any return on the minute bars was computed. [Entry 16 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-16-conditional-parameter-optimization-chans-quantitative-trading) lists them, and records each figure below beside the assertion that computes it.

## Lesson 1: neither column reproduces, and re-choosing daily wins on one metric of four

A method’s claim can be tested even where its digits cannot. Chan’s claim is that re-choosing beats holding on every metric. That claim can be checked with any reasonable model, because it compares two arms of one run. His digits for the re-chosen arm rest on a model nobody outside PredictNow can run. So this repository’s re-chosen column reproduces his only in kind, and its four figures stand beside his rather than reproduce them.

```math
\begin{array}{l|r|r|r|r}
\text{Metric} & \text{Fixed, computed} & \text{Fixed, book} & \text{Re-chosen, computed} & \text{Re-chosen, book} \\ \hline
\text{Cumulative return} & 3.40 & 73\% & 3.12 & 83\% \\
\text{Annual return} & 0.6612 & 17.29\% & 0.6234 & 19.77\% \\
\text{Sharpe ratio} & 5.700 & 1.947 & 5.274 & 2.325 \\
\text{Calmar ratio} & 15.249 & 0.984 & 18.637 & 1.454
\end{array}
```

Each computed figure is quoted at the precision Chan printed it. The cumulative return is the growth of one dollar over the 736 test days less the dollar, so 3.40 is 340%. The annual return compounds it to a year of 252 trading days. The Calmar ratio divides the annual return by the deepest fall of compounded wealth from a high.

Three things follow from the table.

1. **The fixed column overshoots by a wide margin.** The gaps between computed and printed figures are +2.67, +0.4883, +3.753 and +14.265. As multiples of Chan’s figures, that is about 4.7 times on cumulative return, 3.8 times on annual return, 2.9 times on the Sharpe ratio and 15.5 times on the Calmar ratio. None of the four is near.
2. **The claim fails.** Re-choosing beats holding on the Calmar ratio, 18.637 against 15.249. It loses on the Sharpe ratio, on cumulative return and on annual return.
3. **The two arms are close because the model mostly agrees with the fixed choice.** On 557 of the 736 test days, the model picked the same cell the training years chose. Over the test it used 44 different cells and switched 254 times. This count was added after the result was seen. It decides nothing, but it explains why the two columns sit near each other.

The model is a stand-in. A better model could win where this one did not, which is the first thing this replication cannot say.

## Lesson 2: the book’s own figures cannot all be right

Before checking a source’s figures against a run, check them against each other. That check needs no data, so a reader can run it on a clone without the archive.

Chan prints an annual return and a cumulative return for each arm over the same three test years. If the annual return compounds, three years of it should give the cumulative return. They do not.

1. **The fixed arm.** 17.29% a year compounds to 61.4% over three years, not the printed 73%.
2. **The re-chosen arm.** 19.77% a year compounds to 71.8%, not the printed 83%.

The other common definition of an annual return is arithmetic: 252 times the average daily return, with no compounding. A figure defined that way need not compound to the cumulative return, so it might seem to explain the mismatch. It does not bring this run near Chan’s figures. Computed that way, the annual return is 0.5121 for the fixed arm and 0.4892 for the re-chosen one, lower than the compounded figures and still far above his. Under neither definition do his annual and cumulative returns both reproduce.

[The buy-on-gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) found that one phrase names two formulas in *Algorithmic Trading*, and that the script settles which formula produced a figure. What is new here is that neither formula fits, and no script was published to settle it.

## Lesson 3: the first run broke a declared reading, and both runs are reported

When a run turns out not to follow its own declared reading, the remedy is to fix the code to the reading, rerun, and publish both runs. Changing the reading to fit the result would turn the run into a search for a reading that passes.

1. **What broke.** The New York Stock Exchange closes at 13:00 on some days, such as the day after Thanksgiving. From 2006 to 2020 there were 34 of them. One declared reading says the run reads the regular session only. The first run kept the bars from 13:00 to 15:59 on those days, which are extended-hours trading, against that reading. A review of the first run found it.
2. **What the fix did.** It ended those days at 12:59, the last regular-session minute, which is what the reading said all along. The reading itself did not change.
3. **What moved and what did not.** In the first run, re-choosing won on the Sharpe and Calmar ratios. In the corrected run it wins on the Calmar ratio alone. So 34 days of 3,680 moved which metrics the re-chosen arm won. The claim needs all four, and it failed in both runs.

Both runs sit side by side below. The corrected columns are the ones Lesson 1 quotes.

```math
\begin{array}{l|r|r|r|r}
\text{Metric} & \text{Fixed, first run} & \text{Fixed, corrected} & \text{Re-chosen, first run} & \text{Re-chosen, corrected} \\ \hline
\text{Cumulative return} & 3.55 & 3.40 & 3.48 & 3.12 \\
\text{Annual return} & 0.6798 & 0.6612 & 0.6710 & 0.6234 \\
\text{Sharpe ratio} & 5.791 & 5.700 & 5.916 & 5.274 \\
\text{Calmar ratio} & 15.676 & 15.249 & 16.604 & 18.637
\end{array}
```

[The calendar-spreads post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#lesson-2-the-simulated-contracts-have-to-move-together-like-real-ones) also reports two runs, for a different reason. There, review showed that the declared reading was wrong, so the reading was corrected after the result was seen, and the correction moved a verdict. Here the reading stood and the code was wrong, and no verdict moved.

## Lesson 4: the selection picks a cell that trades 47 times a day

A selection rule with no cost in it chooses the cell that trades most profitably before costs. When a strategy earns less on each trade than a trade costs, it loses money however good its Sharpe ratio looks before costs.

1. **The chosen cell.** Maximising the compounded return on the training years picks `2_30_0.2`: the smallest weight, the shortest lookback and the lowest entry threshold on the grid. On the test days it trades 46.7 round trips a day, and the re-chosen arm trades 42.1. Chan says only that the strategy may make multiple round trips a day (p. 140).
2. **What a basis point does.** A basis point is a hundredth of a percent. At a cost of 1 basis point a round trip, the cost the declared readings name, the fixed arm’s Sharpe ratio becomes −7.614 and its cumulative return −0.858. The re-chosen arm’s become −6.122 and −0.814. Both arms lose most of their capital over three years.
3. **Why.** Before costs, the fixed arm earns 0.435 basis points a round trip, the sum of its test-day returns over the sum of its round trips. The re-chosen arm earns 0.462. A cost of 1 basis point is larger than either, so each trade costs more than it earns on average. This edge per trade was measured after the result was seen. [The survivorship and transaction costs post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md#lesson-1-on-the-sp-500-a-days-cost-is-larger-than-a-days-profit) shows the same arithmetic on a daily reversal strategy.
4. **Where Chan’s 1.947 sits.** Across the 400 cells, the test Sharpe ratios run from 0.807 to 5.891, with a median of 3.506. Only 39 cells sit below 1.947. The nearest is `3_60_2.5`, at 1.931, and it trades 1.19 round trips a day. Turnover and Sharpe ratio rise together: the rank correlation between the cells’ round trips a day and their test Sharpe ratios is 0.95. These figures were added after the result was seen, to say where Chan’s number would have to come from. They decide nothing.
5. **A hypothesis, labelled as one.** Chan’s figures may carry a cost, or something that acts like one. A cost charged during his own optimisation, a fill one bar later, or a coarser bar would each move the choice toward cells that trade less, and the cells that trade less sit where his 1.947 does. That is a hypothesis about the gap, and nothing here tests it. None of the three was declared before the run, so none was tried. Trying costs and fill delays until one matched would be a search across readings, which is what declaring the readings first exists to prevent.
6. **A third party found the same overshoot.** A public reproduction in the jeffmcphail/mctheory-praxis repository, at commit `b7c5b5d`, ran the example on Kibot bars from 2009. It reported a test Sharpe ratio of 5.974 for its fixed arm at 50.1 round trips a day, and a gross edge of 0.425 basis points a round trip. These are their figures from their files, which this repository cannot check. Both runs land on a high-turnover cell, and both overshoot Chan’s 1.947 by a wide margin, 2.9 times here. They differ on where 1.947 sits. They found it near their lowest cell, while here 39 cells sit below it.

The figure below draws those 400 cells.

![A scatter plot of 400 points, one per cell of the parameter grid. The horizontal axis is round trips a day on the test days, on a log scale from under one to about fifty. The vertical axis is the test Sharpe ratio before costs. The points rise from lower left to upper right: cells that trade about once a day sit between roughly 1 and 3, and cells that trade forty or more times a day sit between roughly 4.5 and 6. A dashed brass horizontal line marks Chan’s Sharpe ratio of 1.947, near the bottom of the cloud. Three points are labelled. 2.5_30_0.2, the highest test Sharpe ratio, sits at the upper right at 5.891. 2_30_0.2, chosen on the train years, sits just below it at 46.7 round trips a day and 5.700. 3_60_2.5, the nearest to Chan’s 1.947, sits at the lower left at 1.19 round trips a day and 1.931. The title calls the figure exploratory and says it was added after the result was seen, and the note says nothing is charged for costs and names both vintages by hash.](../docs/figures/cpo_cells.png)

*Each point is one of the 400 cells on the test days, before costs. The selection lands at the upper right, and Chan’s 1.947 sits among the cells that trade about once a day.*

## What this replication cannot say

Every result above is exploratory. A run that spends its data on a rule Chan chose can say whether his figures reproduce and nothing about whether the method works. Five questions are beyond it.

1. **Whether Conditional Parameter Optimization works.** The model here is not PredictNow’s. Its features lack the book’s unnamed eighth indicator, and they are read at the day’s last bar rather than summarised over the day. The `ta` library’s average true range and average directional index also return 0 rather than nothing before their windows fill, so the earliest rows carry zeros the model cannot tell from readings. A better model could win where this one did not.
2. **What would reproduce Chan’s numbers.** Lesson 4 places his Sharpe ratio among cells that trade far less, and shows the chosen cell losing once trading costs something. Searching costs and fill delays until one matched is the search the declared readings forbid, so it was not run.
3. **Whether the strategy pays.** At 1 basis point a round trip both arms lose heavily. What a round trip in GLD actually costs, with its spread and its fees, is not measured here.
4. **Anything a public clone can check.** The bars are licensed, so the checks on the run’s figures run only where the owner’s archive is. The hashes say exactly which bytes were read, and nothing here can show those bytes to anyone else.
5. **Whether predicting a strategy’s return is less crowded than predicting gold’s.** Chan argues that everyone tries to predict GLD’s return, “but nobody (until they read this book!) is predicting the returns of this particular GLD trading strategy” (Chan, 2021, location 3617). Nothing here tests that.

## What this means for a trader

One habit from each lesson.

1. **Test the claim where the digits cannot be had.** A proprietary model blocks a reproduction of its numbers, and it does not block a test of the claim that one arm beats another. Run both arms with the best model available, and report the comparison.
2. **Check a source’s figures against each other first.** An annual return that does not compound to its own cumulative return is a defect found before any data is read.
3. **Fix the code to the reading, and publish both runs.** A run that breaks its own declared reading is fixed by making it follow the reading. Rewording the reading to fit the result is how a backtest drifts toward the answer it wants.
4. **Put the cost into the selection, or price it straight after.** A rule that maximises return before costs will choose the cell that trades most. Divide each arm’s return by its trades and set the result beside a realistic cost before reading any Sharpe ratio.

On these bars, Chan’s method does not beat holding the parameters fixed, his fixed column overshoots by a multiple, and the strategy under both loses money at a basis point a trade. All of it is exploratory.

## References

1. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Example 7.1 at pp. 137 to 146, with pages 137, 140, 142 and 145 quoted, and Kindle locations 3414 and 3617. The pages were read in the Kindle Cloud Reader on 2026-10-03, which labels each screen with the print page it opens on. Location 3414 falls before the example and 3617 after it, outside the pages that reading covered, so those two are cited by location from [the committed notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md).
2. Chan, E. P. (2021, April). [Conditional Parameter Optimization](http://epchan.blogspot.com/2021/04/conditional-parameter-optimization.html), on his blog. It prints the same three pairs of annual return, Sharpe ratio and Calmar ratio as the book, and states no window, grid or costs.
3. jeffmcphail/mctheory-praxis at commit `b7c5b5d`, a third-party reproduction on Kibot bars, cited for its own figures.
4. Alpha Vantage, `TIME_SERIES_INTRADAY` at one-minute intervals and `adjusted=false`, the source of the bars. Their hashes are in [data/archive_vintages.jsonl](https://github.com/l3a0/quantitative-trading/blob/main/data/archive_vintages.jsonl).

*Not investment advice. Code: [the strategy, the selection and the model](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cpo.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cpo_figures.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cpo.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cpo_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-16-conditional-parameter-optimization-chans-quantitative-trading) that records each verdict.*
