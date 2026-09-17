# Build plan — quantitative-trading

This doc carries the grouping, the build order, and each deliverable's test
surface. It does not carry scope. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and the entries
below are links rather than restatements. A plan entry that restates an issue
goes stale the moment work lands.

## How the work is grouped

The tracker carries no milestones. Every issue stands alone, so this doc is the
only surface that groups them at all.

Experiments are grouped by the chapter of Chan's book they come from. A chapter
is a property of the source rather than a property of this plan, so the grouping
survives every change of priority. The chapter numbers come from the committed
highlights in
[research/book-notes/quantitative-trading.md](../research/book-notes/quantitative-trading.md),
read off the Kindle location where each figure is printed, not off a table of
contents nobody here holds.

Everything the experiments run on is machinery. Machinery belongs to no chapter,
so it is listed on its own below.

The price of grouping this way is that the grouping says nothing about order. A
milestone at least implied a sequence. A chapter does not, and the book is
lopsided enough that most of it lands in one chapter anyway. Order comes from
the dependencies at the end of this doc and from nowhere else.

## The order

The ranking rule in [CLAUDE.md](../CLAUDE.md) decides it: what is missing from
the shortest path to something usable goes first. Then ship it, use it, and let
what breaks set the order after that.

Three facts set the order today, and not one of them is a chapter.

1. The vintage recorder unblocks more than anything else on the tracker. Five
   of the six experiments this repo could otherwise reach cannot run until a
   series is recorded and committed, because the design doc rejects fetching at
   run time.
2. The coin-flip game needs no data at all. It is synthetic, so it is the one
   experiment the unbuilt recorder does not block, and the shortest path to the
   repo doing its job twice instead of once.
3. Five experiments wait on data that is not free. They are not waiting on
   anybody's time, so they never compete for a place in the order.

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
| [Decide whether the cross-surface sweep policy applies](https://github.com/l3a0/quantitative-trading/issues/6) | An owner decision rather than a session's work |
| [Close the pins the ported suite leaves open, found by mutating it](https://github.com/l3a0/quantitative-trading/issues/10) | Deferred on purpose, on a count of zero runs |

Test surface for the vintage deliverables: every rule is executable with no
network, because the recorder takes rows rather than fetching them. One test
writes a synthetic series, reads back every manifest field, and confirms a
second write to the same path leaves the original file unchanged. Three more
drive the three verification failures and assert each message names which
vintage and which state. One makes a vintage unreadable rather than absent,
which is the case a `Path.exists` check reports wrongly.

## Chapter 3

One experiment, at Kindle location 2099.

- [Reproduce the Khandani-Lo linear reversal, Example 3.7](https://github.com/l3a0/quantitative-trading/issues/17)

What it pins is a collapse rather than an edge. A Sharpe of 4.47 in the
original paper falls to 0.25 on an S&P 500 large-cap universe and to −3.19
after five basis points of cost, so the costing model matters more than the
universe does.

## Chapter 6

Two experiments, at locations 2858 and 3186.

- [Reproduce the coin-flip game, Example 6.1](https://github.com/l3a0/quantitative-trading/issues/13)
- [Reproduce Kelly leverage on SPY, Example 6.2](https://github.com/l3a0/quantitative-trading/issues/14)

The coin-flip game is the only experiment in the book that needs no data, which
makes it the only one that can run before the recorder exists. Kelly on SPY
needs one free series and nothing else, so it is the cheapest experiment after
the recorder lands.

## Chapter 7

Twelve of the book's fifteen experiments are here, between locations 3360 and
4684. Chan calls it the special topics chapter at location 1093, and it is
where he works almost every numbered example. A reader who stops before it
never reaches them.

Four are reproduced already, all under one issue.

- [Reproduce the GLD/GDX example against committed vintages, pinning each number to its own run](https://github.com/l3a0/quantitative-trading/issues/4)
- [Write the GLD/GDX replication log entry, naming what matched and what did not](https://github.com/l3a0/quantitative-trading/issues/5)
- [Check the GLD/GDX two-window framing against the edition it came from](https://github.com/l3a0/quantitative-trading/issues/12)

Three more are reachable, and each needs a series this repo does not hold yet.

- [Reproduce risk parity against 60/40](https://github.com/l3a0/quantitative-trading/issues/15)
- [Reproduce the other stationary-spread candidates](https://github.com/l3a0/quantitative-trading/issues/16)
- [Reproduce the equity seasonals and their disappearance, Examples 7.6 and 7.7](https://github.com/l3a0/quantitative-trading/issues/18)

Five are blocked by data that is not free and is not derivable from anything
here. They are filed rather than dropped, because an unfiled experiment is one
nobody finds again and the data question gets rediscovered from scratch every
time someone reads the chapter.

- [Reproduce the commodity-futures seasonals](https://github.com/l3a0/quantitative-trading/issues/19)
- [Reproduce post-earnings announcement drift](https://github.com/l3a0/quantitative-trading/issues/20)
- [Reproduce the PCA statistical factor model](https://github.com/l3a0/quantitative-trading/issues/21)
- [Reproduce the Fama-French three factors and the momentum leg](https://github.com/l3a0/quantitative-trading/issues/22)
- [Reproduce Conditional Parameter Optimization, the revised edition's centrepiece](https://github.com/l3a0/quantitative-trading/issues/23)

They need continuous futures history, point-in-time earnings estimates,
fundamentals, a small-cap panel, or fifteen years of one-minute bars. Keeping
them in this chapter rather than in a backlog of their own says what is true:
they are part of the book, and no amount of building here will produce what
they read.

## Test surface for the experiments

Each experiment pins the figures the book prints, at the precision the book
prints them, naming its vintage and its window. Where the book states a ranking
or a verdict rather than a figure, that is what gets pinned, because inventing a
digit the source does not carry would be worse than pinning the claim the source
makes. Which figures those are is on each issue, not restated here.

Three pins were planned for GLD/GDX, each naming its window and its regression
specification, because the book prints two of these near each other and they
come from different runs: the through-origin slope on the Chapter 7 window, the
slope with an intercept on the Chapter 3 training window, and the cointegration
test statistic on that training window. All three landed with the port,
alongside the rest of the suite the sibling repo had already built.

One more test carries the premise, and it has not landed. Two vintages of the
same symbol, taken at different dates, return the same raw series and a
different adjusted one where a corporate action falls between them. That turns
the reason this repo commits vintages into something executable rather than
something asserted in the design doc. GDX is the symbol that shows it, since
GLD pays no distributions and its adjusted series does not drift.

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

The split back-out sits with the machinery because it belongs to the vintage
story, not because the first replication needs it. Whether the GLD/GDX span
carries a split is not established here, and assuming it does not is exactly the
assumption that cost the sibling repo a false positive. Issue 4 checks rather
than assumes, and the scale comparison in
[issue 3](https://github.com/l3a0/quantitative-trading/issues/3) is what
answers it.
