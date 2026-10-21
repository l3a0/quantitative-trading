# Two equity seasonals show no edge a trader can count on

*One strategy shows no detectable return, and free data cannot judge the other.*

## Why test a strategy published as dead

A claim that a strategy died is one a reader acts on by leaving it alone. If the effect still works, that reader walks away from it. So the death is worth checking.

Ernest Chan’s *Quantitative Trading* works through two seasonal strategies in stocks and reports that seasonality of this kind has faded. The first, Example 7.6, is the January effect, which he reports as failing in January 2006 and January 2007 and then working in January 2008 (Chan, 2021, p. 175). The second, Example 7.7, is a monthly rotation from a 2007 working paper by Heston and Sadka, which he publishes as dead. Its average annual return before 2002 was “more than 13 percent” before costs, and the effect “has disappeared since then” (p. 179).

Running Chan’s code on his own data files reproduces every figure it printed. That shows the code and the data agree with the book. It cannot show whether either effect died. Both files hold only the companies still in their index on the day Chan saved them. A company that was acquired, shrank out of the index or failed before that day is missing, so the strategies never trade it. A backtest on such a file measures only the survivors, and the error this causes is called survivorship bias. Lesson 3 explains it and links to a post that measures how large it can be.

![An animated whiteboard sketch titled “What a saved file can see”, drawn stroke by stroke over a timeline from 1999 to 2007. Six black lines labelled “companies still in the index in 2007” run the whole way to 2007. Below them three red lines stop early, labelled “acquired”, “shrank out of the index” and “failed”. A dashed brown line at the end is labelled “Chan saves the file”. A black bracket beside the six is labelled “in the file”, and a red bracket beside the three is labelled “missing from it”.](../docs/figures/equity_seasonals_survivors_file.gif)

Two later runs asked whether either effect still works. Each tested one example on its index as it stood from 2009 on. The companies that later left the index remain in the sample wherever free data could check their price.

![An animated whiteboard sketch titled “Which years each source reads”, drawn slowly stroke by stroke. A grey axis runs from 1960 to 2030 with a tick at each decade. A thick black bar labelled “Heston and Sadka’s 13%, before 2002” runs to the start of 2002, with a dashed grey lead-in at its left end, and a dashed brown line at 2002 is labelled “disappeared since then”. Below it two short black bars run from late 1999 to late 2007, labelled “Example 7.7, S&P 500”, and from early 2004 to early 2008, labelled “Example 7.6, S&P 600”, with “Chan’s files, survivors only” beside them. A brown dot on the axis at 2009 is labelled “the book”, and a green bar from there to late 2026 is labelled “two later runs, index as it stood”. The finished drawing holds for twelve seconds.](../docs/figures/equity_seasonals_which_years.gif)

For each, this repository wrote down the claim, the test and the wording of the verdict before computing any return. A result tested that way is called registered, and only a registered result can confirm an effect. A result computed first and judged afterwards is exploratory. It can kill an idea or justify a closer look, but it carries no verdict.

![An animated whiteboard sketch titled “What registered means”, drawn stroke by stroke. Three boxes joined by arrows, “claim”, “test” and “verdict’s words”, stand before a dashed brown line labelled “all written down”, and past it a green box reads “then returns computed”. The word “registered” heads that row. Below the row, a red box “returns computed” leads to a box “no claim written down first”, under the word “exploratory”. The words “exploratory can kill an idea, only registered can confirm one” close the sketch.](../docs/figures/equity_seasonals_january_registered.gif)

The two later runs found the following.

1. **The January effect** averages between −0.1047 and 0.0879 a January before costs, a loss of 10.47 percent to a gain of 8.79 percent, depending on how the index members whose prices free data cannot check are filled in.
2. **Heston and Sadka’s rotation** shows no return detectable above about 4.2 percent a year before costs, on the index members with a checked price. The test catches a true return that large four times in five, so a smaller one could pass unseen.

![An animated whiteboard sketch titled “Two verdicts”, drawn slowly stroke by stroke, with two number lines. Each line has its own scale. The upper line, labelled “January effect” and “per January”, has a zero tick, “0”, and a brown bracket from “−0.1047” to “0.0879” that straddles it, with the words “free data cannot decide”. The lower line, labelled “Heston and Sadka” and “per year”, has its own “0”, a pale green band from zero to a brown tick labelled “about 4.2% a year”, and a black dot at zero labelled “measured”, with the words “could pass unseen” beneath the band. A red arrow under the band points back toward zero and stops halfway, labelled “costs lower it, not measured”. The words “not shown dead, and no edge a trader can count on” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_two_verdicts.gif)

Neither run shows that the effect died, and neither gives a trader an edge to count on. The section on what later data can and cannot say describes both runs and what each leaves open.

The reproduction teaches three lessons, each with its own section below:

1. Account for every choice and every bug, or one strategy gives several answers.
2. To test whether an effect died, fix the criterion and the sample first.
3. Rule out survivorship bias before trusting a backtest.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two strategies

**Example 7.6, the January effect.** It is a **mean reversion** trade, betting that last year’s losers recover in January and its winners give some back. At each December year-end, rank the S&P 600, an index of 600 smaller US companies, on their return over the calendar year. Buy the worst tenth and short the best tenth at that close, and exit both at January’s last close. The bought stocks are the long side. Shorting means selling borrowed shares, so the short side gains when its stocks fall. The reason Chan gives is that investors sell their losers in December to claim the tax loss, and the selling pressure lifts in January (p. 175). Each trade pays a cost of 5 basis points, or 0.05 percent, to enter and another 5 to exit.

![An animated whiteboard sketch titled “The January trade”, drawn stroke by stroke. A long black bar labelled “a year of returns” ends at a brown dot, and a short thick brown segment one twelfth as long runs on from it, labelled “hold January”. A grey arrow labelled “rank at the year’s last close” points down to a rising row of twenty grey dots, the stocks sorted from the lowest return at the lower left to the highest at the upper right. A green ring circles the lowest two, labelled “buy the worst tenth”, and a red ring the highest two, labelled “short the best tenth”. On the right a green arrow pointing up, labelled “losers up”, sits below a red arrow pointing down, labelled “winners down”, and the words “mean reversion” close the sketch.](../docs/figures/equity_seasonals_january_trade.gif)

**Example 7.7, Heston and Sadka.** It is a **seasonal momentum** trade, betting the other way, that a stock’s return in a calendar month repeats in the same month the next year. At each S&P 500 month-end, rank the stocks on their return in the same calendar month a year earlier. Buy the best tenth and short the worst tenth, and hold for the month.

![An animated whiteboard sketch titled “The same-month trade”, drawn stroke by stroke. Two strips of twelve cells stand one above the other, labelled “last year” and “this year”. March is outlined in brown on the upper strip and labelled “March”, and a brown arrow drops from it to March on the lower strip. The upper strip ends with the words “rank on” and the lower with “hold”. April is then outlined in grey on both strips, labelled “then April, May, …”. Below, a rising row of twenty grey dots sorts the stocks from the lowest return to the highest. A green ring circles the highest two, labelled “buy the best tenth”, and a red ring the lowest two, labelled “short the worst tenth”. On the right a green arrow points up, labelled “winners up”, above a red arrow pointing down, labelled “losers down”, and the words “seasonal momentum” close the sketch.](../docs/figures/equity_seasonals_same_month_trade.gif)

Each of Chan’s scripts for Example 7.7 turns its monthly returns into an annual return and a Sharpe ratio as below. The **Sharpe ratio** is return per unit of risk: the average return divided by its standard deviation, the typical size of a month’s swing around that average. Chan’s scripts subtract no risk-free rate, the return on cash, before dividing. Here `r̄` is the mean monthly return and `s` its standard deviation.

