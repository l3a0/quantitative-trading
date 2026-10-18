# Two equity seasonals show no edge a trader can count on

*One strategy shows no detectable return, and free data cannot judge the other.*

## Why test a strategy published as dead

A claim that a strategy died is one a reader acts on by leaving it alone. If the effect still works, that reader walks away from it. So the death is worth checking.

Ernest Chan’s *Quantitative Trading* works through two seasonal strategies in stocks as numbered examples with code, and reports that seasonality of this kind has faded. The first, Example 7.6, is the January effect, which he reports as failing in January 2006 and January 2007 and then working in January 2008 (Chan, 2021, p. 175). The second, Example 7.7, is a monthly rotation from a 2007 working paper by Heston and Sadka, which he publishes as dead. Its average annual return before 2002 was “more than 13 percent” before costs, and the effect “has disappeared since then” (p. 179).

Running Chan’s code on his own data files reproduces every figure it printed. That shows the code and the data agree with the book. It cannot show whether either effect died. Both files hold only the companies still in their index on the day Chan saved them.

Two later runs asked whether either effect still works. Each tested one example on its index as it stood from 2009 on. The companies that later left the index remain in the sample. Each wrote down its claim, its test and the wording of its verdict before computing any return.

![An animated whiteboard sketch titled “Which years each source reads”, drawn stroke by stroke. A grey axis runs from 1960 to 2030 with a tick at each decade. A thick black bar labelled “Heston and Sadka’s 13%, before 2002” runs to the start of 2002, with a dashed grey lead-in at its left end, and a dashed brown line at 2002 is labelled “disappeared since then”. Below it two short black bars, labelled “Chan’s files, survivors only”, run from late 1999 to late 2007 and from early 2004 to early 2008. A brown dot on the axis at 2009 is labelled “the book”, and a green bar from there to late 2026 is labelled “two later runs, index as it stood”.](../docs/figures/equity_seasonals_which_years.gif)

1. **The January effect** averages anywhere from −0.1047 to 0.0879 a January before costs, depending on index members that free data does not price.
2. **Heston and Sadka’s rotation** shows no return detectable above about 4.2 percent a year before costs, on the index members free data could price.

![An animated whiteboard sketch titled “Two verdicts”, drawn stroke by stroke, with two number lines. Each line has its own scale. The upper line, labelled “January effect, per January”, carries a brown bracket from −0.1047 to 0.0879 that straddles its zero tick, and the words “free data cannot decide”. The lower line, labelled “Heston and Sadka, per year”, carries a black dot at zero labelled “measured”, and a pale green band from zero to a brown tick labelled “about 4.2% a year”, with the words “could pass unseen” beneath it.](../docs/figures/equity_seasonals_two_verdicts.gif)

Neither run shows that the effect died, and neither gives a trader an edge to count on. The section on what this replication cannot say describes both runs and what each leaves open.

The three lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two strategies

**Example 7.6, the January effect.** It is a mean reversion trade, betting that last year’s losers recover in January and its winners give some back. At each December year-end, rank the S&P 600 small caps on their return over the calendar year. Buy the worst tenth and short the best tenth at that close, and exit both at January’s last close. The reason Chan gives is that investors sell their losers in December to claim the tax loss, and the selling pressure lifts in January (p. 175). Each trade pays two one-way costs of 5 basis points.

![An animated whiteboard sketch titled “The January trade”, drawn stroke by stroke. A long black bar labelled “a year of returns” ends at a brown dot, and a short thick brown segment one twelfth as long runs on from it, labelled “hold January”. A grey arrow labelled “rank at the year’s last close” points down to a rising row of twenty grey dots, the stocks sorted from the lowest return at the lower left to the highest at the upper right. A green ring circles the lowest two, labelled “buy the worst tenth”, and a red ring the highest two, labelled “short the best tenth”. On the right a red arrow points down, labelled “winners down”, above a green arrow pointing up, labelled “losers up”, and the words “mean reversion” close the sketch.](../docs/figures/equity_seasonals_january_trade.gif)

**Example 7.7, Heston and Sadka.** It is a seasonal momentum trade, betting the other way, that a stock’s return in a calendar month repeats in the same month the next year. At each S&P 500 month-end, rank the stocks on their return in the same calendar month a year earlier. Buy the best tenth and short the worst tenth, and hold for the month. The two scripts this repository holds turn their monthly returns into an annual return by multiplying their mean by 12, and into a Sharpe ratio by multiplying the mean over the standard deviation by √12, with no risk-free rate. The MATLAB and R in the book’s revised edition (2021) do the same.

