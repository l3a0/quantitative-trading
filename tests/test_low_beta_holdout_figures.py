"""The pins for the figure in the post on Chan's low-beta rule after the book, Entry 49.

``tests/test_low_beta_holdout.py`` holds what the holdout computes, and
``tests/test_low_beta_leverage.py`` what the run on Chan's file computes. This
file holds that the figure draws those numbers, so a generator that plotted a
leverage at its formation month rather than its holding month, dropped the
skipped formations or marked the wrong month fails even when the arithmetic
is right. Some numbers repeat here on purpose, because a figure's labels are
prose and the suite is the authority for every number prose quotes. No test
compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The right column reads the holdout, and the real holdout needs the owner's
archive of Alpha Vantage prices, so the file splits in two.

1. **The drawing**, on Chan's committed files for the left column and a
   synthetic holdout built here for the right, runs on every clone. The
   synthetic holdout is :func:`chan.low_beta_leverage.build_portfolios` under
   ``skip_non_positive`` on a hand-built panel, so it skips one formation the
   way the real run skips four, with its beta and leverage paths replaced by
   ones whose marks sit where a test can name them.
2. **The marks on the real right column** read one run of
   :func:`chan.low_beta_holdout.read_holdout`, so they skip where no archive is
   configured or ``QT_ARCHIVE_RUN`` is not 1, as ``tests/conftest.py``'s
   ``archive_skip_reason`` decides. They read the vintages and the
   specification that ``tests/test_low_beta_holdout.py`` carries as its
   ``SPEC``.

The price is that CI never sees the real right column drawn, and a reader
cannot redraw it. Each column's verdict is registered under its amendments,
and every path drawn is exploratory.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pandas as pd
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.dates import date2num
from matplotlib.text import Text

from chan import low_beta_holdout
from chan import low_beta_holdout_figures as module
from chan.low_beta_holdout import HoldoutRefused
from chan.low_beta_holdout_figures import (
    BETA_LIMITS,
    LEVERAGE_LIMITS,
    LOW_BETA_HOLDOUT_FIGURE,
    main,
    make_low_beta_holdout_figure,
    span,
)
from chan.low_beta_leverage import Portfolios, build_portfolios, read_sources
from chan.paths import FIGURES_DIR
from chan.regime_figure import INK, LOST, MUTED
from tests.conftest import archive_skip_reason
from tests.test_low_beta_holdout import HELD_TO, everyone
from tests.test_low_beta_holdout import SPEC as HOLDOUT_SPEC
from tests.test_low_beta_leverage import SPEC as CHAN_SPEC
from tests.test_low_beta_leverage import panel, rates, spy
from tests.test_regime_figure import png_size

#: The synthetic holdout's skipped formation and the month it would have held.
SKIP_FORMED, SKIP_HELD = pd.Timestamp("2001-01-31"), pd.Timestamp("2001-02-28")

#: Where the synthetic paths put their marks, each a holding month.
LOWEST, WORST = pd.Timestamp("2001-07-31"), pd.Timestamp("2001-04-30")


def negative_in_one_month() -> tuple[pd.DataFrame, pd.DataFrame]:
    """A panel whose low group is N, at a beta of −0.3, only at the formation of 2001-01-31.

    ``tests/test_low_beta_holdout.py`` builds the same panel at −0.5, which
    lies below :data:`BETA_LIMITS`, the axis the real skipped betas fit.
    """
    closes = panel(rates(0.06), N=-0.3, A=0.5, B=1.0, C=1.5, D=2.0, E=2.5)
    mask = everyone(closes)
    mask["N"] = mask.index == HELD_TO
    return closes, mask


def synthetic_holdout() -> Portfolios:
    """A holdout of ten holding months with one formation skipped, and marks set by hand.

    The low beta bottoms at :data:`LOWEST`, so k peaks there, and the worst
    levered month is :data:`WORST`, a different month, so a figure that marked
    the worst month at the highest k fails. No month is ruined.
    """
    closes, mask = negative_in_one_month()
    p = build_portfolios(closes, spy(), rates(0.06), members=mask, skip_non_positive=True)
    months = pd.DatetimeIndex(p.held_to)
    low = pd.Series(np.linspace(0.6, 0.3, len(months)), index=months)
    low[LOWEST] = 0.08
    high = pd.Series(1.6, index=months)
    levered = pd.Series(0.02, index=months)
    levered[WORST] = -0.7
    return dataclasses.replace(
        p,
        low_beta=low.rename("low beta"),
        high_beta=high.rename("high beta"),
        leverage=(high / low).rename("k"),
        levered=levered.rename("levered low"),
    )


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def chan(sources) -> Portfolios:
    _, closes, _, market, _, bills = sources
    return build_portfolios(closes, market, bills)


@pytest.fixture(scope="module")
def ivv() -> Portfolios:
    return synthetic_holdout()


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("low_beta_holdout_figure") / LOW_BETA_HOLDOUT_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources, chan, ivv):
    return make_low_beta_holdout_figure(out=out, chan=chan, ivv=ivv, sources=sources)


def _renderer(figure):
    """The figure drawn once more on a canvas that can measure text and lay out tick labels."""
    FigureCanvasAgg(figure)
    figure.canvas.draw()
    return figure.canvas.get_renderer()


@pytest.fixture(scope="module")
def renderer(figure):
    return _renderer(figure)


def _axes(figure) -> dict:
    chan_beta, ivv_beta, chan_k, ivv_k = figure.axes
    return {
        ("chan", "beta"): chan_beta,
        ("ivv", "beta"): ivv_beta,
        ("chan", "k"): chan_k,
        ("ivv", "k"): ivv_k,
    }


@pytest.fixture(scope="module")
def axes(figure):
    return _axes(figure)


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _months(line) -> pd.DatetimeIndex:
    return pd.DatetimeIndex(line.get_xdata())


def _shaded(ax) -> tuple:
    """The x-extent of the skipped months' shading, in matplotlib's date numbers."""
    (patch,) = [p for p in ax.patches if p.get_gid() == "skipped-span"]
    xs = patch.get_patch_transform().transform(patch.get_path().vertices)[:, 0]
    return float(xs.min()), float(xs.max())


class TestTheFigure:
    def test_there_are_four_panels_and_each_row_shares_its_y_axis(self, figure, axes) -> None:
        assert len(figure.axes) == 4
        for row in ("beta", "k"):
            left, right = axes[("chan", row)], axes[("ivv", row)]
            assert left.get_shared_y_axes().joined(left, right), row
            assert left.get_ylim() == right.get_ylim(), row

    def test_the_title_carries_both_labels_and_the_note_names_each_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Registered verdicts, exploratory paths: the beta match on Chan's file and after the "
            "book"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Quantitative Trading, locations 4684 and 4709. Left: stocks from SPX_20071123.mat, "
            "saved 2007-11-24, survivors only, and SPY from spy_chan.csv. Not a holdout.\n"
            "Right: IVV's members at each month-end, Alpha Vantage adjusted closes downloaded "
            "2026-10-05, and SPY's downloaded 2026-10-11, in a private archive. A holdout.\n"
            "Both borrow at FRED's TB3MS, downloaded 2026-09-30. Each value sits at the month "
            "it applied to.\nEach verdict is registered under its amendments, and every path "
            "drawn is exploratory."
        ], HOLDOUT_SPEC

    def test_each_column_spans_its_holding_months_and_the_skipped_ones(self, axes, ivv) -> None:
        chan_span = (date2num(pd.Timestamp("2000-12-29")), date2num(pd.Timestamp("2007-10-31")))
        ivv_span = (date2num(ivv.held_to[0]), date2num(ivv.held_to[-1]))
        for row in ("beta", "k"):
            assert axes[("chan", row)].get_xlim() == chan_span, CHAN_SPEC
            assert axes[("ivv", row)].get_xlim() == ivv_span

    def test_the_y_axes_and_their_limits(self, axes) -> None:
        assert axes[("chan", "beta")].get_ylabel() == "mean beta at formation"
        assert axes[("chan", "k")].get_ylabel() == "leverage, log scale"
        assert axes[("chan", "beta")].get_ylim() == pytest.approx(BETA_LIMITS)
        assert axes[("chan", "k")].get_ylim() == pytest.approx(LEVERAGE_LIMITS)

    def test_every_series_lies_inside_its_panel(self, axes) -> None:
        """A limit too tight hides a point the post quotes, such as Chan's k of 69.0762."""
        drawn = {}
        for key, ax in axes.items():
            low, high = ax.get_ylim()
            for line in ax.lines:
                y = np.asarray(line.get_ydata(), dtype=float)
                assert ((low <= y) & (y <= high)).all(), (key, line.get_gid(), y.min(), y.max())
                drawn.setdefault(key, set()).add(line.get_gid())
        assert drawn == {
            ("chan", "beta"): {"zero", "high", "low", "lowest"},
            ("ivv", "beta"): {"zero", "high", "low", "lowest", "skipped"},
            ("chan", "k"): {"k", "highest", "ruined"},
            ("ivv", "k"): {"k", "highest", "worst"},
        }

    def test_the_log_axis_labels_its_ticks_as_plain_numbers(self, axes, renderer) -> None:
        ax = axes[("chan", "k")]
        assert ax.get_yscale() == "log"
        assert list(ax.get_yticks()) == [2, 5, 10, 20, 50, 100]
        assert [t.get_text() for t in ax.get_yticklabels()] == ["2", "5", "10", "20", "50", "100"]

    def test_the_right_column_hides_its_repeated_y_labels(self, axes, renderer) -> None:
        for row in ("beta", "k"):
            labels = axes[("ivv", row)].get_yticklabels()
            assert not any(t.get_visible() and t.get_text() for t in labels), row

    def test_drawing_with_nothing_handed_in_reads_builds_and_reads_the_holdout(
        self, monkeypatch, tmp_path, sources, chan, ivv
    ) -> None:
        """``main`` and the committed PNG take this path, so its wiring is checked here."""
        calls = []

        def read():
            calls.append("read")
            return sources

        def build(closes, market, bills):
            calls.append("build")
            assert (closes, market, bills) == (sources[1], sources[3], sources[5])
            return chan

        def holdout():
            calls.append("holdout")
            return dataclasses.replace(_HOLDOUT_STUB, portfolios=ivv)

        monkeypatch.setattr(module, "read_sources", read)
        monkeypatch.setattr(module, "build_portfolios", build)
        monkeypatch.setattr(module, "read_holdout", holdout)
        drawn = make_low_beta_holdout_figure(out=tmp_path / LOW_BETA_HOLDOUT_FIGURE)
        assert calls == ["read", "build", "holdout"]
        lines = _axes(drawn)
        np.testing.assert_array_equal(
            _by_gid(lines[("chan", "k")].lines)["k"].get_ydata(), chan.leverage.to_numpy()
        )
        np.testing.assert_array_equal(
            _by_gid(lines[("ivv", "k")].lines)["k"].get_ydata(), ivv.leverage.to_numpy()
        )