```math
\begin{aligned}
\text{annual return} &= 12\,\bar{r} \\
\text{Sharpe ratio} &= \sqrt{12}\,\frac{\bar{r}}{s}
\end{aligned}
```

Chan says something different about seasonal stock strategies in general and about each example.

1. **Seasonal strategies in stocks.** Much of the seasonality in equity markets “has weakened or even disappeared in recent years”, Chan writes (p. 175). The same sentence goes on to call some seasonal trades in commodity futures still profitable, and [the companion post on the commodity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md) tests that half. Earlier in the book he recalls praising a seasonal stock strategy on his blog, a reader backtesting it and finding it did not work, and his own backtest confirming the reader’s (p. 13). He names Example 7.6 as that strategy.
2. **Example 7.6.** Its own text is not a death notice. The revised edition says the January effect failed in January 2006 and January 2007 and then “worked wonderfully” in January 2008 (p. 175).
3. **Example 7.7.** This one is published as dead, in the p. 179 sentence quoted at the top of the post.

## Lesson 1: Account for every choice and every bug, or one strategy gives several answers

Chan’s book has two editions. The first, from 2009, gives Examples 7.6 and 7.7 in MATLAB. The revised edition, from 2021, gives each in MATLAB, Python and R. This post names each script by its language and edition, so “the revised Python” is the Python from the revised edition.

All seventeen figures Chan’s code prints reproduce here to the digit, but only by copying his code. The book’s description of each strategy fits several numbers, and each script picks one through rules the description leaves out. Seven of those rules are bugs. Matching the printed figures means copying six of them. The seventh, in the revised MATLAB as the book prints it, stops the script on its first pass and has to be repaired instead.

So a backtest that misses a published figure may differ only in rules like these. Here are the twelve rules, under eleven headings, each marked as a choice or a bug:

- **Example 7.6**
   1. Rounding a tenth, a choice.
   2. Two fewer winners shorted, a bug.
   3. A filled-in close, a bug.
- **Example 7.7**
   1. Summing without dividing, a bug.
   2. The wrong stock’s close, a bug.
   3. Empty months in the mean, a bug.
   4. A missing month as zero, a bug.
   5. Each stock’s own month-end and which stocks it keeps, two choices.
   6. Rounding halves to even, a choice.
   7. Dividing by n or n − 1, a choice.
   8. The month-end lookup, a bug repaired.

### Example 7.6, the January effect

Here is every printout of Example 7.6, at the precision each source prints, one row for each of its three Januaries and one column for each script. The MATLAB column holds both editions, which print the same figures, and the Python and R columns hold the revised edition’s. Each number is the return on one trade, held from a December year-end close to the last close of the January its row names, after a cost of 5 basis points to enter and another 5 to exit. It is a fraction of the capital, split evenly between the long side and the short side. So −0.0244 is a loss of 2.44 percent over January 2006, and 0.0881 is a gain of 8.81 percent over January 2008.

```math
\small\begin{array}{l|r|r|r}
\text{January} & \text{MATLAB} & \text{Python} & \text{R} \\ \hline
2006 & -0.0244 & -0.023853 & -0.0244 \\
2007 & -0.0068 & -0.003641 & -0.0068 \\
2008 & 0.0881 & 0.088486 & 0.0881
\end{array}
```

Its three printouts give two answers. The MATLAB and the R agree to every digit, and the revised Python differs. Three rules account for every figure.

#### Rule 1: rounding a tenth, a choice in the MATLAB

A tenth of the 578 stocks it ranks for January 2006 is 57.8, and it rounds that to 58, so it buys the 58 worst and shorts the 58 best.

```math
\begin{gathered}
\frac{578}{10} = 57.8 \\
\text{rounded: } 58 \\
\text{rounded down: } 57
\end{gathered}
```

Rounding down to 57 of each gives −0.0234 instead of the printed −0.0244.

#### Rule 2: two fewer winners shorted, a bug in the revised Python

It slices its winners as `topN - 2` stocks rather than a full tenth, so in January 2006 it shorts 56 winners against the 58 losers it buys, of 579 ranked, one more than the MATLAB’s 578, because of the fill rule 3 describes. Taking the full tenth gives the MATLAB’s figures for 2006 and 2007 to every digit.

![An animated whiteboard sketch titled “Two fewer winners shorted”, drawn slowly stroke by stroke. A green bar labelled “buy the 58 worst” sits above a red bar labelled “short 56 of the 58 best”. A dashed brown line labelled “a tenth: 58” marks where the green bar ends, and the red bar stops two stocks short of it. A dashed grey segment fills the difference, labelled “2 left out: the best and the 58th”. Beneath them are the words “the winners are sliced as topN − 2” and “January 2006, 579 stocks ranked”. The finished drawing holds for twelve seconds.](../docs/figures/equity_seasonals_rule_short_side.gif)

#### Rule 3: a filled-in close, a bug in the revised Python

The revised Python fills a missing year-end close with the last close before it, as pandas, Python’s data library, did by default before version 3.0. One stock in the file, PMC, has no close in 2005 or 2006. Its last close before then, 6.02, comes before a gap of 851 trading days in its prices, and its close at the end of 2007 is 13.88. The fill carries 6.02 through both missing year-ends, so the script ranks PMC for January 2006 and January 2007 at a return of zero. That is the one extra stock rule 2 counts. For January 2008 it ranks PMC as if it rose from 6.02 to 13.88, a gain of 1.3056, or 130.56 percent. That is fourth best of 595, so the script holds PMC short. Without the fill, PMC drops out, and a tenth of the 594 left rounds to 59 rather than 60. Dropping the fill alone gives 0.090908 for January 2008. Dropping it and also taking rule 2’s full tenth gives the MATLAB’s 0.0881, so all three printouts match.

![An animated whiteboard sketch titled “PMC’s filled close”, drawn stroke by stroke. A grey axis runs from 2004 to 2008. A short black price line labelled “PMC” sits in early 2004, and a dashed grey line carries it flat, under the words “last close 6.02, then 851 trading days with no price”, to a brown dot at the start of 2007, labelled “end of 2006”. A second short black price line runs from August 2007 into 2008 and passes a brown dot near the end of 2007, labelled “13.88”. A red arrow climbs from the first dot to the second, beside the words “+130.56% read as 2007’s gain” and “4th best of 595: shorted”.](../docs/figures/equity_seasonals_rule_filled_close.gif)

### Example 7.7, Heston and Sadka

Here is every printout of Example 7.7, whose two figures are the average annual return and the Sharpe ratio. The annual return is a fraction too, so −0.0129 is a loss of 1.29 percent a year. The first edition’s −0.9167 is not a loss of 91.67 percent a year. It is in different units, which the first rule below explains.

```math
\small\begin{array}{l|r|r}
\text{Example 7.7} & \text{Annual return} & \text{Sharpe ratio} \\ \hline
\text{MATLAB, first} & -0.9167 & -0.1055 \\
\text{MATLAB, revised} & -0.0129 & -0.1243 \\
\text{Python, revised} & -0.012679 & -0.122247 \\
\text{R, revised} & -0.01139674 & -0.1095098
\end{array}
```

Its four printouts give four answers. Rules 1 to 4 are in the first edition’s MATLAB, and the rest name the revised script each belongs to. The three revised printouts differ in four ways:

1. Where a month ends.
2. Which stocks a month keeps.
3. How a tenth is rounded.
4. What the standard deviation divides by.

So one strategy in three languages gives three answers.

#### Rule 1: summing without dividing, a bug in the first edition

