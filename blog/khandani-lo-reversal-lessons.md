# Chan’s reversal reproduces on his 2012 panel, and most of its rise from 0.25 to 1.3 is the data

*Algorithmic Trading runs the first book’s reversal again on 497 stocks from 2007 to 2011. Every figure Chan prints lands on his own file, and the rule explains less of the jump in its Sharpe ratio than the data and the window do.*

## Why look at the reversal a second time

The [post on trading costs and failed companies](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) reproduced a rule Amir Khandani and Andrew Lo published, as Example 3.7 of Ernest Chan’s first book, *Quantitative Trading*. Each day it buys the S&P 500 stocks that fell most against the market and sells short the ones that rose most. On 2006 its Sharpe ratio was 0.2510 before costs, and charging 5 basis points a trade took it to −3.1884. That post explains the weights, the Sharpe ratio and the cost, and this one does not repeat them.

Chan’s second book, *Algorithmic Trading*, brings the rule back as its lesson on cross-sectional mean reversion (Chan, 2013, location 2087). A stock is judged against its peers on the same day rather than against its own past, so the bet is that a stock that did worse than the rest will do better next, “and vice versa”. He runs it on a newer file over 2007 to 2011 and reports a Sharpe ratio of 1.3, about five times the first book’s, and an intraday version with 4.7 (locations 2110 and 2135).

Chan published the script, `andrewlo_2007_2012.m`, and the data file it reads. This repository keeps a copy of the file and ran a line-by-line transcription of the script on it. Every figure the book prints for the two examples lands, and so do the two the script printed at six decimals.

**Every result here is exploratory.** Reproducing Chan’s figures spends the 2007 to 2011 sample on a rule somebody else chose, so it can say whether his numbers follow from his file and nothing about whether the rule pays today. **Every figure is also about survivors.** The file holds the S&P 500 as Chan held it on 2012-04-24, with each stock’s prices carried back over the whole window, so a company that left the index before then is not in it.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

Each day the rule computes every stock’s return, subtracts the average return of all the stocks, and gives the stock minus that difference as its weight. A positive weight is a dollar amount bought and a negative one a dollar amount sold short. The second book then divides each day’s weights by the sum of their absolute values, so the dollars bought and the dollars sold short add up to $1 every day. That total is the gross, and Chan writes that the rule invests “the same total gross capital of $1” each day (location 2087).

**Example 4.3** sets the weights at the close and holds them to the next close. **Example 4.4** keeps the rule and changes the signal and the holding (location 2124). Its weights come from the overnight move, from yesterday’s close to today’s open. It enters at the open and closes everything at the same day’s close. That differs from the first book’s Example 3.8, which the earlier post covers. Example 3.8 sets its weights from the opens and holds them from one open to the next.

The second book’s rule differs from the first book’s in five ways.

1. **The weights are scaled to a gross of 1 each day.** The first book divides them by the count of stocks priced.
2. **A stock with no price gets no weight at all**, where the first book gives it a weight of 0. Both leave it out of the day’s profit.
3. **No cost is charged.** The script’s cost lines are commented out.
4. **The window is cut before any return is taken.** The first book takes returns on its whole file and cuts the profit afterwards. Here the first day of the window has no return, so the first days earn nothing.
5. **The Sharpe ratio uses MATLAB’s own mean and standard deviation.** No series here has a missing day, so this difference moves no figure.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_stocks_20120424.mat`, saved on 2012-04-25 and converted here to one file per stock. It holds 497 stocks with their opens and closes, and this post calls it the panel. The script cuts it to 1,260 trading days, from 2007-01-03 to 2011-12-30. The book says the run starts on January 2, 2007, which was a market holiday. The cut makes Example 4.3’s first two days earn nothing, because its first day has no return and its second holds the first day’s empty weights. Example 4.4’s first day earns nothing for the same reason. This repository transcribed the script from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, which a second copy holds byte for byte.

Chan calls the rule “almost perfectly dollar neutral” (location 2110), meaning the dollars bought match the dollars sold short. With the weights scaled to a gross of 1, they sum to zero exactly on every day of both examples, up to the rounding of the arithmetic.

## Lesson 1: every figure Chan prints lands on his own file

Here is each figure, computed, beside the script’s comment and the book.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{Example 4.3, APR} & \text{13.677582 percent} & \text{13.7 percent} & \text{13.7 percent} \\
\text{Example 4.3, Sharpe ratio} & 1.259478 & 1.3 & 1.3 \\
\text{Example 4.3, APR in 2008} & \text{30.164676 percent} & \text{none} & \text{30 percent} \\
\text{Example 4.3, APR in 2011} & \text{10.577823 percent} & \text{none} & \text{11 percent} \\
\text{Example 4.4, APR} & 0.731553 & 0.731553 & \text{73 percent} \\
\text{Example 4.4, Sharpe ratio} & 4.713284 & 4.713284 & 4.7
\end{array}
```

