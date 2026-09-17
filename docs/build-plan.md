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
   run time.
2. The coin-flip game is synthetic, so the unbuilt recorder does not block it.
   It is the shortest path to the repo doing its job twice instead of once.
3. Five experiments wait on data that is not free. They are not waiting on
   anybody's time, so they never compete for a place in the order.

Beyond those three constraints the order among the reachable experiments is not
set, and that is deliberate rather than an omission. The ranking rule says
evidence from real use decides it, and this repo has run one replication.

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

Test surface for the three above: every rule is executable with no network,
because the recorder takes rows rather than fetching them. One test writes a
synthetic series, reads back every manifest field, and confirms a second write
to the same path leaves the original file unchanged. Three more drive the three
verification failures and assert each message names which vintage and which
state. One makes a vintage unreadable rather than absent, which is the case a
`Path.exists` check reports wrongly.

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

Two experiments.

- [Reproduce Kelly leverage on SPY, Example 6.2](https://github.com/l3a0/quantitative-trading/issues/14),
  worked at location 2858
- [Reproduce the coin-flip game, Example 6.1](https://github.com/l3a0/quantitative-trading/issues/13),
  worked at location 3186

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

- [Write the GLD/GDX replication log entry, naming what matched and what did not](https://github.com/l3a0/quantitative-trading/issues/5)
- [Check the GLD/GDX two-window framing against the edition it came from](https://github.com/l3a0/quantitative-trading/issues/12)

Issue 12 is why this section carries a caveat. The GLD/GDX training-set run is
called the Chapter 3 run throughout this repo, after the first edition's
`example3_6_1.m` and page 63. In the revised edition committed here, the figure
it produces is printed at location 3718, which is Chapter 7. The grouping above
follows where the figure is printed, per the method stated at the top of this
doc. Which edition the citations mean is the open question, not an assumption
this section is entitled to make.

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
prints them, naming its vintage and its window. Where the book states a ranking
or a verdict rather than a figure, that is what gets pinned, because inventing a
digit the source does not carry would be worse than pinning the claim the source
makes. Which figures those are is on each issue, not restated here.

Three pins were planned for GLD/GDX, each naming its window and its regression
specification, because the book prints two of these near each other and they
come from different runs: the through-origin slope on the full window, the slope
with an intercept on the training window, and the cointegration test statistic
on that training window. All three landed with the port, alongside the rest of
the suite the sibling repo had already built. Every number the log entry quotes
traces to one of these assertions.

One more test carries the premise, and half of it has landed. The half that
runs against committed files pins GDX's adjusted 2006 closes about fifteen
percent below its raw ones, and pins GLD as the control that does not move,
since GLD pays no distributions. The half that is still missing needs two
vintages of the same symbol taken at different dates, returning the same raw
series and a different adjusted one where a corporate action falls between
them. That is what turns the reason this repo commits vintages into something
executable rather than something asserted in the design doc, and it waits on
the recorder.

## What comes after that

Nothing is planned past the experiments, on purpose. The ranking rule says
evidence from real use outranks any order set in advance, and the replications
here were copied in finished rather than run into existence, so they have
produced no evidence about what this repo's own machinery makes hard.

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
They read a committed CSV directly, and `data/README.md` records each file's
vendor, symbol, span, download date and checksum by hand in the meantime.

The dependency was real and is now a debt rather than a gate. Issue 4's
remaining half is the test that carries the premise, and that half still needs
issues 1 and 2, because it takes two vintages of one symbol and compares them.
The order to protect from here is that no further replication lands before the
recorder does, since each one added now is another reader to convert later.

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
