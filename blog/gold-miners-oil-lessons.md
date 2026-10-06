# Gold, the gold miners and oil: testing why a pair trade stopped working

*Chan says gold and the gold miners stopped moving together on the day oil peaked, and that adding an oil fund brings the link back. On his own file every claim holds. Two controls the book leaves out pull apart: gold and the miners alone cannot explain the oil fund’s link, but the miners and oil alone could.*

## Why test the reason a strategy failed

A pair trade works only while its two prices keep a stable relationship, and that relationship can end without warning. [The post on testing GLD against GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md) found the link between the gold fund and the gold miners’ fund holding on Ernest Chan’s own windows, at the one lag he used, and failing over the years since. A trader who sees a pair fail has two choices: drop it, or ask why it failed and test the answer.

Chan’s second book, *Algorithmic Trading*, takes the second road with the same pair. The reasoning for the pair is that a gold miner’s main asset is gold, so its shares should track the metal. Chan says they did, “until July 14, 2008, or thereabout” (Chan, 2013, location 1922). That was the day, he writes, that West Texas crude peaked at around $145 a barrel. His explanation is that dear oil makes gold dearer to mine, which cuts the miners’ profits, so their shares lag the metal. To test it, he adds the oil fund USO and asks whether the three funds move together over the whole span.

He makes three claims, each from a Johansen test, and prints no statistic for any of them.

1. **Before.** GLD and GDX from 2006-05-23 to 2008-07-14 “cointegrate with 99 percent probability”.
2. **After.** From 2008-07-15 to 2012-04-09 they “have lost the cointegration”.
3. **With oil.** GLD, GDX and USO over the whole span show “a 99 percent probability that there exists one cointegrating relationship”.

Chan offers this as a model of how to treat a failing strategy: form a hypothesis about the cause, then test whether the data support it. No script ships for the example. So this repository wrote down how it would test each claim before computing any statistic, then ran the tests on Chan’s own data file.

All three claims hold, with room, on both of the Johansen test’s statistics. The control that would rule out the obvious alternative holds too. A second control, added after the first run, does not support the oil story. It finds that the miners and oil alone share a link, which is enough to produce the triplet’s result with no help from gold.

**Every result here is exploratory.** Chan chose the split date and the third fund after seeing the pair break, and the reproduction tests them on the same days. It can say whether his claims follow from his file and nothing about whether the oil explanation is right.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The test and the file

Two prices are cointegrated when some fixed mix of them is stationary, meaning it keeps returning to a stable average rather than wandering off. The earlier post tested that with the Engle-Granger method, which fits a hedge ratio by regression and then tests what the regression leaves over. It handles two series at a time.

The **Johansen test** handles any number of series at once. It asks how many independent stationary mixes the set holds, a count called the rank. Two series hold 0, 1 or 2, and three hold 0 to 3. The test reaches its count in steps. It first tests the hypothesis that the rank is 0. If that is rejected, it tests a rank of at most 1, and so on, and it stops at the first hypothesis it cannot reject. The test also reports, for each mix it finds, the weights that make it, as one column of numbers per mix called an eigenvector.

The test comes with two statistics for each step, the trace statistic and the eigen statistic. Each is a different way of asking whether the next relation is real, and they can disagree. The book does not say which one Chan read. So each claim was judged on both, separately, at the 99 percent level all three claims name.

The specification, written down before any number was seen, has four parts.

1. **The test.** The Johansen test with a constant and one lagged difference, the setting every Johansen call in Chan’s scripts for the book passes. Its critical values are the tables this repository has already checked against one of Chan’s own printouts.
2. **The columns.** GLD, GDX and then USO, the book’s order.
3. **The windows.** 2006-05-23 to 2008-07-14 and 2008-07-15 to 2012-04-09 for the pair, the dates the book names, and the whole span for the three funds.
4. **The criteria.** The first claim holds on one relation or two, the second on none, and the third on exactly one.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and converted here to one file per ETF. The file folds dividends in by subtracting them in dollars. It holds GLD and USO from 2006-04-26 and GDX from 2006-05-23, so the run starts on GDX’s first price, which is where Chan’s first window starts too. That leaves 1,481 trading days to 2012-04-09, split 539 before the break and 942 after it.

## Lesson 1: every claim holds, with room to spare

Here is each test, its statistic for the first hypothesis, and that statistic’s 99 percent bar. A statistic above its bar rejects the hypothesis of no relation.