#: A holdout whose only field the figure reads is ``portfolios``.
_HOLDOUT_STUB = low_beta_holdout.Holdout(
    entries=(),
    spy_entry=None,
    calendar=None,
    bill_entry=None,
    coverage=(),
    portfolios=None,
    members=(),
    covered=(),
    flags={},
    flagged=(0, 0),
    moved=0,
    off_calendar=0,
    survivors=None,
    reads_next=None,
)


class TestTheLeftColumn:
    """Chan's file, from the committed files, as Entry 45's figure draws it."""

    def test_each_line_is_the_groups_mean_beta_by_holding_month(self, axes, chan) -> None:
        lines = _by_gid(axes[("chan", "beta")].lines)
        assert lines["low"].get_color() == INK and lines["high"].get_color() == MUTED
        for gid, series in (("low", chan.low_beta), ("high", chan.high_beta)):
            assert _months(lines[gid]).equals(pd.DatetimeIndex(chan.held_to)), CHAN_SPEC
            np.testing.assert_array_equal(lines[gid].get_ydata(), series.to_numpy())

    def test_the_lowest_beta_is_marked_at_may_2001(self, axes) -> None:
        marker = _by_gid(axes[("chan", "beta")].lines)["lowest"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2001-05-31")], CHAN_SPEC
        assert marker.get_color() == LOST
        label = _by_gid(axes[("chan", "beta")].texts)["lowest-label"]
        assert label.get_text() == "lowest kept, 0.0280, formed 2001-04-30", CHAN_SPEC

    def test_k_and_its_highest(self, axes, chan) -> None:
        ax = axes[("chan", "k")]
        line = _by_gid(ax.lines)["k"]
        assert _months(line).equals(pd.DatetimeIndex(chan.held_to)), CHAN_SPEC
        np.testing.assert_array_equal(line.get_ydata(), chan.leverage.to_numpy())
        label = _by_gid(ax.texts)["highest-label"]
        assert label.xy[0] == pd.Timestamp("2001-05-31"), CHAN_SPEC
        assert label.get_text() == "highest, 69.0762, formed 2001-04-30", CHAN_SPEC

    def test_the_two_ruined_months_are_marked_and_no_worst_month_is(self, axes) -> None:
        ax = axes[("chan", "k")]
        marker = _by_gid(ax.lines)["ruined"]
        assert list(marker.get_xdata()) == [
            pd.Timestamp("2001-06-29"),
            pd.Timestamp("2001-09-28"),
        ], CHAN_SPEC
        assert [f"{k:.4f}" for k in marker.get_ydata()] == ["58.0262", "31.5098"], CHAN_SPEC
        texts = _by_gid(ax.texts)
        assert [texts[f"ruined-label-{n}"].get_text() for n in (0, 1)] == [
            "ruined 2001-06-29: k 58.0262",
            "ruined 2001-09-28: k 31.5098",
        ], CHAN_SPEC
        assert "worst" not in _by_gid(ax.lines) and "worst-label" not in texts

    def test_nothing_is_skipped_or_shaded(self, axes) -> None:
        for row in ("beta", "k"):
            ax = axes[("chan", row)]
            assert not [p for p in ax.patches if p.get_gid() == "skipped-span"], row
            assert "skipped" not in _by_gid(ax.lines), row
        assert axes[("chan", "k")].get_legend() is None

    def test_the_headings(self, axes) -> None:
        assert _title(axes[("chan", "beta")]) == (
            "Chan's file: each fifth's mean beta at formation.\nThe low fifth's fell to 0.0280."
        ), CHAN_SPEC
        assert _title(axes[("chan", "k")]) == (
            "Chan's file: k, the leverage that matches the high fifth's beta,\nmean 7.8414. "
            "2 months lost more than the capital."
        ), CHAN_SPEC


class TestTheRightColumn:
    """The synthetic holdout, whose marks were placed by :func:`synthetic_holdout`."""

    def test_each_line_is_the_groups_mean_beta_by_holding_month(self, axes, ivv) -> None:
        lines = _by_gid(axes[("ivv", "beta")].lines)
        for gid, series in (("low", ivv.low_beta), ("high", ivv.high_beta)):
            assert _months(lines[gid]).equals(pd.DatetimeIndex(ivv.held_to))
            np.testing.assert_array_equal(lines[gid].get_ydata(), series.to_numpy())
        assert SKIP_HELD not in _months(lines["low"])

    def test_the_lowest_kept_beta_is_marked_at_its_holding_month(self, axes) -> None:
        marker = _by_gid(axes[("ivv", "beta")].lines)["lowest"]
        assert list(marker.get_xdata()) == [LOWEST]
        assert list(marker.get_ydata()) == [0.08]
        label = _by_gid(axes[("ivv", "beta")].texts)["lowest-label"]
        assert label.get_text() == "lowest kept, 0.0800, formed 2001-06-29"

    def test_the_skipped_formation_is_plotted_at_its_negative_low_beta(self, axes) -> None:
        marker = _by_gid(axes[("ivv", "beta")].lines)["skipped"]
        assert list(marker.get_xdata()) == [SKIP_HELD]
        assert marker.get_ydata()[0] == pytest.approx(-0.3, abs=1e-9)
        assert (marker.get_markeredgecolor(), marker.get_markerfacecolor()) == (LOST, "none")
        label = _by_gid(axes[("ivv", "beta")].texts)["skipped-label"]
        assert label.get_text() == (
            "1 skipped, formed 2001-01-31 to 2001-01-31, low fifth's beta −0.3000 to −0.3000"
        )

    def test_the_skipped_month_is_shaded_in_both_panels(self, axes) -> None:
        for row in ("beta", "k"):
            assert _shaded(axes[("ivv", row)]) == (date2num(SKIP_FORMED), date2num(SKIP_HELD)), row

    def test_k_and_its_highest(self, axes, ivv) -> None:
        ax = axes[("ivv", "k")]
        line = _by_gid(ax.lines)["k"]
        assert _months(line).equals(pd.DatetimeIndex(ivv.held_to))
        np.testing.assert_array_equal(line.get_ydata(), ivv.leverage.to_numpy())
        label = _by_gid(ax.texts)["highest-label"]
        assert label.xy[0] == LOWEST
        assert label.xy[1] == pytest.approx(20.0)
        assert label.get_text() == "highest, 20.0000, formed 2001-06-29"

    def test_with_no_ruin_the_worst_levered_month_is_marked(self, axes) -> None:
        ax = axes[("ivv", "k")]
        marker = _by_gid(ax.lines)["worst"]
        assert list(marker.get_xdata()) == [WORST]
        assert marker.get_color() == LOST
        label = _by_gid(ax.texts)["worst-label"]
        assert label.get_text() == "worst month 2001-04-30: k 3.0000,\nlevered return −0.7000"
        assert "ruined" not in _by_gid(ax.lines)

    def test_the_legend_names_the_shading(self, axes) -> None:
        legend = [t.get_text() for t in axes[("ivv", "k")].get_legend().get_texts()]
        assert legend == ["months skipped, low beta at or below zero", "k, high beta over low"]

    def test_the_headings(self, axes) -> None:
        assert _title(axes[("ivv", "beta")]) == (
            "IVV's members: each fifth's mean beta at formation.\nThe low fifth's fell to 0.0800, "
            "and 1 formation at or below zero is skipped."
        )
        assert _title(axes[("ivv", "k")]) == (
            "IVV's members: k, the leverage that matches the high fifth's beta,\nmean "
            f"{synthetic_holdout().leverage.mean():.4f}. No month lost the capital."
        )

    def test_a_ruined_month_is_marked_instead_of_the_worst(self, sources, chan, ivv, tmp_path):
        levered = ivv.levered.copy()
        levered[WORST] = -1.0
        drawn = make_low_beta_holdout_figure(
            out=tmp_path / LOW_BETA_HOLDOUT_FIGURE,
            chan=chan,
            ivv=dataclasses.replace(ivv, levered=levered),
            sources=sources,
        )
        ax = _axes(drawn)[("ivv", "k")]
        assert list(_by_gid(ax.lines)["ruined"].get_xdata()) == [WORST]
        assert "worst" not in _by_gid(ax.lines)
        assert _title(ax).endswith("1 month lost more than the capital.")

    def test_with_nothing_skipped_nothing_is_shaded(self, sources, chan, tmp_path) -> None:
        closes, mask = negative_in_one_month()
        whole = build_portfolios(
            closes, spy(), rates(0.06), members=mask.assign(N=False), skip_non_positive=True
        )
        drawn = make_low_beta_holdout_figure(
            out=tmp_path / LOW_BETA_HOLDOUT_FIGURE, chan=chan, ivv=whole, sources=sources
        )
        for row in ("beta", "k"):
            ax = _axes(drawn)[("ivv", row)]
            assert not [p for p in ax.patches if p.get_gid() == "skipped-span"], row
        assert "skipped" not in _by_gid(_axes(drawn)[("ivv", "beta")].lines)
        assert _title(_axes(drawn)[("ivv", "beta")]).endswith("fell to 0.5000.")
        assert _axes(drawn)[("ivv", "k")].get_legend() is None


class TestTheSpan:
    def test_it_runs_to_the_last_skipped_holding_month(self, ivv) -> None:
        last = pd.Timestamp("2002-01-31")
        moved = dataclasses.replace(
            ivv, skipped=(dataclasses.replace(ivv.skipped[0], held_to=last),)
        )
        assert span(moved) == (ivv.held_to[0], last)
        assert span(ivv) == (ivv.held_to[0], ivv.held_to[-1])


def _text_boxes(ax, renderer) -> dict:
    """Each label's text alone, in display pixels, without the rule joining it to its point."""
    return {t.get_gid(): Text.get_window_extent(t, renderer) for t in ax.texts}


def _points(line) -> np.ndarray:
    """A line's points in display pixels, with 50 more along each segment between them."""
    path = line.get_transform().transform(line.get_xydata())
    steps = np.linspace(0, 1, 50)[:, None]
    segments = [a + steps * (b - a) for a, b in zip(path[:-1], path[1:], strict=True)]
    return np.concatenate([path, *segments])


def assert_labels_clear(panels: dict, renderer) -> None:
    """Every label's text sits inside its panel, apart from the others and off every line.

    ``LABEL_AT`` was placed by eye so that this holds on the committed files
    and on the archive run, so only those two are checked.
    """
    for key, ax in panels.items():
        frame = ax.get_window_extent(renderer)
        boxes = _text_boxes(ax, renderer)
        for gid, box in boxes.items():
            assert frame.x0 <= box.x0 and box.x1 <= frame.x1, (key, gid)
            assert frame.y0 <= box.y0 and box.y1 <= frame.y1, (key, gid)
            for line in ax.lines:
                xy = _points(line)
                inside = (
                    (box.x0 <= xy[:, 0])
                    & (xy[:, 0] <= box.x1)
                    & (box.y0 <= xy[:, 1])
                    & (xy[:, 1] <= box.y1)
                )
                assert not inside.any(), (key, gid, line.get_gid())
            legend = ax.get_legend()
            if legend is not None:
                assert not box.overlaps(legend.get_window_extent(renderer)), (key, gid)
        listed = list(boxes.items())
        for n, (gid, box) in enumerate(listed):
            for other, second in listed[n + 1 :]:
                assert not box.overlaps(second), (key, gid, other)


class TestTheLeftLabels:
    def test_every_label_on_chans_file_is_clear(self, axes, renderer) -> None:
        assert_labels_clear({k: v for k, v in axes.items() if k[0] == "chan"}, renderer)


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / LOW_BETA_HOLDOUT_FIGURE).is_file()

    def test_a_fresh_draw_has_the_committed_image_dimensions(self, figure, out) -> None:
        assert png_size(out) == png_size(FIGURES_DIR / LOW_BETA_HOLDOUT_FIGURE)

    def test_drawing_to_out_leaves_the_committed_figure_alone(
        self, tmp_path, sources, chan, ivv
    ) -> None:
        committed = FIGURES_DIR / LOW_BETA_HOLDOUT_FIGURE
        before = committed.read_bytes()
        touched = committed.stat().st_mtime_ns
        make_low_beta_holdout_figure(
            out=tmp_path / LOW_BETA_HOLDOUT_FIGURE, chan=chan, ivv=ivv, sources=sources
        )
        assert committed.read_bytes() == before
        assert committed.stat().st_mtime_ns == touched

    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch) -> None:
        def refuse(*_a, **_k):
            raise HoldoutRefused("no archive here")

        monkeypatch.setattr(module, "make_low_beta_holdout_figure", refuse)
        with pytest.raises(SystemExit, match="^no archive here$") as stopped:
            main()
        assert isinstance(stopped.value.__cause__, HoldoutRefused)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(module, "make_low_beta_holdout_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    def test_main_reports_the_file_it_wrote(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(module, "make_low_beta_holdout_figure", lambda: None)
        main()
        assert capsys.readouterr().out == f"wrote {FIGURES_DIR / LOW_BETA_HOLDOUT_FIGURE}\n"


# --- the real right column, on the owner's archive ---------------------------------


@pytest.fixture(scope="module")
def holdout() -> Portfolios:
    """One run on the owner's archive, or a skip naming what is missing."""
    reason = archive_skip_reason()
    if reason is not None:
        pytest.skip(reason)
    return low_beta_holdout.read_holdout().portfolios


@pytest.fixture(scope="module")
def real(tmp_path_factory, sources, chan, holdout):
    out = tmp_path_factory.mktemp("low_beta_holdout_real") / LOW_BETA_HOLDOUT_FIGURE
    figure = make_low_beta_holdout_figure(out=out, chan=chan, ivv=holdout, sources=sources)
    return figure, _renderer(figure)


class TestTheRealRightColumn:
    """What the committed PNG's right column draws, read from the archive run."""

    def test_the_lines_are_the_holdouts_paths_by_holding_month(self, real, holdout) -> None:
        panels = _axes(real[0])
        for key, gid, series in (
            (("ivv", "beta"), "low", holdout.low_beta),
            (("ivv", "beta"), "high", holdout.high_beta),
            (("ivv", "k"), "k", holdout.leverage),
        ):
            line = _by_gid(panels[key].lines)[gid]
            assert _months(line).equals(pd.DatetimeIndex(holdout.held_to)), HOLDOUT_SPEC
            np.testing.assert_array_equal(line.get_ydata(), series.to_numpy())

    def test_the_lowest_kept_beta_and_the_highest_k_share_april_2025(self, real) -> None:
        panels = _axes(real[0])
        lowest = _by_gid(panels[("ivv", "beta")].texts)["lowest-label"]
        highest = _by_gid(panels[("ivv", "k")].texts)["highest-label"]
        assert lowest.xy[0] == highest.xy[0] == pd.Timestamp("2025-04-30"), HOLDOUT_SPEC
        assert lowest.get_text() == "lowest kept, 0.0563, formed 2025-03-31", HOLDOUT_SPEC
        assert highest.get_text() == "highest, 27.9727, formed 2025-03-31", HOLDOUT_SPEC

    def test_the_four_skipped_formations_are_plotted_and_shaded(self, real) -> None:
        panels = _axes(real[0])
        marker = _by_gid(panels[("ivv", "beta")].lines)["skipped"]
        assert list(marker.get_xdata()) == list(
            pd.DatetimeIndex(["2026-05-29", "2026-06-30", "2026-07-31", "2026-08-31"])
        ), HOLDOUT_SPEC
        assert [f"{b:.4f}" for b in marker.get_ydata()] == [
            "-0.0037",
            "-0.0652",
            "-0.1429",
            "-0.2083",
        ], HOLDOUT_SPEC
        label = _by_gid(panels[("ivv", "beta")].texts)["skipped-label"]
        assert label.get_text() == (
            "4 skipped, formed 2026-04-30 to 2026-07-31, low fifth's beta −0.0037 to −0.2083"
        ), HOLDOUT_SPEC
        shaded = (date2num(pd.Timestamp("2026-04-30")), date2num(pd.Timestamp("2026-08-31")))
        for row in ("beta", "k"):
            assert _shaded(panels[("ivv", row)]) == shaded, HOLDOUT_SPEC
            assert panels[("ivv", row)].get_xlim() == (
                date2num(pd.Timestamp("2009-01-30")),
                shaded[1],
            ), HOLDOUT_SPEC

    def test_no_month_is_ruined_and_december_2024_is_marked(self, real) -> None:
        ax = _axes(real[0])[("ivv", "k")]
        assert "ruined" not in _by_gid(ax.lines)
        marker = _by_gid(ax.lines)["worst"]
        assert list(marker.get_xdata()) == [pd.Timestamp("2024-12-31")], HOLDOUT_SPEC
        assert _by_gid(ax.texts)["worst-label"].get_text() == (
            "worst month 2024-12-31: k 12.3588,\nlevered return −0.8014"
        ), HOLDOUT_SPEC

    def test_the_headings(self, real) -> None:
        panels = _axes(real[0])
        assert _title(panels[("ivv", "beta")]) == (
            "IVV's members: each fifth's mean beta at formation.\nThe low fifth's fell to 0.0563, "
            "and 4 formations at or below zero are skipped."
        ), HOLDOUT_SPEC
        assert _title(panels[("ivv", "k")]) == (
            "IVV's members: k, the leverage that matches the high fifth's beta,\nmean 3.8247. "
            "No month lost the capital."
        ), HOLDOUT_SPEC

    def test_every_value_lies_inside_the_shared_limits(self, real, holdout) -> None:
        assert BETA_LIMITS[0] < min(s.low_beta for s in holdout.skipped), HOLDOUT_SPEC
        assert holdout.high_beta.max() < BETA_LIMITS[1], HOLDOUT_SPEC
        assert LEVERAGE_LIMITS[0] < holdout.leverage.min(), HOLDOUT_SPEC
        assert holdout.leverage.max() < LEVERAGE_LIMITS[1], HOLDOUT_SPEC

    def test_every_label_on_the_holdout_is_clear(self, real) -> None:
        figure, renderer = real
        assert_labels_clear({k: v for k, v in _axes(figure).items() if k[0] == "ivv"}, renderer)
