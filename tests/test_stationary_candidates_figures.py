"""The pins for the stationary-candidates post's three figures.

``tests/test_stationary_candidates.py`` holds what the two drawn candidates
compute. This file holds that the figures draw those numbers against the right
bars, so a generator that put a statistic on the wrong line or a bar at the wrong value
fails even when the arithmetic is right. The bars figure comes first,
``TestTheLags`` holds the lag-count figure, and ``TestTheWindows`` holds the
rolling-scan figure. Some numbers repeat here on purpose,
because a figure's labels are prose and the suite is the authority for every
number prose quotes. No test compares bytes, for the reason
``tests/test_regime_figure.py`` gives.

The vintages and specifications are the ones that file states at its head:
``CADAUD=X`` on the log from 2007-08-06, and TLT against IEF on raw closes over
their shared history, all downloaded 2026-10-02.
"""

from __future__ import annotations

import dataclasses

import pytest
from ithildincore.timeseries import ADF_CRIT_CONST, EG_CRIT_N2
from matplotlib.colors import to_rgba

from chan.paths import FIGURES_DIR
from chan.stationary_candidates import cross_rate, fixed_income, residuals_pass
from chan.stationary_candidates_figures import (
    ACCENT,
    BARS_FIGURE,
    GOOD,
    INK,
    LAGS_FIGURE,
    LEVELS,
    LOST,
    MUTED,
    ONE_SERIES_Y,
    PAIR_Y,
    WINDOWS_FIGURE,
    X_RANGE,
    lag_sweep,
    make_bars_figure,
    make_lags_figure,
    make_windows_figure,
    marks,
)
from chan.vintage import VintageUnavailable


@pytest.fixture(scope="module")
def fixed():
    return fixed_income()


@pytest.fixture(scope="module")
def measured(fixed):
    return cross_rate(), fixed[1]


@pytest.fixture(scope="module")
def out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("stationary_figures") / BARS_FIGURE


@pytest.fixture(scope="module")
def figure(out, measured):
    rate, orientations = measured
    return make_bars_figure(out=out, rate=rate, orientations=orientations)


def _by_gid(figure) -> dict:
    ax = figure.axes[0]
    return {a.get_gid(): a for a in [*ax.lines, *ax.collections] if a.get_gid()}


def _rgb(colour) -> tuple[float, float, float]:
    return tuple(to_rgba(colour)[:3])


