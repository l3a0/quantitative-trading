"""The pins for the figure in the post on AUD.USD against CAD.USD, Example 5.1.

``tests/test_aud_cad_johansen.py`` holds what the run computes. This file holds
that the figure draws those numbers, so a generator that plotted the wrong
series, shaded the wrong days, marked the wrong windows or compounded the wrong
rows fails even when the arithmetic is right. Some numbers repeat here on
purpose, because a figure's labels are prose and the suite is the authority for
every number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The figure reads the vintage and the specification
``tests/test_aud_cad_johansen.py``'s docstring names, which :data:`SPEC` carries
into every failure message here: ``inputData_AUDUSD_20120426.csv`` and
``inputData_USDCAD_20120426.csv``, chan-py, raw, saved 2018-12-12, and
``AUDCAD_unequal.m`` at EpchanPreview ``e4bc46f``.

Exploratory, like everything Example 5.1 computes here.
"""

from __future__ import annotations

import shutil

import numpy as np
import pandas as pd
import pytest
from matplotlib.colors import same_color
from matplotlib.dates import DateFormatter, YearLocator, date2num, num2date

from chan import aud_cad_johansen, paths
from chan import aud_cad_johansen_figures as figures
from chan.aud_cad_johansen import Sources, aud_cad, cross_rates, read_sources
from chan.aud_cad_johansen_figures import (
    AUD_CAD_FIGURE,
    cumulative_return,
    main,
    make_aud_cad_figure,
    signed,
    spells,
)
from chan.paths import FIGURES_DIR
from chan.regime_figure import ACCENT, GOOD, INK, LOST
from chan.series import WindowCrossesScaleBreak
from chan.vintage import VintageUnavailable

SPEC = (
    "inputData_AUDUSD_20120426.csv and inputData_USDCAD_20120426.csv, chan-py, raw, saved "
    "2018-12-12; AUDCAD_unequal.m at EpchanPreview e4bc46f"
)
FIRST, LAST = pd.Timestamp("2009-12-18"), pd.Timestamp("2012-04-26")


@pytest.fixture(scope="module")
def sources() -> Sources:
    return read_sources()


@pytest.fixture(scope="module")
def result(sources):
    return aud_cad(cross_rates(sources.audusd[1], sources.usdcad[1]))


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("aud_cad_figure") / AUD_CAD_FIGURE


@pytest.fixture(scope="module")
def figure(out, sources):
    return make_aud_cad_figure(out=out, sources=sources)


@pytest.fixture(scope="module")
def axes(figure):
    split, cumulative = figure.axes
    return {"split": split, "return": cumulative}


def _by_gid(artists) -> dict:
    return {a.get_gid(): a for a in artists if a.get_gid()}


def _title(ax) -> str:
    return ax.get_title(loc="left")


def _days(line) -> list[pd.Timestamp]:
    return [pd.Timestamp(d) for d in line.get_xdata()]


class TestThePanels:
    def test_there_are_two_in_the_order_the_post_reads_them(self, figure, axes) -> None:
        assert len(figure.axes) == 2
        assert _title(axes["split"]).startswith("Each day's hedge in dollars")
        assert _title(axes["return"]).startswith("The cumulative return")

    def test_they_share_the_date_axis_over_the_612_test_days(self, axes, result) -> None:
        days = result.test_days
        assert len(days) == 612, SPEC
        assert (days[0], days[-1]) == (FIRST, LAST), SPEC
        limits = {ax.get_xlim() for ax in axes.values()}
        assert limits == {(date2num(FIRST), date2num(LAST))}, SPEC
        assert axes["split"].get_shared_x_axes().joined(axes["split"], axes["return"])

    def test_a_tick_falls_on_every_year_from_2010_to_2012(self, axes) -> None:
        axis = axes["return"].xaxis
        assert isinstance(axis.get_major_locator(), YearLocator)
        assert isinstance(axis.get_major_formatter(), DateFormatter)
        assert axis.get_major_formatter().fmt == "%Y"
        low, high = axes["return"].get_xlim()
        shown = [t for t in axis.get_major_locator()() if low <= t <= high]
        assert [num2date(t).year for t in shown] == [2010, 2011, 2012], SPEC

    def test_the_title_carries_the_exploratory_label(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "Exploratory: AUD.USD against CAD.USD redrawn on Chan's own daily closes"
        )

    def test_the_note_names_the_files_the_window_and_the_rule(self, figure) -> None:
        assert [t.get_text() for t in figure.texts if t is not figure._suptitle] == [
            "Example 5.1 of Algorithmic Trading, 2009-12-18 to 2012-04-26, after 250 days of "
            "training.\nCloses from pythoncodesanddata/inputData_AUDUSD_20120426.csv and\n"
            "pythoncodesanddata/inputData_USDCAD_20120426.csv, saved 2018-12-12.\nEach day's "
            "hedge is fitted on the 250 days before it and held in units of minus a 20-day "
            "z-score."
        ], SPEC

    def test_no_label_names_a_figure_number_from_the_book(self, figure) -> None:
        """The post's caption cites the book's Figure 5.1, so the image itself cites none."""
        words = [t.get_text() for t in figure.texts]
        for ax in figure.axes:
            words += [ax.get_title(loc="left"), ax.get_title(), *ax.get_legend_handles_labels()[1]]
        assert len(words) == 9
        assert not any("Figure" in w or "figure 5." in w for w in words)

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        for ax in figure.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in figure.texts:
            assert text.get_parse_math() is False


