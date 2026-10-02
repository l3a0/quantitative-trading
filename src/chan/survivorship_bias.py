"""Chan's toy strategy for survivorship bias, Example 3.3.

Survivorship bias is what a backtest suffers when its database keeps only the
stocks that are still trading. Chan warns at Kindle location 1012 that it hits
a strategy buying cheap stocks hardest, because some stocks are cheap because
the company is about to fail. A database of survivors drops exactly those, so
the backtest buys the cheap stocks that recovered and never the ones that went
to zero. He points the reader to a toy strategy that shows it, and this module
works that toy.

The strategy buys the 10 lowest-priced stocks among the 1,000 largest by market
capitalisation at the close on 1/2/2001, puts equal capital in each, and sells
at the close on 1/2/2002. Chan prints two ten-row tables of picks.

1. ``UNBIASED_PICKS`` is what a survivorship-free database picks. Nine of the
   ten stocks were delisted during the year, so for those the book gives a
   terminal price, the last price traded on or before 1/2/2002. Only MDM has a
   close on that date.
2. ``SURVIVOR_PICKS`` is what a database of survivors picks instead. It keeps
   MDM and continues up the price ranking past the nine stocks it never held.

Location 1471 prints the two returns: −42 percent for the first table, which
Chan calls the return a trader would actually have had, and 388 percent for the
second, which he calls fictitious.

**The inputs are the book's printed tables, not a vintage.** The twenty rows
below are copied from the revised edition, Example 3.3, which sits between the
highlights at Kindle locations 1423 and 1474 of
``research/book-notes/quantitative-trading.md``. They were read through the
Kindle Cloud Reader on 2026-10-02, recorded on
[issue 213](https://github.com/l3a0/quantitative-trading/issues/213), and
checked a second time against a zoomed capture of the page. A vintage is a
series a vendor was asked for or a column lifted from one of Chan's own files,
and a table printed in a book is neither. A vendor cannot restate a printed
number, so what pins these inputs is the edition, and the run prints
``vintage: none, the book's printed tables``.

The universe of 1,000 stocks is not printed, so the selection step cannot be
re-run. Everything from the picks to the two returns can, and both printed
figures sit downstream of the picks.

**The label is a revised-edition one.** ``docs/design.md`` reads every example
number in this repo as first-edition unless it says otherwise, and this one
says otherwise. Whether the 2009 edition numbers the example the same way and
prints the same tables was not checked.

**The specification is equal capital, and the near miss is equal shares.** The
book's own rule puts equal capital in each stock, so the portfolio return is the
mean of the ten per-stock returns. :func:`equal_capital_return` does that and
reproduces both printed figures. Buying one share of each instead weights every
stock by its price, which :func:`equal_shares_return` computes. It misses both
figures, and it is pinned beside the right one so the suite holds a choice
rather than a number.

**NEOF's row mixes two share bases.** Neoforma's FY2001 10-K, filed on EDGAR at
https://www.sec.gov/Archives/edgar/data/1096219/000101287002001537/d10k.htm,
states a 1-for-10 reverse split effective 2001-08-27, and restates its
quarterly price tables for it. So NEOF's 0.875 on 1/2/2001 is a price before
the split and its 27.9 on 1/2/2002 a price after it. Read as printed, NEOF alone
carries most of the survivor-only return. :func:`one_share_basis` puts NEOF's
start price on the post-split basis by multiplying it by
``NEOF_REVERSE_SPLIT``, and on that basis the survivor-only portfolio still
gains, by far less than the printed figure.
``tests/test_survivorship_bias.py`` holds both figures. Only NEOF was checked
against a filing, and the other nineteen rows are taken as printed.

That is a finding about Chan's table, and it does not overturn the
reproduction. The printed 388 percent is what his table gives, and the claim it
was printed to support, that a survivor-only backtest turns a loss into a gain,
survives the correction.

``tests/test_survivorship_bias.py`` is the single authority for every number
quoted about this experiment, and ``docs/replication-log.md`` Entry 7 carries
the verdict.

Usage::

    python -m chan.survivorship_bias
"""

from __future__ import annotations

from dataclasses import dataclass, replace

BOOK_REF = (
    "Example 3.3 (rev. ed., location 1471): equal capital in the 10 cheapest of "
    "the 1,000 largest stocks, 1/2/2001 to 1/2/2002, returns -42 percent "
    "survivorship-free and 388 percent on survivors only"
)

START_DATE = "1/2/2001"
END_DATE = "1/2/2002"

# The price every survivor-only pick other than MDM must start above, because
# the second table continues the first's ranking past the stocks it lacks. It
# is RTHM's start price, the highest in the first table.
UNBIASED_TOP_PRICE = 0.8125

# Neoforma's 1-for-10 reverse split, effective 2001-08-27, from its FY2001
# 10-K. One share after the split is ten shares before it, so a pre-split price
# is put on the post-split basis by multiplying it by this.
NEOF_REVERSE_SPLIT = 10


