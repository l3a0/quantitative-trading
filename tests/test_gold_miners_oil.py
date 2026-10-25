"""The pins for GLD, GDX and USO around July 2008, *Algorithmic Trading*'s location 1922.

This file is the single authority for every number a prose surface quotes
about this example and the rows beside it, with one exception, in
``blog/gold-miners-oil-lessons.md``. The post's figure has its own pins in
``tests/test_gold_miners_oil_figures.py``. ``TestThePostQuotesTheRun`` reads
at least one copy in the post of each figure the post takes from the run, the
chart or the earlier post's regime map, and README lists what the post says
that nothing pins. ``docs/replication-log.md`` Entry 29 carries the verdicts
and points here row by row.

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
  lag. The weight test of row 15 is Johansen's (1991) likelihood-ratio test
  of β = Hφ on the triplet's rank-1 relation over the whole span, built from
  the product moments of ``johansen(·, 0, 1)``, a constant entering
  unrestricted, with T = 1,479, and read against chi-squared with one degree
  of freedom.

The Johansen statistics are pinned at six decimals and the eigenvalues at
eight, the precision Entry 23's pins on the same wrapper use.

Exploratory. The split date and the third ETF were both chosen after the break
was seen. Every test here first ran on 2026-10-05. The post's pre-publish
review added three things after that, and each first ran on 2026-10-25.

1. Row 15's tests, added after every other result had been seen.
2. ``TestThePostQuotesTheRun``, which reads the post rather than the data.
3. The assertions in ``TestTheCut`` that GLD and USO start on 2006-04-26
   with no price missing.
"""

from __future__ import annotations

import dataclasses
import re

import numpy as np
import pandas as pd
import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2
from scipy import optimize
from scipy.stats import chi2

from chan import gold_miners_oil as module
from chan import paths
from chan.gold_miners_oil import (
    AFTER,
    BEFORE,
    BOOK_AFTER,
    BOOK_BEFORE,
    BOOK_TRIPLET,
    CHI2_1,
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
    johansen_moments,
    main,
    read_sources,
    restricted_eigenvalues,
    restricted_lr,
    run,
)
from chan.gold_miners_oil_figures import first_window_portfolio, signed
from chan.johansen import Johansen, johansen
from chan.regime_figure import make_regime_figure
from chan.series import WindowCrossesScaleBreak, scale_breaks
from chan.vintage import VintageUnavailable
from tests.support.committed_vintages import LIFTED_SOURCES

BOOK_NOTES = paths.REPO_ROOT / "research" / "book-notes" / "algorithmic-trading.md"
POST = paths.REPO_ROOT / "blog" / "gold-miners-oil-lessons.md"


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources) -> GoldMinersOil:
    return gold_miners_oil(sources[1])


@pytest.fixture(scope="module")
def triplet(sources):
    return sources[1][list(TRIPLET)].to_numpy(dtype=float)


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


