"""The pins for spot and roll returns of five futures, *Algorithmic Trading*'s Example 5.3.

This file is the single authority for every number any prose surface quotes
about Example 5.3. ``docs/replication-log.md`` carries the verdicts and points
here row by row. The rows are the ones
[issue 347](https://github.com/l3a0/quantitative-trading/issues/347) declared
before the build, under "The pins".

Every pin on the committed files reads one vintage and one specification, so
both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** The five strips ``chan.roll_returns.ROOTS`` names in
  ``SOURCE_FILES``, ``inputdatadaily_{br,c2,cl,hg,tu}_20120813/``, chan-mat,
  raw, saved 2012-08-14, one vintage per contract and one for the spot, read
  for the close through :func:`chan.series.load_panel`. Their identities are
  the rows of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``,
  which ``TestTheVintages`` holds the members to. ``SOURCE_FILES`` also names
  the VX strip, saved 2012-05-08 with no spot, which ``TestTheVxStrip`` reads
  and which no figure here uses. ``OTHER_SAVES`` names CL's 2012-05-02 save,
  saved 2012-05-03 with no spot, which ``TestTheOtherSaves`` reads and which
  no figure here uses either.
- **Specification.** ``estimateFuturesReturns.m`` at the mirror commit
  :mod:`chan.roll_returns` names. α is 252 times the OLS slope of the log spot
  on the strip's row number, counted before the rows with no spot are dropped.
  γ is −12 times the OLS slope of the five nearest priced contracts' log
  prices on their column positions 1 to 5, on rows where those five are
  adjacent columns, averaged over the rows where it is defined.

Rows 1 to 10, Table 5.1's cells, are pinned two ways. ``BOOK_TABLE_5_1`` holds
the book's figure at one decimal of a percent, and ``TestTheFigures`` asserts
which cells round to it. The computed figure is pinned here alone at the six
decimals the script's ``%f`` prints, so a later change cannot move it inside
the book's rounding unnoticed. It is not a module constant, because the script
records no figure in its comments and a constant named for it would carry this
repo's number under Chan's name.

``TestTheReadingsTriedAfterTheMiss`` holds the three readings tried after HG's
and TU's α missed. ``TestTheRowsBeside`` holds the month-spaced γ, which has no
published figure and carries no verdict.

Exploratory. Reproducing Table 5.1 spends Chan's 1986 to 2012 strips on a
model he chose. It first ran here on 2026-10-05.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chan import roll_returns as module
from chan.roll_returns import (
    BOOK_TABLE_5_1,
    NO_SPOT_FILES,
    OTHER_SAVES,
    PORT_C2,
    ROOTS,
    SOURCE_FILES,
    Strip,
    StripReturns,
    contract_month,
    load_strip,
    main,
    maturity_spacings,
    roll_returns,
    roll_returns_in_months,
    run,
    spot_return,
    strip_returns,
)
from chan.series import WindowCrossesScaleBreak, load_panel, refuse_window_crossing_a_break
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

SPEC = (
    "inputdatadaily_*_20120813/ chan-mat raw strips saved 2012-08-14, alpha 252 times the "
    "slope of log spot on row number counted before dropping gaps, gamma -12 times the slope "
    "of the five nearest adjacent contracts' log prices on columns 1 to 5, averaged where "
    "defined"
)

BOOK_NOTES = Path(__file__).resolve().parents[1] / "research/book-notes/algorithmic-trading.md"

#: Each strip's α and γ at the six decimals ``%f`` prints.
COMPUTED = {
    "BR": ("-0.026903", "0.108133"),
    "C2": ("0.028056", "-0.127757"),
    "CL": ("0.073019", "-0.070592"),
    "HG": ("0.050567", "0.077172"),
    "TU": ("0.000039", "0.032032"),
}

#: γ with maturity measured in months, at six decimals.
COMPUTED_IN_MONTHS = {
    "BR": "0.108133",
    "C2": "-0.053011",
    "CL": "-0.070592",
    "HG": "0.038573",
    "TU": "0.010677",
}

# --- the committed strips ------------------------------------------------------


@pytest.fixture(scope="module")
def panels() -> dict[str, tuple]:
    return {root: load_panel(SOURCE_FILES[root]) for root in ROOTS}


@pytest.fixture(scope="module")
def strips(panels) -> dict[str, Strip]:
    """Each strip through the one read path, guard included, on the panels already read."""
    with pytest.MonkeyPatch.context() as patch:
        found = {}
        for root in ROOTS:
            patch.setattr(module, "load_panel", lambda *_a, _r=root, **_k: panels[_r])
            found[root] = load_strip(root)
    return found


@pytest.fixture(scope="module")
def results(strips) -> dict[str, StripReturns]:
    return {root: strip_returns(strip) for root, strip in strips.items()}


def lands(computed: float, book: float) -> bool:
    """Whether a computed fraction rounds to the book's percent at one decimal, sign included.

    The sign matters for TU's α, which the book prints as −0.0, a negative
    number that rounds to zero.
    """
    rounded = round(100 * computed, 1)
    return rounded == book and math.copysign(1, computed) == math.copysign(1, book)


class TestTheSpecification:
    def test_the_five_roots_are_table_5_1s_in_its_order(self) -> None:
        assert ROOTS == ("BR", "C2", "CL", "HG", "TU")

    def test_each_root_reads_the_file_the_scripts_load_line_names(self) -> None:
        """``estimateFuturesReturns.m``'s load lines read ``inputDataDaily_<root>_20120813``,
        and ``calendarSpdsMeanReversion.m``'s commented-out first load line reads VX's."""
        assert SOURCE_FILES == {
            "BR": "inputDataDaily_BR_20120813.mat",
            "C2": "inputDataDaily_C2_20120813.mat",
            "CL": "inputDataDaily_CL_20120813.mat",
            "HG": "inputDataDaily_HG_20120813.mat",
            "TU": "inputDataDaily_TU_20120813.mat",
            "VX": "inputDataDaily_VX_20120507.mat",
        }

    def test_vx_s_file_and_cl_s_2012_05_02_save_alone_are_read_without_a_spot(self) -> None:
        assert NO_SPOT_FILES == frozenset(
            {"inputDataDaily_VX_20120507.mat", "inputDataDaily_CL_20120502.mat"}
        )
        assert not NO_SPOT_FILES & {SOURCE_FILES[root] for root in ROOTS}

    def test_cl_s_2012_05_02_save_is_the_one_other_save(self) -> None:
        """``XLE_CL_rollReturn.m``'s second load line reads ``inputDataDaily_CL_20120502``."""
        assert OTHER_SAVES == {"CL": ("inputDataDaily_CL_20120502.mat",)}

    def test_the_book_table_is_the_recovered_text_of_location_2399(self) -> None:
        text = BOOK_NOTES.read_text(encoding="utf-8")
        exchanges = {"BR": "CME", "C2": "CBOT", "CL": "NYMEX", "HG": "CME", "TU": "CBOT"}
        for root, (alpha, gamma) in BOOK_TABLE_5_1.items():
            symbol = "C" if root == "C2" else root
            row = f"{symbol} ({exchanges[root]}) {alpha:.1f}% {gamma:.1f}%".replace("-", "−")
            assert row in text, row

    def test_tus_alpha_is_a_negative_zero(self) -> None:
        assert math.copysign(1, BOOK_TABLE_5_1["TU"][0]) == -1

    def test_the_ports_figures_are_what_its_comments_print(self) -> None:
        assert PORT_C2 == ("0.02805562210100287", "-0.12775650227459556")


