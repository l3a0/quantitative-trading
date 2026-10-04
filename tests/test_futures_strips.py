"""What Chan's committed futures strips and his 16:00 gold series hold.

[Issue 300](https://github.com/l3a0/quantitative-trading/issues/300) lifted
eight strips from *Algorithmic Trading*, one vintage per contract, and one gold
series. The ``.mat`` files are not committed, so the lift compared each strip
with its file there and then, and these cases pin what that comparison saw in
figures the committed bytes still carry.

- **Vintages.** The nine directories ``data/README.md`` lists for those
  sources, vendor ``chan-mat``, basis ``raw``, each member carrying the close
  alone and the saved date its file's MAT header records. Their identities are
  the nine rows of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **Specification.** Each strip is read whole by
  :func:`chan.series.load_panel`, so a day a contract did not settle is NaN.
  A contract has expired when its last settlement falls before the file's
  last day, and its last day is that settlement, which is how Chan's scripts
  find it. The expiry rule checked is :func:`chan.futures.rbob_last_trade`, the
  last business day of the month before delivery, on NYMEX's calendar.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from chan.futures import rbob_last_trade
from chan.series import load_panel, scale_breaks
from chan.vintage import read_manifest, resolve_vintage
from tests.support.committed_vintages import LIFTED_SOURCES

#: CME's month letters, January first. They run alphabetically in calendar
#: order, which is what lets a sorted panel stand in for Chan's contract order.
MONTHS = "FGHJKMNQUVXZ"

#: Each strip, its root, and what its panel holds: days, priced cells, first
#: and last day, and how many columns stop and restart.
STRIPS = [
    ("inputDataDaily_BR_20120813.mat", "BR", 4216, 92_718, "1995-11-01", "2012-08-13", 15),
    ("inputDataDaily_C2_20120813.mat", "C2", 6492, 25_168, "1986-11-03", "2012-08-13", 0),
    ("inputDataDaily_CL_20120813.mat", "CL", 6467, 100_500, "1986-11-03", "2012-08-13", 1),
    ("inputDataDaily_HG_20120813.mat", "HG", 6473, 87_382, "1986-11-03", "2012-08-13", 29),
    ("inputDataDaily_HO2_20120813.mat", "HO2", 6467, 131_051, "1986-11-03", "2012-08-13", 31),
    ("inputDataDaily_TU_20120813.mat", "TU", 5565, 18_283, "1990-06-22", "2012-08-13", 2),
    ("inputDataDaily_CL_20120502.mat", "CL", 2867, 92_440, "2000-11-20", "2012-05-02", 0),
    ("inputDataDaily_VX_20120507.mat", "VX", 1543, 12_279, "2006-03-23", "2012-05-07", 0),
]

GOLD = "inputData_GC_1600_20100802.mat"


def contract_key(symbol: str) -> tuple[int, int]:
    """A contract symbol's delivery year and month, read off ``<root>-<year><letter>``."""
    contract = symbol.rsplit("-", 1)[1]
    return int(contract[:4]), MONTHS.index(contract[4]) + 1


def restarts(column: pd.Series) -> bool:
    """Whether a column has a NaN between its first and last settlement."""
    held = np.flatnonzero(column.notna().to_numpy())
    return bool(len(held)) and held[-1] - held[0] + 1 != len(held)


class TestEachStripIsChansArray:
    @pytest.mark.parametrize(("source", "root", "days", "priced", "first", "last", "holes"), STRIPS)
    def test_each_panel_has_the_shape_and_the_priced_cells_of_chan_s_array(
        self,
        source: str,
        root: str,
        days: int,
        priced: int,
        first: str,
        last: str,
        holes: int,
    ) -> None:
        entries, panel = load_panel(source)

        assert panel.shape == (days, LIFTED_SOURCES[source][4])
        assert int(panel.notna().to_numpy().sum()) == priced
        assert (str(panel.index[0].date()), str(panel.index[-1].date())) == (first, last)
        assert panel.notna().any(axis=1).all()
        assert sum(restarts(panel[symbol]) for symbol in panel.columns) == holes
        assert {entry.price_basis for entry in entries} == {"raw"}

    @pytest.mark.parametrize(("source", "root"), [strip[:2] for strip in STRIPS])
    def test_sorted_symbols_are_delivery_order_with_the_spot_last(
        self, source: str, root: str
    ) -> None:
        """``calendarSpdsMeanReversion.m`` pairs contracts by position, so the
        panel's column order has to be Chan's. Four strips hold the spot first,
        and sorting puts it last, after every contract."""
        _, panel = load_panel(source)
        symbols = list(panel.columns)
        contracts = [symbol for symbol in symbols if symbol != f"{root}-SPOT"]

        assert all(symbol.startswith(f"{root}-") for symbol in symbols)
        assert contracts == sorted(contracts, key=contract_key)
        assert symbols[: len(contracts)] == contracts

    def test_six_strips_carry_a_spot_column_and_two_do_not(self) -> None:
        spot = {source for source, root, *_ in STRIPS if f"{root}-SPOT" in load_panel(source)[1]}

        assert {source for source, *_ in STRIPS} - spot == {
            "inputDataDaily_CL_20120502.mat",
            "inputDataDaily_VX_20120507.mat",
        }

    def test_one_row_pinned_by_value_so_a_column_read_from_the_wrong_contract_fails(
        self,
    ) -> None:
        """2008-01-02 is where ``calendarSpdsMeanReversion.m`` starts, and the
        two contracts 12 months apart are the spread it trades."""
        _, panel = load_panel("inputDataDaily_CL_20120813.mat")

        assert panel.loc["2008-01-02", ["CL-2008G", "CL-2009G"]].to_dict() == {
            "CL-2008G": 99.62,
            "CL-2009G": 93.04,
        }
        assert panel.loc["1986-11-03"].dropna().to_dict() == {"CL-SPOT": 14.88}

    def test_one_contract_in_two_strips_is_told_apart_by_its_saved_date(self) -> None:
        """The two CL strips both hold ``CL-2008G`` under one vendor and basis,
        so only the date names which save a reader means."""
        found = {
            dated: resolve_vintage(
                vendor="chan-mat", symbol="CL-2008G", price_basis="raw", dated=dated
            ).path
            for dated in ("2012-05-03", "2012-08-14")
        }

        assert found == {
            "2012-05-03": "inputdatadaily_cl_20120502/cl-2008g.csv",
            "2012-08-14": "inputdatadaily_cl_20120813/cl-2008g.csv",
        }

    def test_no_two_vintages_share_vendor_symbol_basis_and_date(self) -> None:
        """The case no reader argument can separate, which is why a contract's
        symbol carries its root: six strips share the saved date 2012-08-14."""
        keys = [(e.vendor, e.symbol, e.price_basis, e.obtained) for e in read_manifest()]

        assert len(keys) == len(set(keys))