It adds up every position held each month and never divides by how many there were. Write `rᵢ,ₜ` for the return of position `i` in month `t`, signed so that a short gains when its stock falls, and `Nₜ` for the number of positions that month.

```math
\begin{aligned}
\text{first edition's month } t &= \sum_{i=1}^{N_t} r_{i,t} \\
\text{revised month } t &= \frac{1}{N_t} \sum_{i=1}^{N_t} r_{i,t}
\end{aligned}
```

So −0.9167 is a sum over positions, not a return on capital. Dividing each month by its positions puts the same script in units of capital, at −0.0105 a year, a figure computed here that Chan did not print. The three revised printouts divide.

![An animated whiteboard sketch titled “Add up, or average”, drawn stroke by stroke. Eight thin bars hang up and down from a line, labelled “one month’s N positions”. A grey arrow leads to a long black bar below the line, labelled “first edition: add them up” and “summed positions”, and beside it a short brown bar labelled “revised: ÷ N” and “capital”. The words “each month is N times too big” close the sketch.](../docs/figures/equity_seasonals_rule_sum_or_mean.gif)

#### Rule 2: the wrong stock’s close, a bug in the first edition

The script sorts the stocks by return, then checks each one for a missing close. It finds that close by position in the file’s column order rather than by stock. So the check for the stock in third place reads whichever stock sits in the third column. A stock can be dropped because another has no close, and a stock with no close can stay in. Keeping each stock on its own close gives an annual return of −1.0822, a sum over positions like the −0.9167 it replaces. Dividing each month by its positions turns that into −0.0113 a year in units of capital.

![An animated whiteboard sketch titled “Checking the wrong stock’s close”, drawn stroke by stroke. A row of five cells labelled “sorted by return” holds D, B, E, A and C. Below it a row labelled “column order” holds A, B, C, D and E, with a red cross under C labelled “no close”. Grey arrows join each upper cell to the cell beneath it, and a red arrow rises from C to E. A red ring circles E, labelled “E dropped: C has no close”, and a brown ring circles C in the upper row, labelled “C ranked anyway”. The words “each check reads the column, not the stock” close the sketch.](../docs/figures/equity_seasonals_rule_wrong_close.gif)

#### Rule 3: empty months in the mean, a bug in the first edition

It averages over 95 months, counting as zero the 12 that hold no position because the ranking does not yet have its year of history. The revised edition drops those months. The 12 add nothing to the summed monthly returns, so dropping them leaves that sum unchanged and divides it by 83 instead of 95. The annual return is twelve times the monthly mean, so write `S` for twelve times the sum. The annual return is then S/95 before the drop and S/83 after it.

```math
\frac{S}{83} = \frac{S}{95} \times \frac{95}{83}
```

Multiplying the old annual return by 95/83 cancels its 95. `S` is −87.08 as a sum over positions and −0.9944 in rule 1’s units of capital:

```math
\begin{aligned}
&\text{as a sum over positions:} \\
&\quad \frac{-87.08}{95\llap{\rule[0.32em]{1.05em}{0.06em}}} \times \frac{95\llap{\rule[0.32em]{1.05em}{0.06em}}}{83} = \frac{-87.08}{83} = -1.0492 \\
&\text{in rule 1's units of capital:} \\
&\quad \frac{-0.9944}{95\llap{\rule[0.32em]{1.05em}{0.06em}}} \times \frac{95\llap{\rule[0.32em]{1.05em}{0.06em}}}{83} = \frac{-0.9944}{83} = -0.0120
\end{aligned}
```

![An animated whiteboard sketch titled “Which months the mean counts”, drawn stroke by stroke. A row of 96 dots runs across the board: a hollow grey dot labelled “month 1: no return”, then 12 grey dots labelled “12 months with no position, each a 0”, then 83 black dots labelled “83 months that hold positions”. A black bracket under months 2 to 96 is labelled “first edition: sum ÷ 95”, and a brown bracket under the last 83 is labelled “revised: sum ÷ 83”.](../docs/figures/equity_seasonals_rule_empty_months.gif)

#### Rule 4: a missing month as zero, a bug in the first edition

Month 1 has no return. The first edition’s mean skips it, but its standard deviation counts it as zero.

```math
\begin{aligned}
\bar{r} &= \frac{1}{95} \sum_{t=2}^{96} r_t \quad \text{month 1 skipped} \\
s &= \operatorname{std}(0, r_2, \dots, r_{96}) \\
&\quad \text{month 1 counted as } 0
\end{aligned}
```

Skipping it in both gives a Sharpe ratio of −0.1049, against the printed −0.1055.

#### Rule 5: each stock’s own month-end and which stocks it keeps, two choices in the revised Python

The revised Python reads each stock’s own last priced day in the month, and the revised MATLAB reads one shared month-end row for every stock. They also keep a stock in the ranking differently. The Python keeps one that has a return, and the MATLAB one that has a close. Run with one shared month-end, the Python gives an annual return of −0.012917. The MATLAB gives the same figure when it keeps a stock on its return rather than its close. So these two choices are what separate the two scripts.

![An animated whiteboard sketch titled “Where a month ends”, drawn stroke by stroke. A pale green column labelled “shared month-end row” covers the last of five trading days. Stock A has a dot on all five days. Stock B has dots on the first three, a green ring round the third, and a red cross labelled “missing” in the shared column. The words “B’s own last priced day, which the revised Python reads” and “the month’s last five trading days” sit below.](../docs/figures/equity_seasonals_rule_own_month_end.gif)

#### Rule 6: rounding halves to even, a choice in the revised R

It rounds a tenth to the nearest whole number, and sends an exact half to the even neighbour.

```math
\begin{array}{r|r|r|r}
\text{A tenth} & \text{R's rounding} & \text{Half up} & \text{Down} \\ \hline
47.5 & 48 & 48 & 47 \\
48.5 & 48 & 49 & 48
\end{array}
```

On this file some months land on a half, so the half matters. Rounding every half up, as school rounding does, gives an annual return of −0.0118031. Rounding down, as the revised MATLAB and Python do, gives the revised MATLAB’s annual return.

#### Rule 7: dividing by n or n − 1, a choice in all three revised scripts

The standard deviation of `n` monthly returns divides their summed squared deviations from the mean by `n` or by `n − 1`.

```math
\begin{aligned}
s_n &= \sqrt{\frac{1}{n} \sum_{t=1}^{n} (r_t - \bar{r})^2} \\
s_{n-1} &= \sqrt{\frac{1}{n-1} \sum_{t=1}^{n} (r_t - \bar{r})^2}
\end{aligned}
```

The revised Python divides by the number of months, `n`, and dividing by `n − 1` gives a Sharpe ratio of −0.121508. The revised R divides by `n − 1`, and dividing by `n` gives −0.1101755. The revised MATLAB calls a helper, `smartstd`, whose body the book does not print, and Chan’s two books ship two versions of it. The one from his second book, *Algorithmic Trading*, divides by `n` and prints the −0.1243. The one from this book’s first edition divides by `n − 1` and gives −0.1236.

#### Rule 8: the month-end lookup, a bug repaired in the revised MATLAB

The listing on p. 179 keeps only the 96 month-end rows, then looks each month up by its row number among the daily rows. On its first pass it asks for row 258, past the end of the 96, and stops. Reading the month-end row instead, which on the first pass is row 13, with the second book’s `smartstd`, gives Chan’s figures. The R on p. 181 needs no repair. The pages leave two questions open: whether the script Chan ran reads the month-end row, and which `smartstd` it calls. [A public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84) answers both. Its Example 7.7 already reads the month-end row, and it ships the second book’s `smartstd`.