class TestTheVintages:
    @pytest.mark.parametrize("root", ROOTS)
    def test_the_members_are_the_pinned_source(self, strips, root) -> None:
        strip = strips[root]
        vendor, basis, saved, folder, count = LIFTED_SOURCES[SOURCE_FILES[root]]
        assert {(m.vendor, m.price_basis, m.obtained) for m in strip.members} == {
            (vendor, basis, saved)
        }
        assert len(strip.members) == count
        assert {m.path.split("/")[0] for m in strip.members} == {folder}

    @pytest.mark.parametrize(
        ("root", "days", "contracts", "spot_days", "spot_first"),
        [
            ("BR", 4216, 321, 4199, "1995-11-01"),
            ("C2", 6492, 30, 6492, "1986-11-03"),
            ("CL", 6467, 89, 6466, "1986-11-03"),
            ("HG", 6473, 181, 6471, "1986-11-03"),
            ("TU", 5565, 93, 4267, "1995-08-10"),
        ],
    )
    def test_each_strip_holds_its_spot_and_contracts_on_the_files_every_day(
        self, strips, panels, root, days, contracts, spot_days, spot_first
    ) -> None:
        strip = strips[root]
        _, closes = panels[root]
        assert strip.root == root
        assert strip.contracts.index.equals(closes.index) and strip.spot.index.equals(closes.index)
        assert (len(strip.spot), strip.contracts.shape[1]) == (days, contracts)
        assert int(strip.spot.notna().sum()) == spot_days
        assert str(strip.spot.first_valid_index().date()) == spot_first
        assert strip.spot.name == f"{root}-SPOT"
        assert list(strip.contracts.columns) == [c for c in closes.columns if c != strip.spot.name]


