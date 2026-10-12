# On the S&P 500 from 2009, Chan’s levered low-beta portfolio trailed the unlevered high-beta one by 0.0590 a year, a gap its test cannot tell from zero

*Chan’s rule says a levered portfolio of low-beta stocks out-compounds an unlevered one of high-beta stocks. On the S&P 500 from 2009 to 2026 the test cannot decide. No month ruined the levered portfolio, and in 2026 the low fifth’s beta turned negative.*

## Why test the rule on later data

Ernest Chan’s *Quantitative Trading* states the rule in its chapter summary: “Holding a highly leveraged portfolio of low-beta stocks should generate higher long-term compounded growth than holding an unleveraged portfolio of high-beta stocks” (Chan, 2021, location 4709). A stock’s beta measures how far it tends to move with the market, and leverage is the position divided by the trader’s own capital. The [post on the levered low-beta rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#why-lever-the-low-beta-stocks) explains beta, leverage and Chan’s argument, and tests the rule on his own S&P 500 file. That test levered the fifth of stocks with the lowest beta until its beta matched the highest fifth’s, and in June 2001 the levered portfolio lost more than its capital.

That earlier test could not say whether the rule holds. Its [sixth lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-6-a-registered-result-on-years-the-claims-source-could-already-read-is-not-a-holdout) gives two reasons. Chan’s file holds only the stocks still in the index in late 2007, and its years were past prices by the time the book printed the claim. This post runs the same test on data that fixes both. The stocks are the S&P 500’s members at each month-end from December 2008, companies that later left the index included, and every holding month comes after the first edition’s release in November 2008. This repository has read the rule only in the 2021 revised edition, and has not checked that the first edition prints it. A separate test caps the leverage on Chan’s file at what a broker would lend, and its write-up is a post of its own.

The holdout draws five lessons.

1. **A holdout that cannot decide still says how big a gap it could have seen.** The levered low fifth trailed by 0.0590 a year at a t of −0.4974. Measured after the run, a one-sided test at 5 percent rejects every levered advantage above 0.1360 a year, and December 2024 alone sets the sign of the gap.
2. **The same rule ruined a portfolio on the old data and not on the new.** The leverage peaked at 27.9727 rather than 69.0762, and the worst month on the new panel stayed above the loss that would have ruined it.
3. **A beta match stops being defined when the low fifth’s beta turns negative.** It did at the last four formations, and the owner ruled to skip them after seeing the first.
4. **A panel that lists the index as it stood each month moves the survivor problem rather than removing it.** Of the 107,115 months that companies spent in the index, 6,816 fail the check that ties each holding in IVV’s filings to a matching price, most because no price was found rather than because the price was wrong. The failures lean toward companies that left.
5. **Carrying a plan over unchanged needed a written list of what the new panel forces.** On Chan’s file, asking for a close a month ahead never removed a company that left, and here it would have looked ahead.

**The verdict is registered under two amendments, and every other figure here is exploratory.** A registered result is one whose test and criterion were written down before any number was seen. The plan for the earlier test, the changes this panel forces and the criterion all predate any beta or return computed on this panel. The first amendment is the earlier test’s own, which reads a levered month losing the whole capital as the claim contradicted, and the owner wrote it after June 2001 had been seen on Chan’s file. This run inherits it, and no month here triggers it. The second amendment skips a formation whose low fifth has a beta of zero or below, and the owner wrote it after the first such formation was seen on this panel. Lesson 3 says what had been seen. A **holdout** is data kept back from every decision about a test, so a result on it is a fresh check. Every holding month here comes after the first edition’s release, so this is a holdout for the claim as long as that edition prints it. The earlier test’s years come before both editions, so it was not one. Every other figure is a single measurement with no statistical test behind it, and each number this write-up measured after the run says so where it appears. **Every figure computed from the prices of IVV’s members reads a private archive of Alpha Vantage prices that stays outside the repository, so a reader cannot rerun them.** Every figure from Chan’s file reads only committed files. So does every count in Lesson 4 except the 6,943, because the members, each row check’s outcome and the schedules are committed. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The panel and what carried over

The test is the earlier one, with the changes Lesson 5 lists. The [earlier post’s section on the test](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file) states its five parts: betas from a year of daily returns, the lowest and highest fifths held one month, the low fifth levered by k, the high fifth’s mean beta over the low fifth’s, and a Newey-West t that has to reach 1.645 to decide. A t-statistic divides the average monthly gap by how far that average would typically wander by chance, and the Newey-West version allows for neighbouring months moving together.

1. **The members.** IVV is an S&P 500 index fund, and it files its holdings with the SEC at each quarter-end. Its 70 schedules from 2008-12-31 to 2026-06-30 give the members, and each schedule’s list carries forward to the months before the next one.
2. **The prices.** The members’ adjusted closes are 817 Alpha Vantage series downloaded 2026-10-05. The market is SPY’s Alpha Vantage series, downloaded 2026-10-11 for this run. The trading calendar is a committed series of SPY’s raw closes, downloaded 2026-10-03, and the borrowing rate is FRED’s TB3MS, the monthly average three-month Treasury bill rate, downloaded 2026-09-30.
3. **The window.** The span allows 212 formations, the month-ends where the stocks are sorted by beta, from 2008-12-31 to 2026-07-31. The skip amendment leaves out four, so the test reads 208 holding months, from January 2009 to April 2026. Between 389 and 501 stocks are eligible at each formation, and each fifth holds 77 to 100 of them.

## Lesson 1: a holdout that cannot decide still says how big a gap it could have seen

The verdict is **not decided**. The statistic is d, each month’s log growth of the levered low fifth minus that of the unlevered high fifth. Over 208 months, twelve times its mean is −0.0590, so the levered side compounded 0.0590 a year more slowly. The Newey-West t is −0.4974 at a lag of four months, far from either line at 1.645 and −1.645.

```math
\begin{array}{l|r}
\text{Months} & 208 \\
\text{Gap a year, levered low minus unlevered high} & -0.0590 \\
\text{Newey-West t, lag 4} & -0.4974 \\
\text{Y, the gap found four times in five} & 0.2948
\end{array}
```

A t that small says the data cannot tell the gap from zero. It does not say the gap is zero. The plan’s criterion reports how big a gap the test could have seen. **Y** is the yearly gap that a one-sided test at 5 percent finds four times in five, which is 1.645 plus 0.8416 standard errors. Here that is 0.2948 a year. A smaller gap is found less often, not never.

The write-up measured two more figures after the run. Neither is part of the registered criterion, and neither decides anything.

```math
\begin{array}{l|r}
\text{Standard error of the gap a year} & 0.1185 \\
\text{One-sided 95 percent upper bound on the levered advantage} & 0.1360
\end{array}
```

The gap plus 1.645 standard errors is the **one-sided 95 percent upper bound**. A one-sided test at 5 percent rejects every levered advantage above 0.1360 a year. Y and the bound answer different questions. Y is the gap the test could have seen, and the bound marks the advantages the data reject. The data do not reject a smaller advantage, and they cannot separate a levered advantage of a few hundredths a year from a deficit of the same size.

One month sets the sign of the gap. The Newey-West t and the bound both treat the monthly gaps as roughly normal, and one very large month strains that. In December 2024, d was −1.5624. Without that month, twelve times the mean of d over the other 207 months is +0.0313, so the levered side would have compounded faster. Without it and March 2026, where d was −1.1582, the figure is +0.0989. In March 2026 the leverage was 9.4342, and the low fifth lost 0.0716 against the high fifth’s 0.0463. Levered, that was a loss of 0.7005 of the capital, the second-worst levered month. The write-up measured all of these after the run. Dropping a month is not a test, so they decide nothing.

The figures beside the verdict decide nothing. Realised growth is twelve times the average monthly log return, the rate a portfolio actually compounded at, and realised beta is the slope of a portfolio’s monthly return above the bill rate on SPY’s.

```math
\begin{array}{l|r|r|r}
\text{Portfolio} & \text{Growth a year} & \text{Sharpe ratio} & \text{Realised beta} \\ \hline
\text{low fifth, levered to the high fifth's beta} & 0.1023 & 0.5223 & 1.8316 \\
\text{low fifth, unlevered} & 0.1069 & 0.8607 & 0.5580 \\
\text{high fifth, unlevered} & 0.1613 & 0.6770 & 1.6461 \\
\text{SPY} & 0.1378 & &
\end{array}
```

The low fifth again had the higher Sharpe ratio, the premise Chan’s argument starts from. Unlevered, the high fifth out-compounded it by 0.0543 a year, from the unrounded values, which the write-up measured after the run. That is the reverse of Chan’s file, where the unlevered low fifth grew faster, at 0.1254 a year against the high fifth’s 0.1183. Levering the low fifth did not close that gap. The levered side grew more slowly than the unlevered low fifth, and its realised beta of 1.8316 overshot the high fifth’s 1.6461, as on Chan’s file. No test sits behind any of these differences.

## Lesson 2: the same rule ruined a portfolio on the old data and not on the new

The leverage k divides the high fifth’s mean beta by the low fifth’s, so a low beta near zero asks for a very large k. The [earlier post’s second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-2-matching-beta-divides-by-the-low-fifths-beta-and-in-spring-2001-that-beta-was-close-to-zero) shows how that happened in spring 2001. On the new panel the low fifth’s beta stayed further from zero, and the high fifth’s beta was lower at the peak too.

```math
\begin{array}{l|r|r}
 & \text{Chan's file} & \text{IVV's members} \\ \hline
\text{Formations kept} & 83 & 208 \\
\text{Highest k} & 69.0762 & 27.9727 \\
\text{Formed} & \text{2001-04-30} & \text{2025-03-31} \\
\text{Low fifth's mean beta there, its lowest} & 0.0280 & 0.0563 \\
\text{High fifth's mean beta there} & 1.9349 & 1.5738 \\
\text{Formations with the low beta below 0.10} & 9 & 2 \\
\text{Formations with the low beta below 0.05} & 4 & 0 \\
\text{Mean k} & 7.8414 & 3.8247 \\
\text{Months ruined} & 2 & 0
\end{array}
```

On IVV’s members the low beta fell below 0.10 only at the formations of 2025-02-28 and 2025-03-31, at 0.0818 and 0.0563. The write-up measured those two counts, the 0.0818 and the high fifth’s 1.5738, after the run.

A lower leverage alone does not rule out ruin. The peak of 27.9727 is above 23.2017, the smallest leverage that would have ruined June 2001, so Chan’s June 2001, levered that far, would still have lost the whole capital. What decides ruin is each month against its own **ruin line**, the low fifth’s return at or below which the levered month loses the whole capital. The [earlier post’s third lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-3-an-ordinary-month-did-it-so-the-caveats-advice-holds-and-its-reason-is-not-what-the-run-shows) derives the line from k and the bill rate. The table also gives each month’s ruinous leverage, the smallest k that would have ruined it.

```math
\begin{array}{l|r|r|r|r|r}
\text{Month} & k & \text{Ruin line} & \text{Low fifth} & \text{Levered} & \text{Leverage that ruins} \\ \hline
\text{June 2001, Chan's file} & 58.0262 & -0.0144 & -0.0403 & -2.5053 & 23.2017 \\
\text{December 2024, IVV} & 12.3588 & -0.0776 & -0.0616 & -0.8014 & 15.4077 \\
\text{April 2025, IVV} & 27.9727 & -0.0324 & -0.0176 & -0.5856 & 47.6485 \\
\text{March 2020, IVV} & 3.4162 & -0.2926 & -0.1250 & -0.4278 &
\end{array}
```

Of the IVV figures in that table, the run’s own tests hold December 2024’s k, low-fifth return and levered return, and April 2025’s k. The write-up measured the rest after the run. On Chan’s file the match asked June 2001 for 2.50 times the leverage that ruins it. On IVV’s members it asked December 2024, the worst levered month, for 0.80 of it, the largest share of any month. December 2024 was the seventh-worst of the low fifth’s 208 months, and it sat 0.0161 above its line. April 2025 came closest to its line, 0.0148 above it, in the month the peak leverage applied to, because the low fifth lost only 0.0176. None of the 208 months fell at or below its own line.

The low fifth’s worst month shows the other half. In March 2020 it lost 0.1250, but the leverage then was 3.4162, so the line sat far below at −0.2926. Ruin needs a large k and a bad month at the same time. On Chan’s file they met in June 2001, and again in September 2001 for a fresh stake levered by the same rule. On IVV’s members the peak leverage met a month in which the low fifth lost only 0.0176, and the worst levered month still stayed above its line.

![Four charts in two columns. The left column is Chan’s file, holding months December 2000 to October 2007. The right column is IVV’s members, holding months January 2009 to August 2026. The top row shows each fifth’s mean beta at formation on one shared axis from −0.4 to 2.6, with a muted line at zero. In the top left, a muted grey line, the highest fifth, stays between about 1.5 and 2, and a black line, the lowest fifth, starts near 0.15, falls almost to zero in the first half of 2001, with a red dot labelled lowest kept, 0.0280, formed 2001-04-30, then climbs to between 0.4 and 0.7. In the top right, the highest fifth stays between about 1.3 and 1.9 apart from a spike to about 2.4 in 2010, and the lowest fifth stays between about 0.35 and 0.75 until 2024, then falls to a red dot labelled lowest kept, 0.0563, formed 2025-03-31, and sits near 0.2 until April 2026. Four hollow red circles below zero at the far right, in a shaded band, are labelled 4 skipped, formed 2026-04-30 to 2026-07-31, low fifth’s beta −0.0037 to −0.2083. The bottom row shows k on one shared log axis from 1.5 to 120. In the bottom left, k climbs from about 10 to a black dot labelled highest, 69.0762, formed 2001-04-30, with red dots labelled ruined 2001-06-29: k 58.0262 and ruined 2001-09-28: k 31.5098, then falls below 10 in 2002 and stays between about 2 and 5 from 2003 on. In the bottom right, k stays between about 2 and 5 from 2009 to 2023, climbs through 2024 to a red dot labelled worst month 2024-12-31: k 12.3588, levered return −0.8014, and peaks at a black dot labelled highest, 27.9727, formed 2025-03-31, then drops below 10, with the skipped months shaded at the far right and named in a legend. The title reads registered verdicts, exploratory paths.](../docs/figures/low_beta_holdout.png)

*Each value sits at the month it applied to, so the beta and the leverage formed on 2025-03-31 appear at April 2025. Both verdicts are registered, the one on Chan’s file under its ruin amendment and the one on IVV’s members under both amendments. Every path drawn is exploratory, and the right column reads the private archive, so a reader cannot redraw it.*

Why the low betas stayed further from zero after 2008 is not something this test measures. The panel is later and built differently, and its high fifth’s beta was lower at the peak, so the two columns differ in more than one way.

## Lesson 3: a beta match stops being defined when the low fifth’s beta turns negative

The match multiplies the low fifth’s beta by k to reach the high fifth’s. A beta of zero cannot be multiplied up to anything, and a negative beta would ask for a negative k, which means selling the low fifth short. The plan said such a formation stops the run rather than levering, and it said nothing about the verdict.

At the last four formations the span allows, the low fifth’s mean beta was below zero, each lower than the one before, from a barely negative −0.0037 to −0.2083. A beta below zero means that over the year of daily returns before the formation, the lowest fifth’s stocks moved, on average, slightly against the market.

```math
\begin{array}{l|l|r|r}
\text{Formed} & \text{Held to} & \text{Low fifth's mean beta} & \text{High fifth's mean beta} \\ \hline
\text{2026-04-30} & \text{2026-05-29} & -0.0037 & 1.8278 \\
\text{2026-05-29} & \text{2026-06-30} & -0.0652 & 1.8696 \\
\text{2026-06-30} & \text{2026-07-31} & -0.1429 & 1.9202 \\
\text{2026-07-31} & \text{2026-08-31} & -0.2083 & 1.9536
\end{array}
```

The order of events decides what the skip rule can claim.

1. The registered run reached the 2026-04-30 formation, whose low fifth had a mean beta of −0.0037, and stopped there. No leverage, return, growth figure or Sharpe ratio had been computed, and no earlier formation’s beta had been printed or read. The earlier formations were known to have positive low betas only because the run checks them in date order and stops at the first that is not.
2. The owner ruled that such a formation is skipped. Its holding month leaves every series, so the criterion, the ruin rule and every figure beside them read the same remaining months.
3. Only then did the run reach the three later formations. Whether any of them was also at or below zero was not known when the rule was written.

So the skip rule was chosen after one such formation was visible, and the test reads 208 months rather than 212. That is the price of keeping the label registered, and it is why the label names the amendment. The skips also end the comparison in April 2026 rather than August.

## Lesson 4: a panel that lists the index as it stood each month moves the survivor problem rather than removing it

Chan’s file holds only the companies still in the index in late 2007, so every figure on it is about survivors. A list of the members at each month-end includes the companies that later left. Each one still needs a price series, and the series has to belong to the company the filing names. A **member-month** is one company in the index for one month, and a **member row** is one company on one quarter’s schedule. The **row check against the filing** looks up the archive’s close on the last trading day on or before each schedule’s report date, and compares it with the price IVV’s filing printed for that holding. A row fails it in one of three ways.

1. **No series.** The archive holds no price series for the ticker.
2. **No close.** The series has no close on that day.
3. **A wrong price.** The close disagrees with the filing’s price.

```math
\begin{array}{l|r|r}
 & \text{Member-months} & \text{Member rows} \\ \hline
\text{In the panel, 2008-12 to 2026-08} & 107{,}115 & 35{,}205 \\
\text{Failing the row check against the filing} & 6{,}816 & 2{,}187 \\
\text{of them, no series} & 933 & 304 \\
\text{of them, no close} & 3{,}654 & 1{,}186 \\
\text{of them, a wrong price} & 2{,}229 & 697 \\
\text{of them, with a ticker absent from the last schedule} & 4{,}614 & \\
\text{of them, with a ticker still in the last schedule} & & 697 \\
\text{of them, from 2009 to 2015} & 5{,}891 &
\end{array}
```

Most failures are a missing price rather than a wrong one. Of the 6,816 failing member-months, 3,654 have no close and 933 have no series, against 2,229 whose close the filing disagrees with. The two counts of 697 among the rows match only by chance. One counts rows with a wrong price, and the other counts rows whose ticker is still listed.

The last schedule is IVV’s of 2026-06-30. A ticker missing from it marks a company that left the index, or one that only changed its ticker, and the check cannot tell the two apart. Of all 35,205 member rows, 26,353 carry a ticker still in that schedule, 74.9 percent. Of the 2,187 failing rows, only 697 do, 31.9 percent. So the failures lean toward companies that left, or toward tickers that changed. The write-up counted the 5,891 from 2009 to 2015, the failing rows’ split by outcome and the share of rows still in the last schedule after the run.

The monthly rule that decides who can be held leaves out 6,927 member-months on the committed list of series spans, and 6,943 on the series the run reads, each cut at its last day of trading. Membership is also coarse in time. Each of the 70 quarter-end schedules carries forward, so a company that joins or leaves between two schedules is dated up to two months late. Around 2013-09-30, a quarter whose filing prints only a summary, the 2013-06-30 schedule carries forward five months. The write-up counted that from the schedule dates after the run.

So the survivor problem shrank and moved. It no longer removes every company that left. It now removes the member-months the row check cannot tie to a matching price, mostly early in the panel and mostly under a ticker absent from the last schedule. Which fifth that flatters is not measured here.

## Lesson 5: carrying a plan over unchanged needed a written list of what the new panel forces

The plan said the earlier test’s specification carries over. Before any beta or return was computed on this panel, an audit of the plan against the data produced a written list of what the panel forces. The list has ten points of four kinds.

1. **Five change what the run computes.** They are the market series, the trading calendar, who is a candidate at a formation, the holding month and the span.
2. **Three restate a rule that carries over.** They are the beta window, two share classes of one company sitting in the same fifth, and days where a series jumps too far to be a price move, which are counted rather than refused.
3. **One corrects the survivor label,** which had said this panel has no survivor problem. Lesson 4 is what it has instead.
4. **One says the tests that need the archive run only where it is.**

The holding month changed most. The earlier test held a stock only if it had a close at the formation and at the next month-end. On Chan’s file no series ends before the file does, so that rule never removed a company that left. It removed only stocks missing a close at the next month-end, 17 of them across six formations, each with closes after the gap. The write-up counted those after the run. Here the rule would keep only the stocks already known to have stayed in trading for the month, which is knowledge the formation does not have. So a stock whose series stops inside the holding month now earns its return to its last close and holds cash after it.

Two exclusions still read the next month-end. A series whose last row is the formation day itself, and one with a hole at the next month-end but rows after it, are not held. At the 208 formations kept they leave out 12 and 4 member-months, beside the 97,667 covered there. That is small, and it is still a look ahead the run carries.

The market series changed too. Chan’s SPY column was saved on 2008-01-29, so the run recorded SPY’s Alpha Vantage series into the archive for this test, and the run read every price on the committed calendar. A day with no SPY close would have stopped the run, and none lacked one.

## What this holdout cannot say

Five questions are beyond it.

1. **Whether a smaller gap exists.** The test finds a gap below 0.2948 a year less than four times in five, and the point estimate of −0.0590 sits well inside that. The panel holds no months beyond these.
2. **What survivorship does to either side.** 6,816 member-months fail the row check against the filing, and 4,614 of them carry a ticker absent from the last schedule. Which fifth they would have joined is not measured.
3. **Whether fat tails caused the worst month.** Fat tails mean extreme months come more often than a bell curve allows, which is the reason Chan’s caveat at location 4700 gives for being wary of leverage. In December 2024 a k of 12.3588 turned the low fifth’s −0.0616 into a loss of 0.8014 of the capital. How near the run came to ruin rests on a handful of months.
4. **What the model’s half of the argument says.** Chan’s claim that both portfolios earn the same average return assumes they have the same market capitalisation and book value, and this panel holds neither.
5. **Whether the first edition prints the rule.** Every holding month comes after the first edition’s release in November 2008, which is what makes this a holdout. This repository has read the rule only in the 2021 revised edition, and has not checked that the first edition prints it.

## What this means for a trader

One habit for each lesson.

1. **Before reading a “no”, compute what the test could have seen.** An upper bound turns “not decided” into a statement about which advantages the data do not reject.
2. **Judge ruin month by month, against each month’s own ruin line.** A peak leverage well below June 2001’s still exceeded the smallest leverage that would have ruined June 2001.
3. **Decide in advance what a leverage formula does when its denominator reaches zero.** Here it did, four times in a row, and the rule came after the first.
4. **Ask which companies a point-in-time list still loses.** Here the failures sat mostly early in the panel, under tickers missing from the last schedule.
5. **List what the new data forces before rerunning an old plan.** A rule that only skipped missing closes on one file can look ahead on another.

## References

1. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Kindle locations 4684, 4700 and 4709.

*Not investment advice. Code: [the holdout](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_holdout.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_holdout_figures.py), with the checks behind [the holdout’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_holdout.py), [the numbers on Chan’s file](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_leverage.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_holdout_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-49-the-levered-low-beta-rule-after-the-book-on-ivvs-sp-500) that records the plan and every figure beside the test that computes it.*
