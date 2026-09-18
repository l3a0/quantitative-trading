"""The pins for the guard: which committed series change scale, and what stops on one.

A verified vintage is not the same thing as a series it is safe to compute
across. The bytes can be exactly what the manifest recorded while the series
means one thing before a day and another after it, and ``ko_chan.csv`` is that
case rather than a hypothetical. So these cases hold two claims. The guard
reads each committed series against itself and reports the days it changed
scale, and a run whose window spans one of those days stops instead of
printing a number.

The case order is the order the rules appear on
[issue 3](https://github.com/l3a0/quantitative-trading/issues/3), which is the
convention ``tests/test_vintage.py`` states for itself against issue 1.

This is its own file rather than more of ``tests/test_series.py``, whose
subject is which vintage a run resolves and that it is that one, or of
``tests/test_vintage.py``, whose every case is driven by a synthetic series.
A guard over the committed eight is neither, and the repo's shape is one file
per concern.

Every refusal is asserted on its message and not only on its type. Absent,
unreadable, altered and never-recorded are the four ``tests/test_series.py``
tells apart, and a window crossing a scale break is a fifth problem with a
fifth fix.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from chan import paths
from chan.pair_cointegration import aligned_closes
from chan.series import (
    SCALE_BREAK_BOUND,
    WindowCrossesScaleBreak,
    load_vintage,
    manifest_scale_breaks,
    refuse_window_crossing_a_break,
    scale_breaks,
)
from chan.vintage import MANIFEST_NAME, VintageUnavailable, read_manifest, record_vintage
from tests.support.committed_vintages import committed_copy as copy_the_committed_tree
from tests.support.committed_vintages import rewrite_entry

#: The breaks the eight committed vintages carry today, recorded rather than failing.
#:
#: Two day-over-day moves in ``ko_chan.csv`` are near-exact halvings, 1.0100 to
#: 0.5100 across 1965-02-19 at a ratio of 0.5050 and 1.0700 to 0.5400 across
#: 1968-06-03 at 0.5047. They are real, so the guard's first run on `main` is
#: red unless they are written down, and this is where they are written down.
#: That they are 2:1 splits is the obvious reading and is not verified here,
#: because nothing in this repo holds a corporate-action feed. The finding does
#: not rest on the label: a near-exact halving is a scale break whichever it
#: was.
#:
#: Nothing computes across them. The KO/PEP replication reads the intersection
#: with ``pep_chan.csv``, which starts 1977-01-03, so both breaks fall outside
#: every window anything reads, which
#: ``TestAWindowThatCrossesABreakStops`` runs rather than asserts in prose.
#: Recording the fact beside the data is
#: [issue 108](https://github.com/l3a0/quantitative-trading/issues/108).
KNOWN_BREAKS = {"ko_chan.csv": ["1965-02-19", "1968-06-03"]}

#: A series that halves partway through, and its date index.
#:
#: Four days is the smallest set that carries a break with an ordinary move on
#: either side of it, which is what separates a guard that flags the break from
#: one that flags everything.
DAYS = ["2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07"]
HALVES = [10.0, 10.5, 5.2, 5.3]


def series_of(closes: list[float], *, days: list[str] = DAYS) -> pd.Series:
    """``closes`` as the reader hands a series back, date-indexed and named."""
    return pd.Series(
        closes, index=pd.DatetimeIndex([pd.Timestamp(day) for day in days]), name="ZZZ"
    )


def days_of(flagged: list[pd.Timestamp]) -> list[str]:
    """Flagged timestamps as the ISO dates a pin is written in."""
    return [str(day.date()) for day in flagged]


def payload_of(rows: list[tuple[str, str]]) -> bytes:
    """The bytes a recorded vintage holds, with the close left as written text.

    Text rather than a float, because two of the cases below need a close no
    float can carry: a value ``_parse_close`` coerces to NaN, and a negative
    one. Neither survives ``record_vintage``, which is why these are written
    into a manifest by hand the way the eight committed ones were.
    """
    return ("Date,Close\n" + "".join(f"{day},{close}\n" for day, close in rows)).encode("utf-8")


def place(directory: Path, *, name: str, rows: list[tuple[str, str]]) -> None:
    """Leave one vintage in ``directory``, the way the eight were left in ``data/``."""
    payload = payload_of(rows)
    days = [day for day, _ in rows]
    entry = {
        "vendor": "yfinance",
        "symbol": "ZZZ",
        "price_basis": "adjusted",
        "first_date": min(days),
        "last_date": max(days),
        "path": name,
        "row_count": len(rows),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "download_date": "2026-02-01",
        "saved_date": None,
    }
    with open(directory / MANIFEST_NAME, "a", encoding="utf-8") as manifest:
        manifest.write(json.dumps(entry, sort_keys=True) + "\n")
    (directory / name).write_bytes(payload)


def halve_one_close(directory: Path, *, named: str, on: str) -> None:
    """Halve one close in a committed vintage's copy and repair its recorded hash.

    The span and the row count do not move, so the entry needs only its sha256
    rewritten. What this produces is two breaks rather than one: the day the
    close halves and the day it comes back.
    """
    path = directory / named
    lines = path.read_text(encoding="utf-8").splitlines()
    for number, line in enumerate(lines):
        if line.startswith(f"{on},"):
            day, close = line.split(",")[:2]
            lines[number] = f"{day},{float(close) / 2}"
            break
    else:
        raise AssertionError(f"{named} carries no row for {on}")
    payload = "".join(line + "\n" for line in lines).encode("utf-8")
    path.write_bytes(payload)
    rewrite_entry(directory, named, sha256=hashlib.sha256(payload).hexdigest())


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    """An empty data directory with an empty manifest, never the committed one."""
    directory = tmp_path / "data"
    directory.mkdir()
    (directory / MANIFEST_NAME).write_text("", encoding="utf-8")
    return directory


@pytest.fixture
def committed_copy(tmp_path: Path) -> Path:
    """The eight committed vintages, copied, so a case may break one."""
    return copy_the_committed_tree(tmp_path)


@pytest.fixture
def halved(committed_copy: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """The committed tree with one GLD close halved, pointed at by the default.

    ``gld_20yr_prices_unadjusted.csv`` is the leg both entry points read, so one
    edit reaches the replication and the figure. ``main`` takes no data
    directory, because it is a command line rather than a library call, so this
    moves the default the way ``tests/test_series.py`` does for the same reason.
    """
    halve_one_close(committed_copy, named="gld_20yr_prices_unadjusted.csv", on="2007-01-03")
    monkeypatch.setattr(paths, "DATA_DIR", committed_copy)
    return committed_copy


class TestTheGuardOverTheWholeManifest:
    """Rule 1. What the eight committed vintages carry, pinned as a count and as dates.

    The cost is not pinned with it. A wall-clock figure is a property of the
    machine rather than of this code, measured at 46.4 ms here. Neither is the
    number of passes over each series, since asserting one would mean counting
    operations or patching the parse, which is more machinery than the property
    is worth.
    """

    def test_the_whole_manifest_flags_exactly_the_two_known_breaks(self) -> None:
        found = manifest_scale_breaks()

        assert {path: days_of(days) for path, days in found.items()} == KNOWN_BREAKS
        assert sum(len(days) for days in found.values()) == 2

    def test_the_seven_other_committed_vintages_are_clean(self) -> None:
        """Said as its own case, because a guard that flagged nothing would pass the count."""
        flagged = set(manifest_scale_breaks())

        assert {entry.path for entry in read_manifest()} - flagged == {
            "gld_20yr_prices.csv",
            "gld_20yr_prices_unadjusted.csv",
            "gdx_20yr_prices.csv",
            "gdx_20yr_prices_unadjusted.csv",
            "gld_chan.csv",
            "gdx_chan.csv",
            "pep_chan.csv",
        }


class TestItSortsBeforeItDifferences:
    """Rule 2. The recorder writes rows in the order it is handed them, on purpose.

    ``_serialize``'s docstring says the file is meant to be what the vendor
    returned, so a vendor answering newest-first produces a vintage committed
    backwards. Differencing that reports every ratio inverted: a fully reversed
    ``ko_chan.csv`` still flags 2, because 0.5050 inverts to about 1.98 and that
    is over the bound too, so a count alone would not notice. The dates are what
    moves, and the dates are what these assert.
    """

    def test_a_series_handed_over_backwards_flags_the_day_the_scale_moved(self) -> None:
        forwards = scale_breaks(series_of(HALVES))
        backwards = scale_breaks(series_of(HALVES)[::-1])

        assert days_of(forwards) == ["2026-01-06"]
        assert days_of(backwards) == days_of(forwards)

    def test_a_shuffled_series_flags_the_same_day(self) -> None:
        """A reversal is one permutation. A guard sorting only the ends would pass it."""
        shuffled = series_of(HALVES).iloc[[2, 0, 3, 1]]

        assert days_of(scale_breaks(shuffled)) == ["2026-01-06"]

    def test_a_vintage_committed_backwards_reads_the_same_way_end_to_end(
        self, data_dir: Path
    ) -> None:
        """``_parse_close`` already sorts, so this pins the whole read rather than the guard."""
        rows = [(day, repr(close)) for day, close in zip(DAYS, HALVES, strict=True)]
        place(data_dir, name="backwards.csv", rows=list(reversed(rows)))

        _, closes = load_vintage("ZZZ", data_dir=data_dir)

        assert days_of(scale_breaks(closes)) == ["2026-01-06"]

    def test_the_two_known_breaks_are_recorded_rather_than_failing(self) -> None:
        """The guard's first run on `main` is red without this list, and the flags are real."""
        _, closes = load_vintage("KO", chan=True)

        assert days_of(scale_breaks(closes)) == KNOWN_BREAKS["ko_chan.csv"]


