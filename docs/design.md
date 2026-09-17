# Design — quantitative-trading

This doc carries the reasoning. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and this doc links
to an issue rather than restating it. [docs/build-plan.md](build-plan.md)
carries the slice order.

## Contents

- [Premise](#premise)
- [What this repo is for](#what-this-repo-is-for)
- [Vocabulary](#vocabulary)
- [Configuration](#configuration)
- [Considered and rejected](#considered-and-rejected)

## Premise

A replication is only worth something if someone can check it later, and the
thing that quietly stops them is the data.

Vendors restate price history. An adjusted close is not a property of a
trading day. It is a function of the day the series was downloaded, because
every later split and dividend rescales the whole series behind it. Run the
same code against the same symbol a year apart and the numbers move, with
nothing in the code or the output saying why. yfinance rescales adjusted
closes on every download, and it split-adjusts `Close` even when asked not to,
which is how the sibling `trading-strategies` repo produced a false positive
strong enough to look like a discovery before the cause was found.

So the one thing this repo must get right is the vintage. A series used to
produce a number is committed alongside that number, with the vendor, the
symbol, the span, and the download date recorded next to it. Everything else
here is regenerable. Rerun the analysis and it comes back. Lose the vintage
and the number becomes an assertion nobody can check, including its author.

That asymmetry is what the ranking rule in [CLAUDE.md](../CLAUDE.md) protects.
A path that can lose a vintage is never deferred. A path that recomputes
something from a vintage still on disk can wait for evidence that it matters.

## What this repo is for

Ernest Chan's books work through examples with published numbers. Reproducing
one tests whether the method survives contact with data a reader can actually
get, and the informative part is usually the gap rather than the match.

The sibling `trading-strategies` repo already ran one of these. Chan prints the
GLD/GDX hedge ratio as 1.6766, and that repo's reproduction against current
data computed 1.6379, while the cointegration test statistic did reproduce.
The hedge ratio moved because the two runs read different vintages of the same
series. That finding is what this repo is built around rather than a detail it
happens to contain.

Three things follow, and they set what the repo holds.

1. **A replication is a record, not a script.** It carries the vintage, the
   code, the number it got, the number the book printed, and a written verdict
   on the gap.
2. **A gap is a result.** A number that fails to reproduce says something about
   the method's sensitivity, and that is worth more than a match nobody
   examined. It gets written down with the same care as a match.
3. **A replication is exploratory until it is registered.** Reproducing a
   published figure spends the sample on a hypothesis someone else already
   chose, so it cannot confirm that an edge exists today. It can only say
   whether the published number reproduces.

## Vocabulary

Terms with exact definitions, reused on purpose. A term listed here is not a
candidate for a synonym.

| Term | Definition |
| --- | --- |
| **vintage** | One download of one series, identified by vendor, symbol, span, and download date, committed as a file with a checksum. |
| **replication** | An attempt to reproduce a specific published number from a named source, against a named vintage. |
| **published figure** | The number the source prints, quoted at the precision the source uses. |
| **gap** | The difference between a published figure and what the replication computed, stated at the precision both support. |
| **verdict** | The written conclusion of a replication: reproduced, reproduced with a gap, or did not reproduce, with the reason. |
| **exploratory** | A result produced by looking at the data. It kills an idea or justifies a closer look, and it is never a verdict about whether an edge exists. |
| **registered** | A result whose hypothesis was committed in writing before the number was seen. Only a registered result confirms anything. |

## Configuration

This repo is public. Tracked files never carry secrets or machine-specific
paths. Machine-local config lives under `~/.config/quantitative-trading/`.

The table below stays empty until a vendor that needs a key is actually used.
yfinance needs none, which is why the first slice runs with no configuration
at all.

| Setting | Secret | Lives in | Read by |
| --- | --- | --- | --- |
| none yet | n/a | n/a | n/a |

## Considered and rejected

Machinery that was considered and cut, pinned here with the reason, so a
decision stays decided. When something new is cut, add it here in the same
change that cuts it.

| Cut | Why |
| --- | --- |
| Downloading a series at run time | It is the failure this repo exists to prevent. A run that fetches its own data produces a number nobody can reproduce, because the next fetch returns a different series. A run reads a committed vintage or it does not run. |
| Recomputing a published number in prose | Prose states numbers and never derives them. A doc that recomputes a figure is a second implementation of the calculation, and the two drift without either looking wrong. The test is the single authority. |
| A price cache shared across replications | It reintroduces the vintage problem at one remove. Two replications reading one cache cannot say which download each result rests on, and refreshing the cache silently re-pins both. |
| Reporting only the replications that matched | A gap is a result. Reporting matches alone turns the log into an advertisement and destroys the thing it is useful for. |
