"""The pins for the thirty-five whiteboard GIFs in the equity-seasonals post.

Four sketch the post's opening section, two its section "The two strategies",
seven the rules its first lesson lists, one rule each, one the split that its
second lesson discusses, three its check of Chan's five-year claim, two its
lesson on survivorship bias, four its question on whether the January effect
still worked after 2008, two its question on whether Heston and Sadka's effect
existed before 2002, and ten its question on whether Heston and Sadka's
effect survived it, three of them on where its 4.2 percent comes from and
three on what a broader series shows. The
opening's timeline places each source's years to scale, from Chan's committed
files and the registered runs' constants, and its verdicts sketch draws the
two registered runs' figures to scale. Those figures are pinned here as
:data:`PINNED`, the values ``tests/test_equity_seasonals.py`` pins, so every
test here runs without the owner's archive.
``test_the_whiteboard_draws_these_runs_verdicts``,
``test_the_whiteboard_draws_these_runs_ranges``,
``test_the_whiteboard_draws_these_runs_ivv_figures`` and
``test_the_whiteboard_draws_these_runs_power`` in
``tests/test_equity_seasonals.py`` hold that the runs give :data:`PINNED`,
:data:`PINNED_RANGES`, :data:`PINNED_IVV` and :data:`PINNED_POWER`.

The strategy sketches are schematic and read no data, so what is pinned for
them is what a reader takes from them.

1. Which way each strategy bets: Example 7.6 buys the lowest-ranked tenth and
   shorts the highest and points its losers up and its winners down, and
   Example 7.7 does the reverse and points each the way it already went.
2. Its timing: January is one twelfth of the year past the year's last close,
   and the same-month trade ranks and holds the same calendar month in two
   strips, a year apart, then moves on a month.
3. That each sketch names its bet in the post's own words, "mean reversion"
   and "seasonal momentum".
4. That no label touches a line, leaves the frame or touches another label,
   in the installed hand font and in the wider fallback.
5. Each file's size, frame count, loop and timing, and that it sits in the
   post right after the paragraph it draws.

The rule sketches print figures from :class:`RuleFigures`, whose defaults
``tests/test_equity_seasonals.py`` derives from Chan's files. What is pinned
here is that each label prints its figure, that the marks stand where the
figures put them, and that other figures move both. Each rule sketch closes
the rule it draws in the post.

The split sketch prints figures from :class:`SplitFigures`, whose defaults
``TestTheYearsInsideTheSplit`` derives. What is pinned for it is that each
bar and bracket stands to one scale on the file's figures and on other ones,
that each bar and its value take the colour of their sign, and that it sits
after the running-sum chart and the paragraph on the split's years.

The five-year sketches print :class:`FiveYearFigures`, which
``TestTheFiveYearSketches`` in ``tests/test_equity_seasonals.py`` derives.
The three survivorship sketches and the January fill are schematic, so what is
pinned for them is what a reader takes from them: who is in the file and who
is not, which stocks a tenth holds, and where each mark stands. The January
ranges sketch draws :data:`PINNED_RANGES`, which
``test_the_whiteboard_draws_these_runs_ranges`` holds the registered run
gives. The two under "What 18 Januaries can detect" draw :data:`PINNED_POWER`,
which ``test_the_whiteboard_draws_these_runs_power`` holds the registered run
gives, beside Chan's three Januaries from :class:`FiveYearFigures`. Section
3's carry-forward sketch is schematic, and eight of its other nine draw
:data:`PINNED_IVV`. Section 2's sources sketch reads no run, and its second
draws :data:`PINNED_OSAP`, which the committed Open Source Asset Pricing
release gives, so its test reads the run itself. The three sketches of the
4.2 percent's derivation draw the test's critical value and δ from
:data:`PINNED_IVV`'s month count. Twenty sketches build slowly, and their
pace is pinned too. The broader series' three read the committed Open Source
Asset Pricing release, and the last two also :data:`PINNED_IVV`'s months.

Two draws on one machine give the same bytes. Whether a committed GIF equals a
fresh draw depends on the font, as ``tests/test_usdcad_tests_whiteboard.py``
explains, so that comparison runs only on macOS arm64 with Comic Sans MS.
"""

from __future__ import annotations

import dataclasses
import hashlib
import math
import platform
import re
from types import SimpleNamespace

import matplotlib
import numpy as np
import pandas as pd
import pytest
from PIL import Image

from chan import equity_seasonals as seasonals
from chan import equity_seasonals_whiteboard as sketches
from chan import usdcad_tests_whiteboard as whiteboard
from chan.archive import ArchiveUnavailable
from chan.equity_seasonals_whiteboard import (
    ANNUAL_RANGE,
    AXIS_Y,
    BOOK_YEAR,
    JANUARY_END,
    JANUARY_RANGE,
    RANKED,
    TENTH,
    TIMELINE_X,
    YEAR,
    Broad,
    FiveYearFigures,
    IvvFigures,
    JanuaryPower,
    JanuaryRanges,
    OsapFigures,
    RuleFigures,
    Shift,
    Spans,
    SplitFigures,
    Together,
    Verdicts,
    _at,
    _year,
    delta_scenes,
    five_year_scenes,
    gif_name,
    ivv_scenes,
    january_power_scenes,
    january_scenes,
    main,
    make_equity_seasonals_whiteboards,
    opening_scenes,
    osap_scenes,
    rule_scenes,
    scenes,
    sketch_timeline,
    split_scenes,
    survivor_scenes,
)
from chan.paths import FIGURES_DIR, REPO_ROOT
from chan.regime_figure import ACCENT, GOOD, LOST
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
from tests.test_usdcad_tests_whiteboard import GIFS as USDCAD_GIFS

POST = REPO_ROOT / "blog" / "equity-seasonals-lessons.md"

TITLES = ["The January trade", "The same-month trade"]
STRATEGY_GIFS = ["equity_seasonals_january_trade.gif", "equity_seasonals_same_month_trade.gif"]
OPENING_GIFS = ["equity_seasonals_which_years.gif", "equity_seasonals_two_verdicts.gif"]
RULE_GIFS = [
    "equity_seasonals_rule_short_side.gif",
    "equity_seasonals_rule_filled_close.gif",
    "equity_seasonals_rule_sum_or_mean.gif",
    "equity_seasonals_rule_wrong_close.gif",
    "equity_seasonals_rule_empty_months.gif",
    "equity_seasonals_rule_own_month_end.gif",
    "equity_seasonals_rule_month_end_lookup.gif",
]
SPLIT_GIFS = ["equity_seasonals_split_swing.gif"]
FIVE_YEAR_GIFS = [
    "equity_seasonals_five_year_months.gif",
    "equity_seasonals_five_year_noise.gif",
    "equity_seasonals_five_year_januaries.gif",
]
#: Every GIF in the order :func:`make_equity_seasonals_whiteboards` writes them.
SURVIVOR_GIFS = [
    "equity_seasonals_survivors_file.gif",
    "equity_seasonals_survivors_ranking.gif",
    "equity_seasonals_survivors_panels.gif",
]
OSAP_GIFS = [
    "equity_seasonals_osap_sources.gif",
    "equity_seasonals_osap_before.gif",
]
JANUARY_GIFS = [
    "equity_seasonals_january_registered.gif",
    "equity_seasonals_january_fill.gif",
    "equity_seasonals_january_ranges.gif",
]
IVV_GIFS = [
    "equity_seasonals_ivv_carry.gif",
    "equity_seasonals_ivv_checked.gif",
    "equity_seasonals_ivv_leavers.gif",
    "equity_seasonals_ivv_running_sum.gif",
]
DELTA_GIFS = [
    "equity_seasonals_delta_scatter.gif",
    "equity_seasonals_delta_shortcut.gif",
    "equity_seasonals_delta_bracket.gif",
]
BROAD_GIFS = [
    "equity_seasonals_broad_before_after.gif",
    "equity_seasonals_broad_together.gif",
    "equity_seasonals_broad_running.gif",
]
POWER_GIFS = ["equity_seasonals_january_catch.gif", "equity_seasonals_january_years.gif"]
GIFS = (
    OPENING_GIFS
    + STRATEGY_GIFS
    + RULE_GIFS
    + SPLIT_GIFS
    + FIVE_YEAR_GIFS
    + SURVIVOR_GIFS
    + JANUARY_GIFS
    + OSAP_GIFS
    + IVV_GIFS
    + DELTA_GIFS
    + BROAD_GIFS
    + POWER_GIFS
)
#: The GIFs a redraw cannot write without the owner's archive.
ARCHIVE_GIFS = {
    "equity_seasonals_two_verdicts.gif",
    "equity_seasonals_january_ranges.gif",
    "equity_seasonals_ivv_checked.gif",
    "equity_seasonals_ivv_leavers.gif",
    "equity_seasonals_ivv_running_sum.gif",
    *DELTA_GIFS,
    "equity_seasonals_broad_together.gif",
    "equity_seasonals_broad_running.gif",
    *POWER_GIFS,
}

#: The registered runs' figures, as ``tests/test_equity_seasonals.py`` pins
#: them in ``TestThePointInTimePins`` and ``TestTheMonthlyPins``. The vintage
#: is Alpha Vantage's ``adjusted_close`` for the IJR and IVV members files'
#: series, downloaded 2026-10-05, in the owner's archive. The specification is
#: ``MATLAB_JANUARY`` on the S&P 600 at each year-end, January 2009 to January
#: 2026, and ``REVISED_MATLAB`` on the S&P 500 each month, January 2009 to
#: September 2026, both before costs. A re-pin there moves these figures.
PINNED = Verdicts(
    january_low=-0.1047304659686345,
    january_high=0.08787549947820747,
    monthly_mean=-0.0001391960725288475,
    detectable=0.0422031836138127,
    january_low_rejects=False,
    january_high_rejects=True,
    monthly_rejects=False,
)

#: The registered January run's count of Januaries and each version's standard
#: deviation of a January before costs, as ``test_the_whiteboard_draws_these_runs_power``
#: in ``tests/test_equity_seasonals.py`` holds the run gives them. Same vintage
#: and specification as :data:`PINNED`'s January figures.
PINNED_POWER = JanuaryPower(n=18, low_std=0.0896119544094856, high_std=0.10072917438308693)

#: The registered January run's eighteen Januaries, each with its low and high
#: return before costs, and then each January's return with every missing
#: member left out, as ``test_the_whiteboard_draws_these_runs_ranges`` in
#: ``tests/test_equity_seasonals.py`` holds the run gives them. Same vintage
#: and specification as :data:`PINNED`'s January figures.
PINNED_RANGES = JanuaryRanges(
    (
        (2009, -0.3102916684682715, 0.31512341488232387),
        (2010, -0.19839476507411702, 0.24494937260065897),
        (2011, -0.192227314302099, 0.1889766558224868),
        (2012, -0.10870572849484236, 0.14492043392989745),
        (2013, -0.15467069691120883, 0.1457086223041022),
        (2014, -0.1653363299933961, 0.1597979963136514),
        (2015, -0.13112900962243856, 0.0686157912693974),
        (2016, -0.09597216550984841, 0.06014433261299512),
        (2017, -0.08469806698164244, 0.044717957152853684),
        (2018, -0.08838588652403147, 0.06835439802701994),
        (2019, -0.009638637680710993, 0.1306503085694603),
        (2020, -0.12694805604135495, -0.004070341602840345),
        (2021, -0.18706825793047532, -0.09002848776268077),
        (2022, -0.007092727187004211, 0.03353559694544943),
        (2023, 0.051120529038608704, 0.08356653439121693),
        (2024, -0.049378548477207414, -0.019616922654241906),
        (2025, -0.024022313935317015, 0.0037277705788413724),
        (2026, -0.0023087433400641386, 0.0026855572271426084),
    ),
    (
        0.012336949438598671,
        0.06180529076981473,
        -0.013370995134989752,
        0.03172977641610309,
        -0.02030750077070813,
        -0.007532225519990697,
        -0.05582536829303888,
        -0.02597585841808829,
        -0.02022825313242196,
        -0.014463170941109132,
        0.07600271988106036,
        -0.07209343541723659,
        -0.14597092899043138,
        0.016770103068295995,
        0.07016665994931218,
        -0.03541739751290522,
        -0.009081193606773712,
        0.001457459899829136,
    ),
)

#: The registered IVV run's figures that section 3's sketches draw, as
#: ``test_the_whiteboard_draws_these_runs_ivv_figures`` in
#: ``tests/test_equity_seasonals.py`` holds the run gives them. Same vintage
#: and specification as :data:`PINNED`'s monthly figures: Alpha Vantage's
#: ``adjusted_close`` for the IVV members file's series, downloaded 2026-10-05,
#: under ``REVISED_MATLAB``, before costs. The months and their mean are the
#: held months January 2009 to September 2026. The coverage runs over the
#: ranking month-ends 2008-12 to 2026-08, and the departures over the ranking
#: months 2008-12 to 2025-08, each counting a name that leaves within twelve
#: months, as row 49 of the replication log says.
IVV_RETURNS = (
    -0.0379857988360995,
    0.021246503696400323,
    -0.0358781205180302,
    0.005875045039702774,
    0.006893493963916881,
    -0.009523025432268926,
    0.009584243093939003,
    -0.016991060735716303,
    -0.035403426750204164,
    4.938861147155206e-05,
    -0.009040584247814808,
    -0.0021031318477821525,
    -0.032733296155586816,
    0.0028581808182344946,
    0.017995219927032322,
    0.01777360155869371,
    -0.0032757426217312723,
    0.006488503458352694,
    0.015289299165042973,
    -0.02526853700193417,
    0.020267063919560225,
    0.016735008596621144,
    0.002507269116061376,
    -0.0001674864254724675,
    -0.014561322057976585,
    0.019159620571970574,
    -0.01920031181295382,
    -0.009676477072137533,
    0.00992746559046442,
    0.008250230975830788,
    -0.00783793804315121,
    0.05071196928363015,
    -0.037005688249535595,
    0.029334174384897074,
    -0.004321783251426416,
    -0.010287561454024064,
    0.028046168145790865,
    -0.005030233925546779,
    -0.02254714209450469,
    0.022577486084970132,
    0.0378976872182034,
    -0.015118529197022314,
    0.010057722934155277,
    -0.03501121108125936,
    -0.025472465674253222,
    -0.005126518760386773,
    -0.0060972076955798545,
    -0.012192590043170115,
    0.009824377303970223,
    -0.004930972097501739,
    0.00016842012717260862,
    0.002745745146091103,
    -0.043678163997261675,
    -0.02994738754659756,
    -0.015496211631478036,
    0.009036701811118644,
    -0.003911273804865304,
    0.004285005556306464,
    0.004937341078907046,
    0.006409959299407806,
    0.00318740204210623,
    -0.00700354924898144,
    -0.003638529442225598,
    -0.005418910344808592,
    0.003410345467538982,
    0.005698487292484544,
    -0.00883995770646569,
    -0.010034462010032434,
    0.00946394422901991,
    -0.008083515396571272,
    0.026171343540710927,
    -0.01275195788625066,
    0.04056607525412072,
    0.018777617068643025,
    -0.008842390388492837,
    -0.0031341799449591456,
    0.009416388992772667,
    -0.014127794666237637,
    0.032506317655804445,
    4.833705579842402e-05,
    0.025386716608256518,
    -0.009452337026060633,
    0.0015433715758404684,
    0.01618869050577917,
    0.02293885312527561,
    -0.012949138360864811,
    -0.017769500369724602,
    0.06023686169694832,
    0.022482862453109573,
    -0.028471746276749962,
    -0.012101392990913944,
    -0.004061576463468347,
    -0.011683067921485196,
    -0.010854897923833482,
    -0.020095832923473392,
    0.00794815333197758,
    -0.023567417938163016,
    0.00015214034148806023,
    0.009182638556711642,
    -0.022816612587554633,
    0.03482543845146469,
    -0.03686332788303407,
    0.0017811029079780015,
    -0.01268423150964028,
    0.006433291198401316,
    0.012062610821206708,
    0.00676088382605724,
    -0.017497630503882856,
    0.024034730176591718,
    0.01126405233969932,
    0.006956438678302258,
    -0.014794845594855064,
    -0.0040995077432267575,
    -0.007789863713150039,
    -0.003949842309618259,
    0.003164488155269736,
    -0.007502941853325388,
    -0.021633407267410417,
    -0.008346186045044422,
    -0.03368944860566857,
    0.015580470921773719,
    0.010673775398913038,
    0.006512433814282702,
    -0.01217650026533752,
    -0.02744339939284119,
    -0.02154675788545266,
    0.004483491285053849,
    0.015063512412976496,
    -0.021320686128913705,
    -0.013272438005894898,
    -0.022888621440883265,
    -0.014568746729453215,
    -0.012583498673268748,
    0.012420234375804797,
    0.05111197422014362,
    0.010827894495133036,
    0.008173074630213937,
    0.00019260838867336238,
    0.013337049145186566,
    -0.013391689472226244,
    -0.005138077686974438,
    0.011343603984537208,
    0.013421758333197918,
    0.007655959466967236,
    -0.009281171127805058,
    -0.08271554925499776,
    0.003324058174240978,
    -0.012483998432641991,
    -0.016832200653850975,
    0.0004226805398053046,
    0.047724449247358476,
    0.0049972602513345885,
    -0.045181608980582384,
    0.017939348639400377,
    -0.011543932517234816,
    -0.003207995386425447,
    -0.007100836748667199,
    0.02733971099041321,
    0.002328566899312652,
    -0.02996689299980593,
    0.024612334907552838,
    0.033502988219168084,
    0.016136567486706416,
    -3.996970272057585e-06,
    -0.0019369077614885101,
    -0.01308648542185879,
    0.02662326865344017,
    0.01081088612413108,
    -0.02305676435299483,
    0.009024383622068383,
    0.03489863706167164,
    0.021994651287566395,
    -0.015264924004552757,
    -0.04910419820734907,
    0.0009362394277770451,
    0.015212455222935963,
    0.007844153783436862,
    0.01253169957757605,
    0.007536674909553988,
    -0.018968968549766242,
    -0.0009940234842372038,
    0.031064687974763208,
    -0.012367655381759012,
    0.0006570394700643113,
    0.016278505305220018,
    0.005476591921781731,
    0.012217235578132325,
    0.019870898975940805,
    -0.024409212952266862,
    0.003021305507002975,
    0.00731643012327767,
    0.004511796435286796,
    0.005346093237442395,
    -0.022249714963908457,
    -0.0022783435215252665,
    0.020620520144283176,
    -0.0012497169381607462,
    0.01175657662312716,
    -0.012647075486355727,
    -0.006945489120624929,
    0.008793185890689725,
    -0.04181480253961732,
    -0.025788968058108565,
    0.017963867975811624,
    -0.022764247287665407,
    0.029813810326942494,
    0.004772837026203943,
    0.028741499213804547,
    0.05174786867973112,
    0.017420219326838612,
    -0.032424858966202286,
    -0.03105164919165711,
    0.048322736942504455,
)
PINNED_IVV = IvvFigures(
    covered=98321,
    members=107115,
    fewest=("2012-09", 364, 501),
    most=("2025-09", 501, 503),
    departing=(505, 698, 3019),
    staying=(8624, 8431, 71055),
    months=tuple(
        zip(
            pd.period_range("2009-01", periods=len(IVV_RETURNS), freq="M").strftime("%Y-%m"),
            IVV_RETURNS,
            strict=True,
        )
    ),
    mean=-0.0001391960725288475,
    detectable=0.0422031836138127,
)

