# Chan’s levered low-beta portfolio lost more than its capital in June 2001, at the leverage his own beta match asked for

*Chan argues that a low-beta portfolio, levered up to a high-beta portfolio’s beta, should out-compound the high-beta one. On his own S&P 500 file the fifth of stocks with the lowest beta had the higher Sharpe ratio. Its mean beta fell close to zero in spring 2001, so the match asked for leverages as high as 69.0762, and an ordinary month took the levered portfolio below zero.*

## Why lever the low-beta stocks

A stock’s **beta** measures how far it tends to move with the market. A stock with a beta of 2 tends to rise 2 percent on a day the market rises 1 percent, and a stock with a beta near 0 barely follows the market at all. **Leverage** is the position divided by the trader’s own capital. A leverage of 3 means \$3 of stock for every \$1 of capital, with the other \$2 borrowed, and here the borrowed part pays the three-month Treasury bill rate.

Ernest Chan’s *Quantitative Trading* puts the two together. A trader can raise a portfolio’s return by levering it or by choosing high-beta stocks, and “it is easy to apply a higher leverage on the low-beta portfolio so as to increase its beta to match that of the high-beta portfolio” (Chan, 2021, location 4684). Under the Fama-French model, which ties a stock’s expected return to its beta, its size and its book-to-price ratio, the two portfolios then earn the same average return, provided their stocks have the same average size and book value. Chan argues a trader should still prefer the low-beta portfolio, because “Empirical studies have found that a portfolio that consists of low-beta stocks generally has lower risk and thus a higher Sharpe ratio.” The **Sharpe ratio** is the return above the bill rate divided by the size of its swings. At the **Kelly leverage**, the leverage that makes wealth grow fastest, a portfolio compounds at the cash rate plus half its Sharpe ratio squared. The [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives that formula. So at its Kelly leverage the side with the higher Sharpe ratio should out-compound the other side at any leverage, unlevered included.

The same passage cites Edward Qian’s risk parity, which levers a low-risk mix of stocks and bonds for the same reason. The [post on risk parity against 60/40](https://github.com/l3a0/quantitative-trading/blob/main/blog/risk-parity-against-60-40.md#how-risk-parity-works) tests that half of the passage.

Chan’s chapter summary states the rule: “Holding a highly leveraged portfolio of low-beta stocks should generate higher long-term compounded growth than holding an unleveraged portfolio of high-beta stocks” (location 4709). A caveat sits between the two. Real returns have fat tails, meaning extreme months come more often than a bell curve allows, so “one should be quite wary of using too much leverage on normally low-beta stocks” (location 4700).

This repository tested the rule on Chan’s own S&P 500 file and drew six lessons.

1. **The low fifth looked like the better portfolio, and the beta match ruined it.** Unlevered, its Sharpe ratio was more than twice the high fifth’s. Levered to the high fifth’s beta, it lost more than its capital in June 2001.
2. **Matching beta divides by the low fifth’s beta.** In spring 2001 that beta was close to zero, so the leverage it asked for rose as high as 69.0762.
3. **An ordinary month did it.** June 2001 was a bad month for the low fifth and not an extreme one. Chan’s caveat about leverage holds, while its reason, the fat tails, is not what the run shows.
4. **The rule names no leverage.** The argument behind it assumes the Kelly leverage, and the test used the beta match.
5. **Registering a criterion did not cover every case.** The plan never said what a month losing more than the capital means, and the owner settled it after seeing the first one.
6. **A registered result on years the claim’s source could already read is not a holdout.** The file also holds only stocks still in the index in late 2007.

**The verdict is registered, and every other figure here is exploratory.** This is the first post in the series whose headline result is registered. Earlier posts that reproduced Chan’s figures labelled their results exploratory, because each reran a rule Chan had already chosen, on his own files. A registered result is one whose test and criterion were written down before any number was seen. Before any beta or return was computed, the plan wrote down the test’s specification, which is the five parts below, along with the first three outcomes of its criterion. The owner added the fourth outcome, ruin, after the first ruined month was visible, so its wording is not registered, and Lesson 5 says what had been seen. Registration rules out a specification tuned on this file. It does not make 2000 to 2007 unseen data, as Lesson 6 explains. Every other figure is a single measurement with no statistical test behind it, and each number this write-up measured after the run says so where it appears. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The test and the file

The plan fixed the test’s five parts before the run computed any number. Only the ruin outcome in part 5 came later.

1. **The data.** Chan’s `SPX_20071123.mat` holds 500 stocks, saved 2007-11-24, as the S&P 500 stood on 2007-11-23. A stock that left the index before then is not in the file, so every figure here is about survivors. SPY, the fund that tracks the index, comes from the adjusted closes in Chan’s `example6_2.xls`, saved 2008-01-29 and committed here as `spy_chan.csv`. The bill rate is FRED’s TB3MS, the monthly average three-month rate, downloaded 2026-09-30.
2. **The beta.** The stock file is cut to the 2,011 days it shares with SPY. At each month-end a stock’s beta is the slope, with an intercept, of its daily return above the bill rate on SPY’s. The fit uses the 252 days ending there and needs at least 200 of them.
3. **The two portfolios.** Each month-end where the test sorts the stocks by beta is a **formation**. The lowest fifth and the highest fifth hold 88 to 99 stocks each, from 444 to 495 eligible. Each is weighted equally and held one month, which gives 83 holding months, December 2000 to October 2007.
4. **The leverage.** At each month-end, k is the high fifth’s mean beta divided by the low fifth’s. Levering a portfolio k times multiplies its beta by k, so this k lifts the low fifth’s beta to the high fifth’s. That is location 4684’s match, and it is known before the month it applies to. A levered month returns rf + k × (r_low − rf), where r_low is the low fifth’s return and rf the bill rate for the month. Borrowing costs the bill rate, and no trading cost is charged.
5. **The criterion.** The statistic compares the two portfolios’ monthly log growth. A **t-statistic** divides the average monthly gap by how far that average would typically wander by chance, and the Newey-West version allows for neighbouring months moving together. The [post on factor models](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#example-74s-own-five-factors-day-to-day) uses the same statistic. The claim holds when the gap favours the levered low fifth with a t of at least 1.645, the one-sided 5 percent line, and is contradicted when the high fifth leads with a t of −1.645 or below. Anything between is not decided. The fourth outcome, added later, is ruin: a levered month at −1 or below means the claim is contradicted.

A levered month at −1 has lost the whole capital, and one below −1 has lost more. The log growth of such a month does not exist, so the statistic cannot be computed once one occurs. The [replication log’s Entry 45](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-45-a-levered-low-beta-portfolio-against-an-unlevered-high-beta-one-chans-quantitative-trading) records every rule and sets each figure beside the test that computes it.

## Lesson 1: the low fifth looked like the better portfolio, and the beta match ruined it

The verdict is **contradicted by ruin**. Levered to the high fifth’s beta, the low fifth lost more than its capital in the month ending 2001-06-29, at a leverage of 58.0262. A fresh stake levered by the same rule would have lost more than its capital again in September 2001.

Unlevered, the low fifth did look like the better portfolio. Realised compounded growth is twelve times the average monthly log return, the rate a portfolio actually compounded at.

```math
\begin{array}{l|r|r}
\text{Portfolio} & \text{Sharpe ratio} & \text{Growth a year} \\ \hline
\text{low fifth, unlevered} & 1.0132 & 0.1254 \\
\text{high fifth, unlevered} & 0.4457 & 0.1183 \\
\text{SPY} & & 0.0379 \\
\text{low fifth, levered to the high fifth's beta} & 0.2836 & \text{ruin}
\end{array}
```

Every one of those figures rests on survivors, and nothing tests the differences between them, so none decides anything. The levered row’s Sharpe ratio reads each month as if it were funded afresh at its start, which is how the plan defines the series. An investor ruined in June 2001 had no capital left to fund the months after it.

The levered path swung hard on the way up. It lost 0.5456 of its capital in January 2001 and 0.4516 in March, and still compounded to 4.8089 times its capital from December 2000 through May 2001. May 2001 alone returned 1.7253, at the highest leverage of the run, 69.0762, on a low-fifth month of 0.0279. The write-up measured all of those figures after the run except the 69.0762. Then June returned −2.5053 at a leverage of 58.0262, and a fresh stake in September −1.1278 at 31.5098. No t was computed, because the ruin ends the comparison, so nothing says what the statistic would have read without it.

## Lesson 2: matching beta divides by the low fifth’s beta, and in spring 2001 that beta was close to zero

The leverage is a ratio, and its denominator is the low fifth’s mean beta. When that beta approaches zero, the leverage has no ceiling. Over the 83 formations the low fifth’s mean beta ranged from 0.0280 to 0.6745, while the high fifth’s stayed between 1.4625 and 1.9532. The numerator moved within a narrow band, so the denominator set the leverage.

Both formations in 2000 sat near 0.15, at 0.1582 on 2000-11-30 and 0.1443 on 2000-12-29. Then the low fifth’s beta fell below 0.10 at nine formations, 2001-01-31 to 2001-09-28, and below 0.05 at four of them. The write-up measured those counts after the run, along with the 0.1443 and the table’s 0.0375 and 0.0448.

```math
\begin{array}{l|r}
\text{Formed} & \text{Low fifth's mean beta} \\ \hline
\text{2001-03-30} & 0.0375 \\
\text{2001-04-30} & 0.0280 \\
\text{2001-05-31} & 0.0337 \\
\text{2001-06-29} & 0.0448
\end{array}
```

So k averaged 7.8414 over the run and ranged from 2.1826 to 69.0762. It sat above 20 at eight formations, 2001-02-28 to 2001-09-28, a count the write-up also measured after the run. The highest, 69.0762, was formed on 2001-04-30 and applied in May. The 58.0262 that ruined June was formed on 2001-05-31.

After the fact the match overshot its own target. The levered low fifth’s realised beta, its slope on SPY’s monthly return above the bill rate, came to 3.4596, against the high fifth’s 2.0671. That reading also treats each month as freshly funded.

## Lesson 3: an ordinary month did it, so the caveat’s advice holds and its reason is not what the run shows

A levered month is ruined when its return reaches −1. Solving for the low fifth’s return, with k positive as it is in every month here, gives the **ruin line**, the return at or below which the levered month loses the whole capital.

```math
r_f + k\,(r_\text{low} - r_f) \le -1 \quad\Longleftrightarrow\quad r_\text{low} \le r_f - \frac{1 + r_f}{k}
```

The write-up computed the line after the run. In June 2001 the bill rate for the month was 0.0029 and k was 58.0262, so the line sat at −0.0144. A low-fifth month of −1.44 percent was enough to wipe out the levered portfolio. The low fifth returned −0.0403 that month.

```math
\begin{array}{l|r|r|r|r|r}
\text{Month} & k & \text{Ruin line} & \text{Low fifth} & \text{Rank of 83} & \text{Leverage that ruins} \\ \hline
\text{June 2001} & 58.0262 & -0.0144 & -0.0403 & \text{6th worst} & 23.2017 \\
\text{September 2001} & 31.5098 & -0.0296 & -0.0337 & \text{8th worst} & 27.9461
\end{array}
```

Neither month was extreme. June was the sixth-worst of the low fifth’s 83 months and September the eighth-worst. The write-up measured September’s −0.0337 and its rank after the run, along with the last column, the smallest leverage that would have ruined each month. The match asked June for 58.0262, 2.50 times its ruinous leverage of 23.2017 to four places.

The rest of the history says the same. Of the 83 months, 13 fell at or below June’s line of −0.0144, so holding June’s leverage of 58.0262 in every month would have ruined 13 of them. A bell curve with the low fifth’s own monthly mean of 0.0109 and standard deviation of 0.0292 puts the chance of a month at or below that line at 0.1931, about one month in five. The write-up measured all of these figures after the run. No fat tail was needed. A month a bell curve expects regularly was enough at that leverage.

The line was closest to zero in May 2001, at −0.0115, the month the leverage peaked. Once the leverage dropped, the line sank below the low fifth’s worst month. From 2002-02-28 on it sat below −0.10, while the low fifth’s worst month, July 2002, returned −0.0733, another figure the write-up measured after the run.

![Three charts sharing one axis of holding months from December 2000 to October 2007. The top chart shows each fifth’s mean beta at formation. A muted grey line, the highest fifth, stays between about 1.5 and 2 throughout. A black line, the lowest fifth, starts near 0.15, falls almost to zero in the first half of 2001, with a red dot labelled 0.0280, formed 2001-04-30, then climbs to between 0.4 and 0.7 from late 2002 on. The middle chart shows the leverage on a log scale. A black line climbs from about 10 to a peak labelled highest, 69.0762, in May 2001, then falls below 10 in February 2002, sits between 7 and 9 until July 2002, and stays between 2 and 5 from August 2002 on. Two red dots mark the ruined months, June 2001 at k 58.0262 with a levered return of −2.5053, and September 2001 at k 31.5098 with a levered return of −1.1278. A dashed grey line at 9.9884 is labelled full-sample Kelly, look-ahead. The bottom chart shows the low fifth’s monthly return in black, swinging mostly between −0.05 and 0.08, against a dashed red ruin line that rises from −0.10 to about −0.01 in spring 2001 and then drops out of the bottom of the chart in early 2002. Two red dots mark the months the return fell below the line, June 2001 at −0.0403 against −0.0144 and September 2001 at −0.0337 against −0.0296. The title reads registered verdict, exploratory path.](../docs/figures/low_beta_leverage.png)

*Each value sits at the month it applied to, so the beta and the leverage formed on 2001-04-30 appear at May 2001. The ruined months carry the verdict, registered under an amendment made after June 2001 was seen. Every path drawn is exploratory, and the ruin line and the Kelly line were added after the run. The Kelly line looks ahead and decides nothing.*

Chan’s caveat at location 4700 warns against “too much leverage on normally low-beta stocks” because returns have fat tails. Its advice is borne out. Its reason is not what this run shows. The near-zero betas set the leverage, and the return that met it was only a bad month. Which of the two did more damage is not something this test can separate.

## Lesson 4: the rule names no leverage, and the argument behind it assumes Kelly’s

Location 4709 says “highly leveraged” and names no number. Location 4684 names the beta match, which the passage proposes, and the Kelly leverage, which its growth argument rests on. The plan tested the beta match, the leverage the passage spells out, which is known before the month it applies to.

The Kelly reading needs the whole sample, so it looks ahead and decides nothing. The low fifth’s full-sample Kelly leverage is 9.9884. At that leverage the formula’s growth is the bill rate plus half the Sharpe ratio squared, 0.0283 + 0.5132 = 0.5415 a year, against the high fifth’s realised 0.1183. That comparison is built to favour the low fifth. In-sample Kelly leverage gives a portfolio the highest growth the formula allows, so the low fifth gets its best case while the high fifth stays unlevered. The 0.5415 is also the formula’s figure, and no portfolio realised it.

The beta match asked for more than that look-ahead Kelly leverage at 13 formations, all between 2000-12-29 and 2001-12-31, a count the write-up measured after the run. Overshooting the Kelly leverage is costly even when returns follow a bell curve. The [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#lesson-6-twice-the-kelly-leverage-earns-only-the-cash-rate) shows that twice the Kelly leverage earns only the cash rate, and that growth falls below zero not far past it.

## Lesson 5: registering a criterion did not cover every case

The plan’s statistic reads ln(1 + r) for every levered month, and that does not exist for r at −1 or below. The plan never said what such a month means. The build stopped at June 2001, before computing anything the criterion reads.

The repository’s owner then ruled that ruin means the claim is contradicted. By then four things had been seen.

1. The calendar of formations and holding months.
2. The leverage path.
3. Both ruined months.
4. Both fifths’ unlevered returns for the first eight formations.

So the ruin case and its wording are not registered. The hypothesis, the specification and the first three outcomes stay registered, because they were written before any of that was seen. The verdict follows from a rule written after its first instance was seen. The [post on factor models](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#lesson-5-fix-the-rule-before-the-number) explains why the order of a rule and its number decides what a verdict can claim.

## Lesson 6: a registered result on years the claim’s source could already read is not a holdout

A **holdout** is data kept back from every decision about a test, so a result on it is a fresh check. Registration stops this repository from tuning the specification to this file. It does nothing about which years the file covers. Chan’s premise comes from “empirical studies” of past prices, and 2000 to 2007 were past prices by the time the book printed the claim. So this test checks the rule on years its source could already have read.

The file also holds only survivors. Which side that flatters is not measured here. High-beta stocks that fell out of the index would flatter the high side and work against the claim, and that is a hypothesis rather than a finding. The [post on factor models](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#lesson-6-every-figure-that-touches-the-stocks-is-about-survivors) walks through what survivorship does to a file built this way.

The rule can be tested on later data, with the index as it stood each month, and at leverage a broker would lend. This post predicts no result for either.

## What this replication cannot say

Five questions are beyond it.

1. **What the t-statistic would have read.** The ruin ended the comparison in June 2001, so the statistic was never computed.
2. **Whether fat tails or near-zero betas did more damage.** The betas set the leverage and an ordinary month met it, and the test does not separate the two.
3. **What survivorship does to either side.** The file lacks every stock that left the index before 2007-11-23.
4. **Whether the claim holds after the book.** Every year here was available to the claim’s source.
5. **The model’s half of the argument.** Location 4684’s equal average returns assume both portfolios have the same market capitalisation and book value, and this file holds neither.

## What this means for a trader

One habit for each lesson.

1. **Judge a leverage rule by its worst month, not by the portfolio’s Sharpe ratio.** A portfolio with the better Sharpe ratio was ruined by the leverage asked of it.
2. **Check what a leverage formula divides by.** A ratio whose denominator can approach zero can ask for any leverage at all.
3. **Compute the loss that ruins at the leverage asked for, and count how often the history reaches it.** Here 13 of 83 months did.
4. **Ask which leverage a claim means.** A rule that says “highly leveraged” leaves the number to the reader, and the argument behind it may assume a different one.
5. **Write down what the criterion does in every case, ruin included.** A case the plan leaves open gets settled after it is seen.
6. **Treat years the source could already read as spent.** A result on them can contradict a claim, and a confirmation needs later data.

## References

1. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Kindle locations 4684, 4700 and 4709.

*Not investment advice. Code: [the test](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_leverage.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_leverage_figures.py), with the checks behind [the test’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_leverage.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_leverage_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-45-a-levered-low-beta-portfolio-against-an-unlevered-high-beta-one-chans-quantitative-trading) that records the plan and every figure beside the test that computes it.*
