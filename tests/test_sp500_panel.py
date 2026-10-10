"""The pins for the S&P 500 monthly panel: IVV's members, their tickers, and their coverage.

This file is the single authority for every number any prose surface quotes
about ``research/filings/ivv/members.csv`` and ``research/filings/ivv/holes.csv``.
[Issue 373](https://github.com/l3a0/quantitative-trading/issues/373) built them.

**The specification.** A member is a row :func:`chan.fund_holdings.members`
keeps in one of IVV's 70 listed schedules. Its ticker is the one the members
file maps it to. Its check compares Alpha Vantage's raw ``close`` on the price
date, times the filing's share count, with the filing's value, within half the
filing's value unit, plus half a share at the close on an HTML schedule, which
prints whole shares. The price date is the last trading day on or before the
report date in the committed raw SPY vintage,
``yfinance_spy_raw_1993-01-29_2026-10-02_dl2026-10-03.csv``. Coverage at a
month-end follows :mod:`chan.sp500_panel`'s rule for Example 7.7: the close at
the month-end, the two closes a year back, and a close at the next month-end
unless the series ends inside that month.

**The vintage.** The closes are the ``sp500`` cross-section in
``data/archive_vintages.jsonl``, downloaded from Alpha Vantage with
``TIME_SERIES_DAILY_ADJUSTED`` on the dates its lines record. The coverage pins
read only the members file, the holes file and those lines, whose sha256 they
name, so they run in CI. The pins that recompute the check read the archive,
and skip with the archive's own reason where there is none.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter

import pandas as pd
import pytest

from chan import archive, fetch_alphavantage, sp500_panel
from chan.archive import ArchiveUnavailable, read_cross_section
from chan.fund_holdings import IVV
from chan.fund_panel import (
    PanelRefused,
    listed,
    numbered_members,
    panel_keys,
    previous_rows,
    price_date,
    read_members,
    serialize_members,
)
from chan.vintage import SYMBOL_PATTERN

ROWS = read_members(sp500_panel.MEMBERS_PATH)
BY_KEY = {row.key: row for row in ROWS}
COVERAGE = {month.month: month for month in sp500_panel.coverage_from_committed(ROWS)}


def _name(report_date: str, row: int) -> str:
    return dict(numbered_members(IVV, report_date))[row].name


#: The members file and the holes file these pins were measured on, by sha256.
MEMBERS_SHA256 = "0b8e0f8ca7eaf388eda4784ebe30bd787b5bd4a857ffaf49c38a25676435445b"
HOLES_SHA256 = "85c6c9498610e82f2852eafb9fcffcedabbfe8870ccc4f334f311f62de770158"

#: The report's whole output on the pinned files, by sha256.
REPORT_SHA256 = "bf56300d1ca02a34a020ed351632b31e749b528b517e224ed6e02d5700ddc307"

#: Per month-end: members, covered, misses by reason, and covered members
#: whose series ends inside the next month.
MONTHS = (
    ("2008-12", 500, 415, {"no-row": 50, "no-series": 22, "price": 9, "rank": 4}, 1),
    ("2009-01", 500, 414, {"no-row": 50, "no-series": 22, "price": 9, "rank": 4, "stopped": 1}, 0),
    ("2009-02", 500, 414, {"no-row": 50, "no-series": 22, "price": 9, "rank": 4, "stopped": 1}, 0),
    ("2009-03", 500, 416, {"no-row": 49, "no-series": 20, "price": 12, "rank": 3}, 1),
    ("2009-04", 500, 415, {"no-row": 49, "no-series": 20, "price": 12, "rank": 3, "stopped": 1}, 0),
    ("2009-05", 500, 416, {"no-row": 49, "no-series": 20, "price": 12, "rank": 2, "stopped": 1}, 0),
    ("2009-06", 502, 411, {"no-row": 48, "no-series": 20, "price": 22, "rank": 1}, 0),
    ("2009-07", 502, 411, {"no-row": 48, "no-series": 20, "price": 22, "rank": 1}, 0),
    ("2009-08", 502, 411, {"no-row": 48, "no-series": 20, "price": 22, "rank": 1}, 0),
    ("2009-09", 500, 417, {"no-row": 45, "no-series": 19, "price": 17, "rank": 2}, 0),
    ("2009-10", 500, 417, {"no-row": 45, "no-series": 19, "price": 17, "rank": 2}, 0),
    ("2009-11", 500, 418, {"no-row": 45, "no-series": 19, "price": 17, "rank": 1}, 0),
    ("2009-12", 500, 407, {"no-row": 43, "no-series": 17, "price": 31, "rank": 2}, 0),
    ("2010-01", 500, 407, {"no-row": 43, "no-series": 17, "price": 31, "rank": 2}, 0),
    ("2010-02", 500, 406, {"no-row": 43, "no-series": 17, "price": 31, "rank": 3}, 0),
    ("2010-03", 500, 395, {"no-row": 41, "no-series": 14, "price": 48, "rank": 2}, 0),
    ("2010-04", 500, 395, {"no-row": 41, "no-series": 14, "price": 48, "rank": 2}, 0),
    ("2010-05", 500, 391, {"no-row": 41, "no-series": 14, "price": 48, "rank": 6}, 0),
    ("2010-06", 500, 420, {"no-row": 41, "no-series": 14, "price": 11, "rank": 14}, 0),
    ("2010-07", 500, 420, {"no-row": 41, "no-series": 14, "price": 11, "rank": 14}, 0),
    ("2010-08", 500, 426, {"no-row": 41, "no-series": 14, "price": 11, "rank": 8}, 0),
    ("2010-09", 500, 408, {"no-row": 39, "no-series": 14, "price": 30, "rank": 9}, 0),
    ("2010-10", 500, 408, {"no-row": 39, "no-series": 14, "price": 30, "rank": 9}, 0),
    ("2010-11", 500, 398, {"no-row": 39, "no-series": 14, "price": 30, "rank": 19}, 0),
    ("2010-12", 500, 416, {"no-row": 40, "no-series": 12, "price": 11, "rank": 21}, 0),
    ("2011-01", 500, 416, {"no-row": 40, "no-series": 12, "price": 11, "rank": 21}, 0),
    ("2011-02", 500, 398, {"no-row": 40, "no-series": 12, "price": 11, "rank": 39}, 1),
    ("2011-03", 501, 386, {"no-row": 40, "no-series": 11, "price": 39, "rank": 25}, 0),
    ("2011-04", 501, 386, {"no-row": 40, "no-series": 11, "price": 39, "rank": 25}, 0),
    ("2011-05", 501, 409, {"no-row": 40, "no-series": 11, "price": 39, "rank": 2}, 0),
    ("2011-06", 499, 442, {"no-row": 39, "no-series": 9, "price": 7, "rank": 2}, 0),
    ("2011-07", 499, 442, {"no-row": 39, "no-series": 9, "price": 7, "rank": 2}, 0),
    ("2011-08", 499, 422, {"no-row": 39, "no-series": 9, "price": 7, "rank": 22}, 0),
    ("2011-09", 500, 393, {"no-row": 37, "no-series": 9, "price": 42, "rank": 19}, 0),
    ("2011-10", 500, 393, {"no-row": 37, "no-series": 9, "price": 42, "rank": 19}, 0),
    ("2011-11", 500, 408, {"no-row": 37, "no-series": 9, "price": 42, "rank": 4}, 0),
    ("2011-12", 500, 443, {"no-row": 38, "no-series": 8, "price": 5, "rank": 6}, 0),
    ("2012-01", 500, 443, {"no-row": 38, "no-series": 8, "price": 5, "rank": 6}, 0),
    ("2012-02", 500, 416, {"no-row": 38, "no-series": 8, "price": 5, "rank": 33}, 0),
    ("2012-03", 500, 401, {"no-row": 36, "no-series": 8, "price": 31, "rank": 24}, 0),
    ("2012-04", 500, 401, {"no-row": 36, "no-series": 8, "price": 31, "rank": 24}, 0),
    ("2012-05", 500, 420, {"next": 1, "no-row": 36, "no-series": 8, "price": 31, "rank": 4}, 0),
    ("2012-06", 501, 447, {"no-row": 35, "no-series": 8, "price": 7, "rank": 4}, 0),
    ("2012-07", 501, 447, {"no-row": 35, "no-series": 8, "price": 7, "rank": 4}, 0),
    ("2012-08", 501, 415, {"no-row": 35, "no-series": 8, "price": 7, "rank": 36}, 0),
    ("2012-09", 501, 364, {"no-row": 33, "no-series": 8, "price": 69, "rank": 27}, 0),
    ("2012-10", 501, 365, {"no-row": 33, "no-series": 8, "price": 69, "rank": 26}, 0),
    ("2012-11", 501, 388, {"no-row": 33, "no-series": 8, "price": 69, "rank": 3}, 0),
    ("2012-12", 500, 389, {"no-row": 33, "no-series": 7, "price": 69, "rank": 2}, 0),
    ("2013-01", 500, 389, {"no-row": 33, "no-series": 7, "price": 69, "rank": 2}, 0),
    ("2013-02", 500, 377, {"no-row": 33, "no-series": 7, "price": 69, "rank": 14}, 0),
    ("2013-03", 500, 385, {"no-row": 33, "no-series": 7, "price": 59, "rank": 16}, 0),
    ("2013-04", 500, 386, {"no-row": 33, "no-series": 7, "price": 59, "rank": 15}, 0),
    ("2013-05", 500, 397, {"no-row": 33, "no-series": 7, "price": 59, "rank": 4}, 0),
    ("2013-06", 500, 410, {"no-row": 32, "no-series": 7, "price": 46, "rank": 5}, 0),
    ("2013-07", 500, 410, {"no-row": 32, "no-series": 7, "price": 46, "rank": 5}, 0),
    ("2013-08", 500, 373, {"no-row": 32, "no-series": 7, "price": 46, "rank": 42}, 0),
    ("2013-09", 500, 374, {"no-row": 32, "no-series": 7, "price": 46, "rank": 41}, 0),
    ("2013-10", 500, 374, {"no-row": 32, "no-series": 7, "price": 46, "rank": 41}, 0),
    ("2013-11", 500, 372, {"no-row": 32, "no-series": 7, "price": 46, "rank": 43}, 0),
    ("2013-12", 500, 387, {"no-row": 30, "no-series": 3, "price": 25, "rank": 55}, 0),
    ("2014-01", 500, 388, {"no-row": 30, "no-series": 3, "price": 25, "rank": 54}, 0),
    ("2014-02", 500, 399, {"no-row": 30, "no-series": 3, "price": 25, "rank": 43}, 0),
    ("2014-03", 500, 403, {"no-row": 29, "no-series": 3, "price": 18, "rank": 47}, 0),
    ("2014-04", 500, 403, {"no-row": 29, "no-series": 3, "price": 18, "rank": 47}, 0),
    ("2014-05", 500, 417, {"no-row": 29, "no-series": 3, "price": 18, "rank": 33}, 0),
    ("2014-06", 502, 425, {"no-row": 28, "no-series": 3, "price": 3, "rank": 43}, 1),
    ("2014-07", 502, 424, {"no-row": 28, "no-series": 3, "price": 3, "rank": 43, "stopped": 1}, 0),
    ("2014-08", 502, 424, {"no-row": 28, "no-series": 3, "price": 3, "rank": 43, "stopped": 1}, 0),
    ("2014-09", 502, 426, {"no-row": 27, "no-series": 3, "price": 3, "rank": 43}, 0),
    ("2014-10", 502, 425, {"next": 1, "no-row": 27, "no-series": 3, "price": 3, "rank": 43}, 0),
    ("2014-11", 502, 445, {"close": 1, "no-row": 27, "no-series": 3, "price": 3, "rank": 23}, 0),
    ("2014-12", 502, 446, {"no-row": 27, "no-series": 3, "price": 3, "rank": 23}, 0),
    ("2015-01", 502, 446, {"no-row": 27, "no-series": 3, "price": 3, "rank": 23}, 2),
    ("2015-02", 502, 451, {"no-row": 27, "no-series": 3, "price": 3, "rank": 16, "stopped": 2}, 1),
    ("2015-03", 502, 456, {"no-row": 27, "no-series": 3, "price": 2, "rank": 14}, 0),
    ("2015-04", 502, 457, {"no-row": 27, "no-series": 3, "price": 2, "rank": 13}, 0),
    ("2015-05", 502, 470, {"no-row": 27, "no-series": 3, "price": 2}, 2),
    ("2015-06", 502, 469, {"no-row": 27, "no-series": 3, "price": 2, "rank": 1}, 3),
    ("2015-07", 502, 466, {"no-row": 27, "no-series": 3, "price": 2, "rank": 1, "stopped": 3}, 0),
    ("2015-08", 502, 466, {"no-row": 27, "no-series": 3, "price": 2, "rank": 1, "stopped": 3}, 1),
    ("2015-09", 505, 431, {"no-row": 26, "no-series": 3, "price": 43, "rank": 2}, 0),
    ("2015-10", 505, 430, {"next": 1, "no-row": 26, "no-series": 3, "price": 43, "rank": 2}, 1),
    ("2015-11", 505, 429, {"no-row": 26, "no-series": 3, "price": 43, "rank": 2, "stopped": 2}, 1),
    ("2015-12", 504, 467, {"no-row": 27, "no-series": 3, "price": 2, "rank": 5}, 0),
    ("2016-01", 504, 468, {"no-row": 27, "no-series": 3, "price": 2, "rank": 4}, 0),
    ("2016-02", 504, 467, {"next": 1, "no-row": 27, "no-series": 3, "price": 2, "rank": 4}, 1),
    ("2016-03", 504, 471, {"next": 1, "no-row": 20, "no-series": 2, "price": 2, "rank": 8}, 0),
    ("2016-04", 504, 471, {"close": 1, "no-row": 20, "no-series": 2, "price": 2, "rank": 8}, 1),
    (
        "2016-05",
        504,
        469,
        {"close": 1, "next": 1, "no-row": 20, "no-series": 2, "price": 2, "rank": 8, "stopped": 1},
        0,
    ),
    ("2016-06", 507, 478, {"no-row": 17, "no-series": 1, "price": 2, "rank": 9}, 1),
    ("2016-07", 507, 479, {"no-row": 17, "no-series": 1, "price": 2, "rank": 6, "stopped": 2}, 0),
    ("2016-08", 507, 440, {"no-row": 17, "no-series": 1, "price": 2, "rank": 45, "stopped": 2}, 0),
    ("2016-09", 505, 445, {"no-row": 14, "no-series": 1, "rank": 45}, 0),
    ("2016-10", 505, 446, {"no-row": 14, "no-series": 1, "rank": 44}, 0),
    ("2016-11", 505, 485, {"no-row": 14, "no-series": 1, "rank": 5}, 0),
    ("2016-12", 505, 485, {"no-row": 14, "no-series": 1, "rank": 5}, 1),
    ("2017-01", 505, 485, {"no-row": 14, "no-series": 1, "rank": 4, "stopped": 1}, 0),
    ("2017-02", 505, 487, {"no-row": 14, "no-series": 1, "rank": 2, "stopped": 1}, 2),
    ("2017-03", 505, 490, {"no-row": 12, "no-series": 1, "rank": 2}, 0),
    ("2017-04", 505, 491, {"no-row": 12, "no-series": 1, "rank": 1}, 0),
    ("2017-05", 505, 490, {"no-row": 12, "no-series": 1, "rank": 2}, 1),
    ("2017-06", 505, 489, {"no-row": 12, "no-series": 1, "rank": 3}, 1),
    ("2017-07", 505, 489, {"no-row": 12, "no-series": 1, "rank": 2, "stopped": 1}, 2),
    ("2017-08", 505, 488, {"no-row": 12, "no-series": 1, "rank": 1, "stopped": 3}, 0),
    ("2017-09", 505, 491, {"no-row": 10, "no-series": 1, "rank": 3}, 1),
    ("2017-10", 505, 490, {"no-row": 10, "no-series": 1, "rank": 3, "stopped": 1}, 1),
    ("2017-11", 505, 489, {"no-row": 10, "no-series": 1, "rank": 3, "stopped": 2}, 0),
    ("2017-12", 504, 490, {"no-row": 10, "no-series": 1, "rank": 3}, 0),
    ("2018-01", 504, 490, {"no-row": 10, "no-series": 1, "rank": 3}, 0),
    ("2018-02", 504, 491, {"no-row": 10, "no-series": 1, "rank": 2}, 1),
    ("2018-03", 505, 492, {"no-row": 10, "no-series": 1, "rank": 2}, 0),
    ("2018-04", 505, 492, {"no-row": 10, "no-series": 1, "rank": 2}, 1),
    ("2018-05", 505, 490, {"next": 1, "no-row": 10, "no-series": 1, "rank": 2, "stopped": 1}, 1),
    ("2018-06", 505, 491, {"no-row": 8, "no-series": 1, "price": 2, "rank": 3}, 0),
    ("2018-07", 505, 493, {"no-row": 8, "no-series": 1, "price": 2, "rank": 1}, 1),
    ("2018-08", 505, 492, {"no-row": 8, "no-series": 1, "price": 2, "rank": 1, "stopped": 1}, 1),
    ("2018-09", 506, 495, {"next": 1, "no-row": 8, "no-series": 1, "rank": 1}, 1),
    ("2018-10", 506, 494, {"no-row": 8, "no-series": 1, "rank": 1, "stopped": 2}, 2),
    ("2018-11", 506, 492, {"no-row": 8, "no-series": 1, "rank": 1, "stopped": 4}, 2),
    ("2018-12", 506, 495, {"next": 1, "no-row": 7, "no-series": 1, "rank": 2}, 0),
    ("2019-01", 506, 495, {"no-row": 7, "no-series": 1, "rank": 2, "stopped": 1}, 0),
    ("2019-02", 506, 495, {"no-row": 7, "no-series": 1, "rank": 2, "stopped": 1}, 0),
    ("2019-03", 505, 496, {"no-row": 4, "no-series": 1, "rank": 4}, 0),
    ("2019-04", 505, 496, {"no-row": 4, "no-series": 1, "rank": 4}, 0),
    ("2019-05", 505, 494, {"no-row": 4, "no-series": 1, "rank": 6}, 0),
    ("2019-06", 505, 492, {"no-row": 4, "no-series": 1, "rank": 8}, 1),
    ("2019-07", 505, 491, {"no-row": 4, "no-series": 1, "rank": 8, "stopped": 1}, 0),
    ("2019-08", 505, 493, {"no-row": 4, "no-series": 1, "rank": 6, "stopped": 1}, 1),
    ("2019-09", 505, 491, {"no-row": 3, "no-series": 1, "price": 4, "rank": 6}, 0),
    ("2019-10", 505, 492, {"no-row": 3, "no-series": 1, "price": 4, "rank": 5}, 1),
    ("2019-11", 505, 491, {"no-row": 3, "no-series": 1, "price": 4, "rank": 5, "stopped": 1}, 2),
    ("2019-12", 505, 495, {"no-row": 3, "no-series": 1, "price": 1, "rank": 5}, 1),
    ("2020-01", 505, 494, {"no-row": 3, "no-series": 1, "price": 1, "rank": 5, "stopped": 1}, 0),
    ("2020-02", 505, 494, {"no-row": 3, "no-series": 1, "price": 1, "rank": 5, "stopped": 1}, 0),
    ("2020-03", 505, 498, {"no-row": 3, "no-series": 1, "price": 1, "rank": 2}, 1),
    ("2020-04", 505, 497, {"no-row": 3, "no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 1),
    ("2020-05", 505, 497, {"no-row": 3, "no-series": 1, "price": 1, "rank": 1, "stopped": 2}, 0),
    ("2020-06", 505, 498, {"no-row": 3, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2020-07", 505, 498, {"no-row": 3, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2020-08", 505, 495, {"no-row": 3, "no-series": 1, "price": 1, "rank": 5}, 0),
    ("2020-09", 505, 496, {"no-row": 3, "no-series": 1, "rank": 5}, 2),
    ("2020-10", 505, 494, {"no-row": 3, "no-series": 1, "rank": 5, "stopped": 2}, 1),
    ("2020-11", 505, 495, {"no-row": 3, "no-series": 1, "rank": 3, "stopped": 3}, 0),
    ("2020-12", 505, 496, {"no-row": 3, "no-series": 1, "rank": 5}, 2),
    ("2021-01", 505, 494, {"no-row": 3, "no-series": 1, "rank": 5, "stopped": 2}, 0),
    ("2021-02", 505, 494, {"no-row": 3, "no-series": 1, "rank": 5, "stopped": 2}, 0),
    ("2021-03", 505, 499, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2}, 1),
    ("2021-04", 505, 498, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 1),
    ("2021-05", 505, 497, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2, "stopped": 2}, 0),
    ("2021-06", 505, 498, {"no-row": 2, "no-series": 1, "price": 1, "rank": 3}, 1),
    ("2021-07", 505, 497, {"no-row": 2, "no-series": 1, "price": 1, "rank": 3, "stopped": 1}, 0),
    ("2021-08", 505, 498, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 1),
    ("2021-09", 505, 499, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2021-10", 505, 499, {"no-row": 2, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2021-11", 505, 500, {"no-row": 2, "no-series": 1, "price": 1, "rank": 1}, 1),
    ("2021-12", 505, 500, {"no-row": 2, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2022-01", 505, 500, {"no-row": 2, "no-series": 1, "price": 1, "rank": 1}, 1),
    ("2022-02", 505, 499, {"no-row": 2, "no-series": 1, "price": 1, "rank": 1, "stopped": 1}, 0),
    ("2022-03", 505, 499, {"next": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 1),
    (
        "2022-04",
        505,
        498,
        {"close": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 2, "stopped": 1},
        0,
    ),
    (
        "2022-05",
        505,
        497,
        {"close": 1, "next": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 2, "stopped": 1},
        0,
    ),
    ("2022-06", 504, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2022-07", 504, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2022-08", 504, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2022-09", 503, 498, {"next": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 3),
    (
        "2022-10",
        503,
        495,
        {"close": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 1, "stopped": 3},
        0,
    ),
    (
        "2022-11",
        503,
        494,
        {"next": 1, "no-row": 1, "no-series": 1, "price": 1, "rank": 1, "stopped": 4},
        0,
    ),
    ("2022-12", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-01", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-02", 503, 500, {"no-row": 1, "no-series": 1, "price": 1}, 0),
    ("2023-03", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-04", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-05", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-06", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-07", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-08", 503, 499, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1}, 0),
    ("2023-09", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 1),
    ("2023-10", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 0),
    ("2023-11", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 0),
    ("2023-12", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 3}, 0),
    ("2024-01", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2024-02", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2024-03", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 0),
    ("2024-04", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 2}, 1),
    ("2024-05", 503, 498, {"no-row": 1, "no-series": 1, "price": 1, "rank": 1, "stopped": 1}, 0),
    ("2024-06", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 3}, 0),
    ("2024-07", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 3}, 0),
    ("2024-08", 503, 497, {"no-row": 1, "no-series": 1, "price": 1, "rank": 3}, 0),
    ("2024-09", 504, 497, {"no-series": 1, "price": 1, "rank": 5}, 0),
    ("2024-10", 504, 498, {"no-series": 1, "price": 1, "rank": 4}, 1),
    ("2024-11", 504, 497, {"no-series": 1, "price": 1, "rank": 4, "stopped": 1}, 1),
    ("2024-12", 503, 498, {"no-series": 1, "price": 1, "rank": 3}, 0),
    ("2025-01", 503, 498, {"no-series": 1, "price": 1, "rank": 3}, 0),
    ("2025-02", 503, 498, {"no-series": 1, "price": 1, "rank": 3}, 0),
    ("2025-03", 504, 500, {"no-series": 1, "price": 1, "rank": 2}, 0),
    ("2025-04", 504, 500, {"no-series": 1, "price": 1, "rank": 2}, 1),
    ("2025-05", 504, 499, {"no-series": 1, "price": 1, "rank": 2, "stopped": 1}, 0),
    ("2025-06", 504, 499, {"next": 1, "no-series": 1, "price": 1, "rank": 2}, 2),
    ("2025-07", 504, 498, {"close": 1, "no-series": 1, "price": 1, "rank": 1, "stopped": 2}, 1),
    ("2025-08", 504, 497, {"close": 1, "no-series": 1, "price": 1, "rank": 1, "stopped": 3}, 0),
    ("2025-09", 503, 501, {"no-series": 1, "rank": 1}, 0),
    ("2025-10", 503, 501, {"no-series": 1, "rank": 1}, 1),
    ("2025-11", 503, 500, {"no-series": 1, "rank": 1, "stopped": 1}, 1),
    ("2025-12", 503, 499, {"no-series": 1, "rank": 3}, 0),
    ("2026-01", 503, 499, {"no-series": 1, "rank": 3}, 1),
    ("2026-02", 503, 499, {"no-series": 1, "rank": 2, "stopped": 1}, 0),
    ("2026-03", 503, 500, {"no-series": 1, "rank": 2}, 1),
    ("2026-04", 503, 499, {"no-series": 1, "rank": 2, "stopped": 1}, 1),
    ("2026-05", 503, 498, {"no-series": 1, "rank": 2, "stopped": 2}, 0),
    ("2026-06", 503, 498, {"no-series": 1, "rank": 4}, 0),
    ("2026-07", 503, 498, {"no-series": 1, "rank": 4}, 2),
    ("2026-08", 503, 497, {"no-series": 1, "rank": 3, "stopped": 2}, 0),
)

#: How many rows each source answered, each check gave, and each exit says.
SOURCES = {"hand": 249, "link": 34201, "name": 755}
CHECKS = {"no-row": 1186, "no-series": 304, "pass": 33018, "price": 697}
EXITS = {"close": 32927, "stop": 91}


class TestTheMembersFile:
    def test_it_holds_every_row_of_the_panel_once_in_order(self) -> None:
        assert [row.key for row in ROWS] == sorted(panel_keys(IVV, whole_first=True))

    def test_it_holds_the_whole_first_schedule(self) -> None:
        """2008-12-31 sets December 2008 to February 2009, so all 500 of its members are rows."""
        first = [row for row in ROWS if row.report_date == "2008-12-31"]
        assert len(first) == len(numbered_members(IVV, "2008-12-31")) == 500
        assert len(panel_keys(IVV)) == len(ROWS) - 12

    def test_it_is_what_the_writer_writes(self) -> None:
        assert serialize_members(ROWS) == sp500_panel.MEMBERS_PATH.read_bytes()

    def test_a_link_row_takes_the_ticker_of_the_row_that_links_to_it(self) -> None:
        forward = {before: after for after, before in previous_rows(IVV).items()}
        for row in ROWS:
            if row.source == "link":
                assert BY_KEY[forward[row.key]].ticker == row.ticker, row.key

    def test_the_skipped_schedule_has_no_rows_and_is_linked_across(self) -> None:
        assert not any(row.report_date == "2013-09-30" for row in ROWS)
        assert {
            before[0] for after, before in previous_rows(IVV).items() if after[0] == "2013-12-31"
        } == {"2013-06-30"}

    def test_every_ticker_is_a_symbol_the_archive_records_as_written(self) -> None:
        assert all(SYMBOL_PATTERN.fullmatch(row.ticker) for row in ROWS if row.ticker)

    def test_every_hand_row_names_its_evidence(self) -> None:
        assert all(row.note for row in ROWS if row.source == "hand")

    def test_every_row_carries_a_check(self) -> None:
        assert all(row.check for row in ROWS)

    def test_no_two_members_of_one_schedule_pass_on_one_ticker(self) -> None:
        passing = [(row.report_date, row.ticker) for row in ROWS if row.check == "pass"]
        assert len(passing) == len(set(passing))

    def test_the_sources_checks_and_exits(self) -> None:
        assert dict(sorted(Counter(row.source for row in ROWS).items())) == SOURCES
        assert dict(sorted(Counter(row.check for row in ROWS).items())) == CHECKS
        assert dict(sorted(Counter(row.exit for row in ROWS if row.exit).items())) == EXITS


class TestTheCoverage:
    def test_the_files_are_the_ones_these_pins_were_measured_on(self) -> None:
        for path, digest in (
            (sp500_panel.MEMBERS_PATH, MEMBERS_SHA256),
            (sp500_panel.HOLES_PATH, HOLES_SHA256),
        ):
            assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, path.name

    @pytest.mark.parametrize("pin", MONTHS, ids=lambda pin: pin[0])
    def test_each_month_end_covers_its_pinned_members(self, pin: tuple) -> None:
        month, members, covered, misses, stops = pin
        found = COVERAGE[month]
        assert (found.members, found.covered, found.misses, found.stops) == (
            members,
            covered,
            misses,
            stops,
        )

    def test_every_month_end_from_december_2008_to_august_2026_is_reported(self) -> None:
        assert [pin[0] for pin in MONTHS] == [str(month) for month in sp500_panel.months()]
        assert len(MONTHS) == 213

    def test_coverage_runs_from_364_in_september_2012_to_501(self) -> None:
        low = min(MONTHS, key=lambda pin: pin[2])
        assert (low[0], low[1], low[2]) == ("2012-09", 501, 364)
        assert max(pin[2] for pin in MONTHS) == 501
        assert [pin[0] for pin in MONTHS if pin[2] == 501] == ["2025-09", "2025-10"]
        assert (min(pin[1] for pin in MONTHS), max(pin[1] for pin in MONTHS)) == (499, 507)

    def test_the_rule_on_its_own_gives_every_month_ends_misses(self) -> None:
        """Issue 336's union mask asks :func:`sp500_panel.coverage_rule` about one row at a time."""
        covers = sp500_panel.coverage_rule(
            ROWS, sp500_panel.spans(), sp500_panel.read_holes(), sp500_panel.calendar()
        )
        by_schedule: dict[str, list] = {}
        for row in ROWS:
            by_schedule.setdefault(row.report_date, []).append(row)
        for month, found in COVERAGE.items():
            period = pd.Period(month, "M")
            missed = {
                row.key: reason
                for row in by_schedule[found.schedule]
                if (reason := covers(row, period)) is not None
            }
            assert missed == dict(zip(found.missing, found.reasons, strict=True)), month

    def test_2013_06_30_sets_six_month_ends(self) -> None:
        assert [month for month, found in COVERAGE.items() if found.schedule == "2013-06-30"] == [
            "2013-06",
            "2013-07",
            "2013-08",
            "2013-09",
            "2013-10",
            "2013-11",
        ]