class TestTheBooksClaims:
    @pytest.mark.parametrize("quoted", [BOOK_BEFORE, BOOK_AFTER, BOOK_TRIPLET])
    def test_each_quote_is_location_1922s_highlight_verbatim(self, quoted) -> None:
        notes = BOOK_NOTES.read_text(encoding="utf-8")
        start = notes.index("### Location 1922")
        highlight = notes[start : notes.index("### Location", start + 1)]
        assert quoted in highlight


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
        """One relation, not a full rank, so the reading Entry 23's second conclusion weighs
        does not arise here."""
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

    def test_a_row_is_judged_at_99_and_counted_at_the_level_asked(self, result) -> None:
        """On the file the counts agree at every level, so a stub makes them differ.

        A first null of 17 clears its 90 and 95 percent bars and misses 99, so
        row 3 holds on its 99 percent count of 0 and would fail on the others.
        """
        bars = np.array([[13.4294, 15.4943, 19.9349], [2.7055, 3.8415, 6.6349]])
        stub = Johansen(
            trace=np.array([17.0, 0.1]),
            trace_critical=bars,
            eigen=np.array([17.0, 0.1]),
            eigen_critical=bars,
            eigenvalues=np.array([0.01, 0.0001]),
            eigenvectors=np.eye(2),
        )
        moved = dataclasses.replace(result, after=stub)
        assert [moved.found(_row(3), level) for level in (90, 95, 99)] == [1, 1, 0]
        assert moved.found(_row(3)) == 0
        assert moved.holds(_row(3))

    def test_the_report_prints_the_99_count_and_each_statistics_own_counts(
        self, sources, result, capsys
    ) -> None:
        """On the file trace and eigen counts agree, so a stub makes them differ."""
        bars = np.array([[13.4294, 15.4943, 19.9349], [2.7055, 3.8415, 6.6349]])
        eigen_bars = np.array([[12.2971, 14.2639, 18.52], [2.7055, 3.8415, 6.6349]])
        stub = Johansen(
            trace=np.array([17.0, 0.1]),
            trace_critical=bars,
            eigen=np.array([1.0, 0.1]),
            eigen_critical=eigen_bars,
            eigenvalues=np.array([0.01, 0.0001]),
            eigenvectors=np.eye(2),
        )
        module.report(sources[0], dataclasses.replace(result, after=stub))
        lines = [line.strip() for line in capsys.readouterr().out.splitlines()]
        assert "after    trace  1 at 90%, 1 at 95%, 0 at 99%" in lines
        assert "after    eigen  0 at 90%, 0 at 95%, 0 at 99%" in lines
        row_3 = next(line for line in lines if line.startswith("3  "))
        assert row_3.split()[-2:] == ["0", "reproduced"]

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
    """Rows 11 to 14. No book prints these, so none carries a verdict."""

    def test_row_11_the_triplets_first_eigenvector(self, result) -> None:
        """Rows GLD, GDX, USO, with statsmodels' sign, which makes the first row positive."""
        np.testing.assert_allclose(
            result.triplet.eigenvectors[:, 0], [0.033109, -0.177036, 0.002549], atol=1e-6
        )

    def test_row_12_the_cadf_rejects_at_95_before_and_not_at_99(self, result) -> None:
        """GLD on GDX rejects at 95 percent before the break and nowhere near it after.

        At the 99 percent level the claims are judged at, it rejects in neither window.
        """
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

    def test_row_14_gdx_and_uso_alone_hold_a_relation_and_gld_and_uso_do_not(self, result):
        """Added after review, to ask whether the triplet's one relation is GDX and USO's own.

        Row 15 answers it on the triplet's weights. GLD's weight being zero is
        rejected against the asymptotic 99 percent bar, which the post reads
        at 95 percent, so the relation is not the pair's alone.
        """
        gld, gdx = result.with_oil["GLD"], result.with_oil["GDX"]
        np.testing.assert_allclose(gld.trace, [4.349962, 0.573598], atol=1e-6)
        np.testing.assert_allclose(gld.eigen, [3.776364, 0.573598], atol=1e-6)
        np.testing.assert_allclose(gld.eigenvalues, [0.00255007, 0.00038775], atol=1e-8)
        np.testing.assert_allclose(gdx.trace, [27.165550, 3.034162], atol=1e-6)
        np.testing.assert_allclose(gdx.eigen, [24.131388, 3.034162], atol=1e-6)
        np.testing.assert_allclose(gdx.eigenvalues, [0.01618363, 0.00204939], atol=1e-8)
        for statistic in ("trace", "eigen"):
            assert [gld.relations(statistic, level) for level in (90, 95, 99)] == [0, 0, 0]
            assert [gdx.relations(statistic, level) for level in (90, 95, 99)] == [2, 1, 1]

    def test_row_14_reads_the_triplets_days_with_uso_second(self, sources, result) -> None:
        closes = sources[1]
        for symbol in ("GLD", "GDX"):
            alone = johansen(closes[[symbol, "USO"]].to_numpy(dtype=float))
            np.testing.assert_allclose(alone.trace, result.with_oil[symbol].trace, atol=1e-12)
            np.testing.assert_allclose(
                alone.eigenvectors, result.with_oil[symbol].eigenvectors, atol=1e-12
            )

    def test_the_cadf_regresses_gld_on_gdx(self, sources, result) -> None:
        """Entry 1's direction. The other way round gives a different statistic."""
        before = sources[1].loc[BEFORE[0] : BEFORE[1]]
        swapped = module.lesage_cadf(
            before["GDX"].to_numpy(dtype=float), before["GLD"].to_numpy(dtype=float), 1
        )
        assert swapped[0] != pytest.approx(result.cadf["before"].t, abs=1e-3)


