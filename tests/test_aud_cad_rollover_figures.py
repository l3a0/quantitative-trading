"""The pins for the figure in the post on AUD.CAD with rollover interest.

``tests/test_aud_cad_rollover.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, shaded the wrong days or mislabelled a panel fails even when the
arithmetic is right. Some numbers repeat here on purpose, because a figure's
labels are prose and the suite is the authority for every number prose quotes.
No test compares bytes, for the reason ``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_aud_cad_rollover.py`` states in its module docstring:
``pythoncodesanddata/inputData_AUDCAD_20120426.csv``, ``AUD_interestRate.csv``
and ``CAD_interestRate.csv``, all chan-py, saved 2018-12-13, and
``AUDCAD_daily.m`` at EpchanPreview ``e4bc46f`` as :mod:`chan.aud_cad_rollover`
transcribes it. A day's held position is ``lag1(position)``, the one
yesterday's z-score set, and the cumulative return is ``cumprod(1 + returns)
− 1``, the compounding line 49 of the script applies.

Exploratory, like everything Example 5.2 computes here.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color, to_rgb
from matplotlib.dates import date2num

from chan import aud_cad_rollover_figures
from chan.aud_cad_rollover import aud_cad_rollover, read_sources
from chan.aud_cad_rollover_figures import (
    CUMULATIVE_COLOURS,
    HELD_COLOURS,
    RATE_COLOURS,
    ROLLOVER_FIGURE,
    cumulative,
    held_position,
    main,
    make_rollover_figure,
    missing_months,
    spells,
)
from chan.matlab_helpers import lag1
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST, MUTED, RULE
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

JULY_2007 = pd.Timestamp("2007-07-01")


@pytest.fixture(scope="module")
def sources():
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return aud_cad_rollover(sources.closes[1], sources.aud[1], sources.cad[1])


@pytest.fixture(scope="module")
def held(result):
    return held_position(result)


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("aud_cad_rollover_figure") / ROLLOVER_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_rollover_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    rates, close, cumulative_ax = figure.axes
    return {"rates": rates, "close": close, "cumulative": cumulative_ax}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _shown(monthly: pd.Series) -> pd.Series:
    return monthly.loc[JULY_2007:]


class TestThePanels:
    def test_there_are_three_sharing_the_date_axis_from_july_2007(
        self, figure, axes, result
    ) -> None:
        assert len(figure.axes) == 3
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(JULY_2007), date2num(result.days[-1]))}
        rates = axes["rates"]
        for other in (axes["close"], axes["cumulative"]):
            assert rates.get_shared_x_axes().joined(rates, other)

    def test_the_y_axes_are_labelled(self, axes) -> None:
        assert [ax.get_ylabel() for ax in axes.values()] == [
            "rate, percent a year",
            "AUD.CAD close, CAD per AUD",
            "cumulative return",
        ]

    def test_the_title_carries_the_label_and_the_note_names_the_vintage(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: AUD.CAD with and without rollover interest, on Chan's own files"
        )
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Algorithmic Trading, Example 5.2, 2007-07-23 to 2012-04-26, 1,237 days. Closes "
            "from inputData_AUDCAD_20120426.csv,\nrates from AUD_interestRate.csv and "
            "CAD_interestRate.csv, Chan's Python port, saved 2018-12-13.\nChan chose the rule "
            "and the sample, and no cost is charged."
        ]

    def test_drawing_with_no_sources_reads_the_committed_files(self, tmp_path, result) -> None:
        """``main`` and the committed PNG take this path, so it is drawn here too."""
        drawn = make_rollover_figure(out=tmp_path / ROLLOVER_FIGURE)
        line = _by_gid(drawn.axes[2].lines)["with"]
        np.testing.assert_array_equal(line.get_ydata(), cumulative(result.returns))


class TestTheRates:
    def test_each_line_is_its_files_rates_from_july_2007(self, axes, sources) -> None:
        lines = _by_gid(axes["rates"].lines)
        for name, (_, monthly) in (("AUD", sources.aud), ("CAD", sources.cad)):
            shown = _shown(monthly)
            assert list(lines[name].get_xdata()) == list(shown.index)
            np.testing.assert_array_equal(lines[name].get_ydata(), shown.to_numpy())
        assert (len(_shown(sources.aud[1])), len(_shown(sources.cad[1]))) == (57, 54)

    def test_the_rates_peak_and_bottom_where_the_heading_says(self, sources) -> None:
        """Each at its first month, since AUD holds 3.00 and CAD 0.24 for several months.

        AUD's peak is the file's own number, which prints as 7.25 at two decimals.
        """
        aud, cad = _shown(sources.aud[1]), _shown(sources.cad[1])
        assert aud.max() == pytest.approx(7.25001675398684, abs=1e-12)
        assert aud.min() == 3.0
        assert cad.max() == 4.51
        assert cad.min() == 0.24
        assert [
            str(d.date()) for d in (aud.idxmax(), aud.idxmin(), cad.idxmax(), cad.idxmin())
        ] == [
            "2008-07-01",
            "2009-05-01",
            "2007-10-01",
            "2009-05-01",
        ]

    def test_the_missing_months_are_marked_at_zero(self, axes) -> None:
        lines = _by_gid(axes["rates"].lines)
        expected = {
            "AUD": ["2012-04-01"],
            "CAD": ["2012-01-01", "2012-02-01", "2012-03-01", "2012-04-01"],
        }
        for name, months in expected.items():
            missing = lines[f"{name}-missing"]
            assert [str(pd.Timestamp(x).date()) for x in missing.get_xdata()] == months
            assert list(missing.get_ydata()) == [0.0] * len(months)
            assert missing.get_markerfacecolor() == "none"
            assert missing.get_linestyle() == "None"

    def test_the_marked_months_are_the_days_the_run_reads_as_zero(self, result, sources) -> None:
        """The marks and the run's zero fill are one set of months, read two ways."""
        for monthly, daily in ((sources.aud[1], result.aud), (sources.cad[1], result.cad)):
            zero_months = sorted(set(result.days[daily == 0].to_period("M")))
            marked = missing_months(monthly, result.days).to_period("M")
            assert list(marked) == zero_months

    def test_a_dotted_drop_joins_each_last_month_to_its_zeros(self, axes, sources) -> None:
        lines = _by_gid(axes["rates"].lines)
        for name, (_, monthly) in (("AUD", sources.aud), ("CAD", sources.cad)):
            drop = lines[f"{name}-drop"]
            missing = list(_by_gid(axes["rates"].lines)[f"{name}-missing"].get_xdata())
            assert list(drop.get_xdata()) == [monthly.index[-1], *missing]
            assert list(drop.get_ydata()) == [monthly.iloc[-1]] + [0.0] * len(missing)
            assert drop.get_linestyle() == ":"

    def test_each_currency_keeps_one_colour_across_its_line_drop_and_rings(self, axes) -> None:
        """The legend is the only key to which currency is which."""
        lines = _by_gid(axes["rates"].lines)
        assert same_color(RATE_COLOURS["AUD"], ACCENT)
        assert same_color(RATE_COLOURS["CAD"], INK)
        for name, colour in RATE_COLOURS.items():
            assert same_color(lines[name].get_color(), colour)
            assert same_color(lines[f"{name}-drop"].get_color(), colour)
            assert same_color(lines[f"{name}-missing"].get_markeredgecolor(), colour)
        assert not same_color(RATE_COLOURS["AUD"], RATE_COLOURS["CAD"])

    def test_aud_s_ring_is_drawn_around_cad_s_in_april_2012(self, axes) -> None:
        """Both files lack April 2012, so equal rings would hide one behind the other."""
        lines = _by_gid(axes["rates"].lines)
        assert lines["AUD-missing"].get_markersize() > lines["CAD-missing"].get_markersize()

    def test_the_legend_names_each_line_and_each_ring_in_its_colour(self, axes) -> None:
        legend = axes["rates"].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == [
            "AUD",
            "AUD, month missing from the file, read as 0",
            "CAD",
            "CAD, month missing from the file, read as 0",
        ]
        handles = legend.legend_handles
        assert same_color(handles[0].get_color(), ACCENT)
        assert same_color(handles[1].get_markeredgecolor(), ACCENT)
        assert same_color(handles[2].get_color(), INK)
        assert same_color(handles[3].get_markeredgecolor(), INK)

    def test_the_heading_names_each_extreme(self, axes) -> None:
        assert _title(axes["rates"]) == (
            "The monthly rates from July 2007. AUD peaks at 7.25 in July 2008 and bottoms at "
            "3.00 in May 2009.\nCAD peaks at 4.51 in October 2007 and bottoms at 0.24 in May "
            "2009.\nThe script reads a month a file lacks as 0, drawn dotted to a hollow ring."
        )