![An animated whiteboard sketch titled “The same-month trade”, drawn stroke by stroke. Two strips of twelve cells stand one above the other, labelled “last year” and “this year”. March is outlined in brown on the upper strip and labelled “March”, and a brown arrow drops from it to March on the lower strip. The upper strip ends with the words “rank on” and the lower with “hold”. April is then outlined in grey on both strips, labelled “then April, May, …”. Below, a rising row of twenty grey dots sorts the stocks from the lowest return to the highest. A green ring circles the highest two, labelled “buy the best tenth”, and a red ring the lowest two, labelled “short the worst tenth”. On the right a green arrow points up, labelled “winners up”, above a red arrow pointing down, labelled “losers down”, and the words “seasonal momentum” close the sketch.](../docs/figures/equity_seasonals_same_month_trade.gif)

What Chan says of each is not the same, and the difference matters for what a reproduction can find.

1. **Seasonal strategies in stocks.** Much of the seasonality in equity markets “has weakened or even disappeared in recent years”, Chan writes (p. 175). The same sentence goes on to call some seasonal trades in commodity futures still profitable, and [the companion post on the commodity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md) tests that half. Earlier in the book he recalls praising a seasonal stock strategy on his blog, a reader backtesting it and finding it did not work, and his own backtest confirming the reader’s (p. 13). He names Example 7.6 as that strategy.
2. **Example 7.6.** Its own text is not a death notice. The revised edition says the January effect failed in January 2006 and January 2007 and then “worked wonderfully” in January 2008 (p. 175).
3. **Example 7.7.** This one is published as dead, in the p. 179 sentence quoted at the top of the post.

## Lesson 1: Chan’s numbers come from his code, bugs and all

All seventeen figures Chan’s code prints reproduce here to the digit. None of them comes from the strategy as the book describes it. Each needs choices that only its own script makes, and four of those choices are bugs, so matching the book means copying them. A fifth bug, in the revised MATLAB as the book prints it, stops the script on its first month and has to be repaired instead. The book’s description of each strategy fits several different numbers, and Example 7.7’s four printouts give four.

### Example 7.6, the January effect

Here is every printout of Example 7.6, at the precision each source prints, one column for each of its three Januaries. Each number is the return on one trade, held from a December year-end close to the last close of the January its column names, after the two costs. It is a fraction of the capital, split evenly between the long side and the short side. So −0.0244 is a loss of 2.44 percent over January 2006, and 0.0881 is a gain of 8.81 percent over January 2008.

```math
\begin{array}{l|r|r|r}
\text{Example 7.6 printout} & \text{January 2006} & \text{January 2007} & \text{January 2008} \\ \hline
\text{MATLAB, both editions} & -0.0244 & -0.0068 & 0.0881 \\
\text{Python, revised edition} & -0.023853 & -0.003641 & 0.088486 \\
\text{R, revised edition} & -0.0244 & -0.0068 & 0.0881
\end{array}
```

Its three printouts give two answers. The MATLAB and the R agree to every digit, and the revised Python differs. Three rules account for every figure.

1. **How many stocks make a tenth, a choice in the MATLAB.** It rounds a tenth of the ranked stocks half away from zero. Rounding down instead gives −0.0234 for January 2006.
2. **How many winners the revised Python shorts, a bug.** It slices its winners as `topN - 2` stocks rather than a full tenth, so in January 2006 it shorts 56 winners against the 58 losers it buys, of 579 ranked. Taking the full tenth gives the MATLAB’s figures for 2006 and 2007 to every digit.
3. **Whether the revised Python ranks a stock with no year-end close, a bug.** The revised Python fills a missing year-end close with the last one before it, as pandas did before version 3.0. So for 2007 it ranks PMC, which has no close at the end of 2006, on its last close before an 851-day gap in its prices. That reads the gap as a gain of 1.3056, or 130.56 percent, fourth best of 595, and the script holds PMC short. Without PMC, 594 stocks are ranked. A tenth of 595 rounds to 60 and a tenth of 594 to 59. Without the fill, January 2008 gives 0.090908. Dropping the fill and taking the full tenth together give the MATLAB’s 0.0881, so all three printouts match.

### Example 7.7, Heston and Sadka

