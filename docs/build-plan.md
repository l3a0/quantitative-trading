# Build plan — quantitative-trading

This doc carries the slicing rule, the build order, and each slice's test
surface. It does not carry scope. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and the entries
below are links rather than restatements. A plan entry that restates an issue
goes stale the moment work lands.

## The slicing rule

A slice is the smallest set of deliverables that leaves the repo usable by
someone at the end of it. Not a layer, and not a subsystem. A slice that ends
with a component nobody can run is a slice cut the wrong way.

The order comes from the ranking rule in [CLAUDE.md](../CLAUDE.md): what is
missing from the shortest path to something usable goes first. Then ship it,
use it, and let what breaks set the order after that.

A slice carries one milestone on the tracker, with the same name, so a filed
issue has a milestone to take.

## Slices

### Slice 1, the vintage record

**What it leaves usable.** Any series this repo uses can be downloaded once,
committed with its provenance, and read back later as exactly the bytes a
result was computed from. Nothing here computes a result yet. It is first
because a result computed before the vintage machinery exists is a result
nobody can check, including its author, and that is the one loss
[docs/design.md](design.md) names as unrecoverable.

**Deliverables.**

- [Record a downloaded series as a vintage, immutable once written](https://github.com/l3a0/quantitative-trading/issues/1)
- [Verify a vintage before a run reads it, and tell absent apart from unreadable](https://github.com/l3a0/quantitative-trading/issues/2)
- [Back the split adjustment out of a vendor series that adjusts when asked not to](https://github.com/l3a0/quantitative-trading/issues/3)

**Test surface.** Every rule above is executable with no network, because the
recorder takes rows rather than fetching them. A test writes a synthetic
series, reads back every manifest field, and confirms a second write to the
same path leaves the original file unchanged. Three more drive the three
verification failures and assert each message names which vintage and which
state. One makes a vintage unreadable rather than absent, which is the case a
`Path.exists` check reports wrongly.

### Slice 2, the first replication

**What it leaves usable.** One published figure reproduced end to end against
a committed vintage, with a written verdict on the gap. At the end of this
slice the repo does the thing it exists to do, once, for one example.

GLD/GDX goes first because the sibling repo already worked out where its
traps are, so the work here is checking that the vintage machinery makes those
traps visible rather than rediscovering them.

**Deliverables.**

- [Reproduce the GLD/GDX cointegration example against a committed vintage, and pin what it computes](https://github.com/l3a0/quantitative-trading/issues/4)
- [Write the GLD/GDX replication log entry, naming what matched and what did not](https://github.com/l3a0/quantitative-trading/issues/5)
- [Decide whether the cross-surface sweep policy applies, once a second prose surface exists](https://github.com/l3a0/quantitative-trading/issues/6)

**Test surface.** Three pins were planned, each naming its window and its
regression specification, because the book prints two of these near each other
and they come from different runs: the through-origin slope on the Chapter 7
window, the slope with an intercept on the Chapter 3 window, and the
cointegration test statistic on the Chapter 3 window. All three landed with the
port, alongside the rest of the suite the sibling repo had already built.

One more test carries the premise, and it has not landed. Two vintages of the
same symbol, taken at different dates, return the same raw series and a
different adjusted one where a corporate action falls between them. That turns
the reason this repo commits vintages into something executable rather than
something asserted in the design doc. GDX is the symbol that shows it, since
GLD pays no distributions and its adjusted series does not drift.

Every number the log entry quotes traces to one of these assertions.

### Slice 3, more of Chan's experiments

**What it leaves usable.** A second replication, and then a third, so the repo
has done the thing it exists to do more than once. Six of the book's examples
sit here, and every one of them is reachable: the data is either synthetic or
free to fetch.

**Deliverables.** The
[milestone](https://github.com/l3a0/quantitative-trading/milestone/3) carries
them, and each issue is the source of truth for what its experiment is and
which of the book's figures it must match.

**Order inside the slice is not set**, and that is deliberate rather than an
omission. The ranking rule says evidence from real use decides it, and this
repo has run one replication. One thing is worth saying in advance: the
coin-flip game is the only experiment in the book that needs no data at all,
so it is the only one that can run before slice 1 exists.

**Test surface.** Each experiment pins the figures the book prints, at the
precision the book prints them, naming its vintage and its window. Where the
book states a ranking or a verdict rather than a figure, that is what gets
pinned, because inventing a digit the source does not carry would be worse than
pinning the claim the source makes. Which experiments those are is on their
issues, not restated here.

## Not a slice: the experiments the data blocks

Five more of the book's experiments are filed under
[a milestone that is not a slice](https://github.com/l3a0/quantitative-trading/milestone/4).
They need continuous futures history, point-in-time earnings estimates,
fundamentals, a small-cap panel, or fifteen years of one-minute bars. None of
that is free, and none of it is derivable from anything here.

They are filed rather than dropped because an unfiled experiment is one nobody
finds again, and the data question gets rediscovered from scratch every time
someone reads that chapter. They are kept out of the slices because putting
them in one would say they are waiting on somebody's time, and they are not.
The price of naming them is a milestone that will sit unfinished, possibly for
good.

## What comes after that

Nothing is planned past the experiments, on purpose. The ranking rule says
evidence from real use outranks any order set in advance, and the two
replications here were copied in finished rather than run into existence, so
they have produced no evidence about what this repo's own machinery makes hard.

Two candidates are worth naming so they are not re-invented, and neither is
committed to.

1. A negative-results log, once a replication has failed in a way worth
   recording separately from its own entry.
2. A registered experiment, which is a different object from a replication and
   needs its hypothesis committed in writing before any number is seen.

The third candidate this section used to name, more replications chosen by
what the first one made easy or hard, is no longer a candidate. It is slice 3,
and the catalogue is filed.

## Dependencies between slices

Slice 2 was planned to wait on slice 1, and only on the two vintage
deliverables it actually reads:
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

The split back-out sits in slice 1 because it belongs to the vintage story,
not because the first replication needs it. Whether the GLD/GDX span carries a
split is not established here, and assuming it does not is exactly the
assumption that cost the sibling repo a false positive. Issue 4 checks rather
than assumes, and the scale comparison in
[issue 3](https://github.com/l3a0/quantitative-trading/issues/3) is what
answers it.
