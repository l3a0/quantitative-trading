# Replication log

A replication is finished when it reaches a verdict. Until then the repo holds
a reproduced experiment, which is a number sitting next to another number with
nobody saying what the pair means.

This file is where the verdicts live. One entry per replication, apart from
the one exception the paragraphs below name, and one row per published result, carrying the five parts
[docs/design.md](design.md#vocabulary) defines: the published figure, the
vintage, what this repo computed, the gap, and the verdict. A row usually
matches one published figure to one computation. Four of Entry 1's rows do not,
and each says so in its own cells.

1. Row 2 carries no published figure, because the book prints no
   with-intercept slope.
2. Row 5 reproduces one published figure from two vintages at once.
3. Row 10 carries no published figure, because the book stops in 2007.
4. Row 11 covers the two statistics Chan printed from what he read as one
   disagreement, and they come from two different tests.

Entries 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13 and 14 carry their own, three,
eleven, twelve, five, six, one, three, eight, six, two, eight and seven, and they
are listed in those entries rather than here, because the list is about an entry's rows and not
about the file.

Entry 5 is the one entry that is not a replication. Chan states the claim it
tests without printing a number, so it carries a finding rather than a verdict,
and its tables drop the columns that would hold a published figure, a gap and a
verdict. Entry 6 comes from the same sentence of the book and is a replication,
because the claim it tests is about one series Chan names.

Every result in Entries 1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13 and 14 is **exploratory** in the design
doc's sense. Reproducing a published figure spends the sample on a hypothesis
someone else already chose, and testing a claim the source states does the same, so an
entry can say whether the number reproduces or the claim holds on its vintage
and nothing about whether the trade works today. Entries 2 and 9 spend no
sample at all and are outside that label and its opposite both, which each
states rather than picking one.

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
  - [Which lag count the residuals allow](#which-lag-count-the-residuals-allow)
  - [Two counts and two senses of one word](#two-counts-and-two-senses-of-one-word)
  - [What the citations do not cover](#what-the-citations-do-not-cover)
  - [The chapter labels are first-edition shorthand](#the-chapter-labels-are-first-edition-shorthand)
  - [Nothing checks this file's numbers against the suite](#nothing-checks-this-files-numbers-against-the-suite)
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
  - [What this entry cannot say](#what-this-entry-cannot-say)
- [Entry 4: risk parity against 60/40, Chan's *Quantitative Trading*](#entry-4-risk-parity-against-6040-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-3)
  - [What this repo computed](#what-this-repo-computed-3)
  - [The verdicts](#the-verdicts-3)
  - [What the entry concludes](#what-the-entry-concludes-3)
  - [What this entry cannot say](#what-this-entry-cannot-say-1)
- [Entry 5: the fixed-income candidate, Chan's *Quantitative Trading*](#entry-5-the-fixed-income-candidate-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated)
  - [What this repo computed](#what-this-repo-computed-4)
  - [What each row says](#what-each-row-says)
  - [What the entry concludes](#what-the-entry-concludes-4)
  - [What this entry cannot say](#what-this-entry-cannot-say-2)
- [Entry 6: the CAD/AUD cross rate, Chan's *Quantitative Trading*](#entry-6-the-cadaud-cross-rate-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-4)
  - [What this repo computed](#what-this-repo-computed-5)
  - [The verdicts](#the-verdicts-4)
  - [What the entry concludes](#what-the-entry-concludes-5)
  - [What this entry cannot say](#what-this-entry-cannot-say-3)
- [Entry 7: the equity seasonals, Chan's *Quantitative Trading*](#entry-7-the-equity-seasonals-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-5)
  - [What this repo computed](#what-this-repo-computed-6)
  - [The verdicts](#the-verdicts-5)
  - [What the entry concludes](#what-the-entry-concludes-6)
  - [The third January return the committed file cannot reach](#the-third-january-return-the-committed-file-cannot-reach)
  - [What this entry cannot say](#what-this-entry-cannot-say-4)
- [Entry 8: the Khandani-Lo reversal, Chan's *Quantitative Trading*](#entry-8-the-khandani-lo-reversal-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-6)
  - [What this repo computed](#what-this-repo-computed-7)
  - [The verdicts](#the-verdicts-6)
  - [What the entry concludes](#what-the-entry-concludes-7)
  - [What this entry cannot say](#what-this-entry-cannot-say-5)
- [Entry 9: the survivorship toy, Chan's *Quantitative Trading*](#entry-9-the-survivorship-toy-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-7)
  - [What this repo computed](#what-this-repo-computed-8)
  - [The verdicts](#the-verdicts-7)
  - [What the entry concludes](#what-the-entry-concludes-8)
  - [What this entry cannot say](#what-this-entry-cannot-say-6)
- [Entry 10: the Khandani-Lo reversal at the open, Chan's *Quantitative Trading*](#entry-10-the-khandani-lo-reversal-at-the-open-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-8)
  - [What this repo computed](#what-this-repo-computed-9)
  - [The verdicts](#the-verdicts-8)
  - [What the entry concludes](#what-the-entry-concludes-9)
  - [What this entry cannot say](#what-this-entry-cannot-say-7)
- [Entry 11: the commodity seasonals, Chan's *Quantitative Trading*](#entry-11-the-commodity-seasonals-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-9)
  - [What this repo computed](#what-this-repo-computed-10)
  - [The verdicts](#the-verdicts-9)
  - [What the entry concludes](#what-the-entry-concludes-10)
  - [What this entry cannot say](#what-this-entry-cannot-say-8)
- [Entry 12: post-earnings drift, Chan's *Algorithmic Trading*](#entry-12-post-earnings-drift-chans-algorithmic-trading)
  - [What the book printed](#what-the-book-printed-10)
  - [What this repo computed](#what-this-repo-computed-11)
  - [The verdicts](#the-verdicts-10)
  - [What the entry concludes](#what-the-entry-concludes-11)
  - [What this entry cannot say](#what-this-entry-cannot-say-9)
- [Entry 13: the PCA factor model, Chan's *Quantitative Trading*](#entry-13-the-pca-factor-model-chans-quantitative-trading)
  - [What the book printed](#what-the-book-printed-11)
  - [What this repo computed](#what-this-repo-computed-12)
  - [The verdicts](#the-verdicts-11)
  - [What the entry concludes](#what-the-entry-concludes-12)
  - [What this entry cannot say](#what-this-entry-cannot-say-10)
- [Entry 14: the market and momentum factors, Chan's *Quantitative Trading*](#entry-14-the-market-and-momentum-factors-chans-quantitative-trading)
  - [What the book stated](#what-the-book-stated-1)
  - [What this repo computed](#what-this-repo-computed-13)
  - [The verdicts](#the-verdicts-12)
  - [What the entry concludes](#what-the-entry-concludes-13)
  - [What this entry cannot say](#what-this-entry-cannot-say-11)

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
   Entry 3,
   [tests/test_risk_parity.py](../tests/test_risk_parity.py) holds Entry 4,
   [tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py)
   holds Entries 5 and 6, which come from one sentence of the book and share a
   module,
   [tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py) holds
   Entry 7, [tests/test_khandani_lo.py](../tests/test_khandani_lo.py) holds
   Entries 8 and 10, which are Examples 3.7 and 3.8 and share a module,
   [tests/test_survivorship_bias.py](../tests/test_survivorship_bias.py) holds
   Entry 9,
   [tests/test_commodity_seasonals.py](../tests/test_commodity_seasonals.py)
   holds Entry 11, [tests/test_pead.py](../tests/test_pead.py) holds
   Entry 12, [tests/test_pca_factor.py](../tests/test_pca_factor.py) holds
   Entry 13, and
   [tests/test_momentum_factor.py](../tests/test_momentum_factor.py) holds
   Entry 14.
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
at location 3718. Row 12 quotes the same figure for the same reason.

### What precision a number is quoted at

A computed number is quoted at the precision its assertion holds, never past it.

The CADF statistics of rows 3, 4, 8 and 10 are pinned at `abs=1e-2`, so they
are quoted at two decimals even though the engine returns four. The hedge
ratios are pinned at `abs=5e-4` and are quoted at four. The Chapter 3 statistic
is the exception: `TestLagSettingDetour::test_fixed_lag_reproduces_the_book`
holds that same statistic at `abs=5e-4`, so row 4 quotes −3.0875 and cites that
assertion rather than the two-decimal pin on the same quantity. Row 12, the
same statistic on Chan's own files under `cadf`'s own regression, is held at
`abs=5e-9`, so it quotes all eight decimals the book prints.

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
otherwise print as −0.09. The +0.0035 in its row 12 reason column would print
as +0.0036 the same way, which is the figure
[issue 232](https://github.com/l3a0/quantitative-trading/issues/232) first
quoted. Row numbers restart per entry, so a reference to one
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
Entry 1's rows 2 and 10 are in that position, as are Entry 2's rows 6, 7 and 8,
Entry 3's rows 10, 13, 14, 16, 17 and 29 to 34, and Entry 4's rows 4 to 21, and
each verdict cell says so rather than reaching for a fourth value. Every row of
Entry 5 is in that position too, so that entry drops the verdict column rather
than filling it. So are Entry 6's rows 2 to 6, Entry 7's rows 15 to 18,
Entry 8's row 3, Entry 9's rows 3 to 5, Entry 10's rows 6 to 13, Entry 11's
rows 2 and 6 to 10, Entry 12's rows 10 and 11, Entry 13's rows 11 to 16, and
Entry 14's rows 3 to 9.

A row with no published *number* can still be a replication, which is the case
[docs/design.md](design.md) covers by saying that where a source states a
ranking or a verdict, the claim is what gets pinned. Entry 3's rows 12, 15, 27
and 28 are all of those, and they split two and two. So is Entry 4's row 3,
which is the ranking Qian's two printed figures were printed to support.
Entry 10's row 1 is one too, for the reason Entry 6's row 1 below is: the
claim is about one strategy the book names, and its criterion was declared on
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206) before
any figure was computed. Entry 11's row 3 is one as well. The sidebar's claim
names one trade, and its criterion, a profit in every year from 1995 to 2008,
was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) before any
trade was computed. Entry 13's row 10 is a claim too, and the exception
among them: its criterion was written on
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the
overlap it judges was measured. Round-off would leave two books of one size
the same on every day. Given the MATLAB's 50 longs, the Python's book matches
on none of 752 days and differs in at least 125 positions on each, so the
verdict does not rest on where a threshold sits. Entry 14's rows 1 and 2 are
two more. Location 4014's claim is about factors, and the section names both
MKT and WML, so each is a definite case of it. Their criterion was written on
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22), and the
owner ruled that each factor carries its own verdict, both before any
autocorrelation was computed.

Entry 5's claim does not take that route. Each claim above is about an
instrument its source names, SPY in Chan's Example 6.2 and Qian's own
portfolios. Chan's fixed-income sentence names none, so what Entry 5 tests is a
pair of stand-ins this repo chose, and its result is a finding about them
rather than a verdict on his sentence. His claim is also that such pairs can be
found, and one pair that fails does not refute that.

Entry 6's row 1 does take it. The same passage gives the CAD/AUD cross rate as
its example and says the rate "is quite stationary", which is a definite claim
about one series it names. The owner ruled on 2026-10-02 that the row carries a
verdict, and the criterion was written on
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) before any
statistic was computed, because a criterion chosen after the number is a
search.

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
  omission. Every row of Entry 2 does. Entry 9 reads the tables Chan prints,
  which have a source and no vendor, so its rows write
  `none, the book's printed tables` instead.
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

Twelve rows, and all of them are derivable from
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
| 11 | Chan's Python-versus-MATLAB disagreement, with his R run read as the tiebreak | −2.4 from his Python run, printed in full as t = −2.3591268376687244 with p = 0.3444494880427884 and a through-origin hedge of 1.631009, and −3.2 from his R run, printed in full as t = −3.240868894 with p = 0.004975, against the −3.18156477 of row 4 | Kindle locations 3755 and 3806 for the prose. The code and the full printouts are at pp. 149 to 151 of the revised edition, read by the owner on 2026-10-02 and recorded on [issue 168](https://github.com/l3a0/quantitative-trading/issues/168) rather than in the book notes |
| 12 | GLD/GDX CADF statistic from Chan's own archive, Chapter 3 window | −3.18156477, the same figure as row 4, printed beside an AR(1) estimate of −0.070038 | Kindle location 3718 |

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
| 11 | 2006-05-23 to 2007-05-23 for the Python run and the lag sweep, 2006-05-23 to 2007-11-30 for the R run | Python: `statsmodels` `coint` at its defaults, which is the Engle-Granger test on the with-intercept residual spread at the lag `autolag='aic'` picks. R: Hansen's covariate-augmented Dickey-Fuller regression, the daily change in GLD by OLS on a constant, GLD's lagged level, one lagged change of GLD, and GDX today and yesterday, with the t on the lagged level. GDX enters as its price, so the regression is an error-correction cointegration test whose coefficients imply a hedge. The lag sweep: row 4's spread at `autolag='aic'` and at every fixed lag from 0 to 16 | two vintages, run separately: `gld_chan.csv` and `gdx_chan.csv`, saved 2007-12-02, for both of Chan's runs, and the two raw yfinance files of row 1 for the sweep | On Chan's files, −2.3591 at 6 lags with p = 0.3444, and −3.2409 on 378 residual degrees of freedom, with an implied hedge of 1.6992, and +0.3554 when GDX's daily change replaces its price. On the yfinance raw closes, −2.2979 at 6 lags and −3.0875 at 1 lag, and the sweep clears −3.04 only at 0 and 1 lags | `TestChansPythonRun::test_coint_at_its_defaults_lands_the_printout` and `::test_the_default_picks_six_lags`, and `TestChansRRunIsACovariateAugmentedDickeyFuller::test_the_regression_lands_the_printout`, `::test_the_covariate_went_in_as_a_price` and `::test_the_training_subset_was_not_applied` for Chan's files, and `TestLagSettingDetour::test_the_default_lag_choice_flips_the_verdict`, `::test_fixed_lag_reproduces_the_book` and `::test_the_statistic_is_not_monotone_in_the_lag` for the yfinance raw closes |
| 12 | 2006-05-23 to 2007-05-23 | LeSage's `cadf(GLD, GDX, 0, 1)` as `example3_6_1.m` calls it, reconstructed as `lesage_cadf`: ADF at a fixed lag of 1 on the with-intercept residual spread, with the regression demeaned and its standard error formed as `cadf` forms it | `gld_chan.csv` and `gdx_chan.csv`, the adjusted-close columns of Chan's own `GLD.xls` and `GDX.xls`, saved 2007-12-02 | −3.18156477, with an AR(1) estimate of −0.070038. Row 4's specification gives −3.1780 on the same files | `TestChansPythonRun::test_cadfs_own_regression_lands_matlabs_printout`, `::test_the_port_misses_cadf_by_one_detail_of_its_regression` for −3.1780, and `TestResidualCheckOnChansFiles::test_the_fit_and_its_residuals` for the residual check the reason column quotes |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −0.0387 | reproduced with a gap | The claim survives on rows 3 and 4, which reject the no-cointegration null. The number does not, and the cause is named and outside the method: Chan read a 2007-vintage adjusted series, and nineteen years of GDX distributions have rescaled that history since, so no modern download reaches it. |
| 2 | none | none, not a replication | The book prints no with-intercept slope, so there is nothing to reproduce. The row exists so that 1.3905 is not read against 1.6766, which would compare two specifications rather than two vintages. |
| 3 | −0.10 | reproduced | Chan reports better than 95% confidence. The computed statistic clears the 5% critical value under both tables in play, −3.34 from `EG_CRIT_N2` in the tree and −3.380 from the MATLAB printout quoted at location 3718, so the level he states survives. That printout is from his Chapter 3 run, and these are asymptotic values, so reading it across to this window is sound. |
| 4 | +0.0940 | reproduced | Chan reports better than 90% and not 95%, which is exactly the band the computed statistic lands in. It clears the 10% value and misses the 5% one under both tables. The margin is what the verdict rests on, and the two tables disagree about how thin it is: −0.0475 against `EG_CRIT_N2`'s −3.04, which is the only critical table in the tree, and −0.0055 against the −3.082 his MATLAB printed at location 3718, which survives only as quoted highlight text. Same verdict, and under his table the margin is smaller by a factor of 8.6. This row cites `EG_CRIT_N2` as the table it used. Under `cadf`'s own regression, which row 12 reproduces on Chan's files, these closes give −3.0908 and the margin against his table widens to −0.0088, so the verdict holds under it too. |
| 5 | not statable, the source gives one significant figure | reproduced | Both computations land on about 10 days. Two vintages that disagree on the hedge agree on the half-life, which is the evidence for which of the two estimates is fragile. |
| 6 | −0.0371 | did not reproduce | A smaller distance than row 1 and a worse verdict, because the vintage explanation is spent. This is Chan's own saved spreadsheet, re-run through his own specification, missing the number he printed from it. The 2007 book-run series is a state no surviving file carries, his included. |
| 7 | 0.0000 | reproduced | The same code, on a vintage that was not lost, lands on the printed digits. This is the counterpart to row 1 and the reason the GLD/GDX gap is a vintage story rather than a broken implementation. |
| 8 | 0.00 | reproduced | Chan's claim is that the pair does not cointegrate. The computed statistic sits well above `EG_CRIT_N2`'s 10% value of −3.04, so it fails to reject and the claim survives. |
| 9 | 0.0000 at four decimals | reproduced | Chan's claim is that the correlation is statistically significant. It clears the 5% level two-sided by a wide margin. Together with row 8 this is the demonstration that correlation and cointegration are different things. |
| 10 | none | none, not a replication | The book stops in 2007, so there is no published figure. What the row shows is the shelf life: the statistic fails to reject at 10% and the half-life runs to 833.5 days against the about 10 of row 5. |
| 11 | 0.0000 at four decimals on Chan's files, against both printed t-statistics. On the yfinance raw closes, +0.1 against his −2.4 | reproduced | Every figure both runs print reproduces on Chan's files at the precision printed, apart from R's p-value and its ρ², and the verdict rests there. The yfinance gap is the vintage gap of row 1. The Python claim survives: its p of 0.3444 fails to reject at 10%. The R claim is not settled by its own printout. Its p of 0.004975 comes from Hansen's distribution, which assumes a stationary covariate, and the code passed GDX's price, which fails to reject a unit root. That makes the regression an error-correction cointegration test, so neither Hansen's table nor `EG_CRIT_N2` is its critical value, and nothing here supplies one. Given GDX's daily change, the input Hansen's test is built for, the t is +0.3554, which rejects nothing. The conclusion Chan draws does not survive. He concludes that Python's statistics and econometrics packages are not to be trusted. Python and MATLAB ran one test on one window and differ in the lag count and in a detail of `cadf`'s regression worth 0.0035 at one lag, which row 12 pins, and R ran a different test on a longer window with an input it was not built for, so the disagreement says nothing about Python's packages. `TestChansPythonRun::test_the_fixed_lags_that_matched_the_2026_closes_miss_on_chans` kills three earlier readings: zero fixed lags, which give −3.2018 on the yfinance closes and −3.2975 on Chan's, three fixed lags, which give −2.4067 against −2.4857, and one fixed lag, whose −3.1780 rounds to R's −3.2 but comes from a different test than R ran. |
| 12 | 0.00000000 on the t-statistic and 0.000000 on the AR(1) estimate, at the decimals printed | reproduced | Chan's own files land both figures his MATLAB printed, once `cadf`'s own regression runs. The claim survives too. Chan reports better than 90% and not 95%, and the statistic clears `EG_CRIT_N2`'s −3.04 by 0.1416 and the −3.082 his MATLAB printed by 0.0996, and misses both 5% values. Row 4's specification gives −3.1780 on these files, +0.0035 away, and the difference is how `cadf` forms its regression. It demeans the regressors, charges the constant that implies no degree of freedom, and takes the covariance from the raw regressors. With a constant, row 4's specification matches `cadf`'s coefficient at every printed digit and gives −3.1749, so what is left is the standard error. The detail is inside the method and does not explain row 4's gap: `cadf`'s regression gives −3.0908 on the yfinance closes against −3.0875. The residual check ran on row 4's specification rather than on `cadf`'s. On these files it gives a Breusch-Godfrey p of 0.0460 and residual lag 6 outside the band, which limits what the rejection supports, as it does for row 4, and leaves the verdict alone. |

### What the entry concludes

Four things, in the order of how much they cost to learn.

1. **The pair's verdict reproduced and its hedge ratio did not.** Rows 3, 4,
   8 and 12 land the rejection levels Chan states, row 5 lands his half-life,
   and row 9 lands his correlation. Rows 1 and 6 miss his hedge. A published
   number and the claim it supports have different shelf lives, and only the
   number depends on a vintage.
2. **Chan's own saved data misses his own printed hedge.** Row 6 is the
   receipt. It removes the obvious reply to row 1, that the reproduction is
   simply wrong, and it puts the 2007 book-run series beyond reach of any file
   that still exists. Row 12 lands his Chapter 3 statistic on the same files to
   all eight decimals printed. His Chapter 7 statistic is not in the same
   position: those files give −3.52 over the Chapter 7 window against the
   −3.357 he printed, which no row carries yet, and
   [issue 268](https://github.com/l3a0/quantitative-trading/issues/268) asks
   why.
3. **Chan's conclusion about Python is refuted by his own numbers.** Row 11 is
   the most useful verdict here. His −2.4 and his −3.2 both reproduce on his
   own files, each t-statistic to within a billionth, and they come from two
   different tests on two different windows. His Python run is the
   Engle-Granger test on 252 days, with `autolag='aic'` picking six lags. His
   R run calls Hansen's covariate-augmented Dickey-Fuller test on all 385
   days and passes GDX's price where the test expects a stationary series, so
   its printed p-value does not settle whether it rejects. Chan's MATLAB call,
   as `example3_6_1.m` reads, runs the Engle-Granger test on the same 252 days
   as Python with one lag passed as an argument, so against MATLAB what
   separates Python is mostly the lag count. Row 12 reproduces that MATLAB call
   on his files, so all three printouts reproduce there. The rest is a detail
   of how `cadf` forms its regression, which makes MATLAB's one-lag statistic
   0.0035 more negative than the port's and changes no verdict. On the
   yfinance raw closes the statistic does not weaken steadily as lags are added, since it is more
   negative at four lags than at three. The verdict is what holds there: zero or one lag clears the 10% line
   and every count from two to sixteen misses it. A conclusion about a library
   turns out to be a conclusion about a default and about which test ran.
   Which lag count the test is entitled to is a separate question, taken up
   under
   [Which lag count the residuals allow](#which-lag-count-the-residuals-allow).
4. **The relationship itself has expired.** Row 10 is not a replication and is
   the reason the entry does not end on a match.

Every computed figure here agrees with
[blog/gld-gdx-cointegration-lessons.md](../blog/gld-gdx-cointegration-lessons.md),
which carries a four-row summary of the same comparison and compresses the two
CADF windows into one cell. The two-run table's published figures agree too,
and one of them took a correction to get there. Row 12 has no counterpart in
the essay, whose fifth detour says Chan's files land two of his three numbers.
[Issue 262](https://github.com/l3a0/quantitative-trading/issues/262) carries
the third.

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

### Which lag count the residuals allow

Row 11 shows that the lag count decides the verdict. It does not say which lag
count to believe. The ADF critical values assume the fitted regression leaves
residuals with no autocorrelation. A lag count that leaves some behind reads its
statistic against a table that does not apply, so the test no longer rejects at
the rate it states. Which way the error runs depends on what is left behind. On
this spread, the fits with fewer lags are the ones that reject.

This check is exploratory. It spent the Chapter 3 sample looking, after the
sweep behind row 11 had already been seen.

Each fixed-lag fit on the row 4 spread had its residuals checked at lags 1 to
10, in two ways. Passing means both.

1. Each autocorrelation against a white-noise band of ±1.96/√n, which is
   ±0.1240 at one lag. The band is pointwise. Under white noise each bar has a
   5% chance of leaving it, so one of ten bars outside is common and says less
   than it looks.
2. A Breusch-Godfrey test over the same ten lags, at the 10% cut. It replaces
   Ljung-Box here because the ADF regression carries lagged differences on its
   right-hand side, which is the case Breusch-Godfrey is built for.

[![Five panels of residual autocorrelation at lags 1 to 10, one panel each for ADF fits at 0, 1, 2, 3 and 6 lags. In the first four panels a bar at lag 6 rises above the shaded white-noise band, and in the panel for 2 lags a bar at lag 3 falls below it. In the panel for 6 lags every bar sits inside the band.](figures/adf_residual_autocorrelation.png)](figures/adf_residual_autocorrelation.png)

An autocorrelation at lag 6 of 0.15 to 0.18 survives every fit from zero lags
to five. Six lags is the first count whose residuals pass both checks, with a
Breusch-Godfrey p of 0.8395, and at six lags the statistic is −2.2979, which
does not reject. At one lag, which is the book's specification and the one row 4
reproduces, the Breusch-Godfrey p is 0.0421. So the fit behind Chan's
better-than-90% verdict fails the residual check, and the fit `autolag='aic'`
picks is the one that passes it.

The ten-lag horizon is a choice, so the check was repeated at every horizon
from one to ten. The one-lag fit fails at every horizon from two up, and six
lags pass at all ten. Zero lags is the fit whose verdict turns on the choice,
failing only at horizons six and seven.

Row 4's verdict stands, because it asks whether Chan's number reproduces under
his specification, and it does. What changes is what that number can support.
At the first lag count whose residuals pass, the test does not reject, so the
Chapter 3 window gives no evidence of cointegration on this vintage. That is an
absence of evidence rather than evidence against. The ADF has little power on
245 observations, and a failure to reject is what a weakly cointegrated pair
would also produce. Two more things bear on how far the result reaches.

1. At one lag the lag-6 autocorrelation is 0.1668 against a band of 0.1240, on
   250 observations, near enough the edge that a different vintage could move
   it inside. Chan's own files, the vintage his Python printout reproduces on,
   do not. There the bar is 0.1659 against the same band, the one-lag fit
   fails Breusch-Godfrey with a p of 0.0460, and six lags is again the first
   count that passes, at −2.3591, which does not reject. That six-lag fit is
   the one `coint` runs at its defaults, so the statistic Chan printed and
   distrusted is the one whose residuals pass. The one-lag fit checked here is
   row 4's specification on Chan's files rather than `cadf`'s own regression,
   which row 12 reproduces, and its failure bears on what row 12's rejection
   supports rather than on its verdict.
2. At the 5% cut, Breusch-Godfrey alone passes the fits at zero, two and five
   lags as well, and still fails one lag. What keeps those three out is the
   lag-6 bar outside the band, and the band is the pointwise check.

The same check on the Chapter 7 window, 2006-05-23 to 2007-11-30, gives a
different answer. It ran on two vintages, the yfinance raw closes behind row 3
and Chan's own files, and the two agree on the shape. At one lag, which rejects
at 5% on both, the residuals fail both halves of the check. The Breusch-Godfrey
p is 0.0325 on the yfinance closes and 0.0337 on Chan's files, and the
autocorrelation at lag 10 is 0.1443 and 0.1435 against a band of 0.1002. Every
lag count from zero to nine leaves that lag-10 autocorrelation outside the
band. Ten lags is the first count that passes, with a Breusch-Godfrey p of
0.3861 and 0.3896, and there the test still rejects. On the yfinance closes the
statistic is −3.2965, which clears 10% and misses 5% under both tables. On
Chan's files it is −3.3580, which clears `EG_CRIT_N2`'s −3.34 by 0.018 and
misses the −3.380 his MATLAB printed by 0.022. Its nearness to Chan's printed
−3.357 is a coincidence, since that figure is a one-lag fit on an earlier
vintage.

The lag-10 bar that decides this is the last one the band reads, so the count
of bars is a choice in the way the Breusch-Godfrey horizon is. With the
horizon held at ten, a band reading nine bars lets zero lags pass first, and a
band reading sixteen or more reaches a lag-16 bar and moves the first pass to
sixteen lags. At every setting tried, the first fit that passes rejects at 10%
or better on both vintages. So the check leaves the rejection in row 3
standing, at better than 90% rather than the better than 95% Chan reports.
Row 3's verdict stands for the reason row 4's does, since it asks whether
Chan's number reproduces under his specification.

Zero lags, which `autolag='aic'` and `autolag='bic'` both pick on this window,
clears Breusch-Godfrey and rejects at 5%. One bar at lag 10 keeps it out, and
that bar stays outside even a band widened for reading ten bars at once,
2.807/√n. This check is exploratory too, and it was run after the Chapter 3
result had been seen.

`TestResidualCheck`, `TestResidualCheckOnChansFiles` and
`TestResidualCheckChapter7` in `tests/test_pair_cointegration.py` pin every
number in this section.
`src/chan/lag_residual_figure.py` redraws the figure, and
`tests/test_lag_residual_figure.py` holds that it draws what the check
computes.

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
  1 that these rows use: 383 for row 3, 250 for rows 4 and 12, 7833 for row 8,
  and 5028 for row 10. The suite pins all five.
- Row 5's half-life is an AR(1) regression on the same spreads as rows 3 and 6.
- Row 9 is neither. It runs on 7834 daily returns with 7832 degrees of freedom,
  which is what its pinned t of 49.0707 carries.
- Row 11 holds several runs, each with its own count. On the yfinance raw
  closes, the fixed-lag run has the 250 observations of row 4. The
  `autolag='aic'` run drops five more to its six lags and has 245, which the
  suite does not assert there, because
  `test_the_default_lag_choice_flips_the_verdict` pins the lag and the
  statistic and discards the count. The sweep drops one observation per lag,
  from 251 at 0 lags to 235 at 16, and the suite does not assert those counts
  either. On Chan's files the Python run also has 245, which
  `TestChansPythonRun::test_the_default_picks_six_lags` asserts, and the R
  regression has 383 rows and 378 residual degrees of freedom, which
  `TestChansRRunIsACovariateAugmentedDickeyFuller::test_the_regression_lands_the_printout`
  asserts.

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
   `ct` fails eleven tests. [Issue 10](https://github.com/l3a0/quantitative-trading/issues/10)'s body says all three terms leave the
   suite green, which running them does not bear out, and that correction is
   recorded on the issue.
3. `_verdict` has no test either, and reversing its level order so that every
   rejection reports the weakest level goes unnoticed. That one does not reach
   these rows. `_verdict` formats the CLI's report, and every rejection claim
   above traces instead to a test comparing the statistic against `EG_CRIT_N2`
   directly, such as `assert ch7.adf_stat < EG_CRIT_N2["5%"]`.

So a row saying the statistic rejects at the 5% level traces to a real
assertion, and the one thing that assertion would not notice is the critical
table moving underneath it. Closing that pin belongs to [issue 10](https://github.com/l3a0/quantitative-trading/issues/10) rather than to
this entry.

### The chapter labels are first-edition shorthand

The rows call one window the Chapter 7 window and the other the Chapter 3
window, which is this repo's naming throughout, taken from the first edition's
`example3_6_1.m` and page 63. That naming does not survive into the edition
committed here, and
[issue 12](https://github.com/l3a0/quantitative-trading/issues/12) settled it.

The *Quantitative Trading* notes in
[research/book-notes](../research/book-notes/README.md) are the 2021 revised
edition. In it the two printouts sit nine Kindle locations apart,
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

### Nothing checks this file's numbers against the suite

Nothing compares the numbers in this document against the assertions they name.
[tests/test_markdown_hygiene.py](../tests/test_markdown_hygiene.py) sweeps this
file's formatting and resolves every anchor its Contents carries, and neither
reads a figure, so a re-pin that moves a number leaves this entry stale and
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
Algorithmic Trading Business*, Box 6.1, "Loss aversion is not a behavioral
bias". Shipped under
[issue 13](https://github.com/l3a0/quantitative-trading/issues/13).

The label is a revised-edition one, and this entry declares it because the
repo reads a label as first-edition unless it says otherwise. The gamble sits in Box 6.1 of
Chapter 6, a sidebar the 2009 edition could not hold because it quotes
Kahneman's 2011 book. The box cites a separate Example 6.1 at Kindle location
3186, "As Example 6.1 shows", for the continuous approximation it uses. This
entry called the gamble Example 6.1 until 2026-09-29, misreading that sentence,
and the owner corrected the label against the book. The first-edition code
mirror this repo cites for `example7_2.m` and `example7_3.m` carries
`example6_2.xls` and `example6_3.m` and nothing for Box 6.1, so there is no
companion file to check the arithmetic against. The printed prose is the whole
source.

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
| 6 | none | none, not a replication | The book prints only the continuous approximation. The row exists so −0.00050025 is not read as a failure to reproduce −0.0005125: it is a different quantity, computed exactly, differing at the second significant digit. |
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
   Three candidate formulas give three numbers, and only one reproduces all four
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
quantity of 5e-4. Chan prints seven decimals. Bringing the standard error down
to one part in a hundred thousand takes about 110 million flips, and to one
part in a million about eleven billion. So the simulation demonstrates the argument and the closed form
is what the book's figures are pinned against.

Two things the suite does pin about it, because a demonstration nobody sized is
a demonstration that works on the seed somebody tried. At 1,000 paths by 1,000
rounds the time average comes out negative on all of the first 200 seeds. At
100 rounds by 200 paths it comes out positive on 56 of them, so more than a
quarter of seeds get the sign of the time average wrong. The report prints the
standard error beside the estimate and says when a size cannot resolve the
sign, which is a line a reader sees rather than an exception, because at that
size nothing has failed.

The draw method is part of what a seed means, and the module names it. On seed
7, `rng.integers`, `rng.random`, `rng.binomial` and `rng.standard_normal` give
four different flip sequences. This is the shape row 11 of Entry 1 records,
where a conclusion about a library turned out to be a conclusion about an
`autolag` default.

Nothing checks this entry against the suite either, for the reason Entry 1
states above. A change to any assertion this entry names moves it in the same
commit, and moves
[blog/coin-toss-expected-value-vs-growth.md](../blog/coin-toss-expected-value-vs-growth.md)
with it, since that post quotes the same pins.

## Entry 3: Kelly leverage on SPY, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Example 6.2, with the specification read off his
own `example6_3.m`. Rows 1 to 17 shipped under
[issue 14](https://github.com/l3a0/quantitative-trading/issues/14), rows 18 to
30 under [issue 138](https://github.com/l3a0/quantitative-trading/issues/138),
and rows 31 to 34 under
[issue 192](https://github.com/l3a0/quantitative-trading/issues/192).

Thirty-four rows, all derivable from
[tests/test_kelly_leverage.py](../tests/test_kelly_leverage.py).

**The entry reads three vintages of SPY over Chan's own span.**

1. **Rows 1 to 17 read a 2026 download.** He read SPY through 2007-12-28 on a
   2008-vintage adjusted series, so rows 1 to 8 measure how two downloads
   eighteen years apart differ, with the window held fixed. Rows 1 and 3 to 8
   all miss, every one of them high. Row 2, the dispersion, lands on the two
   decimals he prints.
2. **Rows 18 to 28 read his own `example6_2.xls`**, committed as
   `data/spy_chan.csv`. Every figure he computed from a series reproduces from
   it at the precision he printed it. The one printed figure that does not is
   row 26's \$252,800, because he rounded the leverage to 2.528 before
   multiplying.
3. **Rows 31 to 34 read the same workbook's as-traded `Close`**, committed as
   `data/spy_unadjusted_chan.csv`. Chan printed nothing from it. It shares the
   adjusted column's days and saved date, so it changes the price basis and
   nothing else, and on his data that is enough to reverse his risk
   conclusion.

Rows 29 and 30 set the first two day by day against each other, which is what
says why the first group misses. Dividends paid after his window cannot
explain it, because they scale every price inside it by one factor and leave
every return unchanged. Those two hold the same 3,758 days, and the
whole gap in the mean sits on about ten days on or beside SPY's quarterly
ex-dividend dates. The differences mostly raise the 2026 mean, and the rest of
the days together pull back less than a tenth of the gap. A few large
differences move a mean while barely touching a standard deviation. Row 30 pins
all of that, including that each of the ten falls on a quarter-end month's
third Friday or the trading day after.

Two finer descriptions are measured on
[issue 138](https://github.com/l3a0/quantitative-trading/issues/138) rather
than pinned. On the four largest days, one download folds nearly a whole
quarterly payout into the day's return and the other does not, and on the rest
of the ten it folds in part of one. Outside the ten, the differences are mostly
rounding and a few smaller dividend differences.

Two more rows reproduce and neither reads a series. Rows 9 and 11 are
arithmetic on figures the book prints, so nothing could have moved them.

Eleven rows carry no published figure and say so in their own cells.

- Row 10 is the 2026 download's own account beside the book's.
- Row 13 is the worst day SPY actually holds.
- Rows 14, 16 and 17 are three windows the book does not work. Those three are
  why the window is an argument, and rows 16 and 17 are the two that make the
  case, since between them the leverage runs from a short of 2.82 times equity
  to a long of 4.90.
- Rows 29 and 30 are the first two vintages set against each other.
- Rows 31 to 34 read the as-traded column, which Chan printed nothing from.
  Row 34 is his Black Monday claim tested on that column, and it is not a
  replication because his claim is about the series he read.

Four rows chase a claim rather than a number, which is the shape
[docs/design.md](design.md) names for a source that states a verdict instead of
a figure. Rows 12 and 27 are Chan's Black Monday conclusion, on the 2026
download and on his adjusted column, and it survives on both. Rows 15 and 28
are his time-scale independence, and it fails on both. A fifth row, 34, tests
the Black Monday conclusion a third time, on his as-traded column, where it
fails. It is not among the four and carries no verdict rather than `did not reproduce`, because rows 12 and 27 test
his claim on the series he read and row 34 tests it on a series he did not.

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
| 18 | SPY mean annual return, on Chan's own workbook | 11.23 percent | location 2858 |
| 19 | Annualised standard deviation, on Chan's own workbook | 16.91 percent | location 2858 |
| 20 | Mean excess return, on Chan's own workbook | 7.231 percent | location 2858 |
| 21 | Sharpe ratio, on Chan's own workbook | 0.4275 | location 2858 |
| 22 | Optimal Kelly leverage, on Chan's own workbook | 2.528 | location 2858 |
| 23 | Levered compounded growth rate, on Chan's own workbook | 13.14 percent | locations 2858 and 2869 |
| 24 | Unlevered compounded growth rate, on Chan's own workbook | 9.8 percent | location 2869 |
| 25 | Half-Kelly leverage, on Chan's own workbook | 1.26 | location 3083 |
| 26 | The worked example and the rebalancing chain, on the leverage his own workbook gives | \$252,800, \$227,520, \$74,720 and \$188,892, the same figures as row 9 | locations 2869 and 3021 |
| 27 | Chan's Black Monday conclusion, on his own workbook | the claim of row 12 | location 3083 |
| 28 | Kelly's independence of time scale, on his own workbook | the claim of row 15 | location 2858 |
| 29 | The days the 2026 download and Chan's adjusted column hold over his span | none, the book reads one vintage | n/a |
| 30 | The difference in return between those two over Chan's span | none, the book reads one vintage | n/a |
| 31 | Optimal Kelly leverage, on Chan's own as-traded close | none, the book reads only the adjusted close | n/a |
| 32 | What the price basis is worth on the leverage | none, the book reads one price basis | n/a |
| 33 | What the price basis is worth on the mean annual return | none, the book reads one price basis | n/a |
| 34 | Chan's Black Monday conclusion, on his own as-traded close | the claim of row 12, on a series he did not read | location 3083 |

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
| 18 | 1993-01-29 to 2007-12-28 | row 1's specification | `spy_chan.csv`, the adjusted-close column of Chan's own `example6_2.xls`, saved 2008-01-29 | 11.2307 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 19 | 1993-01-29 to 2007-12-28 | row 2's specification | same file as row 18 | 16.9131 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 20 | 1993-01-29 to 2007-12-28 | row 3's specification | same file as row 18 | 7.2307 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_moments` |
| 21 | 1993-01-29 to 2007-12-28 | row 4's specification | same file as row 18 | 0.427523, against 0.427580 under the population dispersion form | `TestEveryFigureHePrintedReproducesFromHisData::test_the_sharpe_ratio_and_the_dispersion_form_it_decides` |
| 22 | 1993-01-29 to 2007-12-28 | row 5's specification | same file as row 18 | 2.5278 | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 23 | 1993-01-29 to 2007-12-28 | row 6's specification | same file as row 18 | 13.1388 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 24 | 1993-01-29 to 2007-12-28 | row 7's specification | same file as row 18 | 9.8005 percent | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 25 | 1993-01-29 to 2007-12-28 | row 8's specification | same file as row 18 | 1.2639 | `TestEveryFigureHePrintedReproducesFromHisData::test_the_kelly_leverage_and_the_growth_rates` |
| 26 | 1993-01-29 to 2007-12-28 | row 9's chain at row 22's leverage | same file as row 18 | \$252,775.87, \$227,498.28, \$74,722.41 and \$188,880.23 | `TestThePrintedPortfolioOnHisExactLeverage::test_his_exact_leverage_buys_less_than_he_printed` and `::test_rounding_the_leverage_is_the_whole_cause` |
| 27 | 1993-01-29 to 2007-12-28 | row 25 against row 11, which holds exactly while row 22 is above 1.954079 | same file as row 18, for row 22 only | the claim holds, by a margin of 0.57 on the leverage | `TestHisOwnDataOnTheRestOfTheEntry::test_the_black_monday_conclusion_survives_on_his_data` |
| 28 | 1993-01-29 to 2007-12-28 | row 15's three monthly rules | same file as row 18 | 3.6908 on calendar month-ends, 3.7195 dropping the partial final month, 3.6163 on 21-day blocks, against 2.5278 daily | `TestHisOwnDataOnTheRestOfTheEntry::test_the_time_scale_claim_fails_on_his_own_series` |
| 29 | 1993-01-29 to 2007-12-28 | the two indexes intersected, with what each side lost counted | row 18's file and row 1's | 3,758 days in each and 3,758 joined, so the join drops nothing from either side | `TestTheTwoVintagesOverChansWindow::test_the_join_drops_nothing_from_either_side` |
| 30 | 1993-01-29 to 2007-12-28 | simple returns on the joined days, the 2026 download's less Chan's | row 18's file and row 1's | the annual mean differs by 0.0641 percentage points and the standard deviation by 0.0014. The ten largest daily differences carry 108.5 percent of the summed difference, eight raising the 2026 mean and two lowering it. Each of the ten falls on a quarter-end month's third Friday or the trading day after, and days in SPY's quarterly dividend months carry 100.4 percent | `TestTheTwoVintagesOverChansWindow::test_the_gap_in_the_mean_and_the_dispersion_that_does_not_move`, `::test_ten_days_carry_the_whole_gap_and_dividend_months_carry_it_too` and `::test_the_ten_days_are_all_quarterly_ex_dividend_days` |
| 31 | 1993-01-29 to 2007-12-28 | row 5's specification | `spy_unadjusted_chan.csv`, the as-traded `Close` column of Chan's own `example6_2.xls`, saved 2008-01-29 | 1.9341, from a mean of 9.5498 percent and a standard deviation of 16.9396 percent | `TestThePriceBasisOnHisOwnWorkbook::test_the_entry_is_his_workbook_s_close_column` and `::test_the_as_traded_leverage_and_the_moments_beneath_it` |
| 32 | 1993-01-29 to 2007-12-28 | row 22 less row 31 | row 18's file and row 31's | 0.5937 | `TestThePriceBasisOnHisOwnWorkbook::test_the_price_basis_is_worth_0_59_on_the_leverage` |
| 33 | 1993-01-29 to 2007-12-28 | row 18 less row 31's mean, in percentage points | row 18's file and row 31's | 1.6809 percentage points, against 0.0265 on the standard deviation | `TestThePriceBasisOnHisOwnWorkbook::test_the_price_basis_is_worth_1_68_points_on_the_mean` |
| 34 | 1993-01-29 to 2007-12-28 | row 31 halved against row 11, which holds exactly while row 31 is above 1.954079 | row 31's file, with row 18's beside it for the adjusted verdict | the claim fails, 0.0200 short of the threshold on the leverage, with half-Kelly at 0.9670 | `TestThePriceBasisOnHisOwnWorkbook::test_the_black_monday_conclusion_reverses_on_the_as_traded_close` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | +0.06 percentage points | reproduced with a gap | Chan's claim is that SPY's mean annual return over his span is about 11 percent, and it survives. The number does not, and the cause is named and outside the method: his 2008 download and this one differ on about ten quarterly dividends inside the window, so this download does not reach it. Later dividends are not the cause, since they scale every earlier price by one factor and leave returns unchanged. |
| 2 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. The whole gap in the mean sits on about ten days on or beside SPY's quarterly ex-dividend dates, where one download folds in all or part of a payout that the other does not, mostly raising the 2026 mean. That moves a mean and barely touches a standard deviation. |
| 3 | +0.064 percentage points | reproduced with a gap | Row 1's gap, carried through. The risk-free rate is the book's own constant, so nothing else moved. |
| 4 | +0.0038 | reproduced with a gap | Chan's claim is that SPY's Sharpe ratio over his span is a shade above 0.42, and it survives. This row is also what holds the specification: the population dispersion form gives 0.4276 rather than 0.4275 on his own data, and only an assertion tighter than 5.7e-5 can tell the two apart. |
| 5 | +0.023 | reproduced with a gap | The replication. Chan's claim is that the growth-optimal leverage on SPY is about two and a half times equity, and it survives with room. The number does not, for row 1's reason. |
| 6 | +0.16 percentage points | reproduced with a gap | Row 4's gap carried through `S^2 / 2`, which is how 0.0038 on a Sharpe ratio becomes 0.16 percentage points of growth. The formula itself is not among the committed highlights, because location 2849 renders it as an image, so it is recovered from `example6_3.m` rather than quoted. |
| 7 | +0.1 percentage points | reproduced with a gap | Chan's claim is that unlevered growth is below the mean return and levered growth above it, and both survive. Reading `m` as the total return instead of the excess return would put this row four points out, which is a misread symbol that looks like a gap in the data. |
| 8 | +0.02 | reproduced with a gap | Row 5 halved, so its gap halved. |
| 9 | \$0 on all four figures | reproduced | Every number in the chain is arithmetic on the book's own rounded 2.528. Nothing reads a series, so nothing could have moved. Chan's printed \$252,800 is itself derived from that rounded input: the exact leverage he computed buys \$252,775.87, which is the one printed figure his own workbook misses. |
| 10 | none | none, not a replication | The book works one leverage. The row exists so \$255,059.13 is not read against \$252,800 as a failure to reproduce: it is a different account, and the difference is row 5's gap times \$100,000. |
| 11 | not statable, the source gives one significant figure | reproduced | Chan prints "about 1" and 0.20 divided by 0.2047 is 0.977040. Both operands are his. |
| 12 | none, the source states a claim | reproduced | The claim is that even half-Kelly would not have survived Black Monday, and it survives on this vintage. It is thinner than 2.5506 against 1.954079 sounds: on Chan's own workbook the as-traded close gives a leverage of 1.9341, below the threshold, so the price basis alone reverses his conclusion, which rows 31 and 34 compute. That is why this repo's usual preference for a series that cannot be restated is set aside here and the adjusted close is read. |
| 13 | none | none, not a replication | SPY's first bar is 1993-01-29 and Black Monday is 1987-10-19, so no SPY vintage of any span can check the book's 20.47 percent. The worst day this window holds is 7.2473 percent, about a third of it, and the row exists so the two are not read as one number. |
| 14 | none | none, not a replication | The book stops in 2007. What the row shows is that nineteen more years of SPY lower the leverage to 2.3281 while leaving the Sharpe ratio at 0.4315, within 0.0002 of the shorter window's. The dispersion rose and the ratio did not move, which is the shape of a claim that has aged better than its number. |
| 15 | none, the source states a claim | did not reproduce | The claim is true in the reading nobody needs and false in the one they do. Under the annualisation in use the factor cancels between the mean and the variance, so the annualised and per-period ratios agree to floating-point noise, exactly and for any factor. Resampling the returns rather than rescaling their moments moves `f*` by 43 to 47 percent, on all three monthly rules, and those sit within 0.11 of each other. No vintage explanation is available, because the same three rules on Chan's own workbook land 43 to 47 percent above his daily figure too. This is the shape of Entry 1's row 11, where a conclusion about a library turned out to be a conclusion about a default. |
| 16 | none | none, not a replication | The book works one window. Kelly recommends a short of 2.82 times equity here, because the mean excess return over these three years is negative, and the row exists because that is the case requirement 10 of the issue was written for: a negative leverage is arithmetic rather than a failure, and neither half-Kelly nor the drawdown comparison carries across the sign change. |
| 17 | none | none, not a replication | The book works one window. Read against row 16 this is the entry's fourth conclusion in two cells: one vintage, one specification, and a leverage running from −2.82 to +4.90 depending only on which years are read. |
| 18 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. This is row 1 on the series Chan read, and the gap row 1 carries is gone, which is what names it as the vintage. |
| 19 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints, as row 2 already was on the 2026 download. |
| 20 | +0.000 percentage points | reproduced | Exact at the three decimals the book prints. |
| 21 | +0.0000 | reproduced | Exact at the four decimals the book prints, and only under the sample dispersion form. The population form gives 0.427580, which prints as 0.4276, so this row demonstrates on his own data what row 4 could only argue by analogy. |
| 22 | +0.000 | reproduced | Exact at the three decimals the book prints. A zero here says Chan's arithmetic is right on Chan's data. It says nothing about whether 2.528 is a leverage anyone should carry, and the report prints that above the table. |
| 23 | +0.00 percentage points | reproduced | Exact at the two decimals the book prints. |
| 24 | +0.0 percentage points | reproduced | Exact at the one decimal the book prints. |
| 25 | +0.00 | reproduced | Exact at the two decimals the book prints. |
| 26 | −\$24, −\$22, +\$2 and −\$12, in whole dollars because the book prints whole dollars | reproduced with a gap | The claim is that 2.528 times \$100,000 buys about a quarter of a million dollars of SPY and resizes as the chain shows, and it survives. The numbers differ because Chan rounded the leverage to 2.528 before multiplying. Rounding row 22 to the three decimals he printed reproduces the first three figures to the cent and the fourth to the dollar he printed it at, so the cause is named and sits in his arithmetic rather than in his data. |
| 27 | none, the source states a claim | reproduced | The claim survives on his own data as it does on the 2026 download in row 12. The margin is 0.57 here against 0.60 there, because his leverage is the lower of the two. |
| 28 | none, the source states a claim | did not reproduce | Row 15's refutation, on the series Chan read. Every monthly rule lands 43 to 47 percent above his daily figure, so the vintage explanation is spent, which is the sharpest case of this verdict the rules above name. |
| 29 | none | none, not a replication | The book reads one vintage. The row exists because a vendor restates which days a series holds as well as what they are worth, and a silent join would hide the first. Over this span the 2026 download and his adjusted column hold the same days, so row 30 is a difference in prices rather than in calendars. |
| 30 | none | none, not a replication | The book reads one vintage. This row is why rows 1 and 3 to 8 miss while row 2 does not. About ten days near SPY's ex-dividend dates carry more than the whole gap in the mean, and they barely move a standard deviation. |
| 31 | none | none, not a replication | The book prints nothing from the as-traded close. His `example6_3.m` reads the adjusted column, and this row reads the column beside it in the same workbook. |
| 32 | none | none, not a replication | The book reads one price basis. The basis is worth more than row 27's 0.57 margin over the threshold, which is why the conclusion turns over in row 34. |
| 33 | none | none, not a replication | The book reads one price basis. The mean moves by 1.68 points and the standard deviation by 0.0265 points, so the leverage falls with the mean rather than with the risk. SPY has not split, so what separates the two columns is its distributions. |
| 34 | none, the source's claim is about the series he read | none, not a replication | The claim fails on this column. Half-Kelly is 0.9670, below the 0.977040 a 20 percent day allows, so Black Monday's loss would have left it inside the tolerance. Rows 12 and 27 test his claim on the series he read and this row tests it on one he did not, so the verdict there stands. What this row shows is that the price basis decides the verdict rather than shading it. |

### What the entry concludes

Five things, and the first is what makes the other four worth reading.

1. **Seven numbers moved and every claim but one held.** Every level Chan
   computed from a series except the dispersion is higher on the 2026 download,
   by 0.06 percentage points on the mean and 0.023 on the leverage. Every
   statement those numbers were printed to support but one still holds on that
   vintage. The exception is his claim that the Kelly leverage does not depend
   on the time scale, which rows 15 and 28 record as `did not reproduce` on that
   vintage and on his own workbook alike, so its failure owes nothing to the
   vintage. The rest is the same split Entry 1 found on
   a different pair with a different estimator: a published number and the
   claim it supports have different shelf lives, and only the number depends on
   a vintage. What is new here is the one that did not move. The dispersion of
   row 2 reproduces while the mean of row 1 does not, because the two downloads
   differ on about ten days on or beside SPY's quarterly ex-dividend dates,
   mostly raising the 2026 mean, which moves a mean and barely touches a
   standard deviation. Row 30 measures that rather than arguing it.
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
   The margin is 0.60 on a threshold of 1.954079 on the 2026 download and 0.57
   on Chan's own adjusted column. The price basis alone is worth 0.59 on his
   data, which row 32 computes, so it spends the whole of his margin and row
   34 shows the verdict turning over. A replication that reported only "2.5506
   against 1.26" would have looked comfortable.
4. **The window moves the answer further than the vendor does.** Inside this
   one vintage the leverage runs from a short of 2.82 times equity over 2000 to
   2002 to a long of 4.90 over 2003 to 2007, a spread of 7.72 against a gap of
   0.023 in row 5. So a leverage reported with no window named mixes sample
   choice and vendor drift, and neither is recoverable afterwards. That is why
   the window is an argument and why the default is Chan's own.
5. **On his own data every figure reproduces, and that is all it shows.** Rows
   18 to 25 land on what Chan printed at the precision he printed it, and row
   26 misses only by the rounding he did before multiplying. This is the repo's
   first exact reproduction of a leverage, which makes it the result most
   likely to be over-read. It is exploratory like everything above it: the
   sample was spent on a hypothesis Chan chose, so `reproduced` here means his
   arithmetic is right on his data. It is not evidence that 2.528 is a leverage
   anyone should carry, and the report prints that sentence above the table
   rather than leaving it to this one. It is also the counterpart to Entry 1's
   row 7 rather than its row 6: the same code, on a vintage that was not lost,
   reaching the printed number.

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
[blog/kelly-leverage-on-spy.md](../blog/kelly-leverage-on-spy.md) moves with
it, since that essay quotes most of the figures in rows 1 to 34 and a few this
entry does not carry.

## Entry 4: risk parity against 60/40, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 4684, reporting
Edward Qian's argument. Shipped under
[issue 15](https://github.com/l3a0/quantitative-trading/issues/15).

Twenty-one rows, all derivable from
[tests/test_risk_parity.py](../tests/test_risk_parity.py).

**The allocation lands near Qian's and the ranking goes the other way.** On the
full common span the risk-parity weights are 21.78 to 78.22 against his 23-77,
and the leverage that matches 60/40's volatility is 1.9812 against his 1.8.
Rows 1 and 2 are therefore a percentage point and two tenths out. Row 3 is the
claim those two were printed to support, that the levered risk-parity portfolio
earns a higher Sharpe ratio at the same risk, and at Chan's 4 percent rate
60/40 wins it by 0.2169 with a robust t of −2.17. So this entry is the first
here where a published number lands close and the central claim behind it does
not survive.

Three rows are replications and eighteen are not. Rows 1, 2 and 3 are the three
things location 4684 prints. The other eighteen fall into five groups.

1. **Rows 4 and 5**, the volatility ratio Qian's weights imply and the one
   these two legs measured. They are what row 1's gap is really about.
2. **Rows 6 and 9**, the measured correlation and the one this run's leverage
   implies on Qian's printed weights. The second is row 2 restated in the unit
   his 1.8 is about.
3. **Rows 7, 8 and 10**, the risk decomposition under each allocation and both
   portfolios' Sharpe ratios. The decomposition is the argument the allocation
   rests on, and a weight reported with nothing behind it would be a number
   with no reasoning attached. Row 10 is there because a ranking reported as a
   sign hides its size.
4. **Rows 11 to 15**, the two sub-windows.
5. **Rows 16 to 21**, the same three windows with IWB in place of SPY. IWB
   tracks the Russell 1000, the index Qian's paper reads, so these rows price
   the substitution. Row 21 is what it cost, under a rule
   [issue 160](https://github.com/l3a0/quantitative-trading/issues/160)
   declared before any IWB number existed. SPY stays the equity leg of rows 1
   to 15, because promoting IWB after its numbers were seen would be choosing
   a proxy for its result.

**The sub-window rows carry no verdict either**, because the book makes no
claim about a window. They are what turns rows 1 to 3 into a verdict rather
than verdicts themselves, which is the position Entry 1's rows 2 and 10 are
already in.

**Two things the reader needs before reading a single number.** Both are
specification choices rather than measurements, and both push the same way.

1. **The risk-free rate is Chan's 4 percent constant, and it is not neutral.**
   The run reads no risk-free series and declares Chan's constant, so the rate
   is a specification rather than a rate anyone paid. FRED's TB3MS is
   committed under
   [issue 187](https://github.com/l3a0/quantitative-trading/issues/187), and
   the run does not read it. Only the post's figures do, for the bill
   average. Over this span AGG returned 3.09
   percent a year, so the bond leg's excess return is negative and a 78 percent
   bond weight is carrying it. The direction is exact rather than a guess: the
   Sharpe difference moves with the rate by `1 / vol(60/40)` less
   `1 / vol(risk parity)`, which is negative whenever the unlevered
   risk-parity portfolio is the quieter of the two, and it is on all three
   windows. So a higher assumed rate penalises risk parity and a lower one
   favours it. That derivative is pinned in
   `TestTheRankingIsBuiltOnAPointEstimateLeverageCannotMove`.
2. **No transaction costs and no financing spread are charged**, because the
   book charges none. The omission points one way: a daily rebalance has
   turnover, the levered portfolio has more of it plus a borrowing cost, so
   charging nothing favours the portfolio the book is arguing for. The ranking
   below goes against that portfolio anyway.

Every result here is **exploratory** in the design doc's sense. Reproducing a
figure someone else chose spends the sample on their hypothesis, so this entry
says whether the numbers reproduce and nothing about which allocation anyone
should hold.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Qian's allocation between stocks and bonds | 23-77 | Kindle location 4684 |
| 2 | The leverage on the whole risk-parity portfolio | 1.8 | location 4684 |
| 3 | Qian's claim, a higher Sharpe ratio at 60/40's risk level | a claim rather than a figure | location 4684 |
| 4 | The volatility ratio his weights imply | none, the ratio is derived from row 1 rather than printed | n/a |
| 5 | SPY and AGG annualised volatility, full span | none, the book prints no volatilities | n/a |
| 6 | The stock-bond correlation, full span | none, the book prints no correlation | n/a |
| 7 | The equity leg's risk contribution under 60/40, full span | none, the book states the imbalance without a number | n/a |
| 8 | The risk contributions under the risk-parity weights, full span | none | n/a |
| 9 | The correlation this run's leverage implies on his printed weights | none, this is row 2 read backwards through the same map | n/a |
| 10 | Both portfolios' Sharpe ratios at matched volatility, full span | none, the book prints no Sharpe ratio | n/a |
| 11 | Risk-parity weights and volatility ratio, falling-rates window | none, the book works no window | n/a |
| 12 | The ranking on the falling-rates window | none, the book works no window | n/a |
| 13 | Risk-parity weights and volatility ratio, rising-rates window | none, the book works no window | n/a |
| 14 | The ranking on the rising-rates window, on weights from before it | none, the book works no window | n/a |
| 15 | The leverage that matches 60/40's volatility, both sub-windows, on each window's own weights and on the weights row 14 carries | none, the book works no window | n/a |
| 16 | IWB and AGG annualised volatility, their correlation, the risk-parity weights and both risk splits, full span | none, the book prints no IWB figure | n/a |
| 17 | The leverage, the correlation it implies on his weights, the ranking and both Sharpe ratios on IWB, full span | none, the book prints no IWB figure | n/a |
| 18 | The falling-rates window on IWB | none, the book works no window | n/a |
| 19 | The rising-rates window on IWB, on weights from before it, and its leverage on each window's own weights | none, the book works no window | n/a |
| 20 | The rate at which the IWB ranking ties, and both Sharpe ratios at the bill average, full span | none, the book prints no IWB figure | n/a |
| 21 | What the SPY proxy cost, IWB against SPY on all three windows | none, the book prints no IWB figure | n/a |

### What this repo computed

Every row reads the same price basis under the same rebalancing rule and the
same moments, and rows 1 to 15 read the same two vintages, so all of it is
stated once here rather than in twenty-one cells. Rows 1 to 15 read
`yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv` and
`yfinance_agg_adjusted_2003-09-29_2026-09-17_dl2026-09-18.csv`, both yfinance's
both-adjustments close, both downloaded 2026-09-18. Rows 16 to 20 read
`yfinance_iwb_adjusted_2000-05-19_2026-10-02_dl2026-10-03.csv` in place of the
SPY file, yfinance's both-adjustments close downloaded 2026-10-03, against the
same AGG file. Row 21 reads all three. IWB holds every day AGG does inside the
span, so rows 16 to 21 run on exactly the days rows 1 to 15 do. The price basis
is adjusted on both legs. The rebalancing rule is constant weights rebalanced
every trading day. The moments are simple daily returns, the mean scaled by
252 and the sample standard deviation, dividing by n−1, by the square root of
252, with a 4 percent annual risk-free rate subtracted as 0.04/252 a day.

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2003-09-30 to 2026-09-17 | inverse-volatility weights, which equalise the risk contributions on two legs | 21.78 to 78.22 | `TestTheFullSpan::test_the_risk_parity_weights_land_about_a_point_off_qians` |
| 2 | 2003-09-30 to 2026-09-17 | the multiple that lifts the risk-parity portfolio's volatility to 60/40's | 1.9812 | `TestTheFullSpan::test_the_leverage_and_what_it_implies` |
| 3 | 2003-09-30 to 2026-09-17 | the two Sharpe ratios at matched volatility, ranked as the mean of their daily excess-return difference | −0.2169, a mean difference of −2.4552 percent a year, robust t −2.1727 at lag 9 | `TestTheFullSpan::test_the_ranking_goes_against_the_book_and_the_window_resolves_it` |
| 4 | none, both operands are published figures | 0.77 divided by 0.23, and the band weights rounding to 23 and 77 admit | 3.3, band 3.26 to 3.44 | `TestTheTwoLegAlgebra::test_qians_printed_weights_are_a_statement_about_volatilities` |
| 5 | 2003-09-30 to 2026-09-17 | annualised standard deviation of each leg's simple daily returns | SPY 18.5472 percent, AGG 5.1650 percent, ratio 3.5909 | `TestTheFullSpan::test_the_leg_moments` |
| 6 | 2003-09-30 to 2026-09-17 | Pearson correlation of the two legs' daily returns | −0.0002 | `TestTheFullSpan::test_the_leg_moments` |
| 7 | 2003-09-30 to 2026-09-17 | `w_i (Sigma w)_i / (w' Sigma w)` at 60/40 | SPY 96.6717 percent, AGG 3.3283 percent | `TestTheFullSpan::test_60_40_is_nearly_all_equity_risk` |
| 8 | 2003-09-30 to 2026-09-17 | the same quantity at the row 1 weights | 50 percent each, exactly | `TestTheFullSpan::test_the_risk_parity_weights_land_about_a_point_off_qians` |
| 9 | none, the map takes no volatility | row 2 inverted through the leverage-to-correlation map on Qian's 23-77 weights | −0.1508, against the +0.1579 his 1.8 implies | `TestTheFullSpan::test_the_leverage_and_what_it_implies` |
| 10 | 2003-09-30 to 2026-09-17 | annualised mean excess return over annualised volatility, both at 11.3181 percent volatility | 60/40 0.4111, levered risk parity 0.1942 | `TestTheFullSpan::test_the_ranking_goes_against_the_book_and_the_window_resolves_it` |
| 11 | 2003-09-30 to 2022-03-15 | the row 1, 5, 7 and 8 specifications, recomputed inside the window | 20.53 to 79.47, SPY 18.8748 percent, AGG 4.8772 percent, ratio 3.8700, correlation −0.0688, 60/40 risk 98.2290 and 1.7710 percent, risk parity 50 percent each | `TestTheTwoSubWindows::test_the_falling_rates_window` |
| 12 | 2003-09-30 to 2022-03-15 | the row 2, 3, 9 and 10 specifications, on weights fitted inside the window because nothing precedes it | leverage 2.1475, implying −0.3299 on his weights, Sharpe 0.3820 against 0.2255, difference −0.1565, mean difference −1.7777 percent a year, robust t −1.3455 at lag 9 | `TestTheTwoSubWindows::test_the_falling_rates_window` |
| 13 | 2022-03-17 to 2026-09-17 | the row 1, 5, 7 and 8 specifications, recomputed inside the window | 26.63 to 73.37, SPY 17.1193 percent, AGG 6.2127 percent, ratio 2.7555, correlation +0.2442, 60/40 risk 90.0043 and 9.9957 percent, risk parity 50 percent each | `TestTheTwoSubWindows::test_the_rising_rates_window` |
| 14 | 2022-03-17 to 2026-09-17 | the row 3, 9 and 10 specifications, on the row 11 weights, which are strictly earlier data | implying +0.5689 on his weights, Sharpe 0.5071 against 0.0097, difference −0.4974, a mean difference of −5.5417 percent a year, robust t −2.1956 at lag 6 | `TestTheTwoSubWindows::test_the_rising_rates_window` |
| 15 | the two windows of rows 11 and 13 | the row 2 specification on each window's own weights, and for the rising window also on the falling window's weights, which are the weights row 14 ranks | 2.1475 falling on its own 20.53 percent stocks, 1.5495 rising on its own 26.63 percent, and 1.6572 rising on the falling window's 20.53 percent | `TestTheTwoSubWindows::test_the_falling_rates_window`, `::test_the_rising_rates_window` and `::test_each_leverage_in_row_15_names_the_weights_it_was_measured_on` |
| 16 | 2003-09-30 to 2026-09-17 | the row 1, 5, 6, 7 and 8 specifications on IWB | IWB 18.4710 percent, AGG 5.1650 percent, ratio 3.5762, correlation −0.0072, weights 21.85 to 78.15, 60/40 risk 96.7630 and 3.2370 percent, risk parity 50 percent each | `TestIWBInPlaceOfSPY::test_the_leg_moments_on_iwb` and `::test_the_weights_and_risk_split_on_iwb` |
| 17 | 2003-09-30 to 2026-09-17 | the row 2, 3, 9 and 10 specifications on IWB | leverage 1.9795, implying −0.1486 on his weights, Sharpe 0.4132 against 0.1962 at 11.2589 percent volatility, difference −0.2171, mean difference −2.4439 percent a year, robust t −2.1619 at lag 9 | `TestIWBInPlaceOfSPY::test_the_leverage_and_ranking_on_iwb` |
| 18 | 2003-09-30 to 2022-03-15 | the row 11 and 12 specifications on IWB, on weights fitted inside the window because nothing precedes it | 20.61 to 79.39, IWB 18.7833 percent, ratio 3.8512, correlation −0.0802, 60/40 risk 98.3945 percent on IWB, leverage 2.1484 on its own 20.61 percent, Sharpe 0.3887 against 0.2314, difference −0.1574, mean difference −1.7754 percent a year, robust t −1.3423 at lag 9 | `TestIWBInPlaceOfSPY::test_the_sub_windows_on_iwb` |
| 19 | 2022-03-17 to 2026-09-17 | the row 13 and 14 specifications on IWB, ranked on the row 18 weights, which are strictly earlier data, and the row 2 specification on each window's own weights, and for the rising window also on the falling window's weights, which are the weights this row ranks | 26.64 to 73.36, IWB 17.1076 percent, ratio 2.7536, correlation +0.2511, 60/40 risk 89.8823 percent on IWB, leverage 1.5467 on its own 26.64 percent and 1.6532 on the falling window's 20.61 percent, and on those Sharpe 0.4872 against 0.0003, difference −0.4869, mean difference −5.4295 percent a year, robust t −2.1556 at lag 6 | `TestIWBInPlaceOfSPY::test_the_sub_windows_on_iwb` |
| 20 | 2003-09-30 to 2026-09-17 | row 17's tie in closed form, and row 17 recomputed at the 1.744 percent TB3MS average | ties at 1.5050 percent, against SPY's 1.4977. At 1.744 percent, Sharpe 0.6136 against 0.5928, difference −0.0208, robust t −0.2071 | `TestIWBInPlaceOfSPY::test_the_tie_rate_and_the_bill_average_on_iwb` |
| 21 | all three windows | the five answers of the rule [issue 160](https://github.com/l3a0/quantitative-trading/issues/160) declared, each instrument on its own weights and leverage and every change IWB less SPY. They are the change in both Sharpe ratios, their difference and the mean difference, then the robust t on the daily change `d_IWB(t) − d_SPY(t)` in the series each ranking is the mean of, then whether any ranking's sign or resolution flips, then IWB's ratio against row 4's band, and last row 20's tie against the bill average | on the full span, falling and rising windows in turn, 60/40's Sharpe changes +0.0021, +0.0067 and −0.0199, risk parity's +0.0019, +0.0059 and −0.0094, the difference −0.0001, −0.0008 and +0.0105, and the mean difference +0.0113, +0.0023 and +0.1122 percent a year. The robust t on that change is +0.2939, +0.0557 and +0.9764. No sign or resolution flips. IWB's ratio is 3.5762, 3.8512 and 2.7536, all outside the band. The tie is 1.5050 percent, under 1.744 | `TestIWBInPlaceOfSPY::test_what_the_proxy_cost` |

**One return falls in neither sub-window and it is the boundary day's.** Rows 11
to 15 run on 4,647 and 1,130 daily returns against the full span's 5,778, one
short. A return spans two closes, so the one dated 2022-03-16 runs from the
2022-03-15 close to the 2022-03-16 close. Row 11's window ends with the return
dated 2022-03-15 and row 13's starts with the one dated 2022-03-17, so this one
belongs to neither. That return covers the day the Federal Reserve announced
its first rate rise of 2022. SPY gained 2.2174 percent that day against AGG's
0.0743 percent. So the return is named here rather than left for a reader to
notice the counts miss by one. Rows 18 and 19 run on the same counts and lose
the same return.
`TestTheTwoSubWindows::test_the_two_windows_cover_the_span_except_the_return_that_straddles_the_cut`
holds that day's two returns, so the arithmetic above stays checkable.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −1 percentage point on the equity leg | reproduced with a gap | Qian's claim is that equalising risk moves the allocation a long way toward bonds, to roughly a quarter equity, and it survives at 21.78 to 78.22. The number misses by a point, and the cause is named and outside the method: the bond proxy. AGG is the aggregate bond exposure his argument describes and it was committed in writing before anything was downloaded, so the proxy explains the gap and was not chosen to close it. Row 4 is why the miss is larger than a point makes it sound. |
| 2 | +0.2 | reproduced with a gap | His claim is that matching 60/40's risk takes roughly double leverage on the risk-parity portfolio, and 1.9812 survives it. On his printed weights the leverage reads the correlation and nothing else, so this row and row 9 are one measurement stated twice, and the gap is the distance between a correlation near zero and the +0.16 his 1.8 implies. |
| 3 | none, the source states a claim | did not reproduce | The replication. At the declared 4 percent rate, 60/40 earns the higher Sharpe ratio at matched volatility, by 0.2169, and the window resolves it at a robust t of −2.17. The instruments and the span offer no cause outside the method. The vintage explanation that carries Entry 1's rows is about a series nobody holds, and this is a claim about two instruments this repo chose in the open on a span every one of whose days is committed here. The rate is the one input that stands in for something Qian measured, the Treasury-bill rate he subtracted. The ranking ties at an assumed 1.50 percent and resolves only at rates above 3.80 percent, and What this entry cannot say gives both. What the entry concludes says what the gap is made of. |
| 4 | none | none, not a replication | Derived from row 1's published pair rather than printed. It is here because it is the quantity the printed weights are a statement about, and because a reader comparing only the weights would call row 1 a near match. |
| 5 | none | none, not a replication | The book prints no volatilities. The measured ratio of 3.5909 sits outside the 3.26 to 3.44 band row 4 gives, which is the sharper reading of row 1's gap. |
| 6 | none | none, not a replication | The book prints no correlation. Over the full span the two legs are uncorrelated to three decimals, at −0.0002, which is a coincidence of averaging rather than a stable fact: rows 11 and 13 give −0.0688 and +0.2442. |
| 7 | none | none, not a replication | Qian's premise, measured. 60 percent of the capital carries 96.67 percent of the risk, so 60/40 is nearly an all-equity portfolio in risk terms and the labels say otherwise. This row is why rows 1 and 2 are worth chasing at all. |
| 8 | none | none, not a replication | Exactly 50 percent each, which is what says the weights of row 1 are the risk-parity weights rather than something near them. |
| 9 | none | none, not a replication | Row 2 in the unit his 1.8 is really about. It is not the measured correlation of row 6 and the two are kept apart, because the map is read on his printed weights and this run's weights are not his. No claim is made about recovering the correlation Qian measured. His 1.8 carries two significant figures and so do his weights, and letting both roundings vary at once opens the band to −0.01265 through +0.37141, wide enough to include both zero and a clearly positive correlation. |
| 10 | none | none, not a replication | The book prints no Sharpe ratio, only the ranking of row 3. Both are stated because a ranking reported as a sign hides its size, and 0.4111 against 0.1942 is not a near miss. |
| 11 | none | none, not a replication | The book works no window. The bond leg is at its quietest here, so the volatility ratio reaches 3.8700 and risk parity holds the least equity it holds anywhere in this entry. |
| 12 | none | none, not a replication | The book works no window. The robust t is −1.3455, so this window does not resolve its own ranking and nothing is read off the sign. Its weights are fitted inside it, because nothing precedes it, and the row says so rather than letting it pass as the out-of-sample row 14. |
| 13 | none | none, not a replication | The book works no window. The bond leg's volatility rises to 6.2127 percent and the ratio falls to 2.7555, which moves the risk-parity weights toward stocks, to 26.63 percent. They do not pass 60, so risk parity still holds less equity than 60/40 and the correction the book argues for still points the same way. |
| 14 | none | none, not a replication | The book works no window. This is the only ranking here whose weights did not see the window they are judged on, and it is the worst of the three for risk parity, at −0.4974 with a robust t of −2.1956. Refitting the weights inside the window moves it in risk parity's favour, which is why it is not done. |
| 15 | none | none, not a replication | The book works no window. On each window's own weights, which is row 2's specification, the leverage runs from 2.1475 to 1.5495, one on each side of his 1.8. That is what says 1.8 is a regime measurement rather than a constant. Row 14 ranks the rising window at 1.6572, which is that window on the falling window's weights. So setting 1.6572 against 2.1475 holds the weights fixed and moves only the window. |
| 16 | none | none, not a replication | The book prints no IWB figure. IWB's volatility is 18.4710 percent against SPY's 18.5472, so the ratio moves from 3.5909 to 3.5762 and stays outside row 4's band, and the equity weight moves by 0.07 of a percentage point. On this window the broader index and the narrower one carry almost the same risk. |
| 17 | none | none, not a replication | The book prints no IWB figure. Every figure but the robust t moves in the third decimal or later, and the t moves by 0.0107. The leverage is 1.9795 against 1.9812, the difference −0.2171 against −0.2169, and the robust t −2.1619 against −2.1727. The ranking still goes against the book and the window still resolves it. |
| 18 | none | none, not a replication | The book works no window. The robust t is −1.3423, so as on SPY this window does not resolve its own ranking and nothing is read off the sign. |
| 19 | none | none, not a replication | The book works no window. Ranked on weights from before it, as row 14 is, it is again the worst of the three for risk parity, at −0.4869 with a robust t of −2.1556. On each window's own weights the leverage runs from 2.1484 to 1.5467 and straddles his 1.8, the way row 15's SPY figures do. |
| 20 | none | none, not a replication | The book prints no IWB figure. The tie moves by less than a hundredth of a point and stays under the 1.744 percent bill average. So at the rate bills actually paid 60/40 still leads on IWB, and the robust t of −0.2071 does not resolve it. |
| 21 | none | none, not a replication | The answer to the question [issue 160](https://github.com/l3a0/quantitative-trading/issues/160) asked, under the rule it declared before any IWB number existed. The swap moved no verdict. No window changes sign or resolution, no change in the mean difference reaches a robust t of 1, and IWB's ratio misses Qian's band on every window as SPY's does. The largest change is the rising window's, +0.0105 of Sharpe difference, against a difference of −0.4974. The paired t belongs to the change in the mean difference rather than to the change in the Sharpe difference, because the two instruments match different volatilities. |

### What the entry concludes

Five things. The first is the one the next three explain, and the fifth says
the first does not rest on the proxy.

1. **The numbers land close and the claim does not survive.** Row 1 misses by a
   percentage point and row 2 by two tenths, which on the five-figure scale
   Entry 3 works at would read as a comfortable reproduction. Row 3 is the
   claim those two were printed to support and 60/40 wins it by 0.2169 of
   Sharpe, resolved at a robust t of −2.17 at the declared 4 percent rate.
   That is the reverse of the split Entries 1 and 3 both found, where most of
   the numbers moved and the central claims held.
2. **The gap is where the return is, not where the risk is.** Row 8 lands on 50
   percent each exactly, so the method did what it says. Row 7 confirms the
   premise it rests on. What fails is the step from a balanced risk split to a
   higher Sharpe ratio, which needs the bond leg to earn enough per unit of
   risk to be worth the leverage. Over this span AGG returned 3.09 percent a
   year against the 4 percent rate the specification assumes, so its excess
   return is negative and levering a 78 percent holding of it 1.98 times
   multiplies that. The rate is a declared choice. The direction it pushes and
   the rate at which row 3 ties, 1.50 percent, follow from it in closed form
   rather than from a search, and What this entry cannot say gives both.
3. **The out-of-sample window is the worst one, which is the direction that
   matters.** Row 14 is the only ranking whose weights came from outside the
   window they are judged on, and it is the largest loss in the entry.
   Refitting inside the window would have improved it, which is the bias the
   separation exists to remove.
4. **The volatility ratio and the leverage are regime measurements rather
   than constants.** Rows 5, 11 and 13 give 3.5909, 3.8700 and 2.7555 against
   Qian's implied 3.3, and the two sub-windows straddle the band from opposite
   sides. So the quantity his 23-77 encodes moved by a third inside one pair of
   instruments, and an allocation derived from it inherits that. The leverage
   follows. Row 15 gives 2.1475 before the boundary and 1.5495 after, each on
   that window's own weights, which straddle his 1.8 the same way. Its third
   figure, 1.6572, is the later window on the earlier window's weights. Set
   against 2.1475 it measures a change of window alone, and it is not the
   leverage the later window's own risk parity needs. This is the same shape as Entry 3's fourth
   conclusion, where the window moved the leverage further than the vendor
   did.
5. **The S&P 500 proxy is not what separates row 3 from Qian's claim.** Rows
   16 to 21 run IWB, which tracks his Russell 1000, on the same window, rate
   and bond leg. No ranking changes sign or resolution, the largest change in
   a Sharpe difference is 0.0105, and no change in the mean difference reaches
   a robust t of 1. So on this window the instrument explains almost none of
   the gap. It moves the equity weight by 0.07 of a percentage point against
   row 1's miss of one, and it moves no verdict. What is left of the
   difference between his inputs and these includes his sample, his monthly
   frequency and his cash rate, which What this entry cannot say gives.

### What this entry cannot say

Four things. One is a missing series, two are choices inherited from the source
or from this repo, and the fourth is a limit of the estimator.

**Whether the ranking survives a real financing cost.** It is charged nothing,
because the book charges nothing, and the omission favours the levered
portfolio. Row 3 goes against that portfolio anyway, so the missing cost makes
the verdict safer rather than shakier, which is the one direction an omission
is allowed to point without being closed.

**Whether a realised short rate reverses row 3.** That needs a run that
charges cash at a Treasury-bill series rather than a constant, which is a
different deliverable, and the design doc's register already carries the same
cut for Entry 3's Kelly example. FRED's TB3MS is now committed, under
[issue 187](https://github.com/l3a0/quantitative-trading/issues/187), and
the run does not read it.
The rate is Chan's constant and the report says so on its own last lines. The
derivative above says which way a lower rate would push, and it also says how
far. The difference is linear in the rate, so row 3 ties at an assumed rate of
1.50 percent, row 12 at 2.45 percent, and row 14 only at −4.43 percent, which
no positive rate reaches. `test_the_rate_at_which_the_two_sharpe_ratios_tie`
pins all three. Row 3's robust t is linear in the rate too, and it reaches −2
at 3.80 percent, so the window resolves the ranking at rates down to 3.80
percent and at none below, a fifth of a point under the declared rate. At a
rate of zero risk parity leads with a t of +1.30, which does not resolve
either. Row 14's t reaches −2 at 3.25 percent in the same way.
`test_the_two_resolved_rankings_resolve_only_down_to_a_little_below_4_percent`
pins all of these. Whether the realised bill rate averaged below 1.50 percent
over the full span decides row 3's sign to first order. The committed series
answers it: TB3MS averaged 1.744 percent over the full calendar months inside
the span, above the tie, which
[tests/test_bill_rates.py](../tests/test_bill_rates.py) pins.

**Whether Qian's own instruments and span reproduce his numbers.** Chan names
neither, so SPY and AGG and this window are this repo's choice, fixed in writing
on [issue 15](https://github.com/l3a0/quantitative-trading/issues/15) before any number was seen. Rows 1 and 2 are therefore a test of the
argument on the instruments and the period this repo picked rather than of his.

Chan calls the source "not publicly distributed" and it is on PanAgora's own
site, which is what makes this a gap somebody could close rather than one nobody
can. A copy is committed at
[research/papers](../research/papers/README.md), so every figure quoted below
is checkable against the document rather than against a link. Qian's "Risk
Parity Portfolios: Efficient Portfolios Through True Diversification",
September 2005, works monthly excess returns over
three-month Treasury bills on the Russell 1000 Index and the Lehman Aggregate
Bond Index from 1983 to 2004, and prints the volatilities, the correlation, the
risk split and both Sharpe ratios this entry has no published counterpart for.
Two cards read it, because the gap splits into an instrument and a sample.
[Issue 160](https://github.com/l3a0/quantitative-trading/issues/160) swapped
the equity leg for one that tracks his index and held everything else fixed,
which ran on free data and is rows 16 to 21.
[Issue 161](https://github.com/l3a0/quantitative-trading/issues/161) reaches his
1983 to 2004 sample and is blocked on licensed history. Three things the split
turns on are worth stating here rather than leaving to those cards.

1. **His window and this one barely overlap.** 1983 to 2004 against
   2003-09-30 to 2026-09-17. The paper gives years rather than months, so
   fifteen months is the most they can share and only if his sample runs to the
   end of 2004. That is about a seventeenth of his and an eighteenth of this
   one. His is the bond bull market and this one carries its reversal.
2. **His bond index is the one AGG tracks.** The Lehman Aggregate was renamed
   to Barclays and then to Bloomberg, and AGG follows it, so the proxy ruling
   was right about the index. What the fund cannot do is reach his span. Its
   first bar is 2003-09-29 and his sample ends in 2004, so it covers the tail of
   his twenty-two years and nothing before it.
3. **His equity leg is the Russell 1000 and SPY is not that.** It is the S&P
   500, which is a narrower index. IWB tracks the Russell 1000 and shares this
   entry's own window, so rows 16 to 21 measured what the substitution costs on
   it, and it moved no verdict. What the instrument cannot answer is his span,
   which is the first item.

His bond index settles the proxy ruling from the source rather than from
argument. The paper's disclosure describes the Lehman Aggregate as roughly
6,000 bonds with an approximate average maturity of ten years. The paper never
says duration and average maturity is not duration, so the reading that this is
an intermediate rather than a long-duration index is this repo's and not his.
It is the reading [issue 15](https://github.com/l3a0/quantitative-trading/issues/15) took when it chose AGG over TLT, before any of this
was read, and a maturity the source states is better evidence for it than the
argument it had.

**How much of the robust t the estimated leverage is worth.** Every t above is
computed on `leverage * parity - bench`, with the leverage estimated from the
same sample as the mean and then treated as a known constant. The sampling
variation in the two standard deviations behind it never enters the variance,
and the bias points toward significance. A moving-block bootstrap that
re-estimates the leverage on every draw, 4,000 resamples at block length 10,
puts the understatement at 2.7 percent on the full span, 2.6 on the falling
window and 1.3 on the rising one. No verdict above turns over, and the full
span's row 3 clears its threshold by 8.6 percent against an understatement of
2.7. Closing it properly needs a bootstrapped or Jobson-Korkie standard error,
which is a second estimator and a different deliverable. The bootstrap is
quoted here as a measurement taken during review rather than as something this
suite pins, the way `README.md`'s `## The write-up` names the figures its
essays quote and the suite does not hold.

The same estimate is why the ranking's point estimate and its error bar are
reported as different things. `sharpe_difference` does not move with the
leverage at all, so row 3's −0.2169 carries no look-ahead. The t does move, and
`TestTheRankingIsBuiltOnAPointEstimateLeverageCannotMove` pins both halves,
including the rising window's spread from −2.1956 to −1.6422 across the two
leverages a reader could defend.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/risk-parity-against-60-40.md](../blog/risk-parity-against-60-40.md)
moves with it, since that essay quotes most of these figures and a few this
entry does not.

## Entry 5: the fixed-income candidate, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 3951. Shipped
under [issue 136](https://github.com/l3a0/quantitative-trading/issues/136),
under the rules
[issue 16](https://github.com/l3a0/quantitative-trading/issues/16) sets for
every stationary candidate Chan names there.

This entry is not a replication. Chan states that "fixed-income instruments
can be found to be cointegrating", and that one can long and short bonds by
the same issuer at different maturities, but he works no example and prints no
number. So the entry carries a finding rather than a verdict, and its tables
drop the published-figure, gap and verdict columns, because no row has
anything to put in them. `### Rows that are not replications` above says why
the route that lets a stated claim carry a verdict does not reach this one.

Six rows, all derivable from
[tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py).

**TLT and IEF do not cointegrate over their shared history, in either
orientation.** With TLT as the dependent leg the statistic is −2.3887, and with
IEF it is −2.3168, both against a 10% bar of −3.04. The one-lag fits leave
autocorrelation the critical values do not allow for. The first fit whose
residuals pass is at 31 lags in both orientations, and there the statistics are
−1.5677 and −1.5387, further from rejecting. The rolling scan finds 56 and 51 of
278 one-year windows clearing 10%, and just over half of those end in 2003-04
or 2020-21.

Every row reads the same stand-ins, vintages and specification, so the three
are stated once here.

1. **The stand-ins.** TLT, which holds Treasuries maturing in twenty years or
   more, and IEF, which holds Treasuries maturing in seven to ten. They are
   one issuer at two maturities, and the step between them and Chan's
   sentence is that each is a rolling basket rather than a bond. Both were
   named on the issue before anything was downloaded, and the owner confirmed
   them on 2026-09-18.
2. **The vintages.** `yfinance_tlt_raw_2002-07-30_2026-10-01_dl2026-10-02.csv`
   and `yfinance_ief_raw_2002-07-30_2026-10-01_dl2026-10-02.csv`, both
   downloaded 2026-10-02. The basis is raw on both legs, meaning adjusted for
   splits and not for dividends. Most of a bond fund's return is its
   distributions, so an adjusted pair would drift apart by what the two
   maturities pay rather than by anything about whether their prices are
   tied.
3. **The specification.** The with-intercept Engle-Granger regression in
   levels, one ADF lag, over the full common span of 6,083 days. Both
   orientations are reported, because the test is not symmetric and Chan names
   no dependent leg. The residual check reads ten autocorrelations against the
   ±1.96/√n band and a Breusch-Godfrey test over the same ten lags at the 10%
   cut, and its search stops at Schwert's ceiling of 34 lags. The scan uses
   252-day windows stepped by 21.

Every result here is **exploratory**. The sample was spent on a claim Chan
stated and on stand-ins this repo chose for it, so the entry says whether
these two funds cointegrate over this span and nothing about bonds in general.

### What the book stated

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The claim | fixed-income instruments can be found to be cointegrating, long and short bonds by the same issuer at different maturities | Kindle location 3951 |
| 2 | TLT on IEF, full span | nothing, the book works no example | n/a |
| 3 | IEF on TLT, full span | nothing | n/a |
| 4 | The residual check at one lag, both orientations | nothing | n/a |
| 5 | The first lag count whose residuals pass, both orientations | nothing | n/a |
| 6 | The rolling scan, both orientations | nothing | n/a |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2002-07-30 to 2026-10-01 | rows 2 and 3 read together | neither orientation rejects at 10% | `TestBothOrientations::test_neither_orientation_rejects_even_at_ten_percent` |
| 2 | 2002-07-30 to 2026-10-01 | TLT = α + β·IEF + z, ADF at one lag on z | hedge 1.8632, intercept −74.8326, t −2.3887 on 6,081 observations, half-life 333.2 days | `TestBothOrientations::test_the_fit` |
| 3 | 2002-07-30 to 2026-10-01 | IEF = α + β·TLT + z, ADF at one lag on z | hedge 0.4771, intercept 46.6023, t −2.3168 on 6,081 observations, half-life 376.4 days | `TestBothOrientations::test_the_fit` |
| 4 | 2002-07-30 to 2026-10-01 | the residual check on each one-lag fit | Breusch-Godfrey p 0.0000 both ways, autocorrelations outside the band at residual lags 2 to 10 for TLT on IEF, and at 2 to 10 except 6 for IEF on TLT | `TestTheResidualCheck::test_the_one_lag_fit_fails_it` |
| 5 | 2002-07-30 to 2026-10-01 | the smallest lag count from 0 to 34 whose residuals pass both halves | 31 both ways, t −1.5677 and −1.5387, Breusch-Godfrey p 0.1352 and 0.3223 | `TestTheResidualCheck::test_the_first_fit_that_passes_is_further_from_rejecting` |
| 6 | 278 windows ending 2003-07-29 to 2026-09-11 | 252-day windows stepped by 21, one ADF lag | 56 and 51 clear 10%, 33 and 29 clear 5%, 30 and 29 of the 10% windows end in 2003-04 or 2020-21 | `TestTheRollingScan::test_the_counts` and `::test_rejections_cluster_in_two_stretches` |

### What each row says

| # | Why it is here |
| --- | --- |
| 1 | The finding. Chan's claim does not hold for this pair over this span. A stand-in that fails keeps its failure as the result, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule, so no other pair of funds is tried in its place. |
| 2 | The statistic is 0.65 short of the 10% bar, and row 3's is 0.72 short. The half-life of 333.2 trading days is more than a year, which is a spread that barely pulls back at all. |
| 3 | The other orientation, 0.0719 away from row 2, so this is a pair where the choice of dependent leg could not have turned the finding. On GLD/GDX's full raw history the two orientations sit 0.5352 apart, at −1.2893 and −1.8245. That comparison was measured on [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) and nothing in this suite pins it, because pinning the engine's asymmetry is [issue 127](https://github.com/l3a0/quantitative-trading/issues/127). |
| 4 | The one-lag fits leave autocorrelation at nearly every residual lag, so their statistics are read against critical values that do not apply. |
| 5 | The first fits whose residuals pass are further from rejecting than the one-lag fits, so the check strengthens the finding rather than weakening it. On GLD/GDX the band was the half of the check that decided. Here every autocorrelation is inside the band from 9 lags for TLT on IEF and from 10 for IEF on TLT, and the Breusch-Godfrey half is what holds the passing count at 31. `::test_the_breusch_godfrey_half_is_what_holds_the_count_at_31` pins that. |
| 6 | A description of the span, not a second finding. About one window in five clears 10% each way round. On GLD/GDX's raw history `TestRollingRegime` pins 31 of 231 for GLD on GDX, about one in seven, and pins no figure for the other orientation. No window that rejects is promoted to a claim about the pair, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule. |

### What the entry concludes

Three things, and the first is the finding.

1. **On these two funds, Chan's claim does not hold.** Both orientations fall
   short of the 10% bar, and the fits the residual check allows fall further
   short. That is evidence against TLT and IEF being cointegrated over
   2002-2026. It is not evidence against the claim Chan made, which is that
   such pairs can be found.
2. **The scan finds stretches, not a relationship.** About a fifth of the
   one-year windows reject, and just over half of those end in 2003-04 or
   2020-21, with the rest scattered across the other years. A pair trade sized
   on one of those stretches would have been sized on a window, which is the
   shape `TestRollingRegime` pins for GLD/GDX.
3. **The residual check matters more on a long span than on a short one.** The
   Chapter windows of Entry 1 first pass at 6 and 10 lags. This 6,083-day span
   first passes at 31, and it is the Breusch-Godfrey test rather than the band
   that holds it there. The ceiling on that search was fixed before anything
   was downloaded, so the 31 was found rather than chosen.

### What this entry cannot say

Three things.

**Whether individual bonds behave the way the funds do.** Each fund is a
rolling basket held near a constant maturity, while a bond's own maturity
shrinks every day until it stops trading. Chan's sentence is about bonds, and
these are funds that trade like stocks and have free daily history. Treasury
futures and individual bonds both need data this repo does not hold.

**Whether the yields behind these prices are cointegrated.** That is a related
question, whether the gap between long and intermediate yields stays put. It is a different claim from Chan's, because a yield cannot
be bought or sold, and it would need its own issue and its own stand-in named
before any data is read.

**Whether the finding survives another vintage.** These are raw closes, which
a vendor should restate only when a fund splits, so a later download should
match on every shared day unless one of the two has split by then. Nothing
has checked that against a second yfinance download. The nearest measurement
is SPY's two raw vintages, Chan's 2008 file and a 2026 yfinance download, which
come from two sources and disagree on 2 of the 3,758 days they share with no
split between them.
[tests/test_vintage_overlap.py](../tests/test_vintage_overlap.py) pins that,
and it says two sources can hold different closes rather than that a vendor
rewrote one. The comparison
[issue 139](https://github.com/l3a0/quantitative-trading/issues/139) built,
`chan.series.vintage_overlap`, is what would check TLT and IEF, and no second
download of either is committed.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md)
moves with it, since that post quotes most of these figures. So do its
three figures, which `uv run python -m chan.stationary_candidates_figures`
redraws.

## Entry 6: the CAD/AUD cross rate, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle location 3951. Shipped
under [issue 135](https://github.com/l3a0/quantitative-trading/issues/135),
under the rules
[issue 16](https://github.com/l3a0/quantitative-trading/issues/16) sets for
every stationary candidate Chan names there.

Seven rows, all derivable from
[tests/test_stationary_candidates.py](../tests/test_stationary_candidates.py).

**Chan's claim reproduces.** The log of the rate rejects a unit root at 5%,
with t −3.2136 at one lag against a bar of −2.86. The one-lag fit leaves
autocorrelation the critical values do not allow for. The first fit whose
residuals pass is at 10 lags, and there t is −2.9946, still past the bar. Both
had to clear it under the criterion
[issue 135](https://github.com/l3a0/quantitative-trading/issues/135) declared
before any statistic was computed, and both do. The half-life is 141.6 trading
days, a little over half a year.

One row is a replication and six are not. Row 1 is the claim, and it takes
the claim route `### Rows that are not replications` describes. Rows 2 and 3
are the two statistics the criterion reads, rows 4 to 6 say what the verdict
rests on, and row 7 measures what row 6 can see.

Every row reads the same series, vintage and specification, so the three are
stated once here.

1. **The series.** `CADAUD=X`, yfinance's quote of the rate Chan names, in
   Australian dollars per Canadian dollar. It is the rate itself rather than a
   stand-in for a class of instruments, which is what lets row 1 carry a
   verdict where Entry 5 cannot. The owner confirmed it on 2026-10-02, before
   anything was downloaded.
2. **The vintage.** `yfinance_cadaud=x_raw_2005-07-04_2026-09-30_dl2026-10-02.csv`,
   downloaded 2026-10-02. The basis is raw, which for a rate means the vendor's
   close with no adjustment, because none applies. The test reads from
   2007-08-06 to 2026-09-30, 4,984 days, because the vendor returned nothing
   for the 90 weekdays from 2007-04-02 to 2007-08-03 and a lagged regression
   across that gap would treat four months as one day.
   [data/README.md](../data/README.md) says how the rows were filtered.
3. **The specification.** An augmented Dickey-Fuller test with a constant and
   no trend, on the log of the rate, at one lag, against `ADF_CRIT_CONST`. The
   residual check fits the same constant and reads ten autocorrelations against
   the ±1.96/√n band and a Breusch-Godfrey test over the same ten lags at the
   10% cut, and its search stops at Schwert's ceiling of 32 lags. The scan uses
   252-day windows stepped by 21. Entry 5 uses the same lag rule and scan, so
   the two entries read one specification where they can.

Every result here is **exploratory**. The sample was spent on a claim Chan
stated about one named rate, so the entry says whether that rate was
stationary over this window and nothing about whether trading it pays.

### What the book printed

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | The CAD/AUD cross rate is quite stationary | the claim, with no figure | Kindle location 3951 |
| 2 | The ADF statistic at one lag | nothing, the book works no example | n/a |
| 3 | The residual check, and the first lag count whose residuals pass | nothing | n/a |
| 4 | The half-life | nothing | n/a |
| 5 | The test on the rate quoted the other way, and on the level | nothing | n/a |
| 6 | The rolling scan | nothing | n/a |
| 7 | How often a series that truly reverts at row 4's half-life rejects in row 6's scan | nothing | n/a |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2007-08-06 to 2026-09-30 | rows 2 and 3 read against the declared criterion, both below the 5% bar of −2.86 | both clear it | `TestTheCrossRateVerdict::test_it_is_reproduced` |
| 2 | 2007-08-06 to 2026-09-30 | ADF on the log of the rate, constant, one lag | t −3.2136 on 4,982 observations, rejecting at 5% | `TestTheCrossRateStatistic::test_the_lag_one_statistic` |
| 3 | 2007-08-06 to 2026-09-30 | the residual check on the one-lag fit, then the smallest lag count from 0 to 32 whose residuals pass both halves | one lag fails, Breusch-Godfrey p 0.0002 and residual lags 2, 6, 7 and 10 outside the band. The first passing count is 10, t −2.9946, Breusch-Godfrey p 0.6487 | `TestTheCrossRateResidualCheck::test_the_lag_one_fit_fails_it` and `::test_the_first_fit_that_passes_still_rejects` |
| 4 | 2007-08-06 to 2026-09-30 | OU half-life on the log of the rate | 141.6 trading days | `TestTheCrossRateStatistic::test_the_half_life` |
| 5 | 2007-08-06 to 2026-09-30 | rows 2 and 3 on the log negated, on the level, and on the inverted level | −3.2136 negated. On the level −3.2944 at one lag and −3.0241 at the first passing count, 10. Inverted, −3.1552 and −2.9734, also at 10 | `TestTheCrossRateStatistic::test_the_quoting_direction_does_not_move_it` and `::test_on_the_level_both_statistics_the_verdict_reads_still_reject` |
| 6 | 226 windows ending 2008-07-30 to 2026-09-21 | 252-day windows stepped by 21, row 2's test in each | 23 clear 10% and 5 clear 5% | `TestTheCrossRateScan::test_the_counts` |
| 7 | 1,000 simulated paths of 4,984 days | a Gaussian AR(1) reverting at row 4's half-life, from the stationary distribution, seed 20261002, scanned as row 6 is. Declared on [issue 212](https://github.com/l3a0/quantitative-trading/issues/212) before any number was computed | 27.0 of 226 windows clear 10% on average, 12.0%, and 14.0 clear 5%, 6.2%. 388 paths have 23 or fewer past 10%. 968 reject at 5% over the whole path. Added after the results were seen, not declared: 73 have 5 or fewer past 5% | `TestTheWindowPower` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The criterion was declared on the issue before any statistic was computed: the one-lag statistic and the statistic at the first residual-clean lag count both below the 5% bar. They are −3.2136 and −2.9946. Neither clears 1%, at −3.43, so "quite stationary" holds at the level the criterion asks for and no stronger. |
| 2 | none, not a replication | The headline statistic. Lag 1 was fixed before any number was seen, as the rule [issue 136](https://github.com/l3a0/quantitative-trading/issues/136) set for both candidates. Every count from 0 to the ceiling of 32 also rejects at 5%, the closest being 6 at −2.8739, so the lag rule does not decide the verdict here. `::test_every_lag_up_to_the_ceiling_rejects_at_five_percent` pins that. |
| 3 | none, not a replication | The one-lag fit leaves autocorrelation, so its statistic is read against critical values that do not apply. The fit that earns them is further from rejecting and still past the bar. Without the constant the check would audit a different regression, whose one-lag statistic is −2.5159 rather than −3.2136 and is read against a different table, so the check would no longer be about this test. |
| 4 | none, not a replication | The book prints no half-life. At 141.6 trading days a deviation takes a little over half a year to halve, which is a rate that pulls back slowly. |
| 5 | none, not a replication | Chan writes CAD/AUD and the vendor quotes it the other way, so the test was run on the log, where the two directions give one answer. On the level they part, and both statistics the verdict reads still reject at 5% in both directions, so the scale did not decide the verdict either. |
| 6 | none, not a replication | A description of the window, not a second verdict. About one window in ten clears 10%. A 252-day window holds under two half-lives of the full window's estimate. No window that rejects is promoted to a claim, under [issue 16](https://github.com/l3a0/quantitative-trading/issues/16)'s rule. Three windows have no finite half-life, because their fit does not revert. |
| 7 | none, not a replication | A measure of row 6's power. A series that certainly reverts this slowly clears 10% in 12.0% of its windows, against about one in ten for a series that does not revert at all, which is what a 10% bar means. So row 6 barely separates the two, and only the whole span does: it rejects at 5% in 968 of 1,000 paths. Row 6's 23 sits near the middle of the simulated counts. At 5% only 73 paths have 5 or fewer, as the rate does, a number added after the results were seen. The model has neither the rate's fat tails nor its changing volatility, and a half-life estimated from 4,984 days reads short, so the true reversion may be slower than row 4's. This shows that slow reversion can produce so few rejecting windows, and not that it is why the rate does. Exploratory. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Chan's claim reproduces at 5% on a modern download.** Over 2007-2026 the
   CAD/AUD rate rejects a unit root under the criterion fixed before the
   statistic was read, on both statistics the criterion names. Every lag count
   up to the ceiling rejects too, and so does the level in either quoting
   direction. The log, the constant and the window start were fixed on the
   issue before any statistic, and none was tried another way except the scale.
2. **It is a slow reversion, and only the whole window shows it.** A half-life
   of 141.6 trading days means a deviation takes a little over half a year to
   halve, and only 23 of 226 one-year windows reject at 10%. Over the full
   window the rejection holds, and in a year of data it usually does not.
   Row 7 measures what a year of data can see. A simulated series that truly
   reverts at this half-life clears 10% in 12.0% of its one-year windows,
   against about one in ten for a series that does not revert, and rejects
   over its whole span in 968 of 1,000 paths. So the windows barely tell the
   two apart, the rate's 23 can come from either, and the whole-window
   rejection is what separates them. At 5% the rate's 5 windows are fewer
   than most simulated paths give, which row 7 reports and does not explain.
3. **The residual check moves the statistic and not the verdict.** The one-lag
   fit fails it, as Entry 5's one-lag fits do, and the first passing fit is at
   10 lags. That fit still rejects, closer to the bar than the one-lag fit, so
   here the check narrows the margin rather than reversing anything.

### What this entry cannot say

Three things.

**Whether the rate behaved the same before August 2007.** The vendor's history
starts in July 2005, and the 454 rows before its gap are kept in the vintage
and not read by the test, so the two years before the window are untested.

**Whether the result survives another vintage.** The vendor does not restate an
FX close for a corporate action, because a currency has none, but it can fill
or change its own history, and the 2007 gap is the sign that its history has
holes. `TestTheCrossRateVintage::test_the_gap_the_start_rests_on_is_in_the_vintage`
fails if a recorded download fills the gap, so the window cannot quietly move.

**Whether trading the rate pays.** Stationarity is a statement about the
series. A trade adds costs, carry from the two interest rates, and the
question of sizing against a half-life this long, and none of those are here.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/stationary-candidates-lessons.md](../blog/stationary-candidates-lessons.md)
moves with it, since that post quotes most of these figures. So do its
three figures, which `uv run python -m chan.stationary_candidates_figures`
redraws.

## Entry 7: the equity seasonals, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, Examples 7.6 and 7.7, in both editions. Shipped
under [issue 18](https://github.com/l3a0/quantitative-trading/issues/18).

Eighteen rows, all derivable from
[tests/test_equity_seasonals.py](../tests/test_equity_seasonals.py).

**Every figure the committed files reach reproduces, in every printout.** Chan
prints these two examples in four ways: the first edition's MATLAB, and the
revised edition's MATLAB, Python and R. Fourteen printed figures need only data
this repo holds, and all fourteen land on the digits their source prints. None
of them lands from the strategy's description alone. Each needs the rules its
own script applies, and the issue records the figure each rule gives when it is
changed.

Chan publishes both strategies as already dead, so reproducing them checks
whether a documented disappearance is visible in data a reader can get. Every
printout's whole-period figure is negative on his files, as he printed it. What
the files cannot show is the 13 percent before 2002 that a disappearance would
be measured against, so this entry gives no verdict on one.

Each example reads one of two vintages.

1. **Example 7.6** reads `data/ijr_20080114/`, the 600 S&P 600 members lifted
   from Chan's `IJR_20080114.mat`, vendor `chan-mat`, recorded as
   split-adjusted, saved 2008-01-15, spanning 2004-01-15 to 2008-01-14.
2. **Example 7.7** reads `data/spx_20071123/`, the 500 S&P 500 members lifted
   from `SPX_20071123.mat`, the same vendor and basis, saved 2007-11-24,
   spanning 1999-11-24 to 2007-11-23.

[data/README.md](../data/README.md) holds both. Each file holds only the
companies in its index on the day Chan saved it, carried backwards, which is
the first thing this entry cannot get past.

The specification is the script. Rows 1 to 6 are Example 7.6, rows 7 to 14 are
Example 7.7, and rows 15 to 18 split one of them at 2002. Each row names the
printout whose rules it runs, and `chan.equity_seasonals` holds those rules as
`JANUARY_RULES` and `HESTON_SADKA_RULES`.

Two of the four printouts have no code file in this repo. The revised
edition prints its Example 7.7 in MATLAB on p. 179 and in R on p. 181, and the
owner read both listings from the Kindle book on 2026-10-03.
[Issue 226's comment on the printed code](https://github.com/l3a0/quantitative-trading/issues/226#issuecomment-5973504942) quotes the expressions that
decide each rule, and rows 9, 10, 13 and 14 run those rules.

1. **The R needs no repair**, because it indexes the daily closes, and
   `R_HESTON_SADKA` follows it with no change.
2. **The MATLAB needs one repair to run.** It cuts its closes to month-end rows
   and then reads one by a daily row number. `REVISED_MATLAB` reads the
   month-end row instead and follows the listing everywhere else.
3. **The page leaves `smartstd` open.** The listing calls it, and pp. 179 to
   181 do not print its body. Chan's two books ship two versions, and only
   *Algorithmic Trading*'s prints row 10's digits.
4. **The revised code's repost settles both.** The revised edition's MATLAB as
   reposted at pinhaocheng/epchan-quant_trading_MATLAB_codes `7430b84` holds an `example7_7.m` whose mask already
   reads the month-end row, and which matches `REVISED_MATLAB` everywhere
   else, down to the −0.0129 and −0.1243 in its closing comment. Its
   `smartstd.m` divides by n, which is book two's. The repost is a third
   party's copy rather than the book, so the page stays the source for rows 9
   and 10, and the repost is what confirms the two choices the page does not
   decide.

Rows 5 and 6, and the revised edition's half of rows 1 and 2, rest on a
different inference: the figures match the first edition's, so its rules are
assumed.

Every result here is **exploratory**. A replication spends the sample on a
hypothesis Chan chose, and rows 15 to 18 were computed before any criterion for
"disappeared" was written down.

### What the book printed

| # | Row | Published | Where |
| --- | --- | --- | --- |
| 1 | 7.6, entered 2005-12-30, MATLAB in both editions | −0.0244 | `example7_6.m` at `1a71950`, printed in its closing comment. The revised edition prints the same figure, which the owner read on 2026-10-02 |
| 2 | 7.6, entered 2006-12-29, MATLAB in both editions | −0.0068 | as row 1 |
| 3 | 7.6, exited 2006-01-31, revised Python | −0.023853 | `example7_6.py` at `653cf92` in liujiantong/epchan_books, printed in its closing comment |
| 4 | 7.6, exited 2007-01-31, revised Python | −0.003641 | as row 3 |
| 5 | 7.6, January 2006, revised R | −0.0244 | the revised Kindle edition, as the owner read it on 2026-10-02 |
| 6 | 7.6, January 2007, revised R | −0.0068 | as row 5 |
| 7 | 7.7 average annual return, first-edition MATLAB | −0.9167 | `example7_7.m` at `1a71950`, printed in its closing comment |
| 8 | 7.7 Sharpe ratio, first-edition MATLAB | −0.1055 | as row 7 |
| 9 | 7.7 average annual return, revised MATLAB | −0.0129 | the revised Kindle edition, p. 179, in the listing's closing comment, as the owner read it on 2026-10-02 and 2026-10-03 |
| 10 | 7.7 Sharpe ratio, revised MATLAB | −0.1243 | as row 9 |
| 11 | 7.7 average annual return, revised Python | −0.012679 | `example7_7.py` at `653cf92`, printed in its closing comment |
| 12 | 7.7 Sharpe ratio, revised Python | −0.122247 | as row 11 |
| 13 | 7.7 average annual return, revised R | −0.01139674 | the revised Kindle edition, p. 181, read on the same two days as row 9 |
| 14 | 7.7 Sharpe ratio, revised R | −0.1095098 | as row 13 |
| 15 | 7.7 annual return before 2002 | more than 13 percent, Heston and Sadka's sample rather than this file | Kindle location 4425 |
| 16 | 7.7 Sharpe ratio before 2002 | nothing | n/a |
| 17 | 7.7 annual return from 2002 | the effect "has disappeared since then" | Kindle location 4425 |
| 18 | 7.7 Sharpe ratio from 2002 | nothing | n/a |

None of rows 1 to 14 is among the committed highlights, because each is printed
beside code rather than in a sentence somebody marked.
[research/book-notes/README.md](../research/book-notes/README.md) records that
absence. Rows 5, 6, 9, 10, 13 and 14 trace to
[the owner's comment on issue 18](https://github.com/l3a0/quantitative-trading/issues/18#issuecomment-5960594931),
which tables every figure the revised edition prints for both examples. The
code behind rows 9, 10, 13 and 14 traces to
[the comment on issue 226](https://github.com/l3a0/quantitative-trading/issues/226#issuecomment-5973504942).

### What this repo computed

| # | Printout's rules | Computed | Gap, computed minus published | Assertion |
| --- | --- | --- | --- | --- |
| 1 | `MATLAB_JANUARY`: month-ends by row, the number of stocks in a tenth rounded half away from zero, 58 long and 58 short of 578 ranked | −0.0244 | 0.0000 | `TestJanuaryMatlab::test_the_two_reachable_januaries_reproduce` |
| 2 | as row 1, 59 long and 59 short of 592 ranked | −0.0068 | 0.0000 | as row 1 |
| 3 | `PYTHON_JANUARY`: year-end closes forward-filled before ranking, as pandas before 3.0 did, and a winners' slice of `topN - 2` that leaves out the best, 58 long and 56 short of 579 ranked | −0.023853 | 0.000000 | `TestJanuaryPython::test_the_two_reachable_januaries_reproduce` |
| 4 | as row 3 | −0.003641 | 0.000000 | as row 3 |
| 5 | `R_JANUARY`: row 1's rules with R's half-to-even rounding | −0.0244 | 0.0000 | `TestJanuaryR::test_the_two_reachable_januaries_reproduce` |
| 6 | as row 5 | −0.0068 | 0.0000 | as row 5 |
| 7 | `FIRST_EDITION_MATLAB`: month-ends by row, a stock kept or dropped on another stock's close because a sorted row is read against one in column order, a monthly sum over positions, `smartmean` over 95 months and `smartstd` | −0.9167 | 0.0000 | `TestHestonSadkaFirstEdition::test_both_figures_reproduce` |
| 8 | as row 7 | −0.1055 | 0.0000 | as row 7 |
| 9 | `REVISED_MATLAB`: the printed code with its out-of-range index repaired, each stock kept only if its own close exists, each month divided by its positions, 83 months, *Algorithmic Trading*'s `smartstd` | −0.0129 | 0.0000 | `TestHestonSadkaRevisedMatlab::test_both_figures_reproduce` |
| 10 | as row 9 | −0.1243 | 0.0000 | as row 9 |
| 11 | `PYTHON_HESTON_SADKA`: each stock's last priced day, kept only if its own return exists, 83 months, standard deviation over n | −0.012679 | 0.000000 | `TestHestonSadkaPython::test_both_figures_reproduce` |
| 12 | as row 11 | −0.122247 | 0.000000 | as row 11 |
| 13 | `R_HESTON_SADKA`: the printed code, row 9's selection with half-to-even rounding, 83 months, standard deviation over n − 1 | −0.01139674 | 0.00000000 | `TestHestonSadkaR::test_both_figures_reproduce` |
| 14 | as row 13 | −0.1095098 | 0.0000000 | as row 13 |
| 15 | row 11's months from 2000-12-31 to 2001-12-31, 13 of them | −0.145387 | none, not a replication | `TestTheSplitAt2002::test_the_two_halves` |
| 16 | as row 15 | −0.859993 | none | as row 15 |
| 17 | row 11's months from 2002-01-31 to 2007-10-31, 70 of them | 0.011967 | none, not a replication | as row 15 |
| 18 | as row 17 | 0.141777 | none | as row 15 |

Each of rows 1 to 14 is asserted twice: its full value at `abs=1e-9`, and its
rounding at the precision its source prints. So the computed column quotes the
printed precision, and the gap is zero at that precision.

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The script cannot run on this file as written. The file holds four December year-ends and four January month-ends. The script drops the first January. Its check that each January follows its December then compares three dates against four. Pairing each year-end with the January after it inside the file reaches the first two holdings. Rounding the decile down instead gives −0.0234. |
| 2 | reproduced | as row 1 |
| 3 | reproduced | Taking the full top decile instead gives rows 1 and 2 to every digit, so on this file the two editions differ by the winners' slice alone. Without the forward fill the script ranks 578, as MATLAB does, and the return does not move. |
| 4 | reproduced | as row 3 |
| 5 | reproduced | Inferred rules, as the entry's opening says. No decile on this file lands on a half, so R's rounding and MATLAB's give the same stocks. |
| 6 | reproduced | as row 5 |
| 7 | reproduced | The return is a sum over every position held that month, never divided by their number, so −0.9167 is in units of summed positions rather than a fraction of capital. Keeping each stock on its own close instead gives −1.0822, and averaging over the 83 months that hold positions gives −1.0492. Dividing each month by its positions gives −0.0120 a year, a figure this repo derived and Chan did not print. |
| 8 | reproduced | Skipping the NaN month in the standard deviation instead of counting it as zero gives −0.1049. |
| 9 | reproduced | The printed code with one repair. As printed, it reads a daily row of a 96-row array and cannot run. The repair reads the month-end row, and because the printed mask removes stocks by column, it keeps each stock on its own close. Keeping the first edition's sorted-against-columns rule instead gives −0.0120 and does not print. Keeping each stock on its own return also prints −0.0129, so the code chooses the close where four decimals cannot. |
| 10 | reproduced | As row 9. Pp. 179 to 181 do not print `smartstd`, and the revised code's repost ships book two's. *Algorithmic Trading*'s, which skips a month with no position and divides by n, prints −0.1243. The first edition's gives −0.1236. Every month the drop removes holds no position, so under the former the drop count moves no figure. Under the first edition's it does: dropping 12 also prints −0.1243 by counting one empty month as zero, which is the reading this row ran before the code was read, and dropping none gives −0.1330. |
| 11 | reproduced | Taking one shared row per month instead gives −0.012917. |
| 12 | reproduced | Dividing by n − 1 instead gives −0.121508. |
| 13 | reproduced | The printed code, unchanged, and the tightest of rows 9 to 14, because R prints seven significant digits. Rounding half away from zero instead gives −0.0118031, and keeping each stock on its own return gives −0.0117146. |
| 14 | reproduced | Dividing by n instead gives −0.1101755. |
| 15 | none, not a replication | Heston and Sadka's 13 percent is from their own sample, which this file does not reach. It has 13 months before 2002 after the twelve-month lookback, and they lost. |
| 16 | none, not a replication | as row 15 |
| 17 | none, not a replication | Location 4425's claim is a verdict, and `### Rows that are not replications` would let it be pinned as one. It is not, because Entry 6's rule wants the criterion written before any statistic, and these were computed first. |
| 18 | none, not a replication | as row 17 |

### What the entry concludes

Three things.

1. **Every reachable figure reproduces, and not under the strategy as
   described.** The fourteen rows land at the precision each printout gives.
   Each of these five rules moves a printed figure, and none is in the
   description:
   1. keeping or dropping a stock on another stock's close,
   2. a monthly sum rather than a mean over positions,
   3. months with no position counted as zero in the mean,
   4. a standard deviation that counts a NaN month as zero,
   5. a winners' slice that leaves out the best stock.
2. **The four Heston and Sadka printouts disagree on units and agree on sign.**
   The first edition's −0.9167 is a sum over positions. The revised edition
   divides by the positions, and its three printouts land between −0.0114 and
   −0.0129 a year. All four lose money on this file.
3. **Under the revised Python's rules, the loss sits before 2002.** Rows 15
   to 18 show the 13 months before 2002 returning −0.145387 a year and the 70
   after returning 0.011967. Only that printout's rules were split. It is a
   finding about survivors over one short window, with no verdict, and it
   says nothing about Heston and Sadka, whose sample this file does not
   reach.

### The third January return the committed file cannot reach

Chan's third Example 7.6 holding was entered at the close of 2007-12-31 and
closed on 2008-01-31. The book's text says the strategy "worked wonderfully"
that January after failing in 2006 and 2007. `IJR_20080114.mat` ends on
2008-01-14, so no printout's rules can compute it here, and the two Januaries
this entry reproduces are the two that lost.

This follows the shape Entry 3 used for two figures from Chan's workbook until
[issue 192](https://github.com/l3a0/quantitative-trading/issues/192) committed
the column they needed and gave them rows. It is a section rather than rows, because the log has no row state for a
published figure with no computed value.

1. **0.0881**, printed by the MATLAB in both editions and by the revised R.
2. **0.088486**, printed by the revised Python.

`TestJanuaryMatlab::test_the_third_january_is_not_reached` holds that the
file's last day is 2008-01-14 and that 2007-12-31 is the only ranked year-end
left unreached.
[Issue 225](https://github.com/l3a0/quantitative-trading/issues/225) carries
reaching it and the owner question it waits on.

### What this entry cannot say

Three things.

**Whether the effect existed before 2002.** Both files hold only the companies
still in their index on the day Chan saved them, and the S&P 500 file starts
in November 1999. [Issue 196](https://github.com/l3a0/quantitative-trading/issues/196)
is where the 13 percent is tested on a panel that still holds the companies
that left.

**How the revised R rounds Example 7.6.** It is assumed from its Example 7.7
code. The revised MATLAB's `smartstd`, which the page leaves open, is settled
by the revised code's repost.

**What happened after 2007.** After Example 7.7 the revised edition says the
most recent five years give even worse average returns. Neither file reaches
those years, so nothing here reads that claim.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/equity-seasonals-lessons.md](../blog/equity-seasonals-lessons.md) moves
with it, since that post quotes most of these figures. So does its one figure,
which `uv run python -m chan.equity_seasonals_figures` redraws.

## Entry 8: the Khandani-Lo reversal, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.7, Kindle locations
2099, 2137 and 2233. Shipped under
[issue 17](https://github.com/l3a0/quantitative-trading/issues/17).

Three computed rows, all derivable from
[tests/test_khandani_lo.py](../tests/test_khandani_lo.py).

**Both of Chan's figures reproduce at the precision he printed.** The rule buys
the stocks that fell most against the market yesterday and shorts the ones that
rose most. On his own S&P 500 file over 2006 it earns a Sharpe ratio of 0.2510
before costs, against his 0.25, and −3.1884 after 5 basis points a trade,
against his −3.19. A cost a large-cap trader pays every day turns a small edge
into a large loss, and that collapse is the lesson the example was printed to
teach.

The second figure reproduces only because two quirks of Chan's code are kept.
His script never charges the first day's rebalance, which leaves that day's
after-cost profit as NaN. His `smartstd` then counts that NaN as 0 while his
`smartmean` skips it. A port that skips the NaN in both, the way pandas does,
gives −3.1822 and misses −3.19 by one unit. Row 3 removes both quirks and
gives −3.2337, a little worse than Chan printed.

Two rows are replications and one is not. Rows 1 and 2 are the two figures
Chan prints. Row 3 is the same run with both quirks removed, which Chan prints
no figure for, so it carries no verdict.

Two figures from the book have a row in the first table and none in the other
two.

1. **Khandani and Lo's 4.47**, the Sharpe ratio they report for 2006. It was
   computed on their own universe, which this repo does not hold, so nothing
   here computes it and it takes no verdict. Chan's figure is about the S&P
   500, and the distance between his 0.25 and their 4.47 is his point rather
   than a gap.
2. **Chan's explanation**, that most of their returns came from small and
   microcap stocks. It is a claim about a universe this run does not read.
   Location 2236, at the end of Example 3.8, leaves rerunning the strategy on
   the S&P 400 and S&P 600 as an exercise, which would test it, and nothing
   here runs that.

Every row reads the same vintage, window and specification, so the three are
stated once here.

1. **The vintage.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, lifted one vintage per stock, saved 2007-11-24, and read
   back as one frame through `chan.series.load_panel`.
   [data/README.md](../data/README.md) says where the file came from. It is
   the S&P 500 as it stood on 2007-11-23, carried backwards, so a company that
   left the index before then is absent. Of the 500, 491 are priced on the
   window's first day and 495 on its last. **Every figure here is about
   survivors.** [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198)
   is where the same rule runs on the index as it stood in 2006, and
   [issue 213](https://github.com/l3a0/quantitative-trading/issues/213) is
   Chan's own demonstration of what survivorship does.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days. Returns,
   weights and profit are computed on the whole file and only then cut, so the
   window's first profit uses the weights from the day before it.
3. **The specification.** Chan's `example3_7.m`, read in the mirror
   [egorpe/EPChan-QuantitativeTrading](https://github.com/egorpe/EPChan-QuantitativeTrading)
   at `1a71950`. A stock's weight is minus its return less the equal-weighted
   market's, divided by the count of stocks with a close that day, and 0 where
   either day's close is missing. The weights are held for one day and sum to
   zero across stocks. The cost is 5 basis points on each side of a change in
   weight, which is location 998's convention that a round trip is two
   transactions. The Sharpe ratio is √252 times the mean over the standard
   deviation, with no risk-free rate subtracted.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 sample on a rule somebody else chose, so the entry says whether his
numbers reproduce on his file and nothing about whether the rule pays today.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Sharpe ratio on the S&P 500 in 2006, before costs | 0.25 | Kindle location 2137, and again at 2233 |
| 2 | Sharpe ratio after 5 basis points a trade | −3.19 | location 2233 |
| 3 | Sharpe ratio after costs, with the first day charged and nothing zero-filled | none, the book prints no such figure | n/a |
| 4 | Khandani and Lo's Sharpe ratio for 2006, on their own universe | 4.47 | location 2099 |
| 5 | Chan's explanation of the drop | that most of their returns came from small and microcap stocks, a claim rather than a figure | location 2137 |

### What this repo computed

| # | Window | Specification | Computed | Assertion |
| --- | --- | --- | --- | --- |
| 1 | 2006-01-03 to 2006-12-29 | Chan's rule before costs, his `sharpe` | 0.2510 | `TestTheFigures::test_before_costs` |
| 2 | 2006-01-03 to 2006-12-29 | Chan's rule after costs, his `sharpeminustcost`, with the first day uncharged and its NaN counted as 0 in the deviation | −3.1884 | `TestTheFigures::test_after_costs_with_both_quirks` |
| 3 | 2006-01-03 to 2006-12-29 | row 2 with the first day charged from the weights before the window, so no day is NaN | −3.2337 | `TestTheFigures::test_after_costs_with_both_quirks_removed` |

`TestTheQuirksMoveTheFigure::test_dropping_the_nan_misses_chans_second_digit`
holds the −3.1822 a pandas port gives, and that it misses −3.19.

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.00 | reproduced | Chan's claim is that the rule earns a mediocre Sharpe ratio on the S&P 500 in 2006, far below Khandani and Lo's. On his own file and his own code it lands on his figure at the two decimals he printed. |
| 2 | 0.00 | reproduced | The claim is that 5 basis points a trade turns that small edge into a large loss, and it survives at his printed precision. It lands there only with both quirks of his code kept, which is the specification the figure came from rather than a choice made to close a gap. |
| 3 | none | none, not a replication | Chan prints no figure for it. It is here because it is the after-cost figure with the first day charged, so its series holds no NaN for the deviation to count as 0. It lands a little below Chan's figure, so the two quirks moved his figure in his favour without moving the claim. |

### What the entry concludes

Three things, and the first is the verdict.

1. **Both figures reproduce on Chan's own file.** The vintage explanation that
   carries Entry 1's misses is not needed here, because the file is his and
   the code transcribes his script. What the entry adds
   is that his second figure depends on how his helpers treat one NaN, so a
   careful port of the formula alone misses it.
2. **On the S&P 500 the daily cost is larger than the daily edge.** A Sharpe
   ratio of 0.2510 before costs and −3.1884 after is a rule whose average
   daily profit is smaller than the average cost of rebalancing into it every
   day. On the specification of row 3, the average day's cost is 13.7453
   times its average profit. The rule trades 1.4505 times its average gross
   position a day. `TestWhatAnAverageDayCosts` holds both. Removing the
   quirks makes the after-cost figure slightly worse, not better.
3. **The universe is survivors, and nothing here measures what that cost.**
   Every stock that left the S&P 500 before 2007-11-23 is missing, whether it
   failed or was taken over, so neither the size nor the sign of the effect on
   either figure is known.
   [Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) is
   what would measure it.

### What this entry cannot say

Four things.

**Whether Khandani and Lo's figure reproduces.** It was computed on a universe
this repo does not hold, so it stays a cited number.

**Whether Chan's explanation holds.** The rule on small caps is the test of
it, and Chan leaves that as an exercise. The S&P 600 file under
`ijr_20080114/` spans 2006, and running the rule on it would be a finding with
no published figure to check, like Entry 5, rather than a replication.
[Issue 249](https://github.com/l3a0/quantitative-trading/issues/249) runs it.

**What survivorship cost.** Neither its size nor its sign is measured.

**What trading at the open gives.** That is Example 3.8, and Entry 10
carries it. Entry 10 also reproduces Chan's Python notebook for this example,
which prints 0.9578 and −2.1617 rather than 0.25 and −3.19, because its rule
differs from `example3_7.m` in six ways and its forward-fill reads WYN's gap
as one day's move.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post quotes most of these figures. So does its
running-profit figure, which `uv run python -m chan.survivorship_and_costs_figures`
redraws.

## Entry 9: the survivorship toy, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.3, between the
highlights at Kindle locations 1423 and 1474. Shipped under
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213).

Chan warns at location 1012 that a database holding only surviving stocks
inflates a backtest that buys cheap stocks, because some stocks are cheap
because the company is about to fail. Example 3.3 is the toy he points to. It
buys the 10 lowest-priced stocks among the 1,000 largest by market
capitalisation at the close on 1/2/2001, with equal capital in each, and sells
at the close on 1/2/2002. The book prints two tables of ten picks.

1. **The survivorship-free picks.** Nine of the ten were delisted during the
   year, so the book gives each a terminal price, the last price traded on or
   before 1/2/2002. Only MDM has a close on that date.
2. **The survivor-only picks.** A database holding only survivors keeps MDM and
   continues up the price ranking past the nine stocks it never held.

The label is a revised-edition one, and this entry declares it because the
repo reads an example number as first-edition unless it says otherwise. Whether the 2009
edition numbers this example 3.3 and prints the same tables was not checked.
The first-edition code mirror this repo cites elsewhere holds no file for it
among its Chapter 3 files, so the printed tables are the whole source.

Five rows, all derivable from
[tests/test_survivorship_bias.py](../tests/test_survivorship_bias.py). Rows 1
and 2 are the two figures the book prints. Rows 3 and 4 are the equal-shares
near miss on each table, and row 5 is the survivor-only figure with NEOF on one
share basis. Those three carry no published figure and say so in their own
cells.

**The vintage column says `none, the book's printed tables` in every row.** The
twenty rows are copied from the book into
[src/chan/survivorship_bias.py](../src/chan/survivorship_bias.py), whose
docstring names their source, and nothing was downloaded. A printed number
cannot be restated by a vendor, so the edition is what pins it.
[docs/design.md](design.md#a-replication-that-reads-the-books-own-tables) says
why that is not a vintage. The cell names no price basis, because the book does
not say whether its database adjusted for splits, and row 5 shows that at least
one row was not adjusted.

**The window column stays.** Entry 2 dropped it because a gamble has no window,
and this toy has one in every row, because the book fixes the dates.

Neither epistemic label reaches this entry, for the reason Entry 2 gives.
Reproducing the arithmetic on a printed table spends no sample.

### What the book printed

| # | Row | Published figure | Where the book prints it |
| --- | --- | --- | --- |
| 1 | Survivorship-free portfolio, equal capital | −42 percent, the return Chan says a trader would actually have had | Kindle location 1471 |
| 2 | Survivor-only portfolio, equal capital | 388 percent, which Chan calls fictitious | Kindle location 1471 |
| 3 | Survivorship-free portfolio, equal shares | none, the book specifies equal capital | n/a |
| 4 | Survivor-only portfolio, equal shares | none, the book specifies equal capital | n/a |
| 5 | Survivor-only portfolio with NEOF on one share basis | none, the book prints NEOF's row as it stands | n/a |

### What this repo computed

| # | Window | Specification | Vintage | Computed | Assertion |
| --- | --- | --- | --- | --- | --- |
| 1 | 1/2/2001 to 1/2/2002 | mean of the ten per-stock returns, end over start less one, each delisted stock at its terminal price | none, the book's printed tables | −41.72 percent | `TestBookFigures::test_the_survivorship_free_portfolio_loses_42_percent` |
| 2 | 1/2/2001 to 1/2/2002 | the same mean over the survivor-only picks | none, the book's printed tables | 387.88 percent | `TestBookFigures::test_the_survivor_only_portfolio_gains_388_percent` |
| 3 | 1/2/2001 to 1/2/2002 | one share of each, the sum of end prices over the sum of start prices less one | none, the book's printed tables | −47.62 percent | `TestTheNearMiss::test_equal_shares_on_the_survivorship_free_picks` |
| 4 | 1/2/2001 to 1/2/2002 | the same over the survivor-only picks | none, the book's printed tables | 373.17 percent | `TestTheNearMiss::test_equal_shares_on_the_survivor_picks` |
| 5 | 1/2/2001 to 1/2/2002 | row 2's mean with NEOF's start price multiplied by 10, the ratio of its 2001 reverse split | none, the book's printed tables | 100.91 percent. As printed, NEOF carries 308.86 of row 2's 387.88 points | `TestTheReverseSplit::test_on_one_share_basis_the_survivor_portfolio_still_gains` and `::test_neof_carries_most_of_the_survivor_only_return` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0 at the whole percent the book prints | reproduced | Chan's claim is that a trader running this strategy on the stocks actually available would have lost money. The equal-capital mean is negative and rounds to his figure, so the claim survives. |
| 2 | 0 at the whole percent the book prints | reproduced | Chan's claim is that a survivor-only backtest turns that loss into a large gain. The figure reproduces from his table as printed. Most of it rests on NEOF's row, which compares a price before a reverse split with a price after it, and row 5 puts it on one basis. The claim survives there at a gain against a loss, so the verdict stays with the figure, as Entry 1's row 11 does, and this column carries the qualification. |
| 3 | none | none, not a replication | The book specifies equal capital. The row exists so the specification is held rather than the number: buying one share of each gives −47.62 percent, which does not round to −42. |
| 4 | none | none, not a replication | The same near miss on the second table. It gives 373.17 percent, which does not round to 388. The two misses together are what rule the weighting out. |
| 5 | none | none, not a replication | The book prints NEOF's row unadjusted. Neoforma's FY2001 10-K, [on EDGAR](https://www.sec.gov/Archives/edgar/data/1096219/000101287002001537/d10k.htm), states a 1-for-10 reverse split effective 2001-08-27 and restates its quarterly price tables for it, so 0.875 is a price before the split and 27.9 a price after it. On one basis the survivor-only portfolio still gains, which is the claim row 2 supports, and by far less than the printed figure. |

### What the entry concludes

Three things, and the first is why the verdicts carry less than they look.

1. **The verdicts were knowable before the work started.** As with Entry 2,
   nothing can move a printed table's arithmetic, so rows 1 and 2 could only
   reproduce once the right weighting was found. The work is worth the
   specification it settles and the row it checked against an outside source.
2. **The book prints no formula, so the weighting is what rows 1 to 4 hold.**
   Equal capital reproduces both figures, and equal shares misses both. Both
   are pinned, because an assertion on the right figure alone would hold a
   number rather than a choice.
3. **One stock carries most of the fictitious return, and its row mixes two
   share bases.** NEOF contributes 308.86 of the 387.88 points. With its start
   price on the basis of its reverse split, the survivor-only portfolio returns
   100.91 percent. The lesson survives, since −41.72 against 100.91 is still a
   loss against a gain, but the difference between the two portfolios is much
   smaller once NEOF's row is on one share basis. That is a finding about
   Chan's table, and it does not change what the table as printed reproduces
   to.

Chan tells the same toy a second time. The notes on his *Algorithmic
Trading*, at location 704 in
[research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md),
give the same 388 percent but describe the honest outcome as "almost 100
percent loss" rather than −42 percent. That is the same author with a
different number, cited from the note and not reproduced.

### What this entry cannot say

Three things.

**Whether the picks are right.** The universe of 1,000 stocks is not printed,
so the selection step cannot be re-run. Re-running it would need the 1,000
largest US stocks as they stood on 2001-01-02, delisted ones included, which is
bought data. No issue is filed for it, because both printed figures sit
downstream of the picks.

**Whether the other nineteen rows sit on one share basis.** Only NEOF was
checked against a filing. The rest are taken as printed, so row 5 corrects the
one row known to mix two bases and claims nothing about the others.

**Whether buying cheap stocks pays.** The toy shows what a survivor-only
database does to a backtest. It runs one year on ten stocks and is not a test
of the strategy.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post quotes most of these figures. So does its
figure of the three portfolios' returns, which
`uv run python -m chan.survivorship_and_costs_figures` redraws.

## Entry 10: the Khandani-Lo reversal at the open, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Example 3.8, p. 78, and the
notebook `example3_8.ipynb` the book points to. Shipped under
[issue 206](https://github.com/l3a0/quantitative-trading/issues/206).

The label is a revised-edition one, and this entry declares it because the
repo reads an example number as first-edition unless it says otherwise. The
first-edition mirror holds `example3_7.m` and no file for this example, and
whether the 2009 edition carries it was not checked.

Thirteen rows, all derivable from
[tests/test_khandani_lo.py](../tests/test_khandani_lo.py).

**Chan's notebook reproduces, and the book's claim does not.** Example 3.8
takes Example 3.7's reversal and changes one thing, updating the positions at
the market open instead of the close. The book prints no figure and says only
that the Sharpe ratios before and after costs are "both very positive". Chan's
notebook prints 2.3818 before costs and 1.3997 after, and its transcription
lands on both. Run on the rule the book describes, the reversal earns 4.4202
before costs and 0.7834 after, so the after-cost figure misses the line of 1.0
that the claim was held to, declared before any figure on the opens was
computed.

Those two results come from two rules, and the difference between them is the
finding.

1. **Rule B is Example 3.7's MATLAB with the open in place of the close**, the
   rule Entry 8 reproduces. Chan's sentence at p. 78 recalls that strategy's
   0.25 and −3.19 and calls updating at the open "the only change", so rule B
   carries the claim.
2. **Rule A is the notebook as written.** It forward-fills before taking
   returns, carrying each stock's last price into a gap. It scales each day's
   weights to a gross exposure of 1, zeroes no stock for a missing price,
   divides its deviation by n, charges nothing on the first day, and charges
   no change in weight beside a missing one. Its Example 3.7 twin prints
   0.9578 and −2.1617 rather than the book's 0.25 and −3.19, and rows 4 and 5
   reproduce both on the closes.

The forward-fill is what separates them most. `spx_20071123/wyn.csv` holds two
companies under one symbol, 952 trading days apart, and the fill reads that gap
as a single day's move on 2006-08-01: a return of 121.5 on the closes and
127.65 on the opens, gains of over 12,000 percent. On the closes the fill
lifts rule A from 0.4179 to 0.9578 before costs, and dropping WYN alone gives
0.4268. On the opens it pulls rule A's figure before costs down, from 4.8606 to
2.3818, and dropping WYN alone gives 4.8508. After costs on the opens it
pushes the figure up, from 1.0335 to 1.3997.

Five rows are replications and eight are not. Row 1 is the claim, which takes
the claim route `### Rows that are not replications` describes, and rows 2 to
5 are the four figures Chan's notebooks print. Rows 6 to 13 have no published
figure.

Every row reads the same vintage, window and costs, so the three are stated
once here.

1. **The vintage.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, read through `chan.series.load_panel` with
   `field="Open"`, or the default close where a row says closes. Chan's
   notebooks read `SPX_op_20071123.txt` and `SPX_20071123.txt` instead, which
   this repo does not commit. Measured on
   [issue 206](https://github.com/l3a0/quantitative-trading/issues/206) at
   `7150afb`, each
   matches its panel cell for cell, NaN for NaN, to a largest relative
   difference of 2.0e-16, so the two are one series and nothing here can
   re-measure that. **Every figure here is about survivors**, for the reason
   Entry 8 gives.
2. **The window.** 2006-01-03 to 2006-12-29, 251 trading days, cut after the
   profit is computed.
3. **The costs and the ratio.** 5 basis points on each side of a change in
   weight, and √252 times the mean over the standard deviation with no
   risk-free rate. Rule B divides the deviation by n − 1 and rule A by n.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2006 sample on a rule somebody else chose, so the entry says whether his
numbers and his claim reproduce on his file and nothing about whether trading
at the open pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Both Sharpe ratios, before and after costs, at the open | "both very positive", a claim rather than a figure | p. 78. Not among the committed highlights, as [research/book-notes/README.md](../research/book-notes/README.md) records |
| 2 | The notebook's Sharpe ratio before costs | 2.381759409645483 | `example3_8.ipynb`, as reposted at pinhaocheng/epchan-quant_trading_Python_codes `5fcab61` |
| 3 | The notebook's Sharpe ratio after costs | 1.3996944546182997 | the same |
| 4 | The Example 3.7 notebook's Sharpe ratio before costs, on the closes | 0.957785681010386 | `example3_7.ipynb`, the same repost |
| 5 | The Example 3.7 notebook's Sharpe ratio after costs | −2.1617433718962276 | the same |
| 6 to 13 | rule B's figures, what the open recovered, rule A without its fill or without WYN, and the one-year bar | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | rows 6 and 7 read against the declared criterion, both at least 1.0 unrounded | before costs clears it and after costs does not | `TestTheVerdicts::test_the_claim_does_not_hold_because_after_costs_misses` |
| 2 | rule A on the opens, before costs | 2.3818 | `TestRuleAOnTheOpens::test_the_figures` |
| 3 | rule A on the opens, after costs | 1.3997 | `TestRuleAOnTheOpens::test_the_figures` |
| 4 | rule A on the closes, before costs | 0.9578 | `TestRuleAOnTheCloses::test_it_reproduces_the_notebooks_example_37` |
| 5 | rule A on the closes, after costs | −2.1617 | `TestRuleAOnTheCloses::test_it_reproduces_the_notebooks_example_37` |
| 6 | rule B on the opens, before costs | 4.4202 | `TestRuleBOnTheOpens::test_before_costs` |
| 7 | rule B on the opens, after costs, first day uncharged and its NaN counted as 0 | 0.7834 | `TestRuleBOnTheOpens::test_after_costs_with_both_quirks` |
| 8 | row 7 with the first day charged, so no day is NaN | 0.8293 | `TestRuleBOnTheOpens::test_after_costs_with_both_quirks_removed` |
| 9 | row 7 less Entry 8's row 2 | 3.9718 | `TestRuleBOnTheOpens::test_what_trading_at_the_open_recovered` |
| 10 | rule A on the opens without the forward-fill | 4.8606 before costs, 1.0335 after | `TestRuleAOnTheOpens::test_without_the_forward_fill` |
| 11 | rule A on the opens without WYN | 4.8508 before costs, 1.0357 after | `TestRuleAOnTheOpens::test_without_wyn` |
| 12 | rule A on the closes without the forward-fill, and without WYN | 0.4179 and −3.3760, and 0.4268 and −3.3643 | `TestRuleAOnTheCloses::test_without_the_forward_fill_it_does_not` and `::test_without_wyn_it_lands_near_the_unfilled_figure` |
| 13 | rows 2, 3, 6 and 7 against 1 × √(681/251), Chan's minimum-backtest estimate at p. 61 scaled to the window | the bar is 1.6472, and only the two before-cost figures clear it | `TestTheVerdicts::test_which_figures_clear_the_one_year_bar` and `::test_the_bar_is_chans_estimate_scaled_to_the_window` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | none, the source states a claim | did not reproduce | The criterion was declared on [issue 206](https://github.com/l3a0/quantitative-trading/issues/206) and the threshold confirmed by the owner before any figure on the opens was computed: both of rule B's figures at least 1.0, Chan's own line for a strategy worth trading on its own at p. 23. Before costs is 4.4202 and after costs 0.7834. The run reads Chan's own file through a transcription of the rule Entry 8 reproduces, so no cause outside the method is available, which is the reasoning behind Entry 1's row 6. |
| 2 | 0.0000 | reproduced | Chan's figure, on his own data, through his own notebook transcribed. |
| 3 | 0.0000 | reproduced | The same. |
| 4 | 0.0000 | reproduced | Rule A's control. Without it a transcription that leaned on pandas' current `pct_change`, which no longer fills gaps, would give row 12's 0.4179 and look plausible. |
| 5 | 0.0000 | reproduced | The same. |
| 6 | none | none, not a replication | Half of what row 1 reads. Updating at the open lifts the figure before costs from Entry 8's 0.2510 to 4.4202. |
| 7 | none | none, not a replication | The half that fails. Charging 5 basis points a side takes the figure from row 6's 4.4202 to 0.7834. |
| 8 | none | none, not a replication | Charging the first day moves the figure up rather than down here, and it stays below 1.0, so the quirks do not decide row 1. |
| 9 | none | none, not a replication | What the open recovered against Example 3.7 after costs. It turns a large loss into a small gain. |
| 10 | none | none, not a replication | The forward-fill is pandas 0.24's default, which the notebook's bare `pct_change()` inherits rather than asks for. Without it rule A's after-cost figure is 1.0335, above 1.0. |
| 11 | none | none, not a replication | Dropping only WYN gives 4.8508 against row 10's 4.8606, and 1.0357 against 1.0335, so on the opens WYN's gap carries most of what the fill does. |
| 12 | none | none, not a replication | The same pair on the closes. There WYN's gap lifts the figure rather than lowering it, and dropping WYN alone brings rule A from row 4's 0.9578 to 0.4268, near the 0.4179 it gives without the fill. |
| 13 | none | none, not a replication | The two before-cost figures clear the bar and the two after-cost figures do not. Chan states the estimate behind it as 95 percent confidence over 681 days, and scaling it to one year is this repo's step, so the row decides nothing. |

### What the entry concludes

Three things, and the first is the verdict.

1. **On the rule the book describes, the claim does not hold.** Updating at
   the open turns Example 3.7's −3.1884 after costs into 0.7834, a recovery of
   3.9718, and the before-cost figure reaches 4.4202. "Both very positive"
   asks both to clear 1.0, and the after-cost figure does not.
2. **Chan's notebook reproduces exactly and computes something else.** Its
   figures land at four decimals on both examples, and both of its Example
   3.8 figures clear 1.0. But it differs from the MATLAB in six ways, and on
   Example 3.7 it prints 0.9578 where the book prints 0.25, so it is not the
   strategy behind 0.25 and −3.19 with one change, which is what the book's
   sentence describes.
3. **WYN's gap moves rule A on both fields, in opposite directions.** Reading
   it as a gap rather than a move, by dropping the fill or dropping WYN, gives
   0.4179 to 0.4268 before costs on the closes and 4.8508 to 4.8606 on the
   opens. Rule A's after-cost figure on the opens stays above 1.0 either way,
   at 1.0335 and 1.0357.

### What this entry cannot say

Four things.

**What `example3_8.R` prints.** The book points to it beside the notebook, and
no copy was found.

**Whether trading at the open is tradeable on the open's own signal.** Both
rules set a weight from the day's open and trade at that same open, as Example
3.7 does at the close. Neither run adjusts that timing.

**What survivorship cost.** Neither its size nor its sign is measured, as
Entry 8 says.

**Whether the rule pays on small caps.** Chan leaves that as an exercise, and
[issue 249](https://github.com/l3a0/quantitative-trading/issues/249) runs it on
the S&P 600 file.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit, and
[blog/survivorship-and-transaction-costs.md](../blog/survivorship-and-transaction-costs.md)
moves with it, since that post's Lessons 6 and 7 quote these figures.

## Entry 11: the commodity seasonals, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, the main text at Kindle
locations 4529, 4585 and 4632 and the two sidebars at 4536 and 4590. Shipped
under [issue 19](https://github.com/l3a0/quantitative-trading/issues/19).

Ten rows, all derivable from
[tests/test_commodity_seasonals.py](../tests/test_commodity_seasonals.py).

**Both natural gas figures reproduce under the reading the issue pinned, and
the gasoline count agrees with the book on every year the file can read.** Chan says commodity seasonal trades still pay where
the equity ones have died, and gives two. Gasoline buys the May contract at the
close of April 13 and sells at the close of April 25. Natural gas buys the June
contract at the close of February 25 and sells at the close of April 15.

1. **Natural gas.** Every year from 1994 to 2008 is profitable. Counted from
   1995, the run is 13 years ending in 2007 and 14 ending in 2008, the main
   text's figure and the sidebar's.
2. **Gasoline.** 1995 to 2015 holds exactly 2 losing years, 2009 and 2012,
   which is 21 less 19. It shows 16 profitable years rather than 19, because
   EIA's file holds no row on the trade date in 1997, 1998 or 1999.

Every rule was written on
[issue 19](https://github.com/l3a0/quantitative-trading/issues/19) on
2026-10-03, before any trade was computed. Three of them carry the result, so
they are stated here.

1. **The vintages.** EIA's NYMEX settlements, downloaded 2026-10-02:
   `eia_eer-epmr-pe1-y35ny-dpg_raw_1985-01-02_2006-12-29_dl2026-10-02.csv`, New
   York Harbor regular gasoline, through 2005,
   `eia_eer-epmrr-pe1-y35ny-dpg_raw_2005-10-03_2024-04-05_dl2026-10-02.csv`,
   RBOB gasoline, from 2006, and `eia_rngc2`, `eia_rngc3` and `eia_rngc4` for
   natural gas. [data/README.md](../data/README.md) says what each holds. Each
   file numbers contracts by expiry, so the run maps a date to the file that
   holds the May or June contract. The expiry rule behind that map gives the
   last trading day the Massive futures API recorded for all 16 contracts
   checked, March to June of 2017, 2018, 2021 and 2024. Those 16 dates were read
   from the API on 2026-10-03 and are pinned as a measurement, because nothing
   in this repo can read them again. Before mid-1997 contracts stopped trading
   five or six days before delivery rather than three, which the files'
   handovers show, and the rule follows them. That moves the 1996 and 1997
   entries to contract 3 and changes neither year's sign.
2. **Profitable** means the exit settlement strictly above the entry, on one
   contract, with no costs.
3. **A missing row stays missing.** A year whose trade date has no row in its
   file counts neither way, rather than moving to another day.

Every result here is **exploratory**. Chan chose both trades after looking at
the history the run reads, so the entry says whether his counts reproduce and
nothing about whether either trade pays today.

### What the book printed

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Gasoline, profitable years in 1995 to 2015 | 19 of 21 | location 4529 |
| 2 | Gasoline, the years out of sample | the last 9 of the 21, with no count | location 4529 |
| 3 | Gasoline, the sidebar's claim | a profit every year since 1995 | location 4536 |
| 4 | Natural gas, the main text's run | 13 consecutive years | location 4585 |
| 5 | Natural gas, the sidebar's run | 14 consecutive years | location 4590 |
| 6 | Natural gas out of sample | "didn't hold up as well", a claim with no figure | location 4632 |
| 7 to 10 | the runs counted from 1994, 2006 on the older gasoline contract, the expiry-day file, and both trades after the book | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | gasoline, 1995 to 2015 | 16 profitable, 2 losses in 2009 and 2012, 3 unreadable in 1997, 1998 and 1999 | `TestTheVerdicts::test_19_of_21_reproduces_with_a_gap_the_missing_years_explain` |
| 2 | gasoline, 2007 to 2015 | 7 of 9 | `TestTheVerdicts::test_the_nine_out_of_sample_years` |
| 3 | gasoline, 1995 to 2008, read as the years before the 2008 first edition | no loss, 11 profitable, 3 unreadable | `TestTheVerdicts::test_every_year_since_1995_has_no_loss_and_three_unreadable_years` |
| 4 | natural gas, the run counted from 1995 ending in 2007 | 13 | `TestTheVerdicts::test_13_and_14_consecutive_years_reproduce` |
| 5 | natural gas, the run counted from 1995 ending in 2008 | 14 | `TestTheVerdicts::test_13_and_14_consecutive_years_reproduce` |
| 6 | natural gas, 1994 to 2008 against 2009 to 2023 | 15 of 15 against 7 of 15 | `TestTheVerdicts::test_natural_gas_before_and_after_the_first_edition` |
| 7 | natural gas, the same two runs counted from 1994 | 14 and 15 | `TestNaturalGas::test_the_runs_counted_from_the_files_first_year` |
| 8 | gasoline 2006 on the older contract instead of RBOB | unreadable, no row on 2006-04-13 | `TestGasoline::test_the_2006_side_row_on_the_harbor_contract_is_missing` |
| 9 | the 10 natural gas entries on the March contract's last day, read from contract 3 instead of 4 | no year changes sign | `TestTheNaturalGasExpiries::test_ten_entries_fall_on_march_s_last_day_and_none_flips_on_the_other_file` |
| 10 | both trades, 2016 to 2023 | gasoline 3 of 8, natural gas 4 of 8 | `TestTheVerdicts::test_both_trades_after_the_book` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | −3 profitable years, all 3 unreadable | reproduced with a gap | The criterion the issue pinned, exactly 19, fails at 16. The verdict was taken afterwards under this file's rule, and the issue records that. The file bounds the count between 16 and 19 rather than settling it. The cause is named and outside the method: EIA's harbor gasoline file holds no row on 1997-04-14, 1998-04-24 or 1999-04-23, each a trading day, and the run neither fills a row nor moves a date. Every readable year agrees with the book, because the 2 losses are the 2 that 21 less 19 allows. |
| 2 | none | none, not a replication | The book says which years were out of sample and prints no count for them. 7 of the 9 were profitable, and the two losses of row 1 both fall among them. |
| 3 | none, the source states a claim | reproduced with a gap | The criterion the issue pinned, a profit in every year, cannot be met with 3 years unreadable, and the verdict was taken afterwards on the same footing as row 1. The claim holds on every readable year, with no loss from 1995 to 2008. Read as 1995 to 2007 instead, it gives no loss and 10 profitable. |
| 4 | 0 | reproduced | Under the reading pinned on the issue, both figures written for the 2008 first edition and counted from 1995. |
| 5 | 0 | reproduced | The same reading. The two figures differ by the one year between the main text and the sidebar. |
| 6 | none | none, not a replication | A claim with no figure, and the issue declared no criterion for it. The halves are 15 of 15 and 7 of 15. |
| 7 | none | none, not a replication | 1994 is profitable too, so counting from the files' first year makes both runs one longer. With runs ending in 2007 and 2008, only a count from 1995 matches, the year the gasoline sidebar names as its start. Counted from 1994, runs of 13 and 14 end in 2006 and 2007 instead. |
| 8 | none | none, not a replication | The older contract's file has no row on 2006's entry day, so the side row cannot say whether the switch to RBOB decides 2006. |
| 9 | none | none, not a replication | In 10 years the entry falls on the March contract's last trading day, so the file read depends on contract 1 keeping an expiring contract on its last day. The files show that convention in 2014 and 2019. Reading contract 3 instead flips no year, so the convention cannot move a verdict. |
| 10 | none | none, not a replication | After the book, gasoline profits in 3 of 8 years and natural gas in 4 of 8, its 2016 to 2023 share of row 6. |

### What the entry concludes

Three things.

1. **Natural gas reproduces under the pinned reading.** Every year from 1995
   to 2008 is profitable, which gives the main text's 13 and the sidebar's 14
   once both are read as first-edition figures counted from 1995. 2009 is a
   loss, so neither figure can be a run ending in the revised edition's years.
2. **Gasoline agrees with the book on every year the file can read.** 1995 to
   2015 holds the 2 losing years 19 of 21 allows and no third. The three
   unreadable years are gaps in EIA's file, not losses.
3. **In this exploratory record, both trades win fewer years after the years
   Chan read.** Natural gas wins 15 of 15 through 2008 and 7 of 15 after, which
   agrees with his remark at location 4632. Gasoline wins 3 of 8 from 2016 to
   2023. Eight years with no costs charged can show the change and cannot
   measure it.

### What this entry cannot say

Four things.

**What the three unreadable years held.** EIA's harbor file has no row on any
of them, and no other committed source covers the contract then. A source
holding each named contract's settlements would settle them.

**Whether Chan read the same contracts.** The sidebar names RB and glosses it
as the unleaded gasoline futures. Before RBOB began trading in October 2005,
his series presumably held the older contract, and the run assumes so. His
data vendor is not named.

**Which year each natural gas figure was written in.** Neither passage says,
and the reading pinned on the issue is a hypothesis that both are
first-edition figures counted from 1995. The files rule out a run ending in
the revised edition's years, because 2009 is a loss. They cannot pick the
start year, because 1994 is profitable too.

**Whether either trade pays after costs.** No commission, slippage or margin is
charged, as the rule on the issue states.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 12: post-earnings drift, Chan's *Algorithmic Trading*

Source: Ernest P. Chan, *Algorithmic Trading: Winning Strategies and Their
Rationale*, Wiley, 2013, Example 7.2, Kindle location 3024, and the script
`pead.m` the example names. Shipped under
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20). It is the
first entry from Chan's second book, and its location numbers are that book's,
in [research/book-notes/algorithmic-trading.md](../research/book-notes/algorithmic-trading.md).

Eleven rows, all derivable from [tests/test_pead.py](../tests/test_pead.py).

**Every figure Chan prints reproduces on his own files.** Prices drift in the
direction of an earnings surprise after the announcement, and Chan trades the
first day of that drift without knowing what was announced. On a day a stock
announced after the previous close and before the open, the gap from that
close to the open stands in for the surprise. A gap of at least half its
90-day moving standard deviation buys the stock at the open, or shorts it if
the gap was down, and the position is closed at the same day's close. Each
day's summed return is divided by 30. The book reports an APR of 6.7 percent
and a Sharpe ratio of 1.5. `pead.m` prints five figures, and the
transcription in `chan.pead` lands on all of them at the precision the script
prints.

One choice decides a printed digit. Chan's two books ship two helpers called
`smartstd`. The first edition's, which Entries 8 and 10 and Entry 7's
first-edition rows run, counts a missing value as zero and divides by n − 1.
Book two's, which Entry 7's revised MATLAB rows run too, skips it and divides
by n. With book two's, the arithmetic return is 0.066743, which prints as
Chan's 0.0667. With the first edition's it is 0.066833, which prints as
0.0668, and row 11 holds that.

Every row reads the same vintages and specification, so both are stated once
here.

1. **The vintages.** `inputdataohlcdaily_stocks_20120424/`, the 497 stocks of
   Chan's `inputDataOHLCDaily_stocks_20120424.mat`, saved 2012-04-25, read for
   the open and the close, and `earnannfile/`, the 497 flag series of his
   `earnannFile.mat`, saved 2012-05-15. Both are read through
   `chan.series.load_panel`, and [data/README.md](../data/README.md) records
   where each came from and what it holds. **Every figure here is about
   survivors**, because the price file is the S&P 500 as Chan held it on
   2012-04-24, carried backwards.
2. **The specification.** `pead.m` at `45670240` in
   [ivanliu1989/algorithmic_trading](https://github.com/ivanliu1989/algorithmic_trading).
   The prices are cut to the flag file's 330 days, 2011-01-03 to 2012-04-24,
   before the gap is taken. The lookback is 90 days, the entry is 0.5 moving
   standard deviations, and the denominator is 30. Every annualisation uses
   252 days, and the Sharpe ratio subtracts no risk-free rate. No cost is
   charged.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2011 and 2012 sample on a rule he chose, so the entry says whether his numbers
reproduce on his files and nothing about whether the drift pays today.

### What the book printed

`pead.m` prints its figures in the comment lines that close it, and the book
quotes two of them rounded.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | Arithmetic annual return, 252 times the mean daily return | 0.0667 | `pead.m` |
| 2 | The same figure, as the book quotes it | "APR" of 6.7 percent | location 3024 |
| 3 | Sharpe ratio | 1.49 | `pead.m` |
| 4 | The same figure, as the book quotes it | 1.5 | location 3024 |
| 5 | Compounded APR | 0.0680 | `pead.m` |
| 6 | Maximum drawdown | −0.026052 | `pead.m` |
| 7 | Maximum drawdown duration | 109 days | `pead.m` |
| 8 | Most positions held on one day, which is the denominator | 30 | location 3024 |
| 9 | Annual return levered four times | "close to 27 percent" | location 3024 |
| 10 and 11 | the positions taken in all, and row 1 under the first edition's `smartstd` | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `252 · smartmean(ret)` | 0.066743 | `TestTheFigures::test_the_arithmetic_annual_return_is_the_books_apr` |
| 2 | row 1, in percent at the book's one decimal, against the compounded figure's 6.8 | 6.7 | the same, and `TestTheFigures::test_the_books_apr_is_not_the_compounded_one` |
| 3 | `√252 · smartmean(ret) / smartstd(ret)`, book two's `smartstd` | 1.4909 | `TestTheFigures::test_the_sharpe_ratio` |
| 4 | row 3 at the book's one decimal | 1.5 | the same |
| 5 | `prod(1 + ret)^(252/330) − 1` | 0.067952 | `TestTheFigures::test_the_compounded_apr` |
| 6 | `calculateMaxDD` on `cumprod(1 + ret) − 1` | −0.026052 | `TestTheFigures::test_the_maximum_drawdown_and_its_duration` |
| 7 | the same | 109 days | the same |
| 8 | the most nonzero positions on one of the 330 days | 30 | `TestTheFigures::test_the_busiest_day_holds_chans_denominator` |
| 9 | four times row 1 | 0.266970 | `TestTheFigures::test_levered_four_times_it_is_close_to_27_percent` |
| 10 | the nonzero positions across the window, none in its first 89 days | 1,072 | `TestTheFigures::test_the_busiest_day_holds_chans_denominator` and `::test_no_stock_trades_before_its_window_fills` |
| 11 | row 1 with the first edition's `smartstd` in the moving deviation and the Sharpe ratio | 0.066833, and 1,071 positions | `TestTheHelperMovesADigit::test_the_first_editions_helper_misses_chans_printed_digit` and `::test_the_other_printed_figures_survive_the_swap` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | Chan's figure, on his own files, through his own script transcribed. |
| 2 | 0.0 | reproduced | The book's "APR" is the arithmetic figure. The compounded one is 6.8 percent at the book's precision, so the label names the wrong one of the two. |
| 3 | 0.00 | reproduced | The same as row 1. |
| 4 | 0.0 | reproduced | The same. |
| 5 | 0.0000 | reproduced | The same. |
| 6 | 0.000000 | reproduced | The same. The port keeps `calculateMaxDD`'s two quirks, a high-water mark that starts at zero and a loop that starts on the second row. Neither moves this run, because its first day returns nothing, so `tests/test_matlab_helpers.py` holds both on inputs where they do. |
| 7 | 0 | reproduced | The same. |
| 8 | 0 | reproduced | The 30 is a fact about the run that Chan then used as an input, and the run gives it back. He names the look-ahead bias that makes it at location 3024. |
| 9 | 0 | reproduced | 26.6970 percent rounds to 27, the precision Chan quotes. Leverage multiplies every day's return by four, so it multiplies the arithmetic figure by four. |
| 10 | none | none, not a replication | The first 89 days hold no position, because the moving deviation has not filled. |
| 11 | none | none, not a replication | The first edition's helper also takes one position fewer, 1,071. The Sharpe ratio, the compounded APR and the drawdown still print as Chan's, so the arithmetic return is the only printed figure it moves. |

### What the entry concludes

Two things.

1. **Example 7.2 reproduces exactly on Chan's own files.** Every figure
   `pead.m` prints, both figures the book quotes, its 30 and its levered 27
   percent land at the precision each was printed.
2. **Which book's helper runs is part of the specification.** The two
   `smartstd` files share a name and differ in what they do with a missing
   value and in their denominator. Here the difference is one unit in one
   printed digit, so a port that reached for the helper the repo already held
   would have looked like a near miss on a vintage problem rather than a
   wrong helper.

### What this entry cannot say

Four things.

**What the drift earned on the index as it stood each day.** Every stock here
was in the S&P 500 on 2012-04-24.
[Issue 252](https://github.com/l3a0/quantitative-trading/issues/252) reruns the
rule on a point-in-time universe, which waits on a purchase.

**Whether Chan's flags are the announcement calendar.** They catch three of
Apple's five releases inside the window, a measurement recorded on
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20).
[Issue 251](https://github.com/l3a0/quantitative-trading/issues/251) reruns the
rule on EDGAR's filings and modern prices.

**What costs would take.** `pead.m` charges none, and every position is a
round trip inside one day.

**How large the look-ahead in the 30 is.** Chan argues it is small because the
number of announcements a day is predictable, and nothing here tests that.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 13: the PCA factor model, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading*, Example 7.4, "Principal
Component Analysis as an Example of the Factor Model". The revised edition
prints it on pp. 163 to 167, read in the Kindle Cloud Reader on 2026-10-03,
with its setup at Kindle location 4034 and its result at 4051. The first
edition's script is `example7_4.m`. Shipped under
[issue 21](https://github.com/l3a0/quantitative-trading/issues/21).

Sixteen rows, all derivable from
[tests/test_pca_factor.py](../tests/test_pca_factor.py). Eight do not pair one
published figure with one computation. Row 7 sets two readings against three
printed figures, row 9 sets three programs against one, and rows 11 to 16
carry no published figure.

**Three of the four printouts reproduce, and Chan's account of why they
disagree does not hold.** The strategy takes five statistical factors from a
year of returns, assumes the factor returns carry momentum, buys the 50 stocks
with the highest expected return and shorts the 50 with the lowest. Chan
reports 2 percent a year in MATLAB and 4 percent in Python and R, and calls the
difference "essentially round off errors". The first edition's MATLAB, the
revised MATLAB and the revised Python each land on every figure they print,
on the file they all load. The revised R prints the Python's three figures to
17 digits, and its own code reads differently.

The spread between 2 and 4 percent is method. The revised Python never uses
its factors. It regresses each stock's returns on an intercept and five factor
series and ranks on the summed fitted values, and with an intercept in the
regression that sum is the stock's summed return. So the Python ranks on a
year of momentum, and its book is the same on every day as a ranking that
leaves the PCA out. The revised MATLAB fits today's cross-section of returns
on the stocks' factor exposures instead. Given the MATLAB's 50 longs, the
Python's book matches the MATLAB's on none of the 752 days both trade.

Every row reads the same vintage and specification, so both are stated once
here.

1. **The vintage.** `ijr_20080114/`, the 600 stocks of Chan's
   `IJR_20080114.mat`, saved 2008-01-15, spanning 2004-01-15 to 2008-01-14,
   read for the close through `chan.series.load_panel`. Every printout loads
   this file. The revised repost's `.mat` has the sha256 the lifted file has,
   and the Python's text file holds the same closes to 2.0e-16, which
   [data/README.md](../data/README.md) records. **Every figure here is about
   survivors**, because the file holds the S&P 600 as it stood on 2008-01-14,
   carried backwards.
2. **The specification.** A lookback of 252, five factors, 50 stocks shorted
   and no cost, under each printout's own rule as `chan.pca_factor`
   transcribes it. The first edition's `example7_4.m` is read at `1a71950` in
   the mirror [data/README.md](../data/README.md) names. The revised MATLAB and
   Python are read from the book's pages and from their reposts at
   pinhaocheng/epchan-quant_trading_MATLAB_codes `7430b84` and
   pinhaocheng/epchan-quant_trading_Python_codes `5fcab61`. The R is read from
   the pages alone. Every annualisation uses 252 days, and no Sharpe ratio
   subtracts a risk-free rate.

Every result here is **exploratory**. Reproducing Chan's figures spends the
2004 to 2008 sample on a rule he chose, so the entry says whether his numbers
reproduce on his file and nothing about whether a statistical factor model
earns money.

### What the book printed

The revised edition prints each program's figures in the comment lines that
close its listing, and the text quotes two of them as whole percents. Only the
text is among the committed highlights. The code-printed figures are not, and
[research/book-notes/README.md](../research/book-notes/README.md) records that
absence.

| # | Row | Published figure | Where |
| --- | --- | --- | --- |
| 1 | First-edition MATLAB, `smartmean(ret)*252`, a sum over positions | −1.8099 | `example7_4.m`, first edition |
| 2 | Revised MATLAB, annual mean return | 0.020205 | revised edition p. 164 |
| 3 | Revised MATLAB, Sharpe ratio | 0.211120 | revised edition p. 164 |
| 4 | Revised Python, annual mean return | 0.04052422056844459 | revised edition p. 165 |
| 5 | Revised Python, annualised standard deviation | 0.07002908500498846 | revised edition p. 165 |
| 6 | Revised Python, Sharpe ratio | 0.5786769963588398 | revised edition p. 165 |
| 7 | Revised R, the same three lines | rows 4 to 6, digit for digit | revised edition p. 167 |
| 8 | The MATLAB return, as the text quotes it | 2% | location 4051 |
| 9 | The Python and R return, as the text quotes it | 4% | location 4051 |
| 10 | Why the programs differ | "essentially round off errors" | location 4051 |
| 11 to 16 | what separates the printouts, and each without PMC | none, the book prints no such figures | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | `first_edition_matlab`, the mean over 1,005 rows | −1.809865 | `TestThePrintouts::test_the_first_edition_prints_minus_1_8099` |
| 2 | `revised_matlab`, the mean over the 752 days that trade | 0.020205 | `TestThePrintouts::test_the_revised_matlab_prints_its_two_figures` |
| 3 | the same, with book two's `smartstd` | 0.211120 | the same |
| 4 | `revised_python`, the mean over all 1,006 rows | 0.040524220568445 | `TestThePrintouts::test_the_revised_python_lands_its_printed_figures` |
| 5 | the same, `np.nanstd` dividing by n | 0.070029085004988 | the same |
| 6 | the same | 0.578676996358840 | the same |
| 7 | `revised_r_reading`, unfilled and forward-filled | 0.0401, 0.0797, 0.5038 and 0.0426, 0.0802, 0.5319 | `TestThePrintouts::test_neither_r_reading_lands_the_printed_figures` |
| 8 | row 2 at the text's whole percent | 2% | `TestThePrintouts::test_the_revised_matlab_prints_its_two_figures` |
| 9 | row 4 at the text's whole percent, and row 7's two readings | 4%, 4% and 4% | `TestThePrintouts::test_the_revised_python_lands_its_printed_figures` and `::test_neither_r_reading_lands_the_printed_figures` |
| 10 | the shared days on which the revised MATLAB and the Python given 50 longs hold the same book, and the fewest positions in which they differ on one day | 0 of 752, and 125 | `TestWhatSeparatesTwoFromFour::test_at_one_size_the_revised_books_are_never_identical` and `::test_round_off_does_not_explain_the_spread` |
| 11 | the Python ranked on each stock's summed return, with the PCA left out | the same book on every day | `TestWhatSeparatesTwoFromFour::test_the_pythons_pca_changes_no_position` |
| 12 | the mean share of the revised MATLAB's names the Python holds the same way, as printed and with 50 longs | 13.83% and 14.14% | `TestWhatSeparatesTwoFromFour::test_the_revised_books_share_few_names` and `::test_at_one_size_the_revised_books_are_never_identical` |
| 13 | the Python buying the top 50 rather than the 49 ranked second to 50th | 0.0414, Sharpe ratio 0.5908 | `TestWhatSeparatesTwoFromFour::test_fifty_longs_move_the_pythons_figures` |
| 14 | the Python over its 751 trading days, the first edition over its 753, and the Python keeping the first book it clears | 0.0543, Sharpe ratio 0.6699, then −2.4156, then 0.0417, Sharpe ratio 0.5945 | `TestWhatSeparatesTwoFromFour::test_averaging_over_trading_days_moves_both_programs` and `::test_keeping_the_first_book_moves_the_pythons_figures` |
| 15 | row 3 under the first edition's `smartstd` | 0.2441 | `TestWhatSeparatesTwoFromFour::test_the_first_editions_smartstd_moves_the_revised_sharpe` |
| 16 | rows 1 to 6 without PMC | −1.8014, then 0.0180 and 0.1869, then 0.0408 and 0.5851 | `TestTheSplice::test_each_printout_without_pmc` |

### The verdicts

| # | Gap, computed minus published | Verdict | Why |
| --- | --- | --- | --- |
| 1 | 0.0000 | reproduced | Chan's first-edition figure, on his file, through his script transcribed. It is a sum over 100 positions of ±1 with no division by capital, and its mean runs over 252 rows from before the first trade. |
| 2 | 0.000000 | reproduced | The same, for the revised MATLAB. |
| 3 | 0.000000 | reproduced | The same. The printed figure lands with book two's `smartstd` and misses with the first edition's, row 15, and the revised repost at `7430b84` carries book two's file. |
| 4 | under 1e-15 | reproduced | Within 1e-12 of each figure printed to 17 digits, the verdict's criterion, and within 1e-15, the pin. They agree to 15 significant digits. |
| 5 | under 1e-15 | reproduced | The same. |
| 6 | under 1e-15 | reproduced | The same. |
| 7 | none | did not reproduce | Neither reading of the printed R lands its printed figures, which are the Python's to the last digit. The R's window ends today rather than yesterday, it buys 52, its mean skips the days with no position, and its `sd` divides by n − 1. It sources a `calculateReturns.R` the book does not print, and no R runtime is installed here, so the row is a reading of the code rather than a run of it. [Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it once Chan's download is in hand. |
| 8 | 0 | reproduced | 2.02 percent rounds to 2. |
| 9 | 0 | reproduced | The Python's 4.05 percent rounds to 4, and so does each R reading. The whole-percent figure is reached even by the code whose 17-digit figures are not. |
| 10 | none | did not reproduce | Round-off would leave two books of one size the same on every day. The printed Python buys 49 and the MATLAB 50, so the comparison gives the Python 50, and the books then match on none of 752 days and differ in at least 125 positions on each. The criterion was written on [issue 21](https://github.com/l3a0/quantitative-trading/issues/21) after the overlap was measured, which is the cost named there. |
| 11 | none | none, not a replication | This is why the Python's figure is momentum's. Its PCA changes no position. |
| 12 | none | none, not a replication | The two revised programs trade mostly different stocks. |
| 13 | none | none, not a replication | The Python's `np.arange(-topN, -1)` never buys the top-ranked stock. |
| 14 | none | none, not a replication | The Python's mean and spread run over all 1,006 rows, including 255 that hold no position, and its `positionsTable[capital==0,]=0` zeroes its first book. The first edition's mean runs over 252 rows with no position. |
| 15 | none | none, not a replication | The first edition's `smartstd` zero-fills a missing day and divides by n − 1. |
| 16 | none | none, not a replication | PMC closes at 6.02 on 2004-03-12 and resumes at 17.25 on 2007-08-01, two price histories under one symbol. Every program but the unfilled R reading forward-fills, so the gap becomes one day's return of 1.8654. |

### What the entry concludes

Two things.

1. **The three printouts that can run reproduce on Chan's file.** The first
   edition's −1.8099 and the revised MATLAB's 0.020205 and 0.211120 land at
   the precision printed, and the revised Python's three 17-digit figures land
   within 1e-15.
2. **The 2-versus-4 spread is two different strategies, not round-off.** The
   revised MATLAB trades a factor model and the Python trades a year of
   momentum, because its regression's intercept cancels its factors. Three
   bookkeeping choices each lower the Python's figure toward the MATLAB's: its
   long side, its averaging, and the first book it clears. Without any one of
   them the Python's figure is higher than 4.05 percent, rows 13 and 14.

### What this entry cannot say

Three things.

**What the strategy earned on the index as it stood each day.** Every stock
here was in the S&P 600 on 2008-01-14.
[Issue 269](https://github.com/l3a0/quantitative-trading/issues/269) reruns it
on a point-in-time universe, which waits on data.

**What the R printout actually computed.** Without `calculateReturns.R` and an
R runtime, row 7 is a reading.
[Issue 271](https://github.com/l3a0/quantitative-trading/issues/271) runs it
once Chan's download is in hand.

**What costs would take.** Every printout charges none, and the books turn over
daily.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.

## Entry 14: the market and momentum factors, Chan's *Quantitative Trading*

Source: Ernest P. Chan, *Quantitative Trading: How to Build Your Own
Algorithmic Trading Business*, revised edition, Kindle locations 3978, 4004
and 4014. Shipped under
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22). Every
location is the revised edition's. Whether the first edition carries the
sentences at 4004 and 4014 was not checked.

Nine rows, all derivable from
[tests/test_momentum_factor.py](../tests/test_momentum_factor.py).

**The claim holds for the market factor and does not hold for the momentum
factor.** Chan says at location 4014 that "often factor returns are more
stable than individual stock returns", that they "exhibit stronger serial
autocorrelations than individual stock's returns", and so "have momentum".
That persistence is what lets this period's factor return stand in for the
next. Two of the factors his section names need only prices. MKT, which
location 3978 names as "the return of the market", is built here as the
index's return over the bill rate, the way French's market factor is. WML, winners
minus losers, defined at location 4004, longs the stocks whose past return was
positive and shorts those whose past return was negative. Over 83 months,
MKT's lag-1 autocorrelation is 0.0675 and WML's is −0.1099, against a median
of −0.0392 across the 446 stocks priced in every month. MKT is above 0 and
above the median stock. WML is below both.

Two rows are claims and seven are not replications. Rows 1 and 2 take the
claim route `### Rows that are not replications` describes, one per factor.
Rows 3 to 9 are the figures the issue reports beside the verdicts, which
decide nothing.

Every rule was fixed on
[issue 22](https://github.com/l3a0/quantitative-trading/issues/22) on
2026-10-03, before any autocorrelation was computed. The owner ruled the same
day, also before, that each factor carries its own verdict with Chan's "often"
quoted beside it and that no combined verdict is formed. Four of the rules
carry the result, so they are stated here.

1. **The vintages.** `spx_20071123/`, the 500 stocks of Chan's
   `SPX_20071123.mat`, saved 2007-11-24, read through `chan.series.load_panel`.
   `spy_chan.csv`, the adjusted-close column of his `example6_2.xls`, saved
   2008-01-29. FRED's TB3MS, downloaded 2026-09-30.
   [data/README.md](../data/README.md) says what each holds.
2. **The construction.** The month-ends are the panel's rows whose next row
   falls in another month, Chan's own rule, which gives 96 from 1999-11-30 to
   2007-10-31. At month-end t a stock's past return runs from its close at
   t − 12 to its close at t − 1, skipping the latest month as French's
   momentum factor does. A positive past return makes a winner and a negative
   one a loser. A stock enters only with a finite close at all 14 month-ends
   from t − 12 to t + 1, which leaves 442 to 494 at each formation. Each leg is
   equally weighted, held one month, and charged no costs. MKT is SPY's
   month-end to month-end return less that month's TB3MS over 12. The
   holding months run from December 2000 to October 2007, 83 of them.
3. **The statistic.** `pandas.Series.autocorr(lag=1)` on each series of 83
   monthly returns, which is the correlation of the 82 pairs of one month's
   return with the month before. The comparison set is every stock with a
   finite return in all 83 months, 446 of them, and their median stands for
   "individual stock's returns".
4. **The criterion.** The claim holds for a factor when its autocorrelation is
   above 0 and above the median stock's, both compared unrounded. Monthly is
   the only frequency computed, because the factors are re-formed monthly.

**Every figure touching the stocks is about survivors.** The panel is the
S&P 500 as it stood on 2007-11-23, carried backwards. That reaches WML's two
legs in opposite directions, and which dominates is not measured here.

1. **The loser leg** lacks the stocks that fell and then left the index, so
   it holds losers that recovered enough to stay. That pushes WML down.
2. **The winner leg** lacks past winners that later collapsed out of the
   index. That pushes WML up.

MKT reads SPY, which held the index as it stood each day, so it carries no
survivorship.

Every result here is **exploratory**. Testing a claim someone else chose
spends the 2000 to 2007 sample on it, so the entry says whether the claim
holds on this file and nothing about factor momentum today.

### What the book stated

The book prints no number for this claim, so the published-figure and gap
columns have nothing to hold in any row and are dropped, under
`### What a second entry does to this file`.

| # | Row | What the book says | Where |
| --- | --- | --- | --- |
| 1 | MKT has stronger serial autocorrelation than single stocks, so it has momentum | the claim, "often", with no figure | location 4014, MKT defined at location 3978 |
| 2 | WML has stronger serial autocorrelation than single stocks, so it has momentum | the same claim | location 4014, WML defined at location 4004 |
| 3 to 9 | each factor's autocorrelation and percentile, the stocks' quartiles, the band, each factor's mean and t-statistic, and the legs | nothing, the book works no example | n/a |

### What this repo computed

| # | Specification | Computed | Assertion |
| --- | --- | --- | --- |
| 1 | MKT's autocorrelation against 0 and against the median stock's, unrounded | 0.0675, above 0 and above −0.0392 | `TestTheVerdicts::test_mkt_holds_above_zero_and_above_the_median_stock` |
| 2 | WML's autocorrelation against the same two | −0.1099, below 0 and below −0.0392 | `TestTheVerdicts::test_wml_does_not_hold_on_either_half` |
| 3 | MKT's lag-1 autocorrelation, and the percent of the 446 stocks strictly below it | 0.0675, 80.7175, which is 360 stocks | `TestTheFigures::test_mkts_autocorrelation` and `::test_each_factors_percentile_among_the_stocks` |
| 4 | WML's lag-1 autocorrelation, and the same percent | −0.1099, 27.8027, which is 124 stocks | `TestTheFigures::test_wmls_autocorrelation` and `::test_each_factors_percentile_among_the_stocks` |
| 5 | the 446 stocks' lag-1 autocorrelations, lower quartile, median and upper quartile, by linear interpolation | −0.1198, −0.0392 and 0.0402 | `TestTheFigures::test_the_stocks_quartiles` |
| 6 | ±1.96/√83, and which factors fall outside it | 0.2151, neither | `TestTheBand::test_the_band_is_1_96_over_root_83` and `::test_neither_factor_falls_outside_it` |
| 7 | MKT's mean monthly return times 12, and its plain t-statistic | 0.0185 and 0.3660 | `TestTheFigures::test_each_factors_annual_mean_and_t_statistic` |
| 8 | WML's mean monthly return times 12, and its plain t-statistic | 0.0241 and 0.4505 | `TestTheFigures::test_each_factors_annual_mean_and_t_statistic` |
| 9 | the eligible stocks, the excluded stocks, the winner leg and the loser leg, fewest and most over the 83 formations | 442 to 494 eligible, so 6 to 58 excluded for a missing close. Winners 79 to 468, losers 11 to 397 | `TestTheLegs::test_442_to_494_stocks_are_eligible`, `::test_6_to_58_stocks_are_excluded` and `::test_the_winner_and_loser_legs_sizes` |

### The verdicts

| # | Verdict | Why |
| --- | --- | --- |
| 1 | reproduced | The claim holds for MKT, which Chan says factors "often" show. Its autocorrelation is above 0 and above the median stock's, under the criterion declared on the issue before any autocorrelation was computed. It sits at 0.0675, inside row 6's band, so a series with no autocorrelation would land there often, and this verdict could be noise. |
| 2 | did not reproduce | The claim, which Chan says factors "often" show, does not hold for WML, on either half: its autocorrelation is below 0 and below the median stock's. Under the owner's ruling this verdict stands on its own, and no combined verdict is drawn from rows 1 and 2. The value is forced, because the log's two other verdicts both need the claim to survive. Two causes outside the method are open and neither is measured: the panel holds only survivors, and 2000 to 2007 is one window. Nothing here argues which way either moves an autocorrelation. |
| 3 | none, not a replication | MKT sits at the 80.7175th percentile of the stocks, above 360 of 446. |
| 4 | none, not a replication | WML sits at the 27.8027th percentile, above 124 of 446, so it is less persistent than most single stocks on this file. |
| 5 | none, not a replication | The quartiles use pandas' default linear interpolation. The median is negative, so on this file a factor above 0 is also above the median stock. That is a fact about this panel, and the criterion keeps both halves as declared. |
| 6 | none, not a replication | Under a series with no autocorrelation, an estimate from 83 months falls outside ±0.2151 about 5 percent of the time. Both factors sit inside it, so neither verdict rests on an autocorrelation 83 months can tell from zero. |
| 7 | none, not a replication | MKT's mean monthly return over the bill, times 12, is 0.0185, an arithmetic figure rather than a compounded one. Its plain t-statistic of 0.3660 is uncorrected for autocorrelation and decides nothing. |
| 8 | none, not a replication | WML's mean monthly return times 12 is 0.0241, with a plain t-statistic of 0.4505 that decides nothing. Survivorship moves a mean before it moves an autocorrelation, so this row carries the survivor-only label most loudly. |
| 9 | none, not a replication | Every formation has both legs, so the refusal for an empty leg never fires. At its smallest the loser leg holds 11 stocks, so WML's return that month rests on few short positions. |

### What the entry concludes

Three things, and the first is the verdict.

1. **On this file the claim holds for the market factor and not for the
   momentum factor.** MKT's autocorrelation is positive and above the median
   stock's. WML's is negative and below the median stock's. Each verdict
   stands on its own, with Chan's "often" quoted beside it, and the entry
   draws no combined verdict from the two.
2. **Neither autocorrelation is far from zero.** Both sit inside the band a
   series with no autocorrelation stays inside 95 percent of the time, so 83
   months cannot tell MKT's 0.0675 from no persistence at all. The verdict in
   row 1 is what the declared criterion says, and row 6 says how little it
   rests on.
3. **The median stock sits below 0 on this file.** Its lag-1 autocorrelation
   is −0.0392, so a factor above 0 is also above the median stock here. The
   comparison set is survivors, so where the median sits is a fact about this
   panel rather than about single stocks in general.

### What this entry cannot say

Four things.

**What survivorship does to WML.** The panel lacks the stocks that left the
index before 2007-11-23, and the two legs lose different ones.
[Issue 198](https://github.com/l3a0/quantitative-trading/issues/198) waits on
a panel of the index as it stood each day, which would measure it.

**Whether the factors persist at another frequency.** Only monthly returns
were computed, by the rule on the issue, so a daily autocorrelation was not
tried after the monthly one was seen.

**Whether French's published factors agree.** Kenneth French's library
publishes a market and a momentum factor built on every listed stock.
[Issue 274](https://github.com/l3a0/quantitative-trading/issues/274) records
that library as a vintage, and the skip here matches its momentum factor's so
the two can be set side by side.

**What the other two factors of location 3978 do.** SMB and HML need market
capitalisation and book value at each date, which this repo does not hold.
[Issue 273](https://github.com/l3a0/quantitative-trading/issues/273) carries
them.

Nothing checks this entry against the suite, for the reason Entry 1 states. A
change to any assertion named above moves this entry in the same commit.