class TestTheHolesFile:
    def test_it_is_what_the_writer_writes(self) -> None:
        holes = sp500_panel.read_holes()
        assert sp500_panel.serialize_holes(holes) == sp500_panel.HOLES_PATH.read_bytes()

    def test_389_holes_fall_in_22_series(self) -> None:
        holes = sp500_panel.read_holes()
        assert (len(holes), len({ticker for ticker, _ in holes})) == (389, 22)

    def test_every_hole_names_a_recorded_series_inside_the_span_the_report_reads(self) -> None:
        spans = sp500_panel.spans()
        days = sp500_panel.calendar()
        for ticker, month in sp500_panel.read_holes():
            first, last = spans[ticker]
            day = sp500_panel.month_end(days, pd.Period(month, "M"))
            assert pd.Timestamp(first) <= day <= pd.Timestamp(last), (ticker, month)


class TestTheManifestLines:
    """The sp500 lines this panel recorded."""

    def _lines(self) -> list[bytes]:
        return [
            line
            for line in archive._manifest_path(None).read_bytes().split(b"\n")
            if line.strip() and json.loads(line).get("cross_section") == "sp500"
        ]

    def test_this_panel_recorded_822_lines_on_one_download_date(self) -> None:
        lines = self._lines()
        entries = [json.loads(line) for line in lines]
        assert len(lines) == 822
        assert sum(len(line) + 1 for line in lines) == 318_413
        assert sum(entry["row_count"] for entry in entries) == 4_305_502
        assert {entry["download_date"] for entry in entries} == {"2026-10-05"}
        assert min(entry["first_date"] for entry in entries) == "1999-11-01"
        assert max(entry["last_date"] for entry in entries) == "2026-10-02"
        digest = hashlib.sha256(b"".join(sorted(line + b"\n" for line in lines))).hexdigest()
        assert digest == "f3af75ff867643a7718d44d93860e04f1bf0f5c9f27872840d8f354a3ea199c7"

    def test_ivv_and_four_tickers_tried_and_replaced_are_lines_no_member_reads(self) -> None:
        mapped = {row.ticker for row in ROWS if row.ticker}
        symbols = sorted(json.loads(line)["symbol"] for line in self._lines())
        assert [symbol for symbol in symbols if symbol not in mapped] == [
            "CUK", "FTRPR", "IVV", "PCLN", "PRH",
        ]  # fmt: skip

    def test_every_mapped_ticker_with_no_line_is_one_alpha_vantage_holds_no_series_for(
        self,
    ) -> None:
        recorded = {json.loads(line)["symbol"] for line in self._lines()}
        absent = {row.ticker for row in ROWS if row.ticker and row.ticker not in recorded}
        assert absent == {row.ticker for row in ROWS if row.check == "no-series"}
        assert len(absent) == 22