class TestTheBars:
    """Each table on its own line, at the values the run reads it against."""

    @pytest.mark.parametrize(
        ("name", "y", "table"), [("adf", ONE_SERIES_Y, ADF_CRIT_CONST), ("eg", PAIR_Y, EG_CRIT_N2)]
    )
    def test_each_bar_sits_at_its_constant_on_its_own_line(self, figure, name, y, table) -> None:
        artists = _by_gid(figure)
        for level in LEVELS:
            bar = artists[f"bar-{name}-{level}"]
            assert set(bar.get_xdata()) == {table[level]}
            assert min(bar.get_ydata()) < y < max(bar.get_ydata())

    def test_the_bars_are_the_two_tables_the_post_quotes(self) -> None:
        """The post's Lesson 2 quotes all six, so they are held here by value
        and not only by name."""
        assert [ADF_CRIT_CONST[level] for level in LEVELS] == [-3.43, -2.86, -2.57]
        assert [EG_CRIT_N2[level] for level in LEVELS] == [-3.9, -3.34, -3.04]

    def test_each_bar_is_labelled_with_its_level_and_value(self, figure) -> None:
        labels = [t.get_text() for t in figure.axes[0].texts[:6]]
        assert labels == [
            "1%\n−3.43",
            "5%\n−2.86",
            "10%\n−2.57",
            "1%\n−3.90",
            "5%\n−3.34",
            "10%\n−3.04",
        ]

    @pytest.mark.parametrize(("name", "y"), [("adf", ONE_SERIES_Y), ("eg", PAIR_Y)])
    def test_each_line_and_its_shading_sit_at_its_own_height(self, figure, name, y) -> None:
        artists = _by_gid(figure)
        rule = artists[f"axis-{name}"]
        assert tuple(rule.get_xdata()) == X_RANGE
        assert tuple(rule.get_ydata()) == (y, y)
        ys = artists[f"shade-{name}"].get_paths()[0].vertices[:, 1]
        assert ys.min() < y < ys.max()
        assert _rgb(artists[f"shade-{name}"].get_facecolor()[0]) == _rgb(GOOD)

    def test_the_bars_wear_the_muted_ink_and_their_labels_sit_above_them(self, figure) -> None:
        artists = _by_gid(figure)
        anchors = [t.xy for t in figure.axes[0].texts[:6]]
        expected = []
        for name, y, table in (("adf", ONE_SERIES_Y, ADF_CRIT_CONST), ("eg", PAIR_Y, EG_CRIT_N2)):
            for level in LEVELS:
                assert _rgb(artists[f"bar-{name}-{level}"].get_color()) == _rgb(MUTED)
                expected.append((table[level], y + 0.16))
        assert anchors == [pytest.approx(xy) for xy in expected]

    @pytest.mark.parametrize(("name", "table"), [("adf", ADF_CRIT_CONST), ("eg", EG_CRIT_N2)])
    def test_the_shading_runs_from_the_left_edge_to_the_five_percent_bar(
        self, figure, name, table
    ) -> None:
        path = _by_gid(figure)[f"shade-{name}"].get_paths()[0]
        xs = path.vertices[:, 0]
        assert xs.min() == pytest.approx(X_RANGE[0])
        assert xs.max() == pytest.approx(table["5%"])


class TestTheMarks:
    """Each statistic on the line whose bars it is read against."""

    def test_the_rate_sits_on_the_one_series_line_at_both_statistics(
        self, figure, measured
    ) -> None:
        rate, _ = measured
        artists = _by_gid(figure)
        for gid, stat in (
            ("mark-cadaud-1", rate.adf_stat),
            ("mark-cadaud-passing", rate.passing.adf_stat),
        ):
            assert (artists[gid].get_xdata()[0], artists[gid].get_ydata()[0]) == (
                stat,
                ONE_SERIES_Y,
            )

    def test_the_pair_sits_on_the_pair_line_in_both_orientations(self, figure, measured) -> None:
        _, orientations = measured
        by = {o.dependent: o for o in orientations}
        artists = _by_gid(figure)
        for gid, leg in (("mark-tlt-on-ief", "TLT"), ("mark-ief-on-tlt", "IEF")):
            assert (artists[gid].get_xdata()[0], artists[gid].get_ydata()[0]) == (
                by[leg].fit.adf_stat,
                PAIR_Y,
            )

    def test_the_rate_is_drawn_again_hollow_on_the_pair_line(self, figure, measured) -> None:
        """Lesson 2 in the picture: the same two statistics, read against the
        pair's bars, fall short of its 5% bar."""
        rate, _ = measured
        artists = _by_gid(figure)
        for gid, stat in (
            ("mark-cadaud-1-as-pair", rate.adf_stat),
            ("mark-cadaud-passing-as-pair", rate.passing.adf_stat),
        ):
            mark = artists[gid]
            assert (mark.get_xdata()[0], mark.get_ydata()[0]) == (stat, PAIR_Y)
            assert mark.get_markerfacecolor() == "none"
            assert _rgb(mark.get_markeredgecolor()) == _rgb(GOOD)
            assert EG_CRIT_N2["5%"] < stat < ADF_CRIT_CONST["5%"]

    def test_the_filled_marks_wear_the_verdict_colours(self, figure) -> None:
        artists = _by_gid(figure)
        for gid in ("mark-cadaud-1", "mark-cadaud-passing"):
            assert _rgb(artists[gid].get_markerfacecolor()) == _rgb(GOOD)
        for gid in ("mark-tlt-on-ief", "mark-ief-on-tlt"):
            assert _rgb(artists[gid].get_markerfacecolor()) == _rgb(LOST)

    def test_each_mark_is_labelled_with_its_own_numbers(self, figure) -> None:
        assert [t.get_text() for t in figure.axes[0].texts[6:]] == [
            "CAD/AUD, 1 lag\n−3.2136",
            "CAD/AUD, 10 lags\n−2.9946",
            "TLT on IEF\n−2.3887",
            "IEF on TLT\n−2.3168",
            "CAD/AUD's two, read\nagainst these bars",
        ]

    def test_each_label_is_anchored_at_its_own_mark(self, figure) -> None:
        labelled = [m for m in figure.marks if m.label]
        assert len(figure.marks) == 6
        assert [t.xy for t in figure.axes[0].texts[6:]] == [(m.x, m.y) for m in labelled]

    def test_the_passing_label_reads_the_lag_count_the_run_found(self, measured) -> None:
        """The real search stops at 10, so a label hard-coding 10 would pass
        on the real data. A result whose search stopped elsewhere holds it."""
        rate, orientations = measured
        moved = dataclasses.replace(rate, passing=dataclasses.replace(rate.passing, lags=7))
        labels = [m.label for m in marks(moved, orientations)]
        assert "CAD/AUD, 7 lags\n−2.9946" in labels

    def test_every_mark_is_inside_the_axis(self, figure) -> None:
        """The post's alt text quotes the range, so the constant is held by
        value as well as by what it has to contain."""
        assert X_RANGE == (-4.1, -2.0)
        assert figure.axes[0].get_xlim() == X_RANGE
        for mark in figure.marks:
            assert X_RANGE[0] < mark.x < X_RANGE[1]


