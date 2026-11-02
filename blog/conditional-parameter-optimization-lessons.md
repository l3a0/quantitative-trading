# Chan’s Conditional Parameter Optimization does not reproduce, and the cell it selects makes 47 round trips a day

*A method can be tested where its model cannot be had. Here the test fails with a stand-in model and its random seed fixed in advance, and the selection underneath it lands on one of the busiest cells on the grid.*

## Why test the method Chan added to the revised edition

The revised edition of Ernest Chan’s *Quantitative Trading* adds a method the first edition does not have. Traders usually fit a strategy’s parameters once on a stretch of history, or re-fit them on a moving window, and Chan argues that both react too slowly. Re-fitting on a window that moves one day at a time changes the parameters very little, because one day changes the history very little. His method, Conditional Parameter Optimization, trains a model to predict the strategy’s own next-day return from the parameters and the day’s market conditions. After each close the model scores every parameter set, and the strategy trades the best one the next day. That lets traders change parameters “as frequently as they like” (Chan, 2021, Kindle edition, p. 138).

Example 7.1 tests the method on a strategy that trades gold. Chan reports that holding the parameters fixed on the three test years earned a Sharpe ratio of 1.947, and that re-choosing them daily earned 2.325, with “all other metrics” improved (Chan, 2021, p. 146). The Sharpe ratio divides the average daily return by its standard deviation and scales the result to a year, so it measures return per unit of risk.

### What the replication found

This repository ran the example on one-minute bars and checked Chan’s printed figures against each other. Four findings came of it.

1. **Neither of Chan’s two sets of figures reproduces.** Holding the parameters fixed earns a Sharpe ratio of 5.700 on the test years before trading costs, against his 1.947.
2. **His claim that re-choosing beats holding on every metric fails, with a stand-in for the book’s model and the stand-in’s seed fixed in advance.** A seed is a number that sets the model’s random choices. With that seed, re-choosing the parameters daily wins on one metric of the four he prints, and loses on the other three. Refit with each of ten seeds after the result was seen, the model makes re-choosing win on all four for two of them, and the claim fails for the other eight.
3. **His own printed figures cannot all be right.** His annual returns do not compound to his cumulative ones.
4. **The parameters chosen on the training years make 46.7 round trips a day on the test days, and a cost of 1 basis point a round trip turns that into a loss.** A round trip is one entry and the exit that closes it, and a basis point is a hundredth of a percent. At 1 basis point a round trip, a cost written down before the run, both versions of the strategy lose most of their capital over the test years.

Every result here is **exploratory**: it can kill an idea or justify a closer look, and it cannot confirm one. A replication tests a hypothesis someone else chose, so it can say whether Chan’s figures and claim reproduce on these bars, and nothing about whether the method works. A result confirms something only when its own hypothesis was written down before any number was seen, and the hypothesis here is Chan’s.

Where the book leaves a choice open, the run follows a written interpretation, called a reading here. Every reading was written down before any return on the minute bars was computed, so none was chosen to fit the result. A reading settles how to run the test and states no hypothesis, so the result stays exploratory. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

### Which figures are checked, and where

The figures computed from the minute bars cannot be re-run from a copy of the repository. The minute bars are licensed for personal use, so the repository keeps a fingerprint of each file, called a hash, and not the bars themselves, which stay in its owner’s archive. A hash identifies the exact bytes read without revealing them. The figures come in four kinds, by whether and where the repository’s tests check them.

1. **Checked in every copy of the repository.** Chan’s own arithmetic in Lesson 2, the count of early-closing days and the fix in Lesson 3, and the grid and rules below need no bars. The early-closing dates were copied from a software calendar of the New York Stock Exchange’s published schedule, and a copy of the repository checks how many there are, not which days.
2. **Checked where the archive is.** Every computed figure from the run is checked there. The hashes in `data/archive_vintages.jsonl` say which files were read, though a reader cannot read the files themselves.
3. **Checked by an earlier version of the code.** The figures of the first run in Lesson 3 were checked by tests that a later fix replaced.
4. **Not checked at all.** Chan’s words and printed results, a third party’s figures, a few facts about the market, and the references are cited rather than computed.

## The strategy, the grid and the bars

The strategy is a mean-reversion trade on a spread between two gold funds, traded in only one of them. Readers who know this pair from its daily cointegration test will find [that post](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md) useful background. This one works on minutes rather than days.