HEATING_OIL = "inputDataDaily_HO2_20120813.mat"


@pytest.fixture(scope="module")
def expiries() -> dict[str, tuple[pd.Timestamp, pd.Timestamp]]:
    """Each expired HO2 contract's last settlement and the RBOB rule's day for it."""
    _, panel = load_panel(HEATING_OIL)
    found = {}
    for symbol in panel.columns:
        if symbol == "HO2-SPOT":
            continue
        last = panel[symbol].last_valid_index()
        if last == panel.index[-1]:
            continue
        found[symbol] = (last, pd.Timestamp(rbob_last_trade(*contract_key(symbol))))
    return found


class TestHeatingOilExpiresOnTheRbobRule:
    """RBOB's rule is heating oil's too, and ``chan.futures`` already holds it.

    Measured on HO2's contracts that stop before the file does. Most last settle
    on the rule's day. Where they do not, the rule's day is usually missing from
    Chan's calendar, so the contract stops on the row before it.
    """

    def test_300_of_309_expired_contracts_last_settle_on_the_rule_s_day(self, expiries) -> None:
        on = [symbol for symbol, (last, rule) in expiries.items() if last == rule]

        assert (len(on), len(expiries)) == (300, 309)

    def test_8_stop_the_day_before_a_rule_s_day_the_file_has_no_row_for(self, expiries) -> None:
        _, panel = load_panel(HEATING_OIL)
        missing = {
            symbol: (str(last.date()), str(rule.date()))
            for symbol, (last, rule) in expiries.items()
            if last != rule and rule not in panel.index
        }

        assert missing == {
            "HO2-1986Z": ("1986-11-26", "1986-11-28"),
            "HO2-1994F": ("1993-12-30", "1993-12-31"),
            "HO2-1996Z": ("1996-11-27", "1996-11-29"),
            "HO2-1997Z": ("1997-11-26", "1997-11-28"),
            "HO2-2000F": ("1999-12-30", "1999-12-31"),
            "HO2-2002Z": ("2002-11-27", "2002-11-29"),
            "HO2-2003Z": ("2003-11-26", "2003-11-28"),
            "HO2-2005F": ("2004-12-30", "2004-12-31"),
        }
        for last, rule in missing.values():
            following = panel.index[panel.index.get_loc(pd.Timestamp(last)) + 1]
            assert following > pd.Timestamp(rule)

    def test_one_stops_a_day_early_on_a_day_the_file_holds(self, expiries) -> None:
        _, panel = load_panel(HEATING_OIL)
        early = {
            symbol: (str(last.date()), str(rule.date()))
            for symbol, (last, rule) in expiries.items()
            if last < rule and rule in panel.index
        }

        assert early == {"HO2-2012Q": ("2012-07-30", "2012-07-31")}
        assert not [s for s, (last, rule) in expiries.items() if last > rule]


class TestTheGoldSeries:
    def test_it_is_one_raw_series_named_for_its_root(self) -> None:
        entries, panel = load_panel(GOLD)

        assert [(e.symbol, e.price_basis, e.saved_date) for e in entries] == [
            ("GC", "raw", "2012-05-07")
        ]
        assert panel.shape == (761, 1)
        assert (str(panel.index[0].date()), str(panel.index[-1].date())) == (
            "2007-08-03",
            "2010-08-02",
        )
        assert panel["GC"].notna().all()
        assert (panel["GC"].iloc[0], panel["GC"].iloc[-1]) == (721.7, 1182.6)


class TestTheGuardFlagsNothing:
    def test_no_member_of_the_nine_changes_scale(self) -> None:
        """Every member is a ``raw`` price, so the guard reads each against
        itself across its own rows, holes included, and none moves by more than
        the bound in a day."""
        flagged = {}
        for source in [strip[0] for strip in STRIPS] + [GOLD]:
            _, panel = load_panel(source)
            for symbol in panel.columns:
                days = scale_breaks(panel[symbol].dropna())
                if days:
                    flagged[symbol] = days

        assert flagged == {}
