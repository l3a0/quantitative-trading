# What a backtest leaves out: Chan’s lessons on trading costs and dead stocks

*Five basis points a trade take a Sharpe ratio from 0.25 to −3.19, and a database of survivors turns a 42% loss into a 388% gain.*

## Why two results change sign

A backtest replays a trading rule on old prices and reports what it would have earned. Whatever the replay leaves out, the result quietly assumes away. Chapter 3 of Ernest Chan’s *Quantitative Trading* (Chan, 2021) works two examples where putting one missing thing back turns a gain into a loss.

1. **The cost of trading.** Example 3.7 runs a rule Amir Khandani and Andrew Lo published, which buys yesterday’s biggest losers and sells short its biggest winners. On the S&P 500 over 2006, Chan gets a Sharpe ratio of 0.25 before costs and −3.19 after charging 5 basis points a trade.
2. **The stocks that died.** Example 3.3 buys the ten cheapest of the 1,000 largest US stocks and holds them for a year. On a database that keeps the companies that later failed, the portfolio loses 42%. On a database of survivors only, it gains 388%.

This repository reproduced all four numbers. The reversal gives 0.2510 and −3.1884 on the file of prices Chan’s own code reads, and the toy gives −41.72% and 387.88% from the two tables the book prints. Reproducing them turned up two things the book does not say: the −3.19 depends on two quirks of Chan’s code, and most of the 388% comes from one row of his table that compares two different kinds of share. This post draws five lessons from the two examples. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How the two examples work

**The reversal.** Each day, every stock in the S&P 500 gets a weight equal to minus its return against the market’s, divided by the number of stocks priced that day:

```math
w_{i,t} = -\frac{r_{i,t} - \bar r_t}{n_t}
```

Here `rᵢₜ` is stock `i`’s return on day `t`, `r̄ₜ` is the average return across stocks that day, and `nₜ` counts the stocks with a price. A stock that fell more than the market gets a positive weight, so the rule buys it, and one that rose more gets a negative weight, so the rule sells it short. The weights sum to zero, so the book is as long as it is short. The rule holds each day’s weights for one day and then sets them again.

The usual measure of how well a strategy pays for its risk is the **Sharpe ratio**, the average return divided by the size of its swings. Chan’s version uses the daily profit, subtracts no interest rate, and multiplies by √252 to put a daily figure on a yearly scale:

```math
\text{Sharpe} = \sqrt{252}\;\frac{\text{mean daily profit}}{\text{standard deviation of daily profit}}
```

Chan charges 5 basis points, five-hundredths of a percent, on each side of every change in weight. That is his estimate at Kindle location 998 of what an S&P 500 stock costs to trade, with a round trip of a buy and a sell counted as two trades.

The prices come from `SPX_20071123.mat`, the file Chan’s MATLAB code reads, from a public mirror of the book’s code. It holds the 500 stocks in the S&P 500 on 23 November 2007, with their prices carried back to 1999. The test window is 2006, 251 trading days from 3 January to 29 December.

**The toy.** On 2 January 2001, rank the 1,000 largest US stocks by price, buy the ten cheapest with equal money in each, and sell them on 2 January 2002. The book prints two tables of ten picks, one from each kind of database, and the returns follow from those tables alone. Example 3.3 is the revised edition’s number for it, and whether the 2009 first edition numbers it the same way was not checked.

The two results carry different labels. The reversal’s is **exploratory**: reproducing Chan’s figures spent the 2006 data on a rule somebody else chose, so the result says whether his numbers reproduce on his file and nothing about whether the rule pays today. The toy carries neither that label nor any other, because it reads the book’s printed tables and spends no data at all. Re-doing a printed table’s arithmetic tests the arithmetic.

## Lesson 1: on the S&P 500, a day’s cost is larger than a day’s profit

Chan’s weights are small numbers that he never scales to a dollar amount, so the clearest way to read an average day is as a share of the position the rule holds. Over 2006, per dollar of its average gross position, the long side plus the short side, the rule earned 0.53 basis points a day before costs. Its daily profit swung by about 33 basis points. The Sharpe ratio is that average over that swing, times √252, which gives 0.2510. A small edge under a large swing is a mediocre strategy, which is what Chan calls it.

Then the cost. Because the rule sets every weight again from yesterday’s returns, little of yesterday’s book survives into today’s. Each day it trades 1.45 times its average position, and at 5 basis points on each unit traded that costs 7.25 basis points of the position a day. The day’s cost is 13.7 times the day’s profit. Subtracting it barely changes the swing, so the Sharpe ratio drops to −3.2337, with the first day’s trades charged. Chan’s −3.19 comes from the same arithmetic with the first day treated differently, which Lesson 2 explains.

