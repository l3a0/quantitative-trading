# Chan’s other stationary spreads: a currency rate holds and a pair of bond funds does not

*At the usual 5% level, the currency rate passes the cutoff for a single price series and would miss the stricter one for a fitted pair of prices. The rate involves no fitting, so the single-series cutoff applies.*

## Why the bar matters

The Canadian dollar against the Australian dollar gives a test statistic of −3.2136 over nineteen years. The more negative the statistic, the stronger the evidence that the rate keeps returning to its average. It counts as evidence only if it falls below the bar, a cutoff taken from a published table. Read as one series, the rate faces a 5% bar of −2.86. The statistic clears it, and Ernest Chan’s claim that the rate is stationary holds. A fitted pair of prices faces a stricter 5% bar, −3.34, and against that the same number falls short. Which bar is right depends on whether anything was fitted before the test ran.

Chan’s *Quantitative Trading* (Chan, 2021) builds its pairs-trading examples around gold against gold miners. Then it says stationarity is not limited to the spread between stocks. It names three more places to look:

1. **A currency rate.** The CAD/AUD cross rate “is quite stationary”, Chan writes, “both being commodities currencies”.
2. **Futures calendar spreads.** A long and a short position in one commodity’s futures, expiring in different months.
3. **Bonds of one issuer at two maturities.** Chan writes that “fixed-income instruments can be found to be cointegrating”, long one maturity and short another.

He names them without working any of them, so he prints no number to match. This repository tested all three. The CAD/AUD rate holds. The bond pair, tested on two Treasury funds, shows no evidence of it. The calendar spreads, tested on every pair of neighbouring natural gas and RBOB gasoline contracts in the US Energy Information Administration’s free settlement prices, hold for natural gas and not for gasoline, an exploratory result like the other two. This post covers the first and the third, which were tested first.

