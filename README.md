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
every number this repo quotes about either pair, and it is the only place any
of them is derived. Each GLD/GDX pin names its window and its regression
specification, because the book prints two of those near each other and they
come from different runs.

The vintage machinery is not built yet, so a replication reads a committed CSV
directly rather than through a recorder that verifies it first.
[data/README.md](data/README.md) carries each file's vendor, symbol, span,
download date and checksum in the meantime.

The tracker is the source of truth for what each deliverable is, and it carries
no milestones. Every issue stands alone, so
[docs/build-plan.md](docs/build-plan.md) is the only place the work is grouped
at all. It groups the experiments by the chapter of the book they come from,
and lists the machinery they run on separately.

The deliverables are the book's own worked examples. Fifteen are tracked: four
reproduced, six reachable, and five blocked by data that is not free. Twelve of
the fifteen sit in Chapter 7, which is where Chan works almost every numbered
example.

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

## Where the book's numbers come from

[research/book-notes](research/book-notes/README.md) holds verbatim Kindle
highlights from Chan's *Quantitative Trading*, cited by location. Where a
published figure a replication chases is among them, that is where it traces
to. A highlight covers what somebody marked, so the notes carry two of the five
figures this repo names.

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
