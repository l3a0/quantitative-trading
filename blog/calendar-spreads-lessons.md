# Chan’s calendar spreads hold for natural gas, and gasoline’s pass vanishes once the simulated contracts move like real ones

*A claim with no number needs a pass mark written down before the run, and a pass mark is only as good as the simulation behind it.*

## Why test a claim that prints no number

Ernest Chan’s *Quantitative Trading* names calendar spreads as “the simplest examples of cointegrating futures pairs” (Chan, 2021, location 3951). A calendar spread is a long position in one commodity’s futures for one delivery month and a short position in the same commodity for another. Two prices **cointegrate** when some combination of them keeps returning to a fixed average, which is what a trade on the spread between them needs. Chan prints no figure for the claim and works no example.

His later book, *Algorithmic Trading*, qualifies it. Calendar spreads “do not generally mean-revert”, he writes there (Chan, 2013, location 2321). A few pages on he finds one that does. The 12-month calendar spread of crude oil, taken in logs, keeps returning to its average at 99% confidence, with a **half-life** of 36 days, the time a gap from the average takes to close halfway (locations 2461 and 2471). So the later book doubts the earlier claim in general and then finds an exception. This repository wrote that doubt down before computing any statistic, so neither verdict below can be presented afterwards as a surprise.

A sentence with no number is still a claim a reader might act on, so it is worth checking. This repository tested every pair of neighbouring contracts in the free settlement prices the US Energy Information Administration (EIA) publishes for natural gas and RBOB gasoline futures, both traded on the New York Mercantile Exchange (NYMEX). In short:

1. **Natural gas reproduces.** 57 of its 360 pairs reject the hypothesis of no cointegration, against a pass mark of 47.
2. **RBOB gasoline does not.** 14 of its 220 pairs reject, against a pass mark of 31.
3. **The pass marks were corrected after the result was seen.** Under the ones written down first, both commodities passed. The correction moved gasoline’s verdict and not natural gas’s, and both readings are reported here.

Each commodity is judged alone. Every result here is **exploratory**. The data was spent checking a claim Chan chose, so it can say whether these spreads behaved as he said over these windows and nothing about whether trading them pays. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

