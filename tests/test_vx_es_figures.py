"""The pins for the figure in the post on VX against ES from August 2008.

``tests/test_vx_es.py`` holds what the run computes. This file holds that the
figure draws those numbers, so a generator that plotted the wrong series,
moved the split or mislabelled a panel fails even when the arithmetic is
right. Some numbers repeat here on purpose, because a figure's labels are
prose and the suite is the authority for every number prose quotes. No test
compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification ``tests/test_vx_es.py``
states in its module docstring: Chan's ``inputDataOHLCDaily_20120507.mat``,
saved 2012-05-09, VX and ES on their 1,999 common days, and
``ols(50·ES, [1000·VX, 1])`` on 2008-08-04 to 2010-07-28 traded against a band
at ±1 until the opposite band.

Exploratory, like everything locations 2546 to 2559 compute here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.dates import date2num

from chan import vx_es_figures
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, RULE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable
from chan.vx_es import ES, VX, position_changes, read_legs, vx_es
from chan.vx_es_figures import (
    DOWNGRADE,
    REGIMES,
    VX_ES_FIGURE,
    Holding,
    cumulative_return,
    holdings,
    main,
    make_vx_es_figure,
    regime_masks,
    signed,
)


@pytest.fixture(scope="module")
def sources():
    return read_legs()


@pytest.fixture(scope="module")
def legs(sources) -> pd.DataFrame:
    return sources[1]


@pytest.fixture(scope="module")
def result(legs):
    return vx_es(legs)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("vx_es_figure") / VX_ES_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_vx_es_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    scatter, z, returns = figure.axes
    return {"scatter": scatter, "z": z, "returns": returns}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


class TestTheFigure:
    def test_there_are_three_panels(self, figure) -> None:
        assert len(figure.axes) == 3

    def test_the_title_carries_the_label_and_the_note_names_the_save(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: VX against ES from August 2008, on Chan's 2012-05-07 save"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, locations 2546 to 2559. Closes from "
            "inputDataOHLCDaily_20120507.mat, saved 2012-05-09.\nThe save and the exit were "
            "chosen because they land the printed figures, so the match is partly built in."
        ]

    def test_drawing_with_no_sources_reads_the_committed_save(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_vx_es_figure(out=tmp_path / VX_ES_FIGURE)
        line = _by_gid(drawn.axes[1].lines)["zscore"]
        np.testing.assert_array_equal(line.get_ydata(), result.trade.zscore)


class TestTheScatter:
    """Figure 5.10, ``scatter(VX, ES)`` in ``VX_ES.m``, each price in dollars per contract."""

    def test_the_regimes_split_the_1999_days(self, legs) -> None:
        masks = regime_masks(legs.index)
        assert len(legs) == 1999
        assert {k: int(v.sum()) for k, v in masks.items()} == {
            "first": 1006,
            "between": 43,
            "second": 950,
        }
        assert sum(masks.values()).tolist() == [1] * 1999
        assert str(legs.index[masks["first"]][-1].date()) == "2008-05-30"
        assert str(legs.index[masks["second"]][0].date()) == "2008-08-01"

    def test_each_group_plots_its_days_in_dollars(self, axes, legs) -> None:
        groups = _by_gid(axes["scatter"].collections)
        masks = regime_masks(legs.index)
        for gid, _, _ in REGIMES:
            expected = np.column_stack(
                [1000 * legs[VX].to_numpy()[masks[gid]], 50 * legs[ES].to_numpy()[masks[gid]]]
            )
            np.testing.assert_array_equal(groups[gid].get_offsets(), expected)

    def test_each_group_is_coloured_and_labelled_as_its_legend_says(self, axes) -> None:
        groups = _by_gid(axes["scatter"].collections)
        legend = [t.get_text() for t in axes["scatter"].get_legend().get_texts()]
        assert legend == [
            "2004 to May 2008, 1,006 days",
            "June and July 2008, between the regimes, 43 days",
            "August 2008 to May 2012, 950 days",
            "the fit on the 500 training days",
        ]
        assert [tuple(groups[g].get_facecolor()[0][:3]) for g, _, _ in REGIMES] == [
            pytest.approx(tuple(int(c[i : i + 2], 16) / 255 for i in (1, 3, 5)))
            for c in (ACCENT, RULE, INK)
        ]

    def test_the_fit_is_the_training_regression_over_the_training_range(
        self, axes, legs, result
    ) -> None:
        h = result.hedge
        fit = _by_gid(axes["scatter"].lines)["fit"]
        training = 1000 * legs.loc[h.days, VX].to_numpy()
        x = np.array([training.min(), training.max()])
        np.testing.assert_array_equal(fit.get_xdata(), x)
        np.testing.assert_allclose(fit.get_ydata(), h.intercept - h.hedge * x, rtol=1e-12)
        assert fit.get_color() == LOST

    def test_the_heading_names_the_fit(self, axes) -> None:
        assert _title(axes["scatter"]) == (
            "Figure 5.10: 50·ES against 1000·VX on each of the 1,999 days both traded.\n"
            "The fit on 2008-08-04 to 2010-07-28 is long 0.3906 VX contracts against one ES,\n"
            "with a residual deviation of $2,044.91."
        )


class TestTheZScore:
    def test_the_line_is_the_run_s_z_score_from_the_anchor(self, axes, result) -> None:
        line = _by_gid(axes["z"].lines)["zscore"]
        t = result.trade
        assert len(t.days) == 949
        assert list(line.get_xdata()) == list(t.days)
        np.testing.assert_array_equal(line.get_ydata(), t.zscore)
        assert axes["z"].get_xlim() == (date2num(t.days[0]), date2num(t.days[-1]))

    def test_the_band_sits_at_plus_and_minus_one(self, axes) -> None:
        lines = _by_gid(axes["z"].lines)
        assert list(lines["upper"].get_ydata()) == [1, 1]
        assert list(lines["lower"].get_ydata()) == [-1, -1]

    def test_the_split_is_the_last_training_day(self, axes) -> None:
        split = _by_gid(axes["z"].lines)["split"]
        assert list(split.get_xdata()) == [pd.Timestamp("2010-07-28")] * 2
        assert split.get_linestyle() == "--"

    def test_holdings_are_the_runs_of_the_band_s_units(self, result) -> None:
        runs = holdings(result.trade)
        assert [(str(r.first.date()), str(r.last.date()), r.units) for r in runs] == [
            ("2008-08-04", "2008-09-12", 0),
            ("2008-09-15", "2008-10-27", 1),
            ("2008-10-28", "2009-02-02", -1),
            ("2009-02-03", "2009-09-15", 1),
            ("2009-09-16", "2010-06-30", -1),
            ("2010-07-01", "2011-11-07", 1),
            ("2011-11-08", "2011-12-16", -1),
            ("2011-12-19", "2012-02-16", 1),
            ("2012-02-17", "2012-05-08", -1),
        ]

    def test_holdings_close_a_run_on_the_last_day_before_a_change(self) -> None:
        days = pd.date_range("2010-07-26", periods=5, freq="B")

        class Traded:
            units = np.array([0.0, 1.0, 1.0, -1.0, -1.0])

        Traded.days = days
        assert holdings(Traded) == [
            Holding(days[0], days[0], 0.0),
            Holding(days[1], days[2], 1.0),
            Holding(days[3], days[4], -1.0),
        ]

    def test_each_shade_runs_from_an_entry_to_the_next(self, axes, result) -> None:
        """Green for a long and red for a short, with the flat start left unshaded."""
        runs = holdings(result.trade)
        shades = [p for p in axes["z"].patches if p.get_gid() in ("long", "short")]
        held = [r for r in runs if r.units]
        ends = [after.first for after in runs[1:]] + [runs[-1].last]
        ends = [end for r, end in zip(runs, ends, strict=True) if r.units]
        assert len(shades) == len(held) == 8
        for shade, run, end in zip(shades, held, ends, strict=True):
            assert shade.get_x() == pytest.approx(date2num(run.first))
            assert shade.get_x() + shade.get_width() == pytest.approx(date2num(end))
            assert shade.get_gid() == ("long" if run.units > 0 else "short")
            colour = GOOD if run.units > 0 else LOST
            assert tuple(shade.get_facecolor()[:3]) == pytest.approx(
                tuple(int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
            )

    def test_the_heading_names_the_band_and_the_lowest_day(self, axes) -> None:
        assert _title(axes["z"]) == (
            "The z-score from 2008-08-04, with the band at ±1. Shaded green while long and red "
            "while short.\nDashed: the last training day, 2010-07-28. The lowest, −3.89, is on "
            "2011-08-08."
        )


class TestTheCumulativeReturn:
    """Figure 5.12, ``cumprod(1+ret)-1`` over the 449 test days."""

    def test_the_line_is_the_compounded_test_return(self, axes, result) -> None:
        line = _by_gid(axes["returns"].lines)["cumulative"]
        t = result.trade
        assert list(line.get_xdata()) == list(t.test_days)
        np.testing.assert_allclose(line.get_ydata(), np.cumprod(1 + t.daily) - 1, rtol=1e-12)
        assert axes["returns"].get_xlim() == (date2num(t.test_days[0]), date2num(t.test_days[-1]))

    def test_the_axis_reads_the_return_as_a_percentage(self, axes) -> None:
        """A cumulative return of 0.2 is labelled 20%, not 0.2%."""
        assert axes["returns"].yaxis.get_major_formatter()(0.2) == "20%"

    def test_it_ends_where_the_apr_says(self, axes, result) -> None:
        ydata = _by_gid(axes["returns"].lines)["cumulative"].get_ydata()
        assert ydata[-1] == pytest.approx((1 + result.trade.apr) ** (449 / 252) - 1, rel=1e-12)
        assert ydata[-1] == pytest.approx(0.229231, abs=5e-7)

    def test_the_dots_are_the_three_changes_of_position(self, axes, result) -> None:
        dots = _by_gid(axes["returns"].lines)["changes"]
        changes = [day for day, _ in position_changes(result.trade)]
        cumret = cumulative_return(result.trade)
        assert [str(d.date()) for d in dots.get_xdata()] == [
            "2011-11-08",
            "2011-12-19",
            "2012-02-17",
        ]
        assert list(dots.get_xdata()) == changes
        np.testing.assert_array_equal(dots.get_ydata(), cumret.loc[changes])

    def test_the_downgrade_is_marked_with_its_figure(self, axes, result) -> None:
        artists = _by_gid(axes["returns"].lines)
        assert list(artists["downgrade"].get_xdata()) == [DOWNGRADE] * 2
        assert DOWNGRADE == pd.Timestamp("2011-08-05")
        label = _by_gid(axes["returns"].texts)["downgrade-label"]
        assert label.get_text() == "−4.59 percent at the close of 2011-08-05"
        assert label.xy == (DOWNGRADE, cumulative_return(result.trade).loc[DOWNGRADE])

    def test_the_heading_sets_the_figures_beside_the_book_s(self, axes) -> None:
        assert _title(axes["returns"]) == (
            "Figure 5.12: the test set, 2010-07-29 to 2012-05-08, ending at 22.92 percent. "
            "Dots: the three changes of position.\nAPR 0.122811 and Sharpe ratio 1.393201, "
            "where the book prints 12.3 percent and 1.4. No cost is charged."
        )

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-3.886) == "−3.89"
        assert signed(4.5935) == "4.59"


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / VX_ES_FIGURE).is_file()

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(vx_es_figures, "make_vx_es_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_a_missing_save_reaches_the_operator_as_one_line(self, monkeypatch, tmp_path) -> None:
        """No mock: the real read, pointed at an empty directory, refuses the save."""
        real = vx_es_figures.read_legs
        monkeypatch.setattr(vx_es_figures, "read_legs", lambda: real(data_dir=tmp_path))
        with pytest.raises(SystemExit) as stopped:
            main()
        assert "inputDataOHLCDaily_20120507.mat" in str(stopped.value)
        assert "\n" not in str(stopped.value)

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is lifted from inputDataOHLCDaily_20120507"),
            WindowCrossesScaleBreak("inputdataohlcdaily_20120507/vx.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(vx_es_figures, "make_vx_es_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