![Two lines of cumulative profit over 2006, each day’s profit divided by the year’s average gross position. The green line, before costs, wanders around zero and ends the year at +1.3%. The red line, after 5 basis points a side, falls steadily from January and ends at −16.9%. The note gives the Sharpe ratios as 0.2510 before costs and −3.2337 after.](../docs/figures/khandani_lo_cumulative_profit.png)

*Each day’s profit summed over the year, as a share of the average position. Before costs the rule ends 2006 up 1.3%. After costs it ends down 16.9%.*

Khandani and Lo report a Sharpe ratio of 4.47 for the same rule in 2006, before costs (Khandani & Lo, 2007). Chan’s explanation is the universe. In their paper, he writes, most of the returns came from small and microcap stocks, and his test used only the 500 largest. That figure was computed on stocks this repository does not hold, so it is cited here rather than checked. Chan makes the same point about costs with a second rule at location 1004, where a five-minute futures strategy he describes falls from a Sharpe ratio of about 3 to about −3 at 1 basis point a trade.

## Lesson 2: reproducing −3.19 depends on two quirks of Chan’s code

The −3.2337 above charges every day, including the first. Chan’s code does not, and his helper functions treat the gap that leaves in a way a careful port would not copy.

1. **The first day’s trades are never charged.** Chan cuts the weights to 2006 before taking the day-to-day change, so the first day has no earlier weight to compare against and its after-cost profit is missing. The code stores it as NaN, a value that stands for missing.
2. **His standard deviation counts the missing day as zero, while his mean skips it.** Chan’s `smartstd` fills NaN with zero and his `smartmean` leaves it out, so the swing is measured over 251 days and the average over 250.

Each quirk moves the answer.

```math
\begin{array}{l|c}
\text{After-cost specification} & \text{Sharpe ratio} \\ \hline
\text{Chan's code, both quirks kept} & -3.1884 \\
\text{The missing day skipped in both the mean and the deviation} & -3.1822 \\
\text{The first day charged, so nothing is missing} & -3.2337 \\ \hline
\text{Printed in the book} & -3.19
\end{array}
```

A port that skips the missing day in both places, as the pandas library does by default, gives −3.1822, which rounds to −3.18 and misses the book. Only Chan’s exact handling lands on −3.19. Charging the first day removes both quirks and gives a slightly worse figure, so the quirks moved Chan’s number a little in his favour without changing his point. Matching a printed figure to its last digit can mean transcribing the author’s helper functions, not only the formula on the page.

## Lesson 3: a database of survivors turns a loss into a large gain

Chan states the mechanism at location 1012. Some stocks are cheap because the company is about to fail, so a database that has dropped the failures offers a cheap-stock strategy only the cheap stocks that recovered.

The two tables show it. Nine of the ten survivorship-free picks were delisted during 2001, and the book gives each one’s last traded price, which is what a holder got out. Only MDM still traded on 2 January 2002, and it is the one stock in both tables. The survivor-only database never held the other nine, so it skips them and keeps going up the price ranking to stocks that all survived the year.

With equal money in each stock, the survivorship-free picks return −41.72% and the survivor-only picks 387.88%, which round to Chan’s −42% and 388%. The book prints no formula, so the weighting was something the reproduction had to find. Buying one share of each instead gives −47.62% and 373.17%, and neither rounds to the book, which is what rules that weighting out. Chan calls the 388% “fictitious”.

## Lesson 4: the author’s own table mixes two kinds of share in one row

One stock carries most of the 388%. NEOF, Neoforma, contributes 308.86 of the 387.88 points. Its row starts at $0.875 on 2 January 2001 and ends at $27.90 on 2 January 2002.