@dataclass(frozen=True)
class Pick:
    """One row of a printed table.

    ``end`` is the close on 1/2/2002 for a stock still trading then, and the
    book's terminal price for one that was delisted during the year. The
    survivorship-free table prints NaN in its 1/2/2002 column for those nine
    stocks and gives the terminal price in a column of its own, and the
    terminal price is what a holder actually got out.
    """

    symbol: str
    start: float
    end: float
    delisted: bool

    @property
    def ret(self) -> float:
        """The simple return from ``start`` to ``end``."""
        return self.end / self.start - 1.0


# The survivorship-free picks, in the book's row order: symbol, close on
# 1/2/2001, then the terminal price. MDM is the only one with a close on
# 1/2/2002, which equals its terminal price of 0.49. RTHM's terminal price is
# printed as 0.3000.
UNBIASED_PICKS: tuple[Pick, ...] = (
    Pick("ETYS", 0.2188, 0.125, True),
    Pick("MDM", 0.3125, 0.49, False),
    Pick("INTW", 0.4063, 0.11, True),
    Pick("FDHG", 0.5, 0.33, True),
    Pick("OGNC", 0.6875, 0.2, True),
    Pick("MPLX", 0.7188, 0.8, True),
    Pick("GTS", 0.75, 0.35, True),
    Pick("BUYX", 0.75, 0.17, True),
    Pick("PSIX", 0.75, 0.2188, True),
    Pick("RTHM", 0.8125, 0.3, True),
)

# The survivor-only picks, in the book's row order: symbol, close on 1/2/2001,
# close on 1/2/2002. Every stock here was still trading at the end, which is
# the bias.
SURVIVOR_PICKS: tuple[Pick, ...] = (
    Pick("MDM", 0.3125, 0.49, False),
    Pick("ENGA", 0.8438, 0.44, False),
    Pick("NEOF", 0.875, 27.9, False),
    Pick("ENP", 0.875, 0.05, False),
    Pick("MVL", 0.9583, 2.5, False),
    Pick("URBN", 1.0156, 3.0688, False),
    Pick("FNV", 1.0625, 0.81, False),
    Pick("APT", 1.125, 0.88, False),
    Pick("FLIR", 1.2813, 9.475, False),
    Pick("RAZF", 1.3438, 0.25, False),
)


def equal_capital_return(picks: tuple[Pick, ...]) -> float:
    """The book's specification: equal capital in each stock, held for the year.

    Equal capital makes the portfolio return the plain mean of the per-stock
    returns. A delisted stock enters at its terminal price, which is what its
    holder got out, rather than being dropped, which is the error the example
    exists to show.
    """
    return sum(p.ret for p in picks) / len(picks)


def equal_shares_return(picks: tuple[Pick, ...]) -> float:
    """The near miss: one share of each, which weights every stock by its price."""
    return sum(p.end for p in picks) / sum(p.start for p in picks) - 1.0


def contributions(picks: tuple[Pick, ...]) -> dict[str, float]:
    """Each stock's share of the equal-capital return, which sums to that return."""
    return {p.symbol: p.ret / len(picks) for p in picks}


def one_share_basis(picks: tuple[Pick, ...]) -> tuple[Pick, ...]:
    """The same picks with NEOF's start price put on its post-split basis.

    NEOF's 1/2/2001 price predates the reverse split and its 1/2/2002 price
    follows it, so the printed row compares two different shares. Multiplying
    the start price by ``NEOF_REVERSE_SPLIT`` compares one share to one share.
    Every other row is returned unchanged.
    """
    return tuple(
        replace(p, start=p.start * NEOF_REVERSE_SPLIT) if p.symbol == "NEOF" else p for p in picks
    )


def main() -> None:
    """Print both tables' returns beside the book's and the NEOF correction."""
    unbiased = equal_capital_return(UNBIASED_PICKS)
    survivor = equal_capital_return(SURVIVOR_PICKS)
    neof = contributions(SURVIVOR_PICKS)["NEOF"]
    print("Chan's toy strategy for survivorship bias, Example 3.3 (revised edition)")
    print(f"  {BOOK_REF}")
    print("  vintage: none, the book's printed tables")
    print(f"  window: the close on {START_DATE} to the close on {END_DATE}")
    print()
    print("Equal capital, the book's specification:")
    print(f"  survivorship-free = {unbiased:+.2%}   (the book prints -42 percent)")
    print(f"  survivors only    = {survivor:+.2%}   (the book prints 388 percent)")
    print()
    print("Equal shares, the near miss, which reproduces neither:")
    print(f"  survivorship-free = {equal_shares_return(UNBIASED_PICKS):+.2%}")
    print(f"  survivors only    = {equal_shares_return(SURVIVOR_PICKS):+.2%}")
    print()
    print("NEOF's row spans a 1-for-10 reverse split, effective 2001-08-27:")
    print(f"  NEOF's share of the survivor-only return = {neof:+.2%}")
    print(
        f"  survivors only, NEOF on one share basis  = "
        f"{equal_capital_return(one_share_basis(SURVIVOR_PICKS)):+.2%}"
    )
    print("  The loss against a gain survives the correction. The size of the")
    print("  printed gap does not.")
    print()
    print("A replication is exploratory when a sample was spent looking. This one")
    print("spends none, so neither that label nor its opposite reaches it.")
    print("docs/replication-log.md Entry 7 carries the verdict.")


if __name__ == "__main__":
    main()