```math
\begin{array}{l|r|r|r|r|c}
\text{Test} & \text{Trace} & \text{99\% bar} & \text{Eigen} & \text{99\% bar} & \text{Relations at 99\%} \\ \hline
\text{GLD, GDX, before} & 22.571 & 19.935 & 22.424 & 18.520 & 1 \\
\text{GLD, GDX, after} & 6.133 & 19.935 & 6.059 & 18.520 & 0 \\
\text{GLD, GDX, USO, whole span} & 44.838 & 35.463 & 37.833 & 25.865 & 1
\end{array}
```

All three claims hold on both statistics.

1. **Before the break, one relation.** Both statistics clear their bars, and the test stops at one relation rather than two.
2. **After the break, none.** Both statistics fall short even of the 90 percent bars, 13.429 for the trace and 12.297 for the eigen statistic. So the pair has not merely weakened. The test finds nothing at any level it reports.
3. **The three funds, exactly one.** The first hypothesis is rejected easily, and the second stands at every level. Its trace statistic is 7.005 against a 90 percent bar of 13.429.

The nearest call of all is the first, where the trace statistic clears its bar by 2.636. Every other claim clears or misses its bar by more, and the counts at 90 and 95 percent agree with the count at 99 on every claim. So the two choices the book left open, which statistic and which level, change nothing here. That is not always so. On another of Chan’s examples in the same book, the two statistics disagree on his own file.

The figure shows the break in two ways. The top panel holds the three closes. On Chan’s file, USO’s highest close, 117.48, falls on 2008-07-14 itself, the last day of his first window. The bottom panel holds GLD and GDX in the weights the first window’s Johansen test finds, 0.191 shares of GLD against −0.514 of GDX, measured in standard deviations from that portfolio’s first-window average. Before the break it stays between −3.24 and 2.56 and keeps crossing its average. After the break it runs from 0.47 to 13.52 and never comes back.

![Two line charts stacked on one shared date axis from May 2006 to April 2012, with a dashed vertical line on July 14, 2008 in both. The top chart plots the closes of GLD, GDX and USO in dollars. USO climbs to its highest close of 117.48 on the dashed line, marked with a dot, then collapses to about 25 by early 2009. GLD dips in late 2008 and then climbs to about 185 in 2011. GDX falls with USO in late 2008, recovers to between about 45 and 65, and ends near 47. The bottom chart plots GLD and GDX held in the first window’s Johansen weights, 0.191 and −0.514 shares, in standard deviations from that portfolio’s mean over the first window. Left of the dashed line it moves between −3.24 and 2.56 and crosses zero again and again. Right of the line it jumps above 12 in late 2008, sags to between about 1.5 and 7 through 2009 and 2010, and climbs to 13.52 by April 2012, staying above zero throughout at a lowest value of 0.47. The title calls the figure exploratory, and the note names Chan’s file and says the split date was chosen after the break was seen.](../docs/figures/gold_miners_oil_break.png)

*The three closes, and the first window’s GLD and GDX portfolio carried across the break, on Chan’s file over the 1,481 days GDX is priced.*

The bottom panel holds the first window’s weights fixed, so everything right of the line shows those weights on days they never saw. The second window’s own Johansen test is a stronger statement. It fits fresh weights to the 942 days after the break and still finds no stationary mix.

One word in the book needs care. “99 percent probability” reads as a 99 percent chance that the pair cointegrates, and the test cannot say that. It says that if the pair did not cointegrate, a statistic this large would turn up less than 1 percent of the time. That is a level the test was run at, not a probability that the claim is true.

## Lesson 2: the control the book leaves out holds

A result with three funds over the whole span means something only if the pair alone fails over the same days. If GLD and GDX already cointegrated from 2006 to 2012 by themselves, adding USO would find their relation again and say nothing about oil. The book does not run that check.

Run here, the pair alone over the triplet’s 1,481 days gives a trace statistic of 10.447, short of even the 90 percent bar of 13.429. Adding USO raises the first trace statistic to 44.838. So the triplet’s relation is not one the pair already held, and USO is doing work in it.

The Engle-Granger test from the earlier post agrees about the break. Regressing GLD on GDX, it gives −3.724 before the break, past its 95 percent bar of −3.34 and short of its 99 percent bar of −3.90. After the break it gives −1.512, nowhere near either. So it sees the same break, though only at 95 percent before it.

## Lesson 3: a second control weakens the story

The first control shows that USO matters to the triplet. It does not show how. Chan’s story says oil restores the link between gold and the miners. But a triplet with one relation is also what a link between any two of the three would produce, with the third fund along for the ride.

