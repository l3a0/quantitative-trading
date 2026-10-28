# Capped at the leverage a broker would lend, Chan’s low-beta portfolio was never wiped out in a month, and its lead over the high-beta portfolio could still be noise

*Chan’s rule says a highly levered portfolio of low-beta stocks should out-compound an unlevered portfolio of high-beta stocks. At the leverage his beta match asked for, the levered portfolio lost more than its capital in June 2001. Capped at 2 or 5, the two ceilings his own text names, it never lost all its capital in a month. It led by 0.0934 and 0.1659 a year in compounded growth, and 83 months cannot tell either lead from zero.*

## Why cap the leverage

Ernest Chan’s *Quantitative Trading* states a rule on p. 191 of its Kindle edition: a “highly leveraged” portfolio of low-beta stocks should compound faster over the long run than an unleveraged portfolio of high-beta stocks. The [previous post](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#why-lever-the-low-beta-stocks) tested it on Chan’s own S&P 500 file and explains the setup, from beta and leverage to the Sharpe ratio and the Kelly leverage. It levered the fifth of stocks with the lowest beta until its beta matched the highest fifth’s, which is the beta match Chan proposes on p. 189. The low fifth’s beta fell close to zero in spring 2001, so the [match asked for leverages up to 69.0762](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-2-matching-beta-divides-by-the-low-fifths-beta-and-in-spring-2001-that-beta-was-close-to-zero). At a leverage of 58.0262, the [levered portfolio lost more than its capital in June 2001](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-1-the-low-fifth-looked-like-the-better-portfolio-and-the-beta-match-ruined-it).

That verdict is about the beta match. The rule itself names no number, so the question it left open is whether the rule holds at a leverage a broker would actually lend. Chan’s text gives two answers.

1. **A leverage of 2.** Under Regulation T, the Federal Reserve rule that caps what a broker may lend against stock, positions held overnight “allow only a leverage of 2” (p. 16). The book limits a retail account to 2 overnight (p. 112).
2. **A leverage of 5.** Some brokers offer portfolio margin, which sets the margin by the portfolio’s estimated risk. On p. 16 Chan says it “may require only 20 percent or less of overnight margin”, and a margin of 20 percent is a leverage of 5. Chan gives that figure for a portfolio of large-cap stocks hedged so that its long and short sides are equal in value. For a long-only portfolio of risky small-cap stocks he gives 50 percent, a leverage of 2. The low fifth is long-only and large-cap, so a broker might not lend it 5. Five is the highest leverage the book puts a number on for stocks held overnight, and its “or less” leaves room for more.

This repository reran the test with the leverage capped at each ceiling and drew five lessons.

1. **A plan written after the data was seen has to say what was seen.** The previous test had already shown the unlevered low fifth ahead, so a positive gap at either ceiling was predictable.
2. **Capping the leverage removes the ruin.** No month at either ceiling lost all the capital, and no leverage below 13.4118 would have ruined any month in the file.
3. **A large point estimate can still be noise.** Both capped portfolios led the high fifth, and neither lead reached the line a 5 percent test draws.
4. **Testing two ceilings costs a correction.** Two tests find a false gap more often than one, and the Benjamini-Hochberg correction raises the bar for each.
5. **The borrowing rate is a hidden assumption.** The run borrows at the Treasury bill rate, and a spread of 0.0946 a year over it at a ceiling of 2, or 0.0661 at 5, would erase the point estimate.

**Every figure here is exploratory.** An exploratory result can kill an idea or justify a closer look, and it confirms nothing however good the number. Three things make this one exploratory.

1. **The plan came after the previous test’s figures.** It was written before any capped number existed, but after the previous test had shown which side was ahead. Lesson 1 lists what had been seen.
2. **The file holds only survivors.** It is the S&P 500 as it stood on 2007-11-23, so every stock that left the index before then is missing.
3. **It is not a replication.** Chan prints no figure for this rule at any leverage, so there is no published number to reproduce, and nothing here tests his arithmetic.

The years are not new to the rule either. Chan already had every one of them when he wrote it, which the [previous post’s sixth lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-6-a-registered-result-on-years-the-claims-source-could-already-read-is-not-a-holdout) explains. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The test and the file

Everything the [previous post’s test section](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file) describes is unchanged. That covers Chan’s file, the betas, the two fifths, the bill rate, and the 83 holding months from December 2000 to October 2007. The plan, written on 2026-10-11 before any capped number, kept the previous test’s statistic and its four outcomes, and changed two things.

1. **The leverage.** At each month-end the low fifth is levered by L = min(k, C), the beta match k capped at a ceiling C of 2 or 5. A capped month returns rf + L × (r_low − rf), where r_low is the low fifth’s return and rf the bill rate for the month. Borrowing costs the bill rate, and the run charges no trading cost. The match never fell below 2.1826, so a ceiling of 2 is a constant leverage of 2.
2. **The correction.** The previous test decided with a single test in each direction, at a t of 1.645 or −1.645. With two ceilings to test, the Benjamini-Hochberg procedure runs at 5 percent across both, once in the claim’s direction and once against it. Lesson 4 explains it.

The statistic is the previous test’s. For each month, d is the capped portfolio’s monthly log growth, the natural log of one plus its return, less the unlevered high fifth’s. Twelve times the average of d is the gap in compounded growth a year. The test reads its Newey-West t at a lag of 3 months over the 83 months. That t allows each month’s d to move with the three months before it, as the [previous post explains](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file).

The outcomes are the previous test’s four, with the correction deciding in place of those single tests. This time the plan wrote all four before the run, the ruin case included. Any capped month at −1 or below contradicts the claim by ruin. The claim holds when the gap is positive and passes the correction in the claim’s direction. It is contradicted when the gap is negative and passes the correction in the contrary direction. Anything else is not decided, and the run reports it with Y, the gap the test could have found, which Lesson 3 explains.

Capping changes what is compared. Over the whole sample the capped portfolios’ realised betas were 0.8584 at a ceiling of 2 and 1.5831 at 5, against the high fifth’s 2.0671. Neither carried the high fifth’s market exposure, so the test asks whether a leverage a broker would lend is enough, not whether matched betas are. The [replication log’s Entry 48](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-48-the-low-beta-rule-at-leverage-a-broker-would-lend-chans-quantitative-trading) records every rule and sets each figure beside the test that computes it.

## Lesson 1: A plan written after the data was seen has to say what was seen

The plan for this test was written before any capped return was computed. It still came after the previous test, which had shown five things about the same file.

1. The calendar of formations, the month-ends where the test sorts stocks by beta, and of the holding months.
2. The leverage path k.
3. The two months the beta match ruined.
4. Both fifths’ unlevered returns for the first eight formations, so any capped return for those months could already be computed by hand.
5. Its side figures: both fifths’ Sharpe ratios, their growth, their realised betas and the low fifth’s full-sample Kelly leverage.

The side figures nearly fixed the sign in advance. Unlevered, the low fifth compounded at 0.1254 a year against the high fifth’s 0.1183, so it was already ahead. Its full-sample Kelly leverage was 9.9884, and under a bell-curve approximation growth rises with leverage up to the Kelly leverage, as the [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md#the-kelly-formula) derives. Both ceilings sit below 9.9884, so levering the low fifth by 2 or 5 was expected to widen its lead. A positive point estimate at either ceiling was predictable before the run.

So the result is exploratory however it came out. Even a gap that passed would have confirmed nothing, because the ceilings were chosen by someone who already knew which side was ahead. The plan said so in writing and listed the five things above, and that list is what lets a reader judge the result. What the run could still add is whether either gap could be told from noise, and whether any month at a ceiling of 5 came near ruin.

## Lesson 2: Capping the leverage removes the ruin

Neither capped portfolio lost all its capital in any month. The worst month at both ceilings was July 2002, whose portfolios were formed on 2002-06-28. June 2001, the month that ruined the beta match, lost far less at either ceiling than it did at the match.

```math
\begin{array}{l|r|r|r|r}
\text{Ceiling} & \text{Mean leverage} & \text{Months capped} & \text{June 2001} & \text{July 2002, the worst month} \\ \hline
2 & 2.0000 & 83 & -0.0835 & -0.1479 \\
5 & 3.5134 & 20 & -0.2132 & -0.3719
\end{array}
```

At the beta match, June 2001 returned −2.5053 at a leverage of 58.0262. At a ceiling of 2 the same month lost 0.0835 of the capital, and at 5 it lost 0.2132. The cap sets the leverage whenever k is above the ceiling. That is every month at a ceiling of 2, and 20 of the 83 months at 5, so the beta match set the leverage in the other 63.

The previous post computed [the smallest leverage that would have ruined each month](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-3-an-ordinary-month-did-it-so-the-caveats-advice-holds-and-its-reason-is-not-what-the-run-shows). For a month when the low fifth trailed the bill rate, it is (1 + rf) / (rf − r_low). Across all 83 months the smallest is 13.4118, for July 2002, when the low fifth returned −0.0733, its worst month. No leverage below 13.4118 ruins any month in the file, and both ceilings sit below it. The write-up measured that figure after the run, along with the June 2001 losses.

No ruin is not the same as no damage. At a ceiling of 5, July 2002 took 0.3719 of the capital in one month.

## Lesson 3: A large point estimate can still be noise

Both capped portfolios compounded faster than the unlevered high fifth’s 0.1183 a year.

```math
\begin{array}{l|r|r|r|r|r}
\text{Ceiling} & \text{Growth a year} & \text{Gap a year} & \text{Newey-West } t & \text{One-sided } p & Y \\ \hline
2 & 0.2118 & 0.0934 & 1.0715 & 0.1420 & 0.2168 \\
5 & 0.2843 & 0.1659 & 1.2111 & 0.1129 & 0.3407
\end{array}
```

Each gap is rounded from its own unrounded value, so it can differ in the last digit from the difference of the two rounded growth figures. The one-sided p-value is the chance of a gap at least this large if the true gap were zero, and Lesson 4 uses it.

A lead of 0.0934 a year sounds large. Whether it means anything depends on how far a gap measured over 83 months would typically wander by chance, which is its **standard error**. The Newey-West standard error of the yearly gap is 0.0872 at a ceiling of 2 and 0.1370 at 5. A one-sided 5 percent test calls a gap real when it sits at least 1.645 standard errors above zero, which puts the line at 0.1434 at a ceiling of 2 and 0.2254 at 5. Both point estimates fall short of their line, which is what a t below 1.645 means.

Falling short of the line does not show that the true gap is zero. A test can miss a real gap, and how often it misses depends on the gap’s size. **Power** is the chance that a test finds a gap of a given size when that gap is real. **Y**, the detectable gap, is the gap this test finds four times in five, a power of 80 percent. If the true gap were Y, the measured gap would scatter around Y with the same standard error. It lands past the line whenever it falls no more than 0.8416 standard errors short of Y, because 80 percent of a bell curve lies above 0.8416 standard deviations below its centre. So Y sits 1.645 + 0.8416 standard errors above zero.

```math
Y = (1.645 + 0.8416) \times s
```

Here s is the yearly standard error. At a ceiling of 2, Y is 0.2168, and at 5 it is 0.3407. Each point estimate is under half of its own Y. The plan’s fixed wording for this outcome says so: “At a ceiling of 2, no gap in compounded growth detectable above about 0.2168 a year over 83 months, where the point estimate is 0.0934.” The sentence for a ceiling of 5 reads the same with 0.3407 and 0.1659. The data are consistent with a true gap of zero, and with one of 0.0934. Eighty-three months cannot tell the two apart.

![Two charts stacked on one shared horizontal axis, the yearly gap in compounded growth between the capped low fifth and the unlevered high fifth, running from −0.4 to 0.8. The top chart is a ceiling of 2, a constant leverage of 2, with a standard error of 0.0872 a year. A grey bell curve centred on 0 is the one the legend names if the true gap were 0. A dashed red vertical line is labelled 5 percent line, 0.1434. A black bell curve of the same width is centred on Y, labelled 0.2168, the gap a 5 percent test finds four times in five, and its part to the right of the dashed line is shaded green, which the legend names 80 percent of that curve, past the line. A red diamond on the baseline marks the point estimate, 0.0934, with a Newey-West t of 1.0715, to the left of the dashed line. The bottom chart is a ceiling of 5, a mean leverage of 3.5134 capped in 20 of 83 months, with a standard error of 0.1370 a year. Both curves are wider. The dashed line sits further right at 0.2254, the black curve is centred on Y at 0.3407, and the red diamond sits at 0.1659 with a t of 1.2111, again left of the line. The title reads exploratory, neither capped gap reaches the line a 5 percent test draws.](../docs/figures/low_beta_capped.png)

*The grey curve is where the measured gap would land by chance if the true gap were zero, and the dashed line is where a one-sided 5 percent test starts calling it a gap. The black curve is where it would land if the true gap were Y, and four fifths of it lies past the line. Both point estimates sit left of their line. The write-up measured the standard errors and the lines after the run, and every figure drawn is exploratory.*

From a ceiling of 2 to 5 the gap rose from 0.0934 to 0.1659, about 1.78 times. Its standard error rose from 0.0872 to 0.1370, about 1.57 times. So t moved only from 1.0715 to 1.2111. Leverage multiplies the low fifth’s return above the bill rate and its swings by the same L. But d also subtracts the high fifth’s log return, which leverage leaves alone, and log growth gives up more to volatility as leverage rises. So nothing fixes t as leverage changes. Between these two ceilings, the ones the plan fixed, it rose only a little. The figure shows the same thing. From the top panel to the bottom one, the 5 percent line moves right along with the point estimate.

## Lesson 4: Testing two ceilings costs a correction

Each ceiling is its own test. A single one-sided test at 5 percent calls a gap in its direction real when there is none 5 percent of the time. Run two, and the chance that at least one does so rises, to as much as twice as high. Two independent tests reach 0.0975, and these two share the low fifth’s returns, so their chance sits below that. A trader who tried both ceilings and reported whichever passed would be quoting the better of two draws.

The **Benjamini-Hochberg procedure** corrects for that (Benjamini & Hochberg, 1995). It controls the false discovery rate, the expected share of false findings among the results declared significant, here at 5 percent. With m tests, it sorts the p-values from smallest to largest and requires the i-th smallest to be at most i/m × 0.05. The largest p-value that meets its bar passes, and so does every p-value below it. With two ceilings, both pass when both p-values are at most 0.05. Otherwise only the smaller can pass, and only if it is at most 0.025.

The run applied it twice, once in the claim’s direction and once against it. In the claim’s direction the one-sided p-values are 0.1420 at a ceiling of 2 and 0.1129 at 5. Both are above 0.05, and the smaller is above 0.025, so neither ceiling passes. Against the claim they are 0.8580 and 0.8871, further still, so neither ceiling passes in that direction either.

Here the correction changed nothing. Both p-values are above 0.05, so neither ceiling would pass a single uncorrected test either. The correction matters for the run that comes close. Had a ceiling of 5 come in at a p-value of 0.04 beside a ceiling of 2 at 0.1420, a single test would have called the gap at 5 real, and the correction would not. The plan fixed the correction before the run, so it could not be dropped once a ceiling came close.

Y ignores the correction. It is the gap a single 5 percent test finds four times in five, the definition the previous test’s plan wrote, though the ruin left that test without one. The corrected test needs a gap at least as large, and a larger one unless the other ceiling also clears 5 percent.

## Lesson 5: The borrowing rate is a hidden assumption

The run borrows at the three-month Treasury bill rate. A broker lending to a trader charges a **borrowing spread**, an extra yearly rate on top of a benchmark rate, on the money it lends. A trader levered L times borrows L − 1 for each unit of capital, so a yearly spread c costs (L − 1) × c / 12 of the capital each month.

The run searched for the spread at which the gap’s point estimate falls to zero. At a ceiling of 2 it is 0.0946 a year, and at a ceiling of 5 it is 0.0661. The larger lead breaks even at the smaller spread. The lead at 5 is about 1.78 times the lead at 2, but it borrows about 2.51 times as much, a mean of 2.5134 for each unit of capital against 1, so a smaller spread erases it.

Two cautions keep that from reading as a margin of safety. The break-even spread is about the point estimate, which Lesson 3 showed cannot be told from zero, so a spread below it does not make the gap real. And the run says how far the cost could rise before the point estimate vanishes, and nothing about what a broker charged between 2000 and 2007.

## What this test cannot say

Six questions are beyond it.

1. **Anything confirmed.** The ceilings were chosen after the previous test’s figures had been seen, so even a gap that passed would have confirmed nothing. Only a run planned before any number, on data the plan had not seen, could confirm a ceiling. The plan would have sent both ceilings to such a run only if one had held here, and neither did.
2. **What survivorship does to either side.** The file lacks every stock that left the index before 2007-11-23.
3. **Whether the rule holds in later years.** Chan already had every year here when he wrote the rule. A separate test of the rule on later data, with the index as it stood each month, takes up that question.
4. **What borrowing really cost.** The break-even spread bounds the cost the point estimate could bear, and says nothing about the rate a broker charged.
5. **Whether a margin call came inside a month.** Under FINRA Rule 4210’s maintenance margin of 25 percent, a position levered 2 gets a margin call, a broker’s demand for more cash, after a fall of a third within the month. Regulation T sets only the 50 percent needed to open it. At a leverage of 5 and a margin of 20 percent there is no cushion, so any fall within the month leaves the account below its margin. Month-end prices cannot see either.
6. **Whether a broker would have lent 5.** Chan gives a margin of 20 percent for a hedged portfolio of large-cap stocks, and the low fifth is long-only.

## What this means for a trader

One habit for each lesson.

1. **List what the data had already shown before writing the plan.** A plan that comes after the data cannot test what the data already showed, and listing what was seen lets a reader judge how much the plan could still test.
2. **Know the smallest leverage that would have ruined any month in the history.** Here it was 13.4118, and both ceilings sat below it. That figure is the most leverage a short history can show to be safe, and a longer history can only lower it, since every added month can bring a worse one.
3. **Report the gap a test could have found beside the gap it found.** A point estimate under half of Y means the test could not tell an effect that size from zero, so the miss says nothing either way about whether it exists.
4. **Decide how many variants to test before the run, and correct for all of them.** Reporting the best of several variants quotes the best draw.
5. **Price the borrowing before believing a levered lead.** A lead earned at the bill rate shrinks with every point of spread, and faster at higher leverage.

## References

1. Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, 57(1), 289–300.
2. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 16, 112, 189 and 191 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.

*Not investment advice. Code: [the test](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_capped.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_capped_figures.py), with the checks behind [the test’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_capped.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_capped_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-48-the-low-beta-rule-at-leverage-a-broker-would-lend-chans-quantitative-trading) that records the plan and every figure beside the test that computes it.*
