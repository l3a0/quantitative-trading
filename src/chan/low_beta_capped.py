"""Chan's low-beta leverage rule at leverage a broker would lend, on his S&P 500 file. Exploratory.

[Issue 275](https://github.com/l3a0/quantitative-trading/issues/275) levered
the low-beta fifth of Chan's S&P 500 file to the high-beta fifth's beta, as
location 4684 of the revised edition matches them, and the levered portfolio
lost more than its capital in June 2001 at a leverage of 58.0262. That
verdict is about the leverage the beta match asks for. Location 4709 says only
"highly leveraged", so the question left open is whether the rule holds at a
leverage a broker would lend.
[Issue 516](https://github.com/l3a0/quantitative-trading/issues/516) asks it,
and its plan, written on 2026-10-11 before any capped number existed, fixes
every rule below.

**The result is exploratory, and nothing here confirms anything.** Entry 45's
calendar, its leverage path, the ruin, eight months of both groups' returns
and its side figures had been seen before either ceiling was chosen. The plan
lists the five things.

1. The calendar: 2,011 shared days, 96 month-ends, and 83 holding months from
   December 2000 to October 2007.
2. The beta match's leverage k, its mean, its minimum and its maximum.
3. The two ruined months at the beta match, June and September 2001, with
   their k, and June 2001's unlevered low return.
4. Both groups' unlevered returns for the eight formations from 2000-11-30 to
   2001-06-29, which make any capped return for those months arithmetic.
5. Entry 45's side figures: both fifths' Sharpe ratios, the realised growth of
   the low fifth, the high fifth and SPY, both fifths' realised betas, and the
   low fifth's full-sample Kelly leverage.

The unlevered low fifth already out-compounded the high fifth, and growth
rises with leverage up to the Kelly leverage under a Gaussian approximation,
so both ceilings were expected to show a positive point estimate. What the run
can add is whether either gap is distinguishable from noise once the
fat-tailed months are in, and whether any month at a ceiling of 5 comes near
ruin.

**The construction.** :func:`chan.low_beta_leverage.read_sources` and
:func:`chan.low_beta_leverage.build_portfolios` run unchanged, so the
universe, the calendar, the betas, the fifths, the weights, k and the bill
rate are Entry 45's, and so is the decision to refuse no window across a
scale break. At each formation the low fifth is levered by
L = min(k, C), the beta match capped at a ceiling C, and the capped month
returns rf + L × (r_low − rf). Borrowing costs the bill rate, and no trading
cost is charged. Two ceilings are tried, and both come from Chan's text.

1. **C = 2.** Location 814 says "interday (overnight) positions allow only a
   leverage of 2" under Regulation T, and location 2836 restricts a retail
   account to 2 overnight. k never falls below 2 on this panel, so this
   ceiling is a constant leverage of 2.
2. **C = 5.** Location 814's portfolio margin "may require only 20 percent or
   less of overnight margin", a leverage of 5. That is the highest leverage
   the book puts a number on for stocks held overnight, and its "or less"
   leaves room for more.

A :class:`chan.low_beta_leverage.Portfolios` whose ``levered`` and ``leverage``
are both replaced carries each ceiling, so
:func:`chan.low_beta_leverage.ruined_months` names the capped leverage and
:func:`chan.low_beta_leverage.differences` reads the capped return.

**The statistic** is the Newey-West t of d = ln(1 + r_capped) − ln(1 + r_high)
over the 83 months, from :func:`ithildincore.stats.newey_west_summary` at its
default lag. Twelve times the mean of d is the gap in realised compounded
growth a year.

**The control** is Benjamini-Hochberg at q = 0.05 across the two ceilings,
with :func:`chan.pca_factor_momentum.one_sided_p` and
:func:`chan.pca_factor_momentum.benjamini_hochberg` unchanged. It runs twice.

1. Once on the claim's direction, p = one_sided_p(t).
2. Once on the contrary direction, p = one_sided_p(−t).

A ruined ceiling enters both families with a p-value of 1, so it can never
help the other ceiling pass.

**The four outcomes**, each worded on the issue before any number:

1. **Contradicted by ruin** when any month's capped return is −1 or below.
   Neither t nor Y is computed.
2. **Holds** when the mean of d is above 0 and the claim's family rejects.
3. **Contradicted** when the mean of d is below 0 and the contrary family
   rejects.
4. **Not decided** otherwise, with Y, Entry 45's (1.645 + 0.8416) times the
   Newey-West standard error of the mean of d, times 12. Y ignores the
   correction, so it compares with Entry 45's.

:attr:`chan.low_beta_leverage.Verdict.detectable` supplies Y. Its ``line`` and
``log_verdict`` are not reused, because they word the beta match and map a
holding result to ``reproduced``.

**Beside the outcomes**, deciding nothing, the report prints five figures for
each ceiling.

1. Its realised compounded growth a year, beside Entry 45's unlevered low and
   high, read from :mod:`chan.low_beta_leverage`.
2. Its mean leverage and the number of months the ceiling binds, which is
   every month k is above C.
3. Its worst month, with the formation date, the leverage and the capped
   return.
4. Its realised beta, the slope of its monthly excess return on SPY's, beside
   the high fifth's.
5. The break-even borrowing spread. A yearly spread s on the borrowed L − 1
   takes (L − 1) × s / 12 from each month, and bisection finds the s at which
   twelve times the mean of d reaches 0. A charged month at −1 or below counts
   as a gap unbounded below. The spread is "none" when the gap is already 0
   or below at s = 0, and no outcome reads it.

Location 4700's caveat is printed beside the result, that "one should be
quite wary of using too much leverage on normally low-beta stocks".

**Five limits** go with every figure.

1. **Exploratory**, for the reasons above.
2. **Survivor-only.** The file is the S&P 500 as it stood on 2007-11-23,
   carried backwards, as in Entry 45. WYN, DFS and SE also carry an earlier
   company's prices. The write-up counted after the run that those prices sit
   in one of the fifths in 36 of the 83 holding months.
3. **Not a holdout.** The years 2000 to 2007 were past prices by the time the
   book printed the claim.
4. **Borrowing at the bill rate flatters the levered side.** The break-even
   spread measures by how much.
5. **No margin call inside a month is modelled.** Under FINRA Rule 4210's 25
   percent maintenance margin, a position levered 2 gets a call after a fall
   of a third within the month, and month-end closes cannot see that.
   Regulation T sets only the 50 percent needed to open the position.

If either ceiling holds, the plan's follow-up registers both, unchanged, on
[issue 526](https://github.com/l3a0/quantitative-trading/issues/526)'s
point-in-time panel from 2008 to 2026, which is a holdout.

``tests/test_low_beta_capped.py`` is the single authority for every number any
prose surface quotes about this run. The Entry 45 figures it reads unchanged,
such as the unlevered growths and the beta match's 58.0262, are pinned in
``tests/test_low_beta_leverage.py``. ``docs/replication-log.md`` Entry 48
carries the result. It first ran here on 2026-10-11.

:func:`yearly_standard_error` and :func:`five_percent_line` were added by the
write-up, ``blog/capped-low-beta-lessons.md``, after the run. They measure how
far each point estimate sat from the line a one-sided 5 percent test draws,
and decide nothing. :mod:`chan.low_beta_capped_figures` draws that post's
figure.

Usage:
    python -m chan.low_beta_capped
"""

