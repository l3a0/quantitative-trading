# Chan’s VIX filter reproduces on his own files, and a test cannot tell the days it keeps from the rest

*Chan backtests two gap rules on the days after VIX closed above 35. Buy on gap’s return rises to 17.2 percent and FSTX’s falls to 2.6. Both reproduce on his files, but a test cannot tell the kept days from the rest, and one day earns most of the 17.2.*

## Why filter a strategy on the VIX

A risk indicator is a number read before a trade that is meant to say how risky the next day will be. If one worked, a trader could stand aside on the days it flags. Ernest Chan’s *Algorithmic Trading* argues that no single one serves every strategy: “There is no one risk indicator that is applicable to all strategies: What is a risky period to one strategy may be a highly profitable period for another” (Chan, 2013, location 3509).

He makes the case with the **VIX**, an index the Chicago Board Options Exchange computes from the prices of options on the S&P 500. It measures the swings those options imply for the next month, so it rises when traders expect turmoil. Chan keeps only the days after VIX closed above 35, “a common threshold for highly risky periods” (location 3509), and reruns two rules the book already ran.

1. **Buy on gap**, Example 4.1, which buys stocks that opened far below the previous day’s low and sells them at the close. On every day, Chan reports “an annualized average return of around 8.7 percent and a Sharpe ratio of 1.5” (location 3509). On the kept days he reports 17.2 percent and 1.4, and concludes that “this strategy benefits from the so-called risk!” (location 3509).
2. **The opening gap rule on FSTX**, Example 7.1, a STOXX Europe 50 index future. On every day, Chan reports “around 13 percent and a Sharpe ratio of 1.4” (location 3509). On the kept days the return drops to “2.6 percent and the Sharpe ratio to 0.16” (location 3509). He concludes that “VIX tells us to avoid trading on the following day” (location 3509).

This repository ran both rules unchanged on Chan’s own files and applied the filter. The results fall into five lessons.

1. **The filtered figure is 252 times the mean, and the unfiltered one beside it is compounded.** Buy on gap gives 0.171924 and a Sharpe ratio of 1.417425 on 190 kept days, which print as 17.2 percent and 1.4. The 8.7 percent Chan sets beside it is a different formula.
2. **FSTX’s filtered figures belong to the script’s fading sign.** Chan’s script for Example 7.1 computes its return with the sign that trades against the jump at the open. His text describes following the jump, which this post calls momentum. Under the script’s sign the figures are 0.025730 and 0.164869 on 185 kept days, and momentum gives them negated.
3. **The 2.6 percent depends on which VIX close each FSTX day reads, and a search chose the join.** The replication tried six ways of reading VIX on FSTX’s days, and only one, which this post calls the join, lands both printed figures.
4. **The kept days are few, and most fall in 2008 and 2009.** Buy on gap held a position on 20 of its 190 kept days, and one of those days earned most of its return.
5. **A test cannot tell the kept days from the rest.** For either rule, the mean return on kept days differs from the other days’ by less than chance alone would often produce.

**Every result here is exploratory.** Three reasons make it so.

1. Chan chose the rules, the threshold and the windows, so reproducing his figures spends the sample on his choices.
2. The replication chose the join after seeing its figures, as Lesson 3 says.
3. Every kept day falls from 2008 to 2011, so the sample holds few separate episodes of high VIX.

So the run can say whether his numbers follow from his files, and nothing about whether VIX above 35 guards either rule today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The filter, the two rules and the files

**The filter.** A day is kept when VIX’s close on the previous day was strictly above 35. VIX closes at 16:15 New York time, so the previous day’s close is known before either rule trades. No close in the file sits exactly on 35, the nearest being 35.02 and 34.95, so whether the test is strict decides no day here.

**The two rules.** The [buy on gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#the-strategy-and-the-file) sets out Example 4.1’s four rules and the file of 497 stocks it reads. The [opening gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#the-rule-and-the-file) sets out Example 7.1’s rule on FSTX, and its [Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-1-the-script-trades-against-the-jump-the-text-says-it-follows) shows that the script’s return line fades the jump at the open, while the text describes following it. Both rules run here exactly as those posts ran them. The filter only chooses which of their days count.

**The files.** Three of Chan’s saved files, each recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md).

