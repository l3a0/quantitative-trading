"""A symbol's committed adjusted and raw yfinance closes, read as one frame.

Kept apart from :mod:`tests.support.committed_vintages`, which reads only the
manifest and so stays on the standard library. That module is imported by
``tests/test_vintage.py``, and :mod:`chan.vintage` keeps to the standard
library so that its tests do not import pandas. Parsing a series costs pandas,
so the one helper that parses lives here.
"""

from __future__ import annotations

import pandas as pd

from chan.series import load_vintage


def adjusted_against_raw(symbol: str) -> pd.DataFrame:
    """A symbol's committed adjusted and raw yfinance closes, on the days both carry.

    Two checks read this pair for different reasons. One divides the columns to
    price a cut scale-break detector, and the other compares them to say which
    column an adjusted file holds. Both load it here, so the two cannot come to
    read different pairs while each still looks right.

    The columns are ``adjusted`` and ``raw``, and a row is kept only where both
    hold a close, which is the inner join of the two dated series.
    """
    adjusted = load_vintage(symbol)[1].rename("adjusted")
    raw = load_vintage(symbol, unadjusted=True)[1].rename("raw")
    return pd.concat([adjusted, raw], axis=1, join="inner").dropna()
