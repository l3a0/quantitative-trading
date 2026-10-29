# Capped at the leverage a broker would lend, Chan’s low-beta portfolio was never wiped out in a month, and its lead over the high-beta portfolio could still be noise

*Chan’s rule says a highly levered portfolio of low-beta stocks should out-compound an unlevered portfolio of high-beta stocks. At the leverage his beta match asked for, the levered portfolio lost more than its capital in June 2001. Capped at 2 or 5, the two ceilings his own text names, it never lost all its capital in a month. It led by 0.0934 and 0.1659 a year in compounded growth, and 83 months cannot tell either lead from zero.*

## Why cap the leverage

Ernest Chan’s *Quantitative Trading* states a rule on p. 191 of its Kindle edition: a “highly leveraged” portfolio of low-beta stocks should compound faster over the long run than an unleveraged portfolio of high-beta stocks.

A stock’s beta measures how far it tends to move with the market, so a stock with a beta of 2 tends to rise 2 percent when the market rises 1 percent. Levering a portfolio by L means borrowing so that it holds L dollars of stock for each dollar of capital. Returns, rates and growth here are written as fractions rather than percentages, so a month returning 0.05 gained 5 percent and one returning −1 lost the whole capital.

The [previous post](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#why-lever-the-low-beta-stocks) tested the rule on Chan’s own S&P 500 file and explains the setup in full. It levered the fifth of stocks with the lowest beta until its beta matched the highest fifth’s, which is the beta match Chan proposes on p. 189. The low fifth’s beta fell close to zero in spring 2001, so the [match asked for leverages up to 69.0762](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-2-matching-beta-divides-by-the-low-fifths-beta-and-in-spring-2001-that-beta-was-close-to-zero). At a leverage of 58.0262, the [levered portfolio lost more than its capital in June 2001](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-1-the-low-fifth-looked-like-the-better-portfolio-and-the-beta-match-ruined-it).

That ruin came from the leverage the beta match asked for. The rule itself names no leverage, so the previous test left open whether the rule holds at a leverage a broker would actually lend. Chan’s text gives two answers.

1. **A leverage of 2.** Under Regulation T, the Federal Reserve rule that caps what a broker may lend against stock, positions held overnight “allow only a leverage of 2” (p. 16). Chan repeats the overnight limit of 2 for a retail account on p. 112.
2. **A leverage of 5.** A margin is the share of a position’s value a trader puts up from their own capital, so a margin of 20 percent is a leverage of 1 / 0.20, or 5. Some brokers offer portfolio margin, which sets the margin by the portfolio’s estimated risk. On p. 16 Chan says portfolio margin “may require only 20 percent or less of overnight margin”, meaning a margin of 20 percent or less on positions held overnight. Five is the highest leverage the book puts a number on for stocks held overnight. A margin below 20 percent, which “or less” allows, would mean a leverage above 5.

Chan gives 20 percent for a portfolio of large-cap stocks hedged so that its long and short sides are equal in value. For a long-only portfolio of risky small-cap stocks he gives 50 percent, a leverage of 2. The low fifth is large-cap but long-only, so a broker might not lend it 5.

### What the test found

This repository wrote a plan that set the ceilings, the statistic, the correction and the possible outcomes, then reran the test with the leverage capped at each ceiling and drew five lessons.

1. **A plan written after the data was seen has to say what was seen.** The previous test had already shown the unlevered low fifth ahead, so a lead for the levered low fifth at either ceiling was predictable.
2. **Capping the leverage removed the ruin on this file.** No month at either ceiling lost all the capital, and no leverage below 13.4118 would have ruined any month in the file.
3. **A large point estimate can still be noise.** Both capped portfolios led the high fifth. Each measured lead is called a point estimate, and neither was large enough for a one-sided test at 5 percent to tell it from chance.
4. **Testing two ceilings costs a correction.** Two tests find a false gap more often than one, and the Benjamini-Hochberg correction raises the bar for each.
5. **The borrowing rate is a hidden assumption.** The run borrows at the Treasury bill rate. A broker charging 0.0946 a year above it at a ceiling of 2, or 0.0661 at 5, would erase the measured lead.

**Every figure here is exploratory.** An exploratory result can kill an idea or justify a closer look, and it confirms nothing however good the number. This one is exploratory because the plan was written after the previous test’s figures had shown which side was ahead, though before any capped number existed. Lesson 1 lists what had been seen.

Two more limits apply to every figure.

1. **The file is built from survivors.** It holds the stocks in the S&P 500 on 2007-11-23, with their prices back to November 1999, though some stocks’ prices start later. So every stock that left the index before 2007-11-23 is missing, and a stock that joined the index after November 1999 counts for the years it traded before it joined. The symbols WYN, DFS and SE each also carry a different, earlier company’s prices, up to 2002 for WYN and 2005 for the other two, before a gap of more than a year. Those earlier prices sit in one of the two fifths in 36 of the 83 months the portfolios were held. This post counted those months after the run.
2. **It is not a replication.** Chan prints no figure for this rule at any leverage, so there is no published number to reproduce, and nothing here tests his arithmetic.

The years tested are not fresh data for the rule either. Every one of them had passed by the time the book printed the rule, as the [previous post’s sixth lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-6-a-registered-result-on-years-the-claims-source-could-already-read-is-not-a-holdout) explains.

The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The test and the file

Everything the [previous post’s test section](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file) describes is unchanged. That covers Chan’s file, the betas, the two fifths, and the bill rate. It also covers the calendar. At each month-end the test sorts the stocks by beta and holds each fifth for the next month, which gives 83 holding months from December 2000 to October 2007.

The plan, written on 2026-10-11 before any capped number, kept the previous test’s statistic and its four possible outcomes, both set out below, and changed two things.

1. **The leverage.** At each month-end the low fifth is levered by L = min(k, C), where k is the leverage the beta match asks for and C is the ceiling, 2 or 5. A capped month returns rf + L × (r_low − rf), where r_low is the low fifth’s return and rf the bill rate for the month. Borrowing costs the bill rate, and the run charges no trading cost. The match never fell below 2.1826, so a ceiling of 2 is a constant leverage of 2.
2. **The correction.** The previous test used a single test in each direction. It called a gap real when its t, defined below, reached 1.645 in favour of Chan’s claim or −1.645 against it. With two ceilings to test, the Benjamini-Hochberg procedure runs at 5 percent across both, once in the claim’s direction and once against it. Lesson 4 explains it.

The statistic is the previous test’s. A month’s log growth is the natural log of one plus its return. For each month, d is the capped portfolio’s log growth less the unlevered high fifth’s. Twelve times the average of d is the gap in compounded growth a year.

The test divides that gap by its standard error, how far a gap measured over 83 months would typically wander by chance, and the result is the t. The standard error is the Newey-West kind, which allows each month’s d to be correlated with the d of the three months before it. The [previous post](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file) explains the Newey-West t.

The outcomes are the previous test’s four, with the correction deciding in place of those single tests. The previous test added its ruin outcome only after its first ruined month was visible. This time the plan wrote all four before the run.

1. **Contradicted by ruin.** Any capped month that returned −1 or less, losing all the capital or more, contradicts the claim.
2. **Holds.** The gap is positive and passes the correction in the claim’s direction.
3. **Contradicted.** The gap is negative and passes the correction in the contrary direction.
4. **Not decided.** Anything else. The run then reports Y, the gap the test could have found, which Lesson 3 explains.

Capping changes what is compared. A portfolio’s realised beta is the slope of its monthly return above the bill rate against that of SPY, a fund that tracks the S&P 500. Over the whole sample the capped portfolios’ realised betas were 0.8584 at a ceiling of 2 and 1.5831 at 5, against the high fifth’s 2.0671. Neither carried the high fifth’s market exposure. So the test asks whether a leverage a broker would lend is enough to out-compound the high fifth, rather than whether matching the betas is.

The [replication log’s Entry 48](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-48-the-low-beta-rule-at-leverage-a-broker-would-lend-chans-quantitative-trading) records the rules the result depends on and sets each figure in its tables beside the test that computes it.

## Lesson 1: a plan written after the data was seen has to say what was seen

The plan for this test was written before any capped return was computed. It still came after the previous test, which had shown five things about the same file.

1. The month-ends where the test sorts the stocks by beta, and the 83 months the portfolios were held.
2. The leverage k the beta match asked for each month.
3. The two months the beta match ruined.
4. Both fifths’ unlevered returns for the eight months held after the sorts from 2000-11-30 to 2001-06-29, so any capped return for those months could already be computed by hand.
5. Its side figures: both fifths’ Sharpe ratios (return above the bill rate divided by the size of its swings), the growth of both fifths and of SPY, both fifths’ realised betas and the low fifth’s Kelly leverage over the whole sample.

The side figures nearly fixed the gap’s sign in advance. Unlevered, the low fifth compounded at 0.1254 a year against the high fifth’s 0.1183, so it was already ahead. Its Kelly leverage over the whole sample, the leverage that makes wealth grow fastest, was 9.9884. Under a bell-curve approximation, growth rises with leverage up to the Kelly leverage, as the [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives. Both ceilings sit below 9.9884, so levering the low fifth by 2 or 5 was expected to widen its lead. A positive point estimate at either ceiling was predictable before the run.

So the result is exploratory however it came out. Even a gap that passed would have confirmed nothing, because the ceilings were chosen by someone who already knew which side was ahead. The plan said so in writing and listed the five things above, and that list is what lets a reader judge the result. What the run could still add is whether either gap could be told from noise, and whether any month at a ceiling of 5 came near ruin.

## Lesson 2: capping the leverage removed the ruin on this file

Neither capped portfolio lost all its capital in any month. The worst month at both ceilings was July 2002, whose portfolios were formed on 2002-06-28. June 2001, the month that ruined the beta match, lost far less at either ceiling than it did at the match.

```math
\small\begin{array}{l|r|r}
\text{Ceiling} & 2 & 5 \\ \hline
\text{Mean leverage} & 2.0000 & 3.5134 \\
\text{Months capped} & 83 & 20 \\
\text{June 2001} & -0.0835 & -0.2132 \\
\text{July 2002, the worst month} & -0.1479 & -0.3719
\end{array}
```

At the beta match, June 2001 returned −2.5053 at a leverage of 58.0262. At a ceiling of 2 the same month lost 0.0835 of the capital, and at 5 it lost 0.2132. The cap sets the leverage whenever k is above the ceiling. That is every month at a ceiling of 2, and 20 of the 83 months at 5, so the beta match set the leverage in the other 63.

A capped month returns rf + L × (r_low − rf). In a month when the low fifth trailed the bill rate, that return reaches −1, a loss of all the capital, at L = (1 + rf) / (rf − r_low), and any leverage above it loses more. The previous post computed that leverage for [June and September 2001](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-3-an-ordinary-month-did-it-so-the-caveats-advice-holds-and-its-reason-is-not-what-the-run-shows). Across all 83 months the smallest is 13.4118, for July 2002, when the low fifth returned −0.0733, its worst month. No leverage below 13.4118 ruins any month in the file, and both ceilings sit below it. This post measured that figure after the run, along with the June 2001 losses.

No ruin is not the same as no damage. At a ceiling of 5, July 2002 took 0.3719 of the capital in one month.

## Lesson 3: a large point estimate can still be noise

Both capped portfolios compounded faster than the unlevered high fifth’s 0.1183 a year.

```math
\begin{array}{l|r|r}
\text{Ceiling} & 2 & 5 \\ \hline
\text{Growth a year} & 0.2118 & 0.2843 \\
\text{Gap a year} & 0.0934 & 0.1659 \\
\text{Newey-West } t & 1.0715 & 1.2111 \\
\text{One-sided } p & 0.1420 & 0.1129 \\
Y & 0.2168 & 0.3407
\end{array}
```

Each gap is rounded from its own unrounded value, so it can differ in the last digit from the difference of the two rounded growth figures. The one-sided p-value is the chance of a gap at least this large if the true gap were zero, and Lesson 4 uses it.

A lead of 0.0934 a year sounds large. Whether it means anything depends on its standard error. The Newey-West standard error of the yearly gap is 0.0872 at a ceiling of 2 and 0.1370 at 5. If the true gap were zero, the measured gap would scatter around zero in a bell curve whose standard deviation is the standard error. Only 5 percent of a bell curve lies more than 1.645 standard deviations above its centre. So a one-sided 5 percent test calls a gap real when it sits at least 1.645 standard errors above zero. That puts the 5 percent line at 0.1434 at a ceiling of 2 and 0.2254 at 5. Both point estimates fall short of their line. Since t is the gap divided by its standard error, that is what a t below 1.645 means.

### The gap the test could have found

Falling short of the 5 percent line does not show that the true gap is zero. A test can miss a real gap, and how often it misses depends on the gap’s size. **Power** is the chance that a test finds a gap of a given size when that gap is real. **Y**, the detectable gap, is the gap this test finds four times in five, a power of 80 percent. If the true gap were Y, the measured gap would scatter around Y in a bell curve whose standard deviation is the same standard error. Take the point 0.8416 standard deviations below a bell curve’s centre. Eighty percent of the curve lies above it. So for the measured gap to land past the line four times in five, the line must sit 0.8416 standard errors below Y. The line sits 1.645 standard errors above zero, so Y sits 1.645 + 0.8416 standard errors above zero.

```math
Y = (1.645 + 0.8416) \times s
```

Here s is the yearly standard error. At a ceiling of 2, Y is 0.2168, and at 5 it is 0.3407. Each point estimate is under half of its own Y. The plan fixed this outcome’s wording before the run, and the run filled in both numbers: “At a ceiling of 2, no gap in compounded growth detectable above about 0.2168 a year over 83 months, where the point estimate is 0.0934.” The sentence for a ceiling of 5 reads the same with 0.3407 and 0.1659. At a ceiling of 2, the data are consistent with a true gap of zero, and with one of 0.0934. Eighty-three months cannot tell the two apart.

![Two charts stacked on one shared horizontal axis, the yearly gap in compounded growth between the capped low fifth and the unlevered high fifth, running from −0.4 to 0.8. The top chart is a ceiling of 2, a constant leverage of 2, with a standard error of 0.0872 a year. A grey bell curve centred on 0 carries the legend label “if the true gap were 0”. A dashed red vertical line is labelled “5 percent line, 0.1434”. A black bell curve of the same width, with the legend label “if the true gap were Y”, is centred on Y and labelled “Y, 0.2168, the gap a 5 percent test finds four times in five”. Its part to the right of the dashed line is shaded green, with the legend label “80 percent of that curve, past the line”. A red diamond on the baseline, to the left of the dashed line, is labelled “point estimate 0.0934, Newey-West t 1.0715”. The bottom chart is a ceiling of 5, a mean leverage of 3.5134 capped in 20 of 83 months, with a standard error of 0.1370 a year. Both curves are wider. The dashed line sits further right at 0.2254, the black curve is centred on Y at 0.3407, and the red diamond sits at 0.1659 with a t of 1.2111, again left of the line. The title reads “Exploratory: neither capped gap reaches the line a 5 percent test draws”.](../docs/figures/low_beta_capped.png)

*The grey curve is where the measured gap would land by chance if the true gap were zero, and the dashed line is where a one-sided 5 percent test starts calling the gap real. The black curve is where it would land if the true gap were Y, and 80 percent of it lies past the line. Both point estimates sit left of their line. This post measured the standard errors and the lines after the run, and every figure drawn is exploratory.*

From a ceiling of 2 to 5 the gap rose from 0.0934 to 0.1659, about 1.78 times. Its standard error rose from 0.0872 to 0.1370, about 1.57 times. So t moved only from 1.0715 to 1.2111. Suppose d were just the levered low fifth’s return above the bill rate, L × (r_low − rf), with L one number in every month. Then leverage would multiply the gap and its standard error by the same L, and t would not move at all. Three things break that.

1. d also subtracts the high fifth’s log growth, which leverage leaves alone.
2. d is log growth rather than a return, and log growth loses more to swings in return as leverage rises.
3. At a ceiling of 5 the leverage is not one number. It is 5 in the 20 months the cap sets it, and the beta match’s smaller k in the other 63.

So t can move either way as leverage changes. The chart above shows how little it moved from a ceiling of 2 to 5. From the top panel to the bottom one, the 5 percent line moves right along with the point estimate.

## Lesson 4: testing two ceilings costs a correction

Each ceiling is its own test. A single one-sided test at 5 percent calls a gap in its direction real when there is none 5 percent of the time. Run two, and the chance that at least one does so rises, to as much as twice as high. For two independent tests the chance is 1 − 0.95², or 0.0975. These two share the low fifth’s returns, so their chance sits below 0.0975. A trader who tried both ceilings and reported whichever passed would be quoting the better of two draws.

The **Benjamini-Hochberg procedure** corrects for that (Benjamini & Hochberg, 1995). It controls the false discovery rate, the expected share of false findings among the results declared significant, here at 5 percent. With m tests, it sorts the p-values from smallest to largest and requires the i-th smallest to be at most i/m × 0.05. The largest p-value that meets its bar passes, and so does every p-value below it. With two ceilings, both pass when both p-values are at most 0.05. Otherwise only the smaller can pass, and only if it is at most 0.025.

The run applied it twice, once in the claim’s direction and once against it. In the claim’s direction the one-sided p-values are 0.1420 at a ceiling of 2 and 0.1129 at 5. Both are above 0.05, and the smaller is above 0.025, so neither ceiling passes. Against the claim they are 0.8580 and 0.8871, further still, so neither ceiling passes in that direction either.

Here the correction changed nothing. Both p-values are above 0.05, so neither ceiling would pass a single uncorrected test either. The correction matters when a ceiling comes close to passing. Had a ceiling of 5 come in at a p-value of 0.04 beside a ceiling of 2 at 0.1420, a single test would have called the gap at 5 real, and the correction would not. The plan fixed the correction before the run, so it could not be dropped once a ceiling came close.

Y ignores the correction. It is the gap a single 5 percent test finds four times in five. The previous test’s plan defined Y that way, but the ruin ended that test before it reported one. The corrected test needs a true gap at least as large as Y to find it four times in five. If the other ceiling’s p-value is above 0.05, the corrected test needs a larger gap still, because this ceiling’s p-value must then be at most 0.025.

## Lesson 5: the borrowing rate is a hidden assumption

The run borrows at the three-month Treasury bill rate. A broker lending to a trader charges a **borrowing spread**, an extra yearly rate on top of a benchmark rate, on the money it lends. A trader levered L times borrows L − 1 for each unit of capital, so a yearly spread c costs (L − 1) × c / 12 of the capital each month.

The run searched for the spread at which the gap’s point estimate falls to zero. At a ceiling of 2 it is 0.0946 a year, and at a ceiling of 5 it is 0.0661. The larger lead breaks even at the smaller spread. The lead at 5 is about 1.78 times the lead at 2, but the portfolio at 5 borrows about 2.51 times as much. It borrows a mean of 2.5134 for each unit of capital, one less than its mean leverage of 3.5134, against 1 at a ceiling of 2.

![A whiteboard sketch, “Who breaks even first”, drawn slowly, one label at a time, then held for twelve seconds. A grey upright axis is labelled “gap a year”, and a grey axis along the bottom is labelled “yearly borrowing spread”. A grey line across the board just above the bottom axis is labelled “0” and marks a gap of zero. A black line starts on the upright axis at the height labelled “ceiling 2: 0.0934” and falls gently to the zero line, and its label reads “borrows 1 per unit of capital”. From the point where the black line reaches zero, a dashed grey drop falls to the bottom axis, labelled “0.0946”. A brass line starts higher, at the height labelled “ceiling 5: 0.1659”, and its label reads “borrows 2.5134”. It falls about two and a half times as steeply, passes under the black line partway across, and reaches the zero line first, further left, where a second dashed drop is labelled “0.0661”. Last comes “steeper line: smaller spread erases it”.](../docs/figures/capped_low_beta_sketch_break_even.gif)

Two cautions keep the break-even spreads from reading as room to spare.

1. The break-even spread is about the point estimate, which Lesson 3 showed cannot be told from zero, so a spread below it does not make the gap real.
2. The run says how far the cost could rise before the point estimate vanishes, and nothing about what a broker charged between 2000 and 2007.

## What this test cannot say

Six questions are beyond it.

1. **Anything confirmed.** The ceilings were chosen after the previous test’s figures had been seen, so even a gap that passed would have confirmed nothing. Only a run planned before any number, on data the plan had not seen, could confirm a ceiling. The plan sends both ceilings to such a run, unchanged, if either one holds here. Neither did.
2. **What the file’s makeup does to either side.** It lacks every stock that left the index before 2007-11-23, counts each stock that joined the index after November 1999 for the years it traded before it joined, and carries earlier companies’ prices under WYN, DFS and SE. Nothing here measures which fifth any of that flatters.
3. **Whether the rule holds in later years.** Every year here had passed by the time the book printed the rule. A separate test of the rule on later data, with the index as it stood each month, takes up that question at the leverage the beta match asks for rather than at either ceiling.
4. **What borrowing really cost.** The break-even spread bounds the cost the point estimate could bear, and says nothing about the rate a broker charged.
5. **Whether a margin call came inside a month.** A position levered 2 opens at a margin of 50 percent, the least Regulation T allows. FINRA Rule 4210, a rule of the brokers’ own regulator, then requires a maintenance margin of 25 percent. Below it the broker makes a margin call, a demand for more cash. A fall of a third in the stocks within the month takes the margin from 50 to 25 percent. At a leverage of 5 the account starts at a margin of 20 percent, the figure Chan gives for portfolio margin, so any fall within the month leaves it below that margin. Month-end prices cannot see either.
6. **Whether a broker would have lent 5.** Chan gives a margin of 20 percent for a hedged portfolio of large-cap stocks, and the low fifth is long-only.

## What this means for a trader

One habit for each lesson.

1. **List what the data had already shown before writing the plan.** A plan that comes after the data cannot test what the data already showed, and listing what was seen lets a reader judge how much the plan could still test.
2. **Know the smallest leverage that would have ruined at least one month in the history.** Here it was 13.4118, and both ceilings sat below it. At that leverage July 2002 would have lost all the capital by month-end, and a leverage just under it would have lost almost all of it. A longer history can only lower that figure, since every added month can bring a worse one. Losses within a month, which month-end prices cannot see, can lower it too.
3. **Report the gap a test could have found beside the gap it found.** A point estimate short of the 5 percent line means the test could not tell an effect that size from zero. Here each point estimate was under half of its Y, so the miss says little about whether an effect that size exists.
4. **Decide how many variants to test before the run, and correct for all of them.** Reporting the best of several variants quotes the best draw.
5. **Price the borrowing before believing a levered lead.** A lead earned at the bill rate shrinks as the spread rises, and faster at higher leverage.

## References

1. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
2. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 16, 112, 189 and 191 cited. The page numbers are the Kindle edition’s, which match the print edition’s.

*Not investment advice. Code: [the test](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_capped.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_capped_figures.py) and [the whiteboard sketch](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/capped_low_beta_whiteboard.py), with the checks behind [the test’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_capped.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_capped_figures.py) and [what the sketch draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_capped_low_beta_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-48-the-low-beta-rule-at-leverage-a-broker-would-lend-chans-quantitative-trading) that records the rules the result depends on and sets each figure in its tables beside the test that computes it.*
