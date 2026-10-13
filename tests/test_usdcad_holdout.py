"""Issue 607's holdout of Example 2.5 on USD/CAD: the command, the run's rules, and the pins.

This file is the single authority for every number any prose surface quotes
about [issue 607](https://github.com/l3a0/quantitative-trading/issues/607).
``docs/replication-log.md`` Entry 51 carries the verdict and points here.
``blog/usdcad-holdout-lessons.md`` quotes most of these figures, so a change to
an assertion here moves that post too. ``TestWhatThePostMeasured`` holds the
numbers it added after the run, and ``tests/test_usdcad_holdout_figures.py``
holds what its figure draws.

Every pin on the committed closes reads one vintage under one specification,
so both are stated once here and carried in every figure's failure message as
:data:`SPEC`.

- **Vintage.** ``alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv``,
  Alpha Vantage's ``FX_DAILY`` close for USD/CAD, downloaded 2026-10-13,
  5,000 rows from 2007-08-10 to 2026-10-12, sha256
  ``9792b44c3491c1c3ab3cdfb61b073e221a4022811e36dca2823d127f95c4f067``. It is
  committed in ``data/``, so CI runs every pin here.
- **Specification.** Example 2.5's rule as
  :func:`chan.usdcad_mean_reversion.linear_mean_reversion` computes it, at the
  lookback of 115 days fixed from Chan's 2007 to 2012 closes and never
  re-estimated. It runs over the 115 closes before 2012-03-29 and every close
  after, and the traded days are ``pnl[115:]``, 2012-03-29 to 2026-10-12. The
  tested closes ``y`` cover the same span. H1 is ``pnl[115:].sum() > 0``. H3 is
  the Newey-West t of the mean daily P&L above 1.645. H4 is jplv7's ADF at a
  constant and 1 lag below ``ztcrit``'s 10 percent value. H5 is
  ``vratiotest(log y)`` rejecting at 5 percent. H6 is ``genhurst(log y, 2)``
  within 2 SDs, ``ddof=1``, of its mean over 40,000 random walks of the same
  length from seed 20261011. H7 is the half-life of ``y``.

The result is **registered**: issue 607 fixed every prediction, pass mark and
comparator on 2026-10-13 before any holdout close was read. H3 to H7 decide
nothing, and each pin says whether its prediction matched. The figures are
pinned in full at 1e-9 and at the four decimals the log quotes. The run first
ran here on 2026-10-13.

Nothing here calls the vendor. ``tests/test_fetch_alphavantage.py`` holds every
rule about the ``FX_DAILY`` response on stubbed bodies, and this file holds the
command around it: each refusal reaches the operator as one line, and the key
reaches no line.

The run's rules are held on synthetic rows, recorded into a temporary data
directory where a test needs a vintage: each refusal, the window, and the
slicing that makes the positions ``market_value(...)[114:-1]`` earn
``pnl[115:]``.
"""

from __future__ import annotations

import math
import re
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from ithildincore.stats import newey_west_summary
from ithildincore.timeseries import ou_half_life

from chan import fetch_alphavantage, usdcad_holdout
from chan.fetch_alphavantage import KEY_ENV, RunStopped
from chan.khandani_lo import plain_sharpe
from chan.series import WindowCrossesScaleBreak
from chan.stationarity_tests import genhurst, jplv7_adf, vratiotest
from chan.usdcad_holdout import (
    DOWNLOAD_DATE,
    LOOKBACK,
    Band,
    Gap,
    HoldoutRefused,
    compute,
    parse_closes,
    random_walk_genhurst,
    read_closes,
    read_holdout,
    report,
)
from chan.usdcad_hurst_noise import SEED, random_walk_hurst
from chan.usdcad_mean_reversion import market_value, pnl_drawdown
from chan.vintage import (
    MANIFEST_NAME,
    VintageEntry,
    VintageRefused,
    VintageUnavailable,
    record_vintage,
)

KEY = "SECRETKEY123"


