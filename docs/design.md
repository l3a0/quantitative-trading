# Design — quantitative-trading

This doc carries the reasoning. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and this doc links
to an issue rather than restating it. [docs/build-plan.md](build-plan.md)
carries the build order.

## Contents

- [Premise](#premise)
- [What this repo is for](#what-this-repo-is-for)
  - [Three more results came across with it](#three-more-results-came-across-with-it)
  - [The estimators live outside this repo](#the-estimators-live-outside-this-repo)
- [Vocabulary](#vocabulary)
- [Configuration](#configuration)
- [Considered and rejected](#considered-and-rejected)

## Premise

A replication is only worth something if someone can check it later, and the
thing that quietly stops them is the data.

Vendors restate price history. An adjusted close is not a property of a
trading day. It is a function of the day the series was downloaded, because an
adjusted series is pinned to the latest price and every later split or
dividend rescales the whole history behind it.

The effect is per corporate action, not per download. A symbol that has paid
nothing since the last download returns the same series. GDX has paid
dividends for nineteen years since 2007, so its adjusted 2006 price today sits
roughly 15% below the number Chan saw. GLD pays no distributions, so its
adjusted series does not drift at all. Which symbol you are looking at decides
whether the problem shows up, which is why it is easy to miss.

A second failure is cruder and not about adjustment at all. yfinance
split-adjusts `Close` even when called with `auto_adjust=False`. That put
XLE's pre-split prices at half the scale of its strikes in the sibling
`trading-strategies` repo, and the delta hedge built on them reported a
fabricated result strong enough to read as a discovery before the cause was
found.

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
get. Some of those published figures are recorded in
[research/book-notes](../research/book-notes/README.md), quoted verbatim and
cited by Kindle location, so where a target number is there it traces to the
sentence that printed it rather than to someone's memory of it. A highlight
covers what somebody marked, so the notes carry 1.6766 and 0.4849 and not the
other three figures this doc names. The notes are also the 2021 revised
edition of *Quantitative Trading*, while the chapter and page citations below
are first-edition.

A gap between the published number and the reproduction is as informative as a
match, and often more so, because it names something the method depends on
that the text did not.

The sibling `trading-strategies` repo already ran one of these, and what it
found is the reason this repo is shaped the way it is. That run now lives here
too, ported into `src/chan/pair_cointegration.py`. Every computed number this
section quotes is asserted in
[tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py), and
this section states them rather than deriving them. Chan's own published
figures, 1.6766 among them, are quoted from the book and are not computed here
at all, which is the distinction the vocabulary table draws between a published
figure and a replication.

The GLD/GDX hedge ratio and the cointegration test statistic are printed near
each other in the book and are not one result. The hedge ratio, 1.6766, comes
from a full-window run in Chapter 7. The test statistic comes from a Chapter 3
example that drops the last 60 days and tests only the first 252. They also
come from two different regression specifications: Chan's hedge ratio is a
regression forced through the origin, and his test statistic uses a separate
regression with an intercept.

Reading them as one result produces the wrong number twice over. On modern
data the through-origin slope is about 1.6379, and independent reproductions
converge there. The slope from the test's own specification, with an
intercept, is 1.3905. Neither is 1.6766, and the reason no modern download
reaches 1.6766 is the vintage: Chan read a 2007-vintage adjusted series, and
nineteen years of GDX dividends have rescaled it since.

The sibling's response was to read raw as-traded prices instead, which are
fixed by construction. A given day's close is a historical fact whatever
dividends come later.

Two things follow for this repo. Trace every published number to its own run
and its own specification before trying to match it. And prefer a series that
cannot be restated, falling back on a committed vintage when only an adjusted
series will do.

### Three more results came across with it

Each one earns its place by answering an objection the GLD/GDX gap invites.

1. **Chan's own archived GLD and GDX files.** The obvious reply to a hedge that
   will not reproduce is that the reproduction is wrong. Chan's own companion
   spreadsheets, re-run through the same code, give 1.6395 rather than his
   printed 1.6766. His saved data does not reach his published number either,
   so the 2007 vintage he read is a state no surviving file carries. The
   cointegration verdict survives the drift. Only the hedge moved.
2. **KO and PEP, Example 7.3.** The second reply is that a replication which
   never matches is a replication that cannot match anything. Chan's KO/PEP
   counter-example reproduces his printed figures to the digit, because his
   companion data for it survives intact. The same code, on a vintage that was
   not lost, lands exactly. That pair is also the demonstration that
   correlation and cointegration are different things: KO and PEP correlate in
   daily returns at 0.4849 and do not cointegrate in levels.
3. **The lag setting behind Chan's Python verdict.** Chan reports that Python
   disagreed with MATLAB and R on this pair and concludes Python's statistics
   packages cannot be trusted. The packages are fine. `statsmodels` reads the
   lag count off the data by default and picks six on the short window, where
   MATLAB and R fix it at one, and six lags carry the statistic back across the
   10% line. A conclusion about a library turned out to be a conclusion about a
   default.

A fourth piece of machinery came with them. The rolling-window scan in
`rolling_cointegration` re-runs the test on a one-year window stepped monthly
across the whole history, which turns a single verdict into a map of when the
relationship held. Over GLD/GDX only 31 of 231 windows clear even the 10% bar
and they cluster before 2015, so cointegration here is a property of a window
rather than of the pair. Nothing outside the tests calls it yet.

Three things follow, and they set what the repo holds.

1. **A replication is a record, not a script.** It carries the vintage, the
   code, the number it got, the number the book printed, and a written verdict
   on the gap. [docs/replication-log.md](replication-log.md) is where those
   records are kept, and it carries the rule for choosing between the three
   verdicts the vocabulary below defines.
2. **A gap is a result.** A number that fails to reproduce says something about
   the method's sensitivity, and that is worth more than a match nobody
   examined. It gets written down with the same care as a match.
3. **A replication is exploratory until it is registered.** Reproducing a
   published figure spends the sample on a hypothesis someone else already
   chose, so it cannot confirm that an edge exists today. It can only say
   whether the published number reproduces.

### The estimators live outside this repo

The least squares, the Augmented Dickey-Fuller statistic, the half-life and
the MacKinnon critical values are not in `src/chan`. They are in
[ithildincore](https://github.com/l3a0/ithildin-core), a package this repo shares
with the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo.

They moved because both repos had them. `src/chan/timeseries.py` and that
repo's `common/timeseries.py` parsed to the same tree once docstrings were set
aside, and two copies of one calculation drift without either looking wrong.
A rule to keep them matching was considered and cut, for the reason in the
register below.

This cuts against the premise, and the way it is pinned is what limits the
damage rather than what removes it. A result here has to be re-readable, and
part of the code that produced it now lives somewhere else.

So `pyproject.toml` names the dependency by a direct URL at an exact commit,
`uv.lock` records that commit, and CI runs `uv sync --locked`. Each of those
does one job, and each answers a different way the pin could have failed.

1. **The commit rather than the `v0.1.0` tag it belongs to.** A tag can be
   moved on the remote. `uv sync --locked` would not follow it, but a
   `uv lock --upgrade` would, and then the lock would record the new target as
   though nothing had happened.
2. **The lock, because a plain `uv sync` re-locks silently** and installs
   different code the moment `pyproject.toml` and the lock disagree, rewriting
   the lock inside a runner where nothing commits it. `--locked` fails instead.
3. **The URL rather than a bare `ithildincore>=0.1` with a `[tool.uv.sources]`
   entry.** `ithildincore` is an occupied name on PyPI, an unrelated backtesting
   package whose 0.1.0 release satisfies that floor, and `tool.uv.sources` is a
   uv-only key that pip ignores. The earlier spelling would have had a
   contributor running `pip install .` install a stranger's package under the
   name this repo imports. A direct URL is satisfiable by no index.

Moving the pin is therefore a re-pin of this repo rather than a dependency
bump.

The price is real and is not paid off by the pin. A committed vintage sits in
this repository, and the code now sits behind a remote reference. If
`ithildin-core` is deleted, made private, or force-pushed past the commit the lock
names, no pinned number here is re-derivable at all, and nothing in this repo
can prevent that. The data has no such failure mode. What the pin buys is that
a change cannot happen quietly, not that it cannot happen.

Two things did not move, and the reasons are worth keeping.

1. `src/chan/paths.py` stays, because the line that matters differs between
   the two repos. It resolves `parents[2]` here against `parents[1]` there,
   since this repo nests its package under `src/`. What is shared is the
   pattern rather than the constant.
2. `tests/test_timeseries.py` went with the code, and something had to take
   its place rather than nothing.
   [tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py)
   exercises the same estimators against committed vintages with exact pins,
   so it does fail when the dependency moves. What it cannot do is say so. Every
   one of its assertions reads a CSV, so a dependency change and a vintage
   change arrive as the same red, and telling those two apart is the thing this
   repo exists to do.
   [tests/test_ithildincore_contract.py](../tests/test_ithildincore_contract.py) is
   what restores the distinction. Its cases read no vintage and have answers
   known in closed form, so they fail only on the dependency. Both files red
   points at the pin, the pair tests alone red points at the data. Mutating
   `ou_half_life` in the installed package was run to confirm the first half of
   that.

## Vocabulary

Terms with exact definitions, reused on purpose. A term listed here is not a
candidate for a synonym.

| Term | Definition |
| --- | --- |
| **vintage** | One download of one series, identified by vendor, symbol, span, download date, and which price the series carries, committed as a file with a checksum. |
| **raw price** | The as-traded close. Fixed once the day has passed, so it is the same in every vintage. |
| **adjusted price** | A close rescaled backward to fold in splits and dividends. It moves whenever a corporate action falls between two downloads, which is what makes a vintage necessary. |
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
yfinance needs none, which is why everything built so far runs with no
configuration at all.

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
| The sibling repo's price-fetch script | Nothing here regenerates a committed vintage, on purpose. A re-download returns a different series, which moves the pinned numbers and fails the suite, so replacing a vintage stays a deliberate act with a visible cost. [data/README.md](../data/README.md) states the same next to the files it governs. This cuts the script, not the work: [issue 1](https://github.com/l3a0/quantitative-trading/issues/1) records a series as a vintage and keeps the download outside itself, so every rule it carries is testable with no network. |
| Recomputing a published number in prose | Prose states numbers and never derives them. A doc that recomputes a figure is a second implementation of the calculation, and the two drift without either looking wrong. The test is the single authority. |
| The sibling's blog essay on the GLD/GDX reproduction, cut then reversed | Cut because it is that repo's write-up, and copying it would put a second prose surface here quoting numbers the test suite already owns. The owner reversed that on 2026-09-17 and the essay is at [blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md). The price the cut named is now real and is paid rather than avoided: every figure the piece quotes had to be pinned or named as unpinned, and re-pinning one moves four surfaces instead of two. The verdict an essay does not reach is now written down separately, in [docs/replication-log.md](replication-log.md), which makes a fifth. |
| The sibling's catalog of unbuilt Chan experiments | It is a plan for work nobody has started, and the tracker is authoritative for unbuilt scope. A catalog in a doc competes with the issues and goes stale the moment one of them moves. |
| The regime-map figure and its generator, cut then reversed | Cut because the scan behind the figure was already pinned, so the picture is presentation rather than a result, and an image nothing regenerates is an artifact nobody can check. The owner reversed that on 2026-09-17. The objection is answered rather than ignored: [src/chan/regime_figure.py](../src/chan/regime_figure.py) draws the figure from the committed vintages, and [tests/test_regime_figure.py](../tests/test_regime_figure.py) pins that it draws the scan `TestRollingRegime` computes. It does not compare bytes, because a PNG carries the matplotlib version that rendered it. The image still counts as a checked-in generated artifact for [issue 6](https://github.com/l3a0/quantitative-trading/issues/6). |
| Keeping the duplicated estimators in step with a drift test | The test cannot exist. Neither repo's continuous integration can see the other's checkout, so the check would compare against a committed checksum that fires only when somebody updates it. A rule that depends on remembering is what the duplication already was. The estimators moved to [ithildincore](https://github.com/l3a0/ithildin-core) instead. |
| Depending on ithildincore by name plus a `[tool.uv.sources]` redirect | `ithildincore` is an occupied name on PyPI, and `tool.uv.sources` is a uv-only key that pip ignores, so `pip install .` resolved the name against an unrelated package. A direct URL at a commit is satisfiable by no index, which closes it for every installer rather than only for uv. Hatchling needs `allow-direct-references` to permit that, which is fine here because this repo is cloned and run rather than published. |
| Depending on ithildincore by version range | A range lets a release change a number here with nothing in this repo's diff to explain it, which is the vintage failure applied to code. The dependency names a tag and `uv.lock` records the commit, so a bump is a visible, deliberate re-pin. |
| A price cache shared across replications | It reintroduces the vintage problem at one remove. Two replications reading one cache cannot say which download each result rests on, and refreshing the cache silently re-pins both. |
| Reporting only the replications that matched | A gap is a result. Reporting matches alone turns the log into an advertisement and destroys the thing it is useful for. |