class TestTheWeightTest:
    """Row 15. Each fund's weight set to zero in the triplet's one relation.

    Added in the post's pre-publish review after every other result had been
    seen, so exploratory, conditional on rank 1, asymptotic, and one of three
    tests run together. The statistics are pinned at six decimals, as the
    Johansen statistics they are built beside.
    """

    def test_the_bars_are_chi_squared_with_one_degree_of_freedom(self) -> None:
        assert CHI2_1 == pytest.approx({90: 2.705543, 95: 3.841459, 99: 6.634897}, abs=1e-6)
        assert [f"{CHI2_1[level]:.3f}" for level in (90, 95, 99)] == ["2.706", "3.841", "6.635"]

    def test_the_moments_give_statsmodels_eigenvalues(self, sources, result, triplet) -> None:
        """So the restricted test is built on the model the unrestricted one ran."""
        moments = johansen_moments(triplet)
        assert moments.nobs == 1479
        np.testing.assert_allclose(
            restricted_eigenvalues(moments, np.eye(3)), result.triplet.eigenvalues, atol=1e-12
        )
        for symbol in PAIR:
            pair = sources[1][[symbol, "USO"]].to_numpy(dtype=float)
            np.testing.assert_allclose(
                restricted_eigenvalues(johansen_moments(pair), np.eye(2)),
                result.with_oil[symbol].eigenvalues,
                atol=1e-12,
            )

    def test_row_15_gld_and_gdx_cannot_be_left_out_and_uso_can(self, result) -> None:
        """GLD at zero is rejected at 99 percent, GDX far past it, USO not even at 90."""
        lr = result.zero_weight
        assert list(lr) == ["GLD", "GDX", "USO"]
        assert lr == pytest.approx({"GLD": 10.014660, "GDX": 26.336768, "USO": 0.056678}, abs=1e-6)
        assert lr["GLD"] > CHI2_1[99] and lr["GDX"] > CHI2_1[99]
        assert lr["USO"] < CHI2_1[90]
        assert chi2.sf(lr["GLD"], 1) == pytest.approx(0.00155, abs=5e-6)
        assert chi2.sf(lr["USO"], 1) == pytest.approx(0.812, abs=5e-4)

    def test_row_15_by_maximising_the_likelihood_directly(self, result, triplet) -> None:
        """An independent route to the GLD statistic, with its own moments.

        At rank 1 the concentrated log-likelihood is −T/2 times
        ``ln|S00 − S01 b (b'S11 b)⁻¹ b'S10|``, so the statistic is T times the
        gap between that log-determinant's minimum with GLD's weight at zero
        and its minimum with every weight free. The moments here demean and
        project with a pseudo-inverse, as ``coint_johansen`` does, and the free
        minimum is checked against statsmodels' own largest eigenvalue.
        """
        dx = np.diff(triplet, axis=0)
        lags = dx[:-1] - dx[:-1].mean(axis=0)

        def residual(values):
            values = values - values.mean(axis=0)
            return values - lags @ (np.linalg.pinv(lags) @ values)

        r0, r1 = residual(dx[1:]), residual(triplet[1:-1])
        t = len(r0)
        s00, s01, s11 = r0.T @ r0 / t, r0.T @ r1 / t, r1.T @ r1 / t

        def log_det(b):
            b = np.asarray(b, dtype=float)[:, None]
            kept = s01 @ b @ b.T @ s01.T / (b.T @ s11 @ b).item()
            return np.linalg.slogdet(s00 - kept)[1]

        held = optimize.minimize_scalar(lambda x: log_det([0.0, 1.0, x]), tol=1e-12)
        free = optimize.minimize(
            lambda v: log_det([v[0], 1.0, v[1]]),
            [0.0, 0.0],
            method="Nelder-Mead",
            options={"xatol": 1e-12, "fatol": 1e-15, "maxiter": 20000},
        )
        floor = np.linalg.slogdet(s00)[1] + np.log(1 - result.triplet.eigenvalues[0])
        assert free.fun == pytest.approx(floor, abs=1e-12)
        assert t * (held.fun - free.fun) == pytest.approx(result.zero_weight["GLD"], abs=1e-6)

    def test_a_restriction_that_holds_exactly_costs_nothing(self, result, triplet) -> None:
        """A span holding the unrestricted relation leaves the largest eigenvalue where it was."""
        relation = result.triplet.eigenvectors[:, 0]
        h = np.column_stack([relation, [1.0, 0.0, 0.0]])
        assert restricted_lr(johansen_moments(triplet), h) == pytest.approx(0.0, abs=1e-9)

    def test_the_report_prints_each_statistic_and_its_bars(self, capsys, no_arguments) -> None:
        main()
        lines = [line.strip() for line in capsys.readouterr().out.splitlines()]
        for expected in (
            "against chi-squared with 1 degree of freedom, "
            "2.706 at 90%, 3.841 at 95%, 6.635 at 99%",
            "GLD = 0  LR 10.014660, asymptotic p 0.00155",
            "GDX = 0  LR 26.336768, asymptotic p 2.87e-07",
            "USO = 0  LR  0.056678, asymptotic p 0.812",
            "Conditional on rank 1, asymptotic, and one of three tests run together.",
        ):
            assert expected in lines, expected


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
        assert int(uncut["GLD"].isna().sum()) == 0 and int(uncut["USO"].isna().sum()) == 0
        assert str(uncut.index[0].date()) == "2006-04-26"
        with pytest.raises(ValueError, match="column 1 is nan on row 0"):
            johansen(uncut.to_numpy(dtype=float))


