"""Whether Example 7.4's own factor returns have momentum, on Chan's S&P 600 file.

Example 7.4's revised MATLAB rests on a factor return seen today saying
something about tomorrow's. Chan states the assumption at Kindle location
4051 of the revised edition: the strategy is "based on the assumption that factor returns
have momentum". Entry 14 tested the general claim at location 4014 on two
named factors, monthly, on his S&P 500 file. This module tests the five
statistical factors Example 7.4 itself fits, daily, on the S&P 600 file the
example loads. [Issue 286](https://github.com/l3a0/quantitative-trading/issues/286)
carries the plan, and every rule below was fixed there before any factor
return was computed.

**The factor returns.** Only the revised MATLAB, :func:`chan.pca_factor.revised_matlab`,
is tested, for the reasons the issue's rule 7 gives. On day t it decomposes
the 252 returns ending t − 1 and fits day t's cross-section of returns on an
intercept and five scores. Each score is a unit-length singular vector u_k
times its singular value s_k, so each fitted slope is u_k · r_t / s_k. The
fitted value the strategy ranks on does not depend on s_k, so the factor
return tested here is f_t[k] = u_k · r_t, the slope times s_k.

1. Day t's pair is f_t[k] = u_k · r_t and f_{t+1}[k] = u_k · r_{t+1}, both on
   day t's vectors and day t's stocks, so each pair comes from one
   decomposition. :func:`chan.pca_factor.revised_matlab_components` supplies
   the vectors, so the exposures rule exists once.
2. Every day t from the revised MATLAB's first fitting day to the
   second-to-last row has a pair, which is 752 of them.
3. Factor k is the k-th largest component as each day's decomposition orders
   it. When two neighbours swap places between days, their pairs mix into
   each other's statistic, and no pair breaks.

**The statistic** for each factor is the uncentred correlation of its pairs,
the sum of f_t f_{t+1} over the square root of the sum of f_t² times the sum
of f_{t+1}². A singular vector's sign is arbitrary, and flipping it flips both
members of every pair it touches, so no product and no sum of squares moves.
Leaving out the centring is deliberate. A factor return that keeps a steady
nonzero mean in one orientation counts as persistent, which is what Chan's
"remain constant from the current time period to the next" asks.

**The comparison set** is every stock with a finite return on every row the
pairs read, after the forward fill the program does. Each stock gets the same
uncentred statistic on its own pairs of one day's return and the next. Their
median stands for "individual stock's returns", as in Entry 14.

**The criterion**, applied to each factor on its own. The claim holds for a
factor when its statistic is above 0 and above the median stock's, both
compared unrounded. Chan wrote "often", so no combined verdict is formed. The
owner ruled that way on 2026-10-10, before any factor return was computed.

**Beside the verdicts, deciding nothing.**

- Each factor's share of pairs whose two members have the same sign.
- The band ±1.96/√n that a series of independent returns centred on zero
  stays inside about 95 percent of the time, where n is the number of pairs.
- Each factor's one-sided Newey-West t of its products f_t f_{t+1} against a
  mean of zero, from :func:`ithildincore.stats.newey_west_summary`, its normal
  p-value, and which factors survive Benjamini-Hochberg at q = 0.05 across
  the five.
- Each factor's percentile among the stocks, and the stocks' quartiles.
- The intercept's uncentred statistic and its ordinary correlation across its
  pairs. The intercept moves no position, because it is added to every
  stock's expected return alike, and it equals the day's equal-weighted mean
  return.
- Every figure again without PMC, whose two price histories forward-fill into
  one day's return of 1.8654.

**Every figure here is about survivors.** ``IJR_20080114.mat`` holds the 600
companies in the index on 2008-01-14, carried backwards.

Every result here is exploratory. Testing a claim someone else chose spends
the 2004 to 2008 sample on it, so the run says whether the claim holds on this
file and nothing about factor momentum today.

**What the write-up measured after the run.** ``blog/pca-factor-momentum-lessons.md``
teaches why each pair reads one day's vectors, and the functions after
:func:`compute_both` measure what the other ways of building a factor's series
give. A singular vector's sign is whatever the numerical library returns, and
two machines running this suite returned different ones, so every vector's
sign is first fixed by a rule, its largest weight in size positive. Then they count
the days a vector's sign still flips and the days two or more factors swap
rank, and compute the statistic on each day's own weights, with sign and rank
matched, and with tomorrow's weights fitted on 251 days that leave today's
return out.
A control fits tomorrow's weights on the 251 days ending today, the same
length with today's return kept in. They also read PMC's weight on the days
whose window holds its one large return and which factor carries it, check
that the program's ranking moves nowhere when the intercept is dropped, and
find how close any stock comes to tying a factor. All of it was measured
after the verdicts and decides nothing.
:mod:`chan.pca_factor_momentum_figures` draws the post's figure from them.

``tests/test_pca_factor_momentum.py`` is the single authority for every
number any prose surface quotes about this experiment.

Usage:
    python -m chan.pca_factor_momentum
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ithildincore.stats import newey_west_summary
from scipy.optimize import linear_sum_assignment

from chan.matlab_helpers import matlab_sort
from chan.pca_factor import (
    FACTORS,
    LOOKBACK,
    SMALL_CAPS,
    SPLICED,
    matlab_returns,
    revised_matlab_components,
    revised_matlab_expected,
)
from chan.series import load_panel, panel_line
from chan.vintage import VintageEntry, VintageUnavailable

#: Each factor's name, in the order each day's decomposition ranks them.
NAMES = tuple(f"PC{k + 1}" for k in range(FACTORS))

#: The two-sided 5 percent point of the normal, for the band reported beside
#: the verdicts.
CRITICAL = 1.96

#: The false-discovery rate Benjamini-Hochberg runs at across the five factors.
FALSE_DISCOVERY = 0.05

#: The Kindle locations of the revised edition the report cites: the general
#: claim, and Example 7.4's assumption.
CLAIM_LOCATION = 4014
ASSUMPTION_LOCATION = 4051

#: Chan's word for how reliably factors behave this way, quoted beside each
#: verdict.
OFTEN = "often"


@dataclass(frozen=True)
class Pairs:
    """Each day's factor returns and the next day's, fitted on one decomposition.

    Row i is day t = ``days[i]``. ``today`` and ``tomorrow`` are pairs by
    factors, f_t and f_{t+1}. ``intercept_today`` and ``intercept_tomorrow``
    are the fitted intercepts on the same stocks, which are each day's mean
    return.
    """

    days: pd.DatetimeIndex
    today: np.ndarray
    tomorrow: np.ndarray
    intercept_today: np.ndarray
    intercept_tomorrow: np.ndarray


def uncentred(first: np.ndarray, second: np.ndarray) -> np.ndarray:
    """Σ first·second / √(Σ first² · Σ second²), down each column.

    A one-dimensional pair of series gives a zero-dimensional array.
    """
    return (first * second).sum(axis=0) / np.sqrt((first**2).sum(axis=0) * (second**2).sum(axis=0))


def file_returns(closes: pd.DataFrame) -> np.ndarray:
    """Each day's return on the closes after the program's forward fill, days by stocks."""
    return matlab_returns(closes.ffill().to_numpy(dtype=float))  # fillMissingData(cl)


@dataclass(frozen=True)
class Decomposition:
    """One window's five components, on the stocks priced on every day of it.

    The window is the ``lookback`` rows of returns ending the row before
    ``end``. ``stocks`` are the column indices it keeps, and ``vectors`` holds
    one unit-length column of weights across them per factor.
    """

    end: int
    stocks: np.ndarray
    vectors: np.ndarray
    singular: np.ndarray


def decompose(returns: np.ndarray, end: int, lookback: int = LOOKBACK) -> Decomposition:
    """The revised MATLAB's components on the ``lookback`` returns before row ``end``."""
    window = returns[end - lookback : end].T  # dailyret(t-lookback:t-1,:)'
    has = np.flatnonzero(np.isfinite(window).all(axis=1))
    vectors, singular = revised_matlab_components(window[has])
    return Decomposition(end=end, stocks=has, vectors=vectors, singular=singular)


