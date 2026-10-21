# Chan’s commodity seasonals fit his counts in every year the files have prices for, and win a smaller share of years after the book

*A count of profitable years is only as good as the years it counts, where it starts, and who chose the trade.*

## Why test a strategy published as alive

A seasonal trade buys and sells on the same calendar dates every year, betting that a price pattern repeats. Ernest Chan’s *Quantitative Trading* sets two families of them side by side in one sentence. Much of the seasonality in equity markets, he writes, has weakened or even disappeared in recent years, while some seasonal trades in commodity futures are still profitable (Chan, 2021, p. 175). Later in the same chapter he says commodity seasonals are “alive and well”, perhaps, he suggests, because the demand behind them is a real economic need rather than speculation (p. 183).

[The companion post on the equity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) tested the equity half of Chan’s sentence on p. 175. This one tests the commodity half. A claim that a trade still pays is one a reader might act on, so this post checks the record behind it.

Chan gives two trades, each with a count of profitable years. This repository ran both on the free settlement prices the US Energy Information Administration (EIA) publishes for futures traded on the New York Mercantile Exchange (NYMEX). In short:

1. **Natural gas reproduces both of Chan’s counts**, 13 and 14 consecutive profitable years, under one reading of which years he counted. Lesson 1 sets out that reading. The data constrains it and cannot prove it.
2. **Gasoline fits Chan’s count in every year the files have prices for.** Chan prints 19 profitable years of 21. The data shows the 2 losing years his count allows and no third, plus 3 years with no price on a trade date.
3. **Both trades win a smaller share of years after the ones Chan counted.** Natural gas wins 15 of 15 years through 2008 and 7 of 15 after.

Every result here is **exploratory**, meaning it describes what the data shows and cannot confirm that a trade works. Chan chose both trades after looking at years before his book. This run reads those years too, so on them it can say only whether his counts reproduce. Before this repository computed the years after the book, nobody wrote down what those years would have to show for a trade to count as still working. With no such test and no costs charged, those years cannot say whether either trade pays today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two trades and the files

A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, so the May gasoline contract and the June gasoline contract have different prices. Each trading day ends with a **settlement price** for every contract, the price the exchange sets as that day’s official close. Both trades buy and sell at it.

The book describes each trade twice, once in the main text and once in a sidebar that states the exact rule.

1. **Gasoline** (sidebar, pp. 183 to 184). Buy one May gasoline futures contract at the close of April 13, or the next trading day if April 13 is a holiday, and sell it at the close of April 25, or the previous trading day. Chan’s reason is the summer driving season.
2. **Natural gas** (sidebar, p. 185). Buy one June natural gas contract at the close of February 25, or the next trading day, and exit on April 15, or the previous trading day. Chan does not say at what time of day to exit, so the run exits at the close. Chan’s reason is power generators buying gas ahead of air-conditioning season.

**Which edition says what.** Every passage quoted here is in the revised edition (2021). The first edition matters too, because one reading below depends on it. Wiley released it in November 2008 and dated it 2009.

### Five files from EIA, numbered by expiry

EIA publishes the settlement prices for free, for the nearest four contracts of each product. It numbers them by expiry rather than by month: contract 1 is whichever contract stops trading next. Each contract number has its own file, with a row for each day the file has a price, giving the date and that day’s settlement price.

So the run has to work out which numbered file holds the May or June contract on each trade date, which Lesson 4 comes back to. The run reads five files, covering three products, all downloaded on 2 October 2026:

1. New York Harbor regular gasoline, contract 1, through 2005.
2. RBOB gasoline, contract 1, from 2006. RBOB is the gasoline contract that replaced the New York Harbor one, and it began trading in October 2005.
3. Henry Hub natural gas, contracts 2, 3 and 4.

### The two rules most results rest on

This repository wrote down the rules that decide each result before it computed any trade, as [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) records. That log sets each of Chan’s figures beside the figure this repository reproduced. After the first run, a review corrected one of the rules, the rule that decides which numbered file holds the June natural gas contract. The correction changed no count, as Lesson 4 says. Two of the rules carry most of what follows:

1. **Profitable** means the exit settlement is strictly above the entry settlement, on one contract, with no costs. A zero change is not a profit.
2. **A missing row stays missing.** A year whose trade date has no row in its file counts neither as a profit nor as a loss. The run does not move it to a neighbouring day.

## Lesson 1: a count of consecutive years needs its start year and its edition

The main text says the natural gas trade “has been profitable for 13 consecutive years as of this writing” (p. 185). The sidebar says 14 (p. 185). Neither says which year its streak ends in. Both sit in the revised edition of 2021, but either may be text kept from the first edition, released in 2008, so the question is which years “this writing” covers.