def _spans(ax, gid: str) -> list[tuple[float, float]]:
    return [
        (patch.get_x(), patch.get_x() + patch.get_width())
        for patch in ax.patches
        if patch.get_gid() == gid
    ]


class TestTheHeldPositions:
    def test_the_held_position_is_yesterdays_sign(self, result, held) -> None:
        np.testing.assert_array_equal(held, lag1(result.position))
        assert np.isnan(held[:20]).all()
        assert not np.isnan(held[20:]).any()

    def test_the_close_line_is_the_file(self, axes, sources) -> None:
        close = _by_gid(axes["close"].lines)["close"]
        assert list(close.get_xdata()) == list(sources.closes[1].index)
        np.testing.assert_array_equal(close.get_ydata(), sources.closes[1].to_numpy())

    def test_the_close_runs_where_the_heading_says(self, sources, axes) -> None:
        closes = sources.closes[1]
        assert (closes.min(), str(closes.idxmin().date())) == (0.725, "2008-10-08")
        assert (closes.max(), str(closes.idxmax().date())) == (1.07555, "2012-02-08")
        assert _title(axes["close"]) == (
            "The AUD.CAD close, from 0.72500 on 2008-10-08 to 1.07555 on 2012-02-08.\n"
            "Shaded green on the 510 days held long and red on the 707 held short. The first "
            "20 days hold nothing."
        )

    def test_the_shading_covers_exactly_the_days_held_each_way(self, axes, result, held):
        """Each held day t is the stretch from close t − 1 to close t, shaded once."""
        index = {date2num(day): i for i, day in enumerate(result.days)}
        drawn = np.zeros(len(result.days))
        times = np.zeros(len(result.days), dtype=int)
        for gid, sign in (("long", 1.0), ("short", -1.0)):
            for left, right in _spans(axes["close"], gid):
                first, last = index[left] + 1, index[right]
                drawn[first : last + 1] = sign
                times[first : last + 1] += 1
        assert (times[:20] == 0).all()
        assert (times[20:] == 1).all()
        np.testing.assert_array_equal(drawn[20:], np.sign(held[20:]))
        assert (np.count_nonzero(drawn > 0), np.count_nonzero(drawn < 0)) == (510, 707)

    def test_each_spell_is_a_maximal_run(self, axes) -> None:
        """Adjacent spells alternate, so the count of patches is the count of reversals plus one."""
        ordered = sorted(
            (left, gid) for gid in ("long", "short") for left, _ in _spans(axes["close"], gid)
        )
        sides = [gid for _, gid in ordered]
        assert all(a != b for a, b in zip(sides, sides[1:], strict=False))
        assert len(sides) == 181

    def test_the_first_20_days_are_shaded_as_holding_nothing(self, axes, result) -> None:
        (unfilled,) = _spans(axes["close"], "unfilled")
        assert unfilled == (date2num(result.days[0]), date2num(result.days[19]))

    def test_long_is_green_short_is_red_and_the_unfilled_days_grey(self, axes) -> None:
        """No legend tells the two apart, so the colour and the heading are the claim."""
        assert same_color(HELD_COLOURS["long"], GOOD)
        assert same_color(HELD_COLOURS["short"], LOST)
        for gid, colour in (("long", GOOD), ("short", LOST), ("unfilled", RULE)):
            patches = [p for p in axes["close"].patches if p.get_gid() == gid]
            assert patches
            for patch in patches:
                assert same_color(to_rgb(patch.get_facecolor()), colour), gid

    def test_spells_merge_consecutive_days_and_skip_the_unfilled(self) -> None:
        found = spells(np.array([np.nan, np.nan, 1.0, 1.0, -1.0, 1.0, 1.0, 1.0]))
        assert [(s.side, s.first, s.last) for s in found] == [
            ("long", 2, 3),
            ("short", 4, 4),
            ("long", 5, 7),
        ]


