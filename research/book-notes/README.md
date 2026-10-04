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

*Algorithmic Trading*'s Example 7.2 is the opposite case. Its two book
figures, its denominator of 30 and its levered 27 percent all sit at location
3024, while the figures its script prints sit in `pead.m` and nowhere in the
book. The replication log's Entry 12 traces each to one or the other.

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
