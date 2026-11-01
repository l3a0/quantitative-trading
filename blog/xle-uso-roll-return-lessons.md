# Chan’s XLE against USO trade reproduces on his own files, and a third of its return comes from the days it bet on backwardation

*Chan holds a fund of oil producers against a fund of oil futures, in whichever direction crude oil’s roll return favours, and reports 16 percent a year. On his own files every figure he prints reproduces. The trade bets on contango on most days, yet the few days it bets on backwardation earn a third of its return, and on those days USO’s own rise dwarfs the roll return the signal reads.*

## Why trade a fund of producers against a fund of futures

A futures contract earns two things as it ages: what the commodity’s price does, and a roll return, which comes from the contract’s price converging on the commodity’s price by expiry. Ernest Chan’s *Algorithmic Trading* shows one way to collect the roll return alone. He says to “buy the underlying asset and short the futures” when the roll return is negative, which he calls contango, and to do the reverse when it is positive, which he calls backwardation (Chan, 2013, Kindle edition, p. 208). The commodity’s own moves cancel between the two legs. Either way, what is left is a gain the size of the roll return. The [post on long GLD and short gold futures](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gc-lessons.md#why-own-the-metal-and-short-the-future) runs that arbitrage on gold, where a fund does hold the metal.

The arbitrage needs a way to hold the commodity itself, and for crude oil none exists. “There are no ETFs that hold other physical commodities as opposed to commodities futures”, Chan writes, because storing them costs too much (p. 209). USO, the oil fund, “doesn’t actually own oil. It invests in oil futures contracts” (p. 142). So Chan offers what he calls “a less exact form of arbitrage” (p. 209). A fund of companies that produce a commodity “usually cointegrates with the spot price of that commodity” (p. 178), meaning the two move together over time. The spot price is the price for delivery today. By that argument, XLE, the energy sector fund, can stand in for crude’s spot price.

The trade pairs XLE with USO rather than directly with crude oil futures, whose symbol is CL. The reason is a timing one: “XLE and CL have different closing times”, while USO closes with XLE and “contains nothing but front month contracts of CL” (p. 209), meaning the contracts nearest expiry. The rule is two sentences.

1. “Short USO and long XLE whenever CL is in contango”, meaning later contracts are priced above earlier ones.
2. “Long USO and short XLE whenever CL is in backwardation”, the reverse.

Chan reports “a very respectable 16 percent” a year from April 26, 2006, to April 9, 2012, “with a Sharpe ratio of about 1” (p. 209).

### What the reproduction found

Chan published the trade’s MATLAB script, `XLE_CL_rollReturn.m`, and this repository transcribed it into Python line by line and ran it on the two files it loads.

The results fall into five groups.

1. **The pair stands in for crude’s spot and its futures only by the book’s argument.** Chan makes both claims, and this replication tests neither.
2. **Every printed figure lands.** Each of the five figures in the script’s closing comment, and each of the book’s two, rounds to the printed value on Chan’s own files.
3. **The trade mostly bets on contango, and holds nothing at first.** It is short USO and long XLE on 1,129 days, the reverse on 244, and holds nothing for its first 123 days.
4. **The XLE closes are not what a holder earned.** Chan’s fund file adjusts for dividends by subtraction, and nothing in the repository measures how much that moves XLE’s returns.
5. **The few backwardation days earn a third of the return.** The trade’s daily returns sum to 0.308117 over those days, of 0.946538 over all of Chan’s dates. On those days USO rose 0.532304 in log terms, while the roll return the signal reads came to 0.072380.

**Every result here is exploratory.** Chan chose the funds, the signal, the rule and the dates, and the reproduction runs them on his own files. It can say whether his numbers follow from those files, and nothing about whether the trade would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The funds, the ratio and the files

The [post on Chan’s crude oil calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md#the-spread-the-signal-and-the-file) builds up a futures contract, its expiry, the roll from one contract to the next, the roll return, and contango and backwardation. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#the-model-and-the-files) works through the model behind the roll return, which Chan calls γ. This post covers only what this script does differently.

**The signal is a ratio of two contracts.** On each day the script reads one CL contract, which it calls the front, and the contract expiring a month after it, the back. The ratio is the back’s price over the front’s. Above 1 is contango, and below 1 is backwardation.

The book’s model makes this ratio a reading of the roll return. In that model, a contract a month further out is priced lower by one month’s roll return, in log terms. A positive roll return therefore puts the back below the front, which is backwardation, and a negative one puts it above, which is contango. So the roll return, annualised, is about 12 times the log of the front over the back. That is the ratio turned upside down, so a ratio above 1 gives a negative roll return.

```math
\gamma_t \approx 12 \ln \frac{F_{\text{front}}(t)}{F_{\text{back}}(t)}
```

That reading assumes the two contracts are a month apart, which on CL they are. Lesson 5 uses it.

**The front window is the script’s own.** A row here is one trading day in Chan’s CL file. Each contract is the front from 40 rows to 10 rows before its last priced row, and no earlier than the row after the previous front ends. The script’s comment calls these days before expiration, but the script finds each expiry as the last day the file prices a contract. CL contracts expire a month apart, which in this file is fewer than 30 rows, the distance from a window’s 40-row start to its 10-row end. So each contract’s 40-row start falls before the previous front’s 10-row end. The 40 decides only the front window of CL-2007F, the January 2007 contract, and every later contract starts on the row after the previous one ends. That differs from the crude oil calendar spread, which holds named pairs of contracts on a schedule of its own. On the days outside every front window the ratio is undefined and the trade holds nothing.

**The rule and its returns.** Each day the trade takes its position from the ratio and earns on that position the next day, on each fund’s percentage change. Each fund carries half the capital, so the day’s return is the sum of the two legs divided by 2. Nothing is charged for trading. The APR is the compounded return per year, taking a year as 252 trading days. The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate.

### The fund file, the CL file and the days they share

The script loads two of Chan’s files, both recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md).

1. **`inputData_ETF.mat`**, saved 2012-04-10. USO and XLE hold 1,500 closes each from 2006-04-26 to 2012-04-09, with none missing. The [post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#the-test-and-the-file) read the same file to test whether a gold fund, a fund of gold miners and USO move together. Its test of the gold fund against the fund of gold miners pairs a producers’ fund with a commodity fund, as this trade does, though the gold fund holds the metal and USO holds futures.
2. **`inputDataDaily_CL_20120502.mat`**, saved 2012-05-03. It holds 89 CL contracts, one for each month from CL-2007F to CL-2014K, the May 2014 contract, over 2,867 days from 2000-11-20. It holds no spot price.

The two calendars share 1,498 days. The fund file holds 2006-07-03 and 2006-11-24, which the CL file lacks. The first front window opens on 2006-10-20, so the ratio is defined on 1,375 of the shared days.

### Chan’s later save of the CL contracts

A later save of the same set of CL contracts, `inputDataDaily_CL_20120813.mat`, saved 2012-08-14, is the file Chan’s Example 5.3 reads to fit γ. This section compares the ratio on the later save with the ratio on the CL file, and Lesson 2 compares γ with the ratio on the later save.

The later save of 2012-08-14 holds every price of the CL file unchanged, and it gives the same ratio on all 1,375 days. The [post on the crude oil reversal and momentum rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#lesson-1-both-figures-land-and-a-save-a-week-later-prints-the-same-to-the-books-precision) found that a save dated a week later moves every close over that post’s dates, because a continuous future, one price series stitched from contract after contract, is rewritten at every roll. Each contract in the CL file holds only that contract’s own prices, so Chan’s single contracts were not rewritten that way.

The rules that decide each result are in [Entry 39 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-39-xle-against-uso-signed-by-crude-oils-contango-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the pair stands in for crude’s spot and its futures only by the book’s argument

The trade rests on two claims from the book, and this replication tests neither.

1. **XLE stands in for crude’s spot price.** Chan says a producers’ fund usually cointegrates with the spot (p. 178). The file the script loads holds no spot price. Chan’s later save of the same CL contracts, on 2012-08-14, holds a spot price on every one of the 1,498 days the fund file and the CL file share, but nothing here tests XLE against it.
2. **USO holds the front contract.** The script’s ratio reads its own front, which is not always the contract nearest expiry. On 734 of the 1,375 days with a ratio, the script’s front is the nearest contract the file prices that day. On the other 641 it is the second-nearest. The script moves to the next contract 10 rows before the current one’s last price, and for those 10 rows the old contract is still priced. So “front month” in the signal means the contract the script reads, which need not be the one USO held that day.

![A whiteboard sketch titled “The front moves on before the last price”, drawn slowly. A grey axis of the CL file’s trading days runs along the bottom from “Oct 2006” to “Jan 2007”. On the upper row, a thin grey bar runs in from the left and ends at “last price 12-19”. It marks the days the file prices CL-2007F. A thick black bar over its left part is labelled “CL-2007F front, 10-20 to 12-05: 31 rows”. On the lower row, a second thick black bar starts on the next trading day and is labelled “CL-2007G front, 12-06 to 01-05: 20 rows”, with grey words under it, “the February 2007 contract”. Between the rows, a brown brace spans the days from 12-06 to 12-19, where the grey bar still runs above the second black bar, with brown words “CL-2007F still priced: 10 rows” and “so the front is the second-nearest”. Black words at the bottom read “of the 1,375 days with a ratio, the front is the nearest priced contract” and “on 734 days and the second-nearest on 641”. Every bar sits at its own trading days on the axis. The finished drawing holds for twelve seconds.](../docs/figures/xle_uso_roll_return_sketch_front_handover.gif)

Until both claims are tested, treat the trade as a bet on the two funds. From 2006-04-26 to 2012-04-09 the two funds went opposite ways. In Chan’s fund file, USO’s close fell from 69.54 to 38.97, or 43.9603 percent. XLE’s rose from 51.97 to 69.61, or 33.9427 percent. Lesson 4 explains why XLE’s first close in that file may sit below the price that traded, so its rise there may be larger than the traded price’s. A trade mostly short USO and long XLE gains from both moves, whether or not either move came from the roll return. Lesson 5 splits those days by the view the trade held, contango or backwardation, and sets USO’s move on each group’s days beside the roll return the ratio implies.

## Lesson 2: every printed figure lands on Chan’s files

The script’s closing comment prints five figures. A figure lands when the computed value rounds to the printed one at the decimals printed, and all five do.

```math
\small\begin{array}{l|r|r}
\text{Figure} & \text{Computed} & \text{Comment} \\ \hline
\text{Average annual return} & 0.159231 & 0.1592 \\
\text{Sharpe ratio} & 1.046596 & 1.05 \\
\text{APR} & 0.159102 & 0.1591 \\
\text{Maximum drawdown} & -0.192321 & -0.192321 \\
\text{Longest drawdown} & 487 & 487
\end{array}
```

The average annual return is 252 times the mean daily return, without compounding. The maximum drawdown is the deepest fall from a previous high, and the longest drawdown is the most days in a row spent below a previous high. The book prints two of the five, an APR of 16 percent and a Sharpe ratio of “about 1”. The script’s APR and Sharpe ratio round to them, and the book’s dates are the fund file’s first and last days, so the text fits the script’s run.

Two caveats come with the match.

1. **The order of the run.** A first run printed all five figures before the plan for this replication wrote down when a figure lands. The plan then took a rule that earlier replications here had already used, so nothing in it was chosen to fit. The replication ran one reading of the script, so it had no set of readings to pick a match from.
2. **The Sharpe ratio’s divisor.** The run computes the standard deviation with n, the number of days, as its divisor. Using n − 1 instead gives a Sharpe ratio of 1.046247, which also rounds to 1.05. The printout cannot tell the two apart.

### How often the ratio and Example 5.3’s γ call the same view

The book’s rule is “whenever CL is in contango”, and the script decides that from one pair of contracts. Chan’s Example 5.3 measures the roll return another way, as γ fitted across the five nearest contracts each day. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#lesson-4-the-average-hides-a-roll-return-that-drifts-and-changes-sign) shows that from 2004-11-22 to 2012-08-13, CL’s γ is mostly negative, which is contango, and changes sign 29 times. On the later save of 2012-08-14, where both the ratio and γ can be read, they mostly agree.

1. **Same view on 1,354 days** of the 1,373 on which the ratio is not exactly 1.
2. **Contango by the ratio and backwardation by γ** on 13.
3. **Backwardation by the ratio and contango by γ** on 6.

On the 2 days the ratio is exactly 1 it calls no view, and γ calls backwardation on both.

## Lesson 3: mostly contango, and nothing held for the first 123 days

Of the 1,375 days with a ratio, the trade holds contango’s position on 1,129 and backwardation’s on 244. On 2 days, 2008-02-07 and 2008-08-07, the ratio is exactly 1 and the trade holds nothing. So the trade is mostly short USO and long XLE.

It also holds nothing on its first 123 days, the days the fund file and the CL file share from 2006-04-26 to 2006-10-19. The CL file’s first contract is CL-2007F, and its front window opens on 2006-10-20. Earlier contracts are not in the file, so no ratio exists before then. Counting the 2 days the ratio is exactly 1, the trade holds nothing on 125 days in all.

Chan’s figures count those 123 days as earning 0, as the script does. Measured from 2006-10-20 instead, the APR is 0.174513 and the Sharpe ratio 1.092618. The drawdown figures do not change, because the deepest fall and the longest run below a high both come later.

![Two charts on one shared date axis from April 2006 to April 2012. The top chart redraws Figure 6.3, the trade’s cumulative compounded return, as a solid black line. It stays at zero until late October 2006, rises to about 30 percent by late 2007, climbs steeply in late 2008 to a marked high of 1.272665, or 127 percent, on 2009-02-18, falls to a marked trough of 0.835584, or 84 percent, on 2009-06-29, regains its high in January 2011 after 487 days below it, and ends near 141 percent. A dashed grey line shows a fixed view that holds contango’s position on every day the trade holds anything. It falls below zero through 2008 to about −20 percent, recovers in late 2008, and ends near 30 percent. Nine shaded bands mark the days held long USO and short XLE. All but one fall between July 2007 and October 2008, the widest from July to December 2007, and the last sits in late 2011. A hatched band marks the first 123 days, when no ratio exists and nothing is held. The bottom chart plots the ratio of the back contract to the front from October 2006, with a line at 1. It sits mostly between 1.00 and 1.03, dips below 1 in the shaded stretches of 2007 and 2008 to a marked low of 0.982067 on 2007-09-26, and spikes to a marked high of 1.111489 on 2009-02-05. The title calls the figure exploratory.](../docs/figures/xle_uso_roll_return.png)

*The top panel redraws the book’s Figure 6.3, “Cumulative Returns of XLE-USO Arbitrage”, with a fixed view beside it that holds contango’s position on every day the trade holds anything, which Lesson 5 measures. The bottom panel is the ratio that sets the trade’s direction, which the book does not draw. The script’s own last lines, commented out, would have marked the contango days on Chan’s plot.*

The figure is exploratory like every number here. The bottom panel shows where the backwardation days fall. Nine stretches hold them. The longest runs from 2007-07-13 to 2007-12-13, 108 days, and the last from 2011-10-24 to 2011-11-18, 20 days. The ratio’s lowest value is 0.982067 on 2007-09-26 and its highest 1.111489 on 2009-02-05, in the contango of early 2009.

## Lesson 4: the XLE closes are not what a holder earned

A fund that pays a dividend drops in price by about the dividend on the day it goes out. A price series adjusted for dividends removes that drop, and there are two ways to do it.

1. **Rescaling.** Multiply every earlier close by a factor, so each day’s percentage change equals what a holder earned with the dividend reinvested. Yahoo Finance’s adjusted close does this.
2. **Subtraction.** Take each dividend, in dollars, off every earlier close. Each day’s dollar move stays as it traded, except on the day the dividend goes out. The earlier closes are lower, though, so each percentage change is a dollar move over a smaller price.

Chan’s fund file subtracts. The file holds 67 funds, among them SPY, the fund that tracks the S&P 500, and GDX, the fund of gold miners. A check of the file against SPY’s raw closes from Yahoo Finance, downloaded 2026-10-03, found SPY’s close on 2006-04-26 sitting 14.98 below the price that traded. The gap shrinks by each of the 24 dividends SPY paid over the file’s span and is zero on its last day. Yahoo Finance’s adjusted closes, downloaded 2026-09-18, give those dividends when set against the raw closes. Each one comes from the step in the rescaling factor on the day it went out. The [post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#the-test-and-the-file) read the same file and notes the same adjustment.

XLE pays dividends too. If the file adjusts XLE the way it adjusts SPY and GDX, XLE’s daily moves in this file read larger in size than a holder’s, most of all in the earliest years. The only XLE series in the repository is Chan’s, so nothing measures the gap between his XLE and the price that traded.

None of this touches the replication, because Chan’s script read the same bytes. It does mean the trade’s figures are what the script computes on Chan’s file, not what holding the two funds earned.

## Lesson 5: the backwardation days earn a third of the return

The trade earns each day on the view it held the day before. Splitting its days that way gives two groups.

1. **The 1,128 days earning on contango.** This is one fewer than the 1,129 days it held contango’s position, because the last day, 2012-04-09, is one of them and nothing follows it.
2. **The 244 days earning on backwardation.**

```math
\small\begin{array}{l|r|r}
\text{Earning on} & \text{Contango} & \text{Backwardation} \\ \hline
\text{Days} & 1{,}128 & 244 \\ \hline
\text{Compounded} & & \\
\text{the trade} & 79.0269\% & 34.3539\% \\
\text{USO} & -56.7754\% & 70.2850\% \\
\text{XLE} & 54.9091\% & -9.7061\% \\ \hline
\text{Summed} & & \\
\text{the trade} & 0.638420 & 0.308117 \\
\text{USO, in logs} & -0.838762 & 0.532304 \\
\text{implied roll return} & -0.766081 & 0.072380
\end{array}
```

The USO and XLE rows give each fund’s own move over the group’s days, not what its leg earned the trade. The trade’s daily returns sum to 0.946538 over all of Chan’s dates. The backwardation days hold 0.308117 of that, about a third, on under a fifth of the days earning on either view. Compounded returns multiply rather than add, so the share comes from the sums.

A fixed view shows how much the backwardation days matter. Hold contango’s position, short USO and long XLE, on every day the trade holds anything, and ignore the ratio’s sign. That earns an APR of 0.044949 and a Sharpe ratio of 0.364524, against the trade’s 0.159102 and 1.046596. The fixed view ends at 29.87 percent where the trade ends at 140.53 percent. The dashed line in the figure is that fixed view. It falls through the longer backwardation stretches of 2007 and 2008, where the trade’s line rises.

### USO’s move beside the implied roll return

Each cell under “Summed” in the table above adds up one number for each of its column’s days. For the trade it is the day’s return. For USO it is the day’s log move, and those sum to the natural log of one plus USO’s compounded move. The last row applies the equation for γ above to each day. It takes 12 times the log of the front over the back, on the ratio that set that day’s view, and divides by 252. It reads every ratio as two contracts a month apart, and it approximates the roll return a holder of the futures would collect under the book’s model. So USO’s row and the last row are sums of the same kind and can be compared.

Under the book’s model, USO’s move is the spot’s move plus the roll return. These rows leave out what the spot did over the same days, so they set two sizes side by side rather than measure how much of USO’s move the roll return caused.

The two groups’ sums compare as follows.

1. **On the contango days, the implied roll return comes close to USO’s fall.** USO fell by 0.838762 in log terms, and the ratio implies a roll return of −0.766081 over the same days. Under the book’s model, the trade on these days was short the fund that loses the roll return and long the fund that does not. Added up day by day, as the trade’s row under “Summed” is, the long XLE leg earned the trade more than the short USO leg did, though USO’s fall in the table, compounded or in logs, is larger than XLE’s rise. So these days too were in large part a bet on XLE’s own move.
2. **On the backwardation days, USO’s rise far exceeds the implied roll return.** USO rose by 0.532304 in log terms, while the ratio implies a roll return of 0.072380 over the same days, under a seventh of USO’s rise. Added up the same way, the trade earned these days mostly by being long USO while USO rose, and a little by being short XLE while XLE fell. That is a bet on the two funds’ moves.

![A whiteboard sketch titled “USO’s log move against the implied roll return”, drawn slowly. A grey zero line runs across the board. Above it on the left, black words read “1,128 days earning on contango”. A black bar hangs down from the line, named “USO” above the line and marked “−0.838762” at its end, and beside it a brown bar nearly as long, named “roll return” and marked “−0.766081”. Black words beside the brown bar read “close to” and “USO’s fall”. Below the line on the right, black words read “244 days earning on backwardation”. A black bar stands up from the line, named “USO” below the line and marked “0.532304” at its top, and beside it a short brown bar named “roll return” and marked “0.072380”. A dashed grey line runs from the top of the black bar, above the brown bar, to a black brace. The brace stands to the right of the brown bar and spans from the brown bar’s top up to the dashed line, with black words beside it, “USO’s move beyond” and “the roll return”. Grey words at the bottom read “roll return: 12 · ln(front / back) / 252, each group’s days summed,” and “on the ratio that set the view”. Both values in each group are log quantities, and every bar is drawn to one scale. The finished drawing holds for twelve seconds.](../docs/figures/xle_uso_roll_return_sketch_roll_vs_uso.gif)

**The split is a description of one sample, and it is exploratory.** It has no parameter to tune, because it uses the rule’s own two views, but it came after the run was seen. A split at the end of 2008 was also measured and left out, because its date would have been picked after seeing the curve. Nothing here says the backwardation days will keep earning, or why USO rose on them.

## What this replication cannot say

Five questions are beyond it.

1. **What a holder of XLE earned.** The fund file subtracts dividends, and the repository holds no second XLE series over Chan’s dates.
2. **Whether XLE tracks crude’s spot price.** The save the script loads holds no spot, and nothing here tests XLE against the spot in the save of 2012-08-14.
3. **Which standard deviation Chan’s Sharpe ratio uses.** With n as the divisor the Sharpe ratio is 1.046596, with n − 1 it is 1.046247, and both print as 1.05.
4. **What trading costs.** After the trade’s first entry on 2006-10-20, the position changes on 19 days. Each change trades both funds, and nothing is charged for any of it.
5. **Whether the trade works after 2012.** The rule and the dates are Chan’s. A test of the trade would fix the rule in writing first and run it on later prices.

## What this means for a trader

One habit for each lesson.

1. **Check that a stand-in tracks what it stands in for.** A trade built on one fund standing in for a price needs the stand-in tested against that price. Until it is, treat the trade as a bet on the two funds.
2. **Read the script before trusting the text.** Here the text’s two figures fit the script’s run, and the script is what says how the trade tells contango from backwardation. When a book gives a rule in a sentence or two, the script is where its details live.
3. **Count the days a rule holds each view, and the days it holds nothing.** A trade that is mostly one view is mostly a bet on that view. Days with no position still count in an annual figure.
4. **Ask how a price file adjusts for dividends.** Subtraction and rescaling give different returns from the same closes. A figure computed on subtracted closes is not what a holder earned. One computed on rescaled closes is, with each dividend reinvested.
5. **Split the return by the views the rule takes.** If the rarer view earns a large share, find what earned it. Here, on the backwardation days, USO’s own rise was far larger than the roll return the signal reads.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Figure 6.3, with pages 142, 178 and 208 to 209 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. `XLE_CL_rollReturn.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/xle_uso_roll_return.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/xle_uso_roll_return_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/xle_uso_roll_return_whiteboard.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_xle_uso_roll_return.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_xle_uso_roll_return_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_xle_uso_roll_return_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-39-xle-against-uso-signed-by-crude-oils-contango-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
