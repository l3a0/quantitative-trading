"""Example 2.5's linear rule on USD/CAD after 2012, with the lookback fixed from Chan's sample.

[Issue 607](https://github.com/l3a0/quantitative-trading/issues/607) registers
the test. This command fetches the closes it reads, Alpha Vantage's
``FX_DAILY`` USD/CAD, which the owner ruled on 2026-10-13 are committed to
``data/`` for this one series.

Usage::

    zsh -i -c 'uv run python -m chan.usdcad_holdout fetch'

The fetch reads ``ALPHAVANTAGE_API_KEY`` from the environment of the run, and
the owner's ``~/.zshrc`` exports it, which is why the command runs in an
interactive ``zsh``. :func:`chan.fetch_alphavantage.fetch_fx_daily` does the
work and holds every rule about the response.
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence

from chan import fetch_alphavantage
from chan.fetch_alphavantage import KEY_ENV, RunStopped
from chan.vintage import VintageRefused

#: The pair, as ``FX_DAILY`` names its two currencies.
FROM_SYMBOL = "USD"
TO_SYMBOL = "CAD"


def fetch(key: str) -> None:
    """Fetch USD/CAD's ``FX_DAILY`` closes and record them, or refuse with one line."""
    if not key:
        raise ValueError(f"{KEY_ENV} is not set, so no request was made")
    fetch_alphavantage.fetch_fx_daily(FROM_SYMBOL, TO_SYMBOL, key=key)


def main(argv: Sequence[str] | None = None) -> None:
    """``python -m chan.usdcad_holdout fetch``."""
    parser = argparse.ArgumentParser(
        prog="python -m chan.usdcad_holdout",
        description=(
            "Example 2.5's linear rule on USD/CAD after 2012, issue 607. fetch records "
            f"Alpha Vantage's FX_DAILY closes, reading {KEY_ENV} from the environment."
        ),
    )
    parser.add_argument("command", choices=("fetch",))
    parser.parse_args(sys.argv[1:] if argv is None else list(argv))
    key = os.environ.get(KEY_ENV, "").strip()
    try:
        fetch(key)
    except (VintageRefused, ValueError, RunStopped, OSError) as refusal:
        # A refusal is worth nothing at the bottom of a traceback, so it
        # reaches the reader as one line, the way chan.sp500_panel prints one.
        # The line passes through the key's redaction, in case a transport
        # error or a vendor body ever quotes the request.
        said = str(refusal).replace(key, "<key>") if key else str(refusal)
        raise SystemExit(said) from refusal


if __name__ == "__main__":
    main()
