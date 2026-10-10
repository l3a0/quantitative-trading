# Chan’s AUD.USD against CAD.USD reproduces on every day, and its Johansen hedge was rarely one the test backed

*Example 5.1 of Algorithmic Trading trades the Australian dollar against the Canadian dollar in weights a Johansen test supplies each day. On Chan’s own closes every one of the 612 returns lands on the one he saved, while the test found a relation in 26 of the windows that set the weights, and on 90 days the weights held both currencies the same way.*

## Why the quote currency decides what a hedge means

A pair trade holds one thing against another in proportions chosen so the combination stays near a fixed level. In Ernest Chan’s *Algorithmic Trading*, those proportions often come from the Johansen test, which reads several price series together and returns weights for each. With currencies the weights only mean something if each price is measured the same way. Chan warns that the test and the returns need “a point move in one currency pair” to have “the same dollar value as a point move in another currency pair”, and that otherwise “the results will not make sense” (Chan, 2013, location 2169).

A currency price names two currencies. Chan’s own example is AUD.ZAR: the Australian dollar is the base currency, the one being bought, and the South African rand is the quote currency, the one the price is counted in. A quote of 9.58 means it takes 9.58 rand to buy one Australian dollar (Chan, 2013, location 2186). AUD.USD is therefore counted in US dollars. The Canadian dollar is normally quoted the other way, as USD.CAD, the price of a US dollar in Canadian dollars. A move of 0.01 in AUD.USD is worth one US cent per unit, and a move of 0.01 in USD.CAD is worth one Canadian cent, so the two are not the same size.

Example 5.1 fixes that by turning USD.CAD over into CAD.USD, so both legs are quoted in US dollars. Location 2186 gives the reason: “in order to interpret the eigenvector from the Johansen test as capital weights, the two price series must have the same quote currency.” Chan expects the two to move together because the stock index funds of Australia and Canada do, and he notes that traders call both commodity currencies (Chan, 2013, location 2173). He reports an annual return of 11 percent and a Sharpe ratio of 1.6, the average return over its standard deviation, from 2009-12-18 to 2012-04-26 (Chan, 2013, location 2237).

This repository transcribed his script, `AUDCAD_unequal.m`, line by line and ran it on the daily closes from his 2018 Python port of the book’s code. The results fall into four groups.

1. **Every figure the script prints lands**, because every one of the 612 daily returns lands on the return Chan’s own script saved.
2. **The match ties the committed files to the ones Chan’s MATLAB read**, up to a constant scale on each currency, and no more.
3. **The test rarely backed the hedge it supplied.** It found a relation in 26 of the 612 windows the weights came from, and on 90 days the weights held both currencies long or both short.
4. **The Python port’s version of the example is a different strategy**, so its printout is no check on the data.

**Every result here is exploratory.** Chan chose the currencies, the dates and the 250-day fitting window, and the reproduction runs them on the same days he did. It can say whether his numbers follow from his files and nothing about whether the pair trades today.

The six lessons below say what the reproduction teaches. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

