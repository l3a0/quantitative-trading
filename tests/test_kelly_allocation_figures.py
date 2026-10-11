"""The pins for the figure in the post on capped Kelly allocation.

``tests/test_kelly_allocation.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
line, moved a marker or shaded the wrong side of the cap fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose quotes.
No test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The specification is the book's, as ``tests/test_kelly_allocation.py`` states
it: the inputs location 3287 gives, zero correlation, a risk-free rate of 0, a
cap of 2, and ``g = r + F'M - F'CF / 2``. The vintage is ``none, synthetic``,
since nothing here reads a series.
"""

from __future__ import annotations

import numpy as np
import pytest

import chan.coin_flip_figures as shared
from chan import kelly_allocation_figures as figures
from chan.kelly_allocation import MAX_LEVERAGE, MEANS, VOLS, covariance, growth_rate
from chan.kelly_allocation_figures import (
    ALLOCATION_FIGURE,
    BEYOND_CAP,
    allocation_curve,
    make_allocation_figure,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import LOST


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("kelly_allocation_figure") / ALLOCATION_FIGURE


@pytest.fixture(scope="module")
def figure(out):
    return make_allocation_figure(out=out)


@pytest.fixture(scope="module")
def ax(figure):
    (only,) = figure.axes
    return only


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _point(line) -> tuple[float, float]:
    (x,), (y,) = line.get_xdata(), line.get_ydata()
    return float(x), float(y)


class TestTheSolidCurve:
    """The curve the book's Figure 8.1 plots, F2 from 0 to the cap."""

    def test_it_runs_from_zero_to_the_cap(self, ax) -> None:
        f2 = _by_gid(ax.lines)["inside"].get_xdata()
        assert (f2[0], f2[-1]) == (0.0, MAX_LEVERAGE)
        assert np.all(np.diff(f2) > 0)

    def test_it_starts_at_0_4648_and_ends_at_0_955(self, ax) -> None:
        """Everything on strategy 1 at one end, everything on strategy 2 at the other."""
        g = _by_gid(ax.lines)["inside"].get_ydata()
        assert g[0] == pytest.approx(0.4648, abs=1e-12)
        assert g[-1] == pytest.approx(0.955, abs=1e-12)

    def test_it_rises_the_whole_way(self, ax) -> None:
        assert np.all(np.diff(_by_gid(ax.lines)["inside"].get_ydata()) > 0)

    def test_each_point_is_the_growth_rate_on_the_line(self, ax) -> None:
        line = _by_gid(ax.lines)["inside"]
        cov = covariance(VOLS)
        expected = [growth_rate((MAX_LEVERAGE - x, x), MEANS, cov) for x in line.get_xdata()]
        np.testing.assert_allclose(line.get_ydata(), expected, atol=1e-15)

    def test_it_is_solid(self, ax) -> None:
        assert _by_gid(ax.lines)["inside"].get_linestyle() == "-"


class TestPastTheCap:
    """The part the book does not draw, dashed over a shaded region."""

    def test_the_dashed_curve_runs_from_the_cap_to_2_6(self, ax) -> None:
        beyond = _by_gid(ax.lines)["beyond"]
        f2 = beyond.get_xdata()
        assert (f2[0], f2[-1]) == (MAX_LEVERAGE, BEYOND_CAP) == (2.0, 2.6)
        assert beyond.get_linestyle() == "--"

    def test_it_joins_the_solid_curve_at_the_corner(self, ax) -> None:
        lines = _by_gid(ax.lines)
        assert lines["beyond"].get_ydata()[0] == lines["inside"].get_ydata()[-1]

    def test_it_passes_the_unbounded_peak_and_turns_over(self, ax) -> None:
        f2, g = (np.asarray(a) for a in _by_gid(ax.lines)["beyond"].get_data())
        top = int(np.argmax(g))
        assert f2[top] == pytest.approx(2.289321, abs=1e-3)
        assert g[top] == pytest.approx(0.962956, abs=1e-6)
        assert 0 < top < len(g) - 1, "the peak must sit inside the dashed range"
        assert g[-1] < g[top] and g[0] < g[top]

    def test_the_shaded_region_starts_at_the_cap(self, ax) -> None:
        shade = _by_gid(ax.patches)["over_cap"]
        xs = shade.get_path().transformed(shade.get_patch_transform()).vertices[:, 0]
        assert (xs.min(), xs.max()) == pytest.approx((MAX_LEVERAGE, BEYOND_CAP), abs=1e-12)

    def test_the_shaded_region_says_what_it_is(self, ax) -> None:
        label = _by_gid(ax.texts)["over_cap_label"]
        assert label.get_text() == "over the gross cap of 2:\nstrategy 1 is held short"
        assert MAX_LEVERAGE < label.get_position()[0] < BEYOND_CAP

    def test_the_axis_ends_where_the_dashed_curve_does(self, ax) -> None:
        assert ax.get_xlim() == (0.0, BEYOND_CAP)


class TestTheMarkers:
    def test_the_proportional_split(self, ax) -> None:
        f2, g = _point(_by_gid(ax.lines)["proportional"])
        assert f2 == pytest.approx(1.049282, abs=5e-7)
        assert g == pytest.approx(0.816798, abs=5e-7)

    def test_the_corner(self, ax) -> None:
        assert _point(_by_gid(ax.lines)["corner"]) == pytest.approx((2.0, 0.955), abs=1e-12)

    def test_the_unbounded_peak(self, ax) -> None:
        f2, g = _point(_by_gid(ax.lines)["peak"])
        assert f2 == pytest.approx(2.289321, abs=5e-7)
        assert g == pytest.approx(0.962956, abs=5e-7)

    def test_only_the_peak_is_hollow(self, ax) -> None:
        """Hollow is how the figure says the peak is not allowed."""
        lines = _by_gid(ax.lines)
        assert lines["peak"].get_markerfacecolor() == "none"
        assert lines["peak"].get_markeredgecolor() == LOST
        for gid in ("proportional", "corner"):
            assert lines[gid].get_markerfacecolor() != "none"

    def test_each_label_carries_its_markers_values(self, ax) -> None:
        labels = [t.get_text() for t in ax.texts if not t.get_gid()]
        assert labels == [
            "proportional split, F2 = 1.049282\ng = 0.816798",
            "everything on strategy 2, F2 = 2\ng = 0.955",
            "unbounded peak, F2 = 2.289321\ng = 0.962956, not allowed",
        ]

    def test_the_markers_come_from_the_runs_functions(self) -> None:
        curve = allocation_curve()
        assert curve.corner.f2 == MAX_LEVERAGE
        assert curve.proportional.f2 < curve.corner.f2 < curve.peak.f2


class TestTheText:
    def test_the_title_carries_no_label(self, figure) -> None:
        """Neither epistemic label applies, because no sample was spent."""
        title = figure._suptitle.get_text()
        assert title == (
            "Under a cap of 2, the growth rate rises all the way to everything on strategy 2"
        )
        assert "xploratory" not in title and "egistered" not in title

    def test_the_note_names_the_inputs_and_what_is_added(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Example 8.2, location 3287. Means 0.30 and 0.60, volatilities "
            "0.26 and 0.35, no correlation, risk-free rate 0.\n"
            "g = F′M − F′CF / 2 along F1 + F2 = 2. The solid curve redraws the book's Figure "
            "8.1. The dashed part past the cap is added."
        ]

    def test_the_axes_say_what_they_hold(self, ax) -> None:
        assert ax.get_xlabel() == "F2, the leverage on strategy 2, with F1 = 2 − F2 on strategy 1"
        assert ax.get_ylabel() == "growth rate g"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / ALLOCATION_FIGURE).is_file()

    def test_drawing_elsewhere_writes_nothing_where_the_committed_file_lives(
        self, tmp_path, monkeypatch
    ) -> None:
        default = tmp_path / "default"
        default.mkdir()
        monkeypatch.setattr(shared, "FIGURES_DIR", default)
        make_allocation_figure(out=tmp_path / "elsewhere.png")
        assert list(default.iterdir()) == []

    def test_the_command_writes_the_file_and_says_where(self, tmp_path, monkeypatch, capsys):
        """The save helper lives in ``chan.coin_flip_figures``, so both modules'
        figure directory is redirected, and the file must land where the
        printed line says."""
        monkeypatch.setattr(figures, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(shared, "FIGURES_DIR", tmp_path)
        figures.main()
        assert capsys.readouterr().out == f"wrote {tmp_path / ALLOCATION_FIGURE}\n"
        assert (tmp_path / ALLOCATION_FIGURE).is_file()