def daily_components(returns: np.ndarray) -> list[Decomposition]:
    """Every fitting day's decomposition, from the revised MATLAB's first to the last row.

    Day t's window ends on day t − 1, so one more decomposition exists than
    there are pairs. :func:`factor_pairs` reads all but the last, and
    :func:`weight_statistics` reads the last as the day after the last pair.
    """
    return [decompose(returns, t) for t in range(LOOKBACK + 1, len(returns))]


def factor_pairs(closes: pd.DataFrame) -> Pairs:
    """Every fitting day's five factor returns and the next day's, on that day's vectors."""
    returns = file_returns(closes)
    days, today, tomorrow, mean_today, mean_tomorrow = [], [], [], [], []
    for d in daily_components(returns)[:-1]:  # the revised MATLAB's days with a next row
        t, has = d.end, d.stocks
        days.append(closes.index[t])
        today.append(d.vectors.T @ returns[t, has])
        tomorrow.append(d.vectors.T @ returns[t + 1, has])
        mean_today.append(returns[t, has].mean())
        mean_tomorrow.append(returns[t + 1, has].mean())
    return Pairs(
        days=pd.DatetimeIndex(days),
        today=np.array(today),
        tomorrow=np.array(tomorrow),
        intercept_today=np.array(mean_today),
        intercept_tomorrow=np.array(mean_tomorrow),
    )


