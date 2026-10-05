"""The pins for GLD, GDX and USO around July 2008, *Algorithmic Trading*'s location 1922.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it. ``docs/replication-log.md``
Entry 24 carries the verdicts and points here row by row.

Every pin on the committed file reads one vintage and one specification, so
both are stated once here.

- **Vintage.** ``inputdata_etf/gld.csv``, ``gdx.csv`` and ``uso.csv``, lifted
  from Chan's ``inputData_ETF.mat``, chan-mat, adjusted by subtracting each
  dividend in dollars, saved 2012-04-10, read for the close through
  ``chan.series.load_panel`` and cut to GDX's first price. That leaves 1,481
  trading days from 2006-05-23 to 2012-04-09. Its identity is that file's row
  of ``LIFTED_SOURCES`` in ``tests/support/committed_vintages.py``.
- **Specification.** Declared on issue 344 before any statistic was computed,
  since no script ships for this example. ``johansen(·, 0, 1)``, a constant
  and one lagged difference, on columns GLD, GDX and then USO. Windows
  2006-05-23 to 2008-07-14 and 2008-07-15 to 2012-04-09 for the pair, and the
  whole span for the triplet and the control. Each claim is judged at 99
  percent on the trace and eigen statistics separately. ``cadf(GLD, GDX, 0,
  1)`` is ``lesage_cadf`` with one lag, and each ADF has a constant and one
  lag.

The Johansen statistics are pinned at six decimals and the eigenvalues at
eight, the precision Entry 23's pins on the same wrapper use.

Exploratory. The split date and the third ETF were both chosen after the break
was seen. Every test here first ran on 2026-10-05.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2

from chan import gold_miners_oil as module
from chan import paths
from chan.gold_miners_oil import (
    AFTER,
    BEFORE,
    CLAIM_ROWS,
    JOHANSEN_K,
    JOHANSEN_P,
    LEVEL,
    PAIR,
    SOURCE_FILE,
    TRIPLET,
    WHOLE,
    GoldMinersOil,
    gold_miners_oil,
    main,
    read_sources,
    run,
)
from chan.johansen import johansen
from chan.series import WindowCrossesScaleBreak, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> GoldMinersOil:
    return gold_miners_oil(sources[1])


@pytest.fixture
def no_arguments(monkeypatch):
    """``main`` parses ``sys.argv``, which under pytest holds pytest's own arguments."""
    monkeypatch.setattr("sys.argv", ["chan.gold_miners_oil"])


def _row(n: int):
    return next(row for row in CLAIM_ROWS if row.row == n)


class TestTheSpecification:
    def test_the_declared_test_and_level(self) -> None:
        assert (JOHANSEN_P, JOHANSEN_K, LEVEL) == (0, 1, 99)

    def test_the_columns_are_the_books_order(self) -> None:
        assert PAIR == ("GLD", "GDX")
        assert TRIPLET == ("GLD", "GDX", "USO")

    def test_the_windows_are_location_1922s(self) -> None:
        assert BEFORE == ("2006-05-23", "2008-07-14")
        assert AFTER == ("2008-07-15", "2012-04-09")
        assert WHOLE == (BEFORE[0], AFTER[1])

    def test_the_six_criteria_are_the_ones_issue_344_declared(self) -> None:
        assert [(r.row, r.test, r.statistic, r.criterion) for r in CLAIM_ROWS] == [
            (1, "before", "trace", ">= 1"),
            (2, "before", "eigen", ">= 1"),
            (3, "after", "trace", "== 0"),
            (4, "after", "eigen", "== 0"),
            (5, "triplet", "trace", "== 1"),
            (6, "triplet", "eigen", "== 1"),
        ]

    @pytest.mark.parametrize(
        ("n", "holding"),
        [(1, {1, 2}), (2, {1, 2}), (3, {0}), (4, {0}), (5, {1}), (6, {1})],
    )
    def test_each_criterion_holds_on_exactly_the_declared_counts(self, n, holding) -> None:
        """Rows 1 and 2 hold on a full rank too. Rows 5 and 6 claim exactly one.

        A pair can find 0 to 2 relations and the triplet 0 to 3.
        """
        possible = range(3) if n <= 4 else range(4)
        assert {count for count in possible if _row(n).holds_on(count)} == holding