1. **The spread.** GLD holds gold, and GDX holds gold-mining stocks. The spread is GLD’s close less a weight times GDX’s (Chan, 2021, p. 140).
2. **The signal.** Each minute, the spread’s **z-score** measures how far it sits from its recent average, in units of its recent standard deviation. Both are exponentially weighted, so recent minutes count more than older ones. The lookback, a number of minutes, sets how fast older minutes fade: each new minute’s share of the average is 2 divided by the lookback, so a longer lookback averages over more history.
3. **The rules.** Buy GLD when the z-score falls below minus the entry threshold, and short it when the z-score rises above the threshold. Exit a long when the z-score rises back above −0.6 times the entry threshold, and exit a short when it falls back below 0.6 times the threshold. The strategy trades in the regular session, 09:30 to 15:59 New York time, and liquidates at the session’s last close, 16:00 on most days, as Chan says (pp. 140 to 141), from the last trade before the closing auction. A day’s return is the sum of its **round trips**, since the strategy “may execute multiple round trips per day” (Chan, 2021, p. 141).
4. **The grid.** The strategy has three parameters: the weight, the lookback and the entry threshold. The book’s grid has five weights from 2 to 4, eight lookbacks from 30 to 720 minutes, and ten entry thresholds from 0.2 to 2.5, so 5 × 8 × 10 = 400 combinations (p. 140). This post calls each combination a **cell** and labels it the way Chan’s output on p. 145 does, with the three numbers in that order joined by underscores. So `2_30_0.2` is a weight of 2, a lookback of 30 minutes and an entry threshold of 0.2. The book’s list of entry thresholds prints eleven numbers where it states ten, ending “1.5, 2, 2, 5”, and the run reads the final “2, 5” as 2.5.
5. **The two arms.** The run trades the strategy two ways, called arms here. Chan calls them unconditional and conditional, and this post calls them fixed and re-chosen. The fixed arm holds the cell with the highest compounded return on the training years, the first 80% of the days. The re-chosen arm asks a model each evening for the cell with the highest predicted return the next day, and trades that cell (pp. 140 to 141).
6. **The model.** Chan uses PredictNow’s commercial service, which he describes as “random forest with boosting” (p. 142). The book’s code reaches that model through predictnow.ai, and the book says it will not run without a trial account there. The book prints the few options that code sets, and not the model’s hyperparameters, the settings that decide how it fits. Without those settings, this repository uses a gradient-boosted tree model from the scikit-learn library, `HistGradientBoostingRegressor`, with default settings.
7. **The features.** The model’s inputs, called features, are the three parameters and seven named technical indicators for each fund, each computed over seven windows, the same seven for every indicator and separate from the strategy’s lookback. That makes 3 + 7 × 2 × 7 = 101 features. The book counts 115 from eight indicators, and it names only seven.
8. **The bars.** Alpha Vantage supplies the bars, one per minute, not adjusted for splits or dividends. GLD was downloaded on 2026-07-17 and GDX on 2026-10-03. Both downloads include extended-hours bars, and the run keeps only the regular session. The downloaded files are kept in the owner’s archive and checked against their hashes before the run reads them. Chan’s stated start of January 1, 2006 (p. 140) cannot hold for the pair, because GDX did not trade until 2006-05-22. From then to 2020-12-31 there are 3,680 days on which both funds traded. The test is the last 736 of those days, from 2018-01-31 to 2020-12-31.

![A whiteboard sketch titled “The entry and exit rule”, drawn slowly stroke by stroke, which holds its finished drawing for twelve seconds. It is schematic and carries no figures from the run. A grey line labelled “0” crosses the board, then dashed black lines labelled “+entry” and “−entry”, then dashed brass lines labelled “+0.6 × entry” and “−0.6 × entry” between them and 0. A black path labelled “z-score” falls below −entry, climbs past +entry and settles between 0 and +0.6 times the entry. Under it a strip starts “flat” and is labelled “position”. Four dots follow, each dropping a grey dashed guide to the strip before its label appears. A green dot where the path falls below −entry is labelled “buy GLD”, and the strip turns “long”. A brass dot where the path rises back above −0.6 times the entry is labelled “exit long”, and the strip turns “flat”. A red dot where the path rises above +entry is labelled “short GLD”, and the strip turns “short”. A brass dot where the path falls back below +0.6 times the entry is labelled “exit short”, and the strip turns “flat”. A brass line at the top reads “each exit comes before the z-score reaches 0”, and a grey line under the title reads “lowest entry 0.2: lines at ±0.2, ±0.12”.](../docs/figures/cpo_sketch_rule.gif)