[The stationary candidates post](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) covers the two other places Chan names in the same sentence, a currency rate and a pair of bonds. This post leans on it for the machinery. [Its section on how the test reads](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#how-the-test-reads) defines the Engle-Granger test and the critical values it is read against, and [How to test whether a price spread mean-reverts](https://baowebdev.substack.com/p/how-to-test-whether-a-price-spread) builds the test step by step.

## The claim and the files

Seven facts set up everything that follows.

1. **A calendar spread.** A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date, and each delivery month trades as its own contract. The spread here is one month’s contract against the next month’s, the June natural gas contract against the July one, for example.
2. **The files.** EIA publishes daily settlement prices for the nearest four contracts only, numbered by how soon each stops trading. Natural gas is `eia_rngc1` to `eia_rngc4`, and RBOB gasoline is `eia_eer-epmrr-pe1-y35ny-dpg` to `pe4`. All eight were downloaded on 2 October 2026.
3. **The pairs.** The run reads every pair of neighbouring months whose whole window lies inside all four of a commodity’s files. That gives 360 natural gas pairs, with near months from May 1994 to April 2024, and 220 RBOB pairs, from January 2006 to April 2024.
4. **The days.** A pair sits inside the nearest four for about three months. Six of those days are dropped for a reason Lesson 4 gives, and so is any day either file lacks. Natural gas pairs keep 39 to 59 days, a median of 56, and RBOB pairs keep 40 to 59, a median of 57.
5. **What was left out.** EIA also publishes New York Harbor gasoline, the contract RBOB replaced. Its four files each lack different days, so a pair of its neighbouring contracts keeps a median of 42 days, and 141 of its 150 pairs keep fewer than 50. The run left it out for that reason, measured before any statistic.
6. **The test.** Engle-Granger with an intercept, at one lag, on the settlement prices themselves rather than their logs. It regresses one price on the other, then checks whether the **residuals**, what the regression leaves over, keep returning to zero. It is the bond pair’s test in the stationary candidates post. That post explains why its currency test took a constant, a log and one lag, so each deserves a word here.
   - **The intercept** is Engle-Granger’s own, and it is why the 10% critical value, the cutoff the test statistic must fall below, is −3.04.
   - **Prices rather than logs** is this repository’s rule for every pair. A settlement is a price in dollars, so there is no quoting direction for a log to remove, which was the currency’s reason.
   - **One lag**, one earlier day’s change in the check on the residuals, was written down before any statistic, as it was for the other two candidates.
7. **The residual check at one lag.** [The stationary candidates post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-3-checking-for-leftover-autocorrelation-can-strengthen-a-finding-shrink-a-margin-or-reverse-a-verdict) teaches that leftover autocorrelation in a fit’s residuals can reverse a verdict, because the critical values no longer apply. About seven fits in ten pass that check for natural gas, 250 and 255 of 360, one count per direction of the regression. About three in four pass for RBOB, 168 and 166 of 220. The rest are read against critical values that may not apply. The simulated contracts below are tested at one lag too, so the run searched for a passing lag count on neither side.

The rules that decide each result are in [Entry 15 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-15-calendar-spreads-chans-quantitative-trading), which records each figure below beside the assertion that computes it.

## Lesson 1: a claim with no number still needs a pass mark written down first

Chan’s sentence gives nothing to match, so the run had to decide what agreeing with it would look like before computing anything. A pass mark chosen after the statistic is seen can always be placed to pass.

No single pair is tested alone. A pair keeps about 56 days, which gives one test little power to find a relationship that is there. Testing 580 pairs at 10% would also produce rejections by chance. So the statistic is a count: how many of a commodity’s pairs reject in both orientations at the 10% critical value of −3.04.

**Both orientations** means the test runs twice on each pair, once with the near month regressed on the far and once the other way round. The test is not symmetric, and Chan names no dependent leg, the one regressed on the other. Requiring both was meant to stop either orientation being chosen after its result was seen.

The count is not read against 10%. The test’s critical values assume a long series, while a pair keeps about 56 days, and pairs that share a contract are not independent. So the pass mark, called the bar from here on, comes from simulation. The simulated sets are called the **null**, because they are what the data would look like if the claim were false. A commodity reproduces when its count is strictly above the 975th of 1,000 counts from simulated contracts that do not cointegrate, read on the same days the real pairs keep, with seed 20261003. Using the 975th rather than the 950th splits a 5% chance of a false pass across the two commodities.

This answers a question the stationary candidates post raises. [Its Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-1-a-named-series-can-be-checked-while-a-class-can-only-be-sampled) says a class of instruments can only be sampled, so two Treasury funds standing in for bonds carried a finding rather than a verdict. Calendar spreads are a class too, yet each commodity here carries a verdict. A June and July natural gas pair is a calendar spread, a member of the class Chan names rather than a stand-in for one, so a batch of them failing bears on his sentence. [The replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#rows-that-are-not-replications) records that reasoning, and the criterion was written down before any statistic on the futures was computed. The verdicts still reach only two commodities out of many, so neither is a ruling on calendar spreads in general.

## Lesson 2: the simulated contracts have to move together like real ones

The pass mark written down first simulated every contract as an independent random walk, a price that takes random steps with no pull toward any level. Under it, both commodities passed. A check made after the first run found that real neighbouring contracts move together, and the simulated ones did not.

```math
\begin{array}{l|r|r}
 & \text{Natural gas} & \text{RBOB} \\ \hline
\text{Pairs rejecting in both orientations} & 57 \text{ of } 360 & 14 \text{ of } 220 \\
\text{Independent walks: median, bar} & 12, \ 19 & 7, \ 13 \\
\text{Walks correlated as the files are: median, bar} & 35, \ 47 & 21.5, \ 31 \\
\text{Verdict against independent walks} & \text{reproduced} & \text{reproduced} \\
\text{Verdict against correlated walks} & \text{reproduced} & \text{did not reproduce}
\end{array}
```

Four steps took the result from the first reading to the second.

1. **What the check found.** Two contracts a month apart move almost as one. Across a commodity’s pairs, the median correlation between the two legs’ daily price changes is 0.9942 for natural gas and 0.9951 for RBOB. Independent walks have none of that, and under them RBOB cleared its bar of 13 by one pair.
2. **Why requiring both orientations removed so little.** When two prices move almost as one, regressing either on the other gives nearly the same answer. Natural gas rejects in 62 pairs with the near month as the dependent leg and 62 the other way round, against 57 in both. RBOB rejects in 17 and 16, against 14. Requiring both cost natural gas five pairs against either orientation alone, and RBOB three against the first. With no cointegration at all, the median natural gas count rises from 12 pairs to 35 once the simulated walks correlate as the files do.
3. **The correction.** The repository’s owner ruled on 3 October 2026 to judge both commodities again, against walks whose daily changes correlate at each commodity’s own median. Each simulated contract became the square root of that correlation times one walk shared by the whole commodity, plus the square root of one minus it times a walk of its own. The correction raised both bars, so it made a pass harder rather than easier, and it is not a search toward the claim. It moved RBOB’s verdict and left natural gas’s where it was.
4. **How far each verdict sits from its bar.** None of the 1,000 correlated null sets reaches natural gas’s 57, and 973 of them reach RBOB’s 14. Natural gas clears its bar by ten pairs, and RBOB falls seventeen short. That count of null sets was added after the verdicts were seen, because a bar alone does not say how close a verdict sat to it.

![Two panels of histograms, one per commodity, counting pairs that reject in both orientations at 10% on the horizontal axis and null sets of 1,000 on the vertical. The upper panel is natural gas, 57 of 360 pairs. A grey histogram of 1,000 sets of independent walks is centred near its median of 12 pairs, with its 975th set marked as a dashed grey line at 19. A brass histogram of 1,000 sets of walks correlated as the files are is centred near its median of 35, with its dashed line at 47. A solid dark line at 57 sits past both. The lower panel is RBOB gasoline, 14 of 220 pairs. Its grey histogram is centred near its median of 7 with its bar at 13, and its brass histogram near its median of 21.5 with its bar at 31. The solid line at 14 sits just past the grey bar and well inside the brass histogram.](../docs/figures/calendar_spread_nulls.png)

*Each histogram is 1,000 sets of simulated contracts that do not cointegrate. Correlating them as the files are moves the whole histogram right. Natural gas stays past both bars, and gasoline falls inside the corrected one.*

Build the null from what the data does that the claim does not explain. When the null is corrected after the result is seen, report both verdicts.

## Lesson 3: about 56 days cannot tell slow reversion from none

A pass mark says what pairs that never revert would give. It does not say what pairs that revert slowly would give, and that is a separate simulation. The speed to use came from Chan himself: the 36-day half-life of his crude oil spread. That spread is twelve months apart and logged, while these are one month apart and in prices, so the run borrows only its speed.

The run simulated 1,000 sets in which every pair truly cointegrates, with seed 20261004. In each, the far leg is a random walk and the near leg is the far leg plus a spread that reverts with a 36-day half-life. Read on the real pairs’ days and tested the same way, the sets averaged 21.9 rejecting pairs of 360 for natural gas and 13.5 of 220 for RBOB.

The two commodities read differently against that.

1. **Natural gas’s 57 is far more than reversion that slow gives.** Whatever produces it reverts faster within these windows, or comes from something neither simulation models. The run cannot say which.
2. **RBOB’s 14 sits at what slow reversion gives**, and also inside what no reversion gives, since 973 of the 1,000 correlated null sets reach it. A window of about 56 days cannot separate the two.

So “did not reproduce” is not evidence that RBOB spreads fail to cointegrate. It says this test, on windows this short, could not show that they do.

A 36-day half-life is also slow for trading, not only for testing. [The stationary candidates post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-6-a-reversion-as-slow-as-the-rates-is-hard-to-size) works through what a half-life does to the size and the return of a trade on it, with the same 36 days as one of its two speeds.

## Lesson 4: a calendar that is one day wrong should cost nothing

EIA numbers its files by expiry, so contract 1 is whichever contract stops trading next. Reading a named month, such as June, means knowing which numbered file holds it on each day, and that takes an expiry rule. [The commodity seasonals post’s Lesson 4](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md#lesson-4-reading-one-named-contract-from-files-numbered-by-expiry-needs-a-calendar-checked-outside-the-files) teaches that numbering and checks the rule against the exchange’s own dates for 16 contracts. What is new here is a design that survives a rule one day off, and a check of the rule over every expiry the pairs read.

1. **Each pair rests on four expiries.** A pair reads its two contracts through the numbered files for about three months. Its window opens the day after the expiry of the contract three months ahead of the near one, crosses two more expiries, and closes on the near contract’s own last day.
2. **The check against the files.** On the day after an expiry, each numbered file should take over the prices the next file held the day before, a **handover**. Over the contracts delivered from February 1994 to April 2024, the handover falls on the rule’s expiry date for 298 of the 316 natural gas expiries the files can read. Over January 2006 to April 2024 it does for 202 of 213 RBOB expiries. With the rule moved a day earlier it fits 38 of 324 and 15 of 210, and a day later 16 of 324 and 9 of 213. How many expiries the files can read changes with the day tested, because a file can lack a row on one day and hold one on the next.
3. **The days dropped.** Each window drops its first and last days, and each expiry inside it together with the day after. Those six are the only days a rule one day wrong could misread. On every day a pair keeps, a rule moved a day either way reads the same two prices.
4. **What that does not cover.** The run cannot say whether each of the 18 natural gas and 11 RBOB handovers that do not fit is noise in the files or a rule one day off, and one day is all the dropped days absorb. A rule two days off would put a neighbouring contract into a day or two of four pairs, and these counts do not rule that out.
5. **The correction the check forced.** The calendar had counted three days as closed: 29 and 30 October 2012, during Hurricane Sandy, and 5 December 2018. Every natural gas and RBOB file settled on all three. Counting them closed put the November 2012 natural gas expiry on 25 October, two trading days before 29 October, where the files actually hand over. That is beyond what the dropped days absorb, so the calendar now counts all three as open.

## What this replication cannot say

Four questions are beyond it.

1. **Whether a pair cointegrates over its whole life.** The nearest four hold a pair for about three months. A contract’s full history, and pairs more than a month apart, need contract-level data EIA does not publish. A request to the Massive futures data service on 3 October 2026 returned no prices for the three natural gas contracts it asked for, and no other source for that data is known here.
2. **How much the corrected null leaves out.** It gives every pair in a commodity the same correlation, the median, and gives both legs the same volatility. Real correlations and volatilities vary from pair to pair and over time. Natural gas clears its bar by ten pairs and RBOB misses by seventeen, and how far a richer null could move either bar has not been measured.
3. **Which pairs cointegrate.** No pair is a finding, for the two reasons Lesson 1 gives for testing none alone.
4. **Whether trading a calendar spread pays.** Cointegration is a statement about two price series. A trade adds costs, the timing of each roll to the next pair, and margin, and none of those is modelled here.

## What this means for a trader

On these windows, natural gas’s neighbouring contracts behaved as Chan said, and RBOB’s could not be shown to. That is a reason to look more closely at natural gas, with longer windows and costs included. It is not a strategy, and nothing here prices a roll, a commission or the margin a spread ties up.

Two habits carry over to any claim that prints no number.

1. **Write the pass mark down first.** The count, the 975th set as the bar and the split across two commodities were fixed before any statistic was computed, which is what lets the natural gas verdict mean something.
2. **Ask what the simulation leaves out.** Against independent walks, both commodities passed. Against walks that move together as real contracts do, only natural gas did. The second simulation is closer to the data, and it is the harder one to pass.

Chan’s later book said calendar spreads do not generally mean-revert, then found one that does. On EIA’s free settlements, natural gas reproduces his earlier claim and RBOB gasoline does not, and both results are exploratory.

## References

- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 2321, 2461 and 2471.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Kindle location 3951.
- Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. *Econometrica*, 55(2), 251–276.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for Henry Hub natural gas and RBOB gasoline, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the test and both nulls](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_figures.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_figures.py), and [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-15-calendar-spreads-chans-quantitative-trading) that records each verdict.*