class TestTheText:
    def test_the_title_states_the_finding(self, figure) -> None:
        assert figure._suptitle.get_text() == (
            "CAD/AUD clears the one-series bar at 5%, "
            "and the same statistics fall short of the pair's"
        )

    def test_the_note_names_the_vintages_and_what_the_marks_mean(self, figure) -> None:
        note = figure.texts[-1].get_text()
        assert "CADAUD=X, log of the rate, 2007-08-06 to 2026-09-30." in note
        assert "TLT and IEF raw closes, 2002-07-30 to 2026-10-01." in note
        assert "All downloaded 2026-10-02." in note
        assert "Shaded: past the 5% bar." in note
        assert note.endswith(
            "Hollow: CAD/AUD's two statistics read against the pair's bars, "
            "which pay for a fitted hedge ratio."
        )

    def test_the_axes_show_both_lines_every_bar_and_their_names(self, figure) -> None:
        ax = figure.axes[0]
        low, high = ax.get_ylim()
        assert low < PAIR_Y < ONE_SERIES_Y < high
        left, right = ax.get_xlim()
        for table in (ADF_CRIT_CONST, EG_CRIT_N2):
            assert all(left < table[level] < right for level in LEVELS)
        ticks = dict(
            zip(ax.get_yticks(), (t.get_text() for t in ax.get_yticklabels()), strict=True)
        )
        assert ticks == {
            ONE_SERIES_Y: "one series,\nADF with a constant",
            PAIR_Y: "a fitted pair,\nEngle-Granger",
        }
        assert ax.get_xlabel() == (
            "t-statistic, where further left is stronger evidence of a stationary series or spread"
        )

    def test_no_label_is_parsed_as_math(self, figure) -> None:
        """The bar labels carry percent signs, so math parsing stays off the
        way it does for the other figures."""
        for text in [*figure.axes[0].texts, *figure.texts]:
            assert text.get_parse_math() is False