def stock_statistics(closes: pd.DataFrame) -> pd.Series:
    """The uncentred statistic of each stock priced on every row the pairs read."""
    returns = file_returns(closes)[LOOKBACK + 1 :]
    complete = np.isfinite(returns).all(axis=0)
    values = uncentred(returns[:-1, complete], returns[1:, complete])
    return pd.Series(values, index=closes.columns[complete])


@dataclass(frozen=True)
class Comparison:
    """The five factors' statistics and the comparison set's."""

    factors: np.ndarray
    #: One per stock with a finite return on every row the pairs read.
    stocks: pd.Series
    pairs: int

    @property
    def median(self) -> float:
        return float(self.stocks.median())

    #: The quartiles use pandas' default, linear interpolation between the two
    #: nearest stocks, as Entry 14's do.
    @property
    def lower_quartile(self) -> float:
        return float(self.stocks.quantile(0.25))

    @property
    def upper_quartile(self) -> float:
        return float(self.stocks.quantile(0.75))

    @property
    def band(self) -> float:
        """±1.96/√n, where independent returns centred on zero land 95 percent of the time."""
        return CRITICAL / math.sqrt(self.pairs)

    def percentile(self, value: float) -> float:
        """The percent of the comparison set whose statistic is strictly below ``value``."""
        return float((self.stocks < value).mean() * 100)


@dataclass(frozen=True)
class Verdict:
    """The criterion applied to one factor: both halves, and whether the claim holds."""

    factor: str
    statistic: float
    median: float

    @property
    def above_zero(self) -> bool:
        return self.statistic > 0

    @property
    def above_median(self) -> bool:
        return self.statistic > self.median

    @property
    def holds(self) -> bool:
        return self.above_zero and self.above_median

    def line(self) -> str:
        if self.holds:
            return "HOLDS. Above 0 and above the median stock"
        if self.above_zero:
            return "DOES NOT HOLD. Above 0, but not above the median stock"
        if self.above_median:
            return "DOES NOT HOLD. Above the median stock, but not above 0"
        return "DOES NOT HOLD. Neither above 0 nor above the median stock"


def one_sided_p(t: float) -> float:
    """The normal probability of a t at least this large when the mean is zero."""
    return 0.5 * math.erfc(t / math.sqrt(2))


def benjamini_hochberg(p_values: np.ndarray, q: float = FALSE_DISCOVERY) -> np.ndarray:
    """Which hypotheses the Benjamini-Hochberg step-up rejects at false-discovery rate ``q``.

    Sorted ascending, the i-th smallest of m p-values is compared with i·q/m,
    counting i from 1. Every hypothesis up to the largest i that passes is
    rejected, including any smaller one that failed its own comparison.
    """
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="stable")
    passes = p[order] <= np.arange(1, m + 1) * q / m
    rejected = np.zeros(m, dtype=bool)
    if passes.any():
        rejected[order[: np.flatnonzero(passes)[-1] + 1]] = True
    return rejected


@dataclass(frozen=True)
class Result:
    """Every figure one run reports, for one set of columns."""

    pairs: Pairs
    comparison: Comparison
    same_sign: np.ndarray
    t_newey_west: np.ndarray
    p_values: np.ndarray
    survives: np.ndarray
    intercept_uncentred: float
    intercept_pearson: float

    def verdicts(self) -> tuple[Verdict, ...]:
        """The criterion applied to each factor, separately."""
        median = self.comparison.median
        return tuple(
            Verdict(name, float(value), median)
            for name, value in zip(NAMES, self.comparison.factors, strict=True)
        )


