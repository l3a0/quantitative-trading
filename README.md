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

Fifteen pins in [tests/test_pair_cointegration.py](tests/test_pair_cointegration.py)
freeze what they compute. Each names its window and its regression
specification, because the book prints two of those near each other and they
come from different runs.

The vintage machinery is not built yet, so a replication reads a committed CSV
directly rather than through a recorder that verifies it first.
[data/README.md](data/README.md) carries each file's vendor, symbol, span,
download date and checksum in the meantime.

The tracker is the source of truth for what each deliverable is, and the two
open slices are
[the vintage record](https://github.com/l3a0/quantitative-trading/milestone/1)
and [the first replication](https://github.com/l3a0/quantitative-trading/milestone/2).

## Running a replication

```bash
uv run python -m chan.pair_cointegration --ch3
```

Chan's Chapter 3 run, on the first 252 trading days. `--ch7` runs the full
Chapter 7 window, `--ko-pep` runs the counter-example, and `--selftest` checks
the arithmetic against synthetic series with known answers. Each report names
the window, the price basis, and the specification every number came from.

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
