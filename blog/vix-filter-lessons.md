# Chan’s VIX filter reproduces on his own files, and a test cannot tell the mean return on the days it keeps from the rest

*Chan backtests two gap rules on the days after VIX closed above 35. Buy on gap’s return rises to 17.2 percent and FSTX’s falls to 2.6. Both reproduce, but a test cannot tell the kept days’ mean return from the rest, and one day earns most of the 17.2.*

## Why filter a strategy on the VIX

A risk indicator is a number read before a trade that is meant to say how risky the next day will be. If one worked, a trader could stand aside on the days it flags. Ernest Chan’s *Algorithmic Trading* argues that no single one serves every strategy: “There is no one risk indicator that is applicable to all strategies: What is a risky period to one strategy may be a highly profitable period for another” (Chan, 2013, Kindle edition, p. 269).

He makes the case with the **VIX**, an index the Chicago Board Options Exchange computes from the prices of options on the S&P 500. It measures the swings those options imply for the next month, so it rises when traders expect turmoil. Chan keeps only the days after VIX closed above 35, “a common threshold for highly risky periods” (p. 269), and reruns two rules the book already ran.

1. **Buy on gap**, Example 4.1, which buys stocks that opened far below the previous day’s low and sells them at the close. Far below means the return from that low to the open is a loss larger than the 90-day standard deviation of the stock’s daily returns, and the open must still sit above the 20-day moving average of the stock’s closes. On every day, Chan reports “an annualized average return of around 8.7 percent and a Sharpe ratio of 1.5” (p. 269). The Sharpe ratio is the return per unit of day-to-day swing, and Lesson 1 gives its formula. On the kept days he reports 17.2 percent and 1.4, and concludes that “this strategy benefits from the so-called risk!” (p. 269).
2. **The opening gap rule on FSTX**, Example 7.1. FSTX is a futures contract on the STOXX Europe 50 index. Chan’s script goes long when FSTX opens above the previous day’s high, and short when it opens below the previous day’s low. The open must clear that high or low by at least a tenth of the 90-day standard deviation of FSTX’s daily returns, with that distance measured as a return from the high or low. The script holds the position from the open to the close. The line of the script that computes its return, though, credits a long position when the price falls from the open. So in effect the script bets that a price opening above the high falls by the close and one opening below the low rises, which trades against the jump at the open, as Lesson 2 explains. On every day, Chan reports “around 13 percent and a Sharpe ratio of 1.4” (p. 269). On the kept days the return drops to “2.6 percent and the Sharpe ratio to 0.16” (p. 269). He concludes that “VIX tells us to avoid trading on the following day” (p. 269).

### What the reproduction found

This repository ran buy on gap and the opening gap rule on FSTX unchanged on Chan’s own files and applied the filter. The results fall into five lessons.

1. **The filtered figure is 252 times the mean, and the unfiltered one beside it is compounded.** Buy on gap gives 0.171924 and a Sharpe ratio of 1.417425 on 190 kept days, which round to 17.2 percent and 1.4, the figures Chan prints. The 8.7 percent Chan sets beside it comes from a different formula.
2. **FSTX’s figures belong to the script’s fading sign.** Chan’s script for Example 7.1 computes its return with the sign that trades against the jump at the open. His text describes following the jump, which this post calls momentum. Under the script’s sign the figures are 0.025730 and 0.164869 on 185 kept days, and momentum gives them negated.
3. **The 2.6 percent depends on which VIX close each FSTX day reads, and a search chose the join.** The replication tried six ways of reading VIX on FSTX’s days, and only one, which this post calls the join, lands both printed figures. The join uses only the days both calendars share and reads VIX’s close on the previous shared day.
4. **The kept days are few, and most fall in 2008 and 2009.** Buy on gap held a position on 20 of its 190 kept days, and one of those days earned most of its return.
5. **A test cannot tell the mean return on kept days from the rest.** For either rule, the mean return on kept days differs from the other days’ by less than chance alone would often produce.

### What the sample can support

**Every result here is exploratory.** Three reasons make it so.

1. Chan chose the rules, the threshold and the windows, and reported his figures on these same files. So reproducing them checks his arithmetic but leaves no unseen data on which to test his choices.
2. The replication chose the join after seeing its figures, as Lesson 3 says. It also chose to read Chan’s filtered return as 252 times the mean daily return after seeing what two other formulas give. One compounds the daily returns into a yearly rate. The other averages over every day, counting each day the filter leaves out as zero. Lesson 1 sets out all three.
3. Every kept day falls from 2008 to 2011, so the sample holds few separate episodes of high VIX.

