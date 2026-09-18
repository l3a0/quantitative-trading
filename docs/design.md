# Design — quantitative-trading

This doc carries the reasoning. An unbuilt deliverable's scope lives on its
issue, which [CLAUDE.md](../CLAUDE.md) makes authoritative, and this doc links
to an issue rather than restating it. The order lives there too, in each
issue's own statement of what it waits on.

## Contents

- [Premise](#premise)
- [What this repo is for](#what-this-repo-is-for)
  - [Three more results came across with it](#three-more-results-came-across-with-it)
  - [The estimators live outside this repo](#the-estimators-live-outside-this-repo)
  - [The one replication that reads nothing](#the-one-replication-that-reads-nothing)
- [How work is cut and ordered](#how-work-is-cut-and-ordered)
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
symbol, the span, the download date, and which price it carries recorded next
to it. Everything else
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
other three figures this doc names. The notes are the 2021 revised edition of
*Quantitative Trading*, and the chapter and page citations in this repo are
first-edition. The next subsection says what follows from that, because the
two editions do not tell the same story about where these numbers come from.

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

### Which edition the chapter labels mean

This repo calls one GLD/GDX run the Chapter 7 run and the other the Chapter 3
run. Those are **first-edition labels**, and the revised edition committed in
[research/book-notes](../research/book-notes/README.md) does not support them.
[Issue 12](https://github.com/l3a0/quantitative-trading/issues/12) asked the
question. The committed highlights answer it.

1. **Location 1862.** "Here, however, I will defer until Chapter 7 the
   cointegration analysis on the training set." The training-set run is the one
   this repo labels Chapter 3, and Chapter 3 hands it forward rather than
   performing it.
2. **Location 3678.** "This example teaches you how to use a free MATLAB
   package ... to determine if two price series are cointegrated and, if so,
   how to find the optimal hedge ratio." One example produces both outputs.
3. **Locations 3718 and 3727.** The CADF printout and the hedge printout, nine
   locations apart, the second closing with "This should produce a chart
   similar to Figure 7.2."

So in the revised edition there is no two-chapter split. Both printouts belong
to one worked example in Chapter 7.

**What survives, and it is the half the pins rest on.** The repo asserts two
separations at once, and only one of them was ever about chapters.

- **Two chapters on two windows** is first-edition numbering. It does not hold
  in the revised edition.
- **Two regression specifications** holds in any edition, because it is a
  property of the MATLAB package rather than of the book's structure. `cadf`
  fits with an intercept and reports the t-statistic, while the printed hedge
  ratio of 1.6766 comes from a through-origin `ols`. Reading one figure as
  though it came from the other's fit is the trap, and renumbering chapters
  does not touch it.

The labels stay, because the windows they name are unambiguous and renaming
them across five surfaces would buy nothing the price basis and the date range
do not already say. What changes is that they are now declared as
first-edition shorthand rather than left to look like the book's own
structure. Every citation of a chapter, a page, an example number or a MATLAB
filename in this repo means the 2009 first edition unless it says otherwise.
Example 6.1, the coin-flip gamble, is the one that says otherwise: that name
comes from the revised edition's prose at location 3186, and the first-edition
mirror carries no `example6_1` at all.

One thing this does not settle, and the difference matters. `-3.357` appears
nowhere in the committed highlights, and neither does a window label for the
`-3.18` run. A highlight covers what somebody marked, so absence here is not
absence in the book, and neither number's provenance is closed by this.

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

1. **The commit rather than the tag it belongs to.** A tag can be moved on the
   remote. `uv sync --locked` would not follow it, but a `uv lock --upgrade`
   would, and then the lock would record the new target as though nothing had
   happened.
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

### The one replication that reads nothing

Every argument above is about data that moves underneath a result. Chan's
coin-flip gamble, Example 6.1, has none. It is a fair coin paying $110 or
costing $100 against $1,000 of capital, and every figure the book prints
follows from those payoffs.
[src/chan/coin_flip_growth.py](../src/chan/coin_flip_growth.py) works it, and
[tests/test_coin_flip_growth.py](../tests/test_coin_flip_growth.py) is the
authority for every number quoted about it.

Four things follow, and each one is a rule stated elsewhere in this repo
meeting a case it was not written for.

1. **A vintage column can say it has none.** The premise says a result is
   committed next to the series it came from. There is no series, so the row
   writes `none, synthetic` and `src/chan/__init__.py` now says a result names
   its vintage or says it has none. Saying nothing would read as an omission.
2. **Neither epistemic label reaches it.** The vocabulary defines exploratory
   as a result produced by looking at the data, and registered as one whose
   hypothesis was committed before the number was seen. This spends no sample,
   so the entry states that both are inapplicable rather than picking one.
3. **The verdict was knowable before the work started.** A verdict says
   whether the claim a published figure supports survives on this repo's
   vintage, and the mechanism that moves a number is a vintage. With none,
   nothing can move it. The value of this replication is therefore not its
   verdict. It is that the ensemble average and the time average are shown
   disagreeing in sign, and that the log format was exercised a second time.
4. **The book prints no formula, so the formula is what the pin holds.** Three
   plausible choices give three numbers. The population standard deviation
   with `g = m - s^2 / 2` reproduces −0.0005125 exactly. The sample form gives
   −0.006025, out by a factor of 11.8. The exact discrete rate gives
   −0.00050025, which differs at the fourth significant digit. The suite pins
   all three, because a pin on the first alone holds a number rather than a
   choice.

One thing this replication cannot do is reach its own precision by simulation,
because the spread of a single coin flip is two hundred times the quantity
being estimated. So the pins are closed form and the seeded run is the
demonstration, sized from a measurement rather than from taste.
[docs/replication-log.md](replication-log.md) carries both figures, under the
heading that says why no simulated number is pinned against the book, which is
where that entry's numbers belong.

## How work is cut and ordered

The tracker carries the plan. Issues say what each deliverable is, milestones
group them, and each issue names what it waits on. This section carries only
the reasoning behind that, which an issue is the wrong place for because it
outlives any one of them.

`docs/build-plan.md` used to hold both. It was retired on 2026-09-18 because a
plan in a document and a plan in a tracker drift, and the tracker is the one
that is authoritative under [CLAUDE.md](../CLAUDE.md). The price of keeping it
had become visible: two issues were open against its staleness at the moment it
was removed.

### Cutting

A deliverable is cut down to the smallest piece that leaves the repo usable by
someone at the end of it. Not a layer, and not a subsystem. A piece that ends
with a component nobody can run is cut the wrong way.

The recorder is the worked example and the caution at once. It shipped as
`Part of` its issue rather than closing it, because a vintage nothing can read
is a component nobody can run. Nothing here reads what it writes yet, and that
wait is what cutting this one too narrowly cost.

### What an experiment pins

Each experiment pins the figures the book prints, at the precision the book
prints them, naming its vintage and its window. An experiment that reads no
series names neither and says so, rather than leaving the column blank, because
a blank reads as an omission. A column with nothing to hold in any row is
dropped instead, which is why the coin flip's computed table has five columns
where the pair entry's has six.

Where the book states a ranking or a verdict rather than a figure, the claim is
what gets pinned. Inventing a digit the source does not carry would be worse
than pinning the claim the source makes.

### The debt that replaced the dependency

The first replications were planned to wait on the vintage machinery. That is
not what happened: the sibling repo's finished replications were copied here
first, so the computation arrived before the machinery meant to feed it.

The dependency was real and is now a debt rather than a gate. Every replication
still reads by filename, so each one added before the reader lands is another
reader to convert. That is the live constraint on ordering, and it is the
reason a synthetic experiment can go ahead of the machinery while a
series-reading one cannot.

### Two candidates, named so they are not re-invented

Neither is committed to, and neither has an issue.

1. A negative-results log, once a replication has failed in a way worth
   recording separately from its own entry.
2. A registered experiment, which is a different object from a replication and
   needs its hypothesis committed in writing before any number is seen.

Nothing else is planned past the experiments, on purpose. The ranking rule says
evidence from real use decides the order, and this repo has run few enough
replications to have produced little of it.

## Vocabulary

Terms with exact definitions, reused on purpose. A term listed here is not a
candidate for a synonym.

| Term | Definition |
| --- | --- |
| **vintage** | One download of one series, identified by vendor, symbol, span, download date, and which price the series carries, committed as a file with a checksum. |
| **raw price** | The as-traded close. Fixed once the day has passed, so it is the same in every vintage. |
| **adjusted price** | A close rescaled backward to fold in splits and dividends. It moves whenever a corporate action falls between two downloads, which is what makes a vintage necessary. |
| **replication** | An attempt to reproduce a specific published number from a named source, against a named vintage, or against no data at all where the source's own number needs none. |
| **published figure** | The number the source prints, quoted at the precision the source uses. |
| **gap** | The difference between a published figure and what the replication computed, stated at the precision both support. |
| **manifest** | `data/vintages.jsonl`, the record of every committed vintage, one JSON object per line. The authority for a vintage's provenance. Nothing else in this repo is called a manifest. |
| **projection** | A file derived from the manifest and rewritten from it, never edited. `data/checksums.sha256` is the only one. |
| **verdict** | The written conclusion of a replication: reproduced, reproduced with a gap, or did not reproduce, with the reason. |
| **ensemble average** | The average across many players of one gamble, which is what an expected return describes. Chan names it at Kindle location 3166. |
| **time average** | The average over one player's own sequence of rounds, which is the compound growth rate of that player's capital. Chan calls it the time series average at location 3166. It is the one a trader lives in. |
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
| The sibling repo's price-fetch script | Nothing here regenerates a committed vintage, on purpose. A re-download returns a different series, which moves the pinned numbers and fails the suite, so replacing a vintage stays a deliberate act with a visible cost. [data/README.md](../data/README.md) states the same next to the files it governs. This cut the script and not the work. [src/chan/vintage.py](../src/chan/vintage.py) records a series as a vintage and keeps the download outside itself, so every rule it carries is exercised with no network. |
| Recomputing a published number in prose | Prose states numbers and never derives them. A doc that recomputes a figure is a second implementation of the calculation, and the two drift without either looking wrong. The test is the single authority. |
| The sibling's blog essay on the GLD/GDX reproduction, cut then reversed | Cut because it is that repo's write-up, and copying it would put a second prose surface here quoting numbers the test suite already owns. The owner reversed that on 2026-09-17 and the essay is at [blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md). The price the cut named is now real and is paid rather than avoided: every figure the piece quotes had to be pinned or named as unpinned, and re-pinning one moves four surfaces instead of two. The verdict an essay does not reach is now written down separately, in [docs/replication-log.md](replication-log.md), which makes a fifth. |
| The sibling's catalog of unbuilt Chan experiments | It is a plan for work nobody has started, and the tracker is authoritative for unbuilt scope. A catalog in a doc competes with the issues and goes stale the moment one of them moves. |
| The regime-map figure and its generator, cut then reversed | Cut because the scan behind the figure was already pinned, so the picture is presentation rather than a result, and an image nothing regenerates is an artifact nobody can check. The owner reversed that on 2026-09-17. The objection is answered rather than ignored: [src/chan/regime_figure.py](../src/chan/regime_figure.py) draws the figure from the committed vintages, and [tests/test_regime_figure.py](../tests/test_regime_figure.py) pins that it draws the scan `TestRollingRegime` computes. It does not compare bytes, because a PNG carries the matplotlib version that rendered it. The image still counts as a checked-in generated artifact for [issue 6](https://github.com/l3a0/quantitative-trading/issues/6). |
| Keeping the duplicated estimators in step with a drift test | The test cannot exist. Neither repo's continuous integration can see the other's checkout, so the check would compare against a committed checksum that fires only when somebody updates it. A rule that depends on remembering is what the duplication already was. The estimators moved to [ithildincore](https://github.com/l3a0/ithildin-core) instead. |
| Depending on ithildincore by name plus a `[tool.uv.sources]` redirect | `ithildincore` is an occupied name on PyPI, and `tool.uv.sources` is a uv-only key that pip ignores, so `pip install .` resolved the name against an unrelated package. A direct URL at a commit is satisfiable by no index, which closes it for every installer rather than only for uv. Hatchling needs `allow-direct-references` to permit that, which is fine here because this repo is cloned and run rather than published. |
| Depending on ithildincore by version range | A range lets a release change a number here with nothing in this repo's diff to explain it, which is the vintage failure applied to code. The dependency names an exact commit and `uv.lock` records it, so a bump is a visible, deliberate re-pin. |
| A price cache shared across replications | It reintroduces the vintage problem at one remove. Two replications reading one cache cannot say which download each result rests on, and refreshing the cache silently re-pins both. |
| Renaming the eight committed vintages to the recorder's path convention | The recorder's path carries vendor, symbol, price basis, span and download date. The eight predate it and carry none of that. Renaming them would move the eight files, `data/checksums.sha256`, [data/README.md](../data/README.md)'s table and prose, `load_close` and three provenance comments in [src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), two docstrings in [tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py), and five rows of [docs/replication-log.md](replication-log.md). Each of those cites a filename beside a pinned number, and a rename buys none of them. The manifest carries the path, so identity is read from the record rather than parsed out of a name, which is what makes two conventions affordable. |
| Reading a clock for a vintage's download date | The recorder does not fetch, so it cannot know when a fetch happened, and a date it invents is wrong in the field that identifies the vintage. It would also make every test differ from the last run. The caller supplies it. |
| Porting the sibling's `kelly_fraction` for the coin-flip growth rate | It is the only place in `trading-strategies` that computes a time-average log growth rate, and it computes it as one line inside a grid search rather than as a callable, so there is a line to retype and nothing to port. [Issue 14](https://github.com/l3a0/quantitative-trading/issues/14) had already ruled the function out as the discrete form over a bag of trades. The ruling reaches Example 6.1 by a shorter route: that example optimises nothing at all. |
| Porting the sibling's `common/portfolio.py` as growth arithmetic | It is not growth arithmetic. Its own docstring fixes every leg as dollar diffs over a fixed capital base, "never prior-day-equity returns (compounding returns do not add; dollars do)", so it decided against compounding on purpose. |
| Porting the sibling's `simulate_sizing` for the coin-flip simulation | It folds draws through `equity *= (1 + fraction * r)`, which is the identity Example 6.1 needs, and nothing around that line carries over: an empirical bag of trade outcomes rather than a known two-point distribution, percentiles and ruin probabilities rather than a growth rate, and `random.Random` rather than the `numpy.random.default_rng` this repo uses throughout. A port would have been a rewrite. |
| Moving the growth arithmetic to `ithildincore` | The bar there is two repositories, not two call sites, and the duplication does not exist. `ithildincore` holds no growth function and the sibling holds one line inside a grid search, so a shared module today would have one consumer and a plan. The price is named rather than hidden: a second implementation later if [issue 14](https://github.com/l3a0/quantitative-trading/issues/14) needs the same arithmetic. That is the moment to re-ask, because it is the first at which a second real consumer could exist. |
| A figure for the coin-flip divergence | `docs/figures` holds one image and it already costs three copies to keep in step, one file and two embeds, plus a redraw in the same change that moves it. The divergence is four rows of capital, which a terminal table and a log row carry without adding a third copy of a number the suite already pins. |
| A repo-wide `* text=auto eol=lf` | The exposure it would answer stops at `data/`. Measured on a clone of `main` made with `core.autocrlf=true`, `docs/figures/reproduction_regime_map.png` is byte-identical, because git detects a PNG as binary on its own, and `ruff check` and `ruff format --check` both pass over the rewritten sources. A rule reaching the whole repository would be fixing past the class it was written for. `.gitattributes` names `data/**` and stops there, which is what [issue 41](https://github.com/l3a0/quantitative-trading/issues/41) built. |
| `data/** text eol=lf` as the spelling of that rule | The two spellings agree on every file this repo holds, because both deliver LF for content already stored as LF, so no comparison of bytes tells them apart on today's data. That is why `tests/test_checkout_bytes.py` reads the attribute itself in a second case. They differ on content carrying a carriage return. Committing such a file from a checkout with `core.autocrlf=true` stores the bytes on disk under `-text` and stores them with the carriage returns gone under `text eol=lf`, which git reports only as a warning. A vintage's sha256 is recorded before the commit, so that spelling turns a recorded fact into a false one and leaves no way back to the bytes. `-text` forbids conversion. `text eol=lf` only promises which ending git picks when it rewrites. `binary` is cut for a different reason. It is a macro for `-text`, `-diff` and `-merge`, so it would also stop the textual three-way merge on a vintage. A vintage's diff is how a replacement gets read, and [data/README.md](../data/README.md) already calls replacing one a deliberate act with a visible cost. `tests/test_checkout_bytes.py` pins that too, because `binary` holds the bytes as well as `-text` does and no byte comparison separates them. |
| Reporting only the replications that matched | A gap is a result. Reporting matches alone turns the log into an advertisement and destroys the thing it is useful for. |
