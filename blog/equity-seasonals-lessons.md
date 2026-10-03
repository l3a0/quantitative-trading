# Chan’s equity seasonals reproduce to the digit, and the digits cannot say whether they died

*Reproducing a strategy published as dead checks the figures its author printed. It does not check the death.*

## Why reproduce a strategy its author called dead

Ernest Chan’s *Quantitative Trading* describes two seasonal strategies in stocks, and reports that seasonality of this kind has faded. The second strategy, a monthly rotation from a 2007 working paper by Heston and Sadka, he publishes as dead. Its average annual return before 2002 was “more than 13 percent” before costs, he writes, and the effect “has disappeared since then” (Chan, 2021, p. 179). The same sentence invites the reader to check that in Example 7.7.

This repository checked. The data files behind both examples are public, and they are committed here, though for Example 7.6 the public file is an earlier save than the one Chan’s script loads. The book prints the examples in MATLAB in the first edition, and in MATLAB, Python and R in the revised edition. Fourteen of the printed figures need only data the committed files hold, and all fourteen reproduce to the digits printed.

None of the fourteen can say whether the effect died. Example 7.7’s are figures over the whole file, and the S&P 500 file holds only 13 months before 2002 once the ranking has its year of history. Both files hold only the companies still in their index on the day Chan saved them. A printed figure that reproduces shows that the code and the data agree with the book. A death is a claim about two periods, and testing it needs a criterion for “disappeared” written down before anything is computed. This repository wrote none before computing returns on either side of 2002, so the post reports them and draws no verdict from them.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two strategies and the two files

**Example 7.6, the January effect.** At each December year-end, rank the S&P 600 small caps on their return over the calendar year. Buy the worst tenth and short the best tenth at that close, and exit both at January’s last close. The reason Chan gives is that investors sell their losers in December to claim the tax loss, and the selling pressure lifts in January (p. 175). Each trade pays two one-way costs of 5 basis points.

**Example 7.7, Heston and Sadka.** At each S&P 500 month-end, rank the stocks on their return in the same calendar month a year earlier. Buy the best tenth and short the worst tenth, and hold for the month. The two scripts this repository holds turn their monthly returns into an annual return by multiplying their mean by 12, and into a Sharpe ratio by multiplying the mean over the standard deviation by √12, with no risk-free rate. The revised MATLAB and R the book prints do the same.

What Chan says of each is not the same, and the difference matters for what a reproduction can find.

1. **Seasonal strategies in stocks.** Much of the seasonality in equity markets “has weakened or even disappeared in recent years”, Chan writes (p. 174). Earlier in the book he recalls praising a seasonal stock strategy on his blog, a reader backtesting it and finding it did not work, and his own backtest confirming the reader’s (p. 13). He names Example 7.6 as that strategy.
2. **Example 7.6.** Its own text is not a death notice. The revised edition says the January effect failed in January 2006 and January 2007 and then “worked wonderfully” in January 2008 (p. 175).
3. **Example 7.7.** This one is published as dead, in the sentence quoted above.

The examples read two of Chan’s own MATLAB data files, converted into one file per stock.

1. **For Example 7.6**, `IJR_20080114.mat`: 600 members of the S&P 600, recorded as split-adjusted, saved 2008-01-15, spanning 2004-01-15 to 2008-01-14.
2. **For Example 7.7**, `SPX_20071123.mat`: 500 members of the S&P 500, also recorded as split-adjusted, saved 2007-11-24, spanning 1999-11-24 to 2007-11-23.

Chan’s Example 7.6 script loads a later save, `IJR_20080131.mat`, which the mirror of his first-edition code and data, named below, does not hold. Lesson 3 says what that costs. Both files hold only the companies in their index on the day Chan saved them, carried backwards. That limits everything below, and Lesson 4 comes back to it.

