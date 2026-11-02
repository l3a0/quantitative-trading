# On Chan’s window, trading TU on its roll return beats his momentum rule by stepping out of the market, and misses all three of his figures

*Chan reports that trading the two-year Treasury note future on its roll return beats his momentum rule. On one rebuilt series it does, by sitting out days that earned about nothing while the momentum rule stays in. None of the three figures reproduces.*

## Why trade the roll return instead of the past return

A trend-following rule on futures has a puzzle behind it. Why should a future’s past return say anything about its next one? Ernest Chan’s second book, *Algorithmic Trading*, offers an answer and then tests it.

The test starts from Example 6.1, a momentum strategy on TU, the two-year Treasury note future. Each day it buys if TU’s price is above its level 250 trading days earlier and sells if it is below, and it holds each of those bets for 25 days. Chan reports that from 2004-06-01 to 2012-05-11 “the Sharpe ratio is a respectable 1”, with an APR of 1.7 percent and a maximum drawdown of 2.5 percent (Chan, 2013, Kindle edition, pp. 204 to 205). The APR is the compounded annual return. The Sharpe ratio divides the average daily return by its standard deviation and scales it to a year, so it measures return per unit of risk. The maximum drawdown is the largest fall from a peak.

Then comes the explanation. A future’s total return is the move of its spot price plus a roll return. The spot price is the price of the thing the future is written on. The roll return is what the future earns by converging on the spot price as it nears expiry. Chan argues that the roll return is what makes futures trend: “Typically, the sign of roll returns does not vary very often” (Chan, 2013, p. 206). The spot return swings in both directions from day to day. So if the roll return keeps its sign for months and makes up most of the average return, a long holding period sees a total return that keeps its sign too.

If that is the cause, the roll return itself should be a better signal than the past total return. Chan says so on p. 206, calling it “a cleaner and potentially better momentum signal”, and tries it on TU. The rule goes long when the lagged roll return is above 3 percent a year, short when it is below −3 percent, and flat otherwise. The book does not say how far the roll return is lagged, and the rule tested here uses the previous day’s value. It also compares the 3 percent with the roll return as Chan’s script computes it, which for TU is three times the yearly rate, as the section on the rule and the files explains. Chan reports “a higher APR of 2.5 percent and Sharpe ratio of 2.1 from January 2, 2009, to August 13, 2012, with a reduced maximum drawdown of 1.1 percent” (Chan, 2013, p. 206).

### What the reproduction found

No script ships for the experiment on p. 206, so this repository wrote the rule down itself and ran it on Chan’s own files. The rule misses all three printed figures.

It does beat Example 6.1 on all three when the two rules run on one series over one window. That series had to be rebuilt, because no file this repository keeps follows TU’s front contract, the one nearest expiry, to the end of the window. Chan’s continuous close, a front-contract series he saved in May 2012, shows the same win on the days it covers.

The Sharpe ratio carries most of the win. The margin between the two rules’ APRs is small enough that swapping Chan’s close for the rebuilt series moves it by about a quarter, and a threshold of 2.9 or 3.2 percent instead of the book’s 3 turns it negative. At 2.8 percent the rule here loses on all three, though at 2.7 and 2.9 percent it still wins on the Sharpe ratio.

**Every result here is exploratory.** This repository wrote the rule down after trying about 90 variants on the same data, so the run cannot count as a test of whether the roll-return signal works. It can say what the book’s sentence gives on Chan’s files under one stated reading, and nothing about the trade today.

The four lessons below say what the run does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

