"""The pins for the twenty-seven whiteboard GIFs in the commodity seasonals post.

Three sketches draw the opening: the two trades on one calendar, the years
each won in the book's years and after, and the fall inside 2002's natural
gas trade. Two draw Lesson 1, its natural gas streaks
and gasoline's two claims.
Nine draw Lesson 2: the range the missing rows leave, a guessed price, what
Chan's 19 needs, how fill 2 carries June's move, which April days can test a
fill, how its misses lean and spread, how the lean looks April by April, why
a miss subtracts at an entry and adds at an exit, and each fill's miss
against each year's move. Eight draw Lesson 4: how far each Sharpe ratio can
stray, why fewer results widen a range, where natural gas's ±12% comes from,
which later range holds its earlier mean, what the Mann-Whitney test counts,
what its chance means, the four chances against the 5% line, and how one year
moves natural gas's mean but not its ranks. Five draw Lesson 5: which numbered file holds
June, a handover, which years each check reaches, an entry on March's last
day, and a holiday row. The scenes are
built from the natural gas and gasoline runs on the committed EIA files rather
than from a pinned copy of their figures. Most tests check the drawing against
the run, and a few check the run against literal dates, counts and labels the
post quotes, such as test_the_run_gives_these_dates_and_files.

1. The two-trades sketch draws each trade's entry and exit as a bar on one
   calendar. What is pinned is that each bar runs from the run's entry date to
   its exit date on one scale, that its labels name those dates and Chan's
   counts, and that other dates move the bars and the labels.
2. The split sketch draws both trades' years on one axis, split where the
   book's years end. What is pinned is that each mark sits at its year on one
   scale, that no year without a row gets a mark, that each dashed line falls
   between the last of the book's years and the next, that the counts on each side are
   the run's and the opening table's, and that other figures move them.
3. The drawdown sketch draws natural gas's 2002 trade as its return over its
   entry price on each trading day the files hold a price, with its peak, the
   largest fall after it and its exit. What is pinned is that each mark sits at
   its trading day and its return on one scale, that the marks are the run's,
   one per trading day the files hold a price, that the bracket spans the
   run's drawdown, the same as the book's years' drawdown, that the labels
   read their figures from the run, and that other figures move them.
4. The streak sketch draws a dot at each profitable year from 1994 to the
   first loss, a cross at that loss, a note naming the trade as natural gas's
   June contract, the first edition's release between 2008 and 2009, and
   brackets for Chan's counts of 13 and 14, from 1995 above the
   axis and from 1994 below it. What is pinned is that each mark sits at its
   year on one scale, that each bracket ends where
   :func:`chan.commodity_seasonals.runs_ending` says that count ends, and
   that other figures move the marks and the labels.
5. The gasoline sketch draws a dot at each profitable gasoline year from 1995
   to 2015, a cross at each loss, a span under the years with no row, the
   first edition's release, and brackets for the sidebar's claim and the main
   text's count. What is pinned is that each mark sits at its year on one
   scale, that no year without a row gets a mark, that the sidebar's bracket
   ends before the release and the first loss while the main text's covers
   every loss, and that other figures move the marks and the labels.
6. The range sketch draws gasoline's years and a scale of counts. What is
   pinned is that the files' range runs from the profitable years to those
   plus the missing ones, and that Chan's count sits at its top end.
7. The Chan's-19 sketch draws Chan's years and the files' as two bars. What
   is pinned is that each box spans its count, that the missing years fill
   exactly the gap between the files' profits and Chan's, and that both bars'
   losses line up.
8. The interpolation sketch draws the May contract around 1997's missing
   entry, the straight line across the gap and its guess, and a band of one
   typical miss either side of the guess, split at the exit price. What is
   pinned is that each settlement sits at its trading day and price on one
   scale, that the guess lies on the line, that the band spans the run's
   typical miss and splits where the exit price is, that the guess sits on
   the profit side while the band reaches the loss side, and that other
   figures move it.
9. The fill 2 sketch draws May's and June's prices around 1997's gap, June's
   rise and the same rise on May, and fill 2's band. What is pinned is that
   both arrows rise by June's change, that the guess is fill 2's, that the
   band spans fill 2's typical miss and splits at the exit price, and that
   May and June differ by mark as well as by ink.
10. The test-day sketch draws the April trading days narrowing to 1997's test
   days. What is pinned is that each bar is drawn to scale at the run's count,
   that each drop is the difference between two bars, and that the last bar is
   the number of test days behind fill 2's figures.
11. The three-numbers sketch draws fill 2's misses on every test day of 1997's
   pattern. What is pinned is one dot per test day, each in its stack, and
   that the average, the spread and the typical miss it draws equal the
   run's ``june_bias``, ``june_spread`` and ``june_error``.
12. The Aprils sketch draws each April's average miss. What is pinned is one
   bar per April at its average, the test-day counts, and a title that counts
   the Aprils and those leaning low from the run.
13. The miss-sign sketch draws 1997's missing entry and 1998's missing exit,
   each guess lifted by fill 2's average miss. What is pinned is that each
   bracket spans its two prices on one scale, that the lift is the run's
   average miss, and that the lifted bracket is shorter for the entry and
   longer for the exit by exactly that miss.
14. The fill-miss sketch draws each missing year's move with fill 2's guess
   corrected by its average miss, and a bar of the spread of its misses. What
   is pinned is that each dot, bar and σ sit at the run's figures on one scale,
   and that a bar crosses zero exactly when its move is under one spread.
15. The Sharpe sketch draws each period of the returns table as a dot at its
   Sharpe ratio on a bar 1.96 standard errors either side. What is pinned is
   that each dot and bar sit at the run's figures on one scale, and that a
   bar crosses zero exactly for the two periods after the book.
16. The multiplier sketch draws Student's t's 95% multiplier for the post's
   two counts of later years, for 30 results and for very many, against the
   normal curve's 1.96. What is pinned is that each bar's height is the
   multiplier for its count and that the post's counts come from the run.
17. The half-width sketch builds natural gas's ±12% from its spread, divided
   by the root of its count and times the multiplier, each bar starting on a
   dashed line at the later mean, against a dashed line at its earlier mean. What
   is pinned is that each bar is the run's figure on one scale, that every
   bar starts on that line, and that the last bar reaches past the gap.
18. The mean-range sketch draws each period's mean and 95% range, with each
   trade's earlier mean carried down past its later bar. What is pinned is
   that each dot, bar and dashed line sit at the run's figures, and that
   natural gas's line lands inside its later bar and gasoline's outside.
19. The pairs sketch draws every pairing of an earlier natural gas year with
   a later one as a dot. What is pinned is that each dot sits in its cell,
   blue exactly where the earlier year returned more, that the blue count is
   :func:`chan.commodity_seasonals.pairs_won`'s, that the edge falls after
   each row's last blue dot, and that 2022's column is all vermilion.
20. The luck sketch draws the exact chance of each count of pairs won, which
   the Mann-Whitney p-value is counted from. What is pinned is that the
   chances add to one, that its shaded share is
   :func:`chan.commodity_seasonals.rank_p_value`'s, that the curve peaks at
   half the pairs, and that the years' count sits past the 5% line.
21. The chances sketch draws the table's four chances on one scale. What is
   pinned is that each dot sits at its chance from the run, and that only a
   chance past 5% is drawn in purple.
22. The one-year sketch draws natural gas's returns after 2008 with ticks at
   their mean with and without 2022, and all 30 years ranked. What is pinned
   is that the ticks sit at the run's means, that each rank dot sits in its
   period's row in rank order, that the nine worst ranks are later years, and
   that shrinking 2022's gain moves the mean and leaves every rank in place.
23. The calendar sketch draws the March to June contracts in 2008 and 2006,
   each bar ending at its last trading day, with a dashed line at each entry
   and exit. What is pinned is that June's number in each label is how many
   bars reach that line, that it equals the file the run reads, and that the
   March note follows the dates.
24. The handover sketch draws the two files in February 1996. What is pinned
   is that the files hand over the day after the rule's last day, and that
   each dashed line sits between its two days.
25. The coverage sketch draws which years each check reaches. What is pinned
   is that its counts are the run's, that the exchange's dates are the ones
   ``tests/test_commodity_seasonals.py`` pins, and that each bar spans its
   years.
26. The edge-day sketch draws 2018's entry on March's own last day. What is
   pinned is that the entry line meets the end of March's bar.
27. The holiday sketch draws Christmas week of 2018 and 2016. What is pinned is
   that a dot stands on exactly the days the contract-1 file holds a row.

The rules every sketch shares are pinned here too: labels clear of ink in the
hand font and the fallback, each GIF's size, frames, loop and timing, every
sketch's slower pace, that two draws give the same bytes, and that
each committed GIF is a fresh draw, a comparison that runs only on macOS
arm64 with Comic Sans MS, as
``tests/test_usdcad_tests_whiteboard.py`` explains. The check that
``docs/figures`` holds exactly the GIFs the modules draw lives in
``tests/test_equity_seasonals_whiteboard.py``, which reads :data:`GIFS` from
here.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re
from datetime import date, timedelta

import matplotlib
import numpy as np
import pytest
from PIL import Image

from chan import commodity_seasonals as seasonals
from chan import commodity_seasonals_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.commodity_seasonals_whiteboard import (
    CALENDAR,
    CALENDAR_X,
    CHANCE_DY,
    CHANCE_LINE,
    CHANCE_POINT,
    CHANCE_ROWS,
    CHANCE_X0,
    EDGE_YEAR,
    EXCHANGE_LAST_TRADES,
    FIRST_EDITION,
    HALF_POINT,
    HALF_X,
    HANDOVER_YEAR,
    LUCK_BASE,
    LUCK_PEAK,
    LUCK_SPAN,
    LUCK_X,
    PAIRS_CELL,
    PAIRS_X0,
    PAIRS_Y0,
    PERIODS,
    RANK_AFTER_Y,
    RANK_BEFORE_Y,
    RANK_X,
    STREAK_AXIS_Y,
    T_BASE,
    T_COMPARE,
    T_UNIT,
    ChanceRow,
    CheckCoverage,
    DrawdownFigures,
    FillTwoFigures,
    GasolineFigures,
    GuessFigures,
    MissFigures,
    NarrowingFigures,
    OneYearFigures,
    SplitFigures,
    StreakFigures,
    _after_book,
    _april_leans,
    _april_x,
    _bar_x,
    _cents_x,
    _chan_needs_gaps,
    _chances,
    _check_coverage,
    _count_x,
    _cover_x,
    _day_x,
    _drawdown,
    _drawdown_x,
    _drawdown_y,
    _expiry_scenes,
    _fill_misses,
    _fill_two_x,
    _fill_two_y,
    _gap_range,
    _gasoline_editions,
    _gasoline_x,
    _guess_x,
    _guess_y,
    _half_width,
    _interpolation_guess,
    _june_file,
    _june_move_fill,
    _last_trade_with_lead,
    _luck,
    _mean_ranges,
    _mean_scenes,
    _mean_x,
    _miss_sign,
    _miss_stacks,
    _miss_x,
    _narrow_end,
    _one_year,
    _pairs,
    _sharpe_ranges,
    _sharpe_x,
    _sign_y,
    _split_x,
    _streak_start,
    _streak_x,
    _t_multiplier,
    _test_days,
    _three_numbers,
    _trades_x,
    _two_trades,
    _year_x,
    chance_rows,
    edge_years,
    gif_name,
    june_years,
    main,
    make_commodity_seasonals_whiteboards,
    mean_rows,
    pair_count_chances,
    scenes,
    sharpe_rows,
    sketch_timeline,
)
from chan.futures import is_trading_day, ng_last_trade
from chan.palette import ACCENT, GOOD, LOST
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import INK, MUTED
from chan.usdcad_tests_whiteboard import (
    HEIGHT,
    HOLD_MS,
    TITLE_MS,
    WIDTH,
    Frame,
    Label,
    clearances,
    hand_font,
    timeline,
)

POST = REPO_ROOT / "blog" / "commodity-seasonals-lessons.md"

#: Every GIF in the order :func:`make_commodity_seasonals_whiteboards` writes them.
GIFS = [
    "commodity_sketch_two_trades.gif",
    "commodity_sketch_after_book.gif",
    "commodity_sketch_drawdown_2002.gif",
    "commodity_sketch_streak_start.gif",
    "commodity_sketch_gasoline_editions.gif",
    "commodity_sketch_gap_range.gif",
    "commodity_sketch_chan_needs_gaps.gif",
    "commodity_sketch_interpolation_guess.gif",
    "commodity_sketch_june_move_fill.gif",
    "commodity_sketch_test_days.gif",
    "commodity_sketch_three_numbers.gif",
    "commodity_sketch_april_leans.gif",
    "commodity_sketch_miss_sign.gif",
    "commodity_sketch_fill_misses.gif",
    "commodity_sketch_sharpe_ranges.gif",
    "commodity_sketch_t_multiplier.gif",
    "commodity_sketch_half_width.gif",
    "commodity_sketch_mean_ranges.gif",
    "commodity_sketch_rank_pairs.gif",
    "commodity_sketch_luck_curve.gif",
    "commodity_sketch_four_chances.gif",
    "commodity_sketch_one_year.gif",
    "commodity_sketch_june_file.gif",
    "commodity_sketch_handover.gif",
    "commodity_sketch_check_coverage.gif",
    "commodity_sketch_edge_day.gif",
    "commodity_sketch_holiday_rows.gif",
]

#: The paragraph each GIF follows, by its opening words.
FOLLOWS = (
    "1. **Gasoline.** Buy the May contract",
    "```math\n\\small\\begin{array}{l|r|r}\n & \\text{Book’s years}",
    "A year’s return is the change in the contract’s price over its entry price",
    "1. **They rule out the revised edition.**",
    "Gasoline’s main text says 19 profitable years",
    "EIA’s New York Harbor file holds no row",
    "The losses say more than the gaps.",
    "Fill 1 draws a straight line",
    "Fill 2 takes May’s price on the last day before the gap",
    "A pattern that reaches back fewer days",
    "Fill 2’s misses also lean one way.",
    "Test days close together read some of the same prices, though,",
    "```math\n\\begin{aligned}\n\\text{true move} &= (\\text{guess} + e) - \\text{entry}",
    "So the chance that all three years were profits",
    "For the four Sharpe ratios in the returns table",
    "```math\n\\bar r \\pm t_{n-1}",
    "```math\n\\begin{aligned}\n&-0.4\\%",
    "That range, −6% to +2%, leaves out",
    "The Mann-Whitney test ignores how large each return was.",
    "Each test gives the chance that luck alone",
    "```math\n\\small\\begin{array}{l|r|r}\n & \\text{Welch}",
    "Without 2022 the average after 2008 is −5.0%",
    "For gasoline that is always contract 1.",
    "When a contract expires, every later contract moves forward one place",
    "Over every natural gas contract delivered from February 1994",
    "In 10 of the 30 years, the entry date falls",
    "The run computes its own calendar of trading days",
)

TWO_TRADES_LABELS = [
    "Feb",
    "Mar",
    "Apr",
    "May",
    "natural gas: buy June contract Feb 25, sell Apr 15",
    "demand: air conditioning",
    "Chan: 13 years in a row, 14 in the sidebar",
    "gasoline: buy May contract Apr 13, sell Apr 25",
    "demand: summer driving",
    "Chan: 19 of 21 years, 1995 to 2015",
]

SPLIT_LABELS = [
    "natural gas, June contract",
    "15 of 15 won",
    "7 of 15 won",
    "gasoline, May contract",
    "16 of 18 won",
    "3 of 8 won",
    "no row",
    "1994",
    "2008",
    "2015",
    "2023",
    "dot: a profitable year   x: a loss",
    "dashed: where the book’s years end",
]

DRAWDOWN_LABELS = [
    "0%",
    "Feb 25",
    "Apr 15",
    "return over the entry price, marked each day the files hold a price",
    "peak: +48%",
    "drawdown:",
    "22 points",
    "exit: +40%",
    "a profitable year",
    "natural gas, June contract, 2002",
]

STREAK_LABELS = [
    "1994",
    "1995",
    "2006",
    "2007",
    "2008",
    "2009",
    "loss",
    "dot: a profitable year",
    "natural gas, June contract",
    "first edition, Nov 2008",
    "13 from 1995, main text",
    "14 from 1995, sidebar",
    "13 from 1994",
    "14 from 1994",
]

GASOLINE_LABELS = [
    "1995",
    "2008",
    "2015",
    "no row",
    "first edition, Nov 2008",
    "sidebar: a profit every year since 1995",
    "main text: 19 of 21, as of 2015",
    "dot: a profitable year",
    "x: a loss, 2009 and 2012",
    "May contract",
]

RANGE_LABELS = [
    "1995",
    "2015",
    "no row: a profit or a loss?",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "the files allow 16 to 19",
    "Chan: 19",
    "profitable years of 21",
    "gasoline, May contract",
]

NEEDS_LABELS = [
    "19 profits",
    "Chan",
    "16 profits",
    "EIA",
    "2 losses",
    "2009, 2012",
    "no row",
    "1997 to 1999 must all be profits for Chan’s 19",
    "gasoline, May contract",
]

FILL_TWO_LABELS = [
    "May",
    "June",
    "dot: May   ring: June",
    "gasoline",
    "Apr 14, the entry: no May row",
    "June rose 0.9¢",
    "same rise on May: guess 62.1¢",
    "exit price 62.5¢",
    "63.0¢",
    "61.2¢",
    "fill 2’s typical miss either side",
    "entry here: a loss",
    "entry here: a profit",
]

NARROW_LABELS = [
    "April trading days, 1994 to 2005",
    "247",
    "the pattern fits inside April",
    "187",
    "−60: fall outside April",
    "May has all four prices",
    "108",
    "−79: lack a May price",
    "June has both of fill 2’s prices",
    "80",
    "−28: lack a June price",
    "1997’s gap: rows 2 days back and 1 ahead, fill 2 starts 4 back",
    "gasoline, May contract",
]

THREE_LABELS = [
    "−2¢",
    "−1¢",
    "0¢",
    "+1¢",
    "+2¢",
    "cents a gallon",
    "dot: one test day’s miss, 80 days",
    "typical miss ±0.89¢, around zero",
    "average +0.26¢, spread ±0.86¢",
    "gasoline, May contract",
]

APRIL_LABELS = [
    "1994 (5)",
    "1995 (5)",
    "1996 (8)",
    "1997 (3)",
    "1998 (1)",
    "1999 (2)",
    "2000 (8)",
    "2001 (9)",
    "2002 (11)",
    "2003 (8)",
    "2004 (15)",
    "2005 (5)",
    "left: May guessed too high",
    "right: too low",
    "(n): test days that April",
    "8 of 12 Aprils lean low",
    "gasoline, May contract",
]

SIGN_LABELS = [
    "1997: the entry is missing",
    "exit 62.5¢",
    "guess 62.1¢",
    "e = 0.26¢",
    "guess + e",
    "m",
    "m − e",
    "1998: the exit is missing",
    "entry 49.8¢",
    "guess 50.3¢",
    "e = 0.21¢",
    "guess + e",
    "m",
    "m + e",
    "e drawn at fill 2’s average miss",
    "gasoline, May contract",
]

MISS_LABELS = [
    "loss",
    "profit",
    "σ = 0.86¢",
    "1997",
    "57%",
    "σ = 0.74¢",
    "1998",
    "83%",
    "σ = 0.62¢",
    "1999",
    "90%",
    "−1¢",
    "+1¢",
    "cents a gallon",
    "chance of profit",
    "dot: the corrected move",
    "bar: σ, fill 2’s spread, either side",
    "gasoline, May contract",
]

GUESS_LABELS = [
    "gasoline, May contract, April 1997",
    "Apr 14, the entry: no row",
    "exit price 62.5¢",
    "straight-line guess 61.6¢",
    "63.5¢",
    "59.7¢",
    "one typical miss either side",
    "entry here: a loss",
    "entry here: a profit",
]

HANDOVER_LABELS = [
    "contract-1 file",
    "contract-2 file",
    "Feb 26: file 1 picks up file 2’s price",
    "March stopped Feb 23, 5 trading days before delivery",
    "3-day rule: here",
    "natural gas, March contract, Feb 1996",
]

COVERAGE_LABELS = [
    "1994",
    "2000",
    "2010",
    "2017",
    "2026",
    "the files’ handovers: 298 of 316 expiries fit",
    "the exchange’s dates: 40 of 40 March to June contracts",
    "before 2017, the files alone",
    "natural gas, contracts’ last trading days",
]

EDGE_LABELS = [
    "March",
    "April",
    "May",
    "June",
    "entry, close of Feb 26",
    "March’s last day: it still trades at this close",
    "June is contract 4",
    "10 of 30 years enter on March’s last day.",
    "Reading the contract-3 file instead turns no year from a profit to a loss.",
    "natural gas, June contract",
]

HOLIDAY_LABELS = [
    "2018",
    *("21", "22", "23", "24", "25"),
    "Dec 25: closed, row repeats Dec 24’s $3.467",
    *("26", "27", "28"),
    "2016",
    *("21", "22", "23", "24", "25", "26"),
    "Dec 26: closed, no row",
    *("27", "28"),
    "dot: a row in the contract-1 file   no dot: a weekend or a closed day",
]

JUNE_LABELS = [
    "March",
    "April",
    "May",
    "June",
    "2008",
    "March still trading",
    "June is contract 4 on Feb 25",
    "contract 2 on Apr 15",
    "March",
    "April",
    "May",
    "June",
    "2006",
    "March has expired",
    "June is contract 3 on Feb 27",
    "contract 2 on Apr 13",
    "June’s number is how many bars each line crosses",
]

SHARPE_LABELS = [
    "loses",
    "earns",
    "natural gas, 1994 to 2008",
    "1.0",
    "natural gas, 2009 to 2023",
    "0.0",
    "gasoline, 1995 to 2015",
    "0.8",
    "gasoline, 2016 to 2023",
    "−0.4",
    "−1",
    "+1",
    "+2",
    "Sharpe ratio",
    "dot: the Sharpe ratio",
    "bar: 1.96 standard errors either side",
]

T_LABELS = [
    "2.36",
    "8 results",
    "2.14",
    "15 results",
    "2.05",
    "30 results",
    "1.96",
    "many",
    "normal, 1.96",
    "95% multiplier from Student’s t",
    "purple: the later periods’ 8 and 15 years",
]

HALF_LABELS = [
    "the later mean, −0.4%",
    "spread s = 21.6%",
    "s / √15 = 5.6%",
    "× 2.14 = 12.0%",
    "the earlier mean, 11.0 points higher",
    "natural gas, June contract, 2009 to 2023",
]

MEAN_LABELS = [
    "0%",
    "natural gas, 1994 to 2008",
    "+10.6%",
    "natural gas, 2009 to 2023",
    "−0.4%",
    "gasoline, 1995 to 2015",
    "+3.2%",
    "gasoline, 2016 to 2023",
    "−1.9%",
    "−10%",
    "+10%",
    "+20%",
    "mean yearly return",
    "dot: the mean",
    "bar: 95% range   dashed: the earlier mean",
]

PAIRS_LABELS = [
    "rows: 1994 to 2008,",
    "worst at the bottom",
    "columns: 2009 to 2023, worst on the left",
    "blue: the earlier year did better",
    "vermilion: the later year did",
    "2022",
    "2022 beats all 15 earlier years",
    "earlier year won 177 of 225 pairs",
    "chance alone: 112.5",
    "natural gas, June contract",
]

LUCK_LABELS = [
    "pairs the earlier years win, of 225",
    "what luck alone gives,",
    "if nothing changed",
    "112.5: no change",
    "the 5% line",
    "177 pairs:",
    "what the years did",
    "this far out, either side: 0.7% of luck’s draws",
    "natural gas, June contract",
]

CHANCE_LABELS = [
    "0%",
    "5%",
    "10%",
    "below: luck explains it poorly",
    "above: luck could explain it",
    "gasoline",
    "Welch, 2.3%",
    "Mann-Whitney, 1.1%",
    "natural gas",
    "Welch, 9.2%",
    "Mann-Whitney, 0.7%",
]

ONE_YEAR_LABELS = [
    "0%",
    "returns, 2009 to 2023",
    "2014 and 2018: just above 0%",
    "2022: +64%",
    "mean −0.4%",
    "without 2022: −5.0%",
    "1994 to 2008",
    "2009 to 2023",
    "worst",
    "best: 2022",
    "ranked worst to best, 2022 is the top rank however large its gain",
    "natural gas, June contract",
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def streaks():
    return StreakFigures.from_run()


@pytest.fixture(scope="module")
def years():
    return june_years()


@pytest.fixture(scope="module")
def gasoline():
    return GasolineFigures.from_run()


@pytest.fixture(scope="module")
def guess():
    return GuessFigures.from_run()


@pytest.fixture(scope="module")
def fill_two():
    return FillTwoFigures.from_run()


@pytest.fixture(scope="module")
def misses():
    return MissFigures.from_run()


@pytest.fixture(scope="module")
def narrowing():
    return NarrowingFigures.from_run()


@pytest.fixture(scope="module")
def split():
    return SplitFigures.from_run()


@pytest.fixture(scope="module")
def drawdown():
    return DrawdownFigures.from_run()


@pytest.fixture(scope="module")
def every(streaks, years, gasoline, guess, fill_two, misses, narrowing, split, drawdown):
    return scenes(streaks, years, gasoline, guess, fill_two, misses, narrowing, split, drawdown)


@pytest.fixture(scope="module")
def gifs(
    tmp_path_factory, streaks, years, gasoline, guess, fill_two, misses, narrowing, split, drawdown
):
    return make_commodity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"),
        streaks=streaks,
        years=years,
        gasoline=gasoline,
        guess=guess,
        fill_two=fill_two,
        misses=misses,
        narrowing=narrowing,
        split=split,
        drawdown=drawdown,
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _label(scene, text):
    return next(s for s in scene.steps if isinstance(s, Label) and s.text == text)


def _font(monkeypatch, fallback: bool) -> None:
    if fallback:
        monkeypatch.setattr(whiteboard, "hand_font", lambda: whiteboard.FALLBACK_FONT)


def _boxes(scene):
    with matplotlib.rc_context(whiteboard._style()):
        canvas, artists = whiteboard._board(scene)
        whiteboard._show(scene, artists, Frame(len(scene.steps), 0, 0))
        canvas.draw()
        renderer = canvas.get_renderer()
        return [
            (artist.get_text(), artist.get_window_extent(renderer))
            for artist in artists
            if hasattr(artist, "get_text") and artist.get_visible()
        ]


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        found = []
        for index in range(image.n_frames):
            image.seek(index)
            found.append(image.info["duration"])
        return found


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _or(words: list[str]) -> str:
    """Words joined as the alt text writes them: "9", "9 or 15", "9, 10 or 15"."""
    return words[0] if len(words) == 1 else f"{', '.join(words[:-1])} or {words[-1]}"


# --- The rules every sketch shares --------------------------------------------


class TestTheScenes:
    def test_there_are_twenty_seven_in_the_order_the_post_reads_them(self, every) -> None:
        assert [gif_name(scene) for scene in every] == GIFS

    def test_every_label_names_a_stroke_drawn_before_it(self, every) -> None:
        for scene in every:
            for index, step in enumerate(scene.steps):
                if isinstance(step, Label):
                    earlier = [s.gid for s in scene.steps[:index] if not isinstance(s, Label)]
                    assert step.names in earlier, (scene.title, step.text)

    def test_no_label_is_parsed_as_math(self, every) -> None:
        assert not [s.text for scene in every for s in scene.steps if getattr(s, "math", 0)]

    def test_every_stroke_has_a_point_for_each_of_its_frames(self, every) -> None:
        for scene in every:
            for stroke in scene.strokes:
                assert stroke.points >= stroke.frames, (scene.title, stroke.gid)

    def test_each_sketch_of_one_trade_names_it(self, every) -> None:
        """A reader who meets a sketch before its paragraph can tell which
        commodity it draws, from its title or from one grey note. A title that
        names the commodity leaves the note only the contract. The calendar
        sketch draws several natural gas contracts and names each one, and the
        Sharpe, multiplier and mean-range sketches draw both trades or neither
        and name each row's, so they are the exceptions. So are the first two
        opening sketches, which draw both trades and name each one."""
        trades = {
            "drawdown_2002": ("natural gas", "June contract"),
            "streak_start": ("natural gas", "June contract"),
            "gasoline_editions": ("gasoline", "May contract"),
            "gap_range": ("gasoline", "May contract"),
            "interpolation_guess": ("gasoline", "May contract"),
            "chan_needs_gaps": ("gasoline", "May contract"),
            "fill_misses": ("gasoline", "May contract"),
            "june_move_fill": ("gasoline", "gasoline"),
            "miss_sign": ("gasoline", "May contract"),
            "test_days": ("gasoline", "May contract"),
            "three_numbers": ("gasoline", "May contract"),
            "april_leans": ("gasoline", "May contract"),
            "one_year": ("natural gas", "June contract"),
            "rank_pairs": ("natural gas", "June contract"),
            "luck_curve": ("natural gas", "June contract"),
            "half_width": ("natural gas", "June contract"),
            "handover": ("natural gas", "March contract"),
            "edge_day": ("natural gas", "June contract"),
        }
        exceptions = {
            "two_trades",
            "after_book",
            "june_file",
            "sharpe_ranges",
            "t_multiplier",
            "mean_ranges",
            "four_chances",
            "check_coverage",
            "holiday_rows",
        }
        assert set(trades) | exceptions == {scene.slug for scene in every}
        for scene in every:
            if scene.slug not in trades:
                continue
            commodity, contract = trades[scene.slug]
            notes = [label for label in scene.labels if contract in label]
            assert len(notes) == 1, scene.slug
            assert _label(scene, notes[0]).color == MUTED, scene.slug
            in_title = commodity in scene.title.lower()
            assert (commodity in notes[0]) != in_title, scene.slug

    def test_every_pale_tint_has_a_green_edge(self, every) -> None:
        """No sketch draws a tint today. One that does would need the
        green edge the equity seasonals module's ``_tinted`` draws, since the
        tint alone stands 1.29 to 1 against the board."""
        tints = [fill for scene in every for fill in scene.fills if fill.color == whiteboard.TINT]
        assert tints == []


class TestTheLabelsStayClearOfTheLines:
    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_clears_every_stroke(self, every, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            found = clearances(scene)
            assert set(found) == {*scene.labels, scene.title}
            for text, pixels in found.items():
                assert pixels >= CLEAR_PX, (scene.title, text, round(pixels, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_every_label_and_title_sits_inside_the_board(
        self, every, monkeypatch, fallback
    ) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            for text, box in _boxes(scene):
                inside = min(box.x0, box.y0, WIDTH - box.x1, HEIGHT - box.y1)
                assert inside >= INSIDE_PX, (scene.title, text, round(inside, 1))

    @pytest.mark.parametrize("fallback", [False, True], ids=["installed font", "fallback font"])
    def test_no_two_labels_touch(self, every, monkeypatch, fallback) -> None:
        _font(monkeypatch, fallback)
        for scene in every:
            boxes = _boxes(scene)
            for k, (one, a) in enumerate(boxes):
                for other, b in boxes[k + 1 :]:
                    gap = math.hypot(
                        max(a.x0 - b.x1, b.x0 - a.x1, 0.0), max(a.y0 - b.y1, b.y0 - a.y1, 0.0)
                    )
                    assert gap >= APART_LABELS_PX, (scene.title, one, other, round(gap, 1))


class TestTheGifs:
    def test_there_is_one_named_for_each_scene(self, gifs) -> None:
        assert [path.name for path in gifs] == GIFS

    def test_each_is_680_by_320_and_loops_forever(self, gifs, every) -> None:
        for path, scene in zip(gifs, every, strict=True):
            steps = sketch_timeline(scene)
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every) -> None:
        for scene in every:
            steps = sketch_timeline(scene)
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = sketches.PACED_HOLD_MS if scene.slug in sketches.PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_every_sketch_builds_slowly_and_holds_twelve_seconds(self, every) -> None:
        """The pace the owner asked for, for each sketch in turn: each label alone
        for 0.9 s, or 1.8 s with strokes at 250 ms a frame for the sketches in
        SLOWER, and the drawing for 12 s, the equity post's slow pace. A
        sketch in DRAW_MS draws each part-drawn stroke frame at its own pace
        and keeps SLOWER's 250 ms on each finished stroke."""
        from chan import equity_seasonals_whiteboard as equity

        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (
            equity.PACED_LABEL_MS,
            equity.PACED_HOLD_MS,
        )
        assert sketches.PACED == (
            "two_trades",
            "after_book",
            "drawdown_2002",
            "streak_start",
            "gasoline_editions",
            "gap_range",
            "chan_needs_gaps",
            "interpolation_guess",
            "june_move_fill",
            "test_days",
            "three_numbers",
            "april_leans",
            "miss_sign",
            "fill_misses",
            "sharpe_ranges",
            "t_multiplier",
            "half_width",
            "mean_ranges",
            "rank_pairs",
            "luck_curve",
            "four_chances",
            "one_year",
            "june_file",
            "handover",
            "check_coverage",
            "edge_day",
            "holiday_rows",
        )
        assert sketches.SLOWER == {
            "gasoline_editions": (250, 1800),
            "half_width": (250, 1800),
            "rank_pairs": (250, 1800),
        }
        assert sketches.DRAW_MS == {"gasoline_editions": whiteboard.FRAME_MS}
        for scene in every:
            frames = sketch_timeline(scene)
            paced = scene.slug in sketches.PACED
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            assert labels, scene.slug
            slower = sketches.SLOWER.get(scene.slug)
            label_ms = slower[1] if slower else sketches.PACED_LABEL_MS
            assert {f.ms for f in labels} == {label_ms if paced else whiteboard.LABEL_MS}, (
                scene.slug
            )
            if slower:
                drawn = [f for f in frames[1:-1] if f not in labels]
                draw_ms = sketches.DRAW_MS.get(scene.slug, slower[0])
                partial = {f.ms for f in drawn if f.partial}
                finished = {f.ms for f in drawn if not f.partial}
                assert partial == {draw_ms} and finished == {slower[0]}, scene.slug
            assert frames[-1].ms == (sketches.PACED_HOLD_MS if paced else HOLD_MS)
            assert [(f.done, f.partial) for f in frames] == [
                (f.done, f.partial) for f in timeline(scene)
            ]

    def test_the_alt_text_says_slow_exactly_when_the_sketch_is_paced(self, every) -> None:
        """A reader learns the pace from the alt text: "drawn slowly" and a
        twelve-second hold for each paced sketch, and neither for the rest."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt = _alt(text, scene)
            paced = scene.slug in sketches.PACED
            assert ("drawn slowly" in alt) == paced, scene.slug
            assert ("twelve seconds" in alt) == paced, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(
        self,
        gifs,
        tmp_path,
        streaks,
        years,
        gasoline,
        guess,
        fill_two,
        misses,
        narrowing,
        split,
        drawdown,
    ) -> None:
        again = make_commodity_seasonals_whiteboards(
            out_dir=tmp_path,
            streaks=streaks,
            years=years,
            gasoline=gasoline,
            guess=guess,
            fill_two=fill_two,
            misses=misses,
            narrowing=narrowing,
            split=split,
            drawdown=drawdown,
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


class TestTheCommittedGifs:
    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, every) -> None:
        for name, scene in zip(GIFS, every, strict=True):
            steps = sketch_timeline(scene)
            committed = FIGURES_DIR / name
            with Image.open(committed) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(committed) == [f.ms for f in steps], name

    def test_each_is_a_fresh_draw_byte_for_byte(self, gifs) -> None:
        system, machine, font = platform.system(), platform.machine(), hand_font()
        if (system, machine, font) != ("Darwin", "arm64", "Comic Sans MS"):
            pytest.skip(
                f"the committed GIFs were drawn on Darwin arm64 in Comic Sans MS, and this is "
                f"{system} {machine} drawing in {font}"
            )
        for path in gifs:
            committed = (FIGURES_DIR / path.name).read_bytes()
            assert (
                hashlib.sha256(path.read_bytes()).hexdigest()
                == hashlib.sha256(committed).hexdigest()
            ), f"{path.name}: redraw with: uv run python -m chan.commodity_seasonals_whiteboard"


class TestTheCommand:
    def test_it_writes_every_gif_into_the_figures_folder(
        self, monkeypatch, tmp_path, capsys
    ) -> None:
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        main()
        assert sorted(path.name for path in tmp_path.glob("*.gif")) == sorted(GIFS)
        assert capsys.readouterr().out.splitlines() == [f"wrote {tmp_path / name}" for name in GIFS]


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(FOLLOWS, GIFS, strict=True):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_gif_is_embedded_once(self) -> None:
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            assert text.count(f"(../docs/figures/{name})") == 1, name

    def test_each_alt_text_quotes_every_label_in_drawing_order(self, every) -> None:
        """Each label is quoted after the one drawn before it, and a label drawn
        twice, such as the calendar's month names, is quoted twice."""
        text = POST.read_text(encoding="utf-8")
        for scene in every:
            alt, at = _alt(text, scene), 0
            for label in scene.labels:
                found = alt.find(f"“{label}”", at)
                assert found >= 0, (scene.slug, label)
                at = found + len(label) + 2


