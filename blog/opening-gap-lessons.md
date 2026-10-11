# Chan’s opening gap strategy reproduces on his own file, and the script trades the opposite of what the text describes

*Chan describes a momentum rule on STOXX Europe 50 futures, which buys an upward jump at the open and shorts a downward one, and reports an APR of 13 percent. His script reproduces those figures exactly, but its return line pays a long when the price falls from the open. Read with the sign the text describes, the same trades lose 12 percent a year.*

## Why trade the jump at the open

A stop order is an order to buy or sell once the price reaches a set level, and it rests until then. A market that opens far from where it closed can reach many of them at once. Ernest Chan’s *Algorithmic Trading* names “the triggering of stops” as a cause of momentum over short horizons (Chan, 2013, location 2954). After a night or a weekend without trading, “stop orders set at different prices may get triggered all at once at the open”. Filling them moves the price further, and “a cascading effect may trigger stop orders placed further away from the open price as well” (location 2985). If that is right, a price that jumps at the open should keep moving the same way through the day. A move that persists is what momentum means, and the [post on TU momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#why-measure-momentum-before-trading-it) shows Chan measuring it before trading it.

Chan’s Chapter 4 had argued the reverse for stocks. A stock that opens far below the previous day often recovers by the close, because the selling at the open was panic. The [post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#why-reproduce-a-strategy-that-buys-a-panic) reproduces that strategy. Chapter 7 then turns it around for futures. “The opposite momentum strategy will sometimes work on futures and currencies: buying when the instrument gaps up, and shorting when it gaps down” (location 2965). On “the Dow Jones STOXX 50 index futures (FSTX) trading on Eurex”, Chan reports that the rule “generates an annual percentage rate (APR) of 13 percent and a Sharpe ratio of 1.4 from July 16, 2004, to May 17, 2012”, and points to “the gap momentum code” he published as `gapFutures_FSTX.m`. Later he calls it “a breakout strategy that works for some futures and currencies” (location 3170), meaning one that trades a price leaving its recent range.

This repository transcribed the script line by line and ran it on the file it loads. The results fall into six groups.

1. **The script trades against the jump.** Its return line pays a long when the price falls from the open, so it sells an upward jump and buys a downward one, the direction of Chapter 4. Chan’s later Python port takes the text’s sign, and a flipped test has it sell every upward jump all the same.
2. **Every printed figure lands on the script as written.** A figure lands when the computed value rounds to the printed one at the decimals printed, and misses when it does not. The APR is 0.132733 and the Sharpe ratio 1.441620, which land on the 0.1327 and 1.44 in the script’s closing comment and on the book’s 13 percent and 1.4.
3. **The momentum the text describes loses.** The same trades with the sign the text gives earn an APR of −0.124236 and a Sharpe ratio of −1.441620.
4. **The save and its window both move the last printed digit.** Chan saved this file under several dates, and the two earlier saves that hold FSTX miss the comment’s APR. Comparing the three separates the window’s effect from that of the earlier prices each later save rewrote.
5. **The rule is rarely in the market.** It holds a position on 469 of 2,000 days.
6. **The long days earn about three quarters of the return.** Selling an upward jump earns 0.749529 of the summed 1.020809.

**Every result here is exploratory.** Chan chose the instrument, the rule and the dates, and the reproduction runs them on his own file. It can say whether his numbers follow from that file, and nothing about whether either sign would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

**FSTX** is the futures contract on the STOXX Europe 50, an index of fifty large European companies, traded on Eurex. Chan’s book calls the index by its older name, the Dow Jones STOXX 50. A futures contract expires, so years of prices are stitched from one contract after the next into a **continuous future**. Each switch to the next contract is a roll, and each roll shifts the earlier history. The [post on volatility against the stock index](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains the stitching. Lesson 4 turns on it.

**The rule.** Each day the script compares the open with the previous day’s range, its high and its low. It reads one more number, the standard deviation of the last 90 close-to-close returns, which the [buy on gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#the-strategy-and-the-file) explains.

1. **Long** when the open is at or above the previous high times one plus a tenth of the standard deviation. That is a jump up through the range.
2. **Short** when the open is at or below the previous low times one minus a tenth of the standard deviation.
3. **Flat** on every other day.

Each position is taken at the open and closed at the same day’s close. The standard deviation needs 90 returns, so the first 90 rows, from 2004-07-16 to 2004-11-18, hold nothing. The first position comes on 2004-11-22.

**Two readings of one line.** Line 23 of the script computes each day’s return as `positions.*(op-cl)./op`, the position times the open less the close, over the open. Call that the literal reading. The text describes the other sign, which this post calls the momentum reading. With pₜ the position, Oₜ the open and Cₜ the close:

```math
r_t^{\text{literal}} = p_t \, \frac{O_t - C_t}{O_t}, \qquad r_t^{\text{momentum}} = p_t \, \frac{C_t - O_t}{O_t}
```

The two differ only in sign, day by day. Neither charges a cost. The APR compounds the daily returns over all 2,000 rows and annualises at 252 days a year, and the Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate. The [buy on gap post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-1-both-figures-bogm-prints-reproduce-on-chans-own-file) covers both.

**The file** is FSTX’s column of Chan’s `inputDataOHLCDaily_20120517.mat`, saved 2012-05-18 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). Its open, high, low and close each hold 2,000 days from 2004-07-16 to 2012-05-17, the book’s window exactly. Chan saved dated versions of this file on other days in May 2012, and this post calls each one a save and names it by the date in its file name. Two earlier saves, `inputDataOHLCDaily_20120507.mat` and `inputDataOHLCDaily_20120511.mat`, also hold FSTX, and Lesson 4 reads them.

The rules that decide each result are in [Entry 40 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-40-the-opening-gap-strategy-on-stoxx-europe-50-futures-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the script trades against the jump the text says it follows

Take a long day. The open jumped above the previous high, and the rule is long. Under line 23, the day earns the open less the close. If the price falls from 100 at the open to 90 at the close, the long earns 10 percent. On a short day, a rise from 100 to 120 earns the short 20 percent. So a “long” in this script profits when the jump reverses, and a “short” profits when a downward jump recovers.

Held from the open to the close that way, the trade sells an upward jump during the day and buys a downward one. That is fading, trading against a move in the expectation that it reverses. It is the direction of Chapter 4’s buy on gap, run on a future, the strategy that location 2965 calls this rule’s opposite. The [buy on gap post’s Lesson 4](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-4-a-mirror-written-down-before-the-run-lands-at-12-percent-not-46) cites this same script for the mirror of buy on gap, a rule that shorts an upward jump. As written, the script’s return line does exactly that.

A script in this book has disagreed with the words around it before. The [cross-sectional momentum post](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md#lesson-1-the-040-is-the-comments-not-the-codes) found a script whose printed comment disagreed with its own code. Here the comment and the code agree, and the text is the odd one out.

Chan’s later Python port of the script, `gapFutures_FSTX.py`, takes the sign the text describes, and it still sells the upward jump. It flips the script’s short test, from an open at or below the previous low to one at or above it. Any open that clears the previous high also clears the previous low, and the port assigns the short after the long, so it never holds a long. It is short on 1,718 of the 2,000 days, every one of the 278 upward jumps among them. A short under the momentum sign earns exactly what the script’s long earns under its own, so on those 278 days the port’s returns are the script’s, day for day. They sum to 0.749529, and the port’s other 1,440 short days sum to −0.050957. So the port’s gain comes from selling the upward jump too. Two smaller changes sit beside that. Its 90-day standard deviation divides by n − 1 and is first set one row later, and its Sharpe ratio divides by n rather than n − 1. All four figures its comments print land on the committed file, among them an APR of 0.074864 and a Sharpe ratio of 0.494857.

## Lesson 2: both printed figures land on the script as written

The script’s closing comment reads `APR=    0.1327 Sharpe=1.44`.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script comment} & \text{Book} \\ \hline
\text{APR} & 0.132733 & 0.1327 & 13 \text{ percent} \\
\text{Sharpe ratio} & 1.441620 & 1.44 & 1.4 \\
\text{252 times the mean daily return} & 0.128622 & \text{none} & \text{none}
\end{array}
```

Three questions that decided other replications here decide nothing in this one.

1. **Which formula “annualized average return” names.** Location 3509 quotes this strategy as having “an annualized average return of around 13 percent and a Sharpe ratio of 1.4”. The [buy on gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) shows that phrase naming two formulas in this book. Here both round to 13 percent: the compounded APR of 0.132733 and the 252 times the mean daily return of 0.128622.
2. **Which `smartstd` sits behind the standard deviation.** Chan’s two books ship two helpers of that name, and the [buy on gap post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-2-the-helper-behind-the-90-day-standard-deviation-decides-both-printed-figures) found that the wrong one moves both of its figures. Here the first edition’s helper changes the standard deviation and still leaves the rule holding the same position on every one of the 2,000 days, so both figures are unchanged at six decimals.
3. **The order of the run.** The replication ran both readings and saw their figures before it wrote down when a figure lands. The rule it then wrote down is the one every replication here uses, and line 23 has only two signs, both reported, so nothing in it was chosen to fit.

## Lesson 3: the momentum the book describes loses what the script earns

The momentum reading’s daily returns are the literal reading’s negated, so its Sharpe ratio is the same number with the sign flipped. Its APR is not, because compounding treats gains and losses unequally.

```math
\begin{array}{l|r|r}
\text{Figure} & \text{Literal, as written} & \text{Momentum, as described} \\ \hline
\text{APR} & 0.132733 & -0.124236 \\
\text{Sharpe ratio} & 1.441620 & -1.441620 \\
\text{Cumulative return at the end} & 1.688951 & -0.651056 \\
\text{Maximum drawdown} & -0.190023 & -0.651056 \\
\text{Longest drawdown, days} & 287 & 1{,}909
\end{array}
```

The maximum drawdown is the deepest fall from a previous high, and the longest drawdown is the most days spent below one. The momentum reading’s longest drawdown is every day from its first trade, and its deepest is where it ends.

Neither curve ever crosses its starting capital after the first trade. On 2004-11-22, the first day holding a position, the literal reading gains 0.002878 and the momentum reading loses the same. Over the 1,909 days from then, the literal curve never falls below that first gain, and the momentum curve never climbs above that first loss. So the figures the text prints in support of momentum are not figures momentum earns on the file they came from.

![Two charts on one shared date axis from July 2004 to May 2012. The top chart redraws Figure 7.1, the cumulative compounded return of the script as written, as a solid black line, beside the same trades with the sign the text describes as a red line, with a line at zero. A grey band covers the first 90 days, to 2004-11-18, when no standard deviation exists and nothing is held, and both lines sit at zero there. The black line rises to a marked high of 0.573901 on 2008-07-08, falls to a marked trough of 0.274823 on 2008-10-13, stays below that high for 287 days to 2009-08-31, which a dotted line marks, and climbs to end at its highest, 168.90 percent. The red line falls almost steadily, with a brief rise in late 2008, and ends at its lowest, −65.11 percent. The heading sets the script’s APR of 0.132733 and Sharpe ratio of 1.441620 beside the book’s 13 percent and 1.4, and the described sign’s −0.124236 and −1.441620. The bottom chart keeps the script’s returns on the 278 long days only, as a solid black line, and on the 191 short days only, as a dashed grey line, each earning nothing on the other days. The long days’ line climbs to end at its highest, 108.44 percent. The short days’ line rises to a high of about 18 percent in July 2008, falls to a marked low of −0.038153 on 2009-02-20, and ends at its highest, 29.00 percent. The title calls the figure exploratory.](../docs/figures/opening_gap.png)

*The top panel redraws the script’s `plot(cumret)`, Chan’s Figure 7.1, “Equity Curve of FSTX Opening Gap Strategy” (location 2971), with the sign the text describes beside it. Nothing compares the redraw with the chart the book prints, so it is a redraw of the script’s plot rather than a checked copy. The bottom panel splits the script’s returns by side, which Lesson 6 measures and the book does not draw.*

The figure is exploratory like every number here.

## Lesson 4: the save and its window both decide the printed digit

Chan saved at least three dated versions of this file in May 2012, and each save holds FSTX over a different 2,000 days. The script as written gives a different APR on each.

```math
\begin{array}{l|r|r|r}
\text{Save} & \text{Window} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{2012-05-07} & \text{2004-07-07 to 2012-05-08} & 0.133561 & 1.466345 \\
\text{2012-05-11} & \text{2004-07-12 to 2012-05-11} & 0.131543 & 1.448082 \\
\text{2012-05-17} & \text{2004-07-16 to 2012-05-17} & 0.132733 & 1.441620
\end{array}
```

All three round to the book’s 13 percent. Only the 2012-05-17 save lands the comment’s 0.1327. Two causes move the APR, and the three saves separate them.

1. **The window alone.** The 2012-05-07 and 2012-05-11 saves price FSTX’s open, high, low and close identically on all 1,997 days they share. Only their windows differ, and the window moves the APR by 0.002017.
2. **The restated prices alone.** The 2012-05-11 and 2012-05-17 saves share 1,996 days, and on all but 45 of them each of the four fields differs, by 24 distinct amounts. Nothing committed records why the prices moved, though a roll between the two saves would shift the history this way. To hold the window fixed, the replication runs the 2012-05-11 save from 2004-07-16, the later save’s first day, so both standard deviations start on the same rows. Over the shared days the two runs then take a different position on 6 days, and the APR moves from 0.130360 to 0.133016, by 0.002655.

Each move is more than ten times the comment’s last printed digit, 0.0001. So the printed 0.1327 specifies both the save and the window, and neither alone. The [crude oil reversal and momentum post](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#lesson-1-both-figures-land-and-a-save-a-week-later-prints-the-same-to-the-books-precision) found a save a week later moving a figure below the printed digits, and the [volatility post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run) found one halving an APR. Here the move falls between the two, inside the book’s rounding and outside the comment’s.

A percentage return divides each day’s move by a price the roll has shifted, which the [crude oil post](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#the-rule-and-the-file) explains. That is why restating the history moves the returns at all.

## Lesson 5: in the market on fewer than a quarter of its days

Of the 2,000 days, the rule is long on 278, short on 191 and flat on 1,531. No day qualifies as both. With the first 90 days set aside, an opening jump of a tenth of a standard deviation outside the previous range happens on about a quarter of the days.

The mean return on a day holding a position is 0.002177. A round trip, in at the open and out at the close, would have to cost 0.002177 of the price to erase it. That is arithmetic on the backtest, not an estimate of what FSTX cost to trade. Nothing here charges a cost.

## Lesson 6: selling the upward jumps earns about three quarters of the return

The rule has two branches, a long after an upward jump and a short after a downward one, and the book prints only their total. Under the literal reading the long sells the upward jump and the short buys the downward one, as Lesson 1 showed. Splitting the literal reading’s returns by the branch that held them gives two curves, which the figure’s bottom panel draws. Each earns its own returns on its own days and nothing on the others.

```math
\begin{array}{l|r|r}
\text{On the days held} & \text{Long} & \text{Short} \\ \hline
\text{Days} & 278 & 191 \\
\text{Daily returns, summed} & 0.749529 & 0.271280 \\
\text{Compounded} & 1.084422 & 0.290022 \\
\text{APR, holding nothing on other days} & 0.096964 & 0.032607 \\
\text{Sharpe ratio, the same} & 1.534735 & 0.527473 \\
\text{Mean move of FSTX from the open} & -0.002696 & 0.001420 \\
\text{Days the close went against the jump} & 163 & 108
\end{array}
```

The daily returns sum to 1.020809 over the whole window, and the long days hold 0.749529 of it, about three quarters. The two sides hold on different days, so one plus each side’s compounded return, multiplied, gives one plus the whole curve’s 1.688951.

The last two rows are FSTX’s own move, with no position attached. After an upward jump, FSTX fell from the open on average, and closed below the open on 163 of the 278 days. After a downward jump, it rose on average, and closed above the open on 108 of the 191. On the 1,441 flat days after the first 90, its mean move from the open is 0.000025. So on this file the jumps tended to reverse during the day, and the upward ones more strongly. That is what the literal reading collects and the momentum reading pays.

**This is a description of one sample, and it is exploratory.** The split comes from the rule’s own two branches, not from a date chosen after the curve was seen, so it has no parameter to tune. It was still chosen after the run, and it tests nothing. The replication also measured a split by year, and this post leaves it out for that reason. Nothing here says upward jumps will keep reversing, or why they did.

## What this replication cannot say

Six questions are beyond it.

1. **Which sign Chan meant.** His text describes momentum, his script trades the fade, and its comment prints the fade’s figures. His Python port takes the text’s sign and still sells the upward jump, so it does not settle the question either. The reproduction shows which sign earns the printed figures, not which one he intended.
2. **Whether the rule works on GBPUSD.** Location 2971 reports “an APR of 7.2 percent and a Sharpe ratio of 1.3” on the British pound against the dollar, with the open at 5 a.m. and the close at 5 p.m., Eastern time. No such series is committed here, and neither is the code that ran it.
3. **What the VIX filter does, and under which sign.** Location 3509 reports that on a day when the preceding day’s VIX, the market’s implied volatility index, is over 35, the strategy’s annualized average return drops to “2.6 percent” and its Sharpe ratio to “0.16”. That filter is not run here, and the 13 percent it starts from belongs to the literal sign. The [post on the VIX filter](https://github.com/l3a0/quantitative-trading/blob/main/blog/vix-filter-lessons.md#lesson-2-fstxs-figures-belong-to-the-scripts-fading-sign) runs it. Both filtered figures land under the literal sign too, on a way of joining VIX’s calendar to FSTX’s that was chosen after the figures were seen. The momentum sign gives them negated, and a test cannot tell the kept days from the rest.
4. **How far the roll’s restatements move the returns.** Every later roll shifts the continuous future’s early prices, and nothing committed holds the prices that traded.
5. **What costs and timing would take.** Nothing is charged, and a trader cannot be filled at an open price that is known only once it prints. The [buy on gap post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-6-an-exact-reproduction-checks-the-arithmetic-not-the-edge) covers that cost for the same kind of trade.
6. **Whether either sign works after 2012.** The rule, the save and the window are Chan’s. A test of it would fix one sign in writing first and run it on later prices.

## What this means for a trader

One habit for each lesson.

1. **Read the return line, not the name of the strategy.** One sign in one line decides whether a rule follows a move or fades it, and the words around it can say the opposite.
2. **Reproduce the printed figures before arguing with the text.** Here they land, which is what shows the text and the script disagree.
3. **Run the sign the text describes too.** A script that matches its printed figures can still contradict the claim those figures were printed to support.
4. **Record the save and the window with the result.** On a continuous future both move the last printed digit, so a figure without them cannot be checked.
5. **Count the days a rule is in the market.** A strategy holding a position on fewer than a quarter of its days earns its APR from few trades, and each one carries a cost the backtest leaves out.
6. **Split the return by the rule’s own branches.** If one branch earns most of it, find what that branch is betting on. Here it is upward jumps reversing.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 7.1, Figure 7.1, and Kindle locations 2954, 2965, 2971, 2985, 3170 and 3509.
2. `gapFutures_FSTX.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/opening_gap.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/opening_gap_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_opening_gap.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_opening_gap_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-40-the-opening-gap-strategy-on-stoxx-europe-50-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
