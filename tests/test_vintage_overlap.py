"""The pins for setting two vintages of one series against each other.

``docs/design.md`` defines a raw price as fixed once the day has passed, "so it
is the same in every vintage". That is a claim two downloads can be checked
against, and this file is where it is checked. The adjusted half of the same
premise, that an adjusted series moves when a dividend falls between two
downloads, is ``TestAdjustedCloseMovesWithTheDownloadDate`` in
``tests/test_pair_cointegration.py``. The two together are the premise test
[issue 4](https://github.com/l3a0/quantitative-trading/issues/4) asked for, and
[issue 139](https://github.com/l3a0/quantitative-trading/issues/139) is what
specified the comparison.

The case order is the order the rules appear on issue 139, which is the
convention ``tests/test_scale_breaks.py`` states for itself against issue 3.

This is its own file rather than more of ``tests/test_scale_breaks.py``,
because that file reads each series against itself and this one reads a series
against a second download of it. They catch different failures, and the
synthetic split below is a case one catches and the other cannot.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from chan.kelly_leverage import compare_vintages
from chan.series import departures, load_vintage, scale_breaks, vintage_overlap
from chan.vintage import VintageEntry

#: Chan's workbook prints cents and yfinance prints a binary float, so the two
#: cannot agree more closely than half a cent. That is the tolerance every
#: comparison against one of his files uses.
HALF_A_CENT = 0.005

SPY_CHAN_RAW = "spy_unadjusted_chan.csv"
SPY_YFINANCE_RAW = "yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv"


def _entry(path: str, *, symbol: str = "XYZ", price_basis: str = "raw") -> VintageEntry:
    """A manifest entry for a synthetic series, which no file backs."""
    return VintageEntry(
        vendor="test",
        symbol=symbol,
        price_basis=price_basis,
        first_date="2020-01-02",
        last_date="2020-01-06",
        path=path,
        row_count=3,
        sha256="0" * 64,
        download_date="2020-01-07",
    )


def _closes(*values: float, start: str = "2020-01-02") -> pd.Series:
    return pd.Series(values, index=pd.bdate_range(start, periods=len(values)), dtype=float)


# ============================================================
# Rule 1 -- two vintages of one symbol, side by side
# ============================================================


class TestTheOverlap:
    """The frame holds both closes and their ratio on every shared day, and nothing else."""

    def test_it_keeps_only_the_days_both_hold_with_newer_over_older(self) -> None:
        older = (_entry("older.csv"), _closes(100.0, 102.0, 104.0, 106.0))
        newer = (_entry("newer.csv"), _closes(51.0, 52.0, 53.0, start="2020-01-03"))
        overlap = vintage_overlap(older, newer)

        assert list(overlap.columns) == ["older", "newer", "ratio"]
        assert [str(day.date()) for day in overlap.index] == [
            "2020-01-03",
            "2020-01-06",
            "2020-01-07",
        ]
        assert overlap["ratio"].tolist() == pytest.approx([0.5, 0.5, 0.5])
        assert overlap.attrs["vintages"] == (older[0], newer[0])

    def test_a_vintage_repeating_a_date_is_refused(self) -> None:
        repeated = _closes(1.0, 2.0)
        repeated.index = pd.DatetimeIndex(["2020-01-02", "2020-01-02"])
        with pytest.raises(ValueError, match="older.csv repeats a date"):
            vintage_overlap((_entry("older.csv"), repeated), (_entry("newer.csv"), _closes(1.0)))

    def test_two_symbols_are_refused(self) -> None:
        with pytest.raises(ValueError, match="two series rather than two vintages of one"):
            vintage_overlap(
                (_entry("a.csv", symbol="AAA"), _closes(1.0)),
                (_entry("b.csv", symbol="BBB"), _closes(1.0)),
            )

    def test_a_pair_sharing_no_day_is_refused_rather_than_read_as_agreement(self) -> None:
        """An empty frame holds no departure, so returning one would read as agreement."""
        with pytest.raises(ValueError, match="share no day"):
            vintage_overlap(
                (_entry("older.csv"), _closes(1.0, 2.0)),
                (_entry("newer.csv"), _closes(1.0, 2.0, start="2021-01-04")),
            )


# ============================================================
# Rule 2 -- a pair on two price bases is refused
# ============================================================


class TestTwoBasesAreRefused:
    """An adjusted close drifts from a raw one by construction, which is not a restatement."""

    def test_a_synthetic_pair_on_two_bases_is_refused(self) -> None:
        with pytest.raises(ValueError, match="raw basis and newer.csv the adjusted one"):
            vintage_overlap(
                (_entry("older.csv"), _closes(100.0)),
                (_entry("newer.csv", price_basis="adjusted"), _closes(80.0)),
            )

    def test_chans_gld_against_yfinance_raw_is_refused(self) -> None:
        """The first of the cross-basis pairs pinned below, which the refusal is for."""
        with pytest.raises(ValueError, match="measures the adjustment, not a restatement"):
            vintage_overlap(load_vintage("GLD", chan=True), load_vintage("GLD", unadjusted=True))


# ============================================================
# Rule 3 -- departures at a tolerance in price units
# ============================================================


class TestDepartures:
    """The days two vintages disagree on, at half a unit in the coarser one's last digit."""

    @staticmethod
    def _overlap(older: pd.Series, newer: pd.Series) -> pd.DataFrame:
        return vintage_overlap((_entry("older.csv"), older), (_entry("newer.csv"), newer))

    def test_a_difference_inside_the_tolerance_agrees(self) -> None:
        overlap = self._overlap(_closes(44.88, 127.95), _closes(44.875, 127.9500001))
        assert departures(overlap, tolerance=HALF_A_CENT).empty

    def test_a_difference_outside_it_departs_and_names_the_day(self) -> None:
        overlap = self._overlap(_closes(44.88, 127.95), _closes(44.875, 127.90))
        found = departures(overlap, tolerance=HALF_A_CENT)
        assert [str(day.date()) for day in found.index] == ["2020-01-03"]

    def test_a_tie_at_exactly_half_a_cent_agrees_despite_the_subtraction(self) -> None:
        """45.125 against 45.13 is half a cent on paper and 0.0050000000000026 in a float."""
        overlap = self._overlap(_closes(45.13), _closes(45.125))
        assert abs(overlap["newer"].iloc[0] - overlap["older"].iloc[0]) > HALF_A_CENT
        assert departures(overlap, tolerance=HALF_A_CENT).empty


