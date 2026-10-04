# Chan’s commodity seasonals fit his counts on every year the data can read, and win fewer years after the book

*A count of profitable years is only as good as the years it counts, where it starts, and who chose the trade.*

## Why test a trade its author calls alive

Ernest Chan’s *Quantitative Trading* sets two families of seasonal trade side by side in one sentence. Much of the seasonality in equity markets, he writes, has weakened or even disappeared in recent years, while some seasonal trades in commodity futures are still profitable (Chan, 2021, location 4303). Later in the same chapter he says commodity seasonals are “alive and well”, perhaps, he suggests, because the demand behind them is a real economic need rather than speculation (location 4529).

[The companion post on the equity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) tested the first half of that sentence. This post tests the second half. A claim that a trade still pays is one a reader might act on, so it is worth checking what the record behind it shows.

Chan gives two trades, each with a count of profitable years. This repository ran both on the free settlement prices the US Energy Information Administration (EIA) publishes for futures traded on the New York Mercantile Exchange (NYMEX). In short:

1. **Natural gas reproduces both of Chan’s counts**, 13 and 14 consecutive profitable years, under one reading of which years he counted. The data constrains that reading and cannot prove it.
2. **Gasoline’s readable years fit Chan’s count.** Chan prints 19 profitable years of 21. The data shows the 2 losing years his count allows and no third, plus 3 years it cannot read at all.
3. **Both trades win fewer years after the years Chan read.** Natural gas wins 15 of 15 years through 2008 and 7 of 15 after.

Every result here is **exploratory**. Chan chose both trades after looking at the same years of history this run reads, so the run can say whether his counts reproduce and nothing about whether either trade pays today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two trades and the files

A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, so the May gasoline contract and the June gasoline contract have different prices. Each trading day ends with a **settlement price** for every contract, which is what both trades buy and sell at.

Each trade appears twice in the book, once in the main text and once in a sidebar that gives the exact rule.

1. **Gasoline** (sidebar, location 4536). Buy one May gasoline futures contract at the close of April 13, or the next trading day if April 13 is a holiday, and sell it at the close of April 25, or the previous trading day. Chan’s reason is the summer driving season.
2. **Natural gas** (sidebar, location 4590). Buy one June natural gas contract at the close of February 25 and exit on April 15, which the run reads as the close, moving the dates the same way. Chan’s reason is power generators buying gas ahead of air-conditioning season (location 4585).

EIA publishes those settlements for free, for the nearest four contracts of each product. It numbers them by expiry rather than by month: contract 1 is whichever contract stops trading next. So the run has to work out which numbered file holds the May or June contract on each trade date, which Lesson 4 comes back to. It reads five files from three series, all downloaded on 2 October 2026:

1. New York Harbor regular gasoline, contract 1, through 2005.
2. RBOB gasoline, contract 1, from 2006. RBOB is the gasoline contract that replaced the New York Harbor one, and it began trading in October 2005.
3. Henry Hub natural gas, contracts 2, 3 and 4.

The rules that decide each result were written down before any trade was computed, and one was corrected after the first run without changing any count, as Lesson 4 says. Two of them carry most of what follows:

1. **Profitable** means the exit settlement is strictly above the entry settlement, on one contract, with no costs. A zero change is not a profit.
2. **A missing row stays missing.** A year whose trade date has no row in its file counts neither as a profit nor as a loss. The run does not move it to a neighbouring day.

**Which edition says what.** Every passage quoted here is in the revised edition (2021). The first edition matters too, because one reading below depends on it. Wiley released it in November 2008 and dated it 2009.

## Lesson 1: a count of consecutive years needs its start year and its edition

The main text says the natural gas trade “has been profitable for 13 consecutive years as of this writing” (location 4585). The sidebar says 14 (location 4590). Neither says which year its run ends in, and the revised edition was published in 2021, so the question is which years “this writing” covers.

The files answer part of it. Every year from 1994, the first year the files hold a whole trade, to 2008 is profitable. 2009 is a loss. So the length of the run ending in any year depends on where the count starts:

```math
\begin{array}{l|r|r}
\text{Count starts in} & \text{Run ending in 2007} & \text{Run ending in 2008} \\ \hline
1995 & 13 & 14 \\
1994 & 14 & 15
\end{array}
```

Read as first-edition figures counted from 1995, both of Chan’s counts reproduce. The main text’s 13 is the run ending in 2007 and the sidebar’s 14 is the run ending in 2008, both inside the years before a book released in November 2008. That reading was written down before any trade was computed, as a hypothesis. The files constrain it in two ways and prove it in neither.

1. **They rule out the revised edition’s years.** 2009 is a loss, and counted from 1995 no run of 13 or more ends in any year except 2007 and 2008. So neither count can describe a run that reached into the years after the first edition.
2. **They cannot pick the start year.** 1994 is profitable too. Counted from 1994, the runs of 13 and 14 end in 2006 and 2007 instead. The only reason to prefer 1995 is that Chan’s gasoline sidebar names it as its own start.