def compute(closes: pd.DataFrame) -> Result:
    """The pairs, the statistics, the comparison set and every figure beside the verdicts."""
    pairs = factor_pairs(closes)
    products = pairs.today * pairs.tomorrow
    t_values = np.array([newey_west_summary(products[:, k]).t_newey_west for k in range(FACTORS)])
    p_values = np.array([one_sided_p(t) for t in t_values])
    return Result(
        pairs=pairs,
        comparison=Comparison(
            factors=uncentred(pairs.today, pairs.tomorrow),
            stocks=stock_statistics(closes),
            pairs=len(pairs.days),
        ),
        same_sign=(products > 0).mean(axis=0),
        t_newey_west=t_values,
        p_values=p_values,
        survives=benjamini_hochberg(p_values),
        intercept_uncentred=float(uncentred(pairs.intercept_today, pairs.intercept_tomorrow)),
        intercept_pearson=float(np.corrcoef(pairs.intercept_today, pairs.intercept_tomorrow)[0, 1]),
    )


@dataclass(frozen=True)
class Results:
    """The run the verdicts read, and the same run without :data:`chan.pca_factor.SPLICED`."""

    spliced: Result
    unspliced: Result


def compute_both(closes: pd.DataFrame) -> Results:
    return Results(spliced=compute(closes), unspliced=compute(closes.drop(columns=[SPLICED])))


# --- what the write-up measured after the run ------------------------------------
#
# ``blog/pca-factor-momentum-lessons.md`` explains why each pair reads one
# day's vectors by measuring what the other ways of building a factor's series
# give. Everything below was measured after the verdicts and decides nothing.


def overlaps(earlier: Decomposition, later: Decomposition) -> np.ndarray:
    """Each of ``earlier``'s vectors against each of ``later``'s, on the stocks both keep.

    Row k, column j is the dot product of ``earlier``'s factor k with
    ``later``'s factor j. Near ±1 on the diagonal means the two days found the
    same factor in the same place, up to its sign.
    """
    _, mine, theirs = np.intersect1d(earlier.stocks, later.stocks, return_indices=True)
    return earlier.vectors[mine].T @ later.vectors[theirs]


def sign_flips(components: list[Decomposition]) -> np.ndarray:
    """For each factor, how many consecutive decompositions point its vector the other way."""
    flips = np.zeros(FACTORS, dtype=int)
    for earlier, later in zip(components[:-1], components[1:], strict=True):
        flips += np.diag(overlaps(earlier, later)) < 0
    return flips


def match(earlier: Decomposition, later: Decomposition) -> tuple[np.ndarray, np.ndarray]:
    """Which of ``later``'s factors is each of ``earlier``'s, and the sign that lines it up.

    The assignment maximises the summed size of the matched overlaps, through
    :func:`scipy.optimize.linear_sum_assignment`, so each of ``later``'s
    factors is used once. ``order[k]`` is the factor matched to factor k, and
    ``signs[k]`` is +1 or −1, whichever makes that overlap positive.
    """
    overlap = overlaps(earlier, later)
    rows, order = linear_sum_assignment(-np.abs(overlap))
    return order, np.where(overlap[rows, order] < 0, -1.0, 1.0)


def swap_days(components: list[Decomposition]) -> int:
    """How many consecutive decompositions rank two or more factors in a different order."""
    identity = np.arange(FACTORS)
    return sum(
        bool((match(earlier, later)[0] != identity).any())
        for earlier, later in zip(components[:-1], components[1:], strict=True)
    )


def with_largest_weight_positive(d: Decomposition) -> Decomposition:
    """``d`` with each vector's sign set so its largest weight in size is positive.

    A singular vector's sign is whatever the numerical library returns, and two
    libraries can return opposite signs for the same window. Fixing the sign by
    a rule that reads only the vector makes a series built from each day's
    vectors the same on every machine.
    """
    largest = np.abs(d.vectors).argmax(axis=0)
    signs = np.where(d.vectors[largest, np.arange(d.vectors.shape[1])] < 0, -1.0, 1.0)
    return Decomposition(end=d.end, stocks=d.stocks, vectors=d.vectors * signs, singular=d.singular)


def _on_own_weights(returns: np.ndarray, d: Decomposition, row: int) -> np.ndarray:
    return d.vectors.T @ returns[row, d.stocks]


