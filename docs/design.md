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
  - [The replications that read nothing](#the-replications-that-read-nothing)
  - [A replication that reads the book's own tables](#a-replication-that-reads-the-books-own-tables)
  - [The first time the fallback clause fires](#the-first-time-the-fallback-clause-fires)
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

A second failure is cruder and not about adjustment at all. A series can
change scale partway through while the record says nothing about it, and a
number computed across that day is arithmetic on two different units.

The class is named rather than the vendor, because it arrives by more than one
route. yfinance split-adjusts `Close` even when called with
`auto_adjust=False`. That put XLE's pre-split prices at half the scale of its
strikes in the sibling `trading-strategies` repo, and the delta hedge built on
them reported a fabricated result strong enough to read as a discovery before
the cause was found. `ko_chan.csv` reaches the same place from a workbook
column saved in 2008, which has nothing to do with yfinance: two of its
day-over-day moves are near-exact halvings. So `src/chan/series.py` reads each
committed price series against itself and stops a run whose window spans a scale
break, and [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) is the
authority for what the committed vintages carry.

So the one thing this repo must get right is the vintage. A series used to
produce a number is committed alongside that number, with the vendor, the
symbol, the span, the download date, and which price, rate or event the series
carries recorded next to it. Everything else here is regenerable. Rerun the analysis and it comes back. Lose the vintage
and the number becomes an assertion nobody can check, including its author.

**One exception, for licensed bars.** Alpha Vantage's one-minute GLD and GDX
bars, which [issue 23](https://github.com/l3a0/quantitative-trading/issues/23)
reads, are the first series this repo may not commit. The vendor's terms grant
personal, non-commercial use, and no vendor priced on that issue published terms
allowing raw bars to be republished. The owner decided on 2026-10-03 that the
owner's data archive keeps the bytes and this repo commits only their hashes, in
`data/archive_vintages.jsonl`. The series is still kept and the record still
names its exact bytes, so a result still rests on a series that can be checked,
but only where the archive is. A public clone can see what a run read and
cannot re-run it, which is the price, and it is why the minute pins never run
in CI. The exception covers these two series. A later licensed series needs its
own decision from the owner, and a series anyone may republish is committed as
before.

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
other three figures this doc names. A figure from a source Chan cites rather
than prints traces to
[research/papers](../research/papers/README.md) instead, which holds the
document whole. The *Quantitative Trading* notes are that book's 2021
revised edition, and the chapter and page citations of it in this repo are
first-edition. The *Algorithmic Trading* notes are that book's only edition,
of 2013. The next subsection says what follows from that, because the
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
   packages cannot be trusted. The packages are fine. Against MATLAB the
   disagreement is a lag count. `statsmodels` reads the count off the data by
   default and picks six on the short window, where Chan's MATLAB call passes
   one, and six lags carry the statistic back across the 10% line. A
   conclusion about a library turned out to be a conclusion about a default.
   On Chan's own files a reconstruction of MATLAB's `cadf` at one lag lands
   the printed −3.18156477 to all eight decimals, which row 12 of the
   replication log's Entry 1 records. `cadf` forms its regression slightly
   differently from `statsmodels`, which moves the one-lag statistic by
   0.0035 and changes no verdict.
   His R run is a different test. The book's R code calls `CADFtest`,
   Hansen's covariate-augmented Dickey-Fuller test, on all 385 days rather
   than the 252, and passes GDX's price where the test expects a stationary
   series. That makes the regression an error-correction cointegration test
   whose printed p-value comes from a distribution that does not apply. On
   Chan's own files every figure both runs print reproduces at the precision
   printed, apart from R's p-value and its ρ², and the two t-statistics agree
   to within a billionth. Which lag count the Engle-Granger test is entitled
   to is a different question,
   and an exploratory residual check bears on it where a sweep cannot. That
   check is the second figure in `docs/figures`, added on the owner's request
   on 2026-09-27. It earns the place a number cannot take, because it shows
   which lag is missing, and it costs two copies rather than the regime map's
   three, one file and one embed in
   [docs/replication-log.md](replication-log.md), since nothing inlines it.

A fourth piece of machinery came with them. The rolling-window scan in
`rolling_cointegration` re-runs the test on a one-year window stepped monthly
across the whole history, which turns a single verdict into a map of when the
relationship held. Over GLD/GDX only 31 of 231 windows clear even the 10% bar
and they cluster before 2015, so cointegration here is a property of a window
rather than of the pair. `chan.regime_figure` and `chan.stationary_candidates`
call it, the second for Chan's fixed-income candidate.

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
A citation from *Algorithmic Trading* names that book, as Example 7.2 and
`pead.m` do.
Box 6.1, the coin-flip gamble, says otherwise, because its label exists only
in the revised edition. It is a revised-edition sidebar titled "Loss aversion
is not a behavioral bias", which the 2009 edition could not hold because it
quotes Kahneman's 2011 book, so the first-edition mirror has no file for it. This repo called it Example 6.1 until
2026-09-29, misreading the box's own sentence at location 3186, "As Example 6.1
shows". That sentence cites a separate, earlier example for the continuous
approximation, and the owner corrected the label against the book. Example 3.3,
Chan's survivorship toy, also says otherwise. Its label comes from the revised
edition, and whether the 2009 edition numbers it the same way was not checked.
Example 3.8, the reversal updated at the open, says otherwise too. It is on
p. 78 of the revised edition, the first-edition mirror holds no file for it,
and whether the 2009 edition carries it was not checked.

One thing this does not settle, and the difference matters. `-3.357` appears
nowhere in the committed highlights, and neither does a window label for the
`-3.18` run. A highlight covers what somebody marked, so absence here is not
absence in the book, and neither number's provenance is closed by this.

### The estimators live outside this repo

The least squares, the Augmented Dickey-Fuller statistic, the half-life, the
MacKinnon critical values and the Newey-West significance block are not in
`src/chan`. They are in
[ithildincore](https://github.com/l3a0/ithildin-core), a package this repo shares
with the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo.

The first four moved because both repos had them. `src/chan/timeseries.py` and
that repo's `common/timeseries.py` parsed to the same tree once docstrings were
set aside, and two copies of one calculation drift without either looking
wrong. A rule to keep them matching was considered and cut, for the reason in
the register below.

The Newey-West block took the other route in, and naming it here is what stops
the two being read as one rule. `common/stats.py` was never duplicated here. It
had eleven consumers next door and none in this repo, and it went over because
this repo's next significance claim would need it. That claim is Qian's risk
parity, which reports a Sharpe ranking as a measured difference and a robust
t-statistic rather than as a sign, so relocating exercised code was the whole
of what happened rather than anything being built.

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

### The replications that read nothing

Every argument above is about data that moves underneath a result. Chan's
coin-flip gamble, Box 6.1, has none. It is a fair coin paying $110 or
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
   candidate formulas give three numbers. The population standard deviation
   with `g = m - s^2 / 2` reproduces −0.0005125 exactly. The sample form gives
   −0.006025, out by a factor of 11.8. The exact discrete rate gives
   −0.00050025, which differs at the second significant digit. The suite pins
   all three, because a pin on the first alone holds a number rather than a
   choice.

One thing this replication cannot do is reach its own precision by simulation,
because the spread of a single coin flip is two hundred times the quantity
being estimated. So the pins are closed form and the seeded run is the
demonstration, sized from a measurement rather than from taste.
[docs/replication-log.md](replication-log.md) carries both figures, under the
heading that says why no simulated number is pinned against the book, which is
where that entry's numbers belong.

A second replication reads nothing. *Algorithmic Trading*'s Examples 8.1 and
8.2, constant leverage and capped Kelly allocation, are arithmetic on inputs the
book states, and
[src/chan/kelly_allocation.py](../src/chan/kelly_allocation.py) works them.
The first three points above apply unchanged, and
[docs/replication-log.md](replication-log.md) Entry 17 states them for its own
rows. The fourth applies in a sharper form. The book gives its formulas as
images, so the specification is what the suite pins beside each figure, and one
printed figure, 0.96, lands only because Chan rounds an exact tie up. No
simulation is involved, so nothing here needs the seeded demonstration the coin
flip carries.

### A replication that reads the book's own tables

Chan's toy strategy for survivorship bias, Example 3.3 in the revised edition,
runs on two ten-row tables the book prints and on nothing else. One is what a
survivorship-free database picks and the other what a database of survivors
picks instead.
[src/chan/survivorship_bias.py](../src/chan/survivorship_bias.py) holds both
tables and works the returns, and
[tests/test_survivorship_bias.py](../tests/test_survivorship_bias.py) is the
authority for every number quoted about it.
[docs/replication-log.md](replication-log.md) Entry 9 carries the two figures
the book prints and the verdict on each, which is where those numbers belong.

Four things follow, and they are where this case parts from the coin flip.

1. **The inputs are not a vintage, and the vocabulary is extended rather than
   stretched.** A vintage is a series a vendor was asked for or a column lifted
   from one of Chan's own files, and a table printed in a book is neither. A
   printed number cannot be restated by a vendor, so what pins it is the
   edition, which [research/book-notes](../research/book-notes/README.md)
   already records. So the definition of a replication gains a third case,
   inputs the source itself prints, and the vintage column reads
   `none, the book's printed tables`. The price is that the twenty rows sit in
   code rather than beside the other committed data, so
   [data/README.md](../data/README.md) does not list them and the module's
   docstring is where a reader finds their source.
2. **The vintage cell names no price basis.** Every committed vintage names
   its basis. The book does not say whether its
   database adjusted for splits, and at least one row shows a split it did not
   adjust for, so writing either word would assert something nobody measured.
3. **It keeps a window.** The coin flip has no window in any row, so its
   column was dropped. This toy reads no series, but the book fixes the dates,
   so every row has a window to hold and the column stays.
4. **Having no vintage does not put the inputs beyond question.** The coin
   flip's verdict was knowable before the work started, because nothing could
   move its number. The same is true of a printed table's arithmetic. What this
   case adds is that a printed row can still be checked against something
   outside the book, and the one row that was checked against a company filing
   compares a price before a reverse split with one after it. That is a
   finding about Chan's table rather than a failure to reproduce it, and the
   log entry carries it beside the figure it qualifies.

Neither epistemic label reaches it, for the coin flip's reason: reproducing the
arithmetic on a printed table spends no sample.

### The first time the fallback clause fires

`## What this repo is for` ends by saying to prefer a series that cannot be
restated, falling back on a committed vintage when only an adjusted series will
do. Chan's Kelly example, Example 6.2, is the first deliverable where the
fallback is what fires, and the reasoning outlives its log entry because every
later experiment on a dividend-paying instrument meets the same question.

The preference for raw closes rests on GDX, which had paid almost nothing by
2007. That made Chan's 2007-vintage adjusted close near raw, so a modern raw
series was the closest surviving proxy for what he read. SPY had been paying
for fifteen years by the end of his window, and on his own data the difference
between the two columns is worth a quarter of the answer.
[docs/replication-log.md](replication-log.md) Entry 3 carries both figures,
and [tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py) pins both.
The first, 2.5278, comes from his adjusted column, which the repo holds as
`data/spy_chan.csv`. The second, 1.9341, comes from his as-traded column, which
[issue 192](https://github.com/l3a0/quantitative-trading/issues/192) committed
as `data/spy_unadjusted_chan.csv`. So reading raw here would not be a
conservative choice about restatement. It would be a different experiment.

It is also not a choice about a number. Chan's own conclusion at Kindle
location 3083 is that even half-Kelly would not have survived Black Monday, and
that claim holds exactly while the leverage is above 1.954079, which is a figure
this repo does compute and pin. His adjusted column clears that threshold and
his as-traded column does not, so the price basis decides the verdict rather
than shading it. That makes the column a yfinance download hands over part of
the result. Under `auto_adjust=False`, yfinance returns a split-only `Close`
beside the close carrying the dividends. SPY has not split, so its split-only close is its as-traded close,
and on Chan's own data that is the side of the threshold his conclusion does
not survive on. Recorded as `adjusted`, it would carry that answer under the
other label. So
every `adjusted` yfinance line in the manifest names its column in a
`vendor_column` field, which
[issue 125](https://github.com/l3a0/quantitative-trading/issues/125) added, and
a test fails on a line that leaves it out.

What this adds to the standing rule above is how to tell which half of it
applies, which the rule itself leaves to judgement. Ask what the source's own
adjustment was worth on the symbol and the span in question. Near zero, and the
raw series is the better proxy for what the author read. Not near zero, and the
raw series answers a different question, so the committed adjusted vintage is
what the fallback was written for.

That measurement is the price of the rule, and it is not free. Answering it
for SPY took both columns of Chan's own workbook, and this repo committed the
second one for that reason alone. Where no such measurement is available, the
rule cannot be applied and the honest move is to say which basis was read and
that the choice was not tested.

One more thing this experiment settles, because it contradicts a choice made
two deliverables earlier. The dispersion is the sample form, dividing by
`n - 1`. `src/chan/coin_flip_growth.py` uses the population form, and that is
also right: it averages over two outcomes that are the whole distribution,
where the sample correction has nothing to correct for. Here the returns are a
sample of a process, MATLAB's `cov` is what Chan's own `example6_3.m` calls,
and on this repo's own SPY vintage the two forms are 5.74e-5 apart on the
Sharpe ratio, which `tests/test_kelly_leverage.py` pins. The rule is that the
form follows what the numbers are rather than what the last experiment picked.

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
is a component nobody can run. The reader landed on 2026-09-18 and closed that
gap, two deliverables after the recorder rather than one. What the narrow cut
cost is the stretch in between, when the repo held a component that wrote a
record nothing could read back.

### What an experiment pins

Each experiment pins the figures the book prints, at the precision the book
prints them, naming its vintage and its window. An experiment that reads no
series names neither and says so, rather than leaving the column blank, because
a blank reads as an omission. The exception is an experiment whose source fixes
the dates without supplying a series, which names its window and says it has no
vintage. Chan's survivorship toy is that case, and
[A replication that reads the book's own tables](#a-replication-that-reads-the-books-own-tables)
says why. A column with nothing to hold in any row is dropped instead, which is
why the coin flip's computed table has five columns where the pair entry's has
six.

Where the book states a ranking or a verdict rather than a figure, the claim is
what gets pinned. Inventing a digit the source does not carry would be worse
than pinning the claim the source makes.

### The debt that replaced the dependency

The first replications were planned to wait on the vintage machinery. That is
not what happened: the sibling repo's finished replications were copied here
first, so the computation arrived before the machinery meant to feed it.

The dependency was real and the debt it left has been paid. Every replication
read by filename until the reader landed, so each one added in between was
another reader to convert, and the conversion reached `aligned_closes`, `run`,
`make_regime_figure` and two `main` functions rather than one function. That
cost is what the ordering rule was protecting against, and it is the reason a
synthetic experiment can go ahead of the machinery while a series-reading one
cannot.

### Two candidates, named so they are not re-invented

Neither is committed to, and neither has an open issue.

1. A negative-results log, once a replication has failed in a way worth
   recording separately from its own entry.
2. A registered experiment, which is a different object from a replication and
   needs its hypothesis committed in writing before any number is seen. The
   first one proposed, running Conditional Parameter Optimization on daily
   closes, was declined, and `## Considered and rejected` records it.

Nothing else is planned past the experiments, on purpose. The ranking rule says
evidence from real use decides the order, and this repo has run few enough
replications to have produced little of it.

## Vocabulary

Terms with exact definitions, reused on purpose. A term listed here is not a
candidate for a synonym.

| Term | Definition |
| --- | --- |
| **vintage** | One series as one source held it on one date, identified by vendor, symbol, span, that date, and which price, rate or event the series carries, committed as a file with a checksum. Example 7.1's two series of Alpha Vantage minute bars are kept in the owner's data archive instead, with only their checksums committed, under the exception the premise states. The date is a download date when a vendor was asked for the series, and a saved date when the series is a column lifted from one of Ernest Chan's own files, because nothing was fetched on that day. An entry in the **manifest** carries exactly one of `download_date` and `saved_date`, and which one it carries says which kind of vintage it describes. A stock lifted from one of Chan's MATLAB files is one vintage holding its close, high, low, open and volume together, decided on [issue 88](https://github.com/l3a0/quantitative-trading/issues/88), because the source saved them together and an identity naming one series could not tell them apart. |
| **raw price** | The as-traded close, or for a futures series the exchange's daily settlement as published. Fixed once the day has passed, so it is the same in every vintage. |
| **adjusted price** | A close rescaled backward to fold in splits and dividends. It moves whenever a corporate action falls between two downloads, which is what makes a vintage necessary. |
| **scale break** | A day on which a committed price series changes scale rather than price, meaning a day-over-day close ratio too far from 1 for a price move. The date is the later of the two days, so a window opening on it does not span the break. [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) holds the bound and what the committed vintages carry. The guard skips a **rate** vintage and an **event** vintage, because neither holds a price. |
| **rate** | The third basis a vintage can carry, beside **raw price** and **adjusted price**. A rate vintage holds a series of rates, such as a Treasury-bill yield, recorded as the vendor publishes it. It has no raw or adjusted form, and the scale-break guard does not read it, because a rate near zero can move sixfold in a month without changing units. |
| **event** | The fourth basis a vintage can carry. An event vintage holds a 0 or 1 for each day of a calendar, saying whether something happened that day, such as an earnings announcement, in one field named `Flag`. Every day of the calendar is kept, a 0 included, because a reader may cut its prices to the calendar's own days, and a file of events alone would start that calendar at its first event. It has no raw or adjusted form, the scale-break guard does not read it, and a panel read refuses to hand it back as a close. Decided on [issue 250](https://github.com/l3a0/quantitative-trading/issues/250) for Chan's earnings flags. |
| **replication** | An attempt to reproduce a specific published number from a named source, against a named vintage, against inputs the source itself prints, or against no data at all where the source's own number needs none. |
| **published figure** | The number the source prints, quoted at the precision the source uses. |
| **gap** | The difference between a published figure and what the replication computed, stated at the precision both support. |
| **manifest** | `data/vintages.jsonl`, the record of every committed vintage, one JSON object per line. The authority for a vintage's provenance. `data/archive_vintages.jsonl` is the second manifest, recording the vintages kept in the owner's archive, decided on [issue 23](https://github.com/l3a0/quantitative-trading/issues/23). Nothing else in this repo is called a manifest. |
| **projection** | A file derived from the manifest and rewritten from it, never edited. `data/checksums.sha256` is the only one. |
| **verdict** | The written conclusion of a replication: reproduced, reproduced with a gap, or did not reproduce, with the reason. |
| **ensemble average** | The average across many players of one gamble, which is what an expected return describes. Chan names it at Kindle location 3166. |
| **time average** | The average over one player's own sequence of rounds, which is the compound growth rate of that player's capital. Chan calls it the time series average at location 3166. It is the one a trader lives in. |
| **risk contribution** | A leg's share of a portfolio's variance, `w_i (Sigma w)_i / (w' Sigma w)`, where `Sigma` is the covariance matrix of the legs' returns. The shares sum to 1. It is what says how far a capital split is from a risk split, and it is not a capital weight. |
| **risk parity** | The allocation whose risk contributions are equal. On two legs it is the same allocation as inverse-volatility weighting, because the correlation cancels out of the equal-contribution equation, and the two part company from three legs onward. A pin names which of the two it computed. |
| **exploratory** | A result produced by looking at the data. It kills an idea or justifies a closer look, and it is never a verdict about whether an edge exists. |
| **registered** | A result whose hypothesis was committed in writing before the number was seen. Only a registered result confirms anything. |

## Configuration

This repo is public. Tracked files never carry secrets or machine-specific
paths. Machine-local config lives under `~/.config/quantitative-trading/`.

The table below names every setting a run or a test reads from the machine.
None is a secret. yfinance needs no key, and the Alpha Vantage bars are read
from the owner's archive rather than fetched, so no vendor key enters the repo.
Everything that reads only committed vintages runs with no configuration at
all.

| Setting | Secret | Lives in | Read by |
| --- | --- | --- | --- |
| The data archive's path | no | `~/.config/quantitative-trading/archive_dir`, one line, or `QT_ARCHIVE_DIR` for one run | `chan.archive`, for the vintages `data/archive_vintages.jsonl` records |
| `QT_ARCHIVE_RUN=1` | no | the environment of one test run | `tests/test_cpo.py`, which runs its archive pins only when it is set, because the full run takes minutes |

## Considered and rejected

Machinery that was considered and cut, pinned here with the reason, so a
decision stays decided. When something new is cut, add it here in the same
change that cuts it.

| Cut | Why |
| --- | --- |
| Downloading a series at run time | It is the failure this repo exists to prevent. A run that fetches its own data produces a number nobody can reproduce, because the next fetch returns a different series. A run reads a committed vintage, or under the premise's exception an archived one whose hash is committed, or it does not run. |
| The sibling repo's price-fetch script | Nothing here regenerates a committed vintage, on purpose. A re-download returns a different series, which moves the pinned numbers and fails the suite, so replacing a vintage stays a deliberate act with a visible cost. [data/README.md](../data/README.md) states the same next to the files it governs. This cut the script and not the work. [src/chan/vintage.py](../src/chan/vintage.py) records a series as a vintage and keeps the download outside itself, so every rule it carries is exercised with no network. |
| Recomputing a published number in prose | Prose states numbers and never derives them. A doc that recomputes a figure is a second implementation of the calculation, and the two drift without either looking wrong. The test is the single authority. |
| Recomputing the p-value of Chan's R run | The book's R output prints p = 0.004975 from Hansen's covariate-augmented Dickey-Fuller distribution, and its t-statistic and every coefficient already reproduce on Chan's files. That distribution assumes a stationary covariate, and Chan's code passed GDX's price, which `TestChansRRunIsACovariateAugmentedDickeyFuller::test_the_covariate_went_in_as_a_price` shows is not stationary. So a recomputed p-value would reproduce a figure that does not apply to the run. Recomputing it would also need two things no dependency here carries: the R package `CADFtest`'s table of response surfaces in ρ², from Costantini, Lupi and Popp (2007), and the long-run covariance estimate from the `sandwich` package that the package computes ρ² with. Porting the table brings GPL code into an MIT repository, and calling R through `rpy2` adds a runtime dependency and a second language to CI. The essay quotes 0.005 as Chan's and README names it unpinned. Decided under [issue 168](https://github.com/l3a0/quantitative-trading/issues/168). |
| The sibling's blog essay on the GLD/GDX reproduction, cut then reversed | Cut because it is that repo's write-up, and copying it would put a second prose surface here quoting numbers the test suite already owns. The owner reversed that on 2026-09-17 and the essay is at [blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md). The price the cut named is now real and is paid rather than avoided: every figure the piece quotes had to be pinned or named as unpinned, and re-pinning one moves four surfaces instead of two. The verdict an essay does not reach is now written down separately, in [docs/replication-log.md](replication-log.md), which makes a fifth. A second post, [blog/price-spread-mean-reversion.md](../blog/price-spread-mean-reversion.md), quotes many of the same figures and makes a sixth. [blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md) sets GLD/GDX's full-span statistic, its half-life, its window count and the plain ADF bars beside the stationary candidates, and makes a seventh. |
| The sibling's catalog of unbuilt Chan experiments | It is a plan for work nobody has started, and the tracker is authoritative for unbuilt scope. A catalog in a doc competes with the issues and goes stale the moment one of them moves. |
| The regime-map figure and its generator, cut then reversed | Cut because the scan behind the figure was already pinned, so the picture is presentation rather than a result, and an image nothing regenerates is an artifact nobody can check. The owner reversed that on 2026-09-17. The objection is answered rather than ignored: [src/chan/regime_figure.py](../src/chan/regime_figure.py) draws the figure from the committed vintages, and [tests/test_regime_figure.py](../tests/test_regime_figure.py) pins that it draws the scan `TestRollingRegime` computes. It does not compare bytes, because a PNG carries the matplotlib version that rendered it. The image still counts as a checked-in generated artifact for [issue 6](https://github.com/l3a0/quantitative-trading/issues/6). |
| Keeping the duplicated estimators in step with a drift test | The test cannot exist. Neither repo's continuous integration can see the other's checkout, so the check would compare against a committed checksum that fires only when somebody updates it. A rule that depends on remembering is what the duplication already was. The estimators moved to [ithildincore](https://github.com/l3a0/ithildin-core) instead. |
| Depending on ithildincore by name plus a `[tool.uv.sources]` redirect | `ithildincore` is an occupied name on PyPI, and `tool.uv.sources` is a uv-only key that pip ignores, so `pip install .` resolved the name against an unrelated package. A direct URL at a commit is satisfiable by no index, which closes it for every installer rather than only for uv. Hatchling needs `allow-direct-references` to permit that, which is fine here because this repo is cloned and run rather than published. |
| Depending on ithildincore by version range | A range lets a release change a number here with nothing in this repo's diff to explain it, which is the vintage failure applied to code. The dependency names an exact commit and `uv.lock` records it, so a bump is a visible, deliberate re-pin. |
| A price cache shared across replications | It reintroduces the vintage problem at one remove. Two replications reading one cache cannot say which download each result rests on, and refreshing the cache silently re-pins both. |
| Renaming the hand-named committed vintages to the recorder's path convention | The recorder's path carries vendor, symbol, price basis, span and download date. A hand-placed file carries none of that, which was true of the eight this row was measured over and is true of every one added since. Renaming them would move the eight files, the manifest's `path` field, `data/checksums.sha256`, [data/README.md](../data/README.md)'s table and prose, two provenance comments in [src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), all four files under `tests/`, and five rows of [docs/replication-log.md](replication-log.md). The surfaces are named rather than the citations inside them counted, because a count goes stale on the next test that names a file. Each of those cites a filename beside a pinned number, and a rename buys none of them. The reader is the one surface a rename no longer touches, because [src/chan/series.py](../src/chan/series.py) asks the manifest for the path rather than building one out of a ticker. Identity read from the record rather than parsed out of a name is what makes two conventions affordable. |
| Resolving a vintage by the latest download date | It is the clock cut below, arriving through the manifest instead of through a time function. A new download of a series would move every pinned number that reads it, with nothing in the diff to explain the move. It also does not run: the committed workbook columns carry a saved date and no download date, so the comparison raises `TypeError` on `None`. [src/chan/vintage.py](../src/chan/vintage.py) refuses an ambiguous request and names the candidates, so a second download stops a run rather than re-pinning it. |
| Naming a vintage by its path to tell two downloads apart | The path is the record's shadow and the manifest is the record, which is the same reasoning as the rename row above. A path argument hands identity back to the filename this reader exists to stop parsing, and it ties every pinned replication to the recorder's naming convention, so the convention could not change without moving pins. The reader takes a date instead, compared against whichever of `download_date` and `saved_date` an entry carries, which names every committed vintage where an argument named for the download date reaches only the downloads. |
| Pinning the eight committed vintages by set equality over the whole manifest | The pin compared the whole manifest against a set of eight tuples, so it described the eight and spoke for every entry the manifest would ever hold. A ninth vintage is an extra member and fails it, which made recording one fail the suite and put the five replications that each need a new series behind a choice about weakening an integrity check. It is keyed on the hand-written paths instead, and still asserts every one of them is present. Name what that gives up, and name it accurately, because the first version of this row claimed more than the code does. Set equality failed on any ninth entry at all, a forged one included, for the same reason it failed on a recorded one: it enumerated eight. Keying on paths gives that up entirely. A hand-written entry that brings its own file, hashes it correctly, takes the name its own fields produce and has the projection regenerated over it passes the whole suite, measured at 257 passed. No test can close that, because such an entry is byte for byte what the recorder would have written, and what separates the two is the commit that added one. What the remaining assertions catch is an entry inconsistent with itself. `test_every_committed_series_has_exactly_one_entry` fails one naming no file on disk or repeating a path already taken, and the path-identity check below fails one whose fields and whose name disagree. |
| Writing the symbol into a recorded vintage's file rather than holding it from the path | Scoping the pin above leaves four of the five identity fields [src/chan/vintage.py](../src/chan/vintage.py)'s `vintage_filename` puts in a path covered by no test: vendor, symbol, price basis and download date. A manifest naming the wrong series then reads green, and the reader hands one series' closes back under another's name, verified against the recorded sha256. The fifth is the span, which stays covered along with the row count and the sha256, because `test_every_entry_describes_the_file_it_names` derives all three from the file. Writing the symbol into the bytes would cover it, and it costs four surfaces that pin the recorder's single `Date,Close` header: the two byte-for-byte pins, the assertion that the header does not borrow one vendor's shape, and the prose in `_serialize` and [data/README.md](../data/README.md)'s `## Header shape`, which state one thing between them. The reader does not constrain the choice, since `_parse_close` drops every leading row whose first field is not a date and reads either shape. What decided it was when the decision was made. No recorded vintage existed yet, so the change would have cost those four surfaces and nothing else, while after the first one was recorded a vintage is immutable by the premise, so the older shape would stay on disk and the set of files a check has to exempt would grow by an entry nothing marks as older. The path already carries all five identity fields, so comparing an entry against the name it took is the cheaper check and it moves no bytes. It does not reopen the two rows above. Those forbid identity being read out of a filename, and this reads the filename out of the identity. Their cost still lands, because a check that asserts the naming convention moves when the convention does, and the hand-written vintages are exempt from it since the rename row keeps their hand-given names. |
| Reading a clock for a vintage's download date | The recorder does not fetch, so it cannot know when a fetch happened, and a date it invents is wrong in the field that identifies the vintage. It would also make every test differ from the last run. The caller supplies it. |
| Porting the sibling's `kelly_fraction` for the coin-flip growth rate | It is the only place in `trading-strategies` that computes a time-average log growth rate, and it computes it as one line inside a grid search rather than as a callable, so there is a line to retype and nothing to port. [Issue 14](https://github.com/l3a0/quantitative-trading/issues/14) had already ruled the function out as the discrete form over a bag of trades. The ruling reaches Box 6.1 by a shorter route: that box optimises nothing at all. |
| Porting the sibling's `common/portfolio.py` as growth arithmetic | It is not growth arithmetic. Its own docstring fixes every leg as dollar diffs over a fixed capital base, "never prior-day-equity returns (compounding returns do not add; dollars do)", so it decided against compounding on purpose. |
| Porting the sibling's `simulate_sizing` for the coin-flip simulation | It folds draws through `equity *= (1 + fraction * r)`, which is the identity Box 6.1 needs, and nothing around that line carries over: an empirical bag of trade outcomes rather than a known two-point distribution, percentiles and ruin probabilities rather than a growth rate, and `random.Random` rather than the `numpy.random.default_rng` this repo uses throughout. A port would have been a rewrite. |
| Moving the growth arithmetic to `ithildincore` | The bar there is two repositories, not two call sites, and the duplication does not exist. `ithildincore` holds no growth function and the sibling holds one line inside a grid search, so a shared module today would have one consumer and a plan. The price is named rather than hidden: a second implementation later if [issue 14](https://github.com/l3a0/quantitative-trading/issues/14) needs the same arithmetic. That is the moment to re-ask, because it is the first at which a second real consumer could exist. Re-asked when [issue 14](https://github.com/l3a0/quantitative-trading/issues/14) shipped and the answer is unchanged. The sibling repo was searched at `cc1ec3a` and holds no leverage or growth arithmetic at all, only a Sharpe ratio written twice as a four-line private helper inside a strategy module, so there is still one consumer and a plan. [Issue 14](https://github.com/l3a0/quantitative-trading/issues/14)'s own arithmetic shares no function with the coin flip either, since one computes a leverage from a return series' moments and the other a growth rate over two outcomes. Re-asked for [issue 298](https://github.com/l3a0/quantitative-trading/issues/298), which added the Gaussian `g = r + F'M - F'CF / 2` in `chan.kelly_allocation` beside `chan.kelly_leverage`'s `levered_growth` and the coin flip's `growth_continuous`. That is three call sites in one repository. The sibling, searched at `477c594`, still holds only the one growth line inside `kelly_fraction`'s grid search, so there is still one repository with a consumer and the answer is unchanged. |
| A figure for the coin-flip divergence | `docs/figures` held one image when this was decided, and it already cost three copies to keep in step, one file and two embeds, plus a redraw in the same change that moves it. The divergence is four rows of capital, which a terminal table and a log row carry without adding a third copy of a number the suite already pins. [blog/coin-toss-expected-value-vs-growth.md](../blog/coin-toss-expected-value-vs-growth.md) later added that third copy, as a four-row table of ratios, so a re-pin now moves three surfaces. That is still text a re-pin edits in place, where an image would need a redraw and its embeds. **Reversed by the owner on 2026-09-29**, who chose three figures for that post knowing this row: growth against the stake, a fan of capital paths, and the distribution of final balances. [src/chan/coin_flip_figures.py](../src/chan/coin_flip_figures.py) draws them and [tests/test_coin_flip_figures.py](../tests/test_coin_flip_figures.py) pins what they draw. The cost named above is now paid, three files and three embeds plus a redraw in any change that moves them. The owner added two more the same day, for Lesson 6, so the count is five of each. The row stays so the reasoning and its reversal are read together. |
| A constrained Kelly allocator for any number of strategies | Example 8.2 works two strategies on one line, `F1 + F2 = Fmax` with both long, and [src/chan/kelly_allocation.py](../src/chan/kelly_allocation.py) solves that in closed form. A general allocator is a quadratic program with a gross-leverage constraint, which is machinery no example in either book runs and nothing here would call a second time. The price is named rather than hidden: the two-strategy search is long-only, and with a strong positive correlation a short hedge inside the cap beats it. `tests/test_kelly_allocation.py` holds such a case, so the limit is tested rather than only stated. Cut while planning [issue 298](https://github.com/l3a0/quantitative-trading/issues/298). |
| Figures for the stationary candidates | Ruled out on [issue 16](https://github.com/l3a0/quantitative-trading/issues/16), on the reasoning of the regime-map row above: the candidates' rolling scans are pinned, so a picture of them is presentation, and each of the three scans invites reading one window as a finding. **Reversed by the owner on 2026-10-02** for [blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md), three times in one day: for a figure that draws no scan, then for the scans themselves, then for a lag sweep that draws none. The post carries all three. In the post's order, the first is two number lines carrying the bars of the ADF with a constant and of Engle-Granger, with the cross rate's and the bond pair's statistics over the whole test period on them. The second draws each candidate's statistic at every lag count up to the ceiling, filled where the residuals pass the check. Neither draws a window. The third draws the rolling scans, so its reversal reaches the whole ruling. It responds to the objection in words rather than avoiding it: its title reads "How often one-year windows reject says little about the whole test period", each panel's title gives the result over that period, its note says a window that clears a bar is not a finding, and its dots take each line's own colour rather than the green the regime map gives cointegrating windows. The post's Lesson 4 says the same beside it. [src/chan/stationary_candidates_figures.py](../src/chan/stationary_candidates_figures.py) draws all three and [tests/test_stationary_candidates_figures.py](../tests/test_stationary_candidates_figures.py) pins what they draw. The part of the objection none of them answers is the cost: three more files and three more embeds to keep in step, and a redraw in any change that moves a statistic, a lag sweep or a scan they draw. The row stays so the ruling and its reversals are read together. |
| A repo-wide `* text=auto eol=lf` | The exposure it would answer stops at `data/`. Measured on a clone of `main` made with `core.autocrlf=true`, `docs/figures/reproduction_regime_map.png` is byte-identical, because git detects a PNG as binary on its own, and `ruff check` and `ruff format --check` both pass over the rewritten sources. A rule reaching the whole repository would be fixing past the class it was written for. `.gitattributes` names `data/**` and stops there, which is what [issue 41](https://github.com/l3a0/quantitative-trading/issues/41) built. |
| `data/** text eol=lf` as the spelling of that rule | The two spellings agree on every file this repo holds, because both deliver LF for content already stored as LF, so no comparison of bytes tells them apart on today's data. That is why `tests/test_checkout_bytes.py` reads the attribute itself in a second case. They differ on content carrying a carriage return. Committing such a file from a checkout with `core.autocrlf=true` stores the bytes on disk under `-text` and stores them with the carriage returns gone under `text eol=lf`, which git reports only as a warning. A vintage's sha256 is recorded before the commit, so that spelling turns a recorded fact into a false one and leaves no way back to the bytes. `-text` forbids conversion. `text eol=lf` only promises which ending git picks when it rewrites. `binary` is cut for a different reason. It is a macro for `-text`, `-diff` and `-merge`, so it would also stop the textual three-way merge on a vintage. A vintage's diff is how a replacement gets read, and [data/README.md](../data/README.md) already calls replacing one a deliberate act with a visible cost. `tests/test_checkout_bytes.py` pins that too, because `binary` holds the bytes as well as `-text` does and no byte comparison separates them. |
| Comparing a symbol's raw vintage against its adjusted one as the scale-break detector | A split rescales both bases together, so dividing one by the other cancels the thing the detector is looking for. Measured on GDX's two committed vintages, the adjusted-over-raw ratio moves by at most 0.0163 on any single day the two vintages share, which is dividend drift rather than a split, and [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) pins that number so the dead end is not re-derived. It also needs two vintages of one symbol on different bases. Only GLD and GDX had them when this was cut, and SPY's two workbook columns, which [issue 192](https://github.com/l3a0/quantitative-trading/issues/192) added, do not reach KO, so it could say nothing about `ko_chan.csv`, which is where the finding actually is. `scale_breaks` in [src/chan/series.py](../src/chan/series.py) reads each series against itself instead, which needs nothing external. |
| Porting the sibling repo's `[0.5, 2.0]` band as the scale-break bound | Both `ko_chan.csv` breaks sit inside it, at 0.5050 and 0.5047, so it would find nothing here. It is not wrong next door. It runs on already-adjusted closes, where a correct split leaves no cliff at all and anything reaching 0.5 is a different fault. The bound here is fitted to what this manifest holds instead, and [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) derives the envelope it was fitted to. It is a bound on the log of the ratio rather than a pair of endpoints, because a price ratio is multiplicative: `[0.6, 1.6]` is asymmetric by 0.0408 in log terms, so a guard built on it would answer differently on a series and on the same series reversed. |
| Backing the split adjustment out of the committed vintages for this repo's own reads | Cut by the owner on 2026-09-18, and the whole of what [issue 3](https://github.com/l3a0/quantitative-trading/issues/3) found wrong with the committed data goes to [issue 133](https://github.com/l3a0/quantitative-trading/issues/133) instead, which owns the `raw price` row above. No computation here wants an as-traded series repaired out of a vendor's split-adjusted one. Chan's own as-traded SPY column, which [issue 192](https://github.com/l3a0/quantitative-trading/issues/192) committed as `data/spy_unadjusted_chan.csv`, is a different object and does not reopen this. It is his bytes rather than a repair, SPY has not split so there is nothing to back out, and it is read to measure what the price basis is worth on his Kelly leverage rather than as the series every reader gets. Measured on that issue at `e9860fb` and not pinned by any test, on a synthetic pair carrying a two-for-one at the midpoint of four hundred seeded days: the hedge ratio is 2.3616 on a continuous series and 18.9014 on an as-traded one, and the worst daily log return goes from 0.0377 to 0.6998, which is the split itself. [src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py) regresses levels and [src/chan/regime_figure.py](../src/chan/regime_figure.py) rolls the same scan, and both want the continuity that split adjustment produces. The replication needs it too. Chan's 2007 series was adjusted for splits and dividends and today's `raw` for splits and not dividends, and raw works as a proxy because the two agree on splits. Chan says the same at Kindle location 1324, where unadjusted data drops at the ex-date "which may trigger an erroneous trading signal". Nothing is lost by cutting it, because the vendor's bytes are committed, while recording a repaired series would make the as-traded scale what every reader gets. An opt-in repair is the alternative, and an opt-in function with no caller is a path with a count of zero. The sibling `trading-strategies` repo does back it out and needed to, because it compared prices to option strikes. This repo holds no option chain. |
| Reporting only the replications that matched | A gap is a result. Reporting matches alone turns the log into an advertisement and destroys the thing it is useful for. |
| Asserting on `chan.vintage`'s own source to hold its writes to bytes | [tests/test_markdown_hygiene.py](../tests/test_markdown_hygiene.py) reads prose surfaces as text, so reading a module the same way had precedent. A source assertion pins a spelling rather than a behaviour, and a write can be text-mode under any number of spellings. Three reach this module: the builtin `open`, `pathlib.Path.open` and `pathlib.Path.write_text`, which opens through `Path.open`. The behavioural case is available instead: patching the module's `open` and `pathlib.Path.open` to translate, the way Windows does, drives the same code path on ubuntu and macOS, and it reports which file carried a carriage return rather than which line looked wrong. [Issue 64](https://github.com/l3a0/quantitative-trading/issues/64) built both and kept the behavioural one. |
| Making `read_manifest` refuse a line that ends in a carriage return | It would turn the reader into the alarm, which is the wrong place for one. The entries parse identically either way, so a manifest carrying carriage returns costs a run nothing, and refusing it would stop a run over a record whose content is correct. The premise stops a run when the bytes it is about to compute from are not the bytes that were recorded, and a line ending is not that. So the writer stops producing them, the reader keeps normalising, and `TestTheCommittedManifest` is where a stray one gets reported. |
| Repairing a misspelled identity field on read rather than refusing it | `_validated_identity` returns normalised values as well as refusing, so `read_manifest` could have matched a line spelling the vendor `Yfinance` instead of stopping on it. That is a repair, and a record one surface quietly rewrites while another writes it plainly is a record two surfaces disagree about. The manifest is in git, so a refusal sends the reader to [data/README.md](../data/README.md)'s own recovery procedure, `git diff --stat -- data/` and then `git checkout -- data/`, while a repair hides that anything moved. This does not reopen the carriage-return row above, and the difference is what the reader matches on. A carriage return changes nothing `resolve_vintage` compares, so refusing it would stop a run over a record that works. A vendor spelled `Yfinance` changes the thing being compared, so the record goes unreachable and the run is told no such vintage was ever committed. The alarm is already ringing there and it is ringing the wrong sentence. |
| A sweep that fails an open issue body naming a closed issue as a dependency | It cannot tell a stale claim from a satisfied one, and no form of it catches the class. Measured on 2026-09-18 over the 49 open bodies as they stood before [issue 52](https://github.com/l3a0/quantitative-trading/issues/52) corrected eight of them, counting a closed issue rather than a merged pull request, which is what separates these counts from a wider reading. Scoped to a paragraph carrying dependency wording, it flags 4 bodies and catches 2 of the eight. Scoped to the whole section under a heading naming dependencies, it flags 12 and catches 5. The two sets of catches are disjoint, and [issue 47](https://github.com/l3a0/quantitative-trading/issues/47) is caught by neither, because its stale sentence sits under a heading about what the issue is not. This overturns [issue 52](https://github.com/l3a0/quantitative-trading/issues/52)'s own `## Done when`, which said the section-scoped form misses issues [14](https://github.com/l3a0/quantitative-trading/issues/14) through [18](https://github.com/l3a0/quantitative-trading/issues/18) entirely. It catches exactly those five and misses issues [4](https://github.com/l3a0/quantitative-trading/issues/4), [43](https://github.com/l3a0/quantitative-trading/issues/43) and [47](https://github.com/l3a0/quantitative-trading/issues/47) instead, so the guard fails in the other direction rather than not at all. Seven of the 12 are correct bodies. Issues [19](https://github.com/l3a0/quantitative-trading/issues/19) through [23](https://github.com/l3a0/quantitative-trading/issues/23) name [#1](https://github.com/l3a0/quantitative-trading/issues/1) and [#2](https://github.com/l3a0/quantitative-trading/issues/2) in the same `## Depends on` section that issues [14](https://github.com/l3a0/quantitative-trading/issues/14) through [18](https://github.com/l3a0/quantitative-trading/issues/18) did, as needs a purchased series would still have to meet, which is true where "neither exists yet" was false. Separating those two needs a reader. |
| Requiring a branch to be up to date with `main` before it merges | GitHub's `strict_required_status_checks_policy`, on from the first commit and off since 2026-09-18 on an owner directive. It bought one thing: CI builds the merge of a branch and its base, so a run is computed against one merge ref, a later merge to the base replaces it, and a rollup can read green after the branch underneath it has gone stale. Requiring every branch current means every rollup was computed against the base the branch actually merges into. The price was charged to every branch rather than to the stale ones. On 2026-09-18 four pull requests were open at once, and [PR 111](https://github.com/l3a0/quantitative-trading/pull/111) was brought current twice after its review had already passed, once by a rebase when [PR 110](https://github.com/l3a0/quantitative-trading/pull/110) merged and once by a merge of `main` when two more landed. Each cost a full round of six checks, and [PR 110](https://github.com/l3a0/quantitative-trading/pull/110) shared no file with it. `CLAUDE.md`'s rule to re-read a rollup whenever the base has moved covers the same failure, on the branches where the base actually matters rather than on all of them. What is accepted in exchange is that a branch can now merge on a rollup computed against a base that has moved, caught by a session reading rather than by GitHub refusing. [Issue 129](https://github.com/l3a0/quantitative-trading/issues/129) carries the change and [l3a0/repo-template#14](https://github.com/l3a0/repo-template/issues/14) makes the same one in the template, so a repository seeded later does not get the rule back. |
| Generating [data/README.md](../data/README.md)'s table from the manifest, and scoping the test that replaced it to the eight | Two surfaces state each committed vintage's vendor, symbol, price basis, span and date, and the generator was the obvious way to leave one. Most of that file is prose a manifest cannot carry: why GLD's adjusted series covers a different span from its raw twin, what the `*_chan.csv` files are and where they came from, and what the three-row header means for `load_close`. A generator owning a block inside that prose is a generator plus a hygiene test plus a rule about where the block starts and stops, where the assertion in [tests/test_vintage.py](../tests/test_vintage.py) buys the same protection against drift. That claim was overstated when it was written, and it is corrected here rather than restated. It held for five columns and not for the Vendor cell, whose expected value the test joined from the entry's symbol instead of reading off the record, so the one column the two surfaces spell differently was compared against a guess rather than against the manifest. [Issue 152](https://github.com/l3a0/quantitative-trading/issues/152) closed that gap by recording the workbook, and the claim now holds for every column. It holds on a second assertion rather than on this one alone, which is worth naming because the Vendor column is the one place both surfaces are now hand-typed. Two hand-typed statements moving together agree with each other, so this check passes on a coordinated forgery and the identity pin in `tests/support/committed_vintages.py` is what fails it, measured as 472 passed before the workbook joined that pin and 2 failed after. Having `record_vintage` append a row is the same cut reached from the writing side. Scoping the check to the eight is cut with it, and the row above that scoped three other assertions does not cover this one. Those pinned an identity the recorder derives from the path it writes, so a second check could take back what scoping gave up. A table row is prose nothing derives, so scoping this one would let the table quietly stop describing the directory, which is the drift it exists to catch. The price is named rather than hidden, and it is the condition [issue 51](https://github.com/l3a0/quantitative-trading/issues/51) closed on. Recording a new vintage into `data/` leaves the suite red until somebody writes the row, measured as exactly one disagreement naming the recorded path rather than a cascade, and `TestARecordedVintageIsHeldToo` is where the suite states that rather than leaving it for whoever records the next one to discover. |
| A map in test support, and dropping the Vendor cell's workbook assertion, as the two other ways to stop deriving a workbook's filename from its symbol | `_vendor_cell` in [tests/test_vintage.py](../tests/test_vintage.py) joined a symbol to `.xls`, which states a fact about a mirror this repo does not hold from a field that does not carry it. It was true of the four workbook columns committed then and false of a column lifted from `example6_2.xls`, whose symbol names a real workbook in the same mirror holding another series. [Issue 124](https://github.com/l3a0/quantitative-trading/issues/124) committed that column as `spy_chan.csv`, so the case the derivation would have got wrong is now in the record. Three routes replaced it and two are cut. A map keyed by path in `tests/support/` is cut because every negative case drives `the_table_and_the_manifest_agree(directory)` against a copy `committed_copy` makes of `data/`, so a module constant sits outside the tree under test and no case can vary it. The route buys nothing until it also buys a helper and a parameter on the check. Dropping the assertion is cut because it takes the guard with it, measured at `8657c02` by two mutations that each left the case rewriting `ko_chan.csv`'s Vendor cell to another series' workbook red with `DID NOT RAISE AssertionError`, and because the owner ruled on 2026-09-18 that a vintage is immutable once committed, so a provenance claim written beside one is written permanently and the premise names the record as the thing that must not fail. What ships instead is an optional `source_workbook` on `VintageEntry`, which the vocabulary above already argued for by calling the manifest the authority for a vintage's provenance. The price is that a test-only change became a change to the record, and that the record gained a second field `record_vintage` can never write. `saved_date` is the first, so the precedent and the module docstring carrying it were both already there. |
| A section of [data/README.md](../data/README.md) as the record of which column an `adjusted` yfinance vintage holds | [Issue 125](https://github.com/l3a0/quantitative-trading/issues/125) weighed it against a field on `VintageEntry`, and the owner chose the field on 2026-10-02. The metric that decided between them was how many committed `adjusted` yfinance vintages leave their column undetermined, by their bytes and their prose together, in a way that moves a pinned number. Measured at `980e15a` it read 0 of 4. GDX's bytes show the dividends against its raw twin, GLD's route cannot move a number, and SPY's and AGG's stated calls agree with their bytes. That count argued for the convention, which was the recommendation, because a section and a test rewrite no committed line. The field puts the route on the manifest line, where a reader of the record or of the entry a load returns sees it, rather than only in prose. That follows the row above, which chose the record over prose for `source_workbook` and cited the owner's 2026-09-18 ruling that a vintage is immutable once committed. The ruling does not say whether a manifest line is part of the vintage. This row reads it by the vocabulary's definition: a vintage is its bytes and the identity fields that name them, so neither may change, and a provenance field added beside them changes neither. A field already on a committed line is never changed, so a claim written there stays written. [PR #155](https://github.com/l3a0/quantitative-trading/pull/155) added `source_workbook` to four committed lines on that basis without stating it, and [PR #235](https://github.com/l3a0/quantitative-trading/pull/235) added `vendor_column` to four more. Each of the eight differs from its committed form only by the added key, so no vintage's bytes, identity fields or sha256 moved, and neither did its line in `data/checksums.sha256`, which names files and not the manifest. The price is those four rewritten lines, and a field `VintageEntry` cannot require on the lines it is for, because requiring it on yfinance lines is a rule stated against a vendor and the module enforces none. A test over the committed manifest holds it instead, which is the enforcement the convention would have had. Neither route catches a mislabel at write time, because the recorder never sees the call. |
| A fallback requiring a heading span nothing attributes to exist somewhere in the tracked set | The sweep [issue 39](https://github.com/l3a0/quantitative-trading/issues/39) built reads a quoted heading against the document the sentence hands it to. A fallback for a sentence that hands it to nothing inverts that. Run over the tracked set at `92637fa`, it flags nine correct sentences, every one of them quoting a heading that belongs to a pull request body, an issue body, a review comment or a template shape. The span in this row makes it ten, which is the guard reading its own reasoning rather than a defect in the row. An issue body's `## Done when` is not a rename of anything, and no repository keeps the document it names. So the sweep classifies what a sentence attributes a heading to, and a span nothing attributes is left alone. The price is that a rename nobody wrote an attribution for goes unnoticed, which is cheaper than nine failures on prose that is right. |
| A slug normaliser that strips inline markup out of a heading before hashing it | GitHub's anchor for a heading carrying a link or a backtick is not the anchor for its raw characters. No heading in any tracked file carries either, measured at `92637fa`, so the normaliser is a branch nothing reaches and nothing would notice breaking. Emphasis markers need no special case, since an asterisk is dropped by the same filter that drops a comma. Write it when a heading needs it. |
| Checking that every Markdown link names a file that exists | It is a wider class than the anchor sweep and it was not what the issue asked for. The anchor sweep resolves a link's target only because it has to read that document's headings, and it reports a target it cannot find because an anchor into a retired document is the failure it exists for. Extending that to every link is a separate question with its own false-positive surface, starting with a link into a directory rather than a file. |
| Resolving a backticked filename from the directory of the document that writes it | A Markdown link resolves from the file holding it, because that is what a renderer follows. A filename written in prose is followed by nobody, and this repo writes those from the repository root. Trying the document's own directory as a second attempt would give a filename that names nothing a second chance, and that is the branch reporting a document nobody keeps. |
| Requiring a quoted heading's attribution to sit beside it | The nearest attribution ending before the span wins, scanned back through one unit, and nothing makes it adjoin the span. Every reference here is adjacent, separated from its span by a possessive and nothing else, so requiring adjacency would cost nothing measured at `92637fa`. It is not required because the loose forms are ordinary English and this check reads prose rather than a notation. A sentence that names a document and then quotes one of its headings a clause later attributes as plainly as a possessive does, and a rule that skipped it would go quiet on the rename it was built for. The price is a false positive where one unit names a document and then quotes a heading belonging to something else. Splitting a table row and a list item into their own units removes the shapes this repo actually writes. Four units name a document and quote one of its own headings at `92637fa`, and none names a document and quotes a heading belonging to something else. When one does, the message names the document it resolved to, so the misattribution reads off the failure rather than having to be guessed. |
| A Treasury-bill series for the risk-free rate in Chan's Kelly example | It would move two inputs at once, which is what makes a gap unattributable to either. The second vintage it needed is now committed, FRED's TB3MS under [issue 187](https://github.com/l3a0/quantitative-trading/issues/187), and the Kelly run still reads only the book's constant. The rate stays the book's 4 percent, held as a constant the source supplies, and the report says it is his constant applied to whatever window was read rather than a rate anyone paid. [Issue 14](https://github.com/l3a0/quantitative-trading/issues/14) is where this was decided. |
| A second series to check the 20.47 percent Black Monday loss against | It would need an S&P 500 index vintage, which is a different symbol and a different deliverable. SPY's first bar is 1993-01-29 and the loss is from 1987-10-19, so no SPY vintage of any span can check it. It enters the replication as a constant the book supplies, named as such, with the worst loss the window actually holds reported beside it. |
| TLT as the bond leg of the risk-parity replication | Cut by the owner on 2026-09-18. Qian's bond leg is an aggregate bond exposure and TLT is a twenty-plus-year Treasury fund, whose volatility sits far closer to equities' than an aggregate index's does. The derived weights could not then land near his 23-77, and the cause would be the instrument rather than the method, which is a verdict about a proxy rather than about the claim. AGG replaced it, chosen in writing before anything was downloaded. The ruling rested on that argument alone until Qian's own paper was found and committed at [research/papers](../research/papers/README.md), which describes the Lehman Aggregate as roughly 6,000 bonds with an approximate average maturity of ten years. Reading a maturity as a duration is this repo's step rather than his, because the paper never says duration, but an index his argument rests on that averages ten years is intermediate rather than long. So the cut stands on a figure the source states and not only on reasoning about it. Nothing inherits the choice: [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) tests Chan's fixed-income pair in [src/chan/stationary_candidates.py](../src/chan/stationary_candidates.py), where a long-duration leg is the faithful stand-in, and it carries its own written commitment to TLT and its own raw vintage of it. |
| Scanning the risk-free rate beside the 4 percent the risk-parity run declares | The rate moves the ranking and the direction is not in doubt, so a scan would spend the sample on a search nothing recorded, which is what the declared windows exist to prevent. The Sharpe difference moves with the rate by `1 / vol(60/40)` less `1 / vol(risk parity)`, which is exact and is pinned in [tests/test_risk_parity.py](../tests/test_risk_parity.py), so the report states the direction and computes no second ranking. `--risk-free` still moves it for a reader who wants to, and a run that moves it is off the reproduction the same way a new window is. Because the difference and its robust t are both linear in the rate, the rate at which the two Sharpe ratios tie and the rate at which the t reaches −2 follow in closed form from the declared ranking. The suite pins both, along with the t at a rate of zero. Quoting them is not a scan, because nothing is chosen from them and the report still prints the ranking at the declared rate only. The post's Lesson 1 figure computes one more ranking, at the 1.74% average three-month bill rate, through `full_span_ranking` in [src/chan/risk_parity_figures.py](../src/chan/risk_parity_figures.py). That is not a scan either. The rate is the one cash actually paid on average over the span, which is the like-for-like comparison with Qian's bill-rate figures, and it was fixed before the ranking was computed rather than picked from a range of rates. The Lesson 4 figure, `make_rate_figure` in the same module, computes the ranking at 51 rates from 0% to 5% to draw the line the closed form already gives. That is not a scan either. It draws every rate it computes and picks none of them, its three marked rates were fixed before it was drawn, and `test_the_gap_and_the_t_move_in_a_straight_line` holds every point to the closed-form line. The report still prints the ranking at the declared rate only. |
| Refitting the risk-parity weights inside each sub-window before ranking it | 60/40 is fixed by definition and never sees the data. Weights refitted inside a window have seen every day they are then judged on, so a ranking built that way compares a fixed allocation against a fitted one and risk parity wins some of that for a reason the book is not claiming. Measured on the rising-rates window, refitting moves the ranking in risk parity's favour, which is the direction that would have flattered the claim under test. The decomposition is still computed in-window, because what it answers is what balanced risk looked like in that regime, and it carries no ranking. The post's Lesson 5 figure, `make_window_figure` in [src/chan/risk_parity_figures.py](../src/chan/risk_parity_figures.py), draws the refitted Sharpe ratio as a fourth row beside the ranked one. That does not reopen this row. The refitted row is labelled hindsight and carries no t-statistic, and it is drawn to show how much of the later period's gap a refit would close, the flattery this row describes. The ranked row is still the one on the earlier period's weights, which is what `rank_the_windows` returns. |
| Giving `record_vintage` a saved-date parameter, so a column lifted from one of Chan's workbooks could be recorded rather than typed | It is the other way to make [issue 124](https://github.com/l3a0/quantitative-trading/issues/124)'s `spy_chan.csv` hold, and it is cut. `vintage_filename` takes `download_date` as a required keyword and ends every name it builds with `_dl{download_date}.csv`, so a recorder able to write a saved date needs a second naming convention, and `the_recorded_entries_name_themselves` compares a path against that join. The row above already says a check asserting the naming convention moves when the convention does, so this route pays that price to generate lines a person types once per workbook column. The route that shipped moves no predicate and one count, measured. The checks read a set of hand-written paths, so `spy_chan.csv` joining that set turns them on for it, and the only assertion that moved is `len(resolved) == 8` becoming `== 9` in [tests/test_series.py](../tests/test_series.py), which counts that same set. Nothing executable in `src/` moved, and the changes there are prose. What is given up is that a hand-typed line has no generator to check it against, and what replaces the generator is the identity pinned in [tests/support/committed_vintages.py](../tests/support/committed_vintages.py) and the `Ticker,` header row the file's own bytes carry, which names the series and is derived rather than restated. `python -m chan.kelly_leverage --chan` reads this vintage, shipped under [issue 138](https://github.com/l3a0/quantitative-trading/issues/138), whose body assumed this outcome. **Re-priced on 2026-10-02 for [issue 88](https://github.com/l3a0/quantitative-trading/issues/88).** The price this row weighed was one typed line per workbook column, and Chan's two MATLAB files hold 1,100 columns. The recorder still takes no saved date, so the cut stands for a single column. A second writer, `record_lifted_columns` in [src/chan/vintage.py](../src/chan/vintage.py), writes a whole source at once under a directory named for it, so it needs no second convention inside `vintage_filename` and `the_recorded_entries_name_themselves` skips its members by directory. |
| One vintage per cross-section, whose symbol names the universe rather than a ticker | Cut by the owner on 2026-10-02 on [issue 88](https://github.com/l3a0/quantitative-trading/issues/88). It needs a second file format and a rule for what `load_close` returns for a universe, where one vintage per stock keeps `record_vintage`, `vintage_filename` and `_serialize` as they are. What it would have saved is the scaling cost, which moved to the index instead: [tests/support/committed_vintages.py](../tests/support/committed_vintages.py) pins each source once, `data/README.md`'s table gives a directory one row, and `chan.series.load_panel` reads a source back from one manifest read. |
| Recording a stock's open, high, low and volume as vintages of their own beside its close | An open series would share vendor, symbol, basis and saved date with the close of the same stock, so `vintage_filename`'s fields and `resolve_vintage`'s match could not tell the two apart without a new identity field. Recording the close alone was decided first on 2026-10-02 for that reason, and the owner reversed it the same day on [issue 88](https://github.com/l3a0/quantitative-trading/issues/88), before anything merged, because the other four fields exist only in the mirror, which this repo does not control. One file per stock holds all five instead, so a stock stays one vintage. The price is 71.9 MB of file content where the closes took 28.0 MB, summed from the sizes git records for each file. Deciding after the merge would have meant a second set of 1,100 files carrying every close twice, since a vintage is never rewritten. |
| Pinning each column lifted from Chan's MATLAB files by its path, as `HAND_WRITTEN` pins a workbook column | It would be one hand-typed tuple per column, 1,100 when this was decided, then 2,094 once [issue 250](https://github.com/l3a0/quantitative-trading/issues/250) landed and 2,694 once [issue 225](https://github.com/l3a0/quantitative-trading/issues/225) landed, each saying the same four things, because one source was saved once and every member shares its vendor, basis, date and file. `LIFTED_SOURCES` pins each source once, with its member count, and the symbol is read from each member's own `Ticker,` header row. The count is what notices a member dropped with its file. What it gives up is a per-member date or basis, which nothing here has a reason to vary inside one file. |
| Committing Chan's `.mat` files themselves beside the columns lifted from them | They are 20 MB and 10 MB of binary that diff as nothing, and every array in them that holds a price or a volume is committed as text instead, one file per stock with all five fields, so the binaries would add their day list and their symbol list, which the text files restate, and a 116-byte header, of which the manifest restates the save date and nothing else. Their sha256 is recorded in [data/README.md](../data/README.md) instead, the way a workbook's is recorded beside the run that reads it. The price is that the check proving the per-stock files rebuild Chan's five arrays, NaN for NaN, ran once at conversion and cannot run again here, so [tests/test_series.py](../tests/test_series.py) pins the shape and the count of priced cells it saw. |
| Holding the lifted columns to the scale-break envelope the single-series vintages were fitted to | The bound flags a close below 0.625 or above 1.6 times the one before, and 52 of the first 1,100 columns cross it on 62 days, most of them real moves in single stocks. The book-two price file added 17 of its 497 columns on 30 days, all in 2007 to 2009, and the later S&P 600 save added 19 of its 600 on 21 days. [tests/test_scale_breaks.py](../tests/test_scale_breaks.py) pins every one by path and day instead, so a day that appears or disappears fails, and the envelope test keeps reading the single-series vintages it was fitted to. |
| Batching the checkout sweep through `git cat-file --batch --filters` | The sweep started two processes a path, 36 in all, and 2,236 once the lifted columns were in the index. The batched form converts the content and keeps the stored size in each header, measured at 37,542 against 38,229 bytes for `README.md` as it stood at `d7993f7`, so its output cannot be split by size. [tests/test_checkout_bytes.py](../tests/test_checkout_bytes.py) has `git checkout-index` perform the converting checkout into a scratch directory instead, in one process, which is also the conversion a clone actually runs. |
| Running Conditional Parameter Optimization on the daily GLD and GDX closes, with 2021-01-04 to 2026-08-27 held out | Conditional Parameter Optimization is the method of Chan's revised-edition Example 7.1: each day a model predicts the strategy's next-day return for every parameter set, and the set with the highest prediction is traded. [Issue 278](https://github.com/l3a0/quantitative-trading/issues/278) proposed running it on the daily closes this repo already holds, as the part of [issue 23](https://github.com/l3a0/quantitative-trading/issues/23) that needs no bought data. It was a method study with no printed figure to meet rather than a replication, since it differed from Chan's run in its bars, its overnight holding, its features and its model. The owner decided on 2026-10-03 not to run it and gave no reason, so taking it up again starts by asking the owner. The issue closed as not planned. No result from the method was computed, and the registered holdout was never run. It is not free of everything known about the pair, because the regime map draws the hedge across those years. The holdout stays clean only while nothing computes a result from the method on a day after 2020-12-31, and that includes runs under [issue 23](https://github.com/l3a0/quantitative-trading/issues/23), whose minute archive reaches into 2026. Taking the design up again needs an audit of its plan against the code, which has moved since it was written at `84ee556`. The method code shipped in `chan.cpo` under [issue 23](https://github.com/l3a0/quantitative-trading/issues/23), which brought scikit-learn in as a runtime dependency. That run stops at `SPAN_END`, 2020-12-31, in both its labels and its features, so it computed nothing on the holdout. |
| Committing Alpha Vantage's one-minute bars to `data/` | The vendor's terms grant personal, non-commercial use, and none of the six vendors priced on [issue 23](https://github.com/l3a0/quantitative-trading/issues/23) published terms allowing raw bars to be republished. The owner decided on 2026-10-03 that the archive keeps the bytes and the repo commits their hashes, which the premise records as an exception. |
| A private data repository with a deploy key, so CI could run the minute pins | It would have let CI execute the pins, at the price of the repo's first secret and a second repository to keep. The owner's archive already held GLD's bars beside a checksum, so the owner chose it on 2026-10-03 and the pins run only where the archive is. |
| Buying the minute bars from Kibot or FirstRate | Kibot quoted $83.62 for this slice and FirstRate about $400. The owner's premium Alpha Vantage key, which the owner keeps, supplied GDX at no extra cost, and GLD was already in the archive. Kibot stays the fallback if Alpha Vantage's terms ever rule the archive out. |
| Running every archive pin on every local test run | The full run of Example 7.1 reads 3.0 million GLD bars and 2.7 million GDX bars and fits a model on more than a million rows, which takes about five minutes. Every session here runs the suite, so the pins skip unless `QT_ARCHIVE_RUN=1` asks for them, with a reason that says so. The checks that the archive files still hash to their lines and agree with the committed daily closes run wherever an archive is configured, in about 20 seconds. |