from __future__ import annotations

import argparse
import dataclasses
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import NeweyWestSummary, newey_west_summary

from chan.low_beta_leverage import (
    CAVEAT_LOCATION,
    CRITICAL,
    MARKET,
    MONTHS,
    POWER,
    PREMISE_LOCATION,
    RUIN,
    RULE_LOCATION,
    EmptyPortfolio,
    NonPositiveBeta,
    Portfolios,
    Ruin,
    UnreadableStandardError,
    Verdict,
    build_portfolios,
    differences,
    growth,
    read_sources,
    realised_beta,
    ruined_months,
)
from chan.pca_factor_momentum import benjamini_hochberg, one_sided_p
from chan.series import panel_line, vintage_line
from chan.vintage import VintageEntry, VintageUnavailable

#: The two ceilings on the beta match, Regulation T's overnight leverage and
#: portfolio margin's 20 percent, both from location 814.
CEILINGS = (2.0, 5.0)

#: The false-discovery rate Benjamini-Hochberg controls across the ceilings.
FALSE_DISCOVERY = 0.05

#: The Kindle locations of the revised edition that give each ceiling.
MARGIN_LOCATION = 814
RETAIL_LOCATION = 2836

#: The widest yearly spread the break-even search tries before refusing. A
#: spread this large would charge a levered month more than its whole capital.
MAX_SPREAD = 1e6