class TestTheVintage:
    def test_the_three_members_are_the_pinned_source(self, sources) -> None:
        members, closes = sources
        vendor, basis, saved, folder, _ = LIFTED_SOURCES[SOURCE_FILE]
        assert {(m.vendor, m.price_basis, m.obtained) for m in members} == {(vendor, basis, saved)}
        assert sorted(m.path for m in members) == [
            f"{folder}/gdx.csv",
            f"{folder}/gld.csv",
            f"{folder}/uso.csv",
        ]
        assert list(closes.columns) == ["GLD", "GDX", "USO"]

    def test_the_span_is_gdxs_1481_days_with_no_price_missing(self, sources) -> None:
        closes = sources[1]
        assert len(closes) == 1481
        assert str(closes.index[0].date()) == "2006-05-23"
        assert str(closes.index[-1].date()) == "2012-04-09"
        assert np.isfinite(closes.to_numpy()).all()

    def test_the_windows_hold_539_and_942_days_and_split_the_span(self, result) -> None:
        before, after, whole = (result.days[name] for name in ("before", "after", "whole"))
        assert (len(before), len(after), len(whole)) == (539, 942, 1481)
        assert [str(d.date()) for d in (before[0], before[-1], after[0], after[-1])] == [
            "2006-05-23",
            "2008-07-14",
            "2008-07-15",
            "2012-04-09",
        ]
        assert before.append(after).equals(whole)

    def test_the_lowest_closes_are_far_from_zero(self, sources) -> None:
        """A subtracted dividend can take a close below zero. These three stay well above."""
        assert sources[1].min().round(2).to_dict() == {"GLD": 55.62, "GDX": 15.71, "USO": 22.86}


class TestTheClaims:
    """Rows 1 to 6, each a count of relations at 99 percent on one statistic."""

    @pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
    def test_every_claim_holds(self, result, n) -> None:
        assert result.holds(_row(n))

    def test_rows_1_and_2_the_pair_holds_one_relation_before(self, result) -> None:
        """One relation, not a full rank, so the second conclusion's reading does not arise."""
        assert result.found(_row(1)) == 1
        assert result.found(_row(2)) == 1

    def test_rows_3_and_4_the_pair_holds_none_after_even_at_90(self, result) -> None:
        """The loss holds at every level, so the stronger reading of "lost" holds too."""
        for statistic in ("trace", "eigen"):
            assert [result.after.relations(statistic, level) for level in (90, 95, 99)] == [0, 0, 0]

    def test_rows_5_and_6_the_triplet_holds_one_at_every_level(self, result) -> None:
        for statistic in ("trace", "eigen"):
            assert [result.triplet.relations(statistic, level) for level in (90, 95, 99)] == [
                1,
                1,
                1,
            ]

    def test_the_counts_at_90_and_95_agree_with_99_on_every_claim(self, result) -> None:
        for row in CLAIM_ROWS:
            assert {result.found(row, level) for level in (90, 95, 99)} == {result.found(row)}

    def test_a_miss_would_be_reported_as_one(self) -> None:
        """A row's verdict reads its criterion, so a count outside it does not reproduce."""
        assert not _row(3).holds_on(1)
        assert not _row(5).holds_on(2)
        assert not _row(1).holds_on(0)