So this post says natural gas reproduces under that reading, and never that it reproduces outright.

Gasoline shows the same split inside one trade. Its main text says 19 profitable years of the last 21 “as of 2015” (location 4529), which is revised-edition text. Its sidebar says Chan “would have realized a profit every year since 1995” (location 4536), which reads as first-edition text, covering 1995 to 2008. On that reading the files show no losing year from 1995 to 2008: 11 profitable years and 3 the file cannot read. Read that way, one book prints a 2015 count beside a 2008 claim, and a reader who takes both as one moment in time compares two different spans.

## Lesson 2: a missing row is not a losing year

Chan’s gasoline count is 19 profitable years of 21, from 1995 to 2015. The run gives this:

```math
\begin{array}{l|r}
\text{Gasoline, 1995 to 2015} & \text{Years} \\ \hline
\text{Profitable} & 16 \\
\text{Losing, in 2009 and 2012} & 2 \\
\text{No row on a trade date, in 1997, 1998 and 1999} & 3 \\ \hline
\text{Total} & 21
\end{array}
```

Three years cannot be read. EIA’s New York Harbor file holds no row on 14 April 1997, the entry date that year, or on 24 April 1998 and 23 April 1999, the exit dates those years. Each was a trading day. Under the rule written before any trade was computed, those years count neither way.

Taking a neighbouring day’s price instead would turn a gap into a guess, and a guess that decides the count it is meant to check. So the file shows 16 profitable years and 2 losses, and it bounds Chan’s count between 16 and 19 without settling it.

The losses say more than the gaps do. Chan’s 19 of 21 allows exactly 2 losing years, and the file shows exactly 2, in 2009 and 2012. So the file’s readable years fit Chan’s count. His 19 holds only if all three unreadable years were profitable in his data, and only if his data agrees with EIA’s on the other 18. The file cannot say whether they were, and no other committed source holds the contract in those years.

One more year has a gap of the same kind. RBOB began trading in October 2005, so the first April it covers is 2006, and the run reads RBOB from then. The older New York Harbor contract still traded in April 2006, but its file has no row on 13 April 2006, so the files cannot say whether reading the older contract that year would change its result.

The verdict [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) records for this row is “reproduced with a gap”. That verdict was taken after the criterion written down in advance, exactly 19 profitable years, failed at 16. The log’s rule allows the verdict when the gap has a named cause outside the method, and the missing rows are one. The log says the verdict came afterwards, and this post says it too.

## Lesson 3: a trade chosen after looking at the history is tested by the years after the book

Chan chose both trades after looking at the history. The gasoline sidebar says he found the best trade after scanning the literature, and both rules name exact days. A rule chosen from the past tends to look good on the past, so the years it was chosen on cannot test it. The years after the book can.

```math
\begin{array}{l|r|r}
\text{Trade} & \text{The book's years} & \text{After the book} \\ \hline
\text{Natural gas} & 15 \text{ of } 15, \text{ 1994 to 2008} & 7 \text{ of } 15, \text{ 2009 to 2023} \\
\text{Gasoline} & 16 \text{ of } 21, \text{ 1995 to 2015, 3 unreadable} & 3 \text{ of } 8, \text{ 2016 to 2023}
\end{array}
```

For natural gas the trade went from winning every year to winning fewer than half. Chan says as much himself: the natural gas trade “didn’t hold up as well out-of-sample” (location 4632). He prints no figure for it. The files give 7 of 15 for 2009 to 2023, a span that runs past any years he could have seen.

For gasoline, Chan marks the last 9 of his 21 years, 2007 to 2015, as out of sample, meaning years he did not use to choose the rule. The trade won 7 of those 9, and both of its losing years fall among them. From 2016 to 2023, after the revised edition’s count ends, it won 3 of 8. Natural gas won 4 of the same 8.

![Two panels of bar charts, one bar per year at the change in settlement price from entry to exit. The upper panel is gasoline, the May contract from the close of April 13 to the close of April 25, from 1995 to 2023 in dollars a gallon. Its years 1997, 1998 and 1999 are empty slots labelled “no row”. A dashed line after 2015 divides 1995 to 2015, 16 of 21 profitable with 3 with no row, from 2016 to 2023, 3 of 8 profitable. Bars before the line are mostly small and positive, with losses in 2009 and 2012, and five of the eight after it are losses. The lower panel is natural gas, the June contract from the close of February 25 to the close of April 15, from 1994 to 2023 in dollars per million Btu. A dashed line after 2008 divides 1994 to 2008, 15 of 15 profitable, from 2009 to 2023, 7 of 15 profitable. Every bar before the line is positive, and after it losses alternate with gains, including one gain near three dollars in 2022. Marks along the foot of each panel point up for each profitable year and down for each losing one.](../docs/figures/commodity_seasonals_years.png)

