"""What the committed continuous futures saves and ``VIX.csv`` hold, and what moves between them.

[Issue 313](https://github.com/l3a0/quantitative-trading/issues/313) lifted
four saves of Chan's ``inputDataOHLCDaily`` file from *Algorithmic Trading*,
named for 2012-05-04, 2012-05-07, 2012-05-11 and 2012-05-17, and his
``VIX.csv``. The lift checked every member against its ``.mat`` column, every
field, exactly. The ``.mat`` files are not committed, so these pin what that
check saw in figures the committed bytes still carry.

A save is named here by the date in its file's name, the way the issue and the
scripts name it. Its saved date, from the MAT header, is one to three days
later and is what each entry records.

Each member keeps its own calendar, so a member is read as
``load_panel(source)[symbol].dropna()``. The panel's index is the union of every
member's days, which is not the file's layout.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan.series import departures, load_panel, panel_line, vintage_overlap
from chan.vintage import LIFTED_FIELDS
from tests.support.committed_vintages import LIFTED_SOURCES

SAVES = {
    "20120504": "inputDataOHLCDaily_20120504.mat",
    "20120507": "inputDataOHLCDaily_20120507.mat",
    "20120511": "inputDataOHLCDaily_20120511.mat",
    "20120517": "inputDataOHLCDaily_20120517.mat",
}

#: The symbols a script of Chan's reads from one of these saves.
READ_BY_A_SCRIPT = ("CL", "ES", "TU", "VX", "FSTX")


def member(save: str, symbol: str, field: str = "Close"):
    """One member's entry and its own rows, which is how a replication reads it."""
    entries, panel = load_panel(SAVES[save], field=field)
    (entry,) = [entry for entry in entries if entry.symbol == symbol]
    return entry, panel[symbol].dropna()


