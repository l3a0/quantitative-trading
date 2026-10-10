# Book notes

Kindle highlights from the books this repo replicates, quoted verbatim and
cited by Kindle location.

| Note | Book | Edition | Highlights |
| --- | --- | --- | --- |
| [algorithmic-trading.md](algorithmic-trading.md) | *Algorithmic Trading: Winning Strategies and Their Rationale* | 1st, Wiley, 2013 | 301 |
| [quantitative-trading.md](quantitative-trading.md) | *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* | 2nd (Revised), Wiley, 2021 | 235 |

Both files came from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, byte for
byte. The *Algorithmic Trading* note is that repo's
`research/book-notes/algorithmic-trading.md` at `7612281`, and it landed here
with [PR #263](https://github.com/l3a0/quantitative-trading/pull/263), with
nothing changed on the way over. It came because
[issue 20](https://github.com/l3a0/quantitative-trading/issues/20) replicates
that book's Example 7.2, which is the first replication here from Chan's second
book. The sibling also holds notes for four other authors. They stayed there,
because nothing here replicates those books.

Mind the edition. The *Quantitative Trading* notes are the revised second
edition of 2021, while this repo's citations of chapter and page numbers for
that book come from the first edition of 2009. The two are not interchangeable, and these notes are what showed it:
the GLD/GDX chapter labels this repo uses throughout turn out to be
first-edition shorthand, because in this edition both printouts belong to one
Chapter 7 example and Chapter 3 defers the analysis at location 1862.
[docs/design.md](../../docs/design.md) carries the argument and what survives
it.

## What the notes carry

They hold some of the published figures a replication tries to match, and not
all of them. Chan's GLD/GDX hedge of 1.6766 and his KO/PEP return correlation
of 0.4849 are both quoted here. His CADF statistic of -3.357, his KO/PEP hedge
of 1.0114 and its statistic of -2.14 are not: a highlight covers the sentences
somebody marked, which is a different set from the numbers a replication ends
up chasing. Where a figure is here, this is where it traces to.

Examples 7.6 and 7.7 are absent the same way, and more completely. None of the
figures their four printouts give is here, the third January's 0.0881 and
0.088486 included, because every one is printed beside code. The replication log's Entry 7 traces each to the script
and commit that prints it, or to the owner's reading of the revised edition
recorded on
[issue 18](https://github.com/l3a0/quantitative-trading/issues/18#issuecomment-5960594931).

*Algorithmic Trading*'s Example 4.1 is the plain case. Every figure its entry
quotes from the book is here: the 8.7 percent and 1.5 at location 1974, the
mirror's 46 percent and 1.27 and its steeper drawdown at 1993, and the same
8.7 percent called an annualized average return at 3509. The script `bog.m`
repeats the first two in its closing comment and prints nothing the book
lacks. The replication log's Entry 18 traces each.

*Algorithmic Trading*'s Example 7.2 is the opposite case. Its two book
figures, its denominator of 30 and its levered 27 percent all sit at location
3024, while the figures its script prints sit in `pead.m` and nowhere in the
book. The replication log's Entry 12 traces each to one or the other.

Examples 4.3 and 4.4 of the same book split the same way. The six figures the
book prints are here: 13.7 percent and 1.3 and the 30 and 11 percent of 2008
and 2011 at location 2110, 73 percent and 4.7 at 2135, and 4.7 again at 2890.
The two figures `andrewlo_2007_2012.m` prints for Example 4.4, 0.731553 and
4.713284, sit in its closing comment and nowhere in the book. The replication
log's Entry 19 traces each to one or the other.

Examples 2.1 to 2.5 split the same way. The book's figures are here: the ADF
statistic of about −1.84 and the 10 percent critical value of −2.594 at
location 1114, H of 0.49 at 1119, and the half-life of 115 days at 1193 and
again at 1347. The six decimals of `stationarityTests.m`'s comments, −1.840744,
0.994120, the 1 and 5 percent critical values, the variance ratio's 0.367281
and 115.209794, sit in the script and nowhere in the book. The replication
log's Entry 22 traces each to one or the other.

Example 7.4 splits the same way. Its setup at location 4034 and its result at
4051 are here, including the 2 and 4 percent and Chan's account of the gap
between them as round-off. The figures its four programs print are not,
because the book prints them beside code: the first edition's −1.8099, the
revised MATLAB's 0.020205 and 0.211120, and the three 17-digit figures the
revised Python and R both print. The replication log's Entry 13 traces each to
its script or to the revised edition's page.

Example 3.8 is absent in both ways. Its setup sentence at location 2233 and
its closing exercise at 2236 are here, and the sentence carrying its result,
that both Sharpe ratios turn "very positive", is not. That sentence traces to
the owner's reading of p. 78, recorded on
[issue 17](https://github.com/l3a0/quantitative-trading/issues/17#issuecomment-5960534071).
The four figures Chan's notebooks print for Examples 3.7 and 3.8 are not here
either, because the book prints none of them. The replication log's Entry 10
traces each to the notebook and the repost it was read at.

Example 7.1 splits the same way. Its setup is here, at locations 3428, 3444,
3479 and 3517: the grid, the rules, the span and split, the features and the
model. Its results are not. The p. 145 table of Chan's eight figures and his
sentence that every other metric improves sit beside code and a figure, and the
endnote's recursions are rendered as images. The replication log's Entry 16
traces each to the pages read in the Kindle Cloud Reader on 2026-10-03,
recorded on
[issue 23](https://github.com/l3a0/quantitative-trading/issues/23).

*Algorithmic Trading*'s Example 6.2 splits the same way as its Example 7.2.
Its two 2007 figures, its −30 percent for 2008 and 2009 and its sentence that
the return "did stabilize" afterwards all sit at location 2800, while the five
figures its script's closing comment prints sit in `kentdaniel.m` and nowhere
in the book. The replication log's Entry 17 traces each to one or the other.

*Algorithmic Trading*'s Example 3.1 splits the same way, with one figure
that disagrees. Location 1505 prints the price spread's "about 10.9 percent"
and "about 0.59", the log price spread's 9 percent and 0.5, and the ratio's
"negative APR" with no number. The six-decimal figures sit in the closing
comments of `PriceSpread.m`, `LogPriceSpread.m` and `Ratio.m` and nowhere in
the book. The book's 10.9 percent is not its script's 0.108335 rounded. The
replication log's Entry 21 traces each to one or the other.

*Algorithmic Trading*'s Example 3.2 splits the same way, and here the book's
figures are its script's rounded. Location 1559 prints "APR = 17.8 percent,
and Sharpe ratio of 0.96" and calls the result "quite an improvement" on the
linear rule. The six-decimal figures, 0.178249 and 0.964673, sit in the
closing comment of `bollinger.m` and nowhere in the book. The replication
log's Entry 26 traces each to one or the other.

*Algorithmic Trading*'s Examples 2.6 to 2.8 split the same way as its
Example 7.2. The book's four figures are here: the CADF statistic of "about
–3.64" at location 1292, the half-life of 23 days at 1347, and the APR of 12.6
percent and Sharpe ratio of 1.4 at 1368. So are the claims at 1324 and 1337
about how many cointegrating relations each Johansen statistic finds. The
figures `cointegrationTests.m` prints sit in its comments and nowhere in the
book: −3.64346635, every Johansen statistic, critical value, eigenvalue and
eigenvector, the half-life of 22.662578, and 0.125739 and 1.391310. The
replication log's Entry 23 traces each to one or the other.

*Algorithmic Trading*'s Example 4.2 splits the same way. The book's 98
stocks, its APR of 4.5 percent and Sharpe ratio of 1.3, and its claims of
cointegration "with better than 95 percent probability" and of two
cointegrating relations are here, at location 2035. The figures `indexArb.m`
prints sit in its comments and nowhere in the book: every Johansen statistic
and critical value for the basket against SPY, its eigenvectors, and 0.044930
and 1.319397. The replication log's Entry 24 traces each to one or the other.

*Algorithmic Trading*'s Example 5.1 splits the same way. The book's figures
are here, at location 2237: the APR of 11 percent, the Sharpe ratio of 1.6, and
the window from December 18, 2009, to April 26, 2012. The figures
`AUDCAD_unequal.m` prints, 0.112410, 1.610890 and a Kelly leverage of
23.845328, sit in its comments and nowhere in the book. The replication log's
Entry 25 traces each to one or the other.

*Algorithmic Trading*'s Example 5.3 splits a third way, because its script
records no figure. The book's are here: the whole of Table 5.1 in the
recovered text of location 2399, with the corn row repeated at 2444, and
Figure 5.5's first day, November 22, 2004, in the same passage. The claims at
2399 and 2683 about which roll returns outweigh their spot returns are here
too. `estimateFuturesReturns.m` prints its two figures and keeps neither in
its comments. Chan's 2018 Python port of it does, for corn alone:
`0.02805562210100287` and `-0.12775650227459556` sit in its comments and
nowhere in the book. The replication log's Entry 27 traces each to one or the
other.

*Algorithmic Trading*'s VX against ES, in its Chapter 5, splits the same third
way, because `VX_ES.m` records no figure either. All four figures the book
prints are here, at location 2559: the hedge of 0.3906, the residual
deviation of $2,047, and the APR of 12.3 percent and Sharpe ratio of 1.4 on
the test set from July 29, 2010, to May 8, 2012.
The script prints none of them, and no script that ships computes the trade.
The replication log's Entry 28 traces each to the run that reaches it.

*Algorithmic Trading*'s Example 5.2 splits the same way as its Example 5.1.
The book's five figures are here, at location 2303: the APR of 6.2 percent and
Sharpe ratio of 0.54 with rollover interest, the 6.7 percent and 0.58 without
it, and the annualised rollover of "almost 5 percent". The two figures
`AUDCAD_daily.m` prints, 0.061564 and 0.541802, sit in its closing comment and
nowhere in the book. The replication log's Entry 30 traces each to one or the
other.

*Algorithmic Trading*'s crude oil rule, in its Chapter 6, is the opposite
case: both figures are in the book and in the script. The APR of 12 percent
and the Sharpe ratio of 1.1 sit at location 2701. `CL_rev.m` computes them,
and the comment under its `fprintf` records `APR=0.117600 Sharpe=1.100368`,
which rounds to both. The replication log's Entry 31 traces both to the
script's run.

*Algorithmic Trading*'s Kalman filter on EWA and EWC, in its Chapter 3, splits
the same way as its Example 3.2, and the book's figures are its script's
rounded. Location 1726 prints "a reasonable APR of 26.2 percent and a Sharpe
ratio of 2.4", and makes the two claims about the filter's slope and intercept.
The six-decimal figures, 0.262252 and 2.361162, sit in the closing comment of
`KF_beta_EWA_EWC.m` and nowhere in the book. The filter's equations are absent
the second way described below, as Examples 8.1 and 8.2's are. Locations 1658
and 1760 are here, and each equation survives in them only as its number, such
as "(3.5)". Box 3.1, which carries the equations the script labels 3.7 to
3.12, is not among the highlights. The replication log's Entry 32 traces each
figure to one or the other.

*Algorithmic Trading*'s Example 6.1 splits the way Examples 2.1 to 2.5 do. The
book's figures are here: the 250/25 correlation of 0.27 with a p-value of 0.02
at location 2659, H of 0.44 and the variance ratio test's failure to reject at
2646, and the Sharpe ratio of 1, the APR of 1.7 percent and the maximum
drawdown of 2.5 percent from June 1, 2004, to May 11, 2012, at 2668. The
figures `TU_mom.m`'s comment prints, 0.0167 twice, 1.04, −0.024847, 343 days
and a Kelly f of 64.919535, sit in the script and nowhere in the book. Table
6.2 is named at 2668 and none of its rows is here. The replication log's
Entry 33 traces each figure to one or the other.

*Algorithmic Trading*'s Example 5.4 splits the same way as its Example 6.1.
The book's figures are here: the half-life of 36 days and the claim that CL's
12-month log calendar spread is "stationary with 99 percent probability" at
location 2461, and the APR of 8.3 percent and Sharpe ratio of 1.3 from January
2, 2008, to August 13, 2012, at 2461 and again at 2471. Location 2471 holds a
pair for "3 months (61 trading days)", while `calendarSpdsMeanReversion.m`
sets `holddays=3*21`, which is 63. The figures the script's comments print,
a half-life of 36.394034, an APR of 0.083406, a Sharpe ratio of 1.288661, a
maximum drawdown of −0.053222 and a longest drawdown of 206 days, sit in the
script and nowhere in the book. The replication log's Entry 34
traces each figure to one or the other.

Every figure of *Algorithmic Trading*'s VX calendar spread, in its Chapter 5,
is in the book and none is in a script, the opposite of Example 5.4, whose
six-decimal figures sit in the script and nowhere in the book. The claim that
the ratio of back to front is "stationary with a 99 percent probability", the
APR of 17.7 percent and Sharpe ratio of 1.5 from
October 27, 2008, to April 23, 2012, and the claim that it "performed much
more poorly prior to October 2008" are all here, at location 2502. No script
ships under the experiment's own name. `calendarSpdsMeanReversion.m` carries a
commented-out load of the VX strip, and its comments print CL's figures, not
VX's. The replication log's Entry 35 traces each figure to the rows run
against it.

*Algorithmic Trading*'s Examples 8.1 and 8.2 are absent the second way
described below. Every figure their prose prints is here, at locations 3216
and 3287. Equations 8.1 to 8.4 are not, because the book renders each as an
image. The prose around them fixes their content, and location 3319 gives the
one-strategy growth rate inline, with its variance recovered as `m2` where
`s2` belongs. Whether Equation 8.3's image prints a value is not known from
here, which is why the replication log's Entry 20 row 11 carries no published
figure.

A second kind of absence turns up in *Quantitative Trading*'s Example 6.2, and
it costs more than a
missing figure. Every number that example prints is here. Its levered growth
formula is not, because the book renders that equation as an image at location
2849 and a highlight captures text. Its unlevered twin survives as inline text
at 2869, so the two halves of one specification are not equally reachable. A
formula is what a replication needs to know which quantity it is computing, so
[src/chan/kelly_leverage.py](../../src/chan/kelly_leverage.py) recovers the
missing one from Chan's own `example6_3.m` rather than reconstructing it, and
says so.

Each entry gives the Kindle location and the highlight's text. Amazon's export
limit truncates some highlights on the notebook page, and those were recovered
from the Cloud Reader and carry a `↻` tag. The header gives the total and how
many were recovered. Both totals are asserted in `tests/test_book_notes.py`, so
a re-extraction that returns fewer highlights fails the suite instead of
passing quietly.

## These files are quoted, not authored

Editing a highlight's text is out of bounds. A note is a record of what the
book says, and a record that has been tidied is no longer evidence. Fix a
transcription error by re-extracting from the source, not by hand.

That rule is what
[.markdownlint.jsonc](.markdownlint.jsonc) in this directory exists for. It
switches off four rules and keeps the rest. Three fire on the book's own text:
websites cited in running prose without a scheme, a `* i` that is
multiplication rather than emphasis, and a numbered list Chan prints whose
items were highlighted one at a time, so the *Algorithmic Trading* note's
item 2 at location 885 opens a list of its own. The fourth is the note format,
which runs one h1 title and then one h3 per highlight. The only way to satisfy any of them
here would be to alter the quotation, and a re-extraction would undo the
alteration anyway.

That directory config also covers this README, which is the price of putting
the exemption next to what it governs. The four rules it relaxes are minor
style checks, and every other markdownlint rule still applies here.

The prose sweeps in `tests/test_markdown_hygiene.py` do still read this
directory, notes included. When a note trips one, the fix is an exemption
written down here, not an edit to the quotation.

One exemption stands. The *Algorithmic Trading* note quotes Chan's pointer to a
Kalman filter package at location 1726, and the URL he prints,
`www.cs.ubc.ca/~murphyk/Software/Kalman/kalman.html`, carries a tilde glued to
a slash. The tilde sweep flags that shape, because it can close a
strikethrough. Escaping it would edit the book's text, so
`QUOTED_IN_A_NOTE` in the hygiene tests excuses that exact URL and nothing
else. Every other character of the line is still swept, and a test fails if
the exemption ever stops being needed.

## Copyright

These are highlights from a book under copyright, kept for reference and cited
by location. The file carries its full citation. They are quotation, not a
substitute for the book, and nothing here reproduces a work in full.