So the run can say whether his numbers follow from his files, and nothing about whether VIX above 35 guards either rule today. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The filter, the two rules and the files

**The filter.** A day is kept when VIX’s close on the previous day was strictly above 35. VIX closes at 16:15 New York time, so the previous day’s close is known before either rule trades. No close in Chan’s VIX file sits exactly on 35, so reading “above 35” as strictly above or as 35 and above keeps the same days. The nearest closes are 35.02 on 2010-05-26, just above, and 34.95 on 2001-10-18, just below. The 35.02 falls inside the dates both rules cover. Inside those dates, the nearest close below 35 is 34.78 on 2011-10-20.

**The two rules.** The [buy on gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#the-strategy-and-the-file) sets out Example 4.1’s four rules and the file of 497 stocks it reads. The [opening gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#the-rule-and-the-file) sets out Example 7.1’s rule on FSTX, and its [Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-1-the-script-trades-against-the-jump-the-text-says-it-follows) shows that the script’s return line fades the jump at the open, while the text describes following it. Both rules run here exactly as those posts ran them. The filter only chooses which of their days count.

**The files.** The run reads three of Chan’s saved files, each recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md).

1. **VIX** from Chan’s `VIX.csv`, saved 2012-05-09, 5,635 closes from 1990-01-02 to 2012-05-08. A CSV records no save date, so that date is the one stamped on the copy inside the zip of Chan’s Python code.
2. **The stocks** from Chan’s `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, 1,500 days from 2006-05-11 to 2012-04-24. Every stock was in the S&P 500 in late 2011, so every figure on them is about survivors.
3. **FSTX** from Chan’s `inputDataOHLCDaily_20120517.mat`, saved 2012-05-18, 2,000 days from 2004-07-16 to 2012-05-17. The file holds 52 futures series, FSTX among them. The data README’s row for the file starts in 1995 because that row covers all 52 series.

**The join.** Each rule runs on its own full calendar first. The join then drops each rule’s daily returns on any day missing from VIX’s calendar, and the filter reads VIX’s close on the previous day the two calendars share. Buy on gap loses none of its 1,500 days, because the stock file’s days are exactly VIX’s days over that span. FSTX is left with 1,945 of its 2,000. It loses the 7 days after VIX’s last close and 48 days on which Eurex, the European exchange FSTX trades on, was open and the US exchanges were not.

**No script ships for the filter on p. 269.** This repository has read three public copies of Chan’s code, and none holds a file that applies the filter.

1. ivanliu1989/algorithmic_trading.
2. ericnberwick/EpchanPreview.
3. burakbayramli/books.

So this replication inferred the specification above from the figures Chan prints for the filter, 17.2 percent and 1.4 for buy on gap and 2.6 percent and 0.16 for FSTX, rather than reading it from code. The [replication log’s Entry 47](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-47-the-vix-filter-on-buy-on-gap-and-the-stoxx-europe-50-gap-rule-chans-algorithmic-trading) records every reading the replication tried and sets each figure beside the test that computes it.

## Lesson 1: the filtered figure is 252 times the mean, and the unfiltered one beside it is compounded

Chan calls both of buy on gap’s returns an “annualized average return” (p. 269). Two formulas could sit behind that phrase.

1. **The arithmetic figure**, 252 times the mean daily return. It scales an average day to a year of 252 trading days.
2. **The compounded APR**, short for annual percentage rate. It is the yearly rate that, compounded, turns one dollar into what the daily returns multiply out to.

On the kept days the arithmetic figure lands Chan’s number and the compounded one misses. On every day it is the other way round. The table sets both formulas, on the 190 kept days and on all 1,500 days, beside the book’s figures.

```math
\small\begin{array}{l|r|r}
 & \text{Kept days} & \text{Every day} \\ \hline