class TestTheFigures:
    """Rows 1 to 12 of the pins issue 347 declared."""

    @pytest.mark.parametrize("root", ROOTS)
    def test_alpha_and_gamma_at_the_six_decimals_the_script_prints(self, results, root) -> None:
        result = results[root]
        assert (f"{result.alpha:.6f}", f"{result.mean_gamma:.6f}") == COMPUTED[root], SPEC

    def test_eight_of_table_5_1s_ten_cells_land_and_hg_and_tu_alpha_miss(self, results) -> None:
        missed = []
        for root in ROOTS:
            book_alpha, book_gamma = BOOK_TABLE_5_1[root]
            if not lands(results[root].alpha, book_alpha):
                missed.append((root, "alpha"))
            if not lands(results[root].mean_gamma, book_gamma):
                missed.append((root, "gamma"))
        assert missed == [("HG", "alpha"), ("TU", "alpha")], SPEC

    def test_hgs_alpha_rounds_to_5_1_not_the_printed_5_0(self, results) -> None:
        assert round(100 * results["HG"].alpha, 1) == 5.1, SPEC

    def test_tus_alpha_is_positive_where_the_book_prints_a_negative_zero(self, results) -> None:
        assert 0 < results["TU"].alpha < 0.00005, SPEC

    def test_cls_first_day_with_gamma_is_figure_5_5s_first_day(self, results) -> None:
        """Location 2399 plots CL's γ "over the period November 22, 2004, to August 13, 2012"."""
        defined = results["CL"].gamma.dropna().index
        assert (str(defined[0].date()), str(defined[-1].date())) == (
            "2004-11-22",
            "2012-08-13",
        ), SPEC

    def test_c_agrees_with_the_python_ports_printed_figures(self, results) -> None:
        """The two programs sum in different orders, so the tolerance is 1e-12."""
        c = results["C2"]
        assert c.alpha == pytest.approx(float(PORT_C2[0]), abs=1e-12), SPEC
        assert c.mean_gamma == pytest.approx(float(PORT_C2[1]), abs=1e-12), SPEC


class TestTheClaims:
    """Rows 13 and 14, with the criteria issue 347 fixed before the build, though after a
    scratch run had measured the figures they judge."""

    def test_br_c_and_tu_each_have_a_roll_return_at_least_twice_their_spot_return(
        self, results
    ) -> None:
        """Location 2399: "the magnitude of the roll returns is much larger than that of
        the spot returns". BR is the narrowest, at four times."""
        ratios = {r: abs(results[r].mean_gamma) / abs(results[r].alpha) for r in ROOTS}
        assert all(ratios[r] >= 2 for r in ("BR", "C2", "TU")), SPEC
        assert min(("BR", "C2", "TU"), key=ratios.__getitem__) == "BR", SPEC
        assert round(ratios["BR"], 2) == 4.02, SPEC

    def test_br_hg_and_tu_each_have_a_roll_return_bigger_than_their_spot_return(
        self, results
    ) -> None:
        """Location 2683, Chapter 6's explanation of their momentum."""
        assert all(
            abs(results[r].mean_gamma) > abs(results[r].alpha) for r in ("BR", "HG", "TU")
        ), SPEC

    def test_cl_is_the_one_strip_whose_roll_return_is_smaller(self, results) -> None:
        smaller = [r for r in ROOTS if abs(results[r].mean_gamma) <= abs(results[r].alpha)]
        assert smaller == ["CL"], SPEC