@dataclass(frozen=True)
class WeightStatistics:
    """Each factor's uncentred statistic when tomorrow's return reads other weights.

    Every one runs over the same days as the pairs, and pairs today's factor
    return on today's weights, u_k(t) · r_t, with a return for tomorrow.

    - ``own``: tomorrow's on tomorrow's weights, u_k(t + 1) · r_{t+1}, as a
      series rebuilt from each day's decomposition would read it, with every
      vector's sign fixed by :func:`with_largest_weight_positive`.
    - ``matched``: the same, with tomorrow's factors put in today's order and
      sign by :func:`match`.
    - ``left_out``: tomorrow's weights fitted on the 251 days before today,
      which leave today's return out, then matched.
    - ``shortened``: tomorrow's weights fitted on the 251 days ending today,
      which still hold today's return, then matched. It is the control for
      ``left_out``, with the same window length and today's return kept in.

    None of the four depends on the signs the library returns. ``own`` fixes
    them by rule, and the other three match tomorrow's signs to today's.
    """

    own: np.ndarray
    matched: np.ndarray
    left_out: np.ndarray
    shortened: np.ndarray


def weight_statistics(returns: np.ndarray, components: list[Decomposition]) -> WeightStatistics:
    """The four statistics, from every decomposition :func:`daily_components` gives."""
    components = [with_largest_weight_positive(d) for d in components]
    today, own, matched, left_out, shortened = [], [], [], [], []
    for d, after in zip(components[:-1], components[1:], strict=True):
        t = d.end
        today.append(_on_own_weights(returns, d, t))
        tomorrow = _on_own_weights(returns, after, t + 1)
        own.append(tomorrow)
        order, signs = match(d, after)
        matched.append(signs * tomorrow[order])
        unseen = decompose(returns, t, LOOKBACK - 1)  # rows t − 251 to t − 1
        order, signs = match(d, unseen)
        left_out.append(signs * _on_own_weights(returns, unseen, t + 1)[order])
        seen = decompose(returns, t + 1, LOOKBACK - 1)  # rows t − 250 to t
        order, signs = match(d, seen)
        shortened.append(signs * _on_own_weights(returns, seen, t + 1)[order])
    today = np.array(today)
    return WeightStatistics(
        own=uncentred(today, np.array(own)),
        matched=uncentred(today, np.array(matched)),
        left_out=uncentred(today, np.array(left_out)),
        shortened=uncentred(today, np.array(shortened)),
    )


def windows_holding(components: list[Decomposition], row: int) -> list[Decomposition]:
    """The decompositions whose window holds the return on ``row``."""
    return [d for d in components if d.end - LOOKBACK <= row < d.end]


def largest_loading(d: Decomposition, column: int) -> tuple[float, int]:
    """The largest absolute weight any factor puts on one stock, and which factor puts it."""
    (position,) = np.flatnonzero(d.stocks == column)
    sizes = np.abs(d.vectors[position])
    return float(sizes.max()), int(sizes.argmax())


def without_the_intercept(window: np.ndarray, today: np.ndarray) -> np.ndarray:
    """The revised MATLAB's fitted values less the intercept, Σ u_k (u_k · r_t).

    The vectors sum to zero across the stocks, because each day of the window
    is centred across them first, so the intercept is the day's mean return
    and the slopes carry everything else.
    """
    vectors, _ = revised_matlab_components(window)
    return vectors @ (vectors.T @ today)


def rankings_agree(returns: np.ndarray, components: list[Decomposition]) -> np.ndarray:
    """Whether the program's ranking and the ranking without the intercept agree, per pair day."""
    agree = []
    for d in components[:-1]:
        window = returns[d.end - LOOKBACK : d.end].T[d.stocks]
        today = returns[d.end, d.stocks]
        agree.append(
            np.array_equal(
                matlab_sort(revised_matlab_expected(window, today)),
                matlab_sort(without_the_intercept(window, today)),
            )
        )
    return np.array(agree)


def smallest_gap(comparison: Comparison) -> float:
    """The closest any stock's statistic comes to any factor's.

    A gap above zero means no stock ties a factor, so the share of stocks at
    or below a factor equals the share strictly below, which
    :meth:`Comparison.percentile` counts.
    """
    stocks = comparison.stocks.to_numpy()
    return float(np.abs(stocks[:, None] - comparison.factors[None, :]).min())


def share_of_largest(values: np.ndarray, count: int) -> tuple[float, np.ndarray]:
    """The share of Σ values² that the ``count`` largest squares hold, and their positions."""
    squares = np.asarray(values, dtype=float) ** 2
    largest = np.argsort(squares, kind="stable")[::-1][:count]
    return float(squares[largest].sum() / squares.sum()), np.sort(largest)