# ============================================================
# Rule 4 -- a ratio that is not a finite positive number departs
# ============================================================


class TestARatioNobodyCanReadDeparts:
    """Each arises from finite inputs, and none of them is agreement.

    A zero close is what ``_validated_rows`` allows for a halted day, a NaN is
    what the parse makes of an unreadable value, and a negative close passes
    every check that reads only the size of a difference.
    """

    @pytest.mark.parametrize(
        ("older", "newer", "why"),
        [
            (0.0, 0.0, "zero over zero is NaN although the closes are equal"),
            (0.0, 0.001, "a zero denominator is infinite although the closes differ by 0.001"),
            (100.0, math.nan, "a NaN close"),
            (0.001, -0.001, "a negative ratio although the closes differ by 0.002"),
        ],
    )
    def test_it_is_reported(self, older: float, newer: float, why: str) -> None:
        overlap = vintage_overlap(
            (_entry("older.csv"), _closes(older)), (_entry("newer.csv"), _closes(newer))
        )
        assert len(departures(overlap, tolerance=HALF_A_CENT)) == 1, why


# ============================================================
# Done-when 5 -- a split between two downloads
# ============================================================


class TestASplitBetweenDownloads:
    """The case issue 139 exists for, which no check on one series can see.

    A vendor that applies a split after the first download rescales the whole
    history behind it, so the later vintage reads half the earlier one on every
    shared day. Neither series has a step, so the scale-break guard passes
    both, and every day-over-day return is unchanged, so a comparison of
    returns passes them too. The constant ratio is the only trace.
    """

    OLDER = (_entry("older.csv"), _closes(100.0, 102.0, 104.0))
    NEWER = (_entry("newer.csv"), _closes(50.0, 51.0, 52.0))

    def test_the_ratio_is_the_split_factor_on_every_shared_day(self) -> None:
        overlap = vintage_overlap(self.OLDER, self.NEWER)
        assert overlap["ratio"].round(4).tolist() == [0.5, 0.5, 0.5]
        assert len(departures(overlap, tolerance=HALF_A_CENT)) == 3

    def test_the_guard_on_either_series_alone_reports_nothing(self) -> None:
        assert scale_breaks(self.OLDER[1]) == []
        assert scale_breaks(self.NEWER[1]) == []

    def test_a_comparison_of_returns_reads_it_as_agreement(self) -> None:
        """Why ``chan.kelly_leverage.compare_vintages`` is not reused for this."""
        compared = compare_vintages(self.OLDER[1], self.NEWER[1])
        assert compared.mean_gap == pytest.approx(0.0, abs=1e-12)


