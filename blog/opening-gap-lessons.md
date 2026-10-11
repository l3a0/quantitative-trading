# Chan’s opening gap strategy reproduces on his own file, and the script trades the opposite of what the text describes

*Chan describes a momentum rule on STOXX Europe 50 futures, which buys an upward jump at the open and shorts a downward one, and reports an APR of 13 percent. His script reproduces those figures exactly, but its return line earns the fall from the open on a long. Read with the sign the text describes, the same trades lose 12 percent a year.*

## Why trade the jump at the open

A stop order is an order to buy or sell once the price reaches a set level, and it rests until then. A market that opens far from where it closed can reach many of them at once. Ernest Chan’s *Algorithmic Trading* names “the triggering of stops” as a cause of momentum over short horizons (Chan, 2013, location 2954). After a night or a weekend without trading, “stop orders set at different prices may get triggered all at once at the open”. Filling them moves the price further, and “a cascading effect may trigger stop orders placed further away from the open price as well” (location 2985). If that is right, a price that jumps at the open should keep moving the same way through the day. A move that persists is what momentum means, and the [post on TU momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#why-measure-momentum-before-trading-it) shows Chan measuring it before trading it.

Chan’s Chapter 4 had argued the reverse for stocks. A stock that opens far below the previous day often recovers by the close, because the selling at the open was panic. The [post on buy on gap](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#why-reproduce-a-strategy-that-buys-a-panic) reproduces that strategy. Chapter 7 then turns it around for futures. “The opposite momentum strategy will sometimes work on futures and currencies: buying when the instrument gaps up, and shorting when it gaps down” (location 2965). On “the Dow Jones STOXX 50 index futures (FSTX) trading on Eurex”, Chan reports that the rule “generates an annual percentage rate (APR) of 13 percent and a Sharpe ratio of 1.4 from July 16, 2004, to May 17, 2012”, and points to “the gap momentum code” he published as `gapFutures_FSTX.m`. Later he calls it “a breakout strategy that works for some futures and currencies” (location 3170), meaning one that trades a price leaving its recent range.

This repository transcribed the script line by line and ran it on the file it loads. The results fall into six groups.

1. **The script trades against the jump.** Its return line earns a long’s fall from the open, so it sells an upward jump and buys a downward one, the direction of Chapter 4.
2. **Every printed figure lands on the script as written.** The APR is 0.132733 and the Sharpe ratio 1.441620, the comment’s 0.1327 and 1.44 and the book’s 13 percent and 1.4.
3. **The momentum the text describes loses.** The same trades with the sign the text gives earn an APR of −0.124236 and a Sharpe ratio of −1.441620.
4. **The save and its window both move the last printed digit.** Two earlier saves of the same file miss the comment’s APR, and comparing the three separates the window’s effect from the restated prices’.
5. **The rule is rarely in the market.** It holds a position on 469 of 2,000 days.
6. **The long days earn about three quarters of the return.** Selling an upward jump earns 0.749529 of the summed 1.020809.

**Every result here is exploratory.** Chan chose the instrument, the rule and the dates, and the reproduction runs them on his own file. It can say whether his numbers follow from that file, and nothing about whether either sign would pay after 2012. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the file

**FSTX** is the futures contract on the STOXX Europe 50, an index of fifty large European companies, traded on Eurex. Chan’s book calls the index by its older name, the Dow Jones STOXX 50. A futures contract expires, so years of prices are stitched from one contract after the next into a **continuous future**, and each switch shifts the earlier history. The [post on volatility against the stock index](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains the stitching. Lesson 4 turns on it.

**The rule.** Each day the script compares the open with the previous day’s range, its high and its low. It reads one more number, the standard deviation of the last 90 close-to-close returns, which the [buy on gap post](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#the-strategy-and-the-file) explains. This post calls it the spread.

1. **Long** when the open is at or above the previous high times one plus a tenth of the spread. That is a jump up through the range.
2. **Short** when the open is at or below the previous low times one minus a tenth of the spread.
3. **Flat** on every other day.

Each position is taken at the open and closed at the same day’s close. The spread needs 90 returns, so the first 90 rows, from 2004-07-16 to 2004-11-18, hold nothing. The first position comes on 2004-11-22.

**Two readings of one line.** Line 23 of the script computes each day’s return as `positions.*(op-cl)./op`, the position times the open less the close, over the open. Call that the literal reading. The text describes the other sign, which this post calls the momentum reading. With pₜ the position, Oₜ the open and Cₜ the close:

```math
r_t^{\text{literal}} = p_t \, \frac{O_t - C_t}{O_t}, \qquad r_t^{\text{momentum}} = p_t \, \frac{C_t - O_t}{O_t}
```

The two differ only in sign, day by day. Neither charges a cost. The APR compounds the daily returns over all 2,000 rows and annualises at 252 days a year, and the Sharpe ratio is the mean daily return over its standard deviation, times √252, with no risk-free rate. The [buy on gap post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-1-both-figures-bogm-prints-reproduce-on-chans-own-file) covers both.

**The file** is FSTX’s column of Chan’s `inputDataOHLCDaily_20120517.mat`, saved 2012-05-18 and recorded in the repository’s [data README](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md). One series as one source held it on one date is what this repository calls a vintage. Its open, high, low and close each hold 2,000 days from 2004-07-16 to 2012-05-17, the book’s window exactly. Two earlier saves of the same file, from 2012-05-07 and 2012-05-11, also hold FSTX, and Lesson 4 reads them.

The rules that decide each result are in [Entry 40 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-40-the-opening-gap-strategy-on-stoxx-europe-50-futures-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the script trades against the jump the text says it follows

Take a long day. The open jumped above the previous high, and the rule is long. Under line 23, the day earns the open less the close. If the price falls from 100 at the open to 90 at the close, the long earns 10 percent. On a short day, a rise from 100 to 120 earns the short 20 percent. So a “long” in this script profits when the jump reverses, and a “short” profits when a downward jump recovers.

Held from the open to the close that way, the trade sells an upward jump during the day and buys a downward one. That is fading, trading against a move in the expectation that it reverses. It is the direction of Chapter 4’s buy on gap, run on a future, the strategy location 2965 calls this rule’s opposite. The [buy on gap post’s Lesson 4](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-4-a-mirror-written-down-before-the-run-lands-at-12-percent-not-46) cites this same script for the mirror of buy on gap, a rule that shorts an upward jump. As written, the script’s return line does exactly that.

A script that disagrees with the words around it has happened before in this book. The [cross-sectional momentum post](https://github.com/l3a0/quantitative-trading/blob/main/blog/cross-sectional-momentum-lessons.md#lesson-1-the-040-is-the-comments-not-the-codes) found a script whose printed comment disagreed with its own code. Here the comment and the code agree, and the text is the odd one out.

## Lesson 2: both printed figures land on the script as written

A figure lands when the computed value rounds to the printed one at the decimals printed. The script’s closing comment reads `APR=    0.1327 Sharpe=1.44`.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script comment} & \text{Book} \\ \hline
\text{APR} & 0.132733 & 0.1327 & 13 \text{ percent} \\
\text{Sharpe ratio} & 1.441620 & 1.44 & 1.4 \\
\text{252 times the mean daily return} & 0.128622 & \text{none} & \text{none}
\end{array}
```

Every printed figure lands. Three questions that decided other replications here decide nothing in this one.

1. **Which formula “annualized average return” names.** Location 3509 quotes this strategy as having “an annualized average return of around 13 percent and a Sharpe ratio of 1.4”. The [buy on gap post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-3-one-phrase-names-two-formulas) shows that phrase naming two formulas in this book. Here both round to 13 percent: the compounded APR of 0.132733 and the 252 times the mean daily return of 0.128622.
2. **Which `smartstd` sits behind the spread.** Chan’s two books ship two helpers of that name, and the [buy on gap post’s Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-2-the-helper-behind-the-90-day-standard-deviation-decides-both-printed-figures) found that the wrong one moves both of its figures. Here the first edition’s helper changes the spread and still leaves the rule holding the same position on every one of the 2,000 days, so both figures are unchanged at six decimals.
3. **The order of the run.** A first run saw both readings’ figures before the rule for a landing figure was written down. The rule then fixed is the one every replication here uses, and line 23 has only two signs, both reported, so nothing in it was chosen to fit.

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

![Two charts on one shared date axis from July 2004 to May 2012. The top chart redraws Figure 7.1, the cumulative compounded return of the script as written, as a solid black line, beside the same trades with the sign the text describes as a red line, with a line at zero. A grey band covers the first 90 days, to 2004-11-18, when no spread exists and nothing is held, and both lines sit at zero there. The black line rises to a marked high of 0.573901 on 2008-07-08, falls to a marked trough of 0.274823 on 2008-10-13, stays below that high for 287 days to 2009-08-31, which a dotted line marks, and climbs to end at its highest, 168.90 percent. The red line falls almost steadily, with a brief rise in late 2008, and ends at its lowest, −65.11 percent. The heading sets the script’s APR of 0.132733 and Sharpe ratio of 1.441620 beside the book’s 13 percent and 1.4, and the described sign’s −0.124236 and −1.441620. The bottom chart keeps the script’s returns on the 278 long days only, as a solid black line, and on the 191 short days only, as a dashed grey line, each earning nothing on the other days. The long days’ line climbs to end at its highest, 108.44 percent. The short days’ line rises to about 15 percent by mid 2008, falls to a marked low of −0.038153 on 2009-02-20, and ends at its highest, 29.00 percent. The title calls the figure exploratory.](../docs/figures/opening_gap.png)

*The top panel redraws the script’s `plot(cumret)`, Chan’s Figure 7.1, “Equity Curve of FSTX Opening Gap Strategy” (location 2971), with the sign the text describes beside it. Nothing compares the redraw with the chart the book prints, so it is a redraw of the script’s plot rather than a checked copy. The bottom panel splits the script’s returns by side, which Lesson 6 measures and the book does not draw.*

The figure is exploratory like every number here.

## Lesson 4: the save and its window both decide the printed digit

Chan saved the same file at least three times in May 2012, and each save holds FSTX over a different 2,000 days. The script as written gives a different APR on each.

```math
\begin{array}{l|r|r|r}
\text{Save} & \text{Window} & \text{APR} & \text{Sharpe ratio} \\ \hline
\text{2012-05-07} & \text{2004-07-07 to 2012-05-08} & 0.133561 & 1.466345 \\
\text{2012-05-11} & \text{2004-07-12 to 2012-05-11} & 0.131543 & 1.448082 \\
\text{2012-05-17} & \text{2004-07-16 to 2012-05-17} & 0.132733 & 1.441620
\end{array}
```

All three round to the book’s 13 percent. Only the 2012-05-17 save lands the comment’s 0.1327. Two causes move the APR, and the three saves separate them.

1. **The window alone.** The 2012-05-07 and 2012-05-11 saves price FSTX’s open, high, low and close identically on all 1,997 days they share. Only their windows differ, and the window moves the APR by 0.002018.
2. **The restated prices alone.** The 2012-05-11 and 2012-05-17 saves share 1,996 days, and on all but 45 of them each of the four fields differs, by 25 distinct amounts. FSTX rolled between the two saves, so the later one shifted the earlier history. Held to the shared days, the two runs take a different position on 7 days, and the APR moves from 0.131823 to 0.133016, by 0.001193.

Each move is more than ten times the comment’s last printed digit, 0.0001. So the printed 0.1327 specifies both the save and the window, and neither alone. The [crude oil reversal and momentum post](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#lesson-1-both-figures-land-and-a-save-a-week-later-prints-the-same-to-the-books-precision) found a save a week later moving a figure below the printed digits, and the [volatility post](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#lesson-2-the-save-decides-and-the-script-that-ships-is-not-the-run) found one halving an APR. Here the move lands between the two, inside the book’s rounding and outside the comment’s.

A percentage return divides each day’s move by a price the roll has shifted, which the [crude oil post](https://github.com/l3a0/quantitative-trading/blob/main/blog/crude-oil-reversal-momentum-lessons.md#the-rule-and-the-file) explains. That is why restating the history moves the returns at all.

## Lesson 5: in the market on fewer than a quarter of its days

Of the 2,000 days, the rule is long on 278, short on 191 and flat on 1,531. No day qualifies as both. With the first 90 days set aside, an opening jump of a tenth of a spread outside the previous range happens on about a quarter of the days.

The mean return on a day holding a position is 0.002177. A round trip, in at the open and out at the close, would have to cost 0.002177 of the price to erase it. That is arithmetic on the backtest, not an estimate of what FSTX cost to trade. Nothing here charges a cost.

## Lesson 6: selling the upward jumps earns three quarters of the return

The rule has two branches, a long after an upward jump and a short after a downward one, and the book prints only their total. Splitting the literal reading’s returns by the branch that held them gives two curves, which the figure’s bottom panel draws. Each earns its own returns on its own days and nothing on the others.

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

The last two rows are FSTX’s own move, with no position attached. After an upward jump, FSTX fell from the open on average, and closed below the open on 163 of the 278 days. After a downward jump, it rose on average, and closed above the open on 108 of the 191. On the 1,441 days that carry a spread and hold nothing, its mean move from the open is 0.000025. So on this file the jumps tended to reverse during the day, and the upward ones more strongly. That is what the literal reading collects and the momentum reading pays.

**This is a description of one sample, and it is exploratory.** The split comes from the rule’s own two branches, not from a date chosen after the curve was seen, so it has no parameter to tune. It was still chosen after the run, and it tests nothing. A split by year was measured and is left out for that reason. Nothing here says upward jumps will keep reversing, or why they did.

## What this replication cannot say

Seven questions are beyond it.

1. **Which sign Chan meant.** His text describes momentum, and his script and its comment trade the fade. The reproduction shows which sign earns the printed figures, not which one he intended.
2. **What Chan’s Python port prints.** A second transcription, in Python, exists, and this replication does not read it.
3. **Whether the rule works on GBPUSD.** Location 2971 reports “an APR of 7.2 percent and a Sharpe ratio of 1.3” on the British pound against the dollar, with the open at 5 a.m. and the close at 5 p.m., Eastern time. No such series is committed here, and neither is the code that ran it.
4. **What the VIX filter does, and under which sign.** Location 3509 reports that on days after the VIX, the market’s implied volatility index, closed over 35, the strategy’s annualized average return drops to “2.6 percent” and its Sharpe ratio to “0.16”. That filter is not run here, and the 13 percent it starts from belongs to the literal sign.
5. **How far the roll’s restatements move the returns.** The continuous future’s early prices are shifted by every later roll, and nothing committed holds the prices that traded.
6. **What costs and timing would take.** Nothing is charged, and a trader cannot be filled at an open price that is known only once it prints. The [buy on gap post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/buy-on-gap-lessons.md#lesson-6-an-exact-reproduction-checks-the-arithmetic-not-the-edge) covers that cost for the same kind of trade.
7. **Whether either sign works after 2012.** The rule, the save and the window are Chan’s. A test of it would fix one sign in writing first and run it on later prices.

## What this means for a trader

One habit for each lesson.

1. **Read the return line, not the name of the strategy.** One sign in one line decides whether a rule follows a move or fades it, and the words around it can say the opposite.
2. **Reproduce the printed figures before arguing with the text.** Here they land exactly, which is what shows the text and the script disagree.
3. **Run the sign the text describes too.** A script that matches its printed figures can still contradict the claim those figures were printed to support.
4. **Record the save and the window with the result.** On a continuous future both move the last printed digit, so a figure without them cannot be checked.
5. **Count the days a rule is in the market.** A strategy holding a position on fewer than a quarter of its days earns its APR from few trades, and each one carries a cost the backtest leaves out.
6. **Split the return by the rule’s own branches.** If one branch earns most of it, find what that branch is betting on. Here it is upward jumps reversing.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 7.1, Figure 7.1, and Kindle locations 2954, 2965, 2971, 2985, 3170 and 3509.
2. `gapFutures_FSTX.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [the strategy](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/opening_gap.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/opening_gap_figures.py), with the checks behind [the strategy’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_opening_gap.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_opening_gap_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-40-the-opening-gap-strategy-on-stoxx-europe-50-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
