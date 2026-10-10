# Chan’s spot and roll returns reproduce on his own files, and three of the five count contracts where the text says months

*Table 5.1 of Algorithmic Trading splits five futures’ returns into spot and roll returns. Eight of its ten cells land on Chan’s own files. His script counts contracts where the text says months, and in months each of the book’s two claims loses a strip.*

## Why split a future’s return in two

A futures contract has to end up at the spot price, the price of the thing it is written on, on the day it expires. So a future can earn or lose money while the spot price stands still. If the contract trades above the spot today, it must drift down to meet it, and if it trades below, it must drift up. Ernest Chan calls that drift the **roll return**, and in *Algorithmic Trading* he writes that it is “an intrinsic part of its total return” (Chan, 2013, location 2326). The rest of the total return is the **spot return**, the move of the spot price itself.

The direction of the drift has a name. When the contracts nearest to expiry trade above the later ones, the market is in **backwardation**, and a holder earns a positive roll return as each contract climbs toward the spot. When the near contracts trade below the later ones, the market is in **contango**, and the roll return is negative (location 2326).

The split matters because it decides what a trader actually earns. Chan writes that misjudging it “cost me more than \$100,000 in trading loss” in 2006, his first year trading on his own (location 2385). The subtlety was that an ETF of commodity producers can move with the commodity’s spot price and not with its futures price, because the roll return separates the two. Chapter 6 then leans on the split to explain why some futures trend: their roll returns keep one sign for long stretches and outweigh their spot returns (location 2683).

Chan’s Example 5.3 measures both parts for five futures: the Brazilian real (BR), corn (C), WTI crude oil (CL), copper (HG) and the two-year US Treasury note (TU). Table 5.1 prints the averages. This repository ran his script, `estimateFuturesReturns.m`, on his own data files and found three things.

1. **Eight of Table 5.1’s ten cells land.** HG’s and TU’s spot returns miss, by a tenth of a point and by a sign, on the files Chan saved himself.
2. **The script counts contracts, not months.** The text says the time to maturity is measured in months. The script regresses on contract positions 1 to 5, so for the three futures whose contracts are not a month apart it overstates the roll return, by 2.4 to 3.0 times.
3. **In months, each of the book’s two claims loses a strip.** HG’s roll return falls below its spot return, and C’s falls short of twice its spot return.

**Every result here is exploratory.** Chan chose the model, the futures and the dates, and the reproduction runs them on the same files. It can say whether his numbers follow from his data and nothing about whether a roll return persists after 2012.