class TestTheBindings:
    def test_load_refuses_a_file_that_is_not_the_panel(self, tmp_path) -> None:
        short = tmp_path / "members.csv"
        short.write_bytes(serialize_members(ROWS[1:]))
        with pytest.raises(PanelRefused, match="lacks 1 they do"):
            sp500_panel.load(short)

    def test_spans_reads_only_the_sp500_lines(self) -> None:
        lines = [
            json.loads(line)
            for line in archive._manifest_path(None).read_bytes().split(b"\n")
            if line.strip()
        ]
        mine = {
            line["symbol"]: (line["first_date"], line["last_date"])
            for line in lines
            if line.get("cross_section") == "sp500"
        }
        assert sp500_panel.spans() == mine

    def test_check_asks_for_the_close_the_last_position_is_closed_at(self, monkeypatch) -> None:
        seen = {}

        def fake_check(fund, rows, closes, calendar, filings_dir=None, *, exit_on):
            seen["exit_on"] = exit_on
            return list(rows)

        monkeypatch.setattr(sp500_panel, "read_cross_section", lambda *a, **k: ([], pd.DataFrame()))
        monkeypatch.setattr(sp500_panel, "check_members", fake_check)
        monkeypatch.setattr(sp500_panel, "find_holes", lambda *a: set())
        sp500_panel.check()
        assert seen["exit_on"] is sp500_panel.exit_close


