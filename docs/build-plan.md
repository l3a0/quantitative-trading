# Build plan — quantitative-trading

This doc carries the grouping, the build order, and each deliverable's test
surface. It does not carry scope. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and the entries
below are links rather than restatements. A plan entry that restates an issue
goes stale the moment work lands.

## How the work is grouped

The tracker carries one milestone per section below, with the same name, so a
filed issue has a milestone to take and the two surfaces say the same thing. The
tracker is where an issue's group is recorded. This doc is where the grouping is
reasoned about.

Experiments are grouped by the chapter of Chan's book they come from. A chapter
is a property of the source rather than a property of this plan, so the grouping
survives every change of priority. The chapter numbers come from the committed
highlights in
[research/book-notes/quantitative-trading.md](../research/book-notes/quantitative-trading.md),
read off the Kindle location where each figure is printed, not off a table of
contents nobody here holds.

Everything the experiments run on is machinery. Machinery belongs to no chapter,
so it is listed on its own below.

The price of grouping this way is that the grouping says nothing about order.
A grouping cut by the work itself at least implies a sequence, because the
earlier piece is the one the later piece needs. A chapter implies nothing, and
the book is lopsided enough that most of it lands in one chapter anyway. Order
comes from the dependencies at the end of this doc and from nowhere else, and
milestone order is not it.

## How work gets cut

A deliverable is cut down to the smallest piece that leaves the repo usable by
someone at the end of it. Not a layer, and not a subsystem. A piece that ends
with a component nobody can run is cut the wrong way.

What the milestones are named after has changed, and this has not, because it is
a rule about cutting work rather than about filing it.

## The order

The ranking rule in [CLAUDE.md](../CLAUDE.md) decides it: what is missing from
the shortest path to something usable goes first. Then ship it, use it, and let
what breaks set the order after that.

Three facts constrain the order today, and not one of them is a chapter.

