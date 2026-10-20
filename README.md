# quantitative-trading

Experiments and replications from Ernest Chan's quantitative trading books,
each one pinned to the data vintage it ran on, or saying it has none.

## Why the vintage comes first

Vendors restate price history. An adjusted close is not a property of a trading
day. It is a function of the day the series was downloaded, because the series
is pinned to the latest price and every later split or dividend rescales the
history behind it. Run the same code against a symbol that has paid a dividend
since the last download and the numbers move, with nothing in the code or the
output saying why. A symbol that has paid nothing comes back unchanged, which
is what makes the problem easy to miss.

So a result computed from a series is committed next to the exact series it was
computed from, and a result computed from none says so. Licensed data is the
one exception. Example 7.1's two series of minute bars, and Alpha Vantage's
daily closes for the S&P 600, S&P 500 and S&P 400 cross-sections, stay in the owner's data archive
and only their hashes are committed, as `docs/design.md`'s premise records.
Alpha Vantage's USD/CAD daily closes are committed after all, by the owner's
ruling on [issue 607](https://github.com/l3a0/quantitative-trading/issues/607),
so CI runs their pins. Everything else is
regenerable. Rerun the analysis and it comes back. Lose the
vintage and the number becomes an assertion nobody can check, including its
author.

[docs/design.md](docs/design.md) carries the reasoning. The
[tracker](https://github.com/l3a0/quantitative-trading/issues) carries the
order, because an issue and a document describing the same plan drift and only
one of them can be authoritative.

## What a replication is here

A record, not a script. It carries five things.

1. The source and the published figure, at the precision the source uses.
2. The vintage each number was computed from.
3. What this repo computed.
4. The gap, at the precision both numbers support.
5. The verdict, with the reason.

A gap is a result. A number that fails to reproduce says something about the
method's sensitivity, and that is worth more than a match nobody examined.

[docs/replication-log.md](docs/replication-log.md) is where those records live.
It also carries the rule it uses to pick between the three verdicts, which the
vocabulary defines without saying how to choose.

A replication against data is exploratory by construction. Reproducing a
published figure spends the sample on a hypothesis someone else chose, so it
can say whether the number reproduces and nothing more. A replication that
spends no sample is outside that label and its opposite both, which the
coin-flip entry says in place of picking one.

## Status

Forty-seven replications run here, eighteen from Chan's *Quantitative Trading*
and twenty-nine from his *Algorithmic Trading*. The first two were ported from the
sibling [trading-strategies](https://github.com/l3a0/trading-strategies) repo,
where they were first built. The other forty-five were built here.

1. The GLD/GDX cointegration example, Chapter 3 and Chapter 7.
2. The KO/PEP counter-example, Example 7.3, which is a pair that correlates in
   returns yet does not cointegrate in levels.
3. The coin-flip gamble, Box 6.1, where the expected return of a round is
   positive and the growth rate of capital is negative. It reads nothing at
   all, so it has no vintage to name. The survivorship toy, item 9, has none
   either, because it reads tables the book prints. Neither do the leverage
   examples, item 20, which work arithmetic on inputs the book states.
4. The Kelly leverage on SPY, Example 6.2, which asks how much leverage
   maximises compounded growth and then whether that much would have survived
   the worst day the index has had. Most of the levels Chan computed from a
   series land high on a modern download, and the standard deviation
   reproduces at the two decimals he printed. Every claim behind those numbers
   but one still holds, and the entry is about that split. The exception is
   Chan's claim that the Kelly leverage, unlike the Sharpe ratio, does not
   depend on the time scale. Rows 15 and 28 of the entry record it as
   `did not reproduce`, on the 2026 download and on his own workbook alike, so
   its failure owes nothing to the download. On his own workbook every level he
   computed from a series reproduces at the precision he printed, and setting the two
   series day by day against each other puts the whole gap on about ten days
   on or beside SPY's quarterly ex-dividend dates.
5. Edward Qian's risk parity against the classic 60/40, reported at Kindle
   location 4684, on SPY and AGG. Both figures Chan prints land close and the
   claim behind them does not survive: 60/40 earns the higher Sharpe ratio at
   matched risk on the full span at Chan's 4 percent rate, resolved at a robust
   t of −2.17. It is the first entry here where the numbers reproduce and the
   central claim does not, which is the reverse of the split the GLD/GDX and Kelly
   entries both found. Swapping SPY for IWB, which tracks the Russell 1000
   index Qian read, moves no verdict on any of the three windows. That swap is
   a measurement beside the replication rather than a replication, because
   the book prints no IWB figure.
6. The CAD/AUD cross rate, which Chan calls "quite stationary" at Kindle
   location 3951 without working it. He names the rate itself, so the claim is
   what gets pinned and it carries a verdict against a criterion fixed before
   any statistic was read. On `CADAUD=X` over 2007-08-06 to 2026-09-30 the log
   of the rate rejects a unit root at 5%, at −3.2136 at one lag and −2.9946 at
   the first lag count whose residuals pass, against a bar of −2.86, so the
   claim reproduces. Its half-life is 141.6 trading days, and only 23 of 226
   one-year windows reject at 10%.
7. The equity seasonals, Examples 7.6 and 7.7, which Chan publishes as already
   dead: the January effect on his S&P 600 file and Heston and Sadka's
   year-on-year rotation on his S&P 500 file. He prints them in the first
   edition's MATLAB and in the revised edition's MATLAB, Python and R, and all
   seventeen figures his files reach reproduce to the digits printed. None
   lands from the strategy as described. The revised MATLAB and R rules follow
   the code the book prints, with one index repaired so the MATLAB runs. A
   repost of the revised code carries the same repair and book two's
   `smartstd`, which is the helper the printed digits need.
   The first edition's −0.9167 a year is a sum over positions rather than a
   return on capital, and the revised edition's three annual returns land
   between −0.0114 and −0.0129 a year. Example 7.6's third January, the one
   that made money, reproduces as 0.0881 and 0.088486 on the later save of
   the S&P 600 file that Chan's script loads, committed from a repost of the
   revised edition's code. Chan's p. 180 claim that the most recent five years
   of his S&P 500 file do even worse holds under a criterion written before
   the check ran: −0.0165 a year against −0.0129. The gap is far inside the
   noise of 47 months, so the verdict is about his file of survivors rather
   than about whether the effect weakened. Example 7.6 also runs from January
   2009 to January 2026 on the 603 companies IJR held at 2025-12-31, on Alpha
   Vantage closes kept in the owner's archive. Those rows are survivor-only
   and exploratory, and read in one direction only, because the companies
   that left the index are missing and both legs gain from their absence. The
   mean January before costs is 0.0108, with a one-sided p of 0.132, so no
   January effect is detectable above about 2.4% a January, on members that
   favour the effect. The same rules then ran on the members IJR held at each
   year-end from 2008 to 2025, which keeps the companies that left. That run
   is registered, because its criterion was written before any return was
   computed. Every year-end has members with no checked price that could
   change a tenth, so every January is bounded. The low series averages
   −0.1047 a January before costs with a one-sided p of 1.000, and the high
   series 0.0879 with a p of 0.001. Leaving out every member with no checked
   price averages −0.0083, between the two, described rather than tested. The two series
   disagree, so the free sources cannot decide whether the January effect
   survived the book, and
   [issue 407](https://github.com/l3a0/quantitative-trading/issues/407) asks
   whether to buy prices for the members that threaten a tenth. Example 7.7
   then ran under the revised MATLAB's rules on the members IVV held each
   month from January 2009 to September 2026, carried forward from its
   quarterly schedules. That run is registered too. Its 213 months average
   −0.0001 a month before costs, with a one-sided p of 0.539, so no return is
   detectable above about 4.2% a year. The verdict reads only the 98,321 of
   107,115 member-months with a checked price, and it leaves out costs and
   the return a failing stock takes when it leaves. Entry 52 sets both of
   Example 7.7's runs beside the Open Source Asset Pricing project's
   `MomSeasonShort`, Heston and Sadka's signal rebuilt from CRSP, which holds
   the companies that later left. That series averages 0.0136 a month over
   their 1965 to 2002 sample, with a t of 8.63, and 0.0012 a month from 2002,
   with a t of 0.50. It correlates at 0.592 with the IVV run. The comparison
   is exploratory and reaches no verdict.
8. Khandani and Lo's linear reversal, Example 3.7, which buys yesterday's
   losers against the market and shorts its winners. On Chan's own S&P 500
   file over 2006 it gives a Sharpe ratio of 0.2510 before costs and −3.1884
   after 5 basis points a trade, against his printed 0.25 and −3.19, so both
   reproduce. The second lands only because two quirks of his code are kept.
   His script never charges the first day's rebalance, which leaves that day's
   profit missing, and his standard deviation counts the missing day as 0
   while his mean skips it. Removing both gives −3.2337. The file holds only
   the stocks still in the index on 2007-11-23, so every figure is about
   survivors.
9. Chan's toy strategy for survivorship bias, Example 3.3 in the revised
   edition, which buys the ten cheapest of the 1,000 largest stocks and holds
   them for 2001. It runs on the two tables of picks the book prints, one from
   a survivorship-free database and one from a database holding only
   survivors. Equal capital reproduces Chan's −42 and 388 percent as −41.72 and
   387.88. Neoforma's 10-K shows that NEOF's row spans a 1-for-10 reverse
   split, and with NEOF on one share basis the survivor-only return is 100.91
   percent. The loss against a gain survives that correction, and the printed
   388 still reproduces from the table as printed.
10. The same reversal updated at the open instead of the close, Example 3.8 in
    the revised edition, where the book says both Sharpe ratios turn "very
    positive". On the rule the book describes it earns 4.4202 before costs and
    0.7834 after, so the claim does not hold at the line of 1.0 declared before
    the run. Chan's own Python notebook computes a different rule and prints
    2.3818 and 1.3997, which reproduce. The notebook fills each gap with the
    last price, so it reads WYN's change of company as a one-day return of
    121.5 on the closes and 127.65 on the opens, and on Example 3.7 it prints
    0.9578 rather than the book's 0.25. Every figure is exploratory and about
    survivors.
11. Chan's two commodity seasonal trades, which he says still pay where the
    equity ones have died: the May gasoline contract from April 13 to April 25,
    and the June natural gas contract from February 25 to April 15. On EIA's
    NYMEX settlements, natural gas is profitable in every year from 1995 to
    2008, which reproduces both the main text's 13 consecutive years and the
    sidebar's 14, read as first-edition figures counted from 1995. Gasoline from 1995 to 2015 holds the 2 losing years that
    Chan's 19 of 21 allows, and shows 16 profitable rather than 19, because
    EIA's file has no row on the trade date in 1997, 1998 or 1999. Both trades
    win fewer years after the years he read. Every figure is exploratory.
12. Post-earnings announcement drift, Example 7.2 of *Algorithmic Trading*,
    which buys or shorts a stock at the open after an earnings announcement
    when the overnight gap is large, and sells at the close. On Chan's own
    S&P 500 file and earnings flags it reproduces every figure his script
    prints: an arithmetic annual return of 0.066743, which is the book's "APR"
    of 6.7 percent, a Sharpe ratio of 1.4909, a compounded APR of 0.067952,
    a deepest drawdown of −0.026052, and a longest drawdown of 109 days. Book
    two's `smartstd` is what lands the first of those. The first edition's, which
    shares its name, gives 0.066833 and misses Chan's printed digit. Every
    figure is exploratory and about survivors.
13. The PCA factor model, Example 7.4, which takes five statistical factors
    from a year of returns on Chan's S&P 600 file, buys the 50 stocks they
    rank highest and shorts the 50 lowest. Chan reports 2 percent a year in
    MATLAB and 4 percent in Python and R, and calls the difference round-off.
    The first edition's MATLAB, the revised MATLAB and the revised Python
    reproduce every figure they print, the Python's 17-digit figures within
    1e-15. The R block prints the Python's figures and its own code reads
    differently. The round-off account does not hold. The Python's regression
    carries an intercept, which cancels its factors, so it ranks on a year of
    momentum. Given the same 50 longs, its book matches the revised MATLAB's on
    none of 752 days. Every figure is exploratory and about survivors.
14. The market and momentum factors, built on Chan's S&P 500 file to test his
    claim at Kindle location 4014 of the revised edition that factor returns
    "often" have stronger serial autocorrelation than single stocks', so they
    have momentum. MKT is SPY's monthly return over the three-month bill, and
    WML longs the stocks whose past eleven months, skipping the latest, rose
    and shorts those that fell. Over the 83 months from December 2000 to
    October 2007, MKT's lag-1 autocorrelation is 0.0675 and WML's is −0.1099,
    against a median of −0.0392 across the 446 stocks priced in every month.
    The claim holds for MKT and does not hold for WML, which is below 0 and
    below the median stock. Neither factor's estimate is outside the 0.2151
    band that a series with no autocorrelation stays inside 95 percent of the
    time, so MKT's verdict could be noise. Every figure is exploratory, and WML
    and the stocks' figures are about survivors.
15. Chan's calendar spreads, which he calls "the simplest examples of
    cointegrating futures pairs" at Kindle location 3951. Every adjacent pair
    of delivery months is tested on EIA's nearest four contracts, 360 for
    natural gas and 220 for RBOB gasoline, over the 39 to 59 days a pair keeps.
    A pair rejects when Engle-Granger clears the 10% bar in both orientations.
    Each commodity is judged as one batch against the 975th of 1,000 shares
    from simulated contracts that do not cointegrate. Natural gas reproduces,
    with 57 of 360 pairs against a bar of 47. RBOB does not, with 14 of 220
    against a bar of 31. Those bars come from a null corrected after the result
    was seen, on the owner's ruling, so that simulated neighbouring contracts
    move together as closely as the real ones do. The null declared before any
    statistic made every contract independent, gave bars of 19 and 13, and
    passed both. Every figure is exploratory.
16. Conditional Parameter Optimization, Example 7.1 of the revised edition,
    where a model re-chooses a GLD strategy's three parameters every day from
    the 400 in its grid. It reads Alpha Vantage's one-minute GLD and GDX bars
    from the owner's data archive, because the vendor's terms grant personal,
    non-commercial use and the repo does not republish them, so its pins run
    only where that archive is. Neither of Chan's columns reproduces. Holding
    the parameters the train years chose earns a test Sharpe ratio of 5.700
    against his 1.947, on a cell that trades 46.7 round trips a day.
    Re-choosing daily wins on the Calmar ratio alone, so his claim that it
    improves every metric does not hold. At 1 basis point a round trip both
    arms lose money. Every reading the book left open was declared on the issue
    before any return was computed. The first run broke one of them, by keeping
    extended-hours bars on early-close days, and the entry reports both runs.
    Every figure is exploratory.
17. Cross-sectional momentum, Example 6.2 of *Algorithmic Trading*, which buys
    the 50 stocks with the highest 252-day return, shorts the 50 with the
    lowest, and holds each day's picks for 25 days. The script's closing
    comment prints a Sharpe ratio of 0.40 against the book's 4.1. Transcribed
    and run on the S&P 500 file it loads, the script prints none of its
    comment's five figures. It gives a Sharpe ratio of 4.0657, and compounded
    APRs of 0.372577 for 2007 and −0.298789 for 2008 and 2009, which round to
    the book's 4.1, 37 percent and −30 percent. The rule declared before the
    run read the book's "APR" as the arithmetic return, as Example 7.2's is,
    and that gives 32 and −32 percent. So under the declared rule no book
    figure reproduces, and the compounded match is reported as found
    afterwards. None of the four readings declared to explain the gap lands.
    Every figure is exploratory and about survivors.
18. Buy on gap, Example 4.1 of *Algorithmic Trading*, which buys at the open
    the ten stocks that opened furthest below their previous day's low, while
    still above their 20-day moving average, and sells at the close. On Chan's
    own S&P 500 file both figures his script prints reproduce: an APR of
    0.087385, his 8.7 percent, and a Sharpe ratio of 1.5371, his 1.5. Book
    two's `smartstd` is what lands them, and the first edition's moves both.
    The book's short-on-gap mirror has no script, so its rule was declared on
    the issue before any run. It earns 0.122030 and 1.7853 against Chan's 46
    percent and 1.27, and does not reproduce, though its drawdown is the
    steeper as he says. Every figure is exploratory and about survivors.
19. Khandani and Lo's reversal again, as *Algorithmic Trading*'s Examples 4.3
    and 4.4 run it on Chan's 2012 S&P 500 file over 2007 to 2011. Book two
    changes the rule as well as the data: it scales each day's weights to a
    gross of 1, leaves a missing price's weight missing, charges no cost, and
    cuts the window before taking returns. Example 4.3 holds the weights from
    close to close, and Example 4.4 trades
    from the open to the same day's close on the overnight gap. Every figure
    Chan prints reproduces: an APR of 13.68 percent and a Sharpe ratio of
    1.2595 against his 13.7 and 1.3, 30.16 percent in 2008 and 10.58 in 2011
    against his 30 and 11, and 0.731553 and 4.713284 for Example 4.4, the six
    decimals his script printed. The first book's rule on the same panel and
    window earns 1.2219 before costs, so most of the distance from that book's
    0.25 is the data and the window rather than the rule, and 5 basis points a
    side take it to 0.3797. The data include a longer survivor horizon, which
    nothing here prices. Every figure is exploratory and about survivors.
20. Constant leverage and capped Kelly allocation, Examples 8.1 and 8.2 of
    *Algorithmic Trading*, which are arithmetic on inputs the book states.
    Holding leverage 5 sells \$40K into a \$10K loss and buys \$80K into a
    \$20K gain, exactly as printed. Under a cap of 2 on two strategies whose
    Kelly leverages are 4.4 and 4.9, scaling both down to 0.95 and 1.05 grows
    at 0.82, and putting the whole cap on the second grows at 0.955, which the
    book prints as 0.96. Every printed figure lands. The 0.96 lands only by
    rounding an exact tie up, so the run prints three decimals.
21. Price spread, log price spread and ratio, Example 3.1 of *Algorithmic
    Trading*, which trades GLD against USO by holding minus the 20-day
    z-score of a signal in units of the pair, with the hedge ratio refitted
    every day over the last 20. On Chan's own ETF file the price spread and
    the log price spread reproduce all four figures their scripts print, to six
    decimals: an APR of 0.108335 and a Sharpe ratio of 0.589651, then 0.088863
    and 0.504153. The book calls the first "about 10.9 percent", which is not
    0.108335 rounded. The ratio's script as published gives −0.134608 and
    −0.702522 and misses its comment's −0.141522 and −0.746663. The same
    script with GLD and USO swapped lands both, a reading found after the miss.
    Chan's claim that the ratio loses money holds either way. Every figure is
    exploratory.
22. Four tests for mean reversion on USD.CAD and the trade they set, Examples
    2.1 to 2.5 of *Algorithmic Trading*, on Chan's own minute file read at
    16:59 each day. Every figure his script prints lands every digit: the ADF
    statistic −1.840744 with its AR(1) estimate and critical values, the
    variance ratio test's p-value of 0.367281, and the half-life of 115.209794
    days. The ADF figure needs jplv7's regression, which fits one row fewer
    than `adfuller`, whose −1.843018 misses. The Hurst exponent does not land:
    0.4732 against the book's 0.49, and Chan's own Python port gives 0.4758.
    Neither can be told apart from a random walk of the same length. Starting
    the sample one day later moves `genhurst` to 0.4891, which prints as 0.49,
    but the script's other figures place its own run at the first close.
    Example 2.5's P&L ends positive at
    0.1141, which is the claim the issue declared before any P&L was
    computed. On the way it falls 0.6425 from a high of 0.1321. Its lookback comes from the closes it trades,
    as the book says. Every figure is exploratory.
23. The cointegration tests and mean-reverting portfolio of *Algorithmic
    Trading*'s Examples 2.6 to 2.8, on the ETFs EWA, EWC and IGE in Chan's own
    ETF file. Every figure `cointegrationTests.m` prints reproduces to its last
    digit, the eigenvectors up to their sign: a CADF statistic of −3.64346635,
    every Johansen statistic and eigenvalue, a half-life of 22.662578 days, and
    an APR of 0.125739 with a Sharpe ratio of 1.391310, his 12.6 percent and
    1.4. The Johansen test is statsmodels' `coint_johansen`, which carries the
    critical-value tables of the jplv7 function Chan calls and lands its
    output, wrapped once in `chan.johansen` for the three issues that need it
    next. The book's claim
    that both Johansen statistics find three relations for the triplet does
    not reproduce, because the eigen statistic finds none, which the script's
    own printout already shows. Every figure is exploratory, and the
    portfolio's weights are fitted on the days it trades.
24. SPY against the S&P 500 stocks that pass a cointegration screen, Example
    4.2 of *Algorithmic Trading*, on Chan's own 2012 S&P 500 file and his ETF
    file's SPY. `indexArb.m` tests each of 480 stocks against SPY over 2007
    and keeps the 98 that pass a 90 percent bar. That bar passes about 28
    percent of random walks unrelated to SPY, about 135 of 480, so the count
    alone does not show that any stock cointegrates with SPY. It holds them with equal capital against SPY on the basket test's
    first eigenvector and trades from 2008 with a lookback of 5. Every figure
    the script prints reproduces to its last digit: the 98, both Johansen
    statistics for the basket, the eigenvectors with Chan's own signs, and an
    APR of 0.044930 with a Sharpe ratio of 1.319397, his 4.5 percent and 1.3.
    The book's claim that the basket cointegrates with SPY at better than 95
    percent holds for the trace test and not the eigen test. Every figure is
    exploratory and survivor-only, and the lookback was chosen with hindsight,
    so the 2008 to 2012 figures are not out of sample.
25. AUD.USD against CAD.USD with a rolling Johansen hedge, *Algorithmic
    Trading*'s Example 5.1, on the daily closes in Chan's 2018 Python port.
    Every figure `AUDCAD_unequal.m` prints reproduces: an APR of 0.112410 and
    a Sharpe ratio of 1.610890, his 11 percent and 1.6, and a Kelly leverage of
    23.845328. They reproduce because all 612 daily returns match the ones the
    script saved, to within the 1e-9 declared before any return was computed,
    which also shows the port's daily files agree with the inputs his MATLAB
    read, up to a constant scale on each leg. The trace test finds a relation
    in 26 of the 612 training windows, so on most days the rule traded a hedge
    the test did not back. Every figure is
    exploratory, and the 250-day training length was chosen in hindsight.
26. Bollinger bands on GLD and USO, Example 3.2 of *Algorithmic Trading*,
    which trades item 21's price spread with one unit at most, entering when
    the 20-day z-score passes ±1 and exiting when it crosses 0. Both figures
    `bollinger.m` prints reproduce to six decimals on Chan's own file, an APR
    of 0.178249 and a Sharpe ratio of 0.964673, his 17.8 percent and 0.96.
    Both beat the linear rule's 0.108335 and 0.589651, which is the
    improvement the book claims. Unlike item 21, the run depends on the
    moving deviation's divisor: n in place of the script's n − 1 gives
    0.183306 and 0.984872. Every figure is exploratory.
27. The spot and roll returns of *Algorithmic Trading*'s Example 5.3, on
    Chan's own strips of BR, corn, CL, HG and TU. Eight of Table 5.1's ten
    cells reproduce, and HG's and TU's spot returns do not: HG's 0.050567
    rounds to 5.1 percent against the book's 5.0, and TU's 0.000039 is
    positive where the book prints −0.0. Corn's two figures agree with the
    ones Chan's Python port printed to within 10⁻¹². `estimateFuturesReturns.m`
    measures a contract's maturity in columns rather than months, so beside
    the replication runs the same fit in months, and the script's figures
    overstate corn's, HG's and TU's roll returns by 2.4, 2.0 and 3.0 times.
    Under months, HG's falls below its spot return, so the comparison
    Chapter 6 rests its explanation of HG's momentum on holds only under the
    script's arithmetic, and corn's is no longer twice its spot return.
    `chan.roll_returns` exports the strip reader and both fits for later
    experiments to build on, Example 5.4 among them, and the reader also
    takes the VX strip, which has no spot. Every figure is exploratory.
28. VX futures against E-mini S&P 500 futures, from *Algorithmic Trading*'s
    Chapter 5, on Chan's own continuous futures. A regression of ES on VX
    from August 2008 gives the hedge, and a band one training deviation wide
    trades the residual. On the save of 2012-05-07, fitted on the first 500
    days from 2008-08-04, the hedge of 0.390594, the APR of 0.122811 and the
    Sharpe ratio of 1.393201 reproduce the book's 0.3906, 12.3 percent and
    1.4. The residual's deviation of $2,044.91 misses the book's $2,047, and
    dropping the first training day reaches $2,046.93. `VX_ES.m` as it ships
    loads a later save, fits on the test days too and runs no trade. The
    window comes from Chan's `VX_ES_rollreturn.m`, while the save and the exit
    at the opposite band were chosen because they land the book's figures.
    The test holds four positions in 449 days.
    Every figure is exploratory.
29. The Johansen tests on GLD and GDX around July 2008 in *Algorithmic
    Trading*, and on the triplet with the oil fund USO added, on Chan's own
    ETF file. The book prints no statistic, so its three claims were judged on
    each Johansen statistic at 99 percent, with criteria written down before
    any statistic was computed. All six rows hold. The pair finds one
    relation from 2006-05-23 to 2008-07-14 and none from 2008-07-15 to
    2012-04-09, even at 90 percent, and the triplet finds exactly one over the
    whole 1,481 days. The control the book leaves out holds too: GLD and GDX
    alone over the same days find none, at a trace statistic of 10.447
    against a 90 percent bar of 13.429. GDX and USO alone find one relation
    at 99 percent, though, so the triplet's result cannot tell the oil
    hypothesis from a link between the miners and oil alone. Every figure is
    exploratory, and the split date and the third ETF were chosen after the
    break was seen.
30. AUD.CAD with rollover interest, *Algorithmic Trading*'s Example 5.2, on
    the daily closes and monthly interest rates in Chan's 2018 Python port.
    Both figures `AUDCAD_daily.m` prints reproduce to their last digit, an APR
    of 0.061564 and a Sharpe ratio of 0.541802, his 6.2 percent and 0.54, and
    so do the 6.7 percent and 0.58 the book gives without the rollover. The
    book's annualised rollover of "almost 5 percent" does not reproduce. The
    interest differential the book defines comes to 0.032642 a year, while two
    other readings land near 5 percent: the AUD rate alone at 0.046648, and
    the differential annualised over 365 days at 0.047279. Every figure is
    exploratory, and the script triples CAD's rollover on Thursdays where the
    book's own settlement rule says Wednesday.
31. Crude oil reversal joined to momentum, from *Algorithmic Trading*'s
    Chapter 6, on Chan's own continuous futures. The rule buys CL at the
    close when it is below its price 30 trading days ago and above its price
    40 trading days ago, shorts on the mirror, and is flat otherwise. On the
    2012-05-04 save `CL_rev.m` loads, the APR of 0.117600 and the Sharpe
    ratio of 1.100368 match the script's comment to every digit and the
    book's 12 percent and 1.1. Momentum alone gives 0.090228 and 0.439049
    and reversal alone 0.068326 and 0.370289, so on the book's window the
    join beats each rule alone. On the four years before it, read from the
    2012-05-07 save, the join gives 0.021324 and 0.369864 and momentum alone
    beats it, on a series that
    [issue 313](https://github.com/l3a0/quantitative-trading/issues/313)
    found back-adjusted above the traded price. Swapping the two lookbacks
    negates every position. Every figure is exploratory.
32. A Kalman filter hedge ratio on EWA and EWC, from *Algorithmic Trading*'s
    Chapter 3, on Chan's own ETF file. The filter re-estimates the slope and
    intercept of EWC on EWA every day, and the band trades its forecast error
    against the square root of its forecast variance. Both figures
    `KF_beta_EWA_EWC.m` prints reproduce to their last digit, an APR of
    0.262252 and a Sharpe ratio of 2.361162, which the book rounds to 26.2
    percent and 2.4. The script shorts EWC alone on the file's first day,
    while the filter's slope is still 0, and withholding the signal on the
    first two days gives 0.260669 and 2.349460, which round to 26.1 percent
    and 2.3 rather than the book's figures. The book's two claims about
    the filter, a slope that "oscillates around 1" and an intercept that
    "increases monotonically", are carried as findings with no verdict,
    because the only criteria for them were written after a run. The slope's
    median is 1.047367 and its mean 1.089693. The intercept's yearly mean
    rises every year from 0.1440 in 2006 to 6.7748 in 2012, and 513 of its
    1,499 daily steps fall. Every figure is exploratory.
33. Time-series momentum on TU, the two-year Treasury note future, Example
    6.1 of *Algorithmic Trading*, on Chan's own 2012-05-11 continuous futures
    save. Past returns over 250 days correlate with returns over the next 25
    at 0.2719 with a p-value of 0.0238, the book's 0.27 and 0.02, and the
    variance ratio test does not reject a random walk, as the book says. The
    trade goes long when the 250-day return is positive and short when it is
    negative, holding each day's call for 25 days with a twenty-fifth of the
    capital. All six figures `TU_mom.m`'s comment prints reproduce on the full
    2004 to 2012 window: an average annual return of 0.016699, a Sharpe ratio
    of 1.041462, an APR of 0.016708, a maximum drawdown of −0.024847 lasting
    343 days, and a Kelly f of 64.919535. The script's own active line starts
    in 2009 and lands none of them. The Hurst exponent does not reproduce:
    0.433357 against the book's 0.44, through the same `genhurst` that misses
    USD.CAD's 0.49 in item 22. Every figure is exploratory.
34. Mean reversion on crude oil's 12-month calendar spread, Example 5.4 of
    *Algorithmic Trading*, on Chan's own CL strip. The roll return's
    half-life of 36.394034 days is the script's printed figure and rounds to
    the book's 36, and its ADF statistic of −4.727778 clears the 1 percent
    critical value of −3.4583, so the book's "stationary with 99 percent
    probability" holds. Trading the spread on a z-score over that lookback,
    on the script's window from 2008-01-02, gives an APR of 0.082671 and a
    Sharpe ratio of 1.278216, which round to the book's 8.3 percent and 1.3,
    and the drawdown of −0.053222 over 206 days that the script's comment
    prints. The
    comment's APR of 0.083406 and Sharpe ratio of 1.288661 do not reproduce
    on that window, and starting a day later lands both to every digit. The
    book's 61 holding days in place of the script's 63 give 0.067315 and
    1.044327. The spread falls as the roll return rises, so the script's sign
    flip mostly sells the spread when it is low, and reversing it gives an APR
    of −0.080125. Every figure is exploratory.
35. VIX futures calendar spreads traded on the ratio of the back contract to
    the front, from *Algorithmic Trading*'s Chapter 5, on Chan's own VX
    strip, which has no spot column. No script ships under its own name, and
    Example 5.4's script carries a commented-out load of this strip, so the
    specification is that script with the ratio as its signal, a 15-day
    lookback and pairs a month apart, declared before any figure. Its ADF
    statistic of −5.568107 clears the 1 percent critical value of −3.4583,
    so the book's "stationary with a 99 percent probability" holds. Its APR
    of −0.040454 and Sharpe ratio of −0.563912 have the wrong sign against
    the book's 17.7 percent and 1.5. Of four rows declared beside it, B3
    trades the ratio of the pair it holds with each pair held in turn, which
    from 2008-10-27 is every pair from VX-2008X's to VX-2012K's. On the
    book's window to 2012-04-23 it gives 0.176952 and 1.475658, which round
    to the book's 17.7 percent and 1.5, and it alone does worse before
    October 2008, as the book says. Its last pair ends on the book's end
    date, but so does the row that holds pairs the same way on the
    specification's signal, so the date does not single it out. B3 was picked
    out after the run, so its match is a search. The specification's near
    leg is the front contract on 126 of its 847 held rows, so its signal
    mostly reads a pair it does not hold. Every figure is exploratory.
36. TU momentum traded on the lagged roll return, location 2690 of
    *Algorithmic Trading*, on Chan's 2012-08-13 TU strip. The rule goes long
    when item 27's roll return is above 3 percent and short when it is below
    −3 percent, and holds the front contract, rebuilt from the strip because
    no committed continuous save covers the whole of the book's 2009 to 2012
    window. It misses all three printed figures, with an APR of 0.013725, a
    Sharpe ratio of 1.803348 and a maximum drawdown of −0.007299 against the
    book's 2.5 percent, 2.1 and 1.1 percent. It beats Example 6.1's rule on all
    three when both run on the same series, which is the claim the book's
    "higher" and "reduced" make, though its APR leads by only 0.000348.
    The rebuild agrees with Chan's 2012-05-11 save at a return correlation
    of 0.998359. The rule was declared after about 90 scratch readings, a
    count from the issue's disclosure that no test pins, and the module says
    so. Every figure is exploratory.
37. Three hypothesis tests on item 33's TU momentum, Example 1.1 of
    *Algorithmic Trading*, on the same 2012-05-11 save. The Gaussian
    statistic of 2.933253 is the script's 2.93. Rerunning the strategy on
    10,000 simulated return series with TU's first four moments, drawn from
    Pearson type IV, gives 1,221 at or above the observed mean, inside two
    standard errors of the book's 1,166 and far from the script's printed
    0.027500. Shuffling the entry days gives 0 of 100,000, as the book says,
    though the script as written cannot give anything else, because it adds
    the shuffled positions to the observed ones. Two of three rows added
    after a scratch run saw results point at TU's drift rather than its
    kurtosis: a normal draw gives 1,165 of 10,000, and the type IV draws with
    the mean set to zero give 19. Every figure is exploratory.
38. Long GLD and short gold futures, locations 2718 and 2730 of
    *Algorithmic Trading*, on Chan's GC series and his book-two ETF file.
    `GLD_GC.m` holds the pair every day over the 752 days both calendars
    share, and every figure lands on the printed digits: an average annual
    return of 0.019014, a Sharpe ratio of −0.066564, an APR of 0.019084, a
    maximum drawdown of −0.0082465 lasting 91 days, and the text's 1.9 and
    0.8 percent. The book says GLD's financing cost eats the return. The
    three-month bill rate over the window averages 0.010141, which leaves
    +0.008874 above it, and the bill rate is a floor on that cost, so the
    claim is neither confirmed nor refuted. The GC file is read within
    minutes of GLD's 4 p.m. close rather than at the 1:30 p.m. settlement
    the book describes. It holds 9 US exchange holidays, so it is not a
    settlement series, and its ratio to GLD barely moves from one day to the
    next, which a gap of two and a half hours between the closes would not
    allow. The negative Sharpe ratio comes from the script's constant 2
    percent, which is more than the return, and at the window's bill rate the
    Sharpe ratio is 0.599257. Every figure is exploratory.
39. XLE, the energy producers' ETF, held against USO, the crude oil futures
    ETF, in whichever direction crude's roll return favours, location 2734 of
    *Algorithmic Trading*, on Chan's own ETF file and his 2012-05-02 CL strip.
    The trade is short USO and long XLE when the back contract is priced above
    the front, which is contango, and the reverse when it is priced below.
    All five figures `XLE_CL_rollReturn.m`'s comment prints reproduce: an
    average annual return of 0.159231, a Sharpe ratio of 1.046596, an APR of
    0.159102, and a maximum drawdown of −0.192321 lasting 487 days. The APR
    and the Sharpe ratio round to the book's 16 percent and "about 1". The
    strip's first front window opens on 2006-10-20, so the window's first 123
    days hold nothing. The ETF file subtracts dividends in dollars, so the
    returns are not what a holder of XLE earned. The 244 days earning on
    backwardation hold 0.308117 of the trade's summed daily return of
    0.946538, and on them USO rose 0.5323 in log terms while the ratio
    implies a roll return of 0.072380. Every figure is exploratory.
40. The opening gap strategy on FSTX, the STOXX Europe 50 index future on
    Eurex, which the book calls the Dow Jones STOXX 50. It is Example 7.1 of
    *Algorithmic Trading*, run on Chan's 2012-05-17 save. A day is
    long when the open clears the previous high by a tenth of the 90-day
    standard deviation of daily returns and short when it clears the previous
    low, held from the open to the close. `gapFutures_FSTX.m`'s return line
    as written earns a long's fall from the open, which fades the jump. It
    gives an APR of 0.132733 and a Sharpe ratio of 1.441620, which print as
    the script's 0.1327 and 1.44 and round to the book's 13 percent and 1.4.
    The momentum sign the text describes gives −0.124236 and −1.441620, so the
    claim the figures were printed for does not reproduce. Chan's Python port
    flips the short test and so is never long, and its rule lands the port's
    printed APR of 0.074864 and Sharpe ratio of 0.494857. The 278 long days
    hold 0.749529 of the summed daily return of 1.020809, and on them FSTX
    fell 0.002696 from the open on average. Every figure is exploratory.
41. VX futures against E-mini S&P 500 futures on VX's roll return, after
    Simon and Campasano, locations 2747 to 2754 of *Algorithmic Trading*, on
    Chan's own VX strip, his `VIX.csv` and the ES of his 2012-05-07 save. The
    trade is short the front VX contract and ES when the front sits above VIX
    by more than 0.1 point per trading day to settlement, and long both when
    it sits below by that much. `VX_ES_rollreturn.m` carries two rules, and
    all eight figures its comments print reproduce at the precision printed,
    the APRs, Sharpe ratios and maximum drawdowns to six decimals and the two
    day counts exactly. With 0.3906 VX contracts per ES contract, the
    commented rule, the APR is 0.069065, the Sharpe ratio 1.002020, and the maximum drawdown −0.075683
    lasting 259 days. Those round to the book's 6.9 percent and Sharpe ratio
    of 1. With one VX contract per ES contract, the rule the script ships,
    they are 0.293906, 3.263952, −0.035798 and 59 days. Trading the fitted
    0.390594 misses the APR and the Sharpe ratio at their sixth decimal, so
    the script traded the printed 0.3906. An entry from flat pays no cost,
    as in the script. Measured after the run, the 0.3906 hedge leaves the VX
    leg a median 0.119966 of the gross, and the ES leg gives back 0.159336 of
    the 0.285954 the VX leg earns. Every figure is exploratory.
42. Example 7.4's own five factors, tested on Chan's S&P 600 file against the
    claim at Kindle location 4014 of the revised edition that factor returns
    "often" have stronger serial autocorrelation than single stocks', which
    location 4051 says the example rests on. Each day's factor return is
    paired with the next day's on that day's decomposition, whose signs are
    arbitrary, and the statistic is the correlation of the pairs without
    subtracting their means, which a flipped sign cannot move. Over 752 pairs
    from 2005-01-18 to 2008-01-11, the statistics of PC1 to PC5 are 0.0316,
    0.0778, −0.0189, 0.0305 and 0.0710, against a median of −0.0283 across
    the 579 stocks priced on every day the pairs read. The claim holds for
    PC1, PC2, PC4 and PC5, and does not hold for PC3, which is above the
    median stock but below 0. PC2 alone is outside the ±0.0715 band a series
    with no persistence stays inside 95 percent of the time, and no factor
    survives Benjamini-Hochberg at q = 0.05, a control for false discoveries
    across the five, so any verdict could be noise. PMC is one symbol whose
    two price histories join into one day's return. Without it, PC2 falls to
    −0.0152 and PC3 rises to 0.0139, so which factor misses rests on that
    symbol. Measured after the run, a series rebuilt from each day's own
    weights, with each vector's sign set so its largest weight is positive,
    would read PC2 at −0.1105, and −0.0161 with sign and rank matched
    to today's. Fitting tomorrow's weights on a window that leaves today's
    return out brings it to 0.0776.
    Every figure is exploratory and about survivors.
43. The leverage of Chapter 8's Boxes 8.1 to 8.6 in *Algorithmic Trading*,
    chosen three ways on Example 5.1's 612 saved returns: by the optimum of
    100,000 returns drawn from a Pearson type IV fitted to their four
    moments, by the optimum of the historical growth rate, and with
    constant proportion portfolio insurance (CPPI). The simulated figures
    run on a declared seed and are judged against 200 more. The book's Kelly
    and historical optimum of 18.4 do not reproduce, since Chan's own returns
    give 23.845328 and 23.721773. A series matching Example 5.1's printed
    Sharpe ratio and APR has a Kelly of at least 21.56 when the APR compounds
    the log growth, and at least 20.89 under the simplest compounding, so
    none reaches 18.4. The minimum draw and the drawdown at the optimum land.
    The simulated optimum, the drawdowns at half and a seventh of the
    optimum, and both growth rates of location 3438 fall outside their bands.
    The simulated optimum landed under the band the issue declared, and the
    band chosen after the ensemble was seen excludes it, for a reason the log
    entry gives. Moving the draws' mean so the Kelly is 18.4 lands all of
    those but the drawdown at half the optimum.
    Box 8.6's CPPI loop breaks the 0.5 drawdown floor on every one of the
    200 seeds, and the CPPI location 3426 describes keeps it on every one.
    The write-up measured after the run that the declared seed's least draw,
    −0.043071, is 1.9550 times as deep as the worst of the 612 saved returns,
    and that the Kelly lies at or past the ruin leverage on 78 of the 200
    seeds. The depth comes from the count of draws rather than a fatter tail,
    since 612 draws from the fit reach that worst return with a chance of only
    0.091663. Every figure is exploratory.
44. Chan's rule at location 4709 of *Quantitative Trading* that "a highly
    leveraged portfolio of low-beta stocks should generate higher long-term
    compounded growth than holding an unleveraged portfolio of high-beta
    stocks", on Chan's S&P 500 file. Each month-end the lowest and highest
    fifths by trailing beta are held one month, and the low fifth is levered
    to the high fifth's mean beta, location 4684's match. The claim is
    contradicted by ruin. The low fifth's beta at formation fell as low as
    0.0280, so the match asked for a leverage of up to 69.0762, and the levered
    portfolio lost more than its capital in the month ending 2001-06-29, at a
    leverage of 58.0262. A fresh stake levered by the same rule would have
    lost more than its capital again in September 2001. Location 4700 warns of
    this: "one should be quite wary of using too much leverage on normally
    low-beta stocks". The verdict is registered, because the plan and its
    criterion were written on
    [issue 275](https://github.com/l3a0/quantitative-trading/issues/275)
    before any number was computed. The ruin case and its wording are that
    issue's amendment of 2026-10-11, which the owner ruled after the first
    ruined month was visible. The span is not a holdout, and every figure is
    about the stocks still in the index on 2007-11-23. Beside the verdict, the
    low fifth's Sharpe ratio of 1.0132 against the high fifth's 0.4457 is an
    untested point estimate, exploratory, and decides nothing. The low fifth's
    return in June 2001 was −0.0403, the sixth-worst of its 83 months.
    Measured after the run, that sat below a ruin line of −0.0144, so an
    ordinary month did the damage.
45. The VIX filter at location 3509 of *Algorithmic Trading*, which keeps
    only the days after the VIX closed above 35 and reruns two rules on
    them: item 18's buy on gap and item 40's opening gap rule on FSTX. Each
    rule runs unchanged on Chan's own files, its calendar is joined to that
    of Chan's `VIX.csv`, and the figures are 252 times the mean and the
    Sharpe ratio over the days kept. Buy on gap keeps 190 days and gives
    0.171924 and 1.417425, which round to the book's 17.2 percent and 1.4.
    FSTX keeps 185 and gives 0.025730 and 0.164869 under the script's fading
    sign, which round to the book's 2.6 percent and 0.16. The momentum sign
    gives the same numbers negated. Beside the verdict, Welch's t on mean
    daily return, the kept days against the other joined days, is 0.705402
    for buy on gap and −0.684181 for FSTX's fade, with p of 0.481405 and
    0.494679, treating each day as independent. So the claim that VIX above
    35 warns the gap trader off rests on point estimates this test cannot
    tell from noise, for either sign. It is exploratory and decides nothing.
    No script ships for the filter. The FSTX alignment was chosen after six
    were tried, and all six are recorded. Only the join lands 2.6 percent. The latest VIX close
    before each day lands the Sharpe ratio but prints 2.5 percent, and the
    two that read VIX on the trade's own date look ahead. Buy on gap's
    figures are the same under any alignment that reads the previous day.
    Measured after the run, 151 of buy on gap's 190 kept days and 146 of
    FSTX's 185 fall in 2008 and 2009, and one day, 2009-04-21, returned
    0.093601 of the 0.129625 buy on gap's kept days sum to. Every figure is
    exploratory.
46. Item 44's rule after the book, on the S&P 500 as IVV held it at each
    month-end from 2008, with SPY's Alpha Vantage closes as the market. It is
    not decided: "No gap in compounded growth detectable above about 0.2948 a
    year over 208 months, where the point estimate is -0.0590." Levered to the
    high fifth's beta, the low fifth trailed the unlevered high fifth at a
    Newey-West t of −0.4974, and no month was ruined. Four formations, the
    first 2026-04-30, are skipped, because the low fifth's mean beta there was
    zero or below and no leverage matches it. Location 4700's caveat, "one
    should be quite wary of using too much leverage on normally low-beta
    stocks", stands beside it, and the worst levered month lost 0.8014 of the
    capital. The result is registered on
    [issue 526](https://github.com/l3a0/quantitative-trading/issues/526),
    under [issue 275](https://github.com/l3a0/quantitative-trading/issues/275)'s ruin amendment and
    [issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s skip amendment, both of
    2026-10-11, and the skip rule was ruled after the first skipped formation
    was visible. Every holding month comes after the first edition's release
    in November 2008, and this repository has read the rule only in the 2021
    revised edition. Membership is the
    members the monthly coverage rule keeps, which leaves out 6,943 of
    107,115 member-months. 6,816 of those fail the row check against the
    filing, and 4,614 of the 6,816 carry a ticker absent from the 2026-06-30
    schedule, which marks a company that left the index or changed its
    ticker. Each quarter-end schedule is carried forward, so a change between
    schedules is dated up to two months late, or five around the missing
    2013-09-30 schedule. Measured after the run, a one-sided test at 5
    percent rejects every levered advantage above 0.1360 a year, and
    December 2024 alone sets the gap's sign, since without it the gap is
    +0.0313.
47. Item 22's Example 2.5 after Chan's sample, on Alpha Vantage's USD/CAD
    daily closes from 2012-03-29 to 2026-10-12, at the lookback of 115 days
    fixed from his closes and never re-estimated. The claim that the P&L ends
    positive reproduces: over 3,791 traded days it sums to 0.1132. It
    survives on its sign alone. The mean daily P&L has a Newey-West t of
    0.2670, and the deepest drawdown, 0.5033, is more than four times the
    final P&L. On the later closes the ADF, variance ratio and Hurst tests
    read as a random walk, and each of those three landed as
    [issue 607](https://github.com/l3a0/quantitative-trading/issues/607)
    registered it before any holdout close was read. The half-life is
    457.8077 days against the frozen 115, and the issue registered no
    prediction for it. The result is
    registered and comes from one feed, the vendor's daily close rather than
    Chan's 16:59 bar, because the holdout on his bar moved to
    [issue 608](https://github.com/l3a0/quantitative-trading/issues/608).

Two more results run here, and neither is a replication. The first comes from
the same passage, which names bonds of one issuer as a place a stationary
spread should live without naming an instrument, so there is no number of his
to reproduce and no series of his to test. That fixed-income candidate, bonds
of one issuer at two maturities, is tested on TLT against IEF, and the result
is a finding rather than a verdict. Over
2002-07-30 to 2026-10-01 neither orientation rejects the no-cointegration
null, at −2.3887 and −2.3168 against a 10% bar of −3.04, and the residual check
moves both further from rejecting rather than closer. It is exploratory, and it
says nothing about bonds beyond these two funds.

The second is the Khandani-Lo reversal on Chan's S&P 600 file, which tests his
explanation that most of Khandani and Lo's returns came from small and
microcap stocks. Example 3.8 leaves that run as an exercise and prints no
figure for it, so the result is a finding rather than a verdict. Before costs
the rule earns a Sharpe ratio of 3.4086 on the closes and 5.3052 on the opens,
against the S&P 500 file's 0.2510 and 4.4202, so it points the way Chan says
at both prices under the reading declared before the run. The gap on the
closes, +3.1576, is more than three times its standard error of 0.9872, and
the gap on the opens, +0.8850, is smaller than its 1.1640, so one year of the
opens cannot tell the two universes apart. The standard error assumes
independent, normal days, which a reversal's are not, so it is an
approximation. After 5 basis points a side the S&P 600's closes lose only a
little. The rule trades about the same amount a day on both files at both
prices, so the profit decides, and the S&P 600's average day on the closes
pays 1.0945 times its profit in cost, against the S&P 500's 13.7453. It is
exploratory, both files hold only survivors, and it says nothing about
microcaps. The S&P 600 file holds prices and volumes but no market values, so
nothing here measures how many of its members were microcaps.

A third result runs the S&P 400 half of the same exercise, and it is not a
replication either.
[Issue 303](https://github.com/l3a0/quantitative-trading/issues/303) runs the
reversal on IJH's holdings in iShares Trust's N-Q for 2007-12-31, priced from
the owner's archive of Alpha Vantage files, and reads the three indexes as one
ladder. Before costs the S&P 400 earns 2.0338 on the closes, between its two
neighbours, and 3.4533 on the opens, below both. So the order Chan's
explanation predicts holds on the closes and is partial on the opens, which
the reading declared before the run calls mixed. One of the four steps is
beyond one year's noise, the closes' step from the S&P 500 to the S&P 400, at
a z of +2.1973. The S&P 400's prices come from another vendor and another
decade than Chan's files, so an S&P 600 control built the same way is read
against Chan's S&P 600 file. It lands +0.1108 from that file on the closes and
−0.7244 on the opens, inside the S&P 400's steps to its nearer neighbour of
1.3748 and 0.9669, so under the declared rule the ordering is separable from
how the panel was built. Every figure is exploratory and about survivors, and
Entry 50 in [docs/replication-log.md](docs/replication-log.md) carries them
all.

A rerun of item 12 runs here too, and it is not a replication either. Item 12
reproduces Chan's post-earnings drift on his own prices and flags, and
[issue 251](https://github.com/l3a0/quantitative-trading/issues/251) asks what
the same rule gives on a calendar nobody hand-collected and on prices from
another vendor. The calendar comes from the Item 2.02 8-Ks EDGAR accepted for
Chan's stocks, timed by each filing's header, and the prices from the owner's
archive of Alpha Vantage files. On the 441 stocks with a checked CIK and a
checked series, Chan's prices and flags give an arithmetic annual return of
0.043678 and a Sharpe ratio of 1.2815, and the archive's prices on the
calendar a trader could have built before each open give 0.057489 and 1.6585.
Most of that rise in return comes from the calendar taking more trades,
because the rule divides each day by a fixed 30. Each trade earns only about 6
percent more on average than on Chan's flags. Narrowing the 497 stocks to
those 441 moves the arithmetic return most, by −0.023065, and the vendor and
the price basis move it by about a ten-thousandth each, judged on the closes.
Every figure is exploratory, and Entry 46 in
[docs/replication-log.md](docs/replication-log.md) carries them all, with the
checks on the archive's opens that the series check does not make.

Item 44's own run reaches a registered verdict: ruin contradicts the claim.
The same rule also runs at leverage a broker would lend, and that capped run
reaches no verdict.
[Issue 516](https://github.com/l3a0/quantitative-trading/issues/516) caps
location 4684's beta match at 2, the overnight leverage Regulation T allows,
and at 5, from portfolio margin's "20 percent or less" at location 814. Five
is the highest leverage the book puts a number on for stocks held overnight,
and the "or less" leaves room for more. Neither ceiling ruins the portfolio.
In point estimate the capped low fifth out-compounded the unlevered high
fifth, by 0.0934 a year at a ceiling of 2 and 0.1659 at 5, with Newey-West t
of 1.0715 and 1.2111.
Benjamini-Hochberg across the two ceilings rejects neither in either
direction, so neither ceiling is decided. Every figure is exploratory, because
the ceilings were chosen after item 44's calendar, leverage path and ruin had
been seen, along with eight months of both groups' returns and its Sharpe
ratios, growths, betas and Kelly leverage. As in item 44, the span is not a
holdout and every figure is about the stocks still in the index on
2007-11-23. The run borrows at the bill rate, which flatters the levered side,
and month-end closes cannot see a margin call inside a month. Entry 48 in
[docs/replication-log.md](docs/replication-log.md) carries them, with the
break-even borrowing spread, the worst month and location 4700's caveat
beside them.

[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py) freezes
every number this repo quotes about either pair, and it is the only place any of
them is derived. The two blog posts about the pairs are the exceptions, and
what each says that nothing here asserts is listed below. Each GLD/GDX pin
names its window and its regression specification, because the book prints two
of those near each other and they come from different runs.

[tests/test_coin_flip_growth.py](tests/test_coin_flip_growth.py) does the same
for the coin flip, and separates the figures the book prints from what a seeded
run is entitled to claim, because no simulation this suite could afford
resolves Chan's seven decimals.

[tests/test_kelly_leverage.py](tests/test_kelly_leverage.py) does it for the
Kelly run, and separates the figures from the specification that produces them,
because three of the five choices behind Chan's numbers are invisible on the
page and each has a plausible wrong answer that does not look wrong. The blog
post about it is the exception, and what it says that nothing here asserts is
listed below.

[tests/test_risk_parity.py](tests/test_risk_parity.py) does it for the risk
parity run, and pins the ranking as a measured difference and a robust
t-statistic rather than as the comparison's result, because an assertion that
one Sharpe ratio exceeds another survives any mutation that leaves the sign
alone. The blog post about it is the exception, and what it says that nothing
here asserts is listed below.

[tests/test_stationary_candidates.py](tests/test_stationary_candidates.py)
does it for all three stationary candidates. It pins both orientations of every
fixed-income number, because the test is not symmetric in its legs and Chan
names no dependent one. For the cross rate it pins the verdict rule as well as
the verdict, so a criterion edited after the fact fails a test. For the
calendar spreads it pins how often the files hand over on the day each expiry
rule says and on a day either side, so a rule moved by one day fails a test,
and it pins the bars of both the declared null and the corrected one.
The two blog posts about them are the exception, and what each says that
nothing here asserts is listed below.

[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py) does it for
the equity seasonals. It pins every printout's figures at its own printed
precision, and the figure each of Chan's rules gives when it is changed, so a
builder who corrects his code fails a test rather than moving a pin. Its
survivor-run and point-in-time pins read the owner's archive and skip where
none is configured. The survivor run's mechanics and its 603 manifest lines
are held everywhere, and so are the point-in-time run's flags, bound, verdict
and refusals. So are the monthly run's `members` keyword, stop rule,
stopped-price fill and verdict wording, and the names that changed between
IVV's schedules. The
blog post about them is the exception, and what it says that nothing here
asserts is listed below.

[tests/test_khandani_lo.py](tests/test_khandani_lo.py) does it for the
reversal. It pins Chan's two figures at four decimals and at the book's two,
and the figure with both quirks removed at four. It also pins the −3.1822 a
port gives when it skips the missing day in the standard deviation as well as
the mean, because that is the mistake that misses Chan's −3.19. It also pins
what an average day earns, costs and trades as a share of the position held,
which explains where the third figure lands. For Example 3.8 it pins both rules
on the opens, the claim's verdict, and the notebook's Example 3.7 figures on
the closes, which fail if a transcription leans on pandas' current
`pct_change`, because that no longer fills gaps. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.

[tests/test_khandani_lo_small_caps.py](tests/test_khandani_lo_small_caps.py)
does it for the reversal on the S&P 600. It pins the six figures, their six
gaps to the S&P 500's, and both before-cost gaps' standard errors,
correlations and z values, each naming its vintage, and it pins the declared
reading. It works Memmel's standard error by hand on a four-day series. It
also holds that the two files' 2006 calendars are the same 251 days, that
BCSI's and SCUR's two days past the scale-break bound are weighted, that PMC,
two companies under one symbol with no 2006 price, carries no weight, and that
the scale-break guard refuses the window on exactly those two days. It holds
what the write-up measured after the run too: the average day of the three
books `tests/test_khandani_lo.py` does not already pin, the cost a side at
which each of the four breaks even, the open's lift in each universe, the
closes' standard error with the correlation set to 0, and the share of
Memmel's bracket the correlation term carries on each price, with the helper
behind them worked by hand. The blog post about it is the exception, and what
it says that nothing here asserts is listed below.

[tests/test_khandani_lo_mid_caps.py](tests/test_khandani_lo_mid_caps.py) does
it for the reversal on the S&P 400, between Chan's two files. It pins the
S&P 400's six figures, each step to both neighbours with its standard error,
correlation and z value, the S&P 600 control built the way the S&P 400 panel
is, with and without its three exclusions, the control's gap to Chan's S&P 600
file with its standard error, and the declared reading. It holds that the
S&P 500 and S&P 600 runs give the same floats as
`chan.khandani_lo_small_caps`. Those pins skip unless the archive is
configured and `QT_ARCHIVE_RUN=1`. On figures and frames built by hand it
holds the three-universe reading, the control's rule, and that the exclusions
change the returns on exactly the declared cells.

[tests/test_survivorship_bias.py](tests/test_survivorship_bias.py) does it for
the survivorship toy, and pins equal shares beside the book's equal capital,
because a pin on the right number alone holds a number rather than a choice. Its
tolerance is tight enough to hold the two tables as well as the arithmetic: a
sweep run when the pins were written found that moving any printed cell by one
unit in its last digit fails a test. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.

[tests/test_commodity_seasonals.py](tests/test_commodity_seasonals.py) does it
for the commodity seasonals. It pins every year's outcome for both trades,
rather than only the counts, so a calendar error that swaps a profit for a loss
fails a test even where the count survives. It also pins the natural gas
expiry rule against the exchange's own last trading days, and each date Good
Friday moved. The blog post about them is the exception, and what it says that
nothing here asserts is listed below.

[tests/test_pead.py](tests/test_pead.py) does it for post-earnings drift. It
pins each figure `pead.m` prints at the precision that is real and again as
the script formats it, beside the book's rounded figures. It also pins the
first edition's `smartstd` landing on 0.0668, so a port that reaches for the
helper this repo already held fails a test rather than reading as a near
miss. The blog post about it is the exception, and what it says that nothing
here asserts is listed below.

[tests/test_pead_rerun.py](tests/test_pead_rerun.py) does it for the rerun on
EDGAR's calendar. It pins the figures, trades, busiest day and mean return
per trade of each run
[issue 251](https://github.com/l3a0/quantitative-trading/issues/251) fixed
before it ran, the attribution, and each calendar's cell-by-cell agreement
with Chan's flags. The pins that read the
archive's prices skip unless the archive is configured and
`QT_ARCHIVE_RUN=1`. Its `TestWhatThePostMeasured` holds what the post on the
rerun measured after the runs: run A split among U and the groups of
stocks outside it, why each stock outside U failed its check, the day the
stocks outside U add most, their mean trade against U's, R1's extra trades
priced at its own mean, and the days B1 and B5 hold more than 30 positions.
Every one of those reads committed files and decides nothing. The trades
behind each move of E1 and E5 on Chan's opens are pinned beside the opens, and
skip with them. The blog post about it is the exception, and what it says that
nothing here asserts is listed below.

[tests/test_pca_factor.py](tests/test_pca_factor.py) does it for the PCA
factor model. It pins each printout's figures as the printout formats them and
in full, and the figure each of the Python's bookkeeping choices gives when it
is changed, so a builder who corrects Chan's code fails a test rather than
moving a pin. It also holds the Python's book equal to a momentum ranking on
every day, which is the finding the entry rests on. The blog post about it is
the exception, and what it says that nothing here asserts is listed below.

[tests/test_momentum_factor.py](tests/test_momentum_factor.py) does it for the
market and momentum factors. It pins the calendar, the legs, both factors'
autocorrelations and the stocks' quartiles, and one verdict per factor. Its
`test_the_month_before_formation_does_not_rank` holds the skip, so a
lookback that runs to the formation's own close fails a test. The blog post
about them is the exception, and what it says that nothing here asserts is
listed below.

[tests/test_cpo.py](tests/test_cpo.py) does it for Conditional Parameter
Optimization. Its mechanics run everywhere. The recursions, the rules and the
round trips are each held against a literal loop over the book's rules, and the
rest by worked examples. Its pins run only where the
owner's archive of minute bars is, and only when `QT_ARCHIVE_RUN=1` asks,
because the full run takes about five minutes. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.
[tests/test_archive.py](tests/test_archive.py) holds the archive's own record:
each standalone line field for field everywhere, and the files' hashes and the
minute bars' agreement with the committed daily closes wherever an archive is
configured. The 603 lines the survivor run reads from the `sp600`
cross-section are held by the sha256 of their bytes in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py), everywhere.

[tests/test_cross_sectional_momentum.py](tests/test_cross_sectional_momentum.py)
does it for cross-sectional momentum. It pins each figure `kentdaniel.m`
computes at the precision that is real and as the script formats it, beside
the comment it misses and the book. It pins each declared reading over all
three windows, its distance from the book, and the rule deciding whether one
lands. It holds the transcription to a second implementation written
separately in pandas, which rules out a slip in the numpy code, though not a
misreading of the MATLAB, since both read it the same way. It also pins the
first edition's `smartstd` printing 4.05 against 4.07, so a port that reaches
for the helper this repo held first fails a test. The blog post about it is
the exception, and what it says that nothing here asserts is listed below.

[tests/test_buy_on_gap.py](tests/test_buy_on_gap.py) does it for buy on gap.
It pins both figures `bog.m` prints at the precision that is real and at the
book's, the declared mirror's figures beside Chan's, and both sides under the
first edition's `smartstd`, so a port that reaches for the helper this repo
already held fails a test. It also holds the decision not to call the
scale-break guard, by running it and pinning what it would refuse. The blog
post about it is the exception, and what it says that nothing here asserts is
listed below.

[tests/test_khandani_lo_book_two.py](tests/test_khandani_lo_book_two.py) does
it for the reversal on the 2012 panel. It pins each figure at six decimals and
again at the precision Chan printed, and both bridge rows beside the first
book. It also holds the first days at zero, the same series under either
reading of the `lag` the script calls, and the profit of Example 3.8's
notebook without its fill, which computes the same rule by another route, so a
transcription that takes returns before the cut fails a test. The blog post
about it is the exception, and what it says that nothing here asserts is
listed below.

[tests/test_price_spread.py](tests/test_price_spread.py) does it for Example
3.1. It pins each figure the three scripts print at their six decimals and
again at eight, and the book's rounding beside them. It pins the ratio's miss
and the swapped legs that land it, both of location 1505's claims, and the
Engle-Granger test of its statement that the pair does not cointegrate. It also
holds two choices no figure here can see, the padding of `lag` and the
divisor of the moving deviation, so a reader does not take these figures as
evidence about either. The blog post about it is the exception, and what it
says that nothing here asserts is listed below.

[tests/test_bollinger.py](tests/test_bollinger.py) does it for Example 3.2.
It pins both figures `bollinger.m` prints at six decimals and again at eight,
the book's rounding beside them, and the claim that the band improves on the
linear rule. It also pins the run with the deviation divided by n, which moves
both figures here, and holds the band's edges on synthetic arrays, since no
real day sits exactly on one. The blog post about it is the exception, and
what it says that nothing here asserts is listed below.

[tests/test_kelly_allocation.py](tests/test_kelly_allocation.py) does it for
the leverage examples. It pins Example 8.1's figures to the dollar and each
Example 8.2 figure at six decimals and again at the precision the book prints,
and pins the near miss beside them: solving along
Chan's line without bounding it finds a higher growth rate by going short,
over the gross cap. The blog post about the leverage examples is the
exception, and what it says that nothing here asserts is listed below.

[tests/test_usdcad_mean_reversion.py](tests/test_usdcad_mean_reversion.py)
does it for the stationarity tests on USD.CAD. It pins each figure the script
prints at the precision that is real and at the script's, H as a miss against
the book's 0.49, and the ADF statistic `adfuller` gives beside jplv7's, so a
port that reaches for the ADF this repo already held fails a test. It also
recomputes Example 2.5's daily P&L with plain pandas, pins its Sharpe ratio
against any fixed account, and pins how far H moves on 40,000 seeded random
walks and with the sample's start day. It pins the
standard errors 40,000 walks carry and checks that every quoted digit holds
with two of them to spare.
[tests/test_stationarity_tests.py](tests/test_stationarity_tests.py) holds the
three toolbox tests' rules on synthetic series: the row jplv7 drops, the bins
of its critical values, `genhurst`'s indifference to level and scale, and the
variance ratio's trim to whole periods. The blog post about the USD.CAD
examples is the exception, and what it says that nothing here asserts is listed
below.

[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py) does it for
the ETF cointegration examples. It pins every figure `cointegrationTests.m`
prints at the precision that is real and as the script printed it, each
critical value as the script formatted it, and the book's rounder figures. It
also holds that negating the eigenvector moves no figure, since statsmodels
returns it with the opposite sign from Chan's, and that padding the lag with
zeros as LeSage's `lag` does gives the same series. The blog post about them
is the exception, and what it says that nothing here asserts is listed below.
[tests/test_index_arbitrage.py](tests/test_index_arbitrage.py) does it for
Example 4.2. It pins the screen's count with the 17 stocks it skips by name,
every figure `indexArb.m` prints at the precision that is real and as the
script printed it, and the screen's rules on frames built by hand. It also runs
the scale-break guard on the stocks and holds that it would refuse the run,
which is why only SPY is guarded. The blog post about it is the exception, and
what it says that nothing here asserts is listed below.
[tests/test_johansen.py](tests/test_johansen.py) holds what the wrapper adds:
a known cointegrating vector recovered from a built system, real figures
without a warning, and a refusal naming the column and row of any price that
is not a finite number.

[tests/test_aud_cad_johansen.py](tests/test_aud_cad_johansen.py) does it for
Example 5.1. It pins the three printed figures at the precision that is real,
as the script printed them and as the book rounded them, and holds the 612
returns against Chan's saved ones row by row. It also holds that negating or
scaling one day's hedge moves no return, that two series on different dates
are refused, that scaling either leg leaves the match and one digit on a close
in the test window breaks it, and that ending both windows a day earlier, as
the Python port does, breaks it too. The blog post about it is the exception,
and what it says that nothing here asserts is listed below.

[tests/test_roll_returns.py](tests/test_roll_returns.py) does it for the spot
and roll returns. It pins each strip's two figures at the six decimals the
script's `%f` prints, which of Table 5.1's cells they round to with the sign
included, corn's agreement with the Python port, and the two claims the book
makes from the table under criteria fixed before the build, though after a
scratch run had measured the figures. Beside them it
pins the month-spaced roll return, the month gaps each day's fit reads, and
the three readings of the spot return tried after HG's and TU's missed. On
synthetic frames it holds the script's rule: no fit on a day with four priced
contracts or with a gap among the nearest five, only the nearest five read,
and a gap in the spot still counted as elapsed days. The blog post about it is
the exception, and what it says that nothing here asserts is listed below.

[tests/test_vx_es.py](tests/test_vx_es.py) does it for VX against ES. It pins
the four figures on the 2012-05-07 save at the precision that is real and at
the book's, and each diagnostic beside them: the first training day dropped,
an exit at the mean, a band started flat on the first test day, the printed
hedge traded, the 2012-05-11 and 2012-05-17 saves, and `VX_ES.m` as it ships.
It also holds the training and test spans, the four positions, and the
scale-break guard on each leg of each save. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.

[tests/test_gold_miners_oil.py](tests/test_gold_miners_oil.py) does it for
the Johansen tests on GLD, GDX and USO. It pins the six claim criteria as the
issue declared them, the book's three quotes against the highlight they come
from, every statistic and eigenvalue of the four tests and of each ETF with
USO alone at the precision that is real, the CADF and ADF rows beside them,
and the cut to GDX's first price that keeps a missing price from reaching the
test. The blog post about it is the exception, and what it says that nothing
here asserts is listed below.

[tests/test_aud_cad_rollover.py](tests/test_aud_cad_rollover.py) does it for
Example 5.2. It pins the script's two printed figures, the book's four, and
the annualised rollover against the criterion written before it was computed,
each at the precision that is real. It also holds that a month the rate file
lacks gets a rate of zero, that AUD triples on Wednesdays and CAD on
Thursdays and a holiday multiplies nothing, that each day's return carries the
previous day's position and rates, and that zero rates give the script's
commented-out formula without rollover bit for bit. The blog post about it is
the exception, and what it says that nothing here asserts is listed below.

[tests/test_cl_reversal_momentum.py](tests/test_cl_reversal_momentum.py) does
it for the crude oil rule. It pins the two figures on the 2012-05-04 save at
the script's six decimals and at the book's precision, the script's other
three rules beside them, the 2012-05-11 save, and the three rules on the
2012-05-07 save's four years before the window. It also holds the positions,
the ten rows where ComboOR differs, five changes to the specification that
each move a figure, and the scale-break guard on each span of each save. The
blog post about it is the exception, and what it says that nothing here
asserts is listed below.

[tests/test_kalman_hedge.py](tests/test_kalman_hedge.py) does it for the
Kalman filter on EWA and EWC. It pins the script's two printed figures at its
six decimals and at eight, the book's rounding of them, and the run with no
signal on the first two days. It holds the filter's zero start on the first
row, the second row against its closed form, the first position and return,
and every figure the two findings quote: the slope's median, mean, share above
1 and crossings, and the intercept's yearly means, its falls at each finer
grain and its peak. It also
holds that the read calls the scale-break guard on both legs and that a
planted break in either is refused. The blog post about it is the exception,
and what it says that nothing here asserts is listed below.

[tests/test_tu_momentum.py](tests/test_tu_momentum.py) does it for TU's
momentum. It pins the six figures of `TU_mom.m`'s comment, the 250/25
correlation, H and the variance ratio test at six decimals and at the
precision Chan printed, all 49 cells of the correlation table, the script's
2009 window, and the 2012-05-17 save that `correlationTest.m` loads. It also
holds the Gaussian statistic of 2.9333 that Example 1.1's hypothesis tests
start from, the rule on synthetic arrays, the refusal of a position larger
than the tranche count, and the scale-break guard on TU. The blog post about it
is the exception, and what it says that nothing here asserts is listed below.

[tests/test_calendar_spread_reversion.py](tests/test_calendar_spread_reversion.py) does it
for the crude oil calendar spread. It pins the script's window and the window
a day later at six decimals and at the precision Chan printed, the ADF
statistic against its 1 percent critical value, the run holding each pair at
least 61 days, the first and last days a pair is held, and the 66 rows at the
window's end that return exactly 0. It pins the direction the trade bets too:
the held spread's correlation with γ, its own z-score's sign against γ's, the
far leg's side against the z-score's sign, the figures with every position
reversed or flipped on the spread's own z-score, the rule before the window,
and each calendar year. It also runs the script's window on CL
with a lookback and an end passed in, which no row above passes, and pins the
CL strip as the vintage `run` reads from the directory it is given. On
synthetic frames it holds the script's schedule, sign flip and return, and the
refusal of a signal on an index other than the contracts'. Seven of those
synthetic cases hold choices the CL strip cannot show.

1. Line 98's strict comparison, which never holds a one-row window.
2. Line 83's last mark, which expires a contract with a gap in its prices on
   its last priced row.
3. Line 107's strict comparison, which keeps the schedule's sign where the
   z-score is exactly 0.
4. The lookback's rounding, which takes a half-life with a fractional part of
   at least 0.5 up.
5. Line 42's forward fill, which the half-life, the ADF test and the z-score
   all read, since γ on CL has no gap after its first value.
6. Line 85's `max(1, ...)`, which starts a first pair on the file's first row
   when its expiry comes sooner than `holddays + 10` rows in.
7. Line 110's `smartsum`, which skips a leg whose return is infinite.

The blog post about it is the exception, and what it says that nothing here
asserts is listed below.

[tests/test_vx_calendar_spread.py](tests/test_vx_calendar_spread.py) does it
for the VX calendar spread. It pins the specification and the four rows
declared beside it at six decimals, the book's three figures against the
specification at the precision Chan printed, and the two measurements taken
after the run, each marked as such. It also holds why the specification pairs
contracts a month apart, the 64 of VX's 71 pairs and 68 of CL's 77 held under
`holddays=0`, the 43 pairs B3 holds from 2008-10-27, and why its last pair
ends on the book's end date. It holds which pair each row's signal reads
too: the specification's near leg is the front contract on 126 of its 847
held rows from 2008-10-27, and under `holddays=0` on 459 of 879. On synthetic
frames it holds the two signals' rules and the near leg's place: a row whose
nearest two contracts skip one, the held pair across a roll, and the fill
across days nothing is held. The blog post about it is the exception, and what
it says that nothing here asserts is listed below.

[tests/test_roll_momentum.py](tests/test_roll_momentum.py) does it for TU's
momentum on the roll return. It pins the three figures at six decimals and
at the book's precision, Example 6.1's rule on the same rebuilt series and
each claim's margin, the rebuild against the 2012-05-11 save, both rules on
that save's own close, and the month-unit and fifth-contract readings. It
also holds the declared rule and the roll's off-by-one on synthetic strips,
the March 2012 roll, and the scale-break guard on every member's own rows.
The blog post about it is the exception, and what it says that nothing here
asserts is listed below.

[tests/test_tu_hypothesis_tests.py](tests/test_tu_hypothesis_tests.py) does it
for Example 1.1's three hypothesis tests on TU. It pins every count exactly at
its declared seed and every proportion at six decimals, the landing bands, the
Gaussian statistic, and the three rows added after the scratch run. It holds
the Pearson type IV sampler's parameters against their closed-form moments and
its tails against quadrature, and holds the two-dimensional form equal to
`chan.tu_momentum`'s functions draw by draw and unchanged by the batch size. It
also holds that the third test as written leaves every simulated return at
zero. The blog post about it is the exception, and what it says that nothing
here asserts is listed below.

[tests/test_gld_gc.py](tests/test_gld_gc.py) does it for long GLD and short
gold futures. It pins the five figures of `GLD_GC.m`'s closing comment and the
text's two at six decimals and at the precision Chan printed, the financing
row beside them, and the measurements that say the GC file is read at GLD's
close. It also holds every step of the script on synthetic legs whose
figures are worked out by hand, and the scale-break guard on each series it
reads. It holds what the write-up measured after the run too: the Sharpe
ratio at no rate and at the window's bill rate, the two drawdowns, the
return against the bill rate by calendar year, and the daily change in
log(GC / GLD) on both GC series, with the three helpers behind them on
synthetic legs. The blog post about it is the exception, and what it says
that nothing here asserts is listed below.

[tests/test_xle_uso_roll_return.py](tests/test_xle_uso_roll_return.py) does it
for the XLE against USO trade. It pins the five figures at full precision
against the script's comment and the book's two, the 1,498 days the two
calendars share, the 123 days with no front ratio, and the days in contango
and in backwardation. It holds the two quirks of the script's loop on this
strip and the ratio the calendar spread's schedule would give in its place.
On synthetic strips it holds the 40-row start, a later front waiting for the
previous one to end, the NaN left off every front window, the one-day lag and
the half-capital divisor. It also holds both reads guarded. It holds what the
write-up measured too: the 40-row start binding only for CL-2007F, the same
ratio on the save of 2012-08-14, the script's front as the nearest contract on
734 days and the second on 641, the ratio against Example 5.3's γ, the
figures from 2006-10-20, and each view's days, returns and implied roll
return beside the fixed view's. On synthetic frames it holds the split by
view and the fixed view. The blog post about it is the exception, and what it
says that nothing here asserts is listed below.

[tests/test_opening_gap.py](tests/test_opening_gap.py) does it for the
opening gap strategy on FSTX. It pins both readings of the script's return
line at six decimals. The literal reading is pinned against the script's
comment and the book's two figures, and the momentum reading against the
book's two figures alone. It also pins the drawdowns, the days each side
holds and the literal rule on the two earlier saves. On synthetic days it
holds both entry tests non-strict, a missing spread qualifying nothing, a
short overriding a long, and the sign of each reading's open-to-close
return. It also holds the read guarded. For Chan's Python port it pins the
four figures the port's comments print, the days it holds each side, and
three variants that each swap one difference between the two programs. On
synthetic days it holds the port's spread dividing by n − 1 and starting a
row later, its short test flipped and non-strict, an open above the
previous high being short, a missing spread qualifying nothing, and its
Sharpe ratio dividing by n with either sign of mean. It also holds the
Experiments page's figures as the port's comment rounded, and the run's
port block reporting a figure off the comment as a gap. It holds what the
write-up measured too: the first edition's `smartstd` changing no position,
each curve keeping to its side of zero from the first trade, all four fields
equal across the two earlier saves and restated between the later two, the
APR on the 1,996 days those two share with both run from the same first day,
the mean return on a held day, each side's returns and FSTX's move from the
open on long, short and flat days, and the port earning the script's returns
on every upward jump. On synthetic days it holds the split by side, the move
from the open, and two saves run from the same first day so their windows
cannot differ. The blog post about it is the exception, and what it says
that nothing here asserts is listed below.

[tests/test_vx_es_roll_return.py](tests/test_vx_es_roll_return.py) does it
for VX against ES on VX's roll return. It pins the eight figures of both
rules at full precision against the script's comments and the book's two,
the fitted hedge's miss beside them, and the counts of the test's days held,
short, long and entered from flat. It holds the two quirks the run keeps,
the free entry from flat and the file's last day read as an expiry. On
synthetic strips it holds the days to settlement counting one past expiry,
the strict threshold, both legs signed alike with VX scaled by the hedge, the
one-day lag, the gross divisor and the cost of an exit. It also holds each
read guarded and the flagged day in VIX read by no trade figure. It holds what the
write-up measured after the run too: the stretches held, the APR with each
entry charged and with no cost, where the front sits among the priced
contracts, the hedge's 500 days, each leg's share and sum, 2011-08-08, and
the correlation of the front with ES, with the two helpers behind them on
synthetic strips. The blog post about it is the exception, and what it says
that nothing here asserts is listed below.

[tests/test_pca_factor_momentum.py](tests/test_pca_factor_momentum.py) does it
for Example 7.4's own factors. It pins the 752 pairs and the 579 stocks, each
factor's statistic, percentile and same-sign share, the stocks' quartiles, the
band and which factors fall outside it, the Newey-West t and p-values and
Benjamini-Hochberg, and the intercept, each with and without PMC, and one
verdict per factor. On three of the file's days it holds each factor return
equal to the program's fitted slope times its singular value. On synthetic
returns it holds that a flipped vector moves no statistic, that a steady sign
counts as persistence, and the Benjamini-Hochberg step-up. It holds what the
write-up measured after the run too. Those pins count how often each factor's
weights flip sign once each vector's largest weight is made positive, check
that every flip left falls on a day the largest weight moves to another stock
or two factors swap rank, and count how often they swap rank. They give the
statistic when tomorrow's return is read on tomorrow's own weights, matched,
fitted on 251 days that leave today out, and fitted on the 251 days ending
today as the control. They read PMC's weight on the days whose window holds
its one large return and which factor carries it, the ranking left unchanged
without the intercept, and the two days that carry PC2's statistic, which
carry PC1's without PMC. Synthetic data checks the helpers behind them. The
blog post about it is the exception, and what it says that nothing
here asserts is listed below.

[tests/test_monte_carlo_leverage.py](tests/test_monte_carlo_leverage.py) does
it for Chapter 8's leverage boxes. It pins the deterministic rows exactly, each
simulated row on the declared seed and its band across the 200 others, and
each claim row's criterion. It holds the Pearson type IV sampler's parameters
against their closed-form moments, its tail against quadrature at the book's
minimum, and the declared draws' mean and standard deviation. It holds both
CPPI forms equal to their loops, the search to the root of the growth rate's
derivative, and both CPPI forms on a path worked by hand. It also holds the
evidence on the book's 18.4: the Kelly band Example 5.1's printed figures
allow under three compoundings, and the ensemble rerun with the Kelly set to
18.4. It holds which band row 3 reads, and both CPPI forms refusing a NaN
return. `TestWhatThePostMeasured` holds what the write-up measured after the
run: the saved returns' least day and ruin leverage, the chance that 612 draws
from the fit reach that day, how far the 42 seeds ruined below the cap sit
above the exact chance, the low seeds' ruin leverages, the split at the cap,
the 78 seeds on which the Kelly ruins, and the saved returns' drawdowns at the
optimum and the Kelly. `TestThePostsHelpers` holds the helpers the figure
shares with the run. The run calls `pearson_fit` and `kelly` too, and
`account_drawdowns` gives each day's drawdown through `drawdown_path`, which
the run's `max_drawdown` shares, with a test holding its least value equal to
`max_drawdown`'s.

[tests/test_low_beta_leverage.py](tests/test_low_beta_leverage.py) does it for
the levered low-beta claim. It pins the calendar, the leverage path, both
ruined months and the verdict's wording, and beside them the Sharpe ratios,
the growth, the realised betas, the Kelly reading's Gaussian growth, the
formation table and the flagged stock-months. On synthetic panels it holds the beta's intercept and its floor
of 200 days, the tie-break by symbol, the leverage formula, the bill of the
holding month, the ruin threshold, the 1.645 threshold and the detectable
gap's formula. It holds what the write-up measured after the run too: the
formations whose low-fifth beta fell below 0.05 and 0.10, the formations whose
leverage passed 20 and the look-ahead Kelly leverage, the levered wealth
before the first ruin and the two levered losses on the way, the ruin line,
the low fifth's worst month, the leverage that ruins each month, and the
chance a normal month reaches June 2001's line, with the three helpers
behind them on synthetic months. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.

[tests/test_vix_filter.py](tests/test_vix_filter.py) does it for the VIX
filter. It pins both rules' figures on the days kept at six decimals against
the book's four, and FSTX's under the momentum sign beside them. It pins each
reading that misses with the reason it was set aside: the compounded APR, the
zeroed days, and the five FSTX alignments besides the join. Those are the
latest VIX close before each day, VIX forward-filled and moved one row, a
shift on FSTX's own calendar, and the same day's close with and without a
fill, which look ahead. It also pins the days each calendar keeps, the days each rule held
a position, the unfiltered figures on the joined calendar, FSTX's rule
run after the join keeping the same returns on the days kept, and Welch's t
for the days kept against the rest. On synthetic
series it holds the strict threshold, the previous joined day's close and a
missing close qualifying nothing. It also holds VIX guarded on both sides of
its flagged day, a planted doubling before that day refused, and a planted
rescale under 1.6 times passing the guard and moving a figure. It holds what
the write-up measured after the run too: the kept days by year and in runs,
VIX's closes above 35 inside FSTX's window and before it, its highest close,
each rule's returns summed over its kept days, and buy on gap's largest kept
day, with the two helpers behind them on synthetic series. The blog post
about it is the exception, and what it says that nothing here asserts is
listed below.

[tests/test_low_beta_capped.py](tests/test_low_beta_capped.py) does it for
the same rule at leverage a broker would lend. It pins each ceiling's
outcome, gap, t, both p-values, both decisions of the Benjamini-Hochberg
control and the detectable gap Y, the gap a 5 percent test finds four times
in five. Beside them it pins the growth, the mean leverage, the months each
ceiling binds, the worst month, the realised beta and the break-even spread.
On portfolios built by hand it holds the cap, the replacement of both the
return and the leverage, a ruined ceiling at p = 1 in both families, both
Benjamini-Hochberg families, each outcome's wording, and the break-even
spread's bisection, and its "none" when the gap is 0 or below with no spread.
It also holds the refusal of a ceiling at or below 1, which borrows nothing,
and the bisection's limit on halvings, which ends the search where the floats
lie too far apart for its tolerance. It holds what the write-up
measured after the run too: each ceiling's yearly standard error and 5
percent line, that each point estimate falls short of its line and under half
of its Y, June 2001's capped return at each ceiling, and the smallest leverage
that would ruin any of the 83 months. It also checks the two functions that
compute the standard error and the line against a statistic set by hand. The
blog post about it is the exception, and what it says that nothing here
asserts is listed below.

[tests/test_low_beta_holdout.py](tests/test_low_beta_holdout.py) does it for
the same claim on IVV's S&P 500 from 2008. It pins the verdict, the four
skipped formations, the side figures, the counts, the flagged stock-months
and the archive half of the vintage, and those pins skip unless the archive
is configured and `QT_ARCHIVE_RUN=1`. Every other test in it runs everywhere.
That covers the committed half of the vintage, the members and holes files'
hashes and SPY's manifest line. On frames built by hand it holds membership
at t, the holding month of a stock that stops, and the skip of a formation
with no positive low-group beta. On the committed members file it holds the
survivor gap and how the exclusions that read t + 1 split. It holds what the
write-up measured after the run too. `TestWhatThePostCounted` reads committed
files and runs everywhere: the row check's failures by year and by outcome,
the share of member rows still in the last schedule, each schedule's carry,
and the stocks the earlier test's close at the next month-end left out on
Chan's file. `TestWhatThePostMeasured` reads the archive: the upper bound on
the levered advantage, the unlevered fifths' gap, the formations with the
lowest low-fifth betas, December 2024, April 2025 and March 2020 against
their ruin lines, March 2026's levered loss, and the gap with one or two
months dropped. The blog post about it is the exception, and what it says that
nothing here asserts is listed below.

[tests/test_usdcad_holdout.py](tests/test_usdcad_holdout.py) does it for
Example 2.5's rule on USD/CAD after 2012. It pins H1's cumulative P&L and
its verdict, each of H3 to H7's statistics with whether its registered
prediction matched, H6's random-walk band, the drawdown, the Sharpe ratio,
the largest position, the shares long and short, the window and its weekday
gaps, and the report's lines. The vintage is committed, so every pin runs
everywhere, CI included. On synthetic rows it holds each refusal of the run,
the window, and the slicing that makes the positions `market_value(...)[114:-1]`
earn `pnl[115:]`. On stubbed calls it holds that each refusal of the command
prints one line and that the key reaches none. `TestWhatThePostMeasured`
holds what the write-up measured after the run: the closes across the
drawdown and their rise, the days of the fall held short, the day the P&L
regains its 2013 high, the largest position's day, and H6's distance from
the band's mean and the band's half-width. The blog post about it is the
exception, and what it says that nothing here asserts is listed below.
[tests/test_fetch_alphavantage.py](tests/test_fetch_alphavantage.py) holds
the fetch's refusals of a response on stubbed bodies.

All forty-seven replications reach a verdict in
[docs/replication-log.md](docs/replication-log.md), row by row. Entry 5 there
carries the fixed-income finding, which has no published number to reach a
verdict against, Entry 6 the cross rate's verdict, Entry 7 the equity
seasonals', Entry 8 the Khandani-Lo reversal's, Entry 9 the survivorship
toy's, Entry 10 the reversal at the open's, Entry 11 the commodity
seasonals', Entry 12 post-earnings drift's, Entry 13 the PCA factor model's,
Entry 14 the market and momentum factors', Entry 15 the calendar spreads',
Entry 16 Conditional Parameter Optimization's, Entry 17 cross-sectional
momentum's, Entry 18 buy on gap's, Entry 19 the reversal on the 2012
panel's, Entry 20 the leverage examples', Entry 21 Example 3.1's, Entry 22
the stationarity tests' on USD.CAD, Entry 23 the ETF cointegration
examples', Entry 24 Example 4.2's, Entry 25 Example 5.1's, Entry 26 Example
3.2's, Entry 27 the spot and roll returns', Entry 28 VX against ES's,
Entry 29 the Johansen tests' on GLD, GDX and USO, Entry 30 Example
5.2's, Entry 31 the crude oil rule's, Entry 32 the Kalman filter's on
EWA and EWC, Entry 33 TU momentum's, Entry 34 the crude oil calendar
spread's, Entry 35 the VX calendar spread's, Entry 36 the roll-return
rule's on TU, Entry 37 Example 1.1's hypothesis tests, Entry 38 the
trade of GLD against gold futures, Entry 39 the XLE against USO
trade's, Entry 40 the opening gap strategy's on FSTX, Entry 41 the
roll-return rule's on VX against ES, Entry 42 Example 7.4's own factors',
Entry 43 Chapter 8's leverage boxes', Entry 44 the finding on the reversal on
the S&P 600, which has no published number to reach a verdict against either,
Entry 45 the levered low-beta claim's, Entry 47 the VIX filter's on buy on
gap and on FSTX, Entry 49 the levered low-beta claim's on IVV's S&P 500
after the book, Entry 50 the finding on the reversal on the S&P 400
beside Chan's two files, which has no published number either, and Entry 51
Example 2.5's claim on USD/CAD after 2012.
Entry 46 carries the rerun of Example 7.2 described above, which
chases no published figure and so reaches no verdict. Entry 48 carries the
levered low-beta rule at leverage a broker would lend, which is exploratory
and, like Entry 46, reaches no verdict. Entry 52 sets Example 7.7 beside the
Open Source Asset Pricing project's `MomSeasonShort`, which is exploratory and
reaches no verdict either.

A vintage is recorded rather than dropped in. `src/chan/vintage.py` writes a
series and its provenance together and refuses to overwrite either, and
[data/vintages.jsonl](data/vintages.jsonl) holds one line per committed series,
naming its vendor, symbol, price basis, span, date, row count and sha256.
[data/README.md](data/README.md) says the same in prose, next to the files.

The other side reads it back. `src/chan/series.py` resolves a vintage through
the manifest rather than by building a filename, recomputes its sha256 from the
bytes it is about to parse, and stops the run when they disagree. So a
replication names the file it read, and the default GLD/GDX run says its two
legs were downloaded 72 days apart.

Bytes that verify are still not a series it is safe to compute across. The same
module reads each committed price series against itself day over day and reports any
day it changed scale rather than price, and a run whose window spans one stops
instead of printing a number. Among the single-series vintages, two days of
`ko_chan.csv` are reported and nothing computes across them, because the KO/PEP
replication reads the intersection with `pep_chan.csv` and that starts in 1977.
The columns lifted from Chan's stock, ETF and strip files, below, report 171 more. In
his stock files most are real moves in single stocks, and the 58 in his ETF
file fall in eight leveraged and inverse funds in 2008 and 2009. His
continuous futures saves report 126 more, all in the ZB and ZF bond columns no
script of his reads, and his `VIX.csv` reports one, a real move on 2007-02-27.
Each replication that reads one of these files decides whether to call the
guard, and one that does not says why in its own docstring. The
Khandani-Lo reversal's 2006 window spans one of the stock days, WYN's restart
on 2006-08-01, and prints a number anyway, because
it reads a panel rather than one series and its rule never weights a return
that is not finite. `chan.khandani_lo`'s docstring says why the guard is not
called there. Example 3.8's rule A, Chan's Python notebook, fills the gap and
reads it as a return of 121.5 on the closes and 127.65 on the opens, because
that is what his notebook computed, and the entry reports what the figures are
without it. The reversal on the S&P 600 file does not call the guard either.
Over each stock's own closes the guard refuses its 2006 window on BCSI's
2006-02-06 and SCUR's 2006-07-12. Before the run both were classified as
earnings warnings recorded at the prices that traded, so the run keeps them
and Entry 44 says what each was. The reversal on the S&P 400 does not call it
either. The five days flagged on its archive panels were classified before the
run, one kept and four excluded, and Entry 50 says what each was. The
reversal on the 2012 panel does not call it. Its 2007 to 2011 window spans all
30 of that file's flagged days, Chan's script computes across them, and his
figures reproduce only with them in. Most read as the 2008 crisis, and CAH's
2009-09-02 does not. The
PCA factor model does not call it. Its printouts forward-fill PMC's 851-day
gap in the S&P 600 file into one day's return of 1.8654, because Chan's
programs do, and its entry reports every figure without PMC beside them.
Example 7.6's revised Python forward-fills the same gap at year-end, so its
2007 ranking reads PMC as a return of 1.3056 and holds it short in January
2008. That is Chan's program as printed, and Entry 7 says what the fill moves.
Cross-sectional momentum does not call the guard either. It flags ETFC's
2007-11-12 inside the 2007 window and 29 stock-days inside 2008 and 2009, so it would
refuse both windows the book prints, and Chan's script ran across them as they
stand. Examples 3.1 and 3.2 are one case of a run that calls the guard. They
read GLD and USO over the ETF file's whole span, where neither leg carries a
flagged day, so nothing is refused.
[tests/test_scale_breaks.py](tests/test_scale_breaks.py) is the authority for
the bound and for what the committed vintages carry.

A series checked against itself cannot show a vendor rewriting history between
two downloads, so the same module also sets two vintages of one series against
each other on the days both hold. SPY's raw close as Chan saved it in 2008 and
as yfinance returned it in 2026 agree to the half cent on all but 2 of 3,758
shared days, and
[tests/test_vintage_overlap.py](tests/test_vintage_overlap.py) pins both the
agreement and the two days.

One vintage, FRED's three-month Treasury-bill series, holds a rate rather than
a price, so the scale-break check skips it.
[src/chan/bill_rates.py](src/chan/bill_rates.py) reads it and averages it over
a window of months, and [tests/test_bill_rates.py](tests/test_bill_rates.py)
pins what it gives.

Twelve vintages hold NYMEX futures settlement prices as the US Energy
Information Administration publishes them: contracts 1 to 4 of RBOB gasoline,
of the New York Harbor gasoline contract it replaced, and of Henry Hub natural
gas. `src/chan/commodity_seasonals.py` reads five of them for
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19), and the
issue records the owner's decision to commit all twelve.
`src/chan/stationary_candidates.py` reads eight, every natural gas and RBOB
file, for [issue 137](https://github.com/l3a0/quantitative-trading/issues/137).
`src/chan/futures.py` holds the exchange calendar and the expiry rules both
read.
[data/README.md](data/README.md) says what each file holds.

Six of Chan's own files are cross-sections rather than series. Five hold
prices.

1. The S&P 500 as it stood on 2007-11-23.
2. The S&P 600 in a save named for 2008-01-14.
3. The S&P 600 in a later save named for 2008-01-31.
4. The S&P 500 as he held it on 2012-04-24.
5. The 67 ETFs his second book's examples read, as he saved them on
   2012-04-10.

The sixth holds his earnings-announcement flags for the 497 stocks of the 2012 S&P
500 file, a 0 or 1 for each day. Each is committed as one vintage per stock or
ETF, 2,761 between them, written by
`src/chan/mat_columns.py` under a directory per file. A price file's member
holds its close, high, low, open and volume, and a flag file's member holds its
flag for every day of the file's calendar.
`chan.series.load_panel` reads a whole file back as one date-by-symbol frame
and checks every member's bytes on the way.
[Issue 88](https://github.com/l3a0/quantitative-trading/issues/88) is where that
shape was decided, and
[data/README.md](data/README.md) says what was measured on each file. The Khandani-Lo reversal,
for one, reads the 2007 S&P 500 file's closes for Example 3.7 and its opens
for Example 3.8. Example 3.1 reads GLD's and USO's closes from the ETF file,
for [issue 340](https://github.com/l3a0/quantitative-trading/issues/340), and
is the first run to read it. The lift for
[issue 299](https://github.com/l3a0/quantitative-trading/issues/299) commits
it for *Algorithmic Trading*'s cointegration, mean-reversion and Kalman filter
examples on EWA, EWC, IGE, GLD and USO, and for the SPY leg of Example 4.2.

Nine more of Chan's MATLAB files hold futures from *Algorithmic Trading*.
Eight are per-contract strips, each holding one column per futures contract
on one commodity. A contract's column holds its settlement, the price the
exchange publishes for it each day it trades. The strips are named by the
exchange's code for the commodity: BR, C2, CL in two saves, HG, HO2, TU and
VX. The ninth is his gold series sampled at 16:00. Each contract is committed
as one vintage, under a symbol joining the code to the delivery month, such
as `CL-2007F` for January 2007 crude oil, and `src/chan/mat_columns.py` writes
them too.
[Issue 300](https://github.com/l3a0/quantitative-trading/issues/300) is where
that shape was decided. The spot and roll returns of Example 5.3 read five of
them, BR, C2, CL, HG and TU, through `chan.roll_returns`, for
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347), and
later replications read their strips through the same reader. No replication
reads HO2, the CL save named for 2012-05-02 or the gold series yet.

Seven more of Chan's files are committed as his 2018 Python port's zip shipped
them, under `data/pythoncodesanddata/`, for
[issue 301](https://github.com/l3a0/quantitative-trading/issues/301). They are
USD.CAD's one-minute bars, the daily closes of USD.CAD, AUD.USD and AUD.CAD,
the monthly AUD and CAD interest rates, and the AUD.CAD returns his Example 5.1
saved. `chan.series.load_minute_close` reads the minute file's 16:59 bar as
the daily close his Examples 2.1 to 2.5 read, and the stationarity tests on
USD.CAD read it. `chan.series.load_port_close` reads the AUD.USD and USD.CAD
daily files and `chan.series.load_returns` reads the saved returns, all three
for Example 5.1. Example 5.2 reads the AUD.CAD daily file through
`chan.series.load_port_close` too, and the two rate files through
`chan.series.load_rates`, so a replication reads each of the seven.

Four more of his MATLAB files hold his continuous futures series, four saves of one file named
for 2012-05-04, 2012-05-07, 2012-05-11 and 2012-05-17. Each symbol there is a
series rolled from contract to contract and shifted at each roll, priced on
its own calendar, and each is one vintage with all five fields, as a stock
is. His `VIX.csv` is committed beside them as one vintage under the vendor
`chan-csv`. Those five files hold 209 vintages, and
[issue 313](https://github.com/l3a0/quantitative-trading/issues/313) carries
their shape. VX against ES, for one, reads VX and ES from the 2012-05-07 and
2012-05-17 saves for
[issue 350](https://github.com/l3a0/quantitative-trading/issues/350), and its
tests read the 2012-05-11 save too.

IJR's holdings at every year-end from 2007 to 2025, and IVV's at every
quarter-end from 2008-12-31 to 2026-06-30 but one, are committed under
[research/filings](research/filings/README.md), read from the schedules
iShares Trust files with the SEC rather than from a vendor. A filing is never
restated, so each file is pinned by the filing's accession number rather than
kept as a vintage, and that directory's README says why.
`src/chan/fund_holdings.py` reads the filings.
[Issue 361](https://github.com/l3a0/quantitative-trading/issues/361) carries
IJR's shape and
[issue 372](https://github.com/l3a0/quantitative-trading/issues/372) carries
IVV's. Beside IJR's, `research/filings/ijr/members.csv` maps each member to the
ticker Alpha Vantage files it under and records whether that series' close
agrees with the filing, which
[issue 332](https://github.com/l3a0/quantitative-trading/issues/332) built and
[tests/test_sp600_panel.py](tests/test_sp600_panel.py) pins.
`research/filings/ivv/members.csv` does the same for IVV's quarter-ends, and the
report counts which members Example 7.7 can rank at each month-end from
December 2008 to August 2026, which
[issue 373](https://github.com/l3a0/quantitative-trading/issues/373) built and
[tests/test_sp500_panel.py](tests/test_sp500_panel.py) pins. The panel covers
between 364 and 501 of the 499 to 507 members a month-end holds, the fewest in
September 2012.
IJH's 2007-12-31 holdings sit in `research/filings/ijh/2007-12-31.csv`, and
`research/filings/ijh/members.csv` maps and checks them the same way.
`research/filings/ijr/members_2007-12-31.csv` does the same for all of IJR's
holdings that day, as the control beside them, which
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303) built and
[tests/test_sp400_panel.py](tests/test_sp400_panel.py) pins.
`chan.equity_seasonals` runs Example 7.6 on the members of
IJR's 2025-12-31 filing as a replication, and on the members of every
year-end from 2008 to 2025 through that members file as a registered
experiment.

The same directory holds a second record, `research/filings/earnings/`, the
Item 2.02 8-Ks that EDGAR accepted for Chan's 497 stocks from 2010-12-01 to
2012-04-24, which
[issue 251](https://github.com/l3a0/quantitative-trading/issues/251) built
and `src/chan/earnings_filings.py` reads. A ticker table beside the index maps
each 2012 ticker to the SEC's CIK and to an archive series and records the
check each mapping passed, and
[tests/test_earnings_filings.py](tests/test_earnings_filings.py) pins it.
`chan.pead_rerun` reads it to rerun Example 7.2 on that calendar.

The coin flip reaches none of that. It records no vintage and reads no series,
which is why it could ship before the recorder existed. The leverage examples
read none either.

The estimators behind those numbers are not in this repo. Least squares, the
Augmented Dickey-Fuller statistic, the half-life, the MacKinnon critical values
and the Newey-West significance block live in
[ithildincore](https://github.com/l3a0/ithildin-core), shared with
the sibling repo because both had the same copy. The dependency is a direct URL
at an exact commit, `uv.lock` records it, and CI syncs with `--locked` so the
two cannot drift apart unnoticed. All three parts earn their place, and
[docs/design.md](docs/design.md) says which failure each one closes. Two
toolbox forms of the Dickey-Fuller test are the exception and live in
`src/chan`, because each reproduces a figure the shared one cannot. So do the
Hurst exponent and the variance ratio test Chan's scripts call, which the
shared package does not carry. The design doc says why none of them moved.
[tests/test_ithildincore_contract.py](tests/test_ithildincore_contract.py) is what
tells a dependency change apart from a vintage change, since its cases read no
vintage. [docs/design.md](docs/design.md) carries why the pin is not optional,
and what it does not buy.

The tracker is the source of truth for what each deliverable is and for what
each waits on. Milestones do the grouping: the experiments by the chapter of
the book they come from, and the machinery they run on separately, because a
vintage recorder belongs to no chapter.

The deliverables are the book's own worked examples, and the tracker counts
them rather than this file. The `replication` label is the set, `blocked-on-data`
marks the ones whose series is not free, and most of the rest sit in Chapter 7,
the chapter Chan calls the special topics chapter at Kindle location 2735. This
paragraph carried those three figures until 2026-09-18 and two of them were
already wrong, because nothing fails when an issue is filed and a sentence here
is not.

## Running a replication

```bash
uv run python -m chan.pair_cointegration --ch3
```

Chan's Chapter 3 run, on the first 252 trading days. `--ch7` runs the full
Chapter 7 window and `--ko-pep` runs the counter-example. Each of the three
names the window, the price basis, and the specification every number came
from, so no figure in the report is separable from the vintage that produced
it.

`--selftest` is the odd one out. It reads no vintage and reports no window,
because it checks the arithmetic against synthetic series whose answers are
known in advance.

The coin-flip gamble is its own command, and it reads nothing:

```bash
uv run python -m chan.coin_flip_growth
```

It prints the figures the book prints, the two averages in one unit so their
signs can be compared, a seeded run with the standard error beside it, and the
capital those two rates compound into over four horizons. The ensemble side
compounds `ensemble_log_growth` and the time-average side compounds
`growth_exact`, the exact discrete rate rather than the continuous
approximation the book prints, and the report says so beneath the table. The
rates themselves are constants, so the divergence is visible in the capital and
nowhere else.
`--rounds`, `--paths` and `--seed` move the run off its pinned size. The report
prints the standard error beside the estimate either way, and says outright
when a size is too small to resolve the sign, which is a line a reader sees
rather than an exception, because at that size nothing has failed.

The Kelly run reads one series, or two under `--chan`, and takes a window:

```bash
uv run python -m chan.kelly_leverage
```

The default is Chan's own span, 1993-01-29 to 2007-12-28, read on a 2026
download and held fixed so the vintage is the only thing that differs from his.
`--chan` reads his own workbook instead:

```bash
uv run python -m chan.kelly_leverage --chan
```

That run reproduces his printed figures and then prints the two vintages side
by side over the same window, with the days each one holds and the share of the
gap in the mean that its ten largest days and SPY's dividend months carry.
`--start` and `--end` move the window, and the report drops the published
column on any other window rather than printing a comparison against figures
that came from his. `--dated` picks a vintage by its date, which matters the
day a second adjusted SPY download arrives. Left out, it means the 2026 download, or no
date under `--chan`, which finds his adjusted workbook column. `--risk-free` moves
the book's 4 percent constant, and on Chan's window the report then says the
gap column measures the rate as well as anything else.

It prints the moments against the book's, the worked example on this vintage's
leverage beside the book's own rounded 2.528, the Black Monday comparison with
Chan's constant kept apart from the worst day SPY actually holds, and the
time-scale check. A window whose mean excess return is negative makes Kelly
recommend a short, and that arrives as a line saying what it means rather than
as an exception, because nothing has failed.

The risk parity run reads SPY and AGG by default and takes no window, because
its windows were declared in advance:

```bash
uv run python -m chan.risk_parity
```

It prints the three windows
[issue 15](https://github.com/l3a0/quantitative-trading/issues/15) declared
before any number existed, every run, so a window cannot be reported alone.
The boundary between the two sub-windows is the Federal Reserve's first
increase of the 2022 tightening cycle, 2022-03-16, which is a dated external
event rather than anything read from the series under test. `--start` and
`--end` add a fourth window, reported as off the reproduction and carrying no
published counterpart, and `--risk-free` moves Chan's 4 percent constant.
`--stock IWB` swaps the equity leg for IWB, which tracks the Russell 1000 index
Qian read, keeps the same AGG vintage, and then reads SPY again to print what
the substitution cost under the rule
[issue 160](https://github.com/l3a0/quantitative-trading/issues/160) declared
before any IWB number existed. SPY stays the default, because it is the leg
[issue 15](https://github.com/l3a0/quantitative-trading/issues/15) fixed in
writing.

Each window reports both legs' volatilities against the ratio Qian's 23-77
implies, the risk each leg contributes under 60/40 and under risk parity, the
leverage that matches 60/40's volatility, and the Sharpe ranking as a measured
difference with a robust t-statistic beside it. A window whose robust t cannot
resolve the ranking says so in a line rather than stopping the run, because a
sample that cannot settle a sign has not failed at anything. One of the two
sub-windows is in that position.

Chan's three stationary candidates share one command, and none takes a
window:

```bash
uv run python -m chan.stationary_candidates
```

With no argument it runs all three, and `fixed-income`, `cross-rate` or
`calendar-spread` runs one. The
fixed-income candidate prints the full-span test in both orientations, the
residual check at one lag beside the first lag count whose residuals pass, and
the rolling scan each way round. The cross rate prints the same three for the
log of `CADAUD=X` over its test window, then the verdict and the criterion it
was read against. The calendar spreads print, for each commodity, how many pairs
reject in both orientations, the corrected null's bar and the verdict it gives,
the declared null's bar and verdict beside them, and the rows that describe the
batch and decide nothing. Both simulations run each time, and the
command takes about seven seconds. There is no `--start` or `--end`, because a
window option is what would let a reader pick one that rejects, and each issue
declared exactly one window. `--dated` names which `CADAUD=X` download to read,
defaults to the one the suite pins, and is refused when the candidate named is
one of the other two.

Chan's equity seasonals are one command. On Chan's files it takes no option,
and two options run Example 7.6 on IJR's members instead:

```bash
uv run python -m chan.equity_seasonals
```

It reads the S&P 600 file Chan's Example 7.6 loads and his S&P 500 file, and
prints every figure each printout of Examples 7.6 and 7.7 reaches, beside the
panel it came from. A January a file ends before would print as not computable
with the date the file ends, and the 2002 split of the revised Python prints
under a line saying it carries no verdict. Last come both readings of p. 180's
most recent five years under the revised MATLAB's and Python's rules, with the
verdict printed beside the MATLAB's rerun alone.

`--survivors` runs Example 7.6 instead on the 603 companies IJR held at
2025-12-31, from January 2009 to January 2026. It reads their Alpha Vantage
closes from the owner's archive, so it needs the archive's path, set as
Example 7.1's command sets it:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.equity_seasonals --survivors
```

It prints the members with no series and the year-ends each member misses,
then each January before costs with its ranked, long and short counts and how
many ranked members have no exit close. Then come the mean, the standard
deviation, the one-sided t-test, the smallest mean the test detects, the mean
after costs, and the reading. The run is survivor-only, so the reading goes one
way only, which the output says beside it. A machine with no archive gets one
line naming both ways to set it, and so does every other refusal.

`--point-in-time` runs Example 7.6 over the same Januaries on the members IJR
held at each year-end, as `research/filings/ijr/members.csv` records them, and
then Example 7.7 on the members IVV held each month, as
`research/filings/ivv/members.csv` records them. It reads the same archive:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.equity_seasonals --point-in-time
```

Each year-end ranks only its covered members, with the tenth taken of the
whole index, and prints its January with the members missing and how many of
them threaten each tenth. A January with any threat prints as a low and a high
bound. Then come each series' test, its detectable mean and its mean after
costs, the verdict, and the survivor run's January less this one's.

Example 7.7's report follows, from January 2009 to September 2026 on the 817
`sp500` series in the same archive. It names the members file, the closes and
the calendar it read, how many series stop before their file's last row, and
each month's coverage by year. Under the revised MATLAB's rules it prints the
mean, the standard deviation, the one-sided t and p, the Newey-West t, the
annual return the test detects with 80% probability, and the verdict. The
revised Python's figures follow with no verdict. Then come the means on the
two masks that bracket each name that changed between schedules, the names
removed and added between each pair of schedules with the positions held on
them, the positions whose stock stopped inside the month held, and where
departing names fell, which it marks as descriptive only.

`--open-asset-pricing` sets Example 7.7 beside the Open Source Asset Pricing
project's `MomSeasonShort`, Heston and Sadka's own signal rebuilt from CRSP,
from the release `data/` holds. It needs the archive for its last part only:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.equity_seasonals --open-asset-pricing
```

It prints the project's mean and t over Heston and Sadka's 1965 to 2002
sample beside their printed figure, then before 2002 beside Chan's 13 percent
a year, and from 2002. Then, on Chan's file and on IVV's members, it prints
each side's mean, standard deviation and t over the months both hold, their
correlation, and their difference of means, raw and at the rule's scale. The
rule earns half the top tenth less the bottom and the project the whole of
it, which is why the second difference halves the project's mean. A machine
with no archive gets every figure but the IVV one, then one line saying why it
stopped. Entry 52 of the replication log carries the result, labelled
exploratory.

The three options cannot be given together.

Khandani and Lo's reversal reads Chan's S&P 500 file and takes no window,
because his script fixes both the file and the window:

```bash
uv run python -m chan.khandani_lo
```

It prints the panel in one line, the window and its day count, and each Sharpe
ratio beside the book's, naming which quirks of Chan's code each one keeps.
Khandani and Lo's own 4.47 is printed as a citation, since it was computed on a
universe this repo does not hold.

Its one option, `--open`, runs Example 3.8 on the same file's opens:

```bash
uv run python -m chan.khandani_lo --open
```

It prints both rules, Chan's notebook figures beside the rule that printed
them, "very positive" beside the rule the claim is read on, both verdicts, the
one-year bar, and the exploratory label.

The same rule on Chan's S&P 600 file takes no option, because the comparison
declared before it ran fixes both files, the window and the rule:

```bash
uv run python -m chan.khandani_lo_small_caps
```

It prints both files, the six pairs of figures with the S&P 600's beside the
S&P 500's and the gap, each before-cost gap's standard error and whether it is
beyond one year's noise, the declared reading, Khandani and Lo's 4.47 judged
against nothing, and the exploratory label.

The same rule on the S&P 400 reads IJH's 2007-12-31 holdings from the owner's
archive, beside Chan's two files and an S&P 600 control built the same way,
and takes no option either:

```bash
uv run python -m chan.khandani_lo_mid_caps
```

It prints the four panels, every figure for the S&P 500, S&P 400, S&P 600 and
the control with and without its exclusions, each step's standard error, the
control's gap to Chan's S&P 600 file, the order at each price, the declared
reading, and the exploratory label.

Chan's survivorship toy reads the two tables the book prints and takes no
option:

```bash
uv run python -m chan.survivorship_bias
```

It prints both portfolios' returns under equal capital beside the figures the
book prints, the equal-shares near miss, and the survivor-only return again
with NEOF's start price put on the basis of its 2001 reverse split. Its vintage
line reads `none, the book's printed tables`, and its window line names the
book's dates.

Chan's commodity seasonals read EIA's settlements and take no option:

```bash
uv run python -m chan.commodity_seasonals
```

It prints every year's trade for both contracts, with its dates, settlements
and the numbered file each price came from, then the counts the book prints
beside its own. A year whose trade date has no row in its file prints as
missing rather than moving to another day.

Post-earnings drift reads Chan's book-two S&P 500 file and his earnings flags,
and takes no option, because his script fixes the files, the window and the
rule:

```bash
uv run python -m chan.pead
```

It prints both sources in a line each, the window, the rule, the busiest day
beside the 30 Chan divides by, and each figure beside what `pead.m` and the
book print. It refuses to run if the two files name different stocks, because
the script pairs their columns by position.

Its rerun on EDGAR's calendar and the archive's prices takes no option either,
because the comparison was fixed on
[issue 251](https://github.com/l3a0/quantitative-trading/issues/251) before it
ran:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.pead_rerun
```

It prints each of the ten runs the issue fixed, with each run's mean return
per trade, the attribution of the change to the universe, the calendar, the
vendor and the price basis, the other comparisons the issue names, each
calendar's agreement with Chan's flags, and every stock left out of a universe
with the check it failed. Without an archive it runs the six runs that read only
committed files and says why the other four did not run.

The reversal on the 2012 panel runs both of *Algorithmic Trading*'s examples
at once, and takes no option, because `andrewlo_2007_2012.m` fixes the file,
the window and the rule:

```bash
uv run python -m chan.khandani_lo_book_two
```

It prints the panel, the window and the rule, then each of Chan's eight
figures beside what the run computed and a verdict, then the two rows that set
the first book's rule and this one on each other's data.

The PCA factor model runs every printout of Example 7.4 at once:

```bash
uv run python -m chan.pca_factor
```

It prints each printout's figures beside Chan's, the verdicts, what separates
the 2 percent from the 4, and every figure without PMC. It takes about a
minute, most of it the first edition's eigendecomposition on every day.

The market and momentum factors read Chan's S&P 500 file, his SPY column and
the bills, and take no option, because the issue fixed the construction and
the window before any return was computed:

```bash
uv run python -m chan.momentum_factor
```

It prints the three vintages, the window, the eligible stocks and the legs,
each factor's lag-1 autocorrelation beside the stocks' quartiles, a verdict per
factor, and the band beside them. It refuses to run if a month's winner or
loser leg is empty, and names the month.

Conditional Parameter Optimization, Example 7.1, reads Alpha Vantage's
one-minute GLD and GDX bars from the owner's data archive, because the
vendor's terms grant personal, non-commercial use and the repo does not
republish them. `data/archive_vintages.jsonl`
records their hashes, and the run needs the archive's path, set as
`docs/design.md`'s Configuration section describes:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.cpo
```

It prints both vintages and their hashes, the span and the split, the
unconditional cell, each arm's four figures beside Chan's with the gap, the
same figures net of 1 basis point a round trip, the verdict on Chan's claim,
and, added after the result was seen and deciding nothing, where his 1.947
sits among all 400 cells. It takes about five minutes. On a
machine with no archive it refuses, naming both ways to set one, and its pins
in `tests/test_cpo.py` skip unless `QT_ARCHIVE_RUN=1` asks for them. Run those
pins with `-n 0`, because a parallel run builds the run once for each of the
two test files that read it.

The fetch writes Alpha Vantage's daily closes for a list of symbols into the
owner's archive, one file per symbol, and records each one as a line of
`data/archive_vintages.jsonl` under a cross-section name. It reads the owner's
key from the environment of the run. One other command asks Alpha Vantage for
data with the same key, `python -m chan.usdcad_holdout fetch`, and it records
USD/CAD's daily closes in `data/` rather than in the archive:

```bash
ALPHAVANTAGE_API_KEY=... QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.fetch_alphavantage --cross-section sp600 --symbols symbols.txt
```

The symbols file holds one symbol per line. A rerun skips every symbol already
recorded, so a run that stopped resumes where it left off, and it never
overwrites a file the archive already holds. The run opens on a line naming
the archive and the manifest, each symbol it fetches or refuses prints one
line, and the run ends on a tally of recorded, already recorded, failed and not
reached.
Run it after the close, from the branch that will commit the lines, because
the lines are what a rerun reads.

The S&P 600 panel joins IJR's year-end members to those closes. `fetch` hands
every ticker in `research/filings/ijr/members.csv` to the fetch above, `check`
reads the archive and rewrites the file's check columns, and `report` reads
only committed tables:

```bash
QT_ARCHIVE_DIR=/path/to/archive zsh -i -c 'uv run python -m chan.sp600_panel fetch'
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp600_panel check
uv run python -m chan.sp600_panel report
```

The report prints one line per year-end from 2008 to 2025: its members, how
many the panel covers, the January stops, the misses by reason, and how many
missing members could change a tenth of Example 7.6's ranking. A line per
missing member follows, giving its reason and marking those that threaten a
tenth. `check` with no archive prints the archive's own one-line refusal.

The S&P 500 panel does the same for IVV's quarter-end members, into the
`sp500` cross-section, and its `fetch` hands IVV itself on too:

```bash
QT_ARCHIVE_DIR=/path/to/archive zsh -i -c 'uv run python -m chan.sp500_panel fetch'
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp500_panel check
uv run python -m chan.sp500_panel report
```

Its report prints one line per month-end from December 2008 to August 2026,
each carrying the schedule that sets the month, its members, how many the
panel covers, the stops, which are covered members whose series ends inside
the next month, and the misses by reason. A line per missing member
follows with its reason. `check` also writes `research/filings/ivv/holes.csv`,
which names every month-end a series' span covers with no row on it, so the
report can run with no archive.

The S&P 400 panel does the same for IJH's 2007-12-31 holdings, into the
`sp400` cross-section, and its control does it for all of IJR's holdings that
day. Each command takes `ijh` or `control`:

```bash
QT_ARCHIVE_DIR=/path/to/archive zsh -i -c 'uv run python -m chan.sp400_panel fetch ijh'
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp400_panel check ijh
uv run python -m chan.sp400_panel report ijh
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.sp400_panel history ijh
```

`report` reads only committed tables and prints each check's members and
value, then every member that did not pass. `history` reads the archive and
sorts each passing member by its 2006 rows, then lists those a run over 2006
leaves out.

Cross-sectional momentum reads Chan's 2012 S&P 500 file and takes no option,
because the issue fixed the rule, the windows and the readings before any
return was computed:

```bash
uv run python -m chan.cross_sectional_momentum
```

It prints the source, the three windows, the script's five figures beside its
comment and the book, then every declared reading's return and Sharpe ratio in
each window and whether it lands, and the verdicts on the book's −30 percent
and its claim about the years after 2009.

Buy on gap reads Chan's book-two S&P 500 file and takes no option, because
his script fixes the file, the window and the rule, and the issue fixed the
mirror's before any run:

```bash
uv run python -m chan.buy_on_gap
```

It prints the source, the window, both rules, how many positions each side
took, and each figure beside what `bog.m` and the book print.

Example 3.1 reads GLD and USO from Chan's book-two ETF file and takes no
option, because his three scripts fix the file, the lookback and the rule:

```bash
uv run python -m chan.price_spread
```

It prints the two vintages, the window, the rule, and each script's two
figures beside its comment and the book, then the ratio again with GLD and USO
swapped.

Example 3.2 reads the same two ETFs and takes no option, because
`bollinger.m` fixes the file, the lookback and both bands:

```bash
uv run python -m chan.bollinger
```

It prints the two vintages, the window, the rule, and the band's two figures
beside the script's comment and the book, then Example 3.1's linear rule on
the same spread for the book's comparison.

The leverage examples, Examples 8.1 and 8.2 of *Algorithmic Trading*, read
nothing and take no option, because the book fixes every input:

```bash
uv run python -m chan.kelly_allocation
```

It prints Example 8.1's two days of resizing, each Example 8.2 figure beside
the book's, the growth rate along the line Figure 8.1 plots, the line's
stationary point outside the cap, and the cap above which the second strategy
alone stops being best.

The stationarity tests on USD.CAD, Examples 2.1 to 2.5 of *Algorithmic
Trading*, read Chan's minute file and take no option, because his script fixes
the closes, every test's settings and the trade, and the issue fixed Example
2.5's claim before any P&L was computed:

```bash
uv run python -m chan.usdcad_mean_reversion
```

It prints the source, each test's figures beside the script's and the book's,
Example 2.5's lookback, cumulative P&L and drawdown, and the two rows reported
beside the script: `adfuller`'s statistic and the Python port's own Hurst
exponent.

How far that Hurst exponent moves by chance and by the day the sample starts is
a second run on the same closes, seeded so it gives the same numbers each time:

```bash
uv run python -m chan.usdcad_hurst_noise
```

It prints each estimator's mean and standard deviation on 40,000 Gaussian
random walks of 1,216 log prices and where the observed H falls among them. It
then prints both estimators with the first 0 to 10 closes dropped, beside
whether the script's other figures still land. It was designed after the miss was seen, so it is
exploratory.

Example 2.5's rule on USD/CAD after 2012 takes two commands. `fetch` records
Alpha Vantage's `FX_DAILY` closes as a vintage in `data/`, once, and refuses
when one is already recorded. It reads `ALPHAVANTAGE_API_KEY` from the
environment of the run. The owner's `~/.zshrc` exports it and a plain shell
does not read that file, hence the interactive `zsh`. `run` needs no key:

```bash
zsh -i -c 'uv run python -m chan.usdcad_holdout fetch'
uv run python -m chan.usdcad_holdout run
```

`run` takes no option, because
[issue 607](https://github.com/l3a0/quantitative-trading/issues/607) fixed
the window, the lookback of 115 and every prediction before any holdout close
was read. It prints the vintage, the warm-up, the traded days and their
weekday gaps, and each of H1 to H7 with its outcome and whether it landed as
registered. Then it prints the drawdown, the Sharpe ratio, the largest
position and the shares long and short, which decide nothing. Every refusal
of either command prints one line.

The ETF cointegration examples, Examples 2.6 to 2.8 of *Algorithmic Trading*,
take no option, because `cointegrationTests.m` fixes the file, the three ETFs
and every test:

```bash
uv run python -m chan.etf_cointegration
```

It prints the three vintages and the window, each figure the script prints
beside the computed one and a verdict, the first eigenvector beside Chan's with
its sign flipped, how many relations each Johansen statistic finds at each
level, and the rows beside the replication.

Example 4.2 of *Algorithmic Trading* takes no option either, because
`indexArb.m` fixes both files, the screen, the windows and the lookback:

```bash
uv run python -m chan.index_arbitrage
```

It prints the two vintages and both windows, each figure the script prints
beside the computed one and a verdict, how many relations each Johansen
statistic finds for the basket, and the rows beside the replication: the 480
stocks tested, the 17 skipped, a plain ADF test of each 2007 log series, and
the first day the strategy earns.

Example 5.1 of *Algorithmic Trading* takes no option either, because
`AUDCAD_unequal.m` fixes the two files, the training length and the lookback:

```bash
uv run python -m chan.aud_cad_johansen
```

It prints the three vintages and the test window, each figure the script
prints beside the computed one and a verdict, the book's rounder figures, how
far the 612 returns sit from Chan's saved ones, and the rows beside the
replication.

The spot and roll returns, Example 5.3 of *Algorithmic Trading*, take no
option, because `estimateFuturesReturns.m` fixes the method and the book names
the five strips:

```bash
uv run python -m chan.roll_returns
```

It prints the five strips' vintages, each strip's spot and roll returns beside
Table 5.1's, and then the roll return with maturity in months, the days each
fit covers and the month gaps between its contracts.

VX against ES takes no option, because the issue fixed the save, the window
and the band:

```bash
uv run python -m chan.vx_es
```

It prints the vintage, the calendar, the training and test spans, the four
figures beside the book's with a verdict, the diagnostics in a table, and the
position held into the test with each change after it.

The Johansen tests on GLD, GDX and USO take no option either, because the
issue fixed the windows, the three ETFs and the test before any statistic was
computed:

```bash
uv run python -m chan.gold_miners_oil
```

It prints the three vintages and each window, each claim's count of relations
at 99 percent and its verdict, every test's statistics against its critical
values, and the rows beside the replication.

Example 5.2 takes no option either, because `AUDCAD_daily.m` fixes
the files and the lookback:

```bash
uv run python -m chan.aud_cad_rollover
```

It prints the three vintages, the window and the days with no rate, each
figure the script and the book print beside the computed one and a verdict,
the annualised rollover against its criterion, and the rows beside the
replication.

The crude oil rule takes no option either, because `CL_rev.m` fixes the save,
the window and the two lookbacks:

```bash
uv run python -m chan.cl_reversal_momentum
```

It prints the vintage and the window, the two figures beside the script's and
the book's with a verdict, the positions, the script's other three rules and
the later save in a table, and the three rules on the four years before the
window.

The Kalman filter on EWA and EWC takes no option either, because
`KF_beta_EWA_EWC.m` fixes the file and both of the filter's constants:

```bash
uv run python -m chan.kalman_hedge
```

It prints the vintage, the rows, the filter's constants, both figures beside
the script's comment and the book with a verdict, the first position and the
run with no signal on the first two days, and the two findings with no verdict.

TU's momentum, Example 6.1 of *Algorithmic Trading*, takes no option either, because
`TU_mom.m` fixes the table, the lookback and the hold:

```bash
uv run python -m chan.tu_momentum
```

It prints the vintage, the 49-cell correlation table, each figure beside the
script's or the book's with a verdict, and then the six pairs the book calls
the best compromises, the script's 2009 window and the 2012-05-17 save.

The crude oil calendar spread, Example 5.4 of *Algorithmic Trading*, takes no
option, because the script fixes the strip, the window and the holding period:

```bash
uv run python -m chan.calendar_spread_reversion
```

It prints the vintage and the window, each figure the script's comment and the
book print beside the computed one with a verdict, the ADF statistic against
its criterion, and then the window a day later, the 61-day holding period and
the last day a pair is held.

The VX calendar spread of *Algorithmic Trading*'s Chapter 5 takes no option,
because the issue declared the strip, the window and every row before the
run:

```bash
uv run python -m chan.vx_calendar_spread
```

It prints the vintage and the window, the specification's ADF statistic, APR
and Sharpe ratio beside the book's claims with a verdict, then the four rows
declared beside it, B1 to B4. B3, the row that trades the held pair's ratio
with each pair held in turn, is then measured on the book's window, and each
row before October 2008. None of these carries a verdict.

TU momentum on the roll return takes no option either, because the issue
declared its threshold, its lag and its roll row:

```bash
uv run python -m chan.roll_momentum
```

It prints the strip's vintage, the three figures beside the book's with a
verdict, the three claims against Example 6.1's rule with their margins, and
the rows beside them, the 2012-05-11 save's among them.

Example 1.1's hypothesis tests on TU take no option either, because the issue
declared both seeds and every draw method before the run:

```bash
uv run python -m chan.tu_hypothesis_tests
```

It prints the vintage and the seeds, then the five rows beside the book's or
the script's figure. Rows 2 to 4 carry a landing band, and every row but row 5
carries a verdict. The three rows added after the scratch run come last, and
none of them carries a verdict.

Long GLD and short gold futures takes no option, because `GLD_GC.m` has no
parameter to set:

```bash
uv run python -m chan.gld_gc
```

It prints both legs' vintages and the days they share, the script's five
figures and the text's two beside the book's with a verdict, then the bill
rate over the window and the measurements of the GC series, none of which
carries a verdict.

The XLE against USO trade takes no option, because the script fixes both files,
the front window and the window:

```bash
uv run python -m chan.xle_uso_roll_return
```

It prints the two ETF vintages and the strip, the five figures beside the
script's comment with a verdict, the APR and the Sharpe ratio beside the
book's with a verdict, and how many days fall in contango, in backwardation
and with no ratio.

The opening gap strategy on FSTX takes no option, because the script fixes
the save, the margin and the window:

```bash
uv run python -m chan.opening_gap
```

It prints the vintage, both readings of the return line beside the script's
comment and the book's figures with a verdict, the drawdowns and the days
each side holds, and the literal reading on the 2012-05-11 and 2012-05-07
saves. It then prints the Python port's four figures beside the port's
comments with a verdict, and the days the port holds each side.

VX against ES on VX's roll return takes no option either, because the script
fixes its three files, its threshold, its cost and its test:

```bash
uv run python -m chan.vx_es_roll_return
```

It prints the strip, the VIX and ES vintages, and the vintage of VX's
continuous close. Loading ES checks that file against its checksum, since it
belongs to the same save, and only the fitted hedge uses it as data. Then it
prints the four figures of each rule beside the script's comment with a
verdict, the APR and the Sharpe ratio beside the book's with a verdict, the
fitted hedge's figures with no verdict, and how many of the test's days are
held, short, long and entered from flat.

Example 7.4's own factors take no option, because the issue fixed the
printout, the lookback, the factor count and the statistic before any factor
return was computed:

```bash
uv run python -m chan.pca_factor_momentum
```

It prints the vintage, the rule and the pairs, each factor's statistic beside
its percentile, same-sign share, Newey-West t, p-value and Benjamini-Hochberg
result, the stocks' quartiles, the intercept and the band, a verdict per
factor, and every figure again without PMC. It runs 752 decompositions with
PMC and 752 without.

Chapter 8's leverage boxes take no option either, because the seeds, the cap
and D are part of the declaration:

```bash
uv run python -m chan.monte_carlo_leverage
```

It prints the vintage and the seeds, every row beside the book's figure with
its band and a verdict, then the rows beside them, which carry none: the
fitted parameters, the CPPI location 3426 describes, and the script's lines on
the historical returns. It ends with the evidence on the book's 18.4. The run
takes under a minute, about half of it in the two searches for an optimum on each of 401 seeds.

The levered low-beta claim takes no option either, because the issue
registered the universe, the window and every rule:

```bash
uv run python -m chan.low_beta_leverage
```

It prints the three vintages, the verdict with every ruined month, and beside
it the growth, the Sharpe ratios, the realised betas, the Kelly reading's
Gaussian growth, the flagged stock-months and a row for every formation, none
of which decides anything.

The VIX filter takes no option either, because location 3509 fixes the
threshold and the two rules, and their scripts fix the files:

```bash
uv run python -m chan.vix_filter
```

It prints the three vintages, the days each calendar keeps once joined to
VIX's, and both rules' figures on the days kept beside the book's with a
verdict, FSTX under both signs. Then it prints the readings that miss beside
the book's figures, and the days kept, the days held, the unfiltered figures
and Welch's t, none of which carries a verdict.

The same rule at leverage a broker would lend takes no option either, because
the issue's plan fixed both ceilings and every rule before any capped number:

```bash
uv run python -m chan.low_beta_capped
```

It prints the three vintages and each ceiling's outcome with its gap, t, both
p-values and the detectable gap Y. Beside them it prints the growth, the mean leverage, the
months each ceiling binds, the realised beta, the break-even spread and the
worst month, none of which decides anything, then location 4700's caveat and
the five limits. Every line is exploratory.

The levered low-beta claim's run on IVV's S&P 500 takes no option
either, because
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526)
registered the panel's changes before it ran:

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.low_beta_holdout
```

It prints the same report, plus every skipped formation with both groups'
mean betas, the members, covered members and eligible stocks at each
formation, and the survivor gap. It reads the archive, so it refuses where
none is configured.

Chan's own archived GLD/GDX files have no CLI mode on purpose. They exist to
show that even his saved data misses his printed hedge, which is a claim about
a number rather than a run someone would repeat, so
`TestGldGdxChanArchive` is where it lives.

His SPY workbook gets `--chan` for the opposite reason. It reproduces every
figure he printed from a series, so reading it is the result rather than a
footnote to one, and it is the run that explains why the modern download
misses.

The residual check behind the lag setting has a figure of its own. It draws
what each ADF lag count leaves in the residuals on the Chapter 3 window, which
bears on which lag count the test is entitled to. The result is exploratory,
and Entry 1 of [docs/replication-log.md](docs/replication-log.md) embeds it
and says what it can support.
[blog/price-spread-mean-reversion.md](blog/price-spread-mean-reversion.md)
embeds it too. `TestResidualCheckChapter7` runs the same check
on the Chapter 7 window, which has no figure. `TestResidualCheck` pins the
numbers,
[src/chan/lag_residual_figure.py](src/chan/lag_residual_figure.py) draws them
from the committed vintages, and
[tests/test_lag_residual_figure.py](tests/test_lag_residual_figure.py) holds
that the picture shows them rather than its bytes:

```bash
uv run python -m chan.lag_residual_figure
```

## The write-up

[blog/gld-gdx-cointegration-lessons.md](blog/gld-gdx-cointegration-lessons.md)
is the human-readable account of the GLD/GDX replication: what the book
printed, what this repo computes, and what explains the gap.
[docs/gld-gdx-cointegration-lessons.html](docs/gld-gdx-cointegration-lessons.html)
is the same piece as a self-contained styled page, images inlined, which is
what gets published.

Its one figure, the rolling regime map, is drawn by
[src/chan/regime_figure.py](src/chan/regime_figure.py) from the committed
vintages:

```bash
uv run python -m chan.regime_figure
```

A redraw under another matplotlib release can produce the same picture in a
different file, because a PNG carries the matplotlib version that rendered it.
[tests/test_regime_figure.py](tests/test_regime_figure.py) therefore holds the
data behind the picture rather than its bytes, and asserts that the figure
plots the same scan `TestRollingRegime` computes.
[tests/test_figures_match_code.py](tests/test_figures_match_code.py) compares
the picture itself. It draws every committed PNG but `cpo_cells.png`, which
[tests/test_cpo_figures.py](tests/test_cpo_figures.py) compares, and checks
each fresh draw's decoded pixels exactly against the committed file. So a
figure whose code moved without a redraw fails the suite. The comparison runs
only on macOS arm64, where the committed figures are drawn. CI's Linux runner
draws some figures slightly differently, so CI skips it, and only a run on
the owner's machine catches a stale figure. The USD.CAD post's animated GIFs
are checked by
[tests/test_usdcad_tests_whiteboard.py](tests/test_usdcad_tests_whiteboard.py)
instead, which compares each fresh draw with the committed GIF byte for byte,
also only on macOS arm64 and only with the hand font they were drawn in. The
equity seasonals post's thirty GIFs are checked the same way by
[tests/test_equity_seasonals_whiteboard.py](tests/test_equity_seasonals_whiteboard.py),
which also fails on any GIF in the folder that neither module draws.

Both documents were written in the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, where
the replication was first built, and copied here byte for byte apart from three
changes. The links back to the implementation now name this repo. Chan's own
archive is quoted at 1.6395, which is what
[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py) pins,
rather than at the 1.6379 the sibling's copy gives it. The footer says the
committed engine is the statsmodels-backed port of the numpy-only test the
piece describes, because the piece describes an implementation this repo does
not hold.

The piece is a replication write-up, so it is exploratory by construction. It
says whether a published number reproduces and nothing about whether the trade
works today. An essay is not a verdict, so the verdicts live separately, in
[docs/replication-log.md](docs/replication-log.md). The two quote the same
computed figures, the essay at coarser granularity, so a re-pin moves both. They
agree on the two-run table's published figures too, since the essay's Chapter 3
row no longer gives the Chapter 7 hedge a second window. That correction landed
under [issue 27](https://github.com/l3a0/quantitative-trading/issues/27).

Seven of its figures are not pinned here, and they are worth knowing before
quoting any of them.

1. GDX has paid dividends for nineteen years since 2007. A fact about the
   fund's distribution history, not derivable from committed closes.
2. The hedge slipped "about two percent". Derived from 1.6766 and 1.6379,
   which are both pinned. The true figure is 2.31%.
3. Chan's Chapter 3 example "drops the last 60 days". The 252 reconciles and
   the 60 does not, and `example3_6_1.m` is not committed here.
4. A test statistic of −3.36 and a verdict of roughly 95% confidence on the
   Chapter 7 window. Both are Chan's, and neither is among the committed
   highlights. They live in a code comment.
5. The two-window table gives −3.18 for 2006 to 2008. That is Chan's printed
   figure, not a window this repo computes. The runs here give −3.45 and −3.09
   on the yfinance raw closes. On Chan's own files, a reconstruction of
   MATLAB's `cadf` gives −3.18156477 for the Chapter 3 window, his printed
   figure to all eight decimals, which row 12 of the replication log's
   Entry 1 records.
6. The piece dates the book to 2009 and names first-edition chapters. That is
   consistent rather than confused, and it now says so: every chapter, page and
   MATLAB filename this repo cites means the first edition unless stated. The
   revised edition puts both GLD/GDX printouts in one Chapter 7 example, which
   [docs/design.md](docs/design.md) works through.
7. The p-value of 0.005, rounded from the 0.004975 Chan's R run prints. It
   comes from Hansen's covariate-augmented Dickey-Fuller distribution, which
   assumes a stationary covariate the run did not have. Nothing here computes
   it, and the design doc's considered-and-rejected register says why.

Chan's −2.4 and −3.2, and the t-statistics, coefficients and hedge printed
beside them, are book figures. The code carries them as cited constants in
`TestChansPythonRun` and `TestChansRRunIsACovariateAugmentedDickeyFuller` and
asserts the computed figures against them. Every other number in the essay
traces to an assertion in
[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py).

[blog/price-spread-mean-reversion.md](blog/price-spread-mean-reversion.md) is a
second post, written for Substack and copied in as Markdown. It walks through
the Engle-Granger test, the ADF lag choice and the half-life on the same two
pairs. Two of its figures are not pinned here, and both are about R rather than
about any committed vintage.

1. `urca::ur.df` uses 1 lag unless told otherwise. That is a package default,
   and nothing here runs R.
2. `tseries::adf.test` uses 6 lags at 252 days. Its default is
   trunc((n − 1)^(1/3)), which gives 6 at n = 252, but that formula is the
   package's and no test here calls it.

Chan's printed −3.18 and the −3.380 his MATLAB reported are book figures. The
code carries them as cited constants, `BOOK_REF_TRAIN` and
`TestResidualCheckChapter7.MATLAB_5PCT`, rather than computing them. Every
other number in the post traces to an assertion in
[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py).

[blog/coin-toss-expected-value-vs-growth.md](blog/coin-toss-expected-value-vs-growth.md)
is a third post, about the coin-flip gamble rather than either pair. It draws
six lessons from Box 6.1 on expected value against the compound growth
rate of capital. The growth-maximising stake it quotes is pinned beside the
rest, in `TestTheStakeDecidesTheSign`. SPY's mean annual return of 11.23% and
its unlevered growth rate of 9.8%, Chan's at Kindle location 2869, are pinned
in [tests/test_kelly_leverage.py](tests/test_kelly_leverage.py) instead. The
code carries both as cited constants in `_PUBLISHED`, and
`test_every_published_figure_reproduces_at_the_precision_he_printed` asserts
that his own `example6_2.xls` rounds to each at the decimals he printed.
Three groups of its figures are not pinned here.

1. A stock moving 1% up or down each minute loses about half a basis point a
   minute. That is Chan's, at location 2822, and no test computes it.
2. One head and one tail leave 0.999 of the capital, a tenth of a percent
   lost every two rounds, and the worked \$1,110, \$111 and \$999 of that pair. The
   two-round table of \$810.00, \$999.00 and \$1,232.10 is the same kind, and
   so is Chan's own \$2,000 account that wins \$220 or loses \$200. All of it
   is arithmetic on the two pinned multipliers, 1.11 and 0.90, and no test
   asserts it.
3. The \$606 median path is a loss of 39%. The test that pins \$606 says so in
   its docstring and does not assert the percentage. Lesson 2's 6% gap at ten
   rounds is the same kind, the pinned ratio of 1.06 written as a percentage.
   So are Lesson 3's 1.43-percentage-point gap between SPY's two figures, the
   pinned 11.23% less the pinned 9.8%, Lesson 4's multiple of 3.11, the pinned
   \$3,111 divided by \$1,000, and Lesson 6's "a fifth of the growth", the
   pinned standard error of 1.05e-4 set against the growth of about 0.0005.

Every other number in the post traces to an assertion in
[tests/test_coin_flip_growth.py](tests/test_coin_flip_growth.py). The numbers
the figures print, including the two shares in the distribution figure's title
and the \$21,664 the fan's 200 paths average, trace to
[tests/test_coin_flip_figures.py](tests/test_coin_flip_figures.py). So does
the 0.013% of traders the distribution figure's caption leaves out, which no
figure prints.

The post carries five figures, drawn from the gamble's own arithmetic by
[src/chan/coin_flip_figures.py](src/chan/coin_flip_figures.py). They read no
vintage, so they redraw anywhere:

```bash
uv run python -m chan.coin_flip_figures
```

1. The probability of every balance 1,000 rounds can reach, with an inset
   showing the continuous approximation's balance falling between two of
   them, for Lessons 1 and 5.
2. A fan of 200 seeded capital paths with the ensemble mean and the median
   path, for Lesson 2.
3. Growth per round against the stake, for Lesson 4.
4. Histograms of the simulated time average from 200 seeds at two run sizes,
   where the small run gets the sign wrong on 56 of them and the large run on
   none, for Lesson 6.
5. Two estimates of the ensemble growth from each of 20 seeds, where
   averaging final wealth reads low on every seed, for Lesson 6.

The test file holds what each figure draws rather than its bytes, for the
reason given above for the regime map.

[blog/kelly-leverage-on-spy.md](blog/kelly-leverage-on-spy.md) is a fourth
post, about Example 6.2's Kelly leverage on SPY. It draws seven lessons,
numbered here as the post numbers them. Lesson 6 comes from the growth formula
and the other six from Entry 3 of the replication log.

1. The gap from Chan's figures, which is gone on his own `example6_2.xls` and
   sits on ten days on or beside SPY's quarterly ex-dividend dates.
2. The specification.
3. Rebalancing at a constant leverage.
4. The stress test's threshold, and the price series that reverses it.
5. The window.
6. Overbetting past the Kelly leverage.
7. The return frequency.

Two groups of its figures are not pinned here.

1. Chan's inputs: the 4% risk-free rate, the \$100,000 of equity and 10% fall
   of the worked example, and the 20.47% Black Monday loss and 20% tolerance of
   the stress test. The code carries them as cited constants and computes none
   of them.
2. Arithmetic that no test asserts: the 99% a 10% loss and a 10% gain leave,
   with their variance of 0.01, half of it 0.5% a period and 1% over two, the
   1.43% volatility drag, the 6.98% half-Kelly adds above the 4% rate, the
   9.30% that `S²/2` adds, the 0.60 margin above the 1.954 threshold, the 7.72
   spread between the bear and bull windows, the variance of 0.0286 and the
   factor of about 35 it multiplies an error in the mean by, the worst SPY day
   being about a third of Black Monday, and twice Kelly carrying about five
   times SPY's swings. The 43 to 47% that monthly sampling adds on the 2026
   download is held by a test only as a band of 42 to 48%.

Every other number in the post traces to an assertion in
[tests/test_kelly_leverage.py](tests/test_kelly_leverage.py). Three groups of
those are worth naming, because each reads Chan's own workbook.

1. Chan's eight printed figures in the table: the 11.23% mean, 16.91% standard
   deviation, 7.231% excess return, 0.4275 Sharpe ratio, 2.528 leverage,
   13.14% and 9.8% growth rates and 1.26 half-Kelly. The code carries them as
   cited constants. `test_every_published_figure_reproduces_at_the_precision_he_printed`
   asserts that his workbook's figures round to each of them at the decimals
   he printed, which is what the table's middle column shows.
2. Every other figure the post quotes from the workbook's adjusted column, from
   its 3,758 days to the \$252,775.87 its unrounded leverage buys. That
   includes the 43 to 47% that monthly sampling adds, which a test asserts as
   written on this column.
3. The figures from its as-traded column: the leverage of 1.9341, the 0.59 it
   sits below the adjusted leverage, the 1.68 points between the two columns'
   mean returns, the 0.020 by which it misses the threshold and its half-Kelly
   of 0.9670.
   `TestThePriceBasisOnHisOwnWorkbook` holds them.

The numbers read off the growth formula trace to
[tests/test_kelly_figures.py](tests/test_kelly_figures.py) instead. They include the
10.98% half-Kelly keeps and the 5.10 of twice Kelly, which the figure prints,
and the 5.60 at which growth reaches zero and the 5.43% the bull window's 4.90
earns on Chan's window, which it does not.

Its one figure, growth against leverage on Chan's window, is drawn from the
committed SPY vintage by [src/chan/kelly_figures.py](src/chan/kelly_figures.py):

```bash
uv run python -m chan.kelly_figures
```

The test file holds what it draws rather than its bytes, for the reason given
above for the regime map.

[blog/risk-parity-against-60-40.md](blog/risk-parity-against-60-40.md) is a
fifth post, about Qian's risk parity against 60/40, which Chan reports at
Kindle location 4684. It draws six lessons from Entry 4 of the replication log:
the close numbers and the failed claim, bonds earning too little per unit of
risk beside stocks, the volatility ratio and correlation Qian's two figures
encode, the cash rate at which the ranking ties, the weights judged on a window
they did not see, and the inputs moving between the two windows. Two groups
of its figures are not pinned here.

1. Published figures. Chan's 23-77 and 1.8 and his 4% rate, which the code
   carries as cited constants. From Qian's paper, committed at
   [research/papers](research/papers/README.md): the 1983 to 2004 sample, the
   15.1% and 4.6% volatilities, the 0.2 correlation, the 93% risk share, the
   Sharpe ratios of 0.55, 0.80, 0.67 and 0.87, the bond index's 3.7% a year
   above Treasury bills, the 2 points a year his levered portfolio beat 60/40
   by, his 60/40 volatility of 9.6%, and the condition under which his paper
   says risk parity is mean-variance optimal. The Federal Reserve's near-zero
   policy rate from December 2008 to December 2015 and from March 2020 to March
   2022 is a public record rather than anything committed here. The 15-month
   overlap of the two samples comes from Entry 4.
2. Arithmetic that no test asserts: stocks' term in 60/40's variance being
   about 29 times bonds', the \$43 of SPY, \$155 of AGG and \$98 borrowed per
   \$100 of equity, risk parity being about half as volatile as 60/40 before
   leverage, the 0.98 points a year each point off the rate is worth, risk
   parity's Sharpe ratio moving about twice as far as 60/40's per point, the
   2.5 points it takes to close the gap, the 8.36% and −0.91% a year above
   cash, the 1.11%, 2.20% and 4.65% the portfolios earn above cash, the 0.87
   and 0.67 that Lesson 2's arithmetic reproduces from Qian's inputs, AGG's
   Sharpe ratio of about −0.46 against SPY's 0.66 in the later period, the
   whole-period Sharpe ratios of 0.18 and 0.25 that the earlier and later
   periods' weights would give risk parity, and the 0.44 of the 0.98
   difference in bonds' Sharpe ratio that the cash rate accounts for.

The bill-rate averages the post quotes, 1.74% from October 2003 to August
2026, 1.17% before the 2022 rise and 4.18% after it, and the 108 months under
0.25% behind its nine near-zero years, trace to
[tests/test_bill_rates.py](tests/test_bill_rates.py), which reads them from
the committed TB3MS vintage. On Qian's weights, the 20% and 8% rises in risk
parity's and 60/40's variance as the correlation goes from 0 to 0.2, and the
fall in leverage from 1.88 to 1.78, trace to
`test_a_higher_correlation_needs_less_leverage_on_his_weights` in
[tests/test_risk_parity.py](tests/test_risk_parity.py). The multipliers
0.71, 0.98 and 0.18 that Lesson 2 puts on the two funds' Sharpe ratios trace
to `test_the_multipliers_lesson_2_writes_the_hurdle_from` in the same file. So
do the 0.525 and 0.276 in the inequality that sets the hurdle, which come from
subtracting one portfolio's multipliers from the other's. At the 1.17%
average, that file also pins risk parity's lead of about 0.13 in the earlier
period and its t-statistic of +1.12.

Every other number in the post traces to an assertion in
[tests/test_risk_parity.py](tests/test_risk_parity.py), including the rates of
1.50%, 2.45% and −4.43% at which the two Sharpe ratios tie and the full span's
t-statistic of −2 at 3.80% and +1.30 at zero, the later period's −2 at 3.25%,
and the 0.38 gap its weights would leave if computed inside it. It also holds
the hurdle bonds' Sharpe ratio has to clear, about 0.53 over the whole period
and about 0.7 in the later period, and AGG's 0.46 and −0.39 times SPY's
Sharpe ratio at the 1.74% bill average and at 4%. The IWB figures in "What
this replication cannot say" trace to `TestIWBInPlaceOfSPY` in the same file,
which reads `yfinance_iwb_adjusted_2000-05-19_2026-10-02_dl2026-10-03.csv`
against the same AGG vintage. That covers the May 2000 start of IWB's history
and its 3 October 2026 download date, its 18.47% volatility and 3.58
volatility ratio, its 21.9% stock weight and 1.98 leverage, and the Sharpe
ratios of 0.41 and 0.20 at 4% with their gap of 0.22 and t-statistic of
−2.16. It also covers the tie at 1.51%, which a separate assertion checks
prints as 1.51, the gap of 0.02 and t-statistic of −0.21 at the bill average,
and the changes from swapping SPY for IWB, −0.0001, −0.0008 and +0.0105,
with their t-statistics of +0.29, +0.06 and +0.98. What its seven figures draw
traces to [tests/test_risk_parity_figures.py](tests/test_risk_parity_figures.py).
That includes the Sharpe ratios of 0.61 for 60/40 and 0.59 for risk parity at
the 1.74% bill average, the gap of about 0.02 between them and its t-statistic
of −0.21, which the second figure draws. The third draws the hurdle of about
two-thirds at Qian's inputs, his bonds' 1.45 times stocks', and the funds'
Sharpe ratios of 0.45 for SPY and −0.18 for AGG at 4% and of 0.57 and 0.26 at
the 1.74% bill average. The fourth draws the volatility ratio of about 3.3 in
Qian's paper, with the 3.24 to 3.33 its rounding allows, beside 3.59, 3.87 and
2.76 on SPY and AGG, and the leverage curve on each set of weights and on the
two ends of 23-77's rounding. The fifth draws the Sharpe gap across cash rates
from 0% to 5%, including risk parity's lead of 0.13 at a zero rate, and checks
that every point it draws lies on one straight line. The sixth draws the Sharpe
ratios over the whole period and on each side of the 2022 rise, as the run
ranks them, with the later period also on weights fitted to it with hindsight.
That includes the later period's t-statistic of −1.64 at the earlier leverage
of 2.15, risk parity's Sharpe ratio of 0.13 on the hindsight weights, and the
0.12 of the later period's 0.50 gap that hindsight closes, about a quarter,
which leaves the three-quarters the post quotes. The seventh draws the later
period's hurdle across correlations on both sets of weights: about 0.70 and
0.78 at the measured +0.24, AGG's −0.69 times SPY's, the correlation of −0.62
below which the curve on fitted weights turns negative, the correlation of
−0.96 at which it meets AGG, and the −0.37 times stocks' Sharpe ratio below
which the curve on carried weights never falls. The second, third
and fourth figures carry Qian's printed numbers, listed in group 1, as cited
constants.

All seven figures are drawn from the committed SPY and AGG vintages by
[src/chan/risk_parity_figures.py](src/chan/risk_parity_figures.py):

1. The capital and risk shares of 60/40 and risk parity on the full span.
2. Risk parity's stock weight and leverage beside Qian's, and the Sharpe ratios
   of 60/40 and levered risk parity in his data and on SPY and AGG at the 1.74%
   bill average and at 4%, for Lesson 1.
3. Bonds' Sharpe ratio as a multiple of stocks' against the hurdle risk parity
   needs, in the same three rows, for Lesson 2.
4. The volatility ratio Qian's weights stand for beside the ratios his paper
   and SPY and AGG give, and the leverage that matches 60/40 against the
   correlation with the band his rounding allows, for Lesson 3.
5. Risk parity's Sharpe ratio less 60/40's against the assumed cash rate,
   with the tie, the rates at which the data names 60/40, and the bill average
   and 4% marked, for Lesson 4.
6. The Sharpe ratios of 60/40 and levered risk parity over the whole period,
   before the 2022 rise and after it on the earlier period's weights, and
   after it on weights fitted with hindsight, for Lesson 5.
7. The hurdle bonds' Sharpe ratio had to clear in the later period, against the
   stock-bond correlation, for weights fitted to the period and for the weights
   carried from before, beside AGG's actual ratio, for Lesson 6.

```bash
uv run python -m chan.risk_parity_figures
```

The test file holds what they draw rather than their bytes, for the reason
given above for the regime map.

[blog/stationary-candidates-lessons.md](blog/stationary-candidates-lessons.md)
is a sixth post, about two of Chan's three stationary candidates at Kindle
location 3951, the CAD/AUD cross rate and the bond pair tested on TLT and IEF.
It draws six lessons from Entries 5 and 6 of the replication log. Its opening
and its close also state the third candidate's verdicts, the calendar spreads
of Entry 15, which `TestTheCalendarSpreadVerdicts` holds.
[blog/calendar-spreads-lessons.md](blog/calendar-spreads-lessons.md), the
thirteenth post below, is the one that covers them.

1. A named series carries a verdict, while a class of instruments tested on
   stand-ins carries a finding.
2. A fitted pair faces a stricter critical value than one series, and on the
   cross rate which of the two applies decides the verdict.
3. The check for leftover autocorrelation strengthens the bond pair's finding
   and shrinks the cross rate's margin.
4. How often one-year windows reject says little about the whole span.
5. Each choice that could turn the answer was fixed in advance or checked both
   ways.
6. A reversion as slow as the cross rate's is hard to size, which an idealised
   model of a known-mean version of Chan's linear rule measures without running
   a trade on the rate.

Four groups of its figures are not pinned here.

1. Chan's words. "Quite stationary", "both being commodities currencies" and
   "fixed-income instruments can be found to be cointegrating" are quoted from
   location 3951, and nothing computes them. Lesson 6's 36-day half-life for a
   crude oil calendar spread is quoted from *Algorithmic Trading* Example 5.4,
   and so is the description of Chan's rule as measuring the distance from a
   moving average. [tests/test_calendar_spread_reversion.py](tests/test_calendar_spread_reversion.py)
   now computes and pins the half-life and the book's "stationary with 99
   percent probability" on Chan's own CL strip, while the model behind Lesson
   6 still reads 36 as an input rather than computing it.
2. Facts about the instruments. TLT holding Treasuries maturing in twenty years
   or more and IEF seven to ten are the funds' descriptions, not derivable from
   committed closes. That a cross rate is, in logs, a spread between two dollar
   rates with its hedge ratio fixed at one is an identity no test states.
3. Arithmetic that no test asserts. Nothing states that 2007-08-06 to
   2026-09-30 is nineteen years, that the vendor's 90-weekday gap is four
   months, that a half-life of 141.6 trading days is a little over half a year,
   that a 21-day step is a month, or that the history before the gap is a
   little under two years. Lesson 6 adds two more of the same kind: that 3.93
   is about four times, and that a gap 10.1 times a day's noise wide takes
   months rather than weeks to close.
4. Its references. The eight citations, and the rules the post attributes to
   them, such as Schwert's ceiling and the Breusch-Godfrey test, are cited
   rather than computed.

Every other number in the post traces to an assertion in
[tests/test_stationary_candidates.py](tests/test_stationary_candidates.py),
apart from what it sets beside them from GLD/GDX. The full-span −1.45 and
833.5 days, the 31 of 231 windows and the plain ADF table trace to
[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py), and the
5,099 days behind GLD/GDX's ceiling of 33 to
[tests/test_series.py](tests/test_series.py). Lesson 6's sentence that twice
the Kelly leverage earns only the cash rate is quoted from the Kelly post, and
`test_half_kelly_keeps_three_quarters_and_twice_kelly_keeps_none` in
[tests/test_kelly_figures.py](tests/test_kelly_figures.py) holds it. Six groups of its numbers had
no pin before it, and `tests/test_stationary_candidates.py` now pins them.

1. The bars of the ADF with a constant, −2.57, −2.86 and −3.43.
2. Both cross-rate statistics falling short of the pair's 5% bar of −3.34.
3. A one-year window holding about 1.78 half-lives.
4. The window-power simulation behind Lesson 4: 1,000 series that truly
   revert at the rate's half-life, scanned as the rate is, on a specification
   [issue 212](https://github.com/l3a0/quantitative-trading/issues/212) fixed
   before it ran. `TestTheWindowPower` holds its counts. It takes about half a
   minute of the suite's run.
5. The two checks behind Lesson 2's other choices: the rate's one-lag
   statistic with a trend and the trend's bars, and the test without a
   constant on the rate quoted per 100.
6. The model behind Lesson 6, exploratory and added after the verdict. It
   holds the Sharpe ratio of 0.78 against 1.55 at 36 days and the yearly 1.24
   against 4.29, the typical distance of 10.1 times a day's noise against 5.1,
   the 35.2 half-lives in the test period, the half-lives of 110.1 and 198.2
   days one standard error either side of the fitted slope, and the Kelly
   leverage moving almost one for one with the speed. `TestTheKnownMeanRule`
   holds them, and checks each closed form by running the trade on simulated
   series.

Its three figures are drawn from the committed vintages by
[src/chan/stationary_candidates_figures.py](src/chan/stationary_candidates_figures.py).

1. Both sets of bars as number lines, with the cross rate's two statistics on
   the first and the bond pair's on the second, and the cross rate's two
   statistics drawn again against the pair's bars, for Lesson 2.
2. The statistic at every lag count up to the ceiling, filled where the fit's
   residuals pass the check and hollow where they fail, the cross rate in one
   panel and both orientations of the bond pair in the other, for Lesson 3.
3. The two candidates' one-year rolling scans against their bars, laid out the
   same way, with a dot on each window past the 10% bar, for Lesson 4.

```bash
uv run python -m chan.stationary_candidates_figures
```

[tests/test_stationary_candidates_figures.py](tests/test_stationary_candidates_figures.py)
holds what they draw rather than their bytes, for the reason given above for
the regime map.

[blog/survivorship-and-transaction-costs.md](blog/survivorship-and-transaction-costs.md)
is a seventh post, about Chapter 3's warnings about a backtest: the
Khandani-Lo reversal, Example 3.7, which loses its edge to trading costs,
Chan's survivorship toy, Example 3.3, and Example 3.8, the reversal traded at
the open. It draws seven lessons from Entries 8, 9 and 10 of the replication
log.

1. On the S&P 500 a day's cost is larger than a day's profit.
2. Matching −3.19 means matching how Chan's code handles one missing day.
3. A database of survivors turns a loss into a large gain.
4. The book's own table mixes two kinds of share in NEOF's row.
5. The toy cannot measure survivorship's effect on the reversal.
6. On the book's rule, trading at the open misses Chan's claim after costs,
   while his notebook's own figures reproduce.
7. One column of Chan's file, WYN's, joins two stretches of prices, and the
   notebook reads the gap as one day's move.

Four groups of its figures are not pinned here. Its page numbers are the
revised edition's, read in the Kindle Cloud Reader on 2026-10-03.

1. Chan's words. "Of less than 1 is not suitable" from p. 23, the 5 basis
   points of p. 25, the mechanism and the futures rule at about 3 before costs
   and −3 after 1 basis point, both on p. 26, "fictitious" from p. 44, the
   small and microcap explanation on p. 74, and from p. 78 "mediocre", "the
   only change", the exercise on the S&P 400 and S&P 600 that closes Example
   3.8, and Example 3.8's "very positive". The last is not among the
   committed highlights, and
   [issue 206](https://github.com/l3a0/quantitative-trading/issues/206)
   records where the owner read it.
2. Facts outside the committed data. Neoforma's 1-for-10 reverse split
   effective 27 August 2001, from its 10-K. Khandani and Lo's 4.47, which the
   post quotes as Chan reports it on p. 72, and the stocks it was computed on.
   That older versions of pandas filled a gap with the last price by default,
   which is how the post explains the notebook's fill. The repost of Chan's
   notebooks at pinhaocheng/epchan-quant_trading_Python_codes `5fcab61`,
   where the four printouts were read. The suite pins their values, not where
   they were read.
3. Chan's *Algorithmic Trading*, cited through
   [its committed notes](research/book-notes/algorithmic-trading.md):
   his argument at location 432 that survivorship flatters a long-short
   reversal by less than a buy-only rule, and his second telling of the toy at
   location 704, with "almost 100 percent loss".
4. Arithmetic no test asserts: that −3.1822 rounds to −3.18, that a
   41.72% loss against a 100.91% gain is still a loss turned into a gain,
   that a return of 121.5 is a gain of over 12,000 percent, and that 952
   trading days is years.

Every other number in the post traces to an assertion in
[tests/test_khandani_lo.py](tests/test_khandani_lo.py),
[tests/test_series.py](tests/test_series.py) for WYN's 0.26, 31.85 and 952
trading days, or
[tests/test_survivorship_bias.py](tests/test_survivorship_bias.py), or to
[tests/test_survivorship_and_costs_figures.py](tests/test_survivorship_and_costs_figures.py)
for the two figures' own numbers. Five groups had no pin before it.

1. What an average day of the reversal earns, costs, trades and swings, as a
   share of the window's mean gross position, and that √252 times the average
   over the swing gives the Sharpe ratios. `TestWhatAnAverageDayCosts` holds
   them.
2. The −3.1886 that NumPy's NaN-skipping functions give at their default
   divisor, which lands on −3.19 without either quirk.
   `TestTheQuirksMoveTheFigure` holds it beside pandas' −3.1822.
3. That no stock priced on the window's first day is missing on its last,
   which `TestTheVintage` holds.
4. Where each running total ends and NEOF's 21.89 points on one share basis,
   which the figure tests hold.
5. That both of the notebook's figures on the opens clear 1.0, that its
   figure after costs still clears 1.0 without the fill or without WYN, and
   that charging the first day leaves the book's rule below 1.0. Two tests in
   `TestTheVerdicts` hold them.

Its two figures are drawn by
[src/chan/survivorship_and_costs_figures.py](src/chan/survivorship_and_costs_figures.py),
the first from the committed S&P 500 file and the second from the book's
printed tables.

1. The reversal's running profit over 2006, before costs and after, each day
   over the year's mean gross position, for Lesson 1.
2. The equal-capital return of the two printed tables and of the survivor-only
   table with NEOF on one share basis, each split into NEOF's share and the
   other nine's, for Lessons 3 and 4.

```bash
uv run python -m chan.survivorship_and_costs_figures
```

[tests/test_survivorship_and_costs_figures.py](tests/test_survivorship_and_costs_figures.py)
holds what they draw rather than their bytes, for the reason given above for
the regime map.

[blog/equity-seasonals-lessons.md](blog/equity-seasonals-lessons.md) is an
eighth post, about the equity seasonals, Examples 7.6 and 7.7. Chan reports
seasonality in stocks as fading and publishes Example 7.7 as dead, while his
text on Example 7.6 says it won in January 2008 after losing in the two
Januaries before. The post draws three lessons from Entry 7 of the replication
log.

1. Account for every choice and every bug, or one strategy gives several
   answers. Every figure his code prints reproduces, but the book's
   description fits several numbers, and six of the rules each script adds are
   bugs, which matching the printed figures means copying. Example 7.7's four
   printouts give four answers, and the first edition's is in different units
   from the other three.
2. To test whether an effect died, fix the criterion and the sample first.
   Reproducing a strategy published as dead checks its printed figures and not
   its death. The split at 2002 is exploratory with no verdict, and Chan's
   claim that the most recent five years do worse holds on his own file under
   a criterion written before the check ran.
3. Rule out survivorship bias before trusting a backtest. A file of survivors
   is the first thing the result cannot get past.

Four groups of its figures are not pinned here.

1. Chan's words, each cited by its page in the revised edition. "More than 13
   percent" and "has disappeared since then" are on p. 179, "has weakened or
   even disappeared in recent years" on p. 175, and "worked wonderfully" on
   p. 175 too, beside the tax-loss reason Chan gives for the January effect. The
   reader whose backtest of Example 7.6 failed is on p. 13. "The most
   recent five years instead of the entire data period", and Chan's
   statement that those years do even worse, are on p. 180.
2. Counts, arithmetic and facts no test asserts. Nothing counts the seventeen
   reproduced figures, nine for Example 7.6 and eight for Example 7.7, or
   Lesson 1's rules, which of them are bugs, and the six it copies and one it
   repairs, or the
   first edition's 95 months with a return and 83 with a position, which are
   its 96 months less the one with no return and less the twelve with no
   position. Nothing states that a stretch's slope in the figure is its
   average monthly return, that the revised Python copy's five printed figures match the book,
   that the mirror lacks `IJR_20080131.mat`, or that the repost it comes from
   carries the earlier save byte for byte as the mirror has it, which
   [data/README.md](data/README.md) records by its sha256.
3. Its references. The four citations, including the publication details the
   post gives for Heston and Sadka and for Singal, are cited rather than
   computed.
4. Heston and Sadka's own figures, read from their October 2006 working
   paper: NYSE- and AMEX-listed stocks in CRSP from January 1965 to December
   2002, only firms listed before each month, and the 1.15 percent a month in
   Table 2 for ranking on the return a year earlier. The post's 13.8 percent a
   year is twelve times that. Lesson 2 sets these beside Chan's file to say
   why the file cannot test them.

Every other number in the post traces to an assertion in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py), or to
[tests/test_equity_seasonals_figures.py](tests/test_equity_seasonals_figures.py)
for the figure's own labels, or to
[tests/test_equity_seasonals_whiteboard.py](tests/test_equity_seasonals_whiteboard.py)
for the whiteboard sketches' labels. One group had no pin before it, and
`TestTheYearsInsideTheSplit` now pins it: the calendar-year sums of the
revised Python's months, 0.2227 for 2002 and −0.1319 for 2006, that those
two years differ by more than the two halves of the split do, and that the
running sum peaks in January 2006.

Its one figure is drawn from the committed S&P 500 file by
[src/chan/equity_seasonals_figures.py](src/chan/equity_seasonals_figures.py).
It draws the 83 months the revised Python keeps as a running sum, split at
2002 and labelled with each half's month count, annual return and Sharpe
ratio, for Lesson 2.

```bash
uv run python -m chan.equity_seasonals_figures
```

[tests/test_equity_seasonals_figures.py](tests/test_equity_seasonals_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

The post also carries thirty looping whiteboard sketches, drawn by
[src/chan/equity_seasonals_whiteboard.py](src/chan/equity_seasonals_whiteboard.py)
on the USD.CAD post's sketch machinery. Each sits after the text it draws.

1. `equity_seasonals_which_years.gif`, in the opening, the years each source
   reads on one axis to scale: the years behind Heston and Sadka's 13
   percent, ending at Chan's 2002 split, Chan's two files, the book's first
   edition, and the two registered runs from 2009 on.
2. `equity_seasonals_two_verdicts.gif`, in the opening, the two registered
   runs' verdicts on number lines, each to its own scale: the January bracket
   from −0.1047 to 0.0879 across zero, and Heston and Sadka's mean at zero
   with the returns up to about 4.2 percent a year tinted as ones that could
   pass unseen. That 4.2 percent is the return the test detects 80 percent of
   the time.
3. `equity_seasonals_january_trade.gif`, Example 7.6's year of returns, its
   ranking at the year's last close, its January hold, and its bet that the
   extremes come back.
4. `equity_seasonals_same_month_trade.gif`, Example 7.7's ranking on one month
   a year ago, its hold of the same month, and its bet that the month repeats.
5. `equity_seasonals_rule_short_side.gif`, Example 7.6's rule 2, the 58 losers
   bought against the 56 winners shorted in January 2006, as bars to scale,
   with the best winner and the 58th left out.
6. `equity_seasonals_rule_filled_close.gif`, Example 7.6's rule 3, PMC's last
   close carried across its 851-day gap and read as a gain of 130.56 percent
   for 2007.
7. `equity_seasonals_rule_sum_or_mean.gif`, Example 7.7's rule 1, one month's
   positions added up against averaged.
8. `equity_seasonals_rule_wrong_close.gif`, Example 7.7's rule 2, each stock in
   the sorted row checked against the close in the same column of the
   unsorted one.
9. `equity_seasonals_rule_empty_months.gif`, Example 7.7's rule 3, the 96
   months and the 95 and 83 each mean divides by.
10. `equity_seasonals_rule_own_month_end.gif`, Example 7.7's rule 5, a shared
    month-end row against each stock's own last priced day.
11. `equity_seasonals_rule_month_end_lookup.gif`, Example 7.7's rule 8, the
    first pass asking the 96 month-end rows for row 258, and row 13, which
    the repair reads.
12. `equity_seasonals_split_swing.gif`, in Lesson 2, the two halves' annual
    returns beside the sums of 2002 and 2006, to one scale, with their gaps
    of 0.1574 and 0.3546.
13. `equity_seasonals_five_year_months.gif`, in Lesson 2's five-year check,
    the months the whole period, the split and the five-year rerun each
    cover, with the 23 months the rerun leaves out of the split.
14. `equity_seasonals_five_year_noise.gif`, the verdict's gap of 0.0036
    against the rerun's standard error of 0.0281, on one number line.
15. `equity_seasonals_five_year_januaries.gif`, Example 7.6's three
    reproduced Januaries as three bars.
16. `equity_seasonals_survivors_file.gif`, in Lesson 3, the companies a file
    saved in 2007 holds against the ones that left before the save.
17. `equity_seasonals_survivors_ranking.gif`, a month's ranking as it stood
    against the same ranking as the file holds it, whose worst tenth is a
    different set.
18. `equity_seasonals_survivors_panels.gif`, a file saved in 2007 against the
    index as it stood at each ranking date, the panel the later runs used
    from 2009.
19. `equity_seasonals_january_registered.gif`, under "Whether the January
    effect survived the book", the claim, test and verdict's words written
    down before any return is computed.
20. `equity_seasonals_january_fill.gif`, how the low and high versions fill a
    member with no checked price.
21. `equity_seasonals_january_ranges.gif`, each of the registered run's
    eighteen Januaries as a bar from its low version to its high, with a dot
    beside each bar for that January with the unchecked members left out.
22. `equity_seasonals_osap_sources.gif`, under "Whether Heston and Sadka's
    effect existed before 2002", CRSP, Norgate Diamond and Open Source Asset
    Pricing against four questions, with what each costs. Only Open Source
    Asset Pricing can be committed, and only it cannot run Chan's rule.
23. `equity_seasonals_osap_before.gif`, Heston and Sadka's printed 1.15
    percent a month against Open Source Asset Pricing's 1.36 percent over
    their sample, with one standard error each way, and 1.31 percent before
    Chan's 2002, against Chan's 13 percent a year as 1.08 percent a month.
24. `equity_seasonals_ivv_carry.gif`, under "Whether Heston and Sadka's effect
    survived the book", a company that leaves between two of IVV's filings,
    still on the list until the next one, and one that joins, not yet on it
    until then.
25. `equity_seasonals_ivv_checked.gif`, the 98,321 of 107,115 member-months
    with a checked price, and the month-ends with the fewest and the most.
26. `equity_seasonals_ivv_leavers.gif`, the companies that left the index
    within a year against those that stayed, as shares placed long, short and
    neither.
27. `equity_seasonals_ivv_running_sum.gif`, the run's 213 held months added up
    against the lines 13 percent a year and the 4.2 percent a year its test
    detects would climb.
28. `equity_seasonals_delta_scatter.gif`, under "Where the 4.2 percent comes
    from", the t-statistic's scatter for a true mean of zero, which clears
    1.652 5 percent of the time, above the same scatter slid right by
    δ = 2.494, which clears it 80 percent of the time.
29. `equity_seasonals_delta_shortcut.gif`, a normal curve centred at
    1.652 + 0.842 = 2.494, with the 20 percent that misses 1.652 and the 80
    percent that clears it.
30. `equity_seasonals_delta_bracket.gif`, the chance of clearing 1.652 against
    δ, the 0.80 line, and the solver's own first three brackets inside δ from
    0 to 5, which halve down from 50, keep the upper half once and then jump
    close to the crossing at 2.494.

Like the strategy sketches, Lesson 3's three, the January registered and fill
sketches and the carry-forward sketch are schematic and carry no figures. The
sources sketch carries no figure a run computes, only each source's cost.
Twelve sketches build more slowly than the rest and hold their finished
drawings for twelve seconds, because each carries more than the usual pace lets
a reader take in.

1. The first two of the five-year sketches, 13 and 14.
2. The last two of Lesson 3's sketches, 17 and 18.
3. The January fill and ranges sketches, 20 and 21.
4. The two sketches on whether Heston and Sadka's effect existed before 2002,
   22 and 23.
5. The leavers sketch, 26.
6. The three sketches of the 4.2 percent's derivation, 28 to 30.

```bash
uv run python -m chan.equity_seasonals_whiteboard
```

Eight sketches read the owner's archive: the verdicts sketch, the ranges
sketch, section 3's checked, leavers and running-sum sketches, and the three
of the 4.2 percent's derivation, which read the run's month count. On a
machine without it the command redraws the other twenty-two and exits
non-zero, naming the eight it left.

[tests/test_equity_seasonals_whiteboard.py](tests/test_equity_seasonals_whiteboard.py)
holds which tenth each strategy sketch buys and shorts, which way each points
its extremes, the timing each draws, that the opening sketches place every
figure and date to scale and refuse figures their words would misdescribe,
that each rule sketch prints its figures and puts its marks where they say,
that the split sketch draws each bar and bracket to one scale and colours each
bar by its sign, that the five-year sketches draw each bar to its months and
each dot, band and January bar at its figure, that Lesson 3's sketches keep
the companies that left out of the file, its ranking and its saved panel, that
section 2's sketches tick and cross each source as the post describes it and
draw each bar at its figure, that the 4.2 percent's three sketches put the
critical value, δ and each bracket where the test's figures say, that twelve
sketches build slowly and hold for
twelve seconds, that the ranges sketch
draws each January from its low to its high, that section 3's sketches hold a
change until the next filing, split each bar at its share and add up the
held months to one scale, that no label touches a line,
another label or the frame's edge, and that each GIF follows its text in the
post. The rule sketches' figures are defaults in `RuleFigures`, and
`TestTheRuleSketchesFigures` in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py) derives each
one from Chan's files. The split sketch's figures are defaults in
`SplitFigures`, and `TestTheYearsInsideTheSplit` derives each one from Chan's
S&P 500 file. The five-year sketches' figures are defaults in
`FiveYearFigures`, and `TestTheFiveYearSketches` in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py) derives each
one from Chan's files. The whiteboard test draws the verdicts from the pinned
figures, the January ranges from `PINNED_RANGES` and section 3's figures
from `PINNED_IVV`, and reads section 2's from the committed Open Source Asset
Pricing release as `PINNED_OSAP`, so it runs without the archive, and three tests in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py) hold that the
registered runs give those figures where the archive is. The test
compares each committed GIF with a fresh draw byte for byte only on macOS
arm64 in Comic Sans MS, as the USD.CAD sketches' test does. The sketches draw
with the USD.CAD module's strokes, timeline and renderer, so an edit there
needs both redraw commands.

[blog/post-earnings-drift-lessons.md](blog/post-earnings-drift-lessons.md) is
a ninth post, about post-earnings drift, Example 7.2 of Chan's *Algorithmic
Trading*. Chan trades the first day after an overnight earnings announcement
by the direction of the open, without reading the earnings, and reports an
APR of 6.7 percent and a Sharpe ratio of 1.5. It is the first post whose
experiment comes from that book. The post draws five lessons from Entry 12 of
the replication log.

1. Every figure Chan prints reproduces on his own files.
2. The gap from the previous close to the open stands in for the surprise,
   and Chan's flags stand in for the announcement calendar.
3. The 30 Chan divides by and the leverage he applies are facts about the run.
4. Which book's `smartstd` runs decides a printed digit.
5. An exact reproduction checks the arithmetic and not the edge.

Three groups of its figures are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "Used to last several days" and "barely until the market closes" are at
   2890. "The slow diffusion of news" is at 2990. "Known and studied since
   1968" and the trader needing no view of expectations are at 2994. The
   earnings.com calendar and the window from the previous close to the open
   are at 3002 and 3010. The 90-day deviation as the test of "surprising" is
   at 3019. "A very respectable 1.5", "a certain degree of look-ahead bias",
   "not a very grievous bias" and "at least four times" are at 3024. "The
   overnight returns are negative on average" is at 3039. The book's figures
   at 3024 are pinned, and its words are not. The *Quantitative Trading* quotation the plan named, at
   location 3360 of the revised edition, was dropped, because the Kindle
   Cloud Reader could not be reached on 2026-10-03 to read its page.
2. The book's Figure 7.2, which the post's figure redraws from `pead.m`'s
   `plot(cumret)` and which nothing compares with the book's own.
3. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_pead.py](tests/test_pead.py), to
[tests/test_series.py](tests/test_series.py) for the 1,885 flags, Apple's
three flagged days and the 29 stocks with none, to
[tests/test_pead_rerun.py](tests/test_pead_rerun.py) for Apple's five
releases inside the window and the two of them the rerun's calendar flags,
and for the 488 stocks and the 1,540, 311 and 914 flags that the rerun's
calendar and Chan's file share or hold alone, read from the committed Item
2.02 record against Chan's flag file, to
[tests/test_earnings_filings.py](tests/test_earnings_filings.py) for the time
each of Apple's filings was accepted, to
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py) for the two
Example 7.7 Sharpe ratios Lesson 4 recalls, or to
[tests/test_pead_figures.py](tests/test_pead_figures.py) for the figure's own
numbers. Four had no pin before it.

1. That 157 of the 330 days hold a position, the first on 2011-05-11, the
   first day the moving deviation can be computed.
2. That 1,279 flagged stock-days fall on or after that day, and that the
   1,072 positions are all among them.
3. That 29 of the 497 stocks carry no flag.
4. That the longest spell below the high runs from 2011-08-05 to 2012-01-10
   after a high on 2011-08-04, and that the deepest drawdown falls inside it
   on 2011-11-02.

Its one figure is drawn from the committed files by
[src/chan/pead_figures.py](src/chan/pead_figures.py), which reads them
through the same scale-break guard as `python -m chan.pead`. It redraws the
cumulative return `pead.m` plots, with the 89 days before the moving
deviation fills and the longest spell below the high shaded, for Lessons 1
and 3.

```bash
uv run python -m chan.pead_figures
```

[tests/test_pead_figures.py](tests/test_pead_figures.py) holds what it draws
rather than its bytes, for the reason given above for the regime map.

[blog/factor-models-lessons.md](blog/factor-models-lessons.md) is a tenth
post, about Chan's factor models: Example 7.4, the PCA factor model, and his
claim that factor returns have momentum, tested on the market and momentum
factors and on Example 7.4's own five. Example 7.4 rests on that claim, so the
post draws six lessons from Entries 13, 14 and 42 of the replication log
together. Every result in it is exploratory.

1. Three of the four printouts reproduce, and the fourth, the R, prints
   another program's figures.
2. Chan's round-off is a second strategy, because the revised Python's
   intercept cancels its factors and leaves single-stock momentum.
3. The momentum the strategy assumes held for the market factor and not the
   momentum factor, and for four of Example 7.4's own five factors. Each
   verdict stands on its own, none of the five survives a test across all
   five, and which one misses moves when PMC is dropped.
4. A verdict can follow the declared criterion and still rest on almost
   nothing, because both autocorrelations sit inside the range a series with
   no autocorrelation lands in 95 percent of the time.
5. Fix the rule before the number, which Entry 14 did and Entry 13's
   round-off criterion did not.
6. Every figure that touches the stocks is about survivors, and the market
   factor is not.

Four groups of its figures are not pinned here.

1. Chan's words, each cited by its page in the revised edition, read in the
   Kindle Cloud Reader on 2026-10-03 from the Annotations panel, which labels
   each highlight with the page it starts on. "The return of the market"
   (location 3978) is on p. 160. WML's definition (location 4004), and
   "often factor returns are more stable than individual stock returns",
   "stronger serial autocorrelations", "individual stock's returns" and "have
   momentum" (location 4014), are on p. 162. The setup of statistical factors
   (location 4034) is on p. 163. "Remain constant from the current time
   period to the next", "only 2% (MATLAB) to 4% (Python and R)" and
   "essentially round off errors" (location 4051) are cited at p. 164, where
   that highlight starts. A quotation late in a highlight could fall on the
   next page, which the panel cannot show. Example 7.4 itself runs from p. 163
   to p. 167, with the revised MATLAB's figures on p. 164, the Python's on
   p. 165 and the R's on p. 167, as Entry 13 records from the same reader. The
   suite pins the 2 and the 4 as whole percents, not the words.
2. Facts outside the committed data. That French's market factor subtracts
   the bill rate and his momentum factor skips the latest month. That the
   revised MATLAB repost at `7430b84` carries *Algorithmic Trading*'s
   `smartstd`. The commits the sources are read at: `1a71950` of the
   first-edition mirror, `7430b84` of the MATLAB repost and `5fcab61` of the
   Python repost. The Fama and French citation and its publication details.
3. Counts and arithmetic no test asserts. Each autocorrelation of 83 months
   rests on 82 pairs. 1.96 marks a two-sided 5 percent, which is what puts
   the band at 95 percent. Each annual mean is the monthly mean times 12. The
   Python's 255 rows with no position are its 1,006 rows less its 751 traded
   days.
4. Its references. The five citations are cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_pca_factor.py](tests/test_pca_factor.py),
[tests/test_momentum_factor.py](tests/test_momentum_factor.py) or
[tests/test_pca_factor_momentum.py](tests/test_pca_factor_momentum.py), to
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py)'s
`TestTheVintages::test_the_large_cap_panel` for the S&P 500 file's span, or to
[tests/test_momentum_factor_figures.py](tests/test_momentum_factor_figures.py)
for the figure's own labels. One figure was half pinned before it, and
`TestTheSplice::test_pmc_forward_fills_into_one_days_return` now pins both
ends of PMC's 851-day gap rather than only the days inside it.

Its one figure is drawn from the committed S&P 500 file by
[src/chan/momentum_factor_figures.py](src/chan/momentum_factor_figures.py). It
draws the 446 stocks' lag-1 autocorrelations as their cumulative curve, with
MKT, WML, the median stock, zero and the ±0.2151 band, so each factor's line
meets the curve at its percentile, for Lessons 3 and 4.

```bash
uv run python -m chan.momentum_factor_figures
```

[tests/test_momentum_factor_figures.py](tests/test_momentum_factor_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/commodity-seasonals-lessons.md](blog/commodity-seasonals-lessons.md) is
an eleventh post, about the commodity seasonals, the gasoline and natural gas
trades Chan says still pay where the equity ones weakened. It is the companion to
the equity seasonals post, and draws four lessons from Entry 11 of the
replication log.

1. A count of consecutive years needs its start year and its edition, and the
   natural gas counts reproduce only under the reading pinned on
   [issue 19](https://github.com/l3a0/quantitative-trading/issues/19).
2. A missing row is not a losing year, so three gaps in EIA's file bound the
   gasoline count between 16 and 19 rather than settling it.
3. A trade chosen after looking at the history is tested by the years after
   the book, and both trades win fewer of them.
4. Reading one named contract from files numbered by expiry needs a calendar
   checked against something the files do not supply.

It cites the revised edition by page, while the replication log cites the
same passages by Kindle location. Four groups of its figures are not pinned
here.

1. Chan's words, each cited by its page in the revised edition. The pairing
   of equity and commodity seasonals is on p. 175. "Alive and well", the
   demand from real economic need rather than speculation, and 19 profitable
   years of the last 21 "as of 2015" with the last 9 out of sample are on
   p. 183, as are the summer driving season and the scan of the literature.
   The gasoline rule's April dates and the profit every year since 1995 are
   on p. 184. 13 consecutive years and the demand from power generators, 14
   consecutive years and the exit on April 15, and "didn't hold up as well
   out-of-sample" are on p. 185. The warning about data-snooping and the
   suggestion to try nearby dates are on p. 186.
2. Facts outside the committed data. RBOB beginning to trade in October 2005,
   the first edition's release in November 2008 and its 2009 date, RB as the
   symbol RBOB trades under, a natural gas contract stopping three trading days
   before delivery and the May gasoline contract trading until the last
   business day of April as the exchange's rules, Good Friday as the only NYMEX
   holiday that can land on a trade date, EIA publishing the nearest four
   contracts numbered by expiry, EIA's statement that its source is NYMEX, and
   the Massive futures data service returning April 2025 gasoline prices, which
   [issue 19](https://github.com/l3a0/quantitative-trading/issues/19) records.
3. Arithmetic no test asserts: that 21 less 19 is 2, that 16 profitable years
   and 3 unreadable ones bound the count between 16 and 19, that 19 then needs
   all three unreadable years profitable, that four contracts in four years
   are 16, that 1994 to 2023 is 30 years, that the last 9 of 1995 to 2015 are
   2007 to 2015, that 7 of 15 is fewer than half, and that 2016 to 2023 is
   eight years.
4. Its references. The three citations are cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_commodity_seasonals.py](tests/test_commodity_seasonals.py), or to
[tests/test_commodity_seasonals_figures.py](tests/test_commodity_seasonals_figures.py)
for the figure's own labels. One had no pin before it, and
`TestNaturalGas::test_the_runs_counted_from_the_files_first_year` now pins it:
counted from 1994, the run of 13 profitable years ends in 2006.

Its one figure is drawn from the committed EIA files by
[src/chan/commodity_seasonals_figures.py](src/chan/commodity_seasonals_figures.py).
It draws every year of both trades as a bar at its settlement change, with the
three unreadable gasoline years as labelled empty slots, a mark giving each
year's sign, and a dashed line where the book's years end, for Lessons 2 and 3.

```bash
uv run python -m chan.commodity_seasonals_figures
```

[tests/test_commodity_seasonals_figures.py](tests/test_commodity_seasonals_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/buy-on-gap-lessons.md](blog/buy-on-gap-lessons.md) is a twelfth post,
about buy on gap, Example 4.1 of Chan's *Algorithmic Trading*. Each day the
strategy buys at the open the stocks that fell furthest below the previous
day's low, while still above their 20-day average, and sells at the close.
Chan reports an APR of 8.7 percent and a Sharpe ratio of 1.5, and 46 percent
and 1.27 for a mirror he prints no script for. The post draws six lessons
from Entry 18 of the replication log.

1. Both figures `bog.m` prints reproduce on Chan's own file.
2. The `smartstd` behind the 90-day standard deviation decides both printed
   figures.
3. One phrase, "annualized average return", names two formulas in this book.
4. The mirror, written down before any run, lands at 12 percent and not 46,
   though its drawdown is the steeper as Chan says.
5. Chan's own pair of figures implies at least four and a half times the
   written rule's volatility, from arithmetic alone.
6. An exact reproduction checks the arithmetic and not the edge.

Five groups of its figures are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The four rules, "panic selling at the open", "will gradually appreciate
   over the course of the day", "a momentum filter superimposed on a
   mean-reverting strategy" and the drops of "just a little" and "a lot" are
   at 1948. The 8.7 percent and 1.5, "has survivorship bias", "quite
   profitably", "suffered from diminishing returns from 2009 onward" and
   "does not have a large capacity" are at 1974. "Can't" and "signal noise"
   are at 1988. The mirror's sentence, its 46 percent and 1.27, "steeper
   drawdown" and "suffered from" are at 1993. "An annualized average return
   of around 8.7 percent", in a later chapter on risk management, is at 3509,
   and the same phrase for Example 7.2's
   levered figure is at 3024. The book's figures are pinned, and its words
   are not.
2. Facts outside the committed data. That `gapFutures_FSTX.m` measures a jump
   from the previous high, and that the name `bog.m` loads is the same bytes as
   the committed file in both public mirrors, which `src/chan/buy_on_gap.py`'s
   docstring and [data/README.md](data/README.md) record. That MS, the stock
   the mirror shorted on 2008-10-13, is Morgan Stanley's ticker. That the same
   script's return line sells the upward jump is not among them, since
   [tests/test_opening_gap.py](tests/test_opening_gap.py) holds that sign.
3. Arithmetic no test asserts: that ln(1 + r) ≤ r for every daily return,
   which the floor rests on, and the steps from it to the floor.
4. The book's Figures 4.1 and 4.2, which the post's figure redraws from
   `bog.m`'s `plot(cumret)` and from the written rule, and which nothing
   compares with the book's own.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_buy_on_gap.py](tests/test_buy_on_gap.py), to
[tests/test_pead.py](tests/test_pead.py) for Example 7.2's 6.7 percent as the
arithmetic figure, or to
[tests/test_buy_on_gap_figures.py](tests/test_buy_on_gap_figures.py) for the
figure's own numbers. Two had no pin before it, and the figure's test now pins
both, for each side.

1. That the longest spell below the high runs from 2008-09-02 to 2009-04-20
   after a high on 2008-08-29 for buy on gap, and from 2008-11-24 to
   2010-05-05 after a high on 2008-11-21 for the mirror.
2. That each side's deepest drawdown falls inside that spell, on 2008-12-09
   and 2009-02-03.

Its one figure is drawn from the committed file by
[src/chan/buy_on_gap_figures.py](src/chan/buy_on_gap_figures.py), which reads
it through the same `both_sides` as `python -m chan.buy_on_gap`. It draws two
panels on one scale, the cumulative return `bog.m` plots above and the
written mirror's below, each with the 90 days before the spread exists and the
longest spell below the high shaded, for Lessons 1 and 4.

```bash
uv run python -m chan.buy_on_gap_figures
```

[tests/test_buy_on_gap_figures.py](tests/test_buy_on_gap_figures.py) holds
what it draws rather than its bytes, for the reason given above for the regime
map.

[blog/calendar-spreads-lessons.md](blog/calendar-spreads-lessons.md) is a
thirteenth post, about the third of Chan's stationary candidates at Kindle
location 3951, the futures calendar spreads, tested on every pair of
neighbouring natural gas and RBOB gasoline contracts in EIA's settlements. It
draws four lessons from Entry 15 of the replication log.

1. A claim with no number still needs a pass mark written down first, and a
   batch of calendar spreads carries a verdict because each pair is a member
   of the class Chan names rather than a stand-in for it.
2. The simulated contracts have to move together like real ones, and
   correlating them as the files are moved RBOB's verdict and not natural
   gas's, with both readings reported.
3. About 56 days cannot tell slow reversion from none, so RBOB's verdict is
   not evidence that its spreads fail to cointegrate.
4. A calendar that is one day wrong should cost nothing. The days each window
   drops make that true, and the check of the expiry rule over every handover
   forced one correction.

Five groups of its figures are not pinned here.

1. Chan's words. "The simplest examples of cointegrating futures pairs" is
   quoted from location 3951 of *Quantitative Trading*. "Do not generally
   mean-revert" is quoted from location 2321 of *Algorithmic Trading*, and the
   12-month crude oil spread taken in logs, stationary
   at 99% with a 36-day half-life, from
   locations 2461 and 2471, both through
   [its committed notes](research/book-notes/algorithmic-trading.md).
   [tests/test_calendar_spread_reversion.py](tests/test_calendar_spread_reversion.py)
   now computes and pins the half-life and the 99 percent claim on Chan's own
   CL strip, while the power simulation still reads 36 as an input.
2. New York Harbor gasoline's two counts, a median of 42 days for a pair of
   its neighbouring contracts and 141 of its 150 pairs keeping fewer than 50,
   which [issue 137](https://github.com/l3a0/quantitative-trading/issues/137)
   measured before any statistic.
3. Facts outside the committed data. EIA publishing only the nearest four
   contracts, numbered by expiry, RBOB replacing New York Harbor gasoline, and
   29 and 30 October 2012 falling during Hurricane Sandy are each stated
   rather than derived. So are the owner's ruling of 2026-10-03 that corrected
   the null, and the request to the Massive futures data service that day
   which returned no prices for the three natural gas contracts it asked for,
   both of which
   [issue 137](https://github.com/l3a0/quantitative-trading/issues/137)
   records.
4. Arithmetic no test asserts. That 57 against 47 is ten pairs clear and 14
   against 31 seventeen short, that 14 against 13 is one pair clear under the
   declared null, that the 975th of 1,000 rather than the 950th splits a 5%
   chance of a false pass across two commodities, that requiring both
   orientations costs natural gas five pairs and RBOB three against the
   near-on-far orientation, that 250 and 255 of 360 are about seven in ten and
   168 and 166 of 220 about three in four, that 316 less 298 is 18 and 213
   less 202 is 11, that 580 is 360 and 220, that 2012-10-25 is two trading
   days before 2012-10-29, and that a window opening after one expiry,
   crossing two more and closing on a fourth rests on four, so each expiry
   falls inside four pairs' windows.
5. Its references. The four citations are cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_stationary_candidates.py](tests/test_stationary_candidates.py),
which pins Entry 15's rows, to
[tests/test_commodity_seasonals.py](tests/test_commodity_seasonals.py) for the
16 contracts whose exchange dates check the expiry rule, or to
[tests/test_calendar_spread_figures.py](tests/test_calendar_spread_figures.py)
for the figure's own labels.

Its one figure is drawn from the committed EIA files by
[src/chan/calendar_spread_figures.py](src/chan/calendar_spread_figures.py),
which reads them through the same `calendar_spread` as
`python -m chan.stationary_candidates calendar-spread`. It draws one panel per
commodity, with the 1,000 shares under each null as a histogram counted in
pairs, each null's 975th share as a dashed line, and the real count as a solid
line, for Lesson 2.

```bash
uv run python -m chan.calendar_spread_figures
```

[tests/test_calendar_spread_figures.py](tests/test_calendar_spread_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/conditional-parameter-optimization-lessons.md](blog/conditional-parameter-optimization-lessons.md)
is a fourteenth post, about Conditional Parameter Optimization, Example 7.1 of
the revised *Quantitative Trading*. A model re-chooses a GLD/GDX spread
strategy's three parameters each evening, and Chan reports that this beats
holding them fixed on every metric he prints. The post draws four lessons from
Entry 16 of the replication log.

1. Neither of Chan's columns reproduces, and re-choosing daily wins on the
   Calmar ratio alone, so his claim fails. The re-chosen column is reproduced
   only in kind, because his rests on PredictNow's model.
2. The book's own annual returns do not compound to its cumulative ones, under
   either definition of annual return, which arithmetic alone shows.
3. The first run broke a declared reading on the 34 early closes. The code was
   fixed to the reading, and both runs are reported, unlike Entry 15, where the
   reading itself was corrected.
4. The selection picks a cell that makes 46.7 round trips a day, whose edge
   before costs is under half a basis point a round trip, so 1 basis point a
   round trip turns both arms to losses.

It is the first post here whose figures a public clone cannot re-run. Its
computed figures trace to `TestExample71OnTheArchive` in
[tests/test_cpo.py](tests/test_cpo.py), whose pins run only where the owner's
archive of minute bars is and only when `QT_ARCHIVE_RUN=1` asks, because the
bars are licensed and the repo commits only their hashes. Chan's arithmetic in
Lesson 2, the early closes and the 12:59 fix in Lesson 3, and the grid and
rules run on every clone.

Six groups of its figures are not pinned here.

1. Chan's words. "As frequently as they like" is quoted from location 3414 and
   "but nobody (until they read this book!) is predicting the returns of this
   particular GLD trading strategy" from location 3617, both through
   [its committed notes](research/book-notes/quantitative-trading.md). "May
   execute multiple round trips per day" is quoted from p. 140 and "random
   forest with boosting" from p. 142, which the notes hold at locations 3444
   and 3517 and the pages read on 2026-10-03 place on those pages. The
   eleven tokens of the printed entry grid and the stated start of January 1,
   2006 are quoted from p. 137.
2. The book's printed results on p. 145, the eight figures and "all other
   metrics" improved, which the committed notes do not hold. The eight figures are `chan.cpo`'s constants `BOOK_UNCONDITIONAL`
   and `BOOK_CONDITIONAL`, but nothing ties those constants to the page.
3. The third party's figures, a run on Kibot bars from 2009 with a test Sharpe
   ratio of 5.974 at 50.1 round trips a day and a gross edge of 0.425 basis
   points a round trip, cited as theirs from jeffmcphail/mctheory-praxis at
   `b7c5b5d`.
4. The first run's figures in Lesson 3. The archive pins at `cb30336`, the
   merge of the first run, asserted them, and no test that runs today does.
   `git show cb30336:tests/test_cpo.py` shows them.
5. Arithmetic no test asserts: that three parameters and seven indicators on
   each of two funds at seven lookbacks make 101 features, against the book's
   115 at p. 140, that
   [issue 23](https://github.com/l3a0/quantitative-trading/issues/23) declared
   19 readings, that a fraction such as 3.40 is the percentage 340%, and that
   gaps of 2.67 and 0.4883 are 267 and 48.83 percentage points.
6. Its references, cited rather than computed, and facts outside the data:
   that NYSE closes at 13:00 on some days such as the day after Thanksgiving,
   and that a basis point is a hundredth of a percent.

Five of its figures had no pin before it, and each now has one. The first
runs on every clone, and the other four sit in `TestExample71OnTheArchive`.

1. The cap on what Chan's annual returns, read as arithmetic, can compound to
   over three years: 68.0% and 81.0%, below his 73% and 83%.
2. The fixed column as multiples of Chan's figures: 4.7, 3.8, 2.9 and 15.5.
3. Each arm's gross return a round trip, 0.435 and 0.462 basis points, added
   after the result was seen.
4. That only `2.5_30_0.2` trades more than the chosen cell, added after the
   result was seen.
5. Spearman's rank correlation between the 400 cells' round trips a day and
   their test Sharpe ratios, 0.95, added after the result was seen.

Its one figure is drawn by
[src/chan/cpo_figures.py](src/chan/cpo_figures.py) from one run of
`chan.cpo.run`. It plots the 400 cells' test Sharpe ratios against their round
trips a day on a log axis, with Chan's 1.947 as a line and three cells
labelled, for Lesson 4. The run reads the archive, so the committed PNG
redraws only where the archive is, in about five minutes.

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.cpo_figures
```

[tests/test_cpo_figures.py](tests/test_cpo_figures.py) holds what it draws
rather than its bytes, for the reason given above for the regime map. Its
drawing runs on every clone against a synthetic run of 400 cells. Its three
checks on the real run need the archive: that the three labels are the cells
Entry 16 names, that the run ends on 2020-12-31, and that a fresh draw matches
the committed file. A public clone can check what the code draws but cannot
redraw the committed figure.

[blog/cross-sectional-momentum-lessons.md](blog/cross-sectional-momentum-lessons.md)
is a fifteenth post, about cross-sectional momentum, Example 6.2 of Chan's
*Algorithmic Trading*. Each day the strategy buys the 50 stocks with the
highest 252-day return and shorts the 50 with the lowest, and holds each day's
picks 25 days. Chan reports an APR of 37 percent and a Sharpe ratio of 4.1 over
2007, and −30 percent over 2008 and 2009, while the comment closing
`kentdaniel.m` records a Sharpe ratio of 0.40. The post draws four lessons from
Entry 17 of the replication log.

1. The 0.40 is the comment's and not the code's, which computes 4.0657 on the
   file it loads.
2. A rule taken from one example did not carry to the next. Read as the
   arithmetic return, as Example 7.2's "APR" is, the book's APR reproduces in
   neither window, and the compounded figure that matches both was seen only
   afterwards.
3. The crash Chan describes is in the file, and the one book claim that
   reproduces under a rule fixed in advance is that the return after 2009
   stabilized below 2007's.
4. A reproduction checks the arithmetic and not the edge.

Five groups of its figures are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The top and bottom deciles held for a month are at 2797. The 37 percent and
   4.1, "a miserable −30 percent", "did stabilize, though it hasn't returned
   to its former high level yet", and Daniel and Moskowitz's 16.7 percent and
   0.83 from 1947 to 2007 are at 2800, and so are the labels "APR" for
   Chan's figure and "annualized average return" for theirs. That Example
   7.2 calls its 6.7 percent an APR is at 3024. "Performed similarly well
   pre-2008", the reversal's 4.7, "vanished during the aftermath of the stock market
   crash in 2008–2009" and the cause in "the strong rebound of short
   positions" are at 2890. The book's figures are pinned, and its words are
   not.
2. Facts outside the committed data. The scripts' print labels,
   `Avg Ann Ret=` for the arithmetic figure and `APR=` for the compounded one,
   in `kentdaniel.m` and `pead.m`, and `bog.m`'s label on its compounded
   figure. That neither public copy of Chan's code ships a `lag.m`, that the
   first edition's `lag1.m` shifts by one row, and that both copies hold the
   same `kentdaniel.m`, which `src/chan/cross_sectional_momentum.py`'s
   docstring records. Whether ETFC's move from 85.9 to 35.5 was a real move or
   a bad print, which nothing checks.
3. Arithmetic no test asserts: that 0.40 is about a tenth of 4.1 and of
   4.0530, so either helper's Sharpe ratio is ten times the comment's, that
   2007-05-15 to 2007-12-31 is seven and a half months, and that 1947 to 2007
   is sixty years.
4. The book's Figure 6.6, which the post's figure redraws from
   `kentdaniel.m`'s `plot(cumret)` and which nothing compares with the book's
   own.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_cross_sectional_momentum.py](tests/test_cross_sectional_momentum.py),
to [tests/test_pead.py](tests/test_pead.py) for Example 7.2's 6.7 percent as
the arithmetic figure, to
[tests/test_khandani_lo_book_two.py](tests/test_khandani_lo_book_two.py) for
the reversal's 4.713284 on the same file, or to
[tests/test_cross_sectional_momentum_figures.py](tests/test_cross_sectional_momentum_figures.py)
for the figure's own numbers. Three had no pin before it.

1. That the 2008 and 2009 spell below the high runs from 2008-07-15, after a
   high on 2008-07-14, to the window's last day, 2009-12-31, so it was still
   running when the window ended, which the figure's test now pins.
2. Each window's deepest drawdown, the high it fell from and its trough,
   which the figure's test now pins too.
3. ETFC's closes of 85.9 on 2007-11-09 and 35.5 on 2007-11-12, and the
   strategy's position of −25 in it on 2007-11-09, which
   `TestTheScaleBreakDecision` now pins.

Its one figure is drawn from the committed file by
[src/chan/cross_sectional_momentum_figures.py](src/chan/cross_sectional_momentum_figures.py),
which reads it through the same `read_closes` and `script_as_printed` as
`python -m chan.cross_sectional_momentum`, and slices each window through the
same `window_returns` as the printed figures. It draws three panels on one
scale, one per window the script carries, each restarting at zero, with its
deepest drawdown marked and the 2008 and 2009 spell below the high shaded, for
Lessons 2 and 3.

```bash
uv run python -m chan.cross_sectional_momentum_figures
```

[tests/test_cross_sectional_momentum_figures.py](tests/test_cross_sectional_momentum_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/price-spread-ratio-lessons.md](blog/price-spread-ratio-lessons.md) is a
sixteenth post, about Example 3.1 of Chan's *Algorithmic Trading*, which trades
GLD against USO on the price spread, the log price spread and the ratio with
one linear mean-reversion rule. Chan reports about 10.9 percent and 0.59 for
the price spread, 9 percent and 0.5 for the log price spread, and a negative
APR for the ratio, and each script's closing comment prints six decimals. The
post draws six lessons from Entry 21 of the replication log.

1. Two scripts land to six digits, and the book's 10.9 percent is not its
   script's 0.108335 rounded.
2. The three signals hold three portfolios, fixed shares, fixed dollars and
   equal dollars.
3. `Ratio.m`'s comment matches the script with GLD and USO swapped, a reading
   found after the published script missed.
4. The pair shows no cointegration on Chan's file, the 20-day hedge ratio
   changes sign, and the traded spread is mostly the fit's intercept.
5. The rule's return cannot see how its units are scaled, so the deviation's
   divisor moves no figure.
6. A reproduction checks the arithmetic and not the edge.

Five groups of its figures are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   That a stationary mix of log prices is a portfolio of constant dollar
   weights rebalanced every day is at 1435. That a ratio is stationary only in
   "a special case", that a ratio is unchanged when both prices scale
   together, and that Chan knows no general answer are at 1476. "Are not, in
   fact, cointegrated", "near-optimal" with "the benefit of hindsight", the
   word stationary for the spread, "actually lower", the extra cost of the log
   price spread, "a negative APR" and the caption "Ratio = USO/GLD" are at
   1505. The book's figures are pinned, and its words are not.
2. Facts outside the committed data. That two public copies of Chan's code
   hold the three scripts byte for byte and neither holds another version of
   `Ratio.m`, which `src/chan/price_spread.py`'s docstring records, and that
   the copy of the two closes in Chan's Python port equals the committed
   closes, which [data/README.md](data/README.md) records.
3. Arithmetic no test asserts: that any positive constant on the positions
   cancels out of the return, which the equation shows. The tests check a
   factor of 2 on synthetic arrays and the two divisors on Chan's file.
4. The book's Figures 3.1 and 3.2, which the post's figure redraws from the
   scripts' `plot` calls and which nothing compares with the book's own.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_price_spread.py](tests/test_price_spread.py), to
[tests/test_series.py](tests/test_series.py) for the file's 67 ETFs, its
dividends subtracted in dollars and GLD paying none, to
[tests/test_bollinger.py](tests/test_bollinger.py) for Example 3.2's APR and
Sharpe ratio under either divisor, which Lesson 5's link to the Bollinger band
post quotes, or to
[tests/test_price_spread_figures.py](tests/test_price_spread_figures.py) for
the figure's own numbers. Six had no pin before it.

1. Engle-Granger's −1.5150 for USO on GLD over all 1,500 days, that it does
   not reach the 10% bar of −3.04, and its whole-period hedge ratio of
   −0.2669.
2. The 20-day hedge ratio's range, −0.948 to 2.168, and its 334 days below
   zero.
3. The 20-day fit's intercept against the spread: a correlation of 0.9987,
   standard deviations of 45.37 for the spread and 2.27 for the leftover, a
   quarter of a percent of the variance, and the leftover traded alone at
   −0.005130 and 0.082065.
4. The ratio's 1.03 on the first traded day, 0.24 on the last, 1.30 at its
   highest and 0.44 at its highest after 2008.
5. The two readings tried after the ratio missed: keeping the first 20 days,
   −0.140674 and −0.744310, and Chan's Python port, −0.140674 and −0.749583.
6. The figure's own lines and labels.

Its one figure is drawn from the committed file by
[src/chan/price_spread_figures.py](src/chan/price_spread_figures.py), which
reads it through the same `read_sources` and `example_three_one` as
`python -m chan.price_spread`, scale-break guard included. It draws four panels
on one date axis, for Lessons 1, 2 and 4.

1. The 20-day hedge ratio, with its days below zero shaded.
2. The price spread, the book's Figure 3.1.
3. The ratio, the book's Figure 3.2.
4. Every run's cumulative return, the swapped ratio dashed.

```bash
uv run python -m chan.price_spread_figures
```

[tests/test_price_spread_figures.py](tests/test_price_spread_figures.py) holds
what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/gold-miners-oil-lessons.md](blog/gold-miners-oil-lessons.md) is a
seventeenth post, about location 1922 of Chan's *Algorithmic Trading*, where
GLD and GDX cointegrate until July 14, 2008, stop afterwards, and regain one
relation once the oil fund USO joins them. The book prints no statistic for
any of the three claims. The post draws four lessons from Entry 29 of the
replication log.

1. Every claim holds on both Johansen statistics, with room, and the book's
   "99 percent probability" is a test level rather than a probability.
2. The control the book leaves out holds, since GLD and GDX alone over the
   triplet's days find no relation even at 90 percent.
3. A second control weakens the story, since GDX and USO alone find one
   relation at 99 percent and GLD and USO find none.
4. The split date and the third ETF were both chosen after the break was seen,
   so the result is exploratory and cannot confirm the oil hypothesis.

Six groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "Until July 14, 2008, or thereabout", the three claims' quotes, the oil
   peak at around $145 a barrel, the mining-cost explanation, the suggestions
   to trade the triplet or to stop trading the pair above an oil threshold,
   and the framing of the example as a hypothesis to test are all at 1922.
   The three claims' quotes are also matched against that highlight by
   `TestTheBooksClaims`.
2. Facts outside the committed data. That USO holds the crude oil futures
   nearest expiry and drifts from the spot price as it rolls, which Entry 29
   records, and that every Johansen call in Chan's scripts for the book passes
   a constant and one lagged difference, which
   [src/chan/gold_miners_oil.py](src/chan/gold_miners_oil.py)'s docstring
   records.
3. Two readings no test asserts: that a test level is not the probability a
   claim is true, and that a full Johansen rank says each series is
   stationary alone.
4. The MacKinnon critical values of −3.34 and −3.90 for the Engle-Granger
   test, which are constants of `ithildincore.timeseries` rather than
   something this repository computes. The suite asserts that the statistic
   falls between them.
5. The figure's alt text, whose readings of the lines, such as "about 23" and
   "between about 40 and 66", are approximate by design.
6. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_gold_miners_oil.py](tests/test_gold_miners_oil.py), to
[tests/test_gold_miners_oil_figures.py](tests/test_gold_miners_oil_figures.py)
for the figure's own numbers, to
[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py) for the
critical values checked against Chan's printout and the two Johansen
statistics disagreeing on his file, or to
[tests/test_regime_figure.py](tests/test_regime_figure.py) for the earlier
post's rolling windows. Five had no pin before it.

1. USO's highest close on the file, 117.48, on 2008-07-14, the last day of the
   first window.
2. The first window's Johansen weights, 0.191134 shares of GLD and −0.513914
   of GDX.
3. That portfolio in standard deviations from its first-window mean: −3.24 to
   2.56 over the 539 days before the split, and 0.47 to 13.52 over the 942
   after it, where it never returns to the mean.
4. That portfolio crossing its first-window mean 61 times before the split.
5. The rolling windows of the earlier post's regime map: 9 of the 45 ending
   inside 2008-07-15 to 2012-04-09 pass at 10 percent, and the last to pass
   before 2019 ends on 2015-10-22.

Its one figure is drawn from the committed file by
[src/chan/gold_miners_oil_figures.py](src/chan/gold_miners_oil_figures.py),
which reads it through the same `read_sources` and `gold_miners_oil` as
`python -m chan.gold_miners_oil`, scale-break guard included. It draws two
panels on one date axis, for Lesson 1, with the split marked on both.

1. The closes of GLD, GDX and USO, with USO's highest marked.
2. GLD and GDX in the first window's Johansen weights, carried across the
   split.

```bash
uv run python -m chan.gold_miners_oil_figures
```

[tests/test_gold_miners_oil_figures.py](tests/test_gold_miners_oil_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/johansen-etf-lessons.md](blog/johansen-etf-lessons.md) is an eighteenth
post, about Examples 2.6 to 2.8 of Chan's *Algorithmic Trading*, which test
EWA, EWC and IGE for cointegration with the CADF and Johansen tests and trade
the triplet's first eigenvector with a linear mean-reversion rule. Chan reports
a CADF statistic of about −3.64, a half-life of 23 days, and an APR of 12.6
percent with a Sharpe ratio of 1.4. It is the blog's explanation of the
Johansen test, built from the CADF test the earlier posts teach. The post
draws six lessons from Entry 23 of the replication log.

1. Every figure `cointegrationTests.m` prints reproduces to its last digit,
   the eigenvectors with their signs flipped.
2. One regression depends on which ETF goes on the left, and the Johansen
   test does not depend on the column order.
3. The trace test counts three relations among the three ETFs and the eigen
   test counts none, though location 1337 says both count three.
4. Two relations between two series is a full rank, which says each ETF
   reverts alone, and a plain ADF on each rejects a unit root for none.
5. The first eigenvector is long EWC and short EWA and IGE, and reverts
   fastest of the three.
6. An exact reproduction checks the arithmetic and not the edge.

Five groups of its figures are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "The use of in-sample data to find the half-life" is at 1225. "Commodity
   based, so they seem likely to cointegrate" is at 1264. The question of
   swapping the legs, its answer "yes" and "try each variable as independent"
   are at 1282. The 95 percent verdict is at 1292. The Johansen equation, the
   counting rule and the eigenvectors as hedge ratios are at 1295. "Which are
   not necessarily reciprocal of each other" and the test's independence of
   order are at 1324. IGE joining is at 1334, "Both Trace statistic and Eigen
   statistic tests conclude" at 1337, and the first eigenvector reverting
   fastest at 1340. "No parameters to optimize", "continuously enters and
   exits positions" and "obviously not a practical strategy" are at 1350, and
   "the same data for parameter optimization (such as finding the best hedge
   ratio) and for backtest" is at 1429. The book's figures are pinned, and its
   words are not.
2. Facts outside the committed data. That jplv7 is James LeSage's toolbox and
   that statsmodels multiplies the eigenvector matrix by the sign of its
   top-left element, which `src/chan/johansen.py`'s docstring records, and
   that the file subtracts dividends in dollars, which
   [data/README.md](data/README.md) records.
3. Arithmetic no test asserts: that a full rank makes every combination
   stationary, including one ETF held alone, that the test's eigenvalues lie
   between 0 and 1, and the two formulas for the trace and eigen statistics,
   which the post shows as equations.
4. The book's Figures 2.4, 2.6 and 2.7, which the post's figure redraws from
   the script's `plot` calls and which nothing compares with the book's own.
   The alt text's description of shapes in the figure, such as EWC sitting
   above EWA and both falling in late 2008, is read off the drawing rather
   than asserted.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py), to
[tests/test_index_arbitrage.py](tests/test_index_arbitrage.py) for the two
relations the trace test counts at 95 percent and none the eigen test finds in
the Entry 24 post that Lesson 4 links, or to
[tests/test_etf_cointegration_figures.py](tests/test_etf_cointegration_figures.py)
for the figure's own numbers. Four had no pin before it, and
[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py) now pins
them.

1. That each trace statistic is the sum of the eigen statistics from its row
   down, for the pair and the triplet.
2. That the triplet's trace test counts three relations at 90 and 95 percent
   and none at 99, since 34.429 falls short of 35.463.
3. The first eigenvector's dollars per unit on 2012-04-09, 28.72 of EWC
   against −17.43 of EWA and −8.49 of IGE.
4. The strategy's deepest drawdown of −0.101249 on 2010-08-16, and its longest
   spell below a high, 598 days from 2009-04-02 to 2011-08-15 after a high on
   2009-04-01.

Its one figure is drawn from the committed file by
[src/chan/etf_cointegration_figures.py](src/chan/etf_cointegration_figures.py),
which reads it through the same `read_sources` and `etf_cointegration` as
`python -m chan.etf_cointegration`, scale-break guard included. It draws four
panels, for Lessons 1, 3 and 6.

1. EWA and EWC over the file, the book's Figure 2.4.
2. The residual of EWC on EWA, the book's Figure 2.6.
3. The triplet's trace and eigen statistics against their 90, 95 and 99
   percent critical values, one group per null.
4. The strategy's compounded cumulative return, the book's Figure 2.7, with
   the deepest drawdown marked and the longest spell below a high shaded.

```bash
uv run python -m chan.etf_cointegration_figures
```

[tests/test_etf_cointegration_figures.py](tests/test_etf_cointegration_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/vx-es-lessons.md](blog/vx-es-lessons.md) is a nineteenth post, about
locations 2546 to 2559 of Chan's *Algorithmic Trading*, which hedge VX, the
VIX future, against ES, the E-mini S&P 500 future, from August 2008 and trade
the portfolio against a band one deviation wide. Chan reports a hedge of
0.3906 VX contracts per ES contract, a residual standard deviation of \$2,047,
and an APR of 12.3 percent with a Sharpe ratio of 1.4. The post draws four
lessons from Entry 28 of the replication log.

1. Three of the four figures land at the book's precision on Chan's
   2012-05-07 save, and the residual deviation misses by \$2.09.
2. The 2012-05-11 and 2012-05-17 saves miss all four, and `VX_ES.m` loads the
   later one, fits on days that include the test set, and runs no trade.
3. The exit the book leaves out decides the trade, since closing at the mean
   gives 6.8 percent, and of the three rules tried only holding until the
   opposite band lands both.
4. The APR rests on four positions, all of them winners, and the whole of the
   test set's gain came after the close of 2011-08-05.

Seven groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "When the market goes down, volatility shoots up" is at 2546. The two
   regimes, the second's lower volatility for a given index level, and the
   warning against a regression across both are at 2552. The
   dollars per point, the four figures, the long 0.3906 VX contracts and one
   ES contract, the band of one training deviation, and "particularly
   profitable" around the downgrade are at 2559. "0.3906 front contracts of
   VX" in the roll-return trade is at 2754. The book's figures are pinned, and
   its words are not.
2. The search behind the window. Its 22,446 windows across the three saves,
   and the one window among them that rounds to both fitted figures, are
   recorded in Entry 28 and on the issue that shipped the run. No test reruns
   the search.
3. Facts outside the committed data. What ES and VX are and what the VIX
   index measures. That Standard and Poor's announced its downgrade of the
   U.S. credit rating after the close of Friday 2011-08-05. That a continuous
   future shifts its history at each roll, and that VX's and ES's closes do
   not move by one constant between saves, so how Chan's source rebuilt them
   was not measured, both of which [data/README.md](data/README.md) records.
4. What Chan's scripts at `e4bc46f` in `ericnberwick/EpchanPreview` do. That
   `VX_ES.m` loads the 2012-05-17 save, keeps the days both legs traded,
   draws the scatter and stops after the regression. That
   `VX_ES_rollreturn.m` anchors at 2008-08-04, tests from the 501st row on,
   computes every day's return before keeping those rows, reads ES from the
   2012-05-07 save, and trades one VX contract against one ES contract with
   every line holding 0.3906 commented out. That `bollinger.m` exits at a
   z-score of 0.
   [src/chan/vx_es.py](src/chan/vx_es.py)'s docstring and
   [data/README.md](data/README.md) record the first two.
5. Arithmetic on pinned numbers that no test asserts as written: the
   deviation missing by about a tenth of a percent, the APR on the later saves
   falling by more than half, the 449 test days making about a year and three
   quarters, and 236 of 449 days being more than half.
6. The figure's alt text, whose readings of the points and lines, such as
   "about 56,000 and 77,000 dollars" and "about minus 8 percent", are
   approximate by design.
7. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_vx_es.py](tests/test_vx_es.py), or to
[tests/test_vx_es_figures.py](tests/test_vx_es_figures.py) for the figure's
own numbers. Three groups had no pin before it, and
[tests/test_vx_es.py](tests/test_vx_es.py) now pins them.

1. The test set around the downgrade. It is down 0.045935 at the close of
   2011-08-05, after 259 of the 449 test days, and grows 0.288414 over the
   190 days after it to end at 0.229231. Its lowest, −0.077553, falls on
   2011-08-08, the day the z-score reaches −3.886, its lowest since the
   anchor.
2. The four positions' returns over the test days each one earned: long for
   325 days at 0.058104, short for 28 at 0.056144, long for 41 at 0.056877,
   and short for 55 at 0.040777.
3. That starting flat on the first test day lands the Sharpe ratio and misses
   the APR by 0.2, and that closing at the mean misses the Sharpe ratio too.

Its one figure is drawn from the committed save by
[src/chan/vx_es_figures.py](src/chan/vx_es_figures.py), which reads it through
the same `read_legs` and `vx_es` as `python -m chan.vx_es`, scale-break guard
included. It draws three panels after the book's Figures 5.10 to 5.12.

1. 50·ES against 1000·VX on the 1,999 common days, coloured by the two
   regimes, with the fit on the 500 training days.
2. The z-score from 2008-08-04 with the band at ±1, the last training day
   marked, and each position the band holds shaded.
3. The test set's compounded cumulative return, with the three changes of
   position and 2011-08-05 marked.

```bash
uv run python -m chan.vx_es_figures
```

[tests/test_vx_es_figures.py](tests/test_vx_es_figures.py) holds what it draws
rather than its bytes, for the reason given above for the regime map.

[blog/aud-cad-rollover-lessons.md](blog/aud-cad-rollover-lessons.md) is a
twentieth post, about Example 5.2 of Chan's *Algorithmic Trading*, which adds
the rollover interest a currency position earns or pays overnight to a rule
that holds minus the sign of AUD.CAD's 20-day z-score. Chan reports an APR of
6.2 percent and a Sharpe ratio of 0.54 with rollover interest, 6.7 percent and
0.58 without it, and an annualised rollover interest of almost 5 percent. The
post draws five lessons from Entry 30 of the replication log.

1. The script's two printed figures and the book's four land every digit, and
   a constant scale on the closes moves none of them.
2. The book's "almost 5 percent" is not the rollover interest location 2273
   defines, which misses the pass mark at 3.26 percent a year, while the AUD
   rate alone and the difference over 365 days both land inside it.
3. The rollover the strategy earned was a cost of about half a point a year,
   because the rule held short on 707 days and long on 510.
4. The book's Sharpe ratio of 0.54 depends on the script filling a missing
   month's rate with zero.
5. An exact reproduction checks the arithmetic and not the edge.

Six groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The difference iB − iQ, which Chan calls "the interest differential" and
   "also called a rollover interest", the
   5 p.m. close, the T + 3 rule for a cross and the T + 1 exception for
   USD.CAD are at 2273. Adding the rollover interest to the cross rate's
   percent change, after Dueker (2006), is at 2287. The three claims, "even
   though", the linear mean-reverting strategy and the two central banks as
   the rates' sources are at 2303.
2. Facts outside the committed data. What T + 2 settlement is and why it makes
   one weekday pay three days, and that the MATLAB script kept the 16:59 bar
   of a minute file no public copy holds, which
   [src/chan/aud_cad_rollover.py](src/chan/aud_cad_rollover.py)'s docstring
   records. The script's line 50, `APR=0.061564 Sharpe=0.541802`, is pinned
   through its constants, and its line number was read at `e4bc46f`. So were
   two more readings of the script: that its line 44, the return without
   rollover interest, is commented out, and that it computes no rollover
   figure.
3. Arithmetic no test asserts: that 3.65 percent a year is 0.0001 a day, that
   the two monthly averages of 4.908 and 1.592 percent differ by about 3.3
   points, that the reading over 365 days is the one over 252 scaled by
   365 / 252, about 1.45, and that the rule holds short on 197 more days than
   long.
4. Three readings no test asserts: that the tripled day already pays for the
   weekends, so annualising over 365 days overstates the year, that long and
   short days cancel in total when they see about the same rollover interest,
   and that the stationary-candidates post finds the CAD/AUD rate reverting,
   which that post's own tests pin. That neither location 2303 nor the script
   mentions the zero fill is read from the book notes and the script.
5. The figure's alt text, whose readings of the lines, such as AUD staying
   above CAD in every month and the line without rollover interest sitting
   above the line with it on every day after January 2008, were measured once
   on the committed files and are not asserted.
6. Its references, cited rather than computed. Location 2287 cites Dueker
   and Neely's working paper as Dueker (2006). The book's bibliography, on
   page 192 of the print edition, names both authors and the series number,
   and the committed notes record that entry. The paper supplied its revision
   date and its DOI, and Crossref's record supplied its journal version.

Every other number in the post traces to an assertion in
[tests/test_aud_cad_rollover.py](tests/test_aud_cad_rollover.py), or to
[tests/test_aud_cad_rollover_figures.py](tests/test_aud_cad_rollover_figures.py)
for the figure's own numbers, among them the rates' extremes, the close's
low and high, where the two cumulative returns end, and their deepest fall
from 2008-07-30 to 2008-10-08. Three had no pin before it, and
[tests/test_aud_cad_rollover.py](tests/test_aud_cad_rollover.py) now pins
them.

1. The difference between the APR without rollover interest and the APR with
   it, 0.0055770095.
2. The net share of held days, (510 − 707) / 1,217, times the annualised
   rollover interest, −0.0052838233, against the rollover the strategy earned
   of −0.0052212787.
3. The rollover interest annualised over the days held long, 0.0328995788, and
   over the days held short, 0.0328677609.

Its one figure is drawn from the committed files by
[src/chan/aud_cad_rollover_figures.py](src/chan/aud_cad_rollover_figures.py),
which reads them through the same `read_sources` and `aud_cad_rollover` as
`python -m chan.aud_cad_rollover`, scale-break guard included. It draws three
panels on one date axis, for Lessons 1, 3 and 4.

1. The AUD and CAD monthly rates from July 2007, with the months each file
   lacks marked.
2. The AUD.CAD close, with the days held short and the days held long shaded.
3. The cumulative return with and without rollover interest, compounded as the
   script compounds it.

```bash
uv run python -m chan.aud_cad_rollover_figures
```

[tests/test_aud_cad_rollover_figures.py](tests/test_aud_cad_rollover_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.
[blog/bollinger-band-lessons.md](blog/bollinger-band-lessons.md) is a
twenty-first post, about Example 3.2 of Chan's *Algorithmic Trading*, which
trades Example 3.1's GLD and USO price spread with a Bollinger band instead of
the linear rule. It holds one unit at most, entering when the 20-day z-score
passes ±1 and leaving when it crosses 0. Chan reports an APR of 17.8 percent
and a Sharpe ratio of 0.96, "quite an improvement" on the linear rule, and the
script's closing comment prints six decimals. The post answers the Example 3.1
post's Lesson 5 and draws five lessons from Entry 26 of the replication log.

1. Both figures `bollinger.m` prints reproduce to six digits, and the book's
   17.8 percent and 0.96 are those figures rounded.
2. The band beats the linear rule on both measures the book names, on one
   spread with one lookback, and on its deepest drawdown and longest spell
   below a high too.
3. A fixed threshold makes the moving deviation's divisor matter, so dividing
   by n rather than n − 1 moves both figures.
4. The band holds one unit at most and changes its units on 162 days against
   the linear rule's 1,460, though a held unit's GLD leg is still resized
   every day.
5. An exact reproduction checks the arithmetic and not the edge.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The band as the rule for practical trading, "either zero or one unit (long
   or short) invested", "very easy to allocate capital to this strategy or to
   manage its risk", "a free parameter to be optimized in a training set" for
   the entry threshold, a lookback that "can be a free parameter to be
   optimized, or it can be set equal to the half-life of mean reversion", and
   "more round trip trades and generally higher profits" are at 1548. The 17.8 percent and 0.96, "quite an
   improvement from the linear mean reversal strategy", the thresholds of 1 and
   0, `fillMissingData` and Figure 3.3 are at 1559. "Near-optimal", "the
   benefit of hindsight" and "about 10.9 percent" are at 1505. The book's
   figures are pinned, and its words are not.
2. Facts outside the committed data. That a second public copy of Chan's code
   holds `bollinger.m` byte for byte, which `src/chan/bollinger.py`'s docstring
   records, and that the file was converted to one file per ETF, which
   [data/README.md](data/README.md) records.
3. Arithmetic no test asserts: that a z-score such as 0.99 moves beyond 1
   once multiplied by 1.0260, and that the factor cancels from the linear
   rule's return, which the Example 3.1 post shows. The equation for the factor is pinned at four
   decimals and on every day.
4. The book's Figure 3.3, which the post's figure redraws from the script's
   `plot` call and which nothing compares with the book's own. The alt text's
   description of shapes, such as the band ending well above the linear rule
   and the dashed line running close to the band, is read off the drawing
   rather than asserted.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_bollinger.py](tests/test_bollinger.py), to
[tests/test_price_spread.py](tests/test_price_spread.py) for Example 3.1's
book figure of 10.9 percent against its script's 10.8, the file's 1,500 days
and the hedge ratio's 334 days below zero, to
[tests/test_series.py](tests/test_series.py) for the file's 67 ETFs, or to
[tests/test_bollinger_figures.py](tests/test_bollinger_figures.py) for the
figure's own numbers. Seven had no pin before it.
[tests/test_bollinger.py](tests/test_bollinger.py) now pins the first six, and
[tests/test_bollinger_figures.py](tests/test_bollinger_figures.py) pins the
seventh.

1. Each rule's deepest drawdown and longest spell below a high. The band's is
   −21.83 percent on 2009-05-21 and 252 days from 2008-12-08 to 2009-12-07.
   The linear rule's is −34.24 percent on 2009-01-06 and 640 days from
   2008-12-08 to 2011-06-22. Both spells follow a high on 2008-12-05, and the
   band's is under half as long.
2. The band's 162 changes of units, split into 77 entries from flat, 76 exits
   to flat and 9 turns from one side to the other in a single day, with the
   run ending on a unit held.
3. The 62 days on which the band is flat and the hedge ratio is below zero,
   two different counts that are both 334.
4. Dividing the deviation by n multiplies every z-score by √(20/19), 1.0260.
   It puts the z-score beyond ±1 on 777 of the 1,461 days where it exists,
   against 756 under n − 1, and moves the units on 15 days. The exit test at 0
   passes on the same days under either divisor. All 76 exits under n − 1 fall
   on the same days under n, and a 77th under n, on 2007-06-07, closes a short
   entered on 2007-05-29 that the n − 1 run never opened.
5. That the spread has no missing values on the kept days, which is why
   swapping the moving average as well moves nothing further.
6. That the hedge ratio changes on all 1,479 steps between the 1,480 days, so a
   held unit's GLD leg is resized every day.
7. The figure's own lines and labels.

Its one figure is drawn from the committed file by
[src/chan/bollinger_figures.py](src/chan/bollinger_figures.py), which reads it
through the same `read_sources` and `example_three_two` as
`python -m chan.bollinger`, scale-break guard included. It draws three panels
on one date axis, for Lessons 1, 3 and 4.

1. The 20-day z-score, with the band's lines at −1, 0 and 1.
2. The units held, −1, 0 or 1.
3. The band's cumulative return, the book's Figure 3.3, beside the linear
   rule's, with the band divided by n dashed as a diagnostic.

```bash
uv run python -m chan.bollinger_figures
```

[tests/test_bollinger_figures.py](tests/test_bollinger_figures.py) holds what
it draws rather than its bytes, for the reason given above for the regime map.

[blog/kalman-hedge-lessons.md](blog/kalman-hedge-lessons.md) is a
twenty-second post, about Kindle locations 1633 to 1726 of Chan's
*Algorithmic Trading*, where a Kalman filter re-estimates the slope and intercept of EWC on EWA every
day and trades the filter's forecast error against a band its own forecast
variance sets. Chan reports an APR of 26.2 percent and a Sharpe ratio of 2.4.
The post draws four lessons from Entry 32 of the replication log.

1. Both figures land on every digit of the script's closing comment, and the
   book rounds them correctly.
2. The script shorts EWC alone on the file's first day, before the filter has
   any estimate, and with no signal on the first two days the figures round
   to 26.1 percent and 2.3.
3. Location 1726's two claims carry no verdict, because their only criteria
   were written after a first run, and the grain chosen decides whether the
   intercept rises "monotonically".
4. An exact reproduction checks the arithmetic and not the edge, since the
   two constants are Chan's and the script charges no cost.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   Example 3.2's band, entered at one standard deviation and exited at the
   mean, is at 1559. "An abrupt and artificial impact on the hedge ratio" is
   at 1633, "the expected value of a hidden variable" at 1644, the slope and
   intercept as the hidden state at 1658, and the intercept "in place of the
   moving average of the spread" at 1678. The two claims, the forecast error
   as "the deviation of the spread EWC-EWA from its predicted mean value", the
   rest of the code being `bollinger.m`'s, and "a reasonable APR of 26.2
   percent and a Sharpe ratio of 2.4" are at 1726. The market-making use is at
   1760. The book's figures are pinned, and its words are not.
2. Facts about the script rather than the data: its comment on `delta`, its
   zero start, and its chart of the forecast error plotting `e(3:end)` and
   `sqrt(Q(3:end))`, which the script holds at `e4bc46f` of
   ericnberwick/EpchanPreview, git blob `e2f8a62`.
   [src/chan/kalman_hedge.py](src/chan/kalman_hedge.py)'s docstring records
   the zero start and the two rows the plot leaves out, but not those words.
3. Readings no test asserts: that the gain is large when the filter is unsure
   and small when it is confident, that starting the filter from a regression
   would need data from before the file's first day, and that a filter
   started from the whole-file intercept might show no rise.
4. The figure's alt text, whose readings of the lines, such as "about 1.4"
   and "about 2.9 by September 2008", are approximate by design.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_kalman_hedge.py](tests/test_kalman_hedge.py), to
[tests/test_kalman_hedge_figures.py](tests/test_kalman_hedge_figures.py) for
the figure's own numbers, to
[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py) and
[tests/test_etf_cointegration_figures.py](tests/test_etf_cointegration_figures.py)
for the slope of 0.9624 and the intercept of 6.4113 of one regression over the
whole file, or to [tests/test_price_spread.py](tests/test_price_spread.py) for
the 20-day window of the earlier post's rolling slope. Four had no pin before
it.

1. Row 1's forecast error is EWC's whole close of 22.95, exactly.
2. The short on EWC alone earns 0.0074074 on 2006-04-27, and the run with no
   signal on rows 1 and 2 holds the script's units from row 3 on, so their
   returns differ only on 2006-04-27 and 2006-04-28.
3. The script holds a long on 358 days, a short on 350 and nothing on 792, and
   its units change from one day to the next 875 times.
4. The cumulative return the last panel draws ends at 2.999998 for the script
   and 2.970231 with no signal on rows 1 and 2, which the alt text reads as
   about 300 percent.

Two more were pinned when Lesson 3 gained them after the post first merged. A
300-day rolling mean of the intercept falls on 25 of its 1,200 steps, and a
350-day one on none of its 1,150.

Its one figure is drawn from the committed file by
[src/chan/kalman_hedge_figures.py](src/chan/kalman_hedge_figures.py), which
reads it through the same `read_sources` and `kalman_hedge` as
`python -m chan.kalman_hedge`, scale-break guard included. It draws four
panels on one date axis, after the book's Figures 3.5 to 3.8.

1. The slope over all 1,500 rows, with its zero start marked and a line at 1.
2. The intercept, with each year's mean drawn flat over its year and its
   highest value marked.
3. The forecast error and the band from row 3, with a note naming rows 1 and
   2.
4. The cumulative return of the script and, dashed, of the run with no signal
   on rows 1 and 2.

```bash
uv run python -m chan.kalman_hedge_figures
```

[tests/test_kalman_hedge_figures.py](tests/test_kalman_hedge_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/index-arbitrage-lessons.md](blog/index-arbitrage-lessons.md) is a
twenty-third post, about Example 4.2 of Chan's *Algorithmic Trading*, which
tests each stock in his 2012 S&P 500 file against SPY over 2007 with the
Johansen test, holds the ones that pass as one basket, and trades the basket
against SPY from 2008. Chan reports 98 stocks, a basket that cointegrates with
SPY "with better than 95 percent probability", an APR of 4.5 percent and a
Sharpe ratio of 1.3. The post draws four lessons from Entry 24 of the
replication log.

1. Every figure `indexArb.m` prints reproduces to its last digit, with Chan's
   signs on the eigenvectors, while the claim of better than 95 percent holds
   for the trace test and fails for the eigen test.
2. The screen's 98 is a count of tests passed, and random walks unrelated to
   SPY pass the same screen more often than the stocks do.
3. The basket's two relations with SPY make the same full-rank claim as the
   Entry 23 post's pair, and the ADF test rejects a unit root for neither
   series alone.
4. The 4.5 percent is in-sample on its lookback and survivor-only.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "Such a well-known strategy that the difference in market values has become
   extremely small" and picking "all the stocks that cointegrate individually
   with the ETF" are at 2006. "With at least 90 percent probability" and "an
   arbitrary assignment of equal capital weight" are at 2027. The 98 stocks
   "each separately", "better than 95 percent probability", "two cointegrating
   relations", "the one with the largest eigenvalue", the equal weight on each
   stock, "the benefit of hindsight", the 4.5 percent and 1.3, "the
   performance decreases as time goes on", the universe shared with Example
   4.1 and Figure 4.3 are at 2035. "A maximum of 12 symbols" and eigenvectors
   with "both long and short stock positions" are at 2066. "Has survivorship
   bias" is at 1974. The book's figures are pinned, and its words are not.
2. Facts outside the committed data. That a second public copy of Chan's code
   holds `indexArb.m` byte for byte, which `src/chan/index_arbitrage.py`'s
   docstring records, that both files were converted to one file per symbol,
   which [data/README.md](data/README.md) records, that the stock file holds
   the index as Chan held it on 2012-04-24, the date in its name, and that the
   committed index holdings under `research/filings/ivv/` start at the end of
   2008.
3. Arithmetic and readings no test asserts: the nominal 48 as 10 percent of
   480, that a 90 percent bar bounds how often the test rejects with no
   relation rather than giving a probability about one stock, and that four
   years of returns are unlikely to separate a decline from noise.
4. The book's Figure 4.3, which the post's figure redraws from the script's
   `plot` call and which nothing compares with the book's own. The alt text's
   description of the curve's shape, such as its steep climb from late 2008
   and its high in late 2010, is read off the drawing rather than asserted.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_index_arbitrage.py](tests/test_index_arbitrage.py) or to
[tests/test_index_arbitrage_figures.py](tests/test_index_arbitrage_figures.py)
for the figure's own numbers. Three had no pin before it.

1. The 98 stock weights together, 107.198, against SPY's −105.560, a
   difference of 1.638, so one unit is close to as long in stocks as it is
   short in SPY.
2. The cumulative return ends at 0.206422 and sits at zero until 2008-01-09.
3. The stocks pass the screen at 20.4 percent and the random walks at 28.1
   percent.

[tests/test_index_arbitrage.py](tests/test_index_arbitrage.py) pins the first,
and [tests/test_index_arbitrage_figures.py](tests/test_index_arbitrage_figures.py)
pins the other two with the figure's lines and labels.

Its one figure is drawn from the committed files by
[src/chan/index_arbitrage_figures.py](src/chan/index_arbitrage_figures.py),
which reads them through the same `read_sources` and `index_arbitrage` as
`python -m chan.index_arbitrage`, scale-break guard included. It draws two
panels.

1. The book's Figure 4.3, the cumulative return over the 1,076 test days,
   against the date rather than the row number.
2. The share of series the screen passes over 2007, 98 of 480 stocks beside
   561 of 2,000 random walks unrelated to SPY, with the 90 percent bar's
   nominal 10 percent as a line. The walks come from
   `chan.index_arbitrage.walks_unrelated_to`, the same function the pin of
   561 reads.

```bash
uv run python -m chan.index_arbitrage_figures
```

[tests/test_index_arbitrage_figures.py](tests/test_index_arbitrage_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/usdcad-stationarity-lessons.md](blog/usdcad-stationarity-lessons.md) is a
twenty-fourth post, about Examples 2.1 to 2.5 of Chan's *Algorithmic Trading*,
which test USD.CAD for mean reversion four ways and then trade it with the
linear rule over a lookback of the half-life. Chan reports an ADF statistic of
about −1.84, an H of 0.49 and a half-life of 115 days, and says the trade's P&L
"manages to be positive, albeit with a large drawdown". The post draws five
lessons from Entry 22 of the replication log.

1. Four statistics land every digit the script prints, so the closes are
   Chan's, and the ADF test cannot reject a random walk.
2. The ADF figure depends on the toolbox, because jplv7's `adf` fits one row
   fewer than `adfuller` at the same lag.
3. H misses 0.49 by less than chance moves it. Under both implementations
   Chan's code uses, each estimate sits within about one standard deviation of
   its own estimator's average on random walks of the same length, and
   starting the sample a day later moves `genhurst` to 0.49. So an H this
   close to 0.5 cannot be told from a random walk on 1,216 days, and the
   variance ratio test cannot reject one either.
4. The trade ends positive after a fall more than five times its final P&L,
   short on every day of that fall and at its largest short inside it.
5. The lookback came from the closes the rule traded, so the result checks the
   arithmetic and not whether the trade would pay.

Five passages point at the forty-eighth post below, which trades the rule after
2012 at the same lookback: the opening's note on what the reproduction cannot
say, Lesson 5's paragraph on avoiding the look-ahead and the caption of its
look-ahead sketch, the third item in what the post cannot say, and the fifth
habit. None of them quotes its statistics.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its page in the 2013 print edition of
   *Algorithmic Trading* and recorded by Kindle location in
   [its committed notes](research/book-notes/algorithmic-trading.md). Most
   prices as random walks is on page 39, the variance growing like τ²ᴴ on 41,
   the critical value and its table on 42, the reading of the statistic and of
   λ on 44, H's meaning on 44 and 45 and the 0.49 on 45, the variance ratio
   test as H's significance test on 45, the half-life on 46 and 47 and the
   warning about round trips on 47, the case for trading below 90 percent
   certainty on 47, the linear rule on 48, the claim on 49 and its three
   cautions on 49 and 50, the case for testing before a backtest on 50, the
   23-day half-life on 58 and the lookback with no parameters to optimize on
   60. Each page came from searching the quoted sentence in Google Books'
   preview of that edition, and no test checks it. The book's figures are
   pinned, and its words are not.
2. Facts about the code rather than the data: that jplv7 trims one more row
   when it lines up the lagged close, that `genhurst` averages over windows of
   5 to 19 days, that every copy of it a search found is dated 2013-01-30 and
   runs one algorithm, that Chan's 2018 Python port fits the log variance of
   τ-day changes on log τ, that `genhurst` counts its sampled closes from the
   first while the port uses every overlapping change, and that the port and
   `ithildincore` both run `adfuller`.
   [src/chan/stationarity_tests.py](src/chan/stationarity_tests.py),
   [src/chan/usdcad_mean_reversion.py](src/chan/usdcad_mean_reversion.py) and
   [src/chan/usdcad_hurst_noise.py](src/chan/usdcad_hurst_noise.py) record each
   in their docstrings.
3. Readings no test asserts: that about two-thirds of a bell-shaped spread
   lands within one standard deviation of its average, that each day keeps
   roughly 99.41 percent of its
   distance from the mean, that a p-value of 0.367 means a random walk gives a
   ratio this far from 1 more than a third of the time, that none of the four
   statistics depends on the units of the closes, that a random walk has no
   half-life, and that a fall in a commodity currency fits the autumn of 2008,
   which the post says nothing here tests.
4. The figures' alt text, whose readings of the lines, such as "near 1.05",
   "about 0.92 in late 2007" and "about −3.9 in early August", are approximate
   by design. The book's own chart
   of the cumulative P&L, its Figure 2.3, is not compared with the redraw. The
   post cites that number from the caption recorded in
   [research/book-notes/algorithmic-trading.md](research/book-notes/algorithmic-trading.md),
   and [tests/test_book_notes.py](tests/test_book_notes.py) fails if the two
   disagree.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_usdcad_mean_reversion.py](tests/test_usdcad_mean_reversion.py), to
[tests/test_tu_momentum.py](tests/test_tu_momentum.py) for H at a `maxT` of
24, to [tests/test_stationary_candidates.py](tests/test_stationary_candidates.py)
for the 141.6-day half-life, to
[tests/test_etf_cointegration.py](tests/test_etf_cointegration.py) for the
book's 23 days, or to
[tests/test_usdcad_mean_reversion_figures.py](tests/test_usdcad_mean_reversion_figures.py)
for the charts' own numbers, or to
[tests/test_usdcad_tests_whiteboard.py](tests/test_usdcad_tests_whiteboard.py)
for the whiteboard sketches' labels. Eight had no pin before it, and
[tests/test_usdcad_mean_reversion.py](tests/test_usdcad_mean_reversion.py)
now pins them all, reading the position from the run's own `market_value`.

1. The closes on the drawdown's two dates, 1.00835 and 1.29485, a rise of 28.4
   percent.
2. The largest short, −4.12 on 2008-10-10 inside the fall, and the largest
   long, 3.04 on 2009-05-29.
3. The close on the day of the largest short, 1.17325, the further 10.4
   percent it rose by the trough, and the short of −3.83 held there.
4. The rule is short on all 69 days of the fall.
5. The rule holds a short on 488 days and a long on 613 of the 1,101 it holds
   anything.
6. The P&L ends 2008 at −0.2552, and the rest of the run adds 0.3693.
7. The run ends 0.0180 below its high, after climbing 0.6246 from its low.
8. The 1,216 closes span 10.6 half-lives.

Its two charts, both in Lesson 4, are drawn from the committed file by
[src/chan/usdcad_mean_reversion_figures.py](src/chan/usdcad_mean_reversion_figures.py),
which reads it through the same `read_sources` and `stationarity_tests` as
`python -m chan.usdcad_mean_reversion`, scale-break guard included. The first,
`usdcad_mean_reversion.png`, draws two panels on one date axis.

1. The 1,216 closes with their 115-day moving average.
2. The cumulative P&L, the script's plot, with the fall from 2008-07-22 to
   2008-10-27 shaded.

The second, `usdcad_fall_position.png`, draws three panels on one date axis
over that fall alone.

1. The closes with their moving average and dashed rungs 1 to 4 moving
   standard deviations above it.
2. The position the rule held at each close, from `market_value`, which the
   script does not plot.
3. The cumulative P&L, with its high and its low marked.

```bash
uv run python -m chan.usdcad_mean_reversion_figures
```

[tests/test_usdcad_mean_reversion_figures.py](tests/test_usdcad_mean_reversion_figures.py)
holds what both draw rather than their bytes, for the reason given above for
the regime map.

The post also carries fourteen looping whiteboard sketches, drawn by
[src/chan/usdcad_tests_whiteboard.py](src/chan/usdcad_tests_whiteboard.py).
Each sits after the text it draws.

1. One in the opening section, `usdcad_tests_every_day.gif`.
2. Six in the section on the tests, `usdcad_tests_question.gif`,
   `usdcad_tests_adf.gif`, `usdcad_tests_hurst.gif`,
   `usdcad_tests_variance_ratio.gif`, `usdcad_tests_half_life.gif` and
   `usdcad_tests_linear_rule.gif`.
3. Two in Lesson 1, `usdcad_tests_no_rejection.gif` and
   `usdcad_tests_fingerprint.gif`.
4. One in Lesson 2, `usdcad_tests_one_row.gif`.
5. Two in Lesson 3, `usdcad_tests_noise_band.gif` and
   `usdcad_tests_lean_not_cross.gif`.
6. Two in Lesson 5, `usdcad_tests_look_ahead.gif` and
   `usdcad_tests_half_lives.gif`.

```bash
uv run python -m chan.usdcad_tests_whiteboard
```

[tests/test_usdcad_tests_whiteboard.py](tests/test_usdcad_tests_whiteboard.py)
holds what each sketch says and draws, that every number a sketch prints is
read from the run or from the random-walk measurement, and that a run whose
figures would make a sketch's words false is refused. It compares
each committed GIF with a fresh draw byte for byte only on macOS arm64 in
Comic Sans MS, where the files were drawn, because the hand font is whichever
one is installed.

[blog/khandani-lo-reversal-lessons.md](blog/khandani-lo-reversal-lessons.md)
is a twenty-fifth post, about Examples 4.3 and 4.4 of Chan's *Algorithmic
Trading*, which run the first book's Khandani-Lo reversal again on his 2012
panel of 497 stocks over 2007 to 2011. Chan reports an APR of 13.7 percent and
a Sharpe ratio of 1.3 for the close-to-close rule, with 30 percent in 2008 and
11 percent in 2011, and 73 percent and 4.7 for the intraday rule. The post
links the earlier post on the first book's rule rather than repeating it, and
draws four lessons from Entry 19 of the replication log.

1. Every figure the book prints lands on Chan's own file, and so do the two
   the script printed at six decimals, though two of the book's roundings have
   little room.
2. The match needs CAH's prices of 2009-08-31 to 2009-09-02, which read as a
   data error or a corporate action, so a cleaner file would miss both of
   Example 4.3's figures.
3. Most of the rise from the first book's 0.25 to this book's 1.3 comes from
   the data and the window rather than the rule, and two days the cut zeroes
   carry 0.1313 of the rule's 0.2974.
4. Costs still take most of the first book's rule's edge on the panel, but
   they cost 0.6924 of a day's profit there against 13.7453 times it on 2006,
   because the profit is about twenty times larger and the trading barely
   changes.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   Cross-sectional mean reversion, "and vice versa", and "the same total gross
   capital of $1" are at 2087. "Almost perfectly dollar neutral", "the year of
   Lehman Brothers' bankruptcy" and "a true out-of-sample test, as the
   strategy was published in 2007" are at 2110. The intraday version is at
   2124, and the doubled costs and the noise of the open at 2135. The 4.7 set
   against momentum is at 2890. The book's figures are pinned, and its words
   are not.
2. Facts about the script rather than the data: that both of its `plot` lines
   compound, that its cost lines are commented out, and that its comment for
   Example 4.3 reads 13.7 percent and 1.3, which `andrewlo_2007_2012.m` holds
   at `e4bc46f` of ericnberwick/EpchanPreview. That a second copy holds the
   script byte for byte is recorded in
   [src/chan/khandani_lo_book_two.py](src/chan/khandani_lo_book_two.py)'s
   docstring.
3. Readings no test asserts: that most of the scale-break guard's flags on
   this window fall in the 2008 crisis, that CAH's prices read as a data error
   or a corporate action, and that a longer stretch of survivors leaves out
   more of the companies that left the index. The survivor horizons of five
   years and under two are arithmetic on the two files' membership dates.
4. Ratios the post takes between pinned figures in words: about five times,
   nearly four times, four times the average return, about the same standard
   deviation, more than twice, by about a third, and less than a third. So is
   what a figure would print as at the book's precision, such as 1.2, 10, 13.3
   and 0.731552.
   The figure's alt text reads its curves approximately too, such as "about 70
   percent" and "about 1,460 percent".
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_khandani_lo_book_two.py](tests/test_khandani_lo_book_two.py), to
[tests/test_khandani_lo_book_two_figures.py](tests/test_khandani_lo_book_two_figures.py)
for the figure's own numbers, or to
[tests/test_khandani_lo.py](tests/test_khandani_lo.py) for the first book's
0.2510, −3.1884 and −3.2337 and its average day on 2006. Four had no pin
before it.

1. Each calendar year's APR for both examples, 2007 to 2011, and Example
   4.4's falling in every year after 2008.
2. Each example's annual mean and standard deviation, 0.1338 and 0.1063 for
   Example 4.3 and 0.5565 and 0.1181 for Example 4.4.
3. The bridge differences, 0.2974 for the rule, 0.1313 of it for the two days
   the cut zeroes, which is 0.44 of the rule's share, and 0.7111 still to go.
   Entry 19 had printed the second as 0.1314, taken on rounded figures.
4. The first book's rule's average day on the panel: a profit of 10.5234 and a
   cost of 7.2868 basis points of its position, 0.6924 of the profit, a
   turnover of 1.4574, and a profit 19.94 times 2006's.

Its one figure is drawn from the committed panel by
[src/chan/khandani_lo_book_two_figures.py](src/chan/khandani_lo_book_two_figures.py),
which reads it through the same `close_to_close` and `open_to_close` as
`python -m chan.khandani_lo_book_two`. That module computes across the scale
breaks the guard would refuse, as its docstring decides, so the figure does
too. It draws two panels on one date axis, each with every calendar year's APR
above its span.

1. Example 4.3's compounded cumulative return, the book's Figure 4.4, with
   2008 and 2011 shaded.
2. Example 4.4's on its own axis, for which the book draws no figure.

```bash
uv run python -m chan.khandani_lo_book_two_figures
```

[tests/test_khandani_lo_book_two_figures.py](tests/test_khandani_lo_book_two_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/aud-cad-johansen-lessons.md](blog/aud-cad-johansen-lessons.md) is a
twenty-sixth post, about Example 5.1 of Chan's *Algorithmic Trading*, which
trades AUD.USD against CAD.USD in weights a rolling Johansen test supplies each
day. Chan reports an APR of 11 percent and a Sharpe ratio of 1.6 from
2009-12-18 to 2012-04-26. The post links the earlier posts on the Johansen
test, the linear rule, rollover interest, the Kelly leverage, Chan's stationary
candidates and the gold miners rather than repeating them, and the later post
on Chapter 8's leverage for where the book's Kelly of 18.4 most likely came
from. It draws six lessons from Entry 25 of the replication log.

1. Every figure the script prints matches, because every one of the 612
   returns matches the one Chan's script saved, within a criterion written
   before any return was computed.
2. The match ties the traded closes to the ones Chan's MATLAB read up to a
   constant scale on each leg, and no more. The closes before the test period
   are checked only as far as they move a hedge.
3. The Johansen test rarely found a relation behind the hedge it supplied. The
   trace test finds a relation in 26 of the 612 windows, in three stretches,
   and two relations in 19 of them.
4. The hedge is a capital weight that wandered. It held both currencies the
   same way on 90 days, 85 of them from 2010-06-01 to 2010-10-05, and those
   days carried about two fifths of the growth in log terms with twice the
   volatility, though a Welch t of 1.09 cannot rule out chance.
5. The Python port's version of the example is a different strategy, so its
   printout is no check on the data.
6. An exact reproduction checks the arithmetic, not the edge.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The point move of equal dollar value is at 2169, and the commodity
   currencies at 2173. The base and quote currencies, the AUD.ZAR quote of
   9.58, the capital weights and the sale of USD.CAD are at 2186. Rollover
   interest "usually not large for short-term strategies" is at 2205. "A
   classic linear mean-reverting strategy", the gross market value, "better
   results in hindsight", the 11 percent and 1.6 and the caption of Figure
   5.1 are at 2237. The Kelly leverage of 18.4 is at 3342. The book's 11
   percent and 1.6 are pinned, and so is its 18.4, as a book target in
   `TestTheDeclaration::test_the_printed_figures` in
   [tests/test_monte_carlo_leverage.py](tests/test_monte_carlo_leverage.py).
   Its words and its 9.58 are not.
2. Facts about the script and the port rather than the data: the comments on
   lines 60 and 66 of `AUDCAD_unequal.m`, which ericnberwick/EpchanPreview
   holds at `e4bc46f`, that the script loads two minute files neither public
   copy carries, that line 57 plots against the row number, and that the
   port ends both windows a day earlier and prints a Sharpe ratio of
   1.362926. So is that the files quote six decimals.
3. Readings no test asserts: that the two rates are close to random walks,
   that the test has little power against them, that a position held both
   ways is a bet on the US dollar's direction, and that wider swings are what
   such a bet gives. That neighbouring windows share 249 of their 250 days
   is arithmetic on the window length. That CAD/AUD tested stationary over
   nineteen years is the stationary-candidates post's, listed under its
   entry above.
4. Ratios and differences the post takes from pinned figures in words: about
   three quarters, about twice as wide, 15 percent of the days, the 586 days
   left when 26 of 612 are taken away, and that a move of 0.01 is worth one
   cent. The figure's alt text reads its curves approximately too, such as
   "near −0.64" and "about 0.32", and it names the dates of two one-day moves,
   2010-05-20 and 2010-07-06, read from the drawn line.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_aud_cad_johansen.py](tests/test_aud_cad_johansen.py), or to
[tests/test_aud_cad_johansen_figures.py](tests/test_aud_cad_johansen_figures.py)
for the figure's own numbers. The post also cites the Chapter 8 post's
finding on 18.4, that no series with Example 5.1's printed Sharpe ratio and
APR reaches it under three ways of compounding the APR, and that finding
traces to `TestRowGroup13TheEighteenPointFourGap` in
[tests/test_monte_carlo_leverage.py](tests/test_monte_carlo_leverage.py). Six
of the post's numbers had no pin before the post.

1. The three stretches the trace test's 26 windows fall in, which hold the 19
   two-relation windows, and the stretch the eigen test's 11 fall in.
2. The 90 days the hedge held both currencies the same way, the 85 of them
   from 2010-06-01 to 2010-10-05, the longest run of 65 days, and that none
   falls in a window the trace test backed.
3. The last day's hedge as CAD.USD's share of the gross, −0.4325.
4. The 90 days compounded alone to 0.1074 and the other 522 to 0.1696, so the
   90 carried 0.394 of the growth in log terms.
5. The compounded return of 0.0214 on 2010-05-31 and 0.1170 on 2010-10-05.
6. The two groups' standard deviations of 0.0073 and 0.0035, their means, and
   a Welch t of 1.09 with a p-value of 0.28.

Its one figure is drawn from the committed files by
[src/chan/aud_cad_johansen_figures.py](src/chan/aud_cad_johansen_figures.py),
which reads them through the same `read_sources` and `aud_cad` as
`python -m chan.aud_cad_johansen`, so the scale-break guard runs. It draws two
panels on one date axis over the 612 test days.

1. Each day's hedge as CAD.USD's signed share of the gross, with the 90
   same-way days shaded and the trace test's 26 windows marked.
2. The compounded cumulative return, the book's Figure 5.1, against the date.

```bash
uv run python -m chan.aud_cad_johansen_figures
```

[tests/test_aud_cad_johansen_figures.py](tests/test_aud_cad_johansen_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/roll-returns-lessons.md](blog/roll-returns-lessons.md) is a
twenty-seventh post, about Example 5.3 of Chan's *Algorithmic Trading*, which
splits five futures' returns into a spot return and a roll return under a
model that holds both constant, and prints the averages as Table 5.1. The post
links the earlier posts on calendar spreads and on VX against ES for what a
futures contract and a roll are, and draws four lessons from Entry 27 of the
replication log.

1. Eight of Table 5.1's ten cells land on Chan's own files, and HG's and TU's
   spot returns miss there, so no vendor's revision explains either.
2. The script regresses on contract columns where the text says months, so it
   overstates C's, HG's and TU's roll returns by 2.4, 2.0 and 3.0 times.
3. With maturity in months, HG's roll return falls below its spot return and
   C's falls short of twice its spot return, so each of the book's two claims
   fails for one future.
4. CL's roll return, the series behind the table's mean, sits in contango on
   most days, changes sign 29 times and reaches −1.121372, and HG's changes
   sign 198 times, with no criterion for location 2683's "does not vary very
   often" written down before the counts.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The roll return as "an intrinsic part of its total return", backwardation
   and contango are at 2326. The model and "total return = spot return + roll
   return" are at 2364. The loss of more than \$100,000 in 2006 and the ETF of
   commodity producers are at 2385. "Measured in months", the forward curve's
   gloss, "much larger than that of the spot returns" and "a slowly varying
   estimated γ" are at 2399. "Bigger in magnitude than their spot returns" and
   "the sign of roll returns does not vary very often" are at 2683. The book's
   figures are pinned, and its words are not.
2. Facts about the script rather than the data: that it numbers the days with
   `T=[1:length(spot)]'`, prints with `%f`, and annualizes by 252 and by −12,
   which `estimateFuturesReturns.m` holds at `e4bc46f` of
   ericnberwick/EpchanPreview, and that its Python port dates from 2018. The
   figure number the caption cites, 5.5, is the one the notes record at
   location 2399, which
   [tests/test_book_notes.py](tests/test_book_notes.py) holds, and the book's
   chart is compared with the redraw only by its first and last days.
3. Readings no test asserts: the algebra of the model, that a held contract
   earns α + γ and that one day's log prices fall on a line of slope −γ, and
   the reading of location 2385 that the roll return separates a producer
   ETF from the commodity's future.
4. Figures the post rounds from pinned ones or takes between them in words:
   0.0039 percent, "a little over half", and "less than four months later".
   The figure's heading test holds 5.06 and 3.86 percent. The figure's alt text reads its bars and its line
   approximately too, such as "about 5.3" and "about −1.1".
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_roll_returns.py](tests/test_roll_returns.py), or to
[tests/test_roll_returns_figures.py](tests/test_roll_returns_figures.py) for
the figure's own numbers. Four had no pin before it, and
`TestBesideThePost` there now pins them all.

1. CL's γ is negative on 1,388 of its 1,941 days and positive on 552. On
   2006-01-05 its five settlements run 65.38 to 65.41 and back, so it is zero
   apart from rounding, and the sign counts skip that day.
2. It changes sign 29 times, and its longest run of one sign is contango from
   2008-10-09 to 2011-10-21, 766 days.
3. Its highest value is 0.258871 on 2008-09-22 and its lowest −1.121372 on
   2009-01-15.
4. BR's γ is negative on 3 of its 4,210 days, and HG's is positive on 3,139 of
   its 6,028 days and changes sign 198 times.

Its one figure is drawn from the committed strips by
[src/chan/roll_returns_figures.py](src/chan/roll_returns_figures.py), which
reads them through the same `load_strip` and `strip_returns` as
`python -m chan.roll_returns`, scale-break guard included. It draws two panels,
for Lessons 3 and 4.

1. Each strip's spot return, the script's roll return and the month-spaced
   roll return as bars, with a tick at twice the spot return over BR, C and TU.
2. CL's roll return day by day, the book's Figure 5.5, shaded for
   backwardation and contango, with its mean.

```bash
uv run python -m chan.roll_returns_figures
```

[tests/test_roll_returns_figures.py](tests/test_roll_returns_figures.py) holds
what it draws rather than its bytes, for the reason given above for the regime
map.

[blog/tu-hypothesis-tests-lessons.md](blog/tu-hypothesis-tests-lessons.md) is
a twenty-eighth post, about Example 1.1 of Chan's *Algorithmic Trading*, which
asks three ways how often chance alone would match his TU momentum strategy.
The book reports that 1,166 of 10,000 simulated return series do as well and
that not one of 100,000 shuffles of the entry days does. Comments in Chan's
script give a Gaussian statistic of 2.93 and, for the second test, a p-value
of 0.027500. The post restates the rule from location 642 and draws five
lessons from Entry 37 of the replication log.

1. The Gaussian test lands the script's 2.93.
2. A simulated count lands only within sampling error, so the seed and a band
   of two binomial standard errors come before the draw. The second test lands
   the book's 1,166 and misses the script's 0.027500.
3. The second test does not give the script's 0.027500. A check added after a
   trial run, the observed positions applied to the simulated returns, matches
   it, nothing in the script runs that check, and what computed the figure
   stays unknown.
4. The third test as printed cannot fail, and corrected it still finds no
   shuffle as good as the rule.
5. Two of the three checks added after a trial run point at TU's drift rather
   than its kurtosis as what drives the second test, which is exploratory and
   motivates a registered test rather than confirming one.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The four steps of a hypothesis test and the null hypothesis are at 593, the
   Gaussian null at 606, simulated prices at 616, simulated trades and Lo,
   Mamaysky and Wang at 623, the rule at 642, the mean and shape as luck at
   652, the 1,166 and the aside on the mean at 665, the shuffled entry dates
   at 669, the 0 of 100,000 at 672, the kurtosis reading at 674, the roll
   return's definition at 2326, the roll return behind TU's momentum at 2683
   and the 12 percent at 2923. The book's figures are pinned, and its words
   are not.
2. Facts about the script rather than the data: that it writes the shuffled
   tranches into `pos` rather than `pos_sim`, that its comments print 2.93 and
   0.027500, that its file has one commit, and that MathWorks does not state
   the criterion `pearsrnd` uses.
   [src/chan/tu_hypothesis_tests.py](src/chan/tu_hypothesis_tests.py) records
   each in its docstring.
3. Readings and arithmetic no test asserts: that if the true chance equals the
   printed proportion, two standard errors either side cover about 95 percent
   of counts, that a rerun lands inside less often because Chan's own count is
   one random draw, that a normal distribution's kurtosis is 3, that 1,166 of
   10,000 is 0.1166, that 20 million is 10,000 series of 2,000 days, that 49 is
   seven lookbacks against seven holds, that the rule of three bounds a
   p-value at 3/N, that a position nearly the same on every shuffle earns
   nearly the same mean on the same returns, and that a rule net long on most
   days collects a drift wherever its entries fall.
4. The figure's alt text, whose readings of the histograms, such as "near
   3e-5" and "from about 1e-5 to 4e-5", are approximate by design.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_tu_hypothesis_tests.py](tests/test_tu_hypothesis_tests.py), to
[tests/test_tu_momentum.py](tests/test_tu_momentum.py) for the seven periods
behind the 49 pairs, or to
[tests/test_tu_hypothesis_tests_figures.py](tests/test_tu_hypothesis_tests_figures.py)
for the figure's own numbers. Four groups of them had no pin before it, and
[tests/test_tu_hypothesis_tests.py](tests/test_tu_hypothesis_tests.py) now pins
them all.

1. The strategy's daily standard deviation, 1.010320e-03, and the Gaussian
   null's spread of the mean, 2.259145e-05, in closed form.
2. The spreads of the simulated means on seed 20261010: 2.819219e-05 for type
   IV and 2.127120e-05 with the mean set to zero.
3. The spread of the 100,000 shuffled means on seed 20261011, 3.788199e-06.
4. The net position of the first 500 shuffles on seed 20261011 against the
   real rule's: an average absolute size of 9.975403 units against 20.58, and
   long on 0.983958 of days against 0.638. That is the reading that shuffled
   entry days cancel into a net long position of about the same size on every
   shuffle.

Its one figure is drawn from the committed file by
[src/chan/tu_hypothesis_tests_figures.py](src/chan/tu_hypothesis_tests_figures.py),
which reads it through the same `read_sources` and `hypothesis_tests` as
`python -m chan.tu_hypothesis_tests`, scale-break guard included. It draws
three panels on one axis of mean daily strategy return, each with the observed
mean as a line, for Lessons 1, 4 and 5.

1. The Gaussian null as a dashed curve, beside the type IV means with the mean
   set to zero.
2. The type IV means, beside the normal draw's.
3. The corrected third test's 100,000 shuffled means.

```bash
uv run python -m chan.tu_hypothesis_tests_figures
```

[tests/test_tu_hypothesis_tests_figures.py](tests/test_tu_hypothesis_tests_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/crude-oil-calendar-spread-lessons.md](blog/crude-oil-calendar-spread-lessons.md)
is a twenty-ninth post, about Example 5.4 of Chan's *Algorithmic Trading*,
which trades crude oil's 12-month calendar spread on the z-score of its roll
return. Chan reports a half-life of 36 days, stationarity "with 99 percent
probability", and an APR of 8.3 percent with a Sharpe ratio of 1.3 from
2008-01-02 to 2012-08-13. The post links the earlier calendar-spreads post,
the spot and roll returns post, the USD.CAD post, the price-spread-ratio post,
the VX against E-mini post and the VIX calendar spread post rather than
repeating them, and draws five lessons from Entry 34 of the replication log.

1. The book's figures reproduce on Chan's own file, and the figures in the
   script's comment land only on a window starting a day later, found by a
   scan.
2. The spread moves against the roll return, and the script reverses its
   position where the roll return's z-score is above 0, so it mostly sells the
   spread when the spread is low. Reversing every position gives an APR of
   −0.080125, and reversion on the spread's own z-score loses too.
3. The book's 61 holding days and the script's 63 give different trades, and
   the script's is the one that printed the figures.
4. The window's last 66 days earn nothing, because contracts still trading
   when the file was saved look expired on its last day.
5. The half-life that sets the lookback is measured on the days the trade
   uses, and it measures a reversion the trade bets against.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   2321, 2326, 2364, 2449, 2453, 2461, 2471 and 2502, with Figure 5.7's
   caption at 2471.
2. Facts about the script rather than the data: the comments at its lines 71
   and 99, its `idx=find(tday==20080102)` and `3*21`, and the expiry mark at
   line 75, all at `e4bc46f` of ericnberwick/EpchanPreview.
3. Readings no test asserts: that the correlation is strong but not the
   one-for-one the model gives, that the ADF test's long-run reversion and the
   trade's short-run continuation can both hold of one series, that the half-life
   measures a reversion the trade bets against, that the log of a VIX pair's
   ratio of far to near is that pair's log spread, that the book's ratio of
   back to front most plainly reads the two nearest contracts, and that any
   backtest inferring expiry from the last price goes flat at the end of a
   file saved while contracts trade.
4. Figures the post states in words or as percentages of pinned ones, such as
   8.27 percent, 0.28 percent, −8.0 percent, 8.8 percent, 6.7 percent and
   about three days in four. The figure's alt text reads its curves and the
   scatter's ranges approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_calendar_spread_reversion.py](tests/test_calendar_spread_reversion.py),
to
[tests/test_calendar_spread_reversion_figures.py](tests/test_calendar_spread_reversion_figures.py)
for the figure's own numbers, to
[tests/test_vx_calendar_spread.py](tests/test_vx_calendar_spread.py) for the
126 of 847 held days on which the VIX trade's near leg is the front contract,
or to [tests/test_roll_returns.py](tests/test_roll_returns.py) for the strip's
6,467 days from 1986-11-03 and γ as −12 times the slope. Twelve things had no
pin before it.

1. The held pair's log spread correlates with γ at −0.883910 on the window's
   1,097 held days, and at −0.893686 on all 1,429 held days of the file.
2. The far leg is short on all 554 held days of the window where γ's z-score
   is above 0, and long on all 543 where it is below.
3. Reversing every position gives an APR of −0.080125 and a Sharpe ratio of
   −1.278216, and its compounded curve ends at −0.320073.
4. Measured to 2012-05-09, the last day with a return, over 1,098 days, the
   APR is 0.087853 and the Sharpe ratio 1.316295.
5. The script's curve ends at a cumulative return of 0.443248.
6. 1,164 of γ's 1,941 finite days lie in the traded window.
7. The held pair's own 36-day z-score has the opposite sign to γ's on 841 of
   the 1,097 held days and the same on 256, and the two correlate at
   −0.766342.
8. Within one pair, the day-to-day changes of the spread and of γ correlate at
   −0.510282 over 1,082 days, and the script's daily return correlates at
   0.999030 with yesterday's far-leg position times today's change in the
   spread.
9. Line 107 run on the spread's own z-score gives an APR of −0.027380 and a
   Sharpe ratio of −0.402360.
10. The script's rule on the 332 days before the window, from 2006-09-05 to
    2007-12-31, earns 0.050334, an APR of 0.037979 with a Sharpe ratio of
    0.770953.
11. The script's compounded return in each calendar year from 2008 to 2012.
12. `held_log_spread` and `held_spread_zscore`, on synthetic frames.

Its one figure is drawn from the committed CL strip by
[src/chan/calendar_spread_reversion_figures.py](src/chan/calendar_spread_reversion_figures.py),
which reads it through the same `load_strip` and `run_spread` steps as
`python -m chan.calendar_spread_reversion`. It draws two panels.

1. The script's cumulative compounded return from 2008-01-02, the book's
   Figure 5.7, with the last 66 flat days shaded and the reversed trade dashed
   beside it.
2. The held pair's log spread against the roll return on the 1,097 held days,
   for which the book draws no figure.

```bash
uv run python -m chan.calendar_spread_reversion_figures
```

[tests/test_calendar_spread_reversion_figures.py](tests/test_calendar_spread_reversion_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/tu-momentum-lessons.md](blog/tu-momentum-lessons.md) is a thirtieth post,
about Example 6.1 of Chan's *Algorithmic Trading*, which correlates TU's past
and future returns for 49 pairs of lookback and hold and then trades the
250-day lookback with a 25-day hold. Chan reports a correlation of 0.27 with a
p-value of 0.02, an H of 0.44, a Sharpe ratio of 1, an APR of 1.7 percent and a
maximum drawdown of 2.5 percent. The post explains the strategy for the other
TU posts to link, and draws three lessons from Entry 33 of the replication log.

1. The book's figures come from the full window, whose line the script
   leaves commented out, while the line it runs from 2009 lands none of them.
2. H misses 0.44 on Chan's own file, and the `maxT` that lands it on TU moves
   USD.CAD further from its 0.49, so no figure of Chan's vouches for the
   Python copy of `genhurst`.
3. The momentum is thin: the traded cell rests on 69 days, is one of 49 that
   share the same closes, and the variance ratio test cannot tell TU from a
   random walk.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The four causes of momentum and the persistence of roll returns are at
   2591, momentum as a correlation of past and future returns at 2600, the
   optimal pair at 2612, the two tests as momentum tests at 2620, the warning
   about overlapping data and Figure 6.1's bars at 2623, the best compromises
   and the time frames that reconcile the tests at 2646, the paper the rule
   comes from and the twenty-fifth of the capital at 2659, the full window's
   sentence, the notional value of about \$200,000, the margin of about \$400,
   the case for leverage and Figure 6.2's caption at 2668, and the sign of
   roll returns at 2683. The book's figures are pinned, and its words are not.
2. Facts about the code rather than the data: the active line
   `idx = find(tday == 20090102)` and the commented-out `% idx=1;` under it,
   the comment printing no annual volatility, `genhurst`'s default `maxT` of
   19, and `correlationTest.m` loading the 2012-05-17 save.
   [src/chan/tu_momentum.py](src/chan/tu_momentum.py) records each in its
   docstring.
3. Readings no test asserts: that TU's price rises when two-year yields fall,
   that consecutive future returns overlap on 24 of 25 days and each kept past
   return shares 225 of its 250 days with the next, that a four-day shift
   moving the correlation's second decimal shows how few days stand behind
   it, that 2008 was the year of the financial crisis, that the back-adjusted
   series carries roll return as well as moves in yields, that the comment's
   missing volatility suggests it was pasted from an earlier version of the
   printing line, that a rule mostly long on a rising price earns part of the
   rise, and that leverage would multiply the drawdowns along with the
   return.
4. Ratios and roundings the post takes between pinned figures in words: more
   than half of the gain in by 2009-01-02, 2008 earning about four-fifths as
   much as the other years combined, four trading days between the two saves'
   first days, 2.484746 percent rounding to 2.5, and what a figure prints as
   at the book's precision, such as 0.43, 0.45 and 0.29. The figure's alt text
   reads both curves approximately too, such as TU's closes drifting down
   until mid-2007 and the cumulative return dipping below zero in 2005 and
   flattening through 2009.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_tu_momentum.py](tests/test_tu_momentum.py), which also holds
USD.CAD's H at a `maxT` of 19 and 24, or to
[tests/test_tu_momentum_figures.py](tests/test_tu_momentum_figures.py) for the
figure's own numbers. Four had no pin before it, and `TestBesideThePost` now
pins them all.

1. Fourteen of the 49 cells have a p-value below 0.05, ten positive and four
   negative, against the 2.45 that 49 independent tests would give, and the
   negative four are exactly 1/1, 1/5, 5/1 and 5/5.
2. The position is +25 on 1,176 of the 2,000 days, −25 on 397 and 0 on 251,
   of which 250 precede the first signal.
3. TU's close is 97.9219 on the first day and 110.2734 on the last.
4. Calendar 2008 compounds to 0.060565, and every other year together to
   0.075414.

Its one figure is drawn from the committed file by
[src/chan/tu_momentum_figures.py](src/chan/tu_momentum_figures.py), which
reads it through the same `read_sources` and `tu_momentum` as
`python -m chan.tu_momentum`, scale-break guard included. It draws two panels
on one date axis, for Lesson 1.

1. TU's 2,000 closes.
2. The cumulative return, the script's plot and the book's Figure 6.2, with
   the maximum drawdown from 2008-03-17 to 2008-06-13 shaded and the start of
   the script's active line, 2009-01-02, marked.

```bash
uv run python -m chan.tu_momentum_figures
```

[tests/test_tu_momentum_figures.py](tests/test_tu_momentum_figures.py) holds
what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/roll-momentum-lessons.md](blog/roll-momentum-lessons.md) is a
thirty-first post, about location 2690 of Chan's *Algorithmic Trading*, which
revises Example 6.1 to trade TU, the two-year Treasury note future, on the
lagged roll return instead of the past 250-day return. Chan reports an APR of
2.5 percent, a Sharpe ratio of 2.1 and a maximum drawdown of 1.1 percent from
2009-01-02 to 2012-08-13, each better than Example 6.1's. The post draws four
lessons from Entry 36 of the replication log.

1. The declared rule misses all three printed figures, and Chan's 2012-05-11
   save lands near the rebuilt series, so the vintage does not explain the
   miss on the 849 window days that save covers.
2. It beats Example 6.1 on all three on one series, by stepping aside. Example
   6.1 is fully long on every window row, so it is holding TU, and the 341
   rows the declared rule sits out compound to about nothing while its
   volatility falls.
3. No saved series reaches the window, so the front contract is rebuilt from
   the strip, and every change that differs from the save falls on the roll
   row where the save's back-adjustment jumps.
4. The rule was declared after about 90 scratch readings, and the
   fifth-contract reading that lands two of the book's figures is set aside.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   Example 5.3's regression on "time to maturity" is at 2399. "A respectable
   1", the 1.7 and 2.5 percent, and TU's notional value of about $200,000
   against a margin of about $400 are at 2668. "The sign of roll returns does
   not vary very often" is at 2683. "A cleaner and potentially better momentum
   signal", the 3 percent threshold, and the 2.5 percent, 2.1 and 1.1 percent
   are at 2690. The book's figures are pinned, and its words are not.
2. Facts from the run's own disclosure rather than the data: the count of
   about 90 scratch readings, and the 1.801 a scratch fit of γ on the four
   nearest contracts gave the fifth-contract reading. No test repeats either.
3. Readings no test asserts: that a low close on the fifth contract would
   raise γ and put the rule long the same contract, that Example 6.1 would go
   short in a window where TU fell, that a position on TU's notional value
   would be leveraged, and that Example 6.1's line moves up in some of the
   figure's shaded stretches and down in others.
4. Arithmetic the post takes between pinned figures in words: the 1.80 and
   1.20 that average return over volatility gives, the 64 window rows the
   2012-05-11 save does not cover, a third of γ as three times the month
   reading, 341 of 913 as the rows outside the 572, and the APR margins of
   0.000304 and 0.000225 over the save's 849 rows, each the difference of two
   pinned APRs.
   The figure's alt text reads its curves approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_roll_momentum.py](tests/test_roll_momentum.py) or to
[tests/test_roll_momentum_figures.py](tests/test_roll_momentum_figures.py)
for the figure's own numbers. Three had no pin before it.

1. Example 6.1 holds all 25 tranches long on every one of the 913 window rows,
   so its returns are the rebuilt series' own.
2. The 341 rows the declared rule sits flat compound to −0.001244, and the 572
   long rows to 0.050629, the rule's whole return.
3. The two rules' annual volatilities, 0.007575 and 0.011156, and average
   annual returns, 0.013661 and 0.013351.

[tests/test_roll_momentum.py](tests/test_roll_momentum.py) pins all three, and
[tests/test_roll_momentum_figures.py](tests/test_roll_momentum_figures.py)
pins the figure's lines and labels.

Its one figure is drawn from the committed strip by
[src/chan/roll_momentum_figures.py](src/chan/roll_momentum_figures.py), which
reads it through the same `load_strip` and `roll_momentum` as
`python -m chan.roll_momentum`. It draws two panels on one date axis, with the
rows the declared rule sits flat shaded in both.

1. Both rules' compounded cumulative returns on the rebuilt front contract over
   the 913 window rows, ending at 0.050629 and 0.049322.
2. γ in column units against the thresholds at 3 and −3 percent. It peaks at
   0.073403 on 2009-10-12 and never falls below −3 percent.

```bash
uv run python -m chan.roll_momentum_figures
```

[tests/test_roll_momentum_figures.py](tests/test_roll_momentum_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/vx-calendar-spread-lessons.md](blog/vx-calendar-spread-lessons.md) is a
thirty-second post, about the VIX futures calendar spread at location 2502 of
Chan's *Algorithmic Trading*, which runs Example 5.4's script on the ratio of
the back contract to the front. Chan reports that the ratio is "stationary
with a 99 percent probability", and an APR of 17.7 percent with a Sharpe ratio
of 1.5 from 2008-10-27 to 2012-04-23. The post links the crude oil calendar
spread post, which explains Example 5.4's script, the VX against E-mini post,
the spot and roll returns post, the USD.CAD post and the price-spread-ratio
post rather than repeating them, and draws four lessons from Entry 35 of the
replication log.

1. The ratio passes the stationarity test, and the specification read from the
   book's text loses, with an APR of −0.040454 and a Sharpe ratio of −0.563912.
2. The specification's signal reads the front pair while the script holds a
   pair further out, so its near leg is the front contract on 126 of its 847
   held rows. The two readings whose signal reads the held pair are the two
   that earn, a pattern rather than a cause, and B2 cuts against it.
3. B3 lands the book's figures on its window and alone does worse before
   October 2008, but it was picked out among five rows after the run, and the
   book's end date does not single it out.
4. The script as shipped runs on VX without complaint while holding the near
   leg alone on 1,183 of 1,284 held days.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   All of them, and Figure 5.8's caption, are at 2502.
2. Facts about the script rather than the data: its commented-out load of the
   VX file, its pairs 12 months apart, its flip where the z-score is above 0,
   its return summed over the legs that have one and halved, its roll 10 days
   before expiry, its expiry marked on a contract's last priced day, and four
   contracts traded at each roll, all at `e4bc46f` of
   ericnberwick/EpchanPreview.
3. Readings no test asserts: that the ratio moves with the spread's log value,
   that B2's 420 days are the 10 after each roll, that four readings show a pattern rather than a cause, and
   that a rule selling one spread on another's z-score bets on the two moving
   together.
4. Figures the post states in words or rounded from pinned ones, such as 4.0
   percent, −0.56, six days in seven, three or four months between pairs,
   three or four earlier contracts still trading, at least 73 days, and B2's
   share of days reading its held pair against S's. The figure's alt text
   reads its curves approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_vx_calendar_spread.py](tests/test_vx_calendar_spread.py), or to
[tests/test_vx_calendar_spread_figures.py](tests/test_vx_calendar_spread_figures.py)
for the figure's own numbers. Crude oil's spread mostly falling as γ rises,
which the post cites from the crude oil post, is `TestTheTradesDirection` in
[tests/test_calendar_spread_reversion.py](tests/test_calendar_spread_reversion.py).
Four had no pin before it.

1. The specification's near leg is the front contract on 126 of its 847 held
   rows from 2008-10-27, and the second to the fifth on 229, 221, 201 and 70,
   over 11 pairs from VX-2009G's to VX-2012H's.
2. Under `holddays=0` the near leg is the front contract on 459 of 879 held
   rows and the second on the other 420.
3. Of the four readings that run to the file's last day, B1 and B3 earn and
   S and B2 lose.
4. Each curve's end, 0.758213 for B3, −0.135565 for S, 0.123003 for B1 and
   −0.345330 for B2, and B3's 0.765276 on 2012-04-23.

Its one figure is drawn from the committed VX strip by
[src/chan/vx_calendar_spread_figures.py](src/chan/vx_calendar_spread_figures.py),
which reads it through the same `load_strip` and `vx_calendar_spread` as
`python -m chan.vx_calendar_spread`. It draws two panels.

1. The cumulative compounded return of S and B1 to B3 from 2008-10-27, the
   book's Figure 5.8, with the book's end date marked.
2. Each of those rows' APR before October 2008 beside its APR from
   2008-10-27, for the book's third claim, which the book draws no figure for.

```bash
uv run python -m chan.vx_calendar_spread_figures
```

[tests/test_vx_calendar_spread_figures.py](tests/test_vx_calendar_spread_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/capped-kelly-allocation-lessons.md](blog/capped-kelly-allocation-lessons.md)
is a thirty-third post, about Examples 8.1 and 8.2 of Chan's *Algorithmic
Trading*, which hold a leverage constant through a loss and a gain and then
spend a broker's cap of 2 on gross leverage across two strategies. Chan
reports Kelly leverages of 4.4 and 4.9, a proportional split of 0.95 and 1.05
growing at 0.82, and 0.96 with everything on strategy 2. The post links the
earlier posts on the Kelly leverage on SPY and on the coin toss for the
one-strategy formula and the variance drag rather than deriving them again,
and draws six lessons from Entry 20 of the replication log.

1. Every figure the book prints lands, and nothing about the data could have
   moved them, since the inputs are numbers the book states.
2. Scaling every Kelly leverage down to the cap is the recommendation the
   example refutes, and everything on strategy 2 wins because the drag the
   split saves is smaller than the return it gives up.
3. The printed 0.96 is the exact 0.955 rounded up from a tie, and the usual
   float formatting prints 0.95.
4. Solving along the line without its bound finds a higher growth rate by
   shorting strategy 1, over the gross cap.
5. Everything on strategy 2 stays best only below a cap of 2.448980 on these
   inputs. That is where the "all" in Chan's "most or all" ends, since
   strategy 2 keeps most of the cap at every cap up to the total Kelly
   leverage.
6. The best allocation under the cap is long-only on Chan's inputs and not in
   general.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   "The leverage should be kept constant" is at 3210, the discomfort of
   selling into the loss at 3216, "a vicious cycle" and the August 2007
   meltdown at 3228, the upper bound, the broker's limit and the estimation
   errors at 3235, allocating buying power at 3259, the definition of gross
   leverage, "not the net leverage", the usual recommendation, "much smaller
   than" and "most or all" at 3268, and Figure 8.1's caption, Equation 8.3
   applying "only when the leverages used are optimal", "the highest growth
   rate" and "apply all of our buying power" at 3287. The book's figures are
   pinned, and its words are not.
2. Facts about the book rather than the arithmetic: that Equation 8.3 is an
   image the highlights did not capture, and that Chan cites Thorp (1997) for
   Equation 8.3, the growth rate at the Kelly leverages.
3. Readings no test asserts: the slope's first number read as how fast the
   growth rate rises as leverage moves from strategy 1 to strategy 2,
   positive because strategy 2 earns more and strategy 1 sheds drag, and its
   second as the two variances added together, the drag growing with the
   square of the leverage and so staying small under a tight cap, the
   correlated short cancelling most of strategy 2's variance, and that the
   example cannot say whether Chan means the highest mean or the highest
   growth rate. The post's illustration of gross leverage, \$1.50 long and
   \$0.50 short on \$1 of equity, is arithmetic on its own numbers.
4. Ratios and roundings the post takes from pinned figures in words: strategy
   2's mean twice strategy 1's, 0.4648 less than half the corner's rate,
   0.262321 as about a quarter, 2.448980 as 2.45 in the subtitle, a heading
   and Lesson 6, and 0.962956 rounding to 0.96. The figure's alt text reads
   the dashed curve as rising "a little further" and falling "slightly".
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_kelly_allocation.py](tests/test_kelly_allocation.py) or to
[tests/test_kelly_allocation_figures.py](tests/test_kelly_allocation_figures.py)
for the figure's own numbers. Before the post, fourteen had no pin at the
precision it quotes, and
[tests/test_kelly_allocation.py](tests/test_kelly_allocation.py) now pins them
all. `TestBesideTheClaim` holds the first nine, splitting each growth rate
into its return and its drag from the run's own leverages.
`TestWhereTheCornerStopsWinning` holds the tenth, and `TestTheLongOnlyLimit`
the last four.

1. The Sharpe ratios 1.153846 and 1.714286, half the sum of whose squares is
   the growth rate at Kelly.
2. At the Kelly leverages, a return of 4.270136 and a drag of 2.135068,
   exactly half of it.
3. The proportional split's return of 0.914785 and drag of 0.097986.
4. The corner's return of 1.2 and drag of 0.245.
5. The 0.147014 of drag the proportional split saves and the 0.285215 of
   return it gives up.
6. The corner growing 1.169199 times as fast as the proportional split.
7. Everything on strategy 1 growing at 0.4648.
8. The shares of the uncapped Kelly growth each keeps, 0.382563 for the
   proportional split and 0.447292 for the corner.
9. The threshold of 2.448980 as 0.262321 of the total Kelly leverage.
10. Strategy 2's share of the best long-only split of the cap, the whole of
    it at 2.448980, 0.882 at 3, 0.750 at 4 and 0.525 at 9.335829, and above
    half at every cap up to that total.
11. In the correlated case, strategy 2 alone at its own Kelly leverage of
    3.333333, inside the cap of 4, growing at exactly 0.5, which no long-only
    allocation beats.
12. The short hedge's leverages in closed form, 1.002849 short and 2.997151
    long, which a grid had held only to within 0.001.
13. The whole cap of 4 on strategy 2 earning a return of 1.2 and paying a
    drag of 0.72, and the hedge earning 0.849003 and paying 0.192501.
14. The 0.527499 of drag the hedge saves and the 0.350997 of return it gives
    up, 0.050142 lost on the short and 0.300855 on the strategy 2 leverage the
    short displaces.

Its one figure is drawn by
[src/chan/kelly_allocation_figures.py](src/chan/kelly_allocation_figures.py)
from the same `growth_rate`, `proportional_cap`, `best_allocation_at_cap` and
`segment_stationary_point` as `python -m chan.kelly_allocation`, for Lesson 2
and Lesson 4. It draws one panel, the growth rate along `F1 = 2 - F2`.

1. The solid curve from F2 = 0 to the cap, the book's Figure 8.1.
2. The same line continued dashed to F2 = 2.6 over a shaded region past the
   cap, which the book does not draw, with markers at the proportional split,
   the corner and, hollow, the unbounded peak.

```bash
uv run python -m chan.kelly_allocation_figures
```

[tests/test_kelly_allocation_figures.py](tests/test_kelly_allocation_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/crude-oil-reversal-momentum-lessons.md](blog/crude-oil-reversal-momentum-lessons.md)
is a thirty-fourth post, about the crude oil rule at Kindle location 2701 of
Chan's *Algorithmic Trading*. The rule buys CL below its close 30 days earlier
and above its close 40 days earlier, shorts the opposite case, and is flat
otherwise. Chan says the join of a reversal rule and a momentum rule "may work
better than each strategy by itself" and reports an APR of 12 percent and a
Sharpe ratio of 1.1. The post draws three lessons from Entry 31 of the
replication log.

1. Both figures land on the save `CL_rev.m` loads, and the 2012-05-11 save,
   0.27 higher on every day, still rounds to 12 percent and 1.1.
2. Half a position in each rule is the join's position on every row but the
   ten warm-up rows, so the join earns close to the average of the two rules'
   days. It beats each rule alone on the book's window with a smaller average
   day than momentum's, because its returns swing a little over a third as
   much.
3. On the four years before the window, reversal alone loses enough that the
   same averaging drags the join below momentum alone.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The rule, "may work better than each strategy by itself" and the two
   figures are at 2701, and the warning that the real test is out-of-sample
   is at 2715. Crude's peak on July 14, 2008 is location 1922's, cited
   through the gold miners post. The book's figures are pinned, and its words
   are not.
2. Facts about the script rather than the data: that `CL_rev.m` runs four
   rules and prints figures for one, that its comment records
   `APR=0.117600 Sharpe=1.100368`, and that it plots a fourth curve for
   ComboOR, which `CL_rev.m` holds at `e4bc46f` of ericnberwick/EpchanPreview.
3. The EIA's annual average WTI spot price of $41.51 for 2004, read from its
   Cushing, OK series on 2026-10-10 and measured nowhere here.
4. Arithmetic and ratios the post takes between pinned figures in words: a
   little over a third, about 40 percent, under a quarter, most of a gain,
   0.98 × 1.02 = 0.9996, the Sharpe ratios of 0.37 and 0.66 rounded from
   pinned figures, the join's average day sitting slightly below the plain
   average of the two rules' and near it before the window, and "two months
   before" the peak. The figure's alt text reads its curves approximately too,
   such as "about −11 percent" and "about −29 percent".
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_cl_reversal_momentum.py](tests/test_cl_reversal_momentum.py), or
to
[tests/test_cl_reversal_momentum_figures.py](tests/test_cl_reversal_momentum_figures.py)
for the figure's own numbers. The APR falling by more than half between two
VX and ES saves traces to [tests/test_vx_es.py](tests/test_vx_es.py). Five
had no pin before it.

1. Half a position in each rule gives the join's on all but the 10 warm-up
   rows from 2008-07-01 to 2008-07-15, so the join's daily return is the
   average of the two rules' on all but 10 days. Before the window it differs
   on 12 rows, the warm-up and two where the close ties its 40-day lag,
   2005-06-15 and 2007-04-17.
2. Of the 960 rows where both lags exist, the two rules agree on 157 and take
   opposite sides on 803. Before the window, 162 of 958 agree and 796 do not,
   794 of them opposite and 2 the ties where momentum is flat.
3. Each rule's average day and its standard deviation on both segments: on
   the book's window 0.000463 and 0.006687 for the join, 0.000519 and
   0.018748 for momentum alone, and 0.000440 and 0.018864 for reversal alone.
   Before it, 0.000091 and 0.003922, 0.000406 and 0.009765, and −0.000222 and
   0.009792.
4. The 2012-05-11 save takes the same positions as the 2012-05-04 save on
   every day.
5. The three curves' ends, momentum's peak of 1.169842 on 2009-06-11,
   reversal's low of −0.587038 on 2009-02-18 and the join's low of −0.039937,
   which the figure test holds.

Its one figure is drawn from the committed saves by
[src/chan/cl_reversal_momentum_figures.py](src/chan/cl_reversal_momentum_figures.py),
which reads them through the same `read_cl` and `four_rules` as
`python -m chan.cl_reversal_momentum`, so the scale-break guard runs for it
too. It draws three of the script's four curves, compounded, in two panels
that cover different years.

1. The book's 1,000 rows on the 2012-05-04 save.
2. The 998 rows before them on the 2012-05-07 save.

```bash
uv run python -m chan.cl_reversal_momentum_figures
```

[tests/test_cl_reversal_momentum_figures.py](tests/test_cl_reversal_momentum_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/gld-gc-lessons.md](blog/gld-gc-lessons.md) is a thirty-fifth post, about
holding GLD long and gold futures short at Kindle locations 2718 and 2730 of
Chan's *Algorithmic Trading*, which collects gold's negative roll return.
Chan reports an annualized return of 1.9 percent and a maximum drawdown of 0.8
percent from 2007-08-03 to 2010-08-02, and says GLD's financing cost leaves
an excess return close to zero. The post links the spot and roll returns post,
the VX against E-mini post, the crude oil reversal and momentum post, the
factor models post, the Kelly leverage on SPY post and the GLD/GDX post rather
than repeating them, and draws four lessons from Entry 38 of the replication
log.

1. Every figure lands, and the 0.8 percent and the 91 days are two
   drawdowns. The deepest is mostly 2007-11-12, and the longest runs from
   2009-08-28 to 2010-01-08 and reaches only −0.40907 percent.
2. The negative Sharpe ratio comes from the script's constant 2 percent,
   105.18 percent of the return. With no rate subtracted it is 1.284060, and
   at the window's bill rate 0.599257.
3. The bill rate takes 0.533311 of the return, and the return fell with the
   bill rate year by year, a split chosen after the run.
4. The 16:00 series lines up with GLD's close within a bound the suite pins,
   though the book's reason for dismissing the timing caveat does not fit a
   script with no signal.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   The trade, its figures, GLD owning physical gold, the −4.9 percent roll
   return from 1982 to 2004, the leverage of 5 or 6, the financing claim and
   "close to zero" are at 2718. The 1:30 p.m. and 4:00 p.m. times and the
   reason about signals are at 2730, the settlement price as a vendor's usual
   close at 561, and the spread between a future and an ETF at 583.
2. Facts about the script rather than the data: its five steps, its
   `riskFreeRate=0.02/252` line, and that it holds the pair every day with
   no signal, all at `e4bc46f` of ericnberwick/EpchanPreview.
3. Readings no test asserts: that the bill rate is a floor on financing
   because a broker lends above it, that an offset's share of a day carries
   roughly that share of the day's variance in a market trading nearly
   around the clock, that whatever else moves log(GC / GLD) does not cancel
   an offset's moves, which the bound of 0.001775 rests on, that a small
   reading error or an offset of minutes makes a daily change reverse, that
   GC trades on COMEX, and the cost of carry, cited from Hull as the usual
   explanation and not tested.
4. Figures the post states in words or rounded from pinned ones, such as
   about half, ten times as large, the 150 minutes in two and a half hours,
   the 91-day stretch about half as deep as the November 2007 fall, the OHLC
   series moving most of the way back on 2008-09-19, and S rising by less
   than a percentage point from 2008-12-31 to its high. The prose writes
   pinned fractions in percent, such as 1.0141 percent for 0.010141. The
   figure's alt text reads its curves approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_gld_gc.py](tests/test_gld_gc.py), or to
[tests/test_gld_gc_figures.py](tests/test_gld_gc_figures.py) for the
figure's own numbers. `TestWhatThePostMeasured` holds the ones that had no pin
before it, all measured after the run.

1. The Sharpe ratio of 1.284060 with no rate subtracted and 0.599257 at the
   window's bill rate over 252, the break-even rate at the mean return of
   1.9014 percent, and the script's 2 percent as 105.18 percent of the return.
2. The bill rate's share of the return, 0.533311, written in the post as
   53.33 percent.
3. S's average annual return against the bill rate by calendar year, 101,
   253, 251 and 146 rows, 0.052235 against 0.036520, 0.027315 against
   0.013650, 0.005822 against 0.001500 and 0.004458 against 0.001350, a margin
   shrinking from 1.57 percentage points to 0.31, and the 22 of 37 months
   below 0.5 percent, from 2008-11 to 2010-08.
4. The deepest drawdown's high on 2007-10-12, trough on 2007-11-12 and
   recovery on 2007-11-14, that day's −0.6771 percent for the trade, −4.7213
   for GLD and −4.0442 for GC, and the longest stretch from 2009-08-28 to
   2010-01-08 at worst −0.40907 percent.
5. The 16:00 series' largest move falling on 2007-11-12, its minimum of
   −0.006626 and its lag-1 autocorrelation of −0.437059. The bound on an
   offset between the two closes read as about 2.6 minutes of a 24-hour day.
   The OHLC series' largest move falling on 2008-09-18, its minimum of
   −0.075146 on 2008-09-19, and its 8 moves past 0.02 up and 12 down. No GC
   series here starting before 2004-05-24, the OHLC series' first day.
6. The three curves' ends, 0.058033 for S, 0.031057 for bills and 0.061413
   for 2 percent a year, S at 0.049260 and bills at 0.028733 on 2008-12-31,
   S's high of 0.058415 on 2010-07-27, and 2010-05-21 as the last day S stands
   above the 2 percent line.

Its one figure is drawn from the committed vintages by
[src/chan/gld_gc_figures.py](src/chan/gld_gc_figures.py), which reads them
through the same `read_sources`, `read_ohlc_gc`, `gld_gc` and
`ratio_steps` as `python -m chan.gld_gc`, so the scale-break guard runs for it
too, once for each file. It draws two panels.

1. S's cumulative return beside bills accrued at each month's TB3MS over 252
   and the script's 2 percent a year, compounded, with the 91 days shaded and
   the deepest trough marked.
2. The daily change in log(GC / GLD) on the 16:00 series and on the OHLC
   series, with dashed lines at plus and minus 0.02.

```bash
uv run python -m chan.gld_gc_figures
```

[tests/test_gld_gc_figures.py](tests/test_gld_gc_figures.py) holds what it
draws rather than its bytes, for the reason given above for the regime map.

[blog/xle-uso-roll-return-lessons.md](blog/xle-uso-roll-return-lessons.md) is
a thirty-sixth post, about the XLE against USO trade at location 2734 of
Chan's *Algorithmic Trading*. The trade is short USO and long XLE when crude
oil's back contract is priced above its front, and the reverse when below.
Chan reports an APR of 16 percent and a Sharpe ratio of about 1 from
2006-04-26 to 2012-04-09. The post links the long GLD and short gold futures
post, the crude oil calendar spread post, the spot and roll returns post, the
crude oil reversal and momentum post and the gold miners post rather than
repeating them, and draws five lessons from Entry 39 of the replication log.

1. The pair stands in for crude's spot against its futures only by the book's
   argument, and the script's front is the nearest contract on 734 of the
   1,375 days with a ratio and the second-nearest on 641.
2. All five figures the script's comment prints and the book's two land, and
   the one-pair ratio and Example 5.3's γ call the same view on 1,354 of the
   1,373 days the ratio is not exactly 1.
3. The trade holds contango on 1,129 days and backwardation on 244, and
   nothing on its first 123. From 2006-10-20 its APR is 0.174513.
4. The ETF file subtracts dividends in dollars, so XLE's returns are not what
   a holder earned, and nothing committed measures by how much.
5. The 244 days earning on backwardation hold 0.308117 of the summed daily
   return of 0.946538. On them USO rose 0.5323 in log terms while the ratio
   implies a roll return of 0.072380, and holding contango's position
   throughout gives an APR of 0.044949.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   USO not owning oil at 1939, XLE and the spot price at 2385, the arbitrage
   of the underlying against the future at 2718, and the trade, its figures
   and Figure 6.3's caption at 2734.
2. Facts about the script rather than the data: its comment calling the
   front window days before expiration, and its commented-out last lines
   that overlay the contango flag on its plot, both in `XLE_CL_rollReturn.m`
   at `e4bc46f` of ericnberwick/EpchanPreview.
3. Readings no test asserts: that the ratio approximates the roll return
   under the book's model, that the old front is still priced for the 10
   rows after the script moves on, that rescaling gives a holder's return
   and subtraction reads larger in the earliest years, that a yfinance
   adjusted close rescales, that a fund drops by about its dividend on the
   day it goes out, that XLE pays dividends, that Chan's single contracts
   were not rewritten between his saves the way a continuous future is, that
   the contango days are the book's trade and the backwardation days a bet on
   the funds' moves, and that a split by date was measured and left out.
4. Figures the post states in words or rounds from pinned ones, such as a
   third, under a fifth of the earning days, about 7 percent, close to USO's
   fall, far exceeds, a small part, one fewer than 1,129, 127 and 84 percent,
   and the contango of early 2009. The figure's alt text reads its curves
   approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_xle_uso_roll_return.py](tests/test_xle_uso_roll_return.py), or to
[tests/test_xle_uso_roll_return_figures.py](tests/test_xle_uso_roll_return_figures.py)
for the figure's own numbers. CL's γ changing sign 29 times, which the post
cites from the spot and roll returns post, traces to
[tests/test_roll_returns.py](tests/test_roll_returns.py), and SPY's 14.98 and
its 24 dividends to `TestTheETFFileSubtractsEachDividend` in
[tests/test_series.py](tests/test_series.py). Nine had no pin before it.

1. The 40-row start binds only for CL-2007F, and the save of 2012-08-14
   gives the same ratio on all 1,375 days.
2. USO's close falls from 69.54 to 38.97, or 43.9603 percent, and XLE's rises
   from 51.97 to 69.61, or 33.9427 percent.
3. The script's front is the nearest priced contract on 734 days and the
   second-nearest on 641.
4. The ratio and Example 5.3's γ on the save of 2012-08-14 agree on 1,354 of
   the 1,373 days the ratio is not exactly 1, with 13 and 6 the other way, and γ
   positive on both days the ratio is 1.
5. From 2006-10-20 the APR is 0.174513 and the Sharpe ratio 1.092618, with
   both drawdown figures unchanged, and after its first entry the position
   changes on 19 days.
6. The trade earns on contango on 1,128 days and on backwardation on 244,
   compounding to 0.790269 and 0.343539 and summing to 0.638420 and 0.308117
   of 0.946538.
7. USO moves −0.567754 and 0.702850 and XLE 0.549091 and −0.097061 over those
   days, USO's log moves are −0.8388 and 0.5323, and the ratio implies roll
   returns of −0.766081 and 0.072380.
8. Holding contango's position on every held day gives an APR of 0.044949 and
   a Sharpe ratio of 0.364524.
9. The figure's own: the two curves' ends of 1.405296 and 0.298702, which
   its legend prints as 140.53 and 29.87 percent, the
   drawdown's high of 1.272665 on 2009-02-18 and trough of 0.835584 on
   2009-06-29, the longest run below a high from 2009-02-19 to 2011-01-24,
   the nine backwardation spans, and the ratio's low of 0.982067 on 2007-09-26
   and high of 1.111489 on 2009-02-05.

Its one figure is drawn from the committed vintages by
[src/chan/xle_uso_roll_return_figures.py](src/chan/xle_uso_roll_return_figures.py),
which reads them through the same `read_sources`, `front_ratio` and
`arbitrage` as `python -m chan.xle_uso_roll_return`, so the scale-break guard
runs for it too. It draws two panels on one date axis, both shading the days
held in backwardation and hatching the first 123 days.

1. The trade's cumulative compounded return, the book's Figure 6.3, with
   contango's position held on every held day beside it and the drawdown's
   high, trough and longest run marked.
2. The ratio of the back contract to the front, with a line at 1.

```bash
uv run python -m chan.xle_uso_roll_return_figures
```

[tests/test_xle_uso_roll_return_figures.py](tests/test_xle_uso_roll_return_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/vx-es-roll-return-lessons.md](blog/vx-es-roll-return-lessons.md) is a
thirty-seventh post, about VX futures against E-mini S&P 500 futures on VX's
roll return at Kindle locations 2747 and 2754 of Chan's *Algorithmic
Trading*, after Simon and Campasano. The trade is short the front VX contract
and ES when the front sits above VIX by more than 0.1 point per trading day to
settlement, and long both when it sits below by that much. Chan reports an
APR of 6.9 percent and a Sharpe ratio of 1 from 2010-07-29 to 2012-05-07. The
post links the VX against E-mini post, the spot and roll returns post, the
long GLD and short gold futures post, the XLE against USO post, the VIX
calendar spread post and the crude oil reversal and momentum post rather than
repeating them, and draws five lessons from Entry 41 of the replication log.

1. Both of the script's rules land, all eight figures at the precision its
   comments print, and the book's two come from the 0.3906 lines it comments
   out. The live lines trade one VX contract per ES contract.
2. The printed 0.3906 is the specification. The fitted 0.390594 from the same
   500 days, which are the trade's own first 500 from 2008-08-04, misses the
   sixth decimal on both the APR and the Sharpe ratio.
3. Every one of the 32 held stretches opens free. Charging each entry one
   basis point gives an APR of 0.067142, and the last 10 test rows hold
   nothing.
4. The window is out of sample for the hedge alone. The 40-row start decides
   only VX-2007F's window, and the script's front is the nearest contract on
   228 of the test's 438 front rows and the second-nearest on 210.
5. Under 0.3906 the VX leg is a median 0.119966 of the gross, and the ES leg
   gives back 0.159336 of the 0.285954 the VX leg earns. Measured after the
   run.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   VX in contango about three fourths of the time at 2385, no fund holding
   VIX and ES's roll return of about 1 percent at 2747, and the rule, the
   0.3906, the price regression against the paper's returns, the −75 percent,
   the window, the figures and Figure 6.4's caption at 2754.
2. Facts about the script rather than the data: which of its lines are live
   and which commented out, its line 75 plotting line 74's cumulative return
   for the live rule, its loop stopping one short of the last contract, and
   its commented-out entry filter at lines 52 to 53 and 60 to 61 with its
   levels of 21 and 34, all in `VX_ES_rollreturn.m` at `e4bc46f` of
   ericnberwick/EpchanPreview.
3. Readings no test asserts: that a VX contract converges on VIX by
   settlement, that dividing the gap by the days to settlement gives a pace,
   that a short VX leg and a short ES leg hedge each other, that the old
   front is still priced for the 10 rows after the script moves on, that a
   hedge fitted on returns would size the legs differently, and that
   [1, 1]'s larger return on this sample comes from holding more VX.
4. Figures the post states in words or rounds from pinned ones, such as close
   to three in four, more than half, about two and a half times, and years
   before the test or more than three years after VIX's jump. The figure's
   alt text reads its curves approximately too.
5. Its references, cited rather than computed. The paper by Simon and
   Campasano is not in the repository.

Every other number in the post traces to an assertion in
[tests/test_vx_es_roll_return.py](tests/test_vx_es_roll_return.py), or to
[tests/test_vx_es_roll_return_figures.py](tests/test_vx_es_roll_return_figures.py)
for the figure's own numbers. The fitted 0.390594 traces to
[tests/test_vx_es.py](tests/test_vx_es.py) as well, and the 53 series of the
2012-05-07 save to
[tests/test_continuous_futures.py](tests/test_continuous_futures.py). `TestWhatThePostMeasured`
holds the ones that had no pin before it, all measured after the run.

1. The front above VIX on 1,016 of the 1,369 front rows from 2006-11-14 to
   2012-04-23.
2. The 32 held stretches in the test, 25 short and 7 long, with no position
   changing sign without a flat day between.
3. The APR of 0.067142 and Sharpe ratio of 0.975830 with each entry charged
   one basis point, and 0.071248 and 1.030894 with no cost at all.
4. The fit's 500 days from 2008-08-04 to 2010-07-28 as the trade's first 500
   from the anchor, the 40-row start binding only for VX-2007F, and the front
   the nearest contract on 228 of the test's 438 front rows and the second on
   210.
5. The VX leg's median share of the gross, 0.119966 under 0.3906 and 0.258710
   under [1, 1], and the legs summed over the test, 0.285954, −0.159336 and
   0.003634 of cost for 0.122984 under 0.3906, and 0.605959, −0.138046 and
   0.003961 for 0.463952 under [1, 1].
6. 2011-08-08, when both rules held long, ES fell 7.3259 percent and
   VX-2011U rose 15.2672 percent, and the 0.3906 rule lost 3.9889 percent, its
   worst day and its deepest drawdown's trough, while [1, 1] lost 0.3823
   percent.
7. The front's daily return correlating with ES's at −0.813746 on the 224
   test days that earn a position.
8. [1, 1]'s deepest drawdown running from 2012-02-06 to 2012-02-15, and its
   longest from a high on 2011-09-23 to 2011-12-16.
9. The figure's own: the curves' ends of 0.126063 and 0.581024 on 2012-04-24
   and flat for the 9 rows after, 0.3906's high of 0.129142 on 2011-12-19, its
   deepest drawdown from a high of 0.049547 on 2010-08-31 to a trough of
   −0.029886 on 2011-08-08, its longest run below a high from 2010-09-01 to
   2011-09-09 with a new high on 2011-09-12, the 25 short and 7 long spans
   with the longest from 2010-07-29 to 2010-09-20 and from 2011-07-27 to
   2011-08-22, and the signal's 438 rows, 214 between the lines, low of
   −0.574194 on 2011-08-08 and high of 0.311739 on 2012-03-16.

Its one figure is drawn from the committed vintages by
[src/chan/vx_es_roll_return_figures.py](src/chan/vx_es_roll_return_figures.py),
which reads them through the same `read_sources`, `roll_return_trade` and
`front_roll` as `python -m chan.vx_es_roll_return`, so the scale-break guard
runs for it too. Loading ES checks VX's continuous close against its
checksum, as a member of the same save, but the figure never computes the
fitted hedge, the only computation that uses it as data. It draws two panels
on one date axis over the 448 test days, both shading the days held short in
one tint and the days held long in another.

1. The book's Figure 6.4, the cumulative compounded return, under 0.3906 in
   ink and [1, 1] muted, with 0.3906's deepest drawdown's high, trough and
   longest run marked.
2. The front contract less VIX over the trading days to settlement, with
   dashed lines at plus and minus 0.1.

```bash
uv run python -m chan.vx_es_roll_return_figures
```

[tests/test_vx_es_roll_return_figures.py](tests/test_vx_es_roll_return_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/khandani-lo-small-caps-lessons.md](blog/khandani-lo-small-caps-lessons.md)
is a thirty-eighth post, about Khandani and Lo's reversal on Chan's S&P 600
file, which tests his explanation at Kindle location 2137 of *Quantitative
Trading* that most of Khandani and Lo's returns came from small and microcap
stocks. Example 3.8 leaves that run as an exercise at location 2236 and prints
no figure for it. The post links the survivorship and costs post and the post
on Chan's 2012 panel rather than repeating them, and draws six lessons from
Entry 44 of the replication log. Lesson 6's closing paragraphs report what
Entry 50 found on the S&P 400.

1. At the close the S&P 600 earns 3.4086 before costs against the S&P 500's
   0.2510, a gap of +3.1576 and 3.1987 standard errors.
2. At the open the gap is +0.8850 and 0.7603 standard errors, because the
   open lifts the S&P 500 by 4.1693 and the S&P 600 by 1.8966.
3. Memmel's test of a gap between two Sharpe ratios uses the correlation of
   the two books' daily profits. With the correlation set to 0, the closes'
   standard error would be 1.4252 rather than 0.9872.
4. After 5 basis points a side the closes lose and the opens keep a profit.
   Every book trades between 1.4505 and 1.4729 times its position a day, so
   the profit decides, and the S&P 600's closes break even at 4.57 basis
   points a side.
5. The check for split prices flags BCSI on 2006-02-06 and SCUR on
   2006-07-12, and same-day news shows both were earnings warnings that
   traded.
6. The declared reading points the way Chan says, on one year of survivors.
   Nothing here measures how many S&P 600 members were microcaps. The S&P
   400 is the third point, and its run sits between the other two on the
   closes and below both on the opens. The reading written down before that
   run calls this mixed. The S&P 600 rebuilt the same way, as a check on the
   change of vendor, passes its rule only with one stock set aside on each
   of three days, decided in advance.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Quantitative Trading*
   through [its committed notes](research/book-notes/quantitative-trading.md).
   Khandani and Lo's 4.47 is at 2099, the explanation at 2137, the exercise at
   2236, the 5 basis points for S&P 500 stocks at 998, low-priced stocks'
   wider spreads at 2639, small caps being hard to borrow at 2730, and a move
   without news reverting at 3109.
2. Facts about the book and the code rather than the data: that Example 7.4
   reads the same S&P 600 file, that the notebook's rule fills each gap with
   the last price seen, and that a split halves a price the file may not
   adjust.
3. Readings no test asserts: that the open's lift removes most of what
   separated the two universes at the close, that the rule replaces about the
   same share of its book in every universe, that one cost on both universes
   flatters the S&P 600, that the S&P 600 adds a company only above a
   minimum size and does not drop a member just because it later shrank, that
   the reversal bought the two flagged stocks on days Chan's reasoning gives
   no cause to expect a bounce, that the daily profits are neither independent
   nor normal, that the 2012 panel's rule is a close cousin of this one, that
   the distance between two running totals says nothing about how much the
   daily profits swing, that a reversal buys exactly the stocks that fell, and
   that ignoring the correlation understates the noise in a gap when two
   books' daily profits move against each other.
4. Facts from outside the data and figures stated in words: the two news
   reports on BCSI and SCUR, their dates and what they say, that no source
   states SCUR's close, the bound written as 0.625 for 1/1.6, and words such
   as far more, barely past the line, about the same, about one standard
   error, most of the 116 left out, and many of the vendor's histories. The
   prose writes
   pinned fractions in percent, such as 98 percent for 0.98. The figure's alt
   text reads its curves approximately too, such as the S&P 500's dashed line
   on the opens dipping below zero in the middle of the year and the S&P
   600's on the closes falling below zero in the spring.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_khandani_lo_small_caps.py](tests/test_khandani_lo_small_caps.py),
or to
[tests/test_khandani_lo_small_caps_figures.py](tests/test_khandani_lo_small_caps_figures.py)
for the figure's own numbers, which include the low of the S&P 600's dashed
line on the closes, −6.3% on 2006-06-30. The S&P 500's average day on the
closes traces to `TestWhatAnAverageDayCosts` in
[tests/test_khandani_lo.py](tests/test_khandani_lo.py), and the factor of 1.6
to [tests/test_scale_breaks.py](tests/test_scale_breaks.py). The S&P 400's
figures, its steps to both neighbours, the control's gaps with and without
the three stocks set aside, and the reading of mixed trace to
[tests/test_khandani_lo_mid_caps.py](tests/test_khandani_lo_mid_caps.py). Its
fund, filing date, vendor and download date, its 401 holdings, the rule a run
keeps them by, the vendor's 2006-12-28 start and the 285 a run keeps trace to
[tests/test_sp400_panel.py](tests/test_sp400_panel.py).
`TestWhatThePostMeasured` in
[tests/test_khandani_lo_small_caps.py](tests/test_khandani_lo_small_caps.py)
holds the ones that had no pin before it, all
measured after the run.

1. The average day on the charged specification for the S&P 600's closes,
   6.7197 basis points of profit, 7.3545 of cost, a turnover of 1.4709 and a
   cost of 1.0945 times the profit, for the S&P 600's opens, 11.8569, 7.3644,
   1.4729 and 0.6211, and for the S&P 500's opens, 8.9815, 7.3182, 1.4636 and
   0.8148.
2. The cost a side at which each book breaks even, 4.57 and 8.05 basis points
   for the S&P 600's closes and opens, and 0.36 and 6.14 for the S&P 500's.
3. The open's lift before costs, 4.1693 for the S&P 500 and 1.8966 for the
   S&P 600.
4. The closes' standard error with the correlation set to 0, 1.4252, and the
   gap's 2.2155 standard errors against it, and the share of Memmel's
   bracket the correlation term carries, 0.98 on the closes and 0.94 on the
   opens.

Its one figure is drawn from the committed vintages by
[src/chan/khandani_lo_small_caps_figures.py](src/chan/khandani_lo_small_caps_figures.py),
which reads them through the same `compare` as
`python -m chan.khandani_lo_small_caps` and sums each book's days with the
same `cumulative` the survivorship and costs post's figure uses. It draws two
panels, the closes above the opens, each with four running totals over 2006
as a share of each book's mean position: the S&P 600 and the S&P 500, each
before costs and after 5 basis points a side with the first day charged. Each
panel's heading states its gap before costs, the gap's standard error and z.

```bash
uv run python -m chan.khandani_lo_small_caps_figures
```

[tests/test_khandani_lo_small_caps_figures.py](tests/test_khandani_lo_small_caps_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/pead-edgar-rerun-lessons.md](blog/pead-edgar-rerun-lessons.md) is a
thirty-ninth post, about Example 7.2 of Chan's *Algorithmic Trading* rerun
off his own files, on an announcement calendar read from EDGAR's Item 2.02
filings and on Alpha Vantage prices from the owner's archive. Chan reports an
APR of 6.7 percent and a Sharpe ratio of 1.5, which the post on post-earnings
drift reproduces on his files. This post links that one for the rule, the
fixed 30 and the flag counts rather than repeating them, and draws four
lessons from Entry 46 of the replication log. Every result in it is
exploratory, and the runs on the archive's prices cannot be rerun by a reader.

1. A filer check against EDGAR and a price-series check against Alpha
   Vantage drop 56 stocks, and they carry 0.023065 of A's 0.066743, 0.35 of
   it, exactly A against A_U. The 13 whose ticker cannot be tied to the right
   company, the 9 that fail the filer check and 4 reused tickers, carry
   0.014787 of that, 0.64 of it. The other 43 fail because the archive does
   not hold their prices for the whole window under the ticker. Close to half
   of the 0.023065 comes on 2011-08-04.
2. EDGAR's submissions file reads some filers' acceptance times 4 or 5 hours
   late, which would move every before-open release of a filer whose time
   reads late into the session.
3. R1 lifts A_CAL's 0.054481 to 0.071050, and the extra trades are 0.75 of the
   gain at A_CAL's mean per trade and 0.79 at R1's own.
4. The vendor and the price basis move the return by about a ten-thousandth
   each, and three trades on disputed opens move E5 by −0.004566.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   the earnings.com calendar and its window from the previous close to the
   open at 3002, the 4:00 p.m. and 9:30 a.m. times at 3010, and the book's
   6.7 percent and 1.5 at 3024. The figures at 3024 are pinned by
   [tests/test_pead.py](tests/test_pead.py), and the words are not.
2. The sample of the submissions file's acceptance times taken while
   planning the rerun, 175 of 248 filings from 38 filers true UTC and 73 a
   further 4 or 5 hours late, with Apple among them. It is not committed, and
   `chan.earnings_filings`'s docstring records it. That the extra shift is 4
   hours under daylight saving time and 5 under standard time, and that a
   filer read late was read late on every filing, are readings of it.
3. Facts about EDGAR, the archive and the code read when the record was
   built rather than computed from committed files: that today's ticker table
   sends CB to Chubb Limited, which was ACE in 2012 and filed its own
   releases in the window, that the archive's CB series holds ACE's history,
   that the archive files UTX under RTX and adjusts only the close, that
   DuPont's proposed filer was formed after 2015, that R5 matched Chan's
   flags best on a sample of 32 stocks, and the check's 3 percent tolerance
   on price, a constant in `chan.earnings_filings`.
4. Readings and figures the post states in words or rounds from pinned ones,
   such as a third, about two thirds, close to half, three quarters and
   nearer four fifths, Apple's times read after a double conversion as about
   8:30 p.m. for the four filed under daylight saving time and 9:30 p.m. for
   the two in January, about a ten-thousandth, the 54 disagreements on the
   two days, that a filing from 11:00 a.m. in winter or noon in summer
   onward moves past the close when read late, that two vendors defining the
   open differently explains the two days, and that a release can precede
   the filing that reports it. The figure's alt text reads its curves
   approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_pead_rerun.py](tests/test_pead_rerun.py), to
[tests/test_earnings_filings.py](tests/test_earnings_filings.py) for the
universes' tickers and filers, the 398 series that pass under Chan's own
tickers and the 48 companies under a later ticker, the 2 and 72 to 194 days a
series differs on, ACE's 5.92 percent, and the index's 2,930 filings, 1,460
before the open and 405 in the session, Apple's times and the earliest and
latest times of day, to [tests/test_pead_figures.py](tests/test_pead_figures.py)
for 2011-08-04 as the high A's longest drawdown starts from, or to
[tests/test_pead_rerun_figures.py](tests/test_pead_rerun_figures.py) for the
figure's own numbers. Eight had no pin before it, and all were measured after
the runs.

1. That A less A_U is exactly the trades of the 56 stocks outside U, and A
   less A_CAL exactly those of the 9 outside CAL, 0.012261 rounded from the
   true value.
2. The three groups, 441 stocks with 949 trades adding 0.043678, 47 with
   103 adding 0.010803 and 9 with 20 adding 0.012261, and the 56 carrying
   0.35 of A.
3. On 2011-08-04 the stocks outside U add 0.010702 through 8 trades, 0.46 of
   the universe effect, the largest WFR short at 0.1108. The five largest
   trades outside U are shorts of stocks outside CAL carrying 0.54 of the
   outside sum.
4. The mean trade outside U, 0.007367 over 123, against 0.001808 over 949
   inside, and a Welch t of 1.46.
5. R1's extra trades as 0.79 of its gain at its own mean, and B1 and B5
   holding more than 30 positions on 4 and 10 days.
6. That no filing was accepted before 06:00:43 or after 21:49:59 Eastern on
   any day, so a time read 4 or 5 hours late puts every filing accepted
   before the open inside the session.
7. When the owner's archive is configured and `QT_ARCHIVE_RUN=1` is set,
   the trades behind each move on Chan's opens: PNC on 2011-09-12 at
   −0.002261, MCO on 2012-02-08 at −0.001751 and TMK on 2011-10-27 at
   −0.000554 for E5, and the same MCO and TMK with CAM on 2011-10-27 at
   +0.001766 for E1.
8. Why each of the 47 stocks of CAL outside U has no checked series, and
   what each cause adds to A. 36 series lack closes and 7 were never
   proposed, and 4 reused tickers hold another company's returns: AGN, CB,
   JCI and LSI. 35 of the 36 lack all 330 closes, and the committed manifest
   of the archive dates each of those series' first row after 2012-04-24,
   ALTR's on 2017-11-01, DELL's on 2018-12-21 and DOW's on 2019-03-20. EP's
   starts on 2011-02-23 and lacks 35, and the 7 have no line in the
   archive's `sp500` cross-section. The 4 take 8 trades adding 0.002526, the
   43 take 95 adding 0.008278, and the 13 that cannot be tied to the right
   company, the 4 and the 9 outside CAL, take 28 adding 0.014787, 0.64 of
   the universe effect.

Its one figure is drawn from committed files only by
[src/chan/pead_rerun_figures.py](src/chan/pead_rerun_figures.py), which reads
them through the same `read_committed` and `committed_runs` as
`python -m chan.pead_rerun`, so the scale-break guard runs for it too. It
draws two panels and leaves out the four runs on the archive's prices.

1. Run A's arithmetic annual return built up over its 330 days from the
   stocks of U, those with a checked filer and no checked series, and those
   with no checked filer, with 2011-08-04 marked.
2. Each committed run's trades against its mean return per trade, with
   dashed curves of equal return through A and A_CAL and arrows from A to
   A_U and from A_CAL to B1 and B5.

```bash
uv run python -m chan.pead_rerun_figures
```

[tests/test_pead_rerun_figures.py](tests/test_pead_rerun_figures.py) holds
what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/opening-gap-lessons.md](blog/opening-gap-lessons.md) is a
fortieth post, about the opening gap strategy on FSTX, the STOXX Europe
50 index future, Example 7.1 of Chan's *Algorithmic Trading*. The book
describes a rule that buys when the open jumps above the previous day's high
and shorts when it drops below the previous low, holding to the close, and
reports an APR of 13 percent and a Sharpe ratio of 1.4. The post links the buy
on gap post, the volatility against the stock index post, the crude oil
reversal and momentum post, the TU momentum post and the cross-sectional
momentum post rather than repeating them, and draws six lessons from Entry 40
of the replication log. Its third open question points at the VIX filter post
below, whose figures [tests/test_vix_filter.py](tests/test_vix_filter.py)
pins.

1. The script's return line pays a long when the price falls from the open,
   so it sells an upward jump and buys a downward one, against the text's
   description. Chan's Python port takes the text's sign, and a flipped short
   test has it sell every upward jump all the same.
2. Both printed figures land on the script as written, 252 times the mean
   also rounds to 13 percent, and the first edition's `smartstd` changes no
   position.
3. The momentum sign the text describes gives an APR of −0.124236 and a
   Sharpe ratio of −1.441620, and neither curve crosses its starting capital
   after the first trade.
4. The save and its window each move the APR by more than ten times the
   comment's last digit: 0.002017 for the window alone and 0.002655 for the
   restated prices alone.
5. The rule holds a position on 469 of 2,000 days, and the mean return on
   those days is 0.002177.
6. The long days hold 0.749529 of the summed daily return of 1.020809, and on
   them FSTX fell 0.002696 from the open on average.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   "the triggering of stops" at 2954, the rule's sentence, FSTX on Eurex, the
   13 percent and 1.4 and "the gap momentum code" at 2965, the example's and
   Figure 7.1's captions and GBPUSD's 7.2 percent and 1.3 at 2971, the stop
   orders triggered at the open at 2985, "a breakout strategy" at 3170, and
   the annualized average return and the VIX filter's threshold of 35, 2.6
   percent and 0.16 at 3509. The threshold, 2.6 percent and 0.16 are pinned,
   as book targets in `TestTheSpecification` in
   [tests/test_vix_filter.py](tests/test_vix_filter.py), and its words are
   not.
2. Facts about the scripts and the instrument rather than the data: line 23's
   text and the closing comment in `gapFutures_FSTX.m` at `e4bc46f` of
   ericnberwick/EpchanPreview, the name and source text of the Python port
   `gapFutures_FSTX.py`, which `chan.opening_gap.python_port` transcribes,
   that the STOXX Europe 50 is fifty large European companies once named the
   Dow Jones STOXX 50, and GBPUSD's open and close in Eastern time.
3. Readings no test asserts: that triggered stops carry a move through the
   day, that the literal reading trades in buy on gap's direction, that a
   roll between the 2012-05-11 and 2012-05-17 saves would shift the history
   the way it moved, where [data/README.md](data/README.md) records only that
   FSTX moves between them, that a round trip costing 0.002177 of the price
   would erase the mean, and that a split by year was measured and left out.
4. Figures the post states in words or rounds from pinned ones, such as 12
   percent a year, about three quarters, fewer than a quarter and about a
   quarter of the days, the upward jumps reversing more strongly, and Chan
   saving at least three dated versions of the file. The figure's alt text
   reads its curves approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_opening_gap.py](tests/test_opening_gap.py), or to
[tests/test_opening_gap_figures.py](tests/test_opening_gap_figures.py) for the
figure's own numbers. The 100, 90 and 120 of its worked day are the synthetic
day `TestTheRules::test_the_literal_return_fades_the_jump` holds. The port's
figures, its 1,718 short days and its never holding a long trace to
`TestChansPythonPort`. Eleven had no pin before the post.

1. The first edition's `smartstd` moves the standard deviation and changes
   no position, so the APR and the Sharpe ratio hold at six decimals.
2. From 2004-11-22, over 1,909 days, the literal curve's lowest value is
   0.002878 and the momentum curve's highest is −0.002878.
3. The 2012-05-07 and 2012-05-11 saves price all four fields alike on the
   1,997 days they share, and the window alone moves the APR by 0.002017.
4. The 2012-05-11 save differs from the 2012-05-17 save on each of the four
   fields on all but 45 of 1,996 days, by 24 distinct amounts.
5. With the 2012-05-11 save run from 2004-07-16, the 2012-05-17 save's first
   day, the two runs hold a different position on 6 of those 1,996 days,
   with an APR of 0.133016 and a Sharpe ratio of 1.443075 against 0.130360
   and 1.435907, a move of 0.002655, and both moves exceed ten times 0.0001.
6. The mean return on the 469 held days is 0.002177.
7. The long and short days sum to 0.749529 and 0.271280 of 1.020809 and
   compound to 1.084422 and 0.290022, which multiply to one plus 1.688951.
8. Each side alone gives an APR of 0.096964 and a Sharpe ratio of 1.534735
   for the long days, and 0.032607 and 0.527473 for the short days.
9. FSTX moves −0.002696, +0.001420 and +0.000025 from the open on the long,
   short and 1,441 flat days after the first 90, and closes below the open on
   163 long days and above it on 108 short days.
10. Chan's Python port is short on all 278 upward jumps and earns the
    script's returns on them day for day, which sum to 0.749529, and its
    other 1,440 short days sum to −0.050957.
11. The figure's own: the literal curve's end of 1.688951 and the momentum
    curve's of −0.651056, both first reached on 2012-05-07, which its legend
    prints as 168.90 and −65.11 percent, the drawdown's high of 0.573901 on
    2008-07-08 and trough of 0.274823 on 2008-10-13, the longest run below a
    high from 2008-07-15 to 2009-08-31, the first 90 days ending on
    2004-11-18, the long days' end of 1.084422 first reached on 2012-05-02,
    and the short days' end of 0.290022 on 2012-05-07 after a high of
    0.176401 on 2008-07-08 and a low of −0.038153 on 2009-02-20.

Its one figure is drawn from the committed vintage by
[src/chan/opening_gap_figures.py](src/chan/opening_gap_figures.py), which
reads it through the same `read_sources` and `opening_gap` as
`python -m chan.opening_gap`, so the scale-break guard runs for it too. It
draws two panels on one date axis, both shading the first 90 days, which
have no standard deviation.

1. The script's cumulative compounded return as written, the book's Figure
   7.1, with the sign the text describes beside it and the drawdown's high,
   trough and longest run marked.
2. The script's returns kept on the long days only and on the short days
   only, with the short days' low marked.

```bash
uv run python -m chan.opening_gap_figures
```

[tests/test_opening_gap_figures.py](tests/test_opening_gap_figures.py) holds
what it draws rather than its bytes, for the reason given above for the regime
map.

[blog/pca-factor-momentum-lessons.md](blog/pca-factor-momentum-lessons.md) is
a forty-first post, about whether the five statistical factors Example 7.4
of Chan's *Quantitative Trading* fits for itself have the momentum the
strategy assumes, on Chan's S&P 600 file. The factor models post already
reports the result, and this post teaches the method. It links the factor
models post for what Example 7.4 does rather than repeating it, and draws five
lessons from Entry 42 of the replication log.

1. A factor re-estimated every day has no fixed sign, and tomorrow's weights
   have already seen today's return. With each sign fixed by a rule, signs
   still flip on 1, 14, 6, 22 and 24 of 752 days, all but three where the
   largest weight moves to another stock, and ranks swap on 15. On tomorrow's
   own weights PC2 reads −0.1105, matched −0.0161, and on weights fitted
   without today 0.0776, beside the test's 0.0778. A 251-day window that
   still holds today reads −0.0158, like the matched row.
2. Leaving the mean in is a choice with a reason, because "remain constant"
   describes a steady value. The price is that two days carry 97.04 percent
   of PC2's squared products.
3. The factor return the forecast reads is the slope times the day's singular
   value, and dropping the intercept leaves the ranking unchanged on all 752
   days t.
4. Four of five passing says little. Only PC2 is outside the ±0.0715 band,
   its t is 0.8254, and none survives Benjamini-Hochberg.
5. One spliced symbol decides which factor misses. A top-five factor weighs
   PMC at 0.5939 or more on each of the 113 days whose window holds its one
   large return and that have a next day. PMC takes PC1 through 2007-08-10,
   so PC2's two large days belong to the factor that is PC1 without PMC, and
   without PMC the miss moves from PC3 to PC2.

Four groups of what it says are not pinned here.

1. Chan's words, each cited by its page in the revised edition, as the
   factor models post's block above records. "Based on the assumption that
   factor returns have momentum" and "remain constant from the current time
   period to the next" (location 4051) are cited at p. 164, and "often" and
   "stronger serial autocorrelations than individual stock's returns"
   (location 4014) at p. 162, through
   [its committed notes](research/book-notes/quantitative-trading.md).
2. Facts outside the committed data: that 2007-08-09 and 2007-08-10 fall in
   the week Khandani and Lo studied, and that the revised MATLAB prints
   Chan's 2 percent a year before costs.
3. Readings and arithmetic no test asserts: that the library's own signs
   flipped on about half the days on the two machines that ran the checks
   and disagreed about which, which no test pins because it depends on the
   library, that a principal component's rank can change from day to day in
   general, the closed form of
   the slope and intercept written out in Lesson 3, that the positions chosen
   on day t earn day t + 1's return, 5/√70 written as positive, 1.8654 written
   as 186.54 percent, a fifth of 5 percent written as 0.01, the same-sign
   shares called close to a coin toss, that PC1 is the factor that moves the
   whole market, that 2007-08-09 and 2007-08-10 are what put PC2 outside the
   band, and that the window's effect on PC2 is not explained. The figure's alt text reads its curve approximately too.
4. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_pca_factor_momentum.py](tests/test_pca_factor_momentum.py), to
`TestTheSplice` in [tests/test_pca_factor.py](tests/test_pca_factor.py) for
PMC's 1.8654 and its 851 days, or to
[tests/test_pca_factor_momentum_figures.py](tests/test_pca_factor_momentum_figures.py)
for the figure's own labels. `TestWhatThePostMeasured` holds the ones that had
no pin before it, all measured after the run.

1. Each factor's sign flips once every vector's largest weight is made
   positive, 1, 14, 6, 22 and 24 of 752 days, and the 15 days two or more
   factors swap rank, over 753 decompositions. The stock holding the largest
   weight moves on 1, 14, 6, 20 and 23 of those flips, and the three left,
   PC4 on 2005-06-15 and 2007-06-29 and PC5 on 2007-08-01, fall on days two
   or more factors swap rank.
2. The statistic on tomorrow's own weights under the same rule, 0.0326,
   −0.1105, −0.0283, −0.0315 and 0.0025, matched, 0.0246, −0.0161, −0.0318,
   −0.0285 and 0.0768, and on weights fitted on the 251 days that leave today
   out, 0.0315, 0.0776, −0.0228, 0.0338 and 0.0713. The largest gap to the
   test's own figure is PC2's 0.0938 matched and PC3's 0.0039 left out. The
   control, on the 251 days ending today, reads 0.0252, −0.0158, −0.0307,
   −0.0350 and 0.0810.
3. The 114 days whose window holds PMC's return, and the 113 of them from
   2007-08-02 to 2008-01-11 with a next day, PMC's largest weight of at least
   0.5939 on each, and PC2 carrying it on 103, PC1 on 7 and PC3 on 3. PC1
   carries it on the first seven, through 2007-08-10, at a weight between
   0.9144 and 0.9223, and PC2 from 2007-08-13. Without PMC, 2007-08-09 and
   2007-08-10 hold 0.9461 of the sum of PC1's squared products, and on both
   days PC2 with PMC overlaps PC1 without it at 0.98 or more in size.
4. The ranking without the intercept agreeing on all 752 days t.
5. No stock tying any factor, the nearest 1.06e-04 away with PMC and 3.85e-05
   without.
6. The two days, 2007-08-09 and 2007-08-10, holding 0.9704 of the sum of
   PC2's squared products.
7. The steady series' 0.9798 uncentred against −0.8 centred.

Its one figure is drawn from the committed file by
[src/chan/pca_factor_momentum_figures.py](src/chan/pca_factor_momentum_figures.py),
which reads it through the same `load_panel`, `compute_both` and
`daily_components` as the pins. It draws two panels.

1. The 579 stocks' statistics as their cumulative curve, with the ±0.0715
   band, zero and the median stock, each factor's statistic as a filled dot
   at its percentile, and a hollow dot for the same factor without PMC.
2. For each factor, the statistic on tomorrow's own weights with the sign
   rule, matched, on
   weights fitted without today, and as the test reads it, over the same
   band.

```bash
uv run python -m chan.pca_factor_momentum_figures
```

[tests/test_pca_factor_momentum_figures.py](tests/test_pca_factor_momentum_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/monte-carlo-leverage-lessons.md](blog/monte-carlo-leverage-lessons.md)
is a forty-second post, about Chapter 8 of Chan's *Algorithmic Trading*,
which finds a leverage for Example 5.1's AUD.CAD returns two ways, by Monte
Carlo on draws with the returns' four moments and by the optimum of the
historical growth rate, and caps the loss at the chosen leverage with
constant proportion portfolio insurance (CPPI). The post links the capped
Kelly allocation post, the AUD.USD against CAD.USD post, the coin toss post,
the Kelly leverage on SPY post and the TU hypothesis tests post rather than
repeating them, and draws six lessons from Entry 43 of the replication log.

1. The book's Kelly and historical optimum of 18.4 do not reproduce. Chan's
   saved returns give 23.845328 and 23.721773, within 0.52 percent of each
   other.
2. Example 5.1's printed Sharpe ratio and APR allow a Kelly of 21.558894 to
   26.757652, and the edge moves to 22.065999 or 20.891304 under the other two
   compoundings, so none reaches 18.4. Moving the draws' mean to a Kelly of
   18.4 puts the median uncapped optimum at 18.470198 and lands all but the
   drawdown at half the optimum. The post labels as an inference that
   Chapter 8 ran on a different series of returns, with a Kelly near 18.4,
   that nobody holds.
3. The script's search stops at 20, and 158 of the 200 seeds sit on that cap,
   exactly the seeds whose ruin leverage is 20 or more. The 30 seeds whose
   uncapped optimum reaches 19.2 all ruin below 20. Under the declared band
   both of the book's optima land, and under the band chosen after the seeds
   were seen neither does. The post keeps both.
4. The declared seed's least draw of −0.043071 is 1.9550 times as deep as the
   worst saved return, −0.022031, because there are about 163 times as many
   draws. The least of 612 draws from the fit reaches −0.022031 with a chance
   of only 0.091663, so the fit's tail is not the cause. The Kelly lies at or
   past the ruin leverage on 78 of the 200 seeds, and the 42 seeds that ruin
   below the cap sit 2.4 binomial standard errors above the exact chance.
5. Box 8.6's loop falls to −0.848088 and below −0.5 on every seed, while the
   scheme location 3426 describes stays above −0.5 on every seed, at a cost of
   0.255285 of the growth.
6. The drawdown at the optimum and the full account's −0.9 land, and the
   drawdowns at half and a seventh of the optimum and both growth rates miss
   their bands. On the saved returns the drawdown at the historical optimum
   is −0.737560.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   the 11 percent and 1.6 at 2237, the Kelly as an upper bound and the
   bankruptcy in backtest at 3235, Monte Carlo at 3280, the Pearson system at
   3319, the 18.4, the type, the 19, "strikingly close", the −0.0331, the
   total loss above 30.2 and Figure 8.2's caption at 3342, the historical 18.4
   and "again the same" at 3379, the −0.999, the 19.2, the −0.963, the
   seventh and "not exactly reproducible" at 3399, simulated against
   historical drawdowns and serial correlation at 3417, the CPPI scheme and
   its −D at 3426, and the two growth rates, D of 0.5, "By design" and "a
   painful 0.9" at 3438. The book's figures are pinned as the module's
   constants, and its words are not.
2. Facts about the script rather than the data: line 22's
   `fminbnd(minusGsim, 0, 20)` and Box 8.6 scaling its order by the drawdown
   of the unlevered returns, in `monteCarloOptimLeverage.m`, git blob
   `fc32599` at `e4bc46f` of ericnberwick/EpchanPreview.
3. Readings no test asserts: that a bell curve's parabola is defined at every
   leverage while a sampled curve stops at its ruin leverage, that moments
   below order 5.51 mean tails far heavier than a bell curve's, that the
   account at the script's f moves ten times the unlevered returns so the
   loop barely cuts its order, that the book's −0.9 and −0.963 most likely
   come from different runs, that Chapter 8 most likely ran on a different
   series of returns with a Kelly near 18.4 and that the evidence cannot tell
   when or how it differed from the saved file, that trial variants of the
   saved series reached no 18.4, that at the same daily risk a path of 100,000
   days is all but certain to reach a deeper drawdown than one of 612, and
   that a picture built around one band rule would look like an endorsement
   of that rule.
4. Figures the post rounds or states in words from pinned ones: 23.8, a gap
   of 5.4 below the saved returns, within 0.52 percent, 13.9 to 14.9 percent,
   nearly twice as deep, about 163 times as many draws, about 9.2 percent,
   about 29.8 seeds, 2.4 standard errors, about 1.3 percent, 1.4 percent,
   about a quarter, the book's pair near 1.6 percent apart, and one decimal
   covering −0.95 to −0.85. The growth rates pinned at six significant
   figures are quoted at six decimals. The figure's alt text reads its curves
   approximately too, such as a peak of about 0.0048 near 22.3 and a band
   from about 21.6 to 26.8.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_monte_carlo_leverage.py](tests/test_monte_carlo_leverage.py), or
to
[tests/test_monte_carlo_leverage_figures.py](tests/test_monte_carlo_leverage_figures.py)
for the figure's own numbers. The 612 returns' dates, from 2009-12-18 to
2012-04-26, trace to
[tests/test_aud_cad_johansen.py](tests/test_aud_cad_johansen.py). Twelve of
the post's numbers had no pin before the post, all measured after the run.

1. The least of the 612 saved returns, −0.022031, and their ruin leverage,
   45.390502, with the declared seed's least draw 1.9550 times as deep.
2. The 30 seeds whose uncapped optimum is at or below 19.2 and the 28 at or
   below 19, all with a ruin leverage below 20, the largest 19.147175.
3. A seed on the cap exactly when its ruin leverage is 20 or more, the lowest
   uncapped optimum among those 158 at 20.075698.
4. The Kelly at or past the ruin leverage on 78 of the 200 seeds and on the
   declared one.
5. On the saved returns, `calculateMaxDD` at the historical optimum,
   −0.737560, and at the Kelly, −0.739733.
6. The growth on the declared seed at its uncapped optimum, 4.801065e-03, and
   at the script's capped answer, 4.735998e-03.
7. The growth on the saved returns at their optimum, 5.197618e-03, and at the
   Kelly, 5.197464e-03.
8. Box 8.6's loop first below −0.5 on day 303, deepest on day 37,071, and
   below −0.5 on 5,681 days.
9. Location 3426's scheme deepest on day 33,785 and never below −0.5.
10. The full account at f·D deepest on day 37,071, below −0.5 on 6,034 days
    from day 303.
11. The chance of 0.091663 that the least of 612 draws from the fit is at or
    below the saved returns' least day.
12. The 42 seeds that ruin below the cap sitting 2.414274 binomial standard
    errors above the exact chance, with an exact chance of 0.012871 of 42 or
    more.

Its one figure is drawn from the committed vintage by
[src/chan/monte_carlo_leverage_figures.py](src/chan/monte_carlo_leverage_figures.py),
which reads it through the same `read_returns`, `pearson_fit`, `draws`,
`growth`, `optimal_leverage`, `kelly` and CPPI functions as
`python -m chan.monte_carlo_leverage`, and each day's drawdown through
`account_drawdowns`. It draws two panels on the declared seed only.

1. The book's Figure 8.2, the growth rate against the leverage, on the
   declared seed's draws up to their ruin leverage and on the saved returns,
   with the script's cap, both optima, the Kelly, the Kelly range Example
   5.1's printed figures allow and the book's 18.4, 19 and 19.2 marked.
2. The deepest drawdown in each 1,000 days of the draws for Box 8.6's loop,
   location 3426's scheme and the full account at f·D, with a line at −0.5.

```bash
uv run python -m chan.monte_carlo_leverage_figures
```

[tests/test_monte_carlo_leverage_figures.py](tests/test_monte_carlo_leverage_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

[blog/levered-low-beta-lessons.md](blog/levered-low-beta-lessons.md) is a
forty-third post, about Chan's rule at Kindle location 4709 of
*Quantitative Trading* that a highly levered portfolio of low-beta stocks
should out-compound an unlevered portfolio of high-beta stocks, with the beta
match of location 4684 and the fat-tail caveat of location 4700. It is the
first post whose headline result is registered, and it says why that differs
from the earlier posts' label. The post links the Kelly leverage on SPY post,
the risk parity post and the factor models post rather than repeating them,
and draws six lessons from Entry 45 of the replication log.

1. The low fifth had the higher Sharpe ratio, 1.0132 against 0.4457, and
   levered to the high fifth's beta it lost more than its capital in June
   2001, at a leverage of 58.0262.
2. The leverage divides by the low fifth's beta, which fell below 0.05 at
   four formations from 2001-03-30 to 2001-06-29, so k reached 69.0762.
3. An ordinary month did it. June 2001's −0.0403 was the sixth-worst of 83,
   13 months reached that month's ruin line, and a normal month reaches it
   with a chance of 0.1931, so the caveat's advice holds and its reason is
   not what the run shows.
4. The rule names no leverage, and the look-ahead Kelly leverage of 9.9884
   sat below the match at 13 formations.
5. The plan left the ruined month undefined, and the owner settled the ruin
   case after seeing its first instance.
6. A registered result on years the claim's source could already read is
   not a holdout, and the file holds only survivors.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Quantitative Trading*
   through [its committed notes](research/book-notes/quantitative-trading.md):
   the beta match, the Fama-French model, the Kelly argument, "Empirical
   studies" and Qian's risk parity at 4684, the fat-tail caveat at 4700, and
   the rule at 4709.
2. The plan's history rather than the data: that the plan, the
   specification and the first three outcomes were written before any number,
   that the build stopped at June 2001, and the four things seen before the
   ruin ruling. Entry 45 of the replication log records each.
3. Readings no test asserts: that the Fama-French model ties return to beta,
   size and book-to-price ratio, that growth at the Kelly leverage is the
   cash rate plus half the Sharpe ratio squared, which the Kelly post
   derives, that in-sample Kelly leverage gives a portfolio the highest
   growth the formula allows, that levering a portfolio k times multiplies
   its beta by k, that the low fifth's 1.0132 and 0.4457 make the low fifth
   look better, that the numerator of k moved within a narrow band, that
   2000 to 2007 were past prices when the book printed the claim, and that
   high-beta stocks leaving the index would flatter the high side, which is
   a hypothesis.
4. Figures the post states in words or rounds from pinned ones, such as
   more than twice the high fifth's Sharpe ratio, both 2000 formations near
   0.15, −1.44 percent for the line of −0.0144, and about one month in five
   for 0.1931. The worked examples that gloss beta and leverage, a beta of 2
   and a leverage of 3, are illustrations rather than figures from the file.
   The figure's alt text reads its curves approximately too.
5. Its reference, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_low_beta_leverage.py](tests/test_low_beta_leverage.py), or to
[tests/test_low_beta_leverage_figures.py](tests/test_low_beta_leverage_figures.py)
for the figure's own numbers. `TestWhatThePostMeasured` holds the ones that
had no pin before it, all measured after the run.

1. The low fifth's beta of 0.1443 at the 2000-12-29 formation, below 0.05 at
   four formations, 0.0375, 0.0280, 0.0337 and 0.0448 from 2001-03-30 to
   2001-06-29, and below 0.10 at nine, 2001-01-31 to 2001-09-28.
2. k above 20 at eight formations, 2001-02-28 to 2001-09-28, and above the
   look-ahead Kelly leverage of 9.9884 at 13, 2000-12-29 to 2001-12-31.
3. The levered wealth of 4.8089 through 2001-05-31, after levered returns of
   −0.5456 in January 2001 and −0.4516 in March, and May 2001's levered
   return of 1.7253 on a low-fifth return of 0.0279.
4. The ruin line at −0.0144 for June 2001, with that month's bill rate of
   0.0029, and at −0.0296 for September 2001. Its highest value is −0.0115,
   in May 2001, and it sits below −0.10 from 2002-02-28 on, below the low
   fifth's worst month, −0.0733 in July 2002.
5. The low fifth's September 2001 return of −0.0337, the eighth-worst of 83.
6. The 13 of 83 months at or below June's line, which holding k at 58.0262
   every month would also ruin.
7. The leverage that ruins June 2001, 23.2017, and September 2001, 27.9461,
   and the match's 58.0262 for June at 2.50 times the first.
8. The low fifth's monthly mean of 0.0109 and standard deviation of 0.0292,
   and the normal chance of 0.1931 of a month at or below June's line.

Its one figure is drawn from the committed vintages by
[src/chan/low_beta_leverage_figures.py](src/chan/low_beta_leverage_figures.py),
which reads them through the same `read_sources` and `build_portfolios` as
`python -m chan.low_beta_leverage`. It draws three panels on one axis of
holding months, so each value sits at the month it applied to.

1. Each fifth's mean beta at formation, with the low fifth's 0.0280 marked.
2. k on a log axis, with its highest, both ruined months and a dashed line at
   the look-ahead Kelly leverage.
3. The low fifth's monthly return against its ruin line, with the two months
   below it marked.

```bash
uv run python -m chan.low_beta_leverage_figures
```

[tests/test_low_beta_leverage_figures.py](tests/test_low_beta_leverage_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map. It also holds where each label's rule points, and that each
label's text sits inside its panel, clear of the other labels and of every
line.

[blog/build-board-on-github-lessons.md](blog/build-board-on-github-lessons.md)
is a forty-fourth post, and the first about how the repository runs rather
than about one of Chan's books. It reports the build board's move on
2026-10-11 from a claude.ai artifact that every session wrote by hand to a
GitHub Pages page that `.github/workflows/board.yml` rebuilds with
`scripts/build_board.py`. It replicates nothing, so the replication log has no
entry for it. It draws six lessons.

1. Writing the page by hand cost a turn for every change, 240 updates in
   1.887 days at about \$111 a day.
2. The version check refused 77 writes across 57 of the 240 updates.
3. 87 of 146 sub-agent reports ended with something still stale, a count from
   the transcripts alone, and some events, such as a merge from GitHub's web
   page, reached no session.
4. The owner's ranking lived only in the artifact until a backfill moved it
   onto labels, links and issue lines.
5. The move cost \$101.80, and on an estimate, it pays back in about a day
   and a third, at an estimated \$33.5 a day after it.
6. The move added five costs of its own, among them 2,903 new lines of script
   and tests and a page that trails GitHub by a minute or more.

Seven groups of what it says are not pinned here, and none of its figures
traces to a test. The cost figures come from Claude Code transcripts, which
are private and machine-local, so no test can read them, and the post states
each one's window, date and method where it first appears.

1. Figures before the move, from board-update turns over 2026-10-10 00:00Z to
   2026-10-11 21:17Z priced at Claude Opus 5.5 list prices: the 240 updates,
   the \$185.22 and \$24.41 that make \$209.63, \$111.09 a day, the medians,
   times and cost range by kind of update, the token counts, the in-session
   counts under each grouping cutoff, and the 77 refused writes across 57
   updates.
2. The after estimate, from one label edit and one board check, and the
   return table computed from it.
3. The cost of the move, \$101.80 in five parts, and the earlier measurement
   of about \$51 a day with its counts, quoted from
   [issue 531](https://github.com/l3a0/quantitative-trading/issues/531).
4. Counts from transcripts alone: the 87 stale reports of 146 and the two
   incidents.
5. Facts read from GitHub while the post was written: the merge times, the
   board runs and their timings, the backfill's planned and landed writes,
   the `band:N` labels and `Board order:` lines, the line counts of the skill,
   the script and the tests, and the cron runs not yet seen.
6. Readings and rounding no test asserts: about one in four, about a day and
   a third, and that each refused write could have overwritten another
   session's change.
7. Its references, cited rather than computed, which include the list prices
   and the Pages and Actions behaviour.

[blog/capped-low-beta-lessons.md](blog/capped-low-beta-lessons.md) is a
forty-fifth post, about Chan's rule at Kindle location 4709 of *Quantitative
Trading* tested at the two ceilings on leverage his own text gives, 2 under
Regulation T at location 814, which location 2836 repeats for a retail account
held overnight, and 5 under portfolio margin at location 814. Every figure in
it is exploratory, and it says why: the plan came after Entry 45's figures had
been seen, the file holds only survivors, and Chan prints no figure for the
rule to reproduce. The post links the
levered low-beta post for the setup and the Kelly leverage on SPY post rather
than repeating them, and draws five lessons from Entry 48 of the replication
log.

1. A plan written after the data was seen has to say what was seen. Entry
   45's unlevered growth of 0.1254 against 0.1183 and its Kelly leverage of
   9.9884 made a positive point estimate at either ceiling predictable.
2. Capping the leverage removes the ruin. No month lost all the capital at
   either ceiling, the worst was July 2002 at −0.1479 and −0.3719, and no
   leverage below 13.4118 would have ruined any of the 83 months.
3. A large point estimate can still be noise. The gaps of 0.0934 and 0.1659
   a year fall short of 5 percent lines at 0.1434 and 0.2254, and each is
   under half of its detectable gap Y, 0.2168 and 0.3407.
4. Testing two ceilings costs a correction. Benjamini-Hochberg passes
   neither ceiling in either direction, and neither p-value, 0.1420 and
   0.1129, would pass a single test either.
5. The borrowing rate is a hidden assumption. A spread over the bill rate of
   0.0946 a year at a ceiling of 2, or 0.0661 at 5, erases the point estimate.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Quantitative Trading*
   through [its committed notes](research/book-notes/quantitative-trading.md):
   "highly leveraged" at 4709, the beta match at 4684, Regulation T's
   overnight leverage of 2, portfolio margin's 20 percent for a portfolio of
   large-cap stocks hedged so that its long and short sides are equal in
   value and its 50 percent for a long-only portfolio of small-cap stocks at
   814, and a retail account's 2 at 2836.
2. The plan's history rather than the data: that the plan was written on
   2026-10-11 before any capped number and after the five things Entry 45 had
   shown, the four outcomes and the wording of each, and that the plan would
   have sent both ceilings to a holdout only if one had held. Entry 48 of the
   replication log records each.
3. Readings no test asserts: what Regulation T and portfolio margin are, that
   a margin of 20 percent is a leverage of 5, that 5 is the highest leverage
   the book puts a number on for stocks held overnight and its "or less"
   leaves room for more, that a broker might not lend 5 to a long-only
   portfolio, and that growth rises with leverage up to the Kelly leverage
   under a bell curve, which the Kelly post derives. Also that leverage
   multiplies the low fifth's excess return and its swings by the same L,
   while d also subtracts the high fifth's log return and log growth gives up
   more to volatility as leverage rises, so nothing fixes t as leverage
   changes. Also that 80 percent of a bell curve lies above 0.8416 standard
   deviations below its centre, that a second one-sided test raises the chance
   of a false gap to as much as twice as high, the general Benjamini-Hochberg
   rule, and that the corrected test needs a gap at least as large as Y, and a
   larger one unless the other ceiling also clears 5 percent. Last, that a
   higher mean leverage borrows more and so breaks even at a smaller spread,
   that FINRA Rule 4210's maintenance margin of 25 percent calls a position
   levered 2 after a fall of a third while Regulation T sets only the 50
   percent needed to open it, and that a leverage of 5 at a margin of 20
   percent leaves no cushion.
4. Figures the post states in words or derives from pinned ones. The ratios
   of about 1.78 and 1.57 divide ceiling 5's gap and standard error by ceiling
   2's. The 2.5134 borrowed for each unit of capital is ceiling 5's mean
   leverage of 3.5134 less 1, and 2.51 is that against ceiling 2's 1. The
   0.0975 is 1 − 0.95², the chance that two independent 5 percent tests find
   at least one false gap. The p-value of 0.04 in Lesson 4 is an illustration
   rather than a figure from the file. The figure's alt text reads its curves
   approximately too.
5. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_low_beta_capped.py](tests/test_low_beta_capped.py), to
[tests/test_low_beta_leverage.py](tests/test_low_beta_leverage.py) for Entry
45's figures, or to
[tests/test_low_beta_capped_figures.py](tests/test_low_beta_capped_figures.py)
for the figure's own numbers. `TestWhatThePostMeasured` holds the ones that
had no pin before it, all measured after the run.

1. The yearly standard error of the gap, 0.0872 at a ceiling of 2 and 0.1370
   at 5, and the one-sided 5 percent line at 1.645 times it, 0.1434 and
   0.2254, with Y at 1.645 + 0.8416 times it.
2. Each point estimate falling short of its line and under half of its Y.
3. June 2001's capped return, −0.0835 at a ceiling of 2 and −0.2132 at 5.
4. The smallest leverage that would have ruined any of the 83 months,
   13.4118, for July 2002, above both ceilings.

Its one figure is drawn from the committed vintages by
[src/chan/low_beta_capped_figures.py](src/chan/low_beta_capped_figures.py),
which reads them through the same `read_sources`, `build_portfolios` and
`assess` as `python -m chan.low_beta_capped`. It draws one panel per ceiling
on one shared axis of the yearly gap, so the 5 percent line moves right as
the leverage rises. Each panel draws four things.

1. The sampling curve if the true gap were 0, a normal with the yearly
   standard error.
2. The one-sided 5 percent line.
3. The same curve centred on Y, with the four fifths of it past the line
   shaded.
4. The point estimate on the baseline, labelled with its t.

```bash
uv run python -m chan.low_beta_capped_figures
```

[tests/test_low_beta_capped_figures.py](tests/test_low_beta_capped_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map. It also holds where each label's rule points, and that each
label's text sits inside its panel, clear of the other labels, the legend and
every line. Each panel's heading clears the title or the tick labels above it,
and the gap axis's label clears the note below it.

[blog/vix-filter-lessons.md](blog/vix-filter-lessons.md) is a forty-sixth
post, about the VIX filter at Kindle location 3509 of Chan's *Algorithmic
Trading*, which keeps only the days after VIX closed above 35 and reruns
Example 4.1's buy on gap and Example 7.1's opening gap rule on FSTX on them.
The post links the buy on gap post and the opening gap post rather than
repeating them, and draws five lessons from Entry 47 of the replication log.

1. The filtered figure is 252 times the mean, 0.171924 and a Sharpe ratio of
   1.417425 on buy on gap's 190 kept days, while the 8.7 percent set beside
   it is the compounded APR. Like for like, 252 times the mean over every day
   is 0.085279.
2. FSTX's 0.025730 and 0.164869 on 185 kept days belong to the script's
   fading sign, the momentum sign gives them negated, and the book's
   unfiltered and filtered FSTX figures come from different calendars.
3. Six ways of reading VIX on FSTX's days were tried, only the join lands
   both figures, and buy on gap's figures do not move under any reading of
   the previous day.
4. The kept days are few and bunched: 151 of buy on gap's 190 and 146 of
   FSTX's 185 fall in 2008 and 2009, in 15 runs, and buy on gap held a
   position on 20 of its kept days, one of which, 2009-04-21, returned
   0.093601 of the 0.129625 its kept days sum to.
5. Welch's t on mean daily return cannot tell the kept days from the rest,
   with p of 0.481405 for buy on gap and 0.494679 for FSTX.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md):
   the momentum rule at 2965, the sentence that no one risk indicator suits
   every strategy, the threshold of 35, "a common threshold for highly risky
   periods", the four unfiltered and four filtered figures and both of
   Chan's conclusions at 3509, and the warning about data snooping at 3541.
   The threshold and the four filtered figures are pinned, as book targets
   in `TestTheSpecification` in
   [tests/test_vix_filter.py](tests/test_vix_filter.py), and Chan's words are
   not.
2. Facts about the index and the scripts rather than the data: that the
   Chicago Board Options Exchange computes VIX from the prices of options on
   the S&P 500 and that it measures the swings they imply for the next month,
   that it closes at 16:15 New York time, after FSTX opens, and
   that no script in either public copy of Chan's code applies the filter.
3. Readings no test asserts: that the kept days earned more per day and
   swung more for it, that 15 runs are fewer separate episodes than 190 days
   suggest, that the alignment found by search makes the 2.6 percent a
   fit rather than a test, that neighbouring days' returns can move together
   and the test then counts more independent days than the sample holds,
   and that a filter keeping few traded days leaves each cost a larger share
   of the return.
4. Readings the post rounds from pinned figures, most of the 17.2 and about
   half the time for p near one half. The figure's alt text reads its curves
   approximately too. The 8.5 percent it quotes from the buy on gap post is
   pinned in [tests/test_buy_on_gap.py](tests/test_buy_on_gap.py) rather than
   in this post's tests.
5. Its reference, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_vix_filter.py](tests/test_vix_filter.py), or to
[tests/test_vix_filter_figures.py](tests/test_vix_filter_figures.py) for the
figure's own numbers. `TestWhatThePostMeasured` holds the ones that had no pin
before it, all measured after the run.

1. Buy on gap's kept days by year, 68, 83, 9 and 30 for 2008 to 2011, and
   FSTX's, 65, 81, 9 and 30, so 151 of 190 and 146 of 185 fall in 2008 and
   2009.
2. Each rule's 15 runs of kept days, on the same dates for both, the longest
   from 2008-09-30 to 2009-04-17, holding 138 of buy on gap's days and 134
   of FSTX's.
3. VIX's 190 closes above 35 in 15 runs from 2004-07-16 to 2012-05-08, its
   highest close of 80.86 on 2008-11-20, and its last above 35, 36.16 on
   2011-11-09.
4. The 100 closes above 35 in `VIX.csv` before 2004-07-15, the first on
   1990-08-06.
5. Each rule's daily returns summed over its kept days, 0.129625 for buy on
   gap and 0.018889 and −0.018889 for FSTX under the two signs.
6. Buy on gap's largest kept day, 2009-04-21, which returned 0.093601, or
   0.722090 of the sum, its 8 gaining and 12 losing held days, and the other
   189 kept days' 0.048032 and Sharpe ratio of 0.855003.

Its one figure is drawn from the committed vintages by
[src/chan/vix_filter_figures.py](src/chan/vix_filter_figures.py), which reads
them through the same `read_sources` and `vix_filters` as
`python -m chan.vix_filter`, so the scale-break guard runs for it too. It
draws two panels on one date axis from 2004-07-16 to 2012-05-08, both shading
the span from 2008-09-18 to 2011-11-10 that holds every kept day.

1. VIX's close with a dashed line at 35, the closes above it marked, and the
   first, highest and last close above 35 inside the window labelled.
2. Each rule's daily returns summed over its kept days, with nothing earned on
   the other days, and buy on gap's largest kept day marked.

```bash
uv run python -m chan.vix_filter_figures
```

[tests/test_vix_filter_figures.py](tests/test_vix_filter_figures.py) holds
what it draws rather than its bytes, for the reason given above for the regime
map.

[blog/low-beta-holdout-lessons.md](blog/low-beta-holdout-lessons.md) is a
forty-seventh post, about the same rule at location 4709 tested on IVV's S&P
500 members at each month-end from 2008-12, every holding month after the
first edition's release in November 2008. Its verdict is registered under two
amendments and every other figure is exploratory. Every figure computed from
the prices of IVV's members reads the owner's archive, so a reader cannot
rerun it, while the membership and coverage counts read committed files. The
post links the levered low-beta post for the rule, the beta match, the ruin
line and June 2001 rather than repeating them, and draws five lessons from
Entry 49 of the replication log.

1. The test is not decided. The levered low fifth trailed by 0.0590 a year at
   a Newey-West t of −0.4974, and Y is 0.2948. Measured after the run, a
   one-sided test at 5 percent rejects every levered advantage above 0.1360 a
   year, and dropping December 2024 alone turns the gap to +0.0313.
2. The rule ruined a portfolio on Chan's file and not on the new panel. k
   peaked at 27.9727 against 69.0762, the low fifth's beta bottomed at 0.0563
   against 0.0280, and December 2024, the worst levered month, was asked for
   0.80 of the leverage that ruins it, where June 2001 was asked for 2.50
   times.
3. The beta match stops being defined at a low beta of zero or below, which
   the last four formations reached, and the skip rule was ruled after the
   first of them was seen.
4. A point-in-time panel moves the survivor problem. 6,816 of 107,115
   member-months fail the row check against the filing, 3,654 with no close,
   933 with no series and 2,229 with a wrong price. 4,614 of them carry a
   ticker absent from the last schedule and 5,891 fall from 2009 to 2015.
5. Carrying the plan over needed a written list of ten points, five of which
   change what the run computes, and two exclusions still read the month-end
   after the formation.

Six groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Quantitative Trading*
   through [its committed notes](research/book-notes/quantitative-trading.md):
   the rule at 4709, the fat-tail caveat at 4700, and the equal average
   returns at 4684.
2. The plan's history rather than the data: that the plan, the panel's
   changes and the criterion were written before any beta or return was
   computed on this panel, that the run stopped at the 2026-04-30 formation
   before computing anything the criterion reads, that no earlier formation's
   beta had been printed or read, that the owner then ruled to skip such
   formations, and that the three later formations were not yet known. Also
   the sorting of the ten points into five that change the computation, three
   that restate a rule, one that corrects the survivor label and one that
   gates the tests. Entry 49 of the replication log and its plan record each.
3. Readings no test asserts: that a negative k would mean selling the low
   fifth short, that the peak of 27.9727 above June 2001's ruinous 23.2017
   means Chan's June 2001, levered that far, would still have lost the whole
   capital, that ruin needs a large k and a bad month at once, that the
   panel's failures lean toward companies that left, that the Newey-West t
   and the bound treat the monthly gaps as roughly normal, and what the row
   check compares.
4. Figures the post states in words, such as a few hundredths a year, and the
   figure's alt text, which reads its curves approximately.
5. Facts outside the committed data: the first edition's release in November
   2008, and that this repository has read the rule only in the 2021 revised
   edition and has not checked that the first edition prints it.
6. Its reference, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_low_beta_holdout.py](tests/test_low_beta_holdout.py), to
[tests/test_low_beta_leverage.py](tests/test_low_beta_leverage.py) for the
figures on Chan's file, or to
[tests/test_low_beta_holdout_figures.py](tests/test_low_beta_holdout_figures.py)
for the figure's own numbers. Two classes hold the ones that had no pin
before the post, all measured after the run.
`TestWhatThePostCounted` reads committed files and runs everywhere.

1. 5,891 of the 6,816 member-months failing the row check fall in 2009 to
   2015.
2. The 70 schedules each carry forward two months, except 2013-06-30, which
   carries five. The last, 2026-06-30, carries two, to 2026-08.
3. The 2,187 failing member rows split 1,186 with no close, 697 with a wrong
   price and 304 with no series.
4. 26,353 of all 35,205 member rows carry a ticker still in the 2026-06-30
   schedule, 74.9 percent, against 697 of the 2,187 failing rows, 31.9
   percent.
5. On Chan's file, the close the earlier test asks for at the next month-end
   left out 17 stocks at six formations, each with closes after the gap, and
   no series ends before the file's last day.

`TestWhatThePostMeasured` reads the archive.

1. The standard error of the gap, 0.1185 a year, and the one-sided upper
   bound of 0.1360.
2. The unlevered fifths' gap of 0.0543, from the unrounded growth rates.
3. The high fifth's beta of 1.5738 where k peaked, and the low fifth's beta
   below 0.10 at two formations, 0.0818 at 2025-02-28 and 0.0563 at
   2025-03-31, and below 0.05 at none.
4. December 2024's ruin line of −0.0776, its margin of 0.0161 above it, its
   ruinous leverage of 15.4077, the match's 0.80 of it as the largest share of
   any month, and its rank as the seventh-worst of 208 low-fifth months.
5. April 2025's low-fifth return of −0.0176, levered return of −0.5856, ruin
   line of −0.0324 and ruinous leverage of 47.6485, and its margin of 0.0148
   as the closest of any month.
6. No month of 208 at or below its own ruin line.
7. March 2020, the low fifth's worst month at −0.1250, with k at 3.4162, its
   ruin line at −0.2926 and a levered return of −0.4278.
8. December 2024's d of −1.5624 and March 2026's of −1.1582, the two lowest,
   and the gap of +0.0313 without December 2024 and +0.0989 without both.
9. March 2026, the second-worst levered month at −0.7005, with k at 9.4342,
   the low fifth at −0.0716 and the high fifth at −0.0463.

Its one figure is drawn by
[src/chan/low_beta_holdout_figures.py](src/chan/low_beta_holdout_figures.py)
in two columns and two rows. The left column is Chan's file from the committed
files, and the right is IVV's members from one run of
`chan.low_beta_holdout.read_holdout`.

1. Each fifth's mean beta at formation, with the low fifth's lowest marked,
   0.0280 and 0.0563, and the four skipped formations' negative low betas
   plotted.
2. k on one log axis for both columns, with the highest of each, Chan's two
   ruined months and December 2024 marked, and the skipped months shaded.

```bash
QT_ARCHIVE_DIR=/path/to/archive uv run python -m chan.low_beta_holdout_figures
```

[tests/test_low_beta_holdout_figures.py](tests/test_low_beta_holdout_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map. Its drawing runs on every clone, with Chan's committed files on
the left and a synthetic holdout on the right, and only its checks of the
real right column's marks and labels need the archive. So does the comparison
of a fresh draw with the committed file in
[tests/test_figures_match_code.py](tests/test_figures_match_code.py). The
price is that CI never sees the real right column drawn, and a reader cannot
redraw it.

[blog/usdcad-holdout-lessons.md](blog/usdcad-holdout-lessons.md) is a
forty-eighth post, about Example 2.5 of Chan's *Algorithmic Trading* run on
USD.CAD after his sample, with the lookback frozen at the 115 days his closes
give. It reads Alpha Vantage's `FX_DAILY` closes, downloaded 2026-10-13, and
trades 3,791 days from 2012-03-29 to 2026-10-12. Its verdict and four of the
predictions beside it are registered, and every other figure is exploratory.
The post links the earlier USD.CAD post for the tests and the rule rather than
repeating them, and draws five lessons from Entry 51 of the replication log.

1. The claim survives on its sign alone. The P&L ends at 0.1132, above 0, and
   the Newey-West t of its mean daily value is 0.2670. Its Sharpe ratio is
   0.0715, against 0.12 on Chan's closes.
2. Writing the predictions down first is what makes it a check. Six
   predictions and one figure to report were filed before any later close was
   read, and the three earlier reads of those closes decided nothing. The
   prediction on Chan's 16:59 bar did not run.
3. The later closes read as a random walk, as predicted. The ADF statistic of
   −2.0814 does not reject at 10 percent, the variance ratio test's p-value is
   0.4343, and H of 0.4974 sits inside its random-walk band.
4. The frozen lookback is about a quarter of the later half-life, 457.8077
   days, which the plan did not predict.
5. The fall is again several times the final P&L. The drawdown of 0.5033 ran
   from 2013-11-20 to 2016-01-19, while USD.CAD rose 39.5 percent and the rule
   was short on 458 of its 562 days.

Four groups of what it says are not pinned here.

1. Chan's words, each cited by its page in the 2013 print edition, as the
   earlier post cites them: the claim on 49, unlimited capital on 50 and the
   lookback with no parameters to optimize on 60.
2. Readings no test asserts: that a rule with no edge can end positive by
   chance, that the rule holds much the same position for weeks, that a
   p-value of 0.4343 means a random walk gives a ratio this far from 1 more
   than two times in five, that 488 of 1,101 days is fewer than half, and
   that 2013-11-20 to 2024-03-06 is more than ten years.
3. Facts Entry 51 states rather than pins: that the other vendor's minute
   bars reach back only to 2024-10-13 on the current subscription, and that
   an earlier run had read about 20 of the holdout's first days, through
   2012-04-26.
4. The figure's alt text, whose readings of the lines, such as "near 1.43 in
   2026" and "between about 1.21 and 1.45", are approximate by design.

Every other number traces to an assertion in
[tests/test_usdcad_holdout.py](tests/test_usdcad_holdout.py), to
[tests/test_usdcad_holdout_figures.py](tests/test_usdcad_holdout_figures.py)
for the figure's own numbers, or, for Chan's closes, to
[tests/test_usdcad_mean_reversion.py](tests/test_usdcad_mean_reversion.py).
Six had no pin before the post, and `TestWhatThePostMeasured` in
[tests/test_usdcad_holdout.py](tests/test_usdcad_holdout.py) pins them, all
measured after the run.

1. The closes on the drawdown's two dates, 1.0445 and 1.45699, a rise of 39.5
   percent.
2. The rule is short on 458 of the 562 days of the fall.
3. The P&L first passes its 2013 high again on 2024-03-06.
4. The largest position is a short of 5.4054 on 2020-03-19.
5. H sits 0.0014 below the random walks' mean.
6. The band is 0.4987 ± 0.0260, twice the walks' standard deviation.

Its one figure, `usdcad_holdout.png`, is drawn from the committed file by
[src/chan/usdcad_holdout_figures.py](src/chan/usdcad_holdout_figures.py),
which reads it through the same `read_holdout` as
`python -m chan.usdcad_holdout run`, refusals and scale-break guard included.
It draws two panels on one date axis.

1. The 115 warm-up closes and the 3,791 traded days' closes, with their
   115-day moving average and a dashed line on the first traded day.
2. The traded days' cumulative P&L, with the fall from 2013-11-20 to
   2016-01-19 shaded.

```bash
uv run python -m chan.usdcad_holdout_figures
```

[tests/test_usdcad_holdout_figures.py](tests/test_usdcad_holdout_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map, and
[tests/test_figures_match_code.py](tests/test_figures_match_code.py) compares
the committed file with a fresh draw.

## Where the book's numbers come from

[research/book-notes](research/book-notes/README.md) holds verbatim Kindle
highlights from Chan's *Quantitative Trading* and his *Algorithmic Trading*,
cited by location. Where a
published figure a replication chases is among them, that is where it traces
to. A highlight covers what somebody marked, so the notes carry two of the five
figures the design doc names.

Not every published figure is Chan's.
[research/papers](research/papers/README.md) holds whole documents, for a
source he cites rather than prints, and it exists because he cites one he
believed was not publicly available. A figure quoted from one of those traces
there instead.

The notes are quoted rather than written, so nothing edits them by hand and
four markdownlint rules stand down over that directory. The reasoning is in
its README.

## Running the checks

```bash
uv sync --dev
uv run ruff check
uv run ruff format --check
uv run pytest
```

`uv run pytest` runs the suite across one worker per core through
`pytest-xdist`, which `pyproject.toml` turns on in `addopts`. Add `-n 0` for a
serial run, which is the faster choice for a few tests, because every worker
starts whatever the selection. `--pdb` runs serially on its own.

A Claude Code session here also runs the archive pins, the 17 of Example
7.1, the 18 of the Example 7.2 rerun, the 35 of
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s
holdout in `tests/test_low_beta_holdout.py`, the 7 of its figure in
`tests/test_low_beta_holdout_figures.py`, the comparison of that figure with
its committed file in `tests/test_figures_match_code.py`, and the 46 of
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303)'s run in
`tests/test_khandani_lo_mid_caps.py`, because `.claude/settings.json` sets
`QT_ARCHIVE_RUN=1`. They run only where the owner's archive is configured.
Each test file that reads Example 7.1's run builds it in about six minutes,
and the rerun's pins take under a minute. The holdout's pins read 817 member
series' adjusted closes and volumes plus SPY's line. Its test file took 284
seconds serially with the pins and 149 seconds without them, measured once on
one machine at `6da2c3e9`, and no test holds either time. The pins of
[issue 303](https://github.com/l3a0/quantitative-trading/issues/303)'s run read
the `sp400` and `sp600` cross-sections beside Chan's two files.
Five runs of their test file on one 10-core machine, at `f5806ff7` and two
later commits that run the same code, took between 30 and 145 seconds serially
with the pins and between 6 and 24 seconds without them. The fastest ran at a
load average near 11, and the slowest with the pins at 60 to 109. No test
holds any of these times. `QT_ARCHIVE_RUN=0` skips the pins for one run.

`matplotlib` is a dev dependency rather than a runtime one. No replication
needs it. It is there so the committed figures can be redrawn and checked.
Pillow, which matplotlib installs, decodes them for that check.

`uv sync` fetches `ithildincore` from GitHub, so the first sync needs a
network. Every run after that reads the cache, and no replication reaches a
network at any point. Example 7.1 reads its bars from the owner's data archive,
and `chan.equity_seasonals --survivors` and `--point-in-time` read 603 and
1,487 daily files from it. `--point-in-time` then reads 817 more, from the
`sp500` cross-section. The archive is a folder on the owner's machine. If that
folder is synced from a cloud service, the first read of a file the service has
not kept on disk downloads it, which this repo does not measure.

markdownlint has no Python package, so it runs in CI rather than locally. The
prose checks it has no rule for run in the test suite instead, from
`tests/test_markdown_hygiene.py`. They catch things like a tilde that can close
a strikethrough pair, a heading quoted in prose that no longer exists, and an
issue number written without its link.

## License

The code is released under the [MIT License](LICENSE), so anyone may reuse it,
including commercially, as long as the copyright notice travels with it. The
committed vintages under `data/` come from elsewhere. Some are downloads from
their vendors, and most are lifted from Ernest Chan's own book-companion files
in a public mirror that carries no licence of its own.
The licence covers this repo's own work rather than granting any right those
sources did not.

## Where this came from

Seeded from [l3a0/repo-template](https://github.com/l3a0/repo-template), which
carries the agent instructions, CI, and GitHub-side policy shared with
[marketlake](https://github.com/l3a0/marketlake) and
[trading-strategies](https://github.com/l3a0/trading-strategies).

The GLD/GDX replication was first run in `trading-strategies`, and it came
here because that run already mapped the traps: the book's hedge ratio and its
test statistic come from different chapters, on different windows, under
different regression specifications, and the book's own number is
unreproducible from any modern download. What was checked here is whether the
vintage machinery makes those traps visible on its own, rather than through
comments, and each number the suite pins for it names its vintage, its window
and its specification.