The APR is the compounded annual return. The Sharpe ratio is the average daily return over its standard deviation, scaled to a year, with no interest rate subtracted. The script prints no yearly figure, so each year’s APR applies the script’s own APR line to that year’s days of the full run.

Two of the book’s roundings have little room. Example 4.3’s Sharpe ratio sits 0.0095 above 1.25, below which it would print as 1.2. Its APR in 2011 sits 0.08 above 10.5 percent, below which it would print as 10. Example 4.4’s APR is 0.7315525016, which is 1.6 × 10⁻⁹ above the point where the script’s sixth decimal would round down to 0.731552. So these three are the sharpest checks on a port, since a small drift from the script would move them across their rounding points.

The distance from 1.3 to 4.7 comes from the average return, since the two examples swing by about the same amount. A year of Example 4.3 averages a return of 0.1338 with a standard deviation of 0.1063. A year of Example 4.4 averages 0.5565 with a standard deviation of 0.1181. The Sharpe ratio is the first number over the second, so four times the average return with a similar swing gives a ratio nearly four times as large. Location 2890 sets the same 4.7 against cross-sectional momentum, which the [post on cross-sectional momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md) covers.

The figure below redraws the book’s Figure 4.4 for Example 4.3 and draws Example 4.4 below it on its own axis. Both of the script’s plot lines compound the daily returns, so both panels do too. Each year carries its APR above its span. Nothing compares the redraw with the chart in the book, so it is a redraw of the script’s plot rather than a checked copy.

![Two charts on one shared date axis from January 2007 to December 2011. The top chart is Example 4.3’s compounded cumulative return. It drifts slightly below zero through 2007, climbs through 2008 and 2009 to about 70 percent, moves sideways through 2010, and ends 2011 near 90 percent. The years 2008 and 2011 are shaded, and the labels above the chart give each year’s APR: −3.05 percent in 2007, 30.16 in 2008, 33.45 in 2009, 1.82 in 2010 and 10.58 in 2011. Its legend gives an APR of 0.136776 and a Sharpe ratio of 1.259478. The bottom chart is Example 4.4’s compounded cumulative return, which rises steadily from zero to about 1,460 percent. Its labels give 97.17 percent in 2007, 161.09 in 2008, 91.87 in 2009, 36.84 in 2010 and 15.04 in 2011, and its legend gives 0.731553 and 4.713284. The title calls the redraw exploratory and the panel a panel of survivors, and the note says no cost is charged.](../docs/figures/khandani_lo_book_two.png)

*Example 4.3’s cumulative return, the book’s Figure 4.4, and Example 4.4’s on its own axis, both compounded and before costs, over the 1,260 days of Chan’s 2012 panel. The shaded years are the two the book names.*

The book names 2008, “the year of Lehman Brothers’ bankruptcy”, and 2011 (location 2110). The other three years are on the chart too. Example 4.3 lost 3.05 percent in 2007 and earned 33.45 percent in 2009, more than in 2008, and 1.82 percent in 2010. Example 4.4’s APR falls in every year after 2008, from 161.09 percent to 91.87, 36.84 and 15.04.

## Lesson 2: the match needs one stock’s odd prices

This repository checks every price series before a run reads it, with what it calls the scale-break guard. The guard refuses a window in which a stock’s price changes by a ratio too far from 1 to be an ordinary move, the mark a split or a data error leaves. Over this window it would refuse 17 stocks’ closes. Most of the days it flags fall in the 2008 crisis, such as AIG’s collapse on 2008-09-15, which are moves a reversal rule is meant to trade.

One of them is not. CAH closes at 19.96 on 2009-08-31, 14.50 on 2009-09-01 and 23.57 on 2009-09-02. A fall that the next day more than undoes reads as a data error or a corporate action rather than a crash. The script computes across it, and so does the transcription, because removing it misses the book. Without CAH, Example 4.3 gives an APR of 13.26 percent and a Sharpe ratio of 1.2267, which would print as 13.3 and 1.2. Neither lands.

A cleaner file would miss Chan’s figures. So the reproduction checks the computation on his file, odd prices included, and says nothing about what the rule would have earned on correct prices. That is why the guard does not run for this script, a decision made for reproducing it and not for any other rule on the panel.

## Lesson 3: most of the rise from 0.25 to 1.3 is the data and the window

The first book’s rule earned 0.2510 on 2006, and the second book’s earns 1.259478 on 2007 to 2011, which is 1.2595 at the four decimals the other rows carry. Three things changed at once: the rule, the file and the window. Running each book’s rule on the other’s data separates them.