\text{Days} & 190 & 1{,}500 \\
252 \times \text{mean} & 0.171924 & 0.085279 \\
\text{Compounded APR} & 0.179297 & 0.087385 \\
\text{Sharpe ratio} & 1.417425 & 1.537063 \\ \hline
\text{Book return} & 17.2\ \text{percent} & 8.7\ \text{percent} \\
\text{Book Sharpe ratio} & 1.4 & 1.5
\end{array}
```

The Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate. On the kept days, 252 times the mean, 0.171924, prints as Chan’s 17.2 percent, while the compounded APR, 0.179297, would print as 17.9. On every day, the compounded APR, 0.087385, prints as his 8.7 percent, while 252 times the mean, 0.085279, would print as 8.5. The [buy on gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) works through the every-day pair. So in two consecutive sentences on p. 269, Chan’s phrase “annualized average return” names the compounded figure for every day and the arithmetic one for the kept days.

A third reading also takes 252 times the mean, but sets the return to zero on each day the filter leaves out and averages over all 1,500 days, as if the trader held cash on them. It gives 0.021777, which would print as 2.2 percent, and a Sharpe ratio of 0.503869, both far from Chan’s 17.2 percent and 1.4. So Chan’s average runs over the kept days alone.

### The filter’s effect with one formula throughout

The comparison Chan draws survives the mismatch of formulas. Like for like, 252 times the mean rises from 0.085279 on every day to 0.171924 on the kept days. The Sharpe ratio moves the other way, from 1.537063 to 1.417425, so the kept days earned more per day, but the swing of their daily returns grew by a larger factor than the mean did. Lesson 5 asks whether the rise in the mean is larger than chance, and nothing here tests the Sharpe ratio’s fall.

## Lesson 2: FSTX’s figures belong to the script’s fading sign

This post calls the script’s sign the fade and the text’s sign momentum. The opening gap post calls the fade the literal reading. Its [Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-1-the-script-trades-against-the-jump-the-text-says-it-follows) found that the script’s return line credits a long position when the price falls from the open, the reverse of how a long normally earns, so in effect the script trades against the jump. The text describes the opposite, “buying when the instrument gaps up, and shorting when it gaps down” (p. 229), and the [same post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-3-the-momentum-the-book-describes-loses-what-the-script-earns) shows that sign losing what the script earns.

The filtered figures follow the fade. The table gives the fade’s figures on the 185 kept days, on all 1,945 days joined to VIX, and on all 2,000 days of Example 7.1, beside the book’s.

```math
\small\begin{array}{l|r|r|r}
\text{Fade} & \text{Kept} & \text{Joined} & \text{All} \\ \hline
\text{Days} & 185 & 1{,}945 & 2{,}000 \\
252 \times \text{mean} & 0.025730 & 0.139950 & 0.128622 \\
\text{Sharpe ratio} & 0.164869 & 1.589197 & 1.441620 \\ \hline
\text{Book return} & 2.6\% & & \text{around } 13\% \\
\text{Book Sharpe} & 0.16 & & 1.4
\end{array}
```

The fade’s 0.025730 and 0.164869 on the kept days print as the book’s 2.6 percent and 0.16. Momentum’s returns are the fade’s negated day for day, so on the kept days it gives −0.025730 and −0.164869. It misses both printed figures, landing 5.2 percentage points and 0.32 below them.

### Which days the book’s FSTX figures cover

The book’s FSTX figures without the filter and with it come from different calendars. Its “around 13 percent and a Sharpe ratio of 1.4” (p. 269) is Example 7.1 on all 2,000 days. There the Sharpe ratio is 1.441620, and both the compounded APR, 0.132733, and 252 times the mean, 0.128622, print as 13 percent, as the [opening gap post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-2-both-printed-figures-land-on-the-script-as-written) shows. On the 1,945 days joined to VIX, 252 times the mean is 0.139950 and the Sharpe ratio 1.589197, which print as 14 percent and 1.6. The join that lands the filtered 2.6 percent takes its kept days from the 1,945 joined days, while the 13 percent covers all 2,000, so the comparison Chan draws mixes two calendars.

### The filter’s effect under each sign

The filter moves the two signs’ mean returns in opposite directions. Under the fade, 252 times the mean falls from 0.139950 on every joined day to 0.025730 on the kept days. That is the direction Chan reports, and the one his conclusion that “VIX tells us to avoid trading” (p. 269) points to. Under momentum it rises from −0.139950 to −0.025730, so for the sign the text describes, the kept days are the less bad ones, and its mean return moves against that conclusion. Lesson 5 tests whether either change in the mean return is larger than chance.

## Lesson 3: the 2.6 percent depends on which VIX close each FSTX day reads, and a search chose the join

FSTX trades on Eurex and the Chicago Board Options Exchange computes VIX, so the two calendars disagree on US and European holidays. Reading “the preceding day’s VIX” (p. 269) on FSTX’s days needs a choice for those days, and Chan’s sentence makes none. The replication tried six readings, saw their figures, and chose the one that lands both printed figures.

1. **Join.** Keep only the days both calendars share, and read VIX’s close on the previous shared day.
2. **Latest close.** Read VIX’s latest close before each FSTX day.
3. **Filled forward.** Copy each VIX close onto any following FSTX day that has none, and read VIX’s close on FSTX’s previous day.
4. **Row back.** Step back one row on FSTX’s own calendar, read VIX’s close on that day, and drop the day when VIX has none.
5. **Same day.** Read VIX’s close on the trade’s own date, which is missing on US holidays.
6. **Same day, filled.** Read the same, with VIX filled forward onto US holidays.

In the table, the return is 252 times the mean.

```math
\small\begin{array}{l|r|r|r}
 & \text{Days} & \text{Return} & \text{Sharpe} \\ \hline
