"""Pins for Chan's toy strategy for survivorship bias, Example 3.3.

This file is the single authority for every number any prose surface quotes
about this experiment. ``docs/replication-log.md`` Entry 7 states those numbers
and derives none of them, and ``src/chan/survivorship_bias.py`` carries the
reasoning.

Every pin reads the book's two printed tables, revised edition, Example 3.3,
between Kindle locations 1423 and 1474, under the equal-capital specification
unless its name says otherwise. No vintage enters, so the vintage each pin names
is none, the book's printed tables.

The pins sit at ``abs=1e-9``, which is far tighter than the two decimals of a
percent the log quotes. The inputs are exact printed decimals with no vendor
noise, so the arithmetic has nothing else to absorb, and the tight tolerance is
what lets the suite hold the tables themselves. A sweep over all forty printed
cells, run when these pins were written and not asserted here, found that
moving any one by a unit in its last digit shifts a book figure by at least
1.38e-6, the smallest being RAZF's start price, and fails a test. A pin at
``abs=5e-5`` would let 14 of those forty edits pass, measured by the same sweep.
"""

from __future__ import annotations

import pytest

from chan.survivorship_bias import (
    BOOK_REF,
    SURVIVOR_PICKS,
    UNBIASED_PICKS,
    UNBIASED_TOP_PRICE,
    contributions,
    equal_capital_return,
    equal_shares_return,
    main,
    one_share_basis,
)

TOL = 1e-9

# The engine's full values, as fractions rather than percents.
UNBIASED = -0.417179352020
SURVIVOR = 3.878820431279
UNBIASED_SHARES = -0.476195313558
SURVIVOR_SHARES = 3.731739022780
NEOF_SHARE = 3.088571428571
SURVIVOR_ONE_BASIS = 1.009106145565


class TestBookFigures:
    """The two figures location 1471 prints, under equal capital."""

    def test_the_survivorship_free_portfolio_loses_42_percent(self) -> None:
        got = equal_capital_return(UNBIASED_PICKS)

        assert got == pytest.approx(UNBIASED, abs=TOL)
        assert round(got * 100) == -42

    def test_the_survivor_only_portfolio_gains_388_percent(self) -> None:
        got = equal_capital_return(SURVIVOR_PICKS)

        assert got == pytest.approx(SURVIVOR, abs=TOL)
        assert round(got * 100) == 388

    def test_book_ref_states_the_figures_the_suite_computes(self) -> None:
        """``BOOK_REF`` is the line the report prints under its title, so the
        whole percents it quotes must be what the arithmetic rounds to."""
        assert f"{round(equal_capital_return(UNBIASED_PICKS) * 100)} percent" in BOOK_REF
        assert f"{round(equal_capital_return(SURVIVOR_PICKS) * 100)} percent" in BOOK_REF
        assert "location 1471" in BOOK_REF


class TestTheNearMiss:
    """One share of each, which weights every stock by its price.

    Pinned beside the book's specification for the reason
    ``tests/test_coin_flip_growth.py`` pins the sample standard deviation beside
    the population one: a pin on the right number alone holds a number rather
    than a choice.
    """

    def test_equal_shares_on_the_survivorship_free_picks(self) -> None:
        got = equal_shares_return(UNBIASED_PICKS)

        assert got == pytest.approx(UNBIASED_SHARES, abs=TOL)
        assert round(got * 100) != -42

    def test_equal_shares_on_the_survivor_picks(self) -> None:
        got = equal_shares_return(SURVIVOR_PICKS)

        assert got == pytest.approx(SURVIVOR_SHARES, abs=TOL)
        assert round(got * 100) != 388


