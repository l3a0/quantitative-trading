# Gold, the gold miners and oil: testing why a pair trade stopped working

*Chan says gold and the gold miners stopped moving together on the day oil peaked, and that adding an oil fund brings the link back. Every claim holds on his file, but the link the three funds share joins gold and the miners and carries almost no oil.*

## Why test the reason a strategy failed

A pair trade works only while its two prices keep a stable relationship, and that relationship can end without warning. [The post on testing GLD against GDX](https://github.com/l3a0/quantitative-trading/blob/main/blog/gld-gdx-cointegration-lessons.md) found the link between GLD, the gold fund, and GDX, the gold miners’ fund, holding over the date ranges Ernest Chan tested, at the one lag he used, meaning the test allowed for one day of past price changes, and failing over the years since. A trader who sees a pair fail has two choices: drop it, or ask why it failed and test the answer.

Chan’s second book, *Algorithmic Trading*, takes the second road with the same pair. The reasoning for the pair is that a gold miner’s main asset is gold, so its shares should track the metal. Chan says they did, “until July 14, 2008, or thereabout” (Chan, 2013, location 1922). That was the day, he writes, that West Texas crude peaked at around $145 a barrel. His explanation is that dear oil makes gold dearer to mine, which cuts the miners’ profits, so their shares lag the metal. To test it, he adds the oil fund USO and asks whether the three funds move together over the whole span.

He makes three claims and prints no statistic for any of them. Each comes from a Johansen test, which counts the stable relationships among a set of prices. Chan calls prices that hold such a relationship cointegrated, and the next section explains the word and the test.

1. **Before.** GLD and GDX from 2006-05-23 to 2008-07-14 “cointegrate with 99 percent probability”.
2. **After.** From 2008-07-15 to 2012-04-09 they “have lost the cointegration”.
3. **With oil.** GLD, GDX and USO over the whole span, 2006-05-23 to 2012-04-09, show “a 99 percent probability that there exists one cointegrating relationship”.

Chan offers this as a model of how to treat a failing strategy: form a hypothesis about the cause, then test whether the data support it. The scripts Chan publishes with the book include none for this example. So this repository wrote down how it would test each claim before computing any statistic, then ran the tests on Chan’s own data file.

### What the reproduction found

All three claims hold, with room, on both statistics the Johansen test reports. The control the book leaves out, GLD and GDX alone over the whole span, finds nothing, so the oil fund does add something. Two checks added after the first run complicate the story. The miners and oil alone share a relation, but a test on the three funds’ weights rejects the idea that the triplet’s relation is that one. The triplet’s relation joins gold and the miners, with a weight on oil the test cannot tell from zero.

**Every result here is exploratory.** Chan chose the split date and the third fund after seeing the pair break, and the reproduction tests them on the same days. It can say whether his claims follow from his file and nothing about whether the oil explanation is right.

The four lessons below say what the reproduction does teach. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The test and the file

Two prices are cointegrated when some fixed mix of them is stationary, meaning it keeps returning to a stable average rather than wandering off. [The post on the Johansen test](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md#how-the-johansen-test-counts-relations) builds the test up from the Engle-Granger test, the two-price test the earlier post used, and this post leans on it.

In short, the Johansen test counts how many independent stationary mixes a set of prices holds. Each mix is one **relation**, and the count is called the rank. Two series hold 0, 1 or 2 relations, and three hold 0 to 3. The test reaches its count in steps. It first asks whether there are no relations at all. If the data rule that out, it asks whether there is at most one, and so on. The count it reports is the first one the data cannot rule out. For each relation it also reports the weights that make the mix, a column of numbers called an eigenvector.

Each step has two statistics. The trace statistic and the eigen statistic are two ways of asking whether one more relation is real, and they can disagree. Each is compared with a critical value, a bar it must clear for the test to reject that step’s hypothesis at a given level. The test reports a bar at three levels, 90, 95 and 99 percent. At the 99 percent level the bar sits where a statistic that large would turn up less than 1 percent of the time if the hypothesis were true. The book does not say which statistic Chan read, so the reproduction judged each claim on both, separately, at the 99 percent level all three claims name.

The specification, written down before the run computed any statistic, has four parts.

1. **The test.** The Johansen test with a constant and one lagged difference, which means its model of each day’s price changes also uses the previous day’s changes. That is the setting every Johansen call in Chan’s scripts for the book passes. Its critical values are the tables this repository has already checked against one of Chan’s own printouts.
2. **The columns.** GLD, GDX and then USO, the book’s order.
3. **The windows.** 2006-05-23 to 2008-07-14 and 2008-07-15 to 2012-04-09 for the pair, the dates the book names, and the whole span for the three funds.
4. **The criteria.** The first claim holds if the test finds one or two relations, the second if it finds none, and the third if it finds exactly one.

The data is [one file](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md), Chan’s own MATLAB file `inputData_ETF.mat`, saved on 2012-04-10 and converted here to one file per ETF. The file adjusts its earlier prices for dividends by subtracting each dividend’s dollar amount. It holds GLD and USO from 2006-04-26 and GDX from 2006-05-23, so the run starts on GDX’s first price, which is where Chan’s first window starts too. That leaves 1,481 trading days to 2012-04-09, split 539 before the break and 942 after it.

## Lesson 1: every claim holds, with room to spare

Each column below is one test: GLD and GDX before the break, the same pair after it, and the three funds over the whole span. Its first four rows give the trace statistic and its 99 percent bar, then the eigen statistic and its 99 percent bar, all for the test’s first step, which asks whether there are no relations at all. A statistic above its bar rules that out. The last row is the number of relations the test counts at 99 percent.

```math
\small\begin{array}{l|r|r|r}
 & \text{Before} & \text{After} & \text{Three funds} \\ \hline
\text{Trace} & 22.571 & 6.133 & 44.838 \\
\text{Bar, 99 percent} & 19.935 & 19.935 & 35.463 \\ \hline
\text{Eigen} & 22.424 & 6.059 & 37.833 \\
\text{Bar, 99 percent} & 18.520 & 18.520 & 25.865 \\ \hline
\text{Relations} & 1 & 0 & 1
\end{array}
```

All three claims hold on both statistics.

1. **Before the break, one relation.** Both statistics clear their bars, and the test stops at one relation rather than two.
2. **After the break, none.** Both statistics fall short even of the 90 percent bars, 13.429 for the trace and 12.297 for the eigen statistic. The test finds nothing at any level it reports, so the pair has not merely weakened.
3. **The three funds, exactly one.** The test rejects a rank of 0 easily and cannot reject a rank of at most 1 at any level. Its trace statistic for that second step is 7.005 against a 90 percent bar of 13.429.

The nearest call is the first, where the trace statistic clears its bar by 2.636. Every other statistic clears or misses its bar by more, and the counts at 90 and 95 percent agree with the count at 99 on every claim. So the two choices the book left open, which statistic and which level, change nothing here. That is not always so. On [another of Chan’s examples](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md#lesson-3-the-trace-and-eigen-tests-disagree) in the same book, the two statistics disagree on his own file.

The Engle-Granger test from the earlier post sees the same break, though before the break it passes only at 95 percent. That test rejects when its statistic falls below its bar. Run on GLD against GDX, it gives a statistic of −3.724 before the break, past its 95 percent bar of −3.34 and short of its 99 percent bar of −3.90. After the break it gives −1.512, nowhere near either.

### USO’s peak and the first window’s portfolio, in one figure

The figure shows the break in two ways. The top panel plots the three closes. On Chan’s file, USO’s highest close, 117.48, falls on 2008-07-14 itself, the last day of his first window. The bottom panel plots a portfolio of GLD and GDX held in the weights the first window’s Johansen test finds, 0.191 shares of GLD against −0.514 of GDX, where the minus sign means a short position. The panel shows its value in standard deviations from its own first-window average. Before the break the portfolio stays between −3.24 and 2.56 and keeps crossing its average. After the break it runs from 0.47 to 13.52 and never comes back.

![Two line charts stacked on one shared date axis from May 2006 to April 2012, with a dashed vertical line on July 14, 2008 in both. The top chart plots the closes of GLD, GDX and USO in dollars. USO climbs to its highest close of 117.48 on the dashed line, marked with a dot, then collapses to about 23 by early 2009. GLD dips in late 2008 and then climbs to about 185 in 2011. GDX falls with USO in late 2008, recovers to between about 40 and 66 from 2010, and ends near 46. The bottom chart plots GLD and GDX held in the first window’s Johansen weights, 0.191 and −0.514 shares, in standard deviations from that portfolio’s mean over the first window. Left of the dashed line it moves between −3.24 and 2.56 and crosses zero again and again. Right of the line it starts at its lowest value, 0.47, jumps above 12 in late 2008, sags to between about 1.3 and 9 through 2009 and 2010, and climbs to 13.52 by April 2012, staying above zero throughout. The title calls the figure exploratory, and the note names Chan’s file and says the split date was chosen after the break was seen.](../docs/figures/gold_miners_oil_break.png)

*The three closes, and the first window’s GLD and GDX portfolio carried across the break, on Chan’s file over the 1,481 days GDX is priced.*

The bottom panel holds the first window’s weights fixed, so everything right of the dashed line on 2008-07-14 shows those weights on days they never saw. The second window’s own Johansen test is a stronger statement. It fits fresh weights to the 942 days after the break and still finds no stationary mix.

### What the book’s “99 percent probability” means

The book’s “99 percent probability” reads as a 99 percent chance that the pair cointegrates, which the test cannot say. The 99 percent is the level the test was run at, where a statistic past the bar would turn up less than 1 percent of the time with no relation. It is not a probability that the claim is true.

## Lesson 2: the control the book leaves out finds nothing, so USO adds something

A result for the triplet, the three funds together, over the whole span means something only if the pair alone fails over the same days. If GLD and GDX already cointegrated from 2006 to 2012 by themselves, adding USO would find their relation again and say nothing about oil. The book does not run that check.

Run here, the pair alone over the triplet’s 1,481 days gives a trace statistic of 10.447, short of even its 90 percent bar of 13.429. With USO added, the first trace statistic is 44.838, past its own 99 percent bar of 35.463. A test on three funds sets higher bars than a test on two, so each statistic is read against its own bar. Without USO the test finds no relation over these days, and with it the test finds one, so adding USO is what lets the test find it. Lesson 3 asks what USO adds.

## Lesson 3: the weights say what the count cannot

The first control shows that USO matters to the triplet. It does not show how. Chan’s story says oil restores the link between gold and the miners. But one relation among the three funds is also what a link between gold and oil alone, or between the miners and oil alone, would produce, with the remaining fund added on.

This repository added two more tests after the first run, over the same 1,481 days. One pairs USO with GLD alone, the other with GDX alone. Each column below is one of those pairs, and its rows give the trace statistic for the first step, its bars at 90 and 99 percent, and the number of relations the test counts at 99 percent.

```math
\small\begin{array}{l|r|r}
 & \text{GLD, USO} & \text{GDX, USO} \\ \hline
\text{Trace} & 4.350 & 27.166 \\
\text{Bar, 90 percent} & 13.429 & 13.429 \\
\text{Bar, 99 percent} & 19.935 & 19.935 \\ \hline
\text{Relations} & 0 & 1
\end{array}
```

Gold and oil alone find nothing, even at 90 percent. The miners and oil alone find one relation at 99 percent. So by its count alone, the triplet’s single relation could be that pair’s own, and a rank of one cannot tell it apart from Chan’s reading.

The triplet’s weights can. A third test, added in a review before this post was published, uses a test from Johansen’s 1991 paper to ask whether one fund’s weight in the relation could be zero. If the relation were the miners and oil pair’s own, GLD’s weight would be zero. Setting it to zero gives a statistic of 10.015, past the 95 percent bar of 3.841 and the 99 percent bar of 6.635. Those bars come from large-sample theory, which rejects too often on a sample this size, so the result is safer read at 95 percent. Setting USO’s weight to zero gives 0.057, nowhere near any bar. So the triplet’s relation needs gold and the miners, and its weight on oil cannot be told from zero.

The two results pull against each other. If the miners and oil truly shared a relation, the triplet’s single relation would have to be that one, so the pair’s result and the weight test cannot both be right. The first detail below is a reason to trust the pair’s result less. Oil still matters, since GLD and GDX alone find nothing over these days. What USO adds comes through how the funds’ prices change from day to day rather than through the mix. Chan’s mechanism, in which dear oil cuts the miners’ profits, suggests a mix with oil’s price in it, and the weights do not find oil there.

Two details bear on how far to trust these results.

1. **The miners and oil reach full rank at 90 percent.** Full rank is a count equal to the number of funds. At that level the test rejects both of its hypotheses, which on its face says each fund is stationary by itself. Yet a separate test on each fund alone finds neither one stationary, even at 90 percent. No claim here is judged at 90 percent, so this changes no verdict, but it is a reason not to lean hard on the GDX and USO result.
2. **The sizes of the weights do not compare across funds.** The triplet’s eigenvector is 0.033109 shares of GLD, −0.177036 of GDX and 0.002549 of USO. Those are shares, and the three funds trade at different prices, so their sizes cannot be read as how much each fund matters. The zero-weight test does not have that problem, since a weight of zero is zero at any price.

## Lesson 4: a hypothesis formed on the sample cannot be confirmed by it

Chan’s example shows the right process: when a strategy stops working, form a hypothesis about why and test it. The test here cannot finish that process, for two reasons.

1. **The split date was chosen by looking.** Chan saw the pair break and then named the day. A test that splits the sample on that day is tilted toward finding a break there.
2. **The third fund was chosen by looking too.** Oil was proposed after the break was seen, as the explanation for it. The triplet’s result therefore tests a hypothesis on the same data that suggested it.

The result is exploratory however it comes out. It shows that Chan’s claims follow from his file. It cannot show that oil caused the break. A test that could show it would take the hypothesis as Chan stated it, write it down first, and run it on data the hypothesis was not formed on, which here means GLD, GDX and USO after April 2012.

## What this replication cannot say

Five questions are beyond it.

1. **Anything about oil itself.** Over these years USO held the crude oil futures contracts nearest expiry rather than oil. As each one neared expiry the fund sold it and bought the next, and that roll lets the fund drift from the spot price, the price of oil delivered today. The triplet’s relation is with the fund, and whether it holds with the spot price is a different test.
2. **Where inside the second window the link failed.** One test over 2008-07-15 to 2012-04-09 says the window as a whole holds no stable relation. It cannot date the break inside it, and it says nothing about the years after 2012. The earlier post’s rolling test asks a different question. It slides a one-year Engle-Granger test along closing prices downloaded from Yahoo Finance in 2026, and 9 of the 45 tests whose year ends inside Chan’s second window still pass at the 90 percent level. Its passing tests run into 2015 before they thin out, which is why that post places the miners’ detachment from gold in the 2010s. One relation across nearly four years and short stretches inside them are different claims, so the two results do not contradict each other.
3. **How much the tests confirm each other.** The whole span contains both of the pair’s windows, so the tests are not independent, and nothing here corrects for running several tests on one sample.
4. **Whether Chan’s trading rule works.** He suggests trading the triplet, or at least ceasing to trade GLD against GDX whenever oil exceeds a threshold. Nothing here backtests either.
5. **Whether the oil hypothesis holds.** It was formed on this sample and tested on the same one, which Lesson 4 explains.

## What this means for a trader

One habit for each lesson.

1. **Read a test level as a test level.** “99 percent” means a statistic this large would turn up less than 1 percent of the time with no relation. It is not a probability that there is one.
2. **Run the control the story skips.** A third series that restores a relation means something only if the original pair fails without it over the same days.
3. **Test every pair inside a triplet, then test the weights.** One relation among three series can look like the work of any two of them. The pairwise tests say which pairs hold a relation alone, and a test of whether each fund’s weight is zero says which funds the triplet’s relation needs.
4. **Fix the hypothesis before the data that tests it.** A split date and an explanation both chosen after seeing the break make a hypothesis to test next, not a result.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Kindle location 1922.
2. Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551–1580.
3. Engle, R. F., and Granger, C. W. J. (1987). Co-integration and error correction: representation, estimation, and testing. *Econometrica*, 55(2), 251–276.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gold_miners_oil.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/gold_miners_oil_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gold_miners_oil.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_gold_miners_oil_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-29-gld-gdx-and-uso-around-july-2008-chans-algorithmic-trading) that sets each of Chan’s claims beside what was found here.*