The files answer part of it. The natural gas files first hold a whole trade in 1994. Every year from 1994 to 2008 is profitable, and 2009 is a loss. So the length of the streak ending in any year depends on where the count starts:

```math
\begin{array}{l|r|r}
\text{Streak ending in} & \text{From 1995} & \text{From 1994} \\ \hline
2007 & 13 & 14 \\
2008 & 14 & 15
\end{array}
```

Read as first-edition figures counted from 1995, both of Chan’s counts reproduce. The main text’s 13 is the streak ending in 2007 and the sidebar’s 14 is the streak ending in 2008. Each natural gas trade closes by mid-April, so both streaks end before the first edition’s release in November 2008. This repository wrote that reading down as a hypothesis before computing any trade, as [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) records. The files bear on it in two ways, and neither proves it.

1. **They rule out a count written for the revised edition.** 2009 is a loss, and counted from 1995, a streak of 13 or more can end only in 2007 or 2008. So neither count can describe a streak that reached into the years after the first edition.
2. **They cannot pick the start year.** 1994 is profitable too. Counted from 1994, the streaks of 13 and 14 end in 2006 and 2007 instead. The only reason to prefer 1995 is that Chan’s gasoline sidebar counts from 1995.

![“The start year decides where a streak ends”, drawn on a year axis from 1994 to 2009 that carries a label only at “1994”, “1995”, “2006”, “2007”, “2008” and “2009”. Each year from 1994 to 2008 has a green dot on the axis, and 2009 has a red cross labelled “loss”. A caption reads “dot: a profitable year”. A dashed grey line between 2008 and 2009 marks the “first edition, Nov 2008”. Above the axis two brown brackets start at 1995. “13 from 1995, main text” ends at 2007 and “14 from 1995, sidebar” ends at 2008, both before the dashed line. Below the axis two black brackets start at 1994. “13 from 1994” ends at 2006 and “14 from 1994” ends at 2007. Starting the count a year earlier ends each streak a year earlier.](../docs/figures/commodity_sketch_streak_start.gif)

So this post says natural gas reproduces under the first-edition reading counted from 1995, and never that it reproduces outright.

### Gasoline’s two claims read as two editions

Gasoline’s main text says 19 profitable years of the last 21 “as of 2015” (p. 183), which is revised-edition text. Its sidebar says Chan “would have realized a profit every year since 1995” (p. 184). That cannot be true as of 2015, because the main text’s count leaves 2 unprofitable years by then. So the sidebar reads as first-edition text, covering 1995 to 2008. Over those years the files show no losing year: 11 profitable years and 3 with no price on a trade date. On that reading, one book prints a 2015 count beside a 2008 claim, and a reader who takes both as one moment in time compares two different spans.

## Lesson 2: a missing row is not a losing year

Chan’s gasoline count is 19 profitable years of 21, from 1995 to 2015. The run gives this:

```math
\begin{array}{l|r}
\text{Gasoline, 1995 to 2015} & \text{Years} \\ \hline
\text{Profitable} & 16 \\
\text{Losing, 2009 and 2012} & 2 \\
\text{No row, 1997 to 1999} & 3 \\ \hline
\text{Total} & 21
\end{array}
```

Three years have no price on a trade date. EIA’s New York Harbor file holds no row on 14 April 1997, the entry date that year, or on 24 April 1998 and 23 April 1999, the exit dates those years. Each was a trading day. Under the missing-row rule above, those years count neither way.

Taking a neighbouring day’s price instead would turn a gap into a guess, and a guess that decides the count it is meant to check. So the files show 16 profitable years and 2 losses, and they bound Chan’s count between 16 and 19 without settling it.

One more missing row leaves a question open without changing the count. RBOB began trading in October 2005, so the first April it covers is 2006, and the run reads RBOB from then. The older New York Harbor contract still traded in April 2006, but its file has no row on 13 April 2006, so the files cannot say whether reading the older contract that year would change the 2006 result.

### Two losses, as many as Chan’s count allows

The losses say more than the gaps do. Chan’s 19 of 21 allows exactly 2 losing years, and the files show exactly 2, in 2009 and 2012. So in the years they have prices for, the files fit Chan’s count. If Chan’s data agrees with EIA’s on the other 18 years, his 19 holds only if his data shows all 3 years with no price on a trade date as profitable. The files cannot say whether those 3 years were profitable, and no other source this repository holds covers the contract in those years.

The verdict [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) records for Chan’s 19 of 21 is “reproduced with a gap”. The criterion written down in advance was exactly 19 profitable years, and the run found 16, so this repository chose the verdict after the criterion failed. The log’s rule allows that verdict when the claim survives, the number differs, and the difference has a named cause outside the method. Here no year the files can read contradicts Chan’s claim, and the missing rows in EIA’s file are the named cause.