So this repository added two more tests after the first run, over the same 1,481 days, each pairing one gold fund with USO alone.

```math
\begin{array}{l|r|r|r|c}
\text{Pair} & \text{Trace} & \text{90\% bar} & \text{99\% bar} & \text{Relations at 99\%} \\ \hline
\text{GLD, USO} & 4.350 & 13.429 & 19.935 & 0 \\
\text{GDX, USO} & 27.166 & 13.429 & 19.935 & 1
\end{array}
```

Gold and oil alone find nothing, even at 90 percent. The miners and oil alone find one relation at 99 percent. So the triplet’s single relation could be the link between the miners and oil by itself, with GLD along for the ride. That reading says nothing about oil restoring the link between gold and the miners. A rank of one cannot tell the two readings apart, and nothing here tries to.

Two details keep this from being a clean result in either direction.

1. **The miners and oil reach full rank at 90 percent.** At that level the test rejects both of its hypotheses, which on its face says each fund is stationary by itself. Yet a separate test on each fund alone finds neither one stationary, even at 90 percent. A Johansen count equal to the number of funds is hard to read when the funds alone do not support it. No claim here is judged at 90 percent, so this changes no verdict, but it is a reason not to lean hard on the pair.
2. **The weights do not compare across funds.** The triplet’s eigenvector is 0.033109 shares of GLD, −0.177036 of GDX and 0.002549 of USO. Those are shares, and the three funds trade at different prices, so their sizes cannot be read as how much each fund matters. Nothing here measures the weights in dollars.

## Lesson 4: a hypothesis formed on the sample cannot be confirmed by it

Chan’s example shows the right process: when a strategy stops working, form a hypothesis about why and test it. The test here cannot finish that process, for two reasons.

1. **The split date was chosen by looking.** Chan saw the pair break and then named the day. A test that splits the sample at the day the break was seen is favoured by construction, because the date was picked where the break showed.
2. **The third fund was chosen by looking too.** Oil was proposed after the break was seen, as the explanation for it. So the triplet’s result tests a hypothesis on the same data that suggested it.

So the result is exploratory however it comes out. It shows that Chan’s claims follow from his file. It cannot show that oil caused the break. A test that could would take the hypothesis as Chan stated it, write it down first, and run it on data the hypothesis was not formed on, which here means GLD, GDX and USO after April 2012.

## What this replication cannot say

Five questions are beyond it.

1. **Anything about oil itself.** USO holds front-month crude oil futures rather than oil, and a futures fund drifts away from the spot price as it rolls from one contract to the next. So the triplet’s relation is with the fund. Whether it holds with the spot price is a different test.
2. **Where inside the second window the link failed.** One test over 2008-07-15 to 2012-04-09 says the window as a whole holds no relation. It cannot date the break inside it, and it says nothing about the years after 2012. The earlier post’s rolling one-year test, on recent downloads, placed the miners’ detachment from gold somewhere in the 2010s. The two differ in file, test and window, and this run does not try to date the break.
3. **How much the tests confirm each other.** The whole span contains both of the pair’s windows, so the tests are not independent, and nothing here corrects for running several tests on one sample.
4. **Whether Chan’s trading rule works.** He suggests trading the triplet, or at least ceasing to trade GLD against GDX whenever oil exceeds a threshold. Nothing here backtests either.
5. **Whether the oil hypothesis holds.** It was formed on this sample and tested on the same one, which Lesson 4 explains.

## What this means for a trader

One habit for each lesson.

1. **Read a test level as a test level.** “99 percent” is how rarely the statistic would appear if there were no relation, not a probability that there is one.
2. **Run the control the story skips.** A third series that restores a relation means something only if the original pair fails without it over the same days.
3. **Test every pair inside a triplet.** One relation among three series can belong to any two of them, and only the pairwise tests say which.
4. **Fix the hypothesis before the data that tests it.** A split date and an explanation both chosen after seeing the break make a hypothesis to test next, not a result.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle location 1922.
2. Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551–1580.
3. Engle, R. F., and Granger, C. W. J. (1987). Co-integration and error correction: representation, estimation, and testing. *Econometrica*, 55(2), 251–276.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gold_miners_oil.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gold_miners_oil_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gold_miners_oil.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gold_miners_oil_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-29-gld-gdx-and-uso-around-july-2008-chans-algorithmic-trading) that sets each of Chan’s claims beside what was found here.*
