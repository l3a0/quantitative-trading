# Chan’s AUD.USD against CAD.USD reproduces on every day, and the Johansen test rarely found a relation behind its hedge

*Example 5.1 of Algorithmic Trading trades the Australian dollar against the Canadian dollar in weights a Johansen test supplies each day. On Chan’s own closes every one of the 612 returns matches the one he saved, while the test found a relation in 26 of the 612 windows of 250 days that set the weights, and on 90 days the weights held both currencies long or both short.*

## Why the quote currency decides what a hedge means

A pair trade holds one thing against another in proportions chosen so the combination stays near a fixed level. In Ernest Chan’s *Algorithmic Trading*, those proportions often come from the Johansen test, which reads several price series together and returns weights for each. With currencies the weights only mean something if each price is measured the same way. Chan warns that the test and the returns need “a point move in one currency pair” to have “the same dollar value as a point move in another currency pair”, and that otherwise “the results will not make sense” (Chan, 2013, Kindle edition, p. 163).

A currency price names two currencies. Chan’s own example is AUD.ZAR: the Australian dollar is the base currency, the one being bought, and the South African rand is the quote currency, the one the price is counted in. A quote of 9.58 means it takes 9.58 rand to buy one Australian dollar (Chan, 2013, p. 164). AUD.USD is therefore counted in US dollars. The Canadian dollar is normally quoted the other way, as USD.CAD, the price of a US dollar in Canadian dollars. A move of 0.01 in AUD.USD is worth one US cent per unit, and a move of 0.01 in USD.CAD is worth one Canadian cent, so the two are not the same size.

Example 5.1 fixes that by turning USD.CAD over into CAD.USD, so both legs are quoted in US dollars. On pp. 164 to 165 Chan gives the reason: “in order to interpret the eigenvector from the Johansen test as capital weights, the two price series must have the same quote currency.” An eigenvector is one of the test’s sets of weights, with one weight per currency. A capital weight says how many dollars to hold of each.

Chan expects the two currencies to move together because the stock index funds of Australia and Canada do, and he notes that traders call both commodity currencies, the currencies of countries that export a lot of raw materials (Chan, 2013, p. 163). He reports an annual return of 11 percent and a Sharpe ratio of 1.6 from 2009-12-18 to 2012-04-26 (Chan, 2013, p. 168). The Sharpe ratio is the average daily return over its standard deviation, scaled to a year.

### What the reproduction found

This repository transcribed Chan’s MATLAB script, `AUDCAD_unequal.m`, line by line and ran it on the daily closes from his 2018 Python port of the book’s code. The port is his rewrite of that code in Python, and it comes with its own data files. The results fall into four groups.

1. **Every figure the script prints matches**, because every one of the 612 daily returns matches the return Chan’s own script saved.
2. **The match shows that the closes run here are the ones Chan’s MATLAB script read**, except that each currency’s closes could all be multiplied by a constant of its own without changing the match. It shows nothing more.
3. **The test rarely found a relation behind the hedge it supplied.** A relation is a weighted combination of the two prices that stays near a fixed level. Each day’s weights come from the 250 days before it, called that day’s window. The test found a relation in 26 of the 612 windows, and on 90 days the weights held both currencies long or both short.
4. **The Python port’s version of the example is a different strategy**, so its printout is no check on the data.

**Every result here is exploratory.** Chan chose the currencies, the dates and the 250-day window, and the reproduction runs them on the same days he did. It can say whether his numbers follow from his files and nothing about whether the pair trades today.

The six lessons below take the four groups in order, with the third split across Lessons 3 and 4, and close on what an exact match cannot show. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The rule and the files

On p. 167 Chan calls the rule “a classic linear mean-reverting strategy”, the one the [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) builds up on two ETFs. Here it runs in four steps each day.