![An animated whiteboard sketch titled “A lookup past the end”, drawn stroke by stroke. A strip of cells labelled “96 month-end rows” runs from “row 1” to “row 96”. A dashed grey line continues past its end to a red cross labelled “row 258”, with the words “the first pass asks for it and stops”. A green arrow points up near the strip’s left end, at row 13 of 96, labelled “the repair reads row m − 1, here 13”.](../docs/figures/equity_seasonals_rule_month_end_lookup.gif)

## Lesson 2: To test whether an effect died, fix the criterion and the sample first

Every printout’s whole-period figure for Example 7.7 is negative on Chan’s file, as he printed it. That is consistent with an effect that died. It is also consistent with one that never lived on these stocks over these years. A reproduction cannot tell those apart, for three reasons.

### Why a reproduction cannot decide it

1. **This repository wrote no criterion for “disappeared” first.** A claim that an effect “disappeared” needs a test stated before any number is seen: which statistic, over which periods, crossing which bar. The repository’s rule is that a figure computed before its criterion carries no verdict, and it computed the split below first.
2. **The file barely reaches the period before.** The S&P 500 file starts on 1999-11-24. After the twelve months the ranking needs, it holds 13 months before 2002.
3. **The 13 percent comes from a sample this file does not hold.** Heston and Sadka measured it on NYSE- and AMEX-listed stocks in CRSP, the Center for Research in Security Prices’ database of US stock returns, from January 1965 to December 2002. Each month they used only the firms listed by then, so firms that later failed or delisted stay in, which reduces the survivorship bias that Lesson 3 describes. Ranked on the return a year earlier, their best tenth beat their worst by 1.15 percent a month before costs, about 13.8 percent a year, which fits Chan’s “more than 13 percent”. Running the same rule on Chan’s file is no test of that figure, because the file differs from their sample in several ways at once.
   - It holds only the 500 companies still in the S&P 500 when Chan saved it in 2007, so no firm that left is in it.
   - Those are large companies on any exchange, where theirs are NYSE and AMEX stocks of every size.
   - It reaches back only to late 1999.
   - Its closes are split-adjusted, and the file does not say how it treats dividends, where CRSP’s returns include them.
   - Chan’s revised scripts divide each month by every position, long and short together, so they earn half the gap between the best tenth and the worst that Heston and Sadka report.

The last difference comes from how each month is computed. Example 7.7 buys `n` stocks from the best tenth and shorts `n` from the worst. Write `rᵢ` for stock `i`’s return that month. A short gains when its stock falls, so a shorted stock’s return enters with its sign flipped, and Chan’s revised month divides the sum by all `2n` positions:

```math
\begin{aligned}
\text{Chan's month} &= \frac{1}{2n}\Big(\sum_{\text{best}} r_i - \sum_{\text{worst}} r_i\Big) \\
&= \frac{1}{2}\big(\bar r_{\text{best}} - \bar r_{\text{worst}}\big) \\
&= \frac{1}{2} \times \text{gap}
\end{aligned}
```

Each barred term is a tenth’s average return, and the difference between them is the gap Heston and Sadka report, what a dollar bought and a dollar shorted earn together. Chan spreads one dollar across both sides, half on each, so his month earns half the gap.

### The split at 2002

What the file can give is a split, and it is **exploratory, with no verdict**. The revised Python keeps 83 months for its statistics, from December 2000 to October 2007. Cut at the start of 2002:

```math
\small\begin{array}{l|r|r}
\text{Revised Python} & \text{Before 2002} & \text{From 2002} \\ \hline
\text{Months} & 13 & 70 \\
\text{Annual return} & -0.145387 & 0.011967 \\
\text{Sharpe ratio} & -0.859993 & 0.141777
\end{array}
```

On this file of survivors, the strategy lost money before 2002 and made a little after it. That runs the opposite way to the published story. Only the revised Python’s series is split here.

The figure below adds up the 83 months one at a time, so the line rises in a month that made money and falls in one that lost it. The slope of a stretch is its average monthly return, so a steep rise means large gains and a steep fall large losses.

![A line chart of the running sum of Example 7.7’s monthly returns under the revised edition’s Python rules, from December 2000 to October 2007, in fractions of capital. A dashed vertical line marks the start of 2002. To its left, labelled 13 months before 2002 at −0.145387 a year and a Sharpe ratio of −0.859993, the line falls through 2001. To its right, labelled 70 months from 2002 at 0.011967 a year and a Sharpe ratio of 0.141777, the line climbs steeply through 2002, swings up and down through 2003 to 2005, peaks in January 2006, and falls to end below zero. The title calls the split an exploratory cut with no verdict, and the note names Chan’s S&P 500 file, which holds only survivors.](../docs/figures/equity_seasonals_split.png)

*The running sum climbs through 2002, peaks in January 2006 and falls to the end of the file. The labels give each half’s annual return and Sharpe ratio.*

The 70 months from 2002 are not a steady small gain. Between the climb through 2002 and the peak in January 2006, their running sum slips through 2003 and 2004. Two single years inside them sit further apart than the two halves do. The best full year, 2002, adds up to a gain of 0.2227 and the worst, 2006, to a loss of 0.1319, so they are 0.3546 apart. The two halves’ annual returns, −0.145387 and 0.011967, are only 0.1574 apart. Without 2002, the other 58 months from 2002 lose 0.031640 a year, so the small gain after 2002 rests on that one year.

![An animated whiteboard sketch titled “Two years sit further apart than the halves”, drawn stroke by stroke, with bars to one scale. On the left, under “the two halves, an average year”, a red bar labelled “before 2002” hangs below a zero line to −0.145387, and a short green bar labelled “from 2002” rises to +0.011967. A brown bracket beside them is labelled “0.1574 apart”. On the right, under “two single years, 12 months each”, a tall green bar labelled “2002” rises to +0.2227, and a red bar labelled “2006” hangs to −0.1319. A brown bracket more than twice as long is labelled “0.3546 apart”. The words “before costs” close the sketch.](../docs/figures/equity_seasonals_split_swing.gif)

### Chan’s five-year claim

Chan makes one claim about timing that the file can check. He suggests running the program on “the most recent five years instead of the entire data period” and says the average returns are even worse (p. 180).

This repository wrote the check down before computing any five-year figure. The running-sum figure above was already published then, so the shape of those years was in view, and the check was chosen because it runs Chan’s program exactly as his sentence says. The file ends on 2007-11-23, so its most recent five years start after 2002-11-23. Rerun the revised MATLAB’s rules unchanged on the rows after that date, and call the claim reproduced if the annual return comes out below the whole period’s. The first year of those rows only builds the ranking’s history, so the rerun keeps 47 months, from December 2003 to October 2007, and returns −0.0165 a year against the whole period’s −0.0129. The claim holds on this file. The check is still exploratory, because those months had already been computed and drawn in the running-sum figure. Writing its criterion first lets it say whether Chan’s comparison holds on his file, and nothing more. Under the revised Python’s rules, reported beside it with no verdict, the figures are −0.016431 and −0.012679.

That sits beside the split without contradicting it. The 70 months from 2002 include 23, from January 2002 to November 2003, that the five-year rerun leaves out. Under the revised Python’s rules those 23 return 0.069997 a year, also an exploratory figure. Without them, the months that remain lose money.

