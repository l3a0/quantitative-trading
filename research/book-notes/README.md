# Book notes

Kindle highlights from the books this repo replicates, quoted verbatim and
cited by Kindle location.

They carry some of the published figures a replication tries to match, and not
all of them. Chan's GLD/GDX hedge of 1.6766 and his KO/PEP return correlation
of 0.4849 are both quoted here. His CADF statistic of -3.357, his KO/PEP hedge
of 1.0114 and its statistic of -2.14 are not: a highlight covers the sentences
somebody marked, which is a different set from the numbers a replication ends
up chasing. Where a figure is here, this is where it traces to.

Two notes, both Ernest Chan.

| Note | Book | Edition | Highlights |
| --- | --- | --- | --- |
| [quantitative-trading.md](quantitative-trading.md) | *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* | 2nd (Revised), Wiley, 2021 | 235 |
| [algorithmic-trading.md](algorithmic-trading.md) | *Algorithmic Trading: Winning Strategies and Their Rationale* | Wiley, 2013 | 301 |

Both came from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, byte for
byte.

Mind the edition. These notes are the revised second edition of *Quantitative
Trading*, published in 2021, while this repo's citations of chapter and page
numbers come from the first edition of 2009. The two are not interchangeable,
and [issue 12](https://github.com/l3a0/quantitative-trading/issues/12) carries
what that unsettles.

Chan's other books are not here because nothing in this repo replicates them
yet, and the notes for other authors stayed in the sibling for the same reason.

## What a highlight carries

Each entry gives the Kindle location and the highlight's text. Amazon's export
limit truncates some highlights on the notebook page and hides others entirely.
Those were recovered from the Cloud Reader and carry a `↻` tag. A span that
crosses a table, a figure or a display equation carries `≈`, meaning the text
is faithful but the exact boundaries are best-effort.

Each file's header gives its total and how many were recovered. Neither counts
the `≈` spans, of which there are two, both in the Algorithmic Trading notes.
The totals are asserted in `tests/test_book_notes.py`, so a re-extraction that
returns fewer highlights fails the suite instead of passing quietly.

## These files are quoted, not authored

The two prose sweeps in `tests/test_markdown_hygiene.py` skip this directory,
and `QUOTED_SOURCE_DIRS` in `tests/support/markdown_sweep.py` is where that is
written down. The sweeps catch a slip an author made. There is no author here
to correct, and the only way to satisfy the tilde rule inside a quotation is to
edit the quotation. One highlight in `algorithmic-trading.md` quotes a URL
containing a tilde, which is what forced the question.

A test pins the excused set to this directory, so widening it breaks the suite
rather than passing quietly.

markdownlint still runs over these files, under
[.markdownlint.jsonc](.markdownlint.jsonc) in this directory, which switches
off four rules and keeps the rest. Three of the four fire on the books' own
text: websites cited in running prose, a quoted list that starts at 2 because
the highlight begins mid-list, and a `* i` that is multiplication rather than
emphasis. The fourth is the note format, which runs one h1 title and then one
h3 per highlight.

That directory config also covers this README, which is the price of putting
the exemption next to what it governs. The four rules it relaxes are minor
style checks, every other markdownlint rule still applies here, and the two
prose sweeps still read this file.

Editing a highlight's text is out of bounds. A note is a record of what the
book says, and a record that has been tidied is no longer evidence. Fix a
transcription error by re-extracting from the source, not by hand.

## Copyright

These are highlights from books under copyright, kept for reference and cited
by location. Each file carries its full citation. They are quotation, not a
substitute for the book, and nothing here reproduces a work in full.
