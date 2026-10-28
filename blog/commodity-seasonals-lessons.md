# Two commodity seasonals show an edge that has faded after being published

*Gasoline’s seasonality has faded and natural gas is saved by one good year, but not enough data to be confident.*

## Why test a strategy published as alive

A reader might put money on a claim that a trade still pays, so the record behind the claim is worth checking.

Ernest Chan’s *Quantitative Trading* makes that claim for seasonal trades in commodity futures, trades that buy and sell on the same calendar dates every year. Much of the seasonality in equity markets, he writes, has weakened or disappeared, while some commodity seasonals are still profitable (Chan, 2021, p. 175). He calls them “alive and well”, perhaps because the demand behind them is a real economic need rather than speculation (p. 183). [The companion post on the equity seasonals](https://baowebdev.substack.com/p/two-equity-seasonals-show-no-edge) tested the equity half of that claim. This one tests the commodity half.

Chan gives two trades, each with a count of profitable years.

1. **Gasoline.** Buy the May contract at the close of April 13 and sell it at the close of April 25, ahead of the summer driving season. Chan counts 19 profitable years of 21, from 1995 to 2015.
2. **Natural gas.** Buy the June contract at the close of February 25 and sell it on April 15, as power generators buy ahead of the air-conditioning season. Chan counts 13 consecutive profitable years in the main text and 14 in a sidebar.

![“Two trades on one calendar”, drawn slowly stroke by stroke. A grey calendar axis is marked “Feb”, “Mar”, “Apr” and “May”. A long black bar runs from February 25 to April 15, labelled “natural gas: buy June contract Feb 25, sell Apr 15”, with a grey note on the left, “demand: air conditioning”, and a purple caption under the bar, “Chan: 13 years in a row, 14 in the sidebar”. A short black bar below it runs from April 13 to April 25, with its label on its left, “gasoline: buy May contract Apr 13, sell Apr 25”, a grey note at the far left, “demand: summer driving”, and a purple caption under the label, “Chan: 19 of 21 years, 1995 to 2015”. The natural gas trade stays open for about seven weeks and the gasoline trade for under two, and both are open from April 13 to April 15. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_two_trades.gif)

### What the record shows

Both trades ran on the free settlement prices that the US Energy Information Administration (EIA) publishes for futures traded on the New York Mercantile Exchange (NYMEX). Three results came out.

1. **Natural gas reproduces both of Chan’s counts** if both were written for the book’s first edition, released in November 2008, and count from 1995.
2. **Gasoline matches Chan’s count in every year the files have both prices for.** They show 2 losing years, the most his count allows, and 3 years each missing the entry or the exit price.
3. **Both trades averaged a loss after the years Chan counted.** Under Lesson 1’s reading, both rules were in print from the book’s first edition, so all of those later years come after publication.

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

![“Years won, in the book’s years and after”, drawn slowly stroke by stroke. Two rows share a year axis from 1994 to 2023. The upper row, “natural gas, June contract”, has a blue dot for each profitable year and a vermilion cross for each loss, and a dashed grey line after 2008 splits it into “15 of 15 won” on the left and, in purple, “7 of 15 won” on the right. Every year before the line is a dot, and all eight crosses fall after it. The lower row, “gasoline, May contract”, starts in 1995, and a dashed grey line after 2015 splits it into “16 of 18 won” and, in purple, “3 of 8 won”. Before its line the crosses are 2009 and 2012, and after it five of the eight years are crosses. A grey span under 1997 to 1999, which have no mark, reads “no row”. The axis is labelled “1994”, “2008”, “2015” and “2023”, and captions read “dot: a profitable year   x: a loss” and “dashed: where the book’s years end”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_after_book.gif)

A year’s return is the change in the contract’s price over its entry price, before costs. The Sharpe ratio divides the mean yearly return by the standard deviation of the yearly returns. The drawdown is the largest fall from a peak in the running total of yearly returns. The post’s code marks that total on every trading day the files hold a price, so the drawdown counts a fall inside a trade that still ended the year ahead. Natural gas’s 22% before 2009 is one: it came inside 2002’s trade, which rose 48%, gave back 22 points, then recovered to end 40% up. Each year stakes one contract’s entry value, so returns and drawdowns are shares of one stake.

![“A 22-point fall inside a winning year”, drawn slowly stroke by stroke. A dashed grey line marks “0%”. A black line traces natural gas’s 2002 trade as its return over its entry price on each day the files hold a price from “Feb 25” to “Apr 15”, every trading day but April 9, and a caption reads “return over the entry price, marked each day the files hold a price”. The line dips just below zero in its first week, climbs to a black dot at its high, “peak: +48%”, then falls. Dashed grey guides run right from the peak and from the lowest point after it to a purple bracket between them, labelled “drawdown:” and “22 points”. The line then climbs again to a black dot at the exit, “exit: +40%” and “a profitable year”, which sits between the two guides, so the year ended ahead after falling 22 points inside it. A note right of the dates names the trade as “natural gas, June contract, 2002”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_drawdown_2002.gif)

Gasoline’s 1995 to 2015 leaves out the 3 years each missing one trade date’s price. Natural gas’s years start in 1994, the first year the files hold a whole trade. Lesson 1 reads Chan’s counts as starting a year later, in 1995. Nobody set a pass mark for the years after the book before computing them, so the split describes the record rather than grading Chan’s claim.

Each trade happens once a year, so each of the table’s four periods, two for each trade, rests on only 8 to 18 yearly results. Lesson 4 works out what so few results can show. Gasoline’s fall after the book stands out from its year-to-year noise. Natural gas’s typical year got worse, but its yearly returns vary too widely to tell their average after the book apart from the average before. One year decides that. Without 2022, whose trade gained 64%, natural gas’s average after the book would be −5.0% rather than −0.4%, and the fall would stand out. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two trades and the files

A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date. Each delivery month trades as its own contract, so the May and June gasoline contracts have different prices. Each trading day ends with a **settlement price** for every contract, the exchange’s official close, and both trades buy and sell at it. When a trade date is not a trading day, each trade enters on the next one and exits on the previous one (pp. 184 and 185). The run, this post’s code, exits the natural gas trade at the close. Further work lists every parameter of the two trades and what varying each would take. A year is **profitable** when the exit settlement is strictly above the entry settlement.

Every passage quoted here is in the revised edition of 2021. The first edition matters to Lesson 1. Wiley released it in November 2008 and dated it 2009.

### The files from EIA, numbered by expiry

EIA publishes settlement prices for the nearest four contracts of each product. It numbers them by expiry rather than by month: contract 1 is whichever contract stops trading next, and each number has its own file. So the run has to work out which file holds the May or June contract on each trade date, which Lesson 5 comes back to. The two trades read five files covering three products, all downloaded on 2 October 2026:

1. New York Harbor regular gasoline, contract 1, through 2005.
2. RBOB gasoline, contract 1, from 2006. RBOB replaced the New York Harbor contract and began trading in October 2005.
3. Henry Hub natural gas, contracts 2, 3 and 4, one file each.

Lesson 2’s second way of guessing the missing gasoline prices also reads New York Harbor’s contract 2 file. Lesson 5 reads natural gas’s contract 1 file as well, to check the expiry rule against the files’ own prices and to count holiday rows. Both files come from the same download.

## Lesson 1: ask a consecutive count where it starts and which edition wrote it

The main text says the natural gas trade “has been profitable for 13 consecutive years as of this writing” (p. 185). The sidebar says 14 (p. 185). Neither says which year its streak ends in, and either may be text kept from the first edition.

The natural gas files first hold a whole trade in 1994. Every year from 1994 to 2008 is profitable, and 2009 is a loss. So where a streak ends depends on where the count starts:

```math
\begin{array}{l|r|r}
\text{Streak ending in} & \text{From 1995} & \text{From 1994} \\ \hline
2007 & 13 & 14 \\
2008 & 14 & 15
\end{array}
```

Counted from 1995, the main text’s 13 is the streak ending in 2007 and the sidebar’s 14 is the streak ending in 2008. Each natural gas trade closes by mid-April, so both streaks end before the first edition’s release in November 2008. Both counts reproduce if they were written for that edition. The files settle half of that reading.

1. **They rule out the revised edition.** Because 2009 is a loss, a streak of 13 or more counted from 1995 can end only in 2007 or 2008, more than a decade before the revised edition of 2021.
2. **They cannot pick the start year.** 1994 is profitable too. Counted from 1994, the streaks of 13 and 14 end in 2006 and 2007 instead. Only Chan’s gasoline counts favor 1995. Gasoline’s sidebar claims a profit every year since 1995, and its main text’s 21 years to 2015 start there too.

![“The start year decides where a streak ends”, drawn slowly stroke by stroke on a year axis from 1994 to 2009 that carries a label only at “1994”, “1995”, “2006”, “2007”, “2008” and “2009”. Each year from 1994 to 2008 has a blue dot on the axis, and 2009 has a vermilion cross labelled “loss”. A caption reads “dot: a profitable year”. A note in the lower right names the trade as “natural gas, June contract”. A dashed grey line between 2008 and 2009 marks the “first edition, Nov 2008”. Above the axis two purple brackets start at 1995. “13 from 1995, main text” ends at 2007 and “14 from 1995, sidebar” ends at 2008, both before the dashed line. Below the axis two black brackets start at 1994. “13 from 1994” ends at 2006 and “14 from 1994” ends at 2007. Starting the count a year earlier ends each streak a year earlier. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_streak_start.gif)

### Gasoline’s two claims read as two editions

Gasoline’s main text says 19 profitable years of the last 21 “as of 2015” (p. 183). Its sidebar says Chan “would have realized a profit every year since 1995” (p. 184), which cannot hold as of 2015, because 19 of 21 leaves 2 losing years. So the sidebar reads as first-edition text covering 1995 to 2008. Over those years the files show no loss, 11 profitable years and 3 with no price on a trade date. One book prints a 2015 count beside a 2008 claim.

![“Gasoline’s two claims read as two editions”, drawn slowly stroke by stroke on a year axis from 1995 to 2015 that carries a label only at “1995”, “2008” and “2015”. Each profitable year has a blue dot on the axis, and 2009 and 2012 each have a vermilion cross. Under 1997 to 1999, which have no mark, a grey span reads “no row”. A dashed grey line between 2008 and 2009 marks the “first edition, Nov 2008”. Above the axis a purple bracket, “sidebar: a profit every year since 1995”, runs from 1995 to 2008 and ends before the dashed line and before either cross. Above it a black bracket, “main text: 19 of 21, as of 2015”, runs from 1995 to 2015, past the dashed line and both crosses. Captions read “dot: a profitable year” and “x: a loss, 2009 and 2012”, and a note in the lower right names the contract as “May contract”. The sidebar’s claim fits the first edition’s years and the main text’s count fits the revised edition’s. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_gasoline_editions.gif)

## Lesson 2: read a missing row as missing, not as a loss

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

![“Three missing rows leave a range, not a count”, drawn slowly stroke by stroke. A year axis labelled only at “1995” and “2015” carries a blue dot for each profitable gasoline year and a vermilion cross at 2009 and 2012. A grey span under 1997 to 1999, which have no mark, reads “no row: a profit or a loss?”. Below, a scale of profitable years is labelled “15”, “16”, “17”, “18”, “19” and “20”. A purple bracket over 16 to 19 reads “the files allow 16 to 19”, and a black mark at 19, the bracket’s top end, reads “Chan: 19”. A caption names the scale as “profitable years of 21”, and a note in the lower right names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_gap_range.gif)

### Chan’s 19 needs all three missing years

The losses say more than the gaps. Chan’s 19 of 21 allows exactly 2 losing years, and the files show exactly 2, in 2009 and 2012. If Chan’s data agrees with EIA’s on the other 18 years, his 19 holds only if all 3 missing years were profitable in his data. No source here covers the contract in those years.

![“Chan’s 19 needs all three gaps to be profits”, drawn slowly stroke by stroke as two bars of 21 years. The upper bar is a blue box of “19 profits” and a vermilion box, labelled “Chan”. The lower bar is a blue box of “16 profits”, a dashed grey box and a vermilion box, labelled “EIA”. The upper vermilion box reads “2 losses” and the lower one “2009, 2012”, so both bars end in the same two losses. The dashed box, “no row”, sits under the last three of Chan’s profits, and a purple arrow points at it: “1997 to 1999 must all be profits for Chan’s 19”. A note in the lower right names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_chan_needs_gaps.gif)

### A fill cannot call the three years either

#### Two ways to fill a gap

Interpolating, which here means drawing a guess from the neighbouring days’ prices, would turn a gap into a guess, and the guess would decide the count it is meant to check.

The files do hold something on each missing day. EIA’s file for the second contract out, which holds June while May is the first, has a row on all three dates. So the run could fill from June as well as by interpolating. It tried both and measured how far to trust each.

##### Fill 1, a straight line

Fill 1 draws a straight line between the May rows on either side of the gap.

![“Interpolating turns a gap into a guess”, drawn slowly stroke by stroke. Black dots mark the May gasoline contract’s settlements one trading day apart along an axis labelled “gasoline, May contract, April 1997”, with no dot on the day labelled “Apr 14, the entry: no row”. The file misses April 11, 16 and 18 too, so those days have no dot either. A dashed grey line marks the “exit price 62.5¢”. A purple straight line joins the dots either side of the gap, and a purple dot on it at the gap is the “straight-line guess 61.6¢”. Around the guess a band of close strokes runs from “63.5¢” down to “59.7¢”, “one typical miss either side”. The dashed exit line splits it into a vermilion part above, “entry here: a loss”, and a blue part below, “entry here: a profit”. The guess sits in the blue part, and the band reaches into the vermilion. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_interpolation_guess.gif)

##### Fill 2, June’s move

Fill 2 takes May’s price on the last day before the gap, counting only days both files hold, and moves it by June’s change since that day, because the two contracts move almost together.

![“Fill 2 carries June’s move across the gap”, drawn slowly stroke by stroke. Black dots are the May gasoline contract’s settlements and grey rings the June contract’s, one trading day apart from April 7 to April 17, 1997, named “May” and “June” at their first marks, with a caption “dot: May   ring: June” and a note “gasoline”. May has no dot on the day labelled “Apr 14, the entry: no May row”, nor on April 11 or 16. June has no ring on April 9, 10 or 15. A grey arrow carries June from April 8, the last day both files hold, toward April 14, labelled “June rose 0.9¢”, and a purple arrow of the same rise starts at May’s April 8 price and points to a purple dot, “same rise on May: guess 62.1¢”. A dashed grey line marks the “exit price 62.5¢”. Around the guess a band of close strokes runs from “63.0¢” down to “61.2¢”, “fill 2’s typical miss either side”. The exit line splits it into a vermilion part above, “entry here: a loss”, and a blue part below, “entry here: a profit”. The guess sits in the blue part just under the line, and the band reaches into the vermilion. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_june_move_fill.gif)

#### How far each fill misses

To measure a fill, the run took April days from 1994 to 2005 whose May price the file does hold, and hid that price. It filled each hidden price and took the root mean square error, the typical size of a miss.

Not every April day can serve as a test. The rows each fill reads have to sit the same numbers of trading days away as the rows around the real gap, and each missing year’s gap has its own pattern of distances:

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

A year’s move is its exit price minus its entry price. With either fill’s guess in place, all three years’ moves are positive, so both fills guess a profit in all three years. But every move is smaller than its fill’s typical miss, so neither fill decides a year. Fill 2 gives moves of +0.4, +0.5 and +0.6 cents a gallon, against typical misses of 0.89, 0.76 and 0.65. Fill 1’s typical miss is about 2 cents in each year, larger than any of its moves.

Fill 2’s misses also lean one way. A standard error is how far an estimate, here an average miss, typically strays from its true value. On the test days fill 2 guessed May too low by 0.26, 0.21 and 0.20 cents on average, each between 2.7 and 3.2 standard errors from zero.

![“One set of misses, three numbers”, drawn slowly stroke by stroke. Fill 2’s misses on the 80 test days of 1997’s pattern are stacked as dots on a scale labelled “−2¢”, “−1¢”, “0¢”, “+1¢” and “+2¢” in “cents a gallon”, with a dashed line at zero, and a caption reads “dot: one test day’s miss, 80 days”. More of the dots sit right of zero than left, and a few reach past +2¢. Above them a grey bar spans one typical miss either side of zero, “typical miss ±0.89¢, around zero”, and a black bar with a purple dot at its middle spans the spread either side of the average, “average +0.26¢, spread ±0.86¢”, shifted right of zero by the lean. A note names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_three_numbers.gif)

Test days close together read some of the same prices, though, and days in one April share its price moves, so the true standard errors are larger and the lean is suggestive rather than settled.

![“Twelve Aprils, eight lean low”, drawn slowly stroke by stroke. Each April from 1994 to 2005 has a row labelled with its year and its number of test days, “1994 (5)”, “1995 (5)”, “1996 (8)”, “1997 (3)”, “1998 (1)”, “1999 (2)”, “2000 (8)”, “2001 (9)”, “2002 (11)”, “2003 (8)”, “2004 (15)” and “2005 (5)”, and a bar from a dashed zero line to that April’s average miss. Eight bars, in purple, run right of zero, and the longest, for 1996, 2001 and 2003, carry most of the lean. The other four, in grey, sit left of zero or on it. Captions read “left: May guessed too high”, “right: too low” and “(n): test days that April”, a summary reads “8 of 12 Aprils lean low”, and a note names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_april_leans.gif)

#### From a miss to a chance of a profit

Fill 2’s misses on the test days give two numbers, and together the two give each year a chance of a profit.

1. The average miss corrects each guess and gives each year a corrected move. The correction subtracts in 1997, where the entry is missing, and adds in 1998 and 1999, where the exit is missing, for a reason worked out below.
2. The spread of the misses around that average, the typical miss with the lean taken out, sets how far to trust that move.

Moves and misses are in cents a gallon:

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

The chances come from a model of the miss. Write the missing price as fill 2’s guess plus an unknown miss `e`, and suppose `e` follows a normal curve, a symmetric bell shape, with a mean `b` equal to fill 2’s average miss and a standard deviation `σ` equal to the spread:

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

So a true price above the guess, a positive `e`, lowers an entry’s move and raises an exit’s. The sketch marks each arrow with `e` at that year’s average miss `b`, 0.26 cents for 1997 and 0.21 for 1998. Putting `b` in place of `e` gives each case its corrected move `c`:

```math
\begin{array}{l|c|c}
 & \text{True move} & c \\ \hline
\text{Entry, 1997} & m - e & m - b \\
\text{Exit, 1998, 1999} & m + e & m + b
\end{array}
```

Both cases give the chance of a profit by the same formula. `Φ(z)` is the share of a standard normal curve that lies below `z`:

```math
P(\text{profit}) = \Phi\left(\frac{c}{\sigma}\right)
```

For 1997, `m` is 0.4 cents, `b` is 0.26 and `σ` is 0.86, so `c` is 0.14. From the unrounded values, the chance is Φ(0.17), or 57%. If the three misses are also independent of each other, the three chances multiply:

```math
0.566 \times 0.832 \times 0.900 = 0.424
```

So the chance that all three years were profits, which Chan’s 19 needs, is 42%. The same formula with each year’s typical miss around zero, and no correction, gives 41%, so the correction barely moves the figure. It moves the years apart, though: 1997 is close to a coin flip, and 1999 reaches 90%, still short of 95%.

![“Each corrected move against fill 2’s spread”, drawn slowly stroke by stroke. A dashed grey line at zero divides “loss” on the left from “profit” on the right. Three rows follow, each with its σ above its bar: “σ = 0.86¢” for “1997”, with “57%”, then “σ = 0.74¢” for “1998”, with “83%”, then “σ = 0.62¢” for “1999”, with “90%”. In each row a purple dot right of zero marks the year’s move with fill 2’s guess corrected by its average miss, and a black bar of one spread either side. The bar for 1997 reaches well across zero, the bar for 1998 only just reaches past it, and the bar for 1999 stops just short of it. A scale below reads “−1¢” and “+1¢” in “cents a gallon”, and the percentages sit under “chance of profit”, each computed as if fill 2’s misses are normal around their average. Captions read “dot: the corrected move” and “bar: σ, fill 2’s spread, either side”, and a note under the scale names the trade as “gasoline, May contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_fill_misses.gif)

#### What the chance rests on

The run tested neither the assumption that the misses are normal nor the assumption that they are independent. Heavier tails than a normal curve would raise each chance rather than lower it, because a curve with heavier tails and the same spread puts more of its misses near the average. Misses that are not independent could move the figure either way. Misses that run the same way in all three years lower it, because a true price above the guess in every year would help 1998’s and 1999’s exits and hurt 1997’s entry. Misses that set 1997 against 1998 and 1999, or that tie only 1998 to 1999, raise it.

## Lesson 3: test the trade out of sample

Chan picked both trades by studying past prices, and both rules name exact days. That invites **data-snooping bias**, Chan’s own name for it: searching the past for a rule that worked picks up chance patterns along with real ones, so the winning rule looks better on the years it was chosen from than it will on new ones. Only an out-of-sample test, a test on years the rule was not chosen from, can show whether its record holds. This post’s out-of-sample years are the years after the book. The book’s years end where Chan’s counts end: 2015 for gasoline, and 2008 for natural gas under Lesson 1’s reading. Natural gas starts in 1994, the first year the files hold a whole trade.

Natural gas went from winning 15 of 15 years, with a mean return of 10.6%, to winning 7 of 15 with a mean near zero. Chan says as much: the trade “didn’t hold up as well out-of-sample” (p. 185), though he prints no figure.

For gasoline, Chan himself treats part of the book’s years as out of sample: the last 9 of his 21, 2007 to 2015. The trade won 7 of those 9, and both of its losing years fall among them. From 2016 to 2023 it won 3 of 8, and natural gas won 4 of the same 8.

![Two panels of bar charts, one bar per year showing the change in settlement price from entry to exit. The upper panel is gasoline, the May contract from the close of April 13 to the close of April 25, from 1995 to 2023 in dollars a gallon. Its years 1997, 1998 and 1999 are empty slots labelled “no row”. A dashed line after 2015 divides 1995 to 2015, 16 of 21 profitable and 3 with no row, from 2016 to 2023, 3 of 8 profitable. Bars before the line are mostly small and positive, with losses in 2009 and 2012, and five of the eight after it are losses. The lower panel is natural gas, the June contract from the close of February 25 to the close of April 15, from 1994 to 2023 in dollars per million Btu. A dashed line after 2008 divides 1994 to 2008, 15 of 15 profitable, from 2009 to 2023, 7 of 15 profitable. Every bar before the line is positive. After it, 8 years are losses and 7 are gains, in no regular order, including one gain near three dollars in 2022. Marks along the foot of each panel point up for each profitable year and down for each losing one.](../docs/figures/commodity_seasonals_years.png)

*Every year of both trades. Each dashed line is where the book’s years end, and the marks along each foot give every year’s sign, including years too small to see as bars.*

### What could explain the fall

Chan picked each rule because it did well in years the book covers, so those years tend to start it higher than its real edge. Where they do, the drop after the book is measured from a raised start, so it looks like a longer fall than the trade really took.

Publishing a trade can also fade its edge. Once a rule is in print, traders who read it can act before its dates, so the price move it relies on comes sooner and leaves less for anyone who waits for the date. McLean and Pontiff (2016) measured this for 97 published predictors of stock returns. Returns were 26% lower in the years after each study’s data ended but before it was published, and 58% lower after publication. They attribute the 32-percentage-point difference to traders acting on what was published. Their predictors are stock anomalies rather than commodity trades, so their sizes do not carry over to these two trades.

Natural gas’s years after the book are also its years after publication, since Lesson 1 reads its counts as written for the first edition of November 2008. So its fall after 2008 mixes three causes that 15 yearly trades cannot separate.

1. The rule fitted chance patterns in the years it was chosen from.
2. The market changed.
3. Traders acted on the rule once it was in print.

Gasoline’s sidebar reads as first-edition text too, so its rule was also in print from November 2008. It won 5 of its 7 years from 2009 to 2015, and 3 of 8 from 2016 to 2023.

## Lesson 4: count the results before grading a split

Each trade happens once a year, so 15 years give 15 results, about what a strategy that trades every day collects in three weeks. The rest of this lesson works out how far to trust so few results.

### How far a Sharpe ratio can stray

A Sharpe ratio has a standard error too, how far the estimate typically strays from the true ratio. For a Sharpe ratio `SR` estimated from `n` independent returns, Lo (2002) gives its standard error `SE`:

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

For the four Sharpe ratios in the returns table at the top of the post, each trade before and after the book, the standard error runs from 0.3 to 0.4, so each one’s 95% range reaches 0.5 to 0.7 either side of it.

![“How far each Sharpe ratio can stray”, drawn slowly stroke by stroke. A dashed grey line at zero divides “loses” on the left from “earns” on the right. Four rows follow, each labelled with its trade and years: “natural gas, 1994 to 2008”, with a purple dot at “1.0”, then “natural gas, 2009 to 2023” at “0.0”, then “gasoline, 1995 to 2015” at “0.8”, then “gasoline, 2016 to 2023” at “−0.4”. Each dot sits on a black bar reaching 1.96 standard errors either side. The first bar runs from about 0.4 to 1.6 and the third stays right of zero, while the bars of both periods after the book reach across the zero line. A scale along the foot is marked “−1”, “+1” and “+2” and labelled “Sharpe ratio”. Captions read “dot: the Sharpe ratio” and “bar: 1.96 standard errors either side”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_sharpe_ranges.gif)

### Whether the mean return changed

The 95% range for a mean return from `n` results, with standard deviation `s`, uses Student’s t, which widens the range to allow for estimating `s` from so few. The formula writes `t` with the subscript `n − 1`, which statisticians call the degrees of freedom:

```math
\bar r \pm t_{n-1} \times \frac{s}{\sqrt{n}}
```

![“Fewer results, a wider range”, drawn slowly stroke by stroke. Four bars rise from a grey base, each labelled with its height: “2.36” over “8 results”, “2.14” over “15 results”, “2.05” over “30 results” and “1.96” over “many”. A dashed grey line runs across at the normal curve’s value, labelled “normal, 1.96”, and the fewer the results, the higher a bar stands above it. A caption reads “95% multiplier from Student’s t”. The first two bars are purple, and a note reads “purple: the later periods’ 8 and 15 years”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_t_multiplier.gif)

Natural gas after 2008 averaged −0.4% a year with a standard deviation of 21.6% over 15 years, and `t` for 14 degrees of freedom is 2.14. The ±12.0% below comes from the unrounded values of these numbers:

```math
\begin{aligned}
&-0.4\% \pm 2.14 \times \frac{21.6\%}{\sqrt{15}} \\
&= -0.4\% \pm 12.0\%
\end{aligned}
```

![“Where ±12% comes from”, drawn slowly stroke by stroke. A dashed grey line comes first, marking “the later mean, −0.4%”, and three bars grow from it. The first, black, is “spread s = 21.6%”. The second, black and about a quarter as long, is “s / √15 = 5.6%”. The third, purple, is “× 2.14 = 12.0%”. A short dashed grey line across the purple bar marks “the earlier mean, 11.0 points higher”, and the purple bar reaches past it, so the range around the later mean holds the earlier one. A note in the upper right names the trade as “natural gas, June contract, 2009 to 2023”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_half_width.gif)

That range, −12% to +12%, still holds the +10.6% natural gas earned before 2009. So 15 years cannot tell a trade that weakened from one that had a bad stretch of years.

Gasoline after 2015 averaged −1.9% with a standard deviation of 4.8% over 8 years, and `t` for 7 degrees of freedom is 2.36:

```math
\begin{aligned}
&-1.9\% \pm 2.36 \times \frac{4.8\%}{\sqrt{8}} \\
&= -1.9\% \pm 4.0\%
\end{aligned}
```

That range, −6% to +2%, leaves out the +3.2% gasoline earned before.

![“One range holds the earlier mean, one does not”, drawn slowly stroke by stroke. A dashed grey line marks “0%”. Four rows follow, each with a black bar of its 95% range, a purple dot at its mean, and the mean written at the right edge: “natural gas, 1994 to 2008” at “+10.6%”, “natural gas, 2009 to 2023” at “−0.4%”, “gasoline, 1995 to 2015” at “+3.2%” and “gasoline, 2016 to 2023” at “−1.9%”. A dashed grey line drops from each trade’s earlier mean past its later bar. Natural gas’s lands inside the later range, and gasoline’s lands just past its right end. A scale along the foot is marked “−10%”, “+10%” and “+20%” and labelled “mean yearly return”. Captions read “dot: the mean” and “bar: 95% range   dashed: the earlier mean”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_mean_ranges.gif)

### Whether the typical year changed

Two tests compare the periods directly, and they ask different questions.

Welch’s t-test compares the average yearly returns. It lets each period keep its own standard deviation, which matters because natural gas’s standard deviation doubled after 2008.

The Mann-Whitney test ignores how large each return was. It pairs every year before the split with every year after and records which one returned more. If nothing had changed, the earlier year would win about half the pairs. For gasoline the earlier year won 117 of 144 pairs, where chance would give half, 72. For natural gas the earlier year won 177 of 225 pairs, where chance would give half, 112.5.

![“177 of 225 pairs”, drawn slowly dot by dot. A 15 by 15 grid of dots pairs every natural gas year from 1994 to 2008 with every year from 2009 to 2023. Blue dots fill most of the grid first. Notes on the left then read “rows: 1994 to 2008,” and “worst at the bottom”, a note below reads “columns: 2009 to 2023, worst on the left”, and the blue dots are labelled “blue: the earlier year did better”. Vermilion dots then fill the rest, toward the right, labelled “vermilion: the later year did”. The rightmost column, headed “2022”, is all vermilion, and a note reads “2022 beats all 15 earlier years”. A black staircase traces the edge between the blue and the vermilion. A tally on the right reads “earlier year won 177 of 225 pairs” and, beneath it, “chance alone: 112.5”. A note in the upper right names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_rank_pairs.gif)

Each test gives the chance that luck alone would produce a difference at least this large if the trade had worked equally well in both periods. The run counts Mann-Whitney’s chance exactly, over every way the years could split between the two periods. A small chance means luck explains the difference poorly. The usual line is 5%, and a chance below it counts as evidence that the trade changed. For natural gas’s 177 pairs, luck alone lands that far from the middle, 112.5, on either side, 0.7% of the time.

![“What 0.7% means”, drawn slowly stroke by stroke. A grey axis is labelled “pairs the earlier years win, of 225”. A black bell-shaped curve of the chance of each count rises over it, labelled “what luck alone gives,” and “if nothing changed”. A dashed grey line at its peak marks “112.5: no change”, and a dashed grey line to its right marks “the 5% line”. A purple line further right, beyond the 5% line, marks “177 pairs:” and “what the years did”. Purple strokes shade the curve’s two thin tails, the right one from 177 out and its mirror on the left, and a note reads “this far out, either side: 0.7% of luck’s draws”. The tails are so thin that they barely rise off the axis. A note in the upper right names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_luck_curve.gif)

The four chances, as percentages:

```math
\small\begin{array}{l|r|r}
 & \text{Welch} & \text{Mann-Whitney} \\
 & \text{(averages)} & \text{(pairs)} \\ \hline
\text{Gasoline} & 2.3\% & 1.1\% \\
\text{Natural gas} & 9.2\% & 0.7\%
\end{array}
```

![“Four chances against the 5% line”, drawn slowly stroke by stroke. A grey scale runs from “0%” through “5%” to “10%”, and a dashed grey line rises from 5%, with “below: luck explains it poorly” on its left and “above: luck could explain it” on its right. A row for “gasoline” gets a black dot at “Welch, 2.3%” and one at “Mann-Whitney, 1.1%”. A row for “natural gas” gets a purple dot at “Welch, 9.2%”, the only one right of the line, and a black dot at “Mann-Whitney, 0.7%”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_four_chances.gif)

Gasoline’s fall passes both tests, with each chance below the 5% line. For natural gas the two tests disagree because of one year, 2022. The trade’s typical year clearly got worse, from 15 wins in 15 years before 2009 to 7 in 15 after. But 2022’s +64% lifts its average after 2008 to −0.4%. Natural gas’s years vary so widely that luck could explain the difference from the +10.6% before, and Welch’s chance, 9.2%, sits above the line. Mann-Whitney still sees the change, because 2022 beats each of the 15 earlier years once, however large its gain.

Without 2022 the average after 2008 is −5.0%, and Welch’s chance falls to 0.1%. That year was a real gain that a trader holding every year would have collected, so it stays in the record. No plan written before the numbers came out picked one of the tests, so the post reports both rather than the one that reads better.

![“One year moves the mean, not the ranks”, drawn slowly stroke by stroke. A grey axis carries a dashed line at “0%”, and a caption reads “returns, 2009 to 2023”. Natural gas’s 15 returns from 2009 to 2023 sit on it as dots at their true values, stacked where they would touch, vermilion left of zero for the 8 losses and blue right of it for the 7 gains. Two gains sit so close to the line that a note names them, “2014 and 2018: just above 0%”, and one blue dot sits far to the right, labelled “2022: +64%”. A black tick under the axis marks the “mean −0.4%”, and a purple tick left of it marks the mean “without 2022: −5.0%”. Below, a grey line carries all 30 years from 1994 to 2023 ranked from worst to best, with black dots above it for “1994 to 2008” and purple dots below it for “2009 to 2023”. The nine worst ranks all belong to years after 2008, and 2022 takes the top rank on the right. The ends are marked “worst” and “best: 2022”, and a caption reads “ranked worst to best, 2022 is the top rank however large its gain”. A note in the upper right names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_one_year.gif)

### Why the run did not try nearby dates

Chan makes the point about few results too, and offers a check. A trade that happens once a year produces few results, he writes, so data-snooping bias is hard to rule out (p. 186). His check, trying nearby entry and exit dates, is a search across many trades, and the run did not try it. Further work, at the end of this post, says what running it fairly would take.

## Lesson 5: find a contract’s file with the exchange’s calendar

EIA’s files hold contract 1, contract 2 and so on, not the May or June contract, so every trade date needs the file that holds Chan’s contract.

For gasoline that is always contract 1. The April contract stops trading on the last trading day of March, and the May contract trades until the last trading day of April. Natural gas contracts stop trading three trading days before their delivery month begins. So the June contract is contract 4 on February 25 if the March contract has not yet expired, contract 3 if it has, and contract 2 by mid-April.

![“Which file holds the June contract”, drawn slowly stroke by stroke, twice on one calendar from late February to the start of May. Each time, four stacked bars labelled “March”, “April”, “May” and “June” stand for the natural gas contracts, each ending at its last trading day, with June’s bar in purple running off the right. The upper set is “2008”, where March’s bar ends on February 27, marked “March still trading”. A dashed line at the entry crosses all four bars, labelled “June is contract 4 on Feb 25”, and a dashed line at the exit crosses May and June, labelled “contract 2 on Apr 15”. The lower set, with its own “March”, “April”, “May” and “June”, is “2006”, where March’s bar ends on February 24, marked “March has expired”. Its entry line crosses only April, May and June, labelled “June is contract 3 on Feb 27”, and its exit line crosses May and June, labelled “contract 2 on Apr 13”. It closes on “June’s number is how many bars each line crosses”, and the finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_june_file.gif)

*In 2006, February 25 fell on a Saturday, so the trade entered on Monday the 27th, after March had expired. April 15 was a Saturday and the 14th was Good Friday, so the exit moved back to the 13th.*

### Three checks of the expiry rule

Nothing in the files says which contract a file holds on a given day. The run works it out from the expiry rule, so a rule wrong by a day on a trade date reads May’s or July’s price instead of June’s. That price looks like any other, and the trade’s return would then come from two different contracts with nothing in the results to show it. So the run checks the rule three ways.

#### Against the exchange’s own dates

Massive, a market data vendor, records each contract’s last trading day as the exchange set it. For all 40 March to June contracts it records from 2017 to 2026, the rule gives the same day. Massive’s records begin in 2017, so the years before rest on the next check.

#### Against the files’ own handovers

When a contract expires, every later contract moves forward one place: contract 2 becomes contract 1, contract 3 becomes contract 2, and so on. So on the next trading day, each file’s price carries on from the price the file numbered one higher showed the day before, not from its own, and so do the differences between neighbouring files’ prices. That switch is the handover this check looks for, and it reads it in those differences. Before mid-1997 the handovers show contracts stopping five or six trading days before delivery rather than three, so for those years the run follows the handovers. That moves the 1996 and 1997 entries from contract 4 to contract 3, and both years are profitable on either.

![“A handover shows when March stopped”, drawn slowly stroke by stroke. Two rows of dots run across the trading days from mid-February to March 1, 1996, one dot a trading day, the settlements in the “contract-1 file” in black and in the “contract-2 file” in grey. A purple arrow runs from the contract-2 file’s Feb 23 price to the contract-1 file’s next price, labelled “Feb 26: file 1 picks up file 2’s price”. A purple dashed line between Feb 23 and Feb 26 marks “March stopped Feb 23, 5 trading days before delivery”, and a grey dashed line two trading days later marks “3-day rule: here”, where a three-day rule would have put the handover. A note reads “natural gas, March contract, Feb 1996”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_handover.gif)

Over every natural gas contract delivered from February 1994 to April 2024, the handover falls on the rule’s day for 298 of the 316 expiries the files hold rows to check. 30 of the 298 are contracts delivered before June 1997, where the rule’s count of days before delivery came from these handovers. Moved a day earlier or later, the rule fits only 38 and 16 of the 324 expiries the files hold rows to check on the moved days.

![“Which years each check reaches”, drawn slowly stroke by stroke. A year axis is marked “1994”, “2000”, “2010”, “2017” and “2026”. A black bar runs from 1994 to 2024, labelled “the files’ handovers: 298 of 316 expiries fit”. A purple bar runs from 2017 to 2026, labelled “the exchange’s dates: 40 of 40 March to June contracts”. A dashed grey line at 2017, where Massive’s records begin, marks “before 2017, the files alone”. A note reads “natural gas, contracts’ last trading days”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_check_coverage.gif)

Outside those 316, the check cannot reach 47 expiries, because a file lacks a row on the expiry day or the day after. 40 of the 47 fall between 1997 and 2005.

The 18 that do not fit are mostly close calls. 15 fail by under 9 cents, meaning the differences between the files’ prices around the expiry fit slightly better with no handover than with one. That happens where neighbouring contracts trade so close together that a handover and no handover look alike. One of those 15, March 2023, fails although the exchange’s own date matches the rule’s.

A rule wrong by a day would matter only where it moves which file holds June on a trade date. That is true of 4 of the 18, all March contracts at an entry, and of none of the 47. In those 4 years, reading the other file turns none from a profit to a loss, or from a loss to a profit.

#### Against the edge cases

In 10 of the 30 years, the entry date falls on the March contract’s last trading day. A contract still trades on its own last day, so the run reads June as contract 4 then. Reading the contract-3 file instead turns no year from a profit to a loss, or from a loss to a profit.

![“2018: entry on March’s own last day”, drawn slowly stroke by stroke. Four bars stand for the natural gas contracts, “March”, “April” and “May” in black and “June” in purple, against late February 2018. March’s bar ends at its last trading day, and the April, May and June bars run off the right. A dashed grey line marks the “entry, close of Feb 26”, exactly where March’s bar ends, and a note beside it reads “March’s last day: it still trades at this close”. The line reaches all four bars, so “June is contract 4”. Notes read “10 of 30 years enter on March’s last day.” and “Reading the contract-3 file instead turns no year from a profit to a loss.”, and a note names the trade as “natural gas, June contract”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_edge_day.gif)

### Where the run’s trading days come from

The run computes its own calendar of trading days rather than reading one from the files, because a row in the files does not show that the exchange was open. On every exchange holiday from January 2018 to November 2019, the natural gas files hold a row that repeats the previous trading day’s settlement. In other years almost no holiday has a row. Of NYMEX’s holidays, only Good Friday can land on a trade date, and it moved six trade dates between 1994 and 2023.

![“A row in the file is not a trading day”, drawn slowly stroke by stroke. The top row, “2018”, numbers its days “21”, “22”, “23”, “24” and “25”, where a vermilion dot is labelled “Dec 25: closed, row repeats Dec 24’s $3.467”, then “26”, “27” and “28”. A black dot stands on each other day the contract-1 file holds a row, so the weekend of the 22nd and 23rd has none. The bottom row, “2016”, numbers “21”, “22”, “23”, “24”, “25” and “26”, labelled “Dec 26: closed, no row”, then “27” and “28”, and its weekend of the 24th and 25th and the closed 26th have no dot. A caption reads “dot: a row in the contract-1 file   no dot: a weekend or a closed day”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_holiday_rows.gif)

The same map from dates to contracts serves Chan’s calendar spreads, which [the calendar spreads post](https://github.com/l3a0/quantitative-trading/blob/main/blog/calendar-spreads-lessons.md) tests on the same files.

## What this replication cannot say

Two questions are beyond it, besides the gaps, the start year and edition, and the checks under Further work below.

1. **Whether Chan read the same contracts.** His sidebar names RB, the symbol RBOB trades under. Before RBOB began trading in October 2005, his series presumably held the older contract, as the run assumes. Chan does not name his data vendor.
2. **Any year after 2023.** EIA’s RBOB and natural gas files end on 5 April 2024, before either trade’s 2024 exit date.

## What this means for a trader

Four habits follow from the first four lessons.

1. **Ask a consecutive count where it starts and when it was written.** The same files give 13, 14 or 15 consecutive years for natural gas, depending on both.
2. **Read a missing year as missing.** Three gaps in one file leave Chan’s gasoline count anywhere between 16 and 19, and filling them with a neighbouring day would decide the answer instead of checking it. Even the closer of the run’s two fills, fill 2, has a typical miss larger than each year’s move with its guess, and correcting its lean still leaves no year at 95%.
3. **Judge a seasonal trade on the years after it was chosen and published.** Natural gas won every year through 2008 with a mean return of 10.6% a year, and averaged a loss of 0.4% a year after.
4. **Count the results behind a Sharpe ratio, and ask which test a claimed change rests on.** Fifteen yearly trades leave a standard error near 0.3, and one year, 2022, decides whether the fall in natural gas’s average stands out from luck.

## Further work

Each trade is fixed by six parameters, five from Chan’s rules and one the run chose.

1. **The entry date**, April 13 for gasoline and February 25 for natural gas.
2. **The exit date**, April 25 for gasoline and April 15 for natural gas.
3. **The time of day**, the close.
4. **The delivery month**, May for gasoline and June for natural gas.
5. **The rule for a closed date**, which enters on the next trading day and exits on the previous one.
6. **The position size**, one contract’s entry value each year. This is the run’s choice.

Varying each one is a check of its own, and a seventh adds a parameter the rules lack, a stop. Three more checks test the record without changing the trade.

### One search across every parameter

Chan suggests trying somewhat different entry and exit dates to see whether the profits hold (p. 186). The same question applies to every parameter above. Varying them until some version works is a search across many trades, and the best of many looks profitable by chance alone. So the search needs three safeguards, shared by every variant below.

1. **The variants.** Every value of every parameter to be tried, written down before any is computed.
2. **The pass mark.** It gets stricter the more variants the search tries. Neighbouring variants overlap, such as two pairs of dates that share most of their holding period, so their results rise and fall together, and the pass mark has to stay valid when they do.
3. **The held-back years.** The New York Harbor gasoline file begins in January 1985, and nothing here has read its Aprils before 1994, so 1985 to 1993 give nine years the search would never see, though Chan may have seen them. Every natural gas year in EIA’s files is already used, so its held-back years would have to come after 2023, which the files do not reach.

The search asks whether the neighbourhood of Chan’s rules holds up, not which neighbour does best.

![“A cliff or a plateau”, drawn slowly stroke by stroke, schematic and to no scale. Two panels each draw profit against one parameter. On the left a grey line marks “0”, and a vermilion line runs low and nearly flat, then spikes in one narrow peak at a purple dot labelled “Chan’s”, under the heading “a cliff: only Chan’s value pays” and above the caption “likely chance”. On the right a second grey line marks “0”, and a blue line rises into a broad flat top that holds a purple dot labelled “Chan’s” and stays high well to either side of it, under the heading “a plateau: nearby values pay too” and above the caption “worth a closer look”. A grey note on the left reads “profit”, and notes below read “each axis: one parameter, moved either way from Chan’s value” and “schematic, drawn to no scale”. The finished drawing holds for twelve seconds.](../docs/figures/commodity_sketch_plateau.gif)

### Entry and exit dates

Each date moves within a set range of Chan’s, counted in trading days so each one lands on a day the exchange is open. Moving both dates also changes how long the trade is held, so a range wide enough to matter for gasoline’s twelve calendar days can put its entry after its exit.

### Time of day

Every entry and exit in the run is a settlement price. Chan names no time of day for the natural gas exit, so the close there is the run’s own choice. Trading at the open or at a set hour instead needs prices from inside the day, and EIA’s files hold one price a day for each contract. The run holds no prices from inside the day for these contracts, and whether any source reaches back to the 1990s is unmeasured.

### Delivery month

If seasonal demand drives the gain, a neighbouring delivery month bought and sold on the same dates should share it. If only Chan’s month shows the gain, chance is the likelier cause. EIA’s files hold four contracts at a time, which reach the June gasoline contract and the May natural gas contract on every entry and exit date from 1994 to 2023, so this check needs no new data.

### The rule for a closed date

Chan’s rule keeps a trade inside his dates whenever one falls on a weekend or a holiday. The alternatives move it outward, entering on the trading day before and exiting on the one after, or move both dates to the nearest trading day. A rule that only matters in some years can still change which of those years win, and the change is a variant like any other.

### Position size

Each year stakes one contract’s entry value, so every year counts equally in the mean. A trader might size each year by how much the contract has been moving, which weights calm years more than wild ones. Sizing changes the mean return, the Sharpe ratio and the drawdown, but never which years won.

### A stop that ends a trade early

Natural gas’s 2002 trade, the drawdown example under the record, fell 22 points from its peak and still ended the year ahead. A rule that sells once a trade falls a set amount from its peak caps a fall like that. The price is selling some trades that would have recovered, as 2002’s did. Each level of stop tried is one more variant.

### Costs

Every return in the run is before costs. A commission is small next to a futures contract’s value, so the larger unknown is slippage, the gap between the settlement price and the price an order actually gets. Measuring it needs the same prices from inside the day that the time of day needs. Costs only lower a return, so they cannot rescue either trade after the book. What they could change is how much the book’s years paid.

### The three missing gasoline rows

Lesson 2 leaves Chan’s gasoline count between 16 and 19 because EIA’s file holds no row on three dates. A second vendor with settlements on those dates would settle the count without guessing a price. Settlement prices come from the exchange, so the vendor should agree with EIA on every day both hold, which checks the vendor before its three prices are trusted.

### The demand behind each trade

Chan explains both trades by seasonal demand (p. 183). A test of that explanation would ask whether natural gas gains more in the spring when less gas sits in storage at the end of winter, and whether gasoline gains more when its stocks are low ahead of the driving season. EIA publishes both stock levels. A confirmed explanation would make the trades more believable, but only years after a rule was chosen can show that it still pays.

## References

- Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Released in November 2008.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 175 and 183 to 186. Page numbers here are the revised edition’s. The replication log cites the passages on pp. 183 to 185 by Kindle location, 4529 to 4632.
- Lo, A. W. (2002). The statistics of Sharpe ratios. *Financial Analysts Journal*, 58(4), 36 to 52.
- McLean, R. D., and Pontiff, J. (2016). Does academic research destroy stock return predictability? *The Journal of Finance*, 71(1), 5 to 32.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for New York Harbor regular gasoline, RBOB gasoline and Henry Hub natural gas, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the two trades](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/commodity_seasonals_whiteboard.py), with the checks behind [the trades’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_commodity_seasonals_whiteboard.py), and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-11-the-commodity-seasonals-chans-quantitative-trading) that sets each of Chan’s figures beside the one reproduced here.*
