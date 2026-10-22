# Chan’s calendar spreads hold for natural gas, and gasoline’s pass vanishes once the simulated contracts move like real ones

*A claim with no number needs a pass mark written down before the run, and a pass mark is only as good as the simulation behind it.*

## Why test a claim that prints no number

Ernest Chan’s *Quantitative Trading* names calendar spreads as “the simplest examples of cointegrating futures pairs” (Chan, 2021, location 3951). A calendar spread is a long position in one commodity’s futures for one delivery month and a short position in the same commodity for another. Two prices **cointegrate** when some combination of them keeps returning to a fixed average, which is what a trade on the spread between them needs. Chan prints no figure for the claim and works no example.

His other book, *Algorithmic Trading*, published in 2013 between the two editions of *Quantitative Trading*, qualifies it. Calendar spreads “do not generally mean-revert”, he writes there (Chan, 2013, location 2321). A few pages on he finds one that does. The 12-month calendar spread of crude oil, taken in logs, keeps returning to its average at 99% confidence, with a **half-life** of 36 days, the time a gap from the average takes to close halfway (locations 2461 and 2471). So *Algorithmic Trading* doubts the claim in general and then finds an exception. This repository wrote that doubt down before computing any statistic, so neither verdict below can be presented afterwards as a surprise.

A sentence with no number is still a claim a reader might act on, so it is worth checking. This repository tested every pair of neighbouring contracts in the free settlement prices the US Energy Information Administration (EIA) publishes for natural gas and RBOB gasoline futures, both traded on the New York Mercantile Exchange (NYMEX). In short:

1. **Natural gas reproduces.** 57 of its 360 pairs reject the hypothesis of no cointegration, against a pass mark of 47.
2. **RBOB gasoline does not.** 14 of its 220 pairs reject, against a pass mark of 31.
3. **The pass marks were corrected after the result was seen.** Under the ones written down first, both commodities passed. The correction moved gasoline’s verdict and not natural gas’s, and both readings are reported here.

Each commodity is judged alone. Every result here is **exploratory**. The data was spent checking a claim Chan chose, so it can say whether these spreads behaved as he said over these windows and nothing about whether trading them pays. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