class TestTheTables:
    """What Chan's account of the two lists says about them, asserted."""

    def test_each_table_holds_ten_picks(self) -> None:
        assert len(UNBIASED_PICKS) == 10
        assert len(SURVIVOR_PICKS) == 10

    def test_nine_of_the_survivorship_free_picks_were_delisted(self) -> None:
        delisted = [p.symbol for p in UNBIASED_PICKS if p.delisted]

        assert len(delisted) == 9
        assert "MDM" not in delisted

    def test_no_survivor_pick_was_delisted(self) -> None:
        assert not any(p.delisted for p in SURVIVOR_PICKS)

    def test_mdm_is_the_one_stock_in_both_tables(self) -> None:
        both = {p.symbol for p in UNBIASED_PICKS} & {p.symbol for p in SURVIVOR_PICKS}
        assert both == {"MDM"}
        assert [p for p in UNBIASED_PICKS if p.symbol == "MDM"] == [
            p for p in SURVIVOR_PICKS if p.symbol == "MDM"
        ]

    def test_the_second_table_continues_the_first_ranking(self) -> None:
        """Every survivor-only pick except MDM starts above the first table's
        highest price, because a survivor database skips the nine stocks it
        lacks and keeps going up the ranking."""
        assert max(p.start for p in UNBIASED_PICKS) == UNBIASED_TOP_PRICE
        others = [p for p in SURVIVOR_PICKS if p.symbol != "MDM"]

        assert all(p.start > UNBIASED_TOP_PRICE for p in others)
        assert min(p.start for p in others) == 0.8438

    def test_each_table_is_in_the_book_row_order(self) -> None:
        """The book sorts both tables by start price, and the selection rule
        is a ranking by start price, so a row out of order is a row mistyped."""
        for picks in (UNBIASED_PICKS, SURVIVOR_PICKS):
            starts = [p.start for p in picks]
            assert starts == sorted(starts)


class TestTheReverseSplit:
    """NEOF's row compares a pre-split price with a post-split one.

    Neoforma's FY2001 10-K states a 1-for-10 reverse split effective
    2001-08-27. Only NEOF was checked against a filing.
    """

    def test_neof_carries_most_of_the_survivor_only_return(self) -> None:
        shares = contributions(SURVIVOR_PICKS)

        assert sum(shares.values()) == pytest.approx(SURVIVOR, abs=TOL)
        assert shares["NEOF"] == pytest.approx(NEOF_SHARE, abs=TOL)
        assert shares["NEOF"] > SURVIVOR / 2

    def test_on_one_share_basis_the_survivor_portfolio_still_gains(self) -> None:
        got = equal_capital_return(one_share_basis(SURVIVOR_PICKS))

        assert got == pytest.approx(SURVIVOR_ONE_BASIS, abs=TOL)
        assert got > 0 > equal_capital_return(UNBIASED_PICKS)

    def test_only_neof_moves(self) -> None:
        adjusted = one_share_basis(SURVIVOR_PICKS)

        moved = [a.symbol for a, p in zip(adjusted, SURVIVOR_PICKS, strict=True) if a != p]
        assert moved == ["NEOF"]
        assert one_share_basis(UNBIASED_PICKS) == UNBIASED_PICKS

    def test_the_start_price_moves_and_the_end_price_stays(self) -> None:
        """Dividing the end price by the split ratio gives the same return, so
        no figure tells the two apart. The module says the 1/2/2001 price is
        the one that predates the split, and this holds that it is the one
        moved."""
        (neof,) = [p for p in one_share_basis(SURVIVOR_PICKS) if p.symbol == "NEOF"]

        assert neof.start == pytest.approx(8.75, abs=TOL)
        assert neof.end == 27.9


class TestTheReport:
    """What ``python -m chan.survivorship_bias`` prints."""

    def test_it_names_what_it_read(self, capsys: pytest.CaptureFixture[str]) -> None:
        main()
        lines = capsys.readouterr().out.splitlines()

        assert lines[1].strip() == BOOK_REF
        assert "  vintage: none, the book's printed tables" in lines
        assert "  window: the close on 1/2/2001 to the close on 1/2/2002" in lines

    def test_it_prints_the_figures_it_labels(self, capsys: pytest.CaptureFixture[str]) -> None:
        main()
        out = capsys.readouterr().out

        for figure in (
            UNBIASED,
            SURVIVOR,
            UNBIASED_SHARES,
            SURVIVOR_SHARES,
            NEOF_SHARE,
            SURVIVOR_ONE_BASIS,
        ):
            assert f"{figure:+.2%}" in out
        assert "docs/replication-log.md Entry 7 carries the verdict." in out