class TestTheRowsBeside:
    """The four rows beside the replication. None has a published figure."""

    @pytest.mark.parametrize("root", ROOTS)
    def test_gamma_with_maturity_in_months(self, results, root) -> None:
        assert f"{results[root].mean_gamma_in_months:.6f}" == COMPUTED_IN_MONTHS[root], SPEC

    @pytest.mark.parametrize("root", ["BR", "CL"])
    def test_monthly_strips_give_the_same_gamma_either_way(self, results, root) -> None:
        """The two fits differ only in where the regressor starts, so they agree to rounding."""
        result = results[root]
        np.testing.assert_allclose(
            result.gamma_in_months.to_numpy(),
            result.gamma.to_numpy(),
            rtol=0,
            atol=1e-13,
            err_msg=SPEC,
        )

    def test_the_script_overstates_c_by_2_4_hg_by_2_0_and_tu_by_3_0(self, results) -> None:
        overstated = {
            r: round(results[r].mean_gamma / results[r].mean_gamma_in_months, 1)
            for r in ("C2", "HG", "TU")
        }
        assert overstated == {"C2": 2.4, "HG": 2.0, "TU": 3.0}, SPEC

    def test_location_2683_fails_for_hg_on_the_month_spaced_gamma(self, results) -> None:
        holds = {
            r: abs(results[r].mean_gamma_in_months) > abs(results[r].alpha)
            for r in ("BR", "HG", "TU")
        }
        assert holds == {"BR": True, "HG": False, "TU": True}, SPEC

    def test_location_2399_fails_for_c_on_the_month_spaced_gamma(self, results) -> None:
        """Row 13's criterion, at least twice, on the month-spaced γ. C falls short at 1.89."""
        ratios = {
            r: abs(results[r].mean_gamma_in_months) / abs(results[r].alpha)
            for r in ("BR", "C2", "TU")
        }
        assert {r: ratio >= 2 for r, ratio in ratios.items()} == {
            "BR": True,
            "C2": False,
            "TU": True,
        }, SPEC
        assert round(ratios["C2"], 2) == 1.89, SPEC

    def test_the_spacings_each_strips_gamma_reads(self, strips) -> None:
        found = {root: dict(maturity_spacings(strips[root].contracts)) for root in ROOTS}
        assert found == {
            "BR": {(1, 1, 1, 1): 4210},
            "C2": {
                (2, 2, 2, 3): 613,
                (3, 2, 2, 2): 320,
                (3, 3, 2, 2): 216,
                (2, 2, 3, 3): 214,
                (2, 3, 3, 2): 207,
            },
            "CL": {(1, 1, 1, 1): 1941},
            "HG": {
                (2, 2, 2, 1): 1417,
                (1, 2, 3, 2): 1070,
                (3, 2, 2, 2): 1058,
                (2, 1, 2, 3): 972,
                (2, 2, 1, 2): 960,
                (2, 3, 2, 2): 551,
            },
            "TU": {(3, 3, 3, 3): 1087},
        }, SPEC

    @pytest.mark.parametrize(
        ("root", "days", "first", "last"),
        [
            ("BR", 4210, "1995-11-09", "2012-08-13"),
            ("C2", 1570, "2005-12-19", "2012-03-14"),
            ("CL", 1941, "2004-11-22", "2012-08-13"),
            ("HG", 6028, "1986-11-03", "2012-08-13"),
            ("TU", 1087, "2008-03-10", "2012-08-13"),
        ],
    )
    def test_the_days_with_gamma_and_their_span(self, results, root, days, first, last) -> None:
        defined = results[root].gamma.dropna().index
        assert (len(defined), str(defined[0].date()), str(defined[-1].date())) == (
            days,
            first,
            last,
        ), SPEC
        assert results[root].gamma_in_months.dropna().index.equals(defined), SPEC

    def test_cs_gamma_stops_when_its_strip_runs_out_of_contracts(self, strips) -> None:
        """The C2 strip's last contract is 2012Z, so after March 2012's expires no day
        prices five."""
        contracts = strips["C2"].contracts
        after = contracts.loc["2012-03-15":]
        assert contracts.columns[-1] == "C2-2012Z"
        assert int(after.notna().sum(axis=1).max()) == 4, SPEC


def _renumbered(spot: pd.Series) -> float:
    """α with the rows renumbered 1 to n after the spot's gaps are dropped."""
    priced = spot.dropna()
    rows = np.arange(1, len(priced) + 1, dtype=float)
    return 252 * np.polyfit(rows, np.log(priced.to_numpy()), 1)[0]


def _calendar_days(spot: pd.Series) -> float:
    """α regressed on calendar days since the strip's first day and annualized by 365."""
    priced = spot.dropna()
    days = (priced.index - spot.index[0]).days.to_numpy(dtype=float)
    return 365 * np.polyfit(days, np.log(priced.to_numpy()), 1)[0]


def _single_precision(spot: pd.Series) -> float:
    """α with the prices, the rows and the fit all at single precision."""
    values = spot.to_numpy(dtype=np.float32)
    rows = np.arange(1, len(values) + 1, dtype=np.float32)
    priced = np.isfinite(values)
    design = np.column_stack([rows[priced], np.ones(priced.sum(), dtype=np.float32)])
    return 252 * float(np.linalg.lstsq(design, np.log(values[priced]), rcond=None)[0][0])