class TestTheDollarSplit:
    def test_the_line_is_the_runs_dollar_split(self, axes, result) -> None:
        line = _by_gid(axes["split"].lines)["split"]
        assert _days(line) == list(result.test_days), SPEC
        np.testing.assert_array_equal(line.get_ydata(), result.dollar_split)

    def test_it_ends_at_minus_0_4325(self, axes) -> None:
        last = _by_gid(axes["split"].lines)["split"].get_ydata()[-1]
        assert last == pytest.approx(-0.4325417813, abs=1e-10), SPEC

    def test_lines_mark_zero_and_equal_dollars(self, axes) -> None:
        lines = _by_gid(axes["split"].lines)
        assert list(lines["zero"].get_ydata()) == [0, 0]
        assert list(lines["equal-dollars"].get_ydata()) == [-0.5, -0.5]
        assert axes["split"].get_ylim() == (-1.05, 1.05)

    def test_the_shaded_spans_are_the_seven_runs_of_same_way_days(self, axes, result) -> None:
        """Each band runs to the next test day, so the one-day run of 2010-06-01 shows."""
        days = result.test_days
        bands = sorted(
            (p for p in axes["split"].patches if (p.get_gid() or "").startswith("same-way-")),
            key=lambda p: p.get_x(),
        )
        expected = [
            ("2010-06-01", "2010-06-02"),
            ("2010-06-03", "2010-06-07"),
            ("2010-06-10", "2010-06-15"),
            ("2010-06-16", "2010-07-06"),
            ("2010-07-07", "2010-10-06"),
            ("2011-10-28", "2011-11-02"),
            ("2011-11-04", "2011-11-08"),
        ]
        drawn = [
            (str(num2date(b.get_x()).date()), str(num2date(b.get_x() + b.get_width()).date()))
            for b in bands
        ]
        assert drawn == expected, SPEC
        for band in bands:
            assert same_color(band.get_facecolor()[:3], LOST)
        shaded = sum(len(days[(days >= a) & (days < b)]) for a, b in expected)
        assert shaded == 90, SPEC

    def test_the_dots_are_the_trace_tests_windows_one_and_two_apart(self, axes, result):
        lines = _by_gid(axes["split"].lines)
        days, split = result.test_days, result.dollar_split
        for gid, count, n in (("one-relation", 1, 7), ("two-relations", 2, 19)):
            found = result.trace_relations == count
            assert _days(lines[gid]) == list(days[found]), (gid, SPEC)
            np.testing.assert_array_equal(lines[gid].get_ydata(), split[found])
            assert len(lines[gid].get_ydata()) == n, (gid, SPEC)

    def test_one_relation_is_hollow_ink_and_two_is_filled_red(self, axes) -> None:
        lines = _by_gid(axes["split"].lines)
        assert same_color(lines["one-relation"].get_color(), INK)
        assert lines["one-relation"].get_markerfacecolor() == "none"
        assert same_color(lines["two-relations"].get_color(), LOST)
        assert same_color(lines["two-relations"].get_markerfacecolor(), LOST)
        assert same_color(lines["split"].get_color(), ACCENT)

    def test_the_legend_names_the_line_and_both_marks(self, axes) -> None:
        legend = [t.get_text() for t in axes["split"].get_legend().get_texts()]
        assert legend == [
            "CAD.USD's share",
            "trace test finds 1 relation",
            "trace test finds 2 relations",
        ]

    def test_the_heading_sets_the_scale_the_counts_and_the_last_day(self, axes) -> None:
        assert _title(axes["split"]) == (
            "Each day's hedge in dollars. At −0.5 the two legs hold equal dollars against each "
            "other,\nand above 0 they are held the same way, which the shaded 90 days did.\nThe "
            "dots are the 26 of 612 windows where the trace test found a relation at 95 "
            "percent,\n19 of them two. The last day split 1 to −0.7622, long AUD.USD."
        ), SPEC
        assert axes["split"].get_ylabel() == "CAD.USD's share of the gross, AUD.USD long"