*A schematic of the rule rather than the run: each position opens past an entry line and, unless the session ends first, closes at the brass line on its own side, before the z-score gets back to 0.*

The book does not say how to line up the two funds’ bars within its stated hours and dates, or how a minute’s indicators become a day’s features. It also does not say whether an exit and an entry can both fire on the same minute, flipping a long to a short or a short to a long, and it does not state the definition of annual return, the model’s settings or the costs. [Entry 16 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-16-conditional-parameter-optimization-chans-quantitative-trading) summarises the 19 readings that fill those gaps and links to all of them, and records each of the corrected run’s figures beside the test that checks it.

## Lesson 1: Chan’s figures do not reproduce, and with the seed fixed in advance, re-choosing wins on one metric of four

A method’s claim can be tested even where its published figures cannot be reproduced. Chan’s claim is that re-choosing beats holding on every metric. Running the method with a different model tests whether that claim survives a change of model, a weaker question than whether it holds with Chan’s own. His figures for the re-chosen arm rest on PredictNow’s model, whose hyperparameters the book does not print. So this repository’s figures for the re-chosen arm reproduce his only in kind: they come from the same method with a different model, and stand beside his for comparison.

```math
\begin{array}{l|r|r}
\text{Fixed arm} & \text{Computed} & \text{Book} \\ \hline
\text{Cumulative return} & 340\% & 73\% \\
\text{Annual return} & 66.12\% & 17.29\% \\
\text{Sharpe ratio} & 5.700 & 1.947 \\
\text{Calmar ratio} & 15.249 & 0.984
\end{array}
```

```math
\begin{array}{l|r|r}
\text{Re-chosen arm} & \text{Computed} & \text{Book} \\ \hline
\text{Cumulative return} & 312\% & 83\% \\
\text{Annual return} & 62.34\% & 19.77\% \\
\text{Sharpe ratio} & 5.274 & 2.325 \\
\text{Calmar ratio} & 18.637 & 1.454
\end{array}
```

Each computed figure is before trading costs and quoted at the precision Chan printed it. The cumulative return is what one dollar grows to over the 736 test days, minus that starting dollar. The annual return compounds it to a year of 252 trading days. The Calmar ratio divides the annual return by the deepest fall of compounded wealth from a high.

Three things follow from the tables.

1. **The fixed arm’s computed figures overshoot Chan’s on every metric.** The gaps between computed and printed figures are +267 and +48.83 percentage points on the two returns, and +3.753 and +14.265 on the two ratios. As multiples of Chan’s figures, that is about 4.7 times on cumulative return, 3.8 times on annual return, 2.9 times on the Sharpe ratio and 15.5 times on the Calmar ratio.
2. **The claim fails with the seed fixed in advance.** Re-choosing beats holding on the Calmar ratio, 18.637 against 15.249. It loses on the Sharpe ratio, on cumulative return and on annual return. The model’s seed picks which tenth of its training data it holds back to judge its own fit. The seed also picks the sample of that data that sets the bins, the ranges the model sorts each feature’s values into. So each seed fits a different model. The run fixed seed 0 before it started. A check added after the result was seen, which plays no part in any verdict, refit the model with each of seeds 0 to 9. Across the ten, re-choosing beats the fixed arm on the Calmar ratio for six seeds, on the Sharpe ratio for three and on each return for two. With two of those ten seeds, re-choosing wins on all four metrics. The re-chosen arm’s Sharpe ratio runs from 5.166 to 6.353 across all ten seeds, a range the fixed arm’s 5.700 lies inside.
3. **The two arms differ less than their names suggest.** With the seed fixed in advance, on 557 of the 736 test days the model picked the same cell the fixed arm holds. Over the test it used 44 different cells and switched 254 times. These counts were added after the result was seen, so they describe the run and play no part in any verdict.

The model is a stand-in, so the claim fails here only for this model with the seed fixed in advance. That limit heads the list of what this replication cannot say.

## Lesson 2: the book’s own figures cannot all be right

Before checking a source’s figures against a run, check them against each other. That check needs no data, so a reader can run it on a copy of the repository without the archive.

Chan prints an annual return and a cumulative return for each arm over the same three test years. If the annual return compounds, three years of it should give the cumulative return. They do not.