def test_the_command_draws_every_figure_from_one_read(monkeypatch, capsys) -> None:
    """The figures read the same three vintages, so the command reads them
    once and hands the same results to each."""
    import chan.stationary_candidates_figures as figures

    rate, fixed, drawn = object(), (None, ("orientations",)), []
    monkeypatch.setattr(figures, "cross_rate", lambda: rate)
    monkeypatch.setattr(figures, "fixed_income", lambda: fixed)
    monkeypatch.setattr(figures, "make_bars_figure", lambda **kw: drawn.append(("bars", kw)))
    monkeypatch.setattr(figures, "make_windows_figure", lambda **kw: drawn.append(("windows", kw)))
    monkeypatch.setattr(figures, "make_lags_figure", lambda **kw: drawn.append(("lags", kw)))
    figures.main()
    assert drawn == [
        ("bars", {"rate": rate, "orientations": fixed[1]}),
        ("windows", {"rate": rate, "fixed": fixed}),
        ("lags", {"rate": rate, "orientations": fixed[1]}),
    ]
    out = capsys.readouterr().out
    assert BARS_FIGURE in out and WINDOWS_FIGURE in out and LAGS_FIGURE in out


def test_drawing_the_bars_figure_writes_the_file_it_is_given(figure, out) -> None:
    assert out.is_file()


def test_a_missing_vintage_reaches_the_operator_as_a_line(monkeypatch) -> None:
    """The command reads the same vintages as the candidates' own, so a
    missing download ends in the refusal's own sentence, not a traceback."""
    import chan.stationary_candidates_figures as figures

    def refuse(*_, **__):
        raise VintageUnavailable("no CADAUD=X vintage recorded")

    monkeypatch.setattr(figures, "cross_rate", refuse)
    with pytest.raises(SystemExit, match="no CADAUD=X vintage recorded"):
        figures.main()


def test_the_committed_bars_figure_exists() -> None:
    assert (FIGURES_DIR / BARS_FIGURE).is_file()


@pytest.fixture(scope="module")
def windows_out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("stationary_windows") / WINDOWS_FIGURE


@pytest.fixture(scope="module")
def windows(windows_out, measured, fixed):
    return make_windows_figure(out=windows_out, rate=measured[0], fixed=fixed)


def _lines(ax) -> dict:
    return {line.get_gid(): line for line in ax.lines if line.get_gid()}