```math
\begin{array}{l|l|r}
\text{Rule} & \text{File and window} & \text{Sharpe ratio} \\ \hline
\text{First book's} & \text{first book's file, 2006} & 0.2510 \\
\text{Second book's, returns taken before the cut} & \text{first book's file, 2006} & 0.4170 \\
\text{Second book's} & \text{first book's file, 2006} & 0.5484 \\
\text{First book's} & \text{the panel, 2007 to 2011} & 1.2219 \\
\text{Second book's, Example 4.3} & \text{the panel, 2007 to 2011} & 1.2595
\end{array}
```

All five are before costs. The first book’s file is `SPX_20071123.mat`, the 500 stocks in the S&P 500 on 2007-11-23, and its window is the 251 trading days of 2006.

Read from the top, the second book’s rule moves the first book’s year from 0.2510 to 0.5484, by 0.2974. That leaves 0.7111 still to go to Example 4.3’s 1.2595, more than twice what the rule moved. Read from the bottom, the first book’s rule on the panel earns 1.2219, close to 1.2595 on the same days. Both orders say the same thing. The file and the window carry most of the rise.

The rule’s own 0.2974 is not all weighting either. The cut alone carries 0.1313 of it, 0.44 of the rule’s share. Taking returns before the cut lets 2006-01-03 and 2006-01-04 earn, and those two days lost 0.48 and 0.14 percent, which brings the figure down to 0.4170. On one year of 251 days, two days move a Sharpe ratio by about a third.

What changed in the data is not only the years. The panel carries 2012-04-24’s membership back five years, to 2007. The first book’s file carries 2007-11-23’s back under two, to 2006. A longer stretch of survivors leaves out more of the companies that failed along the way, and nothing here measures how much of the 1.2219 that is.

## Lesson 4: costs still take most of the edge, and the panel shows why they take less

Chan prints both of this book’s figures before costs. Charging the first book’s rule 5 basis points on each side of every trade, with the first day’s trades charged too, brings it from 1.2219 to 0.3797 on the panel. On 2006 the same charge took it from 0.2510 to −3.2337. Chan’s own −3.19 for 2006 treats the first day differently, which Lesson 2 of the earlier post explains.

An average day explains the difference. Each figure below is in basis points of the rule’s average gross position.

1. **The trading barely changes.** On the panel the rule trades 1.4574 times its position a day, against 1.4505 on 2006, so the cost is 7.2868 basis points a day against 7.2525.
2. **The profit is about twenty times larger.** It earns 10.5234 basis points a day on the panel, against 0.5276 on 2006.

So on 2006 the cost was 13.7453 times a day’s profit, and on the panel it is 0.6924 of it. The rule pays its costs on the panel and keeps less than a third of its daily profit. Nothing here charges the second book’s rule, which also sets every weight again each day.

Example 4.4 would pay more. Chan writes that its costs “will be doubled, because we are trading twice a day instead of just once a day” (location 2135), and nothing here charges one.

## What this replication cannot say

Five questions are beyond it.

1. **What the rule earned on the index as it stood each day.** Every stock on the panel was in the S&P 500 on 2012-04-24, and nothing here measures what survivorship adds to this rule over 2007 to 2011.
2. **Whether 2008 to 2011 is out of sample in Chan’s sense.** He calls it “a true out-of-sample test, as the strategy was published in 2007” (location 2110). It is out of sample in time, but the stocks were chosen with 2012’s membership.
3. **What costs would take from Example 4.4.** It trades twice a day and nothing charges it.
4. **Whether the open is tradeable on its own signal.** Example 4.4 sets its weights from today’s open and enters at that same open. Chan names the noise that brings at location 2135, and nothing here measures it.
5. **Whether the rule pays today.** The window ends in 2011, and the result is exploratory.

## What this means for a trader

One habit for each lesson.

1. **Check the rounding before trusting a match.** A figure that sits 0.0095 from its rounding point lands or misses on a detail, so know how much room each one has.
2. **Keep the odd prices when reproducing, and remove them when trading.** A reproduction has to run on the author’s file as it was. A decision about the rule needs prices that have been checked.
3. **Swap one thing at a time.** When the rule, the file and the window all change, run each rule on the other’s data before crediting the rule with the difference.
4. **Read a cost as a share of the day’s profit.** The same turnover cost 13.7453 times a day’s profit on one file and 0.6924 of it on another, so a cost that ruins a rule on one sample can leave it standing on the next.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.3 and 4.4, and Kindle locations 2087, 2110, 2124, 2135 and 2890.
2. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Example 3.7.
3. Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
4. `andrewlo_2007_2012.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the two examples](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo_book_two.py), [the first book’s rule](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo_book_two_figures.py), with the checks behind [the examples’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo_book_two.py), [the first book’s](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo_book_two_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-19-the-khandani-lo-reversal-on-the-2012-panel-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