1. **The fixed arm.** 17.29% a year compounds to 61.4% over three years, not the printed 73%.
2. **The re-chosen arm.** 19.77% a year compounds to 71.8%, not the printed 83%.

The other common definition of an annual return is arithmetic: 252 times the average daily return, with no compounding. That definition does not explain the mismatch either. A day multiplies wealth by one plus its return, and one plus a return is never more than e raised to that return. So three years of daily returns can compound to no more than e raised to their sum. At an arithmetic 17.29% a year, the daily returns average 0.1729 ÷ 252, so three years of them sum to 3 × 0.1729, and the cap is a cumulative return of 68.0%, still short of 73%. The re-chosen arm’s 19.77% caps at 81.0%, short of 83%. So Chan’s two figures disagree under either definition, whatever his daily returns were.

![A whiteboard sketch titled “Fixed arm at 17.29% a year”, drawn slowly stroke by stroke, which holds its finished drawing for twelve seconds. Every height is drawn to one scale of a dollar’s growth. A black staircase starts at “$1” and steps up at the end of each year, marked “year 1”, “year 2” and “year 3”, to a top step labelled “61.4%: 17.29% compounded”. A dashed brass ceiling above it is labelled “at most 68.0%: 17.29% arithmetic”, the most three years of daily returns averaging an arithmetic 17.29% a year can compound to. A red mark above both is labelled “73% printed”, the book’s cumulative return, and a red bracket from the ceiling up to the mark is labelled “68.0% still short of 73%”. A grey note reads “re-chosen arm, 19.77% a year:”, “71.8% compounded, at most 81.0% arithmetic,” and “83% printed”.](../docs/figures/cpo_sketch_annual_returns.gif)

*Read either way, Chan’s 17.29% a year cannot reach his printed 73% in three years.*

This run misses his annual figure under both definitions too. Computed arithmetically, its annual return is 51.21% for the fixed arm and 48.92% for the re-chosen one, lower than the compounded figures and still far above his.

[The buy-on-gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) found that in Chan’s other book, *Algorithmic Trading*, one phrase names two formulas, and that only the script published with that example says which one produced a figure. Here neither formula fits, so knowing which one Chan used would not make his figures agree.

## Lesson 3: the first run broke one of its readings, and this post reports both runs

When a run turns out not to follow its own reading, the remedy is to fix the code to the reading, rerun, and publish both runs. Changing the reading to fit the result would turn the run into a search for a reading that passes.

1. **What broke.** The New York Stock Exchange closes at 13:00 on some days, such as the day after Thanksgiving. From 2006 to 2020 there were 34 of them. One reading says the run uses regular-session bars only. On those days the first run kept the bars from 13:00 to 15:59. The 13:00 bar still trades at regular-session volume, likely the closing auction, and the bars after it are extended-hours trading. The reading excludes all of them. A review of the first run found the error.
2. **What the fix did.** It ended those days at 12:59, the last regular-session minute, which is what the reading said all along. The reading itself did not change.
3. **What moved and what did not.** In the first run, re-choosing won on the Sharpe and Calmar ratios. In the corrected run it wins on the Calmar ratio alone. So 34 days of 3,680 moved which metrics the re-chosen arm won. The claim needs all four, and it failed in both runs.

Both runs sit side by side below, one table for each arm. The corrected columns are the ones Lesson 1 quotes.

```math
\begin{array}{l|r|r}
\text{Fixed arm} & \text{First run} & \text{Corrected} \\ \hline
\text{Cumulative return} & 355\% & 340\% \\
\text{Annual return} & 67.98\% & 66.12\% \\
\text{Sharpe ratio} & 5.791 & 5.700 \\
\text{Calmar ratio} & 15.676 & 15.249
\end{array}
```

```math
\begin{array}{l|r|r}
\text{Re-chosen arm} & \text{First run} & \text{Corrected} \\ \hline
\text{Cumulative return} & 348\% & 312\% \\
\text{Annual return} & 67.10\% & 62.34\% \\
\text{Sharpe ratio} & 5.916 & 5.274 \\
\text{Calmar ratio} & 16.604 & 18.637
\end{array}
```

