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
daily closes for the S&P 600 and S&P 500 cross-sections, stay in the owner's data archive
and only their hashes are committed, as `docs/design.md`'s premise records. Everything else is
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

Thirty-seven replications run here, fifteen from Chan's *Quantitative Trading*
and twenty-two from his *Algorithmic Trading*. The first two were ported from the
sibling [trading-strategies](https://github.com/l3a0/trading-strategies) repo,
where they were first built. The other thirty-five were built here.

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
   series 0.0879 with a p of 0.001. The two disagree, so the free sources
   cannot decide whether the January effect survived the book, and
   [issue 407](https://github.com/l3a0/quantitative-trading/issues/407) asks
   whether to buy prices for the members that threaten a tenth. Example 7.7
   then ran under the revised MATLAB's rules on the members IVV held each
   month from January 2009 to September 2026, carried forward from its
   quarterly schedules. That run is registered too. Its 213 months average
   −0.0001 a month before costs, with a one-sided p of 0.539, so no return is
   detectable above about 4.2% a year. The verdict reads only the 98,321 of
   107,115 member-months with a checked price, and it leaves out costs and
   the return a failing stock takes when it leaves.
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
    0.4732 against the book's 0.49, and Chan's own Python port gives 0.4758,
    though both agree H is below a half. Example 2.5's P&L ends positive at
    0.1141 after a fall of 0.6425, which is the claim the issue declared
    before any P&L was computed. Its lookback comes from the closes it trades,
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
    1.044327. Every figure is exploratory.
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
    out after the run, so its match is a search. Every figure is exploratory.
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
    the shuffled positions to the observed ones. Three rows added after a
    scratch run saw results point at TU's drift rather than its kurtosis: a
    normal draw gives 1,165 of 10,000, and the type IV draws with the mean
    set to zero give 19. Every figure is exploratory.

One more result runs here, and it is not a replication. The same passage names
bonds of one issuer as a place a stationary spread should live without naming
an instrument, so there is no number of his to reproduce and no series of his
to test. That fixed-income candidate, bonds of one issuer at two maturities, is tested on TLT
against IEF, and the result is a finding rather than a verdict. Over
2002-07-30 to 2026-10-01 neither orientation rejects the no-cointegration
null, at −2.3887 and −2.3168 against a 10% bar of −3.04, and the residual check
moves both further from rejecting rather than closer. It is exploratory, and it
says nothing about bonds beyond these two funds.

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
over the gross cap.

[tests/test_usdcad_mean_reversion.py](tests/test_usdcad_mean_reversion.py)
does it for the stationarity tests on USD.CAD. It pins each figure the script
prints at the precision that is real and at the script's, H as a miss against
the book's 0.49, and the ADF statistic `adfuller` gives beside jplv7's, so a
port that reaches for the ADF this repo already held fails a test. It also
recomputes Example 2.5's daily P&L with plain pandas.
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
the Python port does, breaks it too.

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
and a gap in the spot still counted as elapsed days.

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
each move a figure, and the scale-break guard on each span of each save.

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
window's end that return exactly 0. It also runs the script's window on CL
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

[tests/test_vx_calendar_spread.py](tests/test_vx_calendar_spread.py) does it
for the VX calendar spread. It pins the specification and the four rows
declared beside it at six decimals, the book's three figures against the
specification at the precision Chan printed, and the two measurements taken
after the run, each marked as such. It also holds why the specification pairs
contracts a month apart, the 64 of VX's 71 pairs and 68 of CL's 77 held under
`holddays=0`, the 43 pairs B3 holds from 2008-10-27, and why its last pair
ends on the book's end date. On synthetic frames it holds the two signals'
rules: a row whose nearest two contracts skip one, the held pair across a
roll, and the fill across days nothing is held.

[tests/test_roll_momentum.py](tests/test_roll_momentum.py) does it for TU's
momentum on the roll return. It pins the three figures at six decimals and
at the book's precision, Example 6.1's rule on the same rebuilt series and
each claim's margin, the rebuild against the 2012-05-11 save, both rules on
that save's own close, and the month-unit and fifth-contract readings. It
also holds the declared rule and the roll's off-by-one on synthetic strips,
the March 2012 roll, and the scale-break guard on every member's own rows.

[tests/test_tu_hypothesis_tests.py](tests/test_tu_hypothesis_tests.py) does it
for Example 1.1's three hypothesis tests on TU. It pins every count exactly at
its declared seed and every proportion at six decimals, the landing bands, the
Gaussian statistic, and the three rows added after the scratch run. It holds
the Pearson type IV sampler's parameters against their closed-form moments and
its tails against quadrature, and holds the two-dimensional form equal to
`chan.tu_momentum`'s functions draw by draw and unchanged by the batch size. It
also holds that the third test as written leaves every simulated return at
zero.

All thirty-seven replications reach a verdict in
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
rule's on TU, and Entry 37 Example 1.1's hypothesis tests.

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
without it. The
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
`chan.equity_seasonals` runs Example 7.6 on the members of
IJR's 2025-12-31 filing as a replication, and on the members of every
year-end from 2008 to 2025 through that members file as a registered
experiment.

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
departing names fell, which it marks as descriptive only. The two options
cannot be given together.

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
`data/archive_vintages.jsonl` under a cross-section name. It is the one command
here that needs the owner's key, read from the environment of the run:

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

Redrawing it produces the same picture and a different file, because a PNG
carries the matplotlib version that rendered it.
[tests/test_regime_figure.py](tests/test_regime_figure.py) therefore holds the
data behind the picture rather than its bytes, and asserts that the figure
plots the same scan `TestRollingRegime` computes.

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
Januaries before. The post draws four lessons from Entry 7 of the replication
log.

1. Every figure the committed files reach reproduces, and only under each
   script's own rules.
2. One strategy gives four answers across four printouts, and the first
   edition's is in different units from the other three.
3. Reproducing a strategy published as dead checks its printed figures and not
   its death. The split at 2002 is exploratory with no verdict, and Chan's
   claim that the most recent five years do worse holds on his own file under
   a criterion written before the check ran.
4. A file of survivors is the first thing the result cannot get past.

Three groups of its figures are not pinned here.

1. Chan's words, each cited by its page in the revised edition. "More than 13
   percent" and "has disappeared since then" are on p. 179, "has weakened or
   even disappeared in recent years" on p. 175, and "worked wonderfully" on
   p. 175 too, beside the tax-loss reason Chan gives for the January effect. The
   reader whose backtest of Example 7.6 failed is on p. 13. "The most
   recent five years instead of the entire data period", and Chan's
   statement that those years do even worse, are on p. 180.
2. Counts, arithmetic and facts no test asserts. Nothing counts the seventeen
   reproduced figures, nine for Example 7.6 and eight for Example 7.7, or the
   first edition's 95 months with a return and 83 with a position, which are
   its 96 months less the one with no return and less the twelve with no
   position. Nothing states that a half's slope in the figure is its annual
   return over 12, that the revised Python copy's five printed figures match the book,
   that the mirror lacks `IJR_20080131.mat`, or that the repost it comes from
   carries the earlier save byte for byte as the mirror has it, which
   [data/README.md](data/README.md) records by its sha256.
3. Its references. The four citations, including the publication details the
   post gives for Heston and Sadka and for Singal, are cited rather than
   computed.

Every other number in the post traces to an assertion in
[tests/test_equity_seasonals.py](tests/test_equity_seasonals.py), or to
[tests/test_equity_seasonals_figures.py](tests/test_equity_seasonals_figures.py)
for the figure's own labels. One group had no pin before it, and
`TestTheYearsInsideTheSplit` now pins it: the calendar-year sums of the
revised Python's months, 0.2227 for 2002 and −0.1319 for 2006, that those
two years differ by more than the two halves of the split do, and that the
running sum peaks in January 2006.

Its one figure is drawn from the committed S&P 500 file by
[src/chan/equity_seasonals_figures.py](src/chan/equity_seasonals_figures.py).
It draws the 83 months the revised Python keeps as a running sum, split at
2002 and labelled with each half's month count, annual return and Sharpe
ratio, for Lesson 3.

```bash
uv run python -m chan.equity_seasonals_figures
```

[tests/test_equity_seasonals_figures.py](tests/test_equity_seasonals_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

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

Four groups of its figures are not pinned here.

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
2. A fact outside the committed data. Apple released earnings five times
   inside the window. Only the three flagged days are pinned.
3. The book's Figure 7.2, which the post's figure redraws from `pead.m`'s
   `plot(cumret)` and which nothing compares with the book's own.
4. Its references, cited rather than computed.

Every other number in the post traces to an assertion in
[tests/test_pead.py](tests/test_pead.py), to
[tests/test_series.py](tests/test_series.py) for the 1,885 flags, Apple's
three flagged days and the 29 stocks with none, to
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
factors. Example 7.4 rests on that claim, so the post draws six lessons from
Entries 13 and 14 of the replication log together. Every result in it is
exploratory.

1. Three of the four printouts reproduce, and the fourth, the R, prints
   another program's figures.
2. Chan's round-off is a second strategy, because the revised Python's
   intercept cancels its factors and leaves single-stock momentum.
3. The momentum the strategy assumes held for the market factor and not for
   the momentum factor, each verdict standing on its own.
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
[tests/test_pca_factor.py](tests/test_pca_factor.py) or
[tests/test_momentum_factor.py](tests/test_momentum_factor.py), to
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
   the mirror shorted on 2008-10-13, is Morgan Stanley's ticker.
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
drawing runs on every clone against a synthetic run of 400 cells, and only its
check that the three labels are the cells Entry 16 names needs the archive. A
public clone can check what the code draws but cannot redraw the committed
figure.

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
3. H misses 0.49 under both implementations Chan's code uses and with a longer
   window, and the variance ratio test cannot reject a random walk either.
4. The trade ends positive after a fall more than five times its final P&L,
   short on every day of that fall and at its largest short inside it.
5. The lookback came from the closes the rule traded, so the result checks the
   arithmetic and not whether the trade would pay.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   Most prices as random walks is at 1036, the variance growing like τ²ᴴ at
   1063, the critical value and its table at 1076, the reading of the
   statistic and of λ at 1114, H's meaning and the 0.49 at 1119, the variance
   ratio test as H's significance test at 1149, the half-life and the warning
   about round trips at 1164, the case for trading below 90 percent certainty
   at 1193, the linear rule at 1205, the claim and its three cautions at 1225,
   the case for testing before a backtest at 1237, the 23-day half-life at 1347
   and the lookback with no parameters to optimize at 1350. The book's figures
   are pinned, and its words are not.
2. Facts about the code rather than the data: that jplv7 trims one more row
   when it lines up the lagged close, that `genhurst` averages over windows of
   5 to 19 days, that every copy of it a search found is dated 2013-01-30 and
   runs one algorithm, that Chan's 2018 Python port fits the log variance of
   τ-day changes on log τ, and that the port and `ithildincore` both run
   `adfuller`. [src/chan/stationarity_tests.py](src/chan/stationarity_tests.py)
   and [src/chan/usdcad_mean_reversion.py](src/chan/usdcad_mean_reversion.py)
   record each in their docstrings.
3. Readings no test asserts: that each day keeps roughly 99.41 percent of its
   distance from the mean, that a p-value of 0.367 means a random walk gives a
   ratio this far from 1 more than a third of the time, that none of the four
   statistics depends on the units of the closes, that a random walk has no
   half-life, and that a fall in a commodity currency fits the autumn of 2008,
   which the post says nothing here tests.
4. The figure's alt text, whose readings of the lines, such as "near 1.05" and
   "about 0.92 in late 2007", are approximate by design. The book's own chart
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
for the figure's own numbers. Eight had no pin before it, and
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

Its one figure is drawn from the committed file by
[src/chan/usdcad_mean_reversion_figures.py](src/chan/usdcad_mean_reversion_figures.py),
which reads it through the same `read_sources` and `stationarity_tests` as
`python -m chan.usdcad_mean_reversion`, scale-break guard included. It draws
two panels on one date axis, for Lesson 4.

1. The 1,216 closes with their 115-day moving average.
2. The cumulative P&L, the script's plot, with the fall from 2008-07-22 to
   2008-10-27 shaded.

```bash
uv run python -m chan.usdcad_mean_reversion_figures
```

[tests/test_usdcad_mean_reversion_figures.py](tests/test_usdcad_mean_reversion_figures.py)
holds what it draws rather than its bytes, for the reason given above for the
regime map.

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

[blog/tu-momentum-lessons.md](blog/tu-momentum-lessons.md) is a twenty-sixth
post, about Example 6.1 of Chan's *Algorithmic Trading*, which correlates TU's
past and future returns for 49 pairs of lookback and hold and then trades the
250-day lookback with a 25-day hold. Chan reports a correlation of 0.27 with a
p-value of 0.02, an H of 0.44, a Sharpe ratio of 1, an APR of 1.7 percent and
a maximum drawdown of 2.5 percent. The post explains the strategy for the
other TU posts to link, and draws three lessons from Entry 33 of the
replication log.

1. The book's figures come from the full window, which the script leaves
   commented out, while the line it runs from 2009 lands none of them.
2. H misses 0.44 on Chan's own file, and the `maxT` that lands it on TU moves
   USD.CAD further from its 0.49, so no figure of Chan's vouches for the
   Python copy of `genhurst`.
3. The momentum is thin: the traded cell rests on 69 days, is one of 49 that
   share the same closes, and the variance ratio test cannot tell TU from a
   random walk.

Five groups of what it says are not pinned here.

1. Chan's words, each cited by its Kindle location in *Algorithmic Trading*
   through [its committed notes](research/book-notes/algorithmic-trading.md).
   Momentum as a correlation of past and future returns is at 2600, the
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
   it, that 2008 was the year of the financial crisis, that a rule mostly long
   on a rising price earns part of the rise, and that leverage would multiply
   the drawdowns along with the return.
4. Ratios and roundings the post takes between pinned figures in words: more
   than half of the gain in by 2009-01-02, 2008 earning about four-fifths as
   much as the other years combined, four trading days between the two saves'
   first days, 2.484746 percent rounding to 2.5, and what a figure prints as
   at the book's precision, such as 0.43, 0.45 and 0.29. The figure's alt text
   reads TU's closes approximately too, as drifting down and then climbing.
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

A Claude Code session here also runs the 16 archive pins of Example 7.1,
because `.claude/settings.json` sets `QT_ARCHIVE_RUN=1`. They run only where
the owner's archive is configured, and each test file that reads the run builds
it in about six minutes. `QT_ARCHIVE_RUN=0` skips them for one run.

`matplotlib` is a dev dependency rather than a runtime one. No replication
needs it. It is there so the committed figures can be redrawn and checked.

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
