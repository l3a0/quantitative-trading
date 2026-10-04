# What a backtest leaves out: Chan’s lessons on trading costs and dead stocks

*Five basis points a trade take a Sharpe ratio from 0.25 to −3.19, and a database of survivors turns a 42% loss into a 388% gain.*

## Why two results change sign

A backtest replays a trading rule on old prices and reports what it would have earned. Whatever the replay leaves out, the result quietly assumes away. Chapter 3 of Ernest Chan’s *Quantitative Trading* (Chan, 2021) works three examples of it. In the first two, putting one missing thing back turns a gain into a loss. The third is Chan’s reply to the first.

1. **The cost of trading.** Example 3.7 runs a rule Amir Khandani and Andrew Lo published, which buys yesterday’s biggest losers and sells short yesterday’s biggest winners. Selling short means borrowing a share and selling it, so the position gains when the price falls. On the S&P 500 over 2006, Chan measures the rule’s reward for its risk, its Sharpe ratio, at 0.25 before costs. After charging 5 basis points a trade, where a basis point is a hundredth of a percent, it is −3.19.
2. **The stocks that died.** Example 3.3 buys the ten cheapest of the 1,000 largest stocks and holds them for a year. On a database that keeps the companies that later failed, the portfolio loses 42%. On a database of survivors only, it gains 388%.
3. **The time of day.** Example 3.8 runs Example 3.7’s rule again with one change, updating the positions at the market open instead of the close. Chan says both Sharpe ratios, before costs and after, then turn “very positive” (p. 78). The book prints no figure for it.

This repository reproduced all four numbers. The reversal gives 0.2510 and −3.1884 on the file of prices Chan’s own code reads, and the toy gives −41.72% and 387.88% from the two tables the book prints. Reproducing them, and running Example 3.8, turned up four things the book does not say.

1. Chan’s −3.19 depends on how his code handles one missing day.
2. Most of the 388% comes from one row of his table, which compares two different kinds of share.
3. On the rule the book describes, trading at the open misses Chan’s claim after costs, while the Python code he published for the example prints figures that meet it.
4. One stock’s prices in Chan’s file stop and restart years later, and his Python code reads the gap as a single day’s gain of over 12,000 percent.

This post draws seven lessons from the three examples. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How the examples work

**The reversal.** Each day, every stock in the S&P 500 gets a weight equal to minus its return against the market’s, divided by the number of stocks priced that day:

```math
w_{i,t} = -\frac{r_{i,t} - \bar r_t}{n_t}
```

Here `rᵢₜ` is stock `i`’s return on day `t`, `r̄ₜ` is the average return across stocks that day, and `nₜ` counts the stocks with a price. A stock that fell more than the market gets a positive weight, so the rule buys it, and one that rose more gets a negative weight, so the rule sells it short. The weights sum to zero, so the rule holds as much in stocks it owns as in stocks it has sold short. Those holdings together are its **book**. The rule keeps each day’s weights for one day and then sets them again.

The usual measure of how well a strategy pays for its risk is the **Sharpe ratio**, the average return divided by the size of its swings. Chan’s version uses the daily profit, subtracts no interest rate, and multiplies by √252 to put a daily figure on a yearly scale:

```math
\text{Sharpe} = \sqrt{252}\;\frac{\text{mean daily profit}}{\text{standard deviation of daily profit}}
```

Chan charges 5 basis points on each side of every change in weight. That is his estimate on p. 25 of what an S&P 500 stock costs to trade, with a round trip of a buy and a sell counted as two trades.

The prices come from `SPX_20071123.mat`, the file Chan’s MATLAB code reads, from a public mirror of the book’s code. It holds one column of prices for each of the 500 stocks in the S&P 500 on 23 November 2007, with their prices carried back to 1999. The test window is 2006, 251 trading days from 3 January to 29 December.

**Trading at the open.** Example 3.8 keeps the reversal and makes what Chan calls “the only change” (p. 78): each day’s weights come from the opening prices, and the positions are updated at the open. The opening prices are in the same `SPX_20071123.mat`. From here on, “on the opens” and “on the closes” say which of the two sets of prices a figure was computed from.

