# Chan’s other stationary spreads: a currency rate holds and a bond pair does not

*One series and a fitted pair are tested against different bars, and on the currency rate the bar decides the verdict.*

## Why the bar matters

The Canadian dollar against the Australian dollar gives a test statistic of −3.2136 over nineteen years. Read as one series, that clears the 5% bar of −2.86, and Ernest Chan’s claim that the rate is stationary holds. Read against the bar a fitted pair of prices has to clear, −3.34, the same number fails. Which bar is right depends on whether anything was fitted before the test ran.

Chan’s *Quantitative Trading* (Chan, 2021) works its pairs-trading chapter on gold against gold miners. Then, at Kindle location 3951, it says stationarity is not limited to the spread between stocks. It names three more places to look:

1. **A currency rate.** The CAD/AUD cross rate “is quite stationary”, Chan writes, “both being commodities currencies”.
2. **Futures calendar spreads.** A long and a short position in one commodity’s futures, expiring in different months.
3. **Bonds of one issuer at two maturities.** Chan writes that “fixed-income instruments can be found to be cointegrating”, long one maturity and short another.

He names them and works none of them, so he prints no number to match. This replication tested the first and the third. The CAD/AUD rate holds. The bond pair, tested on two Treasury funds, does not. The futures spread needs contract-level prices with the roll between contracts intact, which cost money and are not in the repository yet, so it waits on [issue 137](https://github.com/l3a0/quantitative-trading/issues/137).

Two earlier posts covered the machinery. [How to test whether a price spread mean-reverts](https://baowebdev.substack.com/p/how-to-test-whether-a-price-spread) builds the augmented Dickey-Fuller (ADF) test, the Engle-Granger test for a pair, the residual check on the lag count, and the half-life. [Lessons from testing GLD/GDX for cointegration](https://baowebdev.substack.com/p/lessons-from-testing-gldgdx-for-cointegration) shows a pair whose relationship came and went. This post assumes both and draws five lessons from what the two new tests add. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## The two tests

**The rate.** The series is `CADAUD=X`, Yahoo Finance’s quote of the rate in Australian dollars per Canadian dollar, downloaded on 2 October 2026. The vendor’s history starts in July 2005 and has a hole: it returned nothing for the 90 weekdays from 2 April to 3 August 2007. A regression on lagged values across that hole would treat four months as one day, so the test reads from 6 August 2007 to 30 September 2026, 4,984 days. It runs an ADF test with a constant on the log of the rate, at one lag, which is the setting Chan uses throughout the book.

**The bond pair.** Chan names no bond, so this replication chose two funds to stand in. TLT holds Treasuries maturing in twenty years or more and IEF holds Treasuries maturing in seven to ten, so the two are one issuer at two maturities. Both were named in writing before anything was downloaded. The closes are adjusted for splits and not for dividends. Most of a bond fund’s return is its distributions, so a dividend-adjusted pair would drift apart by what the two maturities pay rather than by anything about whether their prices are tied. The test is Engle-Granger with an intercept, at one lag, over the 6,083 days from 30 July 2002 to 1 October 2026, also downloaded on 2 October 2026.

The results, in one line each:

1. **CAD/AUD reproduces.** The statistic is −3.2136 at one lag and −2.9946 at the first lag count whose residuals pass the check, against a 5% bar of −2.86. The criterion that both must clear it was written down before either was computed.
2. **TLT and IEF do not cointegrate.** With TLT as the dependent leg the statistic is −2.3887, and with IEF it is −2.3168, both short of even the 10% bar of −3.04.

Both results are exploratory. They used the data to check a claim someone else chose, so they say whether that claim held on these series over these years and nothing more.

## Lesson 1: a named series can be checked, a class can only be sampled

Chan works neither example, so neither result has a printed figure to match. They still end up as different kinds of result.

The CAD/AUD sentence names one series and says something definite about it. That is a claim this repository can check directly, so it carries a verdict, and the verdict is “reproduced”. The rule for reaching it was fixed before any statistic was read: the one-lag statistic and the statistic at the first lag count whose residuals pass must both clear the 5% bar. Writing the rule first is what stops the choice of rule from following the number.

The bond sentence names a class of instruments and says such pairs “can be found”. No single pair can refute that. TLT and IEF are a sample from the class, and a sample this replication chose, so their result is a finding about those two funds rather than a verdict on Chan’s sentence. Each fund is also a rolling basket held near a constant maturity, while a real bond’s maturity shrinks every day until it stops trading, which is one more step between the stand-ins and the claim.

A stand-in that fails keeps its failure. Trying a second pair of funds after seeing the first one fail would turn a test into a search, so the finding stands as it is.

## Lesson 2: one series and a fitted pair are held to different bars

The earlier post built the ADF test on a spread, the leftover from regressing one price on another:

```math
\Delta z_t = \gamma z_{t-1} + \phi_1 \Delta z_{t-1} + \varepsilon_t
```

There is no constant, because a regression with an intercept makes the spread average zero by construction. A rate is not a leftover from any regression. Its log sits wherever the rate has tended to sit, not at zero, so its test needs a constant `c`:

```math
\Delta y_t = c + \gamma y_{t-1} + \phi_1 \Delta y_{t-1} + \varepsilon_t
```

There is no trend term, because Chan’s claim is that the level is stationary. Adding the constant changes the bars the statistic has to clear. Three tables matter here:

```math
\begin{array}{l|c|c|c}
\text{Test} & 10\% & 5\% & 1\% \\ \hline
\text{ADF, no constant} & -1.62 & -1.94 & -2.57 \\
\text{ADF with a constant, for one series} & -2.57 & -2.86 & -3.43 \\
\text{Engle-Granger, for a fitted pair} & -3.04 & -3.34 & -3.90
\end{array}
```

The value −2.57 appears twice. It is the 1% bar of the plain ADF in the earlier post and the 10% bar of the ADF with a constant here. A reader carrying one table into the other’s test misreads a statistic by two whole levels.

The pair’s bars are stricter for the reason the earlier post gave. Engle-Granger first fits the hedge ratio that makes the spread vary as little as possible, which is the combination of the two prices that looks most stationary. Even two unrelated random walks leave a spread that looks mean-reverting after that fit, so the statistic has to clear a more negative bar to count.

The cross rate pays no such price. In logs it is the difference between the Canadian and Australian dollars’ rates against any third currency, a spread whose hedge ratio is fixed at one. Nothing is fitted, so the ADF’s bars apply.

On this rate the choice of table decides the verdict. Both statistics the verdict reads, −3.2136 and −2.9946, clear the one-series 5% bar of −2.86. Read against the pair’s 5% bar of −3.34, both would miss. At the pair’s 10% bar of −3.04 they would split, with the one-lag statistic clearing and the residual-clean one not. Neither clears the one-series 1% bar of −3.43 either, so “quite stationary” holds at 5% and no stronger.

The constant matters just as much. Without it, the one-lag statistic on the same series is −2.5159 rather than −3.2136, a different regression read against a different table.

![Two horizontal number lines of t-statistics from −4.1 to −2.0. The upper line, for one series tested by an ADF with a constant, has bars at −3.43, −2.86 and −2.57 for 1%, 5% and 10%, with the region past −2.86 shaded. CAD/AUD’s statistics, −3.2136 at one lag and −2.9946 at ten lags, sit inside the shaded region. The lower line, for a fitted pair tested by Engle-Granger, has bars at −3.90, −3.34 and −3.04, with the region past −3.34 shaded. TLT on IEF at −2.3887 and IEF on TLT at −2.3168 sit far outside it, and CAD/AUD’s two statistics, drawn again as hollow marks, sit outside it too.](../docs/figures/stationary_candidates_bars.png)

*The same two CAD/AUD statistics fall inside the one-series 5% region and outside the pair’s. TLT and IEF miss the pair’s bars by a wide margin either way round.*

## Lesson 3: the residual check can strengthen a finding, narrow a verdict, or reverse one

The ADF adds lagged changes to soak up autocorrelation, and leftover autocorrelation means the bars no longer apply. The earlier post’s check asks two things of a fit’s residuals: that a Breusch-Godfrey test for autocorrelation over ten lags gives a p-value above 0.10, and that none of the first ten autocorrelations falls outside a band of ±1.96/√n. On GLD/GDX’s Chapter 3 window, the first lag count that passed both turned a rejection into no rejection. The two new tests show the other two outcomes.

**On TLT and IEF the check strengthened the finding.** Both one-lag fits fail it, with Breusch-Godfrey p-values below 0.0001 and autocorrelations outside the band at nearly every lag. The first fits that pass are at 31 lags in both orientations, and there the statistics are −1.5677 and −1.5387, further from rejecting than at one lag. The finding that the pair does not cointegrate only gets firmer.

The two halves of the check did different work here. Every autocorrelation is inside the band from 9 lags for TLT on IEF and from 10 for IEF on TLT, and every fit from there to 30 lags still fails the Breusch-Godfrey test. A check that read only the band would have stopped 22 and 21 lag counts early, at statistics nearer rejection.

**On CAD/AUD the check narrowed the verdict without turning it.** The one-lag fit fails, with a Breusch-Godfrey p-value of 0.0002 and residual lags 2, 6, 7 and 10 outside the band. The first passing fit is at 10 lags, with a p-value of 0.6487, and its statistic of −2.9946 still clears −2.86. Every lag count from 0 to 32 rejects at 5%, the closest being 6 lags at −2.8739, so here the lag count could not have decided the verdict.

The search for a passing lag count needs a ceiling, or it becomes a hunt for the lag count that gives the wanted answer. Schwert’s rule, 12·(n/100)^(1/4) rounded up, sets it from the sample size before any statistic is read: 34 lags at TLT and IEF’s 6,083 days, 32 at the rate’s 4,984, and 33 at GLD/GDX’s 5,099. Long histories push the ceiling up, and on the bond pair the first pass landed close to it.

## Lesson 4: a rate stationary over nineteen years rarely looks it in one

CAD/AUD’s half-life is 141.6 trading days, so a gap from its average takes a little over half a year to close halfway. Over the whole window the test rejects. In a rolling scan of 226 one-year windows, stepped a month at a time, only 23 reject at 10% and 5 at 5%.

GLD/GDX had the opposite shape. Over 2006 to 2026, on dividend-adjusted closes, it fails at −1.45 with a half-life of 833.5 days, while 31 of its 231 one-year windows on as-traded closes clear the 10% bar, clustered around Chan’s own years. That pair looked tied in short windows and came apart over the long one. The rate looks loose in short windows and holds over the long one.

TLT and IEF never reject over their whole history, yet 56 and 51 of their 278 one-year windows clear 10%, one orientation and then the other. Just over half of those, 30 and 29, end in 2003-04 or 2020-21.

None of those windows is a finding. A scan describes the span it covers, and a window that happens to reject is one of many looks at the same data. Nothing in the replication measures why so few CAD/AUD windows reject. One hypothesis is that a year is too short to see a reversion this slow: a 252-day window holds about 1.78 half-lives, under two. That is a reason the scan could miss a real reversion, and it stays a hypothesis until something tests it.

## Lesson 5: every choice that could turn the answer was fixed before any statistic

A test with free choices can be steered by them, so each one was closed in writing before the statistic it could move was computed.

1. **Which leg depends on which.** Engle-Granger regresses one price on the other, the answer depends on the order, and Chan names no order. So both orientations are reported. They sit 0.0719 apart, so the choice could not have turned this finding.
2. **Which way the rate is quoted.** Chan writes CAD/AUD and the vendor quotes Australian dollars per Canadian dollar. On the log the two directions are the same series with the sign flipped, and the test gives one answer. On the level they part, at −3.2944 and −3.1552 at one lag and −3.0241 and −2.9734 at 10 lags. The level was the one choice tried both ways, after the log’s statistic was read, and all four of those statistics still reject at 5%.
3. **The lag.** One lag for both candidates, Chan’s own setting, with the residual check beside it rather than in place of it.
4. **The window.** The command that runs either test accepts no window, and the cross rate’s start date was fixed on the first day after the vendor’s gap. A window option is exactly the setting that would let someone keep trying until one rejects.

The window was fixed after the download, because only the download could show the gap. What mattered is that it was fixed before any statistic was computed.

## What this replication cannot say

The two results cover two series over two spans. Four questions are beyond them.

1. **Whether trading the rate pays.** Stationarity is a property of the series. A trade adds costs, the carry from two interest rates, and the problem of sizing a position against a half-life of 141.6 trading days. None of those are tested here.
2. **Whether individual bonds, or the yields behind them, behave like the funds.** A fund rolls its holdings to stay near one maturity. Treasury futures and individual bonds both need data the repository does not hold, and a yield cannot be bought or sold, so testing yields would be a different claim.
3. **Whether the rate behaved the same before August 2007.** The two years of history before the vendor’s gap are kept in the data and not tested.
4. **Whether either result survives another download.** Unadjusted closes change only when a fund splits, and a currency rate has no corporate actions, but a vendor can still fill or change its history. A check in the test suite fails if a new download fills the 2007 gap, so the window cannot move quietly.

## What this means for a trader

Five habits follow from the lessons above.

1. **Name the table before reading the statistic.** The same −3.2136 passes one table and fails another, and −2.57 means two different things in two tables.
2. **Ask whether the hedge ratio was fixed or fitted.** A fitted ratio earns a stricter bar. A spread whose ratio is fixed in advance, like a cross rate, does not.
3. **Check the residuals before trusting the statistic.** The check can reverse a verdict, narrow it or harden it, and a statistic from a fit that fails it is read against bars that do not apply.
4. **Keep the span and the window apart.** A verdict over nineteen years says little about any one year, and a run of rejecting years says little about the whole.
5. **Close the free choices before computing.** Which leg, which quote, which lag and which window can each move a statistic across a bar, and a choice made after seeing the number is a search.

Chan’s passage names three places a stationary spread lives. On a modern download the currency rate holds at 5%, the bond funds do not cointegrate, and the futures spreads wait on data that has to be bought. The bar each one was held to came from what was fitted before the test, and on the rate that bar decided the verdict.

## References

- Breusch, T. S. (1978). Testing for autocorrelation in dynamic linear models. *Australian Economic Papers*, 17(31), 334–355.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. *Econometrica*, 55(2), 251–276.
- Godfrey, L. G. (1978). Testing against general autoregressive and moving average error models when the regressors include lagged dependent variables. *Econometrica*, 46(6), 1293–1301.
- MacKinnon, J. G. (2010). *Critical values for cointegration tests*. Queen’s Economics Department Working Paper No. 1227.
- Schwert, G. W. (1989). Tests for unit roots: A Monte Carlo investigation. *Journal of Business & Economic Statistics*, 7(2), 147–159.

*Not investment advice. Code: [the two tests](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates.py) and [the chart](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates_figures.py), with the checks behind [the tests’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates.py) and [what the chart draws](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates_figures.py), and the replication log’s entries for [the bond pair](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-5-the-fixed-income-candidate-chans-quantitative-trading) and [the rate](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-6-the-cadaud-cross-rate-chans-quantitative-trading).*
