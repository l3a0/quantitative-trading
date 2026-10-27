# Chan’s commodity seasonals fit his counts in every year the files have prices for, and win a smaller share of years after the book

*A count of profitable years is only as good as the years it counts, where it starts, and who chose the trade.*

## Why test a strategy published as alive

A reader might put money behind a claim that a trade still pays, so the record behind the claim is worth checking.

Ernest Chan’s *Quantitative Trading* makes that claim for seasonal trades in commodity futures, trades that buy and sell on the same calendar dates every year. Much of the seasonality in equity markets, he writes, has weakened or disappeared, while some commodity seasonals are still profitable (Chan, 2021, p. 175). He calls them “alive and well”, perhaps because the demand behind them is a real economic need rather than speculation (p. 183). [The companion post on the equity seasonals](https://github.com/l3a0/quantitative-trading/blob/main/blog/equity-seasonals-lessons.md) tested the equity half of that claim. This one tests the commodity half.

Chan gives two trades, each with a count of profitable years.

1. **Gasoline.** Buy the May contract at the close of April 13 and sell it at the close of April 25, ahead of the summer driving season. Chan counts 19 profitable years of 21, from 1995 to 2015.
2. **Natural gas.** Buy the June contract at the close of February 25 and sell it on April 15, as power generators buy ahead of the air-conditioning season. Chan counts 13 consecutive profitable years in the main text and 14 in a sidebar.

Both trades ran on the free settlement prices that the US Energy Information Administration (EIA) publishes for futures traded on the New York Mercantile Exchange (NYMEX). Three results came out.

1. **Natural gas reproduces both of Chan’s counts** if both were written for the first edition and count from 1995.
2. **Gasoline fits Chan’s count in every year the files have prices for.** They show the 2 losing years his count allows and no third, plus 3 years with no price.
3. **Both trades averaged a loss after the years Chan counted.**

```math
\small\begin{array}{l|r|r}
 & \text{Book’s years} & \text{After} \\ \hline
\text{Natural gas} & \text{1994 to 2008} & \text{2009 to 2023} \\
\quad\text{Years won} & 15 \text{ of } 15 & 7 \text{ of } 15 \\
\quad\text{Mean return} & +10.6\% & -0.4\% \\
\quad\text{Sharpe ratio} & 1.0 & 0.0 \\
\quad\text{Drawdown} & 22\% & 60\% \\ \hline
\text{Gasoline} & \text{1995 to 2015} & \text{2016 to 2023} \\
\quad\text{Years won} & 16 \text{ of } 18 & 3 \text{ of } 8 \\
\quad\text{Mean return} & +3.2\% & -1.9\% \\
\quad\text{Sharpe ratio} & 0.8 & -0.4 \\
\quad\text{Drawdown} & 11\% & 30\%
\end{array}
```

A year’s return is the change in the contract’s price over its entry price, before costs. The Sharpe ratio divides the mean yearly return by its standard deviation. The drawdown is the largest fall from a peak in the summed yearly returns, marked on every trading day the files hold a price, so it counts a fall inside a trade that still ended the year ahead. Each year stakes one contract’s entry value, so returns and drawdowns are shares of one stake. Gasoline’s 1995 to 2015 leaves out the 3 years with no price. Nobody set a pass mark for the years after the book before computing them, so the split describes the record rather than grading Chan’s claim.

Each trade happens once a year, so each of the table’s four periods, every trade before and after the book, rests on only 8 to 18 yearly results. Lesson 4 works out what that few results can show: gasoline’s fall after the book stands out from its noise, and natural gas’s typical year clearly worsened while its average cannot be told from before. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two trades and the files

A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, so the May and June gasoline contracts have different prices. Each trading day ends with a **settlement price** for every contract, the exchange’s official close, and both trades buy and sell at it. When a trade date is not a trading day, each trade enters on the next one and exits on the previous one (pp. 183 to 185). Chan names no time of day for the natural gas exit, so the run exits at the close. A year is **profitable** when the exit settlement is strictly above the entry settlement.

Every passage quoted here is in the revised edition of 2021. The first edition matters to Lesson 1. Wiley released it in November 2008 and dated it 2009.

### Five files from EIA, numbered by expiry

EIA publishes settlement prices for the nearest four contracts of each product. It numbers them by expiry rather than by month: contract 1 is whichever contract stops trading next, and each number has its own file. So the run has to work out which file holds the May or June contract on each trade date, which Lesson 5 comes back to. The run reads five files covering three products, all downloaded on 2 October 2026:

1. New York Harbor regular gasoline, contract 1, through 2005.
2. RBOB gasoline, contract 1, from 2006. RBOB replaced the New York Harbor contract and began trading in October 2005.
3. Henry Hub natural gas, contracts 2, 3 and 4.

## Lesson 1: a count of consecutive years needs its start year and its edition

The main text says the natural gas trade “has been profitable for 13 consecutive years as of this writing” (p. 185). The sidebar says 14 (p. 185). Neither says which year its streak ends in, and either may be text kept from the first edition.

The natural gas files first hold a whole trade in 1994. Every year from 1994 to 2008 is profitable, and 2009 is a loss. So where a streak ends depends on where the count starts:

```math
\begin{array}{l|r|r}
\text{Streak ending in} & \text{From 1995} & \text{From 1994} \\ \hline
2007 & 13 & 14 \\
2008 & 14 & 15
\end{array}
```

Counted from 1995, the main text’s 13 is the streak ending in 2007 and the sidebar’s 14 is the streak ending in 2008. Each trade closes by mid-April, so both streaks end before the first edition’s release in November 2008. Both counts reproduce if they were written for that edition. The files settle half of that reading.

1. **They rule out the revised edition.** 2009 is a loss, so counted from 1995 a streak of 13 or more can end only in 2007 or 2008.
2. **They cannot pick the start year.** 1994 is profitable too. Counted from 1994, the streaks of 13 and 14 end in 2006 and 2007 instead. Only Chan’s gasoline sidebar, which counts from 1995, favors 1995.

![“The start year decides where a streak ends”, drawn slowly stroke by stroke on a year axis from 1994 to 2009 that carries a label only at “1994”, “1995”, “2006”, “2007”, “2008” and “2009”. Each year from 1994 to 2008 has a blue dot on the axis, and 2009 has an orange cross labelled “loss”. A caption reads “dot: a profitable year”. A note in the lower right names the trade as “natural gas, June contract”. A dashed grey line between 2008 and 2009 marks the “first edition, Nov 2008”. Above the axis two purple brackets start at 1995. “13 from 1995, main text” ends at 2007 and “14 from 1995, sidebar” ends at 2008, both before the dashed line. Below the axis two black brackets start at 1994. “13 from 1994” ends at 2006 and “14 from 1994” ends at 2007. Starting the count a year earlier ends each streak a year earlier. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_streak_start.gif)

### Gasoline’s two claims read as two editions

Gasoline’s main text says 19 profitable years of the last 21 “as of 2015” (p. 183). Its sidebar says Chan “would have realized a profit every year since 1995” (p. 184), which cannot hold as of 2015, because 19 of 21 leaves 2 losing years. So the sidebar reads as first-edition text covering 1995 to 2008. Over those years the files show no loss, 11 profitable years and 3 with no price on a trade date. One book prints a 2015 count beside a 2008 claim.

![“Gasoline’s two claims read as two editions”, drawn slowly stroke by stroke on a year axis from 1995 to 2015 that carries a label only at “1995”, “2008” and “2015”. Each profitable year has a blue dot on the axis, and 2009 and 2012 each have an orange cross. Under 1997 to 1999, which have no mark, a grey span reads “no row”. A dashed grey line between 2008 and 2009 marks the “first edition, Nov 2008”. Above the axis a purple bracket, “sidebar: a profit every year since 1995”, runs from 1995 to 2008 and ends before the dashed line and before either cross. Above it a black bracket, “main text: 19 of 21, as of 2015”, runs from 1995 to 2015, past the dashed line and both crosses. Captions read “dot: a profitable year” and “x: a loss, 2009 and 2012”, and a note in the lower right names the contract as “May contract”. The sidebar’s claim fits the first edition’s years and the main text’s count fits the revised edition’s. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_gasoline_editions.gif)

## Lesson 2: a missing row is not a losing year

### Three missing rows bound the count

Chan counts 19 profitable gasoline years of 21, from 1995 to 2015. The files give this:

```math
\begin{array}{l|r}
\text{Gasoline, 1995 to 2015} & \text{Years} \\ \hline
\text{Profitable} & 16 \\
\text{Losing, 2009 and 2012} & 2 \\
\text{No row, 1997 to 1999} & 3 \\ \hline
\text{Total} & 21
\end{array}
```

EIA’s New York Harbor file holds no row on 14 April 1997, the entry date that year, or on 24 April 1998 and 23 April 1999, the exit dates those years, though each was a trading day. The run counts such a year neither as a profit nor as a loss, so the files bound Chan’s count between 16 and 19.

![“Three missing rows leave a range, not a count”, drawn slowly stroke by stroke. A year axis labelled only at “1995” and “2015” carries a blue dot for each profitable gasoline year and an orange cross at 2009 and 2012. A grey span under 1997 to 1999, which have no mark, reads “no row: a profit or a loss?”. Below, a scale of profitable years is labelled “15”, “16”, “17”, “18”, “19” and “20”. A purple bracket over 16 to 19 reads “the files allow 16 to 19”, and a black mark at 19, the bracket’s top end, reads “Chan: 19”. A caption names the scale as “profitable years of 21”, and a note in the lower right names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_gap_range.gif)

### Chan’s 19 needs all three missing years

The losses say more than the gaps. Chan’s 19 of 21 allows exactly 2 losing years, and the files show exactly 2, in 2009 and 2012. If Chan’s data agrees with EIA’s on the other 18 years, his 19 holds only if all 3 missing years were profitable in his data. No source here covers the contract in those years.

![“Chan’s 19 needs all three gaps to be profits”, drawn slowly stroke by stroke as two bars of 21 years. The upper bar is a blue box of “19 profits” and an orange box, labelled “Chan”. The lower bar is a blue box of “16 profits”, a dashed grey box and an orange box, labelled “EIA”. The upper orange box reads “2 losses” and the lower one “2009, 2012”, so both bars end in the same two losses. The dashed box, “no row”, sits under the last three of Chan’s profits, and a purple arrow points at it: “1997 to 1999 must all be profits for Chan’s 19”. A note in the lower right names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_chan_needs_gaps.gif)

### A fill cannot call the three years either

#### Two ways to fill a gap

Interpolating, which here means drawing a guess from the neighboring days’ prices, would turn a gap into a guess, and the guess would decide the count it is meant to check.

The files do hold something on each missing day. EIA’s file for the second contract out, which holds June while May is the first, has a row on all three dates. So the run tried two fills and measured how far each can be trusted.

##### Fill 1, a straight line

Fill 1 draws a straight line between the May rows on either side of the gap.

![“Interpolating turns a gap into a guess”, drawn slowly stroke by stroke. Black dots mark the May gasoline contract’s settlements one trading day apart along an axis labelled “gasoline, May contract, April 1997”, with no dot on the day labelled “Apr 14, the entry: no row”. The file misses April 11, 16 and 18 too, so those days have no dot either. A dashed grey line marks the “exit price 62.5¢”. A purple straight line joins the dots either side of the gap, and a purple dot on it at the gap is the “straight-line guess 61.6¢”. Around the guess a band of close strokes runs from “63.5¢” down to “59.7¢”, “one typical miss either side”. The dashed exit line splits it into an orange part above, “entry here: a loss”, and a blue part below, “entry here: a profit”. The guess sits in the blue part, and the band reaches into the orange. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_interpolation_guess.gif)

##### Fill 2, June’s move

Fill 2 takes May’s last known price and moves it by June’s change since that day, because the two contracts move almost together.

![“Fill 2 carries June’s move across the gap”, drawn slowly stroke by stroke. Black dots are the May gasoline contract’s settlements and grey rings the June contract’s, one trading day apart from April 7 to April 17, 1997, named “May” and “June” at their first marks, with a caption “dot: May   ring: June” and a note “gasoline”. May has no dot on the day labelled “Apr 14, the entry: no May row”, nor on April 11 or 16. A grey arrow carries June from April 8, the last day both files hold, to April 14, labelled “June rose 0.9¢”, and a purple arrow of the same rise starts at May’s April 8 price and ends on a purple dot, “same rise on May: guess 62.1¢”. A dashed grey line marks the “exit price 62.5¢”. Around the guess a band of close strokes runs from “63.0¢” down to “61.2¢”, “fill 2’s typical miss either side”. The exit line splits it into an orange part above, “entry here: a loss”, and a blue part below, “entry here: a profit”. The guess sits in the blue part just under the line, and the band reaches into the orange. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_june_move_fill.gif)

#### How far each fill misses

To measure a fill, the run hid April days from 1994 to 2005 whose May price the file does hold, each with the rows around it the same number of trading days away as in the real gap. It filled them and took the root mean square error, the typical size of a miss.

Not every April day can serve as a test. A test day needs prices at the same distances as the real gap, and each missing year’s gap sits at its own distances:

```math
\small\begin{array}{l|c|c|c}
\text{Missing year} & 1997 & 1998 & 1999 \\ \hline
\text{Missing price} & \text{entry} & \text{exit} & \text{exit} \\
\text{Missing day} & \text{14 Apr} & \text{24 Apr} & \text{23 Apr} \\
\text{Fill 2 starts} & \text{8 Apr} & \text{21 Apr} & \text{21 Apr} \\
\text{Days back} & 4 & 3 & 2 \\
\text{Test days} & 80 & 90 & 102
\end{array}
```

A pattern that reaches back fewer days fits more April days, so 1998 and 1999 have more test days than 1997. For 1997, 247 April trading days narrow to 80:

![“Which April days can test a fill”, drawn slowly stroke by stroke as four bars drawn to scale, each shorter than the one above. The first, “April trading days, 1994 to 2005”, reads “247”. The second, “the pattern fits inside April”, reads “187”, beside “−60: fall outside April”. The third, “May has all four prices”, reads “108”, beside “−79: lack a May price”. The fourth, in purple, “June has both of fill 2’s prices”, reads “80”, beside “−28: lack a June price”. A caption reads “1997’s gap: rows 2 days back and 1 ahead, fill 2 starts 4 back”, and a note names the trade as “gasoline, May contract”. Most of the days lost lack a price in EIA’s files. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_test_days.gif)

Both fills guess a profit in all three years, and every move is smaller than its fill’s typical miss. Fill 2 gives moves of +0.4, +0.5 and +0.6 cents a gallon and misses by 0.89, 0.76 and 0.65. Fill 1 does no better than fill 2, with moves between 0.1 and 0.8 of its own typical miss.

Fill 2’s misses also lean one way. On the test days it guessed May too low by 0.26, 0.21 and 0.20 cents on average, each between 2.7 and 3.2 standard errors from zero.

![“One set of misses, three numbers”, drawn slowly stroke by stroke. Fill 2’s misses on the 80 test days of 1997’s pattern are stacked as dots on a scale labelled “-2”, “-1”, “0”, “+1” and “+2” in “cents a gallon”, with a dashed line at zero, and a caption reads “dot: one test day’s miss, 80 days”. More of the dots sit right of zero than left, and a few reach past +2. Above them a grey bar spans one typical miss either side of zero, “typical miss ±0.89, around zero”, and a black bar with a purple dot at its middle spans the spread either side of the average, “average +0.26, spread ±0.86”, shifted right of zero by the lean. A note names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_three_numbers.gif)

The test days overlap, though, and days in one April share its price moves, so the true standard errors are larger and the lean is suggestive rather than settled.

![“Twelve Aprils, eight lean low”, drawn slowly stroke by stroke. Each April from 1994 to 2005 has a row labelled with its year and its number of test days, “1994 (5)”, “1995 (5)”, “1996 (8)”, “1997 (3)”, “1998 (1)”, “1999 (2)”, “2000 (8)”, “2001 (9)”, “2002 (11)”, “2003 (8)”, “2004 (15)” and “2005 (5)”, and a bar from a dashed zero line to that April’s average miss. Eight bars, in purple, run right of zero, and the longest, for 1996, 2001 and 2003, carry most of the lean. The other four, in grey, sit left of zero or on it. Captions read “left: May guessed too high”, “right: too low” and “(n): test days that April”, a summary reads “8 of 12 Aprils lean low”, and a note names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_april_leans.gif)

Correcting each guess by its average miss, and measuring the spread of the misses around that average, which is the typical miss with the lean taken out, gives each year a corrected move and a chance of a profit, in cents a gallon:

```math
\small\begin{array}{l|r|r|r}
\text{Fill 2} & 1997 & 1998 & 1999 \\ \hline
\text{Move with the guess} & +0.4 & +0.5 & +0.6 \\
\text{Average miss} & +0.26 & +0.21 & +0.20 \\
\text{Corrected move} & +0.14 & +0.71 & +0.80 \\
\text{Spread of misses} & 0.86 & 0.74 & 0.62 \\
\text{Chance of profit} & 57\% & 83\% & 90\%
\end{array}
```

#### From a miss to a chance of a profit

The chances come from a model of the miss. Write the missing price as fill 2’s guess plus an unknown miss `e`, and suppose `e` is normal, with a mean `b` equal to fill 2’s average miss and a standard deviation `σ` equal to the spread:

```math
\begin{gathered}
\text{true price} = \text{guess} + e \\
e \sim N(b,\ \sigma^{2})
\end{gathered}
```

A year’s move is its exit price minus its entry price:

```math
\text{move} = \text{exit} - \text{entry}
```

Call the move with the guess in place `m`. In 1997 the missing price is the entry:

```math
\begin{aligned}
\text{true move} &= \text{exit} - (\text{guess} + e) \\
&= \underbrace{(\text{exit} - \text{guess})}_{m} - e \\
&= m - e
\end{aligned}
```

In 1998 and 1999 it is the exit:

```math
\begin{aligned}
\text{true move} &= (\text{guess} + e) - \text{entry} \\
&= \underbrace{(\text{guess} - \text{entry})}_{m} + e \\
&= m + e
\end{aligned}
```

![“A miss at the entry subtracts, at the exit it adds”, drawn slowly stroke by stroke in two panels split by a dashed line. On the left, “1997: the entry is missing”, a black dot marks the “exit 62.5¢”, a purple dot marks fill 2’s “guess 62.1¢” for the entry, and a grey arrow lifts the guess by “e = 0.26¢”, written to its left, to a ring, “guess + e”. Dashed guides run from the three prices to two brackets: a purple one from the guess up to the exit, labelled “m”, and a black one from the ring up to the exit, labelled “m − e”, which is shorter. On the right, “1998: the exit is missing”, a black dot marks the “entry 49.8¢”, a purple dot marks the “guess 50.3¢” for the exit, and a grey arrow lifts it by “e = 0.21¢” to a ring, “guess + e”. The purple bracket from the entry up to the guess is labelled “m”, and the black one from the entry up to the ring, labelled “m + e”, is longer. A caption reads “e drawn at fill 2’s average miss”, and a note names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_miss_sign.gif)

So a miss above the guess lowers an entry’s move and raises an exit’s. The sketch marks each arrow with `e` at that year’s average miss `b`, 0.26 cents for 1997 and 0.21 for 1998. Putting `b` in place of `e` gives each case its corrected move `c`:

```math
\begin{array}{l|c|c}
 & \text{True move} & c \\ \hline
\text{Entry, 1997} & m - e & m - b \\
\text{Exit, 1998, 1999} & m + e & m + b
\end{array}
```

Both cases give the same chance of a profit. `Φ(z)` is the share of a standard normal curve that lies below `z`:

```math
P(\text{profit}) = \Phi\left(\frac{c}{\sigma}\right)
```

For 1997, `m` is 0.4 cents, `b` is 0.26 and `σ` is 0.86, so `c` is 0.14 and the chance is Φ(0.17), or 57%. If the three misses are also independent of each other, the three chances multiply:

```math
0.566 \times 0.832 \times 0.900 = 0.424
```

#### What the chance rests on

So the chance that all three years were profits, which Chan’s 19 needs, is 42%. The correction barely moves that figure, but it moves the years apart: 1997 is close to a coin flip, and 1999 reaches 90%, still short of 95%. The run tested neither remaining assumption, that the misses are normal and that they are independent. Heavier tails than a normal curve would raise each chance rather than lower it, because a curve with heavier tails and the same spread puts more of its misses near the average. A fill that misses the same way every April could move the figure either way.

![“Each corrected move against fill 2’s spread”, drawn slowly stroke by stroke. A dashed grey line at zero divides “loss” on the left from “profit” on the right. Three rows follow, each with its σ above its bar: “σ = 0.86” for “1997”, with “57%”, then “σ = 0.74” for “1998”, with “83%”, then “σ = 0.62” for “1999”, with “90%”. In each row a purple dot right of zero marks the year’s move with fill 2’s guess corrected by its average miss, and a black bar of one spread either side. The bar for 1997 reaches well across zero, the bar for 1998 only just reaches past it, and the bar for 1999 stops just short of it. A scale below reads “-1” and “+1” in “cents a gallon”, and the percentages sit under “chance of profit”, each computed as if fill 2’s misses are normal around their average. Captions read “dot: the corrected move” and “bar: σ, fill 2’s spread, either side”, and a note under the scale names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_fill_misses.gif)

## Lesson 3: a trade chosen after looking at the history is tested by the years after the book

Chan picked both trades by studying past prices, and both rules name exact days. That invites **data-snooping bias**, Chan’s own name for it: searching the past for a rule that worked picks up chance patterns along with real ones, so the winning rule looks better on the years it was chosen from than it will on new ones. Only the years after the book test it. The book’s years end where Chan’s counts end: 2015 for gasoline, and 2008 for natural gas under Lesson 1’s reading. Natural gas starts in 1994, the first year the files hold a whole trade.

Natural gas went from winning 15 of 15 years, with a mean return of 10.6%, to winning 7 of 15 with a mean near zero. Chan says as much: the trade “didn’t hold up as well out-of-sample” (p. 185), meaning in years he did not use to choose the rule, though he prints no figure. Its drawdown before 2009 came inside 2002’s trade, which rose 48% before giving back 22 points and ending 40% up.

For gasoline, Chan marks the last 9 of his 21 years, 2007 to 2015, as out of sample. The trade won 7 of those 9, and both of its losing years fall among them. From 2016 to 2023 it won 3 of 8, and natural gas won 4 of the same 8.

![Two panels of bar charts, one bar per year showing the change in settlement price from entry to exit. The upper panel is gasoline, the May contract from the close of April 13 to the close of April 25, from 1995 to 2023 in dollars a gallon. Its years 1997, 1998 and 1999 are empty slots labelled “no row”. A dashed line after 2015 divides 1995 to 2015, 16 of 21 profitable and 3 with no row, from 2016 to 2023, 3 of 8 profitable. Bars before the line are mostly small and positive, with losses in 2009 and 2012, and five of the eight after it are losses. The lower panel is natural gas, the June contract from the close of February 25 to the close of April 15, from 1994 to 2023 in dollars per million Btu. A dashed line after 2008 divides 1994 to 2008, 15 of 15 profitable, from 2009 to 2023, 7 of 15 profitable. Every bar before the line is positive. After it, 8 years are losses and 7 are gains, in no regular order, including one gain near three dollars in 2022. Marks along the foot of each panel point up for each profitable year and down for each losing one.](../docs/figures/commodity_seasonals_years.png)

*Every year of both trades. Each dashed line is where the book’s years end, and the marks along each foot give every year’s sign, including years too small to see as bars.*

The book’s years include the years Chan chose each rule on, so the drop after the book can overstate how far either trade weakened.

## Lesson 4: one trade a year leaves too few results to grade a split

Each trade happens once a year, so 15 years give 15 results, about what a strategy that trades every day collects in three weeks. Two calculations show how far that few results can be trusted.

### How far a Sharpe ratio can stray

A standard error is the amount an estimate typically strays from the true value. For a Sharpe ratio estimated from `n` independent returns, Lo (2002) gives:

```math
\text{SE} \approx \sqrt{\frac{1 + \text{SR}^2 / 2}{n}}
```

Trades a year apart share no days, so treating them as independent is close to right. Natural gas before 2009 has a Sharpe ratio of 1.0 over 15 years:

```math
\begin{aligned}
\text{SE} &\approx \sqrt{\frac{1 + 1.0^2 / 2}{15}} = 0.32 \\
95\%\ \text{range} &= 1.0 \pm 1.96 \times 0.32 \\
&= 0.4 \text{ to } 1.6
\end{aligned}
```

For the four Sharpe ratios in the returns table at the top of the post, each trade before and after the book, the standard error runs from 0.3 to 0.4, so each could plausibly sit 0.5 to 0.7 higher or lower.

![“How far each Sharpe ratio can stray”, drawn slowly stroke by stroke. A dashed grey line at zero divides “loses” on the left from “earns” on the right. Four rows follow, each labelled with its trade and years: “natural gas, 1994 to 2008”, with a purple dot at “1.0”, then “natural gas, 2009 to 2023” at “0.0”, then “gasoline, 1995 to 2015” at “0.8”, then “gasoline, 2016 to 2023” at “-0.4”. Each dot sits on a black bar reaching 1.96 standard errors either side. The first bar runs from about 0.4 to 1.6 and the third stays right of zero, while the bars of both periods after the book reach across the zero line. A scale along the foot is marked “-1”, “+1” and “+2” and labelled “Sharpe ratio”. Captions read “dot: the Sharpe ratio” and “bar: 1.96 standard errors either side”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_sharpe_ranges.gif)

### Whether the mean return changed

The 95% range for a mean return from `n` results, with standard deviation `s`, uses Student’s t, which widens the range to allow for estimating `s` from so few:

```math
\bar r \pm t_{n-1} \times \frac{s}{\sqrt{n}}
```

![“Fewer results, a wider range”, drawn slowly stroke by stroke. Four bars rise from a grey base, each labelled with its height: “2.36” over “8 results”, “2.14” over “15 results”, “2.05” over “30 results” and “1.96” over “many”. A dashed grey line runs across at the normal curve’s value, labelled “normal, 1.96”, and the fewer the results, the higher a bar stands above it. A caption reads “95% multiplier from Student’s t”. The first two bars are purple, and a note reads “purple: the later periods’ 8 and 15 years”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_t_multiplier.gif)

Natural gas after 2008 averaged −0.4% a year with a standard deviation of 21.6% over 15 years, and `t` for 14 degrees of freedom is 2.14:

```math
\begin{aligned}
&-0.4\% \pm 2.14 \times \frac{21.6\%}{\sqrt{15}} \\
&= -0.4\% \pm 12.0\%
\end{aligned}
```

![“Where ±12% comes from”, drawn slowly stroke by stroke. A dashed grey line comes first, marking “the later mean, -0.4%”, and three bars grow from it. The first, black, is “spread s = 21.6%”. The second, black and about a quarter as long, is “s / √15 = 5.6%”. The third, purple, is “× 2.14 = 12.0%”. A short dashed grey line across the purple bar marks “the earlier mean, 11.0 points higher”, and the purple bar reaches past it, so the range around the later mean holds the earlier one. A note in the upper right names the trade as “natural gas, June contract, 2009 to 2023”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_half_width.gif)

That range, −12% to +12%, still holds the +10.6% natural gas earned before 2009. So 15 years cannot tell a trade that weakened from one that had a bad run. Gasoline after 2015 averaged −1.9% with a standard deviation of 4.8% over 8 years, and `t` for 7 degrees of freedom is 2.36:

```math
\begin{aligned}
&-1.9\% \pm 2.36 \times \frac{4.8\%}{\sqrt{8}} \\
&= -1.9\% \pm 4.0\%
\end{aligned}
```

That range, −6% to +2%, leaves out the +3.2% gasoline earned before.

![“One range holds the earlier mean, one does not”, drawn slowly stroke by stroke. A dashed grey line marks “0%”. Four rows follow, each with a black bar of its 95% range, a purple dot at its mean, and the mean written at the right edge: “natural gas, 1994 to 2008” at “+10.6%”, “natural gas, 2009 to 2023” at “-0.4%”, “gasoline, 1995 to 2015” at “+3.2%” and “gasoline, 2016 to 2023” at “-1.9%”. A dashed grey line drops from each trade’s earlier mean past its later bar. Natural gas’s lands inside the later range, and gasoline’s lands just past its right end. A scale along the foot is marked “-10%”, “+10%” and “+20%” and labelled “mean yearly return”. Captions read “dot: the mean” and “bar: 95% range   dashed: the earlier mean”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_mean_ranges.gif)

### Whether the typical year changed

Two tests compare the periods directly, and they ask different questions.

Welch’s t-test compares the average yearly returns. It lets each period keep its own spread, which matters because natural gas’s spread doubled after 2008.

The Mann-Whitney test ignores how large each return was. It pairs every year before the split with every year after and records which one returned more. If nothing had changed, the earlier year would win about half the pairs. For gasoline the earlier year won 117 of 144 pairs, where chance would give about 72. For natural gas the earlier year won 177 of 225 pairs, where chance would give about 112.

Each test gives the chance that luck alone would produce a difference this large if the trade had worked equally well in both periods. A small chance means luck explains the difference poorly. The usual line is 5%, and a chance below it counts as evidence that the trade changed:

```math
\small\begin{array}{l|r|r}
 & \text{Welch} & \text{Mann-Whitney} \\
 & \text{(averages)} & \text{(pairs)} \\ \hline
\text{Gasoline} & 2.3\% & 1.1\% \\
\text{Natural gas} & 9.2\% & 0.8\%
\end{array}
```

Gasoline’s fall clears the line on both. Natural gas splits on one year. Its typical year clearly got worse, from 15 wins in 15 years before 2009 to 7 in 15 after. But 2022’s +64% lifts its average after 2008 to −0.4%, close enough to what came before that Welch’s chance, 9.2%, sits above the line. The ranks still see the change, because 2022 counts as 15 pairs won however large its gain. Without 2022 the average after 2008 is −5.0%, and Welch’s chance falls to 0.1%. That year was a real gain that a trader holding every year would have collected, so it stays in the record. Neither test was chosen before the numbers were seen, so the post reports both rather than the one that reads better.

![“One year moves the mean, not the ranks”, drawn slowly stroke by stroke. A grey axis carries a dashed line at “0%”, and a caption reads “returns, 2009 to 2023”. Natural gas’s 15 returns from 2009 to 2023 sit on it as dots at their true values, stacked where they would touch, orange left of zero for the 8 losses and blue right of it for the 7 gains. Two gains sit so close to the line that a note names them, “2014 and 2018: just above 0%”, and one blue dot sits far to the right, labelled “2022: +64%”. A black tick under the axis marks the “mean -0.4%”, and a purple tick left of it marks the mean “without 2022: -5.0%”. Below, a grey line carries all 30 years from 1994 to 2023 ranked from worst to best, with black dots above it for “1994 to 2008” and purple dots below it for “2009 to 2023”. The nine worst ranks all belong to years after 2008, and 2022 takes the top rank on the right. The ends are marked “worst” and “best: 2022”, and a caption reads “ranked worst to best, 2022 is the top rank however large its gain”. A note in the upper right names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_one_year.gif)

Chan makes the same point and offers a check. A trade that happens once a year produces few results, he writes, so data-snooping bias is hard to rule out. He suggests trying somewhat different entry and exit dates to see whether the profits hold (p. 186). The run did not try it. Varying the dates until some version works is a search across many trades, and a fair search needs a list of variants fixed in advance, a bar that rises with the number tried, and years the search never sees.

## Lesson 5: reading one named contract from files numbered by expiry needs a calendar checked outside the files

EIA’s files hold contract 1, contract 2 and so on, not the May or June contract, so every trade date needs the file that holds Chan’s contract.

For gasoline that is always contract 1. The April contract stops trading on the last trading day of March, and the May contract trades until the last trading day of April. Natural gas contracts stop trading three trading days before their delivery month begins. So the June contract is contract 4 on February 25 if the March contract has not yet expired, contract 3 if it has, and contract 2 by mid-April.

![“Which file holds the June contract”, drawn slowly stroke by stroke, twice on one calendar from late February to the start of May. Each time, four stacked bars labelled “March”, “April”, “May” and “June” stand for the natural gas contracts, each ending at its last trading day, with June’s bar in purple running off the right. The upper set is “2008”, where March’s bar ends on February 27, marked “March still trading”. A dashed line at the entry crosses all four bars, labelled “June is contract 4 on Feb 25”, and a dashed line at the exit crosses May and June, labelled “contract 2 on Apr 15”. The lower set, with its own “March”, “April”, “May” and “June”, is “2006”, where March’s bar ends on February 24, marked “March has expired”. Its entry line crosses only April, May and June, labelled “June is contract 3 on Feb 27”, and its exit line crosses May and June, labelled “contract 2 on Apr 13”. It closes on “June’s number is how many bars each line crosses”, and the finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_june_file.gif)

*In 2006, February 25 fell on a Saturday, so the trade entered on Monday the 27th, after March had expired. April 15 was a Saturday and the 14th was Good Friday, so the exit moved back to the 13th.*

### Three checks of the expiry rule

Because the June contract moves between files, the expiry rule is part of the result, so the run checks it three ways.

#### Against the exchange’s own dates

Massive, a market data vendor, records each contract’s last trading day as the exchange set it. For all 40 contracts it records, March to June of every year from 2017 to 2026, the rule gives the same day. Massive’s records begin in 2017, so the years before rest on the next check.

#### Against the files’ own handovers

When a contract expires, every later contract moves up one number, so each file’s price should carry on from the next file’s price the day before. Before mid-1997 the handovers show contracts stopping five or six trading days before delivery rather than three, so for those years the run follows the handovers. That moves the 1996 and 1997 entries from contract 4 to contract 3, and both years are profitable on either.

![“A handover shows when March stopped”, drawn slowly stroke by stroke. Two rows of dots run across the trading days from mid-February to March 1, 1996, one dot a trading day, the settlements in the “contract-1 file” in black and in the “contract-2 file” in grey. A purple arrow runs from the contract-2 file’s Feb 23 price to the contract-1 file’s next price, labelled “Feb 26: file 1 picks up file 2’s price”. A purple dashed line between Feb 23 and Feb 26 marks “March stopped Feb 23, 5 trading days before delivery”, and a grey dashed line two trading days later marks “3-day rule: here”, where a three-day rule would have put the handover. A note reads “natural gas, March contract, Feb 1996”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_handover.gif)

Over every natural gas contract delivered from February 1994 to April 2024, the handover falls on the rule’s day for 298 of the 316 expiries the files hold rows to check. Moved a day earlier or later, the rule fits only 38 and 16 of 324.

![“Which years each check reaches”, drawn slowly stroke by stroke. A year axis is marked “1994”, “2000”, “2010”, “2017” and “2026”. A black bar runs from 1994 to 2024, labelled “the files’ handovers: 298 of 316 expiries fit”. A purple bar runs from 2017 to 2026, labelled “the exchange’s dates: 40 of 40 March to June contracts”. A dashed grey line at 2017, where Massive’s records begin, marks “before 2017, the files alone”. A note reads “natural gas, contracts’ last trading days”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_check_coverage.gif)

The other 47 expiries cannot be checked this way, because a file lacks a row on the expiry day or the day after, 40 of them between 1997 and 2005. The 18 that do not fit are mostly close calls. 15 fail by under 9 cents, where neighbouring contracts trade so close together that a handover and no handover look alike, and one, March 2023, is a day the exchange’s own date confirms. A rule wrong by a day would matter only where it moves which file holds June on a trade date. That is true of 4 of the 18, all March contracts at an entry, and of none of the 47, and in those 4 years reading the other file turns none from a profit to a loss.

#### Against the edge cases

In 10 of the 30 years, the entry date falls on the March contract’s last trading day. A contract still trades on its own last day, so the run reads June as contract 4 then. Reading the contract-3 file instead turns no year from a profit to a loss, or back.

![“2018: entry on March’s own last day”, drawn slowly stroke by stroke. Four bars stand for the natural gas contracts, “March”, “April” and “May” in black and “June” in purple, against late February 2018. March’s bar ends at its last trading day, and the April, May and June bars run off the right. A dashed grey line marks the “entry, close of Feb 26”, exactly where March’s bar ends, and a note beside it reads “March’s last day: it still trades at this close”. The line reaches all four bars, so “June is contract 4”. Notes read “10 of 30 years enter on March’s last day.” and “Reading the contract-3 file instead turns no year from a profit to a loss.”, and a note names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_edge_day.gif)

### The calendar comes from the exchange’s rules, not the files’ rows

The run computes its own calendar of trading days rather than reading one from the files, because a row in the files does not show that the exchange was open. On every exchange holiday from January 2018 to November 2019, the natural gas files hold a row that repeats the previous trading day’s settlement, and in other years almost none. Of NYMEX’s holidays, only Good Friday can land on a trade date, and it moved six trade dates between 1994 and 2023.

![“A row in the file is not a trading day”, drawn slowly stroke by stroke. The top row, “2018”, numbers its days “21”, “22”, “23”, “24” and “25”, where an orange dot is labelled “Dec 25: closed, row repeats Dec 24’s 3.467”, then “26”, “27” and “28”. A black dot stands on each other day the contract-1 file holds a row, so the weekend of the 22nd and 23rd has none. The bottom row, “2016”, numbers “21”, “22”, “23”, “24”, “25” and “26”, labelled “Dec 26: closed, no row”, then “27” and “28”, and its weekend of the 24th and 25th and the closed 26th have no dot. A caption reads “dot: a row in the contract-1 file   no dot: a weekend or a closed day”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_holiday_rows.gif)

The same map from dates to contracts serves Chan’s calendar spreads, which [the calendar spreads post](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) tests on the same files.

## What this replication cannot say

Three questions are beyond it, besides the gaps, the start year and edition, and the nearby dates that the lessons name.

1. **Whether Chan read the same contracts.** His sidebar names RB, the symbol RBOB trades under. Before RBOB began trading in October 2005, his series presumably held the older contract, as the run assumes. Chan does not name his data vendor.
2. **Whether either trade pays after costs.** The run charges no commission and no slippage, the gap between the settlement price and the price an order would actually get.
3. **Any year after 2023.** EIA’s RBOB and natural gas files end on 5 April 2024, before either trade’s 2024 exit date.

## What this means for a trader

Four habits follow from the first four lessons.

1. **Ask a consecutive count where it starts and when it was written.** The same files give 13, 14 or 15 consecutive years for natural gas, depending on both.
2. **Read a missing year as missing.** Three gaps in one file leave Chan’s gasoline count anywhere between 16 and 19, and filling them with a neighboring day would decide the answer instead of checking it. Even the closer of the two fills the run measured misses by more than each year’s raw move, and correcting its lean still leaves no year at 95%.
3. **Judge a seasonal trade on the years after it was chosen.** Natural gas won every year through 2008 with a Sharpe ratio of 1.0, and averaged a loss of 0.4% a year after.
4. **Count the results behind a Sharpe ratio, and ask which test it rests on.** Fifteen yearly trades leave a standard error near 0.3, and one year, 2022, decides whether natural gas’s average fell.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Released in November 2008.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 175 and 183 to 186. Page numbers here are the revised edition’s. The replication log cites the passages on pp. 183 to 185 by Kindle location, 4529 to 4632.
- Lo, A. W. (2002). The statistics of Sharpe ratios. *Financial Analysts Journal*, 58(4), 36 to 52.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for New York Harbor regular gasoline, RBOB gasoline and Henry Hub natural gas, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the two trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_whiteboard.py), with the checks behind [the trades’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_whiteboard.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