#: Section 2's figures, as ``run_open_asset_pricing`` gives them from the
#: committed release 202510 of Open Source Asset Pricing's ``MomSeasonShort``,
#: long-short in equal-weighted tenths of NYSE and AMEX stocks, before costs,
#: 1965-01 to 2002-12 for ``sample`` and 1965-01 to 2001-12 for ``before``.
#: ``printed`` and ``chan_annual`` are Heston and Sadka's and Chan's figures.
#: Entry 52 of the replication log carries the same numbers.
PINNED_OSAP = OsapFigures(
    printed=0.0115,
    sample=0.01360724437376685,
    sample_t=8.633503160912532,
    before=0.013133990629309849,
    chan_annual=0.13,
)

STROKES = [
    ["year", "close", "january", "to-rank", "ranked", "buy", "short", "losers-up", "winners-down"],
    [
        "last-year",
        "this-year",
        "march-then",
        "repeat",
        "march-now",
        "april-then",
        "april-now",
        "ranked",
        "buy",
        "short",
        "winners-up",
        "losers-down",
    ],
]

LABELS = [
    [
        "a year of returns",
        "hold January",
        "rank at the year’s last close",
        "buy the worst tenth",
        "short the best tenth",
        "losers up",
        "winners down",
        "mean reversion",
    ],
    [
        "last year",
        "this year",
        "March",
        "rank on",
        "hold",
        "then April, May, …",
        "buy the best tenth",
        "short the worst tenth",
        "winners up",
        "losers down",
        "seasonal momentum",
    ],
]

#: The same limits the USD.CAD sketches hold, in pixels.
CLEAR_PX, INSIDE_PX, APART_LABELS_PX = 10, 5, 4


@pytest.fixture(scope="module")
def drawn():
    return scenes()


@pytest.fixture(scope="module")
def spans():
    return Spans.read()


@pytest.fixture(scope="module")
def opening(spans):
    return opening_scenes(PINNED, spans)


@pytest.fixture(scope="module")
def rules():
    return rule_scenes()


@pytest.fixture(scope="module")
def split():
    return split_scenes()


@pytest.fixture(scope="module")
def five():
    return five_year_scenes()


@pytest.fixture(scope="module")
def survivors():
    return survivor_scenes()


@pytest.fixture(scope="module")
def january():
    return january_scenes(PINNED_RANGES)


@pytest.fixture(scope="module")
def power():
    return january_power_scenes(PINNED_POWER)


@pytest.fixture(scope="module")
def osap():
    return osap_scenes(PINNED_OSAP)


@pytest.fixture(scope="module")
def ivv():
    return ivv_scenes(PINNED_IVV)


@pytest.fixture(scope="module")
def delta():
    return delta_scenes(PINNED_IVV)


@pytest.fixture(scope="module")
def project():
    """Open Source Asset Pricing's committed release, which needs no archive."""
    return seasonals.run_open_asset_pricing()


@pytest.fixture(scope="module")
def broad(project):
    return (
        sketches._broad_before_after(Broad.from_run(project)),
        sketches._broad_together(Together.from_runs(PINNED_IVV, project)),
        sketches._broad_running(Together.from_runs(PINNED_IVV, project)),
    )


@pytest.fixture(scope="module")
def every(opening, drawn, rules, split, five, survivors, january, osap, ivv, delta, broad, power):
    """All thirty-five scenes in the order their GIFs are written."""
    return (
        *opening,
        *drawn,
        *rules,
        *split,
        *five,
        *survivors,
        *january,
        *osap,
        *ivv,
        *delta,
        *broad,
        *power,
    )


@pytest.fixture(scope="module")
def frames(every):
    return [sketch_timeline(scene) for scene in every]


@pytest.fixture(scope="module")
def gifs(tmp_path_factory, spans, project):
    return make_equity_seasonals_whiteboards(
        out_dir=tmp_path_factory.mktemp("sketches"),
        verdicts=PINNED,
        spans=spans,
        ranges=PINNED_RANGES,
        ivv=PINNED_IVV,
        osap=PINNED_OSAP,
        power=PINNED_POWER,
        project=project,
    )


def _stroke(scene, gid):
    return next(s for s in scene.strokes if s.gid == gid)


def _inside(ring, x: float, y: float) -> bool:
    """Whether (x, y) lies inside the ellipse ``ring`` traces."""
    cx, cy = ring.x.mean(), ring.y.mean()
    rx, ry = (ring.x.max() - ring.x.min()) / 2, (ring.y.max() - ring.y.min()) / 2
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1


def _ringed(scene, gid) -> list[int]:
    """The ranks, lowest return first, of the stocks the ring ``gid`` encloses."""
    ranked, ring = _stroke(scene, "ranked"), _stroke(scene, gid)
    return [k for k in range(ranked.points) if _inside(ring, ranked.x[k], ranked.y[k])]


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


class TestTheScenes:
    def test_there_are_two_in_the_order_the_post_reads_them(self, drawn) -> None:
        assert [scene.title for scene in drawn] == TITLES

    def test_each_has_its_own_gif_named_for_it(self, drawn) -> None:
        assert [gif_name(scene) for scene in drawn] == STRATEGY_GIFS

    def test_each_draws_its_strokes_in_order(self, drawn) -> None:
        assert [[s.gid for s in scene.strokes] for scene in drawn] == STROKES

    def test_each_says_what_it_should(self, drawn) -> None:
        assert [scene.labels for scene in drawn] == LABELS

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


class TestTheBets:
    def test_a_tenth_of_the_ranked_row(self) -> None:
        assert TENTH * 10 == RANKED

    def test_the_row_is_sorted_lowest_return_first(self, drawn) -> None:
        for scene in drawn:
            ranked = _stroke(scene, "ranked")
            assert ranked.points == RANKED
            assert np.all(np.diff(ranked.y) > 0), scene.title

    def test_the_january_trade_buys_the_lowest_tenth_and_shorts_the_highest(self, drawn) -> None:
        january = drawn[0]
        assert _ringed(january, "buy") == list(range(TENTH))
        assert _ringed(january, "short") == list(range(RANKED - TENTH, RANKED))

    def test_the_same_month_trade_buys_the_highest_tenth_and_shorts_the_lowest(self, drawn) -> None:
        same = drawn[1]
        assert _ringed(same, "buy") == list(range(RANKED - TENTH, RANKED))
        assert _ringed(same, "short") == list(range(TENTH))

    def test_bought_is_green_and_shorted_red_in_rings_arrows_and_labels(self, drawn) -> None:
        for scene in drawn:
            assert _stroke(scene, "buy").color == GOOD
            assert _stroke(scene, "short").color == LOST
            for step in scene.steps:
                if isinstance(step, Label) and step.names in {"buy", "short"}:
                    assert step.color == _stroke(scene, step.names).color, step.text

    def test_the_january_trade_points_its_extremes_back(self, drawn) -> None:
        """Losers, which it buys, go up, and winners, which it shorts, go down."""
        january = drawn[0]
        up, down = _stroke(january, "losers-up"), _stroke(january, "winners-down")
        assert (up.y[1] > up.y[0], up.color) == (True, GOOD)
        assert (down.y[1] < down.y[0], down.color) == (True, LOST)
        assert up.y.max() < down.y.min()

    def test_the_same_month_trade_points_its_extremes_on(self, drawn) -> None:
        """Winners, which it buys, go further up, and losers, which it shorts,
        further down."""
        same = drawn[1]
        up, down = _stroke(same, "winners-up"), _stroke(same, "losers-down")
        assert (up.y[1] > up.y[0], up.color) == (True, GOOD)
        assert (down.y[1] < down.y[0], down.color) == (True, LOST)
        assert down.y.max() < up.y.min()

    def test_each_names_its_bet_in_the_posts_words(self, drawn) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene, bet in zip(drawn, ("mean reversion", "seasonal momentum"), strict=True):
            assert bet in scene.labels
            assert f"a **{bet}** trade" in text, bet


class TestTheTiming:
    def test_january_is_a_twelfth_of_the_year_past_the_close(self, drawn) -> None:
        x0, x1, y = YEAR
        january = _stroke(drawn[0], "january")
        close = _stroke(drawn[0], "close")
        assert (january.x[0], january.y[0]) == (close.x[0], close.y[0]) == (x1, y)
        assert january.x[-1] == pytest.approx(JANUARY_END)
        assert JANUARY_END - x1 == pytest.approx((x1 - x0) / 12)

    def test_the_same_month_is_ranked_last_year_and_held_this_year(self, drawn) -> None:
        same = drawn[1]
        then, now = _stroke(same, "march-then"), _stroke(same, "march-now")
        assert (then.x.min(), then.x.max()) == (now.x.min(), now.x.max())
        assert then.y.min() > now.y.max()
        repeat = _stroke(same, "repeat")
        assert repeat.x[0] == repeat.x[1] == pytest.approx((then.x.min() + then.x.max()) / 2)
        assert repeat.y[0] > repeat.y[1]

    def test_then_it_moves_on_a_month(self, drawn) -> None:
        same = drawn[1]
        march, april = _stroke(same, "march-now"), _stroke(same, "april-now")
        width = march.x.max() - march.x.min()
        assert april.x.min() == pytest.approx(march.x.max())
        assert april.x.max() - april.x.min() == pytest.approx(width)
        assert (_stroke(same, "april-then").x == april.x).all()


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

    def test_each_is_680_by_320_and_loops_forever(self, gifs, frames) -> None:
        for path, steps in zip(gifs, frames, strict=True):
            with Image.open(path) as image:
                assert (image.size, image.n_frames, image.info["loop"]) == (
                    (WIDTH, HEIGHT),
                    len(steps),
                    0,
                )
            assert _durations(path) == [f.ms for f in steps], path.name

    def test_each_opens_on_its_title_and_holds_its_drawing(self, every, frames) -> None:
        for scene, steps in zip(every, frames, strict=True):
            assert (steps[0].done, steps[0].ms) == (0, TITLE_MS)
            hold = sketches.PACED_HOLD_MS if scene.slug in sketches.PACED else HOLD_MS
            assert steps[-1].ms == hold, scene.slug

    def test_each_is_under_1_mb(self, gifs) -> None:
        for path in gifs:
            assert path.stat().st_size < 1_000_000, path.name

    def test_two_draws_give_the_same_bytes(self, gifs, tmp_path, spans, project) -> None:
        again = make_equity_seasonals_whiteboards(
            out_dir=tmp_path,
            verdicts=PINNED,
            spans=spans,
            ranges=PINNED_RANGES,
            ivv=PINNED_IVV,
            osap=PINNED_OSAP,
            project=project,
            power=PINNED_POWER,
        )
        for first, second in zip(gifs, again, strict=True):
            assert first.read_bytes() == second.read_bytes(), first.name


def _durations(path) -> list[int]:
    with Image.open(path) as image:
        found = []
        for index in range(image.n_frames):
            image.seek(index)
            found.append(image.info["duration"])
        return found


class TestTheCommittedGifs:
    def test_every_gif_in_the_figures_folder_is_drawn_by_one_of_the_two_modules(self) -> None:
        """A GIF no module draws is a figure nothing regenerates."""
        assert {path.name for path in FIGURES_DIR.glob("*.gif")} == set(GIFS) | set(USDCAD_GIFS)

    def test_each_has_the_size_frames_loop_and_timing_of_a_fresh_draw(self, frames) -> None:
        for name, steps in zip(GIFS, frames, strict=True):
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
            ), f"{path.name}: redraw with: uv run python -m chan.equity_seasonals_whiteboard"