class TestEachTestsTable:
    """Rows 7 to 10: every statistic and eigenvalue, pinned so nothing moves inside a claim."""

    def test_row_7_the_pair_before(self, result) -> None:
        np.testing.assert_allclose(result.before.trace, [22.571096, 0.147414], atol=1e-6)
        np.testing.assert_allclose(result.before.eigen, [22.423682, 0.147414], atol=1e-6)
        np.testing.assert_allclose(result.before.eigenvalues, [0.04089749, 0.00027448], atol=1e-8)

    def test_row_8_the_pair_after(self, result) -> None:
        np.testing.assert_allclose(result.after.trace, [6.132867, 0.073701], atol=1e-6)
        np.testing.assert_allclose(result.after.eigen, [6.059166, 0.073701], atol=1e-6)
        np.testing.assert_allclose(result.after.eigenvalues, [0.00642519, 0.00007840], atol=1e-8)

    def test_row_9_the_triplet(self, result) -> None:
        np.testing.assert_allclose(result.triplet.trace, [44.837732, 7.004501, 0.164176], atol=1e-6)
        np.testing.assert_allclose(result.triplet.eigen, [37.833231, 6.840326, 0.164176], atol=1e-6)
        np.testing.assert_allclose(
            result.triplet.eigenvalues, [0.02525587, 0.00461429, 0.00011100], atol=1e-8
        )

    def test_row_10_the_control_the_pair_alone_over_the_triplets_days(self, result) -> None:
        np.testing.assert_allclose(result.control.trace, [10.446773, 0.044664], atol=1e-6)
        np.testing.assert_allclose(result.control.eigen, [10.402109, 0.044664], atol=1e-6)
        np.testing.assert_allclose(result.control.eigenvalues, [0.00700853, 0.00003020], atol=1e-8)

    def test_row_10_the_control_finds_no_relation_even_at_90(self, result) -> None:
        """So the triplet's relation is not one the pair already held over the same days."""
        for statistic in ("trace", "eigen"):
            assert [result.control.relations(statistic, level) for level in (90, 95, 99)] == [
                0,
                0,
                0,
            ]

    def test_the_control_reads_the_triplets_days(self, sources, result) -> None:
        closes = sources[1]
        alone = johansen(closes[list(PAIR)].to_numpy(dtype=float), JOHANSEN_P, JOHANSEN_K)
        np.testing.assert_allclose(alone.trace, result.control.trace, atol=1e-12)

    def test_the_critical_values_are_lesages_at_90_95_and_99(self, result) -> None:
        """The same tables Entry 23 checks against Chan's printout, as the script formats them."""
        two = [["13.429", "15.494", "19.935"], ["2.705", "3.841", "6.635"]]
        two_eigen = [["12.297", "14.264", "18.520"], ["2.705", "3.841", "6.635"]]
        three = [["27.067", "29.796", "35.463"], *two]
        three_eigen = [["18.893", "21.131", "25.865"], *two_eigen]
        for test, trace, eigen in (
            (result.before, two, two_eigen),
            (result.after, two, two_eigen),
            (result.control, two, two_eigen),
            (result.triplet, three, three_eigen),
        ):
            assert [[f"{v:.3f}" for v in row] for row in test.trace_critical] == trace
            assert [[f"{v:.3f}" for v in row] for row in test.eigen_critical] == eigen

    def test_the_closest_call_is_row_1_clearing_its_bar_by_2_636(self, result) -> None:
        """Each null a claim turns on, against its 99 percent bar. Row 1 is the nearest."""
        margins = {
            "row 1": result.before.trace[0] - result.before.trace_critical[0, 2],
            "row 2": result.before.eigen[0] - result.before.eigen_critical[0, 2],
            "row 3": result.after.trace_critical[0, 2] - result.after.trace[0],
            "row 4": result.after.eigen_critical[0, 2] - result.after.eigen[0],
            "row 5, r <= 0": result.triplet.trace[0] - result.triplet.trace_critical[0, 2],
            "row 5, r <= 1": result.triplet.trace_critical[1, 2] - result.triplet.trace[1],
            "row 6, r <= 0": result.triplet.eigen[0] - result.triplet.eigen_critical[0, 2],
            "row 6, r <= 1": result.triplet.eigen_critical[1, 2] - result.triplet.eigen[1],
        }
        assert margins == pytest.approx(
            {
                "row 1": 2.636196,
                "row 2": 3.903682,
                "row 3": 13.802033,
                "row 4": 12.460834,
                "row 5, r <= 0": 9.374932,
                "row 5, r <= 1": 12.930399,
                "row 6, r <= 0": 11.968231,
                "row 6, r <= 1": 11.679674,
            },
            abs=1e-6,
        )
        assert min(margins, key=margins.get) == "row 1"


class TestBesideTheReplication:
    """Rows 11 to 13. No book prints these, so none carries a verdict."""

    def test_row_11_the_triplets_first_eigenvector(self, result) -> None:
        """Rows GLD, GDX, USO, with statsmodels' sign, which makes the first row positive."""
        np.testing.assert_allclose(
            result.triplet.eigenvectors[:, 0], [0.033109, -0.177036, 0.002549], atol=1e-6
        )

    def test_row_12_the_cadf_sees_the_same_break(self, result) -> None:
        """GLD on GDX rejects at 95 percent before the break and nowhere near it after."""
        t = {name: result.cadf[name].t for name in ("before", "after", "whole")}
        assert t == pytest.approx(
            {"before": -3.724034, "after": -1.511680, "whole": -1.517588}, abs=1e-6
        )
        assert EG_CRIT_N2["1%"] < t["before"] < EG_CRIT_N2["5%"]
        assert t["after"] > EG_CRIT_N2["10%"] and t["whole"] > EG_CRIT_N2["10%"]
        assert [result.cadf[n].nobs for n in ("before", "after", "whole")] == [537, 940, 1479]

    def test_row_13_no_series_alone_rejects_a_unit_root_even_at_90(self, result) -> None:
        assert result.adf == {
            "before": pytest.approx({"GLD": -0.033875, "GDX": -1.962727}, abs=1e-6),
            "after": pytest.approx({"GLD": -0.575590, "GDX": -1.720225}, abs=1e-6),
            "whole": pytest.approx(
                {"GLD": -0.370352, "GDX": -2.371217, "USO": -1.213340}, abs=1e-6
            ),
        }
        assert all(
            t > ADF_CRIT_CONST["10%"] for stats in result.adf.values() for t in stats.values()
        )

    def test_the_cadf_regresses_gld_on_gdx(self, sources, result) -> None:
        """Entry 1's direction. The other way round gives a different statistic."""
        before = sources[1].loc[BEFORE[0] : BEFORE[1]]
        swapped = module.lesage_cadf(
            before["GDX"].to_numpy(dtype=float), before["GLD"].to_numpy(dtype=float), 1
        )
        assert swapped[0] != pytest.approx(result.cadf["before"].t, abs=1e-3)


