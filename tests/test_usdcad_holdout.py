"""Issue 607's holdout of Example 2.5 on USD/CAD: the command, the run's rules, and the pins.

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

    def test_the_pair_and_the_stripped_key_reach_the_fetch(self, monkeypatch):
        monkeypatch.setenv(KEY_ENV, f"  {KEY}\n")
        seen = []

        def fetched(from_symbol, to_symbol, *, key):
            seen.append((from_symbol, to_symbol, key))

        monkeypatch.setattr(fetch_alphavantage, "fetch_fx_daily", fetched)
        usdcad_holdout.main(["fetch"])
        assert seen == [("USD", "CAD", KEY)]

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
