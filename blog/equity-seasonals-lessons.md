# Chan’s equity seasonals reproduce to the digit, and the digits cannot say whether they died

*Reproducing a strategy published as dead checks the figures its author printed. It does not check the death.*

## Why reproduce a strategy its author called dead

Ernest Chan’s *Quantitative Trading* describes two seasonal strategies in stocks, and reports that seasonality of this kind has faded. The second strategy, a monthly rotation from a 2007 working paper by Heston and Sadka, he publishes as dead. Its average annual return before 2002 was “more than 13 percent” before costs, he writes, and the effect “has disappeared since then” (Chan, 2021, p. 179). The same sentence invites the reader to check that in Example 7.7.

This repository checked. The data files behind both examples are public, and they are committed here. The book prints the examples in MATLAB in the first edition, and in MATLAB, Python and R in the revised edition. Seventeen of the printed figures need only data the committed files hold, and all seventeen reproduce to the digits printed.

None of the seventeen can say whether the effect died. Example 7.7’s are figures over the whole file, and the S&P 500 file holds only 13 months before 2002 once the ranking has its year of history. Both files hold only the companies still in their index on the day Chan saved them. A printed figure that reproduces shows that the code and the data agree with the book. A death is a claim about two periods, and testing it needs a criterion for “disappeared” written down before anything is computed. This repository wrote none before computing returns on either side of 2002, so the post reports them and draws no verdict from them.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two strategies and the two files

**Example 7.6, the January effect.** At each December year-end, rank the S&P 600 small caps on their return over the calendar year. Buy the worst tenth and short the best tenth at that close, and exit both at January’s last close. The reason Chan gives is that investors sell their losers in December to claim the tax loss, and the selling pressure lifts in January (p. 175). Each trade pays two one-way costs of 5 basis points.

**Example 7.7, Heston and Sadka.** At each S&P 500 month-end, rank the stocks on their return in the same calendar month a year earlier. Buy the best tenth and short the worst tenth, and hold for the month. The two scripts this repository holds turn their monthly returns into an annual return by multiplying their mean by 12, and into a Sharpe ratio by multiplying the mean over the standard deviation by √12, with no risk-free rate. The revised MATLAB and R the book prints do the same.

What Chan says of each is not the same, and the difference matters for what a reproduction can find.

1. **Seasonal strategies in stocks.** Much of the seasonality in equity markets “has weakened or even disappeared in recent years”, Chan writes (p. 174). The same sentence goes on to call some seasonal trades in commodity futures still profitable, and [the companion post on the commodity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md) tests that half. Earlier in the book he recalls praising a seasonal stock strategy on his blog, a reader backtesting it and finding it did not work, and his own backtest confirming the reader’s (p. 13). He names Example 7.6 as that strategy.
2. **Example 7.6.** Its own text is not a death notice. The revised edition says the January effect failed in January 2006 and January 2007 and then “worked wonderfully” in January 2008 (p. 175).
3. **Example 7.7.** This one is published as dead, in the sentence quoted above.

The examples read two of Chan’s own MATLAB data files, converted into one file per stock.

1. **For Example 7.6**, `IJR_20080131.mat`: 600 members of the S&P 600, recorded as split-adjusted, saved 2008-02-02, spanning 2004-01-15 to 2008-02-01.
2. **For Example 7.7**, `SPX_20071123.mat`: 500 members of the S&P 500, also recorded as split-adjusted, saved 2007-11-24, spanning 1999-11-24 to 2007-11-23.

The mirror of Chan’s first-edition code and data, named below, holds only an earlier save of the S&P 600 file, `IJR_20080114.mat`, which ends on 2008-01-14. The file his Example 7.6 script loads comes from [a public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84), a third party’s repost rather than Chan’s own. That copy also carries the earlier save, byte for byte as the mirror has it, which is why its later file is trusted. The two saves give the first two Januaries to the same digits. Both files hold only the companies in their index on the day Chan saved them, carried backwards. That limits everything below, and Lesson 4 comes back to it.