# ============================================================
# Done-when 3 and 4 -- the cross-basis ratios, a proxy rather than the check
# ============================================================


class TestTheCrossBasisRatiosAreAProxy:
    """What the repo could measure before a second raw vintage existed.

    The first two set Chan's adjusted file against yfinance's raw download,
    which the comparison refuses, so they are computed here by hand. They read
    as 1 only because Chan's 2007 adjusted close was near raw for GLD and GDX,
    which ``docs/design.md``'s premise already reasons about. The third sets
    his GDX file against yfinance's adjusted download, both adjusted, and reads
    0.851. That is what shows the first two are a proxy: the same file against
    a vintage nineteen years of dividends later is 15% away.

    Each is an approximate equality rather than a bound, because every one
    rounds the wrong way for an inclusive comparison. ``1.00000 <= min`` fails
    all three and ``max <= 1.00304`` fails two. Vintages: ``gld_chan.csv`` and
    ``gdx_chan.csv``, last saved 2007-12-02, against
    ``gld_20yr_prices_unadjusted.csv``, ``gdx_20yr_prices_unadjusted.csv`` and
    ``gdx_20yr_prices.csv``, downloaded from yfinance on 2026-08-27.
    Specification: modern over Chan's, on every day both hold. First measured
    at ``a6144e6`` and unchanged at nine digits at ``85193df``.
    """

    @staticmethod
    def _by_hand(older: pd.Series, newer: pd.Series) -> pd.Series:
        shared = older.index.intersection(newer.index)
        return newer.loc[shared] / older.loc[shared]

    def test_gld_chans_adjusted_against_yfinance_raw(self) -> None:
        ratio = self._by_hand(
            load_vintage("GLD", chan=True)[1], load_vintage("GLD", unadjusted=True)[1]
        )
        assert len(ratio) == 764
        assert float(ratio.min()) == pytest.approx(0.999999944, abs=5e-10)
        assert float(ratio.max()) == pytest.approx(1.000229751, abs=5e-10)

    def test_gdx_chans_adjusted_against_yfinance_raw(self) -> None:
        ratio = self._by_hand(
            load_vintage("GDX", chan=True)[1], load_vintage("GDX", unadjusted=True)[1]
        )
        assert len(ratio) == 385
        assert float(ratio.min()) == pytest.approx(0.999999950, abs=5e-10)
        assert float(ratio.max()) == pytest.approx(1.003041161, abs=5e-10)

    def test_gdx_two_adjusted_vintages_nineteen_years_apart(self) -> None:
        overlap = vintage_overlap(load_vintage("GDX", chan=True), load_vintage("GDX"))
        assert len(overlap) == 385
        assert float(overlap["ratio"].min()) == pytest.approx(0.850983407, abs=5e-10)
        assert float(overlap["ratio"].max()) == pytest.approx(0.851210251, abs=5e-10)


# ============================================================
# Done-when 2 -- the raw half of the premise, on SPY
# ============================================================


@pytest.fixture(scope="module")
def overlap() -> pd.DataFrame:
    """SPY's two raw vintages on the days both hold, Chan's as the older."""
    return vintage_overlap(
        load_vintage("SPY", chan=True, unadjusted=True), load_vintage("SPY", unadjusted=True)
    )