Chan’s code for these examples comes in two forms that disagree. His MATLAB for Example 3.7 gives the book’s 0.25. The revised edition also points to Python notebooks, files that hold code together with the output it printed when its author ran it, and his notebook for Example 3.7 does not give 0.25. So two versions of the rule run here. The **book’s rule** is Example 3.7’s MATLAB, the code behind 0.25 and −3.19, with the open in place of the close. The **notebook’s rule** is Chan’s notebook for Example 3.8, `example3_8.ipynb`, run as written. Lesson 6 says how the two differ.

**The toy.** On 2 January 2001, rank the 1,000 largest stocks by price, buy the ten cheapest with equal money in each, and sell them on 2 January 2002. The book prints two tables of ten picks. The first comes from a **survivorship-free** database, one that keeps the companies that later failed or were removed from the exchange. The second comes from a database holding only the survivors. The returns follow from those two tables alone. Example 3.3 is the revised edition’s number for the toy, and this repository has not checked how the 2009 first edition numbers it. Page numbers here are the revised edition’s too.

## Lesson 1: on the S&P 500, a day’s cost is larger than a day’s profit

Chan’s weights are small numbers that he never scales to a dollar amount, so the clearest way to read an average day is as a share of the position the rule holds. Over 2006, per dollar of its average gross position, the stocks it owns plus the stocks it has sold short, the rule earned 0.5276 basis points a day before costs. Its daily profit swung with a standard deviation of 33.3770 basis points. The Sharpe ratio is that average over that swing, times √252:

```math
\text{Sharpe before costs} = \sqrt{252}\;\frac{0.5276}{33.3770} \approx 0.2510
```

Chan calls 0.25 a “mediocre” Sharpe ratio, a small edge under a large swing.

Then the cost. Because the rule sets every weight again from yesterday’s returns, little of yesterday’s book survives into today’s. Each day it trades 1.4505 times its average position, and each unit traded costs 5 basis points:

```math
\text{daily cost} = 1.4505 \times 5\ \text{basis points} = 7.2525\ \text{basis points}
```

The day’s cost is 13.7453 times the day’s profit. Subtracting it from every day moves the average a long way and barely changes the swing, from 33.3770 to 33.0134 basis points. With the first day’s trades charged, the Sharpe ratio drops to −3.2337:

```math
\text{Sharpe after costs} = \sqrt{252}\;\frac{0.5276 - 7.2525}{33.0134} \approx -3.2337
```

The inputs are shown at four decimals, so redoing the arithmetic on them can miss the last digit of a result, which comes from the unrounded figures. Chan’s −3.19 comes from the same arithmetic with the first day treated differently, which Lesson 2 explains.

![Two lines of cumulative profit over 2006, each day’s profit divided by the year’s average gross position. The green line, before costs, wanders around zero and ends the year at +1.3%. The red line, after 5 basis points a side, falls steadily from January and ends at −16.9%. The note gives the Sharpe ratios as 0.2510 before costs and −3.2337 after.](../docs/figures/khandani_lo_cumulative_profit.png)

*Each day’s profit summed over the year, as a share of the average position. Before costs the rule ends 2006 up 1.3%. After costs it ends down 16.9%.*

Chan writes on p. 72 that Khandani and Lo report a Sharpe ratio of 4.47 for the same rule in 2006, before costs (Khandani & Lo, 2007). He puts the gap down to the stocks tested. In their paper, he writes, most of the returns came from small and microcap stocks, the smallest listed companies, and his test used only S&P 500 stocks. Their figure was computed on stocks this repository does not hold, so it is cited here rather than checked. Chan makes the same point about costs with a second rule on p. 26, where a five-minute futures strategy he describes has a Sharpe ratio of about 3 before costs and −3 after 1 basis point a trade.

## Lesson 2: matching −3.19 means matching how Chan’s code handles one missing day

The −3.2337 above charges every day, including the first. Chan’s code does not, and his helper functions treat the gap that leaves in their own way.

1. **The first day’s trades are never charged.** Chan cuts the weights to 2006 before taking the day-to-day change, so the first day has no earlier weight to compare against and its after-cost profit is missing. The code stores it as NaN, a value that stands for missing.
2. **His standard deviation counts the missing day as zero, while his mean skips it.** Chan’s `smartstd` fills NaN with zero and his `smartmean` leaves it out, so the swing is measured over 251 days and the average over 250.

Rewriting his code in Python shows how much those two choices matter.