## Lesson 3: a trade chosen after looking at the history is tested by the years after the book

Chan picked both trades by studying past prices. The gasoline sidebar says he found the best trade after scanning the literature, and both rules name exact days. A rule chosen from the past tends to look good on the past, so the years it was chosen on cannot test it. The years after the book can. Here the book’s years end at the last year Chan’s counts cover for each trade. For gasoline that is 2015, the year his revised edition’s count runs to. For natural gas it is 2008, where the sidebar’s 14 ends under Lesson 1’s reading, a year after the main text’s 13 ends. The table below starts natural gas in 1994, the first year the files hold a whole trade and one year before the counts in that reading start.

```math
\small\begin{array}{l|l|r|r}
\text{Trade} & \text{Years} & \text{Won} & \text{No row} \\ \hline
\text{Natural gas} & \text{1994 to 2008} & 15 \text{ of } 15 & 0 \\
 & \text{2009 to 2023} & 7 \text{ of } 15 & 0 \\ \hline
\text{Gasoline} & \text{1995 to 2015} & 16 \text{ of } 21 & 3 \\
 & \text{2016 to 2023} & 3 \text{ of } 8 & 0
\end{array}
```

For natural gas the trade went from winning every year to winning fewer than half. Chan says as much himself: the natural gas trade “didn’t hold up as well out-of-sample” (p. 185), meaning in years he did not use to choose the rule. He prints no figure for it. The files give 7 of 15 for 2009 to 2023, a span that runs past the last year he could have seen.

For gasoline, Chan marks the last 9 of his 21 years, 2007 to 2015, as out of sample. The trade won 7 of those 9, and both of its losing years fall among them. From 2016 to 2023, after the revised edition’s count ends, it won 3 of 8. Natural gas won 4 of the same 8.

![Two panels of bar charts, one bar per year showing the change in settlement price from entry to exit. The upper panel is gasoline, the May contract from the close of April 13 to the close of April 25, from 1995 to 2023 in dollars a gallon. Its years 1997, 1998 and 1999 are empty slots labelled “no row”. A dashed line after 2015 divides 1995 to 2015, 16 of 21 profitable and 3 with no row, from 2016 to 2023, 3 of 8 profitable. Bars before the line are mostly small and positive, with losses in 2009 and 2012, and five of the eight after it are losses. The lower panel is natural gas, the June contract from the close of February 25 to the close of April 15, from 1994 to 2023 in dollars per million Btu. A dashed line after 2008 divides 1994 to 2008, 15 of 15 profitable, from 2009 to 2023, 7 of 15 profitable. Every bar before the line is positive. After it, 8 years are losses and 7 are gains, in no regular order, including one gain near three dollars in 2022. Marks along the foot of each panel point up for each profitable year and down for each losing one.](../docs/figures/commodity_seasonals_years.png)

*Every year of both trades. Each dashed line is where the book’s years end, and the marks along each foot give every year’s sign, including years too small to see as bars.*

### What these years cannot grade

The split before and after the book is no verdict on whether either trade is alive. For each trade, the book’s years include the years Chan chose its rule on, so the drop after the book can overstate how much either trade weakened. The run charges no costs in any year, so neither side of the split says whether either trade pays after costs. Nobody wrote down a test for “alive” before this repository computed these years. The figures describe the record. They do not grade Chan’s claim, and like every result here the split is exploratory.

Chan himself raises the same doubt about the years his rules were chosen on, and offers a check. A trade that happens once a year produces few results, he writes, so it is hard to tell whether its results on past prices reflect data-snooping bias, meaning a pattern found by searching the past that will not repeat. He suggests trying somewhat different entry and exit dates to see whether the profits hold up (p. 186). This repository did not try them. Varying the dates until some version works is a search across many trades, and a search needs its own safeguards: a list of the variants written down before any is run, a bar for success that rises with the number of variants tried, and years held back that the search never sees.

## Lesson 4: reading one named contract from files numbered by expiry needs a calendar checked outside the files

EIA’s files hold contract 1, contract 2 and so on, not the May contract or the June contract. So for every trade date the run has to know which numbered file holds the contract Chan names.

For gasoline the answer is simple. The April contract stops trading on the last trading day of March, and the May contract trades until the last trading day of April, so May is contract 1 on both trade dates. For natural gas the number changes. A natural gas contract stops trading three trading days before its delivery month begins. So the June contract is contract 4 on February 25 if the March contract has not yet expired, because March, April and May still come before it. It is contract 3 if March has expired, and contract 2 by mid-April.