*Every year of both trades. Each dashed line is where the book’s years end, and the marks along each foot give every year’s sign, including years too small to see as bars.*

None of this is a verdict on whether either trade is alive. Eight years with no costs charged can show a change and cannot measure it, and nobody wrote down a test for “alive” before these years were computed. The figures describe the record. They do not grade Chan’s claim, and like every result here the split is exploratory.

Chan names the same weakness, and offers a check. A trade that happens once a year produces few results, he writes, so it is hard to tell whether its backtest reflects data-snooping bias, meaning a pattern found by searching the past that will not repeat. He suggests trying somewhat different entry and exit dates to see whether the profits hold up (location 4637). This repository did not try them. Varying the dates until some version works is a search across many trades, and a search needs its own safeguards: a list of the variants written down before any is run, a correction for how many were tried, and years held back that the search never sees.

## Lesson 4: reading one named contract from files numbered by expiry needs a calendar checked outside the files

EIA’s files hold contract 1, contract 2 and so on, not the May contract or the June contract. So for every trade date the run has to know which numbered file holds the contract Chan names.

For gasoline the answer is simple. The May contract trades until the last business day of April, so it is contract 1 on both trade dates. For natural gas it moves. A natural gas contract stops trading three trading days before its delivery month begins. So the June contract is contract 4 on 25 February if the March contract has not yet expired, contract 3 if it has, and contract 2 by mid-April.

That makes the expiry rule part of the result, so the run checks it against things the files do not supply.

1. **Against the exchange’s own dates.** For 16 contracts, March to June of 2017, 2018, 2021 and 2024, the rule gives the last trading day the Massive futures data service recorded. Those 16 dates were read on 3 October 2026, and nothing in this repository can read them again, so the tests carry them as a measurement.
2. **Against the files’ own handovers.** On the day after an expiry, each numbered file should continue the next file’s prices. Before mid-1997 the files show contracts stopping five or six trading days before delivery rather than three. In March 1996 the price handover fits a five-day rule and not a three-day one. Following the files moves the 1996 and 1997 entries from contract 4 to contract 3, and both years are profitable on either contract. That correction came from the review of the pull request that first ran the trades, after the first run, and it changed no count.
3. **Against the edge cases.** In 10 of the 30 years, the entry date falls on the March contract’s last trading day. Reading contract 3 instead of contract 4 on those days flips no year’s result, so on these files that convention moves no count.

The calendar is computed rather than read from the files, for one more reason. The natural gas files carry exchange holidays as rows that repeat the day before’s settlement, so a row’s presence does not mean the exchange was open. Of NYMEX’s holidays, only Good Friday can land on a trade date, and it moved six trade dates between 1994 and 2023.

The same map from dates to contracts serves Chan’s calendar spreads, tested on the same files. [The stationary candidates post](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) reports what those spreads showed.

## What this replication cannot say

Six questions are beyond it.

1. **What the three unreadable years held.** EIA’s New York Harbor file has no row on any of them, and no other committed source covers the contract then.
2. **Whether Chan read the same contracts.** His sidebar names RB, the symbol RBOB trades under, and glosses it as the unleaded gasoline futures. Before RBOB began trading in October 2005, his series presumably held the older contract, and the run assumes so. His data vendor is not named.
3. **Which year each natural gas count was written in.** Lesson 1’s reading is a hypothesis the files constrain and cannot prove.
4. **Whether either trade pays after costs.** No commission, slippage or margin is charged.
5. **Whether nearby dates hold up.** Chan’s own suggested check, at location 4637, was not run, for the reason Lesson 3 gives.
6. **Any year after 2023.** EIA’s RBOB and natural gas files end on 5 April 2024, before either trade’s 2024 exit date. Another vendor could extend the record. The Massive futures data service returned gasoline prices for April 2025, and nothing here extends the record yet.

## What this means for a trader

Three habits follow from the lessons above.

1. **Ask a consecutive count where it starts and when it was written.** The same files give 13, 14 or 15 consecutive years for natural gas, depending on both.
2. **Read a missing year as missing.** Three gaps in one file leave Chan’s gasoline count anywhere between 16 and 19, and filling them with a neighbouring day would decide the answer instead of checking it.
3. **Judge a seasonal trade on the years after it was chosen.** Natural gas won every year through 2008 and fewer than half after, and the earlier years are the ones its rule was picked from.

On EIA’s free settlements, gasoline’s readable years fit Chan’s count, natural gas reproduces under one reading of when he counted, and both trades win fewer years after the book than before it.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Released in November 2008.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Kindle locations 4303, 4529, 4536, 4585, 4590, 4632 and 4637. This post cites the revised edition by Kindle location, as the replication log does. [The companion post](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) cites it by page, and location 4303 is its p. 174.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for New York Harbor regular gasoline, RBOB gasoline and Henry Hub natural gas, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the two trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_figures.py), with the checks behind [the trades’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_figures.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