# --- The opening: the two trades and the years after the book's ----------------


class TestTheTwoTradesSketch:
    def test_its_words(self, every) -> None:
        assert every[0].title == "Two trades on one calendar"
        assert every[0].labels == TWO_TRADES_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[0]
        assert _stroke(scene, "axis").color == MUTED
        for month in ("Feb", "Mar", "Apr", "May"):
            assert _label(scene, month).color == MUTED
        for gid in ("gas", "gasoline"):
            assert _stroke(scene, gid).color == INK
            words = [s for s in scene.steps if isinstance(s, Label) and s.names == gid]
            assert [s.color for s in words] == [INK, MUTED, ACCENT], gid

    def test_the_dates_are_the_runs_and_the_posts(self) -> None:
        assert (seasonals.NG_ENTRY, seasonals.NG_EXIT) == ((2, 25), (4, 15))
        assert (seasonals.GASOLINE_ENTRY, seasonals.GASOLINE_EXIT) == ((4, 13), (4, 25))
        text = POST.read_text(encoding="utf-8")
        assert "close of April 13 and sell it at the close of April 25" in text
        assert "close of February 25 and sell it on April 15" in text

    def test_each_bar_runs_from_its_entry_to_its_exit_on_one_scale(self, every) -> None:
        scene = every[0]
        for gid, entry, exit_ in (
            ("gas", seasonals.NG_ENTRY, seasonals.NG_EXIT),
            ("gasoline", seasonals.GASOLINE_ENTRY, seasonals.GASOLINE_EXIT),
        ):
            bar = _stroke(scene, gid)
            assert (bar.x.min(), bar.x.max()) == pytest.approx(
                (_trades_x(entry), _trades_x(exit_))
            ), gid
        first, last = sketches.TRADES_SPAN
        assert (first, last) == (date(sketches.TRADES_YEAR, 2, 1), date(sketches.TRADES_YEAR, 5, 1))
        assert (_trades_x((2, 1)), _trades_x((5, 1))) == pytest.approx(sketches.TRADES_X)
        axis = _stroke(scene, "axis")
        assert (axis.x.min(), axis.x.max()) == pytest.approx(sketches.TRADES_X)
        day = _trades_x((3, 2)) - _trades_x((3, 1))
        assert _trades_x((4, 1)) - _trades_x((3, 1)) == pytest.approx(31 * day)
        for month, words in ((2, "Feb"), (3, "Mar"), (4, "Apr"), (5, "May")):
            assert _label(scene, words).x == pytest.approx(_trades_x((month, 1)))

    def test_natural_gas_sits_above_gasoline_and_both_above_the_months(self, every) -> None:
        scene = every[0]
        gas, gasoline = _stroke(scene, "gas"), _stroke(scene, "gasoline")
        assert gas.y.min() > gasoline.y.max() > sketches.TRADES_AXIS_Y

    def test_the_two_bars_overlap_from_gasolines_entry_to_natural_gass_exit(self, every) -> None:
        gas, gasoline = _stroke(every[0], "gas"), _stroke(every[0], "gasoline")
        assert gasoline.x.min() < gas.x.max() < gasoline.x.max()

    def test_other_dates_move_the_bars_and_the_labels(self) -> None:
        scene = _two_trades(gas=((3, 1), (4, 1)), gasoline=((4, 2), (4, 20)))
        assert "natural gas: buy June contract Mar 1, sell Apr 1" in scene.labels
        assert "gasoline: buy May contract Apr 2, sell Apr 20" in scene.labels
        assert _stroke(scene, "gas").x.min() == pytest.approx(_trades_x((3, 1)))
        assert _stroke(scene, "gasoline").x.max() == pytest.approx(_trades_x((4, 20)))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[0])
        assert "A long black bar runs from February 25 to April 15" in alt
        assert "A short black bar below it runs from April 13 to April 25" in alt
        held = date(2001, *seasonals.NG_EXIT) - date(2001, *seasonals.NG_ENTRY)
        assert held == timedelta(weeks=7) and "about seven weeks" in alt
        gasoline = date(2001, *seasonals.GASOLINE_EXIT) - date(2001, *seasonals.GASOLINE_ENTRY)
        assert gasoline < timedelta(weeks=2) and "the gasoline trade for under two" in alt
        assert "both are open from April 13 to April 15" in alt
        # The ink each part is named in follows the drawing.
        assert "a purple caption under the bar, “Chan: 13 years in a row" in alt
        assert "a purple caption under the label, “Chan: 19 of 21 years" in alt
        assert "with its label on its left, “gasoline:" in alt
        assert alt.count("a grey note") == 2 and alt.count("black bar") == 2


