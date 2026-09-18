# Replication log

A replication is finished when it reaches a verdict. Until then the repo holds
a reproduced experiment, which is a number sitting next to another number with
nobody saying what the pair means.

This file is where the verdicts live. One entry per replication, one row per
published figure, and every row carrying the five parts
[docs/design.md](design.md#vocabulary) defines: the published figure, the
vintage, what this repo computed, the gap, and the verdict.

Every result here is **exploratory** in the design doc's sense. Reproducing a
published figure spends the sample on a hypothesis someone else already chose,
so an entry can say whether the number reproduces and nothing about whether the
trade works today.

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
  - [The chapter labels follow an open question](#the-chapter-labels-follow-an-open-question)
  - [Nothing checks this file against the suite](#nothing-checks-this-file-against-the-suite)

## How to read an entry

### Two traceability rules

The two columns of numbers come from different places, so one rule cannot cover
both.

1. **Every computed number names the assertion that holds it.**
   [tests/test_pair_cointegration.py](../tests/test_pair_cointegration.py) is
   the single authority for every figure this repo computes about these pairs,
   and the computed column states those figures rather than deriving them.
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

### What precision a number is quoted at

A computed number is quoted at the precision its assertion holds, never past it.

The four CADF statistics are pinned at `abs=1e-2`, so they are quoted at two
decimals even though the engine returns four. The hedge ratios are pinned at
`abs=5e-4` and are quoted at four. The Chapter 3 statistic is the exception:
`TestLagSettingDetour::test_fixed_lag_reproduces_the_book` holds that same
statistic at `abs=5e-4`, so row 4 quotes −3.0875 and cites that assertion
rather than the two-decimal pin on the same quantity.

That exception carries weight. Row 4's verdict turns on a margin of 0.0055
against one of the two critical tables in the tree, and at two decimals the
margin would print as 0.01, nearly double the real one.

A gap is stated at the precision both sides support, which is the coarser of
the two.

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

The rule also settles the two CADF rows, which carry gaps of −0.09 and +0.0941
and still reproduce. Chan's claim is that the pair rejects the no-cointegration
null at a stated level. Both rows reject at that level, so the claim survives.

Two more verdict values suggest themselves and are not adopted. `reproduced
exactly` is not needed, because a gap of 0.0000 already says it in the column
built for it. `not a replication` is not a verdict at all, for the reason
below.

### Rows that are not replications

The vocabulary defines a replication as an attempt to reproduce a specific
published number. A row with no published number is therefore not a
replication, and it can carry neither a gap nor any of the three verdicts. Rows
2 and 10 are in that position, and their verdict cell says so rather than
reaching for a fourth value.

They are in the entry because leaving them out misleads. Row 2 is the slope
from the test's own regression, and a reader who compares it against 1.6766 is
comparing two specifications. Row 10 is what the book's pair looks like twenty
years on, which is the result that makes the shelf life visible.

Row 11 is the opposite case and stays a replication. Chan prints three
statistics there, so there is something to reproduce. The figures reproduce and
the conclusion he drew from them does not, so the verdict stays with the
figures and the reason column carries the refutation.

### What a second entry does to this file

A second entry is a new `## Entry N` section below the last one, with the same
three tables and the same numbered rows. The sections above are shared and are
not restated per entry.

Two things about the shape are deliberate.

- **A vintage column can be empty, and says so rather than going blank.** The
  coin-flip game on
  [issue 13](https://github.com/l3a0/quantitative-trading/issues/13) is
  synthetic. It has no vendor and no download date, so the column that makes
  these rows checkable has nothing to hold. Such a row writes `none, synthetic`
  where every row here writes a file, because a blank cell reads as an
  omission.
- **A negative-results log stays a separate document.**
  [docs/build-plan.md](build-plan.md) names one as a candidate. It records an
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
| 8 | KO/PEP CADF statistic | −2.14, reported as not cointegrating | no location, absence recorded in the book notes, value kept in `KOPEP_REF` |
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
| 6 | 2006-05-23 to 2007-11-30 | OLS through the origin, no intercept, the same specification as row 1 | `gld_chan.csv` and `gdx_chan.csv`, the adjusted-close columns of Chan's own `GLD.xls` and `GDX.xls`, saved 2007-12-02 | 1.6395 | `TestGldGdxChanArchive::test_reproduces_chans_archive` for the value, and `test_hedge_is_not_the_lost_book_vintage` for the direction only, since that one asserts a bound rather than a number |
| 7 | 1977-01-03 to 2008-01-18 | OLS through the origin, no intercept | `ko_chan.csv` and `pep_chan.csv`, the adjusted-close columns of Chan's own `KO.xls` and `PEP.xls`, saved 2008-01-23 | 1.0114 | `TestKoPepNonCointegration::test_hedge_matches_chan_exactly` |
| 8 | 1977-01-03 to 2008-01-18 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | same two files as row 7 | −2.14 | `TestKoPepNonCointegration::test_fails_to_cointegrate` |
| 9 | 1977-01-03 to 2008-01-18 | Pearson correlation of daily returns, returns divided by the earlier price, two-sided significance on n−2 degrees of freedom | same two files as row 7 | 0.48492, with t = 49.0707 | `TestKoPepNonCointegration::test_returns_are_correlated` |
| 10 | 2006-06-19 to 2026-06-16 | ADF at a fixed lag of 1 on the with-intercept residual spread, no deterministic term | `gld_20yr_prices.csv`, downloaded 2026-06-16, and `gdx_20yr_prices.csv`, downloaded 2026-08-27, both Yahoo dividend-adjusted. Two files and two dates, so naming one of them cannot re-derive the row | −1.45, with a half-life of 833.5 | `TestGldGdxReproduction::test_full_span_fails_to_reject` |
| 11 | 2006-05-23 to 2007-05-23 | the same residual spread as row 4, tested twice: once at `autolag='aic'`, which picks 6 lags, and once at the fixed lag of 1 that MATLAB and R use | same two files as row 1 | −2.2979 at 6 lags and −3.0875 at 1 lag | `TestLagSettingDetour::test_the_default_lag_choice_flips_the_verdict` and `::test_fixed_lag_reproduces_the_book` |

### The verdicts

| # | Gap | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0387 | reproduced with a gap | The claim survives on rows 3 and 4, which reject the no-cointegration null. The number does not, and the cause is named and outside the method: Chan read a 2007-vintage adjusted series, and nineteen years of GDX distributions have rescaled that history since, so no modern download reaches it. |
| 2 | none | none, not a replication | The book prints no with-intercept slope, so there is nothing to reproduce. The row exists so that 1.3905 is not read against 1.6766, which would compare two specifications rather than two vintages. |
| 3 | −0.09 | reproduced | Chan reports better than 95% confidence. The computed statistic clears the 5% critical value under both critical tables in the tree, −3.34 from `EG_CRIT_N2` and −3.380 from his own MATLAB printout, so the level he states survives. |
| 4 | +0.0941 | reproduced | Chan reports better than 90% and not 95%, which is exactly the band the computed statistic lands in. It clears the 10% value and misses the 5% one under both tables. The margin is what the verdict rests on, and the two tables disagree about how thin it is: −0.0475 against `EG_CRIT_N2`'s −3.04, and −0.0055 against the −3.082 his MATLAB printed at location 3718. Same verdict, a margin nine times thinner, and this row cites `EG_CRIT_N2` as the table it used. |
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

The entry also contradicts nothing in
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md),
which carries a four-row summary of the same comparison and compresses the two
CADF windows into one cell. One difference in granularity is worth naming. That
essay's two-run table repeats the published 1.6766 on its Chapter 3 row. The
book prints that figure for the Chapter 7 window only, and the Chapter 3
through-origin slope of 1.6283, pinned by
`TestGldGdxReproduction::test_ch3_hedge_and_stat`, has no published counterpart
at all. Reading one published hedge onto both windows is the trap this
replication exists to make visible, and the row granularity here is what keeps
it visible.

### Two counts and two senses of one word

Both are ambiguous in the code this entry quotes, so the entry says which it
means.

**Which count.** A run of `python -m chan.pair_cointegration --ch7` reports 385
aligned trading days and 383 ADF observations. The difference is one day to
difference the spread and one more for the lag. The window column above gives
date spans rather than counts, and where a count matters it is the ADF
observation count, which is what the suite pins: 383 for rows 1, 2, 3, 5 and
6, 250 for rows 4 and 11, 7833 for rows 7 through 9, and 5028 for row 10. The
aligned trading-day counts are two higher in each case and are asserted
nowhere.

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
survived a mutation pass over the ported suite, and three of its findings sit
directly under the rejection levels this entry quotes.

1. `_verdict`, the function that decides which level a statistic clears, has no
   test. Reversing its level order, so that every rejection reports the weakest
   level instead of the most demanding one, changes nothing the suite notices.
2. `EG_CRIT_N2` is protected only by accident, through window counts in the
   rolling tests. Nothing asserts the three values themselves.
3. The ADF regression term can be forced to `c`, `n` or `ct` with the suite
   still green, because on the Chapter 7 window the statistic moves 0.0042,
   well inside the `abs=1e-2` pin.

So a row here that says the statistic rejects at the 5% level traces to a real
assertion, and that assertion would not notice the level being computed
wrongly, the critical table being moved, or the specification changing under
it. Closing those pins belongs to issue 10 rather than to this entry.

### The chapter labels follow an open question

The rows call one window the Chapter 7 window and the other the Chapter 3
window, which is this repo's naming throughout, taken from the first edition's
`example3_6_1.m` and page 63.
[Issue 12](https://github.com/l3a0/quantitative-trading/issues/12) is open on
whether that reading holds against the edition committed here. The notes in
[research/book-notes](../research/book-notes/README.md) are the 2021 revised
edition, the figure this repo calls the Chapter 3 statistic is printed there at
location 3718, which falls in Chapter 7, and Chan writes at location 1862 that
he defers the training-set cointegration analysis to Chapter 7.

The labels stay for now, because renaming them here while the tracker is still
testing the question would make this a fourth surface asserting the answer. The
windows themselves are unambiguous whatever the chapters turn out to be, since
each row gives its dates.

### Nothing checks this file against the suite

Nothing compares the numbers in this document against the assertions they name.
[tests/test_markdown_hygiene.py](../tests/test_markdown_hygiene.py) sweeps
formatting only, so a re-pin that moves a number leaves this entry stale and
the suite green. Whether that guard gets built is the decision on
[issue 6](https://github.com/l3a0/quantitative-trading/issues/6).

Until then this file joins the re-pin sweep by hand. A change to any assertion
named above moves this entry in the same commit, along with the essay, which
quotes the same figures at coarser granularity. 1.6766 now appears on eleven
tracked files and 1.6379 on ten.