Location 2237 calls the rule “a classic linear mean-reverting strategy”, the one the [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds up on two ETFs. Here it runs in four steps each day.

1. **The legs.** AUD.USD, and CAD.USD computed as one over USD.CAD. Every set of weights lists AUD.USD first.
2. **The hedge.** Run the Johansen test on the 250 days before today, with a constant and one lagged daily change, and take its first eigenvector, the set of weights with the largest eigenvalue. That is the day’s hedge: how many units of each currency one portfolio holds. The [post on the Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains what the eigenvectors are and how the test counts relations.
3. **The units.** Value the hedge portfolio over the 20 days ending today, take today’s z-score, the number of standard deviations today’s value sits from the 20-day average, and hold minus that many portfolios. So the rule sells the portfolio when it is high and buys it when it is low.
4. **The return.** Each day’s profit is yesterday’s holding in each currency, in dollars, times today’s percent change in its price. The return is that profit over yesterday’s total holding, long and short together, which location 2237 calls the gross market value.

The script charges no transaction cost and leaves out rollover interest, the interest a currency position earns or pays overnight. Location 2205 says rollover interest is “usually not large for short-term strategies” like this one. The [post on AUD.CAD with rollover interest](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-rollover-lessons.md) measures what it did to the next example, which trades the same two currencies as one cross-rate.

The data is [two files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) from Chan’s Python port, saved 2018-12-12, of 862 daily closes each from 2009-01-02 to 2012-04-26. The script loads two MATLAB files of minute bars, which neither public copy of his code includes. A third file holds the 612 returns his MATLAB script saved. This repository transcribed the script from `ericnberwick/EpchanPreview` at commit `e4bc46f`.

## Lesson 1: every figure lands, because every return does

Here is each figure, computed, beside the value the script’s comments record and the one the book prints. The test window is the 612 days after the first 250, from 2009-12-18 to 2012-04-26, as location 2237 says.

```math
\begin{array}{l|r|r|r}
\text{Figure} & \text{Computed} & \text{Script's comment} & \text{Book} \\ \hline
\text{APR, compounded} & 0.112410 & 0.112410 & 11\ \text{percent} \\
\text{Sharpe ratio} & 1.610890 & 1.610890 & 1.6 \\
\text{Kelly leverage} & 23.845328 & 23.845328 & \text{none}
\end{array}
```

The APR is the annual percentage rate, the return compounded to a year of 252 trading days. The Kelly leverage is the mean daily return over its variance, the leverage that maximizes growth when returns are close to normal, which the [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md) derives. All three land at the six decimals the script prints.

Three figures that close agree could still come from different returns. The stronger check is the returns themselves. Chan’s script saved its 612 daily returns, and each one computed here lands on his within 1e-9, a criterion written down before any return was computed, as [Entry 25 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-25-audusd-against-cadusd-chans-algorithmic-trading) records. His saved returns give all three printed figures themselves. So the returns decide the figures, and matching them is the whole reproduction.

Two details sit inside that match.

1. **The variance divides by n − 1.** The Kelly leverage lands only with the sample variance, the one MATLAB’s `std` computes. Dividing by n instead gives 23.884354.
2. **The book quotes another figure for the same returns.** Location 3342 says “the Kelly leverage is 18.4” for this strategy. Neither variance takes the saved returns to 18.4, so this post quotes the script’s 23.845328 and leaves 18.4 unexplained.

## Lesson 2: the match ties the files to Chan’s up to a scale on each leg, and no more

The MATLAB files Chan’s script read are not public, so nothing can compare them with the Python port’s daily files directly. The returns are the one output of the MATLAB that can be compared, and they say how far the files agree.

A scale is invisible to them. Multiply every AUD.USD close by 2, and each day’s percent change is unchanged, since both closes in it double. The Johansen weights rescale to cancel it: the AUD.USD weight halves, so the dollars held in each leg stay the same. Every return comes out identical. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) met the same blindness in another rule. Running the script with AUD.USD doubled and CAD.USD multiplied by 0.37 still matches Chan’s returns on every row.

Almost anything else breaks the match. The files quote six decimals, so 1e-6 is one unit in the last digit. Adding it to one close in the test window breaks the match, because that close enters a day’s percent change directly. Adding it to the first close of the first fitting window does not, because that close reaches the returns only through one day’s hedge, which it moves too little to show.

So the match says the committed daily files carry the closes Chan’s MATLAB traded, up to a constant scale on each currency. It says nothing about the port’s other files, its USD.CAD minute bars or its AUD.CAD closes, because this script reads neither.

## Lesson 3: the Johansen test rarely backed the hedge it supplied

The Johansen test does two jobs at once. It supplies weights, and it reports how many relations it finds, where a relation is a weighted combination of the prices that stays near a fixed level. It reports that count two ways, through a trace statistic and an eigen statistic. Each reads the same eigenvalues and can reach a different count, as the [post on the Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) shows. The script uses the weights every day and never reads the count.

Reading it on each of the 612 windows, at 95 percent confidence, gives this.

1. **The trace statistic finds a relation in 26 windows.** In 19 of those 26 it finds two.
2. **The eigen statistic finds one in 11.**

Two relations between two series is a stronger claim than it sounds. It means every combination of the two reverts, including each currency held alone, so the test is reading each as stationary on its own rather than the two as sharing a level. The Johansen post works through why. On 19 of its 26 windows, the trace test’s finding is that one.

The 26 windows also bunch together. Fifteen fall from 2010-02-09 to 2010-04-08, six from 2011-01-19 to 2011-02-09, and five from 2011-08-08 to 2011-08-15. Every two-relation window sits in the first stretch or the third, and the eigen statistic’s 11 all fall from 2011-01-19 to 2011-02-10.

The figure below shows where they fell against what the rule held.

![Two charts stacked on one shared date axis from December 2009 to April 2012. The top chart plots each day’s hedge in dollars as CAD.USD’s share of the total position, with AUD.USD held long, on a scale from −1 to 1. A dashed line at −0.5 marks equal dollars held against each other, and a solid line marks 0. The line starts near −0.63, holds near −0.6 until late May 2010 apart from a one-day spike to about 0 on 2010-05-20, then swings between about −1 and 1 through June 2010 and sits between about 0.7 and 1 from July to early October 2010. Those days, 90 in all with five more in late 2011, are shaded red. In October 2010 the line drops to about −1, climbs slowly to about −0.6 by the autumn of 2011, jumps to about 0.7 for a few days in late October 2011, and ends at −0.4325. Dots mark the 26 windows where the trace test found a relation at 95 percent: hollow dark dots for the 7 that found one, near −0.6 in February 2010 and near −0.8 in early 2011, and filled red dots for the 19 that found two, near −0.6 from February to April 2010 and in August 2011. No dot falls on a shaded day. The bottom chart plots the cumulative return, compounded, as a green line. It sits near 0 until May 2010, climbs to about 0.12 by early October 2010, keeps rising unevenly to a high of about 0.32 at the end of 2011, and ends at 0.295. A horizontal line marks zero. The title calls the redraw exploratory.](../docs/figures/aud_cad_johansen.png)

*Each day’s hedge as a dollar split, with the trace test’s 26 windows marked, above the rule’s compounded return over the 612 test days, redrawn on Chan’s closes. The bottom panel is the book’s Figure 5.1, “Cumulative Returns of USD.AUD versus USD.CAD Strategy”, drawn against the date rather than the row number.*

A 95 percent level on 612 windows is weak evidence either way. Each window shares 249 of its 250 days with the next, so the 612 tests are far from 612 separate looks, and a run of findings is one finding seen many times. The two rates are also close to random walks, series whose next change is a fresh draw with no level to return to, and against those the test has little power to find a relation even when one is there. The [post on Chan’s stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) met the same thing in CAD/AUD, which tested stationary over nineteen years and rarely within any one of them.

What the count does show is what the rule did on the other days. On 586 of the 612 days, the strategy held weights from a window where the trace test found no relation. Chan’s rule never asks, and the figures in Lesson 1 are the rule’s.

## Lesson 4: a capital weight that wandered, and sometimes stopped being a spread

Location 2186’s point is that the weights are capital weights once both legs share a quote currency. The last day shows what that means. The hedge on 2012-04-26 holds 1 unit of AUD.USD against −0.7797 of CAD.USD. A unit is worth its price in US dollars, so in dollars that is 1 against −0.7622, long the Australian dollar and short about three quarters as much of the Canadian. Chan notes that this makes live trading no harder: an order to buy a unit of CAD.USD is placed as a sale of USD.CAD (Chan, 2013, location 2186).

That day’s hedge is one of 612. The top panel of the figure draws each as CAD.USD’s share of the whole position, with AUD.USD held long. At −0.5 the two legs hold equal dollars against each other, which is what a pair trade looks like. Above 0 the two are held the same way, long both or short both.

The hedge held both currencies the same way on 90 of the 612 days. Eighty-five of them fall from 2010-06-01 to 2010-10-05, and the longest run is 65 days, from 2010-07-07 to 2010-10-05. On those days the portfolio was not a bet that two currencies would come back together. It was long or short the US dollar against both of them at once. None of the 90 falls in a window where the trace test found a relation.

Those days mattered to the result. Compounding the 90 days alone gives a return of 0.1074, and compounding the other 522 alone gives 0.1696. Together they make the run’s 0.2953, so 15 percent of the days carried about two fifths of the growth. The bottom panel shows it: the curve stood at 0.0214 on 2010-05-31 and at 0.1170 on 2010-10-05.

The same 90 days were also the volatile ones. Their daily returns had a standard deviation of 0.0073, against 0.0035 on the other 522 days, about twice as wide. That is what a position that bets on the dollar’s direction gives, rather than one that bets on a spread. Their average return was higher too, 0.0012 a day against 0.0003. A Welch t-test, which compares two averages without assuming the two groups are equally volatile, gives 1.09 for that gap, far short of what would rule out chance. So the claim is about what the rule held, not that holding it paid.

## Lesson 5: the port’s Example 5.1 is a different strategy

Chan’s 2018 Python port carries its own version of this example, and its printout reads a Sharpe ratio of 1.362926 rather than the script’s 1.610890. That looks like evidence that the port’s data differs. It is not.

The port ends both the Johansen window and the z-score window a day earlier than the MATLAB does. Running the script here with that one change puts 611 of the 612 returns over the criterion, every one but the first, which is zero either way. Its Sharpe ratio comes out at 1.359568, which is not the port’s 1.362926 either. So the port differs from the MATLAB in more than the windows, and nothing here reproduces its printout.

The port’s number therefore says nothing about whether its files are Chan’s. Lesson 2 settled that from the MATLAB’s own saved returns. A port is a second implementation, and when it disagrees with the first, the difference can sit anywhere in the code before it reaches the data.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

Every figure in Lesson 1 lands, and none of that says the strategy would have paid. Location 2237 says the 250-day fitting window “gives better results in hindsight”, so it was chosen after the returns were seen. Reproducing Chan’s numbers on his days spends those days on a rule he chose, which is why every result here is exploratory.

Lessons 3 and 4 say what the arithmetic rested on. The weights came from a test that found a relation in a few windows, and for part of 2010 they turned the pair into a bet on the US dollar. A rule that trades those weights unread can still reproduce to the last digit.

## What this replication cannot say

Three questions are beyond it.

1. **What costs and rollover interest would take.** The rule trades every day, and the script charges no cost. Location 2205 sets rollover interest aside as small, and nothing here measures how small.
2. **Whether the 250-day window was chosen on this sample.** Chan says it gives better results in hindsight. No run here tries another length, and any that did would be searching the sample this one already spent.
3. **Whether the pair trades today.** The run ends on 2012-04-26 with Chan’s data. It says whether his numbers reproduce on his files and nothing about the two currencies since.

## What this means for a trader

One habit for each lesson.

1. **Compare the returns, not only the summary.** Three figures that agree can come from different returns. A day-by-day match settles it.
2. **Know what a match cannot see.** A return ignores a constant scale on its prices, so a match on returns leaves the scale of each input unchecked.
3. **Read the test before trading its weights.** A Johansen eigenvector exists whether or not the test finds a relation, and two relations between two series means neither needs the other.
4. **Watch the signs of the weights, not only their sizes.** A rolling hedge that holds both legs the same way has stopped being a spread, and its risk is the risk of the direction it bets on.
5. **Treat a port’s printout as a claim.** A second implementation that disagrees may differ in its code rather than its data.
6. **Read an exact reproduction as arithmetic.** It checks that the figures follow from the files and the script, and nothing about the edge.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.1 and Kindle locations 2169, 2173, 2186, 2205, 2237 and 3342.
2. `AUDCAD_unequal.m`, git blob `5b8fbc2`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. Its comments on lines 60 and 66 record the printouts `APR=0.112410 Sharpe=1.610890` and `f=23.845328`.
3. Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551–1580.
4. Welch, B. L. (1947). The generalization of “Student’s” problem when several different population variances are involved. *Biometrika*, 34(1–2), 28–35.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_johansen.py), [the Johansen wrapper](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/johansen.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_johansen_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_johansen.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_johansen_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-25-audusd-against-cadusd-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