Here is every printout of Example 7.7, whose two figures are the average annual return and the Sharpe ratio. The annual return is a fraction too, so −0.0129 is a loss of 1.29 percent a year. The first edition’s −0.9167 is not a loss of 91.67 percent a year. It is in different units, which the first rule below explains.

```math
\begin{array}{l|r|r}
\text{Example 7.7 printout} & \text{Annual return} & \text{Sharpe ratio} \\ \hline
\text{MATLAB, first edition} & -0.9167 & -0.1055 \\
\text{MATLAB, revised edition} & -0.0129 & -0.1243 \\
\text{Python, revised edition} & -0.012679 & -0.122247 \\
\text{R, revised edition} & -0.01139674 & -0.1095098
\end{array}
```

Its four printouts give four answers. The first edition’s MATLAB carries four of the rules below and the revised edition’s scripts the rest.

1. **What the first edition’s annual return sums, a bug.** It adds up every position held each month and never divides by how many there were. So −0.9167 is in units of summed positions, not a return on capital. Dividing each month by its positions puts the same script in units of capital, at −0.0120 a year, a figure computed here that Chan did not print. The three revised printouts divide.
2. **Which close keeps a stock in the first edition’s ranking, a bug.** It decides whether to keep a stock by looking at a different stock’s close, because it compares a row sorted by return with a row still in column order. Keeping each stock on its own close gives an annual return of −1.0822, in summed positions like the −0.9167 it replaces.
3. **Which months the first edition’s mean runs over, a choice.** It averages over 95 months, counting the 12 that hold no position as zero. Averaging over the 83 that hold positions gives an annual return of −1.0492, in the same units.
4. **What the first edition’s standard deviation does with a missing month, a choice.** It counts the one month with no return as zero. Skipping it gives a Sharpe ratio of −0.1049.
5. **When a stock’s month ends, a choice in the revised Python.** It reads each stock’s own last priced day in the month. One shared month-end row for every stock gives an annual return of −0.012917.
6. **What the standard deviation divides by, a choice in the revised Python and MATLAB.** The revised Python divides by the number of months, n, and dividing by n − 1 gives a Sharpe ratio of −0.121508. The revised MATLAB calls a helper, `smartstd`, whose body the book does not print, and Chan’s two books ship two versions of it. The one from his second book, *Algorithmic Trading*, divides by n and prints the −0.1243. The one from this book’s first edition divides by n − 1 and gives −0.1236.
7. **How the revised MATLAB finds a month-end, a bug repaired rather than copied.** The listing on p. 179 cuts its prices down to month-end rows and then looks one up by a daily row number, which stops on the first month. Reading the month-end row instead gives Chan’s figures. The R on p. 181 needs no repair. [A public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84) settles both points the pages leave open. Its Example 7.7 already reads the month-end row, and it ships the second book’s `smartstd`.

The three revised printouts still differ in where a month ends, how a tenth is rounded and what the standard deviation divides by, so one strategy in three languages gives three answers.

## Lesson 2: reproducing a strategy published as dead checks its figures, not its death

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

## Lesson 3: a file of survivors is the first thing the result cannot get past

Both files hold the companies in their index on the day Chan saved them, with each one’s history carried backwards. A company that left the S&P 500 in 2003, because it was acquired, shrank or failed, is not in a file saved in 2007. So every figure in the three lessons is about companies that survived to the end of the file.

Both strategies rank stocks on past returns and trade the tenth at each end, so which companies the file holds decides which companies they trade. A company the index dropped before the save is a company neither strategy could pick, whatever its returns were.

[The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) teaches survivorship in full. On two tables Chan prints for the purpose, a database of survivors turns a loss into a large gain. Heston and Sadka’s 13 percent, which covers the years before 2002, has not been tested here on a panel that keeps the companies that left.

## What this replication cannot say

Three questions are beyond it.