1. **The legs.** AUD.USD, and CAD.USD computed as one over USD.CAD. Every set of weights lists AUD.USD first.
2. **The hedge.** Run the Johansen test on the 250 days before today. The test’s model includes a constant, so the level the combination returns to need not be zero, and it includes the previous day’s change in each price. Take its first eigenvector, the set of weights whose combination the test finds pulled back to its level most strongly. That is the day’s hedge: how many units of each currency one portfolio holds. The [post on the Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) explains the eigenvectors and how the test counts relations.
3. **The units.** Value the hedge portfolio on each of the 20 days ending today, and take the average and standard deviation of those 20 values. Today’s z-score is the number of standard deviations today’s value sits above or below that average. Hold minus that many portfolios, so the rule sells the portfolio when it is high and buys it when it is low.
4. **The return.** Each day’s profit is yesterday’s holding in each currency, in dollars, times today’s percent change in its price. The return is that profit over yesterday’s total position, the dollars held long plus the dollars held short, which Chan calls the gross market value (p. 167).

The script charges no transaction cost and leaves out rollover interest, the interest a currency position earns or pays overnight. On p. 166 Chan says rollover interest is “usually not large for short-term strategies” like this one. The [post on AUD.CAD with rollover interest](https://github.com/l3a0/quantitative-trading/blob/main/blog/aud-cad-rollover-lessons.md) measures what it did to the next example, which trades the same two currencies as one cross-rate, a single price of the Australian dollar in Canadian dollars.

Chan’s MATLAB script loads two files of prices taken every minute, which neither of the two public copies of his code on GitHub includes. So the run here reads [two files](https://github.com/l3a0/quantitative-trading/blob/main/data/README.md) from his Python port instead, each holding 862 daily closes from 2009-01-02 to 2012-04-26, saved 2018-12-12. A third file from the port holds the 612 returns his MATLAB script saved. This repository transcribed the script from one of those copies, `ericnberwick/EpchanPreview`, at commit `e4bc46f`.

## Lesson 1: every figure matches, because every return does

The table below sets each figure the script prints, computed here, against the value the script’s comments record and the one the book prints. The APR is the annual percentage rate, the return compounded to a year of 252 days. That is the length of year the script annualises by, though these files hold about 260 closes a year. The Kelly leverage is the mean daily return over its variance, the leverage that maximizes growth when returns are close to normally distributed, which the [post on the Kelly leverage on SPY](https://github.com/l3a0/quantitative-trading/blob/main/blog/kelly-leverage-on-spy.md) derives. The test period is the 612 days after the first 250 days, from 2009-12-18 to 2012-04-26, as Chan says on p. 168.

```math
\small\begin{array}{l|r|r|r}
 & \text{APR} & \text{Sharpe} & \text{Kelly} \\ \hline
\text{Computed} & 0.112410 & 1.610890 & 23.845328 \\
\text{Script} & 0.112410 & 1.610890 & 23.845328 \\
\text{Book} & 11\ \text{percent} & 1.6 & \text{none}
\end{array}
```

All three match at the six decimals the script prints.

Three figures that agree this closely could still come from different returns. The stronger check is the returns themselves. Chan’s script saved its 612 daily returns, and each one computed here matches his to within one billionth, 1e-9, a criterion written down before any return was computed, as [Entry 25 of the replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-25-audusd-against-cadusd-chans-algorithmic-trading) records. Computing the three figures from his saved returns, rather than from the ones computed here, gives the same printed values. So the returns decide the figures, and matching them is the whole reproduction.

### The Kelly leverage the script prints and the one the book quotes

Two details sit inside the match on the Kelly leverage.

1. **The variance divides by n − 1**, where n is the number of returns. The Kelly leverage matches only with this sample variance, the one MATLAB’s `std` computes. Dividing by n instead gives 23.884354.
2. **The book quotes another figure for the same returns.** On p. 258 Chan says “the Kelly leverage is 18.4” for this strategy. Neither variance takes the saved returns to 18.4, so this post quotes the script’s 23.845328. The [post on Chapter 8’s leverage](https://github.com/l3a0/quantitative-trading/blob/main/blog/monte-carlo-leverage-lessons.md#lesson-2-example-51s-own-figures-rule-184-out) tries three ways of compounding the APR. Under each of them, no daily series with this example’s printed Sharpe ratio and APR has a Kelly leverage of 18.4. That post infers that Chapter 8 ran on a different series of returns, with a Kelly leverage near 18.4, that nobody holds. The evidence cannot tell when or how that series differed from the saved file.

## Lesson 2: the match ties the traded closes to Chan’s up to a scale on each leg, and no more

The MATLAB files Chan’s script read are not public, so nothing can compare them with the Python port’s daily files directly. The returns are the one output of the MATLAB script that can be compared, and they say how far the files agree.

Multiplying every close of one currency by the same constant is invisible to the returns. Double every AUD.USD close, and each day’s percent change is unchanged, since both closes in it double. The Johansen weights rescale to cancel it: the AUD.USD weight halves, so the dollars held in each leg stay the same. Every return comes out identical. Running the script with AUD.USD doubled and CAD.USD multiplied by 0.37 still matches Chan’s returns on every day. The [post on the price spread, the log price spread and the ratio](https://github.com/l3a0/quantitative-trading/blob/main/blog/price-spread-ratio-lessons.md) met the same blindness in another rule.

A change of one unit in the sixth decimal, 0.000001, can break the match, depending on where it falls. Six decimals is the most any close in the files carries. Adding it to one close in the test period breaks the match, because that close enters a day’s percent change directly. Adding it to the first close of the first window does not, because that close reaches the returns only through one day’s hedge, and it moves that hedge too little to change any return by more than one billionth.

So the match says the files in this repository carry the closes Chan’s MATLAB script traded, up to a constant scale on each currency. The closes before the test period are checked only as far as they move a hedge. The match says nothing about the port’s other files, its USD.CAD minute prices or its AUD.CAD closes, because this script reads neither.

## Lesson 3: the Johansen test rarely found a relation behind the hedge it supplied

The Johansen test does two jobs at once. It supplies weights, and it reports how many relations it finds. That count comes two ways, each built by stepping up from zero relations and asking at each step whether there is one more. The trace test weighs the evidence for all the further relations at once, and the eigen test weighs only the evidence for the next one. Both read the same data and can reach different counts, as the [post on the Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) shows. The script uses the weights every day and never reads the count.

Each count is taken at 95 percent confidence, meaning the test reports a relation only when evidence that strong would turn up less than 5 percent of the time if the relation were not there. Reading the count on each of the 612 windows gives this.

1. **The trace test finds at least one relation in 26 windows.** It finds one in 7 of them and two in the other 19.
2. **The eigen test finds one in 11 windows**, and never finds two.

On 19 of its 26 windows the trace test found two relations between two series, which is a stronger claim than it sounds. It means every combination of the two stays near a fixed level, including each currency held alone. So the test is reading each currency as stationary on its own, returning to a fixed level by itself, rather than the two as sharing a level. The [post on the Johansen test on three ETFs](https://github.com/l3a0/quantitative-trading/blob/main/blog/johansen-etf-lessons.md) works through why.

### When the 26 windows fell

The 26 windows bunch into three stretches. Fifteen fall from 2010-02-09 to 2010-04-08, six from 2011-01-19 to 2011-02-09, and five from 2011-08-08 to 2011-08-15. Every two-relation window sits in the first stretch or the third, and the eigen test’s 11 all fall from 2011-01-19 to 2011-02-10.

The figure below shows where they fell against what the rule held.

![Two charts stacked on one shared date axis from December 2009 to April 2012. The top chart plots each day’s hedge in dollars as CAD.USD’s share of the total position, with AUD.USD held long, on a scale from −1 to 1. A dashed line at −0.5 marks equal dollars held against each other, and a solid line marks 0. The line starts near −0.64 and holds near −0.6 until late May 2010, apart from a one-day spike to about 0 on 2010-05-20. It then swings between about −1 and 1 through June 2010 and sits between about 0.7 and 1 from July to early October 2010, apart from a one-day drop to about −1 on 2010-07-06. Shading marks 85 days from June to early October 2010 and five in late 2011, 90 in all, on which both legs were held the same way. In October 2010 the line drops to about −1, climbs slowly to about −0.6 by the autumn of 2011, jumps to about 0.7 for a few days in late October 2011, and ends at −0.4325. Dots mark the 26 windows where the trace test found a relation at 95 percent: hollow dark dots for the 7 that found one, near −0.6 in February 2010 and near −0.8 in early 2011, and filled red dots for the 19 that found two, near −0.6 from February to April 2010 and in August 2011. No dot falls on a shaded day. The bottom chart plots the cumulative return, compounded, as a green line. It sits near 0 until May 2010, climbs to about 0.16 in early September 2010, falls back to about 0.12 in early October, then rises unevenly to a high of about 0.32 at the end of 2011, and ends at 0.2953. A horizontal line marks zero. The title calls the redraw exploratory.](../docs/figures/aud_cad_johansen.png)

*Each day’s hedge as a dollar split, with the trace test’s 26 windows marked, above the rule’s compounded return over the 612 test days, redrawn on Chan’s closes. At −0.5 the two legs hold equal dollars against each other, and above 0 they are held the same way. The bottom panel is the book’s Figure 5.1, “Cumulative Returns of USD.AUD versus USD.CAD Strategy”, drawn against the date rather than the row number.*

### How much 612 overlapping tests can show

A 95 percent confidence level on 612 windows is weak evidence either way. Each window shares 249 of its 250 days with the next, so the 612 tests are far from 612 separate looks, and a run of findings counts for much less than its length. The two rates are also close to random walks, series whose next change is a fresh draw with no level to return to. Against those the test has little ability to find a relation even when one is there. The [post on Chan’s stationary candidates](https://github.com/l3a0/quantitative-trading/blob/main/blog/stationary-candidates-lessons.md) met the same thing in the Canadian dollar priced in Australian dollars, which that post writes CAD/AUD. That series tested stationary over nineteen years and rarely within any one of them. The [post on gold, the gold miners and oil](https://github.com/l3a0/quantitative-trading/blob/main/blog/gold-miners-oil-lessons.md) follows a Johansen hedge that held on one window and broke on the next.

What the count does show is what the rule did on the remaining 586 days. Each of them took its weights from a window where the trace test found no relation. Chan’s rule never checks the count, so the figures in Lesson 1 come almost entirely from weights the test did not support.

## Lesson 4: a capital weight that wandered, and sometimes stopped being a spread

The point Chan makes on pp. 164 to 165 is that, once both legs share a quote currency, each weight times its price is a number of US dollars, so the weights translate directly into capital. The last day shows how. The hedge on 2012-04-26 holds 1 unit of AUD.USD against −0.7797 of CAD.USD. A unit is worth its price in US dollars, so in dollars, scaled so the AUD.USD leg is 1, that is 1 against −0.7622, long the Australian dollar and short about three quarters as much of the Canadian. Chan notes that using CAD.USD in the backtest makes live trading no harder: an order to buy a unit of CAD.USD is placed as a sale of USD.CAD (Chan, 2013, p. 165).

That day’s hedge is one of 612. The top panel of the figure draws each day’s hedge as one number, CAD.USD’s dollars as a share of the dollars held in both legs, with the sign set so that AUD.USD is the leg held long. At −0.5 the two legs hold equal dollars against each other, which is what a pair trade looks like. Above 0 the two are held the same way, long both or short both.

The hedge held both currencies the same way on 90 of the 612 days. Eighty-five of them fall from 2010-06-01 to 2010-10-05, and the longest run is 65 days, from 2010-07-07 to 2010-10-05. On those days the portfolio was not a bet that two currencies would come back together. It was long or short the US dollar against both of them at once. None of the 90 days took its weights from a window where the trace test found a relation.

### What the 90 days did to the return and its swings

Compounding the 90 days alone gives a return of 0.1074, and compounding the other 522 alone gives 0.1696. Returns compound by multiplying, so together they make the run’s 0.2953: unrounded, 1.1074 times 1.1696 is 1.2953. Logarithms turn that product into a sum, and ln 1.1074 is about two fifths of ln 1.2953. So 15 percent of the days, 90 of the 612, carried about two fifths of the growth. The bottom panel shows the stretch that holds 85 of them: the curve stood at 0.0214 on 2010-05-31, the day before the first of them, and at 0.1170 on 2010-10-05, the last day of the stretch.

The same 90 days were also the volatile ones. Their daily returns had a standard deviation of 0.0073, against 0.0035 on the other 522 days, about twice as wide. That is what a position that bets on the dollar’s direction gives, rather than one that bets on two currencies coming back together. Their average return was higher too, 0.0012 a day against 0.0003. A Welch t-test, which compares two averages without assuming the two groups are equally volatile, gives 1.09 for that difference, far short of what would rule out chance. So the claim is about what the rule held, not that holding it paid.

## Lesson 5: the port’s Example 5.1 is a different strategy

Chan’s 2018 Python port carries its own version of this example, and its printout reads a Sharpe ratio of 1.362926 rather than the script’s 1.610890, as [Entry 25](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-25-audusd-against-cadusd-chans-algorithmic-trading) records. That looks like evidence that the port’s data differs. It is not.

The port ends both the 250-day Johansen window and the 20 days behind the z-score a day earlier than the MATLAB script does. Running the script here with that one change puts 611 of the 612 returns more than one billionth away from Chan’s, every one but the first, which is zero either way. Its Sharpe ratio comes out at 1.359568, which is not the port’s 1.362926 either. So the port differs from the MATLAB script in more than the windows, and nothing here reproduces its printout.

The port’s number therefore says nothing about whether its files are Chan’s. Lesson 2 settled that from the MATLAB script’s own saved returns.

## Lesson 6: an exact reproduction checks the arithmetic, not the edge

Every figure in Lesson 1 matches, and none of that says the strategy would have paid. Chan says on p. 167 that the 250-day window “gives better results in hindsight”, so it was chosen after the returns were seen. A rule chosen by looking at these days cannot also be tested on them, which is why every result here is exploratory.

Lessons 3 and 4 say what the arithmetic rested on. The weights came from a test that found a relation in a few windows, and for part of 2010 they turned the pair into a bet on the US dollar. A rule that trades those weights without reading the test’s count or watching their signs can still reproduce to the last digit.

## What this replication cannot say

Three questions are beyond it.

1. **What costs and rollover interest would take.** The rule trades every day, and the script charges no cost. Chan sets rollover interest aside as small (p. 166), and nothing here measures how small.
2. **Whether the 250-day window was chosen on this sample.** Chan says it gives better results in hindsight. No run here tries another length, and any that did would be searching days already used to choose this one.
3. **Whether the pair trades today.** The run ends on 2012-04-26 with Chan’s data. It says whether his numbers reproduce on his files and nothing about the two currencies since.

## What this means for a trader

One habit for each lesson.

1. **Compare the returns, not only the summary.** Three figures that agree can come from different returns. A day-by-day match settles it.
2. **Know what a match cannot see.** A return ignores a constant scale on its prices, so a match on returns leaves the scale of each input unchecked.
3. **Read the test before trading its weights.** A Johansen eigenvector exists whether or not the test finds a relation, and two relations between two series means neither needs the other.
4. **Watch the signs of the weights, not only their sizes.** A rolling hedge that holds both legs the same way has stopped being a spread, and its risk is the risk of the direction it bets on.
5. **Treat a port’s printout as a claim.** A second implementation that disagrees may differ in its code or its data, and its printout cannot say which.
6. **Read an exact reproduction as arithmetic.** It checks that the figures follow from the files and the script, and nothing about the edge.

## References

1. Chan, E. P. (2013). *Algorithmic Trading: Winning Strategies and Their Rationale*. Wiley. Example 5.1, with pages 163 to 168 and 258 cited. The page numbers are the Kindle edition’s, which differ from the print edition’s.
2. `AUDCAD_unequal.m`, git blob `5b8fbc2`, at commit `e4bc46f` of ericnberwick/EpchanPreview, a public copy of Chan’s code. Its comments on lines 60 and 66 record the printouts `APR=0.112410 Sharpe=1.610890` and `f=23.845328`.
3. Johansen, S. (1991). Estimation and hypothesis testing of cointegration vectors in Gaussian vector autoregressive models. *Econometrica*, 59(6), 1551–1580.
4. Welch, B. L. (1947). The generalization of “Student’s” problem when several different population variances are involved. *Biometrika*, 34(1–2), 28–35.

*Not investment advice. Code: [the replication](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_johansen.py), [the Johansen wrapper](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/johansen.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/aud_cad_johansen_figures.py), with the checks behind [the replication’s numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_johansen.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_aud_cad_johansen_figures.py), [the book notes](https://github.com/l3a0/quantitative-trading/blob/main/research/book-notes/algorithmic-trading.md) that record every quoted sentence with its location, and the [replication log](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-25-audusd-against-cadusd-chans-algorithmic-trading) that sets each of Chan’s figures beside the one reproduced here.*