class TestTheCases:
    def test_equity_residential_is_a_current_member_alpha_vantage_holds_no_series_for(
        self,
    ) -> None:
        rows = [row for row in ROWS if row.ticker == "EQR"]
        assert {row.check for row in rows} == {"no-series"}
        assert len(rows) == 70

    def test_paramount_global_misses_on_a_para_series_that_is_another_listing(self) -> None:
        row = BY_KEY[("2022-03-31", 190)]
        assert _name("2022-03-31", 190) == "Paramount Global"
        assert (row.ticker, row.check, row.gap) == ("PARA", "price", "-2801.00")

    def test_carnival_is_ccl_rather_than_carnival_plcs_cuk(self) -> None:
        rows = [
            row for row in ROWS if row.report_date >= "2025-12-31" and "Carnival" in _name(*row.key)
        ]
        assert {(row.ticker, row.check) for row in rows} == {("CCL", "pass")}


class TestThePriceDates:
    def test_19_of_the_71_quarter_ends_fall_on_a_weekend_and_take_the_friday_before(self) -> None:
        days = sp500_panel.calendar()
        moved = [
            filing.report_date
            for filing in IVV.filings
            if price_date(days, filing.report_date) != pd.Timestamp(filing.report_date)
        ]
        assert (len(IVV.filings), len(moved)) == (71, 19)
        assert all(pd.Timestamp(date).dayofweek >= 5 for date in moved)

    def test_good_friday_2013_moves_2013_03_31_to_the_thursday(self) -> None:
        assert price_date(sp500_panel.calendar(), "2013-03-31") == pd.Timestamp("2013-03-28")

    def test_the_last_exit_is_2026_09_30(self) -> None:
        assert sp500_panel.exit_close(sp500_panel.calendar(), "2026-06-30") == pd.Timestamp(
            "2026-09-30"
        )

    def test_every_listed_schedule_has_a_form_the_check_knows(self) -> None:
        assert {filing.form for filing in listed(IVV)} == {
            "N-Q", "N-CSR", "N-CSRS", "NPORT-EX", "NPORT-P", "NPORT-P/A",
        }  # fmt: skip


