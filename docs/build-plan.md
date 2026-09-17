# Build plan — PROJECT_NAME

This doc carries the slicing rule, the build order, and each slice's test
surface. It does not carry scope. An unbuilt deliverable's scope lives on its
issue, which is what [CLAUDE.md](../CLAUDE.md) makes authoritative, and the
entries below are links to those issues rather than restatements of them. A
plan entry that restates an issue goes stale the moment work lands.

## The slicing rule

A slice is the smallest set of deliverables that leaves the product usable by
someone at the end of it. Not a layer, and not a subsystem. A slice that ends
with a component nobody can run is a slice cut the wrong way.

Order the slices by what the ranking rule in CLAUDE.md decides: what is missing
from the shortest path to a product someone can use goes first. Then ship it,
use it, and let what breaks set the order after that.

A slice carries one milestone on the tracker, with the same name, so a filed
issue has a milestone to take.

## Slices

<!-- TEMPLATE: one section per slice. Each deliverable is a link to its issue.
     The test surface says what must be true before the slice is done, in
     terms of what a test executes rather than what the code looks like. -->

### Slice 1, TODO

**What it leaves usable.** TODO.

**Deliverables.**

- TODO, issue link

**Test surface.** TODO.

## Dependencies between slices

<!-- TEMPLATE: name only the dependencies that are real, meaning a slice that
     genuinely cannot start until another finishes. An invented dependency is
     how a plan quietly becomes a layered build. -->

TODO.