class TestRawCloseAcrossTwoDownloads:
    """SPY's as-traded close as Chan saved it in 2008 and as yfinance returned it in 2026.

    yfinance's ``raw`` is split-adjusted, which
    [issue 133](https://github.com/l3a0/quantitative-trading/issues/133)
    records, so "the same in every vintage" fails for any symbol that splits.
    SPY has never split, so this pair tests the claim where it should hold.

    It holds on 3,756 of the 3,758 shared days, to the half cent Chan's file
    can carry. The other two are a disagreement between the two vendors' closes
    for the day, which nothing here can settle. On 2006-08-07 Chan's file reads
    127.95 and yfinance 127.90, and on 2007-05-21 they read 152.61 and 152.54.
    ``data/README.md`` records what the download showed about the first. Neither
    is a split, a dividend or a rounding, and each vendor's adjusted column
    agrees with its own raw one on both days, so the disagreement is in the
    close each vendor holds rather than in one file's transcription.

    Vintages: ``spy_unadjusted_chan.csv``, the as-traded ``Close`` of Chan's
    ``example6_2.xls``, last saved 2008-01-29, against
    ``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``, ``Close``
    from yfinance 1.7.0 called with ``auto_adjust=False`` on 2026-10-03.
    Specification: yfinance's close less Chan's on every day both hold,
    1993-01-29 to 2007-12-28, departing where it is more than half a cent.
    First pinned on 2026-10-03.
    """

    def test_the_pair_is_the_two_raw_vintages_named(self, overlap: pd.DataFrame) -> None:
        older, newer = overlap.attrs["vintages"]
        assert (older.path, newer.path) == (SPY_CHAN_RAW, SPY_YFINANCE_RAW)
        assert len(overlap) == 3758
        assert (str(overlap.index[0].date()), str(overlap.index[-1].date())) == (
            "1993-01-29",
            "2007-12-28",
        )

    def test_two_days_depart_and_these_are_the_closes_each_vendor_holds(
        self, overlap: pd.DataFrame
    ) -> None:
        found = departures(overlap, tolerance=HALF_A_CENT)
        assert [str(day.date()) for day in found.index] == ["2006-08-07", "2007-05-21"]
        assert found["older"].tolist() == [127.95, 152.61]
        assert found["newer"].round(2).tolist() == [127.90, 152.54]

    def test_every_other_day_agrees_to_the_half_cent(self, overlap: pd.DataFrame) -> None:
        """247 of them sit on the half cent exactly, none after 2001.

        Those are prices quoted in eighths before US exchanges moved to
        decimals in 2001, such as 45.125. yfinance keeps the eighth and Chan's
        file carries cents, rounding up on 132 of those days and down on 115.
        So the two differ by the rounding and by nothing else.
        """
        found = departures(overlap, tolerance=HALF_A_CENT)
        agreeing = overlap.drop(found.index)
        gap = agreeing["newer"] - agreeing["older"]
        assert float(gap.abs().max()) == pytest.approx(HALF_A_CENT, abs=1e-12)
        ties = gap[(gap.abs() - HALF_A_CENT).abs() < 1e-9]
        assert len(ties) == 247
        assert ((ties < 0).sum(), (ties > 0).sum()) == (132, 115)
        assert ties.index.year.max() == 2001

    def test_each_vendor_agrees_with_itself_on_the_departing_days(
        self, overlap: pd.DataFrame
    ) -> None:
        """Adjusted over raw moves by under 1e-4 into and out of each departing day.

        A close typed wrong in one column would move that ratio by the size of
        the departure, which is 3.9e-4 and 4.6e-4 of the price. So each vendor
        carries the same close in both of its columns, and what departs is the
        close the two vendors hold. yfinance's adjusted column is the
        2026-09-18 download, ``yfinance_spy_adjusted_1993-01-29_2026-09-18_dl2026-09-18.csv``.
        """
        pairs = {
            "chan": (load_vintage("SPY", chan=True)[1], overlap["older"]),
            "yfinance": (load_vintage("SPY")[1], overlap["newer"]),
        }
        for day in ("2006-08-07", "2007-05-21"):
            at = overlap.index.get_loc(pd.Timestamp(day))
            around = overlap.index[at - 1 : at + 2]
            for vendor, (adjusted, raw) in pairs.items():
                ratio = (adjusted.loc[around] / raw.loc[around]).to_numpy()
                assert np.abs(np.diff(ratio)).max() < 1e-4, (day, vendor)
            departure = abs(overlap.loc[day, "ratio"] - 1.0)
            assert departure > 3.5e-4