\text{Join} & 185 & 0.025730 & 0.164869 \\
\text{Latest close} & 188 & 0.025319 & 0.163555 \\
\text{Filled forward} & 188 & 0.025319 & 0.163555 \\
\text{Row back} & 185 & 0.045238 & 0.291589 \\
\text{Same day} & 185 & -0.047063 & -0.297416 \\
\text{Same day, filled} & 188 & -0.046312 & -0.295046
\end{array}
```

The join lands 2.6 percent and 0.16. The latest close lands the Sharpe ratio and prints the return as 2.5 percent. It keeps 2008-11-27, 2009-01-19 and 2009-02-16, US holidays on which Eurex traded and which the join drops, and on each it reads the close before the holiday. Filling VIX forward keeps the same 188 days. Reading a row back keeps those three holidays and drops the day after each, because that day’s previous FSTX day is the holiday, which has no VIX close. It lands neither figure. The last two read VIX on the trade’s own date. VIX closes hours after FSTX opens, so they use a close the trader could not yet know, which rules them out whatever their figures.

![Whiteboard sketch, “One US holiday, four readings”, drawn slowly, with its finished drawing held for twelve seconds. Its columns stand evenly apart, and every figure in it comes from the run. Three columns are headed “Wed 11-26”, “Thu 11-27” and “Fri 11-28” over a grey rule. In the row “VIX closed” they read “54.92”, “none: US holiday” and, in grey, “55.28”, with the grey note “read by 12-01”. In the row “FSTX traded” each column has a black check. Below come four rows, one for each of the four readings that take the previous day’s close. In each row a black arrow runs from each trade day on that reading’s calendar back to the column whose close that day reads, and a word sits at each arrow’s tail. In the “Join” row the Thursday has no arrow and reads, in grey, “not on the joined calendar”, and the Friday’s arrow runs back to the Wednesday, marked in green “kept”. In the “Latest close” row both arrows run back to the Wednesday, the Thursday’s marked in green “kept” and the Friday’s “kept”. The “Filled forward” row is drawn the same, “kept” and “kept”. In the “Row back” row the Thursday’s arrow runs back to the Wednesday, marked in green “kept”, and the Friday’s arrow runs back only to the Thursday, which has no close, marked in red “dropped”. No arrow reaches the Friday’s grey “55.28”.](../docs/figures/vix_filter_sketch_one_holiday.gif)

### What the search settles and what it leaves open

Four facts bound what the search means.

1. **Buy on gap does not move.** Every reading that takes the previous day gives it the same 190 days and the same figures, because its calendar is VIX’s. The search moved only FSTX.
2. **The figures cannot tell joining the calendars before running the rule from joining them after.** Running FSTX’s rule on the 1,945 joined days, rather than on its own 2,000 days with the join after, changes the return on 11 joined days and on none of the 185 kept days. Ten of those 11 are the first joined day after a day the US exchanges were shut and Eurex was open. On the joined days, the rule compares the open on each of those ten with the high or low of two Eurex sessions back, because the day the US exchanges were shut is no longer there. The eleventh, 2005-09-20, moves because on the joined days its 90-day standard deviation spans a different set of days. So the figures cannot say which order Chan used.
3. **Nothing here rules out a seventh reading.** Only the join lands both figures among the six, and another reading could land them too.
4. **The save matters too.** Chan saved FSTX’s file on several dates in May 2012, and the [opening gap post’s Lesson 4](https://github.com/l3a0/quantitative-trading/blob/main/blog/opening-gap-lessons.md#lesson-4-the-save-and-its-window-both-decide-the-printed-digit) shows that the saves price it differently. On the two earlier saves that hold 2,000 days, the join keeps the same 185 days and gives 0.024899 and 0.162148, which print as 2.5 percent and 0.16. Only `inputDataOHLCDaily_20120517.mat`, the save Example 7.1’s script loads, lands 2.6.

So for FSTX the 2.6 percent is a fit to the printed figure rather than a test of it. **Every result here is exploratory**, and this one most of all.

## Lesson 4: the kept days are few, and most fall in 2008 and 2009

From 2004-07-16 to 2012-05-08, the span FSTX’s days share with VIX’s, VIX closed above 35 on 190 days. All of them fall inside buy on gap’s span, from 2006-05-11 to 2012-04-24, and each one keeps the next day on buy on gap’s calendar, which is why buy on gap keeps 190 days too. The first of those 190 closes was 36.22 on 2008-09-17. The highest was 80.86 on 2008-11-20, and the last was 36.16 on 2011-11-09. Chan’s `VIX.csv` also closes above 35 on 100 earlier days, the first of them on 1990-08-06, so VIX crossed the threshold long before either rule’s data begins.

### How the kept days cluster

Both rules keep days from 2008-09-18 to 2011-11-10, and most of them in the first two of those years.

```math
\begin{array}{l|r|r}
\text{Year} & \text{Buy on gap} & \text{FSTX} \\ \hline
2008 & 68 & 65 \\
2009 & 83 & 81 \\
2010 & 9 & 9 \\
2011 & 30 & 30 \\ \hline
\text{Kept days} & 190 & 185
\end{array}
```

So 151 of buy on gap’s 190 kept days, and 146 of FSTX’s 185, fall in 2008 and 2009.

The kept days also come in runs. A run here is a group of kept days in a row on the joined calendar, with no day the filter leaves out between them. Each rule’s kept days form 15 runs. The longest, from 2008-09-30 to 2009-04-17, holds 138 of buy on gap’s days and 134 of FSTX’s, so that one run alone holds most of the kept days.

The 15 runs fall in only three spells of high VIX, each a year or more from the next, so they are not 15 separate episodes.

1. September 2008 to May 2009, which holds the 151 and 146 days above.
2. May to June 2010.
3. August to November 2011.

### How few kept days were traded, and how much one earned

A kept day is not a day traded. Buy on gap held a position on only 20 of its 190 kept days, and its filtered figures rest on those 20. It gained on 8 and lost on 12. One of them, 2009-04-21, returned 0.093601, which is 0.722090, or 72.2 percent, of the 0.129625 that the kept days’ returns sum to. Without that day, both filtered figures fall, and the other 189 give 0.048032 and a Sharpe ratio of 0.855003, which print as 4.8 percent and 0.86. Over all 1,500 days but 2009-04-21, 252 times the mean is 0.069600, above the other 189 kept days’ 0.048032. So without that day the rise Lesson 1 measures, from 0.085279 to 0.171924, becomes a fall. FSTX held a position on 43 of its 185 kept days, long on 21 and short on 22.

![Whiteboard sketch, “What buy on gap’s kept days earned”, drawn slowly, with its finished drawing held for twelve seconds. Every figure and every bar’s height comes from the run, and its ticks and bars stand evenly apart in date order, with no date axis. A row of 190 thin black ticks runs across the top, marked “190 kept days”, and 170 of them turn grey, marked in grey “170 held nothing: each earns 0”. A black dot then appears over each of the other ticks, marked “20 held a position”. Below, a grey zero line appears, marked “0”, and 20 bars stand evenly spaced in date order on it, drawn as outlines to one scale, with green bars above it and short red bars below. Several are so short they show only as dashes on the line. On the right, in green, “8 gained, above 0”, a count that includes the brass bar described next, and in red, “12 lost, below 0”. One brass bar stands far above the rest, marked in brass “2009-04-21: 0.093601”. Along the foot, in brass, “that day is 0.722090 of the 0.129625 the kept days sum to”. A black line then strikes through the brass bar, and the last line reads “the other 189: 252 × mean 0.048032, Sharpe 0.855003”.](../docs/figures/vix_filter_sketch_kept_days.gif)

![Two charts on one shared date axis from July 2004 to May 2012. The top chart shows VIX’s daily close as a black line, mostly between 10 and 20 until mid-2007, with a dashed red line at 35. A grey band covers 2008-09-18 to 2011-11-10. Brass dots mark the 190 closes above 35, which cluster in late 2008 and early 2009, with small groups in May and June 2010 and from August to November 2011. Labels mark the first close above 35 inside the window, 36.22 on 2008-09-17, the highest, 80.86 on 2008-11-20, and the last, 36.16 on 2011-11-09. The bottom chart shows each rule’s daily returns summed over its kept days, flat at zero before September 2008 and flat after November 2011. Buy on gap’s black line wavers between about −0.015 and 0.025 until April 2009, jumps at a brass dot labelled “2009-04-21 alone adds 0.093601”, and ends at 0.129625. FSTX under the script’s sign, a dashed grey line, swings between about −0.08 and 0.11 in late 2008 and early 2009 and ends at 0.018889. FSTX under the sign the text describes, a red line, mirrors it and ends at −0.018889. The heading sets each rule’s figures beside the book’s, and the title calls the figure exploratory.](../docs/figures/vix_filter.png)

*Each curve in the bottom panel is a sum, unlike the compounded curves in the buy on gap and opening gap posts, because the filtered figures on p. 269 are arithmetic means. Each ends at its mean daily return times its number of kept days. For buy on gap that is 0.171924 × 190 / 252, or 0.129625. The book draws no figure for the filter.*

### Rare crises make a false pattern easy to find

Chan warns about testing any risk indicator on a sample that holds few crises. “Since the occurrence of financial panic or crises is relatively rare, it is very easy to fall victim to data-snooping bias when we try to decide whether an indicator is useful” (p. 271). Data snooping is finding a pattern in a sample because someone searched the sample for one. Here 151 of buy on gap’s 190 kept days fall in one panic, the spell from September 2008 to May 2009, and the rule’s 17.2 percent rests mostly on one day inside it. **Every result here is exploratory.**

## Lesson 5: a test cannot tell the mean return on kept days from the rest

Chan reads his figures as evidence that VIX above 35 changes what each rule earns. That is a claim about two groups of days, the kept days and the others, so a test can check it. **Welch’s t-test** compares the mean of two groups. It divides the difference between the means by how far that difference would typically wander by chance, allowing each group its own spread, and calls the ratio t. A t near zero means the difference is small against that wander. The p-value is the chance of a t at least that far from zero if the two groups had the same mean. The table compares each rule’s kept days with its other joined days.

```math
\small\begin{array}{l|r|r}
 & t & p \\ \hline
