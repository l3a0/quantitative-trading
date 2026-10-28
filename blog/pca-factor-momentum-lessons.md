# Four of Example 7.4’s five statistical factors pass Chan’s momentum test, and none clears the noise

*Example 7.4’s strategy, which finds its factors by principal component analysis, assumes its factor returns persist from one day to the next. Testing that needs each day’s factor return paired with the next day’s on one day’s weights, because the weights flip sign from day to day and learn from today’s return. Four of the five factors pass, one symbol with two price histories decides which one misses, and no test across all five finds anything.*

## Why a statistical factor has to persist

Example 7.4 of Ernest Chan’s *Quantitative Trading* trades a statistical factor model on the S&P 600. Each day it finds five factors in a year of returns, works out what each factor returned today, and buys the stocks those factor returns favour. The strategy is “based on the assumption that factor returns have momentum”, in Chan’s words, and “they remain constant from the current time period to the next” (Chan, 2021, p. 164). His general claim is that factor returns “often” show “stronger serial autocorrelations than individual stock’s returns” (p. 162).

The [factor models post](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md) explains what Example 7.4 does and reproduces its printouts. It tested Chan’s claim on two named factors, the market and momentum, on monthly returns, and gave a short account of the five statistical factors too. This post is about those five. It tests them daily, on the file the example loads, and spends most of its length on the method, because a factor that is re-estimated every day does not hand over a return series that can simply be correlated with itself.

Five lessons follow.

1. A factor re-estimated every day has no fixed sign, and tomorrow’s weights have already seen today’s return.
2. Leaving the mean in the statistic is a choice with a reason.
3. The factor return the forecast reads is the regression’s slope times the day’s singular value, the number that says how much of the window’s variation the factor carries, and the intercept moves nothing.
4. Four of five passing says little.
5. One spliced symbol decides which factor misses.

**Every result here is exploratory.** The claim is Chan’s, so testing it spends the 2004 to 2008 sample on a hypothesis chosen by someone else. The test can say whether the claim holds on this file and nothing about factor momentum today. **Every result is also about survivors.** The file holds the S&P 600 as it stood on 2008-01-14, carried backwards, so a company that left the index before then is not in it. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How the test works

**The file.** Chan’s `IJR_20080114.mat` holds the 600 members of the S&P 600 as he saved them on 2008-01-15, with 1,006 trading days of closes from 2004-01-15 to 2008-01-14. Nothing was downloaded.

**The decomposition.** The revised edition’s MATLAB program, the one that prints Chan’s 2 percent a year before costs, does the same thing every day t.

1. It takes the 252 daily returns ending the day before, t − 1, for every stock priced on all of them.
2. It subtracts each day’s average across the stocks and finds the window’s five largest principal components. Each component k comes as a set of weights across the stocks, a vector uₖ of length one, and a singular value sₖ that says how much of the window’s variation that component carries.
3. It fits day t’s returns across the stocks on those components and ranks the stocks on the fit.

The first day with a full window is 2005-01-18. Every day from then to the second-to-last row has a next day, which gives 752 days t.

**The pair.** On each of those days, the factor return of component k is the weighted sum of that day’s returns, fₜ = uₖ · rₜ. Its partner is the same weights applied to the next day’s returns, fₜ₊₁ = uₖ · rₜ₊₁. Lesson 1 explains why both members read day t’s weights, and Lesson 3 why the factor return is this sum rather than the number the regression prints.

**The statistic** is the correlation of the 752 pairs without subtracting their means, defined in Lesson 2.

**The criterion.** The claim holds for a factor when its statistic is above 0 and above the median stock’s. The comparison set is the 579 stocks priced on every day the pairs read, each given the same statistic on its own pairs of one day’s return and the next. Each factor carries its own verdict, and no combined verdict is drawn. The criterion, the pairs and the statistic were all written down before any factor return was computed, as [the replication log’s entry](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-42-whether-example-74s-own-factor-returns-have-momentum-chans-quantitative-trading) records.

## Lesson 1: a factor re-estimated every day has no fixed sign, and tomorrow’s weights have already seen today’s return

The obvious way to test whether PC3, the third component, has momentum is to compute its return every day on that day’s weights and correlate the series with itself one day apart. That series measures three things besides persistence.

1. **The sign.** A principal component is a direction, and a direction and its opposite explain a window equally well. The decomposition returns uₖ or −uₖ with no preference, and which one comes back depends on the numerical library, so a factor return computed on fresh weights can change sign because the weights did.
2. **The rank.** Component k is the k-th largest that day. When two components carry nearly equal variation, they can trade places from one day to the next, and a series called PC3 then switches to another factor.
3. **The window.** Tomorrow’s weights are fitted on the 252 days ending today, so the window that chooses them already holds today’s return.