class TestTheReadingsTriedAfterTheMiss:
    """Three readings of α, each tried after HG's and TU's cells missed.

    None changes the specification, as issue 347 asked in advance. The
    calendar-day reading lands HG's cell, which the issue's scratch run had
    reported it did not, and still misses TU's. It also moves C's α off the
    figure the Python port printed, which the row number lands within the 1e-12
    ``TestTheFigures`` pins, so the port is evidence that Chan's code ran the row
    number.
    """

    @pytest.mark.parametrize(
        ("reading", "hg", "tu_positive"),
        [
            (_renumbered, "0.050587", True),
            (_calendar_days, "0.050315", True),
            (_single_precision, "0.050567", True),
        ],
    )
    def test_each_reading_of_hg_and_tu(self, strips, reading, hg, tu_positive) -> None:
        assert f"{reading(strips['HG'].spot):.6f}" == hg, SPEC
        assert bool(reading(strips["TU"].spot) > 0) is tu_positive, SPEC

    def test_only_the_calendar_day_reading_lands_hgs_cell(self, strips) -> None:
        landing = [
            reading.__name__
            for reading in (_renumbered, _calendar_days, _single_precision)
            if lands(reading(strips["HG"].spot), BOOK_TABLE_5_1["HG"][0])
        ]
        assert landing == ["_calendar_days"], SPEC

    def test_the_calendar_day_reading_misses_the_ports_c_alpha(self, strips) -> None:
        assert f"{_calendar_days(strips['C2'].spot):.6f}" == "0.027998", SPEC
        assert abs(_calendar_days(strips["C2"].spot) - float(PORT_C2[0])) > 1e-5


