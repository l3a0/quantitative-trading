# Replication log

A replication is finished when it reaches a verdict. Until then the repo holds
a reproduced experiment, which is a number sitting next to another number with
nobody saying what the pair means.

This file is where the verdicts live. One entry per replication, and one row
per published result, carrying the five parts
[docs/design.md](design.md#vocabulary) defines: the published figure, the
vintage, what this repo computed, the gap, and the verdict. A row usually
matches one published figure to one computation. Four of Entry 1's rows do not,
and each says so in its own cells.

1. Row 2 carries no published figure, because the book prints no
   with-intercept slope.
2. Row 5 reproduces one published figure from two vintages at once.
3. Row 10 carries no published figure, because the book stops in 2007.
4. Row 11 covers the two statistics Chan printed from one disagreement.

Entries 2 and 3 carry their own, three and three, and they are listed in those
entries rather than here, because the list is about an entry's rows and not
about the file.

Every result in Entries 1 and 3 is **exploratory** in the design doc's sense.
Reproducing a published figure spends the sample on a hypothesis someone else
already chose, so an entry can say whether the number reproduces and nothing
about whether the trade works today. Entry 2 spends no sample at all and is
outside that label and its opposite both, which it states rather than picking
one.

## Contents

- [How to read an entry](#how-to-read-an-entry)
  - [Two traceability rules](#two-traceability-rules)
  - [What precision a number is quoted at](#what-precision-a-number-is-quoted-at)
  - [How a verdict is chosen](#how-a-verdict-is-chosen)
  - [Rows that are not replications](#rows-that-are-not-replications)
  - [What a second entry does to this file](#what-a-second-entry-does-to-this-file)
- [Entry 1: GLD/GDX and KO/PEP, Chan's *Quantitative Trading*](#entry-1-gldgdx-and-kopep-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed)
  - [What this repo computed](#what-this-repo-computed)
  - [The verdicts](#the-verdicts)
  - [What the entry concludes](#what-the-entry-concludes)
  - [Two counts and two senses of one word](#two-counts-and-two-senses-of-one-word)
  - [What the citations do not cover](#what-the-citations-do-not-cover)
  - [The chapter labels are first-edition shorthand](#the-chapter-labels-are-first-edition-shorthand)
  - [Nothing checks this file against the suite](#nothing-checks-this-file-against-the-suite)
- [Entry 2: the coin-flip gamble, Chan's *Quantitative Trading*](#entry-2-the-coin-flip-gamble-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-1)
  - [What this repo computed](#what-this-repo-computed-1)
  - [The verdicts](#the-verdicts-1)
  - [What the entry concludes](#what-the-entry-concludes-1)
  - [Why no simulated number is pinned against the book](#why-no-simulated-number-is-pinned-against-the-book)
- [Entry 3: Kelly leverage on SPY, Chan's *Quantitative Trading*](#entry-3-kelly-leverage-on-spy-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-2)
  - [What this repo computed](#what-this-repo-computed-2)
  - [The verdicts](#the-verdicts-2)
  - [What the entry concludes](#what-the-entry-concludes-2)
  - [Figures from Chan's workbook, which nothing here pins](#figures-from-chans-workbook-which-nothing-here-pins)
  - [What this entry cannot say](#what-this-entry-cannot-say)

## How to read an entry

### Two traceability rules

The two columns of numbers come from different places, so one rule cannot cover
both.

1. **Every computed number names the assertion that holds it.** One test file
   per entry is the single authority for every figure that entry computes, and
   the computed column states those figures rather than deriving them.
   [tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py)
   holds Entry 1,
   [tests/test_coin_flip_growth.py](../tests/test_coin_flip_growth.py) holds
   Entry 2, and
   [tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py) holds
   Entry 3.
2. **Every published figure names where the source prints it, or says it has no
   citation.** A published figure is quoted from the book and is asserted
   nowhere. Chan's 1.6766 is a target the replication chases, and the design
   doc and the suite's own docstring both record that it is asserted nowhere.
   Where the figure is among the committed
   highlights in [research/book-notes](../research/book-notes/README.md), the
   row gives its Kindle location. Where it is not, the row says so and points at
   the recorded absence.

Three of the figures below carry no location, and that absence is already
written down. [research/book-notes/README.md](../research/book-notes/README.md)
names −3.357, 1.0114 and −2.14 as the figures the highlights miss, because a
highlight covers the sentences somebody marked rather than the numbers a
replication ends up chasing. Their values survive in `BOOK_REF_FULL` and
`KOPEP_REF` in
[src/chan/pair_cointegration.py](../src/chan/pair_cointegration.py), which is
where those rows trace to.

Row 8 is therefore quoted at the two decimals `KOPEP_REF` records, and not at
the −2.14258438 that the docstring of `test_fails_to_cointegrate` also carries.
A docstring is not an authority for a number. Row 4 looks like the opposite
call and is not: its eight-digit figure is quoted because the book prints it,
at location 3718.

### What precision a number is quoted at

A computed number is quoted at the precision its assertion holds, never past it.

The four CADF statistics are pinned at `abs=1e-2`, so they are quoted at two
decimals even though the engine returns four. The hedge ratios are pinned at
`abs=5e-4` and are quoted at four. The Chapter 3 statistic is the exception:
`TestLagSettingDetour::test_fixed_lag_reproduces_the_book` holds that same
statistic at `abs=5e-4`, so row 4 quotes −3.0875 and cites that assertion
rather than the two-decimal pin on the same quantity.

That exception carries weight. Row 4's verdict turns on a margin of 0.0055
against Chan's own printed critical values, and at two decimals the margin
would print as 0.01, nearly double the real one.

Two quantities are derived rather than stated: a gap, which the vocabulary
defines as exactly that difference, and a rejection margin, which is a
statistic minus a critical value. Neither is a published figure, so neither
meets the design doc's cut on recomputing a published number in prose. No
published figure is recomputed in any entry.

A gap runs computed minus published, so a negative gap means this repo landed
below the book. The vocabulary names a gap's two operands without fixing their
order, which leaves a reader to guess, so the column header states the
direction and every row follows it.

A gap is stated at the precision both sides support, which is the coarser of
the two, and it is rounded from the engine's full value rather than from the
quoted one. Subtracting two already-rounded numbers moves a gap by up to a full
unit of the last digit, which is how Entry 1's row 3 gap of −0.10 would
otherwise print as −0.09. Row numbers restart per entry, so a reference to one
outside its own entry names the entry too.

### How a verdict is chosen

The vocabulary defines three verdicts and does not say how to pick between
them. Without a rule the obvious choices contradict each other: row 1 misses by
−0.0387 and row 6 misses by −0.0371, a smaller distance, and they do not get
the same verdict.

The rule is this. **A verdict says whether the claim the published figure was
printed to support survives on this repo's vintage.** How far the number moved
does not decide it.

1. **reproduced.** The claim survives and the number lands where the
   specification and the vintage predict.
2. **reproduced with a gap.** The claim survives, the number differs, and the
   difference has a named cause outside the method. A vintage nobody holds is
   that cause here.
3. **did not reproduce.** The number differs and no such cause is available.
   The source's own saved data is the sharpest case of this, because there the
   vintage explanation is spent.

That is why rows 1 and 6 part. Row 1 runs on a modern download and misses a
figure computed from a 2007 series no surviving file carries, so the cause is
named and outside the method. Row 6 re-runs Chan's own saved spreadsheet
through the same specification and still misses the number he printed from it.
Nothing is left to blame, which is the harder failure and the worse verdict.

The rule also settles the two CADF rows, which carry gaps of −0.10 and +0.0940
and still reproduce. Chan's claim is that the pair rejects the no-cointegration
null at a stated level. Both rows reject at that level, so the claim survives.

Two more verdict values suggest themselves and are not adopted. `reproduced
exactly` is not needed, because a gap of 0.0000 already says it in the column
built for it. `not a replication` is not a verdict at all, for the reason
below.

### Rows that are not replications

The vocabulary defines a replication as an attempt to reproduce a specific
published number. A row with no published number is therefore not a
replication, and it can carry neither a gap nor any of the three verdicts.
Entry 1's rows 2 and 10 are in that position, as are Entry 2's rows 6, 7 and 8
and Entry 3's rows 10, 13 and 14, and each verdict cell says so rather than
reaching for a fourth value.

A row with no published *number* can still be a replication, which is the case
[docs/design.md](design.md) covers by saying that where a source states a
ranking or a verdict, the claim is what gets pinned. Entry 3's rows 12 and 15
are both of those, and they take opposite verdicts.

They are in their entries because leaving them out misleads. Row 2 is the slope
from the test's own regression, and a reader who compares it against 1.6766 is
comparing two specifications. Row 10 is what the book's pair looks like twenty
years on, which is the result that makes the shelf life visible.

Row 11 is the opposite case and stays a replication. Chan prints three
statistics there, so there is something to reproduce. The figures reproduce and
the conclusion he drew from them does not, so the verdict stays with the
figures and the reason column carries the refutation.

### What a second entry does to this file

A second entry is a new `## Entry N` section below the last one, with the same
three tables and its own numbered rows, restarting at 1. The sections above are
shared and are not restated per entry. Entry 2 is the first of these and what
follows was written before it, so each point below now names what the entry
actually did.

Three things about the shape are deliberate.

- **A vintage column can be empty, and says so rather than going blank.** The
  coin-flip game is synthetic. It has no vendor and no download date, so the
  column that makes a row checkable has nothing to hold. Such a row writes
  `none, synthetic` rather than going blank, because a blank cell reads as an
  omission. Every row of Entry 2 does.
- **A column with nothing to hold in any row is dropped rather than filled.**
  Entry 1's computed table carries a Window column, because a window is what
  selects the rows a vintage is read over. A gamble has no window in any row,
  so Entry 2's table has five columns where Entry 1's has six. The vintage
  column survives the same test because `none, synthetic` is information and an
  empty window is not.
- **A negative-results log stays a separate document.**
  [docs/design.md](design.md) names one as a candidate. It records an
  idea that was killed, which is a different object from a published figure
  that was chased, so it does not fit these columns and would not share this
  file.

## Entry 1: GLD/GDX and KO/PEP, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, `example7_2.m`, `example3_6_1.m` and
`example7_3.m`. Shipped under
[issue 4](https://github.com/l3a0/quantitative-trading/issues/4), which covered
four reproduced experiments in one piece of work.

Both pairs are in one entry on purpose. KO/PEP is the pair that reproduces to
the digit and GLD/GDX is the pair with the gap, so an entry carrying either
alone would report only matches or only misses. The design doc's
considered-and-rejected register cuts the first of those outright.

Eleven rows, and all of them are derivable from
[tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py).

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | GLD/GDX hedge, Chapter 7 window, through the origin | 1.6766 | Kindle location 3727 |
| 2 | GLD/GDX hedge, Chapter 7 window, with an intercept | none, Chan prints no with-intercept slope | n/a |
| 3 | GLD/GDX CADF statistic, Chapter 7 window | −3.357, reported as better than 95% | no location, absence recorded in the book notes, value kept in `BOOK_REF_FULL` |
| 4 | GLD/GDX CADF statistic, Chapter 3 window | −3.18156477, quoted in his prose as −3.18 and reported as better than 90% | Kindle location 3718 |
| 5 | GLD/GDX mean-reversion half-life | about 10 days | Kindle location 4226 |
| 6 | GLD/GDX hedge from Chan's own archive, through the origin | 1.6766, the same figure as row 1 | Kindle location 3727 |
| 7 | KO/PEP hedge, through the origin | 1.0114 | no location, absence recorded in the book notes, value kept in `KOPEP_REF` |
| 8 | KO/PEP CADF statistic | −2.14258438, quoted in `KOPEP_REF` as −2.14 and reported as not cointegrating | no location, absence recorded in the book notes, value kept in `KOPEP_REF` |
| 9 | KO/PEP daily-return correlation | 0.4849, reported as statistically significant | Kindle location 3838 |
| 10 | GLD/GDX CADF statistic, full modern span | none, the book stops in 2007 | n/a |
| 11 | Chan's Python-versus-MATLAB disagreement | −2.4 from his Python run and −3.2 from his R run, against the −3.18156477 of row 4 | Kindle locations 3755 and 3806 |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 2006-05-23 to 2007-11-30 | OLS through the origin, no intercept, Chan's `ols(GLD, GDX)` | `gld_20yr_prices_unadjusted.csv` and `gdx_20yr_prices_unadjusted.csv`, yfinance raw closes, both downloaded 2026-08-27 | 1.6379 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 2 | 2006-05-23 to 2007-11-30 | OLS with an intercept, the cointegrating regression the test itself runs | same two files as row 1 | 1.3905, intercept 9.9361 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 3 | 2006-05-23 to 2007-11-30 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 1 | −3.45 | `TestGldGdxReproduction::test_ch7_hedge_and_stat` |
| 4 | 2006-05-23 to 2007-05-23 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 1 | −3.0875 | `TestLagSettingDetour::test_fixed_lag_reproduces_the_book` |
| 5 | 2006-05-23 to 2007-11-30, both runs | Ornstein-Uhlenbeck half-life of the with-intercept residual spread | two vintages, run separately: the two raw yfinance files of row 1, and `gld_chan.csv` with `gdx_chan.csv`, saved 2007-12-02 | 10.6 on the yfinance raw closes, 10.3 on Chan's archive | `TestGldGdxReproduction::test_ch7_hedge_and_stat` and `TestGldGdxChanArchive::test_reproduces_chans_archive` |
| 6 | 2006-05-23 to 2007-11-30 | OLS through the origin, no intercept, the same specification as row 1 | `gld_chan.csv` and `gdx_chan.csv`, the adjusted-close columns of Chan's own `GLD.xls` and `GDX.xls`, saved 2007-12-02 | 1.6395 | `TestGldGdxChanArchive::test_reproduces_chans_archive` for the value, and `test_hedge_is_not_the_lost_book_vintage` for the distance only, since that one asserts a two-sided bound of more than 0.03 away from 1.6766 rather than a number, and carries no direction |
| 7 | 1977-01-03 to 2008-01-18 | OLS through the origin, no intercept | `ko_chan.csv` and `pep_chan.csv`, the adjusted-close columns of Chan's own `KO.xls` and `PEP.xls`, saved 2008-01-23 | 1.0114 | `TestKoPepNonCointegration::test_hedge_matches_chan_exactly` |
| 8 | 1977-01-03 to 2008-01-18 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 7 | −2.14 | `TestKoPepNonCointegration::test_fails_to_cointegrate` |
| 9 | 1977-01-03 to 2008-01-18 | Pearson correlation of daily returns, returns divided by the earlier price, two-sided significance on n−2 degrees of freedom | same two files as row 7 | 0.48492, with t = 49.0707 | `TestKoPepNonCointegration::test_returns_are_correlated` |
| 10 | 2006-06-19 to 2026-06-16 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | `gld_20yr_prices.csv`, downloaded 2026-06-16, and `gdx_20yr_prices.csv`, downloaded 2026-08-27, both Yahoo dividend-adjusted. Two files and two dates, so naming one of them cannot re-derive the row | −1.45, with a half-life of 833.5 | `TestGldGdxReproduction::test_full_span_fails_to_reject` |
| 11 | 2006-05-23 to 2007-05-23 | the same residual spread as row 4, tested twice: once at `autolag='aic'`, which picks 6 lags, and once at the fixed lag of 1 that MATLAB and R use | same two files as row 1 | −2.2979 at 6 lags and −3.0875 at 1 lag | `TestLagSettingDetour::test_the_default_lag_choice_flips_the_verdict` and `::test_fixed_lag_reproduces_the_book` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0387 | reproduced with a gap | The claim survives on rows 3 and 4, which reject the no-cointegration null. The number does not, and the cause is named and outside the method: Chan read a 2007-vintage adjusted series, and nineteen years of GDX distributions have rescaled that history since, so no modern download reaches it. |
| 2 | none | none, not a replication | The book prints no with-intercept slope, so there is nothing to reproduce. The row exists so that 1.3905 is not read against 1.6766, which would compare two specifications rather than two vintages. |
| 3 | −0.10 | reproduced | Chan reports better than 95% confidence. The computed statistic clears the 5% critical value under both tables in play, −3.34 from `EG_CRIT_N2` in the tree and −3.380 from the MATLAB printout quoted at location 3718, so the level he states survives. That printout is from his Chapter 3 run, and these are asymptotic values, so reading it across to this window is sound. |
| 4 | +0.0940 | reproduced | Chan reports better than 90% and not 95%, which is exactly the band the computed statistic lands in. It clears the 10% value and misses the 5% one under both tables. The margin is what the verdict rests on, and the two tables disagree about how thin it is: −0.0475 against `EG_CRIT_N2`'s −3.04, which is the only critical table in the tree, and −0.0055 against the −3.082 his MATLAB printed at location 3718, which survives only as quoted highlight text. Same verdict, and under his table the margin is smaller by a factor of 8.6. This row cites `EG_CRIT_N2` as the table it used. |
| 5 | not statable, the source gives one significant figure | reproduced | Both computations land on about 10 days. Two vintages that disagree on the hedge agree on the half-life, which is the evidence for which of the two estimates is fragile. |
| 6 | −0.0371 | did not reproduce | A smaller distance than row 1 and a worse verdict, because the vintage explanation is spent. This is Chan's own saved spreadsheet, re-run through his own specification, missing the number he printed from it. The 2007 book-run series is a state no surviving file carries, his included. |
| 7 | 0.0000 | reproduced | The same code, on a vintage that was not lost, lands on the printed digits. This is the counterpart to row 1 and the reason the GLD/GDX gap is a vintage story rather than a broken implementation. |
| 8 | 0.00 | reproduced | Chan's claim is that the pair does not cointegrate. The computed statistic sits well above `EG_CRIT_N2`'s 10% value of −3.04, so it fails to reject and the claim survives. |
| 9 | 0.0000 at four decimals | reproduced | Chan's claim is that the correlation is statistically significant. It clears the 5% level two-sided by a wide margin. Together with row 8 this is the demonstration that correlation and cointegration are different things. |
| 10 | none | none, not a replication | The book stops in 2007, so there is no published figure. What the row shows is the shelf life: the statistic fails to reject at 10% and the half-life runs to 833.5 days against the about 10 of row 5. |
| 11 | +0.1 against his −2.4, and +0.1 against his −3.2 | reproduced | Both of Chan's figures reproduce, and the conclusion he draws from them does not. He concludes that Python's statistics and econometrics packages are not to be trusted. One Python library produces both statistics here, and the only thing separating them is which lag the test uses. |

### What the entry concludes

Four things, in the order of how much they cost to learn.

1. **The pair's verdict reproduced and its hedge ratio did not.** Rows 3, 4
   and 8 land the rejection levels Chan states, row 5 lands his half-life, and
   row 9 lands his correlation. Rows 1 and 6 miss his hedge. A published number
   and the claim it supports have different shelf lives, and only the number
   depends on a vintage.
2. **Chan's own saved data misses his own printed figure.** Row 6 is the
   receipt. It removes the obvious reply to row 1, that the reproduction is
   simply wrong, and it puts the 2007 book-run series beyond reach of any file
   that still exists.
3. **Chan's conclusion about Python is refuted by his own numbers.** Row 11 is
   the most useful verdict here. His −2.4 and his −3.2 both reproduce, from one
   library, on one window, on one spread. What separates them is
   `autolag='aic'` picking six lags where MATLAB and R fix one, and each added
   lag pulls the statistic toward zero. A conclusion about a library turns out
   to be a conclusion about a default.
4. **The relationship itself has expired.** Row 10 is not a replication and is
   the reason the entry does not end on a match.

Every computed figure here agrees with
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md),
which carries a four-row summary of the same comparison and compresses the two
CADF windows into one cell. The two-run table's published figures agree too,
and one of them took a correction to get there.

That essay's two-run table once gave the published hedge as 1.6766 on its
Chapter 3 row as well as its Chapter 7 row. The book prints 1.6766 for the
Chapter 7 window only, at location 3727. The Chapter 3 window's through-origin
slope is 1.6283, pinned by `TestGldGdxReproduction::test_ch3_hedge_and_stat`,
and it has no published counterpart at all. Reading one published hedge onto
both windows is the exact trap this replication exists to make visible. The
cell now reads `none` in both copies of the essay, the second being
[docs/gld-gdx-cointegration-lessons.html](gld-gdx-cointegration-lessons.html),
corrected under
[issue 27](https://github.com/l3a0/quantitative-trading/issues/27).

One smaller wording difference is worth naming rather than leaving for a reader
to trip on. The essay says Chan's own data "lands at 1.6395, which is no closer
to his printed figure". Rows 1 and 6 give the two distances as 0.0387 and
0.0371, so 1.6395 is nearer by under two thousandths. The essay rounds that to
nothing, which is fair at its granularity, and the rows state both distances
because the verdict rule turns on them.

### Two counts and two senses of one word

Both are ambiguous in the code this entry quotes, so the entry says which it
means.

**Which count.** A run of `python -m chan.pair_cointegration --ch7` reports 385
aligned trading days and 383 ADF observations. The difference is one day to
difference the spread and one more for the lag, so the two counts are not
interchangeable and a row has to say which it means. The window column above
gives date spans rather than counts, because a row's count depends on what that
row computes.

- A hedge ratio is an OLS fit over every aligned trading day: 385 for rows 1, 2
  and 6, and 7835 for row 7. The suite asserts none of these four.
- A CADF statistic is an ADF fit, two observations shorter at the fixed lag of
  1 that these rows use: 383 for row 3, 250 for row 4, 7833 for row 8, and 5028
  for row 10. The suite pins all four.
- Row 5's half-life is an AR(1) regression on the same spreads as rows 3 and 6.
- Row 9 is neither. It runs on 7834 daily returns with 7832 degrees of freedom,
  which is what its pinned t of 49.0707 carries.
- Row 11 is two runs and two counts. The fixed-lag run has the 250 observations
  of row 4. The `autolag='aic'` run drops five more to its six lags and has
  245, which the suite does not assert, because
  `test_the_default_lag_choice_flips_the_verdict` pins the lag and the statistic
  and discards the count.

**Which sense of verdict.** The same run prints `Verdict: REJECTS the
no-cointegration null`, which is the statistical sense: what the test concluded
about one spread. Every use of the word in this file is the vocabulary's sense
instead: the written conclusion of a replication, one of three values, chosen
by the rule above. The statistical sense appears here only inside the reason
column, where it is the thing the vocabulary's verdict is judging.

### What the citations do not cover

Every computed number above names an assertion, and the assertion holds less
than the row might suggest.
[Issue 10](https://github.com/l3a0/quantitative-trading/issues/10) lists what
survived a mutation pass over the ported suite. Three of its findings look as
though they sit under the rejection levels this entry quotes. Re-running them
says one does, one is narrower than the issue claims, and one does not reach
these rows at all.

1. `EG_CRIT_N2` is protected only by accident, through window counts in the
   rolling tests. Nothing asserts the three values themselves, so the table the
   rows compare against could be moved with the suite green.
2. The specification a row names is held, and by exactly one assertion.
   Forcing the ADF regression term from `n` to `c` moves the Chapter 7
   statistic by 0.0042, well inside every `abs=1e-2` pin, and the one test that
   fails is `TestLagSettingDetour::test_fixed_lag_reproduces_the_book`, whose
   `abs=5e-4` pin on −3.0875 is tight enough to catch it. Forcing the term to
   `ct` fails eleven tests. Issue 10's body says all three terms leave the
   suite green, which running them does not bear out, and that correction is
   recorded on the issue.
3. `_verdict` has no test either, and reversing its level order so that every
   rejection reports the weakest level goes unnoticed. That one does not reach
   these rows. `_verdict` formats the CLI's report, and every rejection claim
   above traces instead to a test comparing the statistic against `EG_CRIT_N2`
   directly, such as `assert ch7.adf_stat < EG_CRIT_N2["5%"]`.

So a row saying the statistic rejects at the 5% level traces to a real
assertion, and the one thing that assertion would not notice is the critical
table moving underneath it. Closing that pin belongs to issue 10 rather than to
this entry.

### The chapter labels are first-edition shorthand

The rows call one window the Chapter 7 window and the other the Chapter 3
window, which is this repo's naming throughout, taken from the first edition's
`example3_6_1.m` and page 63. That naming does not survive into the edition
committed here, and
[issue 12](https://github.com/l3a0/quantitative-trading/issues/12) settled it.

The notes in [research/book-notes](../research/book-notes/README.md) are the
2021 revised edition. In it the two printouts sit nine Kindle locations apart,
at 3718 and 3727, under one worked example introduced at location 3678 as
teaching both the cointegration test and the hedge ratio. Chan writes at
location 1862 that Chapter 3 defers the training-set analysis to Chapter 7
rather than performing it. So there is no two-chapter split in that edition.

What the rows rest on is untouched by this, and the distinction is the point.
The separation that matters is between two regression specifications, `cadf`
with an intercept against a through-origin `ols`, and that comes from the
MATLAB package rather than from the book's structure. Chapter numbering was
never load-bearing for a single pinned figure.
[docs/design.md](design.md) carries the full argument.

The labels stay, because the windows they name are unambiguous whatever the
chapters are called, and every row already carries its own date range and price
basis. What changed is that they are declared shorthand rather than left to
look like the book's own structure. The
windows themselves are unambiguous whatever the chapters turn out to be, since
each row gives its dates.

### Nothing checks this file against the suite

Nothing compares the numbers in this document against the assertions they name.
[tests/test_markdown_hygiene.py](../tests/test_markdown_hygiene.py) sweeps
formatting only, so a re-pin that moves a number leaves this entry stale and
the suite green. Whether that guard gets built is the decision on
[issue 6](https://github.com/l3a0/quantitative-trading/issues/6).

Until then this file joins the re-pin sweep by hand. A change to any assertion
named above moves the entry that cites it in the same commit. For Entry 1 that
carries both copies of the essay too, which quote the same figures at coarser
granularity:
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md)
and the published
[docs/gld-gdx-cointegration-lessons.html](gld-gdx-cointegration-lessons.html).
Missing the second is the easy slip, because it is a hand-maintained copy that
no build step regenerates. 1.6766 now appears on eleven tracked files and
1.6379 on ten.

## Entry 2: the coin-flip gamble, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Example 6.1. Shipped under
[issue 13](https://github.com/l3a0/quantitative-trading/issues/13).

The name is a revised-edition label, and this entry declares it because the
repo reads every other one as first-edition. It comes from the book's own prose
at Kindle location 3186, "As Example 6.1 shows". The first-edition code mirror
this repo cites for `example7_2.m` and `example7_3.m` carries `example6_2.xls`
and `example6_3.m` and no `example6_1` in any form, so there is no companion
file to check the arithmetic against. The printed prose is the whole source.

Eight rows, all derivable from
[tests/test_coin_flip_growth.py](../tests/test_coin_flip_growth.py). Three
carry no published figure and say so in their own cells: row 6 is the exact
discrete rate the book does not print, row 7 states the ensemble side in log
units, and row 8 compounds those two against each other, the ensemble side over
the exact discrete rate, into the capital comparison that makes the argument
visible.

**The vintage column says `none, synthetic` in every row.** A gamble has no
vendor and no download date, so the column that makes every other row checkable
has nothing to hold. Leaving it blank would read as an omission.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Expected gain per round, with infinite capital | \$5 | Kindle locations 3176 and 3186, which print it twice |
| 2 | Expected return of one round | 0.005 | location 3186 |
| 3 | Standard deviation of that return | 0.105 | location 3186 |
| 4 | Expected growth rate, continuous approximation | −0.0005125 per round | location 3186 |
| 5 | The rescaling, worked | \$2,000 of capital wins \$220 or loses \$200 | location 3186 |
| 6 | Exact discrete growth rate | none, the book gives only the continuous approximation | n/a |
| 7 | Ensemble average in log units | none, the book prints the simple return | n/a |
| 8 | Capital after 1,000 rounds, the ensemble side against the exact discrete rate | none, the book works no horizon | n/a |

### What this repo computed

| # | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | Half the win less half the loss, at the starting capital | none, synthetic | \$5.00 | `TestBookFigures::test_expected_gain_is_five_dollars` |
| 2 | Mean of the two equally likely returns, +0.11 and −0.10 | none, synthetic | 0.005 | `TestBookFigures::test_expected_return_and_standard_deviation` |
| 3 | Population standard deviation over those two outcomes, not the sample form | none, synthetic | 0.105 | `TestBookFigures::test_expected_return_and_standard_deviation` |
| 4 | `g = m - s^2 / 2` on that mean and that standard deviation | none, synthetic | −0.0005125 | `TestBookFigures::test_the_growth_rate_reproduces_to_the_digit` |
| 5 | The stake the rescaling implies, as a fraction of capital at any level | none, synthetic | exactly 1/10, against a break-even stake of 1/11 | `TestBookFigures::test_the_stake_is_exactly_a_tenth` and `::test_the_gamble_sits_just_past_break_even` |
| 6 | `0.5 * ln(1.11) + 0.5 * ln(0.90)` | none, synthetic | −0.00050025 | `TestTheNearMisses::test_the_exact_discrete_rate_is_a_different_number` |
| 7 | `ln(1 + m)`, so both averages are per-round log rates | none, synthetic | +0.0049875 | `TestBookFigures::test_the_two_averages_disagree_in_sign` |
| 8 | `ensemble_log_growth` and `growth_exact` each compounded from \$1,000 over 1,000 rounds | none, synthetic | \$146,576 against \$606, a ratio of 241.72 | `TestTheCapitalDiverges::test_the_capital_a_reader_sees_at_a_thousand_rounds`, `::test_the_gap_widens_with_every_round` and `::test_the_time_average_path_is_the_median_path` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | \$0, the book prints one significant figure | reproduced | Chan's claim is that a player with infinite capital collects \$5 a round. The figure is exact and nothing can move it. |
| 2 | 0.000 at the three decimals the book prints | reproduced | Exact at that precision. |
| 3 | 0.000 at the three decimals the book prints | reproduced | Exact at that precision, and the specification is what the row holds. The sample form over two outcomes gives 0.14849 instead, which the suite pins as the near miss it is. |
| 4 | 0.0000000 | reproduced | The replication. Chan's claim is that the growth rate is negative while the expected return is positive, so the layman refusing the gamble is right. It reproduces at the seven decimals he prints, and the claim survives with it. |
| 5 | not statable, the source works an illustration rather than a figure | reproduced | Chan's claim is that adjusting the payoff keeps the return moments constant as capital moves. It does, and the stake it implies is exactly a tenth, so the word "roughly" in any paraphrase is doing no work. |
| 6 | none | none, not a replication | The book prints only the continuous approximation. The row exists so −0.00050025 is not read as a failure to reproduce −0.0005125: it is a different quantity, computed exactly, differing at the fourth significant digit. |
| 7 | none | none, not a replication | Derived so the two averages can be compared. The book's own two figures are not in one unit, since 0.005 is an arithmetic mean simple return and −0.0005125 is a log growth rate. |
| 8 | none | none, not a replication | The book works no horizon. This row is what makes the argument visible, and the reason the entry does not end on a rate. |

### What the entry concludes

Four things, and the first is why a verdict here carries less than it looks.

1. **The verdict was knowable before the work started.** A verdict says whether
   the claim a published figure supports survives on this repo's vintage, and a
   vintage is the mechanism that moves a number. There is none, so nothing
   could have moved it and rows 1 to 5 could only reproduce. What this entry is
   worth is rows 7 and 8, not its verdict column.
2. **The book prints no formula, so the formula is what rows 3 and 4 hold.**
   Three plausible choices give three numbers, and only one reproduces all four
   of Chan's figures at once. The sample standard deviation gives −0.006025, out
   by a factor of 11.8 and still printing as a small negative number. The exact
   discrete rate gives −0.00050025. Both are pinned, because an assertion on
   −0.0005125 alone would hold a number rather than a choice.
3. **The two rates do not diverge. The capital does.** Both are constants in
   the number of rounds, so a report showing two rates at one horizon shows a
   disagreement in sign and never a divergence. Row 8 of this entry is the
   divergence: the ratio grows as
   `exp((ensemble_log_growth - growth_exact) * n)`, and it reaches 241.72 by
   1,000 rounds. That exponent rounds to 0.005488 per round, which is a
   rounding of the rate and not the recipe the ratio comes from. Multiplying
   the rounded figure by 1,000 gives 241.77 instead.

   What the ensemble side is set against changes between the two rows, and
   what each row is for is the reason. Row 7 of this entry states that side in
   log units so it can be compared against the continuous approximation the
   book prints, which is what row 4 of this entry reproduces. Row 8 of this
   entry compounds a capital instead, and the book works no horizon there, so
   there is no published figure to match and `growth_exact`, the exact
   discrete rate, is the quantity available. It is also the only rate that
   reproduces the median path: at 1,000 rounds that path reaches \$606, where
   the approximation compounds to \$599, a capital no run of the gamble can
   produce.
4. **Neither epistemic label reaches this entry.** The design doc defines
   exploratory as a result produced by looking at the data and registered as one
   whose hypothesis was committed before the number was seen. This spends no
   sample, so the entry says both are inapplicable rather than picking one. A
   reader taking "exploratory" here would think the arithmetic might not hold.

### Why no simulated number is pinned against the book

[src/chan/coin_flip_growth.py](../src/chan/coin_flip_growth.py) also runs a
seeded simulation, and none of its output appears in the tables above. That is
deliberate and worth stating, because a reader expecting a Monte Carlo would
otherwise look for one.

The per-flip standard deviation of the log return is 0.10486, so a growth rate
estimated from a million flips carries a standard error of 1.05e-4 against a
quantity of 5e-4. Chan prints seven decimals. Reaching one part in a hundred
thousand takes about 110 million flips and one part in a million takes about
eleven billion. So the simulation demonstrates the argument and the closed form
is what the book's figures are pinned against.

Two things the suite does pin about it, because a demonstration nobody sized is
a demonstration that works on the seed somebody tried. At 1,000 paths by 1,000
rounds the time average comes out negative on all of the first 200 seeds. At
100 rounds by 200 paths it comes out positive on 56 of them, so more than a
quarter of seeds show no divergence at all. The report prints the standard error
beside the estimate and says when a size cannot resolve the sign, which is a
line a reader sees rather than an exception, because at that size nothing has
failed.

The draw method is part of what a seed means, and the module names it. On seed
7, `rng.integers`, `rng.random`, `rng.binomial` and `rng.standard_normal` give
four different flip sequences. This is the shape row 11 of Entry 1 records,
where a conclusion about a library turned out to be a conclusion about an
`autolag` default.

Nothing checks this entry against the suite either, for the reason Entry 1
states above. A change to any assertion this entry names moves it in the same
commit, and unlike Entry 1 there is no essay to move with it.

## Entry 3: Kelly leverage on SPY, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Example 6.2, with the specification read off his
own `example6_3.m`. Shipped under
[issue 14](https://github.com/l3a0/quantitative-trading/issues/14).

Seventeen rows, all derivable from
[tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py).

**Exactly one figure Chan computed from a series reproduces here, and it is the
dispersion.** He read SPY through 2007-12-28 on a 2008-vintage adjusted series.
This reads a 2026 download of the same symbol over the same dates, so rows 1 to
8 measure eighteen years of restatement with the window held fixed. Rows 1 and
3 to 8 all miss, every one of them high. Row 2 lands on the two decimals he
prints, because a standard deviation is a dispersion rather than a level and
restatement moves it far less. Reading his own workbook is
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138), and the
`reproduced` verdict on the rest belongs there.

Two more rows reproduce and neither reads a series. Rows 9 and 11 are
arithmetic on figures the book prints, so nothing could have moved them.

Five rows carry no published figure and say so in their own cells: row 10 is
this vintage's own account beside the book's, row 13 is the worst day SPY
actually holds, and rows 14, 16 and 17 are three windows the book does not
work. Those three are why the window is an argument, and rows 16 and 17 are the
two that make the case, since between them the leverage runs from a short of
2.82 times equity to a long of 4.90.

Two rows chase a claim rather than a number, which is the shape
[docs/design.md](design.md) names for a source that states a verdict instead of
a figure. Row 12 is Chan's Black Monday conclusion and it survives. Row 15 is
his time-scale independence and it does not.

Every result here is **exploratory** in the design doc's sense, and this is the
first entry where that matters to a reader rather than to a bookkeeper. Its
output is a leverage rather than a statistic, so it is the first result in this
repo that could be mistaken for advice. The report says so on its own last
lines.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | SPY mean annual return | 11.23 percent | Kindle location 2858 |
| 2 | Annualised standard deviation | 16.91 percent | location 2858 |
| 3 | Mean excess return, over a 4 percent risk-free rate the book supplies | 7.231 percent | location 2858 |
| 4 | Sharpe ratio | 0.4275 | location 2858 |
| 5 | Optimal Kelly leverage | 2.528 | location 2858 |
| 6 | Levered compounded growth rate, including financing costs | 13.14 percent | locations 2858 and 2869 |
| 7 | Unlevered compounded growth rate | 9.8 percent | location 2869 |
| 8 | Half-Kelly leverage | 1.26 | location 3083 |
| 9 | The worked example and the rebalancing chain | \$100,000 of equity buys \$252,800, which falls to \$227,520, leaving \$74,720 of equity, resized to \$188,892 | locations 2869 and 3021 |
| 10 | The same account on this run's leverage | none, the book works one leverage | n/a |
| 11 | The leverage a 20 percent one-day tolerance allows | about 1 | location 3083 |
| 12 | Chan's conclusion, that even half-Kelly would not have survived Black Monday | a claim rather than a figure, resting on a 20.47 percent S&P 500 loss on 1987-10-19 | location 3083 |
| 13 | Worst one-day loss in SPY | none, his 20.47 percent is an S&P 500 index figure from six years before SPY existed | n/a |
| 14 | Kelly leverage over the full modern span | none, the book stops in 2007 | n/a |
| 15 | Kelly's independence of time scale, unlike the Sharpe ratio | a claim rather than a figure | location 2858 |
| 16 | Kelly leverage over the 2000 to 2002 bear market | none, the book works one window | n/a |
| 17 | Kelly leverage over the 2003 to 2007 bull market | none, the book works one window | n/a |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 1993-01-29 to 2007-12-28 | simple daily returns on the adjusted close, mean times 252 | `yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv`, yfinance's both-adjustments close, downloaded 2026-09-18 | 11.2948 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 2 | 1993-01-29 to 2007-12-28 | sample standard deviation, dividing by n−1, times the square root of 252 | same file as row 1 | 16.9117 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 3 | 1993-01-29 to 2007-12-28 | the mean less 0.04/252 per day, annualised by 252 | same file as row 1 | 7.2948 percent | `TestChansWindowOnAModernDownload::test_the_moments` |
| 4 | 1993-01-29 to 2007-12-28 | `S = m / s` on rows 3 and 2 | same file as row 1 | 0.4313 | `TestChansWindowOnAModernDownload::test_the_sharpe_ratio_at_a_tolerance_that_holds_the_specification` |
| 5 | 1993-01-29 to 2007-12-28 | `f* = m / s^2` on rows 3 and 2 | same file as row 1 | 2.5506 | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 6 | 1993-01-29 to 2007-12-28 | `g = r + S^2 / 2`, the scalar case of `example6_3.m`'s `g=0.04+F'*C*F/2` | same file as row 1 | 13.3031 percent | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 7 | 1993-01-29 to 2007-12-28 | `g = r + m - s^2 / 2`, with m the excess return of row 3 | same file as row 1 | 9.8648 percent | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 8 | 1993-01-29 to 2007-12-28 | row 5 halved, the convention location 2836 states | same file as row 1 | 1.2753 | `TestChansWindowOnAModernDownload::test_the_kelly_leverage_and_the_growth_rates` |
| 9 | none, the chain reads no series | buy at the book's rounded 2.528, take a 10 percent loss on the position, resize at the same leverage | none, arithmetic on a published figure | \$252,800.00, \$227,520.00, \$74,720.00 and \$188,892.16 | `TestTheWorkedExample::test_the_books_own_chain_reproduces_to_the_cent` |
| 10 | 1993-01-29 to 2007-12-28 | the same chain at row 5's leverage | same file as row 1 | \$255,059.13, \$229,553.22, \$74,494.09 and \$190,003.97 | `TestTheWorkedExample::test_this_vintages_chain_is_a_different_account` |
| 11 | none, both operands are book constants | 0.20 divided by 0.2047 | none, arithmetic on two published figures | 0.977040 | `TestTheStressTest::test_the_tolerance_allows_about_one_times_equity` |
| 12 | 1993-01-29 to 2007-12-28 | row 8 against row 11, which holds exactly while row 5 is above 1.954079 | same file as row 1, for row 5 only | the claim holds, by a margin of 0.60 on the leverage | `TestTheStressTest::test_the_conclusion_has_a_threshold_and_this_run_clears_it` and `::test_the_verdict_turns_over_at_the_threshold_and_not_before` |
| 13 | 1993-01-29 to 2007-12-28 | the minimum of the daily simple returns | same file as row 1 | −7.2473 percent, on 1997-10-27 | `TestTheStressTest::test_black_monday_is_a_book_constant_and_not_a_vintage_figure` |
| 14 | 1993-01-29 to 2026-09-18 | the same specification as rows 1 to 8 | same file as row 1 | mean 11.9982 percent, sd 18.5349 percent, Sharpe 0.4315, `f*` 2.3281 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_full_modern_span_has_no_published_counterpart` |
| 15 | 1993-01-29 to 2007-12-28 | `f*` recomputed on resampled returns, under three named monthly rules | same file as row 1 | 3.7175 on calendar month-ends, 3.7460 dropping the partial final month, 3.6438 on 21-day blocks, against 2.5506 daily | `TestTimeScaleIndependence::test_resampling_is_what_actually_moves_it` and `::test_the_conclusion_does_not_depend_on_which_monthly_rule_is_picked` |
| 16 | 2000-01-01 to 2002-12-31 | the same specification as rows 1 to 8 | same file as row 1 | mean −12.5412 percent, sd 24.2032 percent, `f*` −2.8237 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_bear_window_recommends_a_short` |
| 17 | 2003-01-01 to 2007-12-28 | the same specification as rows 1 to 8 | same file as row 1 | mean 12.2867 percent, sd 13.0081 percent, `f*` 4.8972 | `TestTheWindowMovesItFurtherThanTheVintageDoes::test_the_bull_window_nearly_doubles_it` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.06 percentage points | reproduced with a gap | Chan's claim is that SPY's mean annual return over his span is about 11 percent, and it survives. The number does not, and the cause is named and outside the method: his 2008-vintage adjusted series has been rescaled by eighteen years of distributions since, so no modern download reaches it. |
| 2 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. A standard deviation is a dispersion rather than a level, so restatement moves it far less than it moves a mean, which is the same asymmetry Entry 1's rows 1 and 5 record. |
| 3 | +0.064 percentage points | reproduced with a gap | Row 1's gap, carried through. The risk-free rate is the book's own constant, so nothing else moved. |
| 4 | +0.0038 | reproduced with a gap | Chan's claim is that SPY's Sharpe ratio over his span is a shade above 0.42, and it survives. This row is also what holds the specification: the population dispersion form gives 0.4276 rather than 0.4275 on his own data, and only an assertion tighter than 5.7e-5 can tell the two apart. |
| 5 | +0.023 | reproduced with a gap | The replication. Chan's claim is that the growth-optimal leverage on SPY is about two and a half times equity, and it survives with room. The number does not, for row 1's reason. |
| 6 | +0.16 percentage points | reproduced with a gap | Row 4's gap carried through `S^2 / 2`, which is how 0.0038 on a Sharpe ratio becomes 0.16 percentage points of growth. The formula itself is not among the committed highlights, because location 2849 renders it as an image, so it is recovered from `example6_3.m` rather than quoted. |
| 7 | +0.1 percentage points | reproduced with a gap | Chan's claim is that unlevered growth is below the mean return and levered growth above it, and both survive. Reading `m` as the total return instead of the excess return would put this row four points out, which is a misread symbol that looks like a gap in the data. |
| 8 | +0.02 | reproduced with a gap | Row 5 halved, so its gap halved. |
| 9 | \$0 on all four figures | reproduced | Every number in the chain is arithmetic on the book's own rounded 2.528. Nothing reads a series, so nothing could have moved. Chan's printed \$252,800 is itself derived from that rounded input: the exact leverage he computed buys \$252,775.87, which is the one printed figure his own workbook misses. |
| 10 | none | none, not a replication | The book works one leverage. The row exists so \$255,059.13 is not read against \$252,800 as a failure to reproduce: it is a different account, and the difference is row 5's gap times \$100,000. |
| 11 | not statable, the source gives one significant figure | reproduced | Chan prints "about 1" and 0.20 divided by 0.2047 is 0.977040. Both operands are his. |
| 12 | none, the source states a claim | reproduced | The claim is that even half-Kelly would not have survived Black Monday, and it survives on this vintage. It is thinner than 2.5506 against 1.954079 sounds: on Chan's own workbook the as-traded close gives a leverage of 1.9341, below the threshold, so the price basis alone reverses his conclusion. That is why this repo's usual preference for a series that cannot be restated is set aside here and the adjusted close is read. |
| 13 | none | none, not a replication | SPY's first bar is 1993-01-29 and Black Monday is 1987-10-19, so no SPY vintage of any span can check the book's 20.47 percent. The worst day this window holds is 7.2473 percent, about a third of it, and the row exists so the two are not read as one number. |
| 14 | none | none, not a replication | The book stops in 2007. What the row shows is that nineteen more years of SPY lower the leverage to 2.3281 while leaving the Sharpe ratio at 0.4315, within 0.0002 of the shorter window's. The dispersion rose and the ratio did not move, which is the shape of a claim that has aged better than its number. |
| 15 | none, the source states a claim | did not reproduce | The claim is true in the reading nobody needs and false in the one they do. Under the annualisation in use the factor cancels between the mean and the variance, so the annualised and per-period ratios agree to floating-point noise, exactly and for any factor. Resampling the returns rather than rescaling their moments moves `f*` by 43 to 47 percent, on all three monthly rules, and those sit within 0.11 of each other. No vintage explanation is available, because the same three rules on Chan's own workbook land 43 to 47 percent above his daily figure too. This is the shape of Entry 1's row 11, where a conclusion about a library turned out to be a conclusion about a default. |
| 16 | none | none, not a replication | The book works one window. Kelly recommends a short of 2.82 times equity here, because the mean excess return over these three years is negative, and the row exists because that is the case requirement 10 of the issue was written for: a negative leverage is arithmetic rather than a failure, and neither half-Kelly nor the drawdown comparison carries across the sign change. |
| 17 | none | none, not a replication | The book works one window. Read against row 16 this is the entry's fourth conclusion in two cells: one vintage, one specification, and a leverage running from −2.82 to +4.90 depending only on which five years are read. |

### What the entry concludes

Four things, and the first is what makes the other three worth reading.

1. **Seven numbers moved and no claim did.** Every level Chan computed from a
   series is now higher, by 0.06 percentage points on the mean and 0.023 on the
   leverage, and every statement those numbers were printed to support still
   holds on this vintage. That is the same split Entry 1 found on a different
   pair with a different estimator: a published number and the claim it
   supports have different shelf lives, and only the number depends on a
   vintage. What is new here is the one that did not move. The dispersion of
   row 2 reproduces while the mean of row 1 does not, which says the
   restatement shifted the level of the series and left its shape alone.
2. **The specification is what rows 4 and 7 really hold.** Two choices are
   invisible on the page and each has a plausible wrong answer that does not
   look wrong. On this vintage the population dispersion form moves the Sharpe
   ratio by 5.74e-5 and the leverage by 6.79e-4, so a suite pinning the
   leverage at the three decimals Chan prints passes on either. Reading `m` as the total return moves
   the unlevered growth rate by exactly the risk-free rate, four points, which
   reads as a data gap rather than a misread symbol. Both are pinned, and the
   first is pinned tighter than the precision rule would ask for, which is the
   second instance of the exception Entry 1's row 4 established.
3. **A verdict can have a threshold, and this one does.** Row 12 is a claim
   rather than a figure, so the entry computes the leverage at which it turns
   over rather than reporting two numbers and leaving a reader to compare them.
   The margin is 0.60 on a threshold of 1.954079, and the price basis alone is
   worth 0.59 on Chan's own data. A replication that reported only "2.5506
   against 1.26" would have looked comfortable.
4. **The window moves the answer further than the vendor does.** Inside this
   one vintage the leverage runs from a short of 2.82 times equity over 2000 to
   2002 to a long of 4.90 over 2003 to 2007, a spread of 7.7 against a gap of
   0.023 in row 5. So a leverage reported with no window named mixes sample
   choice and vendor drift, and neither is recoverable afterwards. That is why
   the window is an argument and why the default is Chan's own.

### Figures from Chan's workbook, which nothing here pins

Five quantities quoted in this entry, in
[src/chan/kelly_leverage.py](../src/chan/kelly_leverage.py) and in
[docs/design.md](design.md), come from Ernest Chan's own `example6_2.xls`,
which this repo does not hold. They are measurements of his data rather than
figures he printed, and no assertion in this repo touches any of them. That
workbook is
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138), and
pinning them is what that issue is for.

They are named here rather than left to read as asserted, which is the shape
`README.md`'s `## The write-up` uses for the six figures its essay quotes and
the suite does not hold.

1. **2.5278 and 1.9341**, his exact leverage on his adjusted close and on his
   as-traded close. Everything this entry says about the price basis rests on
   them, including the 0.59 margin in the conclusions and the reversal of his
   own risk conclusion, since 1.9341 is below the 1.954079 threshold this repo
   does compute.
2. **0.427523 and 0.427580**, his Sharpe ratio under the sample and population
   dispersion forms. They are why row 4 says only the sample form prints as the
   0.4275 he published. This repo's own two forms are 5.74e-5 apart on the same
   quantity, which is pinned, so the argument survives without them and the
   demonstration on his own data does not.
3. **\$252,775.87**, his exact leverage times \$100,000 of equity. Row 9 quotes
   it to say the published \$252,800 is arithmetic on a rounded input.
4. **1.68 percentage points**, what SPY's distributions are worth in annual
   mean return on his span. `src/chan/kelly_leverage.py` quotes it as the size
   of the price-basis choice.
5. **The three monthly resampling rules run on his series**, which land 43 to
   47 percent above his daily figure. Row 15 cites them to say no vintage
   explanation is available for the claim it refutes. That row's own numbers,
   on this vintage, are pinned.

### What this entry cannot say

Two things, and both are the absence of a second series rather than an
oversight.

The 20.47 percent of row 12 is checked against nothing. Checking it needs an
S&P 500 index vintage, which is a different symbol and a different deliverable,
so it is cut and pinned in the design doc's register rather than left as
something a later reader might think was forgotten. The same applies to the 4
percent risk-free rate: a Treasury-bill series would move two inputs at once
and leave every gap above unattributable to either.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
unlike Entry 1 there is no essay to move with it.
