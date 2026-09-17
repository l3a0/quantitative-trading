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
something asserted in the design doc. GDX is the symbol that shows it, since GLD pays no distributions
and its adjusted series does not drift.

Every number the log entry quotes traces to one of these assertions.

## What comes after

Nothing is planned past slice 2, on purpose. The ranking rule says evidence
from real use outranks any order set in advance, and the two replications here
were copied in finished rather than run into existence, so they have produced
no evidence about what this repo's own machinery makes hard. Whatever slice 2
makes awkward is what slice 3 fixes.

Three candidates are worth naming so they are not re-invented, and none of
them is committed to.

1. More replications, chosen by what the first one made easy or hard.
2. A negative-results log, once a replication has failed in a way worth
   recording separately from its own entry.
3. A registered experiment, which is a different object from a replication and
   needs its hypothesis committed in writing before any number is seen.

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