class TestANonFiniteRatioIsReportedNotSkipped:
    """Rule 3. "No break" and "could not tell" must not be the same answer.

    ``chan.vintage._unrecorded`` already writes that rule down for its own
    scan. Here it decides how the comparison is spelled. ``NaN > bound`` is
    ``False``, so a guard written that way reports a clean series over a close
    it could not read anything from, and numpy emits no warning saying so.
    """

    def test_a_nan_close_is_flagged_on_both_days_it_touches(self, data_dir: Path) -> None:
        """``_parse_close`` coerces an unparseable value to NaN, which the eight predate."""
        place(
            data_dir,
            name="unreadable.csv",
            rows=[("2026-01-02", "100"), ("2026-01-05", "n/a"), ("2026-01-06", "52")],
        )

        _, closes = load_vintage("ZZZ", data_dir=data_dir)

        assert closes.isna().sum() == 1
        assert days_of(scale_breaks(closes)) == ["2026-01-05", "2026-01-06"]

    def test_a_negative_close_is_flagged_although_both_inputs_are_finite(self) -> None:
        """Its ratio's log is NaN out of two numbers ``_validated_rows`` would accept."""
        negative = series_of([10.0, -10.0, 11.0], days=DAYS[:3])

        assert days_of(scale_breaks(negative)) == ["2026-01-05", "2026-01-06"]

    def test_a_zero_close_is_flagged_and_warns_nobody(self) -> None:
        """``_validated_rows`` allows ``0.0``, which a vendor returns for a halted day.

        The ratios are ``0.0`` and ``inf``, both correctly flagged, and numpy
        raises a ``RuntimeWarning`` computing them. Turning warnings into
        errors here is what holds the suppression: without it this case fails
        rather than passing quietly.
        """
        halted = series_of([10.0, 0.0, 11.0], days=DAYS[:3])

        with warnings.catch_warnings():
            warnings.simplefilter("error")
            flagged = scale_breaks(halted)

        assert days_of(flagged) == ["2026-01-05", "2026-01-06"]

    def test_a_series_too_short_to_difference_reports_nothing(self) -> None:
        """One row has no day-over-day move, which is not the same as an unreadable one."""
        assert scale_breaks(series_of([10.0], days=DAYS[:1])) == []
        assert scale_breaks(series_of([], days=[])) == []