```math
\begin{array}{l|c}
\text{After-cost specification} & \text{Sharpe ratio} \\ \hline
\text{Chan's code, both quirks kept} & -3.1884 \\
\text{The missing day skipped by pandas} & -3.1822 \\
\text{The missing day skipped by NumPy} & -3.1886 \\
\text{The first day charged, so nothing is missing} & -3.2337 \\ \hline
\text{Printed in the book} & -3.19
\end{array}
```

pandas, the standard Python library for tables of data, skips a missing value in both the mean and the standard deviation by default. That gives −3.1822, which rounds to −3.18 and misses the book. NumPy’s functions that skip missing values do the same, but by default divide the variance by the number of days rather than one fewer. That gives −3.1886, which lands on −3.19 by a different route. So whether a rewrite reproduces the book’s second digit depends on two choices the page never mentions. Charging the first day removes both of Chan’s quirks and gives a slightly worse figure, so the quirks moved his number a little in his favour without changing his point.

## Lesson 3: a database of survivors turns a loss into a large gain

Chan states the mechanism on p. 26. Some stocks are cheap because the company is about to fail, so a database that has dropped the failures offers a cheap-stock strategy only the cheap stocks that recovered.

The two tables show it. Nine of the ten survivorship-free picks were removed from the exchange during 2001, and the book gives each one’s last traded price, which is what a holder got out. Only MDM still traded on 2 January 2002, and it is the one stock in both tables. The survivor-only database never held the other nine, so it skips them and keeps going up the price ranking to stocks that all survived the year.

With equal money in each stock, the survivorship-free picks return −41.72% and the survivor-only picks 387.88%, which round to Chan’s −42% and 388%. The book prints no formula, so the reproduction had to find the weighting. Buying one share of each instead gives −47.62% and 373.17%, and neither rounds to the book, which is what rules that weighting out. Chan calls the 388% “fictitious”.

## Lesson 4: the author’s own table mixes two kinds of share in one row

One stock carries most of the 388%. NEOF, Neoforma, contributes 308.86 of the 387.88 points. Its row starts at $0.875 on 2 January 2001 and ends at $27.90 on 2 January 2002.