class TestTheWindows:
    """The rolling scans the two candidates already run, drawn on one date axis.

    The counts repeat ``TestTheCrossRateScan::test_the_counts`` and
    ``TestTheRollingScan::test_the_counts``, because the post's Lesson 4 quotes
    them beside this figure."""

    def test_the_rate_panel_draws_the_rate_s_scan_at_its_window_ends(
        self, windows, measured
    ) -> None:
        rate, _ = measured
        line = _lines(windows.axes[0])["scan-cadaud"]
        dates = rate.log_rate.index[rate.scan.end_idx]
        assert list(line.get_ydata()) == list(rate.scan.adf_stat)
        assert list(line.get_xdata()) == list(dates)
        assert str(dates[0].date()) == "2008-07-30"
        assert _rgb(line.get_color()) == _rgb(INK)

    def test_the_pair_panel_draws_both_orientations(self, windows, fixed) -> None:
        closes, orientations = fixed
        lines = _lines(windows.axes[1])
        for o, gid, colour in (
            (orientations[0], "scan-tlt-on-ief", INK),
            (orientations[1], "scan-ief-on-tlt", ACCENT),
        ):
            line = lines[gid]
            assert list(line.get_ydata()) == list(o.scan.adf_stat)
            assert list(line.get_xdata()) == list(closes.index[o.scan.end_idx])
            assert line.get_label() == f"{o.dependent} on {o.independent}"
            assert _rgb(line.get_color()) == _rgb(colour)

    @pytest.mark.parametrize(
        ("panel", "gid", "bar", "count"),
        [
            (0, "cadaud", ADF_CRIT_CONST["10%"], 23),
            (1, "tlt-on-ief", EG_CRIT_N2["10%"], 56),
            (1, "ief-on-tlt", EG_CRIT_N2["10%"], 51),
        ],
    )
    def test_a_dot_marks_each_window_past_the_10_percent_bar(
        self, windows, panel, gid, bar, count
    ) -> None:
        lines = _lines(windows.axes[panel])
        scan, dots = lines[f"scan-{gid}"], lines[f"clears-{gid}"]
        past = scan.get_ydata() < bar
        assert len(dots.get_xdata()) == int(past.sum()) == count
        assert list(dots.get_xdata()) == list(scan.get_xdata()[past])
        assert list(dots.get_ydata()) == list(scan.get_ydata()[past])
        assert _rgb(dots.get_color()) == _rgb(scan.get_color())

    @pytest.mark.parametrize(
        ("panel", "name", "table"), [(0, "adf", ADF_CRIT_CONST), (1, "eg", EG_CRIT_N2)]
    )
    def test_each_panel_draws_its_own_bars(self, windows, panel, name, table) -> None:
        ax = windows.axes[panel]
        lines = _lines(ax)
        for level, style in (("10%", "--"), ("5%", ":")):
            bar = lines[f"bar-{name}-{level}"]
            assert set(bar.get_ydata()) == {table[level]}
            assert bar.get_linestyle() == style
            assert _rgb(bar.get_color()) == _rgb(LOST)
        assert {g for g in lines if g.startswith("bar-")} == {f"bar-{name}-10%", f"bar-{name}-5%"}

    def test_the_legend_names_each_orientation_in_its_line_s_colour(self, windows) -> None:
        legend = windows.axes[1].get_legend()
        named = {
            t.get_text(): _rgb(h.get_color())
            for t, h in zip(legend.get_texts(), legend.legend_handles, strict=True)
        }
        assert named == {"TLT on IEF": _rgb(INK), "IEF on TLT": _rgb(ACCENT)}

    def test_the_bar_labels_name_each_level(self, windows) -> None:
        assert [t.get_text() for t in windows.axes[0].texts] == ["10%  −2.57", "5%  −2.86"]
        assert [t.get_text() for t in windows.axes[1].texts] == ["10%  −3.04", "5%  −3.34"]
        for ax in windows.axes:
            assert [t.get_verticalalignment() for t in ax.texts] == ["bottom", "top"]

    def test_each_panel_title_gives_the_whole_span_result(self, windows) -> None:
        assert windows.axes[0].get_title(loc="left") == (
            "CAD/AUD, one series. Over the whole test period the test rejects at 5%, "
            "with t = −3.2136."
        )
        assert windows.axes[1].get_title(loc="left") == (
            "TLT and IEF, a fitted pair. Over the whole period it does not reject even at 10%:\n"
            "−2.3887 for TLT on IEF, −2.3168 for IEF on TLT."
        )

    def test_the_panels_share_one_date_axis(self, windows) -> None:
        top, bottom = windows.axes[:2]
        assert top.get_shared_x_axes().joined(top, bottom)
        assert bottom.get_xlabel() == "date the one-year window ends"
        assert [ax.get_ylabel() for ax in (top, bottom)] == ["one-year t-statistic"] * 2

    def test_the_title_and_note_say_what_a_window_is_not(self, windows) -> None:
        assert windows._suptitle.get_text() == (
            "How often one-year windows reject says little about the whole test period"
        )
        assert windows.texts[-1].get_text() == (
            "Windows of 252 trading days stepped by 21, one lag. "
            "Dots mark windows past the 10% bar.\n"
            "CADAUD=X, log of the rate, from 2007-08-06. "
            "TLT and IEF raw closes from 2002-07-30. All downloaded 2026-10-02.\n"
            "A window that clears a bar is one look at the data among many, "
            "not a finding about the candidate."
        )

    def test_no_label_is_parsed_as_math(self, windows) -> None:
        for ax in windows.axes:
            for text in [*ax.texts, ax.title, ax._left_title]:
                assert text.get_parse_math() is False
        for text in windows.texts:
            assert text.get_parse_math() is False

    def test_drawing_writes_the_file_it_is_given(self, windows, windows_out) -> None:
        assert windows_out.is_file()

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / WINDOWS_FIGURE).is_file()