class TestTheSplitFigures:
    def test_the_run_gives_these_years(self, split) -> None:
        assert [year for year, _ in split.gas] == list(range(1994, 2024))
        assert [year for year, _ in split.gasoline] == list(range(1995, 2024))
        assert [year for year, won in split.gasoline if won is None] == [1997, 1998, 1999]
        assert all(won is not None for _, won in split.gas)
        assert (split.gas_end, split.gasoline_end) == (2008, 2015)

    def test_each_side_counts_the_years_won(self, split) -> None:
        assert SplitFigures.won(split.gas, False, split.gas_end) == (15, 15)
        assert SplitFigures.won(split.gas, True, split.gas_end) == (7, 15)
        assert SplitFigures.won(split.gasoline, False, split.gasoline_end) == (16, 18)
        assert SplitFigures.won(split.gasoline, True, split.gasoline_end) == (3, 8)

    def test_the_counts_are_the_opening_tables(self, split) -> None:
        text = POST.read_text(encoding="utf-8")
        for years, end in ((split.gas, split.gas_end), (split.gasoline, split.gasoline_end)):
            (a, n), (b, m) = (SplitFigures.won(years, side, end) for side in (False, True))
            assert (
                rf"\quad\text{{Years won}} & {a} \text{{ of }} {n} & {b} \text{{ of }} {m}" in text
            )

    def test_the_split_falls_where_the_post_s_chart_divides_the_years(self, split) -> None:
        from chan import commodity_seasonals_figures as figures

        assert (split.gas_end, split.gasoline_end) == (
            figures.NG_BOOK_END,
            figures.GASOLINE_BOOK_END,
        )


def _centre(stroke) -> tuple[float, float]:
    """The middle of a stroke's extent, which for a cross is the point it is
    drawn around, since its points are spread unevenly along its arms."""
    return (stroke.x.min() + stroke.x.max()) / 2, (stroke.y.min() + stroke.y.max()) / 2


def _split_counts(scene, tag: str) -> list:
    """The years-won labels either side of a row's dashed line, before then after."""
    return [
        s
        for s in scene.steps
        if isinstance(s, Label) and s.names == f"{tag}-split" and s.text.endswith(" won")
    ]


class TestTheSplitSketch:
    def test_its_words(self, every) -> None:
        assert every[1].title == "Years won, in the book’s years and after"
        assert every[1].labels == SPLIT_LABELS

    def test_its_colours(self, every, split) -> None:
        scene = every[1]
        for tag, years in (("gas", split.gas), ("gasoline", split.gasoline)):
            assert _stroke(scene, f"{tag}-axis").color == MUTED
            assert _stroke(scene, f"{tag}-won").color == GOOD
            for year, won in years:
                if won is False:
                    assert _stroke(scene, f"{tag}-lost-{year}").color == LOST, year
            line = _stroke(scene, f"{tag}-split")
            assert (line.color, line.dashed) == (MUTED, True)
            assert [s.color for s in _split_counts(scene, tag)] == [INK, ACCENT], tag
        assert _label(scene, "natural gas, June contract").color == INK
        assert _label(scene, "gasoline, May contract").color == INK
        assert _stroke(scene, "gap-0").color == MUTED
        for words in (
            "no row",
            "dot: a profitable year   x: a loss",
            "dashed: where the book’s years end",
        ):
            assert _label(scene, words).color == MUTED

    def test_profits_are_dots_and_losses_crosses(self, every) -> None:
        """Colour is never the only cue: a profit is a dot and a loss a cross
        drawn as lines, and a caption names both marks."""
        scene = every[1]
        for tag in ("gas", "gasoline"):
            assert _stroke(scene, f"{tag}-won").dots > 0
        crosses = [s for s in scene.strokes if "-lost-" in s.gid]
        assert crosses and all(s.dots == 0 and s.points > 1 for s in crosses)

    def test_every_mark_sits_at_its_year_on_one_scale(self, every, split) -> None:
        scene = every[1]
        xs = [_split_x(year, split) for year in range(split.first, split.last + 1)]
        assert np.diff(xs) == pytest.approx([xs[1] - xs[0]] * (len(xs) - 1))
        for tag, years, y in (
            ("gas", split.gas, sketches.SPLIT_YS[0]),
            ("gasoline", split.gasoline, sketches.SPLIT_YS[1]),
        ):
            dots = _stroke(scene, f"{tag}-won")
            won = [year for year, w in years if w]
            assert list(dots.x) == pytest.approx([_split_x(year, split) for year in won])
            assert set(dots.y) == {y}
            for year, w in years:
                if w is False:
                    assert _centre(_stroke(scene, f"{tag}-lost-{year}")) == pytest.approx(
                        (_split_x(year, split), y)
                    ), year
        for year in ("1994", "2008", "2015", "2023"):
            assert _label(scene, year).x == pytest.approx(_split_x(int(year), split))

    def test_a_year_with_no_row_gets_no_mark_and_sits_under_the_span(self, every, split) -> None:
        scene = every[1]
        marked = list(_stroke(scene, "gasoline-won").x) + [
            _centre(s)[0] for s in scene.strokes if s.gid.startswith("gasoline-lost-")
        ]
        span = _stroke(scene, "gap-0")
        for year in (1997, 1998, 1999):
            x = _split_x(year, split)
            assert all(abs(m - x) > 0.1 for m in marked), year
            assert span.x.min() < x < span.x.max(), year
        assert span.y.max() < sketches.SPLIT_YS[1]

    def test_each_dashed_line_falls_after_the_last_of_the_books_years(self, every, split) -> None:
        scene = every[1]
        for tag, end in (("gas", split.gas_end), ("gasoline", split.gasoline_end)):
            line = _stroke(scene, f"{tag}-split")
            assert list(line.x) == pytest.approx([_split_x(end + 0.5, split)] * len(line.x)), tag
            before, after = _split_counts(scene, tag)
            assert before.x < line.x[0] < after.x, tag
        gas_losses = [_centre(s)[0] for s in scene.strokes if s.gid.startswith("gas-lost-")]
        assert min(gas_losses) > _stroke(scene, "gas-split").x[0]

    def test_other_figures_move_the_counts_and_the_lines(self) -> None:
        made_up = SplitFigures(
            gas=tuple((year, year % 3 != 0) for year in range(2000, 2011)),
            gasoline=tuple(
                (year, None if year == 2004 else year != 2009) for year in range(2001, 2011)
            ),
            gas_end=2005,
            gasoline_end=2007,
        )
        scene = _after_book(made_up)
        assert {"4 of 6 won", "3 of 5 won", "6 of 6 won", "2 of 3 won"} <= set(scene.labels)
        assert {"2000", "2005", "2007", "2010"} <= set(scene.labels)
        assert "2023" not in scene.labels
        assert _stroke(scene, "gas-split").x[0] == pytest.approx(_split_x(2005.5, made_up))
        assert _stroke(scene, "gap-0").x.mean() == pytest.approx(_split_x(2004, made_up))

    def test_its_alt_text_says_what_the_picture_shows(self, every, split) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[1])
        gas_losses = [year for year, won in split.gas if won is False]
        assert min(gas_losses) > split.gas_end
        assert sketches.WORDS[len(gas_losses)] == "eight"
        assert "Every year before the line is a dot, and all eight crosses fall after it" in alt
        before = [y for y, w in split.gasoline if w is False and y <= split.gasoline_end]
        after = [y for y, w in split.gasoline if w is False and y > split.gasoline_end]
        assert before == [2009, 2012] and "the crosses are 2009 and 2012" in alt
        assert (len(after), SplitFigures.won(split.gasoline, True, split.gasoline_end)[1]) == (5, 8)
        assert "five of the eight years are crosses" in alt
        assert "a dashed grey line after 2008" in alt and "a dashed grey line after 2015" in alt
        assert "A grey span under 1997 to 1999, which have no mark" in alt
        # The inks and the gasoline row's first year follow the drawing.
        assert "a blue dot for each profitable year and a vermilion cross for each loss" in alt
        assert "in purple, “7 of 15 won”" in alt and "in purple, “3 of 8 won”" in alt
        assert f"“gasoline, May contract”, starts in {split.gasoline[0][0]}," in alt


class TestTheDrawdownFigures:
    def test_the_run_marks_each_trading_day_the_files_price_in_2002s_trade(self, drawdown) -> None:
        trade = seasonals.natural_gas_trade(2002)
        assert (drawdown.year, drawdown.entry_day, drawdown.exit_day) == (
            2002,
            trade.entry_day,
            trade.exit_day,
        )
        assert (trade.entry_day, trade.exit_day) == (date(2002, 2, 25), date(2002, 4, 15))
        days = [
            trade.entry_day + timedelta(days=k)
            for k in range((trade.exit_day - trade.entry_day).days + 1)
        ]
        trading = [day for day in days if is_trading_day(day)]
        no_row = [
            day
            for day in trading
            if day
            not in seasonals.settlements(
                seasonals.NATURAL_GAS[seasonals.june_contract_number(day)]
            )[1]
        ]
        assert no_row == [date(2002, 4, 9)]
        assert len(drawdown.returns) == len(trading) - len(no_row) == 34

    def test_the_marks_are_the_runs_returns_over_the_entry_price(self, drawdown) -> None:
        trade = seasonals.natural_gas_trade(2002)
        entry = trade.entry_price
        assert list(drawdown.returns) == [
            float((price - entry) / entry) for price in seasonals.daily_marks(trade)
        ]
        assert drawdown.returns[0] == 0.0
        assert drawdown.returns[-1] == pytest.approx(trade.relative_change)

    def test_the_fall_is_the_runs_drawdown_and_the_book_years(self, drawdown) -> None:
        """The bracket's fall is what :func:`chan.commodity_seasonals.max_drawdown`
        measures on this trade alone, and on all of natural gas's years to 2008,
        which is why the opening table's 22% is this one fall."""
        trade = seasonals.natural_gas_trade(2002)
        assert drawdown.drawdown == pytest.approx(seasonals.max_drawdown([trade]), abs=1e-12)
        book = seasonals.natural_gas_trades(1994, 2008)
        assert drawdown.drawdown == pytest.approx(seasonals.max_drawdown(book), abs=1e-12)
        top, low = drawdown.fall
        assert top == int(np.argmax(drawdown.returns))
        assert low == top + int(np.argmin(drawdown.returns[top:]))
        assert drawdown.drawdown == pytest.approx(0.2151, abs=5e-5)

    def test_the_figures_are_the_posts(self, drawdown) -> None:
        top, _ = drawdown.fall
        peak, fall, end = (
            round(100 * value)
            for value in (drawdown.returns[top], drawdown.drawdown, drawdown.returns[-1])
        )
        assert (peak, fall, end) == (48, 22, 40)
        text = POST.read_text(encoding="utf-8")
        assert (
            f"which rose {peak}%, gave back {fall} points, then recovered to end {end}% up" in text
        )
        assert rf"\quad\text{{Drawdown}} & {fall}\% &" in text

    def test_the_fall_starts_at_the_highest_peak_before_its_low(self) -> None:
        """An early peak whose fall is deeper wins over a later, higher peak
        with a shallow one, as a running peak finds it."""
        made_up = DrawdownFigures(
            2010, date(2010, 2, 25), date(2010, 3, 3), (0.0, 0.3, 0.0, 0.35, 0.3)
        )
        assert made_up.fall == (1, 2)
        assert made_up.drawdown == pytest.approx(0.3)


