# Chan’s Kelly of 18.4 does not reproduce on his own returns, and the CPPI loop he prints breaks the floor his text promises

*Chapter 8 of Algorithmic Trading finds a leverage by Monte Carlo and by historical growth, then caps the loss with portfolio insurance. Chan’s saved returns give a Kelly of 23.8, not 18.4, and his insurance loop falls past the floor his scheme keeps.*

## Why find a leverage without the bell curve

The leverage that grows capital fastest can still bring a loss of nearly everything along the way. Ernest Chan’s *Algorithmic Trading* makes that case in its Chapter 8. A fall from the account’s previous high is a drawdown, written here as a negative fraction, so a drawdown of −0.5 leaves the account at half its previous high. The usual answer to how much leverage to use is the Kelly leverage, the mean of the returns over their variance. Chan calls it “best viewed as an upper bound”, because on returns that are not a bell curve it “would have bankrupted us even in backtest” (Chan, 2013, Kindle edition, p. 252). The [post on capped Kelly allocation](https://github.com/l3a0/quantitative-trading/blob/main/blog/capped-kelly-allocation-lessons.md#why-a-leverage-cap-changes-the-answer) covers the upper-bound warning and the growth rate it rests on, from the first half of the same chapter.

The Kelly formula assumes returns follow a bell curve. Chapter 8 gives two ways to find a leverage without that assumption, and one way to cap the loss at whatever leverage is chosen.

1. **By Monte Carlo.** Draw many returns from a distribution fitted to the real ones, and find the leverage that grows the draws fastest. Chan says that where no formula exists, “This is where Monte Carlo simulations can help” (p. 254). The fitted distribution comes from the Pearson system (p. 257).
2. **By the historical growth rate.** Find the same leverage on the returns that actually occurred, at the risk of fitting one history (p. 260).
3. **With constant proportion portfolio insurance, CPPI.** This one does not choose the leverage. It trades only a slice of the account at the chosen leverage and resets the slice at each new high, so the account can never fall further below its high than the slice (p. 263). That limit is called the floor here.

### What the reproduction found

Chan runs all three methods on the returns of Example 5.1, his trade of the Australian dollar against the Canadian dollar. He published the script, `monteCarloOptimLeverage.m`, and this repository transcribed it and ran it on the returns saved by his earlier script, `AUDCAD_unequal.m`. The results fall into six groups.

1. **The book’s 18.4 does not reproduce on Chan’s own returns.** They give a Kelly of 23.845328 and a historical optimum of 23.721773, where the book prints 18.4 for both.
2. **Example 5.1’s own printed figures rule 18.4 out.** Any series with that example’s Sharpe ratio and APR, and a daily swing under 10 percent, has a Kelly of at least 20.891304 under each of three ways of compounding the APR.
3. **The script stops its search at 20.** Rerun on 200 different sets of random draws, it returns the cap itself 158 times. The book prints two simulated optima, 19 and 19.2. Searched without the cap, the 200 runs give 200 optima, and both of the book’s fall inside the middle 90 percent of them, the range a rule written down in advance allows. Neither falls inside the range of a rule chosen after the runs were seen, which reads only 40 of them.
4. **The least of 100,000 draws is deeper than any day in Chan’s backtest, because there are about 163 times as many draws.** The fitted distribution’s left tail is thinner than his history’s. Even so, on 78 of the 200 reruns the least draw puts the ruin leverage, where one day loses everything, at or below the Kelly.
5. **The CPPI code Chan prints, the loop in Box 8.6, breaks the floor the text says CPPI keeps.** The scheme the text describes keeps it, at a cost of about a quarter of the growth.
6. **Four of the book’s six drawdowns and growth rates fall outside the middle 90 percent of what 200 reruns give.**

**Every result here is exploratory.** Chan chose the strategy, the fitted distribution and the method, and the reproduction tests those choices on the same 612 returns, with no fresh data. It can say whether his numbers follow from his file and his script, and nothing about whether any leverage is safe to trade. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The returns, the draws and the seeds

**The returns.** Example 5.1 [trades AUD.USD against CAD.USD in weights a Johansen test sets each day](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-johansen-lessons.md#the-rule-and-the-files). Chan reports an APR of 11 percent and a Sharpe ratio of 1.6 for it (p. 168). His script saved its 612 daily returns, from 2009-12-18 to 2012-04-26, and the [post on that example](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-johansen-lessons.md#lesson-1-every-figure-matches-because-every-return-does) found every one of them reproduced from his closes. Chapter 8 reads those saved returns, and so does this replication. That post also shows the Kelly leverage of these returns is 23.845328 when the variance divides by n − 1, where n is the number of returns, as MATLAB’s `std` does.

**The growth rate.** Leverage f turns a day’s return R into f·R. Compounding multiplies 1 + f·R across the days, so the growth per day is the average of ln(1 + f·R) over the days.

```math
g(f) = \frac{1}{N} \sum_{t=1}^{N} \ln\bigl(1 + f R_t\bigr)
```

The [coin toss post](https://github.com/l3a0/quantitative-trading/blob/main/blog/coin-toss-expected-value-vs-growth.md#lesson-3-variance-is-a-cost-charged-against-growth) shows why this growth rate falls short of the average return. On a bell curve, g(f) becomes the parabola that the [Kelly leverage on SPY post](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives, which peaks at the Kelly leverage. A parabola is defined at every leverage, however large. The average above is not. Once f·R reaches −1 on any one day, that day loses everything, and the logarithm has no value.

**The ruin leverage.** That point is one over the size of the worst return. Above it, the worst day takes the whole account. So a growth curve computed from a sample of returns stops at the sample’s ruin leverage, where the parabola carries on.

**The draws.** The script fits a distribution to the returns’ mean, standard deviation, skewness and kurtosis, and draws 100,000 returns from it. Those four figures are built from the returns’ first four moments, where the moment of order k is the average of the k-th power. The fit comes from the Pearson system, a family of distributions with a member for nearly any four moments, sorted into numbered types. A number called κ, computed from the skewness and the kurtosis, picks the type. The [post on three hypothesis tests on TU momentum](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-hypothesis-tests-lessons.md#the-rule-the-file-and-the-three-tests) explains both. Here κ is 0.038081, which puts the returns in type IV, the type Chan names on p. 258.

The kurtosis is 7.821679, where a bell curve’s is 3, so the draws keep tails fatter than a bell curve’s, the kind the Kelly formula ignores. The fitted type IV has finite moments only below order 5.51, so its first five moments exist and its sixth does not. A bell curve has every moment, so a missing one is a sign of tails far heavier than a bell curve’s. Lesson 4 finds the draws’ left tail still thinner than that of Chan’s own history.

**The script’s cap.** Line 22 of the script searches for the best leverage with `fminbnd(minusGsim, 0, 20)`, MATLAB’s search over a bounded range. It never looks above 20. This replication runs the same search and also runs it without the cap, up to the ruin leverage, because Chan reports one figure from each, 19 from `fminbnd` and 19.2 that he calls unconstrained (Lesson 3).

**The seeds.** A seed is the number that fixes a run of random draws, so a rerun gives the same draws. Chan’s figures came from one set of draws nobody holds, and he warns they “are not exactly reproducible” (pp. 261 to 262). The TU post’s [Lesson 2](https://github.com/l3a0/quantitative-trading/blob/main/blog/tu-hypothesis-tests-lessons.md#lesson-2-a-simulated-count-lands-only-within-sampling-error-so-the-band-comes-first) explains why such a figure can only be judged against a range. So each simulated figure here comes from one seed, 20261012, named in writing before the run and called the declared seed. It is judged against 200 further seeds, 20261013 to 20261212.

**The band.** The book’s figure lands when it sits between the 5th and 95th percentiles of the same quantity across those 200 seeds, a range called its band here. The criteria were written down before any draw on the declared seed or the 200 further seeds. Trial runs on other seeds came before the criteria were written, and their results were seen.

**The verdicts.** Rules written down before the draws give each of Chan’s figures a verdict, and they treat three kinds of figure differently.

1. A figure computed without random draws **reproduced** when the computed value rounds to the book’s at the precision the book prints, and otherwise **did not reproduce**.
2. A simulated figure outside its band did not reproduce. One inside its band reproduced when the declared seed’s value rounds to the book’s. Otherwise it **reproduced with a gap**, and **the seed is the cause**, since Chan says his simulated figures cannot be reproduced exactly.
3. A claim is a sentence of Chan’s rather than a number, such as that two figures agree. It reproduced when the test written for it holds.

The rules that decide each result are in [Entry 43 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-43-monte-carlo-leverage-historical-optimization-and-cppi-chans-algorithmic-trading), which records each figure beside the test that computes it.

## Lesson 1: the 18.4 does not reproduce on Chan’s own returns

On p. 258 Chan says the returns give a Kelly leverage of 18.4. On pp. 260 to 261 he says the optimum of the historical growth rate is 18.4 as well, “again the same as the Kelly optimal f”. Neither figure is computed from a random draw, so each either matches or does not.

```math
\begin{array}{l|r|r}
 & \text{Kelly} & \text{Historical} \\
 & & \text{optimum} \\ \hline
\text{Computed} & 23.845328 & 23.721773 \\
\text{Book} & 18.4 & 18.4 \\
\text{Gap} & {+5.4} & {+5.3}
\end{array}
```

Neither figure reproduced. The gap is the computed figure minus the printed one. A different download of the data cannot explain the gap. These are the returns Chan’s own script saved, and his `AUDCAD_unequal.m` prints the same 23.845328 for them.

The claim the two figures were printed to support still holds. The historical optimum sits 0.005182 below the Kelly in relative terms, or 0.52 percent, inside the 1 percent the replication allowed in advance. So on this file the two methods agree, as Chan says, at about 23.8 rather than 18.4.

## Lesson 2: Example 5.1’s own figures rule 18.4 out

A Kelly leverage of 18.4 needs a series that matches the rest of the book too. Example 5.1 prints a Sharpe ratio of 1.6 and an APR of 11 percent (p. 168). Together they fix the Kelly, once the APR’s compounding is chosen.

The Sharpe ratio S fixes the daily mean m as S·σ / √252, where σ is the daily standard deviation. The APR then fixes σ. Under the second equation below, two values of σ fit the APR. The larger is near 0.2, a daily swing of about 20 percent with a Kelly near 0.5, so the smaller is the one used. The Kelly leverage then follows.

```math
\begin{gathered}
f^{*} = \frac{m}{\sigma^{2}} = \frac{S}{\sqrt{252}\,\sigma} \\
1 + \text{APR} = e^{\,252\,(m - \sigma^{2}/2)}
\end{gathered}
```

The second equation compounds the log growth, the mean less half the variance. Across the rounding of the printed figures, a Sharpe ratio from 1.55 to 1.65 and an APR from 10.5 to 11.5 percent, the Kelly runs from 21.558894 to 26.757652 under that compounding.

The low end of that range depends on how the APR compounds. The script the book names for Example 5.1, `AUDCAD_unequal.m`, compounds the daily returns themselves. So its APR is the growth rate g(f) at a leverage of 1, compounded over 252 days, which on the saved file is 0.112410. The second equation, on the saved file’s mean and its variance divided by n − 1, puts the APR at 0.112426. So the first of the three ways below is the closest to the script’s.

1. **Compounding the log growth**, as above, puts the lowest Kelly at 21.558894.
2. **Compounding 1 + m exactly** each day puts it at 22.065999.
3. **Taking the APR as 252 times the daily mean**, with no compounding, puts it at 20.891304.

None reaches 18.4. At a Sharpe ratio of 1.6, a Kelly of 18.4 needs an APR of 13.9 to 14.9 percent across the three, well above the printed 11.

A second check moves the draws instead. Shifting the fitted distribution’s mean so its Kelly is exactly 18.4, and keeping its spread and shape, changes only where it sits. On the same 200 seeds, the median uncapped optimum becomes 18.470198, close to the book’s 19 and 19.2. Under the shift, the book’s simulated optimum lands, and so do its drawdowns at the optimum and at a seventh of it and both of its growth rates. Lessons 3 and 6 give each of these figures. Only the drawdown at half the optimum still misses. Its −0.963 sits just past a band that runs to −0.953551.

**This is an inference, and it is exploratory.** The evidence favors Chapter 8 having run on a different series of returns, with a Kelly near 18.4, that nobody holds. That series would also disagree with Example 5.1’s own printed Sharpe ratio and APR. The evidence cannot tell when or how it differed from the saved file. Trial variants of the saved series, such as dropping the days whose return is zero or using log returns, reached no 18.4 either, and no test reruns them.

## Lesson 3: the script stops at 20, and the band for 19 and 19.2 changed after the seeds were seen

Chapter 8 reports two simulated optima. On p. 259 Chan says `fminbnd` “yields an optimal f of 19”. On p. 261 he calls the optimum “an unconstrained optimal f of 19.2”.

On the declared seed the script returns its cap of 20, the most it can return, and so it does on 158 of the 200 further seeds. Searched without the cap, the declared seed’s optimum is 22.295382. The 158 seeds split cleanly from the rest. A seed’s optimum always sits below its ruin leverage, because the growth rate plunges as the leverage nears it. So every seed whose ruin leverage is below 20 has an optimum below 20. The run also finds that every seed whose ruin leverage is 20 or more has an uncapped optimum above 20, the lowest at 20.075698. Those are exactly the seeds that sit on the cap. Neither of the book’s figures sits on it, so both are judged against the uncapped optimum.

![Two charts. The top chart redraws Figure 8.2, the growth rate per day against the leverage f from 0 to 27. A solid black curve for the 100,000 draws on seed 20261012 rises from zero to a peak of about 0.0048 near f of 22.3 and stops at a dotted vertical line at 23.217362, the draws’ ruin leverage. A grey curve for Chan’s 612 saved returns runs slightly above it, peaks near 0.0052 at about 23.7 and carries on to 27. A dashed vertical line at 20 marks the script’s cap, with a square marker where the black curve crosses it. A round marker shows the draws’ optimum without the cap, and a diamond and a triangle, almost on top of each other, show the saved returns’ optimum at 23.721773 and their Kelly at 23.845328. A shaded band from about 21.6 to 26.8 marks the Kelly range Example 5.1’s printed figures allow. Three short red ticks at the bottom mark the book’s 18.4, 19 and 19.2, all left of the band. The bottom chart plots the deepest drawdown in each 1,000 days of the draws for three accounts, with a dashed line at −0.5. A green step line for the scheme on p. 263 stays above the line throughout. A red step line for Box 8.6’s loop dips below it in most stretches, deepest at −0.848088 on day 37,071, and a grey line for the full account at f·D runs just below the red one, deepest at −0.871216 on the same day. The title calls the figure exploratory.](../docs/figures/monte_carlo_leverage.png)

*The top panel redraws the book’s Figure 8.2, “Expected Growth Rate g as Function of f”, on the declared seed, with the saved returns beside it. It adds the script’s cap, the ruin leverage where the draws’ curve ends, and the Kelly range from Lesson 2. The bottom panel is Lesson 5. Both read the declared seed only, because a picture built around one of Lesson 3’s two band rules would look like an endorsement of that rule.*

### Two rules for the band

Reading the band needs a choice of seeds. The rule declared before any draw used all 200. Its band runs from 16.622019 to 24.865122, and both 19 and 19.2 land inside it.

A seed with one very deep draw has a low ruin leverage, and its optimum is held down with it. Thirty seeds have an uncapped optimum at or below 19.2, and 28 at or below 19. All 30 have a ruin leverage below 20, the largest 19.147175. A band read without those 30 seeds would hold neither of the book’s figures.

The script’s capped optimum has a band of its own, and its 5th percentile is the same 16.622019, a point between the optima of two of those 30 seeds. The declared rule had set the capped band aside because its low end is made of such seeds, so a book figure could land there for that reason alone. The rule missed that the same seeds make the low end of the uncapped band too.

So the rule changed after the 200 seeds were seen. It now reads only the seeds whose ruin leverage is above 30.2, the ruin leverage the book prints from its least draw of −0.0331. Those are the seeds whose worst draw is no deeper than the book’s. Forty seeds qualify.

The table gives each rule’s band and whether the book’s 19 and 19.2 land in it, for the draws as fitted and for the draws moved to a Kelly of 18.4, as Lesson 2 moves them. Moving the draws makes every draw a little lower, which lowers every seed’s ruin leverage, so the rule chosen after reads 39 seeds there rather than 40.

```math
\small\begin{array}{l|r|r}
 & \text{As fitted} & \text{Moved to 18.4} \\ \hline
\text{Declared rule} & 16.622019 & 16.339353 \\
\text{all 200 seeds} & \text{to } 24.865122 & \text{to } 19.905622 \\
 & \text{both land} & \text{both land} \\ \hline
\text{Rule chosen after} & 22.969856 & 17.514982 \\
\text{ruin above 30.2} & \text{to } 25.374220 & \text{to } 20.017014 \\
 & \text{40 seeds} & \text{39 seeds} \\
 & \text{neither lands} & \text{both land}
\end{array}
```

Under the rule chosen afterwards, the simulated optimum did not reproduce. Under the declared rule it reproduced with a gap, and the seed was the cause. Both verdicts stay on the record. **The changed rule is exploratory,** and the only thing it rests on is Chan’s printed ruin leverage of 30.2. Under the draws moved to a Kelly of 18.4, both figures land under both rules, which fits Lesson 2.

One claim holds whichever band is read. Chan calls the simulated optimum “strikingly close” to the Kelly (p. 259). The Kelly of 23.845328 lies inside both bands, so that claim reproduced.

## Lesson 4: the draws hold a worse day than Chan’s backtest because there are about 163 times as many

On p. 260 Chan reports the most negative simulated return as −0.0331, so any leverage above 30.2 “will result in total loss”. No seed can be expected to give that exact figure. The least of 100,000 draws has its own distribution, though, and that distribution has a formula. The least draw is above x only when every draw is, so with F the fitted distribution’s chance of a draw at or below x:

```math
P\bigl(\min R \le x\bigr) = 1 - \bigl(1 - F(x)\bigr)^{100{,}000}
```

At −0.0331 that chance is 0.807083, inside the 5 to 95 percent range set in advance, so the book’s figure lands. Its ruin leverage of 30.2 lands too, since the chance of a ruin leverage at or below 30.2 is 0.806406. The declared seed’s least draw is −0.043071, a gap of −0.0100, so both reproduced with a gap and the seed is the cause.

The draws hold a worse day than the history, and the count of draws is the reason. The worst of Chan’s 612 backtest returns is −0.022031, a ruin leverage of 45.390502. The declared seed’s least draw is 1.9550 times as deep, nearly twice, and its ruin leverage is 23.217362. A fatter tail in the fitted distribution does not explain it. With 612 draws in place of 100,000, the same formula gives a chance of 0.091663, about 9.2 percent, that the least is at or below −0.022031. So a sample from the fit the size of Chan’s backtest would rarely reach his worst day, and the fit’s left tail is thinner than his history’s.

![A whiteboard sketch titled “The least of many draws goes deeper”, drawn slowly, with its finished drawing held for twelve seconds. Three rows of dots share one return scale, and each dot is a return or a draw below −0.012, placed at its value. The top row, in brass, is labelled “Chan’s 612 returns”, and its leftmost dot sits on a dashed brass line labelled “worst day −0.022031” that runs down through the rows below. The middle row is the first 612 of the declared seed’s draws, labelled “612 draws from the fit” and “reach it with chance 0.091663”, and its three dots all sit right of the dashed line, two of them almost on top of each other. The bottom row is all 100,000 draws, a dense black band near −0.012 that thins to scattered dots on the left, where a red dot marks its least, labelled “−0.043071”. Words beside the row read “100,000 draws, about” and “163 times as many”, then in red “least 1.9550 times as deep”. A grey note at the bottom reads “each dot a value below −0.012, to scale, draws from seed 20261012”.](../docs/figures/monte_carlo_leverage_sketch_least_draw.gif)

The declared seed’s ruin leverage is below the Kelly of 23.845328, so at the Kelly one draw on that seed loses everything. The same holds on 78 of the 200 further seeds. The top panel of the chart in Lesson 3 shows it: the draws’ curve ends before the Kelly, while the saved returns’ curve passes it far from ruin.

Across the 200 seeds, 42 have a ruin leverage below the script’s cap of 20, which means a least draw deeper than −0.05. They are the 42 seeds of Lesson 3 that do not sit on the cap. The formula above gives a chance of 0.149180 that a seed has such a draw, or about 29.8 seeds of 200. So 42 is more than the fit predicts, by 2.4 standard deviations of a binomial count, and the chance of 42 or more is about 1.3 percent.

Chan himself names the tradeoff between many simulated draws and a short history. A simulated drawdown “may be so rare” that it would not happen in a million years, while the history is “far too limited” to hold the worst case (p. 263).

## Lesson 5: Box 8.6’s loop breaks the floor the text says CPPI keeps

Chan describes CPPI on p. 263. Set aside a fraction D of the account for trading, trade it at leverage f, and keep the rest in cash. Whenever the account reaches a new high, reset the trading slice to D of it. The slice can lose at most itself, so the account can never fall more than D below its high, and the book promises “we won’t suffer a drawdown of more than −D”. On p. 264 he sets D at 0.5 and says the drawdown is under 0.5 “By design”.

Box 8.6, the code printed beside that sentence, does something else. Each day it trades at a leverage of f·D multiplied by one plus the drawdown of the unlevered returns. That drawdown belongs to the strategy’s returns at a leverage of 1, not to the account. At the script’s f of 20, f·D is 10, so the account moves ten times as much as those returns. A deep fall in the account is a much shallower fall in the unlevered returns, so the loop barely cuts its leverage while the account falls.

![A whiteboard sketch titled “Box 8.6’s loop barely cuts its leverage”, drawn slowly, with its finished drawing held for twelve seconds. Two grey axes sit under the caption “leverage on the account, from its high on day 169”. The upright one has “f·D = 10” at its top and “0” at its foot. The flat one runs from “day 170” to “day 303”, the first day the loop’s account is below −0.5. Two lines on the declared seed’s draws, one point a day, both start at 10. The red line stays near 10 and ends labelled “Box 8.6’s loop: 9.47” and “drawdown −0.504523, past −0.5”. The green line falls as it goes and ends labelled “the scheme on p. 263: 3.46” and “drawdown −0.407605, above −0.5”. A black note at the bottom reads “the loop’s 1 + drawdown of the unlevered returns to day 302: 0.946693”.](../docs/figures/monte_carlo_leverage_sketch_loop_leverage.gif)

The bottom panel of the chart in Lesson 3 sets the two forms of CPPI, Box 8.6’s loop and the scheme on p. 263, side by side on the declared seed. Beside them is the full account at f·D, meaning the whole account traded every day at a leverage of f·D, with no cash set aside and no insurance. The loop trades at that same leverage whenever the unlevered returns stand at their high, and with D at 0.5 that leverage is half of f.

The table gives each account a column. Its first row is the deepest drawdown on the declared seed. The next two are the 5th and 95th percentiles of that drawdown across the 200 further seeds, which bound its band. The last is the count of days the account spends below −0.5 on the declared seed.

```math
\small\begin{array}{l|r|r|r}
 & \text{Box 8.6's} & \text{Scheme} & \text{Full at} \\
 & \text{loop} & \text{on p. 263} & f \cdot D \\ \hline
\text{Deepest} & -0.848088 & -0.495638 & -0.871216 \\
\text{5th} & -0.902235 & -0.499628 & -0.922292 \\
\text{95th} & -0.742510 & -0.489965 & -0.763269 \\
\text{Days} & 5{,}681 & 0 & 6{,}034
\end{array}
```

The loop first falls below −0.5 on day 303 and reaches its deepest on day 37,071, the same day as the full account. It breaks the floor on all 200 further seeds. The scheme’s deepest is on day 33,785, and it stays above −0.5 on all 200. So the claim about the scheme the text describes reproduced, and the claim about the code the book prints did not.

The floor has a price. Measured as a fraction of the full account’s growth at f·D, the loop’s growth falls short by 0.014469, or 1.4 percent, which matches the book’s “very similar”. The scheme’s falls short by 0.255285, about a quarter. The book’s two growth rates on p. 264, 0.002484 for the loop and 0.002525 for the full account, differ by about 1.6 percent, and the book pairs that cost with a drawdown under 0.5 by design. Each form here keeps one of those two promises and not the other.

## Lesson 6: most of the book’s drawdowns and growth rates miss their bands

Chan reports the drawdown at the optimum and at fractions of it on p. 261, and the two growth rates on p. 264. The two tables set each beside the declared seed’s value and the band of the 200 further seeds, bounded by its 5th and 95th percentiles. On the draws, f is the script’s capped optimum, which is the cap of 20 on the declared seed. The first table holds the drawdowns at f, f / 2 and f / 7.

```math
\small\begin{array}{l|r|r|r}
 & f & f/2 & f/7 \\ \hline
\text{Book} & -0.999 & -0.963 & \text{about } {-0.5} \\
\text{Seed} & -0.991276 & -0.871216 & -0.416419 \\
\text{5th} & -0.999256 & -0.922292 & -0.468433 \\
\text{95th} & -0.979930 & -0.763269 & -0.302281
\end{array}
```

The second holds the growth of Box 8.6’s loop and of the full account at f·D, and the full account’s drawdown.

```math
\small\begin{array}{l|r|r|r}
 & \text{Growth,} & \text{Growth,} & \text{Drawdown,} \\
 & \text{loop} & f \cdot D & f \cdot D \\ \hline
\text{Book} & 0.002484 & 0.002525 & -0.9 \\
\text{Seed} & 0.003224 & 0.003271 & -0.871216 \\
\text{5th} & 0.002913 & 0.002955 & -0.922292 \\
\text{95th} & 0.003577 & 0.003623 & -0.763269
\end{array}
```

The drawdown at the optimum lands, and the declared seed’s value does not round to the book’s, so it reproduced with a gap. The book’s “frightening −0.999” (p. 261) is what a growth-optimal leverage does to these draws. The drawdowns at half and a seventh of the optimum are deeper in the book than anywhere in their bands, and both of the book’s growth rates sit below theirs, so those four did not reproduce. The full account’s −0.9 reproduced, for the reason the third detail below gives. Shifting the draws to a Kelly of 18.4, as Lesson 2 does, moves all but the drawdown at half the optimum into their bands, which fits the inference there.

Three details sit inside the two tables.

1. **The leverage at a seventh.** The declared seed’s f / 7 is 2.857143, since its f is the cap. The book’s leverage at a seventh, 2.7, is 19.2 over 7.
2. **The claim of similar growth holds.** Lesson 5 gives the figures, 1.4 percent on the declared seed against the book’s near 1.6 percent. The loop’s shortfall stays under 2 percent on all 200 seeds.
3. **Two prints of one quantity.** With D at 0.5, the full account at f·D is the account at f / 2. So the book’s “painful 0.9” (p. 264) and its −0.963 measure the same thing, and they disagree. The −0.9 reproduced because the book prints it to one decimal, which covers anything from −0.95 to −0.85 and so takes in the declared seed’s −0.871216. The two most likely come from different runs, and the book reports at least two, the 19 and the 19.2.

On Chan’s 612 real returns the drawdowns are far milder. At the historical optimum the deepest is −0.737560, and at the Kelly −0.739733. The script itself prints the drawdown on these returns at f / 1.4, with f its capped optimum of 20, and there the deepest is −0.526211. The draws at the optimum reach −0.991276. Part of that difference is length alone. The deepest drawdown can only grow as a path gets longer, so at the same daily risk a path of 100,000 days is all but certain to reach deeper than one of 612.

## What this replication cannot say

Four questions are beyond it.

1. **Which Pearson type the script’s draws came from.** The script draws with `pearsrnd`, MATLAB’s Pearson random-number function. Type IV is inferred from κ, the number that picks the type, and from the book’s “type is 4”. These draws follow the script’s in distribution, not draw for draw.
2. **What Chan’s returns were.** Lesson 2 shows that with a Kelly near 18.4 most of the book’s simulated figures land, and that no series matching Example 5.1 has such a Kelly. It cannot recover that series.
3. **Whether any leverage here is safe to trade.** Every figure is computed on 612 days of one strategy or on draws fitted to them. Chan notes that draws “miss some crucial serial correlations” (p. 263), and nothing here measures them.
4. **Which band the simulated optimum belongs against.** Both of the book’s optima land in the declared band, and neither lands in the band chosen afterwards. The second rests on one printed figure, the ruin leverage of 30.2.

## What this means for a trader

One habit for each lesson.

1. **Recompute a leverage from the returns before using it.** The book’s 18.4 sits 5.4 below what its own saved returns give, and only the returns can say which figure is theirs.
2. **Check a figure against the others printed beside it.** A Sharpe ratio and an APR together fix the Kelly, so one inconsistent figure shows up without the data.
3. **Read the bounds of a search.** An optimizer capped at 20 returns 20 whenever the answer lies past it, and the printout looks like an answer.
4. **Find the worst day in the sample before trusting the curve.** One day decides the ruin leverage, and a simulation with many more draws than the history is likely to hold a worse day, even from a distribution whose tail is no fatter.
5. **Run the code the text describes, not only the code printed beside it.** A loop that scales by the wrong drawdown gives up the guarantee that was the reason to use it.
6. **Judge a simulated figure against a band of seeds, and write the band down first.** One seed’s figure says little, and a band chosen after the seeds were seen is only exploratory.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.1, Figure 8.2, Boxes 8.1 to 8.6, with pages 168, 252, 254 and 257 to 264 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. Chan, E. P. `monteCarloOptimLeverage.m`, git blob `fc32599` under `public/img/book2/`, the book’s code, at commit `e4bc46f` of [ericnberwick/EpchanPreview](https://github.com/ericnberwick/EpchanPreview), a public copy of Chan’s code.
3. Heinrich, J. (2004). A guide to the Pearson type IV distribution. CDF/MEMO/STATISTICS/PUBLIC/6820.

*Not investment advice. Code: [the three methods](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/monte_carlo_leverage.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/monte_carlo_leverage_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/monte_carlo_leverage_whiteboard.py), with the checks behind [the methods’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_monte_carlo_leverage.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_monte_carlo_leverage_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_monte_carlo_leverage_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-43-monte-carlo-leverage-historical-optimization-and-cppi-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
