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

Four replications run here, all from Chan's *Quantitative Trading*. The first
two were ported from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, where
they were first built. The other two were built here.

1. The GLD/GDX cointegration example, Chapter 3 and Chapter 7.
2. The KO/PEP counter-example, Example 7.3, which is a pair that correlates in
   returns yet does not cointegrate in levels.
3. The coin-flip gamble, Example 6.1, where the expected return of a round is
   positive and the growth rate of capital is negative. It is the one
   replication here that reads no series at all, so it has no vintage to name.
4. The Kelly leverage on SPY, Example 6.2, which asks how much leverage
   maximises compounded growth and then whether that much would have survived
   the worst day the index has had. Every level Chan computed from a series
   lands high on a modern download and every claim behind those numbers still
   holds, and the entry is about that split.

[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py) freezes
every number this repo quotes about either pair, and it is the only place any of
them is derived. The write-up copied in from the sibling repo is the exception,
and what it says that nothing here asserts is listed below. Each GLD/GDX pin
names its window and its regression specification, because the book prints two
of those near each other and they come from different runs.

[tests/test_coin_flip_growth.py](tests/test_coin_flip_growth.py) does the same
for the coin flip, and separates the figures the book prints from what a seeded
run is entitled to claim, because no simulation this suite could afford
resolves Chan's seven decimals.

[tests/test_kelly_leverage.py](tests/test_kelly_leverage.py) does it for the
Kelly run, and separates the figures from the specification that produces them,
because three of the five choices behind Chan's numbers are invisible on the
page and each has a plausible wrong answer that does not look wrong.

All four reach a verdict in
[docs/replication-log.md](docs/replication-log.md), row by row.

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
module reads each committed series against itself day over day and reports any
day it changed scale rather than price, and a run whose window spans one stops
instead of printing a number. Two days of `ko_chan.csv` are reported today and
nothing computes across them, because the KO/PEP replication reads the
intersection with `pep_chan.csv` and that starts in 1977.
[tests/test_scale_breaks.py](tests/test_scale_breaks.py) is the authority for
the bound and for what the committed vintages carry.

The coin flip reaches none of that. It records no vintage and reads no series,
which is why it could ship before the recorder existed.

The estimators behind those numbers are not in this repo. Least squares, the
Augmented Dickey-Fuller statistic, the half-life and the MacKinnon critical
values live in [ithildincore](https://github.com/l3a0/ithildin-core), shared with
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

The Kelly run reads one series and takes a window:

```bash
uv run python -m chan.kelly_leverage
```

The default is Chan's own span, 1993-01-29 to 2007-12-28, held fixed so the
vintage is the only thing that differs from his. `--start` and `--end` move it,
and the report drops the published column on any other window rather than
printing a comparison against figures that came from his. `--dated` picks which
SPY download to read, which matters because a second one is coming, and
`--risk-free` moves the book's 4 percent constant.

It prints the moments against the book's, the worked example on this vintage's
leverage beside the book's own rounded 2.528, the Black Monday comparison with
Chan's constant kept apart from the worst day SPY actually holds, and the
time-scale check. A window whose mean excess return is negative makes Kelly
recommend a short, and that arrives as a line saying what it means rather than
as an exception, because nothing has failed.

Chan's own archived GLD/GDX files have no CLI mode on purpose. They exist to
show that even his saved data misses his printed hedge, which is a claim about
a number rather than a run someone would repeat, so
`TestGldGdxChanArchive` is where it lives.

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

## Where the book's numbers come from

[research/book-notes](research/book-notes/README.md) holds verbatim Kindle
highlights from Chan's *Quantitative Trading*, cited by location. Where a
published figure a replication chases is among them, that is where it traces
to. A highlight covers what somebody marked, so the notes carry two of the five
figures the design doc names.

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
needs it. It is there so the one committed figure can be redrawn and checked.

`uv sync` fetches `ithildincore` from GitHub, so the first sync needs a
network. Every run after that reads the cache, and no replication reaches a
network at any point.

markdownlint has no Python package, so it runs in CI rather than locally. The
prose checks it has no rule for run in the test suite: a tilde that can close a
strikethrough pair, a table delimiter row written tight, a heading quoted in
prose that no longer exists, and a link whose anchor no heading produces.

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