Neoforma’s annual report for 2001 states a 1-for-10 reverse split effective 27 August 2001, which turned every ten shares into one ([Neoforma, 2002](https://www.sec.gov/Archives/edgar/data/1096219/000101287002001537/d10k.htm)). So the start price is for a share before the split and the end price for a share after it. On one basis, the start price is $8.75. With that one correction NEOF contributes 21.89 points, and the survivor-only portfolio returns 100.91%.

![Three horizontal bars of equal-capital returns. The survivorship-free picks lose 41.72%. The survivor-only picks as the book prints them gain 387.88%, of which a gold segment for NEOF covers 308.86 points and a green segment for the other nine the rest. The same survivor-only picks with NEOF’s start price multiplied by 10 gain 100.91%, with NEOF’s gold segment shrunk to 21.89 points and the other nine’s green segment unchanged.](../docs/figures/survivorship_toy_returns.png)

*The other nine survivors contribute the same in both bars. Putting NEOF’s two prices on one basis takes the survivor-only return from 387.88% to 100.91%.*

The lesson survives the correction, since a 41.72% loss against a 100.91% gain is still a loss turned into a gain. The size of the effect shrinks a lot. Both numbers belong in a report, side by side: 388% reproduces from the table as printed, and 100.91% is what the same picks return once one row is fixed. Only NEOF was checked against a filing, so the other nineteen rows are taken as printed.

Chan tells the same toy again in his later *Algorithmic Trading* (Chan, 2013) and keeps the 388%, but describes the honest outcome as “almost 100 percent loss” rather than 42%.

## Lesson 5: the toy’s size does not carry over to the reversal

Example 3.7’s file has the same flaw the toy demonstrates. It holds the S&P 500 as it stood on 23 November 2007, so every company that left the index before then, whether it failed or was bought, is missing from the 2006 test. The file prices 491 stocks on the window’s first day and 495 on its last. Not one of the 491 is missing by the end, and four that began trading during 2006 join them. A real index loses members during a year, and this one cannot.

It is tempting to read the toy as the size of that problem. It is not. The toy only buys, so a missing failure can only flatter it. The reversal buys and sells short at once. On a day a failing stock falls, the rule buys it, and dropping the stock removes that loss from the long side. On a day it bounces, the rule sells it short, and when it then falls the short makes money, so dropping it removes a gain as well. Neither the size nor the direction of the effect on 0.2510 or −3.1884 is known.

Chan argues in *Algorithmic Trading* that for a strategy like this, long and short at once and betting on reversal, the missing losses on the long side tend to outweigh the missing gains on the short side, so survivorship still flatters it but by less. That is an argument rather than a measurement. Measuring it needs the index as it actually stood on each day of 2006, delisted stocks included, which has to be bought. [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) tracks it.

## What this replication cannot say

Five things are beyond the two results.

1. **Whether Khandani and Lo’s 4.47 reproduces, or Chan’s small-cap explanation holds.** The repository holds Chan’s S&P 600 small-cap file, which covers 2006, and Chan leaves running the rule on it as an exercise at location 2236. Nothing here runs it.
2. **What survivorship cost the reversal.** Lesson 5 says why the toy cannot answer it, and [issue 198](https://github.com/l3a0/quantitative-trading/issues/198) needs bought data.
3. **What trading at the open gives.** That is Chan’s next example, below, and it has not run here.
4. **Whether the toy’s picks are right.** The book does not print the 1,000 stocks it ranked, so the selection cannot be rerun, and only NEOF’s row was checked against a filing.
5. **Whether either strategy pays today.** The reversal’s result is exploratory and covers one year, and the toy covers ten stocks for one year and was never meant as a test of buying cheap stocks.

## What this means for a trader

Five habits follow from the lessons above.

1. **Price the turnover before trusting the edge.** A rule that replaces its book every day pays its cost every day, and on large stocks a few basis points a trade can be many days of profit.
2. **Match the author’s code, not only the formula.** Two lines about a missing day decide whether −3.19 reproduces.
3. **Ask whether the database holds the dead.** A cheap-stock backtest on survivors picks the recoveries and never the failures.
4. **Find the rows that carry the result.** One stock out of ten made most of the 388%, and its row mixed two kinds of share.
5. **Do not carry a bias’s size from one strategy to another.** The same missing stocks flatter a buy-only rule and act in both directions on a long-short one.

Chan follows Example 3.7 with Example 3.8, numbered so in the revised edition. It changes one thing, updating the positions at the market open instead of the close, and Chan says both Sharpe ratios, before and after costs, then turn “very positive”. This repository has not run it yet. [Issue 206](https://github.com/l3a0/quantitative-trading/issues/206) will, on the opening prices already in Chan’s file, and this post will report what it finds.

## References

- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
- Neoforma, Inc. (2002). *Annual report on Form 10-K for the fiscal year ended December 31, 2001*. U.S. Securities and Exchange Commission.

*Not investment advice. Code: [the reversal](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo.py), [the toy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/survivorship_bias.py) and [the charts](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/survivorship_and_costs_figures.py), with the checks behind [the reversal’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo.py), [the toy’s](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_survivorship_bias.py) and [what the charts draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_survivorship_and_costs_figures.py), and the replication log’s entries for [the reversal](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-8-the-khandani-lo-reversal-chans-quantitative-trading) and [the toy](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-9-the-survivorship-toy-chans-quantitative-trading).*