Two earlier posts covered the machinery in more depth. [How to test whether a price spread mean-reverts](https://baowebdev.substack.com/p/how-to-test-whether-a-price-spread) builds the tests step by step, and [Lessons from testing GLD/GDX for cointegration](https://baowebdev.substack.com/p/lessons-from-testing-gldgdx-for-cointegration) shows a pair whose relationship came and went. This post draws five lessons from what the two new tests add. The code is open source at [l3a0/quantitative-trading](https://github.com/l3a0/quantitative-trading).

## How the test reads

A series is **stationary** when it keeps returning to a fixed average instead of wandering off. A single price usually is not, which is why pairs trading looks for a combination of two prices that is. Two prices with such a combination **cointegrate**.

The **augmented Dickey-Fuller (ADF) test** checks one series. It regresses each day’s change on the day before’s level, plus a few earlier changes, called **lags**, which absorb **autocorrelation**, the tendency of one day’s change to echo an earlier one. If the series pulls back toward its average, the coefficient on the level is negative. The test statistic is that coefficient divided by its standard error, so the more negative it is, the stronger the pull.

The test **rejects** the hypothesis that the series wanders like a random walk when the statistic falls below a **critical value**, the textbook name for the bar. Each bar belongs to a significance level, the chance of rejecting when the series really is a random walk. The usual levels are 10%, 5% and 1%, and the 1% bar is the most negative. For a pair, the **Engle-Granger test** first regresses one price on the other, then runs the ADF on what the regression leaves over, the **residuals**.

## The two tests

**The rate.** The series is `CADAUD=X`, Yahoo Finance’s quote of the rate in Australian dollars per Canadian dollar, downloaded on 2 October 2026. The vendor’s history starts in July 2005 and has a hole: it returned nothing for the 90 weekdays from 2 April to 3 August 2007. A regression on lagged values across that hole would treat four months as one day, so the test reads from 6 August 2007 to 30 September 2026, 4,984 days.

The test is an ADF with three settings, and each changes the question it answers. The single lag matches Chan’s MATLAB code for GLD/GDX. The constant and the log are this repository’s choices, and all three were written down before any statistic was computed.

1. **A constant and no trend.** The constant lets the rate revert to whatever level it has tended to sit at. Leaving out a trend matches Chan’s claim, which is that the level itself is stationary, not that it reverts around a line that drifts. Lesson 2 shows what each alternative finds.
2. **The log of the rate.** Chan writes CAD/AUD without saying which currency is the unit, and a rate can be quoted either way round. On the log, flipping the quote only flips the sign, which leaves the statistic unchanged, so the answer does not depend on the convention. The log also turns the rate into a spread between two currencies, which Lesson 2 uses.
3. **One lag.** The lag absorbs a day’s change echoing the day before. Too few lags leave echoes behind, and the bars the statistic is read against no longer apply. Too many cost the test power, because each extra lag is one more coefficient estimated from the same days. Lesson 3 checks whether one is enough, and it is not.

**The bond pair.** Chan names no bond, so this repository chose two funds to stand in. TLT holds Treasuries maturing in twenty years or more and IEF holds Treasuries maturing in seven to ten, so the two are one issuer at two maturities. The repository named both in writing before downloading anything. The test reads raw closes, which this vendor adjusts for splits and not for dividends. Adjusting for dividends would fold each fund’s payouts into its price, so the pair would drift apart by the difference in payouts, which says nothing about whether the two prices move together. The test is Engle-Granger with an intercept, at one lag, over the 6,083 days from 30 July 2002 to 1 October 2026, also downloaded on 2 October 2026.

The results, in one line each:

1. **CAD/AUD reproduces.** The statistic is −3.2136 at one lag and −2.9946 at the first lag count that passes a check for leftover autocorrelation, against a 5% bar of −2.86. Both had to clear that bar, under a rule the repository wrote down before computing either.
2. **TLT and IEF show no evidence of cointegrating.** With TLT as the dependent leg, the one regressed on the other, the statistic is −2.3887. With IEF it is −2.3168. Both fall short of even the 10% bar of −3.04.

Both results are exploratory. They used the data to check a claim someone else chose, so they say whether that claim held on these series over these years and nothing more.

## Lesson 1: a named series can be checked, while a class can only be sampled

The CAD/AUD sentence names one series and says something definite about it. That is a claim this repository can check directly, so it carries a verdict, and the verdict is “reproduced”.

The bond sentence names a class of instruments and says such pairs “can be found”. No single pair can refute that. TLT and IEF are a sample from the class, and a sample this repository chose, so their result is a finding about those two funds rather than a verdict on Chan’s sentence. Each fund is also a rolling basket held near a constant maturity, while a real bond’s maturity shrinks every day until it stops trading, which is one more step between the stand-ins and the claim.

The repository does not swap in a second pair of funds after the first one falls short, because that would turn a test into a search.

## Lesson 2: one series and a fitted pair are held to different bars

[The post on testing a spread](https://baowebdev.substack.com/p/how-to-test-whether-a-price-spread) ran the ADF on a spread, the residuals of one price regressed on another:

```math
\Delta z_t = \gamma z_{t-1} + \phi_1 \Delta z_{t-1} + \varepsilon_t
```

Here `γ` is the pull back toward zero, `φ₁` weights the one lagged change, and `εₜ` is the day’s noise. There is no constant, because the regression that produced the spread had an intercept, so the spread already averages zero. A rate is not the residual of any regression. Its log sits wherever the rate has tended to sit, not at zero, so its test needs a constant `c`:

```math
\Delta y_t = c + \gamma y_{t-1} + \phi_1 \Delta y_{t-1} + \varepsilon_t
```

There is no trend term, for the reason given above. Each choice of terms comes with its own bars. Four sets matter here, one per row:

```math
\begin{array}{l|c|c|c}
\text{Test} & 10\% & 5\% & 1\% \\ \hline
\text{ADF, no constant} & -1.62 & -1.94 & -2.57 \\
\text{ADF with a constant, for one series} & -2.57 & -2.86 & -3.43 \\
\text{ADF with a constant and a trend} & -3.13 & -3.41 & -3.96 \\
\text{Engle-Granger, for a fitted pair} & -3.04 & -3.34 & -3.90
\end{array}
```

The value −2.57 appears twice. It is the 1% bar of the ADF with no constant, which that post used, and the 10% bar of the ADF with a constant here. A reader carrying one row into the other’s test misreads a statistic by two levels.

The pair’s bars are stricter for the reason that post gave. Engle-Granger first fits the hedge ratio that makes the spread vary as little as possible, which is the combination of the two prices that looks most stationary. That fit makes even two unrelated random walks look more mean-reverting than they are, so the statistic has to clear a more negative bar to count.

The cross rate pays no such price. In logs it is the difference between the Canadian and Australian dollars’ rates against any third currency, up to the small gaps that arbitrage leaves between quoted rates, so it is a spread whose hedge ratio is fixed at one. Nothing is fitted, so the ADF’s bars apply.

On this rate the choice of table decides the verdict. Both statistics the verdict reads, −3.2136 and −2.9946, clear the one-series 5% bar of −2.86. Read against the pair’s 5% bar of −3.34, both would fall short. At the pair’s 10% bar of −3.04 they would split, with the one-lag statistic clearing it and the 10-lag one not. Neither clears the one-series 1% bar of −3.43 either, so “quite stationary” holds at 5% and no stronger.

Two checks, run after the verdict, show what the other choices would have found:

1. **Without the constant**, the test asks whether the rate reverts to exactly 1.00, where its log is zero. The one-lag statistic becomes −2.5159, which clears that row’s 5% bar of −1.94. It clears only because the rate has stayed close to 1.00. Quote the same rate per 100 Canadian dollars and the test with a constant gives −3.2136 again, while the test without one gives −0.2982, nowhere near any bar. A regression with no constant is forced through zero, so on a series that sits far from zero it misses the reversion the test with a constant finds.
2. **With a trend as well**, the test asks whether the rate reverts around a line that drifts. The statistic is −3.2947, which clears that row’s 10% bar of −3.13 and not its 5% bar of −3.41, so a trend term would have reversed the verdict.

![Two horizontal number lines of t-statistics from −4.1 to −2.0. The upper line, for one series tested by an ADF with a constant, has bars at −3.43, −2.86 and −2.57 for 1%, 5% and 10%, with the region past −2.86 shaded. CAD/AUD’s statistics, −3.2136 at one lag and −2.9946 at ten lags, sit inside the shaded region. The lower line, for a fitted pair tested by Engle-Granger, has bars at −3.90, −3.34 and −3.04, with the region past −3.34 shaded. TLT on IEF at −2.3887 and IEF on TLT at −2.3168 sit far outside it, and CAD/AUD’s two statistics, drawn again as hollow marks, sit outside it too.](../docs/figures/stationary_candidates_bars.png)

*The same two CAD/AUD statistics fall inside the one-series 5% region and outside the pair’s. TLT and IEF fall well short of the pair’s bars either way round.*

## Lesson 3: checking for leftover autocorrelation can strengthen a finding, shrink a margin, or reverse a verdict

The ADF’s lags absorb autocorrelation, and any left over means the bars no longer apply. The check from that post asks two things of a fit’s residuals:

1. A Breusch-Godfrey test for autocorrelation over ten lags gives a p-value above 0.10.
2. None of the first ten autocorrelations falls outside a band of ±1.96/√n, where n is the number of observations.

On GLD/GDX’s Chapter 3 window, the first lag count that passed both turned a rejection into no rejection. The two new tests show the other two outcomes.

**On TLT and IEF the check strengthened the finding.** Both one-lag fits fail it, with autocorrelation-test p-values below 0.0001 and autocorrelations outside the band at nearly every lag. The first fits that pass are at 31 lags, whichever fund is regressed on the other, and there the statistics are −1.5677 and −1.5387, further from rejecting than at one lag.

The two halves of the check did different work here. Every autocorrelation is inside the band from 9 lags for TLT on IEF and from 10 for IEF on TLT, and every fit from there to 30 lags still fails the autocorrelation test. A check that read only the band would have stopped 22 and 21 lag counts early, at statistics nearer rejection.

**On CAD/AUD the check shrank the margin without turning the verdict.** The one-lag fit fails, with a p-value of 0.0002 and autocorrelations at lags 2, 6, 7 and 10 outside the band. The first passing fit is at 10 lags, with a p-value of 0.6487, and its statistic of −2.9946 still clears −2.86. Every lag count from 0 to 32 rejects at 5%, the closest being 6 lags at −2.8739, so here the lag count could not have decided the verdict.

The search for a passing lag count needs a ceiling, or it becomes a hunt for the lag count that gives the wanted answer. Schwert’s rule, 12·(n/100)^(1/4), rounded up the way the statsmodels library rounds it, sets the ceiling from the sample size before any statistic is read. It gives 34 lags at TLT and IEF’s 6,083 days, 32 at the rate’s 4,984 and 33 at GLD/GDX’s 5,099. Long histories push the ceiling up, and on the bond pair the first pass landed close to it.

![Two panels of ADF t-statistics against the lag count, with one dot per lag count. The upper panel shows CAD/AUD at every count from 0 to 32, all below the 5% bar of −2.86. Its dots are hollow from 0 to 9 lags, where the residuals fail the check, and the first filled dot is at 10 lags, at −2.9946. Three more are hollow, at 23 to 25 lags. The lower panel shows TLT regressed on IEF and IEF regressed on TLT at every count from 0 to 34, against the pair’s bars of −3.04 and −3.34. No count reaches the 10% bar. Their dots stay hollow until 31 lags, where the statistics are −1.5677 and −1.5387, higher than at one lag.](../docs/figures/stationary_candidates_lags.png)

*Filled dots are fits whose residuals pass the check. On CAD/AUD the first one still clears the 5% bar. On TLT and IEF they sit further from the bars than the one-lag fits do.*

## Lesson 4: a rate that tests stationary over nineteen years rarely does so within one year

CAD/AUD’s half-life is 141.6 trading days, so a gap from its average takes a little over half a year to close halfway. Over the whole test period the test rejects. In a rolling scan of 226 one-year windows, stepped a month at a time, only 23 reject at 10% and 5 at 5%.

The other two scans show the same gap from the other side. TLT and IEF never reject over their whole history, yet 56 of their 278 one-year windows clear 10% with TLT regressed on IEF, and 51 with IEF on TLT. Just over half of those end in 2003-04 or 2020-21. GLD/GDX fails over 2006 to 2026 on dividend-adjusted closes, at −1.45 with a half-life of 833.5 days, while 31 of its 231 one-year windows on raw closes clear 10%. How often one-year windows reject says little about the whole span, in either direction.

![Two panels of one-year rolling t-statistics, plotted against the date each window ends, with a dot on each window past the 10% bar. The upper panel shows CAD/AUD from 2008 to 2026 against the one-series bars of −2.57 at 10% and −2.86 at 5%. Over the whole test period its test rejects at 5%, with t = −3.2136, yet only 23 of its 226 windows clear 10%. The lower panel shows TLT regressed on IEF and IEF regressed on TLT from 2003 to 2026 against the pair’s bars of −3.04 and −3.34. Over the whole period the pair does not reject even at 10%, at −2.3887 and −2.3168, yet 56 and 51 of its 278 windows clear 10%, and just over half of those end in 2003-04 or 2020-21.](../docs/figures/stationary_candidates_windows.png)

*Dots mark the windows past the 10% bar. For CAD/AUD the test rejects over the whole test period and in few one-year windows. For TLT and IEF it rejects in more windows and never over the whole period.*

None of those windows is a finding. A scan describes the span it covers, and a window that happens to reject is one of many looks at the same data.

A year is also short for a reversion this slow, since a 252-day window holds about 1.78 half-lives. A simulation measured how much that costs, on a specification written down before any number was computed. It generated 1,000 series that truly revert with a 141.6-day half-life, each as long as the rate’s test period, and ran the rate’s scan on every one. It reported three things:

1. **One-year windows rarely reject.** On average 27.0 of the 226 windows cleared 10%, or 12.0%, and 388 of the 1,000 series had 23 or fewer, as CAD/AUD does.
2. **The whole period almost always rejects.** The same test over each whole series rejected at 5% in 968 of the 1,000.
3. **The 5% bar shows the same.** The simulated series cleared 5% in 14.0 windows on average.

A series that does not revert at all clears the 10% bar in about one window in ten, because that is what a 10% bar means. A series that certainly reverts at CAD/AUD’s speed clears it in 12.0%. So a year of data barely separates the two, and only the whole period does. CAD/AUD’s 23 windows fit either kind of series, and its whole-period rejection is the evidence that it reverts.

One number was added after the results were seen rather than declared before, and it cuts the other way: only 73 of the 1,000 simulated series cleared 5% in 5 or fewer windows, as CAD/AUD does. The model has neither the rate’s fat tails nor its changing volatility, and a half-life estimated from 4,984 days tends to read short, so the rate may revert more slowly than 141.6 days suggests. The simulation shows that a slowly reverting series can reject in this few windows. It does not show why the rate’s windows reject so rarely.

## Lesson 5: each choice that could turn the answer was fixed in advance or checked both ways

A free choice can steer a test, so the repository wrote each one down before computing the statistic it could move, or reported the result both ways.

1. **Which leg depends on which.** Engle-Granger regresses one price on the other, the answer depends on the order, and Chan names no order. So the repository reports both, TLT regressed on IEF and IEF on TLT. They sit 0.0719 apart, so the choice could not have turned this finding.
2. **Which way the rate is quoted.** On the log the direction makes no difference, as the settings above say. On the rate itself the two directions differ. Quoted as the vendor quotes it, in Australian dollars per Canadian dollar, the statistic is −3.2944 at one lag and −3.0241 at 10 lags. Quoted the other way it is −3.1552 and −2.9734. All four reject at 5%, so taking the log decided nothing either.
3. **The constant, and no trend.** Both were written down before any statistic was computed. A check run afterwards, in Lesson 2, found that a trend would have reversed the verdict, so this choice could have turned the answer.
4. **The lag.** Both candidates use one lag, and the autocorrelation check runs beside it rather than replacing it. On the rate, Lesson 3 showed that every other lag count up to the ceiling rejects too.
5. **The start date.** The command that runs either test accepts no window, so nobody can keep trying periods until one rejects. The repository set the cross rate’s start on the first day after the vendor’s gap. That came after the download, since only the download could show the gap, and before any statistic was computed.

## What this replication cannot say

The two results cover two series over two spans. Four questions are beyond them.

1. **Whether trading the rate pays.** Stationarity is a property of the series. A trade adds costs, the carry from two interest rates, and the problem of sizing a position against a half-life of 141.6 trading days. The repository tests none of them.
2. **Whether individual bonds, or the yields behind them, behave like the funds.** A fund rolls its holdings to stay near one maturity. Treasury futures and individual bonds both need data the repository does not hold, and a yield cannot be bought or sold, so testing yields would be a different claim.
3. **Whether the rate behaved the same before August 2007.** The repository keeps the history before the vendor’s gap, a little under two years of it, and does not test it.
4. **Whether either result survives another download.** Raw closes change only when a fund splits, and a currency rate has no corporate actions, but a vendor can still fill or change its history. A test already fails if a new download fills the 2007 gap, so the start date cannot move quietly.

## What this means for a trader

Five habits follow from the lessons above.

1. **Name the table before reading the statistic.** The same −3.2136 clears one bar and falls short of another, and −2.57 means two different things in two rows.
2. **Ask whether the hedge ratio was fixed or fitted.** A fitted ratio earns a stricter bar. A spread whose ratio is fixed in advance, like a cross rate, does not.
3. **Check the residuals before trusting the statistic.** The check can reverse a verdict, shrink its margin or strengthen a finding, and a statistic from a fit that fails it is read against bars that do not apply.
4. **Keep the span and the window apart.** A verdict over nineteen years says little about any one year, and a run of rejecting years says little about the whole.
5. **Close the free choices before computing.** Which leg, which quote, whether to fit a constant or a trend, which lag and which start date can each move a statistic across a bar, and a choice made after seeing the number is a search.

On a modern download, Chan’s currency rate holds at 5%, the bond funds show no evidence of cointegrating, and his calendar spreads hold for natural gas and not for gasoline.

## References

- Breusch, T. S. (1978). Testing for autocorrelation in dynamic linear models. *Australian Economic Papers*, 17(31), 334–355.
- Chan, E. P. (2021). *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* (2nd ed.). Wiley.
- Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. *Econometrica*, 55(2), 251–276.
- Godfrey, L. G. (1978). Testing against general autoregressive and moving average error models when the regressors include lagged dependent variables. *Econometrica*, 46(6), 1293–1301.
- MacKinnon, J. G. (2010). *Critical values for cointegration tests*. Queen’s Economics Department Working Paper No. 1227.
- Schwert, G. W. (1989). Tests for unit roots: A Monte Carlo investigation. *Journal of Business & Economic Statistics*, 7(2), 147–159.

*Not investment advice. Code: [the tests](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates.py) and [the charts](https://github.com/l3a0/quantitative-trading/blob/main/src/chan/stationary_candidates_figures.py), with the checks behind [the tests’ numbers](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates.py) and [what the charts draw](https://github.com/l3a0/quantitative-trading/blob/main/tests/test_stationary_candidates_figures.py), and the replication log’s entries for [the bond pair](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-5-the-fixed-income-candidate-chans-quantitative-trading), [the rate](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-6-the-cadaud-cross-rate-chans-quantitative-trading) and [the calendar spreads](https://github.com/l3a0/quantitative-trading/blob/main/docs/replication-log.md#entry-15-calendar-spreads-chans-quantitative-trading).*