**Which edition says what.** The first edition (2009) prints the examples in MATLAB, cited here by script as `example7_6.m` and `example7_7.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror. The revised edition (2021) prints both in MATLAB, Python and R at pp. 174 to 182. Its Python is cited as `example7_6.py` and `example7_7.py` at commit `653cf92` of liujiantong/epchan_books, a third-party copy whose five printed figures match the book. Page numbers here are the revised edition’s.

Every result below is **exploratory**. Reproducing a printed figure tests a hypothesis Chan chose, on data he chose, so it can say whether the figure reproduces and nothing more.

## Lesson 1: every reachable figure reproduces, and only under each script’s own rules

Here is every printout of Example 7.6, at the precision each source prints. The two columns are the two Januaries the committed file reaches.

```math
\begin{array}{l|r|r}
\text{Example 7.6 printout} & \text{January 2006} & \text{January 2007} \\ \hline
\text{MATLAB, both editions} & -0.0244 & -0.0068 \\
\text{Python, revised edition} & -0.023853 & -0.003641 \\
\text{R, revised edition} & -0.0244 & -0.0068
\end{array}
```

And every printout of Example 7.7, whose two figures are the average annual return and the Sharpe ratio:

```math
\begin{array}{l|r|r}
\text{Example 7.7 printout} & \text{Annual return} & \text{Sharpe ratio} \\ \hline
\text{MATLAB, first edition} & -0.9167 & -0.1055 \\
\text{MATLAB, revised edition} & -0.0129 & -0.1243 \\
\text{Python, revised edition} & -0.012679 & -0.122247 \\
\text{R, revised edition} & -0.01139674 & -0.1095098
\end{array}
```

That is six figures for Example 7.6 and eight for Example 7.7. The MATLAB prints the same two Januaries in both editions, so they count once. Every one of the fourteen is computed here and lands on the digits printed.

None of them comes out of the strategy as described above. Each needs rules the description leaves out, and each of those rules moves a printed figure when it is changed. Six of them, all read from code this repository holds, with the figure each change gives instead:

1. **How many stocks make a tenth.** Example 7.6’s MATLAB rounds a tenth of the ranked stocks half away from zero. Rounding down instead gives −0.0234 for January 2006.
2. **Which close keeps a stock in the ranking.** The first edition’s Example 7.7 decides whether to keep a stock by looking at a different stock’s close, because it compares a row sorted by return with a row still in column order. Keeping each stock on its own close gives −1.0822 a year.
3. **Which months the mean runs over.** The same script averages over 95 months, counting the 12 that hold no position as zero. Averaging over the 83 that hold positions gives −1.0492.
4. **What the standard deviation does with a missing month.** The same script counts the one month with no return as zero. Skipping it gives a Sharpe ratio of −0.1049.
5. **When a stock’s month ends.** The revised Python reads each stock’s own last priced day in the month. One shared month-end row for every stock gives −0.012917.
6. **What the standard deviation divides by.** The revised Python divides by the number of months, n. Dividing by n − 1 gives a Sharpe ratio of −0.121508.

## Lesson 2: one strategy, four printouts, four answers

Example 7.7 gives four answers across its four printouts, and the first of them is in different units from the other three.

The first edition’s −0.9167 is a sum over every position held each month, never divided by how many there were. So it is in units of summed positions, not a return on capital. Dividing each month by its positions puts the same script in units of capital, at −0.0120 a year, a figure computed here that Chan did not print. The revised Python divides, and so do the revised MATLAB and R. The three revised printouts land at −0.0129, −0.012679 and −0.01139674.

The three revised figures still differ, so three languages give three answers to one strategy. The three scripts differ in where a month ends, how a tenth is rounded and what the standard deviation divides by, and each difference moves a digit.

Example 7.6 is a smaller case. Its three languages give two answers, not three. The R prints MATLAB’s figures. The revised Python differs because it slices its winners as `topN - 2` stocks rather than a full tenth, so in January 2006 it shorts 56 winners against the 58 losers it buys, of 579 ranked. Taking the full tenth gives MATLAB’s figures to every digit.

The revised MATLAB and R rules come from the code the book prints, on pp. 179 and 181, which [issue 226](https://github.com/l3a0/quantitative-trading/issues/226) quotes. The R runs as printed. The MATLAB does not: it cuts its prices down to month-end rows and then looks one up by a daily row number, which stops on the first month. Reading the month-end row it means gives Chan’s figures. One choice is inferred rather than read. The listing calls a helper, `smartstd`, whose body no page prints, and Chan’s two books ship two versions of it. The one from his second book, *Algorithmic Trading*, divides by n and prints the −0.1243. The one from this book’s first edition divides by n − 1 and gives −0.1236. So the rules are the printed code for every choice but that one, which rests on the digits it reproduces.

## Lesson 3: reproducing a strategy published as dead checks its figures, not its death

Every printout’s whole-period figure for Example 7.7 is negative on Chan’s file, as he printed it. That is consistent with an effect that died. It is also consistent with one that never lived on these stocks over these years. A reproduction cannot tell those apart, for three reasons.

1. **This repository wrote no criterion first.** A claim that an effect “disappeared” needs a test stated before any number is seen: which statistic, over which periods, crossing which bar. The repository’s rule is that a figure computed before its criterion carries no verdict, and it computed the split below first.
2. **The file barely reaches the period before.** The S&P 500 file starts on 1999-11-24. After the twelve months the ranking needs, it holds 13 months before 2002.
3. **The 13 percent is not computed on this file.** Chan reports it beside his citation of Heston and Sadka, and this file cannot recompute it.

What the file can give is a split, and it is **exploratory, with no verdict**. The revised Python keeps 83 months for its statistics, from 2000-12-31 to 2007-10-31. Cut at the start of 2002:

```math
\begin{array}{l|r|r|r}
\text{Revised Python, split at 2002} & \text{Months} & \text{Annual return} & \text{Sharpe ratio} \\ \hline
\text{Before 2002} & 13 & -0.145387 & -0.859993 \\
\text{From 2002} & 70 & 0.011967 & 0.141777
\end{array}
```

On survivors, over this short window, the loss sits before 2002 and the period after it is slightly positive. That runs the opposite way to the published story. Only the revised Python’s series is split here.

The 70 months from 2002 are not a steady small gain. They climb to a peak in January 2006 and fall from there to the end. The gap between 2002, whose months sum to 0.2227, and 2006, whose months sum to −0.1319, is wider than the gap between the two halves’ annual returns. The figure below draws the 83 months as a running sum, so each half’s slope is its annual return divided by 12.

![A line chart of the running sum of Example 7.7’s monthly returns under the revised edition’s Python rules, from December 2000 to October 2007, in fractions of capital. A dashed vertical line marks the start of 2002. To its left, labelled 13 months before 2002 at −0.145387 a year and a Sharpe ratio of −0.859993, the line falls through 2001. To its right, labelled 70 months from 2002 at 0.011967 a year and a Sharpe ratio of 0.141777, the line climbs steeply through 2002, swings up and down through 2003 to 2005, peaks in January 2006, and falls to end below zero. The title calls the split an exploratory cut with no verdict, and the note names Chan’s S&P 500 file, which holds only survivors.](../docs/figures/equity_seasonals_split.png)

*The running sum climbs through 2002, peaks in January 2006 and falls to the end of the file. The labels give each half’s annual return and Sharpe ratio.*

The split carries no verdict because this repository wrote no criterion before computing it.

Chan says the most recent five years do even worse (p. 180), and the years after 2006 sit inside them. The figure does not test that claim, and the section on what this replication cannot say gives the reason.

Example 7.6 meets the same limit from another side. The two Januaries reproduced here are the two that lost. The one Chan’s text says “worked wonderfully” (p. 175), January 2008, is printed as 0.0881 by both editions’ MATLAB and the revised R, and as 0.088486 by the revised Python. It needs prices through 2008-01-31, and the committed file ends on 2008-01-14. [Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) tracks reaching it. So the reproduction holds both of Chan’s failures and none of his success, which says nothing about whether the January effect lives.

## Lesson 4: a file of survivors is the first thing the result cannot get past

Both files hold the companies in their index on the day Chan saved them, with each one’s history carried backwards. A company that left the S&P 500 in 2003, because it was acquired, shrank or failed, is not in a file saved in 2007. So every figure in this post is about companies that survived to the end of the file.

Both strategies rank stocks on past returns and trade the tenth at each end, so which companies the file holds decides which companies they trade. A company the index dropped before the save is a company neither strategy could pick, whatever its returns were.

[The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches survivorship in full. On two tables Chan prints for the purpose, a database of survivors turns a loss into a large gain. [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196) is where Heston and Sadka’s 13 percent gets tested on a panel that keeps the companies that left.

## What this replication cannot say

Three questions are beyond it.

1. **Whether the effect existed before 2002.** The file holds 13 months before 2002, all on survivors. [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196) is where the test runs on a panel without that limit.
2. **Example 7.6’s third January.** Chan’s one winning January needs a file running to 2008-01-31. [Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) tracks it.
3. **Chan’s claim about the most recent five years.** Directly after the MATLAB listing of Example 7.7, he suggests running the program on “the most recent five years instead of the entire data period” and says those years do even worse (p. 180). The entire data period is the program’s own input, the S&P 500 file, so the five years run roughly from late 2002 to late 2007, inside the committed file. The file can check the claim. This post quotes no five-year figure, because this repository has written no criterion for one. [Issue 254](https://github.com/l3a0/quantitative-trading/issues/254) runs the check under a criterion written first.

## What this means for a trader

Three habits follow from the lessons above.

1. **Reproduce a published figure with the author’s code before trusting a description of it.** Every figure here needed rules the description leaves out.
2. **Check a figure’s units before comparing two printouts.** The first edition’s −0.9167 and the revised edition’s −0.0129 come from one strategy, and only one of them is a return on capital.
3. **Do not read a survivor file as evidence that an effect died or lived.** A file saved after the fact holds the stocks that made it, and a split through 83 months of them swings with a single year.

On Chan’s own files, every printed figure his data reaches reproduces exactly. Whether the strategies died is a separate question, and it needs a criterion and a panel these files do not supply.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Examples 7.6 and 7.7, cited by MATLAB script.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 13, 174, 175, 179 and 180, and Examples 7.6 and 7.7 at pp. 174 to 182.
- Heston, S. L., & Sadka, R. (2007), as Chan (2021, p. 179) cites them, a working paper. Published as Heston, S. L., & Sadka, R. (2008). Seasonality in the cross-section of stock returns. *Journal of Financial Economics*, 87(2), 418–445.
- Singal, V. (2006). *Beyond the Random Walk: A Guide to Stock Market Anomalies and Low-Risk Investing*. Oxford University Press. Cited by Chan (2021, p. 175) for the January effect.

*Not investment advice. Code: [the two strategies](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals_figures.py), with the checks behind [the strategies’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-7-the-equity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