class TestTheFetchCommand:
    def test_no_key_prints_one_line_and_makes_no_request(self, monkeypatch):
        monkeypatch.delenv(KEY_ENV, raising=False)

        def never(*args, **kwargs):
            raise AssertionError("a request was made with no key")

        monkeypatch.setattr(fetch_alphavantage, "fetch_fx_daily", never)
        with pytest.raises(SystemExit) as stopped:
            usdcad_holdout.main(["fetch"])
        assert str(stopped.value) == f"{KEY_ENV} is not set, so no request was made"

    def test_the_stripped_key_reaches_the_fetch(self, monkeypatch):
        monkeypatch.setenv(KEY_ENV, f"  {KEY}\n")
        seen = []

        def fetched(*, key):
            seen.append(key)

        monkeypatch.setattr(fetch_alphavantage, "fetch_fx_daily", fetched)
        usdcad_holdout.main(["fetch"])
        assert seen == [KEY]

    @pytest.mark.parametrize(
        "refusal",
        [
            VintageRefused(f"refused at apikey={KEY}"),
            ValueError(f"refused at apikey={KEY}"),
            RunStopped(f"USDCAD, after 6 attempts: apikey={KEY}"),
            OSError(f"could not reach apikey={KEY}"),
            PermissionError(f"read-only at apikey={KEY}"),
        ],
    )
    def test_each_refusal_prints_one_line_with_the_key_redacted(self, monkeypatch, capsys, refusal):
        monkeypatch.setenv(KEY_ENV, KEY)

        def refused(*args, **kwargs):
            raise refusal

        monkeypatch.setattr(fetch_alphavantage, "fetch_fx_daily", refused)
        with pytest.raises(SystemExit) as stopped:
            usdcad_holdout.main(["fetch"])
        said = str(stopped.value)
        assert "\n" not in said and KEY not in said and "<key>" in said
        out = capsys.readouterr()
        assert KEY not in out.out + out.err

    def test_an_unknown_command_is_refused_by_the_parser(self):
        with pytest.raises(SystemExit) as stopped:
            usdcad_holdout.main(["download"])
        assert stopped.value.code == 2


# --- the run, on synthetic rows ------------------------------------------------------------

#: Weekdays from 2011-09-01, so 2012-03-29 has 150 closes before it.
DAYS = pd.bdate_range("2011-09-01", periods=320)
START = "2012-03-29"


