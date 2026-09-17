# Book notes

Kindle highlights from the books this repo replicates, quoted verbatim and
cited by Kindle location. They are the source of the published figures a
replication tries to match, so a number that appears in a test starts here.

Two notes, both Ernest Chan.

| Note | Book | Edition | Highlights |
| --- | --- | --- | --- |
| [quantitative-trading.md](quantitative-trading.md) | *Quantitative Trading: How to Build Your Own Algorithmic Trading Business* | 2nd (Revised), Wiley, 2021 | 235 |
| [algorithmic-trading.md](algorithmic-trading.md) | *Algorithmic Trading: Winning Strategies and Their Rationale* | Wiley, 2013 | 301 |

Both came from the sibling
[trading-strategies](https://github.com/l3a0/trading-strategies) repo, byte for
byte. Chan's other books are not here because nothing in this repo replicates
them yet, and the notes for other authors stayed in the sibling for the same
reason.

## What a highlight carries

Each entry gives the Kindle location and the highlight's text. Amazon's export
limit truncates some highlights on the notebook page and hides others entirely.
Those were recovered from the Cloud Reader and carry a `↻` tag. A span that
crosses a table, a figure or a display equation carries `≈`, meaning the text
is faithful but the exact boundaries are best-effort. Each file's own header
gives its counts.

## These files are quoted, not authored

The two prose sweeps in `tests/test_markdown_hygiene.py` skip this directory,
and `QUOTED_SOURCE_DIRS` in `tests/support/markdown_sweep.py` is where that is
written down. The sweeps catch a slip an author made. There is no author here
to correct, and the only way to satisfy the tilde rule inside a quotation is to
edit the quotation. One highlight in `algorithmic-trading.md` quotes a URL
containing a tilde, which is what forced the question.

The exemption covers those two rules and nothing else. markdownlint still runs
over these files in CI, and a test pins the excused set to this directory, so
widening it breaks the suite rather than passing quietly.

Editing a highlight's text is out of bounds. A note is a record of what the
book says, and a record that has been tidied is no longer evidence. Fix a
transcription error by re-extracting from the source, not by hand.

## Copyright

These are highlights from books under copyright, kept for reference and cited
by location. Each file carries its full citation. They are quotation, not a
substitute for the book, and nothing here reproduces a work in full.