This repository measured all three on Chan’s file after the verdicts were in. **These measurements are exploratory and decide nothing.**

The library’s signs are not even reproducible. On the two machines that ran this repository’s checks, they flipped between consecutive days on about half the days, and the two machines disagreed about which days. So before measuring anything, the code turns each day’s vectors by a rule that reads only the vector, so that each one’s largest weight is positive. The rule settles the library’s choice, but it cannot keep a direction steady. When a vector’s largest weight moves to a stock it weighed the other way, the rule turns the whole vector over. Comparing each day’s weights with the next day’s, on the stocks both days keep, PC1’s vector points the other way on 1 of the 752 days, PC2’s on 14, PC3’s on 6, PC4’s on 22 and PC5’s on 24. A largest weight moving to another stock accounts for every one of those flips except three, and those three fall on days two factors swap rank. Rank swaps are rare too. On 15 of the 752 days, two or more factors trade places.

The table sets four ways of reading tomorrow’s factor return side by side. Each row keeps today’s return on today’s weights and changes only what tomorrow’s return is read on.

```math
\begin{array}{l|r|r|r|r|r}
\text{Tomorrow's return read on} & \text{PC1} & \text{PC2} & \text{PC3} & \text{PC4} & \text{PC5} \\ \hline
\text{tomorrow's own weights, largest weight positive} & 0.0326 & -0.1105 & -0.0283 & -0.0315 & 0.0025 \\
\text{the same, sign and rank matched to today's} & 0.0246 & -0.0161 & -0.0318 & -0.0285 & 0.0768 \\
\text{weights fitted on the 251 days before today, matched} & 0.0315 & 0.0776 & -0.0228 & 0.0338 & 0.0713 \\
\text{today's weights, the pair the test reads} & 0.0316 & 0.0778 & -0.0189 & 0.0305 & 0.0710
\end{array}
```

On tomorrow’s own weights, PC2 reads −0.1105 and would fail outright, and PC5 reads 0.0025. Matching each of tomorrow’s factors to today’s, by sign and by rank, removes the remaining flips and the swaps, and PC2 still reads −0.0161. The largest gap left between a matched figure and the test’s own is PC2’s, 0.0938.

The window closes that gap. When tomorrow’s weights are fitted on the 251 days before today, a window that leaves today’s return out, and then matched, the five figures land close to the test’s. The largest gap left is PC3’s, 0.0039. Fitting tomorrow’s weights on 251 days that still hold today’s return reads like the matched row instead, with PC2 at −0.0158. So leaving today out closes the gap, and the shorter window does not. Why the window pushes PC2 so far is not measured here.

![A whiteboard sketch titled “Tomorrow’s weights have seen today’s return”, drawn slowly, that holds its finished drawing for twelve seconds. A grey day axis comes first, with ticks marked “t − 252”, “t − 251”, “t − 1”, “t” and “t + 1”, and “…” where it skips the days between t − 251 and t − 1, so it is not to scale. Black dots on the axis at t and t + 1 are marked “today” and “tomorrow”. Three brackets follow above the axis, from the top down. A black bracket from t − 252 to t − 1 reads “day t’s weights: 252 days to t − 1”. A red bracket from t − 251 to t, its right end over today’s dot, reads “day t+1’s weights: 252 days to t”, with “already holds” and “today’s return” beside that end. A brass bracket runs from the red bracket’s left end to the black bracket’s right end and reads “tomorrow’s weights, 251 days, today left out”. Under the axis, red words read “PC2: tomorrow’s own weights, matched −0.0161”, brass words “→ today left out 0.0776”, black words “≈ the pair 0.0778”, and grey words “251 days that hold today: −0.0158”.](../docs/figures/pca_factor_momentum_sketch_window.gif)

The pair fixes all three at once. Both members of day t’s pair are read on day t’s weights, so a flipped sign flips both members and their product does not move, a swap cannot mix two factors inside one pair, and day t’s weights were fitted on a window that ends before either member’s return, so neither member’s weights have seen the other member’s return. It also asks the question the strategy bets on. The positions chosen on day t earn day t + 1’s return, so the strategy needs the same weighted portfolio of stocks to keep earning, which is what uₖ · rₜ₊₁ measures.

The figure’s bottom panel draws the table, with the band Lesson 4 explains shaded behind it.