class TestItIteratesTheManifest:
    """Rule 4. A ninth vintage is covered on the day it is recorded.

    ``COMMITTED`` in ``tests/test_series.py`` is a hand-written list of eight
    and ``TestTheCommittedManifest`` iterates ``read_manifest()`` instead. The
    guard follows the second, so this records a ninth carrying a break and asks
    whether the scan found it. A list of eight passes every other case in this
    file and fails this one.
    """

    def test_a_recorded_ninth_carrying_a_break_is_found(self, committed_copy: Path) -> None:
        assert not [e for e in read_manifest(committed_copy) if e.symbol == "ZZZ"]
        entry = record_vintage(
            list(zip(DAYS, HALVES, strict=True)),
            vendor="yfinance",
            symbol="ZZZ",
            price_basis="adjusted",
            download_date="2026-09-18",
            data_dir=committed_copy,
        )

        found = manifest_scale_breaks(committed_copy)

        assert days_of(found[entry.path]) == ["2026-01-06"]
        assert {path: days_of(days) for path, days in found.items()} == {
            **KNOWN_BREAKS,
            entry.path: ["2026-01-06"],
        }

    def test_the_result_is_keyed_by_path_rather_than_by_entry(self) -> None:
        """An entry carries an unhashable field, so keying by one reaches an operator
        as a traceback, which is
        [issue 93](https://github.com/l3a0/quantitative-trading/issues/93)."""
        assert all(isinstance(key, str) for key in manifest_scale_breaks())


