# quantitative-trading

Experiments and replications from Ernest Chan's quantitative trading books,
each one pinned to the data vintage it ran on.

## Why the vintage comes first

Vendors restate price history. An adjusted close is not a property of a trading
day. It is a function of the day the series was downloaded, because every later
split and dividend rescales the whole series behind it. Run the same code
against the same symbol a year apart and the numbers move, with nothing in the
code or the output saying why.

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

Scaffolded. Nothing built yet. The tracker is the source of truth for what each
deliverable is, and the two open slices are
[the vintage record](https://github.com/l3a0/quantitative-trading/milestone/1)
and [the first replication](https://github.com/l3a0/quantitative-trading/milestone/2).

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

The GLD/GDX reproduction that this repo starts from was first run in
`trading-strategies`. It is the first replication here because it already has a
known gap, which makes it a test of the vintage machinery rather than a fresh
result.