[The stationary candidates post](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) covers the two other places Chan names in the same passage, a currency rate and a pair of bonds. This post leans on it for the machinery. [Its section on how the test reads](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#how-the-test-reads) defines the Engle-Granger test and the critical values it is read against, and [How to test whether a price spread mean-reverts](https://baowebdev.substack.com/p/how-to-test-whether-a-price-spread) builds the test step by step.

## The claim and the files

Five facts about the contracts and the files set up the pairs the run tests.

1. **A calendar spread.** A **futures contract** is an agreement to buy a fixed amount of a commodity at a set price on a delivery date, and each delivery month trades as its own contract. The spread here is one month’s contract, the **near month**, against the next month’s, the **far month**. The June natural gas contract against the July one is an example.
2. **The files.** EIA publishes daily settlement prices for the nearest four contracts only, numbered by how soon each stops trading. Natural gas is `eia_rngc1` to `eia_rngc4`, and RBOB gasoline is `eia_eer-epmrr-pe1-y35ny-dpg` to `pe4`. All eight were downloaded on 2 October 2026.
3. **The pairs.** A pair’s **window** is the stretch of trading days when both its contracts are among the nearest four. The run reads every pair of neighbouring months whose whole window falls within the span of dates all four of a commodity’s files cover. That gives 360 natural gas pairs, with near months from May 1994 to April 2024, and 220 RBOB pairs, from January 2006 to April 2024.
4. **The days.** A window lasts about three months. Six of its trading days are dropped for a reason Lesson 4 gives, and so is any day on which the file holding either contract has no price. Natural gas pairs keep 39 to 59 days, a median of 56, and RBOB pairs keep 40 to 59, a median of 57.
5. **What was left out.** EIA also publishes New York Harbor gasoline, the contract RBOB replaced. Its four files each lack different days, so a pair of its neighbouring contracts keeps a median of 42 days, and 141 of its 150 pairs keep fewer than 50. The run left it out for that reason, and the day counts behind it were measured before any statistic was computed.

### The test each pair is put through

Two facts settle what the run computes on each pair.

1. **The test.** Engle-Granger with an intercept, at one lag, on the settlement prices themselves rather than their logs. It regresses one price on the other, then checks whether the **residuals**, what the regression leaves over, keep returning to zero. It is the bond pair’s test in the stationary candidates post. That post explains why its currency test took a constant, a log and one lag, so each choice gets a word here.
   - **The intercept** takes the place of the currency test’s constant. It is part of Engle and Granger’s test rather than a choice made here, and with it the 10% critical value, the cutoff the test statistic must fall below, is −3.04.
   - **Prices rather than logs** is this repository’s rule for every pair. The currency test took logs because an exchange rate can be quoted either way round, and once it is in logs, flipping the quote only flips the sign. A settlement is a price in dollars with one way to quote it, so that reason does not apply.
   - **One lag** means the test’s regression on the residuals includes one earlier day’s change. It was written down before any statistic, as it was for the currency rate and the bond pair.
2. **The residual check at one lag.** [The stationary candidates post’s Lesson 3](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-3-checking-for-leftover-autocorrelation-can-strengthen-a-finding-shrink-a-margin-or-reverse-a-verdict) teaches that leftover autocorrelation in a fit’s residuals can reverse a verdict, because the critical values no longer apply. Its check reads what the test’s regression on the residuals leaves over, and passes a fit when a Breusch-Godfrey test for autocorrelation gives a p-value above 0.10 and none of the first ten autocorrelations falls outside a band of ±1.96/√n, where n is the number of days that regression fits. About seven fits in ten pass for natural gas: 250 of 360 with the near month regressed on the far, and 255 the other way round. About three in four pass for RBOB, 168 and 166 of 220 in the same order. The rest are read against critical values that may not apply. Every simulated set in the lessons below is tested at one lag too, so neither the real pairs nor the simulated ones had their lag count searched for until the check passed.

The rules behind every result are in [Entry 15 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-15-calendar-spreads-chans-quantitative-trading), the repository’s record of each run and its verdict. The entry also names the automated check in the code that confirms each result.

## Lesson 1: a claim with no number still needs a pass mark written down first

Chan’s sentence gives nothing to match, so the run had to decide what agreeing with it would look like before computing anything. A pass mark chosen after the statistic is seen can always be placed to pass.

No single pair’s result counts as a verdict. A pair keeps about 56 days, which gives one test little power to find a relationship that is there. Testing 580 pairs at 10% would also produce rejections by chance. So the statistic is a count: how many of a commodity’s pairs reject in both orientations at the 10% critical value of −3.04.

**Both orientations** means the test runs twice on each pair, once with the near month regressed on the far and once the other way round. The test is not symmetric, and Chan names no dependent leg, the one regressed on the other. Requiring both was meant to stop either orientation being chosen after its result was seen.

The count is not compared with 10% of the pairs. The test’s critical values assume a long series, while a pair keeps about 56 days, and pairs that share a contract are not independent. So the pass mark comes from simulation instead.

The run simulated 1,000 sets of contracts that do not cointegrate, with seed 20261003, read each set on the same days the real pairs keep, and counted its rejecting pairs. The simulated sets are called the **null**, because they are what the data would look like if the claim were false. The pass mark, called the **bar** from here on, is the 975th smallest of those 1,000 counts, and a commodity reproduces when its count is strictly above it. Using the 975th rather than the 950th splits a 5% chance of a false pass across the two commodities.

This post answers a question the stationary candidates post raises: whether a claim about a class of instruments can carry a verdict. [That post’s Lesson 1](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-1-a-named-series-can-be-checked-while-a-class-can-only-be-sampled) says a class can only be sampled, so two Treasury funds standing in for bonds gave a result about those two funds, a finding, rather than a verdict on the claim. Calendar spreads are a class too, yet each commodity here carries a verdict. A June and July natural gas pair is a calendar spread, a member of the class Chan names rather than a stand-in for one, so a batch of them failing bears on his sentence.

[The replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#rows-that-are-not-replications) records that reasoning, and the criterion was written down before any statistic on the futures was computed. The verdicts still reach only two commodities out of many, so neither is a ruling on calendar spreads in general.

## Lesson 2: the simulated contracts have to move together like real ones

The bar written down first came from simulating every contract as an independent random walk, a price that takes random steps with no pull toward any level. Against that bar, both commodities passed. The plan written down with it already said that real contracts of one commodity move together, and expected that to matter only between pairs that share a contract. A check made after the first run found that moving together matters inside each pair, because it changes how often a pair rejects in both orientations.

```math
\small\begin{array}{l|r|r}
 & \text{Natural gas} & \text{RBOB} \\ \hline
\begin{array}{@{}l@{}}\text{Pairs rejecting in} \\ \text{both orientations}\end{array} & 57 \text{ of } 360 & 14 \text{ of } 220 \\ \hline
\text{Independent walks} & & \\
\quad\text{median, bar} & 12, \ 19 & 7, \ 13 \\
\quad\text{verdict} & \text{reproduced} & \text{reproduced} \\ \hline
\begin{array}{@{}l@{}}\text{Walks correlated} \\ \text{as the files are}\end{array} & & \\
\quad\text{median, bar} & 35, \ 47 & 21.5, \ 31 \\
\quad\text{verdict} & \text{reproduced} & \begin{array}{@{}r@{}}\text{did not} \\ \text{reproduce}\end{array}
\end{array}
```

Four points explain how the result moved from the first reading to the second.

1. **What the check found.** Two contracts a month apart move almost as one. Across a commodity’s pairs, the median correlation between the two legs’ daily price changes is 0.9942 for natural gas and 0.9951 for RBOB. Independent walks have none of that, and under them RBOB cleared its bar of 13 by one pair.
2. **Why requiring both orientations removed so little.** When two prices move almost as one, regressing either on the other gives nearly the same answer. Natural gas rejects in 62 pairs with the near month as the dependent leg and 62 the other way round, against 57 in both. RBOB rejects in 17 and 16, against 14. Requiring both cost natural gas five pairs against either orientation alone, and RBOB three against the near-on-far count. In the null sets, each orientation alone rejects in a median of 38 of natural gas’s 360 pairs, whether the simulated walks are independent or correlate as the files do. Correlating the walks moves only the count rejecting in both orientations, whose median rises from 12 pairs to 35. So independent walks missed how often correlated contracts reject in both orientations with no cointegration at all.
3. **The correction.** The repository’s owner ruled on 3 October 2026 to judge both commodities again, against walks whose daily changes correlate at each commodity’s own median. Each simulated contract became the square root of that correlation times one walk shared by the whole commodity, plus the square root of one minus it times a walk of its own. In symbols, contract i is Xᵢ = √ρ · W + √(1 − ρ) · Zᵢ, where ρ is the commodity’s median correlation, W is the shared walk and Zᵢ is contract i’s own. The correction raised both bars, so it made a pass harder rather than easier, and it was not chosen to make the claim pass. It moved RBOB’s verdict and left natural gas’s where it was.
4. **How far each verdict sits from its bar.** None of the 1,000 correlated null sets reaches natural gas’s 57, and 973 of them reach RBOB’s 14. Natural gas clears its bar by ten pairs, and RBOB falls seventeen short. That count of null sets was added after the verdicts were seen, because a bar alone does not say how close a verdict sat to it.

![Two panels of histograms, one per commodity, counting pairs that reject in both orientations at 10% on the horizontal axis, and on the vertical the number of null sets, out of 1,000, giving each count. The upper panel is natural gas, 57 of 360 pairs. A grey histogram of 1,000 sets of independent walks is centred near its median of 12 pairs, with the 975th smallest of its 1,000 counts marked as a dashed grey line at 19. A brass histogram of 1,000 sets of walks correlated as the files are is centred near its median of 35, with its dashed line at 47. A solid dark line at 57 sits past both. The lower panel is RBOB gasoline, 14 of 220 pairs. Its grey histogram is centred near its median of 7 with its bar at 13, and its brass histogram near its median of 21.5 with its bar at 31. The solid line at 14 sits just past the grey bar and at the low end of the brass histogram, with 973 of the 1,000 brass sets at or above it.](../docs/figures/calendar_spread_nulls.png)

*Each histogram is 1,000 sets of simulated contracts that do not cointegrate. Correlating them as the files are moves the whole histogram right. Natural gas stays past both bars, and gasoline falls short of the corrected bar, at the low end of its histogram.*

![An animated whiteboard sketch titled “What requiring both orientations removes”, drawn slowly stroke by stroke in two panels, with each circle’s area to scale with a count of natural gas pairs. The left panel, “independent walks”, draws a black circle labelled “near on far: 38” above a black circle labelled “far on near: 38”. They overlap in a brown lens labelled “both: 12”, about a third of each circle. The right panel, “walks correlated as the files are”, draws the same two circles, “near on far: 38” and “far on near: 38”, almost on top of each other, so their brown lens, labelled “both: 35”, fills nearly all of each. A grey note reads “medians of 1,000 null sets of 360 natural gas pairs”, and the brown words “the files: 62 and 62 alone, 57 both” close the sketch. The finished drawing holds for twelve seconds.](../docs/figures/calendar_spreads_both_orientations.gif)

Give the null every feature the data has whether or not the claim is true, such as how closely neighbouring contracts move. When the null is corrected after the result is seen, report both verdicts.

## Lesson 3: about 56 days cannot tell slow reversion from none

A bar says what pairs that never revert would give. It does not say what pairs that revert slowly would give, and that is a separate simulation. The speed to use came from Chan himself: the 36-day half-life of his crude oil spread. That spread is twelve months apart and in logs, while these are one month apart and in prices, so the run borrows only its speed.

The run simulated 1,000 sets in which every pair truly cointegrates, with seed 20261004. In each, the far leg is a random walk and the near leg is the far leg plus a spread that reverts with a 36-day half-life. Read on the real pairs’ days and tested the same way, the sets averaged 21.9 rejecting pairs of 360 for natural gas and 13.5 of 220 for RBOB.

The two commodities read differently against that.

1. **Natural gas’s 57 is far more than these slow-reversion sets give.** Either these spreads revert faster than that within these windows, or the count comes from something that neither the correlated null nor the slow-reversion simulation models. The run cannot say which.
2. **RBOB’s 14 sits at what these slow-reversion sets give**, and also inside what no reversion gives, since 973 of the 1,000 correlated null sets reach it. A window of about 56 days cannot separate the two.

So “did not reproduce” is not evidence that RBOB spreads fail to cointegrate. It says this test, on windows this short, could not show that they do.

These slow-reversion sets were not corrected the way the null was. In them, each simulated pair’s two legs move together far less closely than the files’ contracts do. Lesson 2 showed, for walks that do not cointegrate, that legs moving closely together reject in both orientations more often. So on contracts like the files’, reversion this slow would likely give more rejections than these sets do. Natural gas’s 57 would then sit closer to that higher count, and RBOB’s 14 may sit below it rather than at it. No run has repeated the slow-reversion simulation with legs correlated as the files are.

A 36-day half-life is also slow for trading, not only for testing. [The stationary candidates post’s Lesson 6](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md#lesson-6-a-reversion-as-slow-as-the-rates-is-hard-to-size) works through what a half-life does to the size and the return of a trade on it, with the same 36 days as one of its two speeds.

## Lesson 4: a calendar that is one day wrong should cost nothing

EIA numbers its files by expiry, so contract 1 is whichever contract stops trading next. Reading a named month, such as June, means knowing which numbered file holds it on each day, and that takes an expiry rule, which gives each contract’s last trading day. The rule counts in trading days, so it rests on a calendar of the days the exchange is open. [The commodity seasonals post’s Lesson 4](https://github.com/l3a0/quantitative-trading/blob/main/blog/commodity-seasonals-lessons.md#lesson-4-reading-one-named-contract-from-files-numbered-by-expiry-needs-a-calendar-checked-outside-the-files) teaches that numbering and checks the rule against the exchange’s own dates for 16 contracts. What is new here is a design that survives a rule one day off, and a check of the rule against the files themselves.

### The six days each window drops

1. **Each pair rests on four expiries.** A pair reads its two contracts through the numbered files for about three months. Its window opens the day after the expiry of the contract delivered three months before the near one, which for a June pair is the March contract. It crosses two more expiries and closes on the near contract’s own last day.
2. **Where a one-day error lands.** Each window drops its first and last days, and each expiry inside it together with the day after. Those six are the only days a rule one day wrong could misread. On every day a pair keeps, a rule moved a day either way reads the same two prices.

![An animated whiteboard sketch titled “One window, four expiries”, drawn slowly stroke by stroke on a grey axis of trading days from late February to late May 2018. Four grey ticks with dashed guides mark the expiries the June pair rests on, labelled “Mar expires 26 Feb”, “Apr expires 27 Mar”, “May expires 26 Apr” and “Jun expires 29 May”. A black bracket from the day after the first expiry to the last is labelled “the window: 64 trading days”. A thick black lane labelled “June, near” breaks into three stretches, “file 3”, “file 2” and “file 1”, a new one starting the day after each expiry inside the window. Beneath it a lane labelled “July, far” breaks on the same days into “file 4”, “file 3” and “file 2”. A row of grey dots under both lanes is labelled “58 kept”, and six red crosses sit on the window’s first day, on each expiry inside it and the day after, and on its last day. The brown words “a rule a day off misreads only the crossed days” close the sketch. The finished drawing holds for twelve seconds.](../docs/figures/calendar_spreads_one_window.gif)

### The rule checked against the files

1. **How often the rule fits.** On the day after an expiry, each numbered file should take over the contract that the file numbered one higher held the day before, so file 1 takes over file 2’s contract. That move is a **handover**. It shows in the price gaps between neighbouring files. The gap between files 1 and 2 on the day after lines up with the gap between files 2 and 3 on the expiry day, because both are the gap between the same two contracts. The gap between files 2 and 3 lines up the same way with the one between files 3 and 4. Over the contracts delivered from February 1994 to April 2024, the handover falls on the rule’s expiry date for 298 of the 316 natural gas expiries the files have rows to check. Over January 2006 to April 2024 it does for 202 of 213 RBOB expiries. With the rule moved a day earlier it fits 38 of 324 and 15 of 210, and a day later 16 of 324 and 9 of 213. How many expiries the files have rows to check changes with the day tested, because a file can lack a row on one day and hold one on the next.
2. **What that does not cover.** The run cannot say whether each of the 18 natural gas and 11 RBOB handovers that do not fit is noise in the files or a rule one day off. The dropped days absorb an error of one day and no more. A rule two days off would read a neighbouring contract’s price on one kept day in each of up to three pairs around an expiry, and these counts do not exclude that.
3. **A known gap in the first two RBOB pairs.** The RBOB files start on 3 October 2005 and hold the January 2006 contract in file 1 until 30 December. So they never hand over on the rule’s dates for the November and December 2005 contracts, two expiries this check does not read. The two pairs, with near months January and February 2006, therefore read the wrong contracts on every day they keep before December 2005. As the run reads them, neither rejects. Read as the files hold them, the February pair rejects in both orientations, which would raise RBOB’s 14 to 15, still far under its bar of 31.
4. **The correction the check forced.** The trading calendar had counted three days as closed: 29 and 30 October 2012, during Hurricane Sandy, and 5 December 2018. Every natural gas and RBOB file settled on all three. Counting them closed put the November 2012 natural gas expiry on 25 October, two trading days before the 29 October expiry the files’ handover shows. That is beyond what the dropped days absorb, so the trading calendar now counts all three as open.

## What this replication cannot say

Four questions are beyond it.

1. **Whether a pair cointegrates over its whole life.** The nearest four hold a pair for about three months. A contract’s full history, and pairs more than a month apart, need contract-level data EIA does not publish. A request to the Massive futures data service on 3 October 2026 returned no prices for the three natural gas contracts it asked for, and no free source for that data is known here.
2. **How much the corrected null leaves out.** It gives every pair in a commodity the same correlation, the median, and gives both legs the same volatility. Real correlations and volatilities vary from pair to pair and over time. Natural gas clears its bar by ten pairs and RBOB misses by seventeen, and how far a richer null could move either bar has not been measured.
3. **Which pairs cointegrate.** No pair is singled out as cointegrating, for the two reasons Lesson 1 gives for judging none alone.
4. **Whether trading a calendar spread pays.** Cointegration is a statement about two price series. A trade adds costs, the timing of each roll to the next pair, and margin, and none of those is modelled here.

## What this means for a trader

On these windows, natural gas’s neighbouring contracts behaved as Chan said, and RBOB’s could not be shown to. That is a reason to look more closely at natural gas, with longer windows and costs included. It is not a strategy.

Two habits carry over to any claim that prints no number.

1. **Write the pass mark down first.** The count, the bar at the 975th of 1,000 simulated counts, and the split across two commodities were all fixed before any statistic was computed. Only the simulation behind the bar changed afterwards, and natural gas passes under both, which is what lets its verdict mean something.
2. **Ask what the simulation leaves out.** Against independent walks, both commodities passed. Against walks that move together as real contracts do, only natural gas did. The second simulation is closer to the data, and it is the harder one to pass.

In *Algorithmic Trading* Chan said calendar spreads do not generally mean-revert, then found one that does. On EIA’s free settlements, natural gas reproduces his claim in *Quantitative Trading*, and RBOB gasoline does not reproduce it on windows this short, which leaves open whether its spreads cointegrate. Both results are exploratory.

## References

- Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle locations 2321, 2461 and 2471.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley. Kindle location 3951.
- Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. *Econometrica*, 55(2), 251–276.
- US Energy Information Administration. NYMEX futures settlement prices, daily, for Henry Hub natural gas and RBOB gasoline, contracts 1 to 4. Downloaded 2 October 2026.

*Not investment advice. Code: [the test and both nulls](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates.py), [the calendar and expiry rules](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/futures.py), [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spread_figures.py) and [the whiteboard sketches](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/calendar_spreads_whiteboard.py), with the checks behind [the numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates.py), [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spread_figures.py) and [what the sketches draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_calendar_spreads_whiteboard.py), and [the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-15-calendar-spreads-chans-quantitative-trading) that records each verdict.*