#: The width at which the bisection stops, far below the 4 decimals quoted.
TOLERANCE = 1e-12

#: The most halvings the bisection makes. TOLERANCE is absolute, and once the
#: bracket passes about 8192 two neighbouring floats lie further apart than it,
#: so the width alone would never fall below it. Forty halvings already bring
#: a bracket of 1 down to TOLERANCE, and 200 bring any bracket up to
#: MAX_SPREAD down to the spacing of the floats in it.
MAX_HALVINGS = 200

#: The p-value a ruined ceiling enters both families with.
RUINED_P = 1.0


class NoBreakEven(Exception):
    """The gap stays above 0 at every spread up to :data:`MAX_SPREAD`, so nothing brackets it."""


@dataclass(frozen=True)
class WorstMonth:
    """The holding month with the lowest capped return, which need not be a ruin."""

    formed: pd.Timestamp
    held_to: pd.Timestamp
    leverage: float
    capped: float


@dataclass(frozen=True)
class Capped:
    """One ceiling's capped portfolio and the statistic on it, before the control.

    ``portfolios`` is Entry 45's with ``levered`` and ``leverage`` both
    replaced, so every reader of :class:`chan.low_beta_leverage.Portfolios`
    sees the capped series. ``k`` is the uncapped beta match. ``summary`` is
    ``None`` exactly when ``ruined`` is not empty.
    """

    ceiling: float
    portfolios: Portfolios
    k: pd.Series
    ruined: tuple[Ruin, ...]
    summary: NeweyWestSummary | None

    @property
    def by_ruin(self) -> bool:
        return bool(self.ruined)

    @property
    def months(self) -> int:
        return len(self.portfolios.levered)

    def _tested(self) -> NeweyWestSummary:
        if self.summary is None:
            raise ValueError(
                f"at a ceiling of {self.ceiling:g} a capped month lost more than its capital, so "
                "d is undefined and the Newey-West statistic is not computed"
            )
        return self.summary

    @property
    def gap(self) -> float:
        """Twelve times the mean of d, the gap in realised compounded growth a year."""
        return self._tested().mean * MONTHS

    @property
    def t(self) -> float:
        return self._tested().t_newey_west

    @property
    def lag(self) -> int:
        return self._tested().lag

    @property
    def p_claim(self) -> float:
        """The one-sided p-value in the claim's direction, 1 for a ruined ceiling."""
        return RUINED_P if self.by_ruin else one_sided_p(self.t)

    @property
    def p_contrary(self) -> float:
        """The one-sided p-value in the contrary direction, 1 for a ruined ceiling."""
        return RUINED_P if self.by_ruin else one_sided_p(-self.t)

    @property
    def detectable(self) -> float:
        """Y, read through Entry 45's :class:`chan.low_beta_leverage.Verdict`."""
        return Verdict(months=self.months, summary=self._tested()).detectable

    @property
    def binds(self) -> int:
        """The months whose beta match is above the ceiling, so the ceiling sets L."""
        return int((self.k > self.ceiling).sum())

    @property
    def mean_leverage(self) -> float:
        return float(self.portfolios.leverage.mean())

    @property
    def realised_growth(self) -> float | None:
        """Twelve times the mean monthly log return, ``None`` once a month is ruined."""
        return None if self.by_ruin else growth(self.portfolios.levered)

    @property
    def realised_beta(self) -> float:
        """The slope on SPY's monthly excess return over all 83 months, each freshly funded."""
        return realised_beta(self.portfolios.levered, self.portfolios)

    def worst(self) -> WorstMonth:
        """The month with the lowest capped return, its formation date and its leverage."""
        p = self.portfolios
        at = int(np.argmin(p.levered.to_numpy()))
        return WorstMonth(
            formed=p.formed[at],
            held_to=p.held_to[at],
            leverage=float(p.leverage.iloc[at]),
            capped=float(p.levered.iloc[at]),
        )


