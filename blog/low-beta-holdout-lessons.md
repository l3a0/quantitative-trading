# On the S&P 500 from 2009, Chan’s levered low-beta portfolio trailed the unlevered high-beta one by 0.0590 a year, a gap its test cannot tell from zero

*Chan’s rule says a levered portfolio of low-beta stocks out-compounds an unlevered one of high-beta stocks. On the S&P 500 from 2009 to 2026 the test cannot decide. No month ruined the levered portfolio, and in 2026 the low fifth’s beta turned negative.*

## Why test the rule on later data

Ernest Chan’s *Quantitative Trading* states the rule in its chapter summary: “Holding a highly leveraged portfolio of low-beta stocks should generate higher long-term compounded growth than holding an unleveraged portfolio of high-beta stocks” (Chan, 2021, Kindle edition, p. 191). A stock’s beta measures how far it tends to move with the market, and leverage is the position divided by the trader’s own capital. The [post on the levered low-beta rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#why-lever-the-low-beta-stocks) explains beta, leverage and Chan’s argument, and tests the rule on his own S&P 500 file. That test levered the fifth of stocks with the lowest beta until its beta matched the highest fifth’s, and in June 2001 the levered portfolio lost more than its capital.

The earlier test found the rule contradicted on Chan’s file, but that file cannot settle whether the rule holds beyond it, and the same post’s [sixth lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-6-a-registered-result-on-years-the-claims-source-could-already-read-is-not-a-holdout) gives two reasons.

1. Chan’s file holds the stocks in the index in late 2007, so it lacks every company that left before then.
2. Its years were past prices by the time the book printed the claim.

This post runs the same test on data chosen to answer both, and Lesson 4 says how far it answers the first. The stocks are the S&P 500’s members at each month-end from December 2008, including companies that later left the index, and every holding month comes after the first edition’s release in November 2008. This post calls that list of members, with their prices, the panel. A **holdout** is data whose returns, and every figure computed from them, are kept back from every decision about a test, so a result on it is a fresh check. This repository has read the rule only in the 2021 revised edition, and has not checked that the first edition prints it. A separate test caps the leverage on Chan’s file at what a broker would lend, and the [post on the capped rule](https://github.com/l3a0/quantitative-trading/blob/main/blog/capped-low-beta-lessons.md) covers it.

### What the test found

The holdout draws five lessons.

1. **A holdout that cannot decide still says how big a gap it could have seen.** The levered low fifth trailed by 0.0590 a year at a t-statistic of −0.4974, far from the 1.645 or −1.645 a verdict needs. A one-sided test at 5 percent rejects every levered advantage above 0.1360 a year, and dropping either December 2024 or March 2026 alone turns the gap positive. After the run, the write-up measured the bound and the figures without those months, so neither is a verdict.
2. **The same rule ruined a portfolio on the old data and not on the new.** The leverage peaked at 27.9727 rather than 69.0762, and the worst month on the new data stayed above the loss that would have ruined it.
3. **A beta match stops being defined when the low fifth’s beta turns negative.** It did at the last four month-ends where the stocks were sorted. The repository’s owner ruled to skip any such month-end after seeing only the first.
4. **A panel that lists the index as it stood each month moves the survivor problem rather than removing it.** Of the 107,115 months that companies spent in the index, 6,816 fail a check that ties each holding in the filings of IVV, an S&P 500 index fund, to a matching price. Most fail because no price was found, not because the price was wrong. The failures lean toward companies that left, or toward tickers that changed.
5. **Carrying a plan over unchanged needed a written list of what the new panel forces.** The earlier test held a stock only if it had a close at the next month-end, which is not yet known when the stocks are sorted. On Chan’s file that rule removed mostly stocks with a gap in their prices. On this panel it would have dropped most stocks whose prices stop inside the holding month, and held the rest on an unchanged price the vendor went on printing after the price stopped moving.

**The verdict is registered under two amendments, and every other figure here is exploratory.** A registered result is one whose test and criterion were written down before anyone saw the number that decides it. An exploratory figure is one measured without that commitment, so it can rule out an idea or justify a closer look, but it is never a verdict. The plan for the earlier test, the changes this panel forces and the criterion all predate any beta computed on this panel, and any return of a portfolio sorted on beta. A test of another of the book’s rules had already computed the same members’ monthly returns, ranking them on the return in the same month a year before rather than on beta. An amendment is a dated change to the written plan that says what had been seen when it was written, and the verdict carries two.

1. **The ruin amendment.** The earlier test’s own amendment counts the claim as contradicted if any levered month loses the whole capital. The owner wrote it after seeing June 2001 on Chan’s file. This run inherits it, and no month here triggers it.
2. **The skip amendment.** It skips any formation, a month-end where the stocks are sorted by beta, whose low fifth has a beta of zero or below. The owner wrote it after seeing the first such formation on this panel.

Every holding month here comes after the first edition’s release, so this is a holdout for the claim as long as that edition prints it. The one exception is the skip rule, because the owner wrote it after seeing one formation’s low-fifth beta on this panel and knowing every earlier one was positive. Lesson 3 sets out the order of events. The earlier test’s years come before both editions, so the earlier test was not a holdout. Apart from the verdict and Lesson 1’s upper bound, every figure is a single measurement with no statistical test behind it. The upper bound comes from a one-sided test the write-up added after the run. Each number this write-up measured after the run says so where it appears.

**Every figure computed from the prices of IVV’s members or from SPY’s Alpha Vantage series reads a private archive of Alpha Vantage prices that stays outside the repository, so a reader cannot rerun them.** The figures from Chan’s file read only files saved in the repository. So does every count in Lesson 4 but one. That one is 6,943, the months of index membership that Lesson 4’s rule for who can be held leaves out on the archive’s series. Lesson 4’s other counts read files saved in the repository: IVV’s filed lists of holdings, the list of members, the result of checking each holding’s price against those filings, each series’ first and last day, the month-ends between those two days that lack a close, and the trading calendar. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The panel and what carried over

The test is the earlier one, with the changes Lesson 5 lists. The [earlier post’s section on the test](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#the-test-and-the-file) states it in five parts.

1. The data.
2. A beta from a year of daily returns.
3. The lowest and highest fifths, held one month.
4. The leverage k that lifts the low fifth’s beta to the high fifth’s.
5. A Newey-West t, where the claim holds at 1.645 or above and is contradicted at −1.645 or below.

A t-statistic divides the average monthly gap by how far that average would typically wander by chance, and the Newey-West version allows for neighbouring months moving together. Three pieces make up this panel’s data.

1. **The members.** IVV is an S&P 500 index fund, and it files its holdings with the SEC at each quarter-end. Its 70 schedules, the filed lists of holdings, from 2008-12-31 to 2026-06-30 give the members, and each schedule’s list carries forward to the months before the next one.
2. **The prices.** The members’ adjusted closes are 817 Alpha Vantage series downloaded 2026-10-05. The market is SPY, another S&P 500 index fund, as an Alpha Vantage series downloaded 2026-10-11 for this run. The trading calendar is a series of SPY’s raw closes from yfinance saved in the repository, downloaded 2026-10-03, and the borrowing rate is FRED’s TB3MS, the monthly average three-month Treasury bill rate, downloaded 2026-09-30.
3. **The window.** The span allows 212 formations, the month-ends where the stocks are sorted by beta, from 2008-12-31 to 2026-07-31. The skip amendment leaves out four, so the test reads 208 holding months, from January 2009 to April 2026. Between 389 and 501 stocks are eligible at each formation, and each fifth holds 77 to 100 of them.

## Lesson 1: a holdout that cannot decide still says how big a gap it could have seen

The verdict is **not decided**. The statistic is d, each month’s log growth of the levered low fifth minus that of the unlevered high fifth. Over 208 months, twelve times its mean is −0.0590, so the levered side compounded 0.0590 a year more slowly. The Newey-West t is −0.4974, far from either line at 1.645 and −1.645. Its lag of four months allows each month to move with the four before it.

```math
\begin{array}{l|r}
\text{Months} & 208 \\
\text{Gap a year, levered minus high} & -0.0590 \\
\text{Newey-West t, lag 4} & -0.4974 \\
\text{Y, found four times in five} & 0.2948
\end{array}
```

A t that small says the data cannot tell the gap from zero. It does not say the gap is zero. The plan’s criterion reports how big a gap the test could have seen. **Y** is how large a true yearly gap would have to be for a one-sided test at 5 percent to find it four times in five, where finding a gap means its t reaches 1.645. It is the sum of 1.645 and 0.8416, times the standard error of the yearly gap, which is how far that gap would typically wander by chance. The next table gives the standard error, and the [capped rule post’s third lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/capped-low-beta-lessons.md#lesson-3-a-large-point-estimate-can-still-be-noise) shows where 1.645 and 0.8416 come from. Here Y is 0.2948 a year. A smaller gap is found less often, not never.

The write-up measured two more figures after the run. Neither is part of the registered criterion, and neither is a verdict.

```math
\small\begin{array}{l|r}
\text{Standard error of the gap a year} & 0.1185 \\
\text{One-sided 95 percent upper bound} & 0.1360
\end{array}
```

The gap plus 1.645 standard errors is the **one-sided 95 percent upper bound**. A one-sided test at 5 percent rejects every levered advantage above 0.1360 a year. Y and the bound answer different questions. Y is the true gap the test could have seen, and the bound marks the advantages the data reject. The data do not reject a smaller advantage, and they cannot separate a levered advantage of a few hundredths a year from a deficit of the same size.

![A whiteboard sketch, “Y and the upper bound”, drawn slowly, one label at a time, then held for twelve seconds. A grey axis runs across the middle, labelled “gap a year”, with “0” written below it at zero. A red dot sits on the axis left of zero, labelled “measured gap” and “−0.0590”. A black bracket rises from the red dot, runs right above the axis and comes back down at the bound, with the grey label “1.645 × 0.1185” inside it and “upper bound 0.1360” above its right end. Red hatching fills the space above the axis from the bound to the axis’s right end, labelled “advantages the data reject”. A brass bracket hangs below the axis from 0 to a point well right of the bound, with “the gap found four times in five” inside it and “Y 0.2948” at its right end. A short brass tick on its bar marks where its first piece ends, and that point carries no figure. The first piece is the same length as the black bracket, shifted right by the distance from the red dot to 0. Under the bar, the first piece is labelled “the same 1.645 × 0.1185” and the rest “0.8416 × 0.1185”. Last comes “same standard error, different starting points”.](../docs/figures/low_beta_holdout_sketch_bound_and_y.gif)

Either of two months sets the sign of the gap on its own. In December 2024, d was −1.5624. Without that month, twelve times the mean of d over the other 207 months is +0.0313, so the levered portfolio would have compounded faster. The other month is March 2026, where d was −1.1582. Without it alone the figure is +0.0079, and without both months it is +0.0989. In March 2026 the leverage was 9.4342. The low fifth lost 0.0716 and the high fifth lost 0.0463. Levered, that was a loss of 0.7005 of the capital, the second-worst levered month. The best months pull the other way, though less far. Without February 2025, where d was +0.6118, the figure is −0.0947, and without both February 2025 and December 2024 it is −0.0042. The three largest gaps on each side all fall between December 2024 and March 2026, inside the only stretch, October 2024 to April 2026, in which the leverage exceeded 7. Apart from the leverage, which the run printed for every formation, the write-up measured all of these after the run. Dropping a month is not a test, so they decide nothing.

![A whiteboard sketch, “Either of two months sets the sign”, drawn slowly, one label at a time, then held for twelve seconds. A grey axis runs along the bottom, labelled “gap a year”, and a dashed grey upright rises from it at “0” through five rows. Each row prints its figure at the right edge in its dot’s colour, red below zero and green above it. The top row, “all 208 months”, is a red dot left of the upright, printed “−0.0590”. In each row below it, a black arrow starts from that same position and points to the row’s dot. For “without Dec 2024” it runs right, across the upright, to a green dot, “+0.0313”. For “without Mar 2026” it runs right to a green dot just past the upright, “+0.0079”. For “without Feb 2025” it runs left, less than half as far as the first arrow, to a red dot, “−0.0947”. For “without Dec 2024 and Feb 2025” it runs right to a red dot just touching the upright on its left, “−0.0042”. Last comes “dropping a month is not a test”.](../docs/figures/low_beta_holdout_sketch_dropped_months.gif)

The Newey-West t, Y and the bound all rest on one standard error and treat the average of the 208 monthly gaps as roughly normal, and two very large months strain that.

### Growth, Sharpe ratio and beta of each portfolio

The figures beside the verdict decide nothing. In the table, levered is the low fifth levered to the high fifth’s beta, and low and high are the unlevered fifths. Growth is realised growth, twelve times the average monthly log return, the rate a portfolio actually compounded at. Beta is realised beta, the slope of a portfolio’s monthly return above the bill rate against SPY’s monthly return above the bill rate.

```math
\small\begin{array}{l|r|r|r|r}
 & \text{Levered} & \text{Low} & \text{High} & \text{SPY} \\ \hline
\text{Growth} & 0.1023 & 0.1069 & 0.1613 & 0.1378 \\
\text{Sharpe ratio} & 0.5223 & 0.8607 & 0.6770 & \\
\text{Beta} & 1.8316 & 0.5580 & 1.6461 &
\end{array}
```

As on Chan’s file, the low fifth had the higher Sharpe ratio, the premise Chan’s argument starts from. Unlevered, the high fifth out-compounded it by 0.0543 a year, a gap the write-up measured after the run from the unrounded values. Chan’s file showed the reverse, with the unlevered low fifth growing faster, at 0.1254 a year against the high fifth’s 0.1183. Levering the low fifth did not close the 0.0543 gap. The levered side grew more slowly than the unlevered low fifth. Its realised beta of 1.8316 overshot the high fifth’s 1.6461, as on Chan’s file. No test sits behind any of these differences.

## Lesson 2: the same rule ruined a portfolio on the old data and not on the new

The leverage k divides the high fifth’s mean beta by the low fifth’s, so a low beta near zero asks for a very large k. The [earlier post’s second lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-2-matching-beta-divides-by-the-low-fifths-beta-and-in-spring-2001-that-beta-was-close-to-zero) shows how that happened in spring 2001. On the new panel the low fifth’s beta stayed further from zero at every formation kept, and the high fifth’s beta was lower at the peak leverage too. In the table, low beta and high beta are each fifth’s mean beta at formation. Formed is the formation with the highest k, the next two rows give the two fifths’ mean betas there, and that low beta was the lowest at any formation kept. The rows below 0.10 and below 0.05 count formations. Each formation’s k applies to the month after it, so the k formed on 2025-03-31 applied to April 2025.

```math
\small\begin{array}{l|r|r}
 & \text{Chan's file} & \text{IVV} \\ \hline
\text{Formations kept} & 83 & 208 \\
\text{Highest k} & 69.0762 & 27.9727 \\
\text{Formed} & \text{2001-04-30} & \text{2025-03-31} \\
\text{Low beta there, lowest} & 0.0280 & 0.0563 \\
\text{High beta there} & 1.9349 & 1.5738 \\
\text{Low beta below 0.10} & 9 & 2 \\
\text{Low beta below 0.05} & 4 & 0 \\
\text{Mean k} & 7.8414 & 3.8247 \\
\text{Months ruined} & 2 & 0
\end{array}
```

On IVV’s members the low beta fell below 0.10 only at the formations of 2025-02-28 and 2025-03-31, at 0.0818 and 0.0563. The run printed both fifths’ mean betas at every formation, the 0.0818 and the high fifth’s 1.5738 among them. After the run, the write-up counted from them the formations below 0.10 and below 0.05. On Chan’s file, the earlier write-up counted the 9 and 4 the same way, after that test’s run.

Why the low betas at the formations kept stayed further from zero after 2008 is not something this test measures. The panel is later and built differently, and its high fifth’s beta was lower at the peak, so Chan’s file and IVV’s members differ in more than one way.

### How close each month came to ruin

The peak leverage on IVV’s members was lower than on Chan’s file. That alone does not rule out ruin. The peak of 27.9727 is above 23.2017, the smallest leverage that would have ruined June 2001, so Chan’s June 2001, levered that far, would still have lost the whole capital. What decides ruin is each month against its own **ruin line**, the low fifth’s return at or below which the levered month loses the whole capital. The [earlier post’s third lesson](https://github.com/l3a0/quantitative-trading/blob/main/blog/levered-low-beta-lessons.md#lesson-3-an-ordinary-month-did-it-so-the-caveats-advice-holds-and-its-reason-is-not-what-the-run-shows) derives the line from k and the bill rate. The table gives three months’ k, ruin line, low-fifth return and levered return, with each month’s ruinous k, the smallest k that would have ruined it. Chan’s file fills the first column, and IVV’s members the other two.

```math
\small\begin{array}{l|r|r|r}
 & \text{June 2001} & \text{Dec 2024} & \text{Apr 2025} \\ \hline
k & 58.0262 & 12.3588 & 27.9727 \\
\text{Ruin line} & -0.0144 & -0.0776 & -0.0324 \\
\text{Low fifth} & -0.0403 & -0.0616 & -0.0176 \\
\text{Levered} & -2.5053 & -0.8014 & -0.5856 \\
\text{Ruinous k} & 23.2017 & 15.4077 & 47.6485
\end{array}
```

Of the IVV figures in that table, the checks written with the run cover December 2024’s k, low-fifth return and levered return, and April 2025’s k. The write-up measured the rest after the run. For Chan’s file, the earlier write-up measured June 2001’s ruin line and its ruinous k after that test’s run.

Two measures say how near a month came to ruin, and they pick different months.

1. **A month’s k as a share of its ruinous k.** For a month the levered side lost, that share is almost exactly the loss as a fraction of the capital, so the worst levered month has the largest share. On Chan’s file the match asked June 2001 for 2.50 times its ruinous k, a share the earlier write-up also measured after the run. On IVV’s members the match asked December 2024, the worst levered month, for 0.80 of it, the largest share of any month. December 2024 was the seventh-worst of the low fifth’s 208 months, and it sat 0.0161 above its line.
2. **The distance above the line.** By that measure, April 2025, the month the peak leverage applied to, came closest. That leverage raised the line to −0.0324, and the low fifth lost only 0.0176, so the month stayed 0.0148 above it.

After the run, the write-up measured the 0.80 share and checked that no month’s share was larger. It also ranked December 2024 seventh-worst, found the month that came closest and measured both margins. None of the 208 months fell at or below its own line.

Ruin needs a large k and a bad month at the same time. The low fifth’s worst month was a bad month without a large k. In March 2020 it lost 0.1250, but the leverage then was 3.4162, so the line sat far below at −0.2926. Levered, the month lost 0.4278, and only a leverage of 7.9837 would have ruined it. The write-up measured March 2020’s figures after the run, apart from the leverage, which the run printed. On Chan’s file a large k and a bad month met in June 2001, and again in September 2001 for a fresh stake, new capital put in at the start of that month and levered by the same rule. On IVV’s members the peak leverage met a month in which the low fifth lost only 0.0176, and the worst levered month still stayed above its line.

![Four charts in two columns. The left column is Chan’s file, holding months December 2000 to October 2007. The right column is IVV’s members, holding months January 2009 to August 2026. The top row shows each fifth’s mean beta at formation on one shared axis from −0.4 to 2.6, with a muted line at zero. In the top left, a muted grey line, the highest fifth, stays between about 1.5 and 2, and a black line, the lowest fifth, starts near 0.15, falls almost to zero in the first half of 2001, with a red dot labelled lowest kept, 0.0280, formed 2001-04-30, then climbs to between 0.4 and 0.7. In the top right, the highest fifth stays between about 1.3 and 1.9 apart from a spike to about 2.4 in 2010, and the lowest fifth stays between about 0.35 and 0.75 until 2024, then falls to a red dot labelled lowest kept, 0.0563, formed 2025-03-31, and sits near 0.2 until April 2026. Four hollow red circles below zero at the far right, in a shaded band, are labelled 4 skipped, formed 2026-04-30 to 2026-07-31, low fifth’s beta −0.0037 to −0.2083. The bottom row shows k on one shared log axis from 1.5 to 120. In the bottom left, k climbs from about 10 to a black dot labelled highest, 69.0762, formed 2001-04-30, with red dots labelled ruined 2001-06-29: k 58.0262 and ruined 2001-09-28: k 31.5098, then falls below 10 in 2002 and stays between about 2 and 5 from 2003 on. In the bottom right, k stays between about 2 and 5 from 2009 to 2023, climbs through 2024 to a red dot labelled worst month 2024-12-31: k 12.3588, levered return −0.8014, and peaks at a black dot labelled highest, 27.9727, formed 2025-03-31, then drops below 10, with the skipped months shaded at the far right and named in a legend. The title reads registered verdicts, exploratory paths: the beta match on Chan’s file and on IVV’s members from 2009.](../docs/figures/low_beta_holdout.png)

*Each value sits at the month it applied to, so the beta and the leverage formed on 2025-03-31 appear at April 2025. Both verdicts are registered, the one on Chan’s file under its ruin amendment and the one on IVV’s members under both amendments. Every path drawn is exploratory, and the right column reads the private archive, so a reader cannot redraw it.*

## Lesson 3: a beta match stops being defined when the low fifth’s beta turns negative

The match multiplies the low fifth’s beta by k to reach the high fifth’s. A beta of zero cannot be multiplied up to anything, and a negative beta would ask for a negative k, which means selling the low fifth short. The plan said such a formation stops the run rather than levering, and it said nothing about the verdict.

At the last four formations the span allows, the low fifth’s mean beta was below zero, each lower than the one before, from a barely negative −0.0037 to −0.2083. The table gives both fifths’ mean betas at each formation. A beta below zero means that over the year of daily returns before the formation, the lowest fifth’s stocks moved, on average, slightly against the market.

```math
\small\begin{array}{l|l|r|r}
\text{Formed} & \text{Held to} & \text{Low fifth} & \text{High fifth} \\ \hline
\text{2026-04-30} & \text{2026-05-29} & -0.0037 & 1.8278 \\
\text{2026-05-29} & \text{2026-06-30} & -0.0652 & 1.8696 \\
\text{2026-06-30} & \text{2026-07-31} & -0.1429 & 1.9202 \\
\text{2026-07-31} & \text{2026-08-31} & -0.2083 & 1.9536
\end{array}
```

The order of events decides what the skip rule can claim.

1. The registered run reached the 2026-04-30 formation, whose low fifth had a mean beta of −0.0037, and stopped there. The run had computed no growth figure or Sharpe ratio. Its loop had computed each earlier formation’s beta, leverage and monthly returns in memory as it went, and the stop discarded them before anyone printed or read any. The stop showed only that the earlier low betas were positive, because the run checks formations in date order and stops at the first that is not.
2. The owner ruled to skip such a formation. The rule drops its holding month from every series, so the criterion, the ruin rule and every figure beside them read the same remaining months.
3. Only then did the run reach the three later formations. Nobody knew, when the owner wrote the rule, whether any of them was also at or below zero.

So the owner chose the skip rule after one such formation was visible, and the test reads 208 months rather than 212. The verdict keeps its registered label only by naming that amendment. The four skipped formations were the last four. A different amendment, ending the run at the first of them and testing the months before it, would have read the same 208 months, so choosing it instead of the skip rule would not have moved the verdict. The skips also end the comparison in April 2026 rather than August.

## Lesson 4: a panel that lists the index as it stood each month moves the survivor problem rather than removing it

Chan’s file holds the companies in the index in late 2007, so it lacks every company that left before then. Three of its symbols, WYN, DFS and SE, also carry a different, earlier company’s prices before a gap of more than a year, and nothing here checks whether those companies were ever in the index. Their earlier prices enter the portfolios. The earlier test held a stock only if it had a close at the next month-end, and Lesson 5 shows that this rule left each earlier company out of the holding month in which its prices stopped. So no month in which a company stopped trading reaches the figures. Leaving those months out reads the next month-end, which the formation cannot know, and that is the look ahead that lesson describes.

A list of the members at each month-end includes the companies that later left. Each one still needs a price series, and the series has to belong to the company the filing names.

A **member-month** is one company in the index for one month, and a **member row** is one company on one quarter’s schedule. The **row check against the filing** looks up the archive’s close on the last trading day on or before each schedule’s report date. It then checks whether that close times the share count IVV’s filing printed for the holding matches the value the filing printed. A row fails it in one of three ways.

1. **No series.** The archive holds no price series for the ticker.
2. **No close.** The series has no close on that day.
3. **A wrong price.** The close times the share count disagrees with the filing’s value.

The last schedule is IVV’s of 2026-06-30. A ticker missing from it marks a company that left the index, or one that only changed its ticker, and its absence alone does not say which.

```math
\small\begin{array}{l|r|r}
 & \text{Months} & \text{Rows} \\ \hline
\text{In the panel} & 107{,}115 & 35{,}205 \\
\text{Failing the row check} & 6{,}816 & 2{,}187 \\
\text{failing, no series} & 933 & 304 \\
\text{failing, no close} & 3{,}654 & 1{,}186 \\
\text{failing, a wrong price} & 2{,}229 & 697 \\
\text{failing, not in last schedule} & 4{,}614 & \\
\text{failing, in last schedule} & & 697 \\
\text{failing, from 2009 to 2015} & 5{,}891 &
\end{array}
```

A blank cell marks a count the write-up did not make. The table gives the months not in the last schedule and the rows in it, which are the two counts the run’s report gives. Most failures are a missing price rather than a wrong one. Of the 6,816 failing member-months, 3,654 have no close and 933 have no series, against 2,229 whose close the filing disagrees with. The two counts of 697 among the rows match only by chance. One counts rows with a wrong price, and the other counts rows whose ticker is still in the last schedule.

Of all 35,205 member rows, 26,353 carry a ticker still in that schedule, 74.9 percent. Of the 2,187 failing rows, only 697 do, 31.9 percent. So the failures lean toward companies that left, or toward tickers that changed. After the run, the write-up counted the 5,891 failing member-months from 2009 to 2015, the failing rows’ split by outcome and the share of rows still in the last schedule.

A member can be held at a month-end only when its row passes the row check, its series has a close that day, and it either has a close at the next month-end or its prices stop inside the holding month. That monthly rule leaves out more member-months than fail the row check, because it leaves out every member-month that fails the check and then those missing a close. Going by the first and last date the repository lists for each series, it leaves out 6,927, and once the run cuts each series at its last day that traded and moved the price, it leaves out 6,943. Some series end in a run of days at an unchanged price or with no volume, and the cut drops that run with its closes. That leaves out a few member-months that needed one of those closes. It also lets in a few with no close at the next month-end but prices after it, because their series now stops inside the holding month. Both counts include the 6,816 that fail the row check.

Membership is also coarse in time. Each of the 70 quarter-end schedules carries forward, so the panel dates a company that joins or leaves between two schedules up to two months late. Around 2013-09-30, a quarter whose filing prints only a summary, the 2013-06-30 schedule carries forward five months. Lesson 5’s written list named those five months before the run.

So the survivor problem shrank and moved. The panel no longer loses every company that left. It now loses the member-months the row check cannot tie to a matching price, mostly early in the panel and mostly under a ticker absent from the last schedule. Nothing here measures which fifth that flatters.

## Lesson 5: carrying a plan over unchanged needed a written list of what the new panel forces

The plan said the earlier test’s specification carries over. Before the run computed any beta or return on this panel, an audit of the plan against the data produced a written list of what the panel forces. The list has ten points of four kinds.

1. **Five change what the run computes.** They are the market series, the trading calendar, who is a candidate at a formation, the holding month and the span.
2. **Three restate a rule that carries over.** They are the beta window, two share classes of one company sitting in the same fifth, and days where a series jumps too far to be a price move, which the run counts rather than stopping on.
3. **One corrects the plan’s statement that this panel has no survivor problem.** Lesson 4 is what it has instead.
4. **One says the tests that need the archive run only where it is.**

The holding month changed most. The earlier test held a stock only if it had a close at the formation and at the next month-end. On this panel that rule would keep the stocks already known to have stayed in trading for the month, which is knowledge the formation does not have. It would also keep a few whose series go on printing an unchanged price after the price stopped moving. So a stock whose series stops inside the holding month now earns its return to its last close and holds cash after it.

![A schematic whiteboard sketch, “What the formation cannot know”, drawn slowly, one label at a time, then held for twelve seconds. It carries no figures. A grey time axis runs along the bottom, with two dashed grey uprights labelled “formation” on the left and “next month-end” on the right. A black price line labelled “stock A” runs across the top, past both dates. A second black line starts left of the formation and stops between the two dates at a black dot, labelled “stock B’s series stops”. A red arrow points from the next month-end back to the formation, labelled “old rule: drop B, read from the future”. Last, a green line runs flat from B’s last close to the next month-end, labelled “new rule: B’s return to its last close, then cash”.](../docs/figures/low_beta_holdout_sketch_look_ahead.gif)

On Chan’s file the same rule removed 17 stocks across six formations, each missing a close at the next month-end, and the write-up counted those after the run. Fourteen had closes again within a few months. The other three were earlier companies whose prices stopped inside the holding month. Their symbols, WYN, DFS and SE, resumed more than a year later with a different company. No symbol in that file stops before the file’s last day. Those three companies did stop, though, and the rule left each of them out by reading the next month-end, which is the look ahead it would make on this panel.

Two exclusions still read the next month-end. The run holds neither a stock whose prices end on the formation day itself nor one with no close at the next month-end but prices after it. At the 208 formations kept they leave out 12 and 4 member-months, against the 97,667 the monthly rule kept at those formations. That is small, and it is still a look ahead the run carries. The cut at each series’ last day that traded and moved the price looks ahead too, because only the rows after a formation show whether a run of days at an unchanged price or with no volume ever ends.

The market series changed too. Chan’s SPY column was saved on 2008-01-29 and holds no prices after 2007, so the repository’s downloader saved SPY’s Alpha Vantage series into the archive on 2026-10-11, before the run read it. The run read every series, SPY’s included, on the days of the calendar saved in the repository. A day with no SPY close would have stopped the run, and none lacked one.

## What this holdout cannot say

Five questions are beyond it.

1. **Whether a smaller gap exists.** The data reject a levered advantage above 0.1360 a year, a figure measured after the run. They cannot tell a smaller advantage, or a deficit of similar size, from zero, and the test finds a true gap below 0.2948 a year less than four times in five. The test already reads every month that its span and the skip rule allow.
2. **What survivorship does to either side.** 6,816 member-months fail the row check against the filing, and 4,614 of them carry a ticker absent from the last schedule. Nothing here measures which fifth they would have joined.
3. **Whether fat tails caused the worst month.** Fat tails mean extreme months come more often than a bell curve allows, which is the reason Chan’s caveat on p. 189 gives for being wary of leverage. In December 2024 a k of 12.3588 turned the low fifth’s −0.0616 into a loss of 0.8014 of the capital. How near the run came to ruin rests on a handful of months.
4. **What the Fama-French model’s half of the argument says.** The first step of Chan’s argument comes from the Fama-French model, which ties a stock’s expected return to its beta, its market capitalisation and its book-to-price ratio. Under that model the two portfolios earn the same average return once their betas match, provided their stocks have the same average market capitalisation and book value. This panel holds no market capitalisation or book value, so the test cannot check that condition.
5. **Whether the first edition prints the rule.** Every holding month comes after the first edition’s release in November 2008, which is what makes this a holdout. This repository has read the rule only in the 2021 revised edition, and has not checked that the first edition prints it.

## What this means for a trader

One habit for each lesson.

1. **Before reading “not decided” as a no, compute what the test could have seen and what it rules out.** Y is the true gap the test would find four times in five, and the upper bound marks the advantages the data reject.
2. **Judge ruin month by month, against each month’s own ruin line.** A peak leverage well below June 2001’s still exceeded the smallest leverage that would have ruined June 2001.
3. **Decide in advance what a leverage formula does when its denominator reaches zero.** Here it did, four times in a row, and the rule came after the first.
4. **Ask which companies a point-in-time list still loses.** Here the failures sat mostly early in the panel, under tickers missing from the last schedule.
5. **List what the new data forces before rerunning an old plan.** A rule that reads the next month-end looks ahead on any file. On one file it mostly dropped stocks with a gap in their prices, and on another it would drop most stocks whose prices stop inside the holding month.

## References

1. Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Pages 189 and 191 cited. The page numbers are the Kindle edition’s, which match the print edition’s.
2. Chan, E. P. (2009). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business*. Wiley. Released in November 2008, and cited for that date only.

*Not investment advice. Code: [the holdout](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_holdout.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_holdout_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/low_beta_holdout_whiteboard.py), with the checks behind [the holdout’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_holdout.py), [the numbers on Chan’s file](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_leverage.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_holdout_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_low_beta_holdout_whiteboard.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/quantitative-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-49-the-levered-low-beta-rule-after-the-book-on-ivvs-sp-500) that records the rules the result depends on and sets each figure in its tables beside the test that computes it.*