![An animated whiteboard sketch titled “Which months each figure covers”, drawn slowly stroke by stroke over a timeline from 2001 to 2007. A black bar for the whole period is labelled “whole period: 83 months, −0.012679”. Below it the split’s two bars meet at the start of 2002: a short red one labelled “before 2002: 13 months, −0.145387” and a long green one labelled “from 2002: 70 months, +0.011967”. Below that the five-year rerun starts with a dashed grey stretch from late 2002 to late 2003, labelled “first year only ranks”, then a brown bar to the end, labelled “five-year rerun: 47 months, −0.016431”. A green bracket from the start of 2002 to the start of the brown bar is labelled “23 months the rerun leaves out: +0.069997”. The words “revised Python’s rules, a year, before costs” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_five_year_months.gif)

The five-year result is narrow. The gap between the two figures is 0.0036 a year, and the rerun’s annual return has a standard error of 0.0281 a year, about eight times larger. A standard error is how far a measured average typically lands from the true one by chance alone, so a gap eight times smaller than it is well inside the noise. So the check shows that Chan’s comparison holds on his own file of survivors. It does not show that the effect weakened.

![An animated whiteboard sketch titled “A gap far smaller than the noise”, drawn slowly stroke by stroke. A number line runs from below −0.04 to above 0, with ticks at −0.04, −0.02 and 0. A pale green band labelled “one standard error each way, 0.0281” stretches from about −0.045 to about +0.012 around a brown dot labelled “five-year rerun −0.0165”. Beside it a black dot is labelled “whole period −0.0129”. A small red bracket above the two dots is labelled “0.0036 apart”. The words “revised MATLAB’s rules, a year, before costs” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_five_year_noise.gif)

### Example 7.6’s three Januaries

Example 7.6 meets the same limit from another side. All three of its Januaries reproduce: the two that lost, and January 2008, the one Chan’s text says “worked wonderfully” (p. 175), at 0.0881 in both editions’ MATLAB and the revised R and 0.088486 in the revised Python. One winning January after two losing ones, on a file of survivors, is three trades. They show that Chan’s code and data agree with his book, and they say nothing about whether the January effect lives.

![An animated whiteboard sketch titled “Three Januaries are three trades”, drawn stroke by stroke. Three bars stand on a grey zero line: a short red bar hanging to −0.0244 labelled “January 2006”, a shorter red bar hanging to −0.0068 labelled “January 2007”, and a tall green bar rising to +0.0881 labelled “January 2008”. The words “three trades” sit to the right, and “Example 7.6 in MATLAB, after costs” closes the sketch.](../docs/figures/equity_seasonals_five_year_januaries.gif)

## Lesson 3: Rule out survivorship bias before trusting a backtest

The opening named the bias: Chan’s files hold only the companies still in their index on the day he saved them. Each company in them has its prices carried back to the start of the file, so a company that left the S&P 500 in 2003, because it was acquired, shrank or failed, is not in a file saved in 2007.

Both strategies trade the tenth at each end of a ranking, so a company missing from the file is one they could never trade, whatever its returns were. Every figure this post computes from Chan’s files is about companies that survived to the end of the file.

![An animated whiteboard sketch titled “The ranking only sees survivors”, drawn slowly stroke by stroke. A row labelled “as it stood” ranks twenty stocks from “lowest return” to “highest”, three of them drawn as red rings, and a dashed grey ring round the lowest two is labelled “worst tenth”. Below it a row labelled “in the file” holds the same stocks without the three, and a brown ring round its lowest two is labelled “the file’s worst tenth: a different set”. The words “red rings: companies that left the index before the file was saved” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_survivors_ranking.gif)

[The post on survivorship and transaction costs](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) shows how large the bias can be: on two tables Chan prints for the purpose, a database of survivors turns a loss into a large gain. Chan’s rule has not been run here on 1965 to 2002 with the companies that left the index kept in. Open Source Asset Pricing’s version of the signal has been, as the section on whether Heston and Sadka’s effect existed before 2002 describes. The two later runs kept those companies too, but only from 2009.

![An animated whiteboard sketch titled “Two ways to build the data”, drawn slowly stroke by stroke. On the left, under “a file saved in 2007”, six black lines and one green line run the full width, the green one labelled “joined later, carried back”, with “2007’s members, carried back” beneath. On the right, under “the index as it stood”, the same six black lines run the full width, a green line labelled “joined” starts partway, and two red lines labelled “left” stop early, with “members at each ranking date” beneath. The words “the later runs, from 2009, used the data on the right” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_survivors_panels.gif)

## What later data can and cannot say

Three open questions:

1. Whether the January effect survived the book.
2. Whether Heston and Sadka’s effect existed before 2002.
3. Whether Heston and Sadka’s effect survived the book.

To survive the book means to keep working after the book’s first edition, which came out in November 2008 with a 2009 date. The two later runs test the years from January 2009.

### Whether the January effect survived the book

#### How the run was built

The first later run, the January run below, tested Example 7.6 on the S&P 600 as it stood at each year-end, January 2009 to January 2026, so the companies that later left the index are in it. The membership comes from IJR, an iShares fund that holds the index and files its holdings with the SEC.

Before any return was computed, this repository wrote down the claim, the test and the wording of every possible verdict, so the run is registered rather than exploratory. The claim is about μ, the true average January return of Example 7.6 before costs in the years after the book. The 18 Januaries from 2009 to 2026 are a sample of those years. The test starts from H₀, that the strategy earns nothing in January, and asks whether the data favour H₁, that μ is above zero:

```math
H_0: \mu = 0 \qquad \text{against} \qquad H_1: \mu > 0
```

It is a one-sided t-test on the 18 Januaries. One-sided means only an average above zero counts as an effect. The t-statistic is the average divided by its standard error, so it counts how many standard errors the average sits above zero. Its p value is the chance that a strategy that truly earns nothing in January would give a t-statistic at least as high as the one measured. A p below 0.05 rejects H₀ and so finds a January effect.

#### Which prices it could check

Free daily prices cover most of the index’s members but not all of them. A member’s price counts as checked only when it agrees with the fund’s filing, to within the filing’s rounding. The close is the free price on the filing’s date, and the shares and the value are what the filing lists for that member:

```math
\text{close} \times \text{shares} = \text{value}
```

That match is what shows the price belongs to that company and not to a later one using the same ticker. A member that was also in the filing a year earlier must pass the same check there, because its ranking starts from that year-end’s close.

#### Filling the members it could not check

At every year-end some member with no checked price could have fallen in a traded tenth. Leaving those members out would rank each year on a different set of stocks than the strategy would really have traded, a version of the problem Lesson 3 describes in Chan’s files. Their returns are unknown, and a single guess would give a false impression of accuracy.

A lower and an upper bound show how far the answer could move, so each January was computed twice, once near each extreme. The low version is close to the worst case for the strategy. Each such member it would hold long gets a return near the worst of that January, and each it would short gets one near the best. The high version is close to the best case and does the reverse. If both versions gave the same test result, that result would be the verdict.

![An animated whiteboard sketch titled “Two ways to fill a gap”, drawn slowly stroke by stroke. A row of twenty ranked stocks has a green ring round its lowest two, labelled “buy the worst tenth”, and a red ring round its highest two, labelled “short the best tenth”. Above the row a question mark, labelled “a member with no checked price”, sends a grey arrow to each ring, and beneath the row are the words “could land in a traded tenth”. To the right, in red, “low version”, then “if bought: near the worst January return” and “if shorted: near the best”. Below it, in green, “high version”, then “if bought: near the best January return” and “if shorted: near the worst”. The words “so each January gets a low and a high result” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_january_fill.gif)

#### What the run found

Each version goes through the same test. The low series averages −0.1047 a January before costs, with a p of 1.000, so it shows no sign of an effect. The high series averages 0.0879, with a p of 0.001, which rejects H₀ and would read as a January effect on its own.