def synthetic(days: pd.DatetimeIndex = DAYS, seed: int = 7) -> pd.Series:
    """A positive series that wanders and reverts, one close per weekday."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0.0, 0.004, len(days))
    level = np.zeros(len(days))
    for t in range(1, len(days)):
        level[t] = 0.97 * level[t - 1] + steps[t]
    return pd.Series(1.2 + level, index=days, name="USDCAD")


def entry_for(closes: pd.Series, data_dir: Path) -> VintageEntry:
    return record_vintage(
        [(str(day.date()), float(value)) for day, value in closes.items()],
        vendor="alphavantage",
        symbol="USDCAD",
        price_basis="raw",
        download_date=DOWNLOAD_DATE,
        data_dir=data_dir,
    )


@pytest.fixture
def recorded(tmp_path) -> tuple[Path, VintageEntry, pd.Series]:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / MANIFEST_NAME).write_bytes(b"")
    closes = synthetic()
    return data_dir, entry_for(closes, data_dir), closes


def payload(*rows: str, header: str = "Date,Close") -> bytes:
    return ("\n".join([header, *rows]) + "\n").encode("utf-8")


class TestTheRowsTheRunReads:
    def test_a_recorded_vintage_reads_back_as_its_closes(self, recorded) -> None:
        data_dir, entry, closes = recorded
        read_entry, read = read_closes(data_dir=data_dir)
        assert read_entry == entry
        pd.testing.assert_series_equal(read, closes, check_freq=False)

    @pytest.mark.parametrize(
        ("body", "words"),
        [
            (payload("2012-03-29,1.0", header="Date,Price"), "not 'Date,Close'"),
            (b"", "not 'Date,Close'"),
            (payload("2012-03-29,1.0,2.0"), "line 2 holds 3 fields"),
            (payload("2012-03-29"), "line 2 holds 1 fields"),
            (payload("2012-03-29,x"), "line 2 cannot be read"),
            (payload("2012-02-30,1.0"), "line 2 cannot be read"),
            (payload("2012-03-29,1.0", "2012-03-31,1.0"), "a Saturday"),
            (payload("2012-04-01,1.0"), "a Sunday"),
            (payload("2012-03-29,1.0", "2012-03-29,1.1"), "do not strictly increase"),
            (payload("2012-03-29,1.0", "2012-03-28,1.1"), "do not strictly increase"),
        ],
    )
    def test_a_row_the_run_cannot_trust_is_refused(self, body, words) -> None:
        with pytest.raises(HoldoutRefused, match=re.escape(words)):
            parse_closes(body)

    @pytest.mark.parametrize(
        "body",
        [
            b"Date,Close\r\n2012-03-29,1.0\r\n2012-03-30,1.1\r\n",
            b"Date,Close\n2012-03-29,1.0\n2012-03-30,1.1",
        ],
    )
    def test_crlf_line_ends_and_a_missing_last_newline_lose_no_close(self, body) -> None:
        assert parse_closes(body).tolist() == [1.0, 1.1]

    def test_a_nan_or_a_zero_close_is_parsed_and_left_to_the_guard(self) -> None:
        closes = parse_closes(payload("2012-03-29,nan", "2012-03-30,0"))
        assert np.isnan(closes.iloc[0]) and closes.iloc[1] == 0.0


class TestTheWindow:
    def test_the_warm_up_is_the_lookback_closes_before_the_start(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        before = closes.loc[closes.index < pd.Timestamp(START)]
        pd.testing.assert_series_equal(h.warm_up, before.iloc[-LOOKBACK:], check_freq=False)
        assert h.tested.index[0] == pd.Timestamp(START)
        assert h.tested.index[-1] == closes.index[-1]

    def test_fewer_warm_up_closes_than_the_lookback_are_refused(self, recorded) -> None:
        _, entry, closes = recorded
        start = closes.index[LOOKBACK - 1]
        with pytest.raises(HoldoutRefused, match=f"holds {LOOKBACK - 1} closes before"):
            compute(entry, closes, start=str(start.date()))
        assert compute(entry, closes, start=str(closes.index[LOOKBACK].date())).lookback == LOOKBACK

    def test_a_holdout_of_one_close_is_refused(self, recorded) -> None:
        _, entry, closes = recorded
        with pytest.raises(HoldoutRefused, match="holds 1 closes from 2012-03-29 on"):
            compute(entry, closes, start=START, end=START)

    def test_the_end_is_a_parameter(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START, end="2012-06-29")
        assert h.tested.index[-1] == pd.Timestamp("2012-06-29")

    def test_the_lookback_is_a_parameter_and_never_estimated(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START, lookback=20)
        assert h.lookback == 20 and len(h.warm_up) == 20
        assert (h.pnl.iloc[:20] == 0).all() and h.pnl.iloc[20] != 0


class TestTheSlicing:
    def test_positions_114_to_the_last_but_one_earn_pnl_115_on(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        x = h.closes.to_numpy()
        assert len(h.held) == len(h.traded) == len(h.tested)
        assert np.array_equal(h.held, market_value(x, LOOKBACK)[LOOKBACK - 1 : -1])
        returns = x[LOOKBACK:] / x[LOOKBACK - 1 : -1] - 1
        assert h.traded.to_numpy() == pytest.approx(h.held * returns, rel=1e-12)
        assert (h.pnl.iloc[:LOOKBACK] == 0).all() and h.traded.iloc[0] != 0
        assert h.traded.index[0] == pd.Timestamp(START)

    def test_every_statistic_reads_the_traded_days_or_the_tested_closes(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        y = closes.loc[START:].to_numpy()
        traded = h.traded.to_numpy()
        assert h.total_pnl == pytest.approx(traded.sum(), abs=1e-15)
        assert h.newey_west == newey_west_summary(traded)
        assert h.adf == jplv7_adf(y, 0, 1)
        assert h.vratio == vratiotest(np.log(y))
        assert h.hurst == genhurst(np.log(y), 2)
        assert h.half_life == ou_half_life(y)
        assert h.sharpe == plain_sharpe(traded)
        assert h.drawdown == pnl_drawdown(h.traded)

    def test_the_shares_count_every_traded_day_and_a_zero_position_as_neither(
        self, recorded
    ) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        held = h.held.copy()
        held[0] = 0.0
        flat = replace(h, positions=np.concatenate([h.positions[: LOOKBACK - 1], held, [0.0]]))
        assert flat.long_share + flat.short_share == pytest.approx(1 - 1 / len(held), abs=1e-12)
        assert h.long_share + h.short_share == pytest.approx(1.0, abs=1e-12)
        assert h.largest_position == pytest.approx(np.max(np.abs(h.held)), abs=0)

    def test_the_largest_position_ignores_the_last_day_s_which_earns_nothing(
        self, recorded
    ) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        late = replace(h, positions=np.concatenate([h.positions[:-1], [1e6]]))
        assert late.largest_position == h.largest_position

    def test_a_loss_from_the_first_traded_day_puts_the_peak_on_no_warm_up_day(
        self, recorded
    ) -> None:
        _, entry, _ = recorded
        rng = np.random.default_rng(3)
        level = np.empty(len(DAYS))
        level[0] = 1.2
        for t in range(1, len(DAYS)):
            level[t] = level[t - 1] * 1.003 + rng.normal(0.0, 0.0002)
        h = compute(entry, pd.Series(level, index=DAYS), start=START)
        assert h.traded.iloc[0] < 0
        assert h.drawdown == pnl_drawdown(h.traded)
        assert h.drawdown.peak >= pd.Timestamp(START)


class TestTheGuard:
    @pytest.mark.parametrize("value", [0.0, -1.2, float("nan"), float("inf"), 1.2 * 1.7])
    def test_a_close_the_rule_cannot_trade_is_refused(self, recorded, value) -> None:
        _, entry, closes = recorded
        bad = closes.copy()
        bad.loc[pd.Timestamp("2012-06-01")] = value
        with pytest.raises(WindowCrossesScaleBreak):
            compute(entry, bad, start=START)

    def test_a_bad_close_on_the_first_warm_up_day_is_refused(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        bad = closes.copy()
        bad.loc[h.warm_up.index[0]] = 0.0
        with pytest.raises(WindowCrossesScaleBreak):
            compute(entry, bad, start=START)

    def test_a_bad_close_on_the_last_traded_day_is_refused(self, recorded) -> None:
        _, entry, closes = recorded
        bad = closes.copy()
        bad.iloc[-1] = 0.0
        with pytest.raises(WindowCrossesScaleBreak):
            compute(entry, bad, start=START)

    def test_a_bad_close_before_the_warm_up_is_not_read(self, recorded) -> None:
        _, entry, closes = recorded
        bad = closes.copy()
        bad.iloc[0] = 0.0
        assert (
            compute(entry, bad, start=START).total_pnl
            == compute(entry, closes, start=START).total_pnl
        )


class TestThePredictions:
    def test_each_comparator_is_the_registered_one(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        nw = h.newey_west
        assert replace(h, newey_west=nw._replace(t_newey_west=1.645)).h3 is False
        assert replace(h, newey_west=nw._replace(t_newey_west=1.6451)).h3 is True
        critical = h.adf.critical
        assert replace(h, adf=replace(h.adf, statistic=critical[2])).h4 is False
        assert replace(h, adf=replace(h.adf, statistic=critical[2] - 1e-9)).h4 is True
        assert replace(h, adf=replace(h.adf, statistic=critical[1] + 1e-9)).h4 is True
        assert replace(h, vratio=replace(h.vratio, rejects=True)).h5 is True

    def test_h1_maps_to_the_verdict(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        flat = pd.Series(0.0, index=h.pnl.index)
        assert replace(h, pnl=flat).h1 is False
        assert replace(h, pnl=flat).log_verdict == "did not reproduce"
        up = flat.copy()
        up.iloc[-1] = 1e-12
        assert replace(h, pnl=up).log_verdict == "reproduced"
        warm = flat.copy()
        warm.iloc[0] = 1.0
        assert replace(h, pnl=warm).h1 is False

    def test_h6_holds_at_two_sds_and_not_past_them(self) -> None:
        band = Band(mean=0.5, sd=0.25, length=100, paths=10, seed=1)
        assert band.holds(1.0) and band.holds(0.0)
        assert not band.holds(1.0001) and not band.holds(-0.0001)

    def test_the_band_is_random_walk_hursts_genhurst(self) -> None:
        band = random_walk_genhurst(150, paths=600, chunk=250)
        walks = random_walk_hurst(150, paths=600, chunk=250)
        assert band.mean == pytest.approx(walks.genhurst.mean(), abs=1e-15)
        assert band.sd == pytest.approx(walks.genhurst.std(ddof=1), abs=1e-15)
        assert (band.length, band.paths, band.seed) == (150, 600, SEED)

    def test_a_series_that_does_not_revert_reports_an_infinite_half_life(
        self, recorded, capsys
    ) -> None:
        _, entry, _ = recorded
        rng = np.random.default_rng(3)
        level = np.empty(len(DAYS))
        level[0] = 1.2
        for t in range(1, len(DAYS)):
            level[t] = level[t - 1] * 1.003 + rng.normal(0.0, 0.002)
        trend = pd.Series(level, index=DAYS)
        h = compute(entry, trend, start=START)
        assert math.isinf(h.half_life)
        report(h, random_walk_genhurst(len(h.tested), paths=200))
        assert "H7 half-life infinite days" in capsys.readouterr().out


class TestTheGaps:
    def test_missing_weekdays_and_the_longest_run(self, recorded) -> None:
        _, entry, closes = recorded
        dropped = closes.drop(pd.to_datetime(["2012-05-02", "2012-05-03", "2012-07-10"]))
        h = compute(entry, dropped, start=START)
        assert h.missing_weekdays == 3
        assert h.weekdays == len(pd.bdate_range(START, closes.index[-1]))
        assert h.longest_gap == Gap(2, pd.Timestamp("2012-05-01"), pd.Timestamp("2012-05-04"))

    def test_a_missing_warm_up_day_is_not_counted_as_a_holdout_gap(self, recorded) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes.drop(pd.Timestamp("2012-02-01")), start=START)
        assert h.weekdays == len(pd.bdate_range(START, closes.index[-1]))
        assert h.missing_weekdays == 0


class TestTheReportAndTheCommand:
    def test_the_report_names_every_prediction_and_the_label(self, recorded, capsys) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        report(h, random_walk_genhurst(len(h.tested), paths=200))
        out = capsys.readouterr().out
        for label in ("H1", "H2 not run", "H3", "H4", "H5", "H6", "H7"):
            assert f"  {label}" in out
        assert "Registered on issue 607" in out and "chan.aud_cad_johansen" in out
        assert "Entry 51" in out

    def test_a_band_the_hurst_falls_outside_reads_against_the_registration(
        self, recorded, capsys
    ) -> None:
        _, entry, closes = recorded
        h = compute(entry, closes, start=START)
        report(h, Band(mean=-5.0, sd=1e-6, length=len(h.tested), paths=10, seed=1))
        h6 = capsys.readouterr().out.split("  H6 ", 1)[1].split("\n", 1)[0]
        assert h6.endswith(": does not hold, against the registration.")

    def test_the_run_passes_its_window_and_lookback_through_and_prints_the_report(
        self, recorded, capsys
    ) -> None:
        data_dir, _, _ = recorded
        h, band = usdcad_holdout.run(
            data_dir=data_dir, start="2012-04-02", end="2012-06-29", lookback=20
        )
        assert h.lookback == 20 and len(h.warm_up) == 20
        assert h.tested.index[0] == pd.Timestamp("2012-04-02")
        assert h.tested.index[-1] == pd.Timestamp("2012-06-29")
        assert band.length == len(h.tested)
        assert f"over 40,000 walks of {len(h.tested)}: " in capsys.readouterr().out

    def test_the_run_reads_the_vintage_named_by_its_download_date(self, recorded) -> None:
        data_dir, entry, closes = recorded
        h = read_holdout(data_dir=data_dir)
        assert h.entry == entry
        assert h.total_pnl == compute(entry, closes).total_pnl
        with pytest.raises(VintageUnavailable, match="dated 2026-10-14"):
            read_holdout(data_dir=data_dir, dated="2026-10-14")

    @pytest.mark.parametrize(
        "refusal",
        [
            HoldoutRefused("refused"),
            WindowCrossesScaleBreak("refused"),
            VintageUnavailable("refused"),
            VintageRefused("refused"),
            ValueError("refused"),
            RunStopped("refused"),
            OSError("refused"),
        ],
    )
    def test_each_refusal_of_the_run_prints_one_line(self, monkeypatch, refusal) -> None:
        def refused(**kwargs):
            raise refusal

        monkeypatch.setattr(usdcad_holdout, "run", refused)
        with pytest.raises(SystemExit) as stopped:
            usdcad_holdout.main(["run"])
        assert str(stopped.value) == "refused"


# --- the pins on the committed vintage ------------------------------------------------------

SPEC = (
    "alphavantage USDCAD raw dl 2026-10-13, FX_DAILY close, 5,000 rows 2007-08-10 to "
    "2026-10-12, sha256 9792b44c; Example 2.5's linear rule at the frozen lookback of 115, "
    "warm-up the 115 closes before 2012-03-29, traded days pnl[115:] from 2012-03-29 to "
    "2026-10-12, tested closes y over the same span; jplv7 adf(y, 0, 1) against ztcrit's 10%, "
    "vratiotest(log y), genhurst(log y, 2) with maxT 19 against 40,000 walks seed 20261011, "
    "registered on issue 607 on 2026-10-13"
)

VINTAGE = "alphavantage_usdcad_raw_2007-08-10_2026-10-12_dl2026-10-13.csv"
VINTAGE_SHA256 = "9792b44c3491c1c3ab3cdfb61b073e221a4022811e36dca2823d127f95c4f067"


def pin(value: float, full: float, printed: str) -> None:
    """The full value at 1e-9, and the figure at the four decimals the log quotes."""
    assert value == pytest.approx(full, abs=1e-9), SPEC
    assert f"{value:.4f}" == printed, SPEC


@pytest.fixture(scope="module")
def holdout() -> usdcad_holdout.Holdout:
    """One run on the committed vintage."""
    return read_holdout()


@pytest.fixture(scope="module")
def band(holdout) -> Band:
    """H6's band at the tested closes' length, about 6 s."""
    return random_walk_genhurst(len(holdout.tested))


class TestTheVintage:
    def test_the_entry_names_the_fx_daily_closes_downloaded_2026_10_13(self, holdout) -> None:
        entry = holdout.entry
        assert (entry.path, entry.sha256) == (VINTAGE, VINTAGE_SHA256), SPEC
        assert (entry.row_count, entry.first_date, entry.last_date) == (
            5000,
            "2007-08-10",
            "2026-10-12",
        ), SPEC
        assert entry.download_date == DOWNLOAD_DATE, SPEC
        assert entry.vendor_column == (
            "close, FX_DAILY from_symbol=USD to_symbol=CAD outputsize=full"
        ), SPEC


class TestTheHoldoutWindow:
    def test_115_warm_up_closes_from_2011_10_20_to_2012_03_28(self, holdout) -> None:
        warm = holdout.warm_up
        assert len(warm) == LOOKBACK == holdout.lookback == 115, SPEC
        assert (warm.index[0], warm.index[-1]) == (
            pd.Timestamp("2011-10-20"),
            pd.Timestamp("2012-03-28"),
        ), SPEC

    def test_3791_traded_days_from_2012_03_29_to_2026_10_12(self, holdout) -> None:
        assert len(holdout.traded) == len(holdout.tested) == len(holdout.held) == 3791, SPEC
        assert (holdout.tested.index[0], holdout.tested.index[-1]) == (
            pd.Timestamp("2012-03-29"),
            pd.Timestamp("2026-10-12"),
        ), SPEC

    def test_2_of_3793_weekdays_have_no_row_and_no_run_is_longer_than_1(self, holdout) -> None:
        assert (holdout.missing_weekdays, holdout.weekdays) == (2, 3793), SPEC
        assert holdout.longest_gap == Gap(
            1, pd.Timestamp("2014-12-26"), pd.Timestamp("2014-12-30")
        ), SPEC


class TestThePrimaryPrediction:
    def test_h1_the_cumulative_pnl_is_above_0_so_the_claim_reproduces(self, holdout) -> None:
        pin(holdout.total_pnl, 0.11316189494446321, "0.1132")
        assert holdout.h1 is True, SPEC
        assert holdout.log_verdict == "reproduced", SPEC


class TestTheSecondaryPrediction:
    def test_h3_the_newey_west_t_does_not_clear_1_645_as_registered(self, holdout) -> None:
        nw = holdout.newey_west
        pin(nw.t_newey_west, 0.2670103469846707, "0.2670")
        assert (nw.lag, nw.n) == (8, 3791), SPEC
        assert holdout.h3 is False, SPEC


class TestTheDescriptivePredictions:
    def test_h4_the_adf_does_not_reject_at_10_percent_as_registered(self, holdout) -> None:
        pin(holdout.adf.statistic, -2.0814344247981156, "-2.0814")
        assert holdout.adf.critical[2] == -2.59369, SPEC
        assert holdout.h4 is False, SPEC
        pin(holdout.adfuller_statistic, -2.0242932919577257, "-2.0243")

    def test_h5_the_variance_ratio_does_not_reject_at_5_percent_as_registered(
        self, holdout
    ) -> None:
        pin(holdout.vratio.p_value, 0.43433951622694444, "0.4343")
        assert holdout.h5 is False, SPEC

    def test_h6_genhurst_falls_inside_2_sds_of_the_random_walks_as_registered(
        self, holdout, band
    ) -> None:
        pin(holdout.hurst, 0.4973527784353397, "0.4974")
        pin(band.mean, 0.4987401602023661, "0.4987")
        pin(band.sd, 0.013002157308381909, "0.0130")
        assert (band.length, band.paths, band.seed) == (3791, 40_000, 20261011), SPEC
        assert band.holds(holdout.hurst) is True, SPEC

    def test_h7_the_half_life_is_457_8077_days_beside_the_frozen_115(self, holdout) -> None:
        pin(holdout.half_life, 457.807742210632, "457.8077")


class TestTheSideFigures:
    """Point estimates nothing tests. They decide nothing."""

    def test_the_deepest_drawdown_and_its_dates(self, holdout) -> None:
        d = holdout.drawdown
        pin(d.depth, 0.5032929211770972, "0.5033")
        assert (d.peak, d.trough) == (
            pd.Timestamp("2013-11-20"),
            pd.Timestamp("2016-01-19"),
        ), SPEC

    def test_the_sharpe_ratio_of_the_raw_pnl(self, holdout) -> None:
        pin(holdout.sharpe, 0.07154201996511289, "0.0715")

    def test_the_largest_position_and_the_shares_long_and_short(self, holdout) -> None:
        pin(holdout.largest_position, 5.405373425565022, "5.4054")
        pin(holdout.long_share, 0.399366921656555, "0.3994")
        pin(holdout.short_share, 0.600633078343445, "0.6006")
        assert int(np.sum(holdout.held == 0)) == 0, SPEC


class TestWhatThePostMeasured:
    """Numbers ``blog/usdcad-holdout-lessons.md`` quotes that no row of Entry 51 declared.

    Each was computed after the run, on 2026-10-13, to describe the drawdown
    the log reports. They are exploratory and decide nothing.
    """

    def test_the_close_rose_39_5_percent_across_the_fall(self, holdout) -> None:
        d = holdout.drawdown
        assert holdout.closes[d.peak] == 1.0445, SPEC
        assert holdout.closes[d.trough] == 1.45699, SPEC
        rise = holdout.closes[d.trough] / holdout.closes[d.peak] - 1
        assert rise == pytest.approx(0.3949162279, abs=1e-9), SPEC
        assert f"{100 * rise:.1f}" == "39.5", SPEC

    def test_the_rule_was_short_on_458_of_the_562_days_of_the_fall(self, holdout) -> None:
        """The positions that earn each day after the peak, up to and including the trough."""
        d = holdout.drawdown
        held = pd.Series(holdout.held, index=holdout.traded.index)
        fall = held[(held.index > d.peak) & (held.index <= d.trough)]
        assert (len(fall), int((fall < 0).sum())) == (562, 458), SPEC

    def test_the_pnl_first_regains_its_2013_high_on_2024_03_06(self, holdout) -> None:
        d = holdout.drawdown
        cumulative = holdout.traded.cumsum()
        after = cumulative[cumulative.index > d.trough]
        assert after[after >= cumulative[d.peak]].index[0] == pd.Timestamp("2024-03-06"), SPEC

    def test_the_largest_position_is_a_short_on_2020_03_19(self, holdout) -> None:
        held = pd.Series(holdout.held, index=holdout.traded.index)
        at = held.abs().idxmax()
        assert at == pd.Timestamp("2020-03-19"), SPEC
        pin(held[at], -5.405373425565022, "-5.4054")


class TestTheReport:
    def test_it_prints_each_prediction_its_outcome_and_the_label(
        self, holdout, band, capsys
    ) -> None:
        report(holdout, band)
        out = capsys.readouterr().out
        assert f"{VINTAGE}   alphavantage raw, downloaded 2026-10-13" in out, SPEC
        assert "warm-up  115 closes, 2011-10-20 to 2012-03-28" in out, SPEC
        assert "traded   3791 days, 2012-03-29 to 2026-10-12, lookback 115 days, frozen" in out, (
            SPEC
        )
        assert (
            "2 of 3793 weekdays have no row, the longest run 1 weekday, between 2014-12-26 and "
            "2014-12-30"
        ) in out, SPEC
        assert "H1 cumulative P&L 0.1132, against > 0: holds. Verdict: reproduced." in out, SPEC
        assert "H2 not run" in out, SPEC
        assert "H3 Newey-West t 0.2670 at lag 8 over 3791 days" in out, SPEC
        assert "> 1.645: does not hold, as registered." in out, SPEC
        assert "H4 jplv7 ADF -2.0814, against the 10% value -2.5937" in out, SPEC
        assert "-2.5937: does not hold, as registered. adfuller beside it -2.0243" in out, SPEC
        assert (
            "H5 variance ratio p-value 0.4343, rejects at 5%: does not hold, as registered." in out
        ), SPEC
        assert (
            "H6 genhurst 0.4974, against 0.4987 +/- 2 x 0.0130 over 40,000 walks of 3791" in out
        ), SPEC
        assert "holds, as registered." in out, SPEC
        assert "H7 half-life 457.8077 days, beside the frozen 115, no prediction." in out, SPEC
        assert "deepest drawdown 0.5033, from 2013-11-20 to 2016-01-19. Sharpe 0.0715" in out, SPEC
        assert "largest absolute position 5.4054, long on 0.3994 and short on 0.6006" in out, SPEC
        assert "Registered on issue 607" in out and "through 2012-04-26" in out, SPEC