Two earlier posts cover the futures background this one needs. [The calendar spreads post](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md#the-claim-and-the-files) explains what a futures contract is and why each delivery month trades as its own contract. [The post on VX against ES](https://github.com/l3a0/quantitative-trading/blob/main/blog/vx-es-lessons.md#the-regression-and-the-files) explains a roll and the continuous future stitched across rolls. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The model and the files

Chan’s model assumes both returns are constant (location 2364). Take a contract that expires at time T, priced on day t. Its log price is a constant, plus the spot return α times the date, minus the roll return γ times the time left to expiry:

```math
\ln F(t, T) = c + \alpha\, t - \gamma\, (T - t)
```

Two readings of that one line give the two returns.

1. **Hold one contract.** T is fixed, so as t moves forward a year the log price rises by α from the spot and by γ from the shrinking time to expiry. The contract’s total return is α + γ, which is the sentence “total return = spot return + roll return” in symbols (location 2364).
2. **Hold one day.** Every contract trading that day shares t, so the log prices of contracts with later expiries fall on a straight line whose slope is −γ. Positive γ means the later contracts are cheaper, which is backwardation.

So the estimates are two regressions, each a straight line fitted through points with its slope read off.

1. **The spot return α** is the slope of the log spot price on the day number, times 252 trading days a year.
2. **The roll return γ** comes from one day at a time. The script takes the five nearest contracts with prices that day, fits their log prices against their time to maturity, and multiplies the slope by −12 to turn a slope per month into a return per year. That line is the day’s **forward curve**, which location 2399 glosses as “the future price as a function of maturity date”. The figure the table reports is the mean of γ over every day the fit runs.

The data is Chan’s own: five MATLAB files saved on 2012-08-14, which this post calls **strips**. Each strip holds one commodity’s spot price and the daily settlement of every contract, all on one calendar of trading days. Chan’s corn file is named C2, and it is the C of Table 5.1. The strips start as early as 1986, and γ is defined on 1,087 to 6,028 days per strip, ending in March 2012 for C and in August 2012 for the rest. The rules that decide each result are in [Entry 27 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading), which records every figure below beside the assertion that computes it.

## Lesson 1: eight of ten cells land on Chan’s own files

A cell **lands** when the computed figure rounds to the book’s at its one decimal of a percent, sign included. Here are the script’s figures, at the six decimals its `%f` prints, beside Table 5.1.

```math
\begin{array}{l|r|r|r|r}
\text{Future} & \alpha\ \text{computed} & \alpha\ \text{book} & \gamma\ \text{computed} & \gamma\ \text{book} \\ \hline
\text{BR} & -0.026903 & -2.7\% & 0.108133 & 10.8\% \\
\text{C} & 0.028056 & 2.8\% & -0.127757 & -12.8\% \\
\text{CL} & 0.073019 & 7.3\% & -0.070592 & -7.1\% \\
\text{HG} & 0.050567 & 5.0\% & 0.077172 & 7.7\% \\
\text{TU} & 0.000039 & -0.0\% & 0.032032 & 3.2\%
\end{array}
```

Eight cells land. Two miss.

1. **HG’s spot return** is 5.06 percent, which rounds to 5.1 against the printed 5.0.
2. **TU’s spot return** is positive. The book prints −0.0, a negative number that rounds to zero, and 0.0039 percent rounds to zero from the other side.

Two more checks land exactly. CL’s γ is first defined on 2004-11-22 and last on 2012-08-13, the span Chan gives for his Figure 5.5. Chan’s 2018 Python port of the script prints C’s two figures in full in its comments, 0.02805562210100287 and −0.12775650227459556, and the run here agrees with both to within 10⁻¹².

The misses come from Chan’s own saved files, so a vendor revising its price history cannot explain them. Three other readings of α were tried after the miss.

1. **Numbering the days after the gaps are dropped**, rather than before, gives HG 0.050587.
2. **Reading the prices at single precision** gives 0.050567, unchanged.
3. **Regressing on calendar days and annualizing by 365** gives 0.050315, which lands HG’s cell.

The third reading is the only one that lands HG, and it is not what the script computes. The script numbers the days with `T=[1:length(spot)]'`, and the calendar-day reading moves C’s α to 0.027998, off the figure the Python port printed. So the day number stays. None of the three turns TU’s α negative.

Neither miss changes what the table is used to argue. HG’s is a tenth of a point, and TU’s is a sign on a spot return of almost nothing.

## Lesson 2: the script counts contracts, not months

Location 2399 says the fit runs against each contract’s time to maturity, “measured in months”. The script does something simpler. It regresses the five log prices on the numbers 1 to 5, their positions in the list, and multiplies the slope by −12. That treats neighbouring contracts as one month apart. For a future with a contract every month, the two agree. For one without, they do not.

A planted example shows the size of the gap. Build a forward curve with a roll return of exactly 0.03 a year on quarterly contracts, March, June, September, December and the next March. Neighbouring contracts are three months apart, so the price falls three months’ worth from one to the next. The month fit recovers 0.03. The column fit reads that three-month step as one month’s and returns 0.09, three times too large.

The five strips split the same way. Across every day each strip’s γ is defined, the five nearest contracts are spaced like this.

1. **BR** is one month apart on all 4,210 days, and **CL** on all 1,941.
2. **TU** is three months apart on all 1,087 days.
3. **C** mixes gaps of two and three months, in five patterns.
4. **HG** mixes gaps of one, two and three months, in six patterns.

Measuring maturity in months instead gives this, beside the script’s figure.

```math
\begin{array}{l|r|r}
\text{Future} & \gamma\ \text{on columns, the script} & \gamma\ \text{on months} \\ \hline
\text{BR} & 0.108133 & 0.108133 \\
\text{C} & -0.127757 & -0.053011 \\
\text{CL} & -0.070592 & -0.070592 \\
\text{HG} & 0.077172 & 0.038573 \\
\text{TU} & 0.032032 & 0.010677
\end{array}
```

BR’s and CL’s agree to within 10⁻¹³, as monthly contracts must. Table 5.1 overstates C’s roll return by 2.4 times, HG’s by 2.0 and TU’s by 3.0.

The month-spaced figures carry no verdict. Chan printed none for them, and they are this repository’s reading of his sentence. The script’s figures are the ones that land, so the script is what printed Table 5.1.

## Lesson 3: in months, each of the book’s claims loses a strip

The book draws two claims from the table.

1. **Location 2399** says that for BR, C and TU, the roll return is “much larger than that of the spot returns”. The replication read “much larger” as at least twice, a pass mark written down before the build, though after a scratch run had already measured the figures.
2. **Location 2683** says BR, HG and TU have roll returns “bigger in magnitude than their spot returns”, which is why Chapter 6 expects them to trend.

Under the script’s γ, both hold. BR is the narrowest case for the first claim, with a roll return 4.02 times its spot return, so the verdict does not rest on where the line sits. CL is the one strip whose roll return is smaller than its spot return, and neither claim names it.

Under the month-spaced γ, each claim loses a strip.

1. **HG fails the second claim.** Its roll return of 3.86 percent is smaller than its spot return of 5.06 percent. So the comparison Chapter 6 rests its HG explanation on holds only under the script’s arithmetic.
2. **C fails the first.** Its roll return is 1.89 times its spot return, short of twice.

BR and TU hold either way. The pass marks were not written at the same moment, which is one more reason the month-spaced results carry no verdict. Only the second claim’s pass mark was declared for the month-spaced γ before the build. The first claim’s was applied to it at the build, after the figures were seen.

Neither claim tests what Chapter 6 uses it for. Comparing two averages says nothing about whether a roll return explains any momentum.

The figure below sets out both lessons. The upper panel puts each strip’s spot return and its two roll returns side by side, and the lower panel redraws Chan’s Figure 5.5.

![Two charts stacked. The upper chart is a bar chart with five groups, BR, C, CL, HG and TU, each holding three bars in percent per year. A grey bar shows the size of the spot return, a brown bar the script’s roll return, and a green bar the roll return with maturity in months. For BR the brown and green bars are equal at about 10.8, well above a dashed red tick at twice the grey bar. For C the brown bar reaches about 12.8 while the green bar, about 5.3, sits just under the dashed tick at twice the 2.8 spot return. For CL all three bars are near 7. For HG the brown bar is about 7.7, above the grey bar of about 5.1, while the green bar of about 3.9 falls below it. For TU the grey bar is invisible at almost zero, the brown bar is about 3.2 and the green about 1.1. The lower chart plots CL’s daily roll return from late 2004 to August 2012 as a thin black line around a horizontal zero line. Areas above zero are shaded green and areas below shaded red. The line sits just above zero through 2005, dips below to about −0.3 in 2007, rises above zero to about 0.15 from mid-2007 to mid-2008, spikes briefly to about 0.26 in September 2008, then plunges to about −1.1 in January 2009. It stays below zero, with dips to between −0.2 and −0.5, until late 2011, and ends just below zero. A dashed brown line marks the mean of −0.070592. The title calls the redraw exploratory.](../docs/figures/roll_returns.png)

*Each strip’s spot return and two roll returns, with a tick at twice the spot return where location 2399’s claim applies, and CL’s roll return day by day, redrawn on Chan’s strips saved 2012-08-14. The upper panel redraws Table 5.1 with the month-spaced roll return beside it, and the lower panel redraws the book’s Figure 5.5, CL’s roll return from November 22, 2004, to August 13, 2012.*

## Lesson 4: the average hides a roll return that drifts and changes sign

Table 5.1 prints one number per future, and the model behind it says γ is constant. Chan says himself that it is not: the fit depends on the day and the contracts trading then, so “we will still end up with a slowly varying estimated γ” (location 2399). The lower panel of the figure shows how far it varies for CL.

1. **Mostly contango.** CL’s γ is negative on 1,389 of its 1,941 days and positive on 552.
2. **Long runs, with many breaks.** It changes sign 29 times. Its longest run of one sign is contango, from 2008-10-09 to 2011-10-21, 766 days.
3. **Extremes far from the mean.** Its highest value is 0.258871, on 2008-09-22. Its lowest is −1.121372, on 2009-01-15, less than four months later. The mean is −0.070592.

Chapter 6’s explanation needs the sign to stay put. Location 2683 says “the sign of roll returns does not vary very often”, so that holding a future for long collects a roll return of one sign. The strips differ on that.

1. **BR** fits the sentence. Its γ is negative on 3 of its 4,210 days.
2. **HG** does not. Its γ is positive on 3,139 of its 6,028 days, a little over half, and changes sign 198 times.

So HG, the strip whose explanation Lesson 3 already weakened, is also the strip whose roll return changes sign most. These counts carry no verdict. Nobody wrote down beforehand how few sign changes count as “not very often”, so no pass mark existed when they were measured.

This is the first limit Entry 27 names. The table reproduces the mean of a series that drifts, and reproducing a mean does not test the model that calls it constant. The result stays exploratory. It shows what Chan’s own files hold and nothing about a roll return’s sign in later years.

## What this replication cannot say

Three questions are beyond it.

1. **Whether returns are constant.** The model is the book’s simplification, and Lesson 4 shows γ drifting. The replication reproduces the mean of the drifting series without testing the model.
2. **Whether the month-spaced γ is what Chan meant.** It is this repository’s reading of his sentence, and he printed no figure for it.
3. **Whether a roll return persists.** Every figure is in-sample on 1986 to 2012. Two later examples in the book trade on γ, a [crude oil calendar spread](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-34-mean-reversion-on-crude-oils-12-month-calendar-spread-chans-algorithmic-trading) and [TU momentum traded on the lagged roll return](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-36-tu-momentum-traded-on-the-lagged-roll-return-chans-algorithmic-trading), and each has its own entry in the replication log.

## What this means for a trader

One habit for each lesson.

1. **Test the arithmetic once the data is ruled out.** When a figure misses on the author’s own saved file, a vendor’s revision cannot explain it. Try the readings the arithmetic allows, and keep the one the script states.
2. **Check the units a script regresses on.** A slope annualized by 12 assumes monthly steps, and quarterly contracts triple it.
3. **Re-run a claim under the method the text describes.** When text and script disagree, a conclusion that holds under only one of them rests on the arithmetic rather than the idea.
4. **Read the series behind an average.** A mean roll return can hide long runs, sign changes and extremes many times its size, and a trade that relies on the sign needs the run, not the mean.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.3, Table 5.1, Figure 5.5 and Kindle locations 2326, 2364, 2385, 2399 and 2683.
2. `estimateFuturesReturns.m`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code, and `estimateFuturesReturns.py` in `PythonCodesAndData.zip` at the same commit, his 2018 Python port.
3. Hull, J. C. (1997). *Options, Futures, and Other Derivatives*. Prentice Hall. Location 2364 cites it for the model of a futures price.

*Not investment advice. Code: [the spot and roll returns](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/roll_returns_figures.py), with the checks behind [the example’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_returns.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_roll_returns_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-27-spot-and-roll-returns-of-five-futures-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