![An animated whiteboard sketch titled “Eighteen Januaries, each a range”, drawn slowly stroke by stroke. Eighteen vertical bars stand along a grey zero line from 2009 to 2026, each running from that January’s low version to its high, under the words “each bar runs from a January’s low version to its high”. The bars are tallest in the first years and shrink to almost nothing by 2026. Most are black and straddle zero. The bars for 2020, 2021 and 2024 are red and sit wholly below zero, and the bar for 2023 is green and sits wholly above it. The words “black: straddles zero, so free data cannot tell which side” and “before costs” follow. Then a brown dot appears beside each bar, at that January’s return with the unchecked members left out, and every dot falls inside its bar’s range. The words “brown dot: the unchecked members left out” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_january_ranges.gif)

#### What the verdict says

The wording written before the run covers three outcomes.

1. **Both versions reject H₀.** The verdict is a January effect above zero.
2. **Neither rejects.** The verdict is no January effect detectable above some size X, the smallest average the test would catch 80 percent of the time.
3. **One rejects and the other does not.** The verdict is that the free sources cannot decide it.

The two versions disagree, so the verdict is the third. Free data cannot decide whether the January effect survived the book. Prices for the members that could have fallen in a traded tenth are what could decide it.

Leaving the unchecked members out, with each tenth taken of the checked members alone, averages −0.0083, near zero and between the two. That figure carries the survivorship bias described above, and no rule for it was written before the run, so it is exploratory rather than registered.

#### What 18 Januaries can detect

A second limit would remain even with every price checked. Example 7.6 trades once a year, so its test has only 18 numbers to work with. On the two versions’ spreads, the smallest average January the test would catch four times in five is 0.0547 for the low version and 0.0615 for the high one, a gain of about 5.5 to 6.2 percent each January. A true effect smaller than that could pass unseen. Two of Chan’s own three Januaries, −0.0244 and −0.0068, are smaller than that in size, and so is their mean, 0.0190. Only 0.0881 is larger. The section on where Heston and Sadka’s 4.2 percent comes from, further down, works the same calculation through step by step.

![An animated whiteboard sketch titled “What eighteen Januaries can catch”, drawn slowly stroke by stroke. A grey number line runs from below −0.04 to above 0.08, with ticks labelled “−0.04”, “0”, “0.04” and “0.08”. A pale green tint runs from about −0.055 to about 0.055, labelled “could pass unseen”. Above its right end a brown bracket is labelled “0.0547 to 0.0615” and “caught four times in five”. Two red dots sit inside the tint below zero, labelled “2006: −0.0244” and “2007: −0.0068”, and a green dot sits past the bracket, labelled “2008: +0.0881”. A black mark inside the tint, at the three’s average, is labelled “their mean: +0.0190”. A two-line key, “dots: Chan’s three Januaries, one trade each, after costs” and “bracket: what the registered run’s 18 Januaries catch, before costs”, closes the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_january_catch.gif)

Settling the January effect needs more Januaries as well as better prices, and more Januaries take more years.

![An animated whiteboard sketch titled “More Januaries take more years”, drawn slowly stroke by stroke. A grey axis along the bottom is labelled “Januaries”, and a grey axis up the side “X”. A black curve labelled “high” and a grey one labelled “low” fall from left to right and flatten as the count grows. A brown mark between them at “18” is labelled “0.0547 to 0.0615”, and another at “72” is labelled “0.0265 to 0.0298”. The words “Four times the Januaries, about half the X” and “one January a year, so 72 Januaries take 72 years” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_january_years.gif)

### Whether Heston and Sadka’s effect existed before 2002

Chan’s file holds 13 months before 2002, all on survivors. Testing the effect in those years needs monthly returns from long before 2002 for every stock listed at the time, including the companies that later failed, merged or delisted. Three sources come close.