class TestTheScaleBreakDecision:
    """The guard reads each member's own rows, and passing the panel columns is refused."""

    @pytest.mark.parametrize("root", ROOTS)
    def test_passing_a_panel_column_over_the_strips_span_is_refused(self, panels, root) -> None:
        """A contract's column is NaN before it lists and after it expires, so the guard
        reads a day with no move. Each strip's nearest contract is enough to show it, and
        the measurement on issue 347 found every strip refused this way."""
        members, closes = panels[root]
        nearest = next(entry for entry in members if entry.symbol == closes.columns[0])
        with pytest.raises(
            WindowCrossesScaleBreak,
            match=f"{nearest.symbol.lower()}.csv has no readable day-over-day move",
        ):
            refuse_window_crossing_a_break(
                [(nearest, closes[nearest.symbol])], start=closes.index[0], end=closes.index[-1]
            )

    @pytest.mark.parametrize("which", ["spot", "first contract", "last contract"])
    def test_a_member_planted_with_a_scale_break_is_refused(
        self, panels, monkeypatch, which
    ) -> None:
        members, closes = panels["CL"]
        symbol = {
            "spot": "CL-SPOT",
            "first contract": closes.columns[0],
            "last contract": closes.columns[-2],
        }[which]
        own = closes[symbol].dropna().index
        broken = closes.copy()
        broken.loc[own[len(own) // 2] :, symbol] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv changes scale"):
            load_strip("CL")

    def test_a_restart_gap_is_read_across_rather_than_refused(self, strips) -> None:
        """HG has 29 contracts that stop and restart, and the strip still loads, because
        the guard compares the settlements on either side of each gap."""
        strip = strips["HG"]
        columns = [strip.spot, *(strip.contracts[s] for s in strip.contracts.columns)]
        restarted = [column.name for column in columns if _holes(column)]
        assert len(restarted) == 29, SPEC


def _holes(column: pd.Series) -> bool:
    """Whether a column has a NaN between its first and last settlement."""
    held = np.flatnonzero(column.notna().to_numpy())
    return bool(len(held)) and held[-1] - held[0] + 1 != len(held)


class TestTheRun:
    def test_it_prints_each_figure_beside_table_5_1(
        self, strips, results, monkeypatch, capsys
    ) -> None:
        monkeypatch.setattr(module, "load_strip", lambda root, *_a, **_k: strips[root])
        monkeypatch.setattr(module, "strip_returns", lambda strip: results[strip.root])
        run()
        out = capsys.readouterr().out
        figures = [
            r.split() for r in out.splitlines() if r.split()[1:2] and r.split()[1][-1].isdigit()
        ]
        assert [r[0] for r in figures] == ["BR", "C", "CL", "HG", "TU"] * 2
        for label, root in (("BR", "BR"), ("C", "C2"), ("CL", "CL"), ("HG", "HG"), ("TU", "TU")):
            alpha, gamma = COMPUTED[root]
            book_alpha, book_gamma = BOOK_TABLE_5_1[root]
            rows = [
                r.split()
                for r in out.splitlines()
                if r.split()[:1] == [label] and r.split()[1][-1].isdigit()
            ]
            assert rows[0] == [label, alpha, f"{book_alpha:.1f}%", gamma, f"{book_gamma:.1f}%"]
            defined = results[root].gamma.dropna().index
            assert rows[1][:7] == [
                label,
                gamma,
                COMPUTED_IN_MONTHS[root],
                str(len(defined)),
                str(defined[0].date()),
                "to",
                str(defined[-1].date()),
            ]
        assert "inputdatadaily_hg_20120813/" in out
        assert "1-1-1-1 on 1941" in out
        assert "2012-08-13  2-2-2-1 on 1417, 1-2-3-2 on 1070," in out
        assert "Exploratory" in out

    def test_the_data_directory_reaches_every_read(self, panels, monkeypatch) -> None:
        asked = []

        def fake_load_panel(source, *, data_dir=None):
            asked.append(data_dir)
            return panels[next(r for r in ROOTS if SOURCE_FILES[r] == source)]

        monkeypatch.setattr(module, "load_panel", fake_load_panel)
        monkeypatch.setattr(module, "report", lambda results: None)
        run(data_dir=Path("elsewhere"))
        assert asked == [Path("elsewhere")] * len(ROOTS)


# --- the rule on synthetic frames ------------------------------------------------


DAYS = pd.bdate_range("2020-01-01", periods=4)
MONTHLY = [f"X-2020{letter}" for letter in "FGHJKMN"]
QUARTERLY = ["X-2020H", "X-2020M", "X-2020U", "X-2020Z", "X-2021H", "X-2021M"]


def _curve(gamma: float, maturities: np.ndarray, spot: float = 50.0) -> np.ndarray:
    """Prices on a forward curve with roll return ``gamma``, maturity in months."""
    return spot * np.exp(-gamma / 12 * maturities)


class TestTheRule:
    def test_a_planted_roll_return_is_recovered_on_monthly_contracts(self) -> None:
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        np.testing.assert_allclose(roll_returns(frame), 0.08, rtol=1e-12)
        np.testing.assert_allclose(roll_returns_in_months(frame), 0.08, rtol=1e-12)

    def test_quarterly_contracts_triple_the_column_gamma_and_not_the_month_gamma(self) -> None:
        prices = np.tile(_curve(0.03, np.arange(6.0) * 3), (4, 1))
        frame = pd.DataFrame(prices, index=DAYS, columns=QUARTERLY)
        np.testing.assert_allclose(roll_returns(frame), 0.09, rtol=1e-12)
        np.testing.assert_allclose(roll_returns_in_months(frame), 0.03, rtol=1e-12)

    def test_a_row_with_four_priced_contracts_has_no_gamma(self) -> None:
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        prices[1, 4:] = np.nan
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        assert np.isnan(roll_returns(frame).iloc[1])
        assert np.isnan(roll_returns_in_months(frame).iloc[1])
        assert np.isfinite(roll_returns(frame).drop(DAYS[1])).all()

    @pytest.mark.parametrize("skipped", [1, 3, 4])
    def test_a_row_whose_first_five_priced_columns_skip_one_has_no_gamma(self, skipped) -> None:
        """Column 4 puts the skip between the fourth and fifth priced contracts, the last
        gap the script checks."""
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        prices[2, skipped] = np.nan
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        assert np.isnan(roll_returns(frame).iloc[2])
        assert np.isnan(roll_returns_in_months(frame).iloc[2])

    def test_a_row_starting_on_a_later_column_still_fits(self) -> None:
        """The nearest five need only be adjacent to each other, not to the first column."""
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        prices[0, :2] = np.nan
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        assert roll_returns(frame).iloc[0] == pytest.approx(0.08, rel=1e-12)
        assert roll_returns_in_months(frame).iloc[0] == pytest.approx(0.08, rel=1e-12)

    def test_only_the_nearest_five_are_read_when_more_are_priced(self) -> None:
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        prices[:, 5:] *= 3.0
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        np.testing.assert_allclose(roll_returns(frame), 0.08, rtol=1e-12)
        np.testing.assert_allclose(roll_returns_in_months(frame), 0.08, rtol=1e-12)

    def test_the_nan_rows_stay_in_place(self) -> None:
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        prices[[0, 3], 2:] = np.nan
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY)
        for gamma in (roll_returns(frame), roll_returns_in_months(frame)):
            assert gamma.index.equals(DAYS)
            assert list(np.isnan(gamma.to_numpy())) == [True, False, False, True]

    def test_the_spot_return_keeps_each_rows_original_number_across_a_gap(self) -> None:
        rows = np.arange(1.0, 11.0)
        spot = pd.Series(20 * np.exp(0.001 * rows), index=pd.bdate_range("2020-01-01", periods=10))
        spot.iloc[3:6] = np.nan
        assert spot_return(spot) == pytest.approx(0.252, rel=1e-12)
        assert _renumbered(spot) != pytest.approx(0.252, rel=1e-6)

    def test_the_spot_return_fits_an_intercept(self) -> None:
        spot = pd.Series(np.exp(4.0 + 0.002 * np.arange(1.0, 6.0)))
        assert spot_return(spot) == pytest.approx(0.504, rel=1e-12)

    def test_the_spot_return_refuses_fewer_than_two_priced_days(self) -> None:
        with pytest.raises(ValueError, match="at least two priced days"):
            spot_return(pd.Series([np.nan, 3.0, np.nan]))

    def test_the_spot_return_fits_on_two_priced_days(self) -> None:
        spot = pd.Series([np.nan, 2.0, np.nan, 2.0 * np.exp(0.002)])
        assert spot_return(spot) == pytest.approx(0.252, rel=1e-12)

    @pytest.mark.parametrize("fit", [roll_returns, roll_returns_in_months])
    def test_contracts_out_of_delivery_order_are_refused(self, fit) -> None:
        """Both fits read the nearest contracts by column position, so a reordered frame
        would give a wrong γ without the refusal."""
        prices = np.tile(_curve(0.08, np.arange(7.0)), (4, 1))
        frame = pd.DataFrame(prices, index=DAYS, columns=MONTHLY).iloc[:, ::-1]
        with pytest.raises(ValueError, match="X-2020N before X-2020M"):
            fit(frame)

    def test_a_contracts_month_is_read_off_its_symbol(self) -> None:
        assert contract_month("TU-2008H") - contract_month("TU-2007Z") == 3
        assert contract_month("HG-1987F") - contract_month("HG-1986Z") == 1

    @pytest.mark.parametrize("symbol", ["CL-SPOT", "CL-SPOTZ", "CL-2008", "CL-2008A", "CL-08F"])
    def test_a_symbol_naming_no_contract_is_refused(self, symbol) -> None:
        with pytest.raises(ValueError, match="does not name a contract"):
            contract_month(symbol)

    def test_the_spacings_count_the_gaps_across_the_fitted_five(self) -> None:
        prices = np.tile(_curve(0.03, np.arange(6.0) * 3), (4, 1))
        prices[0, :] = np.nan
        prices[3, 0] = np.nan
        frame = pd.DataFrame(prices, index=DAYS, columns=QUARTERLY)
        assert dict(maturity_spacings(frame)) == {(3, 3, 3, 3): 3}


class TestTheVxStrip:
    """The VX strip through the same read path, which issue 349 widened to a strip with no spot."""

    def test_vx_loads_72_contracts_and_no_spot_after_the_guard_reads_each(
        self, monkeypatch
    ) -> None:
        guarded = []
        guard = module.refuse_window_crossing_a_break

        def record(legs, *, start, end):
            guarded.append(legs[0][0].symbol)
            return guard(legs, start=start, end=end)

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        strip = load_strip("VX")
        assert LIFTED_SOURCES[SOURCE_FILES["VX"]] == (
            "chan-mat",
            "raw",
            "2012-05-08",
            "inputdatadaily_vx_20120507",
            72,
        )
        assert (strip.root, strip.spot, len(strip.members)) == ("VX", None, 72)
        assert strip.contracts.shape == (1543, 72)
        columns = list(strip.contracts.columns)
        assert (columns[0], columns[-1]) == ("VX-2007F", "VX-2012Z")
        assert sorted(guarded) == sorted(columns)


class TestTheOtherSaves:
    """CL's 2012-05-02 save through the same read path, which issue 356 widened to it."""

    CL_20120502 = "inputDataDaily_CL_20120502.mat"

    def test_it_loads_89_contracts_and_no_spot_after_the_guard_reads_each(
        self, monkeypatch
    ) -> None:
        guarded = []
        guard = module.refuse_window_crossing_a_break

        def record(legs, *, start, end):
            guarded.append(legs[0][0].symbol)
            return guard(legs, start=start, end=end)

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        strip = load_strip("CL", source_file=self.CL_20120502)
        assert LIFTED_SOURCES[self.CL_20120502] == (
            "chan-mat",
            "raw",
            "2012-05-03",
            "inputdatadaily_cl_20120502",
            89,
        )
        assert {m.path.split("/")[0] for m in strip.members} == {"inputdatadaily_cl_20120502"}
        assert (strip.root, strip.spot, len(strip.members)) == ("CL", None, 89)
        assert strip.contracts.shape == (2867, 89)
        columns = list(strip.contracts.columns)
        assert (columns[0], columns[-1]) == ("CL-2007F", "CL-2014K")
        assert sorted(guarded) == sorted(columns)

    def test_naming_the_default_file_reads_what_leaving_it_out_reads(self, strips) -> None:
        named = load_strip("CL", source_file=SOURCE_FILES["CL"])
        assert named.contracts.equals(strips["CL"].contracts)
        assert named.spot.equals(strips["CL"].spot)

    def test_an_undeclared_no_spot_save_is_refused_by_its_own_name(self, monkeypatch) -> None:
        """The refusal names the save that was read, not the root's default file."""
        monkeypatch.setattr(module, "NO_SPOT_FILES", frozenset({SOURCE_FILES["VX"]}))
        with pytest.raises(
            VintageUnavailable, match="^inputDataDaily_CL_20120502.mat holds no CL-SPOT column$"
        ):
            load_strip("CL", source_file="inputDataDaily_CL_20120502.mat")

    @pytest.mark.parametrize(
        ("root", "source_file"),
        [
            ("CL", "inputDataDaily_CL_20120501.mat"),
            ("CL", "inputDataDaily_VX_20120507.mat"),
            ("VX", "inputDataDaily_CL_20120502.mat"),
        ],
    )
    def test_a_save_nobody_declared_for_the_root_is_refused(self, root, source_file) -> None:
        with pytest.raises(ValueError, match=f"and not {source_file}$"):
            load_strip(root, source_file=source_file)

    def test_cl_s_2012_08_13_save_without_its_spot_is_still_refused(
        self, panels, monkeypatch
    ) -> None:
        """The declaration names the 2012-05-02 file, so it does not reach CL's other save."""
        members, closes = panels["CL"]
        monkeypatch.setattr(
            module,
            "load_panel",
            lambda *_a, **_k: (
                [m for m in members if m.symbol != "CL-SPOT"],
                closes.drop(columns="CL-SPOT"),
            ),
        )
        with pytest.raises(
            VintageUnavailable, match="inputDataDaily_CL_20120813.mat holds no CL-SPOT column"
        ):
            load_strip("CL")

    def test_the_named_file_is_the_one_read(self, monkeypatch) -> None:
        seen = []
        real = module.load_panel

        def record(source_file, data_dir=None):
            seen.append(source_file)
            return real(source_file, data_dir=data_dir)

        monkeypatch.setattr(module, "load_panel", record)
        load_strip("CL", source_file=self.CL_20120502)
        assert seen == [self.CL_20120502]


class TestTheRefusals:
    @pytest.mark.parametrize("root", ["HO2", "C", "cl", "vx"])
    def test_any_other_root_is_refused_naming_the_six(self, root) -> None:
        with pytest.raises(
            ValueError, match=f"BR, C2, CL, HG and TU, and the VX strip, and not {root}$"
        ):
            load_strip(root)

    def test_a_member_with_no_priced_day_is_skipped_by_the_guard(self, panels, monkeypatch) -> None:
        """No committed member is empty, and an empty one has no move for the guard to read."""
        members, closes = panels["C2"]
        empty = closes.copy()
        empty[closes.columns[0]] = np.nan
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, empty))
        assert load_strip("C2").contracts[closes.columns[0]].isna().all()

    def test_a_strip_with_no_spot_column_is_refused(self, panels, monkeypatch) -> None:
        members, closes = panels["C2"]
        monkeypatch.setattr(
            module,
            "load_panel",
            lambda *_a, **_k: (
                [m for m in members if m.symbol != "C2-SPOT"],
                closes.drop(columns="C2-SPOT"),
            ),
        )
        with pytest.raises(VintageUnavailable, match="holds no C2-SPOT column"):
            load_strip("C2")

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "load_strip", fail)
        monkeypatch.setattr("sys.argv", ["roll_returns"])
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataDaily_BR_20120813"),
            WindowCrossesScaleBreak("inputdatadaily_tu_20120813/tu-spot.csv changes scale"),
        ],
    )
    def test_main_prints_a_refusal_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(module, "load_strip", refuse)
        monkeypatch.setattr("sys.argv", ["roll_returns"])
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