class TestTheCumulativeReturns:
    def test_each_line_is_its_returns_compounded_as_the_script_does(self, axes, result) -> None:
        lines = _by_gid(axes["cumulative"].lines)
        for gid, returns in (("with", result.returns), ("without", result.without)):
            assert list(lines[gid].get_xdata()) == list(result.days)
            np.testing.assert_array_equal(lines[gid].get_ydata(), np.cumprod(1 + returns) - 1)
        assert list(lines["zero"].get_ydata()) == [0, 0]

    def test_each_line_ends_at_its_apr_compounded_over_1237_days(self, axes, result) -> None:
        lines = _by_gid(axes["cumulative"].lines)
        for gid, figures, end in (
            ("with", result.with_rollover, 0.3407952416),
            ("without", result.without_rollover, 0.3757290374),
        ):
            last = lines[gid].get_ydata()[-1]
            assert last == pytest.approx((1 + figures.apr) ** (1237 / 252) - 1, abs=1e-12)
            assert last == pytest.approx(end, abs=1e-10)

    def test_the_deepest_fall_is_from_2008_07_30_to_2008_10_08_on_both(self, axes, result):
        """The dip a reader sees in October 2008, the close's own low."""
        lines = _by_gid(axes["cumulative"].lines)
        for gid, depth in (("with", -0.2486008485), ("without", -0.2545382718)):
            wealth = 1 + np.asarray(lines[gid].get_ydata())
            fall = wealth / np.maximum.accumulate(wealth) - 1
            trough = int(fall.argmin())
            peak = int(wealth[: trough + 1].argmax())
            assert fall[trough] == pytest.approx(depth, abs=1e-10)
            assert (str(result.days[peak].date()), str(result.days[trough].date())) == (
                "2008-07-30",
                "2008-10-08",
            )

    def test_with_is_ink_and_solid_without_is_muted_and_dashed(self, axes) -> None:
        """The legend tells them apart by colour and dash, so both are the claim."""
        lines = _by_gid(axes["cumulative"].lines)
        assert same_color(CUMULATIVE_COLOURS["with"], INK)
        assert same_color(CUMULATIVE_COLOURS["without"], MUTED)
        assert same_color(lines["with"].get_color(), INK)
        assert same_color(lines["without"].get_color(), MUTED)
        assert (lines["with"].get_linestyle(), lines["without"].get_linestyle()) == ("-", "--")
        legend = axes["cumulative"].get_legend()
        assert [t.get_text() for t in legend.get_texts()] == ["with rollover interest", "without"]
        for handle, gid in zip(legend.legend_handles, ("with", "without"), strict=True):
            assert same_color(handle.get_color(), lines[gid].get_color())
            assert handle.get_linestyle() == lines[gid].get_linestyle()

    def test_the_heading_sets_where_each_ends(self, axes) -> None:
        assert _title(axes["cumulative"]) == (
            "Each day's log return compounded as if it were simple, as the script does.\n"
            "With rollover interest it ends at 34.08 percent, and without it at 37.57 percent."
        )