def _store():
    try:
        return archive.archive_dir()
    except ArchiveUnavailable as absent:
        pytest.skip(str(absent))


class TestTheArchive:
    """Runs only where an archive is configured."""

    def test_the_committed_check_and_holes_are_what_the_archive_gives(self) -> None:
        store = _store()
        try:
            rows, holes = sp500_panel.check(directory=store)
        except ArchiveUnavailable as absent:
            pytest.skip(str(absent))
        assert tuple(rows) == ROWS
        assert holes == set(sp500_panel.read_holes())

    def test_ivv_trades_on_the_same_month_end_days_as_the_spy_calendar(self) -> None:
        """Issue 336's plan named IVV's trading days, and its run takes SPY's like this panel."""
        store = _store()
        entries, closes = read_cross_section(
            "sp500", column="close", symbols=["IVV"], directory=store
        )
        assert [entry.download_date for entry in entries] == ["2026-10-05"]
        ivv = pd.DatetimeIndex(closes["IVV"].dropna().index)
        spy = sp500_panel.calendar()
        span = pd.period_range("2007-12", "2026-09", freq="M")
        assert [sp500_panel.month_end(ivv[ivv <= "2026-10-02"], m) for m in span] == [
            sp500_panel.month_end(spy, m) for m in span
        ]