1. **VIX** from Chan’s `VIX.csv`, saved 2012-05-09, 5,635 closes from 1990-01-02 to 2012-05-08.
2. **The stocks** from Chan’s `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, 1,500 days from 2006-05-11 to 2012-04-24. Every stock was in the S&P 500 on the last day, so every figure on them is about survivors.
3. **FSTX** from Chan’s `inputDataOHLCDaily_20120517.mat`, saved 2012-05-18, 2,000 days from 2004-07-16 to 2012-05-17.

**The join.** Each rule runs on its own full calendar first. The join then keeps each rule’s daily returns on the days that rule’s calendar shares with VIX’s, and the filter reads the previous shared day. Buy on gap keeps all 1,500 of its days, because the stocks traded on exactly VIX’s days. FSTX keeps 1,945 of its 2,000. It loses the 7 days after VIX’s last close and 48 days on which Eurex, the European exchange FSTX trades on, was open and the US exchanges were not.

**No script ships for location 3509.** Neither of the two public copies of Chan’s code on GitHub, ivanliu1989/algorithmic_trading and ericnberwick/EpchanPreview, holds a file that applies the filter. So this replication inferred the specification above from Chan’s four filtered figures, 17.2 percent and 1.4 for buy on gap, and 2.6 percent and 0.16 for FSTX, rather than reading it from code. The [replication log’s Entry 47](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-47-the-vix-filter-on-buy-on-gap-and-the-stoxx-europe-50-gap-rule-chans-algorithmic-trading) records every reading the replication tried and sets each figure beside the test that computes it.

## Lesson 1: the filtered figure is 252 times the mean, and the unfiltered one beside it is compounded

Chan calls both of buy on gap’s returns an “annualized average return” (location 3509). Two formulas could sit behind that phrase.

1. **The arithmetic figure**, 252 times the mean daily return. It scales an average day to a year of 252 trading days.
2. **The compounded APR**, short for annual percentage rate. It is the yearly rate that, compounded, turns one dollar into what the daily returns multiply out to.

On the kept days the arithmetic figure lands Chan’s number and the compounded one misses.

```math
\begin{array}{l|r|r|r}
\text{Reading} & \text{Days} & \text{Computed} & \text{Book} \\ \hline
\text{252 times the mean, kept days} & 190 & 0.171924 & 17.2 \text{ percent} \\
\text{Sharpe ratio, kept days} & 190 & 1.417425 & 1.4 \\
\text{Compounded APR, kept days} & 190 & 0.179297 & \text{prints as } 17.9 \\
\text{252 times the mean, other days zeroed} & 1{,}500 & 0.021777 & \text{prints as } 2.2 \\
\text{252 times the mean, every day} & 1{,}500 & 0.085279 & \text{none} \\
\text{Sharpe ratio, every day} & 1{,}500 & 1.537063 & 1.5
\end{array}
```

The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate. A third reading sets the other days to zero and averages over all 1,500, as if the trader held cash on them. It gives 0.021777 and a Sharpe ratio of 0.503869, far from both printed figures, so the average runs over the kept days alone.

The 8.7 percent Chan sets beside the 17.2 is the other formula. The [buy on gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) shows that it is the compounded APR over every day, and that 252 times the mean over every day is 0.085279, which prints as 8.5 percent. So in two consecutive sentences the same phrase names the compounded figure for every day and the arithmetic one for the kept days.

The comparison Chan draws survives the mismatch here. Like for like, 252 times the mean rises from 0.085279 on every day to 0.171924 on the kept days. The Sharpe ratio moves the other way, from 1.537063 to 1.417425, so the kept days earned more per day and swung more for it. Lesson 5 asks whether either difference is larger than chance.

## Lesson 2: FSTX’s figures belong to the script’s fading sign

The [opening gap post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-1-the-script-trades-against-the-jump-the-text-says-it-follows) found that the script’s return line pays a long when the price falls from the open, so it trades against the jump. The text describes the opposite, “buying when the instrument gaps up, and shorting when it gaps down” (location 2965), and the [same post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-3-the-momentum-the-book-describes-loses-what-the-script-earns) shows that sign losing what the script earns. This post calls the script’s sign the fade, which the opening gap post calls the literal reading, and the text’s sign momentum.

The filtered figures follow the fade.

```math
\begin{array}{l|r|r|r}
\text{Reading} & \text{Days} & \text{252 times the mean} & \text{Sharpe ratio} \\ \hline
\text{Fade, kept days} & 185 & 0.025730 & 0.164869 \\
\text{Momentum, kept days} & 185 & -0.025730 & -0.164869 \\
\text{Book, kept days} & & 2.6 \text{ percent} & 0.16 \\ \hline
\text{Fade, every joined day} & 1{,}945 & 0.139950 & 1.589197 \\
\text{Fade, every day of Example 7.1} & 2{,}000 & 0.128622 & 1.441620 \\
\text{Book, every day} & & \text{around } 13 \text{ percent} & 1.4
\end{array}
```

The fade’s 0.025730 and 0.164869 print as the book’s 2.6 percent and 0.16. Momentum’s returns are the fade’s negated day for day, so it misses both, landing 5.2 percentage points and 0.32 below them.

The two signs read the filter in opposite directions. Under the fade, 252 times the mean falls from 0.139950 on every joined day to 0.025730 on the kept days, which is what Chan reports. Under momentum it rises from −0.139950 to −0.025730, so for the sign the text describes, the kept days are the less bad ones. The script’s figures lean the way “VIX tells us to avoid trading” (location 3509) says, and the figures for the rule the text describes lean the opposite way. Lesson 5 tests whether either lean is larger than chance.

The book’s before and after for FSTX also come from different calendars. Its “around 13 percent and a Sharpe ratio of 1.4” (location 3509) is Example 7.1 on all 2,000 days, 0.128622 and 1.441620. On the 1,945 days joined to VIX, the same figures are 0.139950 and 1.589197, which print as 14 percent and 1.6. The filtered 2.6 percent is taken from the joined days, so the comparison the sentence draws mixes two calendars.

## Lesson 3: the 2.6 percent depends on which VIX close each FSTX day reads, and a search chose the join

FSTX trades on Eurex and the Chicago Board Options Exchange computes VIX, so the two calendars disagree on US and European holidays. Reading “the preceding day’s VIX” (location 3509) on FSTX’s days needs a choice for those days, and the sentence makes none. The replication tried six readings, saw their figures, and kept the one that lands both.

```math
\begin{array}{l|r|r|r}
\text{Which VIX close each FSTX day reads} & \text{Days} & \text{252 times the mean} & \text{Sharpe ratio} \\ \hline
\text{Join on shared days, previous shared day} & 185 & 0.025730 & 0.164869 \\
\text{Latest VIX close before each day} & 188 & 0.025319 & 0.163555 \\
\text{VIX filled forward, one row back} & 188 & 0.025319 & 0.163555 \\
\text{One row back on FSTX's own calendar} & 185 & 0.045238 & 0.291589 \\
\text{Same day, missing on US holidays} & 185 & -0.047063 & -0.297416 \\
\text{Same day, filled forward} & 188 & -0.046312 & -0.295046
\end{array}
```

The join lands 2.6 percent and 0.16. The latest close before each day lands the Sharpe ratio and prints the return as 2.5 percent. It keeps three days the join drops, 2008-11-27, 2009-01-19 and 2009-02-16, US holidays on which Eurex traded, and each reads the close before the holiday. Filling VIX forward onto FSTX’s calendar keeps the same 188 days. Reading one row back on FSTX’s own calendar keeps those three holidays and drops the day after each, which reads the holiday’s missing close, and it lands neither figure. The last two read VIX on the trade’s own date. VIX closes hours after FSTX opens, so they look ahead, which rules them out whatever their figures.

Three facts bound what the search means.

1. **Buy on gap does not move.** Every reading that takes the previous day gives it the same 190 days and the same figures, because its calendar is VIX’s. The search moved only FSTX.
2. **Filtering before or after the rule cannot be told apart.** Running FSTX’s rule on the 1,945 joined days instead of its own 2,000 changes the return on 11 joined days and on none of the 185 kept days. So the figures cannot say which order Chan used.
3. **Nothing here rules out a seventh reading.** Only the join lands both figures among the six, and another reading could land them too.

So for FSTX the 2.6 percent is a fit to the printed figure rather than a test of it. **Every result here is exploratory**, and this one most of all, since the replication chose the join after seeing its figures.

## Lesson 4: the kept days are few, and most fall in 2008 and 2009

From 2004-07-16 to 2012-05-08, VIX closed above 35 on 190 days. That is the span FSTX’s days share with VIX’s, and it holds buy on gap’s span from 2006-05-11 to 2012-04-24. The first was 2008-09-17, at 36.22, the highest 80.86 on 2008-11-20, and the last 2011-11-09, at 36.16. Those dates hold only inside the window. The committed `VIX.csv` also closes above 35 on 100 days before 2004-07-15, the first of them on 1990-08-06, so the threshold was crossed long before either rule’s data begins.

Both rules keep days from 2008-09-18 to 2011-11-10, and most of them in the first two of those years.

```math
\begin{array}{l|r|r}
\text{Year} & \text{Buy on gap} & \text{FSTX} \\ \hline
2008 & 68 & 65 \\
2009 & 83 & 81 \\
2010 & 9 & 9 \\
2011 & 30 & 30 \\ \hline
\text{Kept days} & 190 & 185
\end{array}
```

So 151 of buy on gap’s 190 kept days, and 146 of FSTX’s 185, fall in 2008 and 2009. The days also come in stretches. A run here is a group of kept days with no other shared day between them, and each rule’s kept days form 15 runs. The longest, from 2008-09-30 to 2009-04-17, holds 138 of buy on gap’s days and 134 of FSTX’s. So the 190 kept days come from 15 separate episodes, and one episode holds most of them.

A kept day is not a day traded. Buy on gap held a position on only 20 of its 190 kept days, and its filtered figures rest on those 20. It gained on 8 and lost on 12. One of them, 2009-04-21, returned 0.093601, which is 0.722090 of the 0.129625 the kept days sum to. Without that day, the other 189 give 0.048032 and a Sharpe ratio of 0.855003, which print as 4.8 percent and 0.86. FSTX held a position on 43 of its 185 kept days, long on 21 and short on 22.

![Two charts on one shared date axis from July 2004 to May 2012. The top chart shows VIX’s daily close as a black line, mostly between 10 and 20 until mid-2007, with a dashed red line at 35. A grey band covers 2008-09-18 to 2011-11-10. Brass dots mark the 190 closes above 35, which cluster in late 2008 and early 2009, with small groups in May and June 2010 and from August to November 2011. Labels mark the first close above 35 inside the window, 36.22 on 2008-09-17, the highest, 80.86 on 2008-11-20, and the last, 36.16 on 2011-11-09. The bottom chart shows each rule’s daily returns summed over its kept days, flat at zero before September 2008 and flat after November 2011. Buy on gap’s black line wavers between about −0.02 and 0.03 until April 2009, jumps at a brass dot labelled “2009-04-21 alone adds 0.093601”, and ends at 0.129625. FSTX under the script’s sign, a dashed grey line, swings between about −0.08 and 0.11 in late 2008 and early 2009 and ends at 0.018889. FSTX under the sign the text describes, a red line, mirrors it and ends at −0.018889. The heading sets each rule’s figures beside the book’s, and the title calls the figure exploratory.](../docs/figures/vix_filter.png)

*Each curve in the bottom panel is a sum, unlike the compounded curves in the buy on gap and opening gap posts, because location 3509’s filtered figures are arithmetic means. Each ends at its 252 times the mean, times the kept days over 252. The book draws no figure for the filter.*

Chan warns about testing any risk indicator on a sample like this one. “Since the occurrence of financial panic or crises is relatively rare, it is very easy to fall victim to data-snooping bias when we try to decide whether an indicator is useful” (location 3541). Data snooping is finding a pattern in a sample because someone searched the sample for one. Here the panic is one stretch of 2008 and 2009, and buy on gap’s 17.2 percent rests mostly on one day inside it. **Every result here is exploratory.**

## Lesson 5: a test cannot tell the kept days from the rest

Chan reads his figures as evidence that VIX above 35 changes what each rule earns. That is a claim about two groups of days, the kept days and the others, so it can be tested. **Welch’s t-test** compares the mean of two groups. It divides the gap between the means by how far that gap would typically wander by chance, allowing each group its own spread, and calls the ratio t. A t near zero means the gap is small against that wander. The p-value is the chance of a t at least that far from zero if the two groups had the same mean.

```math
\begin{array}{l|r|r}
\text{Kept days against the other joined days} & t & p \\ \hline
\text{Buy on gap} & 0.705402 & 0.481405 \\
\text{FSTX, fade} & -0.684181 & 0.494679 \\
\text{FSTX, momentum} & 0.684181 & 0.494679
\end{array}
```

Both p-values sit near one half. A gap this size, or larger, would turn up about half the time between two groups with the same mean. So neither rule’s kept days can be told from its other days by this test, in either direction and under either sign. Chan prints no test, and the figures he prints are point estimates, single numbers with no measure of how much they could move.

The test treats each day as independent of the others. Kept days come in runs, and returns on neighbouring days can move together. When they do, the test counts more independent days than the sample holds. **Every result here is exploratory**, and this one says only that Chan’s four filtered figures, though they reproduce, are not evidence that VIX above 35 points either way for these two rules.

## What this replication cannot say

Six questions are beyond it.

1. **What Chan’s own code for the filter did.** No script ships for location 3509, and a search chose the join for FSTX.
2. **Whether Chan filtered before or after running the rule.** Both give the same figures on FSTX’s kept days, as Lesson 3 says.
3. **Whether the filter guards either rule after 2012.** Every kept day falls from 2008 to 2011. A test of it would fix the threshold and the join in writing first and run them on later data.
4. **What buy on gap earned on the index as it stood each day.** Every stock here was in the S&P 500 on 2012-04-24, so the [buy on gap post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-6-an-exact-reproduction-checks-the-arithmetic-not-the-edge) applies to the kept days too.
5. **Whether every VIX close is a clean print.** The repository’s check for a sudden change of scale flags one day, 2007-02-27, a real move from 11.15 to 18.31, and nothing here compares it with a second source. That check sees only a move of 1.6 times or more, so a smaller rescale anywhere in the file could move a day into the filter unseen.
6. **What costs would take.** Nothing is charged on either rule, and a filter that keeps few traded days leaves each cost a larger share of the return.

## What this means for a trader

One habit for each lesson.

1. **Compare like with like.** Before reading a filter’s effect, put the filtered and unfiltered figures on the same formula. Here one was compounded and the other arithmetic.
2. **Run a filter under both signs of the rule it guards.** A filter that cuts one sign’s return raises the other’s, so which way it points depends on the sign.
3. **Count how many ways someone could read the data.** When a specification is inferred from a printed figure, every reading tried is part of the result, and the one that lands is a fit.
4. **Count the days traded, not the days kept, and find the largest one.** Here 20 traded days carried buy on gap’s filtered return, and one of them carried most of it.
5. **Test the gap between the kept days and the rest.** Two point estimates that differ are not evidence of a difference until something says how far they could wander by chance.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.1 and 7.1, and Kindle locations 2965, 3509 and 3541.

*Not investment advice. Code: [the filter](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vix_filter.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vix_filter_figures.py), with the checks behind [the filter’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vix_filter.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vix_filter_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-47-the-vix-filter-on-buy-on-gap-and-the-stoxx-europe-50-gap-rule-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