1. The vintage recorder unblocks more than anything else on the tracker. Five
   of the six experiments this repo could otherwise reach cannot run until a
   series is recorded and committed, because the design doc rejects fetching at
   run time. The recorder is built. Those five still wait, because each needs a
   series recorded and each reads it through a reader
   [issue 2](https://github.com/l3a0/quantitative-trading/issues/2) has yet to
   build.
2. The coin-flip game is synthetic, so it never needed the recorder. It was the
   shortest path to the repo doing its job twice instead of once, and it has
   shipped.
3. Five experiments wait on data that is not free. They are not waiting on
   anybody's time, so they never compete for a place in the order.

Beyond those three constraints the order among the reachable experiments is not
set, and that is deliberate rather than an omission. The ranking rule says
evidence from real use decides it, and this repo has now run two, only one of
which was built here.

## The machinery

None of these is an experiment. They are what an experiment reads, and the
premise in [docs/design.md](design.md) is why they rank where they do: a result
computed before the vintage machinery exists is a result nobody can check,
including its author.

| Deliverable | What it leaves usable |
| --- | --- |
| [Record a downloaded series as a vintage, immutable once written](https://github.com/l3a0/quantitative-trading/issues/1) | Any series can be downloaded once, committed with its provenance, and read back later as exactly the bytes a result came from |
| [Verify a vintage before a run reads it, and tell absent apart from unreadable](https://github.com/l3a0/quantitative-trading/issues/2) | A run refuses a vintage it cannot trust, and says which one and in which state |
| [Back the split adjustment out of a vendor series that adjusts when asked not to](https://github.com/l3a0/quantitative-trading/issues/3) | A raw series is raw, including across a split the vendor silently applied |
| [Hold the committed vintages' bytes fixed across checkouts](https://github.com/l3a0/quantitative-trading/issues/41) | A recorded sha256 stays a fact on a clone that rewrites line endings |
| [Fail the suite when data/README.md and the vintage manifest disagree](https://github.com/l3a0/quantitative-trading/issues/43) | One surface owns each field a vintage's provenance states |

The first of those five is built. `src/chan/vintage.py` records a vintage and
refuses to overwrite one, `data/vintages.jsonl` holds the eight this repo
already carried, and `data/checksums.sha256` is now regenerated from that
manifest rather than kept by hand. The two new entries came out of decomposing
it, and each is separable in the way its own issue records.

Test surface for the five above: every rule is executable with no network,
because the recorder takes rows rather than fetching them.

The recorder's cases live in [tests/test_vintage.py](../tests/test_vintage.py)
and are not counted here, because a count in prose is a number no test holds and
`tests/test_markdown_hygiene.py` exists to make that point. What is worth
recording is where they came from. This entry planned one test. Issue 1's
decomposition settled twelve rules and asked for twelve tests, and mutating a
first implementation showed that four of those rules were held by none of them.
The rollback was the sharpest: without it one transient disk error retires a
vintage's path for good, and only a case written for it says so.

The other four entries keep their planned surface. For issues 2 and 3, three
tests drive the three verification failures and assert each message names which
vintage and which state, and one makes a vintage unreadable rather than absent,
which is the case a `Path.exists` check reports wrongly. Issues 41 and 43 each
carry their own, on their own issue.

## Open questions and deferred work

Neither of these leaves anything usable, which is why they are listed apart from
the machinery rather than inside it.

- [Decide whether the cross-surface sweep policy applies, once a second prose surface exists](https://github.com/l3a0/quantitative-trading/issues/6)
  is an owner decision rather than a session's work, and the issue carries the
  trigger that would make it live.
- [Close the pins the ported suite leaves open, found by mutating it](https://github.com/l3a0/quantitative-trading/issues/10)
  is deferred on purpose, on a count of zero runs through the paths the
  surviving mutants sit on.

## Chapter 3

One experiment, introduced at Kindle location 2099.

- [Reproduce the Khandani-Lo linear reversal, Example 3.7](https://github.com/l3a0/quantitative-trading/issues/17)

## Chapter 6

Two experiments, one of them reproduced.

- [Reproduce Kelly leverage on SPY, Example 6.2](https://github.com/l3a0/quantitative-trading/issues/14),
  worked at location 2858
- [Reproduce the coin-flip game, Example 6.1](https://github.com/l3a0/quantitative-trading/issues/13),
  worked at location 3186, landed as
  [src/chan/coin_flip_growth.py](../src/chan/coin_flip_growth.py) with its
  verdict in [docs/replication-log.md](replication-log.md)

Example 6.1 is a revised-edition label, unlike every other example number in
this doc. It comes from the book's own prose at location 3186, and the
first-edition code mirror carries no `example6_1` in any form.

## Chapter 7

Twelve of the book's fifteen experiments are here, between locations 3360 and
4684. It is the chapter Chan calls the special topics chapter at location 2735,
and twelve of fifteen is what makes the chapter grouping worth having: the
tracker's deliverables are not spread across the book.

Four are reproduced, and all four shipped under one issue. They are the GLD/GDX
cointegration test, the Ornstein-Uhlenbeck half-life, the Python-versus-MATLAB
disagreement, and the KO/PEP counter-example at Example 7.3.

- [Reproduce the GLD/GDX example against committed vintages, pinning each number to its own run](https://github.com/l3a0/quantitative-trading/issues/4)

Two more belong to those four without being experiments themselves. One writes
the verdict up, and one asks whether the chapter numbering here is even the
right one.

- [Write the replication log for both pairs, naming what matched and what did not](https://github.com/l3a0/quantitative-trading/issues/5),
  landed as [docs/replication-log.md](replication-log.md)
- [Check the GLD/GDX two-window framing against the edition it came from](https://github.com/l3a0/quantitative-trading/issues/12)

Issue 12 is why this section says which edition it means. The GLD/GDX
training-set run is called the Chapter 3 run throughout this repo, after the
first edition's `example3_6_1.m` and page 63. In the revised edition committed
here the figure it produces is printed at location 3718, which is Chapter 7,
and Chapter 3 defers the analysis rather than performing it. The grouping above
follows where the figure is printed, per the method stated at the top of this
doc, so it is the revised edition's grouping while the run's name is the first
edition's. Both are now declared rather than assumed, and
[docs/design.md](design.md) carries the argument.

Three more are reachable, and each needs a series this repo does not hold yet.

- [Reproduce risk parity against 60/40](https://github.com/l3a0/quantitative-trading/issues/15)
- [Reproduce the other stationary-spread candidates](https://github.com/l3a0/quantitative-trading/issues/16)
- [Reproduce the equity seasonals and their disappearance, Examples 7.6 and 7.7](https://github.com/l3a0/quantitative-trading/issues/18)

Five are blocked by data that is not free and is not derivable from anything
here. They are filed rather than dropped, because an unfiled experiment is one
nobody finds again and the data question gets rediscovered from scratch every
time someone reads the chapter. They stay in this chapter rather than in a
backlog of their own, because a backlog says somebody's time is what they wait
on.

- [Reproduce the commodity-futures seasonals](https://github.com/l3a0/quantitative-trading/issues/19)
- [Reproduce post-earnings announcement drift](https://github.com/l3a0/quantitative-trading/issues/20)
- [Reproduce the PCA statistical factor model](https://github.com/l3a0/quantitative-trading/issues/21)
- [Reproduce the Fama-French three factors and the momentum leg](https://github.com/l3a0/quantitative-trading/issues/22)
- [Reproduce Conditional Parameter Optimization, the revised edition's centrepiece](https://github.com/l3a0/quantitative-trading/issues/23)

They need continuous futures history, point-in-time earnings estimates,
fundamentals, a small-cap panel, or fifteen years of one-minute bars.

## Test surface for the experiments

Each experiment pins the figures the book prints, at the precision the book
prints them, naming its vintage and its window. An experiment that reads no
series names neither and says so, which is what the coin-flip game does. Its
computed table therefore drops the window column rather than filling it. Where the book states a ranking
or a verdict rather than a figure, that is what gets pinned, because inventing a
digit the source does not carry would be worse than pinning the claim the source
makes. Which figures those are is on each issue, not restated here.

Three pins were planned for GLD/GDX, each naming its window and its regression
specification, because the book prints two of these near each other and they
come from different runs: the through-origin slope on the full window, the slope
with an intercept on the training window, and the cointegration test statistic
on that training window. All three landed with the port, alongside the rest of
the suite the sibling repo had already built. The log entry in
[docs/replication-log.md](replication-log.md) quotes more than these three, and
traces to assertions across the whole suite rather than to this planned set.
Each of its rows names the assertion it uses.

One more test carries the premise, and half of it has landed. The half that
runs against committed files pins GDX's adjusted 2006 closes about fifteen
percent below its raw ones, and pins GLD as the control that does not move,
since GLD pays no distributions. The half that is still missing needs two
vintages of the same symbol taken at different dates, returning the same raw
series and a different adjusted one where a corporate action falls between
them. That is what turns the reason this repo commits vintages into something
executable rather than something asserted in the design doc. The recorder it
waited on is built, so what it needs now is two downloads of one symbol taken
on different days and a reader that finds them, which is
[issue 2](https://github.com/l3a0/quantitative-trading/issues/2).

## What comes after that

Nothing is planned past the experiments, on purpose. The ranking rule says
evidence from real use outranks any order set in advance, and the two
replications that read a series were copied in finished rather than run into
existence, so they have produced no evidence about what this repo's own
machinery makes hard. The coin-flip game was built here and reads nothing, so
it exercised the log format and none of the vintage machinery.

Two candidates are worth naming so they are not re-invented, and neither is
committed to.

1. A negative-results log, once a replication has failed in a way worth
   recording separately from its own entry.
2. A registered experiment, which is a different object from a replication and
   needs its hypothesis committed in writing before any number is seen.

A third candidate this section used to name, more replications chosen by what
the first one made easy or hard, is no longer a candidate. The catalogue is
filed, and the chapters above are where it lives.

## Dependencies

The first replication was planned to wait on the vintage machinery, and only on
the two deliverables it actually reads:
[issue 4](https://github.com/l3a0/quantitative-trading/issues/4) starting once
[issue 1](https://github.com/l3a0/quantitative-trading/issues/1) and
[issue 2](https://github.com/l3a0/quantitative-trading/issues/2) land.

That is not what happened. The sibling repo's finished replications were copied
here first, so the computation arrived before the machinery meant to feed it.
They read a committed CSV directly. `data/vintages.jsonl` now records each
file's vendor, symbol, price basis, span, date, row count and checksum, and
`data/README.md`'s table says the same in prose.

The dependency was real and is now a debt rather than a gate. Issue 4's
remaining half is the test that carries the premise, and that half still needs
issues 1 and 2, because it takes two vintages of one symbol and compares them.
The order that was worth protecting, no further replication landing before the
recorder, is no longer at risk. What replaces it is that each replication still
reads by filename, so every one added before issue 2 is another reader to
convert.

GLD/GDX went first because the sibling repo had already worked out where its
traps are, so the work here was checking that the vintage machinery makes those
traps visible rather than rediscovering them.

The split back-out sits with the machinery because it belongs to the vintage
story, not because the first replication needs it. Whether the GLD/GDX span
carries a split is not established here, and assuming it does not is exactly the
assumption that cost the sibling repo a false positive. Issue 4 checks rather
than assumes, and the scale comparison in
[issue 3](https://github.com/l3a0/quantitative-trading/issues/3) is what
answers it.