class TestThePost:
    def test_each_gif_follows_the_paragraph_it_draws(self) -> None:
        """The timeline right after the paragraph that introduces the later
        runs, the last source it draws, then the list of the two verdicts and
        the verdicts sketch right after it, the
        January trade right after Example 7.6's paragraph, and the same-month
        trade right after Example 7.7's."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "Two later runs asked whether either effect still works.",
                "1. **The January effect** averages",
                "**Example 7.6, the January effect.**",
                "**Example 7.7, Heston and Sadka.**",
            ),
            OPENING_GIFS + STRATEGY_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_the_two_definitions_bring_their_sketches_into_the_opening(self) -> None:
        """The opening explains survivorship bias and the registered label, so
        the sketch for each sits right after the paragraph that explains it."""
        text = POST.read_text(encoding="utf-8")
        opening = text[: text.index("\n## The two strategies")]
        paragraphs = [p for p in opening.split("\n\n") if p.strip()]
        for start, name in (
            ("Running Chan’s code on his own data files", SURVIVOR_GIFS[0]),
            ("For each, the repository wrote down the claim", JANUARY_GIFS[0]),
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(start)]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", paragraphs[index + 1]
            ), name
        assert any("is called survivorship bias" in p for p in paragraphs)
        assert any("is called registered" in p for p in paragraphs)

    def test_each_rule_sketch_closes_the_rule_it_draws(self) -> None:
        """Example 7.6's rules 2 and 3, then Example 7.7's rules 1, 2, 3, 5 and
        8, each with its sketch as the last block before the next heading."""
        text = POST.read_text(encoding="utf-8")
        for (example, rule), name in zip(
            (
                ("### Example 7.6", "#### Rule 2:"),
                ("### Example 7.6", "#### Rule 3:"),
                ("### Example 7.7", "#### Rule 1:"),
                ("### Example 7.7", "#### Rule 2:"),
                ("### Example 7.7", "#### Rule 3:"),
                ("### Example 7.7", "#### Rule 5:"),
                ("### Example 7.7", "#### Rule 8:"),
            ),
            RULE_GIFS,
            strict=True,
        ):
            start = text.index("\n" + rule, text.index("\n" + example))
            end = re.compile(r"\n#{2,4} ").search(text, start + 1).start()
            blocks = [b.strip() for b in text[start:end].split("\n\n") if b.strip()]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", blocks[-1]
            ), name
            assert sum(name in b for b in blocks) == 1, name

    def test_the_split_sketch_follows_the_paragraph_on_the_years(self) -> None:
        """After the running-sum chart and the paragraph that reads its shape,
        so the chart comes before the words that describe it."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith("The 70 months from 2002")]
        name = re.escape(SPLIT_GIFS[0])
        assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{name}\)", paragraphs[index + 1])
        assert paragraphs[index - 1].startswith("*The running sum climbs")
        assert "equity_seasonals_split.png" in paragraphs[index - 2]
        assert paragraphs[index - 3].startswith("The figure below adds up the 83 months")
        assert paragraphs[index + 2] == "### Chan’s five-year claim"
        assert paragraphs[index + 3].startswith("Chan makes one claim about timing")

    def test_each_five_year_sketch_follows_its_paragraph(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "The five-year result does not contradict the split.",
                "The five-year result is narrow.",
                "Example 7.6 meets the same limit from another side.",
            ),
            FIVE_YEAR_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_lesson_3s_sketches_follow_their_paragraphs(self) -> None:
        """The ranking after the paragraph on what the strategies could trade,
        and the two ways to build the data after the one on keeping the
        companies that left. The saved-file sketch moved to the opening with
        the definition of survivorship bias."""
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        (define,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("The opening named the bias")
        ]
        (trade,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("Both strategies trade the tenth")
        ]
        (panel,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("[The post on survivorship and")
        ]
        for offset, name in (
            (trade + 1, SURVIVOR_GIFS[1]),
            (panel + 1, SURVIVOR_GIFS[2]),
        ):
            embed = paragraphs[offset]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name
        assert (trade, panel) == (define + 1, define + 3)

    def test_each_january_sketch_follows_its_paragraph(self) -> None:
        """The fill and ranges sketches after their paragraphs under the January
        question. The registered sketch moved to the opening with its definition."""
        text = POST.read_text(encoding="utf-8")
        start = text.index("### Whether the January effect still worked after 2008")
        end = text.index("\n### ", start + 1)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "A lower and an upper bound show how far the answer could move",
                "Each version goes through the same test",
            ),
            JANUARY_GIFS[1:],
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed.strip()
            ), name

    def test_the_open_questions_are_listed_as_their_subsections_name_them(self) -> None:
        """The list under "Three open questions:" names each subsection, in order."""
        text = POST.read_text(encoding="utf-8")
        start = text.index("## What later data can and cannot say")
        end = text.index("\n## ", start + 1)
        section = text[start:end]
        listed = re.findall(r"^\d\. (.+)\.$", section.split("\n### ", 1)[0], flags=re.MULTILINE)
        headings = re.findall(r"^### (.+)$", section, flags=re.MULTILINE)
        assert len(headings) == 3
        assert listed == headings

    def test_each_section_3_sketch_follows_its_part(self) -> None:
        """Each under its own heading, after the paragraph it draws."""
        text = POST.read_text(encoding="utf-8")
        start = text.index("### Whether Heston and Sadka’s effect still worked after 2008")
        end = text.index("\n## ", start)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for heading, opening, name in zip(
            (
                "#### How the IVV run was built",
                "#### Which companies it kept",
                "#### Whether dropping the rest matters",
                "#### What the IVV run found",
            ),
            (
                "The second later run, the IVV run below, tested Example 7.7",
                "Free daily prices gave a checked price",
                "Dropping the rest is harmless only if",
                "The 213 months average",
            ),
            IVV_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            assert paragraphs[index - 1] == heading, name
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)",
                paragraphs[index + 1].strip(),
            ), name
        (verdict,) = [
            k for k, p in enumerate(paragraphs) if p.startswith("The verdict, in the words written")
        ]
        assert paragraphs[verdict - 1] == "#### What the IVV verdict says"
        for heading, opening in (
            (
                "##### Where the 4.2 percent comes from",
                "A reader who wants only the verdict, stated above, can skip",
            ),
            ("#### What a broader series shows", "A broader series agrees with the IVV run"),
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            assert paragraphs[index - 1] == heading

    def test_every_sketch_is_embedded_once_and_the_verdicts_twice(self) -> None:
        """The verdicts sketch opens the post and closes it, with one alt text."""
        text = POST.read_text(encoding="utf-8")
        for name in GIFS:
            twice = name == "equity_seasonals_two_verdicts.gif"
            assert text.count(f"(../docs/figures/{name})") == (2 if twice else 1), name
        embeds = re.findall(
            r"!\[[^\]]+\]\(\.\./docs/figures/equity_seasonals_two_verdicts\.gif\)", text
        )
        assert len(embeds) == 2 and embeds[0] == embeds[1]

    def test_the_verdicts_sketch_closes_the_post_after_its_last_paragraph(self) -> None:
        text = POST.read_text(encoding="utf-8")
        start = text.index("## What this means for a trader")
        end = text.index("\n## ", start + 1)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        assert paragraphs[-3].startswith(
            "On Chan’s own files, all seventeen figures his code prints"
        )
        assert paragraphs[-2].startswith("For Heston and Sadka’s rotation")
        assert (
            "A return the test would likely miss is under about 4.2 percent a year before "
            "costs, and costs only lower it, so it is not an edge a trader can count on."
        ) in paragraphs[-2]
        assert "it is not an edge a trader can count on." in paragraphs[-2]
        assert (
            paragraphs[-1].strip().endswith("(../docs/figures/equity_seasonals_two_verdicts.gif)")
        )


class TestTheCommand:
    def test_it_writes_every_committed_path(self, monkeypatch, capsys) -> None:
        monkeypatch.setattr(
            sketches,
            "make_equity_seasonals_whiteboards",
            lambda: [FIGURES_DIR / name for name in GIFS],
        )
        main()
        assert capsys.readouterr().out.splitlines() == [
            f"wrote {FIGURES_DIR / name}" for name in GIFS
        ]

    @pytest.mark.parametrize(
        "refusal",
        [
            ArchiveUnavailable("no archive here"),
            seasonals.PointInTimeRefused("a member is missing"),
            seasonals.MonthlyRunRefused("a schedule is missing"),
        ],
        ids=["no archive", "January run refused", "monthly run refused"],
    )
    def test_without_the_archive_it_names_the_gifs_it_left(
        self, monkeypatch, refusal, tmp_path
    ) -> None:
        """It draws into a scratch folder, because a draw into the figures
        folder would overwrite the committed GIFs that the byte test compares."""

        def refuse():
            raise refusal

        before = {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")}
        monkeypatch.setattr(sketches, "FIGURES_DIR", tmp_path)
        monkeypatch.setattr(seasonals, "run_point_in_time", refuse)
        with pytest.raises(SystemExit) as stopped:
            main()
        assert str(stopped.value) == (
            "equity_seasonals_two_verdicts.gif, equity_seasonals_january_ranges.gif, "
            "equity_seasonals_ivv_checked.gif, equity_seasonals_ivv_leavers.gif, "
            "equity_seasonals_ivv_running_sum.gif, equity_seasonals_delta_scatter.gif, "
            "equity_seasonals_delta_shortcut.gif, equity_seasonals_delta_bracket.gif, "
            "equity_seasonals_broad_together.gif, equity_seasonals_broad_running.gif, "
            "equity_seasonals_january_catch.gif, equity_seasonals_january_years.gif "
            f"were not redrawn: {refusal}"
        )
        assert len(list(tmp_path.glob("*.gif"))) == len(GIFS) - len(ARCHIVE_GIFS)
        assert {path.name: path.read_bytes() for path in FIGURES_DIR.glob("*.gif")} == before

    def test_without_the_archive_it_still_writes_the_other_twenty_three(
        self, monkeypatch, tmp_path, spans
    ) -> None:
        def absent():
            raise ArchiveUnavailable("no archive here")

        monkeypatch.setattr(seasonals, "run_point_in_time", absent)
        with pytest.raises(ArchiveUnavailable):
            make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans)
        written = sorted(path.name for path in tmp_path.glob("*.gif"))
        assert written == sorted(set(GIFS) - ARCHIVE_GIFS)


class TestTheVerdicts:
    """The verdicts sketch draws the registered runs' figures to scale."""

    def test_its_labels_print_the_pinned_figures(self, opening) -> None:
        assert opening[1].title == "Two verdicts"
        assert opening[1].labels == [
            "January effect",
            "per January",
            "0",
            "−0.1047",
            "0.0879",
            "free data cannot decide",
            "Heston and Sadka",
            "per year",
            "0",
            "about 4.2% a year",
            "measured",
            "could pass unseen",
            "costs lower it, not measured",
            "not shown dead, and no edge a trader can count on",
        ]

    def test_costs_point_back_toward_zero_under_the_band(self, opening) -> None:
        """The arrow runs from X back toward zero below the line, in red, and
        the closing words are brown, with the alt text quoting them in order."""
        verdicts = opening[1]
        costs = _stroke(verdicts, "costs")
        zero, x = _at(0.0, *ANNUAL_RANGE), _at(PINNED.detectable, *ANNUAL_RANGE)
        assert costs.color == LOST
        assert costs.x.max() == pytest.approx(x - 0.1)
        assert costs.x.min() == pytest.approx((zero + x) / 2), "it stops halfway, implying no size"
        assert costs.x[0] == pytest.approx(x - 0.1), "it starts at X and points toward zero"
        assert costs.y.max() < sketches.MONTHLY_Y - 0.5
        assert _labelled(verdicts, "costs lower it, not measured").color == LOST
        assert (
            _labelled(verdicts, "not shown dead, and no edge a trader can count on").color == ACCENT
        )
        alt = _alt(POST.read_text(encoding="utf-8"), verdicts)
        place = 0
        for label in verdicts.labels:
            place = alt.index(f"“{label}”", place) + 1
        assert "A red arrow under the band points back toward zero" in alt
        assert "holds for twelve seconds" in alt and "drawn slowly" in alt

    def test_the_bracket_spans_the_two_means_to_scale(self, opening) -> None:
        bracket = _stroke(opening[1], "bracket")
        assert bracket.x.min() == pytest.approx(_at(PINNED.january_low, *JANUARY_RANGE))
        assert bracket.x.max() == pytest.approx(_at(PINNED.january_high, *JANUARY_RANGE))
        zero = _stroke(opening[1], "january-zero")
        assert bracket.x.min() < zero.x[0] < bracket.x.max()

    def test_the_tint_runs_from_zero_to_x_and_the_dot_sits_at_the_mean(self, opening) -> None:
        scene = opening[1]
        (tint,) = scene.fills
        zero = _stroke(scene, "monthly-zero").x[0]
        detect = _stroke(scene, "detectable").x[0]
        assert (tint.x0, tint.x1) == pytest.approx((zero, detect))
        assert detect == pytest.approx(_at(PINNED.detectable, *ANNUAL_RANGE))
        mean = _stroke(scene, "mean")
        assert mean.x[0] == pytest.approx(_at(12 * PINNED.monthly_mean, *ANNUAL_RANGE))
        assert abs(mean.x[0] - zero) < detect - zero

    def test_other_figures_move_the_labels_and_the_marks(self, spans) -> None:
        moved = dataclasses.replace(
            PINNED, january_low=-0.05, january_high=0.12, monthly_mean=0.001, detectable=0.03
        )
        scene = opening_scenes(moved, spans)[1]
        assert {"−0.0500", "0.1200", "about 3.0% a year"} <= set(scene.labels)
        assert _stroke(scene, "bracket").x.max() == pytest.approx(_at(0.12, *JANUARY_RANGE))

    @pytest.mark.parametrize(
        "changes",
        [
            {"january_low": 0.01},
            {"january_high": -0.01},
            {"monthly_mean": 0.004},
            {"monthly_mean": -0.0015, "detectable": 0.01},
            {"january_low": -0.2},
            {"january_low_rejects": True},
            {"january_high_rejects": False},
            {"monthly_rejects": True},
        ],
        ids=[
            "bracket above zero",
            "bracket below zero",
            "mean past X",
            "mean past minus X",
            "off the line",
            "both January series reject",
            "neither January series rejects",
            "the monthly run rejects",
        ],
    )
    def test_figures_the_words_would_misdescribe_are_refused(self, spans, changes) -> None:
        with pytest.raises(ValueError):
            opening_scenes(dataclasses.replace(PINNED, **changes), spans)

    def test_the_january_line_is_to_scale(self, opening) -> None:
        """Absolute positions, not the scale function checked against itself:
        zero halfway along a line from −0.15 to 0.15, and each end of the
        bracket as far from zero as its value."""
        scene = opening[1]
        line = _stroke(scene, "january-line")
        zero = _stroke(scene, "january-zero").x[0]
        bracket = _stroke(scene, "bracket")
        assert zero == pytest.approx((line.x[0] + line.x[-1]) / 2)
        unit = (line.x[-1] - line.x[0]) / 0.30
        assert zero - bracket.x.min() == pytest.approx(-PINNED.january_low * unit)
        assert bracket.x.max() - zero == pytest.approx(PINNED.january_high * unit)

    def test_the_annual_line_is_to_scale(self, opening) -> None:
        """Zero a fifth of the way along a line from −0.02 to 0.08, and the
        tint as wide as X on that scale."""
        scene = opening[1]
        line = _stroke(scene, "monthly-line")
        width = line.x[-1] - line.x[0]
        (tint,) = scene.fills
        assert tint.x0 == pytest.approx(line.x[0] + 0.2 * width)
        assert tint.x1 - tint.x0 == pytest.approx(PINNED.detectable / 0.10 * width)


class TestTheTimeline:
    """The timeline places each source's years to scale."""

    def test_the_spans_are_the_files_and_the_runs(self, spans) -> None:
        """Chan's files as ``data/README.md`` records them, and the months
        both registered runs hold, January 2009 to September 2026."""
        day = pd.Timestamp
        assert spans.large_caps == (day("1999-11-24"), day("2007-11-23"))
        assert spans.small_caps == (day("2004-01-15"), day("2008-02-01"))
        assert spans.later == (day("2009-01-01"), day("2026-09-30"))
        assert spans.split == seasonals.SPLIT == day("2002-01-01")

    def test_its_labels(self, opening) -> None:
        assert opening[0].title == "Which years each source reads"
        assert opening[0].labels == [
            "1970",
            "1980",
            "1990",
            "2000",
            "2010",
            "2020",
            "Heston and Sadka’s 13%, before 2002",
            "“disappeared since then”",
            "Example 7.7, S&P 500",
            "Example 7.6, S&P 600",
            "Chan’s files, survivors only",
            "the book",
            "two later runs, index as it stood",
        ]

    def test_each_file_names_its_example_beside_its_bar(self, opening, spans) -> None:
        """The S&P 500 file is Example 7.7's and the S&P 600 file Example 7.6's,
        each labelled level with its own bar and just past its end."""
        scene = opening[0]
        for gid, text, (_, end) in (
            ("large-caps", "Example 7.7, S&P 500", spans.large_caps),
            ("small-caps", "Example 7.6, S&P 600", spans.small_caps),
        ):
            bar, label = _stroke(scene, gid), _labelled(scene, text)
            assert label.names == gid
            assert label.y == pytest.approx(bar.y[0])
            assert label.x == pytest.approx(_year(end) + 0.2)
        assert _stroke(scene, "large-caps").y[0] > _stroke(scene, "small-caps").y[0]

    def test_its_alt_text_quotes_its_labels_and_names_each_files_span(self, opening, spans) -> None:
        """Every label but the decades, quoted in the order it is drawn, and each
        file's example named right after the span its bar runs, in the post's
        words for the part of the year: early, mid or late."""
        scene = opening[0]
        alt = _alt(POST.read_text(encoding="utf-8"), scene)
        quoted = [w if w.startswith("“") else f"“{w}”" for w in scene.labels if not w.isdigit()]
        places = [alt.find(w) for w in quoted]
        assert -1 not in places, [w for w, at in zip(quoted, places, strict=True) if at < 0]
        assert places == sorted(places)

        def when(day: pd.Timestamp) -> str:
            return f"{('early', 'mid', 'late')[(day.month - 1) // 4]} {day.year}"

        for text, (start, end) in (
            ("Example 7.7, S&P 500", spans.large_caps),
            ("Example 7.6, S&P 600", spans.small_caps),
        ):
            assert f"from {when(start)} to {when(end)}, labelled “{text}”" in alt

    def test_every_bar_sits_at_its_dates(self, opening, spans) -> None:
        scene = opening[0]
        assert _stroke(scene, "sample").x[-1] == pytest.approx(_year(spans.split))
        assert _stroke(scene, "split").x[0] == pytest.approx(_year(spans.split))
        for gid, (start, end) in (
            ("large-caps", spans.large_caps),
            ("small-caps", spans.small_caps),
        ):
            bar = _stroke(scene, gid)
            assert (bar.x[0], bar.x[-1]) == pytest.approx((_year(start), _year(end))), gid
        later = _stroke(scene, "later")
        assert (later.x[0], later.x[-1]) == pytest.approx(
            (_year(spans.later[0]), _year(spans.later[1]))
        )
        assert _stroke(scene, "book").x[0] == pytest.approx(_year(float(BOOK_YEAR)))

    def test_the_book_is_the_first_edition_the_post_cites_and_the_runs_start_that_year(
        self, spans
    ) -> None:
        assert "Chan, E. P. (2009)" in POST.read_text(encoding="utf-8")
        assert BOOK_YEAR == spans.later[0].year == seasonals.FIRST_HELD.year

    def test_the_monthly_months_hold_the_januaries_too(self, spans) -> None:
        first = pd.Timestamp(f"{BOOK_YEAR}-01-01")
        last = first + pd.DateOffset(years=seasonals.SURVIVOR_JANUARIES - 1)
        assert spans.later[0] <= first and last <= spans.later[1]

    def test_the_axis_runs_1960_to_2030_with_even_decades(self, opening) -> None:
        """Absolute positions: the axis spans the board's timeline, and
        1999-11-24 sits at its share of the seventy years."""
        axis = _stroke(opening[0], "axis")
        lo, hi = TIMELINE_X
        assert (axis.x.min(), axis.x.max()) == pytest.approx((lo, hi))
        ticks = sorted(
            {round(float(x), 9) for x, y in zip(axis.x, axis.y, strict=True) if y < AXIS_Y - 0.1}
        )
        assert len(ticks) == 6
        assert np.diff(ticks) == pytest.approx([(hi - lo) / 7] * 5)
        start = _stroke(opening[0], "large-caps").x[0]
        share = (pd.Timestamp("1999-11-24") - pd.Timestamp("1960-01-01")).days / (
            pd.Timestamp("2030-01-01") - pd.Timestamp("1960-01-01")
        ).days
        assert start == pytest.approx(lo + share * (hi - lo), abs=0.002)

    def test_the_sample_ends_where_chan_says_the_effect_disappeared(self, opening) -> None:
        """Its start is drawn dashed, since nothing here checked it."""
        scene = opening[0]
        lead, sample = _stroke(scene, "sample-lead"), _stroke(scene, "sample")
        assert lead.dashed and not sample.dashed
        assert lead.x[-1] == pytest.approx(sample.x[0])

    def test_chans_files_end_before_the_book_and_the_runs_begin_at_it(self, spans) -> None:
        assert max(spans.large_caps[1], spans.small_caps[1]) < spans.later[0]

    def test_other_spans_move_the_bars(self, spans) -> None:
        moved = dataclasses.replace(
            spans, large_caps=(pd.Timestamp("1995-01-02"), spans.large_caps[1])
        )
        bar = _stroke(opening_scenes(PINNED, moved)[0], "large-caps")
        assert bar.x[0] == pytest.approx(_year(pd.Timestamp("1995-01-02")))


def _labels(scene) -> list[str]:
    return scene.labels


def _xs(scene, gid) -> np.ndarray:
    return _stroke(scene, gid).x


def _middle(scene, gid) -> float:
    """The middle of the stroke's horizontal extent, the centre of a ring or a cross."""
    x = _stroke(scene, gid).x
    return float(x.min() + x.max()) / 2


#: Figures unlike the defaults in every field, so a mark that ignores its
#: figure and draws the default lands in the wrong place.
MOVED = RuleFigures(
    ranked_2006=600,
    longs_2006=60,
    shorts_2006=57,
    pmc_last_close=5.5,
    pmc_gap_days=800,
    pmc_2007_close=12.0,
    pmc_gain=1.1818,
    pmc_rank=3,
    ranked_2007=590,
    empty_months=11,
    held_months=85,
    month_end_rows=97,
    first_pass_row=240,
    repaired_row=11,
)


@pytest.fixture(params=[RuleFigures(), MOVED], ids=["the files' figures", "other figures"])
def figures(request) -> RuleFigures:
    return request.param


def _bar_heights(scene) -> list[float]:
    """Each bar's drawn return in the add-up scene, read from its stroke."""
    bars = _stroke(scene, "bars")
    heights = []
    for k in range(len(sketches.POSITION_RETURNS)):
        x = 0.8 + k * 0.33
        at = np.isclose(bars.x, x)
        offsets = bars.y[at] - sketches.SUM_BASE
        heights.append(float(offsets[np.argmax(np.abs(offsets))]))
    return heights


class TestTheRuleSketches:
    """What each rule sketch says and where it puts its marks."""

    def test_they_are_seven_in_the_order_the_post_reads_them(self, rules) -> None:
        assert [gif_name(scene) for scene in rules] == RULE_GIFS

    def test_each_prints_its_figures(self, rules) -> None:
        short, filled, _, _, empty, _, lookup = rules
        assert _labels(short) == [
            "buy the 58 worst",
            "short 56 of the 58 best",
            "a tenth: 58",
            "2 left out: the best and the 58th",
            "the winners are sliced as topN − 2",
            "January 2006, 579 stocks ranked",
        ]
        assert [s for s in _labels(filled) if not s.isdigit()] == [
            "PMC",
            "last close 6.02, then 851 trading days with no price",
            "end of 2006",
            "13.88",
            "+130.56% read as 2007’s gain",
            "4th best of 595: shorted",
        ]
        assert _labels(empty) == [
            "month 1: no return",
            "12 months with no position, each a 0",
            "83 months that hold positions",
            "first edition: sum ÷ 95",
            "revised: sum ÷ 83",
        ]
        assert _labels(lookup) == [
            "96 month-end rows",
            "row 1",
            "row 96",
            "row 258",
            "the first pass asks for it and stops",
            "the repair reads row m − 1, here 13",
        ]

    def test_the_schematic_ones_say_what_they_should(self, rules) -> None:
        _, _, bars, wrong, _, own, _ = rules
        assert _labels(bars) == [
            "one month’s N positions",
            "first edition: add them up",
            "summed positions",
            "revised: ÷ N",
            "capital",
            "each month is N times too big",
        ]
        assert _labels(wrong) == [
            "sorted by return",
            *sketches.SORTED,
            "column order",
            *sketches.COLUMNS,
            "no close",
            "E dropped: C has no close",
            "C ranked anyway",
            "each check reads the column, not the stock",
        ]
        assert _labels(own) == [
            "shared month-end row",
            "stock A",
            "stock B",
            "missing",
            "B’s own last priced day, which the revised Python reads",
            "the month’s last five trading days",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        short, filled, _, _, empty, _, lookup = rule_scenes(MOVED)
        assert "3 left out: the best and the 60th" in _labels(short)
        assert "January 2006, 600 stocks ranked" in _labels(short)
        assert "3rd best of 590: shorted" in _labels(filled)
        assert "+118.18% read as 2007’s gain" in _labels(filled)
        assert "last close 5.50, then 800 trading days with no price" in _labels(filled)
        assert "first edition: sum ÷ 96" in _labels(empty)
        assert "revised: sum ÷ 85" in _labels(empty)
        assert "the repair reads row m − 1, here 11" in _labels(lookup)
        assert "row 240" in _labels(lookup) and "97 month-end rows" in _labels(lookup)

    def test_the_two_sides_are_to_scale_and_the_long_side_reaches_a_tenth(self, figures) -> None:
        short = rule_scenes(figures)[0]
        long_bar, short_bar = _stroke(short, "long"), _stroke(short, "short")
        assert np.ptp(long_bar.x) == pytest.approx(figures.longs_2006 * sketches.STOCK_WIDTH)
        assert np.ptp(short_bar.x) == pytest.approx(figures.shorts_2006 * sketches.STOCK_WIDTH)
        assert _xs(short, "tenth").min() == pytest.approx(long_bar.x.max())
        gap = _stroke(short, "missing")
        assert (gap.x.min(), gap.x.max()) == pytest.approx((short_bar.x.max(), long_bar.x.max()))
        assert (long_bar.color, short_bar.color) == (GOOD, LOST)

    def test_pmcs_close_is_carried_flat_to_the_end_of_2006_and_rises_to_2007s(
        self, figures
    ) -> None:
        filled = rule_scenes(figures)[1]
        carried = _stroke(filled, "carried")
        assert np.ptp(carried.y) == pytest.approx(0.0)
        assert carried.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_last_close))
        start, end = _stroke(filled, "end-2006"), _stroke(filled, "end-2007")
        assert start.x[0] == pytest.approx(sketches._pmc_x(2007.0))
        assert carried.x.max() == pytest.approx(start.x[0])
        assert start.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_last_close))
        assert end.y[0] == pytest.approx(sketches._pmc_y(figures.pmc_2007_close))
        assert sketches._pmc_x(2007.5) < end.x[0] < sketches._pmc_x(2008.0)
        after = _stroke(filled, "after")
        assert end.y[0] in after.y and end.x[0] in after.x
        gain = _stroke(filled, "gain")
        assert gain.color == LOST and gain.y.max() > gain.y[0]

    def test_the_sum_is_the_bars_added_up_and_n_times_the_average(self, rules) -> None:
        bars = rules[2]
        heights = _bar_heights(bars)
        assert heights == pytest.approx(list(sketches.POSITION_RETURNS))
        total = _stroke(bars, "sum").y.min() - sketches.SUM_BASE
        mean = _stroke(bars, "mean").y.min() - sketches.SUM_BASE
        assert total == pytest.approx(sum(heights))
        assert total == pytest.approx(len(heights) * mean)
        assert total < mean < 0

    def test_the_check_pairs_columns_and_rings_the_wrong_stock(self, rules) -> None:
        wrong = rules[3]
        hole = sketches.COLUMNS.index(sketches.NO_CLOSE)
        for k in range(len(sketches.COLUMNS)):
            arrow = _stroke(wrong, f"pair-{k}")
            assert arrow.x[0] == pytest.approx(sketches._card(k))
            assert arrow.color == (LOST if k == hole else whiteboard.MUTED)
        rising = _stroke(wrong, f"pair-{hole}")
        assert rising.y[0] < rising.y.max() == pytest.approx(sketches.SORTED_Y - 0.42)
        assert _middle(wrong, "dropped") == pytest.approx(sketches._card(hole), abs=0.01)
        assert sketches.SORTED[hole] != sketches.NO_CLOSE
        kept_at = sketches.SORTED.index(sketches.NO_CLOSE)
        assert _middle(wrong, "kept") == pytest.approx(sketches._card(kept_at), abs=0.01)
        assert _middle(wrong, "no-close") == pytest.approx(sketches._card(hole), abs=0.01)
        assert (_stroke(wrong, "dropped").color, _stroke(wrong, "kept").color) == (
            LOST,
            whiteboard.ACCENT,
        )

    def test_the_months_are_counted_and_each_bracket_spans_its_mean(self, figures) -> None:
        empty = rule_scenes(figures)[4]
        months = 1 + figures.empty_months + figures.held_months
        assert _stroke(empty, "empty").points == figures.empty_months
        assert _stroke(empty, "held").points == figures.held_months
        assert _middle(empty, "missing") == pytest.approx(sketches._month(1, months), abs=0.01)
        first, revised = _stroke(empty, "first"), _stroke(empty, "revised")
        assert (first.x.min(), first.x.max()) == pytest.approx(
            (sketches._month(2, months), sketches._month(months, months))
        )
        assert (revised.x.min(), revised.x.max()) == pytest.approx(
            (sketches._month(2 + figures.empty_months, months), sketches._month(months, months))
        )
        assert revised.x.min() == pytest.approx(_stroke(empty, "held").x.min())

    def test_b_is_read_on_its_own_last_day_and_missing_on_the_shared_row(self, rules) -> None:
        own = rules[5]
        shared = next(step for step in own.fills if step.gid == "shared")
        last = sketches.DAYS_X[-1]
        assert shared.x0 < last < shared.x1
        assert _stroke(own, "a").points == len(sketches.DAYS_X)
        b = _stroke(own, "b")
        assert b.x.max() < shared.x0
        assert _middle(own, "b-own") == pytest.approx(b.x.max(), abs=0.01)
        assert _middle(own, "b-missing") == pytest.approx(last, abs=0.01)
        assert (_stroke(own, "b-own").color, _stroke(own, "b-missing").color) == (GOOD, LOST)

    def test_the_lookup_runs_past_the_rows_and_the_repair_reads_a_row(self, figures) -> None:
        lookup = rule_scenes(figures)[6]
        x0, x1, _ = sketches.ROWS
        assert _stroke(lookup, "past").x.min() == pytest.approx(x1)
        assert _middle(lookup, "asks") > x1
        width = (x1 - x0) / figures.month_end_rows
        repair = _stroke(lookup, "repair")
        assert repair.x[0] == pytest.approx(x0 + (figures.repaired_row - 0.5) * width)