class TestTheDrawdownSketch:
    def test_its_words(self, every) -> None:
        assert every[2].title == "A 22-point fall inside a winning year"
        assert every[2].labels == DRAWDOWN_LABELS

    def test_its_colours(self, every) -> None:
        """Purple marks the one idea, the fall. Colour is never its only cue,
        since the bracket carries its own words."""
        scene = every[2]
        zero = _stroke(scene, "zero")
        assert (zero.color, zero.dashed) == (MUTED, True)
        assert _stroke(scene, "path").color == INK
        for gid in ("peak", "end"):
            assert _stroke(scene, gid).color == INK
        for gid in ("peak-guide", "low-guide"):
            guide = _stroke(scene, gid)
            assert (guide.color, guide.dashed) == (MUTED, True), gid
        assert _stroke(scene, "fall").color == ACCENT
        colours = {
            "0%": MUTED,
            "Feb 25": MUTED,
            "Apr 15": MUTED,
            "return over the entry price, marked each day the files hold a price": MUTED,
            "peak: +48%": INK,
            "drawdown:": ACCENT,
            "22 points": ACCENT,
            "exit: +40%": INK,
            "a profitable year": INK,
            "natural gas, June contract, 2002": MUTED,
        }
        assert {text: _label(scene, text).color for text in scene.labels} == colours

    def test_each_mark_sits_at_its_trading_day_and_its_return_on_one_scale(
        self, every, drawdown
    ) -> None:
        scene = every[2]
        path = _stroke(scene, "path")
        n = len(drawdown.returns)
        assert path.points == n
        assert list(path.x) == pytest.approx([_drawdown_x(k, drawdown) for k in range(n)])
        assert np.diff(path.x) == pytest.approx([path.x[1] - path.x[0]] * (n - 1))
        assert (path.x[0], path.x[-1]) == pytest.approx(sketches.DRAWDOWN_X)
        returns = np.array(drawdown.returns)
        slope = (path.y[-1] - path.y[0]) / (returns[-1] - returns[0])
        assert list(path.y) == pytest.approx(list(path.y[0] + slope * (returns - returns[0])))
        assert slope > 0
        lo, hi = min(0.0, *drawdown.returns), max(0.0, *drawdown.returns)
        assert (_drawdown_y(lo, drawdown), _drawdown_y(hi, drawdown)) == pytest.approx(
            sketches.DRAWDOWN_Y
        )
        zero = _stroke(scene, "zero")
        assert list(zero.y) == pytest.approx([_drawdown_y(0.0, drawdown)] * zero.points)
        assert path.y[0] == pytest.approx(zero.y[0])
        assert _label(scene, "Feb 25").x == pytest.approx(path.x[0])
        assert _label(scene, "Apr 15").x == pytest.approx(path.x[-1])

    def test_the_dots_sit_on_the_peak_and_the_exit(self, every, drawdown) -> None:
        scene = every[2]
        path = _stroke(scene, "path")
        top, _ = drawdown.fall
        peak, end = _stroke(scene, "peak"), _stroke(scene, "end")
        assert (peak.x[0], peak.y[0]) == pytest.approx((path.x[top], path.y[top]))
        assert peak.y[0] == pytest.approx(path.y.max())
        assert (end.x[0], end.y[0]) == pytest.approx((path.x[-1], path.y[-1]))

    def test_the_bracket_spans_the_fall_from_the_peak_to_its_low(self, every, drawdown) -> None:
        scene = every[2]
        path = _stroke(scene, "path")
        top, low = drawdown.fall
        bracket = _stroke(scene, "fall")
        assert (bracket.y.min(), bracket.y.max()) == pytest.approx((path.y[low], path.y[top]))
        scale = (_drawdown_y(1.0, drawdown) - _drawdown_y(0.0, drawdown)) / 1.0
        assert (bracket.y.max() - bracket.y.min()) / scale == pytest.approx(drawdown.drawdown)
        stem = np.median(bracket.x)
        assert stem == pytest.approx(sketches.DRAWDOWN_BRACKET_X)
        for gid, k in (("peak-guide", top), ("low-guide", low)):
            guide = _stroke(scene, gid)
            assert list(guide.y) == pytest.approx([path.y[k]] * guide.points), gid
            assert path.x[k] < guide.x.min() and guide.x.max() < bracket.x.min(), gid
        for text in ("exit: +40%", "a profitable year"):
            label = _label(scene, text)
            assert path.x[-1] < label.x < bracket.x.min(), text
            assert path.y[low] < label.y < path.y[top], text
        for text in ("drawdown:", "22 points"):
            label = _label(scene, text)
            assert label.x > bracket.x.max(), text
            assert path.y[low] < label.y < path.y[top], text

    def test_other_figures_move_the_title_and_the_labels(self) -> None:
        made_up = DrawdownFigures(
            2010, date(2010, 3, 1), date(2010, 3, 8), (0.0, 0.1, 0.3, -0.05, 0.2, -0.1)
        )
        scene = _drawdown(made_up)
        assert scene.title == "A 40-point fall inside a losing year"
        assert scene.slug == "drawdown_2010"
        assert {
            "Mar 1",
            "Mar 8",
            "peak: +30%",
            "40 points",
            "exit: −10%",
            "a losing year",
            "natural gas, June contract, 2010",
        } <= set(scene.labels)
        path = _stroke(scene, "path")
        assert path.y.min() == pytest.approx(sketches.DRAWDOWN_Y[0])
        assert path.y.max() == pytest.approx(sketches.DRAWDOWN_Y[1])
        assert _stroke(scene, "peak").x[0] == pytest.approx(_drawdown_x(2, made_up))

    def test_its_alt_text_says_what_the_picture_shows(self, every, drawdown) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[2])
        returns = drawdown.returns
        top, low = drawdown.fall
        dip = int(np.argmin(returns))
        assert -0.05 < returns[dip] < 0 and dip < 5
        assert "The line dips just below zero in its first week" in alt
        assert top == int(np.argmax(returns)) and "climbs to a black dot at its high" in alt
        assert low == top + int(np.argmin(returns[top:]))
        assert "from the peak and from the lowest point after it to a purple bracket" in alt
        assert returns[low] < returns[-1] < returns[top]
        assert "which sits between the two guides" in alt
        assert "so the year ended ahead after falling 22 points inside it" in alt
        assert "A dashed grey line marks “0%”" in alt and "A black line traces" in alt
        assert "A note right of the dates names the trade" in alt
        # The one trading day with no row, which the figures test finds.
        assert "every trading day but April 9" in alt


# --- Lesson 1: the streak sketch -----------------------------------------------


class TestTheStreakFigures:
    def test_the_run_gives_profitable_years_to_2008_and_a_loss_in_2009(self, streaks) -> None:
        assert streaks.years == tuple((year, year < 2009) for year in range(1994, 2010))
        assert streaks.loss == 2009

    def test_each_count_ends_where_the_runs_streak_reaches_it(self, streaks) -> None:
        gas = seasonals.natural_gas_trades(*seasonals.NG_YEARS)
        for start in sketches.STARTS:
            runs = seasonals.runs_ending([t for t in gas if t.year >= start])
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                assert runs[end] == count
                assert end - start + 1 == count

    def test_counted_from_1995_the_streaks_end_in_2007_and_2008_and_from_1994_a_year_earlier(
        self, streaks
    ) -> None:
        assert streaks.ends == {1995: (2007, 2008), 1994: (2006, 2007)}

    def test_the_book_counts_are_chans(self) -> None:
        assert sketches.BOOK_COUNTS == ((13, "main text"), (14, "sidebar"))
        assert sketches.STARTS == (1995, 1994)


class TestTheStreakSketch:
    def test_its_words(self, every) -> None:
        assert every[3].title == "The start year decides where a streak ends"
        assert every[3].labels == STREAK_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[3]
        assert _stroke(scene, "profitable").color == GOOD
        assert _label(scene, "dot: a profitable year").color == GOOD
        assert _label(scene, "natural gas, June contract").color == MUTED
        assert _stroke(scene, "loss").color == LOST
        assert _label(scene, "loss").color == LOST
        release = _stroke(scene, "release")
        assert (release.color, release.dashed) == (MUTED, True)
        for start, color in ((1995, ACCENT), (1994, INK)):
            for count in (13, 14):
                gid = f"from-{start}-{count}"
                assert _stroke(scene, gid).color == color, gid
                (label,) = [s for s in scene.steps if isinstance(s, Label) and s.names == gid]
                assert label.color == color, gid

    def test_profitable_years_are_dots_and_the_loss_a_cross(self, every, streaks) -> None:
        """Colour is never the only cue: a profitable year is a dot and the loss
        a cross drawn as lines, each named by its own label."""
        scene = every[3]
        dots, cross = _stroke(scene, "profitable"), _stroke(scene, "loss")
        assert dots.dots > 0 and cross.dots == 0 and cross.points > 1
        won = [year for year, profitable in streaks.years if profitable]
        assert dots.x == pytest.approx([_streak_x(year, streaks) for year in won])
        assert set(dots.y) == {STREAK_AXIS_Y}
        assert cross.x.mean() == pytest.approx(_streak_x(streaks.loss, streaks))

    def test_years_sit_at_one_scale(self, every, streaks) -> None:
        xs = [_streak_x(year, streaks) for year, _ in streaks.years]
        assert np.diff(xs) == pytest.approx([xs[1] - xs[0]] * (len(xs) - 1))
        for year in ("1994", "1995", "2006", "2007", "2008", "2009"):
            assert _label(every[3], year).x == pytest.approx(_streak_x(int(year), streaks))

    def test_each_bracket_runs_from_its_start_to_its_end(self, every, streaks) -> None:
        scene = every[3]
        for start in sketches.STARTS:
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                bracket = _stroke(scene, f"from-{start}-{count}")
                assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
                    (_streak_x(start, streaks), _streak_x(end, streaks))
                )

    def test_1995_sits_above_the_axis_and_1994_below(self, every) -> None:
        scene = every[3]
        for count in (13, 14):
            assert _stroke(scene, f"from-1995-{count}").y.min() > STREAK_AXIS_Y
            assert _stroke(scene, f"from-1994-{count}").y.max() < STREAK_AXIS_Y
        # The longer streak sits further from the axis on each side.
        assert _stroke(scene, "from-1995-14").y.min() > _stroke(scene, "from-1995-13").y.max()
        assert _stroke(scene, "from-1994-14").y.max() < _stroke(scene, "from-1994-13").y.min()

    def test_the_release_sits_in_november_2008_after_every_bracket(self, every, streaks) -> None:
        scene = every[3]
        release = _stroke(scene, "release")
        assert FIRST_EDITION == (2008, 11)
        slot = _streak_x(2009, streaks) - _streak_x(2008, streaks)
        assert release.x[0] == pytest.approx(_streak_x(2008, streaks) + (10.5 / 12 - 0.5) * slot)
        assert set(release.x) == {release.x[0]}
        brackets = [s for s in scene.strokes if s.gid.startswith("from-")]
        assert max(b.x.max() for b in brackets) < release.x[0] < _streak_x(2009, streaks)

    def test_other_figures_move_the_marks_and_the_labels(self) -> None:
        made_up = StreakFigures(
            years=tuple((year, year != 2001) for year in range(1985, 2002)),
            ends={1995: (2000, 2001), 1994: (1999, 2000)},
        )
        scene = _streak_start(made_up)
        assert made_up.loss == 2001
        assert _stroke(scene, "from-1995-13").x.max() == pytest.approx(_streak_x(2000, made_up))
        assert _stroke(scene, "loss").x.mean() == pytest.approx(_streak_x(2001, made_up))
        assert {"1994", "1995", "1999", "2000", "2001"} <= set(scene.labels)
        assert "1985" not in scene.labels
        assert "2009" not in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every, streaks) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[3])
        assert "a blue dot" in alt and "a vermilion cross" in alt and "dashed grey line" in alt
        assert "names the trade as “natural gas, June contract”" in alt
        for start, colour in ((1995, "purple"), (1994, "black")):
            assert f"two {colour} brackets start at {start}" in alt
            for (count, _), end in zip(sketches.BOOK_COUNTS, streaks.ends[start], strict=True):
                assert re.search(rf"“{count} from {start}[^”]*” ends at {end}", alt), (start, count)


# --- Lesson 1: the gasoline sketch ---------------------------------------------


class TestTheGasolineFigures:
    def test_the_run_gives_these_years(self, gasoline) -> None:
        assert [year for year, _ in gasoline.years] == list(range(1995, 2016))
        assert gasoline.lost == [2009, 2012]
        assert gasoline.gaps == [1997, 1998, 1999]
        assert len(gasoline.won) == 16

    def test_the_count_is_chans_and_spans_the_axis(self, gasoline) -> None:
        """Chan's 19 of 21 counts the 21 years the axis draws."""
        assert sketches.GASOLINE_COUNT == (19, 21)
        assert len(gasoline.years) == sketches.GASOLINE_COUNT[1]

    def test_no_loss_falls_in_the_first_editions_years(self, gasoline) -> None:
        assert min(gasoline.lost) > FIRST_EDITION[0]


class TestTheGasolineSketch:
    def test_its_words(self, every) -> None:
        assert every[4].title == "Gasoline’s two claims read as two editions"
        assert every[4].labels == GASOLINE_LABELS

    def test_its_colours(self, every, gasoline) -> None:
        scene = every[4]
        assert _stroke(scene, "profitable").color == GOOD
        assert _label(scene, "dot: a profitable year").color == GOOD
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").color == LOST
        assert _label(scene, "x: a loss, 2009 and 2012").color == LOST
        assert _stroke(scene, "gap-0").color == MUTED
        assert _label(scene, "no row").color == MUTED
        release = _stroke(scene, "release")
        assert (release.color, release.dashed) == (MUTED, True)
        assert _stroke(scene, "sidebar").color == ACCENT
        assert _label(scene, "sidebar: a profit every year since 1995").color == ACCENT
        assert _stroke(scene, "main-text").color == INK
        assert _label(scene, "main text: 19 of 21, as of 2015").color == INK
        assert _label(scene, "May contract").color == MUTED

    def test_every_mark_sits_at_its_year_on_one_scale(self, every, gasoline) -> None:
        scene = every[4]
        dots = _stroke(scene, "profitable")
        assert list(dots.x) == pytest.approx([_gasoline_x(y, gasoline) for y in gasoline.won])
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").x.mean() == pytest.approx(
                _gasoline_x(year, gasoline)
            )
        for year in ("1995", "2008", "2015"):
            assert _label(scene, year).x == pytest.approx(_gasoline_x(int(year), gasoline))

    def test_a_year_with_no_row_gets_no_mark_and_sits_under_the_span(self, every, gasoline) -> None:
        scene = every[4]
        marked = list(_stroke(scene, "profitable").x) + [
            _stroke(scene, f"loss-{year}").x.mean() for year in gasoline.lost
        ]
        span = _stroke(scene, "gap-0")
        for year in gasoline.gaps:
            x = _gasoline_x(year, gasoline)
            assert all(abs(m - x) > 0.1 for m in marked), year
            assert span.x.min() - 1e-9 <= x <= span.x.max() + 1e-9, year
        assert span.y.max() < sketches.GASOLINE_AXIS_Y
        note = _label(scene, "no row")
        assert note.x == pytest.approx((span.x.min() + span.x.max()) / 2)
        assert note.y < span.y.min()

    def test_the_sidebar_ends_before_the_release_and_the_main_text_covers_every_loss(
        self, every, gasoline
    ) -> None:
        scene = every[4]
        sidebar, main_text = _stroke(scene, "sidebar"), _stroke(scene, "main-text")
        release = _stroke(scene, "release").x[0]
        first_loss = _gasoline_x(min(gasoline.lost), gasoline)
        assert sidebar.x.min() == pytest.approx(_gasoline_x(1995, gasoline))
        assert sidebar.x.max() == pytest.approx(_gasoline_x(FIRST_EDITION[0], gasoline))
        assert sidebar.x.max() < release < first_loss
        assert main_text.x.min() == pytest.approx(_gasoline_x(1995, gasoline))
        assert main_text.x.max() == pytest.approx(_gasoline_x(2015, gasoline))
        assert main_text.x.max() >= _gasoline_x(max(gasoline.lost), gasoline)
        assert sketches.GASOLINE_AXIS_Y < sidebar.y.min() and sidebar.y.max() < main_text.y.min()

    def test_other_figures_move_the_marks_and_the_labels(self) -> None:
        outcomes = {1999: None, 2002: None, 2003: None, 2004: False, 2010: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2011))
        )
        scene = _gasoline_editions(made_up)
        assert "x: a loss, 2004 and 2010" in scene.labels
        assert "main text: 19 of 21, as of 2010" in scene.labels
        assert {"1995", "2008", "2010"} <= set(scene.labels)
        assert "2015" not in scene.labels
        assert scene.labels.count("no row") == 2
        assert _stroke(scene, "gap-1").x.max() == pytest.approx(_gasoline_x(2003, made_up))
        assert _stroke(scene, "main-text").x.max() == pytest.approx(_gasoline_x(2010, made_up))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[4])
        assert "2009 and 2012 each have a vermilion cross" in alt
        assert "Under 1997 to 1999, which have no mark" in alt
        assert (
            "a purple bracket, “sidebar: a profit every year since 1995”, runs from 1995 to 2008"
            in alt
        )
        assert "ends before the dashed line and before either cross" in alt
        assert "a black bracket, “main text: 19 of 21, as of 2015”, runs from 1995 to 2015" in alt


