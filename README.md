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
computed from, and a result computed from none says so. Everything else is
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

Six replications run here, all from Chan's *Quantitative Trading*. The first
two were ported from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, where
they were first built. The other four were built here.

1. The GLD/GDX cointegration example, Chapter 3 and Chapter 7.
2. The KO/PEP counter-example, Example 7.3, which is a pair that correlates in
   returns yet does not cointegrate in levels.
3. The coin-flip gamble, Box 6.1, where the expected return of a round is
   positive and the growth rate of capital is negative. It is the one
   replication here that reads no series at all, so it has no vintage to name.
4. The Kelly leverage on SPY, Example 6.2, which asks how much leverage
   maximises compounded growth and then whether that much would have survived
   the worst day the index has had. Every level Chan computed from a series
   lands high on a modern download and every claim behind those numbers still
   holds, and the entry is about that split. On his own workbook every one of
   those levels reproduces at the precision he printed, and setting the two
   series day by day against each other puts the whole gap on about ten days
   on or beside SPY's quarterly ex-dividend dates.
5. Edward Qian's risk parity against the classic 60/40, reported at Kindle
   location 4684, on SPY and AGG. Both figures Chan prints land close and the
   claim behind them does not survive: 60/40 earns the higher Sharpe ratio at
   matched risk on the full span at Chan's 4 percent rate, resolved at a robust
   t of −2.17. It is the first entry here where the numbers reproduce and the
   claim does not, which is the reverse of the split the GLD/GDX and Kelly
   entries both found.
6. The CAD/AUD cross rate, which Chan calls "quite stationary" at Kindle
   location 3951 without working it. He names the rate itself, so the claim is
   what gets pinned and it carries a verdict against a criterion fixed before
   any statistic was read. On `CADAUD=X` over 2007-08-06 to 2026-09-30 the log
   of the rate rejects a unit root at 5%, at −3.2136 at one lag and −2.9946 at
   the first lag count whose residuals pass, against a bar of −2.86, so the
   claim reproduces. Its half-life is 141.6 trading days, and only 23 of 226
   one-year windows reject at 10%.

One more result runs here, and it is not a replication. The same passage names
other places a stationary spread should live without naming an instrument, so
there is no number of his to reproduce and no series of his to test. His
fixed-income candidate, bonds of one issuer at two maturities, is tested on TLT
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
does it for both stationary candidates. It pins both orientations of every
fixed-income number, because the test is not symmetric in its legs and Chan
names no dependent one. For the cross rate it pins the verdict rule as well as
the verdict, so a criterion edited after the fact fails a test.

All six replications reach a verdict in
[docs/replication-log.md](docs/replication-log.md), row by row. Entry 5 there
carries the fixed-income finding, which has no published number to reach a
verdict against, and Entry 6 the cross rate's verdict.

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
The columns lifted from Chan's MATLAB files, below, report 62 more, most of
them real moves in single stocks.
[tests/test_scale_breaks.py](tests/test_scale_breaks.py) is the authority for
the bound and for what the committed vintages carry.

One vintage, FRED's three-month Treasury-bill series, holds a rate rather than
a price, so the scale-break check skips it.
[src/chan/bill_rates.py](src/chan/bill_rates.py) reads it and averages it over
a window of months, and [tests/test_bill_rates.py](tests/test_bill_rates.py)
pins what it gives.