#: Figures unlike the file's, with the halves further apart than the years,
#: so a mark drawn from the defaults lands in the wrong place.
SWUNG = SplitFigures(before_2002=-0.05, from_2002=0.12, year_2002=-0.08, year_2006=0.04)


#: Figures with the halves the other way round, so a gap that is not a
#: distance would print with a minus sign.
FLIPPED = SplitFigures(before_2002=0.09, from_2002=-0.02, year_2002=0.15, year_2006=-0.1)


@pytest.fixture(
    params=[SplitFigures(), SWUNG, FLIPPED],
    ids=["the file's figures", "other figures", "the halves the other way round"],
)
def split_figures(request) -> SplitFigures:
    return request.param


class TestTheSplitSketch:
    """The two halves' annual returns beside two single years, to one scale."""

    def test_it_says_what_it_should(self, split) -> None:
        (swing,) = split
        assert gif_name(swing) == SPLIT_GIFS[0]
        assert swing.labels == [
            "the two halves, an average year",
            "before 2002",
            "−0.145387",
            "from 2002",
            "+0.011967",
            "0.1574 apart",
            "two single years, 12 months each",
            "2002",
            "+0.2227",
            "2006",
            "−0.1319",
            "0.3546 apart",
            "before costs",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        (swing,) = split_scenes(SWUNG)
        for text in (
            "−0.050000",
            "+0.120000",
            "0.1700 apart",
            "−0.0800",
            "+0.0400",
            "0.1200 apart",
        ):
            assert text in swing.labels, text

    def test_each_bar_runs_from_zero_to_its_figure_in_its_signs_colour(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        for gid, value in (
            ("before", f.before_2002),
            ("after", f.from_2002),
            ("y2002", f.year_2002),
            ("y2006", f.year_2006),
        ):
            bar = _stroke(swing, gid)
            assert np.ptp(bar.x) == pytest.approx(0.0)
            assert bar.y[0] == pytest.approx(sketches.SWING_ZERO)
            assert bar.y[-1] - bar.y[0] == pytest.approx(value * sketches.SWING_PER)
            assert bar.color == (GOOD if value > 0 else LOST), gid

    def test_each_bracket_spans_its_pairs_gap(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        for gid, ends in (
            ("halves-gap", (f.before_2002, f.from_2002)),
            ("years-gap", (f.year_2002, f.year_2006)),
        ):
            bracket = _stroke(swing, gid)
            assert (bracket.y.min(), bracket.y.max()) == pytest.approx(
                tuple(sketches._swing_y(v) for v in sorted(ends))
            ), gid

    def test_the_years_bracket_is_longer_on_the_files_figures(self, split) -> None:
        (swing,) = split
        halves = np.ptp(_stroke(swing, "halves-gap").y)
        years = np.ptp(_stroke(swing, "years-gap").y)
        assert years / halves == pytest.approx(0.35464347755594144 / 0.15735417776401822)
        assert years > 2 * halves

    def test_each_pair_stands_in_its_own_group(self, split) -> None:
        (swing,) = split
        halves = [_stroke(swing, gid).x[0] for gid in ("before", "after")]
        years = [_stroke(swing, gid).x[0] for gid in ("y2002", "y2006")]
        assert max(halves) < _stroke(swing, "halves-gap").x.max() < min(years)
        assert max(years) < _stroke(swing, "years-gap").x.max()

    def test_each_gap_prints_as_a_distance(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        gaps = [text for text in swing.labels if text.endswith(" apart")]
        assert gaps == [
            f"{abs(f.from_2002 - f.before_2002):.4f} apart",
            f"{abs(f.year_2002 - f.year_2006):.4f} apart",
        ]

    def test_each_value_sits_by_its_bar_in_its_signs_colour(self, split_figures) -> None:
        (swing,) = split_scenes(split_figures)
        f = split_figures
        values = {
            "before": f.before_2002,
            "after": f.from_2002,
            "y2002": f.year_2002,
            "y2006": f.year_2006,
        }
        for gid, value in values.items():
            places = 6 if gid in ("before", "after") else 4
            text = f"{value:+.{places}f}".replace("-", "−")
            (label,) = [s for s in swing.steps if isinstance(s, Label) and s.text == text]
            assert label.names == gid
            assert abs(label.x - _stroke(swing, gid).x[0]) <= 0.25, gid
            assert label.color == (GOOD if value > 0 else LOST), gid

    def test_both_brackets_and_their_gaps_are_brown(self, split) -> None:
        (swing,) = split
        for gid in ("halves-gap", "years-gap"):
            assert _stroke(swing, gid).color == whiteboard.ACCENT
        gaps = [s for s in swing.steps if isinstance(s, Label) and s.text.endswith(" apart")]
        assert [s.color for s in gaps] == [whiteboard.ACCENT, whiteboard.ACCENT]


#: Five-year figures unlike the file's in every field, so a mark drawn from
#: the defaults lands in the wrong place.
SHIFTED = FiveYearFigures(
    whole_months=80,
    before_months=10,
    after_months=70,
    rerun_months=44,
    between_months=26,
    whole_python=-0.02,
    before_2002=0.1,
    from_2002=-0.02,
    rerun_python=-0.03,
    between=-0.05,
    whole_matlab=-0.01,
    rerun_matlab=-0.02,
    rerun_error=0.015,
    januaries=((2006, 0.03), (2007, -0.02), (2008, 0.05)),
)


@pytest.fixture(params=[FiveYearFigures(), SHIFTED], ids=["the files' figures", "other figures"])
def five_figures(request) -> FiveYearFigures:
    return request.param


def _labelled(scene, text: str) -> Label:
    (label,) = [s for s in scene.steps if isinstance(s, Label) and s.text == text]
    return label


class TestTheFiveYearSketches:
    """The months each figure covers, the gap against the noise, and three Januaries."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, five) -> None:
        assert [gif_name(scene) for scene in five] == FIVE_YEAR_GIFS

    def test_each_says_what_it_should(self, five) -> None:
        months, noise, januaries = five
        assert months.labels == [
            *[str(year) for year in range(2001, 2008)],
            "whole period: 83 months, −0.012679",
            "before 2002: 13 months, −0.145387",
            "from 2002: 70 months, +0.011967",
            "first year only ranks",
            "five-year rerun: 47 months, −0.016431",
            "23 months the rerun leaves out: +0.069997",
            "revised Python’s rules, a year, before costs",
        ]
        assert noise.labels == [
            "one standard error each way, 0.0281",
            "−0.04",
            "−0.02",
            "0",
            "five-year rerun −0.0165",
            "whole period −0.0129",
            "0.0036 apart",
            "revised MATLAB’s rules, a year, before costs",
        ]
        assert januaries.labels == [
            "January 2006",
            "−0.0244",
            "January 2007",
            "−0.0068",
            "January 2008",
            "+0.0881",
            "three trades",
            "Example 7.6 in MATLAB, after costs",
        ]

    def test_other_figures_move_the_labels(self) -> None:
        months, noise, januaries = five_year_scenes(SHIFTED)
        for text in (
            "whole period: 80 months, −0.020000",
            "before 2002: 10 months, +0.100000",
            "five-year rerun: 44 months, −0.030000",
            "26 months the rerun leaves out: −0.050000",
        ):
            assert text in months.labels, text
        for text in (
            "one standard error each way, 0.0150",
            "0.0100 apart",
            "five-year rerun −0.0200",
        ):
            assert text in noise.labels, text
        assert "+0.0300" in januaries.labels and "−0.0200" in januaries.labels

    def test_each_bar_on_the_timeline_covers_its_months(self, five) -> None:
        """Each bar's length is its month count, a twelfth of a year each."""
        (months, _, _) = five
        figures = FiveYearFigures()
        month = sketches._when(sketches.MONTHS_FROM + 1 / 12) - sketches._when(sketches.MONTHS_FROM)
        whole = _stroke(months, "whole")
        assert np.ptp(whole.x) == pytest.approx(figures.whole_months * month)
        halves = np.ptp(_stroke(months, "before").x) + np.ptp(_stroke(months, "after").x)
        assert halves == pytest.approx(
            (figures.before_months + figures.after_months) * month, abs=0.09
        )
        assert np.ptp(_stroke(months, "rerun").x) == pytest.approx(figures.rerun_months * month)
        assert np.ptp(_stroke(months, "warm-up").x) == pytest.approx(12 * month)
        between = _stroke(months, "between")
        assert np.ptp(between.x) == pytest.approx(figures.between_months * month)
        assert between.x.max() == pytest.approx(_stroke(months, "rerun").x.min())
        assert between.x.min() == pytest.approx(sketches._when(sketches.SPLIT_YEAR))

    def test_the_timeline_takes_its_colours_from_the_signs(self, five_figures) -> None:
        months = five_year_scenes(five_figures)[0]
        f = five_figures
        assert _stroke(months, "before").color == (GOOD if f.before_2002 > 0 else LOST)
        assert _stroke(months, "after").color == (GOOD if f.from_2002 > 0 else LOST)
        assert _stroke(months, "between").color == (GOOD if f.between > 0 else LOST)
        assert _stroke(months, "warm-up").dashed
        for gid, prefix in (
            ("before", "before 2002:"),
            ("after", "from 2002:"),
            ("between", f"{f.between_months} months the rerun"),
        ):
            (label,) = [
                s for s in months.steps if isinstance(s, Label) and s.text.startswith(prefix)
            ]
            assert label.color == _stroke(months, gid).color, gid

    def test_each_year_label_sits_on_its_tick(self, five) -> None:
        months = five[0]
        axis = _stroke(months, "axis")
        for year in range(2001, 2008):
            label = _labelled(months, str(year))
            assert label.x == pytest.approx(sketches._when(year))
            assert np.isclose(axis.x, label.x).sum() >= 2, year
            assert axis.y[np.isclose(axis.x, label.x)].min() < sketches.MONTHS_AXIS_Y

    def test_each_value_on_the_noise_line_sits_on_its_tick(self, five) -> None:
        noise = five[1]
        line = _stroke(noise, "line")
        for value, text in ((-0.04, "−0.04"), (-0.02, "−0.02"), (0.0, "0")):
            label = _labelled(noise, text)
            assert label.x == pytest.approx(sketches._on_noise(value))
            assert line.y[np.isclose(line.x, label.x)].min() < sketches.NOISE_Y, text

    def test_each_alt_text_quotes_its_sketchs_words(self, five) -> None:
        """Every label but the axis numbers appears in the alt text word for word."""
        text = POST.read_text(encoding="utf-8")
        ticks = {str(year) for year in range(2001, 2008)} | {"−0.04", "−0.02", "0"}
        for scene in five:
            match = re.search(
                rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text
            )
            assert match, scene.slug
            alt = match.group(1)
            assert f"“{scene.title}”" in alt, scene.slug
            for label in scene.labels:
                if label not in ticks and not label.startswith("January "):
                    assert label in alt, (scene.slug, label)

    def test_the_band_and_dots_stand_at_their_figures(self, five_figures) -> None:
        noise = five_year_scenes(five_figures)[1]
        f = five_figures
        band = next(step for step in noise.fills if step.gid == "band")
        assert band.x0 == pytest.approx(sketches._on_noise(f.rerun_matlab - f.rerun_error))
        assert band.x1 == pytest.approx(sketches._on_noise(f.rerun_matlab + f.rerun_error))
        rerun, whole = _stroke(noise, "rerun"), _stroke(noise, "whole")
        assert rerun.x[0] == pytest.approx(sketches._on_noise(f.rerun_matlab))
        assert whole.x[0] == pytest.approx(sketches._on_noise(f.whole_matlab))
        gap = _stroke(noise, "gap")
        assert (gap.x.min(), gap.x.max()) == pytest.approx(tuple(sorted((rerun.x[0], whole.x[0]))))

    def test_the_gap_is_far_inside_the_band_on_the_files_figures(self, five) -> None:
        noise = five[1]
        band = next(step for step in noise.fills if step.gid == "band")
        gap = _stroke(noise, "gap")
        assert (band.x1 - band.x0) / np.ptp(gap.x) > 15

    def test_each_january_bar_runs_to_its_trade(self, five_figures) -> None:
        januaries = five_year_scenes(five_figures)[2]
        for year, r in five_figures.januaries:
            bar = _stroke(januaries, f"jan-{year}")
            assert bar.y[0] == pytest.approx(sketches.JANUARY_ZERO)
            assert bar.y[-1] - bar.y[0] == pytest.approx(r * sketches.JANUARY_PER)
            assert bar.color == (GOOD if r > 0 else LOST)
            value = _labelled(januaries, f"{r:+.4f}".replace("-", "−"))
            assert value.names == f"jan-{year}" and value.color == bar.color
            assert abs(value.x - bar.x[0]) < 1e-9

    def test_the_paced_sketches_build_slowly_and_hold_twelve_seconds(self, every) -> None:
        """The pace the owner accepted: each label alone for 0.9 s, the drawing for 12 s."""
        assert (sketches.PACED_LABEL_MS, sketches.PACED_HOLD_MS) == (900, 12000)
        for scene in every:
            frames = sketch_timeline(scene)
            labels = [
                f
                for f in frames[:-1]
                if f.partial == 0 and f.done and isinstance(scene.steps[f.done - 1], Label)
            ]
            paced = scene.slug in sketches.PACED
            assert paced == (
                scene.slug
                in (
                    "which_years",
                    "rule_short_side",
                    "two_verdicts",
                    "five_year_months",
                    "five_year_noise",
                    "survivors_ranking",
                    "survivors_panels",
                    "january_fill",
                    "january_ranges",
                    "ivv_leavers",
                    "osap_sources",
                    "osap_before",
                    "delta_scatter",
                    "delta_shortcut",
                    "delta_bracket",
                    "broad_before_after",
                    "broad_together",
                    "broad_running",
                    "january_catch",
                    "january_years",
                )
            )
            assert {f.ms for f in labels} <= {
                sketches.PACED_LABEL_MS if paced else whiteboard.LABEL_MS
            }
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


class TestTheSurvivorSketches:
    """The three schematic sketches of survivorship bias, one in the opening and two in Lesson 3."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, survivors) -> None:
        assert [gif_name(scene) for scene in survivors] == SURVIVOR_GIFS

    def test_each_says_what_it_should(self, survivors) -> None:
        saved, ranking, panels = survivors
        assert saved.labels == [
            "1999",
            "2003",
            "2007",
            "companies still in the index in 2007",
            "acquired",
            "shrank out of the index",
            "failed",
            "Chan saves the file",
            "in the file",
            "missing from it",
        ]
        assert ranking.labels == [
            "as it stood",
            "lowest return",
            "highest",
            "worst tenth",
            "in the file",
            "the file’s worst tenth: a different set",
            "red rings: companies that left the index before the file was saved",
        ]
        assert panels.labels == [
            "a file saved in 2007",
            "joined later, carried back",
            "2007’s members, carried back",
            "the index as it stood",
            "joined",
            "left",
            "left",
            "members at each ranking date",
            "the later runs, from 2009, used the data on the right",
        ]

    def test_the_survivors_reach_the_save_and_the_leavers_stop_short(self, survivors) -> None:
        saved = survivors[0]
        save = _stroke(saved, "save")
        for k in range(len(sketches.SURVIVOR_ROWS)):
            line = _stroke(saved, f"survivor-{k}")
            assert (line.x.min(), line.x.max()) == pytest.approx(
                (sketches.SAVED_FROM_X, sketches.SAVED_TO_X)
            )
            assert line.color == whiteboard.INK
        for k, (_, share, why) in enumerate(sketches.LEAVERS):
            line = _stroke(saved, f"leaver-{k}")
            assert line.x.max() < sketches.SAVED_TO_X and line.color == LOST, why
            assert line.x.max() == pytest.approx(
                sketches.SAVED_FROM_X + (sketches.SAVED_TO_X - sketches.SAVED_FROM_X) * share
            )
        assert save.dashed and save.x[0] > sketches.SAVED_TO_X

    def test_each_bracket_spans_its_rows_past_the_save(self, survivors) -> None:
        saved = survivors[0]
        save_x = _stroke(saved, "save").x[0]
        rows = sketches.SURVIVOR_ROWS
        leavers = [y for y, _, _ in sketches.LEAVERS]
        for gid, ys, colour in (("in-file", rows, whiteboard.INK), ("not-in-file", leavers, LOST)):
            bracket = _stroke(saved, gid)
            assert bracket.x.min() > save_x
            assert bracket.y.min() < min(ys) and bracket.y.max() > max(ys)
            assert bracket.color == colour

    def test_the_file_drops_the_leavers_so_its_tenth_is_a_different_set(self, survivors) -> None:
        ranking = survivors[1]
        xs = np.linspace(*sketches.SURVIVOR_XS, sketches.SURVIVOR_RANKED)
        kept = [k for k in range(sketches.SURVIVOR_RANKED) if k not in sketches.GONE]
        stood, in_file = _stroke(ranking, "stood"), _stroke(ranking, "file")
        assert stood.x == pytest.approx(xs[kept]) and in_file.x == pytest.approx(xs[kept])
        for k in sketches.GONE:
            assert _middle(ranking, f"gone-{k}") == pytest.approx(xs[k], abs=0.01)
            assert _stroke(ranking, f"gone-{k}").color == LOST
        tenth = sketches.SURVIVOR_TENTH
        assert _middle(ranking, "stood-tenth") == pytest.approx(xs[:tenth].mean(), abs=0.01)
        assert _middle(ranking, "file-tenth") == pytest.approx(xs[kept[:tenth]].mean(), abs=0.01)
        assert set(range(tenth)) & set(sketches.GONE), "the worst tenth as it stood holds a leaver"
        assert not set(kept[:tenth]) & set(sketches.GONE)
        assert _stroke(ranking, "stood-tenth").dashed
        assert _stroke(ranking, "file-tenth").color == whiteboard.ACCENT
        assert sketches.SURVIVOR_TENTH * 10 == sketches.SURVIVOR_RANKED

    def test_the_saved_panel_keeps_no_leaver_and_carries_the_joiner_back(self, survivors) -> None:
        panels = survivors[2]
        left, right = sketches.SAVED_PANEL, sketches.STOOD_PANEL
        saved = [s for s in panels.strokes if s.gid.startswith("saved-")]
        assert len(saved) == 7
        for line in saved:
            assert (line.x.min(), line.x.max()) == pytest.approx(left)
        assert _stroke(panels, "saved-joiner").color == GOOD
        for k in range(6):
            assert _stroke(panels, f"saved-{k}").color == whiteboard.INK
        stood = [s for s in panels.strokes if s.gid.startswith("stood-")]
        assert len(stood) == 9
        for line, (a, b), colour in zip(
            stood, sketches.STOOD_SPANS, sketches.STOOD_COLOURS, strict=True
        ):
            assert (line.x.min(), line.x.max()) == pytest.approx(
                (sketches._panel_x(right, a), sketches._panel_x(right, b))
            )
            assert line.color == colour
        assert sketches.STOOD_COLOURS.count(LOST) == 2
        assert sketches.STOOD_SPANS[6][0] > 0 and sketches.STOOD_COLOURS[6] == GOOD
        for (a, b), colour in zip(sketches.STOOD_SPANS, sketches.STOOD_COLOURS, strict=True):
            if colour == whiteboard.INK:
                assert (a, b) == (0, 1)
            elif colour == LOST:
                assert a == 0 and b < 1
            else:
                assert a > 0 and b == 1

    def test_each_alt_text_quotes_its_sketchs_words(self, survivors) -> None:
        """Every label but the axis years appears in the alt text word for word,
        and the alt text's counts are the sketch's."""
        text = POST.read_text(encoding="utf-8")
        for scene in survivors:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label not in ("1999", "2003", "2007"):
                    assert label in alt, (scene.slug, label)
        saved = _alt(text, survivors[0]).lower()
        assert f"{_count_word(len(sketches.SURVIVOR_ROWS))} black lines" in saved
        assert f"{_count_word(len(sketches.LEAVERS))} red lines" in saved
        ranking = _alt(text, survivors[1]).lower()
        assert f"ranks {_count_word(sketches.SURVIVOR_RANKED)} stocks" in ranking
        assert f"{_count_word(len(sketches.GONE))} of them drawn as red rings" in ranking


def _alt(text: str, scene) -> str:
    match = re.search(rf"!\[([^\]]+)\]\(\.\./docs/figures/{re.escape(gif_name(scene))}\)", text)
    assert match, scene.slug
    alt = match.group(1)
    assert f"“{scene.title}”" in alt, scene.slug
    return alt


def _count_word(n: int) -> str:
    return {3: "three", 6: "six", 18: "eighteen", 20: "twenty"}.get(n, str(n))


class TestTheJanuarySketches:
    """The three January sketches, the first in the opening: registered, the fill, the ranges."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, january) -> None:
        assert [gif_name(scene) for scene in january] == JANUARY_GIFS

    def test_each_says_what_it_should(self, january) -> None:
        registered, fill, ranges = january
        assert registered.labels == [
            "claim",
            "test",
            "verdict’s words",
            "all written down",
            "then returns computed",
            "registered",
            "returns computed",
            "no claim written down first",
            "exploratory",
            "exploratory can kill an idea, only registered can confirm one",
        ]
        assert fill.labels == [
            "buy the worst tenth",
            "short the best tenth",
            "?",
            "a member with no checked price",
            "could land in a traded tenth",
            "low version",
            "if bought: near the worst January return",
            "if shorted: near the best",
            "high version",
            "if bought: near the best January return",
            "if shorted: near the worst",
            "so each January gets a low and a high result",
        ]
        assert ranges.title == "Eighteen Januaries, each a range"
        assert ranges.labels == [
            "0",
            "2009",
            "2014",
            "2019",
            "2026",
            "each bar runs from a January’s low version to its high",
            "black: straddles zero, so free data cannot tell which side",
            "before costs",
            "brown dot: the unchecked members left out",
        ]

    def test_the_written_steps_come_before_the_line_and_the_returns_after(self, january) -> None:
        registered = january[0]
        line = _stroke(registered, "written").x[0]
        for k in range(len(sketches.WRITTEN_STEPS)):
            assert _stroke(registered, f"box-{k}").x.max() < line
        assert _stroke(registered, "box-3").x.min() > line
        assert _stroke(registered, "box-3").color == GOOD
        assert _stroke(registered, "box-4").color == LOST
        assert _stroke(registered, "box-4").x.max() < _stroke(registered, "box-5").x.min()

    def test_the_gap_can_land_in_a_traded_tenth(self, january) -> None:
        fill = january[1]
        xs = np.linspace(*sketches.FILL_XS, sketches.FILL_RANKED)
        tenth = sketches.FILL_TENTH
        assert tenth * 10 == sketches.FILL_RANKED
        assert _middle(fill, "buy") == pytest.approx(xs[:tenth].mean(), abs=0.01)
        assert _middle(fill, "short") == pytest.approx(xs[-tenth:].mean(), abs=0.01)
        assert (_stroke(fill, "buy").color, _stroke(fill, "short").color) == (GOOD, LOST)
        colours = {s.text: s.color for s in fill.steps if isinstance(s, Label)}
        for text in (
            "low version",
            "if bought: near the worst January return",
            "if shorted: near the best",
        ):
            assert colours[text] == LOST, text
        for text in (
            "high version",
            "if bought: near the best January return",
            "if shorted: near the worst",
        ):
            assert colours[text] == GOOD, text
        to_buy, to_short = _stroke(fill, "to-buy"), _stroke(fill, "to-short")
        assert to_buy.x[0] < sketches.UNPRICED[0] < to_short.x[0]
        assert to_buy.x.min() < xs[tenth] and to_short.x.max() > xs[-tenth - 1]

    @pytest.mark.parametrize(
        "ranges",
        [
            PINNED_RANGES,
            JanuaryRanges(
                ((2009, -0.2, 0.1), (2010, 0.02, 0.05), (2011, -0.04, -0.01)), (0.0, 0.03, -0.02)
            ),
        ],
        ids=["the run's Januaries", "other Januaries"],
    )
    def test_each_bar_runs_from_low_to_high_in_its_colour(self, ranges) -> None:
        scene = january_scenes(ranges)[2]
        xs = np.linspace(*sketches.RANGES_X, len(ranges.januaries))
        for x, (year, low, high) in zip(xs, ranges.januaries, strict=True):
            bar = _stroke(scene, f"jan-{year}")
            assert bar.x == pytest.approx(np.full(bar.points, x))
            assert bar.y[0] == pytest.approx(sketches.RANGES_ZERO + low * sketches.RANGES_PER)
            assert bar.y[-1] == pytest.approx(sketches.RANGES_ZERO + high * sketches.RANGES_PER)
            expected = whiteboard.INK if low < 0 < high else (GOOD if low > 0 else LOST)
            assert bar.color == expected, year
        for x, (year, _, _), left_out in zip(xs, ranges.januaries, ranges.left_out, strict=True):
            dot = _stroke(scene, f"left-{year}")
            assert (dot.points, dot.color) == (1, ACCENT), year
            assert dot.x[0] == pytest.approx(x + sketches.RANGES_DOT_OFFSET), year
            assert dot.y[0] == pytest.approx(sketches.RANGES_ZERO + left_out * sketches.RANGES_PER)
        count = len(ranges.januaries)
        word = {18: "Eighteen", 3: "Three"}[count]
        assert scene.title == f"{word} Januaries, each a range"

    def test_the_runs_januaries_straddle_but_four(self) -> None:
        """What the alt text says: 2020, 2021 and 2024 below zero, 2023 above."""
        below = [y for y, low, high in PINNED_RANGES.januaries if high < 0]
        above = [y for y, low, high in PINNED_RANGES.januaries if low > 0]
        assert (below, above) == ([2020, 2021, 2024], [2023])

    def test_each_alt_text_quotes_its_sketchs_words(self, january) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in january:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label not in ("0", "2014", "2019", "?"):
                    assert label in alt, (scene.slug, label)
        ranges = _alt(text, january[2])
        assert "Eighteen vertical bars" in ranges and "2020, 2021 and 2024" in ranges
        assert "the bar for 2023 is green" in ranges
        assert "every dot falls inside its bar’s range" in ranges

    def test_each_dot_clears_its_bar(self, january) -> None:
        """A dot on its bar hides the short late bars, which the first draw did."""
        ranges = january[2]
        year = PINNED_RANGES.januaries[-1][0]
        bar, dot = _stroke(ranges, f"jan-{year}"), _stroke(ranges, f"left-{year}")
        assert sketches.RANGES_DOT_OFFSET >= 0.1
        assert dot.x[0] - bar.x[0] == pytest.approx(sketches.RANGES_DOT_OFFSET)

    def test_every_dot_sits_inside_its_januarys_range(self) -> None:
        """What the alt text says, and what places the left-out figure between the two."""
        for (year, low, high), left_out in zip(
            PINNED_RANGES.januaries, PINNED_RANGES.left_out, strict=True
        ):
            assert low <= left_out <= high, year

    def test_the_dots_average_to_the_left_out_mean(self) -> None:
        """The post's −0.0083, which ``tests/test_equity_seasonals.py`` pins on the archive."""
        assert float(np.mean(PINNED_RANGES.left_out)) == pytest.approx(
            -0.00833318712859331, abs=1e-12
        )

    def test_the_ranges_average_to_the_verdicts_pinned_means(self) -> None:
        """The two pins come from one run, so the Januaries average to its means."""
        lows = [low for _, low, _ in PINNED_RANGES.januaries]
        highs = [high for _, _, high in PINNED_RANGES.januaries]
        assert float(np.mean(lows)) == pytest.approx(PINNED.january_low, abs=1e-12)
        assert float(np.mean(highs)) == pytest.approx(PINNED.january_high, abs=1e-12)

    def test_a_redraw_with_the_archive_draws_the_ranges_from_the_run(
        self, monkeypatch, tmp_path, spans
    ) -> None:
        """Without this, a redraw could draw the ranges without reading the run."""
        run, seen = object(), []

        def from_run(january):
            seen.append(january)
            return PINNED_RANGES

        monkeypatch.setattr(seasonals, "run_point_in_time", lambda: run)
        monkeypatch.setattr(seasonals, "run_monthly_point_in_time", lambda: object())
        monkeypatch.setattr(sketches.Verdicts, "from_runs", classmethod(lambda cls, a, b: PINNED))
        monkeypatch.setattr(sketches.IvvFigures, "from_run", classmethod(lambda cls, m: PINNED_IVV))
        monkeypatch.setattr(
            sketches.JanuaryRanges, "from_run", classmethod(lambda cls, january: from_run(january))
        )
        powers = []

        def power_from_run(january):
            powers.append(january)
            return PINNED_POWER

        monkeypatch.setattr(
            sketches.JanuaryPower,
            "from_run",
            classmethod(lambda cls, january: power_from_run(january)),
        )
        written = make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans)
        assert sorted(path.name for path in written) == sorted(GIFS)
        assert (seen, powers) == ([run], [run])
        seen.clear(), powers.clear()
        make_equity_seasonals_whiteboards(out_dir=tmp_path, spans=spans, verdicts=PINNED)
        assert seen == [run], "the ranges are read from the run even when the verdicts are given"
        assert powers == [run], "so are the spreads"
        seen.clear(), powers.clear()
        make_equity_seasonals_whiteboards(
            out_dir=tmp_path, spans=spans, verdicts=PINNED, ranges=PINNED_RANGES
        )
        assert (seen, powers) == ([], [run]), "the spreads are read even when the rest is given"


#: Made-up spreads for the two sketches under "What 18 Januaries can detect",
#: so a count, a mark or a word that should follow the run is seen to.
OTHER_POWER = JanuaryPower(n=12, low_std=0.05, high_std=0.06)


class TestTheJanuaryPowerSketches:
    """The two under "What 18 Januaries can detect": what the run's Januaries
    can catch, and how many more Januaries a smaller effect takes."""

    def test_they_are_two_in_the_order_the_post_reads_them(self, power) -> None:
        assert [gif_name(scene) for scene in power] == POWER_GIFS

    def test_the_pinned_spread_gives_the_runs_x(self) -> None:
        """The X that ``TestThePointInTimePins`` pins, 0.0547 and 0.0615, and
        the X at four times the Januaries the years sketch marks."""
        assert PINNED_POWER.detectable() == pytest.approx(
            (0.05474237393477483, 0.06153368896545796), abs=1e-12
        )
        assert PINNED_POWER.detectable(72) == pytest.approx(
            (0.02651321756997502, 0.029802435776136182), abs=1e-12
        )

    def test_each_says_what_it_should(self, power) -> None:
        catch, years = power
        assert catch.title == "What eighteen Januaries can catch"
        assert catch.labels == [
            "−0.04",
            "0",
            "0.04",
            "0.08",
            "could pass unseen",
            "0.0547 to 0.0615",
            "caught four times in five",
            "2006: −0.0244",
            "2007: −0.0068",
            "2008: +0.0881",
            "their mean: +0.0190",
            "dots: Chan’s three Januaries, one trade each, after costs",
            "bracket: what the registered run’s 18 Januaries catch, before costs",
        ]
        assert years.title == "More Januaries take more years"
        assert years.labels == [
            "Januaries",
            "X",
            "high",
            "low",
            "18",
            "0.0547 to 0.0615",
            "72",
            "0.0265 to 0.0298",
            "Four times the Januaries, about half the X",
            "one January a year, so 72 Januaries take 72 years",
        ]

    def test_each_label_is_in_the_ink_its_meaning_calls_for(self, power) -> None:
        """Ticks, axes and the run's note are context, so muted. The bracket and
        the marks it is read at are brass. Each of Chan's Januaries takes its
        sign's colour."""
        catch, years = power
        colors = {
            scene.slug: [s.color for s in scene.steps if isinstance(s, Label)] for scene in power
        }
        assert colors[catch.slug] == [
            *[sketches.MUTED] * 4,
            GOOD,
            ACCENT,
            ACCENT,
            LOST,
            LOST,
            GOOD,
            sketches.INK,
            sketches.INK,
            sketches.MUTED,
        ]
        assert colors[years.slug] == [
            sketches.MUTED,
            sketches.MUTED,
            sketches.INK,
            sketches.MUTED,
            *[ACCENT] * 4,
            sketches.INK,
            sketches.MUTED,
        ]

    def test_the_tint_runs_the_same_size_each_side_of_zero(self, power) -> None:
        catch = power[0]
        x_low, x_high = PINNED_POWER.detectable()
        above, below = _fill(catch, "unseen"), _fill(catch, "unseen-below")
        zero = sketches._on_catch(0.0)
        assert (above.x0, above.x1) == pytest.approx((zero, sketches._on_catch(x_low)))
        assert (below.x0, below.x1) == pytest.approx((sketches._on_catch(-x_low), zero))
        assert above.color == below.color == sketches.TINT
        # Over the lower half, so the mark at Chan's mean above zero keeps its own label.
        assert _labelled(catch, "could pass unseen").x == pytest.approx((below.x0 + zero) / 2)
        bracket = _stroke(catch, "caught")
        assert bracket.color == ACCENT
        assert (bracket.x.min(), bracket.x.max()) == pytest.approx(
            (sketches._on_catch(x_low), sketches._on_catch(x_high))
        )

    def test_chans_januaries_sit_at_their_returns_in_their_signs_colour(self, power) -> None:
        catch = power[0]
        for year, r in FiveYearFigures().januaries:
            dot = _stroke(catch, f"chan-{year}")
            assert dot.x[0] == pytest.approx(sketches._on_catch(r))
            assert dot.y[0] == pytest.approx(sketches.CATCH_Y)
            assert dot.color == (GOOD if r > 0 else LOST)
        below = [r for _, r in FiveYearFigures().januaries if r < 0]
        assert all(-PINNED_POWER.detectable()[0] < r < 0 for r in below)

    def test_chans_mean_january_stands_at_the_mean_of_his_three(self, power) -> None:
        """The fair comparison for a detectable average is an average, so the
        sketch marks the mean of Chan's three Januaries, 0.0190, inside the
        tint."""
        chan = FiveYearFigures()
        assert chan.january_mean == pytest.approx(0.0189714446581901, abs=1e-15)
        assert f"{chan.january_mean:.4f}" == "0.0190"
        mark = _stroke(power[0], "chan-mean")
        assert mark.color == sketches.INK
        assert mark.x == pytest.approx(sketches._on_catch(chan.january_mean))
        assert mark.y.min() < sketches.CATCH_Y < mark.y.max()
        assert 0 < chan.january_mean < PINNED_POWER.detectable()[0]

    def test_each_curve_is_its_versions_x_at_every_count(self, power) -> None:
        years = power[1]
        for gid, side in (("low", 0), ("high", 1)):
            curve = _stroke(years, gid)
            counts = range(sketches.POWER_FROM, sketches.POWER_N[1] + 1)
            assert curve.x == pytest.approx([sketches._power_at(k) for k in counts])
            assert curve.y == pytest.approx(
                [sketches._power_up(PINNED_POWER.detectable(k)[side]) for k in counts]
            )
        assert _stroke(years, "low").color == sketches.MUTED
        assert _stroke(years, "high").color == sketches.INK

    def test_each_mark_spans_both_versions_at_its_count(self, power) -> None:
        years = power[1]
        for gid, n in (("now", 18), ("more", 72)):
            mark = _stroke(years, gid)
            low, high = PINNED_POWER.detectable(n)
            assert mark.color == ACCENT
            assert mark.x == pytest.approx(sketches._power_at(n))
            assert (mark.y.min(), mark.y.max()) == pytest.approx(
                (sketches._power_up(low), sketches._power_up(high))
            )

    def test_other_spreads_move_the_count_the_marks_and_the_words(self) -> None:
        catch, years = january_power_scenes(OTHER_POWER)
        assert catch.title == "What twelve Januaries can catch"
        assert "bracket: what the registered run’s 12 Januaries catch, before costs" in catch.labels
        assert _stroke(years, "more").x == pytest.approx(sketches._power_at(48))
        assert "one January a year, so 48 Januaries take 48 years" in years.labels
        low, high = OTHER_POWER.detectable()
        assert f"{low:.4f} to {high:.4f}" in catch.labels

    def test_each_follows_the_paragraph_it_draws(self) -> None:
        paragraphs = [p for p in POST.read_text(encoding="utf-8").split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "A second limit would remain even with every price checked.",
                "Settling the January effect needs more Januaries",
            ),
            POWER_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            embed = paragraphs[index + 1]
            assert re.fullmatch(rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)", embed), name

    def test_each_alt_text_quotes_its_labels_in_drawing_order(self, power) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in power:
            alt = _alt(text, scene)
            places = [alt.find(f"“{label}”") for label in scene.labels]
            assert -1 not in places, [
                w for w, at in zip(scene.labels, places, strict=True) if at < 0
            ]
            assert places == sorted(places), scene.slug
        catch_alt = _alt(text, power[0])
        x_low = PINNED_POWER.detectable()[0]
        ticks = sketches.CATCH_TICKS
        assert (
            f"from below {sketches._signed(ticks[0], 2)} to above {sketches._signed(ticks[-1], 2)}"
            in catch_alt
        )
        assert (
            f"from about {sketches._signed(-x_low, 3)} to about {sketches._signed(x_low, 3)}"
            in catch_alt
        )
        assert "Two red dots sit inside the tint below zero" in catch_alt
        assert "a green dot sits past the bracket" in catch_alt


def _fill(scene, gid):
    return next(f for f in scene.fills if f.gid == gid)


#: Made-up figures for section 3's sketches, so a mark or a word that should
#: follow the run's figures is seen to.
OTHER_IVV = IvvFigures(
    covered=60,
    members=100,
    fewest=("2010-03", 30, 100),
    most=("2011-07", 90, 100),
    departing=(1, 3, 6),
    staying=(2, 2, 6),
    months=(("2010-12", 0.01), ("2011-01", -0.02), ("2011-02", 0.03)),
    mean=0.0066666666666666671,
    detectable=0.09,
)


class TestTheSection3Sketches:
    """Section 3's four sketches: carry-forward, checked prices, leavers, the running sum."""

    def test_they_are_four_in_the_order_the_post_reads_them(self, ivv) -> None:
        assert [gif_name(scene) for scene in ivv] == IVV_GIFS

    def test_each_says_what_it_should(self, ivv) -> None:
        carry, checked, leavers, running = ivv
        assert carry.labels == [
            "quarter-end filings",
            "a company that leaves",
            "leaves the index",
            "still on the list",
            "a company that joins",
            "not yet on the list",
            "each filing’s list stands until the next one",
        ]
        assert checked.labels == [
            "98,321 member-months with a checked price",
            "8,794 dropped",
            "fewest: 364 of 501, 2012-09",
            "most: 501 of 503, 2025-09",
        ]
        assert leavers.labels == [
            "left within a year",
            "long 12.0%",
            "short 16.5%",
            "neither",
            "stayed",
            "long 9.8%",
            "short 9.6%",
            "neither",
            "leavers sit in a traded tenth more often, most of all the short one",
        ]
        assert running.title == "213 months add up to nothing"
        assert running.labels == [
            "0",
            "2009",
            "2026",
            "13% a year, the book’s figure",
            "4.2% a year",
            "the run’s 213 months, added up",
            "a mean of −0.0001 a month: flat, under the 4.2% a year its test could detect",
        ]

    def test_a_change_is_held_until_the_next_filing(self, ivv) -> None:
        """The leaver stays on the list, in red, up to the next filing, and the
        joiner is not on it, in red and dashed, until one."""
        carry = ivv[0]
        held, late = _stroke(carry, "held"), _stroke(carry, "late")
        missed, joined = _stroke(carry, "missed"), _stroke(carry, "joined")
        assert held.x[-1] == late.x[0] == sketches.LEAVES_AT
        assert late.x[-1] == next(f for f in sketches.FILINGS if f > sketches.LEAVES_AT)
        assert missed.x[0] == sketches.JOINS_AT
        assert (
            missed.x[-1]
            == joined.x[0]
            == next(f for f in sketches.FILINGS if f > sketches.JOINS_AT)
        )
        assert (held.color, late.color, missed.color, joined.color) == (
            whiteboard.INK,
            LOST,
            LOST,
            whiteboard.INK,
        )
        assert missed.dashed and not late.dashed
        for k in range(len(sketches.FILINGS)):
            filing = _stroke(carry, f"filing-{k}")
            assert (filing.color, filing.dashed) == (whiteboard.MUTED, True)

    @pytest.mark.parametrize("figures", [PINNED_IVV, OTHER_IVV], ids=["the run's", "other"])
    def test_each_bar_splits_at_its_share(self, figures) -> None:
        checked, leavers = ivv_scenes(figures)[1:3]
        x0, x1 = sketches.BAR_X
        assert _fill(checked, "all-checked").x1 == pytest.approx(
            x0 + (x1 - x0) * figures.covered / figures.members
        )
        for name, (_, covered, members) in (("fewest", figures.fewest), ("most", figures.most)):
            assert _fill(checked, f"{name}-checked").x1 == pytest.approx(
                x0 + (x1 - x0) * covered / members
            )
            assert _fill(checked, f"{name}-dropped").color == LOST
        start = sketches.LEAVERS_X0
        for k, counts in enumerate((figures.departing, figures.staying)):
            total = sum(counts)
            long, short = _fill(leavers, f"long-{k}"), _fill(leavers, f"short-{k}")
            assert long.x1 - long.x0 == pytest.approx((x1 - start) * counts[0] / total)
            assert short.x1 - short.x0 == pytest.approx((x1 - start) * counts[1] / total)
            assert (long.color, short.color) == (GOOD, LOST)
            assert _labelled(leavers, f"long {counts[0] / total:.1%}").color == GOOD
            assert _fill(leavers, f"neither-{k}").color == whiteboard.MUTED
        assert _fill(leavers, "long-0").y0 > _fill(leavers, "long-1").y0, "the leavers sit above"
        assert (_fill(checked, "all-checked").color, _fill(checked, "all-dropped").color) == (
            whiteboard.INK,
            LOST,
        )

    @pytest.mark.parametrize("figures", [PINNED_IVV, OTHER_IVV], ids=["the run's", "other"])
    def test_the_running_sum_adds_up_the_months_to_one_scale(self, figures) -> None:
        running = ivv_scenes(figures)[3]
        values = np.array([value for _, value in figures.months])
        run, book = _stroke(running, "run"), _stroke(running, "book")
        per = (book.y[-1] - book.y[0]) / (sketches.BOOK_ANNUAL / 12 * len(values))
        assert book.y[-1] == pytest.approx(sketches.RUNNING_TOP)
        assert run.y == pytest.approx(
            sketches.RUNNING_ZERO + per * np.concatenate([[0.0], np.cumsum(values)])
        )
        assert (run.color, book.color, book.dashed) == (whiteboard.INK, GOOD, True)
        detect = _stroke(running, "detectable")
        assert detect.y == pytest.approx(
            sketches.RUNNING_ZERO + per * figures.detectable / 12 * np.arange(len(values) + 1)
        )
        assert (detect.color, detect.dashed) == (ACCENT, True)
        assert _labelled(running, f"{100 * figures.detectable:.1f}% a year").y == pytest.approx(
            detect.y[-1]
        )
        first, last = figures.months[0][0][:4], figures.months[-1][0][:4]
        assert running.labels[1:3] == [first, last]
        assert running.title == f"{len(values)} months add up to nothing"

    def test_the_extremes_are_by_share_and_the_months_by_label(self) -> None:
        """The month with the fewest members covered is not the one with the
        lowest share, so a rule reading counts would pick the wrong one."""
        coverage = [
            SimpleNamespace(month="2010-01", covered=50, members=100),
            SimpleNamespace(month="2010-02", covered=45, members=50),
            SimpleNamespace(month="2010-03", covered=60, members=150),
            SimpleNamespace(month="2010-04", covered=99, members=100),
        ]
        monthly = SimpleNamespace(
            covered=254,
            members=400,
            coverage=coverage,
            departures=SimpleNamespace(table=((1, 2, 3), (4, 5, 6))),
            matlab=SimpleNamespace(
                returns=pd.Series(
                    [0.01, -0.02], index=pd.to_datetime(["2010-01-29", "2010-02-26"])
                ),
                test=SimpleNamespace(mean=-0.005),
                x=0.07,
            ),
        )
        figures = IvvFigures.from_run(monthly)
        assert (figures.fewest, figures.most) == (("2010-03", 60, 150), ("2010-04", 99, 100))
        assert figures.months == (("2010-01", 0.01), ("2010-02", -0.02))
        assert (figures.departing, figures.staying) == ((1, 2, 3), (4, 5, 6))

    def test_the_mean_is_the_months_mean(self) -> None:
        values = [value for _, value in PINNED_IVV.months]
        assert float(np.mean(values)) == pytest.approx(PINNED_IVV.mean, abs=1e-15)

    def test_the_leavers_build_slowly(self) -> None:
        assert "ivv_leavers" in sketches.PACED

    def test_each_alt_text_quotes_its_sketchs_words(self, ivv) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in ivv:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label != "0":
                    assert label in alt, (scene.slug, label)
        assert "holds for twelve seconds" in _alt(text, ivv[2])

    def test_a_redraw_with_the_archive_draws_section_3_from_the_ivv_run(
        self, monkeypatch, tmp_path, spans
    ) -> None:
        """Without this, a redraw could draw section 3 without reading the run."""
        monthly, seen = object(), []

        def from_run(run):
            seen.append(run)
            return PINNED_IVV

        def unneeded():
            raise AssertionError("the January run is read though nothing needs it")

        monkeypatch.setattr(seasonals, "run_monthly_point_in_time", lambda: monthly)
        monkeypatch.setattr(seasonals, "run_point_in_time", unneeded)
        monkeypatch.setattr(
            sketches.IvvFigures, "from_run", classmethod(lambda cls, m: from_run(m))
        )
        written = make_equity_seasonals_whiteboards(
            out_dir=tmp_path, spans=spans, verdicts=PINNED, ranges=PINNED_RANGES, power=PINNED_POWER
        )
        assert sorted(path.name for path in written) == sorted(GIFS)
        assert seen == [monthly]


class TestTheSection2Sketches:
    """Section 2's two sketches: the three sources, and the figures before 2002."""

    def test_they_are_two_in_the_order_the_post_reads_them(self, osap) -> None:
        assert [gif_name(scene) for scene in osap] == OSAP_GIFS

    def test_the_committed_release_gives_the_pinned_figures(self) -> None:
        drawn = OsapFigures.from_run(seasonals.run_open_asset_pricing())
        for field in ("printed", "sample", "sample_t", "before", "chan_annual"):
            assert getattr(drawn, field) == pytest.approx(getattr(PINNED_OSAP, field), abs=1e-12), (
                field
            )

    def test_each_says_what_it_should(self, osap) -> None:
        sources, before = osap
        assert sources.labels == [
            "CRSP",
            "Norgate Diamond",
            "Open Source Asset Pricing",
            "keeps the companies that left",
            "reaches back to 1965",
            "can be committed here",
            "runs Chan’s own rule",
            "institutions only",
            "$787.50 a year",
            "free",
            "only Open Source Asset Pricing can be committed, and it cannot run Chan’s rule",
        ]
        assert before.labels == [
            "0",
            "Open Source Asset Pricing:",
            "Heston and Sadka printed",
            "1.15%",
            "1965 to 2002, their sample",
            "1.36%",
            "one standard error each way",
            "1965 to 2001, before Chan’s 2002",
            "1.31%",
            "Chan’s “more than 13%” a year, 1.08% a month",
            "a month, before costs, NYSE and AMEX stocks with the ones that left",
        ]

    def test_each_answer_is_a_green_tick_or_a_red_cross(self, osap) -> None:
        """Only Open Source Asset Pricing can be committed, and only it cannot run Chan's rule."""
        sources = osap[0]
        gids = {stroke.gid for stroke in sources.strokes}
        for r, (_, answers) in enumerate(sketches.SOURCE_QUESTIONS):
            for k, yes in enumerate(answers):
                mark = _stroke(sources, f"mark-{r}-{k}")
                assert mark.color == (GOOD if yes else LOST), (r, k)
                assert (f"mark-{r}-{k}-b" in gids) is (not yes), (r, k)
                assert mark.x.min() == pytest.approx(sketches.SOURCE_COLUMNS[k] - 0.2)
        assert sketches.SOURCE_QUESTIONS == (
            ("keeps the companies that left", (True, True, True)),
            ("reaches back to 1965", (True, True, True)),
            ("can be committed here", (False, False, True)),
            ("runs Chan’s own rule", (True, True, False)),
        )
        crosses = [s for s in sources.strokes if s.gid.endswith("-b")]
        assert len(crosses) == 3
        assert all(stroke.color == LOST for stroke in crosses)

    def test_each_word_is_in_the_ink_its_meaning_calls_for(self, osap) -> None:
        sources, before = osap
        inks = {label.text: label.color for label in sources.steps if isinstance(label, Label)}
        for text in (*sketches.SOURCES, *(q for q, _ in sketches.SOURCE_QUESTIONS)):
            assert inks[text] == whiteboard.INK, text
        for cost in sketches.SOURCE_COSTS:
            assert inks[cost] == whiteboard.MUTED, cost
        assert inks[sources.labels[-1]] == ACCENT
        inks = {label.text: label.color for label in before.steps if isinstance(label, Label)}
        assert inks["0"] == whiteboard.MUTED
        assert inks["one standard error each way"] == whiteboard.MUTED
        assert inks["Open Source Asset Pricing:"] == ACCENT
        assert inks[before.labels[-1]] == ACCENT
        assert inks[before.labels[-2]] == GOOD
        for text in ("Heston and Sadka printed", "1965 to 2002, their sample"):
            assert inks[text] == whiteboard.INK, text

    def test_the_printed_bar_sits_above_the_projects_two(self, osap) -> None:
        """Heston and Sadka's bar on top, then the project's heading and its two bars."""
        before = osap[1]
        middle = {
            gid: (_fill(before, gid).y0 + _fill(before, gid).y1) / 2
            for gid in ("printed", "sample", "prior")
        }
        heading = _labelled(before, "Open Source Asset Pricing:").y
        assert middle["printed"] > heading > middle["sample"] > middle["prior"]
        assert _labelled(before, "Heston and Sadka printed").y == pytest.approx(middle["printed"])
        assert _labelled(before, "1965 to 2002, their sample").y == pytest.approx(middle["sample"])

    @pytest.mark.parametrize(
        "figures",
        [
            PINNED_OSAP,
            OsapFigures(printed=0.01, sample=0.008, sample_t=4.0, before=0.012, chan_annual=0.06),
        ],
        ids=["the run's", "other"],
    )
    def test_each_bar_and_mark_stands_at_its_figure(self, figures) -> None:
        before = osap_scenes(figures)[1]
        per = (sketches.OSAP_X1 - sketches.OSAP_X0) / sketches.OSAP_TOP

        def at(value):
            return sketches.OSAP_X0 + value * per

        for gid, value, colour in (
            ("printed", figures.printed, whiteboard.INK),
            ("sample", figures.sample, ACCENT),
            ("prior", figures.before, ACCENT),
        ):
            bar = _fill(before, gid)
            assert (bar.x0, bar.x1, bar.color) == (
                sketches.OSAP_X0,
                pytest.approx(at(value)),
                colour,
            ), gid
            assert _labelled(before, f"{100 * value:.2f}%").color == colour
        error = _stroke(before, "error")
        assert error.x.min() == pytest.approx(
            at(figures.sample - figures.sample / figures.sample_t)
        )
        assert error.x.max() == pytest.approx(
            at(figures.sample + figures.sample / figures.sample_t)
        )
        chan = _stroke(before, "chan")
        assert chan.x == pytest.approx(np.full(chan.points, at(figures.chan_annual / 12)))
        assert (chan.color, chan.dashed) == (GOOD, True)

    def test_heston_and_sadka_sit_just_outside_one_standard_error(self) -> None:
        """What the post says: about 1.3 standard errors apart, and the sketch draws it."""
        gap = (PINNED_OSAP.sample - PINNED_OSAP.printed) / PINNED_OSAP.error
        assert f"{gap:.1f}" == "1.3"
        assert PINNED_OSAP.printed < PINNED_OSAP.sample - PINNED_OSAP.error
        assert 12 * PINNED_OSAP.before > PINNED_OSAP.chan_annual

    def test_both_build_slowly(self) -> None:
        assert {"osap_sources", "osap_before"} <= set(sketches.PACED)

    def test_each_alt_text_quotes_its_sketchs_words(self, osap) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in osap:
            alt = _alt(text, scene)
            for label in scene.labels:
                if label != "0":
                    assert label in alt, (scene.slug, label)
            assert "drawn slowly stroke by stroke" in alt, scene.slug
            assert "holds for twelve seconds" in alt, scene.slug

    def test_each_alt_text_says_what_the_drawing_shows(self, osap) -> None:
        """Each claim the alt text makes about ink or place, held against the scene."""
        sources, before = osap
        text = POST.read_text(encoding="utf-8")
        alt = _alt(text, sources)
        rows = dict(sketches.SOURCE_QUESTIONS)
        assert "Green ticks fill the first two rows for all three." in alt
        assert all(rows["keeps the companies that left"]) and all(rows["reaches back to 1965"])
        assert _stroke(sources, "mark-0-0").color == GOOD
        alt = _alt(text, before)
        assert "a black bar for “Heston and Sadka printed”" in alt
        assert "a brown bar for “1965 to 2002, their sample”" in alt
        assert "A second brown bar, “1965 to 2001, before Chan’s 2002”" in alt
        assert [_fill(before, gid).color for gid in ("printed", "sample", "prior")] == [
            whiteboard.INK,
            ACCENT,
            ACCENT,
        ]
        assert "which stops just short of 1.15" in alt
        assert PINNED_OSAP.sample - PINNED_OSAP.error > PINNED_OSAP.printed
        assert "past a green dashed mark" in alt
        chan = _stroke(before, "chan")
        assert (chan.color, chan.dashed) == (GOOD, True)
        assert _fill(before, "prior").x1 > chan.x.max()

    def test_each_follows_its_paragraph(self) -> None:
        text = POST.read_text(encoding="utf-8")
        start = text.index("### Whether Heston and Sadka’s effect existed before 2002")
        end = text.index("\n### ", start + 1)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "Every result in this post is computed from data published",
                "This repository has since read the free source.",
            ),
            OSAP_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)",
                paragraphs[index + 1].strip(),
            ), name