class TestTheCommand:
    def test_report_prints_one_line_per_month_end_then_every_missing_member(self, capsys) -> None:
        sp500_panel.main(["report"])
        out = capsys.readouterr().out
        lines = out.splitlines()
        assert [line.split()[0] for line in lines[:213]] == [pin[0] for pin in MONTHS]
        assert lines[0] == (
            "2008-12  schedule 2008-12-31  members 500  covered 415  stops 1  "
            "missing 85 (no-row 50, no-series 22, price 9, rank 4)"
        )
        assert lines[213] == "missing members:"
        assert len(lines) == 214 + sum(pin[1] - pin[2] for pin in MONTHS)
        assert "  2022-03 row 190 PARA: Paramount Global, price" in lines
        assert hashlib.sha256(out.encode()).hexdigest() == REPORT_SHA256

    def test_fetch_hands_on_ivv_and_every_ticker_and_redacts_the_key(
        self, monkeypatch, capsys
    ) -> None:
        handed = {}

        def fake_fetch(cross_section, symbols, *, key):
            handed.update(cross_section=cross_section, symbols=list(symbols), key=key)
            return fetch_alphavantage.Tally(recorded=["AAA"], failed=[f"X{key}"])

        monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "SECRETKEY")
        monkeypatch.setattr(fetch_alphavantage, "fetch", fake_fetch)
        with pytest.raises(SystemExit) as stopped:
            sp500_panel.main(["fetch"])
        assert stopped.value.code == 1
        assert handed["cross_section"] == "sp500"
        assert handed["symbols"] == ["IVV", *sp500_panel.tickers(ROWS)]
        assert "" not in handed["symbols"]
        out = capsys.readouterr().out
        assert "SECRETKEY" not in out
        assert "X<key>" in out

    def test_a_complete_fetch_exits_cleanly(self, monkeypatch, capsys) -> None:
        monkeypatch.setenv("ALPHAVANTAGE_API_KEY", "SECRETKEY")
        monkeypatch.setattr(
            fetch_alphavantage, "fetch", lambda *a, **k: fetch_alphavantage.Tally(already=["A"])
        )
        sp500_panel.main(["fetch"])
        assert capsys.readouterr().out.startswith("recorded 0, already recorded 1")

    @pytest.mark.parametrize("refusal", [PanelRefused, archive.ArchiveRefused])
    def test_a_refusal_is_one_line(self, monkeypatch, refusal) -> None:
        def refuse(*args, **kwargs):
            raise refusal("the one line")

        monkeypatch.setattr(sp500_panel, "load", refuse)
        with pytest.raises(SystemExit, match="^the one line$"):
            sp500_panel.main(["report"])

    def test_check_with_no_archive_prints_one_line(self, monkeypatch, tmp_path) -> None:
        monkeypatch.delenv("QT_ARCHIVE_DIR", raising=False)
        monkeypatch.setattr(archive, "ARCHIVE_DIR_CONFIG", tmp_path / "absent")
        with pytest.raises(SystemExit) as stopped:
            sp500_panel.main(["check"])
        assert str(stopped.value).startswith("no data archive is configured")

    def test_fetch_with_no_key_makes_no_request(self, monkeypatch) -> None:
        monkeypatch.delenv("ALPHAVANTAGE_API_KEY", raising=False)
        with pytest.raises(SystemExit, match="ALPHAVANTAGE_API_KEY is not set"):
            sp500_panel.main(["fetch"])

    def test_an_unknown_command_prints_the_usage(self) -> None:
        with pytest.raises(SystemExit, match="usage"):
            sp500_panel.main(["fetch", "now"])
