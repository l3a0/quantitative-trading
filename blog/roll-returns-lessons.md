# Chan’s spot and roll returns mostly reproduce on his own files, but his script counts contracts where his text says months, which inflates three of the five roll returns

*Table 5.1 of Algorithmic Trading splits five futures’ returns into spot and roll returns. Eight of ten cells match on Chan’s own files. His script counts contracts where the text says months, and in months each of the book’s claims fails for one future.*

## Why split a future’s return in two

On the day a futures contract expires, its price has to equal the spot price, the price of the thing it is written on. So a future can earn or lose money while the spot price stands still. If the contract trades above the spot today, it must drift down to meet it, and if it trades below, it must drift up. Ernest Chan calls that drift the **roll return**, and in *Algorithmic Trading* he writes that it is “an intrinsic part of its total return” (Chan, 2013, Kindle location 2326). The rest of the total return is the **spot return**, the move of the spot price itself.

The direction of the drift has a name. When the contracts nearest to expiry trade above the later ones, the market is in **backwardation**, and a holder earns a positive roll return as each contract climbs toward the spot. When the near contracts trade below the later ones, the market is in **contango**, and the roll return is negative (location 2326).

The split matters because it decides what a trader earns. Chan writes that misjudging it “cost me more than \$100,000 in trading loss” in 2006, his first year trading on his own (location 2385). His example is an ETF of commodity producers. Such an ETF usually **cointegrates** with the commodity’s spot price, meaning the two keep a stable long-run relation. It may still not cointegrate with the commodity’s futures price, because the roll return separates the future from the spot.

Chapter 6 then leans on the split to explain why some futures trend. Their roll returns keep one sign for long stretches and outweigh their spot returns (location 2683).

### What the reproduction found

Chan’s Example 5.3 measures the spot and roll returns of five futures: the Brazilian real (BR), corn (C), WTI crude oil (CL), copper (HG) and the two-year US Treasury note (TU). Table 5.1 prints each future’s average spot and roll return. This repository ran his script, `estimateFuturesReturns.m`, on his own data files and found three things.

1. **Eight of Table 5.1’s ten cells match.** Only HG’s and TU’s spot returns miss, even on the files Chan saved himself. HG’s is a tenth of a percentage point off, and TU’s has the opposite sign.
2. **The script counts contracts, not months.** The text says the time to maturity is measured in months. The script instead numbers the five contracts nearest to expiry 1 to 5, which treats neighbouring contracts as one month apart. For the three futures whose contracts are not all a month apart, that overstates the roll return by 2.0 to 3.0 times.
3. **With maturity measured in months, each of the book’s two claims fails for one future.** The first says BR, C and TU have roll returns much larger in size than their spot returns, which the replication reads as at least twice, and C’s falls short of twice. The second says BR, HG and TU have roll returns bigger in size than their spot returns, and HG’s falls below its spot return.

**Every result here is exploratory.** Chan chose the model, the futures and the dates, and the reproduction runs them on the same files. It can say whether his numbers follow from his data and nothing about whether a roll return persists after 2012.

Two earlier posts cover the futures background this one needs.