#: What :class:`Shift` gives for the IVV run's 213 months, the values
#: ``test_how_the_4_2_percent_is_derived`` in ``tests/test_equity_seasonals.py``
#: pins.
PINNED_SHIFT = Shift(
    df=212, critical=1.6520729200438098, shift=2.494447174535743, z=0.8416212335729143
)

#: A made-up run of 30 months, so the labels have to follow the figures.
SHORT = dataclasses.replace(PINNED_IVV, months=PINNED_IVV.months[:30])


class TestTheDeltaSketches:
    """The three sketches under "Where the 4.2 percent comes from"."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, delta) -> None:
        assert [gif_name(scene) for scene in delta] == DELTA_GIFS

    def test_the_test_gives_the_pinned_figures(self) -> None:
        drawn = Shift.of(PINNED_IVV)
        assert drawn.df == PINNED_SHIFT.df
        for field in ("critical", "shift", "z"):
            assert getattr(drawn, field) == pytest.approx(getattr(PINNED_SHIFT, field), abs=1e-9)

    def test_each_says_what_it_should(self, delta) -> None:
        scatter, shortcut, bracket = delta
        assert scatter.labels == [
            "true mean 0",
            "1.652, the 5% bar",
            "clears it 5% of the time",
            "true mean X",
            "δ = 2.494",
            "clears it 80% of the time",
        ]
        assert shortcut.labels == [
            "centre = 1.652 + 0.842 = 2.494",
            "1.652, the bar",
            "20% miss",
            "80% clear it",
            "0.842",
            "0.842 is the normal curve’s 80th percentile, so 80% of it lies above 0.842 "
            "below the centre",
        ]
        assert bracket.labels == [
            "chance of",
            "clearing 1.652",
            "δ",
            "drawn from 0 to 5, the solver starts at 50",
            "0.05",
            "0.80",
            "narrowed from 50",
            "keeps the upper half",
            "then jumps close",
            "δ = 2.494",
            "each bracket keeps the part where the curve crosses 0.80",
        ]

    def test_the_labels_follow_the_figures(self) -> None:
        """Fewer months move the critical value and δ, and the words move with them."""
        s = Shift.of(SHORT)
        assert s.df == 29 and s.critical > PINNED_SHIFT.critical and s.shift > PINNED_SHIFT.shift
        scatter, shortcut, bracket = delta_scenes(SHORT)
        assert f"{s.critical:.3f}, the 5% bar" in scatter.labels
        assert f"δ = {s.shift:.3f}" in scatter.labels and f"δ = {s.shift:.3f}" in bracket.labels
        assert f"centre = {s.critical:.3f} + 0.842 = {s.critical + s.z:.3f}" in shortcut.labels
        assert f"clearing {s.critical:.3f}" in bracket.labels

    def test_each_mark_is_in_the_ink_its_meaning_calls_for(self, delta) -> None:
        scatter, shortcut, bracket = delta
        for scene, gid, ink, dashed in (
            (scatter, "null", whiteboard.MUTED, False),
            (scatter, "bar", LOST, True),
            (scatter, "null-tail", LOST, False),
            (scatter, "moved", ACCENT, False),
            (scatter, "moved-tail", GOOD, False),
            (scatter, "shift", whiteboard.INK, False),
            (shortcut, "curve", ACCENT, False),
            (shortcut, "centre", ACCENT, True),
            (shortcut, "bar", LOST, True),
            (shortcut, "miss", LOST, False),
            (shortcut, "clear", GOOD, False),
            (shortcut, "gap", whiteboard.INK, False),
            (bracket, "power", whiteboard.INK, False),
            (bracket, "target", ACCENT, True),
            (bracket, "found", ACCENT, True),
        ):
            stroke = _stroke(scene, gid)
            assert (stroke.color, stroke.dashed) == (ink, dashed), (scene.slug, gid)
        spans = [s for s in bracket.strokes if s.gid.startswith("bracket-")]
        assert [s.color for s in spans] == [whiteboard.MUTED, whiteboard.MUTED, ACCENT]
        for scene, text, ink in (
            (scatter, "1.652, the 5% bar", LOST),
            (scatter, "clears it 5% of the time", LOST),
            (scatter, "true mean X", ACCENT),
            (scatter, "clears it 80% of the time", GOOD),
            (shortcut, "1.652, the bar", LOST),
            (shortcut, "20% miss", LOST),
            (shortcut, "80% clear it", GOOD),
            (shortcut, "centre = 1.652 + 0.842 = 2.494", ACCENT),
            (bracket, "0.80", ACCENT),
            (bracket, "δ = 2.494", ACCENT),
        ):
            assert _labelled(scene, text).color == ink, (scene.slug, text)

    @pytest.mark.parametrize("figures", [PINNED_IVV, SHORT], ids=["the run's", "made up"])
    def test_the_scatter_stands_at_its_figures(self, figures) -> None:
        s = Shift.of(figures)
        scatter = delta_scenes(figures)[0]
        at = sketches._scatter_at
        bar = _stroke(scatter, "bar")
        assert bar.x == pytest.approx(np.full(bar.points, at(s.critical)))
        for tail in ("null-tail", "moved-tail"):
            assert _stroke(scatter, tail).x.min() == pytest.approx(at(s.critical)), tail
        arrow = _stroke(scatter, "shift")
        assert (arrow.x.min(), arrow.x.max()) == (
            pytest.approx(at(0.0)),
            pytest.approx(at(s.shift)),
        )
        null = _stroke(scatter, "null")
        assert null.x[np.argmax(null.y)] == pytest.approx(at(0.0), abs=0.05)
        assert _stroke(scatter, "moved").y.max() < sketches.SCATTER_UPPER

    @pytest.mark.parametrize("figures", [PINNED_IVV, SHORT], ids=["the run's", "made up"])
    def test_the_shortcut_centres_its_curve_past_the_bar(self, figures) -> None:
        s = Shift.of(figures)
        shortcut = delta_scenes(figures)[1]
        at = sketches._shortcut_at
        centre = _stroke(shortcut, "centre")
        assert centre.x == pytest.approx(np.full(centre.points, at(s.critical + s.z)))
        curve = _stroke(shortcut, "curve")
        assert curve.x[np.argmax(curve.y)] == pytest.approx(at(s.critical + s.z), abs=0.05)
        gap = _stroke(shortcut, "gap")
        assert (gap.x.min(), gap.x.max()) == (
            pytest.approx(at(s.critical)),
            pytest.approx(at(s.critical + s.z)),
        )
        assert _stroke(shortcut, "miss").x.max() == pytest.approx(at(s.critical))
        assert _stroke(shortcut, "clear").x.min() == pytest.approx(at(s.critical))

    @pytest.mark.parametrize("figures", [PINNED_IVV, SHORT], ids=["the run's", "made up"])
    def test_the_brackets_are_the_solvers_own(self, figures) -> None:
        """The three rows are the first three brackets the solver holds inside
        δ from 0 to 5, each inside the last and each around δ."""
        s = Shift.of(figures)
        bracket = delta_scenes(figures)[2]
        at, up = sketches._bracket_at, sketches._bracket_up
        spans = [
            (st.x.min(), st.x.max()) for st in bracket.strokes if st.gid.startswith("bracket-")
        ]
        every = seasonals.shift_brackets(s.df + 1)
        first = next(k for k, (_, high) in enumerate(every) if high <= 5.0)
        assert first == 0 or every[first - 1][1] > 5.0
        for (x0, x1), (low, high) in zip(spans, every[first : first + 3], strict=True):
            assert (x0, x1) == (pytest.approx(at(low)), pytest.approx(at(high)))
        for (a0, b0), (a1, b1) in zip(spans, spans[1:], strict=False):
            assert a0 <= a1 + 1e-9 and b1 <= b0 + 1e-9
        assert all(a <= at(s.shift) <= b for a, b in spans)
        found = _stroke(bracket, "found")
        assert found.x == pytest.approx(np.full(found.points, at(s.shift)))
        target = _stroke(bracket, "target")
        assert target.y == pytest.approx(np.full(target.points, up(0.8)))
        power = _stroke(bracket, "power")
        assert power.y[0] == pytest.approx(up(0.05), abs=0.01)
        crossing = np.interp(up(0.8), power.y, power.x)
        assert crossing == pytest.approx(at(s.shift), abs=0.02)

    def test_the_rows_say_what_the_solver_did(self) -> None:
        """For the run's 213 months it narrows down from 50, keeps the upper
        half once, then jumps close, and the words come from the brackets."""
        every = seasonals.shift_brackets(213)
        widths = [high - low for low, high in every[:4]]
        ratios = [b / a for a, b in zip(widths, widths[1:], strict=False)]
        assert ratios == pytest.approx([0.5, 0.5, 0.5])
        assert every[3] == pytest.approx((0.0, 4.934210526315789))
        assert every[4][0] > every[3][0] and every[4][1] == every[3][1]
        assert every[5][1] - every[5][0] < (every[4][1] - every[4][0]) / 10
        shown, words = sketches._brackets(213)
        assert shown == every[3:6]
        assert words == ["narrowed from 50", "keeps the upper half", "then jumps close"]

    def test_the_shading_and_curves_hold_their_shape(self, delta) -> None:
        """The shortcut's curve has a spread of 1, its two shadings cover the
        curve from end to end on each side of the bar, and every shading is
        upright strokes joined along the base or the curve, never diagonals.
        The moved scatter peaks near δ."""
        scatter, shortcut, bracket = delta
        s = PINNED_SHIFT
        at = sketches._shortcut_at
        centre = s.critical + s.z
        curve = _stroke(shortcut, "curve")
        base, height = sketches.SHORTCUT_BASE, sketches.SHORTCUT_HEIGHT
        one_off = np.interp(at(centre + 1.0), curve.x, curve.y)
        assert one_off == pytest.approx(base + height * math.exp(-0.5), abs=0.01)
        miss, clear = _stroke(shortcut, "miss"), _stroke(shortcut, "clear")
        assert miss.x.min() == pytest.approx(at(sketches.SHORTCUT_T[0] + 0.05))
        assert clear.x.max() == pytest.approx(at(sketches.SHORTCUT_T[1] - 0.05))
        for scene, gid in (
            (scatter, "null-tail"),
            (scatter, "moved-tail"),
            (shortcut, "miss"),
            (shortcut, "clear"),
        ):
            shade = _stroke(scene, gid)
            dx, dy = np.diff(shade.x), np.diff(shade.y)
            sideways = np.abs(dx) > 1e-9
            slopes = np.abs(dy[sideways] / dx[sideways])
            assert slopes.max() < 3, (scene.slug, gid)
        moved = _stroke(scatter, "moved")
        assert moved.x[np.argmax(moved.y)] == pytest.approx(sketches._scatter_at(s.shift), abs=0.1)

    def test_the_brackets_narrow_downward_and_the_line_reaches_the_last(self, delta) -> None:
        bracket = delta[2]
        rows = [st.y.mean() for st in bracket.strokes if st.gid.startswith("bracket-")]
        assert rows == pytest.approx(list(sketches.BRACKET_ROWS))
        assert rows == sorted(rows, reverse=True)
        assert rows[0] < sketches._bracket_up(0.0)
        found = _stroke(bracket, "found")
        assert found.y.min() == pytest.approx(sketches.BRACKET_ROWS[-1] - 0.12)
        assert found.y.max() == pytest.approx(sketches._bracket_up(0.8))

    def test_all_three_build_slowly_and_need_the_archive(self) -> None:
        slugs = {"delta_scatter", "delta_shortcut", "delta_bracket"}
        assert slugs <= set(sketches.PACED)
        assert slugs <= set(sketches.ARCHIVE_SLUGS)

    def test_each_alt_text_quotes_its_words_and_its_pace(self, delta) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in delta:
            alt = _alt(text, scene)
            for label in scene.labels:
                assert f"“{label}”" in alt, (scene.slug, label)
            assert "drawn slowly stroke by stroke" in alt, scene.slug
            assert "holds for twelve seconds" in alt, scene.slug

    def test_each_alt_text_says_what_the_drawing_shows(self, delta) -> None:
        scatter, shortcut, bracket = delta
        text = POST.read_text(encoding="utf-8")
        alt = _alt(text, scatter)
        assert "a grey scatter" in alt and _stroke(scatter, "null").color == whiteboard.MUTED
        assert "a red dashed line marks “1.652, the 5% bar”" in alt
        assert "the thin tail past the line is shaded red" in alt
        assert "slid right by an arrow labelled “δ = 2.494”" in alt
        assert "its larger part past the line is shaded green" in alt and "in brown" in alt
        assert "A red dashed line marks “1.652, the bar”" in _alt(text, shortcut)
        assert _stroke(shortcut, "bar").color == LOST
        alt = _alt(text, shortcut)
        assert "A brown normal curve" in alt and "A black bracket" in alt
        assert _stroke(shortcut, "gap").color == whiteboard.INK
        alt = _alt(text, bracket)
        assert "A black curve" in alt and "a brown dashed line" in alt
        assert "three brackets" in alt and len(sketches.BRACKET_ROWS) == 3
        assert "the last is brown" in alt

    def test_each_follows_what_it_draws(self) -> None:
        text = POST.read_text(encoding="utf-8")
        start = text.index("##### Where the 4.2 percent comes from")
        end = text.index("\n#### ", start)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for opening, name in zip(
            (
                "The test calls a mean above zero when its t-statistic clears",
                "```math\n\\begin{aligned}\n\\text{clears the bar:}",
                "The chance of clearing 1.652 rises as δ grows.",
            ),
            DELTA_GIFS,
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)",
                paragraphs[index + 1].strip(),
            ), name


#: What :class:`Broad` gives from the committed Open Source Asset Pricing
#: release 202510, ``MomSeasonShort`` long-short, 1965-01 to 2001-12 and
#: 2002-01 to 2024-12. Entry 52 of the replication log carries the means and ts.
PINNED_BROAD = Broad(
    before=0.013133990629309849,
    before_error=0.013133990629309849 / 8.280547072932409,
    after=0.0012242855992733068,
    after_error=0.0012242855992733068 / 0.5042545079355029,
    first=1965,
    split=2002,
    last=2024,
)


class TestTheBroaderSeriesSketches:
    """The three under "What a broader series shows"."""

    def test_they_are_three_in_the_order_the_post_reads_them(self, broad) -> None:
        assert [gif_name(scene) for scene in broad] == BROAD_GIFS

    def test_the_release_gives_the_pinned_figures(self, project) -> None:
        drawn = Broad.from_run(project)
        assert (drawn.first, drawn.split, drawn.last) == (1965, 2002, 2024)
        for field in ("before", "before_error", "after", "after_error"):
            assert getattr(drawn, field) == pytest.approx(getattr(PINNED_BROAD, field), abs=1e-12)

    def test_the_scatter_holds_the_192_months_entry_52_compares(self, project) -> None:
        together = Together.from_runs(PINNED_IVV, project)
        assert len(together.months) == 192
        assert (together.months[0][0], together.months[-1][0]) == ("2009-01", "2024-12")
        assert together.correlation == pytest.approx(0.5915365787192671, abs=1e-12)
        theirs = np.array([m[1] for m in together.months])
        ours = np.array([m[2] for m in together.months])
        assert np.abs(theirs).max() < sketches.TOGETHER_LIMITS[0]
        assert np.abs(ours).max() < sketches.TOGETHER_LIMITS[1]

    def test_each_says_what_it_should(self, broad) -> None:
        before_after, together, running = broad
        assert running.labels == [
            "0",
            "2009",
            "2024",
            "Open Source Asset Pricing’s series",
            "the IVV run",
            "both added up, neither halved",
        ]
        assert before_after.labels == [
            "0",
            "1965 to 2001",
            "1.31%",
            "2002 to 2024",
            "0.12%",
            "one standard error each way",
            "Open Source Asset Pricing, a month before costs, "
            "NYSE and AMEX with the ones that left",
        ]
        assert together.labels == [
            "Open Source Asset Pricing’s month",
            "the IVV run’s month",
            "192 months,",
            "2009 to 2024",
            "correlation 0.59",
            "they rise and fall together",
        ]
        assert before_after.title == "Before 2002 and after"

    def test_each_mark_is_in_the_ink_its_meaning_calls_for(self, broad) -> None:
        before_after, together, running = broad
        assert _stroke(running, "theirs").color == ACCENT
        assert _stroke(running, "ours").color == whiteboard.INK
        assert _stroke(running, "zero").color == whiteboard.MUTED
        assert _labelled(running, "Open Source Asset Pricing’s series").color == ACCENT
        assert [_fill(before_after, gid).color for gid in ("before", "after")] == [ACCENT, ACCENT]
        for gid in ("before-error", "after-error", "zero"):
            ink = whiteboard.MUTED if gid == "zero" else whiteboard.INK
            assert _stroke(before_after, gid).color == ink, gid
        assert _labelled(before_after, "1.31%").color == ACCENT
        assert _labelled(before_after, "0.12%").color == ACCENT
        months = _stroke(together, "months")
        assert (months.color, months.dots > 0) == (whiteboard.INK, True)
        assert _labelled(together, "correlation 0.59").color == GOOD
        assert _labelled(together, "Open Source Asset Pricing’s month").color == ACCENT

    @pytest.mark.parametrize(
        "figures",
        [
            PINNED_BROAD,
            Broad(
                before=0.006,
                before_error=0.002,
                after=-0.002,
                after_error=0.001,
                first=1970,
                split=2002,
                last=2020,
            ),
        ],
        ids=["the release's", "made up"],
    )
    def test_each_bar_and_bracket_stands_at_its_figure(self, figures) -> None:
        scene = sketches._broad_before_after(figures)
        at = sketches._broad_at
        zero = at(0.0)
        for gid, mean, error in (
            ("before", figures.before, figures.before_error),
            ("after", figures.after, figures.after_error),
        ):
            bar = _fill(scene, gid)
            assert (bar.x0, bar.x1) == (pytest.approx(zero), pytest.approx(at(mean))), gid
            span = _stroke(scene, f"{gid}-error")
            assert (span.x.min(), span.x.max()) == (
                pytest.approx(at(mean - error)),
                pytest.approx(at(mean + error)),
            ), gid
            assert _labelled(scene, f"{100 * mean:.2f}%").color == ACCENT
        assert f"{figures.first} to {figures.split - 1}" in scene.labels
        assert f"{figures.split} to {figures.last}" in scene.labels

    def test_the_earlier_years_sit_above_the_later(self, broad) -> None:
        before_after = broad[0]
        assert _labelled(before_after, "1965 to 2001").y > _labelled(before_after, "2002 to 2024").y
        assert _fill(before_after, "before").y0 > _fill(before_after, "after").y1

    def test_the_after_bracket_crosses_zero_and_the_before_one_does_not(self) -> None:
        """What the alt text says, held on the release's figures."""
        b = PINNED_BROAD
        assert b.after - b.after_error < 0 < b.after + b.after_error
        assert b.before - b.before_error > 0

    def test_each_dot_stands_at_its_month(self, broad, project) -> None:
        together = Together.from_runs(PINNED_IVV, project)
        months = _stroke(broad[1], "months")
        xs, ys = sketches._together_at(
            np.array([m[1] for m in together.months]), np.array([m[2] for m in together.months])
        )
        assert months.x == pytest.approx(xs)
        assert months.y == pytest.approx(ys)
        cx, cy = sketches.TOGETHER_CENTRE
        assert sketches._together_at(0.0, 0.0) == (pytest.approx(cx), pytest.approx(cy))
        (lx, ly), (rx, ry) = sketches.TOGETHER_LIMITS, sketches.TOGETHER_REACH
        theirs_all = np.array([m[1] for m in together.months])
        ours_all = np.array([m[2] for m in together.months])
        assert months.x == pytest.approx(cx + theirs_all * rx / lx), (
            "across is the project, to its own limit"
        )
        assert months.y == pytest.approx(cy + ours_all * ry / ly), "up is the run, to its own limit"
        theirs = np.array([m[1] for m in together.months])
        ours = np.array([m[2] for m in together.months])
        assert np.argmax(months.x) == np.argmax(theirs), "the project's best month is rightmost"
        assert np.argmax(months.y) == np.argmax(ours), "the IVV run's best month is highest"
        assert np.argmin(months.x) == np.argmin(theirs)
        assert np.argmin(months.y) == np.argmin(ours)

    def test_the_running_sums_add_up_each_series_unhalved(self, broad, project) -> None:
        """Each line is its series' running sum at one vertical scale, inside
        the scale's ends, with the project's ending above zero and the run's
        below, as the alt text says."""
        together = Together.from_runs(PINNED_IVV, project)
        theirs = np.concatenate([[0.0], np.cumsum([m[1] for m in together.months])])
        ours = np.concatenate([[0.0], np.cumsum([m[2] for m in together.months])])
        running = broad[2]
        up = sketches._running_sums_up
        assert _stroke(running, "theirs").y == pytest.approx(up(theirs))
        assert _stroke(running, "ours").y == pytest.approx(up(ours))
        x0, x1 = sketches.RUNNING_SUMS_X
        for line in ("theirs", "ours"):
            stroke = _stroke(running, line)
            assert (stroke.x[0], stroke.x[-1]) == (pytest.approx(x0), pytest.approx(x1))
        assert up(0.0) == pytest.approx(sketches.RUNNING_SUMS_ZERO)
        low, high = sketches.RUNNING_SUMS_LOW, sketches.RUNNING_SUMS_HIGH
        assert low < min(theirs.min(), ours.min()) and max(theirs.max(), ours.max()) < high
        assert theirs[-1] > 0 > ours[-1]
        months = np.array([(m[1], m[2]) for m in together.months])
        spread = months[:, 0].std(ddof=1) / months[:, 1].std(ddof=1)
        assert 1.8 < spread < 2.5, "the project's months swing about twice as far"
        assert abs(theirs.min() - ours.min()) < 0.05, "both reach about the same low"
        assert up(high) == pytest.approx(sketches.RUNNING_SUMS_TOP)
        x0, x1 = sketches.RUNNING_SUMS_X
        assert _labelled(running, "2009").x == pytest.approx(x0)
        assert _labelled(running, "2024").x == pytest.approx(x1)

    def test_all_build_slowly_and_two_need_the_archive(self) -> None:
        slugs = {"broad_before_after", "broad_together", "broad_running"}
        assert slugs <= set(sketches.PACED)
        assert {"broad_together", "broad_running"} <= set(sketches.ARCHIVE_SLUGS)
        assert "broad_before_after" not in sketches.ARCHIVE_SLUGS

    def test_each_alt_text_quotes_its_words_and_says_what_it_shows(self, broad) -> None:
        text = POST.read_text(encoding="utf-8")
        for scene in broad:
            alt = _alt(text, scene)
            for label in scene.labels:
                assert f"“{label}”" in alt, (scene.slug, label)
            assert "drawn slowly stroke by stroke" in alt and "holds for twelve seconds" in alt
        alt = _alt(text, broad[0])
        assert "its bracket crosses zero" in alt and "far from zero" in alt
        assert (
            "A long brown bar for “1965 to 2001”" in alt
            and "A short brown bar for “2002 to 2024”" in alt
        )
        assert "black bracket" in alt
        alt = _alt(text, broad[1])
        assert "tilts up to the right" in alt and "in green" in alt
        assert "Two grey axes cross" in alt
        alt = _alt(text, broad[2])
        assert "A brown line" in alt and "A black line" in alt
        assert "ends above it" in alt and "ends below zero" in alt
        assert "climbs well above it in the middle years" in alt
        assert "falls back below it in 2021, climbs back above it late in 2022" in alt
        assert "reaches about the same low" in alt

    def test_each_follows_its_paragraph(self) -> None:
        text = POST.read_text(encoding="utf-8")
        start = text.index("#### What a broader series shows")
        end = text.index("\n## ", start)
        paragraphs = [p for p in text[start:end].split("\n\n") if p.strip()]
        for opening, name in zip(
            ("A broader series agrees with the IVV run.", "Over the 192 months"),
            BROAD_GIFS[:2],
            strict=True,
        ):
            (index,) = [k for k, p in enumerate(paragraphs) if p.startswith(opening)]
            assert re.fullmatch(
                rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(name)}\)",
                paragraphs[index + 1].strip(),
            ), name
        (index,) = [k for k, p in enumerate(paragraphs) if p.startswith("Month to month,")]
        assert BROAD_GIFS[1] in paragraphs[index - 1]
        assert re.fullmatch(
            rf"!\[[^\]]+\]\(\.\./docs/figures/{re.escape(BROAD_GIFS[2])}\)",
            paragraphs[index + 1].strip(),
        )