@dataclass(frozen=True)
class Outcome:
    """One ceiling's result after Benjamini-Hochberg has run on both families."""

    capped: Capped
    claim_rejected: bool
    contrary_rejected: bool

    @property
    def outcome(self) -> str:
        c = self.capped
        if c.by_ruin:
            return "Contradicted by ruin"
        if c.summary.mean > 0 and self.claim_rejected:
            return "Holds"
        if c.summary.mean < 0 and self.contrary_rejected:
            return "Contradicted"
        return "Not decided"

    def line(self) -> str:
        """The outcome in the wording the plan fixed before any capped number."""
        c = self.capped
        ceiling = f"{c.ceiling:g}"
        outcome = self.outcome
        if outcome == "Contradicted by ruin":
            first = c.ruined[0]
            return (
                f"Levered by the beta match capped at {ceiling}, the low-beta portfolio lost "
                f"more than its capital in the month ending {first.held_to.date()}, at a "
                f"leverage of {first.leverage:.4f}, so its compounded growth is unbounded below "
                "and the unlevered high-beta portfolio out-compounded it."
            )
        if outcome == "Holds":
            return (
                f"Levered by the beta match capped at {ceiling}, the low-beta portfolio "
                f"out-compounded the unlevered high-beta portfolio by {c.gap:.4f} a year, "
                f"Newey-West t = {c.t:.4f} over {c.months} months, a discovery under "
                "Benjamini-Hochberg at 5 percent across the two ceilings."
            )
        if outcome == "Contradicted":
            # The sentence names the high-beta side as the winner, so the gap it
            # quotes is the size of that side's lead, a positive number.
            return (
                "The unlevered high-beta portfolio out-compounded the low-beta portfolio "
                f"levered by the beta match capped at {ceiling} by {-c.gap:.4f} a year, "
                f"Newey-West t = {c.t:.4f} over {c.months} months, a discovery under "
                "Benjamini-Hochberg at 5 percent across the two ceilings."
            )
        return (
            f"At a ceiling of {ceiling}, no gap in compounded growth detectable above about "
            f"{c.detectable:.4f} a year over {c.months} months, where the point estimate is "
            f"{c.gap:.4f}."
        )


def cap(portfolios: Portfolios, ceiling: float) -> Portfolios:
    """Entry 45's portfolios levered by min(k, ceiling), with ``levered`` and ``leverage`` replaced.

    A ceiling of 1 or below refuses as :class:`ValueError`, because the capped
    portfolio would then borrow nothing and the run would test no leverage.
    Both fields go together, because
    :func:`chan.low_beta_leverage.ruined_months` reads the leverage it reports
    from ``leverage``, and a ruin would otherwise name the uncapped k.
    """
    if not ceiling > 1:
        raise ValueError(
            f"a ceiling of {ceiling:g} is at or below 1, so nothing is borrowed and no leverage "
            "is tested"
        )
    p = portfolios
    leverage = p.leverage.clip(upper=ceiling).rename(f"L at {ceiling:g}")
    levered = (p.rf + leverage * (p.low - p.rf)).rename(f"capped at {ceiling:g}")
    return dataclasses.replace(p, levered=levered, leverage=leverage)


