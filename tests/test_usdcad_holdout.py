"""The command that fetches and runs issue 607's holdout of Example 2.5 on USD/CAD.

Nothing here calls the vendor. ``tests/test_fetch_alphavantage.py`` holds every
rule about the ``FX_DAILY`` response on stubbed bodies, and this file holds the
command around it: each refusal reaches the operator as one line, and the key
reaches no line.
"""

from __future__ import annotations

import pytest

from chan import fetch_alphavantage, usdcad_holdout
from chan.fetch_alphavantage import KEY_ENV, RunStopped
from chan.vintage import VintageRefused

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