@pytest.mark.parametrize("group", ["delta", "broad"])
def test_each_alt_text_quotes_its_labels_in_drawing_order(group, request) -> None:
    """The alt text follows the order the frames show, so each quoted label
    first appears after the one drawn before it."""
    text = POST.read_text(encoding="utf-8")
    for scene in request.getfixturevalue(group):
        alt = _alt(text, scene)
        places = [alt.index(f"“{label}”") for label in scene.labels]
        assert places == sorted(places), (scene.slug, scene.labels)


def test_every_alt_text_quotes_the_labels_it_names_in_drawing_order(every) -> None:
    """Every sketch's alt text follows the frames. A label the alt text leaves
    unquoted, such as an axis tick, is allowed, but each one it quotes comes
    after the one drawn before it. A label drawn twice, such as "0" on two
    number lines, is found again further along when the alt text quotes it
    twice, and once is enough when the alt text quotes it once."""
    text = POST.read_text(encoding="utf-8")
    for scene in every:
        alt, at, seen = _alt(text, scene), 0, set()
        for label in scene.labels:
            quoted = f"“{label}”"
            found = alt.find(quoted, at)
            if found < 0 and (label in seen or quoted not in alt):
                continue
            assert found >= 0, (scene.slug, label, "quoted before an earlier label")
            at, seen = found + len(quoted), seen | {label}