class TestTheScaleBreakDecision:
    def test_no_leg_carries_a_flagged_day(self, sources) -> None:
        """``tests/test_scale_breaks.py`` pins 58 closes in eight other ETFs of this file."""
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
        assert "inputdata_etf/" in out and "lifted from inputData_ETF.mat: GDX, GLD, USO" in out

    def test_the_report_prints_each_figure_from_its_own_test(self, capsys, no_arguments) -> None:
        main()
        lines = [line.strip() for line in capsys.readouterr().out.splitlines()]
        for expected in (
            "r <= 0  trace 22.571096 against 13.429, 15.494, 19.935"
            "   eigen 22.423682 against 12.297, 14.264, 18.520",
            "r <= 0  trace  6.132867 against 13.429, 15.494, 19.935"
            "   eigen  6.059166 against 12.297, 14.264, 18.520",
            "r <= 0  trace 44.837732 against 27.067, 29.796, 35.463"
            "   eigen 37.833231 against 18.893, 21.131, 25.865",
            "r <= 0  trace 10.446773 against 13.429, 15.494, 19.935"
            "   eigen 10.402109 against 12.297, 14.264, 18.520",
            "r <= 0  trace  4.349962 against 13.429, 15.494, 19.935"
            "   eigen  3.776364 against 12.297, 14.264, 18.520",
            "r <= 1  trace  3.034162 against 2.705, 3.841, 6.635"
            "   eigen  3.034162 against 2.705, 3.841, 6.635",
            "GDX-USO  eigen  2 at 90%, 1 at 95%, 1 at 99%",
            "triplet's first eigenvector, rows GLD, GDX, USO  0.033109, -0.177036, 0.002549",
            "before   -3.724034 on 537 observations",
            "after    -1.511680 on 940 observations",
            "whole    -1.517588 on 1479 observations",
            "4  GLD and GDX have lost it after       eigen     == 0       0          reproduced",
        ):
            assert expected in lines, expected

    def test_the_report_says_a_criterion_that_fails(
        self, sources, monkeypatch, capsys, no_arguments
    ) -> None:
        """Swapping the windows makes rows 1 to 4 fail, which the report must say."""
        monkeypatch.setattr(module, "WINDOWS", {"before": AFTER, "after": BEFORE, "whole": WHOLE})
        main()
        out = capsys.readouterr().out
        verdicts = [line for line in out.splitlines() if line[:4].strip().isdigit()]
        assert [line.endswith("did not reproduce") for line in verdicts] == [True] * 4 + [False] * 2


def _quoted(fragment: str, text: str) -> bool:
    """Whether ``text`` holds ``fragment`` with no digit run on at either end.

    A plain substring test lets 10.0157 stand for 10.015, or 110.015 for
    10.015, so a digit typed beside a figure would pass.
    """
    return re.search(rf"(?<!\d){re.escape(fragment)}(?!\d)", text) is not None