def capped(portfolios: Portfolios, ceiling: float) -> Capped:
    """One ceiling's capped portfolio, its ruined months, and the Newey-West summary of d."""
    replaced = cap(portfolios, ceiling)
    ruined = ruined_months(replaced)
    summary = None if ruined else newey_west_summary(differences(replaced).to_numpy())
    return Capped(
        ceiling=ceiling,
        portfolios=replaced,
        k=portfolios.leverage,
        ruined=ruined,
        summary=summary,
    )


def decide(results: Sequence[Capped], q: float = FALSE_DISCOVERY) -> tuple[Outcome, ...]:
    """Benjamini-Hochberg on each direction's one-sided p-values, then each ceiling's outcome."""
    claim = benjamini_hochberg(np.array([c.p_claim for c in results]), q=q)
    contrary = benjamini_hochberg(np.array([c.p_contrary for c in results]), q=q)
    outcomes = tuple(
        Outcome(capped=c, claim_rejected=bool(a), contrary_rejected=bool(b))
        for c, a, b in zip(results, claim, contrary, strict=True)
    )
    # Read Y once here for every undecided ceiling, so a degenerate d refuses
    # as UnreadableStandardError before anything is printed.
    for outcome in outcomes:
        if outcome.outcome == "Not decided":
            _ = outcome.capped.detectable
    return outcomes


def assess(portfolios: Portfolios, ceilings: Sequence[float] | None = None) -> tuple[Outcome, ...]:
    """Each ceiling capped, tested and decided under one control, :data:`CEILINGS` by default."""
    chosen = CEILINGS if ceilings is None else ceilings
    return decide([capped(portfolios, ceiling) for ceiling in chosen])


def yearly_standard_error(result: Capped) -> float:
    """The Newey-West standard error of the yearly gap, 12 times that of the mean of d.

    Read through Entry 45's :attr:`chan.low_beta_leverage.Verdict.standard_error`,
    the same path :attr:`Capped.detectable` takes, so Y is exactly
    (1.645 + 0.8416) times this. ``blog/capped-low-beta-lessons.md`` added it
    after the run, so it decides nothing, and
    :mod:`chan.low_beta_capped_figures` draws each sampling curve with it.
    """
    return Verdict(months=result.months, summary=result._tested()).standard_error * MONTHS


def five_percent_line(result: Capped) -> float:
    """The yearly gap at which the one-sided t reaches 1.645, 1.645 times the standard error.

    A point estimate past this line is what a one-sided 5 percent test calls
    a gap, before any correction across ceilings. Added after the run by the
    write-up, like :func:`yearly_standard_error`.
    """
    return CRITICAL * yearly_standard_error(result)


def charged_gap(portfolios: Portfolios, spread: float) -> float:
    """Twelve times the mean of d once a yearly spread s is charged on the borrowed L − 1.

    Each month loses (L − 1) × s / 12. A charged month at :data:`RUIN` or below
    has lost its capital, so the gap is unbounded below and reads as −inf.
    """
    p = portfolios
    charged = p.levered - (p.leverage - 1) * spread / MONTHS
    if (charged <= RUIN).any():
        return -math.inf
    return float((np.log1p(charged) - np.log1p(p.high)).mean() * MONTHS)


