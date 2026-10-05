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
daily closes for the S&P 600 cross-section, stay in the owner's data archive
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

Twenty-two replications run here, fifteen from Chan's *Quantitative Trading*
and seven from his *Algorithmic Trading*. The first two were ported from the
sibling [trading-strategies](https://github.com/l3a0/trading-strategies) repo,
where they were first built. The other twenty were built here.

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
   than about whether the effect weakened.
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
builder who corrects his code fails a test rather than moving a pin. The blog
post about them is the exception, and what it says that nothing here asserts
is listed below.

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
each line field for field everywhere, and the files' hashes and their
agreement with the committed daily closes wherever an archive is configured.

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
transcription that takes returns before the cut fails a test.

[tests/test_price_spread.py](tests/test_price_spread.py) does it for Example
3.1. It pins each figure the three scripts print at their six decimals and
again at eight, and the book's rounding beside them. It pins the ratio's miss
and the swapped legs that land it, and both of location 1505's claims. It also
holds two choices no figure here can see, the padding of `lag` and the
divisor of the moving deviation, so a reader does not take these figures as
evidence about either.

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
variance ratio's trim to whole periods.

All twenty-two replications reach a verdict in
[docs/replication-log.md](docs/replication-log.md), row by row. Entry 5 there
carries the fixed-income finding, which has no published number to reach a
verdict against, Entry 6 the cross rate's verdict, Entry 7 the equity
seasonals', Entry 8 the Khandani-Lo reversal's, Entry 9 the survivorship
toy's, Entry 10 the reversal at the open's, Entry 11 the commodity
seasonals', Entry 12 post-earnings drift's, Entry 13 the PCA factor model's,
Entry 14 the market and momentum factors', Entry 15 the calendar spreads',
Entry 16 Conditional Parameter Optimization's, Entry 17 cross-sectional
momentum's, Entry 18 buy on gap's, Entry 19 the reversal on the 2012
panel's, Entry 20 the leverage examples', Entry 21 Example 3.1's and Entry 22
the stationarity tests on USD.CAD.

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
script of his reads, and his `VIX.csv` reports one, a real move on 2007-02-27. The
Khandani-Lo reversal's 2006 window spans one of the stock days, WYN's restart
on 2006-08-01, and prints a number anyway, because
it reads a panel rather than one series and its rule never weights a return
that is not finite. `chan.khandani_lo`'s docstring says why the guard is not
called there. Example 3.8's rule A, Chan's Python notebook, fills the gap and
reads it as a return of 121.5 on the closes and 127.65 on the opens, because
that is what his notebook computed, and the entry reports what the figures are
without it. Post-earnings drift calls the guard on each stock from its first
price, over its 2011 and 2012 window, and nothing there needs refusing. The
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
stand. Example 3.1 calls it on GLD and USO over the ETF file's whole span, and
neither carries a flagged day, so nothing is refused.
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
[data/README.md](data/README.md) says what was measured on each file. The
equity seasonals read the 2007 S&P 500 file and the later S&P 600 save, and
the Khandani-Lo reversal reads the
2007 S&P 500 file's closes for Example 3.7 and its opens for Example 3.8.
Post-earnings drift reads the 2012 S&P 500 file's opens and closes and its
flags, for
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20). Buy on gap
reads the same file's opens, highs, lows and closes, for
[issue 295](https://github.com/l3a0/quantitative-trading/issues/295), and the
reversal reads its opens and closes for *Algorithmic Trading*'s Examples 4.3
and 4.4, for
[issue 296](https://github.com/l3a0/quantitative-trading/issues/296). The PCA
factor model reads the earlier S&P 600 save's closes, for
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21).
Cross-sectional momentum reads the 2012 S&P 500 file's closes, for
[issue 297](https://github.com/l3a0/quantitative-trading/issues/297).
Example 3.1 reads GLD's and USO's closes from the ETF file, for
[issue 340](https://github.com/l3a0/quantitative-trading/issues/340), and is
the first run to read it. The lift for
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
that shape was decided. No replication reads them yet.

Seven more of Chan's files are committed as his 2018 Python port's zip shipped
them, under `data/pythoncodesanddata/`, for
[issue 301](https://github.com/l3a0/quantitative-trading/issues/301). They are
USD.CAD's one-minute bars, the daily closes of USD.CAD, AUD.USD and AUD.CAD,
the monthly AUD and CAD interest rates, and the AUD.CAD returns his Example 5.1
saved. `chan.series.load_minute_close` reads the minute file's 16:59 bar as
the daily close his Examples 2.1 to 2.5 read, and the stationarity tests on
USD.CAD read it. No replication reads the other six yet.

Four more of his MATLAB files hold his continuous futures series, four saves of one file named
for 2012-05-04, 2012-05-07, 2012-05-11 and 2012-05-17. Each symbol there is a
series rolled from contract to contract and shifted at each roll, priced on
its own calendar, and each is one vintage with all five fields, as a stock
is. His `VIX.csv` is committed beside them as one vintage under the vendor
`chan-csv`. Those five files hold 209 vintages, and
[issue 313](https://github.com/l3a0/quantitative-trading/issues/313) carries
their shape. No replication reads them yet.

IJR's holdings at every year-end from 2007 to 2025 are committed under
[research/filings](research/filings/README.md), read from the schedules
iShares Trust files with the SEC rather than from a vendor. A filing is never
restated, so each file is pinned by the filing's accession number rather than
kept as a vintage, and that directory's README says why.
`src/chan/fund_holdings.py` reads the filings, and
[issue 361](https://github.com/l3a0/quantitative-trading/issues/361) carries
their shape. No replication reads them yet.

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

Chan's equity seasonals are one command, and they take no option:

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
   and the suite reads it as an input rather than computing it. So is the
   description of Chan's rule as measuring the distance from a moving average.
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
   [its committed notes](research/book-notes/algorithmic-trading.md). The
   suite reads the 36 days as an input rather than computing it.
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

`matplotlib` is a dev dependency rather than a runtime one. No replication
needs it. It is there so the committed figures can be redrawn and checked.

`uv sync` fetches `ithildincore` from GitHub, so the first sync needs a
network. Every run after that reads the cache, and no replication reaches a
network at any point. Example 7.1 reads its bars from the owner's data archive,
which is a folder on the owner's machine. If that folder is synced from a cloud
service, the first read of a file the service has not kept on disk downloads
it, which this repo does not measure.

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