def moved(older: str, newer: str, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The two saves' closes side by side, and the days they differ at all."""
    overlap = vintage_overlap(member(older, symbol), member(newer, symbol))
    return overlap, departures(overlap, tolerance=0.0)


def distinct_differences(overlap: pd.DataFrame) -> int:
    """How many different amounts the newer save sits above the older one, zero included.

    Rounded to the micro-unit, because a subtraction of two binary floats
    lands a hair either side of the difference the two printed prices make.
    """
    return len(set(np.round((overlap["newer"] - overlap["older"]).to_numpy(), 6)))


class TestTheCommittedSavesAreChansColumns:
    @pytest.mark.parametrize(
        ("save", "members", "rows", "length", "first", "last"),
        [
            ("20120504", 51, 50_259, 1000, "2008-04-02", "2012-05-04"),
            ("20120507", 53, 97_128, 2000, "1995-10-20", "2012-05-08"),
            ("20120511", 52, 95_167, 2000, "1995-10-20", "2012-05-11"),
            ("20120517", 52, 95_219, 2000, "1995-10-20", "2012-05-17"),
        ],
    )
    def test_each_save_holds_its_members_on_their_own_calendars(
        self, save: str, members: int, rows: int, length: int, first: str, last: str
    ) -> None:
        """No member is longer than the save's ``tday``, and the panel is not one calendar."""
        entries, panel = load_panel(SAVES[save])

        assert len(entries) == members == LIFTED_SOURCES[SAVES[save]][4]
        assert sum(entry.row_count for entry in entries) == rows
        assert max(entry.row_count for entry in entries) == length
        assert (min(e.first_date for e in entries), max(e.last_date for e in entries)) == (
            first,
            last,
        )
        assert len(panel) > length

    @pytest.mark.parametrize("save", list(SAVES))
    def test_every_symbol_a_script_reads_is_priced_on_every_row(self, save: str) -> None:
        length = 1000 if save == "20120504" else 2000
        entries, _ = load_panel(SAVES[save])
        held = {entry.symbol: entry.row_count for entry in entries}

        assert {symbol: held[symbol] for symbol in READ_BY_A_SCRIPT if symbol in held} == {
            symbol: length for symbol in READ_BY_A_SCRIPT if symbol != "ES" or save != "20120504"
        }

    @pytest.mark.parametrize("save", list(SAVES))
    def test_every_field_is_priced_on_exactly_the_days_the_close_is(self, save: str) -> None:
        _, closes = load_panel(SAVES[save])
        for field in LIFTED_FIELDS[1:]:
            _, panel = load_panel(SAVES[save], field=field)
            assert (panel.notna() == closes.notna()).all().all(), field

    def test_cl_is_back_adjusted(self) -> None:
        """The 2012-05-04 save's CL is the front contract shifted at each roll.

        The front contract is the earliest contract priced on a day in Chan's
        ``inputDataDaily_CL_20120502.mat``, which
        [issue 300](https://github.com/l3a0/quantitative-trading/issues/300)
        lifted. Its symbols sort in expiry order, because the month codes F to Z
        are in alphabetical order. On 2008-05-19 the save sits 48.43 above it,
        and by 2012-04-10 the gap has closed to 0.51, which is the shape of a
        history shifted by every later roll's gap.
        """
        _, strip = load_panel("inputDataDaily_CL_20120502.mat")
        contracts = strip[[symbol for symbol in strip.columns if not symbol.endswith("-SPOT")]]
        front = contracts.bfill(axis=1).iloc[:, 0].dropna()
        _, cl = member("20120504", "CL")
        shared = cl.index.intersection(front.index)

        assert cl.loc["2008-05-19"] == 175.48
        assert front.loc["2008-05-19"] == 127.05
        assert round(cl.loc["2012-04-10"] - front.loc["2012-04-10"], 6) == 0.51
        assert len(shared) == 998
        assert int((cl.loc[shared] == front.loc[shared]).sum()) == 8

    def test_tu_holds_the_day_tu_mom_anchors_on(self) -> None:
        """``TU_mom.m`` starts its holding period on 2009-01-02, a row of TU's own column."""
        _, tu = member("20120511", "TU")

        assert pd.Timestamp("2009-01-02") in tu.index

    def test_each_save_names_itself_in_one_line(self) -> None:
        assert panel_line(load_panel(SAVES["20120507"])[0]) == (
            "inputdataohlcdaily_20120507/   chan-mat adjusted, saved 2012-05-09, "
            "53 members lifted from inputDataOHLCDaily_20120507.mat"
        )


class TestTheColumnWithNoName:
    """The 2012-05-07 save's sixth column, kept as ``COLUMN-6`` under the owner's ruling."""

    def test_it_is_the_2012_05_11_save_s_c(self) -> None:
        column, unnamed = member("20120507", "COLUMN-6")
        _, later = member("20120511", "C")
        shared = unnamed.index.intersection(later.index)

        assert column.path == "inputdataohlcdaily_20120507/column-6.csv"
        assert len(unnamed) == 2000
        assert len(shared) == 1997
        assert (unnamed.loc[shared] == later.loc[shared]).all()

    def test_it_keeps_three_days_no_later_save_holds(self) -> None:
        _, unnamed = member("20120507", "COLUMN-6")
        _, later = member("20120511", "C")

        assert [str(day.date()) for day in unnamed.index.difference(later.index)] == [
            "2004-05-28",
            "2004-06-01",
            "2004-06-02",
        ]

    def test_the_same_save_s_own_c_is_another_series(self) -> None:
        _, unnamed = member("20120507", "COLUMN-6")
        _, own = member("20120507", "C")
        shared = unnamed.index.intersection(own.index)

        assert float(np.median(own.loc[shared] - unnamed.loc[shared])) == -48.75


class TestWhatMovesBetweenSaves:
    """A back-adjusted series is rewritten at every roll, so a later save restates history.

    The tolerance is zero, because every save is one source's binary floats.
    """

    @pytest.mark.parametrize(
        ("older", "newer"),
        [("20120504", "20120507"), ("20120507", "20120511"), ("20120511", "20120517")],
    )
    def test_tu_never_moves_on_a_shared_day(self, older: str, newer: str) -> None:
        overlap, differ = moved(older, newer, "TU")

        assert len(overlap) > 0
        assert differ.empty

    def test_cl_moves_by_one_constant_between_the_2012_05_07_and_2012_05_11_saves(self) -> None:
        overlap, differ = moved("20120507", "20120511", "CL")

        assert len(overlap) == len(differ) == 1997
        assert set(np.round((overlap["newer"] - overlap["older"]).to_numpy(), 6)) == {0.27}
        assert moved("20120504", "20120507", "CL")[1].empty
        assert moved("20120511", "20120517", "CL")[1].empty

    @pytest.mark.parametrize(
        ("symbol", "older", "newer", "shared", "agree", "distinct"),
        [
            ("ES", "20120507", "20120511", 1997, 294, 17),
            ("VX", "20120507", "20120511", 1997, 3, 79),
            ("FSTX", "20120511", "20120517", 1996, 45, 25),
        ],
    )
    def test_the_symbols_rolled_in_between_take_many_differences(
        self, symbol: str, older: str, newer: str, shared: int, agree: int, distinct: int
    ) -> None:
        overlap, differ = moved(older, newer, symbol)

        assert len(overlap) == shared
        assert len(overlap) - len(differ) == agree
        assert distinct_differences(overlap) == distinct

    @pytest.mark.parametrize(
        ("symbol", "older", "newer"),
        [
            ("ES", "20120511", "20120517"),
            ("VX", "20120511", "20120517"),
            ("FSTX", "20120507", "20120511"),
        ],
    )
    def test_and_hold_still_across_the_other_pair(
        self, symbol: str, older: str, newer: str
    ) -> None:
        assert moved(older, newer, symbol)[1].empty

    def test_the_first_two_saves_differ_mostly_on_the_earlier_one_s_last_day(self) -> None:
        """18 of 51 agree on every field. 31 differ on 2012-05-04 alone, FFI on two, BZ on all."""
        earlier = {field: load_panel(SAVES["20120504"], field=field)[1] for field in LIFTED_FIELDS}
        later = {field: load_panel(SAVES["20120507"], field=field)[1] for field in LIFTED_FIELDS}
        days_differing = {}
        for symbol in earlier["Close"].columns:
            days = set()
            for field in LIFTED_FIELDS:
                old, new = earlier[field][symbol].dropna(), later[field][symbol].dropna()
                shared = old.index.intersection(new.index)
                days |= set(shared[old.loc[shared].to_numpy() != new.loc[shared].to_numpy()])
            days_differing[symbol] = days

        counts = {symbol: len(days) for symbol, days in days_differing.items()}
        assert sum(count == 0 for count in counts.values()) == 18
        assert {symbol: count for symbol, count in counts.items() if count > 1} == {
            "BZ": 1000,
            "FFI": 2,
        }
        one_day = [days for days in days_differing.values() if len(days) == 1]
        assert len(one_day) == 31
        assert {day for days in one_day for day in days} == {pd.Timestamp("2012-05-04")}

    def test_only_cl_and_qm_move_by_one_constant(self) -> None:
        """The shift a roll makes is measured for CL and QM, and not for C, ES, GC or VX.

        Between the 2012-05-07 and 2012-05-11 saves, 46 shared symbols do not
        move. CL and QM move by one constant, which is a back-adjusting roll.
        The other four change by neither one constant nor one factor, which is
        why ``data/README.md`` says their method was not measured.
        """
        older, newer = load_panel(SAVES["20120507"])[1], load_panel(SAVES["20120511"])[1]
        kinds: dict[str, list[str]] = {"same": [], "shift": [], "other": []}
        for symbol in sorted(set(older.columns) & set(newer.columns)):
            old, new = older[symbol].dropna(), newer[symbol].dropna()
            shared = old.index.intersection(new.index)
            gaps = set(np.round((new.loc[shared] - old.loc[shared]).to_numpy(), 6))
            factors = set(np.round((new.loc[shared] / old.loc[shared]).to_numpy(), 6))
            if gaps == {0.0}:
                kinds["same"].append(symbol)
            elif len(gaps) == 1:
                kinds["shift"].append(symbol)
            else:
                assert len(factors) > 1, symbol
                kinds["other"].append(symbol)

        assert len(kinds["same"]) == 46
        assert kinds["shift"] == ["CL", "QM"]
        assert kinds["other"] == ["C", "ES", "GC", "VX"]


class TestTheBondColumnsSkipTenYears:
    """ZB, ZF and ZN jump from 1998-03-10 to 2008-04 between two adjacent rows.

    Their stretch before the jump is sparse too, with gaps of up to 103 days.
    No other column in any save skips more than ten days between rows.
    """

    @pytest.mark.parametrize("save", ["20120507", "20120511", "20120517"])
    @pytest.mark.parametrize(
        ("symbol", "after"), [("ZB", "2008-04-16"), ("ZF", "2008-04-16"), ("ZN", "2008-04-17")]
    )
    def test_the_widest_gap_is_the_decade(self, save: str, symbol: str, after: str) -> None:
        _, closes = member(save, symbol)
        gaps = closes.index.to_series().diff()
        widest = gaps.idxmax()

        assert closes.index[closes.index.get_loc(widest) - 1] == pd.Timestamp("1998-03-10")
        assert widest == pd.Timestamp(after)
        assert gaps.drop(widest).max() <= pd.Timedelta(days=103)

    @pytest.mark.parametrize("save", list(SAVES))
    def test_no_other_column_skips_more_than_ten_days(self, save: str) -> None:
        _, panel = load_panel(SAVES[save])
        wide = {}
        for symbol in panel.columns:
            gaps = panel[symbol].dropna().index.to_series().diff()
            long = gaps[gaps > pd.Timedelta(days=10)]
            if len(long):
                wide[symbol] = long.index.max()

        assert set(wide) == ({"ZB", "ZF", "ZN"} if save != "20120504" else set())
        assert all(day <= pd.Timestamp("2008-04-17") for day in wide.values())


class TestVix:
    def test_it_is_one_raw_vintage_under_chan_csv(self) -> None:
        (entry,), panel = load_panel("VIX.csv")

        assert (entry.vendor, entry.symbol, entry.price_basis, entry.saved_date) == (
            "chan-csv",
            "VIX",
            "raw",
            "2012-05-09",
        )
        assert (entry.path, entry.row_count) == ("vix/vix.csv", 5635)
        assert (entry.first_date, entry.last_date) == ("1990-01-02", "2012-05-08")
        assert list(panel.columns) == ["VIX"]

    def test_its_volume_is_non_zero_on_136_days(self) -> None:
        _, volume = load_panel("VIX.csv", field="Volume")

        assert int((volume["VIX"] != 0).sum()) == 136

    def test_its_one_flagged_day_is_a_real_move(self) -> None:
        _, closes = load_panel("VIX.csv")

        assert closes.loc["2007-02-26":"2007-02-27", "VIX"].tolist() == [11.15, 18.31]