[The calendar-spreads post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#lesson-2-the-simulated-contracts-have-to-move-together-like-real-ones) also reports two runs, for a different reason. There, review showed that the reading was wrong, so the reading was corrected after the result was seen, and the correction moved a verdict. Here the reading stood and the code was wrong. No verdict moved: Chan’s figures and his claim fail in both runs, though the re-chosen arm’s win on the Sharpe ratio in the first run became a loss.

## Lesson 4: the selection picks a cell that makes 47 round trips a day, because its rule charges nothing for trading

A selection rule with no cost in it rewards whatever earns most before costs, and here that is trading often. When a strategy earns less on each round trip than a round trip costs, it loses money however good its Sharpe ratio looks before costs.

1. **The chosen cell.** Maximising the compounded return on the training years picks `2_30_0.2`: the smallest weight, the shortest lookback and the lowest entry threshold on the grid. On the test days it trades 46.7 round trips a day, the second most of the 400 cells, a ranking added after the result was seen. Chan says only that the strategy may make multiple round trips a day (p. 141). The re-chosen arm trades 42.1, and its figures in this lesson come from the seed fixed in advance.
2. **What a basis point does.** At a cost of 1 basis point a round trip, the cost the readings name, the fixed arm’s Sharpe ratio becomes −7.614 and its cumulative return −85.8%. The re-chosen arm’s become −6.122 and −81.4%. Both arms lose most of their capital over three years.
3. **Why.** Before costs, the fixed arm earns 0.435 basis points a round trip: its test-day returns added up and divided by the number of round trips it made. The re-chosen arm earns 0.462. A cost of 1 basis point is larger than either, so each round trip costs more than it earns on average. This return per round trip was measured after the result was seen. [The survivorship and transaction costs post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md#lesson-1-on-the-sp-500-a-days-cost-is-larger-than-a-days-profit) shows the same arithmetic on a daily reversal strategy.

### Where Chan’s 1.947 sits on the grid

1. **The cells near 1.947.** Across the 400 cells, the test Sharpe ratios run from 0.807 to 5.891, with a median of 3.506. Only 39 cells sit below 1.947. The nearest is `3_60_2.5`, at 1.931, and it trades 1.19 round trips a day. Before costs, cells that trade more tend to earn higher Sharpe ratios. Ranked by round trips a day and by test Sharpe ratio, the 400 cells come out in nearly the same order: Spearman’s rank correlation, which is 1 when two rankings agree exactly and 0 when they are unrelated, is 0.95. These figures were added after the result was seen, to say where Chan’s number would have to come from. They play no part in any verdict.
2. **A hypothesis, labelled as one.** Chan’s figures may carry a cost, or something that acts like one. A cost charged during his own optimisation would move the choice toward cells that trade less. So would trading at the next minute’s price rather than the signal minute’s, and so would bars longer than a minute. The cells that trade less sit where his 1.947 does. Nothing here tests this hypothesis. None of these three was written down before the run, so none was tried. Trying costs, delays and bar lengths until one matched would be a search across readings, which is what writing the readings down first exists to prevent.
3. **A third party found the same overshoot.** A public reproduction in the jeffmcphail/mctheory-praxis repository, at commit `b7c5b5d`, ran the example on Kibot bars from 2009. It reported a test Sharpe ratio of 5.974 for its fixed arm at 50.1 round trips a day, and a return before costs of 0.425 basis points a round trip. These are their figures, read in their files at that commit. This repository cannot rerun their backtest, because it does not hold their Kibot bars. Both runs land on a cell that trades often, and both overshoot Chan’s 1.947, by 2.9 times here. The two runs differ on where 1.947 sits. The third party found it near its lowest cell, while here 39 cells sit below it.

The figure below draws those 400 cells.

![A scatter plot of 400 points, one per cell of the parameter grid. The horizontal axis is round trips a day on the test days, on a log scale from under one to about fifty. The vertical axis is the test Sharpe ratio before costs. The points rise from lower left to upper right: cells that trade about once a day sit low, and cells that trade forty or more times a day sit near the top. A dashed brass horizontal line marks Chan’s Sharpe ratio of 1.947, near the bottom of the cloud. Three points are labelled. 2.5_30_0.2, the highest test Sharpe ratio, sits at the upper right at 5.891. 2_30_0.2, chosen on the training years, sits just below it at 46.7 round trips a day and 5.700. 3_60_2.5, the nearest to Chan’s 1.947, sits at the lower left at 1.19 round trips a day and 1.931. The title calls the figure exploratory and says it was added after the result was seen, and the note says nothing is charged for costs and names each file by the start of its hash.](../docs/figures/cpo_cells.png)

*Each point is one of the 400 cells on the test days, before costs. The selection lands at the upper right, and the cell nearest Chan’s 1.947 trades 1.19 round trips a day.*

## What this replication cannot say

Every result above is exploratory, for the reason the opening gives. Five questions are beyond it.

1. **Whether Conditional Parameter Optimization works.** The model here is not PredictNow’s. Its features lack the book’s unnamed eighth indicator, and they are read at the day’s last bar rather than summarised over the day. The technical-indicator library `ta` also returns 0 rather than a missing value for its average true range and average directional index before their windows fill, so the earliest rows carry zeros the model cannot tell from real values. A better model could win where this one did not. Even this model’s verdict depends on its seed. Of ten seeds tried after the result was seen, two make re-choosing win on all four metrics.
2. **What would reproduce Chan’s numbers.** Lesson 4 places his Sharpe ratio among cells that trade far less, and shows the chosen cell losing once trading costs something. Searching costs, delays and bar lengths until one matched is the search that writing the readings down first rules out, so it was not run.
3. **Whether the strategy pays.** At 1 basis point a round trip both arms lose heavily. What a round trip in GLD actually costs, with its spread and its fees, is not measured here.
4. **Whether a copy of the repository can check the run’s figures.** The bars are licensed, so the checks on the run’s figures run only where the owner’s archive is. The hashes say exactly which bytes were read, and nothing here can show those bytes to anyone else.
5. **Whether predicting a strategy’s return is less crowded than predicting gold’s.** Chan argues that everyone tries to predict GLD’s return, “but nobody (until they read this book!) is predicting the returns of this particular GLD trading strategy” (Chan, 2021, p. 146). Nothing here tests that.

## What this means for a trader

One habit from each lesson.

1. **Test the claim where the figures cannot be reproduced.** A proprietary model blocks a reproduction of its numbers, and it does not block a test of the claim that one arm beats another. Run both arms with more than one model, or more than one seed of one, and report the comparison.
2. **Check a source’s figures against each other first.** An annual return that does not compound to its own cumulative return is a defect found before any data is read.
3. **Fix the code to the reading, and publish both runs.** A run that breaks its own reading is fixed by making it follow the reading. Rewording the reading to fit the result is how a backtest drifts toward the answer it wants.
4. **Put the cost into the selection, or price it straight after.** A rule that maximises return before costs favours cells that trade often, and here it chose one of the two busiest on the grid, a ranking made after the result was seen. Divide each arm’s return by its round trips and set the result beside a realistic cost before reading any Sharpe ratio.

On these bars, with a stand-in for the book’s model and the stand-in’s seed fixed in advance, re-choosing the parameters daily wins on one metric of four, so Chan’s claim that it wins on all four fails. Refit with seeds 0 to 9 after the result was seen, the model makes re-choosing win on all four metrics for two of them, and the claim fails for the other eight. This run’s fixed arm overshoots Chan’s figures by a multiple, and the strategy under both arms loses money at a basis point a round trip. All of it is exploratory.

## References

1. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Example 7.1 and the passage before it that introduces the method, at pp. 138 to 146, with pages 138, 140 to 142 and 145 to 146 cited. The page numbers are the Kindle edition’s, read in the Kindle Cloud Reader, and match the print edition’s.
2. Chan, E. P. (2021, April). A post on Conditional Parameter Optimization on his blog, at [epchan.blogspot.com](http://epchan.blogspot.com/2021/04/conditional-parameter-optimization.html). It prints the same annual return, Sharpe ratio and Calmar ratio for each of the two arms as the book, and states no window, grid or costs.
3. jeffmcphail/mctheory-praxis at commit `b7c5b5d`, a third-party reproduction on Kibot bars, cited for its own figures.
4. Alpha Vantage, `TIME_SERIES_INTRADAY` at one-minute intervals with extended hours and no adjustment, requested one month at a time, the source of the bars. [data/archive_vintages.jsonl](https://github.com/l3a0/quantitative-trading/blob/main/data/archive_vintages.jsonl) records each file’s vendor call, download date and hash.

*Not investment advice. Code: [the strategy, the selection and the model](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cpo.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cpo_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/cpo_whiteboard.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cpo.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cpo_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_cpo_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record each quoted passage at its Kindle location, except p. 146’s “all other metrics”, and [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-16-conditional-parameter-optimization-chans-quantitative-trading) that records each verdict.*