# --- Lesson 2: the range, the guess, Chan's 19 and the fill misses ---------------


def _span_ends(stroke) -> tuple[float, float]:
    return stroke.x.min(), stroke.x.max()


class TestTheRangeSketch:
    def test_its_words(self, every) -> None:
        assert every[5].title == "Three missing rows leave a range, not a count"
        assert every[5].labels == RANGE_LABELS

    def test_its_colours(self, every, gasoline) -> None:
        scene = every[5]
        assert _stroke(scene, "profitable").color == GOOD
        for year in gasoline.lost:
            assert _stroke(scene, f"loss-{year}").color == LOST
        assert _stroke(scene, "gaps").color == MUTED
        assert _stroke(scene, "range").color == ACCENT
        assert _label(scene, "the files allow 16 to 19").color == ACCENT
        assert _stroke(scene, "chan").color == INK
        assert _label(scene, "Chan: 19").color == INK

    def test_the_range_runs_from_the_files_profits_to_those_plus_the_gaps(
        self, every, gasoline
    ) -> None:
        scene = every[5]
        low, high = len(gasoline.won), len(gasoline.won) + len(gasoline.gaps)
        assert (low, high) == (16, 19)
        left, right = _span_ends(_stroke(scene, "range"))
        assert left == pytest.approx(_count_x(low, gasoline))
        assert right == pytest.approx(_count_x(high, gasoline))
        for n in range(low - 1, high + 2):
            assert _label(scene, str(n)).x == pytest.approx(_count_x(n, gasoline))

    def test_chans_count_sits_at_the_top_end(self, every, gasoline) -> None:
        chan = _stroke(every[5], "chan")
        assert list(chan.x) == pytest.approx(
            [_count_x(sketches.GASOLINE_COUNT[0], gasoline)] * len(chan.x)
        )
        assert chan.x[0] == pytest.approx(_span_ends(_stroke(every[5], "range"))[1])

    def test_other_figures_move_the_range_and_the_title(self) -> None:
        outcomes = {2000: None, 2001: None, 2004: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2011))
        )
        scene = _gap_range(made_up)
        assert scene.title == "Two missing rows leave a range, not a count"
        assert "the files allow 13 to 15" in scene.labels
        assert "profitable years of 16" in scene.labels
        assert [str(n) for n in range(12, 17)] == [
            label for label in scene.labels if label.isdigit() and len(label) == 2
        ]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[5])
        assert "a vermilion cross at 2009 and 2012" in alt
        assert "A grey span under 1997 to 1999, which have no mark" in alt
        assert "A purple bracket over 16 to 19" in alt
        assert "a black mark at 19, the bracket’s top end" in alt


class TestTheGuessFigures:
    def test_it_reads_the_runs_fill_and_the_prices_around_it(self, guess) -> None:
        assert guess.fill == seasonals.gap_fills()[0]
        days = [day for day, _ in guess.prices]
        assert (days[0], days[-1]) == (date(1997, 4, 7), date(1997, 4, 25))
        missing = [
            day
            for day in (date(1997, 4, 7) + timedelta(days=k) for k in range(19))
            if seasonals.is_trading_day(day) and day not in days
        ]
        assert missing == [date(1997, 4, d) for d in (11, 14, 16, 18)]
        assert len(days) == 11
        assert guess.top == pytest.approx(guess.fill.linear + guess.fill.linear_error)
        assert guess.bottom == pytest.approx(guess.fill.linear - guess.fill.linear_error)


class TestTheInterpolationSketch:
    def test_its_words(self, every) -> None:
        assert every[7].title == "Interpolating turns a gap into a guess"
        assert every[7].labels == GUESS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[7]
        assert _stroke(scene, "prices").color == INK
        exit_line = _stroke(scene, "exit")
        assert (exit_line.color, exit_line.dashed) == (MUTED, True)
        assert _stroke(scene, "line").color == ACCENT
        assert _stroke(scene, "guess").color == ACCENT
        assert _label(scene, "straight-line guess 61.6¢").color == ACCENT
        assert _stroke(scene, "loss-zone").color == LOST
        assert _label(scene, "entry here: a loss").color == LOST
        assert _stroke(scene, "profit-zone").color == GOOD
        assert _label(scene, "entry here: a profit").color == GOOD

    def test_each_price_sits_at_its_trading_day_and_price(self, every, guess) -> None:
        prices = _stroke(every[7], "prices")
        assert list(prices.x) == pytest.approx([_guess_x(d, guess) for d, _ in guess.prices])
        assert list(prices.y) == pytest.approx([_guess_y(p, guess) for _, p in guess.prices])
        steps = np.diff(prices.x)
        gap = list(prices.x).index(_guess_x(guess.fill.before, guess))
        assert steps[gap] == pytest.approx(3 * steps[0])

    def test_the_guess_lies_on_the_line(self, every, guess) -> None:
        scene = every[7]
        line, dot = _stroke(scene, "line"), _stroke(scene, "guess")
        x0, x1, y0, y1 = line.x[0], line.x[-1], line.y[0], line.y[-1]
        on_line = y0 + (dot.x[0] - x0) * (y1 - y0) / (x1 - x0)
        assert dot.y[0] == pytest.approx(on_line)
        assert dot.x[0] == pytest.approx(_guess_x(guess.fill.day, guess))
        assert dot.y[0] == pytest.approx(_guess_y(guess.fill.linear, guess))

    def test_the_band_is_one_typical_miss_either_side_split_at_the_exit(self, every, guess) -> None:
        scene = every[7]
        loss, profit = _stroke(scene, "loss-zone"), _stroke(scene, "profit-zone")
        exit_y = _guess_y(guess.fill.other, guess)
        assert (loss.y.min(), loss.y.max()) == pytest.approx((exit_y, _guess_y(guess.top, guess)))
        assert (profit.y.min(), profit.y.max()) == pytest.approx(
            (_guess_y(guess.bottom, guess), exit_y)
        )
        exit_line = _stroke(scene, "exit")
        assert list(exit_line.y) == pytest.approx([exit_y] * len(exit_line.y))

    def test_the_guess_is_a_profit_and_the_band_reaches_a_loss(self, guess) -> None:
        assert guess.bottom < guess.fill.linear < float(guess.fill.other) < guess.top

    def test_other_figures_move_the_guess_and_the_band(self, guess) -> None:
        moved = dataclasses.replace(guess.fill, linear=0.600, linear_error=0.010)
        scene = _interpolation_guess(GuessFigures(prices=guess.prices, fill=moved))
        assert "straight-line guess 60.0¢" in scene.labels
        assert {"61.0¢", "59.0¢"} <= set(scene.labels)

    def test_its_alt_text_says_what_the_picture_shows(self, every, guess) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[7])
        assert "settlements one trading day apart" in alt
        days = [day for day, _ in guess.prices]
        span = (days[0] + timedelta(n) for n in range((days[-1] - days[0]).days + 1))
        missed = [str(d.day) for d in span if is_trading_day(d) and d not in days]
        missed.remove(str(guess.fill.day.day))
        assert f"The file misses April {', '.join(missed[:-1])} and {missed[-1]} too" in alt
        assert "The guess sits in the blue part, and the band reaches into the vermilion" in alt


class TestTheChanNeedsGapsSketch:
    def test_its_words(self, every) -> None:
        assert every[6].title == "Chan’s 19 needs all three gaps to be profits"
        assert every[6].labels == NEEDS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[6]
        for gid in ("chan-won", "files-won"):
            assert _stroke(scene, gid).color == GOOD, gid
        for gid in ("chan-lost", "files-lost"):
            assert _stroke(scene, gid).color == LOST, gid
        gap = _stroke(scene, "files-gap")
        assert (gap.color, gap.dashed) == (MUTED, True)
        assert _stroke(scene, "needs").color == ACCENT
        assert _label(scene, "1997 to 1999 must all be profits for Chan’s 19").color == ACCENT

    def test_each_box_spans_its_count(self, every, gasoline) -> None:
        scene = every[6]
        won = len(gasoline.won)
        spans = {
            "chan-won": (0, 19),
            "chan-lost": (19, 21),
            "files-won": (0, won),
            "files-gap": (won, won + len(gasoline.gaps)),
            "files-lost": (won + len(gasoline.gaps), 21),
        }
        for gid, (a, b) in spans.items():
            assert _span_ends(_stroke(scene, gid)) == pytest.approx(
                (_bar_x(a, gasoline), _bar_x(b, gasoline))
            ), gid

    def test_the_missing_years_fill_the_gap_to_chans_profits(self, every) -> None:
        scene = every[6]
        assert _span_ends(_stroke(scene, "files-gap"))[1] == pytest.approx(
            _span_ends(_stroke(scene, "chan-won"))[1]
        )
        assert _span_ends(_stroke(scene, "files-lost")) == pytest.approx(
            _span_ends(_stroke(scene, "chan-lost"))
        )

    def test_other_figures_move_the_boxes_and_the_labels(self) -> None:
        outcomes = {2000: None, 2001: None, 2004: False, 2007: False}
        made_up = GasolineFigures(
            years=tuple((year, outcomes.get(year, True)) for year in range(1995, 2016))
        )
        scene = _chan_needs_gaps(made_up)
        assert scene.title == "Chan’s 19 needs all two gaps to be profits"
        assert {"17 profits", "2004, 2007"} <= set(scene.labels)
        assert "2000 to 2001 must all be profits for Chan’s 19" in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[6])
        assert "two bars of 21 years" in alt
        assert "both bars end in the same two losses" in alt
        assert "sits under the last three of Chan’s profits" in alt


class TestTheFillTwoSketch:
    def test_its_words(self, every) -> None:
        assert every[8].title == "Fill 2 carries June’s move across the gap"
        assert every[8].labels == FILL_TWO_LABELS

    def test_its_colours_and_marks(self, every, fill_two) -> None:
        scene = every[8]
        may = _stroke(scene, "may")
        assert (may.color, may.dots) == (INK, 6.0)
        for k in range(len(fill_two.june)):
            ring = _stroke(scene, f"june-{k}")
            assert (ring.color, ring.dots) == (MUTED, 0.0), k
            assert len(ring.x) > 1 and ring.x[0] == pytest.approx(ring.x[-1]), k
        assert _stroke(scene, "june-rise").color == MUTED
        assert _stroke(scene, "may-rise").color == ACCENT
        assert _stroke(scene, "guess").color == ACCENT
        assert _stroke(scene, "loss-zone").color == LOST
        assert _stroke(scene, "profit-zone").color == GOOD
        exit_line = _stroke(scene, "exit")
        assert (exit_line.color, exit_line.dashed) == (MUTED, True)

    def test_it_reads_the_runs_fill_two_and_both_contracts(self, fill_two) -> None:
        fill = seasonals.gap_fills()[0]
        assert fill_two.fill == fill
        assert fill_two.window == (date(1997, 4, 7), date(1997, 4, 17))
        june = dict(fill_two.june)
        may = dict(fill_two.may)
        assert fill.day not in may and fill.day in june
        assert float(may[fill.base] + june[fill.day] - june[fill.base]) == pytest.approx(fill.june)

    def test_each_mark_sits_at_its_trading_day_and_price(self, every, fill_two) -> None:
        scene = every[8]
        may = _stroke(scene, "may")
        assert list(may.x) == pytest.approx([_fill_two_x(d, fill_two) for d, _ in fill_two.may])
        assert list(may.y) == pytest.approx([_fill_two_y(p, fill_two) for _, p in fill_two.may])
        for k, (d, p) in enumerate(fill_two.june):
            ring = _stroke(scene, f"june-{k}")
            assert (ring.x.min() + ring.x.max()) / 2 == pytest.approx(
                _fill_two_x(d, fill_two), abs=1e-6
            ), k
            assert (ring.y.min() + ring.y.max()) / 2 == pytest.approx(
                _fill_two_y(p, fill_two), abs=1e-6
            ), k

    def test_both_arrows_rise_by_junes_change(self, every, fill_two) -> None:
        """The purple arrow is the grey one carried onto May: same start day,
        same end point, same rise."""
        scene = every[8]
        fill, june, may = fill_two.fill, dict(fill_two.june), dict(fill_two.may)
        grey, purple = _stroke(scene, "june-rise"), _stroke(scene, "may-rise")
        assert (grey.x[0], purple.x[0]) == pytest.approx((_fill_two_x(fill.base, fill_two),) * 2)
        assert grey.y[0] == pytest.approx(_fill_two_y(june[fill.base], fill_two))
        assert purple.y[0] == pytest.approx(_fill_two_y(may[fill.base], fill_two))
        tip = lambda stroke: max(range(len(stroke.x)), key=lambda i: stroke.x[i])  # noqa: E731
        grey_rise = grey.y[tip(grey)] - grey.y[0]
        purple_rise = purple.y[tip(purple)] - purple.y[0]
        assert grey_rise == pytest.approx(purple_rise)
        assert purple.y[tip(purple)] == pytest.approx(_fill_two_y(fill.june, fill_two))
        assert _stroke(scene, "guess").y[0] == pytest.approx(_fill_two_y(fill.june, fill_two))

    def test_no_may_dot_sits_on_junes_arrow(self, every, fill_two) -> None:
        """Each May dot clears the grey June arrow by 5 pixels, edge to edge, so
        no May price reads as part of June's path. A straight arrow put April
        10's dot on the line."""
        scene = every[8]
        grey, may = _stroke(scene, "june-rise"), _stroke(scene, "may")
        dot_radius, half_line = 6.0 * 100 / 72 / 2, grey.width * 100 / 72 / 2
        for x, y in zip(may.x, may.y, strict=True):
            gap = np.hypot(grey.x - x, grey.y - y).min() * 68 - dot_radius - half_line
            assert gap >= 5, (x, y, gap)

    def test_the_band_is_fill_twos_miss_split_at_the_exit(self, every, fill_two) -> None:
        scene = every[8]
        loss, profit = _stroke(scene, "loss-zone"), _stroke(scene, "profit-zone")
        exit_y = _fill_two_y(fill_two.fill.other, fill_two)
        assert (loss.y.min(), loss.y.max()) == pytest.approx(
            (exit_y, _fill_two_y(fill_two.top, fill_two))
        )
        assert (profit.y.min(), profit.y.max()) == pytest.approx(
            (_fill_two_y(fill_two.bottom, fill_two), exit_y)
        )
        assert fill_two.bottom < fill_two.fill.june < float(fill_two.fill.other) < fill_two.top
        assert (fill_two.bottom, fill_two.top) == pytest.approx((0.612063, 0.629937), abs=1e-6)

    def test_other_figures_move_the_guess_and_the_band(self, fill_two) -> None:
        moved = dataclasses.replace(fill_two.fill, june_error=0.002)
        scene = _june_move_fill(dataclasses.replace(fill_two, fill=moved))
        assert {"62.3¢", "61.9¢"} <= set(scene.labels)

    def test_its_alt_text_says_what_the_picture_shows(self, every, fill_two) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[8])
        assert "Black dots are the May gasoline contract’s settlements and grey rings" in alt
        first, last = fill_two.window
        assert f"apart from April {first.day} to April {last.day}, {last.year}" in alt
        days = [first + timedelta(n) for n in range((last - first).days + 1)]
        trading = [day for day in days if is_trading_day(day)]
        june = {day for day, _ in fill_two.june}
        no_ring = [str(day.day) for day in trading if day not in june]
        assert f"June has no ring on April {_or(no_ring)}." in alt
        may = {day for day, _ in fill_two.may}
        no_dot = [str(d.day) for d in trading if d not in may and d != fill_two.fill.day]
        assert f"nor on April {_or(no_dot)}." in alt
        base = fill_two.fill.base
        assert base == max(d for d in may if d in june and d < fill_two.fill.day)
        assert f"carries June from April {base.day}, the last day both files hold," in alt
        assert f"toward April {fill_two.fill.day.day}, labelled" in alt
        assert f"a purple arrow of the same rise starts at May’s April {base.day} price" in alt
        assert "The guess sits in the blue part just under the line" in alt