1. [The calendar spreads post](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#the-claim-and-the-files) explains what a futures contract is and why each delivery month trades as its own contract.
2. [The post on VX against ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains a roll and the continuous future stitched across rolls.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The model and the files

Chan’s model assumes both returns are constant (location 2364). Take a contract that expires at time T, priced on day t. Its log price, the natural logarithm of its price, is a constant, plus the spot return α times the date, minus the roll return γ times the time left to expiry. The book calls that time the time to maturity. On a log scale a steady percentage return draws a straight line:

```math
\ln F(t, T) = c + \alpha\, t - \gamma\, (T - t)
```

Two readings of that one equation give the two returns.

1. **Hold one contract.** T is fixed, so as t moves forward a year the log price rises by α from the spot and by γ from the shrinking time to expiry. The contract’s total return is α + γ, which is the sentence “total return = spot return + roll return” in symbols (location 2364).
2. **Hold one day.** Every contract trading that day shares t, so the log prices of contracts with later expiries fall on a straight line against their time to expiry, with slope −γ. Positive γ means the later contracts are cheaper, which is backwardation.

![An animated whiteboard sketch titled “One line, read two ways”, drawn slowly stroke by stroke. It is schematic and carries no figures from the run. A grey axis across is labelled “date t” and a grey axis up is labelled “log price”. A black line rising gently from left to right is labelled “spot: rises at the spot return”. Three grey lines start lower at the left edge, each below the one before, and each climbs more steeply than the spot line until it meets it, ending in a grey dot, the first about a third of the way across, the second past the middle and the third near the right end. A grey label reads “each contract ends at the spot”. The lowest grey line is then retraced in brown with an arrowhead where it meets the spot line, labelled “hold one contract: spot return + roll return”. A dashed black vertical line near the left edge crosses all four lines, with a black dot at each crossing, the spot highest and each later contract lower. A black label beneath reads “hold one day: one roll return lower per year to expiry”, and a last green label reads “roll return above 0: backwardation”. The finished drawing holds for twelve seconds.](../docs/figures/roll_returns_sketch_one_line.gif)

### How the script estimates each return

Two kinds of regression estimate the two returns. Each fits a straight line through points and reads off its slope.

1. **The spot return α** is the slope of the log spot price against the day number, which counts the trading days 1, 2, 3 and on. That slope is a return per trading day, and multiplying it by 252 trading days a year turns it into a return per year.
2. **The roll return γ** comes from one day at a time. The script takes the five contracts in the file nearest to expiry that have prices that day, provided no contract between them lacks a price. The book says to fit their log prices against their time to maturity, measured in months, and the script multiplies the fitted slope by −12. The 12 turns a slope per month into a return per year, and the minus sign turns the slope, which is −γ, into γ. The fitted line traces the day’s **forward curve**, which location 2399 glosses as “the future price as a function of maturity date”. The figure the table reports is the mean of γ over every day the fit runs. Lesson 2 shows that the script fits against something simpler than months.

### The data files

The data is Chan’s own: five MATLAB files saved on 2012-08-14. Each file holds one future’s spot price and the daily settlement price of each of its contracts, all on one calendar of trading days. A settlement price is the official end-of-day price the exchange sets. Chan’s corn file is named C2, and it is the C of Table 5.1.

The files start as early as 1986, and γ is defined on 1,087 to 6,028 days per file, ending in March 2012 for C and in August 2012 for the rest. The rules that decide each result are in [Entry 27 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading), which records Table 5.1 and the figures of Lessons 1 to 3 beside the tests that compute them.

## Lesson 1: eight of ten cells match on Chan’s own files

A cell **matches** when the computed figure rounds to the book’s at its one decimal of a percent, sign included. Here are the script’s figures beside Table 5.1, at the six decimal places the script’s `%f` format prints, the spot returns first and then the roll returns. The script prints each return as a fraction a year, so 0.050567 is 5.06 percent.

```math
\begin{array}{l|r|r}
\text{Future} & \alpha\ \text{computed} & \alpha\ \text{book} \\ \hline
\text{BR} & -0.026903 & -2.7\% \\
\text{C} & 0.028056 & 2.8\% \\
\text{CL} & 0.073019 & 7.3\% \\
\text{HG} & 0.050567 & 5.0\% \\
\text{TU} & 0.000039 & -0.0\%
\end{array}
```

```math
\begin{array}{l|r|r}
\text{Future} & \gamma\ \text{computed} & \gamma\ \text{book} \\ \hline
\text{BR} & 0.108133 & 10.8\% \\
\text{C} & -0.127757 & -12.8\% \\
\text{CL} & -0.070592 & -7.1\% \\
\text{HG} & 0.077172 & 7.7\% \\
\text{TU} & 0.032032 & 3.2\%
\end{array}
```

Eight cells match. Two miss.

1. **HG’s spot return** is 5.06 percent, which rounds to 5.1 against the printed 5.0.
2. **TU’s spot return** is positive. The book prints −0.0, a negative number that rounds to zero, and 0.0039 percent rounds to zero from the other side.

Two more checks agree.

1. **CL’s γ** is first defined on 2004-11-22 and last on 2012-08-13, the span Chan gives for his Figure 5.5.
2. **C’s two figures** agree with Chan’s 2018 Python port of the script, his translation of the MATLAB into Python, which prints them in full in its comments, 0.02805562210100287 and −0.12775650227459556. The run here agrees with both to within 10⁻¹².

### Other ways to compute the spot return

The misses come from Chan’s own saved files, so a vendor revising its price history cannot explain them. The replication tried three other readings of α after HG’s miss.

1. **Numbering the days after dropping the days with no spot price**, rather than before, gives HG 0.050587.
2. **Reading the prices at single precision** gives 0.050567, unchanged.
3. **Regressing on calendar days and annualizing by 365** gives 0.050315, which matches HG’s cell.

The third reading is the only one that matches HG, and it is not what the script computes. The script numbers the days with `T=[1:length(spot)]'`, which counts the rows 1, 2, 3 and on. The calendar-day reading also moves C’s α to 0.027998, off the figure the Python port printed. So the replication keeps the script’s day numbering. None of the three turns TU’s α negative.

Neither miss changes what the book uses the table to argue, which is the two claims Lesson 3 tests. HG’s miss is a tenth of a percentage point, and TU’s is the sign of a spot return that is almost zero.

## Lesson 2: the script counts contracts, not months

Location 2399 says the fit runs against each contract’s time to maturity, “measured in months”. The script does something simpler. It numbers the five contracts 1 to 5 in order of expiry, regresses their log prices on those numbers, and multiplies the slope by −12. That treats neighbouring contracts as one month apart. For a future with a contract every month, the script’s fit and the fit in months agree. For one without, they do not.

A made-up example shows how large the difference is. Build a forward curve with a roll return of exactly 0.03 a year on quarterly contracts, March, June, September, December and the next March. Neighbouring contracts are three months apart, so the price falls three months’ worth from one to the next. The fit in months recovers 0.03. The script’s fit reads that three-month step as one month’s and returns 0.09, three times too large.

![An animated whiteboard sketch titled “Same five prices, three times the slope”, drawn stroke by stroke from the made-up example. A grey axis across the bottom, with a tick for each month, is marked “Mar”, “Jun”, “Sep”, “Dec” and “Mar” under every third tick and labelled “months from the nearest contract”. Five black dots sit at those five months, falling evenly from upper left to lower right, the drop drawn far larger than the true fall from 50.00 to 48.52, and no price axis is drawn. A green line through them is labelled “fit in months: 0.03 a year”. Grey arrows then slide the four later dots left at the same heights until the five sit one tick apart, labelled “same prices, one column apart”. Red dots mark the new places, and a red line through them, three times as steep as the green one and starting from the same first dot, is labelled “script’s fit: 0.09 a year, three times”.](../docs/figures/roll_returns_sketch_same_five_prices.gif)

### The five futures under both fits

In Chan’s files, two futures have a contract every month and three do not. On every day the script computes a future’s γ, its five nearest contracts are spaced like this.

1. **BR** is one month apart on all 4,210 days, and **CL** on all 1,941.
2. **TU** is three months apart on all 1,087 days.
3. **C** mixes gaps of two and three months, in five patterns.
4. **HG** mixes gaps of one, two and three months, in six patterns.

The fit in months gives this, beside the script’s fit.

```math
\begin{array}{l|r|r}
\text{Future} & \gamma\ \text{script's fit} & \gamma\ \text{fit in months} \\ \hline
\text{BR} & 0.108133 & 0.108133 \\
\text{C} & -0.127757 & -0.053011 \\
\text{CL} & -0.070592 & -0.070592 \\
\text{HG} & 0.077172 & 0.038573 \\
\text{TU} & 0.032032 & 0.010677
\end{array}
```

BR’s and CL’s agree to within 10⁻¹³, as monthly contracts must. Table 5.1 overstates C’s roll return by 2.4 times, HG’s by 2.0 and TU’s by 3.0.

Nothing here scores the figures from the fit in months as a pass or a fail. Chan printed none for them, and they are this repository’s reading of his sentence at location 2399. The script’s figures are the ones that match, so the script is what printed Table 5.1.

## Lesson 3: with maturity measured in months, each of the book’s two claims fails for one future

The book draws two claims from the table.

1. **Location 2399** says that for BR, C and TU, the magnitude of the roll return is “much larger than that of the spot returns”. The replication read “much larger” as at least twice. That [pass mark was written down](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading) before the replication’s code existed, though after a first rough run had already measured the figures.
2. **Location 2683** says BR, HG and TU have roll returns “bigger in magnitude than their spot returns”, which is how Chapter 6 explains why they trend.

Under the script’s γ, both hold. BR is the narrowest case for the first claim, with a roll return 4.02 times its spot return, so the pass does not depend on exactly where the pass mark of twice sits. CL is the one future whose roll return is smaller than its spot return, and neither claim names it.

Under the fit in months, each claim fails for one future.

1. **C fails the first claim.** Its roll return is 1.89 times its spot return, short of twice.
2. **HG fails the second.** Its roll return of 3.86 percent is smaller than its spot return of 5.06 percent. So Chapter 6’s explanation for HG rests on a comparison that holds only under the script’s arithmetic.

BR and TU hold either way. Nothing here scores these results as a pass or a fail, because Chan printed no figure for the fit in months, and the order of the pass marks gives a second reason. The replication wrote down the second claim’s pass mark, a roll return bigger than the spot return, for the fit in months before its code existed. It applied the first claim’s pass mark, at least twice, to the fit in months only afterwards, once it had seen the figures.

Neither claim tests what Chapter 6 uses the table for, which is explaining why these futures trend. Comparing two averages says nothing about whether a roll return causes any of that trending.

The figure below sets out Lessons 2 and 3 in its upper panel, each future’s spot return beside its two roll returns. Its lower panel redraws Chan’s Figure 5.5 for Lesson 4.

![Two charts stacked. The upper chart is a bar chart with five groups, BR, C, CL, HG and TU, each holding three bars in percent per year. A grey bar shows the size of the spot return, a brown bar the script’s roll return, and a green bar the roll return with maturity in months. For BR the brown and green bars are equal at about 10.8, well above a dashed red tick at twice the grey bar. For C the brown bar reaches about 12.8 while the green bar, about 5.3, sits just under the dashed tick at twice the 2.8 spot return. For CL all three bars are near 7. For HG the brown bar is about 7.7, above the grey bar of about 5.1, while the green bar of about 3.9 falls below it. For TU the grey bar and its dashed tick both sit at almost zero, the brown bar is about 3.2 and the green about 1.1. The lower chart plots CL’s daily roll return from late 2004 to August 2012 as a thin black line around a horizontal zero line. Areas above zero are shaded green and areas below shaded red. The line sits just above zero, shaded green, through 2005 and near zero in early 2006, then dips below zero from mid-2006 to about −0.3 in the first half of 2007, rises above zero to about 0.15 from mid-2007 to mid-2008, spikes briefly to about 0.26 in September 2008, then plunges to about −1.1 in January 2009. It stays below zero, with dips to between −0.2 and −0.5, until late 2011, and ends just below zero. A dashed brown line marks the mean of −0.070592. The title calls the redraw exploratory.](../docs/figures/roll_returns.png)

*Each future’s spot return and two roll returns, with a tick at twice the spot return where location 2399’s claim applies, and CL’s roll return day by day, redrawn on Chan’s files saved 2012-08-14. The upper panel redraws Table 5.1 with the roll return from the fit in months beside it, and the lower panel redraws the book’s Figure 5.5, CL’s roll return from November 22, 2004, to August 13, 2012.*

## Lesson 4: the average hides a roll return that drifts and changes sign

Table 5.1 prints one number per future, and the model behind it says γ is constant. Chan himself says the estimate will not be constant: the fit depends on the day and the contracts trading then, so “we will still end up with a slowly varying estimated γ” (location 2399). The lower panel of the figure shows how far it varies for CL. CL’s file holds no contract earlier than January 2007. So until that contract expired on 2006-12-19, the five nearest were always the January to May 2007 contracts, more than two years out when the panel starts and about a year out on 2006-01-05, rather than the front months a holder rolls.

1. **Mostly contango.** CL’s γ is negative on 1,388 of its 1,941 days and positive on 552. On the remaining day, 2006-01-05, the five prices rise and fall back evenly, from 65.38 to 65.41 and back to 65.38, so the fitted slope and γ are zero apart from rounding.
2. **Long runs, with many breaks.** It changes sign 29 times. Its longest run of one sign is contango, from 2008-10-09 to 2011-10-21, 766 trading days.
3. **Extremes far from the mean.** Its highest value is 0.258871, on 2008-09-22. Its lowest is −1.121372, on 2009-01-15, less than four months later. The mean is −0.070592.

Chapter 6’s explanation needs the sign to stay put. Location 2683 says “the sign of roll returns does not vary very often”, so that holding a future for a long time collects a roll return of one sign. The five futures differ on that.

1. **BR’s γ** is negative on 3 of its 4,210 days.
2. **HG’s γ** is positive on 3,139 of its 6,028 days, a little over half, and changes sign 198 times, against CL’s 29.

These counts score nothing as a pass or a fail. Nobody wrote down beforehand how few sign changes would satisfy “does not vary very often”, so no pass mark existed when the replication measured them.

## What this replication cannot say

Three questions are beyond it.

1. **Whether returns are constant.** The model is the book’s simplification, and Lesson 4 shows γ drifting. The replication reproduces the mean of the drifting series without testing the model.
2. **Whether the fit in months is what Chan meant.** It is this repository’s reading of his sentence, and he printed no figure for it.
3. **Whether a roll return persists.** Every figure is in-sample, computed on the same 1986 to 2012 data the book studied, and none comes from later years. Two later examples in the book trade on γ, a [crude oil calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading) and [TU momentum traded on the lagged roll return](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-36-tu-momentum-traded-on-the-lagged-roll-return-chans-algorithmic-trading), and each has its own entry in the replication log.

## What this means for a trader

One habit for each lesson.

1. **Test the arithmetic once the data is ruled out.** When a figure misses on the author’s own saved file, a vendor’s revision cannot explain it. Try the readings the arithmetic allows, and keep the one the script states.
2. **Check the units a script regresses on.** Multiplying a slope by 12 to make it yearly assumes monthly steps, and quarterly contracts triple the result.
3. **Re-run a claim under the method the text describes.** When text and script disagree, run the claim both ways and report which one it holds under.
4. **Read the series behind an average.** A mean roll return can hide long runs, sign changes and extremes many times its size, so a claim about the sign needs the series, not the mean.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.3, Table 5.1, Figure 5.5 and Kindle locations 2326, 2364, 2385, 2399 and 2683.
2. `estimateFuturesReturns.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code, and `estimateFuturesReturns.py` in `PythonCodesAndData.zip` at the same commit, his 2018 Python port.
3. Hull, J. C. (1997). *Options, Futures, and Other Derivatives*. Prentice Hall. Location 2364 cites it for the model of a futures price.

*Not investment advice. Code: [the spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns_figures.py), with the checks behind [the example’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_returns.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_returns_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