class TestAWindowThatCrossesABreakStops:
    """Rule 5. Four windows, because a containment test against a flag list passes one.

    The guard run on the clipped series is the straddle test, so there is no
    flag table to match a window against. That matters in the third case below,
    where the flagged row is gone and the halving is still in the window, one
    day later. A precomputed list of flagged dates finds nothing there.
    """

    @pytest.fixture
    def ko(self) -> tuple[object, pd.Series]:
        return load_vintage("KO", chan=True)

    def test_a_window_straddling_a_break_refuses(self, ko) -> None:
        entry, closes = ko

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(entry, closes)],
                start=pd.Timestamp("1965-02-01"),
                end=pd.Timestamp("1965-03-31"),
            )

        message = str(refused.value)
        assert "ko_chan.csv" in message
        assert "1965-02-19" in message
        assert "\n" not in message

    def test_a_window_starting_on_the_break_runs(self, ko) -> None:
        """The flagged date is the later of the two days, so a window opening there
        does not contain the move."""
        entry, closes = ko

        assert (
            refuse_window_crossing_a_break(
                [(entry, closes)],
                start=pd.Timestamp("1965-02-19"),
                end=pd.Timestamp("1965-03-31"),
            )
            is None
        )

    def test_a_window_whose_flagged_row_was_removed_still_refuses(self, ko) -> None:
        entry, closes = ko
        without = closes.drop(pd.Timestamp("1965-02-19"))

        with pytest.raises(WindowCrossesScaleBreak) as refused:
            refuse_window_crossing_a_break(
                [(entry, without)],
                start=pd.Timestamp("1965-02-01"),
                end=pd.Timestamp("1965-03-31"),
            )

        assert "1965-02-23" in str(refused.value)

    def test_the_default_ko_pep_window_runs(self) -> None:
        """Both KO breaks are in the 1960s and PEP starts in 1977, so nothing crosses one."""
        joined = aligned_closes("KO", "PEP", chan=True)

        assert str(joined.index[0].date()) == "1977-01-03"
        assert not joined.empty

    def test_the_check_reads_the_window_it_returns_and_not_the_one_it_was_asked_for(
        self,
    ) -> None:
        """The intersection with PEP is narrower than a 1962 start, and a check
        reading the argument would refuse a run that reads nothing wrong."""
        joined = aligned_closes("KO", "PEP", chan=True, start="1962-01-01")

        assert str(joined.index[0].date()) == "1977-01-03"

    def test_the_replication_reader_refuses_a_crossing_window(self, halved: Path) -> None:
        """The wiring, not the guard. ``aligned_closes`` is where the clip happens."""
        with pytest.raises(WindowCrossesScaleBreak) as refused:
            aligned_closes("GLD", "GDX", unadjusted=True, data_dir=halved)

        message = str(refused.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message

    def test_a_window_clear_of_the_halving_still_runs(self, halved: Path) -> None:
        """A refusal that fired on the whole vintage rather than the window passes
        the case above and fails this one."""
        joined = aligned_closes("GLD", "GDX", unadjusted=True, start="2011-01-03", data_dir=halved)

        assert not joined.empty


class TestTheRefusalIsAType:
    """Rule 6. Caught by both ``main`` functions, and told apart from the other refusal.

    A vintage being unavailable and a window crossing a break are two problems
    with two fixes. ``chan.vintage`` already argues that sharing an exception
    hands the next reader a docstring describing something that did not happen,
    and that argument is why ``VintageRefused`` sits beside ``VintageUnavailable``.
    """

    def test_it_is_not_a_kind_of_vintage_unavailable(self) -> None:
        assert not issubclass(WindowCrossesScaleBreak, VintageUnavailable)
        assert not issubclass(VintageUnavailable, WindowCrossesScaleBreak)

    def test_the_replication_command_prints_a_line(
        self, halved: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from chan import pair_cointegration

        monkeypatch.setattr(sys, "argv", ["chan.pair_cointegration", "--ch7"])
        with pytest.raises(SystemExit) as stopped:
            pair_cointegration.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message
        assert "\n" not in message

    def test_the_figure_command_prints_a_line(self, halved: Path) -> None:
        from chan import regime_figure

        with pytest.raises(SystemExit) as stopped:
            regime_figure.main()

        message = str(stopped.value)
        assert "gld_20yr_prices_unadjusted.csv" in message
        assert "2007-01-03" in message
        assert "\n" not in message


class TestTheBoundIsTheOneThatWasMeasured:
    """The envelope the eight committed vintages actually span, run rather than quoted.

    The bound is computed from 1.6 rather than typed as 0.4700, because a price
    ratio is multiplicative and ``[0.6, 1.6]`` is asymmetric by 0.0408 in log
    terms. A guard built on a pair of endpoints answers differently on a series
    and on the same series reversed, which is the property the first case here
    holds.
    """

    def test_it_is_the_log_of_one_point_six(self) -> None:
        assert SCALE_BREAK_BOUND == math.log(1.6)

    def test_a_move_and_its_reciprocal_are_judged_the_same(self) -> None:
        """0.62 and 1.613 straddle ``[0.6, 1.6]`` and sit the same side of this bound."""
        rising = series_of([10.0, 16.13], days=DAYS[:2])
        falling = series_of([16.13, 10.0], days=DAYS[:2])

        assert days_of(scale_breaks(rising)) == ["2026-01-05"]
        assert days_of(scale_breaks(falling)) == ["2026-01-05"]

    def test_black_monday_is_not_a_scale_break(self) -> None:
        """The widest legitimate move across all eight, at 0.7521, in the same file."""
        _, closes = load_vintage("KO", chan=True)

        assert "1987-10-19" not in days_of(scale_breaks(closes))

    def test_the_siblings_band_would_miss_both_ko_breaks(self) -> None:
        """``[0.5, 2.0]`` is deliberately not ported. It runs on already-adjusted
        closes next door, where a correct split leaves no cliff at all, and both
        breaks here sit inside it at 0.5050 and 0.5047."""
        _, closes = load_vintage("KO", chan=True)

        assert scale_breaks(closes, bound=math.log(2.0)) == []

    def test_the_committed_ratios_leave_a_margin_on_both_sides(self) -> None:
        """What carries forward to a ninth vintage is this derivation, not the number.

        Every number the prose quotes about the envelope is derived here, which
        is the single-authority rule. ``docs/design.md``'s register and
        ``chan.series``'s own docstring state these and never recompute them.
        One of them is corrected against the issue that specified it: the
        smaller break is 0.68329 and rounds to 0.6833, where
        [issue 3](https://github.com/l3a0/quantitative-trading/issues/3) prints
        the truncation 0.6832.
        """
        widest, breaks, ratios = 0.0, [], []
        for entry in read_manifest():
            _, closes = load_vintage(
                entry.symbol,
                unadjusted=entry.price_basis == "raw",
                chan=entry.vendor == "chan-xls",
            )
            values = closes.to_numpy(dtype=float)
            moves = values[1:] / values[:-1]
            magnitudes = np.abs(np.log(moves))
            flagged = magnitudes > SCALE_BREAK_BOUND
            widest = max(widest, float(magnitudes[~flagged].max()))
            breaks.extend(magnitudes[flagged])
            ratios.extend(moves[flagged])

        assert round(widest, 4) == 0.2849
        assert [round(float(one), 4) for one in sorted(breaks)] == [0.6833, 0.6838]
        assert sorted(round(float(one), 4) for one in ratios) == [0.5047, 0.5050]
        assert widest < SCALE_BREAK_BOUND < min(breaks)

    def test_a_band_of_endpoints_would_judge_the_same_move_two_ways(self) -> None:
        """The 0.0408 the register quotes, derived rather than restated.

        ``[0.6, 1.6]`` is the band the bound would have been written as. Its two
        endpoints are that far apart in log terms, which is the whole of why the
        bound is on the log instead."""
        assert round(abs(math.log(0.6)) - abs(math.log(1.6)), 4) == 0.0408


class TestWhyTheComparisonDetectorWasCut:
    """The rejected detector's decisive number, pinned so the design doc can quote it.

    Comparing a symbol's raw vintage against its adjusted one was the other
    candidate for noticing a split. A split rescales both bases together, so
    dividing one by the other cancels exactly the thing being looked for, and
    what is left is dividend drift. ``docs/design.md``'s register carries the
    reasoning and this carries the number, because a cheap check nobody wrote
    down gets re-derived from scratch and the same dead end costs the same
    afternoon twice.
    """

    def test_dividing_gdx_adjusted_by_gdx_raw_moves_too_little_to_detect_anything(
        self,
    ) -> None:
        adjusted = load_vintage("GDX")[1]
        raw = load_vintage("GDX", unadjusted=True)[1]

        ratio = (
            pd.concat([adjusted, raw], axis=1, join="inner")
            .dropna()
            .pipe(lambda both: both.iloc[:, 0] / both.iloc[:, 1])
        )
        widest = float(ratio.diff().abs().max())

        assert round(widest, 4) == 0.0163
        assert widest < 1 - math.exp(-SCALE_BREAK_BOUND)