def _minus(value: float, places: int) -> str:
    return f"{value:.{places}f}".replace("-", "−")


def test_the_post_quotes_the_pinned_figures() -> None:
    """The post's body quotes these figures, and each comes from a pin that a
    test elsewhere holds the run or Chan's files give. So a typo in the post,
    or a re-pin the post was not moved with, fails here rather than reaching a
    reader. Each fragment carries enough words to say which figure it is."""
    p, ivv, shift, osap, broad = PINNED, PINNED_IVV, PINNED_SHIFT, PINNED_OSAP, PINNED_BROAD
    f, (x_low, x_high) = FiveYearFigures(), PINNED_POWER.detectable()
    fragments = [
        f"averages between {_minus(p.january_low, 4)} and {_minus(p.january_high, 4)}"
        " a January before costs",
        f"The low series averages {_minus(p.january_low, 4)} a January before costs",
        f"The high series averages {_minus(p.january_high, 4)}, with",
        f"The {len(ivv.months)} months average {_minus(p.monthly_mean, 4)} a month before costs",
        f"no return detectable above about {100 * p.detectable:.1f} percent a year",
        f"a checked price for {ivv.covered:,} of its {ivv.members:,} member-months",
        f"its t-statistic clears {shift.critical:.3f}",
        f"The normal-curve shortcut gives {shift.critical + shift.z:.4f}"
        f" and the exact answer {shift.shift:.4f}",
        f"land above −{shift.z:.3f}",
        f"it earned {100 * osap.sample:.2f} percent a month before costs,"
        f" where they printed {100 * osap.printed:.2f} percent."
        f" Its t-statistic of {osap.sample_t:.2f}",
        f"it earned {100 * osap.before:.2f} percent a month,"
        f" about {1200 * osap.before:.1f} percent a year",
        f"earned {100 * broad.after:.2f} percent a month,"
        f" with a t-statistic of {broad.after / broad.after_error:.2f}",
        f"The two halves’ annual returns, {_minus(f.before_2002, 6)} and {_minus(f.from_2002, 6)}",
        f"the rerun keeps {f.rerun_months} months",
        f"returns {_minus(f.rerun_matlab, 4)} a year"
        f" against the whole period’s {_minus(f.whole_matlab, 4)}",
        f"the figures are {_minus(f.rerun_python, 6)} and {_minus(f.whole_python, 6)}",
        f"those {f.between_months} return {_minus(f.between, 6)} a year",
        f"The gap between the two figures is {abs(f.rerun_matlab - f.whole_matlab):.4f}"
        f" a year, and the rerun’s annual return has a standard error of {f.rerun_error:.4f}",
        f"is {x_low:.4f} for the low version and {x_high:.4f} for the high one,"
        f" a gain of about {100 * x_low:.1f} to {100 * x_high:.1f} percent",
        f"and so is their mean, {f.january_mean:.4f}",
    ]
    text = POST.read_text(encoding="utf-8")
    assert [fragment for fragment in fragments if fragment not in text] == []


