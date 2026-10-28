# Chan’s XLE against USO trade reproduces on his own files, and a third of its return comes from the days it bet on backwardation

*Chan holds a fund of oil producers against a fund of oil futures, in whichever direction crude oil’s roll return favours, and reports an APR of 16 percent. On his own files every figure he prints reproduces. The trade sits in contango on most days, yet the few days it holds the other way earn a third of its return, and on those days the funds’ own moves dwarf the roll return the signal reads.*

## Why trade a fund of producers against a fund of futures

A futures contract earns two things as it ages: what the commodity’s price does, and a roll return from its price converging on that price by expiry. Ernest Chan’s *Algorithmic Trading* shows one way to collect the roll return alone. When the roll return is negative, “buy the underlying asset and short the futures”, and the reverse when it is positive (Chan, 2013, Kindle edition, p. 208). The commodity’s own moves cancel between the two legs and the roll return is left. The [post on long GLD and short gold futures](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gc-lessons.md#why-own-the-metal-and-short-the-future) runs that arbitrage on gold, where a fund does hold the metal.

That needs a way to hold the commodity itself, and for crude oil none exists. “There are no ETFs that hold other physical commodities as opposed to commodities futures”, Chan writes, because storing them costs too much (p. 209). USO, the oil fund, “doesn’t actually own oil. It invests in oil futures contracts” (p. 142). So Chan offers what he calls “a less exact form of arbitrage” (p. 209). A fund of companies that produce a commodity “usually cointegrates with the spot price of that commodity” (p. 178), meaning the two move together over time. The spot price is the price for delivery today. XLE, the energy sector fund, can then stand in for crude’s spot price.

The trade pairs XLE with USO rather than with crude oil futures directly, which trade as CL. The reason is a timing one: “XLE and CL have different closing times”, while USO closes with XLE and “contains nothing but front month contracts of CL” (p. 209). The rule is two sentences.

1. “Short USO and long XLE whenever CL is in contango”, meaning later contracts are priced above earlier ones.
2. “Long USO and short XLE whenever CL is in backwardation”, the reverse.

Chan reports “a very respectable 16 percent” a year from April 26, 2006, to April 9, 2012, “with a Sharpe ratio of about 1” (p. 209). He published the script, `XLE_CL_rollReturn.m`, and this repository transcribed it line by line and ran it on the two files it loads.

The results fall into five groups.

1. **The pair stands in for crude’s spot and its futures only by assumption.** The book argues it, and this replication does not test it.
2. **Every printed figure lands.** All five figures in the script’s comment and the book’s two match on Chan’s own files.
3. **The trade is mostly in contango and holds nothing at first.** It is short USO and long XLE on 1,129 days, the reverse on 244, and holds nothing for its first 123 days.
4. **The XLE closes are not what a holder earned.** Chan’s fund file adjusts for dividends by subtraction, and nothing committed measures how much that moves XLE’s returns.
5. **The few backwardation days earn a third of the return.** On those days USO rose 0.5323 in log terms, while the roll return the signal reads came to 0.072380.

**Every result here is exploratory.** Chan chose the funds, the signal, the rule and the dates, and the reproduction runs them on his own files. It can say whether his numbers follow from those files, and nothing about whether the trade would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The funds, the ratio and the files

The [post on Chan’s crude oil calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-calendar-spread-lessons.md#the-spread-the-signal-and-the-file) builds up a futures contract, its expiry, the roll from one contract to the next, the roll return, and contango and backwardation. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#the-model-and-the-files) works through the model behind the roll return, which Chan calls γ. This post covers only what this script does differently.

**The signal is a ratio of two contracts.** On each day the script reads one CL contract, which it calls the front, and the contract expiring a month after it, the back. The ratio is the back’s price over the front’s. Above 1 is contango, and below 1 is backwardation. The book’s model makes this ratio a reading of the roll return. A contract a month further out is priced lower by one month’s roll return, so the roll return, annualised, is about 12 times the log of the front over the back.

```math
\gamma_t \approx 12 \ln \frac{F_{\text{front}}(t)}{F_{\text{back}}(t)}
```

That reading assumes the two contracts are a month apart, which on CL they are. Lesson 5 uses it.

**The front window is the script’s own.** Each contract is the front from 40 rows to 10 rows before its last priced row in Chan’s file, and no earlier than the row after the previous front ends. A row is one trading day in the file. The script’s comment calls these days before expiration, but the script finds each expiry as the last day the file prices a contract. CL contracts expire a month apart, so after the first contract the 40-row start never binds. The 40 decides only the window of CL-2007F, the January 2007 contract, and every later contract starts on the row after the previous one ends. That differs from the crude oil calendar spread, which holds named pairs of contracts on a schedule of its own. On the days outside every window the ratio is undefined and the trade holds nothing.

**The rule and its returns.** Each day the trade takes its position from the ratio and earns that position the next day, on each fund’s percentage change. Each fund carries half the capital, so the day’s return is the sum of the two legs divided by 2. Nothing is charged for trading. The APR is the compounded annual return over 252 trading days. The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate.

**The files are two of Chan’s.** Both are recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md).

1. **`inputData_ETF.mat`**, saved 2012-04-10. USO and XLE hold 1,500 closes each from 2006-04-26 to 2012-04-09, with none missing. The [post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#the-test-and-the-file) read the same file to test whether a gold fund, a fund of gold miners and USO move together, pairing a producers’ fund with a fund of the commodity as this trade does.
2. **`inputDataDaily_CL_20120502.mat`**, saved 2012-05-03. It holds 89 CL contracts, one for each month from CL-2007F to CL-2014K, over 2,867 days from 2000-11-20. It holds no spot price.

A later save of the same strip, `inputDataDaily_CL_20120813.mat`, saved 2012-08-14, is the file Example 5.3 reads, and two comparisons below use it.

The two calendars share 1,498 days. The fund file holds 2006-07-03 and 2006-11-24, which the CL file lacks. The first front window opens on 2006-10-20, so the ratio is defined on 1,375 of the shared days.

Each contract in the CL file is one contract’s own prices. The [post on the crude oil reversal and momentum rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#lesson-1-both-figures-land-and-a-save-a-week-later-prints-the-same-to-the-books-precision) found that a save dated a week later moves every close in that post’s window, because a continuous future is rewritten at every roll. Chan’s single contracts were not rewritten that way. The save of 2012-08-14 gives the same ratio on all 1,375 days.

The rules that decide each result are in [Entry 39 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-39-xle-against-uso-signed-by-crude-oils-contango-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the pair stands in for crude’s spot only by the book’s argument

The trade rests on two claims from the book, and this replication tests neither.

1. **XLE stands in for crude’s spot price.** Chan says a producers’ fund usually cointegrates with the spot (p. 178). The file the script loads holds no spot price. Chan’s later save of the strip holds one over the whole window, but nothing here tests XLE against it.
2. **USO holds the front contract.** The script’s ratio reads its own front, which is not always the contract nearest expiry. On 734 of the 1,375 days with a ratio, the script’s front is the nearest contract the file prices that day. On the other 641 it is the second-nearest. The script moves to the next contract 10 rows before the current one’s last price, and for those 10 rows the old contract is still priced. So “front month” in the signal means the contract the script reads, which need not be the one USO held that day.

Over the window the two funds went opposite ways. USO’s close fell from 69.54 to 38.97, or 43.9603 percent. XLE’s rose from 51.97 to 69.61, or 33.9427 percent. A trade mostly short USO and long XLE gains from both moves, whether or not either move came from the roll return. Lesson 5 splits the window by the view the trade held and measures how much of USO’s move the ratio’s roll return accounts for.

## Lesson 2: every printed figure lands on Chan’s files

A figure lands when the computed value rounds to the printed one at the decimals printed. Every figure does.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script comment} & \text{Book} \\ \hline
\text{Average annual return} & 0.159231 & 0.1592 & \text{none} \\
\text{Sharpe ratio} & 1.046596 & 1.05 & \text{about 1} \\
\text{APR} & 0.159102 & 0.1591 & 16 \text{ percent} \\
\text{Maximum drawdown} & -0.192321 & -0.192321 & \text{none} \\
\text{Longest drawdown, days} & 487 & 487 & \text{none}
\end{array}
```

The average annual return is 252 times the mean daily return, without compounding. The maximum drawdown is the deepest fall from a previous high, and the longest drawdown is the most days spent below one. The book’s 16 percent and “about 1” are the script’s APR and Sharpe ratio rounded, so the text and the script describe one run.

Two caveats come with the match.

1. **The order of the run.** A first run saw all five figures before the rule for a landing figure was written down. The rule then fixed is the one every replication here uses, and nothing in it was chosen to fit. There is one reading of the script and no others beside it.
2. **The Sharpe ratio’s divisor.** The run divides the standard deviation by n, the number of days. Dividing by n − 1 gives 1.046247, which also rounds to 1.05. The printout cannot tell the two apart.

The book’s rule is “whenever CL is in contango”, and the script decides that from one pair of contracts. Chan’s Example 5.3 measures the roll return another way, as γ fitted across the five nearest contracts each day, and the [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#lesson-4-the-average-hides-a-roll-return-that-drifts-and-changes-sign) shows CL’s γ is mostly contango and changes sign 29 times. On the later save, where both can be read, the two mostly agree.

1. **Same view on 1,354 days** of the 1,373 on which the ratio is not exactly 1.
2. **Contango by the ratio and backwardation by γ** on 13.
3. **Backwardation by the ratio and contango by γ** on 6.

On the 2 days the ratio is exactly 1 it calls no view, and γ calls backwardation on both.

## Lesson 3: mostly contango, and nothing held for the first 123 days

Of the 1,375 days with a ratio, the trade holds contango’s position on 1,129 and backwardation’s on 244. On 2 days, 2008-02-07 and 2008-08-07, the ratio is exactly 1 and it holds nothing. So the trade is mostly short USO and long XLE.

It also holds nothing on the window’s first 123 days, from 2006-04-26 to 2006-10-19. The CL file’s first contract is CL-2007F, and its front window opens on 2006-10-20. Earlier contracts are not in the file, so no ratio exists before then. With the two days at 1, that leaves 125 days flat.

Chan’s figures count those 123 days as earning 0, as the script does. Measured from 2006-10-20 instead, the APR is 0.174513 and the Sharpe ratio 1.092618. The drawdown figures do not change, because the deepest fall and the longest run below a high both come later.

![Two charts on one shared date axis from April 2006 to April 2012. The top chart redraws Figure 6.3, the trade’s cumulative compounded return, as a solid black line. It stays at zero until late October 2006, rises to about 30 percent by late 2007, climbs steeply in late 2008 to a marked high of 1.272665, or 127 percent, on 2009-02-18, falls to a marked trough of 0.835584, or 84 percent, on 2009-06-29, regains its high in January 2011 after 487 days below it, and ends near 141 percent. A dashed grey line holds contango’s position on every day the trade holds anything. It falls below zero through 2008 to about −20 percent, recovers in late 2008, and ends near 30 percent. Nine shaded bands mark the days held long USO and short XLE. All but one fall between July 2007 and October 2008, the widest from July to December 2007, and the last sits in late 2011. A hatched band marks the first 123 days, when no ratio exists and nothing is held. The bottom chart plots the ratio of the back contract to the front from October 2006, with a line at 1. It sits mostly between 1.00 and 1.03, dips below 1 in the shaded stretches of 2007 and 2008 to a marked low of 0.982067 on 2007-09-26, and spikes to a marked high of 1.111489 on 2009-02-05. The title calls the figure exploratory.](../docs/figures/xle_uso_roll_return.png)

*The top panel redraws the book’s Figure 6.3, “Cumulative Returns of XLE-USO Arbitrage”, with a fixed view beside it that holds contango’s position on every day the trade holds anything, which Lesson 5 measures. The bottom panel is the ratio that signs the trade, which the book does not draw. The script’s own last lines, commented out, would have overlaid the contango flag on Chan’s plot.*

The figure is exploratory like every number here. The bottom panel shows where the backwardation days fall. Nine stretches hold them. The longest runs from 2007-07-13 to 2007-12-13, 108 days, and the last from 2011-10-24 to 2011-11-18, 20 days. The ratio’s lowest value is 0.982067 on 2007-09-26 and its highest 1.111489 on 2009-02-05, in the contango of early 2009.

## Lesson 4: the XLE closes are not what a holder earned

A fund that pays a dividend drops in price by about the dividend on the day it goes out. A price series adjusted for dividends removes that drop, and there are two ways to do it.

1. **Rescaling.** Multiply every earlier close by a factor, so each day’s percentage change equals what a holder earned with the dividend reinvested. A yfinance adjusted close does this.
2. **Subtraction.** Take each dividend, in dollars, off every earlier close. Each day’s dollar move stays as it traded, except on the day the dividend goes out. The earlier closes are lower, though, so each percentage change is a dollar move over a smaller price.

Chan’s fund file subtracts. A check of the file against a raw SPY download found SPY’s close on 2006-04-26 sitting 14.98 below the price that traded. The gap shrinks by each of the 24 dividends SPY paid over the file’s span and is zero on its last day. The [gold miners post](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md#the-test-and-the-file) read the same file and notes the same adjustment.

XLE pays dividends too, so its daily moves in this file read larger in size than a holder’s, most of all in the earliest years. By how much is not known here. The only XLE series committed is Chan’s, so nothing measures the gap between his XLE and the price that traded.

None of this touches the replication, because Chan’s script read the same bytes. It does mean the trade’s figures are what the script computes on Chan’s file, not what holding the two funds earned.

## Lesson 5: the backwardation days earn a third of the return

The trade earns each day on the view it held the day before. Splitting its days that way gives two groups.

1. **The 1,128 days earning on contango.** One fewer than the 1,129 days it held contango, because the window’s last day is one of them and nothing follows it.
2. **The 244 days earning on backwardation.**

```math
\begin{array}{l|r|r}
\text{On the days earning on} & \text{Contango} & \text{Backwardation} \\ \hline
\text{Days} & 1{,}128 & 244 \\
\text{The trade, compounded} & 79.0269 \text{ percent} & 34.3539 \text{ percent} \\
\text{The trade, daily returns summed} & 0.638420 & 0.308117 \\
\text{USO, compounded} & -56.7754 \text{ percent} & 70.2850 \text{ percent} \\
\text{XLE, compounded} & 54.9091 \text{ percent} & -9.7061 \text{ percent} \\
\text{USO, log move} & -0.8388 & 0.5323 \\
\text{Roll return the ratio implies, log} & -0.766081 & 0.072380
\end{array}
```

The trade’s daily returns sum to 0.946538 over the whole window. The backwardation days hold 0.308117 of that, about a third, on under a fifth of the days that earn anything.

The last row sums the equation from the setup over each group’s days, as 12 times the log of the front over the back, divided by 252, on the ratio that set the view. It reads every ratio as two contracts a month apart, and it approximates the roll return a holder of the futures would collect under the book’s model.

The two groups tell different stories.

1. **On the contango days, the implied roll return comes close to USO’s fall.** USO fell by 0.8388 in log terms, and the ratio implies a roll return of −0.766081 over the same days. That is the trade the book describes. It is short the fund that loses the roll return and long the fund that does not. XLE rising 54.9091 percent over the same days added to it.
2. **On the backwardation days, USO’s rise far exceeds the implied roll return.** USO rose by 0.5323 in log terms, while the ratio implies a roll return of 0.072380, about 7 percent. The trade earned these days by being long USO while USO rose and short XLE while XLE fell. That is a bet on the two funds’ moves, of which the implied roll return is a small part.

A fixed view shows how much the backwardation days matter. Hold contango’s position, short USO and long XLE, on every day the trade holds anything, and ignore the ratio’s sign. That earns an APR of 0.044949 and a Sharpe ratio of 0.364524, against the trade’s 0.159102 and 1.046596. The fixed view ends at 29.87 percent where the trade ends at 140.53 percent. The dashed line in the figure is that fixed view. It falls through the backwardation stretches of 2007 and 2008, where the trade’s line rises.

**This is a description of one sample, and it is exploratory.** The split has no parameter to tune, because it uses the rule’s own two views, but it was chosen after the run was seen, which is why it is exploratory. A split by date was also measured and is left out, because its date would have been picked after seeing the curve. Nothing here says the backwardation days will keep earning, or why USO rose on them.

## What this replication cannot say

Five questions are beyond it.

1. **What a holder of XLE earned.** The fund file subtracts dividends, and no second XLE series over the window is committed.
2. **Whether XLE tracks crude’s spot price.** The save the script loads holds no spot, and nothing here tests XLE against the spot in the save of 2012-08-14.
3. **Which standard deviation Chan’s Sharpe ratio divides by.** Dividing by n gives 1.046596 and by n − 1 gives 1.046247, and both print as 1.05.
4. **What trading costs.** After its first entry on 2006-10-20, the position changes on 19 days. Each change trades both funds, and nothing is charged for any of it.
5. **Whether the trade works after 2012.** The rule and the window are Chan’s. A test of it would fix the rule in writing first and run it on later prices.

## What this means for a trader

One habit for each lesson.

1. **Check that a stand-in tracks what it stands in for.** A trade built on one fund standing in for a price needs the stand-in tested against that price. Until it is, treat the trade as a bet on the two funds.
2. **Read the script before trusting the text.** Here the text and the script describe one run, and the script is what says how contango is decided. When the book gives a rule in one sentence, the script is where its details live.
3. **Count the days a rule holds each view, and the days it holds nothing.** A trade that is mostly one view is mostly a bet on that view. Days with no position still count in an annual figure.
4. **Ask how a price file adjusts for dividends.** Subtraction and rescaling give different returns from the same closes. A figure computed on one is not what a holder of the other earned.
5. **Split the return by the views the rule takes.** If the rarer view earns a large share, find what earned it. Here the funds’ own moves were far larger than the roll return the signal reads.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Figure 6.3, with pages 142, 178 and 208 to 209 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. `XLE_CL_rollReturn.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/xle_uso_roll_return.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/xle_uso_roll_return_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_xle_uso_roll_return.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_xle_uso_roll_return_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-39-xle-against-uso-signed-by-crude-oils-contango-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