class TestTheTestDaysSketch:
    def test_its_words(self, every) -> None:
        assert every[9].title == "Which April days can test a fill"
        assert every[9].labels == NARROW_LABELS

    def test_it_counts_the_runs_test_days(self, narrowing) -> None:
        fill = seasonals.gap_fills()[0]
        assert narrowing.fill == fill
        assert narrowing.counts == seasonals.count_test_days(fill) == (247, 187, 108, 80)
        assert narrowing.counts[-1] == fill.tested

    def test_each_bar_is_drawn_to_scale(self, every, narrowing) -> None:
        scene = every[9]
        for k, count in enumerate(narrowing.counts):
            bar = _stroke(scene, f"stage-{k}")
            assert bar.x.max() == pytest.approx(_narrow_end(count, narrowing)), k
            assert bar.x.min() == pytest.approx(sketches.NARROW_X0), k
        lengths = [_stroke(scene, f"stage-{k}").x.max() - sketches.NARROW_X0 for k in range(4)]
        assert lengths == sorted(lengths, reverse=True)

    def test_each_drop_is_the_gap_between_two_bars(self, every, narrowing) -> None:
        drops = [label for label in every[9].labels if label.startswith("−")]
        counts = narrowing.counts
        assert [int(d.split(":")[0][1:]) for d in drops] == [
            counts[k - 1] - counts[k] for k in range(1, len(counts))
        ]

    def test_its_inks(self, every) -> None:
        scene = every[9]
        assert [_stroke(scene, f"stage-{k}").color for k in range(4)] == [INK, INK, INK, ACCENT]
        assert _label(scene, "80").color == ACCENT

    def test_other_figures_move_the_bars_and_labels(self, narrowing) -> None:
        scene = _test_days(dataclasses.replace(narrowing, counts=(200, 150, 100, 50)))
        assert {"200", "150", "100", "50", "−50: fall outside April"} <= set(scene.labels)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[9])
        assert "four bars drawn to scale, each shorter than the one above" in alt
        assert "Most of the days lost lack a price in EIA’s files" in alt


class TestTheThreeNumbersSketch:
    def test_its_words(self, every) -> None:
        assert every[10].title == "One set of misses, three numbers"
        assert every[10].labels == THREE_LABELS

    def test_its_inks(self, every) -> None:
        scene = every[10]
        assert _stroke(scene, "misses").color == INK
        assert _stroke(scene, "average").color == ACCENT
        assert _stroke(scene, "spread").color == INK
        assert _stroke(scene, "typical").color == MUTED
        zero = _stroke(scene, "zero")
        assert (zero.color, zero.dashed) == (MUTED, True)

    def test_it_reads_every_test_day_of_1997s_pattern(self, misses) -> None:
        fill = seasonals.gap_fills()[0]
        assert misses.fill == fill
        assert len(misses.misses) == fill.tested == 80
        assert [day for day, *_ in misses.misses] == sorted(day for day, *_ in misses.misses)

    def test_one_dot_per_test_day_in_its_stack(self, every, misses) -> None:
        dots = _stroke(every[10], "misses")
        xs, ys = _miss_stacks(misses.cents)
        assert len(dots.x) == len(misses.misses)
        assert list(dots.x) == pytest.approx(xs)
        assert list(dots.y) == pytest.approx(ys)

    def test_its_three_numbers_are_the_runs(self, every, misses) -> None:
        """The average, spread and typical miss it draws are the ones the
        chances and the table use."""
        scene, fill = every[10], misses.fill
        assert _stroke(scene, "average").x[0] == pytest.approx(_miss_x(100 * fill.june_bias))
        spread = _stroke(scene, "spread")
        assert (spread.x.min(), spread.x.max()) == pytest.approx(
            (
                _miss_x(100 * (fill.june_bias - fill.june_spread)),
                _miss_x(100 * (fill.june_bias + fill.june_spread)),
            )
        )
        typical = _stroke(scene, "typical")
        assert (typical.x.min(), typical.x.max()) == pytest.approx(
            (_miss_x(-100 * fill.june_error), _miss_x(100 * fill.june_error))
        )

    def test_other_figures_move_the_marks(self, misses) -> None:
        shifted = dataclasses.replace(
            misses, misses=tuple((d, b, m + 0.01) for d, b, m in misses.misses)
        )
        scene = _three_numbers(shifted)
        assert "average +1.26¢, spread ±0.86¢" in scene.labels
        assert _stroke(scene, "average").x[0] == pytest.approx(_miss_x(1.2575), abs=1e-3)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[10])
        assert "More of the dots sit right of zero than left" in alt
        assert "shifted right of zero by the lean" in alt


class TestTheAprilsSketch:
    def test_its_words(self, every) -> None:
        assert every[11].title == "Twelve Aprils, eight lean low"
        assert every[11].labels == APRIL_LABELS

    def test_one_bar_per_april_at_its_average(self, every, misses) -> None:
        scene = every[11]
        for year, cents in misses.by_april.items():
            bar = _stroke(scene, f"april-{year}")
            mean = sum(cents) / len(cents)
            end = bar.x.max() if mean > 0 else bar.x.min()
            assert end == pytest.approx(_april_x(mean)), year
            assert bar.color == (ACCENT if mean > 0 else MUTED), year
        assert sum(len(c) for c in misses.by_april.values()) == len(misses.misses)

    def test_eight_of_twelve_lean_low_and_three_carry_most(self, misses) -> None:
        means = {y: sum(c) / len(c) for y, c in misses.by_april.items()}
        assert sum(1 for m in means.values() if m > 0) == 8
        biggest = sorted(means, key=means.get, reverse=True)[:3]
        assert sorted(biggest) == [1996, 2001, 2003]

    def test_other_figures_move_the_title(self, misses) -> None:
        lowered = dataclasses.replace(
            misses, misses=tuple((d, b, m - 0.01) for d, b, m in misses.misses)
        )
        scene = _april_leans(lowered)
        assert scene.title == "Twelve Aprils, none lean low"

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[11])
        assert "Eight bars, in purple, run right of zero" in alt
        assert "for 1996, 2001 and 2003, carry most of the lean" in alt


class TestTheMissSignSketch:
    def test_its_words(self, every) -> None:
        assert every[12].title == "A miss at the entry subtracts, at the exit it adds"
        assert every[12].labels == SIGN_LABELS

    def test_its_inks(self, every) -> None:
        scene = every[12]
        for tag in ("entry", "exit"):
            assert _stroke(scene, f"{tag}-known").color == INK
            assert _stroke(scene, f"{tag}-guess").color == ACCENT
            assert _stroke(scene, f"{tag}-lifted").color == MUTED
            assert _stroke(scene, f"{tag}-m").color == ACCENT
            assert _stroke(scene, f"{tag}-c").color == INK
            for k in range(3):
                guide = _stroke(scene, f"{tag}-guide-{k}")
                assert (guide.color, guide.dashed) == (MUTED, True)

    def test_the_entry_panel_sits_left_of_the_divider_and_the_exit_right(self, every) -> None:
        scene = every[12]
        divider = _stroke(scene, "divider").x[0]
        for gid in ("known", "guess", "lifted", "m", "c"):
            assert _stroke(scene, f"entry-{gid}").x.max() < divider, gid
            assert _stroke(scene, f"exit-{gid}").x.min() > divider, gid

    def test_it_draws_1997s_entry_and_1998s_exit(self) -> None:
        entry, exit_ = seasonals.gap_fills()[:2]
        assert (entry.year, entry.leg, exit_.year, exit_.leg) == (1997, "entry", 1998, "exit")

    def test_each_bracket_spans_its_prices(self, every) -> None:
        scene = every[12]
        for tag, f in zip(("entry", "exit"), seasonals.gap_fills()[:2], strict=True):
            known, guess, lifted = float(f.other), f.june, f.june + f.june_bias
            m, c = _stroke(scene, f"{tag}-m"), _stroke(scene, f"{tag}-c")
            assert (m.y.min(), m.y.max()) == pytest.approx(
                tuple(sorted((_sign_y(guess, f), _sign_y(known, f))))
            ), tag
            assert (c.y.min(), c.y.max()) == pytest.approx(
                tuple(sorted((_sign_y(lifted, f), _sign_y(known, f))))
            ), tag
            ring = _stroke(scene, f"{tag}-lifted")
            assert (ring.y.min() + ring.y.max()) / 2 == pytest.approx(_sign_y(lifted, f)), tag

    def test_the_lift_shortens_the_entry_and_lengthens_the_exit_by_the_miss(self, every) -> None:
        scene = every[12]
        for tag, f, sign in zip(("entry", "exit"), seasonals.gap_fills()[:2], (-1, 1), strict=True):
            m, c = _stroke(scene, f"{tag}-m"), _stroke(scene, f"{tag}-c")
            m_len, c_len = m.y.max() - m.y.min(), c.y.max() - c.y.min()
            lift = _sign_y(f.june + f.june_bias, f) - _sign_y(f.june, f)
            assert lift == pytest.approx(f.june_bias * 100 * sketches.SIGN_CENT), tag
            assert c_len == pytest.approx(m_len + sign * lift), tag

    def test_each_arrow_says_its_miss_in_cents(self, every) -> None:
        """The post quotes these two values, so the drawing has to show them."""
        scene = every[12]
        for f in seasonals.gap_fills()[:2]:
            assert f"e = {100 * f.june_bias:.2f}¢" in scene.labels
        text = POST.read_text(encoding="utf-8")
        cents = [f"{100 * f.june_bias:.2f}" for f in seasonals.gap_fills()[:2]]
        assert f"{cents[0]} cents for 1997 and {cents[1]} for 1998" in text

    def test_other_figures_move_the_prices_and_labels(self) -> None:
        entry, exit_ = seasonals.gap_fills()[:2]
        scene = _miss_sign(dataclasses.replace(entry, june=0.619), exit_)
        assert "guess 61.9¢" in scene.labels
        assert "guess 62.1¢" not in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[12])
        assert "a black one from the ring up to the exit, labelled “m − e”, which is shorter" in alt
        assert "labelled “m + e”, is longer" in alt


class TestTheFillMissesSketch:
    def test_its_words(self, every) -> None:
        assert every[13].title == "Each corrected move against fill 2’s spread"
        assert every[13].labels == MISS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[13]
        zero = _stroke(scene, "zero")
        assert (zero.color, zero.dashed) == (MUTED, True)
        assert _label(scene, "loss").color == LOST
        assert _label(scene, "profit").color == GOOD
        for year in (1997, 1998, 1999):
            assert _stroke(scene, f"move-{year}").color == ACCENT
            assert _stroke(scene, f"miss-{year}").color == INK

    def test_each_dot_and_bar_sit_at_the_runs_figures(self, every) -> None:
        scene = every[13]
        for fill in seasonals.gap_fills():
            move, miss = 100 * fill.move(fill.june_corrected), 100 * fill.june_spread
            assert _stroke(scene, f"move-{fill.year}").x[0] == pytest.approx(_cents_x(move))
            assert _span_ends(_stroke(scene, f"miss-{fill.year}")) == pytest.approx(
                (_cents_x(move - miss), _cents_x(move + miss))
            )

    def test_each_bar_carries_its_sigma_over_its_right_half(self, every) -> None:
        scene = every[13]
        for fill in seasonals.gap_fills():
            move, miss = 100 * fill.move(fill.june_corrected), 100 * fill.june_spread
            label = _label(scene, f"σ = {miss:.2f}¢")
            assert label.names == f"miss-{fill.year}"
            assert label.x == pytest.approx(_cents_x(move + miss / 2))
            assert label.y > _stroke(scene, f"miss-{fill.year}").y.max()

    def test_a_bar_crosses_zero_exactly_when_its_move_is_under_one_spread(self, every) -> None:
        """Every dot is a profit. 1997's and 1998's bars cross zero and 1999's
        stops short, because only 1999's corrected move clears one spread."""
        scene = every[13]
        zero = _stroke(scene, "zero").x[0]
        crossing = {}
        for fill in seasonals.gap_fills():
            left, right = _span_ends(_stroke(scene, f"miss-{fill.year}"))
            assert right > zero and _stroke(scene, f"move-{fill.year}").x[0] > zero, fill.year
            crossing[fill.year] = left < zero
            assert crossing[fill.year] == (fill.june_margin < 1), fill.year
        assert crossing == {1997: True, 1998: True, 1999: False}

    def test_other_figures_move_the_rows(self) -> None:
        fills = seasonals.gap_fills()
        sure = dataclasses.replace(fills[0], june_spread=0.0002)
        scene = _fill_misses((sure, *fills[1:]))
        left, _ = _span_ends(_stroke(scene, "miss-1997"))
        assert left > _stroke(scene, "zero").x[0]
        assert "100%" in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[13])
        assert (
            "a purple dot right of zero marks the year’s move with fill 2’s guess corrected" in alt
        )
        assert "the bar for 1998 only just reaches past it, and the bar for 1999 stops" in alt


class TestTheSharpeSketch:
    def test_its_words(self, every) -> None:
        assert every[14].title == "How far each Sharpe ratio can stray"
        assert every[14].labels == SHARPE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[14]
        zero = _stroke(scene, "zero")
        assert (zero.color, zero.dashed) == (MUTED, True)
        assert _label(scene, "loses").color == LOST
        assert _label(scene, "earns").color == GOOD
        for trade, first, _ in PERIODS:
            assert _stroke(scene, f"range-{trade}-{first}").color == INK
            assert _stroke(scene, f"ratio-{trade}-{first}").color == ACCENT

    def test_each_dot_and_bar_sit_at_the_runs_figures(self, every) -> None:
        """Read from the run's own functions, not from the sketch's rows."""
        scene = every[14]
        for trade, first, last in PERIODS:
            trades = (
                seasonals.natural_gas_trades(first, last)
                if trade == "natural gas"
                else seasonals.gasoline_trades(first, last)
            )
            ratio = seasonals.sharpe_ratio(trades)
            error = seasonals.sharpe_standard_error(trades)
            tag = f"{trade}-{first}"
            assert _stroke(scene, f"ratio-{tag}").x[0] == pytest.approx(_sharpe_x(ratio))
            assert _span_ends(_stroke(scene, f"range-{tag}")) == pytest.approx(
                (_sharpe_x(ratio - 1.96 * error), _sharpe_x(ratio + 1.96 * error))
            )

    def test_only_the_bars_after_the_book_cross_zero(self, every) -> None:
        scene = every[14]
        zero = _stroke(scene, "zero").x[0]
        crossing = {}
        for trade, first, _ in PERIODS:
            left, right = _span_ends(_stroke(scene, f"range-{trade}-{first}"))
            crossing[(trade, first)] = left < zero < right
        assert crossing == {
            ("natural gas", 1994): False,
            ("natural gas", 2009): True,
            ("gasoline", 1995): False,
            ("gasoline", 2016): True,
        }

    def test_other_figures_move_the_dots_and_labels(self) -> None:
        rows = sharpe_rows()
        moved = (dataclasses.replace(rows[0], ratio=1.5), *rows[1:])
        scene = _sharpe_ranges(moved)
        assert "1.5" in scene.labels and "1.0" not in scene.labels
        assert _stroke(scene, "ratio-natural gas-1994").x[0] == pytest.approx(_sharpe_x(1.5))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[14])
        assert "The first bar runs from about 0.4 to 1.6 and the third stays right of zero" in alt
        assert "the bars of both periods after the book reach across the zero line" in alt
        first = sharpe_rows()[0]
        assert (round(first.low, 1), round(first.high, 1)) == (0.4, 1.6)


class TestTheMultiplierSketch:
    def test_its_words(self, every) -> None:
        assert every[15].title == "Fewer results, a wider range"
        assert every[15].labels == T_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[15]
        rows = mean_rows()
        ours = (rows[3].count, rows[1].count)
        for n in (*ours, T_COMPARE, 1000):
            assert _stroke(scene, f"bar-{n}").color == (ACCENT if n in ours else INK), n
        normal = _stroke(scene, "normal")
        assert (normal.color, normal.dashed) == (MUTED, True)

    def test_each_bar_is_its_multiplier_and_the_counts_are_the_runs(self, every) -> None:
        from scipy import stats

        scene = every[15]
        rows = mean_rows()
        assert (rows[3].count, rows[1].count) == (8, 15)
        for n in (8, 15, T_COMPARE, 1000):
            bar = _stroke(scene, f"bar-{n}")
            assert bar.y.max() == pytest.approx(T_BASE + stats.t.ppf(0.975, n - 1) * T_UNIT), n
        line = _stroke(scene, "normal")
        assert line.y[0] == pytest.approx(T_BASE + stats.norm.ppf(0.975) * T_UNIT)

    def test_other_counts_move_the_bars_and_the_note(self) -> None:
        scene = _t_multiplier((5, 12))
        assert "purple: the later periods’ 5 and 12 years" in scene.labels
        assert "5 results" in scene.labels and "8 results" not in scene.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[15])
        assert "the fewer the results, the higher a bar stands above it" in alt


class TestTheHalfWidthSketch:
    def test_its_words(self, every) -> None:
        assert every[16].title == "Where ±12% comes from"
        assert every[16].labels == HALF_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[16]
        assert [_stroke(scene, f"half-{k}").color for k in range(3)] == [INK, INK, ACCENT]
        for name in ("start", "gap"):
            line = _stroke(scene, name)
            assert (line.color, line.dashed) == (MUTED, True), name

    def test_each_bar_is_the_runs_figure_and_the_last_passes_the_gap(self, every) -> None:
        from scipy import stats

        scene = every[16]
        before, after = mean_rows()[0], mean_rows()[1]
        trades = seasonals.natural_gas_trades(2009, 2023)
        low, high = seasonals.mean_interval(trades)
        half = 100 * (high - low) / 2
        widths = (
            after.spread,
            after.spread / math.sqrt(after.count),
            stats.t.ppf(0.975, after.count - 1) * after.spread / math.sqrt(after.count),
        )
        assert widths[2] == pytest.approx(half)
        for k, width in enumerate(widths):
            assert _span_ends(_stroke(scene, f"half-{k}")) == pytest.approx(
                (HALF_X, HALF_X + width * HALF_POINT)
            ), k
        gap = _stroke(scene, "gap").x[0]
        assert gap == pytest.approx(HALF_X + (before.mean - after.mean) * HALF_POINT)
        assert _span_ends(_stroke(scene, "half-2"))[1] > gap
        line, purple = _stroke(scene, "gap"), _stroke(scene, "half-2")
        assert line.y.min() < purple.y.min() and line.y.max() > purple.y.max()

    def test_every_bar_starts_on_the_dashed_line_at_the_later_mean(self, every) -> None:
        scene = every[16]
        start = _stroke(scene, "start")
        assert start.x == pytest.approx(np.full(len(start.x), HALF_X))
        bars = [_stroke(scene, f"half-{k}") for k in range(3)]
        assert start.y.min() < min(bar.y.min() for bar in bars)
        assert start.y.max() > max(bar.y.max() for bar in bars)
        assert scene.steps.index(start) < min(scene.steps.index(bar) for bar in bars)

    def test_the_title_follows_the_figures(self) -> None:
        before, after = mean_rows()[0], mean_rows()[1]
        wide = dataclasses.replace(after, spread=30.0)
        assert _half_width(wide, before).title == "Where ±17% comes from"

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[16])
        assert "the purple bar reaches past it, so the range around the later mean holds" in alt


