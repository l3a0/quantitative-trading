# Chan’s VIX roll return trade reproduces on his own files, from the rule his script comments out, and its hedge leaves it mostly a trade in the E-mini

*Chan collects VIX futures’ roll return with E-mini futures as the hedge and reports 6.9 percent a year. Every figure lands on his files. The book’s rule is the one his script comments out, and its hedge leaves the trade mostly in the E-mini.*

## Why collect VIX futures’ roll return

A VIX future, which trades as VX, settles at the level of the VIX index on its expiry. So as settlement nears, its price converges on VIX. A contract priced above VIX tends to fall toward it, and one priced below tends to rise. That convergence is VX’s roll return, the part of a future’s return that comes from its price meeting the spot by expiry. The [post on spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#why-split-a-futures-return-in-two) builds up the roll return, the spot return, contango and backwardation. The [post on VX against the E-mini](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#why-trade-volatility-against-the-stock-index) explains what VIX measures, what the E-mini future ES is, and why the two move against each other.

VX usually sits above VIX, a state called contango. Ernest Chan’s *Algorithmic Trading* says VX “has been in contango around three fourths of the time” (Chan, 2013, location 2385), citing Simon and Campasano (2012). On Chan’s own VX file the front contract, defined below, sits above VIX on 1,016 of the 1,369 days it has one, from 2006-11-14 to 2012-04-23. That is close to three in four. The book gives no span for Simon and Campasano’s count, so the two cannot be compared.

Collecting a roll return alone means holding the future against something that tracks its underlying, so the underlying’s moves cancel. The [post on long GLD and short gold futures](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gc-lessons.md#why-own-the-metal-and-short-the-future) runs that trade on gold, where a fund holds the metal. Nothing holds VIX. Keeping a basket of options that replicates it is too expensive, and “no ETF sponsors have been foolish enough to do that” (location 2747). Chan argues that a stand-in only needs a high correlation, or anticorrelation, with the spot return. He picks ES, whose roll return is “about 1 percent annualized” (location 2747), so its return is almost the index’s.

The rule at location 2754 comes from Simon and Campasano (2012). If the front VX contract sits above VIX by 0.1 point times the trading days until settlement, “short 0.3906 front contracts of VX and short 1 front contract of ES.” If it sits below by that much, buy both. Either way, “Hold for one day.” Both legs take the same side because the two move against each other. A short VX position loses when the market falls and volatility rises, and a short ES position gains. Chan reports “6.9 percent, with a Sharpe ratio of 1” from July 29, 2010, to May 7, 2012, a window “not used for hedge ratio determination” (location 2754). He published the script, `VX_ES_rollreturn.m`, and this repository transcribed it line by line and ran it on the three files it loads.

The results fall into five groups.

1. **Both of the script’s rules land, and the book’s is the one it comments out.** The live lines trade one VX contract per ES contract and print an APR of 0.293906. The book’s 6.9 percent comes from the commented-out lines trading 0.3906.
2. **The printed 0.3906 is the specification.** The fitted hedge it rounds from misses the script’s sixth decimal on both the APR and the Sharpe ratio.
3. **Every entry is free, and the last ten days hold nothing.** Charging each entry one basis point lowers the APR to 0.067142.
4. **The window is out of sample for the hedge alone.** The threshold and the window that picks the front contract carry no such statement.
5. **The hedge leaves the trade mostly in the E-mini.** Under 0.3906 the VX leg is a median 0.119966 of the money held, and the ES leg gives back more than half of what the VX leg earns.

**Every result here is exploratory.** Simon and Campasano proposed the rule, and Chan chose the hedge and the dates. The reproduction runs them on his own files. It can say whether his numbers follow from those files, and nothing about whether the trade would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule, the script and the files

The script runs in six steps.

1. **It loads three files.** One holds VX contracts, one VIX and one ES.
2. **It keeps the days all three hold.**
3. **It picks the front contract for each day.** Each contract is the front from 40 rows to 10 rows before its last priced row, and no earlier than the row after the previous front ends. A row is one trading day in the file, and the script reads a contract’s last priced row as its expiry. The [post on XLE against USO](https://github.com/l3a0/quantitative-trading/blob/main/blog/xle-uso-roll-return-lessons.md#the-funds-the-ratio-and-the-files) works through this window, which `XLE_CL_rollReturn.m` shares. Outside every window there is no front, and the trade holds nothing.
4. **It reads the roll on each front row.** The roll is VX less VIX, divided by the trading days to settlement, counting the expiry row itself. Dividing turns a gap into a pace: the points a contract must close each day to meet VIX by settlement. Above 0.1 the trade is short both legs, below −0.1 it is long both, and otherwise it holds nothing.
5. **It earns each day on yesterday’s position.** A move of one point is worth \$1,000 on VX and \$50 on ES, which the [VX against E-mini post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains as dollars per point. The day’s return is the dollar profit on yesterday’s positions over yesterday’s gross market value. The gross is the sum of what each position is worth in dollars, counting a short as positive. One basis point of the day’s change in market value, over the same gross, comes off as a cost.
6. **It measures the 448 days after the first 500 from 2008-08-04.** They run from 2010-07-29 to 2012-05-07. The APR is the compounded annual return over 252 trading days, and the Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate, as the [post on the crude oil reversal and momentum rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#the-rule-and-the-file) sets them out. The maximum drawdown is the deepest fall from a previous high, and the longest drawdown is the most days spent below one.

The files are three of Chan’s, each recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md).

1. **`inputDataDaily_VX_20120507.mat`**, saved 2012-05-08. It holds 72 VX contracts, one for each month from January 2007 to December 2012, over 1,543 days from 2006-03-23 to 2012-05-07, and no spot price. The [post on Chan’s VIX calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-calendar-spread-lessons.md#what-changes-from-crude-oil) read the same file.
2. **`VIX.csv`**, saved 2012-05-09. It holds 5,635 closes of the index from 1990-01-02 to 2012-05-08.
3. **`inputDataOHLCDaily_20120507.mat`**, saved 2012-05-09. It holds 53 series. The trade reads its ES, 2,000 rows from 2004-06-02 to 2012-05-08. The VX against E-mini post calls this file the 2012-05-07 save.

The three share all 1,543 of the VX file’s days. 948 of them fall on or after 2008-08-04, and the last 448 are the test. VIX jumps from 11.15 to 18.31 on 2007-02-27, which the repository’s check for a change of scale flags. It is a real move. That day the front contract sits far enough below VIX for the rule to hold long, so the day counts among the front rows below VIX in the 1,016 of 1,369 above. It enters no figure of the trade’s. Each day’s position reads only that day’s VIX, and the test’s first day earns the position held at the close of 2010-07-28, more than three years later.

The order of the run was not the one this repository asks for. A scratch run saw all eight of the script’s figures land before the rule for a landing figure was written down. That rule is the one every replication here uses: a figure lands when the computed value rounds to the printed one at the decimals printed. Nothing in it was chosen to fit. [Entry 41 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-41-vx-against-es-on-vxs-roll-return-chans-algorithmic-trading) records each figure beside the test that computes it.

## Lesson 1: both rules land, and the book’s is the one the script comments out

The script carries two position rules. The lines trading 0.3906 VX contracts per ES contract are commented out. The live lines trade one VX contract per ES contract, written here as [1, 1]. The script’s closing comment prints four figures for each.

```math
\begin{array}{l|r|r|r|r|r}
\text{Figure} & \text{0.3906, computed} & \text{0.3906, comment} & \text{[1, 1], computed} & \text{[1, 1], comment} & \text{Book} \\ \hline
\text{APR} & 0.069065 & 0.069065 & 0.293906 & 0.293906 & 6.9 \text{ percent} \\
\text{Sharpe ratio} & 1.002020 & 1.002020 & 3.263952 & 3.263952 & 1 \\
\text{Maximum drawdown} & -0.075683 & -0.075683 & -0.035798 & -0.035798 & \text{none} \\
\text{Longest drawdown, days} & 259 & 259 & 59 & 59 & \text{none}
\end{array}
```

All eight land at the precision the comments print. The APRs, Sharpe ratios and maximum drawdowns land to six decimals, and the two day counts exactly. The book’s two come from the 0.3906 block. Its APR is 6.906464 percent, which rounds to 6.9, and its Sharpe ratio rounds to 1. Neither rule lands the other’s figures. Each misses the other’s APR by 0.224841 and its Sharpe ratio by 2.261932, so the two blocks cannot be read as one run. The two rules hold the same 224 test days with the same signs. The hedge scales the VX leg and changes nothing else.

So the live lines are not the rule the book describes. The script’s line 75 plots line 74’s cumulative return for whichever rule is live, so the script as shipped draws the [1, 1] curve, while the text quotes the figures of 0.3906. The book’s notes in this repository hold Figure 6.4’s caption and not its curve, so which rule the printed figure shows cannot be read from anything committed here. The figure below draws both. A reader holding the book can match its Figure 6.4 to one of them. The VX against E-mini post met a cousin of this in its [second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run), where the script that ships loads another file and never trades.

![Two charts on one shared date axis from late July 2010 to early May 2012. The top chart redraws Figure 6.4, the cumulative compounded return over the test. A solid black line trades 0.3906 VX contracts per ES contract. It rises to a marked high of 0.049547 on 2010-08-31, drifts between about 0 and 5 percent through mid 2011, dips to a marked trough of −0.029886 on 2011-08-08, climbs to about 8 percent by October 2011 and about 13 percent in December 2011, and ends at 12.61 percent. A dotted line at the August 2010 high is labelled 259 days below this high, to 2011-09-09. A dashed grey line trades one VX contract per ES contract. It climbs to about 24 percent by mid 2011, jumps to about 37 percent in August and September 2011, and ends at 58.10 percent. Tan bands mark the days held short both legs. They cover most of August and September 2010, much of late 2010, scattered days through mid 2011 and most of December 2011 to April 2012. Green bands mark the days held long both legs, mostly late July to late August 2011. The bottom chart plots the signal, the front VX contract less VIX over the trading days to settlement, with dashed lines at plus and minus 0.1. It sits mostly between 0 and 0.25, plunges below −0.1 in the green stretch to a marked low of −0.574194 on 2011-08-08, peaks at a marked 0.311739 on 2012-03-16, and stops 10 days before the end. The title calls the figure exploratory.](../docs/figures/vx_es_roll_return.png)

*The top panel redraws the book’s Figure 6.4, “Cumulative Returns of VX-ES Roll Returns Strategy” (location 2754), under both of the script’s rules. The bottom panel is the signal that sets the position, which the book does not draw. Both panels shade the days held short in tan and the days held long in green.*

The figure is exploratory like every number here. Both curves reach their ends on 2012-04-24, at 12.61 percent for 0.3906 and 58.10 percent for [1, 1], and stay flat for the 9 rows after. The 0.3906 curve’s highest point is 0.129142, on 2011-12-19. Its deepest drawdown of −0.075683 runs from a high on 2010-08-31 to a trough on 2011-08-08, where the curve reads −0.029886. Its longest run below a high, 259 days from 2010-09-01 to 2011-09-09, is the same episode, and the curve makes a new high on 2011-09-12. Under [1, 1] the two drawdown figures are separate episodes. The deepest, −0.035798, runs from a high on 2012-02-06 to 2012-02-15. The longest, 59 days, runs from a high on 2011-09-23 to 2011-12-16.

## Lesson 2: the printed 0.3906 is the specification

The 0.3906 is a fitted number printed to four decimals. The VX against E-mini post’s [first lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-1-three-figures-land-and-the-deviation-misses-by-209) fits it as 0.390594, on the 500 days from 2008-08-04 to 2010-07-28 of VX’s and ES’s continuous closes. Those 500 days are the same 500 days this trade’s calendar holds from 2008-08-04, so the fit and the trade split the sample at the same row.

Trading the fitted 0.390594 in place of 0.3906 gives an APR of 0.069062 and a Sharpe ratio of 1.001978. They miss the script’s 0.069065 and 1.002020 by −0.000003 and −0.000042. The printed 0.3906 lands both, and the script’s commented lines hold it as a literal. So the script traded the rounded number, and a reproduction has to trade it too. In the VX against E-mini post, trading 0.3906 in place of 0.390594 moved nothing that prints at the book’s precision. Here the script prints six decimals, and at six decimals it does.

## Lesson 3: every entry is free, and the last ten days hold nothing

A position earns nothing on the day it opens, since it earns from the next close. What the script skips is the cost of entering. On the day a position opens from flat, meaning the day before held nothing, yesterday’s gross is 0. The day’s return divides by 0, is set to 0, and the entry’s cost is never charged.

That covers every entry in the test. Its held days fall into 32 stretches, 25 short and 7 long, and no position changes sign without a flat day between. So every stretch opens from flat, including the first test day, 2010-07-29, and every one opens free. The script does charge a held day on its mark-to-market move as well as on a trade, because it takes the change in the positions’ market value rather than the change in the positions.

```math
\begin{array}{l|r|r}
\text{The 0.3906 rule} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{As the script runs it} & 0.069065 & 1.002020 \\
\text{Each entry charged one basis point} & 0.067142 & 0.975830 \\
\text{No cost at all} & 0.071248 & 1.030894
\end{array}
```

The middle row sets each of the 32 entry days’ returns to −0.0001, one basis point of the gross just opened. That prints as 6.7 percent against the book’s 6.9, and the Sharpe ratio still rounds to 1. So, at the script’s own one-basis-point rate, the book’s 6.9 percent depends on the free entries. The bottom row charges no cost at all, not even on held days, and gives an APR of 0.071248 and a Sharpe ratio of 1.030894.

The test ends with ten days holding nothing. Eight contracts are priced on 2012-05-07, the file’s last day, so the script reads each as expiring there. VX-2012K, the May 2012 contract, is the front until 2012-04-23, and its days to settlement count to 2012-05-07 rather than to its real expiry. The script’s loop stops one short of the last contract, VX-2012Z, so it reads 71 of the 72. The six between VX-2012K and VX-2012Z get windows holding no row, so 65 of the 71 are ever the front. The [VIX calendar spread post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-calendar-spread-lessons.md#lesson-3-one-reading-of-five-matches-the-book-and-that-is-a-search) met the same false expiry on the same contract. The first of the ten days, 2012-04-24, earns the position held at the 2012-04-23 close less its exit cost: −0.000500 under 0.3906 and 0.005394 under [1, 1]. The other nine earn 0, which the annual figures count. In the figure’s bottom panel those ten days are blank.

## Lesson 4: out of sample for the hedge alone

The book says the test window “was not used for hedge ratio determination” (location 2754). That holds. The fit runs from 2008-08-04 to 2010-07-28, and the test starts the next day. So the window is out of sample for the hedge ratio. Two more facts about the hedge come from the same paragraph and the files.

1. **It fits prices, where the paper fit returns.** Chan says the hedge “is based on the regression fit between the VX versus ES prices”, not “between their returns as in the original paper” (location 2754).
2. **It fits a continuous future, while the trade holds single contracts.** The fit reads VX’s continuous close from that same save, stitched from one contract after another. The trade holds one front contract at a time from the VX file.

The rule has two more choices, and neither carries a statement like the hedge’s.

1. **The 0.1 threshold** is Simon and Campasano’s, by the book’s account. Their sample is not committed here, so whether it overlaps the test window cannot be checked.
2. **The window from 40 to 10 rows** appears nowhere in the text. Its 40-row start decides only the window of VX-2007F, the January 2007 contract, which opens on 2006-11-14, years before the test. Every later contract starts on the row after the previous one ends. Its 10-row end decides which contract the script calls the front. On 228 of the test’s 438 rows with a front, that is the nearest contract the file prices. On the other 210 it is the second-nearest, because the old contract is still priced for the 10 rows after the script moves on.

The bottom panel of the figure shows what the rule reads. Of the 438 rows, 196 sit above 0.1 and 28 below −0.1, and 214 sit between the lines and hold nothing. The longest short stretch runs from 2010-07-29 to 2010-09-20, 37 days, and the longest long one from 2011-07-27 to 2011-08-22, 19 days. The signal’s low is −0.574194 on 2011-08-08 and its high 0.311739 on 2012-03-16.

**So the result stays exploratory.** The hedge was fixed before the test window, but the threshold and the window that picks the front were not shown to be, and the reproduction spends the test on the rule Chan reported.

## Lesson 5: the hedge leaves the trade mostly in the E-mini

The trade is described as collecting VX’s roll return, so the VX leg should carry it. Splitting each day’s return shows how much it does. A day’s return splits into three parts, each over yesterday’s gross. They are the VX leg’s dollar profit, the ES leg’s, and the cost, which comes off. A leg’s share of the gross is what that leg is worth in dollars over the gross.

```math
\begin{array}{l|r|r}
\text{Measure} & \text{0.3906} & \text{[1, 1]} \\ \hline
\text{VX leg's median share of the gross} & 0.119966 & 0.258710 \\
\text{VX leg, summed over the test} & 0.285954 & 0.605959 \\
\text{ES leg, summed over the test} & -0.159336 & -0.138046 \\
\text{Cost, summed over the test, subtracted} & 0.003634 & 0.003961 \\
\text{Daily returns, summed} & 0.122984 & 0.463952
\end{array}
```

The median share is over the 224 test days holding a position, and the sums are of daily returns over the 448 test days, without compounding. Under the book’s 0.3906, the VX leg is a median 0.119966 of the gross, so the trade is mostly a position in ES. The ES leg gives back 0.159336 of the 0.285954 the VX leg earns, more than half. [1, 1] holds 1 / 0.3906 times as many VX contracts per ES contract, about two and a half times. That is where its larger return comes from on this sample.

One day shows the cost of the hedge. Both rules went into 2011-08-08 long both legs, and that day the signal reached its low of −0.574194. ES fell 7.3259 percent and VX-2011U, the front, rose 15.2672 percent. The 0.3906 rule lost 3.9889 percent, its worst day and its deepest drawdown’s trough, while [1, 1] lost 0.3823 percent. With most of the money in ES, the VX leg’s rise could not cover ES’s fall.

The anticorrelation the hedge rests on holds here. On the 224 test days that earn a position, the front contract’s daily return correlates with ES’s at −0.813746. Chan gives “a correlation coefficient of daily returns reaching −75 percent” (location 2754) and names no span, so the two are not a like-for-like comparison.

Nothing here tests why the VX leg is so small. Simon and Campasano fit returns, which would size the legs differently, and nothing here computes that hedge.

**This is a description of one sample, and it is exploratory.** The write-up measured the split after the run. It has no parameter to tune, and it tests no cause.

## What this replication cannot say

Five questions are beyond it.

1. **What a broker would have charged to enter.** The script charges no entry, and the one basis point in Lesson 3 is a guess at a cost, not a measured one.
2. **What a hedge fitted on returns would have earned.** Simon and Campasano fit returns, and nothing here does.
3. **What the script’s entry filter does.** Its commented-out lines 52 to 53 and 60 to 61 form an entry-level filter. It would hold a short only on days the front trades above 21 and a long only on days it trades below 34, once the unconditional lines above them are commented out. It prints no figure, and nothing here runs it.
4. **ES’s own roll return.** The book puts it at about 1 percent a year. No ES contract strip is committed, so nothing here measures it.
5. **Anything after 2012-05-07.** The rule is Simon and Campasano’s, and the hedge and the window are Chan’s. A test of the trade would fix the rule in writing first and run it on later prices.

## What this means for a trader

One habit for each lesson.

1. **Check which lines of a script are live.** A script can print figures for a rule it no longer runs. Match each printed figure to the lines that produce it before trusting either.
2. **Trade the number that was printed when reproducing.** A rounded hedge in a book can be the one the author traded, and the fitted number behind it can miss at the precision the script prints.
3. **Find where a backtest stops charging.** A cost formula can skip every entry and still charge every held day. Count the entries and price them.
4. **Ask what out of sample covers.** A window can be out of sample for one fitted number and not for the rest of the rule. List each choice and say where it came from.
5. **Split the return by leg.** A hedge ratio fixes the money in each leg, and the leg the trade is named for can end up the smaller one. Measure each leg’s share before calling it a trade on that leg.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Figure 6.4, and Kindle locations 2385, 2747 and 2754.
2. `VX_ES_rollreturn.m`, git blob `849e0ac` at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.
3. Simon, D. P., and Campasano, J. (2012), as *Algorithmic Trading* cites them at locations 2385 and 2754. The paper is not in this repository.

*Not investment advice. Code: [the trade](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es_roll_return.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/vx_es_roll_return_figures.py), with the checks behind [the trade’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es_roll_return.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_vx_es_roll_return_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-41-vx-against-es-on-vxs-roll-return-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