Neoforma’s annual report for 2001 states a 1-for-10 reverse split effective 27 August 2001, which turned every ten shares into one ([Neoforma, 2002](https://www.sec.gov/Archives/edgar/data/1096219/000101287002001537/d10k.htm)). So the start price is for a share before the split and the end price for a share after it. Counted in shares after the split, the start price is $8.75. With that one correction NEOF contributes 21.89 points, and the survivor-only portfolio returns 100.91%.

![Three horizontal bars of equal-capital returns. The survivorship-free picks lose 41.72%. The survivor-only picks as the book prints them gain 387.88%, of which a gold segment for NEOF covers 308.86 points and a green segment for the other nine the rest. The same survivor-only picks with NEOF’s start price multiplied by 10 gain 100.91%, with NEOF’s gold segment shrunk to 21.89 points and the other nine’s green segment unchanged.](../docs/figures/survivorship_toy_returns.png)

*The other nine survivors contribute the same in both bars. Counting NEOF’s two prices in the same kind of share takes the survivor-only return from 387.88% to 100.91%.*

The lesson survives the correction, since a 41.72% loss against a 100.91% gain is still a loss turned into a gain. The effect is far smaller than the printed table shows. Both numbers belong in a report, side by side: 388% reproduces from the table as printed, and 100.91% is what the same picks return once one row is fixed. This repository checked only NEOF against a filing, so the other nineteen rows are taken as printed.

Chan tells the same toy again in his later *Algorithmic Trading* (Chan, 2013) and keeps the 388%, but describes the honest outcome as “almost 100 percent loss” rather than 42%.

## Lesson 5: the toy cannot measure survivorship’s effect on the reversal

Example 3.7’s file has the same flaw the toy demonstrates. It holds the S&P 500 as it stood on 23 November 2007, so every company that left the index before then, whether it failed or was bought, is missing from the 2006 test. The file prices 491 stocks on the window’s first day and 495 on its last. Not one of the 491 is missing by the end, and four stocks with no price on the first day have one on the last. One of the four, WYN, also has prices from years earlier, which Lesson 7 is about. A real index loses members during a year, and this one cannot.

The toy cannot say how much that flatters the reversal, because the toy only buys, and the reversal buys and sells short at once. For a buy-only rule, a missing failure can only flatter the result. For the reversal it acts both ways. On a day a failing stock falls, the rule buys it, and dropping the stock removes that loss from the side it owns. On a day it bounces, the rule sells it short, and when it then falls the short makes money, so dropping it removes a gain as well. Neither the size nor the direction of the effect on 0.2510 or −3.1884 is known.

Chan argues in *Algorithmic Trading* that for a strategy like this, long and short at once and betting on reversal, the missing losses on the side it owns tend to outweigh the missing gains on the short side, so survivorship still flatters it but by less. That is an argument rather than a measurement. Measuring it needs the index as it actually stood on each day of 2006, removed stocks included, which has to be bought. [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) tracks it.

## Lesson 6: on the book’s rule, trading at the open misses Chan’s claim after costs

Chan’s claim for Example 3.8 is that both Sharpe ratios, before costs and after, are “very positive” (p. 78). The book prints no figure, so the claim needs a threshold before it can be tested. [Issue 206](https://github.com/l3a0/quantitative-trading/issues/206) wrote it down before any figure on the opens was computed: both figures at least 1.0, compared unrounded. The threshold comes from Chan’s own rule of thumb. He writes that a strategy with a Sharpe ratio “of less than 1 is not suitable” to trade on its own (p. 23).

On the book’s rule, trading at the open earns 4.4202 before costs and 0.7834 after. The recovery is large, since Example 3.7’s −3.1884 after costs rises by 3.9718. But 0.7834 is below 1.0, so the claim does not hold on the book’s rule. Lesson 2’s quirks do not decide it. Charging the first day removes both and gives 0.8293, also below 1.0.

The notebook’s rule clears the threshold. Run as written, it reproduces both figures Chan’s notebook printed, to four decimals: 2.3818 before costs and 1.3997 after. The book prints neither number. They are the notebook’s own output, read in [a third-party copy of Chan’s Python code on GitHub](https://github.com/pinhaocheng/epchan-quant_trading_Python_codes/tree/5fcab614d75c53c61e79a9049f6f623b84e2f4d4), at commit `5fcab61`.

This post tests the claim on the book’s rule because of what Chan’s sentence says. It recalls Example 3.7’s 0.25 and −3.19 and calls trading at the open the only change. The notebook’s rule is not that strategy with one change. Chan’s companion notebook for Example 3.7, `example3_7.ipynb` in the same copy, printed 0.9578 before costs and −2.1617 after on the closes, where the book prints 0.25 and −3.19, and the notebook’s rule reproduces both. Among other differences from the MATLAB, it fills each gap in a stock’s prices with the last price seen, scales each day’s weights to a fixed total size, and divides the variance by the number of days rather than one fewer.

```math
\begin{array}{l|l|c|c}
\text{Rule} & \text{Prices} & \text{Before costs} & \text{After costs} \\ \hline
\text{The book's rule} & \text{close} & 0.2510 & -3.1884 \\
\text{The book's rule} & \text{open} & 4.4202 & 0.7834 \\
\text{The notebook's rule} & \text{close} & 0.9578 & -2.1617 \\
\text{The notebook's rule} & \text{open} & 2.3818 & 1.3997 \\ \hline
\text{Printed in the book} & \text{close} & 0.25 & -3.19 \\
\text{Printed in the book} & \text{open} & \text{very positive} & \text{very positive} \\
\text{The line declared in advance} & \text{open} & 1.0 & 1.0
\end{array}
```

## Lesson 7: one column of Chan’s file joins two stretches of prices

The stock with ticker WYN is one of the four Lesson 5 counts as priced on the window’s last day and not its first. Its column’s last price before a gap is 0.26. It then holds no price at all, and restarts 952 trading days later, at 31.85 on 1 August 2006. Nothing here says how the earlier prices entered the column.

The two rules read that gap differently. The book’s rule sets a stock’s weight from its return since the day before, and a stock with no price the day before gets a weight of zero, so the restart never enters a weight. The notebook’s rule first fills every gap with the last price seen. Older versions of pandas did that by default, and the notebook relies on it. So it carries 0.26 forward across the gap and reads 1 August 2006 as one day’s return of 121.5, a gain of over 12,000 percent, on the closes, and a return of 127.65 on the opens.

That one day moves the notebook’s figures, and not always in the same direction.

```math
\begin{array}{l|c|c|c}
\text{The notebook's rule} & \text{Without the fill} & \text{Without WYN} & \text{As written} \\ \hline
\text{Closes, before costs} & 0.4179 & 0.4268 & 0.9578 \\
\text{Opens, before costs} & 4.8606 & 4.8508 & 2.3818 \\
\text{Opens, after costs} & 1.0335 & 1.0357 & 1.3997
\end{array}
```

On the closes the gap lifts the figure before costs, from 0.4179 without the fill to 0.9578. On the opens it pulls the figure before costs down, from 4.8606 to 2.3818, and pushes the figure after costs up, from 1.0335 to 1.3997. Dropping WYN alone lands near dropping the fill in every row, so WYN’s gap carries most of what the fill does. WYN decides neither half of Lesson 6. The book’s rule never weights the gap, and the notebook’s figure after costs on the opens clears 1.0 either way. What WYN does decide is whether Chan’s notebooks reproduce, since each of their four printed figures, two on the closes and two on the opens, needs the gap read as one day’s move.

Like NEOF’s row in Lesson 4, one column of the author’s own data holds two things that code treats as one, and a published figure rests on the result. And as in Lesson 5, the question is what a file built from the 2007 index holds.

## What this replication cannot say

Five things are beyond these results.

1. **Whether Khandani and Lo’s 4.47 reproduces, or Chan’s small-cap explanation holds.** At the end of Example 3.8, on p. 78, Chan leaves testing the strategy on the S&P 400 mid-cap and S&P 600 small-cap stocks as an exercise. The repository holds Chan’s S&P 600 file, which covers 2006, and [issue 249](https://github.com/l3a0/quantitative-trading/issues/249) tracks running the rule on it.
2. **What survivorship cost the reversal, at the close or at the open.** Lesson 5 says why the toy cannot answer it, and [issue 198](https://github.com/l3a0/quantitative-trading/issues/198) needs bought data.
3. **Whether trading at the open can be done on the open’s own prices.** Both rules set a weight from the day’s opening prices and trade at that same open, as Example 3.7 does at the close. Neither run adjusts that timing.
4. **Whether the toy’s picks are right.** The book does not print the 1,000 stocks it ranked, so the selection cannot be rerun, and only NEOF’s row was checked against a filing.
5. **Whether either strategy pays today.** The reversal’s results are exploratory and cover one year, and the toy covers ten stocks for one year and was never meant as a test of buying cheap stocks.

## What this means for a trader

Seven habits follow from the lessons above.

1. **Price the turnover before trusting the edge.** A rule that replaces its book every day pays its cost every day, and on large stocks a few basis points a trade can be many days of profit.
2. **Match the author’s handling of missing data, not only the formula.** One missing day and the choice of divisor decide whether −3.19 reproduces.
3. **Ask whether the database holds the dead.** A cheap-stock backtest on survivors picks the recoveries and never the failures.
4. **Find the rows that carry the result.** One stock out of ten made most of the 388%, and its row mixed two kinds of share.
5. **Size a bias on the strategy it affects.** The same missing stocks flatter a buy-only rule and act in both directions on a long-short one.
6. **Test a claim on the rule the text describes, and a printout on the code that printed it.** Chan’s notebook reproduces its own figures exactly, while the book’s rule misses his claim after costs.
7. **Check each stock’s prices for long gaps, and what filling one does.** One column of Chan’s file stops and restarts years later, and filling the gap made it a one-day gain of over 12,000 percent.

## References

- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
- Neoforma, Inc. (2002). *Annual report on Form 10-K for the fiscal year ended December 31, 2001*. U.S. Securities and Exchange Commission.

*Not investment advice. Code: [the reversal](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo.py), [the toy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/survivorship_bias.py) and [the charts](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/survivorship_and_costs_figures.py), with the checks behind [the reversal’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo.py), [WYN’s column](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_series.py), [the toy’s](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_survivorship_bias.py) and [what the charts draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_survivorship_and_costs_figures.py), and the replication log’s entries for [the reversal](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-8-the-khandani-lo-reversal-chans-quantitative-trading), [the reversal at the open](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-10-the-khandani-lo-reversal-at-the-open-chans-quantitative-trading) and [the toy](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-9-the-survivorship-toy-chans-quantitative-trading).*