def _figures(result: Result) -> None:
    c = result.comparison
    print(
        f"  {'Series':<30} {'Statistic':>9} {'Pctile':>7} {'Same sign':>9} {'NW t':>8} "
        f"{'p':>7} {'BH':>4}"
    )
    for k, name in enumerate(NAMES):
        print(
            f"  {name:<30} {c.factors[k]:>9.4f} {c.percentile(c.factors[k]):>7.2f} "
            f"{result.same_sign[k]:>9.4f} {result.t_newey_west[k]:>8.4f} "
            f"{result.p_values[k]:>7.4f} {'yes' if result.survives[k] else 'no':>4}"
        )
    count = len(c.stocks)
    for label, value in (
        (f"Stocks, lower quartile of {count}", c.lower_quartile),
        (f"Stocks, median of {count}", c.median),
        (f"Stocks, upper quartile of {count}", c.upper_quartile),
    ):
        print(f"  {label:<30} {value:>9.4f}")
    print(
        f"  Intercept, the day's mean return: uncentred {result.intercept_uncentred:.4f}, "
        f"ordinary correlation {result.intercept_pearson:.4f}. Decides nothing."
    )
    print(
        f"  Band +/-{CRITICAL}/sqrt({c.pairs}) = {c.band:.4f}, where a series of "
        "independent returns centred on zero stays inside 95 percent of the time. "
        "Decides nothing."
    )


def report(members: list[VintageEntry], closes: pd.DataFrame, results: Results) -> None:
    """Print the vintage, the rule, every figure, the five verdicts and both labels."""
    s = results.spliced
    days = s.pairs.days
    print("Whether Example 7.4's own factor returns have momentum, on Chan's S&P 600 file")
    print(f"  closes   {panel_line(members)}")
    print(
        f"  file     {closes.index[0].date()} to {closes.index[-1].date()}, "
        f"{len(closes)} days, {closes.shape[1]} stocks"
    )
    print(
        f"  rule     the revised MATLAB's components, lookback {LOOKBACK}, {FACTORS} factors, "
        "f_t = u_k . r_t and f_t+1 = u_k . r_t+1 on day t's vectors"
    )
    print(f"  pairs    day t from {days[0].date()} to {days[-1].date()}, {len(days)} pairs")
    print(f"  assumed  location {ASSUMPTION_LOCATION}, factor returns have momentum")
    print()
    print("  Uncentred correlation of each day's factor return with the next day's")
    _figures(s)
    print(
        "  Quartiles by linear interpolation. The percentile counts stocks strictly below. "
        f"NW t is one-sided, BH at q = {FALSE_DISCOVERY}."
    )
    print()
    for verdict in s.verdicts():
        print(
            f'  Claim for {verdict.factor}, location {CLAIM_LOCATION}, factor returns "{OFTEN}" '
            f"have stronger serial autocorrelation than stocks: {verdict.line()}."
        )
    print(
        "  Each factor is judged on its own: above 0 and above the median stock, unrounded, "
        "declared before any factor return was computed."
    )
    print()
    print(f"  Without {SPLICED}, whose two price histories forward-fill into one day's return")
    _figures(results.unspliced)
    print("  The verdicts read the file as the program does, which forward-fills.")
    print()
    print(
        "  The file holds only the companies in the index on 2008-01-14, "
        "so every figure above is about survivors."
    )
    print(
        "  Exploratory. Testing a claim someone else chose spends the 2004 to 2008 sample on it, "
        "so this says whether"
    )
    print(
        "  the claim holds on this file and nothing about factor momentum today. "
        "docs/replication-log.md Entry 42 carries the verdicts."
    )


def run(data_dir: Path | None = None) -> Results:
    """Read the S&P 600 file, compute every figure with and without PMC, and print the report."""
    members, closes = load_panel(SMALL_CAPS, field="Close", data_dir=data_dir)
    results = compute_both(closes)
    report(members, closes, results)
    return results


def main() -> None:
    argparse.ArgumentParser(
        description="Whether Example 7.4's own factor returns have momentum, on Chan's S&P 600 file"
    ).parse_args()
    try:
        run()
    except VintageUnavailable as refused:
        # A refusal naming the missing member is worth nothing at the bottom of
        # a traceback, so it reaches the reader as one line, the way
        # chan.pca_factor.main does it.
        raise SystemExit(str(refused)) from refused


if __name__ == "__main__":
    main()