1. **CRSP**, Heston and Sadka’s own source. It licenses its data to universities, government agencies and investment firms, which usually reach it through WRDS, a data service the Wharton School runs for subscribers. It publishes no price for individuals.
2. **Norgate Data’s Diamond tier**, at $787.50 a year in October 2026. It carries US stocks back to 1950, delisted ones included, with past index membership. Whether its early decades cover as many stocks as CRSP’s is unchecked.
3. **[The Open Source Asset Pricing project](https://www.openassetpricing.com/)**, free. It rebuilds Heston and Sadka’s signal from CRSP and publishes the monthly returns of portfolios sorted on it. Those are its portfolios rather than Chan’s rule, so they test the effect rather than reproduce Example 7.7.

The two paid sources’ licences bar republishing their data. Every result here is computed from data committed beside it, so that anyone can recompute it.

![An animated whiteboard sketch titled “Three ways to get the data”, drawn slowly stroke by stroke as a grid. Its columns are “CRSP”, “Norgate Diamond” and “Open Source Asset Pricing”, and its rows ask whether each “keeps the companies that left”, “reaches back to 1965”, “can be committed here” and “runs Chan’s own rule”. Green ticks fill the first two rows for all three. On “can be committed here” CRSP and Norgate Diamond get red crosses and Open Source Asset Pricing a tick, and on “runs Chan’s own rule” the first two get ticks and Open Source Asset Pricing a cross. Below, the costs read “institutions only”, “$787.50 a year” and “free”. The words “only Open Source Asset Pricing can be committed, and it cannot run Chan’s rule” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_osap_sources.gif)

#### What the free source found

This repository has since read the free source. The Open Source Asset Pricing project’s portfolio goes long the tenth of NYSE and AMEX stocks that did best in the same month a year earlier and short the tenth that did worst, re-formed each month, on data that keeps the companies that later failed, merged or delisted. Over Heston and Sadka’s own sample, 1965 to 2002, it earned 1.36 percent a month before costs, where they printed 1.15 percent. Its t-statistic of 8.63 puts that average more than eight standard errors above zero. From 1965 to 2001, before Chan’s 2002, it earned 1.31 percent a month, about 15.8 percent a year, consistent with Chan’s “more than 13 percent”. So on data without survivorship bias the signal earned well above zero before 2002. Its 1.36 percent sits about 1.3 standard errors above Heston and Sadka’s figure, a gap small enough to arise by chance, so the comparison cannot tell the two figures apart. That is the project’s construction rather than Chan’s rule, and the comparison was run after a first look at these numbers, so it is exploratory.

![An animated whiteboard sketch titled “Before 2002, without survivors”, drawn slowly stroke by stroke, with three bars in percent a month to one scale. The words “Open Source Asset Pricing:” head the two lower bars. Above them, a black bar for “Heston and Sadka printed” reaches “1.15%”. Below, a brown bar for “1965 to 2002, their sample” reaches “1.36%”, with a bracket below it marking “one standard error each way”, which stops just short of 1.15. A second brown bar, “1965 to 2001, before Chan’s 2002”, reaches “1.31%”, past a green dashed mark for “Chan’s “more than 13%” a year, 1.08% a month”. The words “a month, before costs, NYSE and AMEX stocks with the ones that left” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_osap_before.gif)

### Whether Heston and Sadka’s effect survived the book

#### How the run was built

The second later run, the IVV run below, tested Example 7.7 under the revised MATLAB’s rules on the S&P 500 as it stood each month, from January 2009 to September 2026, so the companies that later left the index are in it. The membership comes from IVV, an iShares fund that holds the index and files its holdings with the SEC each quarter. Each filing’s list stands for the months until the next, so a company that joins or leaves between two filings counts as doing so at the next one. This run is **registered** too, for the same reason as the January run.

![An animated whiteboard sketch titled “A list stands until the next filing”, drawn stroke by stroke. Four grey dashed lines stand for “quarter-end filings”. On a row labelled “a company that leaves”, a black line runs from the first filing to a tick labelled “leaves the index”, and a red stretch carries on to the next filing, labelled “still on the list”. On a row labelled “a company that joins”, a red dashed stretch labelled “not yet on the list” runs from where it joins to the next filing, and a black line runs on from there. The words “each filing’s list stands until the next one” close the sketch.](../docs/figures/equity_seasonals_ivv_carry.gif)

#### Which companies it kept

Free daily prices gave a checked price for 98,321 of its 107,115 member-months, each one company in one month, and the run dropped the rest, so each tenth is a tenth of the companies with a checked price.

![An animated whiteboard sketch titled “Who had a checked price”, drawn stroke by stroke. A long bar is black for the “98,321 member-months with a checked price” and red for the “8,794 dropped”. Two thinner bars below it split the same way at two month-ends, labelled “fewest: 364 of 501, 2012-09” and “most: 501 of 503, 2025-09”.](../docs/figures/equity_seasonals_ivv_checked.gif)

#### Whether dropping the rest matters

Dropping the rest is harmless only if leaving the index has little to do with where a company ranks. Among the companies kept, those that left the index within a year landed in a traded tenth more often than those that stayed, most of all in the short tenth. That comparison is described rather than tested. It counts against the drop being harmless, and which way it moves the result is not measured.

![An animated whiteboard sketch titled “Leavers land in the tenths”, drawn slowly stroke by stroke, with two bars split into green, red and grey shares of member-months. The bar for companies that “left within a year” is “long 12.0%”, “short 16.5%” and “neither” for the rest. The bar for those that “stayed” is “long 9.8%”, “short 9.6%” and “neither”. The words “leavers sit in a traded tenth more often, most of all the short one” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_ivv_leavers.gif)

#### What the run found

The 213 months average −0.0001 a month before costs. A strategy that truly earns nothing would give a t-statistic at least that high more than half the time, which is a one-sided p of 0.539. The revised Python’s rules give the same return in every one of the 213 months.

![An animated whiteboard sketch titled “213 months add up to nothing”, drawn stroke by stroke. A grey zero line runs from 2009 to 2026. A green dashed line, labelled “13% a year, the book’s figure”, climbs steeply above it, and a brown dashed line labelled “4.2% a year” climbs more gently. A black line labelled “the run’s 213 months, added up” runs just below zero nearly the whole way, lowest in 2021, and ends just below it. The words “a mean of −0.0001 a month: flat, under the 4.2% a year its test could detect” close the sketch.](../docs/figures/equity_seasonals_ivv_running_sum.gif)

The green line draws the book’s 13 percent as printed. Read as Heston and Sadka’s figure, that is the gap between the best tenth and the worst, and Chan’s rule earns half that gap, so at the rule’s scale it is about 6.5 percent a year. The run falls well short of either.

#### What the verdict says

The verdict, in the words written before the run, is “no return detectable above about 4.2% a year”. The 4.2 percent is the smallest annual return the test detects 80 percent of the time, so a smaller true return could pass unseen, and the verdict does not say the effect died. It also leaves out costs, which can only lower the return, and the last return a failing company takes as it leaves the index, which free data does not carry.

##### Where the 4.2 percent comes from

A reader who wants only the verdict, stated above, can skip this arithmetic and go to the next section, *What a broader series shows*.

The 4.2 percent follows from the noise in the 213 months and the two numbers fixed before the run, the 5 percent bar and the 80 percent chance. The 80 percent is the convention Jacob Cohen proposed for a test’s power, the chance it catches a true effect of a given size. Paired with the 5 percent bar, it lets the test miss a real effect a fifth of the time but raise a false alarm only a twentieth of the time, so a false alarm counts as four times as costly as a miss. The months have a standard deviation of 0.0206, so their mean has a standard error of

```math
\text{SE} = \frac{s}{\sqrt{n}} = \frac{0.0206}{\sqrt{213}} = 0.00141
```

The test calls a mean above zero when its t-statistic clears 1.652. That is the one-sided 5 percent critical value at 212 degrees of freedom, one fewer than the 213 months, because the mean is estimated from them. If the true mean were zero, the t-statistic would scatter around zero with a spread of about 1, and it would clear 1.652 only 5 percent of the time. If the true mean is X, the whole scatter shifts right by about X divided by the standard error. Call that shift δ. The 4.2 percent comes from asking how far the scatter must shift for the statistic to clear 1.652 four times in five.

![An animated whiteboard sketch titled “Shifting the scatter”, drawn slowly stroke by stroke. Two rows share one axis of t-statistics. In the top row a grey scatter for “true mean 0” rises and falls, a red dashed line marks “1.652, the 5% bar”, and the thin tail past the line is shaded red, “clears it 5% of the time”. In the row below, the same shape in brown, for “true mean X”, sits slid right by an arrow labelled “δ = 2.494”, and its larger part past the line is shaded green, “clears it 80% of the time”. The finished drawing holds for twelve seconds.](../docs/figures/equity_seasonals_delta_scatter.gif)

A normal curve gives a close answer. With a spread of 1, the statistic is about δ plus a normal draw Z, and 80 percent of normal draws land above −0.842, because 0.842 is the normal curve’s 80th percentile and the curve is symmetric. So the statistic clears 1.652 four times in five when 1.652 sits 0.842 below the centre, which puts the centre at 0.842 past 1.652:

```math
\begin{aligned}
\text{clears the bar:}\quad & \delta + Z > 1.652 \\
\text{four in five:}\quad & P(Z > -0.842) = 0.80 \\
\text{so:}\quad & 1.652 - \delta = -0.842 \\
& \delta \approx 1.652 + 0.842 = 2.494
\end{aligned}
```

![An animated whiteboard sketch titled “The normal shortcut”, drawn slowly stroke by stroke. A brown normal curve has a dashed line at its centre, labelled “centre = 1.652 + 0.842 = 2.494”. A red dashed line marks “1.652, the bar”. The part of the curve left of it is shaded red, “20% miss”, and the part right of it green, “80% clear it”. A black bracket from the bar to the centre is labelled “0.842”, and the words “0.842 is the normal curve’s 80th percentile, so 80% of it lies above 0.842 below the centre” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_delta_shortcut.gif)

The exact answer uses the shifted scatter itself. With 212 degrees of freedom and a shift of δ, it is a normal draw shifted by δ, divided by the ratio of the months’ measured spread to the true spread:

```math
T_{212}(\delta) = \frac{Z + \delta}{\sqrt{V / 212}}
```

Z is a draw from a normal curve with a spread of 1. V is a draw from a chi-squared distribution with 212 degrees of freedom, so V / 212 averages 1 and wanders around it, the way a spread measured from 213 months wanders around the true spread. That wandering widens the scatter a little beyond the normal curve’s.

No formula turns the 0.80 back into δ, so a solver searches for it:

```math
\begin{gathered}
P\left(T_{212}(\delta) > 1.652\right) = 0.80 \\
\Rightarrow\quad \delta = 2.494
\end{gathered}
```

The chance of clearing 1.652 rises as δ grows. At δ = 0 it is 0.05, the 5 percent bar, and at δ = 50 it is all but certain. So the solver starts with that bracket, keeps narrowing it to the part where the chance crosses 0.80, and stops once it is narrower than a trillionth.

![An animated whiteboard sketch titled “Narrowing the bracket”, drawn slowly stroke by stroke. An upright axis is labelled “chance of” and “clearing 1.652”, a level one “δ”, and a grey note reads “drawn from 0 to 5, the solver starts at 50”. A black curve rises from “0.05” and crosses a brown dashed line at “0.80”. Below the axis, three brackets show the solver’s steps, each inside the one above: “narrowed from 50” runs from 0 to about 4.9, “keeps the upper half” from about 2.5 to 4.9, and “then jumps close” is a short bracket around 2.5, and the last is brown. A brown dashed line drops from the crossing to it, labelled “δ = 2.494”. The words “each bracket keeps the part where the curve crosses 0.80” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_delta_bracket.gif)

The normal-curve shortcut gives 2.4937 and the exact answer 2.4944, so they agree to three decimals. The exact answer is the larger, because the wider scatter needs a slightly bigger shift to clear 1.652 four times in five.

X is that many standard errors, and twelve months make a year:

```math
\begin{aligned}
X &= 2.494 \times 0.00141 \\
&= 0.00352 \text{ a month} \\
12X &= 0.0422 \text{ a year}
\end{aligned}
```

More months or less noise would lower it.

#### What a broader series shows

A broader series agrees with the IVV run. From 2002 to 2024 Open Source Asset Pricing’s portfolio on NYSE and AMEX stocks earned 0.12 percent a month, with a t-statistic of 0.50.

![An animated whiteboard sketch titled “Before 2002 and after”, drawn slowly stroke by stroke. A grey line marks “0”. A long brown bar for “1965 to 2001” reaches “1.31%”, with a black bracket under it, far from zero, for one standard error each way. A short brown bar for “2002 to 2024” reaches “0.12%”, and its bracket crosses zero, labelled “one standard error each way”. The words “Open Source Asset Pricing, a month before costs, NYSE and AMEX with the ones that left” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_broad_before_after.gif)

Over the 192 months it shares with the IVV run, 2009 to 2024, it earned 0.12 percent a month with a t of 0.39, and the two series moved together, at a correlation of 0.59. Neither shows a mean detectably above zero after the book. Like the figures before 2002, this comparison is exploratory.

![An animated whiteboard sketch titled “Moving together”, drawn slowly stroke by stroke. Two grey axes cross, one labelled “Open Source Asset Pricing’s month” across and one “the IVV run’s month” up. A black dot for each month fills in, a cloud that tilts up to the right. Beside it the words “192 months,” and “2009 to 2024” and, in green, “correlation 0.59”. The words “they rise and fall together” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_broad_together.gif)

Month to month, Open Source Asset Pricing’s series swings about twice as far as the IVV run’s. The IVV run follows Chan’s rule, which divides each month’s sum by every position it holds, long and short together, so it earns half the gap between the best tenth and the worst. Lesson 2 derives that half under “Why a reproduction cannot decide it”.

![An animated whiteboard sketch titled “Two running sums”, drawn slowly stroke by stroke. A grey line marks “0” from “2009” to “2024”. A brown line, “Open Source Asset Pricing’s series”, dips below zero in the first years, climbs well above it in the middle years, falls back below it in 2021, climbs back above it late in 2022, and ends above it. A black line, “the IVV run”, rises and falls with the brown one in smaller steps, reaches about the same low around 2021, and ends below zero. A grey note, “both added up, neither halved”, closes the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_broad_running.gif)

## What this means for a trader

Three habits follow from the lessons above.

1. **Account for every choice, every bug and every unit before comparing two figures for one strategy.** Every figure here needed rules the description leaves out, seven of those rules are bugs, and the first edition’s −0.9167 is not a return on capital.
2. **Write the criterion and fix the sample before reading a split.** A split computed first carries no verdict, and through 83 months of survivors it swings with a single year.
3. **Rule out survivorship bias before reading a result as an effect that died or lived.** A file saved after the fact holds only the stocks that made it.

On Chan’s own files, all seventeen figures his code prints reproduce to the digit. Whether the strategies died is a separate question, which these files cannot answer. For the January effect, a criterion written in advance and data that keeps the companies that left the index reach a bound, and the bound is too wide to read. It does not show that the effect died, and it does not show that it lived. For Heston and Sadka’s rotation, the same kind of test on the S&P 500 as it stood each month finds no return detectable above about 4.2 percent a year before costs, on the companies with a checked price. A smaller return could pass unseen, so it does not show that the effect died. It does back the title, though. A return the test would likely miss is under about 4.2 percent a year before costs, and costs only lower it, so it is not an edge a trader can count on. A January effect that free data cannot confirm is not one to count on either.

![An animated whiteboard sketch titled “Two verdicts”, drawn slowly stroke by stroke, with two number lines. Each line has its own scale. The upper line, labelled “January effect” and “per January”, has a zero tick, “0”, and a brown bracket from “−0.1047” to “0.0879” that straddles it, with the words “free data cannot decide”. The lower line, labelled “Heston and Sadka” and “per year”, has its own “0”, a pale green band from zero to a brown tick labelled “about 4.2% a year”, and a black dot at zero labelled “measured”, with the words “could pass unseen” beneath the band. A red arrow under the band points back toward zero and stops halfway, labelled “costs lower it, not measured”. The words “not shown dead, and no edge a trader can count on” close the sketch, which holds for twelve seconds.](../docs/figures/equity_seasonals_two_verdicts.gif)

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Examples 7.6 and 7.7, cited by MATLAB script as `example7_6.m` and `example7_7.m` at commit `1a71950` of the egorpe/EPChan-QuantitativeTrading mirror.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 13, 175, 179, 180 and 181, and Examples 7.6 and 7.7 at pp. 175 to 182. Page numbers in the post are this edition’s. Its Python is cited as `example7_6.py` and `example7_7.py` at commit `653cf92` of liujiantong/epchan_books, a third-party copy whose five printed figures match the book. Its Example 7.6 MATLAB is read from the public copy named under Data, and matches the first edition’s rules. Its Example 7.6 R is printed only in the book, so its rules are inferred from its figures matching the MATLAB’s.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates. The source of the 80 percent convention for a test’s power.
- Heston, S. L., & Sadka, R. (2007), as Chan (2021, p. 179) cites them, a working paper. Published as Heston, S. L., & Sadka, R. (2008). Seasonality in the cross-section of stock returns. *Journal of Financial Economics*, 87(2), 418–445. Lesson 2’s description of their sample and its 1.15 percent a month come from the October 2006 working paper of the same title, Table 2, the row for annual lags in year 1, read from [a copy hosted by NYU Stern](https://w4.stern.nyu.edu/finance/docs/pdfs/Seminars/063f-sadka.pdf).
- Singal, V. (2006). *Beyond the Random Walk: A Guide to Stock Market Anomalies and Low-Risk Investing*. Oxford University Press. Cited by Chan (2021, p. 175) for the January effect.
- Data: two of Chan’s own MATLAB data files, converted into one file per stock. For Example 7.6, `IJR_20080131.mat` holds 600 members of the S&P 600, recorded as split-adjusted, saved 2008-02-02, spanning 2004-01-15 to 2008-02-01. For Example 7.7, `SPX_20071123.mat` holds 500 members of the S&P 500, also recorded as split-adjusted, saved 2007-11-24, spanning 1999-11-24 to 2007-11-23. The mirror of the first edition’s code and data holds only an earlier save of the S&P 600 file, `IJR_20080114.mat`, which ends on 2008-01-14. The later file comes from [a public copy of the revised edition’s code](https://github.com/pinhaocheng/epchan-quant_trading_MATLAB_codes/tree/7430b84), a third party’s repost rather than Chan’s own. That copy also carries the earlier save, byte for byte as the mirror has it, which is why its later file is trusted. The two saves give the first two Januaries to the same digits.

*Not investment advice. Code: [the two strategies](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/equity_seasonals_whiteboard.py), with the checks behind [the strategies’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_equity_seasonals_whiteboard.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-7-the-equity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