Two of Chan's own files are cross-sections rather than series: the S&P 500 as
it stood on 2007-11-23 and the S&P 600 as it stood on 2008-01-14. Each is
committed as one vintage per stock, 1,100 between them, each holding the
stock's close, high, low, open and volume, written by
`src/chan/mat_columns.py` under a directory per file.
`chan.series.load_panel` reads a whole file back as one date-by-stock frame
and checks every member's bytes on the way.
[Issue 88](https://github.com/l3a0/quantitative-trading/issues/88) is where that
shape was decided, and
[data/README.md](data/README.md) says what was measured on each file. No
replication reads them yet.
[Issue 17](https://github.com/l3a0/quantitative-trading/issues/17) and
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18) are the ones
that will.

The coin flip reaches none of that. It records no vintage and reads no series,
which is why it could ship before the recorder existed.

The estimators behind those numbers are not in this repo. Least squares, the
Augmented Dickey-Fuller statistic, the half-life, the MacKinnon critical values
and the Newey-West significance block live in
[ithildincore](https://github.com/l3a0/ithildin-core), shared with
the sibling repo because both had the same copy. The dependency is a direct URL
at an exact commit, `uv.lock` records it, and CI syncs with `--locked` so the
two cannot drift apart unnoticed. All three parts earn their place, and
[docs/design.md](docs/design.md) says which failure each one closes.
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
day a second SPY download arrives. Left out, it means the 2026 download, or no
date under `--chan`, which finds his adjusted workbook column. `--risk-free` moves
the book's 4 percent constant, and on Chan's window the report then says the
gap column measures the rate as well as anything else.

It prints the moments against the book's, the worked example on this vintage's
leverage beside the book's own rounded 2.528, the Black Monday comparison with
Chan's constant kept apart from the worst day SPY actually holds, and the
time-scale check. A window whose mean excess return is negative makes Kelly
recommend a short, and that arrives as a line saying what it means rather than
as an exception, because nothing has failed.

The risk parity run reads two series and takes no window, because its windows
were declared in advance:

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

Each window reports both legs' volatilities against the ratio Qian's 23-77
implies, the risk each leg contributes under 60/40 and under risk parity, the
leverage that matches 60/40's volatility, and the Sharpe ranking as a measured
difference with a robust t-statistic beside it. A window whose robust t cannot
resolve the ranking says so in a line rather than stopping the run, because a
sample that cannot settle a sign has not failed at anything. One of the two
sub-windows is in that position.

Chan's two stationary candidates share one command, and neither takes a
window:

```bash
uv run python -m chan.stationary_candidates
```

With no argument it runs both, and `fixed-income` or `cross-rate` runs one. The
fixed-income candidate prints the full-span test in both orientations, the
residual check at one lag beside the first lag count whose residuals pass, and
the rolling scan each way round. The cross rate prints the same three for the
log of `CADAUD=X` over its test window, then the verdict and the criterion it
was read against. There is no `--start` or `--end`, because a window option is
what would let a reader pick one that rejects, and each issue declared exactly
one window. `--dated` names which `CADAUD=X` download to read and defaults to
the one the suite pins.

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

Six of its figures are not pinned here, and they are worth knowing before
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
   figure, not a window this repo computes. The runs here give −3.45 and −3.09.
6. The piece dates the book to 2009 and names first-edition chapters. That is
   consistent rather than confused, and it now says so: every chapter, page and
   MATLAB filename this repo cites means the first edition unless stated. The
   revised edition puts both GLD/GDX printouts in one Chapter 7 example, which
   [docs/design.md](docs/design.md) works through.

Every other number in it traces to an assertion in
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
rest, in `TestTheStakeDecidesTheSign`. Four groups of its figures are not pinned here.

1. SPY's mean annual return of 11.23% and its unlevered growth rate of 9.8%,
   and the 1.43-percentage-point gap between them. All three are Chan's, at
   Kindle location 2869. [tests/test_kelly_leverage.py](tests/test_kelly_leverage.py)
   cites the first two as book figures and computes its own on a modern
   vintage.
2. A stock moving 1% up or down each minute loses about half a basis point a
   minute. That is Chan's, at location 2822, and no test computes it.
3. One head and one tail leave 0.999 of the capital, a tenth of a percent
   lost every two rounds, and the worked \$1,110, \$111 and \$999 of that pair. The
   two-round table of \$810.00, \$999.00 and \$1,232.10 is the same kind, and
   so is Chan's own \$2,000 account that wins \$220 or loses \$200. All of it
   is arithmetic on the two pinned multipliers, 1.11 and 0.90, and no test
   asserts it.
4. The \$606 median path is a loss of 39%. The test that pins \$606 says so in
   its docstring and does not assert the percentage. Lesson 2's 6% gap at ten
   rounds is the same kind, the pinned ratio of 1.06 written as a percentage.
   So are Lesson 4's multiple of 3.11, the pinned \$3,111 divided by \$1,000,
   and Lesson 6's "a fifth of the growth", the pinned standard error of
   1.05e-4 set against the growth of about 0.0005.

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
post, about Example 6.2's Kelly leverage on SPY. It draws six lessons from
Entry 3 of the replication log: the gap from Chan's figures, the specification,
rebalancing at a constant leverage, the stress test's threshold and price
series, the window, and the return frequency. A further lesson, Lesson 6, on
overbetting past the Kelly leverage, comes from the growth formula. Two
groups of its figures are not pinned here.

1. Chan's printed figures: the 11.23% mean, 16.91% standard deviation,
   7.231% excess return, 0.4275 Sharpe ratio, 2.528 leverage, 13.14% and 9.8%
   growth rates and 1.26 half-Kelly, the 4% risk-free rate, the \$100,000 of
   equity and 10% fall of the worked example, and the 20.47% Black Monday loss
   and 20% tolerance of the stress test. The code carries them as cited
   constants and computes none of them.
2. Arithmetic that no test asserts: the 99% a 10% loss and a 10% gain leave,
   with their variance of 0.01, half of it 0.5% a period and 1% over two, the
   1.43% volatility drag, the 6.98% half-Kelly adds above the 4% rate, the
   9.30% that `S²/2` adds, the 0.60 margin above the 1.954 threshold, the 7.72
   spread between the bear and bull windows, the variance of 0.0286 and the
   factor of about 35 it multiplies an error in the mean by, the worst SPY day
   being about a third of Black Monday, and twice Kelly carrying about five
   times SPY's swings. The 43 to 47% that monthly sampling adds is held by a
   test only as a band of 42 to 48%.

Every other number in the post traces to an assertion in
[tests/test_kelly_leverage.py](tests/test_kelly_leverage.py), apart from the
numbers read off the growth formula, which trace to
[tests/test_kelly_figures.py](tests/test_kelly_figures.py). Those include the
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
Sharpe ratio at the 1.74% bill average and at 4%. What its seven figures draw
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

## Where the book's numbers come from

[research/book-notes](research/book-notes/README.md) holds verbatim Kindle
highlights from Chan's *Quantitative Trading*, cited by location. Where a
published figure a replication chases is among them, that is where it traces
to. A highlight covers what somebody marked, so the notes carry two of the five
figures the design doc names.

Not every published figure is Chan's.
[research/papers](research/papers/README.md) holds whole documents, for a
source he cites rather than prints, and it exists because he cites one he
believed was not publicly available. A figure quoted from one of those traces
there instead.

The notes are quoted rather than written, so nothing edits them by hand and
three markdownlint rules stand down over that directory. The reasoning is in
its README.

## Running the checks

```bash
uv sync --dev
uv run ruff check
uv run ruff format --check
uv run pytest
```

`matplotlib` is a dev dependency rather than a runtime one. No replication
needs it. It is there so the committed figures can be redrawn and checked.

`uv sync` fetches `ithildincore` from GitHub, so the first sync needs a
network. Every run after that reads the cache, and no replication reaches a
network at any point.

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
unreproducible from any modern download. What is left to check is whether the
vintage machinery makes those traps visible on its own, rather than through the
comments that currently point them out.
