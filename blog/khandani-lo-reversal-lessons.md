# Chan’s reversal reproduces on his 2012 file, and most of its Sharpe ratio’s rise from 0.25 to 1.3 is the data and the window

*Algorithmic Trading runs the first book’s reversal again on 497 stocks from 2007 to 2011. Every return and Sharpe ratio Chan prints reproduces on his own file, and the new rule explains less of the jump in its Sharpe ratio than the new data and window do.*

## Why look at the reversal a second time

The [post on trading costs and failed companies](https://github.com/l3a0/quantitative-trading/blob/main/blog/survivorship-and-transaction-costs.md) reproduced a rule Amir Khandani and Andrew Lo published (Khandani & Lo, 2007), as Example 3.7 of Ernest Chan’s first book, *Quantitative Trading* (Chan, 2021). Each day it buys the S&P 500 stocks that fell most against the market and sells short the ones that rose most.

The Sharpe ratio measures how well a strategy pays for its risk: the average daily return over its standard deviation, scaled to a year, with no interest rate subtracted. Over 2006 the rule’s Sharpe ratio was 0.2510 before costs. A basis point is a hundredth of a percent. Charging 5 basis points on every buy and every sell, so that a round trip pays twice, took it to −3.1884, the figure behind Chan’s printed −3.19. That post works through the cost in detail, and Lesson 4 here draws on it.

Chan’s second book, *Algorithmic Trading*, brings the rule back as its lesson on cross-sectional mean reversion (Chan, 2013, Kindle location 2087). A stock is judged against its peers on the same day rather than against its own past, so the bet is that a stock that did worse than the rest will do better next, “and vice versa”. He runs it on a newer file over 2007 to 2011 and reports a Sharpe ratio of 1.3, about five times the first book’s, and an intraday version with 4.7 (locations 2110 and 2135).

### What the reproduction found

Chan published the MATLAB script, `andrewlo_2007_2012.m`, and the data file it reads. This repository keeps the file’s contents as one table per stock, and together the tables rebuild the file’s open, high, low, close and volume arrays exactly. It ran a line-by-line Python transcription of the script on those tables. Every return and Sharpe ratio the book prints for the two examples reproduces, and so do Example 4.4’s APR and Sharpe ratio as the script’s closing comment records them, at six decimals.

**Every result here is exploratory.** Reproducing Chan’s figures uses the 2007 to 2011 data to check a rule somebody else chose, so it can say whether his numbers follow from his file and nothing about whether the rule pays today. **Every figure is also about survivors.** The file holds 497 stocks that were in the S&P 500 in late 2011, and the run treats them as the index on every earlier day it has a price for them. A company that was out of the index for all of late 2011 is not in the file.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

Each day the rule computes every stock’s return, subtracts the average return of all the stocks, and sets the stock’s weight to the negative of that difference. A positive weight is a dollar amount bought and a negative one a dollar amount sold short. The second book then divides each day’s weights by the sum of their absolute values, so on every day that has a return the dollars bought and the dollars sold short come to $0.50 each, $1 in all. That total is the gross, and Chan writes that the rule invests “the same total gross capital of $1” each day (location 2087).

**Example 4.3** sets the weights at the close and holds them to the next close. **Example 4.4** keeps the rule and changes the signal and the holding (location 2124). Its weights come from the overnight move, from yesterday’s close to today’s open. It enters at the open and closes everything at the same day’s close. That differs from the first book’s Example 3.8, which the earlier post covers. Example 3.8 sets its weights from the opens and holds them from one open to the next.

Chan calls the rule “almost perfectly dollar neutral” (location 2110), meaning the dollars bought match the dollars sold short. Each weight is minus a stock’s return against the day’s average return, so the weights sum to zero, and dividing them by the gross keeps them summing to zero. They do on every day of both examples, to within the rounding of the arithmetic.

The second book’s rule differs from the first book’s in five ways.

1. **The weights are scaled to a gross of 1 each day.** The first book divides them by the count of stocks priced.
2. **A stock with no price gets no weight at all**, where the first book gives it a weight of 0. Both leave it out of the day’s profit, so the difference could matter only to a cost, and the second book charges none.
3. **No cost is charged.** The script’s cost lines are commented out.
4. **The window is cut before any return is taken.** The first book takes returns on its whole file and cuts the profit to the window afterwards. Here the window’s first day has no earlier price to take a return from, so the first day or two earn nothing, as the paragraph below counts.
5. **The Sharpe ratio uses MATLAB’s own mean and standard deviation**, where the first book uses Chan’s own functions, whose mean skips a missing day and whose standard deviation counts it as a zero. No series here has a missing day, so this difference moves no figure.

### Where the prices and the script come from

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputDataOHLCDaily_stocks_20120424.mat`, saved on 2012-04-25. It holds the daily prices of 497 stocks, and the script reads their opens and closes. This post calls the file the panel.

The script cuts the panel to 1,260 trading days, from 2007-01-03 to 2011-12-30. The book says the run starts on January 2, 2007, which was a market holiday. Because the cut comes before any return is taken, Example 4.3’s first two days earn nothing: its first day has no return, and its second holds the first day’s empty weights. Example 4.4’s first day earns nothing for the same reason.

This repository transcribed the script from a public copy of Chan’s code, `ericnberwick/EpchanPreview` at commit `e4bc46f`, and a second public copy holds the same script byte for byte.

## Lesson 1: every return and Sharpe ratio Chan prints reproduces on his own file

The book reports each example’s APR, the compounded annual return. Compounding means each day’s return is earned on the capital the earlier days left, so the growth multiplies rather than adds. Here is each figure, computed, beside the script’s comment and the book.

```math
\small\begin{array}{l|r|r|r}
\text{Example 4.3} & \text{Computed} & \text{Script} & \text{Book} \\ \hline
\text{APR} & 0.136776 & 13.7\% & 13.7\% \\
\text{Sharpe ratio} & 1.259478 & 1.3 & 1.3 \\
\text{APR in 2008} & 0.301647 & \text{none} & 30\% \\
\text{APR in 2011} & 0.105778 & \text{none} & 11\%
\end{array}
```

```math
\small\begin{array}{l|r|r|r}
\text{Example 4.4} & \text{Computed} & \text{Script} & \text{Book} \\ \hline
\text{APR} & 0.731553 & 0.731553 & 73\% \\
\text{Sharpe ratio} & 4.713284 & 4.713284 & 4.7
\end{array}
```

The script prints no yearly figure, so each year’s APR applies the script’s own APR formula to that year’s days, taken from the full five-year run rather than from a run of that year alone.

The jump from 1.3 to 4.7 comes from the average return, since the two examples have about the same standard deviation. Scaled to a year, Example 4.3’s daily returns average 0.1338 with a standard deviation of 0.1063, and Example 4.4’s average 0.5565 with a standard deviation of 0.1181. These are averages of daily returns, not the compounded APRs in the tables. The Sharpe ratio is the average over the standard deviation, so four times the average return with a similar standard deviation gives a ratio nearly four times as large.

Location 2890 sets the same 4.7 against cross-sectional momentum, which instead buys the stocks that rose most against their peers. The [post on cross-sectional momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md) covers that comparison.

### How much room each rounding has

Three figures sit close to the point where the printed digit would change, given the precision each one is printed at.

1. Example 4.3’s Sharpe ratio sits 0.0095 above 1.25, below which the book would print 1.2.
2. Its APR in 2011 sits 0.08 percentage points above 10.5 percent, below which the book would print 10.
3. Example 4.4’s APR is 0.7315525016, which sits 1.6 × 10⁻⁹ above the point where the script’s sixth decimal would round down to 0.731552.

The third is the tightest. A transcription whose APR came out lower than this one by more than that would print 0.731552 instead.

### The cumulative return and each year’s APR

The figure below redraws the book’s Figure 4.4, Example 4.3’s cumulative return, and draws Example 4.4’s below it on a vertical scale of its own. The script’s two plotting commands both compound the daily returns, so both charts do too. Each year’s APR sits above that year’s stretch of the chart. Nothing compares the redraw with the chart in the book, so it is a redraw of the script’s plot rather than a checked copy.

![Two charts on one shared date axis from January 2007 to December 2011. The top chart is Example 4.3’s compounded cumulative return. It drifts slightly below zero through 2007, climbs through 2008 and 2009 to about 70 percent, moves sideways through 2010, and ends 2011 near 90 percent. The years 2008 and 2011 are shaded, and the labels above the chart give each year’s APR: −3.05 percent in 2007, 30.16 in 2008, 33.45 in 2009, 1.82 in 2010 and 10.58 in 2011. Its legend gives an APR of 0.136776 and a Sharpe ratio of 1.259478. The bottom chart is Example 4.4’s compounded cumulative return, which rises steadily from zero to about 1,460 percent. Its labels give 97.17 percent in 2007, 161.09 in 2008, 91.87 in 2009, 36.84 in 2010 and 15.04 in 2011, and its legend gives 0.731553 and 4.713284. The title calls the redraw exploratory and the panel a panel of survivors, and the note says no cost is charged.](../docs/figures/khandani_lo_book_two.png)

*Example 4.3’s cumulative return, which the book draws as its Figure 4.4, above Example 4.4’s on a scale of its own. Both are compounded and before costs, over the 1,260 days the script cuts from Chan’s 2012 panel. The shaded years are the two the book names.*

The book names 2008, “the year of Lehman Brothers’ bankruptcy”, and 2011 (location 2110). The chart shows the other three years too. Example 4.3’s APR was −3.05 percent in 2007, 33.45 percent in 2009 and 1.82 percent in 2010, so 2009 beat 2008’s 30.16 percent. Example 4.4’s APR falls in every year after 2008, from 161.09 percent to 91.87, 36.84 and 15.04.

## Lesson 2: the match needs one stock’s odd prices

Many runs in this repository check each price series before reading it. The check refuses a window in which a stock’s price changes by a ratio too far from 1 to be an ordinary move, the mark a split or a data error leaves. Over this window it would refuse 17 stocks’ closes and 14 stocks’ opens. Most of the closes it flags fall in the 2008 crisis, such as AIG’s collapse on 2008-09-15. Those are moves a reversal rule is meant to trade.

One of them is not. CAH closes at 19.96 on 2009-08-31, 14.50 on 2009-09-01 and 23.57 on 2009-09-02. The check flags the rise on 2009-09-02, and the fall before it stays inside the check’s bounds. A fall that the next day more than undoes reads as a data error or a corporate action, such as a split or a spin-off, rather than a crash. Chan’s script takes returns across those days, and so does the transcription, because dropping CAH makes the figures miss the book’s. Without CAH, Example 4.3 gives an APR of 13.26 percent and a Sharpe ratio of 1.2267, which would print as 13.3 and 1.2, so neither matches the book’s 13.7 and 1.3.

![An animated whiteboard sketch titled “The bounce the rule bought”, drawn slowly stroke by stroke and held for twelve seconds when finished. Its marks are drawn to one scale from the run. A grey price axis labelled “CAH’s close” rises at the left, and a grey time axis runs along the bottom with ticks labelled “2009-08-31”, “09-01” and “09-02”. The price axis carries ticks labelled “19.96”, “14.50” and “23.57” at the three closes, and one labelled “11.00” at its foot, so it starts at 11 rather than 0. Then three black dots stand at those closes above the three days, the middle one lowest and the last one highest. A black arrow runs down from the first dot to the second, labelled “× 0.7265: inside the check’s bounds”. A red arrow runs up from the second dot to the third, labelled “× 1.6255: past 1.6, flagged”. A thick green bar sits just under the second dot, labelled “bought at the close: 3.17 cents of the $1”. A green bracket to the right spans the rise from the second dot’s height to the third’s, labelled “up 62.55 percent: 1.98 cents earned the next day”. A grey line along the bottom reads “without CAH: 13.26 percent and 1.2267, neither matches the book”.](../docs/figures/khandani_lo_book_two_sketch_cah_bounce.gif)

*Drawn to one scale from the run, on a price axis that starts at 11 rather than 0, so both moves look bigger than they are and the labels give their size. The check flags a day on which the close changes by a ratio above 1.6 or below 1 / 1.6, which is 0.625. The black arrow is the fall it lets through, and the red arrow is the rise it flags. The green bar is what Example 4.3 bought at the middle close, and the green bracket is the rise that weight earned on.*

So the transcription does not run the check. This repository made that decision to reproduce this one script, and it applies to no other rule run on the panel. The reproduction checks the computation on Chan’s file, odd prices included, and says nothing about what the rule would have earned on correct prices.

## Lesson 3: most of the rise from 0.25 to 1.3 is the data and the window

The first book’s rule had a Sharpe ratio of 0.2510 over 2006, and the second book’s has 1.259478 over 2007 to 2011, which is 1.2595 at the four decimals the table below uses. The rule, the file and the window all changed at once. Running each book’s rule on the other’s data separates them.

```math
\small\begin{array}{l|l|r}
\text{Rule} & \text{Data} & \text{Sharpe} \\ \hline
\text{First book's} & \text{2006} & 0.2510 \\
\text{Second, returns before the cut} & \text{2006} & 0.4170 \\
\text{Second book's} & \text{2006} & 0.5484 \\
\text{First book's} & \text{panel} & 1.2219 \\
\text{Second book's, Example 4.3} & \text{panel} & 1.2595
\end{array}
```

All five are Sharpe ratios before costs. In the data column, 2006 is the first book’s file, `SPX_20071123.mat`, the 500 stocks in the S&P 500 on 2007-11-23, over the 251 trading days of 2006. The panel is Chan’s 2012 file over 2007 to 2011.

Start from the first book’s file and year and change only the rule. The second book’s rule raises the Sharpe ratio there from 0.2510 to 0.5484, by 0.2974, the first and third rows. Example 4.3 reaches 1.2595, so 0.7111 of the rise is still left, more than twice what the change of rule gave. Start instead from the panel and change only the rule. The first book’s rule has a Sharpe ratio of 1.2219 there, close to Example 4.3’s 1.2595 on the same days, the last two rows. Both comparisons say the file and the window carry most of the rise.

Part of that 0.2974 comes from cutting the window before taking returns, rather than from how the weights are set. When the window is cut first, the year’s first two days, 2006-01-03 and 2006-01-04, earn nothing, because the first has no return and the second holds the first day’s empty weights. With returns taken before the cut, those two days lose 0.48 and 0.14 percent, and the Sharpe ratio comes down to 0.4170, the second row. So zeroing two losing days raises the figure from 0.4170 to 0.5484, by about a third. That is 0.1313 of the 0.2974, or 0.44 of it. Both come from the unrounded figures, and the rounded rows give 0.1314. One year holds only 251 days, so two of them can move a Sharpe ratio that far.

The data differ in more than the years. The panel carries a list of the index from late 2011 back almost five years, to 2007. The first book’s file carries 2007-11-23’s membership back under two years, to 2006. The longer the stretch, the more of the companies that left the index along the way are missing from the file, whether they failed, were bought or left for another reason. No test here measures how much leaving them out moves the 1.2219.

## Lesson 4: after costs, the first book’s rule keeps under a third of its profit on the panel and loses money over 2006

The second book prints every figure before costs, and no run here charges its rule, though it sets every weight again each day just as the first book’s does. So this lesson charges the first book’s rule. At 5 basis points on every buy and every sell, with the first day’s trades charged too, its Sharpe ratio falls from 1.2219 to 0.3797 on the panel. Over 2006 the same charge took it from 0.2510 to −3.2337. That is lower than the −3.1884 quoted at the top of this post, which reproduces Chan’s −3.19, because the −3.1884 leaves the first day’s trades uncharged, as Lesson 2 of the post on trading costs explains.

An average day explains the difference. Each profit and cost below is in basis points of the rule’s average gross position.

1. **The trading barely changes.** On the panel the rule trades 1.4574 times its average gross position a day, against 1.4505 over 2006. At 5 basis points on every dollar traded, that costs 7.2868 basis points a day against 7.2525.
2. **The profit is about twenty times larger.** It earns 10.5234 basis points a day on the panel, against 0.5276 over 2006.

So over 2006 the cost was 13.7453 times a day’s profit, and on the panel it is 0.6924 of it. The rule pays its costs on the panel and keeps less than a third of its daily profit.

![An animated whiteboard sketch titled “Same trading, twenty times the profit”, drawn slowly stroke by stroke and held for twelve seconds when finished. Its bars are drawn to one scale from the run. A grey axis runs along the bottom with ticks labelled “0”, “5” and “10”, and beneath it “basis points a day, of the average gross position”. Under the heading “2006, the first book’s file” two bars start at zero: a red bar labelled “cost 7.2525” and, below it, a short green bar labelled “profit 0.5276”. Under the heading “2007 to 2011, the panel” a red bar labelled “cost 7.2868”, about as long as the first, sits above a long green bar labelled “profit 10.5234”. A grey note at the top right reads “trades 1.4505 and 1.4574 times the position a day”. On 2006’s profit row a red hatched stretch runs from the end of the short green bar to where the red cost bar above it ends, labelled “cost is 13.7453 times the profit”. On the panel’s cost row a brown bracket runs from the end of the red cost bar to where the green profit bar below it ends, labelled “kept: 3.2366, less than a third”. A grey line at the bottom reads “first book’s rule, 5 basis points on every buy and sell, first day’s trades charged”.](../docs/figures/khandani_lo_book_two_sketch_average_day.gif)

*Drawn to one scale from the run, in basis points of the rule’s average gross position. Each red bar is the average day’s cost and each green bar the average day’s profit. The red hatching is how far 2006’s cost passes its profit, and the brown bracket is what the panel keeps.*

Example 4.4 would pay more. Chan writes that its costs “will be doubled, because we are trading twice a day instead of just once a day” (location 2135), and it is charged no cost here.

## What this replication cannot say

Five questions are beyond it.

1. **What the rule earned on the index as it stood each day.** Every stock on the panel was in the S&P 500 in late 2011, and nothing here measures how survivorship moves this rule over 2007 to 2011.
2. **Whether 2008 to 2011 is out of sample in Chan’s sense**, meaning data the rule was not designed on. He calls it “a true out-of-sample test, as the strategy was published in 2007” (location 2110). It is out of sample in time, but the stocks were chosen from the index as it stood in late 2011, at the end of the window.
3. **What costs would take from Example 4.4.** It trades twice a day and is charged no cost.
4. **Whether a trade can get the open price that set its weight.** Example 4.4 sets its weights from today’s open and enters at that same open, so the price that sets a weight may not be a price the trade can get. Chan calls this “trading signal noise” at location 2135, and the run does not measure it.
5. **Whether the rule pays today.** The window ends in 2011, and the result is exploratory.

## What this means for a trader

One habit for each lesson.

1. **Check the rounding before trusting a match.** A figure that sits 0.0095 from its rounding point can match or miss the printed value on a small detail, so check how close each one sits to its rounding point.
2. **Keep the odd prices when reproducing, and correct or exclude them when trading.** A reproduction has to run on the author’s file as it was. A decision about the rule needs prices that have been checked.
3. **Swap one thing at a time.** When the rule, the file and the window all change, run each rule on the other’s data before crediting the rule with the difference.
4. **Read a cost as a share of the day’s profit.** Nearly the same amount of trading cost 13.7453 times a day’s profit on one file and 0.6924 of it on another, so a cost that ruins a rule on one sample can leave it standing on the next.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.3 and 4.4, and Kindle locations 2087, 2110, 2124, 2135 and 2890.
2. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Example 3.7.
3. Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
4. `andrewlo_2007_2012.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the two examples](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo_book_two.py), [the first book’s rule](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/khandani_lo_book_two_figures.py), with the checks behind [the examples’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo_book_two.py), [the first book’s](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_khandani_lo_book_two_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-19-the-khandani-lo-reversal-on-the-2012-panel-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