![“Which file holds the June contract”, drawn twice on one calendar from late February to the start of May. Each time, four stacked bars labelled “March”, “April”, “May” and “June” stand for the natural gas contracts, each ending at its last trading day, with June’s bar in brown running off the right. The upper set is “2008”, where March’s bar ends on February 27, marked “March still trading”. A dashed line at the entry crosses all four bars, labelled “June is contract 4 on Feb 25”, and a dashed line at the exit crosses May and June, labelled “contract 2 on Apr 15”. The lower set, with its own “March”, “April”, “May” and “June”, is “2006”, where March’s bar ends on February 24, marked “March has expired”. Its entry line crosses only April, May and June, labelled “June is contract 3 on Feb 27”, and its exit line crosses May and June, labelled “contract 2 on Apr 13”. It closes on “June’s number is how many bars each line crosses”.](../docs/figures/commodity_sketch_june_file.gif)

*In 2006, February 25 fell on a Saturday, so the trade entered on Monday the 27th, after March had expired. April 15 was a Saturday and the 14th was Good Friday, so the exit moved back to the 13th.*

### Three checks of the expiry rule

Because the June contract moves between files, the expiry rule is part of the result, so the run checks it three ways.

1. **Against the exchange’s own dates.** Massive, a market data vendor, records the last trading day the exchange set for each contract. For 16 contracts, March to June of 2017, 2018, 2021 and 2024, the rule gives the date Massive recorded. This repository read those 16 dates on 3 October 2026 and holds no code that can fetch them again, so its tests keep the 16 dates as they were read that day.
2. **Against the files’ own handovers.** When a contract expires, every later contract moves up one number. So on the day after an expiry, each file’s price should carry on from the price the file one number higher showed the day before. Contract 2’s file, for example, picks up where contract 3’s file left off. Before mid-1997 the files show contracts stopping five or six trading days before delivery rather than three. For the March 1996 contract, the price handover in late February 1996 fits a five-day rule and not a three-day one. After the first run, a review made the run follow the files’ handovers before mid-1997 instead of the three-day rule. That moves the 1996 and 1997 entries from contract 4 to contract 3. Both years are profitable on either contract, so the correction changed no count.
3. **Against the edge cases.** In 10 of the 30 years, the entry date falls on the March contract’s last trading day. The rule counts a contract as trading on its own last day, so the run reads June as contract 4 on those days. Reading contract 3 instead flips no year’s result.

The run also computes its own calendar of trading days and expiries rather than reading it from the files, because a row in the files does not show that the exchange was open. On every exchange holiday from January 2018 to November 2019, the natural gas files hold a row that repeats the previous trading day’s settlement. In other years they hold a row on almost no holiday. Of NYMEX’s holidays, only Good Friday can land on a trade date, and it moved six trade dates between 1994 and 2023.

The same map from dates to contracts serves Chan’s calendar spreads, trades that buy one delivery month and sell another, tested on the same files. [The calendar spreads post](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) reports what those spreads showed.

## What this replication cannot say

Six questions are beyond it.

1. **What the 3 trade dates with no row held.** EIA’s New York Harbor file has no row on one trade date in each of 1997, 1998 and 1999, and no other source this repository holds covers the contract then.
2. **Whether Chan read the same contracts.** His sidebar names RB, the symbol RBOB trades under, and glosses it as the unleaded gasoline futures. Before RBOB began trading in October 2005, his series presumably held the older contract, and the run assumes so. Chan does not name his data vendor.
3. **Which year each natural gas count was written in.** Lesson 1’s reading is a hypothesis the files constrain and cannot prove.
4. **Whether either trade pays after costs.** The run charges no commission and no slippage, the gap between the settlement price and the price an order would actually get. It also ignores margin, the deposit a broker holds against each futures contract.
5. **Whether nearby dates hold up.** This repository did not try Chan’s own suggested check, on p. 186, for the reason Lesson 3 gives.
6. **Any year after 2023.** EIA’s RBOB and natural gas files end on 5 April 2024, before either trade’s 2024 exit date. Another vendor could extend the record. Massive returned gasoline prices for April 2025, and nothing here reads them yet.

## What this means for a trader

Three habits follow from the first three lessons.

1. **Ask a consecutive count where it starts and when it was written.** The same files give 13, 14 or 15 consecutive years for natural gas, depending on both.
2. **Read a missing year as missing.** Three gaps in one file leave Chan’s gasoline count anywhere between 16 and 19, and filling them with a neighbouring day would decide the answer instead of checking it.
3. **Judge a seasonal trade on the years after it was chosen.** Natural gas won every year through 2008 and fewer than half after, and Chan picked its rule from years before the book.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Released in November 2008.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 175 and 183 to 186. Page numbers here are the revised edition’s. The replication log cites the passages on pp. 183 to 185 by Kindle location, 4529 to 4632.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for New York Harbor regular gasoline, RBOB gasoline and Henry Hub natural gas, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the two trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_whiteboard.py), with the checks behind [the trades’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_whiteboard.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