A futures contract is a promise to buy or sell something on a set date, and each delivery month trades as its own contract. The [post on calendar spreads](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#the-claim-and-the-files) explains futures contracts. When later contracts trade above nearer ones, the market is in contango, and a long position loses as its contract’s price sinks toward the spot. When later contracts trade below nearer ones, the market is in backwardation, and a long position gains as its price rises toward the spot. That gain or loss is the roll return.

### The roll return γ

Chan estimates the roll return, which he writes γ, in Example 5.3, by regressing “the prices of the various contracts against their time to maturity” on a fixed day (Chan, 2013, p. 179). His script, `estimateFuturesReturns.m`, does it on each day with the log prices of the five nearest contracts against their place in line, 1 to 5. Then γ is −12 times the slope, meant as an annual rate. A positive γ means the later contracts are cheaper, which is backwardation and pays a long position. The [post on Chan’s spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#the-model-and-the-files) reproduces this fit on TU and four other futures.

The −12 assumes adjacent contracts are a month apart, so the script counts each step from one contract’s column of Chan’s file to the next as one month. This post calls the result γ in column units. TU’s contracts are a quarter apart, so each step is really three months. On all 1,087 days where γ is defined, γ in column units is exactly three times γ measured in months, which counts each step as the three months it really is. Only γ in months is TU’s roll return a year, the rate the book’s words describe. The roll returns post’s [second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/roll-returns-lessons.md#lesson-2-the-script-counts-contracts-not-months) shows what the one-month assumption does to a future whose contracts are not a month apart.

Chan gives the threshold on p. 206 in annualized terms, so γ in months might look like the signal to use. But γ in months peaks at 2.447 percent inside the test window and never reaches 3 percent, so a rule on it never trades. The rule here therefore reads γ in column units. Its 3 percent threshold then means a roll return of 1 percent a year on TU. That is a reading of the book, and the post says so wherever it matters.

### Example 6.1’s rule

Example 6.1 trades in 25 tranches. A tranche is one twenty-fifth of the capital, opened on one day and held for 25. Each day opens a long tranche if the price is above its level 250 trading days back, or a short one if it is below, and the oldest tranche closes. So the position runs from 25 tranches short to 25 long, and each day’s return is the position’s profit divided by 25. The [post on Example 6.1](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#the-strategy-and-the-file) explains the strategy and reproduces its figures on Chan’s file.

### The declared rule

With no script to transcribe, this repository wrote the rule down in five parts and calls it the declared rule. It was written down before this experiment’s code was built, but after two trial runs had tried about 90 variants, which Lesson 4 describes.

1. **The signal.** γ in column units, from Chan’s Example 5.3 fit.
2. **The threshold.** Long where γ is strictly above 0.03 and short where it is strictly below −0.03. A day with no γ is neither long nor short.
3. **The lag.** The position set on one day earns the next day’s return, which is Example 6.1’s own convention.
4. **The window.** Every series is computed on the full file first and only then trimmed to 2009-01-02 to 2012-08-13, the 913 trading days of the window Chan names on p. 206. Trimming first would leave Example 6.1’s 250-day signal with no value for the window’s first 250 trading days. Its signal would then exist on only 663 of the 913, and its APR, written as a fraction, would fall from 0.013377 to 0.008435.
5. **The arithmetic.** Example 6.1’s script, `TU_mom.m`, for the APR, the Sharpe ratio and the drawdown, with 252 trading days a year, no risk-free rate and no cost.

### The TU strip and the front-contract series

The data is a strip, Chan’s own MATLAB file holding every contract of one future and its spot price, converted here to one file per contract. This strip holds 93 TU contracts over 5,565 days, from 1990-06-22 to 2012-08-13, and TU’s spot price from 1995-08-10. It was saved on 2012-08-14 and is the only TU file in the [repository’s data](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) that reaches the end of the book’s window.

Example 6.1 trades a continuous series of TU. It follows the front contract, the one nearest expiry, and switches to the next contract shortly before each expires. The switch is called a roll, which is a different thing from the roll return. Chan’s own copies of that series end in May 2012, three months short of the window’s end. So the position here earns on a front-contract series rebuilt from the strip, which Lesson 3 describes. Example 6.1’s rule runs on the same rebuilt series, so the two rules are compared on one set of prices, days and arithmetic.

## Lesson 1: the declared rule misses all three printed figures

Here are the three figures beside the book’s. A gap is the computed figure minus the printed one, at the book’s precision. The drawdown column shows its size, as the book prints it.

```math
\small\begin{array}{l|r|r|r}
 & \text{APR} & \text{Sharpe} & \text{Drawdown} \\ \hline
\text{Computed} & 1.3725\% & 1.803348 & 0.7299\% \\
\text{Book} & 2.5\% & 2.1 & 1.1\% \\
\text{Gap} & -1.1 & -0.3 & -0.4
\end{array}
```

All three miss. The APR and the Sharpe ratio land below the book, and the drawdown is shallower than the book’s.

### Where the miss could come from

A different download of the prices is the first thing to suspect, because vendors restate history. It does not explain the miss on the days a saved copy covers. Chan’s continuous TU close, the copy Example 6.1’s script loads, follows the front contract. It ends on 2012-05-11, was saved the next day, and covers 849 of the window’s 913 trading days. On those days, the declared rule earning that close gives an APR of 1.4373 percent, a Sharpe ratio of 1.791969 and a drawdown of 0.8077 percent. The rebuilt series gives 1.4682 percent, 1.870808 and 0.7299 percent on the same days. Both sit far from the book. The 64 window days the close does not cover would have to earn about 4.2 percent between them to lift the APR to the book’s 2.5 percent. On the rebuild they earn 0.03 percent.

A miss cannot say whether Chan computed a different number or read his own sentence differently. The sentence leaves the lag, the series the position earns and the unit of γ open, and each choice is part of the method. Lesson 4 shows one variant that matches two of the three figures, and why it is not the one tested.

### How the declared rule trades the window

In this window the rule is long on 572 of the 913 days, 62.65 percent, and flat on the other 341. Because γ never falls below −3 percent, the rule is never short. It changes position 21 times. It opens the window flat, because the position that earns the window’s first day is set by γ on 2008-12-31, which is 1.61 percent, under the threshold. On the window’s first three days, the five nearest contracts close at the same price, so the fit’s slope and γ are zero to within 10⁻¹³.

Those three days fall inside a longer pattern that began before the window. On 185 of the 187 window days from 2009-01-02 to 2009-09-29, the third, fourth and fifth nearest contracts close at one price, and that shared price changes from day to day. A fit whose three farthest prices are equal finds no roll among those contracts. The position on 169 of the 341 flat days was set on a γ fitted on a day whose three farthest prices were equal. The first of those positions was set on 2008-12-31, the day before the window. The strip cannot say whether the exchange or the data vendor priced those contracts that way.

The figure below draws both rules on the rebuilt series. The book prints no chart for this experiment, so the figure is this repository’s own.

![Two charts sharing a date axis from January 2009 to August 2012, with the same days shaded grey in both. The top chart is the compounded cumulative return of two rules on TU, in percent, before costs. The brown line, Example 6.1’s rule, wanders around zero through mid-2009, climbs to about 3.9 percent by late 2010, dips, rises to about 5 percent by late 2011 and ends at 4.9 percent. The green line, the declared rule, is flat at zero for the first months, flat again through each shaded stretch, and otherwise moves with the brown line. It ends just above it, at 5.1 percent. Its heading sets the declared rule’s APR of 0.013725 and Sharpe ratio of 1.803348 beside the book’s 2.5 percent and 2.1, gives Example 6.1’s rule 0.013377 and 1.196742, and says Example 6.1’s rule holds all 25 tranches long on every window day, so its line is holding TU. The bottom chart is the roll return γ in column units, a step-like line between about 0 and 7.3 percent, with dashed lines at 3 and −3 percent. The shaded stretches follow γ’s spells below 3 percent, one day late, and γ never comes near −3 percent. Its heading says γ peaks at 0.073403 on 2009-10-12 and the rule is long on 572 trading days, short on none and flat on the 341 shaded ones. The title calls the figure exploratory, and the note names Chan’s TU strip, saved 2012-08-14, the front contract rebuilt from it, and the rule declared after about 90 scratch readings.](../docs/figures/roll_momentum.png)

*Above, the compounded cumulative return of both rules on the rebuilt front contract, with the days the declared rule sits flat shaded. Below, the roll return γ in column units against the 3 percent thresholds.*

## Lesson 2: the declared rule beats Example 6.1 by stepping out of the market

The comparison on p. 206 makes three claims against Example 6.1.

1. A higher APR.
2. A higher Sharpe ratio.
3. A smaller drawdown.

A claim holds when the declared rule beats Example 6.1’s rule on the same series and days. Here are the two rules side by side. Unlike the table in Lesson 1, this one writes the APR and the drawdown as fractions, so 0.013725 is the 1.3725 percent above. It also signs the drawdowns, so the larger number is the smaller fall.

```math
\small\begin{array}{l|r|r|r}
 & \text{APR} & \text{Sharpe} & \text{Drawdown} \\ \hline
\text{Declared} & 0.013725 & 1.803348 & -0.007299 \\
\text{Example 6.1} & 0.013377 & 1.196742 & -0.009167 \\
\text{Margin} & 0.000348 & 0.606606 & 0.001868
\end{array}
```

All three claims hold. They hold on Chan’s continuous close too, over the 849 days it covers. There the declared rule gives an APR of 1.4373 percent against Example 6.1’s 1.4069 percent, a Sharpe ratio of 1.791969 against 1.187438, and a drawdown of 0.8077 percent against 0.9851 percent.

The margins are not equally strong. The APR margin of 0.000348 is small. Over the 849 days Chan’s continuous close covers, again as a fraction, the APR margin is 0.000304 on that close and 0.000225 on the rebuild. It keeps its sign on both copies of the prices but moves by about a quarter between them. Its sign also depends on the threshold, since a threshold of 2.9 or 3.2 percent turns it negative. So the APR claim is the weakest of the three.

The Sharpe ratio’s margin of 0.606606 carries the comparison at the book’s threshold. At 2.8 percent even that margin turns negative, and the declared rule loses all three claims. At 2.7 and 2.9 percent the Sharpe ratio’s margin is positive again. No test here asks whether any of the three margins is larger than day-to-day swings in TU’s returns could produce by chance.

### Where the Sharpe ratio’s margin comes from

Over the whole window, Example 6.1 never leaves the market. From 25 trading days before the window to its end, the rebuilt series always stood above its level 250 trading days earlier. So every tranche Example 6.1 opened was long, and all 25 are long on all 913 days. A rule that is fully long every day earns exactly the contract’s own return, so in this window Example 6.1’s rule is the same as buying TU and holding it. The [post on Example 1.1’s hypothesis tests](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-hypothesis-tests-lessons.md#lesson-5-two-checks-added-afterwards-point-at-drift-not-kurtosis) reaches the same mechanism from another direction. On a series that drifts upward, the 250-day rule is long most of the time and collects the drift.

The declared rule is that same long position with 341 days taken out. Over those 341 days, TU’s return compounds to −0.001244, close to nothing. Over the 572 days the rule is long, it compounds to 0.050629, which is the declared rule’s whole return. So the two rules earn almost the same. Their average annual returns, the mean daily return times 252 without compounding, are 0.013661 for the declared rule and 0.013351 for Example 6.1’s rule.

What differs is the risk. Sitting out 341 days that went nowhere removes their day-to-day swings without removing any return. Annual volatility is the standard deviation of daily returns scaled to a year, and the declared rule’s is 0.007575 against 0.011156 for holding TU. Divide each average return by its volatility and the Sharpe ratios of 1.80 and 1.20 follow.

![A whiteboard sketch titled “Nearly the same return, less swing”, drawn slowly. A brown row of short up and down ticks runs across the board, a schematic stand-in for TU’s daily returns, with brown words beside it reading “Example 6.1’s rule” and “holds TU every day”. Below it the same row is drawn again. It is green where its ticks match the brown ones, and it flattens to a grey line in three stretches, the first at the start. The ticks and the number and places of the stretches are schematic, and the grey share of the row is about the share of window days the rule sits flat. Green and grey words beside the row read “the declared rule” and “flat on 341 days”. Grey brackets sit under the three grey stretches, with grey words at the right end of their row reading “TU on 341 flat days: −0.001244”, and green brackets sit under the three green stretches, with green words at the right end of their row reading “TU on 572 long days: 0.050629”. Grey words at the bottom left read “average annual return / annual volatility”, then a green line reads “declared: 0.013661 / 0.007575 = 1.80” and a brown one “Example 6.1: 0.013351 / 0.011156 = 1.20”. Black words at the bottom right read “nearly the same return,” and “a smaller swing”. Each label shows for longer than usual, and the finished drawing holds for twelve seconds.](../docs/figures/roll_momentum_sketch_less_swing.gif)

The top panel of the figure in Lesson 1 shows the difference. The declared rule’s line goes flat through every shaded stretch, while Example 6.1’s line wanders up in some of them and down in others, and the two end close together.

So on this window the roll-return signal’s advantage is that it was out of the market on 341 of the 913 days, and those days earned about nothing. This run cannot say whether the roll return picked those days, chance did, or the shared prices behind γ did. On 169 of the flat days the position was set by a γ fitted on a day when the three farthest of its five contracts shared one price, the pattern Lesson 1 describes. TU swung more on those 169 days than across the window, with an annual volatility of 0.016727 against 0.011156. From 2009-10-01, once no position rests on those prices, the declared rule’s Sharpe ratio is 1.85 against Example 6.1’s 1.43, so a smaller margin remains.

That advantage belongs to this window. It says nothing about a window where TU fell. There Example 6.1 would go short, while the declared rule goes short only if γ falls below −3 percent, which it never did here.

### The book’s own comparison spans two windows

The book sets its new figures against Example 6.1’s printed ones: an APR of 2.5 percent against 1.7 percent, a Sharpe ratio of 2.1 against 1, and a drawdown of 1.1 percent against 2.5 percent. Example 6.1’s printed figures cover 2004-06-01 to 2012-05-11, and the [Example 6.1 post’s first lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-momentum-lessons.md#lesson-1-the-books-figures-come-from-the-full-window-not-the-line-the-script-runs) shows they reproduce on that window. The new figures start in 2009. So the book compares two windows as well as two rules. When both rules run on the same window, the APR margin is 0.000348 as a fraction, far smaller than the gap between the printed 2.5 and 1.7 percent.

## Lesson 3: a series saved only to May 2012 has to be rebuilt

This repository rests on one premise. A vendor can restate a price history, so a number computed from a series nobody kept is a number nobody can check. No file this repository keeps follows TU’s front contract to the end of the window. The strip does keep each contract’s own prices to that day, so the series can be rebuilt from a kept file, and then checked against Chan’s continuous close on the days the close covers.

A continuous future stitches one contract after another, and each switch is a roll. At each roll, a saved continuous series shifts its earlier prices so its price level has no gap. That shift is called back-adjustment, and the [post on VX against ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains it. The change on the roll day then depends on how the shift was measured, and it need not equal either contract’s own change. The rebuild here does something simpler. It takes each day’s return within one contract, from yesterday’s close to today’s, so a roll never enters a return.

The question is which day to switch. The rebuild takes the nearest contract that was priced the day before and still has at least seven trading days left before its last price. So the old contract earns through the seventh trading day before its last price and the new one from the sixth. The March 2012 roll shows it. The March 2012 contract’s last price in the strip is on 2012-03-30. It earns through 2012-03-21, and the June contract earns from 2012-03-22.

### Checking the rebuild against Chan’s continuous close

Chan’s continuous close sets the rebuild’s switch to within one day. Its daily changes are the old contract’s own through the eighth trading day before that contract’s last price, and the new contract’s from the sixth. On the seventh, the day between, its price is already the new contract’s, shifted as on the days after. Its change that day still does not say which contract earned it. On 29 of the 32 rolls in its span, its change on that day matches neither contract’s own change, and on one it matches the new contract’s.

The rebuild gives the day to the old contract. If the new contract gets it instead, a switch one day earlier, the declared rule gives an APR of 1.3665 percent and a Sharpe ratio of 1.789044, against 1.3725 percent and 1.803348.

The check against Chan’s continuous close covers the 1,999 daily changes the two series share.

1. **The returns agree.** They correlate at 0.998359.
2. **Every disagreement sits on the roll day.** 30 changes differ by more than the files’ rounding. All 30 fall on the seventh trading day before a contract’s last price, where the close’s change differs from the old contract’s own change and the rebuild takes the old contract’s return. The close’s span holds 32 rolls, and on the other two its change lands within rounding of the old contract’s.

![A whiteboard sketch titled “Chan’s continuous close switches a day early”, drawn slowly. A grey axis of TU’s trading days runs along the bottom from 2012-03-19 to 2012-03-30, one tick a day, with grey dates under four ticks reading “03-20”, “03-21”, “03-22” and “03-30”. Grey words under the dates read “days to last price”, with “8”, “7”, “6” and “0” under those four dates. Above the axis, two thin grey lines run across the same days. The upper one, labelled “March 2012 contract”, ends in a tick at 03-30, and the lower one is labelled “June 2012 contract”. A thick black line covers the March line from 03-19 to 03-21, and a second thick black line covers the June line from 03-22 to 03-30, with black words above reading “rebuild: March through 03-21, June from 03-22”. Between the two grey lines, a brown line labelled “Chan’s continuous close” runs to 03-20, where a dashed grey guide rises to the March line, with brown words reading “March’s close less 0.1407”. The brown line thickens from 03-20 to 03-21, where a second dashed grey guide drops to the June line. Brown words beside it read “03-21: switches to June’s close, +0.0625”, and black words under them read “neither March’s +0.0547 nor June’s +0.0546”, each contract’s own change that day. The brown line then runs on to 03-30. The rows say which contract each series reads rather than drawing prices to scale, and every mark sits at its own trading day. Black words at the bottom read “30 of 1,999 changes differ beyond rounding, all at 7 days to last price”. Each label shows for longer than usual, and the finished drawing holds for twelve seconds.](../docs/figures/roll_momentum_sketch_switch_day.gif)

So the rebuild’s daily changes match those of Chan’s continuous close within rounding on every shared day but 30 of the 32 roll days. On the 849 window days the close covers, the declared rule’s APR on the rebuild sits 0.000309 above its APR on that close. The margin between the two rules moves less, from 0.000304 on the close to 0.000225 on the rebuild, because both rules earn the same prices and much of the difference cancels. Lesson 2’s APR margin of 0.000348 is still small enough that the rebuild moves a fair share of it.

## Lesson 4: a rule declared late, and a variant set aside

A rule fixed before the data is read can be tested by the data. A rule fixed after trying many variants has already been fitted to it. The plan was to write this experiment’s rule down before computing any figure. That did not happen. Two trial runs first tried about 90 variants, across lags, held contracts, units, thresholds and roll rules. That count comes from a written note about the runs, and no test here checks it.

The declaration rests on three grounds the trial runs did not choose.

1. **The lag** is Example 6.1’s own convention, a position set on one day earning the next.
2. **The series** is Example 6.1’s front contract, since the rule on p. 206 revises Example 6.1.
3. **The roll day** comes from Chan’s continuous close to within one day, as Lesson 3 describes. Lesson 3 also gives the figures for a switch one day earlier.

The unit of γ is not among them. Chan’s script computes γ in column units, but the rule reads them because γ in months never trades in this window, which is a fact read from the same data the rule is tested on.

### The fifth-contract variant

One variant in the trial runs came close to the book. Instead of the front contract, it holds the fifth-nearest contract among those priced the day before, the farthest of the five that γ is fitted on. That gives an APR of 2.4712 percent, a Sharpe ratio of 2.144165 and a drawdown of 1.1583 percent. The first two match the book’s 2.5 percent and 2.1 at the book’s precision. The drawdown misses 1.1 percent.

How it is built gives one reason to doubt it. The position is set by γ, and γ is fitted partly on that same fifth contract’s price. Suppose the fifth contract closes a little low one day. The slope steepens, γ rises, and the rule goes long that same contract. If the low close was noise that reverses the next day, the long position earns the reversal. So part of what the variant earns could come from the fit reading the held contract’s price, rather than from the roll return the book describes. A fit of γ on the four nearest contracts alone, which leaves the held contract out of the fit, lowers the variant’s Sharpe ratio from 2.144165 to 1.802262. The same fit lowers the declared rule’s Sharpe ratio further, from 1.803348 to 1.429338, though the front contract it holds is in both fits. So the fall does not single out the held contract, and that explanation stays a candidate rather than a finding.

One related variant is checked by a test. It takes the fifth contract only from among those priced both the day before and the day it earns, so a nearer contract that stopped trading the day before drops out of the count. It gives a Sharpe ratio of 1.957852, short of the book’s 2.1.

Picking the fifth-contract variant now, after seeing that two of its figures match the book’s, would fit the rule to the answer. A search across enough variants on one file can often find one that matches a printed number. So the fifth-contract variant is reported beside the result and never counted as the result.

The same reasoning is why every result here is exploratory. The declaration came after the variants, so nothing here is a registered test of the roll-return signal, one whose rule was written down before any data was read. A registered test would fix its rule first and run on data this search never loaded.

## What this replication cannot say

Three things are beyond it.

1. **Whether the signal works out of sample.** The rule was written down after about 90 variants on the same strip, so its margins are not a test.
2. **Which version of the rule Chan ran.** No script ships for the rule on p. 206, and the book does not say how far Chan lagged the roll return or which price the position earns. The fifth-contract variant comes close to the book’s figures, and choosing it after its number was seen would fit the rule to the answer.
3. **What a trader would earn.** The returns are on the market value of the notes one contract controls. They include no trading cost and no margin, the deposit a broker requires to hold the contract. Chan puts TU’s notional value, the face value of those notes, at about $200,000 against a margin of about $400 (pp. 204 to 205), so any real position would be leveraged, and the figures here say nothing about the leverage.

## What this means for a trader

One habit for each lesson.

1. **Check a second copy of the data before blaming the download.** Here Chan’s continuous close lands near the rebuild on the days it covers, so the miss is not in the download there. What is left is how Chan read his own sentence or how he computed his figures.
2. **Ask what the benchmark was doing.** Example 6.1 was fully long for the whole window, so beating it meant beating buy and hold, and the win came from sitting out days that earned about nothing.
3. **Check a rebuilt series against the nearest saved one, and measure how far it moves the comparison.** Here the rebuild moved the APR margin by about a quarter, which matters for a margin that small.
4. **Write the rule down before reading the data, and distrust the variant that matches the book.** A variant found after the number is seen has already been fitted to it.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Examples 5.3 and 6.1, with pages 179 and 204 to 206 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. `TU_mom.m` and `estimateFuturesReturns.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code.

*Not investment advice. Code: [both rules and the rebuild](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_momentum.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_momentum_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_momentum_whiteboard.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_momentum.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_momentum_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_momentum_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-36-tu-momentum-traded-on-the-lagged-roll-return-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