1. **Whether Heston and Sadka’s effect existed before 2002.** The file holds 13 months before 2002, all on survivors. Testing it needs a panel without that limit.
2. **Whether the January effect survived the book.** A second run tested Example 7.6 on the S&P 600 as it stood at each year-end, January 2009 to January 2026, so the companies that later left the index are in it. Its claim, its test and the wording of its verdict were written down before any return was computed, which makes it **registered** rather than exploratory. Free daily prices cover most of the index’s members but not all of them, and at every year-end some member with no checked price could have fallen in a traded tenth. So each January was computed twice. The low version gives each such member a return near the worst of that January if the strategy would hold it long and near the best if it would short it, and the high version does the reverse. The low series averages −0.1047 a January before costs, nowhere near above zero. The high series averages 0.0879, well above it. Free data cannot decide between them, and prices for the members that could have fallen in a traded tenth are what could.
3. **Whether Heston and Sadka’s effect survived the book.** A third run tested Example 7.7 under the revised MATLAB’s rules on the S&P 500 as it stood each month, from January 2009 to September 2026, so the companies that later left the index are in it. The membership comes from IVV, an iShares fund that holds the index and files its holdings with the SEC each quarter. Each filing’s list stands for the months until the next, so a company that joins or leaves between two filings counts as doing so at the next one. This run is **registered** too, for the same reason as the second. Free daily prices gave a checked price for 98,321 of its 107,115 member-months, each one company in one month, and the run dropped the rest, so each tenth is a tenth of the companies with a checked price. Dropping the rest is harmless only if leaving the index has little to do with where a company ranks. Among the companies kept, those that left the index within a year landed in a traded tenth more often than those that stayed, most of all in the short tenth. That comparison is described rather than tested. It counts against the drop being harmless, and which way it moves the result is not measured. The 213 months average −0.0001 a month before costs. A strategy that truly earns nothing would print a mean at least that high more than half the time, which is a one-sided p of 0.539. The revised Python’s rules give the same return in every one of the 213 months. The verdict, in the words written before the run, is “no return detectable above about 4.2% a year”. The 4.2 percent is the smallest annual return the test detects 80 percent of the time, so a smaller true return could pass unseen, and the verdict does not say the effect died. It also leaves out costs, which can only lower the return, and the last return a failing company takes as it leaves the index, which free data does not carry.

## What this means for a trader

Three habits follow from the lessons above.

1. **Reproduce a published figure with the author’s code before trusting a description of it.** Every figure here needed rules the description leaves out.
2. **Check a figure’s units before comparing two printouts.** The first edition’s −0.9167 and the revised edition’s −0.0129 come from one strategy, and only one of them is a return on capital.
3. **Do not read a survivor file as evidence that an effect died or lived.** A file saved after the fact holds the stocks that made it, and a split through 83 months of them swings with a single year.

On Chan’s own files, every printed figure his data reaches reproduces exactly. Whether the strategies died is a separate question, which these files cannot answer. For the January effect, a criterion written in advance and a panel that keeps the companies that left the index reach a bound, and the bound is too wide to read. It does not show that the effect died, and it does not show that it lived. For Heston and Sadka’s rotation, the same kind of test on the S&P 500 as it stood each month finds no return detectable above about 4.2 percent a year before costs, on the companies with a checked price. A smaller return could pass unseen, so it does not show that the effect died.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Examples 7.6 and 7.7, cited by MATLAB script as `example7_6.m` and `example7_7.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 13, 175, 179 and 180, and Examples 7.6 and 7.7 at pp. 175 to 182. Page numbers in the post are this edition’s. Its Python is cited as `example7_6.py` and `example7_7.py` at commit `653cf92` of liujiantong/epchan_books, a third-party copy whose five printed figures match the book.
- Heston, S. L., & Sadka, R. (2007), as Chan (2021, p. 179) cites them, a working paper. Published as Heston, S. L., & Sadka, R. (2008). Seasonality in the cross-section of stock returns. *Journal of Financial Economics*, 87(2), 418–445.
- Singal, V. (2006). *Beyond the Random Walk: A Guide to Stock Market Anomalies and Low-Risk Investing*. Oxford University Press. Cited by Chan (2021, p. 175) for the January effect.
- Data: two of Chan’s own MATLAB data files, converted into one file per stock. For Example 7.6, `IJR_20080131.mat` holds 600 members of the S&P 600, recorded as split-adjusted, saved 2008-02-02, spanning 2004-01-15 to 2008-02-01. For Example 7.7, `SPX_20071123.mat` holds 500 members of the S&P 500, also recorded as split-adjusted, saved 2007-11-24, spanning 1999-11-24 to 2007-11-23. The mirror of the first edition’s code and data holds only an earlier save of the S&P 600 file, `IJR_20080114.mat`, which ends on 2008-01-14. The later file comes from [a public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84), a third party’s repost rather than Chan’s own. That copy also carries the earlier save, byte for byte as the mirror has it, which is why its later file is trusted. The two saves give the first two Januaries to the same digits.

*Not investment advice. Code: [the two strategies](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals_whiteboard.py), with the checks behind [the strategies’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals_whiteboard.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-7-the-equity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