## Lesson 2: leaving the mean in is a choice with a reason

The statistic is the ordinary correlation with one step left out. It does not subtract either series’ mean first, which is what makes it uncentred. For one factor’s 752 pairs:

```math
\rho = \frac{\sum_t f_t \, f_{t+1}}{\sqrt{\sum_t f_t^{2} \; \sum_t f_{t+1}^{2}}}
```

Two series, 1, 2, 3 and 2, 0, 1, show the difference. Their products sum to 5, and their squares to 14 and 5, so the statistic is 5/√70, which is positive. Their ordinary correlation is −0.5.

The reason is in Chan’s sentence. A factor return that keeps a steady value from one day to the next, positive day after day, is what “remain constant from the current time period to the next” describes. Subtracting the mean removes that steady part and keeps only the wiggles around it. The series 1, 1.2, 0.9, 1.1, 1.0 read one day apart shows it. Its uncentred statistic is 0.9798, close to perfect persistence, while its ordinary correlation is −0.8, because each wiggle reverses. The uncentred form also survives a sign flip, which Lesson 1 needs, because flipping both members of every pair leaves every product and every square where it was.

The price is that a few large days can carry the statistic. Every product counts by its size, so one day with large factor returns outweighs many quiet ones. PC2 shows how far that goes. Two days, 2007-08-09 and 2007-08-10, hold 97.04 percent of the sum of PC2’s squared daily products. So the share of pairs whose two members have the same sign sits beside each statistic. It is 0.5226 for PC1, 0.5146 for PC2, 0.5106 for PC3, 0.5173 for PC4 and 0.5000 for PC5, all close to a coin toss.

## Lesson 3: the factor return the forecast reads is the slope times the day’s singular value, and the intercept moves nothing

The revised MATLAB fits day t’s returns across the stocks, rᵢ, on an intercept a and five scores. Stock i’s score on component k is its weight times the singular value, uₖᵢ sₖ:

```math
r_i = a + \sum_{k=1}^{5} b_k \, s_k \, u_{k,i} + e_i
```

The weight vectors have length one and are at right angles to each other. Each also sums to zero across the stocks, because the window’s days were centred across the stocks before the decomposition. So the least-squares fit splits into one simple piece per term. The intercept is the day’s average return, and each slope is

```math
b_k = \frac{u_k \cdot r_t}{s_k}
```

The fitted value for stock i is then a plus the sum over k of uₖᵢ (uₖ · rₜ). The singular value cancels. So the number the forecast actually carries forward for factor k is uₖ · rₜ, which is the slope times sₖ, and that is the factor return this test pairs. A check on three of the file’s days confirms that each factor return equals the program’s fitted slope times its singular value.

The price is that the test does not read the coefficient the regression prints. That coefficient divides by sₖ, which changes from day to day, so a test on it would weight each day by 1/sₖ². Nothing in the strategy weights days that way.

The intercept is added to every stock’s forecast alike, so it cannot change which stocks rank highest. Dropping it leaves the program’s ranking unchanged on all 752 days t, a check made after the run. It is therefore not one of the factors tested. Its own figures are −0.0395 uncentred and −0.0401 as an ordinary correlation.

## Lesson 4: four of five passing says little

Here are the five verdicts beside the stocks, with a Newey-West t-statistic for each. The Newey-West t asks whether the products fₜ fₜ₊₁ average above zero. It divides their average by how far that average would wander by chance, widened for neighbouring days that move together and for days of different size. The p-value is one-sided, the chance that luck alone gives a t that large.

```math
\begin{array}{l|r|r|r|r|l}
\text{Factor, 752 pairs} & \text{Statistic} & \text{Percentile among the stocks} & \text{Newey-West } t & p & \text{Claim} \\ \hline
\text{PC1} & 0.0316 & 83.9378 & 0.9029 & 0.1833 & \text{holds} \\
\text{PC2} & 0.0778 & 95.6822 & 0.8254 & 0.2046 & \text{holds} \\
\text{PC3} & -0.0189 & 55.0950 & -0.4034 & 0.6567 & \text{does not hold} \\
\text{PC4} & 0.0305 & 83.4197 & 0.8743 & 0.1910 & \text{holds} \\
\text{PC5} & 0.0710 & 94.3005 & 1.2697 & 0.1021 & \text{holds} \\ \hline
\text{579 stocks, lower quartile} & -0.0729 & & & & \\
\text{579 stocks, median} & -0.0283 & & & & \\
\text{579 stocks, upper quartile} & 0.0137 & & & &
\end{array}
```