def test_every_section_the_post_points_to_is_a_heading() -> None:
    """The post's prose sends a reader to a section by name, quoted after
    "under" or in italics after "section". A renamed heading would leave the
    pointer naming nothing, so each name must match a heading. Alt texts quote
    sketch labels after "under" too, so they are left out."""
    text = POST.read_text(encoding="utf-8")
    headings = {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}
    prose = "\n\n".join(p for p in text.split("\n\n") if not p.startswith("!["))
    named = re.findall(r"under “([^”]+)”", prose) + re.findall(r"section, \*([^*]+)\*", prose)
    assert len(named) >= 2, named
    assert [name for name in named if name not in headings] == []


def test_the_broader_series_sentence_says_what_the_months_show(project) -> None:
    """The post's "about twice as far" is the months' spread, which the run and
    the release give, and the sentence names the months."""
    text = POST.read_text(encoding="utf-8")
    assert (
        "Month to month, Open Source Asset Pricing’s series swings"
        " about twice as far as the IVV run’s." in text
    )
    together = Together.from_runs(PINNED_IVV, project)
    months = np.array([(m[1], m[2]) for m in together.months])
    ratio = months[:, 0].std(ddof=1) / months[:, 1].std(ddof=1)
    assert f"{ratio:.1f}" == "2.1"
