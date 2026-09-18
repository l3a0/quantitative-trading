# Book notes

Kindle highlights from the book this repo replicates, quoted verbatim and cited
by Kindle location.

| Note | Book | Edition | Highlights |
| --- | --- | --- | --- |
| [quantitative-trading.md](quantitative-trading.md) | *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* | 2nd (Revised), Wiley, 2021 | 235 |

The file came from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, byte for
byte. That repo also holds notes for Chan's *Algorithmic Trading* and for four
other authors. They stayed there, because nothing here replicates those books.

Mind the edition. These notes are the revised second edition of 2021, while
this repo's citations of chapter and page numbers come from the first edition
of 2009. The two are not interchangeable, and these notes are what showed it:
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

A second kind of absence turns up in Example 6.2, and it costs more than a
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
switches off three rules and keeps the rest. Two fire on the book's own text:
websites cited in running prose without a scheme, and a `* i` that is
multiplication rather than emphasis. The third is the note format, which runs
one h1 title and then one h3 per highlight. The only way to satisfy any of them
here would be to alter the quotation, and a re-extraction would undo the
alteration anyway.

That directory config also covers this README, which is the price of putting
the exemption next to what it governs. The three rules it relaxes are minor
style checks, and every other markdownlint rule still applies here.

The two prose sweeps in `tests/test_markdown_hygiene.py` do still read this
directory, including the note itself, because the note happens to contain
nothing either sweep objects to. If a future re-extraction or a second note
introduces something they flag, the fix is an exemption written down here, not
an edit to the quotation.

## Copyright

These are highlights from a book under copyright, kept for reference and cited
by location. The file carries its full citation. They are quotation, not a
substitute for the book, and nothing here reproduces a work in full.