Each verdict is **exploratory** and stands on its own. The claim holds for PC1, PC2, PC4 and PC5, which are above 0 and above the median stock. It does not hold for PC3, which is above the median stock and below 0. The median stock’s statistic is negative, so on this file any factor above 0 clears the median too. Only the first half of the criterion did any work.

Three measurements say how little the four passes rest on.

1. **The band.** A series of returns that average zero, each one independent of the others and no more likely to be large than any other day’s, still gives a nonzero statistic over a finite sample. Over 752 pairs it lands inside ±1.96/√752 = ±0.0715 about 95 percent of the time, the same band the factor models post [explains for the monthly factors](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#lesson-4-a-verdict-can-follow-the-declared-criterion-and-still-rest-on-almost-nothing). PC2’s 0.0778 is outside it. PC5’s 0.0710 is just inside, and the other three well inside.
2. **The band and the t disagree about PC2.** The band is right only when a large return, up or down, makes a large one the next day no more likely. The Newey-West t measures how widely the products themselves scatter, and PC2’s statistic rests on two days, as Lesson 2 measured. Those two days, 2007-08-09 and 2007-08-10, fall in the week quantitative equity funds suffered the losses Khandani and Lo (2007) studied. Both days belong to the factor that moves the whole market. Without PMC they fall on PC1 and hold 94.61 percent of its squared products. With PMC in the file, PMC takes PC1 on both days and pushes that factor into PC2’s place, as Lesson 5 explains. So PC2 clears the band and its t is only 0.8254.
3. **A test across all five.** Testing five factors at once raises the chance that one looks significant by luck. The Benjamini-Hochberg procedure (Benjamini & Hochberg, 1995) holds the expected share of false findings among the factors declared significant to 5 percent. Run across the five p-values, it declares none. The smallest p-value is PC5’s 0.1021, so none would pass at 5 percent even tested alone.

![Two charts. The top chart is a step curve of the 579 stocks’ statistics, from about −0.23 to about 0.14, rising from 0 to 1, with the height at each point giving the share of stocks at or below it. A shaded band covers −0.0715 to 0.0715, a dotted line marks the median stock at −0.0283, and a solid line marks zero. Five filled dots sit on the curve at the factors’ statistics, each joined by a thin line to a hollow dot for the same factor without PMC. A column of labels on the right reads PC2 0.0778 → −0.0152, PC5 0.0710 → 0.0536, PC1 0.0316 → 0.0740, PC4 0.0305 → 0.0975 and PC3 −0.0189 → 0.0139. The bottom chart shows four markers for each factor, PC1 to PC5, over the same shaded band: a hollow circle for tomorrow’s own weights with the sign rule, a grey square for sign and rank matched, a brass diamond for weights fitted without today, and a black dot for the pair the test reads. The diamonds sit next to the black dots for every factor. PC2’s hollow circle sits below the band, near −0.11. The title calls the test exploratory, and the note says the file holds only survivors and that the bottom panel was measured after the verdicts.](../docs/figures/pca_factor_momentum.png)

*The top panel draws the verdicts. Each factor’s dot meets the stocks’ curve at its percentile, and only PC2’s filled dot sits outside the band. No stock’s statistic ties a factor’s, so the height where a dot meets the curve is the percentile the table gives. The bottom panel draws Lesson 1’s table, measured after the run. **Both are exploratory, and every figure in them is about survivors.***

## Lesson 5: one spliced symbol decides which factor misses

PMC is one symbol in the file that holds two price histories. It closes on 2004-03-12, has no close for 851 trading days, and resumes on 2007-08-01 as a different price history under the same ticker. The program fills each missing close with the last one it saw, so the file shows one day’s return of 1.8654, a rise of 186.54 percent, on 2007-08-01. The [factor models post](https://github.com/l3a0/quantitative-trading/blob/main/blog/factor-models-lessons.md#lesson-6-every-figure-that-touches-the-stocks-is-about-survivors) describes the same splice and what it does to the strategy’s printed returns.

A return that size dominates any window that holds it. Every day from 2007-08-02 to the end of the file fits its components on a window that holds it. That is 114 days, and 113 of them have a next day to pair with, the last being 2008-01-11. On each of those 113 days, one of the top five factors puts a weight of at least 0.5939 on PMC alone, out of a vector of length one spread across every stock in the window. PC2 carries it on 103 of the days, PC1 on 7 and PC3 on 3. From 2007-08-02 to 2007-08-10, PC1 carries PMC, with a weight between 0.9144 and 0.9223, so on 2007-08-09 and 2007-08-10 PC2 is the factor that is PC1 without PMC. Those are the two days that put PC2 outside the band. **These counts were measured after the run and decide nothing.**

![A whiteboard sketch titled “PMC takes PC1, so the usual PC1 lands in PC2”, drawn slowly, that holds its finished drawing for twelve seconds. Three grey shelves mark three slots, named “PC1”, “PC2” and “PC3” from the top. In the left column, a black box marked “usual PC1” sits in the first slot, under the heading “without PMC”. In the right column, a brass box marked “mostly PMC” and “weight 0.9144 to 0.9223” takes the first slot, under the heading “with PMC: days 2007-08-02 to 08-10”. An arrow runs from the left column’s box down to a second black box marked “usual PC1” in the right column’s second slot. The third slot stays empty in both columns. To the right, three bars stand on a grey baseline, all to one scale: a short grey bar marked “750 other days” for the other days together, and two red bars marked “08-09” and “08-10”, the second more than three times as tall as the first. Red words beside them read “97.04% of PC2’s” and “squared products”. Along the foot, grey words read “without PMC: the same two days, 94.61% of PC1’s”, and black words “PC2: 0.0778 with PMC → −0.0152 without”.](../docs/figures/pca_factor_momentum_sketch_rank_shift.gif)

Dropping PMC and running everything again moves every factor.

```math
\begin{array}{l|r|r}
\text{Factor} & \text{With PMC, 579 stocks} & \text{Without PMC, 578 stocks} \\ \hline
\text{PC1} & 0.0316 & 0.0740 \\
\text{PC2} & 0.0778 & -0.0152 \\
\text{PC3} & -0.0189 & 0.0139 \\
\text{PC4} & 0.0305 & 0.0975 \\
\text{PC5} & 0.0710 & 0.0536 \\ \hline
\text{Median stock} & -0.0283 & -0.0283
\end{array}
```

Without PMC, PC2 falls below 0 and PC3 rises above it, so the criterion would miss PC2 instead of PC3. PC1 and PC4 move outside the band, and PC2 moves back inside it. Benjamini-Hochberg still declares none. The smallest p-value is PC4’s 0.0319, and as the smallest of five it is held to a fifth of 5 percent, 0.01. The verdicts themselves read the file as the program does, with the forward fill, so this run moves no verdict.

## What this replication cannot say

Five things.

1. **Whether the factors persist on the S&P 600 as it stood each day.** Every figure here is about the companies still in the index on 2008-01-14.
2. **Whether the first edition’s factors persist.** Its day-t weights come from a window that ends on day t itself, so its day-t factor return helped choose its own weights and the next day’s did not. That pair is not like for like, and it was not tested.
3. **Whether the factors persist at another lag, frequency, lookback or number of factors.** Only lag 1 on daily returns, with a 252-day lookback and five factors, was tested.
4. **How much of the revised MATLAB’s 2 percent the factors’ momentum earns.** The test checks the assumption, not what the assumption pays.
5. **Whether the window effect in Lesson 1 holds on other files.** It was measured once, on this file, after the run.

## What this means for a trader

One habit for each lesson.

1. **Before correlating a re-estimated factor with itself, check its sign, its rank and what its weights were fitted on.** On this file the library’s signs were not even the same on two machines, and of the three, only leaving today’s return out of the window changed a verdict, putting PC2 and PC4 back above 0.
2. **Pick the statistic from the sentence being tested.** “Remain constant” is about a steady value, and the uncentred correlation keeps it. Then check how many days carry the result.
3. **Test the number the strategy actually carries forward.** Here that is the slope times the singular value, not the slope.
4. **Read a pass beside the band and a test across all the factors.** Four passes out of five, with none surviving a correction for testing five, is no evidence of momentum.
5. **Look for one bad record before trusting which factor failed.** One symbol with two price histories moved the miss from PC3 to PC2.

## References

1. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
2. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 162 and 164, and Example 7.4 at pp. 163 to 167. Page numbers here are the revised edition’s. The replication log cites the same passages by Kindle location, 4014 for p. 162 and 4051 for p. 164.
3. Khandani, A. E., & Lo, A. W. (2007). What happened to the quants in August 2007? Working paper, MIT.
4. Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.

*Not investment advice. Code: [the test of Example 7.4’s own factors](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor_momentum.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor_momentum_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/pca_factor_momentum_whiteboard.py), with the checks behind [the test’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor_momentum.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor_momentum_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_pca_factor_momentum_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-42-whether-example-74s-own-factor-returns-have-momentum-chans-quantitative-trading) that records every rule before its number.*