\text{Buy on gap} & 0.705402 & 0.481405 \\
\text{FSTX, fade} & -0.684181 & 0.494679 \\
\text{FSTX, momentum} & 0.684181 & 0.494679
\end{array}
```

Each rule’s p-value sits near one half. A difference this size, or larger, would turn up about half the time between two groups with the same mean. So this test cannot tell either rule’s mean return on kept days from its mean on other days, in either direction and under either sign. A p near one half says this sample cannot tell, not that the filter does nothing. Chan prints no test, and the figures he prints are point estimates, single numbers with no measure of how much they could move.

The test treats each day as independent of the others. Kept days come in runs, and returns on neighbouring days can move together. When they rise and fall together, the test counts more independent days than the sample holds, and its p comes out too small, so a difference looks less like chance than it is. Buy on gap’s mean also rests mostly on one day, 2009-04-21.

**Every result here is exploratory**, and this one says only that Chan’s two filtered returns, though they reproduce, are not evidence that VIX above 35 moves either rule’s mean return either way. Nothing here tests his two filtered Sharpe ratios.

## What this replication cannot say

Six questions are beyond it.

1. **What Chan’s own code for the filter did.** No script ships for the filter on p. 269, and a search chose the join for FSTX.
2. **Whether Chan joined the calendars before or after running the rule.** Both orders give the same figures on FSTX’s kept days, as Lesson 3 says.
3. **Whether the filter guards either rule after 2012.** Every kept day falls from 2008 to 2011. A test of the filter on later data would write down at least these nine choices before reading that data.
   1. The threshold.
   2. The join.
   3. The formula, 252 times the mean.
   4. Each rule’s own settings, as the book states them.
   5. The sign of FSTX’s return line.
   6. The stocks buy on gap may choose from on each day.
   7. The costs charged on each trade.
   8. The direction each rule’s mean return should move on kept days.
   9. The test that compares the kept days with the rest, and the p below which a difference counts as more than chance, with that p chosen for the two rules together.
4. **What buy on gap earned on the index as it stood each day.** Every stock here was in the S&P 500 in late 2011, so a company outside the index for all of late 2011 is missing, even on the days it was a member. The [buy on gap post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-6-an-exact-reproduction-checks-the-arithmetic-not-the-edge) shows that an exact reproduction checks the arithmetic, not the edge, and that holds for the kept days too.
5. **Whether every price in the files is right.** The repository has a check for a sudden change of scale, such as a vendor multiplying every close from some day on by a constant. What it covers differs by file, and some prices need a second source that nothing here reads.
   - **FSTX.** The run applies the check to every FSTX close in the file, and it flags none.
   - **VIX’s flagged day.** The check flags one VIX day, 2007-02-27, a move from 11.15 to 18.31 that reads as real, and nothing here compares it with a second source. If the move were a change of scale instead, undoing it would mean rescaling the closes on one side of that day by 18.31 over 11.15, either the later ones or the earlier ones.
   - **VIX’s later closes rescaled.** Dividing every close from 2007-02-27 on by that factor would make the lowest close after it, 11.98 on 2007-04-16, a true 7.3, below every earlier close in the file. That makes this reading unlikely but not impossible. Each rule would keep 34 days rather than 190 and 185. Buy on gap would hold a position on one of them and lose, printing −2.6 percent against 8.5 on every day, and FSTX would print 42.0 percent against 14 on every joined day. Both of Chan’s conclusions would turn the other way.
   - **VIX’s earlier closes rescaled.** Multiplying every close before 2007-02-27 by that factor would put the earlier closes inside the range of the later ones, so nothing in the file argues against this reading. It would make 23.81 on 2006-06-13 a true 39.1 and 21.46 the next day a true 35.2, which adds 2006-06-14 and 2006-06-15 to each rule’s kept days. Buy on gap would print 17.0 percent rather than 17.2, and FSTX 2.5 rather than 2.6, so neither of Chan’s conclusions would change.
   - **The rest of VIX.** From each rule’s first joined day on, the run applies the check to every day-over-day move it reads in VIX but the flagged one. There the check catches only a move of more than 1.6 times, so a rescale of 1.6 times or less could move a day into or out of the filter unseen.
   - **The stocks.** The run does not check the stocks’ prices. Run on them the way the buy on gap replication runs it, the same check flags 30 closes in 17 stocks, 20 of them on kept days. Buy on gap held none of those stocks from the flagged day through the 91 trading days after it, which covers every day whose 90-day standard deviation of daily returns or 20-day moving average reads that close. Dividing each of those stocks’ prices from each flagged day on by the size of its move changes none of buy on gap’s positions.
   - **Buy on gap’s best day.** The day that earns most of the 17.2 percent, 2009-04-21, rests on three opening prices in Chan’s file that sit 10 to 23 percent below the previous close. Nothing here compares those with a second source either.
6. **What costs would take.** The replication charges no costs on either rule, and a filter that keeps few traded days leaves each cost a larger share of the return.

## What this means for a trader

One habit for each lesson.

1. **Compare like with like.** Before reading a filter’s effect, put the filtered and unfiltered figures on the same formula. Here one was compounded and the other arithmetic.
2. **Run a filter under both signs of the rule it guards.** A filter that cuts one sign’s return raises the other’s, so which way it points depends on the sign.
3. **Count how many ways someone could read the data.** When someone infers a specification from a printed figure, every reading tried is part of the result, and the one that lands is a fit.
4. **Count the days traded, not the days kept, and find the largest one.** Here 20 traded days carried buy on gap’s filtered return, and one of them carried most of it.
5. **Test the difference between the kept days and the rest.** Two point estimates that differ are not evidence of a difference until something says how far they could wander by chance.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 4.1 and 7.1, with pages 229, 269 and 271 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.

*Not investment advice. Code: [the filter](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vix_filter.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vix_filter_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vix_filter_whiteboard.py), with the checks behind [the filter’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vix_filter.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vix_filter_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vix_filter_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-47-the-vix-filter-on-buy-on-gap-and-the-stoxx-europe-50-gap-rule-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