class TestTheMeanRangeSketch:
    def test_its_words(self, every) -> None:
        assert every[17].title == "One range holds the earlier mean, one does not"
        assert every[17].labels == MEAN_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[17]
        for trade, first, _ in PERIODS:
            assert _stroke(scene, f"range-{trade}-{first}").color == INK
            assert _stroke(scene, f"mean-{trade}-{first}").color == ACCENT
        for trade in ("natural gas", "gasoline"):
            carry = _stroke(scene, f"carry-{trade}")
            assert (carry.color, carry.dashed) == (MUTED, True)

    def test_each_dot_and_bar_sit_at_the_runs_figures(self, every) -> None:
        scene = every[17]
        for trade, first, last in PERIODS:
            trades = (
                seasonals.natural_gas_trades(first, last)
                if trade == "natural gas"
                else seasonals.gasoline_trades(first, last)
            )
            mean = 100 * seasonals.mean_return(trades)
            low, high = seasonals.mean_interval(trades)
            tag = f"{trade}-{first}"
            assert _stroke(scene, f"mean-{tag}").x[0] == pytest.approx(_mean_x(mean))
            assert _span_ends(_stroke(scene, f"range-{tag}")) == pytest.approx(
                (_mean_x(100 * low), _mean_x(100 * high))
            )

    def test_natural_gas_s_earlier_mean_lands_inside_and_gasoline_s_outside(self, every) -> None:
        scene = every[17]
        landed = {}
        for trade, later in (("natural gas", 2009), ("gasoline", 2016)):
            x = _stroke(scene, f"carry-{trade}").x[0]
            bar = _stroke(scene, f"range-{trade}-{later}")
            left, right = _span_ends(bar)
            landed[trade] = left < x < right
            carry = _stroke(scene, f"carry-{trade}")
            assert carry.y.min() < bar.y.min() and carry.y.max() > bar.y.max(), trade
        assert landed == {"natural gas": True, "gasoline": False}

    def test_each_range_is_the_runs_low_then_high(self) -> None:
        for row, (trade, first, last) in zip(mean_rows(), PERIODS, strict=True):
            trades = (
                seasonals.natural_gas_trades(first, last)
                if trade == "natural gas"
                else seasonals.gasoline_trades(first, last)
            )
            low, high = seasonals.mean_interval(trades)
            assert (row.low, row.high) == pytest.approx((100 * low, 100 * high)), trade

    def test_other_figures_move_the_rows(self) -> None:
        rows = mean_rows()
        moved = (dataclasses.replace(rows[0], mean=5.0), *rows[1:])
        scene = _mean_ranges(moved)
        assert "+5.0%" in scene.labels
        assert _stroke(scene, "carry-natural gas").x[0] == pytest.approx(_mean_x(5.0))

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[17])
        assert "Natural gas’s lands inside the later range, and gasoline’s lands just past" in alt

    def test_the_three_come_in_the_post_s_order(self) -> None:
        assert [s.slug for s in _mean_scenes(mean_rows())] == [
            "t_multiplier",
            "half_width",
            "mean_ranges",
        ]


def _natural_gas_periods() -> tuple[list, list]:
    return seasonals.natural_gas_trades(1994, 2008), seasonals.natural_gas_trades(2009, 2023)


class TestThePairsSketch:
    def test_its_words(self, every) -> None:
        assert every[18].title == "177 of 225 pairs"
        assert every[18].labels == PAIRS_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[18]
        strokes = {gid: _stroke(scene, gid).color for gid in ("won", "lost", "edge")}
        assert strokes == {"won": GOOD, "lost": LOST, "edge": INK}
        assert _label(scene, "blue: the earlier year did better").color == GOOD
        assert _label(scene, "vermilion: the later year did").color == LOST

    def test_each_dot_sits_in_its_cell_in_the_colour_of_who_won(self, every) -> None:
        scene, f = every[18], OneYearFigures.from_run()
        rows = sorted(r for _, r in f.before)
        cols = sorted(r for _, r in f.after)

        def cells(gid: str) -> set[tuple[int, int]]:
            stroke = _stroke(scene, gid)
            got = set()
            for x, y in zip(stroke.x, stroke.y, strict=True):
                j, i = (x - PAIRS_X0) / PAIRS_CELL - 0.5, (y - PAIRS_Y0) / PAIRS_CELL - 0.5
                assert (j, i) == pytest.approx((round(j), round(i)))
                got.add((round(i), round(j)))
            return got

        won, lost = cells("won"), cells("lost")
        assert won == {(i, j) for i, r in enumerate(rows) for j, c in enumerate(cols) if r > c}
        assert won | lost == {(i, j) for i in range(len(rows)) for j in range(len(cols))}
        assert not won & lost
        assert all((i, len(cols) - 1) in lost for i in range(len(rows)))

    def test_the_count_is_the_rank_test_s(self, every) -> None:
        won, pairs = seasonals.pairs_won(*_natural_gas_periods())
        assert len(_stroke(every[18], "won").x) == won
        assert every[18].title == f"{won:.0f} of {pairs} pairs"

    def test_the_edge_follows_each_row_s_last_blue_dot(self, every) -> None:
        scene, f = every[18], OneYearFigures.from_run()
        edge = _stroke(scene, "edge")
        for i, r in enumerate(sorted(r for _, r in f.before)):
            beaten = sum(1 for _, c in f.after if c < r)
            y = PAIRS_Y0 + (i + 0.5) * PAIRS_CELL
            at = [x for x, ey in zip(edge.x, edge.y, strict=True) if abs(ey - y) < 1e-9]
            assert at == pytest.approx([PAIRS_X0 + beaten * PAIRS_CELL]), i

    def test_the_title_follows_the_figures(self) -> None:
        f = OneYearFigures.from_run()
        worse = dataclasses.replace(f, before=tuple((y, r - 100) for y, r in f.before))
        assert _pairs(worse).title.endswith(f"of {len(f.before) * len(f.after)} pairs")
        assert _pairs(worse).title != _pairs(f).title

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[18])
        for label in PAIRS_LABELS:
            assert f"“{label}”" in alt, label
        assert "The rightmost column, headed “2022”, is all vermilion" in alt


class TestTheLuckSketch:
    def test_its_words(self, every) -> None:
        assert every[19].title == "What 0.7% means"
        assert every[19].labels == LUCK_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[19]
        assert [_stroke(scene, g).color for g in ("ours", "tail-high", "tail-low")] == [ACCENT] * 3
        assert _stroke(scene, "bell").color == INK
        for gid in ("middle", "five"):
            assert (_stroke(scene, gid).color, _stroke(scene, gid).dashed) == (MUTED, True)

    def test_its_shaded_share_is_the_rank_test_s_p_value(self, every) -> None:
        p = seasonals.rank_p_value(*_natural_gas_periods())
        assert every[19].title == f"What {100 * p:.1f}% means"
        assert _luck(OneYearFigures.from_run()).title == every[19].title

    def test_the_counts_are_the_exact_distribution(self) -> None:
        """Each count's chance is its share of every way to split the years,
        counted by brute force on small splits, and the chances add to one."""
        from itertools import combinations

        for m, n in ((3, 4), (5, 5), (4, 7)):
            tally = np.zeros(m * n + 1)
            for earlier in combinations(range(m + n), m):
                later = set(range(m + n)) - set(earlier)
                tally[sum(1 for e in earlier for x in later if e > x)] += 1
            assert pair_count_chances(m, n) == pytest.approx(tally / tally.sum()), (m, n)
        chances = pair_count_chances(15, 15)
        assert len(chances) == 226
        assert chances.sum() == pytest.approx(1)
        assert chances == pytest.approx(chances[::-1])

    def test_its_curve_and_marks_sit_at_the_counts(self, every) -> None:
        scene, f = every[19], OneYearFigures.from_run()
        n1, n2 = len(f.before), len(f.after)
        won, _ = seasonals.pairs_won(*_natural_gas_periods())
        won = int(won)
        chances = pair_count_chances(n1, n2)
        mu, sd = n1 * n2 / 2, math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
        lo, hi = mu - LUCK_SPAN * sd, mu + LUCK_SPAN * sd

        def x_of(u: float) -> float:
            return LUCK_X[0] + (u - lo) / (hi - lo) * (LUCK_X[1] - LUCK_X[0])

        bell = _stroke(scene, "bell")
        for u in (100, 112, 150, 177):
            at = np.isclose(bell.x, x_of(u))
            assert at.any() and bell.y[at][0] == pytest.approx(
                LUCK_BASE + LUCK_PEAK * chances[u] / chances.max()
            ), u
        assert _stroke(scene, "middle").x[0] == pytest.approx(x_of(mu))
        assert _stroke(scene, "ours").x[0] == pytest.approx(x_of(won))
        five = _stroke(scene, "five").x[0]
        line = min(u for u in range(113, n1 * n2 + 1) if 2 * chances[u:].sum() <= 0.05)
        assert 2 * chances[line - 1 :].sum() > 0.05
        assert five == pytest.approx(x_of(line))
        assert five < _stroke(scene, "ours").x[0]
        high, low = _stroke(scene, "tail-high"), _stroke(scene, "tail-low")
        assert high.x.min() == pytest.approx(x_of(won))
        assert low.x.max() == pytest.approx(x_of(n1 * n2 - won))
        assert high.y.min() == pytest.approx(LUCK_BASE) and low.y.min() == pytest.approx(LUCK_BASE)
        assert 2 * chances[won:].sum() == pytest.approx(
            seasonals.rank_p_value(*_natural_gas_periods())
        )

    def test_the_title_follows_the_figures(self) -> None:
        f = OneYearFigures.from_run()
        closer = dataclasses.replace(f, before=tuple((y, r - 12) for y, r in f.before))
        assert _luck(closer).title != _luck(f).title

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[19])
        for label in LUCK_LABELS:
            assert f"“{label}”" in alt, label
        assert "The tails are so thin that they barely rise off the axis." in alt


class TestTheChancesSketch:
    def test_its_words(self, every) -> None:
        assert every[20].title == "Four chances against the 5% line"
        assert every[20].labels == CHANCE_LABELS

    def test_the_rows_are_the_run_s_chances(self) -> None:
        gas = seasonals.gasoline_trades(1995, 2015), seasonals.gasoline_trades(2016, 2023)
        ng = _natural_gas_periods()
        want = [
            ("gasoline", seasonals.change_p_value(*gas), seasonals.rank_p_value(*gas)),
            ("natural gas", seasonals.change_p_value(*ng), seasonals.rank_p_value(*ng)),
        ]
        got = [(r.trade, r.welch / 100, r.rank / 100) for r in chance_rows()]
        assert [g[0] for g in got] == [w[0] for w in want]
        for g, w in zip(got, want, strict=True):
            assert g[1:] == pytest.approx(w[1:])

    def test_each_dot_sits_at_its_chance(self, every) -> None:
        scene = every[20]
        assert _stroke(scene, "line").x[0] == pytest.approx(CHANCE_X0 + CHANCE_LINE * CHANCE_POINT)
        for row, y in zip(chance_rows(), CHANCE_ROWS, strict=True):
            for test, pct, dy in (
                ("Welch", row.welch, CHANCE_DY),
                ("Mann-Whitney", row.rank, -CHANCE_DY),
            ):
                dot = _stroke(scene, f"{row.trade}-{test}")
                assert (dot.x[0], dot.y[0]) == pytest.approx(
                    (CHANCE_X0 + pct * CHANCE_POINT, y + dy)
                )

    def test_only_a_chance_past_the_line_is_purple(self, every) -> None:
        scene = every[20]
        purple = [s.gid for s in scene.strokes if s.color == ACCENT]
        assert purple == ["natural gas-Welch"]
        made_up = (ChanceRow("gasoline", 6.0, 1.0), ChanceRow("natural gas", 4.0, 0.5))
        assert [s.gid for s in _chances(made_up).strokes if s.color == ACCENT] == ["gasoline-Welch"]
        on_line = (ChanceRow("gasoline", CHANCE_LINE, 1.0), ChanceRow("natural gas", 4.0, 0.5))
        assert [s.gid for s in _chances(on_line).strokes if s.color == ACCENT] == ["gasoline-Welch"]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[20])
        for label in CHANCE_LABELS:
            assert f"“{label}”" in alt, label
        assert "a purple dot at “Welch, 9.2%”, the only one right of the line" in alt


class TestTheOneYearSketch:
    @staticmethod
    def ranked(f: OneYearFigures) -> list[tuple[float, str, int]]:
        return sorted(
            [(r, "before", y) for y, r in f.before] + [(r, "after", y) for y, r in f.after]
        )

    def test_its_words(self, every) -> None:
        assert every[21].title == "One year moves the mean, not the ranks"
        assert every[21].labels == ONE_YEAR_LABELS

    def test_its_colours(self, every) -> None:
        scene, f = every[21], OneYearFigures.from_run()
        for year, pct in f.after:
            assert _stroke(scene, f"year-{year}").color == (GOOD if pct > 0 else LOST), year
        assert _stroke(scene, "mean").color == INK
        assert _stroke(scene, "mean-without").color == ACCENT
        for year, _ in f.before:
            assert _stroke(scene, f"rank-{year}").color == INK
        for year, _ in f.after:
            assert _stroke(scene, f"rank-{year}").color == ACCENT

    def test_the_figures_are_the_runs(self) -> None:
        f = OneYearFigures.from_run()
        after = seasonals.natural_gas_trades(2009, 2023)
        assert f.mean_after == pytest.approx(100 * seasonals.mean_return(after))
        best = max(after, key=lambda trade: trade.relative_change)
        rest = [trade for trade in after if trade is not best]
        assert f.best == (best.year, pytest.approx(100 * best.relative_change))
        assert f.mean_without_best == pytest.approx(100 * seasonals.mean_return(rest))
        assert (len(f.before), len(f.after)) == (15, 15)

    def test_each_tick_sits_at_its_mean(self, every) -> None:
        scene, f = every[21], OneYearFigures.from_run()
        assert list(_stroke(scene, "mean").x) == pytest.approx(
            [_year_x(f.mean_after)] * len(_stroke(scene, "mean").x)
        )
        without = _stroke(scene, "mean-without").x
        assert list(without) == pytest.approx([_year_x(f.mean_without_best)] * len(without))

    def test_each_return_dot_sits_at_its_true_return(self, every) -> None:
        """No rounding moves a dot, so each one sits on its true side of zero and
        of both mean ticks. 2021's −4.5% once sat left of the −5.0% tick."""
        scene, f = every[21], OneYearFigures.from_run()
        means = (0.0, f.mean_after, f.mean_without_best)
        for year, pct in f.after:
            x = _stroke(scene, f"year-{year}").x[0]
            assert x == pytest.approx(_year_x(pct)), year
            for mean in means:
                assert (x < _year_x(mean)) == (pct < mean), (year, mean)
        dots = [_stroke(scene, f"year-{year}") for year, _ in f.after]
        for k, one in enumerate(dots):
            for two in dots[k + 1 :]:
                if one.y[0] == two.y[0]:
                    assert abs(one.x[0] - two.x[0]) >= sketches.YEAR_DOT_GAP, (one.gid, two.gid)

    def test_a_note_names_each_gain_too_close_to_zero_to_show_its_side(self, every) -> None:
        """2014's +0.09% sits half a pixel right of the zero line, so its side
        cannot be seen and colour alone would mark it a gain."""
        scene, f = every[21], OneYearFigures.from_run()
        near = sorted(y for y, pct in f.after if 0 < pct < sketches.YEAR_NEAR_ZERO)
        assert near == [2014, 2018]
        zero = _stroke(scene, "zero").x[0]
        for year in near:
            assert (_stroke(scene, f"year-{year}").x[0] - zero) * 68 < 5, year
        assert _label(scene, "2014 and 2018: just above 0%").color == GOOD
        others = OneYearFigures(
            before=f.before, after=tuple((y, 5.0 if y in near else r) for y, r in f.after)
        )
        assert not any("just above" in label for label in _one_year(others).labels)

    def test_each_rank_dot_sits_in_its_row_in_rank_order(self, every) -> None:
        scene, f = every[21], OneYearFigures.from_run()
        ranked = self.ranked(f)
        xs = [_stroke(scene, f"rank-{year}").x[0] for _, _, year in ranked]
        assert xs == sorted(xs)
        assert (xs[0], xs[-1]) == pytest.approx(RANK_X)
        for _, period, year in ranked:
            row = RANK_BEFORE_Y if period == "before" else RANK_AFTER_Y
            assert _stroke(scene, f"rank-{year}").y[0] == pytest.approx(row), year
        assert [period for _, period, _ in ranked[:9]] == ["after"] * 9
        assert ranked[9][1] == "before"
        assert ranked[-1][2] == f.best[0] == 2022

    def test_a_smaller_2022_moves_the_mean_and_no_rank(self) -> None:
        """2022 at +45% is still above every year before 2009, so it keeps the
        top rank and every other dot stays put, while the mean falls."""
        f = OneYearFigures.from_run()
        smaller = OneYearFigures(
            before=f.before,
            after=tuple((y, 45.0 if y == 2022 else r) for y, r in f.after),
        )
        assert max(r for _, r in f.before) < 45.0
        big, small = _one_year(f), _one_year(smaller)
        for _, _, year in self.ranked(f):
            assert _stroke(big, f"rank-{year}").x[0] == _stroke(small, f"rank-{year}").x[0]
        assert smaller.mean_after < f.mean_after
        assert "2022: +45%" in small.labels

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[21])
        f = OneYearFigures.from_run()
        losses = sum(r < 0 for _, r in f.after)
        gains = len(f.after) - losses
        expected = (
            f"left of zero for the {losses} losses and blue right of it for the {gains} gains"
        )
        assert expected in alt
        assert "The nine worst ranks all belong to years after 2008" in alt
        assert "2022 takes the top rank on the right" in alt