def _table_row(label: str, values, last: bool = False) -> str:
    """One whole row of a table in the post, as its LaTeX writes it.

    The row's end is part of it, so a row of Lesson 3's two-column table
    cannot match the first two cells of Lesson 1's three-column one.
    """
    return rf"\text{{{label}}} & " + " & ".join(values) + ("\n" if last else r" \\")


@pytest.fixture(scope="module")
def post() -> str:
    return POST.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def regime(tmp_path_factory: pytest.TempPathFactory):
    """The earlier post's regime map, drawn somewhere that is not the repo."""
    return make_regime_figure(out=tmp_path_factory.mktemp("regime") / "regime.png")


class TestThePostQuotesTheRun:
    """At least one copy of each run figure that ``blog/gold-miners-oil-lessons.md`` prints.

    The pins above hold the run's numbers. This class reads the post, so
    editing a copy it reads fails here, and a re-pin fails here until the
    post moves with it. Each fragment is built from the value the
    code computes, at the precision the post prints, and none is typed in. It
    reads Lesson 1's and Lesson 3's tables row by row, and at least one copy
    in the prose of every other figure the post takes from
    ``chan.gold_miners_oil``, ``chan.gold_miners_oil_figures`` or
    ``chan.regime_figure``, with enough words around each that only that
    copy matches. A figure the post prints again, such as the 1,481 days in
    the caption or the 942 days under the figure, is read only where the
    fragment's words put it. The list of Chan's three claims, the headings,
    the caption and the alt texts are not read, and nor is a count written in
    words, such as full rank at 90 percent. A test level is read only in the
    words around a figure, as in the 90 percent bar of 13.429, so a level
    stated apart from one, such as the Engle-Granger test finding the
    relation only at 95 percent, is not. The sketches' labels are held by
    ``tests/test_gold_miners_oil_whiteboard.py``, and README lists what the
    post says that nothing asserts.
    """

    @staticmethod
    def _missing(fragments: list[str], post: str) -> list[str]:
        return [f for f in fragments if not _quoted(f, post)]

    def test_the_file_and_the_windows(self, post, sources, result) -> None:
        members, _ = sources
        _, uncut = module.load_panel(SOURCE_FILE)
        start = {s: str(uncut[s].first_valid_index().date()) for s in TRIPLET}
        assert start["GLD"] == start["USO"], "the post names one start for GLD and USO"
        (saved,) = {m.obtained for m in members}
        before, after, whole = (result.days[name] for name in ("before", "after", "whole"))

        def day(d: pd.Timestamp) -> str:
            return str(d.date())

        fragments = [
            f"`inputData_ETF.mat`, saved on {saved}.",
            f"It holds GLD and USO from {start['GLD']} and GDX from {start['GDX']}, so the run "
            "starts on GDX’s first price",
            f"That leaves {len(whole):,} trading days to {day(whole[-1])}, split {len(before)} "
            f"before the break and {len(after)} after it.",
            f"{day(before[0])} to {day(before[-1])} and {day(after[0])} to {day(after[-1])} "
            "for the pair",
            f"which here means GLD, GDX and USO after {whole[-1]:%B %Y}.",
            f"it says nothing about the years after {whole[-1].year}.",
        ]
        assert self._missing(fragments, post) == []

    def test_lesson_1s_table(self, post, result) -> None:
        tests = (result.before, result.after, result.triplet)
        for test in tests:
            counts = {test.relations(statistic, 99) for statistic in ("trace", "eigen")}
            assert len(counts) == 1, "the table gives one count for both statistics"
        fragments = [
            _table_row("Trace", [f"{t.trace[0]:.3f}" for t in tests]),
            _table_row("Bar, 99 percent", [f"{t.trace_critical[0, 2]:.3f}" for t in tests]),
            _table_row("Eigen", [f"{t.eigen[0]:.3f}" for t in tests]),
            _table_row("Bar, 99 percent", [f"{t.eigen_critical[0, 2]:.3f}" for t in tests]),
            _table_row("Relations", [str(t.relations("trace", 99)) for t in tests], last=True),
        ]
        assert self._missing(fragments, post) == []

    def test_lesson_1s_prose(self, post, result) -> None:
        after, triplet, before = result.after, result.triplet, result.before
        margin = before.trace[0] - before.trace_critical[0, 2]
        fragments = [
            f"the 90 percent bars, {after.trace_critical[0, 0]:.3f} for the trace and "
            f"{after.eigen_critical[0, 0]:.3f} for the eigen statistic",
            f"Its trace statistic for that second step is {triplet.trace[1]:.3f} against a 90 "
            f"percent bar of {triplet.trace_critical[1, 0]:.3f}.",
            f"the trace statistic clears its bar by {margin:.3f}.",
            f"it gives a statistic of {signed(result.cadf['before'].t, 3)} before the break",
            f"After the break it gives {signed(result.cadf['after'].t, 3)}, nowhere near either.",
        ]
        assert self._missing(fragments, post) == []

    def test_the_figures_paragraph(self, post, sources, result) -> None:
        closes = sources[1]
        portfolio = first_window_portfolio(closes, result)
        before, after = portfolio.z.loc[: BEFORE[1]], portfolio.z.loc[AFTER[0] :]
        gld, gdx = portfolio.weights
        fragments = [
            f"USO’s highest close, {closes['USO'].max():.2f}, falls on "
            f"{closes['USO'].idxmax().date()} itself",
            f"{signed(gld, 3)} shares of GLD against {signed(gdx, 3)} of GDX",
            f"the portfolio stays between {signed(before.min())} and {signed(before.max())}",
            f"it runs from {signed(after.min())} to {signed(after.max())} and never comes back",
        ]
        assert self._missing(fragments, post) == []

    def test_lesson_2s_control(self, post, result) -> None:
        control, triplet = result.control, result.triplet
        fragments = [
            f"over the triplet’s {len(result.days['whole']):,} days gives a trace statistic of "
            f"{control.trace[0]:.3f}, short of even its 90 percent bar of "
            f"{control.trace_critical[0, 0]:.3f}",
            f"the trace statistic for the first step is {triplet.trace[0]:.3f}, past its own 99 "
            f"percent bar of {triplet.trace_critical[0, 2]:.3f}",
        ]
        assert self._missing(fragments, post) == []

    def test_lesson_3s_table(self, post, result) -> None:
        pairs = (result.with_oil["GLD"], result.with_oil["GDX"])
        fragments = [
            _table_row("Trace", [f"{p.trace[0]:.3f}" for p in pairs]),
            _table_row("Bar, 90 percent", [f"{p.trace_critical[0, 0]:.3f}" for p in pairs]),
            _table_row("Bar, 99 percent", [f"{p.trace_critical[0, 2]:.3f}" for p in pairs]),
            _table_row("Relations", [str(p.relations("trace", 99)) for p in pairs], last=True),
        ]
        assert self._missing(fragments, post) == []

    def test_lesson_3s_weights(self, post, result) -> None:
        lr = result.zero_weight
        weights = result.triplet.eigenvectors[:, 0]
        fragments = [
            f"gives a statistic of {lr['GLD']:.3f}, past the 95 percent bar of "
            f"{CHI2_1[95]:.3f} and the 99 percent bar of {CHI2_1[99]:.3f}.",
            f"Setting GDX’s weight to zero gives {lr['GDX']:.3f}, far past both bars.",
            f"Setting USO’s weight to zero gives {lr['USO']:.3f}, nowhere near any bar.",
            f"The triplet’s eigenvector is {signed(weights[0], 6)} shares of GLD, "
            f"{signed(weights[1], 6)} of GDX and {signed(weights[2], 6)} of USO.",
        ]
        assert self._missing(fragments, post) == []

    def test_the_earlier_posts_rolling_test(self, post, regime) -> None:
        """The figures the post takes from ``chan.regime_figure``, read as its test reads them."""
        line = regime.axes[0].lines[0]
        ends = pd.DatetimeIndex(line.get_xdata())
        passing = line.get_ydata() < EG_CRIT_N2["10%"]
        inside = (ends >= AFTER[0]) & (ends <= AFTER[1])
        last = ends[passing & (ends.year < 2019)].max()
        (downloaded,) = {entry.obtained[:4] for entry in regime.vintages}
        fragments = [
            f"closing prices downloaded from Yahoo Finance in {downloaded}",
            f"Of the {int(inside.sum())} tests whose year ends inside Chan’s second window, "
            f"{int((inside & passing).sum())} still pass at the 90 percent level.",
            f"That test’s passing years run into {last.year} before they thin out",
        ]
        assert self._missing(fragments, post) == []