class TestTheFile:
    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.exists() and out.stat().st_size > 0

    def test_drawing_to_out_leaves_the_committed_figure_alone(self, tmp_path, sources) -> None:
        committed = FIGURES_DIR / ROLLOVER_FIGURE
        before = committed.read_bytes()
        make_rollover_figure(out=tmp_path / ROLLOVER_FIGURE, sources=sources)
        assert committed.read_bytes() == before

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / ROLLOVER_FIGURE).is_file()

    def test_main_turns_a_missing_vintage_into_one_line(self, monkeypatch, tmp_path) -> None:
        """The data directory is emptied, so the first read refuses."""
        from chan import paths

        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert isinstance(stopped.value.__cause__, VintageUnavailable)
        assert "\n" not in str(stopped.value)

    def test_main_lets_any_other_error_through_as_itself(self, monkeypatch) -> None:
        def fail(*_a, **_k):
            raise ValueError("a bug, not a refusal")

        monkeypatch.setattr(aud_cad_rollover_figures, "make_rollover_figure", fail)
        with pytest.raises(ValueError, match="a bug, not a refusal"):
            main()

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage is inputData_AUDCAD_20120426.csv"),
            WindowCrossesScaleBreak("inputData_AUDCAD_20120426.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(aud_cad_rollover_figures, "make_rollover_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)
