# quantitative-trading

Experiments and replications from Ernest Chan's quantitative trading books,
each one pinned to the data vintage it ran on.

## Why the vintage comes first

Vendors restate price history. An adjusted close is not a property of a trading
day. It is a function of the day the series was downloaded, because the series
is pinned to the latest price and every later split or dividend rescales the
history behind it. Run the same code against a symbol that has paid a dividend
since the last download and the numbers move, with nothing in the code or the
output saying why. A symbol that has paid nothing comes back unchanged, which
is what makes the problem easy to miss.

So a result here is committed next to the exact series it was computed from.
Everything else is regenerable. Rerun the analysis and it comes back. Lose the
vintage and the number becomes an assertion nobody can check, including its
author.

[docs/design.md](docs/design.md) carries the reasoning.
[docs/build-plan.md](docs/build-plan.md) carries the order.

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

A replication is exploratory by construction. Reproducing a published figure
spends the sample on a hypothesis someone else chose, so it can say whether the
number reproduces and nothing more.

## Status

Two replications run here, both from Chan's *Quantitative Trading* and both
ported from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, where
they were first built.

1. The GLD/GDX cointegration example, Chapter 3 and Chapter 7.
2. The KO/PEP counter-example, Example 7.3, which is a pair that correlates in
   returns yet does not cointegrate in levels.

[tests/test_pair_cointegration.py](tests/test_pair_cointegration.py) freezes
every number this repo quotes about either pair, and it is the only place any of
them is derived. The write-up copied in from the sibling repo is the exception,
and what it says that nothing here asserts is listed below. Each GLD/GDX pin
names its window and its regression specification, because the book prints two
of those near each other and they come from different runs.

Both reach a verdict in
[docs/replication-log.md](docs/replication-log.md), row by row.

The vintage machinery is not built yet, so a replication reads a committed CSV
directly rather than through a recorder that verifies it first.
[data/README.md](data/README.md) carries each file's vendor, symbol, span,
download date and checksum in the meantime.

The estimators behind those numbers are not in this repo. Least squares, the
Augmented Dickey-Fuller statistic, the half-life and the MacKinnon critical
values live in [quantcore](https://github.com/l3a0/quant-core), shared with
the sibling repo because both had the same copy. The dependency names an exact
tag and `uv.lock` records the commit it resolved to, so the code behind a
pinned number is fixed the way the data behind it is fixed.
[docs/design.md](docs/design.md) carries why that pin is not optional.

The tracker is the source of truth for what each deliverable is, and it carries
one milestone per section of [docs/build-plan.md](docs/build-plan.md), with the
same name. The experiments are grouped by the chapter of the book they come
from, and the machinery they run on is grouped separately, because a vintage
recorder belongs to no chapter.

The deliverables are the book's own worked examples. Fifteen are tracked: four
reproduced, six reachable, and five blocked by data that is not free. Twelve of
the fifteen sit in Chapter 7, the chapter Chan calls the special topics chapter
at Kindle location 2735.

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
disagree on one published figure, which
[issue 27](https://github.com/l3a0/quantitative-trading/issues/27) carries.

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
6. The piece dates the book to 2009 and cites the revised edition, which is the
   edition question on
   [issue 12](https://github.com/l3a0/quantitative-trading/issues/12).

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

`uv sync` fetches `quantcore` from GitHub at the tag `pyproject.toml` pins, so
the first sync needs a network. Every run after that reads the cache, and no
replication reaches a network at any point.

markdownlint has no Python package, so it runs in CI rather than locally. The
two prose sweeps it cannot do run in the test suite.

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