class TestTheCumulativeReturn:
    def test_the_line_is_cumprod_of_the_612_test_returns(self, axes, result) -> None:
        line = _by_gid(axes["return"].lines)["cumulative"]
        assert _days(line) == list(result.test_days), SPEC
        expected = np.cumprod(1 + result.test) - 1
        np.testing.assert_array_equal(line.get_ydata(), expected)
        np.testing.assert_array_equal(cumulative_return(result).to_numpy(), expected)

    def test_it_ends_at_the_apr_compounded_over_612_days(self, axes, result) -> None:
        last = _by_gid(axes["return"].lines)["cumulative"].get_ydata()[-1]
        assert last == pytest.approx(0.2952620351, abs=1e-10), SPEC
        assert last == pytest.approx((1 + result.figures.apr) ** (612 / 252) - 1, rel=1e-12)

    def test_it_starts_at_zero_on_the_first_test_day(self, axes) -> None:
        """Row 251's return is 0, as Chan's first saved return is."""
        assert _by_gid(axes["return"].lines)["cumulative"].get_ydata()[0] == 0

    def test_a_line_marks_zero_and_the_curve_is_green(self, axes) -> None:
        lines = _by_gid(axes["return"].lines)
        assert list(lines["zero"].get_ydata()) == [0, 0]
        assert same_color(lines["cumulative"].get_color(), GOOD)

    def test_the_heading_sets_the_total_and_the_apr(self, axes) -> None:
        assert _title(axes["return"]) == (
            "The cumulative return over the 612 test days, ending at 0.295, an APR of 0.112.\n"
            "Unlevered, before costs and without rollover interest."
        ), SPEC
        assert axes["return"].get_ylabel() == "cumulative return, compounded"


class TestTheHelpers:
    def test_spells_finds_each_run_including_one_at_either_end(self) -> None:
        mask = np.array([True, False, True, True, False, False, True])
        assert spells(mask) == [(0, 0), (2, 3), (6, 6)]
        assert spells(np.zeros(3, dtype=bool)) == []

    def test_signed_prints_a_true_minus_sign(self) -> None:
        assert signed(-0.7622442800, 4) == "−0.7622"
        assert signed(0.2952620351) == "0.295"


class TestTheReadPath:
    def test_drawing_with_no_sources_reads_the_runs_path(self, monkeypatch, tmp_path, sources):
        asked = []

        def read():
            asked.append(True)
            return sources

        monkeypatch.setattr(figures, "read_sources", read)
        make_aud_cad_figure(out=tmp_path / AUD_CAD_FIGURE)
        assert asked == [True]

    def test_sources_handed_in_are_the_sources_drawn(self, tmp_path, sources, result) -> None:
        """AUD.USD raised by 0.01, so a figure that ignored the argument and read the files
        would fail. Scaling a leg would not do, because the return cancels a scale."""
        entry, closes = sources.audusd
        shifted = Sources(audusd=(entry, closes + 0.01), usdcad=sources.usdcad, saved=sources.saved)
        drawn = make_aud_cad_figure(out=tmp_path / AUD_CAD_FIGURE, sources=shifted)
        line = _by_gid(drawn.axes[1].lines)["cumulative"]
        again = aud_cad(cross_rates(closes + 0.01, sources.usdcad[1]))
        np.testing.assert_array_equal(line.get_ydata(), np.cumprod(1 + again.test) - 1)
        assert not np.array_equal(line.get_ydata(), np.cumprod(1 + result.test) - 1)

    def test_the_guard_runs_on_the_default_path(self, monkeypatch, tmp_path) -> None:
        def refuse(legs, *, start, end):
            raise WindowCrossesScaleBreak("inputData_AUDUSD_20120426.csv changes scale")

        monkeypatch.setattr(aud_cad_johansen, "refuse_window_crossing_a_break", refuse)
        with pytest.raises(WindowCrossesScaleBreak, match="changes scale"):
            make_aud_cad_figure(out=tmp_path / AUD_CAD_FIGURE)

    def test_a_missing_vintage_reaches_the_operator_as_one_line(
        self, monkeypatch, tmp_path
    ) -> None:
        """The manifest is copied and the files are not, so the refusal names the file."""
        shutil.copy(paths.DATA_DIR / "vintages.jsonl", tmp_path)
        monkeypatch.setattr(paths, "DATA_DIR", tmp_path)
        with pytest.raises(SystemExit) as stopped:
            main()
        message = str(stopped.value)
        assert message.startswith("pythoncodesanddata/inputData_AUDUSD_20120426.csv: ")
        assert "\n" not in message

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageUnavailable("no committed vintage of AUDUSD saved 2018-12-12"),
            WindowCrossesScaleBreak("inputData_USDCAD_20120426.csv changes scale"),
        ],
    )
    def test_a_refusal_reaches_the_operator_as_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*_a, **_k):
            raise refusal

        monkeypatch.setattr(figures, "make_aud_cad_figure", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == str(refusal)

    def test_any_other_error_keeps_its_traceback(self, monkeypatch) -> None:
        def broken(*_a, **_k):
            raise KeyError("Close")

        monkeypatch.setattr(figures, "make_aud_cad_figure", broken)
        with pytest.raises(KeyError, match="Close"):
            main()

    def test_the_command_writes_the_committed_path(self, monkeypatch, capsys) -> None:
        drawn = []
        monkeypatch.setattr(figures, "make_aud_cad_figure", lambda **kw: drawn.append(kw))
        main()
        assert drawn == [{}]
        assert f"wrote {FIGURES_DIR / AUD_CAD_FIGURE}" in capsys.readouterr().out

    def test_drawing_writes_the_file_it_is_given(self, figure, out) -> None:
        assert out.is_file() and out.stat().st_size > 0


def test_the_committed_figure_exists() -> None:
    assert (FIGURES_DIR / AUD_CAD_FIGURE).is_file()