**Which edition says what.** The first edition (2009) prints the examples in MATLAB, cited here by script as `example7_6.m` and `example7_7.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror. The revised edition (2021) prints both in MATLAB, Python and R at pp. 174 to 182. Its Python is cited as `example7_6.py` and `example7_7.py` at commit `653cf92` of liujiantong/epchan_books, a third-party copy whose five printed figures match the book. Page numbers here are the revised edition’s.

Every result below is **exploratory**. Reproducing a printed figure tests a hypothesis Chan chose, on data he chose, so it can say whether the figure reproduces and nothing more.

## Lesson 1: every reachable figure reproduces, and only under each script’s own rules

Here is every printout of Example 7.6, at the precision each source prints, one column for each of its three Januaries. Each number is the return on one trade, held from a December year-end close to the last close of the January its column names, after the two costs. It is a fraction of the capital, split evenly between the long side and the short side. So −0.0244 is a loss of 2.44 percent over January 2006, and 0.0881 is a gain of 8.81 percent over January 2008.

```math
\begin{array}{l|r|r|r}
\text{Example 7.6 printout} & \text{January 2006} & \text{January 2007} & \text{January 2008} \\ \hline
\text{MATLAB, both editions} & -0.0244 & -0.0068 & 0.0881 \\
\text{Python, revised edition} & -0.023853 & -0.003641 & 0.088486 \\
\text{R, revised edition} & -0.0244 & -0.0068 & 0.0881
\end{array}
```

And every printout of Example 7.7, whose two figures are the average annual return and the Sharpe ratio. The annual return is a fraction too, so −0.0129 is a loss of 1.29 percent a year. The first edition’s −0.9167 is not a loss of 91.67 percent a year. It is in different units, which Lesson 2 explains.

```math
\begin{array}{l|r|r}
\text{Example 7.7 printout} & \text{Annual return} & \text{Sharpe ratio} \\ \hline
\text{MATLAB, first edition} & -0.9167 & -0.1055 \\
\text{MATLAB, revised edition} & -0.0129 & -0.1243 \\
\text{Python, revised edition} & -0.012679 & -0.122247 \\
\text{R, revised edition} & -0.01139674 & -0.1095098
\end{array}
```

That is nine figures for Example 7.6 and eight for Example 7.7. The MATLAB prints the same three Januaries in both editions, so they count once. Every one of the seventeen is computed here and lands on the digits printed.

None of them comes out of the strategy as described above. Each needs rules the description leaves out, and each of those rules moves a printed figure when it is changed. Seven of them, all read from code this repository holds, with the figure each change gives instead:

1. **How many stocks make a tenth.** Example 7.6’s MATLAB rounds a tenth of the ranked stocks half away from zero. Rounding down instead gives −0.0234 for January 2006.
2. **Which close keeps a stock in the ranking.** The first edition’s Example 7.7 decides whether to keep a stock by looking at a different stock’s close, because it compares a row sorted by return with a row still in column order. Keeping each stock on its own close gives an annual return of −1.0822, in summed positions like the −0.9167 it replaces.
3. **Which months the mean runs over.** The same script averages over 95 months, counting the 12 that hold no position as zero. Averaging over the 83 that hold positions gives an annual return of −1.0492, in the same units.
4. **What the standard deviation does with a missing month.** The same script counts the one month with no return as zero. Skipping it gives a Sharpe ratio of −0.1049.
5. **When a stock’s month ends.** The revised Python reads each stock’s own last priced day in the month. One shared month-end row for every stock gives an annual return of −0.012917.
6. **What the standard deviation divides by.** The revised Python divides by the number of months, n. Dividing by n − 1 gives a Sharpe ratio of −0.121508.
7. **Whether a stock missing a year-end close is ranked.** Example 7.6’s revised Python fills a missing year-end close with the last one before it, as pandas did before version 3.0. So for 2007 it ranks PMC, which has no close at the end of 2006, on its last close before an 851-day gap in its prices. That reads the gap as a gain of 1.3056, or 130.56 percent, fourth best of 595, and the script holds PMC short. Without PMC, 594 stocks are ranked. A tenth of 595 rounds to 60 and a tenth of 594 to 59. Without the fill, January 2008 gives 0.090908.

## Lesson 2: one strategy, four printouts, four answers

Example 7.7 gives four answers across its four printouts, and the first of them is in different units from the other three.

The first edition’s −0.9167 is a sum over every position held each month, never divided by how many there were. So it is in units of summed positions, not a return on capital. Dividing each month by its positions puts the same script in units of capital, at −0.0120 a year, a figure computed here that Chan did not print. The revised Python divides, and so do the revised MATLAB and R. The three revised printouts land at −0.0129, −0.012679 and −0.01139674.

The three revised figures still differ, so three languages give three answers to one strategy. The three scripts differ in where a month ends, how a tenth is rounded and what the standard deviation divides by, and each difference moves a digit.

Example 7.6 is a smaller case. Its three languages give two answers, not three. The R prints MATLAB’s figures. The revised Python differs because it slices its winners as `topN - 2` stocks rather than a full tenth, so in January 2006 it shorts 56 winners against the 58 losers it buys, of 579 ranked. Taking the full tenth gives MATLAB’s figures for 2006 and 2007 to every digit. January 2008 also needs the fill in Lesson 1’s seventh rule dropped, and then all three match.

The revised MATLAB and R rules come from the code the book prints, on pp. 179 and 181. The R needs no repair. The MATLAB does: it cuts its prices down to month-end rows and then looks one up by a daily row number, which stops on the first month. Reading the month-end row instead, with the helper below, gives Chan’s figures. The listing also calls a helper, `smartstd`, whose body those pages do not print, and Chan’s two books ship two versions of it. The one from his second book, *Algorithmic Trading*, divides by n and prints the −0.1243. The one from this book’s first edition divides by n − 1 and gives −0.1236. [A public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84) settles both points the page leaves open. Its Example 7.7 already reads the month-end row, and it ships the second book’s `smartstd`.

## Lesson 3: reproducing a strategy published as dead checks its figures, not its death

Every printout’s whole-period figure for Example 7.7 is negative on Chan’s file, as he printed it. That is consistent with an effect that died. It is also consistent with one that never lived on these stocks over these years. A reproduction cannot tell those apart, for three reasons.

1. **This repository wrote no criterion for “disappeared” first.** A claim that an effect “disappeared” needs a test stated before any number is seen: which statistic, over which periods, crossing which bar. The repository’s rule is that a figure computed before its criterion carries no verdict, and it computed the split below first.
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

Chan makes one claim about timing that the file can check. Directly after the MATLAB listing of Example 7.7, he suggests running the program on “the most recent five years instead of the entire data period” and says the average returns are even worse (p. 180). The entire data period is the program’s own input, the S&P 500 file, so those five years are inside it.

This repository wrote the check down before computing any five-year figure. The running-sum figure above was already published then, so the shape of those years was in view, and the check was chosen because it runs Chan’s program exactly as his sentence says. Rerun the revised MATLAB’s rules unchanged on the file’s rows after 2002-11-23, and call the claim reproduced if the annual return comes out below the whole period’s. The rerun keeps 47 months, from December 2003 to October 2007, and returns −0.0165 a year against the whole period’s −0.0129. The claim holds. Under the revised Python’s rules, reported beside it with no verdict, the figures are −0.016431 and −0.012679.

That sits beside the split without contradicting it. The 70 months from 2002 include 23, from January 2002 to November 2003, that the five-year rerun leaves out. Under the revised Python’s rules those 23 return 0.069997 a year. Without them, the months that remain lose money.

That verdict is narrow. The gap between the two figures is 0.0036 a year, and the rerun’s annual return has a standard error of 0.0281 a year, about eight times larger. So the check shows that Chan’s comparison holds on his own file of survivors. It does not show that the effect weakened.

Example 7.6 meets the same limit from another side. All three of its Januaries reproduce: the two that lost, and January 2008, the one Chan’s text says “worked wonderfully” (p. 175), at 0.0881 in both editions’ MATLAB and the revised R and 0.088486 in the revised Python. One winning January after two losing ones, on a file of survivors, is three trades. They show that Chan’s code and data agree with his book, and they say nothing about whether the January effect lives.

## Lesson 4: a file of survivors is the first thing the result cannot get past

Both files hold the companies in their index on the day Chan saved them, with each one’s history carried backwards. A company that left the S&P 500 in 2003, because it was acquired, shrank or failed, is not in a file saved in 2007. So every figure in this post is about companies that survived to the end of the file.

Both strategies rank stocks on past returns and trade the tenth at each end, so which companies the file holds decides which companies they trade. A company the index dropped before the save is a company neither strategy could pick, whatever its returns were.

[The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches survivorship in full. On two tables Chan prints for the purpose, a database of survivors turns a loss into a large gain. Heston and Sadka’s 13 percent has not been tested here on a panel that keeps the companies that left.

## What this replication cannot say

One question is beyond it: whether the effect existed before 2002. The file holds 13 months before 2002, all on survivors. Testing it needs a panel without that limit.

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