def break_even_spread(portfolios: Portfolios) -> float | None:
    """The yearly spread at which the gap reaches 0, by bisection, or ``None``.

    ``None`` when the gap is already 0 or below at a spread of 0. The upper end
    of the bracket doubles from 1 until the gap is 0 or below there, and the
    search refuses as :class:`NoBreakEven` past :data:`MAX_SPREAD`. The bisection
    stops at a width of :data:`TOLERANCE` or after :data:`MAX_HALVINGS` halvings,
    whichever comes first, so it ends even where the floats are too far apart
    for the width to reach :data:`TOLERANCE`.
    """
    if not charged_gap(portfolios, 0.0) > 0:
        return None
    low, high = 0.0, 1.0
    while charged_gap(portfolios, high) > 0:
        high *= 2
        if high > MAX_SPREAD:
            raise NoBreakEven(
                f"the gap stays above 0 at a yearly spread of {MAX_SPREAD:g}, so no borrowing "
                "cost brings it to 0"
            )
    for _ in range(MAX_HALVINGS):
        if high - low <= TOLERANCE:
            break
        middle = (low + high) / 2
        if charged_gap(portfolios, middle) > 0:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def report(
    members: list[VintageEntry],
    spy_entry: VintageEntry,
    bill_entry: VintageEntry,
    portfolios: Portfolios,
) -> tuple[Outcome, ...]:
    """Print the vintages, each ceiling's outcome and statistic, the side figures and the labels."""
    p = portfolios
    outcomes = assess(p)
    print(
        "EXPLORATORY. Chan's low-beta leverage rule at leverage a broker would lend, on his "
        "S&P 500 file"
    )
    print(f"  stocks   {panel_line(members)}")
    print(f"  market   {vintage_line(spy_entry)}")
    print(f"  bills    {vintage_line(bill_entry)}")
    print(
        f"  window   formed {p.formed[0].date()} to {p.formed[-1].date()}, held to "
        f"{p.held_to[0].date()} to {p.held_to[-1].date()}, {len(p.low)} months"
    )
    print(
        f"  leverage L = min(k, C), k the beta match of location {PREMISE_LOCATION}, C each "
        f"ceiling of location {MARGIN_LOCATION}: " + ", ".join(f"{c:g}" for c in CEILINGS)
    )
    print("  capped   rf + L x (r_low - rf), borrowing at the bill rate, no trading cost")
    print()
    print(
        f'  Claim, location {RULE_LOCATION}, "Holding a highly leveraged portfolio of low-beta '
        "stocks should generate higher"
    )
    print(
        "  long-term compounded growth than holding an unleveraged portfolio of high-beta "
        'stocks", read at each ceiling.'
    )
    for o in outcomes:
        c = o.capped
        print()
        print(f"  Ceiling {c.ceiling:g}: {o.outcome.upper()}, exploratory.")
        print(f"  {o.line()}")
        if c.by_ruin:
            print(f"  {'Ruined month':<14} {'Formed':<12} {'L':>8} {'Capped':>9}")
            for ruin in c.ruined:
                print(
                    f"  {str(ruin.held_to.date()):<14} {str(ruin.formed.date()):<12} "
                    f"{ruin.leverage:>8.4f} {ruin.levered:>9.4f}"
                )
            print(
                f"  A capped return of {RUIN:.0f} or below leaves d undefined, so neither t nor Y "
                f"is computed, and the ceiling enters both families at p = {RUINED_P:g}."
            )
        else:
            print(
                f"  d = ln(1 + capped low) - ln(1 + high), {c.months} months, mean x 12 "
                f"{c.gap:.4f}, Newey-West t {c.t:.4f} at lag {c.lag}"
            )
            print(
                f"  one-sided p, claim {c.p_claim:.4f}, rejected "
                f"{'yes' if o.claim_rejected else 'no'}. Contrary {c.p_contrary:.4f}, rejected "
                f"{'yes' if o.contrary_rejected else 'no'}."
            )
            if o.outcome == "Not decided":
                print(
                    f"  Y = ({CRITICAL} + {POWER}) x the Newey-West standard error x 12 = "
                    f"{c.detectable:.4f}, per ceiling, ignoring the correction."
                )
    print()
    print(
        f"  Benjamini-Hochberg at q = {FALSE_DISCOVERY} across the {len(CEILINGS)} ceilings, run "
        "once on one_sided_p(t) and once on one_sided_p(-t)."
    )
    print()
    print("  Beside the outcomes, deciding nothing")
    print(
        f"  {'Ceiling':<8} {'Growth':>8} {'Mean L':>8} {'Binds':>6} {'Beta':>8} {'Spread':>8}   "
        "Worst month"
    )
    for o in outcomes:
        c = o.capped
        grew = "ruin" if c.realised_growth is None else f"{c.realised_growth:.4f}"
        spread = break_even_spread(c.portfolios)
        spread_text = "none" if spread is None else f"{spread:.4f}"
        worst = c.worst()
        print(
            f"  {c.ceiling:<8g} {grew:>8} {c.mean_leverage:>8.4f} {c.binds:>6} "
            f"{c.realised_beta:>8.4f} {spread_text:>8}   {worst.held_to.date()}, formed "
            f"{worst.formed.date()}, L {worst.leverage:.4f}, return {worst.capped:.4f}"
        )
    print(
        f"  Entry 45, unlevered: low growth {growth(p.low):.4f}, high growth "
        f"{growth(p.high):.4f}, high beta {realised_beta(p.high, p):.4f}"
    )
    print(
        "  Growth is 12 x the mean monthly log return. Binds counts the months k is above the "
        "ceiling. Beta is on SPY's monthly excess"
    )
    print(
        f"  return over all {len(p.low)} months, each freshly funded. Spread is the yearly "
        "borrowing spread over the bill, charged (L - 1) x s / 12"
    )
    print(
        "  a month, at which the gap's point estimate reaches 0, found by bisection, and none "
        "where the gap is 0 or below without it."
    )
    print()
    print(
        f'  Location {CAVEAT_LOCATION}: "one should be quite wary of using too much leverage on '
        'normally low-beta stocks".'
    )
    print("  Five limits on every figure above:")
    print(
        "  1. Exploratory. Entry 45's calendar, its leverage path, the ruin, eight months of both "
        "groups' returns and its side figures,"
    )
    print(
        "  both Sharpe ratios, the growths, the realised betas and the full-sample Kelly leverage, "
        "were seen before either ceiling was chosen."
    )
    print(
        "  2. Survivor-only. The panel holds the stocks in the index on 2007-11-23, carried "
        "backwards, and WYN, DFS and SE also carry an earlier company's prices."
    )
    print(
        "  3. Not a holdout. The years 2000 to 2007 were past prices by the time the book "
        "printed the claim."
    )
    print("  4. Borrowing at the bill rate flatters the levered side, by the spread above.")
    print(
        "  5. No margin call inside a month is modelled. Under FINRA Rule 4210's 25 percent "
        "maintenance margin, a position levered 2"
    )
    print(
        "  gets a call after a fall of a third within the month, and month-end closes cannot "
        "see that."
    )
    print(
        f"  Ceilings from locations {MARGIN_LOCATION} and {RETAIL_LOCATION}. "
        "docs/replication-log.md Entry 48 carries the result."
    )
    return outcomes


def run(data_dir: Path | None = None) -> tuple[Outcome, ...]:
    """Read Entry 45's three vintages, build its portfolios, and print the capped report."""
    members, closes, spy_entry, spy, bill_entry, bills = read_sources(data_dir)
    portfolios = build_portfolios(closes, spy, bills)
    return report(members, spy_entry, bill_entry, portfolios)


def main() -> None:
    argparse.ArgumentParser(
        description="Chan's low-beta leverage rule at leverage a broker would lend, on his S&P "
        f"500 file against {MARKET}. Exploratory."
    ).parse_args()
    try:
        run()
    except (
        VintageUnavailable,
        NonPositiveBeta,
        EmptyPortfolio,
        UnreadableStandardError,
        NoBreakEven,
    ) as refused:
        # A refusal is one line rather than the bottom of a traceback, the way
        # chan.low_beta_leverage.main prints it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