@pytest.fixture(scope="module")
def lags_out(tmp_path_factory: pytest.TempPathFactory):
    return tmp_path_factory.mktemp("stationary_lags") / LAGS_FIGURE


@pytest.fixture(scope="module")
def lags(lags_out, measured):
    rate, orientations = measured
    return make_lags_figure(out=lags_out, rate=rate, orientations=orientations)


@pytest.fixture(scope="module")
def sweeps(measured):
    rate, orientations = measured
    by = {o.dependent: o for o in orientations}
    return {
        "cadaud": lag_sweep(rate.log_rate.to_numpy(float), rate.ceiling, "c"),
        "tlt-on-ief": lag_sweep(by["TLT"].fit.spread, by["TLT"].ceiling, "n"),
        "ief-on-tlt": lag_sweep(by["IEF"].fit.spread, by["IEF"].ceiling, "n"),
    }


class TestTheLags:
    """The statistic at every lag count up to the ceiling, for Lesson 3.

    The first passing counts and their statistics repeat
    ``TestTheCrossRateResidualCheck`` and ``TestTheResidualCheck``, because the
    figure labels them."""

    def test_the_sweeps_are_the_search_the_candidates_run(self, sweeps, measured) -> None:
        """Each sweep runs from 0 to its ceiling, and its first passing fit is
        the one the candidate's own search returns."""
        rate, orientations = measured
        by = {o.dependent: o for o in orientations}
        for gid, ceiling, passing in (
            ("cadaud", 32, rate.passing),
            ("tlt-on-ief", 34, by["TLT"].passing),
            ("ief-on-tlt", 34, by["IEF"].passing),
        ):
            checks = sweeps[gid]
            assert [c.lags for c in checks] == list(range(ceiling + 1))
            first = next(c for c in checks if residuals_pass(c))
            assert (first.lags, first.adf_stat) == (passing.lags, passing.adf_stat)
        assert sweeps["cadaud"][1].adf_stat == pytest.approx(rate.adf_stat, abs=1e-12)

    @pytest.mark.parametrize(
        ("panel", "gid", "colour"),
        [(0, "cadaud", INK), (1, "tlt-on-ief", INK), (1, "ief-on-tlt", ACCENT)],
    )
    def test_each_lag_count_is_filled_exactly_when_its_residuals_pass(
        self, lags, sweeps, panel, gid, colour
    ) -> None:
        lines = _lines(lags.axes[panel])
        checks = sweeps[gid]
        line = lines[f"sweep-{gid}"]
        assert list(line.get_xdata()) == [c.lags for c in checks]
        assert list(line.get_ydata()) == [c.adf_stat for c in checks]
        assert _rgb(line.get_color()) == _rgb(colour)
        filled, hollow = lines[f"pass-{gid}"], lines[f"fail-{gid}"]
        passed = [c for c in checks if residuals_pass(c)]
        failed = [c for c in checks if not residuals_pass(c)]
        assert list(filled.get_xdata()) == [c.lags for c in passed]
        assert list(filled.get_ydata()) == [c.adf_stat for c in passed]
        assert list(hollow.get_xdata()) == [c.lags for c in failed]
        assert list(hollow.get_ydata()) == [c.adf_stat for c in failed]
        assert _rgb(filled.get_markerfacecolor()) == _rgb(colour)
        assert hollow.get_markerfacecolor() == "none"
        assert _rgb(hollow.get_markeredgecolor()) == _rgb(colour)

    def test_every_rate_fit_rejects_at_5_percent_as_the_panel_title_says(self, sweeps) -> None:
        stats = [c.adf_stat for c in sweeps["cadaud"]]
        assert max(stats) < ADF_CRIT_CONST["5%"]
        assert max(stats) == pytest.approx(-2.8739, abs=5e-5)

    def test_the_rate_fails_the_check_below_10_lags_and_again_at_23_to_25(self, sweeps) -> None:
        """The post's alt text names both stretches of hollow dots."""
        failed = [c.lags for c in sweeps["cadaud"] if not residuals_pass(c)]
        assert failed == [*range(10), 23, 24, 25]

    def test_no_pair_fit_reaches_the_10_percent_bar_as_the_panel_title_says(self, sweeps) -> None:
        """The lowest statistic in either sweep is the one-lag fit's."""
        for gid, one_lag in (("tlt-on-ief", -2.3887), ("ief-on-tlt", -2.3168)):
            stats = [c.adf_stat for c in sweeps[gid]]
            assert min(stats) > EG_CRIT_N2["10%"]
            assert min(stats) == pytest.approx(one_lag, abs=5e-5) == stats[1]
            assert [c.lags for c in sweeps[gid] if residuals_pass(c)] == [31, 32, 33, 34]

    def test_the_first_passing_fits_are_labelled_where_they_sit(self, lags) -> None:
        labelled = [
            (t.get_text(), t.xy) for ax in lags.axes[:2] for t in ax.texts if "pass" in t.get_text()
        ]
        assert [text for text, _ in labelled] == [
            "CAD/AUD, first passes at 10 lags, −2.9946",
            "TLT on IEF, first passes at 31 lags, −1.5677",
            "IEF on TLT, first passes at 31 lags, −1.5387",
        ]
        assert [xy[0] for _, xy in labelled] == [10, 31, 31]
        assert [round(xy[1], 4) for _, xy in labelled] == [-2.9946, -1.5677, -1.5387]

    @pytest.mark.parametrize(
        ("panel", "name", "table"), [(0, "adf", ADF_CRIT_CONST), (1, "eg", EG_CRIT_N2)]
    )
    def test_each_panel_draws_its_own_bars(self, lags, panel, name, table) -> None:
        lines = _lines(lags.axes[panel])
        for level in ("10%", "5%"):
            assert set(lines[f"bar-{name}-{level}"].get_ydata()) == {table[level]}
        assert {g for g in lines if g.startswith("bar-")} == {f"bar-{name}-10%", f"bar-{name}-5%"}

    def test_the_legend_names_each_orientation_in_its_line_s_colour(self, lags) -> None:
        legend = lags.axes[1].get_legend()
        named = {
            t.get_text(): _rgb(h.get_color())
            for t, h in zip(legend.get_texts(), legend.legend_handles, strict=True)
        }
        assert named == {"TLT on IEF": _rgb(INK), "IEF on TLT": _rgb(ACCENT)}

    def test_the_text_says_what_each_panel_shows(self, lags) -> None:
        top, bottom = lags.axes[:2]
        assert top.get_title(loc="left") == (
            "CAD/AUD. The first fit that passes sits nearer the 5% bar, and every count up to "
            "32 still rejects at 5%."
        )
        assert bottom.get_title(loc="left") == (
            "TLT and IEF. The first fits that pass sit further from both bars than the one-lag "
            "fits, and no count reaches the 10% bar."
        )
        assert [ax.get_ylabel() for ax in (top, bottom)] == ["t-statistic"] * 2
        assert top.get_shared_x_axes().joined(top, bottom)
        assert bottom.get_xlabel() == "lag count, the number of earlier changes the ADF includes"
        assert lags._suptitle.get_text() == (
            "The check for leftover autocorrelation decides which lag count's statistic is read"
        )
        assert lags.texts[-1].get_text() == (
            "Each dot is one ADF fit over the whole test period. Filled: its residuals pass "
            "both halves of the check, a Breusch-Godfrey p-value above 0.10\n"
            "and all ten autocorrelations inside ±1.96/√n. Hollow: they fail. "
            "The search stops at Schwert's ceiling, rounded up as statsmodels rounds it."
        )
        for ax in lags.axes:
            for text in [*ax.texts, ax._left_title]:
                assert text.get_parse_math() is False

    def test_drawing_writes_the_file_it_is_given(self, lags, lags_out) -> None:
        assert lags_out.is_file()

    def test_the_committed_figure_exists(self) -> None:
        assert (FIGURES_DIR / LAGS_FIGURE).is_file()