class TestTheCut:
    def test_a_column_starting_late_cuts_the_frame_to_its_first_price(
        self, sources, monkeypatch
    ) -> None:
        """Rather than a missing price reaching the Johansen test's refusal."""
        members, _ = sources
        days = pd.bdate_range("2020-01-01", periods=60)
        walk = 50.0 + np.cumsum(np.random.default_rng(0).normal(0, 0.2, size=(60, 3)), axis=0)
        frame = pd.DataFrame(walk, index=days, columns=list(TRIPLET))
        frame.iloc[:7, 1] = np.nan
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, frame))
        _, cut = read_sources()
        assert cut.index[0] == days[7]
        assert len(cut) == 53
        assert np.isfinite(cut.to_numpy()).all()

    def test_the_cut_is_what_keeps_the_wrapper_from_refusing(self) -> None:
        """Uncut, the file's first 19 rows hold no GDX price, and the wrapper names it."""
        _, closes = module.load_panel(SOURCE_FILE)
        uncut = closes[list(TRIPLET)]
        assert int(uncut["GDX"].isna().sum()) == 19
        with pytest.raises(ValueError, match="column 1 is nan on row 0"):
            johansen(uncut.to_numpy(dtype=float))


class TestTheScaleBreakDecision:
    def test_no_leg_carries_a_flagged_day(self, sources) -> None:
        """``tests/test_scale_breaks.py`` pins 58 days in eight other ETFs of this file."""
        _, closes = sources
        for symbol in TRIPLET:
            assert scale_breaks(closes[symbol]) == []

    @pytest.mark.parametrize("symbol", list(TRIPLET))
    @pytest.mark.parametrize("row", [1, 740, 1480])
    def test_any_leg_changing_scale_anywhere_in_the_span_is_refused(
        self, sources, monkeypatch, symbol, row
    ) -> None:
        """The guard reads all three over every day of the cut span, its last included."""
        members, closes = sources
        broken = closes.copy()
        broken.loc[broken.index[row:], symbol] *= 10
        monkeypatch.setattr(module, "load_panel", lambda *_a, **_k: (members, broken))
        with pytest.raises(WindowCrossesScaleBreak, match=f"{symbol.lower()}.csv"):
            read_sources()

    def test_the_guard_reads_the_three_over_the_cut_span(self, monkeypatch) -> None:
        seen = []

        def record(legs, *, start, end):
            seen.append(([entry.symbol for entry, _ in legs], start, end))

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", record)
        read_sources()
        assert len(seen) == 1
        symbols, start, end = seen[0]
        assert sorted(symbols) == ["GDX", "GLD", "USO"]
        assert (start, end) == (pd.Timestamp("2006-05-23"), pd.Timestamp("2012-04-09"))


class TestTheRun:
    def test_a_refusal_from_the_guard_reaches_the_caller(self, monkeypatch) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("flagged")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="flagged"):
            run()

    def test_main_turns_a_guard_refusal_into_one_line(self, monkeypatch, no_arguments):
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputdata_etf/gdx.csv changes scale on 2008-01-02")

        monkeypatch.setattr(module, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(SystemExit, match="gdx.csv changes scale on 2008-01-02"):
            main()

    def test_run_reads_the_directory_it_is_given(self, tmp_path) -> None:
        with pytest.raises(VintageUnavailable, match="inputData_ETF.mat"):
            run(tmp_path)

    def test_main_turns_a_missing_vintage_into_one_line(
        self, monkeypatch, tmp_path, no_arguments
    ) -> None:
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit, match="inputData_ETF.mat"):
            main()

    def test_the_report_prints_each_verdict_and_count(self, capsys, no_arguments) -> None:
        main()
        out = capsys.readouterr().out
        verdicts = [line for line in out.splitlines() if line[:4].strip().isdigit()]
        assert len(verdicts) == 6
        assert all(line.endswith("reproduced") for line in verdicts)
        assert "did not reproduce" not in out
        assert "control  trace  0 at 90%, 0 at 95%, 0 at 99%" in out
        assert "2006-05-23 to 2012-04-09, 1481 trading days" in out
        assert "Exploratory." in out

    def test_the_report_says_a_criterion_that_fails(
        self, sources, monkeypatch, capsys, no_arguments
    ) -> None:
        """Swapping the windows makes rows 1 to 4 fail, which the report must say."""
        monkeypatch.setattr(module, "WINDOWS", {"before": AFTER, "after": BEFORE, "whole": WHOLE})
        main()
        out = capsys.readouterr().out
        verdicts = [line for line in out.splitlines() if line[:4].strip().isdigit()]
        assert [line.endswith("did not reproduce") for line in verdicts] == [True] * 4 + [False] * 2