# --- Lesson 5: the calendar sketch ---------------------------------------------


def _reaches(scene, tag: str, x: float) -> list[str]:
    """The months whose bar in year ``tag`` reaches the vertical line at ``x``."""
    return [
        month
        for month in ("march", "april", "may", "june")
        if _stroke(scene, f"{tag}-{month}").x.max() >= x
    ]


class TestTheJuneYears:
    def test_the_run_gives_these_dates_and_files(self, years) -> None:
        still, expired = years
        assert (still.year, still.entry, still.last_trade[0]) == (
            2008,
            date(2008, 2, 25),
            date(2008, 2, 27),
        )
        assert (expired.year, expired.entry, expired.last_trade[0]) == (
            2006,
            date(2006, 2, 27),
            date(2006, 2, 24),
        )
        assert (still.entry_number, still.exit_number) == (4, 2)
        assert (expired.entry_number, expired.exit_number) == (3, 2)
        assert (still.exit, expired.exit) == (date(2008, 4, 15), date(2006, 4, 13))

    def test_each_number_is_the_file_the_trade_reads(self, years) -> None:
        for f in years:
            trade = seasonals.natural_gas_trade(f.year)
            assert trade.entry_symbol == seasonals.NATURAL_GAS[f.entry_number]
            assert trade.exit_symbol == seasonals.NATURAL_GAS[f.exit_number]
            assert f.last_trade == tuple(ng_last_trade(f.year, month) for month in (3, 4, 5, 6))

    def test_each_number_counts_the_contracts_still_trading(self, years) -> None:
        """A contract still trades on its own last day, so June's number is how
        many of the four have a last trading day on or after the day."""
        for f in years:
            for day, number in ((f.entry, f.entry_number), (f.exit, f.exit_number)):
                assert sum(last >= day for last in f.last_trade) == number

    def test_2007_is_left_out_because_its_entry_is_marchs_last_day(self) -> None:
        trade = seasonals.natural_gas_trade(2007)
        assert trade.entry_day == ng_last_trade(2007, 3)

    def test_march_still_trades_on_its_own_last_day(self) -> None:
        """2007 enters on March's last trading day, where the run reads June as
        contract 4, so its note would call March still trading."""
        f = sketches.JuneYear.from_run(2007)
        assert f.entry == f.last_trade[0]
        assert (f.march_trading, f.entry_number) == (True, 4)


class TestTheJuneSketch:
    def test_its_words(self, every) -> None:
        assert every[22].title == "Which file holds the June contract"
        assert every[22].labels == JUNE_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[22]
        for tag in ("2008", "2006"):
            assert _stroke(scene, f"{tag}-june").color == ACCENT
            for month in ("march", "april", "may"):
                assert _stroke(scene, f"{tag}-{month}").color == INK
            for moment in ("entry", "exit"):
                line = _stroke(scene, f"{tag}-{moment}")
                assert (line.color, line.dashed) == (MUTED, True)
        for step in scene.steps:
            if not isinstance(step, Label):
                continue
            if re.fullmatch(r"(June is )?contract \d on \w+ \d+", step.text) or step.text == "June":
                assert step.color == ACCENT, step.text
            elif step.text in {"March", "April", "May"} or step.text.startswith("March "):
                assert step.color == MUTED, step.text

    def test_the_calendar_is_one_scale_of_days(self) -> None:
        assert _day_x(CALENDAR[0]) == pytest.approx(CALENDAR_X[0])
        assert _day_x(CALENDAR[1]) == pytest.approx(CALENDAR_X[1])
        per_day = _day_x(date(2008, 3, 2)) - _day_x(date(2008, 3, 1))
        assert _day_x(date(2008, 4, 15)) - _day_x(date(2008, 2, 25)) == pytest.approx(50 * per_day)
        # Month and day decide the place, not the year.
        assert _day_x(date(2006, 4, 13)) == _day_x(date(2008, 4, 13))

    def test_each_bar_ends_at_its_last_trading_day_and_june_runs_off(self, every, years) -> None:
        scene = every[22]
        for f in years:
            for month, last in zip(("march", "april", "may"), f.last_trade, strict=False):
                bar = _stroke(scene, f"{f.year}-{month}")
                assert bar.x.max() == pytest.approx(_day_x(last)), (f.year, month)
                assert bar.x.min() == pytest.approx(CALENDAR_X[0])
            june = _stroke(scene, f"{f.year}-june")
            assert june.x.min() == pytest.approx(CALENDAR_X[0])
            # The shaft runs flat along June's row from the calendar's start
            # past its end, so a shortened shaft bends away from the row.
            shaft = june.x <= CALENDAR_X[1]
            assert june.y[shaft] == pytest.approx([june.y[0]] * int(shaft.sum()))
            assert june.x.max() > CALENDAR_X[1]
            assert f.last_trade[3] > CALENDAR[1].replace(year=f.year)

    def test_june_is_numbered_by_the_bars_each_line_crosses(self, every, years) -> None:
        scene = every[22]
        for f in years:
            tag = str(f.year)
            for moment, day, number in (
                ("entry", f.entry, f.entry_number),
                ("exit", f.exit, f.exit_number),
            ):
                line = _stroke(scene, f"{tag}-{moment}")
                assert line.x == pytest.approx([_day_x(day)] * line.points)
                crossed = _reaches(scene, tag, line.x[0])
                assert crossed[-1] == "june" and len(crossed) == number, (tag, moment)
                (label,) = [
                    s
                    for s in scene.steps
                    if isinstance(s, Label) and s.names == line.gid and " on " in s.text
                ]
                assert label.text.endswith(f"contract {number} on {day:%b} {day.day}")
                assert label.x == pytest.approx(line.x[0])

    def test_each_line_spans_its_years_four_bars(self, every, years) -> None:
        scene = every[22]
        for f in years:
            rows = [_stroke(scene, f"{f.year}-{m}").y[0] for m in ("march", "april", "may", "june")]
            for moment in ("entry", "exit"):
                line = _stroke(scene, f"{f.year}-{moment}")
                assert line.y.max() > max(rows) and line.y.min() < min(rows)

    def test_march_is_drawn_still_trading_in_2008_and_expired_in_2006(self, every, years) -> None:
        scene = every[22]
        still, expired = years
        assert _stroke(scene, "2008-march").x.max() > _stroke(scene, "2008-entry").x[0]
        assert _stroke(scene, "2006-march").x.max() < _stroke(scene, "2006-entry").x[0]
        assert (still.march_trading, expired.march_trading) == (True, False)

    def test_the_years_are_stacked_and_their_rows_ordered_by_expiry(self, every) -> None:
        scene = every[22]
        for tag in ("2008", "2006"):
            rows = [_stroke(scene, f"{tag}-{m}").y[0] for m in ("march", "april", "may", "june")]
            assert rows == sorted(rows, reverse=True)
        assert _stroke(scene, "2006-entry").y.max() < _stroke(scene, "2008-entry").y.min()

    def test_other_figures_move_the_bars_the_note_and_the_numbers(self, years) -> None:
        still, expired = years
        swapped = (
            dataclasses.replace(still, entry=date(2008, 2, 28), entry_number=3),
            dataclasses.replace(expired, entry=date(2006, 2, 23), entry_number=4),
        )
        scene = _june_file(*swapped)
        assert "March has expired" in scene.labels[:8]
        assert "March still trading" in scene.labels[8:]
        assert "June is contract 3 on Feb 28" in scene.labels
        assert "June is contract 4 on Feb 23" in scene.labels
        assert len(_reaches(scene, "2008", _stroke(scene, "2008-entry").x[0])) == 3

    def test_it_closes_on_the_rule_it_draws(self, every) -> None:
        last = every[22].steps[-1]
        assert (last.text, last.color) == ("June’s number is how many bars each line crosses", INK)

    def test_its_alt_text_says_what_the_picture_shows(self, every, years) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[22])
        still, expired = years
        for f in years:
            assert f"March’s bar ends on {f.last_trade[0]:%B} {f.last_trade[0].day}" in alt
        assert "crosses all four bars" in alt
        assert "crosses only April, May and June" in alt
        assert alt.count("crosses May and June") == 2
        assert (still.entry_number, expired.entry_number) == (4, 3)


# --- Lesson 5: the three checks of the expiry rule ---------------------------


class TestTheHandoverSketch:
    def test_its_words(self, every) -> None:
        assert every[23].title == "A handover shows when March stopped"
        assert every[23].labels == HANDOVER_LABELS

    def test_its_colours(self, every) -> None:
        scene = every[23]
        assert _stroke(scene, "file-1").color == INK
        assert _stroke(scene, "file-2").color == MUTED
        assert _stroke(scene, "carry").color == ACCENT
        expiry, three = _stroke(scene, "expiry"), _stroke(scene, "three")
        assert (expiry.color, expiry.dashed) == (ACCENT, True)
        assert (three.color, three.dashed) == (MUTED, True)

    def test_the_files_hand_over_the_day_after_the_rule_s_last_day(self) -> None:
        """The day after March's last trading day, contract 1's file carries on
        from contract 2's price rather than from its own."""
        last = ng_last_trade(HANDOVER_YEAR, 3)
        one = seasonals.settlements(seasonals.NATURAL_GAS[1])[1]
        two = seasonals.settlements(seasonals.NATURAL_GAS[2])[1]
        after = min(d for d in one if d > last)
        assert (last, after) == (date(1996, 2, 23), date(1996, 2, 26))
        assert abs(one[after] - two[last]) < abs(one[after] - one[last])
        assert _last_trade_with_lead(HANDOVER_YEAR, 3, 3) == date(1996, 2, 27)

    def test_each_dot_and_the_arrow_sit_at_the_files_prices(self, every) -> None:
        scene = every[23]
        one = seasonals.settlements(seasonals.NATURAL_GAS[1])[1]
        two = seasonals.settlements(seasonals.NATURAL_GAS[2])[1]
        days = [
            d for d in sorted(one) if sketches.HANDOVER_DAYS[0] <= d <= sketches.HANDOVER_DAYS[1]
        ]
        days = [d for d in days if d in two]
        span = sketches.HANDOVER_PRICE[1] - sketches.HANDOVER_PRICE[0]
        height = sketches.HANDOVER_Y[1] - sketches.HANDOVER_Y[0]

        def y(price) -> float:
            return (
                sketches.HANDOVER_Y[0] + (float(price) - sketches.HANDOVER_PRICE[0]) / span * height
            )

        assert list(_stroke(scene, "file-1").y) == pytest.approx([y(one[d]) for d in days])
        assert list(_stroke(scene, "file-2").y) == pytest.approx([y(two[d]) for d in days])
        last = ng_last_trade(HANDOVER_YEAR, 3)
        after = days[days.index(last) + 1]
        carry = _stroke(scene, "carry")
        assert carry.y[0] == pytest.approx(y(two[last]))
        tip = int(np.argmax(carry.x))
        assert carry.y[tip] == pytest.approx(y(one[after]))
        assert _last_trade_with_lead(1996, 4, 3) == date(1996, 3, 27)

    def test_the_lines_sit_between_their_days(self, every) -> None:
        scene = every[23]
        dots = _stroke(scene, "file-1").x
        expiry, three = _stroke(scene, "expiry").x[0], _stroke(scene, "three").x[0]
        assert dots[6] < expiry < dots[7]
        assert dots[8] < three < dots[9]

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[23])
        assert "a grey dashed line two trading days later marks" in alt
        end, last = sketches.HANDOVER_DAYS[1], ng_last_trade(HANDOVER_YEAR, 3)
        assert f"to {end:%B} {end.day}, {end.year}, one dot a trading day" in alt
        assert f"the contract-2 file’s {last:%b} {last.day} price" in alt
        after = min(d for d in seasonals.settlements(seasonals.NATURAL_GAS[1])[1] if d > last)
        assert f"between {last:%b} {last.day} and {after:%b} {after.day} marks" in alt


class TestTheCoverageSketch:
    def test_its_words(self, every) -> None:
        assert every[24].title == "Which years each check reaches"
        assert every[24].labels == COVERAGE_LABELS

    def test_its_figures_are_the_runs(self) -> None:
        from tests.test_commodity_seasonals import TestTheNaturalGasExpiries

        f = CheckCoverage.from_run()
        assert (f.handover_fits, f.handover_readable) == (298, 316)
        assert (f.exchange_matches, f.exchange_contracts) == (40, 40)
        assert f.exchange_years == (2017, 2026)
        pinned = TestTheNaturalGasExpiries.EXCHANGE
        assert {
            y: tuple(d.isoformat() for d in days) for y, days in EXCHANGE_LAST_TRADES.items()
        } == pinned

    def test_each_bar_spans_its_years(self, every) -> None:
        scene = every[24]
        last = max(day for days in EXCHANGE_LAST_TRADES.values() for day in days)
        assert last == date(2026, 5, 27)
        assert _span_ends(_stroke(scene, "files")) == pytest.approx(
            (_cover_x(1994 + 1 / 12), _cover_x(2024 + 4 / 12))
        )
        assert _span_ends(_stroke(scene, "exchange")) == pytest.approx(
            (
                _cover_x(2017),
                _cover_x(last.year + (last.timetuple().tm_yday - 1) / 365),
            )
        )
        assert _stroke(scene, "begins").x[0] == pytest.approx(_cover_x(2017))
        assert _stroke(scene, "files").color == INK
        assert _stroke(scene, "exchange").color == ACCENT

    def test_other_figures_move_the_labels(self) -> None:
        f = dataclasses.replace(CheckCoverage.from_run(), handover_fits=300, exchange_matches=39)
        labels = _check_coverage(f).labels
        assert "the files’ handovers: 300 of 316 expiries fit" in labels
        assert "the exchange’s dates: 39 of 40 March to June contracts" in labels


class TestTheEdgeDaySketch:
    def test_its_words(self, every) -> None:
        assert every[25].title == "2018: entry on March’s own last day"
        assert every[25].labels == EDGE_LABELS

    def test_the_entry_falls_on_march_s_last_day(self, every) -> None:
        scene = every[25]
        f = sketches.JuneYear.from_run(EDGE_YEAR)
        assert f.entry == f.last_trade[0] and f.entry_number == 4
        assert _stroke(scene, "entry").x[0] == pytest.approx(_stroke(scene, "bar-3").x.max())
        assert len(edge_years()) == 10 and EDGE_YEAR in edge_years()

    def test_its_colours(self, every) -> None:
        scene = every[25]
        assert _stroke(scene, "bar-6").color == ACCENT
        assert [_stroke(scene, f"bar-{m}").color for m in (3, 4, 5)] == [INK] * 3

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[25])
        assert "exactly where March’s bar ends" in alt


class TestTheHolidaySketch:
    def test_its_words(self, every) -> None:
        assert every[26].title == "A row in the file is not a trading day"
        assert every[26].labels == HOLIDAY_LABELS

    def test_the_rows_are_the_files(self, every) -> None:
        scene = every[26]
        rows = seasonals.settlements(seasonals.NATURAL_GAS[1])[1]
        christmas, boxing = date(2018, 12, 25), date(2016, 12, 26)
        assert not is_trading_day(christmas) and not is_trading_day(boxing)
        assert christmas in rows and rows[christmas] == rows[date(2018, 12, 24)]
        assert boxing not in rows
        assert _stroke(scene, "day-2018-25").color == LOST
        for stroke in scene.strokes:
            if stroke.gid.startswith("day-"):
                _, year, day = stroke.gid.split("-")
                open_ = is_trading_day(date(int(year), 12, int(day)))
                assert stroke.color == (INK if open_ else LOST), stroke.gid
        assert not [s for s in scene.strokes if s.gid == "day-2016-26"]
        for year in (2018, 2016):
            for day in range(21, 29):
                drawn = [s for s in scene.strokes if s.gid == f"day-{year}-{day}"]
                assert bool(drawn) == (date(year, 12, day) in rows), (year, day)

    def test_its_alt_text_says_what_the_picture_shows(self, every) -> None:
        alt = _alt(POST.read_text(encoding="utf-8"), every[26])
        assert "so the weekend of the 22nd and 23rd has none" in alt
        assert [date(2016, 12, d).weekday() for d in (24, 25)] == [5, 6]
        assert "its weekend of the 24th and 25th and the closed 26th have no dot" in alt

    def test_the_four_come_in_the_post_s_order(self) -> None:
        assert [s.slug for s in _expiry_scenes()] == [
            "handover",
            "check_coverage",
            "edge_day",
            "holiday_rows",
        ]
